"""Allowlisted source adapters and immutable corpus artifacts."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from rag.sources import (
    canonical_edge,
    canonical_tariff,
    context_scope_edges,
    first,
    source_manifest,
    source_path,
)

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED = ROOT / "data" / "normalized"
SOURCES = source_manifest(ROOT)["files"]
GOLD = ROOT / "data/verified"


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
    if not re.fullmatch(
        r"(?:\d{2}|\d{4}|\d{6}|\d{8}|\d{2}\.\d{2}|\d{4}\.\d{2}(?:\.\d{2})?)", value
    ):
        raise ValueError(f"Invalid HS code: {value}")
    return value.replace(".", "")


def source_files() -> dict:
    return {
        key: read(source_path(NORMALIZED, path))
        for key, path in source_manifest(ROOT)["files"].items()
    }


def audit() -> dict:
    data = source_files()
    registered = source_manifest(ROOT)
    validator = jsonschema.Draft202012Validator(data["tt31_unified_rag_schema"])
    taxonomy = {r["chapter_code"]: r["section_code"] for r in data["scope"]["records"]}
    quality, codes, broken = {}, set(), []
    all_ids = set()
    graph_edges = 0
    for source in registered["tariffs"]:
        records = data[source["records"]]
        ids = {r["id"] for r in records}
        if len(ids) != len(records):
            raise ValueError("Duplicate tariff source IDs")
        for r in records:
            validator.validate(r)
            md = r["metadata"]
            if md.get("chapter") and taxonomy.get(md["chapter"]) != md["section"]:
                raise ValueError(f"Source Section/Chapter mismatch: {r['id']}")
            if r["id"] != r["source_id"] or r["text"] != r["content"]["embedding_text"]:
                raise ValueError(f"Inconsistent canonical source record: {r['id']}")
            if not r["text"].strip() or not r["provenance"]:
                raise ValueError(f"Missing source text or provenance: {r['id']}")
            code = first(md, "code_compact", "code")
            if code:
                codes.add(str(code).replace(".", ""))
        for n in data.get(source.get("nodes"), []):
            ids.add(first(n, "node_id", "id", "record_id"))
        all_ids.update(ids)
        edges = [canonical_edge(e, "") for e in data.get(source.get("edges"), [])]
        graph_edges += len(edges)
        broken.extend(e for e in edges if e["source"] not in ids or e["target"] not in ids)
        quality[source["records"]] = {
            "count": len(records),
            "duplicate_wording": len(records) - len({r["text"] for r in records}),
            "short_ids": [r["id"] for r in records if len(r["text"]) < 40],
        }
    if broken:
        raise ValueError("Broken source graph endpoints")
    for key, id_field, text_field in [("gir", "id", "text_vi"), ("tt85", "chunk_id", "text")]:
        rows = data[key]
        if len({r[id_field] for r in rows}) != len(rows) or any(
            not r[text_field].strip() for r in rows
        ):
            raise ValueError(f"Invalid legal source records: {key}")
        quality[key] = {
            "count": len(rows),
            "duplicate_wording": len(rows) - len({r[text_field] for r in rows}),
            "short_ids": [r[id_field] for r in rows if len(r[text_field]) < 40],
        }
    gold = [
        r
        for part in ("train", "test")
        for path in sorted((GOLD / "hs" / part).glob("*.jsonl"))
        for r in read(path)
    ]
    raw = ROOT / "data/raw/ThongTu_85-2026_TT-BTC.docx"
    hash_matches = (
        hashlib.sha256(raw.read_bytes()).hexdigest() == data["tt85_metadata"]["source_sha256"]
    )
    if not hash_matches:
        raise ValueError("TT85 source hash mismatch")
    return {
        "quality": quality,
        "scope_count": len(taxonomy),
        "graph_nodes": len(all_ids),
        "graph_edges": graph_edges,
        "broken_endpoints": [],
        "gold_count": len(gold),
        "unique_gold_codes": len({g["expected_hs_8"] for g in gold}),
        "gold_missing": [r["record_id"] for r in gold if r["expected_hs_8"] not in codes],
        "tt85_source_hash_matches": hash_matches,
        "legal_verification": "LOCAL_METADATA_ONLY",
        "source_hashes": {
            path: hashlib.sha256(source_path(NORMALIZED, path).read_bytes()).hexdigest()
            for path in registered["files"].values()
        },
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
    edges.extend(context_scope_edges(rows, masters))
    annotations = source.get("annotations")
    if annotations:
        by_code = {r["code"]: r for r in rows if r["code"]}
        for code, info in data[annotations["file"]].items():
            row = by_code.get(code)
            if row is None:
                raise ValueError(f"Annotation has no registered source code: {code}")
            parts = [
                f"{label}: {info[field]}"
                for field, label in annotations["fields"].items()
                if info.get(field) and info[field] not in annotations.get("omit_values", [])
            ]
            if not parts:
                continue
            nid = "tt31:SOURCE_ANNOTATION_" + digest([annotations["file"], code])[:20]
            locator = {
                "source_key": annotations["file"],
                "source_code": code,
                "document": annotations["source_document"],
                "page": info.get("page"),
                "basis": "REGISTERED_SOURCE_ANNOTATION",
            }
            nodes[nid] = {
                "id": nid,
                "metadata": {
                    "role": "context",
                    "section": row["section"],
                    "chapter": row["chapter"],
                    "source_text": "\n".join(parts),
                    "locator": locator,
                    "annotation": info,
                },
            }
            edges.append(
                {
                    "source": nid,
                    "target": row["id"],
                    "relation": "CONTEXT_FOR",
                    "metadata": {"basis": "REGISTERED_SOURCE_ANNOTATION", "locator": locator},
                }
            )
    unique = {}
    for e in edges:
        key = (e["source"], e["relation"], e["target"])
        unique.setdefault(key, {**e, "id": "SOURCE_EDGE:" + digest(key)[:24]})
    return rows, list(nodes.values()), list(unique.values())


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

    registered = source_manifest(ROOT)
    nodes, edges = [], []
    for source in registered["tariffs"]:
        source_rows, source_nodes, source_edges = tariff_bundle(source, data)
        rows.extend(source_rows)
        nodes.extend(source_nodes)
        edges.extend(source_edges)

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
    registered_chapters = {r["chapter"] for r in rows if r.get("level") == 8}
    for r in data["scope"]["records"]:
        r = {
            **r,
            "in_scope": r["chapter_code"] in registered_chapters,
            "scope_status": "IN_SCOPE"
            if r["chapter_code"] in registered_chapters
            else "OUT_OF_SCOPE",
        }
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
    node_ids = {n["id"] for n in nodes}
    supported = {
        "gir_rule",
        "gir_explanation",
        "section_note",
        "chapter_note",
        "subheading_note",
        "tariff_entry",
        "tariff_footnote",
        "legal_clause",
    }
    for row in rows:
        row["input_hash"] = digest(row["embedding_text"])
        md = row["metadata"]
        dataset = row["dataset"]
        row["namespace"] = "legal_classification" if dataset == "tt85" else "hs_classification"
        row.setdefault("section", md.get("section", md.get("section_code")))
        row.setdefault("hs6", md.get("hs6"))
        row.setdefault("ahtn8", md.get("ahtn8"))
        if dataset == "tt31" and "chunk_type" not in row:
            original = md.get("chunk_type")
            row["chunk_type"] = (
                "tariff_entry"
                if row.get("level")
                else "tariff_footnote"
                if md.get("original_type") == "tariff_footnote"
                else original
                if original in supported
                else None
            )
            if row["role"] == "evidence" and row["chunk_type"] is None:
                row["role"] = (
                    "context"  # Source footnotes are retained, not relabeled as statutory notes.
                )
        elif dataset == "gir":
            row["chunk_type"] = "gir_explanation" if "NOTE" in row["source_id"] else "gir_rule"
        elif dataset == "tt85":
            row["chunk_type"] = "legal_clause"
        elif dataset == "scope":
            row["chunk_type"] = None
            row["level"] = 2
            row["code"] = row["chapter"]
        row.setdefault("source", row["locator"])
        row.setdefault("legal_status", "UNVERIFIED")
        for field in (
            "namespace",
            "dataset",
            "chunk_type",
            "role",
            "section",
            "chapter",
            "heading",
            "hs6",
            "ahtn8",
            "source",
            "effective_from",
            "effective_to",
            "legal_status",
        ):
            row.setdefault(field, None)
        row["metadata"] = {
            **md,
            **{
                field: row[field]
                for field in (
                    "namespace",
                    "dataset",
                    "chunk_type",
                    "role",
                    "section",
                    "chapter",
                    "heading",
                    "hs6",
                    "ahtn8",
                    "source",
                    "effective_from",
                    "effective_to",
                    "legal_status",
                )
            },
        }
        if row["id"] not in node_ids and dataset == "tt31":
            nodes.append({"id": row["id"], "metadata": row["metadata"]})
            node_ids.add(row["id"])
    by_code = {r["code"]: r["id"] for r in rows if r["dataset"] == "tt31" and r.get("code")}
    for node in list(nodes):
        nid = node["id"]
        if "EXT" not in nid:
            continue
        md = node["metadata"]
        code = md.get("code_compact", md.get("code"))
        if code:
            target = by_code.get(str(code).replace(".", ""))
            if target and target != nid:
                edges.append(
                    {
                        "id": "RESOLVE:" + nid,
                        "source": nid,
                        "target": target,
                        "relation": "RESOLVES_TO",
                        "metadata": {"basis": "CODE_EQUALITY"},
                    }
                )
    # Some source exports connect AHTN8 directly to a heading when no HS6 row is printed.
    # Restore the logical six-digit step as a graph-only node, never fabricated legal text.
    explicit_hs6 = {r["code"] for r in rows if r.get("level") == 6}
    for row in rows:
        if row.get("level") != 8 or row["code"][:6] in explicit_hs6:
            continue
        code = row["code"][:6]
        nid = "tt31:DERIVED_HS6_" + code
        if nid not in node_ids:
            nodes.append(
                {
                    "id": nid,
                    "metadata": {
                        "level": 6,
                        "code": code,
                        "section": row["section"],
                        "chapter": row["chapter"],
                        "virtual": True,
                        "derivation": "AHTN8_PREFIX",
                        "legal_text_available": False,
                    },
                }
            )
            node_ids.add(nid)
            heading_id = by_code.get(code[:4])
            if heading_id:
                edges.append(
                    {
                        "id": "DERIVE_PARENT:" + code,
                        "source": heading_id,
                        "target": nid,
                        "relation": "CONTAINS",
                        "metadata": {"basis": "CODE_PREFIX_STRUCTURAL_DERIVATION"},
                    }
                )
        edges.append(
            {
                "id": "DERIVE_CHILD:" + row["id"],
                "source": nid,
                "target": row["id"],
                "relation": "CONTAINS",
                "metadata": {"basis": "CODE_PREFIX_STRUCTURAL_DERIVATION"},
            }
        )
    assert all(e["source"] in node_ids and e["target"] in node_ids for e in edges)
    manifest = {
        "strategy": cfg["chunk_strategy"],
        "source_hashes": report["source_hashes"],
        "source_manifest_hash": digest(registered),
        "graph_version": "source-context-v2",
        "count": len(rows),
        "roles": dict(Counter(r["role"] for r in rows)),
        "namespaces": dict(Counter(r["namespace"] for r in rows)),
        "sections": dict(Counter(r["section"] or "GLOBAL" for r in rows)),
        "records_hash": digest(rows),
        "edges_hash": digest(edges),
        "nodes_hash": digest(nodes),
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
    assert bundle["manifest"]["nodes_hash"] == digest(bundle["nodes"]), "Graph nodes hash mismatch"
    return bundle
