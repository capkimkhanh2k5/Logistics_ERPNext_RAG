"""Staging Service Layer for managing draft documents, chunks review, and approved snapshots."""

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any, Optional, Union

import psycopg
from psycopg.types.json import Jsonb

from config.settings import ROOT
from rag.ingestion.docx import (
    DocType,
    ParsedDocumentResult,
    ReviewStatus,
    UnifiedDOCXParser,
)
from rag.utils.files import digest
from rag.vectordb.postgres import connect


class StagingService:
    """Manages the full lifecycle of documents and chunks in the Staging Area."""

    @classmethod
    def upload_and_parse(
        cls,
        file_path: Union[str, Path],
        document_no: Optional[str] = None,
        document_type: Optional[str] = None,
        effective_from: Optional[str] = None,
        effective_to: Optional[str] = None,
        user: str = "system",
    ) -> dict[str, Any]:
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"DOCX file not found: {path}")

        doc_id = str(uuid.uuid4())

        # 1. Parse using UnifiedDOCXParser
        parsed: ParsedDocumentResult = UnifiedDOCXParser.parse_file(
            file_path=path,
            explicit_type=document_type,
            document_no=document_no,
            document_id=doc_id,
        )

        # 2. Insert into PostgreSQL staging tables transactionally
        with connect() as conn, conn.transaction():
            # Insert document
            conn.execute(
                """
                INSERT INTO rag.staged_documents (
                    id, filename, document_no, document_type, file_sha256,
                    file_path, parser_version, status, total_nodes, total_chunks,
                    approved_chunks, excluded_chunks, effective_from, effective_to,
                    metadata, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                )
                """,
                (
                    doc_id,
                    parsed.filename,
                    parsed.document_no or document_no,
                    parsed.document_type.value,
                    parsed.file_sha256,
                    str(path),
                    "3.0.0",
                    "PARSED",
                    len(parsed.nodes),
                    len(parsed.chunks),
                    0,
                    0,
                    effective_from,
                    effective_to,
                    Jsonb(parsed.metadata),
                    user,
                ),
            )

            # Insert nodes with document-scoped IDs to guarantee global uniqueness
            for node in parsed.nodes:
                scoped_node_id = f"{doc_id}:{node.id}"
                scoped_parent_id = f"{doc_id}:{node.parent_id}" if node.parent_id else None
                conn.execute(
                    """
                    INSERT INTO rag.staged_nodes (
                        id, document_id, parent_node_id, node_type, node_level,
                        node_order, canonical_anchor, code, title, source_text,
                        source_location, breadcrumb, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        scoped_node_id,
                        doc_id,
                        scoped_parent_id,
                        node.node_type.value,
                        node.node_level,
                        node.node_order,
                        node.canonical_anchor,
                        node.code,
                        node.title,
                        node.source_text,
                        Jsonb(node.source_location.to_dict()),
                        node.breadcrumb,
                        Jsonb(node.metadata),
                    ),
                )

            # Insert chunks with matching scoped node_id
            for chunk in parsed.chunks:
                scoped_chunk_node_id = f"{doc_id}:{chunk.node_id}"
                conn.execute(
                    """
                    INSERT INTO rag.staged_chunks (
                        id, document_id, node_id, chunk_index, chunk_type,
                        canonical_anchor, code, level, role, namespace,
                        source_text, edited_text, embedding_text, embedding_hash,
                        breadcrumb, source_location, review_status, revision,
                        confidence_score, validation_issues, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """,
                    (
                        chunk.chunk_id,
                        doc_id,
                        scoped_chunk_node_id,
                        chunk.chunk_index,
                        chunk.chunk_type.value,
                        chunk.canonical_anchor,
                        chunk.code,
                        chunk.level,
                        chunk.role,
                        chunk.namespace,
                        chunk.source_text,
                        chunk.edited_text,
                        chunk.embedding_text,
                        digest(chunk.embedding_text),
                        chunk.breadcrumb,
                        Jsonb(chunk.source_location.to_dict()),
                        chunk.review_status.value,
                        1,
                        chunk.confidence_score,
                        Jsonb([i.to_dict() for i in chunk.validation_issues]),
                        Jsonb(chunk.metadata),
                    ),
                )

        return {
            "document_id": doc_id,
            "filename": parsed.filename,
            "document_type": parsed.document_type.value,
            "document_no": parsed.document_no,
            "total_nodes": len(parsed.nodes),
            "total_chunks": len(parsed.chunks),
            "status": "PARSED",
        }

    @classmethod
    def list_documents(
        cls, status: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        with connect() as conn:
            query = "SELECT * FROM rag.staged_documents"
            params: list[Any] = []
            if status:
                query += " WHERE status = %s"
                params.append(status)
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    @classmethod
    def get_document(cls, doc_id: str) -> Optional[dict[str, Any]]:
        with connect() as conn:
            row = conn.execute(
                "SELECT * FROM rag.staged_documents WHERE id = %s", (doc_id,)
            ).fetchone()
            if not row:
                return None

            counts = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE review_status = 'APPROVED') as approved,
                    COUNT(*) FILTER (WHERE review_status = 'EXCLUDED') as excluded,
                    COUNT(*) FILTER (WHERE review_status = 'PENDING_REVIEW') as pending,
                    COUNT(*) FILTER (WHERE review_status = 'NEEDS_REVIEW') as needs_review
                FROM rag.staged_chunks
                WHERE document_id = %s
                """,
                (doc_id,),
            ).fetchone()

            doc = dict(row)
            doc["chunk_stats"] = dict(counts) if counts else {}
            return doc

    @classmethod
    def get_nodes(cls, doc_id: str) -> list[dict[str, Any]]:
        """Fetch hierarchical AST nodes for a staged document."""
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT id, document_id, parent_node_id, node_type, node_level,
                       node_order, canonical_anchor, code, title, source_text,
                       breadcrumb, metadata
                FROM rag.staged_nodes
                WHERE document_id = %s
                ORDER BY node_order ASC
                """,
                (doc_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    @classmethod
    def get_chunks(
        cls,
        doc_id: str,
        review_status: Optional[str] = None,
        chunk_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        with connect() as conn:
            clauses = ["document_id = %s"]
            params: list[Any] = [doc_id]

            if review_status:
                clauses.append("review_status = %s")
                params.append(review_status)
            if chunk_type:
                clauses.append("chunk_type = %s")
                params.append(chunk_type)
            if search_query:
                clauses.append("(source_text ILIKE %s OR code ILIKE %s OR breadcrumb ILIKE %s)")
                q = f"%{search_query}%"
                params.extend([q, q, q])

            where_str = " AND ".join(clauses)
            query = f"""
                SELECT * FROM rag.staged_chunks
                WHERE {where_str}
                ORDER BY chunk_index ASC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    @classmethod
    def update_chunk(
        cls,
        chunk_id: str,
        edited_text: str,
        change_reason: str = "Manual edit during staging review",
        user: str = "system",
    ) -> dict[str, Any]:
        with connect() as conn, conn.transaction():
            old_chunk = conn.execute(
                "SELECT * FROM rag.staged_chunks WHERE id = %s", (chunk_id,)
            ).fetchone()
            if not old_chunk:
                raise ValueError(f"Chunk not found: {chunk_id}")

            new_revision = old_chunk["revision"] + 1

            # Update embedding text to incorporate edited text
            doc_no = old_chunk["metadata"].get("document_no") or "Tài liệu"
            new_embedding_text = f"{doc_no} | {old_chunk['breadcrumb']} | {edited_text.strip()}"

            conn.execute(
                """
                UPDATE rag.staged_chunks
                SET
                    edited_text = %s,
                    embedding_text = %s,
                    embedding_hash = %s,
                    review_status = 'APPROVED',
                    revision = %s,
                    reviewed_by = %s,
                    reviewed_at = clock_timestamp(),
                    updated_at = clock_timestamp()
                WHERE id = %s
                """,
                (
                    edited_text.strip(),
                    new_embedding_text,
                    digest(new_embedding_text),
                    new_revision,
                    user,
                    chunk_id,
                ),
            )

            # Record audit revision
            conn.execute(
                """
                INSERT INTO rag.staged_chunk_revisions (
                    chunk_id, revision_no, old_value, new_value, change_reason, changed_by
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    chunk_id,
                    new_revision,
                    Jsonb(
                        {
                            "source_text": old_chunk["source_text"],
                            "edited_text": old_chunk["edited_text"],
                            "embedding_text": old_chunk["embedding_text"],
                        }
                    ),
                    Jsonb(
                        {
                            "edited_text": edited_text.strip(),
                            "embedding_text": new_embedding_text,
                        }
                    ),
                    change_reason,
                    user,
                ),
            )

            # Update document stats
            cls._recalculate_doc_stats(conn, old_chunk["document_id"])
            return {"chunk_id": chunk_id, "revision": new_revision, "status": "APPROVED"}

    @classmethod
    def review_chunk(
        cls,
        chunk_id: str,
        action: str,  # 'APPROVE', 'EXCLUDE', 'NEEDS_REVIEW'
        user: str = "system",
    ) -> dict[str, Any]:
        status_map = {
            "APPROVE": "APPROVED",
            "EXCLUDE": "EXCLUDED",
            "NEEDS_REVIEW": "NEEDS_REVIEW",
        }
        new_status = status_map.get(action.upper())
        if not new_status:
            raise ValueError(f"Invalid review action: {action}. Must be APPROVE, EXCLUDE, or NEEDS_REVIEW.")

        with connect() as conn, conn.transaction():
            chunk = conn.execute(
                "SELECT document_id FROM rag.staged_chunks WHERE id = %s", (chunk_id,)
            ).fetchone()
            if not chunk:
                raise ValueError(f"Chunk not found: {chunk_id}")

            conn.execute(
                """
                UPDATE rag.staged_chunks
                SET review_status = %s, reviewed_by = %s, reviewed_at = clock_timestamp(), updated_at = clock_timestamp()
                WHERE id = %s
                """,
                (new_status, user, chunk_id),
            )
            cls._recalculate_doc_stats(conn, chunk["document_id"])
            return {"chunk_id": chunk_id, "review_status": new_status}

    @classmethod
    def review_all_chunks(
        cls,
        doc_id: str,
        action: str = "APPROVE",
        user: str = "system",
    ) -> dict[str, Any]:
        new_status = "APPROVED" if action.upper() == "APPROVE" else "EXCLUDED"
        with connect() as conn, conn.transaction():
            res = conn.execute(
                """
                UPDATE rag.staged_chunks
                SET review_status = %s, reviewed_by = %s, reviewed_at = clock_timestamp(), updated_at = clock_timestamp()
                WHERE document_id = %s AND review_status = 'PENDING_REVIEW'
                """,
                (new_status, user, doc_id),
            )
            cls._recalculate_doc_stats(conn, doc_id)
            return {"document_id": doc_id, "action": action, "updated_count": res.rowcount}

    @classmethod
    def create_approved_snapshot(
        cls, doc_id: str, user: str = "system"
    ) -> dict[str, Any]:
        """Creates an immutable snapshot artifact of approved chunks ready for background ingestion."""
        with connect() as conn, conn.transaction():
            doc = conn.execute(
                "SELECT * FROM rag.staged_documents WHERE id = %s", (doc_id,)
            ).fetchone()
            if not doc:
                raise ValueError(f"Document not found: {doc_id}")

            # Check if there are still pending chunks
            pending = conn.execute(
                "SELECT COUNT(*) as count FROM rag.staged_chunks WHERE document_id = %s AND review_status IN ('PENDING_REVIEW', 'NEEDS_REVIEW')",
                (doc_id,),
            ).fetchone()
            if pending and pending["count"] > 0:
                raise ValueError(
                    f"Cannot approve document with {pending['count']} pending/unreviewed chunks. Review or approve all first."
                )

            # Fetch all approved chunks
            approved_chunks = conn.execute(
                """
                SELECT * FROM rag.staged_chunks
                WHERE document_id = %s AND review_status = 'APPROVED'
                ORDER BY chunk_index ASC
                """,
                (doc_id,),
            ).fetchall()

            if not approved_chunks:
                raise ValueError("No approved chunks to snapshot (all chunks might be excluded).")

            # Serialize snapshot data
            snapshot_records = []
            for r in approved_chunks:
                snapshot_records.append(
                    {
                        "id": r["id"],
                        "node_id": r["node_id"],
                        "chunk_type": r["chunk_type"],
                        "code": r["code"],
                        "level": r["level"],
                        "role": r["role"],
                        "namespace": r["namespace"],
                        "source_text": r["edited_text"] or r["source_text"],
                        "embedding_text": r["embedding_text"],
                        "breadcrumb": r["breadcrumb"],
                        "source_location": r["source_location"],
                        "metadata": r["metadata"],
                    }
                )

            raw_json = json.dumps(snapshot_records, sort_keys=True, default=str)
            snapshot_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

            # Insert approved snapshot
            snap_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO rag.approved_snapshots (
                    id, staged_document_id, snapshot_hash, total_records, snapshot_data, approved_by
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    snap_id,
                    doc_id,
                    snapshot_hash,
                    len(snapshot_records),
                    Jsonb(snapshot_records),
                    user,
                ),
            )

            # Mark document as APPROVED
            conn.execute(
                """
                UPDATE rag.staged_documents
                SET status = 'APPROVED', reviewed_by = %s, reviewed_at = clock_timestamp()
                WHERE id = %s
                """,
                (user, doc_id),
            )

            return {
                "snapshot_id": snap_id,
                "document_id": doc_id,
                "snapshot_hash": snapshot_hash,
                "total_records": len(snapshot_records),
                "status": "APPROVED",
            }

    @staticmethod
    def _recalculate_doc_stats(conn: psycopg.Connection, doc_id: str) -> None:
        stats = conn.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE review_status = 'APPROVED') as approved,
                COUNT(*) FILTER (WHERE review_status = 'EXCLUDED') as excluded
            FROM rag.staged_chunks
            WHERE document_id = %s
            """,
            (doc_id,),
        ).fetchone()

        if stats:
            conn.execute(
                """
                UPDATE rag.staged_documents
                SET approved_chunks = %s, excluded_chunks = %s, status = 'IN_REVIEW'
                WHERE id = %s AND status = 'PARSED'
                """,
                (stats["approved"], stats["excluded"], doc_id),
            )
