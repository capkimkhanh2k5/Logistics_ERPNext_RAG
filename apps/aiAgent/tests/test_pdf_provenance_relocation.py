"""Moving processors must preserve old proofs without accepting unrelated code drift."""

import ast
import copy
import hashlib

import pytest

from config.settings import ROOT
from rag.ingestion.pdf_graph import extractor_identity
from rag.ingestion.pdf_wording import (
    apply_wording_reviews,
    review_processor,
    validate_reviewed_extraction,
)
from rag.ingestion.provenance import same_processor
from rag.utils.files import read
from tests.test_pdf_wording import fixture

RELOCATIONS = read(ROOT / "rag/ingestion/provenance_relocations.json")["processors"]


@pytest.mark.parametrize("relocation", RELOCATIONS, ids=["pdf-parser", "wording-review"])
def test_relocation_is_bound_to_exact_source_and_preserved_processing(relocation):
    path = ROOT / relocation["after_path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == relocation["after_sha256"]
    definitions = {
        node.name: ast.dump(node, include_attributes=False)
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.FunctionDef)
    }
    for name, expected in relocation["preserved_definitions"].items():
        assert hashlib.sha256(definitions[name].encode()).hexdigest() == expected


@pytest.mark.parametrize("relocation", RELOCATIONS, ids=["pdf-parser", "wording-review"])
def test_relocation_accepts_original_identity_but_rejects_code_or_version_drift(relocation):
    identity = (
        extractor_identity() if relocation["hash_field"] == "parser_sha256" else review_processor()
    )
    recorded = {**identity, relocation["hash_field"]: relocation["before_sha256"]}
    assert same_processor(recorded, identity)
    assert not same_processor(recorded, {**identity, relocation["hash_field"]: "0" * 64})
    assert not same_processor(recorded, {**identity, "version": "different-algorithm"})
    assert not same_processor(recorded, {**identity, "extra": True})
    assert not same_processor(None, identity)
    if "pymupdf_version" in identity:
        assert not same_processor(recorded, {**identity, "pymupdf_version": "different-library"})


def test_original_pdf_and_review_proofs_validate_without_rewriting_them():
    rows, extraction, registry = fixture()
    reviewed, proof = apply_wording_reviews(rows, extraction, registry)
    proof["extractor"]["parser_sha256"] = RELOCATIONS[0]["before_sha256"]
    proof["wording_reviews"]["processor"]["sha256"] = RELOCATIONS[1]["before_sha256"]
    original = copy.deepcopy((reviewed, proof, registry))
    validate_reviewed_extraction(reviewed, proof, "a" * 64, registry)
    assert (reviewed, proof, registry) == original
