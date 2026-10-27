"""Share comparison matrices only between jobs for the same item and evidence scope."""

import json
from copy import deepcopy
from typing import Any

from rag.llm.evidence.conditions import condition_id_schema, sources_with_spans
from rag.llm.evidence.proof_contract import id_only_fact_schema, product_fact_ids
from rag.llm.validation.answer import schema_errors
from rag.prompts.generation.task_answering import SHARED_COMPARISON_SCHEMA
from rag.prompts.schemas.review_slots import review_slots

SHARED_FIELDS = (
    "candidate_evidence",
    "review_scope",
    "required_comparison_codes",
    "required_branch_groups",
)
PROOF_FIELDS = ("candidate_assessments", "candidate_group_assessments", "branch_checks")


def review_packet(payload: dict, schema: dict) -> tuple[dict, dict, dict]:
    packet, wire = deepcopy(payload), deepcopy(schema)
    packet["sources"] = sources_with_spans(packet["sources"])
    packet["product_fact_ids"] = product_fact_ids(packet["user_context"])
    for job in packet["jobs"]:
        job["allowed_fact_ids"] = [
            ref for ref in job["allowed_fact_ids"] if ref in packet["product_fact_ids"]
        ]
    groups: list[dict] = []
    keys: dict[str, str] = {}
    bindings: dict[str, str] = {}
    for job in packet["jobs"]:
        common = {key: job.pop(key) for key in SHARED_FIELDS}
        common["item_id"] = job["item"]["id"]
        common["allowed_fact_ids"] = job["allowed_fact_ids"]
        key = json.dumps(common, sort_keys=True, ensure_ascii=False)
        if key not in keys:
            gid = f"C{len(groups) + 1}"
            keys[key] = gid
            groups.append({"comparison_id": gid, **common})
        job["comparison_id"] = keys[key]
        bindings[job["result_id"]] = keys[key]
    packet["comparison_contexts"] = groups
    if not packet["jobs"]:
        wire["properties"].pop("reviews", None)
        wire["properties"].pop("comparison_reviews", None)
        wire["required"] = [
            k for k in wire.get("required", []) if k not in {"reviews", "comparison_reviews"}
        ]
    else:
        review = wire["properties"]["reviews"]["items"]["properties"]["review"]
        shared: dict[str, Any] = deepcopy(SHARED_COMPARISON_SCHEMA)
        for key in PROOF_FIELDS:
            shared["items"]["properties"][key] = deepcopy(review["properties"][key])
            review["properties"].pop(key, None)
        review["required"] = [key for key in review["required"] if key not in PROOF_FIELDS]
        # Roles are derived from the matrix, never assigned by the model.
        checks = review["properties"]["condition_checks"]["items"]["properties"]
        checks.pop("proof_role", None)
        checks.pop("target_codes", None)
        shared["items"]["properties"]["comparison_id"]["enum"] = [
            g["comparison_id"] for g in groups
        ]
        shared.update(minItems=len(groups), maxItems=len(groups))
        wire["properties"]["comparison_reviews"] = shared
        wire["required"].append("comparison_reviews")

    from rag.prompts.schemas.proof import catalogue_schema, proof_schema

    base = id_only_fact_schema(condition_id_schema(wire))
    if payload.get("reasoning_contract") == "semantic-v1":
        from rag.llm.contracts.obligations import compact_schema

        base = compact_schema(base)
    else:
        base = proof_schema(base)
    wire, packet["review_slots"] = review_slots(packet, base)
    return (
        packet,
        wire if payload.get("reasoning_contract") == "semantic-v1" else catalogue_schema(wire),
        bindings,
    )


def expand_comparisons(value: dict, bindings: dict) -> tuple[dict, list[str]]:
    """Accept saved legacy per-job proofs, but never merge contradictory representations."""
    if "comparison_reviews" not in value:
        return value, []
    from rag.llm.contracts.errors import ContractIssue

    shared = value["comparison_reviews"]
    if not isinstance(shared, list):
        return value, [
            ContractIssue(
                "Ma trận không đúng cấu trúc.", code="SCHEMA_VIOLATION", path="comparison_reviews"
            )
        ]
    matrices: dict[str, dict] = {}
    errors: list[str] = []
    for gid in set(bindings.values()):
        matches = [
            row for row in shared if isinstance(row, dict) and row.get("comparison_id") == gid
        ]
        failures = (
            schema_errors(matches[0], SHARED_COMPARISON_SCHEMA["items"])
            if len(matches) == 1
            else ["Ma trận thiếu hoặc lặp."]
        )
        if failures:
            errors.extend(
                ContractIssue(
                    f"{rid}: {error}",
                    code="CANDIDATE_COVERAGE_MISSING",
                    path=f"{rid}/comparison_reviews/{gid}",
                )
                for rid, group in bindings.items()
                if group == gid
                for error in failures
            )
        else:
            matrices[gid] = matches[0]
    result = deepcopy(value)
    result.pop("comparison_reviews")
    valid_rows = []
    for row in result.get("reviews", []):
        if not isinstance(row, dict) or row.get("result_id") not in bindings:
            continue
        rid = row["result_id"]
        matrix = matrices.get(bindings[rid])
        if matrix is None or not isinstance(row.get("review"), dict):
            continue
        conflict = False
        for key in PROOF_FIELDS:
            proof = matrix.get(key, [])
            if key in row["review"] and row["review"][key] != proof:
                errors.append(
                    ContractIssue(
                        f"{rid}: Chứng minh riêng mâu thuẫn ma trận.",
                        code="SCHEMA_VIOLATION",
                        path=f"{rid}/comparison_reviews",
                    )
                )
                conflict = True
            row["review"][key] = deepcopy(proof)
        if not conflict:
            valid_rows.append(row)
    result["reviews"] = valid_rows
    return result, errors
