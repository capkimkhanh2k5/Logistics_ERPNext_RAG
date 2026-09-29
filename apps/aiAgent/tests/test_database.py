"""Opt-in integration checks against the isolated RAG database."""

import copy
import os
from datetime import date

import psycopg
import pytest

from rag.data import digest, load_corpus
from rag.db import connect, counts, ingest, migrate
from rag.embedding import load_embeddings
from rag.retrieval import Retriever

pytestmark = pytest.mark.skipif(
    os.getenv("RAG_RUN_DB_TESTS") != "1", reason="Set RAG_RUN_DB_TESTS=1 for isolated RAG DB"
)


@pytest.fixture
def conn():
    with connect() as connection:
        migrate(connection)
        yield connection


def test_database_idempotency_and_exact_codes(conn):
    bundle = load_corpus()
    manifest, vectors, sparse = load_embeddings(bundle)
    before = counts(conn, bundle["snapshot"], manifest["profile_id"])
    ingest(conn, bundle, manifest, vectors, sparse, apply=True)
    assert counts(conn, bundle["snapshot"], manifest["profile_id"]) == before
    retriever = Retriever(conn)
    assert retriever.lookup("8517.13.00")["matches"][0]["code"] == "85171300"
    assert retriever.lookup("99999999")["status"] == "CODE_NOT_IN_CORPUS"
    with pytest.raises(ValueError):
        retriever.lookup("85171300; DROP TABLE rag.chunks")


def test_fts_unaccent_and_source_citations(conn):
    retriever = Retriever(conn)
    assert [r["id"] for r in retriever.lexical("máy tính")] == [
        r["id"] for r in retriever.lexical("may tinh")
    ]
    output = retriever.search("smartphone'; DROP TABLE rag.chunks; --", mode="fts", levels=[8])
    assert all(r["level"] == 8 and r["locator"] for r in output["candidates"])
    evidence = retriever.lookup("85171300")["evidence"]
    assert evidence["records"]
    assert all(r["role"] == "evidence" and r["locator"] for r in evidence["records"])
    assert len(evidence["records"]) <= 30
    assert evidence["characters_used"] <= evidence["character_budget"]


def test_effective_date_filter(conn):
    retriever = Retriever(conn)
    assert not retriever.search(
        "phân loại", intent="tt85", mode="fts", expand=False, as_of=date(2026, 9, 14)
    )["matches"]
    assert retriever.search(
        "phân loại", intent="tt85", mode="fts", expand=False, as_of=date(2026, 9, 15)
    )["matches"]
    assert not retriever.search(
        "máy tính", mode="fts", expand=False, as_of=date(2026, 9, 26), chapters=["84", "85"]
    )["candidates"]  # TT31 validity unknown


def test_failed_snapshot_never_becomes_active(conn):
    original = load_corpus()
    original_manifest, vectors, sparse = load_embeddings(original)
    before = conn.execute("SELECT * FROM rag.active").fetchone()
    bundle = copy.deepcopy(original)
    bundle["edges"][0]["target"] = "tt31:nonexistent-node"
    bundle["manifest"]["edges_hash"] = digest(bundle["edges"])
    bundle["snapshot"] = digest(bundle["manifest"])[:24]
    manifest = {**original_manifest, "snapshot": bundle["snapshot"]}
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        ingest(conn, bundle, manifest, vectors, sparse, apply=True)
    assert conn.execute("SELECT * FROM rag.active").fetchone() == before
    assert (
        conn.execute("SELECT id FROM rag.snapshots WHERE id=%s", (bundle["snapshot"],)).fetchone()
        is None
    )


def test_learned_sparse_postings_have_correct_dot_product(conn):
    retriever = Retriever(conn)
    tokens = conn.execute(
        "SELECT token FROM rag.sparse_postings WHERE snapshot=%s AND profile=%s ORDER BY token LIMIT 2",
        (retriever.snapshot, retriever.profile),
    ).fetchall()
    assert len(tokens) == 2
    weights = {str(tokens[0]["token"]): 0.3, str(tokens[1]["token"]): 0.7}
    ranked = retriever.sparse(weights)
    assert ranked
    first = ranked[0]
    saved = conn.execute(
        "SELECT token,weight FROM rag.sparse_postings WHERE snapshot=%s AND profile=%s AND chunk_id=%s",
        (retriever.snapshot, retriever.profile, first["id"]),
    ).fetchall()
    expected = sum(row["weight"] * weights.get(str(row["token"]), 0) for row in saved)
    assert first["score"] == pytest.approx(expected, rel=1e-5)


def test_bm25_uses_pinned_library_and_respects_namespace(conn):
    from rank_bm25 import BM25Okapi

    retriever = Retriever(conn)
    rows = retriever.bm25("phân loại hồ sơ", intent="tt85")
    assert isinstance(retriever._bm25_index, BM25Okapi)
    assert rows and all(r["namespace"] == "legal_classification" for r in rows)
    assert not any("FORM-" in r["id"] for r in rows)
    assert retriever.route("Chú giải Phần XVII loại trừ thiết bị điện")["intent"] == "legal"


