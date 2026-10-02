"""Experimental framework for Nested Stratified Group Cross-Validation and OOF evaluation."""

import re
import unicodedata

from sklearn.model_selection import StratifiedGroupKFold

from rag.data import ROOT, digest, write_json
from rag.evaluation import clean_product_text, discover_gold


def get_token_set(text: str) -> set[str]:
    cleaned = unicodedata.normalize("NFKC", clean_product_text(text)).casefold()
    return set(re.findall(r"\w+", cleaned))


def build_eval_groups(cases: list[dict], threshold: float = 0.70) -> dict[str, str]:
    """Group contrastive and template-similar cases using Disjoint Set Union."""
    parent = {c["record_id"]: c["record_id"] for c in cases}

    def find(i: str) -> str:
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i: str, j: str) -> None:
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    tokens = [get_token_set(c["product_name_vi"]) for c in cases]
    for i in range(len(cases)):
        t1 = tokens[i]
        sec1 = cases[i]["section"]
        for j in range(i + 1, len(cases)):
            if sec1 != cases[j]["section"]:
                continue
            t2 = tokens[j]
            union_len = len(t1 | t2)
            if union_len > 0 and len(t1 & t2) / union_len >= threshold:
                union(cases[i]["record_id"], cases[j]["record_id"])

    # Family and contrastive identities are mandatory groups, even with low text similarity.
    families: dict[tuple, str] = {}
    for c in cases:
        for field in (
            "case_family_id",
            "contrastive_pair_id",
            "parent_record_id",
            "eval_parent_id",
        ):
            value = c.get(field)
            if not value:
                continue
            key = (field, c["section"], str(value))
            if key in families:
                union(c["record_id"], families[key])
            else:
                families[key] = c["record_id"]

    groups = {}
    for c in cases:
        groups[c["record_id"]] = f"grp_{find(c['record_id'])}"
    return groups


def prepare_manifest(
    run_id: str = "run_generic_graph_v2",
    outer_folds: int = 5,
    inner_folds: int = 3,
    seed: int = 20260930,
) -> dict:
    cases, paths = discover_gold()
    eval_groups = build_eval_groups(cases)

    y = [c["section"] for c in cases]
    group_labels = [eval_groups[c["record_id"]] for c in cases]
    indices = list(range(len(cases)))

    sgkf_outer = StratifiedGroupKFold(n_splits=outer_folds, shuffle=True, random_state=seed)
    outer_splits = list(sgkf_outer.split(indices, y, group_labels))

    rows = []
    fold_assignments = {}
    for fold, (train_idx, test_idx) in enumerate(outer_splits):
        for idx in test_idx:
            c = cases[idx]
            fold_assignments[c["record_id"]] = fold

    # Generate inner fold mappings for each outer fold
    inner_splits_by_outer = {}
    for fold, (train_idx, test_idx) in enumerate(outer_splits):
        train_cases = [cases[i] for i in train_idx]
        y_train = [c["section"] for c in train_cases]
        g_train = [eval_groups[c["record_id"]] for c in train_cases]
        idx_train = list(range(len(train_cases)))

        sgkf_inner = StratifiedGroupKFold(
            n_splits=inner_folds, shuffle=True, random_state=seed + fold + 1
        )
        inner_splits = []
        for i_fold, (i_train_idx, i_val_idx) in enumerate(
            sgkf_inner.split(idx_train, y_train, g_train)
        ):
            inner_splits.append(
                {
                    "inner_fold": i_fold,
                    "train_ids": [train_cases[i]["record_id"] for i in i_train_idx],
                    "val_ids": [train_cases[i]["record_id"] for i in i_val_idx],
                }
            )
        inner_splits_by_outer[str(fold)] = inner_splits

    for c in cases:
        rid = c["record_id"]
        rows.append(
            {
                "record_id": rid,
                "original_split": c.get("original_split", c["split"]),
                "split": c["split"],
                "section": c["section"],
                "expected_hs_8": c["expected_hs_8"],
                "chapter": c["expected_hs_8"][:2],
                "eval_group_id": eval_groups[rid],
                "outer_fold": fold_assignments[rid],
            }
        )

    manifest = {
        "run_id": run_id,
        "evaluation_version": "shared-source-graph-v2",
        "seed": seed,
        "outer_folds": outer_folds,
        "inner_folds": inner_folds,
        "grouping_version": "mandatory-family-and-template-v2",
        "dataset_hash": digest(cases),
        "total_cases": len(cases),
        "total_groups": len(set(eval_groups.values())),
        "source_paths": paths,
        "rows": rows,
    }

    folds_meta = {
        "outer_folds": [
            {
                "fold": f,
                "test_ids": [r["record_id"] for r in rows if r["outer_fold"] == f],
                "train_ids": [r["record_id"] for r in rows if r["outer_fold"] != f],
                "inner_splits": inner_splits_by_outer[str(f)],
            }
            for f in range(outer_folds)
        ]
    }

    out_dir = ROOT / "artifacts/experiments" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "manifest.json", manifest)
    write_json(out_dir / "folds.json", folds_meta)
    return manifest
