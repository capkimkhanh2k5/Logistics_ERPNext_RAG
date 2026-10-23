# Lộ Trình Tích Hợp Và Kế Hoạch Triển Khai: Trade Case Overview

> **Tài liệu định hướng nghiệp vụ & kỹ thuật**  
> **Dự án**: Logistics Wizard — Hệ sinh thái Quản trị Chuỗi cung ứng Xuất Nhập Khẩu trên nền tảng ERPNext / Frappe  
> **Vị trí tài liệu**: `todoTradeCase.md`  
> **Trạng thái**: Đã dựng xong khung giao diện Unified Desk Page (Trade Case Overview + Shipment Tracking Hub) & Doctype Trade Case. Sẵn sàng tích hợp khi các module nghiệp vụ con hoàn tất.

---

## 1. Mục Đích & Nguyên Tắc Thiết Kế Cốt Lõi

1. **Hồ sơ điều hành trung tâm (Central Operating Dossier)**:
   - `Trade Case` là đối tượng trung tâm quản lý một lô hàng xuất/nhập khẩu xuyên suốt từ Purchase Order (PO) / Sales Order (SO) đến khi hàng nhập kho và chốt toàn bộ chi phí (Landed Cost).
   - Trang **Trade Case Overview** đóng vai trò là "màn hình buồng lái điều hành", tổng hợp trạng thái đa chiều và hỗ trợ drill-down sâu vào từng module chuyên biệt.
2. **Nguyên tắc "Không trùng lặp dữ liệu" (Zero Data Duplication)**:
   - `Trade Case` **không** lưu lại các thông tin chi tiết đã thuộc quyền sở hữu của các module con (như tọa độ GPS, ngày ETA chi tiết của từng trạm trung chuyển, từng dòng chi phí hóa đơn lẻ, danh sách tệp đính kèm scan...).
   - `Trade Case` chỉ lưu thông tin cấp Master (Case ID, Type, Partner, Owner, Current Stage, Health, Priority, Stage-Gate status) và các khóa liên kết (Link Reference). Dữ liệu hiển thị trên Overview được tổng hợp theo thời gian thực (On-the-fly aggregation) thông qua API backend.
3. **8 Câu hỏi sống còn Trade Case Overview phải trả lời trong vài giây**:
   1. *Đây là lô hàng nào?* (Header Identification)
   2. *Nó đang ở giai đoạn nào trong toàn bộ vòng đời?* (Lifecycle Stepper)
   3. *Vận chuyển quốc tế có đúng tiến độ không?* (Shipment Summary)
   4. *Hồ sơ chứng từ đã đủ để thông quan chưa?* (Document Readiness)
   5. *Hải quan & Tuân thủ đã sẵn sàng chưa?* (Customs & Compliance)
   6. *Kho bãi và nhân sự tiếp nhận đã sẵn sàng chưa?* (Warehouse Readiness)
   7. *Chi phí hiện tại thế nào so với dự toán ban đầu?* (Landed Cost Summary)
   8. *Có sự cố gì và ai đang chịu trách nhiệm xử lý?* (Exceptions & RACI Responsibility)

---

## 2. Danh Mục Các Module Liên Quan Cần Hoàn Thành Tiếp Theo

Dưới đây là 5 phân hệ chuyên sâu cần được xây dựng/tích hợp tiếp theo để cung cấp dữ liệu sống cho Trade Case Overview:

