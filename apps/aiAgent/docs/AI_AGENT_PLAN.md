# KẾ HOẠCH TRIỂN KHAI HỆ THỐNG AI AGENT ĐỀ XUẤT MÃ HS TRÊN ERPNEXT

## 1. Mục tiêu tài liệu

Tài liệu này mô tả kế hoạch triển khai hoàn chỉnh lớp AI cho đề tài **Quản trị Hoạt động Xuất Nhập khẩu và Phân bổ Chi phí Mua hàng trên ERPNext**, trong đó AI hỗ trợ hai nghiệp vụ chính:

1. Tra cứu văn bản pháp luật xuất nhập khẩu bằng RAG.
2. Đề xuất mã HS Code từ thông số kỹ thuật của sản phẩm theo kiến trúc **Multi-Agent + Hierarchical Hybrid RAG + Graph Traversal Reasoning + Human-in-the-Loop**.

Hệ thống AI đóng vai trò **hỗ trợ ra quyết định**, không tự động thay thế quyết định nghiệp vụ của nhân viên khai báo hải quan.

---

# 2. Phạm vi triển khai

## 2.1. Phần ERPNext

Hệ thống ERPNext tiếp tục đảm nhiệm:

- Item Master.
- Supplier.
- Purchase Order.
- Purchase Receipt.
- Purchase Invoice.
- Shipment Tracking.
- Landed Cost Voucher.
- Báo cáo giá vốn trước và sau Landed Cost.
- Lưu kết quả đề xuất HS.
- Lưu lịch sử xác nhận hoặc từ chối đề xuất AI.

## 2.2. Phần AI

Hệ thống AI gồm:

- Technical Specification Extraction.
- Chuẩn hóa thuật ngữ kỹ thuật.
- Chuẩn hóa đơn vị đo.
- Legal RAG.
- HS Code Retrieval.
- Hybrid Search.
- HS Graph Traversal.
- GIR Rule Engine.
- Critic Agent.
- Human-in-the-Loop.
- Confidence Scoring.
- Citation/Evidence.
- Tax Lookup.
- Audit Trail.
- Evaluation Framework.

---

# 3. Kiến trúc tổng thể

```text
┌──────────────────────────────────────────────────────────────┐
│                         ERPNext                              │
│                                                              │
│ Item / PO / PR / Shipment / LCV                             │
│                                                              │
│ [AI Suggest HS Code]                                         │
│ [Ask Customs AI]                                             │
└──────────────────────────────┬───────────────────────────────┘
                               │ REST API
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                      AI ORCHESTRATOR                          │
│                                                              │
│ FastAPI + Workflow State Machine                             │
└───────────────┬────────────────┬────────────────┬────────────┘
                │                │                │
                ▼                ▼                ▼
       ┌────────────────┐ ┌──────────────┐ ┌───────────────┐
       │ Spec Agent     │ │ RAG Agent    │ │ Critic Agent  │
       │                │ │              │ │               │
       │ Parse          │ │ Legal Search │ │ GIR Check     │
       │ Normalize      │ │ HS Search    │ │ Exclusion     │
       │ Structure      │ │ Evidence     │ │ Conflict      │
       └───────┬────────┘ └──────┬───────┘ └───────┬───────┘
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ HS GRAPH TRAVERSAL    │
                     │                       │
                     │ Chapter 2 digits      │
                     │      ↓                │
                     │ Heading 4 digits      │
                     │      ↓                │
                     │ Subheading 6 digits   │
                     │      ↓                │
                     │ AHTN 8 digits         │
                     └──────────┬────────────┘
                                │
             ┌──────────────────┴───────────────────┐
             ▼                                      ▼
┌────────────────────────────┐          ┌─────────────────────────┐
│ Legal Knowledge Base       │          │ Human-in-the-Loop       │
│                            │          │                         │
│ HS/AHTN                    │          │ Missing information     │
│ GIR                        │          │ Ambiguous candidate      │
│ Legal Notes                │          │ Conflict                │
│ Effective Legal Docs       │          │ Human confirmation      │
│ Tariff Data                │          └─────────────────────────┘
└────────────────────────────┘
```

---

# 4. Nguyên tắc kiến trúc

## 4.1. Không để LLM tự đoán mã HS trực tiếp

Không sử dụng pipeline:

```text
Product Description → LLM → HS Code
```

Thay vào đó:

```text
Product
→ Structured Technical Specification
→ Candidate Retrieval
→ Legal Evidence
→ Graph Traversal
→ GIR Validation
→ Critic Review
→ Human Review
→ Final Recommendation
```

