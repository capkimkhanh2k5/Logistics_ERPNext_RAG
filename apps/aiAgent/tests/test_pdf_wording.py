"""Image-reviewed wording must retain complete, immutable source authority."""

import copy

import pytest

from config.settings import ROOT
from rag.chunking.corpus import load_corpus
from rag.graph.legal_evidence import evidence_digest
from rag.ingestion.audit import audit
from rag.ingestion.pdf_graph import extractor_identity
from rag.ingestion.pdf_wording import (
    apply_wording_reviews,
    validate_reviewed_extraction,
    wording_proof,
)
from rag.utils.files import read


def fixture():
    locator = {
        "document": "new.pdf",
        "sha256": "a" * 64,
        "physical_page": 2,
        "bbox": [10, 20, 30, 40],
        "continuations": [{"physical_page": 3, "bbox": [10, 1, 30, 12]}],
    }
    native = "- Công suất không quá 7 kVA"
    source = "Công suất không quá 75 kVA (SEN) (*)"
    rows = [{"code": "990110", "text_vi": native, "locator": locator, "depth": 1}]
    extraction = {
        "document": "new.pdf",
        "sha256": "a" * 64,
        "extractor": extractor_identity(),
        "rows_hash": evidence_digest(rows),
        "pages": [{"status": "EXTRACTED"}],
        "code_inventory": [{"code": "990110", "physical_page": 2}],
    }
    registry = {
        "version": 1,
        "records": [
            {
                "id": "source:new",
                "code": "990110",
                "status": "VISUALLY_VERIFIED",
                "locator": copy.deepcopy(locator),
                "native_pdf_text": native,
                "reviewed_row_text": "- " + source,
                "source_text": source,
            }
        ],
    }
    return rows, extraction, registry


def test_transcription_retains_native_layer_and_complete_multipage_authority():
    rows, extraction, registry = fixture()
    reviewed, proof = apply_wording_reviews(rows, extraction, registry)
    assert reviewed[0]["native_text_vi"] == rows[0]["text_vi"]
    assert reviewed[0]["text_vi"] == registry["records"][0]["reviewed_row_text"]
    assert proof["native_rows_hash"] == extraction["rows_hash"]
    assert reviewed[0]["locator"]["continuations"] == rows[0]["locator"]["continuations"]
    validate_reviewed_extraction(reviewed, proof, "a" * 64, registry)
    result = wording_proof(
        reviewed[0],
        {"id": "source:new", "source_text": registry["records"][0]["source_text"]},
        registry,
    )
    assert result["wording_status"] == "VISUALLY_VERIFIED_COMPLETE_MATCH"
    assert "75 kVA (SEN) (*)" in result["reviewed_pdf_text"]


@pytest.mark.parametrize(
    "change", ["pdf", "code", "page", "continuation", "native", "duplicate", "missing"]
)
def test_review_cannot_be_reused_for_a_different_source(change):
    rows, extraction, registry = fixture()
    record = registry["records"][0]
    if change == "pdf":
        record["locator"]["sha256"] = "b" * 64
    elif change == "code":
        record["code"] = "990120"
    elif change == "page":
        record["locator"]["physical_page"] += 1
    elif change == "continuation":
        record["locator"].pop("continuations")
    elif change == "native":
        record["native_pdf_text"] += " changed"
    elif change == "duplicate":
        registry["records"].append(copy.deepcopy(record))
    elif change == "missing":
        rows.clear()
        extraction["rows_hash"] = evidence_digest(rows)
        extraction["code_inventory"] = []
    with pytest.raises(ValueError):
        apply_wording_reviews(rows, extraction, registry)


@pytest.mark.parametrize(
    "change", ["quantity", "negation", "note", "transcript", "registry", "processor"]
)
def test_reviewed_extraction_rejects_wording_or_provenance_drift(change):
    rows, extraction, registry = fixture()
    reviewed, proof = apply_wording_reviews(rows, extraction, registry)
    if change == "quantity":
        reviewed[0]["text_vi"] = reviewed[0]["text_vi"].replace("75", "750")
    elif change == "negation":
        reviewed[0]["text_vi"] = reviewed[0]["text_vi"].replace("không quá", "trên")
    elif change == "note":
        reviewed[0]["text_vi"] = reviewed[0]["text_vi"].replace("(SEN)", "")
    elif change == "transcript":
        registry["records"][0]["reviewed_row_text"] += " extra"
    elif change == "registry":
        registry["new_review"] = "changed"
    elif change == "processor":
        proof["wording_reviews"]["processor"]["version"] = "old"
    with pytest.raises(ValueError):
        validate_reviewed_extraction(reviewed, proof, "a" * 64, registry)


def test_reviewed_source_requires_exact_canonical_text_even_when_tokens_match():
    rows, extraction, registry = fixture()
    reviewed, _ = apply_wording_reviews(rows, extraction, registry)
    source = registry["records"][0]["source_text"].replace("(*)", "(4)")
    with pytest.raises(ValueError, match="canonical source wording drifted"):
        wording_proof(reviewed[0], {"id": "source:new", "source_text": source}, registry)


def test_all_205_reviewed_rows_are_used_by_corpus_without_changing_product_rules():
    registry = read(ROOT / "data/normalized/TT31/PDF_WORDING_REVIEWS.json")
    records = {r["id"]: r for r in load_corpus()["records"]}
    assert len(registry["records"]) == 205
    assert sum(r["source_text_changed"] for r in registry["records"]) == 4
    for review in registry["records"]:
        record = records[review["id"]]
        assert record["source_text"] == review["source_text"]
        assert record["source_text"] in record["embedding_text"]
        assert record["locator"]["raw_pdf_text"] == review["native_pdf_text"]
        assert record["locator"]["reviewed_pdf_text"] == review["reviewed_row_text"]
        assert record["locator"]["wording_status"] == "VISUALLY_VERIFIED_COMPLETE_MATCH"
    assert audit()["verified_pdf_wording_reviews"] == 205
