"""Reconnect evidence gaps to retrieval without another model-driven routing step."""

import re
from copy import deepcopy

from rag.retrieval.evidence_recovery import recover_evidence
from rag.retrieval.request_plan import referenced_codes


def _gaps(context: dict, generated: dict) -> list[dict]:
    explicit = generated["generation"].get("evidence_gaps", [])
    if explicit:
        return explicit
    unresolved = [
        r
        for r in generated["answer"].get("results", [])
        if r["required"] and r["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    ]
    if not unresolved:
        return []
    goals = {g["id"]: g for g in context["request"]["objectives"]}

    def related_codes(row):
        items = goals[row["objective_id"]]["item_ids"]
        checked = {
            r["suggested_hs_code"]
            for r in generated["answer"].get("results", [])
            if r["kind"] == "CLASSIFY"
            and r["item_id"] in items
            and r["status"] == "RECOMMENDATION"
            and r.get("review_valid")
        }
        checked.update(
            r["reviewed_code"]
            for r in generated["answer"].get("results", [])
            if r["kind"] == "CLASSIFY"
            and r["item_id"] in items
            and r.get("reviewed_code")
            and any(s.get("code") == r["reviewed_code"] for s in context["sources"])
        )
        analysis_ids = {
            eid
            for r in generated["answer"].get("results", [])
            if set(goals[r["objective_id"]]["item_ids"]) & set(items)
            for check in r.get("analysis_checks", [])
            for eid in check["evidence_ids"]
        }
        checked.update(
            s["code"]
            for s in context["sources"]
            if s["evidence_id"] in analysis_ids and s.get("code")
        )
        return sorted(checked or referenced_codes(context["question"]))[:6]

    return [
        {
            "anchor": goals[r["objective_id"]]["anchor"],
            "codes": related_codes(r),
            "query": " ".join(r["missing_legal_evidence"])[:200],
            "reason": "Khoảng trống nguồn của mục tiêu chưa hoàn tất.",
            "kind": "APPLICATION" if r.get("application_evidence_gap") else "WORDING",
        }
        for r in unresolved
    ]


def _retain_completed(old_context: dict, old: dict, context: dict, generated: dict) -> dict:
    from rag.llm.task_validation import render_task_answer

    before = {
        (r["objective_id"], r["item_id"]): r
        for r in old["answer"]["results"]
        if r["status"] in {"ANSWERED", "RECOMMENDATION"}
    }
    sources = {s["id"]: s for s in context["sources"]}
    by_label = {s["label"]: s for s in old_context["sources"]}
    rows = generated["answer"]["results"]
    retained_ids: set[str] = set()
    for index, row in enumerate(rows):
        prior = before.get((row["objective_id"], row["item_id"]))
        if row["status"] in {"ANSWERED", "RECOMMENDATION"} or not prior:
            continue
        cited_labels = {c["label"] for c in prior["citations"]}
        cited_labels.update(
            c["label"]
            for candidate in prior.get("hs_candidates", [])
            for c in candidate["citations"]
        )
        if not cited_labels <= by_label.keys():
            continue
        cited = [by_label[label] for label in cited_labels]
        if not all(s["id"] in sources and s["text"] == sources[s["id"]]["text"] for s in cited):
            continue
        mapping = {s["label"]: sources[s["id"]]["label"] for s in cited}
        retained = deepcopy(prior)
        retained["answer"] = re.sub(
            r"\[(S\d+)\]", lambda m: f"[{mapping.get(m[1], m[1])}]", retained["answer"]
        )
        retained["citations"] = [
            {"label": mapping[c["label"]], "quote": c["quote"]} for c in prior["citations"]
        ]
        for check in retained.get("review", {}).get("condition_checks", []):
            check["source_label"] = mapping.get(check["source_label"], check["source_label"])
        for candidate in retained.get("hs_candidates", []):
            for citation in candidate["citations"]:
                citation["label"] = mapping[citation["label"]]
            for condition in candidate["conditions"]:
                condition["source_label"] = mapping[condition["source_label"]]
            candidate["reason"] = re.sub(
                r"\[(S\d+)\]", lambda m: f"[{mapping.get(m[1], m[1])}]", candidate["reason"]
            )
        retained["retained_after_recovery"] = True
        rows[index] = retained
        retained_ids.add(retained.get("result_id") or row.get("result_id") or f"R{index + 1}")
    generated["answer"] = render_task_answer(rows, context)
    labels = {c["label"] for c in generated["answer"]["citations"]}
    generated["validation"].update(
        cited_labels=sorted(labels),
        cited_source_ids=[s["id"] for s in context["sources"] if s["label"] in labels],
    )
    generated["validation"]["task_completion"] = not any(
        r["required"] and r["status"] not in {"ANSWERED", "RECOMMENDATION"} for r in rows
    )
    if retained_ids and generated.get("diagnostics", {}).get("reasons"):
        if not any(r["status"] == "REQUIRES_REVIEW" for r in rows):
            generated["diagnostics"] = {}
        else:
            remaining = [
                reason
                for reason in generated["diagnostics"]["reasons"]
                if not any(reason.startswith(f"{rid}:") for rid in retained_ids)
            ]
            if remaining:
                generated["diagnostics"]["reasons"] = remaining
            else:
                generated["diagnostics"] = {}
    return generated


def recover_answer(
    context: dict,
    generated: dict,
    result: dict,
    client,
    retriever,
    graph,
    *,
    task="auto",
    model=None,
    allow_fallback=True,
) -> tuple[dict, dict]:
    """At most one retrieval correction, sharing the original answer/review call budget."""
    from rag.llm.context import prepare_context
    from rag.llm.task_generation import generate_task_answer

    if context.get("response_protocol") != "goals-v1" or generated["validation"].get(
        "task_completion"
    ):
        return context, generated
    if generated.get("diagnostics", {}).get("code") == "SYSTEM_VALIDATION_ERROR":
        return context, generated
    if generated["generation"].get("recovery"):
        return context, generated
    pending = [
        r
        for r in generated["answer"].get("results", [])
        if r["required"] and r["status"] not in {"ANSWERED", "RECOMMENDATION"}
    ]
    if pending and all(r["status"] == "MISSING_PRODUCT_INFO" for r in pending):
        return context, generated
    gaps = _gaps(context, generated)
    if not gaps:
        return context, generated
    remaining = generated["generation"]["remaining_calls"]
    if remaining < 2:
        generated["generation"]["recovery"] = {
            "rounds": 0,
            "reason": "CALL_BUDGET_EXHAUSTED" if not remaining else "INSUFFICIENT_REVIEW_BUDGET",
        }
        return context, generated
    recovered, metadata = recover_evidence(
        context["question"], result, context, gaps, retriever, graph
    )
    if recovered is None:
        generated["generation"]["recovery"] = metadata
        return context, generated
    updated = prepare_context(context["question"], recovered, task, client.config, graph)
    updated.update(
        {
            k: context[k]
            for k in ["conversation_routing", "packing_ms", "retrieval_timings"]
            if k in context
        }
    )
    final = generate_task_answer(
        updated, client, model=model, allow_fallback=allow_fallback, remaining=remaining
    )
    final = _retain_completed(context, generated, updated, final)
    first, last = generated["generation"], final["generation"]
    last.update(
        application_calls=first["application_calls"] + last["application_calls"],
        elapsed_ms=first["elapsed_ms"] + last["elapsed_ms"],
        usage={k: first["usage"].get(k, 0) + last["usage"].get(k, 0) for k in last["usage"]},
        attempts=[*first["attempts"], *last["attempts"]],
        recovery={
            **metadata,
            "initial_status": generated["answer"]["status"],
            "initial_diagnostics": generated.get("diagnostics", {}),
        },
    )
    for key in final["timings"]:
        final["timings"][key] += generated["timings"].get(key, 0)
    final["timings"]["total_ms"] += metadata.get("elapsed_ms", 0)
    return updated, final
