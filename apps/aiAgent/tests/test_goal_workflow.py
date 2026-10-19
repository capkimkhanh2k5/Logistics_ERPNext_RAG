"""Requested resolution, multiple items and reviewed conclusions share one contract."""

import copy
import json
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.answering import generate_answer
from rag.llm.context import prepare_context
from rag.llm.recovery import _gaps
from rag.llm.task_generation import _resolve_comparisons, _resolve_levels, review_jobs
from rag.llm.task_validation import decode_task_answer, item_context, item_quote_errors
from rag.llm.validation import _ownership_errors
from rag.retrieval.query_planning import QueryPlanner
from rag.retrieval.request_plan import explicit_level, referenced_codes, validate_request
from rag.utils.files import digest


def request(query, *, level=4, explain=False):
    result = {
        "items": [{"id": "I1", "anchor": "Dây A"}, {"id": "I2", "anchor": "Dây B"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "CLASSIFY",
                "level": level,
                "item_ids": ["I1", "I2"],
                "anchor": "Xác định nhóm HS",
                "required": True,
            }
        ],
    }
    if explain:
        result["objectives"].append(
            {
                "id": "G2",
                "kind": "EXPLAIN",
                "level": 0,
                "item_ids": ["I1", "I2"],
                "anchor": "giải thích kim loại nền",
                "required": True,
            }
        )
    return validate_request(query, result)


def context(*, explain=False, compare=False, requirements=False, detail_sources=True):
    query = (
        "Dây A bằng bạc 925; Dây B bằng thép mạ vàng. Xác định nhóm HS và giải thích kim loại nền."
    )
    rows = [
        {"id": "a4", "code": "7113", "level": 4, "source_text": "Đồ trang sức bằng kim loại quý."},
        {"id": "a6", "code": "711311", "level": 6, "source_text": "Bằng bạc."},
        {"id": "a8", "code": "71131190", "level": 8, "source_text": "Loại khác bằng bạc."},
        {
            "id": "b4",
            "code": "7117",
            "level": 4,
            "source_text": "Đồ trang sức làm bằng chất liệu khác.",
        },
        {"id": "b6", "code": "711719", "level": 6, "source_text": "Bằng kim loại cơ bản."},
        {"id": "b8", "code": "71171920", "level": 8, "source_text": "Đồ trang sức mạ điện."},
    ]
    edges = [
        {"source": a, "target": b, "relation": "CONTAINS"}
        for a, b in [("a4", "a6"), ("a6", "a8"), ("b4", "b6"), ("b6", "b8")]
    ]
    graph = GraphContext(rows, [], edges)
    planned = request(query, explain=explain)
    if requirements:
        assert not explain and not compare
        query += " Những thông số cần thiết để phân loại đến HS8?"
        planned["objectives"].append(
            {
                "id": "G2",
                "kind": "REQUIREMENTS",
                "level": 0,
                "item_ids": ["I1", "I2"],
                "anchor": "Những thông số cần thiết để phân loại đến HS8?",
                "required": True,
            }
        )
        planned = validate_request(query, planned)
    if compare:
        assert not explain
        query += " Hai mặt hàng có cùng mã HS8 hay không?"
        planned["objectives"].append(
            {
                "id": "G2",
                "kind": "COMPARE",
                "level": 8,
                "item_ids": ["I1", "I2"],
                "anchor": "Hai mặt hàng có cùng mã HS8 hay không?",
                "required": True,
            }
        )
        planned = validate_request(query, planned)
    plan = {"request": planned, "query_hash": digest(query)}
    result = {
        "snapshot": "fixture",
        "query_plan": plan,
        "hs_candidates": [rows[2], rows[5]],
        "matches": rows if detail_sources else [r for r in rows if r["level"] == 4],
    }
    return prepare_context(query, result, "auto", GroqConfig(keys=("fixture",)), graph)


