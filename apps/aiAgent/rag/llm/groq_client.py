"""Groq REST client with secret-free diagnostics and bounded key rotation."""

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.settings import GroqConfig
from rag.llm.errors import LLMError

API_BASE = "https://api.groq.com/openai/v1"


class GroqError(LLMError):
    def __init__(
        self, status: int, model: str, retry_after: float = 0, error_code: str | None = None
    ):
        super().__init__(status, model, retry_after, error_code, provider="groq")


class GroqClient:
    def __init__(self, config: GroqConfig | None = None):
        self.config = config or GroqConfig.from_env()
        if not self.config.keys:
            raise ValueError("At least one Groq key is required")
        self._cursor = 0
        self._disabled: set[int] = set()
        self._cooldown: dict[str, float] = {}

    def _slot(self) -> int:
        for _ in self.config.keys:
            slot = self._cursor % len(self.config.keys)
            self._cursor += 1
            if slot not in self._disabled:
                return slot
        raise GroqError(401, "")

    def _request(self, path: str, payload: dict | None = None) -> tuple[dict, int]:
        if path not in {"/models", "/chat/completions"}:
            raise ValueError("Unsupported Groq API path")
        model = (payload or {}).get("model", "")
        last_error = GroqError(503, model)
        for attempt in range(max(2, len(self.config.keys))):
            remaining = self._cooldown.get(model, 0) - time.monotonic()
            if remaining > self.config.max_wait_seconds:
                raise GroqError(429, model, remaining)
            if remaining > 0:
                time.sleep(remaining)
            slot = self._slot()
            request = Request(
                API_BASE + path,
                data=json.dumps(payload).encode() if payload is not None else None,
                headers={
                    "Authorization": "Bearer " + self.config.keys[slot],
                    "Content-Type": "application/json",
                    "User-Agent": "aiAgent-RAG/1.0",
                },
            )
            try:
                # Fixed HTTPS origin and allowlisted endpoint paths.
                with urlopen(request, timeout=self.config.timeout_seconds) as response:  # nosec B310
                    return json.load(response), slot + 1
            except HTTPError as exc:
                error_code = None
                try:
                    code = json.load(exc).get("error", {}).get("code")
                    if code in {
                        "json_validate_failed",
                        "rate_limit_exceeded",
                        "model_not_found",
                        "invalid_api_key",
                        "invalid_request_error",
                    }:
                        error_code = code
                except (ValueError, AttributeError, TypeError):
                    pass
                try:
                    delay = max(1.0, float(exc.headers.get("retry-after", "2")))
                except ValueError:
                    delay = 2.0
                last_error = GroqError(exc.code, model, delay if exc.code == 429 else 0, error_code)
                exc.close()
                if exc.code == 401:
                    self._disabled.add(slot)
                elif exc.code == 429:
                    # Organization limits apply to every key; do not bypass them by rotating.
                    self._cooldown[model] = time.monotonic() + delay
                elif exc.code not in {403, 408, 500, 502, 503, 504}:
                    raise last_error from None
                elif exc.code != 403:
                    time.sleep(min(2**attempt, self.config.max_wait_seconds))
            except (URLError, TimeoutError, OSError):
                last_error = GroqError(503, model)
        raise last_error from None

    def models(self) -> list[dict]:
        result, _ = self._request("/models")
        return sorted(result["data"], key=lambda r: r["id"])

    def complete(
        self,
        messages: list[dict],
        schema: dict,
        *,
        model: str | None = None,
        allow_fallback: bool = True,
    ) -> dict:
        requested = model or self.config.model
        models = [requested]
        if allow_fallback and self.config.fallback_model not in models:
            models.append(self.config.fallback_model)
        failures: list[dict[str, Any]] = []
        started = time.perf_counter()
        for candidate in models:
            payload = {
                "model": candidate,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_completion_tokens": self.config.max_output_tokens,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "grounded_rag_answer",
                        "strict": True,
                        "schema": schema,
                    },
                },
                "reasoning_effort": self.config.reasoning_effort,
            }
            if candidate.startswith("qwen/"):
                payload["reasoning_format"] = "hidden"
            else:
                payload["include_reasoning"] = False
            try:
                response, slot = self._request("/chat/completions", payload)
            except GroqError as exc:
                failures.append(
                    {
                        "model": candidate,
                        "http_status": exc.status,
                        "error_code": exc.error_code,
                        "retry_after": exc.retry_after,
                    }
                )
                invalid_generation = exc.status == 400 and exc.error_code == "json_validate_failed"
                if not invalid_generation and exc.status not in {
                    403,
                    404,
                    408,
                    429,
                    500,
                    502,
                    503,
                    504,
                }:
                    raise
                continue
            choice = response["choices"][0]
            return {
                "content": choice["message"].get("content") or "",
                "finish_reason": choice.get("finish_reason"),
                "requested_model": requested,
                "model": candidate,
                "response_model": response.get("model"),
                "provider": "groq",
                "key_slot": slot,
                "fallback_used": candidate != requested,
                "failures": failures,
                "usage": response.get("usage", {}),
                "elapsed_ms": (time.perf_counter() - started) * 1000,
            }
        raise GroqError(
            failures[-1]["http_status"],
            models[-1],
            retry_after=failures[-1]["retry_after"],
            error_code=failures[-1]["error_code"],
        )
