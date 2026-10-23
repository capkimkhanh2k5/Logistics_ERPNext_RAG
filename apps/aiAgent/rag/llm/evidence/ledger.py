"""Validate attributed facts and explicit supersession without a product vocabulary."""

from collections import defaultdict
from copy import deepcopy

from rag.llm.contracts.errors import ContractIssue
from rag.llm.validation.answer import schema_errors
from rag.prompts.schemas.proof import FACT_LEDGER_SCHEMA, WIRE_LEDGER_SCHEMA
from rag.utils.files import digest


def attribute_key(value: str) -> str:
    return " ".join(value.casefold().split())


def build_ledger(entries, context: dict) -> tuple[list[dict], list[str]]:
    entries, binding_errors = materialize_ledger(entries, context)
    if binding_errors:
        return [], binding_errors
    errors = schema_errors(entries, FACT_LEDGER_SCHEMA)
    if errors:
        return [], [
            ContractIssue(str(e), code="LEDGER_INVALID", path="fact_ledger") for e in errors
        ]
    statements = {s["id"]: s for s in context["user_context"]["statements"]}
    items = {i["id"] for i in context.get("request", {}).get("items", [])} or {""}
    rows, keys = [], {}

    def error(message, index):
        errors.append(ContractIssue(message, code="LEDGER_INVALID", path=f"fact_ledger/{index}"))

    for index, entry in enumerate(entries):
        if entry["key"] in keys or entry["item_id"] not in items:
            error("Ledger key hoặc chủ thể không hợp lệ.", index)
            continue
        statement = statements.get(entry["fact_id"])
        absent = entry["modality"] == "UNKNOWN" and not entry["fact_id"] and not entry["quote"]
        if not absent and (
            not statement or not entry["quote"] or entry["quote"] not in statement["text"]
        ):
            error("Ledger phải dẫn nguyên văn lời khai đã đăng ký.", index)
            continue
        if entry["modality"] == "ASSERTED" and (
            not entry["value"] or entry["polarity"] == "UNSPECIFIED"
        ):
            error("Lời khai xác định cần giá trị và chiều khẳng định/phủ định.", index)
        from rag.llm.validation.answer import LEGAL_INFORMATION, _folded, match_user_quote

        if entry["modality"] == "ASSERTED" and not match_user_quote(
            entry["value"], [entry["quote"]]
        ):
            error(
                "Giá trị ledger phải có nguyên văn trong lời khai, không suy thêm thuộc tính.",
                index,
            )
        if entry["modality"] == "UNKNOWN" and entry["value"]:
            error("Thuộc tính chưa biết phải giữ giá trị rỗng.", index)
        if entry["quote"] and LEGAL_INFORMATION.search(_folded(entry["quote"])):
            error("Lời người dùng về luật không trở thành thuộc tính hàng hóa/vụ việc.", index)
        if entry["modality"] != "ASSERTED" and entry["polarity"] != "UNSPECIFIED":
            error("Lời khai chưa xác định không trở thành khẳng định hoặc phủ định.", index)
        from rag.llm.validation.task_validation import item_context, item_quote_errors

        if context.get("request") and entry["quote"]:
            errors.extend(
                item_quote_errors([entry["quote"]], item_context(context, entry["item_id"], 0))
            )
        row = {
            **deepcopy(entry),
            "id": "L"
            + digest(
                [
                    entry["item_id"],
                    attribute_key(entry["attribute"]),
                    entry["value"],
                    entry["polarity"],
                    entry["modality"],
                    entry["fact_id"],
                    entry["quote"],
                ]
            )[:20],
            "turn": statement.get("turn", 1) if statement else 0,
            "position": statement.get("start", 0) + statement["text"].find(entry["quote"])
            if statement
            else -1,
            "state": "ACTIVE" if entry["modality"] == "ASSERTED" else entry["modality"],
        }
        keys[entry["key"]] = row
        rows.append(row)
    if len({row["id"] for row in rows}) != len(rows):
        error("Ledger lặp cùng dữ kiện dưới nhiều key.", 0)
    for index, row in enumerate(rows):
        old_ids = []
        for key in row["supersedes"]:
            old = keys.get(key)
            if (
                not old
                or old is row
                or old["item_id"] != row["item_id"]
                or attribute_key(old["attribute"]) != attribute_key(row["attribute"])
                or (old["turn"], old["position"]) >= (row["turn"], row["position"])
                or not row["correction_quote"]
                or row["correction_quote"] not in statements.get(row["fact_id"], {}).get("text", "")
                or row["modality"] not in {"ASSERTED", "UNKNOWN"}
            ):
                error(
                    "Supersedes cần đính chính có nguồn, cùng thuộc tính/chủ thể và ở lượt sau.",
                    index,
                )
                continue
            old_ids.append(old["id"])
        row["supersedes"] = old_ids
    superseded = {key for row in rows for key in row["supersedes"]}
    groups = defaultdict(list)
    for row in rows:
        if row["id"] in superseded:
            row["state"] = "SUPERSEDED"
        if row["state"] in {"ACTIVE", "UNKNOWN"}:
            groups[(row["item_id"], attribute_key(row["attribute"]))].append(row)
    for group in groups.values():
        signatures = {(r["value"], r["polarity"], r["modality"]) for r in group}
        if len(signatures) > 1:
            for row in group:
                row["state"] = "CONFLICT"
    return rows, errors


