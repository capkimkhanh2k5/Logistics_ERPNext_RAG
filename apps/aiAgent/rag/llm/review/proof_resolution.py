"""Deterministic downgrades only from a valid generic proof, never from an error label."""

from copy import deepcopy

from rag.llm.evidence.conditions import condition_span_registry
from rag.llm.validation.proof import evaluate_proof


def resolve_review(value: dict, context: dict) -> dict:
    if not isinstance(value, dict) or not context.get("proof_required"):
        return value
    result = deepcopy(value)
    causes, questions, adjustments = [], [], []
    spans = condition_span_registry(context["sources"])
    fields = [
        (field, result.get(field, []))
        for field in ("condition_checks", "candidate_assessments", "branch_checks")
    ]
    if result.get("status") == "SUPPORTED":
        fields.append(
            (
                "reason_proof",
                [
                    {
                        "assessment": "SATISFIED",
                        "proof": result.get("reason_proof"),
                        "criterion_quote": result.get("reason"),
                    }
                ],
            )
        )
    for field, checks in fields:
        for index, check in enumerate(checks):
            proof, errors = evaluate_proof(
                check.get("proof"), context, target=check.get("criterion_quote")
            )
            if errors or not proof or proof["state"] != "UNKNOWN":
                continue
            old = check.get("assessment")
            if old not in {"SATISFIED", "KNOWN", "RULED_OUT"}:
                continue
            cause = proof["cause"]
            if old == "RULED_OUT":
                check.update(assessment="POSSIBLE", decisive_evidence_ids=[])
            elif old == "KNOWN":
                if cause != "MISSING_PRODUCT_FACT":
                    continue
                check["assessment"] = "MISSING"
                check.update(fact_ids=[], user_quotes=[])
            else:
                check["assessment"] = {
                    "MISSING_PRODUCT_FACT": "MISSING_PRODUCT_INFO",
                    "MISSING_LEGAL_RULE": "INSUFFICIENT_LEGAL_EVIDENCE",
                }.get(cause, "UNRESOLVED_APPLICATION")
                check.update(fact_ids=[], user_quotes=[])
            causes.append(cause)
            adjustments.append(
                {
                    "path": f"{field}/{index}",
                    "from": old,
                    "to": check["assessment"],
                    "proof_id": proof["id"],
                }
            )
            if cause != "MISSING_PRODUCT_FACT":
                continue
            for node in check["proof"]["nodes"]:
                refs = node["condition_ids"]
                if (
                    node["operator"] != "ATOM"
                    or node["cause"] != "MISSING_PRODUCT_FACT"
                    or not node["attribute"]
                    or not refs
                    or any(cid not in spans for cid in refs)
                ):
                    continue
                quotes = [
                    {"evidence_id": spans[cid]["evidence_id"], "quote": spans[cid]["quote"]}
                    for cid in refs
                ]
                question_text = f"Vui lòng cho biết {node['attribute']} của mặt hàng đang xét."
                question_node = {**deepcopy(node), "text": question_text}
                question_proof = {
                    "target": question_text,
                    "decomposition_review": "FAITHFUL_COMPLETE",
                    "ledger_review": check["proof"]["ledger_review"],
                    "root": node["key"],
                    "nodes": [question_node],
                }
                questions.append(
                    {
                        "question": question_text,
                        "proof": question_proof,
                        "attribute": node["attribute"],
                        "evidence_ids": list(dict.fromkeys(q["evidence_id"] for q in quotes)),
                        "condition_ids": refs,
                        "criterion_quote": quotes[0]["quote"],
                        **({"criterion_quotes": quotes} if len(quotes) > 1 else {}),
                    }
                )
    if causes and result.get("status") == "SUPPORTED":
        if "MISSING_LEGAL_RULE" in causes:
            result.update(
                status="INSUFFICIENT_LEGAL_EVIDENCE",
                clarifications=[],
                missing_legal_evidence=[
                    "Nguồn hiện có chưa chứng minh đầy đủ điều kiện áp dụng đang xét."
                ],
            )
        elif questions and set(causes) == {"MISSING_PRODUCT_FACT"}:
            result.update(
                status="MISSING_PRODUCT_INFO", clarifications=questions, missing_legal_evidence=[]
            )
        else:
            result.update(status="REQUIRES_REVIEW", clarifications=[], missing_legal_evidence=[])
    # A withheld decision renders backend text. Model prose remains only in the raw trace.
    if result.get("status") != "SUPPORTED":
        result["reason"] = {
            "MISSING_PRODUCT_INFO": "Chưa đủ dữ kiện để xác nhận điều kiện quyết định.",
            "INSUFFICIENT_LEGAL_EVIDENCE": "Nguồn hiện có chưa chứng minh đầy đủ điều kiện áp dụng đang xét.",
            "REJECTED": "Ứng viên đang xét có điều kiện cần bị bác bỏ; các nhánh khác vẫn cần được kiểm tra.",
            "REQUIRES_REVIEW": "Chưa phân định được cách áp dụng các điều kiện trong nguồn.",
        }.get(result.get("status", ""), "Chưa hoàn tất kiểm tra chứng minh.")
    context.setdefault("proof_adjustments", []).extend(adjustments)
    return result


def resolve_analysis(check: dict, claim: dict, context: dict) -> dict:
    if not context.get("proof_required"):
        return check
    proof, errors = evaluate_proof(
        check.get("proof"),
        context,
        target=claim["text"],
        evidence_ids=check["evidence_ids"],
        fact_ids=check["fact_ids"],
    )
    if (
        errors
        or not proof
        or proof["state"] == "PROVEN"
        or check["assessment"]
        not in {"APPLICATION", "REFERENCE", "CONDITIONAL_APPLICATION", "FACT_SUPPORTED"}
    ):
        return check
    result = deepcopy(check)
    result["assessment"] = (
        "FACT_UNSUPPORTED"
        if claim["kind"] == "PRODUCT_FACT"
        else "INSUFFICIENT_LEGAL_EVIDENCE"
        if proof["cause"] == "MISSING_LEGAL_RULE"
        else "UNRESOLVED_APPLICATION"
    )
    result["reason"] = "Nhận định chưa có chứng minh đầy đủ từ dữ kiện và nguồn đang được kiểm tra."
    context.setdefault("proof_adjustments", []).append(
        {
            "claim_index": check["claim_index"],
            "from": check["assessment"],
            "to": result["assessment"],
            "proof_id": proof["id"],
        }
    )
    return result
