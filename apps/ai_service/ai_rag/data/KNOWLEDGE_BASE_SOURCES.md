# KNOWLEDGE_BASE_SOURCES.md
## Knowledge Base thu gọn cho AI RAG phân loại HS – Phần XVI

> **Project:** ERPNext + AI-assisted HS Classification  
> **Scope MVP:** Thiết bị điện tử, máy tính, điện thoại, thiết bị mạng, nguồn điện, pin, màn hình và các thiết bị liên quan thuộc **Phần XVI – Chương 84 và Chương 85**.  
> **Mục tiêu:** Giảm phạm vi dữ liệu để xây dựng và kiểm thử RAG trước khi mở rộng ra toàn bộ 21 Phần và 97 Chương.

---

# 1. Phạm vi hiện tại

Hệ thống AI **không xử lý toàn bộ Danh mục HS** ở giai đoạn MVP.

Phạm vi hiện tại:

```text
TT31/2022/TT-BTC
│
├── Phụ lục II
│   └── GIR 1 → GIR 6
│
├── Bảng tổng mục lục
│   └── 21 Phần + 97 Chương
│       └── chỉ dùng để xác định OUT_OF_SCOPE
│
└── Phụ lục I
    └── PHẦN XVI
        ├── Chú giải Phần XVI
        ├── Chương 84
        │   ├── Chú giải Chương 84
        │   ├── các Nhóm 4 số
        │   ├── các Phân nhóm 6 số
        │   └── các dòng AHTN/VN 8 số
        │
        └── Chương 85
            ├── Chú giải Chương 85
            ├── các Nhóm 4 số
            ├── các Phân nhóm 6 số
            └── các dòng AHTN/VN 8 số
```

---

# 2. Các nguồn dữ liệu bắt buộc

## KB-01 — Thông tư 31/2022/TT-BTC

### Vai trò

Đây là **nguồn dữ liệu HS/AHTN chính cho MVP**.

Sử dụng để lấy:

- cấu trúc 21 Phần và 97 Chương;
- toàn bộ Phần XVI;
- Chương 84;
- Chương 85;
- Chú giải Phần;
- Chú giải Chương;
- Chú giải phân nhóm;
- mã HS 4 số, 6 số;
- mã AHTN/Vietnam 8 số;
- mô tả hàng hóa.

### Nguồn

```text
https://vbpl.vn/TW/Pages/ivbpq-toanvan.aspx?ItemID=155207
```

Trang Công báo:

```text
https://congbao.chinhphu.vn/van-ban/thong-tu-so-31-2022-tt-btc-37431.htm
```

### Priority

```text
P0
```

### Namespace

```text
hs_scope_index
hs_section_xvi
hs_chapter_84
hs_chapter_85
legal_notes
```

---

# 3. KB-02 — Phụ lục II của TT31: GIR 1 → GIR 6

## Vai trò

Đây là Rule Knowledge Base cho toàn bộ quá trình phân loại.

Phải ingest đầy đủ:

```text
GIR 1
GIR 2(a)
GIR 2(b)
GIR 3(a)
GIR 3(b)
GIR 3(c)
GIR 4
GIR 5(a)
GIR 5(b)
GIR 6
```

Không chỉ lưu dưới dạng text.

Nên tạo thêm rule dạng có cấu trúc:

```json
{
  "rule_id": "GIR_3B",
  "trigger": [
    "mixture",
    "composite_good",
    "retail_set"
  ],
  "principle": "essential_character"
}
```

### Priority

```text
P0
```

### Namespace

```text
gir_rules
```

---

# 4. KB-03 — Bảng tổng mục lục 21 Phần + 97 Chương

## Có cần không?

**Có, nhưng không dùng làm corpus reasoning chính.**

Mục đích:

```text
product
   ↓
scope router
   ↓
thuộc Chapter 84/85?
   ├── YES → tiếp tục RAG
   └── NO  → OUT_OF_SCOPE
```

