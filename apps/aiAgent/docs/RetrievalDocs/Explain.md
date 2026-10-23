# GIẢI THÍCH VỀ CHUẨN BỊ CORPUS

PDF nguồn -> Trích xuất text -> Chuẩn Hoá Nội Dung -> Chunking -> Tạo Records | Dựng Node/Edge -> Embedding & Index

Cách chunk cụ thể của từng loại như sau:
- HS / biểu thuế TT31: mỗi dòng mã HS4/HS6/HS8 là một record riêng. Các nhãn không có mã như “Ngọc trai nuôi cấy” chủ yếu được giữ trong graph để bổ sung nghĩa cho các dòng mã bên dưới.
- Chú giải / Notes: mỗi đơn vị Chú giải Phần, Chú giải Chương, Chú giải phân nhóm hoặc chú thích là một record riêng, đồng thời giữ phạm vi áp dụng của nó trong graph.
- GIR: tách theo từng quy tắc và các đoạn giải thích liên quan của quy tắc đó; vẫn giữ quan hệ/ngữ cảnh trong cùng quy tắc. Nghĩa là GIR 1 không bị trộn với GIR 2 chỉ vì nằm gần nhau trong PDF.
- TT85 / văn bản pháp lý: tách theo cấu trúc Điều → Khoản → Điểm; mỗi đơn vị có thể là record, nhưng vẫn giữ liên kết tới cha để sau này dựng context đầy đủ.

Văn bản `embedding_text` của Source Record đưa vào BGE M3 tạo Dense Vector (đại diện ngữ nghĩa) và Sparse Representation (trọng số token do mô hình học để phục vụ khớp từ vựng giữa query và tài liệu).

-> Như vậy, DataBase (Vector DB) sẽ lưu gồm:
    - corpus (nội dung source Records)
    - Dense Embedding (dense vector của record)
    - Sparse Vector (dữ liệu sparse tương ứng)
    - Graph (quan hệ cấu trúc)

## Phân biệt **Record** và **Graph**.

Giả sử PDF TT31 có cấu trúc:

```text
    Phần XIV
    └── Chương 71
        └── Nhóm 7101
            └── Ngọc trai nuôi cấy
                ├── 7101.21.00 - Chưa được gia công
                └── 7101.22.00 - Đã gia công
```

### Source Record là gì?

Với dòng `7101.22.00`, hệ thống tạo một record, về mặt khái niệm:

```json
{
  "id": "tt31:HS8:71012200",
  "source_text": "Đã gia công",
  "embedding_text": "Ngọc trai nuôi cấy - Đã gia công",
  "chunk_type": "tariff_entry",
  "metadata": {
    "section": "XIV",
    "chapter": "71",
    "hs_code": "71012200",
    "level": 8
  },
  "citation": "vị trí tương ứng trong PDF"
}
```

Record này trả lời câu hỏi:

> **“Nội dung nguồn mà tôi có thể search, embedding, xếp hạng và trích dẫn là gì?”**

Tài liệu quy định mỗi record có ID, nội dung nguồn, text phục vụ tìm kiếm, chunk type, metadata và locator/citation. 

### Còn Graph là gì?

Cùng dữ liệu đó tạo graph:

```text
    [Section XIV]
        │
        ↓ CONTAINS
    [Chapter 71]
        │
        ↓ CONTAINS
    [Heading 7101]
        │
        ↓ CONTAINS
    [Ngọc trai nuôi cấy]
        │
        ↓ CONTEXT_FOR
    [tt31:HS8:71012200 (Source ID : 71012200)]
```

Ở đây:

```text
    NODE:
    Section XIV
    Chapter 71
    7101
    Ngọc trai nuôi cấy
    71012200

    EDGE:
    Section XIV → Chapter 71
    Chapter 71 → 7101
    7101 → Ngọc trai nuôi cấy
    Ngọc trai nuôi cấy → 71012200
```

Graph trả lời câu hỏi khác:

> **“Record `71012200` nằm ở đâu trong cấu trúc và liên quan đến cái gì?”**

NODE/EDGE của hệ thống đúng là để giữ Phần, Chương, nhóm, dòng mã, nhãn, Notes và các quan hệ cha-con/phạm vi giữa chúng. 

