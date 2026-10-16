"""Scenario behavior, clarification isolation, and fault injection without network calls."""

import json
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig, RAGGenerationConfig
from rag.llm.context import compose_query
from rag.llm.groq_client import GroqClient
from tests.support.generation_scenarios import (
    _generate,
    check_expectations,
    load_scenarios,
    run_scenarios,
)


def answered(status="ANSWERED"):
    return {
        "status": status,
        "answer": "Căn cứ hồ sơ [S1]." if status == "ANSWERED" else "Cần rõ loại tài liệu.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [{"label": "S1", "quote": "Nội dung hồ sơ"}] if status == "ANSWERED" else [],
        "missing_information": ["Loại tài liệu"] if status == "MISSING_PRODUCT_INFO" else [],
        "missing_legal_evidence": [],
    }


def test_combined_query_preserves_user_supplements_and_enforces_total_budget():
    query = compose_query("Câu hỏi", ["Vật liệu", "Công dụng"], 200)
    assert query.startswith("Câu hỏi")
    assert "Vật liệu" in query and "Công dụng" in query
    with pytest.raises(ValueError, match="Combined question"):
        compose_query("Câu hỏi", ["x" * 200], 100)
    with pytest.raises(ValueError, match="Additional context"):
        compose_query("Câu hỏi", [" "], 100)


def test_token_mode_scenario_rejects_oversized_input_before_retrieval_or_generation(
    monkeypatch, tmp_path
):
    config = RAGGenerationConfig(
        "gemini-3.5-flash-lite", "gpt-oss-120b-medium", None, None, use_model_token_limits=True
    )
    scenario = next(row for row in load_scenarios(config) if row["id"] == "oversized_question")
    monkeypatch.setattr("tests.support.generation_scenarios.load_generation_graph", lambda _: None)
    monkeypatch.setattr(
        "tests.support.generation_scenarios.retrieval_for",
        lambda *args: pytest.fail("Oversized input must be rejected before retrieval"),
    )
    client = SimpleNamespace(
        config=config,
        complete=lambda *args, **kwargs: pytest.fail("Unexpected model call"),
    )
    retriever = SimpleNamespace(snapshot="s", profile="p", unified_policy={})
    report = run_scenarios([scenario], retriever, client, tmp_path, progress=lambda _: None)
    assert report["rows"][0]["run_status"] == "INPUT_REJECTED"
    assert report["rows"][0]["input_error"] == "context_length_exceeded"
    assert report["rows"][0]["passed"]


def test_valid_json_does_not_pass_a_missing_information_scenario_if_it_selects_a_code():
    generated = {
        "answer": {**answered(), "status": "RECOMMENDATION", "suggested_hs_code": "85171300"},
        "validation": {"valid": True},
        "generation": {},
    }
    result = check_expectations(
        {"expected_statuses": ["MISSING_PRODUCT_INFO"], "require_missing_information": True},
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
        status = "MISSING_PRODUCT_INFO" if len(messages) == 1 else "ANSWERED"
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
                {"expected_statuses": ["MISSING_PRODUCT_INFO"]},
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


def test_evidence_gap_expectation_cannot_pass_with_a_user_question():
    generated = {
        "answer": answered("MISSING_PRODUCT_INFO"),
        "validation": {"valid": True},
        "generation": {},
    }
    result = check_expectations({"require_legal_evidence_gap": True}, generated)
    assert not result["passed"]
    generated["answer"] = {
        **answered("INSUFFICIENT_LEGAL_EVIDENCE"),
        "missing_legal_evidence": ["Missing source wording"],
    }
    assert check_expectations({"require_legal_evidence_gap": True}, generated)["passed"]


def test_empty_hs_scenario_requires_identity_review_but_explicit_qa_skips_all_calls():
    scenarios = load_scenarios(GroqConfig(keys=("fixture",)))
    hs = next(row for row in scenarios if row["id"] == "vf9_missing_legal_evidence")["turns"][0]
    assert hs["expect_main_skipped"] and hs["require_decision_review"]
    assert not hs.get("expect_skipped")
    empty_qa = next(
        row
        for row in scenarios
        if row["task"] == "qa" and row["turns"][0].get("mode") == "empty_context"
    )
    assert empty_qa["turns"][0]["expect_skipped"]
    generated = {
        "answer": {
            **answered("INSUFFICIENT_LEGAL_EVIDENCE"),
            "missing_legal_evidence": ["Nguồn liên quan chưa được cấp trong ngữ cảnh."],
        },
        "validation": {"valid": True},
        "generation": {"main_skipped": True, "skipped": False, "decision_review": {"valid": True}},
    }
    assert check_expectations(hs, generated)["passed"]
    generated["generation"]["decision_review"]["valid"] = False
    assert not check_expectations(hs, generated)["passed"]
