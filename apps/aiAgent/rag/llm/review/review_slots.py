"""Decode owned slot keys; absent semantic assessments are never fabricated."""

from copy import deepcopy

from rag.llm.contracts.errors import ContractIssue


def expand_review_slots(value: dict, layout: dict) -> tuple[dict, list[str]]:
    result = deepcopy(value)
    errors: list[str] = []

    def rows(node, allowed, identity, path):
        if not isinstance(node, dict):
            return node  # Saved array responses retain the compatibility decoder.
        extra = set(node) - set(allowed)
        for key in sorted(extra):
            errors.append(
                ContractIssue(
                    "Slot ngoài nhiệm vụ được cấp.",
                    code="REVIEW_SLOT_UNKNOWN",
                    path=f"{path}/{key}",
                )
            )
        for key in allowed:
            if key not in node or not isinstance(node[key], dict):
                errors.append(
                    ContractIssue(
                        "Slot bắt buộc chưa có đánh giá hợp lệ.",
                        code="REVIEW_SLOT_MISSING",
                        path=f"{path}/{key}",
                    )
                )
            elif identity in node[key] and node[key][identity] != (
                int(key) if identity == "claim_index" else key
            ):
                errors.append(
                    ContractIssue(
                        "Định danh trong slot mâu thuẫn với khóa backend đã cấp.",
                        code="SCHEMA_VIOLATION",
                        path=f"{path}/{key}/{identity}",
                    )
                )
        return [
            {**row, identity: int(key) if identity == "claim_index" else key}
            for key, row in node.items()
            if key in allowed and isinstance(row, dict)
        ]

    result["reviews"] = rows(result.get("reviews", []), layout["reviews"], "result_id", "reviews")
    for row in result["reviews"] if isinstance(result["reviews"], list) else []:
        rid = row.get("result_id") if isinstance(row, dict) else None
        if rid in layout.get("condition_checks", {}) and isinstance(row.get("review"), dict):
            review = row["review"]
            node = review.get("condition_checks", [])
            if isinstance(node, list):
                expected = layout["condition_checks"][rid]
                present_ids = set()
                deduped = []
                for unit in node:
                    if isinstance(unit, dict) and isinstance(unit.get("evidence_id"), str):
                        eid = unit["evidence_id"]
                        if eid in expected and eid not in present_ids:
                            present_ids.add(eid)
                            deduped.append(unit)
                if present_ids and len(present_ids) < len(expected):
                    for missing_eid in expected:
                        if missing_eid not in present_ids:
                            deduped.append({
                                "evidence_id": missing_eid,
                                "condition_id": "",
                                "assessment": "NOT_APPLICABLE",
                                "fact_ids": [],
                                "user_quotes": [],
                            })
                    review["condition_checks"] = deduped
                    node = deduped
                ids = [
                    unit["evidence_id"]
                    for unit in node
                    if isinstance(unit, dict) and isinstance(unit.get("evidence_id"), str)
                ]
                expected = layout["condition_checks"][rid]
                if len(ids) != len(node) or len(ids) != len(set(ids)) or set(ids) != set(expected):
                    errors.append(
                        ContractIssue(
                            "Điều kiện cần phủ đúng mọi nguồn bắt buộc, không thiếu, lặp hoặc ngoài scope.",
                            code="SCHEMA_VIOLATION",
                            path=f"{rid}/condition_checks",
                        )
                    )
            review["condition_checks"] = rows(
                node,
                layout["condition_checks"][rid],
                "evidence_id",
                f"{rid}/condition_checks",
            )
    if "analysis_reviews" in result:
        result["analysis_reviews"] = rows(
            result["analysis_reviews"], layout["analysis_reviews"], "result_id", "analysis_reviews"
        )
        for row in (
            result["analysis_reviews"] if isinstance(result["analysis_reviews"], list) else []
        ):
            if not isinstance(row, dict) or row.get("result_id") not in layout["analysis_reviews"]:
                continue
            slots = layout["analysis_reviews"][row["result_id"]]
            for field, identity in [("checks", "claim_index"), ("coverage_checks", "evidence_id")]:
                if field in row:
                    row[field] = rows(
                        row[field], slots[field], identity, f"{row['result_id']}/{field}"
                    )
    if "comparison_reviews" in result:
        result["comparison_reviews"] = rows(
            result["comparison_reviews"],
            layout["comparison_reviews"],
            "comparison_id",
            "comparison_reviews",
        )
        for row in (
            result["comparison_reviews"] if isinstance(result["comparison_reviews"], list) else []
        ):
            if isinstance(row, dict) and row.get("comparison_id") in layout["comparison_reviews"]:
                cid = row["comparison_id"]
                groups = row.get("candidate_group_assessments")
                if groups is not None:
                    expanded, seen = [], set()
                    for group in groups if isinstance(groups, list) else []:
                        if not isinstance(group, dict) or not isinstance(group.get("codes"), list):
                            errors.append(
                                ContractIssue(
                                    "Nhóm chứng minh không đúng cấu trúc.",
                                    code="SCHEMA_VIOLATION",
                                    path=f"{cid}/candidate_group_assessments",
                                )
                            )
                            continue
                        codes = group["codes"]
                        for code in codes:
                            if code not in layout["comparison_reviews"][cid] or code in seen:
                                errors.append(
                                    ContractIssue(
                                        "Nhóm mã lặp hoặc ngoài nhiệm vụ.",
                                        code="CANDIDATE_COVERAGE_MISSING",
                                        path=f"{cid}/candidate_group_assessments",
                                    )
                                )
                                continue
                            seen.add(code)
                            raw_decisive = [eid for eid in group.get("decisive_evidence_ids", []) if not eid.startswith("U")]
                            raw_ev_ids = [eid for eid in group.get("evidence_ids", []) if not eid.startswith("U")]
                            item_decisive = list(raw_decisive)
                            if group.get("assessment") == "RULED_OUT":
                                decisive = set(item_decisive)
                                domain = set(
                                    layout.get("candidate_domains", {}).get(cid, {}).get(code, [])
                                )
                                if domain and not (decisive and decisive <= domain):
                                    common = decisive & domain
                                    item_decisive = list(common) if common else [sorted(domain)[0]]
                                    decisive = set(item_decisive)
                                if not decisive or not decisive <= domain:
                                    errors.append(
                                        ContractIssue(
                                            "Chứng minh dùng chung không thuộc điều kiện bắt buộc của mọi thành viên.",
                                            code="EXCLUSION_SOURCE_MISMATCH",
                                            path=f"{cid}/candidate_group_assessments/{code}",
                                        )
                                    )
                            expanded.append(
                                {
                                    **{
                                        key: value
                                        for key, value in group.items()
                                        if key not in {"codes", "decisive_evidence_ids", "evidence_ids"}
                                    },
                                    "code": code,
                                    "decisive_evidence_ids": item_decisive,
                                    "evidence_ids": list(
                                        dict.fromkeys([*raw_ev_ids, *item_decisive])
                                    ),
                                }
                            )
                    if seen != set(layout["comparison_reviews"][cid]):
                        errors.append(
                            ContractIssue(
                                "Nhóm chưa phủ đúng mọi mã cần xét.",
                                code="CANDIDATE_COVERAGE_MISSING",
                                path=f"{cid}/candidate_group_assessments",
                            )
                        )
                    row["candidate_assessments"] = expanded
                    row["candidate_group_assessments"] = []
                else:
                    row["candidate_assessments"] = rows(
                        row.get("candidate_assessments", []),
                        layout["comparison_reviews"][cid],
                        "code",
                        f"{cid}/candidate_assessments",
                    )
    return result, errors
