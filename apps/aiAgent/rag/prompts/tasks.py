"""Task instructions and user-fact labels for grounded HS/QA generation."""

TASK_INSTRUCTIONS = {
    "hs": (
        "Trước tiên kiểm tra mâu thuẫn chưa đính chính và thuộc tính còn thiếu: "
        "dùng MISSING_PRODUCT_INFO, mã rỗng khi chưa rõ. Chỉ đối chiếu dữ kiện hiện tại, "
        "bỏ dữ kiện người dùng đã đính chính. Chỉ đề xuất mã HS 8 chữ số khi đủ chứng cứ: status=RECOMMENDATION, "
        "suggested_hs_code=mã đã chọn. Nếu chưa thể kết luận, để trường mã rỗng."
    ),
    "qa": "Trả lời câu hỏi QA có dẫn nguồn; dùng status=ANSWERED khi đủ chứng cứ, không đề xuất mã HS.",
    "auto": (
        "Tự xác định nhu cầu từ câu hỏi gốc và thông tin người dùng bổ sung. "
        "Nếu người dùng yêu cầu phân loại hàng hóa, áp dụng quy tắc HS: chỉ dùng "
        "RECOMMENDATION kèm mã ứng viên 8 chữ số khi đủ thuộc tính và chứng cứ. "
        "Nếu hỏi kiến thức, quy định, hồ sơ hoặc giải thích mã có sẵn, trả lời QA có dẫn nguồn: "
        "ANSWERED, mã đề xuất rỗng và alternatives=[]. Việc nhắc tới HS/GIR không tự đồng nghĩa "
        "với yêu cầu phân loại hàng hóa. Nếu cần cả phân loại và hỏi đáp, trả lời cả hai theo nguồn; "
        "chỉ đề xuất HS khi phần phân loại đủ căn cứ. intent_advice chỉ là gợi ý, có thể sai; "
        "không để gợi ý này quyết định thay câu hỏi. Khi nhu cầu chưa rõ hoặc thiếu thuộc tính, "
        "dùng MISSING_PRODUCT_INFO, hỏi thông tin cụ thể, không yêu cầu người dùng chọn HS/QA. "
        "Khi thiếu nguồn, dùng INSUFFICIENT_LEGAL_EVIDENCE hoặc REQUIRES_REVIEW."
    ),
}

USER_SUPPLEMENT_TEMPLATE = "Thông tin người dùng bổ sung ở lượt {turn}: {text}"

SOURCE_COMPARISON_CLARIFICATION = (
    "Please provide product specifications needed to compare these cited source conditions."
)
