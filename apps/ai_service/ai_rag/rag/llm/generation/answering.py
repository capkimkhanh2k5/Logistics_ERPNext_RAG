"""Generate, repair and review grounded answers over locked retrieval outputs."""

import json
from time import perf_counter

from rag.llm.contracts.errors import ContractIssue, LLMError
from rag.llm.evidence.evidence import (
    decode_answer,
    decode_product_review,
    model_candidate,
    model_sources,
)
from rag.llm.providers.budget import ContextBudgetError
from rag.llm.providers.client import RAGClient
from rag.llm.providers.groq_client import GroqClient
from rag.llm.review.decision_review import review_decision
from rag.llm.review.disambiguation import review_scope
from rag.llm.validation.answer import (
    LEGAL_INFORMATION,
    _folded,
    _normalized,
    schema_errors,
    validate_answer,
)
from rag.llm.validation.quantitative import quantitative_grounding_errors
from rag.prompts.core.repair import format_product_review_repair_prompt, format_repair_prompt
from rag.prompts.review.product_review import PRODUCT_REVIEW_PROMPT
from rag.prompts.schemas.answer import (
    MODEL_ANSWER_SCHEMA,
    MODEL_DISAMBIGUATION_REVIEW_SCHEMA,
    MODEL_PRODUCT_REVIEW_SCHEMA,
    PRODUCT_REVIEW_SCHEMA,
)
from rag.utils.files import digest


def _legal_abstention(gaps: list[str]) -> dict:
    return {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Chưa đủ chứng cứ pháp lý trong ngữ cảnh được truy xuất để kết luận. Hệ thống cần bổ sung chứng cứ.",
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
        "answer": "Bước kiểm tra dữ kiện hàng hóa chưa hoàn tất hợp lệ; hệ thống chưa phát hành mã HS.",
    }


def _complete(client, messages, schema, timings: dict, phase: str, **kwargs) -> dict:
    started = perf_counter()
    try:
        return client.complete(messages, schema, **kwargs)
    except LLMError as exc:
        exc.timings = timings
        raise
    finally:
        elapsed = (perf_counter() - started) * 1000
        timings["llm_ms"] += elapsed
        timings[f"{phase}_llm_ms"] += elapsed


def _safe_diagnostic_errors(errors: list[str]) -> list[str]:
    return [
        "Phản hồi kiểm tra không đúng cấu trúc JSON bắt buộc." if error.startswith("/") else error
        for error in errors
    ]


def _review_diagnostics(context: dict, candidate: dict, review: dict) -> dict:
    reasons = _safe_diagnostic_errors(review.get("errors", []))
    if (
        review.get("http_status") is not None
        and review.get("error_code") != "context_length_exceeded"
    ):
        reasons.append(f"Dịch vụ kiểm tra phản hồi HTTP {review['http_status']}.")
    if review.get("valid"):
        reasons = [review["review"]["reason"]]
    known = {source["label"] for source in context["sources"]}
    labels = set(candidate["required_citation_labels"])
    if review.get("valid"):
        labels.update(check["source_label"] for check in review["review"]["condition_checks"])
    return {
        "stage": "product_review",
        "code": "PRODUCT_REVIEW_BLOCKED" if review.get("valid") else "PRODUCT_REVIEW_FAILED",
        "reasons": list(dict.fromkeys(reasons)),
        "candidate_hs_code": candidate["code"],
        "source_labels": sorted(labels & known, key=lambda label: int(label[1:])),
    }


def _clarification_diagnostics(context: dict, answer: dict) -> dict:
    cited = {citation["label"] for citation in answer["citations"]}
    candidates = [
        candidate
        for candidate in context.get("candidate_evidence", [])
        if candidate["wording_label"] in cited and candidate["hierarchy"]["status"] == "VERIFIED"
    ]
    if len(candidates) != 1:
        return {}
    candidate = candidates[0]
    return {
        "stage": "generation",
        "code": "CLASSIFICATION_NOT_CONCLUDED",
        "reasons": [],
        "candidate_hs_code": candidate["code"],
        "source_labels": candidate["required_citation_labels"],
    }


