"""One bounded corrective retrieval round over the existing immutable source graph."""

import re
from collections import deque
from itertools import zip_longest
from time import perf_counter

from rag.llm.validation.answer import _folded
from rag.retrieval.request_plan import explicit_level, referenced_codes

MAX_RECOVERY_SOURCES = 96
MAX_RECOVERY_GAPS = 3


def requirements_bundle(graph, headings: set[str], level: int) -> tuple[list[dict], list[dict]]:
    """Fairly pack bounded branch inventories; navigation nodes do not require invented wording."""
    inventories: list[list[dict]] = []
    scopes: list[dict] = []
    for heading in sorted(headings):
        root_ids = sorted(
            sid
            for sid in graph.nodes.keys() | graph.records.keys()
            if graph.node_code(sid) == heading
        )
        covered_navigation: set[str] = set()
        if level == 8:
            for leaf in graph.records.values():
                if len(leaf.get("code") or "") != 8 or not leaf["code"].startswith(heading):
                    continue
                path = graph.hs_hierarchy(leaf, target_level=8)
                if path["status"] == "VERIFIED" and any(n["id"] in root_ids for n in path["chain"]):
                    covered_navigation.update(
                        n["id"]
                        for n in path["chain"]
                        if not n["legal_evidence_ids"] and n["level"] == 6
                    )
        frontier = deque((sid, 0) for sid in root_ids)
        seen, needed, unavailable = set(), set(), []
        rows: dict[str, dict] = {}
        truncated, reached_target = False, False
        while frontier:
            sid, depth = frontier.popleft()
            if sid in seen:
                continue
            seen.add(sid)
            code = graph.node_code(sid) or ""
            if len(code) in {4, 6, 8} and len(code) > level:
                continue
            reached_target = reached_target or len(code) == level
            if len(code) in {4, 6, 8} and sid not in covered_navigation:
                proof = graph.hs_hierarchy({"id": sid, "code": code}, target_level=len(code))
                if proof["status"] != "VERIFIED":
                    unavailable.append(code)
            view = graph.source_view({"id": sid})
            for nid in [sid, *view["context_ids"], *view["note_ids"]]:
                evidence = graph.legal_evidence(nid)
                if (
                    nid == sid
                    and len(code) in {4, 6, 8}
                    and not evidence
                    and nid not in covered_navigation
                ):
                    hierarchy = graph.hs_hierarchy(
                        {"id": sid, "code": code}, target_level=len(code)
                    )
                    if hierarchy["legal_evidence_status"] != "VERIFIED":
                        unavailable.append(code)
                for citation in evidence:
                    source = graph.source_record(citation["id"])
                    if not source:
                        continue
                    needed.add(source["id"])
                    if len(rows) < MAX_RECOVERY_SOURCES:
                        rows.setdefault(source["id"], source)
            if depth < 12 and len(code) < level:
                frontier.extend(
                    (child, depth + 1) for child in sorted(graph.children.get(sid, set()))
                )
            elif depth >= 12 and graph.children.get(sid):
                truncated = True
        inventories.append(list(rows.values()))
        scopes.append(
            {
                "heading": heading,
                "level": level,
                "source_ids": sorted(needed),
                "complete": reached_target and not unavailable and not truncated,
                "missing_codes": sorted(set(unavailable)),
                "truncated": truncated,
            }
        )
    packed: dict[str, dict] = {}
    for group in zip_longest(*inventories):
        for row in group:
            if row is not None and len(packed) < MAX_RECOVERY_SOURCES:
                packed.setdefault(row["id"], row)
    for scope in scopes:
        if not set(scope["source_ids"]) <= packed.keys():
            scope.update(complete=False, truncated=True)
    return list(packed.values()), scopes


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
        row = (
            graph.source_record(row.get("id"))
            if hasattr(graph, "source_record")
            else graph.records.get(row.get("id"))
        ) or {}
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
    anchors = [r for r in graph.records.values() if r.get("code") in codes]
    neighbours: dict[str, dict] = {}
    if not application_gap:
        for anchor in anchors:
            level = len(anchor.get("code") or "")
            if level not in {6, 8}:
                continue
            path = graph.hs_hierarchy(anchor, target_level=level)
            if path["structure_status"] != "VERIFIED":
                continue
            parent = next((n for n in reversed(path["chain"]) if n["level"] < level), None)
            if parent:
                for peer in graph.records.values():
                    if len(peer.get("code") or "") == level and parent["id"] in graph.ancestors(
                        peer["id"]
                    ):
                        neighbours.setdefault(peer["id"], peer)
    frontier = deque((r["id"], 0) for r in [*anchors, *neighbours.values()])
    seen = set()
    while frontier and len(recovered) < MAX_RECOVERY_SOURCES:
        sid, depth = frontier.popleft()
        if sid in seen:
            continue
        seen.add(sid)
        row = graph.records.get(sid)
        if row:
            view = graph.source_view(row)
            # Navigation-only nodes can still carry legal branch context. Recover
            # prerequisites before leaves so the bounded pack retains their scope.
            for related in [*view["ancestor_ids"], *view["context_ids"], *view["note_ids"]]:
                for citation in graph.legal_evidence(related):
                    add(citation)
            for citation in graph.legal_evidence(sid):
                add(citation)
        if depth < (0 if application_gap else 3):
            frontier.extend((child, depth + 1) for child in sorted(graph.children.get(sid, set())))

    extra = None
    queries = [g["query"] for g in gaps if g.get("query")]
    closure = []
    for goal in context.get("request", {}).get("objectives", []):
        target = max(goal["level"], explicit_level(goal["anchor"]) or 0)
        if goal["kind"] == "REQUIREMENTS" and target > 4:
            _, scopes = requirements_bundle(graph, {c[:4] for c in codes}, target)
            closure.extend(scopes)
    present = prior_ids | recovered.keys()
    wording_closed = bool(closure) and all(
        s["complete"] and set(s["source_ids"]) <= present for s in closure
    )
    metadata["wording_scope_closed"] = wording_closed
    if (
        (not recovered or application_gap or not wording_closed)
        and queries
        and hasattr(retriever, "unified_search")
    ):
        query = question + "\nKhoảng trống nguồn cần tìm (giả thuyết): " + "; ".join(queries)
        try:
            extra = retriever.unified_search(query, intent_hint="auto")
        except (ValueError, RuntimeError) as exc:
            metadata["search_error"] = type(exc).__name__
        if extra and extra.get("snapshot") != context.get("snapshot"):
            return None, {**metadata, "reason": "SNAPSHOT_MISMATCH"}
        graph_rows = list(recovered.values())
        recovered.clear()
        # Corrective search must retain space even when a broad graph branch filled the cap.
        # Every replacement still passes the same source/citation checks in add().
        for row in (extra or {}).get("package", []):
            add(row)
        for row in (extra or {}).get("hs_candidates", []):
            add(row)
        metadata["search_priority"] = bool(recovered)
        for row in graph_rows:
            add(row)
        metadata["graph_sources_displaced"] = sorted(
            {row["id"] for row in graph_rows} - recovered.keys()
        )
        metadata["application_search"] = application_gap
    metadata["wording_scope_closed"] = bool(closure) and all(
        scope["complete"] and set(scope["source_ids"]) <= prior_ids | recovered.keys()
        for scope in closure
    )
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
