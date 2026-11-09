"""Specialized parser for Product Catalogs and Technical Standards tables in DOCX files.
Handles fuzzy header matching, merged cells, hierarchical group rows, and multi-code cells.
"""

import re
from typing import Optional

from rag.ingestion.docx.ast_models import ASTNode, DocType, NodeType, SourceLocation
from rag.ingestion.docx.openxml_reader import RawCell, RawDocumentPackage, RawParagraph, RawTable


class CatalogParser:
    """Parses product catalog and technical regulation tables into AST nodes."""

    @classmethod
    def parse(cls, pkg: RawDocumentPackage) -> list[ASTNode]:
        nodes: list[ASTNode] = []
        node_order = 0

        # We first look for Annex titles or Document Title
        current_annex: Optional[ASTNode] = None

        for block in pkg.blocks:
            if isinstance(block, RawParagraph):
                t = block.text.strip()
                if not t:
                    continue
                annex_match = re.match(
                    r"^(PHỤ LỤC\s+[IVXLCDM\d]+|PHỤ LỤC)(?:[\s:–—\-]+(.*))?$",
                    t,
                    re.IGNORECASE,
                )
                if annex_match:
                    annex_name = annex_match.group(1).upper()
                    annex_desc = annex_match.group(2) or t
                    node_order += 1
                    current_annex = ASTNode(
                        id=f"annex_{annex_name.replace(' ', '_').lower()}_{node_order}",
                        node_type=NodeType.ANNEX,
                        node_level=1,
                        node_order=node_order,
                        canonical_anchor=annex_name.replace(" ", "-"),
                        title=f"{annex_name}: {annex_desc}",
                        source_text=t,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=annex_name,
                    )
                    nodes.append(current_annex)

            elif isinstance(block, RawTable):
                if block.row_count < 2:
                    continue

                # 1. Detect Column Mapping from first 1-2 rows
                col_map = cls._detect_columns(block)
                if not col_map or "product_name" not in col_map:
                    continue

                # 2. Iterate through data rows
                # Stack for group hierarchy: dict[tier, ASTNode]
                group_stack: dict[int, ASTNode] = {}
                header_row_idx = col_map.get("__header_row_idx", 0)

                for r_idx in range(header_row_idx + 1, block.row_count):
                    raw_cells = block.rows[r_idx]
                    cells = [c.text.strip() for c in raw_cells]
                    if not any(cells):
                        continue

                    # Extract mapped field contents
                    stt = cls._get_field(raw_cells, col_map.get("stt", -1))
                    name = cls._get_field(raw_cells, col_map.get("product_name", -1))
                    hs_raw = cls._get_field(raw_cells, col_map.get("hs_code", -1))
                    standard = cls._get_field(raw_cells, col_map.get("standard", -1))
                    desc = cls._get_field(raw_cells, col_map.get("description", -1))
                    reg = cls._get_field(raw_cells, col_map.get("regulation", -1))

                    # Check if this row is a Group Header row
                    # (e.g. STT is "1", "1.1", "I", "A" and no HS code, or spans almost all columns)
                    is_group = (not hs_raw and not standard) or (
                        stt and re.fullmatch(r"([IVXLCDM]+|[A-Z]|\d+(?:\.\d+)?)\.?", stt) and not hs_raw
                    )

                    if is_group and name:
                        tier = cls._calculate_tier(stt)
                        group_stack = {k: v for k, v in group_stack.items() if k < tier}
                        parent = (
                            group_stack[max(group_stack)]
                            if group_stack
                            else (current_annex if current_annex else None)
                        )
                        parent_bc = (
                            parent.breadcrumb
                            if parent
                            else (current_annex.breadcrumb if current_annex else "Danh mục")
                        )
                        breadcrumb = f"{parent_bc} > {name}"

                        node_order += 1
                        group_node = ASTNode(
                            id=f"grp_{block.block_index}_{r_idx}",
                            node_type=NodeType.GROUP_ROW,
                            node_level=2 + tier,
                            node_order=node_order,
                            title=name,
                            source_text=f"{stt} {name}".strip(),
                            source_location=SourceLocation(
                                block_index=block.block_index,
                                table_index=block.block_index,
                                row_index=r_idx,
                            ),
                            breadcrumb=breadcrumb,
                            parent_id=parent.id if parent else None,
                            metadata={"stt": stt, "tier": tier},
                        )
                        nodes.append(group_node)
                        group_stack[tier] = group_node
                        continue

                    # Otherwise, this is a Data Row (Product / Regulation Entry)
                    # Extract all distinct HS codes from hs_raw (may contain multiple 8-digit codes)
                    hs_codes = cls._extract_hs_codes(hs_raw)
                    if not hs_codes and hs_raw:
                        # Fallback if unformatted code
                        cleaned = re.sub(r"[^\d]", "", hs_raw)
                        if len(cleaned) in (4, 6, 8):
                            hs_codes = [cleaned]

                    parent_grp = (
                        group_stack[max(group_stack)]
                        if group_stack
                        else (current_annex if current_annex else None)
                    )
                    parent_bc = (
                        parent_grp.breadcrumb
                        if parent_grp
                        else (current_annex.breadcrumb if current_annex else "Danh mục")
                    )

                    # Build detailed metadata
                    row_metadata = {
                        "stt": stt,
                        "product_name": name,
                        "technical_standard": standard,
                        "description": desc,
                        "regulatory_requirement": reg,
                        "all_hs_codes": hs_codes,
                    }

                    # If multiple HS codes, create atomic node for each code or one node with codes
                    if hs_codes:
                        for code in hs_codes:
                            node_order += 1
                            breadcrumb = f"{parent_bc} > {code}: {name}"
                            full_text_parts = [
                                f"Mã HS: {code}",
                                f"Tên sản phẩm: {name}",
                                f"Tiêu chuẩn áp dụng: {standard}" if standard else "",
                                f"Mô tả: {desc}" if desc else "",
                                f"Quy định áp dụng: {reg}" if reg else "",
                            ]
                            source_text = "\n".join(p for p in full_text_parts if p)

                            item_node = ASTNode(
                                id=f"item_{block.block_index}_{r_idx}_{code}",
                                node_type=NodeType.DATA_ROW,
                                node_level=8,
                                node_order=node_order,
                                canonical_anchor=f"catalog-{code}",
                                code=code,
                                title=name,
                                source_text=source_text,
                                source_location=SourceLocation(
                                    block_index=block.block_index,
                                    table_index=block.block_index,
                                    row_index=r_idx,
                                ),
                                breadcrumb=breadcrumb,
                                parent_id=parent_grp.id if parent_grp else None,
                                metadata={**row_metadata, "hs_code": code},
                            )
                            nodes.append(item_node)
                    else:
                        node_order += 1
                        breadcrumb = f"{parent_bc} > {name}"
                        full_text_parts = [
                            f"Tên sản phẩm: {name}",
                            f"Tiêu chuẩn áp dụng: {standard}" if standard else "",
                            f"Mô tả: {desc}" if desc else "",
                            f"Quy định áp dụng: {reg}" if reg else "",
                        ]
                        source_text = "\n".join(p for p in full_text_parts if p)
                        item_node = ASTNode(
                            id=f"item_{block.block_index}_{r_idx}",
                            node_type=NodeType.DATA_ROW,
                            node_level=8,
                            node_order=node_order,
                            title=name,
                            source_text=source_text,
                            source_location=SourceLocation(
                                block_index=block.block_index,
                                table_index=block.block_index,
                                row_index=r_idx,
                            ),
                            breadcrumb=breadcrumb,
                            parent_id=parent_grp.id if parent_grp else None,
                            metadata=row_metadata,
                        )
                        nodes.append(item_node)

        return nodes

    @classmethod
    def _detect_columns(cls, table: RawTable) -> dict[str, int]:
        col_map: dict[str, int] = {}
        for r_idx in range(min(3, table.row_count)):
            row_texts = [c.text.lower() for c in table.rows[r_idx]]
            for c_idx, cell_txt in enumerate(row_texts):
                if re.search(r"^(stt|số tt|tt)$", cell_txt):
                    col_map.setdefault("stt", c_idx)
                elif any(k in cell_txt for k in ["tên sản phẩm", "tên hàng", "tên thiết bị", "chủng loại"]):
                    col_map.setdefault("product_name", c_idx)
                elif any(k in cell_txt for k in ["mã số hs", "mã hs", "mã hàng", "mã số"]):
                    col_map.setdefault("hs_code", c_idx)
                elif any(k in cell_txt for k in ["quy chuẩn", "tiêu chuẩn", "qcvn", "tcvn"]):
                    col_map.setdefault("standard", c_idx)
                elif any(k in cell_txt for k in ["mô tả sản phẩm", "mô tả hàng hóa", "mô tả chi tiết"]):
                    col_map.setdefault("description", c_idx)
                elif any(k in cell_txt for k in ["quy định áp dụng", "biện pháp", "chứng nhận"]):
                    col_map.setdefault("regulation", c_idx)

            if "product_name" in col_map:
                col_map["__header_row_idx"] = r_idx
                return col_map
        return col_map

    @staticmethod
    def _get_field(row: list[RawCell], col_idx: int) -> str:
        if 0 <= col_idx < len(row):
            return row[col_idx].text.strip()
        return ""

    @staticmethod
    def _calculate_tier(stt: str) -> int:
        if not stt:
            return 1
        stt_clean = stt.rstrip(".")
        if re.fullmatch(r"[IVXLCDM]+", stt_clean):
            return 0
        if re.fullmatch(r"[A-Z]", stt_clean):
            return 1
        parts = stt_clean.split(".")
        return max(1, len(parts))

    @staticmethod
    def _extract_hs_codes(raw_text: str) -> list[str]:
        # Matches 8-digit dotted: 8517.13.00, or 8 digits continuous: 85171300
        dotted = re.findall(r"\b\d{4}\.\d{2}\.\d{2}\b", raw_text)
        if dotted:
            return [d.replace(".", "") for d in dotted]
        continuous = re.findall(r"\b\d{8}\b", raw_text)
        if continuous:
            return continuous
        return []
