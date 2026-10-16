"""Complete-request token bounds cover schemas, Unicode and shared context output."""

import copy
import json

import pytest

from config.model_limits import MODEL_LIMITS, ModelLimits, get_model_limits
from rag.llm.budget import (
    ContextBudgetError,
    build_request_messages,
    check_request_budget,
    request_budget,
)
from rag.llm.errors import LLMError
from rag.prompts.provider_format import format_json_schema_prompt

MESSAGES = [
    {"role": "system", "content": "A complete instruction"},
    {"role": "user", "content": "x"},
]
SCHEMA = {"type": "object", "description": "unique_schema_marker", "properties": {}}


def register_limit(monkeypatch, model, *, spare=0, output=16, shared=False):
    measured = request_budget(MESSAGES, SCHEMA, model)["input_tokens"]
    monkeypatch.setitem(MODEL_LIMITS, model, ModelLimits(measured + spare, output, shared))
    return measured


def test_separate_input_and_output_limits_allow_the_exact_input_boundary(monkeypatch):
    measured = register_limit(monkeypatch, "exact-separate")
    result = check_request_budget(MESSAGES, SCHEMA, "exact-separate")
    assert result["input_tokens"] == result["input_limit"] == measured
    assert result["mode"] == "CONSERVATIVE_UTF8_BOUND"
    assert result["output_tokens"] == result["max_output_tokens"] == 16
    assert result["remaining_input_tokens"] == 0
    assert result["context_limit"] is None
    assert result["remaining_after_output_tokens"] is None


def test_one_byte_beyond_input_limit_raises_a_safe_provider_error(monkeypatch):
    register_limit(monkeypatch, "beyond-separate")
    messages = copy.deepcopy(MESSAGES)
    messages[-1]["content"] += "x"
    budget = request_budget(messages, SCHEMA, "beyond-separate")
    assert not budget["fits"]
    assert budget["remaining_input_tokens"] == -1
    with pytest.raises(ContextBudgetError) as exc_info:
        check_request_budget(messages, SCHEMA, "beyond-separate")
    error = exc_info.value
    assert isinstance(error, LLMError)
    assert error.status == 413
    assert error.error_code == "context_length_exceeded"
    assert error.provider == "cliproxyapi"
    assert error.budget == budget
    assert "A complete instruction" not in str(error)
    assert "unique_schema_marker" not in json.dumps(error.budget)


def test_shared_context_clamps_output_to_remaining_capacity_and_requires_one_token(monkeypatch):
    measured = register_limit(monkeypatch, "shared", spare=5, output=16, shared=True)
    full = check_request_budget(MESSAGES, SCHEMA, "shared")
    assert full["input_tokens"] == measured
    assert full["context_limit"] == measured + 5
    assert full["output_tokens"] == 5
    assert full["remaining_after_output_tokens"] == 0
    assert check_request_budget(MESSAGES, SCHEMA, "shared", 3)["output_tokens"] == 3
    messages = copy.deepcopy(MESSAGES)
    messages[-1]["content"] += "xxxx"
    assert check_request_budget(messages, SCHEMA, "shared")["output_tokens"] == 1
    messages[-1]["content"] += "x"
    exhausted = request_budget(messages, SCHEMA, "shared")
    assert exhausted["input_tokens"] == exhausted["context_limit"]
    assert exhausted["output_tokens"] == 0
    with pytest.raises(ContextBudgetError):
        check_request_budget(messages, SCHEMA, "shared")


def test_utf8_estimate_counts_bytes_rather_than_unicode_characters():
    ascii_messages = [{"role": "user", "content": "a" * 100}]
    unicode_messages = [{"role": "user", "content": "đ" * 100}]
    ascii_budget = request_budget(ascii_messages, SCHEMA, "gemini-3.8-flash-high")
    unicode_budget = request_budget(unicode_messages, SCHEMA, "gemini-3.8-flash-high")
    assert len(ascii_messages[0]["content"]) == len(unicode_messages[0]["content"])
    assert unicode_budget["input_tokens"] - ascii_budget["input_tokens"] == 100
    assert unicode_budget["input_tokens"] == (
        unicode_budget["serialized_request_bytes"] + unicode_budget["framing_reserve_tokens"]
    )


