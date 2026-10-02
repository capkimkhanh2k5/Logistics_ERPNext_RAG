# RAG — Knowledge Base, HS và QA

| Notebook | Workflow |
|---|---|
| `notebooks/01_build_knowledge_base.ipynb` | Audit manifest nguồn → GIR/TT85/HS → BGE-M3 → nạp snapshot mới trong transaction → QA |
| `notebooks/02_test_retrieval.ipynb` | Dev → chọn/khóa cấu hình HS chung → Test → chất lượng và latency |

V2 lưu report và predictions trong `artifacts/experiments/<run-id>`; notebook đọc cùng runtime/runner. Các module `rag/` giữ logic dùng chung để notebook và runtime dùng cùng implementation.

### Vai trò các file v2

| File | Vai trò |
|---|---|
| `rag/sources.py` | Đọc manifest, chuẩn hóa định dạng records/NODE/EDGE và quan hệ nguồn khi build corpus; không chọn mã HS theo sản phẩm. |
| `rag/experiments.py` | Nhóm các câu cùng họ/biến thể, lưu manifest và fold mappings cho đánh giá; v2 hiện chưa tối ưu tham số trong folds. |
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
| QA pháp lý | 650 | 520 | 130 | Dev chọn cấu hình QA; Test đánh giá policy đã khóa. |

File đang dùng nằm trong `data/verified/hs/dev_test/` và `data/verified/qa/dev_test/`, mỗi bộ gồm hai JSONL và một manifest. Các file giữ câu hỏi/đáp án gốc, thêm `original_split`, `eval_group_id`, `dev_fold`; HS có `query` đã loại nhãn/chỉ dẫn phân loại. Gold chỉ dùng để chấm, không vào corpus hoặc fine-tune BGE/Cross-Encoder.

HS phân tầng theo Chương, QA theo loại câu hỏi; cả hai giữ nguyên nhóm các câu cùng họ/biến thể. Không có nhóm nằm ở cả Dev và Test. Mỗi Dev có năm folds nội bộ để kiểm tra ổn định; folds không làm mô hình tự học thêm. Một số loại QA chỉ có 2–4 câu nên không thể đạt đúng 80/20 ở từng loại và có loại chưa xuất hiện trong Test; manifest ghi rõ số lượng thực tế.

Các file Train/Test/Holdout cũ và Excel chia theo tập cũ đã xóa khỏi thư mục dữ liệu đang dùng. Bản lưu cùng hashes ở `artifacts/experiments/run_shared_dev_v3/legacy_data/` chỉ phục vụ truy vết/reproduce dữ liệu; runtime, notebook và runner không đọc bản lưu để đánh giá. `.venv/bin/python scripts/prepare_dev_test.py` kiểm chứng/tái tạo hai bộ mới từ archive; mặc định từ chối thay nội dung đã khóa.

Tất cả câu hỏi đã từng được xem. Test mới là kiểm tra hồi quy trên phân chia theo nhóm mới, không phải Test mù và không chứng minh chất lượng ở Chương chưa có câu hỏi.

### Chọn cấu hình HS chung trên Dev

`scripts/tune_shared_retrieval.py dev` khóa danh sách 24 phương án trước khi chạy: Dense/BM25 trực tiếp 0.35/0.35 hoặc 0.55/0.15, tỷ trọng dense trong kênh graph 0 hoặc 0.5, pool 40/60/80, rank weight 0.85 hoặc 1.0. Các trọng số Sparse/FTS/Exact, ngân sách graph và source context dùng chung cho toàn corpus.

Tiêu chí là Macro MRR@10, Macro Recall@5 không giảm, Recall@5 mỗi Phần giảm tối đa 1 điểm phần trăm, và p95 runtime tối đa 3000 ms trên 30 câu Dev cân bằng giữa các Phần. Score neural cho cùng query/source được tái sử dụng khi so sánh cấu hình; latency phục vụ được đo riêng, bỏ query/reranker caches.

Sau khi lưu `locked_selection.json`, chạy `scripts/tune_shared_retrieval.py test` để chấm 188 câu Test với baseline và cấu hình đã chọn. Không dùng Test chọn lại cấu hình. Đây là chọn tham số Retrieval trên Dev, không phải fine-tune hoặc Nested CV. Kết quả nằm ở `artifacts/experiments/run_shared_dev_v3/`.

## Mở và chạy

Trong `frappe-bench/apps/aiAgent`:

```bash
.venv/bin/jupyter lab notebooks
```

