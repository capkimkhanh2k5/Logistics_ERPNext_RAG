# MÔ TẢ HỆ THỐNG AI ĐỀ XUẤT MÃ HS BẰNG MULTI-AGENT, RAG VÀ GRAPH TRAVERSAL

## 1. Giới thiệu

Trong nghiệp vụ xuất nhập khẩu, việc phân loại đúng mã HS Code ảnh hưởng trực tiếp đến:

- thuế nhập khẩu;
- chính sách quản lý hàng hóa;
- giấy phép;
- thủ tục hải quan;
- chi phí;
- thời gian thông quan;
- rủi ro truy thu và xử phạt.

Khó khăn lớn là thông tin của nhà sản xuất thường sử dụng nhiều:

- từ viết tắt;
- thuật ngữ kỹ thuật;
- đơn vị đo khác nhau;
- mã model;
- tên thương mại.

Trong khi đó hệ thống HS và các văn bản pháp lý sử dụng cấu trúc phân cấp, thuật ngữ pháp lý và nhiều chú giải loại trừ.

Do đó hệ thống AI được xây dựng theo hướng:

> **Multi-Agent + Retrieval-Augmented Generation + Hierarchical Hybrid Retrieval + Graph Traversal Reasoning + Rule Engine + Human-in-the-Loop**

Hệ thống không được thiết kế để tự động thay thế nhân viên hải quan hoặc người khai báo. AI cung cấp:

- đề xuất;
- bằng chứng;
- phương án thay thế;
- cảnh báo;
- câu hỏi bổ sung;

để con người đưa ra quyết định cuối cùng.

---

# 2. Mục tiêu AI

Hệ thống AI giải quyết hai bài toán.

## 2.1. Customs Legal Assistant

Cho phép người dùng đặt câu hỏi:

```text
Mặt hàng này thuộc nhóm nào?

Quy định hiện hành áp dụng cho mặt hàng X là gì?

Điều kiện để loại khỏi Chương Y là gì?

Tại sao mã A không phù hợp?
```

AI tìm và trả lời dựa trên nguồn pháp lý có trích dẫn.

## 2.2. HS Classification Assistant

Nhận dữ liệu kỹ thuật từ Item hoặc datasheet và đề xuất:

```text
Chapter
Heading
HS6
AHTN8
```

cùng với:

- classification path;
- GIR đã áp dụng;
- supporting evidence;
- exclusion checks;
- alternative HS Codes;
- confidence;
- thông tin còn thiếu;
- tax lookup;
- yêu cầu xác nhận của con người.

---

# 3. Vì sao không dùng một LLM duy nhất?

Cách đơn giản:

```text
Product Description
      ↓
     LLM
      ↓
   HS Code
```

có nhiều rủi ro:

- hallucination;
- nhảy trực tiếp đến mã 8 số;
- bỏ qua cấu trúc HS;
- bỏ qua chú giải loại trừ;
- không biết văn bản còn hiệu lực hay không;
- confidence do LLM tự khai báo không đáng tin cậy;
- khó audit;
- khó giải thích.

Hệ thống đề xuất thay thế bằng:

```text
Product
   ↓
Technical Extraction
   ↓
Normalization
   ↓
Legal Retrieval
   ↓
Hierarchical Classification
   ↓
Rule Validation
   ↓
Critical Review
   ↓
Human Confirmation
```

---

# 4. Khái niệm Multi-Agent

Multi-Agent trong hệ thống không có nghĩa là nhiều chatbot trò chuyện tự do.

Mỗi Agent có nhiệm vụ riêng, input/output được kiểm soát.

Kiến trúc:

```text
                    ┌──────────────────┐
                    │ AI Orchestrator  │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
    │ Spec Agent  │   │ RAG Agent   │   │ Critic Agent │
    └──────┬──────┘   └──────┬──────┘   └──────┬───────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ▼
                    HS Graph Traversal
                             │
                             ▼
                    Human-in-the-Loop
```

---

# 5. Agent 1 — Technical Specification Agent

## Nhiệm vụ

Agent 1 chịu trách nhiệm đọc và chuẩn hóa dữ liệu sản phẩm.

Nguồn đầu vào:

- Item Description.
- Manufacturer Datasheet.
- PDF.
- Catalog.
- Technical Specification.
- Custom fields từ ERPNext.

