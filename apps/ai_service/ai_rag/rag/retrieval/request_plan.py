"""Traceable request goals, separate from product facts and legal conclusions."""

import re
from copy import deepcopy

from jsonschema import validate

from rag.prompts.planning.query_planning import REQUEST_SCHEMA
from rag.utils.files import digest


def canonical_anchor(query: str, anchor: str) -> str:
    if anchor in query:
        return anchor
    matches = list(re.finditer(re.escape(anchor), query, re.I))
    if len(matches) != 1:
        raise ValueError("untraceable_request_anchor")
    return matches[0][0]


def explicit_level(text: str) -> int | None:
    match = re.search(r"(?:HS\s*|mã\s*)([468])\b|([468])\s*(?:chữ\s*)?số", text, re.I)
    if match:
        return int(match[1] or match[2])
    code = re.search(r"(?:nhóm|HS|mã)\s*(\d[\d.]*)", text, re.I)
    codes = referenced_codes(code[1].rstrip(".")) if code else set()
    if not codes:
        codes = {c for c in referenced_codes(text) if len(c) in {6, 8}}
    return len(next(iter(codes))) if len(codes) == 1 else None


def _resolve_goal_scope(goals: list[dict], query: str = "") -> None:
    for goal in goals:
        position = query.find(goal["anchor"])
        prefix = re.split(r"[.!?;\n]", query[:position])[-1] if position >= 0 else ""
        question_context = prefix[-100:] + goal["anchor"]
        method_choice = bool(
            re.search(
                r"(?:có\s+(?:thể|được)\s+|được\s+(?:phép\s+)?)lựa\s+chọn", question_context, re.I
            )
        )
        if (
            goal["kind"] == "CLASSIFY"
            and (goal["level"] == 0 or method_choice)
            and not re.search(r"\b(?:mã|nhóm|hs)\b|\d", goal["anchor"], re.I)
            and re.search(
                r"phân\s*loại.+(?:riêng\s*(?:biệt|lẻ)|phân\s*loại\s+theo|phương\s*pháp)",
                goal["anchor"],
                re.I,
            )
        ):
            goal["kind"] = "EXPLAIN"
            goal["level"] = 0
            continue
        if (
            goal["kind"] == "COMPARE"
            and goal["level"]
            and len(goal["item_ids"]) == 1
            and re.search(r"thuộc.*(?:hay|hoặc)", goal["anchor"], re.I)
        ):
            if len([c for c in referenced_codes(goal["anchor"]) if len(c) == goal["level"]]) >= 2:
                goal["kind"] = "CLASSIFY"
                continue
        if (
            goal["kind"] == "CLASSIFY"
            and len(goal["item_ids"]) >= 2
            and re.search(
                r"\b(?:cả\s+hai|tất\s+cả|cùng\s+(?:thuộc|được\s+phân\s*loại|mã|nhóm|phân\s*nhóm))\b",
                goal["anchor"],
                re.I,
            )
            and any(
                other is not goal
                and other["kind"] == "CLASSIFY"
                and set(other["item_ids"]) == set(goal["item_ids"])
                for other in goals
            )
        ):
            goal["kind"] = "COMPARE"
            continue
        if (
            goal["kind"] == "CLASSIFY"
            and not explicit_level(goal["anchor"])
            and not referenced_codes(goal["anchor"])
            and not re.search(r"\b(?:nhóm|phân\s*nhóm|mã|hs|phân\s*loại)\b", goal["anchor"], re.I)
            and re.search(r"\b(?:hay|hoặc)\b", goal["anchor"], re.I)
            and any(
                other is not goal
                and other["kind"] == "CLASSIFY"
                and set(other["item_ids"]) & set(goal["item_ids"])
                for other in goals
            )
        ):
            goal["kind"] = "EXPLAIN"
            goal["level"] = 0
            continue
        if (
            goal["kind"] != "CLASSIFY"
            or goal["level"] != 8
            or explicit_level(goal["anchor"])
            or re.search(r"\bmã\b|chi tiết", goal["anchor"], re.I)
        ):
            continue
        explicit = {
            explicit_level(g["anchor"])
            for g in goals
            if g["kind"] in {"CLASSIFY", "COMPARE"} and set(g["item_ids"]) == set(goal["item_ids"])
        }
        concrete = [level for level in explicit if level is not None]
        if concrete:
            goal["level"] = max(concrete)


