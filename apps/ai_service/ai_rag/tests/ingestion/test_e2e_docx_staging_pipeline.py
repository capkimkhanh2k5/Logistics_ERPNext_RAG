"""End-to-End Test Suite for Unified DOCX Ingestion, Staging Area, and Publication Pipeline."""

import pytest
import uuid
from pathlib import Path

from config.settings import ROOT
from rag.embedding.bge_m3 import Embedder
from rag.ingestion.docx import DocType, UnifiedDOCXParser
from rag.ingestion.staging.staging_service import StagingService
from rag.ingestion.jobs.ingestion_orchestrator import IngestionOrchestrator
from rag.retrieval.temporal_retrieval import TemporalRetriever
from rag.vectordb.postgres import connect

FIXTURE_PATH = ROOT / "data/raw/docx/05_VBHN-BGTVT_m_640747.docx"


def test_full_e2e_staging_to_publication_pipeline():
    assert FIXTURE_PATH.is_file(), f"Fixture missing: {FIXTURE_PATH}"

    # Capture original active snapshot to guarantee isolation
    orig_snapshot = None
    with connect() as conn:
        active = conn.execute("SELECT snapshot FROM rag.active WHERE singleton = True").fetchone()
        if active:
            orig_snapshot = active["snapshot"]

    try:
        # 1. Upload & Parse into Staging
        doc_no = f"TEST-VBHN-{uuid.uuid4().hex[:6]}"
        doc_res = StagingService.upload_and_parse(
            file_path=FIXTURE_PATH,
            document_no=doc_no,
            document_type="LEGAL_DOCUMENT",
            user="test_e2e_runner",
        )
        doc_id = doc_res["document_id"]
        assert doc_res["status"] == "PARSED"
        assert doc_res["total_chunks"] > 0

        # 2. Inspect staged chunks
        chunks = StagingService.get_chunks(doc_id=doc_id, limit=5)
        assert len(chunks) == 5
        target_chunk = chunks[0]

        # 3. Edit chunk text and verify audit revision
        edit_text = target_chunk["source_text"] + " [E2E_AUDITED_OK]"
        edit_res = StagingService.update_chunk(
            chunk_id=target_chunk["id"],
            edited_text=edit_text,
            change_reason="Automated E2E Verification",
            user="test_e2e_runner",
        )
        assert edit_res["status"] == "APPROVED"
        assert edit_res["revision"] == 2

        # Verify revision was recorded in staged_chunk_revisions
        with connect() as conn:
            rev = conn.execute(
                "SELECT * FROM rag.staged_chunk_revisions WHERE chunk_id = %s",
                (target_chunk["id"],),
            ).fetchone()
            assert rev is not None
            assert rev["revision_no"] == 2
            assert rev["new_value"]["edited_text"] == edit_text

        # 4. Approve remaining chunks
        approve_res = StagingService.review_all_chunks(
            doc_id=doc_id,
            action="APPROVE",
            user="test_e2e_runner",
        )
        assert approve_res["updated_count"] >= 0

        # 5. Create immutable approved snapshot
        snapshot_res = StagingService.create_approved_snapshot(
            doc_id=doc_id,
            user="test_e2e_runner",
        )
        snapshot_id = snapshot_res["snapshot_id"]
        assert snapshot_res["status"] == "APPROVED"
        assert len(snapshot_res["snapshot_hash"]) == 64

        # 6. Queue and execute ingestion job
        job_id = IngestionOrchestrator.queue_ingestion_job(
            staged_document_id=doc_id,
            snapshot_id=snapshot_id,
            idempotency_key=f"e2e-job-{doc_id}",
        )
        assert job_id is not None

        exec_res = IngestionOrchestrator.execute_job(job_id=job_id, activate_snapshot=True)
        assert exec_res["status"] == "COMPLETED"
        new_snapshot_id = exec_res["new_snapshot_id"]

        # 7. Verify atomic publication pointer in rag.active
        with connect() as conn:
            active = conn.execute("SELECT snapshot, profile FROM rag.active").fetchone()
            assert active["snapshot"] == new_snapshot_id

            # Verify chunk exists in official rag.chunks with canonical ID
            canonical_target_id = (
                target_chunk["id"].split(":", 1)[1]
                if ":" in target_chunk["id"] and len(target_chunk["id"].split(":", 1)[0]) == 36
                else target_chunk["id"]
            )
            chunk_in_kb = conn.execute(
                "SELECT * FROM rag.chunks WHERE snapshot = %s AND id = %s",
                (new_snapshot_id, canonical_target_id),
            ).fetchone()
            assert chunk_in_kb is not None
            assert "[E2E_AUDITED_OK]" in chunk_in_kb["source_text"]

        # 8. Test retrieval of the newly committed chunk
        retriever = TemporalRetriever()
        results = retriever.search(
            query=edit_text,
            top_k=10,
        )
        assert len(results) > 0
        top_ids = [r["id"] for r in results]
        assert canonical_target_id in top_ids
    finally:
        if orig_snapshot:
            with connect() as conn:
                conn.execute(
                    "UPDATE rag.active SET snapshot = %s WHERE singleton = True",
                    (orig_snapshot,),
                )
                conn.commit()


def test_idempotent_job_execution():
    with connect() as conn:
        job = conn.execute(
            "SELECT * FROM rag.ingestion_jobs WHERE status = 'COMPLETED' LIMIT 1"
        ).fetchone()

    if job:
        # Re-running already completed job should return COMPLETED without error
        res = IngestionOrchestrator.execute_job(str(job["id"]), activate_snapshot=False)
        assert res["status"] == "COMPLETED"
