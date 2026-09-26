# KNOWLEDGE_BASE_SOURCES.md
## Nguồn dữ liệu tri thức hiện hành cho hệ thống AI hỗ trợ phân loại mã HS

> **Project:** ERPNext + AI-assisted Customs Classification  
> **AI Architecture:** Multi-Agent + Hierarchical Hybrid RAG + HS Graph Traversal + GIR Rule Engine + Critic Agent + Human-in-the-Loop  
> **Ngày rà soát:** 25/09/2026  
> **Nguyên tắc:** Chỉ sử dụng nguồn **còn hiệu lực, đang áp dụng hoặc có giá trị trực tiếp cho phân loại hiện hành tại Việt Nam**. Không đưa văn bản đã bị thay thế, nguồn chỉ có giá trị lịch sử hoặc nguồn nước ngoài không ràng buộc tại Việt Nam vào Knowledge Base hiện hành.

---

# 1. Mục tiêu

Knowledge Base phục vụ 4 nhiệm vụ chính:

1. Hiểu chính xác thông số kỹ thuật của hàng hóa.
2. Phân loại theo cấu trúc HS/AHTN từ 2 → 4 → 6 → 8 số.
3. Áp dụng đúng GIR và các chú giải pháp lý.
4. Truy xuất bằng chứng pháp lý và case chính thức để giải thích/kiểm tra kết quả.

Knowledge Base **không phải** là thư mục chứa toàn bộ văn bản hải quan.

Chỉ ingest dữ liệu thật sự cần cho AI:

```text
CURRENT LEGAL CORE
+
CURRENT HS/AHTN STRUCTURE
+
OFFICIAL CLASSIFICATION GUIDANCE
+
CURRENT VIETNAM CUSTOMS CASES
+
PRODUCT TECHNICAL EVIDENCE
+
CURRENT TARIFF DATA
```

---

# 2. Nguyên tắc loại bỏ dữ liệu

Không đưa vào Knowledge Base hiện hành các nguồn sau:

- văn bản đã bị thay thế toàn bộ;
- văn bản đã hết hiệu lực;
- văn bản chỉ phục vụ tra cứu lịch sử;
- phiên bản HS cũ không dùng cho phân loại hiện hành;
- bảng tương quan HS chỉ phục vụ chuyển đổi phiên bản;
- nguồn nước ngoài không có giá trị ràng buộc tại Việt Nam;
- blog, forum, website tra mã thương mại;
- tài liệu WCO không có quyền sử dụng hợp lệ;
- mức thuế cũ đã bị sửa đổi/thay thế.

Đối với văn bản **hết hiệu lực một phần**, không ingest nguyên văn như nguồn hiện hành. Chỉ sử dụng:

```text
phần còn hiệu lực
+
nội dung sửa đổi hiện hành
```

hoặc văn bản hợp nhất/chuyển đổi thành dữ liệu hiện hành trước khi index.

---

# 3. Phân cấp nguồn

## P0 — Nguồn quyết định phân loại

Nguồn AI phải ưu tiên cao nhất:

- Danh mục hàng hóa XNK Việt Nam hiện hành.
- HS 2022.
- GIR.
- Section Notes.
- Chapter Notes.
- Subheading Notes.
- AHTN 2022/Vietnam 8-digit.
- Thông tư 85/2026/TT-BTC.

Các nguồn này có thể trực tiếp làm thay đổi hoặc loại bỏ một candidate HS.

---

## P1 — Nguồn giải thích/case chính thức

Dùng để hỗ trợ khi nguồn P0 chưa đủ để chốt một mã duy nhất:

- WCO Explanatory Notes.
- WCO Classification Opinions.
- WCO Classification Decisions hiện hành.
- AHTN Supplementary Explanatory Notes.
- thông báo xác định trước mã số của Hải quan Việt Nam;
- thông báo kết quả phân tích/phân loại;
- kết quả kiểm tra/đánh giá tiêu chí kỹ thuật;
- quyết định giải quyết khiếu nại về phân loại nếu còn giá trị và liên quan.

---

## P2 — Nguồn kỹ thuật sản phẩm

Dùng để xác định đặc tính thật của hàng hóa:

