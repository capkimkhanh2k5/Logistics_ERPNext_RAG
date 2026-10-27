"""Review explanatory and unresolved classification claims in the existing batch."""

import re

from rag.llm.contracts.errors import ContractIssue, scoped_issue
from rag.llm.evidence.evidence import render_claims
from rag.llm.validation.answer import _folded, match_user_quote, schema_errors
from rag.llm.validation.task_validation import item_context, item_quote_errors
from rag.prompts.generation.task_answering import ANALYSIS_REVIEW_SCHEMA


def analysis_jobs(rows: list[dict], context: dict) -> list[dict]:
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    return [
        {
            "result_id": row["result_id"],
            "item_ids": [row["item_id"]]
            if row["kind"] == "CLASSIFY"
            else goals[row["objective_id"]]["item_ids"],
            "objective": goals[row["objective_id"]],
            "application_claim_indices": [
                i
                for i, claim in enumerate(row["claims"])
                if goals[row["objective_id"]]["item_ids"]
                and claim["kind"] != "PRODUCT_FACT"
                and (
                    claim.get("fact_ids")
                    or (
                        row["kind"] == "CLASSIFY"
                        and context.get("reasoning_contract") == "semantic-v1"
                        and claim.get("kind") in {"CONCLUSION", "APPLICATION"}
                    )
                )
            ],
            "coverage_evidence_ids": _requirement_sources(row, rows, context),
            "claims": [{"claim_index": i, **claim} for i, claim in enumerate(row["claims"])],
        }
        for row in rows
        if (
            row["kind"] in {"EXPLAIN", "COMPARE", "REQUIREMENTS"}
            or row["kind"] == "CLASSIFY"
            and (
                context.get("reasoning_contract") == "semantic-v1"
                or row["status"] != "RECOMMENDATION"
            )
        )
        and row["claims"]
        and row.get("valid")
    ]


def _requirement_sources(row: dict, rows: list[dict], context: dict) -> list[str]:
    if row["kind"] != "REQUIREMENTS" or row["status"] != "ANSWERED":
        return []
    goal = next(g for g in context["request"]["objectives"] if g["id"] == row["objective_id"])
    all_rows = [*rows, *context.get("draft_rows", []), *context.get("all_rows", [])]
    primary_rows = [
        r
        for r in all_rows
        if r["kind"] == "CLASSIFY"
        and r["item_id"] in goal["item_ids"]
        and (r.get("suggested_hs_code") or r.get("code"))
        and (not "." in r.get("result_id", "") or r.get("result_id", "").endswith(".C1"))
    ]
    candidate_rows = primary_rows or [
        r
        for r in all_rows
        if r["kind"] == "CLASSIFY"
        and r["item_id"] in goal["item_ids"]
        and (r.get("suggested_hs_code") or r.get("code"))
    ]
    headings = {(r.get("suggested_hs_code") or r.get("code"))[:4] for r in candidate_rows}
    sources = {s["evidence_id"]: s for s in context.get("sources", [])}
    return sorted(
        {
            eid
            for scope in context.get("requirements_scopes", [])
            if scope["objective_id"] == goal["id"]
            and (not headings or scope["heading"] in headings)
            for eid in scope["evidence_ids"]
            if sources.get(eid, {}).get("chunk_type") != "section_note"
            and not (
                sources.get(eid, {}).get("chunk_type") == "tariff_entry"
                and len(sources.get(eid, {}).get("code", "")) < goal.get("level", 8)
            )
        }
    )


