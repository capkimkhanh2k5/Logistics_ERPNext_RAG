# RAG — Knowledge Base, HS và QA

| Notebook | Workflow |
|---|---|
| `notebooks/01_build_knowledge_base.ipynb` | Audit XIV/XVI/XVII → namespaces / GIR / TT85 clauses → BGE-M3 dense+sparse → PostgreSQL → integrity/idempotency |
| `notebooks/02_test_retrieval.ipynb` | HS train 709 / test 143 / holdout 88 → C1–C15 / weight sweep → soft Top-2 Sections / parent graph / reranker → Top-K benchmark |
| `notebooks/03_qa_retrieval_experiment.ipynb` | Train 320 / test 150 QA → so sánh graph trước/sau reranker và truy vấn bỏ mã nghi vấn → chọn cấu hình QA / kiểm tra runtime |

Outputs được giữ ngay trong các notebook. Không tạo report rời. Các module `rag/` giữ logic dùng chung để notebook và runtime dùng cùng implementation.

## Mở và chạy

Trong `frappe-bench/apps/aiAgent`:

```bash
.venv/bin/jupyter lab notebooks
```

Chọn kernel **Python (AI Agent RAG)**. Chạy notebook 01 trước. Trong notebook 02, chọn các cell từ mục **New verified HS partitions — active snapshot** đến cuối và dùng *Run Selected Cells*; phần phía trên giữ output thí nghiệm lịch sử. Để kiểm tra QA với cấu hình đã khóa, trong notebook 03 chạy hai cell setup đầu tiên rồi cell cuối ở mục **QA regression on the new active Knowledge Base snapshot**. Notebook 02/03 đọc corpus/model profile active từ artifacts/database, không cần giữ kernel notebook 01.

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
- `config/`: model/retrieval settings và selected runtime config.
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

`routed_search` nhận diện intent; product dùng cross-Section retrieval → Top-2 Sections → ứng viên HS8 từ nhiều kênh → chính sách rerank theo Phần. Notes/GIR và graph được trả kèm ứng viên; riêng XIV, Cross-Encoder có thể đọc ngữ cảnh định nghĩa đã nối nguồn. Kết quả có `validation_status=REQUIRES_GIR_EXCLUSION_REASONING`; chưa phải kết luận HS. Không hard-filter Chapter 84/85 quá sớm.

## Metadata và retrieval

Cùng PostgreSQL/pgvector, hai namespaces `hs_classification` và `legal_classification`. Dataset vẫn là `tt31`, `gir`, `tt85`, `scope`. Metadata gồm namespace/dataset/chunk_type/role, section/chapter/heading/hs6/ahtn8, source/effective_from/effective_to/legal_status. Legal status chỉ phản ánh metadata nguồn, không là xác minh pháp lý độc lập.

Bảy chunk types: gir_rule, gir_explanation, section_note, chapter_note, subheading_note, tariff_entry, legal_clause. Structural/context/source-footnote records có chunk_type null khi không thuộc bảy loại này; subtype nguồn được giữ nguyên. 5 mẫu TT85 giữ trong source template registry, không có vectors. Tạo Word chưa triển khai.

Các retrievers: dense BGE-M3, learned sparse token postings, Okapi BM25 từ `rank-bm25==0.2.2`/`BM25Okapi` (`k1=1.2,b=0.75,epsilon=0.25`, index trong RAM từ active PostgreSQL snapshot), FTS `simple+unaccent/ts_rank_cd`, Exact mã/thuộc tính kỹ thuật. BM25 không được thay bằng FTS/sparse. Weighted RRF kết hợp rank, k=5/10/20/40/60/100/200. Trọng số chuẩn hóa về 1 là quy ước benchmark; toán học RRF không yêu cầu tổng bằng 1.

C11 cross-encoder BGE reranker v2-m3 pin revision; C12 BGE-M3 `colbert_score()` từ FlagEmbedding rerank top30 sau dense+sparse. Các scores reranker không cộng vào RRF. MPS dùng cho cross-encoder nếu có; BGE embedding/ColBERT giữ CPU FP32. Cache branches và reranking là artifacts phục vụ resume, không phải report.

Graph chứa hierarchy, notes, cross references của XIV/XVI/XVII; các external stubs có mã trong corpus được nối bằng RESOLVES_TO. Unknown external references vẫn là stubs, không biến thành căn cứ đầy đủ. Expansion có budget/omitted/missing-required IDs; Notes coverage không thay thế GIR/exclusion reasoning.

## Benchmark

Dùng `data/verified/hs/train/HS_RAG_TRAIN.jsonl` (709 sản phẩm), `test/HS_RAG_TEST.jsonl` (143) và `holdout/HS_RAG_HOLDOUT.jsonl` (88). Train/test không trùng sản phẩm hoặc `case_family_id`; có 22 mã HS xuất hiện ở cả train và test. Train có phần tune/validation tách theo `case_family_id` để chọn trọng số. Test và holdout hiện là các tập **hồi quy** vì đã được xem trên snapshot trước; muốn xác nhận khách quan policy mới cần holdout chưa sử dụng. Không fine-tune BGE và không ingest gold. Query được dựng từ tên/mô tả kỹ thuật, không dùng nhãn hoặc câu trả lời.

