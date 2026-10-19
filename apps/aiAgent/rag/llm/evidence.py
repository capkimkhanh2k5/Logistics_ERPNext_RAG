"""Snapshot-bound evidence IDs; the backend alone renders labels and exact quotes."""

import re

from rag.llm.disambiguation import disambiguation_errors, review_scope
from rag.llm.quantitative import _proves, _quantities
from rag.llm.validation import _folded, match_user_quote, schema_errors
from rag.prompts.schemas import (
    MODEL_ANSWER_SCHEMA,
    MODEL_DECISION_REVIEW_SCHEMA,
    MODEL_DISAMBIGUATION_REVIEW_SCHEMA,
    MODEL_PRODUCT_REVIEW_SCHEMA,
)
from rag.utils.files import digest


def bind_evidence(sources: list[dict], snapshot=None) -> list[dict]:
    return [
        {
            **source,
            "evidence_id": "E"
            + digest([snapshot, source["id"], source["text"], 0, len(source["text"])])[:20],
        }
        for source in sources
    ]


def source_registry(context: dict) -> dict[str, dict]:
    return {s["evidence_id"]: s for s in context["sources"]}


def model_sources(sources: list[dict]) -> list[dict]:
    return [
        {key: value for key, value in source.items() if key not in {"label", "id"}}
        for source in sources
    ]


def model_candidate(candidate: dict, sources: list[dict]) -> dict:
    labels = {source["label"]: source["evidence_id"] for source in sources}

    def project(value):
        if isinstance(value, list):
            return [project(item) for item in value]
        if not isinstance(value, dict):
            return value
        projected = {}
        for key, item in value.items():
            if key.endswith("_labels"):
                projected[key.removesuffix("_labels") + "_evidence_ids"] = [
                    labels[v] for v in item if v in labels
                ]
            elif key.endswith("_label"):
                projected[key.removesuffix("_label") + "_evidence_id"] = labels.get(item, "")
            else:
                projected[key] = project(item)
        return projected

    return project(candidate)


def bind_user_context(question: str) -> dict:
    """Preserve human turns and literal clauses; assign IDs without classifying products."""
    turns = re.split(r"\n\nThông tin người dùng bổ sung ở lượt \d+: ", question)
    statements = []
    for index, text in enumerate(turns, 1):
        spans = {(0, len(text))}
        if len(text) <= 4000:
            for pattern in (
                r"(?:\.(?=\s|$)|[;\n!?])+",
                r"(?:\.(?=\s|$)|(?<!\d),|,(?!\d)|[;\n!?])+",
            ):
                pos = 0
                for match in re.finditer(pattern, text):
                    chunk = text[pos : match.start()]
                    start = pos + len(chunk) - len(chunk.lstrip())
                    end = pos + len(chunk.rstrip())
                    if start < end:
                        spans.add((start, end))
                    pos = match.end()
                tail = text[pos:]
                start = pos + len(tail) - len(tail.lstrip())
                end = pos + len(tail.rstrip())
                if start < end:
                    spans.add((start, end))
        seen: set[str] = set()
        for start, end in sorted(spans):
            quote = text[start:end]
            if quote.strip() and quote not in seen:
                seen.add(quote)
                statements.append(
                    {
                        "id": "U" + digest([index, text, start, end])[:20],
                        "turn": index,
                        "text": quote,
                        "start": start,
                        "end": end,
                    }
                )
    return {"statements": statements, "interpretation": "USER_STATEMENTS_NOT_VERIFIED_FACTS"}


def user_registry(context: dict) -> dict[str, dict]:
    return {row["id"]: row for row in context["user_context"]["statements"]}


