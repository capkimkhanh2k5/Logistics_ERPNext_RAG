"""Provider routing, bounded recovery, and repair continuity without external APIs."""

import io
import json
from email.message import Message
from urllib.error import HTTPError, URLError

import pytest

from config.model_limits import MODEL_LIMITS, ModelLimits
from config.settings import CLIProxyConfig, GroqConfig
from rag.llm.contracts.errors import LLMError
from rag.llm.generation.answering import generate_answer
from rag.llm.providers.budget import request_budget
from rag.llm.providers.client import RAGClient
from rag.llm.providers.cliproxy_client import CLIProxyClient
from rag.llm.providers.groq_client import GroqError
from rag.prompts.schemas.answer import ANSWER_SCHEMA
from tests.support.generation_scenarios import _generate
from tests.support.legacy_generation import prepare_legacy_context as prepare_context


def answer():
    return {
        "status": "ANSWERED",
        "answer": "A supported conclusion [S1].",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [{"label": "S1", "quote": "printed source passage"}],
        "missing_information": [],
        "missing_legal_evidence": [],
    }


def context():
    source = {"id": "fixture", "source_text": "A printed source passage with evidence."}
    return prepare_context("A question", {"matches": [source]}, "qa", GroqConfig(keys=("fixture",)))


def api_response(content=None):
    return {
        "model": "gemini-3.8-flash-n",
        "choices": [
            {
                "message": {"content": json.dumps(answer()) if content is None else content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


@pytest.fixture
def client():
    return RAGClient(
        CLIProxyConfig(api_key="gateway-secret"),
        GroqConfig(keys=("groq-secret",)),
        allow_fallback=True,
    )


@pytest.mark.parametrize("status", [400, 401, 429, 503])
def test_primary_only_session_cannot_be_reopened_by_call_flag(monkeypatch, status):
    client = RAGClient(CLIProxyConfig(api_key="fixture"), GroqConfig(keys=("fixture",)))
    calls = []

    def fail(path, payload):
        calls.append(payload["model"])
        raise LLMError(status, payload["model"], retry_after=60, provider="cliproxyapi")

    monkeypatch.setattr(client.primary, "_request", fail)
    monkeypatch.setattr(
        client.fallback, "complete", lambda *a, **kw: pytest.fail("Unexpected Groq")
    )
    with pytest.raises(LLMError) as error:
        client.complete([], {}, allow_fallback=True)
    assert error.value.status == status
    assert calls == [client.config.model]
    assert not client.config.allow_fallback
    assert client.config.fallback_models == ()


def test_primary_only_session_rejects_other_model_aliases_before_transport(monkeypatch):
    client = RAGClient(CLIProxyConfig(api_key="fixture"), GroqConfig(keys=("fixture",)))
    monkeypatch.setattr(
        client.primary, "complete", lambda *a, **kw: pytest.fail("Unexpected request")
    )
    monkeypatch.setattr(
        client.fallback, "complete", lambda *a, **kw: pytest.fail("Unexpected Groq")
    )
    for alias in [client.config.fallback_model, client.fallback.config.model, "unregistered-model"]:
        with pytest.raises(ValueError, match="configured primary model"):
            client.complete([], {}, model=alias, allow_fallback=True)


def test_explicit_model_switch_preserves_primary_only_policy(monkeypatch):
    client = RAGClient(CLIProxyConfig(api_key="fixture"), GroqConfig(keys=("fixture",)))
    for preset in ["3.8-high", "120b", "3.5-lite-high"]:
        client.select_model(preset)
        assert not client.allow_fallback and not client.config.allow_fallback
        assert client.config.fallback_models == ()
        monkeypatch.setattr(client.primary, "_request", lambda *a: api_response())
        result = client.complete([], {}, allow_fallback=True)
        assert result["model"] == client.config.model
        assert not result["fallback_used"]


def test_primary_sends_strict_schema_and_high_reasoning_without_groq_options(monkeypatch):
    client = CLIProxyClient(CLIProxyConfig(api_key="gateway-secret", timeout_seconds=1.5))
    messages = [{"role": "user", "content": "Question with context"}]
    schema = {"type": "object"}

    def send(request, **kwargs):
        payload = json.loads(request.data)
        assert request.full_url == "http://127.0.0.1:8317/v1/chat/completions"
        assert request.get_header("Authorization") == "Bearer gateway-secret"
        assert kwargs["timeout"] == 1.5
        assert payload["messages"] == messages
        assert payload["response_format"]["json_schema"] == {
            "name": "grounded_rag_answer",
            "strict": True,
            "schema": schema,
        }
        assert payload["reasoning_effort"] == "high"
        assert payload["max_tokens"] == 65535
        assert "reasoning_format" not in payload and "include_reasoning" not in payload
        return io.BytesIO(json.dumps(api_response()).encode())

    monkeypatch.setattr("rag.llm.providers.cliproxy_client.urlopen", send)
    result = client.complete(messages, schema)
    assert result["model"] == "gemini-3.5-flash-lite"
    assert result["response_model"] == "gemini-3.8-flash-n"


def test_healthy_primary_never_calls_groq(client, monkeypatch):
    monkeypatch.setattr(client.primary, "_request", lambda *args: api_response())
    monkeypatch.setattr(client.fallback, "_request", lambda *args: pytest.fail("Unexpected Groq"))
    result = generate_answer(context(), client)
    assert result["validation"]["valid"]
    assert result["generation"]["provider"] == "cliproxyapi"
    assert not result["generation"]["fallback_used"]


def test_gpt_oss_schema_prompt_avoids_unsupported_gateway_response_format(client, monkeypatch):
    messages = [{"role": "user", "content": "Question and sources"}]
    schema = {"type": "object", "properties": {"status": {"type": "string"}}}

    def send(path, payload):
        assert "response_format" not in payload
        assert payload["reasoning_effort"] == "medium"
        assert payload["messages"][0]["role"] == "system"
        assert json.dumps(schema) in payload["messages"][0]["content"]
        assert payload["messages"][1:] == messages
        return api_response()

    monkeypatch.setattr(client.primary, "_request", send)
    result = client.complete(messages, schema, model=client.config.fallback_model)
    assert result["model"] == client.config.fallback_model
    assert messages == [{"role": "user", "content": "Question and sources"}]


@pytest.mark.parametrize(
    "status", [401, 402, 403, 404, 408, 409, 429, 500, 501, 502, 503, 504, 529]
)
def test_provider_failure_falls_back_with_same_messages_and_schema(client, monkeypatch, status):
    messages, schema = [{"role": "user", "content": "Question and sources"}], {"type": "object"}

    def failed(path, payload):
        raise LLMError(status, payload["model"], retry_after=120, provider="cliproxyapi")

    def fallback(path, payload):
        assert payload["messages"] == messages
        assert payload["response_format"]["json_schema"]["schema"] == schema
        return api_response(), 1

    monkeypatch.setattr(client.primary, "_request", failed)
    monkeypatch.setattr(client.fallback, "_request", fallback)
    result = client.complete(messages, schema)
    assert result["provider"] == "groq"
    assert result["model"] == client.fallback.config.model
    assert result["requested_model"] == client.config.model
    assert result["fallback_used"]
    assert result["failures"][0]["http_status"] == status


@pytest.mark.parametrize("failure", [URLError("gateway-secret"), TimeoutError("gateway-secret")])
def test_transport_failure_is_secret_free_and_recovers(client, monkeypatch, failure):
    def failed(*args, **kwargs):
        raise failure

    monkeypatch.setattr("rag.llm.providers.cliproxy_client.urlopen", failed)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: (api_response(), 1))
    result = client.complete([], {})
    assert result["failures"][0]["http_status"] == 503
    assert "gateway-secret" not in repr(result)


def test_failed_provider_duration_is_separate_from_successful_fallback(client, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr("rag.llm.providers.client.time.perf_counter", lambda: clock[0])

    def complete(messages, schema, *, model):
        if model == client.config.model:
            clock[0] += 60
            raise LLMError(503, model, provider="cliproxyapi")
        clock[0] += 4
        return {"content": "{}", "finish_reason": "stop", "model": model}

    monkeypatch.setattr(client.primary, "complete", complete)
    result = client.complete([], {})
    assert result["failures"][0]["elapsed_ms"] == pytest.approx(60000)
    assert result["elapsed_ms"] == pytest.approx(64000)


def test_quota_cooldown_uses_groq_without_retrying_primary_until_retry_after(client, monkeypatch):
    calls = []
    clock = [100.0]
    monkeypatch.setattr("rag.llm.providers.client.time.monotonic", lambda: clock[0])

    def limited(path, payload):
        calls.append(payload["model"])
        raise LLMError(429, payload["model"], retry_after=120, provider="cliproxyapi")

    monkeypatch.setattr(client.primary, "_request", limited)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: (api_response(), 1))
    client.complete([], {})
    client.complete([], {})
    assert calls == [client.config.model, client.config.fallback_model]
    clock[0] = 221
    client.complete([], {})
    assert calls == [client.config.model, client.config.fallback_model] * 2


def test_gemini_quota_does_not_block_gpt_oss_quota(client, monkeypatch):
    calls = []

    def send(path, payload):
        calls.append(payload["model"])
        if payload["model"] == client.config.model:
            raise LLMError(429, payload["model"], retry_after=120, provider="cliproxyapi")
        assert payload["reasoning_effort"] == "medium"
        return api_response()

    monkeypatch.setattr(client.primary, "_request", send)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: pytest.fail("Unexpected Groq"))
    first = client.complete([], {})
    second = client.complete([], {})
    assert calls == [
        client.config.model,
        client.config.fallback_model,
        client.config.fallback_model,
    ]
    assert first["provider"] == second["provider"] == "cliproxyapi"
    assert first["model"] == second["model"] == client.config.fallback_model
    assert first["fallback_used"] and second["fallback_used"]
    assert first["requested_model"] == client.config.model
    assert first["failures"][0]["model"] == client.config.model


def test_gpt_oss_failure_does_not_put_gemini_on_cooldown(client, monkeypatch):
    calls = []

    def send(path, payload):
        calls.append(payload["model"])
        if payload["model"] == client.config.fallback_model:
            raise LLMError(429, payload["model"], retry_after=120, provider="cliproxyapi")
        return api_response()

    monkeypatch.setattr(client.primary, "_request", send)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: (api_response(), 1))
    assert client.complete([], {}, model=client.config.fallback_model)["provider"] == "groq"
    assert client.complete([], {})["provider"] == "cliproxyapi"
    assert calls == [client.config.fallback_model, client.config.model]


def test_unrelated_bad_request_and_explicit_no_fallback_do_not_switch_provider(client, monkeypatch):
    def failed(path, payload):
        raise LLMError(
            400, payload["model"], error_code="invalid_request_error", provider="cliproxyapi"
        )

    monkeypatch.setattr(client.primary, "_request", failed)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: pytest.fail("Unexpected Groq"))
    with pytest.raises(LLMError, match="HTTP 400"):
        client.complete([], {})
    monkeypatch.setattr(client.primary, "_request", lambda *args: {})
    with pytest.raises(LLMError, match="HTTP 502"):
        client.complete([], {}, allow_fallback=False)


