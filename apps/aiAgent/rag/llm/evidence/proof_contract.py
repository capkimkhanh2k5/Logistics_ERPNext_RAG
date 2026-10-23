"""Backend-owned proof roles and candidate outcomes; never infer legal applicability."""

from copy import deepcopy

from rag.prompts.schemas.statuses import CANDIDATE_OUTCOMES


def bind_fact_quotes(value, context: dict):
    """IDs may select complete registered spans; explicit quotes still require validation."""
    statements = {s["id"]: s["text"] for s in context.get("user_context", {}).get("statements", [])}

    def bind(node):
        if isinstance(node, list):
            return [bind(child) for child in node]
        if not isinstance(node, dict):
            return node
        result = {key: bind(child) for key, child in node.items()}
        if "fact_ids" in result and "user_quotes" not in result:
            refs = result["fact_ids"]
            if isinstance(refs, list):
                result["user_quotes"] = [
                    statements[ref] for ref in refs if isinstance(ref, str) and ref in statements
                ]
        return result

    return bind(value)


def proof_roles(value: dict, context: dict, code: str) -> dict:
    """Classify checks from their actual candidate evidence and exclusion assessment."""
    result = deepcopy(value)
    sources = {s["label"]: s["evidence_id"] for s in context["sources"]}
    candidates = {
        c["code"]: c
        for c in [*context["candidate_evidence"], *context.get("comparison_candidates", [])]
    }
    required = {
        sources[label]
        for label in candidates.get(code, {}).get("required_citation_labels", [])
        if label in sources
    }
    exclusions = {
        row["code"]: set(row.get("decisive_evidence_ids", row["evidence_ids"]))
        & {
            sources[label]
            for label in candidates.get(row["code"], {}).get("required_citation_labels", [])
            if label in sources
        }
        for row in result.get("candidate_assessments", [])
        if row["assessment"] == "RULED_OUT"
    }
    for check in result["condition_checks"]:
        eid = check["evidence_id"]
        targets = sorted(peer for peer, ids in exclusions.items() if peer != code and eid in ids)
        if not targets:
            targets = sorted(
                peer
                for peer in exclusions
                if peer != code
                and eid
                in {
                    sources[label]
                    for label in candidates.get(peer, {}).get("required_citation_labels", [])
                    if label in sources
                }
            )
        # A shared mandatory source cannot be relabelled as an exclusion to bypass it.
        exclusion = eid not in required and targets and check["assessment"] == "CONTRADICTED"
        check["proof_role"] = "EXCLUSION" if exclusion else "APPLICABILITY"
        check["target_codes"] = targets if exclusion else [code]
    rejected = code in exclusions and any(
        check["evidence_id"] in required & exclusions[code]
        and check["assessment"] == "CONTRADICTED"
        and check["fact_ids"]
        and check["user_quotes"]
        for check in result["condition_checks"]
    )
    # Legacy statuses are normalized only when both representations state rejection.
    # Source, quote, subject and exclusion-proof validation still runs afterwards.
    if rejected and result["status"] != "SUPPORTED":
        result.update(status="REJECTED", clarifications=[], missing_legal_evidence=[])
    return result


def candidate_outcome(review: dict) -> str:
    return CANDIDATE_OUTCOMES.get(review.get("status", ""), "INVALID")


def id_only_fact_schema(schema: dict) -> dict:
    """Remove duplicated quote-writing from the current wire, keeping legacy decoding."""
    value = deepcopy(schema)

    def walk(node):
        if isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            properties = node.get("properties", {})
            if "fact_ids" in properties and "user_quotes" in properties:
                properties.pop("user_quotes")
                node["required"] = [k for k in node.get("required", []) if k != "user_quotes"]
            for child in node.values():
                walk(child)

    walk(value)
    return value


def product_fact_ids(user_context: dict) -> list[str]:
    """Exclude statements already rejected as legal content by product validators.

    This is a presentation filter, not fact verification or a supersession ledger.
    Original statements stay available for provenance and legacy decoding.
    """
    from rag.llm.contracts.obligations import statement_role
    from rag.llm.validation.answer import LEGAL_INFORMATION, _folded

    return [
        s["id"]
        for s in user_context.get("statements", [])
        if not LEGAL_INFORMATION.search(_folded(s["text"]))
        and statement_role(s["text"]) == "ASSERTED"
    ]
