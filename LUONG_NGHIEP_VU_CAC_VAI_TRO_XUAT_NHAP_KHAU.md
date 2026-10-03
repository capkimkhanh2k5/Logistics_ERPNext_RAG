# 🌐 BẢN ĐẶC TẢ QUY TRÌNH TÁC NGHIỆP PHÂN VAI TOÀN DIỆN XUẤT NHẬP KHẨU
*(Comprehensive Role-Based Standard Operating Procedures & Modular Workflows on ERPNext v15)*

Tài liệu thiết kế hoàn chỉnh hai luồng nghiệp vụ kinh điển của Doanh nghiệp Thương mại Quốc tế tại Việt Nam:
* **🔵 PHẦN I: LUỒNG NHẬP KHẨU (INBOUND SUPPLY CHAIN & LANDED COST VAS 02)**
* **🟢 PHẦN II: LUỒNG XUẤT KHẨU (OUTBOUND SALES, CONTAINER STUFFING & L/C SETTLEMENT)**

---

# 🔵 PHẦN I: QUY TRÌNH TÁC NGHIỆP LUỒNG NHẬP KHẨU (INBOUND PROCUREMENT)

## 1. TỔNG QUAN DÒNG CHẢY BÀN GIAO GIỮA 6 VỊ TRÍ NHẬP KHẨU (INBOUND HANDSHAKE)

Sơ đồ mô tả dòng bàn giao liên vị trí mức cao giữa 6 bộ phận tác nghiệp. Dòng màu xanh thể hiện tiến trình thuận chiều chuẩn; các đường nét đứt màu đỏ thể hiện các phản hồi trả ngược về khi phát sinh sự cố cần điều chỉnh:

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#38BDF8',
    'lineColor': '#38BDF8',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart LR
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef role fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;

    R1["<b>1. THU MUA</b><br>Hợp đồng & Đơn PO"]:::role
    R2["<b>2. GIÁM ĐỐC / CFO</b><br>Duyệt PO & Chi cọc"]:::role
    R3["<b>3. KẾ TOÁN</b><br>Chi cọc 30%"]:::role
    R4["<b>4. LOGISTICS</b><br>Tàu biển & Vận đơn B/L"]:::role
    R5["<b>5. HẢI QUAN</b><br>Tờ khai VNACCS"]:::role
    R6["<b>6. THỦ KHO</b><br>Dỡ hàng & Nhận PR"]:::role

    R1 ==>|"Trình PO"| R2
    R2 ==>|"Lệnh chi"| R3
    R3 ==>|"Xác nhận cọc"| R4
    R4 ==>|"Gửi B/L & Chứng từ"| R5
    R5 ==>|"Tờ khai tính thuế"| R3
    R3 ==>|"Nộp thuế kho bạc"| R5
    R5 ==>|"Thông quan (M07)"| R4
    R4 ==>|"Điều xe rút cont (M08)"| R6
    R6 ==>|"Phiếu PR (M09)"| R3
    R3 ==>|"Quyết toán giá vốn"| R2

    %% Các đường trả ngược về khi có biến cố
    R2 -. "[Bác bỏ đơn PO]" .-> R1
    R5 -. "[Lệch C/O, B/L]" .-> R1
    R6 -. "[Hàng dập nát/thiếu]" .-> R3
    R2 -. "[Vượt chi phí > 10%]" .-> R4

    linkStyle default stroke:#38BDF8,stroke-width:2px;
```

---

## 2. VỊ TRÍ CHUYÊN VIÊN THU MUA (BUYER)

### 2.1. Sơ đồ Luồng Tác nghiệp của Thu Mua

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#38BDF8',
    'lineColor': '#38BDF8',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    B_IN(["<b>ĐẦU VÀO:</b> Yêu cầu mua sắm (Material Request) / Kế hoạch kinh doanh"]):::input --> B1
    B1["<b>Bước 1: Đàm phán với Nhà máy Quốc tế</b><br>Chốt đơn giá, số lượng, điều kiện Incoterms (CIF/FOB), tiến độ sản xuất"] --> B2
    B2["<b>Bước 2: Lập Đơn Mua Hàng (Purchase Order)</b><br>Nhập đơn giá ngoại tệ USD, tỷ giá kế hoạch, dự toán chi phí lô hàng"] --> B3
    B3["<b>Bước 3: Khởi tạo Hồ sơ Mẹ Trade Case</b><br>Tạo mã <b>IMP-2026-xxxxx</b> để quản lý xuyên suốt vòng đời"] --> B4
    B4{"<b>Bước 4: Trình ký Giám Đốc / CFO</b><br>Đơn PO có được duyệt?"}:::decision
    
    B4 -- "[BÁC BỎ: Giá cao / Vượt ngân sách]" --> B_REVISE["<b>Bước 4.1: Đàm phán lại với Nhà máy</b><br>Thương lượng giảm giá số lượng lớn hoặc đổi điều khoản thanh toán"]:::error
    B_REVISE --> B2
    
    B4 -- "[PHÊ DUYỆT]" --> B5["<b>Bước 5: Ký Hợp Đồng Ngoại Thương Chính Thức</b><br>Bàn giao hợp đồng sang Kế toán để chi tiền cọc 30%"] --> B6
    
    B6["<b>Bước 6: Theo dõi Sản Xuất & Tàu Chạy (M04)</b><br>Khi tàu rời cảng xuất: Hệ thống khóa cứng PO (không được sửa giá/SL)"] --> B7{"<b>Bước 7: Hải Quan Rà Soát Chứng Từ</b><br>Có sai lệch C/O hoặc Hóa đơn?"}:::decision
    
    B7 -- "[SAI LỆCH C/O HOẶC INVOICE]" --> B_AMEND["<b>Bước 7.1: Đòi Nhà máy cấp lại C/O Form E sửa đổi</b><br>Yêu cầu phát hành bản đính chính Amendment trong 48h để kịp thông quan"]:::error
    B_AMEND --> B7
    
    B7 -- "[HỢP LỆ]" --> B_OUT(["<b>ĐẦU RA:</b> Hợp đồng chuẩn, PO đã duyệt, C/O hợp lệ"]):::success

    linkStyle default stroke:#38BDF8,stroke-width:2px;
```

### 2.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Thu Mua)
* **Chứng từ ERPNext tạo ra:** `Material Request`, `Purchase Order` (PO), `Trade Case` (`IMP-.YYYY.-.#####`).
* **Rào chắn 1 (Tolerance Limit):** Hệ thống chặn không cho tạo đơn PO vượt quá hạn mức công nợ tối đa đã cấp cho nhà cung cấp.
* **Rào chắn 2 (Immutable PO at M04):** Ngay khi Chuyến tàu đạt mốc `M04_ETD` (Tàu rời cảng bốc), hệ thống tự động khóa trạng thái đơn PO sang Read-only. Thu mua không được tự ý sửa số lượng hoặc đơn giá để che giấu chênh lệch.
* **Xử lý khi bị trả ngược:** Nếu CFO từ chối hoặc Hải quan báo C/O sai tiêu chí, Thu mua là đầu mối liên hệ nhà máy nước ngoài để đàm phán lại trong vòng 24 - 48h.

---

## 3. VỊ TRÍ BAN GIÁM ĐỐC / GIÁM ĐỐC TÀI CHÍNH (CFO)

