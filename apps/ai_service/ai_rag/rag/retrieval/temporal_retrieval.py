"""Temporal Retrieval Service for TradeRAG.
Supports as-of-date filtering, legal validity checks, and amendment effect enrichment.
"""

import datetime
import re
from typing import Any, Optional, Union

from config.settings import ROOT
from rag.embedding.bge_m3 import Embedder
from rag.utils.canonical_id import remove_vietnamese_accents
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
        suppress_boilerplate: bool = True,
        diversity_threshold: float = 0.92,
    ) -> list[dict[str, Any]]:
        # Format as_of_date
        query_date: Optional[datetime.date] = None
        if as_of_date:
            if isinstance(as_of_date, str):
                query_date = datetime.date.fromisoformat(as_of_date)
            else:
                query_date = as_of_date

        # Detect if query explicitly asks about administrative boilerplate topics
        clean_q = remove_vietnamese_accents(query.lower())
        is_boilerplate_query = any(
            kw in clean_q
            for kw in [
                "hieu luc",
                "ngay ap dung",
                "khi nao co hieu luc",
                "het hieu luc",
                "ai thi hanh",
                "trach nhiem thi hanh",
                "chuyen tiep",
                "bai bo",
                "thay the thong tu",
            ]
        )

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

            # Retrieve candidate pool (3x top_k to enable diversity re-ranking & MMR)
            candidate_limit = min(max(top_k * 3, 20), 100)

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
            params.append(candidate_limit)

            rows = conn.execute(sql, params).fetchall()
            candidates = []
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

                candidates.append(item)

            # Diversity and Boilerplate Filtering (MMR-style Deduplication)
            selected: list[dict[str, Any]] = []

            def _token_set(text: str) -> set[str]:
                return set(re.findall(r"\w+", (text or "").lower()))

            for cand in candidates:
                is_bp = (cand.get("role") == "boilerplate") or bool(
                    cand.get("metadata", {}).get("is_boilerplate")
                )

                # Suppress boilerplate if query is not asking for administrative metadata
                if suppress_boilerplate and not is_boilerplate_query and is_bp:
                    continue

                # Check lexical/semantic near-duplicates against already selected chunks
                cand_tokens = _token_set(cand.get("embedding_text") or cand.get("source_text", ""))
                is_near_dup = False
                for sel in selected:
                    sel_tokens = _token_set(sel.get("embedding_text") or sel.get("source_text", ""))
                    if cand_tokens and sel_tokens:
                        intersection = len(cand_tokens & sel_tokens)
                        union = len(cand_tokens | sel_tokens)
                        jaccard = intersection / union if union > 0 else 0.0
                        if jaccard >= diversity_threshold:
                            is_near_dup = True
                            break

                if not is_near_dup:
                    selected.append(cand)
                    if len(selected) >= top_k:
                        break

            # If diversity filtering pruned too many, backfill remaining best candidates
            if len(selected) < top_k:
                selected_ids = {s["id"] for s in selected}
                for cand in candidates:
                    if cand["id"] not in selected_ids:
                        selected.append(cand)
                        if len(selected) >= top_k:
                            break

            return selected