C1–C15, nhiều bộ trọng số và RRF k được quét trên TRAIN; chính sách cũ cũng là một candidate. Tập validation nội bộ chọn cấu hình cho từng Phần và router. Sau đó notebook thử nhánh tài liệu cha theo `CONTAINS`, định nghĩa Notes và Cross-Encoder trên cùng ngân sách ứng viên. Không dùng nhãn test/holdout để chọn. Ngữ cảnh bổ sung tại thời điểm truy xuất luôn giữ bản ghi và locator riêng, không ghi ngược vào corpus nguồn.

Chính sách HS của snapshot nguồn thuần `e06d50069151e5b0ecae0450`: XIV C9 Dense .35 / BM25 .35 / Exact .30; XVI C6 Dense .145 / BM25 .855; XVII C13 thiên về BM25 .685 và Sparse .315. Cả ba dùng Cross-Encoder pool30; XIV/XVII còn thử nhánh tài liệu cha với trọng số .2. Router dùng Dense .70 / Sparse .10 / BM25 .10 / FTS .05 / Exact .05, RRF k60 và giữ Top-2 Sections. Tỷ lệ đầy đủ trong `config/selected_retrieval.json`; đây là lựa chọn từ TRAIN của corpus mới, chưa được xác nhận trên holdout mới.

| Phần | Test Hit@1 / HS8 Recall@5 | Holdout Hit@1 / HS8 Recall@5 |
|---|---:|---:|
| XIV | 20.8% / 35.4% | 17.2% / 48.3% |
| XVI | 59.6% / 91.5% | 34.5% / 58.6% |
| XVII | 27.1% / 75.0% | 26.7% / 46.7% |

Đây là **Top-K retrieval**, không phải độ chính xác kết luận mã HS. Holdout Top-2 Section Recall vẫn là 87/88, nhưng HS8 Recall@5 giảm mạnh sau khi bỏ văn bản cha/Chú giải đã từng được nối vào từng dòng. Điều này cho thấy nguồn ngữ cảnh có ích cho tìm kiếm, đồng thời xác nhận cần đặt nó ở một kênh truy xuất riêng có citation thay vì trộn vào bản ghi nguồn. Bảng từng câu, MRR/nDCG và độ trễ của cả hai snapshot được giữ trong output notebook 02. Exclusion Violation Rate là N/A vì bộ sản phẩm không có `forbidden_codes` gắn nhãn.

GIR Rule Engine, Critic, LLM generation, Agent2/FastAPI/ERP integration thuộc giai đoạn tiếp theo.

Adapters dùng tên `tt31_section_xiv`, `tt31_section_xvi`, `tt31_section_xvii`; metadata `dataset=tt31` là nguồn thông tư chung, `section` xác định Phần. Không sử dụng tên `tt31` để chỉ riêng adapter XVI. Các HS6 không có dòng nguồn riêng được bổ sung graph-only nodes từ prefix AHTN8, có virtual=true/legal_text_available=false; không tạo nội dung pháp lý hoặc embedding giả.

### Ngữ cảnh định nghĩa và quan hệ cha

`definition_candidates` chỉ đi theo cạnh định nghĩa dương; không biến cạnh loại trừ thành đề xuất HS. `parent_candidates` chỉ duyệt các cạnh `CONTAINS` đến bản ghi thật có nguồn và locator. Các nhánh được thử trên TRAIN; chính sách hiện chọn trọng số parent .2 cho XIV/XVII, 0 cho XVI, còn nhánh definition candidate có trọng số 0. XIV/XVII dùng `definition_context` khi rerank, lấy văn bản từ bản ghi Note độc lập có citation. Không bước nào ghi các đoạn đó vào `source_text` hoặc search text của dòng biểu thuế.

## Dữ liệu chuẩn hóa và hồ sơ hỗ trợ

Trong mỗi `data/normalized/TT31/Section-XIV`, `Section-XVI`, `Section-XVII`, các file mà `rag.data.SOURCES` đọc giữ nguyên tên và vị trí. Các bản xuất phụ, checksum, manifest, báo cáo, audit và nhật ký sửa nguồn nằm trong `supporting/`. Nội dung của hồ sơ lịch sử giữ nguyên; đường dẫn tương đối trong checksum/manifest cũ được hiểu theo cấu trúc gói nguồn trước khi di chuyển. Hash của các đầu vào hiện tại được kiểm chứng trực tiếp trong notebook và QA preflight; checksum lịch sử không được coi là hash snapshot active.

XVII có `SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl`; adapter chuyển các cạnh về schema chung. Node của XVII được lấy từ master, XIV từ GRAPH_NODES, XVI từ master và GRAPH_STRUCTURAL_NODES. Đây là khác biệt định dạng xuất dữ liệu, cùng một graph runtime trong PostgreSQL.

