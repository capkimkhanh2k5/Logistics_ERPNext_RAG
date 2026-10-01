# RAG Module

| File | Mục đích & Mô tả ngắn gọn |
| :--- | :--- |
| [`sources.py`] | **Data Adapters**: Đọc và chuẩn hóa cấu trúc dữ liệu biểu thuế thô. Chuyển đổi bản ghi biểu thuế về dạng chuẩn (`canonical_tariff`), phân loại vai trò (`candidate`, `scope`, `evidence`, `context`), chuẩn hóa mã HS, và thiết lập quan hệ ngữ cảnh theo độ sâu thụt lề (`CONTEXT_FOR`). |
| [`data.py`] | **Corpus & Data Pipeline**: Kiểm toán tính toàn vẹn (audit) dữ liệu nguồn, đóng gói tập ngữ liệu bất biến (`corpus.json`). Xử lý tích hợp biểu thuế TT31, 6 quy tắc GIR, Thông tư 85, tự động suy diễn nút ảo HS6 (`DERIVED_HS6_...`) để khôi phục cây phân cấp, và quản lý snapshot theo hàm băm SHA-256. |
| [`db.py`] | **Database & Ingestion**: Quản lý kết nối PostgreSQL với tiện ích mở rộng `pgvector`. Chịu trách nhiệm nạp dữ liệu snapshot có bảo đảm giao dịch (`transactional snapshot ingestion`), kiểm soát toàn vẹn vector/graph counts, hỗ trợ kiểm thử dry-run và quản lý trạng thái active snapshot/profile. |
| [`embedding.py`] | **Embedding & Reranker Models**: Quản lý mô hình nhúng BGE-M3 (dense 1024-dim, sparse lexical weights, ColBERT multivectors) và mô hình Reranker (`CrossEncoder` / `FlagReranker`). Tích hợp cơ chế cache theo nội dung (`content-addressed caching`) cho cả vector và điểm rerank. |
| [`context.py`] | **Graph Context & Enrichment**: Khai thác đồ thị phân cấp biểu thuế (`GraphContext`). Truy vết chuỗi tổ tiên, nhánh ngữ cảnh trung gian và các chú giải pháp lý ràng buộc để làm giàu thông tin cho các mã ứng viên HS; tối ưu độ dài văn bản theo ngân sách token của reranker (`fit_rerank_context`). |
| [`retrieval.py`] | **Core Hybrid Retriever**: Động cơ tìm kiếm kết hợp đa kênh (Dense pgvector, Sparse lexical, BM25, Exact match). Hợp nhất kết quả bằng RRF (Reciprocal Rank Fusion), định tuyến câu hỏi (`route`), tìm kiếm theo phân cấp thích ứng (`adaptive_search`/`hierarchy_search`), và reranking đa tầng cho cả ứng viên HS lẫn bằng chứng pháp lý. |
| [`evaluation.py`] | **Benchmark & Metrics**: Đo lường và đánh giá hiệu năng retrieval (Hit@k, MRR@10, Macro-code Hit, độ trễ p50/p95, Recall nguồn trích dẫn). Quản lý tập đối sánh gold standard và thuật toán quét tối ưu hóa không gian trọng số (`weight sweep`) mà không làm rò rỉ nhãn (no label leakage). |
| [`experiments.py`] | **Experimental Framework**: Thiết lập quy trình kiểm thử chéo phân tầng theo nhóm lồng nhau (Nested Stratified Group K-Fold). Sử dụng Disjoint Set Union (DSU) để gom cụm các mẫu tương đồng/cùng họ nhằm chống rò rỉ thông tin giữa các fold huấn luyện và đánh giá (OOF). |
| [`ReadMe.md`] | Tài liệu tổng quan mô tả kiến trúc và mục đích của các file trong module RAG. |

---