# FILE TRÌNH BÀY LUỒNG THỰC HIỆN TRUY XUẤT CHO RAG

## 1. XÁC ĐỊNH PHẠM VI TRI THỨC

Tập trung vào 3 nguồn chính: 
 - Section XIV: Đá quý, kim loại quý, ...
 - Section XVI: Máy móc, thiết bị, ...
 - Section XVII: Phương tiện vận tải, ...

## 2. XÁC ĐỊNH CÁC NGUỒN PHÁP LÝ

Thông tư 31: cấu trúc Section/Chapter, chú giải, heading/subheading và nội dung phân loại hàng hóa.
Thông tư 85: dữ liệu pháp lý/bổ sung phục vụ hệ thống.
GIR 1-6: các Quy tắc tổng quát giải thích việc phân loại hàng hóa.

## 3. BÓC TÁCH VÀ CHUẨN HOÁ, XỬ LÝ DỮ LIỆU

Từ các file trên chuyển hoá thành các record JSON, mỗi record gồm:
 - `section`: Section code (XIV, XVI, XVII)
 - `chapter`: Chapter code (2 số)
 -  `heading`: Heading code (4 số)
 - `subheading`: Subheading code (6 số)
 - `loại record`: `note`, `law`, `rule`, `example`, `metadata`
 - `nội dung`: nội dung text, có thể là chú giải, ví dụ, luật, quy tắc, metadata.
 - `nguồn`: nguồn dữ liệu (ví dụ: Thông tư 31, Thông tư 85, GIR 1-6)
 - `ID`: unique identifier cho record, ví dụ: `XIV-84-8471-8471.90-note-01`
 - `Quan hệ phân cấp`: các trường `section`, `chapter`, `heading`, `subheading` tạo thành cây phân cấp.

Ví dụ 1 record sẽ có dạng: 
```json
{
  "id": "TT85-A8-p1",

  "text": "Hàng hóa là máy móc, thiết bị ở dạng chưa lắp ráp hoặc tháo rời...",

  "search_text": "Thông tư 85/2026/TT-BTC | Điều 8 | Phân loại máy móc thiết bị chưa lắp ráp hoặc tháo rời | Quy tắc GIR 2(a) | Hàng hóa là máy móc...",

  "metadata": {
    "document": "TT85/2026/TT-BTC",
    "article": 8,
    "record_type": "legal_rule",
    "topic": "unassembled_machine",
    "gir_reference": "2a"
  },

  "parent_id": "TT85-A8",

  "retrieval_priority": "P0"
}
```

Xây dựng, chuẩn bị các Graph Edge để thể hiện quan hệ phân cấp giữa các record, ví dụ (Section → Chapter → Heading → Subheading → Note / Law / Rule / Example):
 - `XIV-84-8471` → `XIV-84-8471.90` (Heading → Subheading)
 - `XIV-84-8471.90` → `XIV-84-8471.90-note-01` (Subheading → Note)
 - `XIV-84-8471.90` → `XIV-84-8471.90-law-01` (Subheading → Law)
 - `XIV-84-8471.90` → `XIV-84-8471.90-rule-01` (Subheading → Rule)
 - `XIV-84-8471.90` → `XIV-84-8471.90-example-01` (Subheading → Example)

** CHUCKING **:
 - Không đơn giản là cắt mỗi 500 Token vì như vậy sẽ phá vỡ cấu trúc pháp lý.
 - Đối với kho dữ liệu Pháp Luật buộc phải cắt theo các ranh giới tự nhiên của văn bản, ví dụ: mỗi Note, mỗi Law, mỗi Rule, mỗi Example.
 - Chucking theo đơn vị pháp lý hoàn chỉnh.

Ví Dụ:
``` TT 85
    Điều 4
    ├─ Khoản 1
    └─ Khoản 2
        ├─ Điểm a
        ├─ Điểm b
        └─ Điểm c

    Thì có thể tạo chunk như:
    - Chunk 1 = Điều 4, Khoản 1
        ```json
        {
            "id": "TT85-A4-1",
            "text": "Nội dung Khoản 1...",
            "metadata": {
                "article": 4,
                "clause": 1,
                "point": null
            }
        }
        ```
    - Chunk 2 = Điều 4, Khoản 2, Điểm a
    - Chunk 3 = Điều 4, Khoản 2, Điểm b
    - Chunk 4 = Điều 4, Khoản 2, Điểm c
```