Chọn kernel **Python (AI Agent RAG)**. Notebook 01 build corpus từ manifest; mặc định giữ snapshot cũ. Notebook 02 chọn policy HS trên Dev rồi chấm Test. QA trong notebook 01 dùng Dev 520 câu và Test 130 câu. Bản notebook 02 cũ được lưu ở `artifacts/experiments/run_generic_graph_v2/baseline/notebooks/02_test_retrieval.ipynb`.

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
- `artifacts/`: corpus snapshot và embedding cache/checkpoints cần cho resume; được gitignore. Đây là dữ liệu thực thi và báo cáo thực nghiệm; được gitignore.

## Retrieval khi đưa vào sử dụng

```python
from rag.db import connect
from rag.embedding import Embedder
from rag.retrieval import Retriever

with connect() as conn:
    retriever = Retriever(conn, Embedder())
    result = retriever.routed_search("Điện thoại thông minh 5G có hệ điều hành chạy ứng dụng")
```

`routed_search` nhận diện intent. Product dùng hybrid trên toàn corpus đã nạp → source context từ NODE/EDGE → Cross-Encoder chung → Notes làm bằng chứng đọc. Cấu hình ở `config/hybrid_retrieval.json`; không có policy theo Phần, injection danh sách mã theo từ khóa hoặc penalty thuộc tính theo prefix HS. Phạm vi mới có cùng pipeline sau khi đăng ký nguồn, audit, ingest/index.

Kết quả là shortlist có citation và `verification.status=REQUIRES_SOURCE_REASONING`. `decision_support` trả các mô tả/điều kiện nguồn cạnh nhau để đối chiếu và yêu cầu bổ sung thông số sản phẩm; chưa tự xác định thuộc tính thiếu hay ra kết luận HS. Dense context được dựng từ tất cả tariff entries và NODE/EDGE đang nạp, cache gắn snapshot/model/text hashes.

### Kết quả v2 trước nâng cấp Dev/Test — 01/10/2026

Snapshot `6ecd56f663a79e147ea7cdc3`; policy `generic-graph-v2-budget`, B1 mặc định. Chấm đủ 940 ca/798 nhóm đã xem; không fine-tune, không tune theo Chương, không gọi lượt này là nested OOF hoặc kiểm định mù.

| Phần | Số ca | Hit@1 | Recall@5 | Recall@10 | Cand@100 |
|---|---:|---:|---:|---:|---:|
| XIV | 244 | 48.4% | 67.6% | 73.4% | 87.7% |
| XVI | 426 | 74.4% | 90.1% | 95.1% | 98.8% |
| XVII | 270 | 58.1% | 86.7% | 89.3% | 94.1% |
| Toàn bộ | 940 | 63.0% | 83.3% | 87.8% | 94.6% |

Macro Hit@1 60.3%, Macro Recall@5 81.5%, MRR@10 toàn bộ 0.716. B0 chung đạt Hit@1 58.6%, Recall@5 73.7%; thêm graph source search và ngân sách kênh chung cải thiện shortlist. So với M5 lịch sử, XIV tăng Hit@1 nhưng Recall@5 giảm 1.2 điểm phần trăm; cần tiếp tục sửa coverage/context nguồn, không thêm luật theo mã.

QA primary evidence Top10 giữ nguyên: train 363/400, test 129/150, holdout 98/100. Runtime không dùng query/reranker cache, model/index đã warm, 30 câu cân bằng: p50 1593 ms, p95 1800 ms, một worker. Sau khi dọn helper chưa dùng và test tương ứng, 69/69 tests gồm PostgreSQL integration đã qua; lượt trước khi dọn đạt 70/70. Chương 72/Phần XV chỉ được kiểm tra đường mở rộng bằng fixture/model doubles; chưa đo chất lượng trên chương mới thật.

[Báo cáo và giới hạn đầy đủ](artifacts/experiments/run_generic_graph_v2_budget/IMPLEMENTATION_REPORT_V2.md).

## Metadata và retrieval

Cùng PostgreSQL/pgvector, hai namespaces `hs_classification` và `legal_classification`. Dataset vẫn là `tt31`, `gir`, `tt85`, `scope`. Metadata gồm namespace/dataset/chunk_type/role, section/chapter/heading/hs6/ahtn8, source/effective_from/effective_to/legal_status. Legal status chỉ phản ánh metadata nguồn, không là xác minh pháp lý độc lập.

Tám chunk types: gir_rule, gir_explanation, section_note, chapter_note, subheading_note, tariff_entry, tariff_footnote, legal_clause. Structural/context records có chunk_type null khi không thuộc tám loại này; subtype nguồn được giữ nguyên. 5 mẫu TT85 giữ trong source template registry, không có vectors. Tạo Word chưa triển khai.