### Chỉ cần lưu dữ liệu rất nhỏ

Ví dụ:

```csv
section_code,section_name,chapter_from,chapter_to
I,...,01,05
II,...,06,14
...
XVI,...,84,85
...
XXI,...,97,97
```

Hoặc chi tiết theo Chapter:

```csv
chapter_code,section_code,chapter_name,in_scope
84,XVI,...,true
85,XVI,...,true
90,XVIII,...,false
91,XVIII,...,false
```

### Priority

```text
P0-Router
```

### Namespace

```text
hs_scope_index
```

### Lưu ý

Không embedding toàn bộ 97 Chương.

Dùng:

```text
SQL / dictionary / exact lookup
```

sẽ hiệu quả hơn Vector Search.

---

# 5. KB-04 — Toàn bộ Phần XVI

## Đây là dữ liệu chính của RAG MVP

Phải lấy đầy đủ:

```text
PHẦN XVI
│
├── Chú giải Phần XVI
│
├── CHƯƠNG 84
│   ├── Chú giải Chương
│   ├── Heading 4-digit
│   ├── HS6
│   └── AHTN/VN8
│
└── CHƯƠNG 85
    ├── Chú giải Chương
    ├── Heading 4-digit
    ├── HS6
    └── AHTN/VN8
```

## Không được chỉ lấy các dòng mã HS

Phải giữ cả:

```text
Section Notes
Chapter Notes
Subheading Notes
Heading descriptions
HS6 descriptions
AHTN8 descriptions
```

vì đây là dữ liệu pháp lý dùng để loại candidate.

---

# 6. Chương 84 — phạm vi MVP

Chương 84 đặc biệt quan trọng với:

- laptop;
- desktop;
- server;
- máy xử lý dữ liệu;
- một số linh kiện/phụ kiện máy tính;
- thiết bị xử lý dữ liệu tự động.

## Nhóm cần chú ý trước

```text
84.71
```

Máy xử lý dữ liệu tự động và các đơn vị của chúng.

Tuy nhiên:

> Không nên chỉ ingest nhóm 84.71.

Phải giữ **toàn bộ Chương 84** để AI có thể:

- so sánh candidate;
- đọc chú giải;
- phát hiện loại trừ;
- tránh ép mọi thiết bị máy tính vào 84.71.

### Namespace

```text
hs_chapter_84
```

---

# 7. Chương 85 — phạm vi MVP

Chương 85 là trọng tâm cho thiết bị điện tử.

Các nhóm đặc biệt quan trọng:

```text
85.04  — nguồn/sạc/bộ biến đổi điện
85.07  — ắc quy/pin
85.17  — điện thoại/thiết bị truyền dữ liệu
85.18  — microphone/speaker/headphone
85.23  — phương tiện lưu trữ
85.25  — camera/thiết bị truyền hình ảnh
85.28  — monitor/display
```

Ngoài ra vẫn phải ingest:

```text
toàn bộ Chương 85
```

để AI có đủ candidate cạnh tranh.

### Namespace

```text
hs_chapter_85
```

---

# 8. KB-05 — Thông tư 85/2026/TT-BTC

## Vai trò

Dùng làm lớp pháp lý điều khiển quy trình phân loại.

Không phải nguồn chính để semantic search mã HS.

### Nguồn

```text
https://vanban.chinhphu.vn/?classid=1&docid=218770&pageid=27160
```

### Nội dung cần ưu tiên

Các điều liên quan:

- nguyên tắc phân loại;
- căn cứ phân loại;
- sử dụng GIR;
- sử dụng Chú giải HS;
- sử dụng WCO/AHTN;
- dữ liệu phân loại;
- kết quả xác định trước/phân tích/phân loại.

### Priority

```text
P0
```

### Namespace

```text
legal_classification
```

---

# 9. Dataset MVP cuối cùng

