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
    "tt31_section_xvi": "TT31/Section-XVI/SECTION_XVI_RAG_INGEST.jsonl",
    "tt31_section_xvi_master": "TT31/Section-XVI/SECTION_XVI_MASTER_NORMALIZED.jsonl",
    "tt31_section_xvi_schema": "TT31/Section-XVI/SECTION_XVI_RAG_SCHEMA.json",
    "tt31_section_xiv": "TT31/Section-XIV/SECTION_XIV_RAG_INGEST.jsonl",
    "tt31_section_xiv_master": "TT31/Section-XIV/SECTION_XIV_MASTER_NORMALIZED.jsonl",
    "tt31_section_xiv_nodes": "TT31/Section-XIV/SECTION_XIV_GRAPH_NODES.jsonl",
    "tt31_section_xiv_edges": "TT31/Section-XIV/SECTION_XIV_GRAPH_EDGES.jsonl",
    "tt31_section_xvii": "TT31/Section-XVII/SECTION_XVII_RAG_INGEST.jsonl",
    "tt31_section_xvii_master": "TT31/Section-XVII/SECTION_XVII_MASTER_NORMALIZED.jsonl",
    "tt31_section_xvii_edges": "TT31/Section-XVII/SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl",
    "gir": "6_GIR /GIR_RAG_VI_COMBINED.jsonl",
    "tt85": "TT85/tt85_rag_chunks_source.jsonl",
    "articles": "TT85/tt85_articles_source.json",
    "tt85_metadata": "TT85/tt85_metadata_source.json",
    "scope": "HS_Index/HS_2022_SCOPE_INDEX_VI_FINAL.json",
    "tt31_section_xvi_nodes": "TT31/Section-XVI/SECTION_XVI_GRAPH_STRUCTURAL_NODES.jsonl",
    "tt31_section_xvi_edges": "TT31/Section-XVI/SECTION_XVI_GRAPH_EDGES.jsonl",
}
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
    return {key: read(NORMALIZED / path) for key, path in SOURCES.items()}


def xiv_vietnamese_view(master: dict) -> str:
    """Format only this XIV record's normalized Vietnamese source fields."""
    code = master["hs"].get("code")
    own = master["text"].get("vi") or master["text"].get("source_raw_vi")
    parts = [f"Mã {code}." if code else ""]
    if own:
        parts.append(own)
    unit = master.get("unit", {}).get("vi")
    if unit:
        parts.append(f"Đơn vị: {unit}")
    if not any(parts):
        parts.append(f"Phần XIV, Chương {master['chapter']['code']}")
    return " ".join(" ".join(parts).split())


def xvii_vietnamese_view(master: dict) -> str:
    """Format only this XVII record's normalized Vietnamese source fields."""
    content = master["content"]
    code = master.get("code")
    parts = [f"Mã {code}." if code else ""]
    for field in (
        "title_vi_normalized",
        "description_vi_normalized",
        "legal_text_vi_normalized",
        "supplemental_text_normalized",
        "unit_vi_normalized",
    ):
        value = content.get(field)
        if value:
            parts.append(value)
    if not any(parts):
        terms = master.get("legal", {}).get("defined_terms_raw", [])
        if terms:
            parts.append(f"Thuật ngữ: {terms[0]}")
    if not any(parts):
        parts.append(f"Phần XVII, Chương {master['chapter']}")
    return " ".join(" ".join(parts).split())


def xvi_vietnamese_view(master: dict) -> str:
    """Use the normalized title and wording of one XVI source record only."""
    title = (master.get("title_vi") or "").strip()
    wording = (master.get("text_vi") or master.get("source_text_vi") or "").strip()
    if master.get("layer") == "context":
        return wording
    if master.get("layer") == "tariff":
        return f"{master['code_display']} — {wording}"
    return title if wording and wording in title else " ".join(p for p in (title, wording) if p)