Các retrievers: dense BGE-M3, learned sparse token postings, Okapi BM25 từ `rank-bm25==0.2.2`/`BM25Okapi` (`k1=1.2,b=0.75,epsilon=0.25`, index trong RAM từ active PostgreSQL snapshot), FTS `simple+unaccent/ts_rank_cd`, Exact mã/thuộc tính kỹ thuật. BM25 không được thay bằng FTS/sparse. Weighted RRF kết hợp rank, k=5/10/20/40/60/100/200. Trọng số chuẩn hóa về 1 là quy ước benchmark; toán học RRF không yêu cầu tổng bằng 1.

C11 cross-encoder BGE reranker v2-m3 pin revision; C12 BGE-M3 `colbert_score()` từ FlagEmbedding rerank top30 sau dense+sparse. Các scores reranker không cộng vào RRF. MPS dùng cho cross-encoder nếu có; BGE embedding/ColBERT giữ CPU FP32. Cache branches và reranking là artifacts phục vụ resume, không phải report.

Graph chứa hierarchy, notes, cross references của XIV/XVI/XVII; các external stubs có mã trong corpus được nối bằng RESOLVES_TO. Unknown external references vẫn là stubs, không biến thành căn cứ đầy đủ. Expansion có budget/omitted/missing-required IDs; Notes coverage không thay thế GIR/exclusion reasoning.

## Benchmark lịch sử trước v2

Các bảng dưới đây là kết quả lưu từ runtime cũ; không mô tả cấu hình hay chất lượng v2. V2 dùng giao thức cố định B0/B1/B2; xem report hiện tại ở `artifacts/experiments/run_generic_graph_v2_budget/IMPLEMENTATION_REPORT_V2.md`.

Dùng `data/verified/hs/train/HS_RAG_TRAIN.jsonl` (709 sản phẩm), `test/HS_RAG_TEST.jsonl` (143) và `holdout/HS_RAG_HOLDOUT.jsonl` (88). Train/test không trùng sản phẩm hoặc `case_family_id`; có 22 mã HS xuất hiện ở cả train và test. Train có phần tune/validation tách theo `case_family_id` để chọn trọng số. Test và holdout hiện là các tập **hồi quy** vì đã được xem trên snapshot trước; muốn xác nhận khách quan policy mới cần holdout chưa sử dụng. Không fine-tune BGE và không ingest gold. Query được dựng từ tên/mô tả kỹ thuật, không dùng nhãn hoặc câu trả lời.

C1–C15, nhiều bộ trọng số và RRF k được quét trên TRAIN; chính sách cũ cũng là một candidate. Tập validation nội bộ chọn cấu hình cho từng Phần và router. Sau đó notebook thử nhánh tài liệu cha theo `CONTAINS`, định nghĩa Notes và Cross-Encoder trên cùng ngân sách ứng viên. Không dùng nhãn test/holdout để chọn. Ngữ cảnh bổ sung tại thời điểm truy xuất luôn giữ bản ghi và locator riêng, không ghi ngược vào corpus nguồn.

Lần chạy lại từ DB và dữ liệu chuẩn hóa mới nhất tạo snapshot `fdcdfb0db6d856f81b329680`: XIV C9 Dense .35 / BM25 .35 / Exact .30; XVI C6 Dense .145 / BM25 .855; XVII C15 Sparse .266 / BM25 .733 / Exact .001. Hệ thống đã xử lý triệt để rò rỉ nhãn trên tập TRAIN (từ 151/709 mẫu bị lọt nhãn về 0/709 mẫu), mở rộng ứng viên phân cấp cha với quota bảo đảm và làm giàu ngữ cảnh nhóm/phân nhóm vào `rerank_text` cho Cross-Encoder pool 40 (rank_weight 0.75).

| Phần | Test Cand@100 / Hit@1 / Recall@5 | Holdout Cand@100 / Hit@1 / Recall@5 |
|---|---:|---:|
| XIV | 89.6% / 25.0% / 45.8% | 96.6% / 31.0% / 72.4% |
| XVI | 97.9% / 78.7% / 93.6% | 100.0% / 55.2% / 75.9% |
| XVII | 95.8% / 47.9% / 77.1% | 83.3% / 33.3% / 50.0% |
| **Toàn bộ** | **94.4% / 50.3% / 72.0%** | **93.2% / 39.8% / 65.9%** |

