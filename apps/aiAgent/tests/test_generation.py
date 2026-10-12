"""Generation boundaries, source budgets, and provider recovery without API calls."""

import io
import json
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

from config.settings import GroqConfig, parse_keys
from rag.answering import generate_answer, prepare_context, validate_answer
from rag.groq_client import GroqClient, GroqError
from tests.support.generation_eval import run_evaluation, score_case


def source(sid="a", text="A printed source passage with evidence.", code=None):
    return {"id": sid, "source_text": text, "locator": {"page": 1}, "code": code}


def context(task="qa"):
    row = source(code="85171300")
    result = {"matches": [row], "package": [row], "hs_candidates": [row]}
    return prepare_context("A question", result, task, GroqConfig(keys=("secret",)))


def answer():
    return {
        "status": "ANSWERED",
        "answer": "A supported conclusion [S1].",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [{"label": "S1", "quote": "printed source passage"}],
        "missing_information": [],
    }


def test_key_formats_are_deduplicated_and_never_represented():
    assert parse_keys("a, b;a\nc") == ("a", "b", "c")
    assert parse_keys('["a", "b", "a"]') == ("a", "b")
    assert "private-key" not in repr(GroqConfig(keys=("private-key",)))


def test_context_drops_whole_sources_and_reports_omissions():
    cfg = GroqConfig(keys=("x",), max_context_chars=700)
    rows = [source(), source("long", "x" * 1000)]
    ctx = prepare_context("Question", {"matches": rows}, "qa", cfg)
    assert [s["id"] for s in ctx["sources"]] == ["a"]
    assert ctx["omitted_source_ids"] == ["long"]
    assert ctx["sources"][0]["text"] == rows[0]["source_text"]


def test_total_user_message_budget_is_enforced_even_with_large_source_budget():
    cfg = GroqConfig(keys=("x",), max_input_chars=1000, max_context_chars=10000)
    rows = [source(), source("long", "x" * 2000)]
    ctx = prepare_context("Question", {"matches": rows}, "qa", cfg)
    assert len(ctx["messages"][1]["content"]) <= 1000
    assert ctx["omitted_source_ids"] == ["long"]
    assert ctx["sources"][0]["text"] == rows[0]["source_text"]


def test_full_provenance_is_preserved_without_filling_the_llm_context():
    row = source()
    row["locator"] = {
        "document": "Tariff.pdf",
        "physical_page": 18,
        "source": {"printed_page": 654},
        "audit": {"history": "x" * 10000},
    }
    ctx = prepare_context("Question", {"matches": [row]}, "qa", GroqConfig(keys=("x",)))
    assert ctx["sources"][0]["locator"] == {
        "document": "Tariff.pdf",
        "physical_page": 18,
        "printed_page": 654,
    }
    assert ctx["source_locators"]["S1"] == row["locator"]
    assert "history" not in ctx["messages"][1]["content"]


def test_hs_candidate_keeps_its_printed_parent_and_explicit_evidence_relationship():
    candidate = source("leaf", "Other", "71171990")
    parent = source("heading", "Imitation jewellery")
    graph = SimpleNamespace(
        records={"leaf": candidate, "heading": parent},
        source_view=lambda _: {"ancestor_ids": ["heading"], "context_ids": [], "note_ids": []},
        citation=lambda sid: {"text": parent["source_text"], "locator": parent["locator"]},
    )
    ctx = prepare_context(
        "Product", {"hs_candidates": [candidate]}, "hs", GroqConfig(keys=("x",)), graph
    )
    assert ctx["sources"][0]["text"] == "Other"
    assert ctx["sources"][1]["text"] == "Imitation jewellery"
    assert ctx["candidate_evidence"][0]["wording_label"] == "S1"
    assert ctx["candidate_evidence"][0]["ancestor_labels"] == ["S2"]