@pytest.mark.parametrize("body", [{}, {"choices": []}, api_response("")])
def test_malformed_or_empty_gateway_response_recovers(client, monkeypatch, body):
    monkeypatch.setattr(client.primary, "_request", lambda *args: body)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: (api_response(), 1))
    result = client.complete([], {})
    assert result["fallback_used"]
    assert result["failures"][0]["error_code"] == "invalid_provider_response"


def test_http_failure_keeps_only_allowlisted_error_details(monkeypatch):
    def failed(request, **kwargs):
        body = io.BytesIO(
            json.dumps(
                {
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": "gateway-secret",
                    }
                }
            ).encode()
        )
        headers = Message()
        headers["retry-after"] = "120"
        raise HTTPError(request.full_url, 429, "gateway-secret", headers, body)

    monkeypatch.setattr("rag.llm.providers.cliproxy_client.urlopen", failed)
    with pytest.raises(LLMError) as error:
        CLIProxyClient(CLIProxyConfig(api_key="gateway-secret")).complete([], {})
    assert error.value.retry_after == 120
    assert error.value.error_code == "rate_limit_exceeded"
    assert "gateway-secret" not in str(error.value)


@pytest.mark.parametrize("use_fallback", [False, True])
def test_repairs_stay_on_the_same_callable_model(client, monkeypatch, use_fallback):
    calls = []
    invalid = {**answer(), "answer": "Missing inline citation"}

    def primary(path, payload):
        calls.append(payload["model"])
        if use_fallback:
            raise LLMError(503, payload["model"], provider="cliproxyapi")
        return api_response(json.dumps(invalid if len(calls) == 1 else answer()))

    def groq(path, payload):
        calls.append(payload["model"])
        count = calls.count(client.fallback.config.model)
        return api_response(json.dumps(invalid if count == 1 else answer())), 1

    monkeypatch.setattr(client.primary, "_request", primary)
    monkeypatch.setattr(client.fallback, "_request", groq)
    result = generate_answer(context(), client)
    assert result["validation"]["valid"]
    actual = client.fallback.config.model if use_fallback else client.config.model
    expected = [client.config.model, client.config.fallback_model, actual, actual]
    assert calls == (expected if use_fallback else [actual, actual])
    assert result["generation"]["fallback_used"] is use_fallback


