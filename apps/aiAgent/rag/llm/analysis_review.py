"""Review explanatory legal applications in the existing classification batch."""

import re

from rag.llm.evidence import render_claims
from rag.llm.grounding import indirect_drive_gap, unsupported_qualifier_errors
from rag.llm.task_validation import item_context, item_quote_errors
from rag.llm.validation import _folded, match_user_quote, schema_errors

ANALYSIS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "result_id": {"type": "string"},
            "checks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "claim_index": {"type": "integer", "minimum": 0},
                        "assessment": {
                            "enum": [
                                "REFERENCE",
                                "APPLICATION",
                                "CONDITIONAL_APPLICATION",
                                "INSUFFICIENT_LEGAL_EVIDENCE",
                                "UNRESOLVED_APPLICATION",
                            ]
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "uniqueItems": True,
                        },
                        "fact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                        "user_quotes": {"type": "array", "items": {"type": "string"}},
                        "reason": {"type": "string", "minLength": 1},
                        "application_level": {"type": "integer", "enum": [0, 4, 6, 8]},
                    },
                    "required": [
                        "claim_index",
                        "assessment",
                        "evidence_ids",
                        "fact_ids",
                        "user_quotes",
                        "reason",
                    ],
                },
            },
        },
        "required": ["result_id", "checks"],
    },
}

ANALYSIS_PROMPT = """
Nếu có analysis_jobs, trả thêm analysis_reviews đúng một mục mỗi result_id. Kiểm tra độc lập
TỪNG claim_index pháp lý được cấp, kể cả LEGAL_ANALYSIS, không chỉ CONCLUSION.
REFERENCE chỉ khi nhận định mô tả quy định/so sánh từ ngữ nguồn, không áp dụng quy định vào hàng hóa
thực tế (kể cả kết luận bằng tên chủng loại như hybrid mà không ghi mã số).
APPLICATION khi nhận định áp dụng vào hàng hóa cụ thể được chứng minh đầy đủ: cần nguồn hỗ trợ
đúng cơ chế và fact_ids/user_quotes thật của các item_ids; tiêu đề nhóm chung không đủ chứng minh
cách áp dụng cho cơ chế gián tiếp hoặc thiết kế nằm giữa các nhóm cạnh tranh.
INSUFFICIENT_LEGAL_EVIDENCE nếu thiếu căn cứ cho nhận định; UNRESOLVED_APPLICATION nếu cách áp dụng
chưa phân định. reason chỉ mô tả khoảng trống, không lặp kết luận chưa được chứng minh.
CONDITIONAL_APPLICATION khi quy định đã rõ và nhận định chỉ diễn giải có điều kiện/phụ thuộc dữ kiện
hàng hóa chưa cung cấp (ví dụ nếu có sạc ngoài thì xét nhánh này, nếu không thì nhánh kia).
Không biến thiếu dữ kiện hàng hóa thành thiếu luật hoặc cách áp dụng chưa phân định.
Với nhận định chưa đủ căn cứ, application_level ghi cấp 4/6/8 đang tranh chấp nếu có wording nguồn
tương ứng; ghi 0 nếu chưa xác định. Thiếu căn cứ ở mã chi tiết không phủ nhận nhóm cha đã được kiểm tra.
Không đánh dấu REFERENCE cho một câu áp mã/áp tên phân loại cho sản phẩm để né kiểm tra.
evidence_ids phải lấy trong claim hoặc nguồn được cấp; không dùng lời người dùng làm nguồn luật.
"""


def analysis_jobs(rows: list[dict], context: dict) -> list[dict]:
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    return [
        {
            "result_id": row["result_id"],
            "item_ids": goals[row["objective_id"]]["item_ids"],
            "claims": [
                {"claim_index": i, **claim}
                for i, claim in enumerate(row["claims"])
                if claim["kind"] != "PRODUCT_FACT"
            ],
        }
        for row in rows
        if row["kind"] == "EXPLAIN"
        and any(c["kind"] != "PRODUCT_FACT" for c in row["claims"])
        and goals[row["objective_id"]]["item_ids"]
        and row.get("valid")
    ]


