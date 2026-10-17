"""Source-bound comparison coverage and validation; no product attribute catalogue."""

import re

from rag.llm.validation import LEGAL_INFORMATION, _folded

MAX_COMPARISON_EXTRAS = 128


def comparison_neighbours(candidates: list[dict], graph) -> tuple[list[dict], list[dict]]:
    if graph is None or not all(
        hasattr(graph, name) for name in ("hs_hierarchy", "children", "node_code")
    ):
        return candidates, []
    expanded = {row["id"]: row for row in candidates}
    groups, seen_parents = [], set()
    seed_codes = sorted({row["code"] for row in candidates})
    if len(seed_codes) > 1:
        groups.append({"parent_code": "", "codes": seed_codes, "branch_options": []})
    for candidate in candidates:
        hierarchy = graph.hs_hierarchy(candidate)
        if hierarchy["status"] != "VERIFIED":
            continue
        parent = next(node for node in hierarchy["chain"] if node["level"] == 6)
        if parent["id"] in seen_parents:
            continue
        seen_parents.add(parent["id"])
        frontier, visited, leaves = [parent["id"]], set(), {}
        while frontier:
            sid = frontier.pop()
            if sid in visited:
                continue
            visited.add(sid)
            code = graph.node_code(sid) or ""
            if re.fullmatch(r"[0-9]{8}", code):
                leaves[code] = sid
            frontier.extend(graph.children.get(sid, set()))
        if len(leaves) < 2:
            continue
        options: dict[tuple, list[str]] = {}
        for code, sid in sorted(leaves.items()):
            row = graph.records.get(sid)
            if row and len(expanded) < len(candidates) + MAX_COMPARISON_EXTRAS:
                expanded.setdefault(sid, row)
            context_ids = tuple(sorted(graph.source_view({"id": sid})["context_ids"]))
            options.setdefault(context_ids, []).append(code)
        groups.append(
            {
                "parent_code": parent["code"],
                "codes": sorted(leaves),
                "branch_options": [
                    {"source_ids": list(ids), "codes": codes} for ids, codes in options.items()
                ]
                if len(options) > 1
                else [],
            }
        )
    return list(expanded.values()), groups


def comparison_payload(groups: list[dict], evidence: list[dict], sources: list[dict]) -> list[dict]:
    by_code = {item["code"]: item for item in evidence}
    ids = {source["id"]: source["evidence_id"] for source in sources}
    return [
        {
            "parent_code": group["parent_code"],
            "codes": group["codes"],
            "missing_codes": [
                code
                for code in group["codes"]
                if code not in by_code or by_code[code]["hierarchy"]["status"] != "VERIFIED"
            ],
            "branch_options": [
                {
                    "codes": option["codes"],
                    "evidence_ids": [ids[s] for s in option["source_ids"] if s in ids],
                }
                for option in group["branch_options"]
            ],
        }
        for group in groups
    ]


def review_scope(context: dict, code: str | None = None) -> list[dict]:
    return [
        group
        for group in context.get("candidate_comparison", [])
        if code is None or not group["parent_code"] or code in group["codes"]
    ]


