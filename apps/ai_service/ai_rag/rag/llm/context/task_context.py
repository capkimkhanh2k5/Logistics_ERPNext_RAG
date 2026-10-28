"""Build a bounded, source-verified catalogue at the requested HS levels."""

from rag.llm.review.disambiguation import comparison_neighbours
from rag.retrieval.request_plan import explicit_level, referenced_codes

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
    from rag.llm.context.builder import prepare_context
    from rag.llm.validation.application_rules import assembly_rule_rows

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
        from rag.retrieval.evidence_recovery import requirements_bundle

        scopes: list[dict] = []
        requirement_rows: dict[str, dict] = {}
        for goal in request["objectives"]:
            target = max(goal["level"], explicit_level(goal["anchor"]) or 0)
            if goal["kind"] != "REQUIREMENTS" or target <= 4:
                continue
            headings = {c[:4] for c in codes}
            if not headings:
                headings = {r["code"][:4] for r in candidates}
            bundle, covered = requirements_bundle(graph, headings, target)
            for row in bundle:
                requirement_rows[row["id"]] = row
            scopes.extend({**scope, "objective_id": goal["id"]} for scope in covered)
        internal["package"] = [*requirement_rows.values(), *internal["package"]]
        internal["_requirements_scopes"] = scopes
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
