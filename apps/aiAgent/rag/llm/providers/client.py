"""Enforce the session's provider policy at every model request."""

import time

from config.model_limits import get_model_limits
from config.settings import CLIProxyConfig, GroqConfig, RAGGenerationConfig
from rag.llm.contracts.errors import LLMError
from rag.llm.providers.budget import ContextBudgetError
from rag.llm.providers.cliproxy_client import CLIProxyClient
from rag.llm.providers.groq_client import GroqClient


class RAGClient:
    def __init__(
        self,
        primary_config: CLIProxyConfig | None = None,
        groq_config: GroqConfig | None = None,
        *,
        model_preset: str | None = None,
        allow_fallback: bool = False,
    ):
        config = primary_config or CLIProxyConfig.from_env(model_preset=model_preset)
        if primary_config is not None and model_preset is not None:
            config = config.with_model_preset(model_preset)
        self.allow_fallback = allow_fallback
        self.fallback = GroqClient(groq_config)
        self._set_primary_config(config)
        self.model_preset = model_preset
        self._retry_at: dict[str, float] = {}

    def _set_primary_config(self, config: CLIProxyConfig) -> None:
        groq = self.fallback.config
        cli_models = (config.model, config.fallback_model)
        if set(cli_models) & {groq.model, groq.fallback_model}:
            raise ValueError("CLIProxyAPI and Groq must use distinct model aliases")
        self.primary = CLIProxyClient(config)
        self._cli_models = cli_models
        model_budget = get_model_limits(config.model) is not None
        self.config = RAGGenerationConfig(
            model=config.model,
            fallback_model=config.fallback_model,
            max_input_chars=None if model_budget else groq.max_input_chars,
            max_context_chars=None if model_budget else groq.max_context_chars,
            fallback_models=(config.fallback_model, groq.model, groq.fallback_model)
            if self.allow_fallback
            else (),
            use_model_token_limits=model_budget,
            allow_fallback=self.allow_fallback,
        )

    def select_model(self, preset: str) -> None:
        self._set_primary_config(self.primary.config.with_model_preset(preset))
        self.model_preset = preset

    def complete(
        self,
        messages: list[dict],
        schema: dict,
        *,
        model: str | None = None,
        allow_fallback: bool = True,
    ) -> dict:
        requested = model or self.config.model
        if not self.allow_fallback and requested != self.config.model:
            raise ValueError("This session only permits the configured primary model")
        allow_fallback = self.allow_fallback and allow_fallback
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
            attempt_started = time.perf_counter()
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
                if exc.status == 429:
                    self._retry_at[candidate] = time.monotonic() + (exc.retry_after or 60)
                recoverable = (
                    exc.status in {401, 402, 403, 404, 408, 409, 429} or 500 <= exc.status < 600
                )
                recoverable |= isinstance(exc, ContextBudgetError)
                recoverable |= exc.status == 400 and exc.error_code == "json_validate_failed"
                if not allow_fallback or not recoverable:
                    raise
                failures.append(
                    {
                        "provider": "cliproxyapi",
                        "model": candidate,
                        "http_status": exc.status,
                        "error_code": exc.error_code,
                        "retry_after": exc.retry_after,
                        "transport_attempts": exc.transport_attempts,
                        "elapsed_ms": (time.perf_counter() - attempt_started) * 1000,
                        **(
                            {"request_budget": exc.budget}
                            if isinstance(exc, ContextBudgetError)
                            else {}
                        ),
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
