# 🏛️ BẢN THIẾT KẾ KIẾN TRÚC HỆ THỐNG QUẢN TRỊ XUẤT NHẬP KHẨU (GLOBAL TRADE ERP)
*(Enterprise Architecture Blueprint — Clean, Modular & Governance-Driven)*

---

## 💎 TRIẾT LÝ THIẾT KẾ KIẾN TRÚC (ARCHITECTURAL PRINCIPLES)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  1. CLEAN CORE       : Giữ nguyên lõi ERPNext v15, toàn bộ module nằm trong Custom App │
│  2. SINGLE HUB       : Trade Shipment là trục chỉ huy duy nhất (Single Source of Truth)│
│  3. STAGE GATE       : Kiểm soát điều kiện tiên quyết (Readiness) trước khi chuyển mốc │
│  4. VAS 02 / IAS 2   : Phân bổ giá vốn đa tiêu chí chuẩn mực, tách bạch chi phí phạt   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 BẢN VẼ 1: KIẾN TRÚC PHÂN TẦNG TỔNG THỂ (LAYERED ENTERPRISE ARCHITECTURE)

*Mô hình 5 tầng chuẩn TOGAF, phân tách rõ ràng từ người dùng đến hạ tầng lưu trữ:*

```mermaid
flowchart TD
    %% TẦNG 1: NGƯỜI DÙNG
    subgraph L1["👥 TẦNG 1: NGƯỜI DÙNG & VAI TRÒ NGHIỆP VỤ (BUSINESS ACTORS)"]
        direction LR
        U_BUY["🛒 Thu Mua<br><i>Buyer</i>"]
        U_LOG["🚢 Logistics<br><i>Điều phối</i>"]
        U_CUS["🏛️ Hải Quan<br><i>Tuân thủ</i>"]
        U_WH["📦 Thủ Kho<br><i>Giao nhận</i>"]
        U_ACC["💰 Kế Toán<br><i>Giá vốn</i>"]
        U_CFO["👑 Giám Đốc<br><i>Phê duyệt</i>"]
    end

    %% TẦNG 2: GIAO DIỆN
    subgraph L2["🖥️ TẦNG 2: GIAO DIỆN & TRẠM ĐIỀU HÀNH (CONTROL TOWER & WORKSPACES)"]
        direction LR
        DASH["📊 <b>Global Trade Control Tower</b><br>• Cảnh báo rủi ro bến bãi cont • Báo cáo trễ tàu • Biểu đồ chi phí"]
        WORK["📋 <b>Chuyên Biệt Hóa Giao Diện (Role-based Views)</b><br>• Workspace Mua hàng • Workspace Logistics • Workspace Kế toán"]
    end

    %% TẦNG 3: TRUNG TÂM QUẢN TRỊ
    subgraph L3["⚙️ TẦNG 3: TRUNG TÂM QUẢN TRỊ XNK (CUSTOM APP: LOGISTICS WIZARD)"]
        direction TB
        
        subgraph HUB["🚢 TRỤC CHỈ HUY TRUNG TÂM (CORE HUB)"]
            TS["<b>Trade Shipment (Hồ Sơ Lô Hàng)</b><br>Mã Lô • Nhà cung cấp • Incoterms • Cảng đi/đến • Vận đơn B/L • Ngân sách"]
        end

        subgraph SATELLITES["📦 CÁC THỰC THỂ QUẢN TRỊ VỆ TINH"]
            direction LR
            SAT_M["⏱️ <b>9 Mốc Tiến Độ</b><br>(Milestones)"]
            SAT_C["📦 <b>Quản Trị Container</b><br>(Free-time Dem/Det)"]
            SAT_F["💵 <b>Chi Phí & Ngân Sách</b><br>(Cost Items)"]
            SAT_A["🧮 <b>Phân Bổ Mặt Hàng</b><br>(Item Allocation)"]
        end

        subgraph COMPLIANCE["🏛️ PHÂN HỆ HẢI QUAN & PHÁP LÝ"]
            direction LR
            CUS_DEC["📄 Tờ Khai Hải Quan<br><i>Luồng Xanh/Vàng/Đỏ</i>"]
            CUS_PER["📜 Giấy Phép Chuyên Ngành<br><i>Hợp chuẩn / Hợp quy</i>"]
            CUS_DOC["📑 Checklist Chứng Từ<br><i>Đủ/thiếu C/O, B/L, Inv</i>"]
        end

        HUB --> SATELLITES
        HUB <--> COMPLIANCE
    end

    %% TẦNG 4: THUẬT TOÁN
    subgraph L4["🧠 TẦNG 4: BỘ NÃO THUẬT TOÁN & BẢO VỆ CHÍNH SÁCH (ENGINES)"]
        direction LR
        ENG_ALLOC["🧮 <b>Động Cơ Phân Bổ Giá Vốn</b><br>Cước tàu chia theo CBM<br>Bảo hiểm/Thuế chia theo Giá trị"]
        ENG_VAR["📐 <b>Bóc Tách Chênh Lệch</b><br>Biến động Giá cước hãng tàu<br>Biến động Tỷ giá ngoại tệ USD"]
        ENG_GATE["🛡️ <b>Cổng Chặn Quản Trị</b><br>Khóa đóng lô khi vượt > 10%<br>Chặn nhập kho khi chưa thông quan"]
        ENG_RAG["🤖 <b>AI / RAG Service</b><br>Tra cứu căn cứ pháp lý<br>Gợi ý phân loại mã HS"]
    end

    %% TẦNG 5: LÕI ERPNEXT & HẠ TẦNG
    subgraph L5["🏢 TẦNG 5: LÕI KẾ TOÁN/KHO ERPNEXT & HẠ TẦNG DOCKER"]
        direction LR
        ERP_CORE["💼 <b>ERPNext Core Documents</b><br>Purchase Order • Purchase Receipt • Landed Cost Voucher • General Ledger"]
        INFRA["🐳 <b>Hạ Tầng Công Nghệ</b><br>Docker Compose • Frappe Framework v15 • MariaDB • Redis Cache"]
    end

    %% LIÊN KẾT ĐA TẦNG GỌN GÀNG
    L1 ==> L2
    L2 ==> L3
    L3 <==> L4
    L4 ==> L5

    %% PHONG CÁCH MÀU SẮC SANG TRỌNG
    style L1 fill:#F8FAFC,stroke:#64748B,stroke-width:2px
    style L2 fill:#F0F9FF,stroke:#0284C7,stroke-width:2px
    style L3 fill:#FAF5FF,stroke:#9333EA,stroke-width:2px
    style L4 fill:#FFFBEB,stroke:#D97706,stroke-width:2px
    style L5 fill:#ECFDF5,stroke:#059669,stroke-width:2px

    style TS fill:#7E22CE,stroke:#581C87,color:#FFFFFF,stroke-width:2px
    style ENG_ALLOC fill:#FEF3C7,stroke:#B45309,color:#78350F
    style ENG_VAR fill:#FEF3C7,stroke:#B45309,color:#78350F
    style ENG_GATE fill:#FEE2E2,stroke:#B91C1C,color:#7F1D1D
    style ENG_RAG fill:#E0E7FF,stroke:#4338CA,color:#312E81
```

