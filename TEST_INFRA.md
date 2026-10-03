# KIẾN TRÚC VÀ CƠ SỞ HẠ TẦNG KIỂM THỬ (TEST_INFRA.md)
## Module Trade Case Overview & Unified Desk Page — Logistics Wizard

> **Tài liệu chuẩn hóa kiến trúc kiểm thử tự động (E2E Test Infrastructure)**  
> **Dự án**: Logistics Wizard — ERPNext / Frappe Supply Chain Management  
> **Mục tiêu**: Đảm bảo chất lượng toàn diện cho buồng lái điều hành Trade Case Overview (14 Core Sections), Unified Desk Page (Sidebar 2 tab) và quy tắc kiểm soát đóng hồ sơ (Stage Gate).  
> **Nguyên tắc cốt lõi**: Opaque-box (hộp mờ), Requirement-driven (dựa trên yêu cầu gốc), Zero False Positives, Không vi phạm Purple Ban.

---

## 1. TỔNG QUAN VÀ PHẠM VI KIỂM THỬ

### 1.1. Phạm vi nghiệp vụ
Bộ kiểm thử bao quát toàn bộ 4 nhóm yêu cầu chính trong `ORIGINAL_REQUEST.md` và `PROJECT.md`:
1. **R1 (Unified Desk Page Architecture)**: Sidebar trái điều hướng 2 tab (`Trade Case Overview` & `Shipment Tracking Hub`), Case Selector dropdown, đồng bộ trạng thái Case ID, nút drill-down `[View Shipment Tracking]` chuyển tab tức thì không reload trang.
2. **R2 (Complete Trade Case Overview UI Frame)**: Đầy đủ 14 khối chức năng (Header, Stepper 9 chặng, Health Grid 6 thẻ, Shipment Summary, Document Readiness, Customs & Compliance, Cost Summary, Warehouse Readiness, Top Open Exceptions, Upcoming Actions, Related ERP Docs, Responsibility Matrix, Activity Timeline, Quick Actions & Stage Gate).
3. **R3 (Trade Case Data Model Definition)**: DocType `Trade Case` chuẩn Frappe, nguyên tắc Reference-First (Zero Data Duplication), không sao chép chi tiết item hay GPS từ các module con.
4. **R4 (Roadmap todoTradeCase.md)**: Danh mục 5 module phụ thuộc, API interface contracts & schemas, 4 kịch bản kiểm thử tích hợp, ma trận quy tắc Stage-Gate.

### 1.2. Môi trường và Ràng buộc kỹ thuật
- **Môi trường thực thi**: Python 3.10+, Framework unittest tiêu chuẩn.
- **Tính độc lập (Progressive Testability)**: Test suite tích hợp sẵn `StandaloneHarness` giả lập ORM và bộ nhớ cache, cho phép thực thi độc lập trên host CI/CD mà không phụ thuộc bắt buộc vào MariaDB hoặc bench server đang hoạt động.
- **Ràng buộc thiết kế (Purple Ban)**: Quét tự động 100% mã nguồn CSS và JS để bảo đảm không tồn tại bất kỳ mã màu tím nào (no purple/violet/magenta/indigo).

---

## 2. PHÂN TẦNG KIỂM THỬ 4-TIER (4-TIER VERIFICATION HIERARCHY)

Cấu trúc kiểm thử được tổ chức theo mô hình phân tầng kim tự tháp 4 cấp độ:

