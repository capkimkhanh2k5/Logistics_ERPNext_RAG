"""Stable source bindings, not an inferred catalogue of product attributes."""

from copy import deepcopy
from hashlib import sha256


def condition_span_registry(sources: list[dict]) -> dict[str, dict]:
    """Register full wording and unique paragraphs without parsing legal logic."""
    registry = {}
    for source in sources:
        text = source["text"]
        spans = [(0, len(text))]
        position = 0
        for line in text.splitlines(keepends=True):
            stripped = line.strip()
            start = position + len(line) - len(line.lstrip())
            if stripped and text.count(stripped) == 1:
                spans.append((start, start + len(stripped)))
            position += len(line)
        for start, end in list(dict.fromkeys(spans))[:33]:
            if start == end:
                continue
            eid = source["evidence_id"]
            cid = "P" + sha256(f"{eid}:{start}:{end}".encode()).hexdigest()[:20]
            registry[cid] = {
                "condition_id": cid,
                "evidence_id": eid,
                "start": start,
                "end": end,
                "quote": text[start:end],
            }
    return registry


def sources_with_spans(sources: list[dict]) -> list[dict]:
    registry = condition_span_registry(sources)
    return [
        {
            **source,
            "condition_spans": [
                {key: span[key] for key in ("condition_id", "start", "end")}
                for span in registry.values()
                if span["evidence_id"] == source["evidence_id"]
            ],
        }
        for source in sources
    ]


def condition_id_schema(schema: dict) -> dict:
    """Use the same source-span selection contract in draft and review."""
    wire = deepcopy(schema)

    def span_wire(node):
        if isinstance(node, list):
            for child in node:
                span_wire(child)
        elif isinstance(node, dict):
            props = node.get("properties", {})
            if "criterion_quote" in props:
                for key in ("criterion_quote", "criterion_quotes", "condition_ids"):
                    props.pop(key, None)
                required = [
                    k
                    for k in node.get("required", [])
                    if k not in {"criterion_quote", "criterion_quotes", "condition_ids"}
                ]
                ref = {"type": "string", "pattern": "^P[a-f0-9]{20}$"}
                key = "condition_id" if "evidence_id" in props else "condition_ids"
                props[key] = (
                    ref
                    if key == "condition_id"
                    else {
                        "type": "array",
                        "uniqueItems": True,
                        "items": ref,
                    }
                )
                node["required"] = [*required, key]
            for child in node.values():
                span_wire(child)

    span_wire(wire)
    return wire


def bind_registered_conditions(value, registry: dict) -> tuple[dict, list[str]]:
    """Resolve current-wire span IDs; invalid IDs never fall back to a generated quote."""
    errors = []

    def bind(node):
        if isinstance(node, list):
            return [bind(child) for child in node]
        if not isinstance(node, dict):
            return node
        if {"nodes", "root", "decomposition_review"} <= node.keys():
            return deepcopy(node)  # The generic proof validator owns these spans.
        result = {key: bind(child) for key, child in node.items()}
        ids = (
            [result["condition_id"]]
            if "condition_id" in result
            else result.get("condition_ids", [])
        )
        if "condition_ids" in result and ids == [] and result.get("evidence_ids"):
            errors.append("[CONDITION_REF_MISSING] Câu hỏi/check có nguồn phải chọn span nguồn.")
            return result
        # D-prefixed bindings belong to the saved source-only compatibility protocol.
        if (
            not ids
            or not isinstance(ids, list)
            or all(isinstance(cid, str) and cid.startswith("D") for cid in ids)
        ):
            return result
        refs = result.get("evidence_ids", [result.get("evidence_id")])
        if any(
            not isinstance(cid, str)
            or cid not in registry
            or registry[cid]["evidence_id"] not in refs
            for cid in ids
        ):
            errors.append("[CONDITION_REF_INVALID] Span không thuộc registry/nguồn được cấp.")
            return result
        spans = [registry[cid] for cid in ids]
        if result.get("criterion_quote") not in (None, spans[0]["quote"]):
            errors.append("[CONDITION_REF_INVALID] Quote không khớp span đã chọn.")
            return result
        quotes = [{"evidence_id": span["evidence_id"], "quote": span["quote"]} for span in spans]
        if "criterion_quotes" in result and result["criterion_quotes"] != quotes:
            errors.append("[CONDITION_REF_INVALID] Các quote không khớp span đã chọn.")
            return result
        result["criterion_quote"] = spans[0]["quote"]
        if len(spans) > 1:
            result["criterion_quotes"] = quotes
        result.pop("condition_id", None)
        return result

    return bind(value), errors


