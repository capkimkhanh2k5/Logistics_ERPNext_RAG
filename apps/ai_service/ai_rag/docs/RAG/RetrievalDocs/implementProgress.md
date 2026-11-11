# Quá trình triển khai Retrieval HS/Legal

Mục tiêu: từ PDF nguồn xây dựng corpus có thể truy xuất và trích dẫn; chọn một cấu hình chung cho HS/Legal trên Dev; khóa cấu hình, đánh giá Test và đưa vào runtime.

**PDF → chuẩn hóa và chia chunk → NODE/EDGE → audit → embedding/index → thử cấu hình trên Dev → khóa policy → đánh giá Test → phục vụ retrieval.**

## 1. Chuẩn bị dữ liệu từ PDF

PDF là nguồn đối chiếu chuẩn. Trích xuất bảng/văn bản; PDF scan cần OCR. Kiểm tra lỗi dấu tiếng Việt, mã HS, hai cột ngôn ngữ, mô tả nối trang và nhãn thụt cấp bằng trang PDF. DOCX chuyển đổi không dùng để quyết định phạm vi nhánh.

| Dữ liệu cần chuẩn bị | Nội dung và mục đích |
|---|---|
| **Master + records ingest (JSONL)** | Master giữ nội dung chuẩn hóa và provenance; records ingest đưa từng đơn vị nguồn về schema chung để tìm kiếm. |
| **NODE** | Biểu diễn Phần, Chương, nhóm/phân nhóm, dòng mã, nhãn trung gian và chú giải để giữ cấu trúc nguồn. |
| **EDGE** | Nối cha–con, nhãn–phạm vi và chú giải–phạm vi; giúp dựng context và tìm nguồn liên quan. |
| **PDF graph/provenance (JSON)** | Giữ thứ tự/cấp dòng, trang, bbox, hash PDF và cạnh `CONTEXT_FOR`; xác định nhãn áp dụng cho những mã nào. |
| **Schema + source manifest** | Quy định trường dữ liệu và đăng ký các file đầu vào để audit/build có thể tái lập. |

Mỗi bản ghi có ID, nội dung nguồn, văn bản tìm kiếm, loại chunk, metadata và locator/citation. Metadata giữ mã HS/cấp mã, Phần/Chương, văn bản và thông tin hiệu lực nếu có. Nhật ký sửa wording lưu căn cứ PDF; không ánh xạ câu hỏi sang đáp án.

## 2. Chia chunk theo cấu trúc nguồn

Chunk được chuẩn bị theo **đơn vị có nghĩa**, không cắt PDF thành các cửa sổ ký tự đồng loạt:

- **Biểu thuế:** mỗi dòng mã HS4/HS6/HS8 là một bản ghi riêng.
- **Chú giải:** giữ từng đơn vị chú giải Phần/Chương/phân nhóm hoặc chú thích với ID và phạm vi nguồn.
- **GIR:** tách quy tắc và các đoạn giải thích; giữ quan hệ/ngữ cảnh trong cùng quy tắc.
- **Văn bản pháp lý:** tách theo điều/khoản/điểm; giữ nhãn đơn vị và liên kết tới nội dung cha.
- **Nhãn không có mã:** giữ trong graph để bổ sung nghĩa cho dòng mã. Ví dụ “Đã gia công” cần nhánh “Ngọc trai nuôi cấy”.

Phân biệt `source_text` để đối chiếu nguồn và `embedding_text` để tìm kiếm. GIR/TT85 có thể bổ sung ngữ cảnh nguồn lân cận/cha; một số nối context GIR hiện được khai báo bằng ID nguồn đã đối chiếu. Context từ graph được dựng thành biểu diễn tìm kiếm riêng, khử văn bản lặp và giữ citation.

Embedding giới hạn **1.024 token**; chunk vượt giới hạn bị từ chối, không âm thầm cắt. Không có bước tự chia mọi chunk thành 1.024 token hay overlap cố định. Context reranker được fit riêng: M3 tối đa 2.048 token; Qwen dành 1.840 token cho query/context để chừa template. Khi cần rút ngắn, bỏ citation tùy chọn nguyên khối và ghi nhận ID; phần bắt buộc quá dài sẽ báo lỗi.

