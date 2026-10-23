"""Complete-run checkpoints, cache independence and confidence-policy integrity."""

import csv

import pytest

from experiments.quyet_small.full_dynamic import decision_action, path, reusable_path
from experiments.quyet_small.full_evaluate import best, summarize
from experiments.quyet_small.full_report import clustered_delta, confirmed
from experiments.quyet_small.full_run import CachedClient
from experiments.quyet_small.full_store import Store


@pytest.mark.parametrize("cached_metrics", [False, True])
def test_recovery_report_supports_reused_pilot_and_full_baseline_schemas(
    tmp_path, monkeypatch, cached_metrics
):
    from experiments.quyet_small import full_report

    sources = [
        {"id": key, "source_text": key, "locator": {"page": index}}
        for index, key in enumerate(("a", "b"), 1)
    ]
    case = {
        "uid": "qa:test",
        "task": "qa",
        "target_groups": [{"any_of": [key]} for key in ("a", "b")],
    }
    base = {"candidate_pool": sources[:1], "ranked_pool": sources[:1], "package": sources[:1]}
    if cached_metrics:
        base["baseline_metrics"] = {"target_recall@160": 0.5}
    context = {
        "6000": {
            "ids": ["a"],
            "budget_met": True,
            "tokens_saved_fraction": 0,
            "target_recall": 0.5,
            "baseline_target_recall": 0.5,
            "protected_preservation": 1,
        }
    }
    trace = {
        "snapshots": [
            {"round": 0, "top10_ids": ["a"], "metrics": {"target_recall@160": 0.5}},
            {"round": 1, "top10_ids": ["a", "b"], "metrics": {"target_recall@160": 1}},
        ],
        "rounds": [{"candidate_ids": ["a", "b"]}],
        "stopping_reason": "MAX_EXTRA_ROUNDS_2",
    }
    store = Store(tmp_path / "checkpoint.sqlite")
    store.put("baseline", "dev", case["uid"], base)
    store.put(
        "judge",
        "dev",
        case["uid"],
        {
            "passages": {"a": {"status": "ok"}},
            "set": decision("NONE", 1, 1),
            "router": {"status": "ok"},
        },
    )
    store.put(
        "dynamic",
        "dev",
        case["uid"],
        {
            "E4": {"0.95": trace},
            "E5": {
                "matrix": [],
                "new_protected_ids": [],
                "package_target_recall": 0.5,
                "baseline_package_target_recall": 0.5,
                "contexts": context,
            },
            "E7": {"0.95": {**trace, "coverage_matrix": [], "contexts": context}},
            "E1_contexts": context,
        },
    )
    monkeypatch.setattr(full_report, "REPORTS", tmp_path)
    monkeypatch.setattr(full_report, "read", lambda path: {"records": sources})
    try:
        audit, errors = full_report.decision_audit(store, "dev", [case])
    finally:
        store.close()
    with (tmp_path / "rounds_dev.csv").open() as handle:
        recovery = list(csv.DictReader(handle))
    assert errors == []
    assert audit["source_integrity"]
    assert len(recovery) == 6
    assert all(row["before"] == "0.5" for row in recovery)
    assert all(row["recovered"] == str(int(row["budget"]) >= 1) for row in recovery)


