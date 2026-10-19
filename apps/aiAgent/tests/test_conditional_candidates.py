"""Public candidates require independent evidence, not retrieval rank or confidence."""

import copy

import pytest

from rag.llm.answering import check_product_review
from rag.llm.evidence import bind_user_context
from rag.llm.grounding import defining_note_errors
from rag.llm.task_generation import _unreviewed_fallback
from rag.llm.task_validation import code_claim_errors, decode_task_answer
from tests.test_goal_reselection import fixture
from tests.test_goal_workflow import run


def conditional_fixture():
    ctx, draft, _ = fixture()
    ctx["question"] = ctx["question"].replace(", dạng CKD đầy đủ", "")
    ctx["user_context"] = bind_user_context(ctx["question"])
    row = draft["results"][0]
    row.update(status="MISSING_PRODUCT_INFO", code="", candidate_codes=["87038018", "87038098"])
    row["claims"][0]["text"] = "Cần xác nhận dạng nhập khẩu để phân định hai nhánh."
    branch_sources = [s for s in ctx["sources"] if s["text"] in {"Dạng CKD:", "Loại nguyên chiếc:"}]
    branch_ids = [s["evidence_id"] for s in branch_sources]
    question = {
        "question": "Xe nhập nguyên chiếc hay dạng linh kiện tháo rời?",
        "attribute": "dạng nhập khẩu",
        "evidence_ids": branch_ids,
    }
    row["clarifications"] = [question]
    by_label = {s["label"]: s for s in ctx["sources"]}
    fact = ctx["user_context"]["statements"][0]
    proof = {"fact_ids": [fact["id"]], "user_quotes": ["Xe điện SUV 7 chỗ"]}
    candidates = {c["code"]: c for c in [*ctx["candidate_evidence"], *ctx["comparison_candidates"]]}
    reviews = []
    for index, code in enumerate(row["candidate_codes"], 1):
        c = candidates[code]
        reviews.append(
            {
                "result_id": f"R1.C{index}",
                "selected_code": code,
                "review": {
                    "status": "MISSING_PRODUCT_INFO",
                    "reason": "Phù hợp nếu dạng nhập khẩu đáp ứng điều kiện nhánh đang xét.",
                    "condition_checks": [
                        {
                            "evidence_id": by_label[label]["evidence_id"],
                            "assessment": "MISSING_PRODUCT_INFO"
                            if by_label[label] in branch_sources
                            else "SATISFIED",
                            **(
                                {"fact_ids": [], "user_quotes": []}
                                if by_label[label] in branch_sources
                                else proof
                            ),
                        }
                        for label in c["required_citation_labels"]
                    ],
                    "clarifications": [question],
                    "missing_legal_evidence": [],
                    "candidate_assessments": [
                        {
                            "code": peer,
                            "assessment": "POSSIBLE",
                            "evidence_ids": branch_ids,
                            "fact_ids": [],
                            "user_quotes": [],
                        }
                        for peer in row["candidate_codes"]
                    ],
                    "branch_checks": [
                        {
                            "parent_code": "870380",
                            "attribute": "dạng nhập khẩu",
                            "assessment": "MISSING",
                            "evidence_ids": branch_ids,
                            "fact_ids": [],
                            "user_quotes": [],
                        }
                    ],
                },
            }
        )
    return ctx, draft, {"reviews": reviews}


def test_two_conditional_candidates_use_one_review_call_and_keep_discriminating_question():
    ctx, draft, review = conditional_fixture()
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert not out["diagnostics"]
    answer = out["answer"]
    assert answer["status"] == "MISSING_PRODUCT_INFO"
    assert answer["suggested_hs_code"] == ""
    assert len(answer["missing_information"]) == 1
    assert len(answer["hs_candidates"]) == 2
    for candidate in answer["hs_candidates"]:
        assert candidate["evidence_status"] == "CONDITIONAL"
        assert candidate["verified_path"]
        assert candidate["citations"] and candidate["conditions"]
        assert candidate["missing_information"]
        assert "confidence" not in candidate
    assert "cần bổ sung dữ kiện" in answer["answer"]