## 3. Audit, embedding và lập index

Audit schema, ID trùng, mã/wording, endpoint cạnh, chu trình phân cấp, phạm vi nhãn, citation và hash nguồn trước khi build. Phạm vi nhãn dựa trên cấu trúc PDF; không suy ra thuộc tính pháp lý bằng chữ số mã HS.

Dùng **BGE-M3** tạo dense vector và sparse representation. Nạp corpus, embedding, sparse postings và graph vào PostgreSQL/pgvector theo snapshot; ingestion trong transaction, có checkpoint để resume.

Hai biểu diễn được tìm kiếm:

- **Bản ghi nguồn:** Dense + Sparse + BM25 + FTS + Exact.
- **Context từ NODE/EDGE:** đoạn nguồn + nhánh + tổ tiên, tìm bằng BM25 Context và Dense Context.

BM25 context dựng trong bộ nhớ khi runtime khởi tạo; dense context cache theo snapshot/profile/ID/hash text. Index/context được tái sử dụng, không dựng lại toàn graph cho mỗi câu hỏi.

## 4. Chuẩn bị Dev/Test

Chia khoảng **80% Dev / 20% Test**, giữ các câu cùng họ/biến thể ở cùng phía; HS phân tầng theo Chương, QA theo loại câu hỏi.

| Tập | HS | QA pháp lý | Cách dùng |
|---|---:|---:|---|
| Dev | 752 | 520 | Sàng và chọn cấu hình chung. |
| Test | 188 | 130 | Đánh giá sau khi khóa cấu hình. |

Câu hỏi/đáp án gold không vào corpus/index. Đây là lựa chọn model và tham số retrieval, **không fine-tune BGE-M3 hoặc reranker**. Bộ nhận diện intent dùng logistic regression trên vector query, chọn bằng 5 folds Dev giữ nhóm; chỉ trả metadata.

## 5. Các cấu hình đã thử và cách chọn

Runner: [benchmark_unified_retrieval.py](../../scripts/benchmark_unified_retrieval.py). Lượt v5 giữ context `plain`, pool nguồn 160 và RRF `k=60`; thử:

| Thành phần | Các lựa chọn |
|---|---|
| Reranker đơn | BGE-reranker-v2-m3, Qwen3-Reranker-0.6B, BGE-reranker-v2-gemma. |
| Context | **B1:** nguồn + hierarchy; **B2:** bổ sung Notes liên quan vào context. Notes vẫn có thể là ứng viên độc lập ở cả hai. |
| Trọng số Dense/Sparse/BM25/FTS/Exact | **Balanced:** 0.35/0.15/0.35/0.05/0.10; **Lexical:** 0.25/0.25/0.10/0.10/0.30. |
| Cửa sổ rerank tầng một | 60 hoặc 100 nguồn. |
| Trọng số RRF reranker tầng một | 0.85 hoặc 1.00; phần còn lại dành cho thứ hạng pool. |
| Cascade | M3 → Qwen; Qwen chấm 20 hoặc 40 nguồn; trọng số tầng hai 0.50 hoặc 1.00. |

Quy trình lựa chọn:

1. **Khóa protocol và đầu vào:** grid, tiêu chí, nguồn, dataset hashes, model revisions và prompt.
2. **Sàng trên 62 câu Dev nguyên nhóm:** 3 model × 2 context × 2 bộ trọng số × 2 cửa sổ × 2 trọng số rerank = **48 tổ hợp**.
3. **Chấm toàn bộ 1.272 câu Dev:** giữ context/trọng số tốt nhất của từng model qua sàng; hai model đơn tốt nhất là Qwen/Gemma, cùng M3, mỗi model thử 4 tổ hợp pool/rank weight (**12 cấu hình**). Cascade M3 → Qwen thử 2 × 2 × 2 × 2 = **16 cấu hình**. Tổng **28 cấu hình** được đánh giá toàn Dev.
4. **Chọn theo objective:** trung bình của **HS Macro MRR@10** giữa ba Phần và **Legal đủ mọi nhóm chứng cứ sơ cấp trong Top-10**. Khi bằng điểm, ưu tiên Legal group recall, HS Macro Recall@5 rồi cửa sổ rerank nhỏ hơn. Lượt này không dùng latency làm điều kiện loại.
5. **Khóa và kích hoạt policy**, rồi mới chấm Test bằng runtime Auto; không chọn lại tham số theo Test.

