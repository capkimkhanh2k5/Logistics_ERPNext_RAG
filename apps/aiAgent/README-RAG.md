# RAG — hai notebook chính

| Notebook | Workflow |
|---|---|
| `notebooks/01_build_knowledge_base.ipynb` | Audit → GIR context / TT85 hierarchy + forms → BGE-M3 dense+sparse → PostgreSQL → integrity/idempotency |
| `notebooks/02_test_retrieval.ipynb` | Legal/robustness/challenge cases → dev ablation → weighted hybrid selection → routing/graph → final benchmark → uncached latency → code checks |

**Cả hai notebook đã được chạy; outputs được giữ ngay trong file.** Không tạo report rời. Các module `rag/` giữ logic dùng chung để notebook và runtime dùng cùng implementation.

## Mở và chạy

Trong `frappe-bench/apps/aiAgent`:

```bash
.venv/bin/jupyter lab notebooks
```

Chọn kernel **Python (AI Agent RAG)**. Chạy notebook 01 trước, rồi notebook 02. Notebook 02 đọc corpus/model profile active từ artifacts/database, không cần giữ kernel notebook 01.

Máy mới cần:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-rag.lock.txt
cp .env.example .env
```

Đặt mật khẩu riêng trong `.env`, rồi:

```bash
docker compose -f docker-compose.rag.yml up -d
.venv/bin/python -m ipykernel install --user --name aiagent-rag --display-name 'Python (AI Agent RAG)'
```

Giữ `.env` hiện tại nếu đã có database volume. Lockfile đã được kiểm chứng trên macOS ARM64/Python 3.11; khi đổi platform có thể resolve từ `requirements-rag.txt` rồi kiểm chứng lại.

Notebook 01 có cell hiển thị database trước ingestion; `APPLY=True` ghi vào database RAG riêng. Có thể đặt `APPLY=False` để dry-run. Không DROP/TRUNCATE. Model/tokenizer được pin commit; máy mới tải weights khoảng 2,2 GB. Ingestion tái chạy có checkpoint và không tạo duplicate.

## Cấu trúc còn lại

- `data/`: nguồn và gold dataset gốc; không sửa wording nguồn.
- `rag/`: adapters, embeddings, database, retrieval và evaluation dùng chung.
- `config/`: model/retrieval settings, frozen split và selected runtime config.
- `sql/`, `docker-compose.rag.yml`: schema và PostgreSQL service riêng.
- `tests/`: regression/integration checks; notebook 02 chạy và lưu kết quả kiểm tra.
- `artifacts/`: corpus snapshot và embedding cache/checkpoints cần cho resume; được gitignore. Đây là dữ liệu thực thi, không phải report.

## Retrieval khi đưa vào sử dụng

```python
from rag.db import connect
from rag.embedding import Embedder
from rag.retrieval import Retriever

with connect() as conn:
    retriever = Retriever(conn, Embedder())
    result = retriever.routed_search("Điện thoại thông minh 5G có hệ điều hành chạy ứng dụng")
```

`routed_search` nhận diện intent và các strong scope cues; truy vấn chưa chắc chắn search cả 84/85. `NEED_MORE_INFORMATION` vẫn có thể trả ứng viên. Đây là retrieval support, chưa quyết định HS cuối cùng.

Các mode: `fts`, `dense`, `sparse`, `hybrid`, `dense_sparse`, `hybrid_sparse`. Default đọc selected config khớp snapshot/profile/settings. Exact-code dùng `lookup`. FTS là `simple` + `unaccent`/`ts_rank_cd`, không phải BM25. Learned sparse dùng token postings và dot product. Corpus nhỏ dùng exact cosine thay cho ANN; chưa cần HNSW/reranker.

Graph đi lên ancestors trước khi mở rộng notes; explicit constraints được ưu tiên. Output có `required_ids`, `missing_required_ids`, `omitted_ids`, coverage status và budget. Context views có source-ID mapping; nguyên văn source/citation locator giữ riêng. TT85 forms là biểu diễn title+fields trích xuất, không thay thế layout biểu mẫu gốc.

## Cách đọc kết quả

Xem trực tiếp các bảng trong notebook 02. Bộ 50 case cũ được ghi là reproduction; challenge 12 query/mã mới được khóa trước khi chọn dev config. Legal qrels được đối chiếu nguồn local, chưa có independent expert review. Scope suite 16 case là kiểm tra chức năng trên mẫu nhỏ, chưa chứng minh coverage mọi sản phẩm. Date filters dùng metadata local; không mặc định TT31/GIR có legal validity đã xác minh.

Latency được đo riêng với `use_cache=False`. Query chỉ có tên sản phẩm có thể kém query đầy đủ thông số; notebook giữ cả kết quả và các failure cases. RAG ingestion/retrieval/testing đã chạy xuyên suốt; final HS classification, GIR reasoning engine, Critic, LLM generation và ERP integration thuộc giai đoạn sau.
