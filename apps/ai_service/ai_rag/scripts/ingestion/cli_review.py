#!/usr/bin/env python3
"""CLI Review Tool for Inspecting, Editing, and Approving Staged Documents and Chunks."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.ingestion.staging.staging_service import StagingService


def cmd_upload(args):
    path = Path(args.file)
    print(f"Uploading and parsing {path}...")
    res = StagingService.upload_and_parse(
        file_path=path,
        document_no=args.doc_no,
        document_type=args.type,
        user=args.user,
    )
    print(f"[OK] Document uploaded successfully!")
    print(f"     ID:            {res['document_id']}")
    print(f"     Type:          {res['document_type']}")
    print(f"     Total Nodes:   {res['total_nodes']}")
    print(f"     Total Chunks:  {res['total_chunks']}")


def cmd_list(args):
    docs = StagingService.list_documents(status=args.status, limit=args.limit)
    if not docs:
        print("No staged documents found.")
        return
    print(f"{'ID':<38} {'Doc No':<20} {'Type':<18} {'Status':<12} {'Chunks':<8} {'Filename'}")
    print("-" * 115)
    for d in docs:
        d_no = d["document_no"] or "-"
        print(
            f"{str(d['id']):<38} {d_no:<20} {d['document_type']:<18} {d['status']:<12} {d['total_chunks']:<8} {d['filename']}"
        )


def cmd_info(args):
    doc = StagingService.get_document(args.doc_id)
    if not doc:
        print(f"Error: Document not found: {args.doc_id}")
        return
    print(f"=== Document Details ===")
    print(f"ID:           {doc['id']}")
    print(f"Filename:     {doc['filename']}")
    print(f"Document No:  {doc['document_no']}")
    print(f"Type:         {doc['document_type']}")
    print(f"Status:       {doc['status']}")
    print(f"Created:      {doc['created_at']}")
    stats = doc.get("chunk_stats", {})
    print(f"Chunk Stats:  Total: {stats.get('total', 0)} | Approved: {stats.get('approved', 0)} | Pending: {stats.get('pending', 0)} | Excluded: {stats.get('excluded', 0)}")


def cmd_chunks(args):
    chunks = StagingService.get_chunks(
        doc_id=args.doc_id,
        review_status=args.status,
        chunk_type=args.type,
        search_query=args.search,
        limit=args.limit,
    )
    if not chunks:
        print("No matching chunks found.")
        return
    print(f"Showing {len(chunks)} chunks:")
    print("-" * 100)
    for c in chunks:
        code_str = f"[{c['code']}] " if c.get("code") else ""
        print(f"Chunk ID: {c['id']} | Status: {c['review_status']} | Type: {c['chunk_type']}")
        print(f"  Path: {c['breadcrumb']}")
        txt = (c.get("edited_text") or c["source_text"]).replace("\n", " ")
        print(f"  Text: {code_str}{txt[:120]}...")
        print("-" * 100)


def cmd_edit(args):
    res = StagingService.update_chunk(
        chunk_id=args.chunk_id,
        edited_text=args.text,
        change_reason=args.reason or "CLI edit",
        user=args.user,
    )
    print(f"[OK] Chunk {args.chunk_id} updated to revision {res['revision']} (Status: APPROVED)")


def cmd_review(args):
    res = StagingService.review_chunk(
        chunk_id=args.chunk_id,
        action=args.action,
        user=args.user,
    )
    print(f"[OK] Chunk {args.chunk_id} reviewed: {res['review_status']}")


def cmd_approve_all(args):
    res = StagingService.review_all_chunks(
        doc_id=args.doc_id,
        action="APPROVE",
        user=args.user,
    )
    print(f"[OK] Approved {res['updated_count']} pending chunks for document {args.doc_id}")


def cmd_snapshot(args):
    try:
        res = StagingService.create_approved_snapshot(
            doc_id=args.doc_id,
            user=args.user,
        )
        print(f"[OK] Approved Snapshot Created!")
        print(f"     Snapshot ID:    {res['snapshot_id']}")
        print(f"     Total Records:  {res['total_records']}")
        print(f"     SHA-256 Hash:   {res['snapshot_hash']}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="TradeRAG Staging CLI Review Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # upload
    p_upload = subparsers.add_parser("upload", help="Upload and parse a DOCX file")
    p_upload.add_argument("file", help="Path to DOCX file")
    p_upload.add_argument("--doc-no", help="Document number (e.g. 02/2024/TT-BTTTT)")
    p_upload.add_argument("--type", help="Explicit document type")
    p_upload.add_argument("--user", default="cli_admin", help="User name")
    p_upload.set_defaults(func=cmd_upload)

    # list
    p_list = subparsers.add_parser("list", help="List staged documents")
    p_list.add_argument("--status", help="Filter by status (PARSED, IN_REVIEW, APPROVED, etc.)")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    # info
    p_info = subparsers.add_parser("info", help="Get details of a staged document")
    p_info.add_argument("doc_id", help="Document UUID")
    p_info.set_defaults(func=cmd_info)

    # chunks
    p_chunks = subparsers.add_parser("chunks", help="List chunks for a staged document")
    p_chunks.add_argument("doc_id", help="Document UUID")
    p_chunks.add_argument("--status", help="Filter by review status")
    p_chunks.add_argument("--type", help="Filter by chunk type")
    p_chunks.add_argument("--search", help="Search text or code")
    p_chunks.add_argument("--limit", type=int, default=15)
    p_chunks.set_defaults(func=cmd_chunks)

    # edit
    p_edit = subparsers.add_parser("edit", help="Edit a chunk's text")
    p_edit.add_argument("chunk_id", help="Chunk ID")
    p_edit.add_argument("--text", required=True, help="New edited text")
    p_edit.add_argument("--reason", default="Manual review edit", help="Change reason")
    p_edit.add_argument("--user", default="cli_admin", help="User name")
    p_edit.set_defaults(func=cmd_edit)

    # review
    p_review = subparsers.add_parser("review", help="Approve or Exclude a single chunk")
    p_review.add_argument("chunk_id", help="Chunk ID")
    p_review.add_argument("action", choices=["APPROVE", "EXCLUDE", "NEEDS_REVIEW"])
    p_review.add_argument("--user", default="cli_admin", help="User name")
    p_review.set_defaults(func=cmd_review)

    # approve-all
    p_app_all = subparsers.add_parser("approve-all", help="Approve all pending chunks in a document")
    p_app_all.add_argument("doc_id", help="Document UUID")
    p_app_all.add_argument("--user", default="cli_admin", help="User name")
    p_app_all.set_defaults(func=cmd_approve_all)

    # snapshot
    p_snap = subparsers.add_parser("snapshot", help="Create approved snapshot ready for ingestion")
    p_snap.add_argument("doc_id", help="Document UUID")
    p_snap.add_argument("--user", default="cli_admin", help="User name")
    p_snap.set_defaults(func=cmd_snapshot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
