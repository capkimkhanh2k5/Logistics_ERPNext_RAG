"""Regressions for the read-only audit findings; no model or corpus mutation."""

import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from rag.llm.context.builder import prepare_context
from rag.llm.contracts.errors import RequestPlanError
from rag.llm.evidence.evidence import clarification_errors
from rag.llm.review.analysis_review import analysis_jobs, check_analyses
from rag.llm.review.disambiguation import disambiguation_errors
from rag.llm.validation.answer import schema_errors
from rag.llm.validation.task_validation import code_claim_errors, decode_task_answer
from rag.prompts.core.repair import format_task_repair_prompt
from rag.prompts.generation.task_answering import TASK_ANSWER_SCHEMA, task_answer_schema
from rag.prompts.schemas.answer import bind_registry_schema
from rag.retrieval.evidence_recovery import (
    MAX_RECOVERY_SOURCES,
    recover_evidence,
    requirements_bundle,
)
from tests.test_candidate_disambiguation import comparison_review, vehicle_context
from tests.test_evidence_recovery import fixture
from tests.test_goal_workflow import context, model_answer, model_reviews, run


def test_metadata_only_branch_is_recovered_with_provenance():
    q, graph, result, _, ctx, gap = fixture()
    graph.nodes["control"] = {
        "role": "context",
        "source_text": "Chỉ sử dụng cho chuyến bay được điều khiển từ xa.",
        "locator": {"document": "source.pdf", "physical_page": 2, "sha256": "a" * 64},
    }
    graph.contexts["p"].add("control")
    recovered, meta = recover_evidence(q, result, ctx, [gap], SimpleNamespace(), graph)
    assert recovered and "control" in meta["new_source_ids"]
    source = next(r for r in recovered["package"] if r["id"] == "control")
    assert source["source_text"] == graph.citation("control")["text"]
    assert source["locator"] == graph.citation("control")["locator"]
    assert meta["new_source_ids"].index("control") < meta["new_source_ids"].index("l")


def test_navigation_metadata_never_becomes_legal_wording():
    q, graph, result, _, ctx, gap = fixture()
    graph.nodes["virtual"] = {"virtual": True, "source_text": "Nguồn điều hướng."}
    graph.contexts["p"].add("virtual")
    recovered, meta = recover_evidence(q, result, ctx, [gap], SimpleNamespace(), graph)
    assert recovered and "virtual" not in meta["new_source_ids"]


def test_legacy_independent_missing_dimension_is_never_consolidated_as_known():
    ctx = vehicle_context("Xe điện chở người, bằng kim loại.")
    review = comparison_review(ctx, missing=False)
    branch = review["branch_checks"][0]
    eids = branch["evidence_ids"]
    for s in ctx["sources"]:
        if s["evidence_id"] == eids[0]:
            s["text"] = "Bằng kim loại."
        if s["evidence_id"] == eids[-1]:
            s["text"] = "Dùng trong môi trường áp suất cao."
    review["branch_checks"] = [
        {**branch, "attribute": "material", "evidence_ids": [eids[0]]},
        {
            **branch,
            "attribute": "operating_pressure",
            "evidence_ids": [eids[-1]],
            "assessment": "MISSING",
            "fact_ids": [],
            "user_quotes": [],
        },
    ]
    original = deepcopy(review)
    errors = disambiguation_errors(review, ctx, "87038098")
    assert errors
    assert review["branch_checks"] == original["branch_checks"]


def test_legacy_deferred_accepts_a_real_pending_ancestor_without_releasing_code():
    ctx = vehicle_context()
    review = comparison_review(ctx)
    ancestor = next(s for s in ctx["sources"] if s.get("code") == "870380")
    for c in review["condition_checks"]:
        if c["evidence_id"] == ancestor["evidence_id"]:
            c.update(assessment="MISSING_PRODUCT_INFO", fact_ids=[], user_quotes=[])
    review["clarifications"] = [
        {
            "question": "Xe dùng loại động lực nào?",
            "attribute": "propulsion",
            "evidence_ids": [ancestor["evidence_id"]],
        }
    ]
    review["branch_checks"][0]["assessment"] = "DEFERRED"
    assert not disambiguation_errors(review, ctx, "87038098")
    review["status"] = "SUPPORTED"
    assert disambiguation_errors(review, ctx, "87038098")