def test_combined_path_adds_graph_notes_before_its_first_sufficiency_decision():
    leaf = {
        "id": "leaf",
        "source_text": "leaf wording",
        "level": 8,
        "code": "12345678",
        "chunk_type": "tariff_entry",
        "locator": {"page": 1},
    }
    note = {
        "id": "note",
        "source_text": "mandatory note wording",
        "chunk_type": "chapter_note",
        "locator": {"page": 2},
    }

    class Graph:
        records = {"leaf": leaf, "note": note}

        def source_view(self, candidate):
            return {"ancestor_ids": [], "note_ids": ["note"]}

    class Unified:
        graph = Graph()

        def source_package(self, ranked):
            return ranked

    class Client:
        states = []

        def call(self, message):
            responses = []
            for request in message["requests"]:
                self.states.append(request["state"])
                answers = (
                    {"missing": {"choice": "NONE", "confidence": 1}, "sufficient": {"noul": 1}}
                    if "sufficient" in request["questions"]
                    else {key: {} for key in request["questions"]}
                )
                responses.append({"answers": answers, "usage": {"input_tokens": 1}})
            return {"status": "ok", "responses": responses, "elapsed_ms": 1, "peak_rss_mb": 1}

    client = Client()
    case = {
        "task": "hs",
        "query": "query",
        "expected_hs_8": "12345678",
        "target_groups": [{"any_of": ["leaf"]}],
    }
    observation = path(
        client, Unified(), {"case": case}, [leaf], [leaf], {}, 0.5, collect_coverage=True
    )
    assert {row["id"] for row in client.states[-1]["evidence"]} == {"leaf", "note"}
    assert [row["source_text"] for row in observation["package"]] == [
        "leaf wording",
        "mandatory note wording",
    ]
    assert observation["rounds"] == []


def decision(label="UNKNOWN", confidence=0.1, sufficient=0.1):
    return {
        "status": "ok",
        "answers": {
            "missing": {"choice": label, "confidence": confidence},
            "sufficient": {"noul": sufficient},
        },
    }


def test_compressed_checkpoint_is_atomic_and_preserves_vietnamese(tmp_path):
    path = tmp_path / "results.sqlite"
    store = Store(path)
    payload = {"text": "Nhẫn vàng; chú giải loại trừ", "score": 0.1245, "ids": ["source-1"]}
    store.put("baseline", "dev", "a", payload)
    assert store.get("baseline", "dev", "a") == payload
    assert store.count("baseline", "dev") == 1
    store.close()
    reopened = Store(path)
    assert list(reopened.rows("baseline", "dev")) == [payload]
    reopened.close()


def test_confidence_gate_does_not_stop_on_weak_out_of_scope_label():
    assert decision_action(decision("CORPUS_OUT_OF_SCOPE", 0.3, 0.99), 0.7) == (
        "retrieve",
        "UNKNOWN",
    )
    assert decision_action(decision("MISSING_PRODUCT_FACT", 0.99), 0.7) == (
        "stop",
        "MISSING_PRODUCT_FACT",
    )


def test_sufficiency_signal_alone_cannot_bypass_missing_information():
    assert decision_action(decision("MISSING_CORPUS_EVIDENCE", 0.99, 0.99), 0.7) == (
        "retrieve",
        "MISSING_CORPUS_EVIDENCE",
    )
    assert decision_action(decision("NONE", 0.99, 0.99), 0.7)[0] == "stop"


def test_threshold_replay_checks_later_decisions_not_just_first_action():
    path = {
        "threshold": 0.5,
        "snapshots": [
            {"round": 0, "decision": decision()},
            {"round": 1, "decision": decision("NONE", 0.8, 0.9)},
        ],
    }
    assert reusable_path(path, 0.7)
    assert not reusable_path(path, 0.95)


def test_terminal_round_two_decision_cannot_trigger_a_third_retrieval():
    path = {
        "threshold": 0.5,
        "snapshots": [
            {"round": 0, "decision": decision()},
            {"round": 1, "decision": decision()},
            {"round": 2, "decision": decision("NONE", 0.8, 0.9)},
        ],
    }
    assert reusable_path(path, 0.95)


def test_macro_code_metric_does_not_overweight_many_cases_of_the_same_code():
    cases = [
        {"uid": "h1", "task": "hs", "expected_hs_8": "a"},
        {"uid": "h2", "task": "hs", "expected_hs_8": "a"},
        {"uid": "h3", "task": "hs", "expected_hs_8": "b"},
        {"uid": "q", "task": "qa"},
    ]
    observations = {
        "h1": {"hs8_mrr@10": 1, "hs8_hit@10": 1},
        "h2": {"hs8_mrr@10": 1, "hs8_hit@10": 1},
        "h3": {"hs8_mrr@10": 0, "hs8_hit@10": 0},
        "q": {"target_all_groups@10": 1},
    }
    result = summarize(cases, observations)
    assert result["hs"]["macro_code_metrics"]["hs8_mrr@10"] == 0.5
    assert result["objective"] == 0.75