### 3.1. Sơ đồ Luồng Tác nghiệp của Giám Đốc / CFO

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#F59E0B',
    'lineColor': '#F59E0B',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    C_IN(["<b>ĐẦU VÀO:</b> Đơn PO trình ký / Tờ trình chi cọc / Báo cáo Tháp chỉ huy"]):::input --> C1
    C1{"<b>Bước 1: Thẩm Định Đơn PO</b><br>So khớp Ngân sách kế hoạch & Đơn giá thị trường?"}:::decision
    
    C1 -- "[KHÔNG HỢP LÝ]" --> C_REJ_PO["<b>Bác bỏ đơn PO:</b> Yêu cầu Thu mua đàm phán lại với Nhà máy"]:::error
    C1 -- "[HỢP LÝ]" --> C2["<b>Bước 2: Ký Duyệt Đơn Mua Hàng PO</b><br>Kích hoạt phân quyền cho phép Kế toán lập phiếu chi"] --> C3
    
    C3["<b>Bước 3: Ký Duyệt Ủy Nhiệm Chi Cọc 30%</b><br>Phê duyệt xuất quỹ Vietcombank USD chuyển ra nước ngoài"] --> C4
    
    C4["<b>Bước 4: Giám Sát Tháp Chỉ Huy (Control Tower)</b><br>Theo dõi cảnh báo đếm ngược phạt bãi cont, trễ tàu, vượt dự toán"] --> C5
    
    C5{"<b>Bước 5: Thẩm Định Đóng Lô Hàng (Closed)</b><br>Chi phí thực tế có vượt ngân sách > 10%?"}:::decision
    
    C5 -- "[TRONG ĐỊNH MỨC <= 10%]" --> C_OK["<b>Bước 5.1: Phê duyệt đóng lô hàng</b><br>Chốt giá vốn bất biến vào Báo cáo Tài chính"]
    
    C5 -- "[VƯỢT ĐỊNH MỨC > 10%]" --> C6{"<b>Bước 6: Thẩm Định Ngoại Lệ</b><br>Lý do vượt có chính đáng?<br>(Lệch tỷ giá USD vs Lệch cước tàu)"}:::decision
    
    C6 -- "[BÁC BỎ]" --> C_REJ_COST["<b>Bác bỏ:</b> Yêu cầu Logistics/Kế toán truy cứu trách nhiệm & đàm phán giảm cước"]:::error
    C6 -- "[CHẤP THUẬN]" --> C_AUTH["<b>Bước 6.1: Nhập Mã Ủy Quyền Cấp Cao (CFO Override)</b><br>Cho phép đóng quyết toán lô hàng vượt ngân sách"] --> C_OK
    
    C_OK --> C_OUT(["<b>ĐẦU RA:</b> Lô hàng hoàn tất (cost_status = Closed), giá vốn chốt"]):::success

    linkStyle default stroke:#F59E0B,stroke-width:2px;
```

### 3.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (CFO)
* **Quyền hạn tối cao:** Duyệt PO giá trị lớn, duyệt chi ngoại tệ, duyệt ngoại lệ chi phí vượt ngân sách $> 10\%$.
* **Rào chắn 1 (Two-Man Rule):** Kế toán viên không thể tự ý chuyển tiền nếu không có chữ ký điện tử hoặc phê duyệt của Giám đốc/CFO.
* **Rào chắn 2 (Stage Gate 3 - Over Budget Lock):** Hệ thống phân quyền cứng: Chỉ Role `CFO` hoặc `System Manager` mới có quyền chuyển `cost_status` sang `Closed` khi lô hàng có `cost_variance_pct > 10%`. Nhân viên cấp dưới hoàn toàn bị khóa chức năng này.

---

## 4. VỊ TRÍ KẾ TOÁN GIÁ VỐN & CÔNG NỢ (ACCOUNTANT)

### 4.1. Sơ đồ Luồng Tác nghiệp của Kế Toán

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#10B981',
    'lineColor': '#10B981',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    A_IN(["<b>ĐẦU VÀO:</b> PO đã duyệt / Tờ khai thuế / Hóa đơn cước / Phiếu nhập kho PR"]):::input --> A1
    A1["<b>Bước 1: Chi Tạm Ứng Cọc 30% Tiền Hàng</b><br>Lập Payment Entry (Nợ 331 / Có 1121 VCB USD)<br>[Bắt buộc đánh dấu: Is Advance]"] --> A2
    A2["<b>Bước 2: Nộp Thuế Hải Quan Vào Kho Bạc</b><br>Căn cứ Tờ khai VNACCS ➔ Nộp Thuế NK (TK 3333) & Thuế GTGT (TK 33312)"] --> A3
    A3["<b>Bước 3: Thu Thập Hóa Đơn Dịch Vụ Cảng & Forwarder</b><br>Cước biển, phí D/O, nâng hạ, kiểm định, cước bộ. Kiểm tra tính hợp lệ e-Invoice"] --> A4
    A4["<b>Bước 4: Chạy Phân Bổ Giá Vốn (Landed Cost Voucher - LCV)</b><br>• Cước tàu biển: Phân bổ theo Thể tích (CBM)<br>• Thuế & Phí khác: Phân bổ theo Trị giá hàng (Customs Value)"] --> A5
    A5["<b>Bước 5: Bóc Tách Chênh Lệch Dự Toán vs Thực Tế</b><br>Hệ thống tự bóc tách: Lệch Giá cước hãng tàu vs Lệch Tỷ giá USD/VND"] --> A6
    
    A6{"<b>Bước 6: Kho Báo Hàng Hư Hỏng / Mất Mát?</b><br>Có biên bản giám định hiện trường?"}:::decision
    
    A6 -- "[CÓ HÀNG HỎNG]" --> A_CLAIM["<b>Bước 6.1: Hạch toán Phải Thu Bồi Thường (TK 1388)</b><br>Ghi nợ TK 1388 đòi Bảo hiểm/NCC. Không gộp vào giá vốn hàng tồn"]:::error --> A7
    A6 -- "[ĐỦ HÀNG 100%]" --> A7
    
    A7["<b>Bước 7: Quyết Toán Hóa Đơn Mua Hàng (Purchase Invoice - PI)</b><br>ERPNext tự động cấn trừ 30% tiền cọc ➔ Kế toán lập lệnh chi 70% còn lại"] --> A8
    
    A8{"<b>Bước 8: Kiểm Tra Cổng Ngân Sách Lô Hàng</b><br>Tổng chi phí thực tế có vượt > 10% dự toán?"}:::decision
    
    A8 -- "[VƯỢT > 10%]" --> A_REP["<b>Bước 8.1: Lập Tờ Trình Vượt Ngân Sách Trình CFO</b><br>Phân tích rõ nguyên nhân phát sinh chi phí"]:::error
    A_REP --> A9{"<b>CFO Có Duyệt Ngoại Lệ?</b>"}:::decision
    A9 -- "[BÁC BỎ]" --> A_DISPUTE["<b>Bước 8.2: Phối hợp Logistics bắt Forwarder giảm trừ</b><br>Yêu cầu nhà xe/forwarder phát hành hóa đơn điều chỉnh giảm"]:::error --> A4
    A9 -- "[PHÊ DUYỆT]" --> A_CLOSE
    
    A8 -- "[TRONG ĐỊNH MỨC <= 10%]" --> A_CLOSE["<b>Bước 9: Đóng Quyết Toán Lô Hàng (Closed)</b><br>Chốt giá vốn đơn vị vào thẻ kho và sổ cái kế toán"]
    
    A_CLOSE --> A_OUT(["<b>ĐẦU RA:</b> Giá vốn đích thực (Landed Cost) đã chốt, công nợ sạch"]):::success

    linkStyle default stroke:#10B981,stroke-width:2px;
```

### 4.2. Bảng Hạch Toán Kế Toán Chuẩn Mực & Rào Chắn Poka-Yoke (Kế Toán)
* **Bảng tài khoản chuẩn mực kế toán Việt Nam (VAS 02 / Thông tư 200/2014/TT-BTC & IAS 2):**
  * **1. Tạm ứng cọc tiền hàng:** Nợ TK 331 (Phải trả NCC) / Có TK 1122 (Tiền gửi ngân hàng ngoại tệ USD).
  * **2. Nộp thuế Hải quan vào Kho bạc Nhà nước:**
    * *Thuế nhập khẩu (tính vào giá gốc hàng tồn kho):* Nợ TK 3333 / Có TK 1121 (VND).
    * *Thuế GTGT hàng nhập khẩu (được khấu trừ, TUYỆT ĐỐI KHÔNG TÍNH VÀO GIÁ GỐC):* Nợ TK 33312 / Có TK 1121 (VND); đồng thời ghi nhận khấu trừ: Nợ TK 13312 (Thuế GTGT đầu vào hàng nhập khẩu) / Có TK 33312.
  * **3. Nhận hàng vào kho (Purchase Receipt - PR):** Nợ TK 1561 (Hàng hóa kho chính) / Có TK 3388 hoặc TK 331 (Tạm tính theo PO).
  * **4. Xử lý hàng hư hỏng / thiếu hụt (Compound Journal Entry & Rejected Warehouse):**
    * Khi mở cont phát hiện hàng hỏng, kế toán hạch toán định khoản phức cân bằng:
      * **Nợ TK 1561:** Giá trị hàng đạt chuẩn thực nhập (Accepted Qty).
      * **Nợ TK 1388:** Giá trị hàng hư hỏng/thiếu hụt chờ đòi bảo hiểm hoặc nhà máy bồi thường (Rejected Qty).
      * **Có TK 331:** 100% Tổng giá trị hóa đơn gốc của nhà cung cấp.
    * *Cơ chế ERPNext:* Thiết lập Kho hàng cách ly (`Rejected Warehouse`). Số lượng hàng hỏng được ghi nhận riêng biệt, không tính giá vốn thương mại xuất bán.
  * **5. Phân bổ chi phí mua hàng (Landed Cost Voucher - LCV):**
    * *Chi phí được vốn hóa (tính vào giá gốc TK 156 theo VAS 02):* Cước vận tải biển/hàng không, phí làm thủ tục hải quan, phí nâng hạ cảng, phí D/O, bảo hiểm hàng hải, phí lưu kho bãi thông thường tại cảng trong thời gian chờ thông quan hợp lý $\rightarrow$ Nợ TK 1562 (Chi phí thu mua) / Có TK 331 (Forwarder/Hãng tàu).
    * *Chi phí KHÔNG ĐƯỢC VỐN HÓA:* Tiền phạt lưu container tại bãi cảng (Demurrage), phạt lưu vỏ (Detention), tiền phạt vi phạm hải quan do lỗi chậm trễ thủ tục $\rightarrow$ Bắt buộc hạch toán vào Chi phí quản lý kinh doanh trong kỳ: Nợ TK 642 hoặc Nợ TK 811 / Có TK 331 hoặc TK 1121.
    * *Phí lưu kho sau khi hàng đã về kho công ty:* Hạch toán vào Chi phí lưu kho định kỳ: Nợ TK 642 / Có TK 331, không tính vào giá gốc hàng tồn kho.
  * **6. Quyết toán Hóa đơn mua hàng (Purchase Invoice - PI):** Lập hóa đơn PI đối chiếu công nợ NCC ngoại, tự động cấn trừ số tiền cọc đã tạm ứng; phần còn lại thanh toán: Nợ TK 331 / Có TK 1122 (USD). Lệch tỷ giá ghi nhận vào TK 515 (lãi) hoặc TK 635 (lỗ).
  * **7. Chi phí về trễ sau khi đã đóng sổ:** Lập `Additional Landed Cost Voucher`. Nếu hàng trong kho đã xuất bán hết, hệ thống tự động kết chuyển thẳng vào Giá vốn hàng bán trong kỳ: Nợ TK 632 / Có TK 331, bảo vệ sổ cái không bị lỗi "Tồn kho âm".
