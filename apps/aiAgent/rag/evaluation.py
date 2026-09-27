"""Frozen grouped split and candidate benchmarks without label leakage."""

import random
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import numpy as np
from psycopg.types.json import Jsonb

from rag.data import GOLD, ROOT, config, digest, read, write_json
from rag.retrieval import Retriever


def grouped_split() -> dict:
    gold = read(GOLD)
    groups: dict[str, list] = defaultdict(list)
    for row in gold:
        groups[row["expected_hs_8"]].append(row)
    rng = random.Random(config()["seed"])
    test_codes = set()
    for chapter in ("84", "85"):
        codes = sorted(code for code in groups if code.startswith(chapter))
        rng.shuffle(codes)
        test_codes.update(codes[: round(len(codes) * 0.4)])
    split = {
        "seed": config()["seed"],
        "gold_sha256": digest(gold),
        "dev": [g["test_id"] for g in gold if g["expected_hs_8"] not in test_codes],
        "test": [g["test_id"] for g in gold if g["expected_hs_8"] in test_codes],
        "grouping": "expected_hs_8",
        "label_verification": "EXISTING_LOCAL_LABELS",
    }
    path = ROOT / "config/evaluation_split.json"
    if path.exists():
        if read(path) != split:
            raise ValueError("Frozen split differs from gold/config; version the split explicitly")
    else:
        write_json(path, split)
    assert set(split["dev"]).isdisjoint(split["test"])
    dev_codes = {g["expected_hs_8"] for g in gold if g["test_id"] in split["dev"]}
    heldout_codes = {g["expected_hs_8"] for g in gold if g["test_id"] in split["test"]}
    assert dev_codes.isdisjoint(heldout_codes)
    return split


def query_for(row: dict, variant: str) -> str:
    if variant == "name_only":
        return row["product_name_vi"]
    if variant == "name_and_spec":
        return row["product_name_vi"] + ". " + row["technical_description_for_test"]
    raise ValueError("Unknown query variant")


def metrics(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("No evaluation samples")
    rank = [r["gold_rank"] for r in rows]
    result: dict[str, Any] = {"count": len(rows)}
    for k in (1, 3, 5, 10):
        result[f"hit@{k}"] = sum(r is not None and r <= k for r in rank) / len(rank)
    result["mrr@10"] = sum(1 / r if r and r <= 10 else 0 for r in rank) / len(rank)
    per_code: dict[str, list] = defaultdict(list)
    for row in rows:
        per_code[row["gold"]].append(row)
    result["macro_code_hit@10"] = float(
        np.mean(
            [
                np.mean([r["gold_rank"] is not None and r["gold_rank"] <= 10 for r in group])
                for group in per_code.values()
            ]
        )
    )
    result["latency_p50_ms"] = float(np.percentile([r["timings"]["total_ms"] for r in rows], 50))
    result["latency_p95_ms"] = float(np.percentile([r["timings"]["total_ms"] for r in rows], 95))
    result["failures@10"] = [r["test_id"] for r in rows if r["gold_rank"] is None]
    return result


def evaluate(
    retriever: Retriever,
    split_name: str = "dev",
    mode: str = "hybrid",
    expand: bool = False,
    weights: dict | None = None,
    cases: list[dict] | None = None,
    persist: bool = False,
) -> dict:
    if cases is None and split_name not in ("dev", "test"):
        raise ValueError("Split must be dev or test")
    split = grouped_split()
    gold = (
        cases if cases is not None else [r for r in read(GOLD) if r["test_id"] in split[split_name]]
    )
    run_config = {
        "snapshot": retriever.snapshot,
        "profile": retriever.profile,
        "split": split_name,
        "split_hash": digest(split),
        "mode": mode,
        "weights": weights or retriever.weights,
        "evaluation_status": "PREVIOUSLY_EXPOSED_REPRODUCTION"
        if split_name == "test"
        else "SOURCE_GROUNDED_CHALLENGE"
        if cases is not None
        else "DEVELOPMENT",
        "expand": expand,
        "retrieval": retriever.cfg,
        "variants": ["query"] if cases is not None else ["name_only", "name_and_spec"],
    }
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "-" + digest(run_config)[:8]
    results = []
    for row in gold:
        for variant in run_config["variants"]:
            output = retriever.search(
                row["query"] if variant == "query" else query_for(row, variant),
                mode=mode,
                top_k=10,
                expand=expand,
                weights=weights,
            )
            codes = [r["code"] for r in output["candidates"]]
            rank = codes.index(row["expected_hs_8"]) + 1 if row["expected_hs_8"] in codes else None
            results.append(
                {
                    "test_id": row["test_id"],
                    "variant": variant,
                    "gold": row["expected_hs_8"],
                    "gold_rank": rank,
                    "codes": codes,
                    "timings": output["timings"],
                    "retrieval": output,
                }
            )
        print(f"{split_name}/{mode}: {row['test_id']}", flush=True)
    summary = {
        variant: metrics([r for r in results if r["variant"] == variant])
        for variant in run_config["variants"]
    }
    artifact = {
        "run_id": run_id,
        "config": run_config,
        "metrics": summary,
        "results": results,
        "scope": "CANDIDATE_RETRIEVAL_ONLY",
        "evidence_qrels": "NOT_INDEPENDENTLY_ANNOTATED",
    }
    if persist:
        with retriever.conn.transaction():
            retriever.conn.execute(
                "INSERT INTO rag.evaluation_runs(id,snapshot,config,metrics) VALUES (%s,%s,%s,%s)",
                (run_id, retriever.snapshot, Jsonb(run_config), Jsonb(summary)),
            )
            with retriever.conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO rag.retrieval_results VALUES (%s,%s,%s,%s)",
                    [(run_id, r["test_id"], r["variant"], Jsonb(r)) for r in results],
                )
    return artifact


