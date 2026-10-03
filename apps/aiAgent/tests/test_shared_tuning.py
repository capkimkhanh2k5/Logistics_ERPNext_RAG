"""Source-only vector cache identity and offline/runtime ranking equivalence."""

import datetime
import json

import numpy as np
import pytest

from rag.embedding import Embedder
from rag.retrieval import rerank_candidates
from scripts.benchmark_pdf_rerankers import compact_prediction
from scripts.tune_shared_retrieval import candidate_policies, rank_scored_pool


def test_context_cache_rebuilds_when_source_text_or_model_profile_changes(tmp_path, monkeypatch):
    import rag.embedding as module

    monkeypatch.setattr(module, "ROOT", tmp_path)
    embedder = Embedder.__new__(Embedder)
    embedder.profile = {"revision": "first"}
    embedder.cfg = {"checkpoint_size": 4}
    calls = []

    def encode(texts):
        calls.extend(texts)
        return {"dense": np.ones((len(texts), 1024), dtype=np.float32)}

    monkeypatch.setattr(embedder, "encode", encode)
    views = [{"id": "SOURCE_NEW_CHAPTER", "rerank_text": "Cited source hierarchy"}]
    embedder.source_context_vectors("snapshot", views)
    embedder.source_context_vectors("snapshot", views)
    assert len(calls) == 1
    views[0]["rerank_text"] = "Changed cited source hierarchy"
    embedder.source_context_vectors("snapshot", views)
    assert len(calls) == 2
    embedder.profile = {"revision": "second"}
    embedder.source_context_vectors("snapshot", views)
    assert len(calls) == 3


@pytest.mark.parametrize("pool", [40, 60, 80])
@pytest.mark.parametrize("weight", [0.85, 1.0])
def test_cached_score_replay_matches_runtime_ranking(pool, weight):
    rows = [
        {
            "id": str(i),
            "code": f"{i:08d}",
            "level": 8,
            "score": float(i),
            "embedding_text": str(i),
            "rerank_score": float((i * 13) % 97),
        }
        for i in range(100)
    ]

    class Scorer:
        def score(self, query, texts, use_cache=True):
            return [float((int(text) * 13) % 97) for text in texts]

    expected = rerank_candidates("query", rows, "cross_encoder", None, Scorer(), pool, weight, 60)
    actual = rank_scored_pool(rows, {"rerank_pool": pool, "rank_weight": weight, "rrf_k": 60})
    assert [r["code"] for r in actual["ranked"]] == [r["code"] for r in expected[:10]]


def test_policy_grid_is_shared_and_includes_baseline():
    from rag.data import ROOT, read

    baseline = read(ROOT / "config/hybrid_retrieval.json")
    grid = candidate_policies(baseline)
    assert len(grid) == 24
    assert any(p["weights"] == baseline["weights"] for p in grid.values())
    assert {p["rerank_pool"] for p in grid.values()} == {40, 60, 80}
    assert not any("section_policies" in p or "attribute_penalty" in p for p in grid.values())


def test_runtime_checkpoint_serializes_database_dates_without_changing_rank_or_source_proof():
    row = {
        "id": "source-row",
        "code": "99010000",
        "level": 8,
        "rerank_score": 0.42,
        "rerank_text": "Actual fitted source description",
        "metadata": {"effective_date": datetime.date(2026, 10, 2)},
        "hierarchy_citations": [{"id": "source-parent"}],
        "note_citations": [],
        "rerank_omitted_ids": ["long-optional-note"],
    }
    result = compact_prediction({"ranked": [row], "pool_codes": [row["code"]], "latency_ms": 1.0})
    restored = json.loads(json.dumps(result))
    assert restored["ranked"][0]["code"] == row["code"]
    assert restored["ranked"][0]["rerank_score"] == row["rerank_score"]
    assert restored["ranked"][0]["used_citation_ids"] == ["source-parent"]
    assert restored["ranked"][0]["rerank_omitted_ids"] == ["long-optional-note"]
    assert len(restored["ranked"][0]["model_input_text_hash"]) == 64
    assert row["metadata"]["effective_date"] == datetime.date(2026, 10, 2)