## Vấn đề thực tế

Ví dụ cùng một vật liệu có thể xuất hiện dưới nhiều dạng:

```text
SUS304
SS304
Stainless Steel 304
AISI 304
```

AI phải đưa về một biểu diễn chuẩn.

Ví dụ từ viết tắt:

```text
PCB → Printed Circuit Board
VFD → Variable Frequency Drive
ABS → Acrylonitrile Butadiene Styrene
```

## Output dạng có cấu trúc

```json
{
  "product_name": "...",
  "product_type": "...",
  "primary_function": "...",
  "materials": [],
  "composition": [],
  "dimensions": {},
  "electrical": {
    "input_voltage": null,
    "output_voltage": null,
    "power": null,
    "frequency": null
  },
  "operating_principle": "...",
  "intended_use": "...",
  "part_of_machine": null,
  "manufacturer_model": "...",
  "missing_fields": [],
  "evidence": []
}
```

Agent không được chỉ trả một đoạn văn.

---

# 6. Normalization Layer

Sau Spec Agent là lớp chuẩn hóa deterministic.

## 6.1. Abbreviation normalization

```text
VFD → Variable Frequency Drive
PCB → Printed Circuit Board
SUS304 → Stainless Steel 304
```

## 6.2. Unit normalization

Ví dụ:

```text
0.8 kW → 800 W
0.25 cm → 2.5 mm
2500 µm → 2.5 mm
```

Mục tiêu là để điều kiện pháp lý có thể so sánh trực tiếp.

Ví dụ:

```text
Product power = 0.8 kW
Legal threshold = 1000 W
```

sau normalization:

```text
800 W <= 1000 W
```

## 6.3. Material normalization

Chuẩn hóa:

- thép;
- thép không gỉ;
- hợp kim;
- plastic;
- polymer;
- hóa chất;
- vật liệu composite.

---

# 7. Agent 2 — Legal & HS RAG Agent

## Nhiệm vụ

Agent 2 truy xuất bằng chứng từ Knowledge Base.

Nó không được tự tạo văn bản pháp lý.

Các nguồn được tổ chức thành nhiều namespace hoặc collection.

```text
hs_nomenclature
legal_notes
gir_rules
legal_documents
wco_notes
classification_cases
tax_schedule
```

---

# 8. RAG là gì trong hệ thống?

RAG gồm hai bước chính:

```text
Retrieve
   ↓
Generate
```

### Retrieve

Tìm tài liệu liên quan.

### Generate

LLM dựa trên các tài liệu được tìm thấy để:

- tóm tắt;
- giải thích;
- so sánh;
- lập luận;
- đưa bằng chứng.

Trong hệ thống HS:

```text
Product Specification
       ↓
Retriever
       ↓
Legal/HS Candidates
       ↓
LLM Reasoning
```

Tuy nhiên RAG không được phép tự chốt mã cuối cùng mà không qua Graph Traversal và validation.

---

# 9. Hierarchical Chunking

Văn bản pháp lý không được cắt chủ yếu theo số token.

Cấu trúc phải được giữ:

```text
Section
 └── Chapter
     ├── Chapter Notes
     │
     └── Heading
         ├── Heading Description
         ├── Inclusion
         ├── Exclusion
         │
         └── Subheading
              ├── Description
              ├── Subheading Notes
              │
              └── AHTN
```

Ví dụ chunk:

```json
{
  "chunk_type": "subheading_note",
  "section": "XVI",
  "chapter": "85",
  "heading": "8504",
  "subheading": "850440",
  "note_type": "exclusion",
  "gir": ["GIR1", "GIR6"],
  "effective_from": "...",
  "effective_to": null
}
```

Lợi ích:

- filter theo Chapter;
- filter theo level;
- lọc theo thời gian hiệu lực;
- truy được quan hệ cha-con;
- hỗ trợ Graph Traversal.

---

# 10. BGE-M3 và Hybrid Search

Hệ thống sử dụng BGE-M3 để biểu diễn truy vấn và dữ liệu.

Hybrid Search có ba thành phần.

## 10.1. Dense Search

Tìm tương đồng ngữ nghĩa.

Ví dụ:

```text
"thiết bị chuyển đổi nguồn xoay chiều thành điện một chiều ổn định"
```

có thể khớp với:

```text
"static converters"
```

