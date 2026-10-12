# Cấu hình

| File | Vai trò |
|---|---|
| [settings.py](settings.py) | `GroqConfig`, `DatabaseConfig`, đọc `.env`, kiểm tra giá trị và giữ bí mật khỏi repr. |
| [testing.py](testing.py) | `GenerationTestConfig`: cờ chạy và lựa chọn tình huống của notebook 03. |
| [retrieval.py](retrieval.py) | Loader `rag.yaml`; model/revision, instruction và bộ trọng số của retrieval. |
| [rag.yaml](rag.yaml) | Embedding và cấu hình nền cho build/retrieval. |
| [unified_retrieval.json](unified_retrieval.json) | Policy v5 đã khóa theo snapshot/profile, dùng cho runtime. |

`GroqClient()` gọi `GroqConfig.from_env()`. `connect()` gọi `DatabaseConfig.from_env()`. Giá trị trong dataclass là mặc định khi biến môi trường chưa được đặt; runtime ưu tiên biến môi trường rồi đến file `.env`. Notebook 03 gọi `load_environment(override=True)` để đọc lại `.env` khi chạy lại cell. Key/password phải được cung cấp; không có giá trị bí mật mặc định.

Tất cả trường cấu hình Groq đều có biến `.env`: `GROQ_API_KEYS`, `GROQ_MODEL`, `GROQ_FALLBACK_MODEL`, `GROQ_MODERATION_MODEL`, `GROQ_MAX_INPUT_CHARS`, `GROQ_MAX_OUTPUT_TOKENS`, `GROQ_MAX_CONTEXT_CHARS`, `GROQ_REASONING_EFFORT`, `GROQ_TIMEOUT_SECONDS`, `GROQ_MAX_WAIT_SECONDS`, `GROQ_TEMPERATURE`. `GROQ_MODERATION_MODEL` là thiết lập được đọc; luồng generation hiện chưa gọi moderation.

DB đọc `RAG_DB_HOST`, `RAG_DB_PORT`, `RAG_DB_NAME`, `RAG_DB_USER`, `RAG_DB_PASSWORD`. Các mẫu không chứa key thật nằm trong [.env.example](../.env.example).

Notebook 03 đọc `RAG_TEST_RUN_TESTS`, `RAG_TEST_USE_RETRIEVAL_CACHE`, `RAG_TEST_MIN_TURN_INTERVAL_SECONDS`, `RAG_TEST_CASE_IDS` và `RAG_TEST_RUN_CUSTOM_CASE`. `RAG_TEST_CASE_IDS` để rỗng sẽ chạy toàn bộ; nếu chọn nhiều ID thì ngăn cách bằng dấu phẩy. Câu hỏi tự thử và các lượt bổ sung vẫn nhập trong notebook.

Model/revision và policy retrieval vẫn lấy từ cấu hình đã khóa. Thay chúng cần tạo lại hoặc đánh giá lại snapshot/profile tương ứng; biến môi trường Groq không ghi đè các policy này.
