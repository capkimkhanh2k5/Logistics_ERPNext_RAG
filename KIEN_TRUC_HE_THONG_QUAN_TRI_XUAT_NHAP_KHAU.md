# 🏛️ BẢN THIẾT KẾ TOÀN DIỆN KIẾN TRÚC HỆ THỐNG QUẢN TRỊ XUẤT NHẬP KHẨU
*(Comprehensive Enterprise Global Trade & Supply Chain Architecture on ERPNext v15)*

---

## 💎 CHƯƠNG 1: TRIẾT LÝ VÀ NGUYÊN TẮC KIẾN TRÚC DOANH NGHIỆP

Hệ thống được thiết kế theo tiêu chuẩn khung kiến trúc mở **TOGAF Framework**, tích hợp mô hình **Song Trục Đối Xứng (Dual-Stream Shared-Core)** nhằm quản trị trọn vẹn cả hai luồng nghiệp vụ **Nhập khẩu (Inbound)** và **Xuất khẩu (Outbound)** trên cùng một nền tảng lõi ERPNext v15:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. CLEAN ARCHITECTURE  : 100% mã nguồn nằm trong app `logistics_wizard`, giữ lõi sạch. │
│ 2. DUAL-STREAM CORE    : Trục lõi dùng chung (Shared Core) cho cả Nhập khẩu & Xuất khẩu.│
│ 3. TWO-TIER HUB        : Tách Trade Case (Hợp đồng/PO/SO) vs Trade Shipment (Vận tải). │
│ 4. PARTIAL SHIPMENT    : Hỗ trợ 1 Case nhiều chuyến hàng giao từng phần lệch lịch tàu. │
│ 5. 3-TIER STAGE GATES  : Hệ cổng Poka-Yoke 2 chiều chặn rủi ro pháp lý, kho & tài chính.│
│ 6. VAS 02 / IAS 2      : Thuật toán phân bổ đa tiêu chí chuẩn xác, bóc tách rạch ròi. │
│ 7. MANAGEMENT BY EXC.  : Quản trị theo ngoại lệ, hệ thống tự động cảnh báo sớm rủi ro. │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 CHƯƠNG 2: BẢN VẼ KIẾN TRÚC HỆ THỐNG 4 PHÂN TẦNG (MICROSOFT ENTERPRISE ARCHITECTURE)

