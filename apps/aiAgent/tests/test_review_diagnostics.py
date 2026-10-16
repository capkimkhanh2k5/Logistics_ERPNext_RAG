"""Review repair and failure diagnostics preserve usable source evidence."""

import json

import pytest

from config.settings import CLIProxyConfig, GroqConfig
from rag.graph.context import GraphContext
from rag.llm.answering import generate_answer
from rag.llm.client import RAGClient
from rag.llm.cliproxy_client import CLIProxyClient
from rag.llm.context import prepare_context
from rag.llm.groq_client import GroqClient
from rag.prompts.schemas import PRODUCT_REVIEW_SCHEMA


def context(question="Complete equipment made of aluminum for daily use."):
    rows = [
        {"id": "heading", "code": "1111", "level": 4, "source_text": "Complete equipment"},
        {"id": "parent", "code": "111111", "level": 6, "source_text": "Equipment for daily use"},
        {
            "id": "leaf",
            "code": "11111111",
            "level": 8,
            "source_text": "Made of aluminum; mass at most 10 kg.",
        },
    ]
    graph = GraphContext(
        rows,
        [],
        [
            {"source": "heading", "target": "parent", "relation": "CONTAINS"},
            {"source": "parent", "target": "leaf", "relation": "CONTAINS"},
        ],
    )
    return prepare_context(
        question,
        {"hs_candidates": [rows[-1]]},
        "hs",
        GroqConfig(keys=("fixture",)),
        graph,
    )


def recommendation(ctx):
    return {
        "status": "RECOMMENDATION",
        "answer": "Đề xuất 11111111 " + " ".join(f"[{s['label']}]" for s in ctx["sources"]),
        "suggested_hs_code": "11111111",
        "alternatives": [],
        "citations": [{"label": s["label"], "quote": s["text"]} for s in ctx["sources"]],
        "missing_information": [],
        "missing_legal_evidence": [],
    }


def review(ctx, *, status="MISSING_PRODUCT_INFO", assessment="MISSING_PRODUCT_INFO"):
    leaf = next(source for source in ctx["sources"] if source["id"] == "leaf")
    return {
        "status": status,
        "reason": "Chưa có dữ kiện khối lượng để đối chiếu điều kiện của nguồn.",
        "product_facts": [{"fact": "Vật liệu nhôm", "user_quote": "made of aluminum"}],
        "condition_checks": [
            {
                "source_label": leaf["label"],
                "source_quote": "mass at most 10 kg",
                "assessment": assessment,
                "product_fact_indices": [] if assessment == "MISSING_PRODUCT_INFO" else [0],
            }
        ],
        "missing_information": ["Khối lượng thực tế của hàng hóa là bao nhiêu?"]
        if status == "MISSING_PRODUCT_INFO"
        else [],
        "missing_legal_evidence": [],
    }


@pytest.mark.parametrize("defect", ["missing_quantity", "omitted_threshold", "invented_fact"])
def test_supported_review_cannot_skip_a_quantitative_parent_condition(monkeypatch, defect):
    ctx = context()
    unsupported = {
        "status": "SUPPORTED",
        "reason": "Các điều kiện đã được đáp ứng.",
        "product_facts": [
            {
                "fact": "Khối lượng 2 kg" if defect == "invented_fact" else ctx["question"],
                "user_quote": ctx["question"],
            }
        ],
        "condition_checks": [
            {
                "source_label": source["label"],
                "source_quote": "Made of aluminum"
                if source["id"] == "leaf" and defect == "omitted_threshold"
                else source["text"],
                "assessment": "SATISFIED",
                "product_fact_indices": [0],
            }
            for source in ctx["sources"]
        ],
        "missing_information": [],
        "missing_legal_evidence": [],
    }
    responses = iter([recommendation(ctx), unsupported, review(ctx)])
    client = GroqClient(GroqConfig(keys=("fixture",)))
    calls = []

    def complete(messages, schema, **kwargs):
        calls.append(schema)
        return {
            "content": json.dumps(next(responses)),
            "finish_reason": "stop",
            "model": "fixture",
        }

    monkeypatch.setattr(client, "complete", complete)
    generated = generate_answer(ctx, client)
    assert generated["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert generated["answer"]["missing_information"] == [
        "Khối lượng thực tế của hàng hóa là bao nhiêu?"
    ]
    assert generated["answer"]["suggested_hs_code"] == ""
    attempts = generated["generation"]["product_review"]["attempts"]
    assert not attempts[0]["valid"] and attempts[1]["valid"]
    assert len(calls) == 3


