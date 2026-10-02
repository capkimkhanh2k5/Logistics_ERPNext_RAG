# 📘 QUY TRÌNH TÁC NGHIỆP PHÂN VAI THEO VỊ TRÍ CÔNG VIỆC XUẤT NHẬP KHẨU
*(Role-Based Standard Operating Procedures & Isolated Workflows on ERPNext v15)*

---

## 🧭 1. TỔNG QUAN DÒNG CHẢY BÀN GIAO GIỮA 6 VỊ TRÍ (HIGH-LEVEL HANDSHAKE)

Để không bị rối mắt bởi các đường nối chéo nhau, toàn bộ chuỗi cung ứng được chuẩn hóa thành **Sơ đồ bàn giao liên vị trí mức cao (High-Level Handshake)**. Sau đó, mỗi vị trí công việc có **một chương đặc tả và sơ đồ quy trình độc lập riêng biệt**:

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#FFFFFF',
    'primaryTextColor': '#0F172A',
    'primaryBorderColor': '#0284C7',
    'lineColor': '#0284C7',
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '12px'
  }
}}%%
flowchart LR
    R1["🛒 <b>1. THU MUA</b><br>Hợp đồng & PO"]
    R2["👑 <b>2. GIÁM ĐỐC / CFO</b><br>Duyệt PO & Chi cọc"]
    R3["💰 <b>3. KẾ TOÁN</b><br>Chi cọc 30%"]
    R4["🚢 <b>4. LOGISTICS</b><br>Tàu biển & B/L"]
    R5["🏛️ <b>5. HẢI QUAN</b><br>Tờ khai VNACCS"]
    R6["📦 <b>6. THỦ KHO</b><br>Dỡ hàng & Nhận PR"]

    R1 ==>|"Trình PO"| R2
    R2 ==>|"Lệnh chi"| R3
    R3 ==>|"Xác nhận cọc"| R4
    R4 ==>|"Gửi B/L"| R5
    R5 ==>|"Thông quan"| R6
    R6 ==>|"Phiếu PR"| R3
    R3 ==>|"Quyết toán"| R2

    %% Các đường trả ngược về khi có biến cố (Màu đỏ nét đứt)
    R2 -. "❌ Bác bỏ PO" .-> R1
    R5 -. "❌ Lệch C/O" .-> R1
    R6 -. "⚠️ Hàng dập nát" .-> R3
    R2 -. "❌ Vượt chi phí" .-> R4

    style R1 fill:#F0F9FF,stroke:#0284C7,stroke-width:2px,color:#0F172A
    style R2 fill:#FFFBEB,stroke:#D97706,stroke-width:2px,color:#0F172A
    style R3 fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#0F172A
    style R4 fill:#F5F3FF,stroke:#7C3AED,stroke-width:2px,color:#0F172A
    style R5 fill:#FDF2F8,stroke:#DB2777,stroke-width:2px,color:#0F172A
    style R6 fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#0F172A

    linkStyle default stroke:#0284C7,stroke-width:2px;
