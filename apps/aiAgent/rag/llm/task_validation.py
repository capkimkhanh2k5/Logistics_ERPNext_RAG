"""Validate goal coverage and item-scoped conclusions before any public rendering."""

import re

from rag.llm.evidence import clarification_errors, render_claims
from rag.llm.validation import schema_errors, validate_answer
from rag.prompts.task_answering import TASK_ANSWER_SCHEMA
from rag.retrieval.request_plan import explicit_level, referenced_codes


def _item_regions(context: dict) -> list[tuple[str, int, int]]:
    text = context["question"]
    markers = sorted(
        (m.start(), m.end(), item["id"])
        for item in context["request"]["items"]
        for m in re.finditer(re.escape(item["anchor"]), text)
    )
    regions = []
    for index, (start, end, item_id) in enumerate(markers):
        sentence = re.search(r"[.!?](?:\s|$)", text[end:])
        stop = (
            end
            if text[end - 1 : end] in {".", "!", "?"}
            else end + sentence.end()
            if sentence
            else len(text)
        )
        if index + 1 < len(markers):
            stop = min(stop, markers[index + 1][0])
        regions.append((item_id, start, max(end, stop)))
    return regions


def item_quote_errors(quotes: list[str], context: dict) -> list[str]:
    item_id = context.get("scoped_item_id")
    if not item_id:
        return []
    regions = context.get("item_regions", [])
    for quote in quotes:
        matches = list(re.finditer(re.escape(quote), context["question"])) if quote else []
        if matches and all(
            any(
                other != item_id and start <= m.start() and m.end() <= end
                for other, start, end in regions
            )
            for m in matches
        ):
            return [
                f"Trích đoạn '{quote}' thuộc mặt hàng khác, không được dùng chứng minh điều kiện của mặt hàng đang xét ({item_id}); hãy xóa hoặc thay bằng trích đoạn của {item_id}."
            ]
    return []


def item_context(context: dict, item_id: str, level: int, selected_code: str | None = None) -> dict:
    items = {i["id"]: i for i in context["request"]["items"]}
    own = items.get(item_id, {}).get("anchor", "")
    others = [i["anchor"] for key, i in items.items() if key != item_id]
    scope = {**context, "scoped_item_id": item_id, "item_regions": _item_regions(context)}
    statements = [
        s
        for s in context["user_context"]["statements"]
        if (
            not own
            or own in s["text"]
            or s["text"] in own
            or not any(a in s["text"] for a in others)
        )
        and not item_quote_errors([s["text"]], scope)
    ]
    candidates = [c for c in context["candidate_evidence"] if len(c["code"]) == level]
    codes = [c["code"] for c in candidates]
    peers = [
        c
        for c in context.get("comparison_candidates", [])
        if len(c["code"]) == level and selected_code and c["code"][:6] == selected_code[:6]
    ]
    branch_groups = [
        g
        for g in context.get("candidate_comparison", [])
        if g["parent_code"]
        and (selected_code in g["codes"] if selected_code else bool(set(g["codes"]) & set(codes)))
    ]
    if level == 8 and selected_code and branch_groups:
        candidates = [c for c in candidates if c["code"][:6] == selected_code[:6]]
        codes = [c["code"] for c in candidates]
    candidates = list({c["code"]: c for c in [*candidates, *peers]}.values())
    from rag.llm.application_rules import assembly_hypothesis

    rules = context.get("application_rule_labels", [])
    # Preserve turn boundaries: an earlier request must not hide a later correction.
    presentation = context["question"]
    for other, start, stop in reversed(scope["item_regions"]):
        if other != item_id:
            presentation = presentation[:start] + " " * (stop - start) + presentation[stop:]
    if rules and assembly_hypothesis(presentation):
        candidates = [
            {
                **candidate,
                "required_citation_labels": list(
                    dict.fromkeys([*candidate["required_citation_labels"], *rules])
                ),
            }
            for candidate in candidates
        ]
    eligible = codes + [c["code"] for c in peers if c["hierarchy"]["status"] == "VERIFIED"]
    return {
        **scope,
        "response_protocol": "registry-v2",
        "classification_level": level,
        "task": "hs" if level else "qa",
        "user_context": {**context["user_context"], "statements": statements},
        "candidate_evidence": candidates,
        "comparison_candidates": [],
        "allowed_hs_codes": list(dict.fromkeys(eligible)),
        "candidate_comparison": [
            {"parent_code": "", "codes": codes, "missing_codes": [], "branch_options": []},
            *branch_groups,
        ]
        if codes
        else [],
    }