def test_gpt_oss_repair_does_not_restart_the_chain_or_switch_to_groq(client, monkeypatch):
    calls = []
    invalid = {**answer(), "answer": "Missing inline citation"}

    def send(path, payload):
        calls.append(payload["model"])
        if payload["model"] == client.config.model:
            raise LLMError(503, payload["model"], provider="cliproxyapi")
        count = calls.count(client.config.fallback_model)
        return api_response(json.dumps(invalid if count == 1 else answer()))

    monkeypatch.setattr(client.primary, "_request", send)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: pytest.fail("Unexpected Groq"))
    result = generate_answer(context(), client)
    assert result["validation"]["valid"]
    assert calls == [
        client.config.model,
        client.config.fallback_model,
        client.config.fallback_model,
    ]
    assert result["generation"]["model"] == client.config.fallback_model
    assert result["generation"]["fallback_used"]


def test_groq_secondary_model_is_available_after_primary_and_groq_primary_fail(client, monkeypatch):
    calls = []

    def primary(path, payload):
        raise LLMError(503, payload["model"], provider="cliproxyapi")

    def groq(path, payload):
        calls.append(payload["model"])
        if payload["model"] == client.fallback.config.model:
            raise GroqError(429, payload["model"], retry_after=120)
        return api_response(), 1

    monkeypatch.setattr(client.primary, "_request", primary)
    monkeypatch.setattr(client.fallback, "_request", groq)
    result = client.complete([], {})
    assert calls == [client.fallback.config.model, client.fallback.config.fallback_model]
    assert result["model"] == client.fallback.config.fallback_model
    assert [error["http_status"] for error in result["failures"]] == [503, 503, 429]