@pytest.mark.parametrize(
    "defect", ["unknown", "duplicate", "too_many", "wrong_level", "non_classify"]
)
def test_invalid_shortlists_never_enter_review(defect):
    ctx, draft, _ = conditional_fixture()
    row = draft["results"][0]
    if defect == "unknown":
        row["candidate_codes"] = ["12345678"]
    elif defect == "duplicate":
        row["candidate_codes"] *= 2
    elif defect == "too_many":
        row["candidate_codes"] = ["87038018", "87038098", "87038099", "87038090"]
    elif defect == "wrong_level":
        row["candidate_codes"] = ["8703"]
    else:
        ctx["request"]["objectives"][0]["kind"] = "EXPLAIN"
        row["item_id"] = ""
    decoded, errors = decode_task_answer(draft, ctx)
    if defect in {"duplicate", "too_many"}:
        assert errors
    else:
        assert not errors
        assert not decoded[0]["candidate_codes"]
        assert decoded[0]["discarded_candidate_codes"]


def test_invalid_candidate_does_not_get_published_or_silently_excluded():
    ctx, draft, review = conditional_fixture()
    review["reviews"][1]["review"]["condition_checks"] = []
    out, calls = run(ctx, [draft, review, review])
    assert len(calls) == 3
    assert out["answer"]["status"] == "REQUIRES_REVIEW"
    assert not out["answer"]["suggested_hs_code"]
    assert [c["code"] for c in out["answer"]["hs_candidates"]] == ["87038018"]
    assert out["diagnostics"]
    assert "?" not in out["answer"]["answer"]


def test_single_supported_candidate_not_padded_to_three():
    ctx, draft, review = fixture()
    # Existing single-code flow remains compatible; publish only its reviewed code.
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert [c["code"] for c in out["answer"]["hs_candidates"]] == ["87038018"]
    assert out["answer"]["hs_candidates"][0]["evidence_status"] == "SUPPORTED"


@pytest.mark.parametrize(
    "text",
    [
        "Hàng thuộc nhóm 8507, không thuộc nhóm 8708.",
        "Hàng thuộc nhóm 8507, không xếp vào nhóm 8708.",
        "Hàng thuộc nhóm 8507, loại trừ khỏi nhóm 87.08.",
        "Hàng thuộc nhóm 8507 thay vì nhóm 8708.",
    ],
)
def test_negative_competitor_reference_is_not_another_recommendation(text):
    ctx = {"question": "8507 hay 8708?", "sources": [], "candidate_evidence": []}
    assert not code_claim_errors([{"kind": "CONCLUSION", "text": text}], "8507", ctx)
    assert code_claim_errors([{"kind": "CONCLUSION", "text": "Hàng thuộc nhóm 8708."}], "8507", ctx)


def test_failed_review_cannot_release_applied_claim_under_legal_analysis_label():
    ctx, draft, _ = fixture()
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    row = rows[0]
    row["claims"] = [
        {
            "kind": "LEGAL_ANALYSIS",
            "text": "Hàng này thuộc mã 87038098.",
            "evidence_ids": [],
            "fact_ids": [],
        }
    ]
    result = _unreviewed_fallback(row, ctx, "Chưa kiểm tra được.")
    assert "Hàng này thuộc" not in result["answer"]
    assert not result["suggested_hs_code"]


