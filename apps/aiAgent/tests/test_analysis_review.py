import copy

from rag.llm.generation.task_generation import review_jobs
from rag.llm.review.analysis_review import analysis_jobs, check_analyses
from rag.llm.validation.application_rules import assembly_hypothesis
from rag.llm.validation.task_validation import decode_task_answer, item_context
from tests.support.legacy_grounding import indirect_drive_gap
from tests.test_conditional_candidates import conditional_fixture
from tests.test_goal_workflow import context, model_answer, model_reviews, run


def test_explanation_application_gap_suppresses_code_and_leaf_question_in_same_batch():
    ctx, draft, review = conditional_fixture()
    ctx["request"]["objectives"].append(
        {
            "id": "G2",
            "kind": "EXPLAIN",
            "level": 0,
            "item_ids": ["I1"],
            "anchor": "Xe điện",
            "required": True,
        }
    )
    claim = {
        "kind": "LEGAL_ANALYSIS",
        "text": "Hàng hóa này được xếp vào loại đang tranh chấp.",
        "evidence_ids": [ctx["sources"][0]["evidence_id"]],
        "fact_ids": [],
    }
    draft["results"].append(
        {
            "objective_id": "G2",
            "item_id": "",
            "status": "ANSWERED",
            "code": "",
            "claims": [claim],
            "clarifications": [],
            "missing_legal_evidence": [],
        }
    )
    review["analysis_reviews"] = [
        {
            "result_id": "R2",
            "checks": [
                {
                    "claim_index": 0,
                    "assessment": "INSUFFICIENT_LEGAL_EVIDENCE",
                    "evidence_ids": claim["evidence_ids"],
                    "fact_ids": [],
                    "user_quotes": [],
                    "reason": "Thiếu quy định phân định cơ chế cụ thể.",
                }
            ],
        }
    ]
    # Invalid leaf checks become irrelevant once a reviewed parent application gap blocks them.
    for candidate in review["reviews"]:
        candidate["review"]["condition_checks"] = []
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert not out["diagnostics"]
    assert out["generation"]["task_review"]["superseded_errors"]
    assert out["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert "Hàng hóa này được xếp" not in out["answer"]["answer"]
    assert not out["answer"]["missing_information"]
    assert not any(row.get("hs_candidates") for row in out["answer"]["results"])


def test_missing_explanation_review_is_not_implicitly_supported():
    ctx = context(explain=True)
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    review.pop("analysis_reviews")
    out, calls = run(ctx, [draft, review, review])
    assert len(calls) == 3 and out["diagnostics"]
    assert not out["validation"]["task_completion"]


def test_analysis_review_cannot_use_other_item_quotes_or_fake_sources():
    ctx = context(explain=True)
    rows, _ = decode_task_answer(model_answer(ctx), ctx)
    jobs = analysis_jobs(rows, ctx)
    jobs[0]["item_ids"] = ["I1"]
    checks = [
        {
            "result_id": "R3",
            "checks": [
                {
                    "claim_index": 0,
                    "assessment": "APPLICATION",
                    "evidence_ids": ["fake"],
                    "fact_ids": [ctx["user_context"]["statements"][0]["id"]],
                    "user_quotes": ["Dây B bằng thép mạ vàng"],
                    "reason": "Áp dụng cho Dây A.",
                }
            ],
        }
    ]
    checked, errors = check_analyses(checks, jobs, rows, ctx)
    assert not checked and errors


def test_indirect_mechanism_needs_interpretation_not_generic_heading():
    question = "Động cơ xăng không truyền lực cơ học trực tiếp đến bánh xe."
    generic = "Kết hợp động cơ đốt trong và động cơ điện để tạo động lực."
    assert indirect_drive_gap(question, [generic])
    assert not indirect_drive_gap(
        question, [generic, "Giải thích cơ chế máy phát điện và truyền lực gián tiếp."]
    )
    assert not indirect_drive_gap("Cả hai động cơ tạo lực kéo.", [generic])


def test_assembly_hypothesis_uses_latest_presentation_and_does_not_infer_from_model():
    assert assembly_hypothesis("Bộ linh kiện CKD đầy đủ.")
    assert not assembly_hypothesis("Xe VF9.")
    assert not assembly_hypothesis("Xe không phải dạng CKD.")
    assert not assembly_hypothesis(
        "Bộ CKD.\n\nThông tin người dùng bổ sung ở lượt 2: Không phải CKD."
    )
    assert not assembly_hypothesis(
        "Bộ CKD.\n\nThông tin người dùng bổ sung ở lượt 2: Xe nguyên chiếc CBU."
    )
    assert assembly_hypothesis(
        "Xe nguyên chiếc CBU.\n\nThông tin người dùng bổ sung ở lượt 2: Không phải CBU mà là CKD đầy đủ."
    )
    assert assembly_hypothesis(
        "Lô hàng gồm các bộ laptop đầy đủ, chưa lắp ráp. Có thể phân loại theo laptop nguyên chiếc hay không?"
    )


def test_review_requires_available_assembly_rule_in_addition_to_branch_wording():
    ctx, draft, _ = conditional_fixture()
    ctx["application_rule_labels"] = [ctx["sources"][0]["label"]]
    from rag.llm.evidence.evidence import bind_user_context

    ctx["question"] = "Xe điện SUV 7 chỗ, bộ CKD đầy đủ."
    ctx["user_context"] = bind_user_context(ctx["question"])
    scoped = item_context(ctx, "I1", 8, "87038018")
    assert all(
        ctx["application_rule_labels"][0] in c["required_citation_labels"]
        for c in scoped["candidate_evidence"]
    )


def test_valid_independent_review_survives_other_jobs_repair_regression():
    ctx = context()
    draft = model_answer(ctx)
    first = model_reviews(ctx, draft)
    second = copy.deepcopy(first)
    first["reviews"][1]["review"]["reason"] = ""
    second["reviews"][0]["review"]["reason"] = ""
    out, calls = run(ctx, [draft, first, second])
    assert len(calls) == 3
    assert all(row.get("review_valid") for row in out["answer"]["results"])
    assert out["validation"]["task_completion"] and not out["diagnostics"]


def test_unavailable_peer_becomes_legal_gap_never_silent_exclusion():
    from rag.llm.generation.task_generation import _review_payload

    ctx, draft, review = conditional_fixture()
    rows, _ = decode_task_answer(draft, ctx)
    from rag.llm.generation.shortlist import expand_rows

    expanded, _ = expand_rows(rows, ctx)
    _, scopes = review_jobs(expanded, ctx)
    for scoped, _, _ in scopes.values():
        scoped["candidate_comparison"][0]["missing_codes"] = ["87038099"]
        scoped["candidate_comparison"][0]["codes"].append("87038099")
    for row in review["reviews"]:
        row["review"]["candidate_assessments"].append(
            {
                "code": "87038099",
                "assessment": "RULED_OUT",
                "evidence_ids": [],
                "fact_ids": [],
                "user_quotes": [],
            }
        )
    checked, errors = _review_payload(review, ctx, scopes)
    assert not errors
    assert all(
        row["status"] == "INSUFFICIENT_LEGAL_EVIDENCE" and not row["suggested_hs_code"]
        for row in checked.values()
    )


def test_applied_classification_cannot_hide_under_reference_label():
    ctx = context(explain=True)
    main = model_answer(ctx)
    main["results"][-1]["claims"][0]["text"] = "Sản phẩm này được xếp vào nhóm phù hợp."
    rows, _ = decode_task_answer(main, ctx)
    jobs = analysis_jobs(rows, ctx)
    review = model_reviews(ctx, main)["analysis_reviews"]
    checked, errors = check_analyses(review, jobs, rows, ctx)
    assert "R3" not in checked and any("ASSESSMENT_MISMATCH" in e for e in errors)


def test_parent_review_finishes_before_child_jobs_are_created(monkeypatch):
    from types import SimpleNamespace

    from rag.llm.generation.task_generation import review_by_level

    observed = []

    def review(rows, context, run):
        observed.append([r["level"] for r in rows])
        return [{**r, "review_valid": True} for r in rows], {
            "valid": True,
            "errors": [],
            "checked_results": [r["result_id"] for r in rows],
        }

    monkeypatch.setattr("rag.llm.generation.task_generation.review_results", review)
    rows = [
        {
            "result_id": f"R{i}",
            "kind": "CLASSIFY",
            "item_id": "I1",
            "level": level,
            "required": True,
            "status": "RECOMMENDATION",
            "suggested_hs_code": "1" * level,
        }
        for i, level in enumerate([8, 4], 1)
    ]
    result, report = review_by_level(rows, {}, SimpleNamespace())
    assert observed == [[4], [8]]
    assert [r["level"] for r in result] == [8, 4] and report["waves"] == 2


def test_detail_application_gap_does_not_invalidate_independently_reviewed_heading():
    from rag.llm.review.analysis_review import resolve_analysis_gaps

    rows = [
        {
            "kind": "CLASSIFY",
            "level": level,
            "item_id": "I1",
            "status": "RECOMMENDATION",
            "suggested_hs_code": "1" * level,
            "review_valid": True,
        }
        for level in [4, 8]
    ]
    rows.append(
        {
            "kind": "EXPLAIN",
            "objective_id": "G3",
            "application_evidence_gap": True,
            "application_gap_level": 6,
            "status": "INSUFFICIENT_LEGAL_EVIDENCE",
            "missing_legal_evidence": ["Thiếu căn cứ cho phân nhóm."],
        }
    )
    result = resolve_analysis_gaps(
        rows, {"request": {"objectives": [{"id": "G3", "item_ids": ["I1"]}]}}
    )
    assert result[0]["status"] == "RECOMMENDATION"
    assert (
        result[1]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE" and not result[1]["suggested_hs_code"]
    )


def test_pure_product_explanation_is_reviewed_without_requiring_a_classify_goal():
    ctx = context(explain=True)
    rows, _ = decode_task_answer(model_answer(ctx), ctx)
    explanation = rows[-1]
    assert analysis_jobs([explanation], ctx)


def test_rendered_analysis_citations_follow_the_proof_actually_reviewed():
    ctx = context(explain=True)
    main = model_answer(ctx)
    rows, _ = decode_task_answer(main, ctx)
    jobs = analysis_jobs(rows, ctx)
    review = model_reviews(ctx, main)["analysis_reviews"]
    evidence = ctx["sources"][0]
    next(r for r in review if r["result_id"] == "R3")["checks"][0]["evidence_ids"] = [evidence["evidence_id"]]
    checked, errors = check_analyses(review, jobs, rows, ctx)
    assert not errors
    assert [c["label"] for c in checked["R3"]["citations"]] == [evidence["label"]]
