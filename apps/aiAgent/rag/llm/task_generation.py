"""Goal-scoped answers with one batched review and a shared bounded call budget."""

import json
import re
from copy import deepcopy
from time import perf_counter

from rag.llm.disambiguation import review_scope
from rag.llm.errors import LLMError
from rag.llm.evidence import model_candidate
from rag.llm.task_validation import (
    code_claim_errors,
    decode_task_answer,
    item_context,
    item_quote_errors,
    render_task_answer,
)
from rag.llm.validation import schema_errors, validate_answer
from rag.prompts.task_answering import (
    TASK_ANSWER_SCHEMA,
    TASK_REVIEW_PROMPT,
    TASK_REVIEW_SCHEMA,
)

MAX_ANSWER_CALLS = 5  # Shared by draft/review repairs and the optional recovery round.


class TaskRun:
    def __init__(self, client, model, allow_fallback, remaining):
        self.client, self.model, self.allow_fallback = client, model, allow_fallback
        self.remaining = remaining
        self.calls: list[dict] = []
        self.validation_ms = 0.0

    def request(self, messages, schema, checker, phase):
        messages = list(messages)
        decoded, errors, payload = None, ["Ngân sách gọi model đã hết."], {}
        for attempt in range(min(2, self.remaining)):
            self.remaining -= 1
            tick = perf_counter()
            try:
                generation = self.client.complete(
                    messages,
                    schema,
                    model=self.model,
                    allow_fallback=self.allow_fallback if not attempt else False,
                )
            except LLMError as exc:
                self.calls.append(
                    {
                        "phase": phase,
                        "elapsed_ms": (perf_counter() - tick) * 1000,
                        "error_code": exc.error_code,
                        "http_status": exc.status,
                    }
                )
                return {}, None, ["Dịch vụ model chưa hoàn thành kiểm tra."]
            self.model = generation.get("model", self.model)
            entry = {**generation, "phase": phase, "elapsed_ms": (perf_counter() - tick) * 1000}
            self.calls.append(entry)
            validation_started = perf_counter()
            try:
                payload = json.loads(generation["content"])
                decoded, errors = checker(payload)
            except (ValueError, KeyError, TypeError):
                decoded, errors = None, ["Phản hồi không đúng JSON bắt buộc."]
            self.validation_ms += (perf_counter() - validation_started) * 1000
            if generation.get("finish_reason") != "stop":
                errors.append("Phản hồi model chưa hoàn tất bình thường.")
            entry["validation_errors"] = errors
            if not errors:
                break
            messages.extend(
                [
                    {"role": "assistant", "content": generation["content"]},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "repair_errors": errors,
                                "repair_instruction": (
                                    "Sửa trực tiếp các mục bị báo lỗi trong repair_errors; "
                                    "giữ nguyên mọi kết quả/mục đã hợp lệ."
                                ),
                            },
                            ensure_ascii=False,
                        ),
                    },
                ]
            )
        return payload, decoded, errors


def blocked(row: dict, reason: str) -> dict:
    return {
        **row,
        "status": "REQUIRES_REVIEW",
        "suggested_hs_code": "",
        "answer": reason,
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": [],
        "review_valid": False,
    }


def review_jobs(rows: list[dict], context: dict) -> tuple[list[dict], dict]:
    from rag.llm.context import _model_candidate_evidence

    jobs, scopes = [], {}
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    items = {i["id"]: i for i in context["request"]["items"]}
    for row in rows:
        if row["status"] != "RECOMMENDATION":
            continue
        original = row["suggested_hs_code"]
        scoped = item_context(context, row["item_id"], row["level"], original)
        selection = [
            c["code"]
            for c in scoped["candidate_evidence"]
            if c["code"] in scoped["allowed_hs_codes"]
            and (row["level"] != 8 or c["code"][:6] == original[:6])
        ]
        groups = review_scope(scoped, original)
        scopes[row["result_id"]] = (scoped, row, selection)
        jobs.append(
            {
                "result_id": row["result_id"],
                "objective": goals[row["objective_id"]],
                "item": items[row["item_id"]],
                "proposed_answer": {"code": original, "claims": row["claims"]},
                "selection_codes": selection,
                "candidate_evidence": [
                    model_candidate(c, context["sources"])
                    for c in _model_candidate_evidence(scoped["candidate_evidence"])
                ],
                "review_scope": groups,
                "required_branch_groups": [g for g in groups if g["branch_options"]],
                "allowed_fact_ids": [s["id"] for s in scoped["user_context"]["statements"]],
            }
        )
    return jobs, scopes


