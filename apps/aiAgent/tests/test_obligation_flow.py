"""Behavioral regressions for the approved goal-owned review contract."""

import json
from copy import deepcopy

import pytest

from rag.llm.contracts.errors import ContractIssue
from rag.llm.generation.recovery import recover_answer
from rag.llm.generation.task_generation import TaskRun


class Responses:
    """Only replace the external model boundary; validators run normally."""

    def __init__(self, values):
        self.values = iter(values)

    def complete(self, messages, schema, **kwargs):
        return {
            "content": json.dumps(next(self.values)),
            "finish_reason": "stop",
            "model": "fixture",
        }


@pytest.mark.parametrize("mixed", [False, True])
def test_repair_replaces_current_binding_errors_after_valid_attempt(mixed):
    run = TaskRun(Responses([{"ok": False}, {"ok": True}]), None, False, 5)

    def check(value):
        errors = (
            []
            if value["ok"]
            else [
                ContractIssue("invalid reference", code="CONDITION_REF_INVALID", path="R1/claims/0")
            ]
        )
        if mixed and errors:
            errors.append(ContractIssue("unsupported", code="PROOF_INVALID", path="R1/claims/0"))
        return value, errors

    _, decoded, errors = run.request([], {"type": "object"}, check, "answer")
    assert decoded == {"ok": True}
    assert errors == []
    assert run.calls[0]["validation_errors"]  # audit retains the failed attempt
    assert run.remaining == 3


def test_repair_never_accepts_an_unresolved_reference():
    run = TaskRun(Responses([{}, {}]), None, False, 5)
    _, _, errors = run.request(
        [],
        {"type": "object"},
        lambda _: (
            None,
            [ContractIssue("unknown source", code="UNREGISTERED_EVIDENCE", path="R1")],
        ),
        "answer",
    )
    assert errors
    assert run.remaining >= 3


def recovery_fixture():
    context = {
        "response_protocol": "goals-v1",
        "question": "Quy định nào?",
        "sources": [],
        "request": {
            "objectives": [
                {"id": "G1", "item_ids": [], "anchor": "Quy định"},
                {"id": "G2", "item_ids": [], "anchor": "Quy định"},
            ]
        },
    }
    generated = {
        "validation": {"task_completion": False},
        "diagnostics": {"code": "SYSTEM_VALIDATION_ERROR"},
        "generation": {"remaining_calls": 3, "evidence_gaps": []},
        "answer": {
            "results": [
                {
                    "required": True,
                    "result_id": "R1",
                    "objective_id": "G1",
                    "item_id": "",
                    "kind": "EXPLAIN",
                    "status": "REQUIRES_REVIEW",
                    "failure_kind": "TECHNICAL",
                },
                {
                    "required": True,
                    "result_id": "R2",
                    "objective_id": "G2",
                    "item_id": "",
                    "kind": "EXPLAIN",
                    "status": "INSUFFICIENT_LEGAL_EVIDENCE",
                    "analysis_review_valid": True,
                    "missing_legal_evidence": ["Thiếu quy định."],
                },
            ]
        },
    }
    return context, generated


def test_recovery_keeps_independently_reviewed_legal_gap_with_technical_sibling(monkeypatch):
    context, generated = recovery_fixture()
    monkeypatch.setattr(
        "rag.llm.generation.recovery.recover_evidence",
        lambda *args: (None, {"rounds": 1, "reason": "NO_NEW_SOURCES"}),
    )
    _, got = recover_answer(context, generated, {}, None, None, None)
    assert got["generation"]["recovery"] == {"rounds": 1, "reason": "NO_NEW_SOURCES"}
    assert got["answer"]["results"][0]["status"] == "REQUIRES_REVIEW"


def test_recovery_does_not_turn_technical_failure_into_legal_gap():
    context, generated = recovery_fixture()
    generated["answer"]["results"] = generated["answer"]["results"][:1]
    generated["generation"]["evidence_gaps"] = [
        {"anchor": "Quy định", "codes": [], "reason": "raw"}
    ]
    _, got = recover_answer(context, deepcopy(generated), {}, None, None, None)
    assert "recovery" not in got["generation"]


def test_goal_draft_schema_does_not_require_formal_graph_or_ledger():
    from rag.llm.validation.answer import schema_errors
    from rag.prompts.generation.task_answering import task_answer_schema
    from tests.test_goal_workflow import context, model_answer

    ctx = context()
    schema = task_answer_schema(ctx["request"], ["7113", "7117"])
    assert not schema_errors(model_answer(ctx), schema)
    assert "proof_catalogue" not in schema["properties"]
    assert "fact_ledger" not in schema["properties"]
    assert (
        "proof_key"
        not in schema["properties"]["results"]["items"]["properties"]["claims"]["items"][
            "properties"
        ]
    )


