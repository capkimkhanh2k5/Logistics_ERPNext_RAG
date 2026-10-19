"""Build a bounded, source-verified catalogue at the requested HS levels."""

from rag.llm.disambiguation import comparison_neighbours
from rag.retrieval.request_plan import referenced_codes

MAX_TASK_CANDIDATES = 48


def task_candidates(question: str, result: dict, request: dict, graph) -> list[dict]:
    seeds = result.get("hs_candidates", [])[:10]
    if graph is None:
        return seeds
    levels = {g["level"] for g in request["objectives"] if g["kind"] == "CLASSIFY"}
    explicit = referenced_codes(question)
    direct = [r for r in graph.records.values() if r.get("code") in explicit]
    peers, _ = comparison_neighbours(seeds, graph)
    primary_ids = {r["id"] for r in [*direct, *seeds]}
    pool = [
        *direct,
        *seeds,
        *peers,
        *result.get("matches", [])[:10],
        *result.get("package", [])[:10],
    ]
    if not pool:
        pool = list(result.get("ranked_pool", [])[:10])
    selected: dict[str, dict] = {}
    for row in pool:
        code = row.get("code") or ""
        if len(code) not in (4, 6, 8):
            continue
        candidates = (
            [row] if len(code) in levels and (len(code) != 8 or row["id"] in primary_ids) else []
        )
        for sid in graph.ancestors(row["id"]):
            parent = graph.records.get(sid, {})
            if len(parent.get("code") or "") in levels:
                candidates.append(parent)
        for candidate in candidates:
            level = len(candidate["code"])
            if graph.hs_hierarchy(candidate, target_level=level)["status"] == "VERIFIED":
                selected.setdefault(
                    candidate["id"], {**candidate, "included_as": "VERIFIED_SOURCE_CATALOG"}
                )
        if len(selected) >= MAX_TASK_CANDIDATES:
            break
    return list(selected.values())[:MAX_TASK_CANDIDATES]


def prepare_task_context(
    question: str, result: dict, task: str, config, graph, request: dict
) -> dict:
    from rag.llm.application_rules import assembly_rule_rows
    from rag.llm.context import prepare_context

    candidates = task_candidates(question, result, request, graph)
    provenance = {
        r["code"]: {"source_id": r["id"], "included_as": r.get("included_as", "RETRIEVED")}
        for r in candidates
    }
    internal = {
        **result,
        "query_plan": {**result.get("query_plan", {}), "request": None},
        "hs_candidates": candidates,
        "_candidate_limit": MAX_TASK_CANDIDATES,
        "_task_request": request,
        "_candidate_provenance": provenance,
    }
    # Exact user-referenced headings also serve EXPLAIN/COMPARE/REQUIREMENTS goals.
    if graph is not None:
        codes = referenced_codes(question)
        direct = [
            r for r in graph.records.values() if r.get("code") in codes and graph.citation(r["id"])
        ]
        rules = assembly_rule_rows(question, graph)
        internal["package"] = [*rules, *direct, *result.get("package", [])]
        internal["matches"] = [*rules, *result.get("matches", [])]
    context = prepare_context(question, internal, task, config, graph)
    context["query_plan"] = result.get("query_plan", {})
    context["application_rule_labels"] = [
        s["label"]
        for s in context["sources"]
        if any(s["id"] == rule["id"] for rule in (rules if graph is not None else []))
    ]
    context["detail_evidence"] = []
    if graph is not None and any(g["kind"] == "REQUIREMENTS" for g in request["objectives"]):
        for source in context["sources"]:
            row = graph.records.get(source["id"], {})
            level = len(row.get("code") or "")
            if level not in {6, 8}:
                continue
            hierarchy = graph.hs_hierarchy(row, target_level=level)
            if hierarchy["status"] == "VERIFIED":
                context["detail_evidence"].append(
                    {"source_id": source["id"], "chain": hierarchy["chain"]}
                )
    return context