def model_answer(ctx):
    rows = []
    for item, code in [("I1", "7113"), ("I2", "7117")]:
        source = next(s for s in ctx["sources"] if s.get("code") == code)
        rows.append(
            {
                "objective_id": "G1",
                "item_id": item,
                "status": "RECOMMENDATION",
                "code": code,
                "claims": [
                    {
                        "kind": "CONCLUSION",
                        "text": "Phân loại theo kim loại nền thực tế.",
                        "evidence_ids": [source["evidence_id"]],
                        "fact_ids": [],
                    }
                ],
                "clarifications": [],
                "missing_legal_evidence": [],
            }
        )
    if len(ctx["request"]["objectives"]) > 1:
        rows.append(
            {
                "objective_id": "G2",
                "item_id": "",
                "status": "ANSWERED",
                "code": "",
                "claims": [
                    {
                        "kind": "LEGAL_ANALYSIS",
                        "text": "Kim loại nền quyết định hướng phân loại.",
                        "evidence_ids": [s["evidence_id"] for s in ctx["sources"]],
                        "fact_ids": [],
                    }
                ],
                "clarifications": [],
                "missing_legal_evidence": [],
            }
        )
    return {"results": rows, "evidence_gaps": []}


def model_reviews(ctx, main):
    rows, errors = decode_task_answer(main, ctx)
    assert not errors
    jobs, scopes = review_jobs(rows, ctx)
    reviews = []
    for job in jobs:
        scoped, row, _ = scopes[job["result_id"]]
        item = row["item_id"]
        quote = "Dây A bằng bạc 925" if item == "I1" else "Dây B bằng thép mạ vàng"
        statement = next(s for s in scoped["user_context"]["statements"] if quote in s["text"])
        proof = {"fact_ids": [statement["id"]], "user_quotes": [quote]}
        code = row["suggested_hs_code"]
        source = next(s for s in ctx["sources"] if s.get("code") == code)
        assessments = [
            {
                "code": c["code"],
                "assessment": "POSSIBLE" if c["code"] == code else "RULED_OUT",
                "evidence_ids": [
                    next(s["evidence_id"] for s in ctx["sources"] if s.get("code") == c["code"])
                ],
                **proof,
            }
            for c in scoped["candidate_evidence"]
        ]
        reviews.append(
            {
                "result_id": job["result_id"],
                "selected_code": code,
                "review": {
                    "status": "SUPPORTED",
                    "reason": "Kim loại nền phù hợp điều kiện nguồn.",
                    "condition_checks": [
                        {"evidence_id": source["evidence_id"], "assessment": "SATISFIED", **proof}
                    ],
                    "clarifications": [],
                    "missing_legal_evidence": [],
                    "candidate_assessments": assessments,
                    "branch_checks": [],
                },
            }
        )
    from rag.llm.analysis_review import analysis_jobs

    analyses = analysis_jobs(rows, ctx)
    return {
        "reviews": reviews,
        **(
            {
                "analysis_reviews": [
                    {
                        "result_id": job["result_id"],
                        "checks": [
                            {
                                "claim_index": c["claim_index"],
                                "assessment": "REFERENCE",
                                "evidence_ids": c["evidence_ids"],
                                "fact_ids": [],
                                "user_quotes": [],
                                "reason": "Giải thích điều kiện nguồn, không tự áp mã cho hàng hóa.",
                            }
                            for c in job["claims"]
                        ],
                    }
                    for job in analyses
                ]
            }
            if analyses
            else {}
        ),
    }


def run(ctx, outputs):
    calls, pending = [], iter(outputs)

    def complete(messages, schema, **kwargs):
        calls.append({"messages": copy.deepcopy(messages), "schema": schema})
        return {
            "content": json.dumps(next(pending), ensure_ascii=False),
            "finish_reason": "stop",
            "model": "fixture",
            "usage": {"total_tokens": 10},
        }

    return generate_answer(ctx, SimpleNamespace(complete=complete)), calls


def test_two_hs4_results_and_explanation_use_one_draft_and_one_batched_review():
    ctx = context(explain=True)
    main = model_answer(ctx)
    out, calls = run(ctx, [main, model_reviews(ctx, main)])
    assert len(calls) == 2
    assert out["validation"]["task_completion"]
    assert out["answer"]["status"] == "ANSWERED"
    assert [r["suggested_hs_code"] for r in out["answer"]["results"]] == ["7113", "7117", ""]
    assert all(r.get("review_valid") for r in out["answer"]["results"][:2])
    assert (
        calls[1]["schema"]["properties"]["reviews"]["items"]["properties"]["review"]["properties"][
            "branch_checks"
        ]["maxItems"]
        == 0
    )
    assert "7113" in out["answer"]["answer"] and "7117" in out["answer"]["answer"]


def test_missing_explanation_is_not_silently_accepted_as_complete():
    ctx = context(explain=True)
    main = model_answer(ctx)
    main["results"].pop()
    assert any("bao phủ" in e for e in decode_task_answer(main, ctx)[1])


