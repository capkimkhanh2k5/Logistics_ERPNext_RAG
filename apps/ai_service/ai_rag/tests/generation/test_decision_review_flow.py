"""Abstention decisions must assess product identity without weakening HS safeguards."""

import json
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.llm.contracts.errors import LLMError
from rag.llm.generation.answering import generate_answer
from tests.support.legacy_generation import prepare_legacy_context as prepare_context


def legal_answer():
    return {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Hệ thống hiện chưa có cơ sở pháp lý để phân loại sản phẩm.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": ["Chưa truy xuất được nguồn mô tả nhóm hàng phù hợp."],
    }


def decision(*, kind="HS", product_type="", question=""):
    return {
        "request_kind": kind,
        "identity_status": "NOT_APPLICABLE"
        if kind == "QA"
        else "IDENTIFIED"
        if product_type
        else "UNCONFIRMED",
        "product_type": product_type,
        "product_type_quote": product_type,
        "decision": "CLARIFY" if question else "KEEP",
        "reason": "Chưa xác nhận loại hàng thực tế."
        if question
        else "Ngữ cảnh chưa có đủ nguồn phù hợp; không tự đoán thuộc tính cần hỏi.",
        "clarifications": [
            {
                "question": question,
                "basis": "PRODUCT_IDENTITY",
                "source_label": "",
                "source_quote": "",
            }
        ]
        if question
        else [],
        "retained_qa": {"answer": "", "citations": []},
    }


def context(question, *, task="auto", empty=False):
    result = {} if empty else {"matches": [{"id": "source", "source_text": "Quy định chung."}]}
    return prepare_context(question, result, task, GroqConfig(keys=("fixture",)))


def client_with(main, reviewed):
    calls = []

    def complete(messages, schema, **kwargs):
        is_decision = "request_kind" in schema["properties"]
        calls.append({"is_decision": is_decision, **kwargs})
        if is_decision and isinstance(reviewed, Exception):
            raise reviewed
        content = reviewed if is_decision else main
        return {
            "content": json.dumps(content, ensure_ascii=False),
            "finish_reason": "stop",
            "model": "actual-model",
            "provider": "fixture",
            "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
            "elapsed_ms": 1,
        }

    return SimpleNamespace(complete=complete, config=GroqConfig(keys=("fixture",))), calls


@pytest.mark.parametrize("name", ["MacBook Pro M5 Pro", "iPhone 18 Pro Max", "Thiết bị mẫu X"])
def test_trade_name_legal_abstention_is_reviewed_and_becomes_identity_question(name):
    ctx = context(f"{name} có mã HS bao nhiêu?")
    reviewed = decision(question="Bạn xác nhận loại hàng thực tế và dạng hàng nhập khẩu?")
    client, calls = client_with(legal_answer(), reviewed)
    result = generate_answer(ctx, client)
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["answer"]["missing_information"] == [reviewed["clarifications"][0]["question"]]
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["answer"]["missing_legal_evidence"] == []
    assert result["validation"]["decision_grounding"] == "MODEL_REVIEWED"
    assert result["generation"]["usage"]["total_tokens"] == 14
    assert [call["is_decision"] for call in calls] == [False, True]
    assert calls[-1]["model"] == "actual-model"
    assert not calls[-1]["allow_fallback"]


def test_empty_hs_context_still_checks_identity_and_skips_only_main_generation():
    reviewed = decision(question="Sản phẩm thực tế là loại hàng gì?")
    client, calls = client_with(legal_answer(), reviewed)
    result = generate_answer(context("Tên thương mại X", task="hs", empty=True), client)
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert len(calls) == 1 and calls[0]["is_decision"]
    assert calls[0]["allow_fallback"]
    assert result["generation"]["main_skipped"]
    assert not result["generation"]["skipped"]
    assert result["generation"]["model"] == "actual-model"
    assert result["generation"]["usage"]["total_tokens"] == 7


