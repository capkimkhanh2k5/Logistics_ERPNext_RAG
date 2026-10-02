# 🏛️ BẢN THIẾT KẾ KIẾN TRÚC HỆ THỐNG QUẢN TRỊ XUẤT NHẬP KHẨU (GLOBAL TRADE ERP)
*(Enterprise Architecture Blueprint — Chuẩn TOGAF & Phân Tách Trade Case vs Shipment)*

---

## 💎 1. NGUYÊN TẮC THIẾT KẾ CỐT LÕI (CORE ARCHITECTURAL PRINCIPLES)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  1. CLEAN CORE       : Giữ nguyên 100% lõi ERPNext v15; tính năng nằm trong Custom App │
│  2. TWO-TIER HUB     : Phân tách Trade Case (Hồ sơ thương mại) vs Shipment (Vận tải)   │
│  3. PARTIAL SHIPMENT : 1 Trade Case có thể có 1 hoặc nhiều Shipment giao từng phần     │
│  4. STAGE GATE       : Kiểm soát điều kiện tiên quyết (Readiness) trước khi chuyển mốc │
│  5. VAS 02 / IAS 2   : Phân bổ giá vốn đa tiêu chí chuẩn xác, bóc tách rạch ròi chi phí│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 2. BẢN VẼ 1: KIẾN TRÚC PHÂN TẦNG TỔNG THỂ (LAYERED ENTERPRISE ARCHITECTURE)

