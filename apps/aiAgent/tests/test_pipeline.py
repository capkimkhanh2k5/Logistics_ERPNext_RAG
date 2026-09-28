import numpy as np
import pytest

from rag.data import audit, build_corpus, normalize_code, read
from rag.embedding import validate_vectors
from rag.evaluation import benchmark_split, discover_gold, metrics, query_for
from rag.retrieval import fuse, unique_codes


def test_corpus_integrity_and_provenance():
    report = audit()
    assert report["gold_count"] == 390
    assert report["graph_edges"] == 5813
    first, second = build_corpus(), build_corpus()
    assert first["snapshot"] == second["snapshot"]
    assert len(first["records"]) == 5356
    assert all(r["locator"] for r in first["records"])
    assert not any("test/" in p for p in first["manifest"]["source_hashes"])
    assert len({r["id"] for r in first["records"]}) == 5356
    corrected = [r for r in first["records"] if r["metadata"].get("source_anomaly")]
    assert corrected


@pytest.mark.parametrize(
    "value,expected", [("8517.13.00", "85171300"), ("8471", "8471"), ("0101.21", "010121")]
)
def test_codes_preserve_leading_zero(value, expected):
    assert normalize_code(value) == expected


@pytest.mark.parametrize("value", ["10 kg", "123", "8517.130.0", "851713000", "85; DROP TABLE"])
def test_invalid_codes(value):
    with pytest.raises(ValueError):
        normalize_code(value)


def test_rrf_deduplicates_and_uses_rank():
    rows = fuse(
        {
            "dense": [{"id": "a", "score": 0.9}, {"id": "b", "score": 0.7}],
            "fts": [{"id": "b", "score": 20}, {"id": "b", "score": 15}],
        }
    )
    assert rows[0]["id"] == "b"
    assert rows[0]["rrf_score"] == pytest.approx(1 / 62 + 1 / 61)
    assert rows[0]["branches"]["fts"]["rank"] == 1
    assert len(unique_codes([{"code": "01"}, {"code": "01"}, {"code": "02"}], 10)) == 2


def test_vector_validation_rejects_corruption():
    with pytest.raises(ValueError):
        validate_vectors(np.zeros((2, 1024)), 2)
    with pytest.raises(ValueError):
        validate_vectors(np.full((1, 1024), np.nan), 1)
    with pytest.raises(ValueError):
        validate_vectors(np.ones((1, 768)), 1)
    vectors = validate_vectors(np.ones((2, 1024)), 2)
    np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1)


def test_gold_never_enters_query_and_split_matches_supplied_files():
    gold, _ = discover_gold()
    split = benchmark_split(gold)
    dev = {g["expected_hs_8"] for g in gold if g["test_id"] in split["dev"]}
    test = {g["expected_hs_8"] for g in gold if g["test_id"] in split["test"]}
    assert dev & test == set(split["overlapping_codes"])
    assert len(split["dev"]) == 300
    assert len(split["test"]) == 90
    assert len(split["dev"]) + len(split["test"]) == 390
    for row in gold:
        altered = {**row, "expected_hs_8": "99999999", "chapter": "99", "heading": "9999"}
        assert query_for(row, "name_and_spec") == query_for(altered, "name_and_spec")


def test_metrics_do_not_count_heading_as_full_code_hit():
    result = metrics(
        [
            {"test_id": "one", "gold": "85171300", "gold_rank": 2, "timings": {"total_ms": 5}},
            {"test_id": "two", "gold": "85171300", "gold_rank": None, "timings": {"total_ms": 7}},
        ]
    )
    assert result["hit@1"] == 0
    assert result["hit@5"] == 0.5
    assert result["mrr@10"] == 0.25


def test_context_joins_preserve_atomic_wording():
    bundle = build_corpus()
    rows = {r["id"]: r for r in bundle["records"]}
    conclusion = rows["gir:GIR_3_NOTE_038"]
    assert conclusion["source_text"] == "Phân loại vào nhóm 16.02."
    assert "bánh xăng đuých" in conclusion["embedding_text"]
    assert conclusion["locator"]["context_source_ids"] == ["GIR_3_NOTE_037", "GIR_3_NOTE_038"]
    subpoint = rows["tt85:TT85-A9-3.a.1"]
    assert subpoint["metadata"]["context_source_ids"] == [
        "TT85-A9-3",
        "TT85-A9-3.a",
        "TT85-A9-3.a.1",
    ]
    assert len([r for r in rows if r.startswith("tt85:TT85-FORM-")]) == 0