```

---

## 🛒 MỤC 1: VỊ TRÍ CHUYÊN VIÊN THU MUA (BUYER)

### 1.1. Sơ đồ Luồng Tác nghiệp của Thu Mua

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#FFFFFF', 'lineColor': '#0284C7'}}}%%
flowchart TD
    B_IN(["📥 <b>ĐẦU VÀO:</b> Yêu cầu mua sắm (Material Request) / Kế hoạch kinh doanh"]) --> B1
    B1["<b>Bước 1: Đàm phán với Nhà máy Quốc tế</b><br>Chốt đơn giá, số lượng, điều kiện Incoterms (CIF/FOB), lịch giao hàng"] --> B2
    B2["<b>Bước 2: Lập Đơn Mua Hàng (Purchase Order)</b><br>Nhập đơn giá ngoại tệ USD, tỷ giá kế hoạch, dự toán chi phí lô hàng"] --> B3
    B3["<b>Bước 3: Khởi tạo Hồ sơ Mẹ Trade Case</b><br>Tạo mã <b>IMP-2026-xxxxx</b> để quản lý xuyên suốt vòng đời"] --> B4
    B4{"<b>Bước 4: Trình ký Giám Đốc / CFO</b><br>Đơn PO có được duyệt?"}
    
    B4 -- "❌ BÁC BỎ (Giá cao / Vượt ngân sách)" --> B_REVISE["<b>Bước 4.1: Đàm phán lại với Nhà máy</b><br>Ép giảm giá số lượng lớn hoặc đổi điều khoản thanh toán"]
    B_REVISE --> B2
    
    B4 -- "✅ PHÊ DUYỆT" --> B5["<b>Bước 5: Ký Hợp Đồng Ngoại Thương Chính Thức</b><br>Bàn giao hợp đồng sang Kế toán để chi tiền cọc 30%"] --> B6
    
    B6["<b>Bước 6: Theo dõi Sản Xuất & Tàu Chạy (M04)</b><br>Khi tàu rời cảng xuất: Hệ thống khóa cứng PO (không được sửa giá/SL)"] --> B7{"<b>Bước 7: Hải Quan Soi Chứng Từ?</b><br>Có bị sai lệch C/O / Invoice?"}
    
    B7 -- "❌ SAI LỆCH C/O / INVOICE" --> B_AMEND["<b>Bước 7.1: Đòi Nhà máy cấp lại C/O Form E sửa đổi</b><br>Thúc ép phát hành Amendment trong 48h để kịp thông quan"]
    B_AMEND --> B7
    
    B7 -- "✅ HỢP LỆ" --> B_OUT(["📤 <b>ĐẦU RA:</b> Hợp đồng chuẩn, PO đã duyệt, C/O hợp lệ"])

    style B_IN fill:#F0F9FF,stroke:#0284C7,stroke-width:2px,color:#0F172A
    style B4 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style B7 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style B_REVISE fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style B_AMEND fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style B_OUT fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    linkStyle default stroke:#0284C7,stroke-width:2px;
```

### 1.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Thu Mua)
* **Chứng từ ERPNext tạo ra:** `Material Request`, `Purchase Order` (PO), `Trade Case` (`IMP-.YYYY.-.#####`).
* **Rào chắn 1 (Tolerance Limit):** Hệ thống chặn không cho tạo đơn PO vượt quá hạn mức công nợ tối đa đã cấp cho nhà cung cấp.
* **Rào chắn 2 (Immutable PO at M04):** Ngay khi Chuyến tàu đạt mốc `M04_ETD` (Tàu đã rời cảng bốc), hệ thống tự động khóa trạng thái đơn PO sang Read-only. Thu mua không được tự ý sửa số lượng hoặc đơn giá để che giấu chênh lệch.
* **Xử lý khi bị trả ngược:** Nếu CFO từ chối hoặc Hải quan báo C/O sai tiêu chí, Thu mua là đầu mối duy nhất liên hệ nhà máy nước ngoài để đàm phán lại trong vòng 24 - 48h.

---

## 👑 MỤC 2: VỊ TRÍ BAN GIÁM ĐỐC / GIÁM ĐỐC TÀI CHÍNH (CFO)

