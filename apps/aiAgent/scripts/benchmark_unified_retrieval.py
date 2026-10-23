#!/usr/bin/env python3
"""Dev-only accuracy selection for a common HS/Legal retrieval flow."""

import argparse
import ast
import gc
import hashlib
import itertools
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.retrieval import (  # noqa: E402
    INSTRUCTION,
    MODELS,
    WEIGHTS,
    retrieval_config,  # noqa: E402
)
from rag.embedding.bge_m3 import Embedder  # noqa: E402
from rag.retrieval.retriever import Retriever  # noqa: E402
from rag.retrieval.unified import (  # noqa: E402
    UnifiedRetrieval,
    fit_inputs,
    hs_projection,
    make_encoder,
    rank_scores,
)
from rag.utils.files import digest, read, write_json  # noqa: E402
from rag.vectordb.postgres import connect  # noqa: E402
from tests.support.evaluation import discover_qa, qa_direct_coverage  # noqa: E402

RUN = ROOT / "artifacts/experiments/run_unified_accuracy_v5"
BASE = {
    "version": "unified-source-v5",
    "candidate_pool": 160,
    "rrf_k": 60,
    "weights_name": "balanced",
    "channel_weights": {
        "direct": 0.65,
        "context_lex": 0.125,
        "context_dense": 0.125,
        "neighbors": 0.10,
    },
    "method": "B1",
    "context_format": "plain",
    "model": "m3",
    "rerank_pool": 100,
    "rank_weight": 1.0,
    "cascade_pool": 40,
    "cascade_weight": 1.0,
}


def cases(split):
    # The corpus is the active frozen source artifact, not a fresh source rebuild.
    bundle = read(ROOT / "artifacts/corpus.json")
    hs = read(ROOT / f"data/verified/hs/HS_RAG_{split.upper()}.jsonl")
    qa = discover_qa(bundle, split)
    return [{**c, "uid": "hs:" + c["record_id"], "task": "hs"} for c in hs] + [
        {**c, "uid": "qa:" + c["id"], "task": "qa"} for c in qa
    ]


def screen(rows):
    # Whole Dev groups, stratified by HS Section and QA category. Gold is unused.
    groups = defaultdict(list)
    for c in rows:
        groups[(c["task"], c["eval_group_id"])].append(c)
    strata = defaultdict(list)
    for key, items in groups.items():
        strata[items[0]["section"] if key[0] == "hs" else "QA"].append((key, items))
    result = []
    for stratum, items in sorted(strata.items()):
        target = 30 if stratum == "QA" else 10
        items.sort(key=lambda x: digest([20261002, x[0]]))
        chosen = []
        if stratum == "QA":
            by_category = defaultdict(list)
            for item in items:
                by_category[item[1][0]["category"]].append(item)
            while len(chosen) < target and any(by_category.values()):
                for category in sorted(by_category):
                    if by_category[category] and len(chosen) < target:
                        chosen.append(by_category[category].pop(0))
        else:
            chosen = items[:target]
        result.extend(c for _, batch in chosen for c in batch)
    return result


def protocol():
    RUN.mkdir(parents=True, exist_ok=True)
    target = RUN / "protocol.json"
    if target.exists():
        p = read(target)
        for name, value in p["data_hashes"].items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != value:
                raise ValueError("Frozen data changed")
        return p
    rows = cases("dev")
    p = {
        "base": BASE,
        "models": MODELS,
        "instruction": INSTRUCTION,
        "selection": "DEV_ONLY_NO_LATENCY_GATE",
        "objective": "mean(HS macro MRR@10, QA strict all_groups@10)",
        "screen_ids": [c["uid"] for c in screen(rows)],
        "grid": {
            "method": ["B1", "B2"],
            "weights_name": ["balanced", "lexical"],
            "rerank_pool": [60, 100],
            "rank_weight": [0.85, 1.0],
            "cascade_pool": [20, 40],
            "cascade_weight": [0.5, 1.0],
        },
        "finalist_rule": "Best two single models on balanced Dev screen; M3 and M3->Qwen cascade also evaluated on full Dev. Use each model's best screen method/weights; vary rank/pool on full Dev.",
        "baseline": {
            name: read(ROOT / f"config/{name}.json")
            for name in ("hybrid_retrieval", "selected_retrieval")
        },
        "data_hashes": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ROOT / "data/verified").glob("*/*.jsonl")
        },
    }
    with connect() as conn:
        p.update(conn.execute("SELECT snapshot,profile FROM rag.active").fetchone())
    write_json(target, p)
    return p