def test_both_providers_unavailable_propagates_safe_provider_failure(client, monkeypatch):
    def failed(path, payload):
        raise LLMError(503, payload["model"], provider="cliproxyapi")

    def failed_groq(path, payload):
        raise GroqError(503, payload["model"])

    monkeypatch.setattr(client.primary, "_request", failed)
    monkeypatch.setattr(client.fallback, "_request", failed_groq)
    with pytest.raises(LLMError) as error:
        client.complete([], {})
    assert error.value.provider == "groq"


def test_notebook_fault_injection_targets_gateway_and_restores_transport(client, monkeypatch):
    def original(path, payload):
        assert payload["model"] == client.config.fallback_model
        return api_response()

    monkeypatch.setattr(client.primary, "_request", original)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: pytest.fail("Unexpected Groq"))
    result = _generate(context(), client, "primary_unavailable")
    assert result["validation"]["valid"]
    assert result["generation"]["provider"] == "cliproxyapi"
    assert result["generation"]["model"] == client.config.fallback_model
    assert result["generation"]["failures"][0]["http_status"] == 503
    assert client.primary._request is original


@pytest.mark.parametrize(
    "preset,model,effort,fallback",
    [
        ("3.5-lite-high", "gemini-3.5-flash-lite", "high", "gpt-oss-120b-medium"),
        ("3.8-high", "gemini-3.8-flash-high", "high", "gpt-oss-120b-medium"),
        ("120b", "gpt-oss-120b-medium", "medium", "gemini-3.5-flash-lite"),
    ],
)
def test_selected_model_sends_bound_alias_and_effort_without_duplicate_fallback(
    monkeypatch, preset, model, effort, fallback
):
    config = CLIProxyConfig(
        api_key="fixture-key", base_url="http://fixture-gateway/v1", max_output_tokens=4096
    )
    rag_client = RAGClient(config, GroqConfig(keys=("fixture-groq",)), model_preset=preset)
    calls = []

    def send(_self, path, payload):
        calls.append(payload)
        return api_response()

    monkeypatch.setattr(CLIProxyClient, "_request", send)
    result = rag_client.complete([], {"type": "object"}, allow_fallback=False)
    assert len(calls) == 1
    assert calls[0]["model"] == model
    assert calls[0]["reasoning_effort"] == effort
    assert calls[0]["max_tokens"] == 4096
    assert ("response_format" in calls[0]) == (preset != "120b")
    assert rag_client.primary.config.base_url == config.base_url
    assert rag_client.primary.config.api_key == config.api_key
    assert rag_client.config.fallback_model == fallback
    assert rag_client.config.fallback_models == ()
    assert not rag_client.config.allow_fallback
    assert rag_client._cli_models == (model, fallback)
    assert result["model"] == result["requested_model"] == model
    assert not result["fallback_used"]