* **Rào chắn 1 (Auto Advance Deduction):** Khi mở Purchase Invoice, hệ thống tự động kiểm tra bảng tạm ứng và cấn trừ đúng tỷ lệ cọc (tham số `advance_deposit_pct`, mặc định 30%). Kế toán không thể thanh toán trùng 100% tiền hàng lần thứ hai.
* **Rào chắn 2 (VAS 02 Non-Capitalization Enforcement):** Tiền phạt lưu bãi (Demurrage) và phạt vi phạm hải quan tuyệt đối không được chọn vào LCV, hệ thống tự động khóa mã tài khoản chi phí phạt sang TK 811/642.

---

## 5. VỊ TRÍ ĐIỀU PHỐI LOGISTICS (COORDINATOR)

### 5.1. Sơ đồ Luồng Tác nghiệp của Điều Phối Logistics

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#A855F7',
    'lineColor': '#A855F7',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    L_IN(["<b>ĐẦU VÀO:</b> Hợp đồng ngoại thương / Thông báo hàng sẵn sàng (Cargo Ready)"]):::input --> L1
    L1["<b>Bước 1: Khởi Tạo Chuyến Tàu Con Trade Shipment</b><br>Mở mã <b>TS-2026-xxxxx</b> liên kết với Trade Case mẹ. Ghi nhận Incoterm, Cảng đi/đến"] --> L2
    L2["<b>Bước 2: Thu Thập Vận Đơn (B/L) & Dữ Liệu Container</b><br>Nhận Master B/L, House B/L, cập nhật danh sách Container (Số Cont, Số Seal, CBM, KGS)"] --> L3
    L3["<b>Bước 3: Theo Dõi 9 Mốc Hành Trình Chuẩn (M01 ➔ M05)</b><br>Giám sát ngày tàu chạy thực tế (M04_ETD) và ngày tàu dự kiến cập cảng (M05_ETA)"] --> L4
    
    L4{"<b>Bước 4: Tàu Có Bị Delay / Rớt Tàu (Rolled)?</b><br>Hãng tàu thông báo trễ lịch?"}:::decision
    
    L4 -- "[TÀU BỊ TRỄ LỊCH]" --> L_REVISE["<b>Bước 4.1: Cập nhật ETA mới & Tính lại Hạn Bãi</b><br>Hệ thống tự cộng thêm ngày dỡ mới vào Demurrage Deadline.<br>Logistics gửi công văn xin hãng tàu nới thêm Free-time"]:::error --> L5
    L4 -- "[ĐÚNG LỊCH TRÌNH]" --> L5
    
    L5["<b>Bước 5: Kích Hoạt Đếm Ngược Miễn Phí Lưu Bãi (Free-Time)</b><br>Tàu cập cảng (M05) ➔ Hệ thống đếm ngược 7 ngày miễn phí bãi cảng Cát Lái/Hải Phòng"] --> L6
    
    L6{"<b>Bước 6: Kiểm Tra Cảnh Báo Sớm Hạn Bãi?</b><br>Còn <= 3 ngày mà chưa xong thủ tục?"}:::decision
    
    L6 -- "[CÒN <= 3 NGÀY]" --> L_WARN["<b>Bắn Cảnh Báo Khẩn Cấp (Alarm):</b><br>Thúc ép Hải quan và Kế toán nộp thuế giải phóng hàng ngay để tránh phạt > 100$/ngày/cont"]:::error --> L7
    L6 -- "[AN TOÀN > 3 NGÀY]" --> L7
    
    L7{"<b>Bước 7: Cổng Stage Gate Rút Hàng:</b><br>Tờ khai Hải quan đã có cờ Cleared (M07)?"}:::decision
    
    L7 -- "[CHƯA THÔNG QUAN]" --> L_BLOCK["<b>CHẶN LẠI:</b> Tuyệt đối không điều xe kéo cont ra khỏi cảng<br>(Tránh xe đầu kéo chờ tại bãi phát sinh phí lưu ca xe)"]:::error
    L_BLOCK --> L7
    
    L7 -- "[ĐÃ THÔNG QUAN]" --> L8["<b>Bước 8: Phát Lệnh Điều Xe Đầu Kéo (Delivery Order)</b><br>Điều xe ra cảng nâng cont và vận chuyển về kho nhà máy an toàn"] --> L_OUT
    
    L_OUT(["<b>ĐẦU RA:</b> Container về tới cổng kho nguyên vẹn số seal"]):::success

    linkStyle default stroke:#A855F7,stroke-width:2px;
```

### 5.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Logistics)
* **Chứng từ ERPNext:** `Trade Shipment` (`TS-.YYYY.-.#####`), `Trade Shipment Container`, `Trade Shipment Milestone`.
* **Công thức tự động hóa:**
  $$\text{Demurrage Deadline} = \text{ETA Actual} + \text{demurrage\_free\_days}$$
  $$\text{Detention Deadline} = \text{ETA Actual} + \text{detention\_free\_days}$$
* **Rào chắn 1 (Stage Gate Trucking Lock):** Hệ thống chặn không cho phép nhân viên logistics in Phiếu điều xe hoặc xác nhận mốc dỡ hàng nếu Tờ khai liên kết chưa đạt `clearance_status = "Cleared"`.
* **Rào chắn 2 (Demurrage 3-Day Early Warning):** Khi `today() >= Demurrage Deadline - 3 ngày`, hệ thống tự động đổi màu dòng container sang ĐỎ và gửi cảnh báo trực tiếp đến Trưởng phòng Logistics.

---


### 5.3. Bảng Chuẩn 9 Cột Mốc Hành Trình Chuyển Giao (M01 - M09)

