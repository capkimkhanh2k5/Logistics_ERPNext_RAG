#!/usr/bin/env python3
"""Compare raw and planned retrieval against the same read-only corpus snapshot."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import DEFAULT_MODEL_PRESET, MODEL_PRESETS  # noqa: E402
from rag.embedding.bge_m3 import Embedder  # noqa: E402
from rag.llm.client import RAGClient  # noqa: E402
from rag.retrieval.query_planning import QueryPlanner  # noqa: E402
from rag.retrieval.retriever import Retriever  # noqa: E402
from rag.utils.files import digest, read, write_json  # noqa: E402
from rag.vectordb.postgres import connect, counts  # noqa: E402
from tests.support.generation_eval import json_safe  # noqa: E402


def compact(result: dict) -> dict:
    return {
        "query_plan": result.get("query_plan", {}),
        "retrieval_queries": result["retrieval_queries"],
        "hs_candidates": [r["code"] for r in result["hs_candidates"]],
        "top10": [
            {k: r.get(k) for k in ("id", "code", "chunk_type", "source_text")}
            for r in result["matches"]
        ],
        "pool_ids": [r["id"] for r in result["candidate_pool"]],
        "pool_codes": list(
            dict.fromkeys(r["code"] for r in result["candidate_pool"] if r.get("level") == 8)
        ),
        "timings": result["timings"],
        "reranking": result["reranking"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=Path, required=True, help="JSON list of {id, query}")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", choices=MODEL_PRESETS, default=DEFAULT_MODEL_PRESET)
    args = parser.parse_args()
    cases = read(args.queries)
    if not isinstance(cases, list) or not cases:
        parser.error("Provide at least one query")
    client = RAGClient(model_preset=args.model)
    with connect() as conn:
        conn.execute("SET default_transaction_read_only = on")
        retriever = Retriever(conn, Embedder(), query_planner=QueryPlanner(client))
        before = counts(conn, retriever.snapshot, retriever.profile)
        report = {
            "scope": "EXPLORATORY_RETRIEVAL_ONLY_NOT_HS_ACCURACY_EVALUATION",
            "cache_scope": "SEQUENTIAL_SHARED_EMBEDDING_AND_RERANK_CACHES_NOT_SPEED_BENCHMARK",
            "snapshot": retriever.snapshot,
            "profile": retriever.profile,
            "policy_hash": digest(retriever.unified_policy),
            "query_preprocessing_hash": retriever.query_preprocessing_hash(),
            "counts_before": before,
            "rows": [],
        }
        for case in cases:
            query = case["query"]
            raw = retriever.unified_search(query)
            planned = retriever.routed_search(query)
            report["rows"].append(
                {"id": case["id"], "query": query, "raw": compact(raw), "planned": compact(planned)}
            )
            write_json(args.out, json_safe(report))
            print(
                case["id"],
                planned["query_plan"]["status"],
                [r["code"] for r in planned["hs_candidates"][:3]],
                flush=True,
            )
        report["counts_after"] = counts(conn, retriever.snapshot, retriever.profile)
        report["active_after"] = conn.execute("SELECT snapshot,profile FROM rag.active").fetchone()
        assert report["counts_after"] == before, "Corpus counts changed during read-only diagnostic"
        write_json(args.out, json_safe(report))


if __name__ == "__main__":
    main()