def test_goal_wire_rejects_wrong_level_and_nonfinal_code_and_unknown_goal():
    ctx = context()
    draft = model_answer(ctx)
    wire = task_answer_schema(ctx["request"], ["7113", "7117"])
    assert not schema_errors(draft, wire)
    for field, value in (("code", "71131190"), ("objective_id", "G9")):
        changed = deepcopy(draft)
        changed["results"][0][field] = value
        assert schema_errors(changed, wire)
    draft["results"][0]["status"] = "MISSING_PRODUCT_INFO"
    _, errors = decode_task_answer(draft, ctx)
    assert any(getattr(e, "diagnostic", {}).get("code") == "NONFINAL_CODE" for e in errors)
    assert (
        wire["properties"]["results"]["items"]["properties"]["claims"]["items"]["type"] == "object"
    )


def test_gateway_wire_never_contains_an_empty_string_enum():
    ctx = context(explain=True)
    wire = task_answer_schema(ctx["request"], ["7113", "7117"])

    def check(value):
        if isinstance(value, dict):
            assert "" not in value.get("enum", [])
            assert "anyOf" not in value
            for child in value.values():
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)

    check(wire)


def test_code_contract_repairs_include_exact_field_and_expected_level():
    ctx = context()
    draft = model_answer(ctx)
    draft["results"][0].update(code="71131190", status="MISSING_PRODUCT_INFO")
    _, errors = decode_task_answer(draft, ctx)
    feedback = json.loads(format_task_repair_prompt(errors, phase="answer"))
    level = next(e for e in feedback["repair_errors"] if e["code"] == "CODE_LEVEL_MISMATCH")
    assert level["path"] == "/results/0/code"
    assert level["actual"] == "71131190" and level["expected"]["level"] == 4
    assert any(
        e["code"] == "NONFINAL_CODE" and e["expected"] == "" for e in feedback["repair_errors"]
    )


@pytest.mark.parametrize("kind", ["COMPARE", "REQUIREMENTS", "EXPLAIN"])
def test_nonclassification_legal_claims_are_reviewed_even_without_product_items(kind):
    ctx = context(explain=True)
    draft = model_answer(ctx)
    goal = ctx["request"]["objectives"][-1]
    ctx["request"] = {
        "items": [],
        "objectives": [{**goal, "kind": kind, "item_ids": [], "level": 0}],
    }
    draft["results"] = [draft["results"][-1]]
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors and len(analysis_jobs(rows, ctx)) == 1
    out, calls = run(ctx, [draft, model_reviews(ctx, draft)])
    assert len(calls) == 2 and out["validation"]["task_completion"]


def test_applied_code_cannot_be_hidden_in_legal_analysis():
    ctx = {"question": "", "sources": [{"code": "11111111"}], "candidate_evidence": []}
    for kind in ("CONCLUSION", "LEGAL_ANALYSIS"):
        assert code_claim_errors(
            [{"kind": kind, "text": "Thiết bị này thuộc mã 11111111."}], "", ctx
        )
    assert not code_claim_errors(
        [{"kind": "LEGAL_ANALYSIS", "text": "Nguồn mô tả phạm vi mã 11111111."}], "", ctx
    )


def test_requirements_review_cannot_call_omitted_dimension_answered():
    ctx = context(requirements=True)
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    unit = review["analysis_reviews"][0]["coverage_checks"][0]
    unit.update(assessment="OMITTED", claim_indices=[])
    retry_review = {"reviews": [], "analysis_reviews": review["analysis_reviews"]}
    out, calls = run(ctx, [draft, review, draft, retry_review])
    detail = out["answer"]["results"][-1]
    assert len(calls) == 4 and detail["status"] == "REQUIRES_REVIEW"
    assert detail["answer_coverage_gap"] == [unit["evidence_id"]]
    assert not detail["missing_legal_evidence"]
    assert out["answer"]["results"][0]["status"] == "RECOMMENDATION"