Bản vẽ kiến trúc hệ thống được thiết kế theo mô hình **4 Phân Tầng Doanh Nghiệp (Enterprise 4-Tier Architecture)** chuẩn Microsoft Teams (tham chiếu tài liệu kiến trúc kỹ thuật `KTHT_MSTeams`): phân định rạch ròi giữa giao diện người dùng, lớp dịch vụ ngoại thương chuyên biệt & AI, lớp chứng từ lõi ERPNext và nền tảng hạ tầng container:

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '12px', 'lineColor': '#64748B'}}}%%
flowchart TD
    %% ==========================================
    %% TẦNG 1: GIAO DIỆN & ĐIỀU HÀNH (PRESENTATION & CLIENTS)
    %% ==========================================
    subgraph T1["TẦNG 1: GIAO DIỆN NGƯỜI DÙNG & ĐIỀU HÀNH (CLIENTS & PRESENTATION)"]
        direction LR
        ROLES["👥 <b>ĐỘI NGŨ TÁC NGHIỆP ĐA PHÒNG BAN</b><br>🛒 Mua Hàng • 🌍 Bán Hàng QT • 🚢 Logistics • 🏛️ Hải Quan<br>📦 Thủ Kho • 💰 Kế Toán • 👑 Ban Giám Đốc / CFO"]
        DASH["📊 <b>THÁP CHỈ HUY TRUNG TÂM (CONTROL TOWER)</b><br>Định vị GPS & Hành trình tàu biển 3D • Cảnh báo phạt bãi cont<br>Báo cáo trễ hạn tàu • Cảnh báo rủi ro biến động tỷ giá USD/VND"]
        ROLES <==> DASH
    end

    %% ==========================================
    %% TẦNG 2: DỊCH VỤ NGOẠI THƯƠNG & TRÍ TUỆ NHÂN TẠO
    %% ==========================================
    subgraph T2["TẦNG 2: DỊCH VỤ NGOẠI THƯƠNG & TRÍ TUỆ NHÂN TẠO (GLOBAL TRADE SERVICES & AI)"]
        direction LR
        TC["📂 <b>Trade Case Management</b><br>Hồ sơ mẹ (Import / Export)<br>Quản lý Hợp đồng & Ngân sách"]
        TS["🚢 <b>Shipment Tracking Hub</b><br>Quản lý Chuyến tàu & 9 Mốc tiến độ<br>Hạn Free-time & Phạt Demurrage"]
        AIRAG["🤖 <b>AI/RAG HS & Legal Engine</b><br>Tư vấn mã HS theo thông số kỹ thuật<br>Tra cứu biểu thuế & căn cứ pháp lý"]
        LOGIC["🧮 <b>Động Cơ Thuật Toán Lõi</b><br>Phân bổ Landed Cost (VAS 02 / IAS 2)<br>Bóc tách lệch giá • Cổng Stage Gates"]
        
        TC ==>|"1 Case nhiều đợt giao"| TS
        TS <==> AIRAG
        TS <==> LOGIC
    end

    %% ==========================================
    %% TẦNG 3: CHỨNG TỪ & QUY TRÌNH LÕI ERPNEXT
    %% ==========================================
    subgraph T3["TẦNG 3: CHỨNG TỪ & QUY TRÌNH LÕI ERPNEXT (ERPNEXT CORE WORKFLOWS)"]
        direction TB
        subgraph LUONG_NHAP["🔵 LUỒNG NHẬP KHẨU (INBOUND PROCUREMENT)"]
            direction LR
            PO["1. Đơn Mua (PO)"] --> PR["2. Nhập Kho (PR)<br><i>Gate 2: Thông quan</i>"] --> PI["3. Hóa Đơn Mua (PI)<br><i>Cấn trừ 30% cọc</i>"] --> LCV["4. Phân Bổ Giá Vốn (LCV)<br><i>Chuẩn VAS 02</i>"]
        end
        subgraph LUONG_XUAT["🟢 LUỒNG XUẤT KHẨU (OUTBOUND SALES)"]
            direction LR
            SO["1. Đơn Bán (SO)"] --> DN["2. Xuất Kho Đóng Cont (DN)<br><i>Gate 1: SI/VGM Cut-off</i>"] --> SI["3. Hóa Đơn Xuất Khẩu (SI)"] --> PAY["4. Thu Ngoại Tệ (L/C, TT)"]
        end
    end

    %% ==========================================
    %% TẦNG 4: HẠ TẦNG KỸ THUẬT & DỮ LIỆU
    %% ==========================================
    subgraph T4["TẦNG 4: NỀN TẢNG HẠ TẦNG KỸ THUẬT & DỮ LIỆU (INFRASTRUCTURE & PLATFORM LAYER)"]
        direction LR
        INFRA_APP["💻 <b>Frappe App Cluster</b><br>Python 3.11 / Desk (:2828)"]
        INFRA_DB["🗄️ <b>MariaDB 11.8</b><br>Giao dịch ACID • InnoDB Engine"]
        INFRA_REDIS["⚡ <b>Redis Cache & Queue</b><br>Celery Worker • Job tính ngầm"]
        INFRA_SOCK["🔄 <b>WebSocket / Socket.io</b><br>Cập nhật tọa độ 3D & Chuông báo"]
    end

    %% ==========================================
    %% LIÊN KẾT ĐA TẦNG DỌC CHUẨN MSTEAMS
    %% ==========================================
    T1 ==>|"Thao tác nghiệp vụ & Ra quyết định"| T2
    T2 <===>|"Đồng bộ tiến độ & Kiểm soát Stage Gate"| T3
    T3 ==>|"Lưu trữ dữ liệu & Thực thi container ngầm"| T4

    %% ==========================================
    %% PHỐI MÀU CHUẨN MSTEAMS (LIGHT ENTERPRISE CLEAN)
    %% ==========================================
    style T1 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style T2 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style T3 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style T4 fill:#F1F5F9,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A

    style LUONG_NHAP fill:#FFFFFF,stroke:#3B82F6,stroke-width:1.5px,color:#1E3A8A
    style LUONG_XUAT fill:#FFFFFF,stroke:#10B981,stroke-width:1.5px,color:#064E3B

    style ROLES fill:#FFFFFF,stroke:#94A3B8,stroke-width:1px,color:#0F172A
    style DASH fill:#EFF6FF,stroke:#2563EB,stroke-width:1.5px,color:#1E40AF

    style TC fill:#EFF6FF,stroke:#2563EB,stroke-width:2px,color:#1E40AF
    style TS fill:#FFFFFF,stroke:#64748B,stroke-width:1.5px,color:#0F172A
    style AIRAG fill:#EFF6FF,stroke:#2563EB,stroke-width:1px,color:#1E40AF
    style LOGIC fill:#FFFFFF,stroke:#64748B,stroke-width:1px,color:#0F172A

    style PO fill:#EFF6FF,stroke:#3B82F6,stroke-width:1px,color:#1E3A8A
    style PR fill:#EFF6FF,stroke:#3B82F6,stroke-width:1px,color:#1E3A8A
    style PI fill:#EFF6FF,stroke:#3B82F6,stroke-width:1px,color:#1E3A8A
    style LCV fill:#FEF3C7,stroke:#D97706,stroke-width:1px,color:#78350F

    style SO fill:#F0FDF4,stroke:#10B981,stroke-width:1px,color:#064E3B
    style DN fill:#F0FDF4,stroke:#10B981,stroke-width:1px,color:#064E3B
    style SI fill:#F0FDF4,stroke:#10B981,stroke-width:1px,color:#064E3B
    style PAY fill:#FEF3C7,stroke:#D97706,stroke-width:1px,color:#78350F

    style INFRA_APP fill:#FFFFFF,stroke:#94A3B8,stroke-width:1px,color:#0F172A
    style INFRA_DB fill:#FFFFFF,stroke:#94A3B8,stroke-width:1px,color:#0F172A
    style INFRA_REDIS fill:#FFFFFF,stroke:#94A3B8,stroke-width:1px,color:#0F172A
    style INFRA_SOCK fill:#FFFFFF,stroke:#94A3B8,stroke-width:1px,color:#0F172A
