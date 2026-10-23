"""An unconfirmed branch cannot become a recommendation through retrieval rank."""

import copy
import json
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.context.builder import compose_query, prepare_context
from rag.llm.evidence.evidence import decode_product_review
from rag.llm.generation.answering import generate_answer
from rag.llm.review.decision_review import review_decision
from rag.prompts.schemas.answer import MODEL_DISAMBIGUATION_REVIEW_SCHEMA
from tests.test_registry_generation import main_answer, run


def vehicle_context(question="Xe điện VinFast VF9.", *, selected="87038098", budget=None):
    rows = [
        {
            "id": "h",
            "code": "8703",
            "level": 4,
            "source_text": "Ô tô thiết kế chủ yếu để chở người.",
        },
        {"id": "p", "code": "870380", "level": 6, "source_text": "Xe chỉ sử dụng động cơ điện."},
        {"id": "ckd", "code": "87038018", "level": 8, "source_text": "Ô tô khác, trừ ô tô van."},
        {"id": "other", "code": "87038098", "level": 8, "source_text": "Ô tô khác, trừ ô tô van."},
        {"id": "form-ckd", "source_text": "Dạng CKD (SEN):", "role": "context"},
        {"id": "form-other", "source_text": "Loại khác:", "role": "context"},
        # A matching prefix without CONTAINS is not a verified peer.
        {"id": "unlinked", "code": "87038099", "level": 8, "source_text": "Unlinked wording"},
    ]
    edges = [
        {"source": "h", "target": "p", "relation": "CONTAINS"},
        {"source": "p", "target": "ckd", "relation": "CONTAINS"},
        {"source": "p", "target": "other", "relation": "CONTAINS"},
        {"source": "form-ckd", "target": "ckd", "relation": "CONTEXT_FOR"},
        {"source": "form-other", "target": "other", "relation": "CONTEXT_FOR"},
    ]
    graph = GraphContext(rows, [], edges)
    leaf = next(r for r in rows if r.get("code") == selected)
    cfg = GroqConfig(keys=("fixture",), max_input_chars=100000, max_context_chars=budget or 50000)
    return prepare_context(question, {"hs_candidates": [leaf], "matches": [leaf]}, "hs", cfg, graph)


def comparison_review(ctx, *, missing=True):
    ids = {s["label"]: s["evidence_id"] for s in ctx["sources"]}
    source_ids = [
        eid for o in ctx["candidate_comparison"][0]["branch_options"] for eid in o["evidence_ids"]
    ]
    # Import-form proof must include the explicit form, not only the name before the comma.
    statement = max(ctx["user_context"]["statements"], key=lambda s: len(s["text"]))
    proof = {"fact_ids": [statement["id"]], "user_quotes": [statement["text"]]}
    selected = ctx["candidate_evidence"][0]
    return {
        "status": "MISSING_PRODUCT_INFO" if missing else "SUPPORTED",
        "reason": "Chưa biết dạng nhập khẩu để phân biệt các nhánh."
        if missing
        else "Dữ kiện đã phân biệt hai nhánh.",
        "condition_checks": [
            {
                "evidence_id": ids[label],
                "assessment": "MISSING_PRODUCT_INFO"
                if missing and label in selected["context_labels"]
                else "SATISFIED",
                **(
                    {"fact_ids": [], "user_quotes": []}
                    if missing and label in selected["context_labels"]
                    else proof
                ),
            }
            for label in selected["required_citation_labels"]
        ],
        "clarifications": [
            {
                "question": "Xe được nhập khẩu nguyên chiếc hay dạng CKD?",
                "attribute": "dạng nhập khẩu",
                "evidence_ids": source_ids,
            }
        ]
        if missing
        else [],
        "missing_legal_evidence": [],
        "candidate_assessments": [
            {
                "code": code,
                "assessment": "POSSIBLE" if missing or code == selected["code"] else "RULED_OUT",
                "evidence_ids": source_ids,
                **({"fact_ids": [], "user_quotes": []} if missing else proof),
            }
            for code in ctx["candidate_comparison"][0]["codes"]
        ],
        "branch_checks": [
            {
                "parent_code": "870380",
                "attribute": "dạng nhập khẩu",
                "assessment": "MISSING" if missing else "KNOWN",
                "evidence_ids": source_ids,
                **({"fact_ids": [], "user_quotes": []} if missing else proof),
            }
        ],
    }


