"""Small wire-format fixtures for QA integration runners."""

import json


def qa_response(messages, status="ANSWERED"):
    payload = json.loads(messages[1]["content"])
    return {
        "status": status,
        "claims": [
            {
                "kind": "LEGAL_ANALYSIS",
                "text": "Căn cứ được nêu trong nguồn.",
                "evidence_ids": [payload["sources"][0]["evidence_id"]],
                "fact_ids": [],
            }
        ],
        "suggested_hs_code": "",
        "missing_legal_evidence": [],
        "clarifications": [
            {
                "question": "Bạn muốn hỏi loại tài liệu nào?",
                "attribute": "question_scope",
                "evidence_ids": [],
            }
        ]
        if status == "MISSING_PRODUCT_INFO"
        else [],
    }
