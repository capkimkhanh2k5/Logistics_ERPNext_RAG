"""Execute bounded proof graphs; semantic decomposition remains explicitly model-reviewed."""

import re
from copy import deepcopy
from decimal import Decimal, InvalidOperation

from rag.llm.contracts.errors import ContractIssue
from rag.llm.evidence.conditions import condition_span_registry
from rag.llm.evidence.ledger import attribute_key
from rag.llm.validation.answer import schema_errors
from rag.prompts.schemas.proof import PROOF_SCHEMA
from rag.utils.files import digest

STATES = {
    "SATISFIED": "PROVEN",
    "KNOWN": "PROVEN",
    "APPLICATION": "PROVEN",
    "REFERENCE": "PROVEN",
    "CONDITIONAL_APPLICATION": "PROVEN",
    "FACT_SUPPORTED": "PROVEN",
    "CONTRADICTED": "CONTRADICTED",
    "NOT_APPLICABLE": "CONTRADICTED",
    "MISSING": "UNKNOWN",
    "MISSING_PRODUCT_INFO": "UNKNOWN",
    "INSUFFICIENT_LEGAL_EVIDENCE": "UNKNOWN",
    "UNRESOLVED_APPLICATION": "UNKNOWN",
    "DEFERRED": "UNKNOWN",
}


