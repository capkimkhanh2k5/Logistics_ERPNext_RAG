# Phân tích dữ liệu và kế hoạch RAG Ingestion → BGE-M3 → PostgreSQL/pgvector → Hybrid Retrieval → Retrieval Test

Ngày phân tích: 2026-09-26. Đường dẫn tương đối trong tài liệu tính từ `frappe-bench/`.

## 1. Mục tiêu và phạm vi

Xây dựng pipeline retrieval có thể tái chạy, kiểm chứng và giải thích cho corpus HS Phần XVI (Chương 84–85), GIR và TT85. Ưu tiên **Jupyter Notebook** để khảo sát, ingestion, embedding và đánh giá. Kết quả gồm danh sách mã ứng viên và bằng chứng có nguồn; kết luận phân loại HS, GIR Rule Engine đầy đủ, Critic, LLM generation, thuế suất và tích hợp ERPNext thuộc giai đoạn sau.

Đây là phân tích cấu trúc và tính nhất quán dữ liệu local, chưa phải xác minh độc lập tính đúng đắn pháp lý của mọi nguồn hoặc đo chất lượng retrieval. Chưa tải BGE-M3, tạo database hay chạy benchmark.

## 2. Kết quả khảo sát thực tế

`apps/aiAgent/` hiện có data, docs và `workFlows.md`; chưa có mã Python, notebook hoặc dependency manifest cho pipeline. Compose hiện dùng MariaDB cho Frappe, chưa định nghĩa PostgreSQL/pgvector. Tài liệu kiến trúc đã đề xuất FastAPI + BGE-M3 + PostgreSQL và graph; có thể triển khai retrieval riêng trước.

### 2.1. Inventory và nguồn ingest chính thức

| Dataset | File chính trong `apps/aiAgent/data/normalized/` | Số record | Vai trò |
|---|---|---:|---|
| TT31 | `TT31/SECTION_XVI_RAG_INGEST.jsonl` | 3.421 | Corpus HS, notes và hierarchy context |
| GIR | `6_GIR /GIR_RAG_VI_COMBINED.jsonl` | 115 | 11 core + 104 explanatory |
| TT85 | `TT85/tt85_rag_chunks_source.jsonl` | 100 | Tra cứu quy trình và căn cứ theo điều/khoản/điểm |
| HS scope | `HS_Index/HS_2022_SCOPE_INDEX_VI_FINAL.json` → `records` | 97 | Router 21 phần / 97 mục chương, chỉ 84–85 có chi tiết |
| Graph nodes | `TT31/SECTION_XVI_GRAPH_STRUCTURAL_NODES.jsonl` | 3 | Section XVI + hai chapter |
| Graph edges | `TT31/SECTION_XVI_GRAPH_EDGES.jsonl` | 3.762 | Quan hệ phân cấp, notes, context, references |
| Exact index | `TT31/SECTION_XVI_EXACT_CODE_INDEX.csv` | 2.764 | Lookup mã 4/6/8 số |
| Gold test | `apps/aiAgent/data/test/HS_ELECTRONICS_GOLD_TESTSET_50_VERIFIED.jsonl` | 50 | Đánh giá mã ứng viên; vị trí thật là `apps/aiAgent/data/test/` |

**3.636 source chunks chính** = 3.421 + 115 + 100. Nếu embed scope index thì baseline có **3.733 retrieval records**, graph structural nodes lưu riêng. Các view ghép ngữ cảnh và form bổ sung sẽ làm số embedding thay đổi; phải ghi manifest, không dùng 3.733 làm count cố định cho mọi cấu hình.

Không ingest mọi file normalized: JSON/CSV/Markdown/XLSX có thể là các biểu diễn của cùng dữ liệu. GIR combined đã chứa core và explanatory; TT31 master/raw/ingest là các phiên bản cùng record; TT85 definitions/articles trùng một phần với chunks. Chọn allowlist để tránh lặp và không ingest `data/test` vào corpus.

Thư mục `6_GIR ` có dấu cách cuối tên. Loader dùng `pathlib.Path` và đường dẫn cấu hình chính xác; không đổi tên trong bước phân tích.

### 2.2. TT31: nền tảng tốt nhưng phải nối master

Đã kiểm đếm từ JSONL:

