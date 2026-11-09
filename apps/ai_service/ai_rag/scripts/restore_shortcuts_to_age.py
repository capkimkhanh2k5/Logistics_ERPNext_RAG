#!/usr/bin/env python3
"""Utility script to restore the 421 shortcut edges into Apache AGE or revert corpus.json from corpus_BU.json.

Usage:
  python restore_shortcuts_to_age.py --restore-age      # Re-inserts the 421 shortcut edges into Apache AGE
  python restore_shortcuts_to_age.py --restore-corpus   # Copies corpus_BU.json over corpus.json
  python restore_shortcuts_to_age.py --clean-age        # Deletes the 421 shortcut edges from Apache AGE
"""

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rag.graph.age_adapter import ApacheAgeAdapter, _pg_connect

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("restore_shortcuts")

BU_PATH = BASE_DIR / "artifacts" / "corpus_BU.json"
CORPUS_PATH = BASE_DIR / "artifacts" / "corpus.json"


def restore_corpus_file():
    if not BU_PATH.exists():
        logger.error("Backup file not found: %s", BU_PATH)
        return False
    shutil.copyfile(BU_PATH, CORPUS_PATH)
    logger.info("Successfully restored %s from %s!", CORPUS_PATH, BU_PATH)
    return True


def restore_shortcuts_to_age():
    if not BU_PATH.exists():
        logger.error("Backup file not found: %s", BU_PATH)
        return False

    with open(BU_PATH, "r", encoding="utf-8") as f:
        bu_data = json.load(f)

    # Filter the 421 shortcut edges:
    nodes = {n["id"]: n for n in bu_data.get("nodes", [])}
    records = {r["id"]: r for r in bu_data.get("records", [])}

    sub_to_children = set()
    for e in bu_data["edges"]:
        if e.get("relation") == "CONTAINS":
            src = e.get("source")
            tgt = e.get("target")
            snode = nodes.get(src, {})
            srec = records.get(src, {})
            stype = snode.get("type") or snode.get("metadata", {}).get("node_type") or srec.get("node_type")
            scode = snode.get("code") or snode.get("metadata", {}).get("code") or srec.get("code") or ""
            if len(scode) == 6 or stype == "subheading":
                sub_to_children.add(tgt)

    shortcut_edges = []
    for e in bu_data["edges"]:
        src = e.get("source")
        tgt = e.get("target")
        rel = e.get("relation")
        if rel == "CONTAINS":
            snode = nodes.get(src, {})
            srec = records.get(src, {})
            stype = snode.get("type") or snode.get("metadata", {}).get("node_type") or srec.get("node_type")
            scode = snode.get("code") or snode.get("metadata", {}).get("code") or srec.get("code") or ""
            tnode = nodes.get(tgt, {})
            trec = records.get(tgt, {})
            tcode = tnode.get("code") or tnode.get("metadata", {}).get("code") or trec.get("code") or ""
            if (len(scode) == 4 or stype == "heading") and len(tcode) == 8 and tgt in sub_to_children:
                shortcut_edges.append(e)

    logger.info("Found %d shortcut edges to insert into Apache AGE...", len(shortcut_edges))
    age = ApacheAgeAdapter()
    inserted = 0
    with _pg_connect(age.db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, '$user', public;")
            for e in shortcut_edges:
                src = e["source"]
                tgt = e["target"]
                eid = e.get("id", f"e_{inserted}")
                sql = (
                    f"SELECT * FROM cypher('{age.graph_name}', $$ "
                    f"MATCH (a {{id: '{src}'}}), (b {{id: '{tgt}'}}) "
                    f"CREATE (a)-[:CONTAINS {{id: '{eid}', relation: 'CONTAINS'}}]->(b) "
                    f"RETURN a $$) AS (res agtype);"
                )
                cur.execute(sql)
                inserted += 1
        conn.commit()

    logger.info("Successfully re-inserted %d shortcut edges into Apache AGE graph '%s'!", inserted, age.graph_name)
    return True


def clean_shortcuts_from_age():
    age = ApacheAgeAdapter()
    with _pg_connect(age.db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, '$user', public;")
            sql = (
                f"SELECT * FROM cypher('{age.graph_name}', $$ "
                f"MATCH (h)-[r1:CONTAINS]->(item)<-[r2:CONTAINS]-(sub) "
                f"WHERE h.type = 'heading' AND sub.type = 'subheading' AND size(item.code) = 8 "
                f"DELETE r1 "
                f"RETURN count(*) "
                f"$$) AS (cnt agtype);"
            )
            cur.execute(sql)
            res = cur.fetchall()
            logger.info("Deleted shortcut edges from Apache AGE: %s", res)
        conn.commit()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage graph shortcut edges and backups.")
    parser.add_argument("--restore-corpus", action="store_true", help="Restore corpus.json from corpus_BU.json")
    parser.add_argument("--restore-age", action="store_true", help="Re-insert 421 shortcut edges into Apache AGE")
    parser.add_argument("--clean-age", action="store_true", help="Clean 421 shortcut edges from Apache AGE")
    args = parser.parse_args()

    if args.restore_corpus:
        restore_corpus_file()
    elif args.restore_age:
        restore_shortcuts_to_age()
    elif args.clean_age:
        clean_shortcuts_from_age()
    else:
        parser.print_help()