Đây là **Top-K retrieval**, không phải độ chính xác kết luận mã HS. Holdout Top-2 Section Recall đạt 87/88 ca. Cơ sở dữ liệu đồng bộ chứa 5.356 chunk/embedding, 5.521 graph nodes, 6.655 graph edges và 94.649 sparse postings.

### Phễu ứng viên & Thử nghiệm Rerank Pool 40 / 60 / 100 (Snapshot fdcdfb0db6d856f81b329680)

Hệ thống đã dành chỗ cho ứng viên cha ngay trong Top-40 (`definition_fusion` với `top_quota_pool`). Dưới đây là đo đạc chi tiết chuỗi chuyển đổi: **Cand@40 → Recall@10 → Recall@5 → Hit@1** cùng độ trễ p50/p95 (ms) trên 2 dạng query: `name_only` (chỉ tên hàng) và `name_and_spec` (tên hàng kèm thông số kỹ thuật):

#### Tập HOLDOUT (88 ca):
| Dạng Query | Pool | Cand@40 | Cand@100 | Recall@10 | Recall@5 | Hit@1 | Latency p50 / p95 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `name_only` | **40** | **76.1%** (67/88) | 93.2% (82/88) | 73.9% (65/88) | 68.2% (60/88) | 33.0% (29/88) | **171.8 ms / 691.9 ms** |
| `name_only` | **60** | 71.6% (63/88) | 93.2% (82/88) | 83.0% (73/88) | 71.6% (63/88) | 31.8% (28/88) | 602.7 ms / 978.5 ms |
| `name_only` | **100** | 56.8% (50/88) | 93.2% (82/88) | 85.2% (75/88) | 73.9% (65/88) | 36.4% (32/88) | 950.6 ms / 1314.9 ms |
| `name_and_spec` | **40** | **79.5%** (70/88) | 96.6% (85/88) | 72.7% (64/88) | 68.2% (60/88) | 36.4% (32/88) | **1377.5 ms / 1741.8 ms** |
| `name_and_spec` | **60** | 72.7% (64/88) | 96.6% (85/88) | 78.4% (69/88) | 73.9% (65/88) | 38.6% (34/88) | 815.3 ms / 1152.2 ms |
| `name_and_spec` | **100** | 58.0% (51/88) | 96.6% (85/88) | 84.1% (74/88) | 80.7% (71/88) | 39.8% (35/88) | 1305.7 ms / 1660.0 ms |

#### Tập TEST (143 ca):
| Dạng Query | Pool | Cand@40 | Cand@100 | Recall@10 | Recall@5 | Hit@1 | Latency p50 / p95 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `name_only` | **40** | **81.1%** (116/143) | 94.4% (135/143) | 79.7% (114/143) | 72.7% (104/143) | 46.2% (66/143) | **157.9 ms / 617.5 ms** |
| `name_only` | **60** | 76.2% (109/143) | 94.4% (135/143) | 87.4% (125/143) | 76.2% (109/143) | 44.1% (63/143) | 610.9 ms / 929.0 ms |
| `name_only` | **100** | 59.4% (85/143) | 94.4% (135/143) | 91.6% (131/143) | 76.2% (109/143) | 44.1% (63/143) | 1043.9 ms / 1457.9 ms |
| `name_and_spec` | **40** | **82.5%** (118/143) | 95.8% (137/143) | 79.0% (113/143) | 75.5% (108/143) | 49.0% (70/143) | **1387.5 ms / 1701.6 ms** |
| `name_and_spec` | **60** | 79.7% (114/143) | 95.8% (137/143) | 83.9% (120/143) | 76.2% (109/143) | 46.9% (67/143) | 836.5 ms / 1168.7 ms |
| `name_and_spec` | **100** | 62.2% (89/143) | 95.1% (136/143) | 86.7% (124/143) | 74.8% (107/143) | 44.1% (63/143) | 1291.4 ms / 1720.6 ms |

### Đo tải đồng thời (Concurrent Load Benchmark)

Đo kiểm thử hiệu năng và độ trễ trên 40 queries ngẫu nhiên với các mức tải đồng thời:
| Concurrency (Workers) | Throughput (QPS) | Latency p50 | Latency p90 | Latency p95 | Tổng thời gian (40 req) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | 0.42 req/s | 2.10 s | 2.40 s | 2.45 s | 95.5 s |
| **2** | **0.47 req/s** | 3.80 s | 4.20 s | 4.32 s | **85.6 s** |
| **4** | 0.43 req/s | 8.42 s | 9.23 s | 9.80 s | 93.6 s |
| **8** | 0.34 req/s | 22.06 s | 26.07 s | 27.30 s | 119.0 s |

