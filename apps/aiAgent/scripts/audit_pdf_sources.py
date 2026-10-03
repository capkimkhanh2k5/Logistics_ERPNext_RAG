#!/usr/bin/env python3
"""Audit registered source wording and graph integrity against PDFs, without gold labels."""

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.data import source_files, tariff_bundle, write_json  # noqa: E402
from rag.sources import source_manifest  # noqa: E402

RUN = ROOT / "artifacts/experiments/run_pdf_graph_v4"


def tokens(text):
    text = unicodedata.normalize("NFKD", text.lower().replace("đ", "d"))
    return re.findall(r"[a-z0-9]+", "".join(c for c in text if not unicodedata.combining(c)))


def grams(text, size=None):
    words = tokens(text)
    size = size or min(3, len(words))
    return {tuple(words[i : i + size]) for i in range(len(words) - size + 1)}


def locate(text, page_texts):
    query = grams(text)
    size = min(3, len(tokens(text)))
    page_grams = [grams(p, size) for p in page_texts]
    scores = [len(query & p) / max(1, len(query)) for p in page_grams]
    best = max(range(len(scores)), key=scores.__getitem__)
    pages = [best + 1]
    combined = set(page_grams[best])
    for other in (best - 2, best - 1, best + 1, best + 2):
        if 0 <= other < len(scores) and scores[other] > 0.02:
            pages.append(other + 1)
            combined.update(page_grams[other])
    return {
        "physical_pages": sorted(pages),
        "word_trigram_coverage": round(len(query & combined) / max(1, len(query)), 4),
    }


def main():
    global RUN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=RUN.name)
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or args.run_id in {".", ".."}:
        raise ValueError("Run ID must be a directory name")
    RUN = ROOT / "artifacts/experiments" / args.run_id
    data, manifest = source_files(), source_manifest(ROOT)
    proof, hashes, records, nodes, edges = {}, {}, [], [], []
    for source in manifest["tariffs"]:
        rs, ns, es = tariff_bundle(source, data)
        records.extend(rs)
        nodes.extend(ns)
        edges.extend(es)
        pdf = ROOT / source["source_pdf"]
        hashes[source["source_pdf"]] = hashlib.sha256(pdf.read_bytes()).hexdigest()
        with fitz.open(pdf) as doc:
            pages = [p.get_text() for p in doc]
        rows = json.loads((RUN / (rs[0]["section"] + "_pdf_rows.json")).read_text())
        if any(r["locator"]["sha256"] != hashes[source["source_pdf"]] for r in rows):
            raise ValueError(f"PDF table extraction is stale: {pdf.name}")
        by_code = {r["code"]: r for r in rows if r["code"]}
        for record in rs:
            code = record.get("code")
            if code in by_code:
                entry = {
                    **by_code[code]["locator"],
                    "basis": "PDF_CODE_ANCHOR",
                    "raw_pdf_text": by_code[code]["text_vi"],
                }
            elif code:
                entry = {
                    "document": pdf.name,
                    "sha256": hashes[source["source_pdf"]],
                    "basis": "UNPRINTED_TAXONOMY_NODE_NOT_LEGAL_WORDING",
                }
            elif record["metadata"].get("record_type") == "legal_term_concept":
                entry = {
                    "document": pdf.name,
                    "sha256": hashes[source["source_pdf"]],
                    "basis": "NORMALIZED_TERM_INDEX_LABEL_NOT_LEGAL_WORDING",
                }
            else:
                entry = {
                    "document": pdf.name,
                    "sha256": hashes[source["source_pdf"]],
                    "basis": "PDF_TEXT_LAYER_COMPARISON",
                    **locate(record["source_text"], pages),
                }
            proof[record["id"]] = entry
    for dataset, relative in (
        ("gir", "data/raw/6_GIR.pdf"),
        ("tt85", "data/raw/85-btc.signed.pdf"),
        ("scope", "data/raw/HS_2022.pdf"),
    ):
        path = ROOT / relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        if dataset == "tt85":
            ocr = json.loads((RUN / "tt85_pdf_ocr.json").read_text())
            if ocr.get("sha256") != hashes[relative]:
                raise ValueError("OCR must be extracted from the current signed TT85 PDF")
            pages = [" ".join(line["text"] for line in p["lines"]) for p in ocr["pages"]]
            source_rows = [("tt85:" + r["chunk_id"], r["text"]) for r in data[dataset]]
            basis = "PDF_APPLE_VISION_OCR_COMPARISON_EN_US"
        elif dataset == "scope":
            with fitz.open(path) as doc:
                pages = [p.get_text() for p in doc]
            source_rows = [
                ("scope:" + r["chapter_code"], r["chapter_name_en"])
                for r in data[dataset]["records"]
            ]
            basis = "PDF_ENGLISH_INDEX_NAME_COMPARISON_VI_NORMALIZATION_RETAINED"
        else:
            with fitz.open(path) as doc:
                pages = [p.get_text() for p in doc]
            source_rows = (
                [("gir:" + r["id"], r["text_vi"]) for r in data[dataset]]
                if dataset == "gir"
                else [
                    ("scope:" + r["chapter_code"], r["search_text_vi"])
                    for r in data[dataset]["records"]
                ]
            )
            basis = "PDF_TEXT_LAYER_COMPARISON"
        for rid, text in source_rows:
            proof[rid] = {
                "document": path.name,
                "sha256": hashes[relative],
                "basis": basis,
                **locate(text, pages),
            }
    ids = {n["id"] for n in nodes}
    broken = [e["id"] for e in edges if e["source"] not in ids or e["target"] not in ids]
    if broken:
        raise ValueError(f"Broken endpoints: {broken[:5]}")
    children = defaultdict(list)
    for e in edges:
        if e["relation"] == "CONTAINS":
            children[e["source"]].append(e["target"])
    visited, active = set(), set()

    def visit(nid):
        if nid in active:
            raise ValueError(f"Hierarchy cycle: {nid}")
        if nid in visited:
            return
        active.add(nid)
        for child in children[nid]:
            visit(child)
        active.remove(nid)
        visited.add(nid)

    for nid in ids:
        visit(nid)
    comparison = [dict(id=rid, **p) for rid, p in proof.items() if "word_trigram_coverage" in p]
    review_required = [p for p in comparison if p["word_trigram_coverage"] < 0.75]
    report = {
        "source_records": len(proof),
        "graph_nodes": len(ids),
        "graph_edges": len(edges),
        "broken_endpoints": [],
        "hierarchy_cycles": [],
        "relations": dict(Counter(e["relation"] for e in edges)),
        "source_comparison": comparison,
        "review_required": review_required,
        "semantic_scope": "All edges checked for integrity; PDF context scopes rebuilt. Imported reference/Notes relations are retained, not claimed reinterpreted legal semantics.",
        "ocr_limitation": "TT85 Apple Vision language en-US; spelling discrepancies require visual review, not automatic rewriting.",
    }
    write_json(
        ROOT / "data/normalized/PDF_SOURCE_PROVENANCE.json",
        {"version": 1, "pdf_hashes": hashes, "records": proof},
    )
    write_json(RUN / "full_pdf_audit.json", report)
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in {"source_comparison", "review_required"}},
            ensure_ascii=False,
        )
    )
    print(
        "review_required",
        len(review_required),
        Counter(p["id"].split(":")[0] for p in review_required),
    )


if __name__ == "__main__":
    main()
