"""Backend contract regressions with synthetic predicates; no provider or HS evaluation."""

from copy import deepcopy

import pytest

from rag.llm.contracts.errors import ContractIssue
from rag.llm.contracts.repair_dispatch import canonicalize, dispatch
from rag.llm.evidence.conditions import condition_span_registry
from rag.llm.evidence.ledger import build_ledger
from rag.llm.review.proof_resolution import resolve_review
from rag.llm.validation.proof import evaluate_proof


def context():
    return {
        "question": "Mặt hàng A có thuộc tính x.\nĐính chính thuộc tính x chưa biết.",
        "request": {"items": [{"id": "I1", "anchor": "Mặt hàng A"}], "objectives": []},
        "candidate_evidence": [],
        "sources": [
            {
                "id": "source",
                "label": "S1",
                "evidence_id": "E1",
                "text": "Thuộc tính x phải đáp ứng điều kiện nguồn.",
            }
        ],
        "user_context": {
            "statements": [
                {"id": "U1", "turn": 1, "text": "Mặt hàng A có thuộc tính x."},
                {"id": "U2", "turn": 2, "text": "Đính chính thuộc tính x chưa biết."},
            ]
        },
        "proof_required": True,
        "scoped_item_id": "I1",
    }


def entry(key="f1", *, modality="ASSERTED", fact_id="U1", supersedes=()):
    return {
        "key": key,
        "item_id": "I1",
        "attribute": "thuộc tính x",
        "value": "x" if modality == "ASSERTED" else "",
        "polarity": "AFFIRMED" if modality == "ASSERTED" else "UNSPECIFIED",
        "modality": modality,
        "fact_id": fact_id,
        "quote": "Mặt hàng A có thuộc tính x."
        if fact_id == "U1"
        else "Đính chính thuộc tính x chưa biết."
        if fact_id == "U2"
        else "",
        "supersedes": list(supersedes),
        "correction_quote": "Đính chính thuộc tính x chưa biết." if supersedes else "",
    }


def prepared(*, unknown=False):
    ctx = context()
    rows, errors = build_ledger(
        [entry(modality="UNKNOWN" if unknown else "ASSERTED", fact_id="" if unknown else "U1")], ctx
    )
    assert not errors
    ctx["user_context"]["fact_ledger"] = rows
    return ctx


def proof(ctx, state="PROVEN", cause="NONE"):
    target = ctx["sources"][0]["text"]
    return {
        "target": target,
        "decomposition_review": "FAITHFUL_COMPLETE",
        "ledger_review": "CONSISTENT",
        "root": "n1",
        "nodes": [
            {
                "key": "n1",
                "operator": "ATOM",
                "kind": "PREDICATE",
                "text": target,
                "attribute": "thuộc tính x",
                "item_ids": ["I1"],
                "children": [],
                "evidence_ids": ["E1"],
                "condition_ids": [next(iter(condition_span_registry(ctx["sources"])))],
                "ledger_ids": [ctx["user_context"]["fact_ledger"][0]["id"]],
                "assessment": state,
                "cause": cause,
                "comparison": {
                    "left": "",
                    "right": "",
                    "left_unit": "",
                    "right_unit": "",
                    "operator": "NONE",
                },
            }
        ],
    }


def test_explicit_unknown_correction_supersedes_only_same_attribute():
    ctx = context()
    other = {**entry("f3"), "attribute": "thuộc tính khác"}
    rows, errors = build_ledger(
        [entry(), entry("f2", modality="UNKNOWN", fact_id="U2", supersedes=["f1"]), other], ctx
    )
    assert not errors
    assert [r["state"] for r in rows] == ["SUPERSEDED", "UNKNOWN", "ACTIVE"]


def test_conflict_does_not_choose_last_statement():
    rows, errors = build_ledger([entry(), entry("f2", modality="UNKNOWN", fact_id="U2")], context())
    assert not errors and {r["state"] for r in rows} == {"CONFLICT"}


def test_valid_binding_cannot_hide_changed_target_or_attribute():
    ctx = prepared()
    value = proof(ctx)
    _, errors = evaluate_proof(value, ctx, target="Một nhận định khác", product=True)
    assert errors
    value["nodes"][0]["attribute"] = "thuộc tính khác"
    _, errors = evaluate_proof(value, ctx, product=True)
    assert errors