## 4.2. RAG chỉ là một thành phần

RAG có nhiệm vụ:

- tìm văn bản liên quan;
- tìm HS candidate;
- tìm chú giải;
- tìm bằng chứng hỗ trợ hoặc loại trừ.

RAG không phải thành phần duy nhất quyết định mã HS.

## 4.3. Thuế suất được tra bằng dữ liệu xác định

Không yêu cầu LLM nhớ hoặc suy luận thuế suất.

```text
Final HS Code
→ Tax Table
→ Filter theo ngày hiệu lực
→ MFN / loại thuế tương ứng
```

## 4.4. Hệ thống phải cho phép từ chối kết luận

Khi thiếu dữ liệu quan trọng:

```text
NEED_MORE_INFORMATION
```

thay vì cố đưa ra HS Code.

--- 

# 5. Phase 1 — Chuẩn bị dữ liệu pháp lý và HS

## Mục tiêu

Xây dựng Knowledge Base có cấu trúc trước khi triển khai AI.

## Công việc

### 5.1. Thu thập nguồn

Tập trung vào:

- HS/AHTN.
- Biểu thuế.
- GIR.
- Chú giải Phần.
- Chú giải Chương.
- Chú giải phân nhóm.
- Văn bản pháp luật liên quan.
- WCO Explanatory Notes khi có quyền sử dụng phù hợp.

### 5.2. Chuẩn hóa dữ liệu

Chuyển dữ liệu thành:

```text
Section
└── Chapter
    ├── Notes
    └── Heading
        ├── Notes
        └── Subheading
            └── AHTN
```

### 5.3. Versioning

Mỗi văn bản phải có:

```text
effective_from
effective_to
legal_status
version
source
```

### Deliverable

- Database HS hierarchy.
- Legal document database.
- Tax rate database.
- Bộ dữ liệu có thể query bằng SQL.

---

# 6. Phase 2 — Document Ingestion & Hierarchical Chunking

## Mục tiêu

Biến tài liệu pháp lý thành corpus phù hợp cho RAG.

## Không sử dụng fixed-size chunking làm chiến lược chính

Không ưu tiên:

```text
500 tokens/chunk
50 tokens overlap
```

vì có thể cắt đứt nội dung pháp lý.

## Chunk theo cấu trúc

Ví dụ:

```json
{
  "chunk_type": "chapter_note",
  "chapter": "85",
  "heading": null,
  "subheading": null,
  "gir": ["GIR1"],
  "note_type": "exclusion",
  "effective_from": "...",
  "effective_to": null
}
```

## Deliverable

- Pipeline import PDF/HTML.
- Parser.
- Chunker.
- Metadata generator.
- Indexable corpus.

---

# 7. Phase 3 — Xây dựng Hybrid RAG

## 7.1. Dense Search

Sử dụng BGE-M3 để tìm tương đồng ngữ nghĩa.

Ví dụ:

```text
"thiết bị biến đổi nguồn điện xoay chiều sang một chiều"
```

có thể tìm được mô tả pháp lý sử dụng thuật ngữ khác.

## 7.2. Sparse Search

Dùng cho:

- tên hóa chất;
- loại thép;
- ký hiệu;
- model;
- mã kỹ thuật;
- chuẩn kỹ thuật;
- các thuật ngữ chuyên biệt.

## 7.3. Exact/Structured Search

Bổ sung:

- CAS number;
- HS code;
- voltage;
- power;
- frequency;
- dimension;
- chemical formula.

## 7.4. Fusion

Khuyến nghị dùng Reciprocal Rank Fusion:

\[
RRF(d)=\sum_i \frac{1}{k+rank_i(d)}
\]

## 7.5. Reranking

Flow:

```text
Dense Top-K
Sparse Top-K
Exact Results
       ↓
      RRF
       ↓
    Top 20
       ↓
   Reranker
       ↓
     Top 5
```

## Deliverable

- Hybrid retriever.
- Search API.
- Benchmark Recall@K.

---

# 8. Phase 4 — Technical Specification Agent

## Mục tiêu

Chuyển dữ liệu nhà sản xuất thành JSON kỹ thuật chuẩn.

## Input

- Item Description.
- Manufacturer Datasheet.
- PDF.
- Nội dung text.
- Custom fields ERPNext.

## Output

```json
{
  "product_name": "...",
  "product_type": "...",
  "primary_function": "...",
  "materials": [],
  "composition": [],
  "dimensions": {},
  "voltage": {},
  "power": null,
  "frequency": null,
  "operating_principle": "...",
  "intended_use": "...",
  "part_of_machine": null,
  "missing_fields": [],
  "evidence": []
}
```

