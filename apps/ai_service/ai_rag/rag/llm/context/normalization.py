"""Normalize old caller contexts before selecting any model-facing contract."""

import json
from copy import deepcopy

from rag.llm.evidence.evidence import (
    bind_evidence,
    bind_user_context,
    model_candidate,
    model_sources,
)
from rag.prompts.core.system import SYSTEM_PROMPT
from rag.prompts.generation.tasks import TASK_INSTRUCTIONS
from rag.utils.files import digest


def normalize_context(context: dict) -> dict:
    value = deepcopy(context)
    protocol = value.get("response_protocol")
    if protocol not in {None, "registry-v2", "goals-v1"}:
        raise ValueError("Unsupported response protocol; rebuild context from original sources")
    value["proof_required"] = protocol != "goals-v1"
    if protocol == "goals-v1":
        value["reasoning_contract"] = "semantic-v1"
        from rag.llm.contracts.obligations import requests_current

        if value.get("as_of") or requests_current(value.get("question", "")):
            value["legal_scope"] = "CURRENT_APPLICABILITY"
        else:
            value.setdefault("legal_scope", "SOURCE_SNAPSHOT")
    value.setdefault("proof_catalogue", {})
    value.setdefault("proof_cache", {})
    value.setdefault("proof_adjustments", [])
    if protocol is not None:
        return value
    sources = [
        {
            **s,
            "id": s.get("id") or "legacy-" + digest([s.get("locator"), s["text"]])[:20],
            "label": s.get("label") or f"S{index + 1}",
        }
        for index, s in enumerate(value["sources"])
    ]
    value["sources"] = bind_evidence(sources, value.get("snapshot"))
    value["user_context"] = bind_user_context(value["question"])
    value["response_protocol"] = "registry-v2"
    task = value["task"]
    from rag.llm.evidence.conditions import sources_with_spans

    payload = {
        "question": value["question"],
        "task": task,
        "user_context": value["user_context"],
        "sources": sources_with_spans(model_sources(value["sources"])),
        "candidate_evidence": [
            model_candidate(c, value["sources"]) for c in value.get("candidate_evidence", [])
        ],
        "allowed_hs_codes": value.get("allowed_hs_codes", []),
        "candidate_comparison": value.get("candidate_comparison", []),
    }
    value["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n" + TASK_INSTRUCTIONS[task]},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    value["normalized_from"] = "legacy-public-context"
    return value