def test_weighted_fusion_and_conservative_routing():
    rows = fuse(
        {"dense": [{"id": "a", "score": 1}], "fts": [{"id": "b", "score": 100}]},
        weights={"dense": 1, "fts": 0.1},
    )
    assert rows[0]["id"] == "a"
    from rag.retrieval import Retriever

    router = Retriever.__new__(Retriever)
    assert router.route("Thịt bò tươi")["status"] == "OUT_OF_SCOPE"
    assert router.route("Máy xay thịt")["status"] == "UNCERTAIN"
    assert router.route("Thiết bị điện tử")["status"] == "NEED_MORE_INFORMATION"
    assert router.route("0901.21.00")["status"] == "OUT_OF_SCOPE"
    assert router.route("GIR 6 phân nhóm")["intent"] == "gir"


def test_multilevel_metadata_and_form_registry():
    from rag.data import NORMALIZED

    bundle = build_corpus()
    rows = bundle["records"]
    assert set(r["namespace"] for r in rows) == {"hs_classification", "legal_classification"}
    assert {r["section"] for r in rows if r["dataset"] == "tt31"} == {"XIV", "XVI", "XVII"}
    for level in (2, 4, 6, 8):
        assert any(r.get("level") == level for r in rows)
    assert all(
        r["chunk_type"] == "legal_clause" for r in rows if r["namespace"] == "legal_classification"
    )
    assert not any("FORM-" in r["id"] for r in rows)
    assert len(read(NORMALIZED / "TT85/tt85_forms_source.json")) == 5
    assert all(
        e["source"] in {n["id"] for n in bundle["nodes"]}
        and e["target"] in {n["id"] for n in bundle["nodes"]}
        for e in bundle["edges"]
    )


def test_product_filter_is_not_fixed_to_leaf_or_role():
    from rag.retrieval import Retriever

    retriever = Retriever.__new__(Retriever)
    retriever.snapshot = "test"
    clause, params = retriever._filter("product", None, None)
    assert "level" not in clause and "role" not in clause
    assert "hs_classification" in params
    clause, params = retriever._filter(
        "product", None, None, levels=[4, 6], sections=["XVI", "XVII"]
    )
    assert [4, 6] in params and ["XVI", "XVII"] in params
    with pytest.raises(ValueError):
        retriever._filter("knowledge", None, None, namespace="unsafe")


def test_rrf_weight_scaling_preserves_rank_and_soft_section_beam():
    from rag.retrieval import Retriever

    branches = {
        "dense": [
            {"id": "a", "section": "XVII", "score": 1},
            {"id": "b", "section": "XVI", "score": 0.9},
        ],
        "sparse": [{"id": "b", "section": "XVI", "score": 100}],
    }
    a = fuse(branches, weights={"dense": 1, "sparse": 2})
    b = fuse(branches, weights={"dense": 1 / 3, "sparse": 2 / 3})
    assert [r["id"] for r in a] == [r["id"] for r in b]
    retriever = Retriever.__new__(Retriever)
    assert {r["section"] for r in retriever.section_candidates(a)} == {"XVI", "XVII"}
    assert retriever.route("Bộ điều khiển điện dùng cho ô tô")["status"] == "UNCERTAIN"
    assert retriever.route("Vàng miếng")["status"] == "UNCERTAIN"


def test_late_interaction_uses_best_passage_token_per_query_token():
    from FlagEmbedding import BGEM3FlagModel

    q = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    d = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, -1.0]], dtype=np.float32)
    assert float(BGEM3FlagModel.colbert_score(None, q, d)) == pytest.approx(1.0)


def test_verified_gold_uses_supplied_partitions_and_normalized_grid():
    from rag.evaluation import discover_gold, weight_grid

    rows, paths = discover_gold()
    assert len(rows) == 390
    assert paths == [
        "data/verified/hs/train/HS_RAG_TRAIN_300_VERIFIED.jsonl",
        "data/verified/hs/test/HS_RAG_TEST_90_DISJOINT_VERIFIED.jsonl",
    ]
    assert all(r["expected_hs_8"] not in r["query"] for r in rows)
    grid = weight_grid(("dense", "sparse", "bm25", "fts", "exact"))
    assert len(grid) >= 3876
    assert all(sum(w.values()) == pytest.approx(1.0) for w in grid)