### 2.1. Sơ đồ Luồng Tác nghiệp của Giám Đốc / CFO

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#FFFFFF', 'lineColor': '#D97706'}}}%%
flowchart TD
    C_IN(["📥 <b>ĐẦU VÀO:</b> Đơn PO trình ký / Tờ trình chi cọc / Báo cáo Tháp chỉ huy"]) --> C1
    C1{"<b>Bước 1: Thẩm Định Đơn PO</b><br>So khớp Ngân sách kế hoạch & Đơn giá thị trường?"}
    
    C1 -- "❌ KHÔNG HỢP LÝ" --> C_REJ_PO["<b>Bác bỏ đơn PO:</b> Yêu cầu Thu mua đàm phán lại"]
    C1 -- "✅ HỢP LÝ" --> C2["<b>Bước 2: Ký Duyệt Đơn Mua Hàng PO</b><br>Kích hoạt phân quyền cho phép Kế toán lập phiếu chi"] --> C3
    
    C3["<b>Bước 3: Ký Duyệt Ủy Nhiệm Chi Cọc 30%</b><br>Phê duyệt xuất quỹ Vietcombank USD chuyển ra nước ngoài"] --> C4
    
    C4["<b>Bước 4: Giám Sát Tháp Chỉ Huy (Control Tower)</b><br>Theo dõi cảnh báo đếm ngược phạt bãi cont, trễ tàu, vượt dự toán"] --> C5
    
    C5{"<b>Bước 5: Thẩm Định Đóng Lô Hàng (Closed)</b><br>Chi phí thực tế có vượt ngân sách > 10%?"}
    
    C5 -- "🟢 ĐỊNH MỨC <= 10%" --> C_OK["<b>Bước 5.1: Phê duyệt đóng lô hàng</b><br>Chốt giá vốn bất biến vào Báo cáo Tài chính"]
    
    C5 -- "⚠️ VƯỢT > 10%" --> C6{"<b>Bước 6: Thẩm Định Ngoại Lệ</b><br>Lý do vượt có chính đáng?<br><i>(Lệch tỷ giá USD vs Lệch cước tàu)</i>"}
    
    C6 -- "❌ BÁC BỎ" --> C_REJ_COST["<b>Bác bỏ:</b> Yêu cầu Logistics/Kế toán truy cứu trách nhiệm & đàm phán giảm trừ cước"]
    C6 -- "✅ CHẤP THUẬN" --> C_AUTH["<b>Bước 6.1: Nhập Mã Ủy Quyền Cấp Cao (CFO Override)</b><br>Cho phép đóng quyết toán lô hàng vượt ngân sách"] --> C_OK
    
    C_OK --> C_OUT(["📤 <b>ĐẦU RA:</b> Lô hàng hoàn tất (cost_status = Closed), giá vốn chốt"])

    style C_IN fill:#FFFBEB,stroke:#D97706,stroke-width:2px,color:#0F172A
    style C1 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style C5 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style C6 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style C_REJ_PO fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style C_REJ_COST fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style C_AUTH fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    style C_OUT fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    linkStyle default stroke:#D97706,stroke-width:2px;
