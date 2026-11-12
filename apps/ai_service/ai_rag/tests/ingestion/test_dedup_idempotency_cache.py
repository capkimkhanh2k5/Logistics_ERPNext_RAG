"""Test Suite for Canonical Chunk Identity, Idempotency, Global Embedding Cache, and Retrieval Diversity."""

import datetime
import pytest
from config.settings import ROOT
from rag.embedding.bge_m3 import Embedder
from rag.ingestion.docx import DocType, NodeType, UnifiedDOCXParser
from rag.ingestion.jobs.ingestion_orchestrator import IngestionOrchestrator
from rag.ingestion.staging.staging_service import StagingService
from rag.retrieval.temporal_retrieval import TemporalRetriever
from rag.utils.canonical_id import (
    generate_canonical_chunk_id,
    is_boilerplate_content,
    normalize_document_key,
)
from rag.utils.files import digest
from rag.vectordb.postgres import connect


def test_deterministic_canonical_id_generation():
    """Verifies that chunk IDs generated are deterministic and conform to unified schema."""
    # 1. Legal Circular TT85
    doc_slug = normalize_document_key("Thông tư 85/2026/TT-BTC")
    assert doc_slug == "tt85_2026"

    clause_id = generate_canonical_chunk_id(
        namespace="legal_classification",
        document_no="Thông tư 85/2026/TT-BTC",
        node_type="CLAUSE",
        canonical_anchor="dieu-1-khoan-2",
    )
    assert clause_id == "legal:tt85_2026:clause_1_2"

    art_id = generate_canonical_chunk_id(
        namespace="legal_classification",
        document_no="85/2026/TT-BTC",
        node_type="ARTICLE",
        canonical_anchor="dieu-15",
    )
    assert art_id == "legal:tt85_2026:art_15"

    # 2. HS Tariff TT31
    hs_slug = normalize_document_key("Thông tư 31/2022/TT-BTC")
    assert hs_slug == "tt31_2022"

    hs8_id = generate_canonical_chunk_id(
        namespace="hs_classification",
        document_no="31/2022/TT-BTC",
        node_type="AHTN_ENTRY",
        code="8703.70.66",
    )
    assert hs8_id == "hs:tt31_2022:hs8_87037066"

    # 3. Boilerplate recognition
    assert is_boilerplate_content("Điều 15. Hiệu lực thi hành", "Thông tư này có hiệu lực kể từ ngày...") is True
    assert is_boilerplate_content("Điều 3. Tiêu chí phân loại", "Việc phân loại phải dựa vào thành phần lý hóa...") is False


def test_global_embedding_cache_hit():
    """Verifies that rag.embedding_cache correctly yields vectors and avoids recomputation."""
    with connect() as conn:
        active = conn.execute("SELECT snapshot, profile FROM rag.active").fetchone()
        snap, profile = active["snapshot"], active["profile"]

        # Fetch a sample chunk already in active snapshot
        sample = conn.execute(
            """
            SELECT c.embedding_text, e.embedding
            FROM rag.chunks c
            JOIN rag.embeddings e ON e.snapshot = c.snapshot AND e.chunk_id = c.id AND e.profile = %s
            WHERE c.snapshot = %s
            LIMIT 1
            """,
            (profile, snap),
        ).fetchone()

        assert sample is not None, "Active snapshot must contain at least 1 chunk with embedding"
        text = sample["embedding_text"]
        chash = digest(text)

        # Check lookup in rag.embedding_cache
        cached = conn.execute(
            """
            SELECT content_hash, dense_vector
            FROM rag.embedding_cache
            WHERE content_hash = %s AND profile_id = %s
            """,
            (chash, profile),
        ).fetchone()

        assert cached is not None, f"Hash {chash} should be present in global cache"
        assert len(cached["dense_vector"]) == 1024


def test_retrieval_diversity_and_boilerplate_suppression():
    """Verifies that TemporalRetriever filters out boilerplate and suppresses duplicate results."""
    retriever = TemporalRetriever()

    # Query 1: Substantive technical classification query
    substantive_results = retriever.search(
        query="Nguyên tắc phân loại máy móc tháo rời và hàng hóa dạng linh kiện",
        top_k=5,
        suppress_boilerplate=True,
    )
    assert len(substantive_results) > 0
    for r in substantive_results:
        assert r.get("role") != "boilerplate", f"Boilerplate provision found in substantive search: {r['id']}"

    # Query 2: Explicit boilerplate query asking about effective date
    bp_results = retriever.search(
        query="Thông tư có hiệu lực thi hành từ ngày nào và áp dụng ra sao?",
        top_k=5,
        suppress_boilerplate=True,  # Should still keep because query asks for effective date
    )
    assert len(bp_results) > 0


def test_reingestion_idempotency_workflow():
    """Verifies that uploading the same document does not create duplicate chunks in final snapshots."""
    sample_path = ROOT / "data/raw/ThongTu_85-2026_TT-BTC.docx"

    # Ingest version 1 into staging
    up1 = StagingService.upload_and_parse(
        file_path=sample_path,
        document_no="Thông tư 85/2026/TT-BTC",
        document_type="LEGAL_DOCUMENT",
        user="test_admin",
    )
    doc1_id = up1["id"]
    StagingService.review_all_chunks(doc1_id, action="APPROVE", user="test_admin")
    snap1 = StagingService.create_approved_snapshot(doc1_id, user="test_admin")
    job1_id = IngestionOrchestrator.queue_ingestion_job(doc1_id, snap1["snapshot_id"])
    res1 = IngestionOrchestrator.execute_job(job1_id, activate_snapshot=False)

    # Ingest version 2 (simulating re-upload of updated document)
    up2 = StagingService.upload_and_parse(
        file_path=sample_path,
        document_no="Thông tư 85/2026/TT-BTC",
        document_type="LEGAL_DOCUMENT",
        user="test_admin",
    )
    doc2_id = up2["id"]
    StagingService.review_all_chunks(doc2_id, action="APPROVE", user="test_admin")
    snap2 = StagingService.create_approved_snapshot(doc2_id, user="test_admin")
    job2_id = IngestionOrchestrator.queue_ingestion_job(doc2_id, snap2["snapshot_id"])
    res2 = IngestionOrchestrator.execute_job(job2_id, activate_snapshot=False)

    # Verify that total chunks in snapshot 2 matches snapshot 1 without duplication
    assert res1["total_active_chunks"] == res2["total_active_chunks"], (
        f"Re-ingestion must be idempotent! Snap1: {res1['total_active_chunks']} vs Snap2: {res2['total_active_chunks']}"
    )