def test_exact_features_preserve_code_units_purity_and_standards():
    from rag.retrieval import Retriever

    features = Retriever.exact_features(
        "8517.13.00 USB-C 65 W 5G Li-ion 802.11ax bạc 925 độ tinh khiết 99,9%"
    )
    assert {
        "85171300",
        "usb-c",
        "65w",
        "5g",
        "li-ion",
        "802.11ax",
        "fineness:925",
        "99.9%",
    } <= features
    assert not Retriever.exact_features("một thiết bị điện tử không rõ thông số")


def test_supplied_query_sanitization_preserves_product_specs():
    from rag.evaluation import clean_product_text

    text = "Máy tính 10 kg, 65 W, thuộc nhánh 8471.30. Case test dựa trên Chương 84."
    cleaned = clean_product_text(text)
    assert "8471" not in cleaned and "Case test" not in cleaned
    assert "10 kg" in cleaned and "65 W" in cleaned
    assert (
        clean_product_text("Hoa tai bằng bạc. Case test Chú giải 9 Chương 71.")
        == "Hoa tai bằng bạc"
    )


def test_dual_paths_keep_direct_candidates_when_hierarchy_prunes():
    from rag.retrieval import candidate_paths

    rows = [
        {"id": "a", "code": "87011000", "section": "XVII", "level": 8, "score": 1.0},
        {"id": "b", "code": "87111000", "section": "XVII", "level": 8, "score": 0.8},
    ]
    policy = {"XVII": {"weights": {"dense": 1.0}, "k": 20}}
    params = {"beam_size": 1, "strategy": "dual", "direct_weight": 0.75}
    output = candidate_paths({"dense": rows}, [{"section": "XVII", "score": 0.1}], policy, params)
    assert [r["code"] for r in output["hierarchy_candidates"]] == ["87011000"]
    assert {r["code"] for r in output["candidates"]} == {"87011000", "87111000"}
    assert output["hierarchy"][0]["stages"]["heading"] == ["8701"]


def test_rrf_omitted_branches_receive_no_implicit_weight():
    rows = fuse(
        {"dense": [{"id": "a", "score": 1}], "fts": [{"id": "b", "score": 100}]},
        weights={"dense": 1.0},
    )
    assert rows[0]["id"] == "a"
    assert rows[1]["rrf_score"] == 0


def test_definition_paths_do_not_turn_exclusions_into_positive_candidates():
    from rag.retrieval import definition_passages

    records = [
        {
            "id": "n",
            "namespace": "hs_classification",
            "role": "evidence",
            "source_text": "Definition of earrings",
            "locator": {"page": 1},
        },
        {
            "id": "a",
            "namespace": "hs_classification",
            "chunk_type": "tariff_entry",
            "level": 8,
            "embedding_text": "Jewellery silver",
            "source_text": "Other",
        },
        {
            "id": "b",
            "namespace": "hs_classification",
            "chunk_type": "tariff_entry",
            "level": 8,
            "embedding_text": "Excluded item",
            "source_text": "Other",
        },
    ]
    edges = [
        {"source": "n", "relation": "DEFINES_FOR", "target": "h"},
        {"source": "h", "relation": "CONTAINS", "target": "a"},
        {"source": "n", "relation": "EXCLUDES_TO", "target": "b"},
    ]
    views = definition_passages(records, [], edges)
    assert set(views) == {"a"}
    assert views["a"]["record"]["source_text"] == "Other"
    assert views["a"]["citations"][0]["id"] == "n"
    assert "Definition of earrings" in views["a"]["text"]


def test_definition_reference_resolves_only_exact_source_subparagraph():
    from rag.retrieval import definition_passages

    records = [
        {
            "id": "tt31:n",
            "namespace": "hs_classification",
            "role": "evidence",
            "source_text": "See Note 9(a)",
            "locator": {},
        },
        {"id": "tt31:parent", "source_text": "(a) Earrings. (b) Personal boxes.", "locator": {}},
        {
            "id": "tt31:leaf",
            "chunk_type": "tariff_entry",
            "level": 8,
            "embedding_text": "Jewellery",
            "source_text": "Other",
        },
    ]
    nodes = [{"id": "tt31:fragment", "metadata": {"parent_note_id": "parent", "label": "9(a)"}}]
    edges = [
        {"source": "tt31:n", "relation": "DEFINES_FOR", "target": "tt31:leaf"},
        {"source": "tt31:n", "relation": "REFERS_TO", "target": "tt31:fragment"},
    ]
    views = definition_passages(records, nodes, edges)
    assert "Earrings" in views["tt31:leaf"]["text"]
    assert "Personal boxes" not in views["tt31:leaf"]["text"]


