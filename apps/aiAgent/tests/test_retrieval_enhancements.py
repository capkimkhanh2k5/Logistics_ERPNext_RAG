"""Extension contracts: unseen sections, source graphs and cache identity."""

import pytest

from rag.context import GraphContext, fit_rerank_context
from rag.data import ROOT, build_corpus, read, tariff_bundle
from rag.experiments import build_eval_groups
from rag.retrieval import Retriever
from scripts.run_retrieval_experiment import CandidateCache, compute_metrics


def fixture_tariff() -> tuple[dict, dict]:
    def record(sid, code, text, kind="hs_code"):
        return {
            "id": sid,
            "source_id": sid,
            "document_type": kind,
            "text": text,
            "metadata": {"section": "XV", "chapter": "72", "code": code},
            "content": {"embedding_text": text, "exact_keys": []},
            "provenance": {"document": "TEST_SOURCE_NOT_LEGAL_EVIDENCE", "row": sid},
            "graph": {},
        }

    rows = [
        record("CH72", "72", "Chương nguồn mới", "chapter"),
        record("H7207", "7207", "Sản phẩm nguồn mới", "heading"),
        record("LEAF", "72071000", "Loại khác"),
        record("CTX", None, "Nhãn trung gian từ nguồn", "context_label"),
        record("NOTE", None, "Điều kiện theo văn bản nguồn", "chapter_note"),
    ]
    edges = [
        {"source_id": "CH72", "target_id": "H7207", "relation": "CONTAINS"},
        {"source_id": "H7207", "target_id": "LEAF", "relation": "CONTAINS"},
        {"source_id": "CTX", "target_id": "LEAF", "relation": "CONTEXT_FOR"},
        {"source_id": "NOTE", "target_id": "H7207", "relation": "APPLIES_TO"},
    ]
    return {"records": "new_records", "edges": "new_edges"}, {
        "new_records": rows,
        "new_edges": edges,
    }


def test_unseen_section_flows_through_source_adapter_graph_and_router():
    source, data = fixture_tariff()
    rows, nodes, edges = tariff_bundle(source, data)
    graph = GraphContext(rows, nodes, edges)
    leaf = next(r for r in rows if r["level"] == 8)
    enriched = graph.enrich([leaf], relevant_notes=["tt31:NOTE"])[0]
    assert "Nhãn trung gian từ nguồn" in enriched["rerank_text"]
    assert "Điều kiện theo văn bản nguồn" in enriched["rerank_text"]
    assert enriched["note_citations"][0]["locator"]["row"] == "NOTE"
    assert graph.ancestors(leaf["id"]) == ["tt31:CH72", "tt31:H7207"]
    router = Retriever.__new__(Retriever)
    result = router.section_candidates(
        [{"section": "XV", "rrf_score": 0.95}, {"section": "XIV", "rrf_score": 0.10}]
    )
    assert result[0]["section"] == "XV"
    assert enriched["graph_context"]["applicability"] == "REQUIRES_SOURCE_REASONING"


def test_source_context_separates_diamonds_without_keyword_rules():
    bundle = build_corpus()
    graph = GraphContext(bundle["records"], bundle["nodes"], bundle["edges"])
    rows = {r["code"]: r for r in graph.candidate_views().values()}
    industrial = rows["71022100"]["intermediate_branches"]
    nonindustrial = rows["71023100"]["intermediate_branches"]
    assert "Kim cương công nghiệp:" in industrial
    assert "Kim cương công nghiệp:" not in nonindustrial
    assert "Kim cương phi công nghiệp:" in nonindustrial
    assert not any("dùng làm trang sức" in text for text in nonindustrial)
    assert "CKD" in rows["87024021"]["rerank_text"]
    assert "Loại khác:" in rows["87024061"]["intermediate_branches"]
    assert "Dạng CKD (SEN):" not in rows["87024061"]["intermediate_branches"]