def test_identified_product_without_sources_keeps_legal_gap_without_inventing_specs():
    reviewed = decision(product_type="máy tính xách tay nguyên chiếc")
    client, calls = client_with(legal_answer(), reviewed)
    result = generate_answer(context("Đây là máy tính xách tay nguyên chiếc."), client)
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert result["answer"]["missing_information"] == []
    assert "ngữ cảnh" in result["answer"]["answer"]
    assert len(calls) == 2


def test_auto_legal_qa_remains_qa_without_product_questions():
    client, calls = client_with(legal_answer(), decision(kind="QA"))
    result = generate_answer(context("Văn bản nào quy định thời hạn khai báo?"), client)
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert result["answer"]["missing_information"] == []
    assert len(calls) == 2


def test_explicit_empty_qa_preserves_zero_model_calls():
    client = SimpleNamespace(complete=lambda *a, **k: pytest.fail("Unexpected model call"))
    result = generate_answer(context("Văn bản nào?", task="qa", empty=True), client)
    assert result["generation"]["skipped"]
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"


def test_decision_provider_failure_is_a_visible_safe_hold_not_a_product_question():
    client, calls = client_with(legal_answer(), LLMError(503, "actual-model", provider="fixture"))
    result = generate_answer(context("Tên thương mại X cần mã HS."), client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["missing_information"] == []
    assert not result["generation"]["decision_review"]["valid"]
    assert result["diagnostics"]["code"] == "DECISION_REVIEW_FAILED"
    assert len(calls) == 2


def test_invalid_main_answer_technical_hold_does_not_run_decision_review():
    client, calls = client_with({}, decision(question="Loại hàng thực tế là gì?"))
    result = generate_answer(context("Tên thương mại X cần mã HS."), client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["generation"]["guardrail_abstention"]
    assert "decision_review" not in result["generation"]
    assert len(calls) == 2 and not any(call["is_decision"] for call in calls)


@pytest.mark.parametrize("field", ["reason", "retained_qa"])
def test_decision_review_cannot_publish_a_classification_in_free_text(field):
    reviewed = decision(question="Sản phẩm thực tế là loại hàng gì?")
    unsafe = "Sản phẩm này phải phân loại vào mã HS 84713020."
    if field == "reason":
        reviewed["reason"] = unsafe
    else:
        reviewed["request_kind"] = "MIXED"
        reviewed["retained_qa"] = {
            "answer": unsafe + " [S1]",
            "citations": [{"label": "S1", "quote": "Quy định chung."}],
        }
    client, calls = client_with(legal_answer(), reviewed)
    result = generate_answer(context("Tên thương mại X cần mã HS."), client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert "84713020" not in result["answer"]["answer"]
    assert not result["generation"]["decision_review"]["valid"]
    assert len(calls) == 3


def test_unresolved_request_cannot_be_marked_as_a_reviewed_legal_abstention():
    reviewed = decision(kind="QA")
    reviewed["request_kind"] = "UNCLEAR"
    client, _ = client_with(legal_answer(), reviewed)
    result = generate_answer(context("Tôi muốn hỏi về thiết bị X."), client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert not result["generation"]["decision_review"]["valid"]


def test_mixed_request_can_clarify_question_scope_without_sources_or_reasking_type():
    reviewed = decision(product_type="máy tính xách tay", question="Hồ sơ này là hồ sơ nào?")
    reviewed["request_kind"] = "MIXED"
    reviewed["clarifications"][0]["basis"] = "QUESTION_SCOPE"
    client, _ = client_with(legal_answer(), reviewed)
    ctx = context(
        "Đây là máy tính xách tay. Phân loại và cho biết hồ sơ này cần giấy gì?", empty=True
    )
    result = generate_answer(ctx, client)
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["answer"]["missing_information"] == ["Hồ sơ này là hồ sơ nào?"]
    assert result["generation"]["decision_review"]["valid"]