```

### 2.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (CFO)
* **Quyền hạn tối cao:** Duyệt PO $> 1$ tỷ VND, duyệt chi ngoại tệ, duyệt ngoại lệ chi phí vượt ngân sách $> 10\%$.
* **Rào chắn 1 (Two-Man Rule):** Kế toán viên không thể tự ý chuyển tiền nếu không có chữ ký điện tử / mã OTP của Giám đốc hoặc CFO.
* **Rào chắn 2 (Stage Gate 3 - Over Budget Lock):** Hệ thống phân quyền cứng: Chỉ Role `CFO` hoặc `System Manager` mới có quyền chuyển `cost_status` từ `Pending Review` sang `Closed` khi lô hàng có `cost_variance_pct > 10%`. Nhân viên cấp dưới hoàn toàn bị khóa nút bấm này.

---

## 💰 MỤC 3: VỊ TRÍ KẾ TOÁN GIÁ VỐN & CÔNG NỢ (ACCOUNTANT)

### 3.1. Sơ đồ Luồng Tác nghiệp của Kế Toán

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#FFFFFF', 'lineColor': '#059669'}}}%%
flowchart TD
    A_IN(["📥 <b>ĐẦU VÀO:</b> PO đã duyệt / Tờ khai thuế / Hóa đơn cước / Phiếu nhập kho PR"]) --> A1
    A1["<b>Bước 1: Chi Tạm Ứng Cọc 30% Tiền Hàng</b><br>Lập Payment Entry (Nợ 331 - NCC / Có 1121 - VCB USD). <i>Bắt buộc tích Is Advance</i>"] --> A2
    A2["<b>Bước 2: Nộp Thuế Hải Quan Vào Kho Bạc</b><br>Căn cứ Tờ khai VNACCS ➔ Chi tiền nộp Thuế NK (TK 3333) & Thuế GTGT (TK 33312)"] --> A3
    A3["<b>Bước 3: Thu Thập Hóa Đơn Dịch Vụ Cảng & Forwarder</b><br>Cước biển, phí D/O, nâng hạ, kiểm dịch, cước bộ. Kiểm tra tính hợp lệ e-Invoice"] --> A4
    A4["<b>Bước 4: Chạy Phân Bổ Giá Vốn (Landed Cost Voucher - LCV)</b><br>• Cước tàu biển: Phân bổ theo Thể tích (CBM)<br>• Thuế & Phí khác: Phân bổ theo Trị giá hàng (Customs Value)"] --> A5
    A5["<b>Bước 5: Bóc Tách Chênh Lệch Dự Toán vs Thực Tế</b><br>Hệ thống tự bóc tách: Lệch Giá cước hãng tàu vs Lệch Tỷ giá USD/VND"] --> A6
    
    A6{"<b>Bước 6: Kho Báo Hàng Hư Hỏng / Mất Mát?</b><br>Có biên bản giám định hiện trường?"}
    
    A6 -- "⚠️ CÓ HÀNG HỎNG" --> A_CLAIM["<b>Bước 6.1: Hạch toán Phải Thu Bồi Thường (TK 1388)</b><br>Ghi nợ TK 1388 đòi Bảo hiểm/NCC. <i>Tuyệt đối không gộp vào giá vốn hàng tồn</i>"] --> A7
    A6 -- "🟢 ĐỦ HÀNG" --> A7
    
    A7["<b>Bước 7: Quyết Toán Hóa Đơn Mua Hàng (Purchase Invoice - PI)</b><br>ERPNext tự động cấn trừ 30% tiền cọc ➔ Kế toán lập lệnh chi 70% còn lại"] --> A8
    
    A8{"<b>Bước 8: Kiểm Tra Cổng Ngân Sách Lô Hàng</b><br>Tổng chi phí thực tế có vượt > 10% dự toán?"}
    
    A8 -- "⚠️ VƯỢT > 10%" --> A_REP["<b>Bước 8.1: Lập Tờ Trình Vượt Ngân Sách Trình CFO</b><br>Phân tích rõ nguyên nhân phát sinh chi phí"]
    A_REP --> A9{"<b>CFO Có Duyệt Ngoại Lệ?</b>"}
    A9 -- "❌ BÁC BỎ" --> A_DISPUTE["<b>Bước 8.2: Phối hợp Logistics bắt Forwarder giảm trừ</b><br>Yêu cầu nhà xe/forwarder phát hành hóa đơn điều chỉnh giảm"] --> A4
    A9 -- "✅ PHÊ DUYỆT" --> A_CLOSE
    
    A8 -- "🟢 TRONG ĐỊNH MỨC <= 10%" --> A_CLOSE["<b>Bước 9: Đóng Quyết Toán Lô Hàng (Closed)</b><br>Chốt giá vốn đơn vị vào thẻ kho và sổ cái kế toán"]
    
    A_CLOSE --> A_OUT(["📤 <b>ĐẦU RA:</b> Giá vốn đích thực (Landed Cost) đã chốt, công nợ 0"])

    style A_IN fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#0F172A
    style A6 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style A8 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style A9 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style A_CLAIM fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    style A_REP fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style A_DISPUTE fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style A_OUT fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    linkStyle default stroke:#059669,stroke-width:2px;
```

### 3.2. Bảng Hạch Toán Kế Toán & Rào Chắn Poka-Yoke (Kế Toán)
* **Bảng tài khoản chuẩn mực (VAS 02 / IAS 2):**
  * Tạm ứng cọc: Nợ TK 331 / Có TK 1121 (USD).
  * Nộp thuế: Nợ TK 3333 (Thuế NK), Nợ TK 33312 (VAT) / Có TK 1121 (VND).
  * Hàng hỏng: Nợ TK 1388 (Phải thu bồi thường) / Có TK 331 (Giảm nợ NCC) hoặc Có TK 156.
  * Phân bổ chi phí: Nợ TK 156 (Tăng giá trị hàng tồn kho) / Có TK 331 (Forwarder/Cảng).
