"""Conversation decisions must preserve literal inputs and fail closed on uncertain routing."""

import json
from types import SimpleNamespace

import pytest

from config.settings import RAGGenerationConfig
from rag.llm.context.conversation import MAX_ROUTING_CHARS, explicit_turn
from rag.llm.contracts.errors import LLMError
from rag.prompts.planning.query_planning import QUERY_PLAN_SCHEMA, TURN_PLAN_SCHEMA
from rag.retrieval.query_planning import QueryPlanner
from tests.test_query_planning import hint


def planner(payload, *, finish_reason="stop", raw=False):
    calls = []

    def complete(messages, schema):
        calls.append((messages, schema))
        if isinstance(payload, Exception):
            raise payload
        return {
            "content": payload if raw else json.dumps(payload),
            "finish_reason": finish_reason,
            "model": "fixture",
            "provider": "injected",
            "usage": {"total_tokens": 42},
        }

    return QueryPlanner(
        SimpleNamespace(
            complete=complete, config=RAGGenerationConfig("fixture", "fallback", None, None)
        )
    ), calls


def decision(action="FOLLOW_UP", message_anchor="1,6 kg", context_anchor="Khối lượng?"):
    return {
        "action": action,
        "message_anchor": message_anchor,
        "context_anchor": context_anchor,
        "terms": [],
    }


def test_semantic_route_uses_only_active_user_turns_and_validated_questions():
    p, calls = planner(decision())
    facts, questions = ["Máy nguyên chiếc."], ["Khối lượng?"]
    result, plan = p.plan_turn("MacBook có mã HS bao nhiêu?", facts, "Máy nặng 1,6 kg.", questions)
    assert result["action"] == "FOLLOW_UP" and result["method"] == "SEMANTIC"
    assert result["generation"]["usage"] == {"total_tokens": 42}
    assert result["elapsed_ms"] >= 0
    assert calls[0][1] is TURN_PLAN_SCHEMA
    assert plan["status"] == "NO_EXPANSION"
    assert plan["generation"] == result["generation"]
    assert result["shared_with_query_plan"] is True
    assert len(calls) == 1
    assert json.loads(calls[0][0][1]["content"]) == {
        "active_question": "MacBook có mã HS bao nhiêu?",
        "supplements": facts,
        "pending_questions": questions,
        "message": "Máy nặng 1,6 kg.",
    }
    assert facts == ["Máy nguyên chiếc."] and questions == ["Khối lượng?"]


@pytest.mark.parametrize(
    ("question", "message", "override", "expected", "method"),
    [
        ("", "Sản phẩm ZXQ có mã HS nào?", None, "NEW_QUESTION", "FIRST_TURN"),
        ("Q", "Câu hỏi mới: Thuế là gì?", None, "NEW_QUESTION", "PREFIX"),
        ("Q", "New question: What is HS?", None, "NEW_QUESTION", "PREFIX"),
        ("Q", "Bổ sung: nặng 1 kg", None, "FOLLOW_UP", "PREFIX"),
        ("Q", "Bổ sung thông tin: 1 kg", None, "FOLLOW_UP", "PREFIX"),
        ("Q", "ĐÍNH CHÍNH: 2 kg", None, "FOLLOW_UP", "PREFIX"),
        ("Q", "Correction: 2 kg", None, "FOLLOW_UP", "PREFIX"),
        ("Q", "mơ hồ", "NEW_QUESTION", "NEW_QUESTION", "COMMAND"),
        ("Q", "Câu hỏi mới: nhưng ép bổ sung", "FOLLOW_UP", "FOLLOW_UP", "COMMAND"),
    ],
)
def test_clear_routing_paths_do_not_call_model(question, message, override, expected, method):
    result = explicit_turn(question, message, override)
    assert result["action"] == expected and result["method"] == method


@pytest.mark.parametrize("override", ["FOLLOW_UP", "INVALID", "CLARIFY"])
def test_invalid_override_or_follow_up_without_question_is_rejected(override):
    p, calls = planner(None)
    with pytest.raises(ValueError):
        p.plan_turn("", [], "message", [], forced_action=override)
    assert calls == []