def evaluate_proof(
    proof,
    context: dict,
    *,
    target: str | None = None,
    product=False,
    evidence_ids=None,
    fact_ids=None,
) -> tuple[dict, list[str]]:
    if isinstance(proof, dict) and proof.get("target") == "$CONSUMER":
        if not target:
            return {}, [
                ContractIssue(
                    "Proof theo consumer cần target từ slot đang được kiểm tra.",
                    code="PROOF_INVALID",
                    path="proof/target",
                )
            ]
        proof = deepcopy(proof)
        roots = [n for n in proof.get("nodes", []) if n.get("key") == proof.get("root")]
        if len(roots) != 1 or roots[0].get("text") != "$CONSUMER":
            return {}, [
                ContractIssue(
                    "Root theo consumer đã bị đổi nội dung.",
                    code="PROOF_INVALID",
                    path="proof/root",
                )
            ]
        proof["target"] = roots[0]["text"] = target
    errors = schema_errors(proof, PROOF_SCHEMA)
    if errors:
        return {}, [ContractIssue(str(e), code="SCHEMA_VIOLATION", path="proof") for e in errors]

    def issue(message, key=""):
        errors.append(ContractIssue(message, code="PROOF_INVALID", path=f"proof/{key}"))

    if target is not None and proof["target"] != target:
        issue("Proof không chứng minh đúng target chỉ đọc đã cấp.", "target")
    if (
        proof["decomposition_review"] != "FAITHFUL_COMPLETE"
        or proof["ledger_review"] != "CONSISTENT"
    ):
        issue("Phân rã hoặc đối chiếu ledger chưa được xác nhận đầy đủ.")
    cache_key = digest(
        [
            proof,
            target,
            product,
            sorted(evidence_ids) if evidence_ids is not None else None,
            sorted(fact_ids) if fact_ids is not None else None,
            context.get("scoped_item_id"),
            context.get("proof_item_ids"),
            [i["id"] for i in context.get("request", {}).get("items", [])],
            context.get("snapshot"),
            context["user_context"].get("fact_ledger", []),
            [
                (
                    s["evidence_id"],
                    s["text"],
                    s.get("legal_status"),
                    s.get("effective_from"),
                    s.get("effective_to"),
                    s.get("locator"),
                )
                for s in context["sources"]
            ],
        ]
    )
    cache = context.setdefault("proof_cache", {})
    if cache_key in cache:
        return dict(cache[cache_key]), []
    nodes = {n["key"]: n for n in proof["nodes"]}
    if len(nodes) != len(proof["nodes"]) or proof["root"] not in nodes:
        issue("Proof thiếu root hoặc lặp node key.")
        return {}, errors
    if nodes[proof["root"]]["text"] != proof["target"]:
        issue("Root phải giữ nguyên đầy đủ target, không đổi sang mệnh đề yếu hơn.", "root")
    sources = {s["evidence_id"]: s for s in context["sources"]}
    spans = condition_span_registry(context["sources"])
    ledger = {r["id"]: r for r in context["user_context"].get("fact_ledger", [])}
    item = context.get("scoped_item_id")
    allowed_items = (
        set(context.get("proof_item_ids", []))
        or ({item} if item else {i["id"] for i in context.get("request", {}).get("items", [])})
        or {""}
    )
    allowed_evidence = set(evidence_ids) if evidence_ids is not None else set(sources)
    allowed_facts = (
        set(fact_ids)
        if fact_ids is not None
        else {s["id"] for s in context["user_context"]["statements"]}
    )
    visiting: set[str] = set()
    evaluated: dict[str, str] = {}
    used_ledger: set[str] = set()
    used_sources: set[str] = set()

    def evaluate(key):
        if key in evaluated:
            return evaluated[key]
        if key not in nodes or key in visiting:
            issue("Proof có cạnh không tồn tại hoặc chu trình.", key)
            return "UNKNOWN"
        visiting.add(key)
        node = nodes[key]
        refs = node["evidence_ids"]
        facts = [ledger[lid] for lid in node["ledger_ids"] if lid in ledger]
        if set(node["item_ids"]) - allowed_items or any(
            r["item_id"] not in node["item_ids"] for r in facts
        ):
            issue("Node phải giữ đúng các chủ thể của dữ kiện và objective.", key)
        if set(refs) - allowed_evidence or set(refs) - sources.keys():
            issue("Node dùng nguồn ngoài phạm vi chứng minh.", key)
        if len(facts) != len(node["ledger_ids"]):
            issue("Node dùng ledger ID chưa được backend cấp.", key)
        for row in facts:
            if (item and row["item_id"] != item) or (
                row["fact_id"] and row["fact_id"] not in allowed_facts
            ):
                issue("Node dùng lời khai ngoài phạm vi mặt hàng/fact được cấp.", key)
            if (
                row["state"] in {"SUPERSEDED", "CONFLICT", "HYPOTHETICAL", "QUESTION"}
                and node["assessment"] != "UNKNOWN"
            ):
                issue(
                    "Dữ kiện bị thay thế, mâu thuẫn hoặc giả định không được dùng làm chứng minh.",
                    key,
                )
        if any(
            cid not in spans or spans[cid]["evidence_id"] not in refs
            for cid in node["condition_ids"]
        ):
            issue("Predicate không gắn đúng span nguồn được cấp.", key)
        used_ledger.update(r["id"] for r in facts)
        used_sources.update(refs)
        children = node["children"]
        states = [evaluate(child) for child in children]
        operator = node["operator"]
        state = node["assessment"]
        if operator in {"ATOM", "COMPARE"}:
            if children:
                issue("Node nguyên tử không có children.", key)
            if state != "UNKNOWN":
                if node["kind"] in {"PREDICATE", "QUANTITY", "SCOPE"} and (
                    not node["attribute"]
                    or not any(
                        attribute_key(r["attribute"]) == attribute_key(node["attribute"])
                        for r in facts
                    )
                ):
                    issue(
                        "Predicate hàng hóa phải nối đúng thuộc tính đã đăng ký trong ledger.", key
                    )
                if node["kind"] != "PRODUCT_FACT" and (not refs or not node["condition_ids"]):
                    issue("Mệnh đề pháp lý/quan hệ cần nguồn và span riêng.", key)
                if node["kind"] != "LEGAL_RULE" and not any(r["state"] == "ACTIVE" for r in facts):
                    issue("Mệnh đề hàng hóa cần dữ kiện ledger còn hiệu lực.", key)
            if state == "UNKNOWN" and node["cause"] == "MISSING_PRODUCT_FACT":
                if not refs or not any(
                    r["state"] == "UNKNOWN"
                    and attribute_key(r["attribute"]) == attribute_key(node["attribute"])
                    for r in facts
                ):
                    issue(
                        "Thiếu thuộc tính cần entry UNKNOWN đúng thuộc tính và điều kiện nguồn.",
                        key,
                    )
            if operator == "COMPARE":
                state = compare(node, facts, [sources[e] for e in refs if e in sources], issue)
        elif operator in {"ALL", "SCOPE"}:
            if not children or (operator == "SCOPE" and len(children) != 2):
                issue("ALL/SCOPE thiếu toán hạng bắt buộc.", key)
            state = (
                "CONTRADICTED"
                if "CONTRADICTED" in states
                else "PROVEN"
                if states and all(s == "PROVEN" for s in states)
                else "UNKNOWN"
            )
        elif operator == "ANY":
            if not children:
                issue("ANY cần các phương án thực sự của nguồn.", key)
            state = (
                "PROVEN"
                if "PROVEN" in states
                else "CONTRADICTED"
                if states and all(s == "CONTRADICTED" for s in states)
                else "UNKNOWN"
            )
        elif operator == "NOT":
            if len(states) != 1:
                issue("NOT cần đúng một toán hạng.", key)
            state = {"PROVEN": "CONTRADICTED", "CONTRADICTED": "PROVEN"}.get(
                states[0] if states else "UNKNOWN", "UNKNOWN"
            )
        elif operator == "EXCEPT":
            if len(states) != 2:
                issue("EXCEPT cần quy tắc nền và ngoại lệ.", key)
            base, exception = states if len(states) == 2 else ("UNKNOWN", "UNKNOWN")
            state = (
                "CONTRADICTED"
                if base == "CONTRADICTED" or exception == "PROVEN"
                else "PROVEN"
                if base == "PROVEN" and exception == "CONTRADICTED"
                else "UNKNOWN"
            )
        if state != node["assessment"]:
            issue("Đánh giá node mâu thuẫn phép tổng hợp logic.", key)
        if state == "UNKNOWN" and node["cause"] == "NONE":
            issue("UNKNOWN cần nguyên nhân cụ thể, không mặc định thiếu dữ kiện.", key)
        if state != "UNKNOWN" and node["cause"] != "NONE":
            issue("Đánh giá xác định không có nguyên nhân UNKNOWN.", key)
        visiting.remove(key)
        evaluated[key] = state
        return state

    state = evaluate(proof["root"])
    if set(evaluated) != set(nodes):
        issue("Proof chứa node không tham gia target.")
    if (
        product
        and state in {"PROVEN", "CONTRADICTED"}
        and not any(ledger[lid]["state"] == "ACTIVE" for lid in used_ledger)
    ):
        issue("Áp dụng cho hàng hóa cần dữ kiện thực sự còn hiệu lực.")
    if not used_sources and not all(n["kind"] == "PRODUCT_FACT" for n in nodes.values()):
        if state != "UNKNOWN" or nodes[proof["root"]]["cause"] != "MISSING_LEGAL_RULE":
            issue("Nhận định pháp lý chưa có nguồn hỗ trợ.")
    predicate_ids: dict[str, str] = {}
    for key in evaluated:
        node = nodes[key]
        children = [predicate_ids.get(child, "UNVERIFIED") for child in node["children"]]
        if node["operator"] in {"ALL", "ANY"}:
            children = sorted(set(children))
        predicate_ids[key] = (
            "N"
            + digest(
                [
                    {
                        name: node[name]
                        for name in (
                            "operator",
                            "kind",
                            "text",
                            "attribute",
                            "item_ids",
                            "comparison",
                        )
                    },
                    sorted(node["condition_ids"]),
                    children,
                    context.get("snapshot"),
                    [
                        {
                            field: sources[eid].get(field)
                            for field in (
                                "evidence_id",
                                "legal_status",
                                "effective_from",
                                "effective_to",
                                "locator",
                            )
                        }
                        for eid in sorted(node["evidence_ids"])
                        if eid in sources
                    ],
                ]
            )[:20]
        )
    identity = [
        proof["target"],
        predicate_ids.get(proof["root"]),
        [
            (
                predicate_ids[key],
                nodes[key]["assessment"],
                nodes[key]["cause"],
                sorted(nodes[key]["ledger_ids"]),
            )
            for key in evaluated
        ],
    ]
    result = {
        "id": "G" + digest(identity)[:20],
        "state": state,
        "cause": nodes[proof["root"]]["cause"],
        "ledger_ids": sorted(used_ledger),
        "evidence_ids": sorted(used_sources),
        "root_predicate_id": predicate_ids.get(proof["root"]),
        "predicate_ids": sorted(set(predicate_ids.values())),
    }
    if not errors:
        cache[cache_key] = dict(result)
        context.setdefault("proof_catalogue", {})[result["id"]] = {
            **result,
            "target": proof["target"],
            "nodes": [
                {
                    **node,
                    "predicate_id": predicate_ids[node["key"]],
                    "child_predicate_ids": [predicate_ids[child] for child in node["children"]],
                }
                for node in proof["nodes"]
            ],
            "root": proof["root"],
            "semantic_review": "MODEL_REVIEWED",
        }
    return result, errors


