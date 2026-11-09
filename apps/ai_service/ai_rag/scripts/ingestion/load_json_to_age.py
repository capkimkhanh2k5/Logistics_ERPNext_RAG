"""ETL Script: Convert normalized customs JSONL into Apache AGE Cypher statements.

Exports or loads into PostgreSQL Apache AGE all 3 sections:
- Section XIV: Gems & Precious Metals (Ch. 71)
- Section XVI: Machinery & Electrical Equipment (Ch. 84, 85)
- Section XVII: Vehicles & Transport Equipment (Ch. 86, 87, 88, 89)

Generates Vertex nodes and Edges with full metadata and Vietnamese descriptions.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_json_to_age")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "normalized" / "TT31"
SQL_OUT = BASE_DIR / "sql" / "003_customs_graph_age_data.sql"


def escape_cy(val: str) -> str:
    """Escape string for openCypher literals."""
    if val is None:
        return ""
    return (
        str(val)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", "")
    )


def generate_cypher_statements() -> List[str]:
    statements: List[str] = []
    created_nodes: Set[str] = set()

    # 1. Root Node
    root_id = "ROOT_CUSTOMS_TARIFF"
    statements.append(
        f"SELECT * FROM cypher('customs_tariff_graph', $$ "
        f"CREATE (:TariffRoot {{id: '{root_id}', label: 'Biểu Thuế XNK Việt Nam', name: 'Biểu Thuế XNK Việt Nam'}}) "
        f"$$) as (v agtype);"
    )
    created_nodes.add(root_id)

    # 2. Section Structural Nodes
    sections = [
        ("SXVI-S-XVI", "Phần XVI", "XVI", "Máy và các trang thiết bị cơ khí; thiết bị điện"),
        ("SXVII_SECTION", "Phần XVII", "XVII", "Phương tiện vận tải, thiết bị vận tải"),
        ("SXIV_SECTION", "Phần XIV", "XIV", "Đá quý, kim loại quý và các sản phẩm của chúng"),
    ]
    for sid, slabel, scode, sdesc in sections:
        statements.append(
            f"SELECT * FROM cypher('customs_tariff_graph', $$ "
            f"CREATE (:Section {{id: '{sid}', label: '{escape_cy(slabel)}', section: '{scode}', description: '{escape_cy(sdesc)}'}}) "
            f"$$) as (v agtype);"
        )
        statements.append(
            f"SELECT * FROM cypher('customs_tariff_graph', $$ "
            f"MATCH (r:TariffRoot {{id: '{root_id}'}}), (s:Section {{id: '{sid}'}}) "
            f"CREATE (r)-[:CONTAINS]->(s) "
            f"$$) as (e agtype);"
        )
        created_nodes.add(sid)

    # 3. Master Nodes (XIV, XVI, XVII)
    master_files = [
        ("XIV", DATA_DIR / "Section-XIV" / "SECTION_XIV_MASTER_NORMALIZED.jsonl"),
        ("XVI", DATA_DIR / "Section-XVI" / "SECTION_XVI_MASTER_NORMALIZED.jsonl"),
        ("XVII", DATA_DIR / "Section-XVII" / "SECTION_XVII_MASTER_NORMALIZED.jsonl"),
    ]

    for sec_code, path in master_files:
        if not path.exists():
            continue
        logger.info("Processing master nodes for Section %s...", sec_code)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                nid = d.get("record_id") or d.get("code")
                if not nid or nid in created_nodes:
                    continue

                code = escape_cy(d.get("code", ""))
                level = d.get("level", 4)
                ch = escape_cy(d.get("chapter", ""))
                title = escape_cy(d.get("title_vi") or d.get("text_vi", "")[:60])
                desc = escape_cy(d.get("text_vi") or d.get("source_text_vi", "")[:250])
                
                label_type = "Chapter" if level == 2 else ("Heading" if level == 4 else "Subheading")
                statements.append(
                    f"SELECT * FROM cypher('customs_tariff_graph', $$ "
                    f"CREATE (:{label_type} {{id: '{escape_cy(nid)}', code: '{code}', label: '{title or code}', section: '{sec_code}', chapter: '{ch}', level: {level}, description: '{desc}'}}) "
                    f"$$) as (v agtype);"
                )
                created_nodes.add(nid)

    # 4. Edges (XIV, XVI, XVII)
    edge_files = [
        ("XIV", DATA_DIR / "Section-XIV" / "SECTION_XIV_GRAPH_EDGES.jsonl", "source", "target", "relation"),
        ("XVI", DATA_DIR / "Section-XVI" / "SECTION_XVI_GRAPH_EDGES.jsonl", "source_id", "target_id", "relation"),
        ("XVII", DATA_DIR / "Section-XVII" / "SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl", "from_id", "to_id", "relation"),
    ]

    created_edges_count = 0
    for sec_code, path, src_key, tgt_key, rel_key in edge_files:
        if not path.exists():
            continue
        logger.info("Processing edges for Section %s...", sec_code)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                src = escape_cy(d.get(src_key))
                tgt = escape_cy(d.get(tgt_key))
                rel = escape_cy(d.get(rel_key, "CONTAINS")).upper().replace("-", "_")

                if not src or not tgt:
                    continue

                # Ensure endpoints exist or auto-create placeholder
                for endpoint in [src, tgt]:
                    if endpoint not in created_nodes:
                        statements.append(
                            f"SELECT * FROM cypher('customs_tariff_graph', $$ "
                            f"CREATE (:TariffNode {{id: '{endpoint}', label: '{endpoint}', section: '{sec_code}'}}) "
                            f"$$) as (v agtype);"
                        )
                        created_nodes.add(endpoint)

                statements.append(
                    f"SELECT * FROM cypher('customs_tariff_graph', $$ "
                    f"MATCH (a {{id: '{src}'}}), (b {{id: '{tgt}'}}) "
                    f"CREATE (a)-[:{rel}]->(b) "
                    f"$$) as (e agtype);"
                )
                created_edges_count += 1

    logger.info(
        "Prepared total %d nodes and %d edges.",
        len(created_nodes),
        created_edges_count,
    )
    return statements


def main() -> None:
    logger.info("Generating 100% COMPLETE Apache AGE SQL / Cypher statements for all sections...")
    statements = generate_cypher_statements()
    logger.info("Generated %d Cypher SQL statements.", len(statements))

    SQL_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("-- ====================================================================\n")
        f.write("-- Complete Apache AGE Data Migration for Customs Tariff Graph (XIV, XVI, XVII)\n")
        f.write("-- ====================================================================\n")
        f.write("LOAD 'age';\n")
        f.write("SET search_path = ag_catalog, '$user', public;\n\n")
        for stmt in statements:
            f.write(stmt + "\n")

    logger.info("Exported full graph data to %s (File size: %.2f MB)", SQL_OUT, SQL_OUT.stat().st_size / (1024 * 1024))


if __name__ == "__main__":
    main()
