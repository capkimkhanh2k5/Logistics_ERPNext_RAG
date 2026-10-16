"""Independent reviews clarify product identity without inventing legal evidence."""

import copy
import json
from types import SimpleNamespace

import pytest

from rag.llm.budget import ContextBudgetError
from rag.llm.decision_review import review_decision
from rag.llm.errors import LLMError
from rag.llm.validation import validate_answer
from rag.prompts.schemas import DECISION_REVIEW_SCHEMA


def context(question="Mặt hàng mang tên Alpha Pro.", *, sources=None):
    return {
        "question": question,
        "task": "auto",
        "sources": [] if sources is None else sources,
        "allowed_hs_codes": [],
        "candidate_evidence": [],
    }


def legal_gap():
    return {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Chưa có nguồn liên quan trong ngữ cảnh truy xuất để kết luận.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": ["Thiếu mô tả pháp lý phù hợp trong ngữ cảnh truy xuất."],
    }


def decision(**updates):
    return {
        "request_kind": "HS",
        "identity_status": "UNCONFIRMED",
        "product_type": "",
        "product_type_quote": "",
        "decision": "CLARIFY",
        "reason": "Câu hỏi mới nêu tên thương mại nên chưa xác nhận loại hàng thực tế.",
        "clarifications": [
            {
                "question": "Sản phẩm thuộc loại hàng hóa gì và có công dụng gì?",
                "basis": "PRODUCT_IDENTITY",
                "source_label": "",
                "source_quote": "",
            }
        ],
        "retained_qa": {"answer": "", "citations": []},
        **updates,
    }


class ScriptedClient:
    def __init__(self, responses, *, clock=None):
        self.responses = iter(responses)
        self.calls = []
        self.config = SimpleNamespace(model="configured-model")
        self.clock = clock

    def complete(self, messages, schema, **kwargs):
        assert schema is DECISION_REVIEW_SCHEMA
        self.calls.append({"messages": copy.deepcopy(messages), **kwargs})
        try:
            item = next(self.responses)
        except StopIteration:
            pytest.fail("Unexpected third review call")
        if isinstance(item, Exception):
            raise item
        if isinstance(item, dict) and "content" in item:
            result = item.copy()
        else:
            result = {"content": item if isinstance(item, str) else json.dumps(item)}
        result.setdefault("finish_reason", "stop")
        result.setdefault("model", kwargs.get("model") or self.config.model)
        result.setdefault("provider", "fixture")
        result.setdefault("elapsed_ms", 1)
        if self.clock is not None:
            self.clock.value += result["elapsed_ms"] / 1000
        return result


