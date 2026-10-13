"""Apply image-reviewed transcriptions without discarding the native PDF text layer."""

import copy
import hashlib
from pathlib import Path

from rag.legal_evidence import evidence_digest, normalized_wording
from rag.pdf_graph import validate_extraction


def review_processor() -> dict:
    return {
        "version": "image-reviewed-transcription-v1",
        "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def review_records(registry: dict) -> dict[str, dict]:
    if registry.get("version") != 1:
        raise ValueError("Unsupported PDF wording review registry")
    records = registry["records"]
    by_id = {r["id"]: r for r in records}
    anchors = {(r["locator"]["document"], r["code"]) for r in records}
    if len(by_id) != len(records) or len(anchors) != len(records):
        raise ValueError("Duplicate PDF wording review authority")
    for record in records:
        if record.get("status") != "VISUALLY_VERIFIED" or not record.get("reviewed_row_text"):
            raise ValueError(f"Unverified PDF wording review: {record['id']}")
        if normalized_wording(record["source_text"]) != normalized_wording(
            record["reviewed_row_text"]
        ):
            raise ValueError(f"Incomplete reviewed PDF wording: {record['id']}")
    return by_id


def apply_wording_reviews(
    rows: list[dict], extraction: dict, registry: dict
) -> tuple[list[dict], dict]:
    """Pin each complete transcription to its PDF, code, cell geometry and native text."""
    validate_extraction(rows, extraction, extraction["sha256"])
    reviewed_rows, reviewed_extraction = copy.deepcopy(rows), copy.deepcopy(extraction)
    applicable = {
        r["code"]: r
        for r in review_records(registry).values()
        if r["locator"]["document"] == extraction["document"]
    }
    applied = []
    for row in reviewed_rows:
        review = applicable.get(row.get("code"))
        if review is None:
            continue
        if row["locator"] != review["locator"]:
            raise ValueError(f"Reviewed PDF locator drifted: {review['id']}")
        if row["text_vi"] != review["native_pdf_text"]:
            raise ValueError(f"Reviewed PDF native text drifted: {review['id']}")
        row["native_text_vi"] = row["text_vi"]
        row["text_vi"] = review["reviewed_row_text"]
        row["wording_review_id"] = review["id"]
        applied.append(review["id"])
    if len(applied) != len(applicable) or len(set(applied)) != len(applied):
        raise ValueError("A PDF wording review has no unique extracted row")
    reviewed_extraction.update(
        native_rows_hash=extraction["rows_hash"],
        rows_hash=evidence_digest(reviewed_rows),
        wording_reviews={
            "registry_hash": evidence_digest(registry),
            "processor": review_processor(),
            "ids": applied,
        },
    )
    return reviewed_rows, reviewed_extraction


def validate_reviewed_extraction(
    rows: list[dict], extraction: dict, pdf_sha256: str, registry: dict
) -> None:
    native_rows = copy.deepcopy(rows)
    for row in native_rows:
        if "wording_review_id" in row:
            row["text_vi"] = row.pop("native_text_vi")
            row.pop("wording_review_id")
    native_extraction = copy.deepcopy(extraction)
    native_extraction["rows_hash"] = native_extraction.pop("native_rows_hash")
    native_extraction.pop("wording_reviews")
    validate_extraction(native_rows, native_extraction, pdf_sha256)
    expected_rows, expected_extraction = apply_wording_reviews(
        native_rows, native_extraction, registry
    )
    if rows != expected_rows or extraction != expected_extraction:
        raise ValueError("Reviewed PDF extraction or review registry drifted")


def wording_proof(row: dict, record: dict, registry: dict) -> dict:
    review_id = row.get("wording_review_id")
    if review_id:
        review = review_records(registry)[review_id]
        if record["id"] != review_id or record["source_text"] != review["source_text"]:
            raise ValueError(f"Reviewed canonical source wording drifted: {review_id}")
    match = normalized_wording(record["source_text"]) == normalized_wording(row["text_vi"])
    proof = {
        "raw_pdf_text": row.get("native_text_vi", row["text_vi"]),
        "wording_status": "VISUALLY_VERIFIED_COMPLETE_MATCH"
        if review_id and match
        else "NORMALIZED_COMPLETE_MATCH"
        if match
        else "REQUIRES_OCR_WORDING_REVIEW",
    }
    if review_id:
        proof.update(
            reviewed_pdf_text=row["text_vi"],
            wording_review_id=review_id,
            wording_review_hash=evidence_digest(review),
            source_text_hash=evidence_digest(record["source_text"]),
        )
    return proof