mặc dù khác từ ngữ.

## 10.2. Sparse Search

Tìm theo tín hiệu lexical mạnh.

Đặc biệt phù hợp:

```text
LiFePO4
SUS304
polyethylene terephthalate
50 Hz
802.11ax
8504
```

Sparse embedding không đồng nhất với BM25, nhưng đóng vai trò tương tự lexical retrieval và trọng số token được học từ mô hình.

## 10.3. Exact/Structured Search

Dành cho dữ liệu cần matching chính xác:

- CAS number;
- model;
- HS code;
- voltage;
- power;
- dimension;
- chemical formula.

---

# 11. Fusion Retrieval

Các nguồn ranking được hợp nhất.

Khuyến nghị:

\[
RRF(d)=\sum_i\frac{1}{k+rank_i(d)}
\]

Pipeline:

```text
Dense Results
Sparse Results
Exact Results
     ↓
    RRF
     ↓
 Top Candidates
     ↓
   Reranker
     ↓
 Final Evidence
```

---

# 12. Legal Versioning

Một hệ thống RAG pháp lý không chỉ cần nội dung.

Nó phải biết:

```text
Văn bản nào?
Ban hành ngày nào?
Hiệu lực từ ngày nào?
Hết hiệu lực khi nào?
Bị thay thế bởi văn bản nào?
```

Metadata:

```text
document_no
issued_date
effective_from
effective_to
legal_status
replaces_document
amends_document
version
```

Query pháp lý cần gắn với:

```text
classification_date
```

Ví dụ:

```text
Phân loại mặt hàng tại ngày YYYY-MM-DD
```

Retriever chỉ sử dụng văn bản phù hợp tại thời điểm đó.

---

# 13. HS Code như một cây/đồ thị phân cấp

HS không được xem như một danh sách phẳng.

Hệ thống mô hình:

```text
Chapter 2 digits
     ↓
Heading 4 digits
     ↓
Subheading 6 digits
     ↓
AHTN 8 digits
```

Ví dụ:

```text
85
│
├── 8504
│   │
│   ├── 850410
│   ├── 850421
│   └── 850440
│       │
│       ├── 850440xx
│       └── 850440yy
│
└── ...
```

Mỗi node:

```text
code
level
parent_code
description
legal_notes
valid_from
valid_to
```

---

# 14. Graph Traversal Reasoning

## Mục tiêu

Không search hàng nghìn mã ở mỗi bước.

Hệ thống giảm dần không gian tìm kiếm.

```text
97 Chapters
    ↓
<= 3 Chapters
    ↓
Candidate Headings
    ↓
Candidate HS6
    ↓
Candidate AHTN8
```

---

# 15. Tầng 1 — Chapter Classification

Agent phân tích:

- vật liệu;
- chức năng;
- nguyên lý;
- mục đích;
- dạng sản phẩm.

Output:

```json
[
  {
    "chapter": "xx",
    "retrieval_score": 0.91,
    "evidence": []
  },
  {
    "chapter": "yy",
    "retrieval_score": 0.72,
    "evidence": []
  }
]
```

Chỉ giữ tối đa một số Chapter tiềm năng.

---

# 16. Tầng 2 — Heading Classification

Tại cấp 4 số, hệ thống thực hiện:

```text
Candidate Chapter
       ↓
Heading wording
       ↓
Section Notes
       ↓
Chapter Notes
       ↓
Exclusions
       ↓
GIR logic
       ↓
Valid Headings
```

GIR 1 là điểm bắt đầu.

GIR 2–5 chỉ được kích hoạt khi trường hợp sản phẩm đáp ứng điều kiện tương ứng.

GIR 3 không được dùng mặc định cho mọi sản phẩm.

---

# 17. GIR Rule Engine

Hệ thống tách:

```text
LLM semantic analysis
```

khỏi:

```text
Rule activation
```

Ví dụ:

```python
if incomplete_or_unfinished:
    activate("GIR_2A")

if mixture_or_composite:
    activate("GIR_2B")

if multiple_valid_headings:
    activate("GIR_3")

if special_packaging_case:
    activate("GIR_5")
```

Lợi ích:

- dễ audit;
- dễ test;
- giảm hallucination;
- đảm bảo logic nhất quán.

---

# 18. Tầng 3 — HS6

