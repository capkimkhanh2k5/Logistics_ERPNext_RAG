#!/usr/bin/env python3
"""Reproduce active HS/QA Dev/Test files from the archived original questions."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import sklearn
from sklearn.model_selection import StratifiedGroupKFold

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from rag.data import ROOT, digest, read  # noqa: E402
from rag.evaluation import query_for  # noqa: E402
from rag.experiments import build_eval_groups  # noqa: E402

DEFAULT_OUTPUT = ROOT / "data/verified/hs/dev_test"
ARCHIVE = ROOT / "artifacts/experiments/run_shared_dev_v3/legacy_data/archive_manifest.json"
DEFAULT_SEED = 20261001
N_FOLDS = 5


def partition_cases(cases: list[dict], groups: dict[str, str], seed: int) -> tuple[list, int]:
    """Choose a fifth using count balance only, then add validation folds within Dev."""
    labels = [c["expected_hs_8"][:2] for c in cases]
    group_ids = [groups[c["record_id"]] for c in cases]
    splitter = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    splits = list(splitter.split(cases, labels, group_ids))
    totals = {key: Counter(c[key] for c in cases) for key in ("section", "chapter")}

    def balance(fold: int) -> tuple[int, int, int]:
        selected = [cases[i] for i in splits[fold][1]]
        errors = []
        for key, counts in totals.items():
            actual = Counter(c[key] for c in selected)
            errors.append(sum(abs(actual[name] * N_FOLDS - n) for name, n in counts.items()))
        return errors[0], errors[1], fold

    selected_fold = min(range(N_FOLDS), key=balance)
    dev_idx, test_idx = splits[selected_fold]
    dev = [cases[i] for i in dev_idx]
    dev_folds = {}
    inner = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed + 1)
    for fold, (_, val_idx) in enumerate(
        inner.split(
            dev,
            [c["expected_hs_8"][:2] for c in dev],
            [groups[c["record_id"]] for c in dev],
        )
    ):
        for i in val_idx:
            dev_folds[dev[i]["record_id"]] = fold

    test_ids = {cases[i]["record_id"] for i in test_idx}
    rows = []
    for case in cases:
        rid = case["record_id"]
        rows.append(
            {
                **case,
                "original_split": case["split"],
                "split": "test" if rid in test_ids else "dev",
                "query": query_for(case, "name_and_spec"),
                "eval_group_id": groups[rid],
                "dev_fold": dev_folds.get(rid),
            }
        )
    return rows, selected_fold


def partition_qa(cases: list[dict], seed: int) -> tuple[list, int, dict]:
    proxies = [
        {**r, "record_id": r["id"], "section": "QA", "product_name_vi": r["query"]} for r in cases
    ]
    groups = build_eval_groups(proxies)
    counts = Counter(r.get("category") or r["retrieval_type"] for r in cases)
    # Very small categories cannot populate five folds; keep their real labels in the exports.
    labels = [
        (r.get("category") or r["retrieval_type"])
        if counts[r.get("category") or r["retrieval_type"]] >= N_FOLDS
        else "RARE_CATEGORIES"
        for r in cases
    ]
    splitter = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    splits = list(splitter.split(cases, labels, [groups[r["id"]] for r in cases]))

    def balance(fold):
        actual = Counter(
            cases[i].get("category") or cases[i]["retrieval_type"] for i in splits[fold][1]
        )
        return (
            abs(len(splits[fold][1]) * N_FOLDS - len(cases)),
            sum(abs(actual[k] * N_FOLDS - n) for k, n in counts.items()),
            fold,
        )

    selected = min(range(N_FOLDS), key=balance)
    dev_idx, test_idx = splits[selected]
    dev = [cases[i] for i in dev_idx]
    folds = {}
    inner_labels = [labels[i] for i in dev_idx]
    for fold, (_, idx) in enumerate(
        StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed + 1).split(
            dev, inner_labels, [groups[r["id"]] for r in dev]
        )
    ):
        folds.update({dev[i]["id"]: fold for i in idx})
    test_ids = {cases[i]["id"] for i in test_idx}
    rows = [
        {
            **r,
            "original_split": r["split"],
            "split": "test" if r["id"] in test_ids else "dev",
            "eval_group_id": groups[r["id"]],
            "dev_fold": folds.get(r["id"]),
        }
        for r in cases
    ]
    return rows, selected, groups


def export_split(
    output_dir: Path = DEFAULT_OUTPUT,
    seed: int = DEFAULT_SEED,
    dataset: str = "hs",
    replace: bool = False,
) -> dict:
    archive = read(ARCHIVE)
    source_paths = [
        p for p in archive if p.startswith(f"data/verified/{dataset}/") and p.endswith(".jsonl")
    ]
    cases = []
    for path in source_paths:
        archived_path = ROOT / archive[path]["archive"]
        if hashlib.sha256(archived_path.read_bytes()).hexdigest() != archive[path]["sha256"]:
            raise ValueError(f"Archived source changed: {path}")
        for row in read(archived_path):
            cases.append(
                {
                    **row,
                    "test_id": row["record_id"],
                    "query": query_for(row, "name_only"),
                    "source_file": path,
                }
                if dataset == "hs"
                else {**row, "category": row.get("category") or row["retrieval_type"]}
            )
    if dataset == "hs":
        groups = build_eval_groups(cases)
        rows, selected_fold = partition_cases(cases, groups, seed)
        summaries = ("section", "chapter")
        prefix = "HS_RAG"
    else:
        rows, selected_fold, groups = partition_qa(cases, seed)
        summaries = ("category", "case_type")
        prefix = "LEGAL_RETRIEVAL"
    exports = {name: [r for r in rows if r["split"] == name] for name in ("dev", "test")}
    per_section: dict[str, dict[str, int]] = {}
    per_chapter: dict[str, dict[str, int]] = {}
    for key, summary in zip(summaries, (per_section, per_chapter), strict=True):
        for value in sorted({r[key] for r in rows}):
            summary[value] = {
                name: sum(r[key] == value for r in subset) for name, subset in exports.items()
            }

    file_names = {"dev": f"{prefix}_DEV.jsonl", "test": f"{prefix}_TEST.jsonl"}
    payloads = {
        file_names[name]: "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in subset)
        for name, subset in exports.items()
    }
    manifest = {
        "version": f"{dataset}-dev-test-v1",
        "seed": seed,
        "target_dev_fraction": 0.8,
        "target_test_fraction": 0.2,
        "algorithm": "StratifiedGroupKFold_CHAPTER; min_SECTION_then_CHAPTER_count_error"
        if dataset == "hs"
        else "StratifiedGroupKFold_CATEGORY; min_TOTAL_then_CATEGORY_count_error; rare_categories_pooled",
        "selected_test_fold": selected_fold,
        "selection_inputs": "CASE_COUNTS_ONLY_NO_RETRIEVAL_SCORES",
        "grouping_version": "mandatory-family-and-template-v2",
        "grouping_threshold": 0.70,
        "sklearn_version": sklearn.__version__,
        "evaluation_scope": "PREVIOUSLY_SEEN_REGRESSION_NOT_BLIND",
        "dev_validation_folds": N_FOLDS,
        "total_cases": len(rows),
        "total_groups": len(set(groups.values())),
        "counts": {name: len(subset) for name, subset in exports.items()},
        "groups": {
            name: len({r["eval_group_id"] for r in subset}) for name, subset in exports.items()
        },
        summaries[0] + "_counts": per_section,
        summaries[1] + "_counts": per_chapter,
        "source_dataset_hash": digest(cases),
        "source_file_sha256": {path: archive[path]["sha256"] for path in source_paths},
        "original_file_archive": {path: archive[path]["archive"] for path in source_paths},
        "split_code_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in (
                "scripts/prepare_dev_test.py",
                "rag/experiments.py",
                "rag/evaluation.py",
            )
        },
        "files": {
            name: {
                "path": file_names[name],
                "sha256": hashlib.sha256(payloads[file_names[name]].encode()).hexdigest(),
            }
            for name in exports
        },
    }
    payloads["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    for name, text in payloads.items():
        path = output_dir / name
        if path.exists() and path.read_text() != text and not replace:
            raise ValueError(f"Frozen split differs: {path}; choose a new output directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, text in payloads.items():
        (output_dir / name).write_text(text)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dataset", choices=("hs", "qa", "all"), default="all")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    for dataset in ("hs", "qa") if args.dataset == "all" else (args.dataset,):
        output = args.output_dir or ROOT / f"data/verified/{dataset}/dev_test"
        manifest = export_split(output, args.seed, dataset, args.replace)
        print(
            json.dumps(
                {"dataset": dataset, "output": str(output), "counts": manifest["counts"]}, indent=2
            )
        )


if __name__ == "__main__":
    main()