- Manufacturer Datasheet.
- Catalogue/Manual.
- SDS/MSDS.
- BOM.
- Material Certificate / Certificate of Analysis.
- Laboratory Report.
- Technical Drawing.
- PubChem đối với hóa chất.

Nguồn P2 không tự quyết định HS Code.

---

# 4. Namespace hiện hành

```text
hs_core
ahtn_vn
gir_rules
legal_notes
legal_classification
classification_guidance
classification_cases_vn
customs_procedure
tariff_current
trade_controls
product_knowledge
chemical_knowledge
```

Không sử dụng các namespace:

```text
historical_versions
classification_cases_external
hs_old_versions
```

trong Knowledge Base phục vụ phân loại hiện hành.

---

# 5. Bảng nguồn chính thức cần sử dụng

| ID | Nguồn | Trạng thái | Priority | Namespace | Có dùng cho HS reasoning? |
|---|---|---|---|---|---|
| VN-01 | Thông tư 85/2026/TT-BTC | Hiện hành từ 15/09/2026 | P0 | `legal_classification` | Có |
| VN-02 | Thông tư 31/2022/TT-BTC + Danh mục XNK Việt Nam | Còn hiệu lực | P0 | `ahtn_vn` | Có |
| VN-03 | Luật Hải quan hiện hành sau các sửa đổi | Hiện hành một phần sau sửa đổi | P0/P1 | `customs_procedure` | Chỉ nền pháp lý/thủ tục |
| VN-04 | Nghị định 08/2015/NĐ-CP đã cập nhật các sửa đổi hiện hành, gồm NĐ 167/2025 | Còn hiệu lực sau sửa đổi | P0/P1 | `customs_procedure` | Chỉ thủ tục/xác định trước |
| VN-05 | Thông tư 121/2025/TT-BTC | Còn hiệu lực từ 01/02/2026 | P1 | `customs_procedure` | Không dùng để chọn Heading |
| VN-06 | Biểu thuế hiện hành được chuẩn hóa từ NĐ 26/2023 và các sửa đổi còn hiệu lực | Hiện hành theo từng dòng thuế | P0 dữ liệu | `tariff_current` | Không; dùng lookup sau HS |
| VN-07 | Thông báo xác định trước mã số còn giá trị | Theo từng quyết định/case | P1 | `classification_cases_vn` | Có, dạng case evidence |
| VN-08 | Thông báo kết quả phân tích/phân loại hiện hành | Theo từng case | P1 | `classification_cases_vn` | Có |
| VN-09 | Kết quả kiểm tra/đánh giá tiêu chí kỹ thuật | Theo từng case | P1 | `classification_cases_vn` | Có |
| VN-10 | Danh mục quản lý chuyên ngành hiện hành | Theo từng bộ/ngành | P1 | `trade_controls` | Sau khi có HS |
| WCO-01 | HS Nomenclature 2022 | Hiện hành cho HS 2022 | P0 | `hs_core` | Có |
| WCO-02 | General Rules for Interpretation | Hiện hành | P0 | `gir_rules` | Có |
| WCO-03 | Section/Chapter/Subheading Notes | Hiện hành theo HS 2022 | P0 | `legal_notes` | Có |
| WCO-04 | Explanatory Notes | Hiện hành theo edition, có license | P1 | `classification_guidance` | Có |
| WCO-05 | Classification Opinions | Hiện hành theo edition, có license | P1 | `classification_guidance` | Có |
| WCO-06 | Classification Decisions hiện hành | Official/public | P1 | `classification_guidance` | Có |
| ASEAN-01 | AHTN 2022 | Hiện hành tại ASEAN/VN | P0 | `ahtn_vn` | Có |
| ASEAN-02 | AHTN Supplementary Explanatory Notes | Hiện hành theo AHTN 2022 | P1 | `classification_guidance` | Có |
| PROD-01 | Manufacturer Datasheet | Theo sản phẩm | P2 | `product_knowledge` | Xác định facts |
| PROD-02 | SDS/MSDS | Theo sản phẩm | P2 | `product_knowledge` | Xác định facts |
| PROD-03 | BOM | Theo sản phẩm | P2 | `product_knowledge` | Xác định facts |
| PROD-04 | Material Certificate / COA / Lab report | Theo sản phẩm | P2 | `product_knowledge` | Xác định facts |
| PROD-05 | Technical Drawing | Theo sản phẩm | P2 | `product_knowledge` | Xác định facts |
| CHEM-01 | PubChem | Current technical reference | P2 | `chemical_knowledge` | Chỉ normalize hóa chất |