def test_sixth_hs_candidate_is_not_arbitrarily_dropped():
    rows = [source(str(i), "Candidate wording", f"{i:08d}") for i in range(1, 11)]
    ctx = prepare_context("Product", {"hs_candidates": rows}, "hs", GroqConfig(keys=("x",)))
    assert ctx["allowed_hs_codes"] == [r["code"] for r in rows]
    assert ctx["retrieved_hs_codes"] == ctx["allowed_hs_codes"]
    generated = {
        "answer": {**answer(), "suggested_hs_code": "00000006"},
        "validation": {"valid": True, "cited_source_ids": []},
    }
    metrics = score_case({"task": "hs", "expected_hs_8": "00000006"}, ctx, generated)
    assert metrics["gold_hs_in_retrieval_shortlist"]
    assert metrics["gold_hs_retrieval_rank"] == 6
    assert metrics["gold_hs_in_context_candidates"]
    assert metrics["hs_code_exact_match"]


def test_oversized_question_is_rejected_without_truncating_it():
    with pytest.raises(ValueError, match="exceeds GROQ_MAX_INPUT_CHARS"):
        prepare_context("x" * 101, {}, "qa", GroqConfig(keys=("x",), max_input_chars=100))


def test_qa_source_coverage_is_not_reported_as_answer_correctness():
    ctx = context()
    generated = {"answer": answer(), "validation": validate_answer(answer(), ctx)}
    result = score_case({"task": "qa", "canonical_groups": [{"any_of": ["a"]}]}, ctx, generated)
    assert result["cited_primary_group_recall"] == 1
    assert result["answer_correctness"] is None
    assert result["semantic_faithfulness"] is None


def test_cached_evaluation_does_not_require_lazy_retrieval_state(monkeypatch, tmp_path):
    retriever = SimpleNamespace(snapshot="snapshot", profile="profile", unified_policy={})
    monkeypatch.setattr("tests.support.generation_eval.load_generation_graph", lambda _: None)
    monkeypatch.setattr(
        "tests.support.generation_eval.retrieval_for", lambda *a: ({"matches": [source()]}, True)
    )
    client = SimpleNamespace(
        config=GroqConfig(keys=("x",)),
        complete=lambda *a, **k: {
            "content": json.dumps(answer()),
            "finish_reason": "stop",
            "model": "test-model",
        },
    )
    case = {
        "uid": "qa:cached",
        "task": "qa",
        "query": "Question",
        "canonical_groups": [{"any_of": ["a"]}],
    }
    report = run_evaluation(
        [case], retriever, client, ["test-model"], tmp_path, progress=lambda _: None
    )
    assert report["complete"]
    assert report["rows"][0]["run_status"] == "OK"
    assert report["rows"][0]["retrieval_cache_hit"]
    assert report["rows"][0]["metrics"]["cited_primary_group_recall"] == 1


def test_hs_candidate_outside_mixed_top10_gets_its_own_evidence():
    candidate = source("leaf", "The actual candidate wording.", "85171300")
    graph = SimpleNamespace(
        records={"note": source("note", "A binding note.")},
        source_view=lambda _: {"ancestor_ids": [], "context_ids": [], "note_ids": ["note"]},
        citation=lambda sid: {"text": "A binding note.", "locator": {"page": 2}},
    )
    ctx = prepare_context(
        "Product",
        {"matches": [source()], "hs_candidates": [candidate]},
        "hs",
        GroqConfig(keys=("x",)),
        graph,
    )
    assert {s["id"] for s in ctx["sources"]} == {"a", "leaf", "note"}
    assert ctx["allowed_hs_codes"] == ["85171300"]


@pytest.mark.parametrize(
    "change",
    [
        {"citations": [{"label": "S99", "quote": "printed source passage"}]},
        {"citations": [{"label": "S1", "quote": "fabricated legal wording"}]},
        {"answer": "An unsupported conclusion."},
        {"suggested_hs_code": "85171300"},
        {"status": "NEED_MORE_INFORMATION"},
    ],
)
def test_invalid_citations_codes_and_abstention_are_rejected(change):
    assert not validate_answer({**answer(), **change}, context())["valid"]


def test_valid_quote_is_structural_evidence_not_a_faithfulness_score():
    result = validate_answer(answer(), context())
    assert result["valid"]
    assert result["cited_source_ids"] == ["a"]
    assert result["semantic_grounding"] == "NOT_EVALUATED"


def test_hs_code_must_be_in_context_and_recommendation_status():
    proposal = {**answer(), "status": "RECOMMENDATION", "suggested_hs_code": "85171300"}
    assert validate_answer(proposal, context("hs"))["valid"]
    assert not validate_answer({**proposal, "suggested_hs_code": "99999999"}, context("hs"))[
        "valid"
    ]


