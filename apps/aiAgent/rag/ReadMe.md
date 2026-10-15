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
│   └── schemas.py              # ANSWER_SCHEMA và PRODUCT_REVIEW_SCHEMA
├── llm/
│   ├── context.py              # Ghép câu hỏi, nguồn, citation và ứng viên HS vào messages
│   ├── answering.py            # Sinh câu trả lời, sửa lỗi và kiểm tra đề xuất HS
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

Luồng v5 vẫn dùng một policy chung: hybrid toàn nguồn → graph context → pool theo ID → M3 → Qwen. `intent="auto"`, `"product"`, `"qa"` chỉ là hint; không thay candidate pool/ranking. `matches` trả Top-10 nguồn, `hs_candidates` chiếu tối đa 10 mã HS8 từ ranked pool; `package` giữ các nguồn sơ cấp có citation. Retrieval không tự chốt mã HS.

LLM chỉ hỏi người dùng về dữ kiện hàng hóa/hồ sơ còn thiếu qua `MISSING_PRODUCT_INFO`. Thiếu wording, GIR, Notes hoặc quan hệ HS phải trả `INSUFFICIENT_LEGAL_EVIDENCE`; không yêu cầu người dùng bổ sung luật. Đề xuất HS vẫn cần hierarchy `CONTAINS` đã xác minh và đủ nhãn citation bắt buộc. Các kiểm tra này nằm trong code, ngoài system prompt.

## Lệnh và import

Chạy từ thư mục `aiAgent`:

```bash
.venv/bin/python -m rag
.venv/bin/python -m rag --help
```

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
