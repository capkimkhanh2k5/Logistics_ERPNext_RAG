"""Evidence readiness is a partial order, never a probability of legal correctness."""


def _conditions(candidate: dict) -> dict[str, str]:
    checks: dict[str, str] = {}
    for condition in candidate.get("conditions", []):
        if not condition.get("required", True):
            continue
        key = condition.get("source_id")
        if not key:
            return {}
        assessment = condition["assessment"]
        # Repeating/splitting a source cannot increase its weight or hide a gap.
        if checks.get(key) != "MISSING_PRODUCT_INFO":
            checks[key] = assessment
    return checks


def _precedes(left: dict, right: dict) -> bool:
    if left["evidence_status"] != right["evidence_status"]:
        return left["evidence_status"] == "SUPPORTED"
    a, b = _conditions(left), _conditions(right)
    if not a or not b:
        return False
    shared = a.keys() & b.keys()
    # Unknown conditions belonging to different branches are incomparable.
    if any(a[k] != "SATISFIED" for k in a.keys() - shared) or any(
        b[k] != "SATISFIED" for k in b.keys() - shared
    ):
        return False
    return all(a[k] == "SATISFIED" or b[k] != "SATISFIED" for k in shared) and any(
        a[k] == "SATISFIED" and b[k] == "MISSING_PRODUCT_INFO" for k in shared
    )


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """Sort non-dominated layers; code order inside a layer conveys no preference."""
    pending, ranked = list(candidates), []
    rank = 1
    while pending:
        layer = [c for c in pending if not any(_precedes(other, c) for other in pending)]
        # Be conservative even with malformed/inconsistent input.
        if not layer:
            layer = pending[:]
        for candidate in sorted(layer, key=lambda c: c["code"]):
            ranked.append(
                {
                    **candidate,
                    "rank": rank,
                    "tied": len(layer) > 1,
                    "ranking_basis": (
                        "Đủ căn cứ qua review; thứ hạng không thay thế điều kiện phát hành mã."
                        if candidate["evidence_status"] == "SUPPORTED"
                        else "Chưa đủ căn cứ phân biệt thứ tự trong nhóm đồng hạng."
                        if len(layer) > 1
                        else "Ưu tiên theo điều kiện bắt buộc đã được chứng minh; vẫn còn dữ kiện cần xác nhận."
                    ),
                }
            )
        pending = [c for c in pending if c not in layer]
        rank += len(layer)
    return ranked