def test_goal_context_separates_semantic_review_from_legacy_proof():
    from rag.llm.context.normalization import normalize_context
    from tests.test_goal_workflow import context

    ctx = normalize_context(context())
    assert ctx["reasoning_contract"] == "semantic-v1"
    assert ctx["proof_required"] is False


@pytest.mark.parametrize(
    "text",
    [
        "Thiết bị này có đáp ứng điều kiện không?",
        "Giả sử máy nặng 8 kg",
        "Hãy tìm quy định về máy này",
    ],
)
def test_question_hypothesis_and_instruction_are_not_product_assertions(text):
    from rag.llm.evidence.evidence import bind_user_context
    from rag.llm.evidence.proof_contract import product_fact_ids

    assert product_fact_ids(bind_user_context(text)) == []


@pytest.mark.parametrize("first_review_wrong", [False, True])
def test_envelope_valid_draft_reaches_semantic_review_before_publication(first_review_wrong):
    from rag.llm.generation.answering import generate_answer
    from tests.test_goal_workflow import context

    ctx = context()
    ctx["request"] = {
        "items": [],
        "objectives": [
            {
                "id": "G1",
                "kind": "EXPLAIN",
                "level": 0,
                "item_ids": [],
                "anchor": "giải thích",
                "required": True,
            }
        ],
    }
    eid = ctx["sources"][0]["evidence_id"]
    draft = {
        "results": [
            {
                "objective_id": "G1",
                "item_id": "",
                "status": "ANSWERED",
                "code": "",
                "claims": [
                    {
                        "kind": "LEGAL_ANALYSIS",
                        "text": ctx["sources"][0]["text"],
                        "evidence_ids": [eid],
                        "fact_ids": [],
                    }
                ],
                "clarifications": [],
                "missing_legal_evidence": [],
            }
        ],
        "evidence_gaps": [],
    }
    review = {
        "reviews": [],
        "analysis_reviews": {
            "R1": {
                "checks": {
                    "0": {
                        "assessment": "REFERENCE",
                        "evidence_ids": [eid],
                        "fact_ids": [],
                        "reason": "Nguồn mô tả quy định.",
                        "application_level": 0,
                    }
                },
                "coverage_checks": {},
            }
        },
    }
    responses = [draft, review]
    if first_review_wrong:
        bad = deepcopy(review)
        bad["analysis_reviews"]["R1"]["checks"]["0"]["assessment"] = "APPLICATION"
        responses.insert(1, bad)
    client = Responses(responses)
    got = generate_answer(ctx, client)
    assert got["validation"]["task_completion"] is True
    assert got["answer"]["results"][0]["analysis_review_valid"] is True
    assert len(got["generation"]["attempts"]) == (3 if first_review_wrong else 2)


def test_compare_cannot_publish_application_while_separate_item_classifications_are_blocked():
    from rag.llm.generation.task_generation import _resolve_comparisons

    goals = [
        {
            "id": "G1",
            "kind": "COMPARE",
            "level": 6,
            "item_ids": ["I1", "I2"],
            "anchor": "Cả hai có cùng phân nhóm không?",
        },
        {"id": "G2", "kind": "CLASSIFY", "level": 6, "item_ids": ["I1"]},
        {"id": "G3", "kind": "CLASSIFY", "level": 6, "item_ids": ["I2"]},
    ]
    rows = [
        {
            "result_id": "R1",
            "objective_id": "G1",
            "item_id": "",
            "kind": "COMPARE",
            "level": 6,
            "status": "ANSWERED",
            "valid": True,
            "required": True,
            "depends_on": [],
            "answer": "Máy A thuộc phân nhóm 8471.30.",
            "claims": [],
            "citations": [],
            "analysis_review_valid": True,
            "analysis_checks": [{"claim_index": 0, "assessment": "APPLICATION"}],
        }
    ]
    got = _resolve_comparisons(rows, {"request": {"objectives": goals}})
    assert got[0]["status"] == "REQUIRES_REVIEW"
    assert "thuộc phân nhóm" not in got[0]["answer"]


