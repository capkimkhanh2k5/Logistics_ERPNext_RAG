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

# 5. Công nghệ đề xuất

| Thành phần | Công nghệ |
|---|---|
| ERP | ERPNext / Frappe |
| AI Backend | Python + FastAPI |
| Validation Schema | Pydantic |
| Workflow | Python State Machine hoặc LangGraph |
| Relational DB | PostgreSQL |
| Vector Search | pgvector |
| Embedding | BGE-M3 |
| Sparse Retrieval | BGE-M3 Sparse hoặc lexical search |
| Reranking | Cross Encoder / BGE Reranker |
| LLM | API LLM hoặc mô hình local phù hợp |
| Document Parsing | Python PDF/HTML parser |
| API Integration | REST |
| Container | Docker |
| Logging | Python logging / structured logging |
| Evaluation | Python + pandas + sklearn |

---

# 6. Thiết kế repository

```text
ai-hs-service/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── classification.py
│   │   ├── rag.py
│   │   ├── legal.py
│   │   └── health.py
│   │
│   ├── agents/
│   │   ├── spec_agent.py
│   │   ├── rag_agent.py
│   │   ├── classifier_agent.py
│   │   ├── critic_agent.py
│   │   └── question_agent.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── workflow.py
│   │   ├── chapter.py
│   │   ├── heading.py
│   │   ├── subheading.py
│   │   └── ahtn.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── dense_retriever.py
│   │   ├── sparse_retriever.py
│   │   ├── exact_retriever.py
│   │   ├── fusion.py
│   │   ├── reranker.py
│   │   └── citations.py
│   │
│   ├── legal/
│   │   ├── gir_engine.py
│   │   ├── exclusion_checker.py
│   │   ├── note_checker.py
│   │   └── version_filter.py
│   │
│   ├── normalization/
│   │   ├── abbreviations.py
│   │   ├── materials.py
│   │   ├── chemicals.py
│   │   └── units.py
│   │
│   ├── models/
│   │   ├── product.py
│   │   ├── classification.py
│   │   ├── evidence.py
│   │   └── legal.py
│   │
│   └── services/
│       ├── postgres.py
│       ├── llm.py
│       ├── erpnext.py
│       └── tax.py
│
├── ingestion/
│   ├── parsers/
│   ├── chunking/
│   ├── hs_loader/
│   ├── legal_loader/
│   └── embedding_pipeline/
│
├── evaluation/
│   ├── dataset/
│   ├── metrics.py
│   ├── benchmark.py
│   └── ablation.py
│
├── tests/
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 7. Thiết kế dữ liệu

## 7.1. `legal_document`

```text
id
document_no
title
issuing_authority
issued_date
effective_from
effective_to
legal_status
replaces_document_id
amends_document_id
source_url
version
content_hash
```

Mục tiêu:

- quản lý phiên bản;
- tránh dùng văn bản hết hiệu lực;
- hỗ trợ truy vấn theo thời điểm khai báo.

## 7.2. `hs_node`

```text
id
code
level
parent_code
description_vi
description_en
valid_from
valid_to
```

`level`:

```text
2  = Chapter
4  = Heading
6  = HS Subheading
8  = AHTN
```

## 7.3. `hs_note`

```text
id
scope_type
scope_code
note_type
note_number
content
source_document_id
```

`note_type`:

- inclusion;
- exclusion;
- definition;
- legal_note;
- subheading_note.

## 7.4. `rag_chunk`

```text
id
document_id
hs_node_id
chunk_type
content
metadata
dense_vector
sparse_data
```

## 7.5. `tax_rate`

```text
id
hs_code
tax_type
rate
effective_from
effective_to
source_document_id
```

## 7.6. `classification_case`

```text
id
item_code
request_time
product_spec_json
candidate_codes_json
suggested_hs_code
confidence
status
human_final_code
reviewer
reviewed_at
```

## 7.7. `classification_evidence`

```text
id
case_id
source_document_id
chunk_id
evidence_type
evidence_text
```

---

# 8. Phase 1 — Chuẩn bị dữ liệu pháp lý và HS

## Mục tiêu

Xây dựng Knowledge Base có cấu trúc trước khi triển khai AI.

## Công việc

### 8.1. Thu thập nguồn

Tập trung vào:

- HS/AHTN.
- Biểu thuế.
- GIR.
- Chú giải Phần.
- Chú giải Chương.
- Chú giải phân nhóm.
- Văn bản pháp luật liên quan.
- WCO Explanatory Notes khi có quyền sử dụng phù hợp.

### 8.2. Chuẩn hóa dữ liệu

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

### 8.3. Versioning

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

# 9. Phase 2 — Document Ingestion & Hierarchical Chunking

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

# 10. Phase 3 — Xây dựng Hybrid RAG

## 10.1. Dense Search

Sử dụng BGE-M3 để tìm tương đồng ngữ nghĩa.

Ví dụ:

```text
"thiết bị biến đổi nguồn điện xoay chiều sang một chiều"
```

có thể tìm được mô tả pháp lý sử dụng thuật ngữ khác.

## 10.2. Sparse Search

Dùng cho:

- tên hóa chất;
- loại thép;
- ký hiệu;
- model;
- mã kỹ thuật;
- chuẩn kỹ thuật;
- các thuật ngữ chuyên biệt.

## 10.3. Exact/Structured Search

Bổ sung:

- CAS number;
- HS code;
- voltage;
- power;
- frequency;
- dimension;
- chemical formula.

## 10.4. Fusion

Khuyến nghị dùng Reciprocal Rank Fusion:

\[
RRF(d)=\sum_i \frac{1}{k+rank_i(d)}
\]

## 10.5. Reranking

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

# 11. Phase 4 — Technical Specification Agent

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

# 12. Phase 5 — HS Graph Traversal Engine

## Mục tiêu

Phân loại theo đúng cấu trúc HS thay vì search trực tiếp mã 8 số.

## 12.1. Tầng 1 — Chapter

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

## 12.2. Tầng 2 — Heading

Áp dụng:

- GIR 1 trước tiên;
- Section Notes;
- Chapter Notes;
- GIR 2–5 khi điều kiện tương ứng phát sinh;
- GIR 3 khi thực sự tồn tại nhiều Heading cạnh tranh.

## 12.3. Tầng 3 — HS6

Áp dụng GIR 6.

Chỉ so sánh các subheading cùng cấp.

## 12.4. Tầng 4 — AHTN8

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

# 13. Phase 6 — GIR Rule Engine

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

# 14. Phase 7 — Critic Agent

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

# 15. Phase 8 — Human-in-the-Loop

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

# 16. Phase 9 — Confidence Scoring

## Không dùng confidence do LLM tự khai báo

Không sử dụng:

```text
"LLM confidence = 95%"
```

## Confidence nội bộ

Có thể khởi đầu:

\[
C =
0.20R+
0.15M+
0.20E+
0.20G+
0.15D+
0.10K
\]

Trong đó:

- `R`: Retrieval strength.
- `M`: Candidate margin.
- `E`: Evidence coverage.
- `G`: GIR validation.
- `D`: Data completeness.
- `K`: Critic agreement.

## Phân loại

```text
HIGH
MEDIUM
LOW
```

hoặc:

```text
0.00 - 1.00
```

nhưng phải ghi rõ:

> Đây là độ tin cậy nội bộ của hệ thống, không phải xác suất pháp lý tuyệt đối.

## Deliverable

- Confidence service.
- Threshold config.
- Review policy.

---

# 17. Phase 10 — Tax Lookup

## Flow

```text
Final HS8
   ↓
