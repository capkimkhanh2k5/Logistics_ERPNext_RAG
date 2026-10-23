"""Representation instructions selected by protocol and pending job kinds."""


def wire_instruction(protocol: str, phase: str, job_types: list[str] | None = None) -> str:
    if protocol != "goals-v1":
        return """WIRE registry-v2:
Chọn evidence_ids và fact_ids đã cấp. user_quotes trích nguyên văn lời người dùng đúng
fact_ids; criterion_quote nếu có giữ nguyên mệnh đề nguồn. Backend dựng citation và nhãn;
không tự viết nhãn nguồn hoặc ID trong diễn giải. Không tạo condition_ids mới.
"""
    text = """WIRE goals-v1:
Chỉ chọn fact_ids trong product_fact_ids và phạm vi job; backend dựng user_quotes.
Không viết criterion_quote, criterion_quotes hoặc user_quotes; backend dựng chúng từ registry.
ID thật chỉ chứng minh provenance; vẫn kiểm tra đúng chủ thể, phạm vi và nội dung.
Không viết registry ID hoặc nhãn citation trong text; backend dựng nhãn công khai.
"""
    reviewing = phase in {"product_review", "batched_product_review", "analysis_review"}
    classification = phase != "analysis_review" and (
        job_types is None or "classification" in job_types
    )
    if not reviewing or classification:
        text += """Nguồn cấp condition_spans: clarifications chọn condition_ids thuộc evidence_ids tương ứng.
Câu hỏi thuộc tính có nguồn phải chọn span; nhận diện/phạm vi không có nguồn dùng [].
"""
    if phase in {"product_review", "batched_product_review"} and (
        job_types is None or "classification" in job_types
    ):
        text += """condition_checks chọn condition_id của đúng evidence_id;
branch_checks chọn condition_ids thuộc evidence_ids tương ứng.
reviews/comparison_reviews là object theo result_id/comparison_id trong review_slots.
candidate_group_assessments liệt kê codes đúng tập đã cấp, mỗi mã đúng một lần.
Chỉ gom assessment cho các mã thực sự cùng điều kiện quyết định;
RULED_OUT phải có decisive evidence thuộc điều kiện bắt buộc của mọi thành viên.
Nếu không chứng minh được tương đương thì để nhóm một mã. Backend mở lại slot theo từng mã.
comparison_contexts dùng chung theo item/scope; mỗi ma trận giữ chứng minh riêng.
Review riêng của job giữ condition_checks, status, reason, clarifications; không lặp ma trận.
proof_role và target_codes do backend xác định. prerequisites phải xét trước phần con.
"""
    if phase in {"product_review", "batched_product_review", "analysis_review"} and (
        job_types is None or "analysis" in job_types
    ):
        text += "analysis_reviews là object theo result_id; checks theo claim_index, coverage_checks theo evidence_id đã cấp. Điền đủ slot, không tự thêm ID hoặc điền đánh giá cho đủ khi chưa chứng minh.\n"
    return text
