"""Pack user facts, cited source text and verified HS evidence for the LLM."""

import json
import re

from rag.graph.context import GraphContext
from rag.ingestion.sources import SOURCE_TYPES
from rag.llm.evidence.evidence import (
    bind_evidence,
    bind_user_context,
    model_candidate,
    model_sources,
)
from rag.llm.providers.budget import ContextBudgetError, request_budget
from rag.llm.review.disambiguation import comparison_neighbours, comparison_payload
from rag.llm.validation.answer import _folded
from rag.prompts.core.system import SYSTEM_PROMPT
from rag.prompts.generation.tasks import (
    GOAL_TASK_INSTRUCTION,
    TASK_INSTRUCTIONS,
    USER_SUPPLEMENT_TEMPLATE,
)
from rag.prompts.schemas.answer import MODEL_ANSWER_SCHEMA, bind_registry_schema
from rag.utils.files import digest


def compose_query(question: str, supplements: list[str], max_chars: int | None) -> str:
    """Combine user facts for a fresh retrieval, without carrying assistant claims."""
    if not question.strip():
        raise ValueError("Question must not be empty")
    if any(not text.strip() for text in supplements):
        raise ValueError("Additional context must not be empty")
    sections = [question.strip()]
    sections.extend(
        USER_SUPPLEMENT_TEMPLATE.format(turn=i + 2, text=text.strip())
        for i, text in enumerate(supplements)
    )
    combined = "\n\n".join(sections)
    if max_chars is not None and len(combined) > max_chars:
        raise ValueError("Combined question exceeds GROQ_MAX_INPUT_CHARS")
    return combined


def load_generation_graph(retriever) -> GraphContext:
    records = retriever.documents("knowledge", chunk_types=SOURCE_TYPES)
    nodes = retriever.conn.execute(
        "SELECT * FROM rag.graph_nodes WHERE snapshot=%s", (retriever.snapshot,)
    ).fetchall()
    edges = retriever.conn.execute(
        "SELECT * FROM rag.graph_edges WHERE snapshot=%s ORDER BY id", (retriever.snapshot,)
    ).fetchall()
    return GraphContext(records, nodes, edges)


def source_rows(
    result: dict,
    task: str,
    graph=None,
    candidate_limit: int = 10,
    *,
    comparison_candidates: list[dict] | None = None,
) -> tuple[list, list]:
    candidates = result.get("hs_candidates", [])[:candidate_limit] if task in {"hs", "auto"} else []
    advice = result.get("semantic_intent", {})
    # Advisory intent affects packing priority, never filters the common retrieval results.
    rows = (
        list(result.get("matches", []))
        if task == "auto" and advice.get("intent") != "product"
        else []
    )
    notes: list[dict] = []
    for row in comparison_candidates if comparison_candidates is not None else candidates:
        rows.append(row)
        if graph is not None:
            view = graph.source_view(row)
            for nid in [*view["ancestor_ids"], *view["context_ids"], *view["note_ids"]]:
                evidence = (
                    graph.legal_evidence(nid)
                    if hasattr(graph, "legal_evidence")
                    else [graph.citation(nid)]
                )
                for citation in evidence:
                    if not citation:
                        continue
                    sid = citation.get("id", nid)
                    target = notes if nid in view["note_ids"] else rows
                    materialized = (
                        graph.source_record(sid)
                        if hasattr(graph, "source_record")
                        else {
                            **graph.records.get(sid, {}),
                            "id": sid,
                            "source_text": citation["text"],
                            "locator": citation["locator"],
                        }
                    )
                    if materialized:
                        target.append(materialized)
    rows.extend([*result.get("matches", []), *result.get("package", []), *notes])
    unique = {}
    for row in rows:
        if graph is not None and graph.citation(row["id"]) is None:
            continue
        if row.get("source_text") and row["id"] not in unique:
            unique[row["id"]] = row
    return list(unique.values()), candidates


def _phrase(text: str) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", _folded(text or "")).split())


