"""One bounded corrective retrieval round over the existing immutable source graph."""

import re
from collections import deque
from time import perf_counter

from rag.llm.validation import _folded
from rag.retrieval.request_plan import referenced_codes

MAX_RECOVERY_SOURCES = 96
MAX_RECOVERY_GAPS = 3


def recover_evidence(
    question: str, result: dict, context: dict, gaps: list[dict], retriever, graph
) -> tuple[dict | None, dict]:
    tick = perf_counter()
    prior_ids = {s["id"] for s in context["sources"]}
    allowed = referenced_codes(question) | {s.get("code") for s in context["sources"]}
    gaps = [
        g
        for g in gaps
        if isinstance(g.get("anchor"), str)
        and g["anchor"] in question
        and set(g.get("codes", [])) <= allowed
    ][:MAX_RECOVERY_GAPS]
    metadata: dict = {"rounds": 1, "new_source_ids": [], "llm_planner_calls": 0}
    if not gaps or graph is None:
        return None, {**metadata, "reason": "NO_GROUNDED_GAP"}
    if result.get("snapshot") != context.get("snapshot"):
        return None, {**metadata, "reason": "SNAPSHOT_MISMATCH"}
    codes = {code for gap in gaps for code in gap["codes"]}
    application_gap = any(
        gap.get("kind") == "APPLICATION"
        or re.search(
            r"co che|tieu chi phan dinh|cach ap dung",
            _folded(gap.get("query", "") + " " + gap.get("reason", "")),
        )
        for gap in gaps
    )
    recovered: dict[str, dict] = {}

    def add(row):
        row = graph.records.get(row.get("id"), {})
        if (
            row.get("id") not in prior_ids
            and row.get("source_text")
            and graph.citation(row["id"])
            and len(recovered) < MAX_RECOVERY_SOURCES
        ):
            recovered.setdefault(row["id"], {**row, "included_as": "EVIDENCE_RECOVERY"})

    for row in [
        *result.get("ranked_pool", []),
        *result.get("candidate_pool", []),
        *result.get("package", []),
    ]:
        if row.get("code") in codes:
            add(row)
    frontier = deque((r["id"], 0) for r in graph.records.values() if r.get("code") in codes)
    seen = set()
    while frontier and len(recovered) < MAX_RECOVERY_SOURCES:
        sid, depth = frontier.popleft()
        if sid in seen:
            continue
        seen.add(sid)
        row = graph.records.get(sid)
        if row and graph.citation(sid):
            add(row)
            view = graph.source_view(row)
            for related in [*view["ancestor_ids"], *view["context_ids"], *view["note_ids"]]:
                for citation in graph.legal_evidence(related):
                    target = graph.records.get(citation["id"])
                    if target:
                        add(target)
        if depth < (0 if application_gap else 3):
            frontier.extend((child, depth + 1) for child in sorted(graph.children.get(sid, set())))

    extra = None
    queries = [g["query"] for g in gaps if g.get("query")]
    if (not recovered or application_gap) and queries and hasattr(retriever, "unified_search"):
        query = question + "\nKhoảng trống nguồn cần tìm (giả thuyết): " + "; ".join(queries)
        try:
            extra = retriever.unified_search(query, intent_hint="auto")
        except (ValueError, RuntimeError) as exc:
            metadata["search_error"] = type(exc).__name__
        if extra and extra.get("snapshot") != context.get("snapshot"):
            return None, {**metadata, "reason": "SNAPSHOT_MISMATCH"}
        for row in (extra or {}).get("package", []):
            add(row)
        for row in (extra or {}).get("hs_candidates", []):
            add(row)
        metadata["application_search"] = application_gap
    metadata.update(new_source_ids=list(recovered), elapsed_ms=(perf_counter() - tick) * 1000)
    if not recovered:
        return None, {**metadata, "reason": "NO_NEW_SOURCES"}
    rows = list(recovered.values())
    return {
        **result,
        "matches": [*rows, *result.get("matches", [])],
        "package": [*rows, *result.get("package", [])],
        "hs_candidates": [
            *[r for r in rows if len(r.get("code") or "") == 8],
            *result.get("hs_candidates", []),
        ],
        "ranked_pool": [*(extra or {}).get("ranked_pool", []), *result.get("ranked_pool", [])],
    }, metadata
