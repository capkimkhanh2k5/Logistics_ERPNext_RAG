"""Validate canonical sources, PDF provenance and evaluation separation."""

import hashlib

import jsonschema

from config.settings import ROOT
from rag.graph.legal_evidence import evidence_digest
from rag.ingestion.pdf_graph import extractor_identity
from rag.ingestion.pdf_wording import review_processor, review_records
from rag.ingestion.provenance import same_processor
from rag.ingestion.sources import (
    GOLD,
    NORMALIZED,
    canonical_edge,
    canonical_tariff,
    first,
    source_files,
    source_manifest,
    source_path,
)
from rag.utils.files import read


def audit() -> dict:
    data = source_files()
    registered = source_manifest(ROOT)
    repairs = {r["id"]: r for r in data.get("tt31_pdf_text_corrections", {}).get("records", [])}
    verified_repairs = set()
    registry = data["tt31_pdf_wording_reviews"]
    reviews = review_records(registry)
    verified_reviews = set()
    if data["tt31_pdf_graph"].get("version") != 2:
        raise ValueError("PDF source graph must be rebuilt with the current extractor")
    for name, extraction in data["tt31_pdf_graph"].get("extractions", {}).items():
        if not same_processor(extraction.get("extractor"), extractor_identity()):
            raise ValueError(f"PDF graph extractor is stale: {name}")
        if data["pdf_provenance"].get("extractors", {}).get(name) != extraction["extractor"]:
            raise ValueError(f"PDF source provenance extractor is stale: {name}")
        expected_reviews = {rid for rid, r in reviews.items() if r["locator"]["document"] == name}
        review_proof = extraction.get("wording_reviews", {})
        if (
            review_proof.get("registry_hash") != evidence_digest(registry)
            or not same_processor(review_proof.get("processor"), review_processor())
            or set(review_proof.get("ids", [])) != expected_reviews
            or len(review_proof.get("ids", [])) != len(expected_reviews)
            or data["pdf_provenance"].get("wording_reviews", {}).get(name) != review_proof
        ):
            raise ValueError(f"PDF wording review provenance is stale: {name}")
    validator = jsonschema.Draft202012Validator(data["tt31_unified_rag_schema"])
    taxonomy = {r["chapter_code"]: r["section_code"] for r in data["scope"]["records"]}
    quality, codes = {}, set()
    broken: list[dict] = []
    all_ids = set()
    graph_edges = 0
    for source in registered["tariffs"]:
        records = data[source["records"]]
        masters = {first(r, "id", "record_id"): r for r in data.get(source.get("master"), [])}
        ids = {r["id"] for r in records}
        if len(ids) != len(records):
            raise ValueError("Duplicate tariff source IDs")
        for r in records:
            validator.validate(r)
            review_id = "tt31:" + r["id"]
            review = reviews.get(review_id)
            if review:
                canonical = canonical_tariff(r, masters.get(r["id"]))
                proof = data["pdf_provenance"]["records"].get(review_id, {})
                expected = {
                    **review["locator"],
                    "raw_pdf_text": review["native_pdf_text"],
                    "reviewed_pdf_text": review["reviewed_row_text"],
                    "wording_review_id": review_id,
                    "wording_review_hash": evidence_digest(review),
                    "source_text_hash": evidence_digest(review["source_text"]),
                    "wording_status": "VISUALLY_VERIFIED_COMPLETE_MATCH",
                }
                if canonical["source_text"] != review["source_text"] or any(
                    proof.get(k) != v for k, v in expected.items()
                ):
                    raise ValueError(f"Reviewed PDF source wording drifted: {review_id}")
                verified_reviews.add(review_id)
            repair = repairs.get("tt31:" + r["id"])
            if repair:
                canonical = canonical_tariff(r, masters.get(r["id"]))
                if canonical["source_text"] != repair["corrected_source_text"]:
                    raise ValueError(f"PDF source text repair drifted: {r['id']}")
                pdf = ROOT / "data/raw" / repair["locator"]["document"]
                if hashlib.sha256(pdf.read_bytes()).hexdigest() != repair["locator"]["sha256"]:
                    raise ValueError(f"PDF repair authority changed: {r['id']}")
                verified_repairs.add(repair["id"])
            md = r["metadata"]
            if md.get("chapter") and taxonomy.get(md["chapter"]) != md["section"]:
                raise ValueError(f"Source Section/Chapter mismatch: {r['id']}")
            if r["id"] != r["source_id"] or r["text"] != r["content"]["embedding_text"]:
                raise ValueError(f"Inconsistent canonical source record: {r['id']}")
            if not r["text"].strip() or not r["provenance"]:
                raise ValueError(f"Missing source text or provenance: {r['id']}")
            code = first(md, "code_compact", "code")
            if code:
                codes.add(str(code).replace(".", ""))
        for n in data.get(source.get("nodes"), []):
            ids.add(first(n, "node_id", "id", "record_id"))
        all_ids.update(ids)
        edges = [canonical_edge(e, "") for e in data.get(source.get("edges"), [])]
        graph_edges += len(edges)
        broken.extend(e for e in edges if e["source"] not in ids or e["target"] not in ids)
        quality[source["records"]] = {
            "count": len(records),
            "duplicate_wording": len(records) - len({r["text"] for r in records}),
            "short_ids": [r["id"] for r in records if len(r["text"]) < 40],
        }
    if broken:
        raise ValueError("Broken source graph endpoints")
    if verified_repairs != set(repairs):
        raise ValueError("A reviewed PDF source repair has no registered record")
    if verified_reviews != set(reviews):
        raise ValueError("A PDF wording review has no registered canonical source")
    for key, id_field, text_field in [("gir", "id", "text_vi"), ("tt85", "chunk_id", "text")]:
        rows = data[key]
        if len({r[id_field] for r in rows}) != len(rows) or any(
            not r[text_field].strip() for r in rows
        ):
            raise ValueError(f"Invalid legal source records: {key}")
        quality[key] = {
            "count": len(rows),
            "duplicate_wording": len(rows) - len({r[text_field] for r in rows}),
            "short_ids": [r[id_field] for r in rows if len(r[text_field]) < 40],
        }
    gold = [r for path in sorted((GOLD / "hs").glob("*.jsonl")) for r in read(path)]
    from rag.ingestion.legal_documents import legal_document_bundle

    for spec in registered.get("legal_documents", []):
        records, _, _ = legal_document_bundle(ROOT, spec)
        quality[spec["dataset"]] = {
            "count": len(records),
            "raw_sha256": spec["sha256"],
            "legal_status": spec["legal_status"],
        }
    for relative, expected in data["pdf_provenance"]["pdf_hashes"].items():
        if hashlib.sha256(source_path(ROOT, relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Authoritative PDF source hash mismatch: {relative}")
    return {
        "quality": quality,
        "scope_count": len(taxonomy),
        "graph_nodes": len(all_ids),
        "graph_edges": graph_edges,
        "broken_endpoints": [],
        "gold_count": len(gold),
        "unique_gold_codes": len({g["expected_hs_8"] for g in gold}),
        "gold_missing": [r["record_id"] for r in gold if r["expected_hs_8"] not in codes],
        "tt85_source_hash_matches": True,
        "legal_verification": "MIXED_PDF_REVIEW_AND_HASH_BOUND_LOCAL_DOCX"
        if registered.get("legal_documents")
        else "PDF_HASH_BOUND_WITH_TEXT_COMPARISON_AND_OCR_REVIEW_LIMITATIONS",
        "pdf_verification": "PDF_HASH_BOUND_WITH_TEXT_COMPARISON_AND_OCR_REVIEW_LIMITATIONS",
        "docx_verification": "RAW_DOCX_HASH_BOUND_NOT_PDF_VERIFIED",
        "verified_pdf_text_repairs": len(verified_repairs),
        "verified_pdf_wording_reviews": len(verified_reviews),
        "reviewed_canonical_text_changes": sum(r["source_text_changed"] for r in reviews.values()),
        "source_hashes": {
            **{spec["file"]: spec["sha256"] for spec in registered.get("legal_documents", [])},
            **{
                path: hashlib.sha256(source_path(NORMALIZED, path).read_bytes()).hexdigest()
                for path in registered["files"].values()
            },
        },
    }