def test_question_criterion_quote_is_source_bound():
    ctx = {
        "sources": [{"evidence_id": "E1", "text": "Theo công dụng thực tế."}],
        "user_context": {"statements": []},
    }
    question = {
        "question": "Công dụng thực tế là gì?",
        "attribute": "use",
        "evidence_ids": ["E1"],
        "criterion_quote": "Theo tỷ lệ vật liệu.",
    }
    assert any("CRITERION_QUOTE_INVALID" in e for e in clarification_errors([question], ctx))
    question["criterion_quote"] = "Theo công dụng thực tế."
    assert not clarification_errors([question], ctx)


def test_invalid_plan_cannot_silently_enter_legacy_hs8_generation():
    query, graph, result, config, _, _ = fixture()
    result["query_plan"] = {"status": "FALLBACK_RAW", "request": None}
    with pytest.raises(RequestPlanError):
        prepare_context(query, result, "auto", config, graph)


def test_draft_repair_cannot_replace_an_already_valid_independent_result():
    ctx = context()
    draft = model_answer(ctx)
    bad = deepcopy(draft)
    bad["results"][1]["code"] = "71171920"
    repair = deepcopy(draft)
    repair["results"][0]["code"] = "7117"
    out, calls = run(ctx, [bad, repair, model_reviews(ctx, draft)])
    assert len(calls) == 3 and out["validation"]["task_completion"]
    assert out["answer"]["results"][0]["suggested_hs_code"] == "7113"
    feedback = json.loads(calls[1]["messages"][-1]["content"])
    assert feedback["repair_contract"]["locked_results"] == [
        {"objective_id": "G1", "item_id": "I1"}
    ]


def test_wording_recovery_searches_when_new_records_do_not_close_the_source_gap():
    q, graph, result, _, ctx, gap = fixture()
    graph.records.pop("l")
    graph.nodes["l"] = {"code_compact": "88062100", "level": 8}
    note = {"id": "note", "source_text": "Chú giải điều kiện phân nhóm."}
    graph.records["note"] = note
    searched = []

    def search(query, **kwargs):
        searched.append(query)
        return {"snapshot": "s", "package": [note]}

    recovered, meta = recover_evidence(
        q, result, ctx, [gap], SimpleNamespace(unified_search=search), graph
    )
    assert recovered and "p" in meta["new_source_ids"] and "note" in meta["new_source_ids"]
    assert searched and not meta["wording_scope_closed"] and meta["llm_planner_calls"] == 0


def test_corrective_search_results_are_not_discarded_when_graph_expansion_fills_budget():
    from rag.graph.context import GraphContext

    q, graph, result, _, ctx, gap = fixture()
    leaves = [
        {"id": f"leaf-{i:02d}", "code": f"880621{i:02d}", "source_text": f"Điều kiện nhánh {i}."}
        for i in range(1, 100)
    ]
    edges = [
        {"source": "h", "target": "p", "relation": "CONTAINS"},
        {"source": "p", "target": "l", "relation": "CONTAINS"},
        *[{"source": "p", "target": row["id"], "relation": "CONTAINS"} for row in leaves],
    ]
    graph = GraphContext([*graph.records.values(), *leaves], [], edges)
    target = leaves[-1]
    search = SimpleNamespace(unified_search=lambda *a, **kw: {"snapshot": "s", "package": [target]})
    recovered, meta = recover_evidence(q, result, ctx, [gap], search, graph)
    assert recovered and target["id"] in meta["new_source_ids"]
    assert len(meta["new_source_ids"]) == MAX_RECOVERY_SOURCES
    assert meta["search_priority"] and meta["graph_sources_displaced"]