def predicate_bindings(row: dict, context: dict) -> list[dict]:
    """Bind one quoted predicate to unique literal spans; infer no legal meaning."""
    refs = row.get("evidence_ids", [row.get("evidence_id")])
    pairs = {(eid, row.get("criterion_quote", "")) for eid in refs}
    pairs.update(
        (entry["evidence_id"], entry["quote"]) for entry in row.get("criterion_quotes", [])
    )
    bindings = []
    sources = {s["evidence_id"]: s for s in context["sources"]}
    for eid, quote in sorted(pairs):
        source = sources.get(eid)
        if not quote.strip() or not source or eid not in refs or source["text"].count(quote) != 1:
            continue
        start = source["text"].index(quote)
        end = start + len(quote)
        key = f"{source['evidence_id']}:{start}:{end}".encode()
        bindings.append(
            {
                "condition_id": "P" + sha256(key).hexdigest()[:20],
                "evidence_id": source["evidence_id"],
                "start": start,
                "end": end,
                "quote": quote,
            }
        )
    return bindings


def predicate_errors(row: dict, context: dict) -> list[str]:
    primary = {k: v for k, v in row.items() if k != "criterion_quotes"}
    invalid = bool(
        row.get("criterion_quote", "").strip() and not predicate_bindings(primary, context)
    )
    for entry in row.get("criterion_quotes", []):
        invalid |= entry["evidence_id"] not in row.get(
            "evidence_ids", []
        ) or not predicate_bindings(
            {"evidence_ids": [entry["evidence_id"]], "criterion_quote": entry["quote"]}, context
        )
    if invalid:
        return [
            "[CONDITION_SPAN_INVALID] Mệnh đề cần một vị trí nguyên văn duy nhất trong nguồn đã dẫn."
        ]
    return []


def same_condition(question: dict, branch: dict, context: dict) -> bool:
    """Prefer exact predicate identity over model-chosen attribute names."""
    if (question.get("criterion_quote") or question.get("criterion_quotes")) and (
        branch.get("criterion_quote") or branch.get("criterion_quotes")
    ):
        left = {p["condition_id"] for p in predicate_bindings(question, context)}
        right = {p["condition_id"] for p in predicate_bindings(branch, context)}
        return bool(left & right)
    from rag.llm.validation.answer import _folded

    return _folded(question["attribute"]) == _folded(branch["attribute"]) or (
        len(branch["attribute"].strip()) >= 8
        and _folded(branch["attribute"]) in _folded(question["question"])
        and set(question["evidence_ids"]) == set(branch["evidence_ids"])
    )


def review_conditions(context: dict, groups: list[dict], code: str) -> list[dict]:
    sources = {s["label"]: s for s in context["sources"]}
    branch_ids = {
        eid
        for group in groups
        for option in group["branch_options"]
        for eid in option["evidence_ids"]
    }
    candidates = [*context["candidate_evidence"], *context.get("comparison_candidates", [])]
    required: dict[str, set[str]] = {}
    for candidate in candidates:
        for label in [
            *candidate.get("required_citation_labels", []),
            *candidate.get("related_note_labels", []),
        ]:
            if label in sources:
                required.setdefault(sources[label]["evidence_id"], set()).add(candidate["code"])
    parent = code[:6] if len(code) == 8 else code
    registry = []
    for source in context["sources"]:
        eid = source["evidence_id"]
        if eid not in required and eid not in branch_ids:
            continue
        # A source unit may contain several predicates. IDs bind its provenance only;
        # the reviewer must still separate predicates and respect their logical scope.
        key = f"{parent}:{source['id']}".encode()
        registry.append(
            {
                "condition_id": "D" + sha256(key).hexdigest()[:16],
                "parent_code": parent,
                "evidence_ids": [eid],
                "role": "PREREQUISITE"
                if len(source.get("code") or "") in (4, 6) and code.startswith(source["code"])
                else "BRANCH"
                if eid in branch_ids
                else "REQUIRED",
                "codes": sorted(required.get(eid, set())),
            }
        )
    return registry


def bind_condition_refs(value: dict, context: dict) -> dict:
    """Upgrade older source-only responses without guessing an attribute or a fact."""
    registry = context.get("review_conditions", [])
    bound = deepcopy(value)
    for key in ("branch_checks", "clarifications"):
        for row in bound.get(key, []):
            if "condition_ids" not in row:
                row["condition_ids"] = (
                    [p["condition_id"] for p in predicate_bindings(row, context)]
                    if row.get("criterion_quote")
                    else [
                        c["condition_id"]
                        for c in registry
                        if set(c["evidence_ids"]) <= set(row["evidence_ids"])
                        and (key != "branch_checks" or c["parent_code"] == row["parent_code"])
                    ]
                )
    return bound


