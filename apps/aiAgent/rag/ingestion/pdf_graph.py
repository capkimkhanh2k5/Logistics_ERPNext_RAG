"""Read tariff table structure from PDF geometry, independently of HS values."""

import hashlib
import re
from collections import Counter
from pathlib import Path

import fitz
import numpy as np
from scipy.ndimage import find_objects, label

from rag.graph.legal_evidence import evidence_digest
from rag.ingestion.provenance import same_processor

SOURCE_CODE_PATTERN = r"\b(?:\d{4}(?:\.\d{2}){1,2}|\d{2}\.\d{2})\b"


def extractor_identity() -> dict:
    return {
        "version": "bilingual-table-spans-v2",
        "parser_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pymupdf_version": fitz.VersionBind,
    }


def validate_extraction(rows: list[dict], extraction: dict, pdf_sha256: str) -> None:
    if not same_processor(extraction.get("extractor"), extractor_identity()):
        raise ValueError("PDF table extractor version is stale")
    if extraction.get("sha256") != pdf_sha256 or any(
        r["locator"].get("sha256") != pdf_sha256 for r in rows
    ):
        raise ValueError("PDF table extraction source hash is stale")
    if extraction.get("rows_hash") != evidence_digest(rows):
        raise ValueError("PDF table extraction rows changed after extraction")
    if any(p["status"] == "UNRESOLVED_COLUMNS" for p in extraction["pages"]):
        raise ValueError("PDF table extraction has unresolved source pages")
    inventory = {item["code"] for item in extraction["code_inventory"]}
    if inventory != {r["code"] for r in rows if r.get("code")}:
        raise ValueError("PDF code-column inventory differs from extracted rows")


def clusters(values: list[int] | np.ndarray) -> list[float]:
    groups: list[list[int]] = []
    for value in values:
        if not groups or value > groups[-1][-1] + 1:
            groups.append([])
        groups[-1].append(int(value))
    return [float(np.mean(g)) for g in groups]


def cell_text(words: list[tuple], box: tuple[float, float, float, float]) -> str:
    x0, y0, x1, y1 = box
    selected = [w for w in words if x0 < (w[0] + w[2]) / 2 < x1 and y0 < (w[1] + w[3]) / 2 < y1]
    selected.sort(key=lambda w: (round(w[1] / 3), w[0]))
    return " ".join(w[4] for w in selected).strip()


def marker_depth(text: str) -> int | None:
    prefix = re.match(r"^\s*((?:[-–—]\s*)+)", text)
    if not prefix:
        return None
    # Unicode dash widths encode repeated printed hierarchy marks in the PDF text layer.
    return sum({"-": 1, "–": 2, "—": 3}.get(c, 0) for c in prefix[1])


def raster_depth(page, words, box) -> int | None:
    x0, y0, x1, y1 = box
    selected = [w for w in words if x0 < (w[0] + w[2]) / 2 < x1 and y0 < (w[1] + w[3]) / 2 < y1]
    if not selected:
        return None
    top = min(w[1] for w in selected)
    first_line = [w for w in selected if w[1] < top + 4]
    bottom = max(w[3] for w in first_line)
    clip = fitz.Rect(x0 + 3, max(y0 + 1, top), min(x1 - 1, x0 + 90), min(y1 - 1, bottom))
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY, clip=clip)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    components = sorted((s for s in find_objects(label(a < 160)[0]) if s), key=lambda s: s[1].start)
    count = 0
    for sy, sx in components:
        width, height = sx.stop - sx.start, sy.stop - sy.start
        if width > a.shape[1] * 0.7 or width * height < 3:
            continue
        if height <= a.shape[0] * 0.35 and width >= height * 2 and width >= 5:
            count += 1
        else:
            break
    return count or None


