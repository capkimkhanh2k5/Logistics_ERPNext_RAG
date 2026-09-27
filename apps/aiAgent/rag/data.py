"""Allowlisted source adapters and immutable corpus artifacts."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
SOURCES = {
    "tt31": "TT31/SECTION_XVI_RAG_INGEST.jsonl",
    "master": "TT31/SECTION_XVI_MASTER_NORMALIZED.jsonl",
    "schema": "TT31/SECTION_XVI_RAG_SCHEMA.json",
    "gir": "6_GIR /GIR_RAG_VI_COMBINED.jsonl",
    "tt85": "TT85/tt85_rag_chunks_source.jsonl",
    "forms": "TT85/tt85_forms_source.json",
    "articles": "TT85/tt85_articles_source.json",
    "tt85_metadata": "TT85/tt85_metadata_source.json",
    "scope": "HS_Index/HS_2022_SCOPE_INDEX_VI_FINAL.json",
    "nodes": "TT31/SECTION_XVI_GRAPH_STRUCTURAL_NODES.jsonl",
    "edges": "TT31/SECTION_XVI_GRAPH_EDGES.jsonl",
}
GOLD = ROOT / "data/test/HS_ELECTRONICS_GOLD_TESTSET_50_VERIFIED.jsonl"


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def read(path: Path) -> Any:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def config() -> dict:
    return yaml.safe_load((ROOT / "config/rag.yaml").read_text())


def normalize_code(value: str) -> str:
    if not re.fullmatch(r"(?:\d{4}|\d{6}|\d{8}|\d{2}\.\d{2}|\d{4}\.\d{2}(?:\.\d{2})?)", value):
        raise ValueError(f"Invalid HS code: {value}")
    return value.replace(".", "")


def source_files() -> dict:
    return {key: read(NORMALIZED / path) for key, path in SOURCES.items()}


def audit() -> dict:
    data = source_files()
    validator = jsonschema.Draft202012Validator(data["schema"])
    for record in data["master"]:
        validator.validate(record)
    masters = {r["record_id"]: r for r in data["master"]}
    ids = {r["id"] for r in data["tt31"]} | {n["node_id"] for n in data["nodes"]}
    assert len(masters) == len(data["master"])
    for r in data["tt31"]:
        assert r["text"] == masters[r["id"]]["retrieval"]["embedding_text_vi"]
    broken = [
        e["edge_id"]
        for e in data["edges"]
        if e["source_id"] not in ids or e["target_id"] not in ids
    ]
    assert not broken, f"Broken graph endpoints: {broken}"
    quality = {}
    for key, id_field, text_field in [
        ("tt31", "id", "text"),
        ("gir", "id", "text_vi"),
        ("tt85", "chunk_id", "text"),
    ]:
        rows = data[key]
        assert len({r[id_field] for r in rows}) == len(rows), f"Duplicate IDs: {key}"
        assert all(r[text_field].strip() for r in rows), f"Empty content: {key}"
        quality[key] = {
            "count": len(rows),
            "duplicate_wording": len(rows) - len({r[text_field] for r in rows}),
            "short_ids": [r[id_field] for r in rows if len(r[text_field]) < 40],
        }
    codes = {r["metadata"]["code"] for r in data["tt31"] if r["metadata"].get("code")}
    gold = read(GOLD)
    missing = [r["test_id"] for r in gold if r["expected_hs_8"] not in codes]
    assert not missing, f"Gold codes missing: {missing}"
    raw = ROOT / "data/raw/ThongTu_85-2026_TT-BTC.docx"
    hash_matches = (
        hashlib.sha256(raw.read_bytes()).hexdigest() == data["tt85_metadata"]["source_sha256"]
    )
    assert hash_matches, "TT85 source hash mismatch"
    result = {
        "quality": quality,
        "scope_count": len(data["scope"]["records"]),
        "graph_nodes": len(ids),
        "graph_edges": len(data["edges"]),
        "broken_endpoints": broken,
        "gold_count": len(gold),
        "unique_gold_codes": len({g["expected_hs_8"] for g in gold}),
        "gold_missing": missing,
        "tt85_source_hash_matches": hash_matches,
        "legal_verification": "LOCAL_METADATA_ONLY",
        "source_hashes": {
            path: hashlib.sha256((NORMALIZED / path).read_bytes()).hexdigest()
            for path in SOURCES.values()
        },
    }
    return result


def build_corpus() -> dict:
    cfg = config()
    report = audit()
    data = source_files()
    rows = []

    def add(
        dataset: str,
        source_id: str,
        text: str,
        embedding_text: str,
        role: str,
        metadata: dict,
        locator: dict,
        **fields: Any,
    ) -> None:
        rows.append(
            {
                "id": f"{dataset}:{source_id}",
                "source_id": source_id,
                "dataset": dataset,
                "source_text": text,
                "embedding_text": embedding_text,
                "lexical_text": embedding_text,
                "role": role,
                "metadata": metadata,
                "locator": locator,
                "input_hash": digest(embedding_text),
                **fields,
            }
        )

    masters = {r["record_id"]: r for r in data["master"]}
    for r in data["tt31"]:
        m = masters[r["id"]]
        md = r["metadata"]
        role = "candidate" if md["layer"] == "tariff" else "evidence"
        add(
            "tt31",
            r["id"],
            m.get("source_text_vi") or m["text_vi"],
            r["text"],
            role,
            m,
            m["source"],
            code=md.get("code"),
            level=md.get("level"),
            chapter=md.get("chapter"),
            heading=md.get("heading"),
            normalized_text=m["text_vi"],
            effective_from=None,
            effective_to=None,
        )
    # Context joins reviewed against the ordered source text; atomic wording stays intact.
    gir_context = {
        "GIR_3_NOTE_009": ["GIR_3_NOTE_008", "GIR_3_NOTE_009", "GIR_3_NOTE_MERGED_03"],
        "GIR_3_NOTE_017": ["GIR_3_NOTE_016", "GIR_3_NOTE_017"],
        "GIR_3_NOTE_038": ["GIR_3_NOTE_037", "GIR_3_NOTE_038"],
        "GIR_3_NOTE_040": ["GIR_3_NOTE_039", "GIR_3_NOTE_040"],
        "GIR_3_NOTE_047": ["GIR_3_NOTE_MERGED_06", "GIR_3_NOTE_047"],
        "GIR_3_NOTE_049": ["GIR_3_NOTE_048", "GIR_3_NOTE_049"],
        "GIR_5_NOTE_010": ["GIR_5_NOTE_009", "GIR_5_NOTE_010"],
        "GIR_5_NOTE_014": ["GIR_5_NOTE_009", "GIR_5_NOTE_014"],
        "GIR_5_NOTE_016": ["GIR_5_NOTE_016", "GIR_5_NOTE_017"],
    }
    gir_by_id = {r["id"]: r for r in data["gir"]}
    for r in data["gir"]:
        context_ids = gir_context.get(r["id"], [r["id"]])
        context = [gir_by_id[key] for key in context_ids]
        if any(c["rule"] != r["rule"] for c in context):
            raise ValueError("GIR context crosses a rule boundary")
        text = f"GIR Quy tắc {r['rule']} {r.get('subrule') or ''} | {r['dataset_layer']} | "
        text += "\n".join(c["text_vi"] for c in context)
        add(
            "gir",
            r["id"],
            r["text_vi"],
            text,
            "evidence",
            {**r, "context_source_ids": context_ids},
            {
                "document": r["source"],
                "pages": r["source_pages"],
                "context_pages": sorted({page for c in context for page in c["source_pages"]}),
                "context_source_ids": context_ids,
            },
            effective_from=None,
            effective_to=None,
        )
    for r in data["tt85"]:
        article = next(a for a in data["articles"] if a["article_no"] == r["article_no"])
        units = {u["label"]: u for u in article["units"]}
        parts = r["unit_label"].split(".")
        parents = [
            units[".".join(parts[:i])] for i in range(1, len(parts)) if ".".join(parts[:i]) in units
        ]
        # Short clause headers need their immediate source children, not unrelated next articles.
        children = [
            u
            for u in article["units"]
            if u["label"].startswith(r["unit_label"] + ".")
            and len(u["label"].split(".")) == len(parts) + 1
        ]
        context = parents + ([r] if not children or len(r["text"]) >= 50 else [r, *children[:2]])
        ids = [u.get("unit_id", u.get("chunk_id")) for u in context]
        text = f"{r['document_no']} | Điều {r['article_no']}: {r['article_title']} | "
        text += "\n".join(u["text"] for u in context)
        add(
            "tt85",
            r["chunk_id"],
            r["text"],
            text,
            "evidence",
            {**r, "context_source_ids": ids},
            {
                "document": r["document_no"],
                "article": r["article_no"],
                "unit_level": r["unit_level"],
                "unit_label": r["unit_label"],
                "context_source_ids": ids,
                "file": "data/raw/ThongTu_85-2026_TT-BTC.docx",
            },
            effective_from=r["effective_from"],
            effective_to=None,
        )
    for form in data["forms"]:
        text = f"Mẫu {form['form_no']} | {form['code']} | {form['title']}\n"
        text += "Các trường: " + "; ".join(form["fields"])
        add(
            "tt85",
            "TT85-FORM-" + form["form_no"],
            text,
            "85/2026/TT-BTC | Phụ lục | " + text,
            "evidence",
            form,
            {
                "document": "85/2026/TT-BTC",
                "appendix": True,
                "form_no": form["form_no"],
                "form_code": form["code"],
                "file": "data/raw/ThongTu_85-2026_TT-BTC.docx",
                "representation": "EXTRACTED_FORM_TITLE_AND_FIELDS",
            },
            effective_from=data["tt85_metadata"]["effective_from"],
            effective_to=None,
        )
    for r in data["scope"]["records"]:
        add(
            "scope",
            r["chapter_code"],
            r["search_text_vi"],
            r["search_text_vi"],
            "scope",
            r,
            {"document": r["source_vi"], "chapter": r["chapter_code"]},
            chapter=r["chapter_code"],
            effective_from=None,
            effective_to=None,
        )
    node_ids = {r["id"] for r in rows if r["dataset"] == "tt31"}
    nodes = [{"id": r["id"], "metadata": r["metadata"]} for r in rows if r["dataset"] == "tt31"]
    for node in data["nodes"]:
        nodes.append({"id": "tt31:" + node["node_id"], "metadata": node})
        node_ids.add("tt31:" + node["node_id"])
    edges = [
        {
            "id": e["edge_id"],
            "source": "tt31:" + e["source_id"],
            "target": "tt31:" + e["target_id"],
            "relation": e["relation"],
            "metadata": e["metadata"],
        }
        for e in data["edges"]
    ]
    assert all(e["source"] in node_ids and e["target"] in node_ids for e in edges)
    manifest = {
        "strategy": cfg["chunk_strategy"],
        "source_hashes": report["source_hashes"],
        "count": len(rows),
        "roles": dict(Counter(r["role"] for r in rows)),
        "records_hash": digest(rows),
        "edges_hash": digest(edges),
    }
    snapshot = digest(manifest)[:24]
    bundle = {
        "snapshot": snapshot,
        "manifest": manifest,
        "records": rows,
        "nodes": nodes,
        "edges": edges,
    }
    write_json(ROOT / "artifacts/corpus.json", bundle)
    return bundle


def load_corpus() -> dict:
    bundle = read(ROOT / "artifacts/corpus.json")
    assert bundle["manifest"]["records_hash"] == digest(bundle["records"]), "Corpus hash mismatch"
    assert bundle["manifest"]["edges_hash"] == digest(bundle["edges"]), "Graph hash mismatch"
    return bundle
