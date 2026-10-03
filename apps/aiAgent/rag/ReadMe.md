# RAG Module

| File | Mục đích & Mô tả ngắn gọn |
| :--- | :--- |
| [`sources.py`] | **Data Adapters**: Đọc và chuẩn hóa cấu trúc dữ liệu biểu thuế thô. Chuyển đổi bản ghi biểu thuế về dạng chuẩn (`canonical_tariff`), phân loại vai trò (`candidate`, `scope`, `evidence`, `context`), chuẩn hóa mã HS, không suy diễn phạm vi nhánh pháp lý từ prefix mã. |
| [`pdf_graph.py`] | **PDF Table Geometry**: Đọc hàng/cột và dấu thụt cấp in trên PDF TT31; không đọc câu hỏi hoặc nhãn đánh giá. `scripts/build_pdf_graph.py` materialize cạnh `CONTEXT_FOR` có hash PDF, page và bbox. |
| [`data.py`] | **Corpus & Data Pipeline**: Kiểm toán tính toàn vẹn (audit) dữ liệu nguồn, đóng gói tập ngữ liệu bất biến (`corpus.json`). Xử lý tích hợp biểu thuế TT31, 6 quy tắc GIR, Thông tư 85, tự động suy diễn nút ảo HS6 (`DERIVED_HS6_...`) để khôi phục cây phân cấp, và quản lý snapshot theo hàm băm SHA-256. Gold Dev/Test chỉ dùng audit/evaluation, không được ingest. |
| [`db.py`] | **Database & Ingestion**: Quản lý kết nối PostgreSQL với tiện ích mở rộng `pgvector`. Chịu trách nhiệm nạp dữ liệu snapshot có bảo đảm giao dịch (`transactional snapshot ingestion`), kiểm soát toàn vẹn vector/graph counts, hỗ trợ kiểm thử dry-run và quản lý trạng thái active snapshot/profile. |
| [`embedding.py`] | **Embedding & Reranker Models**: BGE-M3 và các backend M3, Gemma, Qwen. Model/revision, instruction, token budget và layout inference được gắn vào cache. Scoring batch phục vụ thực nghiệm offline; runtime đo từng query. Luồng v5 dùng cùng reranker cho mọi nguồn. |
| [`context.py`] | **Graph Context & Enrichment**: Khai thác đồ thị phân cấp biểu thuế (`GraphContext`). Truy vết chuỗi tổ tiên, nhánh ngữ cảnh trung gian và các chú giải pháp lý ràng buộc để làm giàu thông tin cho các mã ứng viên HS; tối ưu độ dài văn bản theo ngân sách token của reranker (`fit_rerank_context`). |
| [`retrieval.py`] | **Core Hybrid Retriever**: Dense/Sparse/BM25/FTS/Exact và RRF. Khi có policy v5 đã khóa, `routed_search` gọi luồng chung cho mọi intent hint. Các API riêng HS/QA cũ giữ để tái lập đối chứng. |
| [`unified.py`] | **Unified Source Retrieval**: Một pool nguồn theo ID, context BM25/dense từ graph, một policy rerank hoặc cascade cho HS và Legal. HS8 chỉ là phép chiếu đầu ra; semantic intent không thay đổi retrieval. |
| [`evaluation.py`] | **Benchmark & Metrics**: Đo lường và đánh giá hiệu năng retrieval (Hit@k, MRR@10, Macro-code Hit, độ trễ p50/p95, Recall nguồn trích dẫn). Quản lý tập đối sánh gold standard và thuật toán quét tối ưu hóa không gian trọng số (`weight sweep`) mà không làm rò rỉ nhãn (no label leakage). |
| [`experiments.py`] | **Experimental Framework**: Lưu các fold mappings theo nhóm; module không tự thực hiện chọn tham số lồng nhau hay fine-tune mô hình. Sử dụng Disjoint Set Union (DSU) để gom cụm các mẫu tương đồng/cùng họ nhằm chống rò rỉ thông tin giữa các fold huấn luyện và đánh giá (OOF). |
| [`ReadMe.md`] | Tài liệu tổng quan mô tả kiến trúc và mục đích của các file trong module RAG. |

---

## Luồng chung v5

`scripts/benchmark_unified_retrieval.py run` resume thực nghiệm đã khóa: so sánh B1/B2, hai bộ trọng số chung, M3/Qwen/Gemma và cascade M3 → Qwen trên Dev; khóa `config/unified_retrieval.json` trước khi chấm Test qua Auto. Không dùng latency để loại phương án. Model M3 ở đây là BGE-reranker-v2-m3, không phải phương pháp M3 thủ công đã nghỉ sử dụng.

`routed_search(query)` tìm cả dòng biểu thuế, GIR, Notes và điều khoản pháp lý. `intent="product"`/`"qa"` chỉ là hint; không lọc nguồn, thay trọng số hoặc chọn nhánh. Nhận diện ngữ nghĩa dùng logistic regression trên vector câu hỏi, chọn bằng Dev folds giữ nhóm, trả metadata sau ranking.

`matches` là Top-10 nguồn hỗn hợp; `hs_candidates` là Top-10 mã HS8 từ cùng ranked pool. `package` bổ sung các nguồn sơ cấp được trích trong context và có thể dài hơn Top-10. Không tính package thay cho primary Top-10 khi chấm Legal. Không tự ra kết luận HS hoặc thực thi đầy đủ GIR/exclusion reasoning.

Notebook 01 chỉ build/audit nguồn. Notebook 02 đọc config và báo cáo v5; demo/runtime và resume benchmark tắt mặc định. Cấu hình khóa đúng snapshot/profile; thay nguồn hoặc embedding cần một lượt lựa chọn mới, không tự bỏ qua kiểm tra hash.

Auto v5 yêu cầu policy chung đã kích hoạt; thiếu policy sẽ báo lỗi. `legacy_routed_search` là API riêng để tái lập router v4, không là fallback của Auto.