*(Khắc phục hoàn toàn lỗi đè chữ bằng cách chuẩn hóa tiêu đề đơn dòng, phân khối độc lập, độ tương phản cao)*

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart TD
    %% TẦNG 1: ACTORS
    subgraph TANG_1["TẦNG 1: NGƯỜI DÙNG & VAI TRÒ (ROLES)"]
        direction LR
        U_BUY["🛒 Thu Mua (Buyer)"]
        U_LOG["🚢 Logistics (Điều Phối)"]
        U_CUS["🏛️ Hải Quan (Tuân Thủ)"]
        U_WH["📦 Thủ Kho (Giao Nhận)"]
        U_ACC["💰 Kế Toán (Giá Vốn)"]
        U_CFO["👑 Giám Đốc (Phê Duyệt)"]
    end

    %% TẦNG 2: GIAO DIỆN
    subgraph TANG_2["TẦNG 2: TRẠM ĐIỀU HÀNH & GIAO DIỆN (PRESENTATION)"]
        direction LR
        DASH["📊 THÁP CHỈ HUY CONTROL TOWER<br>Cảnh báo phạt bãi cont • Báo cáo trễ tàu • Biểu đồ chi phí"]
        WORK["📋 WORKSPACE NGHIỆP VỤ CHUYÊN BIỆT<br>Giao diện làm việc riêng cho từng phòng ban (Role-based Views)"]
    end

    %% TẦNG 3: TRADE CASE & SHIPMENT
    subgraph TANG_3["TẦNG 3: TRUNG TÂM QUẢN TRỊ XNK (LOGISTICS WIZARD)"]
        direction TB
        
        TC["📂 <b>TRADE CASE: HỒ SƠ THƯƠNG MẠI NGOẠI THƯƠNG (IMP / EXP)</b><br>Quản lý Hợp đồng • Đơn mua PO / Đơn bán SO • Nhà cung cấp • Incoterms • Tổng ngân sách Case"]
        
        SHP["🚢 <b>TRADE SHIPMENT: CHUYẾN VẬN TẢI VẬT LÝ (1 HOẶC NHIỀU ĐỢT GIAO)</b><br>Hãng tàu • Vận đơn B/L • Cảng đi/đến • 9 Mốc hành trình • Container & Free-time • Chi phí"]

        TC ==>|"1 Case có thể có 1 hoặc nhiều Shipment"| SHP
    end

    %% TẦNG 4: THUẬT TOÁN
    subgraph TANG_4["TẦNG 4: ĐỘNG CƠ THUẬT TOÁN & BẢO VỆ CHÍNH SÁCH"]
        direction LR
        E_ALLOC["🧮 PHÂN BỔ GIÁ VỐN<br>Cước tàu chia CBM<br>Phí khác chia Trị giá"]
        E_VAR["📐 BÓC TÁCH CHÊNH LỆCH<br>Lệch do Giá cước hãng tàu<br>Lệch do Tỷ giá USD/VND"]
        E_GATE["🛡️ KHÓA CHẶN QUẢN TRỊ<br>Chặn đóng lô khi vượt > 10%<br>Chặn kho khi chưa thông quan"]
        E_RAG["🤖 DỊCH VỤ AI / RAG<br>Tra cứu căn cứ pháp lý<br>Gợi ý phân loại mã HS"]
    end

    %% TẦNG 5: ERPNEXT & DB
    subgraph TANG_5["TẦNG 5: LÕI ERPNEXT GỐC & CƠ SỞ DỮ LIỆU"]
        direction LR
        ERP_DOCS["💼 CHỨNG TỪ LÕI ERPNEXT<br>Purchase Order • Purchase Receipt • Landed Cost Voucher • General Ledger"]
        INFRA_DB["🐳 HẠ TẦNG KỸ THUẬT<br>Docker Compose (9 Containers) • Frappe v15 • MariaDB • Redis Cache"]
    end

    %% LIÊN KẾT GIỮA CÁC TẦNG
    TANG_1 ==> TANG_2
    TANG_2 ==> TANG_3
    TANG_3 <==> TANG_4
    TANG_4 ==> TANG_5

    %% MÀU SẮC ĐỘ TƯƠNG PHẢN CAO (NỀN ĐẬM - CHỮ TRẮNG 100%)
    style TANG_1 fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style TANG_2 fill:#0F172A,stroke:#0284C7,stroke-width:2px,color:#FFFFFF
    style TANG_3 fill:#1E1B4B,stroke:#818CF8,stroke-width:2px,color:#FFFFFF
    style TANG_4 fill:#18181B,stroke:#F59E0B,stroke-width:2px,color:#FFFFFF
    style TANG_5 fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#FFFFFF

    style U_BUY fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style U_LOG fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style U_CUS fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style U_WH fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style U_ACC fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style U_CFO fill:#D97706,stroke:#FBBF24,color:#FFFFFF

    style DASH fill:#0369A1,stroke:#38BDF8,color:#FFFFFF
    style WORK fill:#0369A1,stroke:#38BDF8,color:#FFFFFF

    style TC fill:#4338CA,stroke:#C7D2FE,color:#FFFFFF,stroke-width:3px
    style SHP fill:#6D28D9,stroke:#DDD6FE,color:#FFFFFF,stroke-width:2px

    style E_ALLOC fill:#B45309,stroke:#FCD34D,color:#FFFFFF
    style E_VAR fill:#B45309,stroke:#FCD34D,color:#FFFFFF
    style E_GATE fill:#B91C1C,stroke:#FCA5A5,color:#FFFFFF
    style E_RAG fill:#4F46E5,stroke:#C7D2FE,color:#FFFFFF

    style ERP_DOCS fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style INFRA_DB fill:#047857,stroke:#6EE7B7,color:#FFFFFF
