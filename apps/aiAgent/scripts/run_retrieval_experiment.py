#!/usr/bin/env python3
"""Frozen shared-policy ablations B0/B1/B2; source evidence never reads gold labels."""

import argparse
import json
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from rag.data import ROOT, digest, load_corpus, read  # noqa: E402
from rag.db import connect  # noqa: E402
from rag.embedding import Embedder  # noqa: E402
from rag.evaluation import discover_gold, query_for  # noqa: E402
from rag.experiments import prepare_manifest  # noqa: E402
from rag.retrieval import Retriever  # noqa: E402

DEFAULT_RUN_ID = "run_generic_graph_v2"


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n")
    temporary.replace(path)


def serialize_candidate(row: dict) -> dict:
    fields = (
        "id",
        "code",
        "level",
        "section",
        "chapter",
        "heading",
        "source_text",
        "embedding_text",
        "locator",
        "score",
        "rrf_score",
        "rerank_score",
        "rerank_text",
        "context_chain",
        "intermediate_branches",
        "hierarchy_citations",
        "note_citations",
        "rerank_omitted_ids",
        "graph_context",
        "selection_channel",
    )
    return {k: row[k] for k in fields if k in row}


def cache_identity(retriever: Retriever, cases: list[dict]) -> dict:
    bundle = load_corpus()
    if bundle["snapshot"] != retriever.snapshot:
        raise ValueError("Corpus artifact and active database snapshot differ")
    code_files = [
        "rag/retrieval.py",
        "rag/context.py",
        "rag/sources.py",
        "rag/data.py",
        "rag/evaluation.py",
        "rag/experiments.py",
        "rag/db.py",
        "rag/embedding.py",
        "scripts/run_retrieval_experiment.py",
    ]
    return {
        "version": 2,
        "snapshot": retriever.snapshot,
        "profile": retriever.profile,
        "policy_hash": digest(retriever.product_policy),
        "retrieval_config_hash": digest(retriever.cfg),
        "query_hash": digest([(c["record_id"], c["query"]) for c in cases]),
        "gold_hash": digest([(c["record_id"], c["expected_hs_8"]) for c in cases]),
        "records_hash": bundle["manifest"]["records_hash"],
        "nodes_hash": digest(bundle["nodes"]),
        "edges_hash": digest(bundle["edges"]),
        "code_hash": digest({p: (ROOT / p).read_text() for p in code_files}),
    }