@pytest.mark.parametrize("problem", ["question", "expired", "wrong_item"])
def test_analysis_application_rejects_invalid_support(problem):
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from tests.test_goal_workflow import context

    ctx = context(explain=True)
    ctx["proof_required"] = False
    goal = ctx["request"]["objectives"][-1]
    goal["item_ids"] = ["I1"]
    fact = next(s for s in ctx["user_context"]["statements"] if s["text"] == "Dây A bằng bạc 925")
    eid = ctx["sources"][0]["evidence_id"]
    if problem == "question":
        fact["text"] = "Dây A có bằng bạc không?"
    elif problem == "expired":
        ctx["sources"][0].update(legal_status="EXPIRED", effective_to="2025-12-31")
    else:
        fact = next(
            s for s in ctx["user_context"]["statements"] if s["text"] == "Dây B bằng thép mạ vàng"
        )
    rows = [
        {
            "result_id": "R1",
            "objective_id": goal["id"],
            "item_id": "",
            "kind": "EXPLAIN",
            "status": "ANSWERED",
            "valid": True,
            "claims": [
                {
                    "kind": "LEGAL_ANALYSIS",
                    "text": "Hàng hóa này thuộc nhóm theo vật liệu.",
                    "evidence_ids": [eid],
                    "fact_ids": [fact["id"]],
                }
            ],
        }
    ]
    review = [
        {
            "result_id": "R1",
            "checks": [
                {
                    "claim_index": 0,
                    "assessment": "APPLICATION",
                    "evidence_ids": [eid],
                    "fact_ids": [fact["id"]],
                    "user_quotes": [fact["text"]],
                    "reason": "Áp dụng.",
                    "application_level": 4,
                }
            ],
        }
    ]
    checked, errors = check_analyses(review, analysis_jobs(rows, ctx), rows, ctx)
    assert errors
    assert "R1" not in checked


def test_classification_draft_facts_also_need_independent_claim_review():
    from rag.llm.review.analysis_review import analysis_jobs
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer

    ctx = context()
    rows, errors = decode_task_answer(model_answer(ctx), ctx)
    assert not errors
    assert len(analysis_jobs(rows, ctx)) == 2


def test_application_cannot_claim_supported_numeric_threshold_without_qualifying_measurement():
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from tests.test_goal_workflow import context

    ctx = context(explain=True)
    ctx["proof_required"] = False
    ctx["request"]["objectives"][-1]["item_ids"] = ["I1"]
    source = ctx["sources"][0]
    source["text"] = "Máy có khối lượng không quá 10 kg."
    fact = ctx["user_context"]["statements"][0]
    fact["text"] = "Dây A có khối lượng 12 kg"
    claim = {
        "kind": "LEGAL_ANALYSIS",
        "text": "Mặt hàng này đáp ứng giới hạn khối lượng.",
        "evidence_ids": [source["evidence_id"]],
        "fact_ids": [fact["id"]],
    }
    rows = [
        {
            "result_id": "R1",
            "objective_id": "G2",
            "item_id": "",
            "kind": "EXPLAIN",
            "status": "ANSWERED",
            "valid": True,
            "claims": [claim],
        }
    ]
    review = [
        {
            "result_id": "R1",
            "checks": [
                {
                    "claim_index": 0,
                    "assessment": "APPLICATION",
                    "evidence_ids": [source["evidence_id"]],
                    "fact_ids": [fact["id"]],
                    "user_quotes": [fact["text"]],
                    "reason": "Đạt.",
                }
            ],
        }
    ]
    checked, errors = check_analyses(review, analysis_jobs(rows, ctx), rows, ctx)
    assert errors
    assert "R1" not in checked


def test_draft_packet_preserves_all_rivals_and_sources_without_repeating_full_hierarchies():
    from rag.llm.contracts import obligations

    payload = {
        "request": {"objectives": []},
        "sources": [{"evidence_id": "E1", "text": "Nguồn nguyên văn."}],
        "comparison_candidates": [
            {
                "code": "12345678",
                "hierarchy": {"status": "VERIFIED", "chain": ["large"]},
                "required_citation_evidence_ids": ["E1"],
                "context": "duplicated",
            }
        ],
    }
    packet = obligations.draft_packet(payload)
    assert packet["sources"] == payload["sources"]
    assert packet["comparison_candidates"][0]["code"] == "12345678"
    assert packet["comparison_candidates"][0]["required_citation_evidence_ids"] == ["E1"]
    assert "chain" not in packet["comparison_candidates"][0]["hierarchy"]
    assert payload["comparison_candidates"][0]["hierarchy"]["chain"] == ["large"]