* **Rào chắn 1 (Auto Advance Deduction):** Khi mở Purchase Invoice, hệ thống tự động kiểm tra bảng `advances` và cấn trừ đúng số tiền 30% cọc. Kế toán không thể vô tình thanh toán 100% tiền hàng lần thứ hai.
* **Rào chắn 2 (VAS 02 Non-Capitalization):** Tiền phạt lưu bãi (Demurrage) và phạt vi phạm hải quan tuyệt đối không được chọn vào LCV, bắt buộc tống vào chi phí kinh doanh trong kỳ (TK 811 hoặc 642).

---

## 🚢 MỤC 4: VỊ TRÍ ĐIỀU PHỐI LOGISTICS (COORDINATOR)

### 4.1. Sơ đồ Luồng Tác nghiệp của Điều Phối Logistics

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#FFFFFF', 'lineColor': '#7C3AED'}}}%%
flowchart TD
    L_IN(["📥 <b>ĐẦU VÀO:</b> Hợp đồng ngoại thương / Thông báo hàng sẵn sàng (Cargo Ready)"]) --> L1
    L1["<b>Bước 1: Khởi Tạo Chuyến Tàu Con Trade Shipment</b><br>Mở mã <b>TS-2026-xxxxx</b> liên kết với Trade Case mẹ. Ghi nhận Incoterm, Cảng đi/đến"] --> L2
    L2["<b>Bước 2: Thu Thập Vận Đơn (B/L) & Dữ Liệu Container</b><br>Nhận Master B/L, House B/L, cập nhật danh sách Container (Số Cont, Số Seal, CBM, KGS)"] --> L3
    L3["<b>Bước 3: Theo Dõi 9 Mốc Hành Trình Chuẩn (M01 ➔ M05)</b><br>Giám sát ngày tàu chạy thực tế (M04_ETD) và ngày tàu dự kiến cập cảng (M05_ETA)"] --> L4
    
    L4{"<b>Bước 4: Tàu Có Bị Delay / Rớt Tàu (Rolled)?</b><br>Hãng tàu thông báo trễ lịch?"}
    
    L4 -- "⚠️ TÀU BỊ TRỄ" --> L_REVISE["<b>Bước 4.1: Cập nhật ETA mới & Tính lại Hạn Bãi</b><br>Hệ thống tự cộng thêm ngày dỡ mới vào Demurrage Deadline.<br>Logistics gửi công văn xin hãng tàu nới thêm Free-time"] --> L5
    L4 -- "🟢 ĐÚNG LỊCH" --> L5
    
    L5["<b>Bước 5: Kích Hoạt Đếm Ngược Miễn Phí Lưu Bãi (Free-Time)</b><br>Tàu cập cảng (M05) ➔ Hệ thống đếm ngược 7 ngày miễn phí bãi cảng Cát Lái/Hải Phòng"] --> L6
    
    L6{"<b>Bước 6: Kiểm Tra Cảnh Báo Sớm Hạn Bãi?</b><br>Còn <= 3 ngày mà chưa xong thủ tục?"}
    
    L6 -- "🔴 CÒN <= 3 NGÀY" --> L_WARN["<b>Bắn Chuông Báo Động Khẩn Cấp (Alarm):</b><br>Thúc ép Hải quan và Kế toán nộp thuế giải phóng hàng ngay để tránh phạt > 100$/ngày/cont"] --> L7
    L6 -- "🟢 AN TOÀN > 3 NGÀY" --> L7
    
    L7{"<b>Bước 7: Cổng Stage Gate Rút Hàng:</b><br>Tờ khai Hải quan đã có cờ Cleared (M07)?"}
    
    L7 -- "❌ CHƯA THÔNG QUAN" --> L_BLOCK["🚫 <b>CHẶN LẠI:</b> Tuyệt đối không điều xe kéo cont ra khỏi cảng<br><i>(Tránh xe đầu kéo chờ tại bãi phát sinh phí lưu ca xe)</i>"]
    L_BLOCK --> L7
    
    L7 -- "✅ ĐÃ THÔNG QUAN" --> L8["<b>Bước 8: Phát Lệnh Điều Xe Đầu Kéo (Delivery Order)</b><br>Điều xe ra cảng nâng cont và vận chuyển về kho nhà máy an toàn"] --> L_OUT
    
    L_OUT(["📤 <b>ĐẦU RA:</b> Container về tới cổng kho nguyên vẹn số seal"])

    style L_IN fill:#F5F3FF,stroke:#7C3AED,stroke-width:2px,color:#0F172A
    style L4 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style L6 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style L7 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style L_REVISE fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    style L_WARN fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style L_BLOCK fill:#7F1D1D,stroke:#F87171,stroke-width:2px,color:#FFFFFF
    style L_OUT fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    linkStyle default stroke:#7C3AED,stroke-width:2px;