def audit() -> dict:
    data = source_files()
    validator = jsonschema.Draft202012Validator(data["tt31_section_xvi_schema"])
    for record in data["tt31_section_xvi_master"]:
        validator.validate(record)
    masters = {r["record_id"]: r for r in data["tt31_section_xvi_master"]}
    ids = {r["id"] for r in data["tt31_section_xvi"]} | {
        n["node_id"] for n in data["tt31_section_xvi_nodes"]
    }
    assert len(masters) == len(data["tt31_section_xvi_master"])
    for r in data["tt31_section_xvi"]:
        assert r["text"] == masters[r["id"]]["retrieval"]["embedding_text_vi"]
        assert r["text"] == xvi_vietnamese_view(masters[r["id"]])
    broken = [
        e["edge_id"]
        for e in data["tt31_section_xvi_edges"]
        if e["source_id"] not in ids or e["target_id"] not in ids
    ]
    assert not broken, f"Broken graph endpoints: {broken}"
    quality = {}
    for key, id_field, text_field in [
        ("tt31_section_xvi", "id", "text"),
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
    for key, id_field in [
        ("tt31_section_xiv", "source_record_id"),
        ("tt31_section_xvii", "source_node_id"),
    ]:
        records = data[key]
        assert len({r[id_field] for r in records}) == len(records)
        assert all(r["content"]["embedding_text"].strip() for r in records)
        quality[key] = {
            "count": len(records),
            "duplicate_wording": len(records)
            - len({r["content"]["embedding_text"] for r in records}),
        }
    xvii_master = {r["id"]: r for r in data["tt31_section_xvii_master"]}
    assert all(
        r["language_profile"] == "vi"
        and r["content"]["embedding_text"]
        == r["content"]["fts_text"]
        == xvii_vietnamese_view(xvii_master[r["source_node_id"]])
        for r in data["tt31_section_xvii"]
    ), "Section XVII search inputs must use the verified Vietnamese view"
    xiv_master = {r["id"]: r for r in data["tt31_section_xiv_master"]}
    assert all(
        r.get("search_language") == "vi"
        and r["content"]["embedding_text"]
        == r["content"]["sparse_text"]
        == r["content"]["search_text"]
        == xiv_vietnamese_view(xiv_master[r["source_record_id"]])
        for r in data["tt31_section_xiv"]
    ), "Section XIV search inputs must use the verified Vietnamese view"
    codes = {r["metadata"]["code"] for r in data["tt31_section_xvi"] if r["metadata"].get("code")}
    codes |= {r["metadata"].get("hs_code_compact") for r in data["tt31_section_xiv"]}
    codes |= {r["metadata"].get("hs8_compact") for r in data["tt31_section_xvii"]}
    gold = [
        r
        for part in ("train", "test")
        for path in sorted((GOLD / "hs" / part).glob("*.jsonl"))
        for r in read(path)
    ]
    missing = [r["record_id"] for r in gold if r["expected_hs_8"] not in codes]
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
        "graph_edges": sum(
            len(data[k])
            for k in ("tt31_section_xvi_edges", "tt31_section_xiv_edges", "tt31_section_xvii_edges")
        ),
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

    masters = {r["record_id"]: r for r in data["tt31_section_xvi_master"]}
    for r in data["tt31_section_xvi"]:
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
    for node in data["tt31_section_xvi_nodes"]:
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
        for e in data["tt31_section_xvi_edges"]
    ]
    # Each Section uses its own export schema; preserve the original fields in metadata.
    for section, key in [("XIV", "tt31_section_xiv"), ("XVII", "tt31_section_xvii")]:
        master = {r["id"]: r for r in data[key + "_master"]}
        for r in data[key]:
            sid = r.get("source_record_id", r.get("source_node_id"))
            m = master[sid]
            md = r["metadata"]
            kind = r.get("record_type", r.get("document_type"))
            code = md.get("hs_code_compact", md.get("code_compact"))
            if kind == "chapter":
                code = md["chapter"]
            level = len(code) if code and code.isdigit() and len(code) in (2, 4, 6, 8) else None
            role = (
                "candidate"
                if kind in ("heading", "subheading", "hs_code")
                else "scope"
                if kind in ("chapter", "section", "subchapter")
                else "evidence"
                if kind
                in ("section_note", "chapter_note", "subheading_note", "definition", "legal_term")
                else "context"
            )
            if section == "XIV":
                source_text = (
                    m["text"].get("source_raw_vi")
                    or m["text"]["vi"]
                    or r["content"]["embedding_text"]
                )
                locator = m["source"]
                legal = r.get("legal_context", {})
                notes = legal.get("effective_note_ids", [])
                chunk_type = (
                    "tariff_footnote"
                    if kind == "tariff_footnote"
                    else kind
                    if kind.endswith("_note")
                    else "tariff_entry"
                    if level
                    else None
                )
                source = m["source"]
            else:
                raw = r["content"]["raw_authoritative"]
                source_text = (
                    m["content"].get("legal_text_vi_normalized")
                    or m["content"].get("description_vi_normalized")
                    or m["content"].get("supplemental_text_normalized")
                    or raw.get("legal_text_vi_raw")
                    or raw.get("description_vi_raw")
                    or raw.get("supplemental_text_raw")
                    or r["content"]["embedding_text"]
                )
                locator = r["provenance"]
                notes = r["graph"].get("governing_note_ids", [])
                chunk_type = (
                    kind
                    if kind.endswith("_note")
                    else "chapter_note"
                    if kind in ("definition", "legal_term")
                    else "tariff_entry"
                    if level
                    else None
                )
                source = m["provenance"]
            add(
                "tt31",
                sid,
                source_text,
                r["content"]["embedding_text"],
                role,
                {
                    "original": m,
                    "export_metadata": md,
                    "original_type": kind,
                    "governing_note_ids": notes,
                    "exact_terms": r.get("exact_tokens", r["content"].get("exact_keys", [])),
                },
                locator,
                section=section,
                chapter=md.get("chapter"),
                code=code if level else None,
                level=level,
                heading=(code[:4] if level and level >= 4 else None),
                hs6=(code[:6] if level and level >= 6 else None),
                ahtn8=code if level == 8 else None,
                chunk_type=chunk_type,
                source=source,
                effective_from=md.get("current_application_from"),
                effective_to=None,
                legal_status=md.get("legal_status", "UNVERIFIED"),
            )
        # External graph endpoints stay stubs; links to loaded codes are resolved below.
        graph_rows = (
            data["tt31_section_xiv_nodes"] if section == "XIV" else data["tt31_section_xvii_master"]
        )
        for node in graph_rows:
            sid = node.get("node_id", node.get("id"))
            nid = "tt31:" + sid
            if nid not in node_ids:
                nodes.append({"id": nid, "metadata": node})
                node_ids.add(nid)
        for e in data[key + "_edges"]:
            source = e.get("source_node_id", e.get("from_id"))
            target = e.get("target_node_id", e.get("to_id"))
            relation = e["relation"]
            if relation == "PARENT_OF" or "CONTAINS" in relation:
                relation = "CONTAINS"
            edges.append(
                {
                    "id": section + ":" + e.get("edge_id", e.get("id")),
                    "source": "tt31:" + source,
                    "target": "tt31:" + target,
                    "relation": relation,
                    "metadata": e,
                }
            )
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
        "count": len(rows),
        "roles": dict(Counter(r["role"] for r in rows)),
        "namespaces": dict(Counter(r["namespace"] for r in rows)),
        "sections": dict(Counter(r["section"] or "GLOBAL" for r in rows)),
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