def test_parent_candidates_follow_cited_contains_edges(conn):
    retriever = Retriever(conn)
    vector = conn.execute(
        "SELECT embedding FROM rag.embeddings WHERE snapshot=%s AND profile=%s AND chunk_id=%s",
        (retriever.snapshot, retriever.profile, "tt31:SXVII_HEADING4_8714"),
    ).fetchone()["embedding"]
    candidates = retriever.parent_candidates("khung xe và càng xe đạp", vector, ["XVII"])
    assert candidates
    for candidate in candidates[:10]:
        parent = candidate["parent_support"]
        assert candidate["locator"] and parent["locator"] and candidate["score"] > 0
        path = conn.execute(
            """WITH RECURSIVE descendants(id) AS (
                SELECT target FROM rag.graph_edges WHERE snapshot=%s AND source=%s
                  AND relation='CONTAINS'
                UNION
                SELECT e.target FROM rag.graph_edges e JOIN descendants d ON e.source=d.id
                WHERE e.snapshot=%s AND e.relation='CONTAINS'
            ) SELECT 1 FROM descendants WHERE id=%s LIMIT 1""",
            (retriever.snapshot, parent["id"], retriever.snapshot, candidate["id"]),
        ).fetchone()
        assert path is not None


def test_new_snapshot_without_frozen_policy_has_safe_section_fallback(conn, tmp_path, monkeypatch):
    import rag.retrieval as retrieval_module

    monkeypatch.setattr(retrieval_module, "ROOT", tmp_path)
    retriever = Retriever(conn)
    assert set(retriever.section_policies) == {"XIV", "XVI", "XVII"}
    assert all(
        policy["weights"] == {"dense": 0.5, "sparse": 0.5}
        for policy in retriever.section_policies.values()
    )


def test_implicit_hs6_nodes_preserve_source_and_graph_structure(conn):
    retriever = Retriever(conn)
    node = conn.execute(
        "SELECT metadata FROM rag.graph_nodes WHERE snapshot=%s AND id=%s",
        (retriever.snapshot, "tt31:DERIVED_HS6_851240"),
    ).fetchone()
    assert node and node["metadata"]["virtual"] and not node["metadata"]["legal_text_available"]
    edges = conn.execute(
        "SELECT * FROM rag.graph_edges WHERE snapshot=%s AND source=%s",
        (retriever.snapshot, "tt31:DERIVED_HS6_851240"),
    ).fetchall()
    assert any(e["target"] == "tt31:SXVI-T-85124000" for e in edges)


def test_definition_search_uses_real_graph_and_preserves_atomic_chunks(conn):
    retriever = Retriever(conn)
    views = retriever.definition_views()
    silver = views["tt31:HS8:71131190"]
    assert silver["record"]["source_text"] == retriever.exact("71131190")[0]["source_text"]
    assert any(x["id"] == "tt31:XIV_CH71_NOTE_09" for x in silver["citations"])
    assert any(x["target_id"] == "tt31:HS4:7113" for x in silver["paths"])
    imitation = views["tt31:HS8:71171920"]
    fragments = [x for x in imitation["citations"] if x.get("fragment_id")]
    assert fragments and all("(a)" in x["text"] and "(b)" not in x["text"] for x in fragments)
    candidates = retriever.definition_candidates("hoa tai bằng bạc", sections=["XIV"])
    assert candidates and all(x["section"] == "XIV" for x in candidates)
    assert all(x["definition_paths"] and x["definition_citations"] for x in candidates)
    assert not retriever.definition_candidates("hoa tai bằng bạc", sections=["XVI"])


def test_router_sections_are_selected_before_result_limit(conn):
    retriever = Retriever(conn)
    result = retriever.search("đồ trang sức pin", mode="bm25", top_k=1, expand=False)
    assert len(result["candidates"]) == 1
    assert len(result["section_candidates"]) == 2
    assert len(retriever.section_candidates(result["candidates"])) == 1


def test_parent_evidence_contains_only_actual_source_documents(conn):
    retriever = Retriever(conn)
    leaf = retriever.exact("85171300")
    assert leaf
    result = retriever.tariff_ancestors(leaf)
    assert result["records"] and result["trace"]
    assert any(r["code"] == "8517" for r in result["records"])
    assert all(
        r["source_text"] and r["locator"] and r["chunk_type"] == "tariff_entry"
        for r in result["records"]
    )
    assert all(r["level"] < 8 for r in result["records"])
    assert not any(r["id"].startswith("tt31:DERIVED_HS6_") for r in result["records"])


def test_gir_family_expansion_uses_database_canonical_ids(conn):
    retriever = Retriever(conn)
    rule = conn.execute(
        "SELECT * FROM rag.chunks WHERE snapshot=%s AND id=%s", (retriever.snapshot, "gir:GIR_2A")
    ).fetchone()
    assert rule and "source_id" not in rule
    expanded = retriever.rule_family_evidence("Trình tự áp dụng quy tắc", [rule])
    assert {r["id"] for r in expanded} == {"gir:GIR_2A", "gir:GIR_2B"}
    assert all(r["source_text"] and r["locator"] for r in expanded)


def test_questioned_code_retains_its_source_section_notes_scope(conn):
    from rag.retrieval import code_mention_plan

    retriever = Retriever(conn)
    plan = code_mention_plan("Có thuộc nhóm 87.08 không?")
    assert "8708" not in retriever.exact_features(plan["exact_query"])
    scopes = retriever.referenced_note_scope(plan)
    assert scopes and {r["section"] for r in scopes} == {"XVII"}
    assert all(r["purpose"] == "NOTES_FOR_REFERENCE_VALIDATION_NOT_CANDIDATE_BOOST" for r in scopes)
    assert not retriever.referenced_note_scope(code_mention_plan("Tra cứu nhóm 87.08"))
