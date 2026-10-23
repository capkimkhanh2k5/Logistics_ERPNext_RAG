"""Backend-owned semantic review boundaries; registered references are not entailment."""

import re
from copy import deepcopy
from datetime import date

from rag.llm.contracts.errors import ContractIssue


def draft_packet(payload: dict) -> dict:
    """Keep every rival discoverable; full decision evidence stays in review packets."""
    if "request" not in payload:
        return payload
    packet = deepcopy(payload)
    packet["comparison_candidates"] = []
    for candidate in payload.get("comparison_candidates", []):
        projection = {
            key: candidate[key]
            for key in (
                "code",
                "hierarchy_status",
                "wording_evidence_id",
                "required_citation_evidence_ids",
            )
            if key in candidate
        }
        if "hierarchy" in candidate:
            projection["hierarchy"] = {"status": candidate["hierarchy"]["status"]}
        packet["comparison_candidates"].append(projection)
    return packet


def compact_schema(schema: dict) -> dict:
    """Keep semantic slots and references without asking a model for a formal graph."""
    value = deepcopy(schema)
    removed = {
        "proof",
        "reason_proof",
        "proof_key",
        "reason_proof_key",
        "proof_catalogue",
        "fact_ledger",
    }

    def visit(node):
        if isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, dict):
            properties = node.get("properties", {})
            for key in removed:
                properties.pop(key, None)
            if "required" in node:
                node["required"] = [key for key in node["required"] if key not in removed]
            for child in node.values():
                visit(child)

    visit(value)
    return value


def statement_role(text: str) -> str:
    from rag.llm.validation.answer import _folded

    folded = _folded(text).strip()
    if (
        "?" in text
        or re.search(r"\b(?:co|da)\b.+\b(?:khong|chua)$", folded)
        or re.match(r"^(?:lieu|co phai|cho biet|hay|vui long|tim|tra cuu)\b", folded)
    ):
        return "QUESTION"
    if re.search(r"\b(?:gia su|gia dinh|assuming|hypothetically)\b|^(?:neu|if)\b", folded):
        return "HYPOTHETICAL"
    if re.search(r"\b(?:chua biet|chua ro|khong ro|chua xac nhan|khong chac)\b", folded):
        return "UNKNOWN"
    return "ASSERTED"


def fact_errors(refs: list[str], context: dict) -> list[str]:
    statements = {s["id"]: s for s in context["user_context"]["statements"]}
    errors: list[str] = []
    for ref in refs:
        if ref not in statements or statement_role(statements[ref]["text"]) != "ASSERTED":
            errors.append(
                ContractIssue(
                    "Dữ kiện áp dụng cần lời khai khẳng định, không là câu hỏi/giả định hoặc chưa biết.",
                    code="FACT_ASSESSMENT_MISMATCH",
                    path=f"facts/{ref}",
                )
            )
    return errors


def requests_current(text: str) -> bool:
    from rag.llm.validation.answer import _folded

    folded = _folded(text)
    for match in re.finditer(
        r"hien hanh|hien nay|ap dung hien tai|con hieu luc|currently|current (?:law|regulation|requirement)",
        folded,
    ):
        prefix = re.split(r"[.;,!?]", folded[: match.start()])[-1]
        if not re.search(
            r"(?:khong|chua)\s+(?:hoi|yeu cau|xac dinh|chung nhan|xac minh|can|tra cuu)|khong\s*$",
            prefix,
        ):
            return True
    return False


def temporal_errors(evidence_ids: list[str], context: dict) -> list[str]:
    """An explicit historical date needs a complete applicable interval for expired law."""

    def parsed(value):
        try:
            return date.fromisoformat(str(value)[:10]) if value else None
        except ValueError:
            return None

    supplied = context.get("as_of")
    requested = parsed(supplied) if supplied else date.today()
    sources = {s["evidence_id"]: s for s in context["sources"]}
    errors: list[str] = []
    for eid in evidence_ids:
        source = sources.get(eid, {})
        before, after = parsed(source.get("effective_from")), parsed(source.get("effective_to"))
        status = source.get("legal_status", "")
        historical_interval = bool(
            supplied
            and requested
            and requested < date.today()
            and before
            and after
            and before <= requested <= after
        )
        invalid = not requested or (before and before > requested) or (after and after < requested)
        invalid = (
            invalid
            or (source.get("effective_from") and before is None)
            or (source.get("effective_to") and after is None)
        )
        if status in {"EXPIRED", "REPEALED"}:
            invalid = invalid or not historical_interval
        elif context.get("legal_scope") != "SOURCE_SNAPSHOT":
            invalid = invalid or status not in {"CURRENT", "IN_FORCE"}
        if invalid:
            errors.append(
                ContractIssue(
                    "Chưa đủ căn cứ hiệu lực của phiên bản nguồn tại ngày áp dụng.",
                    code="SOURCE_TEMPORAL_UNPROVEN",
                    path=f"sources/{eid}",
                )
            )
    return errors


def review_obligations(jobs: list[dict], analyses: list[dict]) -> list[dict]:
    """Immutable job/claim scope, not an inferred catalogue of legal predicates."""
    return [
        {
            "owner": job["result_id"],
            "kind": "CLASSIFICATION",
            "item_ids": [job["item"]["id"]],
            "level": job["objective"]["level"],
            "prerequisites": job["prerequisites"],
            "required_codes": job["required_comparison_codes"],
            "release_requires": "ALL_APPLICABLE_CONDITIONS_AND_UNIQUENESS",
        }
        for job in jobs
    ] + [
        {
            "owner": job["result_id"],
            "kind": "CLAIM",
            "claim_index": claim["claim_index"],
            "item_ids": job["item_ids"],
            "target": claim["text"],
            "release_requires": "SEMANTIC_ENTAILMENT_AND_FACT_CONSISTENCY",
        }
        for job in analyses
        for claim in job["claims"]
    ]
