"""Instructions for repairing a response after deterministic validation."""

import json

REPAIR_PROMPT = (
    "Hãy sửa các lỗi kiểm tra sau, chỉ sử dụng các nguồn đã cung cấp: {errors}"
    ". Dùng claims với evidence_ids và fact_ids (ID lời người dùng) từ registry; backend tự dựng nhãn và trích đoạn nguyên văn. "
    "Viết các phần diễn giải bằng tiếng Việt; giữ nguyên tên trường JSON, mã trạng thái và ID nguồn/dữ kiện. "
    "Nếu lỗi là câu hỏi dữ kiện lẫn nội dung/mục đích tra cứu mã, sửa câu hỏi chỉ còn thuộc tính hàng hóa; "
    "không đổi sang thiếu chứng cứ pháp lý chỉ để tránh lỗi wording. Lỗi validation không chứng minh thiếu nguồn luật. "
    "Không tự viết nhãn, quote hoặc tạo ID. "
    "Trả JSON ngắn gọn, đúng schema."
)


def format_repair_prompt(errors: list[str]) -> str:
    return REPAIR_PROMPT.format(errors=json.dumps(errors, ensure_ascii=False))


PRODUCT_REVIEW_REPAIR_PROMPT = (
    "Sửa kết quả kiểm tra sản phẩm theo các lỗi sau: {errors}. "
    "Giữ nguyên nhiệm vụ kiểm tra candidate cùng các nhánh đối chứng được cấp; chỉ dùng question/sources và registry hiện tại. "
    "Không mặc định candidate đúng và không đổi dữ kiện để khớp nhánh. "
    "Chỉ hỏi dữ kiện hàng hóa còn thiếu; việc loại các nhánh HS, giải thích luật hoặc cung cấp "
    "Chú giải thuộc trách nhiệm hệ thống. Nếu dữ kiện đã loại trừ candidate, trả REQUIRES_REVIEW "
    "với reason cụ thể và condition_checks nêu điều kiện bị bác bỏ. "
    "Không dùng NOT_APPLICABLE để bỏ điều kiện bắt buộc của candidate; "
    "nếu dữ kiện bác bỏ điều kiện đó, dùng CONTRADICTED. "
    "Nếu thiếu thuộc tính đã được nguồn xác định, trả MISSING_PRODUCT_INFO với câu hỏi cụ thể. "
    "Chỉ dùng evidence_id và fact_ids hiện có. user_quotes phải trích nguyên văn lời người dùng được tham chiếu; không tự tạo dữ kiện hoặc trích đoạn. "
    "Nếu lỗi nằm ở ID/trích đoạn hoặc trích đoạn chưa thể hiện số đo, đọc lại toàn bộ "
    "user_context và sửa ID/trích đoạn. Không đổi sang thiếu dữ kiện hay hỏi lại thuộc tính "
    "đã có chỉ để tránh lỗi validation. Chỉ chép phần mô tả hàng hóa liên quan, giữ đủ "
    "chủ thể, phủ định và mức chắc chắn; không chép yêu cầu hỏi mã/tra cứu làm dữ kiện. "
    "Trả JSON đúng schema được cấp, gồm candidate_assessments/branch_checks nếu schema yêu cầu; không thêm văn bản ngoài JSON."
)


def format_product_review_repair_prompt(errors: list[str]) -> str:
    return PRODUCT_REVIEW_REPAIR_PROMPT.format(errors=json.dumps(errors, ensure_ascii=False))
