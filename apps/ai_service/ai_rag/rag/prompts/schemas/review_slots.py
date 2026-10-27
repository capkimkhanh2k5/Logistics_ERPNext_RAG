"""Backend-owned review keys and candidate-specific evidence domains."""

from copy import deepcopy
from typing import Any


def keyed(schema: dict, keys: list[str], identity: str) -> dict:
    properties = {}
    for key in keys:
        item = deepcopy(schema["items"])
        item["properties"].pop(identity, None)
        item["required"] = [field for field in item["required"] if field != identity]
        properties[key] = item
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": keys,
    }


def review_slots(packet: dict, wire: dict) -> tuple[dict, dict]:
    value = deepcopy(wire)
    props = value["properties"]
    layout: dict[str, Any] = {
        "reviews": [job["result_id"] for job in packet["jobs"]],
        "analysis_reviews": {
            job["result_id"]: {
                "checks": [str(c["claim_index"]) for c in job["claims"]],
                "coverage_checks": job["coverage_evidence_ids"],
            }
            for job in packet["analysis_jobs"]
        },
        "comparison_reviews": {
            group["comparison_id"]: group["required_comparison_codes"]
            for group in packet["comparison_contexts"]
        },
    }
    if packet["jobs"]:
        props["reviews"] = keyed(props["reviews"], layout["reviews"], "result_id")
        for job in packet["jobs"]:
            props["reviews"]["properties"][job["result_id"]]["properties"]["selected_code"][
                "enum"
            ] = job["selection_codes"]
        groups = layout["comparison_reviews"]
        props["comparison_reviews"] = keyed(
            props["comparison_reviews"], list(groups), "comparison_id"
        )
        for group in packet["comparison_contexts"]:
            fields = props["comparison_reviews"]["properties"][group["comparison_id"]]["properties"]
            # One proof may serve several codes only after per-member domain checks.
            assessment = deepcopy(fields["candidate_assessments"]["items"])
            assessment["properties"].pop("code", None)
            assessment["properties"]["codes"] = {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"type": "string", "enum": group["required_comparison_codes"]},
            }
            assessment["required"] = [
                "codes" if field == "code" else field for field in assessment["required"]
            ]
            candidates = {c["code"]: c for c in group["candidate_evidence"]}
            domains = {
                code: candidates.get(code, {}).get("required_citation_evidence_ids", [])
                for code in group["required_comparison_codes"]
            }
            layout.setdefault("candidate_domains", {})[group["comparison_id"]] = domains
            allowed = sorted({eid for ids in domains.values() for eid in ids})
            if allowed:
                assessment["properties"]["decisive_evidence_ids"]["items"] = {
                    "type": "string",
                    "enum": allowed,
                }
            else:
                assessment["properties"]["decisive_evidence_ids"]["maxItems"] = 0
            fields.pop("candidate_assessments")
            fields["candidate_group_assessments"] = {
                "type": "array",
                "minItems": 1 if domains else 0,
                "maxItems": len(domains),
                "items": assessment,
            }
            container = props["comparison_reviews"]["properties"][group["comparison_id"]]
            container["required"] = [
                "candidate_group_assessments" if field == "candidate_assessments" else field
                for field in container["required"]
            ]
    else:
        props.pop("reviews", None)
        props.pop("comparison_reviews", None)
        value["required"] = [
            k for k in value.get("required", []) if k not in {"reviews", "comparison_reviews"}
        ]
    if packet.get("reasoning_contract") == "semantic-v1":
        condition_layout = layout.setdefault("condition_checks", {})
        for job in packet["jobs"]:
            required = set(job.get("note_scope_evidence_ids", []))
            common = next(
                group
                for group in packet["comparison_contexts"]
                if group["comparison_id"] == job["comparison_id"]
            )
            for candidate in common["candidate_evidence"]:
                if candidate["code"] in job["selection_codes"]:
                    required.update(candidate.get("required_citation_evidence_ids", []))
                    if candidate.get("note_scope_required"):
                        required.update(candidate.get("related_note_evidence_ids", []))
            rid = job["result_id"]
            condition_layout[rid] = sorted(required)
            fields = props["reviews"]["properties"][rid]["properties"]["review"]["properties"]
            # Repeating a nested object per source exceeds Gemini's schema complexity
            # on real leaf scopes. Encode once; exact coverage is checked on decode.
            checks = fields["condition_checks"]
            checks["items"]["properties"]["evidence_id"] = (
                {"type": "string", "enum": sorted(required)}
                if required and len(required) <= 15
                else {"type": "string"}
            )
            checks.update(minItems=len(required), maxItems=len(required))
    if packet["analysis_jobs"]:
        props["analysis_reviews"] = keyed(
            props["analysis_reviews"], list(layout["analysis_reviews"]), "result_id"
        )
        for rid, slots in layout["analysis_reviews"].items():
            fields = props["analysis_reviews"]["properties"][rid]["properties"]
            fields["checks"] = keyed(fields["checks"], slots["checks"], "claim_index")
            if len(slots["coverage_checks"]) > 8:
                checks = fields["coverage_checks"]
                checks["items"]["properties"]["evidence_id"] = {
                    "type": "string",
                    "enum": sorted(slots["coverage_checks"]),
                }
                checks.update(minItems=0, maxItems=len(slots["coverage_checks"]))
            else:
                fields["coverage_checks"] = keyed(
                    fields["coverage_checks"], slots["coverage_checks"], "evidence_id"
                )
            if (
                slots["coverage_checks"]
                and "coverage_checks"
                not in props["analysis_reviews"]["properties"][rid]["required"]
            ):
                props["analysis_reviews"]["properties"][rid]["required"].append("coverage_checks")
    return value, layout
