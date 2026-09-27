import numpy as np
import pytest

from rag.data import GOLD, audit, build_corpus, normalize_code, read
from rag.embedding import validate_vectors
from rag.evaluation import grouped_split, metrics, query_for
from rag.retrieval import fuse, unique_codes


def test_corpus_integrity_and_provenance():
    report = audit()
    assert report["gold_count"] == 50
    assert report["graph_edges"] == 3762
    first, second = build_corpus(), build_corpus()
    assert first["snapshot"] == second["snapshot"]
    assert len(first["records"]) == 3738
    assert all(r["locator"] for r in first["records"])
    assert not any("test/" in p for p in first["manifest"]["source_hashes"])
    assert len({r["id"] for r in first["records"]}) == 3738
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


def test_gold_never_enters_query_and_split_is_grouped():
    gold = read(GOLD)
    split = grouped_split()
    dev = {g["expected_hs_8"] for g in gold if g["test_id"] in split["dev"]}
    test = {g["expected_hs_8"] for g in gold if g["test_id"] in split["test"]}
    assert dev.isdisjoint(test)
    assert len(split["dev"]) + len(split["test"]) == 50
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
    assert len([r for r in rows if r.startswith("tt85:TT85-FORM-")]) == 5


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
