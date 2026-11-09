"""Unified DOCX Parser and Staging Engine."""

from rag.ingestion.docx.ast_models import (
    ASTNode,
    ChunkType,
    DocType,
    NodeType,
    ParsedChunk,
    ParsedDocumentResult,
    ReviewStatus,
    SourceLocation,
    ValidationIssue,
    ValidationSeverity,
)
from rag.ingestion.docx.atomic_chunker import AtomicChunker
from rag.ingestion.docx.catalog_parser import CatalogParser
from rag.ingestion.docx.document_detector import DocumentDetector
from rag.ingestion.docx.hs_parser import HSParser
from rag.ingestion.docx.legal_parser import LegalParser
from rag.ingestion.docx.openxml_reader import OpenXMLReader, RawDocumentPackage
from rag.ingestion.docx.unified_parser import UnifiedDOCXParser
from rag.ingestion.docx.validators import StructuralValidator

__all__ = [
    "DocType",
    "NodeType",
    "ChunkType",
    "ReviewStatus",
    "ValidationSeverity",
    "SourceLocation",
    "ValidationIssue",
    "ASTNode",
    "ParsedChunk",
    "ParsedDocumentResult",
    "OpenXMLReader",
    "RawDocumentPackage",
    "DocumentDetector",
    "HSParser",
    "LegalParser",
    "CatalogParser",
    "AtomicChunker",
    "StructuralValidator",
    "UnifiedDOCXParser",
]