Objective tốt nhất: cascade **0.8464**, Qwen đơn **0.8450**, Gemma **0.8325**, M3 **0.8203**. Cascade được chọn vì đứng đầu tiêu chí đã khóa; khoảng cách với Qwen nhỏ và chưa được chứng minh vượt trội về thống kê. Đây là cấu hình tốt nhất **trong grid đã khảo sát**, không phải tối ưu toàn cục. Pool/score cache hỗ trợ replay tổ hợp; cache không tạo thêm dữ liệu học.

## 6. Cấu hình được chọn và luồng phục vụ

[Policy hiện tại](../../config/unified_retrieval.json): **B1/plain, Balanced, pool 160 → M3 100 → Qwen 40**, dùng chung cho HS và Legal.

1. Nhận query; kiểm tra policy khớp snapshot/profile và model.
2. Tìm trên bản ghi nguồn và hai kênh context. Hybrid nguồn kết hợp bằng RRF với trọng số Balanced, `k=60`.
3. Lấy tối đa **12 direct + 4 Dense Context** làm seed để tìm tổ tiên/Notes qua graph. **BM25 Context không tạo seed**, đi trực tiếp vào hợp nhất.
4. Khử trùng theo **ID nguồn**, phân bổ ngân sách direct/context BM25/context dense/graph = **0.65/0.125/0.125/0.10**, tuyển tối đa 160 nguồn.
5. Chuẩn bị Content có citation. M3 chấm 100 nguồn đầu; RRF kết hợp **0.15 thứ hạng pool + 0.85 thứ hạng M3**.
6. Qwen chấm 40 nguồn đầu sau M3; RRF kết hợp **0.50 thứ hạng tầng một + 0.50 thứ hạng Qwen**. Ghép lại tối đa 60 nguồn còn lại của tầng một. Các nguồn ngoài cửa sổ M3 không vào ranked pool.
7. Trả **Top-10 nguồn hỗn hợp**, **tối đa 10 mã HS8 khác nhau từ toàn ranked pool**, và **package gồm Top-10 cùng các bản ghi được trích trong context**. Semantic intent bổ sung loại query, không đổi pool/ranking.

Hoàn thành retrieval ở bước trả nguồn/shortlist; chưa bao gồm sinh câu trả lời hoặc tự quyết định mã HS.

## 7. Kết quả và kiểm chứng

| HS Test shortlist | N | Hit@1 | Recall@5 | Recall@10 |
|---|---:|---:|---:|---:|
| XIV | 49 | 51.0% | 91.8% | 98.0% |
| XVI | 85 | 81.2% | 94.1% | 98.8% |
| XVII | 54 | 63.0% | 83.3% | 94.4% |
| Toàn HS | 188 | 68.1% | 90.4% | 97.3% |

Legal đủ nhóm chứng cứ sơ cấp Top-10: **121/130 — 93.1%**; package đủ nhóm: **123/130 — 94.6%**. Trên danh sách nguồn hỗn hợp, HS Hit@1 **62.8%**, Recall@10 **93.6%**; đây là chỉ số khác với shortlist HS8.

Hồ sơ nghiệm thu ghi nhận **104 tests passed**, runtime/replay khớp 6 câu Dev với ba hint auto/product/qa; Ruff/format/mypy đạt. Các câu benchmark đã từng được xem nên Test là hồi quy, chưa chứng minh chất lượng ở Chương mới. Retrieval trả chứng cứ hỗ trợ đối chiếu, chưa thực thi đầy đủ GIR/Notes để kết luận mã.

Tham chiếu: [mô tả luồng](retrievalWF_Docs.md), [sơ đồ](retrievalWF.png), [protocol](../../artifacts/experiments/run_unified_accuracy_v5/protocol.json), [Dev selection](../../artifacts/experiments/run_unified_accuracy_v5/dev_selection.json), [báo cáo nghiệm thu](../../artifacts/experiments/run_unified_accuracy_v5/IMPLEMENTATION_REPORT_V5.md).