def test_selection_rejects_a_global_score_gain_that_loses_legal_primary_coverage():
    def summary(objective, legal):
        return {
            "objective": objective,
            "hs": {"macro_code_metrics": {"hs8_hit@10": 1}, "metrics": {"target_ndcg@10": 1}},
            "qa": {"metrics": {"target_all_groups@10": legal, "target_ndcg@10": 1}},
        }

    values = {"E0": summary(0.8, 0.9), "E3_w0.2": summary(0.85, 0.8)}
    assert best(values, list(values)) == "E0"


def test_paired_intervals_preserve_family_dependence():
    cases = [
        {"uid": "a", "bootstrap_group": "family"},
        {"uid": "b", "bootstrap_group": "family"},
    ]
    base = {"a": {"hit": 0}, "b": {"hit": 1}}
    new = {"a": {"hit": 1}, "b": {"hit": 0}}
    result = clustered_delta(cases, base, new, "hit")
    assert result["n_clusters"] == 1
    assert result["delta"] == 0
    assert result["ci95"] == [0, 0]
    assert result["improved_queries"] == result["regressed_queries"] == 1


def test_test_confirmation_rejects_an_uncertain_gain_and_never_retunes():
    baseline = {
        "objective": 0.8,
        "hs": {"macro_code_metrics": {"hs8_hit@10": 1}},
        "qa": {"metrics": {"target_all_groups@10": 1}},
    }
    candidate = {**baseline, "objective": 0.81}
    summaries = {"E0": baseline, "locked": candidate}
    intervals = {
        "locked": {
            "objective": {"ci95": [-0.01, 0.03]},
            "mean_target_ndcg@10": {"ci95": [-0.01, 0.03]},
        }
    }
    assert not confirmed("locked", summaries, intervals, 0)
    intervals["locked"]["objective"]["ci95"] = [0.001, 0.03]
    assert confirmed("locked", summaries, intervals, 0)
    assert not confirmed("locked", summaries, intervals, 1)
    assert confirmed("E0", summaries, intervals, 0)


def test_cached_question_is_independent_of_other_questions_and_invalidated_by_state(
    tmp_path, monkeypatch
):
    identity = {"model_sha256": "sha", "runtime": {"quyet": "pinned"}}
    calls = []

    class FakeClient:
        ready = identity

        def __init__(self, path):
            pass

        def call(self, message):
            if "requests" not in message:
                return {"status": "ok"}
            calls.append(message)
            return {
                "status": "ok",
                "responses": [
                    {
                        "answers": {
                            qid: {"type": "noul", "noul": 0.75} for qid in request["questions"]
                        },
                        "usage": {"input_tokens": 10},
                        "warnings": [],
                    }
                    for request in message["requests"]
                ],
                "elapsed_ms": 1,
                "peak_rss_mb": 1,
            }

        def close(self):
            pass

    monkeypatch.setattr("experiments.quyet_small.full_run.Client", FakeClient)
    monkeypatch.setattr("experiments.quyet_small.full_run.read", lambda path: {"model": identity})
    store = Store(tmp_path / "cache.sqlite")
    client = CachedClient(store)
    question = {"type": "noul", "instructions": "The source is useful"}
    request = {"state": {"query": "nhẫn vàng"}, "questions": {"useful": question}}
    first = client.call({"requests": [request]})
    second = client.call({"requests": [request]})
    assert first["responses"][0]["answers"] == second["responses"][0]["answers"]
    assert len(calls) == 1
    client.call({"requests": [{**request, "state": {"query": "nhẫn bạc"}}]})
    assert len(calls) == 2
    client.close()
    store.close()
