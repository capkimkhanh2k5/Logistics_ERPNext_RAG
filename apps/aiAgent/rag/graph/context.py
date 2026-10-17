"""Source graph context for every registered tariff chapter."""

import re
from collections import defaultdict, deque
from functools import lru_cache
from typing import Any

from rag.chunking.corpus import load_corpus
from rag.graph.legal_evidence import (
    BINDING_VERSION,
    CONSOLIDATED_ROW,
    evidence_digest,
    normalized_wording,
)
from rag.ingestion.sources import first


def context_text(row: dict, hierarchy: list[dict], notes: list[dict], style: str) -> str:
    if style not in {"plain", "structured"}:
        raise ValueError(f"Unsupported shared context format: {style}")
    parts = [row.get("embedding_text") or row["leaf_text"]]
    seen = {" ".join(parts[0].split())}
    for c in [*hierarchy, *notes]:
        text = " ".join(c["text"].split())
        if text in seen:
            continue
        seen.add(text)
        label = (
            "Chú giải nguồn"
            if c in notes
            else "Nhánh nguồn"
            if c["kind"] == "context"
            else "Phân cấp nguồn"
        )
        parts.append(f"{label}: {text}" if style == "structured" else text)
    return "\n".join(parts)


def fit_rerank_context(
    query: str, rows: list[dict], tokenizer, max_tokens: int = 1152
) -> list[dict]:
    """Drop whole optional citations to fit the model; preserve query and atomic source."""
    fitted = []
    lengths = tokenizer([[query, r["rerank_text"]] for r in rows], truncation=False)["input_ids"]
    for row, tokens in zip(rows, lengths, strict=True):
        if len(tokens) <= max_tokens:
            fitted.append(row)
            continue
        hierarchy, notes = list(row["hierarchy_citations"]), list(row["note_citations"])
        omitted = []
        base = row.get("embedding_text") or row["leaf_text"]
        text = row["rerank_text"]
        while len(tokenizer([[query, text]], truncation=False)["input_ids"][0]) > max_tokens:
            if notes:
                omitted.append(notes.pop()["id"])
            elif hierarchy:
                omitted.append(hierarchy.pop()["id"])
            else:
                raise ValueError(f"Atomic source and query exceed reranker budget: {row['id']}")
            text = context_text(
                {**row, "embedding_text": base},
                hierarchy,
                notes,
                row.get("context_format", "plain"),
            )
        fitted.append(
            {
                **row,
                "rerank_text": text,
                "hierarchy_citations": hierarchy,
                "note_citations": notes,
                "rerank_omitted_ids": omitted,
            }
        )
    return fitted


