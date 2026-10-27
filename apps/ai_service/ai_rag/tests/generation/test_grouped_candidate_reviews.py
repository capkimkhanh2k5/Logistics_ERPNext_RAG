import copy
import json
from types import SimpleNamespace

import pytest

from rag.llm.contracts.errors import LLMError
from rag.llm.generation.answering import generate_answer
from rag.llm.generation.shortlist import expand_rows
from rag.llm.generation.task_generation import _review_payload, review_jobs
from rag.llm.validation.task_validation import decode_task_answer
from tests.test_conditional_candidates import conditional_fixture
from tests.test_goal_workflow import context, model_answer, model_reviews, run


def test_grouped_proof_expands_to_same_individual_checks_without_another_call():
    ctx, draft, review = conditional_fixture()
    for row in review["reviews"]:
        values = row["review"]["candidate_assessments"]
        row["review"]["candidate_group_assessments"] = [
            {
                **{k: v for k, v in values[0].items() if k != "code"},
                "codes": [v["code"] for v in values] + [values[-1]["code"]],
            }
        ]
        row["review"]["candidate_assessments"] = []
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2 and not out["diagnostics"]
    assert all(c["rank"] == 1 and c["tied"] for c in out["answer"]["hs_candidates"])


@pytest.mark.parametrize("defect", ["missing", "duplicate", "wrong_proof"])
def test_grouping_never_weakens_per_code_coverage_or_exclusion_evidence(defect):
    ctx, draft, review = conditional_fixture()
    rows, _ = decode_task_answer(draft, ctx)
    expanded, _ = expand_rows(rows, ctx)
    _, scopes = review_jobs(expanded, ctx)
    for row in review["reviews"]:
        assessments = row["review"]["candidate_assessments"]
        if defect == "missing":
            assessments.pop()
        elif defect == "duplicate":
            assessments.append(copy.deepcopy(assessments[0]))
        else:
            assessments[0].update(
                assessment="RULED_OUT", evidence_ids=[], fact_ids=[], user_quotes=[]
            )
    checked, errors = _review_payload(review, ctx, scopes)
    assert errors and not checked


def test_unconfirmed_reason_may_reference_all_reviewed_branches_without_claiming_a_code():
    ctx, draft, review = conditional_fixture()
    for row in review["reviews"]:
        row["review"]["reason"] = "Chưa đủ dữ kiện để phân loại vào 87038018 hay 87038098."
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2 and not out["diagnostics"]
    assert not out["answer"]["suggested_hs_code"]


def test_legal_gap_does_not_create_leaf_review_jobs_from_auxiliary_codes():
    ctx, draft, _ = conditional_fixture()
    row = draft["results"][0]
    row.update(
        status="INSUFFICIENT_LEGAL_EVIDENCE",
        clarifications=[],
        missing_legal_evidence=["Thiếu chú giải áp dụng."],
    )
    row["claims"][0]["text"] = "Ngữ cảnh chưa có đủ căn cứ giải thích cách áp dụng."
    from rag.llm.review.analysis_review import analysis_jobs

    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    jobs, _ = review_jobs(rows, ctx)
    assert not jobs
    analyses = analysis_jobs(rows, ctx)
    review = {
        "reviews": [],
        "analysis_reviews": [
            {
                "result_id": job["result_id"],
                "checks": [
                    {
                        "claim_index": claim["claim_index"],
                        "assessment": "INSUFFICIENT_LEGAL_EVIDENCE",
                        "evidence_ids": [],
                        "fact_ids": [],
                        "user_quotes": [],
                        "reason": "Nguồn hiện tại chưa đủ căn cứ giải thích cách áp dụng.",
                    }
                    for claim in job["claims"]
                ],
            }
            for job in analyses
        ],
    }
    out, calls = run(ctx, [draft, review])
    assert len(calls) == 2
    assert out["answer"]["status"] == "INSUFFICIENT_LEGAL_EVIDENCE"
    assert not out["answer"]["hs_candidates"]


def test_provider_error_during_repair_keeps_independently_validated_results():
    ctx = context()
    draft = model_answer(ctx)
    review = model_reviews(ctx, draft)
    review["reviews"][1]["review"]["reason"] = ""
    pending = iter([draft, review])
    calls = []

    def complete(messages, schema, **kwargs):
        calls.append(schema)
        if len(calls) == 3:
            raise LLMError(503, "fixture", provider="fixture")
        return {"content": json.dumps(next(pending)), "finish_reason": "stop", "model": "fixture"}

    out = generate_answer(ctx, SimpleNamespace(complete=complete))
    first, second = out["answer"]["results"]
    assert first["review_valid"] and first["suggested_hs_code"] == "7113"
    assert not second["review_valid"] and not second["suggested_hs_code"]
    assert out["diagnostics"] and len(calls) == 3