def test_switching_presets_retains_groq_state_and_gateway_settings(client):
    groq_client = client.fallback
    original = client.primary.config
    cooldown = client._retry_at
    cooldown[original.model] = 1234
    for preset, primary_effort, fallback_effort in [
        ("120b", "medium", "high"),
        ("3.8-high", "high", "medium"),
        ("3.5-lite-high", "high", "medium"),
        ("120b", "medium", "high"),
    ]:
        client.select_model(preset)
        config = client.primary.config
        assert client.model_preset == preset
        assert client.fallback is groq_client
        assert client._retry_at is cooldown
        assert client._retry_at[original.model] == 1234
        assert config.reasoning_effort == primary_effort
        assert config.fallback_reasoning_effort == fallback_effort
        assert config.model != config.fallback_model
        assert config.api_key == original.api_key
        assert config.base_url == original.base_url
        assert config.max_output_tokens == original.max_output_tokens
        assert client.config.max_input_chars is None
        assert client.config.max_context_chars is None
        assert client.config.use_model_token_limits


def test_invalid_model_selection_does_not_partially_mutate_client(client):
    before = client.primary, client.config, client._cli_models, client.model_preset
    with pytest.raises(ValueError):
        client.select_model("unavailable-model")
    assert (client.primary, client.config, client._cli_models, client.model_preset) == before


def test_model_selection_rejects_groq_alias_collision_without_mutation():
    rag_client = RAGClient(
        CLIProxyConfig(api_key="fixture", model="gemini-3.8-flash-high"),
        GroqConfig(keys=("fixture",), model="gemini-3.5-flash-lite"),
    )
    before = rag_client.primary, rag_client.config, rag_client.model_preset
    with pytest.raises(ValueError):
        rag_client.select_model("3.5-lite-high")
    assert (rag_client.primary, rag_client.config, rag_client.model_preset) == before


