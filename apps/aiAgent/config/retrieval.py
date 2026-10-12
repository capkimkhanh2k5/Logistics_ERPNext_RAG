"""Pinned retrieval settings; changing them requires a new policy evaluation."""

from typing import Any

import yaml

from config.settings import ROOT


def retrieval_config() -> dict:
    return yaml.safe_load((ROOT / "config/rag.yaml").read_text())


INSTRUCTION = (
    "Retrieve cited source passages relevant to the query. For a product description, "
    "find matching tariff descriptions using their source hierarchy. For a legal question, "
    "find the source provisions that answer it. Do not assume unstated product attributes."
)
MODELS: dict[str, dict[str, Any]] = {
    "m3": {
        "model": "BAAI/bge-reranker-v2-m3",
        "revision": "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e",
        "backend": "cross_encoder",
        "batch_size": 4,
    },
    "qwen": {
        "model": "Qwen/Qwen3-Reranker-0.6B",
        "revision": "e61197ed45024b0ed8a2d74b80b4d909f1255473",
        "backend": "qwen",
        "batch_size": 8,
    },
    "gemma": {
        "model": "BAAI/bge-reranker-v2-gemma",
        "revision": "1787044f8b6fb740a9de4557c3a12377f84d9e17",
        "backend": "flag_llm",
        "batch_size": 4,
        "last_token_only": True,
    },
}
WEIGHTS = {
    "balanced": {"dense": 0.35, "sparse": 0.15, "bm25": 0.35, "fts": 0.05, "exact": 0.10},
    "lexical": {"dense": 0.25, "sparse": 0.25, "bm25": 0.10, "fts": 0.10, "exact": 0.30},
}
