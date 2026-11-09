"""Unified Graph Service with Dual-Engine Architecture.

Supports:
- In-Memory JSON catalog (original baseline, zero dependencies)
- Apache AGE (openCypher on PostgreSQL 17)
- Dynamic fallback & Lazy loading for Cytoscape.js visualization.
"""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from rag.graph.age_adapter import ApacheAgeAdapter

logger = logging.getLogger("rag.graph.service")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "normalized" / "TT31"


class UnifiedGraphService:
    """Manages graph querying across In-Memory (JSON) and Apache AGE (PostgreSQL)."""

    def __init__(self, engine: Optional[str] = None) -> None:
        self.engine_mode = (
            engine or os.getenv("GRAPH_ENGINE", "inmemory")
        ).lower()
        self.age_adapter = ApacheAgeAdapter()

        # In-memory cached structures
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        self._children_index: Dict[str, List[str]] = defaultdict(list)
        self._parents_index: Dict[str, List[str]] = defaultdict(list)
        self._loaded: bool = False

    def load_inmemory_if_needed(self) -> None:
        """Load JSON/JSONL graph data into memory on demand."""
        if self._loaded:
            return

        logger.info("Loading in-memory customs knowledge graph...")

        # 1. Load structural nodes from Section XVI
        sec_xvi_nodes = DATA_DIR / "Section-XVI" / "SECTION_XVI_GRAPH_STRUCTURAL_NODES.jsonl"
        if sec_xvi_nodes.exists():
            with open(sec_xvi_nodes, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    nid = item.get("node_id")
                    if nid:
                        self._nodes[nid] = {
                            "id": nid,
                            "type": item.get("node_type", "section"),
                            "label": item.get("label_vi") or nid,
                            "section": item.get("section"),
                            "chapter": item.get("chapter"),
                            "description": item.get("label_vi", ""),
                        }

        # 2. Load Section XIV nodes
        sec_xiv_nodes = DATA_DIR / "Section-XIV" / "SECTION_XIV_GRAPH_NODES.jsonl"
        if sec_xiv_nodes.exists():
            with open(sec_xiv_nodes, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    nid = item.get("node_id")
                    if nid:
                        self._nodes[nid] = {
                            "id": nid,
                            "type": item.get("node_type", "item"),
                            "label": item.get("code") or item.get("label") or nid,
                            "section": item.get("section", "XIV"),
                            "chapter": item.get("chapter"),
                            "code": item.get("code"),
                            "description": item.get("description_vi") or item.get("policy", ""),
                        }

        # 3. Load Section XVI edges
        sec_xvi_edges = DATA_DIR / "Section-XVI" / "SECTION_XVI_GRAPH_EDGES.jsonl"
        if sec_xvi_edges.exists():
            with open(sec_xvi_edges, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    src = item.get("source_id")
                    tgt = item.get("target_id")
                    rel = item.get("relation", "CONTAINS")
                    if src and tgt:
                        self._edges.append(
                            {
                                "id": item.get("edge_id", f"e_{len(self._edges)}"),
                                "source": src,
                                "target": tgt,
                                "relation": rel,
                                "metadata": item.get("metadata", {}),
                            }
                        )
                        self._children_index[src].append(tgt)
                        self._parents_index[tgt].append(src)

                        # Auto-register leaf target nodes if not yet in _nodes
                        if tgt not in self._nodes:
                            label = tgt
                            code = tgt.split("-")[-1] if "-" in tgt else tgt
                            if code.startswith("T"):
                                code = code[1:]
                            self._nodes[tgt] = {
                                "id": tgt,
                                "type": "subheading" if len(code) >= 6 else "heading",
                                "label": f"Mã {code}" if code.isdigit() else label,
                                "code": code,
                                "section": "XVI",
                                "chapter": code[:2] if len(code) >= 2 else None,
                                "description": f"Dòng thuế / Nhánh {code}",
                            }

        # 4. Load Section XIV edges
        sec_xiv_edges = DATA_DIR / "Section-XIV" / "SECTION_XIV_GRAPH_EDGES.jsonl"
        if sec_xiv_edges.exists():
            with open(sec_xiv_edges, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    src = item.get("source") or item.get("source_id")
                    tgt = item.get("target") or item.get("target_id")
                    rel = item.get("relation", "CONTAINS")
                    if src and tgt:
                        self._edges.append(
                            {
                                "id": item.get("edge_id", f"e_{len(self._edges)}"),
                                "source": src,
                                "target": tgt,
                                "relation": rel,
                                "metadata": item.get("metadata", {}),
                            }
                        )
                        self._children_index[src].append(tgt)
                        self._parents_index[tgt].append(src)

        # 5. Load Section XVII structural & edges
        sec_xvii_edges = DATA_DIR / "Section-XVII" / "SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl"
        if sec_xvii_edges.exists():
            with open(sec_xvii_edges, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    src = item.get("from_id")
                    tgt = item.get("to_id")
                    rel = item.get("relation", "CONTAINS")
                    if src and tgt:
                        self._edges.append(
                            {
                                "id": item.get("id", f"e_{len(self._edges)}"),
                                "source": src,
                                "target": tgt,
                                "relation": rel,
                                "metadata": item,
                            }
                        )
                        self._children_index[src].append(tgt)
                        self._parents_index[tgt].append(src)

        # 6. Enrich nodes with Vietnamese descriptions from Master files
        for sec_code, path in [
            ("XIV", DATA_DIR / "Section-XIV" / "SECTION_XIV_MASTER_NORMALIZED.jsonl"),
            ("XVI", DATA_DIR / "Section-XVI" / "SECTION_XVI_MASTER_NORMALIZED.jsonl"),
            ("XVII", DATA_DIR / "Section-XVII" / "SECTION_XVII_MASTER_NORMALIZED.jsonl"),
        ]:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        d = json.loads(line)
                        nid = d.get("record_id") or d.get("code")
                        if not nid:
                            continue
                        code = d.get("code", "")
                        level = d.get("level", 4)
                        title = d.get("title_vi") or d.get("text_vi", "")[:60]
                        desc = d.get("text_vi") or d.get("source_text_vi", "")

                        self._nodes[nid] = {
                            "id": nid,
                            "type": "chapter" if level == 2 else ("heading" if level == 4 else "subheading"),
                            "label": title or f"Mã {code}",
                            "code": code,
                            "section": sec_code,
                            "chapter": d.get("chapter"),
                            "description": desc,
                        }

        # 7. Add Root Node and connect all Section nodes
        root_id = "ROOT_CUSTOMS_TARIFF"
        if root_id not in self._nodes:
            self._nodes[root_id] = {
                "id": root_id,
                "type": "root",
                "label": "Biểu Thuế XNK Việt Nam",
                "section": "ALL",
                "chapter": None,
                "description": "Danh mục biểu thuế và chú giải pháp lý hải quan (Thông tư 31/2022/TT-BTC)",
            }
            # Connect Root to all Sections (XIV, XVI, XVII)
            for sec_id, sec_label in [
                ("SXIV_SECTION", "Phần XIV (Đá quý, kim loại quý)"),
                ("SXVI-S-XVI", "Phần XVI (Máy móc, thiết bị điện)"),
                ("SXVII_SECTION", "Phần XVII (Phương tiện vận tải)"),
            ]:
                if sec_id not in self._nodes:
                    self._nodes[sec_id] = {
                        "id": sec_id,
                        "type": "section",
                        "label": sec_label,
                        "section": sec_id.replace("S", "").replace("_SECTION", ""),
                        "chapter": None,
                        "description": sec_label,
                    }
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
            "Graph loaded: %d nodes, %d edges.", len(self._nodes), len(self._edges)
        )

    def get_knowledge_graph(
        self,
        section: Optional[str] = None,
        chapter: Optional[str] = None,
        root_id: Optional[str] = None,
        query: Optional[str] = None,
        depth: int = 2,
        limit: int = 150,
    ) -> Dict[str, Any]:
        """Unified endpoint for Cytoscape.js rendering.

        Attempts Apache AGE if configured; gracefully falls back to In-Memory.
        """
        # 1. Try Apache AGE if requested
        if self.engine_mode == "apache_age":
            if self.age_adapter.check_availability():
                try:
                    return self.age_adapter.get_subgraph(
                        root_id=root_id,
                        chapter=chapter,
                        section=section,
                        depth=depth,
                        limit=limit,
                    )
                except Exception as exc:
                    logger.warning(
                        "Apache AGE query failed; falling back to in-memory: %s", exc
                    )

        # 2. In-memory baseline execution
        self.load_inmemory_if_needed()

        selected_node_ids: Set[str] = set()

        # If user searches by keyword / code
        if query and query.strip():
            q = query.strip().lower()
            for nid, n in self._nodes.items():
                code = str(n.get("code") or "").lower()
                label = str(n.get("label") or "").lower()
                desc = str(n.get("description") or "").lower()
                if q in code or q in label or q in desc:
                    selected_node_ids.add(nid)
                    # Include immediate parents and children for context
                    selected_node_ids.update(self._parents_index.get(nid, []))
                    selected_node_ids.update(self._children_index.get(nid, [])[:10])
                    if len(selected_node_ids) >= limit:
                        break

        # If user expands a specific node (Lazy Loading)
        elif root_id and root_id in self._nodes:
            selected_node_ids.add(root_id)
            # Expand BFS up to requested depth
            current_level = {root_id}
            for _ in range(depth):
                next_level = set()
                for parent in current_level:
                    children = self._children_index.get(parent, [])[:25]
                    next_level.update(children)
                selected_node_ids.update(next_level)
                current_level = next_level
                if len(selected_node_ids) >= limit:
                    break

        # Default overview: Root -> Sections -> Chapters -> Top Headings
        else:
            # Start from ROOT
            root_id = "ROOT_CUSTOMS_TARIFF"
            selected_node_ids.add(root_id)
            sections = self._children_index.get(root_id, [])
            selected_node_ids.update(sections)

            for sec in sections:
                if section and section not in sec:
                    continue
                chapters = self._children_index.get(sec, [])
                for ch in chapters:
                    if chapter and chapter not in ch:
                        continue
                    selected_node_ids.add(ch)
                    # Add top headings of this chapter (depth=2)
                    headings = self._children_index.get(ch, [])[:15]
                    selected_node_ids.update(headings)
                    if len(selected_node_ids) >= limit:
                        break

        # Format nodes for Cytoscape.js
        cy_nodes = []
        for nid in selected_node_ids:
            if nid in self._nodes:
                n = self._nodes[nid]
                has_children = len(self._children_index.get(nid, [])) > 0
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
                            "has_children": has_children,
                            "children_count": len(self._children_index.get(nid, [])),
                        }
                    }
                )

        # Format edges connecting the selected nodes
        cy_edges = []
        for e in self._edges:
            if e["source"] in selected_node_ids and e["target"] in selected_node_ids:
                cy_edges.append(
                    {
                        "data": {
                            "id": e["id"],
                            "source": e["source"],
                            "target": e["target"],
                            "label": e["relation"],
                            "relation": e["relation"],
                        }
                    }
                )

        active_engine = "apache_age" if self.engine_mode == "apache_age" and self.age_adapter.check_availability() else "inmemory"

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


# Global singleton instance for high performance
_graph_service_instance: Optional[UnifiedGraphService] = None


def get_graph_service() -> UnifiedGraphService:
    """Get or create singleton graph service."""
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = UnifiedGraphService()
    return _graph_service_instance
