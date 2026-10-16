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
- [schemas.py](schemas.py): contract JSON và mô tả trường mà model nhận được, gồm Answer, Product Review và Decision Review.

## Các nơi sử dụng

- `rag/llm/context.py` ghép câu hỏi, dữ kiện bổ sung, nguồn và chỉ dẫn tác vụ với system prompt.
- `rag/llm/answering.py` sử dụng prompt kiểm tra sản phẩm và prompt sửa lỗi.
- `rag/llm/decision_review.py` kiểm tra độc lập quyết định chưa kết luận; không phát hành mã HS và không coi câu trả lời trước là dữ kiện người dùng.
- `rag/llm/cliproxy_client.py` bổ sung chỉ dẫn định dạng theo khả năng của provider.
- `rag/retrieval/rerankers.py` dựng đầu vào Qwen bằng template trong `reranking.py`.
- `config/retrieval.py` giữ tên import tương thích `INSTRUCTION`, tham chiếu trực tiếp `SOURCE_RELEVANCE_INSTRUCTION`; runtime và các script benchmark dùng cùng nội dung này.
- `rag/retrieval/retriever.py` lấy lời nhắc cho API so sánh nguồn từ `tasks.py`.

## Phân biệt prompt và dữ liệu

Câu hỏi, dữ kiện người dùng, nguồn pháp lý, schema và danh sách lỗi được truyền dưới dạng dữ liệu vào các template. Giá trị được chèn không tiếp tục được xử lý như một template khác, kể cả khi chứa dấu ngoặc nhọn.

Các điều kiện chặn mã HS, kiểm tra nguồn, schema và quyền sở hữu dữ kiện vẫn được thực thi trong code. Sửa văn bản prompt không thay thế việc sửa validator khi contract thay đổi. Thông báo giao diện terminal thuộc `rag/api/cli.py`; các thông báo lỗi validation là phản hồi kiểm tra, không phải nơi định nghĩa chỉ dẫn tác vụ.

Product Review bắt buộc có `reason`, chỉ hỏi thuộc tính còn thiếu trong `MISSING_PRODUCT_INFO` và dùng `UNRESOLVED_APPLICATION` khi có dữ kiện nhưng chưa đối chiếu được với điều kiện. `REQUIRES_REVIEW` không được thay thế câu hỏi bổ sung nếu chỉ thiếu thuộc tính. Runtime sửa review tối đa một lần; nếu vẫn lỗi, chỉ hiển thị chẩn đoán an toàn và nguồn lấy từ context. Tên thương mại kèm loại hàng rộng không tự xác nhận loại hẹp trong nguồn.

Decision Review chạy cho phản hồi thiếu chứng cứ/cần thẩm định hợp lệ chưa được Product Review kiểm tra, và khi ngữ cảnh HS/Auto không có nguồn. Nó tách nhu cầu hỏi đáp/phân loại khỏi việc đã nhận diện sản phẩm; tên loại hàng đã nhận diện phải xuất hiện nguyên văn trong trích đoạn người dùng. Câu hỏi nhận diện không cần nguồn luật; câu hỏi thông số cần nhãn và điều kiện nguyên văn từ nguồn liên quan. QA rõ ràng không bị hỏi nhận diện hàng hóa. Kết quả kỹ thuật không hợp lệ hoặc lỗi provider không được chuyển thành câu hỏi sản phẩm. `/details` ghi riêng thời gian, usage, budget và lý do của bước kiểm tra này.

`rag/llm/quantitative.py` bổ sung guard cho điều kiện định lượng rõ ràng trong nguồn bắt buộc của một Product Review `SUPPORTED`. Số đo phải được chứng minh từ `user_quote` của dữ kiện được tham chiếu, không lấy từ lời diễn giải `fact` hoặc tên model sản phẩm. Guard đọc toàn nguồn bắt buộc để tránh bỏ qua điều kiện trong trích đoạn ngắn. Nếu chưa chứng minh được, runtime yêu cầu sửa review một lần; guard không tự chọn mã hoặc tự sinh câu hỏi. Bộ phân tích chỉ hỗ trợ các đơn vị và so sánh đã định nghĩa, không thay thế việc đánh giá ngoại lệ, nhánh lựa chọn hoặc toàn bộ ngữ nghĩa pháp lý.

Generation và repair giữ tiếng Việt; wrapper JSON và template/instruction Qwen giữ nguyên ngôn ngữ của bản trước refactor. Việc tập trung file không tự thay đổi nội dung hoặc ngôn ngữ prompt.

## Policy, cache và kiểm chứng khi sửa

`config/unified_retrieval.json` lưu bản chụp instruction của policy đã khóa. Đây là dữ liệu đối chiếu với instruction runtime, không phải nơi chỉnh prompt chạy trực tiếp. Output notebook và report cũ cũng là bản ghi lịch sử.

Nếu chỉ đổi vị trí file/import, nội dung đầu vào model, instruction trong policy và cache identity phải giữ nguyên. Nếu sửa nội dung reranking thực sự, cần đánh giá lại policy và cập nhật version/cache phù hợp; không đồng bộ JSON chỉ để bỏ qua kiểm tra lệch policy.

`prompt_hash` của generation hiện nhận diện `SYSTEM_PROMPT`; `context_hash` bao gồm payload và chỉ dẫn tác vụ. Product Review lưu hash prompt/schema riêng. Không coi riêng `prompt_hash` là hash của mọi lớp chỉ dẫn, gồm repair và wrapper provider.

Bản tách ngày 15/10/2026 đã so sánh trước/sau qua các caller thực tế bằng model/network giả lập: ba tác vụ, hai lượt bổ sung, sửa lỗi, payload Gemini/GPT-OSS, Qwen với instruction mặc định/rỗng/chung/riêng và lời nhắc so sánh nguồn. Nội dung thu được trùng nhau hoàn toàn; không gọi API model bên ngoài. Bằng chứng tại `artifacts/diagnostics/prompt-centralization-20261015/` trong workspace (không được Git theo dõi).

Chạy kiểm thử từ thư mục `aiAgent`:

```bash
HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q tests/
```

Các ca DB cần opt-in riêng; suite mặc định không gọi model thật. Khi đổi nội dung chỉ dẫn, cần kiểm tra hành vi tương ứng bằng dữ kiện và nguồn xác định, bên cạnh kiểm tra cấu trúc.