def test_unknown_is_not_negation_and_does_not_satisfy_any():
    ctx = prepared(unknown=True)
    value = proof(ctx, "UNKNOWN", "MISSING_PRODUCT_FACT")
    node = value["nodes"][0]
    root = {**deepcopy(node), "key": "root", "operator": "NOT", "children": ["n1"]}
    value.update(root="root", nodes=[node, root])
    result, errors = evaluate_proof(value, ctx)
    assert not errors and result["state"] == "UNKNOWN"


@pytest.mark.parametrize(
    "operator, states, expected",
    [
        ("ALL", ["PROVEN", "UNKNOWN"], "UNKNOWN"),
        ("ANY", ["CONTRADICTED", "UNKNOWN"], "UNKNOWN"),
        ("ANY", ["PROVEN", "UNKNOWN"], "PROVEN"),
        ("EXCEPT", ["PROVEN", "UNKNOWN"], "UNKNOWN"),
        ("EXCEPT", ["PROVEN", "PROVEN"], "CONTRADICTED"),
    ],
)
def test_logic_aggregates_without_filling_missing_facts(operator, states, expected):
    ctx = prepared()
    value = proof(ctx)
    nodes = []
    for index, state in enumerate(states):
        node = {
            **deepcopy(value["nodes"][0]),
            "key": f"child{index}",
            "assessment": state,
            "cause": "UNRESOLVED_APPLICATION" if state == "UNKNOWN" else "NONE",
        }
        nodes.append(node)
    root = {
        **deepcopy(value["nodes"][0]),
        "key": "root",
        "operator": operator,
        "children": [n["key"] for n in nodes],
        "assessment": expected,
        "cause": "UNRESOLVED_APPLICATION" if expected == "UNKNOWN" else "NONE",
    }
    value.update(root="root", nodes=[*nodes, root])
    result, errors = evaluate_proof(value, ctx)
    assert not errors and result["state"] == expected


def test_cycle_never_becomes_proven():
    ctx = prepared()
    value = proof(ctx)
    value["nodes"][0].update(operator="NOT", children=["n1"])
    assert evaluate_proof(value, ctx)[1]


def test_valid_unknown_proof_downgrades_without_another_model_request():
    ctx = prepared(unknown=True)
    check = {
        "assessment": "SATISFIED",
        "evidence_id": "E1",
        "fact_ids": [],
        "user_quotes": [],
        "proof": proof(ctx, "UNKNOWN", "MISSING_PRODUCT_FACT"),
    }
    result = resolve_review(
        {
            "status": "SUPPORTED",
            "reason": "Không được giữ nhận định này.",
            "condition_checks": [check],
            "candidate_assessments": [],
            "branch_checks": [],
            "clarifications": [],
            "missing_legal_evidence": [],
        },
        ctx,
    )
    assert result["status"] == "MISSING_PRODUCT_INFO"
    assert result["clarifications"][0]["condition_ids"]
    assert result["condition_checks"][0]["assessment"] == "MISSING_PRODUCT_INFO"


def test_dispatch_does_not_retry_binding_or_coverage_or_invent_semantic_status():
    errors = [
        ContractIssue("Binding invalid", code="CONDITION_REF_INVALID", path="R1/checks"),
        ContractIssue("Missing slot", code="REVIEW_SLOT_MISSING", path="R2/review"),
        ContractIssue("Proof incomplete", code="PROOF_INVALID", path="R3/proof"),
    ]
    plan = dispatch(errors, "product_review")
    assert plan["withhold"] == errors[:2] and plan["repair"] == errors[2:]
    value, changes = canonicalize({"fact_ids": ["U1", "U1"], "code": "1234.56.78"}, ["12345678"])
    assert value == {"fact_ids": ["U1"], "code": "12345678"} and len(changes) == 2


def test_legacy_context_is_rebuilt_for_model_wire_without_public_labels():
    from rag.llm.context.normalization import normalize_context

    ctx = context()
    ctx.update(task="qa", messages=[{"role": "system", "content": "old context"}])
    ctx.pop("request")
    normal = normalize_context(ctx)
    assert normal["response_protocol"] == "registry-v2" and normal["proof_required"]
    assert normal["normalized_from"] == "legacy-public-context"
    assert "condition_spans" in normal["messages"][1]["content"]
    assert ctx.get("response_protocol") is None


