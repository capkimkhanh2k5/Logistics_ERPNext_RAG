"""Context and output limits for the callable aliases supported by this RAG runtime."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelLimits:
    input_tokens: int
    output_tokens: int
    shared_context: bool = False
    source: str = "Configured callable model limits"

    def __post_init__(self):
        if self.input_tokens < 1 or self.output_tokens < 1:
            raise ValueError("Model input and output limits must be positive")


MODEL_LIMITS = {
    "gemini-3.8-flash-high": ModelLimits(
        1_048_576,
        65_536,
        source="https://ai.google.dev/gemini-api/docs/models",
    ),
    "gemini-3.5-flash-lite": ModelLimits(
        1_048_576,
        65_535,
        source=(
            "https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.29/"
            "internal/registry/models/models.json; version registry advertised, not boundary-tested"
        ),
    ),
    "gpt-oss-120b-medium": ModelLimits(
        114_000,
        32_768,
        shared_context=True,
        source=(
            "https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.29/"
            "internal/registry/models/models.json; version registry advertised, not boundary-tested"
        ),
    ),
    "qwen/qwen3.8-27b": ModelLimits(
        131_072,
        16_384,
        shared_context=True,
        source="https://console.groq.com/docs/models",
    ),
    "openai/gpt-oss-20b": ModelLimits(
        131_072,
        65_536,
        shared_context=True,
        source="https://console.groq.com/docs/models",
    ),
}


def get_model_limits(model: str) -> ModelLimits | None:
    """Unknown custom aliases keep their caller's existing limit policy."""
    return MODEL_LIMITS.get(model)
