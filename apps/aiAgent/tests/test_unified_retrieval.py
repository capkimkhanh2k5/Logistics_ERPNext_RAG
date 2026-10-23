"""The common flow must not discard evidence by task or code identity."""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from rag.embedding.bge_m3 import Embedder
from rag.retrieval.rerankers import CrossEncoder
from rag.retrieval.retriever import Retriever
from rag.retrieval.unified import UnifiedRetrieval, hs_projection, id_pool
from rag.utils.files import digest, write_json
from scripts.benchmark_unified_retrieval import pool_coverage
from tests.support.evaluation import qa_direct_coverage


def test_unified_source_index_rejects_a_different_query_embedding_space():
    r = SimpleNamespace(profile="active", embedder=SimpleNamespace(profile_id="different"))
    with pytest.raises(ValueError, match="Query embedder differs"):
        UnifiedRetrieval(r, {})


def test_unified_source_index_rejects_changed_defaults_outside_the_selected_policy():
    r = SimpleNamespace(
        profile="active", embedder=SimpleNamespace(profile_id="active"), cfg={"candidate_pool": 500}
    )
    with pytest.raises(ValueError, match="Retrieval settings differ"):
        UnifiedRetrieval(r, {"retrieval_config": {"candidate_pool": 50}})


def test_auto_requires_locked_common_policy_without_falling_back_to_keyword_routing(monkeypatch):
    r = Retriever.__new__(Retriever)
    monkeypatch.setattr(r, "route", lambda _: (_ for _ in ()).throw(AssertionError("Hard routing")))
    with pytest.raises(ValueError, match="Activate a locked unified"):
        r.routed_search("Generic question")


def test_failed_checkpoint_commit_preserves_previous_json(tmp_path, monkeypatch):
    target = tmp_path / "checkpoint.json"
    write_json(target, {"completed": 40})
    previous = target.read_bytes()

    def fail_replace(self, destination):
        raise OSError("Interrupted checkpoint commit")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="Interrupted checkpoint"):
        write_json(target, {"completed": 45})
    assert target.read_bytes() == previous
    assert not list(tmp_path.glob(".*.tmp"))


def test_legal_pool_coverage_accepts_one_source_per_alternative_group():
    case = {
        "task": "qa",
        "canonical_groups": [
            {"any_of": ["a", "alternative-a"]},
            {"any_of": ["b"]},
        ],
    }
    assert pool_coverage(case, [{"id": "a"}, {"id": "b"}]) == 1
    assert pool_coverage(case, [{"id": "alternative-a"}]) == 0.5


def test_hs_pool_coverage_requires_tariff_leaf_not_a_note_with_the_same_code():
    case = {"task": "hs", "expected_hs_8": "71100000"}
    rows = [{"id": "note", "code": "71100000", "level": 8, "chunk_type": "tariff_footnote"}]
    assert pool_coverage(case, rows) == 0
    rows.append({"id": "leaf", "code": "71100000", "level": 8, "chunk_type": "tariff_entry"})
    assert pool_coverage(case, rows) == 1


def test_common_auto_and_explicit_hints_never_call_keyword_router(monkeypatch):
    r = Retriever.__new__(Retriever)
    r.unified_policy = {"version": "fixture"}
    monkeypatch.setattr(r, "route", lambda _: (_ for _ in ()).throw(AssertionError("Hard routing")))
    monkeypatch.setattr(
        r,
        "unified_search",
        lambda query, intent_hint: {"matches": ["legal", "hs"], "hint": intent_hint},
    )
    for query in (
        "Kim cương thô",
        "Hệ thống HS gồm các thành phần nào?",
        "87031010",
        "Chương mới chưa gặp",
    ):
        for hint in ("auto", "product", "qa"):
            assert r.routed_search(query, intent=hint)["matches"] == ["legal", "hs"]


def test_cited_ids_with_same_hs_code_and_no_code_survive_pooling():
    rows = [
        {"id": "leaf", "code": "71100000", "score": 3},
        {"id": "note", "code": "71100000", "score": 2},
        {"id": "rule", "code": None, "score": 1},
        {"id": "clause", "code": None, "score": 0.5},
    ]
    result = id_pool(
        {"direct": rows, "context": list(reversed(rows))}, {"direct": 0.7, "context": 0.3}, 4
    )
    assert {r["id"] for r in result} == {"leaf", "note", "rule", "clause"}


