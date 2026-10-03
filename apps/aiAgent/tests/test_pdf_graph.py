"""Source hierarchy and dispatch contracts; no expected-code rules in retrieval."""

import pytest

from rag.context import GraphContext, context_text, fit_rerank_context
from rag.data import ROOT, load_corpus, read
from rag.retrieval import Retriever
from scripts.audit_pdf_sources import locate
from scripts.build_pdf_graph import materialize


def test_pdf_scope_continues_across_sibling_subheadings_and_closes_at_same_depth():
    codes = ["9901", "990110", "99011001", "990120", "99012001", "99013001"]
    records = [
        {"id": "source:" + c, "code": c, "level": len(c), "role": "candidate", "heading": c[:4]}
        for c in codes
    ]
    rows = []
    for i, (code, depth, text) in enumerate(
        [
            ("9901", 0, "Heading from a newly registered Chapter"),
            (None, 1, "- Source branch A"),
            ("990110", 2, "-- First subheading"),
            ("99011001", 3, "--- First leaf"),
            ("990120", 2, "-- Second subheading"),
            ("99012001", 3, "--- Second leaf"),
            (None, 1, "- Source branch B"),
            ("99013001", 2, "-- Third leaf"),
        ]
    ):
        rows.append(
            {
                "code": code,
                "depth": depth,
                "depth_en": depth,
                "text_vi": text,
                "text_en": text,
                "locator": {"document": "new.pdf", "physical_page": 1, "bbox": [0, i, 10, i + 1]},
            }
        )
    nodes, edges, report = materialize(rows, records, "NEW")
    by_text = {n["metadata"]["source_text"]: n["id"] for n in nodes}
    assert {e["target"] for e in edges if e["source"] == by_text["Source branch A"]} == {
        "source:99011001",
        "source:99012001",
    }
    assert {e["target"] for e in edges if e["source"] == by_text["Source branch B"]} == {
        "source:99013001"
    }
    assert report["missing_hs8"] == []


def test_pdf_rebuild_rejects_missing_registered_leaf():
    with pytest.raises(ValueError, match="Unverified PDF source leaves"):
        materialize(
            [],
            [{"id": "source:99010001", "code": "99010001", "level": 8, "role": "candidate"}],
            "NEW",
        )


def test_pdf_rebuild_rejects_unregistered_printed_parent_in_registered_chapter():
    row = {"code": "9901", "depth": 0}
    with pytest.raises(ValueError, match="Printed source parent/leaf is missing"):
        materialize(
            [row],
            [{"id": "source:99010001", "code": "99010001", "level": 8, "role": "candidate"}],
            "NEW",
        )


def test_pdf_wording_audit_handles_short_source_labels():
    result = locate("Live animals.", ["Page header. Live animals. Other text."])
    assert result["word_trigram_coverage"] == 1.0
    assert result["physical_pages"] == [1]


def test_all_materialized_scopes_have_pdf_locators_and_known_targets():
    bundle = load_corpus()
    ids = {n["id"] for n in bundle["nodes"]}
    graph = read(ROOT / "data/normalized/TT31/PDF_SOURCE_GRAPH.json")
    assert len(graph["edges"]) == 4346
    assert all(e["source"] in ids and e["target"] in ids for e in bundle["edges"])
    assert all(
        e["metadata"]["context_locator"]["sha256"] == e["metadata"]["target_locator"]["sha256"]
        for e in graph["edges"]
    )
    assert not any(e["relation"] == "CONTEXT_WITHIN" for e in bundle["edges"])
    g = GraphContext(bundle["records"], bundle["nodes"], bundle["edges"])
    views = {r["code"]: r for r in g.candidate_views().values()}
    assert not any(
        c["locator"].get("basis") == "UNPRINTED_TAXONOMY_NODE_NOT_LEGAL_WORDING"
        for r in views.values()
        for c in r["hierarchy_citations"]
    )
    assert "Ngọc trai nuôi cấy:" in views["71012200"]["intermediate_branches"]
    assert "Đã gia công cách khác:" in views["71039900"]["intermediate_branches"]
    assert any("Dạng CKD" in x for x in views["87024021"]["intermediate_branches"])
    assert not any("Dạng CKD" in x for x in views["87031010"]["intermediate_branches"])
    assert not any("CBU" in x for x in views["87024061"]["intermediate_branches"])
    assert "không quá 2.500 cc" in views["87032323"]["leaf_text"]
    assert views["85399090"]["leaf_text"] == "Loại khác"
    assert all(c["locator"].get("sha256") for r in views.values() for c in r["hierarchy_citations"])


def test_reviewed_pdf_source_repairs_match_ingested_text_and_citations():
    repairs = read(ROOT / "data/normalized/TT31/PDF_SOURCE_TEXT_CORRECTIONS.json")["records"]
    records = {r["id"]: r for r in load_corpus()["records"]}
    assert len(repairs) == 20
    for repair in repairs:
        row = records[repair["id"]]
        assert row["source_text"] == repair["corrected_source_text"]
        assert repair["corrected_source_text"] in row["embedding_text"]
        assert row["locator"]["sha256"] == repair["locator"]["sha256"]


def test_context_deduplicates_text_while_preserving_distinct_source_citations():
    row = {"embedding_text": "Leaf", "leaf_text": "Leaf"}
    citations = [
        {"id": "section", "kind": "source", "text": "Same source title"},
        {"id": "chapter", "kind": "source", "text": "Same source title"},
    ]
    assert context_text(row, citations, [], "plain") == "Leaf\nSame source title"
    row.update(
        rerank_text="Leaf\nPhân cấp nguồn: Same source title\nNhánh nguồn: Last source condition",
        hierarchy_citations=[
            *citations,
            {"id": "condition", "text": "Last source condition", "kind": "context"},
        ],
        note_citations=[],
        context_format="structured",
    )

    class Tokenizer:
        def __call__(self, pairs, truncation=False):
            assert not truncation
            return {"input_ids": [list(range(len(q.split()) + len(t.split()))) for q, t in pairs]}

    result = fit_rerank_context("query", [row], Tokenizer(), max_tokens=10)[0]
    assert "Phân cấp nguồn:" in result["rerank_text"]
    assert result["rerank_text"].count("Same source title") == 1
    assert result["rerank_omitted_ids"] == ["condition"]


def test_dispatch_uses_hs_policy_and_supports_explicit_ambiguous_qa(monkeypatch):
    retriever = object.__new__(Retriever)
    retriever.qa_policy = {"configuration": "C10"}
    retriever.weights = {"dense": 999}
    calls = []
    monkeypatch.setattr(
        retriever, "adaptive_search", lambda query, **kwargs: calls.append(kwargs) or {"task": "HS"}
    )
    monkeypatch.setattr(retriever, "qa_search", lambda query: {"task": "QA"})
    assert retriever.legacy_routed_search("Generic product description")["task"] == "HS"
    assert calls == [{}]
    assert (
        retriever.legacy_routed_search("Hệ thống HS gồm những thành phần nào?", intent="qa")["task"]
        == "QA"
    )
    assert (
        retriever.legacy_routed_search("Theo chú giải, sản phẩm này là gì?", intent="product")[
            "task"
        ]
        == "HS"
    )
    with pytest.raises(ValueError, match="Intent must"):
        retriever.legacy_routed_search("query", intent="unknown")