class GraphContext:
    """Traverse source relationships; never infer legal branches from a code's digits."""

    def __init__(self, records: list[dict], nodes: list[dict], edges: list[dict]) -> None:
        self.records = {r["id"]: r for r in records}
        self.nodes = {n["id"]: n.get("metadata", {}) for n in nodes}
        self.parents: dict[str, set[str]] = defaultdict(set)
        self.children: dict[str, set[str]] = defaultdict(set)
        self.contexts: dict[str, set[str]] = defaultdict(set)
        self.notes: dict[str, set[str]] = defaultdict(set)
        note_to_scope = {
            "APPLIES_TO",
            "APPLIES_WITHIN",
            "GOVERNS",
            "DEFINES_FOR",
            "DEFINITION_APPLIES_TO",
            "INCLUDES_IN_SCOPE",
            "DEFINES_SCOPE_OF",
        }
        scope_to_note = {"CONSTRAINED_BY", "GOVERNED_BY", "HAS_LEGAL_NOTE", "SUBJECT_TO"}
        for e in edges:
            source, target, relation = e["source"], e["target"], e["relation"]
            if relation == "CONTAINS":
                self.parents[target].add(source)
                self.children[source].add(target)
            elif relation == "CONTEXT_FOR":
                self.contexts[target].add(source)
            elif relation in note_to_scope and self.is_note(source):
                self.notes[target].add(source)
            elif relation in scope_to_note and self.is_note(target):
                self.notes[source].add(target)

    def is_note(self, node_id: str) -> bool:
        r = self.records.get(node_id, self.nodes.get(node_id, {}))
        return r.get("chunk_type") in {
            "section_note",
            "chapter_note",
            "subheading_note",
            "tariff_footnote",
        }

    def ancestors(self, node_id: str, max_depth: int = 12) -> list[str]:
        distance = {}
        frontier = deque([(node_id, 0)])
        visited = {node_id}
        while frontier:
            child, depth = frontier.popleft()
            if depth >= max_depth:
                continue
            for parent in sorted(self.parents.get(child, set())):
                if parent in visited:
                    continue
                visited.add(parent)
                distance[parent] = depth + 1
                frontier.append((parent, depth + 1))
        return sorted(distance, key=lambda n: (-distance[n], n))

    def citation(self, node_id: str) -> dict | None:
        row = self.records.get(node_id)
        md = self.nodes.get(node_id, {})
        if row is None and not first(md, "locator.sha256", "provenance.sha256", "source.sha256"):
            # Navigation-only nodes remain traversable but are not quoted as source evidence.
            return None
        # Nonprinted/derived nodes remain in the path but never become legal wording.
        original = row.get("metadata", {}).get("original", {}) if row else md
        if md.get("virtual") or first(original, "hs.source_explicit") is False:
            return None
        if row and row.get("locator", {}).get("basis") in {
            "UNPRINTED_TAXONOMY_NODE_NOT_LEGAL_WORDING",
            "NORMALIZED_TERM_INDEX_LABEL_NOT_LEGAL_WORDING",
        }:
            return None
        text = (
            row.get("source_text")
            if row
            else first(
                md,
                "source_text",
                "description_vi",
                "label_vi",
                "text.vi",
                "content.legal_text_vi_normalized",
                "content.description_vi_normalized",
            )
        )
        if not text or not str(text).strip():
            return None
        locator = row.get("locator") if row else first(md, "locator", "provenance", "source")
        return {
            "id": node_id,
            "text": " ".join(str(text).split()),
            "locator": locator or {"graph_source_node": node_id},
            "kind": "context" if (row or md).get("role") == "context" else "source",
            "depth": md.get("depth"),
        }

    def source_view(self, row: dict) -> dict:
        ancestors = self.ancestors(row["id"])
        citations, seen, context_ids, note_ids = [], set(), [], set()
        for nid in [*ancestors, row["id"]]:
            if nid != row["id"]:
                citation = self.citation(nid)
                if citation and citation["id"] not in seen:
                    citations.append(citation)
                    seen.add(citation["id"])
            for context_id in sorted(self.contexts.get(nid, set())):
                context_citation = self.citation(context_id)
                if context_citation and context_citation["id"] not in seen:
                    citations.append(context_citation)
                    seen.add(context_citation["id"])
                    context_ids.append(context_id)
            note_ids.update(self.notes.get(nid, set()))
        return {
            "ancestor_ids": ancestors,
            "citations": citations,
            "context_ids": context_ids,
            "note_ids": sorted(note_ids),
        }

    def node_code(self, node_id: str) -> str | None:
        return first(self.records.get(node_id, {}), "code") or first(
            self.nodes.get(node_id, {}), "code_compact", "code", "hs.code_compact"
        )

    def legal_evidence(self, node_id: str) -> list[dict]:
        direct = self.citation(node_id)
        if direct:
            return [{**direct, "wording_origin": "DIRECT_SOURCE"}]
        proof = self.nodes.get(node_id, {}).get("legal_evidence_binding", {})
        if (
            proof.get("version") != BINDING_VERSION
            or proof.get("kind") != CONSOLIDATED_ROW
            or proof.get("status") != "VERIFIED"
            or proof.get("wording_status") != "NORMALIZED_COMPLETE_MATCH"
            or proof.get("scope_basis") != "FULL_PDF_CODE_COLUMN_AND_UNDIVIDED_BILINGUAL_ROW"
        ):
            return []
        code = proof.get("source_code", "")
        covered = [code[:4], code[:6], code]
        ids = proof.get("covered_node_ids", {})
        if (
            not re.fullmatch(r"[0-9]{4}0000", code)
            or proof.get("covered_codes") != covered
            or proof.get("printed_codes") != [code]
            or ids.get(self.node_code(node_id)) != node_id
            or any(self.node_code(ids.get(c)) != c for c in covered)
        ):
            return []
        source_id = proof.get("source_id")
        source = self.records.get(source_id, {})
        citation = self.citation(source_id)
        if (
            not citation
            or source_id != ids.get(code)
            or source.get("code") != code
            or evidence_digest(source.get("source_text")) != proof.get("source_text_hash")
            or evidence_digest(source.get("locator")) != proof.get("source_locator_hash")
            or any(
                source.get("locator", {}).get(k) != v for k, v in proof.get("locator", {}).items()
            )
            or normalized_wording(source.get("source_text", ""))
            != normalized_wording(source.get("locator", {}).get("raw_pdf_text", ""))
        ):
            return []
        if node_id not in self.ancestors(source_id):
            return []
        descendants, frontier = set(), [node_id]
        leaves = set()
        while frontier:
            current = frontier.pop()
            if current in descendants:
                continue
            descendants.add(current)
            if re.fullmatch(r"[0-9]{8}", self.node_code(current) or ""):
                leaves.add(current)
            frontier.extend(self.children.get(current, set()))
        if leaves != {source_id}:
            return []
        return [{**citation, "wording_origin": CONSOLIDATED_ROW}]

    def hs_hierarchy(self, row: dict, *, target_level: int = 8) -> dict:
        """Verify codes against CONTAINS paths; prefixes alone never establish ancestry."""
        code = row.get("code") or ""
        errors: list[str] = []
        legal_errors: list[str] = []
        chain: list[dict] = []
        if target_level not in (4, 6, 8) or not re.fullmatch(rf"[0-9]{{{target_level}}}", code):
            return {
                "status": "INVALID",
                "structure_status": "INVALID",
                "legal_evidence_status": "INSUFFICIENT",
                "chain": [],
                "errors": [f"HS target must have {target_level} ASCII digits"],
            }
        ancestors = self.ancestors(row["id"])

        if self.node_code(row["id"]) != code:
            errors.append("Candidate code differs from its source graph node")
        for level in (n for n in (4, 6, 8) if n <= target_level):
            expected = code[:level]
            ids = (
                [row["id"]]
                if level == target_level
                else [sid for sid in ancestors if self.node_code(sid) == expected]
            )
            if len(ids) != 1:
                errors.append(f"Expected one graph ancestor for HS{level} {expected}")
                continue
            sid = ids[0]
            record, metadata = self.records.get(sid, {}), self.nodes.get(sid, {})
            declared_level = record.get("level") or metadata.get("level")
            if declared_level is not None and declared_level != level:
                errors.append(f"Source level differs from code length: {sid}")
            navigation_only = (
                metadata.get("virtual")
                or record.get("locator", {}).get("basis")
                == "UNPRINTED_TAXONOMY_NODE_NOT_LEGAL_WORDING"
                or first(record.get("metadata", {}).get("original", metadata), "hs.source_explicit")
                is False
            )
            citation = self.citation(sid)
            evidence = self.legal_evidence(sid)
            if not evidence and (
                level == target_level
                or level != 6
                or not navigation_only
                or metadata.get("legal_evidence_binding")
            ):
                legal_errors.append(f"Missing legal wording for HS{level} {expected}")
            chain.append(
                {
                    "id": sid,
                    "code": expected,
                    "level": level,
                    "has_legal_wording": bool(citation),
                    "legal_evidence_ids": [c["id"] for c in evidence],
                    "wording_origin": evidence[0]["wording_origin"]
                    if evidence
                    else "NAVIGATION_ONLY",
                }
            )
        for sid in ancestors:
            parent_code = self.node_code(sid)
            if isinstance(parent_code, str) and re.fullmatch(r"[0-9]{4}|[0-9]{6}", parent_code):
                if not code.startswith(parent_code):
                    errors.append(f"HS ancestor belongs to another branch: {parent_code}")
        for parent, child in zip(chain, chain[1:]):
            if parent["id"] not in self.ancestors(child["id"]):
                errors.append(
                    f"Missing graph parent-child path: {parent['code']} -> {child['code']}"
                )
            if child["id"] in self.ancestors(parent["id"]):
                errors.append("HS hierarchy contains a cycle")
        return {
            "status": "INVALID" if errors or legal_errors else "VERIFIED",
            "structure_status": "INVALID" if errors else "VERIFIED",
            "legal_evidence_status": "INSUFFICIENT" if legal_errors else "VERIFIED",
            "chain": chain,
            "errors": errors + legal_errors,
        }

    def enrich(
        self,
        rows: list[dict],
        context_budget: int = 5000,
        note_budget: int = 1500,
        relevant_notes: list[str] | None = None,
        include_hierarchy: bool = True,
        include_notes: bool = True,
    ) -> list[dict]:
        enriched = []
        note_order = {nid: rank for rank, nid in enumerate(relevant_notes or [])}
        for row in rows:
            view = self.source_view(row)
            base = row.get("embedding_text") or row.get("source_text") or ""
            parts, used, omitted, citations = [base], len(base), [], []
            included_text = {" ".join(base.split())}
            if include_hierarchy:
                ordered = sorted(
                    view["citations"],
                    key=lambda c: (
                        0 if c["id"] in view["context_ids"] else 1,
                        (c.get("depth") or 0)
                        if c["id"] in view["context_ids"]
                        else -(self.records.get(c["id"], {}).get("level") or 0),
                        c["id"],
                    ),
                )
                for citation in ordered:
                    normalized = " ".join(citation["text"].split())
                    if normalized in included_text:
                        citations.append(citation)
                        continue
                    if used + len(citation["text"]) + 1 <= context_budget:
                        parts.append(citation["text"])
                        included_text.add(normalized)
                        used += len(citation["text"]) + 1
                        citations.append(citation)
                    else:
                        omitted.append(citation["id"])
            notes, note_used = [], 0
            if include_notes:
                ids = sorted(view["note_ids"], key=lambda nid: (note_order.get(nid, 10**9), nid))
                # Query-retrieved notes are related source material, not proof of applicability.
                for nid in ids:
                    if relevant_notes is not None and nid not in note_order:
                        continue
                    citation = self.citation(nid)
                    if citation and note_used + len(citation["text"]) <= note_budget:
                        notes.append(citation)
                        parts.append(citation["text"])
                        note_used += len(citation["text"])
                    elif citation:
                        omitted.append(nid)
            enriched.append(
                {
                    **row,
                    "leaf_text": row.get("source_text", base),
                    "rerank_text": "\n".join(parts),
                    "context_chain": [c["text"] for c in citations],
                    "intermediate_branches": [
                        c["text"] for c in citations if c["id"] in view["context_ids"]
                    ],
                    "hierarchy_citations": citations,
                    "note_citations": notes,
                    "graph_context": {
                        **view,
                        "omitted_ids": omitted,
                        "applicability": "REQUIRES_SOURCE_REASONING",
                    },
                }
            )
        return enriched

    def format_candidates(self, rows: list[dict], style: str) -> list[dict]:
        return [
            {
                **r,
                "rerank_text": context_text(
                    r, r["hierarchy_citations"], r["note_citations"], style
                ),
                "context_format": style,
            }
            for r in rows
        ]

    def candidate_views(self) -> dict[str, dict]:
        rows = [
            r
            for r in self.records.values()
            if r.get("level") == 8 and r.get("chunk_type") == "tariff_entry"
        ]
        return {r["id"]: r for r in self.enrich(rows, include_notes=False)}


@lru_cache(maxsize=1)
def load_hierarchy_catalog() -> dict[str, dict[str, Any]]:
    bundle = load_corpus()
    graph = GraphContext(bundle["records"], bundle["nodes"], bundle["edges"])
    return {r["code"]: r for r in graph.candidate_views().values()}


def enrich_candidates_with_full_context(
    candidates: list[dict], graph: GraphContext | None = None
) -> list[dict]:
    if graph is not None:
        return graph.enrich(candidates)
    catalog = load_hierarchy_catalog()
    return [
        {
            **r,
            **{
                k: v
                for k, v in catalog.get(r.get("code") or "", {}).items()
                if k
                in (
                    "rerank_text",
                    "context_chain",
                    "intermediate_branches",
                    "hierarchy_citations",
                    "graph_context",
                )
            },
        }
        for r in candidates
    ]
