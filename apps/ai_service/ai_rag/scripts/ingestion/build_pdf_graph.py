#!/usr/bin/env python3
"""Materialize source context scopes from registered PDF tables; never read evaluation data."""

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.graph.legal_evidence import consolidated_bindings  # noqa: E402
from rag.ingestion.pdf_graph import table_rows, validate_extraction  # noqa: E402
from rag.ingestion.pdf_wording import (  # noqa: E402
    apply_wording_reviews,
    wording_proof,
)
from rag.ingestion.sources import (  # noqa: E402
    canonical_tariff,
    first,
    read_source,
    source_manifest,
)
from rag.utils.files import digest, write_json  # noqa: E402


def normalized(text):
    text = unicodedata.normalize("NFKD", text.lower().replace("đ", "d"))
    return " ".join(
        re.findall(r"[a-z0-9]+", "".join(c for c in text if not unicodedata.combining(c)))
    )


def materialize(rows, records, section):
    codes = {r["code"]: r for r in records if r.get("code")}
    registered_chapters = {code[:2] for code in codes}
    contexts = [r for r in records if r["role"] == "context"]
    nodes, edges, found = {}, [], set()
    stack: list[dict] = []
    scopes: dict[str, list[str]] = {}
    active_heading = None
    for row in rows:
        code, depth = row["code"], row["depth"]
        if code:
            if code not in codes:
                if code[:2] in registered_chapters:
                    raise ValueError(
                        f"Printed source parent/leaf is missing from registered data: {code}"
                    )
                stack, active_heading = [], None
                continue
            found.add(code)
            if len(code) == 4 or depth is None:
                stack = []
                active_heading = code
                depth = 0
            if active_heading is None:
                active_heading = first(codes[code], "heading", default=code)
        elif active_heading is None or depth is None:
            continue
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()
        if code:
            if codes[code].get("level") == 8:
                for ctx in stack:
                    edges.append(
                        {
                            "source": ctx["id"],
                            "target": codes[code]["id"],
                            "relation": "CONTEXT_FOR",
                            "metadata": {
                                "basis": "PDF_PRINTED_ROW_HIERARCHY",
                                "section": section,
                                "context_locator": ctx["locator"],
                                "target_locator": row["locator"],
                            },
                        }
                    )
                    scopes.setdefault(ctx["id"], []).append(code)
            continue
        raw = re.sub(r"^\s*[-–—\s]+", "", row["text_vi"]).strip()
        if not raw:
            english = re.sub(r"^\s*[-–—\s]+", "", row["text_en"]).strip()
            matches = [
                r["source_text"]
                for r in contexts
                if normalized(
                    first(
                        r["metadata"],
                        "text.en",
                        "text_en",
                        "content.description_en_normalized",
                        default="",
                    )
                )
                == normalized(english)
            ]
            raw = matches[0] if matches and len(set(matches)) == 1 else english
            if not raw:
                raise ValueError(f"Empty PDF context wording: {row['locator']}")
        # Existing normalization may correct OCR spelling, but must match the cited PDF wording.
        candidates = [
            (SequenceMatcher(None, normalized(raw), normalized(r["source_text"])).ratio(), r)
            for r in contexts
        ]
        best = max(candidates, key=lambda x: x[0], default=(0, None))
        text = best[1]["source_text"] if best[1] is not None and best[0] >= 0.94 else raw
        nid = "tt31:PDF_CTX:" + digest(row["locator"])[:24]
        nodes[nid] = {
            "id": nid,
            "metadata": {
                "role": "context",
                "section": section,
                "source_text": text,
                "raw_pdf_text": row["text_vi"],
                "source_explicit": True,
                "depth": depth,
                "locator": row["locator"],
                "normalization_similarity": round(best[0], 4),
            },
        }
        stack.append({"id": nid, "depth": depth, "locator": row["locator"]})
    expected = {r["code"] for r in records if r.get("level") == 8}
    missing = sorted(expected - found)
    if missing:
        raise ValueError(f"Unverified PDF source leaves in {section}: {missing}")
    used = {e["source"] for e in edges}
    return (
        [v for k, v in nodes.items() if k in used],
        edges,
        {
            "section": section,
            "verified_hs8": len(expected),
            "contexts": len(used),
            "context_edges": len(edges),
            "scopes": scopes,
            "missing_hs8": missing,
            "unused_pdf_labels": [v for k, v in nodes.items() if k not in used],
            "raster_depth_corrections": sum(
                r["depth"] != r["depth_en"] for r in rows if r["depth_en"] is not None
            ),
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="run_pdf_graph_v4")
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or args.run_id in {".", ".."}:
        raise ValueError("Run ID must be a directory name")
    manifest = source_manifest(ROOT)
    reviews = read_source(ROOT / "data/normalized" / manifest["files"]["tt31_pdf_wording_reviews"])
    report, nodes, edges, hashes, bindings = [], [], [], {}, []
    artifact = ROOT / "artifacts/experiments" / args.run_id
    artifact.mkdir(parents=True, exist_ok=True)
    for source in manifest["tariffs"]:
        masters = read_source(ROOT / "data/normalized" / manifest["files"][source["master"]])
        masters = {first(r, "id", "record_id"): r for r in masters}
        exported = read_source(ROOT / "data/normalized" / manifest["files"][source["records"]])
        records = [canonical_tariff(r, masters.get(r["id"])) for r in exported]
        section = records[0]["section"]
        path = ROOT / source["source_pdf"]
        rows, extraction = table_rows(path)
        validate_extraction(rows, extraction, extraction["sha256"])
        rows, extraction = apply_wording_reviews(rows, extraction, reviews)
        by_code = {r["code"]: r for r in records if r.get("code")}
        for row in rows:
            if row.get("wording_review_id"):
                wording_proof(row, by_code[row["code"]], reviews)
        bindings.extend(consolidated_bindings(rows, records, extraction))
        ns, es, audit = materialize(rows, records, section)
        nodes.extend(ns)
        edges.extend(es)
        report.append({**audit, "extraction": extraction})
        hashes[source["source_pdf"]] = extraction["sha256"]
        write_json(artifact / (section + "_pdf_rows.json"), rows)
        print(
            json.dumps(
                {k: v for k, v in audit.items() if k not in {"scopes", "unused_pdf_labels"}}
            ),
            flush=True,
        )
    graph = {
        "version": 2,
        "basis": "AUTHORITATIVE_PDF_GEOMETRY_AND_PRINTED_INDENTATION",
        "pdf_hashes": hashes,
        "nodes": nodes,
        "edges": edges,
        "legal_evidence_bindings": bindings,
        "extractions": {item["extraction"]["document"]: item["extraction"] for item in report},
    }
    write_json(ROOT / "data/normalized/TT31/PDF_SOURCE_GRAPH.json", graph)
    write_json(artifact / "pdf_scope_audit.json", report)
    print(
        "PDF graph ready",
        len(nodes),
        len(edges),
        "bindings",
        len(bindings),
        Counter(n["metadata"]["section"] for n in nodes),
    )


if __name__ == "__main__":
    main()