@pytest.mark.parametrize(
    "change",
    ["duplicate", "unknown_item", "wrong_level", "hidden_hs8", "unknown_source", "other_item_fact"],
)
def test_goal_validation_rejects_invalid_item_resolution_and_unregistered_codes(change):
    ctx = context()
    main = model_answer(ctx)
    row = main["results"][0]
    if change == "duplicate":
        main["results"].append(copy.deepcopy(row))
    elif change == "unknown_item":
        row["item_id"] = "I8"
    elif change == "wrong_level":
        row["code"] = "71131190"
    elif change == "hidden_hs8":
        row["claims"][0]["text"] = "Mặt hàng được đề xuất mã 71131190."
    elif change == "unknown_source":
        row["claims"][0]["evidence_ids"] = ["Efake"]
    else:
        scoped = item_context(ctx, "I1", 4)
        other = next(
            s
            for s in ctx["user_context"]["statements"]
            if s["id"] not in {x["id"] for x in scoped["user_context"]["statements"]}
        )
        row["claims"][0].update(kind="PRODUCT_FACT", fact_ids=[other["id"]])
    assert decode_task_answer(main, ctx)[1]


def test_invalid_review_does_not_discard_independently_checked_other_item():
    ctx = context()
    main = model_answer(ctx)
    review = model_reviews(ctx, main)
    review["reviews"][0]["review"]["condition_checks"][0]["user_quotes"] = [
        "không do người dùng cung cấp"
    ]
    out, calls = run(ctx, [main, review, review])
    assert len(calls) == 3
    first, second = out["answer"]["results"]
    assert first["status"] == "REQUIRES_REVIEW" and not first["suggested_hs_code"]
    assert second["review_valid"] and second["suggested_hs_code"] == "7117"
    assert not out["validation"]["task_completion"]
    assert out["diagnostics"]["code"] == "SYSTEM_VALIDATION_ERROR"


def test_request_goals_are_anchored_and_share_existing_planning_call():
    ctx = context()
    payload = {"terms": [], "request": ctx["request"]}
    calls = []

    def complete(messages, schema):
        calls.append(schema)
        return {"content": json.dumps(payload), "finish_reason": "stop"}

    planner = QueryPlanner(
        SimpleNamespace(
            config=SimpleNamespace(model="fixture", fallback_model="fallback"), complete=complete
        )
    )
    plan = planner.plan(ctx["question"])
    planner.validate_plan(ctx["question"], plan)
    assert plan["request"] == ctx["request"] and len(calls) == 1
    payload["request"]["items"][0]["anchor"] = "invented"
    fallback = planner.plan(ctx["question"] + " ")
    assert fallback["status"] == "FALLBACK_RAW" and fallback["queries"] == [ctx["question"] + " "]
    assert fallback["request"] is None


def test_explicit_hs8_request_cannot_be_downgraded_to_hs4():
    q = "Dây A; Dây B. Xác định mã HS8"
    value = request("Dây A; Dây B. Xác định nhóm HS")
    value["objectives"][0]["anchor"] = "Xác định mã HS8"
    with pytest.raises(ValueError, match="level_changed"):
        validate_request(q, value)


def test_anchor_capitalization_resolves_to_unique_literal_user_span_without_new_facts():
    q = "Dây A; Dây B. hãy xác định nhóm HS"
    value = request("Dây A; Dây B. Xác định nhóm HS")
    resolved = validate_request(q, value)
    assert resolved["objectives"][0]["anchor"] == "xác định nhóm HS"
    assert value["objectives"][0]["anchor"] == "Xác định nhóm HS"


@pytest.mark.parametrize(
    "sentence",
    [
        "Thép không gỉ là kim loại cơ bản nên lớp mạ không quyết định nhóm.",
        "Kim loại cơ bản có thể được mạ điện.",
        "Văn bản nên được đọc cùng chú giải.",
    ],
)
def test_descriptive_ban_is_not_mistaken_for_addressing_the_user(sentence):
    assert not _ownership_errors(
        {
            "status": "ANSWERED",
            "answer": sentence,
            "missing_information": [],
            "missing_legal_evidence": [],
        }
    )