def validate_request(query: str, value: dict) -> dict:
    validate(value, REQUEST_SCHEMA)
    value = deepcopy(value)
    items = {row["id"]: row for row in value["items"]}
    goals = {row["id"]: row for row in value["objectives"]}
    if len(items) != len(value["items"]) or len(goals) != len(value["objectives"]):
        raise ValueError("duplicate_request_ids")
    for row in [*items.values(), *goals.values()]:
        row["anchor"] = canonical_anchor(query, row["anchor"])
    _resolve_goal_scope(list(goals.values()), query)
    _complete_classification_goals(value)
    goals = {row["id"]: row for row in value["objectives"]}
    if not any(g["required"] for g in goals.values()):
        raise ValueError("request_needs_required_objective")
    if sum(len(g["item_ids"]) if g["kind"] == "CLASSIFY" else 1 for g in goals.values()) > 32:
        raise ValueError("request_result_budget_exceeded")
    for goal in goals.values():
        if not set(goal["item_ids"]) <= items.keys():
            raise ValueError("unknown_request_item")
        if goal["kind"] == "CLASSIFY" and (not goal["item_ids"] or not goal["level"]):
            raise ValueError("classification_needs_items_and_level")
        level = explicit_level(goal["anchor"])
        if goal["kind"] == "CLASSIFY" and level and level != goal["level"]:
            raise ValueError("requested_level_changed")
    return deepcopy(value)


def _complete_classification_goals(request: dict) -> None:
    """Restore explicit classification requests inside nonclassification anchors.

    This is intent coverage only. It neither chooses goods nor derives a legal code.
    Historical text outside the planner's selected objectives cannot add a task.
    """
    goals = request["objectives"]
    for goal in list(goals):
        if goal["kind"] not in {"EXPLAIN", "COMPARE"} or not goal["item_ids"]:
            continue
        signal = re.search(
            r"(?:đề\s+xuất\s+(?:hướng\s+)?phân\s*loại|(?:hãy|yêu\s+cầu)\s+phân\s*loại\s+từng\s+(?:mặt\s*hàng|sản\s*phẩm))",
            goal["anchor"],
            re.I,
        )
        if not signal or re.search(
            r"(?:(?:không|chưa|đừng)\s+(?:cần\s+|yêu\s+cầu\s+)?|(?:để|nhằm)\s+)$",
            goal["anchor"][: signal.start()],
            re.I,
        ):
            continue
        if re.search(
            r"(?:không|chưa)\s+(?:cần|yêu\s+cầu)\s+(?:chốt|đề\s+xuất|xác\s+định)\s+mã",
            goal["anchor"],
            re.I,
        ):
            continue
        covered = {
            item for other in goals if other["kind"] == "CLASSIFY" for item in other["item_ids"]
        }
        missing = [item for item in goal["item_ids"] if item not in covered]
        if not missing:
            continue
        levels = {
            other["level"]
            for other in goals
            if other["kind"] == "COMPARE"
            and other["level"]
            and set(other["item_ids"]) & set(missing)
        }
        level = explicit_level(goal["anchor"]) or (next(iter(levels)) if len(levels) == 1 else 8)
        available = next(
            (f"G{i}" for i in range(1, 13) if all(g["id"] != f"G{i}" for g in goals)), None
        )
        if available is None:
            raise ValueError("request_objective_budget_exceeded")
        goals.append(
            {
                "id": available,
                "kind": "CLASSIFY",
                "level": level,
                "item_ids": missing,
                "anchor": goal["anchor"],
                "required": goal["required"],
            }
        )


def request_from_plan(query: str, plan: dict) -> dict | None:
    value = plan.get("request")
    if value is None:
        return None
    if plan.get("query_hash") != digest(query):
        raise ValueError("request_query_mismatch")
    return validate_request(query, value)


def referenced_codes(query: str) -> set[str]:
    return {
        re.sub(r"\D", "", m[0])
        for m in re.finditer(
            r"(?<!\d)(?:\d{4}(?:\.\d{2}(?:\.?\d{2})?)?|\d{2}\.\d{2}|\d{6}|\d{8})(?!\d|\.\d)",
            query,
        )
    }