def test_graph_adds_unretrieved_counterpart_without_promoting_it_to_retrieved_candidate():
    ctx = vehicle_context()
    assert ctx["allowed_hs_codes"] == ctx["retrieved_hs_codes"] == ["87038098"]
    assert [e["code"] for e in ctx["comparison_candidates"]] == ["87038018"]
    group = ctx["candidate_comparison"][0]
    assert group["codes"] == ["87038018", "87038098"] and not group["missing_codes"]
    assert len(group["branch_options"]) == 2
    assert all(option["evidence_ids"] for option in group["branch_options"])
    assert "Unlinked wording" not in json.dumps(ctx["sources"])


def test_missing_form_overrides_a_proposed_code_with_one_existing_review_call():
    ctx = vehicle_context()
    result, calls = run(ctx, [main_answer(ctx), comparison_review(ctx)])
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["answer"]["missing_information"] == [
        "Xe được nhập khẩu nguyên chiếc hay dạng CKD?"
    ]
    assert len(calls) == 2 and calls[1]["schema"] is MODEL_DISAMBIGUATION_REVIEW_SCHEMA
    payload = json.loads(calls[1]["messages"][1]["content"])
    assert {c["code"] for c in payload["comparison_candidates"]} == {"87038018", "87038098"}
    assert result["generation"]["product_review"]["candidate_disambiguation"]["branch_checks"]


@pytest.mark.parametrize("selected", ["87038018", "87038098"])
def test_known_import_form_does_not_ask_again(selected):
    form = "dạng CKD" if selected.endswith("18") else "nguyên chiếc, không phải CKD"
    q = f"Xe điện chở người VinFast VF9, nhập khẩu {form}, không phải xe van."
    ctx = vehicle_context(q, selected=selected)
    result, calls = run(ctx, [main_answer(ctx), comparison_review(ctx, missing=False)])
    assert result["answer"]["status"] == "RECOMMENDATION"
    assert result["answer"]["suggested_hs_code"] == selected
    assert result["answer"]["missing_information"] == [] and len(calls) == 2


def test_corrected_import_form_is_available_to_the_same_comparison_review():
    q = compose_query(
        "Xe điện nhập khẩu nguyên chiếc.", ["Đính chính: hàng ở dạng CKD, chưa lắp ráp."], None
    )
    ctx = vehicle_context(q, selected="87038018")
    value = comparison_review(ctx, missing=False)
    latest = next(s for s in ctx["user_context"]["statements"] if s["turn"] == 2)
    for item in [
        *value["condition_checks"],
        *value["candidate_assessments"],
        *value["branch_checks"],
    ]:
        item.update(fact_ids=[latest["id"]], user_quotes=[latest["text"]])
    result, calls = run(ctx, [main_answer(ctx), value])
    assert result["answer"]["suggested_hs_code"] == "87038018" and len(calls) == 2
    assert latest["text"] in calls[1]["messages"][1]["content"]


