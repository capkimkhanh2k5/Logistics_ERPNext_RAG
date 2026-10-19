"""Bounded, independently reviewed candidates; no probabilistic confidence scores."""

from rag.llm.application_rules import rule_name
from rag.llm.candidate_ranking import rank_candidates
from rag.llm.evidence import unique_clarifications
from rag.llm.task_validation import item_context

MAX_CANDIDATES = 3
EVIDENCE_LABELS = {
    "SUPPORTED": "Đủ căn cứ đề xuất trong nguồn hiện có",
    "CONDITIONAL": "Có điều kiện — cần bổ sung dữ kiện",
}


def expand_rows(rows: list[dict], context: dict) -> tuple[list[dict], dict]:
    """Reuse the existing batched review, with at most three jobs per result."""
    expanded, groups = [], {}
    for row in rows:
        codes = row.get("candidate_codes", [])
        if (
            not codes
            or row["kind"] != "CLASSIFY"
            or not row.get("valid")
            or row["status"] not in {"RECOMMENDATION", "MISSING_PRODUCT_INFO"}
        ):
            expanded.append(row)
            continue
        members = []
        for index, code in enumerate(codes):
            rid = f"{row['result_id']}.C{index + 1}"
            members.append(rid)
            expanded.append(
                {
                    **row,
                    "result_id": rid,
                    "status": "RECOMMENDATION",
                    "suggested_hs_code": code,
                    "missing_information": [],
                    "missing_legal_evidence": [],
                    "candidate_only": True,
                    "shortlist_codes": codes,
                    "review_evidence_labels": [c["label"] for c in row["citations"]],
                    # Candidate reasoning must be reconstructed from its own review.
                    "claims": [],
                    "answer": "Ứng viên cần kiểm tra độc lập.",
                    "citations": [],
                }
            )
        groups[row["result_id"]] = members
    return expanded, groups


def candidate_record(row: dict, context: dict) -> dict | None:
    review = row.get("review", {})
    if not row.get("review_valid") or review.get("status") not in {
        "SUPPORTED",
        "MISSING_PRODUCT_INFO",
    }:
        return None
    code = row.get("reviewed_code", row.get("suggested_hs_code", ""))
    if any(
        c["code"] == code and c["assessment"] != "POSSIBLE"
        for c in row.get("candidate_assessments", [])
    ):
        return None
    scoped = item_context(context, row["item_id"], row["level"], code)
    candidate = next((c for c in scoped["candidate_evidence"] if c["code"] == code), None)
    if not candidate or candidate["hierarchy"]["status"] != "VERIFIED":
        return None
    checks = review.get("condition_checks", [])
    required = set(candidate["required_citation_labels"])
    covered = {c["source_label"] for c in checks}
    if not required <= covered or any(
        c["assessment"] not in {"SATISFIED", "MISSING_PRODUCT_INFO"}
        for c in checks
        if c["source_label"] in required
    ):
        return None
    if any(
        c["assessment"] in {"CONTRADICTED", "UNRESOLVED_APPLICATION", "INSUFFICIENT_LEGAL_EVIDENCE"}
        for c in checks
    ):
        return None
    conditional = review["status"] == "MISSING_PRODUCT_INFO"
    if conditional and not review["missing_information"]:
        return None
    sources = {s["label"]: s for s in context["sources"]}
    clarifications = row.get("review_clarifications", [])
    question_sources = {sid for q in clarifications for sid in q["source_ids"]}
    labels = (
        required
        | {c["source_label"] for c in checks}
        | {s["label"] for s in context["sources"] if s["id"] in question_sources}
    )
    return {
        "code": code,
        "level": row["level"],
        "evidence_status": "CONDITIONAL" if conditional else "SUPPORTED",
        "reason": review["reason"],
        "conditions": [
            {
                "text": c["source_quote"],
                "source_id": sources[c["source_label"]]["id"],
                "required": c["source_label"] in required,
                **({"rule": name} if (name := rule_name(sources[c["source_label"]])) else {}),
                "assessment": c["assessment"],
                "source_label": c["source_label"],
                "user_quotes": [
                    review["product_facts"][i]["user_quote"] for i in c["product_fact_indices"]
                ],
            }
            for c in checks
        ],
        "missing_information": review["missing_information"],
        "clarifications": clarifications,
        "citations": [
            {"label": label, "quote": sources[label]["text"]}
            for label in sorted(labels, key=lambda value: int(value[1:]))
        ],
        "verified_path": row.get("verified_path", []),
        "selected_source": row.get("selected_source", {}),
    }


