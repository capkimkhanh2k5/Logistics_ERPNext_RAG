"""LLM metadata compaction must preserve full runtime evidence and legal guards."""

import json

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.context import prepare_context
from rag.llm.validation import validate_answer


def fixture(*, broken=False, candidates=3):
    locator = {
        "document": "Source.pdf",
        "physical_page": 12,
        "physical_pages": [12, 13],
        "sha256": "a" * 64,
        "bbox": [10.0, 20.0, 30.0, 40.0],
        "audit": {"reviewed_source": "full provenance"},
    }

    def row(code, text):
        return {
            "id": "source-bound-identifier-" + "x" * 50 + code,
            "code": code,
            "level": len(code),
            "chunk_type": "tariff_entry",
            "source_text": text,
            "locator": locator.copy(),
        }

    heading = row("1111", "Heading conditions")
    parent = row("111111", "Subheading conditions")
    leaves = [row(f"111111{i:02}", f"Distinct candidate wording {i}") for i in range(candidates)]
    edges = [
        {"source": parent["id"], "target": leaf["id"], "relation": "CONTAINS"} for leaf in leaves
    ]
    if not broken:
        edges.append({"source": heading["id"], "target": parent["id"], "relation": "CONTAINS"})
    graph = GraphContext([heading, parent, *leaves], [], edges)
    result = {"hs_candidates": leaves, "matches": leaves, "package": []}
    return graph, result, locator


def test_model_projection_keeps_code_label_chain_and_full_server_provenance():
    graph, result, locator = fixture()
    ctx = prepare_context("Product facts", result, "hs", GroqConfig(keys=("fixture",)), graph)
    payload = json.loads(ctx["messages"][1]["content"])

    assert ctx["allowed_hs_codes"] == [row["code"] for row in result["hs_candidates"]]
    assert ctx["retrieved_hs_codes"] == ctx["allowed_hs_codes"]
    assert [row["code"] for row in result["hs_candidates"]] == ["11111100", "11111101", "11111102"]
    for full, compact in zip(ctx["candidate_evidence"], payload["candidate_evidence"], strict=True):
        assert compact["code"] == full["code"]
        assert compact["required_citation_labels"] == full["required_citation_labels"]
        assert compact["hierarchy"]["status"] == full["hierarchy"]["status"] == "VERIFIED"
        for node, projected in zip(
            full["hierarchy"]["chain"], compact["hierarchy"]["chain"], strict=True
        ):
            assert node["id"] and node["legal_evidence_ids"]
            assert projected["code"] == node["code"]
            assert projected["evidence_labels"] == node["evidence_labels"]
            assert "id" not in projected and "legal_evidence_ids" not in projected

    for full, compact in zip(ctx["sources"], payload["sources"], strict=True):
        assert compact["id"] == full["id"]
        assert compact["text"] == full["text"]
        assert full["locator"]["sha256"] == locator["sha256"]
        assert full["locator"]["bbox"] == locator["bbox"]
        assert compact["locator"] == {
            "document": "Source.pdf",
            "physical_page": 12,
            "physical_pages": [12, 13],
        }
        assert ctx["source_locators"][full["label"]] == locator


def test_metadata_compaction_preserves_candidate_variety_under_actual_message_budget():
    graph, result, _ = fixture()
    cfg = GroqConfig(keys=("fixture",), max_input_chars=3800, max_context_chars=2200)
    ctx = prepare_context("Product facts", result, "hs", cfg, graph)
    payload = json.loads(ctx["messages"][1]["content"])

    assert ctx["allowed_hs_codes"] == [row["code"] for row in result["hs_candidates"]]
    assert not ctx["packing"]["omitted_candidate_codes"]
    assert all(e["hierarchy"]["status"] == "VERIFIED" for e in ctx["candidate_evidence"])
    assert ctx["packing"]["input_chars"] == len(ctx["messages"][1]["content"]) <= 3800
    assert (
        ctx["packing"]["source_chars"]
        == len(json.dumps(payload["sources"], ensure_ascii=False, separators=(",", ":")))
        <= 2200
    )
    assert [s["text"] for s in ctx["sources"]] == [s["text"] for s in payload["sources"]]


def test_compact_invalid_hierarchy_retains_failure_reason_and_blocks_recommendation():
    graph, result, _ = fixture(broken=True, candidates=1)
    ctx = prepare_context("Product facts", result, "hs", GroqConfig(keys=("fixture",)), graph)
    payload = json.loads(ctx["messages"][1]["content"])
    hierarchy = ctx["candidate_evidence"][0]["hierarchy"]
    assert (
        hierarchy["status"] == payload["candidate_evidence"][0]["hierarchy"]["status"] == "INVALID"
    )
    assert hierarchy["errors"] == payload["candidate_evidence"][0]["hierarchy"]["errors"]
    assert hierarchy["errors"]
    citations = [{"label": s["label"], "quote": s["text"]} for s in ctx["sources"]]
    answer = {
        "status": "RECOMMENDATION",
        "answer": "Suggested 11111100 " + " ".join(f"[{s['label']}]" for s in ctx["sources"]),
        "suggested_hs_code": "11111100",
        "alternatives": [],
        "citations": citations,
        "missing_information": [],
        "missing_legal_evidence": [],
    }
    assert not validate_answer(answer, ctx)["valid"]
