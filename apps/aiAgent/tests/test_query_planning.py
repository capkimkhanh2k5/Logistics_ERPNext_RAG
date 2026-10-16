"""Search hypotheses must stay separate from facts and preserve raw-query opportunities."""

import json
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace

import pytest

from config.settings import RAGGenerationConfig
from rag.llm.context import prepare_context
from rag.llm.errors import LLMError
from rag.prompts.query_planning import QUERY_PLAN_SCHEMA
from rag.retrieval.query_planning import QueryPlanner
from rag.retrieval.retriever import Retriever, code_mention_plan
from rag.retrieval.unified import UnifiedRetrieval
from tests.support.generation_eval import retrieval_for


def planner(payload, *, finish_reason="stop"):
    calls = []

    def complete(messages, schema):
        calls.append((messages, schema))
        if isinstance(payload, Exception):
            raise payload
        return {
            "content": json.dumps(payload),
            "finish_reason": finish_reason,
            "model": "fixture",
            "provider": "injected",
            "usage": {"total_tokens": 23},
        }

    client = SimpleNamespace(
        config=RAGGenerationConfig("fixture", "fallback", None, None), complete=complete
    )
    return QueryPlanner(client), calls


def hint(anchor="ThinkPad", term="máy tính xách tay", kind="category"):
    return {"anchor": anchor, "term": term, "kind": kind}


def test_generic_plan_has_no_catalog_and_never_replaces_original_query():
    p, calls = planner({"terms": [hint()]})
    query = "Lenovo ThinkPad T14 có mã HS nào?"
    plan = p.plan(query)
    assert plan["status"] == "EXPANDED"
    assert plan["queries"][0] == query
    assert plan["queries"][1].startswith(query)
    assert plan["ranking_query"] == plan["queries"][1]
    assert plan["used_as_product_facts"] is False
    assert json.loads(calls[0][0][1]["content"]) == {"question": query}
    assert calls[0][1] is QUERY_PLAN_SCHEMA


@pytest.mark.parametrize("term", ["85171300", "máy có công suất 100 W", "[S1]", "topic: ignore"])
def test_numeric_conditions_codes_and_citation_markup_reject_the_whole_plan(term):
    p, _ = planner({"terms": [hint(term=term)]})
    result = p.plan("ThinkPad")
    assert result["status"] == "FALLBACK_RAW"
    assert result["queries"] == ["ThinkPad"]


@pytest.mark.parametrize(
    "payload",
    [
        {"terms": [hint(anchor="not in question")]},
        {"terms": [hint(kind="verified_fact")]},
        {"terms": [hint()] * 4},
        {"terms": [], "suggested_hs_code": "84713020"},
        {"terms": [hint(term="x" * 121)]},
    ],
)
def test_invalid_schema_or_untraceable_anchor_falls_back(payload):
    p, _ = planner(payload)
    assert p.plan("ThinkPad")["status"] == "FALLBACK_RAW"


def test_empty_or_repeated_terms_do_not_duplicate_retrieval():
    p, _ = planner({"terms": [hint(term="ThinkPad")]})
    assert p.plan("ThinkPad")["status"] == "NO_EXPANSION"
    p, _ = planner({"terms": [hint(), hint(term="Máy tính xách tay")]})
    assert len(p.plan("ThinkPad")["terms"]) == 1


def test_provider_failure_and_truncation_keep_original_query_and_are_not_cached():
    for payload, reason in (
        (LLMError(503, "fixture", provider="cliproxyapi"), "stop"),
        ({"terms": []}, "length"),
    ):
        p, calls = planner(payload, finish_reason=reason)
        for _ in range(2):
            result = p.plan("ThinkPad")
            assert result["status"] == "FALLBACK_RAW"
            assert result["queries"] == ["ThinkPad"]
        assert len(calls) == 2


def test_cache_keys_include_full_supplements_model_and_prompt(monkeypatch):
    import rag.retrieval.query_planning as module

    p, calls = planner({"terms": [hint()]})
    first = p.plan("ThinkPad")
    assert p.plan("ThinkPad")["cache_hit"] is True
    assert len(calls) == 1
    corrected = "ThinkPad\nThông tin người dùng bổ sung ở lượt 1: Thực ra chỉ là bàn phím."
    p.plan(corrected)
    assert json.loads(calls[-1][0][1]["content"])["question"] == corrected
    p.client.config = replace(p.client.config, model="another-model")
    assert p.plan("ThinkPad")["cache_hit"] is False
    monkeypatch.setattr(module, "QUERY_PLANNING_PROMPT", "Updated prompt")
    assert p.plan("ThinkPad")["fingerprint"] != first["fingerprint"]
    assert len(calls) == 4