### Sửa đầu vào đã đối chiếu nguồn — 2026-09-29

Notebook 01 đối chiếu và sửa lỗi OCR với PDF nguồn. Các trường embedding/BM25/FTS của XIV/XVI/XVII hiện chỉ dùng mã và văn bản tiếng Việt của **chính bản ghi** đã chuẩn hóa; không nối mô tả của cha hoặc Chú giải vào văn bản ingest. Riêng 85.34, Chú giải 8 là một bản ghi độc lập với ID và locator riêng. Năm dòng XVI bị OCR trộn hai cột ngôn ngữ được sửa theo cột tiếng Việt. Cột tiếng Anh và bản trích xuất thô vẫn giữ để kiểm toán. ID, mã HS và graph giữ nguyên. Mọi kết quả benchmark của snapshot trước khi sửa corpus chỉ có giá trị lịch sử.

Phần XVII bổ sung sửa OCR `0 tô` → `Ô tô` trong 173 mô tả Chương 87 sau khi kiểm tra mẫu trên ảnh PDF; bản trích xuất thô vẫn được giữ. HS6 và Heading cha là các bản ghi riêng có locator; quan hệ cha được giữ bằng cạnh `CONTAINS` trong graph. Nhánh tìm tài liệu cha trong notebook 02 chỉ duyệt các cạnh này.

## QA: 320 train / 150 test

`data/verified/qa/train/LEGAL_RETRIEVAL_TRAIN.jsonl` chứa 320 câu, `data/verified/qa/test/LEGAL_RETRIEVAL_TEST.jsonl` chứa 150 câu, và `all/LEGAL_RETRIEVAL_MASTER.jsonl` là union để kiểm tra. Adapter dùng `record_mapping` hoặc `source_locations` để ánh xạ alias export về chunk nguồn thật; kiểm tra ID, câu hỏi, case family và nguồn. Gold không được ingest, không fine-tune model và không dùng nhãn test để chọn chính sách.

Notebook 03 thử các họ retriever/trọng số trên QA train, sau đó so sánh đường trực tiếp với đường thêm tài liệu cha và Notes thật trước Cross-Encoder. Thử pool 30/50/100, phần ứng viên trực tiếp được giữ, và nhánh truy vấn bỏ mã đang bị nghi vấn. Chọn policy trên train và ghi khóa `qa` trong `config/selected_retrieval.json`; giữ nguyên chính sách HS. Top-10 được chấm theo ID chunk primary chính xác; gói căn cứ được chấm riêng. 50 test cũ từng được dùng để chẩn đoán nên báo riêng với 100 test mới. Kết quả là đánh giá retrieval trên bộ dữ liệu đã cung cấp, chưa phải chứng minh chất lượng kết luận pháp lý cuối cùng.

Trên snapshot nguồn thuần `e06d50069151e5b0ecae0450`, TRAIN chọn QA `graph_50_70`: Dense .25 / Sparse .05 / BM25 .20 / Exact .50, RRF k20, graph trước reranker với 70% chỗ cho ứng viên trực tiếp và rerank pool50. Notebook 03 đã chạy hồi quy đủ 150 câu: **86,0%** có đủ căn cứ bắt buộc trực tiếp trong Top-10; **89,3%** có đủ trong gói căn cứ mở rộng. Snapshot trước đạt 80,7% trực tiếp và 94,0% trong gói, nên thay đổi corpus cải thiện một chỉ số nhưng làm giảm chỉ số kia. Nhóm `cross_section_exclusion` chỉ có 2 câu và còn yếu (0/2 trực tiếp, 1/2 trong gói). Đây vẫn là retrieval, chưa kiểm chứng suy luận pháp lý; test QA đã được xem trên snapshot trước và là tập hồi quy.

`Retriever.qa_search(query)` hoặc `knowledge_search(query)` khi đã có chính sách QA dùng corpus chung với các chunk type GIR, Notes, TT85, tariff entry ở nhiều tầng. Không cố định role/level, không hard-filter Section. Query gốc đi vào semantic/lexical retrieval; Exact che các mã được nhắc để nghi vấn/phủ định. Nhánh truy vấn bổ sung dùng câu đã bỏ mã nghi vấn để tìm hàng hóa, và chỉ hoạt động nếu chọn trên train. Gói bổ sung có graph evidence, các tài liệu cha thật, Notes của các nhánh/mã được nhắc và các rule cùng họ GIR đã tìm được; việc lấy đủ tài liệu không thay thế suy luận pháp lý.

`knowledge_search(policy="hs_transfer")` tái lập thí nghiệm chuyển chính sách HS vào các kênh HS4/HS6/AHTN8; `policy="legacy_fixed"` tái lập baseline đa tầng cũ. `routed_search` chuyển câu hỏi GIR/Notes/thủ tục sang chính sách QA khi đã có; nhánh sản phẩm vẫn dùng `adaptive_search` và chính sách HS hiện có. Các cơ chế che mã nghi vấn và mở rộng căn cứ QA không được tự động áp vào xếp hạng ứng viên sản phẩm.
