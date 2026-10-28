"""Adversarial outputs exercise review coverage and recovery invalidation."""

import copy
import json

import pytest

from rag.llm.generation.recovery import _retain_completed
from rag.llm.generation.task_generation import blocked
from rag.llm.review.analysis_review import analysis_jobs
from rag.llm.validation.task_validation import decode_task_answer
from tests.test_goal_workflow import context, model_answer, model_reviews, run


def fact_draft():
    ctx = context(explain=True)
    draft = model_answer(ctx)
    fid = next(
        s["id"] for s in ctx["user_context"]["statements"] if "Dây A bằng bạc 925" in s["text"]
    )
    draft["results"][-1]["claims"].append(
        {
            "kind": "PRODUCT_FACT",
            "text": "Dây A nặng 500 kg và chứa uranium.",
            "evidence_ids": [],
            "fact_ids": [fid],
        }
    )
    return ctx, draft


def test_product_facts_are_not_outside_analysis_review():
    ctx, draft = fact_draft()
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    job = next(j for j in analysis_jobs(rows, ctx) if j["result_id"] == "R3")
    assert {c["claim_index"] for c in job["claims"]} == {0, 1}


def test_reference_assessment_cannot_certify_fabricated_product_fact():
    ctx, draft = fact_draft()
    review = model_reviews(ctx, draft)
    out, _ = run(ctx, [draft, review, review])
    assert "500 kg" not in out["answer"]["answer"]
    assert not out["validation"]["task_completion"]


def completed():
    ctx = context(explain=True)
    draft = model_answer(ctx)
    old, _ = run(ctx, [draft, model_reviews(ctx, draft)])
    return ctx, old