def test_source_gap_legal_basis_vocabulary_does_not_become_a_code_application():
    ctx = {"question": "", "sources": [{"code": "1111"}], "candidate_evidence": []}
    for text in (
        "Chưa đủ cơ sở pháp lý (thiếu danh mục mã chi tiết thuộc nhóm 1111) để xác định mã.",
        "Chưa có danh mục mã thuộc nhóm 1111 để xác định mã chi tiết.",
    ):
        assert not code_claim_errors([{"kind": "CONCLUSION", "text": text}], "", ctx)
    for text in (
        "Thiết bị này thuộc nhóm 1111. Chưa đủ cơ sở pháp lý cho nhóm 1111.",
        "Chưa đủ cơ sở pháp lý nhưng thiết bị này thuộc nhóm 1111.",
    ):
        assert code_claim_errors([{"kind": "CONCLUSION", "text": text}], "", ctx)


def test_requirement_inventory_accepts_verified_leaf_path_through_unprinted_navigation():
    _, graph, _, _, _, _ = fixture()
    graph.nodes["p"] = {"virtual": True, "code_compact": "880621", "level": 6}
    assert graph.hs_hierarchy(graph.records["l"])["status"] == "VERIFIED"
    rows, scopes = requirements_bundle(graph, {"8806"}, 8)
    assert scopes[0]["complete"] and not scopes[0]["missing_codes"]
    assert "p" not in {r["id"] for r in rows}


def test_large_competitor_inventory_does_not_starve_another_heading():
    _, graph, _, _, _, _ = fixture()
    graph.records["other4"] = {
        "id": "other4",
        "code": "1000",
        "level": 4,
        "source_text": "Nhóm khác.",
    }
    graph.records["other6"] = {
        "id": "other6",
        "code": "100000",
        "level": 6,
        "source_text": "Phân nhóm khác.",
    }
    graph.parents["other6"].add("other4")
    graph.children["other4"].add("other6")
    for n in range(97):
        sid = f"other8-{n}"
        graph.records[sid] = {
            "id": sid,
            "code": f"100000{n:02d}",
            "level": 8,
            "source_text": f"Điều kiện {n}.",
        }
        graph.parents[sid].add("other6")
        graph.children["other6"].add(sid)
    rows, scopes = requirements_bundle(graph, {"1000", "8806"}, 8)
    assert len(rows) == MAX_RECOVERY_SOURCES
    assert next(s for s in scopes if s["heading"] == "8806")["complete"]
    assert not next(s for s in scopes if s["heading"] == "1000")["complete"]
    assert {"h", "p", "l"} <= {r["id"] for r in rows}


def test_registry_wire_rejects_unknown_ids_and_keeps_fact_and_evidence_domains_separate():
    wire = bind_registry_schema(TASK_ANSWER_SCHEMA, ["E-real"], ["U-real"])
    props = wire["properties"]["results"]["items"]["properties"]["claims"]["items"]["properties"]
    assert props["evidence_ids"]["items"]["pattern"] != props["fact_ids"]["items"]["pattern"]
    assert (
        "pattern"
        not in TASK_ANSWER_SCHEMA["properties"]["results"]["items"]["properties"]["claims"][
            "items"
        ]["properties"]["evidence_ids"]["items"]
    )
    ctx = context()
    raw = model_answer(ctx)
    bounded = bind_registry_schema(
        TASK_ANSWER_SCHEMA,
        [s["evidence_id"] for s in ctx["sources"]],
        [s["id"] for s in ctx["user_context"]["statements"]],
    )
    assert not schema_errors(raw, bounded)
    raw["results"][0]["claims"][0]["evidence_ids"] = ["E-invented"]
    assert schema_errors(raw, bounded)