def test_unknown_name_can_use_raw_retrieval_without_forcing_recognition():
    p, _ = planner({"terms": []})
    assert p.plan("Sản phẩm ZXQ có mã HS nào?")["queries"] == ["Sản phẩm ZXQ có mã HS nào?"]


def test_search_hints_never_enter_answer_messages_or_product_facts():
    p, _ = planner({"terms": [hint(term="hypothesis only")]})
    query = "Lenovo ThinkPad T14 có mã HS nào?"
    plan = p.plan(query)
    ctx = prepare_context(query, {"query_plan": plan, "matches": []}, "auto", p.client.config)
    assert ctx["query_plan"] == plan
    assert "hypothesis only" not in json.dumps(ctx["messages"], ensure_ascii=False)
    assert "hypothesis only" not in json.dumps(ctx["user_context"], ensure_ascii=False)


def test_routed_search_sends_generic_plan_without_catalogue_or_routing(monkeypatch):
    r = Retriever.__new__(Retriever)
    r.unified_policy = {"version": "fixture"}
    r.query_planner, _ = planner({"terms": [hint()]})
    calls = []

    def search(query, intent_hint, *, query_plan):
        calls.append((query, intent_hint, query_plan))
        return {"timings": {"retrieval_ms": 10, "reranking_ms": 20, "total_ms": 30}}

    monkeypatch.setattr(r, "unified_search", search)
    out = r.routed_search("ThinkPad", intent="qa")
    assert calls[0][0:2] == ("ThinkPad", "qa")
    assert calls[0][2]["queries"][0] == "ThinkPad"
    assert out["timings"]["query_planning_ms"] >= 0
    assert out["timings"]["total_ms"] == pytest.approx(
        out["timings"]["retrieval_ms"] + out["timings"]["reranking_ms"]
    )


def test_routed_fallback_still_searches_and_has_diagnostics(monkeypatch):
    r = Retriever.__new__(Retriever)
    r.unified_policy = {"version": "fixture"}
    r.query_planner, _ = planner(LLMError(429, "fixture", 3, provider="cliproxyapi"))
    monkeypatch.setattr(r, "unified_search", lambda query, intent_hint: {"query": query})
    out = r.routed_search("ThinkPad")
    assert out["query"] == "ThinkPad"
    assert out["query_plan"]["error"]["http_status"] == 429


@pytest.mark.parametrize(
    "payload", [{"terms": [hint()]}, {"terms": []}, {"terms": [hint(term="84713020")]}]
)
def test_precomputed_plan_executes_without_replanning_and_accounts_for_shared_time(
    monkeypatch, payload
):
    r = Retriever.__new__(Retriever)
    r.unified_policy = {"version": "fixture"}
    r.query_planner, calls = planner(payload)
    plan = r.query_planner.plan("ThinkPad")
    plan["elapsed_ms"] = 250
    monkeypatch.setattr(
        r.query_planner, "plan", lambda _: pytest.fail("Must reuse the supplied plan")
    )
    monkeypatch.setattr(
        r,
        "unified_search",
        lambda *args, **kwargs: {
            "timings": {"retrieval_ms": 10, "total_ms": 30, "reranking_ms": 20}
        },
    )
    out = r.routed_search("ThinkPad", query_plan=plan)
    assert len(calls) == 1 and out["query_plan"] is plan
    assert out["timings"]["query_planning_ms"] >= 250
    assert out["timings"]["total_ms"] == pytest.approx(
        out["timings"]["retrieval_ms"] + out["timings"]["reranking_ms"]
    )