def test_one_invalid_comparison_does_not_drop_an_independent_matrix():
    from rag.llm.review.review_packet import expand_comparisons

    matrix = {
        "comparison_id": "C1",
        "candidate_assessments": [
            {
                "code": "1234",
                "assessment": "POSSIBLE",
                "evidence_ids": [],
                "fact_ids": [],
                "user_quotes": [],
            }
        ],
        "branch_checks": [],
    }
    raw = {
        "reviews": [{"result_id": "R1", "review": {}}, {"result_id": "R2", "review": {}}],
        "comparison_reviews": [matrix],
    }
    expanded, errors = expand_comparisons(raw, {"R1": "C1", "R2": "C2"})
    assert [r["result_id"] for r in expanded["reviews"]] == ["R1"]
    assert errors and all(str(e).startswith("R2:") for e in errors)


def test_grouped_exclusion_cannot_borrow_another_members_domain():
    from rag.llm.review.review_slots import expand_review_slots

    layout = {
        "reviews": [],
        "analysis_reviews": {},
        "comparison_reviews": {"C1": ["1234", "5678"]},
        "candidate_domains": {"C1": {"1234": ["E1"], "5678": ["E2"]}},
    }
    raw = {
        "reviews": [],
        "comparison_reviews": [
            {
                "comparison_id": "C1",
                "candidate_group_assessments": [
                    {
                        "codes": ["1234", "5678"],
                        "assessment": "RULED_OUT",
                        "decisive_evidence_ids": ["E1"],
                    }
                ],
                "branch_checks": [],
            }
        ],
    }
    expanded, errors = expand_review_slots(raw, layout)
    assert len(expanded["comparison_reviews"][0]["candidate_assessments"]) == 2
    assert any(e.diagnostic["code"] == "EXCLUSION_SOURCE_MISMATCH" for e in errors)


def test_malformed_proof_does_not_create_a_product_question():
    ctx = prepared(unknown=True)
    review = {
        "status": "SUPPORTED",
        "reason": "Chờ kiểm tra.",
        "condition_checks": [{"assessment": "SATISFIED", "proof": {}}],
        "clarifications": [],
        "missing_legal_evidence": [],
    }
    result = resolve_review(review, ctx)
    assert result["status"] == "SUPPORTED" and not result["clarifications"]
    # The unchanged hypothesis must still fail the required proof validator.
    assert evaluate_proof(result["condition_checks"][0]["proof"], ctx)[1]


def test_schema_builders_are_idempotent_and_accept_well_formed_json_schema():
    from jsonschema import Draft202012Validator

    from rag.prompts.schemas.answer import MODEL_ANSWER_SCHEMA, MODEL_PRODUCT_REVIEW_SCHEMA
    from rag.prompts.schemas.proof import ledger_schema, proof_schema

    for base in (MODEL_ANSWER_SCHEMA, MODEL_PRODUCT_REVIEW_SCHEMA):
        wire = proof_schema(base)
        assert wire == proof_schema(wire)
        Draft202012Validator.check_schema(wire)
    Draft202012Validator.check_schema(proof_schema(ledger_schema(MODEL_ANSWER_SCHEMA, ["I1"])))


def test_effective_grouped_wire_contains_proof_and_fixed_job_keys():
    from jsonschema import Draft202012Validator

    from rag.llm.generation.task_generation import review_jobs
    from rag.llm.review.review_packet import review_packet
    from rag.llm.validation.task_validation import decode_task_answer
    from rag.prompts.generation.task_answering import TASK_REVIEW_SCHEMA
    from tests.test_goal_workflow import context as source_context
    from tests.test_goal_workflow import model_answer

    ctx = source_context()
    rows, errors = decode_task_answer(model_answer(ctx), ctx)
    assert not errors
    jobs, _ = review_jobs(rows, ctx)
    payload = {
        "jobs": jobs,
        "analysis_jobs": [],
        "sources": ctx["sources"],
        "user_context": ctx["user_context"],
    }
    packet, wire, _ = review_packet(payload, TASK_REVIEW_SCHEMA)
    Draft202012Validator.check_schema(wire)
    assert set(wire["properties"]["reviews"]["required"]) == {job["result_id"] for job in jobs}
    assert packet["review_slots"]["candidate_domains"]
    for group in wire["properties"]["comparison_reviews"]["properties"].values():
        fields = group["properties"]
        assert "candidate_assessments" not in fields
        assert "proof_key" in fields["candidate_group_assessments"]["items"]["required"]


