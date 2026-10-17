"""Small reproducible generation evaluations; gold never enters model messages."""

import json
import time
from collections import defaultdict
from datetime import date, datetime

from config.settings import ROOT
from rag.llm.answering import generate_answer
from rag.llm.context import load_generation_graph, prepare_context
from rag.llm.errors import LLMError
from rag.llm.recovery import recover_answer
from rag.utils.files import digest, read, write_json
from tests.support.evaluation import discover_qa


def json_safe(value):
    def serialize(item):
        if isinstance(item, (date, datetime)):
            return item.isoformat()
        if hasattr(item, "item"):
            return item.item()
        raise TypeError(f"Unsupported artifact value: {type(item).__name__}")

    return json.loads(json.dumps(value, default=serialize, ensure_ascii=False))


def load_cases(split: str = "dev", per_task: int = 2) -> list[dict]:
    if split not in {"dev", "test"} or per_task < 1:
        raise ValueError("Use dev/test and a positive per_task count")
    bundle = read(ROOT / "artifacts/corpus.json")
    hs = [
        {**c, "uid": "hs:" + c["record_id"], "task": "hs"}
        for c in read(ROOT / f"data/verified/hs/HS_RAG_{split.upper()}.jsonl")
    ]
    qa = [{**c, "uid": "qa:" + c["id"], "task": "qa"} for c in discover_qa(bundle, split)]
    selected = []
    for task_rows in (hs, qa):
        strata = defaultdict(list)
        for row in task_rows:
            strata[row.get("section") if row["task"] == "hs" else row["category"]].append(row)
        groups = [sorted(v, key=lambda r: digest(r["uid"])) for _, v in sorted(strata.items())]
        ordered = [
            group[i] for i in range(max(map(len, groups))) for group in groups if i < len(group)
        ]
        selected.extend(ordered[:per_task])
    return selected


def retrieval_for(case: dict, retriever, cache_dir, use_cache: bool = True) -> tuple[dict, bool]:
    identity = {
        "query": case["query"],
        "snapshot": retriever.snapshot,
        "profile": retriever.profile,
        "policy_hash": digest(retriever.unified_policy),
        "query_preprocessing_hash": retriever.query_preprocessing_hash(),
    }
    target = cache_dir / f"{digest(identity)}.json"
    if use_cache and target.exists():
        cached = read(target)
        if cached["identity"] != identity:
            raise ValueError("Retrieval cache identity mismatch")
        return cached["result"], True
    result = json_safe(retriever.routed_search(case["query"]))
    if result.get("query_plan", {}).get("status") != "FALLBACK_RAW":
        write_json(target, {"identity": identity, "result": result})
    return result, False


def score_case(case: dict, context: dict, generated: dict) -> dict:
    answer, validation = generated["answer"], generated["validation"]
    available = {s["id"] for s in context["sources"]}
    cited = set(validation.get("cited_source_ids", []))
    metrics = {
        "structural_validation_pass": validation["valid"],
        "answer_correctness": None,
        "semantic_faithfulness": None,
        "evaluation_scope": "AUTOMATED_STRUCTURE_AND_SOURCE_COVERAGE_ONLY",
    }
    if case["task"] == "hs":
        gold = case.get("expected_hs_8", "")
        shortlist = context.get("retrieved_hs_codes", [])
        metrics.update(
            {
                "gold_hs_in_retrieval_shortlist": gold in shortlist,
                "gold_hs_retrieval_rank": shortlist.index(gold) + 1 if gold in shortlist else None,
                "gold_hs_in_context_candidates": gold in context["allowed_hs_codes"],
                "hs_code_exact_match": validation["valid"]
                and bool(gold)
                and answer.get("suggested_hs_code") == gold,
                "expected_status": case.get("expected_status"),
                "expected_missing_attributes": case.get("missing_attributes", []),
            }
        )
    else:
        groups = [set(g["any_of"]) for g in case["canonical_groups"]]
        metrics.update(
            {
                "context_primary_group_recall": sum(bool(g & available) for g in groups)
                / len(groups),
                "cited_primary_group_recall": sum(bool(g & cited) for g in groups) / len(groups),
            }
        )
    return metrics


def run_evaluation(
    cases: list[dict],
    retriever,
    client,
    models: list[str],
    run_dir,
    use_cache: bool = True,
    progress=print,
) -> dict:
    started = time.perf_counter()
    rows = []
    graph = load_generation_graph(retriever)
    for index, case in enumerate(cases, 1):
        progress(f"Retrieval {index}/{len(cases)}: {case['uid']}")
        retrieved, hit = retrieval_for(
            case, retriever, ROOT / "artifacts/generation/retrieval", use_cache
        )
        context = prepare_context(
            case["query"],
            retrieved,
            case["task"],
            client.config,
            graph,
        )
        for model in models:
            progress(f"Generation: {model}, {case['uid']}")
            row = {
                "case_id": case["uid"],
                "task": case["task"],
                "query": case["query"],
                "requested_model": model,
                "context": context,
                "retrieval_cache_hit": hit,
                "recorded_retrieval_timings": retrieved.get("timings", {}),
            }
            try:
                generated = generate_answer(context, client, model=model, allow_fallback=False)
                context, generated = recover_answer(
                    context,
                    generated,
                    retrieved,
                    client,
                    retriever,
                    graph,
                    task=case["task"],
                    model=model,
                    allow_fallback=False,
                )
                row["context"] = context
                row.update(generated)
                row["metrics"] = score_case(case, context, generated)
                row["run_status"] = (
                    "OK" if generated["validation"]["valid"] else "VALIDATION_FAILED"
                )
            except LLMError as exc:
                row.update(
                    {
                        "run_status": "PROVIDER_ERROR",
                        "http_status": exc.status,
                        "error_code": exc.error_code,
                        "retry_after": exc.retry_after,
                    }
                )
            rows.append(row)
            write_json(run_dir / "results.json", {"rows": rows, "complete": False})
    report = {
        "complete": True,
        "policy_hash": digest(retriever.unified_policy),
        "snapshot": retriever.snapshot,
        "profile": retriever.profile,
        "sample_count": len(cases),
        "model_count": len(models),
        "dataset_split": sorted({c.get("split", "custom") for c in cases}),
        "dataset_sample_hash": digest(cases),
        "elapsed_ms": (time.perf_counter() - started) * 1000,
        "limits": [
            "Small diagnostic sample, not a model ranking benchmark",
            "QA has source labels, not reference answers; correctness is not scored",
            "Exact quotes do not prove that the cited passage entails the answer",
            "Previously inspected Test cases are regression evidence",
            "Cached retrieval timings are historical measurements",
        ],
        "rows": rows,
    }
    write_json(run_dir / "results.json", report)
    return report


def summary_rows(report: dict) -> list[dict]:
    return [
        {
            "task": r["task"],
            "case_id": r["case_id"],
            "model": r["requested_model"],
            "run_status": r["run_status"],
            "answer_status": r.get("answer", {}).get("status"),
            "suggested_hs": r.get("answer", {}).get("suggested_hs_code"),
            "key_slot": r.get("generation", {}).get("key_slot"),
            "generation_ms": r.get("generation", {}).get("elapsed_ms"),
            **r.get("metrics", {}),
        }
        for r in report["rows"]
    ]