---

# 6. VN-01 — Thông tư 85/2026/TT-BTC

## Trạng thái

```text
Ban hành: 30/06/2026
Hiệu lực: 15/09/2026
Trạng thái dùng trong hệ thống: CURRENT
```

Nguồn chính thức:

```text
https://vanban.chinhphu.vn/?classid=1&docid=218770&pageid=27160
```

## Vai trò

Đây là văn bản trung tâm cho lớp AI phân loại hiện hành.

Dùng để xác định:

- nguyên tắc phân loại;
- căn cứ phân loại;
- quy trình phân tích;
- nguồn dữ liệu hỗ trợ phân loại;
- cách sử dụng cơ sở dữ liệu;
- vai trò của Chú giải chi tiết HS;
- vai trò của ý kiến phân loại WCO;
- vai trò của AHTN;
- vai trò của các kết quả phân loại/xác định trước.

## Priority

```text
P0
```

## Namespace

```text
legal_classification
```

## Chunking

```text
Document
└── Chapter
    └── Article
        └── Clause
            └── Point
```

## Metadata

```json
{
  "document_no": "85/2026/TT-BTC",
  "authority": "Bộ Tài chính",
  "jurisdiction": "VN",
  "issued_date": "2026-06-30",
  "effective_from": "2026-09-15",
  "legal_status": "CURRENT",
  "priority": "P0"
}
```

---

# 7. VN-02 — Thông tư 31/2022/TT-BTC và Danh mục hàng hóa XNK Việt Nam

## Trạng thái

CSDL quốc gia về VBPL hiện ghi:

```text
Hiệu lực: Còn hiệu lực
Ngày có hiệu lực: 01/12/2022
```

Nguồn:

```text
https://vbpl.vn/TW/Pages/ivbpq-toanvan.aspx?ItemID=155207
```

## Vai trò

Đây là nguồn chính để xây cây:

```text
Section
 ↓
Chapter 2-digit
 ↓
Heading 4-digit
 ↓
HS Subheading 6-digit
 ↓
AHTN/Vietnam 8-digit
```

## Priority

```text
P0
```

## Namespace

```text
ahtn_vn
```

## Cách lưu

Không lưu nguyên văn thành một vector lớn.

Schema node:

```json
{
  "code": "85044090",
  "level": 8,
  "parent_code": "850440",
  "description_vi": "...",
  "section": "XVI",
  "chapter": "85",
  "heading": "8504",
  "hs6": "850440",
  "ahtn8": "85044090",
  "source_document": "31/2022/TT-BTC"
}
```

---

# 8. VN-03 — Luật Hải quan hiện hành

## Lưu ý trạng thái

Luật Hải quan 54/2014/QH13 hiện được CSDL quốc gia ghi là:

```text
Hết hiệu lực một phần
```

và đã được sửa đổi nhiều lần, trong đó có Luật 90/2025/QH15 có hiệu lực từ 01/07/2025.

Do đó:

> Không ingest toàn bộ bản gốc 54/2014/QH13 như một văn bản hiện hành độc lập.

## Cách sử dụng đúng

Tạo corpus:

```text
CUSTOMS LAW — CURRENT EFFECTIVE TEXT
```

bằng cách sử dụng:

- phần Luật Hải quan còn hiệu lực;
- các điều đã được sửa đổi theo văn bản hiện hành;
- văn bản hợp nhất chính thức nếu có.

## Namespace

```text
customs_procedure
```

## Agent sử dụng

Chỉ sử dụng cho:

- cơ sở pháp lý chung;
- quyền/nghĩa vụ khai hải quan;
- xác định trước;
- yêu cầu hồ sơ/tài liệu;
- quy trình nghiệp vụ.

Không sử dụng corpus này để semantic-search candidate Heading.

---

# 9. VN-04 — Nghị định 08/2015/NĐ-CP sau sửa đổi

## Trạng thái

CSDL quốc gia ghi Nghị định 08/2015/NĐ-CP:

```text
Còn hiệu lực
```