def test_pinned_quota_cooldown_survives_switching_away_and_back(client, monkeypatch):
    calls = []
    lite = "gemini-3.5-flash-lite"
    monkeypatch.setattr("rag.llm.providers.client.time.monotonic", lambda: 100)

    def send(_self, path, payload):
        calls.append(payload["model"])
        if payload["model"] == lite:
            raise LLMError(429, lite, retry_after=120, provider="cliproxyapi")
        return api_response()

    monkeypatch.setattr(CLIProxyClient, "_request", send)
    with pytest.raises(LLMError):
        client.complete([], {}, allow_fallback=False)
    client.select_model("3.8-high")
    client.select_model("3.5-lite-high")
    with pytest.raises(LLMError) as raised:
        client.complete([], {}, allow_fallback=False)
    assert raised.value.status == 429
    assert calls == [lite]
    result = client.complete([], {})
    assert calls == [lite, "gpt-oss-120b-medium"]
    assert result["requested_model"] == lite
    assert result["fallback_used"]
    assert result["failures"][0]["http_status"] == 429


def test_120b_primary_fallback_uses_lite_high_then_preserves_requested_model(client, monkeypatch):
    client.select_model("120b")
    calls = []

    def send(_self, path, payload):
        calls.append((payload["model"], payload["reasoning_effort"]))
        if payload["model"] == "gpt-oss-120b-medium":
            raise LLMError(503, payload["model"], provider="cliproxyapi")
        return api_response()

    monkeypatch.setattr(CLIProxyClient, "_request", send)
    result = client.complete([], {})
    assert calls == [("gpt-oss-120b-medium", "medium"), ("gemini-3.5-flash-lite", "high")]
    assert result["requested_model"] == "gpt-oss-120b-medium"
    assert result["model"] == "gemini-3.5-flash-lite"
    assert result["fallback_used"]


@pytest.mark.parametrize(
    "preset,output_limit",
    [("3.8-high", 65536), ("3.5-lite-high", 65535), ("120b", 32768)],
)
def test_full_output_limit_is_selected_per_model_and_usage_stays_provider_measured(
    client, monkeypatch, preset, output_limit
):
    client.select_model(preset)
    calls = []

    def send(_self, path, payload):
        calls.append(payload)
        response = api_response()
        response["usage"] = {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}
        return response

    monkeypatch.setattr(CLIProxyClient, "_request", send)
    result = client.complete([], {})
    assert calls[0]["max_tokens"] == output_limit
    assert result["request_budget"]["output_tokens"] == output_limit
    assert result["request_budget"]["mode"] == "CONSERVATIVE_UTF8_BOUND"
    assert result["usage"]["completion_tokens"] == 2
    assert client.config.max_input_chars is client.config.max_context_chars is None


def test_smaller_fallback_cannot_send_an_overbudget_request_or_drop_input(client, monkeypatch):
    monkeypatch.setitem(
        MODEL_LIMITS,
        "gpt-oss-120b-medium",
        ModelLimits(500, 100, shared_context=True),
    )
    original = [{"role": "user", "content": "Full product facts and full source wording."}]
    calls = []

    def primary(_self, path, payload):
        calls.append(payload["model"])
        raise LLMError(503, payload["model"], provider="cliproxyapi")

    def groq(path, payload):
        calls.append(payload["model"])
        assert payload["messages"] == original
        return api_response(), 1

    monkeypatch.setattr(CLIProxyClient, "_request", primary)
    monkeypatch.setattr(client.fallback, "_request", groq)
    result = client.complete(original, {})
    assert calls == [client.config.model, client.fallback.config.model]
    assert original == [{"role": "user", "content": "Full product facts and full source wording."}]
    assert result["failures"][1]["error_code"] == "context_length_exceeded"
    assert result["failures"][1]["request_budget"]["fits"] is False


def test_repair_budget_failure_keeps_invalid_attempt_and_returns_safe_diagnostic(
    client, monkeypatch
):
    ctx = context()
    initial = request_budget(ctx["messages"], ANSWER_SCHEMA, client.config.model)
    monkeypatch.setitem(
        MODEL_LIMITS,
        client.config.model,
        ModelLimits(initial["input_tokens"], 100),
    )
    calls = []

    def send(_self, path, payload):
        calls.append(payload)
        return api_response("not JSON")

    monkeypatch.setattr(CLIProxyClient, "_request", send)
    result = generate_answer(ctx, client)
    assert len(calls) == 1
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["generation"]["repair_budget_error"]["fits"] is False
    assert result["generation"]["attempts"][0]["content"] == "not JSON"