*Khuyến nghị vận hành*: Do Cross-Encoder và BGE-M3 chạy CPU/MPS là tác vụ ngốn tài nguyên tính toán chuyên sâu, mức điều phối tối ưu là 2 worker processes đồng thời để đạt thông lượng cao nhất mà không gây tranh chấp CPU core.

### Kiểm định độc lập mù từ đầu (Fresh Blind Benchmark — 100 ca phân tầng)

Để đảm bảo tính khách quan và minh bạch tuyệt đối, hệ thống đã trích xuất phân tầng (Stratified Sampling theo tỷ lệ XIV: 26, XVI: 45, XVII: 29) một tập 100 sản phẩm hoàn toàn mới chưa từng dùng để tune bất kỳ tham số nào, với cấu hình đã khóa cứng (Pool 40, rank_weight 0.75):
| Dạng Query | Cand@40 | Cand@100 | Recall@10 | Recall@5 | Hit@1 |
|---|:---:|:---:|:---:|:---:|:---:|
| `name_only` | **77.0%** (77/100) | 93.0% (93/100) | 77.0% (77/100) | 71.0% (71/100) | 40.0% (40/100) |
| `name_and_spec` | **85.0%** (85/100) | **97.0%** (97/100) | **85.0%** (85/100) | **80.0%** (80/100) | **51.0%** (51/100) |

*Phân rã Section trên Fresh Blind (`name_and_spec`)*:
- Phần XIV (26 ca): Cand@40 73.1%, Cand@100 96.2%, Rec@5 61.5%, Hit@1 50.0%.
- Phần XVI (45 ca): Cand@40 95.6%, Cand@100 97.8%, Rec@5 95.6%, Hit@1 68.9%.
- Phần XVII (29 ca): Cand@40 79.3%, Cand@100 96.6%, Rec@5 72.4%, Hit@1 24.1%.

### Đánh giá Chéo Phân tầng Lồng nhau (Nested Stratified Group CV: 5 Outer Folds, 3 Inner Folds — Toàn bộ 940 ca HS)

Để bảo đảm tính khách quan, khoa học và tránh rò rỉ dữ liệu khi không bổ sung thêm tệp mới từ bên ngoài, toàn bộ 940 ca HS được nhóm thành 798 `eval_group_id` (Disjoint Set Union, Jaccard threshold ≥ 0.70) và đánh giá qua quy trình Nested Stratified Group CV (5 outer folds, 3 inner folds) với các phương pháp ablation tích luỹ từ M0 đến M5 (đã khắc phục triệt để các lỗi điều kiện thuộc tính, phân cấp CKD/CBU từ catalog nguồn, cơ chế quota budget độc lập và tối ưu hoá siêu tham số phân tầng cân bằng):

| Phương pháp | Mô tả kỹ thuật | Macro Hit@1 | Macro Recall@5 | Macro MRR@10 | Cand@100 | Micro Hit@1 (ALL) | Micro Recall@5 (ALL) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **M0** | Baseline historical & CV (pool 40, raw text, không context chain) | **50.3%** | 76.6% | 0.613 | 94.9% | 53.3% | 78.9% |
| **M1** | Full hierarchy & context views (XIV, XVII enriched branches) | **50.3%** | 76.6% | 0.613 | 94.9% | 53.3% | 78.9% |
| **M2** | Trích xuất thuộc tính & phạt mâu thuẫn (CKD/CBU grounded, cc, GVW, platin) | **51.4%** | 76.7% | 0.621 | 94.9% | 54.3% | 79.1% |
| **M3** | Applicability chú giải & query kênh trường (tiêm evidence vào Top rerank pool) | **51.4%** | 76.7% | 0.621 | 95.0% | 54.3% | 79.1% |
| **M4** | Ngân sách quota độc lập (28 direct, 8 evidence, 4 domain attribute) | **55.0%** | 78.2% | 0.653 | 95.0% | 58.0% | 80.1% |
| **M5** | Nested Stratified Inner CV (tối ưu hóa tham số rank/penalty/pool theo từng fold) | **53.7%** | **79.4%** | **0.647** | **95.0%** | **56.7%** | **81.4%** |

