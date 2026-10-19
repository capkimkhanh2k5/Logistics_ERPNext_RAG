import copy

import pytest

from rag.llm.evidence import bind_user_context
from rag.llm.grounding import discriminating_fact_errors
from tests.test_conditional_candidates import conditional_fixture
from tests.test_goal_workflow import run


@pytest.mark.parametrize(
    "source,quote,valid",
    [
        ("Dạng CKD:", "Tôi cần nhập khẩu xe VinFast VF 9", False),
        ("Dạng CKD:", "Xe SUV 7 chỗ", False),
        ("Dạng CKD:", "Bộ CKD đầy đủ", True),
        ("Dạng CKD:", "Xe không phải dạng CKD", False),
        ("Dạng CKD:", "Bộ đầy đủ dưới dạng tháo rời", True),
        ("Loại nguyên chiếc:", "Xe nhập khẩu nguyên chiếc CBU", True),
        ("Loại nguyên chiếc:", "Xe không nhập nguyên chiếc CBU mà nhập CKD", False),
        ("Loại nguyên chiếc:", "Chưa biết có nhập CBU hay không", False),
    ],
)
def test_import_presentation_requires_explicit_non_hypothetical_facts(source, quote, valid):
    assert bool(discriminating_fact_errors([source], [quote], satisfied=True)) is not valid


@pytest.mark.parametrize(
    "excluding,quote,valid",
    [
        (False, "Xe có pin lithium-ion 18 kWh", False),
        (False, "Xe có thể sạc từ nguồn điện bên ngoài", True),
        (False, "Xe có khả năng sạc ngoài", True),
        (False, "Xe không có khả năng sạc ngoài", False),
        (True, "Xe không có khả năng sạc ngoài", True),
        (True, "Xe có thể cắm sạc điện bên ngoài", False),
        (False, "Chưa rõ xe có sạc ngoài hay không", False),
        (True, "Xe không phải HEV", False),
        (False, "Xe không phải PHEV", False),
    ],
)
def test_battery_capacity_does_not_prove_external_charging_and_negation_is_preserved(
    excluding, quote, valid
):
    source = (
        "Kết hợp động cơ đốt trong và động cơ điện, "
        + ("trừ loại " if excluding else "")
        + "có khả năng nạp điện từ nguồn điện bên ngoài."
    )
    assert bool(discriminating_fact_errors([source], [quote], satisfied=True)) is not valid


def test_old_presentation_quote_cannot_override_latest_correction():
    question = "Xe nguyên chiếc CBU.\n\nThông tin người dùng bổ sung ở lượt 2: Tôi đính chính, không phải CBU mà là bộ CKD đầy đủ."
    context = {"request": {"items": [{"id": "I1"}]}, "user_context": bind_user_context(question)}
    assert discriminating_fact_errors(
        ["Loại nguyên chiếc:"], ["Xe nguyên chiếc CBU"], satisfied=True, context=context
    )
    assert not discriminating_fact_errors(
        ["Dạng CKD:"], ["bộ CKD đầy đủ"], satisfied=True, context=context
    )


def test_residual_branch_cannot_be_released_by_assuming_its_ckd_peer_is_ruled_out():
    ctx, draft, good = conditional_fixture()
    for source in ctx["sources"]:
        if source["text"] == "Loại nguyên chiếc:":
            source["text"] = "Loại khác:"
    bad = copy.deepcopy(good)
    fact = next(s for s in ctx["user_context"]["statements"] if "Xe điện SUV 7 chỗ" in s["text"])
    proof = {"fact_ids": [fact["id"]], "user_quotes": ["Xe điện SUV 7 chỗ"]}
    for row in bad["reviews"]:
        review = row["review"]
        review.update(
            status="SUPPORTED", clarifications=[], reason="Xe nguyên chiếc, phù hợp nhánh đang xét."
        )
        for check in review["condition_checks"]:
            check.update(assessment="SATISFIED", **proof)
        for assessment in review["candidate_assessments"]:
            assessment.update(
                assessment="POSSIBLE"
                if assessment["code"] == row["selected_code"]
                else "RULED_OUT",
                **proof,
            )
        for branch in review["branch_checks"]:
            branch.update(assessment="KNOWN", **proof)
    out, calls = run(ctx, [draft, bad, good])
    assert len(calls) == 3 and not out["diagnostics"]
    assert out["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert not out["answer"]["suggested_hs_code"]
    assert len(out["answer"]["hs_candidates"]) == 2
