"""Ingestion Orchestrator and Background Job Processor.
Handles transactional outbox, BGE-M3 embedding, pgvector writing, Apache AGE sync, and atomic publication.
"""

import datetime
import json
import logging
import uuid
from typing import Any, Optional

import numpy as np
import psycopg
from psycopg.types.json import Jsonb

from config.retrieval import retrieval_config
from config.settings import ROOT
from rag.embedding.bge_m3 import Embedder
from rag.embedding.validation import validate_vectors
from rag.graph.age_adapter import escape_cypher
from rag.utils.canonical_id import normalize_document_key
from rag.utils.files import digest
from rag.vectordb.postgres import connect, counts, ingest

logger = logging.getLogger("rag.ingestion.orchestrator")


def _clean_row(row: dict) -> dict:
    cleaned = {}
    for k, v in row.items():
        if isinstance(v, (datetime.date, datetime.datetime, uuid.UUID)):
            cleaned[k] = str(v)
        elif isinstance(v, dict):
            cleaned[k] = _clean_row(v)
        elif isinstance(v, list):
            cleaned[k] = [str(x) if isinstance(x, (datetime.date, datetime.datetime, uuid.UUID)) else x for x in v]
        else:
            cleaned[k] = v
    return cleaned


class IngestionOrchestrator:
    """Coordinates the end-to-end ingestion of approved staging snapshots into Official Knowledge Base."""

    @classmethod
    def queue_ingestion_job(
        cls,
        staged_document_id: str,
        snapshot_id: str,
        idempotency_key: Optional[str] = None,
    ) -> str:
        key = idempotency_key or f"job-{snapshot_id}"
        with connect() as conn, conn.transaction():
            # Check idempotency
            existing = conn.execute(
                "SELECT id, status FROM rag.ingestion_jobs WHERE idempotency_key = %s",
                (key,),
            ).fetchone()
            if existing:
                return str(existing["id"])

            snap = conn.execute(
                "SELECT total_records FROM rag.approved_snapshots WHERE id = %s",
                (snapshot_id,),
            ).fetchone()
            if not snap:
                raise ValueError(f"Approved snapshot not found: {snapshot_id}")

            job_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO rag.ingestion_jobs (
                    id, staged_document_id, snapshot_id, idempotency_key,
                    status, stage, total_chunks, processed_chunks
                ) VALUES (%s, %s, %s, %s, 'QUEUED', 'INIT', %s, 0)
                """,
                (job_id, staged_document_id, snapshot_id, key, snap["total_records"]),
            )

            # Insert into transactional outbox
            conn.execute(
                """
                INSERT INTO rag.ingestion_outbox (
                    job_id, event_type, payload, status
                ) VALUES (%s, 'INGESTION_QUEUED', %s, 'PENDING')
                """,
                (
                    job_id,
                    Jsonb(
                        {
                            "job_id": job_id,
                            "staged_document_id": staged_document_id,
                            "snapshot_id": snapshot_id,
                        }
                    ),
                ),
            )
            return job_id

    @classmethod
    def execute_job(cls, job_id: str, activate_snapshot: bool = True) -> dict[str, Any]:
        """Executes an ingestion job from approved snapshot to published Knowledge Base."""
        with connect() as conn:
            job = conn.execute(
                "SELECT * FROM rag.ingestion_jobs WHERE id = %s", (job_id,)
            ).fetchone()
            if not job:
                raise ValueError(f"Ingestion job not found: {job_id}")
            if job["status"] == "COMPLETED":
                return {"job_id": job_id, "status": "COMPLETED", "message": "Already completed"}

            # Mark running
            conn.execute(
                "UPDATE rag.ingestion_jobs SET status = 'RUNNING', started_at = clock_timestamp(), stage = 'EMBEDDING' WHERE id = %s",
                (job_id,),
            )

        try:
            # 1. Fetch approved snapshot
            with connect() as conn:
                snap = conn.execute(
                    "SELECT * FROM rag.approved_snapshots WHERE id = %s",
                    (job["snapshot_id"],),
                ).fetchone()
                if not snap:
                    raise ValueError(f"Snapshot not found: {job['snapshot_id']}")

                staged_records = snap["snapshot_data"]

                # 2. Fetch current active snapshot to build cumulative records
                active = conn.execute("SELECT snapshot, profile FROM rag.active").fetchone()
                active_snapshot_id = active["snapshot"] if active else None
                active_profile_id = active["profile"] if active else None

                existing_chunks: list[dict] = []
                existing_nodes: list[dict] = []
                existing_edges: list[dict] = []

                if active_snapshot_id:
                    existing_chunks = [
                        _clean_row(dict(r))
                        for r in conn.execute(
                            "SELECT * FROM rag.chunks WHERE snapshot = %s",
                            (active_snapshot_id,),
                        ).fetchall()
                    ]
                    existing_nodes = [
                        _clean_row(dict(r))
                        for r in conn.execute(
                            "SELECT * FROM rag.graph_nodes WHERE snapshot = %s",
                            (active_snapshot_id,),
                        ).fetchall()
                    ]
                    existing_edges = [
                        _clean_row(dict(r))
                        for r in conn.execute(
                            "SELECT * FROM rag.graph_edges WHERE snapshot = %s",
                            (active_snapshot_id,),
                        ).fetchall()
                    ]

            # 3. Format staged chunks into official canonical records
            new_records: list[dict] = []
            new_nodes: list[dict] = []
            new_edges: list[dict] = []

            for r in staged_records:
                raw_id = str(r["id"])
                # Strip UUID prefix if present: e.g. "3b544f65-...:legal:tt85_2026:art_1" -> "legal:tt85_2026:art_1"
                if ":" in raw_id:
                    pfx, rest = raw_id.split(":", 1)
                    record_id = rest if len(pfx) == 36 and "-" in pfx else raw_id
                else:
                    record_id = raw_id

                node_id = r["node_id"]
                loc = r.get("source_location") or {}
                meta = r.get("metadata") or {}
                raw_doc_no = meta.get("document_no") or r.get("metadata", {}).get("document_no")
                dataset_slug = normalize_document_key(raw_doc_no, default_fallback="docx_staged")

                rec = {
                    "id": record_id,
                    "dataset": dataset_slug,
                    "role": r["role"],
                    "code": r.get("code"),
                    "level": r.get("level"),
                    "chapter": r.get("code", "")[:2] if (r.get("level") == 8 and r.get("code")) else None,
                    "heading": r.get("code", "")[:4] if (r.get("level") == 8 and r.get("code")) else None,
                    "source_text": r["source_text"],
                    "embedding_text": r["embedding_text"],
                    "lexical_text": r["embedding_text"],
                    "metadata": {**meta, "document_key": dataset_slug},
                    "locator": loc,
                    "effective_from": meta.get("effective_from"),
                    "effective_to": meta.get("effective_to"),
                    "namespace": r["namespace"],
                    "chunk_type": r["chunk_type"],
                    "section": meta.get("section"),
                    "hs6": r.get("code", "")[:6] if (r.get("level") == 8 and r.get("code")) else None,
                    "ahtn8": r.get("code") if r.get("level") == 8 else None,
                    "source": loc,
                    "legal_status": meta.get("legal_status", "VALID"),
                    "input_hash": digest(r["embedding_text"]),
                }
                new_records.append(rec)

                # Node for graph
                new_nodes.append(
                    {
                        "id": record_id,
                        "metadata": {
                            "type": r["chunk_type"],
                            "code": r.get("code"),
                            "label": r.get("code") or r.get("breadcrumb", "")[-40:],
                            "description": r["source_text"][:200],
                            "document_key": dataset_slug,
                            **meta,
                        },
                    }
                )

            # Idempotency / Document Scope Replacement:
            # Purge existing chunks and nodes that belong to the documents being replaced
            target_datasets = {r["dataset"] for r in new_records if r.get("dataset")}
            target_prefixes = {
                ":".join(r["id"].split(":", 2)[:2]) + ":"
                for r in new_records
                if r.get("id") and r["id"].count(":") >= 2
            }

            purged_existing_chunks = []
            for c in existing_chunks:
                c_dataset = c.get("dataset")
                c_id = c.get("id", "")
                if c_dataset in target_datasets:
                    continue
                if any(c_id.startswith(pfx) for pfx in target_prefixes):
                    continue
                purged_existing_chunks.append(c)

            combined_by_id = {c["id"]: c for c in purged_existing_chunks}
            for rec in new_records:
                combined_by_id[rec["id"]] = rec
            combined_chunks = list(combined_by_id.values())

            # Ensure all chunks have input_hash and lexical_text populated
            for c in combined_chunks:
                if "input_hash" not in c:
                    c["input_hash"] = digest(c["embedding_text"])
                if "lexical_text" not in c:
                    c["lexical_text"] = c.get("embedding_text") or c.get("source_text") or ""

            # Combined graph nodes with replacement
            purged_existing_nodes = []
            for n in existing_nodes:
                n_id = n.get("id", "")
                if any(n_id.startswith(pfx) for pfx in target_prefixes):
                    continue
                purged_existing_nodes.append(n)

            nodes_by_id = {n["id"]: n for n in purged_existing_nodes}
            for n in new_nodes:
                nodes_by_id[n["id"]] = n
            combined_nodes = list(nodes_by_id.values())

            # Edges
            combined_edges = list(existing_edges)

            # Compute new snapshot ID
            snapshot_manifest = {
                "records_hash": digest(combined_chunks),
                "nodes_hash": digest(combined_nodes),
                "edges_hash": digest(combined_edges),
                "staged_snapshot_id": str(snap["id"]),
                "parent_snapshot": str(active_snapshot_id) if active_snapshot_id else None,
            }
            new_snapshot_id = digest(snapshot_manifest)[:24]

            # 4. Generate Embeddings using BGE-M3 (Cache-First Pipeline)
            embedder = Embedder()
            profile_id = embedder.profile_id

            cached_vectors: dict[str, np.ndarray] = {}
            cached_sparse: dict[str, dict] = {}

            # Step 4a: Fast lookup in active snapshot
            if active_snapshot_id and active_profile_id == profile_id:
                with connect() as conn:
                    rows = conn.execute(
                        "SELECT chunk_id, embedding FROM rag.embeddings WHERE snapshot = %s AND profile = %s",
                        (active_snapshot_id, active_profile_id),
                    ).fetchall()
                    for r in rows:
                        cached_vectors[r["chunk_id"]] = np.array(r["embedding"], dtype=np.float32)

                    if embedder.cfg["sparse"]:
                        s_rows = conn.execute(
                            "SELECT chunk_id, token, weight FROM rag.sparse_postings WHERE snapshot = %s AND profile = %s",
                            (active_snapshot_id, active_profile_id),
                        ).fetchall()
                        for sr in s_rows:
                            cached_sparse.setdefault(sr["chunk_id"], {})[str(sr["token"])] = float(
                                sr["weight"]
                            )

            # Step 4b: Check Global Content-Hash Embedding Cache for any unresolved chunks
            unresolved_chunks = [c for c in combined_chunks if c["id"] not in cached_vectors]
            if unresolved_chunks:
                hash_to_chunks: dict[str, list[dict]] = {}
                for c in unresolved_chunks:
                    chash = c.get("input_hash") or digest(c["embedding_text"])
                    hash_to_chunks.setdefault(chash, []).append(c)

                query_hashes = list(hash_to_chunks.keys())
                with connect() as conn:
                    batch_size = 500
                    for i in range(0, len(query_hashes), batch_size):
                        sub_hashes = query_hashes[i : i + batch_size]
                        cache_rows = conn.execute(
                            """
                            SELECT content_hash, dense_vector, sparse_weights
                            FROM rag.embedding_cache
                            WHERE profile_id = %s AND content_hash = ANY(%s)
                            """,
                            (profile_id, sub_hashes),
                        ).fetchall()

                        for cr in cache_rows:
                            h = cr["content_hash"]
                            vec = np.array(cr["dense_vector"], dtype=np.float32)
                            sp = cr["sparse_weights"] or {}
                            for target_c in hash_to_chunks.get(h, []):
                                cached_vectors[target_c["id"]] = vec
                                cached_sparse[target_c["id"]] = sp

                cache_hit_count = len(unresolved_chunks) - len([c for c in combined_chunks if c["id"] not in cached_vectors])
                if cache_hit_count > 0:
                    logger.info("Global Embedding Cache: %d hits out of %d unresolved chunks!", cache_hit_count, len(unresolved_chunks))

            # Step 4c: Only encode truly missing chunks
            missing_chunks = [c for c in combined_chunks if c["id"] not in cached_vectors]
            if missing_chunks:
                logger.info(
                    "Encoding %d missing chunks via BGE-M3 Embedder...", len(missing_chunks)
                )
                encoded = embedder.encode([c["embedding_text"] for c in missing_chunks])
                new_cache_rows = []
                for c, v, w in zip(missing_chunks, encoded["dense"], encoded["sparse"], strict=True):
                    cached_vectors[c["id"]] = v
                    cached_sparse[c["id"]] = w
                    chash = c.get("input_hash") or digest(c["embedding_text"])
                    new_cache_rows.append((chash, profile_id, v.tolist(), json.dumps(w)))

                # Persist newly computed vectors to global embedding cache
                if new_cache_rows:
                    with connect() as conn:
                        with conn.cursor() as cur:
                            cur.executemany(
                                """
                                INSERT INTO rag.embedding_cache (content_hash, profile_id, dense_vector, sparse_weights)
                                VALUES (%s, %s, %s, %s::jsonb)
                                ON CONFLICT (content_hash, profile_id) DO NOTHING
                                """,
                                new_cache_rows,
                            )
                            conn.commit()

            # Build ordered vectors array matching combined_chunks
            combined_dense = np.stack([cached_vectors[c["id"]] for c in combined_chunks])
            combined_sparse = [cached_sparse.get(c["id"], {}) for c in combined_chunks]

            bundle = {
                "snapshot": new_snapshot_id,
                "manifest": snapshot_manifest,
                "records": combined_chunks,
                "nodes": combined_nodes,
                "edges": combined_edges,
            }

            manifest_meta = {
                "snapshot": new_snapshot_id,
                "profile_id": profile_id,
                "profile": embedder.profile,
                "ids": [c["id"] for c in combined_chunks],
                "input_hashes": [c.get("input_hash") or digest(c["embedding_text"]) for c in combined_chunks],
            }

            # 5. Ingest into PostgreSQL
            with connect() as conn:
                conn.execute(
                    "UPDATE rag.ingestion_jobs SET stage = 'VECTOR_WRITE' WHERE id = %s",
                    (job_id,),
                )
                ingest_res = ingest(
                    conn=conn,
                    bundle=bundle,
                    manifest=manifest_meta,
                    dense=combined_dense,
                    sparse=combined_sparse,
                    apply=True,
                )

            # 6. Synchronize into Apache AGE Graph
            with connect() as conn:
                conn.execute(
                    "UPDATE rag.ingestion_jobs SET stage = 'GRAPH_SYNC' WHERE id = %s",
                    (job_id,),
                )
                cls._sync_age_graph(conn, new_nodes, new_edges)

            # 7. Verification stage
            with connect() as conn:
                conn.execute(
                    "UPDATE rag.ingestion_jobs SET stage = 'VERIFYING' WHERE id = %s",
                    (job_id,),
                )
                verified_counts = counts(conn, new_snapshot_id, profile_id)
                if verified_counts["chunks"] != len(combined_chunks):
                    raise ValueError(
                        f"Integrity check failed: expected {len(combined_chunks)} chunks, found {verified_counts['chunks']}"
                    )

            # 8. Publication: Atomic switch of active pointer & retrieval policies
            with connect() as conn, conn.transaction():
                if activate_snapshot:
                    conn.execute(
                        """
                        INSERT INTO rag.active (singleton, snapshot, profile)
                        VALUES (true, %s, %s)
                        ON CONFLICT (singleton) DO UPDATE
                        SET snapshot = EXCLUDED.snapshot, profile = EXCLUDED.profile
                        """,
                        (new_snapshot_id, profile_id),
                    )

                    # Update retrieval policies so Retriever stays synchronized
                    for p_name in ["config/selected_retrieval.json", "config/unified_retrieval.json"]:
                        policy_path = ROOT / p_name
                        if policy_path.exists():
                            try:
                                pol = json.loads(policy_path.read_text())
                                pol["snapshot"] = new_snapshot_id
                                pol["profile"] = profile_id
                                policy_path.write_text(json.dumps(pol, ensure_ascii=False, indent=2) + "\n")
                            except Exception as pe:
                                logger.warning("Could not update policy file %s: %s", p_name, pe)

                # Mark job as COMPLETED
                conn.execute(
                    """
                    UPDATE rag.ingestion_jobs
                    SET status = 'COMPLETED', stage = 'PUBLISHED', processed_chunks = %s, finished_at = clock_timestamp()
                    WHERE id = %s
                    """,
                    (len(combined_chunks), job_id),
                )

                # Mark staged document as COMMITTED
                conn.execute(
                    """
                    UPDATE rag.staged_documents
                    SET status = 'COMMITTED', committed_at = clock_timestamp()
                    WHERE id = %s
                    """,
                    (job["staged_document_id"],),
                )

                # Mark outbox event as DISPATCHED
                conn.execute(
                    """
                    UPDATE rag.ingestion_outbox
                    SET status = 'DISPATCHED', dispatched_at = clock_timestamp()
                    WHERE job_id = %s
                    """,
                    (job_id,),
                )

            logger.info("Ingestion Job %s completed successfully. Published snapshot: %s", job_id, new_snapshot_id)
            return {
                "job_id": job_id,
                "status": "COMPLETED",
                "new_snapshot_id": new_snapshot_id,
                "total_active_chunks": len(combined_chunks),
                "counts": verified_counts,
            }

        except Exception as exc:
            logger.exception("Ingestion Job %s failed: %s", job_id, exc)
            with connect() as conn:
                conn.execute(
                    """
                    UPDATE rag.ingestion_jobs
                    SET status = 'FAILED', error_code = 'INGESTION_ERROR', error_message = %s, finished_at = clock_timestamp()
                    WHERE id = %s
                    """,
                    (str(exc), job_id),
                )
            raise

    @classmethod
    def _sync_age_graph(
        cls,
        conn: psycopg.Connection,
        new_nodes: list[dict],
        new_edges: list[dict],
    ) -> None:
        """Appends new vertices and edges into Apache AGE graph."""
        if not new_nodes:
            return

        with conn.transaction():
            conn.execute("LOAD 'age';")
            conn.execute("SET search_path = ag_catalog, '$user', public;")

            for n in new_nodes:
                nid = escape_cypher(n["id"])
                lbl = escape_cypher(n["metadata"].get("label", nid))
                typ = escape_cypher(n["metadata"].get("type", "item"))
                code = escape_cypher(n["metadata"].get("code", ""))
                desc = escape_cypher(str(n["metadata"].get("description", ""))[:200])

                cypher = f"""
                SELECT * FROM cypher('customs_tariff_graph', $$
                    MERGE (v:TariffNode {{id: '{nid}'}})
                    ON CREATE SET v.label = '{lbl}', v.type = '{typ}', v.code = '{code}', v.description = '{desc}'
                    RETURN v
                $$) as (v agtype);
                """
                try:
                    conn.execute(cypher)
                except Exception as e:
                    logger.debug("AGE node sync skipped or failed for %s: %s", nid, e)
