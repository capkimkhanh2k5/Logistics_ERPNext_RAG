# Quản lý prompt RAG

Các chỉ dẫn model do ứng dụng định nghĩa nằm trong thư mục này. Module xử lý chỉ import và lắp dữ liệu vào template; sửa nội dung tại đây rồi khởi động lại phiên RAG để nạp bản mới.

## Sửa nội dung ở đâu?

Luồng `goals-v1` dùng `request` hợp lệ của planner để truyền mục tiêu/cấp HS và từng mặt hàng xuyên context, generation và validation. `task_answering.py` giữ prompt/schema cho kết quả theo mục tiêu và batch Product Review. Các mô tả luồng đơn mã/Decision Review dưới đây áp dụng cho `registry-v2` fallback/replay. [Contract và recovery](../../docs/GenerationFlow/Goals_And_Recovery.md) ghi các giới hạn và ngân sách.

- [system.py](system.py): `SYSTEM_PROMPT`, vai trò trợ lý, quyền sở hữu dữ kiện/chứng cứ, chọn trạng thái, điều kiện đề xuất và dẫn nguồn.
- [product_review.py](product_review.py): `PRODUCT_REVIEW_PROMPT`, đối chiếu dữ kiện với nhánh đề xuất và các mã đối chứng cùng phân nhóm; hỏi thuộc tính chưa biết còn ảnh hưởng lựa chọn.
- [decision_review.py](decision_review.py): `DECISION_REVIEW_PROMPT` và template repair, kiểm tra nhận diện hàng hóa/phạm vi câu hỏi trước khi chấp nhận quyết định thiếu chứng cứ hoặc cần thẩm định.
- [tasks.py](tasks.py): `TASK_INSTRUCTIONS` cho HS/QA/Auto; `USER_SUPPLEMENT_TEMPLATE` đánh dấu dữ kiện người dùng bổ sung. `SOURCE_COMPARISON_CLARIFICATION` giữ lời nhắc của API so sánh nguồn cũ, không phải câu hỏi do luồng Auto hiện tại tự sinh.
- [repair.py](repair.py): `REPAIR_PROMPT`/`format_repair_prompt()` sửa câu trả lời; `PRODUCT_REVIEW_REPAIR_PROMPT`/`format_product_review_repair_prompt()` sửa Product Review theo danh sách lỗi validation.
- [provider_format.py](provider_format.py): `JSON_SCHEMA_PROMPT` và `format_json_schema_prompt()`, chỉ dẫn JSON cho nhánh GPT-OSS qua CLIProxyAPI khi gateway không hỗ trợ native schema.
- [reranking.py](reranking.py): instruction truy xuất nguồn, instruction mặc định của Qwen, template chat/scoring và version dùng trong cache reranker.
- [query_planning.py](query_planning.py): `QUERY_PLANNING_PROMPT`/`QUERY_PLAN_SCHEMA` cho truy vấn stateless; `TURN_PLANNING_PROMPT`/`TURN_PLAN_SCHEMA` ghép nhận diện hội thoại và từ khóa trong một request trước retrieval. Không chứa danh mục hãng hoặc mã HS. Từ khóa là giả thuyết truy xuất, không thuộc registry dữ kiện; câu hỏi mới chỉ lấy anchor từ tin nhắn mới.
- [conversation.py](conversation.py): chỉ dẫn/schema nhận diện được ghép vào prompt/schema của QueryPlanner; không còn request router riêng. Không viết lại lời người dùng hoặc suy ra thông số; câu hỏi làm rõ đang chờ chỉ là ngữ cảnh nhận diện, không ép nối lượt mới.
- [schemas.py](schemas.py): `MODEL_*_SCHEMA` là contract model dùng ID của registry. `MODEL_DISAMBIGUATION_REVIEW_SCHEMA` thêm `candidate_assessments`/`branch_checks` khi có phạm vi so sánh. `ANSWER_SCHEMA` giữ contract kết quả công khai; các schema review cũ dùng cho chuẩn hóa nội bộ và replay context cũ.

## Các nơi sử dụng

- `rag/llm/context.py` ghép câu hỏi, dữ kiện bổ sung, nguồn và chỉ dẫn tác vụ với system prompt.
- `rag/llm/answering.py` sử dụng prompt kiểm tra sản phẩm và prompt sửa lỗi.
- `rag/llm/disambiguation.py` kiểm tra độ phủ mã/điều kiện nhánh, trạng thái thuộc tính và tham chiếu bằng chứng; không gọi LLM hay tự suy ra thuộc tính theo tên hàng. Dữ liệu so sánh được ghép vào Product Review hiện có.
- `rag/llm/decision_review.py` kiểm tra độc lập quyết định chưa kết luận; không phát hành mã HS và không coi câu trả lời trước là dữ kiện người dùng.
- `rag/llm/cliproxy_client.py` bổ sung chỉ dẫn định dạng theo khả năng của provider.
- `rag/retrieval/rerankers.py` dựng đầu vào Qwen bằng template trong `reranking.py`.
- `rag/retrieval/query_planning.py` gọi client chung một lần qua `plan_turn` để nhận diện và tạo từ khóa; `plan(query)` giữ đường stateless. Quyết định không hợp lệ dừng trước retrieval; quyết định hợp lệ nhưng từ khóa lỗi dùng câu hỏi gốc đã chọn đúng phạm vi. Plan có sẵn được truyền cho retrieval, không gọi planner lại.
- `rag/llm/conversation.py` chỉ ưu tiên chỉ định rõ ràng, kiểm tra schema/anchor và chọn lời người dùng theo action; không gọi client. Lượt chưa rõ yêu cầu chỉ định cách xử lý, không tự ghép ngữ cảnh. Chẩn đoán định tuyến không thuộc bằng chứng sản phẩm/pháp lý.
- `config/retrieval.py` giữ tên import tương thích `INSTRUCTION`, tham chiếu trực tiếp `SOURCE_RELEVANCE_INSTRUCTION`; runtime và các script benchmark dùng cùng nội dung này.
- `rag/retrieval/retriever.py` lấy lời nhắc cho API so sánh nguồn từ `tasks.py`.