def _defining_notes(view: dict, wording_ids: list[str], graph) -> list[str]:
    """Linked notes whose text defines or restricts the short title of the candidate or an ancestor.

    Such a note defines the very term the candidate is named by, so its conditions cannot
    be satisfied by matching the title alone.
    """
    if graph is None:
        return []
    titles = []
    for sid in wording_ids:
        citation = graph.citation(sid)
        if not citation:
            continue
        raw_text = citation.get("text", "").strip()
        raw_clean = re.sub(r"^[-\s]+", "", raw_text).rstrip(":.;, ").strip()
        phrase = _phrase(raw_clean)
        words = phrase.split()
        if 2 <= len(words) <= 8 and phrase != "loai khac":
            titles.append((phrase, raw_clean))
    if not titles:
        return []
    found = []
    for nid in view.get("note_ids", []):
        citation = graph.citation(nid)
        if not citation:
            continue
        raw_note = citation.get("text", "")
        body = f" {_phrase(raw_note)} "
        for phrase, raw_clean in titles:
            if (
                f'"{raw_clean}"' in raw_note
                or f"“{raw_clean}”" in raw_note
                or f"thuat ngu {phrase}" in body
                or f"{phrase} co nghia la" in body
                or f"{phrase} duoc hieu la" in body
            ):
                found.append(nid)
                break
    return found


def _candidate_evidence(candidates: list[dict], sources: list[dict], graph) -> list[dict]:
    labels = {s["id"]: s["label"] for s in sources}
    evidence = []
    for row in candidates:
        if row["id"] not in labels:
            continue
        view = graph.source_view(row) if graph is not None else {}
        hierarchy: dict = (
            (
                graph.hs_hierarchy(row, target_level=len(row["code"]))
                if len(row.get("code") or "") in (4, 6)
                else graph.hs_hierarchy(row)
            )
            if graph is not None and hasattr(graph, "hs_hierarchy")
            else {"status": "INVALID", "chain": [], "errors": ["HS source graph is unavailable"]}
        )
        chain = []
        for node in hierarchy["chain"]:
            source_ids = node.get(
                "legal_evidence_ids", [node["id"]] if node["has_legal_wording"] else []
            )
            evidence_labels = [labels[sid] for sid in source_ids if sid in labels]
            chain.append(
                {
                    **node,
                    "label": evidence_labels[0] if evidence_labels else None,
                    "evidence_labels": evidence_labels,
                }
            )
            for sid in source_ids:
                if sid not in labels:
                    hierarchy["errors"].append(
                        f"HS{node['level']} wording omitted from generation context: {node['code']} ({sid})"
                    )
        hierarchy = {
            **hierarchy,
            "chain": chain,
            "errors": list(hierarchy["errors"]),
        }
        for sid in view.get("context_ids", []):
            if sid not in labels:
                hierarchy["errors"].append(
                    f"Source branch condition omitted from generation context: {sid}"
                )
        if hierarchy["errors"]:
            hierarchy["status"] = "INVALID"
            if hierarchy.get("structure_status") == "VERIFIED":
                hierarchy["legal_evidence_status"] = "INSUFFICIENT"
        context_labels = [labels[sid] for sid in view.get("context_ids", []) if sid in labels]
        required = {label for node in hierarchy["chain"] for label in node["evidence_labels"]}
        required.update(context_labels)
        wording_ids = [row["id"], *[node["id"] for node in hierarchy["chain"]]]
        defining_notes = _defining_notes(view, wording_ids, graph)
        missing_definitions = [sid for sid in defining_notes if sid not in labels]
        if missing_definitions:
            hierarchy["status"] = "INVALID"
            hierarchy["legal_evidence_status"] = "INSUFFICIENT"
            hierarchy["errors"].append(
                "Defining notes omitted from context: " + ", ".join(missing_definitions)
            )
        required.update(labels[sid] for sid in defining_notes if sid in labels)
        evidence.append(
            {
                "code": row["code"],
                "wording_label": labels[row["id"]],
                "ancestor_labels": [
                    labels[sid] for sid in view.get("ancestor_ids", []) if sid in labels
                ],
                "context_labels": context_labels,
                "required_citation_labels": sorted(required, key=lambda label: int(label[1:])),
                "defining_note_labels": [labels[sid] for sid in defining_notes if sid in labels],
                "related_note_labels": [
                    labels[sid] for sid in view.get("note_ids", []) if sid in labels
                ],
                "hierarchy": hierarchy,
                "note_applicability": "REQUIRES_SOURCE_REASONING",
            }
        )
    return evidence