def render_claims(claims: list[dict], context: dict) -> tuple[str, list[dict], list[str]]:
    sources, statements = source_registry(context), user_registry(context)
    parts: list[str] = []
    errors: list[str] = []
    cited: dict[str, dict] = {}
    for claim in claims:
        text = claim["text"].strip()
        if re.search(r"\[S\d+(?:\]|:)", text):
            errors.append("Model chỉ trả evidence_ids; nhãn [S#] do backend dựng.")
        if re.search(r"\[(?:E|U)[0-9a-f]{16,}[^\]]*\]", text):
            errors.append(
                "Không viết registry ID trong text; backend dựng citation từ evidence_ids."
            )
        selected = []
        for eid in dict.fromkeys(claim["evidence_ids"]):
            if eid not in sources:
                errors.append("ID chứng cứ không tồn tại hoặc thuộc snapshot khác: " + eid)
            else:
                source = sources[eid]
                selected.append(source["label"])
                cited.setdefault(
                    source["label"], {"label": source["label"], "quote": source["text"]}
                )
        if claim["kind"] == "PRODUCT_FACT" and not claim["fact_ids"]:
            errors.append("Nhận định hàng hóa phải tham chiếu lời người dùng qua fact_ids.")
        if any(sid not in statements for sid in claim["fact_ids"]):
            errors.append("ID lời người dùng không tồn tại hoặc không thuộc ngữ cảnh hiện tại.")
        parts.append(
            text + (" " + " ".join(f"[{label}]" for label in selected) if selected else "")
        )
    return " ".join(parts), list(cited.values()), list(dict.fromkeys(errors))


def unique_clarifications(items: list[dict]) -> list[dict]:
    """One question per declared attribute and source set, within the same item."""
    seen = set()
    result = []
    for item in items:
        key = (
            _folded(item["attribute"]).strip(),
            tuple(sorted(item.get("source_ids", item.get("evidence_ids", [])))),
        )
        if key not in seen:
            result.append(item)
            seen.add(key)
    return result


def clarification_errors(items: list[dict], context: dict) -> list[str]:
    sources, errors = source_registry(context), []
    statements = user_registry(context).values()
    for item in items:
        refs = item["evidence_ids"]
        if any(eid not in sources for eid in refs):
            errors.append("Câu hỏi tham chiếu ID nguồn không tồn tại hoặc đã thay đổi.")
            continue
        if item["attribute"] not in {"product_type", "question_scope"} and not refs:
            errors.append("Câu hỏi thuộc tính phải tham chiếu điều kiện quyết định từ nguồn.")
        attribute = _folded(item["attribute"]).strip()
        if (
            attribute.replace("_", " ") == "primary function"
            or "chuc nang chinh" in attribute
            or "chuc nang chinh" in _folded(item["question"])
        ) and not any("chuc nang chinh" in _folded(sources[eid]["text"]) for eid in refs):
            errors.append(
                "Câu hỏi chức năng chính phải dẫn nguồn quy định phân loại theo chức năng chính; định nghĩa riêng của từng loại máy không chứng minh tiêu chí này. Dùng chú giải phù hợp trong sources, không hỏi người dùng cung cấp luật."
            )
        thresholds = [
            q
            for eid in refs
            if attribute in _folded(sources[eid]["text"])
            for q in _quantities(sources[eid]["text"])
        ]
        measurements = [
            q
            for statement in statements
            if attribute in _folded(statement["text"])
            for q in _quantities(statement["text"], facts=True)
        ]
        if thresholds and all(
            (matching := [q for q in measurements if q.dimension == threshold.dimension])
            and all(_proves(q, threshold) for q in matching)
            for threshold in thresholds
        ):
            errors.append(
                "Không hỏi lại số đo/giới hạn đã được người dùng cung cấp đủ để đối chiếu "
                "điều kiện nguồn. Lỗi trích đoạn không có nghĩa là thiếu dữ kiện."
            )
    return list(dict.fromkeys(errors))


def decode_answer(value: dict, context: dict) -> tuple[dict, list[str]]:
    errors = schema_errors(value, MODEL_ANSWER_SCHEMA)
    if errors:
        return {}, errors
    text, citations, errors = render_claims(value["claims"], context)
    errors.extend(clarification_errors(value["clarifications"], context))
    if value["status"] != "MISSING_PRODUCT_INFO" and value["clarifications"]:
        errors.append("Chỉ MISSING_PRODUCT_INFO được hỏi làm rõ.")
    return {
        "status": value["status"],
        "answer": text,
        "suggested_hs_code": value["suggested_hs_code"],
        "alternatives": [],
        "citations": citations,
        "missing_information": [
            item["question"] for item in unique_clarifications(value["clarifications"])
        ],
        "missing_legal_evidence": value["missing_legal_evidence"],
    }, errors