| TT | Phân Hệ / Module Con | Trách Nhiệm Cốt Lõi | Dữ Liệu Cung Cấp Cho Overview | Trạng Thái Hiện Tại |
|---|---|---|---|---|
| **M1** | **Shipment Tracking Hub** | Giám sát GPS container, hành trình hãng tàu biển/hàng không, chuẩn hóa 9 mốc DCSA quốc tế, tính toán độ trễ tự động. | ATD, ETA, Delay Days, Hãng vận chuyển, Số cont, Trạng thái chặng biển. | **ĐÃ HOÀN THÀNH** (Tích hợp tại Tab 2 của Unified Desk Page) |
| **M2** | **Document Readiness Engine** | Quản lý vòng đời chứng từ XNK: Commercial Invoice, Packing List, B/L, C/O Form E/B, D/O, Giấy phép chuyên ngành. Kiểm tra tính hợp lệ & cảnh báo hạn chót nộp hồ sơ. | Tỷ lệ % hoàn thành (x/10), cảnh báo chứng từ khẩn cấp bị thiếu (C/O, D/O), trạng thái 4 nhóm (Thương mại, Vận tải, Hải quan, Tuân thủ). | **CHỜ PHÁT TRIỂN** |
| **M3** | **Customs & RAG Compliance** | Ứng dụng AI/RAG tra cứu biểu thuế và mã HS tự động, quản lý tờ khai điện tử VNACCS/VCIS, luồng tờ khai (Xanh, Vàng, Đỏ), kiểm tra chuyên ngành. | Mã HS đã chuẩn hóa & phê duyệt, tiến độ tờ khai hải quan, phân luồng hải quan, tình trạng thông quan. | **CHỜ PHÁT TRIỂN** |
| **M4** | **Trade Cost & Landed Cost** | Thu thập hóa đơn chi phí (Freight, Duty, Port THC, Demurrage, Storage, Trucking), đối chiếu thực tế vs dự toán, tạo Landed Cost Voucher (LCV) cập nhật giá vốn hàng tồn kho ERPNext. | Trị giá hàng mua (PO Value), Chi phí dự toán, Chi phí thực tế, Độ lệch (+/-% Variance), tiến độ hóa đơn (Received/Verified/Allocated). | **CHỜ PHÁT TRIỂN** |
| **M5** | **Warehouse Receiving & Inspection** | Bố trí mặt bằng kho bãi, kiểm đếm hàng thực tế dỡ cont, lập biên bản chênh lệch số lượng (Expected vs Received, Damaged, Missing), tạo Purchase Receipt (PR) ERPNext. | Lịch dự kiến hàng về kho, tình trạng mặt bằng & nhân sự tiếp nhận kho, cảnh báo bất thường số lượng/hư hỏng. | **CHỜ PHÁT TRIỂN** |
| **M6** | **Exception & Action Management** | Động cơ phát hiện sự cố tự động (delay tàu, thiếu chứng từ, vượt ngân sách chi phí, luồng đỏ), giao việc có Owner + Hạn chót (Due Date) + Trạng thái đóng. | Danh sách Top Open Exceptions, chỉ số sức khỏe tổng hợp (Health Score), danh sách việc cần làm (Upcoming Actions & Deadlines). | **CHỜ TÍCH HỢP TẬP TRUNG** |

---

## 3. Bản Mô Tả API Interface & Data Contract

Để đảm bảo tính độc lập và khả năng mở rộng không phụ thuộc cấu trúc nội bộ của từng module, tất cả các module con khi hoàn thành sẽ giao tiếp với Trade Case thông qua các interface chuẩn sau:

### 3.1. Document Readiness Interface (`get_document_readiness_status`)
- **Caller**: Trade Case Aggregator API
- **Callee**: `logistics_wizard.document_engine.api.get_case_documents_status(case_id)`
- **Schema Payload**:
```json
{
  "ready_count": 8,
  "total_count": 10,
  "percentage": 80.0,
  "current_stage": "In Transit",
  "missing_urgent": [
    {
      "code": "DOC-CO",
      "name": "Certificate of Origin (C/O Form E)",
      "type": "critical",
      "deadline": "2026-10-05",
      "note": "Bắt buộc nộp trước khi truyền tờ khai Hải quan để hưởng thuế ưu đãi ACFTA"
    }
  ],
  "categories": [
    {"name": "Commercial", "ready": 3, "total": 3, "status": "completed"},
    {"name": "Transport", "ready": 3, "total": 3, "status": "completed"},
    {"name": "Customs", "ready": 1, "total": 2, "status": "warning"},
    {"name": "Compliance", "ready": 1, "total": 2, "status": "warning"}
  ]
}
```

### 3.2. Customs & Compliance Interface (`get_customs_compliance_status`)
- **Caller**: Trade Case Aggregator API
- **Callee**: `logistics_wizard.customs_engine.api.get_case_customs_status(case_id)`
- **Schema Payload**:
```json
{
  "status": "PREPARING",
  "readiness_pct": 70,
  "hs_classification": "8517.62.99",
  "hs_approval_status": "Approved by Customs Specialist",
  "origin_verified": true,
  "customs_value_verified": true,
  "declaration_status": "Pending (Chờ C/O gốc)",
  "declaration_no": null,
  "channel": null,
  "license": "N/A",
  "inspection": "Pending",
  "clearance_status": "NOT CLEARED"
}
```

### 3.3. Landed Cost Interface (`get_landed_cost_status`)
- **Caller**: Trade Case Aggregator API
- **Callee**: `logistics_wizard.costing_engine.api.get_case_cost_summary(case_id)`
- **Schema Payload**:
```json
{
  "purchase_value": 100000.0,
  "estimated_cost": 17000.0,
  "actual_cost": 18350.0,
  "variance_amount": 1350.0,
  "variance_pct": 7.9,
  "actual_landed_cost": 118350.0,
  "currency": "USD",
  "breakdown": [
    {"label": "Ocean Freight", "amount": 5700.0},
    {"label": "Marine Insurance", "amount": 950.0},
    {"label": "Import Duty & Taxes", "amount": 10000.0},
    {"label": "Port Handling (THC, CIC)", "amount": 700.0},
    {"label": "Storage & Demurrage", "amount": 400.0},
    {"label": "Other Surcharges", "amount": 600.0}
  ],
  "invoices_received": 7,
  "invoices_total": 9,
  "costs_verified": 6,
  "costs_allocated": 4,
  "cost_finalization_status": "IN PROGRESS"
}
```

