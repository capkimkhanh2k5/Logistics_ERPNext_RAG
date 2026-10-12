#!/usr/bin/env python3
"""Run the frozen legal QA policy; this command performs no parameter selection."""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from rag.data import ROOT, digest, load_corpus, read, write_json  # noqa: E402
from rag.db import connect  # noqa: E402
from rag.embedding import Embedder  # noqa: E402
from rag.retrieval import Retriever  # noqa: E402
from tests.support.evaluation import discover_qa, qa_coverage, qa_direct_coverage  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="run_generic_graph_v2_final")
    args = parser.parse_args()
    cases = discover_qa(load_corpus())
    policy_hash = digest(read(ROOT / "config/selected_retrieval.json"))
    embedder = Embedder()
    rows, partitions = [], defaultdict(list)
    with connect() as conn:
        retriever = Retriever(conn, embedder)
        if not getattr(retriever, "qa_policy", None):
            raise ValueError("No QA policy bound to the active snapshot")
        for i, case in enumerate(cases, 1):
            output = retriever.qa_search(case["query"])
            direct = qa_direct_coverage(case, output["matches"])
            package = qa_coverage(case, output["matches"], output["package"])
            row = {
                "id": case["id"],
                "split": case["split"],
                "category": case["category"],
                "all_groups@5": direct["all_groups@5"],
                "all_groups@10": direct["all_groups@10"],
                "group_recall@10": direct["group_recall@10"],
                "mrr@10": direct["mrr@10"],
                "package_all": package["package_all_groups"],
                "returned": direct["returned_top10"],
                "missing_package_groups": package["missing_package_groups"],
            }
            rows.append(row)
            partitions[case["split"]].append(row)
            if i % 25 == 0:
                print(f"QA regression {i}/{len(cases)}", flush=True)
        result = {
            "snapshot": retriever.snapshot,
            "profile": retriever.profile,
            "qa_policy_hash": digest(retriever.qa_policy),
            "selection": "FROZEN_EXISTING_QA_POLICY_NO_RETUNING",
            "rows": rows,
            "splits": {
                split: {
                    "count": len(items),
                    "all_groups@10_correct": sum(r["all_groups@10"] for r in items),
                    **{
                        k: float(np.mean([r[k] for r in items]))
                        for k in (
                            "all_groups@5",
                            "all_groups@10",
                            "group_recall@10",
                            "mrr@10",
                            "package_all",
                        )
                    },
                }
                for split, items in partitions.items()
            },
        }
    assert policy_hash == digest(read(ROOT / "config/selected_retrieval.json")), (
        "QA policy changed during regression"
    )
    target = ROOT / "artifacts/experiments" / args.run_id / "qa_runtime_regression.json"
    write_json(target, result)
    print(result["splits"], flush=True)


if __name__ == "__main__":
    main()
