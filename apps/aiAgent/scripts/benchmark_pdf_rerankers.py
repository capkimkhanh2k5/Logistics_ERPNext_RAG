#!/usr/bin/env python3
"""Frozen Dev-only source/model ablations, followed by locked Test evaluation."""

import argparse
import copy
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.context import fit_rerank_context  # noqa: E402
from rag.data import digest, read, write_json  # noqa: E402
from rag.db import connect  # noqa: E402
from rag.embedding import CrossEncoder, Embedder  # noqa: E402
from rag.retrieval import Retriever  # noqa: E402
from scripts.run_retrieval_experiment import (  # noqa: E402
    CandidateCache,
    compute_metrics,
    paired_cluster_interval,
)
from scripts.tune_shared_retrieval import (  # noqa: E402
    load_partition,
    measure_latency,
    rank_scored_pool,
)

RUN = ROOT / "artifacts/experiments/run_pdf_graph_v4"
MODELS: dict[str, dict] = {
    "m3": {
        "reranker_model": "BAAI/bge-reranker-v2-m3",
        "reranker_revision": "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e",
        "reranker_backend": "cross_encoder",
        "reranker_batch_size": 4,
    },
    "qwen": {
        "reranker_model": "Qwen/Qwen3-Reranker-0.6B",
        "reranker_revision": "e61197ed45024b0ed8a2d74b80b4d909f1255473",
        "reranker_backend": "qwen",
        "reranker_batch_size": 8,
    },
    "gemma": {
        "reranker_model": "BAAI/bge-reranker-v2-gemma",
        "reranker_revision": "1787044f8b6fb740a9de4557c3a12377f84d9e17",
        "reranker_backend": "flag_llm",
        "reranker_batch_size": 4,
    },
}


def balanced(cases, count):
    return [
        c
        for section in sorted({c["section"] for c in cases})
        for c in sorted(
            (c for c in cases if c["section"] == section), key=lambda x: digest(x["record_id"])
        )[:count]
    ]


def candidate_cache(retriever, phase):
    bundle = read(ROOT / "artifacts/corpus.json")
    return CandidateCache(
        RUN / f"{phase}_source_pools.sqlite",
        {
            "snapshot": retriever.snapshot,
            "profile": retriever.profile,
            "records": bundle["manifest"]["records_hash"],
            "graph": bundle["manifest"]["edges_hash"],
            "source_policy": read(RUN / "protocol.json")["source_policy"],
            "representation": "pdf-deduplicated-v4",
            "phase": phase,
        },
    )


def prepare(retriever, cases, phase):
    cache = candidate_cache(retriever, phase)
    for i, case in enumerate(cases, 1):
        query = case["query"]
        for method in ("B1", "B2"):
            key = digest([query, method])
            if cache.get(key) is not None:
                continue
            base = retriever.search(
                query,
                mode="full_hybrid",
                top_k=100,
                levels=[8],
                expand=False,
                weights=retriever.product_policy["weights"],
                rrf_k=60,
            )["candidates"]
            cache.put(key, retriever.prepare_product_candidates(query, base, method))
        if i % 25 == 0 or i == len(cases):
            print(f"{phase} source pools {i}/{len(cases)}", flush=True)
    cache.close()


def model(key):
    cfg = MODELS[key]
    return CrossEncoder(
        cfg["reranker_model"],
        cfg["reranker_revision"],
        "mps" if torch.backends.mps.is_available() else "cpu",
        cfg["reranker_backend"],
        cfg["reranker_batch_size"],
    )


def fitted(retriever, reranker, rows, query, style, pool):
    rows = retriever.graph_context().format_candidates(rows[:pool], style)
    return fit_rerank_context(
        query, rows, reranker.model.tokenizer, 1152 if reranker.backend == "cross_encoder" else 1000
    )


def compact_prediction(result):
    return {
        **result,
        "ranked": [
            {
                **{
                    k: row[k]
                    for k in ("id", "code", "level", "rrf_score", "rerank_score")
                    if k in row
                },
                "model_input_text_hash": digest(row["rerank_text"]),
                "used_citation_ids": [
                    c["id"] for c in [*row["hierarchy_citations"], *row["note_citations"]]
                ],
                "rerank_omitted_ids": row.get("rerank_omitted_ids", []),
            }
            for row in result["ranked"]
        ],
    }


