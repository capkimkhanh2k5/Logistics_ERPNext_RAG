"""Try Gemini and GPT-OSS through CLIProxyAPI before falling back to Groq."""

import time

from config.settings import CLIProxyConfig, GroqConfig, RAGGenerationConfig
from rag.llm.cliproxy_client import CLIProxyClient
from rag.llm.errors import LLMError
from rag.llm.groq_client import GroqClient


class RAGClient:
    def __init__(
        self, primary_config: CLIProxyConfig | None = None, groq_config: GroqConfig | None = None
    ):
        self.primary = CLIProxyClient(primary_config)
        self.fallback = GroqClient(groq_config)
        groq = self.fallback.config
        self._cli_models = (self.primary.config.model, self.primary.config.fallback_model)
        self.config = RAGGenerationConfig(
            model=self.primary.config.model,
            fallback_model=self.primary.config.fallback_model,
            max_input_chars=groq.max_input_chars,
            max_context_chars=groq.max_context_chars,
            fallback_models=(self.primary.config.fallback_model, groq.model, groq.fallback_model),
        )
        if set(self._cli_models) & {groq.model, groq.fallback_model}:
            raise ValueError("CLIProxyAPI and Groq must use distinct model aliases")
        self._retry_at: dict[str, float] = {}

    def complete(
        self,
        messages: list[dict],
        schema: dict,
        *,
        model: str | None = None,
        allow_fallback: bool = True,
    ) -> dict:
        requested = model or self.config.model
        groq_models = {self.fallback.config.model, self.fallback.config.fallback_model}
        if requested in groq_models:
            result = self.fallback.complete(
                messages, schema, model=requested, allow_fallback=allow_fallback
            )
            return {**result, "provider": "groq"}
        if requested not in self._cli_models:
            raise ValueError("Model must be the configured CLIProxyAPI model or Groq fallback")
        candidates = [requested]
        if allow_fallback and requested == self.config.model:
            candidates.append(self.primary.config.fallback_model)
        started = time.perf_counter()
        failures: list[dict] = []
        for candidate in candidates:
            try:
                remaining = self._retry_at.get(candidate, 0) - time.monotonic()
                if remaining > 0:
                    raise LLMError(429, candidate, remaining, provider="cliproxyapi")
                result = self.primary.complete(messages, schema, model=candidate)
                return {
                    **result,
                    "requested_model": requested,
                    "fallback_used": candidate != requested,
                    "failures": failures,
                    "elapsed_ms": (time.perf_counter() - started) * 1000,
                }
            except LLMError as exc:
                recoverable = (
                    exc.status in {401, 402, 403, 404, 408, 409, 429} or 500 <= exc.status < 600
                )
                recoverable |= exc.status == 400 and exc.error_code == "json_validate_failed"
                if not allow_fallback or not recoverable:
                    raise
                if exc.status == 429:
                    self._retry_at[candidate] = time.monotonic() + (exc.retry_after or 60)
                failures.append(
                    {
                        "provider": "cliproxyapi",
                        "model": candidate,
                        "http_status": exc.status,
                        "error_code": exc.error_code,
                        "retry_after": exc.retry_after,
                    }
                )
        result = self.fallback.complete(messages, schema, allow_fallback=True)
        return {
            **result,
            "provider": "groq",
            "requested_model": requested,
            "fallback_used": True,
            "failures": [*failures, *result.get("failures", [])],
            "elapsed_ms": (time.perf_counter() - started) * 1000,
        }
