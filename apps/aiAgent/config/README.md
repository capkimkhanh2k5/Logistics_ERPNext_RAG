# Cấu hình

| File | Vai trò |
|---|---|
| [settings.py](settings.py) | `CLIProxyConfig`, `GroqConfig`, `RAGGenerationConfig`, `DatabaseConfig`; kiểm tra cấu hình và giữ key/password khỏi repr. |
| [testing.py](testing.py) | `GenerationTestConfig`: cờ chạy và lựa chọn tình huống của notebook 03. |
| [retrieval.py](retrieval.py) | Loader `rag.yaml`; model/revision, instruction và bộ trọng số của retrieval. |
| [rag.yaml](rag.yaml) | Embedding và cấu hình nền cho build/retrieval. |
| [unified_retrieval.json](unified_retrieval.json) | Policy v5 đã khóa theo snapshot/profile, dùng cho runtime. |
| [cliproxyapi/README.md](cliproxyapi/README.md) | Gateway LLM và Web UI chạy trong Docker stack `aiagent-rag`; hướng dẫn tạo key local và kết nối OAuth. |

Terminal và notebook 03 dùng `RAGClient()`: CLIProxyAPI là provider chính, Groq là dự phòng. `connect()` gọi `DatabaseConfig.from_env()`. Runtime ưu tiên biến môi trường rồi đến file `.env`. Notebook 03 gọi `load_environment(override=True)` để đọc lại `.env` khi chạy lại cell. Key/password phải được cung cấp; không có giá trị bí mật mặc định.

CLIProxyAPI đọc `CLIPROXYAPI_BASE_URL`, `CLIPROXYAPI_MODEL`, `CLIPROXYAPI_FALLBACK_MODEL`, `CLIPROXYAPI_FALLBACK_REASONING_EFFORT`, `CLIPROXYAPI_MAX_OUTPUT_TOKENS`, `CLIPROXYAPI_REASONING_EFFORT`, `CLIPROXYAPI_TIMEOUT_SECONDS`, `CLIPROXYAPI_TEMPERATURE`. Mặc định gọi `gemini-3.8-flash-high` qua `http://127.0.0.1:8317/v1`. Nếu không đặt `CLIPROXYAPI_API_KEY`, loader đọc `CLIPROXYAPI_CLIENT_API_KEY` trong `config/cliproxyapi/local/credentials.env`; không dùng management password để gọi LLM. Khi ứng dụng chạy trong Docker cùng network, đổi base URL thành `http://cliproxyapi:8317/v1`.

Thứ tự là **CLIProxyAPI/Gemini → CLIProxyAPI/GPT-OSS 120B → `GROQ_MODEL` → `GROQ_FALLBACK_MODEL`**. Model dự phòng trong CLI mặc định là `gpt-oss-120b-medium`, với reasoning `medium`; Gemini vẫn dùng `high`. Lỗi kết nối/timeout, xác thực/quyền truy cập, model không khả dụng, quota `429`, các lỗi `5xx` và response thiếu nội dung chuyển sang model tiếp theo trong chuỗi. `429` ghi cooldown riêng theo từng model theo `Retry-After` (mặc định 60 giây): Gemini hết quota vẫn thử GPT-OSS 120B; chỉ chuyển sang Groq khi cả hai model CLI không khả dụng. Cooldown của GPT-OSS không chặn Gemini và ngược lại; đây là trạng thái trong client RAG, không đảm bảo cách chia quota của nhà cung cấp. Không tự chuyển provider cho lỗi đầu vào `400`, trừ mã `json_validate_failed`. Lượt sửa JSON/citation và kiểm tra đề xuất HS vẫn ghim đúng model đã trả lời, không tự mở thêm chuỗi fallback. Nếu kiểm tra đề xuất HS không khả dụng, giữ trạng thái `REQUIRES_REVIEW` hiện có.

`RAGGenerationConfig.fallback_model` là bước dự phòng kế tiếp, `fallback_models` chứa đầy đủ các bước dự phòng theo thứ tự. Metadata generation ghi `provider`, `model` là alias có thể gọi lại, `response_model` là tên upstream nếu có, `requested_model`, `fallback_used`, các lỗi đã gặp và usage. Alias Gemini `high` được giữ khi sửa phản hồi dù upstream trả tên `gemini-3.8-flash-n`.

Tất cả trường cấu hình Groq đều có biến `.env`: `GROQ_API_KEYS`, `GROQ_MODEL`, `GROQ_FALLBACK_MODEL`, `GROQ_MODERATION_MODEL`, `GROQ_MAX_INPUT_CHARS`, `GROQ_MAX_OUTPUT_TOKENS`, `GROQ_MAX_CONTEXT_CHARS`, `GROQ_REASONING_EFFORT`, `GROQ_TIMEOUT_SECONDS`, `GROQ_MAX_WAIT_SECONDS`, `GROQ_TEMPERATURE`. Hai giới hạn ký tự `GROQ_MAX_INPUT_CHARS`/`GROQ_MAX_CONTEXT_CHARS` tiếp tục dùng chung khi đóng gói RAG để giữ giới hạn cũ; token budget, timeout và reasoning của từng provider độc lập. `GROQ_MODERATION_MODEL` là thiết lập được đọc; luồng generation hiện chưa gọi moderation.

DB đọc `RAG_DB_HOST`, `RAG_DB_PORT`, `RAG_DB_NAME`, `RAG_DB_USER`, `RAG_DB_PASSWORD`. Các mẫu không chứa key thật nằm trong [.env.example](../.env.example).

Notebook 03 đọc `RAG_TEST_RUN_TESTS`, `RAG_TEST_USE_RETRIEVAL_CACHE`, `RAG_TEST_MIN_TURN_INTERVAL_SECONDS`, `RAG_TEST_CASE_IDS` và `RAG_TEST_RUN_CUSTOM_CASE`. `RAG_TEST_CASE_IDS` để rỗng sẽ chạy toàn bộ; nếu chọn nhiều ID thì ngăn cách bằng dấu phẩy. Câu hỏi tự thử và các lượt bổ sung vẫn nhập trong notebook.

Model/revision và policy retrieval vẫn lấy từ cấu hình đã khóa. Thay chúng cần tạo lại hoặc đánh giá lại snapshot/profile tương ứng; biến môi trường Groq không ghi đè các policy này.
