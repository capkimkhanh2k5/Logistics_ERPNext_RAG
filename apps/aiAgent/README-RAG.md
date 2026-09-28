# RAG — Knowledge Base, HS và QA

| Notebook | Workflow |
|---|---|
| `notebooks/01_build_knowledge_base.ipynb` | Audit XIV/XVI/XVII → namespaces / GIR / TT85 clauses → BGE-M3 dense+sparse → PostgreSQL → integrity/idempotency |
| `notebooks/02_test_retrieval.ipynb` | Train 300 / test 90 → C1–C15 / weight sweep → soft Top-2 Sections / hierarchy → legal → held-out benchmark → latency / checks |
| `notebooks/03_qa_retrieval_experiment.ipynb` | Train 320 / test 150 QA → so sánh graph trước/sau reranker và truy vấn bỏ mã nghi vấn → chọn cấu hình QA / kiểm tra runtime |

Outputs được giữ ngay trong các notebook. Không tạo report rời. Các module `rag/` giữ logic dùng chung để notebook và runtime dùng cùng implementation.

## Mở và chạy

Trong `frappe-bench/apps/aiAgent`:

```bash
.venv/bin/jupyter lab notebooks
```

Chọn kernel **Python (AI Agent RAG)**. Chạy notebook 01 trước, rồi notebook 02 (HS), cuối cùng notebook 03 (QA). Notebook 02/03 đọc corpus/model profile active từ artifacts/database, không cần giữ kernel notebook 01.

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

`routed_search` nhận diện intent; product dùng cross-Section retrieval → Top-2 Sections → direct/hierarchy candidate paths → trained reranking policy. Trước xếp hạng cuối, policy đã chọn trên train có thể bổ sung ứng viên qua các cạnh định nghĩa Notes → nhóm → mã con, rồi cho cross-encoder đọc ngữ cảnh định nghĩa. Notes/GIR và graph được trả kèm ứng viên. Kết quả có `validation_status=REQUIRES_GIR_EXCLUSION_REASONING`; chưa phải kết luận HS. Không hard-filter Chapter 84/85 hoặc chỉ AHTN8 trong bộ lọc chung.

## Metadata và retrieval

Cùng PostgreSQL/pgvector, hai namespaces `hs_classification` và `legal_classification`. Dataset vẫn là `tt31`, `gir`, `tt85`, `scope`. Metadata gồm namespace/dataset/chunk_type/role, section/chapter/heading/hs6/ahtn8, source/effective_from/effective_to/legal_status. Legal status chỉ phản ánh metadata nguồn, không là xác minh pháp lý độc lập.

Bảy chunk types: gir_rule, gir_explanation, section_note, chapter_note, subheading_note, tariff_entry, legal_clause. Structural/context/source-footnote records có chunk_type null khi không thuộc bảy loại này; subtype nguồn được giữ nguyên. 5 mẫu TT85 giữ trong source template registry, không có vectors. Tạo Word chưa triển khai.

Các retrievers: dense BGE-M3, learned sparse token postings, Okapi BM25 từ `rank-bm25==0.2.2`/`BM25Okapi` (`k1=1.2,b=0.75,epsilon=0.25`, index trong RAM từ active PostgreSQL snapshot), FTS `simple+unaccent/ts_rank_cd`, Exact mã/thuộc tính kỹ thuật. BM25 không được thay bằng FTS/sparse. Weighted RRF kết hợp rank, k=5/10/20/40/60/100/200. Trọng số chuẩn hóa về 1 là quy ước benchmark; toán học RRF không yêu cầu tổng bằng 1.

C11 cross-encoder BGE reranker v2-m3 pin revision; C12 BGE-M3 `colbert_score()` từ FlagEmbedding rerank top30 sau dense+sparse. Các scores reranker không cộng vào RRF. MPS dùng cho cross-encoder nếu có; BGE embedding/ColBERT giữ CPU FP32. Cache branches và reranking là artifacts phục vụ resume, không phải report.

Graph chứa hierarchy, notes, cross references của XIV/XVI/XVII; các external stubs có mã trong corpus được nối bằng RESOLVES_TO. Unknown external references vẫn là stubs, không biến thành căn cứ đầy đủ. Expansion có budget/omitted/missing-required IDs; Notes coverage không thay thế GIR/exclusion reasoning.

## Benchmark

Dùng `data/verified/hs/train/HS_RAG_TRAIN_300_VERIFIED.jsonl` (100 sản phẩm mỗi Phần) và `data/verified/hs/test/HS_RAG_TEST_90_DISJOINT_VERIFIED.jsonl` (30 mỗi Phần). Không tự chia lại; bỏ qua bản CSV và thư mục all/. Không trùng sản phẩm, có 8 mã HS trùng giữa train/test. Mỗi sản phẩm có hai query variants name_only và name_and_spec. Train chỉ chọn cấu hình retrieval, không fine-tune BGE và không ingest gold. Query không sử dụng nhãn, ground_truth_condition, mô tả đáp án; chỉ dẫn Case test và tham chiếu mã HS/Chapter trong mô tả được loại và đối chiếu ở notebook.

