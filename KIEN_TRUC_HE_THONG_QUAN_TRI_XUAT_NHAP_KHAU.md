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

## 📐 CHƯƠNG 2: BẢN VẼ KIẾN TRÚC TỔNG THỂ SONG TRỤC (TOGAF ENTERPRISE ARCHITECTURE)

Bản vẽ phân bổ hài hòa giữa **Chiều ngang (các bước đối xứng)** và **Chiều dọc (phân tầng chức năng)**, bảo đảm hiển thị vừa vặn trong một màn hình, chữ to rõ ràng, không bị thu nhỏ:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart TD
    %% ==========================================
    %% TẦNG 1: CON NGƯỜI & ĐIỀU HÀNH
    %% ==========================================
    subgraph T1["🏛️ TẦNG 1: VAI TRÒ NGHIỆP VỤ & TRẠM ĐIỀU HÀNH (ROLES & PRESENTATION)"]
        direction LR
        ROLES["👥 <b>ĐỘI NGŨ TÁC NGHIỆP ĐA PHÒNG BAN</b><br>🛒 Mua Hàng • 🌍 Bán Hàng QT • 🚢 Logistics • 🏛️ Hải Quan<br>📦 Thủ Kho • 💰 Kế Toán • 👑 Ban Giám Đốc / CFO"]
        DASH["📊 <b>THÁP CHỈ HUY TRUNG TÂM (CONTROL TOWER)</b><br>Theo dõi GPS tàu biển 3D • Cảnh báo phạt bãi cont<br>Báo cáo trễ hạn tàu • Cảnh báo rủi ro biến động tỷ giá"]
        ROLES <==> DASH
    end

    %% ==========================================
    %% TẦNG 2: TRỤC QUẢN TRỊ NGOẠI THƯƠNG
    %% ==========================================
    subgraph T2["🌐 TẦNG 2: TRUNG TÂM QUẢN TRỊ NGOẠI THƯƠNG & THUẬT TOÁN (SHARED CORE)"]
        direction LR
        TC["📂 <b>TRADE CASE (HỒ SƠ MẸ)</b><br>trade_type: Import / Export<br>Hợp đồng • PO / SO • Ngân sách"]
        TS["🚢 <b>TRADE SHIPMENT (CHUYẾN TÀU)</b><br>9 Mốc hành trình • Container & Free-time<br>Giám sát định vị • Chi phí thực tế"]
        VNACCS["🏛️ <b>VNACCS & TARIFF ENGINE</b><br>Tờ khai chuẩn 11 số • Biểu thuế HS<br>Tỷ giá hải quan tuần của BTC"]
        LOGIC["🧮 <b>ĐỘNG CƠ THUẬT TOÁN & BẢO VỆ</b><br>Phân bổ giá vốn VAS 02 (CBM/Trị giá)<br>Bóc tách lệch giá • 3 Cổng Stage Gates"]
        
        TC ==>|"1 Case nhiều đợt giao"| TS
        TS <==> VNACCS
        TS <==> LOGIC
    end

    %% ==========================================
    %% TẦNG 3: HAI LUỒNG CHỨNG TỪ SONG SONG
    %% ==========================================
    subgraph T3["⚙️ TẦNG 3: HAI LUỒNG CHỨNG TỪ ERPNEXT ĐỐI XỨNG (INBOUND & OUTBOUND)"]
        direction TB
        subgraph LUONG_NHAP["🔵 LUỒNG 1: NHẬP KHẨU (INBOUND PROCUREMENT)"]
            direction LR
            PO["1. Đơn Mua (PO)"] --> PR["2. Nhập Kho (PR)<br><i>Stage Gate 2 chặn</i>"] --> PI["3. Hóa Đơn Mua (PI)"] --> LCV["4. Phân Bổ Giá Vốn (LCV)"]
        end
        subgraph LUONG_XUAT["🟢 LUỒNG 2: XUẤT KHẨU (OUTBOUND SALES)"]
            direction LR
            SO["1. Đơn Bán (SO)"] --> DN["2. Xuất Kho Đóng Cont (DN)<br><i>Kiểm tra SI/VGM</i>"] --> SI["3. Hóa Đơn Xuất Khẩu (SI)"] --> PAY["4. Thu Ngoại Tệ (L/C, TT)"]
        end
    end

    %% ==========================================
    %% TẦNG 4: HẠ TẦNG KỸ THUẬT CONTAINER
    %% ==========================================
    subgraph T4["🐳 TẦNG 4: HẠ TẦNG KỸ THUẬT CONTAINER & DỮ LIỆU (INFRASTRUCTURE)"]
        direction LR
        DB["🗄️ <b>MariaDB 11.8</b><br>Giao dịch ACID • InnoDB"]
        REDIS["⚡ <b>Redis Cache & Queue</b><br>Đệm tọa độ • Job ngầm"]
        APP["💻 <b>Frappe App (:2828)</b><br>Backend & Frontend"]
        SOCK["🔄 <b>WebSocket & Scheduler</b><br>Tọa độ 3D • Quét hạn phạt"]
    end

    %% ==========================================
    %% LIÊN KẾT ĐA TẦNG DỌC
    %% ==========================================
    T1 ==>|"Thao tác & Ra quyết định"| T2
    T2 <===>|"Đồng bộ tiến độ & Kiểm soát Stage Gate"| T3
    T3 ==>|"Lưu trữ dữ liệu & Thực thi ngầm"| T4

    %% ==========================================
    %% PHỐI MÀU GIAO DIỆN DARK TECH
    %% ==========================================
    style T1 fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style T2 fill:#1E1B4B,stroke:#818CF8,stroke-width:2px,color:#FFFFFF
    style T3 fill:#042F2E,stroke:#2DD4BF,stroke-width:2px,color:#FFFFFF
    style T4 fill:#1E293B,stroke:#94A3B8,stroke-width:2px,color:#FFFFFF

    style LUONG_NHAP fill:#0B233D,stroke:#38BDF8,color:#FFFFFF
    style LUONG_XUAT fill:#064E3B,stroke:#34D399,color:#FFFFFF

    style ROLES fill:#0284C7,stroke:#38BDF8,color:#FFFFFF
    style DASH fill:#0369A1,stroke:#38BDF8,color:#FFFFFF

    style TC fill:#4338CA,stroke:#C7D2FE,color:#FFFFFF,stroke-width:2px
    style TS fill:#6D28D9,stroke:#DDD6FE,color:#FFFFFF,stroke-width:2px
    style VNACCS fill:#4C1D95,stroke:#DDD6FE,color:#FFFFFF
    style LOGIC fill:#7C2D12,stroke:#FDBA74,color:#FFFFFF

    style PO fill:#0369A1,stroke:#7DD3FC,color:#FFFFFF
    style PR fill:#0369A1,stroke:#7DD3FC,color:#FFFFFF
    style PI fill:#0369A1,stroke:#7DD3FC,color:#FFFFFF
    style LCV fill:#B45309,stroke:#FCD34D,color:#FFFFFF

    style SO fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style DN fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style SI fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style PAY fill:#047857,stroke:#6EE7B7,color:#FFFFFF

    style DB fill:#334155,stroke:#94A3B8,color:#FFFFFF
    style REDIS fill:#334155,stroke:#94A3B8,color:#FFFFFF
    style APP fill:#334155,stroke:#94A3B8,color:#FFFFFF
    style SOCK fill:#334155,stroke:#94A3B8,color:#FFFFFF