def test_partial_review_cannot_mark_payload_as_gross_weight_satisfied():
    ctx, draft, review = fixture()
    from rag.llm.task_generation import review_jobs

    rows, _ = decode_task_answer(draft, ctx)
    _, scopes = review_jobs(rows, ctx)
    scoped, proposed, _ = scopes["R1"]
    candidate = copy.deepcopy(scoped["candidate_evidence"][0])
    label = candidate["required_citation_labels"][0]
    source = next(s for s in scoped["sources"] if s["label"] == label)
    source["text"] = "Khối lượng toàn bộ theo thiết kế không quá 5 tấn."
    scoped["response_protocol"] = None
    scoped["question"] = "Trọng tải hàng hóa thiết kế 950 kg."
    value = {
        "status": "MISSING_PRODUCT_INFO",
        "reason": "Cần xác nhận dạng nhập khẩu.",
        "product_facts": [{"fact": scoped["question"], "user_quote": scoped["question"]}],
        "condition_checks": [
            {
                "source_label": label,
                "source_quote": source["text"],
                "assessment": "SATISFIED",
                "product_fact_indices": [0],
            }
        ],
        "missing_information": ["Nhập nguyên chiếc hay tháo rời?"],
        "missing_legal_evidence": [],
    }
    _, _, errors = check_product_review(value, scoped, candidate, proposed, {label})
    assert any("định lượng" in e for e in errors)


def test_name_alone_does_not_prove_defining_note_even_in_partial_review():
    candidate = {"defining_note_labels": ["S1"]}
    sources = {
        "S1": {"text": "Điện thoại thông minh có hệ điều hành cho phép tải và chạy ứng dụng."}
    }
    review = {
        "status": "MISSING_PRODUCT_INFO",
        "product_facts": [{"user_quote": "điện thoại iPhone 18 Pro Max nguyên chiếc"}],
        "condition_checks": [
            {"source_label": "S1", "assessment": "SATISFIED", "product_fact_indices": [0]}
        ],
    }
    assert defining_note_errors(review, sources, candidate)
    review["condition_checks"][0]["assessment"] = "MISSING_PRODUCT_INFO"
    assert not defining_note_errors(review, sources, candidate)


def test_conflicting_candidate_reviews_never_promote_one_supported_over_another_possible():
    from rag.llm.shortlist import collapse_rows, expand_rows
    from rag.llm.task_generation import _review_payload, review_jobs

    ctx, draft, review = conditional_fixture()
    original, errors = decode_task_answer(draft, ctx)
    assert not errors
    expanded, groups = expand_rows(original, ctx)
    _, scopes = review_jobs(expanded, ctx)
    checked, errors = _review_payload(review, ctx, scopes)
    assert not errors
    members = list(checked.values())
    # Simulate two individually valid but mutually inconsistent model reviews.
    members[0].update(status="RECOMMENDATION", suggested_hs_code="87038018")
    members[0]["review"]["status"] = "SUPPORTED"
    merged = collapse_rows(original, members, groups, ctx)[0]
    assert merged["status"] != "RECOMMENDATION"
    assert not merged["suggested_hs_code"]
    assert not any(c["evidence_status"] == "SUPPORTED" for c in merged["hs_candidates"])


def test_three_candidates_expand_into_one_batch_with_distinct_job_ids():
    from rag.llm.shortlist import expand_rows

    ctx, draft, _ = conditional_fixture()
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    # The expansion unit receives already catalogue-validated codes.
    rows[0]["candidate_codes"].append("87038019")
    expanded, groups = expand_rows(rows, ctx)
    assert groups == {"R1": ["R1.C1", "R1.C2", "R1.C3"]}
    assert len(expanded) == 3
    assert len({r["suggested_hs_code"] for r in expanded}) == 3


def test_negation_in_previous_clause_cannot_hide_a_positive_code_application():
    ctx = {"question": "8507 hay 8708?", "sources": [], "candidate_evidence": []}
    for text in [
        "Không thuộc loại này. Hàng thuộc nhóm 8708.",
        "Không thuộc loại này nhưng hàng thuộc nhóm 8708.",
    ]:
        assert code_claim_errors([{"kind": "CONCLUSION", "text": text}], "8507", ctx)


