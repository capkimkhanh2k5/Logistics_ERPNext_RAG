"""Instructions for repairing a response after deterministic validation."""

import json

REPAIR_PROMPT = (
    "Hãy sửa các lỗi kiểm tra sau, chỉ sử dụng các nguồn đã cung cấp: {errors}"
    ". Đặt nhãn dạng [S1] ngay trong trường answer. "
    "Viết các phần diễn giải bằng tiếng Việt; giữ nguyên tên trường JSON, "
    "mã trạng thái và trích đoạn nguyên văn. Nếu lỗi trích đoạn, chọn đoạn ngắn liên tục "
    "thực sự có trong nguồn, giữ nguyên mọi ký tự; không chép lại cả nguồn dài theo trí nhớ. "
    "Trả JSON ngắn gọn, đúng schema."
)


def format_repair_prompt(errors: list[str]) -> str:
    return REPAIR_PROMPT.format(errors=json.dumps(errors, ensure_ascii=False))


PRODUCT_REVIEW_REPAIR_PROMPT = (
    "Sửa kết quả kiểm tra sản phẩm theo các lỗi sau: {errors}. "
    "Giữ nguyên nhiệm vụ kiểm tra đúng một candidate và chỉ dùng question/sources đã cấp. "
    "Không mặc định candidate đúng và không đổi dữ kiện để khớp nhánh. "
    "Chỉ hỏi dữ kiện hàng hóa còn thiếu; việc loại các nhánh HS, giải thích luật hoặc cung cấp "
    "Chú giải thuộc trách nhiệm hệ thống. Nếu dữ kiện đã loại trừ candidate, trả REQUIRES_REVIEW "
    "với reason cụ thể và condition_checks nêu điều kiện bị bác bỏ. "
    "Nếu thiếu thuộc tính đã được nguồn xác định, trả MISSING_PRODUCT_INFO với câu hỏi cụ thể. "
    "Giữ nguyên từng ký tự của user_quote và source_quote; không sửa chữ hoa, dấu hoặc nối đoạn. "
    "Trả JSON đúng PRODUCT_REVIEW_SCHEMA, không thêm văn bản ngoài JSON."
)


def format_product_review_repair_prompt(errors: list[str]) -> str:
    return PRODUCT_REVIEW_REPAIR_PROMPT.format(errors=json.dumps(errors, ensure_ascii=False))