def materialize_ledger(entries, context: dict) -> tuple[list, list[str]]:
    """Resolve explicit statement selections, preserving strict legacy quote validation."""
    if not isinstance(entries, list):
        return entries, []
    statements = {s["id"]: s for s in context["user_context"]["statements"]}
    result = []
    errors: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or "source_mode" not in entry:
            result.append(entry)
            continue
        failures = schema_errors([entry], WIRE_LEDGER_SCHEMA)
        statement = statements.get(entry.get("fact_id"))
        if failures or (
            not statement and (entry.get("fact_id") or entry.get("modality") != "UNKNOWN")
        ):
            errors.append(
                ContractIssue(
                    "Ledger phải chọn đúng statement đã đăng ký; không suy nguồn bằng độ giống từ.",
                    code="LEDGER_SELECTION_INVALID",
                    path=f"fact_ledger/{index}",
                )
            )
            continue
        quote = statement["text"] if statement else ""
        result.append(
            {
                **{k: v for k, v in entry.items() if k != "source_mode"},
                "quote": quote,
                "value": quote if entry["modality"] == "ASSERTED" else "",
                "correction_quote": quote if entry["supersedes"] else "",
            }
        )
    return result, errors


def bind_ledger(value: dict, context: dict) -> tuple[dict, list[str]]:
    if "fact_ledger" not in value:
        return context, [
            ContractIssue(
                "Thiếu ledger của lượt sinh hiện tại.", code="LEDGER_MISSING", path="fact_ledger"
            )
        ]
    entries, errors = materialize_ledger(value["fact_ledger"], context)
    if errors:
        return context, errors
    value["fact_ledger"] = entries
    ledger, errors = build_ledger(entries, context)
    return {**context, "user_context": {**context["user_context"], "fact_ledger": ledger}}, errors


def bind_ledger_refs(value, context: dict):
    keys = {r["key"]: r["id"] for r in context["user_context"].get("fact_ledger", [])}

    def bind(node):
        if isinstance(node, list):
            return [bind(v) for v in node]
        if not isinstance(node, dict):
            return node
        return {
            key: [keys.get(v, v) for v in child]
            if key == "ledger_ids" and isinstance(child, list)
            else bind(child)
            for key, child in node.items()
        }

    return bind(value)


def ledger_dependencies_changed(value, before: list[dict], after: list[dict]) -> bool:
    """Unlock draft proofs only when their own ledger dependencies change."""
    old = {r["id"]: (r["state"], r["supersedes"]) for r in before}
    new = {r["id"]: (r["state"], r["supersedes"]) for r in after}

    def changed(node):
        if isinstance(node, list):
            return any(changed(child) for child in node)
        if not isinstance(node, dict):
            return False
        if any(old.get(ref) != new.get(ref) for ref in node.get("ledger_ids", [])):
            return True
        return any(changed(child) for child in node.values())

    return changed(value)