Sau khi xác định Heading:

```text
Heading
   ↓
Get child Subheadings
   ↓
Compare only same-level nodes
   ↓
Apply GIR 6
```

Điểm quan trọng:

> Không so sánh các phân nhóm không cùng cấp.

---

# 19. Tầng 4 — AHTN8

Sau HS6, hệ thống chỉ lấy child nodes của HS6 đó.

Ví dụ:

```text
HS6
 ├── AHTN Candidate A
 ├── AHTN Candidate B
 └── AHTN Candidate C
```

Xét các thuộc tính:

- công suất;
- điện áp;
- tần số;
- vật liệu;
- chiều dài;
- độ dày;
- thành phần;
- mục đích sử dụng;
- cấu tạo.

---

# 20. Agent 3 — Critic Agent

Critic Agent là thành phần kiểm tra chéo.

Nhiệm vụ không phải là cố đồng ý với classifier.

Nó tìm:

- exclusion;
- contradiction;
- candidate cạnh tranh;
- thiếu thông tin;
- giả định không có bằng chứng;
- áp dụng GIR sai;
- dùng văn bản không đúng hiệu lực.

Prompt logic:

```text
1. Tìm bằng chứng có thể loại candidate.
2. Kiểm tra Section Notes.
3. Kiểm tra Chapter Notes.
4. Tìm competing headings.
5. Kiểm tra GIR sequence.
6. Kiểm tra mỗi decisive attribute có evidence.
7. Liệt kê assumption chưa được chứng minh.
```

---

# 21. Supporting Evidence và Negative Evidence

RAG thông thường hay chỉ tìm bằng chứng hỗ trợ.

Hệ thống này cần cả hai loại:

```text
Supporting Evidence
+
Contradicting Evidence
```

Ví dụ:

```text
Heading A có description rất giống sản phẩm
```

nhưng:

```text
Chapter Note loại trừ loại sản phẩm đó
```

thì Candidate A phải bị loại.

Do đó:

> Legal constraint có thể thắng semantic similarity.

---

# 22. Human-in-the-Loop

AI không cố đưa ra kết quả khi dữ liệu không đủ.

Ví dụ có hai mã khác nhau do:

```text
Seamless pipe
vs
Welded pipe
```

nhưng datasheet chỉ ghi:

```text
Steel pipe
```

AI phải hỏi:

```text
"Ống này được sản xuất theo phương pháp liền mạch hay hàn?"
```

Không nên đoán.

---

# 23. Missing Decisive Attribute

Human-in-the-Loop không chỉ dựa trên confidence thấp.

Quan trọng hơn là tìm thuộc tính phân chia candidate.

Ví dụ:

```text
Candidate A:
power <= 1000 W

Candidate B:
power > 1000 W
```

Nếu `power = null`:

```text
NEED_MORE_INFORMATION
```

Question Agent sinh:

```text
"Công suất định mức của thiết bị là bao nhiêu W?"
```

---

# 24. State Machine

Workflow AI được kiểm soát bằng state.

```text
START
  ↓
EXTRACT_SPEC
  ↓
VALIDATE_SPEC
  │
  ├── missing
  │      ↓
  │   ASK_HUMAN
  │      ↓
  │   UPDATE_SPEC
  │      ↓
  └──── RESUME
  ↓
CHAPTER_SEARCH
  ↓
HEADING_REASONING
  ↓
SUBHEADING_REASONING
  ↓
AHTN_REASONING
  ↓
CRITIC
  │
  ├── conflict → REASON AGAIN
  ├── missing  → ASK_HUMAN
  └── pass
         ↓
   TAX_LOOKUP
         ↓
 HUMAN_CONFIRM
         ↓
       FINAL
```

Agent không gọi nhau tự do.

Orchestrator kiểm soát trình tự.

---

# 25. Confidence Scoring

Confidence không lấy trực tiếp từ câu trả lời LLM.

Một công thức prototype:

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

### R — Retrieval Strength

Mức độ tốt của bằng chứng retrieved.

### M — Candidate Margin

Khoảng cách candidate đầu và candidate thứ hai.

### E — Evidence Coverage

Các thuộc tính quyết định có evidence hay không.

### G — GIR Validation

Logic GIR có hợp lệ không.

### D — Data Completeness

Thông tin sản phẩm có đầy đủ không.