def collapse_rows(
    original: list[dict], reviewed: list[dict], groups: dict, context: dict
) -> list[dict]:
    by_id = {row["result_id"]: row for row in reviewed}
    output = []
    for row in original:
        ids = groups.get(row["result_id"], [row["result_id"]])
        members = [by_id[rid] for rid in ids]
        records = [record for r in members if (record := candidate_record(r, context))]
        records = list({r["code"]: r for r in records}.values())[:MAX_CANDIDATES]
        supported = [
            r for r in members if r.get("review_valid") and r["status"] == "RECOMMENDATION"
        ]

        def ruled_out(member):
            code = member.get("reviewed_code", "")
            return (
                member.get("review_valid")
                and member.get("review", {}).get("status") == "REQUIRES_REVIEW"
                and any(
                    c["assessment"] == "CONTRADICTED" for c in member["review"]["condition_checks"]
                )
                and any(
                    c["code"] == code and c["assessment"] == "RULED_OUT"
                    for c in member.get("candidate_assessments", [])
                )
            )

        supported_codes = {r["suggested_hs_code"] for r in supported}
        unique = len(supported_codes) == 1 and all(
            (
                r.get("review_valid")
                and r["status"] == "RECOMMENDATION"
                and r["suggested_hs_code"] in supported_codes
            )
            or ruled_out(r)
            for r in members
        )
        if not unique:
            # Inconsistent independent reviews are not several valid recommendations.
            records = [r for r in records if r["evidence_status"] != "SUPPORTED"]
        if row["result_id"] not in groups:
            merged = members[0]
        elif unique:
            merged = supported[0]
        else:
            valid_members = [r for r in members if r.get("review_valid")]
            structured = unique_clarifications(
                [q for r in valid_members for q in r.get("review_clarifications", [])]
            )
            missing = list(
                dict.fromkeys(
                    [
                        *[q["question"] for q in structured],
                        *[
                            q
                            for r in valid_members
                            if not r.get("review_clarifications")
                            for q in r["missing_information"]
                        ],
                    ]
                )
            )
            legal = list(
                dict.fromkeys(
                    g for r in members if r.get("review_valid") for g in r["missing_legal_evidence"]
                )
            )
            # Invalid jobs never become implicit exclusions or supported results.
            valid = all(r.get("review_valid") for r in members)
            if valid and missing and len(supported) == 0:
                status, text = (
                    "MISSING_PRODUCT_INFO",
                    "Chưa đủ dữ kiện để chọn duy nhất một mã. " + " ".join(missing),
                )
            elif valid and legal:
                status, text = (
                    "INSUFFICIENT_LEGAL_EVIDENCE",
                    "Chưa đủ chứng cứ để phân định các ứng viên.",
                )
            else:
                status = "REQUIRES_REVIEW"
                if valid and not supported:
                    text = "Chưa đủ căn cứ để chọn duy nhất một mã. " + " ".join(
                        dict.fromkeys(r["answer"] for r in members)
                    )
                elif valid:
                    text = "Các kết quả kiểm tra ứng viên chưa nhất quán để chọn duy nhất một mã."
                else:
                    text = "Chưa hoàn tất kiểm tra độc lập các ứng viên để đề xuất một mã."
            references = (
                {c["label"]: c for r in members for c in r["citations"]}
                if valid and not supported
                else {}
            )
            merged = {
                **row,
                "status": status,
                "answer": text,
                "suggested_hs_code": "",
                "review_valid": False,
                "citations": list(references.values()) if status == "REQUIRES_REVIEW" else [],
                "missing_information": missing if status == "MISSING_PRODUCT_INFO" else [],
                "missing_legal_evidence": legal if status == "INSUFFICIENT_LEGAL_EVIDENCE" else [],
            }
        output.append(
            {**merged, "result_id": row["result_id"], "hs_candidates": rank_candidates(records)}
        )
    return output


def render_candidates(candidates: list[dict], *, ask_questions=True) -> str:
    parts = []
    asked = set()
    for candidate in candidates:
        status = EVIDENCE_LABELS[candidate["evidence_status"]]
        labels = " ".join(f"[{c['label']}]" for c in candidate["citations"])
        reason = (
            candidate["reason"]
            if ask_questions or candidate["evidence_status"] == "SUPPORTED"
            else "Ứng viên còn điều kiện chưa xác nhận."
        )
        position = (
            f"Hạng {candidate['rank']}" + (" (đồng hạng)" if candidate.get("tied") else "") + " — "
            if "rank" in candidate
            else ""
        )
        parts.append(f"{position}Ứng viên {candidate['code']} — {status}: {reason} {labels}")
        if candidate.get("ranking_basis"):
            parts.append(candidate["ranking_basis"])
        for condition in candidate["conditions"]:
            if condition.get("rule") and condition["assessment"] == "SATISFIED":
                parts.append(
                    f"Quy tắc đã kiểm tra: {condition['rule']}; dữ kiện đối chiếu: "
                    + "; ".join(condition["user_quotes"])
                    + f". [{condition['source_label']}]"
                )
        unmet = [c for c in candidate["conditions"] if c["assessment"] == "MISSING_PRODUCT_INFO"]
        if unmet:
            parts.append(
                "Điều kiện chưa xác nhận: "
                + "; ".join(f"{c['text']} [{c['source_label']}]" for c in unmet)
            )
        missing = []
        questions = candidate.get("clarifications", [])
        for q in questions:
            key = (q["attribute"].casefold().strip(), tuple(sorted(q["source_ids"])))
            if key not in asked:
                missing.append(q["question"])
                asked.add(key)
        if not questions:
            missing = [q for q in candidate["missing_information"] if q not in asked]
            asked.update(missing)
        if missing and ask_questions:
            parts.append("Cần xác nhận: " + " ".join(missing))
    return "\n".join(parts)