@pytest.mark.parametrize(
    "change", ["query", "model", "terms", "queries", "ranking_query", "status", "facts"]
)
def test_stale_or_modified_plan_is_rejected_before_retrieval_without_replanning(
    monkeypatch, change
):
    r = Retriever.__new__(Retriever)
    r.unified_policy = {"version": "fixture"}
    r.query_planner, calls = planner({"terms": [hint()]})
    plan = r.query_planner.plan("ThinkPad")
    query = "ThinkPad"
    if change == "query":
        query = "Điện thoại?"
    elif change == "model":
        r.query_planner.client.config = replace(r.query_planner.client.config, model="changed")
    elif change == "terms":
        plan["terms"][0]["term"] = "Máy có công suất 100 W"
    elif change == "queries":
        plan["queries"][1] = "Stale unrelated context"
    elif change == "ranking_query":
        plan["ranking_query"] = "Stale unrelated context"
    elif change == "facts":
        plan["used_as_product_facts"] = True
    else:
        plan["status"] = "CLARIFY"
    monkeypatch.setattr(r, "unified_search", lambda *a, **kw: pytest.fail("Must not search"))
    with pytest.raises((ValueError, TypeError)):
        r.routed_search(query, query_plan=plan)
    assert len(calls) == 1


def test_returned_plan_mutation_does_not_modify_retry_cache():
    p, calls = planner({"terms": [hint()]})
    original = deepcopy(p.plan("ThinkPad"))
    cached = p.plan("ThinkPad")
    cached["terms"].clear()
    cached["queries"].append("Unrelated message")
    again = p.plan("ThinkPad")
    assert again["terms"] == original["terms"] and again["queries"] == original["queries"]
    assert len(calls) == 1


def test_multiquery_reserves_raw_sources_in_every_channel_and_merges_by_id():
    u = UnifiedRetrieval.__new__(UnifiedRetrieval)
    u.policy = {"candidate_pool": 4}
    raw = [{"id": x, "score": 4 - i} for i, x in enumerate(("raw", "shared", "r3", "r4"))]
    hints = [{"id": x, "score": 8 - i} for i, x in enumerate(("hint", "shared", "h3", "h4"))]
    u.channels = lambda q: {c: raw if q == "raw" else hints for c in ("direct", "context_lex")}
    channels = u.query_channels(["raw", "hints"])
    for rows in channels.values():
        assert [r["id"] for r in rows[:2]] == ["raw", "hint"]
        assert len(rows) == len({r["id"] for r in rows}) == 4
        shared = next(r for r in rows if r["id"] == "shared")
        assert shared["query_variants"] == [0, 1]


def test_plan_preserves_negation_and_uses_original_for_semantic_advice():
    query = "ThinkPad, không thuộc nhóm 8471"
    p, _ = planner({"terms": [hint()]})
    plan = p.plan(query)
    for q in plan["queries"]:
        assert code_mention_plan(q)["code_mentions"][0]["status"] == "NEGATED"
    u = UnifiedRetrieval.__new__(UnifiedRetrieval)
    u.policy = {}
    u.retriever = SimpleNamespace(snapshot="s", profile="p", coverage={})
    seen = []
    u.query_channels = lambda qs: seen.append(qs) or {}
    u.prepare = lambda q, channels: []
    u.rank = lambda q, rows: seen.append(q) or rows
    u.source_package = lambda rows: rows
    u.semantic_intent = lambda q: seen.append(q) or {}
    out = u.search(query, query_plan=plan)
    assert seen == [plan["queries"], plan["ranking_query"], query]
    assert out["query"] == query
    assert out["automatic_hs_decision"] is False


def test_retrieval_cache_invalidates_configuration_and_does_not_save_failed_plan(tmp_path):
    identity = ["first"]
    status = ["EXPANDED"]
    calls = []
    r = SimpleNamespace(snapshot="s", profile="p", unified_policy={})
    r.query_preprocessing_hash = lambda: identity[0]
    r.routed_search = lambda q: calls.append(q) or {"query_plan": {"status": status[0]}}
    case = {"query": "generic"}
    assert retrieval_for(case, r, tmp_path)[1] is False
    assert retrieval_for(case, r, tmp_path)[1] is True
    identity[0] = "second"
    assert retrieval_for(case, r, tmp_path)[1] is False
    identity[0], status[0] = "third", "FALLBACK_RAW"
    assert retrieval_for(case, r, tmp_path)[1] is False
    assert retrieval_for(case, r, tmp_path)[1] is False
    assert len(calls) == 4