```

---

## 🎯 CHƯƠNG 3: MÔ HÌNH PHÂN TÁCH `TRADE CASE` VS `TRADE SHIPMENT` (PARTIAL SHIPMENT)

Giải quyết trọn vẹn bài toán: **1 Đơn hàng mua lớn (PO) được nhà máy chia làm 2 đợt giao trên 2 chuyến tàu khác nhau**:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart TD
    %% TẦNG HỒ SƠ THƯƠNG MẠI
    subgraph S_CASE["📂 TẦNG HỒ SƠ THƯƠNG MẠI: TRADE CASE (MÃ: IMP-2026-00001)"]
        direction TB
        PO["Đơn Mua Hàng PO: 1,000 iPhone 16 Pro Max ($1,000,000 USD) • Nhà cung cấp: Apple Inc"]
        POL_GOV["Chính Sách & Ngân Sách: Incoterm CIF Cát Lái • Biểu thuế HS 8517.13.00 (Thuế 0%) • Ngân sách tối đa: 25.5 Tỷ VND"]
        PO --- POL_GOV
    end

    %% TẦNG CHUYẾN TÀU CON
    subgraph S_SHP1["🚢 CHUYẾN TÀU 1 (SHIPMENT 1: TS-2026-00001)"]
        direction TB
        SHP1_INFO["<b>Giao Đợt 1: 600 iPhone</b><br>Tàu: Maersk Mc-Kinney Moller<br>Vận đơn B/L: MAEU11223344<br>Container: MSKU1234567 (40ft HC)<br>Hạn Free-time bãi: 7 ngày<br>Trạng thái: <b>Hoàn thành nhập kho & Landed Cost đợt 1</b>"]
    end

    subgraph S_SHP2["🚢 CHUYẾN TÀU 2 (SHIPMENT 2: TS-2026-00002)"]
        direction TB
        SHP2_INFO["<b>Giao Đợt 2: 400 iPhone</b><br>Tàu: MSC Oscar<br>Vận đơn B/L: MSCU99887766<br>Container: MSCU7654321 (40ft HC)<br>Hạn Free-time bãi: 7 ngày<br>Trạng thái: <b>Đang trên biển (In Transit)</b>"]
    end

    S_CASE ==>|"Đợt giao hàng 1 (Lập phiếu PR-001)"| S_SHP1
    S_CASE ==>|"Đợt giao hàng 2 (Lập phiếu PR-002)"| S_SHP2

    style S_CASE fill:#1E1B4B,stroke:#818CF8,stroke-width:3px,color:#FFFFFF
    style S_SHP1 fill:#064E3B,stroke:#34D399,stroke-width:2px,color:#FFFFFF
    style S_SHP2 fill:#0C4A6E,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF

    style PO fill:#3730A3,stroke:#A5B4FC,color:#FFFFFF
    style POL_GOV fill:#3730A3,stroke:#A5B4FC,color:#FFFFFF
    style SHP1_INFO fill:#047857,stroke:#6EE7B7,color:#FFFFFF
    style SHP2_INFO fill:#0369A1,stroke:#7DD3FC,color:#FFFFFF
```

