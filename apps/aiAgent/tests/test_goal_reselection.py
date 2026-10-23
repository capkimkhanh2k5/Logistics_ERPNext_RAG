"""An independently proven graph peer can replace a contradicted initial candidate."""

import copy

import pytest

from config.settings import GroqConfig
from rag.graph.context import GraphContext
from rag.llm.context.builder import prepare_context
from rag.llm.generation.task_generation import review_jobs
from rag.llm.validation.task_validation import decode_task_answer
from rag.utils.files import digest
from tests.test_goal_workflow import run


def fixture():
    query = "Xe điện SUV 7 chỗ, dạng CKD đầy đủ. Hãy đề xuất mã HS8."
    rows = [
        {
            "id": "h",
            "code": "8703",
            "level": 4,
            "source_text": "Ô tô thiết kế chủ yếu để chở người.",
        },
        {
            "id": "p",
            "code": "870380",
            "level": 6,
            "source_text": "Chỉ sử dụng động cơ điện để tạo động lực.",
        },
        {
            "id": "c",
            "code": "87038018",
            "level": 8,
            "source_text": "Ô tô SUV và loại khác, trừ ô tô van.",
        },
        {
            "id": "u",
            "code": "87038098",
            "level": 8,
            "source_text": "Ô tô SUV và loại khác, trừ ô tô van.",
        },
        {"id": "ckd", "source_text": "Dạng CKD:", "role": "context"},
        {"id": "cbu", "source_text": "Loại nguyên chiếc:", "role": "context"},
        {
            "id": "decoy",
            "code": "87038099",
            "level": 8,
            "source_text": "Không có đường graph xác minh.",
        },
    ]
    edges = [
        {"source": a, "target": b, "relation": rel}
        for a, b, rel in [
            ("h", "p", "CONTAINS"),
            ("p", "c", "CONTAINS"),
            ("p", "u", "CONTAINS"),
            ("ckd", "c", "CONTEXT_FOR"),
            ("cbu", "u", "CONTEXT_FOR"),
        ]
    ]
    request = {
        "items": [{"id": "I1", "anchor": "Xe điện SUV 7 chỗ"}],
        "objectives": [
            {
                "id": "G1",
                "kind": "CLASSIFY",
                "level": 8,
                "item_ids": ["I1"],
                "anchor": "Hãy đề xuất mã HS8",
                "required": True,
            }
        ],
    }
    graph = GraphContext(rows, [], edges)
    ctx = prepare_context(
        query,
        {
            "snapshot": "s",
            "query_plan": {"request": request, "query_hash": digest(query)},
            "hs_candidates": [rows[3]],
            "matches": [rows[3]],
        },
        "auto",
        GroqConfig(keys=("fixture",)),
        graph,
    )
    main = {
        "results": [
            {
                "objective_id": "G1",
                "item_id": "I1",
                "status": "RECOMMENDATION",
                "code": "87038098",
                "claims": [
                    {
                        "kind": "CONCLUSION",
                        "text": "Đề xuất theo nhánh đã truy xuất.",
                        "evidence_ids": [s["evidence_id"] for s in ctx["sources"]],
                        "fact_ids": [],
                    }
                ],
                "clarifications": [],
                "missing_legal_evidence": [],
            }
        ],
        "evidence_gaps": [],
    }
    decoded, errors = decode_task_answer(main, ctx)
    assert not errors
    jobs, scopes = review_jobs(decoded, ctx)
    scoped, _, _ = scopes["R1"]
    fact = next(s for s in scoped["user_context"]["statements"] if "dạng CKD đầy đủ" in s["text"])
    proof = {"fact_ids": [fact["id"]], "user_quotes": ["dạng CKD đầy đủ"]}
    candidate = next(c for c in scoped["candidate_evidence"] if c["code"] == "87038018")
    refs = {s["label"]: s["evidence_id"] for s in ctx["sources"]}
    options = jobs[0]["required_branch_groups"][0]["branch_options"]
    review = {
        "reviews": [
            {
                "result_id": "R1",
                "selected_code": "87038018",
                "review": {
                    "status": "SUPPORTED",
                    "reason": "Dạng CKD đã được người dùng xác nhận, phù hợp nhánh đang xét.",
                    "condition_checks": [
                        {"evidence_id": refs[label], "assessment": "SATISFIED", **proof}
                        for label in candidate["required_citation_labels"]
                    ],
                    "clarifications": [],
                    "missing_legal_evidence": [],
                    "candidate_assessments": [
                        {
                            "code": c["code"],
                            "assessment": "POSSIBLE" if c["code"] == "87038018" else "RULED_OUT",
                            "evidence_ids": [
                                refs[label] for label in c["required_citation_labels"]
                            ],
                            **proof,
                        }
                        for c in scoped["candidate_evidence"]
                    ],
                    "branch_checks": [
                        {
                            "parent_code": "870380",
                            "attribute": "dạng nhập khẩu",
                            "assessment": "KNOWN",
                            "evidence_ids": list({e for o in options for e in o["evidence_ids"]}),
                            **proof,
                        }
                    ],
                },
            }
        ]
    }
    return ctx, main, review