*Chi tiết từng Phần trên M5 (Out-Of-Fold)*:
- **Phần XIV (244 ca)**: Hit@1 **41.8%** (tăng +1.2% so với M0: 40.6%), Recall@5 **68.9%** (tăng +4.1% so với M0: 64.8%), Recall@10 **75.4%** (tăng +3.3% so với M0: 72.1%), Cand@100 92.6%, MRR@10 0.533.
- **Phần XVI (426 ca)**: Hit@1 **69.7%** (tăng +3.0% so với M0: 66.7%), Recall@5 **89.4%** (tăng +0.7% so với M0: 88.7%), Recall@10 **92.3%** (tăng +1.2% so với M0: 91.1%), Cand@100 98.1%, MRR@10 0.784.
- **Phần XVII (270 ca)**: Hit@1 **49.6%** (tăng +5.9% so với M0: 43.7%), Recall@5 **80.0%** (tăng +3.7% so với M0: 76.3%), Recall@10 **82.6%** (tăng +4.8% so với M0: 77.8%), Cand@100 92.2%, MRR@10 0.625.

*Kiểm định ý nghĩa thống kê Toàn diện giữa M5 và Baseline M0 (798 cụm sản phẩm, 940 ca HS)*:

1. **Micro Metrics (tính trên 940 câu cá nhân, kèm Cluster Bootstrap 95% CI)**:
   - **HIT@1**: Delta **+3.4%** [1.4%, 5.6%] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)
   - **RECALL@5**: Delta **+2.4%** [0.9%, 4.1%] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)
   - **RECALL@10**: Delta **+2.8%** [1.5%, 4.2%] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)
   - **MRR@10**: Delta **+0.032** [0.017, 0.050] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)

2. **Group-Averaged Metrics (bình quân trên 798 cụm độc lập, tránh thiên lệch cụm lớn)**:
   - **HIT@1**: Delta **+2.6%** [1.0%, 4.3%] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)
   - **RECALL@5**: Delta **+2.1%** [0.8%, 3.4%] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)
   - **RECALL@10**: Delta **+2.5%** [1.4%, 3.7%] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)
   - **MRR@10**: Delta **+0.026** [0.015, 0.038] ✅ CÓ Ý NGHĨA THỐNG KÊ (CI > 0)

3. **Kiểm định Giả thuyết Không (Fisher-Pitman Cluster Sign-Flip Permutation Test — 5.000 hoán vị under H0)**:
   - **HIT@1**: T_obs = +0.0257, Monte Carlo p = **0.0014** (2-sided: 0.0020) ✅ Bác bỏ H0
   - **RECALL@5**: T_obs = +0.0210, Monte Carlo p = **0.0010** (2-sided: 0.0018) ✅ Bác bỏ H0
   - **RECALL@10**: T_obs = +0.0251, Monte Carlo p < **0.0002** (2-sided: < 0.0002) ✅ Bác bỏ H0
   - **MRR@10**: T_obs = +0.0264, Monte Carlo p < **0.0002** (2-sided: < 0.0002) ✅ Bác bỏ H0

*Đo lường Độ trễ Vận hành Thực tế (Fresh End-to-End Runtime Latency — không dùng cache)*:
Đo trực tiếp trên runtime `Retriever.adaptive_search` (gồm pgvector search 5.356 chunks + graph expansion + candidate context enrichment + quota budget 28/8/4 + Cross-Encoder reranking):
- **Pool 40**: p50 = 1283.9 ms, p95 = 1598.1 ms (giai đoạn nạp model khởi động)
- **Pool 50 (Khuyến nghị vận hành M5)**: Mean = 559.6 ms, **p50 = 553.7 ms**, p90 = 606.3 ms, **p95 = 639.0 ms**
- **Pool 60**: Mean = 566.5 ms, **p50 = 572.1 ms**, p90 = 604.9 ms, **p95 = 773.2 ms**

*Đồng bộ hóa Runtime và Production Policy*:
Toàn bộ logic của M5 (ngân sách Quota Budget 28/8/4, context hierarchy enrichment từ catalog nguồn và phạt mâu thuẫn thuộc tính) đã được đóng gói vào module `rag/quota.py`, tích hợp trực tiếp vào runtime `Retriever.adaptive_search` và được lưu khóa trong cấu hình production `config/selected_retrieval.json` (`rank_weight: 0.85`, `penalty_weight: 0.10`, `rerank_pool: 40`, `quota_budget: true`).