def test_auto_keeps_legal_sources_and_hs_hierarchy_despite_qa_advice():
    legal = source("legal", "Legal procedure evidence")
    leaf = source("leaf", "Other jewellery", "71131990")
    parent = source("parent", "Of precious metals other than silver")
    records = {row["id"]: row for row in (legal, leaf, parent)}
    graph = SimpleNamespace(
        records=records,
        source_view=lambda _: {"ancestor_ids": ["parent"], "context_ids": [], "note_ids": []},
        citation=lambda sid: {
            "text": records[sid]["source_text"],
            "locator": records[sid]["locator"],
        },
    )
    ctx = prepare_context(
        "A question combining classification and procedure",
        {
            "matches": [legal],
            "hs_candidates": [leaf],
            "semantic_intent": {"intent": "qa", "status": "ADVISORY"},
        },
        "auto",
        GroqConfig(keys=("x",)),
        graph,
    )
    assert ctx["sources"][0]["id"] == "legal"
    assert {row["id"] for row in ctx["sources"]} == {"legal", "leaf", "parent"}
    assert ctx["allowed_hs_codes"] == ["71131990"]
    assert ctx["candidate_evidence"][0]["ancestor_labels"] == ["S3"]
    payload = json.loads(ctx["messages"][1]["content"])
    assert payload["task"] == "auto"
    assert payload["intent_advice"]["intent"] == "qa"


def test_auto_accepts_both_answer_types_but_keeps_code_and_citation_checks():
    ctx = context("auto")
    assert validate_answer(answer(), ctx)["valid"]
    proposal = {**answer(), "status": "RECOMMENDATION", "suggested_hs_code": "85171300"}
    assert validate_answer(proposal, ctx)["valid"]
    assert not validate_answer({**proposal, "suggested_hs_code": "99999999"}, ctx)["valid"]
    assert not validate_answer({**answer(), "alternatives": ["85171300"]}, ctx)["valid"]
    assert not validate_answer(
        {**answer(), "citations": [{"label": "S1", "quote": "Invented"}]}, ctx
    )["valid"]