## Sau đó hai cái mới kết hợp

Đây chính là phần quan trọng:

```text
    SOURCE RECORD
    "71012200 - Đã gia công"
            +
    GRAPH
    Section XIV
    → Chapter 71
    → 7101
    → Ngọc trai nuôi cấy
            ↓
        CONTEXT
```

Context có thể trở thành:

```text
Phần XIV
Chương 71
Nhóm 7101
Ngọc trai nuôi cấy
71012200 - Đã gia công
```


> **Record = nội dung để retrieval tìm và trả về.**  
> **Graph = cấu trúc và quan hệ xung quanh nội dung đó.**  
> **Context = Record + thông tin phù hợp lấy từ Graph.**

---

# GIẢI THÍCH VỀ RETRIEVAL

***Các Thuật Ngữ***

**RRF (Reciprocal Rank Fusion)**: Là một thuật toán để gộp các BXH khác nhau.Có thể hình dung điểm của một ID theo dạng: 

>Direct Score ≈ 0.35/(60+rank_Dense) + 0.15/(60+rank_Sparse) + 0.35/(60+rank_BM25) + 0.05/(60+rank_FTS) + 0.10/(60+rank_Exact) 

***Các Cấu Hình***

| Cấu hình | Mục đích chính |
|---|---|
| **Dense** | Tìm theo **ngữ nghĩa** |
| **Sparse** | Tìm theo **token/từ quan trọng** |
| **BM25** | Tìm theo **từ khóa có trọng số** |
| **FTS** | Tìm kiếm **toàn văn bản** |
| **Exact** | Tìm **khớp chính xác** |


***Vector DB***

```text
    PostgreSQL / pgvector
    │
    ├─ 1. SOURCE RECORDS / CORPUS
    │    ├─ id
    │    ├─ source_text
    │    ├─ embedding_text
    │    ├─ metadata
    │    └─ citation / locator
    │
    ├─ 2. DENSE EMBEDDINGS (vector của từng Source Record)
    │
    ├─ 3. SPARSE POSTINGS (biểu diễn sparse của từng Source Record)
    │
    └─ 4. GRAPH
        ├─ NODE
        ├─ EDGE
        └─ CONTEXT_FOR
```

Khi hệ thống chạy, mới dùng Source Record + Graph để dựng ra ***Context representation*** cho nhánh NODE/EDGE; từ đó phục vụ tìm kiếm nhánh Context


## Step 1: Tìm ứng viên (candidates)

Câu hỏi của người dùng -> đi tìm từ 2 nguồn:

+ Bản ghi nguồn: là dữ liệu gốc đã được tách thành từng record để tìm kiếm, có thể hiểu là source chunk
    - Chạy 5 cách tìm: Dense, Sparse, BM25, FTS, Exact 
    - 5 kênh tạo ra 5 BXH -> gộp bằng RRF với trọng số [0,35;0,15;0,35;0,05;0,1] để tạo ra bảng Direct chung.

+ Context từ Graph: lấy chính record đó, rồi dùng graph để bổ sung nhãn trung gian và tổ tiên.
    - Chạy 2 cách tìm: BM25, Dense
    - 2 Kênh tạo ra 2 nguồn riêng: BM25 -> BM25 Context, Dense -> Dense Context

```VD
    Trong data về phần 14 chương 71 mục 71.01 mô tả về ngọc trai, và có các mã con mô tả chi tiết về ngọc trai đó như:
        + 7101.10.00 Ngọc trai tự nhiên
        + Ngọc trai nuôi cấy:
            - 7101.21.00 Chưa được gia công
            - 7101.22.00 Đã gia công

    Thì nếu query "ngọc trai nuôi cấy chưa gia công" thì: 
        + Record 71012100 cung cấp nội dung "Chưa được gia công"
        + Context Graph bổ sung "Ngọc trai nuôi cấy -> Chưa được gia công"
    (Graph cung cấp cấu trúc và nhãn nguồn để mô hình chấm mức liên quan; không tự kết luận hoặc bảo đảm chọn đúng mã)
```
***ĐI VÀO SOURCE RECORD***

Data: Source Record