| Mã Mốc | Tên Cột Mốc Chuẩn | Ý Nghĩa Nghiệp Vụ Ngoại Thương | Đơn Vị Cập Nhật | Rào Chắn Poka-Yoke & Cổng Kiểm Soát Gắn Liền |
| :---: | :--- | :--- | :---: | :--- |
| **M01** | `Booking Confirmed` | Hãng tàu xác nhận đặt chỗ thành công | 🚢 Logistics | Kiểm tra hợp đồng ngoại thương & đơn giá cước vận tải |
| **M02** | `Empty Container Released` | Hãng tàu cấp lệnh lấy vỏ container rỗng tại bãi depot | 🚢 Logistics / 📦 Kho | Kiểm tra 7 điểm vỏ cont rỗng (khô ráo, sạch, trần không lọt sáng) |
| **M03** | `Cargo Gate-in` | Container đóng hàng đã hạ bãi cảng xuất | 🚢 Logistics | Bắt buộc có Phiếu cân VGM & nộp SI trước giờ Cut-off |
| **M04** | `Vessel Departed (ETD Actual)` | Tàu rời cảng bốc, phát hành Vận đơn B/L gốc | 🚢 Logistics / Hãng tàu | **Khóa cứng đơn mua PO / đơn bán SO (Immutable Lock)** |
| **M05** | `Vessel Arrived (ETA Actual)` | Tàu cập cảng đến (POD), dỡ cont lên bãi cảng | 🚢 Logistics / Hãng tàu | **Kích hoạt đồng hồ đếm ngược Free-time lưu bãi** (tham số cấu hình) |
| **M06** | `Customs Declaration Registered` | Đăng ký tờ khai điện tử VNACCS (chuẩn 12 ký tự) | 🏛️ Hải Quan | **Cổng 1 (Document Ready Gate):** Đủ 100% Invoice, PL, C/O hợp lệ |
| **M07** | `Customs Cleared` | Hải quan phê duyệt thông quan lô hàng | 🏛️ Hải Quan / 💰 Kế toán | **Cổng 2 (Clearance Gate):** Cho phép nhập Kho Chính (TK 156) |
| **M08** | `Port Gate-out / Delivery Order` | Lấy lệnh giao hàng D/O, điều xe rút cont khỏi cảng | 🚢 Logistics | Chặn rút cont nếu chưa thông quan (trừ trường hợp Kho Bảo Quản) |
| **M09** | `Warehouse Receipt (WH_RECEIPT)` | Hàng dỡ an toàn vào kho, ký PR, trả vỏ cont | 📦 Thủ Kho | **Stage Gate 2 Submit PR:** Tự động hoàn tất chuyến tàu `Trade Shipment` |

---

## 6. VỊ TRÍ CHUYÊN VIÊN HẢI QUAN (CUSTOMS)

### 6.1. Sơ đồ Luồng Tác nghiệp của Chuyên Viên Hải Quan

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#EC4899',
    'lineColor': '#EC4899',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    H_IN(["<b>ĐẦU VÀO:</b> Bộ chứng từ vận tải (B/L, Commercial Invoice, Packing List, C/O)"]):::input --> H1
    H1["<b>Bước 1: Kiểm Tra Checklist 8 Chứng Từ Bắt Buộc</b><br>Rà soát Hợp đồng, Hóa đơn, Vận đơn, C/O, Giấy phép chuyên ngành"] --> H2
    
    H2{"<b>Bước 2: Bộ Chứng Từ Có Khớp 100%?</b><br>Sai lệch tên hàng, mã HS hoặc thiếu tiêu chí C/O?"}:::decision
    
    H2 -- "[SAI LỆCH / THIẾU C/O]" --> H_REJ["<b>Bước 2.1: Từ Chối Chứng Từ & Giữ Cờ Not Ready</b><br>Báo Thu mua/Nhà máy phát hành bản đính chính C/O Amendment"]:::error --> H1
    
    H2 -- "[ĐỦ 100% HỢP LỆ]" --> H3["<b>Bước 3: Mở Cổng Stage Gate 1 (Document Ready)</b><br>Khai báo Giấy phép chuyên ngành <b>Import Permit</b> (nếu có)"] --> H4
    
    H4["<b>Bước 4: Truyền Tờ Khai Hải Quan Điện Tử VNACCS</b><br>Tạo <b>Customs Declaration</b> chuẩn 12 ký tự (CV 5922/TCHQ-VNACCS). Hệ thống tự khớp Tỷ giá tuần BTC"] --> H5
    
    H5{"<b>Bước 5: Kết Quả Phân Luồng Tờ Khai?</b><br>Hệ thống hải quan trả về luồng nào?"}:::decision
    
    H5 -- "[LUỒNG XANH]" --> H_PASS["<b>Bước 5.1: Luồng Xanh (Green)</b><br>Miễn kiểm tra hồ sơ và hàng hóa thực tế"] --> H_CLEAR
    
    H5 -- "[LUỒNG VÀNG]" --> H_YELLOW["<b>Bước 5.2: Luồng Vàng (Yellow)</b><br>In bộ hồ sơ giấy mang đến Chi cục HQ đối chiếu chứng từ"]
    
    H5 -- "[LUỒNG ĐỎ]" --> H_RED["<b>Bước 5.3: Luồng Đỏ (Red - Kiểm Hóa)</b><br>Phối hợp Logistics đưa cont vào bãi kiểm hóa mở thùng kiểm tra thực tế"]:::error
    
    H_YELLOW --> H6{"<b>Hải quan nghi vấn tham vấn giá?</b>"}:::decision
    H6 -- "[BỊ THAM VẤN]" --> H_CONSULT["Chứng minh trị giá giao dịch"] --> H_CLEAR
    H6 -- "[CHẤP THUẬN]" --> H_CLEAR
    
    H_RED --> H7{"<b>Kiểm hóa thực tế có khớp tờ khai?</b>"}:::decision
    H7 -- "[SAI MÃ HS / THỪA THIẾU]" --> H_FINE["<b>Bị lập biên bản vi phạm hành chính:</b><br>Ấn định thuế bổ sung + Phạt tiền (Hạch toán riêng TK 811)"]:::error --> H_CLEAR
    H7 -- "[TRÙNG KHỚP 100%]" --> H_CLEAR

    H_CLEAR["<b>Bước 5.4: Quyết Định Thông Quan (Customs Approval)</b><br>Hồ sơ hợp lệ, đủ điều kiện thông quan"] --> H8
    
    H8["<b>Bước 6: Kế Toán Nộp Thuế & Chốt Thông Quan (Cleared)</b><br>Cập nhật số tờ khai VNACCS 12 ký tự và mốc <b>M07_CUSTOMS_CLEAR</b> lên lô hàng"] --> H_OUT
    
    H_OUT(["<b>ĐẦU RA:</b> Tờ khai hải quan thông quan hoàn tất, đèn xanh cho kho"]):::success

    linkStyle default stroke:#EC4899,stroke-width:2px;
```

### 6.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Hải Quan)
* **Chứng từ ERPNext:** `Trade Document Item`, `Import Permit`, `Customs Declaration` (Số tờ khai 12 ký tự: `1058249xxxxx0`).
* **Ứng dụng AI/RAG:** Tại Bước 1, chuyên viên sử dụng **AI RAG Legal Assistant** để tra cứu văn bản quy phạm pháp luật hải quan, trích dẫn 6 Quy tắc phân loại hàng hóa (GIR), chú giải Chi tiết Chương/Nhóm để xác định mã HS chính xác và cảnh báo các rủi ro tham vấn giá. Chuyên viên con người là người kiểm duyệt và bấm Duyệt cuối cùng.
* **Rào chắn 1 (12-Character VNACCS Standard Validation - CV 5922/TCHQ-VNACCS):** 
  * Căn cứ Công văn 5922/TCHQ-VNACCS của Tổng cục Hải quan, số tờ khai điện tử VNACCS gồm **12 ký tự**:
    * **11 ký tự đầu:** Là mã số tờ khai chính thức cố định, dùng làm khóa duy nhất liên kết với lô hàng `Trade Case` và `Trade Shipment`.
    * **Ký tự thứ 12:** Là số lần sửa đổi bổ sung (mặc định là `0` khi khai lần đầu, tăng dần `1, 2, 3...` khi có tờ khai sửa đổi bổ sung theo mẫu AMA/AMC).
  * Hệ thống tự động kiểm tra định dạng 12 ký tự; nếu người dùng nhập 11 ký tự thì hệ thống tự động gán ký tự thứ 12 là `0`.
* **Rào chắn 2 (Customs Rate Auto-Lookup):** Khóa cứng không cho nhân viên tự nhập tỷ giá tính thuế, bắt buộc hàm `fetch_customs_exchange_rate` lấy tự động từ bảng công bố hàng tuần của Bộ Tài chính.

---

## 7. VỊ TRÍ THỦ KHO VẬT LÝ (WAREHOUSE KEEPER)

### 7.1. Sơ đồ Luồng Tác nghiệp của Thủ Kho

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#EF4444',
    'lineColor': '#EF4444',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    W_IN(["<b>ĐẦU VÀO:</b> Xe container đến cổng kho công ty + Giấy giao nhận vận tải"]):::input --> W1
    W1{"<b>Bước 1: Cổng Stage Gate Thông Quan & Loại Kho Tiếp Nhận</b><br>Hàng đã Cleared (M07) hay về Kho Bảo Quản Chờ Thông Quan?"}:::decision
    
    W1 -- "[NỢ C/O: KHO BẢO QUẢN]" --> W_SUSP["<b>Tiếp nhận Kho Bảo Quản (Suspense Warehouse):</b><br>Kéo cont về kho tránh phạt bãi cảng. Khóa cờ xuất bán, không ghi nhận TK 156"] --> W2
    W1 -- "[CHƯA THÔNG QUAN & KHÔNG CÓ LỆNH]" --> W_BLOCK["<b>CẤM CẮT CHÌ DỠ HÀNG VÀO KHO CHÍNH:</b><br>Giữ nguyên cont tại cổng để tuân thủ pháp lý hải quan"]:::error --> W1
    W1 -- "[ĐÃ THÔNG QUAN (M07)]" --> W2{"<b>Bước 2: Kiểm Tra Số Container & Chì Seal</b><br>Số chì có nguyên vẹn, khớp 100% với B/L gốc?"}:::decision
    
    W2 -- "[ĐỨT CHÌ / SAI SỐ SEAL]" --> W_SURVEY["<b>Bước 2.1: GIỮ NGUYÊN HIỆN TRƯỜNG & LẬP BIÊN BẢN:</b><br>Chụp ảnh chì đứt, mời lái xe ký biên bản bất thường.<br>Mời cơ quan giám định SGS & Bảo hiểm đến đồng kiểm"]:::error --> W3
    
    W2 -- "[CHÌ SEAL NGUYÊN VẸN]" --> W3["<b>Bước 3: Cắt Chì, Mở Cửa Cont & Dỡ Hàng</b><br>Vận chuyển pallet vào khu vực đệm kiểm đếm"] --> W4
    
    W4["<b>Bước 4: Kiểm Đếm Số Lượng & Kiểm Tra Chất Lượng (KCS)</b><br>So sánh số đếm thực tế vs Packing List. Kiểm tra ngoại quan ẩm mốc, dập vỡ"] --> W5
    
    W5{"<b>Bước 5: Có Hàng Hư Hỏng Hoặc Thiếu Hụt?</b>"}:::decision
    
    W5 -- "[CÓ HÀNG HƯ HỎNG / THIẾU]" --> W_SPLIT["<b>Bước 5.1: Tách Hàng Hỏng Vào Kho Cách Ly (Rejected)</b><br>Lập Biên bản thừa thiếu hàng gửi Kế toán đòi bồi thường TK 1388"]:::error --> W6
    
    W5 -- "[ĐỦ 100% LÀNH LẶN]" --> W6["<b>Bước 6: Tạo Phiếu Nhập Kho (Purchase Receipt - PR)</b><br><b>CHỈ GHI NHẬN SỐ HÀNG LÀNH LẶN ĐẠT CHUẨN</b> vào Kho Chính (TK 156)"] --> W7
    
    W7["<b>Bước 7: Chốt Mốc M09_WH_RECEIPT Hoàn Tất</b><br>Ký biên bản giao nhận với lái xe, trả vỏ cont rỗng đúng hạn tránh phạt giữ vỏ"] --> W_OUT
    
    W_OUT(["<b>ĐẦU RA:</b> Phiếu PR hợp lệ, hàng nằm an toàn trong kho, vỏ cont đã trả"]):::success

    linkStyle default stroke:#EF4444,stroke-width:2px;
```