``` TT31
    Section XIV
    ├─ Chapter 84
    │   ├─ Heading 8471
    │   │   ├─ Subheading 8471.90
    │   │   │   ├─ Note 1
    │   │   │   ├─ Note 2
    │   │   │   └─ Law 1
    │   │   └─ Heading 8472
    │   └─ Chapter 85
    └─ Section XVI
    └─ Section XVII

    Thì có thể tạo chunk như:
    - Chunk 1 = Section XIV, Chapter 84, Heading 8471, Subheading 8471.90, Note 1
        ```json
        {
            "id": "XVI-84-8471-847190-NOTE1",

            "text": "Nội dung của Note 1...",

            "metadata": {
                "section": "XVI",
                "chapter": "84",
                "heading": "8471",
                "subheading": "8471.90",
                "record_type": "note",
                "note_no": "1"
            }
        }
        ```
    - Chunk 2 = Section XIV, Chapter 84, Heading 8471, Subheading 8471.90, Note 2
    - Chunk 3 = Section XIV, Chapter 84, Heading 8471, Subheading 8471.90, Law 1

    Mỗi chunk vẫn mang metadata cha:
    Section = XIV
    Chapter = 84
    Heading = 8471
    Subheading = 8471.90

    Note: Nếu một đơn vị quá dài, lúc đó mới chia nhỏ theo token, nhưng vẫn giữ cùng parent_id và context pháp lý.
```
=> Như vậy đảm bảo chuck vừa đủ nhỏ để retrieval tốt nhưng vẫn giữ nguyên ngữ cảnh pháp lý, không phá vỡ cấu trúc phân cấp.


 ## 4. NGHIÊN CỨU KIẾN TRÚC RETRIEVAL

 Phân tích toàn bộ các kiểu Retrieval có thể dùng cho RAG, từ Dense, Sparse, Exact Match, BM25, ColBERT, Graph/Hierarchy, Cross-Encoder Reranker. Xem xét ưu nhược điểm của từng kiểu retrieval và cách kết hợp chúng để đạt hiệu quả cao nhất trong việc truy xuất thông tin từ các nguồn pháp lý và phân loại hàng hóa.

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

` Note `: 
 - BM25 bắt chuỗi ký tự nhưng mù ngữ nghĩa: Tìm cực tốt các thuật ngữ kỹ thuật, mã số, tên riêng nhưng không hiểu cách diễn đạt đồng nghĩa.
 - Dense Embedding hiểu ngữ nghĩa nhưng bỏ sót các mã số, model, thông số exact.
 - Sparse Embedding là một giải pháp trung gian, vừa hiểu ngữ nghĩa vừa bắt keyword có trọng số.
 - Exact Match là một giải pháp đặc biệt, chỉ bắt các chuỗi ký tự chính xác, không hiểu ngữ nghĩa.
 - Metadata Filter là một giải pháp đặc biệt, chỉ lọc theo các trường metadata, không hiểu ngữ nghĩa.
 - ColBERT / Multi-vector là một giải pháp đặc biệt, match token-level rất chi tiết, nhưng storage + latency cao hơn Dense.
 - Hierarchy / Graph Retrieval là một giải pháp đặc biệt, giữ đúng quan hệ phân cấp giữa các record, nhưng phải có graph/schema chuẩn.
 - Cross-encoder Reranker là một giải pháp đặc biệt, xếp lại Top-K cực chính xác, nhưng chậm và không dùng để search toàn corpus.

Từ đó thiết kế cấu hình Hybrid Retrieval phù hợp với từng Section, kết hợp các phương pháp retrieval khác nhau để tối ưu hóa hiệu quả truy xuất thông tin.

## 5. XÂY DỰNG BỘ TEST / BENCHMARK CHO RETRIEVAL

Thiết lập bộ test với các truy vấn thực tế từ các Section XIV, XVI, XVII, bao gồm các truy vấn có thông số cụ thể và các truy vấn tổng quát. Mỗi truy vấn sẽ được đánh giá dựa trên các tiêu chí như Hit@1, Recall@5, MRR, nDCG để xác định hiệu quả của các cấu hình retrieval khác nhau.
 - Hit @1: Tỷ lệ truy vấn trả về kết quả chính xác ở vị trí đầu tiên.
 - Recall @5: Tỷ lệ truy vấn trả về kết quả chính xác trong top
 - MRR (Mean Reciprocal Rank): Trung bình nghịch đảo của vị trí đầu tiên trả về kết quả chính xác.
 - nDCG (Normalized Discounted Cumulative Gain): Đánh giá chất lượng xếp hạng của các kết quả trả về dựa trên vị trí và độ liên quan.

