"""Conservative request accounting without a provider tokenizer or count-tokens API."""

import json
from copy import deepcopy

from config.model_limits import get_model_limits
from rag.llm.contracts.errors import LLMError
from rag.prompts.core.provider_format import format_json_schema_prompt
from rag.utils.files import digest

FRAMING_RESERVE_TOKENS = 256
PER_MESSAGE_RESERVE_TOKENS = 16


def schema_contract(schema: dict, mode: str) -> dict:
    """Record the effective wire rather than a public backend response schema."""
    return {"mode": mode, "schema_hash": digest(schema), "schema": deepcopy(schema)}


class ContextBudgetError(LLMError):
    """Expose only safe measurements when a complete request cannot fit."""

    def __init__(self, model: str, provider: str, budget: dict):
        self.budget = budget.copy()
        super().__init__(413, model, error_code="context_length_exceeded", provider=provider)


def build_request_messages(
    messages: list[dict], schema: dict, model: str, provider: str = "cliproxyapi"
) -> list[dict]:
    """Render the CLI GPT schema wrapper once; native-schema providers retain messages."""
    rendered = [message.copy() for message in messages]
    if provider != "cliproxyapi" or not model.startswith("gpt-oss-"):
        return rendered
    wrapper = {"role": "system", "content": format_json_schema_prompt(schema)}
    while rendered and rendered[0] == wrapper:
        rendered.pop(0)
    return [wrapper, *rendered]


def request_budget(
    messages: list[dict],
    schema: dict,
    model: str,
    requested_output_tokens: int | None = None,
    provider: str = "cliproxyapi",
) -> dict:
    """Bound decoded request content using UTF-8 bytes and explicit framing allowances.

    This deliberately overestimates byte-based tokenization rather than pretending to
    provide an exact tokenizer count. The envelope includes all messages and the native
    schema or CLI GPT wrapper; no provider request or count-tokens endpoint is called.
    """
    if requested_output_tokens is not None and (
        isinstance(requested_output_tokens, bool)
        or not isinstance(requested_output_tokens, int)
        or requested_output_tokens < 1
    ):
        raise ValueError("Requested output tokens must be a positive integer or None")
    rendered = build_request_messages(messages, schema, model, provider)
    envelope: dict = {"model": model, "messages": rendered}
    wrapped_schema = provider == "cliproxyapi" and model.startswith("gpt-oss-")
    if not wrapped_schema:
        envelope["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "grounded_rag_answer", "strict": True, "schema": schema},
        }
    serialized_bytes = len(json.dumps(envelope, ensure_ascii=False).encode("utf-8"))
    framing = FRAMING_RESERVE_TOKENS + PER_MESSAGE_RESERVE_TOKENS * len(rendered)
    input_tokens = serialized_bytes + framing
    limits = get_model_limits(model)
    budget = {
        "mode": "CONSERVATIVE_UTF8_BOUND" if limits else "UNKNOWN_MODEL_LIMITS",
        "checked": limits is not None,
        "input_tokens": input_tokens,
        "serialized_request_bytes": serialized_bytes,
        "framing_reserve_tokens": framing,
        "schema_representation": "SYSTEM_MESSAGE" if wrapped_schema else "NATIVE_JSON_SCHEMA",
        "input_limit": limits.input_tokens if limits else None,
        "context_limit": limits.input_tokens if limits and limits.shared_context else None,
        "shared_context": limits.shared_context if limits else None,
        "requested_output_tokens": requested_output_tokens,
        "output_tokens": requested_output_tokens,
        "max_output_tokens": limits.output_tokens if limits else None,
        "remaining_input_tokens": limits.input_tokens - input_tokens if limits else None,
        "remaining_context_tokens": None,
        "remaining_after_output_tokens": None,
        "fits": True,
        "source": limits.source if limits else "UNKNOWN_CALLABLE_ALIAS",
    }
    if limits is None:
        return budget
    output = min(requested_output_tokens or limits.output_tokens, limits.output_tokens)
    if limits.shared_context:
        remaining = limits.input_tokens - input_tokens
        output = min(output, max(0, remaining))
        budget["remaining_context_tokens"] = remaining
        budget["remaining_after_output_tokens"] = remaining - output
    budget["output_tokens"] = output
    budget["fits"] = input_tokens <= limits.input_tokens and output >= 1
    return budget


def check_request_budget(
    messages: list[dict],
    schema: dict,
    model: str,
    requested_output_tokens: int | None = None,
    provider: str = "cliproxyapi",
) -> dict:
    budget = request_budget(messages, schema, model, requested_output_tokens, provider)
    if not budget["fits"]:
        raise ContextBudgetError(model, provider, budget)
    return budget
