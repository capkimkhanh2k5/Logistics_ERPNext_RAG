"""Goal-scoped answers with one batched review and a shared bounded call budget."""

import json
import re
from copy import deepcopy
from time import perf_counter

from rag.llm.disambiguation import review_scope
from rag.llm.errors import LLMError
from rag.llm.evidence import model_candidate, source_registry, unique_clarifications
from rag.llm.task_validation import (
    code_claim_errors,
    decode_task_answer,
    item_context,
    item_quote_errors,
    render_task_answer,
)
from rag.llm.validation import match_user_quote, schema_errors, validate_answer
from rag.prompts.task_answering import (
    TASK_ANSWER_SCHEMA,
    TASK_REVIEW_PROMPT,
    TASK_REVIEW_SCHEMA,
)
from rag.retrieval.request_plan import referenced_codes

MAX_ANSWER_CALLS = 5  # Shared by draft/review repairs and the optional recovery round.


class TaskRun:
    def __init__(self, client, model, allow_fallback, remaining):
        self.client, self.model, self.allow_fallback = client, model, allow_fallback
        self.remaining = remaining
        self.calls: list[dict] = []
        self.validation_ms = 0.0

    def request(self, messages, schema, checker, phase, *, reserve=0):
        messages = list(messages)
        decoded, errors, payload = None, ["Ngân sách gọi model đã hết."], {}
        for attempt in range(min(2, max(0, self.remaining - reserve))):
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
                if generation.get("finish_reason") == "stop":
                    decoded, errors = checker(payload)
                else:
                    decoded, errors = None, ["Phản hồi model chưa hoàn tất bình thường."]
            except (ValueError, KeyError, TypeError):
                decoded, errors = None, ["Phản hồi không đúng JSON bắt buộc."]
            self.validation_ms += (perf_counter() - validation_started) * 1000
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
        "hs_candidates": [],
    }


def _unreviewed_fallback(row: dict, scoped: dict, reason: str) -> dict:

    labels = {c["label"] for c in row.get("citations", [])}
    sources = [source for source in scoped["sources"] if source["label"] in labels]
    result = blocked(row, reason)
    if row.get("valid") and sources:
        result["answer"] += " Nguồn tham khảo, chưa xác nhận áp dụng cho hàng hóa: " + " ".join(
            f"{source['text']} [{source['label']}]" for source in sources
        )
        result["citations"] = [
            {"label": source["label"], "quote": source["text"]} for source in sources
        ]
    return result


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
        if row.get("candidate_only"):
            peers = {
                c["code"]: c
                for c in [
                    *scoped["candidate_evidence"],
                    *context["candidate_evidence"],
                    *context.get("comparison_candidates", []),
                ]
                if c["code"] in row["shortlist_codes"] or c in scoped["candidate_evidence"]
            }
            scoped["candidate_evidence"] = list(peers.values())
            scoped["candidate_comparison"] = [
                {
                    "parent_code": "",
                    "codes": list(peers),
                    "missing_codes": [],
                    "branch_options": [],
                },
                *[g for g in scoped["candidate_comparison"] if g["parent_code"]],
            ]
        groups = review_scope(scoped, original)
        scopes[row["result_id"]] = (scoped, row, selection)
        jobs.append(
            {
                "result_id": row["result_id"],
                "shortlist_member": row.get("candidate_only", False),
                "objective": goals[row["objective_id"]],
                "item": items[row["item_id"]],
                "proposed_answer": {
                    "code": original,
                    "claims": row["claims"],
                    "clarifications": row.get("draft_clarifications", []),
                },
                "selection_codes": selection,
                "candidate_evidence": [
                    model_candidate(c, context["sources"])
                    for c in _model_candidate_evidence(scoped["candidate_evidence"])
                ],
                "review_scope": groups,
                "required_comparison_codes": sorted(
                    {code for group in groups for code in group["codes"]}
                ),
                "required_branch_groups": [g for g in groups if g["branch_options"]],
                "allowed_fact_ids": [s["id"] for s in scoped["user_context"]["statements"]],
            }
        )
    return jobs, scopes