```

### 4.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Logistics)
* **Chứng từ ERPNext:** `Trade Shipment` (`TS-.YYYY.-.#####`), `Trade Shipment Container`, `Trade Shipment Milestone`.
* **Công thức tự động hóa:**
  $$\text{Demurrage Deadline} = \text{ETA Actual} + \text{demurrage\_free\_days}$$
  $$\text{Detention Deadline} = \text{ETA Actual} + \text{detention\_free\_days}$$
* **Rào chắn 1 (Stage Gate Trucking Lock):** Hệ thống chặn không cho phép nhân viên logistics in Phiếu điều xe hoặc xác nhận mốc dỡ hàng nếu Tờ khai liên kết chưa đạt `clearance_status = "Cleared"`.
* **Rào chắn 2 (Demurrage 3-Day Early Warning):** Khi `today() >= Demurrage Deadline - 3 ngày`, hệ thống tự động đổi màu dòng container sang ĐỎ và bắn email cảnh báo trực tiếp đến Trưởng phòng Logistics.

---

## 🏛️ MỤC 5: VỊ TRÍ CHUYÊN VIÊN HẢI QUAN (CUSTOMS)

### 5.1. Sơ đồ Luồng Tác nghiệp của Chuyên Viên Hải Quan

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#FFFFFF', 'lineColor': '#DB2777'}}}%%
flowchart TD
    H_IN(["📥 <b>ĐẦU VÀO:</b> Bộ chứng từ vận tải (B/L, Commercial Invoice, Packing List, C/O)"]) --> H1
    H1["<b>Bước 1: Kiểm Tra Checklist 8 Chứng Từ Bắt Buộc</b><br>Rà soát Hợp đồng, Hóa đơn, Vận đơn, C/O, Giấy phép chuyên ngành"] --> H2
    
    H2{"<b>Bước 2: Bộ Chứng Từ Có Khớp 100%?</b><br>Sai lệch tên hàng, mã HS hoặc thiếu tiêu chí C/O?"}
    
    H2 -- "❌ SAI LỆCH / THIẾU C/O" --> H_REJ["<b>Bước 2.1: Từ Chối Chứng Từ & Giữ Cờ Not Ready</b><br>Báo Thu mua/Nhà máy phát hành bản đính chính C/O Amendment"] --> H1
    
    H2 -- "✅ ĐỦ 100% HỢP LỆ" --> H3["<b>Bước 3: Mở Cổng Stage Gate 1 (Document Ready)</b><br>Khai báo Giấy phép chuyên ngành <b>Import Permit</b> (nếu có)"] --> H4
    
    H4["<b>Bước 4: Truyền Tờ Khai Hải Quan Điện Tử VNACCS</b><br>Tạo <b>Customs Declaration</b> chuẩn 11 số. Hệ thống tự khớp Tỷ giá tuần BTC"] --> H5
    
    H5{"<b>Bước 5: Kết Quả Phân Luồng Tờ Khai?</b><br>Hệ thống hải quan trả về luồng nào?"}
    
    H5 -- "🟢 LUỒNG XANH" --> H_GREEN["<b>Bước 5.1: Luồng Xanh (Green)</b><br>Miễn kiểm tra hồ sơ và hàng hóa.<br>Chuyển Kế toán nộp thuế"]
    
    H5 -- "🟡 LUỒNG VÀNG" --> H_YELLOW["<b>Bước 5.2: Luồng Vàng (Yellow)</b><br>In bộ hồ sơ giấy mang đến Chi cục HQ đối chiếu chứng từ"]
    
    H5 -- "🔴 LUỒNG ĐỎ" --> H_RED["<b>Bước 5.3: Luồng Đỏ (Red - Kiểm Hóa)</b><br>Phối hợp Logistics đưa cont vào bãi kiểm hóa mở thùng kiểm tra thực tế"]
    
    H_YELLOW --> H6{"<b>Hải quan nghi vấn tham vấn giá?</b>"}
    H6 -- "⚠️ Bị tham vấn" --> H_CONSULT["Chứng minh trị giá giao dịch"] --> H_GREEN
    H6 -- "✅ Chấp thuận" --> H_GREEN
    
    H_RED --> H7{"<b>Kiểm hóa thực tế có khớp tờ khai?</b>"}
    H7 -- "❌ SAI MÃ HS / THỪA THIẾU" --> H_FINE["<b>Bị lập biên bản vi phạm hành chính:</b><br>Ấn định thuế bổ sung + Phạt tiền (Hạch toán riêng TK 811)"] --> H_GREEN
    H7 -- "✅ TRÙNG KHỚP 100%" --> H_GREEN
    
    H_GREEN --> H8["<b>Bước 6: Kế Toán Nộp Thuế & Chốt Thông Quan (Cleared)</b><br>Cập nhật số tờ khai và mốc <b>M07_CUSTOMS_CLEAR</b> lên lô hàng"] --> H_OUT
    
    H_OUT(["📤 <b>ĐẦU RA:</b> Tờ khai hải quan thông quan hoàn tất, đèn xanh cho kho"])

    style H_IN fill:#FDF2F8,stroke:#DB2777,stroke-width:2px,color:#0F172A
    style H2 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style H5 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style H6 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style H7 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style H_REJ fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style H_FINE fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style H_OUT fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    linkStyle default stroke:#DB2777,stroke-width:2px;