### 3.4. Warehouse Readiness Interface (`get_warehouse_receiving_status`)
- **Caller**: Trade Case Aggregator API
- **Callee**: `logistics_wizard.warehouse_engine.api.get_case_warehouse_status(case_id)`
- **Schema Payload**:
```json
{
  "expected_arrival": "2026-10-09",
  "warehouse": "Kho Ngoại quan - WH-DANANG",
  "receiving_status": "NOT READY",
  "expected_qty": 1000,
  "received_qty": null,
  "space_reserved": true,
  "receiving_team": "Assigned (Đội Tiếp nhận Kho B)",
  "discrepancy_alert": false,
  "discrepancy_details": null
}
```

---

## 4. Kịch Bản Kiểm Thử Toàn Diện (Test Scenarios Roadmap)

Khi các module con hoàn thiện, nhóm phát triển sẽ kích hoạt 4 bộ kịch bản kiểm thử tích hợp (End-to-End Test Suite) để kiểm chứng sự phối hợp hoàn hảo:

### Kịch Bản 1: Luồng Tiêu Chuẩn Thuận Lợi (Happy Path — Healthy)
- **Tình huống**:
  - Hàng nhập khẩu từ Tokyo về Nội Bài bằng đường hàng không (`IMP-2026-002`).
  - Chuyến bay hạ cánh đúng giờ (0 delay).
  - Đầy đủ 10/10 chứng từ gốc trước khi hàng đến.
  - Tờ khai Hải quan phân Luồng Xanh, thông quan ngay trong ngày.
  - Chi phí thực tế thấp hơn hoặc bằng dự toán (-1.3%).
  - 0 sự cố phát sinh.
- **Kỳ vọng trên Overview**:
  - `Trade Case Health`: **HEALTHY** (Xanh lá).
  - Tỷ lệ hoàn thành chứng từ: 100%.
  - Tất cả các thẻ chỉ số đều có viền xanh lá (Success).
  - Stage-Gate kiểm tra điều kiện đóng case cho phép chuyển sang bước "Chốt giá thành".

### Kịch Bản 2: Lệch Lịch Trình & Chậm Hồ Sơ (Delay & Missing C/O — Attention/Warning)
- **Tình huống**:
  - Hàng đường biển từ Thượng Hải về Đà Nẵng (`IMP-2026-001`).
  - Tàu gặp bão tại eo biển Đài Loan, ETA lùi lại +2 ngày.
  - Thiếu C/O Form E gốc từ Supplier (chưa gửi chuyển phát nhanh kịp).
  - Chi phí Ocean Freight phát sinh phụ phí thời tiết vượt +7.9%.
  - Tồn tại 3 sự cố đang mở (1 sự cố mức High).
- **Kỳ vọng trên Overview**:
  - `Trade Case Health`: Tự động nhảy sang **ATTENTION** (Vàng hổ phách), tính toán tự động từ signals con, tuyệt đối không nhập tay.
  - Lifecycle Stepper: Chặng `In Transit` hiển thị viền cảnh báo kèm ghi chú "Trễ +2 ngày".
  - Thẻ Chứng từ: Hiện Callout đỏ cảnh báo "Thiếu khẩn cấp: C/O Form E (Hạn 05/10)".
  - Stage-Gate: Chặn nút [Close Case], hiển thị rõ danh sách 4 nguyên nhân chặn.

### Kịch Bản 3: Sự Cố Nghiêm Trọng Luồng Đỏ & Nguy Cơ Rớt Tàu (Critical Exception)
- **Tình huống**:
  - Lô pin năng lượng mặt trời xuất khẩu đi Los Angeles (`EXP-2026-001`).
  - Tờ khai hải quan xuất khẩu bị phân vào **Luồng Đỏ (Kiểm hóa 100%)**.
  - Thời gian kiểm hóa có nguy cơ vượt quá Closing Time của hãng tàu ONE.
  - Tồn tại sự cố mức **CRITICAL** chưa có phương án xử lý.
- **Kỳ vọng trên Overview**:
  - `Trade Case Health`: Chuyển sang **CRITICAL** (Đỏ rực).
  - Thẻ Hải quan: Đổi trạng thái sang "PHYSICAL INSPECTION (RED CHANNEL)".
  - Top Open Exceptions: Đưa sự cố kiểm hóa lên vị trí ưu tiên số 1 kèm nút phân công khẩn cấp cho Port Lead.
  - Khóa toàn bộ các thao tác đóng case hoặc chuyển chặng.

