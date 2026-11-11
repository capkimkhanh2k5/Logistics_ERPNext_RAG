# Các Cấu Hình Retrieval & Reranking

| Thành phần | Mạnh ở đâu | Điểm yếu | Mức phù hợp HS | Mức phù hợp tra luật |
|---|---|---|---:|---:|
| **Dense BGE-M3** | Hiểu ngữ nghĩa, paraphrase, tiếng Việt/Anh | Dễ bỏ sót mã số, model, thông số exact | ★★★★☆ | ★★★★★ |
| **Sparse BGE-M3** | Keyword có trọng số nhưng vẫn học ngữ nghĩa | Tốn inference hơn BM25, khó giải thích score | ★★★★★ | ★★★★☆ |
| **PostgreSQL FTS** | Exact lexical, phrase/proximity, dễ triển khai | Ranking không phải BM25, phụ thuộc tokenizer | ★★★★☆ | ★★★★☆ |
| **BM25** | Keyword ranking rất mạnh, IDF + length normalization | Không hiểu synonym/ngữ nghĩa | ★★★★★ | ★★★★★ |
| **Exact Match** | HS code, `65W`, `5G`, `USB-C`, model... | Không hiểu ngữ nghĩa | ★★★★★ | ★★★☆☆ |
| **Metadata Filter** | chapter, namespace, chunk_type, hiệu lực | Không tự tìm nội dung | ★★★★★ | ★★★★★ |
| **ColBERT / Multi-vector** | Match token-level rất chi tiết | Storage + latency cao hơn Dense | ★★★★☆ | ★★★★☆ |
| **Hierarchy / Graph Retrieval** | Giữ đúng `84→8471→HS6→8 số` | Phải có graph/schema chuẩn | ★★★★★ | ★★☆☆☆ |
| **Cross-encoder Reranker** | Xếp lại Top-K cực chính xác | Chậm, không dùng để search toàn corpus | ★★★★★ | ★★★★★ |

# Các Cấu Hình RAG Được Chọn 

Đã chạy xong vòng benchmark mới với **300 train / 90 test**, giữ nguyên cách chia của bạn. Gold không được đưa vào kho tri thức.

- Thử **78.253 tổ hợp trọng số/k mỗi Phần**, cùng C11/C12, beam 5/10/20 và rerank Top-20/30/50.
- Chọn policy trên train theo **Hit@1 → Recall@5 → MRR → nDCG**.
- Hai notebook đều đã chạy, **giữ output**, không tạo report riêng.

## Cấu hình được chọn và kết quả test

*** Kết Quả TEST Mã HS ***

| Loại câu hỏi HS | Tập đo | Cand@40 | Cand@100 | Mã đúng Top-10 | Top-5 | Top-1 |
|---|---:|---:|---:|---:|---:|---:|
| Section XIV | Test, 48 ca | 62,5% | 91,7% | 56,2% | 47,9% | 18,8% |
| Section XIV | Holdout, 29 ca | 82,8% | 96,6% | 65,5% | 62,1% | 34,5% |
| Section XVI | Test, 47 ca | 97,9% | 97,9% | 95,7% | 95,7% | 85,1% |
| Section XVI | Holdout, 29 ca | 86,2% | 96,6% | 82,8% | 75,9% | 51,7% |
| Section XVII | Test, 48 ca | 87,5% | 97,9% | 85,4% | 83,3% | 43,8% |
| Section XVII | Holdout, 30 ca | 70,0% | 96,7% | 70,0% | 66,7% | 23,3% |
| **HS toàn bộ** | **Test, 143 ca** | **82,5%** | **95,8%** | **79,0%** | **75,5%** | **49,0%** |
| **HS toàn bộ** | **Holdout, 88 ca** | **79,5%** | **96,6%** | **72,7%** | **68,2%** | **36,4%** |

*** Kết Quả TEST Tra Cứu Pháp Luật ***

| Tập đo Legal | Đủ căn cứ chính Top-5 | Đủ căn cứ chính Top-10 | Đủ gói căn cứ | Trung bình recall nhóm căn cứ @10 |
|---|---:|---:|---:|---:|
| Train, 400 câu | 86,8% | 90,8% | 90,8% | 91,1% |
| Test, 150 câu | 82,0% | 86,0% | 89,3% | 87,8% |
| Holdout, 100 câu | 95,0% | 98,0% | 98,0% | 98,0% |