def test_disabled_definition_branch_preserves_baseline_and_new_candidates_can_enter():
    from rag.retrieval import definition_fusion

    base = [{"id": "a", "code": "11111111", "score": 1}]
    added = [{"id": "b", "code": "22222222", "score": 7}]
    assert definition_fusion(base, added, 0, 20) == base
    assert definition_fusion(base, [], 0.5, 20) == base
    assert definition_fusion(base, added, 1, 20)[0]["id"] == "b"


def test_qa_coverage_requires_all_groups_and_respects_alternatives():
    from rag.evaluation import qa_coverage

    case = {
        "id": "QA",
        "query": "rules",
        "canonical_groups": [
            {"label": "first", "any_of": ["gir:a", "gir:b"]},
            {"label": "second", "any_of": ["tt85:c"]},
        ],
    }
    first = {"id": "gir:b", "dataset": "gir", "metadata": {}, "locator": "GIR"}
    second = {
        "id": "tt85:context",
        "dataset": "tt85",
        "metadata": {"context_source_ids": ["c"]},
        "locator": "Article",
    }
    result = qa_coverage(case, [first], [first, second])
    assert result["group_recall@10"] == 0.5
    assert not result["all_groups@10"]
    assert result["package_all_groups"]
    assert result["mrr@10"] == 1
    wrong_dataset = {**second, "dataset": "gir"}
    assert not qa_coverage(case, [first], [first, wrong_dataset])["package_all_groups"]


def test_qa_verified_targets_match_current_sources():
    from rag.evaluation import discover_qa

    cases = discover_qa(build_corpus())
    assert len(cases) == 470
    assert sum(c["split"] == "train" for c in cases) == 320
    assert sum(c["split"] == "test" for c in cases) == 150
    assert next(c for c in cases if c["id"] == "Q001")["canonical_groups"][0]["any_of"] == [
        "tt85:TT85-A2-2"
    ]
    assert next(c for c in cases if c["id"] == "Q200")["canonical_groups"][0]["any_of"] == [
        "tt31:SXVII_NOTE_2"
    ]
    assert next(c for c in cases if c["id"] == "Q201")["canonical_groups"][0]["any_of"] == [
        "tt31:HS4:7105"
    ]
    assert next(c for c in cases if c["id"] == "LQ150")["canonical_groups"][0]["any_of"] == [
        "tt85:TT85-A16-1"
    ]


@pytest.mark.parametrize(
    "query,status",
    [
        ("Có được phân loại vào nhóm 84.82 không?", "QUESTIONED"),
        ("Hàng không thuộc nhóm 85.18", "NEGATED"),
        ("Tra cứu mô tả nhóm 84.82", "MENTIONED"),
        ("Thiết bị không dây của nhóm 85.18", "MENTIONED"),
    ],
)
def test_uncertain_code_mentions_do_not_become_legal_exclusions(query, status):
    from rag.retrieval import Retriever, code_mention_plan

    plan = code_mention_plan(query + " USB-C 65 W")
    assert plan["semantic_query"] == query + " USB-C 65 W"
    assert plan["code_mentions"][0]["status"] == status
    assert "65w" in Retriever.exact_features(plan["exact_query"])
    code = plan["code_mentions"][0]["code"]
    assert (code in Retriever.exact_features(plan["exact_query"])) == (status == "MENTIONED")
    assert plan["exclusion_status"] == "NO_LEGAL_EXCLUSION_DECISION"


def test_gir_sequence_routing_requires_legal_sequence_cues():
    from rag.retrieval import Retriever

    r = Retriever.__new__(Retriever)
    assert (
        r.route("Hàng hóa thuộc nhiều nhóm, thứ tự chọn nhóm thích hợp ra sao?")["intent"] == "gir"
    )
    assert r.route("Máy trộn sản phẩm hỗn hợp, công suất 65 W")["intent"] == "product"
    assert r.route("Thứ tự đóng gói sản phẩm trong hai nhóm máy")["intent"] == "product"