---

## 🎯 BẢN VẼ 2: KIẾN TRÚC TRỤC CHỈ HUY TRUNG TÂM (HUB-AND-SPOKE ARCHITECTURE)

*Mô hình vệ tinh đối xứng: `Trade Shipment` đóng vai trò trái tim kết nối 4 nhóm vệ tinh xung quanh:*

```mermaid
flowchart LR
    %% TRÁI TIM HỆ THỐNG
    CORE(("🚢 <b>TRADE SHIPMENT</b><br>──────────<br><b>TRỤC CHỈ HUY</b><br><i>Hồ Sơ Lô Hàng</i>"))

    %% NHÓM 1: TIẾN ĐỘ & HÀNH TRÌNH
    subgraph G_TRACK["⏱️ 1. TIẾN ĐỘ & CONTAINER"]
        direction TB
        M9["<b>9 Mốc Kiểm Soát Chuẩn</b><br>M01 PO ➔ M04 Tàu chạy ➔ M07 Hải quan ➔ M09 Về kho"]
        CONT["<b>Quản Trị Container & Free-time</b><br>Hạn chót lưu bãi cảng • Hạn chót trả vỏ cont rỗng"]
    end

    %% NHÓM 2: PHÁP LÝ & HẢI QUAN
    subgraph G_COMP["🏛️ 2. PHÁP LÝ & HẢI QUAN"]
        direction TB
        DEC["<b>Tờ Khai Hải Quan VNACCS</b><br>Số tờ khai 11 số • Luồng Xanh / Vàng / Đỏ"]
        DOCS["<b>Bộ Chứng Từ Sẵn Sàng (Readiness)</b><br>B/L gốc • Invoice • Packing List • C/O ưu đãi"]
        PERM["<b>Kiểm Tra Chuyên Ngành</b><br>Giấy phép QCVN Bộ TT&TT, Y tế, Công thương"]
    end

    %% NHÓM 3: TÀI CHÍNH & GIÁ VỐN
    subgraph G_COST["💰 3. CHI PHÍ & GIÁ VỐN (VAS 02)"]
        direction TB
        COST["<b>Đối Soát Dự Toán vs Thực Tế</b><br>Bóc tách: Lệch Giá cước tàu vs Lệch Tỷ giá USD"]
        ALLOC["<b>Phân Bổ Chi Phí Đa Tiêu Chí</b><br>Cước tàu theo CBM • Thuế & Bảo hiểm theo Trị giá"]
        LCV["<b>Landed Cost Voucher</b><br>Ghi tăng chính xác giá vốn tồn kho TK 156"]
    end

    %% NHÓM 4: DANH MỤC NỀN TẢNG
    subgraph G_MASTER["📦 4. MASTER DATA DÙNG CHUNG"]
        direction TB
        CHG["<b>Charge Type (Loại Phí)</b><br>Khóa ranh giới: Cấm đưa phạt lưu cont vào giá vốn"]
        HS["<b>HS Tariff Rate (Biểu Thuế)</b><br>Thuế MFN • Thuế FTA 0% kèm form C/O bắt buộc"]
        FX["<b>Customs Exchange Rate</b><br>Tỷ giá hải quan chính thức theo tuần"]
    end

    %% KẾT NỐI ĐỐI XỨNG CÂN BẰNG
    G_MASTER ==> CORE
    CORE <==> G_TRACK
    CORE <==> G_COMP
    CORE <==> G_COST

    %% PHONG CÁCH
    style CORE fill:#4F46E5,stroke:#312E81,color:#FFFFFF,stroke-width:3px
    style G_TRACK fill:#F0FDF4,stroke:#16A34A,stroke-width:2px
    style G_COMP fill:#EFF6FF,stroke:#2563EB,stroke-width:2px
    style G_COST fill:#FEFCE8,stroke:#CA8A04,stroke-width:2px
    style G_MASTER fill:#FDF4FF,stroke:#C026D3,stroke-width:2px
```