C1–C10 và C13–C15 khảo sát simplex bước .05 cùng 600 Dirichlet samples/family, k=5/10/20/40/60/100/200. C13 dense+sparse+BM25+Exact; C14 dense+sparse+BM25; C15 sparse+BM25+Exact. C11/C12 khảo sát nhiều base policies với Cross-Encoder/ColBERT. Mục tiêu chọn trên train: Hit@1 → Recall@5 → MRR → nDCG@10. Router/15 legal qrels có sweep riêng; pháp luật chưa có test độc lập.

Adaptive pipeline giữ Top-2 Sections, kết hợp ứng viên trực tiếp và graph hierarchy dựa trên tín hiệu mã con. Beam 5/10/20, branch pool 50/100, Section fusion equal/router, direct path weight .25/.5/.75. So sánh thêm rerank pool20/30/50 và rank blending .5/.75/1.0 với Cross-Encoder/ColBERT. Policy runtime chọn theo Section được router dự đoán; không dùng Section nhãn test. Pipeline strict cũ vẫn được giữ để đo pruning và so sánh trên cùng test. Nodes suy ra không mang nội dung luật giả.

Bảng test theo Section/query variant: Hit@1, Section Accuracy/Recall@2, Chapter/Heading/HS6/AHTN8 Recall@5, MRR, nDCG@10, per-case ranks/failures và trace hierarchy. Ancestor projection của leaf retrieval được ghi rõ, không gọi là kết quả traversal thật. Exclusion Violation Rate là N/A nếu không có forbidden-code qrels. Cache hỗ trợ resume; không xuất report riêng và không xóa output notebook.

GIR Rule Engine, Critic, LLM generation, Agent2/FastAPI/ERP integration thuộc giai đoạn tiếp theo.

Adapters dùng tên `tt31_section_xiv`, `tt31_section_xvi`, `tt31_section_xvii`; metadata `dataset=tt31` là nguồn thông tư chung, `section` xác định Phần. Không sử dụng tên `tt31` để chỉ riêng adapter XVI. Các HS6 không có dòng nguồn riêng được bổ sung graph-only nodes từ prefix AHTN8, có virtual=true/legal_text_available=false; không tạo nội dung pháp lý hoặc embedding giả.

### Cải thiện truy xuất theo định nghĩa

Notebook 02 giữ nguyên kết quả benchmark ban đầu và bổ sung các cell phân tích, chọn policy trên train, so sánh trước/sau và kiểm tra runtime. Nhánh `definition_candidates` dùng cùng BM25Okapi trên search views nối qua `DEFINES_FOR`/`DEFINITION_APPLIES_TO`/`INCLUDES_IN_SCOPE` và descendants `CONTAINS`. Không dùng cạnh loại trừ để tạo ứng viên. Placeholder Note 9(a) được giải tới đúng đoạn nguồn của Note 9, không sao chép cả Note 9(b) vào nhóm 7117. Mỗi view có citation và graph path; source_text và vectors gốc không đổi.

Sweep trọng số nhánh định nghĩa 0–1, RRF k và evidence-aware Cross-Encoder (pool10/20/30, rank blending .25/.5/.75/1). Chọn theo Section dự đoán, luôn so sánh với baseline gồm reranker hiện có. Trọng số 0 và evidence_rerank=false giữ đường truy xuất cũ. Gold không tham gia dựng index. TEST đã được xem để chẩn đoán nên các số sau cải thiện là diagnostic regression, cần test mới để xác nhận tổng quát hóa độc lập.

Đối với XIV, notebook so sánh thêm mục tiêu macro giữa hai nhóm nguồn trên TRAIN (dòng biểu thuế và ví dụ Notes), với điều kiện Hit@1 toàn TRAIN XIV không thấp hơn baseline. Policy hiện hành nằm trong `config/selected_retrieval.json`: XIV dùng definition_weight=0 và evidence-aware Cross-Encoder pool30/rank_weight=.25/k60; XVI dùng definition_weight=.5 và pool10/.75/k60; XVII giữ nhánh trực tiếp, không thêm definition branch. Policy áp dụng theo Section được router dự đoán. Kết quả test XIV chỉ cải thiện nhẹ; một số câu XVII vẫn bị ảnh hưởng khi router chọn chính sách XVI.

Router runtime lấy Top-2 Sections từ toàn bộ kết quả fusion trước khi cắt top_k. Notebook kiểm tra runtime parity trên các câu thuộc cả ba Phần và câu bị routing lệch; score RRF so sánh với sai số float nhỏ, thứ tự mã so sánh chính xác. Kết quả trước/sau và lỗi còn lại lưu ở output của notebook 02.

