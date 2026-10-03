"""Offline batching must preserve query/model cache boundaries and pair order."""

from types import SimpleNamespace

from rag.embedding import CrossEncoder


def test_bulk_scores_keep_queries_separate_and_reuse_only_identical_model_pairs(tmp_path):
    encoder = CrossEncoder.__new__(CrossEncoder)
    encoder.model_id = "fixture-reranker"
    encoder.revision = "first-revision"
    encoder.backend = "cross_encoder"
    encoder.batch_size = 4
    encoder.cache = tmp_path
    encoder.model = SimpleNamespace(
        tokenizer=lambda pairs, truncation: {"input_ids": [[1, 2] for _ in pairs]}
    )
    calls = []

    def compute(pairs):
        calls.append(pairs)
        return [float(ord(query[-1]) + len(text)) for query, text in pairs]

    encoder.compute_scores = compute
    requests = [("query-a", ["same", "short", "same"]), ("query-b", ["same"])]
    expected = [[101.0, 102.0, 101.0], [102.0]]
    assert encoder.score_many(requests) == expected
    assert len(calls[0]) == 3
    assert encoder.score_many(requests) == expected
    assert len(calls) == 1
    assert encoder.score("query-a", ["short", "same"]) == [102.0, 101.0]
    assert len(calls) == 1
    encoder.revision = "second-revision"
    assert encoder.score_many(requests) == expected
    assert len(calls) == 2
