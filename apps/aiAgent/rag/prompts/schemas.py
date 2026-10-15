"""Strict JSON response contracts for answer generation and product review."""

ANSWER_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": {
            "type": "string",
            "description": "QA: ANSWERED khi đủ chứng cứ, hoặc trạng thái chưa thể kết luận. HS: RECOMMENDATION kèm mã đã chọn, hoặc trạng thái chưa thể kết luận; không dùng ANSWERED cho HS.",
            "enum": [
                "ANSWERED",
                "RECOMMENDATION",
                "MISSING_PRODUCT_INFO",
                "INSUFFICIENT_LEGAL_EVIDENCE",
                "REQUIRES_REVIEW",
            ],
        },
        "answer": {
            "type": "string",
            "description": "Câu trả lời tiếng Việt có nhãn dẫn nguồn [S1], [S2] ngay trong nội dung. Mọi citation được liệt kê phải xuất hiện ở đây.",
        },
        "suggested_hs_code": {
            "type": "string",
            "description": "Với HS và status=RECOMMENDATION, điền đúng mã ứng viên 8 chữ số đã chọn, ví dụ 85171300. Để rỗng với QA hoặc khi chưa thể kết luận.",
        },
        "alternatives": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Các mã HS ứng viên 8 chữ số khác cần cân nhắc, chỉ lấy từ danh sách được cung cấp. Để rỗng với QA.",
        },
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"label": {"type": "string"}, "quote": {"type": "string"}},
                "required": ["label", "quote"],
            },
        },
        "missing_information": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "description": "Chỉ dùng với MISSING_PRODUCT_INFO: dữ kiện hàng hóa/hồ sơ người dùng cần cung cấp. Không yêu cầu mã HS, mô tả pháp lý, GIR hoặc Chú giải. Các trạng thái khác để [].",
        },
        "missing_legal_evidence": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "description": "Chỉ dùng với INSUFFICIENT_LEGAL_EVIDENCE: nguồn pháp lý hoặc quan hệ HS còn thiếu trong retrieval/corpus. Đây là chẩn đoán hệ thống, không phải yêu cầu người dùng. Các trạng thái khác để [].",
        },
    },
    "required": [
        "status",
        "answer",
        "suggested_hs_code",
        "alternatives",
        "citations",
        "missing_information",
        "missing_legal_evidence",
    ],
}


PRODUCT_REVIEW_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": {
            "type": "string",
            "enum": [
                "SUPPORTED",
                "MISSING_PRODUCT_INFO",
                "INSUFFICIENT_LEGAL_EVIDENCE",
                "REQUIRES_REVIEW",
            ],
        },
        "product_facts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"fact": {"type": "string"}, "user_quote": {"type": "string"}},
                "required": ["fact", "user_quote"],
            },
        },
        "missing_information": ANSWER_SCHEMA["properties"]["missing_information"],
        "missing_legal_evidence": ANSWER_SCHEMA["properties"]["missing_legal_evidence"],
    },
    "required": ["status", "product_facts", "missing_information", "missing_legal_evidence"],
}