---

## 🌊 BẢN VẼ 3: QUY TRÌNH DÒNG CHẢY NGHIỆP VỤ 4 CHẶNG (LIFECYCLE PIPELINE)

*Quy trình thực chiến từ lúc đặt hàng đến khi đóng sổ quyết toán:*

```mermaid
flowchart LR
    %% CHẶNG 1
    subgraph ST1["GIAI ĐOẠN 1: ĐẶT HÀNG"]
        direction TB
        S1_A["🛒 Lập Đơn Mua Hàng PO"]
        S1_B["🏛️ Duyệt Mã HS & Biểu Thuế"]
        S1_C["🚢 Khởi Tạo Hồ Sơ Lô Hàng"]
        S1_A --> S1_B --> S1_C
    end

    %% CHẶNG 2
    subgraph ST2["GIAI ĐOẠN 2: HÀNG TRÊN BIỂN"]
        direction TB
        S2_A["📦 Cập nhật Cont, Chì, Free-time"]
        S2_B["🚢 Theo dõi M04 ETD ➔ M05 ETA"]
        S2_C["📑 Kiểm tra Đủ Bộ Chứng Từ"]
        S2_A --> S2_B --> S2_C
    end

    %% CHẶNG 3
    subgraph ST3["GIAI ĐOẠN 3: THÔNG QUAN & KHO"]
        direction TB
        S3_A["🏛️ Mở Tờ Khai & Nộp Thuế"]
        S3_B["✅ Thông Quan Hải Quan M07"]
        S3_C["📦 Nhập Kho Vật Lý M09 (PR)"]
        S3_A --> S3_B --> S3_C
    end

    %% CHẶNG 4
    subgraph ST4["GIAI ĐOẠN 4: GIÁ VỐN & ĐÓNG LÔ"]
        direction TB
        S4_A["💵 Nhập Hóa Đơn Chi Phí Thật"]
        S4_B["🧮 Chạy Phân Bổ Landed Cost"]
        S4_C["🔒 Đóng Quyết Toán Lô Hàng"]
        S4_A --> S4_B --> S4_C
    end

    %% DÒNG CHẢY XUYÊN SUỐT
    ST1 ==> ST2 ==> ST3 ==> ST4

    %% PHONG CÁCH
    style ST1 fill:#F8FAFC,stroke:#64748B,stroke-width:2px
    style ST2 fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px
    style ST3 fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px
    style ST4 fill:#ECFDF5,stroke:#10B981,stroke-width:2px
```

---

## 🚦 BẢN VẼ 4: CƠ CHẾ CỔNG KIỂM SOÁT ĐIỀU KIỆN (STAGE GATE GOVERNANCE)

*Cơ chế tự động hóa bảo vệ doanh nghiệp: Chưa đủ điều kiện thì hệ thống lập tức khóa chặn:*

