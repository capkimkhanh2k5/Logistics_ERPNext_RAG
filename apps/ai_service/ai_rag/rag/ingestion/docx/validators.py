"""Validation engine for structural integrity, HS code conformance, and legal reference validity."""

from typing import Optional

from rag.ingestion.docx.ast_models import (
    ASTNode,
    ParsedChunk,
    ValidationIssue,
    ValidationSeverity,
)


class StructuralValidator:
    """Validates hierarchy consistency, cyclic relationships, and code integrity."""

    @classmethod
    def validate(
        cls, nodes: list[ASTNode], chunks: list[ParsedChunk]
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        node_map = {n.id: n for n in nodes}

        # 1. Check parent references & cycles
        for node in nodes:
            if node.parent_id:
                if node.parent_id not in node_map:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            code="ORPHAN_PARENT_REFERENCE",
                            message=f"Node {node.id} references non-existent parent {node.parent_id}",
                            target_id=node.id,
                        )
                    )
                else:
                    # Cycle check
                    curr = node.parent_id
                    visited = {node.id}
                    while curr and curr in node_map:
                        if curr in visited:
                            issues.append(
                                ValidationIssue(
                                    severity=ValidationSeverity.CRITICAL,
                                    code="CYCLIC_PARENT_HIERARCHY",
                                    message=f"Cycle detected in parent hierarchy of node {node.id}",
                                    target_id=node.id,
                                )
                            )
                            break
                        visited.add(curr)
                        curr = node_map[curr].parent_id

            # 2. Check HS Code validity if present
            if node.code and node.code.isdigit():
                code_len = len(node.code)
                if code_len not in (2, 4, 6, 8):
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            code="INVALID_HS_CODE_LENGTH",
                            message=f"Code {node.code} has unexpected length {code_len} (expected 2, 4, 6, 8)",
                            target_id=node.id,
                        )
                    )

                # Prefix check if parent has code
                if node.parent_id and node.parent_id in node_map:
                    parent = node_map[node.parent_id]
                    if parent.code and parent.code.isdigit():
                        if not node.code.startswith(parent.code):
                            issues.append(
                                ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    code="HS_PREFIX_MISMATCH",
                                    message=f"Child code {node.code} does not start with parent code {parent.code}",
                                    target_id=node.id,
                                    context={
                                        "parent_id": parent.id,
                                        "parent_code": parent.code,
                                    },
                                )
                            )

        # 3. Check chunks integrity
        seen_chunk_ids = set()
        for chunk in chunks:
            if chunk.chunk_id in seen_chunk_ids:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        code="DUPLICATE_CHUNK_ID",
                        message=f"Duplicate chunk ID: {chunk.chunk_id}",
                        target_id=chunk.chunk_id,
                    )
                )
            seen_chunk_ids.add(chunk.chunk_id)

            if not chunk.source_text.strip():
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="EMPTY_CHUNK_SOURCE_TEXT",
                        message=f"Chunk {chunk.chunk_id} has empty source text",
                        target_id=chunk.chunk_id,
                    )
                )

        return issues