def test_source_gap_code_reference_does_not_hide_an_affirmative_application():
    ctx = {"question": "", "sources": [{"code": "1111"}], "candidate_evidence": []}
    reference = {
        "kind": "CONCLUSION",
        "text": "Do thiếu dữ liệu biểu thuế thuộc nhóm 1111, chưa đủ căn cứ để xác định mã chi tiết.",
    }
    assert not code_claim_errors([reference], "", ctx)
    reference["text"] = (
        "Do thiếu dữ liệu văn bản biểu thuế chi tiết thuộc nhóm 1111, hiện chưa đủ căn cứ pháp lý để xác định mã."
    )
    assert not code_claim_errors([reference], "", ctx)
    for text in (
        "Thiết bị này thuộc nhóm 1111. Chưa đủ căn cứ cho nhóm 1111.",
        "Chưa đủ căn cứ nhưng thiết bị này thuộc nhóm 1111.",
    ):
        assert code_claim_errors([{"kind": "CONCLUSION", "text": text}], "", ctx)


def analysis_application_fixture():
    from rag.llm.evidence.evidence import bind_user_context

    question = "Động cơ xăng không truyền lực cơ học trực tiếp đến bánh xe."
    users = bind_user_context(question)
    ctx = {
        "question": question,
        "request": {
            "items": [{"id": "I1", "anchor": "Động cơ"}],
            "objectives": [{"id": "G1", "item_ids": ["I1"], "kind": "EXPLAIN", "level": 0}],
        },
        "user_context": users,
        "sources": [
            {
                "evidence_id": "E1",
                "code": "111111",
                "label": "S1",
                "text": "Kết hợp động cơ đốt trong và động cơ điện để tạo động lực.",
            }
        ],
        "candidate_evidence": [],
    }
    fid = users["statements"][0]["id"]
    rows = [
        {
            "result_id": "R1",
            "objective_id": "G1",
            "kind": "EXPLAIN",
            "status": "ANSWERED",
            "valid": True,
            "claims": [
                {
                    "kind": "CONCLUSION",
                    "text": "Thiết bị này được xác định thuộc loại đã chọn.",
                    "evidence_ids": ["E1"],
                    "fact_ids": [fid],
                }
            ],
        }
    ]
    value = [
        {
            "result_id": "R1",
            "checks": [
                {
                    "claim_index": 0,
                    "assessment": "APPLICATION",
                    "evidence_ids": ["E1"],
                    "fact_ids": [fid],
                    "user_quotes": [question],
                    "reason": "Nhận định cần chứng minh cơ chế áp dụng.",
                    "application_level": 6,
                }
            ],
        }
    ]
    return ctx, rows, value


def test_unproven_mechanism_application_is_abstained_without_repairing_its_label():
    ctx, rows, value = analysis_application_fixture()
    original = deepcopy(value)
    checked, errors = check_analyses(value, analysis_jobs(rows, ctx), rows, ctx)
    assert not errors and checked["R1"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert "được xác định" not in checked["R1"]["answer"]
    assert checked["R1"]["analysis_checks"][0]["assessment_origin"] == "BACKEND_SOURCE_GUARD"
    assert value == original


def test_case_bound_claim_cannot_become_reference_to_avoid_proof():
    ctx, rows, value = analysis_application_fixture()
    value[0]["checks"][0].update(assessment="REFERENCE", fact_ids=[], user_quotes=[])
    checked, errors = check_analyses(value, analysis_jobs(rows, ctx), rows, ctx)
    assert not checked and any("ASSESSMENT_MISMATCH" in e for e in errors)


def test_exclusion_failure_keeps_typed_source_and_quote_diagnostics():
    ctx = vehicle_context("Xe dùng động cơ diesel.")
    raw = comparison_review(ctx)
    row = raw["candidate_assessments"][0]
    eid = row["evidence_ids"][0]
    next(s for s in ctx["sources"] if s["evidence_id"] == eid)["text"] = (
        "Có khả năng nạp điện từ nguồn điện bên ngoài."
    )
    row.update(assessment="RULED_OUT")
    errors = disambiguation_errors(raw, ctx, "87038098")
    typed = [e.diagnostic for e in errors if hasattr(e, "diagnostic")]
    assert any(
        e["code"] == "EXCLUSION_UNPROVEN"
        and e["expected"]["operation"] == "REFUTE_NECESSARY_CONDITION"
        for e in typed
    )