- 2.764 tariff records: 134 heading, 418 HS6, 2.212 AHTN8.
- 112 legal notes: 29 section, 74 chapter, 9 subheading.
- 537 context và 8 source footnotes.
- 3.421 ID duy nhất, không có text rỗng; 76 bản ghi vượt số lượng text duy nhất. Đây là trùng wording, chưa phải duplicate pháp lý; không xóa chỉ vì cùng text.
- Text retrieval: trung vị 280 ký tự, tối đa 1.252 ký tự. Đây là **ký tự**, chưa phải token BGE-M3.
- Join ingest → `SECTION_XVI_MASTER_NORMALIZED.jsonl` theo ID đủ 3.421/3.421; text ingest khớp `retrieval.embedding_text_vi` trong master.
- Graph có 0 cạnh bị thiếu endpoint khi tính cả 3 structural nodes.
- Quan hệ: CONTAINS 2.766; CONSTRAINED_BY 172; APPLIES_WITHIN 112; REFERENCES_CODE 143; CONTEXT_WITHIN 537; ANNOTATES_SCOPE 4; ANNOTATES 8; NORMALIZED_REFERENCE_TO 20.

Ingest file có `id/text/sparse_text/metadata`; master có thêm `source`, `source_text_vi`, `text_vi`, `title_vi`, `content_sha256`, verification và context chi tiết. **Dùng ingest cho nội dung tìm kiếm, join master cho provenance và citation.** Schema JSON hiện mô tả master (`record_id`, `text_vi`, ...), không áp trực tiếp lên wrapper ingest.

Các mô tả như “Loại khác” cần ancestor context. Nhiều tariff texts đã có Nhóm/HS6/Ngữ cảnh phân cấp: giữ baseline nguyên trạng trước, chỉ bổ sung khi thực sự thiếu. Context trùng wording nhưng khác vị trí có thể mang ý nghĩa khác.

Manifest báo 54 record được chuẩn hóa retrieval và 3 source anomalies đã xử lý vận hành. Giữ warning/resolution IDs và song song wording nguồn với wording operational; trích dẫn nguồn phải phân biệt hai bản này. Các heading derived `8449`, `8548` phải giữ provenance derived, không trình bày như dòng nguồn explicit.

### 2.3. GIR: cần view có ngữ cảnh

Schema sử dụng `text_vi`, `rule`, `subrule`, `source_pages`, `source_ids`, `dataset_layer`, `retrieval_priority`. P0 core và P1 explanatory là metadata ưu tiên, không tự động trở thành điểm relevance.

Có chunks rất ngắn: “Các ví dụ:” (8 ký tự), “Sản phẩm hỗn hợp.”, “Phân loại vào nhóm 16.02.”. Đề xuất:

1. Giữ nguyên toàn bộ 115 source records để audit.
2. Tạo `embedding_text` thêm nhãn rule/subrule và ngữ cảnh liên quan.
3. Với đoạn phụ thuộc, tạo passage từ đoạn trước/sau đã xác minh cùng mục, giữ `source_chunk_ids` theo thứ tự và trang nguồn. Không suy parent chỉ từ ID hoặc tự ghép xuyên rule.
4. So sánh baseline atomic và context view trên bộ test GIR riêng.

Ví dụ GIR ngoài Chương 84–85 vẫn cần giữ như nội dung giải thích quy tắc; không biến mã được nhắc trong ví dụ thành HS candidate trong phạm vi MVP.

### 2.4. TT85: tách source và derived

100 chunks có `chunk_id`, `source_id`, `document_no`, `article_no`, `article_title`, `unit_level`, `unit_label`, `text`, `effective_from`; không có trang PDF. Citation theo văn bản + điều/khoản/điểm + source file, không tự tạo số trang.

Metadata local ghi `85/2026/TT-BTC`, ngày hiệu lực `2026-09-15`, 17 điều, 5 forms. Cần đối chiếu nguồn trước khi gắn trạng thái legal-verified. `source_filename` ghi `ThongTu_85-2026_TT-BTC(1).docx`, file thật là `data/raw/ThongTu_85-2026_TT-BTC.docx`. SHA-256 file raw khớp `source_sha256` trong metadata. Đây là lệch tên với nội dung khớp hash; loader cần ánh xạ đúng path. Hash khớp không thay thế xác minh nguồn pháp lý.

