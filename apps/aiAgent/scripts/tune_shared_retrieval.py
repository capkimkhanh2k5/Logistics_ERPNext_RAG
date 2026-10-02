#!/usr/bin/env python3
"""Select one shared retrieval policy on Dev, lock it, then evaluate Test."""

import argparse
import copy
import hashlib
import itertools
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from rag.data import ROOT, digest, read, write_json  # noqa: E402
from rag.db import connect  # noqa: E402
from rag.embedding import Embedder  # noqa: E402
from rag.retrieval import Retriever, fuse, unique_codes  # noqa: E402
from scripts.run_retrieval_experiment import (  # noqa: E402
    CandidateCache,
    cache_identity,
    compute_metrics,
    paired_cluster_interval,
)

RUN_DIR = ROOT / "artifacts/experiments/run_shared_dev_v3"
SPLIT_DIR = ROOT / "data/verified/hs/dev_test"
LATENCY_BUDGET_MS = 3000


def candidate_policies(baseline: dict) -> dict[str, dict]:
    result = {}
    for i, (dense, context_dense, pool, rank) in enumerate(
        itertools.product((0.35, 0.55), (0.0, 0.5), (40, 60, 80), (0.85, 1.0)), 1
    ):
        policy = copy.deepcopy(baseline)
        policy.update(graph_dense_weight=context_dense, rerank_pool=pool, rank_weight=rank)
        policy["weights"].update(dense=dense, bm25=round(0.7 - dense, 2))
        result[f"C{i:02d}"] = policy
    return result


