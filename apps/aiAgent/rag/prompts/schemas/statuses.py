"""One vocabulary for public statuses and internal candidate outcomes."""

PUBLIC_STATUSES = {
    "ANSWERED": "Chỉ khi mục tiêu giải thích/so sánh/điều kiện đã hoàn tất có nguồn; không thay cho kết quả phân loại.",
    "RECOMMENDATION": "Chỉ cho phân loại: một mã đúng cấp có nguồn, đã chứng minh điều kiện và đối chứng; không dùng khi còn nhánh chưa kiểm tra.",
    "MISSING_PRODUCT_INFO": "Chỉ khi thuộc tính hàng hóa/vụ việc còn thiếu thực sự quyết định và có căn cứ hỏi; không dùng cho lỗi ID, quote hoặc thiếu luật.",
    "INSUFFICIENT_LEGAL_EVIDENCE": "Thiếu nguồn quy định hoặc căn cứ áp dụng; không yêu cầu người dùng cung cấp luật.",
    "REQUIRES_REVIEW": "Cách áp dụng còn tranh chấp khi căn cứ đã có; không dùng thay lỗi kỹ thuật hay một ứng viên đã bị bác bỏ.",
}

CANDIDATE_OUTCOMES = {
    "SUPPORTED": "SUPPORTED",
    "REJECTED": "REJECTED",
    "MISSING_PRODUCT_INFO": "NEEDS_FACT",
    "INSUFFICIENT_LEGAL_EVIDENCE": "LEGAL_GAP",
    "REQUIRES_REVIEW": "APPLICATION_UNRESOLVED",
}

REVIEW_STATUSES = {
    "SUPPORTED": "Chỉ khi đủ điều kiện bắt buộc đang áp dụng và duy nhất một ứng viên sau đối chứng; không dùng khi còn điều kiện chưa biết.",
    "REJECTED": "Chỉ loại ứng viên đang xét bằng phản chứng đúng điều kiện cần của chính nhánh; không coi là kết luận cho mọi đối thủ.",
    **{
        key: value
        for key, value in PUBLIC_STATUSES.items()
        if key not in {"ANSWERED", "RECOMMENDATION"}
    },
}


def status_description(allowed: list[str] | None = None) -> str:
    return " ".join(f"{state}: {PUBLIC_STATUSES[state]}" for state in (allowed or PUBLIC_STATUSES))


def review_status_description() -> str:
    return " ".join(f"{state}: {description}" for state, description in REVIEW_STATUSES.items())
