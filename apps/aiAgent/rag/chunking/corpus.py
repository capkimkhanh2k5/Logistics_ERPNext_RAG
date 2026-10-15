"""Build source-preserving records, graph links and immutable corpus snapshots."""

from collections import Counter
from typing import Any

from config.retrieval import retrieval_config
from config.settings import ROOT
from rag.graph.legal_evidence import attach_bindings
from rag.ingestion.audit import audit
from rag.ingestion.sources import source_files, source_manifest, tariff_bundle
from rag.utils.files import digest, read, write_json


def build_corpus() -> dict:
    cfg = retrieval_config()
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
                "file": "data/raw/85-btc.signed.pdf",
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
        pdf_proof = data["pdf_provenance"]["records"].get(row["id"])
        if pdf_proof:
            row["locator"] = {
                **row["locator"],
                **pdf_proof,
                "legacy_normalization_locator": row["locator"],
            }
            row["source"] = pdf_proof
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
    attach_bindings(rows, nodes, data.get("tt31_pdf_graph", {}).get("legal_evidence_bindings", []))
    assert all(e["source"] in node_ids and e["target"] in node_ids for e in edges)
    manifest = {
        "strategy": cfg["chunk_strategy"],
        "source_hashes": report["source_hashes"],
        "source_manifest_hash": digest(registered),
        "graph_version": "pdf-source-context-v5-evidence-bindings",
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
