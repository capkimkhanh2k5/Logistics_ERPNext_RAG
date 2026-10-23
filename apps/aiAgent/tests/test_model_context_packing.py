"""Runtime model budgets preserve full evidence and account for the whole request."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from config.model_limits import MODEL_LIMITS
from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.context.builder import compose_query, prepare_context
from rag.llm.providers.budget import ContextBudgetError, request_budget
from rag.prompts.schemas.answer import MODEL_ANSWER_SCHEMA as ANSWER_SCHEMA


def runtime_config(model="gemini-3.5-flash-lite"):
    return SimpleNamespace(
        model=model,
        use_model_token_limits=True,
        max_input_chars=8000,
        max_context_chars=6000,
    )


def source_fixture(text, *, additional_leaf=False):
    heading = {"id": "heading", "code": "1111", "source_text": "Full heading conditions"}
    parent = {"id": "parent", "code": "111111", "source_text": "Full parent conditions"}
    leaf = {"id": "leaf", "code": "11111111", "source_text": text}
    leaves = [leaf]
    if additional_leaf:
        leaves.append({"id": "second", "code": "11111112", "source_text": "Other full wording"})
    graph = GraphContext(
        [heading, parent, *leaves],
        [],
        [
            {"source": "heading", "target": "parent", "relation": "CONTAINS"},
            *[{"source": "parent", "target": row["id"], "relation": "CONTAINS"} for row in leaves],
        ],
    )
    return {"hs_candidates": leaves, "matches": leaves}, graph


def test_production_packing_preserves_full_bundles_beyond_old_character_caps():
    text = "Điều kiện nguồn được giữ nguyên. " * 700
    result, graph = source_fixture(text)
    question = compose_query("Dữ kiện hàng hóa. " * 600, ["Cấu tạo đã xác nhận."], None)
    ctx = prepare_context(question, result, "auto", runtime_config(), graph)
    packing = ctx["packing"]
    assert len(question) > 8000
    assert ctx["question"] == question
    assert packing["input_chars"] > 8000
    assert packing["source_chars"] > 6000
    assert packing["max_input_chars"] is None
    assert packing["max_context_chars"] is None
    assert {source["id"] for source in ctx["sources"]} == {"leaf", "heading", "parent"}
    assert next(source["text"] for source in ctx["sources"] if source["id"] == "leaf") == text
    assert ctx["allowed_hs_codes"] == ["11111111"]
    assert ctx["candidate_evidence"][0]["hierarchy"]["status"] == "VERIFIED"
    assert packing["request_budget"]["fits"]


def test_model_profiles_have_distinct_full_request_limits():
    result, graph = source_fixture("Full source wording")
    gemini = prepare_context("Product facts", result, "auto", runtime_config(), graph)
    gpt = prepare_context(
        "Product facts", result, "auto", runtime_config("gpt-oss-120b-medium"), graph
    )
    gemini_budget, gpt_budget = (
        gemini["packing"]["request_budget"],
        gpt["packing"]["request_budget"],
    )
    assert gemini_budget["input_limit"] == 1_048_576
    assert gpt_budget["input_limit"] == 114_000
    assert gemini_budget["shared_context"] is False
    assert gpt_budget["shared_context"] is True
    assert [row["text"] for row in gemini["sources"]] == [row["text"] for row in gpt["sources"]]


def test_overbudget_candidate_is_omitted_whole_without_reordering_remaining_evidence():
    result, graph = source_fixture("x" * 120000, additional_leaf=True)
    ctx = prepare_context(
        "Product facts", result, "auto", runtime_config("gpt-oss-120b-medium"), graph
    )
    assert "leaf" not in {source["id"] for source in ctx["sources"]}
    assert ctx["allowed_hs_codes"] == ["11111112"]
    assert ctx["packing"]["omitted_candidate_codes"] == ["11111111"]
    assert ctx["omitted_source_ids"] == ["leaf"]
    assert [source["id"] for source in ctx["sources"]] == ["second", "heading", "parent"]
    assert next(source["text"] for source in ctx["sources"] if source["id"] == "second") == (
        "Other full wording"
    )
    assert ctx["candidate_evidence"][0]["hierarchy"]["status"] == "VERIFIED"
    assert ctx["packing"]["request_budget"]["fits"]
    assert ctx["packing"]["request_budget"]["input_tokens"] <= 114_000


def test_large_original_question_fits_gemini_but_reports_gpt_input_overflow():
    question = "Product facts " * 10000
    gemini = prepare_context(question, {}, "qa", runtime_config())
    assert gemini["question"] == question
    with pytest.raises(ContextBudgetError) as raised:
        prepare_context(question, {}, "qa", runtime_config("gpt-oss-120b-medium"))
    assert raised.value.model == "gpt-oss-120b-medium"
    assert raised.value.budget["input_tokens"] > raised.value.budget["input_limit"]
    assert raised.value.budget["fits"] is False


def test_budget_counts_system_schema_and_explicit_utf8_cost():
    ascii_ctx = prepare_context("A" * 20, {}, "qa", runtime_config())
    unicode_ctx = prepare_context("ắ" * 20, {}, "qa", runtime_config())
    budget = unicode_ctx["packing"]["request_budget"]
    assert budget["mode"] == "CONSERVATIVE_UTF8_BOUND"
    # Both the question and its provenance-backed statement retain the original text.
    assert budget["input_tokens"] - ascii_ctx["packing"]["request_budget"]["input_tokens"] == 80
    assert budget == request_budget(unicode_ctx["messages"], ANSWER_SCHEMA, runtime_config().model)
    user_only = request_budget([unicode_ctx["messages"][1]], {}, runtime_config().model)
    assert budget["input_tokens"] > user_only["input_tokens"]
    assert unicode_ctx["packing"]["system_chars"] == len(unicode_ctx["messages"][0]["content"])
    assert unicode_ctx["packing"]["user_chars"] == len(unicode_ctx["messages"][1]["content"])
    assert unicode_ctx["packing"]["schema_chars"] > 0


def test_legacy_character_limits_still_apply_without_runtime_token_flag():
    result, graph = source_fixture("Whole source wording. " * 700)
    config = GroqConfig(keys=("fixture",), max_context_chars=1000)
    ctx = prepare_context("Product facts", result, "auto", config, graph)
    assert ctx["packing"]["max_input_chars"] == 8000
    assert ctx["packing"]["max_context_chars"] == 1000
    assert ctx["packing"]["request_budget"] is None
    assert "leaf" not in {source["id"] for source in ctx["sources"]}
    with pytest.raises(ValueError, match="exceeds"):
        compose_query("x" * 8001, [], 8000)
    assert compose_query("x" * 8001, [], None) == "x" * 8001


def test_empty_base_rejects_overflow_caused_by_system_and_schema(monkeypatch):
    config = runtime_config()
    baseline = prepare_context("Product facts", {}, "qa", config)
    full = request_budget(baseline["messages"], ANSWER_SCHEMA, config.model)
    user_only = request_budget([baseline["messages"][1]], {}, config.model)
    capacity = full["input_tokens"] - 1
    assert user_only["input_tokens"] < capacity
    monkeypatch.setitem(
        MODEL_LIMITS, config.model, replace(MODEL_LIMITS[config.model], input_tokens=capacity)
    )
    with pytest.raises(ContextBudgetError) as raised:
        prepare_context("Product facts", {}, "qa", config)
    assert raised.value.budget["input_tokens"] == full["input_tokens"]
    assert raised.value.budget["input_limit"] == capacity


@pytest.mark.parametrize("question,supplements", [(" ", []), ("Question", [" "])])
def test_unlimited_character_mode_still_rejects_empty_user_facts(question, supplements):
    with pytest.raises(ValueError, match="empty"):
        compose_query(question, supplements, None)