### Kịch Bản 4: Bất Thường Nhập Kho & Chênh Lệch Hàng Hóa (Warehouse Discrepancy)
- **Tình huống**:
  - Dỡ container tại kho, số lượng thực nhận 985 kiện so với 1,000 kiện trên hóa đơn và B/L (Hụt 15 kiện, hư hỏng 10 kiện).
- **Kỳ vọng trên Overview**:
  - Thẻ Kho hàng: Hiển thị cảnh báo màu đỏ "⚠ DISCREPANCY DETECTED (Expected: 1,000 / Received: 985 / Damaged: 10)".
  - Hệ thống tự động kích hoạt tạo 1 `Shipment Exception` gắn trách nhiệm cho Trưởng kho và Phụ trách bảo hiểm.

---

## 5. Ma Trận Quy Tắc Chốt Chặn Hồ Sơ (Stage Gate Rules)

Trade Case Overview thực thi nghiêm ngặt các quy tắc kiểm soát cửa ải (Stage Gates) trước khi cho phép người dùng hoặc hệ thống kích hoạt hành động **[Đóng Trade Case] (Close Case)**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   STAGE GATE: ĐIỀU KIỆN ĐÓNG HỒ SƠ                     │
├────┬──────────────────────────────────┬─────────────────┬──────────────┤
│ Mã │ Tiêu Chí Kiểm Tra                │ Điều Kiện Đạt   │ Nếu Vi Phạm  │
├────┼──────────────────────────────────┼─────────────────┼──────────────┤
│ G1 │ Giao Hàng & Dỡ Cont Tại Kho      │ Current Stage in│ Chặn đóng    │
│    │ (Cargo Received at Destination)  │ [Warehouse, End]│ Báo lỗi G1   │
├────┼──────────────────────────────────┼─────────────────┼──────────────┤
│ G2 │ Hoàn Tất Thủ Tục Hải Quan         │ Customs Status =│ Chặn đóng    │
│    │ (Customs Clearance Cleared)      │ CLEARED         │ Báo lỗi G2   │
├────┼──────────────────────────────────┼─────────────────┼──────────────┤
│ G3 │ Hoàn Tất Phân Bổ Chi Phí         │ Landed Cost     │ Chặn đóng    │
│    │ (Landed Cost Voucher Finalized)  │ Voucher = SUBMIT│ Báo lỗi G3   │
├────┼──────────────────────────────────┼─────────────────┼──────────────┤
│ G4 │ Triệt Tiêu Số Dư Trung Gian      │ Số dư tài khoản │ Chặn đóng    │
│    │ (Expenses Included in Valuation) │ trung gian = 0  │ Báo lỗi G4   │
├────┼──────────────────────────────────┼─────────────────┼──────────────┤
│ G5 │ Không Còn Sự Cố Mở               │ Open Exceptions │ Chặn đóng    │
│    │ (Zero Open Exceptions)           │ Count == 0      │ Báo lỗi G5   │
├────┼──────────────────────────────────┼─────────────────┼──────────────┤
│ G6 │ Đầy Đủ Chứng Từ Bắt Buộc         │ Required Docs   │ Cảnh báo     │
│    │ (Mandatory Documents Uploaded)   │ Ready == 100%   │ Cần phê duyệt│
└────┴──────────────────────────────────┴─────────────────┴──────────────┘
```

> **Nguyên tắc kỹ thuật**: Khi người dùng ấn nút `[Close Trade Case]`, hàm `logistics_wizard.api.close_trade_case` sẽ duyệt qua cả 6 điều kiện trên. Nếu có bất kỳ điều kiện nào thất bại (`passed: false`), hệ thống sẽ trả về danh sách chi tiết các nguyên nhân và ném lỗi validation, không cho phép lưu trạng thái `Closed`.

---

## 6. Kế Hoạch Tiếp Theo Khi Quay Lại Module Này

1. **Bước 1**: Khi module M2 (Document Readiness) hoàn tất → Viết hàm kết nối adapter `get_document_readiness_status` trong `api.py`.
2. **Bước 2**: Khi module M3 (Customs/RAG) hoàn tất → Viết hàm kết nối adapter `get_customs_compliance_status` trong `api.py`.
3. **Bước 3**: Khi module M4 (Trade Cost) hoàn tất → Tích hợp số liệu Landed Cost và đối chiếu hóa đơn vào `get_landed_cost_status`.
4. **Bước 4**: Khi module M5 (Warehouse) hoàn tất → Liên kết Purchase Receipt và số liệu dỡ hàng vào `get_warehouse_receiving_status`.
5. **Bước 5**: Chạy toàn bộ 4 kịch bản kiểm thử trong file `test/test_trade_case_overview.py` để nghiệm thu tổng thể giải pháp.
