# GIẢI THÍCH VỀ RETRIEVAL

*** Các Thuật Ngữ ***
> RRF (Reciprocal Rank Fusion): Là một thuật toán để gộp các BXH khác nhau.Có thể hình dung điểm của một ID theo dạng: Direct Score ≈ 0.35/(60+rank_Dense) + 0.15/(60+rank_Sparse) + 0.35/(60+rank_BM25) + 0.05/(60+rank_FTS) + 0.10/(60+rank_Exact)


## Step 1: Tìm ứng viên (candidates)

Câu hỏi của người dùng -> đi tìm từ 2 nguồn:

    + Bản ghi nguồn: là dữ liệu gốc đã được tách thành từng record để tìm kiếm, có thể hiểu là source chunk
        - Chạy 5 cách tìm: Dense, Sparse, BM25, FTS, Exact 
        - 5 kênh tạo ra 5 BXH -> gộp bằng RRF với trọng số [0,35;0,15;0,35;0,05;0,1] để tạo ra bảng Direct chung.

    + Context từ Graph: lấy chính record đó, rồi dùng graph để bổ sung thông tin về record đó đang nằm ở đâu trong cấu trúc.
        - Chạy 2 cách tìm: BM25, Dense
        - 2 Kênh tạo ra 2 nguồn riêng: BM25 -> BM25 Context, Dense -> Dense Context

```VD
    Trong data về phần 14 chương 71 mục 71.01 mô tả về ngọc trai, và có các mã con mô tả chi tiết về ngọc trai đó như:
        + 7101.10.00 Ngọc trai tự nhiên, Ngọc trai nuôi cấy
        + Ngọc trai nuôi cấy:
            - 7101.21.00 Ngọc trai nuôi cấy chưa gia công
            - 7101.22.00 Ngọc trai nuôi cấy đã gia công

    Thì nếu query "ngọc trai nuôi cấy chưa gia công" thì: 
        + Record chỉ map đúng với "Đã gia công"
        + Context Graph map đúng "Ngọc trai nuôi cấy -> Đã gia công"
    (Vì context graph như một đồ thị graph, nó biết node cha -> phụ thuộc vào nhánh nào và node con -> có những node nào)
```

## Step 2: Gom ứng viên

Như vậy sau Step 1 thì chúng ta có 3 nguồn ứng viên:
    + Bản ghi nguồn (Direct)
    + Context từ Graph (BM25, Dense)

Và lấy top 12 từ Direct và top 4 từ Dense Context để làm SEED tìm kiếm mở rộng lấy thêm ứng viên từ Graph. Và cuối cùng chúng ta có 4 nguồn:
    + Bản ghi nguồn (Direct)
    + Context từ Graph (BM25, Dense)
    + Ứng viên mở rộng từ Graph

Tỉ lệ ứng viên lấy từng toàn bộ các nguồn vào pool được chia cho từng cách:
    + Direct: 0.65
    + BM25 Context: 0.125
    + Dense Context: 0,125
    + Graph: 0,1

## Step 3: Chuẩn bị Context

Sau khi có các nguồn từ Step2, thì nó tiến hành dựa vào Graph để tìm các Node Cha (Các node tổ tiên) để bổ sung ngữ cảnh hoàn chỉnh

```VD
    71012200 – Đã gia công
    ↑ Ngọc trai nuôi cấy
    ↑ các cấp cha/tổ tiên phía trên nếu phù hợp

    Rồi ghép chúng lại thành context.
```

## Step 4: Rerank

M3 chấm 100 nguồn đầu tiên, đọc theo cặp: query + context từng ứng viên -> tạo thứ hạng M3 mới dựa trên mức độ liên quan.

Tính RRF tầng 1, kết hợp 2 thứ hạng: score1 = 0.15/(60 + rank_pool) + 0.85/(60 + rank_M3)

Tương tự, hệ thống đưa top 40 cho Qwen3 để rerank thêm 1 lần nữa: score2 = 0.5/(60 + rank_score1) + 0.5/(60 + rank_Qwen3)

Như vậy kết quả trả về là 100 ứng viên đã được rerank 2 lần.

## Step 5: Chọn Top 10

Lấy top 10 nguồn đầu (bất kể loại gì) từ 100 ứng viên trên. Sau đó tạo ra Package chứng cứ bằng cách top 10 + nguồn được trích trong Context (từ Step3).

Lấy 10 mã HS8 là lọc riêng từ toàn bộ 100 nguồn đó chỉ lấy các bản ghi cấp HS8.

*** Chú Ý Sematic Intent*** 
    BGE-M3 biến câu hỏi thành vector → Logistic Regression xác định user đang hỏi theo hướng Legal/QA hay Product/HS.
    