def _check_abstention(context, answer, generation, client, timings, *, allow_fallback=False):
    reviewed, details = review_decision(
        context,
        answer,
        client,
        model=generation.get("model"),
        allow_fallback=allow_fallback,
        timings=timings,
    )
    generation["decision_review"] = details
    generation["elapsed_ms"] = generation.get("elapsed_ms", 0) + details.get("elapsed_ms", 0)
    usage = generation.setdefault("usage", {})
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        usage[key] = usage.get(key, 0) + details.get("usage", {}).get(key, 0)
    if generation.get("skipped"):
        generation.update(
            model=details.get("model"),
            provider=details.get("provider"),
            main_skipped=True,
            skipped=False,
            requested_model=details.get("requested_model"),
            fallback_used=details.get("fallback_used", False),
            failures=details.get("failures", []),
        )
    if (
        details.get("valid")
        and reviewed["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
        and not reviewed["citations"]
    ):
        reviewed = {**reviewed, "answer": _legal_abstention([])["answer"]}
    return reviewed


def _decision_diagnostics(context: dict, generation: dict, answer: dict) -> dict:
    existing = _clarification_diagnostics(context, answer)
    details = generation.get("decision_review")
    if existing or not details:
        return existing
    review = details.get("review", {})
    return {
        "stage": "decision_review",
        "code": "DECISION_REVIEWED" if details["valid"] else "DECISION_REVIEW_FAILED",
        "reasons": [review["reason"]]
        if details["valid"]
        else _safe_diagnostic_errors(details.get("errors", [])),
        "candidate_hs_code": "",
        "source_labels": [citation["label"] for citation in answer["citations"]],
    }


def check_product_review(
    raw_review: dict,
    context: dict,
    candidate: dict,
    answer: dict,
    labels: set[str],
    finish_reason: str = "stop",
) -> tuple[dict, dict, list[str]]:
    from rag.llm.review.proof_resolution import resolve_review

    raw_review = resolve_review(raw_review, context)
    review = raw_review
    registry_protocol = context.get("response_protocol") == "registry-v2"
    errors: list[str] = []
    if registry_protocol:
        review, errors = decode_product_review(review, context, candidate_code=candidate["code"])
    schema_errs = schema_errors(review, PRODUCT_REVIEW_SCHEMA)
    errors.extend(schema_errs)
    if finish_reason != "stop":
        errors.append("Lượt kiểm tra dữ kiện hàng hóa chưa hoàn tất bình thường")
    if not schema_errs and finish_reason == "stop":
        if not review["reason"].strip():
            errors.append("Kết quả kiểm tra phải giải thích lý do cụ thể")
        sources = {
            source["label"]: source for source in context["sources"] if source["label"] in labels
        }
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
                    "[NON_PRODUCT_QUOTE] Nội dung pháp lý do người dùng nêu không được coi là dữ kiện hàng hóa."
                )
        checked = set()
        for check in review["condition_checks"]:
            label, quote = check["source_label"], _normalized(check["source_quote"])
            if (
                not quote
                or label not in sources
                or quote not in _normalized(sources[label]["text"])
            ):
                errors.append("Trích đoạn điều kiện không khớp nguồn pháp lý được cấp")
            indices = check["product_fact_indices"]
            if any(index >= len(review["product_facts"]) for index in indices):
                errors.append("Điều kiện tham chiếu dữ kiện hàng hóa không tồn tại")
            if check["assessment"] == "SATISFIED":
                if not indices and label in candidate.get("required_citation_labels", []):
                    errors.append("Điều kiện đã đáp ứng phải có dữ kiện người dùng xác nhận")
                checked.add(label)
                if review["status"] == "SUPPORTED" and check.get("proof_role") == "EXCLUSION":
                    errors.append("Ứng viên bị loại trừ bởi điều kiện: " + check["source_quote"])
            elif (
                review["status"] == "SUPPORTED"
                and check.get("proof_role") != "EXCLUSION"
                and (
                    check["assessment"] != "NOT_APPLICABLE"
                    or label in candidate["required_citation_labels"]
                )
            ):
                errors.append(
                    "SUPPORTED không được bỏ qua điều kiện chưa được đáp ứng: "
                    + check["source_quote"]
                    + " ("
                    + check["assessment"]
                    + ")."
                )

        if review["status"] != "SUPPORTED":
            for check in review["condition_checks"]:
                if check["assessment"] == "SATISFIED" and check["source_label"] in sources:
                    errors.extend(
                        quantitative_grounding_errors(
                            {**review, "status": "SUPPORTED", "condition_checks": [check]},
                            {check["source_label"]: {"text": check["source_quote"]}},
                            {check["source_label"]},
                        )
                    )
        if candidate.get("note_scope_required"):
            checks_by_label = {check["source_label"]: check for check in review["condition_checks"]}
            for label in candidate.get("related_note_labels", []):
                if label not in checks_by_label or (
                    review["status"] == "SUPPORTED"
                    and checks_by_label[label]["assessment"] not in {"SATISFIED", "NOT_APPLICABLE", "CONTRADICTED"}
                ):
                    errors.append(
                        ContractIssue(
                            "Chưa đối chiếu phạm vi điều kiện/Chú giải ở mức tổ tiên.",
                            code="REQUIRED_CONDITION_MISSING",
                            path=f"condition_checks/{label}",
                        )
                    )
        if review["status"] == "SUPPORTED":
            errors.extend(
                quantitative_grounding_errors(
                    review,
                    sources,
                    set(candidate["required_citation_labels"]),
                )
            )
            if not set(candidate["required_citation_labels"]) <= checked:
                missing = set(candidate["required_citation_labels"]) - checked
                source_refs = [
                    f"{sources[label].get('evidence_id', label)}: {sources[label]['text'][:200]}"
                    for label in sorted(missing)
                    if label in sources
                ]
                errors.append(
                    "[REQUIRED_CONDITION_MISSING] SUPPORTED chưa có SATISFIED cho điều kiện bắt buộc ở mã/cấp cha/nhánh: "
                    + " | ".join(source_refs)
                )
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
                "status": "REQUIRES_REVIEW" if review["status"] == "REJECTED" else review["status"],
                "missing_information": review["missing_information"],
            }
            if review["status"] == "MISSING_PRODUCT_INFO":
                proposed["answer"] = (
                    review["reason"]
                    + " Cần làm rõ dữ kiện hàng hóa: "
                    + " ".join(review["missing_information"])
                )
            else:
                proposed["answer"] = review["reason"]
            if review["status"] in {"REQUIRES_REVIEW", "REJECTED"} and not any(
                check["assessment"] in {"CONTRADICTED", "UNRESOLVED_APPLICATION"}
                for check in review["condition_checks"]
            ):
                errors.append(
                    "[REVIEW_BASIS_MISSING] REQUIRES_REVIEW chưa có điều kiện bị bác bỏ hoặc cách áp dụng chưa phân định."
                )
            if review["status"] == "REJECTED" and not (
                registry_protocol
                and any(
                    c["code"] == candidate["code"] and c["assessment"] == "RULED_OUT"
                    for c in raw_review.get("candidate_assessments", [])
                )
                and any(
                    c["assessment"] == "CONTRADICTED"
                    and c["source_label"] in candidate["required_citation_labels"]
                    and c["product_fact_indices"]
                    for c in review["condition_checks"]
                )
            ):
                errors.append("[REJECTION_UNPROVEN] Loại ứng viên cần phản chứng của chính mã.")
            cited_checks: dict[str, str] = {}
            for check in sorted(
                review["condition_checks"],
                key=lambda item: item["assessment"] in {"SATISFIED", "NOT_APPLICABLE"},
            ):
                cited_checks.setdefault(check["source_label"], check["source_quote"])
            if registry_protocol:
                question_ids = {
                    eid for q in raw_review["clarifications"] for eid in q["evidence_ids"]
                }
                for source in context["sources"]:
                    if source["evidence_id"] in question_ids:
                        cited_checks.setdefault(source["label"], source["text"])
            proposed["citations"] = [
                {"label": label, "quote": quote} for label, quote in cited_checks.items()
            ]
            if cited_checks:
                proposed["answer"] += " " + " ".join(f"[{label}]" for label in cited_checks)
            errors.extend(validate_answer(proposed, context)["errors"])
    return (proposed if not errors else _review_abstention()), review, errors