def test_recovery_cannot_restore_a_semantically_downgraded_result():
    ctx, old = completed()
    new = copy.deepcopy(old)
    new["answer"]["results"][0].update(
        status="INSUFFICIENT_LEGAL_EVIDENCE",
        suggested_hs_code="",
        review_valid=False,
        hs_candidates=[],
        missing_legal_evidence=["Nguồn bổ sung chưa chứng minh cách áp dụng."],
    )
    final = _retain_completed(ctx, old, ctx, new)
    row = final["answer"]["results"][0]
    assert row["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert not row["suggested_hs_code"]
    assert not row.get("retained_after_recovery")


def test_recovery_new_evidence_invalidates_technical_restoration():
    ctx, old = completed()
    new = copy.deepcopy(old)
    new["answer"]["results"][0] = blocked(new["answer"]["results"][0], "Review chưa hoàn tất.")
    updated = copy.deepcopy(ctx)
    source = {
        **updated["sources"][0],
        "id": "new",
        "label": "S99",
        "evidence_id": "E" + "f" * 20,
        "text": "Ngoại lệ cần kiểm tra.",
    }
    updated["sources"].append(source)
    final = _retain_completed(ctx, old, updated, new)
    assert not final["answer"]["results"][0]["suggested_hs_code"]


def test_unchanged_context_can_restore_explicit_technical_failure():
    ctx, old = completed()
    new = copy.deepcopy(old)
    new["answer"]["results"][0] = blocked(new["answer"]["results"][0], "Review chưa hoàn tất.")
    final = _retain_completed(ctx, old, ctx, new)
    assert final["answer"]["results"][0].get("retained_after_recovery")


def test_verified_product_fact_is_rendered_from_user_span_not_model_paraphrase():
    ctx, draft = fact_draft()
    review = model_reviews(ctx, draft)
    check = review["analysis_reviews"][0]["checks"][-1]
    claim = draft["results"][-1]["claims"][-1]
    check.update(
        assessment="FACT_SUPPORTED", fact_ids=claim["fact_ids"], user_quotes=["Dây A bằng bạc 925"]
    )
    out, _ = run(ctx, [draft, review])
    assert "500 kg" not in out["answer"]["answer"]
    assert "Dây A bằng bạc 925" in out["answer"]["answer"]
    assert out["validation"]["review_coverage"][-1]["claim_indices"] == [0, 1]


def test_batch_reviewer_receives_effective_dates_and_locator():
    ctx = context(explain=True)
    source = ctx["sources"][0]
    source.update(
        effective_from="2020-01-01",
        effective_to="2025-01-01",
        locator={"document": "legal.pdf", "physical_page": 7},
    )
    draft = model_answer(ctx)
    _, calls = run(ctx, [draft, model_reviews(ctx, draft)])
    sent = json.loads(calls[1]["messages"][1]["content"])
    actual = next(s for s in sent["sources"] if s["evidence_id"] == source["evidence_id"])
    assert actual["effective_to"] == "2025-01-01"
    assert actual["locator"]["physical_page"] == 7


def test_omitted_coverage_is_revised_in_draft_and_reviewed_within_shared_budget():
    ctx = context(requirements=True)
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    review["analysis_reviews"][0]["coverage_checks"][0].update(
        assessment="OMITTED", claim_indices=[]
    )
    revised = copy.deepcopy(draft)
    revised["results"][-1]["claims"][0]["text"] = (
        "Các chiều điều kiện được liệt kê theo nguồn, gồm mô tả các nhánh."
    )
    # An attempted regression in a completed item must be replaced by its locked draft.
    revised["results"][0]["code"] = "0000"
    confirmed = model_reviews(ctx, draft)
    confirmed["reviews"] = []
    out, calls = run(ctx, [draft, review, revised, confirmed])
    assert len(calls) == 4
    assert out["generation"]["remaining_calls"] == 1
    assert out["validation"]["task_completion"]
    assert out["answer"]["results"][0]["suggested_hs_code"] == "7113"
    assert out["generation"]["draft_revision"]["attempted"]
    assert "Các chiều điều kiện" in out["answer"]["answer"]


def test_explicit_classification_request_is_not_lost_inside_explanation():
    from rag.retrieval.request_plan import validate_request

    query = "Dây A và Dây B có thuộc cùng nhóm HS 7113 không? Hãy phân tích và đề xuất hướng phân loại chính xác."
    plan = {
        "items": [{"id": "I1", "anchor": "Dây A"}, {"id": "I2", "anchor": "Dây B"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "COMPARE",
                "level": 4,
                "item_ids": ["I1", "I2"],
                "anchor": "có thuộc cùng nhóm HS 7113 không?",
                "required": True,
            },
            {
                "id": "G2",
                "kind": "EXPLAIN",
                "level": 0,
                "item_ids": ["I1", "I2"],
                "anchor": "Hãy phân tích và đề xuất hướng phân loại chính xác.",
                "required": True,
            },
        ],
    }
    result = validate_request(query, plan)
    goal = next(g for g in result["objectives"] if g["kind"] == "CLASSIFY")
    assert goal["level"] == 4 and goal["item_ids"] == ["I1", "I2"]
    assert validate_request(query, result) == result
    plan["objectives"][-1]["anchor"] = "Hãy phân tích"
    assert not any(g["kind"] == "CLASSIFY" for g in validate_request(query, plan)["objectives"])


def test_condition_matching_uses_unique_predicate_span_over_attribute_names():
    from rag.llm.evidence.conditions import bind_condition_refs, predicate_bindings, same_condition

    ctx = context()
    source = ctx["sources"][0]
    source["text"] = "Bằng kim loại quý; khối lượng không quá 10 kg."
    branch = {
        "parent_code": "711311",
        "attribute": "material",
        "criterion_quote": "Bằng kim loại quý",
        "evidence_ids": [source["evidence_id"]],
    }
    question = {
        "question": "Vật liệu của hàng hóa là gì?",
        "attribute": "vật liệu",
        "criterion_quote": "Bằng kim loại quý",
        "evidence_ids": branch["evidence_ids"],
    }
    bound = bind_condition_refs({"branch_checks": [branch], "clarifications": [question]}, ctx)
    assert same_condition(bound["clarifications"][0], bound["branch_checks"][0], ctx)
    question["criterion_quote"] = "khối lượng không quá 10 kg"
    question["attribute"] = "material"
    assert not same_condition(question, branch, ctx)
    spans = predicate_bindings(branch, ctx)
    assert source["text"][spans[0]["start"] : spans[0]["end"]] == branch["criterion_quote"]
    source["text"] += "; Bằng kim loại quý"
    assert not predicate_bindings(branch, ctx)


def test_recovery_never_restores_an_explanation_with_a_downgraded_dependency():
    ctx, old = completed()
    old["answer"]["results"][-1]["depends_on"] = [["G1", "I1"]]
    new = copy.deepcopy(old)
    new["answer"]["results"][0].update(
        status="INSUFFICIENT_LEGAL_EVIDENCE", suggested_hs_code="", review_valid=False
    )
    new["answer"]["results"][-1] = blocked(new["answer"]["results"][-1], "Review chưa hoàn tất.")
    final = _retain_completed(ctx, old, ctx, new)
    assert not final["answer"]["results"][-1].get("retained_after_recovery")


def test_span_identity_survives_display_relabeling_but_not_changed_evidence():
    from rag.llm.evidence.conditions import predicate_bindings

    ctx = context()
    source = ctx["sources"][0]
    row = {"evidence_ids": [source["evidence_id"]], "criterion_quote": source["text"]}
    before = predicate_bindings(row, ctx)
    source["label"] = "S999"
    assert predicate_bindings(row, ctx) == before
    source["evidence_id"] = "E" + "a" * 20
    assert not predicate_bindings(row, ctx)


def test_fact_display_uses_authentic_slice_even_when_model_quote_has_no_accents():
    ctx, draft = fact_draft()
    review = model_reviews(ctx, draft)
    claim = draft["results"][-1]["claims"][-1]
    check = review["analysis_reviews"][0]["checks"][-1]
    check.update(
        assessment="FACT_SUPPORTED", fact_ids=claim["fact_ids"], user_quotes=["day a bang bac 925"]
    )
    out, _ = run(ctx, [draft, review])
    assert "Dây A bằng bạc 925" in out["answer"]["answer"]
    assert "day a bang bac" not in out["answer"]["answer"]


def test_one_question_can_bind_alternative_predicates_of_the_same_property():
    from rag.llm.evidence.conditions import predicate_bindings, same_condition

    ctx = context()
    a, b = ctx["sources"][:2]
    a["text"], b["text"] = "Có lớp phủ bảo vệ.", "Không có lớp phủ bảo vệ."
    question = {
        "question": "Hàng có lớp phủ bảo vệ không?",
        "attribute": "lớp phủ",
        "evidence_ids": [a["evidence_id"], b["evidence_id"]],
        "criterion_quote": a["text"],
        "criterion_quotes": [
            {"evidence_id": a["evidence_id"], "quote": a["text"]},
            {"evidence_id": b["evidence_id"], "quote": b["text"]},
        ],
    }
    branch = {
        "parent_code": "711311",
        "attribute": "coating",
        "evidence_ids": [b["evidence_id"]],
        "criterion_quote": b["text"],
    }
    assert len(predicate_bindings(question, ctx)) == 2
    assert same_condition(question, branch, ctx)
    question["criterion_quotes"][1]["quote"] = "Công suất lớn."
    assert not same_condition(question, branch, ctx)


def test_analysis_repair_carries_claim_path_and_application_contract():
    ctx = context(explain=True)
    draft = model_answer(ctx)
    first = model_reviews(ctx, draft)
    first["analysis_reviews"][0]["checks"][0]["assessment"] = "APPLICATION"
    repaired = copy.deepcopy(first)
    check = repaired["analysis_reviews"][0]["checks"][0]
    statement = next(
        s for s in ctx["user_context"]["statements"] if "Dây A bằng bạc 925" in s["text"]
    )
    check.update(fact_ids=[statement["id"]], user_quotes=["Dây A bằng bạc 925"])
    out, calls = run(ctx, [draft, first, repaired])
    feedback = json.loads(calls[-1]["messages"][-1]["content"])
    issue = next(e for e in feedback["repair_errors"] if e["code"] == "APPLICATION_FACTS_REQUIRED")
    assert issue["path"] == "R3/checks/0"
    assert feedback["repair_contract"]["application_claim_indices"] == {"R3": [0]}
    assert feedback["repair_contract"]["read_only_claims"]
    assert out["validation"]["task_completion"]


def test_information_needed_for_classification_does_not_request_a_code():
    from rag.retrieval.request_plan import validate_request

    query = "Dây A bằng bạc. Hãy giải thích thông tin cần biết để phân loại từng mặt hàng, chưa cần chốt mã."
    request = {
        "items": [{"id": "I1", "anchor": "Dây A"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "EXPLAIN",
                "level": 0,
                "item_ids": ["I1"],
                "anchor": "Hãy giải thích thông tin cần biết để phân loại từng mặt hàng, chưa cần chốt mã.",
                "required": True,
            }
        ],
    }
    assert validate_request(query, request) == request


@pytest.mark.parametrize("assessment", ["REFERENCE", "APPLICATION"])
def test_review_level_metadata_does_not_require_a_code_for_general_rules(assessment):
    from rag.llm.review.analysis_review import check_analyses

    ctx = context(explain=True)
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)["analysis_reviews"]
    rows, _ = decode_task_answer(draft, ctx)
    source = ctx["sources"][0]
    source["code"] = None
    check = next(r for r in review if r["result_id"] == "R3")["checks"][0]
    check.update(assessment=assessment, application_level=8, evidence_ids=[source["evidence_id"]])
    if assessment == "APPLICATION":
        statement = next(
            s for s in ctx["user_context"]["statements"] if "Dây A bằng bạc 925" in s["text"]
        )
        check.update(fact_ids=[statement["id"]], user_quotes=["Dây A bằng bạc 925"])
    checked, errors = check_analyses(review, analysis_jobs(rows, ctx), rows, ctx)
    assert not errors
    assert checked["R3"]["analysis_checks"][0]["application_level"] == 0
    assert not checked["R3"]["suggested_hs_code"]
    check.update(assessment="INSUFFICIENT_LEGAL_EVIDENCE", application_level=8)
    assert check_analyses(review, analysis_jobs(rows, ctx), rows, ctx)[1]


