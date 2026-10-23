"""Numeric source conditions require actual user quantities, not product-name guesses."""

import copy

import pytest

from rag.llm.validation.quantitative import quantitative_grounding_errors


def supported(source="Khối lượng không quá 10 kg.", quote="Khối lượng 2 kg.", *, source_quote=None):
    sources = {"S1": {"text": source}}
    review = {
        "status": "SUPPORTED",
        "product_facts": [{"fact": "Thông tin hàng hóa", "user_quote": quote}],
        "condition_checks": [
            {
                "source_label": "S1",
                "source_quote": source if source_quote is None else source_quote,
                "assessment": "SATISFIED",
                "product_fact_indices": [0],
            }
        ],
    }
    return review, sources


@pytest.mark.parametrize(
    "quote",
    [
        "Máy có khối lượng 2 kg.",
        "Máy có khối lượng 2000 g.",
        "Khối lượng không quá 10 kg.",
        "Khối lượng dưới 10 kg.",
        "Khối lượng 2,5 kg.",
        "Khối lượng 2.5 kg.",
        "Khối lượng không vượt quá 2500 g.",
        "Máy xử lý dữ liệu tự động có khối lượng 2 kg.",
    ],
)
def test_actual_measurement_or_compatible_explicit_bound_proves_source_limit(quote):
    review, sources = supported(quote=quote)
    assert not quantitative_grounding_errors(review, sources, {"S1"})


@pytest.mark.parametrize(
    "quote",
    [
        "Máy có khối lượng 20 kg.",
        "Khối lượng ít nhất 2 kg.",
        "Khối lượng lớn hơn 2 kg.",
        "Khối lượng không quá 20 kg.",
        "Điện thoại Model 18 Pro, máy tính Alpha M5 Pro.",
        "Máy nhẹ và là máy tính xách tay.",
        "Công suất 2 W.",
        "Có thể máy có khối lượng 2 kg.",
        "Không biết có quá 10 kg không?",
        "Not sure whether the weight is 2 kg.",
        "Maybe the weight is 2 kg.",
        "Nếu khối lượng là 2 kg thì phù hợp.",
        "Khối lượng không phải 2 kg.",
        "Khối lượng 2 kg hoặc 20 kg.",
        "Weight from 2 kg to 3 kg.",
        "Khối lượng từ 2 kg đến 3 kg.",
        "Khối lượng 2-3 kg.",
        "Khối lượng 1.000 kg.",
    ],
)
def test_missing_uncertain_incompatible_or_insufficient_measurement_does_not_prove_limit(quote):
    review, sources = supported(quote=quote)
    errors = quantitative_grounding_errors(review, sources, {"S1"})
    assert errors
    assert "khối lượng" in errors[0]
    assert "[MEASUREMENT_UNPROVEN]" in errors[0]
    assert "[S1]" in errors[0]


def test_model_fact_paraphrase_cannot_invent_a_measurement_absent_from_user_quote():
    review, sources = supported(quote="Máy tính xách tay có CPU, bàn phím và màn hình.")
    review["product_facts"][0]["fact"] = "Khối lượng của máy là 2 kg."
    assert quantitative_grounding_errors(review, sources, {"S1"})


def test_full_required_source_is_checked_when_reviewer_omits_weight_clause_from_quote():
    review, sources = supported(
        source="Máy có khối lượng không quá 10 kg, có CPU, bàn phím và màn hình.",
        quote="Máy có CPU, bàn phím và màn hình.",
        source_quote="có CPU, bàn phím và màn hình",
    )
    assert quantitative_grounding_errors(review, sources, {"S1"})


def test_only_user_facts_referenced_by_the_condition_can_prove_it():
    review, sources = supported(quote="Máy có CPU, bàn phím và màn hình.")
    review["product_facts"].append({"fact": "Khối lượng", "user_quote": "Khối lượng 2 kg."})
    assert quantitative_grounding_errors(review, sources, {"S1"})
    review["condition_checks"][0]["product_fact_indices"] = [1]
    assert not quantitative_grounding_errors(review, sources, {"S1"})


@pytest.mark.parametrize(
    "source,quote,valid",
    [
        ("Mass <=10kg", "Mass 2kg", True),
        ("Khối lượng≤10kg", "Khối lượng 2kg", True),
        ("Khối lượng không quá10kg", "Khối lượng 2kg", True),
        ("Mass less than 10 kg", "Mass 10 kg", False),
        ("Mass less than 10 kg", "Mass under 10 kg", True),
        ("Mass less than 10 kg", "Mass at most 10 kg", False),
        ("Mass at least 10 kg", "Mass 10 kg", True),
        ("Mass more than 10 kg", "Mass 10 kg", False),
        ("Mass more than 10 kg", "Mass over 10 kg", True),
        ("Mass exactly 10 kg", "Mass at most 10 kg", False),
        ("Power at most 1 kW", "Power 750 W", True),
        ("Power at least 1 kW", "Power 500 W", False),
        ("Power no more than 10 W", "Power 1000 mW", True),
        ("Power no more than 10 W", "Power 2 MW", False),
        ("Power no more than 10 W", "Power 2 mw", False),
        ("Chiều dài không quá 1 m", "Chiều dài 100 cm", True),
        ("Volume at most 1 L", "Volume 500 mL", True),
        ("Voltage at least 12 V", "Voltage 24 V", True),
        ("Current at most 2 A", "Current 2000 mA", True),
        ("Frequency more than 1 MHz", "Frequency 2 MHz", True),
    ],
)
def test_comparison_direction_strictness_and_unit_conversion(source, quote, valid):
    review, sources = supported(source, quote)
    assert bool(quantitative_grounding_errors(review, sources, {"S1"})) is not valid