### 7.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Thủ Kho)
* **Chứng từ ERPNext:** `Purchase Receipt` (PR), `Stock Entry`, `Quality Inspection` (KCS).
* **Rào chắn 1 (Blind Financial Protection):** Giao diện của Thủ kho bị ẩn hoàn toàn các cột: Đơn giá mua (Rate), Số tiền (Amount), Chi phí phân bổ (Landed Cost) và Lợi nhuận. Thủ kho chỉ tập trung kiểm soát **Số lượng thực đếm (Accepted Qty)** và **Số lượng từ chối (Rejected Qty)**.
* **Rào chắn 2 (Stage Gate Physical Unload):** Thủ kho bị cấm dỡ hàng nếu hệ thống chưa ghi nhận cờ `Customs Cleared`. Điều này bảo vệ doanh nghiệp tuyệt đối khỏi rủi ro bị cơ quan hải quan xử phạt về hành vi tiêu thụ hàng hóa đang chịu sự giám sát hải quan.

---

# 🟢 PHẦN II: QUY TRÌNH TÁC NGHIỆP PHÂN VAI LUỒNG XUẤT KHẨU (OUTBOUND SALES & GLOBAL TRADE)
*(Standard Operating Procedures for International Sales, Export Logistics & LC Settlement)*

---

## 8. TỔNG QUAN DÒNG CHẢY BÀN GIAO GIỮA 6 VỊ TRÍ XUẤT KHẨU (OUTBOUND HIGH-LEVEL HANDSHAKE)

Sơ đồ mô tả dòng bàn giao liên vị trí mức cao giữa 6 bộ phận tác nghiệp trong luồng Xuất khẩu. Dòng màu xanh lục thể hiện tiến trình thuận chiều chuẩn; các đường nét đứt màu đỏ thể hiện các phản hồi trả ngược về khi phát sinh sự cố cần điều chỉnh:

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#10B981',
    'lineColor': '#10B981',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart LR
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef role fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    R1["<b>1. SALES QUỐC TẾ</b><br>Hợp đồng & Đơn SO"]:::role
    R2["<b>2. GIÁM ĐỐC / CFO</b><br>Duyệt SO & Tín dụng"]:::role
    R3["<b>3. KẾ TOÁN</b><br>Check cọc & Mở L/C"]:::role
    R4["<b>4. THỦ KHO</b><br>Đóng cont & Xuất DN"]:::role
    R5["<b>5. LOGISTICS</b><br>SI/VGM & B/L gốc"]:::role
    R6["<b>6. HẢI QUAN</b><br>Khai VNACCS & C/O"]:::role

    R1 ==>|"Trình SO"| R2
    R2 ==>|"Lệnh bán"| R3
    R3 ==>|"Xác nhận cọc/LC"| R4
    R4 ==>|"Cont đã seal & Phiếu DN"| R5
    R5 ==>|"SI/VGM & Hạ bãi"| R6
    R6 ==>|"Thông quan & C/O gốc"| R5
    R5 ==>|"Gửi Full set B/L"| R3
    R3 ==>|"Xuất trình đòi tiền L/C"| R2

    %% Các đường trả ngược về khi có biến cố
    R2 -. "[Bác bỏ đơn SO]" .-> R1
    R3 -. "[Khách chưa cọc / L/C lỗi]" .-> R1
    R4 -. "[Vỏ cont thủng/ướt từ chối]" .-> R5
    R5 -. "[Trễ giờ Cut-off SI/VGM]" .-> R1
    R6 -. "[Bị Hải quan luồng Đỏ]" .-> R5

    linkStyle default stroke:#10B981,stroke-width:2px;
```

---

## 9. VỊ TRÍ CHUYÊN VIÊN BÁN HÀNG QUỐC TẾ (INTERNATIONAL SALES SPECIALIST)

### 9.1. Sơ đồ Luồng Tác nghiệp của Sales Xuất Khẩu

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#10B981',
    'lineColor': '#10B981',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    S_IN(["<b>ĐẦU VÀO:</b> Yêu cầu báo giá (Inquiry / RFQ) từ khách hàng quốc tế"]):::input --> S1
    S1["<b>Bước 1: Chào Giá Ngoại Thương & Đàm Phán Incoterms</b><br>Chốt giá ngoại tệ USD, điều kiện Incoterms (FOB/CIF/CFR), lịch tàu dự kiến"] --> S2
    S2["<b>Bước 2: Rà Soát Điều Khoản Thanh Toán Quốc Tế</b><br>Thẩm định dự thảo L/C Draft hoặc thỏa thuận T/T (Cọc 30% - Thanh toán 70% khi có copy B/L)"] --> S3
    
    S3{"<b>Bước 3: L/C Draft Có Điều Khoản Bẫy (Discrepancy)?</b><br>Có quy định ngày giao hàng hoặc chứng từ bất khả thi?"}:::decision
    S3 -- "[CÓ ĐIỀU KHOẢN BẤT HỢP LÝ]" --> S_AMEND["<b>Bước 3.1: Đòi Khách Tu Chỉnh L/C (L/C Amendment)</b><br>Yêu cầu sửa ngày Latest Shipment Date hoặc bỏ chứng từ vô lý"]:::error --> S2
    S3 -- "[L/C CHUẨN XÁC / CỌC ĐỦ]" --> S4

    S4["<b>Bước 4: Khởi Tạo Đơn Bán Hàng (Sales Order) & Hồ Sơ Mẹ</b><br>Tạo mã <b>SO</b> và mở hồ sơ mẹ <b>Trade Case (EXP-2026-xxxxx)</b>"] --> S5
    S5{"<b>Bước 5: Trình Ký Giám Đốc / CFO Phê Duyệt</b><br>Đơn SO có được duyệt hạn mức tín dụng?"}:::decision
    
    S5 -- "[BÁC BỎ: Giá thấp / Rủi ro nợ]" --> S_REVISE["<b>Bước 5.1: Đàm phán lại giá & bảo lãnh</b><br>Yêu cầu khách nâng cọc hoặc mở L/C xác nhận (Confirmed L/C)"]:::error --> S1
    S5 -- "[PHÊ DUYỆT]" --> S6["<b>Bước 6: Ký Hợp Đồng Ngoại Thương Chính Thức</b><br>Kích hoạt phân quyền cho Kế toán theo dõi cọc và Kho chuẩn bị hàng"] --> S7

    S7["<b>Bước 7: Theo Dõi Tàu Chạy & Khóa Bất Biến Đơn SO</b><br>Khi tàu rời cảng bốc có B/L gốc: Hệ thống tự động khóa trạng thái SO"] --> S_OUT
    S_OUT(["<b>ĐẦU RA:</b> Hợp đồng chuẩn, SO đã duyệt, L/C khả dụng, kích hoạt xuất hàng"]):::success

    linkStyle default stroke:#10B981,stroke-width:2px;
```