def check_analyses(value: list[dict], jobs: list[dict], rows: list[dict], context: dict):
    errors = schema_errors(value, ANALYSIS_SCHEMA)
    expected = {job["result_id"]: job for job in jobs}
    if errors or len(value) != len(expected) or {r["result_id"] for r in value} != set(expected):
        return {}, errors or ["analysis_reviews phải bao phủ đúng một lần từng analysis_job."]
    sources = {s["evidence_id"]: s for s in context["sources"]}
    facts = {s["id"]: s["text"] for s in context["user_context"]["statements"]}
    originals = {row["result_id"]: row for row in rows}
    checked = {}
    for review in value:
        rid = review["result_id"]
        claims = {c["claim_index"]: c for c in expected[rid]["claims"]}
        checks = review["checks"]
        if len(checks) != len(claims) or {c["claim_index"] for c in checks} != set(claims):
            errors.append(
                f"{rid}: Kiểm tra đủ từng claim_index pháp lý, không bỏ hoặc lặp nhận định."
            )
            continue
        row_errors = []
        for check in checks:
            claim_text = _folded(claims[check["claim_index"]]["text"])
            if (
                check["assessment"] == "REFERENCE"
                and re.search(
                    r"(?:xe|hang hoa|san pham|thiet bi|phuong tien) nay|trong truong hop nay",
                    claim_text,
                )
                and re.search(
                    r"duoc (?:xep|phan loai|coi la|xem la)|thuoc (?:nhom|phan nhom|ma)", claim_text
                )
            ):
                row_errors.append(
                    "Câu áp phân loại cho hàng hóa cụ thể không phải REFERENCE; kiểm tra APPLICATION hoặc ghi khoảng trống căn cứ."
                )
            if set(check["evidence_ids"]) - sources.keys() or set(check["fact_ids"]) - facts.keys():
                row_errors.append("Review giải thích tham chiếu ID ngoài ngữ cảnh.")
            if any(
                not match_user_quote(q, [facts[f] for f in check["fact_ids"] if f in facts])
                for q in check["user_quotes"]
            ):
                row_errors.append("Review giải thích phải trích đúng dữ kiện người dùng.")
            if check["assessment"] == "APPLICATION" and (
                not check["fact_ids"] or not check["user_quotes"]
            ):
                row_errors.append("Nhận định áp dụng vào hàng hóa phải có dữ kiện xác nhận.")
            if check["assessment"] == "APPLICATION":
                row_errors.extend(
                    unsupported_qualifier_errors(
                        [claims[check["claim_index"]]["text"]],
                        check["user_quotes"],
                    )
                )
            if len(expected[rid]["item_ids"]) == 1:
                scoped = item_context(context, expected[rid]["item_ids"][0], 0)
                row_errors.extend(item_quote_errors(check["user_quotes"], scoped))
            if check["assessment"] == "APPLICATION" and indirect_drive_gap(
                context["question"],
                [sources[eid]["text"] for eid in check["evidence_ids"] if eid in sources],
            ):
                row_errors.append(
                    "Chưa có căn cứ giải thích cơ chế gián tiếp; phải dùng INSUFFICIENT_LEGAL_EVIDENCE thay vì xác nhận APPLICATION từ tiêu đề chung."
                )
            if check["assessment"] == "CONDITIONAL_APPLICATION" and not re.search(
                r"\b(?:neu|khi|chua|can xac dinh|can bo sung|con thieu|phu thuoc)\b", claim_text
            ):
                row_errors.append(
                    "CONDITIONAL_APPLICATION phải giữ điều kiện/chỗ thiếu dữ kiện trong chính nhận định, không khẳng định áp mã."
                )
            level = check.get("application_level", 0)
            if level and not any(
                len(sources[eid].get("code") or "") == level
                for eid in check["evidence_ids"]
                if eid in sources
            ):
                row_errors.append("Cấp áp dụng đang tranh chấp phải có wording nguồn tương ứng.")
        if row_errors:
            errors.extend(f"{rid}: {e}" for e in row_errors)
            continue
        unsupported = [
            c
            for c in checks
            if c["assessment"] in {"INSUFFICIENT_LEGAL_EVIDENCE", "UNRESOLVED_APPLICATION"}
        ]
        row = originals[rid]
        reviewed_claims = [dict(claim) for claim in row["claims"]]
        for check in checks:
            reviewed_claims[check["claim_index"]]["evidence_ids"] = check["evidence_ids"]
        text, citations, _ = render_claims(reviewed_claims, context)
        row = {**row, "claims": reviewed_claims, "answer": text, "citations": citations}
        if unsupported:
            retained = [
                claim
                for i, claim in enumerate(row["claims"])
                if i not in {c["claim_index"] for c in unsupported}
            ]
            text, citations, _ = render_claims(retained, context)
            gap = "Chưa đủ căn cứ xác nhận cách áp dụng quy định cho cơ chế/đặc điểm hàng hóa đã mô tả."
            legal = any(c["assessment"] == "INSUFFICIENT_LEGAL_EVIDENCE" for c in unsupported)
            row = {
                **row,
                "status": "INSUFFICIENT_LEGAL_EVIDENCE" if legal else "REQUIRES_REVIEW",
                "answer": f"{text} {gap}".strip(),
                "citations": citations,
                "missing_legal_evidence": [gap] if legal else [],
                "missing_information": [],
                "application_evidence_gap": True,
                "application_gap_level": min(c.get("application_level", 0) for c in unsupported),
            }
        checked[rid] = {**row, "analysis_review_valid": True, "analysis_checks": checks}
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
        else row
        for row in rows
    ]
