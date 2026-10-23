"""Prompt ownership, shared policy, and actual request assembly contracts."""

import ast
import copy
import importlib
import json
import re
from pathlib import Path

import pytest

from rag.llm.generation.task_generation import _review_payload, review_jobs
from rag.llm.validation.task_validation import decode_task_answer
from rag.prompts.core.policy import EVIDENCE_POLICY
from rag.prompts.core.repair import format_task_repair_prompt, repair_instruction
from rag.prompts.core.system import SYSTEM_PROMPT
from rag.prompts.generation.task_answering import (
    ANALYSIS_REVIEW_SCHEMA,
    TASK_REVIEW_PROMPT,
    TASK_SYSTEM_PROMPT,
)
from rag.prompts.review.product_review import PRODUCT_REVIEW_PROMPT, REVIEW_POLICY
from tests.test_goal_workflow import context, model_answer, model_reviews, run

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "rag"


def test_prompt_schema_and_repair_definitions_stay_in_prompt_package():
    violations = []
    for path in RUNTIME.rglob("*.py"):
        if path.is_relative_to(RUNTIME / "prompts"):
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id.endswith(("_PROMPT", "_SCHEMA")):
                        violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: {target.id}")
            if not isinstance(node, ast.Dict):
                if (
                    isinstance(node, ast.keyword)
                    and node.arg == "task_instruction"
                    and isinstance(node.value, (ast.Constant, ast.JoinedStr))
                ):
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: inline task")
                continue
            fields = {
                key.value: value
                for key, value in zip(node.keys, node.values)
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
            if "repair_instruction" in fields:
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: inline repair")
            if isinstance(fields.get("task_instruction"), (ast.Constant, ast.JoinedStr)):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: inline task")
            if getattr(fields.get("role"), "value", None) == "system":
                content = fields.get("content")
                # Templates may be imported or assembled by a prompt-package helper.
                if isinstance(content, (ast.Constant, ast.JoinedStr)):
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}: inline system")
    assert not violations, "\n".join(violations)


@pytest.mark.parametrize("path", sorted((RUNTIME / "prompts").rglob("*.py")))
def test_runtime_prompt_constants_have_no_business_examples(path):
    module = importlib.import_module(".".join(path.relative_to(ROOT).with_suffix("").parts))
    prohibited = re.compile(
        r"ví dụ|chẳng hạn|for example|\be\.g\.|\b(?:CKD|CBU|diesel|hybrid|camera)\b"
        r"|sạc ngoài|vĩnh viễn|\b(?:MacBook|iPhone|VinFast)\b",
        re.IGNORECASE,
    )
    for name, value in vars(module).items():
        if name.isupper() and isinstance(value, (str, dict)):
            assert not prohibited.search(json.dumps(value, ensure_ascii=False)), (path.name, name)


def test_single_and_batch_protocols_share_evidence_and_review_policies():
    assert SYSTEM_PROMPT.startswith(EVIDENCE_POLICY)
    assert TASK_SYSTEM_PROMPT.startswith(EVIDENCE_POLICY)
    assert PRODUCT_REVIEW_PROMPT.startswith(EVIDENCE_POLICY)
    assert PRODUCT_REVIEW_PROMPT.count(REVIEW_POLICY) == 1
    assert TASK_REVIEW_PROMPT.startswith(EVIDENCE_POLICY)
    assert TASK_REVIEW_PROMPT.count(REVIEW_POLICY) == 1


def test_review_rejects_a_condition_proven_with_another_items_quote():
    ctx = context()
    draft = model_answer(ctx)
    rows, errors = decode_task_answer(draft, ctx)
    assert not errors
    _, scopes = review_jobs(rows, ctx)
    valid = {"reviews": model_reviews(ctx, draft)["reviews"]}
    checked, errors = _review_payload(valid, ctx, scopes)
    assert not errors and len(checked) == 2
    malformed = copy.deepcopy(valid)
    wrong_condition = copy.deepcopy(malformed["reviews"][1]["review"]["condition_checks"][0])
    wrong_condition["assessment"] = "CONTRADICTED"
    malformed["reviews"][0]["review"]["condition_checks"].append(wrong_condition)
    rejected, errors = _review_payload(malformed, ctx, scopes)
    assert malformed["reviews"][0]["result_id"] not in rejected
    assert any("mặt hàng khác" in error for error in errors)
    # The original item-scoped evidence is still accepted by the same validator.
    repaired, errors = _review_payload(valid, ctx, scopes)
    assert not errors and set(repaired) == set(checked)