Các đoạn như `TT85-A6-1.a` chỉ có tên một tài liệu; cần thêm article title và phần dẫn của khoản bằng join `tt85_articles_source.json`. Tạo search view nhưng giữ text nguồn.

`tt85_forms_source.json` có 5 mẫu: nếu hỗ trợ tra cứu mẫu/hồ sơ thì thêm form chunks riêng có ID ổn định; baseline 100 chunks chưa chứng minh bao phủ nội dung 5 mẫu. `definitions` và Điều 13 sources chủ yếu dùng enrichment/lookup, tránh duplicate ingestion.

`TT85/derived_ai/*` là dữ liệu dẫn xuất. Dùng cho routing hoặc cấu hình có provenance, không trộn thành bằng chứng nguyên văn. Không xem tên tài liệu trong Điều 13 là bằng chứng đã có toàn văn tài liệu đó trong corpus.

### 2.5. Scope router

Index là object có `records`, không phải list ở root. Có 97 chapter entries (bao gồm Chương 77 dự phòng), 21 section labels. Chỉ 84–85 có corpus HS chi tiết.

Giữ scope index riêng. Truy vấn sản phẩm có thể tìm top chapters làm **gợi ý**, nhưng title index không đủ đảm bảo phân loại scope chính xác. Dùng trạng thái `IN_SCOPE`, `OUT_OF_SCOPE`, `UNCERTAIN`; khi chưa chắc 84 hay 85, search cả hai. Truy vấn GIR hoặc TT85 đi theo intent pháp lý, không bị router sản phẩm loại bỏ. Có thể trả nội dung note tham chiếu ngoài scope nhưng không tuyên bố có tariff chi tiết chương đó.

### 2.6. Gold test: dùng được cho candidate retrieval

- 50 case, 45 mã AHTN8 duy nhất; 28 case Chương 84 và 22 case Chương 85.
- 50/50 expected codes tồn tại trong corpus; chapter và heading label khớp prefix mã.
- 10 label A+, 40 label A là mức ghi trong file, chưa phải xác minh lại trong lần phân tích này.
- Nhiều sản phẩm cùng mã `84716040`; chia dev/test ngẫu nhiên theo dòng có thể làm cùng code xuất hiện ở cả hai.
- Mô tả kỹ thuật thường gần wording danh mục; kết quả có thể cao hơn truy vấn người dùng thực tế.
- Không có gold note IDs, GIR IDs, TT85 chunk IDs, OUT_OF_SCOPE hoặc NEED_MORE_INFORMATION.
- Một số metadata ghi primary document TT31 nhưng URL official trỏ NĐ26: cần xác minh hoặc tách nguồn gốc label, không xóa/chỉnh label tự động.

Bộ này đo được **gold-code Hit@k và MRR**, chưa đủ để đo đầy đủ legal evidence recall hay độ chính xác kết luận phân loại.

## 3. Thiết kế pipeline đề xuất

```text
Allowlist source files + master/provenance + graph
  → schema adapters + validation + manifest/checksum
  → canonical source records + versioned retrieval views
  → BGE-M3 dense embeddings (+ sparse ở experiment)
  → PostgreSQL: source/chunks/embeddings/graph + exact/FTS indexes
  → intent/scope → exact lookup + lexical + dense → RRF
  → HS candidate ranking riêng + legal evidence expansion riêng
  → retrieval logs + benchmark + error analysis
```

### 3.1. Canonical contract

Tách **source record**, **retrieval view** và **embedding** để không sửa nguyên văn khi thêm context. Contract tối thiểu:

| Nhóm | Trường cần có |
|---|---|
| Identity | dataset_id, dataset_version, source_record_id, chunk_id, chunk_strategy_version |
| Nội dung | source_text, normalized_text, embedding_text, lexical_text, title, language |
| Retrieval | retrieval_role, layer, chunk_type, priority |
| HS | code_digits, code_display, level, chapter, heading, hs6, ahtn8, parent_id |
| Legal/source | document_no, source_file, source_locator, source_pages nullable, article/unit/rule/subrule |
| Provenance | content_hash, source_file_hash, source_chunk_ids, warnings, derived flag, original metadata JSONB |
| Version | effective_from/to nullable, validity_status, embedding_model, model_revision, tokenizer_revision |