```

---

## 🔄 CHƯƠNG 3: LUỒNG NGHIỆP VỤ 5 GIAI ĐOẠN VÒNG ĐỜI LÔ HÀNG (GLOBAL TRADE LIFECYCLE WORKFLOW)

Toàn bộ hoạt động xuất nhập khẩu được quản trị khép kín qua **5 Giai Đoạn Vòng Đời Chuẩn (End-to-End Lifecycle Stages)**, bảo đảm tính liên tục của dòng hàng vật lý và tính chính xác của dòng tài chính kế toán:

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '12px', 'lineColor': '#64748B'}}}%%
flowchart TD
    %% ==========================================
    %% GIAI ĐOẠN 1: CHUẨN BỊ ĐƠN HÀNG & THƯƠNG MẠI
    %% ==========================================
    subgraph STAGE1["GIAI ĐOẠN 1: CHUẨN BỊ ĐƠN HÀNG & HỒ SƠ NGOẠI THƯƠNG (TRADE PREPARATION)"]
        direction LR
        S1_PO["📝 <b>Đơn Hàng & Hợp Đồng</b><br>Tạo Purchase Order (PO) / Sales Order (SO)<br>Chốt đơn giá ngoại tệ, Incoterms (CIF/FOB)"]
        S1_RAG["🤖 <b>AI/RAG Tư Vấn Mã HS</b><br>Tra cứu thông số kỹ thuật sản phẩm<br>Đề xuất mã HS & Biểu thuế ưu đãi FTA"]
        S1_CASE["📂 <b>Khởi Tạo Trade Case</b><br>Mở Hồ sơ mẹ liên kết chứng từ<br>Lập Ngân sách dự toán chi phí lô hàng"]
        S1_PO --> S1_RAG --> S1_CASE
    end

    %% ==========================================
    %% GIAI ĐOẠN 2: LOGISTICS & VẬN TẢI BIỂN
    %% ==========================================
    subgraph STAGE2["GIAI ĐOẠN 2: LOGISTICS, VẬN TẢI QUỐC TẾ & CONTAINER (SHIPMENT TRACKING)"]
        direction LR
        S2_BOOK["🚢 <b>Booking & Vận Đơn B/L</b><br>Mở Trade Shipment, số vận đơn B/L<br>Cập nhật số Container & Số chì Seal"]
        S2_MILE["⏱️ <b>Giám Sát 9 Mốc Hành Trình</b><br>Theo dõi M01 ➔ M04 Tàu chạy (Lock PO)<br>Dự báo ngày tàu cập cảng (M05_ETA)"]
        S2_WARN["🚨 <b>Cảnh Báo Hạn Phạt Bãi</b><br>Đếm ngược Free-time lưu bãi cảng<br>Báo động đỏ trước 3 ngày chạm hạn phạt"]
        S2_BOOK --> S2_MILE --> S2_WARN
    end

    %% ==========================================
    %% GIAI ĐOẠN 3: THỦ TỤC HẢI QUAN
    %% ==========================================
    subgraph STAGE3["GIAI ĐOẠN 3: THỦ TỤC HẢI QUAN & PHÁP LÝ (CUSTOMS CLEARANCE)"]
        direction LR
        S3_DOC["📋 <b>Checklist Chứng Từ (Gate 1)</b><br>Rà soát Hợp đồng, Invoice, P/L, C/O<br>Đảm bảo đủ 100% điều kiện khai báo"]
        S3_VNACCS["🏛️ <b>Tờ Khai VNACCS 11 Số</b><br>Truyền tờ khai điện tử hải quan<br>Khớp tỷ giá tuần của Bộ Tài chính"]
        S3_TAX["💰 <b>Nộp Thuế & Thông Quan</b><br>Kế toán nộp thuế XNK & VAT vào kho bạc<br>Hoàn tất mốc M07_CUSTOMS_CLEAR"]
        S3_DOC --> S3_VNACCS --> S3_TAX
    end

    %% ==========================================
    %% GIAI ĐOẠN 4: KHO BÃI VẬT LÝ
    %% ==========================================
    subgraph STAGE4["GIAI ĐOẠN 4: GIAO NHẬN KHO VẬT LÝ & KIỂM ĐẾM (PHYSICAL RECEIVING)"]
        direction LR
        S4_GATE["🚪 <b>Cổng Kiểm Soát Poka-Yoke (Gate 2)</b><br>Kiểm tra cờ Thông quan (M07)<br>Khóa dỡ hàng nếu chưa thông quan"]
        S4_COUNT["📦 <b>Kiểm Đếm Thực Tế & KCS</b><br>Cắt chì seal, kiểm tra dập vỡ/ẩm mốc<br>Tách hàng hỏng (Rejected Qty) sang TK 1388"]
        S4_PR["📑 <b>Phiếu Nhập Kho (Purchase Receipt)</b><br>Chỉ nhập hàng đạt chuẩn vào Kho (TK 156)<br>Tự động chốt mốc M09_WH_RECEIPT"]
        S4_GATE --> S4_COUNT --> S4_PR
    end

    %% ==========================================
    %% GIAI ĐOẠN 5: QUYẾT TOÁN GIÁ VỐN
    %% ==========================================
    subgraph STAGE5["GIAI ĐOẠN 5: QUYẾT TOÁN CHI PHÍ & GIÁ VỐN ĐÍCH THỰC (LANDED COST VAS 02)"]
        direction LR
        S5_COLLECT["🧾 <b>Tập Hợp Hóa Đơn Chi Phí</b><br>Cước biển, phí D/O, nâng hạ, kiểm định<br>Cấn trừ 30% tiền cọc tạm ứng"]
        S5_LCV["🧮 <b>Động Cơ Phân Bổ Landed Cost</b><br>Cước biển phân bổ theo Thể tích (CBM)<br>Thuế & Phí khác phân bổ theo Trị giá"]
        S5_CLOSE["🔒 <b>Thẩm Định Ngân Sách & Đóng Lô (Gate 3)</b><br>Bóc tách lệch giá cước vs lệch tỷ giá<br>Chốt giá vốn bất biến (cost_status = Closed)"]
        S5_COLLECT --> S5_LCV --> S5_CLOSE
    end

    %% ==========================================
    %% DÒNG CHẢY XUYÊN SUỐT 5 GIAI ĐOẠN
    %% ==========================================
    STAGE1 ==>|"Khởi tạo chuyến tàu & bàn giao vận tải"| STAGE2
    STAGE2 ==>|"Tàu cập cảng & cung cấp B/L, chứng từ"| STAGE3
    STAGE3 ==>|"Thông quan hoàn tất (Đèn xanh cho kho)"| STAGE4
    STAGE4 ==>|"Hàng vào kho an toàn & hóa đơn dịch vụ đủ"| STAGE5

    %% ==========================================
    %% PHỐI MÀU CHUẨN MSTEAMS (LIGHT ENTERPRISE CLEAN)
    %% ==========================================
    style STAGE1 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style STAGE2 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style STAGE3 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style STAGE4 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A
    style STAGE5 fill:#F8FAFC,stroke:#CBD5E1,stroke-width:1.5px,color:#0F172A

    style S1_PO fill:#FFFFFF,stroke:#3B82F6,stroke-width:1px,color:#1E3A8A
    style S1_RAG fill:#EFF6FF,stroke:#2563EB,stroke-width:1px,color:#1E40AF
    style S1_CASE fill:#EFF6FF,stroke:#2563EB,stroke-width:1.5px,color:#1E40AF

    style S2_BOOK fill:#FFFFFF,stroke:#64748B,stroke-width:1px,color:#0F172A
    style S2_MILE fill:#FFFFFF,stroke:#64748B,stroke-width:1px,color:#0F172A
    style S2_WARN fill:#FEF2F2,stroke:#DC2626,stroke-width:1px,color:#991B1B

    style S3_DOC fill:#FFFFFF,stroke:#64748B,stroke-width:1px,color:#0F172A
    style S3_VNACCS fill:#FFFFFF,stroke:#3B82F6,stroke-width:1px,color:#1E3A8A
    style S3_TAX fill:#F0FDF4,stroke:#16A34A,stroke-width:1px,color:#166534

    style S4_GATE fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#991B1B
    style S4_COUNT fill:#FFFFFF,stroke:#64748B,stroke-width:1px,color:#0F172A
    style S4_PR fill:#F0FDF4,stroke:#16A34A,stroke-width:1.5px,color:#166534

    style S5_COLLECT fill:#FFFFFF,stroke:#64748B,stroke-width:1px,color:#0F172A
    style S5_LCV fill:#EFF6FF,stroke:#2563EB,stroke-width:1.5px,color:#1E40AF
    style S5_CLOSE fill:#FEF3C7,stroke:#D97706,stroke-width:1.5px,color:#78350F
```