def test_draft_packet_accepts_existing_flat_comparison_wire():
    from rag.llm.contracts.obligations import draft_packet

    payload = {
        "request": {},
        "comparison_candidates": [
            {
                "code": "12345678",
                "hierarchy_status": "VERIFIED",
                "wording_evidence_id": "E1",
                "context_evidence_ids": ["E2"],
                "required_citation_evidence_ids": ["E1", "E2"],
            }
        ],
    }
    got = draft_packet(payload)
    assert got["comparison_candidates"][0]["hierarchy_status"] == "VERIFIED"
    assert got["comparison_candidates"][0]["wording_evidence_id"] == "E1"
    assert got["comparison_candidates"][0]["required_citation_evidence_ids"] == ["E1", "E2"]


def test_semantic_condition_slots_include_mandatory_wording_and_note_scope():
    from rag.llm.generation.task_generation import review_jobs
    from rag.llm.review.review_packet import review_packet
    from rag.llm.validation.task_validation import decode_task_answer
    from rag.prompts.generation.task_answering import TASK_REVIEW_SCHEMA
    from tests.test_goal_workflow import context, model_answer

    ctx = context()
    rows, _ = decode_task_answer(model_answer(ctx), ctx)
    jobs, _ = review_jobs(rows, ctx)
    note = ctx["sources"][-1]["evidence_id"]
    jobs[0]["note_scope_evidence_ids"] = [note]
    packet, wire, _ = review_packet(
        {
            "jobs": jobs,
            "analysis_jobs": [],
            "user_context": ctx["user_context"],
            "sources": ctx["sources"],
            "reasoning_contract": "semantic-v1",
        },
        TASK_REVIEW_SCHEMA,
    )
    conditions = wire["properties"]["reviews"]["properties"]["R1"]["properties"]["review"][
        "properties"
    ]["condition_checks"]
    assert conditions["type"] == "array"
    required = conditions["items"]["properties"]["evidence_id"]["enum"]
    assert note in required
    assert conditions["minItems"] == conditions["maxItems"] == len(required)
    assert packet["review_slots"]["condition_checks"]["R1"] == required


def test_reviewer_reason_cannot_publish_a_new_unreviewed_classification():
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer, model_reviews

    ctx = context(explain=True)
    draft = model_answer(ctx)
    rows, _ = decode_task_answer(draft, ctx)
    reviews = model_reviews(ctx, draft)["analysis_reviews"]
    check = next(r for r in reviews if r["result_id"] == "R3")["checks"][0]
    check.update(
        assessment="INSUFFICIENT_LEGAL_EVIDENCE",
        reason="Chắc chắn áp mã 99999999 E12345678901234567890.",
    )
    checked, errors = check_analyses(reviews, analysis_jobs(rows, ctx), rows, ctx)
    assert not errors
    assert "99999999" not in checked["R3"]["answer"]
    assert "E12345678901234567890" not in " ".join(checked["R3"]["missing_legal_evidence"])


def test_unverified_metadata_is_never_a_current_certificate_but_can_describe_source_snapshot():
    from rag.llm.contracts.obligations import temporal_errors

    ctx = {
        "sources": [{"evidence_id": "E1", "legal_status": "UNVERIFIED"}],
        "legal_scope": "SOURCE_SNAPSHOT",
    }
    assert temporal_errors(["E1"], ctx) == []
    ctx["legal_scope"] = "CURRENT_APPLICABILITY"
    assert temporal_errors(["E1"], ctx)


def test_source_snapshot_recommendation_discloses_unverified_current_applicability():
    from tests.test_goal_workflow import context, model_answer, model_reviews, run

    ctx = context()
    draft = model_answer(ctx)
    got, _ = run(ctx, [draft, model_reviews(ctx, draft)])
    assert got["validation"]["task_completion"]
    assert got["validation"]["legal_scope"] == "SOURCE_SNAPSHOT"
    assert got["validation"]["current_applicability_verified"] is False
    assert "hiệu lực hiện hành" in got["answer"]["answer"]


def test_classification_analysis_is_scoped_to_its_own_row_item():
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer, model_reviews

    ctx = context()
    draft = model_answer(ctx)
    rows, _ = decode_task_answer(draft, ctx)
    jobs = analysis_jobs(rows, ctx)
    assert {j["result_id"]: j["item_ids"] for j in jobs} == {"R1": ["I1"], "R2": ["I2"]}
    review = model_reviews(ctx, draft)["analysis_reviews"]
    wrong = next(
        s for s in ctx["user_context"]["statements"] if s["text"] == "Dây B bằng thép mạ vàng"
    )
    review[0]["checks"][0].update(fact_ids=[wrong["id"]], user_quotes=[wrong["text"]])
    checked, errors = check_analyses(review, jobs, rows, ctx)
    assert "R1" not in checked and errors