def test_hs_projection_is_output_only_and_legal_top10_remains_mixed():
    rows = [
        {"id": "clause", "chunk_type": "legal_clause", "level": None, "code": None},
        {"id": "hs", "chunk_type": "tariff_entry", "level": 8, "code": "71100000"},
    ]
    assert [r["id"] for r in hs_projection(rows)] == ["hs"]
    assert [r["id"] for r in rows] == ["clause", "hs"]
    case = {"id": "q", "query": "query", "canonical_groups": [{"label": "a", "any_of": ["needed"]}]}
    evidence = [
        {
            "id": "hs",
            "dataset": "source",
            "metadata": {"context_source_ids": ["needed"]},
            "locator": {"page": 1},
        }
    ]
    assert not qa_direct_coverage(case, evidence)["all_groups@10"]


def test_cascade_scores_original_source_notes_after_first_stage_budget(monkeypatch):
    import rag.retrieval.unified as module

    u = UnifiedRetrieval.__new__(UnifiedRetrieval)
    u.policy = {
        "model": "cascade",
        "rerank_pool": 2,
        "rank_weight": 1,
        "rrf_k": 60,
        "cascade_pool": 1,
        "cascade_weight": 1,
    }
    seen = []

    class Encoder:
        def __init__(self, name):
            self.name = name

        def score(self, query, texts):
            seen.append((self.name, texts))
            return [2 - i for i in range(len(texts))]

    u.encoder = lambda name: Encoder(name)
    monkeypatch.setattr(
        module,
        "fit_inputs",
        lambda q, rows, encoder: [
            {**r, "rerank_text": "trimmed" if encoder.name == "m3" else r["rerank_text"]}
            for r in rows
        ],
    )
    u.rank(
        "query",
        [
            {"id": "a", "rerank_text": "full source and notes"},
            {"id": "b", "rerank_text": "other source"},
        ],
    )
    assert seen == [("m3", ["trimmed", "trimmed"]), ("qwen", ["full source and notes"])]


def test_unified_search_measures_retrieval_and_ranking_without_overlap(monkeypatch):
    import rag.retrieval.unified as module

    clock = SimpleNamespace(value=0.0)
    monkeypatch.setattr(module.time, "perf_counter", lambda: clock.value)
    u = UnifiedRetrieval.__new__(UnifiedRetrieval)
    u.policy = {}
    u.retriever = SimpleNamespace(snapshot="snapshot", profile="profile", coverage={})
    u._rank_timings = {"m3_ms": 999}
    u._rank_encoder_cache_cold = {"m3": True}
    row = {"id": "source", "chunk_type": "legal_clause"}

    def advance(seconds, result):
        clock.value += seconds
        return result

    u.channels = lambda _: advance(0.1, {})
    u.prepare = lambda query, channels: advance(0.2, [row])
    u.rank = lambda query, rows: advance(0.5, rows)
    u.source_package = lambda rows: advance(0.3, rows)
    u.semantic_intent = lambda _: advance(0.4, {"used_for_retrieval": False})

    result = u.search("query")

    assert result["timings"] == pytest.approx(
        {"retrieval_ms": 1000, "reranking_ms": 500, "total_ms": 1500}
    )
    assert result["reranking"]["encoder_cache_cold"] == {}
    assert result["matches"] == [row]


def test_cascade_pass_timings_include_encoder_initialization_only_when_needed(monkeypatch):
    import rag.retrieval.unified as module

    clock = SimpleNamespace(value=0.0)
    monkeypatch.setattr(module.time, "perf_counter", lambda: clock.value)
    u = UnifiedRetrieval.__new__(UnifiedRetrieval)
    u.policy = {
        "model": "cascade",
        "rerank_pool": 2,
        "rank_weight": 1,
        "rrf_k": 60,
        "cascade_pool": 1,
        "cascade_weight": 1,
    }
    u.encoders = {}

    def make_encoder(name):
        clock.value += {"m3": 1, "qwen": 2}[name]

        def score(query, texts):
            clock.value += {"m3": 0.2, "qwen": 0.3}[name]
            return [2 - i for i in range(len(texts))]

        return SimpleNamespace(name=name, score=score)

    def fit_inputs(query, rows, encoder):
        clock.value += {"m3": 0.1, "qwen": 0.2}[encoder.name]
        return rows

    monkeypatch.setattr(module, "make_encoder", make_encoder)
    monkeypatch.setattr(module, "fit_inputs", fit_inputs)
    rows = [{"id": "a", "rerank_text": "a"}, {"id": "b", "rerank_text": "b"}]

    assert [row["id"] for row in u.rank("query", rows)] == ["a", "b"]
    assert u._rank_timings == pytest.approx({"m3_ms": 1300, "qwen_ms": 2500})
    assert u._rank_encoder_cache_cold == {"m3": True, "qwen": True}

    u.rank("query", rows)
    assert u._rank_timings == pytest.approx({"m3_ms": 300, "qwen_ms": 500})
    assert u._rank_encoder_cache_cold == {"m3": False, "qwen": False}


