# RAG — Knowledge Base, HS và QA

| Notebook | Workflow |
|---|---|
| `notebooks/01_build_knowledge_base.ipynb` | Audit manifest nguồn → GIR/TT85/HS → BGE-M3 → nạp snapshot trong transaction |
| `notebooks/02_test_retrieval.ipynb` | Đọc kết quả/policy đã khóa; chỉ chạy chọn lại trên Dev khi bật cờ rõ ràng → Test |

Các lượt thực nghiệm lưu report và predictions trong `artifacts/experiments/<run-id>`; notebook đọc cùng runtime/runner. Các module `rag/` giữ logic dùng chung để notebook và runtime dùng cùng implementation.

[Luồng Retrieval HS/Legal v5](docs/retrievalWF_Docs.md) mô tả nguồn, NODE/EDGE, Notes, cấu hình 160/100/40, cascade và đầu ra. Sơ đồ Mermaid trong tài liệu thể hiện luồng đang sử dụng.

### Vai trò các file

| File | Vai trò |
|---|---|
| `rag/sources.py` | Đọc manifest, chuẩn hóa định dạng records/NODE/EDGE và quan hệ nguồn khi build corpus; không chọn mã HS theo sản phẩm. |
| `rag/pdf_graph.py` | Đọc ô bảng, mã, dấu phân cấp và mô tả nối trang từ PDF. Đây là parser nguồn khi build, không chạy phân loại câu hỏi. |
| `scripts/build_pdf_graph.py` | Xuất nhãn PDF và cạnh `CONTEXT_FOR` bằng thứ tự/cấp dòng; không đọc câu hỏi hoặc đáp án benchmark. |
| `scripts/audit_pdf_sources.py` | Kiểm tra mã neo, wording nguồn, Notes, hash PDF và tính toàn vẹn graph. |
| `scripts/ocr_pdf.swift` | OCR PDF scan bằng PDFKit/Apple Vision trên macOS; kết quả OCR cần giữ giới hạn ngôn ngữ khi báo cáo. |
| `scripts/benchmark_pdf_rerankers.py` | Công cụ benchmark biểu diễn PDF graph và reranker. |
| `scripts/benchmark_unified_retrieval.py` | Runner v5: một luồng HS/Legal, sàng accuracy trên Dev, so sánh model/cascade, khóa policy và chấm Test Auto. |
| `rag/experiments.py` | Nhóm các câu cùng họ/biến thể, lưu manifest và fold mappings cho đánh giá. |
| `scripts/prepare_dev_test.py` | Tái tạo/kiểm chứng hai tập HS và QA từ archive; giữ nguyên các nhóm. |
| `scripts/tune_shared_retrieval.py` | Chọn một policy HS trên Dev, đo latency, khóa policy rồi chấm Test. |
| `scripts/run_retrieval_experiment.py` | Chấm các biến thể B0/B1/B2 với policy đã khóa, lưu từng dự đoán và Hit@1/Recall/MRR theo Phần/Chương. |
| `scripts/run_runtime_regression.py` | Chấm lại QA pháp lý bằng policy đã khóa; không tìm trọng số. |
| `scripts/measure_fresh_runtime_latency.py` | Đo thời gian runtime khi bỏ cache truy vấn/reranker. |
| `scripts/finalize_retrieval_report.py` | Kiểm tra completeness/hashes và tổng hợp kết quả, phễu lỗi, CI và báo cáo bàn giao. |

Các scripts chạy khi thực nghiệm/kiểm chứng; chúng không được chạy lại cho mỗi câu hỏi người dùng.

### Dev/Test hiện tại — HS và QA

Hai bộ dữ liệu đang dùng chỉ có Dev và Test:

| Bộ dữ liệu | Tổng | Dev | Test | Mục đích |
|---|---:|---:|---:|---|
| HS XIV | 244 | 195 | 49 | Cùng cấu hình với các Phần khác. |
| HS XVI | 426 | 341 | 85 | Cùng cấu hình với các Phần khác. |
| HS XVII | 270 | 216 | 54 | Cùng cấu hình với các Phần khác. |
| HS toàn bộ | 940 | 752 | 188 | Dev chọn cấu hình; Test chấm sau khi khóa. |
| QA pháp lý | 650 | 520 | 130 | Cùng HS chọn một cấu hình chung trên Dev; Test đánh giá sau khóa. |