### 📋 Bảng Đặc Tả Nghiệp Vụ & Chứng Từ 5 Giai Đoạn Vòng Đời

| Giai Đoạn | Chứng Từ / Dữ Liệu Tác Nghiệp | Vai Trò Chính | Đầu Ra Nghiệp Vụ & Rào Chắn Poka-Yoke |
| :--- | :--- | :---: | :--- |
| **Giai đoạn 1: Chuẩn bị Đơn hàng** | `Purchase Order` (PO), `Sales Order` (SO), `Trade Case`, Tra cứu HS Code (AI RAG) | 🛒 Thu Mua / 🌍 Sales | Khởi tạo hồ sơ mẹ `IMP-xxxx`, chốt dự toán ngân sách; Đơn PO/SO được Giám đốc ký duyệt. |
| **Giai đoạn 2: Logistics & Tàu biển** | `Trade Shipment`, Master/House B/L, Container, Booking Confirmation | 🚢 Logistics | Cập nhật số Cont/Seal; giám sát mốc M01-M05; khóa cứng đơn PO khi tàu rời cảng (M04); đếm ngược Free-time. |
| **Giai đoạn 3: Thủ tục Hải quan** | `Customs Declaration`, C/O Form E/D/AK, Packing List, Tờ khai VNACCS 11 số | 🏛️ Hải Quan / 💰 Kế Toán | Stage Gate 1: đủ 100% chứng từ mới mở tờ khai; nộp thuế kho bạc; chốt mốc thông quan M07_CUSTOMS_CLEAR. |
| **Giai đoạn 4: Kho bãi Vật lý** | `Purchase Receipt` (PR), `Delivery Note` (DN), Biên bản đồng kiểm, KCS | 📦 Thủ Kho | Stage Gate 2: Chặn dỡ hàng và cấm submit PR nếu chưa thông quan; tách hàng hỏng ra TK 1388; chốt mốc M09. |
| **Giai đoạn 5: Quyết toán Giá vốn** | `Purchase Invoice` (PI), Hóa đơn cước forwarder, `Landed Cost Voucher` (LCV) | 💰 Kế Toán / 👑 CFO | Stage Gate 3: Tự cấn trừ 30% cọc; phân bổ chi phí theo CBM & Trị giá (VAS 02); khóa đóng lô nếu vượt dự toán > 10%. |