```text
                       QUERY
                         │
        ┌────────────────┼─────────────────────────┐
        │                │                         │
   BGE-M3 Dense     BGE-M3 Sparse             Text Query
        │                │              ┌──────────┼──────────┐
        ↓                ↓              ↓          ↓          ↓
      Dense            Sparse         BM25        FTS       Exact
        │                │              │          │          │
        └────────────────┴──────────────┴──────────┴──────────┘
                                 ↓
                             Weighted RRF
                                 ↓
                         Direct ranked list
```
***ĐI VÀO NODE/EDGE***

Data: Source Record + Graph (bổ sung ngữ cảnh) => Context
                                                    ├─ BM25 → lexical search → RAM
                                                    └─ BGE-M3 → Dense vector → semantic search → cache

```text 
                QUERY
                  │
          ┌───────┴────────┐
          │                │
     BM25 Context      Dense Context
          │                │
          ↓                ↓
   lexical search     semantic search
          │                │
          └────────┬───────┘
                   ↓
           Context candidates
```

## Step 2: Gom ứng viên

Như vậy sau Step 1 thì chúng ta có 3 nguồn ứng viên:
    + Bản ghi nguồn (Direct)
    + BM25 Context
    + Dense Context

Và lấy tối đa top 12 từ Direct và top 4 từ Dense Context để làm SEED tìm cha, tổ tiên và Notes có liên kết, nguồn có quan hệ từ Graph. BM25 Context không tạo SEED, đi trực tiếp vào hợp nhất. 

Và cuối cùng chúng ta có 4 nguồn:
    + Bản ghi nguồn (Direct)
    + BM25 Context
    + Dense Context
    + Ứng viên mở rộng từ Graph

Ngân sách phân bổ cơ hội tuyển ứng viên từ từng kênh vào pool:
    + Direct: 0.65
    + BM25 Context: 0.125
    + Dense Context: 0,125
    + Graph: 0,1

Pool tối đa 160 nguồn, bỏ trùng theo ID nguồn. Các tỷ lệ trên không bảo đảm số lượng thực tế đúng tỷ lệ khi các kênh có ID trùng hoặc thiếu ứng viên.

## Step 3: Chuẩn bị Context

Sau khi có các nguồn từ Step2, hệ thống chuẩn bị lại context cho reranker: bổ sung các node tổ tiên và nhãn trung gian qua `CONTEXT_FOR`, giữ citation và giới hạn độ dài.

```VD
    71012200 – Đã gia công
    ↑ Ngọc trai nuôi cấy
    ↑ các cấp cha/tổ tiên phía trên nếu phù hợp

    Rồi ghép chúng lại thành context.
```

## Step 4: Rerank

M3 chấm tối đa 100 nguồn đầu tiên, đọc theo cặp: query + context từng ứng viên -> tạo thứ hạng M3 mới dựa trên mức độ liên quan.

Tính RRF tầng 1, kết hợp 2 thứ hạng: score1 = 0.15/(60 + rank_pool) + 0.85/(60 + rank_M3)

Tương tự, hệ thống đưa tối đa top 40 sau tầng 1 cho Qwen3 để rerank thêm 1 lần nữa: score2 = 0.5/(60 + rank_score1) + 0.5/(60 + rank_Qwen3)

Như vậy ranked pool gồm tối đa 40 ứng viên đã qua cả M3 và Qwen3, ghép với tối đa 60 ứng viên còn lại chỉ qua M3. Tổng tối đa 100 ứng viên; các nguồn ngoài cửa sổ 100 của M3 không vào ranked pool.

## Step 5: Chọn Top 10

Lấy tối đa top 10 nguồn đầu (bất kể loại gì) từ ranked pool trên. Sau đó tạo ra Package chứng cứ bằng cách top 10 + các bản ghi nguồn được trích trong context của chính top 10 này.

Lấy tối đa 10 mã HS8 khác nhau từ toàn ranked pool: chỉ lấy các bản ghi biểu thuế cấp HS8 và bỏ mã trùng.

*** Chú Ý Semantic Intent***
    BGE-M3 biến câu hỏi thành vector → Logistic Regression xác định query theo hướng Legal/QA, Product/HS hoặc chưa rõ/kết hợp. Kết quả chỉ bổ sung metadata sau ranking, không điều hướng hoặc thay đổi pool/trọng số/ranking.