def gate(retriever, cases):
    cache = candidate_cache(retriever, "dev")
    samples = balanced(cases, 2)
    results: dict[str, dict] = {}
    sample_quality: dict[str, dict] = {}
    for name in MODELS:
        r = model(name)
        results[name] = {}
        sample_quality[name] = {}
        for pool in (40, 60):
            timings: list[float] = []
            predictions = {}
            for case in samples:
                rows = cache.get(digest([case["query"], "B1"]))
                if rows is None:
                    raise ValueError("Prepare Dev source pools before the model gate")
                source_rows = rows
                rows = fitted(retriever, r, rows, case["query"], "structured", pool)
                # Warm the model once; subsequent timings always bypass per-query/model caches.
                if not timings:
                    r.score(case["query"], [x["rerank_text"] for x in rows[:2]], use_cache=False)
                t = time.perf_counter()
                values = r.score(case["query"], [x["rerank_text"] for x in rows], use_cache=False)
                timings.append((time.perf_counter() - t) * 1000)
                scored = [{**x, "rerank_score": v} for x, v in zip(rows, values, strict=True)]
                policy = {**retriever.product_policy, "rerank_pool": pool, "rank_weight": 0.85}
                predictions[case["record_id"]] = rank_scored_pool(
                    scored + source_rows[pool:], policy
                )
                print(f"gate {name} pool {pool}: {timings[-1]:.0f} ms", flush=True)
            results[name][str(pool)] = {
                "count": len(timings),
                "latency_ms": timings,
                "p95_ms": float(np.percentile(timings, 95)),
                "eligible": float(np.percentile(timings, 95)) <= 3000,
            }
            write_json(RUN / "model_gate.json", results)
            sample_quality[name][str(pool)] = compute_metrics(samples, predictions, pool)
            write_json(
                RUN / "model_gate_sample_quality.json",
                {
                    "scope": "SIX_DEV_QUERIES_ONLY_NOT_A_FULL_MODEL_ACCURACY_COMPARISON",
                    "method": "B1",
                    "style": "structured",
                    "rank_weight": 0.85,
                    "results": sample_quality,
                },
            )
        del r
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    cache.close()
    return results


def method_gate(retriever, cases):
    """Screen actual context lengths using the same frozen latency requirement."""
    gates = read(RUN / "model_gate.json")
    eligible = [k for k, v in gates.items() if any(x["eligible"] for x in v.values())]
    cache = candidate_cache(retriever, "dev")
    results: dict[str, dict] = {}
    for name in eligible:
        r = model(name)
        for method in ("B1", "B2"):
            results[method] = {}
            for style in ("plain", "structured"):
                results[method][style] = {}
                for pool in (40, 60):
                    timings: list[float] = []
                    for case in balanced(cases, 2):
                        rows = cache.get(digest([case["query"], method]))
                        if rows is None:
                            raise ValueError("Prepare Dev source pools before the method gate")
                        fit = fitted(retriever, r, rows, case["query"], style, pool)
                        if not timings:
                            r.score(
                                case["query"], [x["rerank_text"] for x in fit[:2]], use_cache=False
                            )
                        t = time.perf_counter()
                        r.score(case["query"], [x["rerank_text"] for x in fit], use_cache=False)
                        timings.append((time.perf_counter() - t) * 1000)
                    p95 = float(np.percentile(timings, 95))
                    results[method][style][str(pool)] = {
                        "count": len(timings),
                        "latency_ms": timings,
                        "p95_ms": p95,
                        "eligible": p95 <= 3000,
                    }
                    print(
                        f"method gate {name} {method} {style} {pool}: p95 {p95:.0f} ms", flush=True
                    )
                    write_json(RUN / f"method_latency_gate_{name}.json", results)
        del r
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    cache.close()


def configuration_eligible(name, method, style, pool):
    model_gate_result = read(RUN / "model_gate.json")
    path = RUN / f"method_latency_gate_{name}.json"
    if not path.exists():
        return False
    return (
        model_gate_result[name][str(pool)]["eligible"]
        and read(path)[method][style][str(pool)]["eligible"]
    )