def run(monkeypatch, ctx, reviews, main=None):
    client = GroqClient(GroqConfig(keys=("fixture",)))
    calls = []
    pending = iter(reviews)

    def complete(messages, schema, **kwargs):
        calls.append({"schema": schema, "messages": messages, **kwargs})
        if schema is PRODUCT_REVIEW_SCHEMA:
            assert kwargs["allow_fallback"] is False
            try:
                value = next(pending)
            except StopIteration:
                pytest.fail("Unexpected additional product review call")
        else:
            value = main if main is not None else recommendation(ctx)
        return {
            "content": json.dumps(value),
            "finish_reason": "stop",
            "model": "fixture-model",
            "elapsed_ms": 3,
        }

    monkeypatch.setattr(client, "complete", complete)
    return generate_answer(ctx, client), calls


def test_illegal_review_question_repairs_once_to_a_sourced_product_question(monkeypatch):
    ctx = context()
    invalid = review(ctx)
    invalid["missing_information"] = ["Vui lòng cung cấp Chú giải Chương 11."]
    result, calls = run(monkeypatch, ctx, [invalid, review(ctx)])

    assert len(calls) == 3
    assert len(calls[-1]["messages"]) == 4
    assert "Chú giải" in calls[-1]["messages"][-1]["content"]
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["answer"]["missing_information"] == [
        "Khối lượng thực tế của hàng hóa là bao nhiêu?"
    ]
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["answer"]["citations"] == [{"label": "S1", "quote": "mass at most 10 kg"}]
    assert "[S1]" in result["answer"]["answer"]
    assert result["diagnostics"]["candidate_hs_code"] == "11111111"
    attempts = result["generation"]["product_review"]["attempts"]
    assert [attempt["valid"] for attempt in attempts] == [False, True]


def test_review_with_only_missing_facts_repairs_requires_review_status(monkeypatch):
    ctx = context()
    invalid = review(ctx, status="REQUIRES_REVIEW")
    result, calls = run(monkeypatch, ctx, [invalid, review(ctx)])

    assert len(calls) == 3
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["generation"]["product_review"]["valid"]
    assert "MISSING_PRODUCT_INFO" in calls[-1]["messages"][-1]["content"]


def test_contradicted_condition_keeps_review_status_and_actual_source_citation(monkeypatch):
    ctx = context("Complete equipment made of aluminum for daily use; mass 20 kg.")
    contradicted = review(ctx, status="REQUIRES_REVIEW", assessment="CONTRADICTED")
    contradicted["reason"] = "Khối lượng 20 kg vượt giới hạn 10 kg trong điều kiện của nguồn."
    contradicted["product_facts"] = [{"fact": "Khối lượng 20 kg", "user_quote": "mass 20 kg"}]
    result, calls = run(monkeypatch, ctx, [contradicted])

    assert len(calls) == 2
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["answer"]["citations"] == [{"label": "S1", "quote": "mass at most 10 kg"}]
    assert result["diagnostics"]["code"] == "PRODUCT_REVIEW_BLOCKED"
    assert result["diagnostics"]["reasons"] == [contradicted["reason"]]


