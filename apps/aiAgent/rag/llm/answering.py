"""Generate, repair and review grounded answers over locked retrieval outputs."""

import json

from rag.llm.client import RAGClient
from rag.llm.errors import LLMError
from rag.llm.groq_client import GroqClient
from rag.llm.validation import (
    LEGAL_INFORMATION,
    _folded,
    _normalized,
    schema_errors,
    validate_answer,
)
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
    context: dict, answer: dict, client: GroqClient | RAGClient, model: str
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
    except LLMError as exc:
        return _review_abstention(), {
            "valid": False,
            "errors": ["Không thể thực hiện kiểm tra dữ kiện hàng hóa"],
            "http_status": exc.status,
            "provider": exc.provider,
            "model": exc.model,
            "error_code": exc.error_code,
            "retry_after": exc.retry_after,
        }
    try:
        review = json.loads(generation["content"])
    except json.JSONDecodeError:
        review = {}
    errors = schema_errors(review, PRODUCT_REVIEW_SCHEMA)
    if generation["finish_reason"] != "stop":
        errors.append("Lượt kiểm tra dữ kiện hàng hóa chưa hoàn tất bình thường")
    if not errors:
        for fact in review["product_facts"]:
            quote = _normalized(fact["user_quote"])
            if not quote or quote not in _normalized(context["question"]):
                errors.append(
                    "Trích đoạn dữ kiện hàng hóa không khớp nguyên văn câu hỏi người dùng"
                )
            if LEGAL_INFORMATION.search(_folded(quote)) or LEGAL_INFORMATION.search(
                _folded(fact["fact"])
            ):
                errors.append(
                    "Nội dung pháp lý do người dùng nêu không được coi là dữ kiện hàng hóa"
                )
        if review["status"] == "SUPPORTED":
            if (
                not review["product_facts"]
                or review["missing_information"]
                or review["missing_legal_evidence"]
            ):
                errors.append(
                    "SUPPORTED yêu cầu có dữ kiện người dùng và không còn khoảng trống thông tin"
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
    context: dict,
    client: GroqClient | RAGClient,
    *,
    model: str | None = None,
    allow_fallback: bool = True,
) -> dict:
    if not context["sources"]:
        answer = _legal_abstention(
            ["Không có nguồn pháp lý dùng được trong giới hạn ngữ cảnh sinh câu trả lời."]
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
                "Lượt sinh câu trả lời chưa hoàn tất bình thường; kiểm tra giới hạn token đầu ra"
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
                    + json.dumps(validation["errors"], ensure_ascii=False)
                    + ". Đặt nhãn dạng [S1] ngay trong trường answer. "
                    "Viết các phần diễn giải bằng tiếng Việt; giữ nguyên tên trường JSON, "
                    "mã trạng thái và trích đoạn nguyên văn. Trả JSON ngắn gọn, đúng schema.",
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
            ["Kết quả sinh vi phạm quy tắc phân biệt dữ kiện/chứng cứ pháp lý hoặc chuỗi nguồn HS."]
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