_NEGATED_CODE_SPAN = re.compile(
    r"(?:không\s+(?:được\s+|bị\s+|thể\s+|còn\s+)?(?:thuộc|phân\s*loại|xếp\s*vào|áp\s*(?:dụng|mã)|phải(?:\s+là)?|coi\s+là|xem\s+là|đáp\s*ứng|thỏa\s*mãn|đạt)"
    r"|không\s+(?:xếp|vào|thuộc)\b|(?:bị\s+)?loại(?:\s*trừ(?:\s+khỏi)?|\s+khỏi)|thay\s+vì(?:\s+(?:thuộc|nhóm|phân\s*nhóm|mã))?|bác\s+bỏ(?:\s+(?:hướng|nhóm|phân\s*nhóm|mã))?"
    r"|vượt\s+(?:quá\s+)?(?:giới\s*hạn|ngưỡng|mức))"
    r"(?:(?![.;!?](?:\s|$)|\b(?:nhưng|mà|but|however)\b)[^\n]){0,120}?\b(?:như\s+)?(?:nhóm|phân\s*nhóm|mã(?:\s*hs)?|heading|subheading)?\s*"
    r"(?:\d{4}(?:\.\d{2}(?:\.\d{2})?)?|\d{2}\.\d{2}|\d{6}|\d{8})\b\)?",
    re.I,
)

_REJECTED_CODE_SPAN = re.compile(
    r"\b(?:mã(?:\s+HS)?|nhóm|phân\s*nhóm)\s*"
    r"(?:\d{4}(?:\.\d{2}(?:\.\d{2})?)?|\d{2}\.\d{2}|\d{6}|\d{8})\b\s*"
    r"(?:không\s+phù\s+hợp|không\s+áp\s+dụng|bị\s+loại\s+trừ)",
    re.I,
)


def code_claim_errors(
    claims: list[dict],
    selected: str,
    context: dict,
    registrations: set[str] | None = None,
    *,
    allow_comparison_refs=False,
) -> list[str]:
    # Code mentions in legal explanations are allowed; applying a code to goods is structured.
    errors = []
    query_codes = referenced_codes(context["question"])
    reference_codes = query_codes | {s.get("code") for s in context["sources"]}
    candidates = [*context.get("candidate_evidence", []), *context.get("comparison_candidates", [])]
    registered = set(registrations or ()) | ({selected} if selected else set())
    for candidate in candidates:
        if candidate["hierarchy"]["status"] != "VERIFIED":
            continue
        if candidate["code"] == selected:
            registered.update(n["code"] for n in candidate["hierarchy"]["chain"])
        if allow_comparison_refs and selected and len(candidate["code"]) == len(selected):
            registered.add(candidate["code"])
    for claim in claims:
        text = claim["text"]
        check_text = _REJECTED_CODE_SPAN.sub(" ", _NEGATED_CODE_SPAN.sub(" ", text))
        found = set(re.findall(r"(?<!\d)(?:\d{4}\.\d{2}\.\d{2}|\d{8})(?!\d)", check_text))
        found = {s.replace(".", "") for s in found}
        applied = re.search(
            r"(?:thuộc|áp\s*(?:dụng|mã)|đề xuất|phân loại|xếp vào|mã phù hợp)", check_text, re.I
        )
        if (
            found
            - registered
            - (reference_codes if claim["kind"] != "CONCLUSION" or not applied else set())
        ):
            errors.append(
                "Mã HS8 trong diễn giải chưa được đăng ký để kiểm tra; dùng trường code của kết quả phân loại. "
                "Nếu chưa kết luận, chuyển phần tham chiếu mã sang LEGAL_ANALYSIS, "
                "viết CONCLUSION mô tả trạng thái chưa đủ căn cứ mà không ghi mã."
            )
        if claim["kind"] == "CONCLUSION" and applied:
            codes = referenced_codes(check_text) & (reference_codes | registered)
            if codes - registered:
                errors.append(
                    "Kết luận áp mã phải nằm trong đúng result có mã đã được kiểm tra: "
                    + ", ".join(sorted(codes - registered))
                    + ". Nếu chưa kết luận, chuyển phần tham chiếu/so sánh mã sang LEGAL_ANALYSIS "
                    "và viết CONCLUSION chưa đủ căn cứ mà không nhắc mã."
                )
    return errors


