"""Disjoint generation stage measurements use wall time, including repairs and reviews."""

import json
from collections import deque
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm import answering
from rag.llm.groq_client import GroqClient, GroqError
from rag.prompts.schemas import ANSWER_SCHEMA, PRODUCT_REVIEW_SCHEMA
from tests.support.legacy_generation import prepare_legacy_context as prepare_context


class Clock:
    def __init__(self):
        self.seconds = 0.0
        self.validation_ms = 0.0

    def now(self):
        return self.seconds

    def advance(self, milliseconds):
        self.seconds += milliseconds / 1000

    def cpu(self, milliseconds):
        self.validation_ms += milliseconds
        self.advance(milliseconds)


def context():
    rows = [
        {"id": "heading", "code": "8517", "source_text": "Telephone apparatus"},
        {"id": "subheading", "code": "851713", "source_text": "Smartphones"},
        {"id": "leaf", "code": "85171300", "source_text": "Smartphones"},
    ]
    graph = GraphContext(
        rows,
        [],
        [
            {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
            {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
        ],
    )
    return prepare_context(
        "A handheld wireless telephone.",
        {"hs_candidates": [rows[-1]]},
        "auto",
        GroqConfig(keys=("fixture",)),
        graph,
    )


def recommendation(ctx):
    return {
        "status": "RECOMMENDATION",
        "answer": "Đề xuất mã theo nguồn "
        + " ".join(f"[{source['label']}]" for source in ctx["sources"]),
        "suggested_hs_code": "85171300",
        "alternatives": [],
        "citations": [{"label": s["label"], "quote": s["text"]} for s in ctx["sources"]],
        "missing_information": [],
        "missing_legal_evidence": [],
    }


def supported_review(ctx):
    return {
        "status": "SUPPORTED",
        "reason": "Các dữ kiện được xác nhận đáp ứng điều kiện trong nguồn được cấp.",
        "product_facts": [{"fact": "Handheld wireless telephone", "user_quote": ctx["question"]}],
        "condition_checks": [
            {
                "source_label": source["label"],
                "source_quote": source["text"],
                "assessment": "SATISFIED",
                "product_fact_indices": [0],
            }
            for source in ctx["sources"]
        ],
        "missing_information": [],
        "missing_legal_evidence": [],
    }


def legal_abstention():
    return {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Chưa đủ chứng cứ pháp lý trong ngữ cảnh để kết luận.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": [
            "Nguồn pháp lý áp dụng cho loại hàng thực tế chưa được xác minh."
        ],
    }


def instrument_validation(monkeypatch, clock, extra_modules=()):
    for module in (answering, *extra_modules):
        monkeypatch.setattr(module, "perf_counter", clock.now)
        for name, milliseconds in (("validate_answer", 11), ("schema_errors", 7)):
            original = getattr(module, name)

            def timed(*args, _original=original, _milliseconds=milliseconds, **kwargs):
                clock.cpu(_milliseconds)
                return _original(*args, **kwargs)

            monkeypatch.setattr(module, name, timed)
    parse = answering.json.loads

    def timed_parse(*args, **kwargs):
        clock.cpu(3)
        return parse(*args, **kwargs)

    monkeypatch.setattr(answering.json, "loads", timed_parse)


def client_for(clock, entries, calls):
    queue = deque(entries)

    def complete(_messages, schema, **kwargs):
        calls.append((schema, kwargs))
        milliseconds, value = queue.popleft()
        clock.advance(milliseconds)
        if isinstance(value, Exception):
            raise value
        return {
            "content": value if isinstance(value, str) else json.dumps(value),
            "finish_reason": "stop",
            "model": "fixture-model",
            # Deliberately differs from wall time: stage timing must not sum provider metadata.
            "elapsed_ms": 99999,
            "fallback_used": len(calls) == 1,
        }

    return SimpleNamespace(complete=complete)


def assert_disjoint_timings(result, clock, answer_ms, review_ms, decision_ms=0):
    timings = result["timings"]
    assert timings["answer_llm_ms"] == pytest.approx(answer_ms)
    assert timings["product_review_llm_ms"] == pytest.approx(review_ms)
    assert timings.get("decision_review_llm_ms", 0) == pytest.approx(decision_ms)
    assert timings["llm_ms"] == pytest.approx(answer_ms + review_ms + decision_ms)
    assert timings["validation_ms"] == pytest.approx(clock.validation_ms)
    assert timings["total_ms"] == pytest.approx(clock.seconds * 1000)
    assert timings["llm_ms"] + timings["validation_ms"] <= timings["total_ms"] + 1e-9


def test_repairs_and_product_review_accumulate_disjoint_wall_time(monkeypatch):
    ctx, clock = context(), Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock)
    client = client_for(
        clock,
        [(200, "not json"), (300, recommendation(ctx)), (700, supported_review(ctx))],
        calls,
    )
    result = answering.generate_answer(ctx, client)
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "RECOMMENDATION"
    assert [schema for schema, _ in calls] == [ANSWER_SCHEMA, ANSWER_SCHEMA, PRODUCT_REVIEW_SCHEMA]
    assert calls[0][1]["allow_fallback"] is True
    assert calls[1][1]["allow_fallback"] is False
    assert calls[2][1]["allow_fallback"] is False
    assert_disjoint_timings(result, clock, 500, 700)
    assert result["timings"]["validation_ms"] > 0


