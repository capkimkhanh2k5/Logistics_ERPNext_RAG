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
    output = retriever.search("smartphone'; DROP TABLE rag.chunks; --", mode="fts")
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
    assert not retriever.search("máy tính", mode="fts", expand=False, as_of=date(2026, 9, 26))[
        "candidates"
    ]  # TT31 validity unknown


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
