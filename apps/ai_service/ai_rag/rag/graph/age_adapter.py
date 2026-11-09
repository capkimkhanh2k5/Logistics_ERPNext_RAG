"""Apache AGE Graph Database Adapter for PostgreSQL.

Provides:
1. High-level openCypher querying for the Customs Tariff & Legal Knowledge Graph.
2. Proper `agtype` vertex/edge/path deserialization for psycopg3.
3. Direct compatibility with `GraphContext` in `rag/graph/context.py` so RAG Core
   can switch seamlessly between In-Memory JSON and Apache AGE.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("rag.graph.age_adapter")

GRAPH_NAME = os.getenv("AGE_GRAPH_NAME", "customs_tariff_graph")
_AGTYPE_SUFFIX_RE = re.compile(r"::(?:vertex|edge|path|numeric)\s*$")


def parse_agtype(value: Any) -> Any:
    """Deserialize an Apache AGE `agtype` value returned by psycopg into a Python object."""
    if value is None:
        return None
    if isinstance(value, (dict, list, int, float, bool)):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    cleaned = _AGTYPE_SUFFIX_RE.sub("", raw).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return cleaned


def escape_cypher(value: Any) -> str:
    """Safely escape a string literal for openCypher queries."""
    if value is None:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", "")
    )


def _default_dsn() -> str:
    if os.getenv("RAG_DATABASE_URL"):
        return os.environ["RAG_DATABASE_URL"]
    if os.getenv("RAG_DB_USER") and os.getenv("RAG_DB_PASSWORD"):
        user = os.environ["RAG_DB_USER"]
        pw = os.environ["RAG_DB_PASSWORD"]
        host = os.getenv("RAG_DB_HOST", "localhost")
        port = os.getenv("RAG_DB_PORT", "55432")
        dbname = os.getenv("RAG_DB_NAME", "hs_rag")
        return f"postgresql://{user}:{pw}@{host}:{port}/{dbname}"
    try:
        from config.settings import DatabaseConfig

        cfg = DatabaseConfig.from_env()
        return f"postgresql://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.dbname}"
    except Exception:
        return "postgresql://postgres:admin@localhost:55432/postgres"


from contextlib import contextmanager


@contextmanager
def _pg_connect(dsn: str, connect_timeout: int = 2):
    """Connect using either psycopg (v3) or psycopg2 (v2) and ensure cleanup."""
    conn = None
    try:
        try:
            import psycopg

            conn = psycopg.connect(dsn, connect_timeout=connect_timeout)
        except ImportError:
            import psycopg2

            conn = psycopg2.connect(dsn, connect_timeout=connect_timeout)
        yield conn
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


class ApacheAgeAdapter:
    """Interface to Apache AGE graph queries on PostgreSQL."""

    def __init__(
        self,
        db_url: Optional[str] = None,
        graph_name: str = GRAPH_NAME,
    ) -> None:
        self.db_url = db_url or _default_dsn()
        self.graph_name = graph_name
        self._is_available: Optional[bool] = None

    def check_availability(self) -> bool:
        """Check if PostgreSQL has Apache AGE extension loaded and graph populated."""
        if self._is_available is not None:
            return self._is_available

        try:
            with _pg_connect(self.db_url, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM pg_extension WHERE extname = 'age'"
                    )
                    if not cur.fetchone():
                        self._is_available = False
                        return False

                    cur.execute(
                        "SELECT 1 FROM ag_catalog.ag_graph WHERE name = %s",
                        (self.graph_name,),
                    )
                    if not cur.fetchone():
                        self._is_available = False
                        return False

                    cur.execute("LOAD 'age';")
                    cur.execute("SET search_path = ag_catalog, '$user', public;")
                    cur.execute(
                        f"SELECT * FROM cypher('{self.graph_name}', $$ MATCH (n) RETURN n LIMIT 1 $$) AS (n agtype);"
                    )
                    self._is_available = cur.fetchone() is not None
                    return bool(self._is_available)
        except Exception as exc:
            logger.debug("Apache AGE availability check failed: %s", exc)
            self._is_available = False
            return False

    def query_cypher(self, cypher_query: str, return_types: str) -> List[Tuple[Any, ...]]:
        """Execute an openCypher query via `ag_catalog.cypher()` and parse `agtype` columns."""
        if not self.check_availability():
            raise RuntimeError(
                f"Apache AGE is not available on database {self.db_url}"
            )

        with _pg_connect(self.db_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("LOAD 'age';")
                cur.execute("SET search_path = ag_catalog, '$user', public;")
                sql = (
                    f"SELECT * FROM cypher('{self.graph_name}', $$\n"
                    f"    {cypher_query}\n"
                    f"$$) AS ({return_types});"
                )
                cur.execute(sql)
                raw_rows = cur.fetchall()
                return [tuple(parse_agtype(col) for col in row) for row in raw_rows]

    def get_ancestors_cypher(self, node_id: str, max_depth: int = 12) -> List[str]:
        """Traverse incoming CONTAINS edges in Apache AGE to find ancestors ordered furthest-first."""
        safe_id = escape_cypher(node_id)
        depth = max(1, min(int(max_depth), 12))
        cypher = f"""
            MATCH path = (ancestor)-[:CONTAINS*1..{depth}]->(target {{id: '{safe_id}'}})
            RETURN ancestor, length(path) AS dist
        """
        rows = self.query_cypher(cypher, "ancestor agtype, dist agtype")
        distance: Dict[str, int] = {}
        for ancestor_obj, dist_val in rows:
            if not isinstance(ancestor_obj, dict):
                continue
            props = ancestor_obj.get("properties", ancestor_obj)
            aid = props.get("id")
            if not aid or aid == node_id:
                continue
            d = int(dist_val) if dist_val is not None else 1
            if aid not in distance or d < distance[aid]:
                distance[aid] = d
        return sorted(distance, key=lambda n: (-distance[n], n))

    def load_graph_nodes_and_edges(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load all nodes and edges from Apache AGE in the exact format required by `GraphContext`."""
        node_rows = self.query_cypher("MATCH (n) RETURN n", "n agtype")
        nodes: List[Dict[str, Any]] = []
        for (n_obj,) in node_rows:
            if not isinstance(n_obj, dict):
                continue
            props = n_obj.get("properties", n_obj)
            nid = props.get("id")
            if nid:
                md = props.get("metadata")
                if isinstance(md, str):
                    try:
                        md = json.loads(md)
                    except Exception:
                        md = props
                elif not isinstance(md, dict):
                    md = props
                nodes.append({"id": nid, "metadata": md})

        edge_rows = self.query_cypher(
            "MATCH (a)-[r]->(b) RETURN a.id, b.id, label(r), r",
            "src agtype, tgt agtype, rel agtype, r agtype",
        )
        edges: List[Dict[str, Any]] = []
        for src, tgt, rel, r_obj in edge_rows:
            if not src or not tgt:
                continue
            props = r_obj.get("properties", {}) if isinstance(r_obj, dict) else {}
            edges.append(
                {
                    "id": props.get("id", f"AGE_EDGE:{src}:{rel}:{tgt}"),
                    "source": str(src),
                    "target": str(tgt),
                    "relation": str(rel or props.get("relation", "CONTAINS")),
                    "metadata": props,
                }
            )
        return nodes, edges

    def get_subgraph(
        self,
        root_id: Optional[str] = None,
        chapter: Optional[str] = None,
        section: Optional[str] = None,
        query: Optional[str] = None,
        depth: int = 2,
        limit: int = 150,
    ) -> Dict[str, Any]:
        """Retrieve subgraph nodes and edges formatted for Cytoscape.js."""
        if not self.check_availability():
            raise RuntimeError("Apache AGE is not reachable.")

        safe_limit = max(1, min(int(limit), 500))
        safe_depth = max(1, min(int(depth), 4))

        if root_id:
            safe_root = escape_cypher(root_id)
            cypher = f"""
                MATCH (n {{id: '{safe_root}'}})-[r]->(m)
                RETURN n, r, m
                LIMIT {safe_limit}
            """
        elif query and query.strip():
            q = escape_cypher(query.strip().lower())
            cypher = f"""
                MATCH (n)
                WHERE toLower(n.code) CONTAINS '{q}'
                   OR toLower(n.label) CONTAINS '{q}'
                   OR toLower(n.description) CONTAINS '{q}'
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT {safe_limit}
            """
        else:
            if chapter and chapter != "all":
                top_types = "['root', 'section', 'chapter', 'subchapter', 'heading']"
                safe_ch = escape_cypher(chapter)
                cypher = f"""
                    MATCH (n)-[r]->(m)
                    WHERE (n.chapter = '{safe_ch}' OR m.chapter = '{safe_ch}')
                      AND n.type IN {top_types}
                      AND m.type IN {top_types}
                    RETURN n, r, m
                    LIMIT {safe_limit}
                """
            elif section and section != "all":
                top_types = "['root', 'section', 'chapter', 'subchapter', 'heading']"
                safe_sec = escape_cypher(section)
                cypher = f"""
                    MATCH (n)-[r]->(m)
                    WHERE (n.section = '{safe_sec}' OR m.section = '{safe_sec}')
                      AND n.type IN {top_types}
                      AND m.type IN {top_types}
                    RETURN n, r, m
                    LIMIT {safe_limit}
                """
            else:
                # Progressive Disclosure: High-level overview (Root -> Sections -> Chapters)
                overview_types = "['root', 'section', 'chapter']"
                cypher = f"""
                    MATCH (n)-[r]->(m)
                    WHERE n.type IN {overview_types}
                      AND m.type IN {overview_types}
                    RETURN n, r, m
                    LIMIT 50
                """

        rows = self.query_cypher(cypher, "n agtype, r agtype, m agtype")
        nodes_map: Dict[str, Dict[str, Any]] = {}
        edges_list: List[Dict[str, Any]] = []

        for n_raw, r_raw, m_raw in rows:
            n_props = n_raw.get("properties", n_raw) if isinstance(n_raw, dict) else None
            m_props = m_raw.get("properties", m_raw) if isinstance(m_raw, dict) else None

            if isinstance(n_props, dict):
                nid = str(n_props.get("id") or n_props.get("node_id") or "")
                if nid and nid not in nodes_map:
                    nodes_map[nid] = self._format_cytoscape_node(n_props)

            if isinstance(m_props, dict):
                mid = str(m_props.get("id") or m_props.get("node_id") or "")
                if mid and mid not in nodes_map:
                    nodes_map[mid] = self._format_cytoscape_node(m_props)

            if isinstance(r_raw, dict) and isinstance(n_props, dict) and isinstance(m_props, dict):
                r_props = r_raw.get("properties", {})
                rel_label = r_raw.get("label") or r_props.get("relation") or "CONTAINS"
                src_id = str(n_props.get("id") or n_props.get("node_id") or "")
                tgt_id = str(m_props.get("id") or m_props.get("node_id") or "")
                if src_id and tgt_id:
                    edges_list.append(
                        {
                            "data": {
                                "id": r_props.get("id") or f"e_{len(edges_list)}",
                                "source": src_id,
                                "target": tgt_id,
                                "label": rel_label,
                                "relation": rel_label,
                            }
                        }
                    )

        return {
            "success": True,
            "engine": "apache_age",
            "elements": {
                "nodes": list(nodes_map.values()),
                "edges": edges_list,
            },
            "stats": {
                "nodes_count": len(nodes_map),
                "edges_count": len(edges_list),
            },
        }

    def _format_cytoscape_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        node_id = str(node_data.get("id") or node_data.get("node_id") or "")
        node_type = str(node_data.get("type") or node_data.get("node_type") or node_data.get("role") or "item").lower()
        raw_label = (
            node_data.get("label")
            or node_data.get("label_vi")
            or node_data.get("code")
            or str(node_data.get("source_text", ""))[:60]
            or node_id
        )
        code = str(node_data.get("code") or "")

        # Format concise, legible label for the node badge
        short_label = raw_label
        if node_type == "root":
            short_label = "Biểu Thuế XNK"
        elif node_type == "section":
            sec = str(node_data.get("section") or code or "").replace("SEC:", "").replace("tt31:SEC:", "").replace("S", "")
            short_label = f"Phần {sec}" if sec else "Phần HS"
        elif node_type == "chapter":
            ch = str(node_data.get("chapter") or code or "").replace("CH:", "").replace("CH_", "").replace("tt31:CH:", "")
            short_label = f"Chương {ch}" if ch else "Chương"
        elif node_type == "heading":
            short_label = f"Mã {code}" if code else raw_label[:14]
        elif node_type == "subheading":
            short_label = code if code else raw_label[:14]
        elif node_type in ("legal", "note", "legal_note"):
            short_label = f"Chú giải {code}" if code else "Chú giải PL"

        return {
            "data": {
                "id": node_id,
                "label": short_label,
                "full_title": raw_label,
                "type": node_type,
                "code": code,
                "section": node_data.get("section", ""),
                "chapter": node_data.get("chapter", ""),
                "description": node_data.get("description")
                or node_data.get("description_vi")
                or node_data.get("source_text", "")
                or raw_label,
                "has_children": bool(node_data.get("has_children", True)),
                "children_count": int(node_data.get("children_count", 0)),
            }
        }