Nghị định 167/2025/NĐ-CP sửa đổi NĐ08 và có hiệu lực:

```text
15/08/2025
```

Nguồn NĐ08:

```text
https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=48921
```

Nguồn NĐ167:

```text
https://vanban.chinhphu.vn/?classid=1&docid=214375&pageid=27160
```

## Cách ingest

Không tạo hai corpus cạnh tranh:

```text
NĐ08 original
NĐ167 amendment
```

cho retrieval.

Thay vào đó tạo:

```text
ND08_CURRENT
```

là nội dung NĐ08 sau khi áp dụng các sửa đổi còn hiệu lực.

## Namespace

```text
customs_procedure
```

## Vai trò

- xác định trước mã số;
- thủ tục hải quan;
- kiểm tra/phân tích;
- hồ sơ;
- phạm vi giá trị của quyết định xác định trước.

---

# 10. VN-05 — Thông tư 121/2025/TT-BTC

## Trạng thái

```text
Còn hiệu lực
Hiệu lực từ: 01/02/2026
```

Nguồn:

```text
https://vbpl.vn/botuphap/Pages/vbpq-thuoctinh.aspx?ItemID=186329
```

## Có cần không?

Có, nhưng không phải HS classification core.

## Namespace

```text
customs_procedure
```

## Sử dụng

- thủ tục;
- kiểm tra;
- đánh giá tiêu chí;
- thuế và quản lý thuế liên quan XNK.

Không route vào:

```text
Chapter Retriever
Heading Retriever
HS6 Retriever
```

---

# 11. VN-06 — Biểu thuế hiện hành

## Nguồn gốc

Nghị định 26/2023/NĐ-CP là nền của Biểu thuế nhưng CSDL quốc gia hiện ghi:

```text
Hết hiệu lực một phần
```

vì đã được sửa đổi nhiều lần.

Nguồn lịch sử pháp lý:

```text
https://vbpl.vn/botaichinh/Pages/vbpq-lichsu.aspx?ItemID=160629
```

## Quy tắc quan trọng

Không đưa PDF NĐ26 nguyên bản vào RAG rồi để LLM trả thuế.

Phải xây:

```text
CURRENT TARIFF TABLE
```

được tính từ:

```text
NĐ26
+
tất cả sửa đổi còn hiệu lực
```

## Schema

```text
hs_code
tax_type
rate
unit
effective_from
effective_to
source_document
```

## Namespace

```text
tariff_current
```

## Cách truy vấn

```sql
SELECT rate
FROM tariff_rate
WHERE hs_code = :hs_code
  AND tax_type = :tax_type
  AND effective_from <= :date
  AND (effective_to IS NULL OR effective_to >= :date);
```

Đây là deterministic lookup, không phải RAG reasoning.

---

# 12. VN-07 — Thông báo xác định trước mã số

## Chỉ ingest case còn giá trị

Mỗi case cần kiểm tra:

```text
decision_date
valid_until
legal_basis
product_identity
case_status
```

Không ingest một case đã hết giá trị như nguồn hiện hành.

## Namespace

```text
classification_cases_vn
```

## Priority

```text
P1
```

## Schema

```json
{
  "case_type": "advance_ruling",
  "decision_no": "...",
  "decision_date": "...",
  "valid_until": "...",
  "case_status": "CURRENT",
  "product": {
    "name": "...",
    "model": "...",
    "material": [],
    "composition": [],
    "function": "...",
    "technical_specs": {}
  },
  "final_hs": "xxxxxxxx",
  "legal_basis": []
}
```

## Sử dụng

Case-Based RAG.

Case không được biến thành universal rule.

---

# 13. VN-08 — Kết quả phân tích/phân loại

## Điều kiện ingest

Chỉ sử dụng khi:

- nguồn là Hải quan Việt Nam/cơ quan có thẩm quyền;
- xác định được ngày;
- xác định được hàng hóa;
- xác định được mã cuối cùng;
- legal basis không bị thay đổi theo cách làm case mất giá trị tham khảo.

## Namespace

```text
classification_cases_vn
```

## Vai trò

Rất phù hợp cho:

```text
Classifier Agent
Critic Agent
Case Retriever
```

---

# 14. VN-09 — Kết quả kiểm tra/đánh giá tiêu chí kỹ thuật

