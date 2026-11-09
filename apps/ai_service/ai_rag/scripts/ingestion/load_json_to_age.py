"""ETL Script: Convert normalized customs JSONL into Apache AGE Cypher statements.

Exports or loads into PostgreSQL Apache AGE:
- Nodes: Section, Chapter, Heading, Subheading, LegalNote
- Edges: CONTAINS, EXCLUDES, REFERENCES, CONSTRAINED_BY
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_json_to_age")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "normalized" / "TT31"
SQL_OUT = BASE_DIR / "sql" / "003_customs_graph_age_data.sql"


def escape_cypher_str(val: str) -> str:
    """Escape string for openCypher literals."""
    if val is None:
        return ""
    return str(val).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ")


def generate_cypher() -> List[str]:
    statements: List[str] = []

    # 1. Initialize AGE graph
    statements.append("SELECT * FROM cypher('customs_tariff_graph', $$ CREATE (:TariffRoot {id: 'ROOT_CUSTOMS_TARIFF', name: 'Biểu Thuế XNK Việt Nam'}) $$) as (v agtype);")

    # 2. Section XVI Nodes
    sec_xvi_nodes = DATA_DIR / "Section-XVI" / "SECTION_XVI_GRAPH_STRUCTURAL_NODES.jsonl"
    if sec_xvi_nodes.exists():
        with open(sec_xvi_nodes, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                nid = escape_cypher_str(d.get("node_id"))
                label = escape_cypher_str(d.get("label_vi"))
                ntype = d.get("node_type", "Section").capitalize()
                cy = f"SELECT * FROM cypher('customs_tariff_graph', $$ CREATE (:{ntype} {{id: '{nid}', label: '{label}', section: '{d.get('section', '')}', chapter: '{d.get('chapter', '')}'}}) $$) as (v agtype);"
                statements.append(cy)

    # 3. Section XVI Edges
    sec_xvi_edges = DATA_DIR / "Section-XVI" / "SECTION_XVI_GRAPH_EDGES.jsonl"
    if sec_xvi_edges.exists():
        with open(sec_xvi_edges, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                src = escape_cypher_str(d.get("source_id"))
                tgt = escape_cypher_str(d.get("target_id"))
                rel = d.get("relation", "CONTAINS").upper()
                cy = f"""SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {{id: '{src}'}}), (b {{id: '{tgt}'}})
                    CREATE (a)-[:{rel}]->(b)
                $$) as (e agtype);"""
                statements.append(cy)

    return statements


def main() -> None:
    logger.info("Generating Apache AGE SQL / Cypher statements...")
    statements = generate_cypher()
    logger.info("Generated %d Cypher SQL statements.", len(statements))

    SQL_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("-- Apache AGE Data Migration for Customs Tariff Graph\n")
        f.write("LOAD 'age';\n")
        f.write("SET search_path = ag_catalog, '$user', public;\n\n")
        for stmt in statements:
            f.write(stmt + "\n")

    logger.info("Exported to %s", SQL_OUT)


if __name__ == "__main__":
    main()