@pytest.mark.parametrize(
    "sentence",
    [
        "Bạn nên cung cấp vật liệu.",
        "Ban nen cung cap vat lieu.",
        "Bạn có thể cung cấp chú giải HS?",
        "Please provide the legal evidence.",
    ],
)
def test_actual_user_requests_still_respect_ownership_and_status(sentence):
    assert _ownership_errors(
        {
            "status": "ANSWERED",
            "answer": sentence,
            "missing_information": [],
            "missing_legal_evidence": [],
        }
    )


def test_whole_turn_fact_id_cannot_justify_a_quote_only_describing_other_item():
    ctx = context()
    scoped = item_context(ctx, "I1", 4)
    assert item_quote_errors(["thép mạ vàng"], scoped)
    assert not item_quote_errors(["bạc 925"], scoped)


def test_one_item_heading_choice_is_classification_not_just_comparison():
    q = "Xe này thuộc nhóm 8703 hay 8704? Xác định mã 8 chữ số nếu đủ dữ kiện."
    plan = {
        "items": [{"id": "I1", "anchor": "Xe này"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "COMPARE",
                "level": 4,
                "item_ids": ["I1"],
                "anchor": "Xe này thuộc nhóm 8703 hay 8704?",
                "required": True,
            },
            {
                "id": "G2",
                "kind": "CLASSIFY",
                "level": 8,
                "item_ids": ["I1"],
                "anchor": "Xác định mã 8 chữ số nếu đủ dữ kiện.",
                "required": False,
            },
        ],
    }
    resolved = validate_request(q, plan)
    assert [(g["kind"], g["level"]) for g in resolved["objectives"]] == [
        ("CLASSIFY", 4),
        ("CLASSIFY", 8),
    ]


def test_unqualified_classify_inherits_explicit_comparison_resolution():
    q = "Dây A; Dây B. Có cùng phân nhóm HS 6 chữ số hay không? Hãy phân loại từng sản phẩm."
    plan = request("Dây A; Dây B. Xác định nhóm HS")
    plan["objectives"] = [
        {
            "id": "G1",
            "kind": "COMPARE",
            "level": 6,
            "item_ids": ["I1", "I2"],
            "anchor": "Có cùng phân nhóm HS 6 chữ số hay không?",
            "required": True,
        },
        {
            "id": "G2",
            "kind": "CLASSIFY",
            "level": 8,
            "item_ids": ["I1", "I2"],
            "anchor": "Hãy phân loại từng sản phẩm.",
            "required": True,
        },
    ]
    assert validate_request(q, plan)["objectives"][1]["level"] == 6
    q += " Đề xuất mã HS8."
    plan["objectives"][1]["anchor"] = "Đề xuất mã HS8."
    assert validate_request(q, plan)["objectives"][1]["level"] == 8


def test_raw_evidence_ids_do_not_become_user_facing_citation_markers():
    ctx = context()
    main = model_answer(ctx)
    main["results"][0]["claims"][0]["text"] += " [E0123456789abcdef0123]"
    assert any("registry ID" in e for e in decode_task_answer(main, ctx)[1])


def test_valid_request_survives_invalid_numeric_search_hint_without_another_call():
    ctx = context()
    payload = {"terms": [{"anchor": "Dây A", "term": "7113"}], "request": ctx["request"]}
    calls = []

    def complete(messages, schema):
        calls.append(schema)
        return {"content": json.dumps(payload), "finish_reason": "stop"}

    planner = QueryPlanner(
        SimpleNamespace(
            config=SimpleNamespace(model="fixture", fallback_model="fallback"), complete=complete
        )
    )
    plan = planner.plan(ctx["question"])
    planner.validate_plan(ctx["question"], plan)
    assert plan["request"] == ctx["request"] and len(calls) == 1
    assert not plan["terms"] and plan["queries"] == [ctx["question"]]
    assert plan["hint_error"]["error_code"] == "invalid_search_hints_request_preserved"


def test_binary_comparison_uses_reviewed_headings_without_inventing_hs8():
    ctx = context(compare=True)
    main = model_answer(ctx)
    out, _ = run(ctx, [main, model_reviews(ctx, main)])
    comparison = out["answer"]["results"][-1]
    assert comparison["level"] == 8
    assert out["validation"]["task_completion"]
    assert comparison["derived_from_reviewed_results"]
    assert "7113" in comparison["answer"] and "7117" in comparison["answer"]
    assert "không thể dùng chung" in comparison["answer"]
    assert not comparison["suggested_hs_code"]