def test_new_subject_is_possible_while_waiting_for_product_info():
    p, _ = planner(decision("NEW_QUESTION", "Điện thoại iPhone", ""))
    result, plan = p.plan_turn(
        "MacBook?", ["Máy nguyên chiếc"], "Điện thoại iPhone có mã HS nào?", ["Cân nặng?"]
    )
    assert result["action"] == "NEW_QUESTION"
    assert plan["queries"] == ["Điện thoại iPhone có mã HS nào?"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [],
        None,
        decision("INVALID"),
        decision(context_anchor="Không có trong hội thoại"),
        decision(context_anchor=""),
        decision(message_anchor="Thuộc tính do model tự thêm"),
        decision(message_anchor=""),
        decision(message_anchor="x" * 241),
        decision("NEW_QUESTION", "1,6 kg", "Khối lượng?"),
        {**decision(), "rewritten_question": "Máy đáp ứng tiêu chí pháp lý"},
    ],
)
def test_invalid_decisions_do_not_fall_back_to_appending_old_question(payload):
    p, _ = planner(payload)
    result, plan = p.plan_turn("Q", [], "Máy nặng 1,6 kg.", ["Khối lượng?"])
    assert result["action"] == "CLARIFY"
    assert result["error_code"] == "invalid_turn_decision"
    assert plan is None


@pytest.mark.parametrize(
    ("payload", "finish_reason", "raw", "code"),
    [
        ("not JSON", "stop", True, "invalid_turn_decision"),
        (decision(), "length", False, "invalid_turn_decision"),
        (LLMError(429, "fixture", provider="injected"), "stop", False, "routing_provider_error"),
    ],
)
def test_truncation_json_errors_and_provider_errors_require_explicit_routing(
    payload, finish_reason, raw, code
):
    p, calls = planner(payload, finish_reason=finish_reason, raw=raw)
    for _ in range(2):
        result, plan = p.plan_turn("Q", [], "Máy nặng 1,6 kg.", ["Khối lượng?"])
        assert result["action"] == "CLARIFY" and result["error_code"] == code
        assert plan is None
    assert len(calls) == 2  # Transient failures are not retained in a shared cache.


def test_oversized_routing_context_is_not_truncated_and_commands_preserve_full_input():
    p, calls = planner({"terms": []})
    message = "x" * MAX_ROUTING_CHARS
    result, plan = p.plan_turn("Q", [], message, [])
    assert result["action"] == "CLARIFY" and result["error_code"] == "routing_context_too_long"
    assert plan is None
    assert calls == []
    for action in ("FOLLOW_UP", "NEW_QUESTION"):
        routing, plan = p.plan_turn("Q", [], message, [], forced_action=action)
        assert routing["action"] == action
        assert message in plan["queries"][0]
    assert len(calls) == 2
    assert all(schema is QUERY_PLAN_SCHEMA for _, schema in calls)


def test_model_can_request_clarification_without_inventing_an_anchor():
    p, calls = planner(decision("CLARIFY", "", ""))
    result, plan = p.plan_turn("Q", [], "Còn cái kia?", [])
    assert result["action"] == "CLARIFY" and "error_code" not in result
    assert plan is None and len(calls) == 1


def test_new_question_discards_old_context_before_validating_search_hints():
    payload = {
        **decision("NEW_QUESTION", "iPhone", ""),
        "terms": [hint(anchor="iPhone", term="điện thoại thông minh")],
    }
    p, calls = planner(payload)
    message = "iPhone có mã HS nào?"
    routing, plan = p.plan_turn("MacBook?", ["Nhẹ hơn 10 kg"], message, ["Khối lượng?"])
    assert routing["action"] == "NEW_QUESTION" and len(calls) == 1
    assert plan["queries"][0] == message
    assert "MacBook" not in plan["ranking_query"] and "10 kg" not in plan["ranking_query"]
    assert plan["status"] == "EXPANDED"
    p.validate_plan(message, plan)


@pytest.mark.parametrize(
    "terms",
    [
        None,
        "invalid",
        [hint(anchor="MacBook")],
        [hint(anchor="iPhone", term="85171300")],
        [hint(anchor="iPhone", kind="fact")],
        [hint(anchor="iPhone")] * 4,
    ],
)
def test_valid_new_question_with_bad_hints_uses_scoped_raw_query_without_second_call(terms):
    p, calls = planner({**decision("NEW_QUESTION", "iPhone", ""), "terms": terms})
    routing, plan = p.plan_turn("MacBook?", ["Nhẹ hơn 10 kg"], "iPhone?", [])
    assert routing["action"] == "NEW_QUESTION" and len(calls) == 1
    assert plan["status"] == "FALLBACK_RAW" and plan["queries"] == ["iPhone?"]
    p.validate_plan("iPhone?", plan)


