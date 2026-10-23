"""Regressions for product/legal ownership and source-backed HS ancestry."""

import json

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.generation.answering import generate_answer
from rag.llm.providers.groq_client import GroqClient, GroqError
from rag.llm.validation.answer import validate_answer
from rag.prompts.schemas.answer import DECISION_REVIEW_SCHEMA, PRODUCT_REVIEW_SCHEMA
from tests.support.legacy_generation import prepare_legacy_context as prepare_context


def hs_context(*, edges=None, records=None, config=None):
    rows = records or [
        {"id": "heading", "code": "8703", "level": 4, "source_text": "Passenger vehicles"},
        {"id": "subheading", "code": "870380", "level": 6, "source_text": "Electric motor only"},
        {"id": "leaf", "code": "87038099", "level": 8, "source_text": "Other vehicles"},
    ]
    graph = GraphContext(
        rows,
        [],
        edges
        if edges is not None
        else [
            {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
            {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
        ],
    )
    return prepare_context(
        "VF 9: passenger car, 7 seats, electric motor only, imported complete.",
        {"hs_candidates": [rows[-1]]},
        "hs",
        config or GroqConfig(keys=("fixture",)),
        graph,
    )


def abstention(status="MISSING_PRODUCT_INFO", **changes):
    return {
        "status": status,
        "answer": "What is the imported condition?"
        if status == "MISSING_PRODUCT_INFO"
        else "Corpus evidence is missing.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": ["Imported condition"] if status == "MISSING_PRODUCT_INFO" else [],
        "missing_legal_evidence": ["Applicable Chapter 87 notes"]
        if status == "INSUFFICIENT_LEGAL_EVIDENCE"
        else [],
        **changes,
    }


def recommendation(ctx, code="87038099"):
    citations = [{"label": s["label"], "quote": s["text"]} for s in ctx["sources"]]
    return {
        **abstention("RECOMMENDATION"),
        "answer": "Suggested code " + code + " " + " ".join(f"[{c['label']}]" for c in citations),
        "suggested_hs_code": code,
        "citations": citations,
    }


def supported_review(ctx):
    return {
        "status": "SUPPORTED",
        "reason": "Các điều kiện được đối chiếu với dữ kiện người dùng.",
        "product_facts": [
            {
                "fact": "Confirmed vehicle facts",
                "user_quote": "passenger car, 7 seats, electric motor only",
            }
        ],
        "condition_checks": [
            {
                "source_label": source["label"],
                "source_quote": source["text"],
                "assessment": "SATISFIED",
                "product_fact_indices": [0],
            }
            for source in ctx["sources"]
        ],
        "missing_information": [],
        "missing_legal_evidence": [],
    }


@pytest.mark.parametrize(
    "missing",
    [
        "Bổ sung nội dung phân nhóm 8703.90 và Chú giải Chương 87.",
        "Cung cấp mã HS và mô tả pháp lý.",
        "GIR 1 and GIR 6 legal text",
        "Chapter 87 notes and subheading wording",
        "chu giai chuong 87",
    ],
)
def test_legal_gaps_cannot_be_product_questions(missing):
    result = validate_answer(
        abstention(missing_information=[missing], answer=missing), hs_context()
    )
    assert not result["valid"]
    assert any("pháp lý" in e for e in result["errors"])


def test_only_product_status_can_ask_for_user_information():
    ctx = hs_context()
    assert validate_answer(abstention(), ctx)["valid"]
    assert validate_answer(abstention("INSUFFICIENT_LEGAL_EVIDENCE"), ctx)["valid"]
    assert not validate_answer(
        abstention("INSUFFICIENT_LEGAL_EVIDENCE", missing_information=["Seat count"]), ctx
    )["valid"]
    assert not validate_answer(
        abstention("REQUIRES_REVIEW", answer="Please provide seat count?"), ctx
    )["valid"]


def test_legal_request_cannot_hide_in_answer_or_another_status():
    for status in ["MISSING_PRODUCT_INFO", "INSUFFICIENT_LEGAL_EVIDENCE", "REQUIRES_REVIEW"]:
        value = abstention(status, answer="Vui lòng cung cấp Chú giải Chương 87.")
        assert not validate_answer(value, hs_context())["valid"]
    value = abstention(
        "INSUFFICIENT_LEGAL_EVIDENCE", answer="Corpus: vui lòng cung cấp Chú giải Chương 87."
    )
    assert not validate_answer(value, hs_context())["valid"]


@pytest.mark.parametrize(
    "text",
    [
        "Để xác định mã HS, vui lòng cho biết loại hàng thực tế và công dụng.",
        "Để có cơ sở tra cứu và phân loại mã HS, vui lòng làm rõ sản phẩm này là loại hàng gì.",
        "For HS classification, please provide the product material and function.",
        "Vui lòng cung cấp loại hàng và công dụng để có cơ sở xác định mã HS phù hợp.",
        "Vui lòng cho biết vật liệu nhằm xác định điều kiện phân loại.",
        "Please provide the product material for HS classification.",
    ],
)
def test_product_question_can_explain_its_classification_purpose(text):
    value = abstention(answer=text, missing_information=["Loại hàng thực tế và công dụng"])
    assert validate_answer(value, hs_context())["valid"]


@pytest.mark.parametrize(
    "text",
    [
        "Để xác định mã HS, vui lòng cung cấp Chú giải Chương 87.",
        "Chú giải Chương 87: vui lòng cung cấp nội dung đó.",
        "Vui lòng cho biết vật liệu; bạn cần cung cấp GIR 1.",
        "For HS classification, please provide chapter notes.",
        "Vui lòng cung cấp Chú giải Chương 87 để xác định mã HS.",
        "Vui lòng cho biết vật liệu để phân loại; bạn cần cung cấp GIR 1.",
        "Please provide chapter notes for HS classification.",
    ],
)
def test_product_question_preamble_does_not_allow_asking_for_legal_text(text):
    value = abstention(answer=text, missing_information=["Vật liệu hàng hóa"])
    assert not validate_answer(value, hs_context())["valid"]


def test_recommendation_requires_a_verified_and_cited_4_6_8_path():
    ctx = hs_context()
    assert validate_answer(recommendation(ctx), ctx)["valid"]
    path = ctx["candidate_evidence"][0]["hierarchy"]
    assert path["status"] == "VERIFIED"
    assert [node["code"] for node in path["chain"]] == ["8703", "870380", "87038099"]
    broken = hs_context(edges=[{"source": "heading", "target": "leaf", "relation": "CONTAINS"}])
    assert not validate_answer(recommendation(broken), broken)["valid"]
    value = recommendation(ctx)
    value["citations"] = value["citations"][:1]
    value["answer"] = "Suggested code 87038099 [S1]."
    assert not validate_answer(value, ctx)["valid"]


def test_prefix_matches_do_not_replace_actual_parent_child_edges():
    edges = [
        {"source": "heading", "target": "leaf", "relation": "CONTAINS"},
        {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
    ]
    ctx = hs_context(edges=edges)
    assert not validate_answer(recommendation(ctx), ctx)["valid"]


def test_cross_branch_parent_and_missing_graph_are_rejected():
    rows = [
        {"id": "heading", "code": "8703", "level": 4, "source_text": "Passenger vehicles"},
        {"id": "subheading", "code": "870390", "level": 6, "source_text": "Other propulsion"},
        {"id": "leaf", "code": "87038099", "level": 8, "source_text": "Other vehicles"},
    ]
    ctx = hs_context(records=rows)
    assert not validate_answer(recommendation(ctx), ctx)["valid"]
    ctx = prepare_context(
        "Product", {"hs_candidates": [rows[-1]]}, "hs", GroqConfig(keys=("fixture",))
    )
    assert not validate_answer(recommendation(ctx), ctx)["valid"]


@pytest.mark.parametrize("code", ["8703", "870380", "8703.80.99", "８７０３８０９９"])
def test_proposed_codes_must_have_exactly_eight_ascii_digits(code):
    ctx = hs_context()
    ctx["allowed_hs_codes"].append(code)
    assert not validate_answer(recommendation(ctx, code), ctx)["valid"]


def test_empty_hs_context_checks_identity_before_reporting_a_system_evidence_gap(monkeypatch):
    ctx = prepare_context("VF 9", {}, "hs", GroqConfig(keys=("fixture",)))
    client = GroqClient(GroqConfig(keys=("fixture",)))
    calls = []

    def complete(messages, schema, **kwargs):
        assert schema is DECISION_REVIEW_SCHEMA
        calls.append(messages)
        return {
            "content": json.dumps(
                {
                    "request_kind": "HS",
                    "identity_status": "UNCONFIRMED",
                    "product_type": "",
                    "product_type_quote": "",
                    "decision": "CLARIFY",
                    "reason": "Tên thương mại chưa xác nhận loại hàng thực tế.",
                    "clarifications": [
                        {
                            "question": "Sản phẩm thực tế là loại hàng gì?",
                            "basis": "PRODUCT_IDENTITY",
                            "source_label": "",
                            "source_quote": "",
                        }
                    ],
                    "retained_qa": {"answer": "", "citations": []},
                }
            ),
            "finish_reason": "stop",
            "model": "fixture",
        }

    monkeypatch.setattr(client, "complete", complete)
    result = generate_answer(ctx, client)
    assert result["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert result["answer"]["missing_information"] == ["Sản phẩm thực tế là loại hàng gì?"]
    assert result["answer"]["missing_legal_evidence"] == []
    assert result["validation"]["valid"]
    assert len(calls) == 1


def test_provider_gets_a_repair_instruction_for_legal_requests(monkeypatch):
    calls = []

    def complete(messages, schema, **kwargs):
        calls.append(messages)
        value = abstention(
            answer="Bổ sung Chú giải Chương 87.", missing_information=["Chú giải Chương 87"]
        )
        if len(calls) == 2:
            value = abstention("INSUFFICIENT_LEGAL_EVIDENCE")
        if schema is DECISION_REVIEW_SCHEMA:
            value = {
                "request_kind": "HS",
                "identity_status": "IDENTIFIED",
                "product_type": "passenger car",
                "product_type_quote": "passenger car",
                "decision": "KEEP",
                "reason": "Loại hàng đã được xác nhận; nguồn đối chiếu còn thiếu.",
                "clarifications": [],
                "retained_qa": {"answer": "", "citations": []},
            }
        return {"content": json.dumps(value), "finish_reason": "stop", "model": "fixture"}

    client = GroqClient(GroqConfig(keys=("fixture",)))
    monkeypatch.setattr(client, "complete", complete)
    result = generate_answer(hs_context(), client)
    assert len(calls) == 3
    assert "pháp lý" in calls[1][-1]["content"]
    assert "tiếng Việt" in calls[1][-1]["content"]
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"


def test_repeated_legal_requests_are_replaced_by_safe_system_abstention(monkeypatch):
    client = GroqClient(GroqConfig(keys=("fixture",)))
    value = abstention(answer="Cung cấp Chú giải Chương 87.", missing_information=["GIR 1"])
    monkeypatch.setattr(
        client,
        "complete",
        lambda *a, **k: {"content": json.dumps(value), "finish_reason": "stop", "model": "fixture"},
    )
    result = generate_answer(hs_context(), client)
    assert result["generation"]["guardrail_abstention"]
    assert len(result["generation"]["attempts"]) == 2
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["diagnostics"]["code"] == "ANSWER_VALIDATION_FAILED"
    assert result["answer"]["missing_information"] == []
    assert "Cung cấp" not in result["answer"]["answer"]


def test_too_small_budget_omits_candidate_instead_of_a_partial_parent_chain():
    ctx = hs_context(config=GroqConfig(keys=("fixture",), max_context_chars=200))
    assert "leaf" not in {s["id"] for s in ctx["sources"]}
    assert ctx["allowed_hs_codes"] == []
    assert ctx["candidate_evidence"] == []
    assert ctx["packing"]["omitted_candidate_codes"] == ["87038099"]
    assert not validate_answer(recommendation(ctx), ctx)["valid"]


def test_virtual_six_digit_node_verifies_structure_without_becoming_legal_wording():
    heading = {"id": "heading", "code": "8517", "source_text": "Telephone apparatus"}
    leaf = {"id": "leaf", "code": "85171300", "source_text": "Smartphones"}
    graph = GraphContext(
        [heading, leaf],
        [{"id": "subheading", "metadata": {"code": "851713", "level": 6, "virtual": True}}],
        [
            {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
            {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
        ],
    )
    ctx = prepare_context(
        "Smartphone", {"hs_candidates": [leaf]}, "hs", GroqConfig(keys=("fixture",)), graph
    )
    path = ctx["candidate_evidence"][0]["hierarchy"]
    assert path["status"] == "VERIFIED"
    assert path["chain"][1]["code"] == "851713"
    assert path["chain"][1]["label"] is None
    assert not path["chain"][1]["has_legal_wording"]
    assert validate_answer(recommendation(ctx, "85171300"), ctx)["valid"]


def test_expert_review_disclaimer_is_not_a_user_clarification_request():
    ctx = hs_context()
    value = recommendation(ctx)
    value["answer"] += " Đề xuất cần người có chuyên môn xác nhận."
    assert validate_answer(value, ctx)["valid"]


def test_missing_branch_wording_and_inconsistent_levels_are_rejected():
    rows = [
        {"id": "heading", "code": "8703", "level": 4, "source_text": "Passenger vehicles"},
        {"id": "subheading", "code": "870380", "level": 4, "source_text": "Electric motor only"},
        {"id": "leaf", "code": "87038099", "level": 8, "source_text": "Other vehicles"},
    ]
    ctx = hs_context(records=rows)
    assert not validate_answer(recommendation(ctx), ctx)["valid"]
    rows[1]["level"] = 6
    branch = {"id": "branch", "source_text": "Imported complete " + "x" * 2000}
    graph = GraphContext(
        [*rows, branch],
        [],
        [
            {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
            {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
            {"source": "branch", "target": "leaf", "relation": "CONTEXT_FOR"},
        ],
    )
    ctx = prepare_context(
        "Product",
        {"hs_candidates": [rows[-1]]},
        "hs",
        GroqConfig(keys=("fixture",), max_context_chars=1000),
        graph,
    )
    assert "branch" in ctx["omitted_source_ids"]
    assert ctx["allowed_hs_codes"] == []
    assert "leaf" in ctx["omitted_source_ids"]
    assert ctx["packing"]["omitted_candidate_codes"] == ["87038099"]
    assert not validate_answer(recommendation(ctx), ctx)["valid"]


def test_cycle_in_hs_parent_child_graph_is_rejected():
    ctx = hs_context(
        edges=[
            {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
            {"source": "subheading", "target": "leaf", "relation": "CONTAINS"},
            {"source": "leaf", "target": "heading", "relation": "CONTAINS"},
        ]
    )
    assert not validate_answer(recommendation(ctx), ctx)["valid"]


@pytest.mark.parametrize(
    "review, expected",
    [
        (
            {
                "status": "SUPPORTED",
                "product_facts": [
                    {
                        "fact": "Confirmed vehicle facts",
                        "user_quote": "passenger car, 7 seats, electric motor only",
                    }
                ],
                "missing_information": [],
                "missing_legal_evidence": [],
            },
            "RECOMMENDATION",
        ),
        (
            {
                "status": "MISSING_PRODUCT_INFO",
                "product_facts": [],
                "missing_information": ["Imported condition?"],
                "missing_legal_evidence": [],
            },
            "MISSING_PRODUCT_INFO",
        ),
        (
            {
                "status": "INSUFFICIENT_LEGAL_EVIDENCE",
                "product_facts": [],
                "missing_information": [],
                "missing_legal_evidence": ["Applicable Chapter 87 notes"],
            },
            "INSUFFICIENT_LEGAL_EVIDENCE",
        ),
        (
            {
                "status": "REQUIRES_REVIEW",
                "product_facts": [],
                "missing_information": [],
                "missing_legal_evidence": [],
            },
            "REQUIRES_REVIEW",
        ),
        (
            {
                "status": "SUPPORTED",
                "product_facts": [{"fact": "Material", "user_quote": "Solid gold"}],
                "missing_information": [],
                "missing_legal_evidence": [],
            },
            "REQUIRES_REVIEW",
        ),
        (
            {
                "status": "SUPPORTED",
                "product_facts": [
                    {"fact": "Vehicle facts", "user_quote": "VF 9… imported complete"}
                ],
                "missing_information": [],
                "missing_legal_evidence": [],
            },
            "REQUIRES_REVIEW",
        ),
        (
            {
                "status": "MISSING_PRODUCT_INFO",
                "product_facts": [],
                "missing_information": ["Provide GIR 1"],
                "missing_legal_evidence": [],
            },
            "REQUIRES_REVIEW",
        ),
    ],
)
def test_recommendation_review_separates_user_facts_and_legal_evidence(
    monkeypatch, review, expected
):
    ctx = hs_context()
    review = {
        "reason": "Kết quả đối chiếu dữ kiện với nhánh được cấp.",
        "condition_checks": supported_review(ctx)["condition_checks"]
        if review["status"] == "SUPPORTED"
        else [],
        **review,
    }
    client = GroqClient(GroqConfig(keys=("fixture",)))
    calls = []

    def complete(messages, schema, **kwargs):
        calls.append(schema)
        if schema is PRODUCT_REVIEW_SCHEMA:
            payload = json.loads(messages[1]["content"])
            assert payload["question"] == ctx["question"]
            assert "answer" not in payload
            value = review
        else:
            value = recommendation(ctx)
        return {"content": json.dumps(value), "finish_reason": "stop", "model": "fixture"}

    monkeypatch.setattr(client, "complete", complete)
    result = generate_answer(ctx, client)
    assert 2 <= len(calls) <= 3
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == expected
    if expected != "RECOMMENDATION":
        assert result["answer"]["suggested_hs_code"] == ""
    if expected == "MISSING_PRODUCT_INFO":
        assert result["answer"]["missing_information"] == ["Imported condition?"]
    else:
        assert result["answer"]["missing_information"] == []


def test_unavailable_product_review_cannot_release_a_recommendation(monkeypatch):
    ctx = hs_context()
    client = GroqClient(GroqConfig(keys=("fixture",)))

    def complete(messages, schema, **kwargs):
        if schema is PRODUCT_REVIEW_SCHEMA:
            raise GroqError(429, "fixture", 2)
        return {
            "content": json.dumps(recommendation(ctx)),
            "finish_reason": "stop",
            "model": "fixture",
        }

    monkeypatch.setattr(client, "complete", complete)
    result = generate_answer(ctx, client)
    assert result["validation"]["valid"]
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["generation"]["product_review"]["http_status"] == 429


@pytest.mark.parametrize(
    "defect",
    [
        "absent_checks",
        "empty_checks",
        "missing_parent",
        "invented_quote",
        "blank_quote",
        "unknown_label",
        "missing_fact",
        "wrong_fact",
        "unmet_condition",
        "skipped_parent",
    ],
)
def test_supported_review_requires_source_condition_coverage_and_user_facts(monkeypatch, defect):
    ctx = hs_context()
    review = supported_review(ctx)
    checks = review["condition_checks"]
    if defect == "absent_checks":
        review.pop("condition_checks")
    elif defect == "empty_checks":
        checks.clear()
    elif defect == "missing_parent":
        checks.pop()
    elif defect == "invented_quote":
        checks[0]["source_quote"] = "Not printed in the source"
    elif defect == "blank_quote":
        checks[0]["source_quote"] = "   "
    elif defect == "unknown_label":
        checks[0]["source_label"] = "S99"
    elif defect == "missing_fact":
        checks[0]["product_fact_indices"] = []
    elif defect == "wrong_fact":
        checks[0]["product_fact_indices"] = [100]
    elif defect == "unmet_condition":
        checks[0]["assessment"] = "MISSING_PRODUCT_INFO"
    else:
        checks[0]["assessment"] = "NOT_APPLICABLE"
    client = GroqClient(GroqConfig(keys=("fixture",)))

    def complete(messages, schema, **kwargs):
        value = review if schema is PRODUCT_REVIEW_SCHEMA else recommendation(ctx)
        return {"content": json.dumps(value), "finish_reason": "stop", "model": "fixture"}

    monkeypatch.setattr(client, "complete", complete)
    result = generate_answer(ctx, client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["suggested_hs_code"] == ""
    assert result["generation"]["product_review"]["errors"]


def test_user_supplied_legal_text_cannot_be_reused_as_product_facts(monkeypatch):
    ctx = hs_context()
    ctx["question"] += " Tôi cho rằng GIR 1 áp dụng."
    client = GroqClient(GroqConfig(keys=("fixture",)))

    def complete(messages, schema, **kwargs):
        value = recommendation(ctx)
        if schema is PRODUCT_REVIEW_SCHEMA:
            value = {
                "status": "SUPPORTED",
                "reason": "Dữ kiện được người dùng nêu.",
                "product_facts": [{"fact": "GIR 1 applies", "user_quote": "GIR 1"}],
                "condition_checks": supported_review(ctx)["condition_checks"],
                "missing_information": [],
                "missing_legal_evidence": [],
            }
        return {"content": json.dumps(value), "finish_reason": "stop", "model": "fixture"}

    monkeypatch.setattr(client, "complete", complete)
    result = generate_answer(ctx, client)
    assert result["answer"]["status"] == "REQUIRES_REVIEW"
    assert result["answer"]["suggested_hs_code"] == ""
    assert any(
        "Nội dung pháp lý" in error for error in result["generation"]["product_review"]["errors"]
    )
