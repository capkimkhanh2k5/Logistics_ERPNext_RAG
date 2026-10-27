"""Independent product-to-condition review; shared decision policy owns statuses."""

from rag.prompts.core.policy import DECISION_POLICY, EVIDENCE_POLICY
from rag.prompts.core.proof import PROOF_INSTRUCTION

REVIEW_POLICY = """Mọi required_citation_evidence_ids đang áp dụng cần được đối chiếu.
Điều kiện con được hoãn khi điều kiện cha còn thiếu đã có check và câu hỏi cùng nguồn;
không phát hành mã chi tiết hoặc coi phần hoãn là đã đáp ứng.
SATISFIED có chứng minh; MISSING_PRODUCT_INFO thiếu thuộc tính có nguồn; CONTRADICTED bị bác bỏ;
INSUFFICIENT_LEGAL_EVIDENCE thiếu căn cứ; UNRESOLVED_APPLICATION tranh chấp khi đã có căn cứ.
Chỉ SUPPORTED cần mọi điều kiện bắt buộc SATISFIED, không còn ngoại lệ/phản chứng chưa xử lý.
REJECTED chỉ loại ứng viên đang xét bằng điều kiện cần của chính nó; không hỏi dữ kiện cho mã đã loại.
Lỗi ID/trích đoạn là lỗi biểu diễn, không tự chứng minh thiếu dữ kiện hoặc luật.
proposed_answer là giả thuyết cần kiểm chứng, không là nguồn. Giữ đúng chủ thể, phạm vi,
phủ định, AND/OR, ngoại lệ và đính chính; không suy thuộc tính kỹ thuật từ tên thương mại.
Định nghĩa nguồn và điều kiện cấp cha cần dữ kiện tường minh, đại lượng khác bản chất không thay nhau.
"""

PRODUCT_REVIEW_PROMPT = (
    EVIDENCE_POLICY
    + "\n"
    + DECISION_POLICY
    + "\n"
    + REVIEW_POLICY
    + "\n"
    + """Bạn kiểm tra độc lập candidate HS và các nhánh đối chứng được cấp.
Trả schema tiếng Việt, reason ngắn mô tả điều kiện đã đáp ứng hoặc còn chặn; không đề xuất mã khác.

- user_context.statements là lời người dùng theo lượt, ID chỉ xác nhận nguồn gốc.
  Nhận diện chủng loại đủ rõ bằng ngôn ngữ chung; cấu hình/thông số cần dữ kiện riêng.
  Kiểm tra proposed_answer không thêm/đổi thuộc tính; không coi im lặng là phủ định.
- condition_checks tách từng điều kiện mã/cấp cha/nhánh/Chú giải quyết định. Mỗi check
  có evidence_id, criterion_quote nguyên văn mệnh đề đủ phạm vi (nếu schema hỗ trợ),
  assessment, fact_ids và user_quotes trích đúng đoạn hỗ trợ từ các ID đó.
  SATISFIED cần dữ kiện thật đúng chủ thể. Dữ kiện đã có nhưng chọn quote sai cần đọc lại,
  không hỏi người dùng để sửa lỗi trích. Nguồn nhiều mệnh đề cần kiểm tra mọi điều kiện áp dụng.
  Điều kiện/chú giải không có dữ kiện người dùng chứng minh trực tiếp và không phải nguồn bắt buộc
  của mã đang xét: nếu không áp dụng cho sản phẩm thì đánh giá là NOT_APPLICABLE (hoặc CONTRADICTED nếu loại trừ).
  Tuyệt đối không đánh giá SATISFIED nếu fact_ids rỗng khi điều kiện đòi hỏi thuộc tính hàng hóa.
- Chuỗi graph phải VERIFIED, không suy cấp cha từ tiền tố. Metadata không chứng minh
  sản phẩm phù hợp. Nguồn bắt buộc không được NOT_APPLICABLE để bỏ qua điều kiện.
  Khi điều kiện bị bác bỏ dùng CONTRADICTED và xét ứng viên còn có căn cứ.
- candidate_assessments bao phủ từng mã trong codes. POSSIBLE chưa bị bác bỏ;
  RULED_OUT cần nguồn quyết định thuộc chính nhánh đó cùng fact_ids/user_quotes thật;
  thiếu căn cứ dùng INSUFFICIENT_LEGAL_EVIDENCE. Không loại theo thứ hạng hay không thấy mã.
- branch_checks tách thuộc tính độc lập cho mỗi parent_code. Toàn mảng phủ branch_options.
  KNOWN có dữ kiện thật; MISSING không có dữ kiện và có câu hỏi cùng mệnh đề;
  DEFERRED chỉ khi điều kiện cha chưa biết đã có câu hỏi có nguồn, không phát hành mã.
- SUPPORTED cần duy nhất candidate còn hợp lệ, mọi điều kiện bắt buộc chứng minh đủ,
  mọi chiều quyết định KNOWN, missing_codes rỗng. Nhánh phần dư không được mặc định.
  Điều khoản giới hạn phạm vi không áp sang đối tượng khác. Tiêu đề khái quát không đủ
  cho cơ chế áp dụng cần được giải thích; thiếu căn cứ dùng trạng thái theo policy chung.
- MISSING_PRODUCT_INFO chỉ hỏi thuộc tính thực tế còn quyết định, mỗi câu một thuộc tính,
  criterion_quote đúng mệnh đề nguồn, giữ phạm vi/ngoại lệ. Không hỏi lại dữ kiện đã rõ
  hoặc số chính xác khi giới hạn đủ đối chiếu. product_type có thể không cần luật;
  nhận diện chủng loại không xác nhận cấu hình hay trạng thái trình bày.
- clarifications chỉ ở MISSING_PRODUCT_INFO; missing_legal_evidence chỉ ở
  INSUFFICIENT_LEGAL_EVIDENCE. Nguồn thiếu là gap context, không khẳng định cả kho thiếu luật.
  Không tự viết nhãn, source_quote hay ID mới; backend dựng citation.
"""
)

PRODUCT_REVIEW_PROMPT += "\n" + PROOF_INSTRUCTION
