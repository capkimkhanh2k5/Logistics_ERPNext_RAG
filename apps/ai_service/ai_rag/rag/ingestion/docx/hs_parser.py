"""Specialized parser for HS Nomenclature and Tariff Schedules (e.g. TT31/2022/TT-BTC).
Builds complete AST hierarchy: Part -> Chapter -> Note -> Heading -> Subheading -> AHTN8.
"""

import re
from typing import Optional

from rag.ingestion.docx.ast_models import ASTNode, DocType, NodeType, SourceLocation
from rag.ingestion.docx.openxml_reader import RawDocumentPackage, RawParagraph, RawTable


class HSParser:
    """Extracts hierarchical HS nomenclature tree from OpenXML document packages."""

    @classmethod
    def parse(cls, pkg: RawDocumentPackage) -> list[ASTNode]:
        nodes: list[ASTNode] = []
        node_order = 0

        # Stack trackers
        current_part: Optional[ASTNode] = None
        current_chapter: Optional[ASTNode] = None
        current_heading: Optional[ASTNode] = None
        # Stack of subheadings based on dash depth: dict[depth, ASTNode]
        subheading_stack: dict[int, ASTNode] = {}

        in_notes_section = False
        note_type = NodeType.CHAPTER_NOTE

        for block in pkg.blocks:
            if isinstance(block, RawParagraph):
                text = block.text.strip()
                if not text:
                    continue

                # Check for Part (Phần)
                part_match = re.match(
                    r"^(?:PHẦN|PHẢN)\s+([IVXLCDM]+)(?:[\s:–—\-]+(.*))?$", text, re.IGNORECASE
                )
                if part_match:
                    part_num = part_match.group(1).upper()
                    part_title = part_match.group(2) or text
                    node_order += 1
                    current_part = ASTNode(
                        id=f"part_{part_num}",
                        node_type=NodeType.PART,
                        node_level=1,
                        node_order=node_order,
                        canonical_anchor=f"Section-{part_num}",
                        code=part_num,
                        title=f"Phần {part_num}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=f"Phần {part_num}",
                    )
                    nodes.append(current_part)
                    current_chapter = None
                    current_heading = None
                    subheading_stack.clear()
                    in_notes_section = False
                    continue

                # Check for Chapter (Chương)
                chap_match = re.match(r"^CHƯƠNG\s+(\d+)(?:[\s:–—\-]+(.*))?$", text, re.IGNORECASE)
                if chap_match:
                    chap_num = chap_match.group(1).zfill(2)
                    chap_title = chap_match.group(2) or text
                    node_order += 1
                    parent_id = current_part.id if current_part else None
                    breadcrumb = f"{current_part.breadcrumb} > Chương {chap_num}" if current_part else f"Chương {chap_num}"
                    current_chapter = ASTNode(
                        id=f"chap_{chap_num}",
                        node_type=NodeType.CHAPTER,
                        node_level=2,
                        node_order=node_order,
                        canonical_anchor=f"Chapter-{chap_num}",
                        code=chap_num,
                        title=f"Chương {chap_num}: {chap_title}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=breadcrumb,
                        parent_id=parent_id,
                        metadata={"chapter": chap_num},
                    )
                    nodes.append(current_chapter)
                    current_heading = None
                    subheading_stack.clear()
                    in_notes_section = False
                    continue

                # Check for Notes header
                if re.match(r"^(Chú giải|Chú giải bổ sung|Ghi chú)[\.:\s]*$", text, re.IGNORECASE):
                    in_notes_section = True
                    note_type = (
                        NodeType.CHAPTER_NOTE if current_chapter else NodeType.SECTION_NOTE
                    )
                    continue

                # If in notes section, each numbered note or paragraph is a Note node
                if in_notes_section:
                    # If we encounter a Heading code or table, exit notes section
                    if re.match(r"^\d{2}\.\d{2}\b", text):
                        in_notes_section = False
                    else:
                        node_order += 1
                        parent_id = (
                            current_chapter.id
                            if current_chapter
                            else (current_part.id if current_part else None)
                        )
                        breadcrumb = (
                            f"{current_chapter.breadcrumb} > Chú giải"
                            if current_chapter
                            else "Chú giải"
                        )
                        note_node = ASTNode(
                            id=f"note_{block.block_index}",
                            node_type=note_type,
                            node_level=3,
                            node_order=node_order,
                            source_text=text,
                            source_location=SourceLocation(block_index=block.block_index),
                            breadcrumb=breadcrumb,
                            parent_id=parent_id,
                        )
                        nodes.append(note_node)
                        continue

                # Check for explicit Heading in paragraph: e.g. "84.01 — Lò phản ứng..." or "86.06\tToa xe..."
                heading_match = re.match(
                    r"^(\d{2}\.\d{2}|\d{4})(?:[\s\t]*[-–—:]|\t+)\s*(.+)$", text
                )
                if heading_match:
                    h_code = heading_match.group(1).replace(".", "").strip()
                    if current_heading and current_heading.code == h_code:
                        continue
                    raw_title = heading_match.group(2).strip()
                    # If bilingual tab-separated, prioritize first part (Vietnamese)
                    h_title = raw_title.split("\t")[0].strip()
                    node_order += 1
                    parent_id = current_chapter.id if current_chapter else None
                    breadcrumb = (
                        f"{current_chapter.breadcrumb} > Nhóm {h_code}"
                        if current_chapter
                        else f"Nhóm {h_code}"
                    )
                    current_heading = ASTNode(
                        id=f"heading_{h_code}",
                        node_type=NodeType.HEADING,
                        node_level=4,
                        node_order=node_order,
                        canonical_anchor=f"Heading-{h_code}",
                        code=h_code,
                        title=f"Nhóm {h_code}: {h_title}",
                        source_text=text,
                        source_location=SourceLocation(block_index=block.block_index),
                        breadcrumb=breadcrumb,
                        parent_id=parent_id,
                        metadata={"heading": h_code, "chapter": h_code[:2]},
                    )
                    nodes.append(current_heading)
                    subheading_stack.clear()
                    continue

            elif isinstance(block, RawTable):
                # Process tariff rows in table
                for r_idx, row in enumerate(block.rows):
                    if not row:
                        continue
                    cells = [c.text.strip() for c in row]
                    if not any(cells):
                        continue

                    # Extract candidate code from cell 0 or cell 3
                    raw_code_cell = cells[0]
                    desc_cell = cells[1] if len(cells) > 1 else ""
                    unit_cell = cells[2] if len(cells) > 2 else ""

                    # Clean code
                    cleaned_code = raw_code_cell.replace(".", "").strip()

                    # Count dash prefix in description
                    dash_match = re.match(r"^([-–—]+)\s*(.*)$", desc_cell)
                    dash_count = len(dash_match.group(1)) if dash_match else 0
                    clean_desc = dash_match.group(2).strip() if dash_match else desc_cell

                    # If cell 0 has 4-digit code (Heading)
                    if len(cleaned_code) == 4 and cleaned_code.isdigit():
                        node_order += 1
                        parent_id = current_chapter.id if current_chapter else None
                        breadcrumb = (
                            f"{current_chapter.breadcrumb} > Nhóm {cleaned_code}"
                            if current_chapter
                            else f"Nhóm {cleaned_code}"
                        )
                        current_heading = ASTNode(
                            id=f"heading_{cleaned_code}",
                            node_type=NodeType.HEADING,
                            node_level=4,
                            node_order=node_order,
                            canonical_anchor=f"Heading-{cleaned_code}",
                            code=cleaned_code,
                            title=f"Nhóm {cleaned_code}: {desc_cell}",
                            source_text=f"{raw_code_cell} — {desc_cell}",
                            source_location=SourceLocation(
                                block_index=block.block_index,
                                table_index=block.block_index,
                                row_index=r_idx,
                            ),
                            breadcrumb=breadcrumb,
                            parent_id=parent_id,
                            metadata={"heading": cleaned_code, "chapter": cleaned_code[:2]},
                        )
                        nodes.append(current_heading)
                        subheading_stack.clear()
                        continue

                    # If cell 0 has 8-digit code (AHTN 8)
                    if len(cleaned_code) == 8 and cleaned_code.isdigit():
                        h_code = cleaned_code[:4]
                        if current_heading is None or current_heading.code != h_code:
                            existing_h = next(
                                (n for n in nodes if n.node_type == NodeType.HEADING and n.code == h_code),
                                None,
                            )
                            if existing_h:
                                current_heading = existing_h
                            else:
                                node_order += 1
                                parent_chap_id = current_chapter.id if current_chapter else None
                                chap_bc = (
                                    current_chapter.breadcrumb
                                    if current_chapter
                                    else f"Chương {h_code[:2]}"
                                )
                                current_heading = ASTNode(
                                    id=f"heading_{h_code}",
                                    node_type=NodeType.HEADING,
                                    node_level=4,
                                    node_order=node_order,
                                    canonical_anchor=f"Heading-{h_code}",
                                    code=h_code,
                                    title=f"Nhóm {h_code}",
                                    source_text=f"Nhóm {h_code}",
                                    source_location=SourceLocation(block_index=block.block_index),
                                    breadcrumb=f"{chap_bc} > Nhóm {h_code}",
                                    parent_id=parent_chap_id,
                                    metadata={"heading": h_code, "chapter": h_code[:2]},
                                )
                                nodes.append(current_heading)
                            subheading_stack.clear()

                        node_order += 1
                        # Determine parent: nearest subheading with smaller dash count, or heading
                        parent_sub = None
                        if dash_count > 0:
                            for d in sorted(subheading_stack.keys(), reverse=True):
                                if d < dash_count:
                                    cand = subheading_stack[d]
                                    if not cand.code or cleaned_code.startswith(cand.code):
                                        parent_sub = cand
                                        break
                        if parent_sub is None:
                            cand = subheading_stack.get(max(subheading_stack.keys(), default=-1))
                            if cand and (not cand.code or cleaned_code.startswith(cand.code)):
                                parent_sub = cand

                        parent_id = (
                            parent_sub.id
                            if parent_sub
                            else (current_heading.id if current_heading else None)
                        )
                        parent_bc = (
                            parent_sub.breadcrumb
                            if parent_sub
                            else (
                                current_heading.breadcrumb
                                if current_heading
                                else f"Chương {cleaned_code[:2]}"
                            )
                        )
                        breadcrumb = f"{parent_bc} > {cleaned_code}: {clean_desc}"

                        entry_node = ASTNode(
                            id=f"ahtn_{cleaned_code}",
                            node_type=NodeType.AHTN_ENTRY,
                            node_level=8,
                            node_order=node_order,
                            canonical_anchor=f"AHTN-{cleaned_code}",
                            code=cleaned_code,
                            title=clean_desc,
                            source_text=f"{raw_code_cell} — {desc_cell}"
                            + (f" [{unit_cell}]" if unit_cell else ""),
                            source_location=SourceLocation(
                                block_index=block.block_index,
                                table_index=block.block_index,
                                row_index=r_idx,
                            ),
                            breadcrumb=breadcrumb,
                            parent_id=parent_id,
                            metadata={
                                "ahtn8": cleaned_code,
                                "hs6": cleaned_code[:6],
                                "heading": cleaned_code[:4],
                                "chapter": cleaned_code[:2],
                                "unit": unit_cell,
                                "dash_count": dash_count,
                            },
                        )
                        nodes.append(entry_node)
                        continue

                    # If code is 6 digits or empty with dashes (Subheading)
                    if (len(cleaned_code) == 6 and cleaned_code.isdigit()) or (
                        not cleaned_code and dash_count > 0 and clean_desc
                    ):
                        if len(cleaned_code) == 6 and cleaned_code.isdigit():
                            h_code = cleaned_code[:4]
                            if current_heading is None or current_heading.code != h_code:
                                existing_h = next(
                                    (n for n in nodes if n.node_type == NodeType.HEADING and n.code == h_code),
                                    None,
                                )
                                if existing_h:
                                    current_heading = existing_h
                                else:
                                    node_order += 1
                                    parent_chap_id = current_chapter.id if current_chapter else None
                                    chap_bc = (
                                        current_chapter.breadcrumb
                                        if current_chapter
                                        else f"Chương {h_code[:2]}"
                                    )
                                    current_heading = ASTNode(
                                        id=f"heading_{h_code}",
                                        node_type=NodeType.HEADING,
                                        node_level=4,
                                        node_order=node_order,
                                        canonical_anchor=f"Heading-{h_code}",
                                        code=h_code,
                                        title=f"Nhóm {h_code}",
                                        source_text=f"Nhóm {h_code}",
                                        source_location=SourceLocation(block_index=block.block_index),
                                        breadcrumb=f"{chap_bc} > Nhóm {h_code}",
                                        parent_id=parent_chap_id,
                                        metadata={"heading": h_code, "chapter": h_code[:2]},
                                    )
                                    nodes.append(current_heading)
                                subheading_stack.clear()

                        node_order += 1
                        # Find parent subheading with strictly smaller dash count
                        parent_sub = None
                        for d in sorted(subheading_stack.keys(), reverse=True):
                            if d < dash_count:
                                cand = subheading_stack[d]
                                if not cand.code or not cleaned_code or cleaned_code.startswith(cand.code):
                                    parent_sub = cand
                                    break

                        parent_id = (
                            parent_sub.id
                            if parent_sub
                            else (current_heading.id if current_heading else None)
                        )
                        parent_bc = (
                            parent_sub.breadcrumb
                            if parent_sub
                            else (
                                current_heading.breadcrumb
                                if current_heading
                                else "Biểu thuế"
                            )
                        )
                        sub_label = cleaned_code or f"depth_{dash_count}"
                        breadcrumb = f"{parent_bc} > {clean_desc}"

                        sub_node = ASTNode(
                            id=f"sub_{sub_label}_{node_order}",
                            node_type=NodeType.SUBHEADING,
                            node_level=6 if len(cleaned_code) == 6 else 5,
                            node_order=node_order,
                            canonical_anchor=f"Subheading-{cleaned_code}"
                            if cleaned_code
                            else None,
                            code=cleaned_code if cleaned_code else None,
                            title=clean_desc,
                            source_text=f"{raw_code_cell} {desc_cell}".strip(),
                            source_location=SourceLocation(
                                block_index=block.block_index,
                                table_index=block.block_index,
                                row_index=r_idx,
                            ),
                            breadcrumb=breadcrumb,
                            parent_id=parent_id,
                            metadata={
                                "hs6": cleaned_code if len(cleaned_code) == 6 else None,
                                "dash_count": dash_count,
                            },
                        )
                        nodes.append(sub_node)
                        # Purge deeper subheadings from stack and record this one
                        subheading_stack = {
                            d: s for d, s in subheading_stack.items() if d < dash_count
                        }
                        subheading_stack[dash_count] = sub_node

        return nodes