@pytest.mark.parametrize(
    "fault",
    [
        "multiple",
        "unknown_branch",
        "omitted_code",
        "duplicate_code",
        "omitted_branch",
        "unbound_source",
        "foreign_fact",
        "invented_quote",
        "missing_counterpart_source",
        "silent_exclusion",
        "unrelated_question",
        "selected_evidence_gap",
    ],
)
def test_invalid_comparison_cannot_release_a_code(fault):
    ctx = vehicle_context("Xe điện nhập khẩu nguyên chiếc, không phải CKD.")
    value = comparison_review(ctx, missing=False)
    if fault == "multiple":
        value["candidate_assessments"][0]["assessment"] = "POSSIBLE"
    elif fault == "unknown_branch":
        value["branch_checks"][0].update(assessment="MISSING", fact_ids=[], user_quotes=[])
    elif fault == "omitted_code":
        value["candidate_assessments"].pop()
    elif fault == "duplicate_code":
        value["candidate_assessments"].append(copy.deepcopy(value["candidate_assessments"][0]))
    elif fault == "omitted_branch":
        value["branch_checks"] = []
    elif fault == "unbound_source":
        value["branch_checks"][0]["evidence_ids"] = ["Eforeign"]
    elif fault == "foreign_fact":
        value["branch_checks"][0]["fact_ids"] = ["Uforeign"]
    elif fault == "invented_quote":
        value["branch_checks"][0]["user_quotes"] = ["Dữ kiện tự giả định"]
    elif fault == "silent_exclusion":
        value["candidate_assessments"][0].update(fact_ids=[], user_quotes=[])
    elif fault == "unrelated_question":
        value = comparison_review(ctx)
        value["clarifications"][0]["attribute"] = "khối lượng"
    elif fault == "selected_evidence_gap":
        value["candidate_assessments"][-1]["assessment"] = "INSUFFICIENT_LEGAL_EVIDENCE"
    else:
        ctx["candidate_comparison"][0]["missing_codes"] = ["87038018"]
    _, errors = decode_product_review(value, ctx, candidate_code="87038098")
    assert errors
    result, calls = run(ctx, [main_answer(ctx), value, value])
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["answer"]["status"] == "REQUIRES_REVIEW" and len(calls) == 3


def test_missing_comparison_contract_or_malformed_json_is_a_technical_failure():
    ctx = vehicle_context()
    old = comparison_review(ctx, missing=False)
    del old["candidate_assessments"], old["branch_checks"]
    result, _ = run(ctx, [main_answer(ctx), old, old])
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    outputs = iter([json.dumps(main_answer(ctx)), "{", "{"])
    client = SimpleNamespace(
        complete=lambda *a, **kw: {
            "content": next(outputs),
            "finish_reason": "stop",
            "model": "fixture",
        }
    )
    result = generate_answer(ctx, client)
    assert result["answer"]["suggested_hs_code"] == ""


def test_budget_omission_is_reported_as_missing_coverage_not_a_ruled_out_candidate():
    ctx = vehicle_context(budget=1)
    assert ctx["candidate_comparison"][0]["missing_codes"]
    assert "87038018" in ctx["candidate_comparison"][0]["codes"]


def test_answer_can_ask_the_discriminator_without_an_additional_review_request():
    ctx = vehicle_context()
    question = comparison_review(ctx)["clarifications"]
    result, calls = run(ctx, [main_answer(ctx, status="MISSING_PRODUCT_INFO", questions=question)])
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO" and len(calls) == 1


def test_material_difference_without_branch_context_uses_the_same_generic_contract():
    rows = [
        {"id": "h", "code": "1111", "level": 4, "source_text": "Đồ dùng."},
        {"id": "p", "code": "111111", "level": 6, "source_text": "Đồ dùng theo vật liệu."},
        {"id": "glass", "code": "11111101", "level": 8, "source_text": "Bằng thủy tinh."},
        {"id": "plastic", "code": "11111102", "level": 8, "source_text": "Bằng nhựa."},
    ]
    graph = GraphContext(
        rows,
        [],
        [
            {"source": "h", "target": "p", "relation": "CONTAINS"},
            {"source": "p", "target": "glass", "relation": "CONTAINS"},
            {"source": "p", "target": "plastic", "relation": "CONTAINS"},
        ],
    )
    ctx = prepare_context(
        "Đồ dùng mang tên ZXQ.",
        {"hs_candidates": [rows[2]]},
        "hs",
        GroqConfig(keys=("fixture",)),
        graph,
    )
    leaf_sources = [s for s in ctx["sources"] if s["code"] in {"11111101", "11111102"}]
    proof = {"fact_ids": [], "user_quotes": []}
    value = {
        "status": "MISSING_PRODUCT_INFO",
        "reason": "Vật liệu chưa được cung cấp để phân biệt hai mã.",
        "condition_checks": [
            {
                "evidence_id": leaf_sources[0]["evidence_id"],
                "assessment": "MISSING_PRODUCT_INFO",
                **proof,
            }
        ],
        "clarifications": [
            {
                "question": "Sản phẩm làm bằng thủy tinh hay nhựa?",
                "attribute": "vật liệu",
                "evidence_ids": [s["evidence_id"] for s in leaf_sources],
            }
        ],
        "missing_legal_evidence": [],
        "candidate_assessments": [
            {
                "code": s["code"],
                "assessment": "POSSIBLE",
                "evidence_ids": [s["evidence_id"]],
                **proof,
            }
            for s in leaf_sources
        ],
        "branch_checks": [],
    }
    result, calls = run(ctx, [main_answer(ctx), value])
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO" and len(calls) == 2
    assert result["answer"]["missing_information"] == ["Sản phẩm làm bằng thủy tinh hay nhựa?"]