def _review_recommendation(
    context: dict,
    answer: dict,
    client: GroqClient | RAGClient,
    model: str,
    timings: dict | None = None,
    repair_of: dict | None = None,
) -> tuple[dict, dict]:
    if context.get("response_protocol") is None:
        from rag.llm.context.normalization import normalize_context

        context = normalize_context(context)
    if timings is None:
        timings = {"llm_ms": 0.0, "product_review_llm_ms": 0.0, "validation_ms": 0.0}
    candidate = next(
        e for e in context["candidate_evidence"] if e["code"] == answer["suggested_hs_code"]
    )
    labels = (
        set(candidate["required_citation_labels"])
        | set(candidate["related_note_labels"])
        | {citation["label"] for citation in answer["citations"]}
    )
    payload = {
        "question": context["question"],
        "proposed_answer": answer,
        "candidate": candidate,
        "sources": [s for s in context["sources"] if s["label"] in labels],
    }
    registry_protocol = context.get("response_protocol") == "registry-v2"
    review_schema = MODEL_PRODUCT_REVIEW_SCHEMA
    comparison = review_scope(context, candidate["code"]) if registry_protocol else []
    if comparison:
        codes = {code for group in comparison for code in group["codes"]}
        peers = [
            e
            for e in [*context["candidate_evidence"], *context.get("comparison_candidates", [])]
            if e["code"] in codes
        ]
        for peer in peers:
            labels.update(peer["required_citation_labels"])
            labels.update(peer["related_note_labels"])
        payload.update(
            candidate_comparison=comparison,
            comparison_candidates=[model_candidate(peer, context["sources"]) for peer in peers],
            sources=[s for s in context["sources"] if s["label"] in labels],
        )
        review_schema = MODEL_DISAMBIGUATION_REVIEW_SCHEMA
    if registry_protocol:
        payload = {
            **payload,
            "user_context": context["user_context"],
            "candidate": model_candidate(candidate, context["sources"]),
            "sources": model_sources(payload["sources"]),
        }
    from rag.llm.evidence.conditions import sources_with_spans
    from rag.prompts.schemas.proof import catalogue_schema, proof_schema

    payload["sources"] = sources_with_spans(payload["sources"])
    review_schema = catalogue_schema(proof_schema(review_schema))
    messages = [
        {"role": "system", "content": PRODUCT_REVIEW_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    if repair_of is not None:
        messages.extend(
            [
                {"role": "assistant", "content": repair_of["content"]},
                {
                    "role": "user",
                    "content": format_product_review_repair_prompt(repair_of["errors"]),
                },
            ]
        )
    try:
        generation = _complete(
            client,
            messages,
            review_schema,
            timings,
            "product_review",
            model=model,
            allow_fallback=False,
        )
    except LLMError as exc:
        return _review_abstention(), {
            "valid": False,
            "errors": [
                "Request kiểm tra dữ kiện vượt ngân sách context của model."
                if isinstance(exc, ContextBudgetError)
                else "Không thể thực hiện kiểm tra dữ kiện hàng hóa"
            ],
            "http_status": exc.status,
            "provider": exc.provider,
            "model": exc.model,
            "error_code": exc.error_code,
            "retry_after": exc.retry_after,
            **({"request_budget": exc.budget} if isinstance(exc, ContextBudgetError) else {}),
        }
    validation_started = perf_counter()
    try:
        from rag.llm.contracts.repair_dispatch import canonicalize

        review, changes = canonicalize(
            json.loads(generation["content"]), context.get("allowed_hs_codes", [])
        )
        generation["canonicalizations"] = changes
    except json.JSONDecodeError:
        review = {}
    from rag.llm.evidence.catalogue import expand_proofs

    review, proof_ref_errors = expand_proofs(review)
    raw_review = review
    proposed, review, errors = check_product_review(
        raw_review, context, candidate, answer, labels, generation["finish_reason"]
    )
    errors.extend(proof_ref_errors)
    details = {
        **generation,
        "review": review,
        "valid": not errors,
        "errors": errors,
        "prompt_hash": digest(PRODUCT_REVIEW_PROMPT),
        "schema_hash": digest(review_schema),
    }
    if comparison:
        details["candidate_disambiguation"] = {
            key: raw_review.get(key, []) if isinstance(raw_review, dict) else []
            for key in ("candidate_assessments", "branch_checks")
        }
    timings["validation_ms"] += (perf_counter() - validation_started) * 1000
    if errors:
        from rag.llm.contracts.repair_dispatch import dispatch

        disposition = dispatch(errors, "product_review")
        details["repair_disposition"] = disposition
        if disposition["withhold"] or not disposition["repair"]:
            return _review_abstention(), details
        if repair_of is None:
            proposed, repaired = _review_recommendation(
                context, answer, client, model, timings, details
            )
            attempts = [details, *repaired.get("attempts", [repaired.copy()])]
            return proposed, {
                **repaired,
                "attempts": attempts,
                "elapsed_ms": sum(item.get("elapsed_ms", 0) for item in attempts),
                "usage": {
                    key: sum(item.get("usage", {}).get(key, 0) for item in attempts)
                    for key in ("prompt_tokens", "completion_tokens", "total_tokens")
                },
            }
        return _review_abstention(), details
    return proposed, details


def generate_answer(
    context: dict,
    client: GroqClient | RAGClient,
    *,
    model: str | None = None,
    allow_fallback: bool = True,
) -> dict:
    from rag.llm.context.normalization import normalize_context

    context = normalize_context(context)
    if context.get("response_protocol") == "goals-v1":
        from rag.llm.generation.task_generation import generate_task_answer

        return generate_task_answer(context, client, model=model, allow_fallback=allow_fallback)
    if context.get("response_protocol") not in (None, "registry-v2"):
        raise ValueError("Ngữ cảnh registry cũ cần được dựng lại từ câu hỏi và retrieval.")
    started = perf_counter()
    timings = {
        "llm_ms": 0.0,
        "answer_llm_ms": 0.0,
        "product_review_llm_ms": 0.0,
        "decision_review_llm_ms": 0.0,
        "validation_ms": 0.0,
    }
    if not context["sources"]:
        answer = _legal_abstention(
            ["Không có nguồn pháp lý dùng được trong giới hạn ngữ cảnh sinh câu trả lời."]
        )
        generation: dict = {"model": model, "elapsed_ms": 0, "skipped": True}
        if context["task"] != "qa":
            answer = _check_abstention(
                context,
                answer,
                generation,
                client,
                timings,
                allow_fallback=allow_fallback,
            )
        validation_started = perf_counter()
        validation = validate_answer(answer, context)
        if generation.get("decision_review"):
            validation["decision_grounding"] = (
                "MODEL_REVIEWED"
                if generation["decision_review"]["valid"]
                else "REVIEW_UNAVAILABLE_OR_INVALID"
            )
        timings["validation_ms"] += (perf_counter() - validation_started) * 1000
        timings["total_ms"] = (perf_counter() - started) * 1000
        return {
            "answer": answer,
            "validation": validation,
            "generation": generation,
            "diagnostics": _decision_diagnostics(context, generation, answer),
            "timings": timings,
        }
    messages = list(context["messages"])
    registry_protocol = context.get("response_protocol") == "registry-v2"
    from rag.prompts.schemas.proof import catalogue_schema, ledger_schema, proof_schema

    answer_schema = catalogue_schema(proof_schema(ledger_schema(MODEL_ANSWER_SCHEMA, [""])))
    attempts: list[dict] = []
    for attempt in range(2):
        try:
            generation = _complete(
                client,
                messages,
                answer_schema,
                timings,
                "answer",
                model=model if not attempts else attempts[0]["model"],
                allow_fallback=allow_fallback if not attempts else False,
            )
        except ContextBudgetError as exc:
            if not attempts:
                raise
            validation["errors"].append(
                "Request sửa câu trả lời vượt ngân sách context của model; chưa thể sửa hợp lệ."
            )
            generation = {**generation, "repair_budget_error": exc.budget}
            break
        validation_started = perf_counter()
        try:
            from rag.llm.contracts.repair_dispatch import canonicalize

            answer, changes = canonicalize(
                json.loads(generation["content"]), context.get("allowed_hs_codes", [])
            )
            generation["canonicalizations"] = changes
        except json.JSONDecodeError:
            answer = {}
        from rag.llm.evidence.catalogue import expand_proofs

        answer, proof_ref_errors = expand_proofs(answer)
        protocol_errors: list[str] = []
        if registry_protocol:
            from rag.llm.evidence.ledger import bind_ledger, bind_ledger_refs

            bound, ledger_errors = bind_ledger(answer, context)
            context.update(bound)
            answer = bind_ledger_refs(answer, context)
            answer, protocol_errors = decode_answer(answer, context)
            protocol_errors.extend(ledger_errors)
            protocol_errors.extend(proof_ref_errors)
        validation = validate_answer(answer, context)
        validation["errors"].extend(protocol_errors)
        validation["valid"] = not validation["errors"]
        if generation["finish_reason"] != "stop":
            validation["errors"].append(
                "Lượt sinh câu trả lời chưa hoàn tất bình thường; kiểm tra giới hạn token đầu ra"
            )
            validation["valid"] = False
        timings["validation_ms"] += (perf_counter() - validation_started) * 1000
        attempts.append({**generation, "validation": validation})
        from rag.llm.contracts.repair_dispatch import dispatch

        disposition = dispatch(validation["errors"], "answer")
        generation["repair_disposition"] = disposition
        if (
            validation["valid"]
            or attempt == 1
            or disposition["withhold"]
            or not disposition["repair"]
        ):
            break
        messages.extend(
            [
                {"role": "assistant", "content": generation["content"]},
                {
                    "role": "user",
                    "content": format_repair_prompt(validation["errors"]),
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
    diagnostics = {}
    if not validation["valid"]:
        errors = validation["errors"]
        selected = answer.get("suggested_hs_code") if isinstance(answer, dict) else None
        candidate = next(
            (
                item
                for item in context.get("candidate_evidence", [])
                if item["code"] == selected and item["hierarchy"]["status"] == "VERIFIED"
            ),
            None,
        )
        known = {source["label"] for source in context["sources"]}
        diagnostics = {
            "stage": "generation_validation",
            "code": "ANSWER_VALIDATION_FAILED",
            "reasons": _safe_diagnostic_errors(errors),
            "candidate_hs_code": candidate["code"] if candidate else "",
            "source_labels": candidate["required_citation_labels"]
            if candidate
            else sorted(known & set(validation.get("cited_labels", []))),
        }
        generation["guardrail_abstention"] = True
        missing_source_chain = any(
            item["code"] == selected and item["hierarchy"]["status"] != "VERIFIED"
            for item in context.get("candidate_evidence", [])
        )
        if missing_source_chain:
            answer = _legal_abstention(
                ["Chuỗi nguồn hoặc mô tả pháp lý của ứng viên chưa được xác minh đầy đủ."]
            )
        else:
            answer = {
                **_review_abstention(),
                "answer": "Phản hồi của model chưa vượt qua kiểm tra cấu trúc hoặc trích dẫn; hệ thống chưa phát hành mã HS.",
            }
        validation_started = perf_counter()
        validation = validate_answer(answer, context)
        timings["validation_ms"] += (perf_counter() - validation_started) * 1000
    if validation["valid"] and answer["status"] == "RECOMMENDATION":
        candidate = next(
            e for e in context["candidate_evidence"] if e["code"] == answer["suggested_hs_code"]
        )
        answer, review = _review_recommendation(
            context, answer, client, generation["model"], timings
        )
        generation["product_review"] = review
        generation["elapsed_ms"] += review.get("elapsed_ms", 0)
        for key in generation["usage"]:
            generation["usage"][key] += review.get("usage", {}).get(key, 0)
        validation_started = perf_counter()
        validation = validate_answer(answer, context)
        timings["validation_ms"] += (perf_counter() - validation_started) * 1000
        validation["semantic_grounding"] = (
            "MODEL_REVIEWED" if review["valid"] else "REVIEW_UNAVAILABLE_OR_INVALID"
        )
        if answer["status"] != "RECOMMENDATION":
            diagnostics = _review_diagnostics(context, candidate, review)
    elif (
        not diagnostics
        and validation["valid"]
        and answer["status"]
        in {
            "MISSING_PRODUCT_INFO",
            "REQUIRES_REVIEW",
            "INSUFFICIENT_LEGAL_EVIDENCE",
        }
    ):
        if (
            context["task"] != "qa"
            and answer["status"] in {"INSUFFICIENT_LEGAL_EVIDENCE", "REQUIRES_REVIEW"}
            and not generation.get("guardrail_abstention")
        ):
            answer = _check_abstention(context, answer, generation, client, timings)
            validation_started = perf_counter()
            validation = validate_answer(answer, context)
            validation["decision_grounding"] = (
                "MODEL_REVIEWED"
                if generation["decision_review"]["valid"]
                else "REVIEW_UNAVAILABLE_OR_INVALID"
            )
            timings["validation_ms"] += (perf_counter() - validation_started) * 1000
        diagnostics = _decision_diagnostics(context, generation, answer)
    generation["proof_contract_version"] = "proof-v2"
    generation["fact_ledger"] = context["user_context"].get("fact_ledger", [])
    generation["proof_catalogue"] = context.get("proof_catalogue", {})
    generation["proof_adjustments"] = context.get("proof_adjustments", [])
    timings["total_ms"] = (perf_counter() - started) * 1000
    return {
        "answer": answer,
        "validation": validation,
        "generation": generation,
        "diagnostics": diagnostics,
        "timings": timings,
    }