File đang dùng nằm trong `data/verified/hs/` và `data/verified/qa/`, mỗi bộ gồm hai JSONL và một manifest. Các file giữ câu hỏi/đáp án gốc, thêm `original_split`, `eval_group_id`, `dev_fold`; HS có `query` đã loại nhãn/chỉ dẫn phân loại. Gold chỉ dùng để chấm, không vào corpus hoặc fine-tune BGE/Cross-Encoder.

HS phân tầng theo Chương, QA theo loại câu hỏi; cả hai giữ nguyên nhóm các câu cùng họ/biến thể. Không có nhóm nằm ở cả Dev và Test. Mỗi Dev có năm folds nội bộ để kiểm tra ổn định; folds không làm mô hình tự học thêm. Một số loại QA chỉ có 2–4 câu nên không thể đạt đúng 80/20 ở từng loại và có loại chưa xuất hiện trong Test; manifest ghi rõ số lượng thực tế.

`.venv/bin/python scripts/prepare_dev_test.py` kiểm chứng/tái tạo hai bộ Dev/Test từ archive dữ liệu cùng hashes; mặc định từ chối thay nội dung đã khóa. Runtime, notebook và runner đánh giá bằng các file trong `data/verified/hs/` và `data/verified/qa/`.

Tất cả câu hỏi đã từng được xem. Test mới là kiểm tra hồi quy trên phân chia theo nhóm mới, không phải Test mù và không chứng minh chất lượng ở Chương chưa có câu hỏi.

### Nguồn PDF và graph

PDF là căn cứ đối chiếu; pipeline không đọc DOCX để xác lập phạm vi. `PDF_SOURCE_GRAPH.json` lưu nhãn, thứ tự/cấp dòng, bbox, trang vật lý, hash PDF và cạnh tường minh tới các mã thuộc nhánh. Không suy ra CKD/CBU hoặc điều kiện pháp lý từ chữ số của mã. `PDF_SOURCE_PROVENANCE.json` gắn bằng chứng PDF cho records; `PDF_SOURCE_TEXT_CORRECTIONS.json` là nhật ký 20 bản ghi sửa lỗi cắt/gộp mô tả đã kiểm tra trên ảnh PDF, được audit kiểm chứng trước build. Nhật ký này không ánh xạ câu hỏi sang đáp án.

Context loại văn bản trùng, giữ các citation riêng và không trích dẫn node điều hướng/HS6 ảo như wording pháp lý. Notes/references nhập từ dữ liệu nguồn vẫn là evidence, chưa là bộ máy thực thi đầy đủ GIR hoặc điều kiện loại trừ.

## Mở và chạy

Trong `frappe-bench/apps/aiAgent`:

```bash
.venv/bin/jupyter lab notebooks
```

Chọn kernel **Python (AI Agent RAG)**. Notebook 01 build/audit corpus nguồn từ manifest; mặc định giữ snapshot hiện có. Notebook 02 đọc policy/kết quả v5 đã khóa; `RESUME_BENCHMARK=False` và `RUNTIME_DEMO=False` mặc định. Chọn cấu hình trên Dev HS/Legal và đánh giá Test do runner v5 thực hiện.

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

Notebook 01 có cell hiển thị database trước ingestion; `APPLY=True` ghi vào database RAG riêng. `APPLY=True, FRESH_REBUILD=True` xóa các bảng thuộc schema `rag` và nạp lại trong cùng transaction; lỗi sẽ rollback. Nguồn và output notebook được giữ. Có thể đặt `APPLY=False` để dry-run. Model/tokenizer được pin commit; máy mới tải weights khoảng 2,2 GB. Ingestion tái chạy có checkpoint và không tạo duplicate.

## Cấu trúc còn lại

- `data/`: nguồn và gold dataset gốc; không sửa wording nguồn.
- `rag/`: adapters, embeddings, database, retrieval và evaluation dùng chung.
- `config/`: model/retrieval settings và selected runtime config.
- `sql/`, `docker-compose.rag.yml`: schema và PostgreSQL service riêng.
- `tests/`: regression/integration checks; chạy bằng `RAG_RUN_DB_TESTS=1 .venv/bin/pytest tests/`.
- `artifacts/`: corpus snapshot, embedding cache/checkpoints và báo cáo thực nghiệm; được gitignore.

## Retrieval khi đưa vào sử dụng

```python
from rag.db import connect
from rag.embedding import Embedder
from rag.retrieval import Retriever

with connect() as conn:
    retriever = Retriever(conn, Embedder())
    result = retriever.routed_search("Điện thoại thông minh 5G có hệ điều hành chạy ứng dụng", intent="product")
```