def test_eligible_sibling_reselection_requires_complete_independent_proof():
    ctx, main, review = fixture()
    out, calls = run(ctx, [main, review])
    assert len(calls) == 2
    assert out["answer"]["suggested_hs_code"] == "87038018"
    assert out["answer"]["results"][0]["reselected_from"] == "87038098"
    assert out["validation"]["task_completion"]
    assert out["answer"]["results"][0]["selected_source"]["source_id"] == "c"
    assert out["answer"]["results"][0]["selected_source"]["snapshot"] == ctx["snapshot"]
    assert "87038099" not in ctx["allowed_hs_codes"]


@pytest.mark.parametrize(
    "defect", ["unverified_decoy", "wrong_fact", "missing_branch", "other_candidate_still_possible"]
)
def test_reselection_does_not_release_codes_with_incomplete_or_fabricated_proof(defect):
    ctx, main, review = fixture()
    review = copy.deepcopy(review)
    row = review["reviews"][0]
    if defect == "unverified_decoy":
        row["selected_code"] = "87038099"
    elif defect == "wrong_fact":
        row["review"]["condition_checks"][0]["user_quotes"] = ["Dạng CBU"]
    elif defect == "missing_branch":
        row["review"]["branch_checks"] = []
    else:
        for c in row["review"]["candidate_assessments"]:
            c["assessment"] = "POSSIBLE"
    out, calls = run(ctx, [main, review, review])
    assert len(calls) == 3
    assert out["answer"]["status"] == "REQUIRES_REVIEW"
    assert not out["answer"]["suggested_hs_code"]
    assert not out["validation"]["task_completion"]


def test_missing_peer_is_not_silently_removed_when_catalogue_is_bounded():
    ctx, main, review = fixture()
    group = next(g for g in ctx["candidate_comparison"] if g["parent_code"] == "870380")
    group["codes"].append("87038099")
    group["missing_codes"].append("87038099")
    out, calls = run(ctx, [main, review, review])
    assert len(calls) == 3
    assert not out["validation"]["task_completion"]
    assert out["answer"]["results"][0]["status"] == "REQUIRES_REVIEW"


def test_verified_ancestors_in_selected_classification_are_not_other_proposals():
    ctx, main, _ = fixture()
    main["results"][0]["claims"][0]["text"] = (
        "Theo phân loại, hàng thuộc nhóm 8703, phân nhóm 870380 và mã 87038098."
    )
    assert not decode_task_answer(main, ctx)[1]


def test_review_reason_cannot_publish_a_second_unreviewed_code():
    ctx, main, review = fixture()
    review["reviews"][0]["review"]["reason"] = "Đề xuất mã 87038098 và 87038018."
    out, _ = run(ctx, [main, review, review])
    assert not out["answer"]["suggested_hs_code"]


def test_comparison_peer_exposes_required_citation_ids_and_accepts_trailing_punctuation():
    import json

    ctx, main, review = fixture()
    payload = json.loads(ctx["messages"][1]["content"])
    peer = next(c for c in payload["comparison_candidates"] if c["code"] == "87038018")
    assert peer["required_citation_evidence_ids"]
    review["reviews"][0]["review"]["condition_checks"][0]["user_quotes"] = ["dạng CKD đầy đủ."]
    out, calls = run(ctx, [main, review])
    assert len(calls) == 2
    assert out["answer"]["suggested_hs_code"] == "87038018"


def test_split_branch_checks_do_not_silently_promote_missing_to_known():
    ctx, main, review = fixture()
    b0 = review["reviews"][0]["review"]["branch_checks"][0]
    eids = b0["evidence_ids"]
    review["reviews"][0]["review"]["branch_checks"] = [
        {
            "parent_code": "870380",
            "attribute": "dạng CKD",
            "assessment": "KNOWN",
            "evidence_ids": [eids[0]],
            "fact_ids": b0["fact_ids"],
            "user_quotes": b0["user_quotes"],
        },
        {
            "parent_code": "870380",
            "attribute": "dạng CBU",
            "assessment": "MISSING",
            "evidence_ids": eids[1:],
            "fact_ids": [],
            "user_quotes": [],
        },
    ]
    repaired = copy.deepcopy(review)
    repaired["reviews"][0]["review"]["branch_checks"][1].update(
        assessment="KNOWN", fact_ids=b0["fact_ids"], user_quotes=b0["user_quotes"]
    )
    out, calls = run(ctx, [main, review, repaired])
    assert len(calls) == 3
    assert out["answer"]["suggested_hs_code"] == "87038018"


def test_non_supported_reselection_keeps_sources_but_drops_unreviewed_application():
    ctx, main, review = fixture()
    main["results"][0]["claims"].insert(
        0,
        {
            "kind": "LEGAL_ANALYSIS",
            "text": "Theo GIR 2(a), bộ linh kiện CKD đầy đủ được phân loại theo nhóm xe hoàn chỉnh.",
            "evidence_ids": [ctx["sources"][0]["evidence_id"]],
            "fact_ids": [],
        },
    )
    bad = copy.deepcopy(review)
    bad["reviews"][0]["review"]["status"] = "REQUIRES_REVIEW"
    out, calls = run(ctx, [main, bad, bad])
    assert len(calls) == 3
    assert out["answer"]["status"] == "REQUIRES_REVIEW"
    assert not out["answer"]["suggested_hs_code"]
    # The cited fixture contains no GIR 2(a): retaining this draft claim would
    # publish an unreviewed legal application after its review failed.
    assert "GIR 2(a)" not in out["answer"]["answer"]
    assert "Nguồn tham khảo" in out["answer"]["answer"]