### K — Critic Agreement

Critic có đồng ý hoặc phát hiện conflict hay không.

---

# 26. Abstention

Một AI pháp lý tốt không cần trả lời tất cả.

Trạng thái:

```text
INSUFFICIENT_INFORMATION
NEED_MORE_INFORMATION
REQUIRES_REVIEW
RECOMMENDATION
```

Ví dụ:

```json
{
  "status": "NEED_MORE_INFORMATION",
  "candidate_codes": [
    "xxxxxxxx",
    "yyyyyyyy"
  ],
  "missing_information": [
    "alloy composition",
    "wall thickness"
  ],
  "question": "..."
}
```

---

# 27. Evidence & Citation

Mỗi đề xuất phải trả được:

```text
HS Code này dựa trên đâu?
```

Evidence có thể gồm:

- Heading description.
- Chapter Note.
- Subheading Note.
- GIR.
- Legal document.
- Manufacturer datasheet.

Ví dụ output:

```json
{
  "code": "xxxxxxxx",
  "reason": "...",
  "evidence": [
    {
      "source": "...",
      "section": "...",
      "content": "..."
    }
  ]
}
```

Không cho phép explanation không có nguồn khi kết luận phụ thuộc văn bản.

---

# 28. Tax Lookup

Thuế suất là dữ liệu xác định.

Không sử dụng:

```text
LLM memory
```

để trả thuế.

Pipeline:

```text
HS8
 ↓
Tax DB
 ↓
Tax Type
 ↓
Effective Date
 ↓
Rate
```

Kết quả:

```json
{
  "hs_code": "xxxxxxxx",
  "tax_type": "MFN",
  "rate": "...",
  "effective_from": "...",
  "source": "..."
}
```

---

# 29. Tích hợp ERPNext

ERPNext đóng vai trò hệ thống nghiệp vụ chính.

AI Service là service độc lập.

```text
ERPNext
    │
    │ REST
    ▼
AI Service
    │
    ├── LLM
    ├── PostgreSQL
    ├── pgvector
    └── Legal Knowledge Base
```

Trên Item có thể có:

```text
Technical Description
Primary Function
Material
Composition
Power
Voltage
Frequency
Dimensions

Suggested HS Code
HS Confidence
HS Status
HS AI Case ID
HS Reviewed By
HS Review Date
```

---

# 30. Luồng sử dụng

## Bước 1

Nhân viên tạo Item.

## Bước 2

Nhập hoặc upload:

- datasheet;
- thông số kỹ thuật;
- vật liệu;
- công năng.

## Bước 3

Nhấn:

```text
AI Suggest HS Code
```

## Bước 4

Agent 1 đọc và chuẩn hóa.

## Bước 5

RAG truy xuất candidate.

## Bước 6

Graph Traversal đi qua:

```text
2 → 4 → 6 → 8 digits
```

## Bước 7

Critic kiểm tra.

## Bước 8

Nếu thiếu dữ liệu:

```text
AI hỏi nhân viên
```

## Bước 9

AI trả recommendation.

## Bước 10

Nhân viên:

```text
Confirm
Reject
Request Re-analysis
```

## Bước 11

HS được lưu vào Item.

## Bước 12

ERPNext tiếp tục:

```text
PO
→ Shipment
→ Customs
→ Purchase Receipt
→ Landed Cost
→ Final Inventory Valuation
```

---

# 31. Output cuối cùng của AI

Một classification result hoàn chỉnh nên có dạng:

```json
{
  "status": "RECOMMENDATION",

  "product": {
    "name": "...",
    "primary_function": "...",
    "normalized_spec": {}
  },

  "classification": {
    "chapter": "xx",
    "heading": "xxxx",
    "subheading": "xxxxxx",
    "ahtn": "xxxxxxxx"
  },

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

  "confidence": 0.87,

  "alternatives": [
    {
      "code": "yyyyyyyy",
      "reason_rejected": "..."
    }
  ],

  "critic": {
    "status": "PASS",
    "issues": []
  },

  "evidence": [],

  "tax": {
    "type": "MFN",
    "rate": "...",
    "source": "..."
  },

  "requires_human_confirmation": true
}
```

---

# 32. Auditability

Mỗi case phải lưu:

```text
Input
↓
Normalized Spec
↓
Retrieved Documents
↓
Candidate Chapters
↓
Candidate Headings
↓
Candidate HS6
↓
Candidate AHTN8
↓
GIR Applied
↓
Rejected Candidates
↓
Critic Result
↓
Human Questions
↓
Human Answers
↓
Recommendation
↓
Human Final Decision
```

Mục tiêu:

> Có thể trả lời chính xác tại sao hệ thống đưa ra một kết quả.

---

# 33. Feedback Loop

Nếu:

```text
AI Suggested = A
Human Final = B
```

hệ thống lưu:

```json
{
  "ai_code": "A",
  "human_code": "B",
  "reason": "material type misidentified"
}
```

Dữ liệu này có thể dùng sau cho:

- evaluation;
- few-shot examples;
- retrieval cases;
- prompt improvement;
- fine-tuning khi dataset đủ lớn.

Không tự động fine-tune sau mỗi lần user sửa.

---

# 34. Đánh giá AI

Không chỉ dùng một metric accuracy.

Các metric:

```text
Chapter Accuracy
Heading Accuracy
HS6 Accuracy
HS8 Accuracy
Top-3 Recall
Retrieval Recall@K
Citation Precision
Exclusion Violation Rate
Abstention Accuracy
Human Override Rate
Latency
```

---

# 35. Tại sao đo theo tầng?

Ví dụ:

```text
Chapter Accuracy = 97%
Heading Accuracy = 93%
HS6 Accuracy = 89%
HS8 Accuracy = 84%
```

Ta biết hệ thống bắt đầu mất chính xác ở đâu.

Nếu chỉ đo HS8:

```text
Accuracy = 84%
```

sẽ khó biết module nào cần sửa.

---

# 36. Top-3 Recommendation

Vì con người vẫn xác nhận, Top-3 rất quan trọng.

Ví dụ:

```text
Top-1 HS8 Accuracy = 84%
Top-3 HS8 Recall   = 95%
```

Có nghĩa:

> Trong 95% trường hợp, mã đúng nằm trong ba candidate đầu.

Đây là metric phù hợp với hệ thống decision support.

---

# 37. Exclusion Violation Rate

Đây là metric quan trọng cho Critic Agent.

Ví dụ:

```text
Semantic search đề xuất mã A
```

nhưng:

```text
Chapter Note loại mã A
```

nếu hệ thống vẫn trả A:

```text
Exclusion Violation
```

Mục tiêu:

```text
càng gần 0 càng tốt
```

---

# 38. Ablation Study

Để chứng minh kiến trúc thực sự hiệu quả, so sánh:

```text
LLM only
     ↓
Dense RAG
     ↓
Hybrid RAG
     ↓
Hybrid + Graph
     ↓
Hybrid + Graph + Critic
     ↓
Hybrid + Graph + Critic + Human-in-the-Loop
```

Qua đó có thể trả lời:

- Hybrid có cải thiện retrieval không?
- Graph có cải thiện HS8 không?
- Critic có giảm exclusion error không?
- HITL có giảm lỗi khi thiếu dữ liệu không?

---

# 39. Giới hạn của hệ thống

Hệ thống cần công khai các giới hạn:

## 39.1. AI không phải quyết định pháp lý cuối cùng

Kết quả là:

```text
recommendation
```

không phải:

```text
automatic declaration
```

## 39.2. Phụ thuộc dữ liệu sản phẩm

Nếu datasheet thiếu:

- composition;
- manufacturing method;
- dimension;
- power;
- material;

AI có thể không phân loại được.

## 39.3. Phụ thuộc Knowledge Base

Nếu legal dataset:

- thiếu;
- cũ;
- sai phiên bản;

kết quả cũng có thể sai.

## 39.4. WCO Explanatory Notes

Cần kiểm tra quyền truy cập và licensing trước khi sử dụng toàn bộ nội dung trong production.

---

# 40. Điểm mới của hệ thống

Điểm mới không nằm ở việc chỉ dùng LLM hoặc chỉ dùng RAG.

Hệ thống kết hợp:

```text
Structured Product Understanding
+
Hierarchical Hybrid Retrieval
+
Legal Versioning
+
HS Graph Traversal
+
GIR Rule Engine
+
Critic Agent
+
Human-in-the-Loop
+
Audit Trail
```

