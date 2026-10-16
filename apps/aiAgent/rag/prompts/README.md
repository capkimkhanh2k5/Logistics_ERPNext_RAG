# Quản lý prompt RAG

Các chỉ dẫn model do ứng dụng định nghĩa nằm trong thư mục này. Module xử lý chỉ import và lắp dữ liệu vào template; sửa nội dung tại đây rồi khởi động lại phiên RAG để nạp bản mới.

## Sửa nội dung ở đâu?

- [system.py](system.py): `SYSTEM_PROMPT`, vai trò trợ lý, quyền sở hữu dữ kiện/chứng cứ, chọn trạng thái, điều kiện đề xuất và dẫn nguồn.
- [product_review.py](product_review.py): `PRODUCT_REVIEW_PROMPT`, kiểm tra độc lập dữ kiện hàng hóa với điều kiện của nhánh được đề xuất.
- [decision_review.py](decision_review.py): `DECISION_REVIEW_PROMPT` và template repair, kiểm tra nhận diện hàng hóa/phạm vi câu hỏi trước khi chấp nhận quyết định thiếu chứng cứ hoặc cần thẩm định.
- [tasks.py](tasks.py): `TASK_INSTRUCTIONS` cho HS/QA/Auto; `USER_SUPPLEMENT_TEMPLATE` đánh dấu dữ kiện người dùng bổ sung. `SOURCE_COMPARISON_CLARIFICATION` giữ lời nhắc của API so sánh nguồn cũ, không phải câu hỏi do luồng Auto hiện tại tự sinh.
- [repair.py](repair.py): `REPAIR_PROMPT`/`format_repair_prompt()` sửa câu trả lời; `PRODUCT_REVIEW_REPAIR_PROMPT`/`format_product_review_repair_prompt()` sửa Product Review theo danh sách lỗi validation.
- [provider_format.py](provider_format.py): `JSON_SCHEMA_PROMPT` và `format_json_schema_prompt()`, chỉ dẫn JSON cho nhánh GPT-OSS qua CLIProxyAPI khi gateway không hỗ trợ native schema.
- [reranking.py](reranking.py): instruction truy xuất nguồn, instruction mặc định của Qwen, template chat/scoring và version dùng trong cache reranker.
- [query_planning.py](query_planning.py): diễn giải từ khóa tìm kiếm dùng chung cho tên hàng/chủ đề pháp lý. Không chứa ví dụ theo hãng, danh sách danh mục hoặc mã HS. Kết quả là giả thuyết truy xuất, không thuộc registry dữ kiện.
- [schemas.py](schemas.py): `MODEL_*_SCHEMA` là contract model dùng ID của registry. `ANSWER_SCHEMA` giữ contract kết quả công khai; các schema review cũ dùng cho chuẩn hóa nội bộ và replay context cũ.

## Các nơi sử dụng

- `rag/llm/context.py` ghép câu hỏi, dữ kiện bổ sung, nguồn và chỉ dẫn tác vụ với system prompt.
- `rag/llm/answering.py` sử dụng prompt kiểm tra sản phẩm và prompt sửa lỗi.
- `rag/llm/decision_review.py` kiểm tra độc lập quyết định chưa kết luận; không phát hành mã HS và không coi câu trả lời trước là dữ kiện người dùng.
- `rag/llm/cliproxy_client.py` bổ sung chỉ dẫn định dạng theo khả năng của provider.
- `rag/retrieval/rerankers.py` dựng đầu vào Qwen bằng template trong `reranking.py`.
- `rag/retrieval/query_planning.py` gọi client chung để sinh từ khóa, kiểm tra schema/anchor và quay về câu hỏi gốc khi lỗi; các chỉ dẫn nằm trong `prompts/query_planning.py`.
- `config/retrieval.py` giữ tên import tương thích `INSTRUCTION`, tham chiếu trực tiếp `SOURCE_RELEVANCE_INSTRUCTION`; runtime và các script benchmark dùng cùng nội dung này.
- `rag/retrieval/retriever.py` lấy lời nhắc cho API so sánh nguồn từ `tasks.py`.

## Phân biệt prompt và dữ liệu

Câu hỏi, dữ kiện người dùng, nguồn pháp lý, schema và danh sách lỗi được truyền dưới dạng dữ liệu vào các template. Giá trị được chèn không tiếp tục được xử lý như một template khác, kể cả khi chứa dấu ngoặc nhọn.

