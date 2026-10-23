"""Stable error metadata; no diagnostic is permission to invent facts or legal status."""

import re

GROUPS = {
    "BINDING": (
        "VALIDATE_OR_REBIND_EXACT",
        "registry",
        "NONFINAL_CODE CODE_LEVEL_MISMATCH UNREGISTERED_CODE CONDITION_REF_INVALID CONDITION_REF_MISSING "
        "CONDITION_SOURCE_MISMATCH CONDITION_SPAN_INVALID CRITERION_QUOTE_INVALID FACT_PROVENANCE_MISSING "
        "FACT_QUOTE_INVALID UNREGISTERED_EVIDENCE SCHEMA_VIOLATION CLAIMS_REQUIRED LEDGER_INVALID LEDGER_MISSING INTERNAL_ID_LEAKED LEGAL_INFO_REQUESTED",
    ),
    "COVERAGE": (
        "KEEP_UNREVIEWED",
        "review_orchestrator",
        "CANDIDATE_COVERAGE_MISSING RESULT_COVERAGE_MISSING ANALYSIS_COVERAGE_MISSING REQUIREMENTS_COVERAGE_MISSING "
        "REQUIRED_CONDITION_MISSING BRANCH_COVERAGE_MISSING REVIEW_SLOT_MISSING REVIEW_SLOT_UNKNOWN",
    ),
    "PROOF": (
        "WITHHOLD_UNPROVEN_CLAIM",
        "evidence_validator",
        "APPLICATION_FACTS_REQUIRED APPLICATION_UNPROVEN CLAIM_FACT_UNPROVEN EXCLUSION_UNPROVEN "
        "EXCLUSIVE_CONDITION_UNPROVEN MEASUREMENT_UNPROVEN PRESENTATION_SCOPE_UNPROVEN "
        "PRESENTATION_UNPROVEN REJECTION_UNPROVEN SOURCE_CONDITION_UNPROVEN STALE_FACT "
        "CONDITION_POLARITY_MISMATCH DEFINITION_UNPROVEN CANDIDATE_UNIQUENESS_UNPROVEN BRANCH_PROOF_UNPROVEN",
    ),
    "SEMANTIC": (
        "REVIEW_SCOPED_ASSESSMENT",
        "decision_orchestrator",
        "LEDGER_SELECTION_INVALID PROOF_REF_INVALID PROOF_INVALID PROOF_STATE_MISMATCH ASSESSMENT_MISMATCH CONDITIONAL_CLAIM_MISMATCH CRITERION_NOT_CITED DEFERRED_WITHOUT_PREREQUISITE "
        "EXCLUSION_PROOF_INVALID EXCLUSION_SOURCE_MISMATCH FACT_ASSESSMENT_MISMATCH NON_PRODUCT_QUOTE "
        "RESELECTION_UNSUPPORTED REVIEW_BASIS_MISSING",
    ),
}
SPECS = {
    code: {"cause": cause, "owner": owner, "safe_action": action}
    for cause, (action, owner, codes) in GROUPS.items()
    for code in codes.split()
}

# Compatibility adapter for earlier validators and archived errors. New emitters
# should use ContractIssue with a stable code and structured expected/actual values.
LEGACY_PATTERNS = [
    (r"Model chỉ trả evidence_ids|Không viết registry ID trong text", "INTERNAL_ID_LEAKED"),
    (r"ID chứng cứ không tồn tại|ID lời người dùng không tồn tại", "UNREGISTERED_EVIDENCE"),
    (r"Phải đánh giá đúng một lần mỗi mã", "CANDIDATE_COVERAGE_MISSING"),
    (r"Loại ứng viên .+phải tham chiếu điều kiện thuộc chính nhánh", "EXCLUSION_SOURCE_MISMATCH"),
    (
        r"Kiểm tra thuộc tính phân biệt phải bao phủ|Phải kiểm tra từng chiều phân nhánh",
        "BRANCH_COVERAGE_MISSING",
    ),
    (r"Mỗi ứng viên phải kiểm tra mọi điều kiện bắt buộc", "REQUIRED_CONDITION_MISSING"),
    (r"Định nghĩa tại .+chưa được chứng minh", "DEFINITION_UNPROVEN"),
    (r"SUPPORTED chỉ khi còn đúng ứng viên", "CANDIDATE_UNIQUENESS_UNPROVEN"),
    (
        r"Điều kiện đã đáp ứng phải có dữ kiện|Nhận định áp dụng vào hàng hóa chưa có trích đoạn",
        "APPLICATION_FACTS_REQUIRED",
    ),
    (r"Không dùng yêu cầu tra cứu hoặc nội dung pháp lý", "NON_PRODUCT_QUOTE"),
    (r"Không được loại nhánh hoặc xác nhận thuộc tính", "EXCLUSION_UNPROVEN"),
    (
        r"Thuộc tính phân biệt chưa biết phải có câu hỏi|Thuộc tính phân biệt phải gắn",
        "BRANCH_PROOF_UNPROVEN",
    ),
    (
        r"phải dùng trích đoạn thật|phải trích đúng dữ kiện|không khớp nguyên văn",
        "FACT_QUOTE_INVALID",
    ),
    (r"tham chiếu chứng cứ không có|tham chiếu ID ngoài ngữ cảnh", "UNREGISTERED_EVIDENCE"),
]


def metadata(code: str) -> dict:
    return SPECS.get(
        code,
        {"cause": "UNCLASSIFIED", "owner": "validator", "safe_action": "WITHHOLD_AND_DIAGNOSE"},
    ).copy()


def diagnostic(error: str, phase: str = "") -> dict:
    if hasattr(error, "diagnostic"):
        value = error.diagnostic.copy()
    else:
        location, separator, message = str(error).partition(": ")
        located = bool(
            separator
            and (
                location.startswith("/") or re.fullmatch(r"R\d+(?:\.C\d+)?(?:[./][^:]+)?", location)
            )
        )
        description = message if located else str(error)
        coded = re.match(r"^\[([A-Z][A-Z0-9_]+)\]\s*", description)
        code = (
            coded[1]
            if coded
            else next(
                (c for pattern, c in LEGACY_PATTERNS if re.search(pattern, description)),
                "VALIDATION_ERROR",
            )
        )
        if (
            code == "VALIDATION_ERROR"
            and located
            and (location.startswith("/") or description.startswith("/"))
        ):
            code = "SCHEMA_VIOLATION"
        value = {
            "code": code,
            "path": location if located else "",
            "message": description[coded.end() :] if coded else description,
        }
    return {**metadata(value["code"]), **value, **({"phase": phase} if phase else {})}
