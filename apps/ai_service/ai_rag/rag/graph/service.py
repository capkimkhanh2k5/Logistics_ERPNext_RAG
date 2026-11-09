"""Unified Graph Service with Dual-Engine Architecture (In-Memory Corpus & Apache AGE).

Uses the authoritative `load_corpus()` bundle (7,004 nodes, 21,752 edges across
Sections XIV, XVI, XVII, PDF context branches, GIR rules, TT85, ND26, VBHN05, TT02)
as Single Source of Truth, while bridging `GraphContext` for RAG Core and
serving interactive subgraphs for Cytoscape.js.
"""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from rag.graph.age_adapter import ApacheAgeAdapter
from rag.ingestion.sources import first

AI_RAG_ROOT = Path(__file__).resolve().parents[2]


def _load_corpus_bundle() -> Dict[str, Any]:
    corpus_file = AI_RAG_ROOT / "artifacts" / "corpus.json"
    if corpus_file.is_file():
        return json.loads(corpus_file.read_text(encoding="utf-8"))
    from rag.chunking.corpus import load_corpus

    return load_corpus()

logger = logging.getLogger("rag.graph.service")

SECTION_ROOT_IDS = [
    ("tt31:SEC:XIV", "XIV", "Phần XIV — Ngọc trai, đá quý, kim loại quý (Chương 71)"),
    ("tt31:SXVI-S-XVI", "XVI", "Phần XVI — Máy và thiết bị cơ khí, thiết bị điện (Chương 84, 85)"),
    ("tt31:SXVII_SECTION", "XVII", "Phần XVII — Xe cộ, phương tiện bay, tàu thuyền (Chương 86–89)"),
]


def _classify_node_type(nid: str, rec: Dict[str, Any], md: Dict[str, Any]) -> str:
    if nid == "ROOT_CUSTOMS_TARIFF":
        return "root"
    if nid in {s[0] for s in SECTION_ROOT_IDS} or md.get("node_type") == "section":
        return "section"
    chunk_type = rec.get("chunk_type") or md.get("chunk_type")
    if chunk_type in {
        "section_note",
        "chapter_note",
        "subheading_note",
        "tariff_footnote",
        "gir_rule",
        "gir_explanation",
        "legal_clause",
        "technical_standard_item",
    } or rec.get("role") == "evidence" or "NOTE" in nid:
        return "note"
    level = rec.get("level") or md.get("level")
    if (
        level == 2
        or md.get("node_type") in {"chapter", "subchapter"}
        or ":CH:" in nid
        or "-CH-" in nid
        or "_CH_" in nid
        or ":SUBCH:" in nid
    ):
        return "chapter"
    if level == 4 or "HEADING4" in nid:
        return "heading"
    if level in (6, 8):
        return "subheading"
    if (rec.get("role") or md.get("role")) == "context" or "PDF_CTX" in nid:
        return "context"
    return "item"


def _build_node_label(nid: str, ntype: str, code: str, title_text: str) -> str:
    if ntype == "note":
        return "PL"
    clean_title = " ".join(str(title_text or "").split())
    if clean_title.startswith("-"):
        clean_title = clean_title.lstrip("- ").strip()
    short_title = clean_title[:48] + ("..." if len(clean_title) > 48 else "")

    if ntype in {"root", "section"}:
        return clean_title or nid
    if ntype == "chapter":
        if code:
            return f"Chương {code}" + (f": {short_title}" if short_title and not short_title.lower().startswith("chương") else "")
        return short_title or nid
    if code:
        return f"Mã {code}" + (f" — {short_title}" if short_title else "")
    return short_title or nid.replace("tt31:", "")


