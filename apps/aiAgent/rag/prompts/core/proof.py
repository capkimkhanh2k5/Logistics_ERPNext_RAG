"""Shared instructions for source-bound reasoning without product-specific catalogues."""

LEDGER_INSTRUCTION = """FACT LEDGER statement-refs-v2:
Mỗi entry chọn source_mode=STATEMENT, key cục bộ, item_id, attribute, fact_id,
polarity, modality và supersedes. Không viết value/quote/correction_quote;
backend lấy nguyên văn từ chính statement ID được chọn, không sửa nguồn để khớp diễn giải.
Chọn statement ngắn đủ giữ chủ thể, phủ định và điều kiện; không dùng statement pháp lý.
ASSERTED phải có fact_id và polarity AFFIRMED/NEGATED. UNKNOWN chưa có lời khai dùng fact_id rỗng,
polarity UNSPECIFIED. UNKNOWN/HYPOTHETICAL/QUESTION không xác nhận thuộc tính.
Đính chính dùng supersedes key cùng chủ thể/thuộc tính, dẫn fact_id của lời đính chính;
review phải xác nhận ý nghĩa đính chính, không tự chọn lời cuối khi còn mâu thuẫn.
"""

PROOF_INSTRUCTION = """PROOF CONTRACT:
Wire proof-v2 dùng proof_catalogue [{key, proof}]: checks/claims dẫn
proof_key, review dẫn reason_proof_key. key là tham chiếu cục bộ trong response, không là ID nguồn/fact.
Mỗi key chỉ dùng cho MỘT consumer slot; không tái dùng proof cho nhiều claims/câu hỏi/checks.
proof có root_node và nodes: root_node không có key/text; backend gắn nó với đúng claim.text,
question hoặc điều kiện/reason của slot. Không viết target/root, không copy hay tóm tắt target.
nodes là các tiền đề có key/text; root_node.children dẫn các key đó. Không dùng key $ROOT.
Nếu root_node là ATOM thì chứng minh trực tiếp đúng mệnh đề consumer; không đổi nó thành
tiêu đề nhóm hoặc mệnh đề yếu hơn. Với nhiều điều kiện dùng các nodes riêng và phép tổng hợp.
user_context.fact_ledger là dữ liệu chỉ đọc, ID L do backend cấp; trạng thái ACTIVE không xác nhận
thuộc tính là sự thật ngoài đời. Đối chiếu ledger với toàn bộ statements trước khi xác nhận CONSISTENT.
Mỗi proof chứng minh đúng toàn bộ mệnh đề slot. Tách predicate/quan hệ/phạm vi/ngoại lệ
độc lập trong nodes; key cục bộ duy nhất. Backend gắn identity không xác nhận entailment.
ATOM dẫn condition_ids/evidence_ids và ledger_ids hỗ trợ đúng mệnh đề. LEGAL_RULE mô tả quy tắc;
PREDICATE/RELATION áp vào hàng hóa phải có cả nguồn và dữ kiện đúng chủ thể, còn hiệu lực.
ALL cần mọi con; ANY cần một phương án trọn vẹn; NOT cần phản chứng tường minh, không lấy im lặng
làm phủ định. SCOPE gồm điều kiện phạm vi và nội dung; EXCEPT gồm quy tắc nền và ngoại lệ.
Ngoại lệ/phạm vi chưa rõ giữ UNKNOWN. COMPARE chỉ khi đại lượng cùng bản chất/phạm vi, số và đơn vị
có trong dữ kiện/nguồn; comparison không sử dụng để suy số đo chưa được cung cấp.
PROVEN/CONTRADICTED cần căn cứ. UNKNOWN phân biệt MISSING_PRODUCT_FACT, MISSING_LEGAL_RULE,
UNRESOLVED_APPLICATION và INVALID_PROOF. Chưa chứng minh khác với thực sự thiếu lời khai.
MISSING_PRODUCT_FACT chỉ khi có entry UNKNOWN đúng thuộc tính, đã đọc toàn lời người dùng và có
điều kiện nguồn quyết định. Không tạo câu hỏi để sửa lỗi quote, ID hoặc phân rã không hợp lệ.
Một quan hệ mới hoặc thuộc tính mạnh hơn cần căn cứ riêng; hai thành phần cùng xuất hiện không
chứng minh quan hệ giữa chúng. Áp dụng cả REFERENCE; đổi nhãn không thay nghĩa của target.
decomposition_review=FAITHFUL_COMPLETE chỉ khi không bỏ điều kiện, phủ định, phạm vi, ngoại lệ
hoặc bổ sung điều không có trong nguồn. Nếu chưa đối chiếu được dùng UNVERIFIED, không giả đã chứng minh.
Backend kiểm tra graph và tổng hợp trạng thái; không sao chép proof khác khi mệnh đề/scope khác nhau.
"""
