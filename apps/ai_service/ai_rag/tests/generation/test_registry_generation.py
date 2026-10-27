"""Generic user evidence, open attributes and server-owned citations in fresh contexts."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.context.builder import compose_query, prepare_context
from rag.llm.evidence.evidence import (
    bind_user_context,
    decode_answer,
    decode_product_review,
    user_registry,
)
from rag.llm.generation.answering import generate_answer
from rag.prompts.schemas.answer import (
    MODEL_ANSWER_SCHEMA,
    MODEL_DECISION_REVIEW_SCHEMA,
    MODEL_PRODUCT_REVIEW_SCHEMA,
)
from rag.utils.files import digest


def context(question, *, mass=False, broken=False, task="hs", snapshot="snapshot-a"):
    code = "84713020" if mass else "85171300"
    wording = "Máy có khối lượng không quá 10 kg" if mass else "Điện thoại thông minh"
    rows = [
        {"id": "h", "code": code[:4], "level": 4, "source_text": "Mô tả nhóm hàng."},
        {"id": "p", "code": code[:6], "level": 6, "source_text": wording},
        {"id": "l", "code": code, "level": 8, "source_text": "Mô tả phân nhóm hàng."},
    ]
    edges = [
        {"source": "h", "target": "p", "relation": "CONTAINS"},
        {"source": "p", "target": "l", "relation": "CONTAINS"},
    ]
    return prepare_context(
        question,
        {"snapshot": snapshot, "hs_candidates": [rows[-1]], "matches": rows},
        task,
        GroqConfig(keys=("fixture",)),
        GraphContext(rows, [], edges[1:] if broken else edges),
    )


def main_answer(ctx, *, status="RECOMMENDATION", questions=None):
    return {
        "status": status,
        "claims": [
            {
                "kind": "CONCLUSION",
                "text": "Đề xuất theo nguồn và dữ kiện đã đối chiếu."
                if status == "RECOMMENDATION"
                else "Cần làm rõ dữ kiện quyết định.",
                "evidence_ids": [s["evidence_id"] for s in ctx["sources"]],
                "fact_ids": [],
            }
        ],
        "suggested_hs_code": ctx["allowed_hs_codes"][0] if status == "RECOMMENDATION" else "",
        "clarifications": questions or [],
        "missing_legal_evidence": [],
    }


def review(ctx, *, status="SUPPORTED", questions=None, quote=None):
    statement = next(iter(user_registry(ctx).values()))
    return {
        "status": status,
        "reason": "Đã đối chiếu dữ kiện với điều kiện nguồn."
        if status == "SUPPORTED"
        else "Thiếu dữ kiện quyết định mà nguồn yêu cầu.",
        "condition_checks": [
            {
                "evidence_id": s["evidence_id"],
                "assessment": "SATISFIED" if status == "SUPPORTED" else "MISSING_PRODUCT_INFO",
                "fact_ids": [statement["id"]] if status == "SUPPORTED" else [],
                "user_quotes": [quote or statement["text"]] if status == "SUPPORTED" else [],
            }
            for s in ctx["sources"]
        ],
        "clarifications": questions or [],
        "missing_legal_evidence": [],
    }


def run(ctx, outputs):
    calls, pending = [], iter(outputs)

    def complete(messages, schema, **kwargs):
        calls.append({"schema": schema, "messages": copy.deepcopy(messages), **kwargs})
        try:
            value = next(pending)
        except StopIteration:
            pytest.fail("Unexpected additional LLM call")
        return {
            "content": json.dumps(value, ensure_ascii=False),
            "finish_reason": "stop",
            "model": "fixture",
            "elapsed_ms": 1,
        }

    return generate_answer(ctx, SimpleNamespace(complete=complete)), calls


def decision(ctx, *, identified=True):
    return {
        "request_kind": "HS",
        "identity_status": "IDENTIFIED" if identified else "UNCONFIRMED",
        "product_type": "loại hàng do model nhận diện" if identified else "",
        "identity_fact_ids": [next(iter(user_registry(ctx)))] if identified else [],
        "decision": "KEEP" if identified else "CLARIFY",
        "reason": "Đã rõ đối tượng; ngữ cảnh chưa có nguồn pháp lý."
        if identified
        else "Tên chưa đủ rõ để xác định đối tượng.",
        "retained_qa": [],
        "clarifications": []
        if identified
        else [
            {
                "question": "Sản phẩm thuộc loại hàng gì?",
                "attribute": "product_type",
                "evidence_ids": [],
            }
        ],
    }


@pytest.mark.parametrize(
    "query",
    [
        "Tên thương mại ZXQ, độ kín cấp VI, áp suất danh nghĩa PN16.",
        "Vải có mật độ sợi ngang 180 sợi/cm và độ bền kéo 500 N.",
        "MacBook Pro M5 Pro có mã HS nào?",
        "Ốp lưng cho iPhone.",
        "Giả sử đây là điện thoại; chưa xác nhận cấu tạo.",
    ],
)
def test_registry_preserves_arbitrary_user_language_without_classifying_or_inventing(query):
    store = bind_user_context(query)
    assert store["interpretation"] == "USER_STATEMENTS_NOT_VERIFIED_FACTS"
    for row in store["statements"]:
        assert query[row["start"] : row["end"]] == row["text"]
        assert not {"key", "value", "origin", "state", "reference", "category"} & row.keys()
    assert any(row["text"] == query for row in store["statements"])


def test_turns_preserve_corrections_negation_and_unaffected_context_without_a_parser_guess():
    query = compose_query(
        "Vật liệu là bông, khối lượng 20 kg.",
        [
            "Đính chính: khối lượng 2 kg; không thay đổi vật liệu.",
            "Có thể độ bền là 500 N, chưa xác nhận.",
        ],
        None,
    )
    rows = bind_user_context(query)["statements"]
    assert {r["turn"] for r in rows} == {1, 2, 3}
    assert any("20 kg" in r["text"] and r["turn"] == 1 for r in rows)
    assert any("Đính chính" in r["text"] and r["turn"] == 2 for r in rows)
    assert any("chưa xác nhận" in r["text"] and r["turn"] == 3 for r in rows)
    assert bind_user_context(query) == bind_user_context(query)
    assert digest(bind_user_context(query)) != digest(bind_user_context(query + " Khác."))


def test_removed_category_files_and_imports_cannot_become_runtime_dependencies():
    root = Path(__file__).resolve().parents[2]
    for name in (
        "config/product_families.json",
        "config/product_references.json",
        "rag/llm/product_facts.py",
    ):
        assert not (root / name).exists()
    for path in (root / "rag").rglob("*.py"):
        assert "from rag.llm.product_facts" not in path.read_text()


@pytest.mark.parametrize(
    "attribute", ["fiber_density", "pressure_grade", "độ bền kéo", "cấp độ kín"]
)
def test_attributes_are_open_and_citations_are_required_without_a_category_dictionary(attribute):
    ctx = context("Hàng hóa cần phân loại.")
    question = {
        "question": "Thuộc tính quyết định hiện có giá trị nào?",
        "attribute": attribute,
        "evidence_ids": [ctx["sources"][0]["evidence_id"]],
    }
    value = main_answer(ctx, status="MISSING_PRODUCT_INFO", questions=[question])
    _, errors = decode_answer(value, ctx)
    assert not errors
    question["evidence_ids"] = []
    assert decode_answer(value, ctx)[1]


def test_shared_user_statements_reach_main_and_independent_review_and_proposed_answer_is_checked():
    ctx = context("Điện thoại mẫu Z, cấu tạo theo mô tả đã cung cấp.")
    generated, calls = run(ctx, [main_answer(ctx), review(ctx)])
    assert generated["validation"]["valid"]
    assert generated["answer"]["status"] == "RECOMMENDATION"
    assert [c["schema"] for c in calls] == [MODEL_ANSWER_SCHEMA, MODEL_PRODUCT_REVIEW_SCHEMA]
    for call in calls:
        payload = json.loads(call["messages"][1]["content"])
        assert payload["user_context"] == ctx["user_context"]
        assert "product_facts" not in payload
    review_payload = json.loads(calls[1]["messages"][1]["content"])
    assert review_payload["proposed_answer"]["suggested_hs_code"] == "85171300"
    assert generated["validation"]["semantic_grounding"] == "MODEL_REVIEWED"


@pytest.mark.parametrize(
    "defect",
    [
        "unknown_id",
        "other_question",
        "invented_quote",
        "wrong_span_id",
        "fabricated_fact",
        "missing_quotes",
    ],
)
def test_product_review_rejects_forged_user_provenance(defect):
    ctx = context(compose_query("Vật liệu bông.", ["Khối lượng 2 kg."], None))
    bad = review(ctx)
    if defect == "unknown_id":
        bad["condition_checks"][0]["fact_ids"] = ["Ufake"]
    elif defect == "other_question":
        bad["condition_checks"][0]["fact_ids"] = list(user_registry(context("Khác hoàn toàn.")))
    elif defect == "invented_quote":
        bad["condition_checks"][0]["user_quotes"] = ["Khối lượng 3 kg."]
    elif defect == "wrong_span_id":
        bad["condition_checks"][0]["user_quotes"] = ["Khối lượng 2 kg."]
    elif defect == "fabricated_fact":
        bad["product_facts"] = [{"fact": "Tự tạo", "user_quote": "Tự tạo"}]
    else:
        for check in bad["condition_checks"]:
            check["user_quotes"] = []
        generated, _ = run(ctx, [main_answer(ctx), bad, bad])
        assert generated["answer"]["status"] == "REQUIRES_REVIEW"
        assert not generated["answer"]["suggested_hs_code"]
        return
    assert decode_product_review(bad, ctx)[1]


def test_numeric_guard_cannot_turn_a_product_name_into_a_measurement():
    ctx = context("Model Alpha.", mass=True)
    bad = review(ctx)
    question = {
        "question": "Khối lượng hàng thực tế là bao nhiêu?",
        "attribute": "khối lượng",
        "evidence_ids": [next(s["evidence_id"] for s in ctx["sources"] if s["id"] == "p")],
    }
    fixed = review(ctx, status="MISSING_PRODUCT_INFO", questions=[question])
    generated, calls = run(ctx, [main_answer(ctx), bad, fixed])
    assert generated["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert generated["answer"]["missing_information"] == [question["question"]]
    assert len(calls) == 3
    assert not generated["generation"]["product_review"]["attempts"][0]["valid"]


def test_numeric_review_uses_a_real_selected_span_and_preserves_full_context_for_semantics():
    ctx = context("Model Alpha, khối lượng 2 kg có mã HS bao nhiêu?", mass=True)
    statement = next(
        r for r in user_registry(ctx).values() if r["start"] == 0 and r["text"] == ctx["question"]
    )
    value = review(ctx, quote="khối lượng 2 kg")
    for check in value["condition_checks"]:
        check["fact_ids"] = [statement["id"]]
    generated, calls = run(ctx, [main_answer(ctx), value])
    assert generated["answer"]["status"] == "RECOMMENDATION"
    assert json.loads(calls[1]["messages"][1]["content"])["question"] == ctx["question"]


@pytest.mark.parametrize("given", ["khối lượng 2 kg", "khối lượng không quá 5 kg"])
def test_generic_numeric_guard_rejects_reasking_an_already_sufficient_measurement(given):
    ctx = context(f"Tên hàng dòng Z, {given} có mã HS nào?", mass=True)
    question = {
        "question": "Khối lượng của hàng là bao nhiêu?",
        "attribute": "khối lượng",
        "evidence_ids": [next(s["evidence_id"] for s in ctx["sources"] if s["id"] == "p")],
    }
    value = main_answer(ctx, status="MISSING_PRODUCT_INFO", questions=[question])
    assert any("Không hỏi lại số đo" in error for error in decode_answer(value, ctx)[1])


@pytest.mark.parametrize(
    "given",
    [
        "có thể khối lượng 2 kg",
        "khối lượng không quá 20 kg",
        "khối lượng 2 kg hoặc 20 kg",
    ],
)
def test_numeric_guard_does_not_treat_uncertainty_or_insufficient_bounds_as_known(given):
    ctx = context(f"Tên hàng dòng Z, {given} có mã HS nào?", mass=True)
    question = {
        "question": "Khối lượng của hàng là bao nhiêu?",
        "attribute": "khối lượng",
        "evidence_ids": [next(s["evidence_id"] for s in ctx["sources"] if s["id"] == "p")],
    }
    value = main_answer(ctx, status="MISSING_PRODUCT_INFO", questions=[question])
    assert not decode_answer(value, ctx)[1]


def test_review_receives_actual_sources_used_in_the_draft_beyond_candidate_ancestry():
    ctx = context("Loại hàng theo mô tả.")
    from rag.llm.evidence.evidence import bind_evidence

    extra = bind_evidence(
        [
            {
                "id": "extra",
                "label": "S4",
                "text": "Chú giải bổ sung có nội dung.",
            }
        ],
        ctx["snapshot"],
    )[0]
    ctx["sources"].append(extra)
    answer = main_answer(ctx)
    generated, calls = run(ctx, [answer, review(ctx)])
    payload = json.loads(calls[1]["messages"][1]["content"])
    assert extra["evidence_id"] in {s["evidence_id"] for s in payload["sources"]}
    assert generated["answer"]["status"] == "RECOMMENDATION"


def test_unknown_trade_name_can_clarify_without_inventing_a_source():
    ctx = prepare_context("ZXQ là hàng gì?", {}, "hs", GroqConfig(keys=("fixture",)))
    generated, calls = run(ctx, [decision(ctx, identified=False)])
    assert generated["answer"]["status"] == "MISSING_PRODUCT_INFO"
    assert not generated["answer"]["citations"]
    assert calls[0]["schema"] is MODEL_DECISION_REVIEW_SCHEMA


def test_semantic_category_can_differ_from_raw_trade_name_without_a_handwritten_mapping():
    ctx = prepare_context("Tên thương mại dòng Z.", {}, "hs", GroqConfig(keys=("fixture",)))
    generated, _ = run(ctx, [decision(ctx)])
    assert generated["validation"]["valid"]
    assert generated["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert not generated["answer"]["missing_information"]


def test_identity_requires_real_user_ids_even_when_model_declares_it_identified():
    ctx = prepare_context("Tên thương mại dòng Z.", {}, "hs", GroqConfig(keys=("fixture",)))
    bad = decision(ctx)
    bad["identity_fact_ids"] = ["Uinvented"]
    generated, _ = run(ctx, [bad, bad])
    assert generated["answer"]["status"] == "REQUIRES_REVIEW"
    assert not generated["generation"]["decision_review"]["valid"]


def test_product_claims_need_real_user_provenance_but_allow_paraphrase():
    ctx = context("Người dùng mô tả hàng bằng tiếng Việt.")
    value = main_answer(ctx, status="REQUIRES_REVIEW")
    value["claims"] = [
        {
            "kind": "PRODUCT_FACT",
            "text": "Diễn đạt lại nội dung hàng hóa.",
            "evidence_ids": [],
            "fact_ids": [next(iter(user_registry(ctx)))],
        }
    ]
    assert not decode_answer(value, ctx)[1]
    value["claims"][0]["fact_ids"] = []
    assert decode_answer(value, ctx)[1]
    value["claims"][0]["fact_ids"] = ["Uwrong"]
    assert decode_answer(value, ctx)[1]


def test_backend_renders_s4_s5_and_deduplicates_citations_from_source_ids():
    rows = [{"id": str(i), "source_text": f"Quy định độc lập thứ {i}."} for i in range(5)]
    ctx = prepare_context(
        "Giải thích quy định.",
        {"matches": rows, "snapshot": "a"},
        "qa",
        GroqConfig(keys=("fixture",)),
    )
    value = main_answer(ctx, status="ANSWERED")
    value["claims"] = [
        {
            "kind": "LEGAL_ANALYSIS",
            "text": "Theo quy định thứ tư.",
            "evidence_ids": [ctx["sources"][3]["evidence_id"]],
            "fact_ids": [],
        },
        {
            "kind": "LEGAL_ANALYSIS",
            "text": "Đối chiếu quy định thứ năm.",
            "evidence_ids": [ctx["sources"][4]["evidence_id"], ctx["sources"][3]["evidence_id"]],
            "fact_ids": [],
        },
    ]
    generated, _ = run(ctx, [value])
    assert generated["validation"]["valid"]
    assert "[S4]" in generated["answer"]["answer"] and "[S5]" in generated["answer"]["answer"]
    assert [c["label"] for c in generated["answer"]["citations"]] == ["S4", "S5"]
    assert generated["answer"]["citations"][0]["quote"] == rows[3]["source_text"]


@pytest.mark.parametrize(
    "defect", ["unknown_id", "changed_snapshot", "changed_text", "manual_label"]
)
def test_invalid_or_stale_source_ids_fail_without_being_auto_completed(defect):
    ctx = context("Điện thoại mẫu Z.")
    value = main_answer(ctx)
    if defect == "unknown_id":
        value["claims"][0]["evidence_ids"] = ["Efake"]
    elif defect == "changed_snapshot":
        other = context(ctx["question"], snapshot="snapshot-b")
        value["claims"][0]["evidence_ids"] = [other["sources"][0]["evidence_id"]]
    elif defect == "changed_text":
        other = prepare_context(
            ctx["question"],
            {"matches": [{"id": "l", "source_text": "Khác"}], "snapshot": "snapshot-a"},
            "qa",
            GroqConfig(keys=("fixture",)),
        )
        value["claims"][0]["evidence_ids"] = [other["sources"][0]["evidence_id"]]
    else:
        value["claims"][0]["text"] += " [S4] [S5]"
    assert decode_answer(value, ctx)[1]


def test_missing_ancestor_citations_and_broken_graph_remain_blocked():
    ctx = context("Điện thoại mẫu Z.")
    bad = main_answer(ctx)
    bad["claims"][0]["evidence_ids"] = [ctx["sources"][0]["evidence_id"]]
    generated, _ = run(ctx, [bad, bad])
    assert generated["answer"]["status"] == "REQUIRES_REVIEW"
    ctx = context("Điện thoại mẫu Z.", broken=True)
    bad = main_answer(ctx)
    generated, _ = run(ctx, [bad, bad])
    assert generated["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"


def test_qa_does_not_require_a_product_category_or_add_an_unnecessary_review():
    ctx = context("Quy định được giải thích thế nào?", task="qa")
    generated, calls = run(ctx, [main_answer(ctx, status="ANSWERED")])
    assert generated["validation"]["valid"]
    assert generated["answer"]["status"] == "ANSWERED"
    assert len(calls) == 1


def test_old_registry_context_is_explicitly_rejected_and_must_be_rebuilt():
    ctx = context("Điện thoại mẫu Z.")
    ctx["response_protocol"] = "registry-v1"
    with pytest.raises(ValueError, match="dựng lại"):
        run(ctx, [])