def test_missing_qa_sources_measure_validation_without_calling_a_model(monkeypatch):
    ctx = prepare_context("A question", {}, "qa", GroqConfig(keys=("fixture",)))
    clock = Clock()
    instrument_validation(monkeypatch, clock)
    client = GroqClient(GroqConfig(keys=("fixture",)))
    monkeypatch.setattr(client, "complete", lambda *a, **k: pytest.fail("Unexpected model call"))
    result = answering.generate_answer(ctx, client)
    assert result["generation"]["skipped"]
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert result["validation"]["valid"]
    assert_disjoint_timings(result, clock, 0, 0)
    assert result["timings"]["validation_ms"] > 0


def test_review_repair_is_included_without_overlap_with_validation(monkeypatch):
    ctx, clock = context(), Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock)
    client = client_for(
        clock,
        [(200, recommendation(ctx)), (700, "not json"), (300, supported_review(ctx))],
        calls,
    )
    result = answering.generate_answer(ctx, client)
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "RECOMMENDATION"
    assert [schema for schema, _ in calls] == [
        ANSWER_SCHEMA,
        PRODUCT_REVIEW_SCHEMA,
        PRODUCT_REVIEW_SCHEMA,
    ]
    assert len(result["generation"]["product_review"]["attempts"]) == 2
    assert_disjoint_timings(result, clock, 200, 1000)


def test_unavailable_review_keeps_failed_request_wall_time(monkeypatch):
    ctx, clock = context(), Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock)
    client = client_for(
        clock,
        [(200, recommendation(ctx)), (700, GroqError(503, "fixture-model"))],
        calls,
    )
    result = answering.generate_answer(ctx, client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert not result["generation"]["product_review"]["valid"]
    assert result["generation"]["product_review"]["http_status"] == 503
    assert result["validation"]["valid"]
    assert_disjoint_timings(result, clock, 200, 700)


def test_failed_main_request_exposes_measurement_on_safe_provider_error(monkeypatch):
    ctx, clock = context(), Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock)
    error = GroqError(503, "fixture-model")
    client = client_for(clock, [(500, error)], calls)
    with pytest.raises(GroqError) as raised:
        answering.generate_answer(ctx, client)
    assert raised.value is error
    assert error.timings["llm_ms"] == pytest.approx(500)
    assert error.timings["answer_llm_ms"] == pytest.approx(500)
    assert error.timings["product_review_llm_ms"] == 0
    assert error.timings["validation_ms"] == 0


def test_unavailable_decision_review_is_included_in_total_llm_wall_time(monkeypatch):
    from rag.llm import decision_review

    ctx, clock = context(), Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock, (decision_review,))
    client = client_for(
        clock,
        [(200, legal_abstention()), (700, GroqError(503, "fixture-model"))],
        calls,
    )
    result = answering.generate_answer(ctx, client)
    assert result["validation"]["valid"]
    assert not result["generation"]["decision_review"]["valid"]
    assert result["generation"]["decision_review"]["http_status"] == 503
    assert len(calls) == 2
    assert calls[1][1]["allow_fallback"] is False
    assert_disjoint_timings(result, clock, 200, 0, 700)


def test_empty_hs_context_skips_main_but_measures_independent_decision_review(monkeypatch):
    from rag.llm import decision_review

    ctx = prepare_context(
        "A product described by its trade name", {}, "auto", GroqConfig(keys=("fixture",))
    )
    clock = Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock, (decision_review,))
    client = client_for(clock, [(700, GroqError(503, "fixture-model"))], calls)
    result = answering.generate_answer(ctx, client)
    assert result["validation"]["valid"]
    assert result["generation"]["main_skipped"]
    assert not result["generation"]["decision_review"]["valid"]
    assert len(calls) == 1
    assert calls[0][0] is not ANSWER_SCHEMA
    assert calls[0][0] is not PRODUCT_REVIEW_SCHEMA
    assert result["answer"]["suggested_hs_code"] == ""
    assert_disjoint_timings(result, clock, 0, 0, 700)


def test_decision_review_repair_separates_both_model_calls_from_local_validation(monkeypatch):
    from rag.llm import decision_review

    ctx, clock = context(), Clock()
    calls: list[tuple[dict, dict]] = []
    instrument_validation(monkeypatch, clock, (decision_review,))
    kept = {
        "request_kind": "HS",
        "identity_status": "IDENTIFIED",
        "product_type": "telephone",
        "product_type_quote": "telephone",
        "decision": "KEEP",
        "reason": "Chưa đủ chứng cứ để kết luận cho đối tượng đã xác nhận.",
        "retained_qa": {"answer": "", "citations": []},
        "clarifications": [],
    }
    client = client_for(
        clock,
        [(200, legal_abstention()), (400, "not json"), (600, kept)],
        calls,
    )
    result = answering.generate_answer(ctx, client)
    assert result["validation"]["valid"]
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["generation"]["decision_review"]["valid"]
    assert len(result["generation"]["decision_review"]["attempts"]) == 2
    assert len(calls) == 3
    assert calls[1][1]["allow_fallback"] is False
    assert calls[2][1]["allow_fallback"] is False
    assert_disjoint_timings(result, clock, 200, 0, 1000)