def test_missing_hints_does_not_discard_a_valid_routing_decision():
    payload = decision("NEW_QUESTION", "iPhone", "")
    del payload["terms"]
    p, calls = planner(payload)
    routing, plan = p.plan_turn("MacBook?", [], "iPhone?", [])
    assert routing["action"] == "NEW_QUESTION"
    assert plan["status"] == "FALLBACK_RAW" and len(calls) == 1


@pytest.mark.parametrize("anchor", ["Khối lượng?", "Thông tin người dùng bổ sung ở lượt 2"])
def test_pending_questions_and_system_labels_cannot_anchor_hints(anchor):
    p, calls = planner({**decision(), "terms": [hint(anchor=anchor)]})
    routing, plan = p.plan_turn("MacBook?", [], "Máy nặng 1,6 kg.", ["Khối lượng?"])
    assert routing["action"] == "FOLLOW_UP" and len(calls) == 1
    assert plan["status"] == "FALLBACK_RAW"
    assert plan["queries"][0].endswith("Máy nặng 1,6 kg.")


def test_combined_plan_is_reused_by_retry_but_routing_never_uses_query_only_cache(monkeypatch):
    from dataclasses import replace

    import rag.retrieval.query_planning as module

    p, calls = planner({**decision(), "terms": [hint(anchor="MacBook")]})
    _, plan = p.plan_turn("MacBook?", [], "Máy nặng 1,6 kg.", ["Khối lượng?"])
    query = plan["queries"][0]
    assert p.plan(query)["cache_hit"] is True
    assert len(calls) == 1
    # Even the same latest message needs the full active state and pending questions.
    p.plan_turn("MacBook?", ["Màn hình tích hợp"], "Máy nặng 1,6 kg.", ["Cấu hình?"])
    assert len(calls) == 2
    assert json.loads(calls[-1][0][1]["content"])["pending_questions"] == ["Cấu hình?"]
    p.client.config = replace(p.client.config, model="changed")
    assert p.plan(query)["cache_hit"] is False
    monkeypatch.setattr(module, "TURN_PLANNING_PROMPT", "Updated combined prompt")
    assert p.plan(query)["fingerprint"] != plan["fingerprint"]
    assert len(calls) == 4


def test_follow_up_correction_is_preserved_verbatim_and_hints_remain_hypotheses():
    message = "Thực ra tôi hỏi bàn phím rời của MacBook, không phải máy nguyên chiếc."
    p, calls = planner(
        {
            **decision("FOLLOW_UP", "bàn phím rời", "MacBook"),
            "terms": [hint(anchor="bàn phím rời", term="thiết bị nhập dữ liệu")],
        }
    )
    _, plan = p.plan_turn("MacBook?", ["Máy nguyên chiếc"], message, [])
    assert plan["queries"][0].endswith(message)
    assert "thiết bị nhập dữ liệu" not in plan["queries"][0]
    assert plan["used_as_product_facts"] is False and len(calls) == 1


def test_explicit_turn_can_fall_back_to_raw_on_provider_error_without_losing_context():
    p, calls = planner(LLMError(503, "fixture", provider="injected"))
    routing, plan = p.plan_turn("MacBook?", [], "Nhẹ hơn 10 kg", [], forced_action="FOLLOW_UP")
    assert routing["action"] == "FOLLOW_UP"
    assert plan["status"] == "FALLBACK_RAW" and len(calls) == 1
    assert "MacBook?" in plan["queries"][0] and "Nhẹ hơn 10 kg" in plan["queries"][0]


def test_unresolved_turn_does_not_poison_existing_plan_cache():
    p, calls = planner({"terms": []})
    p.plan("MacBook?")
    routing, plan = p.plan_turn("MacBook?", [], "Còn cái đó?", [])
    assert routing["action"] == "CLARIFY" and plan is None
    assert p.plan("MacBook?")["cache_hit"] is True and len(calls) == 2