## Vai trò

Đặc biệt cần với hàng mà phân nhóm phụ thuộc:

```text
power
voltage
frequency
carbon %
alloy %
fiber %
composition
thickness
diameter
length
manufacturing method
```

## Lưu dữ liệu có cấu trúc

```json
{
  "attribute": "rated_power",
  "value": 800,
  "unit": "W",
  "source": "official_technical_assessment"
}
```

---

# 15. VN-10 — Danh mục quản lý chuyên ngành hiện hành

## Mục đích

Không dùng để chọn HS.

Dùng sau khi xác định HS:

```text
HS
 ↓
Trade-control lookup
 ↓
license?
inspection?
prohibition?
specialized management?
```

## Namespace

```text
trade_controls
```

## Điều kiện

Chỉ ingest danh mục:

- đang còn hiệu lực;
- từ bộ/ngành chính thức;
- có mapping HS hoặc tiêu chí hàng hóa rõ ràng.

---

# 16. WCO-01 — HS Nomenclature 2022

Nguồn chính thức:

```text
https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition
```

## Priority

```text
P0
```

## Namespace

```text
hs_core
```

## Data model

```text
Section
→ Chapter
→ Heading
→ Subheading
```

Không xem HS như một flat list.

---

# 17. WCO-02 — General Rules for Interpretation

Nguồn:

```text
https://www.wcotradetools.org/en/harmonized-system/rules
```

## Priority

```text
P0
```

## Namespace

```text
gir_rules
```

## Lưu dạng machine-readable

Ví dụ:

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

---

# 18. WCO-03 — Legal Notes

Bao gồm:

```text
Section Notes
Chapter Notes
Subheading Notes
```

## Priority

```text
P0
```

## Namespace

```text
legal_notes
```

## Schema

```json
{
  "scope_type": "chapter",
  "scope_code": "85",
  "note_number": "3",
  "note_type": "exclusion",
  "content": "...",
  "hs_edition": 2022
}
```

Legal Notes là hard constraint.

```text
high semantic similarity
+
legal exclusion
=
REJECT CANDIDATE
```

---

# 19. WCO-04 — Explanatory Notes

Nguồn thông tin:

```text
https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/tools-to-assist-with-the-classification-in-the-hs/explanatory-notes.aspx
```

## Priority

```text
P1
```

## Namespace

```text
classification_guidance
```

## Điều kiện sử dụng

Chỉ ingest full dataset khi có license/quyền sử dụng hợp lệ.

Không scrape trái phép.

## Vai trò

- phạm vi heading;
- inclusion;
- exclusion;
- technical description;
- manufacturing method;
- use;
- identification guidance.

---

# 20. WCO-05 — Classification Opinions

## Priority

```text
P1
```

## Namespace

```text
classification_guidance
```

## Điều kiện

Chỉ sử dụng full Compendium nếu có license phù hợp.

## Vai trò

Case reasoning chính thức của WCO cho các tình huống phân loại khó.

---

# 21. WCO-06 — Classification Decisions hiện hành

Nguồn:

```text
https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/tools-to-assist-with-the-classification-in-the-hs/hs_classification-decisions/classification-decisions.aspx
```

## Priority

```text
P1
```

## Namespace

```text
classification_guidance
```

## Update

```text
MONTHLY
```

hoặc khi WCO công bố session mới.

## Chỉ giữ

Các decision phù hợp với HS edition đang sử dụng hoặc đã được map/xác minh còn liên quan.

---

# 22. ASEAN-01 — AHTN 2022

Nguồn:

```text
https://asean.org/our-communities/economic-community/asean-customs/
```

## Priority

```text
P0
```

## Namespace

```text
ahtn_vn
```

## Vai trò

Mở rộng:

```text
HS6
 ↓
AHTN8
```

để phục vụ phân loại cấp 8 số tại Việt Nam.

---

# 23. ASEAN-02 — AHTN Supplementary Explanatory Notes

## Priority

```text
P1
```

## Namespace

```text
classification_guidance
```

## Vai trò

Giải thích thêm việc phân loại ở tầng AHTN.

Chỉ sử dụng edition phù hợp AHTN 2022 đang áp dụng.

---

# 24. Product Knowledge

