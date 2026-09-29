"""Frozen grouped split and candidate benchmarks without label leakage."""

import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from typing import Any

import numpy as np

from rag.data import ROOT, config, digest, read
from rag.retrieval import Retriever, code_mention_plan


def clean_product_text(text: str) -> str:
    """Remove dataset instructions and explicit tariff labels, never product quantities."""
    text = re.split(r"(?i)\bcase\s+test\b", text)[0]
    text = re.sub(
        r"(?i)(?:thuộc\s+)?(?:phân nhóm|nhánh|nhóm|mã HS|HS code|heading|chương)"
        r"\s*\d{2,8}(?:\.\d{2}){0,2}",
        "",
        text,
    )
    text = re.sub(r"(?i)chú giải\s+\d+(?:/\d+)*", "", text)
    text = re.sub(r"(?<![\d.])\d{8}(?![\d.])", "", text)
    return " ".join(text.split()).strip(" .;,:")


def query_for(row: dict, variant: str) -> str:
    name = clean_product_text(row["product_name_vi"])
    if variant == "name_only":
        return name
    if variant == "name_and_spec":
        return name + ". " + clean_product_text(row["technical_description_for_test"])
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


def discover_gold(partitions: tuple[str, ...] = ("train", "test")) -> tuple[list[dict], list[str]]:
    """Load only explicitly requested user partitions; ignore all/ and CSV mirrors."""
    rows = []
    paths = []
    if not partitions or set(partitions) - {"train", "test", "holdout"}:
        raise ValueError("Unknown or empty gold partitions")
    for partition in partitions:
        files = sorted((ROOT / "data/verified/hs" / partition).glob("*.jsonl"))
        if len(files) != 1:
            raise ValueError(f"Expected exactly one JSONL in verified/hs/{partition}")
        path = files[0]
        paths.append(str(path.relative_to(ROOT)))
        for row in read(path):
            code = str(row["expected_hs_8"]).replace(".", "").strip()
            if len(code) != 8 or not code.isdigit():
                raise ValueError(f"Invalid gold code: {row['record_id']}")
            section = "XIV" if code[:2] == "71" else "XVI" if code[:2] in ("84", "85") else "XVII"
            if row["split"] != partition or row["section"] != section:
                raise ValueError(f"Partition/Section mismatch: {row['record_id']}")
            rows.append(
                {
                    **row,
                    "test_id": row["record_id"],
                    "query": query_for(row, "name_only"),
                    "section": section,
                    "source_file": str(path.relative_to(ROOT)),
                }
            )
    if len({r["test_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate gold IDs")
    return rows, paths


def benchmark_split(cases: list[dict]) -> dict:
    """Record supplied product and family isolation, with code overlap reported."""

    if len({row["test_id"] for row in cases}) != len(cases):
        raise ValueError("Gold IDs duplicated across partitions")

    def signature(row):
        return unicodedata.normalize("NFKC", query_for(row, "name_only")).casefold()

    groups = {
        name: [r for r in cases if r["split"] == name] for name in ("train", "test", "holdout")
    }
    for left, right in (("train", "test"), ("train", "holdout"), ("test", "holdout")):
        duplicate_products = {signature(r) for r in groups[left]} & {
            signature(r) for r in groups[right]
        }
        if duplicate_products:
            raise ValueError(f"Products duplicated between {left}/{right}: {duplicate_products}")
        left_families = {r["case_family_id"] for r in groups[left] if r.get("case_family_id")}
        right_families = {r["case_family_id"] for r in groups[right] if r.get("case_family_id")}
        if left_families & right_families:
            raise ValueError(f"Case families duplicated between {left}/{right}")
    result = {
        "gold_sha256": digest(cases),
        "grouping": "USER_SUPPLIED_PRODUCT_DISJOINT",
        "dev": [r["test_id"] for r in groups["train"]],
        "test": [r["test_id"] for r in groups["test"]],
        "holdout": [r["test_id"] for r in groups["holdout"]],
        "overlapping_codes": sorted(
            {r["expected_hs_8"] for r in groups["train"]}
            & {r["expected_hs_8"] for r in groups["test"]}
        ),
        "purpose": "train tunes retrieval; test diagnoses; holdout evaluates frozen policy once",
    }
    return result


CONFIGURATIONS = {
    "C1": ("dense",),
    "C2": ("sparse",),
    "C3": ("bm25",),
    "C4": ("fts",),
    "C5": ("dense", "sparse"),
    "C6": ("dense", "bm25"),
    "C7": ("dense", "sparse", "fts"),
    "C8": ("dense", "sparse", "exact"),
    "C9": ("dense", "bm25", "exact"),
    "C10": ("dense", "sparse", "bm25", "fts", "exact"),
    "C13": ("dense", "sparse", "bm25", "exact"),
    "C14": ("dense", "sparse", "bm25"),
    "C15": ("sparse", "bm25", "exact"),
}
INITIAL_POLICIES = {
    "router": {"dense": 0.35, "sparse": 0.20, "bm25": 0.20, "fts": 0.10, "exact": 0.15},
    "XIV": {"dense": 0.20, "sparse": 0.25, "bm25": 0.25, "fts": 0.10, "exact": 0.20},
    "XVI": {"dense": 0.35, "sparse": 0.25, "bm25": 0.15, "fts": 0.10, "exact": 0.15},
    "XVII": {"dense": 0.30, "sparse": 0.20, "bm25": 0.20, "fts": 0.10, "exact": 0.20},
    "legal": {"dense": 0.40, "sparse": 0.15, "bm25": 0.25, "fts": 0.15, "exact": 0.05},
}


@lru_cache(maxsize=32)
def weight_grid(branches: tuple[str, ...], units: int = 20) -> list[dict]:
    # Positive simplex grid (step .05); endpoints are covered by C1-C4/ablations.
    def compositions(total: int, parts: int):
        if parts == 1:
            if total >= 1:
                yield (total,)
        else:
            for first in range(1, total - parts + 2):
                for rest in compositions(total - first, parts - 1):
                    yield (first, *rest)

    if len(branches) == 1:
        return [{branches[0]: 1.0}]
    grid = [
        dict(zip(branches, [v / units for v in values], strict=True))
        for values in compositions(units, len(branches))
    ]
    # Include the proposed .15/.35 policies, even for a different chosen grid resolution.
    for policy in INITIAL_POLICIES.values():
        total = sum(policy[b] for b in branches)
        projected = {b: policy[b] / total for b in branches}
        if projected not in grid:
            grid.append(projected)
    rng = np.random.default_rng(config()["seed"] + len(branches))
    for alpha in (0.3, 1.0, 3.0):
        for values in rng.dirichlet(np.full(len(branches), alpha), size=200):
            grid.append(dict(zip(branches, values.tolist(), strict=True)))
    return grid


def branch_cache(
    retriever: Retriever,
    cases: list[dict],
    intent: str = "product",
    filters: dict | None = None,
    pool: int = 50,
    use_cache: bool = True,
    mask_questioned_codes: bool = False,
) -> list[dict]:
    """Retrieve once per query, then sweep weights without repeating model inference."""
    import gzip
    import json
    import time

    output = []
    filters = filters or {}
    for i, case in enumerate(cases):
        query = case["query"]
        exact_query = code_mention_plan(query)["exact_query"] if mask_questioned_codes else query
        cache_dir = ROOT / "artifacts/benchmark_branches"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_key = digest(
            {
                "snapshot": retriever.snapshot,
                "profile": retriever.profile,
                "query": query,
                "intent": intent,
                "filters": filters,
                "pool": pool,
                "implementation": "rank-bm25-0.2.2-exact-v2",
                "exact_query": exact_query,
            }
        )
        target = cache_dir / (cache_key + ".json.gz")
        if use_cache and target.exists():
            with gzip.open(target, "rt") as stream:
                cached = json.load(stream)
            output.append({**cached, "case": case})
            print(f"Resumed branches {i + 1}/{len(cases)}", flush=True)
            continue
        tick = time.perf_counter()
        encoded = (
            retriever.embedder.encode([query], use_cache=use_cache) if retriever.embedder else None
        )
        if encoded is None:
            raise ValueError("Benchmark needs an embedder")
        embedding_ms = (time.perf_counter() - tick) * 1000
        branches = {}
        timings = {"embedding_ms": embedding_ms, "query_cache_hit": encoded["cache_hit"]}
        functions = {
            "dense": lambda: retriever.dense(encoded["dense"][0], intent, pool, **filters),
            "sparse": lambda: retriever.sparse(encoded["sparse"][0], intent, pool, **filters),
            "bm25": lambda: retriever.bm25(query, intent, pool, **filters),
            "fts": lambda: retriever.lexical(query, intent, pool, **filters),
            "exact": lambda: retriever.exact_match(exact_query, intent, pool, **filters),
        }
        for name, function in functions.items():
            start = time.perf_counter()
            branches[name] = function()
            timings[name + "_ms"] = (time.perf_counter() - start) * 1000
        item = {"case": case, "branches": branches, "timings": timings}
        with gzip.open(target, "wt") as stream:
            json.dump(item, stream, ensure_ascii=False, default=str)
        output.append(item)
        print(f"Cached branches {i + 1}/{len(cases)}", flush=True)
    return output


def ranking_metrics(
    cases: list[dict], rankings: list[list[dict]], sections: list[list[dict]] | None = None
) -> dict:
    import math

    rows = []
    for i, (case, ranked) in enumerate(zip(cases, rankings, strict=True)):
        gold = case["expected_hs_8"]
        codes = [r["code"] for r in ranked if r.get("level") == 8]
        rank = codes.index(gold) + 1 if gold in codes else None
        predicted_sections = sections[i] if sections is not None else []
        row = {
            "rank": rank,
            "section_correct": bool(
                predicted_sections and predicted_sections[0]["section"] == case["section"]
            ),
            "section_recall@2": any(
                s["section"] == case["section"] for s in predicted_sections[:2]
            ),
            "hit@1": rank == 1,
            "mrr": 1 / rank if rank and rank <= 10 else 0,
            "ndcg@10": 1 / math.log2(rank + 1) if rank and rank <= 10 else 0,
        }
        for length, name in [(2, "chapter"), (4, "heading"), (6, "hs6"), (8, "ahtn8")]:
            prefixes = list(dict.fromkeys(c[:length] for c in codes))[:5]
            row[name + "_recall@5"] = gold[:length] in prefixes
        rows.append(row)
    result: dict[str, Any] = (
        {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != "rank"} if rows else {}
    )
    result["count"] = len(rows)
    result["hierarchy_metric_mode"] = "ANCESTOR_PROJECTION_OF_LEAF_RANKING"
    # Exclusions require annotated forbidden codes, not merely graph connectivity.
    annotated = [
        (c, r)
        for c, r in zip(cases, rankings, strict=True)
        if isinstance(c.get("forbidden_codes"), list)
    ]
    result["exclusion_annotated_count"] = len(annotated)
    result["exclusion_violation_rate"] = (
        float(
            np.mean(
                [any(x.get("code") in c["forbidden_codes"] for x in r[:5]) for c, r in annotated]
            )
        )
        if annotated
        else None
    )
    return result


def sweep_weights(
    cache: list[dict], family: str, ks: tuple[int, ...] = (5, 10, 20, 40, 60, 100, 200)
) -> list[dict]:
    """Vectorized RRF scoring; output is an aggregate, not thousands of report files."""
    branches = CONFIGURATIONS[family]
    grid = weight_grid(branches)
    weights = np.array([[w[b] for b in branches] for w in grid], dtype=np.float64)
    runs = []
    for k in ks:
        hit1 = np.zeros(len(grid))
        hit5 = np.zeros(len(grid))
        mrr = np.zeros(len(grid))
        ndcg = np.zeros(len(grid))
        for item in cache:
            rows = {r["id"]: r for b in branches for r in item["branches"][b]}
            ids = sorted(rows)
            index = {sid: i for i, sid in enumerate(ids)}
            matrix = np.zeros((len(branches), len(ids)), dtype=np.float64)
            for bi, branch in enumerate(branches):
                for rank, row in enumerate(item["branches"][branch], 1):
                    matrix[bi, index[row["id"]]] = 1 / (k + rank)
            if not ids:
                continue
            scores = weights @ matrix
            gold_ids = [
                index[sid] for sid in ids if rows[sid].get("code") == item["case"]["expected_hs_8"]
            ]
            if gold_ids:
                # Deterministic ties use sorted IDs, matching fuse().
                gi = gold_ids[0]
                ranks = (
                    1
                    + (scores > scores[:, gi : gi + 1]).sum(axis=1)
                    + ((scores == scores[:, gi : gi + 1]) & (np.arange(len(ids)) < gi)).sum(axis=1)
                )
                hit1 += ranks == 1
                hit5 += ranks <= 5
                mrr += np.where(ranks <= 10, 1 / ranks, 0)
                ndcg += np.where(ranks <= 10, 1 / np.log2(ranks + 1), 0)
        for i, w in enumerate(grid):
            runs.append(
                {
                    "configuration": family,
                    "weights": w,
                    "k": k,
                    "count": len(cache),
                    "hit@1": float(hit1[i] / len(cache)),
                    "ahtn8_recall@5": float(hit5[i] / len(cache)),
                    "mrr": float(mrr[i] / len(cache)),
                    "ndcg@10": float(ndcg[i] / len(cache)),
                }
            )
    return sorted(
        runs, key=lambda r: (-r["hit@1"], -r["ahtn8_recall@5"], -r["mrr"], -r["ndcg@10"], r["k"])
    )


def sweep_router(cache: list[dict]) -> list[dict]:
    branches = CONFIGURATIONS["C10"]
    grid = weight_grid(branches)
    weights = np.array([[w[b] for b in branches] for w in grid], dtype=np.float64)
    results = []
    sections = ["XIV", "XVI", "XVII"]
    for k in (20, 60, 100):
        accuracy = np.zeros((len(grid), 3))
        recall = np.zeros((len(grid), 3))
        counts = np.zeros(3)
        for item in cache:
            rows = {r["id"]: r for b in branches for r in item["branches"][b]}
            ids = sorted(rows)
            index = {sid: i for i, sid in enumerate(ids)}
            matrix = np.zeros((5, len(ids)), dtype=np.float64)
            for bi, b in enumerate(branches):
                for rank, r in enumerate(item["branches"][b], 1):
                    matrix[bi, index[r["id"]]] = 1 / (k + rank)
            scores = weights @ matrix
            section_scores = np.stack(
                [
                    scores[:, [index[sid] for sid in ids if rows[sid]["section"] == section]].max(
                        axis=1
                    )
                    if any(rows[sid]["section"] == section for sid in ids)
                    else np.zeros(len(grid))
                    for section in sections
                ],
                axis=1,
            )
            order = np.argsort(-section_scores, axis=1, kind="stable")
            gold = sections.index(item["case"]["section"])
            accuracy[:, gold] += order[:, 0] == gold
            recall[:, gold] += (order[:, :2] == gold).any(axis=1)
            counts[gold] += 1
        if (counts == 0).any():
            raise ValueError("Router dev must cover all three Sections")
        for i, w in enumerate(grid):
            results.append(
                {
                    "weights": w,
                    "k": k,
                    "section_accuracy_macro": float((accuracy[i] / counts).mean()),
                    "section_recall@2_macro": float((recall[i] / counts).mean()),
                }
            )
    return sorted(
        results, key=lambda r: (-r["section_recall@2_macro"], -r["section_accuracy_macro"], r["k"])
    )


def discover_qa(bundle: dict, split: str | None = None) -> list[dict]:
    """Resolve the supplied QA partitions to cited atomic chunks.

    Reading only train keeps the held-out labels outside policy selection.
    """
    if split not in (None, "train", "test"):
        raise ValueError("QA split must be train, test, or None")
    root = ROOT / "data/verified/qa"
    paths = {
        "train": root / "train/LEGAL_RETRIEVAL_TRAIN.jsonl",
        "test": root / "test/LEGAL_RETRIEVAL_TEST.jsonl",
    }
    partitions = (split,) if split else ("train", "test")
    rows = []
    for partition in partitions:
        for case in read(paths[partition]):
            if case.get("split") != partition:
                raise ValueError(f"QA partition mismatch: {case['id']}")
            rows.append(case)
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate QA IDs")
    if len({r["query"].strip().casefold() for r in rows}) != len(rows):
        raise ValueError("Duplicate QA queries")
    if len({r["case_family_id"] for r in rows}) != len(rows):
        raise ValueError("QA case families overlap within the selected partitions")
    if split is None:
        master = read(root / "all/LEGAL_RETRIEVAL_MASTER.jsonl")
        if {r["id"]: r for r in master} != {r["id"]: r for r in rows}:
            raise ValueError("QA master differs from supplied train/test partitions")

    records = {r["id"]: r for r in bundle["records"]}
    by_source: dict[str, list[dict]] = {}
    for record in records.values():
        by_source.setdefault(record["source_id"], []).append(record)
    for case in rows:
        mapping = {}
        entries = case.get("record_mapping") or case.get("source_locations") or []
        for target in entries:
            source_id = target["source_record_id"]
            candidates = [
                r for r in by_source.get(source_id, []) if r["chunk_type"] in QA_CHUNK_TYPES
            ]
            if len(candidates) != 1:
                raise ValueError(f"QA source absent or ambiguous: {case['id']} {source_id}")
            mapping[target["chunk_id"]] = candidates[0]["id"]
        primary = case["gold_primary_chunk_ids"]
        secondary = case.get("gold_secondary_chunk_ids", [])
        if not primary or any(alias not in mapping for alias in primary + secondary):
            raise ValueError(f"QA gold chunk has no source mapping: {case['id']}")
        case["canonical_groups"] = [
            {"label": alias, "any_of": [mapping[alias]]} for alias in primary
        ]
        case["canonical_secondary"] = [mapping[alias] for alias in secondary]
        case["canonical_id_mapping"] = mapping
        case["category"] = case.get("category") or case["retrieval_type"]
    return rows


def qa_coverage(case: dict, ranked: list[dict], package: list[dict]) -> dict:
    """All groups are required; alternatives within one group use ANY OF semantics."""

    def sources(rows):
        return (
            set().union(
                *(
                    {r["id"]}
                    | {r["dataset"] + ":" + x for x in r["metadata"].get("context_source_ids", [])}
                    for r in rows
                )
            )
            if rows
            else set()
        )

    groups = [set(g["any_of"]) for g in case["canonical_groups"]]
    result: dict[str, Any] = {
        "case": case["id"],
        "query": case["query"],
        "required_groups": len(groups),
    }
    for k in (5, 10):
        returned = sources(ranked[:k])
        hits = sum(bool(g & returned) for g in groups)
        result[f"group_recall@{k}"] = hits / len(groups)
        result[f"all_groups@{k}"] = hits == len(groups)
    returned = sources(package)
    result["package_group_recall"] = sum(bool(g & returned) for g in groups) / len(groups)
    result["package_all_groups"] = all(g & returned for g in groups)
    result["missing_package_groups"] = [
        g["label"] for g in case["canonical_groups"] if not set(g["any_of"]) & returned
    ]
    relevant = set().union(*groups)
    first = next((i for i, r in enumerate(ranked[:10], 1) if sources([r]) & relevant), None)
    result["mrr@10"] = 1 / first if first else 0
    # One gain per newly covered group; repeated chunks of the same evidence add no gain.
    covered: set[int] = set()
    dcg = 0.0
    for i, row in enumerate(ranked[:10], 1):
        new = {j for j, g in enumerate(groups) if g & sources([row])} - covered
        dcg += len(new) / np.log2(i + 1)
        covered |= new
    result["group_discounted_coverage@10"] = float(dcg / len(groups))
    result["returned_top10"] = [r["id"] for r in ranked[:10]]
    result["package_size"] = len(package)
    result["citation_complete"] = all(bool(r["locator"]) for r in package)
    return result


QA_CHUNK_TYPES = [
    "gir_rule",
    "gir_explanation",
    "section_note",
    "chapter_note",
    "subheading_note",
    "tariff_entry",
    "legal_clause",
]


def qa_direct_coverage(case: dict, ranked: list[dict]) -> dict:
    """Strict atomic primary chunk scoring; context aliases cannot satisfy a target."""
    rows = [{**r, "metadata": {}} for r in ranked]
    return qa_coverage(case, rows, rows)


def sweep_qa_weights(cache: list[dict], family: str) -> list[dict]:
    """Train-only vectorized grid with every primary chunk required per query."""
    branches = CONFIGURATIONS[family]
    grid = weight_grid(branches)
    weights = np.array([[w[b] for b in branches] for w in grid])
    runs = []
    for k in (5, 20, 60, 100):
        full5 = np.zeros(len(grid))
        full10 = np.zeros(len(grid))
        recall10 = np.zeros(len(grid))
        mrr = np.zeros(len(grid))
        for item in cache:
            ids = sorted({r["id"] for b in branches for r in item["branches"][b]})
            index = {sid: i for i, sid in enumerate(ids)}
            matrix = np.zeros((len(branches), len(ids)))
            for bi, branch in enumerate(branches):
                for rank, row in enumerate(item["branches"][branch], 1):
                    matrix[bi, index[row["id"]]] = 1 / (k + rank)
            scores = weights @ matrix
            ranks = []
            for group in item["case"]["canonical_groups"]:
                sid = group["any_of"][0]
                if sid not in index:
                    ranks.append(np.full(len(grid), np.inf))
                    continue
                gi = index[sid]
                ranks.append(
                    1
                    + (scores > scores[:, gi : gi + 1]).sum(axis=1)
                    + ((scores == scores[:, gi : gi + 1]) & (np.arange(len(ids)) < gi)).sum(axis=1)
                )
            rr = np.stack(ranks, axis=1)
            full5 += (rr <= 5).all(axis=1)
            full10 += (rr <= 10).all(axis=1)
            recall10 += (rr <= 10).mean(axis=1)
            first = rr.min(axis=1)
            mrr += np.where(first <= 10, 1 / first, 0)
        for i, weight in enumerate(grid):
            runs.append(
                {
                    "configuration": family,
                    "weights": weight,
                    "k": k,
                    "all_groups@5": float(full5[i] / len(cache)),
                    "all_groups@10": float(full10[i] / len(cache)),
                    "group_recall@10": float(recall10[i] / len(cache)),
                    "mrr@10": float(mrr[i] / len(cache)),
                }
            )
    return sorted(runs, key=qa_objective, reverse=True)


def qa_objective(row: dict) -> tuple:
    return (row["all_groups@10"], row["group_recall@10"], row["all_groups@5"], row["mrr@10"])
