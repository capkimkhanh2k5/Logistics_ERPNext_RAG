"""Unit and regression tests for Unified DOCX Parser Core."""

import pytest
from pathlib import Path
from config.settings import ROOT
from rag.ingestion.docx import (
    DocType,
    NodeType,
    UnifiedDOCXParser,
)

FIXTURE_DIR = ROOT / "data/raw/docx"


def test_parser_extracts_hs_nomenclature_section_xiv():
    file_path = FIXTURE_DIR / "TT31-Section-XIV.docx"
    assert file_path.is_file(), f"Fixture missing: {file_path}"

    result = UnifiedDOCXParser.parse_file(file_path, document_no="31/2022/TT-BTC")
    assert result.document_type == DocType.HS_NOMENCLATURE
    assert len(result.nodes) > 50
    assert len(result.chunks) > 50

    # Ensure zero critical validation issues
    criticals = [i for i in result.validation_issues if i.severity.value == "CRITICAL"]
    assert len(criticals) == 0

    # Check AHTN 8-digit codes preservation
    ahtn_chunks = [c for c in result.chunks if c.level == 8 and c.code]
    assert len(ahtn_chunks) > 0
    for chunk in ahtn_chunks:
        assert len(chunk.code) == 8
        assert chunk.code.isdigit()
        assert "Chương" in chunk.breadcrumb or "Nhóm" in chunk.breadcrumb
        assert len(chunk.embedding_text) > 20


def test_parser_extracts_product_catalog_tt02():
    file_path = FIXTURE_DIR / "02_2024_TT-BTTTT_m_605048.docx"
    assert file_path.is_file(), f"Fixture missing: {file_path}"

    result = UnifiedDOCXParser.parse_file(file_path, document_no="02/2024/TT-BTTTT")
    assert result.document_type == DocType.PRODUCT_CATALOG
    assert len(result.chunks) > 100

    # Ensure technical standard chunks exist
    tech_chunks = [c for c in result.chunks if c.chunk_type.value == "technical_standard_item"]
    assert len(tech_chunks) > 100

    # Check that multi-code cells generated distinct 8-digit codes
    codes = {c.code for c in tech_chunks if c.code}
    assert "85171300" in codes
    assert "85171400" in codes


def test_parser_extracts_legal_provisions_nd26():
    file_path = FIXTURE_DIR / "26_2023_ND-CP_548616.docx"
    assert file_path.is_file(), f"Fixture missing: {file_path}"

    result = UnifiedDOCXParser.parse_file(file_path, document_no="26/2023/ND-CP")
    assert len(result.chunks) > 50

    # Verify Article -> Clause hierarchy
    articles = [n for n in result.nodes if n.node_type == NodeType.ARTICLE]
    clauses = [n for n in result.nodes if n.node_type == NodeType.CLAUSE]
    assert len(articles) >= 10
    assert len(clauses) >= 30

    dieu_1 = next((a for a in articles if a.code == "1"), None)
    assert dieu_1 is not None
    assert "Phạm vi điều chỉnh" in dieu_1.title


def test_parser_fails_gracefully_on_missing_file():
    with pytest.raises(FileNotFoundError):
        UnifiedDOCXParser.parse_file(FIXTURE_DIR / "non_existent_file.docx")
