"""Regressions from the full primary-only run: corrections, questions and prose."""

import copy

import pytest

from rag.llm.evidence import (
    bind_evidence,
    bind_user_context,
    clarification_errors,
    unique_clarifications,
)
from rag.llm.grounding import discriminating_fact_errors, unsupported_qualifier_errors
from rag.llm.task_generation import _resolve_comparisons
from rag.llm.task_validation import code_claim_errors, item_context
from tests.test_conditional_candidates import conditional_fixture
from tests.test_goal_workflow import context, run


def test_later_ckd_correction_keeps_gir_mandatory_after_earlier_request():
    ctx, _, _ = conditional_fixture()
    ctx["question"] = (
        "Xe nguyên chiếc CBU. Hãy đề xuất mã HS."
        "\n\nThông tin người dùng bổ sung ở lượt 2: Đính chính: bộ linh kiện CKD đầy đủ."
    )
    ctx["user_context"] = bind_user_context(ctx["question"])
    ctx["application_rule_labels"] = ["S999"]
    scoped = item_context(ctx, "I1", 8, "87038018")
    assert all("S999" in c["required_citation_labels"] for c in scoped["candidate_evidence"])
    ctx["question"] += "\n\nThông tin người dùng bổ sung ở lượt 3: Đính chính: xe nguyên chiếc CBU."
    ctx["user_context"] = bind_user_context(ctx["question"])
    assert all(
        "S999" not in c["required_citation_labels"]
        for c in item_context(ctx, "I1", 8, "87038098")["candidate_evidence"]
    )


def test_ckd_of_other_item_cannot_require_gir_for_assembled_item():
    ctx = context()
    ctx["question"] = "Dây A nguyên chiếc CBU. Dây B dạng CKD đầy đủ. Hãy phân loại."
    ctx["user_context"] = bind_user_context(ctx["question"])
    ctx["application_rule_labels"] = ["S999"]
    assert all(
        "S999" not in c["required_citation_labels"]
        for c in item_context(ctx, "I1", 4, "7113")["candidate_evidence"]
    )


def test_pending_classification_keeps_only_reviewed_independent_explanation():
    ctx = context(explain=True)
    source = ctx["sources"][0]
    claims = [
        {
            "kind": "LEGAL_ANALYSIS",
            "text": "Quy định về ngưỡng đã rõ.",
            "evidence_ids": [source["evidence_id"]],
            "fact_ids": [],
        },
        {
            "kind": "CONCLUSION",
            "text": "Dây A thuộc nhóm đã chọn.",
            "evidence_ids": [source["evidence_id"]],
            "fact_ids": [],
        },
    ]
    row = {
        "objective_id": "G2",
        "item_id": "",
        "kind": "EXPLAIN",
        "status": "ANSWERED",
        "claims": claims,
        "depends_on": [["G1", "I1"]],
        "analysis_review_valid": True,
        "analysis_checks": [
            {"claim_index": 0, "assessment": "REFERENCE"},
            {"claim_index": 1, "assessment": "APPLICATION"},
        ],
    }
    result = _resolve_comparisons([row], ctx)[0]
    assert result["status"] == "REQUIRES_REVIEW"
    assert "Quy định về ngưỡng" in result["answer"]
    assert "Dây A thuộc" not in result["answer"]
    assert result["citations"] == [{"label": source["label"], "quote": source["text"]}]
    unreviewed = copy.deepcopy(row)
    unreviewed["analysis_review_valid"] = False
    assert "Quy định về ngưỡng" not in _resolve_comparisons([unreviewed], ctx)[0]["answer"]


def test_question_dedup_retains_distinct_attributes_and_sources():
    q = {
        "attribute": "primary_function",
        "evidence_ids": ["E1"],
        "question": "Chức năng chính là gì?",
    }
    assert unique_clarifications([q, {**q, "question": "Máy dùng chính để làm gì?"}]) == [q]
    assert (
        len(
            unique_clarifications(
                [q, {**q, "attribute": "secondary_function"}, {**q, "evidence_ids": ["E2"]}]
            )
        )
        == 3
    )