def disambiguation_errors(value: dict, context: dict, code: str | None = None) -> list[str]:
    groups = review_scope(context, code)
    if not groups:
        return []
    errors = []
    sources = {s["evidence_id"]: s for s in context["sources"]}
    statements = {s["id"]: s for s in context["user_context"]["statements"]}
    source_ids = {s["label"]: s["evidence_id"] for s in context["sources"]}
    peers = {
        p["code"]: p
        for p in [*context["candidate_evidence"], *context.get("comparison_candidates", [])]
    }
    expected = {c for group in groups for c in group["codes"]}
    rows = value["candidate_assessments"]
    if {r["code"] for r in rows} != expected or len(rows) != len(expected):
        errors.append(
            "Phải đánh giá đúng một lần mỗi mã trong phạm vi so sánh, không bỏ nhánh đối chứng."
        )

    def grounded(item, required):
        if any(eid not in sources for eid in item["evidence_ids"]):
            errors.append("So sánh ứng viên tham chiếu chứng cứ không có trong ngữ cảnh.")
        refs, quotes = item["fact_ids"], item["user_quotes"]
        if any(fid not in statements for fid in refs) or any(
            not quote.strip()
            or not any(quote in statements[fid]["text"] for fid in refs if fid in statements)
            for quote in quotes
        ):
            errors.append("So sánh ứng viên phải dùng trích đoạn thật từ đúng lời người dùng.")
        if required and (not refs or not quotes or not item["evidence_ids"]):
            errors.append(
                "Không được loại nhánh hoặc xác nhận thuộc tính phân biệt chỉ từ tên hàng/thứ hạng; cần dữ kiện và nguồn."
            )
        if any(LEGAL_INFORMATION.search(_folded(quote)) for quote in quotes):
            errors.append(
                "Không dùng yêu cầu tra cứu hoặc nội dung pháp lý làm dữ kiện loại nhánh."
            )

    for row in rows:
        grounded(row, row["assessment"] == "RULED_OUT")
        if row["assessment"] == "RULED_OUT":
            peer = peers.get(row["code"], {})
            relevant = {
                source_ids[label]
                for label in peer.get("required_citation_labels", [])
                if label in source_ids
            }
            if not relevant & set(row["evidence_ids"]):
                errors.append("Loại ứng viên phải tham chiếu điều kiện thuộc chính nhánh đó.")
    branches = value["branch_checks"]
    required_groups = {g["parent_code"]: g for g in groups if g["branch_options"]}
    if {b["parent_code"] for b in branches} != set(required_groups) or len(
        {(b["parent_code"], _folded(b["attribute"])) for b in branches}
    ) != len(branches):
        errors.append(
            "Phải kiểm tra từng chiều phân nhánh từ graph, không được mặc định nhánh Loại khác."
        )
    for parent_code, group in required_groups.items():
        referenced = {
            eid for b in branches if b["parent_code"] == parent_code for eid in b["evidence_ids"]
        }
        if not all(set(o["evidence_ids"]) <= referenced for o in group["branch_options"]):
            errors.append(
                "Kiểm tra thuộc tính phân biệt phải bao phủ các điều kiện nhánh đối chứng."
            )
    for branch in branches:
        grounded(branch, branch["assessment"] == "KNOWN")
        branch_group = required_groups.get(branch["parent_code"])
        if branch_group and not set(branch["evidence_ids"]) & {
            eid for o in branch_group["branch_options"] for eid in o["evidence_ids"]
        }:
            errors.append("Thuộc tính phân biệt phải gắn với điều kiện phân nhánh thực có.")
        if branch["assessment"] == "MISSING":
            if branch["fact_ids"] or branch["user_quotes"]:
                errors.append("Thuộc tính chưa biết không được có dữ kiện xác nhận giả định.")
            if value["status"] == "MISSING_PRODUCT_INFO" and not any(
                _folded(q["attribute"]) == _folded(branch["attribute"])
                and set(q["evidence_ids"]) & set(branch["evidence_ids"])
                for q in value["clarifications"]
            ):
                errors.append(
                    "Thuộc tính phân biệt chưa biết phải có câu hỏi làm rõ gắn đúng điều kiện nguồn."
                )
    if value["status"] == "SUPPORTED":
        possible = [r["code"] for r in rows if r["assessment"] != "RULED_OUT"]
        if (
            len(possible) != 1
            or (code is not None and possible != [code])
            or any(row["assessment"] == "INSUFFICIENT_LEGAL_EVIDENCE" for row in rows)
        ):
            errors.append(
                "SUPPORTED chỉ khi còn đúng ứng viên đề xuất; không chọn một mã khi nhiều mã chưa bị loại."
            )
        if any(g["missing_codes"] for g in groups):
            errors.append("Nguồn so sánh chưa đầy đủ; không coi mã bị thiếu nguồn là đã bị loại.")
        if any(b["assessment"] != "KNOWN" for b in branches):
            errors.append(
                "SUPPORTED không được tự giả định thuộc tính phân biệt chưa được cung cấp."
            )
    return list(dict.fromkeys(errors))
