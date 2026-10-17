"""Recovery uses real graph relations, preserves prior results and shares the call cap."""

import copy
import json
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.answering import generate_answer
from rag.llm.context import prepare_context
from rag.llm.recovery import recover_answer
from rag.retrieval.evidence_recovery import MAX_RECOVERY_SOURCES, recover_evidence
from rag.utils.files import digest


def fixture():
    query = "Drone thuộc 8806 hay 8525? Những thông số nào cần để phân loại HS8?"
    rows = [
        {"id": "h", "code": "8806", "level": 4, "source_text": "Phương tiện bay không người lái."},
        {
            "id": "p",
            "code": "880621",
            "level": 6,
            "source_text": "Trọng lượng cất cánh tối đa không quá 250 g.",
        },
        {
            "id": "l",
            "code": "88062100",
            "level": 8,
            "source_text": "Trọng lượng cất cánh tối đa không quá 250 g.",
        },
    ]
    edges = [
        {"source": a, "target": b, "relation": "CONTAINS"} for a, b in [("h", "p"), ("p", "l")]
    ]
    graph = GraphContext(rows, [], edges)
    request = {
        "items": [{"id": "I1", "anchor": "Drone"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "CLASSIFY",
                "level": 4,
                "item_ids": ["I1"],
                "anchor": "Drone thuộc 8806 hay 8525?",
                "required": True,
            },
            {
                "id": "G2",
                "kind": "REQUIREMENTS",
                "level": 8,
                "item_ids": ["I1"],
                "anchor": "Những thông số nào cần để phân loại HS8?",
                "required": True,
            },
        ],
    }
    result = {
        "snapshot": "s",
        "matches": [rows[0]],
        "package": [rows[0]],
        "query_plan": {"request": request, "query_hash": digest(query)},
    }
    config = GroqConfig(keys=("fixture",))
    ctx = prepare_context(query, result, "auto", config, graph)
    gap = {
        "anchor": "Drone",
        "codes": ["8806"],
        "query": "ngưỡng trọng lượng cất cánh tối đa",
        "reason": "Thiếu điều kiện phân nhóm trong context.",
    }
    return query, graph, result, config, ctx, gap


def draft(ctx, *, complete=False):
    heading = next(s for s in ctx["sources"] if s.get("code") == "8806")
    source = next(s for s in ctx["sources"] if s.get("code") == "880621") if complete else heading
    first = {
        "objective_id": "G1",
        "item_id": "I1",
        "status": "RECOMMENDATION",
        "code": "8806",
        "claims": [
            {
                "kind": "CONCLUSION",
                "text": "Thiết bị là phương tiện bay không người lái.",
                "evidence_ids": [heading["evidence_id"]],
                "fact_ids": [],
            }
        ],
        "clarifications": [],
        "missing_legal_evidence": [],
    }
    second = {
        "objective_id": "G2",
        "item_id": "",
        "status": "ANSWERED" if complete else "INSUFFICIENT_LEGAL_EVIDENCE",
        "code": "",
        "claims": [
            {
                "kind": "LEGAL_ANALYSIS",
                "text": "Cần xác định trọng lượng cất cánh tối đa theo các ngưỡng nguồn."
                if complete
                else "Ngữ cảnh chưa có các điều kiện phân nhóm để liệt kê đầy đủ.",
                "evidence_ids": [source["evidence_id"]],
                "fact_ids": [],
            }
        ],
        "clarifications": [],
        "missing_legal_evidence": []
        if complete
        else ["Điều kiện phân nhóm theo trọng lượng cất cánh tối đa."],
    }
    return {"results": [first, second], "evidence_gaps": [] if complete else [fixture()[-1]]}


def approved(ctx):
    source = next(s for s in ctx["sources"] if s.get("code") == "8806")
    fact = next(s for s in ctx["user_context"]["statements"] if "Drone" in s["text"])
    proof = {"fact_ids": [fact["id"]], "user_quotes": ["Drone"]}
    return {
        "reviews": [
            {
                "result_id": "R1",
                "selected_code": "8806",
                "review": {
                    "status": "SUPPORTED",
                    "reason": "Đối tượng là phương tiện bay không người lái.",
                    "condition_checks": [
                        {"evidence_id": source["evidence_id"], "assessment": "SATISFIED", **proof}
                    ],
                    "clarifications": [],
                    "missing_legal_evidence": [],
                    "candidate_assessments": [
                        {
                            "code": "8806",
                            "assessment": "POSSIBLE",
                            "evidence_ids": [source["evidence_id"]],
                            **proof,
                        }
                    ],
                    "branch_checks": [],
                },
            }
        ]
    }


def client(outputs, config):
    calls, pending = [], iter(outputs)

    def complete(messages, schema, **kwargs):
        calls.append(schema)
        return {
            "content": json.dumps(next(pending), ensure_ascii=False),
            "finish_reason": "stop",
            "model": "fixture",
            "usage": {"total_tokens": 7},
        }

    return SimpleNamespace(config=config, complete=complete), calls


def test_source_recovery_traverses_contains_and_never_replans_with_llm():
    q, graph, result, _, ctx, gap = fixture()
    retriever = SimpleNamespace(
        unified_search=lambda *a, **kw: pytest.fail("Graph lookup is enough")
    )
    recovered, meta = recover_evidence(q, result, ctx, [gap], retriever, graph)
    assert recovered and meta["llm_planner_calls"] == 0
    assert set(meta["new_source_ids"]) == {"p", "l"}
    assert recovered["query_plan"] == result["query_plan"]
    assert q == ctx["question"]


