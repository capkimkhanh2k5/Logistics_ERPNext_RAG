"""Structured RAG completions through the configured CLIProxyAPI endpoint."""

import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.model_limits import get_model_limits
from config.settings import CLIProxyConfig
from rag.llm.budget import build_request_messages, check_request_budget
from rag.llm.errors import LLMError

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
            try:
                candidate = json.load(exc).get("error", {}).get("code")
                if candidate in ERROR_CODES:
                    code = candidate
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
            ) from None
        except (URLError, TimeoutError, OSError):
            raise LLMError(503, model, provider="cliproxyapi") from None
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
            "usage": response.get("usage", {}),
            "request_budget": budget,
            "elapsed_ms": (time.perf_counter() - started) * 1000,
        }