def compare(node, facts, sources, issue):
    value = node["comparison"]
    if (
        value["operator"] == "NONE"
        or not value["left_unit"]
        or value["left_unit"] != value["right_unit"]
    ):
        issue(
            "So sánh yêu cầu cùng đơn vị tường minh; không tự suy đổi đơn vị chưa hỗ trợ.",
            node["key"],
        )
        return "UNKNOWN"

    def present(number, unit, texts):
        pattern = r"(?<![\w.,])" + re.escape(number) + r"\s*" + re.escape(unit) + r"(?!\w)"
        return any(re.search(pattern, text) for text in texts)

    if not present(
        value["left"], value["left_unit"], [f["quote"] for f in facts if f["state"] == "ACTIVE"]
    ) or not present(value["right"], value["right_unit"], [s["text"] for s in sources]):
        issue("Số và đơn vị so sánh không nằm trong lời khai/nguồn được dẫn.", node["key"])
        return "UNKNOWN"
    try:
        left, right = Decimal(value["left"]), Decimal(value["right"])
        if not left.is_finite() or not right.is_finite():
            raise InvalidOperation
        answer = {
            "EQ": left == right,
            "LT": left < right,
            "LE": left <= right,
            "GT": left > right,
            "GE": left >= right,
        }[value["operator"]]
    except (InvalidOperation, KeyError):
        issue("Đại lượng so sánh không có biểu diễn số được hỗ trợ.", node["key"])
        return "UNKNOWN"
    return "PROVEN" if answer else "CONTRADICTED"


def proof_errors(
    check: dict, context: dict, *, target=None, product=False, evidence_ids=None, fact_ids=None
) -> list[str]:
    result, errors = evaluate_proof(
        check.get("proof"),
        context,
        target=target,
        product=product,
        evidence_ids=evidence_ids,
        fact_ids=fact_ids,
    )
    expected = STATES.get(check.get("assessment", ""))
    if result and expected and result["state"] != expected:
        errors.append(
            ContractIssue(
                "Assessment không khớp proof đã tổng hợp.",
                code="PROOF_STATE_MISMATCH",
                path="proof/root",
                expected=expected,
                actual=result["state"],
            )
        )
    if (
        result
        and check.get("assessment") in {"MISSING", "MISSING_PRODUCT_INFO"}
        and result["cause"] != "MISSING_PRODUCT_FACT"
    ):
        errors.append(
            ContractIssue(
                "Câu hỏi thiếu fact chưa có nguyên nhân tương ứng.",
                code="PROOF_STATE_MISMATCH",
                path="proof/root",
            )
        )
    return errors
