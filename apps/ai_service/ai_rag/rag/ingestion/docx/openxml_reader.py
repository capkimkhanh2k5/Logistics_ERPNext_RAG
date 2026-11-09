"""Low-level OpenXML reader for extracting paragraphs and tables from DOCX files.
Handles OpenXML namespace, merged cells (vMerge, gridSpan), styles, and text runs.
"""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union
from xml.etree import ElementTree
from zipfile import ZipFile

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


@dataclass
class RawCell:
    row_index: int
    col_index: int
    text: str
    lines: list[str] = field(default_factory=list)
    grid_span: int = 1
    is_vmerge_start: bool = False
    is_vmerge_continuation: bool = False


@dataclass
class RawTable:
    block_index: int
    rows: list[list[RawCell]] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def get_row_texts(self, row_index: int) -> list[str]:
        if 0 <= row_index < len(self.rows):
            return [cell.text for cell in self.rows[row_index]]
        return []


@dataclass
class RawParagraph:
    block_index: int
    text: str
    style_id: Optional[str] = None
    is_bold: bool = False
    is_heading: bool = False
    heading_level: Optional[int] = None
    num_id: Optional[int] = None
    num_level: Optional[int] = None


@dataclass
class RawDocumentPackage:
    filename: str
    sha256: str
    blocks: list[Union[RawParagraph, RawTable]] = field(default_factory=list)
    styles: dict[str, dict[str, Any]] = field(default_factory=dict)


