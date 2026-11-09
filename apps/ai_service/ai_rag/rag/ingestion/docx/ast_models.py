"""Normalized Abstract Syntax Tree (AST) and Chunk Data Models for DOCX Ingestion."""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class DocType(str, Enum):
    HS_NOMENCLATURE = "HS_NOMENCLATURE"
    TARIFF_SCHEDULE = "TARIFF_SCHEDULE"
    LEGAL_DOCUMENT = "LEGAL_DOCUMENT"
    TECHNICAL_STANDARD = "TECHNICAL_STANDARD"
    PRODUCT_CATALOG = "PRODUCT_CATALOG"
    UNKNOWN = "UNKNOWN"


class NodeType(str, Enum):
    DOCUMENT = "DOCUMENT"
    PART = "PART"
    CHAPTER = "CHAPTER"
    SECTION_NOTE = "SECTION_NOTE"
    CHAPTER_NOTE = "CHAPTER_NOTE"
    SUBHEADING_NOTE = "SUBHEADING_NOTE"
    HEADING = "HEADING"
    SUBHEADING = "SUBHEADING"
    AHTN_ENTRY = "AHTN_ENTRY"
    ARTICLE = "ARTICLE"
    CLAUSE = "CLAUSE"
    POINT = "POINT"
    ANNEX = "ANNEX"
    TABLE = "TABLE"
    TABLE_HEADER = "TABLE_HEADER"
    GROUP_ROW = "GROUP_ROW"
    DATA_ROW = "DATA_ROW"
    PARAGRAPH = "PARAGRAPH"


class ChunkType(str, Enum):
    TARIFF_ENTRY = "tariff_entry"
    SECTION_NOTE = "section_note"
    CHAPTER_NOTE = "chapter_note"
    SUBHEADING_NOTE = "subheading_note"
    TARIFF_FOOTNOTE = "tariff_footnote"
    LEGAL_CLAUSE = "legal_clause"
    TECHNICAL_STANDARD_ITEM = "technical_standard_item"


class ReviewStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    EXCLUDED = "EXCLUDED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class SourceLocation:
    part: str = "word/document.xml"
    block_index: int = 0
    sub_index: Optional[int] = None
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    col_index: Optional[int] = None
    page_hint: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    code: str
    message: str
    target_id: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "target_id": self.target_id,
            "context": self.context,
        }


@dataclass
class ASTNode:
    id: str
    node_type: NodeType
    node_level: int
    node_order: int
    canonical_anchor: Optional[str] = None
    code: Optional[str] = None
    title: Optional[str] = None
    source_text: str = ""
    source_location: SourceLocation = field(default_factory=SourceLocation)
    breadcrumb: str = ""
    parent_id: Optional[str] = None
    children: list["ASTNode"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_children: bool = False) -> dict[str, Any]:
        res = {
            "id": self.id,
            "node_type": self.node_type.value,
            "node_level": self.node_level,
            "node_order": self.node_order,
            "canonical_anchor": self.canonical_anchor,
            "code": self.code,
            "title": self.title,
            "source_text": self.source_text,
            "source_location": self.source_location.to_dict(),
            "breadcrumb": self.breadcrumb,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
        }
        if include_children:
            res["children"] = [child.to_dict(include_children=True) for child in self.children]
        return res


@dataclass
class ParsedChunk:
    chunk_id: str
    document_id: str
    node_id: str
    chunk_index: int
    chunk_type: ChunkType
    canonical_anchor: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None
    role: str = "candidate"  # candidate, evidence, context, scope
    namespace: str = "hs_classification"  # hs_classification, legal_classification
    source_text: str = ""
    edited_text: Optional[str] = None
    breadcrumb: str = ""
    embedding_text: str = ""
    lexical_text: str = ""
    source_location: SourceLocation = field(default_factory=SourceLocation)
    review_status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    confidence_score: float = 1.0
    validation_issues: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "node_id": self.node_id,
            "chunk_index": self.chunk_index,
            "chunk_type": self.chunk_type.value,
            "canonical_anchor": self.canonical_anchor,
            "code": self.code,
            "level": self.level,
            "role": self.role,
            "namespace": self.namespace,
            "source_text": self.source_text,
            "edited_text": self.edited_text,
            "breadcrumb": self.breadcrumb,
            "embedding_text": self.embedding_text,
            "lexical_text": self.lexical_text,
            "source_location": self.source_location.to_dict(),
            "review_status": self.review_status.value,
            "confidence_score": self.confidence_score,
            "validation_issues": [issue.to_dict() for issue in self.validation_issues],
            "metadata": self.metadata,
        }


@dataclass
class ParsedDocumentResult:
    filename: str
    file_sha256: str
    document_type: DocType
    document_no: Optional[str] = None
    title: Optional[str] = None
    nodes: list[ASTNode] = field(default_factory=list)
    chunks: list[ParsedChunk] = field(default_factory=list)
    validation_issues: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "file_sha256": self.file_sha256,
            "document_type": self.document_type.value,
            "document_no": self.document_no,
            "title": self.title,
            "total_nodes": len(self.nodes),
            "total_chunks": len(self.chunks),
            "critical_issues": sum(
                1 for i in self.validation_issues if i.severity == ValidationSeverity.CRITICAL
            ),
            "warnings": sum(
                1 for i in self.validation_issues if i.severity == ValidationSeverity.WARNING
            ),
        }