def test_comparison_cannot_complete_when_one_item_review_is_invalid():
    ctx = context(compare=True)
    main = model_answer(ctx)
    review = model_reviews(ctx, main)
    review["reviews"][0]["review"]["condition_checks"][0]["user_quotes"] = ["invented"]
    out, _ = run(ctx, [main, review, review])
    assert out["answer"]["results"][-1]["status"] == "REQUIRES_REVIEW"
    assert not out["validation"]["task_completion"]


def test_unresolved_required_heading_suppresses_irrelevant_detail_question():
    rows = [
        {
            "kind": "CLASSIFY",
            "item_id": "I1",
            "level": 4,
            "required": True,
            "status": "REQUIRES_REVIEW",
        },
        {
            "kind": "CLASSIFY",
            "item_id": "I1",
            "level": 8,
            "required": False,
            "status": "MISSING_PRODUCT_INFO",
            "missing_information": ["Dạng SEN?"],
            "suggested_hs_code": "",
        },
    ]
    resolved = _resolve_levels(rows)
    assert resolved[1]["status"] == "REQUIRES_REVIEW"
    assert not resolved[1]["missing_information"]


def test_comparison_prefers_available_detailed_review_over_earlier_coarse_result():
    ctx = context(compare=True)
    ctx["request"]["objectives"][-1]["level"] = 6
    rows = [
        {
            "result_id": f"R{n}",
            "objective_id": "G1",
            "item_id": item,
            "kind": "CLASSIFY",
            "level": len(code),
            "status": "RECOMMENDATION",
            "review_valid": True,
            "suggested_hs_code": code,
            "citations": [],
            "verified_path": [{"level": 4, "code": "7113"}, {"level": len(code), "code": code}],
        }
        for n, (item, code) in enumerate(
            [("I1", "7113"), ("I2", "7113"), ("I1", "711311"), ("I2", "711319")], 1
        )
    ]
    # Distinct objectives can request different resolutions for the same item.
    rows[2]["objective_id"] = rows[3]["objective_id"] = "G3"
    rows.append({"objective_id": "G2", "kind": "COMPARE", "status": "ANSWERED"})
    comparison = _resolve_comparisons(rows, ctx)[-1]
    assert comparison["status"] == "ANSWERED"
    assert "711311" in comparison["answer"] and "711319" in comparison["answer"]


@pytest.mark.parametrize(
    "value,code", [("87.03", "8703"), ("8471.30", "847130"), ("8471.30.20.", "84713020")]
)
def test_explicit_codes_keep_their_resolution_with_dotted_heading_format(value, code):
    assert referenced_codes(value) == {code}
    assert explicit_level("phân nhóm " + value) == len(code)


def test_unqualified_classify_inherits_resolution_of_explicit_subheading_code():
    q = "Dây A; Dây B. Cả hai thuộc phân nhóm 8471.30? Hướng phân loại từng máy."
    plan = request("Dây A; Dây B. Xác định nhóm HS")
    plan["objectives"][0].update(level=6, anchor="Cả hai thuộc phân nhóm 8471.30?")
    plan["objectives"].append(
        {**plan["objectives"][0], "id": "G2", "level": 8, "anchor": "Hướng phân loại từng máy."}
    )
    assert [g["level"] for g in validate_request(q, plan)["objectives"]] == [6, 6]


def test_explicit_smartphone_hs8_code_is_not_downgraded_by_a_heading_goal():
    q = "Dây A; Dây B. Hàng thuộc nhóm 8471 hay 8517? Có đủ điều kiện xem là smartphone 85171300 không?"
    plan = request("Dây A; Dây B. Xác định nhóm HS")
    plan["objectives"][0].update(anchor="Hàng thuộc nhóm 8471 hay 8517?")
    plan["objectives"].append(
        {
            **plan["objectives"][0],
            "id": "G2",
            "level": 8,
            "anchor": "Có đủ điều kiện xem là smartphone 85171300 không?",
        }
    )
    assert [g["level"] for g in validate_request(q, plan)["objectives"]] == [4, 8]


