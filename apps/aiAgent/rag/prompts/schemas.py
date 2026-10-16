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
            "description": "Với HS và status=RECOMMENDATION, điền đúng mã ứng viên 8 chữ số đã chọn. Để rỗng với QA hoặc khi chưa thể kết luận.",
        },
        "alternatives": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Luôn để []; không phát hành mã khác chưa qua kiểm tra độc lập.",
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
        "reason": {
            "type": "string",
            "minLength": 1,
            "description": "Giải thích ngắn kết quả kiểm tra và điều kiện gây chặn nếu có; chỉ dựa trên dữ kiện và nguồn đã cấp, không đề xuất mã HS.",
        },
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
        "condition_checks": {
            "type": "array",
            "description": "Đối chiếu từng điều kiện quyết định trong nguồn với dữ kiện người dùng, gồm điều kiện tại cấp cha và nhánh. Không gộp nhiều điều kiện độc lập thành một kiểm tra.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "source_label": {"type": "string"},
                    "source_quote": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Trích nguyên văn điều kiện đang đối chiếu, giữ ngưỡng, đơn vị, phủ định và ngoại lệ liên quan.",
                    },
                    "assessment": {
                        "type": "string",
                        "enum": [
                            "SATISFIED",
                            "MISSING_PRODUCT_INFO",
                            "CONTRADICTED",
                            "INSUFFICIENT_LEGAL_EVIDENCE",
                            "UNRESOLVED_APPLICATION",
                            "NOT_APPLICABLE",
                        ],
                    },
                    "product_fact_indices": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Chỉ số từ 0 trong product_facts chứng minh riêng điều kiện này; [] nếu chưa có dữ kiện xác nhận.",
                    },
                },
                "required": ["source_label", "source_quote", "assessment", "product_fact_indices"],
            },
        },
        "missing_information": ANSWER_SCHEMA["properties"]["missing_information"],
        "missing_legal_evidence": ANSWER_SCHEMA["properties"]["missing_legal_evidence"],
    },
    "required": [
        "status",
        "reason",
        "product_facts",
        "condition_checks",
        "missing_information",
        "missing_legal_evidence",
    ],
}


DECISION_REVIEW_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "request_kind": {"type": "string", "enum": ["HS", "QA", "MIXED", "UNCLEAR"]},
        "identity_status": {
            "type": "string",
            "enum": ["IDENTIFIED", "UNCONFIRMED", "NOT_APPLICABLE"],
        },
        "product_type": {"type": "string"},
        "product_type_quote": {"type": "string"},
        "decision": {"type": "string", "enum": ["KEEP", "CLARIFY"]},
        "reason": {"type": "string", "minLength": 1},
        "retained_qa": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "answer": {"type": "string"},
                "citations": ANSWER_SCHEMA["properties"]["citations"],
            },
            "required": ["answer", "citations"],
        },
        "clarifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "question": {"type": "string", "minLength": 1},
                    "basis": {
                        "type": "string",
                        "enum": ["PRODUCT_IDENTITY", "QUESTION_SCOPE", "SOURCE_CONDITION"],
                    },
                    "source_label": {"type": "string"},
                    "source_quote": {"type": "string"},
                },
                "required": ["question", "basis", "source_label", "source_quote"],
            },
        },
    },
    "required": [
        "request_kind",
        "identity_status",
        "product_type",
        "product_type_quote",
        "decision",
        "reason",
        "retained_qa",
        "clarifications",
    ],
}


# Wire contracts reference immutable backend registries. ANSWER_SCHEMA remains the
# public terminal/notebook result contract; older saved contexts can still replay it.
_IDS = {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True}
_CLAIMS = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "kind": {"type": "string", "enum": ["PRODUCT_FACT", "LEGAL_ANALYSIS", "CONCLUSION"]},
            "text": {"type": "string", "minLength": 1},
            "evidence_ids": _IDS,
            "fact_ids": _IDS,
        },
        "required": ["kind", "text", "evidence_ids", "fact_ids"],
    },
}
_CLARIFICATIONS = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "question": {"type": "string", "minLength": 1},
            "attribute": {
                "type": "string",
                "minLength": 1,
                "description": "Tên thuộc tính do điều kiện nguồn xác định; không giới hạn danh mục. product_type/question_scope dành cho nhận diện hoặc phạm vi.",
            },
            "evidence_ids": _IDS,
        },
        "required": ["question", "attribute", "evidence_ids"],
    },
}

MODEL_ANSWER_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": ANSWER_SCHEMA["properties"]["status"],
        "claims": {**_CLAIMS, "minItems": 1},
        "suggested_hs_code": ANSWER_SCHEMA["properties"]["suggested_hs_code"],
        "clarifications": _CLARIFICATIONS,
        "missing_legal_evidence": ANSWER_SCHEMA["properties"]["missing_legal_evidence"],
    },
    "required": [
        "status",
        "claims",
        "suggested_hs_code",
        "clarifications",
        "missing_legal_evidence",
    ],
}

MODEL_PRODUCT_REVIEW_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": PRODUCT_REVIEW_SCHEMA["properties"]["status"],
        "reason": PRODUCT_REVIEW_SCHEMA["properties"]["reason"],
        "condition_checks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "evidence_id": {"type": "string", "minLength": 1},
                    "assessment": PRODUCT_REVIEW_SCHEMA["properties"]["condition_checks"]["items"][
                        "properties"
                    ]["assessment"],
                    "fact_ids": _IDS,
                    "user_quotes": {"type": "array", "items": {"type": "string", "minLength": 1}},
                },
                "required": ["evidence_id", "assessment", "fact_ids", "user_quotes"],
            },
        },
        "clarifications": _CLARIFICATIONS,
        "missing_legal_evidence": ANSWER_SCHEMA["properties"]["missing_legal_evidence"],
    },
    "required": [
        "status",
        "reason",
        "condition_checks",
        "clarifications",
        "missing_legal_evidence",
    ],
}

MODEL_DECISION_REVIEW_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "request_kind": DECISION_REVIEW_SCHEMA["properties"]["request_kind"],
        "identity_status": DECISION_REVIEW_SCHEMA["properties"]["identity_status"],
        "identity_fact_ids": _IDS,
        "product_type": {"type": "string"},
        "decision": DECISION_REVIEW_SCHEMA["properties"]["decision"],
        "reason": DECISION_REVIEW_SCHEMA["properties"]["reason"],
        "retained_qa": _CLAIMS,
        "clarifications": _CLARIFICATIONS,
    },
    "required": [
        "request_kind",
        "identity_status",
        "identity_fact_ids",
        "product_type",
        "decision",
        "reason",
        "retained_qa",
        "clarifications",
    ],
}
