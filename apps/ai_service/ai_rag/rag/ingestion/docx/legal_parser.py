"""Specialized parser for Vietnamese Legal Normative Documents (Luật, Nghị định, Thông tư, Quyết định).
Extracts hierarchical provisions: Chapter -> Section -> Article -> Clause -> Point.
"""

import re
from typing import Optional

from rag.ingestion.docx.ast_models import ASTNode, DocType, NodeType, SourceLocation
from rag.ingestion.docx.openxml_reader import RawDocumentPackage, RawParagraph, RawTable


class LegalParser:
    """Parses Vietnamese legal documents into a hierarchical provision tree."""

    @classmethod
    def parse(cls, pkg: RawDocumentPackage) -> list[ASTNode]:
        nodes: list[ASTNode] = []
        node_order = 0

        # Stack trackers
        current_annex: Optional[ASTNode] = None
        current_chapter: Optional[ASTNode] = None
        current_article: Optional[ASTNode] = None
        current_clause: Optional[ASTNode] = None

        doc_title = ""
        doc_no = ""

        # Extract document title / number from preamble
        for block in pkg.blocks[:25]:
            if isinstance(block, RawParagraph) and block.text:
                t = block.text.strip()
                if not doc_no:
                    m_no = re.search(
                        r"(?:Số|Số:)\s*(\d+[\w\d/\-–]+(?:NĐ-CP|TT-BTC|TT-BTTTT|TT-BGTVT|QĐ-TTg|[A-Z\-]+))",
                        t,
                        re.IGNORECASE,
                    )
                    if m_no:
                        doc_no = m_no.group(1).strip()
                if not doc_title and any(
                    w in t.lower() for w in ["nghị định", "thông tư", "quyết định", "luật"]
                ):
                    doc_title = t

        for block in pkg.blocks:
            if isinstance(block, RawParagraph):
                text = block.text.strip()
                if not text:
                    continue

                # 1. Check for Annex (Phụ lục)
                annex_match = re.match(
                    r"^(PHỤ LỤC\s+[IVXLCDM\d]+|PHỤ LỤC)(?:[\s:–—\-]+(.*))?$",
                    text,
                    re.IGNORECASE,
                )
                if annex_match:
                    annex_name = annex_match.group(1).upper()
                    annex_desc = annex_match.group(2) or text
                    node_order += 1
                    current_annex = ASTNode(
                        id=f"annex_{annex_name.replace(' ', '_').lower()}_{node_order}",
                        node_type=NodeType.ANNEX,
                        node_level=1,
                        node_order=node_order,
                        canonical_anchor=annex_name.replace(" ", "-"),
                        title=f"{annex_name}: {annex_desc}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=annex_name,
                    )
                    nodes.append(current_annex)
                    current_chapter = None
                    current_article = None
                    current_clause = None
                    continue

                # 2. Check for Chapter (Chương)
                chap_match = re.match(
                    r"^CHƯƠNG\s+([IVXLCDM\d]+)(?:[\s:–—\-]+(.*))?$", text, re.IGNORECASE
                )
                if chap_match:
                    chap_num = chap_match.group(1).upper()
                    chap_desc = chap_match.group(2) or text
                    node_order += 1
                    parent_id = current_annex.id if current_annex else None
                    breadcrumb = (
                        f"{current_annex.breadcrumb} > Chương {chap_num}"
                        if current_annex
                        else f"Chương {chap_num}"
                    )
                    current_chapter = ASTNode(
                        id=f"chap_{chap_num}_{node_order}",
                        node_type=NodeType.CHAPTER,
                        node_level=2,
                        node_order=node_order,
                        canonical_anchor=f"chuong-{chap_num.lower()}",
                        code=chap_num,
                        title=f"Chương {chap_num}: {chap_desc}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=breadcrumb,
                        parent_id=parent_id,
                    )
                    nodes.append(current_chapter)
                    current_article = None
                    current_clause = None
                    continue

                # 3. Check for Article (Điều)
                art_match = re.match(
                    r"^Điều\s+(\d+[\w\d]*)\s*[\.:–—]\s*(.*)$", text, re.IGNORECASE
                )
                if art_match:
                    art_num = art_match.group(1)
                    art_title = art_match.group(2).strip()
                    node_order += 1
                    parent_id = (
                        current_chapter.id
                        if current_chapter
                        else (current_annex.id if current_annex else None)
                    )
                    parent_bc = (
                        current_chapter.breadcrumb
                        if current_chapter
                        else (current_annex.breadcrumb if current_annex else (doc_no or "Văn bản"))
                    )
                    breadcrumb = f"{parent_bc} > Điều {art_num}"

                    current_article = ASTNode(
                        id=f"art_{art_num}_{node_order}",
                        node_type=NodeType.ARTICLE,
                        node_level=3,
                        node_order=node_order,
                        canonical_anchor=f"dieu-{art_num.lower()}",
                        code=art_num,
                        title=f"Điều {art_num}. {art_title}" if art_title else f"Điều {art_num}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=breadcrumb,
                        parent_id=parent_id,
                        metadata={"article": art_num},
                    )
                    nodes.append(current_article)
                    current_clause = None
                    continue

                # 4. Check for Clause (Khoản: e.g. "1. ...", "Khoản 1. ...")
                clause_match = re.match(
                    r"^(?:Khoản\s+)?(\d+)\.\s+(.*)$", text
                )
                if clause_match and current_article:
                    clause_num = clause_match.group(1)
                    clause_body = clause_match.group(2).strip()
                    node_order += 1
                    breadcrumb = f"{current_article.breadcrumb} > Khoản {clause_num}"
                    current_clause = ASTNode(
                        id=f"{current_article.id}_c{clause_num}_{node_order}",
                        node_type=NodeType.CLAUSE,
                        node_level=4,
                        node_order=node_order,
                        canonical_anchor=f"{current_article.canonical_anchor}-khoan-{clause_num}",
                        code=clause_num,
                        title=f"Khoản {clause_num}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=breadcrumb,
                        parent_id=current_article.id,
                        metadata={
                            "article": current_article.code,
                            "clause": clause_num,
                        },
                    )
                    nodes.append(current_clause)
                    continue

                # 5. Check for Point (Điểm: e.g. "a) ...", "Điểm a) ...")
                point_match = re.match(
                    r"^(?:Điểm\s+)?([a-zđ])\)\s+(.*)$", text, re.IGNORECASE
                )
                if point_match and (current_clause or current_article):
                    point_char = point_match.group(1).lower()
                    node_order += 1
                    parent_node = current_clause if current_clause else current_article
                    breadcrumb = f"{parent_node.breadcrumb} > Điểm {point_char}"
                    point_node = ASTNode(
                        id=f"{parent_node.id}_p{point_char}_{node_order}",
                        node_type=NodeType.POINT,
                        node_level=5,
                        node_order=node_order,
                        canonical_anchor=f"{parent_node.canonical_anchor}-diem-{point_char}",
                        code=point_char,
                        title=f"Điểm {point_char}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=breadcrumb,
                        parent_id=parent_node.id,
                        metadata={
                            "article": current_article.code if current_article else None,
                            "clause": current_clause.code if current_clause else None,
                            "point": point_char,
                        },
                    )
                    nodes.append(point_node)
                    continue

                # General paragraph inside an article
                if current_article:
                    node_order += 1
                    parent_node = current_clause or current_article
                    para_node = ASTNode(
                        id=f"p_{block.block_index}",
                        node_type=NodeType.PARAGRAPH,
                        node_level=6,
                        node_order=node_order,
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=parent_node.breadcrumb,
                        parent_id=parent_node.id,
                        metadata={"article": current_article.code},
                    )
                    nodes.append(para_node)

        return nodes