def _compact_locator(locator: dict) -> dict:
    origin = locator.get("source", {})
    pages = set(locator.get("physical_pages") or [])
    page = locator.get("physical_page") or origin.get("physical_page")
    if page is not None:
        pages.add(page)
    pages.update(c["physical_page"] for c in locator.get("continuations", []))
    values = {
        "document": locator.get("document") or origin.get("source_filename"),
        "physical_page": locator.get("physical_page") or origin.get("physical_page"),
        "printed_page": locator.get("printed_page") or origin.get("printed_page"),
        "graph_source_node": locator.get("graph_source_node"),
        "sha256": locator.get("sha256"),
        "bbox": locator.get("bbox"),
        "file": locator.get("file"),
        "block": locator.get("block"),
        "article": locator.get("article"),
        "official_url": locator.get("official_url"),
        "wording_status": locator.get("wording_status"),
        "continuations": locator.get("continuations"),
        "physical_pages": sorted(pages)
        if len(pages) > 1 or locator.get("physical_pages")
        else None,
    }
    return {k: v for k, v in values.items() if v is not None}


def _source_groups(rows: list[dict], candidates: list[dict], graph) -> list[list[dict]]:
    labelled = [{"id": row["id"], "label": f"S{i + 1}"} for i, row in enumerate(rows)]
    by_label = {source["label"]: source["id"] for source in labelled}
    available = set(by_label.values())
    groups = {}
    for candidate, evidence in zip(
        [c for c in candidates if c["id"] in available],
        _candidate_evidence(candidates, labelled, graph),
        strict=True,
    ):
        labels = set(evidence["required_citation_labels"]) | set(evidence["ancestor_labels"])
        required = {by_label[label] for label in labels}
        groups[candidate["id"]] = [
            candidate,
            *[row for row in rows if row["id"] in required and row["id"] != candidate["id"]],
        ]
    return [groups.get(row["id"], [row]) for row in rows]


def _pack_source(row: dict, index: int) -> dict:
    return {
        "label": f"S{index}",
        "id": row["id"],
        "text": row["source_text"],
        "code": row.get("code"),
        "chunk_type": row.get("chunk_type"),
        "locator": _compact_locator(row.get("locator", {})),
        "effective_from": str(row.get("effective_from") or ""),
        "effective_to": str(row.get("effective_to") or ""),
        "legal_status": row.get("legal_status"),
        "applicability_note": row.get("metadata", {}).get("validity_review", {}).get("note"),
    }


def _model_source(source: dict) -> dict:
    """Keep readable source provenance in the model view; retain audit geometry outside it."""
    projected = {key: value for key, value in source.items() if value not in (None, "", {})}
    locator = {
        key: value
        for key, value in source.get("locator", {}).items()
        if key
        in {
            "document",
            "physical_page",
            "printed_page",
            "physical_pages",
            "block",
            "article",
            "wording_status",
        }
    }
    if locator:
        projected["locator"] = locator
    else:
        projected.pop("locator", None)
    return projected


def _model_candidate_evidence(evidence: list[dict]) -> list[dict]:
    """Reference source labels once per chain without copying graph audit identifiers."""
    compact = []
    for candidate in evidence:
        hierarchy = candidate["hierarchy"]
        compact.append(
            {
                key: candidate[key]
                for key in (
                    "code",
                    "wording_label",
                    "context_labels",
                    "required_citation_labels",
                    "related_note_labels",
                )
            }
            | {
                "hierarchy": {
                    "status": hierarchy["status"],
                    "chain": [
                        {
                            key: node[key]
                            for key in ("code", "level", "wording_origin", "evidence_labels")
                        }
                        for node in hierarchy["chain"]
                    ],
                    "errors": hierarchy["errors"],
                }
            }
        )
    return compact


def _serialize(value: dict | list) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))


def _context_payload(
    base: dict,
    packed: list[dict],
    candidates: list[dict],
    graph,
    comparison_candidates: list[dict] | None = None,
    comparison_groups: list[dict] | None = None,
) -> dict:
    packed = bind_evidence(packed, base.get("snapshot"))
    included = {source["id"] for source in packed}
    payload = {
        **base,
        "sources": model_sources([_model_source(source) for source in packed]),
        "candidate_hs_codes": [
            row["code"]
            for row in candidates
            if row["id"] in included and re.fullmatch(r"[0-9]{8}", row.get("code") or "")
        ],
        "candidate_evidence": [
            model_candidate(item, packed)
            for item in _model_candidate_evidence(_candidate_evidence(candidates, packed, graph))
        ],
    }
    from rag.llm.evidence.conditions import sources_with_spans

    payload["sources"] = sources_with_spans(payload["sources"])
    if base.get("requirements_scopes"):
        ids = {s["id"]: s["evidence_id"] for s in packed}
        payload["requirements_scopes"] = [
            {
                **{k: v for k, v in scope.items() if k != "source_ids"},
                "evidence_ids": [ids[sid] for sid in scope["source_ids"] if sid in ids],
                "complete": scope["complete"] and set(scope["source_ids"]) <= ids.keys(),
            }
            for scope in base["requirements_scopes"]
        ]
    if comparison_groups:
        evidence = _candidate_evidence(comparison_candidates or candidates, packed, graph)
        seed_codes = {c["code"] for c in candidates}
        extra_evidence = [
            model_candidate(
                {
                    key: item[key]
                    for key in (
                        "code",
                        "wording_label",
                        "context_labels",
                        "required_citation_labels",
                    )
                }
                | {"hierarchy_status": item["hierarchy"]["status"]},
                packed,
            )
            for item in _model_candidate_evidence(evidence)
            if item["code"] not in seed_codes
        ]
        comparison = comparison_payload(comparison_groups, evidence, packed)
        if extra_evidence:
            payload["comparison_candidates"] = extra_evidence
        # Avoid repeating a complete flat candidate list already present in candidate_evidence.
        if extra_evidence or any(g["branch_options"] or g["missing_codes"] for g in comparison):
            payload["candidate_comparison"] = comparison
    return payload