```

---

## 🎯 3. BẢN VẼ 2: MÔ HÌNH PHÂN TÁCH `TRADE CASE` VS `TRADE SHIPMENT`

*Minh họa trường hợp thực tế: Một Đơn hàng mua lớn (PO) được chia làm 2 chuyến tàu khác nhau (Partial Shipment):*

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart TD
    %% TẦNG CASE
    subgraph S_CASE["📂 TẦNG HỒ SƠ THƯƠNG MẠI: TRADE CASE (MÃ: IMP-2026-00001)"]
        direction TB
        PO["Đơn Mua Hàng PO: 1,000 iPhone 16 Pro Max ($1,000,000 USD) • Nhà cung cấp: Apple Inc"]
        POL_GOV["Chính Sách & Ngân Sách: Incoterm CIF Cát Lái • Biểu thuế HS 8517.13.00 (Thuế 0%) • Ngân sách tối đa: 25.5 Tỷ VND"]
        PO --- POL_GOV
    end

    %% TẦNG SHIPMENT
    subgraph S_SHP1["🚢 CHUYẾN TÀU 1 (SHIPMENT 1: TS-2026-00001)"]
        direction TB
        SHP1_INFO["<b>Giao Đợt 1: 600 iPhone</b><br>Tàu: Maersk Mc-Kinney Moller<br>Vận đơn B/L: MAEU11223344<br>Container: MSKU1234567 (40ft HC)<br>Hạn Free-time bãi: 7 ngày<br>Trạng thái: <b>Hoàn thành nhập kho</b>"]
    end

    subgraph S_SHP2["🚢 CHUYẾN TÀU 2 (SHIPMENT 2: TS-2026-00002)"]
        direction TB
        SHP2_INFO["<b>Giao Đợt 2: 400 iPhone</b><br>Tàu: MSC Oscar<br>Vận đơn B/L: MSCU99887766<br>Container: MSCU7654321 (40ft HC)<br>Hạn Free-time bãi: 7 ngày<br>Trạng thái: <b>Đang trên biển (In Transit)</b>"]
    end

    S_CASE ==>|"Đợt giao hàng 1"| S_SHP1
    S_CASE ==>|"Đợt giao hàng 2"| S_SHP2

    %% MÀU SẮC PHÂN TÁCH
    style S_CASE fill:#1E1B4B,stroke:#818CF8,stroke-width:3px,color:#FFFFFF
    style S_SHP1 fill:#064E3B,stroke:#34D399,stroke-width:2px,color:#FFFFFF
    style S_SHP2 fill:#0C4A6E,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF

    style PO fill:#3730A3,stroke:#A5B4FC,color:#FFFFFF
    style POL_GOV fill:#3730A3,stroke:#A5B4FC,color:#FFFFFF
    style SHP1_INFO fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style SHP2_INFO fill:#0369A1,stroke:#7DD3FC,color:#FFFFFF
```

---

## 🌊 4. BẢN VẼ 3: QUY TRÌNH DÒNG CHẢY NGHIỆP VỤ 4 GIAI ĐOẠN

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart LR
    %% GIAI ĐOẠN 1
    subgraph G1["GIAI ĐOẠN 1: ĐẶT HÀNG"]
        direction TB
        G1_1["🛒 1. Lập Đơn Mua PO"]
        G1_2["🏛️ 2. Duyệt Mã HS Code"]
        G1_3["📂 3. Mở Trade Case"]
        G1_1 --> G1_2 --> G1_3
    end

    %% GIAI ĐOẠN 2
    subgraph G2["GIAI ĐOẠN 2: TÀU CHẠY"]
        direction TB
        G2_1["📦 4. Cập nhật Số Cont"]
        G2_2["🚢 5. Theo dõi Mốc Tàu"]
        G2_3["📑 6. Kiểm tra Chứng Từ"]
        G2_1 --> G2_2 --> G2_3
    end

    %% GIAI ĐOẠN 3
    subgraph G3["GIAI ĐOẠN 3: THÔNG QUAN"]
        direction TB
        G3_1["🏛️ 7. Mở Tờ Khai HQ"]
        G3_2["✅ 8. Thông Quan M07"]
        G3_3["📦 9. Nhập Kho M09"]
        G3_1 --> G3_2 --> G3_3
    end

    %% GIAI ĐOẠN 4
    subgraph G4["GIAI ĐOẠN 4: GIÁ VỐN"]
        direction TB
        G4_1["💵 10. Nhập Hóa Đơn Thật"]
        G4_2["🧮 11. Phân Bổ Landed Cost"]
        G4_3["🔒 12. Đóng Quyết Toán"]
        G4_1 --> G4_2 --> G4_3
    end

    G1 ==> G2 ==> G3 ==> G4

    style G1 fill:#1E293B,stroke:#64748B,stroke-width:2px,color:#FFFFFF
    style G2 fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style G3 fill:#1E1B4B,stroke:#A78BFA,stroke-width:2px,color:#FFFFFF
    style G4 fill:#064E3B,stroke:#34D399,stroke-width:2px,color:#FFFFFF

    style G1_1 fill:#334155,stroke:#94A3B8,color:#FFFFFF
    style G1_2 fill:#334155,stroke:#94A3B8,color:#FFFFFF
    style G1_3 fill:#334155,stroke:#94A3B8,color:#FFFFFF

    style G2_1 fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style G2_2 fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style G2_3 fill:#0284C7,stroke:#38BDF8,color:#FFFFFF

    style G3_1 fill:#6D28D9,stroke:#C4B5FD,color:#FFFFFF
    style G3_2 fill:#6D28D9,stroke:#C4B5FD,color:#FFFFFF
    style G3_3 fill:#6D28D9,stroke:#C4B5FD,color:#FFFFFF

    style G4_1 fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style G4_2 fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style G4_3 fill:#047857,stroke:#6EE7B7,color:#FFFFFF