---

## 🚦 CHƯƠNG 4: HỆ THỐNG CỔNG KIỂM SOÁT ĐIỀU KIỆN (DUAL-STREAM STAGE GATES)

Hệ thống hoạt động theo cơ chế **Quản trị Chủ động (Proactive Control)**: Trước khi chuyển sang bước tiếp theo, hệ thống tự động kiểm tra các điều kiện sẵn sàng đối xứng cho cả 2 luồng Nhập khẩu và Xuất khẩu:

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '12px', 'lineColor': '#64748B'}}}%%
flowchart TD
    subgraph GATES_IN["HỆ CỔNG KIỂM SOÁT NHẬP KHẨU (INBOUND GATES)"]
        direction TB
        IN_START(["1. Tàu Chở Hàng Đến Cảng Đến (POD)"]) --> IN_G1{"CỔNG 1: HỒ SƠ NGOẠI THƯƠNG<br><i>Đủ 100% C/O, Packing List, Invoice?</i>"}
        IN_G1 -- "❌ Chưa đủ" --> IN_STOP1["CHẶN: Không cho mở tờ khai VNACCS"]
        IN_G1 -- "✅ Đủ 100%" --> IN_PASS1["ĐẠT: Chuyển mốc M06 (Khai hải quan)"]
        
        IN_PASS1 --> IN_G2{"CỔNG 2: THÔNG QUAN NHẬP KHO<br><i>Mốc M07 đã Completed chưa?</i>"}
        IN_G2 -- "❌ Chưa thông quan" --> IN_STOP2["<b>CHẶN SUBMIT PHIẾU NHẬP KHO (PR)</b><br>Thủ kho bị khóa quyền duyệt hàng vào kho"]
        IN_G2 -- "✅ Đã thông quan" --> IN_PASS2["ĐẠT: Cho phép duyệt PR & Nhập kho (M09)"]

        IN_PASS2 --> IN_G3{"CỔNG 3: QUYẾT TOÁN GIÁ VỐN<br><i>Chi phí vượt dự toán > 10%?</i>"}
        IN_G3 -- "❌ Vượt > 10%" --> IN_STOP3["Khóa đóng lô, yêu cầu Giám đốc duyệt"]
        IN_G3 -- "✅ Trong định mức" --> IN_PASS3["ĐẠT: Chạy Landed Cost (LCV) & Đóng lô"]
    end

    subgraph GATES_OUT["HỆ CỔNG KIỂM SOÁT XUẤT KHẨU (OUTBOUND GATES)"]
        direction TB
        OUT_START(["1. Đóng Hàng Cont Tại Kho Công Ty"]) --> OUT_G1{"CỔNG 1: HẠN CUT-OFF HÃNG TÀU<br><i>Đã gửi SI & Phiếu cân VGM trước cut-off?</i>"}
        OUT_G1 -- "❌ Trễ hạn" --> OUT_STOP1["BÁO ĐỘNG ĐỎ: Nguy cơ rớt tàu (Rolled cont)"]
        OUT_G1 -- "✅ Đủ SI & VGM" --> OUT_PASS1["ĐẠT: Cấp phép hạ bãi cont cảng xuất (Gate-in)"]

        OUT_PASS1 --> OUT_G2{"CỔNG 2: THÔNG QUAN XUẤT KHẨU<br><i>Tờ khai xuất đã thông quan chưa?</i>"}
        OUT_G2 -- "❌ Chưa thông quan" --> OUT_STOP2["CHẶN: Hãng tàu từ chối cẩu cont lên tàu"]
        OUT_G2 -- "✅ Đã thông quan" --> OUT_PASS2["ĐẠT: Cẩu cont lên tàu & Phát hành B/L gốc (M04)"]

        OUT_PASS2 --> OUT_G3{"CỔNG 3: THANH TOÁN QUỐC TẾ<br><i>Xuất trình B/L, C/O hợp lệ theo L/C?</i>"}
        OUT_G3 -- "❌ Bất hợp lệ (Discrepancy)" --> OUT_STOP3["Khóa: Ngân hàng từ chối thanh toán ngoại tệ"]
        OUT_G3 -- "✅ Khớp 100% L/C" --> OUT_PASS3["ĐẠT: Thu đủ 100% tiền hàng ngoại tệ về nước"]
    end

    style GATES_IN fill:#F8FAFC,stroke:#3B82F6,stroke-width:1.5px,color:#0F172A
    style GATES_OUT fill:#F8FAFC,stroke:#10B981,stroke-width:1.5px,color:#0F172A

    style IN_START fill:#FFFFFF,stroke:#64748B,color:#0F172A
    style IN_G1 fill:#FFFFFF,stroke:#3B82F6,color:#1E3A8A
    style IN_G2 fill:#FFFFFF,stroke:#3B82F6,color:#1E3A8A
    style IN_G3 fill:#FFFFFF,stroke:#3B82F6,color:#1E3A8A
    style IN_STOP1 fill:#FEF2F2,stroke:#DC2626,color:#991B1B
    style IN_STOP2 fill:#FEF2F2,stroke:#DC2626,color:#991B1B
    style IN_STOP3 fill:#FEF3C7,stroke:#D97706,color:#92400E
    style IN_PASS1 fill:#F0FDF4,stroke:#16A34A,color:#166534
    style IN_PASS2 fill:#F0FDF4,stroke:#16A34A,color:#166534
    style IN_PASS3 fill:#F0FDF4,stroke:#16A34A,color:#166534

    style OUT_START fill:#FFFFFF,stroke:#64748B,color:#0F172A
    style OUT_G1 fill:#FFFFFF,stroke:#10B981,color:#064E3B
    style OUT_G2 fill:#FFFFFF,stroke:#10B981,color:#064E3B
    style OUT_G3 fill:#FFFFFF,stroke:#10B981,color:#064E3B
    style OUT_STOP1 fill:#FEF2F2,stroke:#DC2626,color:#991B1B
    style OUT_STOP2 fill:#FEF2F2,stroke:#DC2626,color:#991B1B
    style OUT_STOP3 fill:#FEF3C7,stroke:#D97706,color:#92400E
    style OUT_PASS1 fill:#F0FDF4,stroke:#16A34A,color:#166534
    style OUT_PASS2 fill:#F0FDF4,stroke:#16A34A,color:#166534
    style OUT_PASS3 fill:#F0FDF4,stroke:#16A34A,color:#166534
