# Package RAG

Code được nhóm theo chức năng. Các thư mục ở đây là Python package; import từ module cụ thể để thấy rõ phụ thuộc. Cấu hình nằm ngoài runtime package tại `config/`; dữ liệu và kết quả thực nghiệm giữ nguyên vị trí.

```text
rag/
├── __init__.py
├── __main__.py                 # python -m rag
├── ingestion/
│   ├── sources.py              # Manifest, adapters và chuẩn hóa records/NODE/EDGE
│   ├── audit.py                # Kiểm tra nguồn, PDF, wording và provenance
│   ├── pdf_graph.py            # Trích cấu trúc bảng từ hình học PDF
│   ├── pdf_wording.py          # Bản chép đã đối chiếu ảnh và lớp chữ PDF gốc
│   ├── provenance.py           # Kiểm tra tương thích fingerprint khi chuyển package
│   └── provenance_relocations.json
├── chunking/
│   └── corpus.py               # Ghép ngữ cảnh nguồn, build/load corpus và snapshot
├── embedding/
│   ├── bge_m3.py               # Dense/sparse/ColBERT vectors và cache
│   └── validation.py           # Kích thước, giá trị và chuẩn hóa vector
├── vectordb/
│   └── postgres.py             # Kết nối, migration, nạp snapshot và pgvector
├── retrieval/
│   ├── retriever.py            # Hybrid retrieval, RRF và các API tìm kiếm
│   ├── unified.py              # Pool nguồn chung, cascade và source package
│   └── rerankers.py            # CrossEncoder M3/Qwen/Gemma và ColBERT scoring
├── graph/
│   ├── context.py              # Hierarchy, Notes và graph context có nguồn
│   └── legal_evidence.py       # Binding wording pháp lý và các cấp HS
├── prompts/
│   ├── system.py               # SYSTEM_PROMPT chính, dùng chung HS/QA
│   ├── product_review.py       # PRODUCT_REVIEW_PROMPT kiểm tra dữ kiện hàng hóa
│   ├── decision_review.py      # Nhận diện hàng hóa và kiểm tra quyết định chưa kết luận
│   ├── tasks.py                # Chỉ dẫn HS/QA/Auto và nhãn dữ kiện bổ sung
│   ├── repair.py               # Prompt sửa phản hồi theo lỗi validation
│   ├── provider_format.py      # Chỉ dẫn JSON theo khả năng của provider
│   ├── reranking.py            # Instruction và template Qwen, version cache
│   └── schemas.py              # ANSWER_SCHEMA và PRODUCT_REVIEW_SCHEMA
├── llm/
│   ├── context.py              # Ghép câu hỏi, nguồn, citation và ứng viên HS vào messages
│   ├── budget.py               # Guard toàn request theo model; ước lượng UTF-8 và output còn lại
│   ├── answering.py            # Sinh câu trả lời, sửa lỗi và kiểm tra đề xuất HS
│   ├── decision_review.py      # Rà soát thiếu dữ kiện trước khi chấp nhận thiếu nguồn
│   ├── quantitative.py         # Guard số đo/ngưỡng từ trích đoạn người dùng và nguồn
│   ├── validation.py           # Schema, trích nguyên văn, ancestry và quyền sở hữu dữ kiện
│   ├── client.py               # CLIProxyAPI chính → Groq fallback
│   ├── cliproxy_client.py      # Structured JSON qua gateway local
│   ├── errors.py               # Lỗi provider, không lộ key/body
│   └── groq_client.py          # Groq dự phòng, giới hạn và xoay key
├── api/
│   └── cli.py                  # Giao diện terminal HS/QA; chưa có HTTP API
└── utils/
    ├── files.py                # Hash nội dung, JSON/JSONL và ghi JSON atomic
    └── codes.py                # Chuẩn hóa định dạng mã HS
```

`chunking/corpus.py` giữ chiến lược ghép các đơn vị nguồn hiện tại, gồm GIR, điều/khoản TT85 và biểu thuế. Nó không bổ sung một thuật toán cắt văn bản mới.

## Luồng và ranh giới

Build knowledge base: `ingestion` → `chunking` → `embedding` → `vectordb`.

Phục vụ câu hỏi: `api/cli.py` → `retrieval` + `graph` → `llm/context.py` + `prompts` → `llm/answering.py` → `llm/validation.py`.

Terminal hiển thị riêng Retrieval, Reranking, LLM và Validation. LLM gồm sinh, sửa lỗi, Product Review và Decision Review, kể cả thời gian provider lỗi trước fallback; đóng gói context được đo riêng trong `/details`. Khi chưa kết luận được, mã ứng viên và nguồn chẩn đoán lấy từ context có thể hiển thị cùng lý do; đây chưa phải đề xuất HS. `/sources` mở nguồn hiện tại để đối chiếu mà không gọi model lại.