```
┌────────────────────────────────────────────────────────────────────────┐
│           TIER 4: REAL-WORLD APPLICATION SCENARIOS                     │
│  (Mô phỏng 4 nghiệp vụ thực tế: Happy Path, Delay+C/O, Red Channel, WH)│
├────────────────────────────────────────────────────────────────────────┤
│           TIER 3: CROSS-FEATURE COMBINATIONS                           │
│  (Đồng bộ trạng thái 2 tab, Drill-down context, Stage-Gate vs Close)   │
├────────────────────────────────────────────────────────────────────────┤
│           TIER 2: BOUNDARY & CORNER CASES                              │
│  (Purple Ban Regex, Dữ liệu rỗng/Null, Thiếu C/O, Vượt chi phí >5%)    │
├────────────────────────────────────────────────────────────────────────┤
│           TIER 1: FEATURE COVERAGE (CHỨC NĂNG CỐT LÕI)                 │
│  (DocType Schema, 14 Khối UI DOM, API Endpoints, Sidebar, todo MD)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### TIER 1: FEATURE COVERAGE (KIỂM THỬ ĐỘ PHỦ TÍNH NĂNG)

Mục tiêu: Đảm bảo từng thành phần riêng lẻ được khai báo đầy đủ, đúng cú pháp và đáp ứng hợp đồng giao tiếp kỹ thuật.

| Nhóm Kiểm Tra | Đối Tượng Kiểm Thử | Tiêu Chuẩn Đạt (Assertion) |
|---|---|---|
| **F1: DocType Schema JSON** | `trade_case.json` | Tồn tại file, JSON hợp lệ, `doctype: "DocType"`, chứa đầy đủ các trường master (`trade_type`, `status`, `current_stage`, `overall_health`, `priority`, `purchase_order`, `mode`, `incoterm`, `origin_port`, `destination_port`, `case_owner`, v.v.). Không chứa trường trùng lặp (`items`, `gps_coordinates`). |
| **F2: Child Sub-structures** | Sub-models & references | Hỗ trợ cấu trúc quan hệ 1:N cho vận đơn (`shipment_summary`), ma trận nhân sự (`responsibility_matrix`), danh mục chốt chặn (`stage_gate` checklist). |
| **F3: Backend API Endpoints** | `apps/logistics_wizard/logistics_wizard/api.py` | Cung cấp các hàm API cốt lõi: `get_trade_case_overview_data`, `get_trade_case_list`, `close_trade_case`. Đảm bảo danh sách `__all__` công khai các hàm này. |
| **F4: Desk Page Structure** | `apps/logistics_wizard/logistics_wizard/page/` | Tệp HTML, JS, CSS, JSON của Desk Page tồn tại, đăng ký hợp lệ trong Frappe Desk. |
| **F5: Sidebar Dual-Tab Nav** | Layout HTML/DOM | Có khối `.lw-sidebar`, menu 2 tab (`Trade Case Overview` & `Shipment Tracking Hub`), nút tab có id `#lw-nav-tab-overview` và `#lw-nav-tab-tracking`. |
| **F6: Case Selector Sync** | Sidebar DOM | Có phần tử dropdown `#lw-case-dropdown`, chip trạng thái `#lw-case-chip`, hiển thị danh sách case sẵn có (`IMP-2026-001`, `IMP-2026-002`, `EXP-2026-001`). |
| **F7: Drill-Down Action** | Card 4 DOM & Event | Tồn tại nút drill-down `#tc-btn-goto-shipment` với nhãn "Xem Shipment Tracking" kèm icon mũi tên. |
| **F8-F21: 14 UI Sections** | DOM Nodes trong `#lw-pane-overview` | Khảo sát đủ 14 khối: 1. Header (`#tc-header-id`, `#tc-header-status`), 2. Stepper (`#tc-lifecycle-stepper`), 3. Health Grid (`#tc-health-grid`), 4. Shipment Summary (`#tc-shipment-summary-body`), 5. Document Readiness (`#tc-doc-readiness-body`), 6. Customs Card (`#tc-customs-body`), 7. Cost Card (`#tc-cost-body`), 8. Warehouse Card (`#tc-wh-body`), 9. Exceptions Card (`#tc-exceptions-body`), 10. Upcoming Actions (`#tc-actions-body`), 11. Related ERP Docs (`#tc-related-erp-body`), 12. Responsibility Matrix (`#tc-responsibility-body`), 13. Audit Timeline (`#tc-activity-body`), 14. Stage Gate (`#tc-stage-gate-body`). |
| **F22-F25: todoTradeCase.md** | `todoTradeCase.md` tại gốc repo | Tồn tại file, có đủ 4 phần: 1. Danh mục module phụ thuộc, 2. API interface contracts & schemas, 3. 4 kịch bản test, 4. Quy tắc Stage Gate. |

---

### TIER 2: BOUNDARY & CORNER CASES (KIỂM THỬ BIÊN VÀ TRƯỜNG HỢP NGOẠI LỆ)

Mục tiêu: Đánh giá khả năng chịu lỗi, phòng vệ và bảo vệ nguyên tắc thiết kế trước dữ liệu bất thường.

1. **Quét Regex PURPLE BAN (Tuân thủ thiết kế giao diện)**:
   - Quét toàn bộ các tệp `.css`, `.js`, `.html` trong `apps/logistics_wizard/logistics_wizard`.
   - Loại bỏ các comment giải thích trước khi quét.
   - Nghiêm cấm tuyệt đối các mã màu HEX: `#800080`, `#8a2be2`, `#9333ea`, `#7c3aed`, `#6366f1`, `#8b5cf6`, `#a855f7`, `#d946ef`, `#4c1d95`, `#581c87`, `#6d28d9`, `#9400d3`, `#4b0082`, `#ee82ee`, `#da70d6`, `#ba55d3`, `#9932cc`, `#8b008b`.
   - Nghiêm cấm các từ khóa màu CSS: `purple`, `violet`, `magenta`, `indigo` trong các thuộc tính style hoạt động.
   - Kết quả bắt buộc: **0 vi phạm**.
