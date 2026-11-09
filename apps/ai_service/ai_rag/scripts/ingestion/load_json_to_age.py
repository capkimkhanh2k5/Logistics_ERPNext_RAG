"""ETL Script: Export the authoritative `corpus.json` graph into Apache AGE openCypher SQL.

Loads `load_corpus()` (7,004 canonical nodes + 1 TariffRoot = 7,005 nodes and
21,752 canonical edges + 3 Root->Section edges = 21,755 edges) across:
- TT31 Sections XIV, XVI, XVII (Chapters 71, 84, 85, 86, 87, 88, 89)
- Derived HS6 nodes & PDF Context branches
- Legal documents: GIR 1-6, TT85, ND26, VBHN05, TT02.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rag.graph.age_adapter import escape_cypher
from rag.graph.service import UnifiedGraphService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_json_to_age")

SQL_OUT = BASE_DIR / "sql" / "003_customs_graph_age_data.sql"

_CYPHER_LABEL_MAP = {
    "root": "TariffRoot",
    "section": "Section",
    "chapter": "Chapter",
    "heading": "Heading",
    "subheading": "Subheading",
    "note": "LegalNote",
    "context": "BranchContext",
    "item": "TariffNode",
}


def sanitize_cypher_identifier(raw: str) -> str:
    """Ensure vertex/edge labels are valid openCypher identifiers."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", str(raw or "RELATED_TO"))
    if not cleaned or cleaned[0].isdigit():
        cleaned = "REL_" + cleaned
    return cleaned


def generate_cypher_statements() -> List[str]:
    svc = UnifiedGraphService(engine="inmemory")
    svc.load_inmemory_if_needed()

    statements: List[str] = []

    logger.info("Generating vertex statements for %d canonical nodes...", len(svc._nodes))
    for nid, n in svc._nodes.items():
        v_label = _CYPHER_LABEL_MAP.get(n.get("type", "item"), "TariffNode")
        safe_id = escape_cypher(nid)
        safe_label = escape_cypher(n.get("label", nid))
        safe_type = escape_cypher(n.get("type", "item"))
        safe_code = escape_cypher(n.get("code", ""))
        safe_sec = escape_cypher(n.get("section", ""))
        safe_ch = escape_cypher(n.get("chapter", ""))
        safe_desc = escape_cypher(str(n.get("description", ""))[:300])
        children_cnt = len(svc._children_index.get(nid, []))
        notes_cnt = len(svc._notes_index.get(nid, []))
        has_children = "true" if (children_cnt + notes_cnt) > 0 else "false"

        statements.append(
            f"SELECT * FROM cypher('customs_tariff_graph', $$ "
            f"CREATE (:{v_label} {{id: '{safe_id}', type: '{safe_type}', label: '{safe_label}', "
            f"code: '{safe_code}', section: '{safe_sec}', chapter: '{safe_ch}', "
            f"description: '{safe_desc}', has_children: {has_children}, children_count: {children_cnt}}}) "
            f"$$) AS (v agtype);"
        )

    logger.info("Generating edge statements for %d canonical edges...", len(svc._edges))
    for e in svc._edges:
        safe_src = escape_cypher(e["source"])
        safe_tgt = escape_cypher(e["target"])
        safe_eid = escape_cypher(e["id"])
        rel_ident = sanitize_cypher_identifier(e["relation"]).upper()
        statements.append(
            f"SELECT * FROM cypher('customs_tariff_graph', $$ "
            f"MATCH (a {{id: '{safe_src}'}}), (b {{id: '{safe_tgt}'}}) "
            f"CREATE (a)-[:{rel_ident} {{id: '{safe_eid}', relation: '{rel_ident}'}}]->(b) "
            f"$$) AS (e agtype);"
        )

    logger.info(
        "Prepared %d nodes and %d edges (%d total statements).",
        len(svc._nodes),
        len(svc._edges),
        len(statements),
    )
    return statements


def main() -> None:
    logger.info("Generating authoritative Apache AGE Cypher SQL from corpus.json...")
    statements = generate_cypher_statements()

    SQL_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("-- ====================================================================\n")
        f.write("-- Authoritative Apache AGE Migration from corpus.json (7,005 Nodes & 21,755 Edges)\n")
        f.write("-- ====================================================================\n")
        f.write("LOAD 'age';\n")
        f.write("SET search_path = ag_catalog, '$user', public;\n\n")
        f.write("BEGIN;\n")
        for stmt in statements:
            f.write(stmt + "\n")
        f.write("COMMIT;\n")

    logger.info(
        "Exported authoritative graph data to %s (%.2f MB)",
        SQL_OUT,
        SQL_OUT.stat().st_size / (1024 * 1024),
    )


if __name__ == "__main__":
    main()