def test_rule_family_expansion_follows_retrieved_atomic_rules(monkeypatch):
    from rag.retrieval import Retriever

    r = Retriever.__new__(Retriever)
    rules = [
        {"source_id": sid, "id": "gir:" + sid}
        for sid in ["GIR_2A", "GIR_2B", "GIR_3A", "GIR_3B", "GIR_3C"]
    ]
    monkeypatch.setattr(r, "documents", lambda *args, **kwargs: rules)
    matches = [{"source_id": "GIR_2A"}]
    assert {
        x["source_id"] for x in r.rule_family_evidence("Trình tự áp dụng quy tắc", matches)
    } == {"GIR_2A", "GIR_2B"}
    assert not r.rule_family_evidence("Giải thích một quy tắc", matches)
    assert not r.rule_family_evidence("Trình tự áp dụng quy tắc", [{"source_id": "GIR_3_NOTE_015"}])


def test_qa_direct_scoring_requires_atomic_chunk_not_context_alias():
    from rag.evaluation import qa_direct_coverage

    case = {
        "id": "QA",
        "query": "q",
        "canonical_groups": [{"label": "note", "any_of": ["tt31:NOTE"]}],
    }
    derived = {
        "id": "tt31:TARIFF",
        "dataset": "tt31",
        "locator": {"page": 1},
        "metadata": {"context_source_ids": ["NOTE"]},
    }
    assert not qa_direct_coverage(case, [derived])["all_groups@10"]


def test_qa_reranker_preserves_multiple_chunks_without_hs_codes():
    from rag.retrieval import rerank_evidence

    class FakeReranker:
        def score(self, query, texts):
            return [1.0, 2.0]

    rows = [
        {"id": sid, "code": None, "score": 1.0, "embedding_text": sid}
        for sid in ("gir:GIR_3A", "gir:GIR_3B")
    ]
    ranked = rerank_evidence("rule", rows, FakeReranker(), 2, 1.0, 20)
    assert [r["id"] for r in ranked] == ["gir:GIR_3B", "gir:GIR_3A"]


def test_qa_graph_pool_keeps_direct_results_and_real_cited_neighbors():
    from rag.retrieval import qa_candidate_pool

    direct = [{"id": key, "score": 1.0} for key in "abcd"]
    parents = [
        {"id": "parent", "source_text": "Nhóm 85.34", "locator": {"page": 1}},
        {"id": "structural", "source_text": "", "locator": {"page": 1}},
    ]
    notes = [
        {"id": "note", "source_text": "Chú giải 8", "locator": {"page": 2}},
        {"id": "a", "source_text": "duplicate", "locator": {"page": 3}},
    ]
    pooled = qa_candidate_pool(direct, parents, notes, 4, direct_fraction=0.5)
    assert [row["id"] for row in pooled] == ["a", "b", "parent", "note"]
    assert all("score" in row for row in pooled)
    assert [row["id"] for row in qa_candidate_pool(direct, [], [], 4)] == list("abcd")


def test_indexed_corpus_contains_no_english_search_passages():
    rows = build_corpus()["records"]
    contaminated = (
        "EN:",
        "with the apparatus of heading",
        "Of a kind used in radio equipment",
        "Battery clamps, of a kind",
        "Of electric accumulators of a kind",
    )
    assert all(
        not any(fragment in row[field] for fragment in contaminated)
        for row in rows
        for field in ("embedding_text", "lexical_text")
    )
    assert next(row for row in rows if row["id"] == "tt31:SXVI-T-8506")[
        "embedding_text"
    ] == "Mã 85.06; Pin và bộ pin."


def test_qa_weight_sweep_uses_all_primary_sources():
    from rag.evaluation import sweep_qa_weights

    case = {"canonical_groups": [{"any_of": ["a"]}, {"any_of": ["b"]}]}
    cache = [{"case": case, "branches": {"dense": [{"id": "a"}]}}]
    result = sweep_qa_weights(cache, "C1")[0]
    assert result["all_groups@10"] == 0
    assert result["group_recall@10"] == 0.5


def test_routed_legal_query_uses_trained_qa_without_changing_product_dispatch(monkeypatch):
    from rag.retrieval import Retriever

    retriever = object.__new__(Retriever)
    retriever.qa_policy = {"configuration": "C11"}
    retriever.weights = {}
    monkeypatch.setattr(retriever, "qa_search", lambda query: {"matches": [{"id": "qa"}]})
    monkeypatch.setattr(
        retriever, "adaptive_search", lambda query, **kw: {"candidates": [{"id": "hs"}]}
    )
    retriever.cfg = {"rrf_k": 60}
    assert retriever.routed_search("Quy tắc GIR 6 là gì?")["matches"] == [{"id": "qa"}]
    assert retriever.routed_search("Máy bơm nước 65W")["candidates"] == [{"id": "hs"}]