def score(retriever, cases, phase, models, methods):
    cache = candidate_cache(retriever, phase)
    protocol = read(RUN / "protocol.json")
    identity = {
        "snapshot": retriever.snapshot,
        "protocol_hash": digest(protocol),
        "models": models,
        "methods": methods,
        "code_hashes": {
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in protocol["code_hashes"]
        },
    }
    identity_path = RUN / f"{phase}_score_identity.json"
    if identity_path.exists() and read(identity_path) != identity:
        raise ValueError("Scoring cache identity mismatch; refuse stale scores")
    write_json(identity_path, identity)
    baseline = read(RUN / "protocol.json")["source_policy"]
    predictions: dict[str, dict] = {}
    policies = {}
    for name in models:
        r = model(name)
        for style in ("plain", "structured"):
            target = RUN / f"{phase}_{name}_{style}_scores.json"
            saved = read(target) if target.exists() else {}
            for method in methods:
                for pool in (40, 60):
                    eligible_pool = configuration_eligible(name, method, style, pool)
                    reference_pool = (name, method, style, pool) == ("m3", "B1", "plain", 60)
                    if not eligible_pool and not reference_pool:
                        continue
                    for rank in (0.85, 1.0):
                        if not eligible_pool and rank != 0.85:
                            continue
                        key = f"{method}_{name}_{style}_{pool}_{rank}"
                        policies[key] = {
                            **copy.deepcopy(baseline),
                            **MODELS[name],
                            "context_format": style,
                            "rerank_pool": pool,
                            "rank_weight": rank,
                            "default_method": method,
                        }
                        predictions[key] = {}
            active_methods = {
                p["default_method"]: max(
                    x["rerank_pool"]
                    for x in policies.values()
                    if x["reranker_model"] == r.model_id
                    and x["context_format"] == style
                    and x["default_method"] == p["default_method"]
                )
                for p in policies.values()
                if p["reranker_model"] == r.model_id and p["context_format"] == style
            }
            if not active_methods:
                continue
            # Length-sort independent pairs together for efficient offline scoring.
            # Serving latency is measured separately using one query at a time.
            for start in range(0, len(cases), 20):
                requests, entries = [], []
                for case in cases[start : start + 20]:
                    for method, max_pool in active_methods.items():
                        key = digest([case["record_id"], method])
                        if key in saved:
                            continue
                        rows = cache.get(digest([case["query"], method]))
                        if rows is None:
                            raise ValueError("Missing frozen source pool")
                        fit = fitted(retriever, r, rows, case["query"], style, max_pool)
                        requests.append((case["query"], [x["rerank_text"] for x in fit]))
                        entries.append((key, fit))
                values = r.score_many(requests)
                for (key, fit), scores in zip(entries, values, strict=True):
                    saved[key] = {x["id"]: v for x, v in zip(fit, scores, strict=True)}
                write_json(target, saved)
                print(
                    f"{phase} {name} {style} bulk {min(start + 20, len(cases))}/{len(cases)}",
                    flush=True,
                )
            for i, case in enumerate(cases, 1):
                query, rid = case["query"], case["record_id"]
                for method, max_pool in active_methods.items():
                    rows = cache.get(digest([query, method]))
                    if rows is None:
                        raise ValueError("Missing frozen source pool")
                    score_key = digest([rid, method])
                    if score_key not in saved:
                        fit = fitted(retriever, r, rows, query, style, max_pool)
                        values = r.score(query, [x["rerank_text"] for x in fit])
                        saved[score_key] = {x["id"]: v for x, v in zip(fit, values, strict=True)}
                    actual_inputs = fitted(retriever, r, rows, query, style, max_pool)
                    scored = [
                        {**x, "rerank_score": saved[score_key][x["id"]]} for x in actual_inputs
                    ] + rows[max_pool:]
                    for key, policy in policies.items():
                        if (
                            policy["reranker_model"] == r.model_id
                            and policy["context_format"] == style
                            and policy["default_method"] == method
                        ):
                            predictions[key][rid] = compact_prediction(
                                rank_scored_pool(scored, policy)
                            )
                if i % 20 == 0 or i == len(cases):
                    write_json(target, saved)
                    print(f"{phase} {name} {style} {i}/{len(cases)}", flush=True)
            for key, prediction in predictions.items():
                if (
                    policies[key]["reranker_model"] == r.model_id
                    and policies[key]["context_format"] == style
                ):
                    write_json(
                        RUN / f"{phase}_{key}_metrics.json",
                        compute_metrics(cases, prediction, policies[key]["rerank_pool"]),
                    )
                    write_json(RUN / f"{phase}_{key}_predictions.json", prediction)
        del r
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    cache.close()
    write_json(RUN / f"{phase}_policies.json", policies)
    return predictions, policies


