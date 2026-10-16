"""Pack user facts, cited source text and verified HS evidence for the LLM."""

import json
import re

from rag.graph.context import GraphContext
from rag.ingestion.sources import SOURCE_TYPES
from rag.llm.budget import ContextBudgetError, request_budget
from rag.prompts.schemas import ANSWER_SCHEMA
from rag.prompts.system import SYSTEM_PROMPT
from rag.prompts.tasks import TASK_INSTRUCTIONS, USER_SUPPLEMENT_TEMPLATE
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
    result: dict, task: str, graph=None, candidate_limit: int = 10
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
    for row in candidates:
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
                    target.append(
                        {
                            **graph.records.get(sid, {}),
                            "id": sid,
                            "source_text": citation["text"],
                            "locator": citation["locator"],
                        }
                    )
    rows.extend([*result.get("matches", []), *result.get("package", []), *notes])
    unique = {}
    for row in rows:
        if graph is not None and graph.citation(row["id"]) is None:
            continue
        if row.get("source_text") and row["id"] not in unique:
            unique[row["id"]] = row
    return list(unique.values()), candidates


def _candidate_evidence(candidates: list[dict], sources: list[dict], graph) -> list[dict]:
    labels = {s["id"]: s["label"] for s in sources}
    evidence = []
    for row in candidates:
        if row["id"] not in labels:
            continue
        view = graph.source_view(row) if graph is not None else {}
        hierarchy: dict = (
            graph.hs_hierarchy(row)
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
        evidence.append(
            {
                "code": row["code"],
                "wording_label": labels[row["id"]],
                "ancestor_labels": [
                    labels[sid] for sid in view.get("ancestor_ids", []) if sid in labels
                ],
                "context_labels": context_labels,
                "required_citation_labels": sorted(required, key=lambda label: int(label[1:])),
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
    }


def _model_source(source: dict) -> dict:
    """Keep readable source provenance in the model view; retain audit geometry outside it."""
    projected = {key: value for key, value in source.items() if value not in (None, "", {})}
    locator = {
        key: value
        for key, value in source.get("locator", {}).items()
        if key in {"document", "physical_page", "printed_page", "physical_pages"}
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


def _context_payload(base: dict, packed: list[dict], candidates: list[dict], graph) -> dict:
    included = {source["id"] for source in packed}
    return {
        **base,
        "sources": [_model_source(source) for source in packed],
        "candidate_hs_codes": [
            row["code"]
            for row in candidates
            if row["id"] in included and re.fullmatch(r"[0-9]{8}", row.get("code") or "")
        ],
        "candidate_evidence": _model_candidate_evidence(
            _candidate_evidence(candidates, packed, graph)
        ),
    }


def _messages(user_message: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def prepare_context(question: str, result: dict, task: str, config, graph=None) -> dict:
    if task not in {"hs", "qa", "auto"}:
        raise ValueError("Task must be hs, qa or auto")
    token_mode = getattr(config, "use_model_token_limits", False)
    max_input_chars = None if token_mode else config.max_input_chars
    max_context_chars = None if token_mode else config.max_context_chars
    if not question.strip() or (max_input_chars is not None and len(question) > max_input_chars):
        raise ValueError("Question is empty or exceeds GROQ_MAX_INPUT_CHARS")
    rows, candidates = source_rows(result, task, graph)
    base = {
        "task": task,
        "task_instruction": TASK_INSTRUCTIONS[task],
        "question": question,
        "omitted_source_count": len(rows),
        "evidence_scope": "RETRIEVED_CONTEXT_ONLY_NOT_ENTIRE_DATABASE",
        "scope": result.get("coverage", {}),
        "legal_validity": "LOCAL_SOURCE_METADATA_NOT_INDEPENDENTLY_VERIFIED",
    }
    if task == "auto":
        base["intent_advice"] = result.get("semantic_intent", {})
    packed: list[dict] = []
    payload = _context_payload(base, packed, candidates, graph)
    user_message = _serialize(payload)
    budget = (
        request_budget(_messages(user_message), ANSWER_SCHEMA, config.model) if token_mode else None
    )
    if budget is not None and not budget["fits"]:
        raise ContextBudgetError(config.model, "cliproxyapi", budget)
    if max_input_chars is not None and len(user_message) > max_input_chars:
        raise ValueError("Question and source metadata exceed GROQ_MAX_INPUT_CHARS")
    included: set[str] = set()
    for group in _source_groups(rows, candidates, graph):
        additions = [row for row in group if row["id"] not in included]
        if not additions:
            continue
        proposed = [
            *packed,
            *[_pack_source(row, len(packed) + i + 1) for i, row in enumerate(additions)],
        ]
        model_sources = [_model_source(source) for source in proposed]
        if max_context_chars is not None and len(_serialize(model_sources)) > max_context_chars:
            continue
        trial = _context_payload(
            {**base, "omitted_source_count": len(rows) - len(proposed)}, proposed, candidates, graph
        )
        message = _serialize(trial)
        trial_budget = (
            request_budget(_messages(message), ANSWER_SCHEMA, config.model) if token_mode else None
        )
        if (max_input_chars is None or len(message) <= max_input_chars) and (
            trial_budget is None or trial_budget["fits"]
        ):
            packed, payload, user_message = proposed, trial, message
            budget = trial_budget
            included.update(row["id"] for row in additions)
    omitted = [row["id"] for row in rows if row["id"] not in included]
    messages = _messages(user_message)
    return {
        "task": task,
        "question": question,
        "sources": packed,
        "allowed_hs_codes": payload["candidate_hs_codes"],
        "retrieved_hs_codes": [r["code"] for r in result.get("hs_candidates", [])],
        "candidate_evidence": _candidate_evidence(candidates, packed, graph),
        "source_locators": {
            s["label"]: next(r.get("locator", {}) for r in rows if r["id"] == s["id"])
            for s in packed
        },
        "omitted_source_ids": omitted,
        "packing": {
            "input_chars": len(user_message),
            "max_input_chars": max_input_chars,
            "system_chars": len(SYSTEM_PROMPT),
            "user_chars": len(user_message),
            "schema_chars": len(_serialize(ANSWER_SCHEMA)),
            "source_chars": len(_serialize(payload["sources"])),
            "max_context_chars": max_context_chars,
            "request_budget": budget,
            "omitted_candidate_codes": [c["code"] for c in candidates if c["id"] not in included],
        },
        "context_hash": digest(payload),
        "prompt_hash": digest(SYSTEM_PROMPT),
        "schema_hash": digest(ANSWER_SCHEMA),
        "messages": messages,
        "snapshot": result.get("snapshot"),
        "profile": result.get("profile"),
        "policy_hash": result.get("policy_hash"),
    }
