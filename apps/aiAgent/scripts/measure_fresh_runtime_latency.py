#!/usr/bin/env python3
"""Measure one shared runtime policy with query and reranker caches bypassed."""

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from rag.data import ROOT, write_json  # noqa: E402
from rag.db import connect  # noqa: E402
from rag.embedding import Embedder  # noqa: E402
from rag.evaluation import discover_gold, query_for  # noqa: E402
from rag.retrieval import Retriever  # noqa: E402


def stats(values: list[float]) -> dict:
    return {
        "count": len(values),
        "mean_ms": float(np.mean(values)),
        "p50_ms": float(np.percentile(values, 50)),
        "p95_ms": float(np.percentile(values, 95)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-section", type=int, default=10)
    parser.add_argument("--run-id", default="run_generic_graph_v2")
    args = parser.parse_args()
    if args.per_section < 1:
        raise ValueError("Sample count must be positive")
    cases, _ = discover_gold(("test", "holdout"))
    by_section = defaultdict(list)
    for case in cases:
        by_section[case["section"]].append(case)
    random = np.random.default_rng(20261001)
    samples = [
        c
        for section in sorted(by_section)
        for c in random.permutation(by_section[section])[: args.per_section]
    ]
    embedder = Embedder()
    with connect() as conn:
        retriever = Retriever(conn, embedder)
        # Warm model/index initialization; query computations below always bypass disk caches.
        retriever.adaptive_search(query_for(samples[0], "name_and_spec"), use_cache=False)
        rows = []
        for i, case in enumerate(samples, 1):
            started = time.perf_counter()
            out = retriever.adaptive_search(query_for(case, "name_and_spec"), use_cache=False)
            rows.append(
                {
                    "record_id": case["record_id"],
                    "section": case["section"],
                    "elapsed_ms": (time.perf_counter() - started) * 1000,
                    "query_cache_hit": out["timings"]["query_cache_hit"],
                }
            )
            print(f"Measured {i}/{len(samples)} cache-bypassed runtime queries", flush=True)
        result = {
            "snapshot": retriever.snapshot,
            "profile": retriever.profile,
            "policy": retriever.product_policy,
            "protocol": "WARM_MODELS_COLD_QUERY_AND_RERANK_CACHES_SINGLE_WORKER",
            "overall": stats([r["elapsed_ms"] for r in rows]),
            "sections": {
                s: stats([r["elapsed_ms"] for r in rows if r["section"] == s])
                for s in sorted(by_section)
            },
            "rows": rows,
        }
    target = ROOT / "artifacts/experiments" / args.run_id / "fresh_runtime_latency.json"
    write_json(target, result)
    print(result["overall"])


if __name__ == "__main__":
    main()
