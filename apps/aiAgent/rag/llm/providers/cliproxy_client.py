"""Structured RAG completions through the configured CLIProxyAPI endpoint."""

import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.model_limits import get_model_limits
from config.settings import CLIProxyConfig
from rag.llm.contracts.errors import LLMError, transport_error_code
from rag.llm.providers.budget import build_request_messages, check_request_budget, schema_contract

ERROR_CODES = {
    "json_validate_failed",
    "rate_limit_exceeded",
    "model_not_found",
    "invalid_api_key",
    "invalid_request_error",
    "RESOURCE_EXHAUSTED",
    "UNAUTHENTICATED",
    "PERMISSION_DENIED",
}


class CLIProxyClient:
    def __init__(self, config: CLIProxyConfig | None = None):
        self.config = config or CLIProxyConfig.from_env()

    def _request(self, path: str, payload: dict | None = None) -> dict:
        self._transport_attempts: list[dict] = []
        retries = self.config.transport_retries if path == "/chat/completions" else 0
        for attempt in range(retries + 1):
            started = time.perf_counter()
            try:
                result = self._request_once(path, payload)
                self._transport_attempts.append(
                    {
                        "attempt": attempt + 1,
                        "ok": True,
                        "elapsed_ms": (time.perf_counter() - started) * 1000,
                    }
                )
                return result
            except LLMError as exc:
                retryable = exc.status == 503
                delay = (2, 5)[attempt] if retryable and attempt < retries else 0
                self._transport_attempts.append(
                    {
                        "attempt": attempt + 1,
                        "ok": False,
                        "http_status": exc.status,
                        "error_code": exc.error_code,
                        "retry_delay_seconds": delay,
                        "elapsed_ms": (time.perf_counter() - started) * 1000,
                    }
                )
                exc.transport_attempts = list(self._transport_attempts)
                if not delay:
                    raise
                time.sleep(delay)
        raise RuntimeError("Unreachable transport retry state")

    def _request_once(self, path: str, payload: dict | None = None) -> dict:
        if path not in {"/models", "/chat/completions"}:
            raise ValueError("Unsupported CLIProxyAPI path")
        model = (payload or {}).get("model", "")
        request = Request(
            self.config.base_url.rstrip("/") + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={
                "Authorization": "Bearer " + self.config.api_key,
                "Content-Type": "application/json",
                "User-Agent": "aiAgent-RAG/1.0",
            },
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:  # nosec B310
                return json.load(response)
        except HTTPError as exc:
            code = None
            err_msg = None
            try:
                err_data = json.load(exc)
                if isinstance(err_data, dict):
                    err_obj = err_data.get("error", {})
                    candidate = err_obj.get("code") if isinstance(err_obj, dict) else None
                    if candidate in ERROR_CODES:
                        code = candidate
                    details = err_obj.get("details") if isinstance(err_obj, dict) else None
                    msg = err_obj.get("message") if isinstance(err_obj, dict) else str(err_data)
                    err_msg = f"{msg} | details: {details}" if details else msg
            except (ValueError, AttributeError, TypeError):
                pass
            try:
                delay = float(exc.headers.get("retry-after", "60"))
                if not math.isfinite(delay) or delay < 0:
                    delay = 60
            except (ValueError, TypeError):
                delay = 60
            exc.close()
            raise LLMError(
                exc.code,
                model,
                delay if exc.code == 429 else 0,
                code,
                provider="cliproxyapi",
                message=err_msg,
            ) from None
        except (URLError, TimeoutError, OSError) as exc:
            raise LLMError(
                503, model, error_code=transport_error_code(exc), provider="cliproxyapi"
            ) from None
        except ValueError:
            raise LLMError(
                502, model, error_code="invalid_provider_response", provider="cliproxyapi"
            ) from None

    def models(self) -> list[dict]:
        return sorted(self._request("/models")["data"], key=lambda row: row["id"])

    def complete(self, messages: list[dict], schema: dict, *, model: str | None = None) -> dict:
        requested = model or self.config.model
        output_limit = self.config.max_output_tokens
        if output_limit is None and get_model_limits(requested) is None:
            output_limit = 8192
        budget = check_request_budget(messages, schema, requested, output_limit)
        payload = {
            "model": requested,
            "messages": build_request_messages(messages, schema, requested),
            "temperature": self.config.temperature,
            "max_tokens": budget["output_tokens"],
            "reasoning_effort": self.config.fallback_reasoning_effort
            if requested == self.config.fallback_model
            else self.config.reasoning_effort,
            "stream": False,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "grounded_rag_answer", "strict": True, "schema": schema},
            },
        }
        if requested.startswith("gpt-oss-"):
            # Antigravity rejects responseSchema for GPT-OSS through CLIProxyAPI v8.0.29.
            # Keep schema enforcement in RAG validation and its bounded repair pass.
            payload.pop("response_format")
        started = time.perf_counter()
        response = self._request("/chat/completions", payload)
        try:
            choice = response["choices"][0]
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Empty completion")
        except (KeyError, IndexError, TypeError, ValueError):
            raise LLMError(
                502, requested, error_code="invalid_provider_response", provider="cliproxyapi"
            ) from None
        return {
            "content": content,
            "finish_reason": choice.get("finish_reason"),
            "requested_model": requested,
            # Keep the callable alias for repairs; upstream may return a different modelVersion.
            "model": requested,
            "response_model": response.get("model"),
            "provider": "cliproxyapi",
            "fallback_used": False,
            "failures": [],
            "transport_attempts": list(getattr(self, "_transport_attempts", [])),
            "transport_retries": max(0, len(getattr(self, "_transport_attempts", [])) - 1),
            "usage": response.get("usage", {}),
            "request_budget": budget,
            "request_contract": schema_contract(
                schema,
                "json_schema_prompt" if requested.startswith("gpt-oss-") else "native_schema",
            ),
            "elapsed_ms": (time.perf_counter() - started) * 1000,
        }