def test_exclusion_edge_never_becomes_positive_note_context():
    source, data = fixture_tariff()
    data["new_edges"][-1]["relation"] = "EXCLUDES_FROM_SCOPE_TO"
    rows, nodes, edges = tariff_bundle(source, data)
    graph = GraphContext(rows, nodes, edges)
    leaf = next(r for r in rows if r["level"] == 8)
    assert not graph.enrich([leaf], relevant_notes=["tt31:NOTE"])[0]["note_citations"]


def test_graph_cycles_and_budget_do_not_invent_or_expand_unbounded_context():
    source, data = fixture_tariff()
    data["new_edges"].append({"source_id": "LEAF", "target_id": "CH72", "relation": "CONTAINS"})
    rows, nodes, edges = tariff_bundle(source, data)
    graph = GraphContext(rows, nodes, edges)
    leaf = next(r for r in rows if r["level"] == 8)
    enriched = graph.enrich([leaf], context_budget=20, include_notes=False)[0]
    assert leaf["id"] not in graph.ancestors(leaf["id"])
    assert enriched["graph_context"]["omitted_ids"]
    assert len(enriched["rerank_text"]) <= 20


def test_reranker_drops_whole_citations_with_trace_and_preserves_atomic_text():
    def tokenizer(pairs, truncation=False):
        assert not truncation
        return {"input_ids": [list(range(len(q) + len(t))) for q, t in pairs]}

    source, data = fixture_tariff()
    rows, nodes, edges = tariff_bundle(source, data)
    leaf = next(r for r in rows if r["level"] == 8)
    enriched = GraphContext(rows, nodes, edges).enrich([leaf], relevant_notes=["tt31:NOTE"])
    fitted = fit_rerank_context("Query", enriched, tokenizer, max_tokens=45)[0]
    assert fitted["rerank_text"].startswith(leaf["embedding_text"])
    assert fitted["rerank_omitted_ids"][0] == "tt31:NOTE"
    assert len(fitted["rerank_text"]) + len("Query") <= 45
    with pytest.raises(ValueError, match="Atomic source and query"):
        fit_rerank_context("Query", enriched, tokenizer, max_tokens=5)


def test_mandatory_family_grouping_handles_different_wording():
    cases = [
        {
            "record_id": "a",
            "section": "XV",
            "product_name_vi": "Mô tả thứ nhất",
            "case_family_id": "same",
        },
        {
            "record_id": "b",
            "section": "XV",
            "product_name_vi": "Cách diễn đạt khác hoàn toàn",
            "case_family_id": "same",
        },
        {
            "record_id": "c",
            "section": "XV",
            "product_name_vi": "Sản phẩm độc lập",
            "case_family_id": "other",
        },
    ]
    groups = build_eval_groups(cases)
    assert groups["a"] == groups["b"]
    assert groups["a"] != groups["c"]


def test_candidate_cache_rejects_source_policy_or_query_drift(tmp_path):
    path = tmp_path / "pools.sqlite"
    cache = CandidateCache(path, {"snapshot": "source-v1", "query_hash": "q1", "policy_hash": "p1"})
    cache.put("Câu hỏi", [{"id": "source:leaf", "code": "72071000", "level": 8}])
    assert cache.get("Câu hỏi")[0]["code"] == "72071000"
    cache.close()
    with pytest.raises(ValueError, match="identity mismatch"):
        CandidateCache(path, {"snapshot": "source-v2", "query_hash": "q1", "policy_hash": "p1"})


def test_new_chapter_metrics_have_no_default_section_assignment():
    cases = [{"record_id": "new", "section": "XV", "expected_hs_8": "72071000"}]
    results = {
        "new": {
            "ranked": [{"code": "72071000", "level": 8}],
            "pool_codes": ["72071000"],
            "latency_ms": 1,
        }
    }
    metrics = compute_metrics(cases, results, 40)
    assert metrics["sections"]["XV"]["hit@1"] == 1
    assert metrics["chapters"]["72"]["hit@1"] == 1
    assert "XVII" not in metrics["sections"]