def _detail_gap(goal: dict, declared: dict, context: dict) -> str:
    target = max(goal["level"], explicit_level(goal["anchor"]) or 0)
    if goal["kind"] != "REQUIREMENTS" or target <= 4:
        return ""
    headings = {
        code
        for (_, item), codes in declared.items()
        if item in goal["item_ids"]
        for code in codes
        if len(code) == 4
    }
    covered = {
        node["code"]
        for proof in context.get("detail_evidence", [])
        if any(n["level"] >= target for n in proof["chain"])
        for node in proof["chain"]
        if node["level"] == 4
    }
    if headings - covered:
        return (
            f"Chưa có wording phân nhóm đến cấp {target} số với đường graph đã xác minh "
            f"trong ngữ cảnh của nhóm {', '.join(sorted(headings - covered))}; "
            "cần phục hồi các phân nhóm và chú giải để xác nhận danh sách thông số."
        )
    return ""


def decode_task_answer(value: dict, context: dict) -> tuple[list[dict], list[str]]:
    errors = schema_errors(value, TASK_ANSWER_SCHEMA)
    if errors:
        return [], errors
    goals = {g["id"]: g for g in context["request"]["objectives"]}

    def _row_item_id(row: dict) -> str:
        goal = goals.get(row["objective_id"])
        if goal and goal["kind"] != "CLASSIFY" and row["item_id"] in set(goal["item_ids"]):
            return ""
        return row["item_id"]

    expected = {
        (g["id"], item)
        for g in goals.values()
        for item in (g["item_ids"] if g["kind"] == "CLASSIFY" else [""])
    }
    actual = [(r["objective_id"], _row_item_id(r)) for r in value["results"]]
    declared: dict[tuple[str, str], set[str]] = {}
    for row in value["results"]:
        goal = goals.get(row["objective_id"], {})
        if (
            goal.get("kind") != "CLASSIFY"
            or row["status"] != "RECOMMENDATION"
            or len(row["code"]) != goal["level"]
        ):
            continue
        candidate = next(
            (
                c
                for c in [*context["candidate_evidence"], *context.get("comparison_candidates", [])]
                if c["code"] == row["code"] and c["hierarchy"]["status"] == "VERIFIED"
            ),
            None,
        )
        if candidate:
            declared[(row["objective_id"], row["item_id"])] = {
                n["code"] for n in candidate["hierarchy"]["chain"]
            }
    if len(set(actual)) != len(actual) or set(actual) != expected:
        errors.append(
            "results phải bao phủ đúng mỗi objective/item một lần, không bỏ vế yêu cầu hoặc gộp nhiều sản phẩm."
        )
    decoded = []
    for index, row in enumerate(value["results"], 1):
        item_id = _row_item_id(row)
        if (row["objective_id"], item_id) not in expected:
            continue
        goal = goals[row["objective_id"]]
        dependencies = {
            key: codes
            for key, codes in declared.items()
            if key[1] in goal["item_ids"] and key != (goal["id"], item_id)
        }
        registered = set().union(*dependencies.values()) if dependencies else set()
        scoped = item_context(
            context,
            item_id,
            goal["level"] if goal["kind"] == "CLASSIFY" else 0,
            row["code"] or None,
        )
        if registered:
            scoped = {**scoped, "registered_hs_codes": sorted(registered)}
        clarifications = row["clarifications"]
        inherited = False
        if (
            goal["kind"] == "CLASSIFY"
            and row["status"] == "MISSING_PRODUCT_INFO"
            and not clarifications
        ):
            parents = [
                parent
                for parent in value["results"]
                if parent["item_id"] == item_id
                and goals.get(parent["objective_id"], {}).get("kind") == "CLASSIFY"
                and 0 < goals[parent["objective_id"]]["level"] < goal["level"]
                and parent["status"] == "MISSING_PRODUCT_INFO"
                and parent["clarifications"]
            ]
            if parents:
                nearest = max(parents, key=lambda parent: goals[parent["objective_id"]]["level"])
                clarifications = nearest["clarifications"]
                inherited = True
        raw_shortlist = [] if inherited else row.get("candidate_codes", [])
        text, citations, row_errors = render_claims(row["claims"], scoped)
        catalogue = {
            c["code"]: c
            for c in [*context["candidate_evidence"], *context.get("comparison_candidates", [])]
        }
        eligible = {
            code
            for code, candidate in catalogue.items()
            if goal["kind"] == "CLASSIFY"
            and len(code) == goal["level"]
            and candidate["hierarchy"]["status"] == "VERIFIED"
        }
        shortlist = [code for code in raw_shortlist if code in eligible]
        if raw_shortlist and row["code"] in eligible:
            shortlist = [row["code"], *[code for code in shortlist if code != row["code"]]][:3]
        discarded = [code for code in raw_shortlist if code not in shortlist]
        if actual.count((row["objective_id"], item_id)) != 1:
            row_errors.append("Kết quả objective/item bị lặp, chưa thể chọn kết luận nào.")
        answer = {
            "status": row["status"],
            "answer": text,
            "suggested_hs_code": row["code"],
            "alternatives": [],
            "citations": citations,
            "missing_information": [q["question"] for q in clarifications],
            "missing_legal_evidence": row["missing_legal_evidence"],
        }
        row_errors.extend(clarification_errors(clarifications, scoped))
        row_errors.extend(
            validate_answer(answer, {**scoped, "structured_code_claims": row["claims"]})["errors"]
        )
        allowed_facts = {s["id"] for s in scoped["user_context"]["statements"]}
        if any(set(c["fact_ids"]) - allowed_facts for c in row["claims"]):
            row_errors.append(
                "fact_ids được phép cho mặt hàng này: " + ", ".join(sorted(allowed_facts))
            )
        row_errors.extend(
            code_claim_errors(
                row["claims"], row["code"], context, registered, allow_comparison_refs=True
            )
        )
        if row["status"] in {"ANSWERED", "RECOMMENDATION"} and any(
            c["kind"] != "PRODUCT_FACT" and not c["evidence_ids"] for c in row["claims"]
        ):
            row_errors.append("Mỗi nhận định pháp lý/kết luận hoàn thành phải có nguồn hỗ trợ.")
        errors.extend(f"R{index}: {e}" for e in row_errors)
        gap = _detail_gap(goal, declared, context)
        if not row_errors and row["status"] == "ANSWERED" and gap:
            answer.update(
                status="INSUFFICIENT_LEGAL_EVIDENCE",
                answer=gap,
                missing_information=[],
                missing_legal_evidence=[gap],
            )
        query_codes = referenced_codes(context["question"])
        query_family = {
            c[:size] for c in query_codes for size in (4, 6, 8) if len(c) >= size
        } | query_codes
        decoded.append(
            {
                **answer,
                "result_id": f"R{index}",
                "objective_id": goal["id"],
                "item_id": item_id,
                "level": goal["level"],
                "required": goal["required"],
                "kind": goal["kind"],
                "claims": row["claims"],
                "candidate_codes": shortlist,
                "discarded_candidate_codes": discarded,
                "draft_clarifications": clarifications,
                "clarifications_inherited": inherited,
                "valid": not row_errors,
                "depends_on": [
                    list(key)
                    for key, codes in dependencies.items()
                    if goal["kind"] != "CLASSIFY"
                    and any(
                        (codes - query_family) & referenced_codes(c["text"])
                        for c in row["claims"]
                        if c["kind"] in {"LEGAL_ANALYSIS", "CONCLUSION"}
                    )
                ],
            }
        )
    allowed_codes = referenced_codes(context["question"]) | {
        s.get("code") for s in context["sources"]
    }
    for gap in value["evidence_gaps"]:
        if gap["anchor"] not in context["question"] or not set(gap["codes"]) <= allowed_codes:
            errors.append("Recovery gap phải dùng anchor thật và mã từ câu hỏi/nguồn được cấp.")
    return decoded, list(dict.fromkeys(errors))