def test_primary_function_question_requires_the_actual_classification_criterion():
    ctx = {
        "sources": bind_evidence(
            [
                {"id": "definition", "label": "S1", "text": "Máy xử lý dữ liệu tự động."},
                {
                    "id": "criterion",
                    "label": "S2",
                    "text": "Máy đa chức năng được phân loại theo chức năng chính.",
                },
            ]
        ),
        "user_context": {"statements": []},
    }
    question = {
        "attribute": "primary_function",
        "question": "Chức năng chính là gì?",
        "evidence_ids": [ctx["sources"][0]["evidence_id"]],
    }
    assert clarification_errors([question], ctx)
    question["evidence_ids"] = [ctx["sources"][1]["evidence_id"]]
    assert not clarification_errors([question], ctx)


def test_conditional_candidates_keep_question_rule_citation_and_ask_once():
    ctx, draft, review = conditional_fixture()
    rule = bind_evidence(
        [
            {
                "id": "presentation-rule",
                "label": "S999",
                "text": "Phân biệt dạng nhập khẩu khi trình bày.",
            }
        ]
    )[0]
    ctx["sources"].append(rule)
    for index, row in enumerate(review["reviews"]):
        question = copy.deepcopy(row["review"]["clarifications"][0])
        row["review"]["clarifications"] = [question]
        question["evidence_ids"].append(rule["evidence_id"])
        if index:
            question["question"] = "Hàng nguyên chiếc hay tháo rời?"
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2 and not out["diagnostics"]
    assert len(out["answer"]["missing_information"]) == 1
    assert all(
        any(c["label"] == "S999" for c in candidate["citations"])
        for candidate in out["answer"]["hs_candidates"]
    )


@pytest.mark.parametrize(
    "statement",
    [
        "Thiết bị có camera tích hợp vĩnh viễn.",
        "Camera kỹ thuật số được gắn vĩnh viễn trên phương tiện.",
        "Thiết bị là phương tiện bay không người lái, đáp ứng mô tả tại nhóm 8806 và Chú giải Chương 88, được trang bị camera kỹ thuật số tích hợp vĩnh viễn.",
    ],
)
def test_integrated_camera_does_not_prove_permanence(statement):
    assert unsupported_qualifier_errors([statement], ["Thiết bị tích hợp camera 4K."])
    assert not unsupported_qualifier_errors([statement], ["Camera tích hợp vĩnh viễn."])
    assert unsupported_qualifier_errors([statement], ["Không có camera tích hợp vĩnh viễn."])
    assert not unsupported_qualifier_errors(
        ["Nguồn quy định thiết bị có camera tích hợp vĩnh viễn."], []
    )
    assert not unsupported_qualifier_errors(
        ["Nếu camera tích hợp vĩnh viễn thì xét điều kiện này."], []
    )


@pytest.mark.parametrize("excluded", ["8525", "85258010"])
def test_postfix_rejection_is_not_a_new_code_recommendation(excluded):
    ctx = {"question": "8806 hay 8525?", "sources": [{"code": excluded}], "candidate_evidence": []}
    text = f"Thiết bị thuộc nhóm 8806, mã {excluded} không phù hợp."
    assert not code_claim_errors([{"kind": "CONCLUSION", "text": text}], "8806", ctx)
    text += f" Nhưng hàng hóa này phải phân loại vào mã {excluded}."
    assert code_claim_errors([{"kind": "CONCLUSION", "text": text}], "8806", ctx)


@pytest.mark.parametrize(
    "quote,valid",
    [
        ("Xe SUV diesel 7 chỗ.", False),
        ("Xe chỉ sử dụng động cơ diesel.", True),
        ("Xe chỉ động cơ nhiên liệu.", True),
        ("Xe không chỉ sử dụng động cơ diesel.", False),
        ("Xe diesel, không có động cơ điện tạo lực kéo.", True),
        ("Xe diesel và động cơ điện cùng tạo lực kéo.", False),
        ("Nếu xe chỉ sử dụng động cơ diesel.", False),
        ("Chưa rõ có động cơ điện hay không.", False),
    ],
)
def test_fuel_name_does_not_prove_exclusive_combustion_propulsion(quote, valid):
    source = "Xe khác, loại chỉ sử dụng động cơ đốt trong kiểu piston cháy do nén (diesel hoặc bán diesel)."
    assert bool(discriminating_fact_errors([source], [quote], satisfied=True)) is not valid
    # Excluding this branch does not require proving its positive exclusivity condition.
    assert not discriminating_fact_errors([source], [quote], satisfied=False)