## Normalization

Ví dụ:

```text
SUS304 → Stainless Steel 304
SS304  → Stainless Steel 304
VFD    → Variable Frequency Drive
PCB    → Printed Circuit Board
```

## Unit normalization

```text
0.8 kW → 800 W
2.5 cm → 25 mm
```

## Deliverable

- `ProductSpecification` schema.
- Spec extraction prompt.
- Normalizer.
- Unit converter.
- Test dataset.

---

# 9. Phase 5 — HS Graph Traversal Engine

## Mục tiêu

Phân loại theo đúng cấu trúc HS thay vì search trực tiếp mã 8 số.

## 9.1. Tầng 1 — Chapter

```text
Product Specification
        ↓
Candidate Chapters
        ↓
Top <= 3 Chapters
```

Dựa vào:

- vật liệu;
- công năng;
- nguyên lý hoạt động;
- loại sản phẩm.

## 9.2. Tầng 2 — Heading

Áp dụng:

- GIR 1 trước tiên;
- Section Notes;
- Chapter Notes;
- GIR 2–5 khi điều kiện tương ứng phát sinh;
- GIR 3 khi thực sự tồn tại nhiều Heading cạnh tranh.

## 9.3. Tầng 3 — HS6

Áp dụng GIR 6.

Chỉ so sánh các subheading cùng cấp.

## 9.4. Tầng 4 — AHTN8

Xét các thuộc tính cụ thể như:

- công suất;
- điện áp;
- tần số;
- kích thước;
- vật liệu;
- cấu tạo;
- mục đích sử dụng.

## Deliverable

- HS tree traversal.
- Candidate state.
- Rule hooks.
- Reasoning trace.

---

# 10. Phase 6 — GIR Rule Engine

## Mục tiêu

Không để LLM tự kích hoạt tùy ý các GIR.

## Ví dụ rule routing

```python
if incomplete_or_unfinished:
    activate("GIR_2A")

if mixture_or_composite:
    activate("GIR_2B")

if len(valid_headings) >= 2:
    activate("GIR_3")

if packaging_condition:
    activate("GIR_5")
```

## LLM đảm nhiệm

LLM có thể phân tích:

```text
Đây có phải hàng hóa hỗn hợp không?
Đây có phải bộ sản phẩm không?
Sản phẩm có hoàn chỉnh về đặc trưng cơ bản không?
```

## Rule Engine đảm nhiệm

- kích hoạt rule;
- lưu rule đã dùng;
- kiểm tra thứ tự;
- đưa vào audit trace.

---

# 11. Phase 7 — Critic Agent

## Nhiệm vụ

Agent này không cố chứng minh đáp án là đúng.

Nó chủ động tìm lý do khiến đáp án có thể sai.

## Kiểm tra

1. Section Notes.
2. Chapter Notes.
3. Exclusion Notes.
4. Competing Headings.
5. GIR sequence.
6. Missing decisive attributes.
7. Unsupported assumptions.
8. Conflicting evidence.

## Output

```json
{
  "candidate": "xxxxxxxx",
  "status": "PASS",
  "critic_score": 0.83,
  "issues": [],
  "competing_codes": [],
  "missing_fields": []
}
```

Hoặc:

```json
{
  "candidate": "xxxxxxxx",
  "status": "REQUIRES_REVIEW",
  "issues": [
    {
      "type": "missing_attribute",
      "field": "rated_power"
    }
  ]
}
```

## Deliverable

- Critic prompt.
- Exclusion checker.
- Contradiction checker.
- Critic tests.

---

# 12. Phase 8 — Human-in-the-Loop

## Trigger

Human review được kích hoạt khi:

- thiếu dữ liệu;
- nhiều candidate gần nhau;
- Critic phát hiện conflict;
- confidence dưới threshold;
- dữ liệu nhà sản xuất không đủ bằng chứng.

## Question Generator

Không hỏi chung chung.

Ví dụ:

```text
Candidate A: power <= 1000 W
Candidate B: power > 1000 W
```

Sinh:

```text
"Công suất định mức của thiết bị là bao nhiêu W?"
```

Sau khi user trả lời:

```text
ASK_HUMAN
    ↓
UPDATE_STATE
    ↓
RESUME_TRAVERSAL
```

## Deliverable

- `NEED_MORE_INFORMATION` state.
- Question Generator.
- Resume workflow.

---