IDs phải có namespace dataset và version; FK/graph chỉ liên kết cùng snapshot phù hợp. Mã lưu **TEXT**, giữ zero đầu; chuẩn hóa `8517.13.00` → `85171300`, chỉ chấp nhận pattern mã hợp lệ và tách khỏi các số đo sản phẩm.

Content hash nguồn và embedding-input hash là hai trường khác nhau. Cache key embedding = model/revision + tokenizer + normalization/chunk strategy + hash của input thực tế.

Null ngày hiệu lực nghĩa là chưa biết, không mặc định đang hiệu lực. Với query có `as_of_date`, chỉ dùng nguồn đủ thông tin hoặc trả cờ validity chưa xác minh; kết quả historical phải gắn đúng version. Metadata local được lưu cùng trạng thái xác minh, không tự nâng thành thẩm quyền pháp lý.

### 3.2. Chunking và BGE-M3

- TT31: baseline 1 record → 1 retrieval view, dùng nguyên `text` và `sparse_text` hiện có.
- GIR: source atomic giữ nguyên; experiment dùng context passages có mapping về source IDs.
- TT85: dùng nhãn điều/khoản/điểm và parent lead-in; form chunks là extension riêng.
- Scope: 1 chapter → 1 scope view; không đưa vào bảng xếp hạng AHTN8.
- Đo token bằng tokenizer của BGE-M3. Mục tiêu passage ban đầu 256–512 tokens; mở tối đa 1.024 khi ngữ cảnh yêu cầu. Đây là cấu hình thử nghiệm, không phải kết quả tối ưu đã đo.
- Không cắt mù mọi record theo 512 tokens; chia theo đơn vị ngữ nghĩa khi vượt budget, giữ parent/source IDs; fail/report nếu input bị truncate ngoài dự kiến.