def test_each_distinct_physical_condition_needs_its_own_supported_measurement():
    review, sources = supported("Khối lượng không quá 10 kg và công suất không quá 100 W.")
    assert quantitative_grounding_errors(review, sources, {"S1"})
    review["product_facts"][0]["user_quote"] = "Khối lượng 2 kg và công suất 50 W."
    assert not quantitative_grounding_errors(review, sources, {"S1"})


def test_contradictory_referenced_values_cannot_be_hidden_by_one_satisfying_value():
    review, sources = supported(quote="Khối lượng 2 kg và khối lượng 20 kg.")
    assert quantitative_grounding_errors(review, sources, {"S1"})
    review, sources = supported()
    second = copy.deepcopy(review["condition_checks"][0])
    review["product_facts"].append({"user_quote": "Khối lượng 20 kg."})
    second["product_fact_indices"] = [1]
    review["condition_checks"].append(second)
    assert quantitative_grounding_errors(review, sources, {"S1"})


def test_optional_sources_and_non_supported_reviews_are_outside_the_guard():
    review, sources = supported(source="Máy có CPU.", quote="Máy có CPU.")
    sources["S2"] = {"text": "Khối lượng không quá 1 kg."}
    assert not quantitative_grounding_errors(review, sources, {"S1"})
    review["status"] = "MISSING_PRODUCT_INFO"
    assert not quantitative_grounding_errors(review, sources, {"S2"})
    review["status"] = "REQUIRES_REVIEW"
    assert not quantitative_grounding_errors(review, sources, {"S2"})


def test_guard_is_read_only_and_rejects_ambiguous_source_quantities_conservatively():
    review, sources = supported("Khối lượng ít nhất 1.000 kg.", "Khối lượng 2 kg.")
    before = copy.deepcopy((review, sources))
    assert quantitative_grounding_errors(review, sources, {"S1"})
    assert (review, sources) == before


@pytest.mark.parametrize(
    "source,quote",
    [
        ("Khối lượng không quá 10 kg.", "Không phải máy có khối lượng 2 kg."),
        ("Khối lượng không quá 10 kg.", "Khối lượng không bằng 2 kg."),
        ("Chiều dài không quá 1 m.", "Chiều rộng 50 cm."),
        ("Máy có khối lượng không quá 10 kg.", "Khối lượng bao bì 2 kg."),
        ("Công suất động cơ không quá 100 W.", "Công suất đèn 50 W."),
        (
            "- - Khối lượng toàn bộ theo thiết kế (SEN) không quá 5 tấn:",
            "Trọng tải hàng hóa thiết kế 950 kg.",
        ),
        (
            "- - Khối lượng toàn bộ theo thiết kế (SEN) không quá 5 tấn:",
            "Khối lượng bản thân 1800 kg.",
        ),
        (
            "Trọng lượng cất cánh tối đa không quá 250 g.",
            "Khối lượng pin 100 g.",
        ),
    ],
)
def test_negated_or_explicitly_different_measurements_cannot_prove_a_condition(source, quote):
    review, sources = supported(source, quote)
    assert quantitative_grounding_errors(review, sources, {"S1"})


@pytest.mark.parametrize(
    "source,quote",
    [
        ("Máy có khối lượng không quá 10 kg.", "Máy có khối lượng 2 kg."),
        ("Khối lượng không quá 10 kg.", "Máy xử lý dữ liệu tự động có khối lượng 2 kg."),
        ("Công suất động cơ không quá 100 W.", "Động cơ có công suất 50 W."),
        ("Engine power at most 100 W.", "Engine power 50 W."),
        ("Khối lượng không quá 10 kg.", "Khối lượng không quá 2 kg."),
        ("Khối lượng không dưới 1 kg.", "Khối lượng không dưới 2 kg."),
        ("Khối lượng không quá 10 kg.", "Máy A có khối lượng chính xác 10,000 kg."),
        ("Khối lượng trên 10 kg.", "Máy B có khối lượng thực tế 10,100 kg."),
        (
            "- - Khối lượng toàn bộ theo thiết kế (SEN) không quá 5 tấn:",
            "Xe có khối lượng toàn bộ theo thiết kế 3200 kg.",
        ),
        (
            "Trọng lượng cất cánh tối đa không quá 250 g.",
            "Trọng lượng cất cánh tối đa 249 g.",
        ),
    ],
)
def test_consistent_measurement_subject_and_valid_non_negative_bounds_remain_accepted(
    source, quote
):
    review, sources = supported(source, quote)
    assert not quantitative_grounding_errors(review, sources, {"S1"})
