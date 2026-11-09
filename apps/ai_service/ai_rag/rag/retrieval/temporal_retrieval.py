"""Temporal Retrieval Service for TradeRAG.
Supports as-of-date filtering, legal validity checks, and amendment effect enrichment.
"""

import datetime
from typing import Any, Optional, Union

from config.settings import ROOT
from rag.embedding.bge_m3 import Embedder
from rag.vectordb.postgres import connect


class TemporalRetriever:
    """Retrieves chunks from active snapshot while respecting legal validity dates and amendment effects."""

    def __init__(self, embedder: Optional[Embedder] = None) -> None:
        self.embedder = embedder or Embedder()

    def search(
        self,
        query: str,
        as_of_date: Optional[Union[str, datetime.date]] = None,
        include_expired: bool = False,
        namespace: Optional[str] = None,
        chunk_type: Optional[str] = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        # Format as_of_date
        query_date: Optional[datetime.date] = None
        if as_of_date:
            if isinstance(as_of_date, str):
                query_date = datetime.date.fromisoformat(as_of_date)
            else:
                query_date = as_of_date

        # Compute query vector
        encoded = self.embedder.encode([query])
        query_vector = encoded["dense"][0]

        with connect() as conn:
            active = conn.execute("SELECT snapshot, profile FROM rag.active").fetchone()
            if not active:
                raise RuntimeError("No active Knowledge Base snapshot found in rag.active")

            snapshot_id = active["snapshot"]

            # Build SQL where clause
            clauses = ["c.snapshot = %s"]
            params: list[Any] = [snapshot_id]

            if namespace:
                clauses.append("c.namespace = %s")
                params.append(namespace)

            if chunk_type:
                clauses.append("c.chunk_type = %s")
                params.append(chunk_type)

            if query_date:
                clauses.append("(c.effective_from IS NULL OR c.effective_from <= %s)")
                params.append(query_date)
                if not include_expired:
                    clauses.append("(c.effective_to IS NULL OR c.effective_to >= %s)")
                    params.append(query_date)
            elif not include_expired:
                clauses.append("(c.legal_status IS NULL OR c.legal_status NOT IN ('EXPIRED', 'REPEALED'))")

            where_str = " AND ".join(clauses)

            # Cosine distance ranking via pgvector
            sql = f"""
            SELECT
                c.id, c.dataset, c.role, c.code, c.level, c.chapter, c.heading,
                c.source_text, c.embedding_text, c.metadata, c.locator,
                c.effective_from, c.effective_to, c.namespace, c.chunk_type,
                c.legal_status,
                (e.embedding <=> %s::vector) AS distance
            FROM rag.chunks c
            JOIN rag.embeddings e ON c.snapshot = e.snapshot AND c.id = e.chunk_id
            WHERE {where_str}
            ORDER BY distance ASC
            LIMIT %s
            """
            params.insert(0, query_vector)
            params.append(top_k)

            rows = conn.execute(sql, params).fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["score"] = float(1.0 - item["distance"])

                # Check if this provision has governing legal effects (amendments/repeals)
                doc_no = item.get("metadata", {}).get("document_no") or item["dataset"]
                anchor = item.get("metadata", {}).get("canonical_anchor")
                if doc_no and anchor:
                    effects = conn.execute(
                        """
                        SELECT effect_type, source_document_no, source_provision_anchor, effective_from
                        FROM rag.legal_effects
                        WHERE target_document_no = %s AND target_provision_anchor = %s
                        """,
                        (doc_no, anchor),
                    ).fetchall()
                    if effects:
                        item["amendment_effects"] = [dict(e) for e in effects]

                results.append(item)

            return results
