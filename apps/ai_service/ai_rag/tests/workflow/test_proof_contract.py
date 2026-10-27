"""Regressions cross draft, evidence review and reduction, including recorded failures."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from rag.llm.generation.task_generation import generate_task_answer, review_jobs
from rag.llm.validation.task_validation import decode_task_answer
from tests.test_conditional_candidates import conditional_fixture
from tests.test_goal_workflow import context, model_answer, model_reviews, run


def recorded(case):
    return json.loads(
        (Path(__file__).parent / "fixtures" / "decision_contract" / f"{case}.json").read_text()
    )


def replay(value):
    pending = iter(value["responses"])
    calls = []

    def complete(messages, schema, **kwargs):
        calls.append(copy.deepcopy({"messages": messages, "schema": schema}))
        return next(pending)

    result = generate_task_answer(value["context"], SimpleNamespace(complete=complete))
    return result, calls


@pytest.mark.parametrize("case,codes", [("12.1", ["7113", "7117"]), ("13.1", ["7103", "7104"])])
def test_recorded_exclusion_failures_recover_without_rewriting_model_responses(case, codes):
    value = recorded(case)
    before = copy.deepcopy(value)
    result, _ = replay(value)
    assert value == before
    assert not result["diagnostics"]
    assert result["validation"]["task_completion"]
    assert [
        r["suggested_hs_code"] for r in result["answer"]["results"] if r["kind"] == "CLASSIFY"
    ] == codes


def test_id_only_fact_selection_recovers_recorded_analysis_without_inventing_quotes():
    value = recorded("03.1")
    response = json.loads(value["responses"][1]["content"])
    for review in response["analysis_reviews"]:
        for check in review["checks"]:
            check.pop("user_quotes")
    value["responses"][1]["content"] = json.dumps(response)
    result, calls = replay(value)
    assert len(calls) == 2 and not result["diagnostics"]
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert not result["answer"]["suggested_hs_code"]
    assert "review" not in calls[1]["schema"]["properties"]["reviews"]["items"]


def test_explicit_paraphrased_quotes_are_still_rejected():
    value = recorded("03.1")
    result, _ = replay(value)
    assert result["diagnostics"]
    assert not result["validation"]["task_completion"]


@pytest.mark.parametrize("case", ["12.1", "13.1"])
def test_recorded_decisions_do_not_depend_on_source_or_candidate_order(case):
    value = recorded(case)
    original, _ = replay(value)
    reordered = copy.deepcopy(value)
    for key in ("sources", "candidate_evidence", "comparison_candidates"):
        if key in reordered["context"]:
            reordered["context"][key].reverse()
    result, _ = replay(reordered)
    assert not result["diagnostics"]
    assert result["validation"]["task_completion"]

    def decisions(output):
        return {
            (r["objective_id"], r["item_id"]): (r["status"], r["suggested_hs_code"])
            for r in output["answer"]["results"]
        }

    assert decisions(result) == decisions(original)


def test_peer_exclusion_checks_are_not_conditions_for_the_selected_code():
    ctx = context()
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    for row in review["reviews"]:
        rejected = next(
            c for c in row["review"]["candidate_assessments"] if c["assessment"] == "RULED_OUT"
        )
        row["review"]["condition_checks"].append(
            {
                "evidence_id": rejected["evidence_ids"][0],
                "assessment": "CONTRADICTED",
                "fact_ids": rejected["fact_ids"],
                "user_quotes": rejected["user_quotes"],
            }
        )
    result, _ = run(ctx, [draft, review])
    assert result["validation"]["task_completion"]
    assert all(
        r["review"]["condition_checks"][-1]["proof_role"] == "EXCLUSION"
        for r in result["answer"]["results"]
    )


def test_model_cannot_relabel_mandatory_proof_as_a_peer_exclusion():
    ctx = context()
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    own = review["reviews"][0]["review"]["condition_checks"][0]
    own.update(assessment="CONTRADICTED", proof_role="EXCLUSION", target_codes=["7117"])
    result, _ = run(ctx, [draft, review, review])
    assert not result["validation"]["task_completion"]
    assert result["answer"]["results"][0]["suggested_hs_code"] == ""
    assert result["answer"]["results"][1]["suggested_hs_code"] == "7117"


def test_rejected_label_without_self_exclusion_cannot_unlock_a_competitor():
    ctx, draft, review = conditional_fixture()
    review["reviews"][1]["review"].update(status="REJECTED", clarifications=[])
    result, _ = run(ctx, [draft, review, review])
    assert not result["validation"]["task_completion"]
    assert not result["answer"]["suggested_hs_code"]
    assert result["diagnostics"]


def test_wire_shares_matrix_only_within_item_and_restores_legacy_decoder_contract():
    ctx, draft, review = conditional_fixture()
    matrix = {
        k: review["reviews"][0]["review"].pop(k) for k in ("candidate_assessments", "branch_checks")
    }
    for key in matrix:
        review["reviews"][1]["review"].pop(key)
    review["comparison_reviews"] = [{"comparison_id": "C1", **matrix}]

    def remove_quotes(node):
        if isinstance(node, dict):
            node.pop("user_quotes", None)
            for child in node.values():
                remove_quotes(child)
        elif isinstance(node, list):
            for child in node:
                remove_quotes(child)

    remove_quotes(review)
    result, calls = run(ctx, [draft, review])
    packet = json.loads(calls[1]["messages"][1]["content"])
    assert len(packet["comparison_contexts"]) == 1
    assert len(packet["jobs"]) == 2
    assert all("candidate_evidence" not in job for job in packet["jobs"])
    assert not result["diagnostics"]
    assert len(result["answer"]["hs_candidates"]) == 2


def test_repair_packet_excludes_locked_jobs_and_old_assistant_response():
    ctx = context(explain=True)
    draft = model_answer(ctx)
    bad = model_reviews(ctx, draft)
    bad["reviews"][0]["review"]["reason"] = ""
    fixed = model_reviews(ctx, draft)
    result, calls = run(ctx, [draft, bad, fixed])
    assert result["validation"]["task_completion"]
    packet = json.loads(calls[2]["messages"][1]["content"])
    assert [j["result_id"] for j in packet["jobs"]] == ["R1"]
    assert not packet["analysis_jobs"]
    assert not any(m["role"] == "assistant" for m in calls[2]["messages"])


def test_hs8_job_has_graph_prerequisites_without_explicit_parent_objective():
    ctx, draft, _ = conditional_fixture()
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    from rag.llm.generation.shortlist import expand_rows

    expanded, _ = expand_rows(rows, ctx)
    jobs, _ = review_jobs(expanded, ctx)
    assert all({p["level"] for p in j["prerequisites"]} == {4, 6} for j in jobs)
    assert all(all(p["evidence_ids"] for p in j["prerequisites"]) for j in jobs)


def test_unknown_ancestor_can_stop_before_unreviewed_leaf_conditions():
    ctx, draft, review = conditional_fixture()
    from rag.llm.evidence.evidence import bind_user_context

    ctx["question"] = ctx["question"].replace("Xe điện", "Xe")
    ctx["user_context"] = bind_user_context(ctx["question"])
    fact = next(s for s in ctx["user_context"]["statements"] if "Xe SUV 7 chỗ" in s["text"])
    source = next(s for s in ctx["sources"] if s.get("code") == "870380")
    parent_ids = {s["evidence_id"] for s in ctx["sources"] if len(s.get("code") or "") in {4, 6}}
    for row in review["reviews"]:
        value = row["review"]
        value["condition_checks"] = [
            c for c in value["condition_checks"] if c["evidence_id"] in parent_ids
        ]
        for check in value["condition_checks"]:
            check.update(fact_ids=[fact["id"]], user_quotes=["Xe SUV 7 chỗ"])
            if check["evidence_id"] == source["evidence_id"]:
                check.update(assessment="MISSING_PRODUCT_INFO", fact_ids=[], user_quotes=[])
        value["clarifications"] = [
            {
                "question": "Cần xác nhận đặc tính động lực đang xét?",
                "attribute": "động lực",
                "evidence_ids": [source["evidence_id"]],
            }
        ]
        value["candidate_assessments"] = []
        value["branch_checks"] = []
    result, _ = run(ctx, [draft, review])
    assert not result["diagnostics"]
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert not result["answer"]["suggested_hs_code"]
    assert not result["answer"]["hs_candidates"]


def test_missing_coverage_records_trigger_revision_without_certifying_the_old_draft():
    ctx = context(requirements=True)
    draft = model_answer(ctx)
    incomplete = model_reviews(ctx, draft)
    incomplete["analysis_reviews"][0]["coverage_checks"] = []
    revised = copy.deepcopy(draft)
    revised["results"][-1]["claims"][0]["text"] = "Các điều kiện cần được kiểm tra theo nguồn."
    confirmed = model_reviews(ctx, revised)
    confirmed["reviews"] = []
    result, calls = run(ctx, [draft, incomplete, incomplete, revised, confirmed])
    assert len(calls) == 5
    assert result["generation"]["draft_revision"]["attempted"]
    assert result["validation"]["task_completion"]
    assert not result["diagnostics"]
    assert result["generation"]["task_review"]["superseded_errors"]


def test_registered_condition_ids_cannot_reference_other_sources_or_invent_offsets():
    from rag.llm.evidence.conditions import bind_registered_conditions, condition_span_registry

    sources = [
        {"evidence_id": "E1", "text": "Điều kiện thứ nhất.\nĐiều kiện thứ hai."},
        {"evidence_id": "E2", "text": "Điều kiện khác."},
    ]
    registry = condition_span_registry(sources)
    span = next(s for s in registry.values() if s["quote"] == "Điều kiện thứ hai.")
    row = {"evidence_id": "E1", "condition_id": span["condition_id"]}
    bound, errors = bind_registered_conditions(row, registry)
    assert not errors and bound["criterion_quote"] == "Điều kiện thứ hai."
    assert bind_registered_conditions({**row, "evidence_id": "E2"}, registry)[1]
    assert bind_registered_conditions({**row, "condition_id": "P" + "0" * 20}, registry)[1]
    assert bind_registered_conditions({**row, "criterion_quote": "Nội dung bịa"}, registry)[1]
    plural = {
        "evidence_ids": ["E1"],
        "condition_ids": [s["condition_id"] for s in registry.values() if s["evidence_id"] == "E1"],
        "criterion_quotes": [{"evidence_id": "E1", "quote": "Nội dung bịa"}],
    }
    assert bind_registered_conditions(plural, registry)[1]


def test_new_wire_span_and_matrix_round_trip():
    from rag.llm.evidence.conditions import condition_span_registry

    ctx, draft, review = conditional_fixture()
    review = copy.deepcopy(review)
    registry = condition_span_registry(ctx["sources"])
    full = {
        s["evidence_id"]: max(
            (p for p in registry.values() if p["evidence_id"] == s["evidence_id"]),
            key=lambda p: p["end"] - p["start"],
        )["condition_id"]
        for s in ctx["sources"]
    }
    matrix = {
        k: review["reviews"][0]["review"].pop(k) for k in ("candidate_assessments", "branch_checks")
    }
    for key in matrix:
        review["reviews"][1]["review"].pop(key)
    review["comparison_reviews"] = [{"comparison_id": "C1", **matrix}]
    for row in review["reviews"]:
        for check in row["review"]["condition_checks"]:
            check["condition_id"] = full[check["evidence_id"]]
            check.pop("user_quotes")
        for question in row["review"]["clarifications"]:
            question["condition_ids"] = [full[eid] for eid in question["evidence_ids"]]
    for branch in matrix["branch_checks"]:
        branch["condition_ids"] = [full[eid] for eid in branch["evidence_ids"]]
    result, calls = run(ctx, [draft, review])
    assert not result["diagnostics"]
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    wire = calls[1]["schema"]["properties"]["reviews"]["properties"]["R1.C1"]["properties"][
        "review"
    ]
    assert "condition_id" in wire["properties"]["condition_checks"]["items"]["required"]
    assert "criterion_quote" not in wire["properties"]["condition_checks"]["items"]["properties"]


def test_draft_selects_registered_source_spans_without_rewriting_quotes():
    from rag.llm.evidence.conditions import condition_span_registry

    ctx, draft, review = conditional_fixture()
    spans = condition_span_registry(ctx["sources"])
    full = {s["evidence_id"]: s["condition_id"] for s in spans.values() if s["start"] == 0}
    for row in draft["results"]:
        for question in row["clarifications"]:
            question["condition_ids"] = [full[eid] for eid in question["evidence_ids"]]
    decoded, errors = decode_task_answer(draft, ctx)
    assert not errors and all(row["valid"] for row in decoded)
    for row in review["reviews"]:
        for check in [*row["review"]["branch_checks"], *row["review"]["clarifications"]]:
            check["condition_ids"] = [full[eid] for eid in check["evidence_ids"]]
    result, calls = run(ctx, [draft, review])
    assert not result["diagnostics"]
    wire = calls[0]["schema"]["properties"]["results"]["items"]["properties"]["clarifications"][
        "items"
    ]
    assert "condition_ids" in wire["required"]
    assert "criterion_quote" not in wire["properties"]
    packet = json.loads(calls[0]["messages"][1]["content"])
    assert all(source["condition_spans"] for source in packet["sources"])


def test_invalid_draft_span_does_not_unlock_or_discard_independent_result():
    ctx = context()
    draft = model_answer(ctx)
    draft["results"][0].update(
        status="MISSING_PRODUCT_INFO",
        code="",
        clarifications=[
            {
                "question": "Thuộc tính nào?",
                "attribute": "vật liệu",
                "evidence_ids": [ctx["sources"][0]["evidence_id"]],
                "condition_ids": ["P" + "0" * 20],
            }
        ],
    )
    decoded, errors = decode_task_answer(draft, ctx)
    assert errors and not decoded[0]["valid"] and decoded[1]["valid"]
    assert any("CONDITION_REF_INVALID" in error for error in errors)


def test_empty_draft_span_list_cannot_skip_source_grounding():
    ctx, draft, _ = conditional_fixture()
    for row in draft["results"]:
        for question in row["clarifications"]:
            question["condition_ids"] = []
    decoded, errors = decode_task_answer(draft, ctx)
    assert errors and not any(row["valid"] for row in decoded)
    assert any("CONDITION_REF_MISSING" in error for error in errors)


def test_mixed_request_statement_is_not_offered_as_product_fact():
    from rag.llm.evidence.evidence import bind_user_context
    from rag.llm.evidence.proof_contract import product_fact_ids

    facts = bind_user_context("Máy nặng 9 kg. Hãy xác định mã HS và căn cứ pháp lý.")
    allowed = product_fact_ids(facts)
    assert allowed
    assert all("mã HS" not in s["text"] for s in facts["statements"] if s["id"] in allowed)
    assert any("Máy nặng 9 kg" == s["text"] for s in facts["statements"] if s["id"] in allowed)
    assert any("mã HS" in s["text"] for s in facts["statements"])


def test_technical_fallback_keeps_reference_without_copying_source_into_answer():
    from rag.llm.generation.task_generation import _unreviewed_fallback

    ctx = context()
    rows, errors = decode_task_answer(model_answer(ctx), ctx)
    assert not errors
    fallback = _unreviewed_fallback(rows[0], ctx, "Chưa hoàn tất kiểm tra.")
    assert fallback["citations"] and "Nguồn tham khảo" in fallback["answer"]
    assert all(citation["quote"] not in fallback["answer"] for citation in fallback["citations"])
    assert not fallback["suggested_hs_code"] and not fallback["review_valid"]


def test_recorded_recovery_cannot_publish_unproven_mechanism_as_reference():
    result, _ = replay(recorded("03.1-recovery"))
    assert not result["diagnostics"]
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert "vẫn nằm trong phạm vi" not in result["answer"]["answer"]
    assert all(not row["suggested_hs_code"] for row in result["answer"]["results"])
    assert "phân nhóm 8703.60" not in result["answer"]["answer"]


def test_recovery_keeps_general_reference_when_it_does_not_claim_unproven_mechanism():
    value = recorded("03.1-recovery")
    draft = json.loads(value["responses"][0]["content"])
    reference = (
        "Nhóm 87.03 mô tả ô tô và các loại xe khác có động cơ được thiết kế chủ yếu để chở người."
    )
    draft["results"][0]["claims"][1]["text"] = reference
    value["responses"][0]["content"] = json.dumps(draft)
    result, _ = replay(value)
    assert not result["diagnostics"]
    assert reference in result["answer"]["answer"]