Tariff Table
   ↓
Filter tax_type
   ↓
Filter declaration date
   ↓
Return rate
```

## Không cho LLM suy luận mức thuế

Ví dụ query:

```sql
SELECT rate
FROM tax_rate
WHERE hs_code = :hs_code
  AND tax_type = 'MFN'
  AND effective_from <= :declaration_date
  AND (
        effective_to IS NULL
        OR effective_to >= :declaration_date
      );
```

## Deliverable

- Tax DB.
- Tax lookup API.
- Source trace.

---

# 18. Phase 11 — API Backend

## API 1 — HS Classification

```http
POST /api/hs/classify
```

### Request

```json
{
  "item_code": "ITEM-001",
  "description": "...",
  "manufacturer": "...",
  "datasheet_text": "...",
  "classification_date": "YYYY-MM-DD"
}
```

### Response thành công

```json
{
  "status": "RECOMMENDATION",
  "hs_code": "xxxxxxxx",
  "confidence": 0.87,
  "classification_path": [
    "xx",
    "xxxx",
    "xxxxxx",
    "xxxxxxxx"
  ],
  "gir_applied": [
    "GIR1",
    "GIR6"
  ],
  "alternative_codes": [],
  "evidence": [],
  "tax": {},
  "requires_human_confirmation": true
}
```

### Response thiếu thông tin

```json
{
  "status": "NEED_MORE_INFORMATION",
  "questions": [
    {
      "field": "rated_power",
      "question": "Công suất định mức của thiết bị là bao nhiêu W?"
    }
  ]
}
```

## API 2 — Customs RAG

```http
POST /api/rag/ask
```

## API 3 — Human Answer

```http
POST /api/hs/cases/{case_id}/answer
```

## API 4 — Confirm

```http
POST /api/hs/cases/{case_id}/confirm
```

---

# 19. Phase 12 — ERPNext Integration

## Custom Fields đề xuất trên Item

```text
Technical Description
Primary Function
Material
Composition
Voltage
Power
Frequency
Dimensions