Các điều kiện chặn mã HS, kiểm tra nguồn, schema và quyền sở hữu dữ kiện vẫn được thực thi trong code. Sửa văn bản prompt không thay thế việc sửa validator khi contract thay đổi. Thông báo giao diện terminal thuộc `rag/api/cli.py`; các thông báo lỗi validation là phản hồi kiểm tra, không phải nơi định nghĩa chỉ dẫn tác vụ.

Product Review bắt buộc có `reason`, chỉ hỏi thuộc tính còn thiếu trong `MISSING_PRODUCT_INFO` và dùng `UNRESOLVED_APPLICATION` khi có dữ kiện nhưng chưa đối chiếu được với điều kiện. `REQUIRES_REVIEW` không được thay thế câu hỏi bổ sung nếu chỉ thiếu thuộc tính. Runtime sửa review tối đa một lần; nếu vẫn lỗi, chỉ hiển thị chẩn đoán an toàn và nguồn lấy từ context. Model tham chiếu `fact_ids` (ID lời người dùng) và `evidence_id`; `user_quotes` phải có thật trong các ID được chọn, không tự viết lại trích đoạn để tạo bằng chứng. Lời người dùng và trích đoạn dùng cho validator lấy từ registry nguồn gốc; chúng chưa tự động trở thành sự thật đã xác minh.

Decision Review chạy cho phản hồi thiếu chứng cứ/cần thẩm định hợp lệ chưa được Product Review kiểm tra, và khi ngữ cảnh HS/Auto không có nguồn. Nó tách nhu cầu hỏi đáp/phân loại khỏi việc đã nhận diện sản phẩm; `identity_fact_ids` phải tham chiếu lời người dùng làm căn cứ nhận diện; model diễn giải loại hàng từ ngữ cảnh, không tra registry dòng sản phẩm. Không yêu cầu tên loại hàng nằm nguyên văn trong tên thương mại. Câu hỏi nhận diện không cần nguồn luật; câu hỏi thông số cần ID điều kiện liên quan. QA rõ ràng không bị hỏi nhận diện hàng hóa. Kết quả kỹ thuật không hợp lệ hoặc lỗi provider không được chuyển thành câu hỏi sản phẩm. `/details` ghi riêng thời gian, usage, budget và lý do của bước kiểm tra này.

`rag/llm/quantitative.py` bổ sung guard cho điều kiện định lượng rõ ràng trong nguồn bắt buộc của một Product Review `SUPPORTED`. Số đo phải được chứng minh từ `user_quote` của dữ kiện được tham chiếu, không lấy từ lời diễn giải `fact` hoặc tên model sản phẩm. Guard đọc toàn nguồn bắt buộc để tránh bỏ qua điều kiện trong trích đoạn ngắn. Nếu chưa chứng minh được, runtime yêu cầu sửa review một lần; guard không tự chọn mã hoặc tự sinh câu hỏi. Bộ phân tích chỉ hỗ trợ các đơn vị và so sánh đã định nghĩa, không thay thế việc đánh giá ngoại lệ, nhánh lựa chọn hoặc toàn bộ ngữ nghĩa pháp lý.

Generation, Product Review, Decision Review và repair giữ tiếng Việt; tên trường, ID, trạng thái và trích đoạn nguồn giữ nguyên. Wrapper JSON và template/instruction Qwen giữ ngôn ngữ của bản trước refactor.

Không có cấu hình riêng theo hãng/dòng sản phẩm hoặc enum thuộc tính theo danh mục. `user_context.statements` giữ lời người dùng và thứ tự lượt; `fact_ids` chỉ là ID nguồn gốc, không xác nhận mọi nội dung trong lời nói là đúng. Model đối chiếu ngữ nghĩa toàn ngữ cảnh, gồm nhận diện loại hàng đủ rõ, giả định, phủ định, mâu thuẫn và đính chính. Product Review còn nhận `proposed_answer` để kiểm tra dữ kiện có bị thêm hoặc đổi nghĩa hay không. `user_quotes` trích nguyên văn lời người dùng được tham chiếu; backend kiểm tra nguồn gốc rồi dựng các trích dẫn. Các điều kiện quyết định và tên thuộc tính cần hỏi xuất phát từ nguồn đang xét.
