# WorkFlows AI Agent

Có thể hình dung toàn bộ hệ thống như một chuỗi **“tìm ứng viên → đi theo graph → kiểm tra luật → chốt mã”**. Tôi lấy ví dụ một sản phẩm cụ thể: **smartphone 5G**.

Giả sử ERPNext gửi sang:

```text
Tên hàng: Smartphone 5G
Chức năng chính: thoại, dữ liệu di động, Internet
Kết nối: 5G / Wi-Fi / Bluetooth
Màn hình: cảm ứng
Camera: có
Pin: tích hợp
```

### 1. Agent 1 chuẩn hóa mô tả sản phẩm

Agent kỹ thuật biến mô tả thô thành cấu trúc:

```json
{
  "product_type": "smartphone",
  "primary_function": "mobile voice and data communication",
  "wireless_network": true,
  "cellular": true,
  "5g": true,
  "camera": true,
  "touchscreen": true
}
```

Mục tiêu bước này là làm rõ **công dụng chính** và các thuộc tính có giá trị phân loại.

---

### 2. Retriever tìm các mã ứng viên

Hệ thống chạy song song:

```text
Exact keyword / BM25
+
Dense vector search
```

Ví dụ trả về:

```text
8517.13.00
8517.14.xx
8525.xx.xx
8471.xx.xx
```

Vector search chỉ nói:

> “Các đoạn này có vẻ giống mô tả sản phẩm.”

Nó **chưa đủ để kết luận mã HS**.

Trong thiết kế của đề tài, retrieval là bước tìm mã gần nghĩa, sau đó LLM/rule engine phải đối chiếu chú giải và nguyên tắc phân loại. :chatgpt-content-reference{index="0"}

---

### 3. Graph bắt đầu từ ứng viên `8517.13.00`

Giả sử ứng viên tốt nhất là:

```text
8517.13.00
```

Graph có thể đi ngược lên:

```text
8517.13.00
   │
   │ CONTAINS / parent
   ▼
8517.13
   │
   ▼
85.17
   │
   ▼
Chapter 85
   │
   ▼
Section XVI
```

Nhờ vậy AI biết mã này **không phải một đoạn text đứng độc lập**, mà nằm trong một hệ phân cấp pháp lý.

---

### 4. Graph mở rộng sang các chú giải ràng buộc

Từ candidate `85.17`, hệ thống tiếp tục tìm:

```text
85.17
   │
   ├── CONSTRAINED_BY → Chapter 85 Notes
   │
   ├── APPLIES_WITHIN → Section XVI Notes
   │
   └── CONTEXT_WITHIN → các context liên quan 85.17
```

Đây là điểm graph quan trọng nhất.

Không chỉ hỏi:

> “Mô tả 8517.13 có giống smartphone không?”

mà còn hỏi:

> “Có chú giải nào loại trừ smartphone khỏi nhóm này không?”

> “Có nhóm nào khác được ưu tiên hơn không?”

> “Mã con này có đúng quan hệ với heading cha không?”

Theo GIR 1, việc phân loại trước hết phải dựa trên **nội dung nhóm và các Chú giải Phần/Chương liên quan**. :chatgpt-content-reference{index="1"} Chú giải còn được coi là yếu tố phải xem xét trước tiên khi phân loại. :chatgpt-content-reference{index="2"}

---

### 5. Loại các candidate sai bằng graph + luật

Giả sử Vector Search cũng lấy được:

```text
8525.xx
```

vì smartphone có camera.

Nếu chỉ dùng semantic similarity:

```text
smartphone
→ camera
→ 8525
```

rất dễ bị lệch.

Nhưng graph cho hệ thống biết:

```text
Product
 ├─ chức năng: communication  ← chức năng chính
 └─ camera                    ← chức năng phụ
```

Sau đó luật kiểm tra heading.

Kết quả reasoning có thể là:

```text
8525:
camera phù hợp về mặt từ khóa,
nhưng camera không phải bản chất/chức năng chính của hàng hóa.

8517:
phù hợp với chức năng truyền/nhận thoại và dữ liệu.
```

Candidate `8525` bị loại.

---

### 6. Tiếp tục từ Heading → HS6

Sau khi chốt phạm vi Heading:

```text
85.17
```

Graph chỉ mở các node con của `85.17`:

```text
85.17
 ├── 8517.xx
 ├── 8517.13
 ├── 8517.14
 └── ...
```

Thay vì để AI lại tìm trên toàn bộ 2.764 tariff records.