```

---

## 🚦 5. BẢN VẼ 4: CƠ CHẾ CỔNG KIỂM SOÁT ĐIỀU KIỆN (STAGE GATE GOVERNANCE)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart TD
    START(["🚢 TÀU CHUẨN BỊ RỜI CẢNG XUẤT"]) --> G1{"🚪 CỔNG 1: XUẤT CẢNG SẴN SÀNG?<br><i>Đã có đủ chứng từ VGM, SI, Tờ khai xuất chưa?</i>"}

    G1 -- "❌ THIẾU CHỨNG TỪ" --> STOP1["🚫 <b>CHẶN LẠI: TRẠNG THÁI NOT READY</b><br>• Cảnh báo đỏ: Nguy cơ rớt tàu (Rolled container)<br>• Tự động tạo Exception Ticket giao Logistics xử lý"]
    G1 -- "✅ ĐỦ 100%" --> PASS1["🟢 <b>ĐẠT: Chuyển mốc M04 Tàu chạy (In Transit)</b>"]

    PASS1 --> G2{"🚪 CỔNG 2: THÔNG QUAN SẴN SÀNG?<br><i>Đã có C/O gốc? Đã nộp thuế vào Kho bạc Nhà nước?</i>"}
    G2 -- "❌ CHƯA ĐỦ ĐIỀU KIỆN" --> STOP2["🚫 <b>CHẶN LẠI: TRẠNG THÁI NOT READY</b><br>• Chưa được phép kéo hàng ra khỏi cảng<br>• Kích hoạt đếm ngược hạn Free-time tránh phạt lưu bãi"]
    G2 -- "✅ ĐÃ THÔNG QUAN" --> PASS2["🟢 <b>ĐẠT: Cho phép kéo container về kho công ty dỡ hàng (M09)</b>"]

    PASS2 --> G3{"🚪 CỔNG 3: QUYẾT TOÁN HỢP LỆ?<br><i>Chi phí thực tế có bị vượt ngân sách dự toán > 10%?</i>"}
    G3 -- "❌ VƯỢT > 10%" --> STOP3["🔒 <b>KHÓA CHỨC NĂNG ĐÓNG LÔ HÀNG</b><br>• Nhân viên thường bị tước quyền đóng quyết toán<br>• Bắt buộc Giám đốc / CFO phê duyệt ngoại lệ mới được đóng"]
    G3 -- "✅ TRONG ĐỊNH MỨC <= 10%" --> PASS3["🎉 <b>HOÀN TẤT ĐÓNG LÔ HÀNG (CLOSED)</b><br>Chốt giá vốn vĩnh viễn và đồng bộ vào Báo cáo tài chính"]

    style START fill:#334155,stroke:#94A3B8,color:#FFFFFF,stroke-width:2px
    style G1 fill:#78350F,stroke:#FBBF24,color:#FFFFFF,stroke-width:2px
    style G2 fill:#78350F,stroke:#FBBF24,color:#FFFFFF,stroke-width:2px
    style G3 fill:#78350F,stroke:#FBBF24,color:#FFFFFF,stroke-width:2px

    style STOP1 fill:#991B1B,stroke:#F87171,color:#FFFFFF,stroke-width:2px
    style STOP2 fill:#991B1B,stroke:#F87171,color:#FFFFFF,stroke-width:2px
    style STOP3 fill:#991B1B,stroke:#F87171,color:#FFFFFF,stroke-width:2px

    style PASS1 fill:#065F46,stroke:#34D399,color:#FFFFFF,stroke-width:2px
    style PASS2 fill:#065F46,stroke:#34D399,color:#FFFFFF,stroke-width:2px
    style PASS3 fill:#065F46,stroke:#34D399,color:#FFFFFF,stroke-width:2px
```