def test_source_bound_question_with_verbatim_branch_label_accepts_attribute_alias():
    from rag.llm.disambiguation import disambiguation_errors
    from rag.llm.shortlist import expand_rows
    from rag.llm.task_generation import review_jobs

    ctx, draft, review = conditional_fixture()
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    expanded, _ = expand_rows(rows, ctx)
    _, scopes = review_jobs(expanded, ctx)
    scoped, _, _ = scopes["R1.C1"]
    raw = review["reviews"][0]["review"]
    raw["branch_checks"][0]["attribute"] = "dạng linh kiện rời (CKD) hay xe nguyên chiếc"
    raw["clarifications"][0]["attribute"] = "dạng nhập khẩu (CKD hay nguyên chiếc)"
    raw["clarifications"][0]["question"] = (
        "Xe nhập khẩu dưới dạng linh kiện rời (CKD) hay xe nguyên chiếc?"
    )
    assert not disambiguation_errors(raw, scoped, "87038018")
    raw["clarifications"][0]["evidence_ids"] = ["Eforeign"]
    assert disambiguation_errors(raw, scoped, "87038018")


def test_recovery_rebinds_nested_candidate_citations_and_conditions():
    from rag.llm.recovery import _retain_completed

    ctx, draft, review = fixture()
    old, _ = run(ctx, [draft, review])
    updated = copy.deepcopy(ctx)
    for index, source in enumerate(updated["sources"], 101):
        source["label"] = f"S{index}"
    generated = copy.deepcopy(old)
    row = generated["answer"]["results"][0]
    row.update(
        status="REQUIRES_REVIEW",
        suggested_hs_code="",
        answer="Chưa hoàn tất.",
        citations=[],
        hs_candidates=[],
        review_valid=False,
    )
    result = _retain_completed(ctx, old, updated, generated)
    by_label = {source["label"]: source for source in updated["sources"]}
    candidate = result["answer"]["hs_candidates"][0]
    assert all(
        c["label"] in by_label and c["quote"] == by_label[c["label"]]["text"]
        for c in candidate["citations"]
    )
    assert all(
        c["source_label"] in by_label and c["text"] == by_label[c["source_label"]]["text"]
        for c in candidate["conditions"]
    )


