"""Typed runtime settings; process environment overrides the local .env file."""

import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def load_environment(*, override: bool = False) -> None:
    load_dotenv(ROOT / ".env", override=override)


def parse_keys(raw: str) -> tuple[str, ...]:
    values = json.loads(raw) if raw.strip().startswith("[") else re.split(r"[,;\s]+", raw)
    if not isinstance(values, list) or any(not isinstance(k, str) for k in values):
        raise ValueError("GROQ_API_KEYS must contain strings")
    return tuple(dict.fromkeys(k.strip() for k in values if k.strip()))


@dataclass(frozen=True)
class GroqConfig:
    keys: tuple[str, ...] = field(repr=False)
    model: str = "qwen/qwen3.8-27b"
    fallback_model: str = "openai/gpt-oss-20b"
    moderation_model: str = "meta-llama/llama-prompt-guard-2-86m"
    max_input_chars: int = 8000
    max_output_tokens: int = 2048
    max_context_chars: int = 6000
    reasoning_effort: str = "medium"
    timeout_seconds: float = 60
    max_wait_seconds: float = 45
    temperature: float = 0.2

    def __post_init__(self):
        if not self.keys:
            raise ValueError("Set GROQ_API_KEYS in the local .env file")
        for name in ("model", "fallback_model", "moderation_model"):
            if not getattr(self, name).strip():
                raise ValueError(f"GROQ_{name.upper()} must not be empty")
        for name in ("max_input_chars", "max_output_tokens", "max_context_chars"):
            if getattr(self, name) < 1:
                raise ValueError(f"GROQ_{name.upper()} must be positive")
        if self.reasoning_effort not in {"low", "medium", "high"}:
            raise ValueError("GROQ_REASONING_EFFORT must be low, medium or high")
        for name in ("timeout_seconds", "max_wait_seconds", "temperature"):
            if not math.isfinite(getattr(self, name)):
                raise ValueError(f"GROQ_{name.upper()} must be finite")
        if self.timeout_seconds <= 0 or self.max_wait_seconds < 0:
            raise ValueError("Groq timeout must be positive and wait must be nonnegative")
        if not 0 <= self.temperature <= 2:
            raise ValueError("GROQ_TEMPERATURE must be between 0 and 2")

    @classmethod
    def from_env(cls):
        load_environment()
        keys = parse_keys(os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY") or "")
        kwargs: dict[str, Any] = {"keys": keys}
        for name in ("model", "fallback_model", "moderation_model", "reasoning_effort"):
            kwargs[name] = os.getenv(f"GROQ_{name.upper()}", getattr(cls, name)).strip()
        for name in ("max_input_chars", "max_output_tokens", "max_context_chars"):
            kwargs[name] = int(os.getenv(f"GROQ_{name.upper()}", str(getattr(cls, name))))
        for name in ("timeout_seconds", "max_wait_seconds", "temperature"):
            kwargs[name] = float(os.getenv(f"GROQ_{name.upper()}", str(getattr(cls, name))))
        return cls(**kwargs)


@dataclass(frozen=True)
class CLIProxyConfig:
    api_key: str = field(repr=False)
    base_url: str = "http://127.0.0.1:8317/v1"
    model: str = "gemini-3.8-flash-high"
    fallback_model: str = "gpt-oss-120b-medium"
    fallback_reasoning_effort: str = "medium"
    max_output_tokens: int = 8192
    reasoning_effort: str = "high"
    timeout_seconds: float = 60
    temperature: float = 0.2

    def __post_init__(self):
        url = urlsplit(self.base_url)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username is not None
            or url.password is not None
            or url.query
            or url.fragment
        ):
            raise ValueError("CLIPROXYAPI_BASE_URL must be an HTTP(S) API base without credentials")
        if not self.api_key.strip():
            raise ValueError(
                "Set CLIPROXYAPI_API_KEY or initialize the local CLIProxyAPI credentials"
            )
        if not self.model.strip() or self.max_output_tokens < 1:
            raise ValueError("CLIProxyAPI requires a model and a positive output token budget")
        if not self.fallback_model.strip() or self.fallback_model == self.model:
            raise ValueError("CLIProxyAPI fallback model must be nonempty and distinct")
        if any(
            value not in {"low", "medium", "high"}
            for value in (self.reasoning_effort, self.fallback_reasoning_effort)
        ):
            raise ValueError("CLIPROXYAPI_REASONING_EFFORT must be low, medium or high")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("CLIPROXYAPI_TIMEOUT_SECONDS must be finite and positive")
        if not math.isfinite(self.temperature) or not 0 <= self.temperature <= 2:
            raise ValueError("CLIPROXYAPI_TEMPERATURE must be between 0 and 2")

    @classmethod
    def from_env(cls):
        load_environment()
        local = ROOT / "config/cliproxyapi/local/credentials.env"
        credentials = dotenv_values(local) if local.is_file() else {}
        return cls(
            api_key=os.getenv(
                "CLIPROXYAPI_API_KEY", credentials.get("CLIPROXYAPI_CLIENT_API_KEY") or ""
            ).strip(),
            base_url=os.getenv("CLIPROXYAPI_BASE_URL", cls.base_url).strip().rstrip("/"),
            model=os.getenv("CLIPROXYAPI_MODEL", cls.model).strip(),
            fallback_model=os.getenv("CLIPROXYAPI_FALLBACK_MODEL", cls.fallback_model).strip(),
            fallback_reasoning_effort=os.getenv(
                "CLIPROXYAPI_FALLBACK_REASONING_EFFORT", cls.fallback_reasoning_effort
            ).strip(),
            max_output_tokens=int(
                os.getenv("CLIPROXYAPI_MAX_OUTPUT_TOKENS", str(cls.max_output_tokens))
            ),
            reasoning_effort=os.getenv(
                "CLIPROXYAPI_REASONING_EFFORT", cls.reasoning_effort
            ).strip(),
            timeout_seconds=float(
                os.getenv("CLIPROXYAPI_TIMEOUT_SECONDS", str(cls.timeout_seconds))
            ),
            temperature=float(os.getenv("CLIPROXYAPI_TEMPERATURE", str(cls.temperature))),
        )


@dataclass(frozen=True)
class RAGGenerationConfig:
    model: str
    fallback_model: str
    max_input_chars: int
    max_context_chars: int
    fallback_models: tuple[str, ...] = ()


@dataclass(frozen=True)
class DatabaseConfig:
    password: str = field(repr=False)
    host: str = "127.0.0.1"
    port: int = 55432
    dbname: str = "hs_rag"
    user: str = "rag"

    def __post_init__(self):
        if not self.password:
            raise ValueError("Set RAG_DB_PASSWORD in the local .env file")
        if not 1 <= self.port <= 65535:
            raise ValueError("RAG_DB_PORT must be between 1 and 65535")

    @classmethod
    def from_env(cls):
        load_environment()
        return cls(
            password=os.getenv("RAG_DB_PASSWORD", ""),
            host=os.getenv("RAG_DB_HOST", cls.host),
            port=int(os.getenv("RAG_DB_PORT", str(cls.port))),
            dbname=os.getenv("RAG_DB_NAME", cls.dbname),
            user=os.getenv("RAG_DB_USER", cls.user),
        )