## Phân biệt prompt và dữ liệu

Câu hỏi, dữ kiện người dùng, nguồn pháp lý, schema và danh sách lỗi được truyền dưới dạng dữ liệu vào các template. Giá trị được chèn không tiếp tục được xử lý như một template khác, kể cả khi chứa dấu ngoặc nhọn.

Các điều kiện chặn mã HS, kiểm tra nguồn, schema và quyền sở hữu dữ kiện vẫn được thực thi trong code. Sửa văn bản prompt không thay thế việc sửa validator khi contract thay đổi. Thông báo giao diện terminal thuộc `rag/api/cli.py`; các thông báo lỗi validation là phản hồi kiểm tra, không phải nơi định nghĩa chỉ dẫn tác vụ.

Product Review bắt buộc có `reason`, chỉ hỏi thuộc tính còn thiếu trong `MISSING_PRODUCT_INFO` và dùng `UNRESOLVED_APPLICATION` khi có dữ kiện nhưng chưa đối chiếu được với điều kiện. `REQUIRES_REVIEW` không được thay thế câu hỏi bổ sung nếu chỉ thiếu thuộc tính. Runtime sửa review tối đa một lần; nếu vẫn lỗi, chỉ hiển thị chẩn đoán an toàn và nguồn lấy từ context. Model tham chiếu `fact_ids` (ID lời người dùng) và `evidence_id`; `user_quotes` phải có thật trong các ID được chọn, không tự viết lại trích đoạn để tạo bằng chứng. Lời người dùng và trích đoạn dùng cho validator lấy từ registry nguồn gốc; chúng chưa tự động trở thành sự thật đã xác minh.

Decision Review chạy cho phản hồi thiếu chứng cứ/cần thẩm định hợp lệ chưa được Product Review kiểm tra, và khi ngữ cảnh HS/Auto không có nguồn. Nó tách nhu cầu hỏi đáp/phân loại khỏi việc đã nhận diện sản phẩm; `identity_fact_ids` phải tham chiếu lời người dùng làm căn cứ nhận diện; model diễn giải loại hàng từ ngữ cảnh, không tra registry dòng sản phẩm. Không yêu cầu tên loại hàng nằm nguyên văn trong tên thương mại. Câu hỏi nhận diện không cần nguồn luật; câu hỏi thông số cần ID điều kiện liên quan. QA rõ ràng không bị hỏi nhận diện hàng hóa. Kết quả kỹ thuật không hợp lệ hoặc lỗi provider không được chuyển thành câu hỏi sản phẩm. `/details` ghi riêng thời gian, usage, budget và lý do của bước kiểm tra này.

Luồng goals có `candidate_codes` tối đa 3 mã để review từng ứng viên trong cùng batch; xem [contract ứng viên có điều kiện](../../docs/GenerationFlow/Conditional_Candidates.md). `hs_candidates` công khai chỉ chứa kết quả đã được review có nguồn và điều kiện rõ ràng, không phải điểm xác suất.

`rag/llm/quantitative.py` bổ sung guard cho điều kiện định lượng rõ ràng trong nguồn bắt buộc của Product Review `SUPPORTED`, đồng thời kiểm tra các điều kiện đánh dấu `SATISFIED` trong review còn thiếu thông tin. Số đo phải được chứng minh từ `user_quote` của dữ kiện được tham chiếu, không lấy từ lời diễn giải `fact` hoặc tên model sản phẩm. Guard đọc toàn nguồn bắt buộc để tránh bỏ qua điều kiện trong trích đoạn ngắn. Nếu chưa chứng minh được, runtime yêu cầu sửa review một lần; guard không tự chọn mã hoặc tự sinh câu hỏi. Bộ phân tích chỉ hỗ trợ các đơn vị và so sánh đã định nghĩa, không thay thế việc đánh giá ngoại lệ, nhánh lựa chọn hoặc toàn bộ ngữ nghĩa pháp lý.

Generation, Product Review, Decision Review và repair giữ tiếng Việt; tên trường, ID, trạng thái và trích đoạn nguồn giữ nguyên. Wrapper JSON và template/instruction Qwen giữ ngôn ngữ của bản trước refactor.

Không có cấu hình riêng theo hãng/dòng sản phẩm hoặc enum thuộc tính theo danh mục. `user_context.statements` giữ lời người dùng và thứ tự lượt; `fact_ids` chỉ là ID nguồn gốc, không xác nhận mọi nội dung trong lời nói là đúng. Model đối chiếu ngữ nghĩa toàn ngữ cảnh, gồm nhận diện loại hàng đủ rõ, giả định, phủ định, mâu thuẫn và đính chính. Product Review còn nhận `proposed_answer` để kiểm tra dữ kiện có bị thêm hoặc đổi nghĩa hay không. `user_quotes` trích nguyên văn lời người dùng được tham chiếu; backend kiểm tra nguồn gốc rồi dựng các trích dẫn. Các điều kiện quyết định và tên thuộc tính cần hỏi xuất phát từ nguồn đang xét.