## Dữ liệu chuẩn hóa và hồ sơ hỗ trợ

Trong mỗi `data/normalized/TT31/Section-XIV`, `Section-XVI`, `Section-XVII`, các file mà `rag.data.SOURCES` đọc giữ nguyên tên và vị trí. Các bản xuất phụ, checksum, manifest, báo cáo, audit và nhật ký sửa nguồn nằm trong `supporting/`. Nội dung của hồ sơ lịch sử giữ nguyên; đường dẫn tương đối trong checksum/manifest cũ được hiểu theo cấu trúc gói nguồn trước khi di chuyển. Hash của các đầu vào hiện tại được kiểm chứng trực tiếp trong notebook và QA preflight; checksum lịch sử không được coi là hash snapshot active.

XVII có `SECTION_XVII_GRAPH_EDGES_NORMALIZED.jsonl`; adapter chuyển các cạnh về schema chung. Node của XVII được lấy từ master, XIV từ GRAPH_NODES, XVI từ master và GRAPH_STRUCTURAL_NODES. Đây là khác biệt định dạng xuất dữ liệu, cùng một graph runtime trong PostgreSQL.

### Sửa đầu vào đã đối chiếu nguồn — 2026-09-28

Notebook 01 có cell xác thực và sửa đầu vào theo PDF nguồn: 87.04 được khôi phục khoảng trắng; 85.06 chỉ giữ tên tiếng Việt trong văn bản tìm kiếm; 85.34 nối Chú giải 8 tiếng Việt với ID và locator. Năm dòng XVI bị OCR trộn hai cột ngôn ngữ được sửa theo cột tiếng Việt, kể cả các search views của dòng con. Các search views XIV/XVII được dựng từ trường tiếng Việt. Cột tiếng Anh nguyên gốc vẫn được giữ trong master để kiểm toán, không đưa vào embedding/BM25/FTS. ID, mã HS và graph giữ nguyên. Snapshot active và hash nguồn hiện hành được ghi trong output notebook 01; output benchmark cũ vẫn là kết quả lịch sử của snapshot trước.

## QA: 320 train / 150 test

`data/verified/qa/train/LEGAL_RETRIEVAL_TRAIN.jsonl` chứa 320 câu, `data/verified/qa/test/LEGAL_RETRIEVAL_TEST.jsonl` chứa 150 câu, và `all/LEGAL_RETRIEVAL_MASTER.jsonl` là union để kiểm tra. Adapter dùng `record_mapping` hoặc `source_locations` để ánh xạ alias export về chunk nguồn thật; kiểm tra ID, câu hỏi, case family và nguồn. Gold không được ingest, không fine-tune model và không dùng nhãn test để chọn chính sách.

Notebook 03 thử các họ retriever/trọng số trên QA train, sau đó so sánh đường trực tiếp với đường thêm tài liệu cha và Notes thật trước Cross-Encoder. Thử pool 30/50/100, phần ứng viên trực tiếp được giữ, và nhánh truy vấn bỏ mã đang bị nghi vấn. Chọn policy trên train và ghi khóa `qa` trong `config/selected_retrieval.json`; giữ nguyên chính sách HS. Top-10 được chấm theo ID chunk primary chính xác; gói căn cứ được chấm riêng. 50 test cũ từng được dùng để chẩn đoán nên báo riêng với 100 test mới. Kết quả là đánh giá retrieval trên bộ dữ liệu đã cung cấp, chưa phải chứng minh chất lượng kết luận pháp lý cuối cùng.

`Retriever.qa_search(query)` hoặc `knowledge_search(query)` khi đã có chính sách QA dùng corpus chung với các chunk type GIR, Notes, TT85, tariff entry ở nhiều tầng. Không cố định role/level, không hard-filter Section. Query gốc đi vào semantic/lexical retrieval; Exact che các mã được nhắc để nghi vấn/phủ định. Nhánh truy vấn bổ sung dùng câu đã bỏ mã nghi vấn để tìm hàng hóa, và chỉ hoạt động nếu chọn trên train. Gói bổ sung có graph evidence, các tài liệu cha thật, Notes của các nhánh/mã được nhắc và các rule cùng họ GIR đã tìm được; việc lấy đủ tài liệu không thay thế suy luận pháp lý.

`knowledge_search(policy="hs_transfer")` tái lập thí nghiệm chuyển chính sách HS vào các kênh HS4/HS6/AHTN8; `policy="legacy_fixed"` tái lập baseline đa tầng cũ. `routed_search` chuyển câu hỏi GIR/Notes/thủ tục sang chính sách QA khi đã có; nhánh sản phẩm vẫn dùng `adaptive_search` và chính sách HS hiện có. Các cơ chế che mã nghi vấn và mở rộng căn cứ QA không được tự động áp vào xếp hạng ứng viên sản phẩm.