def select_dev(runs: list[dict]) -> dict:
    if any(r["config"]["split"] != "dev" for r in runs):
        raise ValueError("Selection accepts development runs only")
    selected = max(
        runs,
        key=lambda r: (
            r["metrics"]["name_and_spec"]["hit@10"],
            r["metrics"]["name_and_spec"]["mrr@10"],
        ),
    )
    result = {
        "selected_mode": selected["config"]["mode"],
        "weights": selected["config"]["weights"],
        "snapshot": selected["config"]["snapshot"],
        "profile": selected["config"]["profile"],
        "dev_run_ids": [r["run_id"] for r in runs],
        "selection_metric": "name_and_spec Hit@10, then MRR@10",
        "retrieval": selected["config"]["retrieval"],
    }
    write_json(ROOT / "config/selected_retrieval.json", result)
    return result


def evidence_metrics(retriever: Retriever, cases: list[dict], mode: str | None = None) -> dict:
    rows = []
    for case in cases:
        result = retriever.search(
            case["query"], intent=case["intent"], mode=mode, top_k=5, expand=False
        )
        matches = result["matches"]
        source_ids = set()
        for match in matches:
            source_ids.add(match["id"])
            source_ids.update(
                match["dataset"] + ":" + sid
                for sid in match["metadata"].get("context_source_ids", [])
            )
        expected = set(case["relevant_ids"])
        recalled = expected & source_ids
        rows.append(
            {
                "case": case["id"],
                "intent": case["intent"],
                "query": case["query"],
                "expected": sorted(expected),
                "returned": [r["id"] for r in matches],
                "source_recall@5": len(recalled) / len(expected),
                "citation_complete": all(bool(r["locator"]) for r in matches),
            }
        )
    return {
        "cases": rows,
        "mean_source_recall@5": float(np.mean([r["source_recall@5"] for r in rows])),
        "annotation_status": "CURATED_AGAINST_LOCAL_SOURCE_NOT_INDEPENDENT_EXPERT_REVIEW",
    }