Đây là input chính của Agent 1.

## Nguồn được sử dụng

```text
Manufacturer Datasheet
Catalogue
Manual
SDS/MSDS
BOM
Material Certificate
Certificate of Analysis
Laboratory Report
Technical Drawing
```

## Priority

```text
P2
```

## Namespace

```text
product_knowledge
```

## Nguyên tắc nguồn

Ưu tiên:

```text
manufacturer/lab evidence
```

cao hơn:

```text
seller description
marketing description
```

---

# 25. Manufacturer Datasheet schema

```json
{
  "manufacturer": "...",
  "model": "...",
  "product_name": "...",
  "primary_function": "...",
  "operating_principle": "...",
  "materials": [],
  "composition": [],
  "dimensions": {},
  "electrical": {},
  "capacity": {},
  "intended_use": "...",
  "standards": []
}
```

Mỗi fact phải có evidence pointer:

```json
{
  "field": "rated_power",
  "raw_value": "0.8 kW",
  "normalized_value": 800,
  "unit": "W",
  "page": 3,
  "evidence": "..."
}
```

---

# 26. SDS/MSDS

Dùng cho:

```text
chemicals
mixtures
industrial preparations
```

Fields:

```text
chemical_name
CAS
composition
percentage
physical_form
intended_use
```

---

# 27. BOM

Dùng để phát hiện:

```text
multi-material goods
composite goods
essential component
component function
```

Hữu ích cho GIR 2/GIR 3.

---

# 28. Material Certificate / COA / Laboratory Report

Đặc biệt cần cho:

```text
steel
alloys
chemicals
polymers
textiles
```

Fields:

```text
material_grade
element
percentage
test_method
standard
certificate_no
```

---

# 29. Technical Drawing

Dùng để lấy:

```text
length
diameter
thickness
geometry
assembly
component relationship
```

Các kích thước có tính quyết định phải được Human-in-the-Loop xác nhận nếu extraction không chắc chắn.

---

# 30. PubChem

Nguồn:

```text
https://pubchem.ncbi.nlm.nih.gov/
```

## Namespace

```text
chemical_knowledge
```

## Sử dụng

Chỉ để chuẩn hóa:

```text
chemical name
synonym
molecular formula
identifier
chemical properties
```

Không dùng PubChem để kết luận HS.

---

# 31. Knowledge Base không sử dụng nguồn lịch sử

Knowledge Base hiện hành **không ingest**:

```text
old legal classification circulars
old HS editions
old tariff rows
expired advance rulings
expired classification decisions
```

Nếu tương lai cần chức năng:

```text
"phân loại tại ngày trong quá khứ"
```

thì xây một database lịch sử riêng, không trộn với current production RAG.

---

# 32. Legal validity là hard filter

Retrieval pipeline:

```text
Query
 ↓
CURRENT-LAW FILTER
 ├─ jurisdiction = VN
 ├─ legal_status = CURRENT
 ├─ HS edition = 2022
 ├─ AHTN edition = 2022
 ├─ valid_on classification_date
 └─ license_allowed = true
 ↓
Hybrid Search
 ↓
Reranker
```

Không cho phép:

```text
expired document similarity = 0.99
→ thắng current law
```

---

# 33. Source priority trong reranking

```text
P0 = binding/current legal core
P1 = official classification guidance/cases
P2 = technical product evidence
```

Không có P3/P4 trong current Knowledge Base.

---

# 34. Source conflict policy

Nếu có xung đột:

```text
Current P0 legal source
    >
P1 official guidance/case
    >
P2 technical enrichment
```

Ngoài ra:

```text
Legal Note
    >
semantic similarity

Current law
    >
old decision

Vietnam binding source
    >
general analogy
```

---

# 35. Cấu trúc thư mục mới

```text
knowledge-base/
│
├── raw/
│   ├── vietnam/
│   │   ├── current_classification_law/
│   │   ├── current_hs_ahtn/
│   │   ├── current_customs_procedure/
│   │   ├── current_tariff/
│   │   ├── current_classification_cases/
│   │   └── current_trade_controls/
│   │
│   ├── wco/
│   │   ├── hs_2022/
│   │   ├── legal_notes/
│   │   ├── explanatory_notes/
│   │   ├── classification_opinions/
│   │   └── classification_decisions/
│   │
│   ├── asean/
│   │   ├── ahtn_2022/
│   │   └── supplementary_notes/
│   │
│   └── product/
│       ├── datasheets/
│       ├── sds/
│       ├── bom/
│       ├── certificates/
│       ├── lab_reports/
│       └── drawings/
│
├── parsed/
├── normalized/
├── chunks/
├── structured/
└── manifests/
```