def test_repeated_source_label_cites_blocking_condition_instead_of_first_satisfied_one(monkeypatch):
    ctx = context()
    value = review(ctx)
    value["condition_checks"].insert(
        0,
        {
            "source_label": "S1",
            "source_quote": "Made of aluminum",
            "assessment": "SATISFIED",
            "product_fact_indices": [0],
        },
    )
    result, calls = run(monkeypatch, ctx, [value])

    assert len(calls) == 2
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["answer"]["citations"] == [{"label": "S1", "quote": "mass at most 10 kg"}]


def test_malformed_review_diagnostics_do_not_expose_unknown_fields_or_fabricated_quotes(
    monkeypatch,
):
    ctx = context()
    invalid = review(ctx)
    invalid["untrusted_extra_field"] = "RAW_UNTRUSTED_VALUE"
    invalid["condition_checks"][0]["source_quote"] = "FABRICATED_SOURCE_QUOTE"
    result, calls = run(monkeypatch, ctx, [invalid, invalid])

    assert len(calls) == 3
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["suggested_hs_code"] == ""
    diagnostics = result["diagnostics"]
    assert diagnostics["code"] == "PRODUCT_REVIEW_FAILED"
    assert diagnostics["candidate_hs_code"] == "11111111"
    assert set(diagnostics["source_labels"]) <= {source["label"] for source in ctx["sources"]}
    rendered = json.dumps({"answer": result["answer"], "diagnostics": diagnostics})
    for untrusted in ("untrusted_extra_field", "RAW_UNTRUSTED_VALUE", "FABRICATED_SOURCE_QUOTE"):
        assert untrusted not in rendered
    assert diagnostics["reasons"]


def test_repeated_invalid_main_citations_fail_safely_with_verified_candidate_diagnostics(
    monkeypatch,
):
    ctx = context()
    invalid = recommendation(ctx)
    invalid["citations"][0]["quote"] = "FABRICATED_SOURCE_QUOTE"
    result, calls = run(monkeypatch, ctx, [], main=invalid)

    assert len(calls) == 2
    assert all(call["schema"] is not PRODUCT_REVIEW_SCHEMA for call in calls)
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["answer"]["citations"] == []
    assert result["generation"]["guardrail_abstention"]
    assert all(not attempt["validation"]["valid"] for attempt in result["generation"]["attempts"])
    diagnostics = result["diagnostics"]
    assert diagnostics["code"] == "ANSWER_VALIDATION_FAILED"
    assert diagnostics["candidate_hs_code"] == "11111111"
    assert diagnostics["candidate_hs_code"] in ctx["allowed_hs_codes"]
    assert diagnostics["source_labels"] == ctx["candidate_evidence"][0]["required_citation_labels"]
    assert all(
        label in {source["label"] for source in ctx["sources"]}
        for label in diagnostics["source_labels"]
    )
    assert "FABRICATED_SOURCE_QUOTE" not in json.dumps(diagnostics)


def test_review_full_request_overflow_is_blocked_before_transport_with_specific_diagnostics(
    monkeypatch,
):
    ctx = context()
    # This audit field is retained server-side, outside the compact initial model message.
    ctx["sources"][0]["locator"]["audit"] = "x" * 1_100_000
    client = RAGClient(CLIProxyConfig(api_key="fixture"), GroqConfig(keys=("fixture",)))
    calls = []

    def send(_self, path, payload):
        calls.append(payload)
        return {
            "choices": [
                {"message": {"content": json.dumps(recommendation(ctx))}, "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
        }

    monkeypatch.setattr(CLIProxyClient, "_request", send)
    result = generate_answer(ctx, client)
    assert len(calls) == 1
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    review_result = result["generation"]["product_review"]
    assert review_result["error_code"] == "context_length_exceeded"
    assert not review_result["request_budget"]["fits"]
    assert "vượt ngân sách context" in result["diagnostics"]["reasons"][0]
    assert result["generation"]["usage"]["completion_tokens"] == 2