def load_partition(name: str, manifest: dict) -> list[dict]:
    info = manifest["files"][name]
    path = SPLIT_DIR / info["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != info["sha256"]:
        raise ValueError(f"Frozen {name} data has changed")
    rows = read(path)
    if len(rows) != manifest["counts"][name] or any(r["split"] != name for r in rows):
        raise ValueError(f"Invalid {name} partition")
    return rows


def rank_scored_pool(rows: list[dict], policy: dict) -> dict:
    started = time.perf_counter()
    pool = rows[: policy["rerank_pool"]]
    ordered = sorted(pool, key=lambda r: (-r["rerank_score"], r["id"]))
    weight = policy["rank_weight"]
    ranked = (
        ordered
        if weight == 1.0
        else unique_codes(
            fuse(
                {"retrieval": pool, "rerank": ordered},
                policy["rrf_k"],
                {"retrieval": 1 - weight, "rerank": weight},
            ),
            len(pool),
        )
    )
    return {
        "ranked": ranked[:10],
        "pool_codes": [r["code"] for r in rows],
        "latency_ms": (time.perf_counter() - started) * 1000,
    }


def evaluate_policies(retriever: Retriever, cases: list[dict], policies: dict, phase: str) -> dict:
    # Scores are shared only for identical source pools; changing rank/pool does not retrain models.
    representatives: dict[str, dict] = {}
    for policy in policies.values():
        key = digest({"weights": policy["weights"], "dense": policy.get("graph_dense_weight", 0)})
        representatives.setdefault(key, policy)
    identity = {
        **cache_identity(retriever, cases),
        "tuning_script_hash": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "representatives": representatives,
        "score_pool": 80,
    }
    cache = CandidateCache(RUN_DIR / f"{phase}_scored_pools.sqlite", identity)
    predictions: dict[str, dict] = {key: {} for key in policies}
    saved_policy = retriever.product_policy
    try:
        for i, case in enumerate(cases, 1):
            query = case["query"]
            direct_pools = {}
            for key, representative in representatives.items():
                cache_key = digest({"query": query, "channels": key})
                scored = cache.get(cache_key)
                if scored is None:
                    retriever.product_policy = {
                        **representative,
                        "rerank_pool": 80,
                        "rank_weight": 1.0,
                    }
                    weight_key = digest(representative["weights"])
                    if weight_key not in direct_pools:
                        direct_pools[weight_key] = retriever.search(
                            query,
                            mode="full_hybrid",
                            levels=[8],
                            top_k=100,
                            expand=False,
                            weights=representative["weights"],
                            rrf_k=representative["rrf_k"],
                        )["candidates"]
                    pool = retriever.prepare_product_candidates(query, direct_pools[weight_key])
                    ordered = retriever.rank_product_candidates(query, pool)
                    scores = {r["id"]: r["rerank_score"] for r in ordered}
                    scored = [
                        {**r, **({"rerank_score": scores[r["id"]]} if r["id"] in scores else {})}
                        for r in pool
                    ]
                    cache.put(cache_key, scored)
                for name, policy in policies.items():
                    policy_key = digest(
                        {"weights": policy["weights"], "dense": policy.get("graph_dense_weight", 0)}
                    )
                    if policy_key == key:
                        predictions[name][case["record_id"]] = rank_scored_pool(scored, policy)
            if i % 20 == 0 or i == len(cases):
                print(
                    f"{phase}: scored {i}/{len(cases)} queries across {len(policies)} policies",
                    flush=True,
                )
    finally:
        retriever.product_policy = saved_policy
        cache.close()
    return predictions


def metrics(cases: list[dict], predictions: dict, policy: dict) -> dict:
    result = compute_metrics(cases, predictions, policy["rerank_pool"])
    result["latency_scope"] = "OFFLINE_SCORE_REPLAY_ONLY_USE_FRESH_RUNTIME_LATENCY"
    # Cached-score replay is a quality measurement; serving latency is measured separately.
    for summary in [result["ALL"], *result["sections"].values(), *result["chapters"].values()]:
        for key in ("latency_ms", "p50_latency_ms", "p95_latency_ms"):
            summary.pop(key, None)
    return result


def measure_latency(retriever: Retriever, cases: list[dict], policy: dict) -> dict:
    by_section = defaultdict(list)
    for row in cases:
        by_section[row["section"]].append(row)
    rng = np.random.default_rng(20261001)
    samples = [
        by_section[section][i]
        for section in sorted(by_section)
        for i in rng.permutation(len(by_section[section]))[:10]
    ]
    previous = retriever.product_policy
    retriever.product_policy = policy
    rows = []
    try:
        retriever.adaptive_search(samples[0]["query"], use_cache=False)
        for case in samples:
            start = time.perf_counter()
            output = retriever.adaptive_search(case["query"], use_cache=False)
            rows.append(
                {
                    "record_id": case["record_id"],
                    "section": case["section"],
                    "elapsed_ms": (time.perf_counter() - start) * 1000,
                    "query_cache_hit": output["timings"]["query_cache_hit"],
                }
            )
    finally:
        retriever.product_policy = previous
    times = [r["elapsed_ms"] for r in rows]
    return {
        "protocol": "WARM_MODELS_COLD_QUERY_AND_RERANK_CACHES_SINGLE_WORKER_DEV_SAMPLE",
        "count": len(rows),
        "p50_ms": float(np.percentile(times, 50)),
        "p95_ms": float(np.percentile(times, 95)),
        "rows": rows,
    }


def select_on_dev(retriever: Retriever, protocol: dict, manifest: dict) -> None:
    cases = load_partition("dev", manifest)
    policies = protocol["candidates"]
    predictions = evaluate_policies(retriever, cases, policies, "dev")
    all_metrics = {
        name: metrics(cases, predictions[name], policy) for name, policy in policies.items()
    }
    baseline = all_metrics["C01"]
    eligible = [
        name
        for name, result in all_metrics.items()
        if result["MACRO"]["recall@5"] >= baseline["MACRO"]["recall@5"]
        and all(
            result["sections"][s]["recall@5"] >= r["recall@5"] - 0.01
            for s, r in baseline["sections"].items()
        )
    ]
    eligible.sort(
        key=lambda name: (
            -all_metrics[name]["MACRO"]["mrr@10"],
            policies[name]["rerank_pool"],
            name,
        )
    )
    latencies = {}
    chosen = None
    for name in eligible:
        print(f"Dev latency check: {name}", flush=True)
        latencies[name] = measure_latency(retriever, cases, policies[name])
        write_json(RUN_DIR / "dev_latency_checks.json", latencies)
        if latencies[name]["p95_ms"] <= protocol["latency_budget_ms"]:
            chosen = name
            break
    if chosen is None:
        raise ValueError("No policy satisfies the frozen latency and recall requirements")
    fold_metrics = {
        str(f): metrics(
            [c for c in cases if c["dev_fold"] == f], predictions[chosen], policies[chosen]
        )
        for f in range(5)
    }
    selected = copy.deepcopy(policies[chosen])
    selected.update(
        version="generic-graph-v3-dev-selected",
        selection_scope="ONE_SHARED_POLICY_SELECTED_ON_752_DEV_CASES_TEST_NOT_USED",
    )
    selection = {
        "chosen": chosen,
        "policy": selected,
        "protocol_hash": digest(protocol),
        "split_manifest_hash": digest(manifest),
        "dev_metrics": all_metrics[chosen],
        "dev_fold_metrics": fold_metrics,
        "latency": latencies[chosen],
        "selection_scope": "DEV_ONLY_ON_PREVIOUSLY_SEEN_DATA_NOT_NESTED_CV",
    }
    write_json(RUN_DIR / "dev_metrics.json", all_metrics)
    write_json(RUN_DIR / "locked_selection.json", selection)
    print(
        json.dumps(
            {
                "chosen": chosen,
                "macro": all_metrics[chosen]["MACRO"],
                "latency_p95_ms": latencies[chosen]["p95_ms"],
            },
            indent=2,
        ),
        flush=True,
    )


def evaluate_test(retriever: Retriever, protocol: dict, manifest: dict) -> None:
    selection = read(RUN_DIR / "locked_selection.json")
    if selection["protocol_hash"] != digest(protocol) or selection["split_manifest_hash"] != digest(
        manifest
    ):
        raise ValueError("Selection, protocol or dataset identity differs")
    cases = load_partition("test", manifest)
    policies = {"baseline": protocol["baseline"], "selected": selection["policy"]}
    predictions = evaluate_policies(retriever, cases, policies, "test")
    results = {name: metrics(cases, predictions[name], policy) for name, policy in policies.items()}
    group_manifest = {"rows": cases}
    result = {
        "selection_hash": digest(selection),
        "scope": "FROZEN_POLICY_REGRESSION_ON_188_PREVIOUSLY_SEEN_TEST_CASES",
        "metrics": results,
        "paired": paired_cluster_interval(
            cases, group_manifest, predictions["baseline"], predictions["selected"]
        ),
    }
    write_json(RUN_DIR / "test_metrics.json", result)
    write_json(RUN_DIR / "test_predictions.json", predictions)
    print(json.dumps(results, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("dev", "test"))
    args = parser.parse_args()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manifest = read(SPLIT_DIR / "manifest.json")
    protocol_path = RUN_DIR / "protocol.json"
    protocol = {
        "baseline": read(ROOT / "config/hybrid_retrieval.json"),
        "split_manifest_hash": digest(manifest),
        "objective": "MACRO_MRR_AT_10; TIE_SMALLER_RERANK_POOL",
        "recall_constraints": "MACRO_R5_AT_LEAST_BASELINE; EACH_SECTION_R5_DROP_AT_MOST_0.01",
        "latency_budget_ms": LATENCY_BUDGET_MS,
        "test_access": "ONLY_AFTER_LOCKED_SELECTION",
    }
    protocol["candidates"] = candidate_policies(protocol["baseline"])
    if protocol_path.exists():
        if read(protocol_path) != protocol:
            raise ValueError("Frozen tuning protocol differs")
    else:
        if args.phase != "dev":
            raise ValueError("Select and lock a Dev policy before accessing Test")
        write_json(protocol_path, protocol)
    with connect() as conn:
        retriever = Retriever(conn, Embedder())
        if args.phase == "dev":
            if (RUN_DIR / "locked_selection.json").exists():
                raise ValueError("Dev selection is already locked")
            select_on_dev(retriever, protocol, manifest)
        else:
            evaluate_test(retriever, protocol, manifest)


if __name__ == "__main__":
    main()