Model đã có trong [registry giới hạn](../config/model_limits.py) dùng token budget riêng. `context.py` giữ nguyên bộ nguồn/ứng viên; `budget.py` kiểm tra system + user + schema + wrapper trước từng request main, review, repair và fallback. Không tự cắt hay đóng gói lại nguồn cho fallback nhỏ hơn. `MAX_OUTPUT_TOKENS=model` dùng mức output của model; số nguyên vẫn được hỗ trợ. Context dùng chung như GPT-OSS 120B giảm output theo phần còn lại. Alias chưa biết và caller legacy giữ đường cấu hình tương thích cũ; xem [cấu hình](../config/README.md).

`CONSERVATIVE_UTF8_BOUND` là ước lượng bảo thủ bằng byte UTF-8, không phải tokenizer chính xác. `/details` hiển thị budget toàn request và usage provider riêng để tránh nhầm ước lượng với tiêu thụ thực tế.

Luồng v5 vẫn dùng một policy chung: hybrid toàn nguồn → graph context → pool theo ID → M3 → Qwen. `intent="auto"`, `"product"`, `"qa"` chỉ là hint; không thay candidate pool/ranking. `matches` trả Top-10 nguồn, `hs_candidates` chiếu tối đa 10 mã HS8 từ ranked pool; `package` giữ các nguồn sơ cấp có citation. Retrieval không tự chốt mã HS.

LLM chỉ hỏi người dùng về dữ kiện hàng hóa/hồ sơ còn thiếu qua `MISSING_PRODUCT_INFO`. Thiếu wording, GIR, Notes hoặc quan hệ HS phải trả `INSUFFICIENT_LEGAL_EVIDENCE`; không yêu cầu người dùng bổ sung luật. Đề xuất HS vẫn cần hierarchy `CONTAINS` đã xác minh và đủ nhãn citation bắt buộc. Các kiểm tra này nằm trong code, ngoài system prompt.

Toàn bộ chỉ dẫn tác vụ, sửa lỗi, định dạng provider và template Qwen do ứng dụng định nghĩa được quản lý tại [prompts/README.md](prompts/README.md). Các module xử lý import template từ đó; policy JSON giữ bản chụp instruction để đối chiếu cấu hình đã khóa.

## Lệnh và import

Chạy từ thư mục `aiAgent`:

```bash
.venv/bin/python -m rag
.venv/bin/python -m rag --model 3.8-high
.venv/bin/python -m rag --model 120b
.venv/bin/python -m rag --help
```

Không chọn thì dùng `3.5-lite-high`. `/model` hiển thị ba lựa chọn trong phiên; `/model 1|2|3` đổi model nhưng giữ dữ kiện, `/retry` chạy lại. Preset và reasoning tương ứng được quản lý tại `config/settings.py`; [cấu hình model](../config/README.md) giải thích fallback và độ ưu tiên so với `.env`.

Import theo vị trí mới:

```python
from rag.chunking.corpus import build_corpus, load_corpus
from rag.embedding.bge_m3 import Embedder
from rag.ingestion.audit import audit
from rag.llm.answering import generate_answer
from rag.llm.context import prepare_context
from rag.prompts.system import SYSTEM_PROMPT
from rag.retrieval.retriever import Retriever
from rag.vectordb.postgres import connect
```

Các đường dẫn cũ như `rag.data`, `rag.answering`, `rag.db` và lệnh `python rag/demoRAG.py` đã được thay thế. Scripts, tests và source cells trong cả ba notebook dùng đường dẫn mới.

## Provenance và thực nghiệm

Việc đổi import làm thay đổi SHA-256 của hai processor PDF. `ingestion/provenance_relocations.json` ghi đúng cặp fingerprint trước/sau và hash AST của các hàm xử lý giữ nguyên. `same_processor()` chỉ chấp nhận cặp đã đăng ký; thay code khác, version hoặc thư viện PDF vẫn bị từ chối. Fingerprint hiện tại luôn được tính từ file hiện tại. Các proof nguồn đã lưu không bị sửa.

Cấu hình E0, nguồn chuẩn hóa, corpus snapshot, embeddings và prompt/schema không đổi. Báo cáo/checkpoint cũ giữ nguyên để bảo toàn lịch sử. Các benchmark khóa hash code cần một run ID mới khi chạy với code sau refactor; không trộn checkpoint từ hai phiên bản code.

Gold, metrics, quét trọng số và kịch bản notebook nằm tại [tests/support/](../tests/support/README.md), cấu hình tại [config/](../config/README.md). Runtime không import các module kiểm thử. Xem [README-RAG.md](../README-RAG.md) để cài đặt và vận hành.
