"""Condition references bind provenance without guessing legal predicate semantics."""

import json
from copy import deepcopy

import pytest

from rag.llm.evidence.conditions import (
    bind_condition_refs,
    condition_ref_errors,
    defer_descendant_comparison,
    review_conditions,
)
from rag.llm.review.disambiguation import disambiguation_errors, review_scope
from rag.prompts.core.repair import format_task_repair_prompt
from tests.test_candidate_disambiguation import comparison_review, vehicle_context


def bound_context():
    ctx = vehicle_context()
    ctx["review_conditions"] = review_conditions(ctx, review_scope(ctx), "87038098")
    return ctx


def test_condition_ids_survive_source_reordering_and_display_relabeling():
    ctx = bound_context()
    other = deepcopy(ctx)
    other["sources"].reverse()
    for source in other["sources"]:
        source["label"] += "-display"
    for row in [*other["candidate_evidence"], *other["comparison_candidates"]]:
        row["required_citation_labels"] = [s + "-display" for s in row["required_citation_labels"]]
    rebuilt = review_conditions(other, review_scope(other), "87038098")
    assert {c["condition_id"] for c in rebuilt} == {
        c["condition_id"] for c in ctx["review_conditions"]
    }


def test_independent_attributes_under_one_parent_have_separate_questions():
    ctx = bound_context()
    raw = comparison_review(ctx)
    original = raw["branch_checks"][0]
    eids = original["evidence_ids"]
    raw["branch_checks"] = [
        {**original, "attribute": f"dimension-{n}", "evidence_ids": [eid]}
        for n, eid in enumerate(eids)
    ]
    raw["clarifications"] = [
        {
            "question": f"Thuộc tính {n} là gì?",
            "attribute": b["attribute"],
            "evidence_ids": b["evidence_ids"],
        }
        for n, b in enumerate(raw["branch_checks"])
    ]
    bound = bind_condition_refs(raw, ctx)
    assert not disambiguation_errors(bound, ctx, "87038098")
    assert len({tuple(b["condition_ids"]) for b in bound["branch_checks"]}) == len(eids)


@pytest.mark.parametrize("fault", ["unknown_id", "wrong_source", "wrong_question"])
def test_fabricated_or_unrelated_condition_links_are_rejected(fault):
    ctx = bound_context()
    raw = bind_condition_refs(comparison_review(ctx), ctx)
    branch = raw["branch_checks"][0]
    if fault == "unknown_id":
        branch["condition_ids"] = ["D-invented"]
    elif fault == "wrong_source":
        wrong = next(
            c
            for c in ctx["review_conditions"]
            if not set(c["evidence_ids"]) & set(branch["evidence_ids"])
        )
        branch["condition_ids"] = [wrong["condition_id"]]
    else:
        raw["clarifications"][0]["evidence_ids"] = [ctx["sources"][0]["evidence_id"]]
        raw["clarifications"][0]["condition_ids"] = []
    assert disambiguation_errors(raw, ctx, "87038098")


def test_unknown_child_dimension_can_wait_for_a_source_bound_parent_question():
    ctx = bound_context()
    raw = comparison_review(ctx)
    parent = next(
        c
        for c in ctx["review_conditions"]
        if c["role"] == "PREREQUISITE" and "87038098" in c["codes"]
    )
    eid = parent["evidence_ids"][0]
    for check in raw["condition_checks"]:
        if check["evidence_id"] == eid:
            check.update(assessment="MISSING_PRODUCT_INFO", fact_ids=[], user_quotes=[])
    raw["clarifications"] = [
        {
            "question": "Đặc tính cấp cha thực tế là gì?",
            "attribute": "parent-condition",
            "evidence_ids": [eid],
        }
    ]
    raw["branch_checks"][0]["assessment"] = "DEFERRED"
    bound = bind_condition_refs(raw, ctx)
    assert not disambiguation_errors(bound, ctx, "87038098")
    bound["clarifications"] = []
    assert any(
        "DEFERRED_WITHOUT_PREREQUISITE" in e for e in disambiguation_errors(bound, ctx, "87038098")
    )
    bound["status"] = "SUPPORTED"
    assert disambiguation_errors(bound, ctx, "87038098")


def test_legacy_binding_never_replaces_explicit_invalid_references():
    ctx = bound_context()
    raw = comparison_review(ctx)
    raw["clarifications"][0]["condition_ids"] = ["D-foreign"]
    bound = bind_condition_refs(raw, ctx)
    assert bound["clarifications"][0]["condition_ids"] == ["D-foreign"]
    assert condition_ref_errors(bound["clarifications"][0], ctx)


