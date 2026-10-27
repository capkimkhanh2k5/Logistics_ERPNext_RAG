"""Adapters for source formats, independent of tariff chapters and product names."""

import hashlib
import json
from pathlib import Path
from typing import Any

from config.settings import ROOT
from rag.utils.files import digest, read

NORMALIZED = ROOT / "data" / "normalized"
GOLD = ROOT / "data/verified"

SOURCE_TYPES = [
    "tariff_entry",
    "gir_rule",
    "gir_explanation",
    "section_note",
    "chapter_note",
    "subheading_note",
    "tariff_footnote",
    "legal_clause",
    "technical_standard_item",
]

QA_CHUNK_TYPES = [
    "gir_rule",
    "gir_explanation",
    "section_note",
    "chapter_note",
    "subheading_note",
    "tariff_entry",
    "tariff_footnote",
    "legal_clause",
    "technical_standard_item",
]


def read_source(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def source_manifest(root: Path) -> dict:
    manifest = read_source(root / "config/source_manifest.json")
    if manifest.get("version") != 1 or not manifest.get("tariffs"):
        raise ValueError("Invalid source manifest")
    return manifest


def source_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Source path is missing or outside the registered root: {relative}")
    return path


def first(record: dict, *paths: str, default: Any = None) -> Any:
    for path in paths:
        value: Any = record
        for part in path.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        if value is not None and value != "":
            return value
    return default


def compact(value: Any) -> str | None:
    value = str(value or "").replace(".", "").strip()
    return value if value.isdigit() and len(value) in (2, 4, 6, 8) else None


def canonical_tariff(record: dict, master: dict | None = None) -> dict:
    """Project the unified export; the master is retained only for source provenance."""
    master = master or record
    md = record["metadata"]
    kind = record["document_type"]
    code = compact(first(md, "code_compact", "code", "hs_code_compact"))
    if kind == "chapter" and code is None:
        code = compact(md.get("chapter"))
    level = len(code) if code else None
    note_types = {"section_note", "chapter_note", "subheading_note", "definition", "legal_term"}
    role = (
        "candidate"
        if level in (4, 6, 8)
        else "scope"
        if kind in ("chapter", "section", "subchapter")
        else "evidence"
        if kind in note_types
        else "context"
    )
    chunk_type = (
        "tariff_entry"
        if level
        else kind
        if kind.endswith("_note")
        else (
            "chapter_note"
            if kind in ("definition", "legal_term")
            else "tariff_footnote"
            if kind == "tariff_footnote"
            else None
        )
    )
    raw_text = first(
        record,
        "content.raw_authoritative.source_text_vi",
        "content.raw_authoritative.text_vi",
        "content.raw_authoritative.legal_text_vi_raw",
        "content.raw_authoritative.description_vi_raw",
        "content.raw_authoritative.supplemental_text_raw",
    )
    text = first(
        master,
        "source_text_vi",
        "text.vi",
        "text_vi",
        "content.legal_text_vi_normalized",
        "content.description_vi_normalized",
        "content.supplemental_text_normalized",
        default=raw_text or record["text"],
    )
    locator = record["provenance"]
    notes = first(
        record, "graph.governing_note_ids", "legal_context.effective_note_ids", default=[]
    )
    return {
        "id": "tt31:" + record["id"],
        "source_id": record["id"],
        "dataset": "tt31",
        "source_text": text,
        "embedding_text": record["text"],
        "lexical_text": record["text"],
        "role": role,
        "namespace": "hs_classification",
        "code": code,
        "level": level,
        "section": md["section"],
        "chapter": md.get("chapter"),
        "heading": code[:4]
        if code and level and level >= 4
        else compact(first(md, "heading", "heading4")),
        "hs6": code[:6] if code and level and level >= 6 else None,
        "ahtn8": code if level == 8 else None,
        "chunk_type": chunk_type,
        "source": locator,
        "locator": locator,
        "effective_from": md.get("current_application_from"),
        "effective_to": None,
        "legal_status": md.get("legal_status", "UNVERIFIED"),
        "metadata": {
            **master,
            "original": master,
            "export_metadata": md,
            "original_type": kind,
            "governing_note_ids": notes,
            "exact_terms": record["content"]["exact_keys"],
            "source_hierarchy": record.get("hierarchy", {}),
            "source_graph": record.get("graph", {}),
        },
    }


def canonical_edge(edge: dict, namespace: str = "tt31:") -> dict:
    source = first(edge, "source_id", "source_node_id", "from_id", "source")
    target = first(edge, "target_id", "target_node_id", "to_id", "target")
    relation = edge["relation"]
    if not source or not target:
        raise ValueError("Graph edge has no endpoints")
    if relation == "CHILD_OF":
        source, target, relation = target, source, "CONTAINS"
    elif relation == "PARENT_OF" or "CONTAINS" in relation:
        relation = "CONTAINS"
    return {
        "source": namespace + source,
        "target": namespace + target,
        "relation": relation,
        "metadata": edge,
    }


SOURCES = source_manifest(ROOT)["files"]


def source_files() -> dict:
    return {
        key: read(source_path(NORMALIZED, path))
        for key, path in source_manifest(ROOT)["files"].items()
    }


def tariff_bundle(source: dict, data: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Adapt one registered source format into the shared record/node/edge contract."""
    masters = {first(r, "id", "record_id"): r for r in data.get(source.get("master"), [])}
    rows = [canonical_tariff(r, masters.get(r["id"])) for r in data[source["records"]]]
    nodes = {
        r["id"]: {
            "id": r["id"],
            "metadata": {
                **r["metadata"],
                "source_text": r["source_text"],
                "locator": r["locator"],
                "code": r["code"],
                "level": r["level"],
                "section": r["section"],
                "chapter": r["chapter"],
                "role": r["role"],
                "chunk_type": r["chunk_type"],
            },
        }
        for r in rows
    }
    for n in data.get(source.get("nodes"), []):
        nid = "tt31:" + first(n, "node_id", "id", "record_id")
        if nid not in nodes:
            nodes[nid] = {"id": nid, "metadata": n}
    edges = [canonical_edge(e) for e in data.get(source.get("edges"), [])]
    for row in rows:
        for note_id in row["metadata"].get("governing_note_ids", []):
            nid = "tt31:" + note_id
            if nid in nodes:
                edges.append(
                    {
                        "source": row["id"],
                        "target": nid,
                        "relation": "CONSTRAINED_BY",
                        "metadata": {
                            "basis": "SOURCE_GOVERNING_NOTE_IDS",
                            "locator": row["locator"],
                        },
                    }
                )
    if source.get("pdf_graph"):
        graph = data[source["pdf_graph"]]
        section = rows[0]["section"]
        for relative, expected in graph["pdf_hashes"].items():
            path = source_path(ROOT, relative)
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Authoritative PDF graph source changed: {relative}")
        # PDF edges replace legacy scope inference and manually enriched annotations.
        edges = [e for e in edges if e["relation"] not in {"CONTEXT_FOR", "CONTEXT_WITHIN"}]
        for node in graph["nodes"]:
            if node["metadata"]["section"] == section:
                nodes[node["id"]] = node
        edges.extend(e for e in graph["edges"] if e["metadata"]["section"] == section)
    unique: dict[tuple, dict] = {}
    for e in edges:
        key = (e["source"], e["relation"], e["target"])
        unique.setdefault(key, {**e, "id": "SOURCE_EDGE:" + digest(key)[:24]})
    return rows, list(nodes.values()), list(unique.values())