def test_classification_reviewer_reason_cannot_add_unreviewed_facts():
    from tests.test_goal_workflow import context, model_answer, model_reviews, run

    ctx = context()
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    for r in review["reviews"]:
        r["review"]["reason"] = (
            "Sản phẩm có trọng lượng 999 kg và nhà sản xuất đã được cấp giấy chứng nhận."
        )
    got, _ = run(ctx, [draft, review])
    assert got["validation"]["task_completion"]
    assert "999 kg" not in got["answer"]["answer"]
    assert "đã được cấp giấy" not in got["answer"]["answer"]


def test_expired_source_needs_verified_historical_interval_even_with_as_of():
    from rag.llm.contracts.obligations import temporal_errors

    ctx = {
        "sources": [{"evidence_id": "E1", "legal_status": "EXPIRED"}],
        "legal_scope": "CURRENT_APPLICABILITY",
        "as_of": "2026-10-22",
    }
    assert temporal_errors(["E1"], ctx)
    ctx["sources"][0].update(effective_from="2024-01-01", effective_to="2024-12-31")
    assert temporal_errors(["E1"], ctx)
    ctx["as_of"] = "2024-06-01"
    assert temporal_errors(["E1"], ctx) == []


def test_explicit_current_request_cannot_default_to_snapshot_advice():
    from config.settings import GroqConfig
    from rag.llm.context.builder import prepare_context
    from rag.utils.files import digest

    q = "Quy định hiện hành về hồ sơ là gì?"
    request = {
        "items": [],
        "objectives": [
            {
                "id": "G1",
                "kind": "EXPLAIN",
                "level": 0,
                "item_ids": [],
                "anchor": q,
                "required": True,
            }
        ],
    }
    ctx = prepare_context(
        q,
        {
            "matches": [{"id": "r", "source_text": "Hồ sơ gồm tài liệu kỹ thuật."}],
            "query_plan": {"request": request, "query_hash": digest(q)},
        },
        "auto",
        GroqConfig(keys=("fixture",)),
    )
    assert ctx["legal_scope"] == "CURRENT_APPLICABILITY"


@pytest.mark.parametrize("claims_current", [False, True])
def test_snapshot_application_explanation_is_qualified_and_cannot_claim_current_law(claims_current):
    from tests.test_goal_workflow import context, run

    ctx = context(explain=True)
    ctx["request"]["objectives"] = [ctx["request"]["objectives"][-1]]
    ctx["request"]["objectives"][0]["item_ids"] = ["I1"]
    source = ctx["sources"][0]
    source["legal_status"] = "UNVERIFIED"
    fact = next(s for s in ctx["user_context"]["statements"] if s["text"] == "Dây A bằng bạc 925")
    text = (
        "Hàng hóa này đáp ứng điều kiện theo nguồn."
        if not claims_current
        else "Hàng hóa này đáp ứng điều kiện theo quy định hiện hành."
    )
    draft = {
        "results": [
            {
                "objective_id": "G2",
                "item_id": "",
                "status": "ANSWERED",
                "code": "",
                "claims": [
                    {
                        "kind": "LEGAL_ANALYSIS",
                        "text": text,
                        "evidence_ids": [source["evidence_id"]],
                        "fact_ids": [fact["id"]],
                    }
                ],
                "clarifications": [],
                "missing_legal_evidence": [],
            }
        ],
        "evidence_gaps": [],
    }
    review = {
        "reviews": [],
        "analysis_reviews": [
            {
                "result_id": "R1",
                "checks": [
                    {
                        "claim_index": 0,
                        "assessment": "APPLICATION",
                        "evidence_ids": [source["evidence_id"]],
                        "fact_ids": [fact["id"]],
                        "reason": "Đối chiếu.",
                        "user_quotes": [fact["text"]],
                    }
                ],
            }
        ],
    }
    got, _ = run(ctx, [draft, review])
    if claims_current:
        assert got["answer"]["status"] != "ANSWERED"
        assert text not in got["answer"]["answer"]
    else:
        assert got["answer"]["status"] == "ANSWERED"
        assert "chưa xác minh hiệu lực hiện hành" in got["answer"]["answer"]


