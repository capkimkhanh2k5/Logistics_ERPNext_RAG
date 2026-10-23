"""Describe actual review coverage without equating it with legal correctness."""


def review_coverage(rows: list[dict]) -> dict:
    results = []
    for row in rows:
        derived = bool(row.get("derived_from_reviewed_results")) and not row.get("failure_kind")
        analysis = bool(row.get("analysis_review_valid")) and not row.get("failure_kind")
        product = bool(row.get("review_valid")) and not row.get("failure_kind")
        prerequisite = bool(row.get("prerequisite_review", {}).get("review_valid")) and not row.get(
            "failure_kind"
        )
        results.append(
            {
                "result_id": row["result_id"],
                "scope": "CODE_COMPARISON"
                if derived
                else "CLAIMS"
                if analysis
                else "PRODUCT_DECISION"
                if product
                else "PREREQUISITE_DECISION"
                if prerequisite
                else "NONE",
                "claim_indices": list(range(len(row.get("claims", [])))) if analysis else [],
                "status": "BACKEND_DERIVED"
                if derived
                else "MODEL_REVIEWED"
                if analysis or product
                else "PARTIALLY_REVIEWED"
                if prerequisite
                else "NOT_EVALUATED",
            }
        )
    reviewed = sum(r["status"] == "MODEL_REVIEWED" for r in results)
    derived_count = sum(r["status"] == "BACKEND_DERIVED" for r in results)
    return {
        "status": "MODEL_REVIEWED"
        if results and reviewed == len(results)
        else "REVIEWED_WITH_BACKEND_DERIVATION"
        if results and reviewed + derived_count == len(results)
        else "PARTIALLY_REVIEWED"
        if reviewed or derived_count or any(r["status"] == "PARTIALLY_REVIEWED" for r in results)
        else "NOT_EVALUATED",
        "results": results,
    }
