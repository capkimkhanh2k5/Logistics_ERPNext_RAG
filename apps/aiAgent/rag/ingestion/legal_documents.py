"""Source-addressed DOCX legal text; normalized hints never become quoted law."""

import hashlib
import re
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from rag.ingestion.sources import source_path
from rag.utils.files import digest

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def paragraph_text(element) -> str:
    parts = []
    for node in element.iter():
        if node.tag == f"{{{NS['w']}}}t":
            parts.append(node.text or "")
        elif node.tag in {f"{{{NS['w']}}}br", f"{{{NS['w']}}}cr"}:
            parts.append("\n")
        elif node.tag == f"{{{NS['w']}}}tab":
            parts.append("\t")
    return "".join(parts).strip()


def legal_document_bundle(root: Path, spec: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Keep paragraphs, table columns, continuations and group scopes from the raw file."""
    path = source_path(root, spec["file"])
    raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if raw_hash != spec["sha256"]:
        raise ValueError(f"Legal source file changed: {spec['file']}")
    with ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    body = ElementTree.fromstring(xml).find("w:body", NS)  # nosec B314: hash-bound local XML
    if body is None:
        raise ValueError("Legal DOCX has no document body")
    rows, edges = [], []
    article, table_index, last_group = "", 0, ""

    def add(text, address, kind, context="", parent=""):
        if not text.strip():
            return ""
        sid = f"{spec['dataset']}:{address}"
        locator = {
            "document": spec["document_no"],
            "file": spec["file"],
            "sha256": raw_hash,
            "block": address,
            "article": article,
            "wording_status": "HASH_BOUND_LOCAL_DOCX_EXTRACTION_NOT_PDF_VERIFIED",
            "official_url": spec["official_url"],
        }
        rows.append(
            {
                "id": sid,
                "source_id": address,
                "dataset": spec["dataset"],
                "role": "evidence",
                "chunk_type": kind,
                "namespace": "legal_classification",
                "code": None,
                "level": None,
                "source_text": text,
                "embedding_text": " | ".join(
                    filter(None, [spec["document_no"], article, context, text])
                ),
                "lexical_text": " | ".join(
                    filter(None, [spec["document_no"], article, context, text])
                ),
                "effective_from": spec.get("effective_from"),
                "effective_to": spec.get("effective_to"),
                "legal_status": spec["legal_status"],
                "locator": locator,
                "source": locator,
                "metadata": {
                    "document_no": spec["document_no"],
                    "validity_review": spec["validity_review"],
                    "official_url": spec["official_url"],
                    "article": article,
                    "parent_source_id": parent,
                    "normalization_usage": "SEARCH_HINTS_ONLY_RAW_DOCX_IS_QUOTE_SOURCE",
                },
            }
        )
        ancestor = parent
        by_id = {r["id"]: r for r in rows}
        while ancestor:
            edges.append(
                {
                    "id": "LEGAL_SCOPE:" + digest([sid, ancestor])[:24],
                    "source": ancestor,
                    "target": sid,
                    "relation": "CONTEXT_FOR",
                    "metadata": {"basis": "DOCX_TABLE_GROUP", "locator": locator},
                }
            )
            ancestor = by_id[ancestor]["metadata"].get("parent_source_id", "")
        return sid

    for block_index, block in enumerate(body):
        if block.tag == f"{{{NS['w']}}}p":
            text = paragraph_text(block)
            if re.match(r"Điều\s+\d+\.", text):
                article = text
            elif re.match(r"PHỤ LỤC", text, re.I):
                article = text
            add(text, f"p{block_index}", "legal_clause")
        elif block.tag == f"{{{NS['w']}}}tbl":
            table_rows = block.findall("w:tr", NS)
            header = (
                "\n".join(paragraph_text(c) for c in table_rows[0].findall("w:tc", NS))
                if table_rows
                else ""
            )
            # Letterheads and signature tables do not establish product obligations.
            if "Mã" not in header or not any(
                term in header for term in ("Tên sản phẩm", "hàng hóa")
            ):
                continue
            table_index += 1
            group_stack: dict[int, str] = {}
            grouped: list[tuple[int, list[str]]] = []
            for row_index, row in enumerate(table_rows[1:], 1):
                cells = [
                    "\n".join(paragraph_text(p) for p in c.findall("w:p", NS)).strip()
                    for c in row.findall("w:tc", NS)
                ]
                if not any(cells):
                    continue
                if cells[0].strip() == "" and grouped:
                    grouped[-1][1].extend(cells)  # Continue the same merged source row.
                    continue
                grouped.append((row_index, cells))
            header_id = add(header, f"t{table_index}-header", "legal_clause")
            last_group = header_id
            for row_index, cells in grouped:
                label = cells[0].strip()
                is_group = len(cells) < 3 or bool(re.fullmatch(r"[A-Z]+\.?", label))
                text = "\n".join(c for c in cells if c.strip())
                if is_group:
                    tier = (
                        0
                        if re.fullmatch(r"[IVX]+\.?", label) or len(cells) == 1
                        else len(label.rstrip(".").split("."))
                        if re.fullmatch(r"\d+(?:\.\d+)*\.?", label)
                        else 1
                    )
                    group_stack = {k: v for k, v in group_stack.items() if k < tier}
                    parent = group_stack[max(group_stack)] if group_stack else header_id
                    sid = add(text, f"t{table_index}-r{row_index}", "legal_clause", header, parent)
                    group_stack[tier] = sid
                    last_group = sid
                else:
                    add(
                        text,
                        f"t{table_index}-r{row_index}",
                        "technical_standard_item",
                        header,
                        last_group,
                    )
    if not rows:
        raise ValueError("Legal source extraction returned no records")
    nodes = [
        {
            "id": row["id"],
            "metadata": {
                **row["metadata"],
                "source_text": row["source_text"],
                "locator": row["locator"],
                "chunk_type": row["chunk_type"],
            },
        }
        for row in rows
    ]
    return rows, nodes, edges