def test_recovery_preserves_strict_temporal_scope_before_regeneration(monkeypatch):
    from types import SimpleNamespace

    context, generated = recovery_fixture()
    context.update(as_of="2026-10-22", legal_scope="CURRENT_APPLICABILITY")
    generated["diagnostics"] = {}
    generated["answer"]["results"] = generated["answer"]["results"][1:]
    monkeypatch.setattr("rag.llm.generation.recovery.recover_evidence", lambda *args: ({}, {}))
    monkeypatch.setattr(
        "rag.llm.context.builder.prepare_context",
        lambda *args: {
            **{k: v for k, v in context.items() if k not in {"as_of", "legal_scope"}},
            "legal_scope": "SOURCE_SNAPSHOT",
        },
    )

    class ReachedRegeneration(Exception):
        pass

    def regenerate(updated, *args, **kwargs):
        assert updated.get("as_of") == "2026-10-22"
        assert updated.get("legal_scope") == "CURRENT_APPLICABILITY"
        raise ReachedRegeneration

    monkeypatch.setattr("rag.llm.generation.task_generation.generate_task_answer", regenerate)
    with pytest.raises(ReachedRegeneration):
        recover_answer(context, generated, {}, SimpleNamespace(config=None), None, None)


def test_two_items_parent_and_leaf_reviews_fit_shared_budget(monkeypatch):
    from types import SimpleNamespace

    from config.settings import GroqConfig
    from rag.graph.context import GraphContext
    from rag.llm.context.builder import prepare_context
    from rag.llm.generation.task_generation import review_by_level
    from rag.llm.validation.task_validation import decode_task_answer
    from rag.utils.files import digest
    from tests.test_goal_workflow import context, model_answer

    base = context(explain=True)
    req = deepcopy(base["request"])
    req["objectives"][0]["level"] = 6
    records = [
        {"id": s["id"], "code": s["code"], "level": len(s["code"]), "source_text": s["text"]}
        for s in base["sources"]
        if s.get("code")
    ]
    graph = GraphContext(
        records,
        [],
        [
            {"source": a, "target": b, "relation": "CONTAINS"}
            for a, b in [("a4", "a6"), ("a6", "a8"), ("b4", "b6"), ("b6", "b8")]
        ],
    )
    ctx = prepare_context(
        base["question"],
        {
            "matches": records,
            "hs_candidates": [r for r in records if r["level"] == 6],
            "query_plan": {"request": req, "query_hash": digest(base["question"])},
        },
        "auto",
        GroqConfig(keys=("fixture",)),
        graph,
    )
    draft = model_answer(ctx)
    for r, code in zip(draft["results"][:2], ["711311", "711719"]):
        r["code"] = code
        r["claims"][0]["evidence_ids"] = [
            s["evidence_id"] for s in ctx["sources"] if s.get("code") in {code[:4], code}
        ]
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    budget = SimpleNamespace(remaining=4)  # One draft already consumed from the shared five.

    def reviewed(batch, scoped, run):
        enough = run.remaining > 0
        run.remaining -= int(enough)
        return [
            {**r, "review_valid": enough, "status": r["status"] if enough else "REQUIRES_REVIEW"}
            for r in batch
        ], {
            "valid": enough,
            "errors": [] if enough else ["budget"],
            "checked_results": [r["result_id"] for r in batch],
        }

    monkeypatch.setattr("rag.llm.generation.task_generation.review_results", reviewed)
    got, report = review_by_level(rows, ctx, budget)
    assert all(r["status"] in {"RECOMMENDATION", "ANSWERED"} for r in got)
    assert report["valid"]
    assert budget.remaining >= 1


def test_strict_current_scope_checks_temporal_evidence_even_for_rule_reference():
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer, model_reviews

    ctx = context(explain=True)
    ctx["legal_scope"] = "CURRENT_APPLICABILITY"
    for source in ctx["sources"]:
        source["legal_status"] = "UNVERIFIED"
    draft = model_answer(ctx)
    rows, _ = decode_task_answer(draft, ctx)
    jobs = [j for j in analysis_jobs(rows, ctx) if j["result_id"] == "R3"]
    reviews = [r for r in model_reviews(ctx, draft)["analysis_reviews"] if r["result_id"] == "R3"]
    checked, errors = check_analyses(reviews, jobs, rows, ctx)
    assert "R3" not in checked and errors


def test_draft_intermediate_code_and_missing_parent_citation_reach_review():
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer

    ctx = context(explain=True)
    draft = model_answer(ctx)
    draft["results"][2]["claims"][0]["text"] = "Dây A được phân loại vào nhóm 7113."
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    assert all(r["valid"] for r in rows)