def test_query_timings_include_lazy_unified_index_initialization_once(monkeypatch):
    import rag.retrieval.unified as module

    clock = SimpleNamespace(value=0.0)
    monkeypatch.setattr(module.time, "perf_counter", lambda: clock.value)

    class FakeUnifiedRetrieval:
        def __init__(self, retriever, policy):
            clock.value += 2

        def search(self, query, intent_hint):
            clock.value += 1
            return {"timings": {"retrieval_ms": 600, "reranking_ms": 400, "total_ms": 1000}}

    monkeypatch.setattr(module, "UnifiedRetrieval", FakeUnifiedRetrieval)
    retriever = Retriever.__new__(Retriever)
    retriever.embedder = object()
    retriever.unified_policy = {}

    cold = retriever.unified_search("query")
    assert cold["timings"] == pytest.approx(
        {"initialization_ms": 2000, "retrieval_ms": 2600, "reranking_ms": 400, "total_ms": 3000}
    )
    warm = retriever.unified_search("query")
    assert warm["timings"] == pytest.approx(
        {"initialization_ms": 0, "retrieval_ms": 600, "reranking_ms": 400, "total_ms": 1000}
    )


def test_instruction_changes_score_cache_identity(tmp_path):
    encoder = CrossEncoder.__new__(CrossEncoder)
    encoder.model_id, encoder.revision, encoder.backend = "fixture", "rev", "qwen"
    encoder.device, encoder.batch_size, encoder.max_length = "cpu", 8, 2048
    encoder.cache = tmp_path
    encoder.instruction = "tariff only"
    encoder.model = SimpleNamespace(
        tokenizer=lambda pairs, truncation: {"input_ids": [[1] for _ in pairs]}
    )
    calls = []
    encoder.compute_scores = lambda pairs: calls.append(pairs) or [float(len(calls)) for _ in pairs]
    assert encoder.score("q", ["text"]) == [1]
    encoder.instruction = "all source evidence"
    assert encoder.score("q", ["text"]) == [2]
    assert encoder.score("q", ["text"]) == [2]
    assert len(calls) == 2


def test_reader_package_materializes_only_actual_cited_atomic_sources():
    u = UnifiedRetrieval.__new__(UnifiedRetrieval)
    u.graph = SimpleNamespace(
        records={"note": {"id": "note", "source_text": "Actual source provision"}}
    )
    row = {
        "id": "hs",
        "hierarchy_citations": [{"id": "virtual"}],
        "note_citations": [{"id": "note"}],
    }
    package = u.source_package([row])
    assert [r["id"] for r in package] == ["hs", "note"]
    assert package[1]["source_text"] == "Actual source provision"
    assert row["id"] == "hs"


def test_context_vector_reuse_requires_matching_text_and_embedding_profile(tmp_path, monkeypatch):
    import rag.embedding.bge_m3 as module

    monkeypatch.setattr(module, "ROOT", tmp_path)
    directory = tmp_path / "artifacts/context_embeddings"
    directory.mkdir(parents=True)
    vector = np.zeros((1, 1024), dtype=np.float32)
    vector[0, 0] = 1
    np.savez_compressed(directory / "previous.npz", dense=vector)
    write_json(
        directory / "previous.json",
        {"profile": {"revision": "a"}, "text_hashes": [digest("same source")]},
    )
    e = Embedder.__new__(Embedder)
    e.profile, e.cfg = {"revision": "a"}, {"checkpoint_size": 2}
    calls = []
    e.encode = lambda texts: calls.append(texts) or {"dense": np.repeat(vector, len(texts), axis=0)}
    e.source_context_vectors(
        "snapshot",
        [
            {"id": "new-id", "rerank_text": "same source"},
            {"id": "other", "rerank_text": "changed source"},
        ],
    )
    assert calls == [["changed source"]]
    e.profile = {"revision": "b"}
    e.source_context_vectors("snapshot", [{"id": "new-id", "rerank_text": "same source"}])
    assert calls[-1] == ["same source"]