def select(retriever, cases, manifest):
    protocol = read(RUN / "protocol.json")
    identity = read(RUN / "dev_score_identity.json")
    if identity["snapshot"] != retriever.snapshot or identity["protocol_hash"] != digest(protocol):
        raise ValueError("Selection does not match frozen Dev score identity")
    policies = read(RUN / "dev_policies.json")
    results = {name: read(RUN / f"dev_{name}_metrics.json") for name in policies}
    if any(m["ALL"]["count"] != len(cases) for m in results.values()):
        raise ValueError("Incomplete Dev evaluation")
    baseline = results["B1_m3_plain_60_0.85"]
    eligible = [
        name
        for name, m in results.items()
        if configuration_eligible(
            name.split("_")[1],
            policies[name]["default_method"],
            policies[name]["context_format"],
            policies[name]["rerank_pool"],
        )
        and all(
            m["sections"][s]["recall@5"] >= baseline["sections"][s]["recall@5"] - 0.02
            for s in baseline["sections"]
        )
    ]
    eligible.sort(
        key=lambda name: (-results[name]["MACRO"]["mrr@10"], policies[name]["rerank_pool"], name)
    )
    latencies = {}
    chosen = None
    for name in eligible:
        print(f"Full Dev runtime latency check {name}", flush=True)
        latencies[name] = measure_latency(retriever, cases, policies[name])
        write_json(RUN / "dev_runtime_latencies.json", latencies)
        if latencies[name]["p95_ms"] <= 3000:
            chosen = name
            break
    if chosen is None:
        raise ValueError("No tested shared policy satisfies the frozen recall/latency requirements")
    policy = {
        **policies[chosen],
        "version": "pdf-source-graph-v4-dev-selected",
        "selection_scope": f"ONE_SHARED_POLICY_SELECTED_ON_{len(cases)}_DEV_CASES_TEST_NOT_USED",
    }
    predictions = read(RUN / f"dev_{chosen}_predictions.json")
    selection = {
        "chosen": chosen,
        "policy": policy,
        "snapshot": retriever.snapshot,
        "profile": retriever.profile,
        "protocol_hash": digest(protocol),
        "manifest_hash": digest(manifest),
        "dev_metrics": results[chosen],
        "latency": latencies[chosen],
        "code_hashes": identity["code_hashes"],
        "method_gate_hashes": {
            path.name: digest(read(path)) for path in RUN.glob("method_latency_gate_*.json")
        },
        "model_gate_hash": digest(read(RUN / "model_gate.json")),
        "dev_fold_metrics": {
            str(i): compute_metrics(
                [c for c in cases if c["dev_fold"] == i], predictions, policy["rerank_pool"]
            )
            for i in range(5)
        },
    }
    write_json(RUN / "locked_policy.json", selection)
    write_json(ROOT / "config/hybrid_retrieval.json", policy)
    metadata = read(ROOT / "config/selected_retrieval.json")
    metadata["hs_shared_policy"] = policy
    metadata["hs_shared_selection"] = {
        "configuration": chosen,
        "run_id": RUN.name,
        "policy_hash": digest(policy),
    }
    write_json(ROOT / "config/selected_retrieval.json", metadata)
    write_json(RUN / "dev_comparison.json", results)
    print(
        json.dumps(
            {
                "chosen": chosen,
                "macro": results[chosen]["MACRO"],
                "latency": latencies[chosen]["p95_ms"],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


def chapter_diagnostic(cases):
    """Exclude one Chapter's questions and related groups during Dev selection."""
    policies = read(RUN / "dev_policies.json")
    predictions = {k: read(RUN / f"dev_{k}_predictions.json") for k in policies}
    baseline_name = "B1_m3_plain_60_0.85"
    results, combined = {}, {}
    for chapter in sorted({c["expected_hs_8"][:2] for c in cases}):
        held = [c for c in cases if c["expected_hs_8"].startswith(chapter)]
        held_groups = {c["eval_group_id"] for c in held}
        development = [c for c in cases if c["eval_group_id"] not in held_groups]
        summaries = {
            k: compute_metrics(development, predictions[k], p["rerank_pool"])
            for k, p in policies.items()
        }
        baseline = summaries[baseline_name]
        eligible = [
            k
            for k, p in policies.items()
            if configuration_eligible(
                k.split("_")[1], p["default_method"], p["context_format"], p["rerank_pool"]
            )
            and all(
                summaries[k]["sections"][s]["recall@5"] >= m["recall@5"] - 0.02
                for s, m in baseline["sections"].items()
            )
        ]
        if not eligible:
            raise ValueError(f"No eligible Dev configuration for Chapter {chapter}")
        chosen = min(
            eligible,
            key=lambda k: (-summaries[k]["MACRO"]["mrr@10"], policies[k]["rerank_pool"], k),
        )
        for c in held:
            combined[c["record_id"]] = predictions[chosen][c["record_id"]]
        results[chapter] = {
            "selected": chosen,
            "selection_queries": len(development),
            "held_queries": len(held),
            "held_groups": len(held_groups),
            "related_queries_excluded": len(cases) - len(development) - len(held),
            "held_metrics": compute_metrics(
                held, predictions[chosen], policies[chosen]["rerank_pool"]
            ),
        }
    write_json(
        RUN / "leave_one_chapter_out_dev.json",
        {
            "scope": "DEV_ONLY_CONFIGURATION_TRANSFER_DIAGNOSTIC_EXISTING_INDEXED_CHAPTERS_PREVIOUSLY_SEEN_QUERIES",
            "latency_scope": "NECESSARY_SIX_QUERY_MODEL_METHOD_GATE_ONLY_NOT_ALL_CONFIGURATIONS_HAVE_FULL_RUNTIME_LATENCY",
            "source_corpus": "FULL_REGISTERED_CORPUS_CHAPTER_NOT_REMOVED_FROM_SOURCE_INDEX",
            "chapters": results,
            "overall": compute_metrics(cases, combined, 100),
            "note": "Overall cand@rerank_pool is not applicable with varying selected pools; do not report it.",
        },
    )


def main():
    global MODELS, RUN
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase",
        choices=[
            "protocol",
            "prepare",
            "gate",
            "method-gate",
            "score",
            "chapter-diagnostic",
            "select",
            "test",
        ],
    )
    parser.add_argument("--run-id", default=RUN.name)
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or args.run_id in {".", ".."}:
        raise ValueError("Run ID must be a directory name")
    RUN = ROOT / "artifacts/experiments" / args.run_id
    if args.phase != "protocol":
        frozen = read(RUN / "protocol.json")
        MODELS = frozen["models"]
        for path, value in frozen["code_hashes"].items():
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != value:
                raise ValueError(f"Frozen runtime code changed: {path}")
        for path, value in frozen["source_hashes"].items():
            if hashlib.sha256((ROOT / "data/normalized" / path).read_bytes()).hexdigest() != value:
                raise ValueError(f"Frozen source changed: {path}")
    torch.set_num_threads(4)
    manifest = read(ROOT / "data/verified/hs/manifest.json")
    if args.phase == "protocol":
        corpus = read(ROOT / "artifacts/corpus.json")
        source_manifest = read(ROOT / "config/source_manifest.json")
        core_files = (
            "rag/embedding.py",
            "rag/retrieval.py",
            "rag/context.py",
            "rag/data.py",
            "rag/pdf_graph.py",
            "config/rag.yaml",
        )
        existing_path = RUN / "protocol.json"
        if existing_path.exists():
            existing = read(existing_path)
            if (
                existing["snapshot"] != corpus["snapshot"]
                or existing["dev_sha256"] != manifest["files"]["dev"]["sha256"]
                or existing["test_sha256"] != manifest["files"]["test"]["sha256"]
                or any(
                    hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != value
                    for path, value in existing["code_hashes"].items()
                )
            ):
                raise ValueError("Frozen inputs changed; use a new --run-id")
            print("Reusing the existing frozen protocol; no overwrite", flush=True)
            return
        write_json(
            RUN / "protocol.json",
            {
                "source_policy": read(ROOT / "config/hybrid_retrieval.json"),
                "models": MODELS,
                "snapshot": corpus["snapshot"],
                "source_hashes": {
                    relative: hashlib.sha256(
                        (ROOT / "data/normalized" / relative).read_bytes()
                    ).hexdigest()
                    for relative in source_manifest["files"].values()
                },
                "code_hashes": {
                    path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                    for path in core_files
                },
                "dev_sha256": manifest["files"]["dev"]["sha256"],
                "test_sha256": manifest["files"]["test"]["sha256"],
                "objective": "Macro MRR@10; Recall@5 no Section loses >2 percentage points vs corrected-source m3/plain; 3000 ms p95 warm-model cold-query latency",
                "latency_gate": "6 Dev queries balanced 2 per Section, rerank-only necessary gate; final 30-query full runtime check before selection",
                "grid": {
                    "formats": ["plain", "structured"],
                    "pools": [40, 60],
                    "ranks": [0.85, 1.0],
                    "methods": ["B1", "B2"],
                },
                "test_role": "Previously seen regression; never used for configuration selection",
                "offline_scoring": "Batch independent pairs across 20 Dev queries; serving latency measured single query with caches bypassed.",
            },
        )
        return
    cases = load_partition("dev", manifest)
    if args.phase == "chapter-diagnostic":
        chapter_diagnostic(cases)
        return
    with connect() as conn:
        retriever = Retriever(conn, Embedder())
        retriever.product_policy = read(RUN / "protocol.json")["source_policy"]
        if args.phase == "prepare":
            prepare(retriever, cases, "dev")
        elif args.phase == "gate":
            gate(retriever, cases)
        elif args.phase == "method-gate":
            method_gate(retriever, cases)
        elif args.phase == "score":
            gates = read(RUN / "model_gate.json")
            eligible = [k for k, v in gates.items() if any(x["eligible"] for x in v.values())]
            if not eligible:
                raise ValueError("No model passes the latency screen")
            score(
                retriever, cases, "dev", ["m3", *[k for k in eligible if k != "m3"]], ["B1", "B2"]
            )
        elif args.phase == "select":
            select(retriever, cases, manifest)
        elif args.phase == "test":
            lock = read(RUN / "locked_policy.json")
            protocol = read(RUN / "protocol.json")
            if (
                lock["snapshot"] != retriever.snapshot
                or lock["protocol_hash"] != digest(protocol)
                or lock["manifest_hash"] != digest(manifest)
                or any(
                    hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h
                    for p, h in lock["code_hashes"].items()
                )
                or digest(read(RUN / "model_gate.json")) != lock["model_gate_hash"]
                or any(digest(read(RUN / p)) != h for p, h in lock["method_gate_hashes"].items())
            ):
                raise ValueError("Locked policy identity changed before Test")
            retriever.product_policy = lock["policy"]
            tests = load_partition("test", manifest)
            prediction_path = RUN / "test_predictions.json"
            prediction_identity = {
                "snapshot": retriever.snapshot,
                "profile": retriever.profile,
                "policy_hash": digest(lock["policy"]),
                "protocol_hash": lock["protocol_hash"],
                "manifest_hash": lock["manifest_hash"],
                "code_hashes": lock["code_hashes"],
            }
            identity_path = RUN / "test_prediction_identity.json"
            if identity_path.exists():
                if read(identity_path) != prediction_identity:
                    raise ValueError("Test checkpoint identity changed")
            elif prediction_path.exists():
                raise ValueError("Existing Test predictions lack a verified checkpoint identity")
            write_json(identity_path, prediction_identity)
            predictions = read(prediction_path) if prediction_path.exists() else {}
            predictions = {
                key: compact_prediction(value) if "rerank_text" in value["ranked"][0] else value
                for key, value in predictions.items()
            }
            for i, case in enumerate(tests, 1):
                if case["record_id"] in predictions:
                    continue
                result = retriever.adaptive_search(case["query"])
                predictions[case["record_id"]] = compact_prediction(
                    {
                        "ranked": result["candidates"][:10],
                        "pool_codes": [r["code"] for r in result["candidate_pool"]],
                        "latency_ms": result["timings"]["total_ms"],
                    }
                )
                if i % 20 == 0 or i == len(tests):
                    write_json(RUN / "test_predictions.json", predictions)
                    print(f"locked Test {i}/{len(tests)}", flush=True)
            write_json(
                RUN / "test_metrics.json",
                compute_metrics(tests, predictions, lock["policy"]["rerank_pool"]),
            )
            old = read(ROOT / "artifacts/experiments/run_shared_dev_v3/test_predictions.json")[
                "selected"
            ]
            write_json(
                RUN / "test_paired_interval.json",
                paired_cluster_interval(tests, {"rows": tests}, old, predictions),
            )


if __name__ == "__main__":
    main()