Knowledge Base MVP chỉ cần:

```text
1. TT31 — Phụ lục II
   └── GIR 1 → 6

2. TT31 — Index
   └── 21 Phần + 97 Chương
       └── chỉ làm Scope Router

3. TT31 — Phụ lục I
   └── Toàn bộ Phần XVI
       ├── Chú giải Phần XVI
       ├── Chương 84
       └── Chương 85

4. TT85/2026
   └── Classification rules/process

5. Product Technical Documents
   ├── Datasheet
   ├── SDS
   ├── BOM
   └── Technical specs
```

---

# 10. Dữ liệu chưa cần ingest ở MVP

Tạm thời **không ingest**:

```text
các Phần I → XV
các Phần XVII → XXI
nội dung chi tiết các Chương khác 84/85
WCO HS 2022 standalone
AHTN 2022 standalone
WCO Explanatory Notes
WCO Classification Opinions
WCO Classification Decisions
case Hải quan Việt Nam
Nghị định về thuế
biểu thuế MFN
trade-control lists
```

Các dữ liệu này sẽ bổ sung ở Phase 2.

---

# 11. Out-of-Scope mechanism

Nếu sản phẩm không phù hợp với Chương 84 hoặc 85:

```json
{
  "status": "OUT_OF_SCOPE",
  "reason": "Sản phẩm có dấu hiệu thuộc Chapter ngoài 84/85.",
  "candidate_chapters": [
    "90"
  ],
  "action": "Expand knowledge base before classification."
}
```

AI **không được ép** sản phẩm về Chương 84/85.

---

# 12. Ví dụ

## Laptop

```text
Product
 ↓
Scope Router
 ↓
Phần XVI
 ↓
Chapter 84
 ↓
84.71
 ↓
HS6
 ↓
AHTN8
```

## Smartphone

```text
Product
 ↓
Scope Router
 ↓
Phần XVI
 ↓
Chapter 85
 ↓
85.17
 ↓
HS6
 ↓
AHTN8
```

## Bộ sạc laptop

```text
Product
 ↓
Chapter 85
 ↓
85.04
 ↓
HS6
 ↓
AHTN8
```

## Thiết bị đo chuyên dụng

```text
Product
 ↓
Scope Router
 ↓
có khả năng thuộc Chapter 90
 ↓
OUT_OF_SCOPE
```

---

# 13. Cấu trúc dữ liệu đề xuất

```text
knowledge-base/
│
├── scope/
│   └── hs_21_sections_97_chapters.csv
│
├── gir/
│   └── gir_1_6.json
│
├── section_xvi/
│   ├── section_notes.json
│   │
│   ├── chapter_84/
│   │   ├── chapter_notes.json
│   │   ├── headings.json
│   │   ├── hs6.json
│   │   └── ahtn8.json
│   │
│   └── chapter_85/
│       ├── chapter_notes.json
│       ├── headings.json
│       ├── hs6.json
│       └── ahtn8.json
│
├── legal/
│   └── tt85_2026/
│
└── product/
    ├── datasheets/
    ├── sds/
    ├── bom/
    └── technical_specs/
```

---

# 14. Metadata cho HS chunk

```json
{
  "source": "TT31/2022/TT-BTC",
  "section": "XVI",
  "chapter": "85",
  "heading": "8517",
  "hs6": "851713",
  "ahtn8": null,
  "chunk_type": "heading_description",
  "legal_level": "P0",
  "in_scope": true
}
```

---

# 15. Metadata cho Legal Note

```json
{
  "source": "TT31/2022/TT-BTC",
  "section": "XVI",
  "chapter": "85",
  "note_number": "3",
  "note_type": "exclusion",
  "chunk_type": "chapter_note",
  "legal_level": "P0"
}
```

---

# 16. Chunking strategy

Không dùng:

```text
500 token fixed chunks
```

làm phương pháp chính.

Dùng:

