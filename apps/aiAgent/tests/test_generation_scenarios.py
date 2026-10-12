"""Scenario behavior, clarification isolation, and fault injection without network calls."""

import json
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.answering import compose_query
from rag.groq_client import GroqClient
from tests.support.generation_scenarios import (
    _generate,
    check_expectations,
    run_scenarios,
)


def answered(status="ANSWERED"):
    return {
        "status": status,
        "answer": "Căn cứ hồ sơ [S1]." if status == "ANSWERED" else "Cần rõ loại tài liệu.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [{"label": "S1", "quote": "Nội dung hồ sơ"}] if status == "ANSWERED" else [],
        "missing_information": ["Loại tài liệu"] if status == "NEED_MORE_INFORMATION" else [],
    }


def test_combined_query_preserves_user_supplements_and_enforces_total_budget():
    query = compose_query("Câu hỏi", ["Vật liệu", "Công dụng"], 200)
    assert query.startswith("Câu hỏi")
    assert "Vật liệu" in query and "Công dụng" in query
    with pytest.raises(ValueError, match="Combined question"):
        compose_query("Câu hỏi", ["x" * 200], 100)
    with pytest.raises(ValueError, match="Additional context"):
        compose_query("Câu hỏi", [" "], 100)


def test_valid_json_does_not_pass_a_missing_information_scenario_if_it_selects_a_code():
    generated = {
        "answer": {**answered(), "status": "RECOMMENDATION", "suggested_hs_code": "85171300"},
        "validation": {"valid": True},
        "generation": {},
    }
    result = check_expectations(
        {"expected_statuses": ["NEED_MORE_INFORMATION"], "require_missing_information": True},
        generated,
    )
    assert not result["passed"]
    assert not result["checks"]["expected_status"]
    assert not result["checks"]["asks_for_information"]


def test_clarification_retrieves_again_and_does_not_carry_facts_to_another_scenario(
    monkeypatch, tmp_path
):
    queries, messages = [], []
    monkeypatch.setattr("tests.support.generation_scenarios.load_generation_graph", lambda _: None)

    def retrieve(case, *args):
        queries.append(case["query"])
        return {"matches": [{"id": "a", "source_text": "Nội dung hồ sơ"}]}, False

    monkeypatch.setattr("tests.support.generation_scenarios.retrieval_for", retrieve)

    def complete(prompt, *args, **kwargs):
        messages.append(prompt)
        status = "NEED_MORE_INFORMATION" if len(messages) == 1 else "ANSWERED"
        return {"content": json.dumps(answered(status)), "finish_reason": "stop", "model": "main"}

    client = SimpleNamespace(config=GroqConfig(keys=("x",)), complete=complete)
    retriever = SimpleNamespace(snapshot="s", profile="p", unified_policy={})
    scenarios = [
        {
            "id": "a",
            "name": "Clarify",
            "task": "qa",
            "question": "Tài liệu nào?",
            "turns": [
                {"expected_statuses": ["NEED_MORE_INFORMATION"]},
                {"supplement": "Thông tin chỉ thuộc phiên A", "expected_statuses": ["ANSWERED"]},
            ],
        },
        {
            "id": "b",
            "name": "Independent",
            "task": "qa",
            "question": "Câu hỏi phiên B",
            "turns": [{"expected_statuses": ["ANSWERED"]}],
        },
    ]
    report = run_scenarios(scenarios, retriever, client, tmp_path, progress=lambda _: None)
    assert all(r["passed"] for r in report["rows"])
    assert len(queries) == 3
    assert queries[0] != queries[1]
    assert "Thông tin chỉ thuộc phiên A" in queries[1]
    assert "Thông tin chỉ thuộc phiên A" not in queries[2]
    assert "Cần rõ loại tài liệu" not in messages[1][1]["content"]


def test_empty_input_is_rejected_without_retrieval_or_api(monkeypatch, tmp_path):
    monkeypatch.setattr("tests.support.generation_scenarios.load_generation_graph", lambda _: None)
    monkeypatch.setattr(
        "tests.support.generation_scenarios.retrieval_for",
        lambda *a: pytest.fail("Unexpected retrieval"),
    )
    client = SimpleNamespace(
        config=GroqConfig(keys=("x",)), complete=lambda *a: pytest.fail("Unexpected API")
    )
    retriever = SimpleNamespace(snapshot="s", profile="p", unified_policy={})
    case = {
        "id": "empty",
        "name": "Empty",
        "task": "qa",
        "question": " ",
        "turns": [{"expected_error": "Question must not be empty"}],
    }
    report = run_scenarios([case], retriever, client, tmp_path, progress=lambda _: None)
    assert report["rows"][0]["run_status"] == "INPUT_REJECTED"
    assert report["rows"][0]["passed"]


def test_simulated_primary_failure_calls_fallback_and_restores_the_client(monkeypatch):
    client = GroqClient(GroqConfig(keys=("x",)))
    calls = []

    def request(path, payload=None):
        calls.append(payload["model"])
        return {
            "choices": [{"message": {"content": json.dumps(answered())}, "finish_reason": "stop"}]
        }, 1

    monkeypatch.setattr(client, "_request", request)
    context = {
        "sources": [{"label": "S1", "id": "a", "text": "Nội dung hồ sơ"}],
        "messages": [],
        "task": "qa",
        "allowed_hs_codes": [],
    }
    result = _generate(context, client, "primary_unavailable")
    assert calls == [client.config.fallback_model]
    assert result["generation"]["fallback_used"]
    assert result["generation"]["failures"][0]["http_status"] == 503
    assert client._request is request


def test_source_coverage_and_schema_are_checked_separately():
    generated = {
        "answer": answered(),
        "validation": {"valid": True, "cited_source_ids": ["wrong"]},
        "generation": {},
    }
    result = check_expectations(
        {"gold_case": {"canonical_groups": [{"any_of": ["right"]}]}}, generated
    )
    assert result["checks"]["valid_output"]
    assert not result["checks"]["expected_sources_cited"]
    assert not result["passed"]