class UnifiedGraphService:
    """Manages graph querying across Authoritative In-Memory Corpus and Apache AGE."""

    def __init__(self, engine: Optional[str] = None) -> None:
        self.engine_mode = (
            engine
            or os.getenv("RAG_GRAPH_ENGINE")
            or os.getenv("GRAPH_ENGINE")
            or "apache_age"
        ).lower()
        self.age_adapter = ApacheAgeAdapter()

        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        self._alias_to_id: Dict[str, str] = {}
        self._children_index: Dict[str, List[str]] = defaultdict(list)
        self._parents_index: Dict[str, List[str]] = defaultdict(list)
        self._notes_index: Dict[str, List[str]] = defaultdict(list)
        self._graph_context: Optional[Any] = None
        self._loaded: bool = False

    def resolve_node_id(self, node_id: Optional[str]) -> Optional[str]:
        """Resolve either canonical (`tt31:SXVI-CH-84`) or short (`SXVI-CH-84`) node IDs."""
        if not node_id:
            return None
        self.load_inmemory_if_needed()
        if node_id in self._nodes:
            return node_id
        prefixed = f"tt31:{node_id}"
        if prefixed in self._nodes:
            return prefixed
        return self._alias_to_id.get(node_id)

    def load_inmemory_if_needed(self) -> None:
        """Load the authoritative `artifacts/corpus.json` graph bundle into memory."""
        if self._loaded:
            return

        logger.info("Loading authoritative customs knowledge graph from corpus.json...")
        bundle = _load_corpus_bundle()
        records_by_id: Dict[str, Dict[str, Any]] = {
            r["id"]: r for r in bundle["records"]
        }

        # 1. Register all 7,004 canonical nodes from bundle["nodes"]
        for n in bundle["nodes"]:
            nid = n["id"]
            md = n.get("metadata", {})
            rec = records_by_id.get(nid, {})

            code = str(
                rec.get("code")
                or first(md, "code", "code_compact", "hs.code_compact")
                or ""
            )
            section = (
                rec.get("section")
                or first(md, "section", "section_code")
                or ""
            )
            chapter = str(
                rec.get("chapter")
                or first(md, "chapter", "chapter_code")
                or (code[:2] if len(code) >= 2 and code[:2].isdigit() else "")
            )
            raw_desc = (
                rec.get("source_text")
                or first(
                    md,
                    "source_text",
                    "description_vi",
                    "label_vi",
                    "title_vi",
                    "text_vi",
                    "content.description_vi_normalized",
                    "content.legal_text_vi_normalized",
                )
                or ""
            )
            ntype = _classify_node_type(nid, rec, md)
            label = _build_node_label(nid, ntype, code, raw_desc)

            self._nodes[nid] = {
                "id": nid,
                "type": ntype,
                "label": label,
                "code": code,
                "section": section,
                "chapter": chapter,
                "level": rec.get("level") or md.get("level"),
                "description": " ".join(str(raw_desc).split()) or label,
            }

            # Register short aliases (without 'tt31:') for backward compatibility
            if nid.startswith("tt31:"):
                short_id = nid.split("tt31:", 1)[1]
                self._alias_to_id[short_id] = nid
            if code and code not in self._alias_to_id:
                self._alias_to_id[code] = nid

        # 2. Ensure Section root labels are friendly
        self._alias_to_id["SXIV_SECTION"] = "tt31:SEC:XIV"
        for sec_id, sec_code, sec_title in SECTION_ROOT_IDS:
            if sec_id in self._nodes:
                self._nodes[sec_id]["type"] = "section"
                self._nodes[sec_id]["label"] = sec_title
                self._nodes[sec_id]["section"] = sec_code
                self._nodes[sec_id]["description"] = sec_title
            else:
                self._nodes[sec_id] = {
                    "id": sec_id,
                    "type": "section",
                    "label": sec_title,
                    "code": sec_code,
                    "section": sec_code,
                    "chapter": "",
                    "level": 1,
                    "description": sec_title,
                }

        # 3. Register all 21,752 canonical edges from bundle["edges"]
        for e in bundle["edges"]:
            src = e["source"]
            tgt = e["target"]
            rel = e["relation"]
            if src not in self._nodes or tgt not in self._nodes:
                continue

            self._edges.append(
                {
                    "id": e.get("id", f"e_{len(self._edges)}"),
                    "source": src,
                    "target": tgt,
                    "relation": rel,
                    "metadata": e.get("metadata", {}),
                }
            )
            if rel == "CONTAINS":
                self._children_index[src].append(tgt)
                self._parents_index[tgt].append(src)
            elif rel in {
                "CONSTRAINED_BY",
                "HAS_LEGAL_NOTE",
                "GOVERNED_BY",
                "EXCLUDES_TO",
                "EXCLUDED_BY",
                "EXCLUDES_FROM_SCOPE_TO",
                "REFERENCES_CODE",
            }:
                self._notes_index[src].append(tgt)
            elif rel in {"APPLIES_TO", "APPLIES_WITHIN", "GOVERNS", "DEFINES_FOR"}:
                self._notes_index[tgt].append(src)

        # 4. Add top-level Tariff Root connecting the 3 Section roots
        root_id = "ROOT_CUSTOMS_TARIFF"
        self._nodes[root_id] = {
            "id": root_id,
            "type": "root",
            "label": "Biểu Thuế XNK Việt Nam (TT31/NĐ26)",
            "code": "VN-AHTN",
            "section": "ALL",
            "chapter": "",
            "level": 0,
            "description": (
                "Đồ thị tri thức Hải quan Việt Nam chuẩn hóa: 7.004 Đỉnh & 21.752 Cạnh "
                "(Phần XIV, XVI, XVII, Chú giải Pháp lý, GIR 1–6, Thông tư 85, Nghị định 26)"
            ),
        }
        for sec_id, _, _ in SECTION_ROOT_IDS:
            self._edges.append(
                {
                    "id": f"e_root_{sec_id}",
                    "source": root_id,
                    "target": sec_id,
                    "relation": "CONTAINS",
                    "metadata": {},
                }
            )
            self._children_index[root_id].append(sec_id)
            self._parents_index[sec_id].append(root_id)

        self._loaded = True
        logger.info(
            "Authoritative Graph loaded: %d nodes, %d edges.",
            len(self._nodes),
            len(self._edges),
        )

    def get_rag_graph_context(self, records: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Return a `GraphContext` instance for RAG Core, using Apache AGE if active or In-Memory fallback."""
        from rag.graph.context import GraphContext

        bundle = _load_corpus_bundle()
        if self.engine_mode == "apache_age" and self.age_adapter.check_availability():
            try:
                if records is None:
                    records = bundle["records"]
                nodes, edges = self.age_adapter.load_graph_nodes_and_edges()
                if nodes and edges:
                    return GraphContext(records, nodes, edges)
            except Exception as exc:
                logger.warning(
                    "Failed loading GraphContext from Apache AGE; using in-memory corpus: %s",
                    exc,
                )
        if self._graph_context is None:
            self._graph_context = GraphContext(
                records or bundle["records"], bundle["nodes"], bundle["edges"]
            )
        return self._graph_context

    def get_knowledge_graph(
        self,
        section: Optional[str] = None,
        chapter: Optional[str] = None,
        root_id: Optional[str] = None,
        query: Optional[str] = None,
        depth: int = 2,
        limit: int = 150,
    ) -> Dict[str, Any]:
        """Unified endpoint for Cytoscape.js visualization with Lazy-Loading & Dual-Run fallback."""
        resolved_root = self.resolve_node_id(root_id) if root_id else None

        # 1. Try Apache AGE if requested and available
        if self.engine_mode == "apache_age" and self.age_adapter.check_availability():
            try:
                return self.age_adapter.get_subgraph(
                    root_id=resolved_root or root_id,
                    chapter=chapter,
                    section=section,
                    query=query,
                    depth=depth,
                    limit=limit,
                )
            except Exception as exc:
                logger.warning(
                    "Apache AGE query failed; falling back to in-memory: %s", exc
                )

        # 2. Authoritative In-Memory Execution
        self.load_inmemory_if_needed()
        selected_node_ids: Set[str] = set()
        safe_limit = max(10, min(int(limit or 150), 500))
        safe_depth = max(1, min(int(depth or 2), 4))

        # Case A: Search by keyword or HS code
        if query and query.strip():
            q = query.strip().lower().replace(".", "")
            q_raw = query.strip().lower()
            for nid, n in self._nodes.items():
                code = str(n.get("code") or "").lower()
                label = str(n.get("label") or "").lower()
                desc = str(n.get("description") or "").lower()
                if (q and q in code) or q_raw in label or q_raw in desc:
                    selected_node_ids.add(nid)
                    # Include ancestors up to section root for clear hierarchy tree
                    curr = nid
                    for _ in range(4):
                        parents = self._parents_index.get(curr, [])
                        if not parents:
                            break
                        selected_node_ids.update(parents)
                        curr = parents[0]
                    # Include immediate children and governing notes
                    selected_node_ids.update(self._children_index.get(nid, [])[:8])
                    selected_node_ids.update(self._notes_index.get(nid, [])[:3])
                    if len(selected_node_ids) >= safe_limit:
                        break

        # Case B: Lazy-loading expansion of a clicked node
        elif resolved_root and resolved_root in self._nodes:
            selected_node_ids.add(resolved_root)
            current_level = {resolved_root}
            for _ in range(safe_depth):
                next_level: Set[str] = set()
                for parent in current_level:
                    children = self._children_index.get(parent, [])[:30]
                    notes = self._notes_index.get(parent, [])[:5]
                    next_level.update(children)
                    selected_node_ids.update(notes)
                selected_node_ids.update(next_level)
                current_level = next_level
                if len(selected_node_ids) >= safe_limit:
                    break

        # Case C: Overview (Root -> Sections -> Chapters -> Headings)
        else:
            top_root = "ROOT_CUSTOMS_TARIFF"
            selected_node_ids.add(top_root)
            sec_filter = None if not section or section == "all" else section.strip().upper()
            ch_filter = None if not chapter or chapter == "all" else str(chapter).strip()

            for sec_id, sec_code, _ in SECTION_ROOT_IDS:
                if sec_filter and sec_code != sec_filter:
                    continue
                selected_node_ids.add(sec_id)
                chapters = self._children_index.get(sec_id, [])
                for ch_id in chapters:
                    ch_node = self._nodes.get(ch_id, {})
                    ch_code = str(ch_node.get("chapter") or ch_node.get("code") or "")
                    if ch_filter and ch_filter != ch_code and ch_filter not in ch_id:
                        continue
                    selected_node_ids.add(ch_id)
                    # Include subchapters/headings under chapter
                    level1_children = self._children_index.get(ch_id, [])[:18]
                    selected_node_ids.update(level1_children)
                    # For Chapter 71 (which has Subchapters I, II, III), also include headings under subchapters
                    for sub_id in level1_children:
                        if ":SUBCH:" in sub_id:
                            selected_node_ids.update(
                                self._children_index.get(sub_id, [])[:10]
                            )
                    if len(selected_node_ids) >= safe_limit:
                        break

        # Format selected nodes for Cytoscape.js
        cy_nodes = []
        for nid in selected_node_ids:
            n = self._nodes.get(nid)
            if not n:
                continue
            children_cnt = len(self._children_index.get(nid, []))
            notes_cnt = len(self._notes_index.get(nid, []))
            cy_nodes.append(
                {
                    "data": {
                        "id": nid,
                        "label": n.get("label", nid),
                        "type": n.get("type", "item"),
                        "code": n.get("code", ""),
                        "section": n.get("section", ""),
                        "chapter": n.get("chapter", ""),
                        "description": n.get("description", ""),
                        "has_children": (children_cnt + notes_cnt) > 0,
                        "children_count": children_cnt,
                        "notes_count": notes_cnt,
                    }
                }
            )

        # Format edges connecting selected nodes (consolidating parallel edges)
        cy_edges = []
        seen_edge_pairs: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for e in self._edges:
            src = e["source"]
            tgt = e["target"]
            rel = e["relation"]
            if src in selected_node_ids and tgt in selected_node_ids:
                pair_key = (src, tgt)
                if pair_key not in seen_edge_pairs:
                    seen_edge_pairs[pair_key] = {
                        "data": {
                            "id": e["id"],
                            "source": src,
                            "target": tgt,
                            "label": rel,
                            "relation": rel,
                            "all_relations": [rel],
                        }
                    }
                else:
                    existing = seen_edge_pairs[pair_key]
                    if rel not in existing["data"]["all_relations"]:
                        existing["data"]["all_relations"].append(rel)
        cy_edges = list(seen_edge_pairs.values())

        active_engine = (
            "apache_age"
            if self.engine_mode == "apache_age" and self.age_adapter.check_availability()
            else "inmemory"
        )

        return {
            "success": True,
            "engine": active_engine,
            "elements": {
                "nodes": cy_nodes,
                "edges": cy_edges,
            },
            "stats": {
                "nodes_count": len(cy_nodes),
                "edges_count": len(cy_edges),
                "total_inmemory_nodes": len(self._nodes),
                "total_inmemory_edges": len(self._edges),
            },
        }


_graph_service_instance: Optional[UnifiedGraphService] = None


def get_graph_service() -> UnifiedGraphService:
    """Get or create singleton graph service."""
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = UnifiedGraphService()
    return _graph_service_instance


def get_rag_graph_context():
    """Return GraphContext backed by Apache AGE (when available) or In-Memory corpus."""
    return get_graph_service().get_rag_graph_context()
