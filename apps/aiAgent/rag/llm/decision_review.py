"""Ground clarification decisions in the user's question and actual source evidence."""

import json
import re
from time import perf_counter

from rag.llm.errors import LLMError
from rag.llm.evidence import decode_decision_review, model_sources, user_registry
from rag.llm.validation import _folded, schema_errors, validate_answer
from rag.prompts.decision_review import (
    DECISION_REVIEW_PROMPT,
    format_decision_review_repair_prompt,
)
from rag.prompts.schemas import DECISION_REVIEW_SCHEMA, MODEL_DECISION_REVIEW_SCHEMA
from rag.utils.files import digest


def _failed_answer() -> dict:
    return {
        "status": "REQUIRES_REVIEW",
        "answer": "Bước kiểm tra nhu cầu và dữ kiện chưa hoàn tất hợp lệ; hệ thống chưa thể kết luận.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": [],
    }


def _safe_errors(errors: list[str]) -> list[str]:
    return list(
        dict.fromkeys(
            "Kết quả kiểm tra không đúng cấu trúc JSON bắt buộc."
            if error.startswith("/")
            else error
            for error in errors
        )
    )


def _checked_decision(review: dict, context: dict, answer: dict) -> tuple[dict, list[str]]:
    errors = schema_errors(review, DECISION_REVIEW_SCHEMA)
    if errors:
        return _failed_answer(), _safe_errors(errors)
    kind, identity = review["request_kind"], review["identity_status"]
    clarifications = review["clarifications"]
    product_type, quote = review["product_type"], review["product_type_quote"]
    if not review["reason"].strip():
        errors.append("Kết quả kiểm tra phải có lý do cụ thể")
    if identity == "IDENTIFIED":
        if not product_type.strip() or not quote.strip():
            errors.append("Loại hàng đã nhận diện phải có tên loại hàng và trích đoạn người dùng")
        elif context.get("response_protocol") == "registry-v2":
            if not any(f["text"] == quote for f in user_registry(context).values()):
                errors.append("Căn cứ nhận diện không thuộc lời người dùng hiện tại.")
        elif quote not in context["question"] or product_type not in quote:
            errors.append("Loại hàng phải nằm nguyên văn trong trích đoạn thực tế của người dùng")
    elif product_type or quote:
        errors.append("Không được điền loại hàng suy đoán khi người dùng chưa xác nhận loại hàng")
    if kind == "QA" and identity != "NOT_APPLICABLE":
        errors.append("Hỏi đáp kiến thức không yêu cầu nhận diện hàng hóa")
    if kind in {"HS", "MIXED"} and identity == "NOT_APPLICABLE":
        errors.append("Yêu cầu phân loại hàng hóa phải kiểm tra nhận diện đối tượng")
    if kind in {"HS", "MIXED"} and identity == "UNCONFIRMED":
        if review["decision"] != "CLARIFY" or not any(
            item["basis"] == "PRODUCT_IDENTITY" for item in clarifications
        ):
            errors.append("Chưa xác nhận loại hàng phải hỏi nhận diện sản phẩm thực tế")
        if any(item["basis"] == "SOURCE_CONDITION" for item in clarifications):
            errors.append("Cần nhận diện loại hàng trước khi hỏi thông số chuyên biệt")
    if review["decision"] == "KEEP" and clarifications:
        errors.append("Giữ nguyên kết quả không được kèm câu hỏi làm rõ")
    if review["decision"] == "CLARIFY" and not clarifications:
        errors.append("Quyết định làm rõ phải có câu hỏi cụ thể")
    if kind == "UNCLEAR" and (
        review["decision"] != "CLARIFY"
        or not any(item["basis"] == "QUESTION_SCOPE" for item in clarifications)
    ):
        errors.append("Nhu cầu chưa rõ phải hỏi làm rõ nội dung câu hỏi")
    sources = {source["label"]: source for source in context["sources"]}
    retained_qa = review["retained_qa"]
    retained_text, retained_citations = retained_qa["answer"], retained_qa["citations"]
    for text in [review["reason"], retained_text, *[item["question"] for item in clarifications]]:
        folded = _folded(text)
        if re.search(r"\b[0-9]{4}\.?[0-9]{2}\.?[0-9]{2}\b", folded) and re.search(
            r"\b(?:de xuat|khuyen nghi|nen (?:su dung|chon)|phan loai (?:vao|theo)"
            r"|(?:san pham|mat hang|hang hoa)\b.{0,80}\bthuoc"
            r"|recommend(?:ed)?|classif(?:y|ied) (?:as|under)|(?:product|item|goods)"
            r"\b.{0,80}\bfalls? under)\b",
            folded,
        ):
            errors.append("Bước kiểm tra quyết định không được phát hành mã HS trong diễn giải")
    if kind != "MIXED" or review["decision"] != "CLARIFY":
        if retained_text or retained_citations:
            errors.append("Chỉ giữ phần hỏi đáp độc lập khi yêu cầu kết hợp cần làm rõ")
    elif retained_text or retained_citations:
        qa_answer = {
            **_failed_answer(),
            "status": "ANSWERED",
            "answer": retained_text,
            "citations": retained_citations,
        }
        errors.extend(validate_answer(qa_answer, {**context, "task": "qa"})["errors"])
        for citation in retained_citations:
            source = sources.get(citation["label"])
            if not source or not citation["quote"] or citation["quote"] not in source["text"]:
                errors.append("Trích đoạn hỏi đáp được giữ phải khớp nguyên văn nguồn thực tế")
    citations: dict[str, str] = {}
    for item in clarifications:
        if not item["question"].strip():
            errors.append("Câu hỏi làm rõ không được để trống")
        basis, label, source_quote = item["basis"], item["source_label"], item["source_quote"]
        if kind == "QA" and basis != "QUESTION_SCOPE":
            errors.append("Chỉ làm rõ nội dung câu hỏi khi yêu cầu là hỏi đáp kiến thức")
        if identity == "IDENTIFIED" and basis == "PRODUCT_IDENTITY":
            errors.append("Không hỏi lại loại hàng đã được người dùng xác nhận")
        if basis == "SOURCE_CONDITION":
            if label not in sources or not source_quote.strip():
                errors.append("Câu hỏi thuộc tính phải có nguồn và trích đoạn điều kiện thực tế")
            elif source_quote not in sources[label]["text"]:
                errors.append("Trích đoạn điều kiện phải khớp nguyên văn nguồn được cấp")
            else:
                citations.setdefault(label, source_quote)
        elif label or source_quote:
            errors.append("Câu hỏi nhận diện hoặc phạm vi không được gắn nguồn pháp lý giả định")
        if basis == "QUESTION_SCOPE":
            folded = _folded(item["question"])
            if re.search(r"\bhs\b", folded) and re.search(r"\bqa\b", folded):
                errors.append("Không yêu cầu người dùng chọn tên luồng HS hoặc QA")
    if review["decision"] == "KEEP":
        reason_check = {**_failed_answer(), "answer": review["reason"]}
        errors.extend(validate_answer(reason_check, context)["errors"])
        return answer, _safe_errors(errors)
    questions = [item["question"] for item in clarifications]
    all_citations = {citation["label"]: citation["quote"] for citation in retained_citations}
    all_citations.update(citations)
    proposed = {
        **_failed_answer(),
        "status": "MISSING_PRODUCT_INFO",
        "answer": " ".join(
            part
            for part in [
                retained_text,
                review["reason"],
                *questions,
                *[f"[{label}]" for label in citations],
            ]
            if part
        ),
        "citations": [{"label": label, "quote": value} for label, value in all_citations.items()],
        "missing_information": questions,
    }
    errors.extend(validate_answer(proposed, context)["errors"])
    return proposed, _safe_errors(errors)


