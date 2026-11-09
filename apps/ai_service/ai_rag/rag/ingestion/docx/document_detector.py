"""Automatic and explicit document type detector for DOCX files."""

import re
from typing import Optional

from rag.ingestion.docx.ast_models import DocType
from rag.ingestion.docx.openxml_reader import RawDocumentPackage, RawParagraph, RawTable


class DocumentDetector:
    """Detects document type using structural signals, keyword frequencies, and explicit overrides."""

    @classmethod
    def detect(
        cls, pkg: RawDocumentPackage, explicit_type: Optional[str] = None
    ) -> tuple[DocType, float, dict]:
        """Returns (DocType, confidence_score, metadata_hints)."""
        if explicit_type:
            try:
                dt = DocType(explicit_type.upper())
                return dt, 1.0, {"mode": "explicit", "provided_type": explicit_type}
            except ValueError:
                pass

        first_texts: list[str] = []
        for block in pkg.blocks[:40]:
            if isinstance(block, RawParagraph) and block.text:
                first_texts.append(block.text)

        joined_sample = " \n ".join(first_texts).lower()

        # Check for explicit normative title
        has_decree_or_circular = bool(
            re.search(r"^(nghị định|thông tư|quyết định|luật)\b", joined_sample.strip())
            or re.search(r"\b(nghị định số|thông tư số|quyết định số)\b", joined_sample)
        )

        # Check for HS Nomenclature / Tariff Schedule
        hs_keywords = [
            "danh mục hàng hóa xuất khẩu",
            "danh mục hàng hoá xuất khẩu",
            "phần xiv",
            "phần xvi",
            "phần xvii",
            "chú giải bổ sung (sen)",
            "ahtn 2022",
            "hs 2022",
        ]
        has_hs_title = any(k in joined_sample for k in hs_keywords)

        # Check tables
        catalog_table_vote = 0
        hs_table_vote = 0
        for block in pkg.blocks:
            if isinstance(block, RawTable) and block.row_count > 1:
                first_row_text = " ".join(block.get_row_texts(0)).lower()
                if any(w in first_row_text for w in ["qcvn", "tcvn", "quy chuẩn kỹ thuật", "chứng nhận hợp quy"]):
                    catalog_table_vote += 1
                for r in range(min(5, block.row_count)):
                    row_txt = " ".join(block.get_row_texts(r))
                    if re.search(r"\b\d{4}\.\d{2}\.\d{2}\b", row_txt):
                        hs_table_vote += 1

        has_legal_articles = bool(re.search(r"\bđiều\s+\d+[\.:]", joined_sample))

        hints = {
            "has_decree_or_circular": has_decree_or_circular,
            "has_legal_articles": has_legal_articles,
            "has_hs_title": has_hs_title,
            "catalog_table_vote": catalog_table_vote,
            "hs_table_vote": hs_table_vote,
        }

        # If it's a circular/decree with product standard tables -> PRODUCT_CATALOG
        if catalog_table_vote >= 1 and (has_decree_or_circular or has_legal_articles):
            return DocType.PRODUCT_CATALOG, 0.9, hints

        # If it has legal articles/circular structure and not a pure HS table schedule -> LEGAL_DOCUMENT
        if (has_decree_or_circular or has_legal_articles) and hs_table_vote < 5:
            return DocType.LEGAL_DOCUMENT, 0.9, hints

        # If it's a pure HS Nomenclature schedule (like TT31 section appendices)
        if has_hs_title or hs_table_vote >= 5:
            return DocType.HS_NOMENCLATURE, 0.9, hints

        if catalog_table_vote >= 1:
            return DocType.PRODUCT_CATALOG, 0.8, hints

        if hs_table_vote >= 1:
            return DocType.HS_NOMENCLATURE, 0.8, hints

        return DocType.UNKNOWN, 0.3, hints
