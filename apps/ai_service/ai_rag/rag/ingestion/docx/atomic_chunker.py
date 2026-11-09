"""Converts normalized AST nodes into Atomic Chunks with contextual breadcrumbs and metadata.
Prepares records for PostgreSQL Staging and downstream BGE-M3 embedding.
"""

import hashlib
import re
from typing import Optional

from rag.ingestion.docx.ast_models import (
    ASTNode,
    ChunkType,
    DocType,
    NodeType,
    ParsedChunk,
    ReviewStatus,
)


class AtomicChunker:
    """Transforms structural AST nodes into semantic, self-contained atomic chunks."""

    @classmethod
    def chunk_nodes(
        cls,
        nodes: list[ASTNode],
        document_id: str,
        document_type: DocType,
        document_no: Optional[str] = None,
    ) -> list[ParsedChunk]:
        chunks: list[ParsedChunk] = []
        chunk_idx = 0

        # Quick lookup for parent breadcrumbs
        node_map = {n.id: n for n in nodes}

        for node in nodes:
            # Skip pure structural container nodes that have children and don't hold leaf content
            if node.node_type in (NodeType.DOCUMENT, NodeType.PART, NodeType.GROUP_ROW):
                continue

            chunk_type, role, namespace = cls._classify_chunk_type(node, document_type)
            if chunk_type is None:
                continue

            chunk_idx += 1
            chunk_id = f"{document_id}:{node.id}"

            # Compose rich embedding text containing complete ancestral breadcrumbs
            doc_prefix = document_no or "Tài liệu"
            embedding_parts = [
                doc_prefix,
                node.breadcrumb,
                node.source_text,
            ]
            embedding_text = " | ".join(p.strip() for p in embedding_parts if p and p.strip())

            # Lexical text mirrors embedding text for full-text search
            lexical_text = embedding_text

            chunk = ParsedChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                node_id=node.id,
                chunk_index=chunk_idx,
                chunk_type=chunk_type,
                canonical_anchor=node.canonical_anchor,
                code=node.code,
                level=node.node_level,
                role=role,
                namespace=namespace,
                source_text=node.source_text,
                breadcrumb=node.breadcrumb,
                embedding_text=embedding_text,
                lexical_text=lexical_text,
                source_location=node.source_location,
                review_status=ReviewStatus.PENDING_REVIEW,
                confidence_score=1.0,
                metadata={
                    **node.metadata,
                    "document_no": document_no,
                    "node_type": node.node_type.value,
                    "canonical_anchor": node.canonical_anchor,
                },
            )
            chunks.append(chunk)

        return chunks

    @staticmethod
    def _classify_chunk_type(
        node: ASTNode, document_type: DocType
    ) -> tuple[Optional[ChunkType], str, str]:
        """Returns (ChunkType, role, namespace)."""
        nt = node.node_type

        # Biểu thuế / HS Nomenclature
        if nt == NodeType.AHTN_ENTRY:
            return ChunkType.TARIFF_ENTRY, "candidate", "hs_classification"
        if nt == NodeType.HEADING:
            return ChunkType.TARIFF_ENTRY, "candidate", "hs_classification"
        if nt == NodeType.SUBHEADING:
            return ChunkType.TARIFF_ENTRY, "context", "hs_classification"
        if nt == NodeType.CHAPTER_NOTE:
            return ChunkType.CHAPTER_NOTE, "evidence", "hs_classification"
        if nt == NodeType.SECTION_NOTE:
            return ChunkType.SECTION_NOTE, "evidence", "hs_classification"
        if nt == NodeType.SUBHEADING_NOTE:
            return ChunkType.SUBHEADING_NOTE, "evidence", "hs_classification"

        # Văn bản pháp luật
        if nt in (NodeType.ARTICLE, NodeType.CLAUSE, NodeType.POINT):
            return ChunkType.LEGAL_CLAUSE, "evidence", "legal_classification"
        if nt == NodeType.PARAGRAPH and node.parent_id:
            return ChunkType.LEGAL_CLAUSE, "evidence", "legal_classification"

        # Bảng danh mục sản phẩm / Quy chuẩn
        if nt == NodeType.DATA_ROW:
            return ChunkType.TECHNICAL_STANDARD_ITEM, "evidence", "legal_classification"

        # Default fallback
        if document_type in (DocType.HS_NOMENCLATURE, DocType.TARIFF_SCHEDULE):
            return ChunkType.TARIFF_ENTRY, "context", "hs_classification"
        return ChunkType.LEGAL_CLAUSE, "context", "legal_classification"