def test_method_choice_with_no_requested_code_is_explanation_not_classification():
    from rag.retrieval.request_plan import validate_request

    query = (
        "Thiết bị A: phân loại từng thiết bị riêng biệt hoặc phân loại theo tổ hợp có được không?"
    )
    request = {
        "items": [{"id": "I1", "anchor": "Thiết bị A"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "CLASSIFY",
                "level": 0,
                "item_ids": ["I1"],
                "anchor": "phân loại từng thiết bị riêng biệt hoặc phân loại theo tổ hợp",
                "required": True,
            }
        ],
    }
    normalized = validate_request(query, request)
    assert normalized["objectives"][0]["kind"] == "EXPLAIN"
    request["objectives"][0]["anchor"] = "Thiết bị A"
    with pytest.raises(ValueError, match="classification_needs_items_and_level"):
        validate_request(query, request)


@pytest.mark.parametrize("wrapper", ["{}", "({})", "[{}]"])
def test_registry_ids_are_not_allowed_in_display_text_in_any_wrapper(wrapper):
    from rag.llm.evidence.evidence import render_claims

    ctx = context()
    eid = ctx["sources"][0]["evidence_id"]
    claim = {
        "kind": "LEGAL_ANALYSIS",
        "text": "Nguồn " + wrapper.format(eid),
        "evidence_ids": [eid],
        "fact_ids": [],
    }
    assert render_claims([claim], ctx)[2]


def test_explicit_right_to_choose_method_is_not_hs8_even_if_planner_says_hs8():
    from rag.retrieval.request_plan import validate_request

    query = "Doanh nghiệp có thể lựa chọn phân loại từng thiết bị riêng biệt hoặc phân loại theo tổ hợp máy không?"
    request = {
        "items": [{"id": "I1", "anchor": "thiết bị"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "CLASSIFY",
                "level": 8,
                "item_ids": ["I1"],
                "anchor": "phân loại từng thiết bị riêng biệt hoặc phân loại theo tổ hợp máy",
                "required": True,
            }
        ],
    }
    result = validate_request(query, request)
    assert result["objectives"][0]["kind"] == "EXPLAIN"
    assert result["objectives"][0]["level"] == 0
    direct = "Hãy phân loại từng thiết bị riêng biệt hoặc phân loại theo tổ hợp máy."
    assert validate_request(direct, request)["objectives"][0]["kind"] == "CLASSIFY"
    separate = "Doanh nghiệp có thể lựa chọn phương pháp nào? " + direct
    assert validate_request(separate, request)["objectives"][0]["kind"] == "CLASSIFY"