2. **Dữ liệu Rỗng & Fallback An Toàn (Null / Empty Data Handling)**:
   - Truy vấn API với Case ID không tồn tại hoặc rỗng (`None`, `""`, `UNKNOWN-CASE`).
   - Hệ thống không được văng lỗi 500 (`Unhandled Exception`), phải tự động fallback sang default case hoặc trả về payload hợp lệ.
3. **Cảnh Báo Thiếu Chứng Từ Khẩn Cấp (Missing Urgent Documents)**:
   - Khi tỷ lệ chứng từ < 100% và thiếu C/O Form E hoặc D/O, thẻ Document Readiness phải kích hoạt cảnh báo khẩn cấp màu đỏ (`missing_urgent`).
4. **Vượt Chi Phí Dự Toán >5% (Cost Overrun Threshold)**:
   - Kiểm tra ngưỡng chênh lệch chi phí (`variance_pct`). Nếu thực tế vượt dự toán > 5%, hệ thống tự động gán nhãn cảnh báo chi phí và phản ánh lên chỉ số sức khỏe `overall_health`.
5. **Khóa Chặn Khi Có Sự Cố Nghiêm Trọng (Critical Exception Lock)**:
   - Khi hồ sơ có sự cố mở ở mức `Critical`, chỉ số sức khỏe tổng thể bắt buộc là `Critical` và khóa chặn hoàn toàn quyền đóng case.

---

### TIER 3: CROSS-FEATURE COMBINATIONS (KIỂM THỬ TƯƠNG TÁC TỔ HỢP)

Mục tiêu: Kiểm tra dòng chảy dữ liệu và sự phối hợp giữa các phân hệ giao diện và backend.

1. **Bảo toàn trạng thái khi chuyển tab (0ms Tab Switching State Machine)**:
   - Chuyển đổi từ `Trade Case Overview` sang `Shipment Tracking Hub` và ngược lại.
   - Biến `currentCaseId` trong bộ nhớ điều phối (`UnifiedLogisticsHub`) phải được bảo toàn nguyên vẹn.
   - Không được reload lại toàn bộ trang (DOM preserve).
   - Khi chuyển sang Tab Tracking, phải kích hoạt lệnh `map.invalidateSize()` để Leaflet map vẽ đúng kích thước khung nhìn.
2. **Kích hoạt Drill-down Context**:
   - Khi bấm nút `[View Shipment Tracking]` từ Card 4, bộ điều phối phải tự động:
     - Chuyển `currentTab` sang `tracking`.
     - Truyền đúng tham số `shipment_id` sang `ShipmentTrackingHub`.
     - Kích hoạt focus/highlight lô hàng tương ứng trên bản đồ và bảng dữ liệu.
3. **Thực thi Stage Gate và Chốt Chặn Đóng Hồ Sơ**:
   - Gọi `close_trade_case` cho hồ sơ đang ở trạng thái `In Transit` hoặc còn sự cố mở:
     - Kết quả: `success: False`, `can_close: False`.
     - Trả về danh sách chi tiết các lý do vi phạm điều kiện chốt chặn.
   - Thử nghiệm với hồ sơ đã thỏa mãn 100% điều kiện (đã nhận hàng, thông quan xong, chốt chi phí, 0 sự cố):
     - Kết quả: `success: True`, trạng thái chuyển sang `Closed`.

---

### TIER 4: REAL-WORLD APPLICATION SCENARIOS (KỊCH BẢN THỰC TẾ)

Mục tiêu: Đảm bảo luồng xử lý trọn vẹn theo 4 nghiệp vụ ngoại thương thực tế được quy định trong `todoTradeCase.md`:

1. **Kịch bản 1: Luồng Tiêu Chuẩn Thuận Lợi (Happy Path — Healthy)**:
   - Dữ liệu thử nghiệm: `IMP-2026-002` (Hàng linh kiện nhập khẩu bằng đường hàng không từ Tokyo về Nội Bài).
   - Đặc điểm: 0 delay, 10/10 chứng từ hoàn tất, hải quan thông quan (Luồng Xanh), 0 sự cố mở.
   - Kết quả kỳ vọng: `overall_health: "Healthy"`, `document_readiness.percentage: 100`, `open_exceptions.total_open: 0`.
2. **Kịch bản 2: Lệch Lịch Trình & Chậm Hồ Sơ (Delay & Missing C/O — Attention)**:
   - Dữ liệu thử nghiệm: `IMP-2026-001` (Hàng điện tử đường biển từ Thượng Hải về Đà Nẵng).
   - Đặc điểm: Tàu trễ +2 ngày do bão, thiếu C/O Form E gốc, chi phí vượt +7.9%, 3 sự cố đang mở.
   - Kết quả kỳ vọng: `overall_health: "Attention"`, phát hiện cảnh báo thiếu C/O trong `missing_urgent`, `close_trade_case` trả về ít nhất 4 lý do chặn đóng hồ sơ.