def table_rows(path: Path) -> tuple[list[dict], dict]:
    """Extract bilingual ruled table rows; raster grids work with scanned PDF text layers."""
    rows: list[dict] = []
    pages = []
    inventory: list[dict] = []
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    with fitz.open(path) as document:
        layouts: Counter[tuple[int, ...]] = Counter()
        for page in document:
            pix = page.get_pixmap(colorspace=fitz.csGRAY, alpha=False)
            a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
            width = page.rect.width
            y = clusters(
                np.where((a[:, int(width * 0.025) : int(width * 0.975)] < 220).mean(axis=1) > 0.65)[
                    0
                ]
            )
            if len(y) > 2:
                x = clusters(np.where((a[int(y[0]) : int(y[-1]) + 1] < 220).mean(axis=0) > 0.90)[0])
                if len(x) == 7:
                    layouts[tuple(round(v) for v in x)] += 1
        if not layouts:
            raise ValueError(f"No validated bilingual table layout in {path.name}")
        common_columns = list(layouts.most_common(1)[0][0])
        for number, page in enumerate(document, 1):
            words = page.get_text("words")
            pix = page.get_pixmap(colorspace=fitz.csGRAY, alpha=False)
            pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
            width = page.rect.width
            # Detect long rules across the table, not text strokes or individual cell borders.
            ys = clusters(
                np.where(
                    (pixels[:, int(width * 0.025) : int(width * 0.975)] < 220).mean(axis=1) > 0.65
                )[0]
            )
            if len(ys) < 3:
                pages.append({"page": number, "status": "NON_TABLE_PAGE"})
                continue
            # Count printed codes independently of row segmentation, inside the ruled table.
            # Chapter-note references outside the table are not tariff code anchors.
            column = cell_text(words, (common_columns[0], ys[0], common_columns[1], ys[-1]))
            inventory.extend(
                {"code": code.replace(".", ""), "physical_page": number}
                for code in re.findall(SOURCE_CODE_PATTERN, column)
            )
            xs = clusters(
                np.where((pixels[int(ys[0]) : int(ys[-1]) + 1] < 220).mean(axis=0) > 0.90)[0]
            )
            xs = [x for x in xs if width * 0.01 < x < width * 0.99]
            if len(xs) != 7:
                # Recover faint rules with the layout measured across this same PDF.
                support = [
                    float(
                        (pixels[int(ys[0]) : int(ys[-1]) + 1, max(0, x - 1) : x + 2] < 245)
                        .any(axis=1)
                        .mean()
                    )
                    for x in common_columns
                ]
                if min(support) < 0.45:
                    pages.append({"page": number, "status": "UNRESOLVED_COLUMNS", "columns": xs})
                    continue
                xs = [float(x) for x in common_columns]
            # The table's first three cells are Vietnamese code, description and unit.
            x0, x1, x2, x3 = xs[:4]
            code_right, description_right = xs[4:6]
            count = 0
            for y0, y1 in zip(ys, ys[1:], strict=False):
                code_text = cell_text(words, (x0, y0, x1, y1))
                vi = cell_text(words, (x1, y0, x2, y1))
                en = cell_text(words, (code_right, y0, description_right, y1))
                matches = re.findall(SOURCE_CODE_PATTERN, code_text)
                if not matches and marker_depth(vi) is None and marker_depth(en) is None:
                    # A wrapped table description can continue in the first cell on the next page.
                    # Headers have a nonempty code-column label; continuation cells do not.
                    is_table_heading = re.match(r"^SUB\s*[-–—]?\s*CHAPTER\b", en, re.I)
                    if rows and not code_text and (vi or en) and not is_table_heading:
                        rows[-1]["text_vi"] += " " + vi
                        rows[-1]["text_en"] += " " + en
                        rows[-1]["locator"].setdefault("continuations", []).append(
                            {
                                "physical_page": number,
                                "bbox": [round(x1, 2), round(y0, 2), round(x2, 2), round(y1, 2)],
                            }
                        )
                    continue
                depth_vi, depth_en = marker_depth(vi), marker_depth(en)
                # Printed bilingual copies cross-check structure without translating source wording.
                depth = depth_en if depth_en is not None else depth_vi
                visual_depth = (
                    raster_depth(page, words, (code_right, y0, description_right, y1))
                    if depth is not None
                    else None
                )
                if visual_depth is not None:
                    depth = visual_depth
                if matches and len(matches) != 1:
                    raise ValueError(
                        f"Multiple source codes in a PDF table cell: {path.name}:{number}"
                    )
                code = matches[0].replace(".", "") if matches else None
                if code and len(code) == 4:
                    depth = 0
                rows.append(
                    {
                        "code": code,
                        "text_vi": vi,
                        "text_en": en,
                        "depth": depth,
                        "depth_vi": depth_vi,
                        "depth_en": depth_en,
                        "depth_basis": "PDF_RASTER_MARKERS"
                        if visual_depth is not None
                        else "PDF_TEXT_MARKERS",
                        "locator": {
                            "document": path.name,
                            "sha256": sha,
                            "physical_page": number,
                            "bbox": [round(x1, 2), round(y0, 2), round(x2, 2), round(y1, 2)],
                        },
                    }
                )
                count += 1
            pages.append({"page": number, "status": "EXTRACTED", "rows": count})
    return rows, {
        "document": path.name,
        "sha256": sha,
        "pages": pages,
        "extractor": extractor_identity(),
        "rows_hash": evidence_digest(rows),
        "code_inventory": inventory,
    }