def test_runtime_has_no_domain_classifier_import_or_literal_hs_injection():
    import ast

    tree = ast.parse((ROOT / "rag/retrieval.py").read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert "rag.attributes" not in imports and "rag.quota" not in imports
    strings = [
        n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]
    assert not any(s.isdigit() and len(s) == 8 for s in strings), (
        "HS8 literals belong in sources/tests, not the runtime classifier"
    )
    policy = read(ROOT / "config/hybrid_retrieval.json")
    assert policy["reranker"] == "cross_encoder"
    assert not any(k in policy for k in ("section_policies", "attribute_penalty", "quota_budget"))
    assert not (ROOT / "rag/attributes.py").exists()
    assert not (ROOT / "rag/quota.py").exists()


def test_unified_schema_accepts_new_section_but_taxonomy_rejects_wrong_metadata(monkeypatch):
    import jsonschema

    import rag.data as data_module

    schema = read(ROOT / "data/normalized/TT31/UNIFIED_RAG_INGEST_SCHEMA.json")
    example = read(ROOT / "data/normalized/TT31/Section-XIV/SECTION_XIV_RAG_INGEST.jsonl")[0]
    example["metadata"]["section"] = "XV"
    example["metadata"]["chapter"] = "72"
    jsonschema.validate(example, schema)
    taxonomy = {
        r["chapter_code"]: r["section_code"]
        for r in read(ROOT / "data/normalized/HS_Index/HS_2022_SCOPE_INDEX_VI_FINAL.json")[
            "records"
        ]
    }
    assert taxonomy["72"] == "XV"
    assert taxonomy["72"] != "XVII"
    sources = data_module.source_files()
    record = sources["tt31_section_xvi"][0]
    record["metadata"].update(chapter="72", section="XVII")
    monkeypatch.setattr(data_module, "source_files", lambda: sources)
    with pytest.raises(ValueError, match="Source Section/Chapter mismatch"):
        data_module.audit()


def test_group_bootstrap_reports_the_same_query_weighted_delta_as_metrics():
    from scripts.run_retrieval_experiment import paired_cluster_interval

    cases = [{"record_id": str(i), "expected_hs_8": "72071000"} for i in range(5)]
    manifest = {
        "rows": [
            {"record_id": str(i), "eval_group_id": "large" if i < 3 else "small"} for i in range(5)
        ]
    }
    a, b = {}, {}
    for i in range(5):
        correct = [{"code": "72071000", "level": 8}]
        wrong = [{"code": "72072000", "level": 8}]
        a[str(i)] = {"ranked": wrong if i < 3 else correct}
        b[str(i)] = {"ranked": correct if i < 3 else wrong}
    comparison = paired_cluster_interval(cases, manifest, a, b)
    assert comparison["metrics"]["hit@1"]["micro_delta"] == pytest.approx(0.2)
    assert comparison["wins_top1"] == 3 and comparison["losses_top1"] == 2
    assert comparison["groups"] == 2


def test_shared_channel_budget_prevents_graph_starvation_at_40_and_100():
    from rag.retrieval import fuse, source_channel_pool, unique_codes

    direct = [{"id": f"d{i}", "code": f"{i:08}", "level": 8, "score": 1.0} for i in range(100)]
    graph = [{"id": f"g{i}", "code": f"{i + 100:08}", "level": 8, "score": 1.0} for i in range(100)]
    channels, weights = (
        {"direct": direct, "graph_context": graph},
        {"direct": 0.75, "graph_context": 0.25},
    )
    naive = unique_codes(fuse(channels, 60, weights), 100)
    assert not any(r["id"].startswith("g") for r in naive)
    balanced = source_channel_pool(channels, weights, 100, 60)
    assert sum(r["selection_channel"] == "graph_context" for r in balanced[:40]) == 10
    assert sum(r["selection_channel"] == "graph_context" for r in balanced) == 25
    assert len({r["code"] for r in balanced}) == 100
    assert (
        len(source_channel_pool({"direct": direct, "graph_context": []}, weights, 100, 60)) == 100
    )
    assert (
        len(source_channel_pool({"direct": direct, "graph_context": direct}, weights, 100, 60))
        == 100
    )
