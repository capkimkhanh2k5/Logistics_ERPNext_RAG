# Cấu hình

| File | Vai trò |
|---|---|
| [settings.py](settings.py) | `CLIProxyConfig`, `GroqConfig`, `RAGGenerationConfig`, `DatabaseConfig`; kiểm tra cấu hình và giữ key/password khỏi repr. |
| [model_limits.py](model_limits.py) | Registry giới hạn input/output và context dùng chung theo alias model. |
| [testing.py](testing.py) | `GenerationTestConfig`: cờ chạy và lựa chọn tình huống của notebook 03. |
| [retrieval.py](retrieval.py) | Loader `rag.yaml`; model/revision, instruction và bộ trọng số của retrieval. |
| [rag.yaml](rag.yaml) | Embedding và cấu hình nền cho build/retrieval. |
| [unified_retrieval.json](unified_retrieval.json) | Policy v5 đã khóa theo snapshot/profile, dùng cho runtime. |
| [cliproxyapi/README.md](cliproxyapi/README.md) | Gateway LLM và Web UI chạy trong Docker stack `aiagent-rag`; hướng dẫn tạo key local và kết nối OAuth. |

Terminal và notebook 03 dùng `RAGClient`: CLIProxyAPI là provider chính, Groq là dự phòng. `connect()` gọi `DatabaseConfig.from_env()`. Runtime ưu tiên biến môi trường rồi đến file `.env`. Notebook 03 gọi `load_environment(override=True)` để đọc lại `.env` khi chạy lại cell. Key/password phải được cung cấp; không có giá trị bí mật mặc định.

CLIProxyAPI đọc `CLIPROXYAPI_BASE_URL`, `CLIPROXYAPI_MODEL`, `CLIPROXYAPI_FALLBACK_MODEL`, `CLIPROXYAPI_FALLBACK_REASONING_EFFORT`, `CLIPROXYAPI_MAX_OUTPUT_TOKENS`, `CLIPROXYAPI_REASONING_EFFORT`, `CLIPROXYAPI_TIMEOUT_SECONDS`, `CLIPROXYAPI_TEMPERATURE`. Mặc định gọi `gemini-3.5-flash-lite` với reasoning `high` qua `http://127.0.0.1:8317/v1`. Nếu không đặt `CLIPROXYAPI_API_KEY`, loader đọc `CLIPROXYAPI_CLIENT_API_KEY` trong `config/cliproxyapi/local/credentials.env`; không dùng management password để gọi LLM. Khi ứng dụng chạy trong Docker cùng network, đổi base URL thành `http://cliproxyapi:8317/v1`.

Ba preset dùng chung của Demo nằm trong `MODEL_PRESETS` tại `config/settings.py`: `3.8-high` → Gemini 3.8 High, `3.5-lite-high` → Gemini 3.5 Lite High (mặc định), `120b` → GPT-OSS 120B với reasoning `medium`. Chạy `python -m rag --model <preset>` hoặc dùng `/model` trong phiên để xem/chọn. `/model 1`, `/model 2`, `/model 3` lần lượt chọn 3.8 High, 3.5 Lite High và 120B; `/retry` chạy lại câu hỏi với dữ kiện hiện tại sau khi đổi.

Demo luôn áp dụng preset, kể cả `.env` cũ còn ghi model 3.8 hoặc reasoning thấp. Preset cố định bốn trường model chính/reasoning/model dự phòng/reasoning dự phòng; các thiết lập kết nối, key, timeout, temperature và token budget vẫn lấy từ môi trường. `RAGClient(model_preset="120b")` hoặc `client.select_model("3.8-high")` dùng cùng cơ chế. `RAGClient()` không truyền preset (như notebook 03) tiếp tục tôn trọng cấu hình model rõ ràng trong `.env`; giá trị mặc định của config và `.env.example` đã đổi sang Lite High.

Thứ tự cho preset Gemini là **Gemini được chọn (`high`) → GPT-OSS 120B (`medium`) → `GROQ_MODEL` → `GROQ_FALLBACK_MODEL`**. Preset 120B dùng **GPT-OSS 120B (`medium`) → Gemini 3.5 Lite (`high`) → Groq**, tránh thử trùng cùng alias. Lỗi kết nối/timeout, xác thực/quyền truy cập, model không khả dụng, quota `429`, các lỗi `5xx` và response thiếu nội dung chuyển sang model tiếp theo trong chuỗi. `429` ghi cooldown riêng theo alias theo `Retry-After` (mặc định 60 giây), kể cả khi repair/review đang ghim model; đổi model không xóa cooldown hoặc trạng thái xoay key Groq. Đây là trạng thái trong client RAG, không đảm bảo cách chia quota của nhà cung cấp. Không tự chuyển provider cho lỗi đầu vào `400`, trừ mã `json_validate_failed`. Lượt sửa JSON/citation và kiểm tra đề xuất HS vẫn ghim đúng model đã trả lời, không tự mở thêm chuỗi fallback. Nếu kiểm tra đề xuất HS không khả dụng, giữ trạng thái `REQUIRES_REVIEW` hiện có.