def decode_product_review(
    value: dict, context: dict, *, candidate_code: str | None = None
) -> tuple[dict, list[str]]:
    comparison = bool(review_scope(context, candidate_code))
    schema = MODEL_DISAMBIGUATION_REVIEW_SCHEMA if comparison else MODEL_PRODUCT_REVIEW_SCHEMA
    errors = schema_errors(value, schema)
    if errors:
        return {}, errors
    errors = clarification_errors(value["clarifications"], context)
    if value["status"] != "MISSING_PRODUCT_INFO" and value["clarifications"]:
        errors.append("Chỉ MISSING_PRODUCT_INFO được yêu cầu người dùng bổ sung dữ kiện")
    if comparison:
        errors.extend(disambiguation_errors(value, context, candidate_code))
    sources, statements = source_registry(context), user_registry(context)
    facts, checks = [], []
    for check in value["condition_checks"]:
        source = sources.get(check["evidence_id"])
        refs = check["fact_ids"]
        if not source:
            errors.append("Điều kiện tham chiếu ID nguồn không tồn tại hoặc đã thay đổi.")
            continue
        if any(sid not in statements for sid in refs):
            errors.append("Điều kiện tham chiếu ID lời người dùng không tồn tại.")
            continue
        indices = []
        for quote in check["user_quotes"]:
            matched = match_user_quote(quote, [statements[sid]["text"] for sid in refs])
            if not matched:
                errors.append("Trích đoạn kiểm tra không thuộc lời người dùng được tham chiếu.")
                continue
            fact = {"fact": matched, "user_quote": matched}
            if fact not in facts:
                facts.append(fact)
            indices.append(facts.index(fact))
        checks.append(
            {
                "source_label": source["label"],
                "source_quote": source["text"],
                "assessment": check["assessment"],
                "product_fact_indices": indices,
            }
        )
    return {
        "status": value["status"],
        "reason": value["reason"],
        "product_facts": facts,
        "condition_checks": checks,
        "missing_information": [
            item["question"] for item in unique_clarifications(value["clarifications"])
        ],
        "missing_legal_evidence": value["missing_legal_evidence"],
    }, errors


def decode_decision_review(value: dict, context: dict) -> tuple[dict, list[str]]:
    errors = schema_errors(value, MODEL_DECISION_REVIEW_SCHEMA)
    if errors:
        return {}, errors
    sources, statements = source_registry(context), user_registry(context)
    errors = clarification_errors(value["clarifications"], context)
    identity_refs = value["identity_fact_ids"]
    if any(sid not in statements for sid in identity_refs):
        errors.append("Nhận diện phải tham chiếu lời người dùng trong ngữ cảnh hiện tại.")
    if value["identity_status"] == "IDENTIFIED":
        if not identity_refs or not value["product_type"].strip():
            errors.append("Nhận diện phải có tên loại hàng và ID lời người dùng làm căn cứ.")
    elif identity_refs or value["product_type"]:
        errors.append("Chưa nhận diện hoặc không áp dụng phải để trống loại hàng và ID nhận diện.")
    text, citations, claim_errors = render_claims(value["retained_qa"], context)
    errors.extend(claim_errors)
    clarifications = []
    for item in value["clarifications"]:
        selected = [sources[eid] for eid in item["evidence_ids"] if eid in sources]
        basis = {
            "product_type": "SOURCE_CONDITION" if selected else "PRODUCT_IDENTITY",
            "question_scope": "QUESTION_SCOPE",
        }.get(item["attribute"], "SOURCE_CONDITION")
        source = selected[0] if selected else {}
        clarifications.append(
            {
                "question": item["question"],
                "basis": basis,
                "source_label": source.get("label", ""),
                "source_quote": source.get("text", ""),
            }
        )
    return {
        **{key: value[key] for key in ("request_kind", "identity_status", "decision", "reason")},
        "product_type": value["product_type"],
        "product_type_quote": statements[identity_refs[0]]["text"]
        if identity_refs and identity_refs[0] in statements
        else "",
        "retained_qa": {"answer": text, "citations": citations},
        "clarifications": clarifications,
    }, errors