def test_detail_requirements_cannot_complete_with_heading_wording_alone():
    ctx = context(requirements=True, detail_sources=False)
    main = model_answer(ctx)
    out, calls = run(ctx, [main, model_reviews(ctx, main)])
    assert len(calls) == 2
    detail = out["answer"]["results"][-1]
    assert detail["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert not out["diagnostics"] and not out["validation"]["task_completion"]
    assert _gaps(ctx, out)[0]["codes"] == ["7113", "7117"]


def test_detail_requirements_use_packed_sources_with_verified_graph_paths():
    ctx = context(requirements=True)
    main = model_answer(ctx)
    assert ctx["detail_evidence"]
    rows, errors = decode_task_answer(main, ctx)
    assert not errors and rows[-1]["status"] == "ANSWERED"
    ctx["detail_evidence"] = [{"source_id": "fake", "chain": [{"code": "7113", "level": 4}]}]
    assert decode_task_answer(main, ctx)[0][-1]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"


def test_unresolved_code_comparison_can_be_repaired_without_accepting_an_applied_code():
    ctx = context()
    main = model_answer(ctx)
    for row in main["results"]:
        row.update(
            status="INSUFFICIENT_LEGAL_EVIDENCE",
            code="",
            missing_legal_evidence=["Thiếu căn cứ áp dụng."],
        )
        row["claims"][0]["text"] = "Chưa đủ căn cứ để kết luận thuộc nhóm 7113 hay 7117."
    repaired = copy.deepcopy(main)
    for row in repaired["results"]:
        row["claims"][0]["kind"] = "LEGAL_ANALYSIS"
    out, calls = run(ctx, [main, repaired])
    assert len(calls) == 2 and not out["diagnostics"]
    assert out["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert not any(r["suggested_hs_code"] for r in out["answer"]["results"])
    assert "LEGAL_ANALYSIS" in calls[1]["messages"][-1]["content"]


def test_conceptual_nature_question_becomes_explain_alongside_classify():
    q = "Xe A có động cơ xăng chỉ chạy máy phát. Xe này là xe thuần điện hay xe hybrid? Nên phân vào nhóm nào?"
    plan = {
        "items": [{"id": "I1", "anchor": "Xe A"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "CLASSIFY",
                "level": 4,
                "item_ids": ["I1"],
                "anchor": "Xe này là xe thuần điện hay xe hybrid?",
                "required": True,
            },
            {
                "id": "G2",
                "kind": "CLASSIFY",
                "level": 4,
                "item_ids": ["I1"],
                "anchor": "Nên phân vào nhóm nào?",
                "required": True,
            },
        ],
    }
    validated = validate_request(q, plan)["objectives"]
    assert [(g["kind"], g["level"]) for g in validated] == [("EXPLAIN", 0), ("CLASSIFY", 4)]


def test_sentence_and_decimal_splitting_keeps_clean_item_statements():
    from rag.llm.evidence import bind_user_context

    q = (
        "Máy A có khối lượng chính xác 10,000 kg; Máy B có khối lượng 10,100 kg. "
        "Cả hai máy đều có thuộc phân nhóm 8471.30 không?"
    )
    texts = [s["text"] for s in bind_user_context(q)["statements"]]
    assert "Máy A có khối lượng chính xác 10,000 kg" in texts
    assert "Máy B có khối lượng 10,100 kg" in texts
    assert not any(t.endswith("10") for t in texts)


def test_legal_analysis_hs8_reference_and_negated_competitor_code_are_allowed():
    from rag.llm.task_validation import code_claim_errors

    ctx = context()
    ctx["question"] += " Có đủ điều kiện xem là 71131190 hay không?"
    unresolved_claims = [
        {
            "kind": "LEGAL_ANALYSIS",
            "text": "Chưa đủ căn cứ để kết luận mặt hàng thuộc mã 7113.11.90 hay nhóm 7117.",
        },
        {
            "kind": "CONCLUSION",
            "text": "Chưa đủ thông tin hàng hóa để kết luận.",
        },
    ]
    assert not code_claim_errors(unresolved_claims, "", ctx)
    negated_conclusion = [
        {
            "kind": "CONCLUSION",
            "text": "Hàng không phân loại vào nhóm 7117 mà phải phân loại vào nhóm 7113.",
        }
    ]
    assert not code_claim_errors(negated_conclusion, "7113", ctx)
    passive_parenthetical_exclusion = [
        {
            "kind": "CONCLUSION",
            "text": (
                "Theo Chú giải 2 Phần XVII, các thiết bị điện thuộc Chương 85 không được phân loại "
                "là bộ phận theo các nhóm xe của Phần XVII (như 8708)."
            ),
        }
    ]
    assert not code_claim_errors(passive_parenthetical_exclusion, "8507", ctx)


def test_non_classify_item_id_canonicalization_and_registered_hs8_in_explain():
    ctx = context(explain=True)
    for c in ctx["candidate_evidence"]:
        c["code"] = "71131190" if c["code"] == "7113" else "71171920"
        c["hierarchy"]["chain"].append({"code": c["code"], "level": 8})
    ctx["request"]["objectives"][0]["level"] = 8
    main = model_answer(ctx)
    main["results"][0]["code"] = "71131190"
    main["results"][1]["code"] = "71171920"
    main["results"][2]["item_id"] = "I1"
    main["results"][2]["claims"][0]["text"] = (
        "Kim loại nền quyết định phân loại Dây A vào mã 7113.11.90 và Dây B vào mã 7117.19.20."
    )
    rows, errors = decode_task_answer(main, ctx)
    assert not errors
    assert rows[2]["item_id"] == ""
    assert rows[2]["depends_on"] == [["G1", "I1"], ["G1", "I2"]]


def test_collective_multi_item_question_becomes_compare_and_resolves_from_reviews():
    q = "Dây A; Dây B. Cả hai có được phân loại vào phân nhóm 7113.11 hay không? Hướng phân loại từng dây."
    plan = request("Dây A; Dây B. Xác định nhóm HS")
    plan["objectives"][0].update(
        level=6, anchor="Cả hai có được phân loại vào phân nhóm 7113.11 hay không?"
    )
    plan["objectives"].append(
        {**plan["objectives"][0], "id": "G2", "level": 8, "anchor": "Hướng phân loại từng dây."}
    )
    validated = validate_request(q, plan)["objectives"]
    assert [(g["kind"], g["level"]) for g in validated] == [("COMPARE", 6), ("CLASSIFY", 6)]


def test_required_detail_missing_product_info_is_preserved_when_heading_also_needs_info():
    rows = [
        {
            "kind": "CLASSIFY",
            "item_id": "I1",
            "level": 4,
            "required": True,
            "valid": True,
            "status": "MISSING_PRODUCT_INFO",
            "answer": "Cần xác định chức năng chính giữa 8471 và 8517.",
            "missing_information": ["Chức năng chính của thiết bị là gì?"],
            "suggested_hs_code": "",
        },
        {
            "kind": "CLASSIFY",
            "item_id": "I1",
            "level": 8,
            "required": True,
            "valid": True,
            "status": "MISSING_PRODUCT_INFO",
            "answer": "Tiêu chí điện thoại thông minh phụ thuộc thiết kế chủ yếu.",
            "missing_information": ["Thiết bị có thiết kế chủ yếu làm điện thoại di động không?"],
            "suggested_hs_code": "",
        },
    ]
    resolved = _resolve_levels(rows)
    assert resolved[1]["status"] == "MISSING_PRODUCT_INFO"
    assert "Tiêu chí điện thoại thông minh" in resolved[1]["answer"]


def test_threshold_violation_and_explain_exclusion_with_registered_codes_are_allowed():
    from rag.llm.task_validation import code_claim_errors
    from rag.llm.validation import validate_answer

    ctx = context(explain=True)
    ctx["question"] += (
        " Có thuộc phân nhóm 7113.11 hay nhóm 8708 không? Có đủ điều kiện mã 71131190 không?"
    )
    threshold_claim = [
        {
            "kind": "CONCLUSION",
            "text": (
                "Hàng vượt quá giới hạn của phân nhóm 7113.11 nên bị loại trừ khỏi 7113.11, "
                "thuộc nhóm 7117."
            ),
        }
    ]
    assert not code_claim_errors(threshold_claim, "7117", ctx)
    explain_claim = [
        {
            "kind": "CONCLUSION",
            "text": "Hàng phải phân loại theo nhóm 7113 thay vì nhóm 7117.",
        }
    ]
    assert not code_claim_errors(explain_claim, "", ctx, {"7113"})
    scoped = item_context(ctx, "I1", 8)
    eval_answer = {
        "status": "MISSING_PRODUCT_INFO",
        "answer": "Để đánh giá điều kiện phân loại vào mã 71131190 [S1], chưa đủ thông tin để kết luận.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [{"label": "S1", "quote": ctx["sources"][0]["text"]}],
        "missing_information": ["Trạng thái cụ thể của sản phẩm là gì?"],
        "missing_legal_evidence": [],
    }
    assert validate_answer(eval_answer, scoped)["valid"]