def test_empty_context_abstains_without_contacting_provider():
    client = SimpleNamespace(complete=lambda *a, **k: pytest.fail("Unexpected API call"))
    ctx = prepare_context("Question", {}, "qa", GroqConfig(keys=("x",)))
    result = generate_answer(ctx, client)
    assert result["answer"]["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["validation"]["valid"]


def test_truncated_generation_never_passes_validation():
    client = SimpleNamespace(
        complete=lambda *a, **k: {
            "content": json.dumps(answer()),
            "finish_reason": "length",
            "model": "test-model",
        }
    )
    assert not generate_answer(context(), client)["validation"]["valid"]


def test_invalid_citation_format_is_repaired_once_with_same_actual_model():
    calls = []
    first = {**answer(), "answer": "A supported conclusion without an inline marker."}

    def complete(messages, schema, **kwargs):
        calls.append(kwargs)
        return {
            "content": json.dumps(first if len(calls) == 1 else answer()),
            "finish_reason": "stop",
            "model": "actual-fallback",
            "fallback_used": True,
            "failures": [{"http_status": 429}] if len(calls) == 1 else [],
        }

    result = generate_answer(context(), SimpleNamespace(complete=complete))
    assert result["validation"]["valid"]
    assert len(calls) == 2
    assert calls[1] == {"model": "actual-fallback", "allow_fallback": False}
    assert result["generation"]["fallback_used"]
    assert result["generation"]["failures"] == [{"http_status": 429}]


@pytest.mark.parametrize("error_code", ["json_validate_failed", "invalid_request_error"])
def test_only_provider_generated_invalid_json_can_trigger_fallback(monkeypatch, error_code):
    client = GroqClient(GroqConfig(keys=("x",)))
    calls = []

    def request(path, payload=None):
        calls.append(payload["model"])
        if payload["model"] == client.config.model:
            raise GroqError(400, client.config.model, error_code=error_code)
        return {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}, 1

    monkeypatch.setattr(client, "_request", request)
    if error_code == "json_validate_failed":
        result = client.complete([], {})
        assert result["fallback_used"]
        assert result["failures"][0]["error_code"] == error_code
        assert calls == [client.config.model, client.config.fallback_model]
    else:
        with pytest.raises(GroqError):
            client.complete([], {})
        assert calls == [client.config.model]


def response(value):
    return io.BytesIO(json.dumps(value).encode())


def test_requests_rotate_keys_and_disable_invalid_credentials(monkeypatch):
    calls = []

    def send(request, **kwargs):
        calls.append(request.get_header("Authorization"))
        if len(calls) == 1:
            raise HTTPError(request.full_url, 401, "Invalid", {}, None)
        return response({"data": []})

    monkeypatch.setattr("rag.groq_client.urlopen", send)
    client = GroqClient(GroqConfig(keys=("bad", "good")))
    client.models()
    client.models()
    assert calls == ["Bearer bad", "Bearer good", "Bearer good"]


def test_successful_requests_round_robin(monkeypatch):
    calls = []

    def send(request, **kwargs):
        calls.append(request.get_header("Authorization"))
        return response({"data": []})

    monkeypatch.setattr("rag.groq_client.urlopen", send)
    client = GroqClient(GroqConfig(keys=("one", "two")))
    for _ in range(3):
        client.models()
    assert calls == ["Bearer one", "Bearer two", "Bearer one"]


def test_provider_failure_records_only_an_allowlisted_code(monkeypatch):
    def failed(request, **kwargs):
        body = response(
            {
                "error": {
                    "code": "json_validate_failed",
                    "message": "secret-key",
                    "failed_generation": "secret-key",
                }
            }
        )
        raise HTTPError(request.full_url, 400, "Invalid", {}, body)

    monkeypatch.setattr("rag.groq_client.urlopen", failed)
    client = GroqClient(GroqConfig(keys=("secret-key",)))
    with pytest.raises(GroqError) as failure:
        client.models()
    assert failure.value.error_code == "json_validate_failed"
    assert "secret-key" not in str(failure.value)


def test_organization_rate_limit_waits_instead_of_immediately_trying_other_keys(monkeypatch):
    calls = []

    def limited(request, **kwargs):
        calls.append(request)
        raise HTTPError(request.full_url, 429, "Limited", {"retry-after": "120"}, None)

    monkeypatch.setattr("rag.groq_client.urlopen", limited)
    client = GroqClient(GroqConfig(keys=("one", "two"), max_wait_seconds=0))
    with pytest.raises(GroqError) as failure:
        client.models()
    assert failure.value.status == 429
    assert len(calls) == 1
    assert "one" not in str(failure.value)


def test_model_fallback_is_explicit_and_can_be_disabled(monkeypatch):
    client = GroqClient(GroqConfig(keys=("one",)))

    def send(path, payload):
        if payload["model"] == client.config.model:
            raise GroqError(503, payload["model"])
        return {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}, 1

    monkeypatch.setattr(client, "_request", send)
    assert client.complete([], {})["fallback_used"]
    with pytest.raises(GroqError):
        client.complete([], {}, allow_fallback=False)


@pytest.mark.parametrize("model", ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"])
def test_reasoning_parameters_match_the_model_and_keep_json_strict(monkeypatch, model):
    client = GroqClient(GroqConfig(keys=("one",)))

    def send(path, payload):
        assert payload["response_format"]["json_schema"]["strict"]
        if model.startswith("qwen/"):
            assert payload["reasoning_format"] == "hidden"
            assert "include_reasoning" not in payload
        else:
            assert payload["include_reasoning"] is False
            assert "reasoning_format" not in payload
        return {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}, 1

    monkeypatch.setattr(client, "_request", send)
    assert client.complete([], {}, model=model, allow_fallback=False)["model"] == model


def test_completion_preserves_provider_retry_after(monkeypatch):
    client = GroqClient(GroqConfig(keys=("one",)))

    def limited(path, payload):
        raise GroqError(429, payload["model"], retry_after=120)

    monkeypatch.setattr(client, "_request", limited)
    with pytest.raises(GroqError) as failure:
        client.complete([], {}, allow_fallback=False)
    assert failure.value.retry_after == 120
