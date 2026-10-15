"""Provider routing, bounded recovery, and repair continuity without external APIs."""

import io
import json
from email.message import Message
from urllib.error import HTTPError, URLError

import pytest

from config.settings import CLIProxyConfig, GroqConfig
from rag.llm.answering import generate_answer
from rag.llm.client import RAGClient
from rag.llm.cliproxy_client import CLIProxyClient
from rag.llm.context import prepare_context
from rag.llm.errors import LLMError
from rag.llm.groq_client import GroqError
from tests.support.generation_scenarios import _generate


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
    return RAGClient(CLIProxyConfig(api_key="gateway-secret"), GroqConfig(keys=("groq-secret",)))


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
        assert payload["max_tokens"] == 8192
        assert "reasoning_format" not in payload and "include_reasoning" not in payload
        return io.BytesIO(json.dumps(api_response()).encode())

    monkeypatch.setattr("rag.llm.cliproxy_client.urlopen", send)
    result = client.complete(messages, schema)
    assert result["model"] == "gemini-3.8-flash-high"
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

    monkeypatch.setattr("rag.llm.cliproxy_client.urlopen", failed)
    monkeypatch.setattr(client.fallback, "_request", lambda *args: (api_response(), 1))
    result = client.complete([], {})
    assert result["failures"][0]["http_status"] == 503
    assert "gateway-secret" not in repr(result)


def test_quota_cooldown_uses_groq_without_retrying_primary_until_retry_after(client, monkeypatch):
    calls = []
    clock = [100.0]
    monkeypatch.setattr("rag.llm.client.time.monotonic", lambda: clock[0])

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

    monkeypatch.setattr("rag.llm.cliproxy_client.urlopen", failed)
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
