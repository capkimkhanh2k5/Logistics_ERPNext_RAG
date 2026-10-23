"""Replay the public v1 answer/review contract for pre-registry regression fixtures.

Fresh runtime contexts always use registry-v2. These fixtures exercise backward
compatibility for saved contexts; registry-v2 has its own end-to-end regressions.
"""

import json

from rag.llm.context.builder import _model_candidate_evidence, _model_source, prepare_context


def prepare_legacy_context(*args, **kwargs):
    context = prepare_context(*args, **kwargs)
    context.pop("response_protocol")
    payload = json.loads(context["messages"][1]["content"])
    payload["sources"] = [_model_source(source) for source in context["sources"]]
    payload["candidate_evidence"] = _model_candidate_evidence(context["candidate_evidence"])
    context["messages"][1]["content"] = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    )
    return context