def test_decision_review_receives_comparison_scope_before_treating_unknown_form_as_legal_gap():
    ctx = vehicle_context()
    calls = []
    statement = ctx["user_context"]["statements"][0]
    value = {
        "request_kind": "HS",
        "identity_status": "IDENTIFIED",
        "identity_fact_ids": [statement["id"]],
        "product_type": "xe điện",
        "decision": "CLARIFY",
        "reason": "Nguồn đã có hai nhánh; cần làm rõ dạng nhập khẩu.",
        "retained_qa": [],
        "clarifications": comparison_review(ctx)["clarifications"],
    }

    def complete(messages, schema, **kwargs):
        calls.append(json.loads(messages[1]["content"]))
        return {
            "content": json.dumps(value),
            "finish_reason": "stop",
            "model": "fixture",
            "elapsed_ms": 1,
        }

    answer = {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Chưa đủ căn cứ.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": ["Chưa phân biệt được dạng nhập khẩu."],
    }
    result, details = review_decision(ctx, answer, SimpleNamespace(complete=complete))
    assert details["valid"] and result["status"] == "MISSING_PRODUCT_INFO"
    assert calls[0]["candidate_comparison"] == ctx["candidate_comparison"]
    assert len(calls) == 1


@pytest.mark.parametrize("omit_competitor", [False, True])
def test_candidates_in_different_subheadings_cannot_be_ignored(omit_competitor):
    rows = []
    edges = []
    for code, wording in [
        ("11111101", "Thiết bị bơm chất lỏng."),
        ("22222201", "Thiết bị thổi khí."),
    ]:
        for level in (4, 6, 8):
            rows.append(
                {"id": code[:level], "code": code[:level], "level": level, "source_text": wording}
            )
        edges.extend(
            [
                {"source": code[:4], "target": code[:6], "relation": "CONTAINS"},
                {"source": code[:6], "target": code, "relation": "CONTAINS"},
            ]
        )
    leaves = [r for r in rows if r["level"] == 8]
    ctx = prepare_context(
        "Thiết bị ZXQ.",
        {"hs_candidates": leaves},
        "hs",
        GroqConfig(keys=("fixture",)),
        GraphContext(rows, [], edges),
    )
    assert ctx["candidate_comparison"][0]["parent_code"] == ""
    sources = {s["code"]: s["evidence_id"] for s in ctx["sources"]}
    value = {
        "status": "MISSING_PRODUCT_INFO",
        "reason": "Cần biết công dụng để phân biệt các mã.",
        "condition_checks": [
            {
                "evidence_id": sources["11111101"],
                "assessment": "MISSING_PRODUCT_INFO",
                "fact_ids": [],
                "user_quotes": [],
            }
        ],
        "clarifications": [
            {
                "question": "Thiết bị dùng để bơm chất lỏng hay thổi khí?",
                "attribute": "công dụng",
                "evidence_ids": [sources["11111101"], sources["22222201"]],
            }
        ],
        "missing_legal_evidence": [],
        "branch_checks": [],
        "candidate_assessments": [
            {
                "code": leaf["code"],
                "assessment": "POSSIBLE",
                "evidence_ids": [sources[leaf["code"]]],
                "fact_ids": [],
                "user_quotes": [],
            }
            for leaf in leaves
        ],
    }
    if omit_competitor:
        value["candidate_assessments"].pop()
        _, errors = decode_product_review(value, ctx, candidate_code="11111101")
        assert errors
    else:
        result, calls = run(ctx, [main_answer(ctx), value])
        assert result["answer"]["status"] == "MISSING_PRODUCT_INFO" and len(calls) == 2
        assert len(json.loads(calls[1]["messages"][1]["content"])["comparison_candidates"]) == 2