def test_single_recovery_round_finishes_remaining_requirement_without_changing_user_facts():
    q, graph, result, config, ctx, gap = fixture()
    retrieved, _ = recover_evidence(q, result, ctx, [gap], SimpleNamespace(), graph)
    ctx2 = prepare_context(q, retrieved, "auto", config, graph)
    provider, calls = client(
        [draft(ctx), approved(ctx), draft(ctx2, complete=True), approved(ctx2)], config
    )
    initial = generate_answer(ctx, provider)
    assert not initial["validation"]["task_completion"]
    final_ctx, final = recover_answer(ctx, initial, result, provider, SimpleNamespace(), graph)
    assert len(calls) == 4 and final["generation"]["application_calls"] == 4
    assert final["validation"]["task_completion"]
    assert final_ctx["user_context"] == ctx["user_context"]
    assert final["generation"]["recovery"]["rounds"] == 1
    _, same = recover_answer(final_ctx, final, result, provider, SimpleNamespace(), graph)
    assert same is final and len(calls) == 4


@pytest.mark.parametrize(
    "defect", ["invented_anchor", "invented_code", "snapshot", "no_new_sources"]
)
def test_invalid_or_unproductive_recovery_stops_without_issuing_codes(defect):
    q, graph, result, _, ctx, gap = fixture()
    result, gap = copy.deepcopy(result), copy.deepcopy(gap)
    if defect == "invented_anchor":
        gap["anchor"] = "not in the question"
    elif defect == "invented_code":
        gap["codes"] = ["99999999"]
    elif defect == "snapshot":
        result["snapshot"] = "other"
    else:
        ctx["sources"] += [{"id": "p"}, {"id": "l"}]
    recovered, meta = recover_evidence(q, result, ctx, [gap], SimpleNamespace(), graph)
    assert recovered is None and meta.get("reason")


def test_completed_goals_product_questions_and_system_errors_do_not_trigger_recovery():
    _, graph, result, config, ctx, _ = fixture()
    for completed, diagnostic, gaps in [
        (True, {}, [fixture()[-1]]),
        (False, {"code": "SYSTEM_VALIDATION_ERROR"}, [fixture()[-1]]),
        (False, {}, []),
    ]:
        generated = {
            "answer": {"results": []},
            "validation": {"task_completion": completed},
            "diagnostics": diagnostic,
            "generation": {"evidence_gaps": gaps},
        }
        provider = SimpleNamespace(
            config=config, complete=lambda *a, **kw: pytest.fail("Must not call model")
        )
        assert (
            recover_answer(ctx, generated, result, provider, SimpleNamespace(), graph)[1]
            is generated
        )


def test_recovery_source_budget_does_not_grow_with_whole_chapter():
    q, graph, result, _, ctx, gap = fixture()
    for index in range(MAX_RECOVERY_SOURCES * 2):
        sid = f"extra-{index}"
        graph.records[sid] = {"id": sid, "source_text": "Nguồn trong nhánh đối chứng."}
        graph.children["h"].add(sid)
    recovered, meta = recover_evidence(q, result, ctx, [gap], SimpleNamespace(), graph)
    assert recovered and len(meta["new_source_ids"]) == MAX_RECOVERY_SOURCES


def test_shared_budget_prevents_recovery_from_resetting_draft_review_repair_limit():
    _, graph, result, config, ctx, _ = fixture()
    provider, calls = client([draft(ctx), approved(ctx)], config)
    initial = generate_answer(ctx, provider)
    initial["generation"]["remaining_calls"] = 0
    _, final = recover_answer(ctx, initial, result, provider, SimpleNamespace(), graph)
    assert final["generation"]["recovery"]["reason"] == "CALL_BUDGET_EXHAUSTED"
    assert len(calls) == 2


def test_product_fact_gap_does_not_trigger_retrieval_even_if_model_suggests_evidence_gap():
    _, graph, result, config, ctx, gap = fixture()
    generated = {
        "answer": {"results": [{"required": True, "status": "MISSING_PRODUCT_INFO"}]},
        "validation": {"task_completion": False},
        "generation": {"evidence_gaps": [gap]},
        "diagnostics": {},
    }
    provider = SimpleNamespace(
        config=config, complete=lambda *a, **kw: pytest.fail("No extra decision call")
    )
    assert (
        recover_answer(ctx, generated, result, provider, SimpleNamespace(), graph)[1] is generated
    )


def test_retained_result_after_recovery_clears_stale_diagnostic_for_that_result():
    q, graph, result, config, ctx, gap = fixture()
    retrieved, _ = recover_evidence(q, result, ctx, [gap], SimpleNamespace(), graph)
    ctx2 = prepare_context(q, retrieved, "auto", config, graph)
    bad_review = copy.deepcopy(approved(ctx2))
    bad_review["reviews"][0]["review"]["reason"] = ""
    provider, _ = client(
        [draft(ctx), approved(ctx), draft(ctx2, complete=True), bad_review, bad_review], config
    )
    initial = generate_answer(ctx, provider)
    _, final = recover_answer(ctx, initial, result, provider, SimpleNamespace(), graph)
    assert final["answer"]["results"][0].get("retained_after_recovery")
    assert final["validation"]["task_completion"]
    assert not final["diagnostics"]