---

## 🚦 CHƯƠNG 4: HỆ THỐNG CỔNG KIỂM SOÁT ĐIỀU KIỆN (DUAL-STREAM STAGE GATES)

Hệ thống hoạt động theo cơ chế **Quản trị Chủ động (Proactive Control)**: Trước khi chuyển sang bước tiếp theo, hệ thống tự động kiểm tra các điều kiện sẵn sàng đối xứng cho cả 2 luồng Nhập khẩu và Xuất khẩu:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '13px'}}}%%
flowchart TD
    subgraph GATES_IN["HỆ CỔNG KIỂM SOÁT NHẬP KHẨU (INBOUND GATES)"]
        direction TB
        IN_START(["1. Tàu Chở Hàng Đến Cảng Đến (POD)"]) --> IN_G1{"🚪 CỔNG 1: HỒ SƠ NGOẠI THƯƠNG<br><i>Đủ 100% C/O, Packing List, Invoice?</i>"}
        IN_G1 -- "❌ Chưa đủ" --> IN_STOP1["🚫 CHẶN: Không cho mở tờ khai VNACCS"]
        IN_G1 -- "✅ Đủ 100%" --> IN_PASS1["🟢 Chuyển mốc M06 (Khai hải quan)"]
        
        IN_PASS1 --> IN_G2{"🚪 CỔNG 2: THÔNG QUAN NHẬP KHO<br><i>Mốc M07 đã Completed chưa?</i>"}
        IN_G2 -- "❌ Chưa thông quan" --> IN_STOP2["🚫 <b>CHẶN SUBMIT PHIẾU NHẬP KHO (PR)</b><br>Thủ kho bị khóa quyền duyệt hàng vào kho"]
        IN_G2 -- "✅ Đã thông quan" --> IN_PASS2["🟢 Cho phép duyệt PR & Nhập kho (M09)"]

        IN_PASS2 --> IN_G3{"🚪 CỔNG 3: QUYẾT TOÁN GIÁ VỐN<br><i>Chi phí vượt dự toán > 10%?</i>"}
        IN_G3 -- "❌ Vượt > 10%" --> IN_STOP3["🔒 Khóa đóng lô, yêu cầu Giám đốc duyệt"]
        IN_G3 -- "✅ Trong định mức" --> IN_PASS3["🎉 Chạy Landed Cost (LCV) & Đóng lô"]
    end

    subgraph GATES_OUT["HỆ CỔNG KIỂM SOÁT XUẤT KHẨU (OUTBOUND GATES)"]
        direction TB
        OUT_START(["1. Đóng Hàng Cont Tại Kho Công Ty"]) --> OUT_G1{"🚪 CỔNG 1: HẠN CUT-OFF HÃNG TÀU<br><i>Đã gửi SI & Phiếu cân VGM trước cut-off?</i>"}
        OUT_G1 -- "❌ Trễ hạn" --> OUT_STOP1["🚫 BÁO ĐỘNG ĐỎ: Nguy cơ rớt tàu (Rolled cont)"]
        OUT_G1 -- "✅ Đủ SI & VGM" --> OUT_PASS1["🟢 Cấp phép hạ bãi cont cảng xuất (Gate-in)"]

        OUT_PASS1 --> OUT_G2{"🚪 CỔNG 2: THÔNG QUAN XUẤT KHẨU<br><i>Tờ khai xuất đã thông quan chưa?</i>"}
        OUT_G2 -- "❌ Chưa thông quan" --> OUT_STOP2["🚫 CHẶN: Hãng tàu từ chối cẩu cont lên tàu"]
        OUT_G2 -- "✅ Đã thông quan" --> OUT_PASS2["🟢 Cẩu cont lên tàu & Phát hành B/L gốc (M04)"]

        OUT_PASS2 --> OUT_G3{"🚪 CỔNG 3: THANH TOÁN QUỐC TẾ<br><i>Xuất trình B/L, C/O hợp lệ theo L/C?</i>"}
        OUT_G3 -- "❌ Bất hợp lệ (Discrepancy)" --> OUT_STOP3["🔒 Ngân hàng từ chối thanh toán ngoại tệ"]
        OUT_G3 -- "✅ Khớp 100% L/C" --> OUT_PASS3["🎉 Thu đủ 100% tiền hàng ngoại tệ về nước"]
    end

    style GATES_IN fill:#0F172A,stroke:#38BDF8,stroke-width:2px,color:#FFFFFF
    style GATES_OUT fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#FFFFFF
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
