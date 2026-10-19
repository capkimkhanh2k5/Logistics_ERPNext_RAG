from copy import deepcopy
from itertools import permutations

from rag.llm.candidate_ranking import rank_candidates


def candidate(code, checks, status="CONDITIONAL"):
    return {
        "code": code,
        "evidence_status": status,
        "conditions": [
            {"source_id": key, "assessment": value, "required": True}
            for key, value in checks.items()
        ],
    }


def test_shared_decisive_evidence_precedes_missing_evidence_independent_of_input_order():
    stronger = candidate("A", {"parent": "SATISFIED", "branch": "MISSING_PRODUCT_INFO"})
    weaker = candidate("B", {"parent": "MISSING_PRODUCT_INFO", "branch": "MISSING_PRODUCT_INFO"})
    for rows in permutations([stronger, weaker]):
        ranked = rank_candidates(rows)
        assert [(c["code"], c["rank"], c["tied"]) for c in ranked] == [
            ("A", 1, False),
            ("B", 2, False),
        ]


def test_distinct_unknown_import_branches_stay_tied_despite_more_generic_matches():
    a = candidate("87038018", {"common": "SATISFIED", "ckd": "MISSING_PRODUCT_INFO"})
    b = candidate("87038098", {"common": "SATISFIED", "cbu": "MISSING_PRODUCT_INFO"})
    b["conditions"] += [{"source_id": "extra", "assessment": "SATISFIED"}] * 10
    for rows in permutations([a, b]):
        ranked = rank_candidates(rows)
        assert all(c["rank"] == 1 and c["tied"] for c in ranked)


def test_duplicate_sources_and_optional_checks_cannot_raise_rank():
    a = candidate("A", {"branch": "MISSING_PRODUCT_INFO"})
    b = deepcopy(a)
    b["code"] = "B"
    a["conditions"] += [{"source_id": "branch", "assessment": "SATISFIED"}] * 10
    a["conditions"].append({"source_id": "optional", "assessment": "SATISFIED", "required": False})
    assert all(c["tied"] for c in rank_candidates([a, b]))


def test_supported_first_without_changing_status_or_inventing_confidence():
    rows = [
        candidate("A", {"x": "MISSING_PRODUCT_INFO"}),
        candidate("B", {"x": "SATISFIED"}, "SUPPORTED"),
    ]
    original = deepcopy(rows)
    ranked = rank_candidates(rows)
    assert [c["code"] for c in ranked] == ["B", "A"]
    assert rows == original
    assert all("confidence" not in c for c in ranked)