```

---

## 👥 CHƯƠNG 5: MA TRẬN PHÂN QUYỀN TRÁCH NHIỆM RACI (GOVERNANCE MATRIX)

| Chứng Từ / Khâu Nghiệp Vụ | 🛒 Mua Hàng (`buyer`) | 🌍 Bán Hàng QT (`sales`) | 🏛️ Tuân Thủ (`customs`) | 🚢 Logistics (`logistics`) | 📦 Thủ Kho (`warehouse`) | 💰 Kế Toán (`accountant`) | 👑 Giám Đốc (`cfo`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Đơn mua hàng (PO - Nhập khẩu)** | 🟢 **R** *(Lập)* | ─ | ⚪ C *(Tham vấn)* | 🔵 I *(Xem)* | 🔵 I *(Xem)* | ⚪ C *(Duyệt ngân sách)* | 🟡 **A** *(Duyệt)* |
| **Đơn bán hàng (SO - Xuất khẩu)** | ─ | 🟢 **R** *(Lập)* | ⚪ C *(Kiểm tra FTA)* | ⚪ C *(Check cước)* | 🔵 I *(Xem tồn kho)* | ⚪ C *(Check hạn mức nợ)*| 🟡 **A** *(Duyệt)* |
| **Duyệt Mã HS & Biểu Thuế XNK** | 🔵 I *(Đề xuất)* | 🔵 I *(Đề xuất)* | 🟢 **R** *(Duyệt mã)* | 🔵 I *(Xem)* | ─ | 🔵 I *(Xem thuế)* | 🟡 **A** |
| **Booking, SI/VGM, Vận tải (M01-M05)**| 🔵 I *(Xem)* | 🔵 I *(Xem)* | 🔵 I *(Xem)* | 🟢 **R** *(Điều phối)* | ─ | ─ | 🟡 **A** |
| **Tờ khai VNACCS Xuất & Nhập (M06-M07)**| ─ | ─ | 🟢 **R** *(Khai báo)* | ⚪ C *(Phối hợp)* | ─ | ⚪ C *(Nộp thuế)* | 🟡 **A** |
| **Phiếu Nhập kho (PR) (M09 - Nhập)** | ─ | ─ | ─ | 🔵 I *(Giao cont)* | 🟢 **R** *(Đếm hàng)* | 🔵 I *(Số lượng)* | 🟡 **A** |
| **Phiếu Xuất kho (DN) (Xuất khẩu)** | ─ | 🔵 I *(Lệnh xuất)*| ─ | ⚪ C *(Lấy cont rỗng)*| 🟢 **R** *(Đóng cont)* | 🔵 I *(Giảm kho)* | 🟡 **A** |
| **Phân bổ Giá vốn (Landed Cost - LCV)**| ─ | ─ | ─ | ─ | ─ | 🟢 **R** *(Chạy LCV)* | 🟡 **A** |
| **Duyệt đóng lô VƯỢT NGÂN SÁCH > 10%**| ─ | ─ | ─ | ─ | ─ | 🔵 I *(Trình duyệt)* | 🔴 **R / A *(Ký duyệt)*** |

*Ký hiệu: **R** (Responsible - Trực tiếp làm) • **A** (Accountable - Phê duyệt tối cao, mỗi khâu duy nhất 1 người) • **C** (Consulted - Tham vấn ý kiến) • **I** (Informed - Nhận thông báo tự động).*

---

## 🛡️ CHƯƠNG 6: KIỂM TOÁN ỨNG SUẤT — KHẮC CHẾ 7 TÌNH HUỐNG HIỂM HÓC

Bảo đảm hệ thống không bao giờ bị nghẽn (Deadlock) trước các biến cố phức tạp ngoài đời thực:

| # | Tình huống rủi ro thực tế | Rủi ro nếu thiết kế kém | Cơ chế Kiến trúc khắc chế triệt để | Đánh giá |
| :-: | :--- | :--- | :--- | :---: |
| **1** | **Giao hàng từng phần (Partial Shipment)** | Hệ thống bắt đợi đủ hợp đồng mới tính giá vốn/doanh thu | Tách `Trade Case` (Hồ sơ tổng) vs `Shipment` (xử lý chứng từ, giá vốn riêng từng đợt tàu) | 🟢 An toàn |
| **2** | **Hàng thiếu hụt, rơi vỡ khi mở cont** | Phân bổ khống chi phí vào hàng hỏng | Phiếu PR chỉ ghi nhận hàng thực nhập; phần hỏng hạch toán Phải thu bồi thường bảo hiểm (TK 1388) | 🟢 An toàn |
| **3** | **Hóa đơn cước về trễ sau khi đã xuất bán hết** | Gây lỗi "Tồn kho âm" sập sổ cái kế toán | Cơ chế Additional LCV: Tự động kết chuyển thẳng vào Giá vốn hàng bán trong kỳ (COGS - TK 632) | 🟢 An toàn |
| **4** | **Giải phóng hàng chờ thông quan (nợ C/O)** | Cont bị giữ chết tại cảng, phạt bãi hàng chục triệu | Trạng thái `Released Pending Clearance`: Kéo hàng về kho bảo quản, khóa cờ xuất bán | 🟢 An toàn |
| **5** | **Rớt tàu, trễ hạn Cut-off SI/VGM (Xuất khẩu)** | Hàng bị lưu bãi cảng xuất, lỡ hẹn với khách quốc tế | Cảnh báo đếm ngược trước 24h hạn Cut-off; tự động sinh Exception Ticket chuyển sang chuyến tàu kế | 🟢 An toàn |
| **6** | **Nhiều cont trả vỏ lệch ngày nhau** | Gộp chung, không biết cont nào bị phạt demurrage | Bảng con `containers` quản lý độc lập từng dòng: Số cont, seal, ngày trả vỏ và tiền phạt riêng | 🟢 An toàn |
| **7** | **Lẫn lộn Incoterms (Hàng FOB lẫn CIF)** | Hàng CIF bị tính trùng cước tàu 2 lần | Cấu hình dòng chi phí: Chỉ định phân bổ cước tàu cho hàng FOB, miễn trừ cho hàng CIF | 🟢 An toàn |

---

## 🔒 CHƯƠNG 7: CƠ CHẾ BẢO VỆ TỪNG VAI TRÒ CHỨC NĂNG (POKA-YOKE)

Ngăn ngừa triệt để sai sót và gian lận của yếu tố con người tại từng vị trí:

1. **🛒 Thu mua (`buyer`):**
   * *Rào chắn 1:* Ngay khi tàu chạy (mốc M04), đơn mua PO bị khóa bất biến (Locked), không ai được tự ý đổi giá hoặc số lượng.
   * *Rào chắn 2:* Thu mua chỉ có quyền "Đề xuất mã HS", không được tự duyệt mã HS.
2. **🌍 Bán hàng quốc tế (`sales`):**
   * *Rào chắn 1:* Hệ thống tự động khóa đơn bán SO ngay khi xuất hành B/L gốc, ngăn chặn nhân viên tự ý sửa giá bán hoặc điều khoản Incoterm sau khi hàng đã rời cảng.
   * *Rào chắn 2:* Bắt buộc kiểm tra hạn mức công nợ (Credit Limit) và nhận đủ tiền cọc trước khi kích hoạt lệnh xuất kho đóng cont (DN).
3. **📦 Thủ kho (`warehouse`):**
   * *Rào chắn 1 (Stage Gate 2):* Hệ thống khóa cứng nút Submit Phiếu Nhập Kho (`Purchase Receipt`) nếu lô hàng chưa hoàn tất Thông quan Hải quan (Mốc M07).
   * *Rào chắn 2:* Phân quyền ẩn hoàn toàn đơn giá mua, chi phí và biên lợi nhuận để bảo mật tài chính.
4. **💰 Kế toán (`accountant`):**
   * *Rào chắn 1:* Tự động cấn trừ tiền cọc: Khi mở hóa đơn, hệ thống tự trừ tiền tạm ứng ngoại tệ, kế toán chỉ có thể chi trả phần còn lại.
   * *Rào chắn 2:* Khóa cứng chức năng đóng sổ lô hàng nếu chi phí thực tế vượt dự toán $> 10\%$.
5. **🏛️ Hải quan (`customs`):**
   * *Rào chắn 1:* Khóa ô nhập tỷ giá tính thuế, bắt buộc lấy tự động từ `Customs Exchange Rate` theo tuần của Bộ Tài chính.
   * *Rào chắn 2:* Bắt buộc tờ khai phải chuẩn 11 chữ số theo hệ thống thông quan tự động VNACCS.
6. **🚢 Logistics (`logistics`):**
   * *Rào chắn 1:* Hệ thống tự động đếm ngược hạn Free-time bãi, tự động gửi chuông cảnh báo trước 3 ngày để nhắc kéo vỏ cont.
   * *Rào chắn 2:* Cảnh báo đếm ngược hạn nộp SI/VGM trước giờ Cut-off của hãng tàu, loại bỏ nguy cơ rớt cont.
7. **👑 Giám đốc / CFO (`cfo`):**
   * *Rào chắn 1:* Cơ chế ủy quyền phê duyệt điện tử (Delegation) khi đi công tác xa; hỗ trợ duyệt trên Mobile App.
   * *Rào chắn 2:* Tính năng `Track Changes` ghi nhật ký vĩnh viễn không thể xóa sửa, phục vụ hậu kiểm thuế sau 3 - 5 năm.

---

## 📊 CHƯƠNG 8: BẢO VỆ NGƯỜI QUẢN TRỊ BẰNG THÁP CHỈ HUY & CẢNH BÁO SỚM

Giải phóng lãnh đạo khỏi các cạm bẫy báo cáo truyền thống:

* **1. Triệt tiêu báo cáo "Sự đã rồi":** Bắn cảnh báo đếm ngược trước 3 ngày trước khi cont bị phạt lưu bãi, giúp xử lý rủi ro trước khi mất tiền.
* **2. Báo cáo Quản trị theo Ngoại lệ (MBE):** Lô hàng an toàn được ẩn đi; màn hình của Giám đốc chỉ hiển thị các điểm nóng cần can thiệp (lô trễ hạn, lô vượt ngân sách).
* **3. Lưu vết bất biến (Immutable Audit Trail):** Ngăn chặn nhân viên xào xáo số liệu, lùi ngày kế hoạch để che giấu khuyết điểm KPI.
* **4. Một nguồn chân lý duy nhất (Single Source of Truth):** Xóa bỏ tranh cãi số liệu giữa phòng Mua hàng, Kế toán và Logistics.
* **5. Báo cáo Biên lợi nhuận đích thực (True Landed Gross Margin):** Tính lãi/lỗ dựa trên **Unit Landed Cost** (FOB + Cước + Phí cảng + Thuế + Bảo hiểm), bảo đảm không bao giờ bị rơi vào bẫy "Lãi giả - Lỗ thật".

---

### 🏆 TỔNG KẾT
Bản thiết kế kiến trúc hoàn thiện này biến hệ thống trở thành một **"Cỗ máy quản trị tự động và vững chắc"**:
* Nhân viên tác nghiệp dễ dàng vì có đường ray chuẩn và máy tính tự động hóa.
* Doanh nghiệp được bảo vệ tuyệt đối về mặt pháp lý và chuẩn mực kế toán.
* Người lãnh đạo nắm trọn quyền kiểm soát toàn cục trong lòng bàn tay!
