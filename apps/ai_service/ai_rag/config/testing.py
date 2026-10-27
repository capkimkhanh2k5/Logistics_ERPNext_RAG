"""Notebook test controls, independent of RAG runtime settings."""

import math
import os
from dataclasses import dataclass

from config.settings import load_environment


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    if value not in {"true", "false", "1", "0"}:
        raise ValueError(f"{name} must be true/false or 1/0")
    return value in {"true", "1"}


@dataclass(frozen=True)
class GenerationTestConfig:
    run_tests: bool = True
    use_retrieval_cache: bool = True
    min_turn_interval_seconds: float = 40
    case_ids: tuple[str, ...] = ()
    run_custom_case: bool = False

    @classmethod
    def from_env(cls):
        load_environment()
        interval = float(
            os.getenv("RAG_TEST_MIN_TURN_INTERVAL_SECONDS", str(cls.min_turn_interval_seconds))
        )
        if not math.isfinite(interval) or not 0 <= interval <= 60:
            raise ValueError("RAG_TEST_MIN_TURN_INTERVAL_SECONDS must be between 0 and 60")
        return cls(
            run_tests=env_bool("RAG_TEST_RUN_TESTS", cls.run_tests),
            use_retrieval_cache=env_bool("RAG_TEST_USE_RETRIEVAL_CACHE", cls.use_retrieval_cache),
            min_turn_interval_seconds=interval,
            case_ids=tuple(
                x.strip() for x in os.getenv("RAG_TEST_CASE_IDS", "").split(",") if x.strip()
            ),
            run_custom_case=env_bool("RAG_TEST_RUN_CUSTOM_CASE", cls.run_custom_case),
        )