```

### 5.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Hải Quan)
* **Chứng từ ERPNext:** `Trade Document Item`, `Import Permit`, `Customs Declaration` (`1058249xxxxx`).
* **Rào chắn 1 (11-Digit Strict Validation):** Bắt buộc số tờ khai VNACCS phải đúng 11 chữ số nguyên vẹn. Hệ thống tự động từ chối lưu bản ghi nếu số ký tự khác 11.
* **Rào chắn 2 (Customs Rate Auto-Lookup):** Khóa cứng không cho nhân viên tự gõ tỷ giá tính thuế, bắt buộc hàm `fetch_customs_exchange_rate` tự động lấy từ bảng công bố hàng tuần của Bộ Tài chính.

---

## 📦 MỤC 6: VỊ TRÍ THỦ KHO VẬT LÝ (WAREHOUSE KEEPER)

### 6.1. Sơ đồ Luồng Tác nghiệp của Thủ Kho

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#FFFFFF', 'lineColor': '#DC2626'}}}%%
flowchart TD
    W_IN(["📥 <b>ĐẦU VÀO:</b> Xe container đến cổng kho công ty + Giấy giao nhận vận tải"]) --> W1
    W1{"<b>Bước 1: Cổng Stage Gate Thông Quan:</b><br>Lô hàng đã có cờ Cleared (M07) trên hệ thống?"}
    
    W1 -- "❌ CHƯA THÔNG QUAN" --> W_BLOCK["🚫 <b>CẤM CẮT CHÌ DỠ HÀNG:</b><br>Giữ nguyên cont tại cổng, không cho nhập hàng lậu/chưa thông quan"]
    W_BLOCK --> W1
    
    W1 -- "✅ ĐÃ THÔNG QUAN" --> W2{"<b>Bước 2: Kiểm Tra Số Container & Chì Seal:</b><br>Số chì có nguyên vẹn, khớp 100% với B/L gốc?"}
    
    W2 -- "❌ ĐỨT CHÌ / SAI SỐ SEAL" --> W_SURVEY["<b>Bước 2.1: GIỮ NGUYÊN HIỆN TRƯỜNG & LẬP BIÊN BẢN:</b><br>Chụp ảnh chì đứt, mời lái xe ký biên bản bất thường.<br>Mời cơ quan giám định SGS & Bảo hiểm đến đồng kiểm"] --> W3
    
    W2 -- "✅ CHÌ SEAL NGUYÊN VẸN" --> W3["<b>Bước 3: Cắt Chì, Mở Cửa Cont & Dỡ Hàng</b><br>Vận chuyển pallet vào khu vực đệm kiểm đếm"] --> W4
    
    W4["<b>Bước 4: Kiểm Đếm Số Lượng & Kiểm Tra Chất Lượng (KCS)</b><br>So sánh số đếm thực tế vs Packing List. Kiểm tra ngoại quan ẩm mốc, dập vỡ"] --> W5
    
    W5{"<b>Bước 5: Có Hàng Hư Hỏng Hoặc Thiếu Hụt?</b>"}
    
    W5 -- "⚠️ CÓ HÀNG HƯ HỎNG / THIẾU" --> W_SPLIT["<b>Bước 5.1: Tách Hàng Hỏng Vào Kho Cách Ly (Rejected)</b><br>Lập Biên bản thừa thiếu hàng (Discrepancy Report) gửi Kế toán đòi bồi thường TK 1388"] --> W6
    
    W5 -- "🟢 ĐỦ 100% LÀNH LẶN" --> W6["<b>Bước 6: Tạo Phiếu Nhập Kho (Purchase Receipt - PR)</b><br><b>CHỈ GHI NHẬN SỐ HÀNG LÀNH LẶN ĐẠT CHUẨN</b> vào Kho Chính (TK 156)"] --> W7
    
    W7["<b>Bước 7: Chốt Mốc M09_WH_RECEIPT Hoàn Tất</b><br>Ký biên bản giao nhận với lái xe, trả vỏ cont rỗng đúng hạn tránh phạt giữ vỏ"] --> W_OUT
    
    W_OUT(["📤 <b>ĐẦU RA:</b> Phiếu PR hợp lệ, hàng nằm an toàn trong kho, vỏ cont đã trả"])

    style W_IN fill:#FEF2F2,stroke:#DC2626,stroke-width:2px,color:#0F172A
    style W1 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style W2 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style W5 fill:#FEF08A,stroke:#CA8A04,stroke-width:2px,color:#713F12
    style W_BLOCK fill:#7F1D1D,stroke:#F87171,stroke-width:2px,color:#FFFFFF
    style W_SURVEY fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style W_SPLIT fill:#FEF3C7,stroke:#D97706,stroke-width:2px,color:#78350F
    style W_OUT fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#14532D
    linkStyle default stroke:#DC2626,stroke-width:2px;
```

### 6.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Thủ Kho)
* **Chứng từ ERPNext:** `Purchase Receipt` (PR), `Stock Entry`, `Quality Inspection` (KCS).
* **Rào chắn 1 (Blind Financial Protection):** Giao diện của Thủ kho bị ẩn hoàn toàn các cột: Đơn giá mua (Rate), Số tiền (Amount), Chi phí phân bổ (Landed Cost) và Lợi nhuận. Thủ kho chỉ tập trung kiểm soát **Số lượng thực đếm (Accepted Qty)** và **Số lượng từ chối (Rejected Qty)**.
* **Rào chắn 2 (Stage Gate Physical Unload):** Thủ kho bị cấm dỡ hàng nếu hệ thống chưa ghi nhận cờ `Customs Cleared`. Điều này bảo vệ doanh nghiệp tuyệt đối khỏi rủi ro bị cơ quan hải quan xử phạt hình sự về hành vi "Tự ý tiêu thụ hàng hóa đang chịu sự giám sát hải quan".
