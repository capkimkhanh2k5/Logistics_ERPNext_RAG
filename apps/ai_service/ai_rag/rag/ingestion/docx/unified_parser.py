"""Unified DOCX Parser Facade.
Coordinates OpenXML reading, document type detection, specialized parsing, chunking, and validation.
"""

import uuid
from pathlib import Path
from typing import Optional, Union

from rag.ingestion.docx.ast_models import (
    ASTNode,
    DocType,
    ParsedDocumentResult,
    ValidationIssue,
    ValidationSeverity,
)
from rag.ingestion.docx.atomic_chunker import AtomicChunker
from rag.ingestion.docx.catalog_parser import CatalogParser
from rag.ingestion.docx.document_detector import DocumentDetector
from rag.ingestion.docx.hs_parser import HSParser
from rag.ingestion.docx.legal_parser import LegalParser
from rag.ingestion.docx.openxml_reader import OpenXMLReader
from rag.ingestion.docx.validators import StructuralValidator


class UnifiedDOCXParser:
    """Master orchestrator for ingesting any Vietnamese legal or tariff DOCX document."""

    @classmethod
    def parse_file(
        cls,
        file_path: Union[str, Path],
        explicit_type: Optional[str] = None,
        document_no: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> ParsedDocumentResult:
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        # 1. Read OpenXML package
        pkg = OpenXMLReader.read_docx(path)
        doc_id = document_id or str(uuid.uuid4())

        # 2. Detect Document Type
        doc_type, confidence, hints = DocumentDetector.detect(pkg, explicit_type)

        # 3. Dispatch to specialized parser with fallback chain
        nodes: list[ASTNode] = []
        if doc_type in (DocType.HS_NOMENCLATURE, DocType.TARIFF_SCHEDULE):
            nodes = HSParser.parse(pkg)
            if not nodes:
                nodes = LegalParser.parse(pkg)
            if not nodes:
                nodes = CatalogParser.parse(pkg)
        elif doc_type == DocType.PRODUCT_CATALOG:
            nodes = CatalogParser.parse(pkg)
            if not nodes:
                nodes = LegalParser.parse(pkg)
        else:
            nodes = LegalParser.parse(pkg)
            if not nodes:
                nodes = CatalogParser.parse(pkg)
            if not nodes:
                nodes = HSParser.parse(pkg)

        # 4. Generate Atomic Chunks
        chunks = AtomicChunker.chunk_nodes(
            nodes=nodes,
            document_id=doc_id,
            document_type=doc_type,
            document_no=document_no,
        )

        # 5. Validate AST and Chunks
        issues = StructuralValidator.validate(nodes, chunks)

        return ParsedDocumentResult(
            filename=pkg.filename,
            file_sha256=pkg.sha256,
            document_type=doc_type,
            document_no=document_no,
            nodes=nodes,
            chunks=chunks,
            validation_issues=issues,
            metadata={
                "detection_confidence": confidence,
                "detection_hints": hints,
                "document_id": doc_id,
            },
        )