Đây chính là lợi ích của **Graph Traversal**:

```text
97 chapters
   ↓
1 chapter
   ↓
1 heading
   ↓
vài HS6
   ↓
vài AHTN8
```

Không gian tìm kiếm càng xuống thấp càng nhỏ.

---

### 7. GIR 6 xử lý cấp phân nhóm

Khi đã ở Heading `85.17`, hệ thống mới so sánh các phân nhóm cùng cấp.

Ví dụ:

```text
8517.13
vs
8517.14
vs
các phân nhóm khác trong 85.17
```

Graph đảm bảo Agent không so sánh:

```text
8517.13
```

với một subheading hoàn toàn khác cấp như:

```text
8525.xx
```

Đây là một lỗi khá dễ xảy ra nếu chỉ đưa tất cả chunks vào vector DB.

---

### 8. Đi đến AHTN 8 số

Graph tiếp tục:

```text
Section XVI
   ↓
Chapter 85
   ↓
Heading 8517
   ↓
HS6 8517.13
   ↓
AHTN8 8517.13.00
```

Mỗi bước đều có thể lưu evidence:

```json
{
  "chapter": "85",
  "heading": "8517",
  "hs6": "851713",
  "ahtn8": "85171300"
}
```

Điều này làm reasoning **trace được**.

---

### 9. Critic Agent kiểm tra ngược

Agent phản biện không hỏi:

> “Mã này có vẻ đúng không?”

mà chủ động tìm lý do để loại nó:

```text
- Có Chapter Note nào loại trừ?
- Có Section Note nào đưa hàng sang chương khác?
- Có candidate cạnh tranh nào mô tả cụ thể hơn?
- Có tính năng phụ bị nhầm thành chức năng chính?
- Có thiếu thông số để phân biệt AHTN8 không?
```

Nếu tìm thấy mâu thuẫn:

```text
Candidate → rejected
```

Nếu không:

```text
Candidate → survives validation
```

---

### 10. Human-in-the-Loop nếu thiếu dữ liệu

Ví dụ nếu để phân biệt hai mã con cần biết:

```text
Có cellular modem không?
Thiết bị có thực hiện thoại di động độc lập không?
Có cần kết nối thiết bị chủ để hoạt động không?
```

Agent không được đoán.

Nó trả lại ERP:

```text
NEED_MORE_INFORMATION

Câu hỏi:
Thiết bị có khả năng kết nối trực tiếp vào mạng di động
và thực hiện cuộc gọi mà không cần thiết bị chủ không?
```

Người dùng bổ sung → hệ thống tiếp tục graph traversal từ điểm đang dừng.

---

### 11. Output cuối không chỉ có mã HS

Kết quả nên dạng:

```text
Đề xuất:
8517.13.00

Đường suy luận:
Section XVI
→ Chapter 85
→ Heading 85.17
→ HS6 8517.13
→ AHTN8 8517.13.00

Căn cứ:
- GIR 1
- GIR 6
- Heading text
- Chapter 85 Notes
- Section XVI Notes

Candidate đã loại:
- 8525.xx: camera chỉ là chức năng phụ
- 8471.xx: không phù hợp chức năng chính

Confidence:
High

Human review:
Recommended before customs declaration
```

### Vai trò của từng thành phần lúc này

Có thể nhớ đơn giản:

```text
Vector Search
      │
      │ "Cái gì có vẻ liên quan?"
      ▼
Candidate HS codes
      │
      ▼
Graph
      │
      │ "Candidate nằm ở đâu và liên quan luật nào?"
      ▼
Chapter → Heading → HS6 → AHTN8
      │
      ├── Notes
      ├── exclusions
      ├── parent/child
      └── cross references
      │
      ▼
GIR Rule Engine
      │
      │ "Theo luật candidate nào sống sót?"
      ▼
Critic Agent
      │
      │ "Có lý do gì để bác bỏ kết quả này?"
      ▼
Human-in-the-Loop
      │
      ▼
Final HS recommendation
```

Điểm cốt lõi là **Vector DB tìm ứng viên**, còn **Graph đảm bảo AI đi đúng cấu trúc pháp lý và quan hệ phân cấp**. Nếu chỉ có Vector DB, RAG rất dễ tìm được đoạn “giống nghĩa” nhưng thuộc sai nhánh HS; Graph giúp hệ thống biết **đang đứng ở node nào, được phép đi xuống đâu, và phải kiểm những chú giải nào trước khi chốt mã**.