def test_multi_item_numeric_claim_needs_item_specific_predicate_support():
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer, model_reviews

    ctx = context(explain=True)
    draft = model_answer(ctx)
    draft["results"][2]["claims"][0]["text"] = "Máy A đáp ứng ngưỡng 10 kg, máy B vượt ngưỡng này."
    src = next(s for s in ctx["sources"] if s.get("code") == "7113")
    src["text"] = "Máy xử lý dữ liệu tự động xách tay, có trọng lượng không quá 10 kg."
    rows, _ = decode_task_answer(draft, ctx)
    jobs = [j for j in analysis_jobs(rows, ctx) if j["result_id"] == "R3"]
    reviews = [r for r in model_reviews(ctx, draft)["analysis_reviews"] if r["result_id"] == "R3"]
    for statement in ctx["user_context"]["statements"]:
        statement["text"] += " Máy A nặng 10 kg, máy B nặng 10,1 kg."
    check = reviews[0]["checks"][0]
    claim = draft["results"][2]["claims"][0]
    claim["fact_ids"] = [s["id"] for s in ctx["user_context"]["statements"]]
    rows[-1]["claims"][0]["fact_ids"] = claim["fact_ids"]
    jobs[0]["claims"][0]["fact_ids"] = claim["fact_ids"]
    check.update(
        assessment="APPLICATION",
        evidence_ids=[src["evidence_id"]],
        fact_ids=claim["fact_ids"],
        user_quotes=[s["text"] for s in ctx["user_context"]["statements"]],
    )
    checked, errors = check_analyses(reviews, jobs, rows, ctx)
    assert errors
    assert "R3" not in checked


@pytest.mark.parametrize("ids", [["E1"], ["E1", "E1"], ["E1", "E3"]])
def test_array_review_conditions_cannot_omit_duplicate_or_substitute_mandatory_source(ids):
    from rag.llm.review.review_slots import expand_review_slots

    _, errors = expand_review_slots(
        {
            "reviews": {
                "R1": {"review": {"condition_checks": [{"evidence_id": eid} for eid in ids]}}
            }
        },
        {"reviews": ["R1"], "condition_checks": {"R1": ["E1", "E2"]}},
    )
    assert errors
    assert any(e.diagnostic["code"] == "SCHEMA_VIOLATION" for e in errors)


def test_semantic_draft_defers_ancestor_coverage_until_product_review():
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer

    ctx = context()
    parent = next(source for source in ctx["sources"] if source.get("code") == "711311")
    ctx["candidate_evidence"][0]["required_citation_labels"].append(parent["label"])
    draft = model_answer(ctx)
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    assert all(r["valid"] for r in rows)


def test_semantic_draft_without_item_binding_reaches_review_for_intermediate_code():
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer

    ctx = context(explain=True)
    ctx["request"]["objectives"][1]["item_ids"] = []
    draft = model_answer(ctx)
    draft["results"][2]["claims"][0].update(
        kind="CONCLUSION", text="Hàng hóa này được phân loại vào nhóm 7113."
    )
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    assert all(r["valid"] for r in rows)


@pytest.mark.parametrize("identity", [[], {}, 3, None])
def test_malformed_array_condition_identity_is_repairable(identity):
    from rag.llm.review.review_slots import expand_review_slots

    _, errors = expand_review_slots(
        {"reviews": {"R1": {"review": {"condition_checks": [{"evidence_id": identity}]}}}},
        {"reviews": ["R1"], "condition_checks": {"R1": ["E1"]}},
    )
    assert errors


def test_explanation_cannot_swap_independently_verified_item_codes():
    from tests.test_goal_workflow import context, model_answer, model_reviews, run

    ctx = context(explain=True)
    draft = model_answer(ctx)
    reviews = model_reviews(ctx, draft)
    text = "Dây A được phân loại vào nhóm 7117; Dây B được phân loại vào nhóm 7113."
    draft["results"][2]["claims"][0]["text"] = text
    check = next(r for r in reviews["analysis_reviews"] if r["result_id"] == "R3")["checks"][0]
    check.update(
        assessment="APPLICATION",
        fact_ids=[s["id"] for s in ctx["user_context"]["statements"]],
        user_quotes=[s["text"] for s in ctx["user_context"]["statements"]],
    )
    got, _ = run(ctx, [draft, reviews])
    assert text not in got["answer"]["answer"]
    assert got["answer"]["results"][2]["status"] == "REQUIRES_REVIEW"