BGE-M3 có dense 1.024 chiều, hỗ trợ dense/sparse/multi-vector và context tối đa 8.192 tokens; query không cần instruction prefix của BGE cũ. Giai đoạn đầu `return_dense=True`, `return_colbert_vecs=False`. Dùng FlagEmbedding để có thể bật sparse cùng model sau này. [Model card BAAI](https://huggingface.co/BAAI/bge-m3), [BGE docs](https://bge-model.com/bge/bge_m3.html).

Máy khảo sát là ARM64, 24 GiB RAM. Pilot CPU FP32 batch 4–8 trên 32–64 passages, ghi thời gian/RAM và giảm batch khi cần; MPS chỉ bật sau khi xác nhận library/device hỗ trợ và kết quả hợp lệ. CUDA/Colab là lựa chọn nếu pilot quá chậm. Không giả định có CUDA trên máy Mac hay FP16 luôn tốt trên CPU.

Validate vector shape `(N,1024)`, finite values, norm gần 1 (normalize nếu cần), thứ tự IDs đúng và query/doc cùng model revision. Lưu checkpoint theo batch để resume. 3.733 dense float32 vectors chiếm khoảng 14,6 MiB dữ liệu vector thuần; không bao gồm model, activations, text, PostgreSQL overhead hoặc HNSW.

### 3.3. PostgreSQL/pgvector

Tạo Compose riêng `apps/aiAgent/docker-compose.rag.yml`, database/volume riêng. Không thay DB MariaDB của ERPNext. Chọn PostgreSQL 17 + pgvector >=0.8 làm baseline tương thích; pin image tag/digest và library versions sau smoke test. Secret qua environment, `.env.example` chỉ có placeholder. Notebook chọn explicit target database trước khi ingest.

Schema đề xuất:

- `rag.datasets`: manifest, source hashes, dataset version và trạng thái snapshot.
- `rag.source_records`: nguyên văn, normalized text, source locator, provenance và metadata JSONB.
- `rag.chunks`: retrieval view, source membership, role, các cột HS/intent/validity và embedding input hash.
- `rag.embeddings`: chunk FK + model revision/profile + `embedding vector(1024)`.
- `rag.graph_nodes`, `rag.graph_edges`: structural/source nodes, typed edges và FK kiểm endpoint.
- `rag.ingestion_runs`: counts, started/finished/status, lỗi và active snapshot.
- `rag.evaluation_runs`, `rag.retrieval_results`: config snapshot, query variant, rank, score thành phần, latency và evidence IDs.

Index: B-tree cho dataset/version/code/chapter/heading/role; GIN cho `tsvector`; HNSW `vector_cosine_ops` cho profile được dùng. Khi có nhiều model revisions, tách partition/profile hoặc partial index phù hợp để không search trộn embedding spaces.

Corpus nhỏ: chạy **exact dense search** trước làm ground truth và benchmark latency. Thêm HNSW khi có lợi; điểm khởi đầu m=16, ef_construction=64, ef_search=100, đo lại với filtered queries. ANN + filter có thể thiếu kết quả: cân nhắc iterative scan (pgvector >=0.8), tăng ef_search hoặc exact fallback. Query dùng `ORDER BY embedding <=> query_vector LIMIT n` để index có thể phục vụ. [pgvector docs](https://github.com/pgvector/pgvector).

Load qua staging + transaction/upsert; cùng snapshot tái chạy không tăng rows. Snapshot mới chỉ chuyển active sau khi source/embedding/graph đủ và validation pass. Record biến mất phải được loại khỏi snapshot active, không để upsert tích lũy dữ liệu cũ. Giữ snapshot cũ cho rollback và evaluation reproducibility.

### 3.4. Hybrid retrieval và evidence

**Baseline A: exact + PostgreSQL FTS + BGE-M3 dense + RRF.** PostgreSQL `ts_rank_cd` là ranking full-text, không gọi là BM25. Lexical dùng cấu hình `simple`, giữ search field có dấu và field bỏ dấu qua `unaccent`; query dùng cùng normalization. Benchmark VI có dấu/không dấu, acronym và English technical names. FTS theo lexeme chưa phải tách từ tiếng Việt hoàn chỉnh. [PostgreSQL FTS](https://www.postgresql.org/docs/17/textsearch.html), [unaccent](https://www.postgresql.org/docs/17/unaccent.html).

Flow sản phẩm:

1. Nhận **chỉ** tên và mô tả sản phẩm; trích explicit code nếu người dùng thực sự nhập mã. Không dùng expected/chapter/heading từ gold làm input.
2. Router đưa intent + scope gợi ý. Baseline HS search cả 84/85; router branch là một ablation riêng.
3. Nếu tra cứu mã explicit: lookup chính xác, giữ kết quả trực tiếp; thêm ancestors/notes. Không ép top code đó vào truy vấn kiểm tra mô tả trái mã.
4. Truy vấn phân loại: lấy top 50 lexical và top 50 dense trên tariff views; nếu chạy hierarchical mode thì lấy heading candidates rồi các descendants, có global fallback để tránh khóa sai heading.
5. Fusion trên unique candidate ID: `RRF(d) = Σ w_branch / (60 + rank_branch(d))`, rank bắt đầu từ 1, branch không có document đóng góp 0. Khởi đầu weights bằng nhau; tune trên dev.
6. Trả top 10 AHTN8 **duy nhất theo mã**; không để notes/context/scope chiếm slots hay dùng heading như một lần hit AHTN8. Lưu intermediate tariff ranking để biết mất gold ở đâu.
7. Evidence expansion từ candidate/ancestors: giữ các section notes áp dụng toàn cục, chapter/subheading notes, constraints, context và source footnotes; quản lý hướng cạnh đúng theo export. Ưu tiên normalized references đã được đánh dấu, giữ trace.
8. Giới hạn 1–2 hops, visited set, số evidence và token budget; không expand tất cả descendants của chapter. Evidence bắt buộc theo scope/constraint tách khỏi optional semantic evidence để không bị fusion làm mất.

Flow pháp lý: GIR intent search rules/explanatory; TT85 intent search articles/forms. Với truy vấn hỗn hợp, trả riêng `candidates` và `evidence`. TT85 procedures không trở thành tariff candidates. Retrieval metadata P0/P1 không thay thế kiểm relevance, graph relation cũng không tự chứng minh đủ điều kiện phân loại.

**Experiment B: BGE-M3 dense + sparse**, và tùy chọn thêm FTS/exact:

- Generate `lexical_weights` với `return_sparse=True`; dùng cùng tokenizer revision cho query/doc.
- Lưu postings `(profile_id, chunk_id, token_id, weight)` trong PostgreSQL, index `(profile_id, token_id)`; score exact sparse = tổng `query_weight × doc_weight` trên token giao nhau, GROUP BY chunk rồi top-k. Đây là baseline learned sparse thực sự; JSONB đơn thuần chỉ lưu được dữ liệu, chưa tạo sparse search.
- Đo số postings, thời gian và RAM trước khi quyết định pruning/index mở rộng. Nếu dùng pgvector sparsevec, kiểm giới hạn số nonzero index, vocabulary dimension và mapping token ID từ zero-based sang one-based; không mặc định mọi passage phù hợp HNSW sparse index.
- So sánh learned sparse độc lập và fusion với dense. Nếu cần BM25, triển khai một backend/extension BM25 được chọn và đo riêng; không gán nhãn BM25 cho FTS hay learned sparse.

Reranker cross-encoder là experiment sau baseline: chỉ bật nếu tăng chất lượng đủ so với latency; giữ kết quả trước/sau. ColBERT multi-vector chưa cần trong MVP.

## 4. Workflow Jupyter Notebook

Ưu tiên notebooks là deliverable chính. Giai đoạn nghiên cứu có thể làm toàn bộ trong notebook; khi tích hợp FastAPI, chuyển các hàm dùng chung sang module nhỏ để notebook/API chạy cùng logic. Không cần viết một ứng dụng Python đầy đủ trước khi có benchmark.

```text
apps/aiAgent/
├── notebooks/
│   ├── 01_build_knowledge_base.ipynb  # audit, context, embeddings, DB
│   └── 02_test_retrieval.ipynb        # suites, dev tuning, final evaluation
├── config/rag.yaml
├── sql/001_rag_schema.sql
├── docker-compose.rag.yml
├── requirements-rag.txt
├── .env.example
├── artifacts/                  # manifests, checkpoint embeddings, per-query runs
└── tests/                      # results displayed in notebook 02
```

Mỗi notebook: mục tiêu → config → input manifest → xử lý → assertions → artifact output → tóm tắt. Cell đầu resolve project root rõ ràng, không phụ thuộc working directory của kernel. Notebook sau đọc artifacts/notebook manifest trước, không phụ thuộc biến của một kernel khác.

Dependencies dự kiến: Python 3.11 environment riêng, jupyterlab, ipykernel, pandas, numpy, jsonschema hoặc pydantic, FlagEmbedding, torch/transformers, psycopg, pgvector, python-dotenv, PyYAML, nbconvert. Pin bộ versions đã chạy smoke thành công; tránh dùng bench env cho model packages.

Không hardcode database password hoặc lưu DSN trong cell outputs. Clear secrets/large outputs trước commit; embeddings/artifacts lớn có cache path và gitignore. Ingest cell có run mode `dry_run`/`apply`; chạy lại kernel không reset DB bằng DROP/TRUNCATE. Notebook headless phải restart-and-run-all được qua nbconvert trên cấu hình explicit; failure cell dừng pipeline.

## 5. Plan triển khai theo thứ tự phụ thuộc

| Bước | Việc thực hiện | Notebook / artifact | Điều kiện hoàn tất |
|---|---|---|---|
| 1 | Audit allowlist, schema, ID/text, hashes, graph và gold-code coverage; xác minh provenance TT85 và nguồn label còn lệch | `00_data_audit.ipynb`, `data_audit.json` | Counts khớp; không có dangling IDs; mọi gap có status rõ |
| 2 | Tạo adapters TT31/GIR/TT85/scope, canonical contract và context views; giữ source riêng | `01_canonical_ingestion.ipynb`, canonical JSONL + manifest | Join đầy đủ, IDs deterministic; source không bị thay wording; chưa ingest test |
| 3 | Tạo rag environment/config, pilot BGE-M3 rồi embed dense có checkpoint; sparse trong experiment profile | `02_bge_m3_embeddings.ipynb`, vector arrays + ID mapping | 1024 dimensions, finite/norm đạt; không truncation im lặng; resume đúng |
| 4 | Tạo PostgreSQL service riêng, migrations, staging import nguồn/chunks/vectors/graph, exact + GIN; thêm HNSW có baseline exact | `03_postgres_pgvector.ipynb`, SQL, Compose | Counts/FKs đúng; rerun không duplicate; active snapshot atomic; code variants lookup đúng |
| 5 | Exact lookup, lexical normalization, dense, RRF, intent/scope và tách candidate/evidence; graph expansion có budget | `04_hybrid_retrieval.ipynb`, retrieval trace | Product không nhận gold metadata; mỗi hit có provenance; notes không chiếm AHTN slots |
| 6 | Tạo eval query variants, grouped dev/test manifest và gold evidence suite riêng | Eval manifests, reviewed qrels | Expected code không vào query; labels/version frozen; evidence labels được review |
| 7 | Chạy ablation trên dev, phân tích lỗi, chọn cấu hình; sparse/reranker chỉ thêm nếu đo được lợi ích | Dev run logs + selected config | Config được khóa trước final test; ghi cả quality/latency/cost |
| 8 — Verification cuối | Restart/run-all notebooks và chạy final held-out retrieval test; kiểm idempotency/snapshot/citations và xuất báo cáo | `05_retrieval_evaluation.ipynb`, report + per-query JSONL | Gates ở mục 6 đạt hoặc nêu rõ failures; mọi kết quả truy vết được |

Critical path: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8. Có thể chuẩn bị hạ tầng và gold evidence khi chốt contract, nhưng không đưa kết quả test vào bước tạo corpus.

## 6. Retrieval Test và tiêu chí nghiệm thu

### 6.1. Hai lớp test

**A. Candidate benchmark 50 cases hiện có:**

- Query variant `name_only`: product_name_vi.
- Query variant `name_and_spec`: product_name_vi + technical_description_for_test; báo cáo riêng vì độ khó khác nhau.
- Bổ sung paraphrase, không dấu, acronym/English và thông số thiếu như challenge suite riêng, có review; không coi variant cùng case là samples độc lập.
- Gold = expected_hs_8 → TT31 record ID. Chapter/heading/ground_truth_condition dùng đánh giá/annotation, không đưa vào input retriever.
- Giữ 50 cases nguyên bản. Tạo split dev/test khoảng 60/40 theo **expected code group**, cân bằng chapter/nhóm sản phẩm khi có thể; ghi IDs cụ thể và seed. Không hứa chính xác 30/20 nếu grouped split không cho phép.
- Nếu đã tune trên toàn bộ 50, báo cáo đó là development benchmark và cần bộ holdout mới. Không gọi lại cùng bộ là test độc lập.

**B. Evidence và robustness suite bổ sung:**

- GIR: quy tắc và explanatory chunk liên quan, gồm các short/context-dependent examples.
- TT85: điều/khoản/điểm, thời điểm hiệu lực, hồ sơ và mẫu biểu.
- TT31: đúng note/constraint/ancestor, khác biệt giữa source wording và operational corrections.
- Scope: ví dụ ngoài 84/85, thông tin mơ hồ, mã không tồn tại, mã ngoài scope, explicit code trái mô tả.
- Missing information: đề xuất ứng viên và đánh dấu cần bổ sung; chưa tuyên bố đo classifier abstention nếu classifier chưa xây.
- Qrels gắn relevant source IDs + graded relevance (nếu có) được review độc lập. Các counts suite được chốt sau annotation, không lấy mã HS làm nhãn thay cho evidence.

### 6.2. Metrics

- Gold-code Hit@1/3/5/10; với một gold code đây cũng là code Recall@k nhị phân theo query.
- MRR@10 trên danh sách AHTN8 deduplicated; macro theo case và macro theo code để giảm ảnh hưởng 45 unique codes/50 cases.
- Heading/HS6 coverage báo cáo riêng; không dùng thay thế hit đúng AHTN8.
- nDCG@k chỉ dùng khi có qrels phù hợp; một gold code chỉ cho tín hiệu nhị phân hạn chế.
- Evidence Recall@k và citation locator completeness trên suite có gold evidence, trước/sau graph expansion; budget cố định giữa các configs.
- Router accuracy và UNCERTAIN rate trên scope suite; recall trước/sau router để thấy tổn thất.
- HNSW overlap/recall đối với exact dense top-k dưới cùng filter; tách khỏi gold-code relevance.
- Latency p50/p95: query embedding, DB lexical/dense, fusion, expansion và end-to-end retrieval; tách cold model-load với warm runs. Ghi hardware, batch, token length, corpus/profile/config.

### 6.3. Ablation tối thiểu

| Cấu hình | Mục đích |
|---|---|
| FTS only | Baseline exact terms/wording |
| Dense exact only | Baseline semantic và reference cho ANN |
| Dense + FTS + RRF | Hybrid MVP |
| Hybrid + scope/hierarchical routing | Đo router giúp hay làm mất gold |
| Hybrid + graph expansion | Đo evidence coverage, không kỳ vọng graph tự tăng code ranking |
| Dense + BGE sparse (+ FTS nếu có) | Đo learned sparse, tách chi phí và chất lượng |
| Hybrid + optional reranker | Đo thêm ranking quality/latency khi cần |

Exact-code tests chạy riêng vì bộ 50 không cung cấp mã trong query. Mỗi configuration chạy cùng query split, snapshot, k và budget. Không so các run có khác corpus mà bỏ qua chunk strategy version.

### 6.4. Gates đề xuất — chưa phải kết quả đã đạt

**Gates dữ liệu bắt buộc:** ID uniqueness, không text rỗng, vector hợp lệ, FK/graph integrity 100%; 50/50 gold codes join được; nguồn/citation locator đầy đủ theo loại tài liệu; rerun same snapshot không tăng counts; data/test không xuất hiện trong ingestion manifest.

**Gates chất lượng mục tiêu:** name+spec code Hit@10 ≥90%, Hit@5 ≥80% trên holdout đã khóa; báo cáo số case thực tế và khoảng bất định vì mẫu nhỏ. Name-only báo cáo riêng để thiết lập baseline; chưa áp cùng ngưỡng. Hybrid được chọn phải có lợi ích rõ so với baseline tốt nhất trên dev mà không gây regression nghiêm trọng theo nhóm; không mặc định hybrid sẽ thắng.

**Gates hiệu năng:** đặt warm end-to-end SLO sau pilot query embedding trên máy đích; initial HNSW top-10 recall so với exact ≥95% nếu quyết định dùng ANN. Không đặt p95 cứng khi chưa đo hardware/runtime. Corpus nhỏ có thể dùng exact nếu latency đạt.

**Báo cáo cuối:** bảng metrics theo config/variant/split; per-query ranks và scores; errors như near-sibling code, “Loại khác”, mất ancestor, router khóa sai chương, lexical mất synonym, thiếu legal note; quyết định giữ/sửa config và residual gaps. Không chuyển điểm similarity thành xác suất đúng mã HS.

## 7. Quyết định triển khai khuyến nghị

1. Dùng Jupyter Notebook cho toàn bộ workflow nghiên cứu/ingestion/evaluation, SQL migrations và Compose là các file hỗ trợ cần thiết.
2. Dùng TT31 ingest + master join, GIR combined và TT85 source chunks; scope/router và graph lưu riêng.
3. Triển khai dense exact + FTS + exact-code + RRF trước; graph bổ sung evidence ngay trong MVP vì dữ liệu đã có.
4. Thử BGE-M3 sparse như experiment PostgreSQL postings sau khi baseline đo được; không cần ColBERT hoặc framework RAG lớn ở bước đầu.
5. Chốt retrieval quality và traceability trước khi đưa logic vào FastAPI/ERPNext hoặc xây luồng kết luận HS.


## Điều chỉnh triển khai theo yêu cầu — 2026-09-26

Workflow thực tế được gộp thành hai notebook nêu ở mục 4; bảng các bước mục 5 là thứ tự logic, không còn là sáu file notebook riêng. Mọi data audit, benchmark, qrels, robustness cases, graph traces và quality checks hiển thị/lưu trong output notebook. Các reports rời từ baseline được loại bỏ; modules Python dùng chung được giữ để tránh duplicate và phục vụ runtime.

GIR short records đã có joins được đối chiếu source; TT85 có khoản/điểm/subpoint context và 5 forms title/fields. Corpus 3.738 records đã embed dense+sparse, ingest vào PostgreSQL và kiểm idempotency/rollback. Notebook 02 có 20 legal cases, 16 routing/robustness cases và 12 challenge queries được khóa trước dev selection; đã chạy dev fusion grid và final evaluation.

Legal/challenge labels được đối chiếu corpus local, không gọi là independent expert review. Bộ test cũ được ghi là reproduction. Exact cosine được giữ cho corpus nhỏ; ANN/reranker là lựa chọn khi có nhu cầu đo được, không là gate bắt buộc. Xem output notebook để biết metrics thực tế, failures và coverage giới hạn.