3. **Kịch bản 3: Sự Cố Nghiêm Trọng Luồng Đỏ Kiểm Hóa (Critical Red Channel)**:
   - Dữ liệu thử nghiệm: `EXP-2026-001` (Lô pin năng lượng mặt trời xuất khẩu đi Los Angeles).
   - Đặc điểm: Tờ khai hải quan bị phân Luồng Đỏ (Kiểm hóa 100%), có sự cố mức Critical.
   - Kết quả kỳ vọng: `overall_health: "Critical"`, tờ khai ghi nhận "Luồng Đỏ - Kiểm hóa 100%", hệ thống khóa toàn bộ thao tác kết thúc case.
4. **Kịch bản 4: Bất Thường Nhập Kho & Đối Soát Hàng Hóa (Warehouse Discrepancy)**:
   - Mô phỏng dữ liệu dỡ cont tại kho: Số lượng dự kiến 1,000 kiện, thực nhận 985 kiện (hụt 15 kiện, hư hỏng 10 kiện).
   - Kết quả kỳ vọng: Phản ánh trạng thái chênh lệch số lượng, kích hoạt cảnh báo lập biên bản bồi thường và ghi nhận sự cố.

---

## 3. CƠ CHẾ HARNESS VÀ KIỂM THỬ KHÔNG PHỤ THUỘC (STANDALONE HARNESS)

Để đảm bảo các kỹ sư và hệ thống CI có thể chạy bộ test một cách độc lập:
1. **Mock Document & Controller**: Lớp `TradeCase` trong `trade_case.py` được thiết kế có fallback an toàn khi không tìm thấy module `frappe` (tự động fallback sang lớp base Document in-memory).
2. **Central Aggregator Mocking**: API `get_trade_case_overview_data` có sẵn 3 bộ hồ sơ chuẩn (`IMP-2026-001`, `IMP-2026-002`, `EXP-2026-001`) đại diện cho 3 trạng thái vận hành điển hình (Warning, Healthy, Critical).
3. **Headless Template & DOM Parser**: Bộ test sử dụng phân tích tĩnh và DOM pattern matching để kiểm tra cấu trúc HTML template, CSS styling và JavaScript controllers mà không bắt buộc khởi động trình duyệt Selenium/Playwright cồng kềnh đối với các bài kiểm tra logic desk.

---

## 4. HƯỚNG DẪN THỰC THI KIỂM THỬ

### 4.1. Lệnh thực thi chính
Chạy toàn bộ 4 Tiers của bộ kiểm thử E2E:

```bash
# Cách 1: Chạy trực tiếp qua module unittest
python3 -m unittest test/test_trade_case_e2e.py -v

# Cách 2: Chạy trực tiếp qua file script
python3 test/test_trade_case_e2e.py

# Cách 3: Chạy qua pytest (nếu môi trường có cài đặt)
pytest test/test_trade_case_e2e.py -v
```

### 4.2. Chạy kiểm tra từng Tier cụ thể
Có thể chỉ định từng test case class để kiểm tra nhanh:

```bash
# Chỉ chạy Tier 1 (Feature Coverage)
python3 -m unittest test.test_trade_case_e2e.TestTier1FeatureCoverage -v

# Chỉ chạy Tier 2 (Boundary & Purple Ban)
python3 -m unittest test.test_trade_case_e2e.TestTier2BoundaryCornerCases -v

# Chỉ chạy Tier 3 (Cross-Feature Combinations)
python3 -m unittest test.test_trade_case_e2e.TestTier3CrossFeatureCombinations -v

# Chỉ chạy Tier 4 (Real-World Scenarios)
python3 -m unittest test.test_trade_case_e2e.TestTier4RealWorldScenarios -v
```

---

## 5. TIÊU CHUẨN NGHIỆM THU & CỔNG CHẤT LƯỢNG (QUALITY GATES)

Một bản build được xem là đạt yêu cầu và đủ điều kiện xuất bản `TEST_READY.md` khi thỏa mãn:
1. **100% Pass Rate**: Tất cả các bài kiểm tra từ Tier 1 đến Tier 4 đều trả về `OK` (0 Failures, 0 Errors).
2. **Zero Purple Ban**: Không phát hiện bất kỳ mã màu tím nào trong toàn bộ stylesheet và logic giao diện.
3. **Zero Data Duplication**: DocType `Trade Case` tuân thủ nguyên tắc Reference-First, không chứa các bảng chi tiết trùng lắp.
4. **Khép Kín Quy Trình Stage Gate**: Mọi trường hợp vi phạm điều kiện chuyển trạng thái đều bị chặn đúng với lý do cụ thể.