`config/unified_retrieval.json` đã được kích hoạt sau lựa chọn trên Dev. `routed_search` dùng một luồng chung: hybrid toàn nguồn → context BM25/dense dựng từ NODE/EDGE → ứng viên tổ tiên/Notes từ graph → pool theo ID nguồn → reranker/cascade chung. `intent="auto"`, `"product"`, `"qa"` không thay đổi candidate pool hoặc ranking. Semantic intent dùng vector câu hỏi và logistic regression được chọn trên Dev; chỉ là metadata sau retrieval.

`matches` là Top-10 nguồn hỗn hợp; `hs_candidates` là shortlist HS8 từ cùng pool đã chấm; `package` chứa cả nguồn sơ cấp được trích trong context. Điểm Legal primary Top-10 và điểm package được báo riêng. `automatic_hs_decision=False`: retrieval chưa tự thực thi đầy đủ GIR, nhận diện thuộc tính thiếu hoặc kết luận mã cuối.

Config khóa snapshot/profile, model revision, prompt và token budget. Thêm Chương mới cùng schema sử dụng cùng thuật toán sau audit/ingest và lựa chọn cấu hình tương ứng với nguồn mới; chất lượng cần đo riêng. Semantic intent chỉ bổ sung metadata sau retrieval, không điều hướng sang cấu hình HS/Legal riêng.

### Thực nghiệm độ chính xác v5

Dev gồm 752 HS + 520 Legal; Test gồm 188 HS + 130 Legal. `scripts/benchmark_unified_retrieval.py run` resume protocol đã khóa. Sàng cố định 62 câu Dev nguyên nhóm cho M3/Qwen/Gemma, B1/B2 và hai bộ trọng số; chấm hai model đơn tốt nhất, M3 và cascade M3 → Qwen trên toàn Dev. Pool 60/100, rank weight .85/1; cascade shortlist 20/40, weight .5/1. Không có latency gate. M3 là tên viết tắt của model BGE-reranker-v2-m3.

Tiêu chí: trung bình(HS Macro MRR@10, Legal đủ mọi nhóm primary @10). Cấu hình tốt nhất chỉ trong grid đã khảo sát. Khóa `config/unified_retrieval.json` trước Test; mô hình ý định ở `config/semantic_intent.json`. Model embedding/reranker không fine-tune; logistic intent có fit trên Dev nhưng không tham gia ranking.

[Báo cáo v5](artifacts/experiments/run_unified_accuracy_v5/IMPLEMENTATION_REPORT_V5.md) lưu kết quả Dev, Test Auto, kiểm chứng runtime và các giới hạn đánh giá. Test đã từng được xem là hồi quy, chưa chứng minh chất lượng trên Chương mới. Notebook 01 build nguồn; notebook 02 đọc kết quả v5, demo và resume benchmark tắt mặc định.

### Kết quả v5 đã hoàn tất — 03/10/2026

Đã chấm toàn bộ 1.272 câu Dev cho M3, Qwen và Gemma, cùng 16 cấu hình cascade M3 → Qwen. Trong 28 cấu hình chấm toàn Dev, cascade đạt objective 0.8464; cấu hình Qwen đơn tốt nhất đạt 0.8450, Gemma 0.8325, M3 0.8203. Khoảng cách cascade/Qwen nhỏ; chưa kiểm định mức vượt trội giữa hai cấu hình này. B1/B2 và hai bộ trọng số được so sánh ở screen; các biến thể không được giữ sau screen chưa được chấm toàn Dev.

Cấu hình khóa: B1/plain, hybrid Dense/Sparse/BM25/FTS/Exact = 0.35/0.15/0.35/0.05/0.10; pool nguồn 160; M3 rerank 100 với rank weight 0.85; Qwen chấm lại 40 nguồn đầu và kết hợp thứ hạng với weight 0.5; RRF k=60. Một cấu hình chung cho HS và Legal, không có luật theo Chương hoặc ánh xạ keyword → mã HS.

| Test HS shortlist | N | Hit@1 | Recall@5 | Recall@10 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| XIV | 49 | 51.0% | 91.8% | 98.0% | 0.6938 |
| XVI | 85 | 81.2% | 94.1% | 98.8% | 0.8696 |
| XVII | 54 | 63.0% | 83.3% | 94.4% | 0.7286 |
| Toàn HS | 188 | 68.1% | 90.4% | 97.3% | 0.7833 |