def condition_ref_errors(row: dict, context: dict, *, parent: str | None = None) -> list[str]:
    if row.get("criterion_quote"):
        errors = predicate_errors(row, context)
        expected = {p["condition_id"] for p in predicate_bindings(row, context)}
        if set(row.get("condition_ids", [])) != expected:
            errors.append(
                "[CONDITION_REF_INVALID] condition_ids không khớp span của mệnh đề nguồn."
            )
        registry = context.get("review_conditions", [])
        allowed = {
            eid
            for c in registry
            if parent is None or c["parent_code"] == parent
            for eid in c["evidence_ids"]
        }
        if registry and any(
            p["evidence_id"] not in allowed for p in predicate_bindings(row, context)
        ):
            errors.append(
                "[CONDITION_SOURCE_MISMATCH] Mệnh đề nằm ngoài phạm vi điều kiện của job."
            )
        return errors
    registry = {c["condition_id"]: c for c in context.get("review_conditions", [])}
    if not registry and not row.get("condition_ids"):
        return []
    refs = row.get("condition_ids", [])
    if not refs or any(cid not in registry for cid in refs):
        return ["[CONDITION_REF_INVALID] condition_ids không thuộc registry điều kiện của job."]
    if any(
        not set(registry[cid]["evidence_ids"]) <= set(row["evidence_ids"])
        or (parent is not None and registry[cid]["parent_code"] != parent)
        for cid in refs
    ):
        return [
            "[CONDITION_SOURCE_MISMATCH] condition_ids và evidence_ids/phạm vi nhánh không khớp."
        ]
    return []


def defer_descendant_comparison(value: dict, context: dict, code: str) -> tuple[dict, list[str]]:
    """Keep comparison undecided while an explicitly questioned ancestor is unknown.

    This never upgrades a proof or releases a code. Descendant exclusions are discarded,
    not accepted, until the prerequisite has been supplied and independently checked.
    """
    level = context.get("classification_level")
    if value["status"] != "MISSING_PRODUCT_INFO" or level not in {6, 8}:
        return value, []
    if any(group["missing_codes"] for group in context.get("candidate_comparison", [])):
        return value, []
    candidate = next((c for c in context["candidate_evidence"] if c["code"] == code), None)
    if not candidate:
        return value, []
    sources = {s["label"]: s for s in context["sources"]}
    parent_levels = {
        sources[label]["evidence_id"]: node["level"]
        for node in candidate["hierarchy"]["chain"]
        if node["level"] < level
        for label in node.get("evidence_labels", [])
        if label in sources
    }
    pending = {
        c["evidence_id"]
        for c in value["condition_checks"]
        if c["assessment"] == "MISSING_PRODUCT_INFO"
        and not c["fact_ids"]
        and not c["user_quotes"]
        and c["evidence_id"] in parent_levels
    }
    questions = [q for q in value["clarifications"] if pending & set(q["evidence_ids"])]
    if not questions:
        return value, []
    # Only questions about the earliest pending ancestor survive. Other questions
    # and peer exclusions have not been accepted as proven by this gate.
    earliest = min(
        parent_levels[eid] for q in questions for eid in set(q["evidence_ids"]) & pending
    )
    earlier = {eid for eid, parent_level in parent_levels.items() if parent_level < earliest}
    satisfied = {
        c["evidence_id"]
        for c in value["condition_checks"]
        if c["assessment"] == "SATISFIED" and c["fact_ids"] and c["user_quotes"]
    }
    if not earlier <= satisfied:
        return value, []
    questions = [
        q
        for q in questions
        if any(parent_levels[eid] == earliest for eid in set(q["evidence_ids"]) & pending)
    ]
    deferred = deepcopy(value)
    deferred["clarifications"] = questions
    # Stop at the unresolved ancestor; descendant assertions have not been reviewed.
    active_ids = {eid for eid, parent_level in parent_levels.items() if parent_level <= earliest}
    deferred["condition_checks"] = [
        check for check in value["condition_checks"] if check["evidence_id"] in active_ids
    ]
    groups = context.get("candidate_comparison", [])
    deferred["candidate_assessments"] = [
        {
            "code": peer,
            "assessment": "POSSIBLE",
            "evidence_ids": [],
            "fact_ids": [],
            "user_quotes": [],
        }
        for peer in sorted({peer for group in groups for peer in group["codes"]})
    ]
    deferred["branch_checks"] = [
        {
            "parent_code": group["parent_code"],
            "attribute": "dependent_conditions",
            "assessment": "DEFERRED",
            "evidence_ids": sorted(
                {eid for option in group["branch_options"] for eid in option["evidence_ids"]}
            ),
            "fact_ids": [],
            "user_quotes": [],
        }
        for group in groups
        if group["branch_options"]
    ]
    return deferred, sorted({eid for q in questions for eid in set(q["evidence_ids"]) & pending})
