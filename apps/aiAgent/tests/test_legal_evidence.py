"""Printed consolidated rows may support logical levels, never fabricated citations."""

import copy
from unittest.mock import Mock

import numpy as np
import pytest

from config.settings import ROOT, GroqConfig
from rag.chunking.corpus import load_corpus
from rag.graph.context import GraphContext
from rag.graph.legal_evidence import attach_bindings, consolidated_bindings, evidence_digest
from rag.ingestion.pdf_graph import extractor_identity, validate_extraction
from rag.llm.context import prepare_context
from rag.llm.validation import validate_answer
from rag.utils.files import read
from rag.vectordb.postgres import ingest
from tests.test_generation_boundaries import recommendation


def fixture(code="99010000", *, continuation=False):
    locator = {
        "document": "new-source.pdf",
        "sha256": "a" * 64,
        "physical_page": 3,
        "bbox": [10, 20, 100, 30],
    }
    if continuation:
        locator["continuations"] = [{"physical_page": 4, "bbox": [10, 5, 100, 15]}]
    text = "Complete undivided heading, including its parts."
    row = {
        "code": code,
        "depth": None,
        "depth_vi": None,
        "depth_en": None,
        "text_vi": text,
        "text_en": text,
        "locator": locator,
    }
    records = [
        {
            "id": "heading",
            "code": code[:4],
            "level": 4,
            "source_text": "Navigation title",
            "locator": {"basis": "UNPRINTED_TAXONOMY_NODE_NOT_LEGAL_WORDING"},
        },
        {
            "id": "subheading",
            "code": code[:6],
            "level": 6,
            "source_text": "Navigation title",
            "locator": {"basis": "UNPRINTED_TAXONOMY_NODE_NOT_LEGAL_WORDING"},
        },
        {
            "id": "leaf",
            "code": code,
            "level": 8,
            "source_text": text,
            "locator": {**locator, "raw_pdf_text": text},
        },
    ]
    nodes = [
        {
            "id": r["id"],
            "metadata": {"code": r["code"], "level": r["level"], "virtual": r["level"] != 8},
        }
        for r in records
    ]
    edges = [
        {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
        {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
    ]
    extraction = {
        "sha256": locator["sha256"],
        "extractor": extractor_identity(),
        "rows_hash": evidence_digest([row]),
        "code_inventory": [{"code": code, "physical_page": 3}],
        "pages": [{"page": 3, "status": "EXTRACTED"}],
    }
    return [row], records, nodes, edges, extraction


def bound_graph(*, continuation=False):
    rows, records, nodes, edges, extraction = fixture(continuation=continuation)
    bindings = consolidated_bindings(rows, records, extraction)
    attach_bindings(records, nodes, bindings)
    return GraphContext(records, nodes, edges), records[-1]


@pytest.mark.parametrize("code", ["99010000", "99120000"])
def test_new_source_undivided_row_supports_all_levels_with_one_real_citation(code):
    rows, records, nodes, edges, extraction = fixture(code)
    validate_extraction(rows, extraction, "a" * 64)
    bindings = consolidated_bindings(rows, records, extraction)
    assert len(bindings) == 1
    attach_bindings(records, nodes, bindings)
    graph = GraphContext(records, nodes, edges)
    assert graph.citation("heading") is None
    assert graph.citation("subheading") is None
    ctx = prepare_context(
        "Complete product",
        {"hs_candidates": [records[-1]]},
        "hs",
        GroqConfig(keys=("fixture",)),
        graph,
    )
    evidence = ctx["candidate_evidence"][0]
    assert [s["id"] for s in ctx["sources"]] == ["leaf"]
    assert evidence["required_citation_labels"] == ["S1"]
    assert [n["label"] for n in evidence["hierarchy"]["chain"]] == ["S1", "S1", "S1"]
    assert evidence["hierarchy"]["structure_status"] == "VERIFIED"
    assert evidence["hierarchy"]["legal_evidence_status"] == "VERIFIED"
    assert validate_answer(recommendation(ctx, code), ctx)["valid"]


def test_zero_suffix_and_a_single_registered_leaf_do_not_establish_legal_evidence():
    _, records, nodes, edges, _ = fixture()
    path = GraphContext(records, nodes, edges).hs_hierarchy(records[-1])
    assert path["structure_status"] == "VERIFIED"
    assert path["legal_evidence_status"] == "INSUFFICIENT"
    assert path["status"] == "INVALID"


@pytest.mark.parametrize(
    "change", ["another_printed_child", "printed_parent", "indented_row", "branch"]
)
def test_a_partial_or_divided_source_scope_cannot_promote_leaf_wording(change):
    rows, records, _, _, extraction = fixture()
    if change == "another_printed_child":
        extraction["code_inventory"].append({"code": "99010100", "physical_page": 3})
    elif change == "printed_parent":
        extraction["code_inventory"].append({"code": "9901", "physical_page": 3})
    elif change == "indented_row":
        rows[0]["depth"] = 1
    else:
        rows.append({"code": None, "depth": 1, "text_vi": "- Specific source branch"})
    assert consolidated_bindings(rows, records, extraction) == []


def test_incomplete_or_changed_wording_is_rejected_even_when_code_anchor_matches():
    rows, records, _, _, extraction = fixture()
    rows[0]["text_vi"] = "Complete undivided heading"
    with pytest.raises(ValueError, match="Incomplete or different"):
        consolidated_bindings(rows, records, extraction)


@pytest.mark.parametrize("change", ["parser", "pdf", "rows", "unresolved", "inventory"])
def test_extraction_cache_checks_parser_source_content_and_complete_code_inventory(change):
    rows, _, _, _, extraction = fixture()
    if change == "parser":
        extraction["extractor"]["version"] = "old-parser"
    elif change == "pdf":
        extraction["sha256"] = "b" * 64
    elif change == "rows":
        rows[0]["text_vi"] = "Modified source text"
    elif change == "unresolved":
        extraction["pages"][0]["status"] = "UNRESOLVED_COLUMNS"
    else:
        extraction["code_inventory"].append({"code": "99010100", "physical_page": 3})
    with pytest.raises(ValueError):
        validate_extraction(rows, extraction, "a" * 64)


@pytest.mark.parametrize(
    "change", ["text", "locator", "version", "covered_node", "scope", "another_leaf"]
)
def test_stale_or_wrong_binding_blocks_recommendation(change):
    graph, leaf = bound_graph()
    if change == "text":
        leaf["source_text"] += " New qualifier."
    elif change == "locator":
        leaf["locator"]["sha256"] = "b" * 64
    elif change == "version":
        graph.nodes["heading"]["legal_evidence_binding"]["version"] = 0
    elif change == "covered_node":
        graph.nodes["heading"]["legal_evidence_binding"]["covered_node_ids"]["9901"] = "wrong"
    elif change == "scope":
        graph.nodes["heading"]["legal_evidence_binding"]["printed_codes"].append("99010100")
    else:
        graph.records["another_leaf"] = {"code": "99010100"}
        graph.children["heading"].add("another_leaf")
    ctx = prepare_context(
        "Product", {"hs_candidates": [leaf]}, "hs", GroqConfig(keys=("fixture",)), graph
    )
    assert ctx["candidate_evidence"][0]["hierarchy"]["status"] == "INVALID"
    assert not validate_answer(recommendation(ctx, leaf["code"]), ctx)["valid"]


def test_parent_child_topology_is_required_even_with_an_audited_shared_description():
    graph, leaf = bound_graph()
    graph.parents["subheading"].clear()
    path = graph.hs_hierarchy(leaf)
    assert path["structure_status"] == "INVALID"
    assert path["status"] == "INVALID"


def test_multi_page_locator_survives_generation_packing():
    graph, leaf = bound_graph(continuation=True)
    ctx = prepare_context(
        "Product", {"hs_candidates": [leaf]}, "hs", GroqConfig(keys=("fixture",)), graph
    )
    locator = ctx["sources"][0]["locator"]
    assert locator["physical_page"] == 3
    assert locator["physical_pages"] == [3, 4]
    assert locator["sha256"] == "a" * 64
    assert locator["continuations"] == [{"physical_page": 4, "bbox": [10, 5, 100, 15]}]


def test_binding_does_not_replace_required_branch_conditions():
    graph, leaf = bound_graph()
    graph.records["branch"] = {"id": "branch", "source_text": "Source condition " + "x" * 2000}
    graph.contexts["leaf"].add("branch")
    ctx = prepare_context(
        "Product",
        {"hs_candidates": [leaf]},
        "hs",
        GroqConfig(keys=("fixture",), max_context_chars=1000),
        graph,
    )
    assert "branch" in ctx["omitted_source_ids"]
    assert ctx["candidate_evidence"][0]["hierarchy"]["legal_evidence_status"] == "INSUFFICIENT"
    assert not validate_answer(recommendation(ctx, leaf["code"]), ctx)["valid"]


def test_binding_attachment_rejects_a_different_provenance_span():
    rows, records, nodes, _, extraction = fixture(continuation=True)
    bindings = consolidated_bindings(rows, records, extraction)
    records[-1]["locator"] = copy.deepcopy(records[-1]["locator"])
    records[-1]["locator"].pop("continuations")
    with pytest.raises(ValueError, match="locator drifted"):
        attach_bindings(records, nodes, bindings)


def test_duplicate_printed_code_anchor_cannot_prove_an_undivided_source():
    rows, records, _, _, extraction = fixture()
    extraction["code_inventory"].append({"code": "99010000", "physical_page": 4})
    assert consolidated_bindings(rows, records, extraction) == []


def test_snapshot_rejects_modified_evidence_metadata_before_database_writes():
    _, records, nodes, edges, _ = fixture()
    for record in records:
        record["input_hash"] = evidence_digest(record["source_text"])
    declaration = {
        "records_hash": evidence_digest(records),
        "edges_hash": evidence_digest(edges),
        "nodes_hash": evidence_digest(nodes),
    }
    bundle = {
        "snapshot": evidence_digest(declaration)[:24],
        "manifest": declaration,
        "records": records,
        "nodes": nodes,
        "edges": edges,
    }
    profile = {"sparse": False}
    manifest = {
        "snapshot": bundle["snapshot"],
        "ids": [r["id"] for r in records],
        "input_hashes": [r["input_hash"] for r in records],
        "profile": profile,
        "profile_id": evidence_digest(profile)[:24],
    }
    nodes[0]["metadata"]["legal_evidence_binding"] = {"status": "VERIFIED"}
    connection = Mock()
    with pytest.raises(AssertionError, match="Graph nodes hash mismatch"):
        ingest(connection, bundle, manifest, np.ones((3, 1024)))
    connection.execute.assert_not_called()


def test_registered_corpus_verifies_all_hs_paths_and_ten_complete_source_bindings():
    bundle = load_corpus()
    graph = GraphContext(bundle["records"], bundle["nodes"], bundle["edges"])
    leaves = [r for r in bundle["records"] if r.get("level") == 8]
    assert len(leaves) == 3480
    assert all(graph.hs_hierarchy(r)["status"] == "VERIFIED" for r in leaves)
    bindings = read(ROOT / "data/normalized/TT31/PDF_SOURCE_GRAPH.json")["legal_evidence_bindings"]
    assert len(bindings) == 10
    for binding in bindings:
        source = graph.records[binding["source_id"]]
        path = graph.hs_hierarchy(source)
        assert all(n["legal_evidence_ids"] == [source["id"]] for n in path["chain"])
        assert graph.citation(path["chain"][0]["id"]) is None
        assert graph.citation(path["chain"][1]["id"]) is None
        assert graph.citation(source["id"])
        assert source["locator"]["wording_status"] == "NORMALIZED_COMPLETE_MATCH"
        ctx = prepare_context(
            source["source_text"],
            {"hs_candidates": [source]},
            "hs",
            GroqConfig(keys=("fixture",)),
            graph,
        )
        assert validate_answer(recommendation(ctx, source["code"]), ctx)["valid"]
        if source["code"] == "84490000":
            assert ctx["sources"][0]["locator"]["physical_pages"] == [75, 76]