def test_proof_catalogue_binds_independent_owners_and_rejects_ambiguous_keys():
    from rag.llm.evidence.catalogue import expand_proofs

    value = proof(prepared())
    payload = {
        "proof_catalogue": [{"key": "good", "proof": value}],
        "reviews": {"R1": {"proof_key": "good"}, "R2": {"proof_key": "missing"}},
    }
    bound, errors = expand_proofs(payload)
    assert bound["reviews"]["R1"]["proof"] == value
    assert bound["reviews"]["R2"]["proof"] is None
    assert len(errors) == 1 and "/R2/" in errors[0].diagnostic["path"]
    payload["proof_catalogue"].append({"key": "good", "proof": value})
    assert len(expand_proofs(payload)[1]) == 2


def test_question_proof_cannot_ask_for_another_registered_attribute():
    from rag.llm.evidence.evidence import clarification_errors

    ctx = prepared(unknown=True)
    value = proof(ctx, "UNKNOWN", "MISSING_PRODUCT_FACT")
    value["nodes"][0]["attribute"] = "thuộc tính khác"
    question = {
        "question": "Vui lòng cho biết thuộc tính khác.",
        "attribute": "thuộc tính khác",
        "evidence_ids": ["E1"],
        "proof": value,
    }
    assert clarification_errors([question], ctx)


def test_structural_error_scoped_to_one_result_never_enters_semantic_repair():
    result = dispatch(["R1: /review/proof: Thiếu trường bắt buộc: root"], "product_review")
    assert result["withhold"] and not result["repair"]


def test_missing_result_skeleton_does_not_reuse_a_retained_result_id():
    from rag.llm.generation.task_generation import _fill_missing

    ctx = context()
    ctx["request"]["objectives"] = [
        {"id": "G1", "kind": "CLASSIFY", "level": 4, "item_ids": ["I1"], "required": True},
        {"id": "G2", "kind": "EXPLAIN", "level": 0, "item_ids": ["I1"], "required": True},
    ]
    rows = [{"result_id": "R2", "objective_id": "G2", "item_id": ""}]
    filled = _fill_missing(rows, ctx)
    assert {r["result_id"] for r in filled} == {"R2", "R3"}


def test_predicate_identity_does_not_change_with_model_keys_or_proof_state():
    ctx = prepared()
    proven = proof(ctx)
    unknown = proof(ctx, "UNKNOWN", "UNRESOLVED_APPLICATION")
    unknown["root"] = "renamed"
    unknown["nodes"][0]["key"] = "renamed"
    first, errors = evaluate_proof(proven, ctx)
    assert not errors
    second, errors = evaluate_proof(unknown, ctx)
    assert not errors
    assert first["predicate_ids"] == second["predicate_ids"] and first["id"] != second["id"]


def test_ledger_never_materializes_a_value_absent_from_user_words():
    bad = {**entry(), "value": "giá trị do model suy thêm"}
    assert build_ledger([bad], context())[1]


def test_invalid_draft_proof_shape_isolated_to_its_result():
    from rag.llm.validation.task_validation import decode_task_answer
    from tests.test_goal_workflow import context as source_context
    from tests.test_goal_workflow import model_answer

    ctx = source_context()
    raw = model_answer(ctx)
    raw["results"][0]["claims"][0]["proof"] = None
    rows, errors = decode_task_answer(raw, ctx)
    assert errors and [row["result_id"] for row in rows] == ["R2"]


def test_ledger_revision_unlocks_only_the_drafts_that_use_changed_facts():
    from rag.llm.evidence.ledger import ledger_dependencies_changed

    before = [
        {"id": "L1", "state": "ACTIVE", "supersedes": []},
        {"id": "L2", "state": "ACTIVE", "supersedes": []},
    ]
    after = [
        {"id": "L1", "state": "SUPERSEDED", "supersedes": []},
        {"id": "L2", "state": "ACTIVE", "supersedes": []},
    ]
    assert ledger_dependencies_changed({"proof": {"ledger_ids": ["L1"]}}, before, after)
    assert not ledger_dependencies_changed({"proof": {"ledger_ids": ["L2"]}}, before, after)