Suggested HS Code
HS Confidence
HS Status
HS AI Case ID
HS Reviewed By
HS Review Date
```

## Nút chức năng

```text
[AI Suggest HS Code]
[Ask Customs AI]
```

## UI đề xuất

```text
┌────────────────────────────────────────────┐
│ AI HS CLASSIFICATION                       │
├────────────────────────────────────────────┤
│ Suggested HS:  XXXXXXXX                    │
│ Confidence:    HIGH                        │
│                                            │
│ Path                                       │
│ XX → XXXX → XXXXXX → XXXXXXXX              │
│                                            │
│ GIR Applied                                │
│ GIR 1 → GIR 6                              │
│                                            │
│ Evidence                                   │
│ [1] ...                                    │
│ [2] ...                                    │
│                                            │
│ Alternative Code                           │
│ XXXXXXXX - Rejected because ...            │
│                                            │
│ Human confirmation required                │
│                                            │
│ [Confirm] [Reject] [Re-analyze]            │
└────────────────────────────────────────────┘
```

---

# 20. Phase 13 — Audit Trail

Mỗi lần phân loại phải lưu:

- input;
- normalized specification;
- retrieved evidence;
- candidate path;
- GIR applied;
- rejected candidates;
- Critic result;
- user questions;
- human answers;
- confidence;
- final recommendation;
- human final decision;
- legal source version.

Mục tiêu:

- giải thích được;
- tái hiện được;
- phục vụ báo cáo;
- hỗ trợ đánh giá lỗi.

---

# 21. Phase 14 — Evaluation

## Dataset

Khuyến nghị prototype:

```text
150–300 sản phẩm
```

Phân bố ở nhiều ngành:

- electronics;
- machinery;
- steel;
- plastics;
- textile;
- chemicals;
- automotive parts;
- consumer goods.

## Metrics

| Metric | Ý nghĩa |
|---|---|
| Chapter Accuracy | đúng chương 2 số |
| Heading Accuracy | đúng nhóm 4 số |
| HS6 Accuracy | đúng phân nhóm 6 số |
| HS8 Accuracy | đúng dòng thuế 8 số |
| Top-3 Recall | mã đúng nằm trong Top-3 |
| Retrieval Recall@K | lấy được bằng chứng đúng |
| Citation Precision | bằng chứng thực sự hỗ trợ kết luận |
| Exclusion Violation Rate | tỷ lệ vi phạm chú giải loại trừ |
| Abstention Accuracy | biết khi nào thiếu dữ liệu |
| Human Override Rate | tỷ lệ user thay kết quả |
| Avg Latency | thời gian xử lý |

---

# 22. Ablation Study

So sánh các cấu hình:

```text
A. LLM only