### 9.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Sales Xuất Khẩu)
* **Chứng từ ERPNext:** `Quotation`, `Sales Order` (SO), `Trade Case` (`EXP-.YYYY.-.#####`).
* **Rào chắn 1 (Credit Limit & Payment Term Lock):** Hệ thống khóa cứng không cho phép kích hoạt lệnh xuất hàng nếu khách hàng chưa chuyển đủ 30% tiền cọc hoặc chưa có xác nhận L/C khả dụng từ Ngân hàng.
* **Rào chắn 2 (Immutable SO at Departure):** Ngay khi Chuyến tàu đạt mốc `M04_ETD` (Tàu rời cảng bốc) và đã phát hành Vận đơn gốc B/L, hệ thống tự động khóa đơn bán SO sang trạng thái Read-only, ngăn chặn nhân viên tự ý sửa giá bán hoặc điều khoản Incoterm để trục lợi chênh lệch.

---

## 10. VỊ TRÍ BAN GIÁM ĐỐC / GIÁM ĐỐC TÀI CHÍNH (CFO) - QUẢN TRỊ XUẤT KHẨU

### 10.1. Sơ đồ Luồng Tác nghiệp của CFO

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#F59E0B',
    'lineColor': '#F59E0B',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    C_IN(["<b>ĐẦU VÀO:</b> Đơn SO xuất khẩu trình ký / Hồ sơ bảo lãnh L/C / Tháp chỉ huy"]):::input --> C1
    C1{"<b>Bước 1: Thẩm Định Đối Tác & Biên Lợi Nhuận</b><br>Biên lợi nhuận gộp có đạt chuẩn (>= 15%) & Uy tín ngân hàng phát hành L/C?"}:::decision
    
    C1 -- "[RỦI RO / LÃI THẤP]" --> C_REJ["<b>Bác bỏ đơn hàng:</b> Yêu cầu Sales đàm phán nâng giá bán hoặc đổi ngân hàng bảo lãnh"]:::error
    C1 -- "[ĐẠT CHUẨN]" --> C2["<b>Bước 2: Phê Duyệt Đơn Bán Hàng (Sales Order)</b><br>Ký duyệt điện tử kích hoạt lệnh sản xuất và đóng gói xuất khẩu"] --> C3
    
    C3["<b>Bước 3: Phê Duyệt Mở Lãnh Nhận L/C & Phương Án Chiết Khấu</b><br>Chấp thuận hạn mức chiết khấu bộ chứng từ tại Ngân hàng TMCP (Vietcombank/BIDV)"] --> C4
    
    C4["<b>Bước 4: Giám Sát Tháp Chỉ Huy Xuất Khẩu (Control Tower)</b><br>Giám sát tiến độ đóng cont, đếm ngược hạn Cut-off SI/VGM, cảnh báo rớt tàu"] --> C5
    
    C5{"<b>Bước 5: Thẩm Định Quyết Toán & Đóng Hồ Sơ Lô Xuất (Closed)</b><br>Đã thu đủ 100% tiền hàng ngoại tệ & không có tranh chấp?"}:::decision
    
    C5 -- "[CHƯA THU ĐỦ / PHÁT SINH LỖI LC]" --> C_HOLD["<b>Tạm giữ cờ mở:</b> Đôn đốc Kế toán & Ngân hàng xử lý điện thoại đòi tiền"]:::error
    C5 -- "[TIỀN NGOẠI TỆ ĐÃ VỀ TÀI KHOẢN]" --> C6["<b>Bước 6: Ký Duyệt Đóng Lô Hàng Xuất Khẩu</b><br>Chốt Doanh thu thực tế, Chi phí xuất khẩu (TK 641) và Lãi ròng vào BCTC"] --> C_OUT

    C_OUT(["<b>ĐẦU RA:</b> Lô hàng xuất hoàn tất (cost_status = Closed), ngoại tệ về nước trọn vẹn"]):::success

    linkStyle default stroke:#F59E0B,stroke-width:2px;
```

### 10.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (CFO Xuất Khẩu)
* **Quyền hạn tối cao:** Duyệt hạn mức tín dụng khách hàng nước ngoài, ký duyệt chiết khấu bộ chứng từ L/C, phê duyệt đóng lô hàng xuất khẩu.
* **Rào chắn 1 (Two-Man Verification for Export Release):** Thủ kho không thể xuất hàng nếu thiếu chữ ký số xác nhận của CFO trên đơn `Sales Order`.
* **Rào chắn 2 (FX Risk Protection):** Hệ thống cảnh báo rủi ro biến động tỷ giá USD/VND vượt quá biên độ dự phòng +/- 2%, kích hoạt khuyến nghị mua Hợp đồng kỳ hạn ngoại tệ (Forward FX Contract) để bảo toàn lợi nhuận.

---

## 11. VỊ TRÍ THỦ KHO XUẤT HÀNG & ĐÓNG CONTAINER (EXPORT WAREHOUSE KEEPER)

### 11.1. Sơ đồ Luồng Tác nghiệp của Thủ Kho Xuất Hàng (Stuffing & Vanning)

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#EF4444',
    'lineColor': '#EF4444',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    W_IN(["<b>ĐẦU VÀO:</b> Lệnh xuất kho đóng cont (Pick List từ Sales Order) + Xe chở vỏ cont rỗng"]):::input --> W1
    W1{"<b>Bước 1: Quy Trình Kiểm Tra Vỏ Container 7 Điểm (7-Point Inspection)</b><br>Sàn khô ráo? Trần không lọt sáng? Vách không thủng? Cửa đóng kín khít?"}:::decision
    
    W1 -- "[CONT LỖI: Thủng / Ẩm / Mùi lạ]" --> W_REJ["<b>TỪ CHỐI NHẬN VỎ CONT:</b><br>Lập biên bản từ chối, yêu cầu nhà xe đổi vỏ cont đạt chuẩn khác"]:::error --> W1
    W1 -- "[VỎ CONT ĐẠT CHUẨN 100%]" --> W2["<b>Bước 2: Lấy Hàng Thành Phẩm Xuất Khẩu Theo Pick List</b><br>Soạn hàng đủ số lượng, kiểm tra quy cách đóng gói pallet và nhãn mã (Shipping Marks)"] --> W3

    W3["<b>Bước 3: Đóng Hàng Vào Container (Stuffing / Vanning)</b><br>Phân bổ đều tải trọng cont, chèn lót túi khí (Dunnage air bag), chằng buộc đai (Lashing), đặt gói hút ẩm"] --> W4
    
    W4["<b>Bước 4: Đóng Cửa Cont & Bấm Chì Niêm Phong (Bolt Seal)</b><br>Bấm seal đạt chuẩn ISO 17712. Chụp ảnh rõ nét: Số container và Số chì seal"] --> W5
    
    W5["<b>Bước 5: Lập Phiếu Xuất Kho (Delivery Note - DN)</b><br>Ghi nhận chính xác số lượng thực xuất, ghi giảm tồn kho thành phẩm (TK 156 / TK 632)"] --> W6

    W6["<b>Bước 6: Bàn Giao Cont Cho Lái Xe & Gửi Dữ Liệu Cho Logistics</b><br>Ký biên bản bàn giao phiếu xuất, gửi ảnh seal và số cân tạm tính cho Logistics làm VGM"] --> W_OUT

    W_OUT(["<b>ĐẦU RA:</b> Cont xuất kho đã bấm seal niêm phong, phiếu DN hợp lệ, xe rời kho ra cảng"]):::success

    linkStyle default stroke:#EF4444,stroke-width:2px;
```