def _canonical_quotes(raw: dict, scoped: dict) -> dict:
    """Replace model quotes by the authentic user slices they refer to, when one exists."""
    statements = {s["id"]: s["text"] for s in scoped["user_context"]["statements"]}
    review = deepcopy(raw)
    for key in ["condition_checks", "candidate_assessments", "branch_checks"]:
        for check in review.get(key, []):
            texts = [statements[sid] for sid in check.get("fact_ids", []) if sid in statements]
            check["user_quotes"] = [
                match_user_quote(quote, texts) or quote for quote in check.get("user_quotes", [])
            ]
    return review


def _confirmed_analysis(proposed: dict, code: str, scoped: dict) -> tuple[str, list[dict]]:
    """Keep the draft's cited legal analysis only when review confirmed the same code."""
    from rag.llm.evidence import render_claims

    if code != proposed["suggested_hs_code"] or not proposed.get("valid"):
        return "", []
    claims = [c for c in proposed.get("claims", []) if c["kind"] == "LEGAL_ANALYSIS"]
    if not claims or code_claim_errors(claims, code, scoped):
        return "", []
    text, citations, errors = render_claims(claims, scoped)
    return ("", []) if errors or not text else (text, citations)


def _review_payload(value: dict, context: dict, scopes: dict) -> tuple[dict, list[str]]:
    from rag.llm.answering import check_product_review

    if (
        not isinstance(value, dict)
        or set(value) != {"reviews"}
        or not isinstance(value.get("reviews"), list)
    ):
        return {}, schema_errors(value, TASK_REVIEW_SCHEMA)
    errors = []
    reviews = value["reviews"]
    ids = [r.get("result_id") for r in reviews if isinstance(r, dict)]
    if any(not isinstance(rid, str) for rid in ids):
        return {}, ["reviews phải dùng result_id chuỗi đã cấp."]
    if set(ids) != set(scopes) or len(ids) != len(set(ids)) or len(ids) != len(reviews):
        return {}, ["reviews phải kiểm tra đúng một lần mỗi result_id đã cấp."]
    checked = {}
    for value_row in reviews:
        value_row = deepcopy(value_row)
        raw_review = value_row.get("review")
        grouped = (
            raw_review.get("candidate_group_assessments", [])
            if isinstance(raw_review, dict)
            else []
        )
        for group in grouped if isinstance(grouped, list) else []:
            codes = group.get("codes") if isinstance(group, dict) else None
            if isinstance(codes, list) and all(isinstance(code, str) for code in codes):
                # Repeated codes within ONE identical proof carry no extra assertion.
                group["codes"] = list(dict.fromkeys(codes))
        row_errors = schema_errors(value_row, TASK_REVIEW_SCHEMA["properties"]["reviews"]["items"])
        if row_errors:
            errors.extend(f"{value_row['result_id']}: {e}" for e in row_errors)
            continue
        rid, code = value_row["result_id"], value_row["selected_code"]
        scoped, proposed, selection = scopes[rid]
        if code not in selection:
            errors.append(f"{rid}: Mã chọn lại không có trong selection_codes đã xác minh.")
            continue
        candidate = next(c for c in scoped["candidate_evidence"] if c["code"] == code)
        raw = deepcopy(value_row["review"])
        grouped = raw.pop("candidate_group_assessments", [])
        raw["candidate_assessments"].extend(
            {**{k: v for k, v in group.items() if k != "codes"}, "code": peer}
            for group in grouped
            for peer in group["codes"]
        )
        raw = _canonical_quotes(raw, scoped)
        # An unavailable peer is a source gap, never a model-proven exclusion.
        missing_peers = {
            code for group in review_scope(scoped, code) for code in group["missing_codes"]
        }
        if missing_peers:
            raw.update(
                status="INSUFFICIENT_LEGAL_EVIDENCE",
                reason="Chưa đủ nguồn của các nhánh đối chứng để phân định ứng viên.",
                clarifications=[],
                missing_legal_evidence=[
                    "Thiếu nguồn đối chứng trong ngữ cảnh: " + ", ".join(sorted(missing_peers))
                ],
            )
            raw["candidate_assessments"] = [
                {
                    **assessment,
                    "assessment": "INSUFFICIENT_LEGAL_EVIDENCE",
                    "evidence_ids": [],
                    "fact_ids": [],
                    "user_quotes": [],
                }
                if assessment["code"] in missing_peers
                else assessment
                for assessment in raw["candidate_assessments"]
            ]
        if raw["status"] != "SUPPORTED":
            # The selected code belongs in the structured candidate field. Its
            # occurrence in a review's explanation is a reference, not a new proposal.
            references = {code} | {
                peer for group in review_scope(scoped, code) for peer in group["codes"]
            }
            references.update(node["code"] for node in candidate["hierarchy"]["chain"])
            forms = {}
            for ref in references:
                for form in {
                    ref,
                    ".".join([ref[:4], *[ref[i : i + 2] for i in range(4, len(ref), 2)]]),
                } | ({ref[:2] + "." + ref[2:]} if len(ref) == 4 else set()):
                    forms[form] = "ứng viên đang xét" if ref == code else "nhánh đối chứng"
            raw["reason"] = re.sub(
                r"(?<!\d)(?:"
                + "|".join(re.escape(form) for form in sorted(forms, key=len, reverse=True))
                + r")(?!\d|\.\d)",
                lambda match: forms[match[0]],
                raw["reason"],
            )
        if code != proposed["suggested_hs_code"] and raw["status"] != "SUPPORTED":
            errors.append(
                f"{rid}: Chỉ được đổi selected_code sang ứng viên khác khi ứng viên mới đạt SUPPORTED; giữ nguyên {proposed['suggested_hs_code']} nếu kết quả là {raw['status']}."
            )
            continue
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
            reason = (
                decoded["reason"]
                + " "
                + " ".join(f"[{s['label']}]" for s in context["sources"] if s["label"] in labels)
            )
            analysis, analysis_citations = _confirmed_analysis(proposed, code, scoped)
            labels.update(c["label"] for c in analysis_citations)
            citations = [
                {"label": s["label"], "quote": s["text"]}
                for s in context["sources"]
                if s["label"] in labels
            ]
            text = f"{analysis} {reason}" if analysis else reason
            answer = {
                **candidate_answer,
                "status": "RECOMMENDATION",
                "answer": text,
                "citations": citations,
                "missing_information": [],
                "missing_legal_evidence": [],
            }
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
                    {
                        **scoped,
                        "structured_code_claims": [
                            {"kind": "CONCLUSION", "text": decoded["reason"]}
                        ],
                    },
                )["errors"]
            )
            row_errors.extend(
                code_claim_errors(
                    [{"kind": "CONCLUSION", "text": decoded["reason"]}], code, context
                )
            )
        if decoded and proposed.get("candidate_only"):
            covered = {c["source_label"] for c in decoded["condition_checks"]}
            if not set(candidate["required_citation_labels"]) <= covered:
                row_errors.append(
                    "Mỗi ứng viên phải kiểm tra mọi điều kiện bắt buộc, kể cả khi thiếu dữ kiện."
                )
        if decoded:
            row_errors.extend(
                code_claim_errors(
                    [{"kind": "CONCLUSION", "text": decoded["reason"]}],
                    code if raw["status"] == "SUPPORTED" else "",
                    context,
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
                "review_clarifications": [
                    {
                        **q,
                        "source_ids": [
                            source_registry(context)[eid]["id"] for eid in q["evidence_ids"]
                        ],
                    }
                    for q in unique_clarifications(raw["clarifications"])
                ],
                "reviewed_code": code,
                "candidate_assessments": raw.get("candidate_assessments", []),
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
    from rag.llm.analysis_review import (
        ANALYSIS_PROMPT,
        ANALYSIS_SCHEMA,
        analysis_jobs,
        check_analyses,
    )

    jobs, scopes = review_jobs(rows, context)
    analyses = analysis_jobs(rows, context)
    if not jobs and not analyses:
        return rows, {}
    schema = deepcopy(TASK_REVIEW_SCHEMA)
    if analyses:
        schema["properties"]["analysis_reviews"] = ANALYSIS_SCHEMA
        schema["required"].append("analysis_reviews")
    schema["properties"]["reviews"]["minItems"] = 1 if jobs else 0
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
    labels.update(
        label for _, row, _ in scopes.values() for label in row.get("review_evidence_labels", [])
    )
    analysis_evidence = {
        eid for job in analyses for claim in job["claims"] for eid in claim["evidence_ids"]
    }
    labels.update(s["label"] for s in context["sources"] if s["evidence_id"] in analysis_evidence)
    payload = {
        "jobs": jobs,
        "analysis_jobs": analyses,
        "user_context": context["user_context"],
        "sources": [
            {k: s[k] for k in ["evidence_id", "code", "chunk_type", "text"] if k in s}
            for s in context["sources"]
            if s["label"] in labels
        ],
    }
    retained = {}
    superseded_errors = []

    def check(value):
        # Validate the dynamic batch schema, then use the original classification decoder.
        if not isinstance(value, dict):
            return retained, ["Batch review phải là JSON object."]
        if "reviews" not in value:
            return retained, ["Batch review thiếu trường reviews bắt buộc."]
        if not scopes and value["reviews"] != []:
            return retained, ["Không được tự tạo job phân loại khi chỉ có analysis_jobs."]
        if set(value) - set(schema["properties"]):
            return retained, ["Batch review chứa trường ngoài schema được cấp."]
        checked, errors = (
            _review_payload({"reviews": value.get("reviews")}, context, scopes)
            if scopes
            else ({}, [])
        )
        if analyses:
            reviewed_analyses, analysis_errors = check_analyses(
                value.get("analysis_reviews", []), analyses, rows, context
            )
            checked.update(reviewed_analyses)
            errors.extend(analysis_errors)
            obsolete = {
                rid
                for rid, (_, row, _) in scopes.items()
                if any(
                    analysis.get("application_evidence_gap")
                    and row["item_id"]
                    in next(j["item_ids"] for j in analyses if j["result_id"] == aid)
                    and row["level"] >= analysis.get("application_gap_level", 0)
                    for aid, analysis in reviewed_analyses.items()
                )
            }
            superseded_errors.extend(
                error for error in errors if any(error.startswith(f"{rid}:") for rid in obsolete)
            )
            errors = [
                error
                for error in errors
                if not any(error.startswith(f"{rid}:") for rid in obsolete)
            ]
        retained.update(checked)
        errors = [e for e in errors if not any(e.startswith(f"{rid}:") for rid in retained)]
        return dict(retained), errors

    _, checked, errors = run.request(
        [
            {
                "role": "system",
                "content": TASK_REVIEW_PROMPT + (ANALYSIS_PROMPT if analyses else ""),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        schema,
        check,
        "product_review",
    )
    checked = checked or retained
    updated = [
        checked.get(
            r["result_id"],
            _unreviewed_fallback(
                r,
                scopes[r["result_id"]][0] if r["result_id"] in scopes else context,
                "Kiểm tra kết luận chưa hoàn tất hợp lệ; xem diagnostic lỗi hệ thống.",
            )
            if r["result_id"] in scopes or any(j["result_id"] == r["result_id"] for j in analyses)
            else r,
        )
        for r in rows
    ]
    return updated, {
        "valid": not errors,
        "errors": errors,
        "checked_results": list(checked),
        "superseded_errors": list(dict.fromkeys(superseded_errors)),
    }


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


def review_by_level(rows: list[dict], context: dict, run: TaskRun) -> tuple[list[dict], dict]:
    """Review parents before leaves, retaining completed results within the same budget."""
    from rag.llm.shortlist import collapse_rows, expand_rows

    pending, completed, reports = list(rows), [], []
    while pending:
        ready = [
            row
            for row in pending
            if row["kind"] != "CLASSIFY"
            or not any(
                p["kind"] == "CLASSIFY"
                and p["required"]
                and p["item_id"] == row["item_id"]
                and 0 < p["level"] < row["level"]
                for p in pending
            )
        ]
        deferred_ids = {row["result_id"] for row in pending} - {row["result_id"] for row in ready}
        pending = [row for row in pending if row["result_id"] in deferred_ids]
        eligible = []
        for row in ready:
            parents = [
                p
                for p in completed
                if p["kind"] == "CLASSIFY"
                and p["required"]
                and p["item_id"] == row["item_id"]
                and 0 < p["level"] < row["level"]
            ]
            if any(p["status"] != "RECOMMENDATION" or not p.get("review_valid") for p in parents):
                completed.append(
                    {**row, "candidate_codes": [], "hs_candidates": []}
                    if row.get("clarifications_inherited")
                    and row["status"] == "MISSING_PRODUCT_INFO"
                    else blocked(
                        row,
                        "Chưa xét mã chi tiết khi nhóm cha chưa được xác định; cần xử lý điều kiện phân biệt ở nhóm cha trước.",
                    )
                )
            else:
                eligible.append(row)
        if eligible:
            expanded, groups = expand_rows(eligible, context)
            reviewed, report = review_results(expanded, context, run)
            completed.extend(collapse_rows(eligible, reviewed, groups, context))
            if report:
                reports.append(report)
    by_id = {row["result_id"]: row for row in completed}
    return [by_id[row["result_id"]] for row in rows], {
        "valid": bool(reports) and all(report["valid"] for report in reports),
        "errors": [error for report in reports for error in report["errors"]],
        "checked_results": [rid for report in reports for rid in report["checked_results"]],
        "superseded_errors": [
            error for report in reports for error in report.get("superseded_errors", [])
        ],
        "waves": len(reports),
    }


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
            if (
                row.get("required")
                and row.get("valid")
                and row["status"] == "MISSING_PRODUCT_INFO"
                and all(r["status"] == "MISSING_PRODUCT_INFO" for r in lower if r["required"])
            ):
                continue
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
            if row["kind"] == "EXPLAIN" and row.get("analysis_review_valid"):
                from rag.llm.evidence import render_claims

                independent = {
                    c["claim_index"]
                    for c in row["analysis_checks"]
                    if c["assessment"] in {"REFERENCE", "CONDITIONAL_APPLICATION"}
                }
                claims = [c for i, c in enumerate(row["claims"]) if i in independent]
                if claims:
                    text, citations, _ = render_claims(claims, context)
                    rows[index].update(
                        claims=claims,
                        answer=text
                        + " Chưa xác nhận áp dụng cho hàng hóa khi kết quả phân loại còn chờ bổ sung.",
                        citations=citations,
                        independent_explanation_retained=True,
                    )
        if (
            goal["kind"] != "COMPARE"
            or not goal["level"]
            or not re.search(r"cùng|chung|khác|cả\s+hai|tất\s+cả", goal["anchor"], re.I)
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
            keeps_reference_answer = (
                row.get("valid")
                and row["status"] == "ANSWERED"
                and referenced_codes(goal["anchor"])
                and any(r is not None for r in items)
            )
            if not keeps_reference_answer and any(
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
        reserve=1,
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
    # Do not spend leaf-review jobs while a required parent is already unresolved.
    for index, row in enumerate(rows):
        unresolved = (
            [
                parent
                for parent in rows
                if parent["kind"] == "CLASSIFY"
                and parent["item_id"] == row["item_id"]
                and parent["required"]
                and 0 < parent["level"] < row["level"]
                and parent["status"] != "RECOMMENDATION"
            ]
            if row["kind"] == "CLASSIFY"
            else []
        )
        if unresolved and not row.get("clarifications_inherited"):
            rows[index] = {
                **blocked(
                    row,
                    "Chưa xét mã chi tiết khi nhóm cha còn thiếu căn cứ hoặc dữ kiện phân biệt.",
                ),
                "candidate_codes": [],
            }
    rows, review = review_by_level(rows, context, run)
    from rag.llm.analysis_review import resolve_analysis_gaps

    rows = resolve_analysis_gaps(rows, context)
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
        "discarded_candidate_codes": [
            {"result_id": row["result_id"], "codes": row["discarded_candidate_codes"]}
            for row in rows
            if row.get("discarded_candidate_codes")
        ],
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