```mermaid
flowchart TD
    %% GATE 1
    START(["Tàu chuẩn bị rời cảng xuất"]) --> G1{"🚪 CỔNG 1: XUẤT CẢNG SẴN SÀNG?<br><i>Đủ VGM, SI, Tờ khai xuất chưa?</i>"}
    G1 -- "❌ THIẾU" --> STOP1["🚫 <b>CHẶN LẠI (NOT READY)</b><br>Cảnh báo nguy cơ rớt tàu • Báo cho Logistics xử lý gấp"]
    G1 -- "✅ ĐỦ" --> PASS1["🟢 Cho phép chuyển trạng thái: <b>In Transit (Hàng đang đi)</b>"]

    %% GATE 2
    PASS1 --> G2{"🚪 CỔNG 2: THÔNG QUAN SẴN SÀNG?<br><i>Đã có C/O gốc? Đã nộp thuế vào Kho bạc?</i>"}
    G2 -- "❌ THIẾU" --> STOP2["🚫 <b>CHẶN LẠI (NOT READY)</b><br>Không được kéo hàng ra cảng • Cảnh báo phạt lưu bãi cont"]
    G2 -- "✅ ĐỦ" --> PASS2["🟢 Cho phép kéo hàng về kho công ty dỡ hàng"]

    %% GATE 3
    PASS2 --> G3{"🚪 CỔNG 3: QUYẾT TOÁN HỢP LỆ?<br><i>Chi phí thực tế có vượt ngân sách > 10%?</i>"}
    G3 -- "❌ VƯỢT > 10%" --> STOP3["🔒 <b>KHÓA QUYẾT TOÁN LÔ HÀNG</b><br>Nhân viên bị khóa nút • Bắt buộc Giám đốc / CFO ký duyệt ngoại lệ"]
    G3 -- "✅ TRONG ĐỊNH MỨC" --> PASS3["🎉 <b>CHO PHÉP ĐÓNG LÔ (CLOSED)</b><br>Ghi nhận chính thức giá vốn vào Báo cáo tài chính"]

    %% PHONG CÁCH
    style G1 fill:#FEF9C3,stroke:#CA8A04,stroke-width:2px
    style G2 fill:#FEF9C3,stroke:#CA8A04,stroke-width:2px
    style G3 fill:#FEF9C3,stroke:#CA8A04,stroke-width:2px
    style STOP1 fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style STOP2 fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style STOP3 fill:#FEE2E2,stroke:#DC2626,stroke-width:2px,color:#991B1B
    style PASS1 fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#166534
    style PASS2 fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#166534
    style PASS3 fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#166534
```

---

## 👥 BẢN VẼ 5: MA TRẬN PHÂN QUYỀN TRÁCH NHIỆM RACI (GOVERNANCE MATRIX)

| Chứng Từ / Khâu Nghiệp Vụ | 🛒 Thu Mua (`buyer`) | 🏛️ Tuân Thủ (`customs`) | 🚢 Logistics (`logistics`) | 📦 Thủ Kho (`warehouse`) | 💰 Kế Toán (`accountant`) | 👑 Giám Đốc (`cfo`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Đơn mua hàng (PO)** | 🟢 **R** *(Lập)* | ⚪ C *(Tham vấn)* | 🔵 I *(Xem)* | 🔵 I *(Xem)* | ⚪ C *(Kiểm tra ngân sách)* | 🟡 **A** *(Duyệt)* |
| **Duyệt Mã HS & Biểu Thuế** | 🔵 I *(Đề xuất)* | 🟢 **R** *(Duyệt)* | 🔵 I *(Xem)* | ─ | 🔵 I *(Xem thuế)* | 🟡 **A** |
| **Hành trình Tàu & Cont (M01-M05)** | 🔵 I *(Theo dõi)* | 🔵 I *(Theo dõi)* | 🟢 **R** *(Điều phối)* | ─ | ─ | 🟡 **A** |
| **Tờ khai Hải quan (M06-M07)** | ─ | 🟢 **R** *(Khai báo)* | ⚪ C *(Phối hợp)* | ─ | ⚪ C *(Nộp thuế)* | 🟡 **A** |
| **Phiếu Nhập kho (PR) (M09)** | ─ | ─ | 🔵 I *(Giao cont)* | 🟢 **R** *(Đếm hàng)* | 🔵 I *(Số lượng)* | 🟡 **A** |
| **Phân bổ Giá vốn (Landed Cost)** | ─ | ─ | ─ | ─ | 🟢 **R** *(Chạy LCV)* | 🟡 **A** |
| **Duyệt đóng lô VƯỢT NGÂN SÁCH** | ─ | ─ | ─ | ─ | 🔵 I *(Trình duyệt)* | 🔴 **R / A *(Ký duyệt)*** |

*Ký hiệu: **R** (Responsible - Thực hiện) • **A** (Accountable - Quyết định tối cao) • **C** (Consulted - Tham vấn) • **I** (Informed - Nhận thông báo).*