Điều này giúp mô phỏng gần hơn quy trình tư duy phân loại hàng hóa thực tế.

---

# 41. Phát biểu mô tả đề tài AI

Có thể mô tả ngắn gọn như sau:

> Hệ thống AI đề xuất mã HS được xây dựng theo kiến trúc Multi-Agent kết hợp Hierarchical Hybrid RAG và Graph Traversal Reasoning. Thông tin sản phẩm trước tiên được Agent kỹ thuật bóc tách và chuẩn hóa thành dữ liệu có cấu trúc. Agent RAG sau đó truy xuất đồng thời mô tả HS, chú giải pháp lý, quy tắc GIR và các nguồn liên quan bằng Dense Search, Sparse Search và Exact Matching. Việc phân loại không được thực hiện trực tiếp trên toàn bộ biểu thuế mà được suy luận tuần tự qua bốn tầng Chapter 2 số, Heading 4 số, HS Subheading 6 số và AHTN 8 số. Một Critic Agent độc lập kiểm tra chú giải loại trừ, candidate cạnh tranh, tính hợp lệ của quy tắc GIR và các giả định thiếu bằng chứng. Khi xuất hiện thuộc tính quyết định chưa có trong datasheet, hệ thống kích hoạt Human-in-the-Loop và hỏi người dùng đúng thông tin cần bổ sung trước khi tiếp tục phân loại. Kết quả cuối cùng bao gồm mã HS đề xuất, classification path, bằng chứng pháp lý, mã thay thế, confidence nội bộ, thuế suất được tra từ cơ sở dữ liệu và yêu cầu người dùng xác nhận trước khi lưu vào ERPNext.

---

# 42. Kiến trúc AI cuối cùng

```text
                      PRODUCT / DATASHEET
                              │
                              ▼
                  ┌───────────────────────┐
                  │ SPECIFICATION AGENT   │
                  │                       │
                  │ Extraction            │
                  │ Normalization         │
                  │ Missing Detection     │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │ HYBRID RAG            │
                  │                       │
                  │ Dense                 │
                  │ Sparse                │
                  │ Exact                 │
                  │ Reranker              │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │ HS GRAPH TRAVERSAL    │
                  │                       │
                  │ Chapter               │
                  │ Heading               │
                  │ HS6                   │
                  │ AHTN8                 │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │ GIR RULE ENGINE       │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │ CRITIC AGENT          │
                  │                       │
                  │ Exclusion             │
                  │ Conflict              │
                  │ Negative Evidence     │
                  │ Missing Attribute     │
                  └──────────┬────────────┘
                             │
             ┌───────────────┴────────────────┐
             │                                │
       Missing/Conflict                       │ Pass
             │                                │
             ▼                                ▼
   ┌───────────────────┐              ┌───────────────────┐
   │ HUMAN-IN-THE-LOOP │              │ TAX LOOKUP        │
   └─────────┬─────────┘              └─────────┬─────────┘
             │                                  │
             └────────────────┬─────────────────┘
                              ▼
                    ┌───────────────────┐
                    │ RECOMMENDATION    │
                    │                   │
                    │ HS Code           │
                    │ Evidence          │
                    │ Confidence        │
                    │ Alternatives      │
                    │ Audit             │
                    └─────────┬─────────┘
                              │
                              ▼
                           ERPNext
```

---

# 43. Kết luận

Phần AI của đề tài được định hướng thành một **AI-assisted Customs Classification System** thay vì chatbot tổng quát.

RAG chịu trách nhiệm tìm bằng chứng.

Graph Traversal chịu trách nhiệm giới hạn không gian phân loại.

GIR Rule Engine chịu trách nhiệm ràng buộc logic.

Critic Agent chịu trách nhiệm tìm sai sót và bằng chứng phản bác.

Human-in-the-Loop chịu trách nhiệm bổ sung thông tin hoặc xác nhận các trường hợp không chắc chắn.

ERPNext chịu trách nhiệm lưu trữ dữ liệu nghiệp vụ, tiếp tục luồng mua hàng, vận chuyển, hải quan và Landed Cost.

Toàn bộ kiến trúc hướng tới ba mục tiêu chính:

1. **Tăng độ chính xác.**
2. **Có khả năng giải thích và truy vết.**
3. **Không tự động đưa ra quyết định pháp lý khi thông tin chưa đủ.**
