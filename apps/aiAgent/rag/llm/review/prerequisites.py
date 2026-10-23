"""Review divergent verified ancestors with their wording and note-scope obligations."""

from copy import deepcopy


def ancestor(candidate: dict, level: int) -> str:
    hierarchy = candidate.get("hierarchy", {})
    if hierarchy.get("status") != "VERIFIED":
        return ""
    return next((n["code"] for n in hierarchy["chain"] if n["level"] == level), "")


def parent_review(row: dict, context: dict) -> tuple[dict, dict] | None:
    if (
        row["kind"] != "CLASSIFY"
        or not row.get("valid")
        or row["status"] not in {"RECOMMENDATION", "MISSING_PRODUCT_INFO"}
    ):
        return None
    candidates = {
        c["code"]: c
        for c in [*context.get("candidate_evidence", []), *context.get("comparison_candidates", [])]
    }
    children = [c for c in candidates.values() if len(c["code"]) == row["level"]]
    original = row.get("suggested_hs_code") or next(iter(row.get("candidate_codes", [])), "")
    selected = candidates.get(original)
    if (
        not selected
        or not children
        or any(c["hierarchy"]["status"] != "VERIFIED" for c in children)
    ):
        return None
    levels = sorted(
        {n["level"] for c in children for n in c["hierarchy"]["chain"] if n["level"] < row["level"]}
    )
    level = next(
        (
            level
            for level in levels
            if len({ancestor(c, level) for c in children}) > 1
            and all(ancestor(c, level) for c in children)
        ),
        None,
    )
    if level is None:
        return None
    sources = {s["label"]: s for s in context["sources"]}
    parents: dict[str, dict] = {}
    for child in children:
        code = ancestor(child, level)
        chain = [n for n in child["hierarchy"]["chain"] if n["level"] <= level]
        if not chain or not all(n.get("evidence_labels") for n in chain):
            return None
        labels = list(dict.fromkeys(label for n in chain for label in n["evidence_labels"]))
        existing = candidates.get(code)
        notes = (
            set(child.get("defining_note_labels", []))
            | set(child.get("related_note_labels", []))
            | set(child.get("context_labels", []))
        )
        if code in parents:
            notes.update(parents[code]["related_note_labels"])
        if existing:
            parent = deepcopy(existing)
        else:
            parent = {
                **child,
                "code": code,
                "wording_label": chain[-1]["evidence_labels"][0],
                "ancestor_labels": labels[: -len(chain[-1]["evidence_labels"])],
                "context_labels": [],
                "required_citation_labels": labels,
                "defining_note_labels": [],
                "related_note_labels": [],
                "hierarchy": {**child["hierarchy"], "chain": chain},
            }
        parent["related_note_labels"] = sorted(set(parent.get("related_note_labels", [])) | notes)
        parent["note_scope_required"] = True
        if any(
            label not in sources
            for label in [*parent["required_citation_labels"], *parent["related_note_labels"]]
        ):
            return None
        parents[code] = parent
    scoped = deepcopy(context)
    for metadata in ("proof_catalogue", "proof_cache", "proof_adjustments"):
        if metadata in context:
            scoped[metadata] = context[metadata]
    scoped.update(
        candidate_evidence=list(parents.values()),
        comparison_candidates=[],
        candidate_comparison=[],
        classification_level=level,
        allowed_hs_codes=list(parents),
    )
    for goal in scoped["request"]["objectives"]:
        if goal["id"] == row["objective_id"]:
            goal["level"] = level
    proposed = {
        **row,
        "result_id": f"{row['result_id']}.P{level}",
        "level": level,
        "status": "RECOMMENDATION",
        "suggested_hs_code": ancestor(selected, level),
        "candidate_only": True,
        "shortlist_codes": list(parents),
        "candidate_codes": [],
        "hs_candidates": [],
        "claims": [],
        "draft_clarifications": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": [],
    }
    return proposed, scoped


def leaf_review(row: dict, context: dict, parent: dict) -> tuple[dict, dict]:
    code, level = parent["suggested_hs_code"], parent["level"]
    candidates = {
        c["code"]: c
        for c in [*context.get("candidate_evidence", []), *context.get("comparison_candidates", [])]
        if len(c["code"]) == row["level"] and ancestor(c, level) == code
    }
    codes = set(candidates)
    groups = []
    for group in context.get("candidate_comparison", []):
        if not group["parent_code"] or not codes.intersection(group["codes"]):
            continue
        groups.append(group)  # Retain missing_codes and every obligation in the selected subtree.
    scoped = {
        **context,
        "candidate_evidence": list(candidates.values()),
        "comparison_candidates": [],
        "candidate_comparison": groups,
    }
    original = row.get("suggested_hs_code", "")
    shortlist = [c for c in row.get("candidate_codes", []) if c in candidates]
    if candidates and original not in candidates:
        original = shortlist[0] if shortlist else next(iter(candidates), "")
        if not shortlist and original:
            shortlist = [original]
    same = original == row.get("suggested_hs_code")
    return {
        **row,
        "status": "RECOMMENDATION",
        "suggested_hs_code": original,
        "candidate_codes": shortlist,
        "prerequisite_review": parent,
        "prerequisite_reviews": [*row.get("prerequisite_reviews", []), parent],
        "claims": row.get("claims", []) if same else [],
        "citations": row.get("citations", []) if same else [],
        "draft_clarifications": [],
    }, scoped


def defer_leaf(row: dict, parent: dict) -> dict:
    fields = (
        "status",
        "answer",
        "citations",
        "missing_information",
        "missing_legal_evidence",
        "failure_kind",
        "review_clarifications",
        "condition_bindings",
    )
    return {
        **row,
        **{key: parent[key] for key in fields if key in parent},
        "suggested_hs_code": "",
        "candidate_codes": [],
        "hs_candidates": [],
        "claims": [],
        "review_valid": False,
        "clarifications_inherited": parent["status"] == "MISSING_PRODUCT_INFO",
        "prerequisite_review": parent,
        "prerequisite_reviews": [*row.get("prerequisite_reviews", []), parent],
    }