def test_trade_name_only_overrides_false_legal_gap_with_product_identity_question():
    ctx = context()
    original = legal_gap()
    client = ScriptedClient([decision()])
    answer, metadata = review_decision(ctx, original, client)
    assert metadata["valid"]
    assert answer["status"] == "MISSING_PRODUCT_INFO"
    assert answer["suggested_hs_code"] == ""
    assert answer["missing_information"] == ["Sản phẩm thuộc loại hàng hóa gì và có công dụng gì?"]
    assert not answer["missing_legal_evidence"]
    assert not answer["citations"]
    assert validate_answer(answer, ctx)["valid"]
    payload = json.loads(client.calls[0]["messages"][1]["content"])
    assert payload["question"] == ctx["question"]
    assert payload["current_answer"] == original
    assert original["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"


def test_user_identified_product_with_missing_sources_keeps_legal_gap():
    ctx = context("Đây là máy tính xách tay.")
    original = legal_gap()
    review = decision(
        identity_status="IDENTIFIED",
        product_type="máy tính xách tay",
        product_type_quote="Đây là máy tính xách tay.",
        decision="KEEP",
        reason="Loại hàng đã rõ nhưng ngữ cảnh truy xuất chưa có nguồn liên quan.",
        clarifications=[],
    )
    answer, metadata = review_decision(ctx, original, ScriptedClient([review]))
    assert metadata["valid"]
    assert answer is original
    assert answer["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"


def test_unconfirmed_hs_identity_cannot_keep_the_original_legal_gap():
    invalid = decision(decision="KEEP", clarifications=[])
    client = ScriptedClient([invalid, decision()])
    answer, metadata = review_decision(context(), legal_gap(), client)
    assert len(client.calls) == 2
    assert metadata["valid"]
    assert not metadata["attempts"][0]["valid"]
    assert answer["status"] == "MISSING_PRODUCT_INFO"


def test_confirmed_identity_is_not_asked_again():
    ctx = context("Đây là máy tính xách tay.")
    invalid = decision(
        identity_status="IDENTIFIED",
        product_type="máy tính xách tay",
        product_type_quote="máy tính xách tay",
    )
    answer, metadata = review_decision(ctx, legal_gap(), ScriptedClient([invalid, invalid]))
    assert not metadata["valid"]
    assert answer["status"] == "REQUIRES_REVIEW"
    assert not answer["missing_information"]


def test_pure_qa_is_kept_without_product_identification():
    sources = [{"label": "S1", "id": "rule", "text": "Hồ sơ gồm một tài liệu."}]
    ctx = context("Hồ sơ trong nguồn gồm những gì?", sources=sources)
    original = {
        **legal_gap(),
        "status": "ANSWERED",
        "answer": "Hồ sơ gồm một tài liệu [S1].",
        "citations": [{"label": "S1", "quote": "Hồ sơ gồm một tài liệu."}],
        "missing_legal_evidence": [],
    }
    review = decision(
        request_kind="QA",
        identity_status="NOT_APPLICABLE",
        decision="KEEP",
        reason="Câu hỏi về nội dung hồ sơ đã rõ.",
        clarifications=[],
    )
    answer, metadata = review_decision(ctx, original, ScriptedClient([review]))
    assert metadata["valid"]
    assert answer is original


@pytest.mark.parametrize(
    "quote,product_type",
    [("máy tính xách tay", "máy tính xách tay"), ("Alpha Pro", "thiết bị điện")],
)
def test_fabricated_product_identity_is_rejected(quote, product_type):
    invalid = decision(
        identity_status="IDENTIFIED",
        product_type=product_type,
        product_type_quote=quote,
        decision="KEEP",
        clarifications=[],
    )
    client = ScriptedClient([invalid, invalid])
    answer, metadata = review_decision(context(), legal_gap(), client)
    assert len(client.calls) == 2
    assert not metadata["valid"]
    assert answer["status"] == "REQUIRES_REVIEW"
    assert not answer["missing_information"]


def condition_decision(*, label="S1", quote="khối lượng không quá 10 kg"):
    return decision(
        identity_status="IDENTIFIED",
        product_type="máy tính xách tay",
        product_type_quote="máy tính xách tay",
        reason="Chưa có dữ kiện khối lượng để đối chiếu điều kiện nguồn.",
        clarifications=[
            {
                "question": "Khối lượng thực tế của máy là bao nhiêu?",
                "basis": "SOURCE_CONDITION",
                "source_label": label,
                "source_quote": quote,
            }
        ],
    )


def source_context():
    return context(
        "Đây là máy tính xách tay có bàn phím và màn hình.",
        sources=[
            {
                "label": "S1",
                "id": "condition",
                "text": "Máy xách tay có khối lượng không quá 10 kg.",
            }
        ],
    )


def test_specific_attribute_question_requires_and_preserves_actual_source_quote():
    ctx = source_context()
    answer, metadata = review_decision(ctx, legal_gap(), ScriptedClient([condition_decision()]))
    assert metadata["valid"]
    assert answer["status"] == "MISSING_PRODUCT_INFO"
    assert answer["citations"] == [{"label": "S1", "quote": "khối lượng không quá 10 kg"}]
    assert "[S1]" in answer["answer"]
    assert validate_answer(answer, ctx)["valid"]


@pytest.mark.parametrize(
    "label,quote", [("S2", "khối lượng không quá 10 kg"), ("S1", "khối lượng không quá 20 kg")]
)
def test_unknown_or_fabricated_legal_condition_is_rejected(label, quote):
    invalid = condition_decision(label=label, quote=quote)
    answer, metadata = review_decision(
        source_context(), legal_gap(), ScriptedClient([invalid, invalid])
    )
    assert not metadata["valid"]
    assert answer["status"] == "REQUIRES_REVIEW"
    assert answer["citations"] == []
    assert answer["missing_information"] == []


def test_review_cannot_ask_user_to_supply_legal_evidence():
    invalid = decision()
    invalid["clarifications"][0]["question"] = "Vui lòng cung cấp Chú giải Chương 84."
    answer, metadata = review_decision(context(), legal_gap(), ScriptedClient([invalid, invalid]))
    assert not metadata["valid"]
    assert answer["status"] == "REQUIRES_REVIEW"
    assert not answer["missing_information"]
    assert "Chú giải" not in answer["answer"]


def test_unclear_question_can_clarify_scope_without_asking_for_routing_selection():
    review = decision(
        request_kind="UNCLEAR",
        reason="Nội dung cần giải quyết chưa rõ.",
        clarifications=[
            {
                "question": "Bạn cần giải quyết vấn đề cụ thể nào?",
                "basis": "QUESTION_SCOPE",
                "source_label": "",
                "source_quote": "",
            }
        ],
    )
    answer, metadata = review_decision(
        context("Tôi cần hỗ trợ."), legal_gap(), ScriptedClient([review])
    )
    assert metadata["valid"]
    assert answer["status"] == "MISSING_PRODUCT_INFO"
    review["clarifications"][0]["question"] = "Bạn muốn chọn HS hay QA?"
    answer, metadata = review_decision(context(), legal_gap(), ScriptedClient([review, review]))
    assert not metadata["valid"]
    assert not answer["missing_information"]


@pytest.mark.parametrize(
    "error",
    [
        LLMError(429, "model", provider="fixture"),
        ContextBudgetError(
            "model", "fixture", {"fits": False, "input_tokens": 100, "input_limit": 10}
        ),
    ],
)
def test_provider_or_budget_error_is_not_retried_and_does_not_turn_into_legal_claim(error):
    client = ScriptedClient([error])
    answer, metadata = review_decision(context(), legal_gap(), client)
    assert len(client.calls) == 1
    assert not metadata["valid"]
    assert metadata["http_status"] == error.status
    assert metadata["failures"][0]["http_status"] == error.status
    if isinstance(error, ContextBudgetError):
        assert metadata["request_budget"] == error.budget
    assert answer["status"] == "REQUIRES_REVIEW"
    assert not answer["missing_information"] and not answer["missing_legal_evidence"]
    assert validate_answer(answer, context())["valid"]


def test_malformed_review_repairs_once_and_aggregates_usage_fallback_and_timings(monkeypatch):
    import rag.llm.decision_review as module

    clock = SimpleNamespace(value=0.0)
    monkeypatch.setattr(module, "perf_counter", lambda: clock.value)
    first = {
        "content": "{",
        "elapsed_ms": 4,
        "model": "actual-fallback",
        "requested_model": "primary",
        "fallback_used": True,
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
    }
    second = {
        "content": json.dumps(decision()),
        "elapsed_ms": 6,
        "model": "actual-fallback",
        "usage": {"prompt_tokens": 20, "completion_tokens": 3, "total_tokens": 23},
    }
    client = ScriptedClient([first, second], clock=clock)
    timings = {"llm_ms": 20.0, "validation_ms": 3.0}
    answer, metadata = review_decision(
        context(), legal_gap(), client, model="primary", allow_fallback=True, timings=timings
    )
    assert metadata["valid"] and answer["status"] == "MISSING_PRODUCT_INFO"
    assert len(metadata["attempts"]) == 2
    assert metadata["usage"] == {"prompt_tokens": 30, "completion_tokens": 5, "total_tokens": 35}
    assert metadata["elapsed_ms"] == 10
    assert metadata["requested_model"] == "primary" and metadata["fallback_used"]
    assert client.calls[0]["allow_fallback"] and not client.calls[1]["allow_fallback"]
    assert client.calls[1]["model"] == "actual-fallback"
    assert len(client.calls[1]["messages"]) == 4
    assert timings["decision_review_llm_ms"] == pytest.approx(10)
    assert timings["llm_ms"] == pytest.approx(30)
    assert timings["validation_ms"] == 3


def test_two_malformed_reviews_fail_safely_without_third_call_or_invalid_question():
    client = ScriptedClient(["{", "not-json"])
    answer, metadata = review_decision(context(), legal_gap(), client)
    assert len(client.calls) == 2 and not metadata["valid"]
    assert answer["status"] == "REQUIRES_REVIEW"
    assert not answer["missing_information"]
    assert "not-json" not in answer["answer"]


def test_failed_repair_keeps_first_usage_and_exposes_safe_budget_error():
    error = ContextBudgetError(
        "model", "fixture", {"fits": False, "input_tokens": 100, "input_limit": 10}
    )
    client = ScriptedClient(
        [
            {
                "content": "{",
                "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
            },
            error,
        ]
    )
    answer, metadata = review_decision(context(), legal_gap(), client)
    assert len(client.calls) == 2 and not metadata["valid"]
    assert metadata["usage"] == {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}
    assert metadata["request_budget"] == error.budget
    assert answer["status"] == "REQUIRES_REVIEW"


def test_mixed_clarification_preserves_only_explicit_grounded_qa_not_original_hs_claim():
    sources = [{"label": "S1", "id": "procedure", "text": "Hồ sơ gồm một tài liệu."}]
    ctx = context("Hồ sơ cần gì và mặt hàng Alpha Pro có mã nào?", sources=sources)
    original = {
        **legal_gap(),
        "answer": "Hồ sơ gồm một tài liệu [S1]. Có thể chọn mã 11111111.",
        "citations": [{"label": "S1", "quote": "Hồ sơ gồm một tài liệu."}],
    }
    review = decision(
        request_kind="MIXED",
        retained_qa={
            "answer": "Hồ sơ gồm một tài liệu [S1].",
            "citations": [{"label": "S1", "quote": "Hồ sơ gồm một tài liệu."}],
        },
    )
    answer, metadata = review_decision(ctx, original, ScriptedClient([review]))
    assert metadata["valid"]
    assert answer["status"] == "MISSING_PRODUCT_INFO"
    assert answer["answer"].startswith("Hồ sơ gồm một tài liệu [S1].")
    assert "11111111" not in answer["answer"]
    assert answer["suggested_hs_code"] == ""
    assert answer["citations"] == review["retained_qa"]["citations"]
    assert validate_answer(answer, ctx)["valid"]


def test_mixed_retained_qa_rejects_fabricated_source_quote():
    ctx = context(sources=[{"label": "S1", "id": "procedure", "text": "Hồ sơ gồm một tài liệu."}])
    invalid = decision(
        request_kind="MIXED",
        retained_qa={
            "answer": "Hồ sơ gồm hai tài liệu [S1].",
            "citations": [{"label": "S1", "quote": "Hồ sơ gồm hai tài liệu."}],
        },
    )
    answer, metadata = review_decision(ctx, legal_gap(), ScriptedClient([invalid, invalid]))
    assert not metadata["valid"]
    assert answer["status"] == "REQUIRES_REVIEW" and not answer["citations"]