def test_conditional_review_can_name_its_own_code_without_publishing_a_recommendation():
    ctx, draft, review = conditional_fixture()
    for row in review["reviews"]:
        row["review"]["reason"] = (
            f"Chưa thể phân loại vào mã {row['selected_code']} vì thiếu dữ kiện dạng nhập khẩu."
        )
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert not out["diagnostics"]
    assert out["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert len(out["answer"]["hs_candidates"]) == 2
    assert not out["answer"]["suggested_hs_code"]


@pytest.mark.parametrize(
    "quote, valid",
    [
        ("Có SIM 5G và có thể gọi thoại qua mạng di động.", False),
        ("Các chức năng được tích hợp trong cùng một vỏ.", False),
        ("Bộ thu phát được nhập khẩu riêng, không kèm máy tính.", True),
        ("Bộ thu phát không được trình bày riêng rẽ.", False),
    ],
)
def test_separately_presented_exclusion_needs_explicit_presentation_fact(quote, valid):
    from rag.llm.grounding import presentation_scope_errors

    source = "Nhóm này không bao gồm các hàng hóa sau đây khi nó được trình bày riêng rẽ: thiết bị truyền nhận dữ liệu."
    assert bool(presentation_scope_errors([source], [quote])) is not valid


def test_defining_note_guard_accepts_explicit_material_and_absence_clause():
    sources = {"S1": {"text": "Đồ trang sức bằng kim loại cơ bản, không gắn đá quý."}}
    candidate = {"defining_note_labels": ["S1"]}
    review = {
        "product_facts": [{"user_quote": "Dây chuyền bằng thép không gỉ mạ vàng, không đính đá."}],
        "condition_checks": [
            {"source_label": "S1", "assessment": "SATISFIED", "product_fact_indices": [0]}
        ],
    }
    assert not defining_note_errors(review, sources, candidate)


def test_candidate_review_keeps_cited_principle_and_pending_question_as_hypotheses():
    from rag.llm.shortlist import expand_rows
    from rag.llm.task_generation import review_jobs

    ctx, draft, _ = conditional_fixture()
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    expanded, _ = expand_rows(rows, ctx)
    jobs, _ = review_jobs(expanded, ctx)
    assert jobs[0]["proposed_answer"]["clarifications"] == draft["results"][0]["clarifications"]
    assert expanded[0]["review_evidence_labels"] == [c["label"] for c in rows[0]["citations"]]
    assert expanded[0]["claims"] == []  # Draft applications never become confirmed claims.


@pytest.mark.parametrize("same_item", [True, False])
def test_detail_inherits_only_same_item_parent_clarification(same_item):
    from tests.test_goal_workflow import context, model_answer

    ctx = context()
    draft = model_answer(ctx)
    parent = draft["results"][0 if same_item else 1]
    parent.update(
        status="MISSING_PRODUCT_INFO",
        code="",
        clarifications=[
            {
                "question": "Kim loại nền thực tế của dây chuyền là gì?",
                "attribute": "kim loại nền",
                "evidence_ids": parent["claims"][0]["evidence_ids"],
            }
        ],
    )
    ctx["request"]["objectives"].append(
        {
            "id": "G2",
            "kind": "CLASSIFY",
            "level": 8,
            "item_ids": ["I1"],
            "required": True,
            "anchor": "Xác định nhóm HS",
        }
    )
    draft["results"].append(
        {
            "objective_id": "G2",
            "item_id": "I1",
            "status": "MISSING_PRODUCT_INFO",
            "code": "",
            "claims": [
                {
                    "kind": "LEGAL_ANALYSIS",
                    "text": "Chờ xác định kim loại nền.",
                    "evidence_ids": draft["results"][0]["claims"][0]["evidence_ids"],
                    "fact_ids": [],
                }
            ],
            "clarifications": [],
            "missing_legal_evidence": [],
        }
    )
    rows, errors = decode_task_answer(draft, ctx)
    if same_item:
        assert not errors
        assert rows[-1]["missing_information"] == [parent["clarifications"][0]["question"]]
        assert rows[-1]["clarifications_inherited"]
        assert not rows[-1]["candidate_codes"]
    else:
        assert any("MISSING_PRODUCT_INFO" in e for e in errors)


def test_shortlist_preserves_independently_supported_peer_reselection():
    ctx, draft, review = fixture()
    draft["results"][0]["candidate_codes"] = ["87038098"]
    review["reviews"][0]["result_id"] = "R1.C1"
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert not out["diagnostics"]
    assert out["answer"]["suggested_hs_code"] == "87038018"
    assert [c["code"] for c in out["answer"]["hs_candidates"]] == ["87038018"]


def test_duplicate_supported_reselections_collapse_to_one_candidate():
    ctx, draft, review = fixture()
    draft["results"][0]["candidate_codes"] = ["87038098", "87038018"]
    second = copy.deepcopy(review["reviews"][0])
    review["reviews"][0]["result_id"] = "R1.C1"
    second["result_id"] = "R1.C2"
    review["reviews"].append(second)
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert not out["diagnostics"]
    assert out["answer"]["suggested_hs_code"] == "87038018"
    assert len(out["answer"]["hs_candidates"]) == 1


def test_shortlist_normalization_never_validates_an_unknown_primary_or_claim():
    ctx, draft, _ = fixture()
    row = draft["results"][0]
    row.update(code="12345678", candidate_codes=["87038098"])
    assert decode_task_answer(draft, ctx)[1]
    row.update(code="87038098", candidate_codes=["12345678"])
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    assert rows[0]["candidate_codes"] == ["87038098"]
    row["claims"][0]["text"] = "Đề xuất mã 12345678."
    assert decode_task_answer(draft, ctx)[1]