```text
Section Note
Chapter Note
Heading
Subheading
AHTN Line
GIR Rule
```

làm đơn vị chunk.

Ví dụ:

```text
chunk_001 = GIR 1
chunk_002 = GIR 2
chunk_100 = Section XVI Note 1
chunk_200 = Chapter 84 Note 1
chunk_300 = Heading 8471
chunk_400 = Chapter 85 Note 1
chunk_500 = Heading 8517
```

---

# 17. Retrieval routing

## Bước 1 — Scope

Query:

```text
Product Specification
```

tra:

```text
hs_scope_index
```

Kết quả:

```text
84 / 85 / OUT_OF_SCOPE
```

## Bước 2 — Chapter

Nếu:

```text
84
```

chỉ search:

```text
Section XVI Notes
Chapter 84 Notes
Chapter 84 headings
GIR
```

Nếu:

```text
85
```

chỉ search:

```text
Section XVI Notes
Chapter 85 Notes
Chapter 85 headings
GIR
```

---

# 18. Graph Traversal MVP

```text
PRODUCT
   ↓
Scope Router
   ↓
PHẦN XVI?
   │
   ├── NO → OUT_OF_SCOPE
   │
   └── YES
        ↓
     84 or 85
        ↓
     Heading 4
        ↓
       HS6
        ↓
      AHTN8
```

---

# 19. Hybrid Search

Trong phạm vi này vẫn dùng:

```text
Dense Search
+
Sparse Search
+
Exact Match
```

### Dense

Cho:

```text
function
usage
operating principle
```

### Sparse

Cho:

```text
Wi-Fi
USB
Li-ion
SSD
LCD
OLED
220V
65W
802.11ax
```

### Exact

Cho:

```text
HS code
model
voltage
power
frequency
standard
```

---

# 20. Phase 2 mở rộng sau MVP

Sau khi hệ thống chạy tốt với Phần XVI:

```text
Phase 2A:
WCO Explanatory Notes

Phase 2B:
Vietnam Customs classification cases

Phase 2C:
WCO Classification Decisions

Phase 2D:
Chapter 90 — nếu mở rộng thiết bị đo/quang học

Phase 2E:
Chapter 91 — nếu mở rộng đồng hồ/wearable

Phase 2F:
mở dần các Chapter khác
```

---

# 21. Definition of Done cho Knowledge Base MVP

Knowledge Base được xem là đủ để bắt đầu AI khi:

- [ ] Có GIR 1–6.
- [ ] Có index 21 Phần/97 Chương.
- [ ] Có Chú giải Phần XVI.
- [ ] Có toàn bộ Chương 84.
- [ ] Có toàn bộ Chương 85.
- [ ] Có hierarchy 2→4→6→8.
- [ ] Có TT85/2026.
- [ ] Có metadata đầy đủ.
- [ ] Có `OUT_OF_SCOPE`.
- [ ] Có product datasheet mẫu.
- [ ] Chunking theo cấu trúc pháp lý hoàn tất.
- [ ] Có Dense/Sparse/Exact retrieval.

---

# 22. Kết luận

Ở giai đoạn hiện tại, **không cần xây RAG cho toàn bộ 21 Phần và 97 Chương**.

Dataset nên thu gọn thành:

```text
GIR 1–6
+
Index 21 Phần / 97 Chương
+
Phần XVI
    ├── Chapter 84
    └── Chapter 85
+
TT85/2026
+
Product Technical Data
```

Trong đó:

```text
Index 21 Phần/97 Chương
```

chỉ đóng vai trò **Scope Router**.

Còn RAG thực sự chỉ xử lý:

```text
Section XVI
+
Chapter 84
+
Chapter 85
+
GIR
+
Legal Notes
```

Đây là scope phù hợp để xây PoC/MVP cho điện thoại, laptop và các thiết bị điện tử trước khi mở rộng sang các nhóm hàng khác.