`RAGGenerationConfig.fallback_model` là bước dự phòng kế tiếp, `fallback_models` chứa đầy đủ các bước dự phòng theo thứ tự và được cập nhật khi đổi preset. Metadata generation ghi `provider`, `model` là alias có thể gọi lại, `response_model` là tên upstream nếu có, `requested_model`, `fallback_used`, các lỗi đã gặp và usage. Alias Gemini `high` được giữ khi sửa phản hồi dù upstream trả tên `gemini-3.8-flash-n`.

Tất cả trường cấu hình Groq đều có biến `.env`: `GROQ_API_KEYS`, `GROQ_MODEL`, `GROQ_FALLBACK_MODEL`, `GROQ_MODERATION_MODEL`, `GROQ_MAX_INPUT_CHARS`, `GROQ_MAX_OUTPUT_TOKENS`, `GROQ_MAX_CONTEXT_CHARS`, `GROQ_REASONING_EFFORT`, `GROQ_TIMEOUT_SECONDS`, `GROQ_MAX_WAIT_SECONDS`, `GROQ_TEMPERATURE`. `GROQ_MODERATION_MODEL` là thiết lập được đọc; luồng generation hiện chưa gọi moderation.

Các preset hiện có:

- Gemini 3.8 High: input 1.048.576, output tối đa 65.536 token.
- Gemini 3.5 Lite High: input 1.048.576, output tối đa 65.535 token.
- GPT-OSS 120B: context input + output dùng chung 114.000 token, output tối đa 32.768 token; output thực gửi được giảm theo phần context còn lại.

`CLIPROXYAPI_MAX_OUTPUT_TOKENS=model` và `GROQ_MAX_OUTPUT_TOKENS=model` là mặc định: dùng mức output của model đang được gọi, kể cả fallback. Số nguyên dương vẫn được hỗ trợ để đặt cap riêng; runtime lấy mức nhỏ hơn giữa cap đó, giới hạn model và phần context còn lại nếu dùng chung. Đây là ngân sách output được phép sinh, không phải số token chắc chắn sẽ sinh.

[budget.py](../rag/llm/budget.py) kiểm tra toàn bộ request: system, user/dữ kiện/nguồn, JSON schema và wrapper định dạng GPT-OSS nếu có. Guard chạy trước từng request sinh, Product Review, repair và fallback theo đúng model đích. Nguồn được đóng gói nguyên bộ; fallback nhỏ hơn không được tự cắt nguồn hoặc đóng gói lại để né giới hạn, mà bị bỏ qua hoặc báo lỗi budget khi không thể tiếp tục. Đổi model rồi `/retry` sẽ đóng gói lại từ dữ kiện người dùng.

Chế độ `CONSERVATIVE_UTF8_BOUND` dùng byte UTF-8 và dự phòng framing để ước lượng bảo thủ; đây không phải tokenizer chính xác. Giới hạn trong registry là metadata/policy theo alias, chưa phải kết quả thử sát biên. `/details` tách budget ước tính của request khỏi usage thực tế do provider trả về.

Alias custom chưa có trong registry giữ đường legacy với `GROQ_MAX_INPUT_CHARS`/`GROQ_MAX_CONTEXT_CHARS` và trạng thái `UNKNOWN_MODEL_LIMITS`; không coi đó là giới hạn token đã xác minh. Khi output để `model`, alias chưa biết dùng cap tương thích cũ: CLIProxyAPI 8.192, Groq 2.048 token; vẫn có thể đặt số riêng. Các caller legacy dùng trực tiếp `GroqConfig` cũng giữ cap ký tự cũ.

DB đọc `RAG_DB_HOST`, `RAG_DB_PORT`, `RAG_DB_NAME`, `RAG_DB_USER`, `RAG_DB_PASSWORD`. Các mẫu không chứa key thật nằm trong [.env.example](../.env.example).

Notebook 03 đọc `RAG_TEST_RUN_TESTS`, `RAG_TEST_USE_RETRIEVAL_CACHE`, `RAG_TEST_MIN_TURN_INTERVAL_SECONDS`, `RAG_TEST_CASE_IDS` và `RAG_TEST_RUN_CUSTOM_CASE`. `RAG_TEST_CASE_IDS` để rỗng sẽ chạy toàn bộ; nếu chọn nhiều ID thì ngăn cách bằng dấu phẩy. Câu hỏi tự thử và các lượt bổ sung vẫn nhập trong notebook.

Model/revision và policy retrieval vẫn lấy từ cấu hình đã khóa. Thay chúng cần tạo lại hoặc đánh giá lại snapshot/profile tương ứng; biến môi trường Groq không ghi đè các policy này.