def render_task_answer(rows: list[dict], context: dict) -> dict:
    from rag.llm.shortlist import render_candidates

    required = [r for r in rows if r["required"]] or rows
    unresolved = [r for r in required if r["status"] not in {"ANSWERED", "RECOMMENDATION"}]
    status = next(
        (
            s
            for s in ["MISSING_PRODUCT_INFO", "INSUFFICIENT_LEGAL_EVIDENCE", "REQUIRES_REVIEW"]
            if any(r["status"] == s for r in unresolved)
        ),
        "ANSWERED",
    )
    items = {i["id"]: i["anchor"] for i in context["request"]["items"]}
    parts, citations = [], {}
    for row in rows:
        title = items.get(row["item_id"], "")
        text = (f"{title}: " if title else "") + row["answer"]
        if row["status"] == "RECOMMENDATION" and row.get("review_valid"):
            text += f" Mã HS {row['level']} số đề xuất: {row['suggested_hs_code']}."
        candidates = row.get("hs_candidates", [])
        if candidates:
            text += "\n" + render_candidates(
                candidates, ask_questions=status == "MISSING_PRODUCT_INFO"
            )
            for candidate in candidates:
                for c in candidate["citations"]:
                    citations[c["label"]] = c
        parts.append(text)
        for c in row["citations"]:
            citations[c["label"]] = c
    single = (
        rows[0]
        if len(rows) == 1 and rows[0].get("review_valid") and rows[0]["level"] == 8
        else None
    )
    if not unresolved and single and single["status"] == "RECOMMENDATION":
        status = "RECOMMENDATION"
    return {
        "status": status,
        "answer": "\n\n".join(parts),
        "suggested_hs_code": single["suggested_hs_code"]
        if single and status == "RECOMMENDATION"
        else "",
        "alternatives": [],
        "citations": list(citations.values()),
        "missing_information": list(
            dict.fromkeys(q for r in rows for q in r["missing_information"])
        )
        if status == "MISSING_PRODUCT_INFO"
        else [],
        "missing_legal_evidence": list(
            dict.fromkeys(g for r in rows for g in r["missing_legal_evidence"])
        )
        if status == "INSUFFICIENT_LEGAL_EVIDENCE"
        else [],
        "hs_candidates": rows[0].get("hs_candidates", []) if len(rows) == 1 else [],
        "results": [
            {
                k: v
                for k, v in r.items()
                if k
                not in {
                    "claims",
                    "valid",
                    "candidate_codes",
                    "discarded_candidate_codes",
                    "candidate_only",
                    "shortlist_codes",
                    "draft_clarifications",
                    "clarifications_inherited",
                    "review_evidence_labels",
                }
            }
            for r in rows
        ],
    }