Không có thư mục:

```text
historical/
external_rulings/
old_hs/
```

trong current production corpus.

---

# 36. Source manifest

```json
{
  "source_id": "VN-TT85-2026",
  "title": "Thông tư 85/2026/TT-BTC",
  "authority": "Bộ Tài chính",
  "source_url": "...",
  "legal_status": "CURRENT",
  "effective_from": "2026-09-15",
  "downloaded_at": "...",
  "sha256": "...",
  "format": "pdf",
  "ingest_status": "VALIDATED"
}
```

---

# 37. Ingestion gate

Chỉ tài liệu đạt tất cả điều kiện mới được embedding:

- [ ] Nguồn chính thức.
- [ ] Xác minh trạng thái hiện hành.
- [ ] Không bị thay thế toàn bộ.
- [ ] Nếu sửa đổi một phần, đã hợp nhất phần hiện hành.
- [ ] Có effective date.
- [ ] Có authority.
- [ ] Có source URL.
- [ ] Có hash.
- [ ] Có namespace.
- [ ] Có source priority.
- [ ] Có license hợp lệ.
- [ ] Parse đúng cấu trúc.
- [ ] Không mất bảng/mã HS.
- [ ] Human spot-check pass.

---

# 38. Pipeline ingest pháp lý

```text
Official source
      ↓
Check CURRENT status
      ↓
Check amendments/replacement
      ↓
Build current effective text
      ↓
SHA-256
      ↓
Parse hierarchy
      ↓
Metadata
      ↓
Validation
      ↓
Chunk
      ↓
Embedding/index
```

Nếu:

```text
REPLACED / EXPIRED
```

thì:

```text
STOP → DO NOT INGEST
```

---

# 39. Pipeline HS/AHTN

```text
Current VN nomenclature
       +
HS 2022
       +
AHTN 2022
       ↓
Validate codes
       ↓
Build hierarchy
       ↓
Attach legal notes
       ↓
Relational/graph DB
       ↓
Textual chunks
       ↓
Hybrid search index
```

---

# 40. Pipeline classification case

```text
Official Customs case
       ↓
Check case validity/relevance
       ↓
Extract product facts
       ↓
Extract HS result
       ↓
Extract legal basis
       ↓
Normalize technical facts
       ↓
Map HS node
       ↓
Case DB
       ↓
Case embedding
```

Expired/non-relevant case:

```text
DO NOT INGEST CURRENT CASE INDEX
```

---

# 41. Pipeline tariff

```text
Base tariff regulation
       +
all current amendments
       ↓
Resolve effective rows
       ↓
Create current tariff table
       ↓
SQL lookup
```

Không embedding tariff rate để LLM suy luận.

---

# 42. Retrieval routing

## Chapter

Search:

```text
hs_core
legal_notes
product_knowledge
```

## Heading

Search:

```text
hs_core
legal_notes
classification_guidance
classification_cases_vn
```

## HS6

Search:

```text
hs_core
legal_notes
classification_guidance
```

## AHTN8

Search:

```text
ahtn_vn
classification_guidance
classification_cases_vn
product_knowledge
```

## Customs procedure question

Search:

```text
legal_classification
customs_procedure
```

## Tax

Use:

```text
tariff_current
```

SQL/structured query only.

---

# 43. Minimum Knowledge Base cho MVP

## Bắt buộc

- [ ] TT 85/2026/TT-BTC.
- [ ] TT 31/2022/TT-BTC + full current Vietnam nomenclature.
- [ ] HS 2022.
- [ ] GIR 1–6.
- [ ] Section Notes.
- [ ] Chapter Notes.
- [ ] Subheading Notes.
- [ ] AHTN 2022.
- [ ] Current NĐ08 content after amendments relevant to classification/advance ruling.
- [ ] Current tariff table.
- [ ] 100+ current/relevant Vietnam Customs classification cases.
- [ ] Manufacturer technical documents for demo products.