class PoolStore:
    def __init__(self, split):
        self.db = sqlite3.connect(RUN / f"{split}_pools.sqlite")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS pools (key TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )

    def get(self, key):
        row = self.db.execute("SELECT payload FROM pools WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, key, value):
        self.db.execute(
            "INSERT OR REPLACE INTO pools VALUES (?,?)",
            (key, json.dumps(value, ensure_ascii=False, default=str)),
        )
        self.db.commit()


def pool_key(case, policy):
    return digest([case["query"], policy["weights_name"], policy["method"]])


def compact(rows):
    keep = {
        "id",
        "code",
        "level",
        "section",
        "chapter",
        "heading",
        "source_text",
        "embedding_text",
        "dataset",
        "locator",
        "score",
        "chunk_type",
        "rrf_score",
        "rerank_text",
        "hierarchy_citations",
        "note_citations",
        "context_format",
        "graph_context",
        "selection_channel",
        "rerank_omitted_ids",
        "leaf_text",
    }
    return [{**{k: v for k, v in row.items() if k in keep}, "metadata": {}} for row in rows]


def prepare(split):
    p = protocol()
    rows = cases(split)
    store = PoolStore(split)
    embedder = Embedder()
    with connect() as conn:
        r = Retriever(conn, embedder, load_unified_policy=False)
        if r.snapshot != p["snapshot"] or r.profile != p["profile"]:
            raise ValueError("Source binding changed")
        u = UnifiedRetrieval(r, BASE)
        for i, case in enumerate(rows, 1):
            for weights in ("balanced", "lexical"):
                policy = {**BASE, "weights_name": weights}
                if all(
                    store.get(pool_key(case, {**policy, "method": method}))
                    for method in ("B1", "B2")
                ):
                    continue
                u.policy = policy
                channels = u.channels(case["query"])
                for method in ("B1", "B2"):
                    store.put(
                        pool_key(case, {**policy, "method": method}),
                        compact(u.prepare(case["query"], channels, {**policy, "method": method})),
                    )
            if i % 20 == 0 or i == len(rows):
                print(f"prepare {split} {i}/{len(rows)}", flush=True)
    store.db.close()


def metrics(rows, predictions):
    hs_sections, qa_rows, detail = defaultdict(list), [], []
    for c in rows:
        ranked = predictions[c["uid"]]
        if c["task"] == "hs":
            codes = [r["code"] for r in hs_projection(ranked)]
            gold = c["expected_hs_8"]
            rank = codes.index(gold) + 1 if gold in codes else 0
            mixed = next(
                (
                    i
                    for i, r in enumerate(ranked, 1)
                    if r.get("code") == gold
                    and r.get("level") == 8
                    and r.get("chunk_type") == "tariff_entry"
                ),
                0,
            )
            item = {
                "hit@1": int(rank == 1),
                "recall@5": int(0 < rank <= 5),
                "recall@10": int(rank > 0),
                "mrr@10": 1 / rank if rank else 0,
                "mixed_hit@1": int(mixed == 1),
                "mixed_recall@10": int(0 < mixed <= 10),
            }
            hs_sections[c["section"]].append(item)
        else:
            direct = qa_direct_coverage(c, ranked[:10])
            item = {
                k: float(direct[k])
                for k in ("all_groups@5", "all_groups@10", "group_recall@10", "mrr@10")
            }
            qa_rows.append(item)
        detail.append(
            {
                "uid": c["uid"],
                "group": c["task"] + ":" + c["eval_group_id"],
                "task": c["task"],
                "section": c.get("section"),
                **item,
                "returned": [r["id"] for r in ranked[:10]],
                "hs_codes": [r["code"] for r in hs_projection(ranked)],
            }
        )

    def mean(items):
        return {"count": len(items), **{k: float(np.mean([r[k] for r in items])) for k in items[0]}}

    hs = {s: mean(v) for s, v in sorted(hs_sections.items())}
    macro = {
        k: float(np.mean([v[k] for v in hs.values()]))
        for k in next(iter(hs.values()))
        if k != "count"
    }
    qa = mean(qa_rows)
    return {
        "objective": (macro["mrr@10"] + qa["all_groups@10"]) / 2,
        "HS": mean([x for v in hs_sections.values() for x in v]),
        "sections": hs,
        "HS_MACRO": macro,
        "QA": qa,
        "rows": detail,
    }


def score(model, phase):
    p = protocol()
    rows = cases("dev")
    if phase == "screen":
        rows = [c for c in rows if c["uid"] in p["screen_ids"]]
        variants = list(itertools.product(("balanced", "lexical"), ("B1", "B2")))
    else:
        selection = read(RUN / "screen_selection.json")
        variants = [tuple(selection["variants"][model])]
    store, encoder = PoolStore("dev"), make_encoder(model)
    target = RUN / f"{phase}_{model}_scores.json"
    identity_path = target.with_suffix(".identity.json")
    identity = {
        "model": MODELS[model],
        "snapshot": p["snapshot"],
        "profile": p["profile"],
        "max_length": 2048,
        "instruction": INSTRUCTION if model == "qwen" else None,
    }
    if identity_path.exists() and read(identity_path) != identity:
        raise ValueError("Score artifact has a different model/input setup; use a new run")
    write_json(identity_path, identity)
    scores = read(target) if target.exists() else {}
    for start in range(0, len(rows), 5):
        requests, pending = [], []
        for case in rows[start : start + 5]:
            for weights, method in variants:
                policy = {**BASE, "weights_name": weights, "method": method}
                key = pool_key(case, policy)
                pool = store.get(key)
                if not pool:
                    raise ValueError("Missing source pool; run prepare first")
                inputs = fit_inputs(case["query"], pool[:100], encoder)
                hashes = {r["id"]: digest(r["rerank_text"]) for r in inputs}
                if key in scores:
                    if hashes != scores[key]["text_hashes"]:
                        raise ValueError("Scored source inputs changed; use a new run")
                    continue
                requests.append((case["query"], [r["rerank_text"] for r in inputs]))
                pending.append((key, inputs, hashes))
        values = encoder.score_many(requests)
        for (key, inputs, hashes), results in zip(pending, values, strict=True):
            scores[key] = {
                "scores": {r["id"]: v for r, v in zip(inputs, results, strict=True)},
                "text_hashes": hashes,
            }
        write_json(target, scores)
        print(f"score {phase} {model} {min(start + 5, len(rows))}/{len(rows)}", flush=True)
    store.db.close()
    del encoder
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def replay(rows, policy, scores, store):
    predictions = {}
    for c in rows:
        key = pool_key(c, policy)
        pool = store.get(key)[: policy["rerank_pool"]]
        values = scores[key]["scores"]
        predictions[c["uid"]] = rank_scores(
            pool, [values[r["id"]] for r in pool], policy["rank_weight"], policy["rrf_k"]
        )
    return predictions


def select_screen():
    p, store = protocol(), PoolStore("dev")
    rows = [c for c in cases("dev") if c["uid"] in p["screen_ids"]]
    results = []
    for model in MODELS:
        scores = read(RUN / f"screen_{model}_scores.json")
        for weights, method, pool, weight in itertools.product(
            ("balanced", "lexical"), ("B1", "B2"), (60, 100), (0.85, 1.0)
        ):
            policy = {
                **BASE,
                "model": model,
                "weights_name": weights,
                "method": method,
                "rerank_pool": pool,
                "rank_weight": weight,
            }
            result = metrics(rows, replay(rows, policy, scores, store))
            result.pop("rows")
            results.append({"policy": policy, "metrics": result})
    results.sort(
        key=lambda x: (
            -x["metrics"]["objective"],
            -x["metrics"]["QA"]["group_recall@10"],
            -x["metrics"]["HS_MACRO"]["recall@5"],
            x["policy"]["rerank_pool"],
        )
    )
    best = {}
    for row in results:
        best.setdefault(row["policy"]["model"], row)
    models = [
        x["policy"]["model"]
        for x in sorted(best.values(), key=lambda x: -x["metrics"]["objective"])[:2]
    ]
    if "m3" not in models:
        models.append("m3")
    write_json(
        RUN / "screen_selection.json",
        {
            "count": len(rows),
            "results": results,
            "full_models": models,
            "variants": {
                m: [r["policy"]["weights_name"], r["policy"]["method"]] for m, r in best.items()
            },
        },
    )
    print("Full Dev models", models, flush=True)
    store.db.close()


def intent():
    protocol()
    rows, embedder = cases("dev"), Embedder()
    vectors = np.stack([embedder.encode([c["query"]])["dense"][0] for c in rows])
    labels = np.array([int(c["task"] == "qa") for c in rows])
    folds = np.array([c["dev_fold"] for c in rows])
    groups = defaultdict(set)
    for c in rows:
        groups[c["task"] + ":" + c["eval_group_id"]].add(c["dev_fold"])
    if any(len(v) != 1 for v in groups.values()):
        raise ValueError("Intent Dev folds split a group")
    trials = []
    for strength in (0.01, 0.1, 1, 10):
        predictions = np.zeros(len(rows), dtype=int)
        probabilities = np.zeros(len(rows))
        for fold in range(5):
            model = LogisticRegression(
                C=strength, class_weight="balanced", random_state=20261002, max_iter=1000
            )
            model.fit(vectors[folds != fold], labels[folds != fold])
            predictions[folds == fold] = model.predict(vectors[folds == fold])
            probabilities[folds == fold] = model.predict_proba(vectors[folds == fold])[:, 1]
        trials.append(
            {
                "C": strength,
                "balanced_accuracy": balanced_accuracy_score(labels, predictions),
                "log_loss": log_loss(labels, probabilities),
                "confusion": confusion_matrix(labels, predictions).tolist(),
            }
        )
    best = max(trials, key=lambda r: (r["balanced_accuracy"], -r["log_loss"], -r["C"]))
    model = LogisticRegression(
        C=best["C"], class_weight="balanced", random_state=20261002, max_iter=1000
    ).fit(vectors, labels)
    write_json(
        RUN / "semantic_intent.json",
        {
            "profile": embedder.profile_id,
            "selection": "DEV_GROUP_FOLDS",
            "trials": trials,
            "C": best["C"],
            "coef": model.coef_[0].tolist(),
            "intercept": float(model.intercept_[0]),
            "classes": ["hs", "qa"],
            "used_for_retrieval": False,
        },
    )
    print("Intent OOF", best, flush=True)


def cascade():
    protocol()
    rows = cases("dev")
    selection = read(RUN / "screen_selection.json")
    weights, method = selection["variants"]["m3"]
    policy = {**BASE, "weights_name": weights, "method": method}
    first_scores = read(RUN / "full_m3_scores.json")
    store, encoder = PoolStore("dev"), make_encoder("qwen")
    target = RUN / "cascade_scores.json"
    scores = read(target) if target.exists() else {}
    for i, c in enumerate(rows, 1):
        key = pool_key(c, policy)
        if key not in scores:
            pool = store.get(key)[:100]
            values = first_scores[key]["scores"]
            selected = {}
            for size, weight in itertools.product((60, 100), (0.85, 1.0)):
                ranked = rank_scores(pool[:size], [values[r["id"]] for r in pool[:size]], weight)
                selected.update({r["id"]: r for r in ranked[:40]})
            inputs = fit_inputs(c["query"], list(selected.values()), encoder)
            values = encoder.score(c["query"], [r["rerank_text"] for r in inputs])
            scores[key] = {"scores": {r["id"]: s for r, s in zip(inputs, values, strict=True)}}
        if i % 5 == 0 or i == len(rows):
            write_json(target, scores)
            print(f"cascade Dev {i}/{len(rows)}", flush=True)
    store.db.close()


def select_full():
    p, store, rows = protocol(), PoolStore("dev"), cases("dev")
    frozen_config = p["baseline"]["selected_retrieval"]["retrieval"]
    if retrieval_config() != frozen_config:
        raise ValueError("Retrieval settings changed since frozen Dev protocol")
    selection = read(RUN / "screen_selection.json")
    results = []
    for model in selection["full_models"]:
        weights, method = selection["variants"][model]
        scores = read(RUN / f"full_{model}_scores.json")
        for pool, weight in itertools.product((60, 100), (0.85, 1.0)):
            policy = {
                **BASE,
                "weights_name": weights,
                "method": method,
                "model": model,
                "rerank_pool": pool,
                "rank_weight": weight,
            }
            result = metrics(rows, replay(rows, policy, scores, store))
            results.append({"policy": policy, "metrics": result})
    first_scores, second_scores = (
        read(RUN / "full_m3_scores.json"),
        read(RUN / "cascade_scores.json"),
    )
    weights, method = selection["variants"]["m3"]
    for pool, weight, shortlist, second_weight in itertools.product(
        (60, 100), (0.85, 1.0), (20, 40), (0.5, 1.0)
    ):
        policy = {
            **BASE,
            "weights_name": weights,
            "method": method,
            "model": "cascade",
            "rerank_pool": pool,
            "rank_weight": weight,
            "cascade_pool": shortlist,
            "cascade_weight": second_weight,
        }
        predictions = replay(rows, policy, first_scores, store)
        for c in rows:
            ranked = predictions[c["uid"]]
            inputs = ranked[:shortlist]
            values = second_scores[pool_key(c, policy)]["scores"]
            predictions[c["uid"]] = (
                rank_scores(inputs, [values[r["id"]] for r in inputs], second_weight)
                + ranked[shortlist:]
            )
        results.append({"policy": policy, "metrics": metrics(rows, predictions)})
    results.sort(
        key=lambda r: (
            -r["metrics"]["objective"],
            -r["metrics"]["QA"]["group_recall@10"],
            -r["metrics"]["HS_MACRO"]["recall@5"],
            r["policy"]["rerank_pool"],
        )
    )
    best = results[0]
    artifact = read(RUN / "semantic_intent.json")
    policy = {
        **best["policy"],
        "snapshot": p["snapshot"],
        "profile": p["profile"],
        "intent_artifact": "config/semantic_intent.json",
        "intent_hash": digest(artifact),
        "models": MODELS,
        "instruction": INSTRUCTION,
        "max_length": 2048,
        "weights": WEIGHTS[best["policy"]["weights_name"]],
        "retrieval_config": frozen_config,
    }
    write_json(RUN / "dev_selection.json", results)
    write_json(RUN / "locked_policy.json", policy)
    print("Selected", policy, flush=True)
    print("Dev metrics", {k: v for k, v in best["metrics"].items() if k != "rows"}, flush=True)
    store.db.close()


def activate():
    p, locked = protocol(), read(RUN / "locked_policy.json")
    if retrieval_config() != locked["retrieval_config"]:
        raise ValueError("Retrieval settings changed since Dev selection")
    with connect() as conn:
        active = conn.execute("SELECT snapshot,profile FROM rag.active").fetchone()
    if active != {"snapshot": p["snapshot"], "profile": p["profile"]}:
        raise ValueError("Source/profile changed since Dev selection")
    write_json(ROOT / locked["intent_artifact"], read(RUN / "semantic_intent.json"))
    write_json(ROOT / "config/unified_retrieval.json", locked)


def pool_coverage(case, rows):
    if case["task"] == "hs":
        return float(
            case["expected_hs_8"]
            in {
                r.get("code")
                for r in rows
                if r.get("level") == 8 and r.get("chunk_type") == "tariff_entry"
            }
        )
    ids = {r["id"] for r in rows}
    groups = case["canonical_groups"]
    return sum(bool(ids & set(g["any_of"])) for g in groups) / len(groups)


def evaluate_test():
    protocol()
    locked = read(RUN / "locked_policy.json")
    if read(ROOT / "config/unified_retrieval.json") != locked:
        raise ValueError("Activate the locked Dev policy first")
    rows, predictions, detail = cases("test"), {}, {}
    target = RUN / "test_runtime_rows.json"
    saved = read(target) if target.exists() else {"policy_hash": digest(locked), "rows": {}}
    if saved["policy_hash"] != digest(locked):
        raise ValueError("Test predictions have a different locked policy")
    embedder = Embedder()
    with connect() as conn:
        r = Retriever(conn, embedder)
        for i, c in enumerate(rows, 1):
            if c["uid"] not in saved["rows"]:
                out = r.routed_search(c["query"])
                if out["routing"]["status"] != "UNIFIED_SOURCE_RETRIEVAL":
                    raise ValueError("Test did not use unified Auto runtime")
                pool = out["candidate_pool"]
                saved["rows"][c["uid"]] = {
                    "ranked": compact(out["ranked_pool"]),
                    "semantic_intent": out["semantic_intent"],
                    "latency_ms": out["timings"]["total_ms"],
                    "candidate_coverage": pool_coverage(c, pool),
                    "rerank_coverage": pool_coverage(c, pool[: locked["rerank_pool"]]),
                    "package_ids": [x["id"] for x in out["package"]],
                }
            detail[c["uid"]] = saved["rows"][c["uid"]]
            predictions[c["uid"]] = detail[c["uid"]]["ranked"]
            if i % 5 == 0 or i == len(rows):
                write_json(target, saved)
                print(f"Auto Test {i}/{len(rows)}", flush=True)
    result = metrics(rows, predictions)
    result["policy_hash"] = digest(locked)
    result["latency"] = {
        "p50_ms": float(np.percentile([v["latency_ms"] for v in detail.values()], 50)),
        "p95_ms": float(np.percentile([v["latency_ms"] for v in detail.values()], 95)),
        "scope": "SEQUENTIAL_RUNTIME_WITH_WARM_MODEL_AND_PERSISTENT_PAIR_CACHE_NO_SELECTION_GATE",
    }
    for task in ("hs", "qa"):
        subset = [detail[c["uid"]] for c in rows if c["task"] == task]
        result["HS" if task == "hs" else "QA"].update(
            {
                "candidate_coverage": float(np.mean([v["candidate_coverage"] for v in subset])),
                "rerank_coverage": float(np.mean([v["rerank_coverage"] for v in subset])),
            }
        )
    qa_cases = [c for c in rows if c["task"] == "qa"]
    package_coverage = [
        sum(
            bool(set(g["any_of"]) & set(detail[c["uid"]]["package_ids"]))
            for g in c["canonical_groups"]
        )
        / len(c["canonical_groups"])
        for c in qa_cases
    ]
    result["QA"]["reader_package_all_groups"] = float(np.mean([x == 1 for x in package_coverage]))
    result["QA"]["reader_package_group_recall"] = float(np.mean(package_coverage))
    labels = np.array([c["task"] == "qa" for c in rows])
    predicted = np.array([detail[c["uid"]]["semantic_intent"]["p_legal"] > 0.5 for c in rows])
    result["semantic_intent_test"] = {
        "balanced_accuracy": balanced_accuracy_score(labels, predicted),
        "confusion_HS_QA": confusion_matrix(labels, predicted).tolist(),
        "used_for_retrieval": False,
    }
    write_json(RUN / "test_metrics.json", result)
    print("Test metrics", {k: v for k, v in result.items() if k != "rows"}, flush=True)


def compare():
    """Paired query-weighted cluster intervals, with exact baseline point estimates."""
    rows = cases("test")
    new = read(RUN / "test_metrics.json")
    baseline = ROOT / "artifacts/experiments/run_pdf_graph_v4"
    old_hs = read(baseline / "test_predictions.json")
    old_qa = {
        r["id"]: r
        for r in read(baseline / "qa_runtime_regression.json")["rows"]
        if r["split"] == "test"
    }
    predictions = {}
    corpus_records = {r["id"]: r for r in read(ROOT / "artifacts/corpus.json")["records"]}
    for c in rows:
        if c["task"] == "hs":
            predictions[c["uid"]] = [
                {**r, "chunk_type": "tariff_entry"} for r in old_hs[c["record_id"]]["ranked"]
            ]
        else:
            predictions[c["uid"]] = [
                {**corpus_records[sid], "metadata": {}} for sid in old_qa[c["id"]]["returned"]
            ]
    old = metrics(rows, predictions)
    old_by_id = {r["uid"]: r for r in old["rows"]}
    intervals = {}
    rng = np.random.default_rng(20261002)
    for task, keys in (
        ("hs", ("hit@1", "recall@5", "recall@10", "mrr@10")),
        ("qa", ("all_groups@10", "group_recall@10", "mrr@10")),
    ):
        grouped = defaultdict(list)
        for row in new["rows"]:
            if row["task"] == task:
                grouped[row["group"]].append(
                    np.array([row[k] - old_by_id[row["uid"]][k] for k in keys])
                )
        sums = np.array([np.sum(v, axis=0) for v in grouped.values()])
        sizes = np.array([len(v) for v in grouped.values()])
        indices = rng.integers(0, len(sums), (2000, len(sums)))
        sampled = sums[indices].sum(axis=1) / sizes[indices].sum(axis=1)[:, None]
        point = sums.sum(axis=0) / sizes.sum()
        intervals[task] = {
            key: {
                "delta": float(point[i]),
                "ci95": np.percentile(sampled[:, i], [2.5, 97.5]).tolist(),
            }
            for i, key in enumerate(keys)
        }
    write_json(
        RUN / "test_comparison.json",
        {
            "baseline": {k: v for k, v in old.items() if k != "rows"},
            "new": {k: v for k, v in new.items() if k != "rows"},
            "intervals": intervals,
            "baseline_scope": "V4 forced HS and forced QA with known task; new run uses Auto for both",
            "bootstrap": "2000 paired whole-group draws, query-weighted means; no significance claim for macro objective",
        },
    )
    print("Paired intervals", intervals, flush=True)


def verify_runtime():
    protocol()
    locked = read(RUN / "locked_policy.json")
    expected = {r["uid"]: r for r in read(RUN / "dev_selection.json")[0]["metrics"]["rows"]}
    chosen, strata = [], set()
    for case in cases("dev"):
        stratum = (case["task"], case.get("section") or case["category"])
        if stratum not in strata and (case["task"] == "hs" or len(chosen) < 6):
            chosen.append(case)
            strata.add(stratum)
        if len(chosen) == 6:
            break
    checked = []
    with connect() as conn:
        r = Retriever(conn, Embedder())
        if r.unified_policy != locked:
            raise ValueError("Runtime verification requires the locked policy")
        source_ids = {row["id"] for row in r.documents("knowledge")}
        for case in chosen:
            reference = None
            for hint in ("auto", "product", "qa"):
                out = r.routed_search(case["query"], intent=hint)
                result = {
                    "returned": [row["id"] for row in out["matches"]],
                    "hs_codes": [row["code"] for row in out["hs_candidates"]],
                }
                if result != {key: expected[case["uid"]][key] for key in result}:
                    raise ValueError(f"Runtime/replay mismatch: {case['uid']}")
                if reference is not None and result != reference:
                    raise ValueError("Intent hint changed ranking")
                if not all(row["id"] in source_ids for row in out["package"]):
                    raise ValueError("Reader package contains a non-atomic source")
                if out["semantic_intent"]["used_for_retrieval"]:
                    raise ValueError("Semantic intent changed retrieval")
                reference = result
            checked.append({"uid": case["uid"], "task": case["task"], "hints": 3, "passed": True})
            print("Runtime parity", case["uid"], flush=True)
    write_json(RUN / "runtime_verification.json", {"policy_hash": digest(locked), "rows": checked})


def validate_implementation():
    protocol()
    checks = {}
    commands = {
        "pytest": [sys.executable, "-m", "pytest", "-q", "--tb=line", "tests/"],
        "ruff": [sys.executable, "-m", "ruff", "check", "rag", "scripts", "tests"],
        "format": [sys.executable, "-m", "ruff", "format", "--check", "rag", "scripts", "tests"],
        "mypy": [sys.executable, "-m", "mypy", "rag", "--ignore-missing-imports"],
        "diff": ["git", "diff", "--check"],
    }
    for name, command in commands.items():
        path = RUN / f"validation_{name}.log"
        with path.open("w") as log:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env={**os.environ, "RAG_RUN_DB_TESTS": "1"},
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        if result.returncode:
            raise RuntimeError(f"Implementation check failed: {name}; see {path}")
        summary = re.findall(r"\d+ passed[^\n]*", path.read_text()) if name == "pytest" else []
        checks[name] = {"passed": True, "log": path.name, "summary": summary[-1:]}
        print("Validation", name, checks[name], flush=True)
    for path in (ROOT / "notebooks").glob("0[12]*.ipynb"):
        notebook = read(path)
        for i, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]), filename=f"{path}:cell-{i}")
        checks[path.name] = {"passed": True, "scope": "CODE_CELL_SYNTAX_ONLY"}
    write_json(
        RUN / "implementation_validation.json",
        {"policy_hash": digest(read(RUN / "locked_policy.json")), "checks": checks},
    )