def _messages(user_message: str, system_prompt: str = SYSTEM_PROMPT) -> list[dict]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def prepare_context(question: str, result: dict, task: str, config, graph=None) -> dict:
    from rag.llm.contracts.obligations import draft_packet, requests_current
    from rag.retrieval.request_plan import request_from_plan

    request = request_from_plan(question, result.get("query_plan", {}))
    if request is None and result.get("query_plan", {}).get("status") == "FALLBACK_RAW":
        from rag.llm.contracts.errors import RequestPlanError

        raise RequestPlanError("Kế hoạch mục tiêu chưa hợp lệ; chưa thể tạo kết quả phân loại.")
    if request is not None:
        from rag.llm.context.task_context import prepare_task_context

        return prepare_task_context(question, result, task, config, graph, request)
    planned = result.get("_task_request")
    schema, system_prompt = MODEL_ANSWER_SCHEMA, SYSTEM_PROMPT
    if planned is not None:
        from rag.prompts.generation.task_answering import TASK_ANSWER_SCHEMA, TASK_SYSTEM_PROMPT

        schema, system_prompt = TASK_ANSWER_SCHEMA, TASK_SYSTEM_PROMPT
    if task not in {"hs", "qa", "auto"}:
        raise ValueError("Task must be hs, qa or auto")
    token_mode = getattr(config, "use_model_token_limits", False)
    max_input_chars = None if token_mode else config.max_input_chars
    max_context_chars = None if token_mode else config.max_context_chars
    if not question.strip() or (max_input_chars is not None and len(question) > max_input_chars):
        raise ValueError("Question is empty or exceeds GROQ_MAX_INPUT_CHARS")
    limit = min(result.get("_candidate_limit", 10), 48)
    seeds = result.get("hs_candidates", [])[:limit] if task in {"hs", "auto"} else []
    comparison_candidates, comparison_groups = comparison_neighbours(seeds, graph)
    rows, candidates = source_rows(
        result, task, graph, candidate_limit=limit, comparison_candidates=comparison_candidates
    )
    if planned is not None:
        from rag.prompts.generation.task_answering import task_answer_schema

        schema = task_answer_schema(
            planned, [c["code"] for c in [*candidates, *comparison_candidates]]
        )
    user_context = bind_user_context(question)
    base = {
        "task": task,
        "task_instruction": TASK_INSTRUCTIONS[task],
        "question": question,
        "user_context": user_context,
        "snapshot": result.get("snapshot"),
        "omitted_source_count": len(rows),
        "evidence_scope": "RETRIEVED_CONTEXT_ONLY_NOT_ENTIRE_DATABASE",
        "scope": result.get("coverage", {}),
        "legal_validity": "LOCAL_SOURCE_METADATA_NOT_INDEPENDENTLY_VERIFIED",
    }
    if task == "auto":
        base["intent_advice"] = result.get("semantic_intent", {})
    if planned is not None:
        from rag.llm.evidence.proof_contract import product_fact_ids

        base.update(
            legal_scope="CURRENT_APPLICABILITY"
            if requests_current(question)
            else "SOURCE_SNAPSHOT",
            product_fact_ids=product_fact_ids(user_context),
            request=planned,
            task_instruction=GOAL_TASK_INSTRUCTION,
            requirements_scopes=result.get("_requirements_scopes", []),
        )
    packed: list[dict] = []
    payload = _context_payload(
        base, packed, candidates, graph, comparison_candidates, comparison_groups
    )
    user_message = _serialize(draft_packet(payload))
    base_schema = schema
    if planned is not None:
        schema = bind_registry_schema(
            base_schema,
            [],
            base.get("product_fact_ids", [s["id"] for s in user_context["statements"]]),
        )
    budget = (
        request_budget(_messages(user_message, system_prompt), schema, config.model)
        if token_mode
        else None
    )
    if budget is not None and not budget["fits"]:
        raise ContextBudgetError(config.model, "cliproxyapi", budget)
    if max_input_chars is not None and len(user_message) > max_input_chars:
        raise ValueError("Question and source metadata exceed GROQ_MAX_INPUT_CHARS")
    included: set[str] = set()
    for group in _source_groups(rows, comparison_candidates, graph):
        additions = [row for row in group if row["id"] not in included]
        if not additions:
            continue
        proposed = [
            *packed,
            *[_pack_source(row, len(packed) + i + 1) for i, row in enumerate(additions)],
        ]
        projected_sources = model_sources(
            [_model_source(source) for source in bind_evidence(proposed, result.get("snapshot"))]
        )
        if max_context_chars is not None and len(_serialize(projected_sources)) > max_context_chars:
            continue
        trial = _context_payload(
            {**base, "omitted_source_count": len(rows) - len(proposed)},
            proposed,
            candidates,
            graph,
            comparison_candidates,
            comparison_groups,
        )
        message = _serialize(draft_packet(trial))
        trial_schema = (
            bind_registry_schema(
                base_schema,
                [s["evidence_id"] for s in bind_evidence(proposed, result.get("snapshot"))],
                base.get("product_fact_ids", [s["id"] for s in user_context["statements"]]),
            )
            if planned is not None
            else schema
        )
        trial_budget = (
            request_budget(_messages(message, system_prompt), trial_schema, config.model)
            if token_mode
            else None
        )
        if (max_input_chars is None or len(message) <= max_input_chars) and (
            trial_budget is None or trial_budget["fits"]
        ):
            packed, payload, user_message = proposed, trial, message
            budget = trial_budget
            schema = trial_schema
            included.update(row["id"] for row in additions)
    omitted = [row["id"] for row in rows if row["id"] not in included]
    messages = _messages(user_message, system_prompt)
    packed = bind_evidence(packed, result.get("snapshot"))
    return {
        "response_protocol": "goals-v1" if planned is not None else "registry-v2",
        **(
            {
                "proof_required": False,
                "reasoning_contract": "semantic-v1",
                "legal_scope": "CURRENT_APPLICABILITY"
                if requests_current(question)
                else "SOURCE_SNAPSHOT",
            }
            if planned is not None
            else {}
        ),
        **(
            {"request": planned, "candidate_provenance": result.get("_candidate_provenance", {})}
            if planned is not None
            else {}
        ),
        "user_context": user_context,
        "task": task,
        "question": question,
        "sources": packed,
        "allowed_hs_codes": payload["candidate_hs_codes"],
        "retrieved_hs_codes": [r["code"] for r in result.get("hs_candidates", [])],
        "query_plan": result.get("query_plan", {}),
        "requirements_scopes": payload.get("requirements_scopes", []),
        "query_preprocessing_hash": result.get("query_preprocessing_hash"),
        "candidate_evidence": _candidate_evidence(candidates, packed, graph),
        "comparison_candidates": [
            e
            for e in _candidate_evidence(comparison_candidates, packed, graph)
            if e["code"] not in {c["code"] for c in candidates}
        ],
        "candidate_comparison": comparison_payload(
            comparison_groups, _candidate_evidence(comparison_candidates, packed, graph), packed
        ),
        "source_locators": {
            s["label"]: next(r.get("locator", {}) for r in rows if r["id"] == s["id"])
            for s in packed
        },
        "omitted_source_ids": omitted,
        "packing": {
            "input_chars": len(user_message),
            "max_input_chars": max_input_chars,
            "system_chars": len(system_prompt),
            "user_chars": len(user_message),
            "schema_chars": len(_serialize(schema)),
            "source_chars": len(_serialize(payload["sources"])),
            "max_context_chars": max_context_chars,
            "request_budget": budget,
            "omitted_candidate_codes": [c["code"] for c in candidates if c["id"] not in included],
        },
        "context_hash": digest(payload),
        "prompt_hash": digest(system_prompt),
        "schema_hash": digest(schema),
        "messages": messages,
        "snapshot": result.get("snapshot"),
        "profile": result.get("profile"),
        "policy_hash": result.get("policy_hash"),
    }