### 11.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Thủ Kho Xuất)
* **Chứng từ ERPNext:** `Pick List`, `Delivery Note` (DN), `Stock Entry`.
* **Rào chắn 1 (7-Point Inspection Compulsory Photo):** Bắt buộc thủ kho phải chụp ảnh 4 góc cont rỗng (đặc biệt là ảnh trần cont từ bên trong đóng kín cửa xem có lỗ lọt sáng hay không) đính kèm vào hệ thống trước khi cho phép lập phiếu `Delivery Note`. Điều này loại bỏ hoàn toàn rủi ro hàng xuất khẩu bị nước mưa ngấm hỏng khi đi biển dài ngày.
* **Rào chắn 2 (Seal Number Integrity Lock):** Số chì niêm phong (Seal No) bắt buộc phải được quét mã barcode hoặc nhập chính xác và khóa bất biến trên phiếu DN. Mọi sai lệch số seal giữa DN và Vận đơn B/L sẽ bị hệ thống báo động đỏ ngay lập tức.

---

## 12. VỊ TRÍ ĐIỀU PHỐI LOGISTICS XUẤT KHẨU (OUTBOUND COORDINATOR)

### 12.1. Sơ đồ Luồng Tác nghiệp của Logistics Xuất Khẩu

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#A855F7',
    'lineColor': '#A855F7',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    L_IN(["<b>ĐẦU VÀO:</b> Sales Order đã duyệt / Thông báo hàng sẵn sàng xuất (Cargo Ready Date)"]):::input --> L1
    L1["<b>Bước 1: Khởi Tạo Chuyến Tàu Con Trade Shipment (Outbound)</b><br>Mở mã <b>TS-2026-xxxxx</b> liên kết với Trade Case mẹ. Ghi nhận cảng xuất, cảng đích, Incoterms"] --> L2
    
    L2["<b>Bước 2: Tìm Cước & Đặt Chỗ Hãng Tàu (Booking Confirmation)</b><br>Lấy Booking hãng tàu (Maersk, ONE, Cosco...). Ghi nhận 3 mốc Cut-off tử huyệt vào hệ thống"] --> L3
    
    L3["<b>Bước 3: Lấy Lệnh Cấp Vỏ Cont & Điều Xe Đến Kho Đóng Hàng</b><br>Phát hành Empty Release Order, điều xe kéo vỏ cont từ bãi depot về kho nhà máy"] --> L4
    
    L4["<b>Bước 4: Cân Xe Lấy Phiếu Cân Khối Lượng VGM Điện Tử</b><br>Xe chở cont ra trạm cân đạt chuẩn SOLAS ➔ Lấy Phiếu xác nhận khối lượng toàn bộ <b>VGM</b>"] --> L5
    
    L5{"<b>Bước 5: Kiểm Tra Đếm Ngược 3 Giờ Cut-Off Tử Huyệt</b><br>Đã gửi SI & VGM trước giờ đóng sổ hãng tàu?"}:::decision
    
    L5 -- "[CÒN <= 6H CHƯA NỘP]" --> L_WARN["<b>BÁO ĐỘNG ĐỎ CUT-OFF:</b><br>Khẩn cấp truyền SI và VGM qua cổng portal hãng tàu tránh nguy cơ rớt cont (Rolled)"]:::error --> L6
    L5 -- "[ĐÃ TRUYỀN HỢP LỆ]" --> L6["<b>Bước 6: Giám Sát Hạ Bãi Cảng Xuất (Gate-In)</b><br>Theo dõi cont hạ bãi an toàn trước Closing time"] --> L7
    
    L7{"<b>Bước 7: Cổng Stage Gate Hải Quan Xuất:</b><br>Tờ khai hải quan đã có cờ Cleared (M07) để vào sổ tàu?"}:::decision
    
    L7 -- "[CHƯA THÔNG QUAN]" --> L_STOP["<b>HÃNG TÀU TỪ CHỐI XẾP LÊN TÀU:</b><br>Khẩn cấp phối hợp Chuyên viên Hải quan giải quyết thông quan"]:::error --> L7
    L7 -- "[ĐÃ THÔNG QUAN]" --> L8["<b>Bước 8: Cẩu Cont Lên Tàu & Lấy Vận Đơn B/L Gốc</b><br>Tàu khởi hành (M04_ETD) ➔ Hãng tàu phát hành Full set 3/3 Original Clean On Board B/L"] --> L_OUT

    L_OUT(["<b>ĐẦU RA:</b> Hàng đã xếp lên tàu, cầm chắc bộ Vận đơn B/L gốc hợp lệ bàn giao Kế toán"]):::success

    linkStyle default stroke:#A855F7,stroke-width:2px;
```

### 12.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Logistics Xuất)
* **Chứng từ ERPNext:** `Trade Shipment`, `Trade Shipment Container`, `Booking Confirmation`, `VGM Certificate`.
* **Công thức nghiệp vụ bắt buộc:**
  $$\text{VGM} = \text{Tare Weight (Khối lượng vỏ cont rỗng)} + \text{Cargo Net Weight (Khối lượng hàng hóa thực tế)} + \text{Dunnage (Vật liệu chèn lót)}$$
* **Rào chắn 1 (3-Tier Cut-off Auto-Countdown):** Hệ thống thiết lập đồng hồ đếm ngược tự động cho 3 mốc:
  1. *SI Cut-off Deadline:* Hạn chót gửi chi tiết làm B/L.
  2. *VGM Cut-off Deadline:* Hạn chót nộp phiếu cân điện tử SOLAS.
  3. *CY / Gate-in Cut-off Deadline:* Hạn chót xe cont vào bãi cảng xuất.
  Khi `hiện tại >= Cut-off - 6 giờ` mà chưa có xác nhận nộp thành công, hệ thống tự động bắn cảnh báo khẩn cấp đến điện thoại Trưởng phòng Logistics.
* **Rào chắn 2 (Rolled Container Exception Handling):** Nếu cont bị rớt tàu do lỗi hãng tàu hoặc trễ thủ tục, hệ thống tự động sinh phiếu bất thường `Exception Ticket`, tách cont sang chuyến tàu kế tiếp (`TS-2026-xxxxx-B`) mà không làm gián đoạn hồ sơ mẹ `Trade Case`.

---

## 13. VỊ TRÍ CHUYÊN VIÊN HẢI QUAN & C/O XUẤT KHẨU (EXPORT CUSTOMS & COMPLIANCE)

### 13.1. Sơ đồ Luồng Tác nghiệp của Hải Quan Xuất Khẩu

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#EC4899',
    'lineColor': '#EC4899',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    H_IN(["<b>ĐẦU VÀO:</b> Hợp đồng ngoại thương, Hóa đơn thương mại (CI), Packing List (PL), Giấy phép xuất khẩu"]):::input --> H1
    H1["<b>Bước 1: Rà Soát Mã HS & Biểu Thuế Xuất Khẩu</b><br>Xác định mã HS hàng xuất, kiểm tra thuế XK (thường 0%), tra cứu chính sách mặt hàng"] --> H2
    
    H2["<b>Bước 2: Truyền Tờ Khai Hải Quan Điện Tử VNACCS (Loại hình B11)</b><br>Khai báo tờ khai chuẩn 12 ký tự (CV 5922/TCHQ-VNACCS) trên phần mềm VNACCS/ECUS"] --> H3
    
    H3{"<b>Bước 3: Kết Quả Phân Luồng Hải Quan?</b><br>Hệ thống tự động trả về luồng nào?"}:::decision
    
    H3 -- "[LUỒNG XANH]" --> H_GREEN["<b>Bước 3.1: Luồng Xanh (Green)</b><br>Thông quan tự động ngay trên hệ thống"]
    H3 -- "[LUỒNG VÀNG]" --> H_YELLOW["<b>Bước 3.2: Luồng Vàng (Yellow)</b><br>In bộ hồ sơ giấy mang đến Chi cục Hải quan cảng xuất đối chiếu"]
    H3 -- "[LUỒNG ĐỎ]" --> H_RED["<b>Bước 3.3: Luồng Đỏ (Red - Kiểm Hóa)</b><br>Đưa cont vào bãi kiểm hóa mở cont kiểm tra thực tế hàng"]:::error
    
    H_YELLOW --> H_CLEAR{"Hải quan phê duyệt hồ sơ?"}:::decision
    H_CLEAR -- "[CHẤP THUẬN]" --> H_GREEN
    H_CLEAR -- "[NGHI VẤN]" --> H_EXP["Giải trình xuất xứ & định mức"]:::error --> H_GREEN

    H_RED --> H_INSP{"Kiểm hóa thực tế trùng khớp?"}:::decision
    H_INSP -- "[TRÙNG KHỚP 100%]" --> H_GREEN
    H_INSP -- "[SAI LỆCH HÀNG]" --> H_FINE["Xử phạt vi phạm & Khai sửa đổi bổ sung"]:::error --> H_GREEN

    H_GREEN --> H4["<b>Bước 4: Thanh Lý Hải Quan Giám Sát Cảng (Vào Sổ Tàu)</b><br>Đăng ký danh sách container đủ điều kiện qua khu vực giám sát để cẩu lên tàu (M07)"] --> H5
    
    H5["<b>Bước 5: Lập Hồ Sơ & Nộp Xin Cấp Chứng Nhận Xuất Xứ (C/O)</b><br>Kê khai bảng tiêu chí xuất xứ (RVC / CTC) nộp VCCI hoặc Bộ Công Thương xin cấp C/O ưu đãi"] --> H_OUT

    H_OUT(["<b>ĐẦU RA:</b> Tờ khai xuất thông quan hoàn tất, cầm C/O gốc ưu đãi bàn giao Kế toán"]):::success

    linkStyle default stroke:#EC4899,stroke-width:2px;
```