def _review_payload(value: dict, context: dict, scopes: dict) -> tuple[dict, list[str]]:
    from rag.llm.answering import check_product_review

    errors = schema_errors(value, TASK_REVIEW_SCHEMA)
    if errors:
        return {}, errors
    reviews = value["reviews"]
    ids = [r["result_id"] for r in reviews]
    if set(ids) != set(scopes) or len(ids) != len(set(ids)):
        return {}, ["reviews phải kiểm tra đúng một lần mỗi result_id đã cấp."]
    checked = {}
    for value_row in reviews:
        rid, code = value_row["result_id"], value_row["selected_code"]
        scoped, proposed, selection = scopes[rid]
        if code not in selection:
            errors.append(f"{rid}: Mã chọn lại không có trong selection_codes đã xác minh.")
            continue
        candidate = next(c for c in scoped["candidate_evidence"] if c["code"] == code)
        raw = value_row["review"]
        foreign = item_quote_errors(
            [
                q
                for key in ["condition_checks", "candidate_assessments", "branch_checks"]
                for check in raw[key]
                for q in check["user_quotes"]
            ],
            scoped,
        )
        if foreign:
            errors.extend(f"{rid}: {e}" for e in foreign)
            continue
        candidate_answer = {**proposed, "suggested_hs_code": code}
        answer, decoded, row_errors = check_product_review(
            raw, scoped, candidate, candidate_answer, {s["label"] for s in context["sources"]}
        )
        if decoded and raw["status"] == "SUPPORTED":
            labels = {c["source_label"] for c in decoded["condition_checks"]}
            citations = [
                {"label": s["label"], "quote": s["text"]}
                for s in context["sources"]
                if s["label"] in labels
            ]
            text = decoded["reason"] + " " + " ".join(f"[{c['label']}]" for c in citations)
            answer = {**candidate_answer, "answer": text, "citations": citations}
            row_errors.extend(
                validate_answer(
                    {
                        k: answer[k]
                        for k in [
                            "status",
                            "answer",
                            "suggested_hs_code",
                            "alternatives",
                            "citations",
                            "missing_information",
                            "missing_legal_evidence",
                        ]
                    },
                    scoped,
                )["errors"]
            )
            row_errors.extend(
                code_claim_errors(
                    [{"kind": "CONCLUSION", "text": decoded["reason"]}], code, context
                )
            )
        if row_errors:
            errors.extend(f"{rid}: {e}" for e in row_errors)
        else:
            checked[rid] = {
                **proposed,
                **answer,
                "review_valid": True,
                "reselected_from": proposed["suggested_hs_code"]
                if code != proposed["suggested_hs_code"]
                else "",
                "review": decoded,
                "verified_path": [
                    {"code": n["code"], "level": n["level"]}
                    for n in candidate["hierarchy"]["chain"]
                ],
                "selected_source": {
                    "snapshot": context.get("snapshot"),
                    "source_id": next(
                        s["id"]
                        for s in context["sources"]
                        if s["label"] == candidate["wording_label"]
                    ),
                },
            }
    return checked, list(dict.fromkeys(errors))