def test_source_snapshot_can_describe_historical_wording_without_applying_it():
    from rag.llm.review.analysis_review import analysis_jobs, check_analyses
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer, model_reviews

    ctx = context(explain=True)
    ctx["legal_scope"] = "SOURCE_SNAPSHOT"
    draft = model_answer(ctx)
    reviews = model_reviews(ctx, draft)
    for source in ctx["sources"]:
        source.update(legal_status="EXPIRED", effective_to="2020-12-31")
    rows, _ = decode_task_answer(draft, ctx)
    jobs = [job for job in analysis_jobs(rows, ctx) if job["result_id"] == "R3"]
    checked, errors = check_analyses(
        [r for r in reviews["analysis_reviews"] if r["result_id"] == "R3"], jobs, rows, ctx
    )
    assert not errors
    assert "R3" in checked


@pytest.mark.parametrize("code,expected", [("7113", "ANSWERED"), ("7117", "REQUIRES_REVIEW")])
def test_named_item_application_uses_only_that_items_verified_codes(code, expected):
    from tests.test_goal_workflow import context, model_answer, model_reviews, run

    ctx = context(explain=True)
    draft = model_answer(ctx)
    reviews = model_reviews(ctx, draft)
    fact = next(s for s in ctx["user_context"]["statements"] if s["text"] == "Dây A bằng bạc 925")
    draft["results"][2]["claims"][0].update(
        text=f"Dây A được phân loại vào nhóm {code}.", fact_ids=[fact["id"]]
    )
    check = next(r for r in reviews["analysis_reviews"] if r["result_id"] == "R3")["checks"][0]
    check.update(assessment="APPLICATION", fact_ids=[fact["id"]], user_quotes=[fact["text"]])
    got, _ = run(ctx, [draft, reviews])
    assert got["answer"]["results"][2]["status"] == expected


def test_application_role_requires_code_binding_even_without_application_verb():
    from rag.llm.validation.task_validation import code_claim_errors
    from tests.test_goal_workflow import context

    assert code_claim_errors(
        [{"kind": "CONCLUSION", "text": "Dây A: mã 7117."}],
        "",
        context(),
        {"7113"},
        application=True,
    )


def test_application_code_gate_does_not_treat_legal_document_year_as_hs_code():
    from rag.llm.validation.task_validation import code_claim_errors
    from tests.test_goal_workflow import context

    ctx = context()
    ctx["question"] += " Áp dụng theo Nghị định 26/2023/NĐ-CP."
    assert not code_claim_errors(
        [{"kind": "CONCLUSION", "text": "Dây A: mã 7113 theo Nghị định 26/2023/NĐ-CP."}],
        "",
        ctx,
        {"7113"},
        application=True,
    )
    assert code_claim_errors(
        [{"kind": "CONCLUSION", "text": "Dây A: mã 9999."}], "", ctx, {"7113"}, application=True
    )


def test_backend_binary_comparison_replaces_failed_prose_with_auditable_derivation():
    from rag.llm.generation.task_generation import _resolve_comparisons
    from rag.llm.review.review_coverage import review_coverage
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer

    ctx = context(compare=True)
    rows, errors = decode_task_answer(model_answer(ctx), ctx)
    assert not errors
    for row in rows[:2]:
        code = row["suggested_hs_code"]
        row.update(review_valid=True, verified_path=[{"level": 4, "code": code}])
    rows[-1].update(
        status="REQUIRES_REVIEW",
        failure_kind="TECHNICAL",
        analysis_review_valid=False,
        claims=[],
        analysis_checks=[],
    )
    resolved = _resolve_comparisons(rows, ctx)
    comparison = resolved[-1]
    assert comparison["status"] == "ANSWERED"
    assert not comparison.get("failure_kind")
    assert comparison["claims"] == []
    assert comparison["derived_from_reviewed_results"] == ["R1", "R2"]
    coverage = review_coverage(resolved)
    assert coverage["results"][-1]["status"] == "BACKEND_DERIVED"
    assert coverage["results"][-1]["scope"] == "CODE_COMPARISON"


def test_code_comparison_cannot_complete_a_comparison_of_legal_conditions():
    from rag.llm.generation.task_generation import _resolve_comparisons
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context, model_answer

    ctx = context(compare=True)
    ctx["request"]["objectives"][-1]["anchor"] = (
        "Cả hai có phải đáp ứng cùng điều kiện kiểm tra hay không?"
    )
    rows, _ = decode_task_answer(model_answer(ctx), ctx)
    for row in rows[:2]:
        row.update(
            review_valid=True, verified_path=[{"level": 4, "code": row["suggested_hs_code"]}]
        )
    rows[-1].update(
        status="REQUIRES_REVIEW",
        failure_kind="TECHNICAL",
        analysis_review_valid=False,
        claims=[],
        analysis_checks=[],
    )
    assert _resolve_comparisons(rows, ctx)[-1]["status"] == "REQUIRES_REVIEW"