### 13.2. Bảng Đặc tả Nghiệp vụ & Rào chắn Poka-Yoke (Hải Quan Xuất)
* **Chứng từ ERPNext:** `Customs Declaration` (Mã loại hình B11), `Certificate of Origin` (C/O Form B, EUR.1, CPTPP, RCEP, AK...).
* **Rào chắn 1 (Customs Gate-in Clearance Barrier):** Hệ thống không cho phép xác nhận mốc hoàn tất xếp hàng lên tàu (`M04_ETD`) nếu Tờ khai xuất khẩu liên kết chưa đạt trạng thái `clearance_status = "Cleared"`.
* **Rào chắn 2 (Rule of Origin Criterion Validation):** Hệ thống tự động kiểm tra tỷ lệ hàm lượng giá trị khu vực (RVC >= 40%) dựa trên giá trị nguyên liệu nội địa và chi phí nhân công trước khi ký nộp hồ sơ xin cấp C/O ưu đãi, tránh bị cơ quan thẩm quyền bác hồ sơ hoặc bị hải quan nước nhập khẩu truy thu thuế.

---

## 14. VỊ TRÍ KẾ TOÁN THANH TOÁN QUỐC TẾ & DOANH THU (EXPORT ACCOUNTANT)

### 14.1. Sơ đồ Luồng Tác nghiệp của Kế Toán Xuất Khẩu

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Segoe UI, Arial, sans-serif',
    'fontSize': '13px',
    'primaryColor': '#1E293B',
    'primaryTextColor': '#F8FAFC',
    'primaryBorderColor': '#10B981',
    'lineColor': '#10B981',
    'edgeLabelBackground': '#0F172A'
  }
}}%%
flowchart TD
    classDef default fill:#1E293B,stroke:#64748B,stroke-width:1.5px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef decision fill:#451A03,stroke:#F59E0B,stroke-width:2px,color:#FEF08A,font-family:Segoe UI,Arial,sans-serif;
    classDef input fill:#0F2942,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-family:Segoe UI,Arial,sans-serif;
    classDef error fill:#450A0A,stroke:#EF4444,stroke-width:2px,color:#FEE2E2,font-family:Segoe UI,Arial,sans-serif;
    classDef success fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#ECFDF5,font-family:Segoe UI,Arial,sans-serif;

    A_IN(["<b>ĐẦU VÀO:</b> Phiếu xuất kho DN / Full set B/L gốc / C/O gốc / Hợp đồng L/C"]):::input --> A1
    A1["<b>Bước 1: Thu Thập & Hoàn Thiện Trọn Bộ Chứng Từ Giao Hàng</b><br>Tập hợp 100% chứng từ: Commercial Invoice, Packing List, Full set 3/3 Original B/L, C/O, Bảo hiểm"] --> A2
    
    A2["<b>Bước 2: Lập Hóa Đơn Xuất Khẩu (Sales Invoice - SI)</b><br>Hệ thống tự động cấn trừ 30% tiền cọc ➔ Ghi nhận Doanh thu xuất khẩu (TK 511, Thuế suất 0%)"] --> A3
    
    A3{"<b>Bước 3: Kiểm Tra Bộ Chứng Từ So Khớp Điều Khoản L/C</b><br>Có bất kỳ lỗi chính tả, sai ngày tháng hay khác biệt từ ngữ (Discrepancy)?"}:::decision
    
    A3 -- "[CÓ LỖI CHỨNG TỪ]" --> A_FIX["<b>Bước 3.1: Đính Chính Lại Chứng Từ Trong 24 Giờ</b><br>Yêu cầu Logistics sửa B/L hoặc Hải quan cấp lại C/O đúng chuẩn từng ký tự L/C"]:::error --> A2
    A3 -- "[100% CLEAN DOCUMENTS]" --> A4["<b>Bước 4: Xuất Trình Bộ Chứng Từ Cho Ngân Hàng Thương Mại</b><br>Nộp hồ sơ thanh toán L/C tại Vietcombank/BIDV để đòi tiền Ngân hàng phát hành"] --> A5

    A5["<b>Bước 5: Tiếp Nhận Ngoại Tệ Về Nước (Điện Báo Swift MT103)</b><br>Ngân hàng nước ngoài thanh toán ➔ Hạch toán Nợ TK 1122 (USD) / Có TK 131, xử lý lệch tỷ giá TK 515"] --> A6
    
    A6["<b>Bước 6: Tập Hợp & Quyết Toán Toàn Bộ Chi Phí Xuất Khẩu</b><br>Hóa đơn cước biển, THC cảng, nâng hạ, kiểm định, phí cấp C/O ➔ Hạch toán Chi phí bán hàng (TK 641)"] --> A7
    
    A7["<b>Bước 7: Lập Hồ Sơ Hoàn Thuế GTGT Đầu Vào Hàng Xuất Khẩu</b><br>Căn cứ Tờ khai thông quan, Hóa đơn SI và Chứng từ thanh toán ngân hàng ➔ Hoàn thuế VAT (TK 133)"] --> A8

    A8["<b>Bước 8: Đóng Sổ Quyết Toán Đơn Hàng Xuất Khẩu (Closed)</b><br>Chốt Biên lợi nhuận gộp thực tế (Gross Margin) và khóa bất biến sổ cái lô hàng"] --> A_OUT

    A_OUT(["<b>ĐẦU RA:</b> Thu đủ 100% ngoại tệ về nước, công nợ sạch, biên lợi nhuận chốt hoàn hảo"]):::success

    linkStyle default stroke:#10B981,stroke-width:2px;
```

### 14.2. Bảng Hạch Toán Kế Toán Chuẩn Mực & Rào Chắn Poka-Yoke (Kế Toán Xuất)
* **Bảng tài khoản chuẩn mực (Thông tư 200/2014/TT-BTC & VAS):**
  * *Nhận cọc ngoại tệ:* Nợ TK 1122 (VCB USD) / Có TK 131 (Phải thu khách hàng).
  * *Ghi nhận giá vốn xuất kho (khi duyệt DN):* Nợ TK 632 (Giá vốn hàng bán) / Có TK 156 (Thành phẩm/Hàng hóa).
  * *Ghi nhận doanh thu xuất khẩu (khi duyệt SI):* Nợ TK 131 / Có TK 511 (Doanh thu bán hàng, Thuế GTGT 0%).
  * *Thu ngoại tệ còn lại:* Nợ TK 1122 (USD) / Có TK 131; Lãi tỷ giá hạch toán Có TK 515; Lỗ tỷ giá hạch toán Nợ TK 635.
  * *Tập hợp chi phí xuất khẩu (Cước, THC, C/O):* Nợ TK 641 (Chi phí bán hàng) / Có TK 331 (Forwarder/Cảng).
  * *Hoàn thuế VAT đầu vào:* Nợ TK 1121 / Có TK 1331.
* **Rào chắn 1 (Zero Discrepancy L/C Verification):** Trước khi xuất trình cho ngân hàng, hệ thống bắt buộc chạy bộ kiểm tra chéo (Cross-check Automation): Tên người thụ hưởng, số tiền, mô tả hàng hóa, cảng đi/đến trên B/L, Invoice và C/O phải khớp 100% từng chữ so với điều khoản L/C, loại trừ hoàn toàn nguy cơ bị ngân hàng quốc tế từ chối thanh toán.
* **Rào chắn 2 (Bank-Verified Revenue Recognition):** Doanh thu xuất khẩu chỉ được phép ghi nhận chính thức khi đã có xác nhận giao hàng qua biên bản tàu chạy và bộ chứng từ vận tải hợp lệ, ngăn ngừa tuyệt đối hành vi ghi nhận doanh thu khống trước kỳ kế toán.

