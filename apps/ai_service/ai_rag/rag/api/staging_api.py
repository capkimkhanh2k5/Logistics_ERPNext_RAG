"""RESTful Service Facade for Staging Area APIs."""

from typing import Any, Optional
from rag.ingestion.staging.staging_service import StagingService


def upload_document(
    file_path: str,
    document_no: Optional[str] = None,
    document_type: Optional[str] = None,
    user: str = "api_user",
) -> dict[str, Any]:
    return StagingService.upload_and_parse(
        file_path=file_path,
        document_no=document_no,
        document_type=document_type,
        user=user,
    )


def list_documents(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    return StagingService.list_documents(status=status, limit=limit, offset=offset)


def get_document(doc_id: str) -> Optional[dict[str, Any]]:
    return StagingService.get_document(doc_id)


def get_chunks(
    doc_id: str,
    review_status: Optional[str] = None,
    chunk_type: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    return StagingService.get_chunks(
        doc_id=doc_id,
        review_status=review_status,
        chunk_type=chunk_type,
        search_query=search_query,
        limit=limit,
        offset=offset,
    )


def update_chunk(
    chunk_id: str,
    edited_text: str,
    reason: str = "API edit",
    user: str = "api_user",
) -> dict[str, Any]:
    return StagingService.update_chunk(
        chunk_id=chunk_id,
        edited_text=edited_text,
        change_reason=reason,
        user=user,
    )


def review_chunk(
    chunk_id: str,
    action: str,
    user: str = "api_user",
) -> dict[str, Any]:
    return StagingService.review_chunk(
        chunk_id=chunk_id,
        action=action,
        user=user,
    )


def approve_all_chunks(
    doc_id: str,
    user: str = "api_user",
) -> dict[str, Any]:
    return StagingService.review_all_chunks(
        doc_id=doc_id,
        action="APPROVE",
        user=user,
    )


def create_approved_snapshot(
    doc_id: str,
    user: str = "api_user",
) -> dict[str, Any]:
    return StagingService.create_approved_snapshot(
        doc_id=doc_id,
        user=user,
    )
