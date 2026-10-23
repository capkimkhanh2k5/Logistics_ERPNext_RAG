"""Experiment integrity: real IDs, no gold-driven actions, protections and fallback."""

import pytest

from experiments.quyet_small.adaptive import stop_reason, template
from experiments.quyet_small.judge import evaluate, set_request
from experiments.quyet_small.local import passage_request
from experiments.quyet_small.protocol import (
    context_select,
    fuse,
    metrics,
    paired_ci,
    protected_ids,
)


def rows():
    return [
        {
            "id": key,
            "source_text": key,
            "level": 8,
            "code": str(i).zfill(8),
            "chunk_type": "tariff_entry",
        }
        for i, key in enumerate(("a", "b", "c", "d"))
    ]


def test_zero_weight_replays_original_order_exactly():
    source = list(reversed(rows()))
    assert fuse(source, {}, 2, 0) == source


def test_fusion_cannot_change_candidate_membership_or_unjudged_tail():
    source = rows()
    decisions = {"a": {"relevance": {"score": 0}}, "b": {"relevance": {"score": 3}}}
    result = fuse(source, decisions, 2, 0.5)
    assert {r["id"] for r in result} == {r["id"] for r in source}
    assert result[2:] == source[2:]


def test_missing_decision_falls_back_without_partial_reorder():
    source = rows()
    assert fuse(source, {"b": {"relevance": {"score": 3}}}, 2, 0.5) == source


def test_replacement_failure_restores_qwen_baseline():
    source = rows()
    case = {"task": "hs", "expected_hs_8": source[0]["code"], "target_groups": [{"any_of": ["a"]}]}
    record = {
        "case": case,
        "candidate_pool": source,
        "m3_ranked": source,
        "ranked_pool": list(reversed(source)),
    }
    ranked, _ = evaluate(record, {}, 2, 0.5, replacement=True)
    assert ranked == record["ranked_pool"]


def test_m3_only_control_does_not_require_a_quyet_decision():
    source = rows()
    record = {
        "case": {
            "task": "hs",
            "expected_hs_8": source[0]["code"],
            "target_groups": [{"any_of": ["a"]}],
        },
        "candidate_pool": source,
        "m3_ranked": source,
        "ranked_pool": list(reversed(source)),
    }
    ranked, _ = evaluate(record, {}, 2, 0, replacement=True)
    assert ranked == source


def test_context_over_budget_preserves_atomic_mandatory_sources():
    source = rows()
    result = context_select(source, {"a", "b"}, {r["id"]: 100 for r in source}, 50)
    assert result["ids"] == [r["id"] for r in source]
    assert result["protected_preservation"] == 1
    assert result["budget_met"] is False


def test_context_selector_rejects_missing_protected_citation():
    with pytest.raises(ValueError, match="Protected sources absent"):
        context_select(rows(), {"fake"}, {r["id"]: 100 for r in rows()}, 500)


def test_legal_notes_and_cited_context_are_protected():
    source = rows()
    source[0]["chunk_type"] = "chapter_note"
    assert protected_ids(source, source[:2]) == {"a", "c", "d"}


def test_hs_projection_does_not_count_a_note_as_a_tariff_target():
    source = rows()
    source[0]["chunk_type"] = "tariff_footnote"
    case = {
        "task": "hs",
        "expected_hs_8": source[0]["code"],
        "target_groups": [{"any_of": ["canonical-leaf"]}],
    }
    result = metrics(case, source, source)
    assert result["hs8_hit@10"] == 0
    assert result["target_recall@10"] == 0


def test_missing_product_facts_never_request_a_law_from_the_user():
    decision = {
        "status": "ok",
        "answers": {"missing": {"choice": "MISSING_PRODUCT_FACT"}, "sufficient": {"noul": 0.99}},
    }
    assert stop_reason(decision) == "NEEDS_PRODUCT_FACT_NO_USER_LAW_REQUEST"
    with pytest.raises(ValueError, match="not whitelisted"):
        template("query", "MISSING_PRODUCT_FACT", 1)


def test_missing_evidence_template_is_bounded_and_does_not_embed_gold():
    value = template("nhẫn vàng", "MISSING_CORPUS_EVIDENCE", 2)
    assert "nhẫn vàng" in value
    assert "GIR" in value
    assert "7113" not in value
    assert "cung cấp" not in value


def test_gold_and_untrusted_locator_fields_cannot_enter_model_state():
    row = {
        **rows()[0],
        "locator": {"gold": "secret"},
        "hierarchy_citations": [
            {
                "id": "parent",
                "text": "original legal wording",
                "locator": {"large_raw_metadata": "omitted"},
            }
        ],
    }
    request = passage_request("query", row, "snapshot")
    assert request["state"]["original_text"] == row["source_text"]
    assert request["state"]["source_hierarchy"] == [
        {"id": "parent", "original_text": "original legal wording"}
    ]
    case = {"query": "query", "expected_hs_8": "secret", "target_groups": ["secret"]}
    assert "secret" not in str(set_request(case, [row]))


def test_paired_ci_is_reproducible_and_preserves_deltas():
    result = paired_ci([0, 1, 0], [1, 1, 0])
    assert result == paired_ci([0, 1, 0], [1, 1, 0])
    assert result["delta"] == pytest.approx(1 / 3)
    assert result["improved"] == 1
    assert result["regressed"] == 0


def test_unlabelled_diagnostics_do_not_generate_fabricated_metrics():
    assert metrics({"task": "diagnostic", "target_groups": []}, rows(), rows()) == {
        "annotation_status": "DIAGNOSTIC_NO_RANKING_GOLD"
    }