B. Dense RAG

C. Hybrid RAG

D. Hybrid RAG + Graph Traversal

E. Hybrid RAG
   + Graph Traversal
   + Critic Agent
   + Human-in-the-Loop
```

Bảng đánh giá:

| Model/System | HS8 Accuracy | Top-3 Recall | Exclusion Errors | Abstention |
|---|---:|---:|---:|---:|
| LLM only | | | | |
| Dense RAG | | | | |
| Hybrid RAG | | | | |
| + Graph | | | | |
| + Critic + HITL | | | | |

---

# 23. Phase 15 — Testing

## Unit Test

- unit conversion;
- abbreviation normalization;
- HS parent/child traversal;
- effective-date filter;
- tax lookup;
- GIR router.

## Integration Test

```text
ERPNext
→ FastAPI
→ RAG
→ Graph
→ LLM
→ DB
→ ERPNext
```

## Adversarial Test

Test sản phẩm:

- mô tả thiếu;
- từ viết tắt;
- nhiều vật liệu;
- sản phẩm composite;
- model name gây nhiễu;
- thông số mâu thuẫn;
- văn bản hết hiệu lực.

## Regression Test

Mỗi lần thay:

- prompt;
- embedding;
- reranker;
- legal dataset;

phải chạy benchmark lại.

---

# 24. Phase 16 — Deployment

## Docker services

```text
erpnext
postgres
ai-api
embedding-service
worker
```

Có thể thêm:

```text
redis
```

nếu cần queue.

## Environment

```text
development
staging
production/demo
```

## Health Check

```http
GET /health
GET /health/db
GET /health/vector
GET /health/llm
```

---

# 25. Timeline triển khai đề xuất

## Tuần 1

- Chốt schema.
- Chốt nguồn dữ liệu.
- Tạo database.
- Import HS hierarchy.

## Tuần 2

- Legal parser.
- Hierarchical chunking.
- Metadata.

## Tuần 3

- BGE-M3.
- Dense retrieval.
- Sparse retrieval.
- Hybrid fusion.

## Tuần 4

- Reranking.
- Citation.
- RAG chatbot API.

## Tuần 5

- ProductSpecification schema.
- Spec Agent.
- Abbreviation/Unit Normalization.

## Tuần 6

- Chapter traversal.
- Heading traversal.
- HS6 traversal.

## Tuần 7

- AHTN traversal.
- GIR Rule Engine.

## Tuần 8

- Critic Agent.
- Exclusion checker.
- Contradiction handling.

## Tuần 9

- Human-in-the-Loop.
- Confidence.
- Tax lookup.

## Tuần 10

- ERPNext integration.
- Item buttons.
- UI results.

## Tuần 11

- Dataset.
- Evaluation.
- Ablation study.

## Tuần 12

- End-to-end test.
- Demo scenario.
- Báo cáo.
- Fix lỗi.

---

# 26. Phân công nhóm đề xuất

## Thành viên 1 — ERPNext

- Procurement.
- Item Custom Fields.
- Shipment.
- Landed Cost.
- ERP-AI integration.

## Thành viên 2 — Data/RAG

- Legal ingestion.
- Chunking.
- Embedding.
- Hybrid retrieval.
- Vector DB.

## Thành viên 3 — AI/Agent

- Spec Agent.
- Graph Traversal.
- GIR.
- Critic Agent.
- HITL.

## Thành viên 4 — Evaluation/Frontend

- Chat UI.
- Classification UI.
- Dataset.
- Metrics.
- Testing.
- Report.

Nếu ít thành viên hơn có thể gộp vai trò.

---

# 27. MVP tối thiểu

Nếu thời gian hạn chế, MVP phải có:

1. ERPNext Item.
2. Technical specification input.
3. Legal/HS Knowledge Base.
4. Dense + lexical/sparse retrieval.
5. Chapter → Heading → HS6 → HS8 traversal.
6. GIR 1 và GIR 6.
7. Một số rule quan trọng của GIR 2–5.
8. Evidence citation.
9. Human confirmation.
10. Demo end-to-end.

Không cần triển khai mọi trường hợp HS trên thế giới ngay ở MVP.

---

# 28. Phiên bản nâng cao

Sau MVP có thể bổ sung:

- OCR cho datasheet scan.
- Table extraction.
- Image/spec diagram analysis.
- Knowledge Graph DB.
- Historical customs classification cases.
- Learned reranking.
- Confidence calibration.
- Automated legal document update.
- Multilingual product description.
- Feedback-based continual evaluation.

---

# 29. Các rủi ro chính

## Rủi ro 1 — Dữ liệu pháp lý không đúng phiên bản

Giải pháp:

- effective date;
- versioning;
- status;
- source tracking.

## Rủi ro 2 — LLM hallucination

Giải pháp:

- structured output;
- RAG;
- legal constraints;
- citation;
- Graph Traversal;
- Critic Agent.

## Rủi ro 3 — Thiếu thông số sản phẩm

Giải pháp:

- Missing Field Detection.
- Human-in-the-Loop.

## Rủi ro 4 — Vector search trả về mã giống ngữ nghĩa nhưng sai pháp lý

Giải pháp:

- Section/Chapter Notes.
- Exclusion checker.
- GIR engine.
- Graph constraints.

## Rủi ro 5 — Sai thuế suất

Giải pháp:

- deterministic Tax DB lookup;
- không cho LLM tự trả mức thuế.

## Rủi ro 6 — WCO Explanatory Notes

Cần kiểm tra quyền sử dụng/licensing trước khi đưa toàn bộ dữ liệu vào hệ thống.

---

# 30. Definition of Done

Hệ thống được xem là hoàn thành khi:

- ERPNext gọi được AI API.
- AI đọc được thông số Item.
- Spec Agent trả JSON hợp lệ.
- RAG truy xuất được HS/legal evidence.
- Graph Traversal thực hiện đủ 2 → 4 → 6 → 8 digits.
- Có validation GIR.
- Critic Agent kiểm tra exclusion/conflict.
- AI hỏi user khi thiếu decisive attributes.
- Có confidence.
- Có source citation.
- Có tax lookup.
- Human có thể confirm/reject.
- Toàn bộ process được audit.
- Có dataset đánh giá.
- Có benchmark.
- Có demo end-to-end từ Item đến Landed Cost.

---

# 31. Kết quả cuối cùng mong đợi

Hệ thống hoàn chỉnh không đơn thuần là chatbot RAG mà trở thành một **AI-assisted Customs Classification System** được tích hợp trực tiếp với ERPNext.

Pipeline cuối cùng:

```text
Manufacturer Datasheet
        ↓
ERPNext Item
        ↓
Technical Specification Agent
        ↓
Normalization
        ↓
Hybrid RAG
        ↓
HS Graph Traversal
        ↓
GIR Validation
        ↓
Critic Agent
        ↓
Human-in-the-Loop
        ↓
HS Recommendation
        ↓
Tax Lookup
        ↓
Human Confirmation
        ↓
Purchase / Import Process
        ↓
Landed Cost
        ↓
Final Inventory Valuation
```

Kiến trúc này vừa giải quyết bài toán AI, vừa gắn trực tiếp với luồng nghiệp vụ xuất nhập khẩu và quản trị giá vốn của đề tài.