## Nâng cao

- [ ] WCO Explanatory Notes licensed.
- [ ] WCO Classification Opinions licensed.
- [ ] AHTN Supplementary Explanatory Notes.
- [ ] Current trade-control lists.

---

# 44. Các nguồn đã loại khỏi thiết kế hiện hành

Các loại nguồn sau không còn được sử dụng trong current Knowledge Base:

```text
văn bản phân loại đã bị TT85/2026 thay thế
văn bản chỉ dùng cho giai đoạn lịch sử
HS edition cũ
HS correlation tables
HS 2028/future mappings
foreign tariff rulings
expired tariff rows
expired advance rulings
non-binding web classifications
blog/forum/SEO sources
```

Mục tiêu là:

> Current AI chỉ reasoning trên corpus pháp lý và dữ liệu kỹ thuật có giá trị hiện hành.

---

# 45. URL registry

## Việt Nam

### TT 85/2026/TT-BTC

```text
https://vanban.chinhphu.vn/?classid=1&docid=218770&pageid=27160
```

### TT 31/2022/TT-BTC

```text
https://vbpl.vn/TW/Pages/ivbpq-toanvan.aspx?ItemID=155207
```

### NĐ 08/2015/NĐ-CP

```text
https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=48921
```

### NĐ 167/2025/NĐ-CP

```text
https://vanban.chinhphu.vn/?classid=1&docid=214375&pageid=27160
```

### TT 121/2025/TT-BTC

```text
https://vbpl.vn/botuphap/Pages/vbpq-thuoctinh.aspx?ItemID=186329
```

### Luật 90/2025/QH15

```text
https://vanban.chinhphu.vn/?docid=214558&pageid=27160
```

### NĐ 26/2023/NĐ-CP — lịch sử sửa đổi

```text
https://vbpl.vn/botaichinh/Pages/vbpq-lichsu.aspx?ItemID=160629
```

---

## WCO

### HS 2022

```text
https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition
```

### GIR

```text
https://www.wcotradetools.org/en/harmonized-system/rules
```

### Explanatory Notes

```text
https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/tools-to-assist-with-the-classification-in-the-hs/explanatory-notes.aspx
```

### Classification Decisions

```text
https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/tools-to-assist-with-the-classification-in-the-hs/hs_classification-decisions/classification-decisions.aspx
```

---

## ASEAN

```text
https://asean.org/our-communities/economic-community/asean-customs/
```

---

## Product/Chemical

```text
https://pubchem.ncbi.nlm.nih.gov/
```

---

# 46. Kiến trúc Knowledge Base sau khi làm sạch

```text
                    CURRENT KNOWLEDGE BASE
                            │
         ┌──────────────────┼───────────────────┐
         │                  │                   │
         ▼                  ▼                   ▼
     LEGAL CORE          HS/AHTN             CASES
         │                  │                   │
    TT85/2026          HS 2022            VN Customs
    Current Law        GIR                WCO Decisions
    Current NĐ08       Notes              WCO Opinions
                       AHTN 2022           WCO EN
         │                  │                   │
         └──────────────────┼───────────────────┘
                            │
                            ▼
                   PRODUCT KNOWLEDGE
                            │
        Datasheet / SDS / BOM / Lab / Certificate
                            │
                            ▼
                  TECHNICAL NORMALIZATION
                            │
                            ▼
                      AI AGENTS
```

---

# 47. Nguyên tắc cuối cùng

Knowledge Base production chỉ chứa:

```text
CURRENT
AUTHORITATIVE
RELEVANT
TRACEABLE
LICENSED
```

Mỗi kết luận của AI phải truy ngược được:

```text
Recommendation
→ Reasoning
→ Evidence
→ Current source
→ Effective provision
→ Official URL
```

Không dùng văn bản hết hiệu lực chỉ vì semantic similarity cao.

Không dùng case hết giá trị như universal rule.

Không dùng tariff cũ.

Không dùng nguồn nước ngoài không ràng buộc để chốt HS Việt Nam.

Không dùng blog/forum làm bằng chứng pháp lý.

Đây là baseline dữ liệu cho hệ thống AI HS Code hiện hành.