def check_analyses(value: list[dict], jobs: list[dict], rows: list[dict], context: dict):
    expected = {job["result_id"]: job for job in jobs}
    if not isinstance(value, list):
        return {}, ["analysis_reviews phải là danh sách các slot đã cấp."]
    errors: list[str] = []
    ids = [
        r["result_id"] for r in value if isinstance(r, dict) and isinstance(r.get("result_id"), str)
    ]
    duplicate = {rid for rid in ids if ids.count(rid) > 1}
    errors.extend(
        ContractIssue(
            f"{rid}: Thiếu analysis review.",
            code="ANALYSIS_COVERAGE_MISSING",
            path=f"{rid}/analysis_reviews",
        )
        for rid in set(expected) - set(ids)
    )
    errors.extend(
        ContractIssue(
            f"{rid}: Analysis review lặp hoặc ngoài phạm vi.",
            code="REVIEW_SLOT_UNKNOWN",
            path=f"{rid}/analysis_reviews",
        )
        for rid in set(ids) - set(expected) | duplicate
    )
    sources = {s["evidence_id"]: s for s in context["sources"]}
    facts = {s["id"]: s["text"] for s in context["user_context"]["statements"]}
    originals = {row["result_id"]: row for row in rows}
    checked = {}
    for review in value:
        if (
            not isinstance(review, dict)
            or review.get("result_id") not in expected
            or review.get("result_id") in duplicate
        ):
            continue
        rid = review["result_id"]
        row_schema_errors = schema_errors(review, ANALYSIS_REVIEW_SCHEMA["items"])
        if row_schema_errors:
            errors.extend(scoped_issue(e, rid) for e in row_schema_errors)
            continue
        claims = {c["claim_index"]: c for c in expected[rid]["claims"]}
        checks = [dict(c) for c in review["checks"]]
        if len(checks) != len(claims) or {c["claim_index"] for c in checks} != set(claims):
            errors.append(f"{rid}: [ANALYSIS_COVERAGE_MISSING] claim_index bị thiếu hoặc lặp.")
            continue
        row_errors = []
        coverage = review.get("coverage_checks", [])
        required_sources = set(expected[rid].get("coverage_evidence_ids", []))
        coverage_ids = [c["evidence_id"] for c in coverage]
        if required_sources and (
            set(coverage_ids) != required_sources or len(coverage_ids) != len(set(coverage_ids))
        ):
            row_errors.append(
                "[REQUIREMENTS_COVERAGE_MISSING] Thiếu hoặc lặp đơn vị điều kiện cần đối chiếu."
            )
        for unit in coverage:
            if unit["evidence_id"] not in sources or set(unit["claim_indices"]) - claims.keys():
                row_errors.append("Đối chiếu độ đầy đủ tham chiếu ngoài phạm vi nguồn/claim.")
            if unit["assessment"] == "COVERED" and not unit["claim_indices"]:
                row_errors.append("Điều kiện được mô tả đầy đủ cần chỉ rõ claim tương ứng.")
        from rag.llm.review.proof_resolution import resolve_analysis

        checks = [
            resolve_analysis(check, claims[check["claim_index"]], context) for check in checks
        ]
        for check in checks:
            claim = claims[check["claim_index"]]
            from rag.llm.contracts.obligations import requests_current

            if (
                context.get("legal_scope") == "SOURCE_SNAPSHOT"
                and check["assessment"] in {"APPLICATION", "REFERENCE", "CONDITIONAL_APPLICATION"}
                and requests_current(claim["text"])
            ):
                check["assessment"] = "INSUFFICIENT_LEGAL_EVIDENCE"
                check["reason"] = "Chưa xác minh hiệu lực hiện hành của nhận định."
            is_fact = claim["kind"] == "PRODUCT_FACT"
            claim_text = _folded(claim["text"])
            if is_fact != (check["assessment"] in {"FACT_SUPPORTED", "FACT_UNSUPPORTED"}):
                row_errors.append(
                    "[FACT_ASSESSMENT_MISMATCH] Dữ kiện cần đánh giá nguồn gốc riêng với nhận định pháp lý."
                )
            if (
                is_fact
                and check["assessment"] == "FACT_SUPPORTED"
                and (
                    not check["fact_ids"]
                    or not check["user_quotes"]
                    or set(check["fact_ids"]) - set(claim["fact_ids"])
                )
            ):
                row_errors.append(
                    "[FACT_PROVENANCE_MISSING] Dữ kiện cần trích đoạn từ chính fact_ids của claim."
                )
            if check["assessment"] == "REFERENCE" and (
                check["claim_index"] in expected[rid].get("application_claim_indices", [])
                or re.search(
                    r"(?:xe|hang hoa|san pham|thiet bi|phuong tien) nay|trong truong hop nay",
                    claim_text,
                )
                and re.search(
                    r"duoc (?:xep|phan loai|coi la|xem la)|thuoc (?:nhom|phan nhom|ma)", claim_text
                )
            ):
                row_errors.append(
                    ContractIssue(
                        "[ASSESSMENT_MISMATCH] Nhận định áp dụng vào hàng hóa cụ thể không phải mô tả quy định thuần túy.",
                        code="ASSESSMENT_MISMATCH",
                        path=f"checks/{check['claim_index']}/assessment",
                        expected=[
                            "APPLICATION",
                            "CONDITIONAL_APPLICATION",
                            "INSUFFICIENT_LEGAL_EVIDENCE",
                            "UNRESOLVED_APPLICATION",
                        ],
                        actual=check["assessment"],
                    )
                )
            if set(check["evidence_ids"]) - sources.keys() or set(check["fact_ids"]) - facts.keys():
                row_errors.append("Review giải thích tham chiếu ID ngoài ngữ cảnh.")
            if (
                check["assessment"] in {"REFERENCE", "APPLICATION", "CONDITIONAL_APPLICATION"}
                and not check["evidence_ids"]
            ):
                row_errors.append("Nhận định được xác nhận phải có nguồn hỗ trợ.")
            authentic_quotes = [
                match_user_quote(q, [facts[f] for f in check["fact_ids"] if f in facts])
                for q in check["user_quotes"]
            ]
            if any(not q for q in authentic_quotes):
                row_errors.append("Review giải thích phải trích đúng dữ kiện người dùng.")
            else:
                check["user_quotes"] = authentic_quotes
            if check["assessment"] == "APPLICATION" and (
                not check["fact_ids"] or not check["user_quotes"]
            ):
                row_errors.append(
                    ContractIssue(
                        "Nhận định áp dụng vào hàng hóa chưa có trích đoạn dữ kiện xác nhận.",
                        code="APPLICATION_FACTS_REQUIRED",
                        path=f"checks/{check['claim_index']}",
                        expected={
                            "fact_ids": "user_context của đúng mặt hàng",
                            "user_quotes": "trích đoạn nguyên văn hỗ trợ claim",
                            "assessment": "APPLICATION",
                        },
                        actual={"fact_ids": check["fact_ids"], "user_quotes": check["user_quotes"]},
                    )
                )
            if len(expected[rid]["item_ids"]) == 1:
                scoped = item_context(context, expected[rid]["item_ids"][0], 0)
                row_errors.extend(item_quote_errors(check["user_quotes"], scoped))
            else:
                scoped = {**context, "proof_item_ids": expected[rid]["item_ids"]}
            if context.get("reasoning_contract") == "semantic-v1" and (
                check["assessment"] == "APPLICATION"
                or context.get("legal_scope") != "SOURCE_SNAPSHOT"
                and check["assessment"] in {"REFERENCE", "CONDITIONAL_APPLICATION"}
            ):
                from rag.llm.contracts.obligations import temporal_errors

                row_errors.extend(temporal_errors(check["evidence_ids"], context))
            if context.get("reasoning_contract") == "semantic-v1" and check["assessment"] in {
                "APPLICATION",
                "FACT_SUPPORTED",
            }:
                from rag.llm.contracts.obligations import fact_errors

                row_errors.extend(fact_errors(check["fact_ids"], scoped))
                if check["assessment"] == "APPLICATION":
                    from rag.llm.validation.quantitative import (
                        _quantities,
                        quantitative_grounding_errors,
                    )

                    quotes = check["user_quotes"]
                    selected_sources = {
                        eid: sources[eid] for eid in check["evidence_ids"] if eid in sources
                    }
                    claim_quantities = _quantities(claim["text"])
                    user_quantities = [
                        q for quote in quotes for q in _quantities(quote, facts=True)
                    ]
                    relevant_dimensions = {q.dimension for q in claim_quantities} | {
                        q.dimension for q in user_quantities
                    }
                    is_exclusion = bool(
                        re.search(
                            r"\b(?:vuot\s+qua|khong\s+(?:thoa\s+man|dap\s+ung|thuoc|duoc\s+phan\s+loai|phu\s+hop|vao)|loai\s+tru|nam\s+ngoai)\b",
                            _folded(claim["text"]),
                        )
                    )
                    if relevant_dimensions and not is_exclusion:
                        matching_sources = {
                            eid: source
                            for eid, source in selected_sources.items()
                            if any(
                                q.dimension in relevant_dimensions
                                for q in _quantities(source["text"])
                            )
                        }
                        if matching_sources:
                            numeric_errors = quantitative_grounding_errors(
                                {
                                    "status": "SUPPORTED",
                                    "product_facts": [{"user_quote": quote} for quote in quotes],
                                    "condition_checks": [
                                        {
                                            "source_label": eid,
                                            "source_quote": source["text"],
                                            "assessment": "SATISFIED",
                                            "product_fact_indices": list(range(len(quotes))),
                                        }
                                        for eid, source in matching_sources.items()
                                    ],
                                },
                                matching_sources,
                                set(matching_sources),
                            )
                            row_errors.extend(numeric_errors)
            if context.get("proof_required"):
                from rag.llm.validation.proof import proof_errors

                row_errors.extend(
                    proof_errors(
                        check,
                        scoped,
                        target=claim["text"],
                        product=check["assessment"] in {"APPLICATION", "FACT_SUPPORTED"},
                        evidence_ids=check["evidence_ids"],
                        fact_ids=check["fact_ids"],
                    )
                )
            if check["assessment"] == "CONDITIONAL_APPLICATION" and not re.search(
                r"\b(?:neu|khi|chua|can xac dinh|can bo sung|con thieu|phu thuoc)\b", claim_text
            ):
                row_errors.append(
                    "[CONDITIONAL_CLAIM_MISMATCH] CONDITIONAL_APPLICATION không khớp nhận định đang khẳng định áp dụng hoặc thiếu biểu thức điều kiện."
                )
            level = check.get("application_level", 0)
            disputed = check["assessment"] in {
                "INSUFFICIENT_LEGAL_EVIDENCE",
                "UNRESOLVED_APPLICATION",
            }
            if not disputed:
                check["application_level"] = 0
            elif level and not any(
                len(sources[eid].get("code") or "") == level
                for eid in check["evidence_ids"]
                if eid in sources
            ):
                row_errors.append("Cấp áp dụng đang tranh chấp phải có wording nguồn tương ứng.")
        if row_errors:
            errors.extend(scoped_issue(e, rid) for e in row_errors)
            continue
        unsupported = [
            c
            for c in checks
            if c["assessment"]
            in {"INSUFFICIENT_LEGAL_EVIDENCE", "UNRESOLVED_APPLICATION", "FACT_UNSUPPORTED"}
        ]
        row = originals[rid]
        reviewed_claims = [dict(claim) for claim in row["claims"]]
        for check in checks:
            claim = reviewed_claims[check["claim_index"]]
            claim["evidence_ids"] = check["evidence_ids"]
            if claim["kind"] == "PRODUCT_FACT":
                # Publish user wording rather than an unchecked model paraphrase.
                claim["text"] = " / ".join(dict.fromkeys(check["user_quotes"]))
                claim["fact_ids"] = check["fact_ids"]
        text, citations, _ = render_claims(reviewed_claims, context)
        row = {**row, "claims": reviewed_claims, "answer": text, "citations": citations}
        if unsupported:
            retained = [
                claim
                for i, claim in enumerate(row["claims"])
                if i not in {c["claim_index"] for c in unsupported}
            ]
            text, citations, _ = render_claims(retained, context)
            has_valid_references = (
                row["kind"] == "EXPLAIN"
                and not expected[rid]["item_ids"]
                and any(c.get("evidence_ids") for c in retained)
                and all(c["assessment"] == "FACT_UNSUPPORTED" for c in unsupported)
            )
            if has_valid_references:
                row = {
                    **row,
                    "claims": retained,
                    "status": "ANSWERED",
                    "answer": text,
                    "citations": citations,
                    "missing_legal_evidence": [],
                    "missing_information": [],
                    "application_evidence_gap": False,
                }
            else:
                gap = (
                    "Nguồn hiện có chưa chứng minh đầy đủ nhận định đang xét."
                    if any(c["assessment"] == "INSUFFICIENT_LEGAL_EVIDENCE" for c in unsupported)
                    else "Nhận định chưa được xác nhận đầy đủ từ dữ kiện và điều kiện nguồn."
                )
                legal = any(c["assessment"] == "INSUFFICIENT_LEGAL_EVIDENCE" for c in unsupported)
                row = {
                    **row,
                    "claims": retained,
                    "status": "INSUFFICIENT_LEGAL_EVIDENCE" if legal else "REQUIRES_REVIEW",
                    "answer": f"{text} {gap}".strip(),
                    "citations": citations,
                    "missing_legal_evidence": [gap] if legal else [],
                    "missing_information": [],
                    "application_evidence_gap": row["kind"] == "EXPLAIN"
                    and bool(expected[rid]["item_ids"]),
                    "application_gap_level": min(c.get("application_level", 0) for c in unsupported),
                }
        omitted = [c["evidence_id"] for c in coverage if c["assessment"] == "OMITTED"]
        if omitted:
            row = {
                **row,
                "status": "REQUIRES_REVIEW",
                "answer": row["answer"]
                + " Phần liệt kê chưa bao phủ đầy đủ điều kiện trong nguồn.",
                "answer_coverage_gap": omitted,
                "missing_information": [],
                "missing_legal_evidence": [],
            }
        checked[rid] = {
            **row,
            "analysis_review_valid": True,
            "analysis_checks": checks,
            "failure_kind": "",
        }
    return checked, errors


def resolve_analysis_gaps(rows: list[dict], context: dict) -> list[dict]:
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    gaps: dict[str, dict] = {}
    for row in rows:
        if row.get("application_evidence_gap"):
            for item in goals[row["objective_id"]]["item_ids"]:
                if item not in gaps or row.get("application_gap_level", 0) < gaps[item].get(
                    "application_gap_level", 0
                ):
                    gaps[item] = row
    return [
        {
            **row,
            "status": gaps[row["item_id"]]["status"],
            "suggested_hs_code": "",
            "answer": "Chưa xét mã chi tiết khi căn cứ áp dụng cho cơ chế/đặc điểm hàng hóa chưa được phân định.",
            "citations": [],
            "hs_candidates": [],
            "review_valid": False,
            "missing_information": [],
            "missing_legal_evidence": gaps[row["item_id"]]["missing_legal_evidence"],
        }
        if row["kind"] == "CLASSIFY"
        and row["item_id"] in gaps
        and row["level"] >= gaps[row["item_id"]].get("application_gap_level", 0)
        and row["status"] not in {"MISSING_PRODUCT_INFO", "INSUFFICIENT_LEGAL_EVIDENCE"}
        else row
        for row in rows
    ]