class OpenXMLReader:
    """Robust extractor for Microsoft Word .docx OpenXML packages."""

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def read_docx(cls, file_path: Union[str, Path]) -> RawDocumentPackage:
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"DOCX file not found: {path}")

        file_hash = cls.calculate_sha256(path)
        with ZipFile(path, "r") as archive:
            styles = cls._parse_styles(archive)
            blocks = cls._parse_document(archive, styles)

        return RawDocumentPackage(
            filename=path.name,
            sha256=file_hash,
            blocks=blocks,
            styles=styles,
        )

    @classmethod
    def _parse_styles(cls, archive: ZipFile) -> dict[str, dict[str, Any]]:
        styles = {}
        if "word/styles.xml" not in archive.namelist():
            return styles

        try:
            xml_data = archive.read("word/styles.xml")
            root = ElementTree.fromstring(xml_data)
            for style in root.findall("w:style", NS):
                style_id = style.get(f"{{{W_NS}}}styleId")
                name_elem = style.find("w:name", NS)
                name = name_elem.get(f"{{{W_NS}}}val") if name_elem is not None else ""
                styles[style_id] = {
                    "name": name,
                    "type": style.get(f"{{{W_NS}}}type"),
                }
        except Exception:
            pass
        return styles

    @classmethod
    def _parse_document(
        cls, archive: ZipFile, styles: dict[str, dict[str, Any]]
    ) -> list[Union[RawParagraph, RawTable]]:
        if "word/document.xml" not in archive.namelist():
            raise ValueError("Invalid DOCX package: missing word/document.xml")

        xml_data = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml_data)
        body = root.find("w:body", NS)
        if body is None:
            raise ValueError("Invalid DOCX: missing w:body element")

        blocks: list[Union[RawParagraph, RawTable]] = []
        for index, elem in enumerate(body):
            tag = elem.tag.split("}")[-1]
            if tag == "p":
                para = cls._parse_paragraph(elem, index, styles)
                if para.text.strip() or para.is_heading:
                    blocks.append(para)
            elif tag == "tbl":
                table = cls._parse_table(elem, index)
                if table.row_count > 0:
                    blocks.append(table)
        return blocks

    @classmethod
    def _parse_paragraph(
        cls, p_elem: ElementTree.Element, block_index: int, styles: dict[str, dict[str, Any]]
    ) -> RawParagraph:
        text_parts = []
        is_bold = False

        # Check paragraph properties
        pPr = p_elem.find("w:pPr", NS)
        style_id = None
        is_heading = False
        heading_level = None
        num_id = None
        num_level = None

        if pPr is not None:
            pStyle = pPr.find("w:pStyle", NS)
            if pStyle is not None:
                style_id = pStyle.get(f"{{{W_NS}}}val")
                if style_id and style_id in styles:
                    style_name = styles[style_id]["name"].lower()
                    if "heading" in style_name or "tiêu đề" in style_name:
                        is_heading = True
                        m = re.search(r"\d+", style_name)
                        heading_level = int(m.group(0)) if m else 1

            numPr = pPr.find("w:numPr", NS)
            if numPr is not None:
                ilvl = numPr.find("w:ilvl", NS)
                numId = numPr.find("w:numId", NS)
                if ilvl is not None:
                    try:
                        num_level = int(ilvl.get(f"{{{W_NS}}}val", "0"))
                    except ValueError:
                        pass
                if numId is not None:
                    try:
                        num_id = int(numId.get(f"{{{W_NS}}}val", "0"))
                    except ValueError:
                        pass

        for node in p_elem.iter():
            tag = node.tag.split("}")[-1]
            if tag == "t":
                text_parts.append(node.text or "")
            elif tag in ("br", "cr"):
                text_parts.append("\n")
            elif tag == "tab":
                text_parts.append("\t")
            elif tag == "rPr":
                if node.find("w:b", NS) is not None:
                    is_bold = True

        raw_text = "".join(text_parts).strip()

        # Heuristic detection of headings if style was not explicitly set
        if not is_heading and raw_text:
            if re.match(r"^(PHẦN|PHẢN)\s+[IVXLCDM]+", raw_text, re.IGNORECASE):
                is_heading = True
                heading_level = 1
            elif re.match(r"^CHƯƠNG\s+\d+", raw_text, re.IGNORECASE):
                is_heading = True
                heading_level = 2
            elif re.match(r"^ĐIỀU\s+\d+", raw_text, re.IGNORECASE):
                is_heading = True
                heading_level = 3
            elif re.match(r"^PHỤ\s+LỤC(\s+[IVXLCDM\d]+)?", raw_text, re.IGNORECASE):
                is_heading = True
                heading_level = 2

        return RawParagraph(
            block_index=block_index,
            text=raw_text,
            style_id=style_id,
            is_bold=is_bold,
            is_heading=is_heading,
            heading_level=heading_level,
            num_id=num_id,
            num_level=num_level,
        )

    @classmethod
    def _parse_table(cls, tbl_elem: ElementTree.Element, block_index: int) -> RawTable:
        raw_rows: list[list[RawCell]] = []
        table_rows = tbl_elem.findall("w:tr", NS)

        # We track vertical merge column states across rows
        vmerge_col_map: dict[int, RawCell] = {}

        for r_idx, tr in enumerate(table_rows):
            current_row_cells: list[RawCell] = []
            c_idx = 0
            for tc in tr.findall("w:tc", NS):
                tcPr = tc.find("w:tcPr", NS)
                grid_span = 1
                is_vmerge_start = False
                is_vmerge_cont = False

                if tcPr is not None:
                    gs = tcPr.find("w:gridSpan", NS)
                    if gs is not None:
                        try:
                            grid_span = int(gs.get(f"{{{W_NS}}}val", "1"))
                        except ValueError:
                            grid_span = 1

                    vmerge = tcPr.find("w:vMerge", NS)
                    if vmerge is not None:
                        val = vmerge.get(f"{{{W_NS}}}val")
                        if val == "restart":
                            is_vmerge_start = True
                        else:
                            is_vmerge_cont = True

                # Extract paragraphs inside this cell
                lines: list[str] = []
                for p in tc.findall("w:p", NS):
                    p_text_parts = []
                    for t in p.iter():
                        tag = t.tag.split("}")[-1]
                        if tag == "t":
                            p_text_parts.append(t.text or "")
                        elif tag in ("br", "cr"):
                            p_text_parts.append("\n")
                        elif tag == "tab":
                            p_text_parts.append("\t")
                    p_text = "".join(p_text_parts).strip()
                    if p_text:
                        lines.append(p_text)

                cell_text = "\n".join(lines).strip()
                cell = RawCell(
                    row_index=r_idx,
                    col_index=c_idx,
                    text=cell_text,
                    lines=lines,
                    grid_span=grid_span,
                    is_vmerge_start=is_vmerge_start,
                    is_vmerge_continuation=is_vmerge_cont,
                )

                if is_vmerge_cont and c_idx in vmerge_col_map:
                    # Append continuation text to parent cell if any
                    parent_cell = vmerge_col_map[c_idx]
                    if cell_text:
                        parent_cell.text += "\n" + cell_text
                        parent_cell.lines.extend(lines)
                elif is_vmerge_start:
                    vmerge_col_map[c_idx] = cell

                current_row_cells.append(cell)
                c_idx += grid_span

            if current_row_cells:
                raw_rows.append(current_row_cells)

        return RawTable(block_index=block_index, rows=raw_rows)