Các số HS trên là shortlist HS8 chiếu từ pool đã chấm. Trên Top-10 nguồn hỗn hợp, HS Hit@1 là 62.8%, Recall@10 là 93.6%. Legal Auto đủ mọi nhóm nguồn sơ cấp Top-10 đạt 121/130 (93.1%); MRR@10 đạt 0.7675. Gói nguồn bổ sung đủ nhóm đạt 123/130 (94.6%), là chỉ số riêng, không thay thế điểm Top-10 sơ cấp hoặc độ đúng câu trả lời.

Shortlist có Recall@5 90.4%, nhưng Hit@1 của XIV là 51.0%. Kết quả phù hợp hỗ trợ đối chiếu nguồn và lựa chọn ứng viên; chưa đủ để tự quyết định mã HS.

Runtime/replay khớp trên 6 câu Dev, mỗi câu thử auto/product/qa; cùng policy hash với Test. Kiểm thử triển khai: 104 passed (database tests bật), Ruff/format/mypy/diff đạt; hai notebook qua kiểm tra cú pháp, không phải thực thi toàn notebook. Các câu benchmark đã từng được xem; chưa có bằng chứng chất lượng trên Chương mới. Độ trễ không là tiêu chí lựa chọn trong lượt v5.

## Metadata và retrieval

Cùng PostgreSQL/pgvector, hai namespaces `hs_classification` và `legal_classification`. Dataset vẫn là `tt31`, `gir`, `tt85`, `scope`. Metadata gồm namespace/dataset/chunk_type/role, section/chapter/heading/hs6/ahtn8, source/effective_from/effective_to/legal_status. Legal status chỉ phản ánh metadata nguồn, không là xác minh pháp lý độc lập.

Tám chunk types: gir_rule, gir_explanation, section_note, chapter_note, subheading_note, tariff_entry, tariff_footnote, legal_clause. Structural/context records có chunk_type null khi không thuộc tám loại này; subtype nguồn được giữ nguyên. 5 mẫu TT85 giữ trong source template registry, không có vectors. Tạo Word chưa triển khai.

Các retrievers: dense BGE-M3, learned sparse token postings, Okapi BM25 từ `rank-bm25==0.2.2`/`BM25Okapi` (`k1=1.2,b=0.75,epsilon=0.25`, index trong RAM từ active PostgreSQL snapshot), FTS `simple+unaccent/ts_rank_cd`, Exact mã/thuộc tính kỹ thuật. Weighted RRF kết hợp thứ hạng với `k=60` trong policy đã khóa.

Cascade dùng BGE-reranker-v2-m3 và Qwen3-Reranker-0.6B với revision cố định. RRF kết hợp thứ hạng retrieval/reranker và thứ hạng hai tầng; không cộng trực tiếp raw logits của hai model. Cache ứng viên và score phục vụ resume/replay thực nghiệm.

Graph chứa hierarchy, notes, cross references của XIV/XVI/XVII; các external stubs có mã trong corpus được nối bằng RESOLVES_TO. Unknown external references vẫn là stubs, không biến thành căn cứ đầy đủ. Expansion có budget/omitted/missing-required IDs; Notes coverage không thay thế GIR/exclusion reasoning.

## Dữ liệu chuẩn hóa và hồ sơ hỗ trợ

Các file records/master/NODE/EDGE/schema được đăng ký tại `config/source_manifest.json`; PDF nguồn chuẩn nằm trong `data/raw`. Wording được đối chiếu với PDF, provenance và hashes đầu vào được kiểm chứng trước build.

`Section-XVII/supporting/SECTION_XVII_BENCHMARK_FINAL_CORRECTIONS.json` là nhật ký sửa dữ liệu được records/master hiện tại tham chiếu. Vai trò của file là provenance nguồn; không dùng để tìm ứng viên từ đáp án gold.

XVII có `SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl`; adapter chuyển các cạnh về schema chung. Node của XVII được lấy từ master, XIV từ GRAPH_NODES, XVI từ master và GRAPH_STRUCTURAL_NODES. Các định dạng xuất dữ liệu được nạp vào cùng một graph runtime trong PostgreSQL.

Adapter dùng `record_mapping` hoặc `source_locations` để ánh xạ alias export về chunk nguồn thật; kiểm tra ID, câu hỏi, case family và nguồn. Gold Dev/Test chỉ phục vụ đánh giá, không được ingest hoặc dùng để fine-tune embedding/reranker.

Auto yêu cầu policy chung đã kích hoạt và khớp snapshot/profile; thiếu policy sẽ báo lỗi. Khi thay nguồn, cần audit/build và kiểm chứng policy tương ứng trước khi phục vụ.