*Hiệu năng hồi quy trên các tập ban đầu khi tích hợp M5 vào `Retriever.adaptive_search`*:
- **Tập Holdout (88 ca)**: Hit@1 tăng từ 25.0% lên **40.9%** (36/88 ca, +15.9%), Recall@5 tăng từ 51.1% lên **70.5%** (62/88 ca, +19.4%).
  - XIV Holdout: Hit@1 17.2% → **27.6%** (+10.4%), Recall@5 51.7% → **62.1%** (+10.4%)
  - XVI Holdout: Hit@1 34.5% → **55.2%** (+20.7%), Recall@5 62.1% → **79.3%** (+17.2%)
  - XVII Holdout: Hit@1 23.3% → **40.0%** (+16.7%), Recall@5 40.0% → **70.0%** (+30.0%)
- **Tập Test (143 ca)**: Hit@1 đạt **53.1%**, Recall@5 đạt **72.7%** (Phần XVII Hit@1 tăng từ 25.0% lên **52.1%**, Recall@5 tăng từ 70.8% lên **83.3%**).
- **QA Pháp lý (650 ca)**: Test đạt **129/150 (86.0%)**, Holdout đạt **98/100 (98.0%)**, đảm bảo không suy giảm hiệu năng trích xuất chứng cứ pháp lý.

GIR Rule Engine, Critic, LLM generation, Agent2/FastAPI/ERP integration thuộc giai đoạn tiếp theo.

Adapters dùng tên `tt31_section_xiv`, `tt31_section_xvi`, `tt31_section_xvii`; metadata `dataset=tt31` là nguồn thông tư chung, `section` xác định Phần. Không sử dụng tên `tt31` để chỉ riêng adapter XVI. Các HS6 không có dòng nguồn riêng được bổ sung graph-only nodes từ prefix AHTN8, có virtual=true/legal_text_available=false; không tạo nội dung pháp lý hoặc embedding giả.

### Ngữ cảnh định nghĩa và quan hệ cha

`definition_candidates` chỉ đi theo cạnh định nghĩa dương; không biến cạnh loại trừ thành đề xuất HS. `parent_candidates` chỉ duyệt các cạnh `CONTAINS` đến bản ghi thật có nguồn và locator. Các nhánh được thử trên TRAIN; chính sách hiện chọn trọng số parent .2 cho XIV/XVII, 0 cho XVI, còn nhánh definition candidate có trọng số 0. XIV/XVII dùng `definition_context` khi rerank, lấy văn bản từ bản ghi Note độc lập có citation. Không bước nào ghi các đoạn đó vào `source_text` hoặc search text của dòng biểu thuế.

## Dữ liệu chuẩn hóa và hồ sơ hỗ trợ

Các file records/master/NODE/EDGE/schema được đăng ký tại `config/source_manifest.json`; PDF/DOCX gốc nằm trong `data/raw`. Sau kiểm tra phụ thuộc, 21 bản xuất phụ/chỉ mục/báo cáo không được pipeline đọc hoặc nguồn đang dùng tham chiếu đã được xóa. Hai thư mục `Section-XIV/supporting` và `Section-XVI/supporting` đã được xóa khi rỗng.

`Section-XVII/supporting` còn hai file: `SECTION_XVII_ENRICHED_CATALOG.json` là annotation nguồn đang được ingest để dựng context assembly, và `SECTION_XVII_BENCHMARK_FINAL_CORRECTIONS.json` là nhật ký sửa dữ liệu được records/master hiện tại tham chiếu. Tên file có "BENCHMARK" nhưng vai trò hiện tại là provenance của dữ liệu nguồn; không được dùng để tìm ứng viên từ đáp án gold. Hash của các đầu vào active được kiểm chứng từ manifest/corpus.

XVII có `SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl`; adapter chuyển các cạnh về schema chung. Node của XVII được lấy từ master, XIV từ GRAPH_NODES, XVI từ master và GRAPH_STRUCTURAL_NODES. Đây là khác biệt định dạng xuất dữ liệu, cùng một graph runtime trong PostgreSQL.

### Sửa đầu vào đã đối chiếu nguồn — 2026-09-29

Các lỗi OCR đã được đối chiếu với PDF nguồn và sửa trong dữ liệu chuẩn hóa trước lượt chạy này; cell đầu notebook 01 nay chỉ kiểm tra schema v2 và văn bản tiếng Việt mà không ghi lại nguồn. Các trường embedding/BM25/FTS của XIV/XVI/XVII chỉ dùng mã và văn bản tiếng Việt của **chính bản ghi**; không nối mô tả của cha hoặc Chú giải vào văn bản ingest. Riêng 85.34, Chú giải 8 là một bản ghi độc lập với ID và locator riêng. Năm dòng XVI bị OCR trộn hai cột ngôn ngữ đã được sửa theo cột tiếng Việt. Cột tiếng Anh và bản trích xuất thô vẫn giữ để kiểm toán. ID, mã HS và graph giữ nguyên. Mọi kết quả benchmark của snapshot trước khi sửa corpus chỉ có giá trị lịch sử.

