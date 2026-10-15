"""Generate, repair and review grounded answers over locked retrieval outputs."""

import json

import jsonschema

from rag.llm.groq_client import GroqClient, GroqError
from rag.llm.validation import LEGAL_INFORMATION, _folded, _normalized, validate_answer
from rag.prompts.product_review import PRODUCT_REVIEW_PROMPT
from rag.prompts.schemas import ANSWER_SCHEMA, PRODUCT_REVIEW_SCHEMA
from rag.utils.files import digest


def _legal_abstention(gaps: list[str]) -> dict:
    return {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Chưa đủ chứng cứ pháp lý trong retrieval/corpus để kết luận. Đây là khoảng trống chứng cứ của hệ thống.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": gaps,
    }


def _review_abstention() -> dict:
    return {
        **_legal_abstention([]),
        "status": "REQUIRES_REVIEW",
        "answer": "Chưa thể xác minh dữ kiện hàng hóa với điều kiện của mã HS; cần thẩm định thêm.",
    }


def _review_recommendation(
    context: dict, answer: dict, client: GroqClient, model: str
) -> tuple[dict, dict]:
    candidate = next(
        e for e in context["candidate_evidence"] if e["code"] == answer["suggested_hs_code"]
    )
    labels = set(candidate["required_citation_labels"]) | set(candidate["related_note_labels"])
    payload = {
        "question": context["question"],
        "candidate": candidate,
        "sources": [s for s in context["sources"] if s["label"] in labels],
    }
    try:
        generation = client.complete(
            [
                {"role": "system", "content": PRODUCT_REVIEW_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            PRODUCT_REVIEW_SCHEMA,
            model=model,
            allow_fallback=False,
        )
    except GroqError as exc:
        return _review_abstention(), {
            "valid": False,
            "errors": ["Product support review is unavailable"],
            "http_status": exc.status,
            "error_code": exc.error_code,
            "retry_after": exc.retry_after,
        }
    try:
        review = json.loads(generation["content"])
    except json.JSONDecodeError:
        review = {}
    errors = [
        e.message
        for e in jsonschema.Draft202012Validator(PRODUCT_REVIEW_SCHEMA).iter_errors(review)
    ]
    if generation["finish_reason"] != "stop":
        errors.append("Product support review did not finish normally")
    if not errors:
        for fact in review["product_facts"]:
            quote = _normalized(fact["user_quote"])
            if not quote or quote not in _normalized(context["question"]):
                errors.append("Product fact quotation does not occur in the user question")
            if LEGAL_INFORMATION.search(_folded(quote)) or LEGAL_INFORMATION.search(
                _folded(fact["fact"])
            ):
                errors.append("Legal text supplied by the user must not become a product fact")
        if review["status"] == "SUPPORTED":
            if (
                not review["product_facts"]
                or review["missing_information"]
                or review["missing_legal_evidence"]
            ):
                errors.append(
                    "Supported product review requires user facts and no information gaps"
                )
            proposed = answer
        else:
            proposed = {
                **_legal_abstention(review["missing_legal_evidence"]),
                "status": review["status"],
                "missing_information": review["missing_information"],
            }
            if review["status"] == "MISSING_PRODUCT_INFO":
                proposed["answer"] = "Cần làm rõ dữ kiện hàng hóa: " + " ".join(
                    review["missing_information"]
                )
            elif review["status"] == "REQUIRES_REVIEW":
                proposed["answer"] = (
                    "Dữ kiện hàng hóa chưa được xác nhận phù hợp với điều kiện của mã HS; cần thẩm định thêm."
                )
            errors.extend(validate_answer(proposed, context)["errors"])
    details = {
        **generation,
        "review": review,
        "valid": not errors,
        "errors": errors,
        "prompt_hash": digest(PRODUCT_REVIEW_PROMPT),
        "schema_hash": digest(PRODUCT_REVIEW_SCHEMA),
    }
    if errors:
        return _review_abstention(), details
    return proposed, details


def generate_answer(
    context: dict, client: GroqClient, *, model: str | None = None, allow_fallback: bool = True
) -> dict:
    if not context["sources"]:
        answer = _legal_abstention(
            ["Retrieval returned no usable legal sources within the generation context budget."]
        )
        return {
            "answer": answer,
            "validation": validate_answer(answer, context),
            "generation": {"model": None, "elapsed_ms": 0, "skipped": True},
        }
    messages = list(context["messages"])
    attempts: list[dict] = []
    for attempt in range(2):
        generation = client.complete(
            messages,
            ANSWER_SCHEMA,
            model=model if not attempts else attempts[0]["model"],
            allow_fallback=allow_fallback if not attempts else False,
        )
        try:
            answer = json.loads(generation["content"])
        except json.JSONDecodeError:
            answer = {}
        validation = validate_answer(answer, context)
        if generation["finish_reason"] != "stop":
            validation["errors"].append(
                "Generation did not finish normally; check output token budget"
            )
            validation["valid"] = False
        attempts.append({**generation, "validation": validation})
        if validation["valid"] or attempt == 1:
            break
        messages.extend(
            [
                {"role": "assistant", "content": generation["content"]},
                {
                    "role": "user",
                    "content": "Hãy sửa các lỗi kiểm tra sau, chỉ sử dụng các nguồn đã cung cấp: "
                    + json.dumps(validation["errors"])
                    + ". Đặt nhãn dạng [S1] ngay trong trường answer. Trả JSON ngắn gọn, đúng schema.",
                },
            ]
        )
    generation = {
        **generation,
        "requested_model": attempts[0].get("requested_model"),
        "fallback_used": attempts[0].get("fallback_used", False),
        "failures": [failure for a in attempts for failure in a.get("failures", [])],
        "attempts": attempts,
        "elapsed_ms": sum(a.get("elapsed_ms", 0) for a in attempts),
        "usage": {
            k: sum(a.get("usage", {}).get(k, 0) for a in attempts)
            for k in ("prompt_tokens", "completion_tokens", "total_tokens")
        },
    }
    if not validation["valid"] and validation.get("boundary_errors"):
        generation["guardrail_abstention"] = True
        answer = _legal_abstention(
            ["Generated output failed the product/legal ownership or HS source hierarchy checks."]
        )
        validation = validate_answer(answer, context)
    if validation["valid"] and answer["status"] == "RECOMMENDATION":
        answer, review = _review_recommendation(context, answer, client, generation["model"])
        generation["product_review"] = review
        generation["elapsed_ms"] += review.get("elapsed_ms", 0)
        for key in generation["usage"]:
            generation["usage"][key] += review.get("usage", {}).get(key, 0)
        validation = validate_answer(answer, context)
        validation["semantic_grounding"] = (
            "MODEL_REVIEWED" if review["valid"] else "REVIEW_UNAVAILABLE_OR_INVALID"
        )
    return {"answer": answer, "validation": validation, "generation": generation}