def review_results(rows: list[dict], context: dict, run: TaskRun) -> tuple[list[dict], dict]:
    jobs, scopes = review_jobs(rows, context)
    if not jobs:
        return rows, {}
    schema = deepcopy(TASK_REVIEW_SCHEMA)
    schema["properties"]["reviews"]["maxItems"] = len(jobs)
    branch_schema = schema["properties"]["reviews"]["items"]["properties"]["review"]["properties"][
        "branch_checks"
    ]
    parents = sorted({g["parent_code"] for job in jobs for g in job["required_branch_groups"]})
    if parents:
        branch_schema["items"]["properties"]["parent_code"]["enum"] = parents
    else:
        branch_schema["maxItems"] = 0
    labels = {
        label
        for scoped, row, _ in scopes.values()
        for candidate in scoped["candidate_evidence"]
        for label in [*candidate["required_citation_labels"], *candidate["related_note_labels"]]
    }
    labels.update(c["label"] for _, row, _ in scopes.values() for c in row["citations"])
    payload = {
        "jobs": jobs,
        "user_context": context["user_context"],
        "sources": [
            {k: s[k] for k in ["evidence_id", "code", "chunk_type", "text"] if k in s}
            for s in context["sources"]
            if s["label"] in labels
        ],
    }
    _, checked, errors = run.request(
        [
            {"role": "system", "content": TASK_REVIEW_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        schema,
        lambda v: _review_payload(v, context, scopes),
        "product_review",
    )
    checked = checked or {}
    if run.calls and run.calls[-1].get("finish_reason") != "stop":
        checked = {}
    updated = [
        checked.get(
            r["result_id"],
            blocked(r, "Kiểm tra kết luận chưa hoàn tất hợp lệ; xem diagnostic lỗi hệ thống.")
            if r["result_id"] in scopes
            else r,
        )
        for r in rows
    ]
    return updated, {"valid": not errors, "errors": errors, "checked_results": list(checked)}


def _fill_missing(rows: list[dict], context: dict) -> list[dict]:
    rows = list({(r["objective_id"], r["item_id"]): r for r in rows}.values())
    actual = {(r["objective_id"], r["item_id"]) for r in rows}
    for goal in context["request"]["objectives"]:
        for item in goal["item_ids"] if goal["kind"] == "CLASSIFY" else [""]:
            if (goal["id"], item) not in actual:
                rows.append(
                    blocked(
                        {
                            "result_id": f"R{len(rows) + 1}",
                            "objective_id": goal["id"],
                            "item_id": item,
                            "level": goal["level"],
                            "kind": goal["kind"],
                            "required": goal["required"],
                        },
                        "Mục tiêu này chưa có phản hồi hợp lệ.",
                    )
                )
    return rows


def _resolve_levels(rows: list[dict]) -> list[dict]:
    for index, row in enumerate(rows):
        if row["kind"] != "CLASSIFY":
            continue
        lower = [
            r
            for r in rows
            if r["kind"] == "CLASSIFY"
            and r["item_id"] == row["item_id"]
            and 0 < r["level"] < row["level"]
        ]
        if any(
            r["required"] and (r["status"] != "RECOMMENDATION" or not r.get("review_valid"))
            for r in lower
        ):
            rows[index] = blocked(
                row,
                "Chưa xét mã chi tiết khi nhóm hoặc phân nhóm bắt buộc của cùng mặt hàng chưa được xác định.",
            )
            continue
        path = {n["level"]: n["code"] for n in row.get("verified_path", [])}
        if row["status"] == "RECOMMENDATION" and any(
            r.get("review_valid")
            and r["status"] == "RECOMMENDATION"
            and path.get(r["level"]) != r["suggested_hs_code"]
            for r in lower
        ):
            rows[index] = blocked(
                row, "Kết quả mã chi tiết mâu thuẫn với nhóm đã được kiểm tra của cùng mặt hàng."
            )
    return rows


def _resolve_comparisons(rows: list[dict], context: dict) -> list[dict]:
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    checked = {
        (r["objective_id"], r["item_id"]): r
        for r in rows
        if r["kind"] == "CLASSIFY" and r["status"] == "RECOMMENDATION" and r.get("review_valid")
    }
    for index, row in enumerate(rows):
        if row["kind"] == "CLASSIFY":
            continue
        goal = goals[row["objective_id"]]
        if row.get("depends_on") and not all(tuple(key) in checked for key in row["depends_on"]):
            rows[index] = blocked(
                row, "Phần kết luận này phụ thuộc kết quả phân loại chưa hoàn tất."
            )
        if (
            goal["kind"] != "COMPARE"
            or not goal["level"]
            or not re.search(r"cùng|chung|khác", goal["anchor"], re.I)
            or len(goal["item_ids"]) < 2
        ):
            continue
        items = [
            max(
                (r for r in checked.values() if r["item_id"] == item),
                key=lambda r: r["level"],
                default=None,
            )
            for item in goal["item_ids"]
        ]
        if any(r is None for r in items):
            if any(
                g["kind"] == "CLASSIFY" and set(goal["item_ids"]) <= set(g["item_ids"])
                for g in goals.values()
            ):
                rows[index] = blocked(
                    row,
                    "Chưa đủ kết quả phân loại đã kiểm tra của từng mặt hàng để xác nhận so sánh mã.",
                )
            continue
        paths = [{n["level"]: n["code"] for n in r["verified_path"]} for r in items if r]
        levels = set.intersection(*(set(p) for p in paths))
        usable = [level for level in levels if level <= goal["level"]]
        if not usable:
            continue
        level = max(usable)
        codes = [p[level] for p in paths]
        same = len(set(codes)) == 1
        if same and level < goal["level"]:
            rows[index] = blocked(
                row,
                "Cùng nhóm ở cấp tổng quát chưa đủ để khẳng định cùng mã ở cấp chi tiết được hỏi.",
            )
            continue
        citations = {c["label"]: c for r in items if r for c in r["citations"]}
        text = (
            ("Các mặt hàng có cùng" if same else "Các mặt hàng có khác")
            + f" mã ở cấp {level} số: "
            + "; ".join(
                f"{item}: {code}" for item, code in zip(goal["item_ids"], codes, strict=True)
            )
            + "."
        )
        if level < goal["level"]:
            text += (
                f" Vì đã khác cấp {level} số, chúng không thể dùng chung mã cấp {goal['level']} số."
            )
        text += " " + " ".join(f"[{label}]" for label in citations)
        rows[index] = {
            **row,
            "status": "ANSWERED",
            "answer": text,
            "suggested_hs_code": "",
            "citations": list(citations.values()),
            "missing_information": [],
            "missing_legal_evidence": [],
            "derived_from_reviewed_results": [r["result_id"] for r in items if r],
        }
    return rows


def generate_task_answer(
    context: dict, client, *, model=None, allow_fallback=True, remaining=MAX_ANSWER_CALLS
) -> dict:
    started = perf_counter()
    run = TaskRun(client, model, allow_fallback, remaining)
    payload, rows, errors = run.request(
        context["messages"],
        TASK_ANSWER_SCHEMA,
        lambda value: decode_task_answer(value, context),
        "answer",
    )
    rows = _fill_missing(rows or [], context)
    if run.calls and run.calls[-1].get("finish_reason") != "stop":
        rows = [blocked(r, "Phản hồi model chưa hoàn tất bình thường.") for r in rows]
    rows = [
        r
        if r.get("valid", True)
        else blocked(r, "Phản hồi mục tiêu chưa qua kiểm tra dữ kiện hoặc nguồn.")
        for r in rows
    ]
    rows, review = review_results(rows, context, run)
    rows = _resolve_levels(rows)
    rows = _resolve_comparisons(rows, context)
    answer = render_task_answer(rows, context)
    cited = {c["label"] for c in answer["citations"]}
    timings = {
        "llm_ms": sum(c["elapsed_ms"] for c in run.calls),
        "answer_llm_ms": sum(c["elapsed_ms"] for c in run.calls if c["phase"] == "answer"),
        "product_review_llm_ms": sum(
            c["elapsed_ms"] for c in run.calls if c["phase"] == "product_review"
        ),
        "decision_review_llm_ms": 0,
        "validation_ms": run.validation_ms,
        "total_ms": (perf_counter() - started) * 1000,
    }
    generation = {
        "model": run.model,
        "provider": next((c.get("provider") for c in run.calls if c.get("provider")), None),
        "elapsed_ms": timings["llm_ms"],
        "application_calls": len(run.calls),
        "remaining_calls": run.remaining,
        "attempts": run.calls,
        "task_review": review,
        "fallback_used": any(c.get("fallback_used") for c in run.calls),
        "failures": [f for c in run.calls for f in c.get("failures", [])],
        "usage": {
            k: sum(c.get("usage", {}).get(k, 0) for c in run.calls)
            for k in ["prompt_tokens", "completion_tokens", "total_tokens"]
        },
        "evidence_gaps": payload.get("evidence_gaps", []) if not errors else [],
    }
    reasons = [*errors, *review.get("errors", [])]
    return {
        "answer": answer,
        "generation": generation,
        "timings": timings,
        "validation": {
            "valid": True,
            "errors": [],
            "cited_labels": sorted(cited),
            "cited_source_ids": [s["id"] for s in context["sources"] if s["label"] in cited],
            "semantic_grounding": "MODEL_REVIEWED" if review.get("valid") else "NOT_EVALUATED",
            "task_completion": not any(
                r["required"] and r["status"] not in {"ANSWERED", "RECOMMENDATION"} for r in rows
            ),
            "boundary_errors": [],
        },
        "diagnostics": {
            "stage": "task_validation",
            "code": "SYSTEM_VALIDATION_ERROR",
            "reasons": reasons,
            "candidate_hs_code": "",
            "source_labels": sorted(cited),
        }
        if reasons
        else {},
    }