def test_analysis_is_in_existing_batch_request_with_central_schema():
    ctx = context(explain=True)
    draft = model_answer(ctx)
    result, calls = run(ctx, [draft, model_reviews(ctx, draft)])
    assert result["validation"]["task_completion"]
    assert len(calls) == 2  # Draft and review, including the legal analysis jobs.
    assert calls[0]["messages"][0]["content"].startswith(TASK_SYSTEM_PROMPT)
    from rag.prompts.generation.task_answering import task_review_prompt

    assert calls[1]["messages"][0]["content"] == task_review_prompt(
        classification=True, analysis=True
    )
    payload = json.loads(calls[1]["messages"][1]["content"])
    analysis = calls[1]["schema"]["properties"]["analysis_reviews"]
    assert analysis["type"] == "object"
    assert set(analysis["required"]) == {j["result_id"] for j in payload["analysis_jobs"]}
    checks = analysis["properties"]["R3"]["properties"]["checks"]
    assert set(checks["required"]) == {
        str(c["claim_index"]) for c in payload["analysis_jobs"][0]["claims"]
    }
    original = ANALYSIS_REVIEW_SCHEMA["items"]["properties"]["checks"]["items"]["properties"][
        "assessment"
    ]["enum"]
    assert all(
        item["properties"]["assessment"]["enum"] == original
        for item in checks["properties"].values()
    )
    assert "analysis_reviews" in calls[1]["schema"]["required"]
    payload = json.loads(calls[1]["messages"][1]["content"])
    assert payload["analysis_jobs"]
    assert all("review_conditions" not in job for job in payload["jobs"])
    review_props = calls[1]["schema"]["properties"]["reviews"]["properties"]["R1"]["properties"][
        "review"
    ]["properties"]
    assert "branch_checks" not in review_props
    branch = calls[1]["schema"]["properties"]["comparison_reviews"]["properties"]["C1"][
        "properties"
    ]["branch_checks"]
    assert "condition_ids" in branch["items"]["properties"]
    assert "criterion_quote" not in branch["items"]["properties"]
    assert "condition_ids" in review_props["clarifications"]["items"]["properties"]


def test_repair_feedback_keeps_instruction_separate_from_diagnostics():
    errors = [
        "R1.C2: [CLAIM_FACT_UNPROVEN] Thuộc tính chưa có chứng minh.",
        "/results/0/code: Giá trị ngoài phạm vi.",
        "[SOURCE_CONDITION_UNPROVEN] Điều kiện chưa được chứng minh.",
    ]
    feedback = json.loads(format_task_repair_prompt(errors, phase="product_review"))
    expected = {
        "phase": "product_review",
        "repair_instruction": repair_instruction("product_review"),
        "repair_errors": [
            {
                "code": "CLAIM_FACT_UNPROVEN",
                "path": "R1.C2",
                "message": "Thuộc tính chưa có chứng minh.",
            },
            {
                "code": "VALIDATION_ERROR",
                "path": "/results/0/code",
                "message": "Giá trị ngoài phạm vi.",
            },
            {
                "code": "SOURCE_CONDITION_UNPROVEN",
                "path": "",
                "message": "Điều kiện chưa được chứng minh.",
            },
        ],
    }

    assert feedback["phase"] == expected["phase"]
    assert feedback["repair_instruction"] == expected["repair_instruction"]
    assert [
        {key: row[key] for key in ("code", "path", "message")} for row in feedback["repair_errors"]
    ] == expected["repair_errors"]
    assert all(
        row["safe_action"] and row["owner"] and row["cause"] for row in feedback["repair_errors"]
    )


def test_validator_diagnostics_do_not_direct_status_selection_or_domain_questions():
    prohibited = re.compile(
        r"dùng (?:MISSING_|REQUIRES_|INSUFFICIENT_)|hãy |sửa trích|phải đối chiếu|; giữ đúng", re.I
    )
    violations = []
    for path in (RUNTIME / "llm").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if prohibited.search(node.value):
                    violations.append(f"{path.name}:{node.lineno}")
    assert not violations, violations


def test_maintained_rag_readmes_link_to_existing_local_files():
    missing = []
    for path in [
        ROOT / "README-RAG.md",
        RUNTIME / "ReadMe.md",
        RUNTIME / "prompts/README.md",
        ROOT / "config/README.md",
        ROOT / "docs/GenerationFlow/GenerationFlow.md",
    ]:
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#", 1)[0]
            if not (path.parent / target).exists():
                missing.append(f"{path.relative_to(ROOT)}: {link}")
    assert not missing, "\n".join(missing)