def test_cli_gpt_wrapper_is_idempotent_and_schema_is_not_counted_twice():
    original = copy.deepcopy(MESSAGES)
    rendered = build_request_messages(MESSAGES, SCHEMA, "gpt-oss-120b-medium")
    assert rendered[0] == {"role": "system", "content": format_json_schema_prompt(SCHEMA)}
    assert build_request_messages(rendered, SCHEMA, "gpt-oss-120b-medium") == rendered
    assert request_budget(MESSAGES, SCHEMA, "gpt-oss-120b-medium") == request_budget(
        rendered, SCHEMA, "gpt-oss-120b-medium"
    )
    assert json.dumps(rendered).count("unique_schema_marker") == 1
    assert MESSAGES == original
    assert (
        request_budget(MESSAGES, SCHEMA, "gpt-oss-120b-medium")["schema_representation"]
        == "SYSTEM_MESSAGE"
    )


def test_groq_gpt_uses_native_schema_and_includes_schema_in_the_bound():
    rendered = build_request_messages(MESSAGES, SCHEMA, "openai/gpt-oss-20b", provider="groq")
    assert rendered == MESSAGES
    measured = request_budget(MESSAGES, SCHEMA, "openai/gpt-oss-20b", provider="groq")
    smaller_schema = request_budget(MESSAGES, {}, "openai/gpt-oss-20b", provider="groq")
    assert measured["schema_representation"] == "NATIVE_JSON_SCHEMA"
    assert measured["input_tokens"] > smaller_schema["input_tokens"]
    assert measured["input_tokens"] > sum(len(m["content"].encode()) for m in MESSAGES)


@pytest.mark.parametrize("additional_content", ["system", "native_schema", "repair_history"])
def test_full_request_guard_counts_system_schema_and_repair_history(
    monkeypatch, additional_content
):
    register_limit(monkeypatch, "complete-request")
    messages, schema = copy.deepcopy(MESSAGES), copy.deepcopy(SCHEMA)
    if additional_content == "system":
        messages[0]["content"] += "x"
    elif additional_content == "native_schema":
        schema["description"] += "x"
    else:
        messages.extend(
            [
                {"role": "assistant", "content": "The previous response"},
                {"role": "user", "content": "Repair its validation errors"},
            ]
        )
    with pytest.raises(ContextBudgetError):
        check_request_budget(messages, schema, "complete-request")


@pytest.mark.parametrize("model", list(MODEL_LIMITS))
def test_known_models_default_to_their_full_output_cap_and_cap_requested_output(model):
    limits = get_model_limits(model)
    assert limits is not None
    assert request_budget(MESSAGES, SCHEMA, model)["output_tokens"] == limits.output_tokens
    assert (
        request_budget(MESSAGES, SCHEMA, model, limits.output_tokens + 1)["output_tokens"]
        == limits.output_tokens
    )
    assert request_budget(MESSAGES, SCHEMA, model, 1)["output_tokens"] == 1


def test_unknown_alias_keeps_custom_client_policy_without_inventing_capacity():
    assert get_model_limits("custom-client-model") is None
    result = check_request_budget(MESSAGES, SCHEMA, "custom-client-model", 123)
    assert result["mode"] == "UNKNOWN_MODEL_LIMITS"
    assert not result["checked"]
    assert result["input_limit"] is result["context_limit"] is result["max_output_tokens"] is None
    assert result["output_tokens"] == 123
    assert result["fits"]
    assert request_budget(MESSAGES, SCHEMA, "custom-client-model")["output_tokens"] is None


@pytest.mark.parametrize("requested", [0, -1, True, 1.5])
def test_invalid_requested_output_is_rejected(requested):
    with pytest.raises(ValueError, match="positive integer"):
        request_budget(MESSAGES, SCHEMA, "gemini-3.8-flash-high", requested)
