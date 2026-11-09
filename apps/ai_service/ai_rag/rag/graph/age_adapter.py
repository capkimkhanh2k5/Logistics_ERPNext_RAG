"""Apache AGE Graph Database Adapter for PostgreSQL.

Provides high-level Cypher querying for customs tariff graph (Nodes & Edges),
bridging openCypher with Python data structures, with graceful fallback.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("rag.graph.age_adapter")

GRAPH_NAME = os.getenv("AGE_GRAPH_NAME", "customs_tariff_graph")


class ApacheAgeAdapter:
    """Interface to Apache AGE graph queries on PostgreSQL."""

    def __init__(
        self,
        db_url: Optional[str] = None,
        graph_name: str = GRAPH_NAME,
    ) -> None:
        self.db_url = db_url or os.getenv(
            "RAG_DATABASE_URL",
            "postgresql://postgres:admin@localhost:55432/postgres",
        )
        self.graph_name = graph_name
        self._is_available: Optional[bool] = None

    def check_availability(self) -> bool:
        """Check if PostgreSQL has Apache AGE extension loaded and graph initialized."""
        if self._is_available is not None:
            return self._is_available

        try:
            import psycopg

            with psycopg.connect(self.db_url, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM pg_extension WHERE extname = 'age'"
                    )
                    row = cur.fetchone()
                    if not row:
                        self._is_available = False
                        return False

                    # Check if the graph exists in ag_catalog
                    cur.execute(
                        "SELECT 1 FROM ag_catalog.ag_graph WHERE name = %s",
                        (self.graph_name,),
                    )
                    self._is_available = cur.fetchone() is not None
                    return bool(self._is_available)
        except Exception as exc:
            logger.debug("Apache AGE availability check failed: %s", exc)
            self._is_available = False
            return False

    def query_cypher(self, cypher_query: str, return_types: str) -> List[Any]:
        """Execute a raw openCypher query using AGE SELECT cypher().

        Example:
            adapter.query_cypher(
                "MATCH (n:Chapter) RETURN n",
                "n agtype"
            )
        """
        if not self.check_availability():
            raise RuntimeError(
                f"Apache AGE is not available on database {self.db_url}"
            )

        import psycopg

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("LOAD 'age';")
                cur.execute("SET search_path = ag_catalog, '$user', public;")
                sql = f"""
                    SELECT * FROM cypher('{self.graph_name}', $$
                        {cypher_query}
                    $$) as ({return_types});
                """
                cur.execute(sql)
                return cur.fetchall()

    def get_subgraph(
        self,
        root_id: Optional[str] = None,
        chapter: Optional[str] = None,
        section: Optional[str] = None,
        depth: int = 2,
        limit: int = 200,
    ) -> Dict[str, Any]:
        """Retrieve nodes and edges for Cytoscape.js rendering.

        Returns:
            Dict with 'nodes' and 'edges' formatted for Cytoscape.js.
        """
        if not self.check_availability():
            raise RuntimeError("Apache AGE is not reachable.")

        cypher = f"""
            MATCH (n)
            WHERE ('{chapter or ""}' = '' OR n.chapter = '{chapter}')
              AND ('{section or ""}' = '' OR n.section = '{section}')
            OPTIONAL MATCH (n)-[r:CONTAINS|EXCLUDES|REFERENCES_CODE]->(m)
            RETURN n, r, m
            LIMIT {limit}
        """
        rows = self.query_cypher(cypher, "n agtype, r agtype, m agtype")
        nodes_map: Dict[str, Dict[str, Any]] = {}
        edges_list: List[Dict[str, Any]] = []

        for row in rows:
            n_raw, r_raw, m_raw = row
            if n_raw:
                nid = str(n_raw.get("id", n_raw.get("node_id", "")))
                if nid and nid not in nodes_map:
                    nodes_map[nid] = self._format_cytoscape_node(n_raw)
            if m_raw:
                mid = str(m_raw.get("id", m_raw.get("node_id", "")))
                if mid and mid not in nodes_map:
                    nodes_map[mid] = self._format_cytoscape_node(m_raw)
            if r_raw and n_raw and m_raw:
                edges_list.append(
                    {
                        "data": {
                            "id": f"e_{len(edges_list)}",
                            "source": str(n_raw.get("id", n_raw.get("node_id"))),
                            "target": str(m_raw.get("id", m_raw.get("node_id"))),
                            "label": r_raw.get("label", "RELATED_TO"),
                            "relation": r_raw.get("label", "RELATED_TO"),
                        }
                    }
                )

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list,
            "engine": "apache_age",
            "stats": {"nodes_count": len(nodes_map), "edges_count": len(edges_list)},
        }

    def _format_cytoscape_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        node_id = str(node_data.get("id") or node_data.get("node_id") or "")
        node_type = node_data.get("node_type") or node_data.get("role") or "item"
        label = (
            node_data.get("label_vi")
            or node_data.get("code")
            or node_data.get("source_text", "")[:35]
            or node_id
        )
        return {
            "data": {
                "id": node_id,
                "label": label,
                "type": node_type,
                "code": node_data.get("code", ""),
                "section": node_data.get("section", ""),
                "chapter": node_data.get("chapter", ""),
                "description": node_data.get("description_vi")
                or node_data.get("source_text", ""),
                "raw": node_data,
            }
        }