---

## 👥 6. BẢN VẼ 5: MA TRẬN PHÂN QUYỀN TRÁCH NHIỆM RACI (GOVERNANCE MATRIX)

| Chứng Từ / Khâu Nghiệp Vụ | 🛒 Thu Mua (`buyer`) | 🏛️ Tuân Thủ (`customs`) | 🚢 Logistics (`logistics`) | 📦 Thủ Kho (`warehouse`) | 💰 Kế Toán (`accountant`) | 👑 Giám Đốc (`cfo`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Đơn mua hàng (PO)** | 🟢 **R** *(Lập)* | ⚪ C *(Tham vấn)* | 🔵 I *(Xem)* | 🔵 I *(Xem)* | ⚪ C *(Kiểm tra tiền)* | 🟡 **A** *(Duyệt)* |
| **Duyệt Mã HS & Biểu Thuế** | 🔵 I *(Đề xuất)* | 🟢 **R** *(Duyệt)* | 🔵 I *(Xem)* | ─ | 🔵 I *(Xem thuế)* | 🟡 **A** |
| **Hành trình Tàu & Cont (M01-M05)** | 🔵 I *(Theo dõi)* | 🔵 I *(Theo dõi)* | 🟢 **R** *(Điều phối)* | ─ | ─ | 🟡 **A** |
| **Tờ khai Hải quan (M06-M07)** | ─ | 🟢 **R** *(Khai báo)* | ⚪ C *(Phối hợp)* | ─ | ⚪ C *(Nộp thuế)* | 🟡 **A** |
| **Phiếu Nhập kho (PR) (M09)** | ─ | ─ | 🔵 I *(Giao cont)* | 🟢 **R** *(Đếm hàng)* | 🔵 I *(Số lượng)* | 🟡 **A** |
| **Phân bổ Giá vốn (Landed Cost)** | ─ | ─ | ─ | ─ | 🟢 **R** *(Chạy LCV)* | 🟡 **A** |
| **Duyệt đóng lô VƯỢT NGÂN SÁCH** | ─ | ─ | ─ | ─ | 🔵 I *(Trình duyệt)* | 🔴 **R / A *(Ký duyệt)*** |

### 💡 Chú giải ký hiệu RACI chuẩn quốc tế:
* 🟢 **R (Responsible):** Người trực tiếp thao tác thực hiện công việc trên phần mềm.
* 🟡/🔴 **A (Accountable):** Người phê duyệt và chịu trách nhiệm tối cao *(Mỗi khâu chỉ có duy nhất 1 người A)*.
* ⚪ **C (Consulted):** Chuyên gia cần được hỏi ý kiến tham vấn trước khi quyết định.
* 🔵 **I (Informed):** Người nhận thông báo tự động từ hệ thống để nắm tình hình.