class CandidateCache:
    """Only raw shared retrieval pools are reusable; identity changes reject stale data."""

    def __init__(self, path: Path, metadata: dict) -> None:
        self.conn = sqlite3.connect(path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS metadata (identity TEXT NOT NULL)")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS pools (query TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        previous = self.conn.execute("SELECT identity FROM metadata").fetchone()
        identity = json.dumps(metadata, sort_keys=True)
        if previous is not None and previous[0] != identity:
            self.conn.close()
            raise ValueError("Candidate cache identity mismatch; use a new run ID")
        if previous is None:
            self.conn.execute("INSERT INTO metadata VALUES (?)", (identity,))
            self.conn.commit()

    def get(self, query: str) -> list[dict] | None:
        row = self.conn.execute("SELECT payload FROM pools WHERE query=?", (query,)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, query: str, rows: list[dict]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO pools VALUES (?,?)",
            (query, json.dumps([serialize_candidate(r) for r in rows], default=str)),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


def compute_metrics(cases: list[dict], predictions: dict[str, dict], pool_size: int) -> dict:
    sections, chapters = defaultdict(list), defaultdict(list)
    for case in cases:
        result = predictions.get(case["record_id"])
        if result is None:
            continue
        gold = case["expected_hs_8"]
        codes = [r["code"] for r in result["ranked"] if r.get("level") == 8]
        rank = codes.index(gold) + 1 if gold in codes else None
        item = {
            "hit@1": float(rank == 1),
            "recall@5": float(rank is not None and rank <= 5),
            "recall@10": float(rank is not None and rank <= 10),
            "mrr@10": 1 / rank if rank is not None and rank <= 10 else 0,
            "cand@100": float(gold in result["pool_codes"][:100]),
            "cand@rerank_pool": float(gold in result["pool_codes"][:pool_size]),
            "latency_ms": result["latency_ms"],
        }
        sections[case["section"]].append(item)
        chapters[gold[:2]].append(item)

    def summarize(items: list[dict]) -> dict:
        if not items:
            return {"count": 0}
        return {
            "count": len(items),
            **{k: float(np.mean([r[k] for r in items])) for k in items[0]},
            "p50_latency_ms": float(np.percentile([r["latency_ms"] for r in items], 50)),
            "p95_latency_ms": float(np.percentile([r["latency_ms"] for r in items], 95)),
        }

    per_section = {key: summarize(items) for key, items in sorted(sections.items())}
    macro = {
        k: float(np.mean([r[k] for r in per_section.values()]))
        for k in ("hit@1", "recall@5", "recall@10", "mrr@10", "cand@100", "cand@rerank_pool")
    }
    return {
        "ALL": summarize([r for items in sections.values() for r in items]),
        "MACRO": macro,
        "sections": per_section,
        "chapters": {k: summarize(v) for k, v in sorted(chapters.items())},
        "latency_scope": "REPLAY_WITH_RAW_POOL_AND_MODEL_CACHE_NOT_SERVING_SLA",
    }


def paired_cluster_interval(cases: list[dict], manifest: dict, a: dict, b: dict) -> dict:
    groups = {r["record_id"]: r["eval_group_id"] for r in manifest["rows"]}
    deltas = defaultdict(list)
    wins = losses = 0
    for c in cases:
        rid, gold = c["record_id"], c["expected_hs_8"]
        if rid not in a or rid not in b:
            continue

        def values(result):
            codes = [r["code"] for r in result["ranked"] if r.get("level") == 8]
            rank = codes.index(gold) + 1 if gold in codes else None
            return np.array(
                [
                    float(rank == 1),
                    float(rank is not None and rank <= 5),
                    float(rank is not None and rank <= 10),
                    1 / rank if rank and rank <= 10 else 0,
                ]
            )

        x, y = values(a[rid]), values(b[rid])
        wins += int(x[0] == 0 and y[0] == 1)
        losses += int(x[0] == 1 and y[0] == 0)
        deltas[groups[rid]].append(y - x)
    if not deltas:
        raise ValueError("No paired predictions to compare")
    sums = np.array([np.sum(v, axis=0) for v in deltas.values()])
    sizes = np.array([len(v) for v in deltas.values()])
    rng = np.random.default_rng(20261001)
    indices = rng.integers(0, len(sums), (2000, len(sums)))
    samples = sums[indices].sum(axis=1) / sizes[indices].sum(axis=1)[:, None]
    point = sums.sum(axis=0) / sizes.sum()
    return {
        "wins_top1": wins,
        "losses_top1": losses,
        "metrics": {
            name: {
                "micro_delta": float(point[i]),
                "ci95": np.percentile(samples[:, i], [2.5, 97.5]).tolist(),
            }
            for i, name in enumerate(("hit@1", "recall@5", "recall@10", "mrr@10"))
        },
        "groups": len(sums),
        "resamples": 2000,
        "estimand": "QUERY_WEIGHTED_DELTA_WITH_WHOLE_GROUP_RESAMPLING",
        "scope": "CONDITIONAL_REGRESSION_ON_PREVIOUSLY_SEEN_CASES",
    }


def load_cases() -> list[dict]:
    cases, _ = discover_gold(("train", "test", "holdout"))
    return [{**c, "query": query_for(c, "name_and_spec")} for c in cases]


def report(run_dir: Path, cases: list[dict], manifest: dict, methods: list[str]) -> None:
    results, metrics = {}, {}
    for method in methods:
        path = run_dir / f"{method}_predictions.json"
        if not path.exists():
            continue
        result = read(path)
        results[method] = result["predictions"]
        metrics[method] = compute_metrics(
            cases, result["predictions"], result["policy"]["rerank_pool"]
        )
        save_json(run_dir / f"{method}_metrics.json", metrics[method])
    lines = [
        "# Shared source-graph Retrieval v2",
        "",
        "Frozen shared configuration; no chapter-specific tuning or HS keyword injection.",
        "",
        "Existing queries are regression data, not a new blind holdout. Gold is used only for scoring.",
        "",
        "| Method | Count | Macro Hit@1 | Macro Recall@5 | Hit@1 | Recall@5 | Cand@pool | Cand@100 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method, m in metrics.items():
        a, macro = m["ALL"], m["MACRO"]
        lines.append(
            f"| {method} | {a['count']} | {macro['hit@1']:.1%} | {macro['recall@5']:.1%} | "
            f"{a['hit@1']:.1%} | {a['recall@5']:.1%} | {a['cand@rerank_pool']:.1%} | {a['cand@100']:.1%} |"
        )
    for method, m in metrics.items():
        lines += [
            "",
            f"## {method}: Sections",
            "",
            "| Section | Count | Hit@1 | Recall@5 | Recall@10 | MRR@10 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for section, r in m["sections"].items():
            lines.append(
                f"| {section} | {r['count']} | {r['hit@1']:.1%} | {r['recall@5']:.1%} | {r['recall@10']:.1%} | {r['mrr@10']:.3f} |"
            )
    if "B0" in results and "B2" in results:
        paired = paired_cluster_interval(cases, manifest, results["B0"], results["B2"])
        save_json(run_dir / "paired_B0_B2.json", paired)
        lines += ["", "## Paired Top-1 comparison B0 → B2", "", json.dumps(paired, indent=2)]
    lines += [
        "",
        "B0: source hierarchy + shared hybrid/reranker. B1: adds graph context retrieval. B2: adds retrieved scoped Notes.",
        "",
        "A chapter receives the same policy even when it has no evaluation queries. Chapter metrics are descriptive; no chapter-specific configuration was fitted.",
        "",
        "Replay latency includes cache effects. Use measure_fresh_runtime_latency.py for serving measurements.",
    ]
    (run_dir / "GENERIC_RETRIEVAL_REPORT.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "report"])
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--method", choices=["B0", "B1", "B2", "ALL"], default="ALL")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run_dir = ROOT / "artifacts/experiments" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    manifest_path = run_dir / "manifest.json"
    manifest = read(manifest_path) if manifest_path.exists() else prepare_manifest(args.run_id)
    canonical_cases, _ = discover_gold(("train", "test", "holdout"))
    if manifest["dataset_hash"] != digest(canonical_cases):
        raise ValueError("Frozen evaluation dataset has changed")
    if {r["record_id"] for r in manifest["rows"]} != {c["record_id"] for c in cases}:
        raise ValueError("Evaluation manifest and current cases differ")
    if args.limit:
        cases = cases[: args.limit]
    methods = ["B0", "B1", "B2"] if args.method == "ALL" else [args.method]
    if args.command == "prepare":
        print(json.dumps({"cases": len(cases), "groups": manifest["total_groups"]}))
        return
    if args.command == "report":
        report(run_dir, cases, manifest, methods)
        return
    embedder = Embedder()
    with connect() as conn:
        retriever = Retriever(conn, embedder)
        identity = cache_identity(retriever, cases)
        cache = CandidateCache(run_dir / "raw_pools.sqlite", identity)
        results = {}
        for method in methods:
            path = run_dir / f"{method}_predictions.json"
            existing = read(path) if path.exists() else None
            if existing and not args.resume:
                raise ValueError("Predictions already exist; resume explicitly or use a new run ID")
            if existing and existing["identity"] != identity:
                raise ValueError("Prediction identity mismatch")
            results[method] = existing["predictions"] if existing else {}
        save_json(
            run_dir / "frozen_protocol.json",
            {
                "identity": identity,
                "policy": retriever.product_policy,
                "methods": methods,
                "selection": "FIXED_BEFORE_RUN_NO_TUNING",
            },
        )
        try:
            for i, case in enumerate(cases, 1):
                rid, query = case["record_id"], case["query"]
                if all(rid in results[m] for m in methods):
                    continue
                raw = cache.get(query)
                hit = raw is not None
                if raw is None:
                    raw = retriever.search(
                        query,
                        mode="full_hybrid",
                        levels=[8],
                        top_k=100,
                        expand=False,
                        weights=retriever.product_policy["weights"],
                        rrf_k=retriever.product_policy["rrf_k"],
                    )["candidates"]
                    cache.put(query, raw)
                for method in methods:
                    if rid in results[method]:
                        continue
                    start = time.perf_counter()
                    pool = retriever.prepare_product_candidates(query, raw, method)
                    ranked = retriever.rank_product_candidates(query, pool)[:10]
                    results[method][rid] = {
                        "ranked": [serialize_candidate(r) for r in ranked],
                        "pool_codes": [r["code"] for r in pool],
                        "latency_ms": (time.perf_counter() - start) * 1000,
                        "raw_pool_cache_hit": hit,
                    }
                if i % 20 == 0 or i == len(cases):
                    for method in methods:
                        save_json(
                            run_dir / f"{method}_predictions.json",
                            {
                                "identity": identity,
                                "policy": retriever.product_policy,
                                "predictions": results[method],
                            },
                        )
                    print(f"Completed {i}/{len(cases)} queries: {', '.join(methods)}", flush=True)
        finally:
            for method in methods:
                save_json(
                    run_dir / f"{method}_predictions.json",
                    {
                        "identity": identity,
                        "policy": retriever.product_policy,
                        "predictions": results[method],
                    },
                )
            cache.close()
        report(run_dir, cases, manifest, methods)


if __name__ == "__main__":
    main()
