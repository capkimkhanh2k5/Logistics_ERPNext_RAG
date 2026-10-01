"""Transactional snapshot loading; database credentials never appear in reports."""

import os
from typing import Any

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rag.data import ROOT, digest
from rag.embedding import validate_vectors


def connect() -> psycopg.Connection[dict[str, Any]]:
    load_dotenv(ROOT / ".env")
    conn = psycopg.connect(
        host=os.getenv("RAG_DB_HOST", "127.0.0.1"),
        port=os.getenv("RAG_DB_PORT", "55432"),
        dbname=os.getenv("RAG_DB_NAME", "hs_rag"),
        user=os.getenv("RAG_DB_USER", "rag"),
        password=os.environ["RAG_DB_PASSWORD"],
        row_factory=dict_row,
        autocommit=True,
    )
    register_vector(conn)
    return conn


def migrate(conn: psycopg.Connection[dict[str, Any]]) -> None:
    with conn.transaction():
        conn.execute((ROOT / "sql/001_rag_schema.sql").read_text())
    register_vector(conn)


def counts(conn: psycopg.Connection[dict[str, Any]], snapshot: str, profile: str) -> dict:
    row = conn.execute(
        """SELECT
      (SELECT count(*) FROM rag.chunks WHERE snapshot=%s) AS chunks,
      (SELECT count(*) FROM rag.embeddings WHERE snapshot=%s AND profile=%s) AS embeddings,
      (SELECT count(*) FROM rag.graph_nodes WHERE snapshot=%s) AS nodes,
      (SELECT count(*) FROM rag.graph_edges WHERE snapshot=%s) AS edges""",
        (snapshot, snapshot, profile, snapshot, snapshot),
    ).fetchone()
    if row is None:
        raise ValueError("Missing count result")
    return row


def ingest(
    conn: psycopg.Connection[dict[str, Any]],
    bundle: dict,
    manifest: dict,
    dense: np.ndarray,
    sparse: list | None = None,
    apply: bool = False,
) -> dict:
    snapshot = bundle["snapshot"]
    rows = bundle["records"]
    assert manifest["snapshot"] == snapshot
    assert manifest["ids"] == [r["id"] for r in rows]
    assert manifest["input_hashes"] == [r["input_hash"] for r in rows]
    assert digest(bundle["manifest"])[:24] == snapshot
    assert digest(manifest["profile"])[:24] == manifest["profile_id"]
    assert digest(rows) == bundle["manifest"]["records_hash"]
    assert digest(bundle["edges"]) == bundle["manifest"]["edges_hash"]
    dense = validate_vectors(dense, len(rows))
    sparse = sparse or []
    if manifest["profile"]["sparse"] and len(sparse) != len(rows):
        raise ValueError("Sparse row count mismatch")
    expected = {
        "chunks": len(rows),
        "embeddings": len(rows),
        "nodes": len(bundle["nodes"]),
        "edges": len(bundle["edges"]),
    }
    if not apply:
        return {"mode": "dry_run", "snapshot": snapshot, "expected": expected}
    profile = manifest["profile_id"]
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(20260926)")
        conn.execute(
            "INSERT INTO rag.snapshots(id,manifest) VALUES (%s,%s) ON CONFLICT DO NOTHING",
            (snapshot, Jsonb(bundle["manifest"])),
        )
        existing = conn.execute(
            "SELECT manifest FROM rag.snapshots WHERE id=%s", (snapshot,)
        ).fetchone()
        assert existing is not None
        assert existing["manifest"] == bundle["manifest"], "Snapshot collision"
        conn.execute(
            "INSERT INTO rag.profiles VALUES (%s,%s) ON CONFLICT DO NOTHING",
            (profile, Jsonb(manifest["profile"])),
        )
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO rag.chunks(snapshot,id,dataset,role,code,level,chapter,heading,source_text,embedding_text,metadata,locator,effective_from,effective_to,lexical,namespace,chunk_type,section,hs6,ahtn8,source,legal_status) VALUES
              (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
               to_tsvector('simple',unaccent(%s)),%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                [
                    (
                        snapshot,
                        r["id"],
                        r["dataset"],
                        r["role"],
                        r.get("code"),
                        r.get("level"),
                        r.get("chapter"),
                        r.get("heading"),
                        r["source_text"],
                        r["embedding_text"],
                        Jsonb(r["metadata"]),
                        Jsonb(r["locator"]),
                        r.get("effective_from"),
                        r.get("effective_to"),
                        r["lexical_text"],
                        r["namespace"],
                        r["chunk_type"],
                        r["section"],
                        r["hs6"],
                        r["ahtn8"],
                        Jsonb(r["source"]),
                        r["legal_status"],
                    )
                    for r in rows
                ],
            )
            cur.executemany(
                "INSERT INTO rag.embeddings VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                [
                    (snapshot, r["id"], profile, vector)
                    for r, vector in zip(rows, dense, strict=True)
                ],
            )
            cur.executemany(
                "INSERT INTO rag.graph_nodes VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                [(snapshot, n["id"], Jsonb(n["metadata"])) for n in bundle["nodes"]],
            )
            cur.executemany(
                "INSERT INTO rag.graph_edges VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                [
                    (
                        snapshot,
                        e["id"],
                        e["source"],
                        e["target"],
                        e["relation"],
                        Jsonb(e["metadata"]),
                    )
                    for e in bundle["edges"]
                ],
            )
            if sparse:
                cur.executemany(
                    "INSERT INTO rag.sparse_postings VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                    [
                        (snapshot, r["id"], profile, int(token), float(weight))
                        for r, weights in zip(rows, sparse, strict=True)
                        for token, weight in weights.items()
                    ],
                )
        actual = counts(conn, snapshot, profile)
        assert actual == expected, f"Count mismatch: {actual} != {expected}"
        conn.execute(
            "INSERT INTO rag.active VALUES (true,%s,%s) ON CONFLICT(singleton) "
            "DO UPDATE SET snapshot=excluded.snapshot,profile=excluded.profile",
            (snapshot, profile),
        )
    return {"mode": "apply", "snapshot": snapshot, "counts": actual}