def review_decision(
    context: dict,
    answer: dict,
    client,
    *,
    model: str | None = None,
    allow_fallback: bool = False,
    timings: dict | None = None,
) -> tuple[dict, dict]:
    """Run one independent review and at most one repair, without issuing an HS code."""
    timings = {} if timings is None else timings
    for key in ("llm_ms", "decision_review_llm_ms", "validation_ms"):
        timings.setdefault(key, 0.0)
    started = perf_counter()
    registry_protocol = context.get("response_protocol") == "registry-v2"
    review_schema = MODEL_DECISION_REVIEW_SCHEMA if registry_protocol else DECISION_REVIEW_SCHEMA
    payload = {
        "question": context["question"],
        "sources": context["sources"],
        "current_answer": answer,
    }
    if registry_protocol:
        payload.update(
            user_context=context["user_context"],
            sources=model_sources(context["sources"]),
        )
    messages = [
        {"role": "system", "content": DECISION_REVIEW_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                payload,
                ensure_ascii=False,
            ),
        },
    ]
    attempts: list[dict] = []
    proposed = _failed_answer()
    for index in range(2):
        call_started = perf_counter()
        try:
            generation = client.complete(
                messages,
                review_schema,
                model=model if index == 0 else attempts[0].get("model", model),
                allow_fallback=allow_fallback if index == 0 else False,
            )
        except LLMError as exc:
            elapsed = (perf_counter() - call_started) * 1000
            timings["llm_ms"] += elapsed
            timings["decision_review_llm_ms"] += elapsed
            attempts.append(
                {
                    "valid": False,
                    "errors": ["Không thể thực hiện kiểm tra nhu cầu và dữ kiện"],
                    "http_status": exc.status,
                    "provider": exc.provider,
                    "model": exc.model,
                    "error_code": exc.error_code,
                    "retry_after": exc.retry_after,
                    "elapsed_ms": elapsed,
                    "failures": [
                        {
                            "provider": exc.provider,
                            "model": exc.model,
                            "http_status": exc.status,
                            "error_code": exc.error_code,
                            "retry_after": exc.retry_after,
                            **({"request_budget": exc.budget} if hasattr(exc, "budget") else {}),
                        }
                    ],
                    **({"request_budget": exc.budget} if hasattr(exc, "budget") else {}),
                }
            )
            proposed = _failed_answer()
            break
        elapsed = (perf_counter() - call_started) * 1000
        timings["llm_ms"] += elapsed
        timings["decision_review_llm_ms"] += elapsed
        validation_started = perf_counter()
        try:
            review = json.loads(generation["content"])
        except (json.JSONDecodeError, TypeError):
            review = {}
        protocol_errors: list[str] = []
        if registry_protocol:
            review, protocol_errors = decode_decision_review(review, context)
        proposed, errors = _checked_decision(review, context, answer)
        errors.extend(protocol_errors)
        if generation.get("finish_reason") != "stop":
            errors.append("Lượt kiểm tra nhu cầu và dữ kiện chưa hoàn tất bình thường")
        timings["validation_ms"] += (perf_counter() - validation_started) * 1000
        attempts.append(
            {
                **generation,
                "elapsed_ms": generation.get("elapsed_ms", elapsed),
                "review": review,
                "valid": not errors,
                "errors": errors,
            }
        )
        if not errors:
            break
        proposed = _failed_answer()
        if index == 0:
            messages.extend(
                [
                    {"role": "assistant", "content": generation["content"]},
                    {"role": "user", "content": format_decision_review_repair_prompt(errors)},
                ]
            )
    last = attempts[-1]
    metadata = {
        **last,
        "attempts": attempts,
        "elapsed_ms": sum(attempt.get("elapsed_ms", 0) for attempt in attempts),
        "wall_ms": (perf_counter() - started) * 1000,
        "usage": {
            key: sum(attempt.get("usage", {}).get(key, 0) for attempt in attempts)
            for key in ("prompt_tokens", "completion_tokens", "total_tokens")
        },
        "failures": [failure for attempt in attempts for failure in attempt.get("failures", [])],
        "requested_model": attempts[0].get("requested_model", model),
        "fallback_used": any(attempt.get("fallback_used", False) for attempt in attempts),
        "prompt_hash": digest(DECISION_REVIEW_PROMPT),
        "schema_hash": digest(review_schema),
    }
    return proposed, metadata