Phần XVII bổ sung sửa OCR `0 tô` → `Ô tô` trong 173 mô tả Chương 87 sau khi kiểm tra mẫu trên ảnh PDF; bản trích xuất thô vẫn được giữ. HS6 và Heading cha là các bản ghi riêng có locator; quan hệ cha được giữ bằng cạnh `CONTAINS` trong graph. Nhánh tìm tài liệu cha trong notebook 02 chỉ duyệt các cạnh này.

## QA: 400 train / 150 test / 100 holdout

`data/verified/qa/train/LEGAL_RETRIEVAL_TRAIN.jsonl` chứa 400 câu, `data/verified/qa/test/LEGAL_RETRIEVAL_TEST.jsonl` chứa 150 câu, và `holdout/LEGAL_RETRIEVAL_HOLDOUT.jsonl` chứa 100 câu và chỉ dùng sau khi khóa chính sách. Adapter dùng `record_mapping` hoặc `source_locations` để ánh xạ alias export về chunk nguồn thật; kiểm tra ID, câu hỏi, case family và nguồn. Gold không được ingest, không fine-tune model và không dùng nhãn test để chọn chính sách.

Phần QA notebook 01 thử các họ retriever/trọng số trên QA train, sau đó so sánh đường trực tiếp với đường thêm tài liệu cha và Notes thật trước Cross-Encoder. Thử pool 30/50/100, phần ứng viên trực tiếp được giữ, và nhánh truy vấn bỏ mã đang bị nghi vấn. Chọn policy trên train và ghi khóa `qa` trong `config/selected_retrieval.json`; giữ nguyên chính sách HS. Top-10 được chấm theo ID chunk primary chính xác; gói căn cứ được chấm riêng. 50 test cũ từng được dùng để chẩn đoán nên báo riêng với 100 test mới. Kết quả là đánh giá retrieval trên bộ dữ liệu đã cung cấp, chưa phải chứng minh chất lượng kết luận pháp lý cuối cùng.

Trên snapshot `fdcdfb0db6d856f81b329680`, QA TRAIN 400 câu chọn C10 graph_30_70: Dense .25 / Sparse .25 / BM25 .10 / FTS .10 / Exact .30, RRF k5, Cross-Encoder pool30, giữ 70% ứng viên trực tiếp trước khi thêm căn cứ graph. Đủ mọi primary chunk trong Top-10: **363/400 (90,8%) train**, **129/150 (86,0%) test** và **98/100 (98,0%) holdout**; Top-5 holdout là 95/100 (95,0%). Gói căn cứ (package_all) đạt 363/400 (90,8%) trên train, 134/150 (89,3%) trên test và 98/100 (98,0%) trên holdout; mean group recall@10 đạt 91,1% train, 87,8% test, 98,0% holdout. QA test cũ là tập hồi quy; holdout đã được dùng để chẩn đoán nguồn nên không còn mù hoàn toàn. Đây là chất lượng retrieval, chưa kiểm chứng suy luận pháp lý.

`Retriever.qa_search(query)` hoặc `knowledge_search(query)` khi đã có chính sách QA dùng corpus chung với các chunk type GIR, Notes, TT85, tariff entry ở nhiều tầng. Không cố định role/level, không hard-filter Section. Query gốc đi vào semantic/lexical retrieval; Exact che các mã được nhắc để nghi vấn/phủ định. Nhánh truy vấn bổ sung dùng câu đã bỏ mã nghi vấn để tìm hàng hóa, và chỉ hoạt động nếu chọn trên train. Gói bổ sung có graph evidence, các tài liệu cha thật, Notes của các nhánh/mã được nhắc và các rule cùng họ GIR đã tìm được; việc lấy đủ tài liệu không thay thế suy luận pháp lý.

`knowledge_search(policy="hs_transfer")` tái lập thí nghiệm chuyển chính sách HS vào các kênh HS4/HS6/AHTN8; `policy="legacy_fixed"` tái lập baseline đa tầng cũ. `routed_search` chuyển câu hỏi GIR/Notes/thủ tục sang chính sách QA khi đã có; nhánh sản phẩm vẫn dùng `adaptive_search` và chính sách HS hiện có. Các cơ chế che mã nghi vấn và mở rộng căn cứ QA không được tự động áp vào xếp hạng ứng viên sản phẩm.