def test_excluding_a_specialised_candidate_does_not_require_proving_unrelated_assembly_form():
    ctx = vehicle_context("Xe điện chở người, không phải xe cứu thương.")
    raw = comparison_review(ctx)
    leaf = next(s for s in ctx["sources"] if s.get("code") == "87038018")
    leaf["text"] = "Xe cứu thương."
    form = next(s for s in ctx["sources"] if "CKD" in s["text"])
    row = next(r for r in raw["candidate_assessments"] if r["code"] == "87038018")
    statement = max(ctx["user_context"]["statements"], key=lambda s: len(s["text"]))
    row.update(
        assessment="RULED_OUT",
        evidence_ids=[leaf["evidence_id"], form["evidence_id"]],
        decisive_evidence_ids=[leaf["evidence_id"]],
        fact_ids=[statement["id"]],
        user_quotes=[statement["text"]],
    )
    assert not disambiguation_errors(raw, ctx, "87038098")
    # Removing the decisive proof preserves the strict legacy full-source check.
    row.pop("decisive_evidence_ids")
    assert any("PRESENTATION_UNPROVEN" in e for e in disambiguation_errors(raw, ctx, "87038098"))


@pytest.mark.parametrize("refs", [[], ["E-foreign"]])
def test_exclusion_cannot_hide_its_proof_with_empty_or_foreign_decisive_ids(refs):
    ctx = vehicle_context("Xe điện nhập khẩu nguyên chiếc, không phải CKD.")
    raw = comparison_review(ctx, missing=False)
    row = next(r for r in raw["candidate_assessments"] if r["assessment"] == "RULED_OUT")
    row["decisive_evidence_ids"] = refs
    assert any("EXCLUSION_PROOF_INVALID" in e for e in disambiguation_errors(raw, ctx, "87038098"))


def test_repair_instructions_respect_phase_permissions_and_locate_nested_errors():
    error = "R1.branch_checks/0: [CONDITION_SOURCE_MISMATCH] Sai liên kết."
    review = json.loads(format_task_repair_prompt([error], phase="product_review"))
    answer = json.loads(format_task_repair_prompt([], phase="answer"))
    decision = json.loads(format_task_repair_prompt([], phase="decision_review"))
    assert review["repair_errors"] == [
        {
            "code": "CONDITION_SOURCE_MISMATCH",
            "path": "R1.branch_checks/0",
            "message": "Sai liên kết.",
        }
    ]
    assert "không sửa proposed_answer" in review["repair_instruction"]
    assert "được sửa claims" in answer["repair_instruction"]
    assert "selected_code" not in decision["repair_instruction"]


def pending_parent_review():
    ctx = bound_context()
    ctx["classification_level"] = 8
    raw = comparison_review(ctx)
    source = next(s for s in ctx["sources"] if s.get("code") == "870380")
    eid = source["evidence_id"]
    for check in raw["condition_checks"]:
        if check["evidence_id"] == eid:
            check.update(assessment="MISSING_PRODUCT_INFO", fact_ids=[], user_quotes=[])
    raw["clarifications"].append(
        {"question": "Xe dùng loại động lực nào?", "attribute": "propulsion", "evidence_ids": [eid]}
    )
    return ctx, raw, eid


def test_ancestor_gate_preserves_question_and_discards_unreviewed_descendant_exclusions():
    ctx, raw, eid = pending_parent_review()
    # A fabricated child exclusion is discarded, never accepted as a legal proof.
    raw["candidate_assessments"][0].update(assessment="RULED_OUT", evidence_ids=["E-fabricated"])
    gated, pending = defer_descendant_comparison(raw, ctx, "87038098")
    assert pending == [eid]
    assert gated["clarifications"] == [raw["clarifications"][-1]]
    assert all(r["assessment"] == "POSSIBLE" for r in gated["candidate_assessments"])
    assert all(b["assessment"] == "DEFERRED" for b in gated["branch_checks"])
    assert gated["status"] == "MISSING_PRODUCT_INFO"
    assert not disambiguation_errors(bind_condition_refs(gated, ctx), ctx, "87038098")
    assert raw["candidate_assessments"][0]["evidence_ids"] == ["E-fabricated"]


@pytest.mark.parametrize(
    "fault", ["supported", "no_question", "known_parent", "missing_peer", "leaf_only"]
)
def test_ancestor_gate_cannot_release_a_code_or_replace_missing_coverage(fault):
    ctx, raw, _ = pending_parent_review()
    if fault == "supported":
        raw["status"] = "SUPPORTED"
    elif fault == "no_question":
        raw["clarifications"] = []
    elif fault == "known_parent":
        for c in raw["condition_checks"]:
            c["assessment"] = "SATISFIED"
    elif fault == "missing_peer":
        ctx["candidate_comparison"][0]["missing_codes"] = ["87038018"]
    else:
        leaf = next(s for s in ctx["sources"] if s.get("code") == "87038098")
        raw["condition_checks"] = [
            {
                "evidence_id": leaf["evidence_id"],
                "assessment": "MISSING_PRODUCT_INFO",
                "fact_ids": [],
                "user_quotes": [],
            }
        ]
        raw["clarifications"] = [
            {
                "question": "Thuộc tính nhánh cuối?",
                "attribute": "leaf",
                "evidence_ids": [leaf["evidence_id"]],
            }
        ]
    gated, pending = defer_descendant_comparison(raw, ctx, "87038098")
    assert gated is raw and not pending