def report():
    protocol()
    locked = read(RUN / "locked_policy.json")
    selected = read(RUN / "dev_selection.json")[0]
    screen_result = read(RUN / "screen_selection.json")
    comparison = read(RUN / "test_comparison.json")
    old, new = comparison["baseline"], comparison["new"]
    intent_model = read(RUN / "semantic_intent.json")

    def pct(value):
        return f"{100 * value:.1f}%"

    lines = [
        "# Báo cáo Retrieval chung HS/Legal — v5",
        "",
        "## 1. Thay đổi luồng phục vụ",
        "",
        "Auto dùng một thuật toán cho mọi câu hỏi: hybrid toàn nguồn → context BM25/dense → ứng viên từ quan hệ graph → pool chung theo ID → reranker/cascade chung → chứng cứ và shortlist HS8.",
        "Nhận diện ngữ nghĩa là thông tin bổ trợ sau retrieval. `intent=product/qa` là hint hiển thị, không lọc hoặc đổi trọng số. Các API `adaptive_search`/`qa_search` và config v4 được giữ để tái lập đối chứng; Auto v5 không gọi router từ khóa và từ chối phục vụ khi chưa có policy chung đã kích hoạt. `legacy_routed_search` chỉ dùng để tái lập router v4.",
        "",
        "Luồng v4: HS dùng B1/M3, pool 100/rerank 60, trọng số .35/.15/.35/.05/.10; QA dùng C10, pool 100/rerank 30, trọng số .25/.25/.10/.10/.30. Auto chọn nhánh bằng regex; chỉ đưa 48/130 câu Legal Test vào QA. Đây là tỷ lệ định tuyến, không phải Recall pháp lý.",
        "",
        "V5 dùng pool nguồn chung 160 và cửa sổ rerank đã chọn bên dưới. So sánh v4/v5 là so sánh hai pipeline, thay cả tuyển ứng viên, biểu diễn context và xếp hạng; không thể quy toàn bộ mức thay đổi cho riêng model reranker hoặc việc bỏ router.",
        "",
        "## 2. Cấu hình đã chọn chỉ bằng Dev",
        "",
        "```json",
        json.dumps(locked, ensure_ascii=False, indent=2),
        "```",
        "",
        "Pool giữ cả HS4/HS6/HS8, Notes, GIR và điều khoản pháp lý. Không gộp các ID chứng cứ có cùng mã HS. Các nhánh và thông số áp dụng chung cho mọi Chương. B1 thêm phân cấp; B2 thêm Notes liên quan từ graph. Model và prompt được khóa; cache phân biệt revision, query, context, instruction và token budget.",
        "",
        "Kênh graph lấy tổ tiên và Notes của các nguồn đã tìm được; chưa duyệt đầy đủ mọi quan hệ tham chiếu hoặc thực thi GIR. Các điều kiện trong code phục vụ schema, ngân sách token, backend model và kiểm tra lock; không có keyword → mã HS, phạt thuộc tính theo mã hoặc cấu hình theo Chương.",
        "",
        "`matches` là Top-10 nguồn hỗn hợp. `hs_candidates` là Top-10 HS8 chiếu từ cùng pool đã chấm. `package` materialize các đoạn nguồn thực sự được trích trong context, có ngân sách lớn hơn Top-10. Điểm HS shortlist và điểm trên danh sách hỗn hợp được báo riêng. Điểm Legal chính đòi đúng mọi ID nguồn sơ cấp trong Top-10; không tính alias hay Notes đính kèm thay cho đoạn nguồn trực tiếp.",
        "",
        "## 3. Thực nghiệm Dev",
        "",
        f"Dev: 752 HS + 520 QA = 1.272 câu. Screen cố định {screen_result['count']} câu, giữ toàn nhóm, cân bằng Phần HS và trải các loại QA. Sàng lọc theo chất lượng, không dùng latency. Hai model đơn tốt nhất được chấm toàn Dev; M3 và cascade M3 → Qwen cũng được chấm toàn Dev. Model bị loại ở screen chỉ có bằng chứng trên screen.",
        "",
        "Tiêu chí chính: trung bình(HS Macro MRR@10, Legal strict all-groups@10). Tie-break: QA group recall, HS Macro Recall@5, ngân sách nhỏ hơn. Hai trọng số hybrid, B1/B2, pool 60/100, rank weight .85/1; cascade shortlist 20/40, weight .5/1. Phương án tốt nhất chỉ nằm trong không gian đã khảo sát, chưa là tối ưu toàn cục.",
        "",
        "| Model | Phạm vi | Method / weights | Objective | HS Hit@1 | Legal đủ nhóm @10 |",
        "|---|---|---|---:|---:|---:|",
    ]
    for model in MODELS:
        item = next(r for r in screen_result["results"] if r["policy"]["model"] == model)
        a, b = item["policy"], item["metrics"]
        lines.append(
            f"| {model} | Screen | {a['method']} / {a['weights_name']} | {b['objective']:.4f} | {pct(b['HS']['hit@1'])} | {pct(b['QA']['all_groups@10'])} |"
        )
    full = read(RUN / "dev_selection.json")
    for model in sorted({r["policy"]["model"] for r in full}):
        item = next(r for r in full if r["policy"]["model"] == model)
        a, b = item["policy"], item["metrics"]
        lines.append(
            f"| {model} | Toàn Dev | {a['method']} / {a['weights_name']} | {b['objective']:.4f} | {pct(b['HS']['hit@1'])} | {pct(b['QA']['all_groups@10'])} |"
        )
    lines += [
        "",
        f"Cấu hình thắng Dev: Macro MRR HS {selected['metrics']['HS_MACRO']['mrr@10']:.4f}, Legal đủ nhóm @10 {pct(selected['metrics']['QA']['all_groups@10'])}.",
        "",
        "## 4. Test qua Auto thực tế sau khi khóa",
        "",
        "| Phạm vi HS | Số câu | Hit@1 v4 | Hit@1 v5 | Recall@5 v4 | Recall@5 v5 | MRR@10 v5 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for section in new["sections"]:
        a, b = old["sections"][section], new["sections"][section]
        lines.append(
            f"| {section} | {b['count']} | {pct(a['hit@1'])} | {pct(b['hit@1'])} | {pct(a['recall@5'])} | {pct(b['recall@5'])} | {b['mrr@10']:.4f} |"
        )
    a, b = old["HS"], new["HS"]
    lines += [
        f"| Toàn HS | {b['count']} | {pct(a['hit@1'])} | {pct(b['hit@1'])} | {pct(a['recall@5'])} | {pct(b['recall@5'])} | {b['mrr@10']:.4f} |",
        "",
        f"HS hỗn hợp: Top-1 toàn danh sách nguồn đúng mã {pct(b['mixed_hit@1'])}; mã đúng trong Top-10 toàn nguồn {pct(b['mixed_recall@10'])}. Không được gọi các số shortlist ở bảng trên là Top-1 của toàn danh sách nguồn.",
        "",
        "| Legal Test (130 câu) | v4 gọi QA trực tiếp | v5 Auto chung |",
        "|---|---:|---:|",
        f"| Đủ mọi nhóm sơ cấp @10 | {pct(old['QA']['all_groups@10'])} | {pct(new['QA']['all_groups@10'])} |",
        f"| Group Recall@10 | {pct(old['QA']['group_recall@10'])} | {pct(new['QA']['group_recall@10'])} |",
        f"| MRR@10 | {old['QA']['mrr@10']:.4f} | {new['QA']['mrr@10']:.4f} |",
        f"| Gói nguồn bổ sung đủ nhóm | Khác quy trình mở rộng | {pct(new['QA']['reader_package_all_groups'])} |",
        "",
        f"Coverage candidate pool v5: HS {pct(new['HS']['candidate_coverage'])}, Legal group coverage {pct(new['QA']['candidate_coverage'])}. Coverage cửa sổ rerank: HS {pct(new['HS']['rerank_coverage'])}, Legal {pct(new['QA']['rerank_coverage'])}.",
        "",
        "## 5. Khoảng tin cậy thay đổi",
        "",
        "Lấy mẫu ghép cặp nguyên cụm 2.000 lần; delta và CI dùng trung bình theo câu, không trộn với Macro. Baseline dùng tác vụ đúng đã biết; v5 dùng Auto cho cả hai.",
        "",
        "| Tác vụ / chỉ số | Delta | 95% CI |",
        "|---|---:|---|",
    ]
    for task, items in comparison["intervals"].items():
        for key, value in items.items():
            scale, unit = (1, "") if key == "mrr@10" else (100, " điểm %")
            lower, upper = value["ci95"]
            lines.append(
                f"| {task} / {key} | {scale * value['delta']:+.3f}{unit} | [{scale * lower:+.3f}, {scale * upper:+.3f}]{unit} |"
            )
    lines += [
        "",
        "## 6. Nhận diện ngữ nghĩa và giới hạn",
        "",
        f"Logistic regression trên vector BGE-M3 của câu hỏi; C chọn bằng 5 Dev folds giữ nhóm, accuracy rồi log-loss. Model embedding/reranker không fine-tune. C={intent_model['C']}. Test balanced accuracy={pct(new['semantic_intent_test']['balanced_accuracy'])}, confusion HS/QA={new['semantic_intent_test']['confusion_HS_QA']}. Nhận diện không ảnh hưởng candidates hoặc ranking.",
        "",
        "Các câu benchmark đã từng được xem. Test là hồi quy; kết quả chưa chứng minh chất lượng ở Chương mới hoặc câu thiếu thuộc tính. Thêm Chương cùng schema sẽ đi qua cùng thuật toán sau ingest/rebind snapshot. Tính đúng của áp dụng Notes/GIR và quyết định mã cuối vẫn cần kiểm chứng nguồn; retrieval không phải bộ suy luận pháp lý hoàn chỉnh.",
        "",
        "Không dùng latency làm điều kiện chọn. Số latency trong test_metrics.json gồm query/model caches theo lịch sử chạy, chỉ mô tả lượt đo; không dùng làm SLA. Các artifact score/pool đầy đủ cho kiểm tra lại; config và nguồn không được chọn lại bằng Test.",
        "",
        "Gemma dùng logits của token cuối, left padding và position_ids tường minh, tắt KV cache/hidden-state outputs không cần thiết. Cache layout này tách khỏi backend full logits cũ. Kiểm tra 4 cặp nguồn cho cùng thứ tự, chênh lệch logit tối đa 0.0078125 (gemma_equivalence.json); đây là kiểm tra backend nhỏ, không thay cho đánh giá chất lượng. Chỉ số screen/full/Test dùng layout mới; không suy ra tương đương số học tuyệt đối từ 4 cặp này.",
        "",
        "## 7. Nghiên cứu và tái lập",
        "",
        "[Sentence Transformers: Retrieve & Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) mô tả tuyển ứng viên trước khi rerank. [Qwen model card](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) cung cấp prompt instruction và yes/no logits; v5 thay prompt chỉ dành cho sản phẩm bằng yêu cầu tìm chứng cứ chung. [Gemma model card](https://huggingface.co/BAAI/bge-reranker-v2-gemma) là căn cứ backend thử nghiệm. [Grouped CV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html) hỗ trợ giữ nhóm câu cùng họ trong đánh giá.",
        "",
        "Runner duy nhất: `scripts/benchmark_unified_retrieval.py`. Protocol, source/profile binding, dataset SHA-256, pools, raw scores, screen selection, Dev selection, intent model, locked policy, Test runtime rows và paired intervals nằm trong thư mục này. Test runtime dùng `Retriever.routed_search`, không ép tác vụ từ gold.",
    ]
    verification_path = RUN / "runtime_verification.json"
    if verification_path.exists():
        verified = read(verification_path)
        if verified["policy_hash"] != digest(locked):
            raise ValueError("Runtime verification differs from report policy")
        lines += [
            "",
            "## 8. Kiểm chứng runtime",
            "",
            f"{len(verified['rows'])} câu Dev đối chiếu chính xác Top-10 nguồn và shortlist HS8 giữa runtime và replay; mỗi câu thử cả auto/product/qa. Mọi package ID đều là bản ghi nguồn thực; semantic intent không tham gia retrieval. Đây là kiểm tra tính nhất quán triển khai, không là tập đánh giá mới.",
        ]
    validation_path = RUN / "implementation_validation.json"
    if validation_path.exists():
        validated = read(validation_path)
        if validated["policy_hash"] != digest(locked):
            raise ValueError("Implementation validation differs from report policy")
        lines += ["", "## 9. Kiểm thử triển khai", ""]
        for name, check in validated["checks"].items():
            lines.append(f"- {name}: PASS. {'; '.join(check.get('summary', []))}")
    (RUN / "IMPLEMENTATION_REPORT_V5.md").write_text("\n".join(lines) + "\n")


def run():
    """Resume the frozen protocol through Dev selection and final runtime Test."""
    protocol()

    def execute(action, *args):
        name = "_".join((action, *args)).replace("--", "")
        print("START", action, *args, flush=True)
        with (RUN / (name + ".log")).open("w") as log:
            subprocess.run(
                [sys.executable, __file__, action, *args],
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        print("DONE", action, *args, flush=True)

    if not (RUN / "locked_policy.json").exists():
        if not (RUN / "dev_pools.sqlite").exists():
            execute("prepare", "--split", "dev")
        if not (RUN / "semantic_intent.json").exists():
            execute("intent")
        for model in MODELS:
            execute("score", "--phase", "screen", "--model", model)
        execute("screen-select")
        for model in read(RUN / "screen_selection.json")["full_models"]:
            execute("score", "--phase", "full", "--model", model)
        execute("cascade")
        execute("select")
    execute("activate")
    execute("test")
    execute("compare")
    execute("verify")
    execute("validate")
    execute("report")
    print("UNIFIED_ACCURACY_RUN_COMPLETE", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "init",
            "prepare",
            "score",
            "screen-select",
            "intent",
            "cascade",
            "select",
            "activate",
            "test",
            "compare",
            "verify",
            "validate",
            "report",
            "run",
        ],
    )
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--phase", choices=["screen", "full"], default="screen")
    parser.add_argument("--model", choices=list(MODELS), default="m3")
    args = parser.parse_args()
    torch.set_num_threads(4)
    if args.action == "init":
        print(protocol()["selection"])
    elif args.action == "prepare":
        if args.split == "test" and not (RUN / "locked_policy.json").exists():
            raise ValueError("Lock policy on Dev before Test")
        prepare(args.split)
    elif args.action == "score":
        score(args.model, args.phase)
    elif args.action == "screen-select":
        select_screen()
    elif args.action == "intent":
        intent()
    elif args.action == "cascade":
        cascade()
    elif args.action == "select":
        select_full()
    elif args.action == "activate":
        activate()
    elif args.action == "test":
        evaluate_test()
    elif args.action == "compare":
        compare()
    elif args.action == "verify":
        verify_runtime()
    elif args.action == "validate":
        validate_implementation()
    elif args.action == "report":
        report()
    else:
        run()


if __name__ == "__main__":
    main()
