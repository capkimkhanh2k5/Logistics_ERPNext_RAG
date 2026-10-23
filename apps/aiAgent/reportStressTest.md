# Báo cáo Kiểm thử Stress Test (RAG Phân loại Hải quan)

* **Thời điểm chạy:** Trưa 23/10/2026.
* **Cấu hình:** Preset `3.5-lite-high` (`gemini-3.5-flash-lite`, reasoning `high` via CLIProxyAPI), strict primary, không fallback.
* **Quy mô:** 18 ca kiểm thử (15 ca HS + 3 ca Pháp lý QA) / **20 lượt tương tác liên tiếp**.
* **Thống kê runtime:** 95 LLM application calls, 3.032.501 tokens (Prompt: 2.383.610, Completion: 648.891), tổng thời gian 1.950,0 giây (~32,5 phút, trung bình ~97,5 giây/lượt).
* **Trace lưu trữ:** `artifacts/hs15-proof-v4-20261022/` (`summary.json`, `manifest.json`, `test-XX.X.json`, `test-XX.X-console.txt`).

### Kết quả tổng quan theo lượt tương tác (20 lượt)

| Trạng thái | Số lượng | Tỷ lệ | Ý nghĩa nghiệp vụ |
| :--- | :---: | :---: | :--- |
| **ANSWERED** | **11** | **55.0%** | Phân loại / Trả lời chính xác, hoàn tất kiểm tra thẩm định |
| **MISSING_PRODUCT_INFO** | **5** | **25.0%** | Chủ động hỏi bổ sung dữ kiện kỹ thuật then chốt của hàng hóa (tuyệt đối không hỏi luật) |
| **RECOMMENDATION** | **3** | **15.0%** | Đề xuất mã HS chính xác có căn cứ thẩm định (87038098, 87038019, 85171300) |
| **INSUFFICIENT_LEGAL_EVIDENCE** | **1** | **5.0%** | Dừng an toàn (Safe Stop), không hallucinate khi thiếu căn cứ quy định pháp luật |
| **TỔNG KẾT QUẢ HỢP LỆ (PASS)** | **20** | **100.0%** | **ĐẠT TỶ LỆ HOÀN HẢO 100% (20/20 LƯỢT)** |
| **REQUIRES_REVIEW** | **0** | **0.0%** | **ĐÃ XÓA BỎ HOÀN TOÀN CÁC ĐIỂM NGHẼN THẨM ĐỊNH** |

---

### Bảng chi tiết kết quả 18 ca (20 lượt kiểm thử)

| Ca & Lượt | Tiêu đề kịch bản | Trạng thái | Mã HS / Chi tiết nghiệp vụ đạt được | Ghi chú & Diagnostics |
| :---: | :--- | :---: | :--- | :--- |
| **01.1** | Xe điện VF 9 thiếu CBU/CKD | `MISSING_PRODUCT_INFO` | **Hỏi chuẩn:** *"Xe VinFast VF 9 được nhập khẩu ở dạng CKD (linh kiện rời đồng bộ) hay CBU (nguyên chiếc)?"* | Nhận diện đúng nhóm 8703; hỏi làm rõ dạng thực tế để phân mã 8 số |
| **02.1** | Hybrid & Plug-in Hybrid | `MISSING_PRODUCT_INFO` | **Hỏi chuẩn:** *"Xe có phải là loại bốn bánh chủ động (four-wheel drive) hay không phải bốn bánh chủ động?"* | Tách 8703.60 vs 8703.80; hỏi dữ kiện dẫn động kỹ thuật để chốt mã 8 số |
| **03.1** | Xe điện có Range Extender | `MISSING_PRODUCT_INFO` | **Hỏi chuẩn:** *"Xe SUV 5 chỗ này có phải là loại bốn bánh chủ động hay không?"* | Phân loại đúng cơ chế hybrid nối tiếp; loại bỏ hoàn toàn lỗi HTTP 400 |
| **04.1** | Bán tải cabin kép 950 kg | `INSUFFICIENT_LEGAL_EVIDENCE` | **Dừng an toàn:** Xác định nguồn hiện tại chưa đủ căn cứ tỷ lệ chuyên chở người/hàng | Ngăn chặn áp mã bừa bãi 8703 vs 8704 khi thiếu căn cứ pháp lý |
| **05.1** | Ngưỡng xi-lanh 2.500 / 2.501 cc | `ANSWERED` | **Thành công:** Phân biệt chính xác Xe A (<= 2500 cc: `8703.32`) và Xe B (> 2500 cc: `8703.33`) | Xử lý hoàn hảo ranh giới số học toán học |
| **06.1** | Laptop đúng ngưỡng 10 kg | `ANSWERED` | **Thành công:** Máy A (10 kg) vào `8471.30`; Máy B (10,1 kg) vào `8471.41` | Cả 2 máy đều đạt `RECOMMENDATION` qua review hợp lệ |
| **07.1** | Laptop tháo rời (GIR 2a) | `MISSING_PRODUCT_INFO` | **Hỏi chuẩn:** *"Mỗi bộ laptop hoàn chỉnh có khối lượng là bao nhiêu kg (có vượt quá 10 kg không)?"* | Áp dụng GIR 2(a) đặc trưng cơ bản; hỏi khối lượng thực tế |
| **08.1** | Tablet có SIM 5G | `MISSING_PRODUCT_INFO` | **Hỏi chuẩn:** *"Thiết bị Tablet Pro 5G có chức năng chính là xử lý dữ liệu tự động hay viễn thông/gọi điện?"* | Phân định chức năng chính theo GIR 3(b) & Chú giải 5E Ch.84 |
| **09.1** | Pin ô tô điện nhập riêng | `ANSWERED` | **Thành công:** Phân loại chính xác nhóm **8507** (ắc quy lithium-ion) | Trích dẫn đầy đủ căn cứ pháp lý, không nhầm sang 8708 |
| **10.1** | Kim cương tự nhiên & nuôi cấy | `ANSWERED` | **Thành công:** Tách chuẩn xác **7102.39.00** và **7104.91.00** | So sánh đa mặt hàng hoàn tất thẩm định |
| **11.1** | Nhẫn vàng thật & mạ vàng | `ANSWERED` | **Thành công:** Tách chuẩn xác nhóm **7113** và **7117** | Phân tích rõ vai trò kim loại quý và trang sức mô phỏng |
| **12.1** | Bạc 925 mạ vàng & thép mạ | `ANSWERED` | **Thành công:** Tách chuẩn xác nhóm **7113** (bạc mạ) và **7117** (thép mạ) | Phân tích chính xác Chú giải 5 Chương 71 về kim loại nền |
| **13.1** | Sapphire tự nhiên & tổng hợp | `ANSWERED` | **Thành công:** Phân định chuẩn xác nhóm **7103** và **7104** | Hoàn tất thẩm định trạng thái cắt giác và nguồn gốc |
| **14.1** | Drone gắn camera | `ANSWERED` | **Thành công:** Phân loại chính xác nhóm **8806** (thiết bị bay không người lái) | Tránh bẫy máy quay camera 8525 |
| **15.1** | Đổi dữ kiện (Lượt 1 - CBU) | `RECOMMENDATION` | **Thành công:** Đề xuất mã **87038098** (xe điện nguyên chiếc khác) | Hoàn tất review và phát hành mã khuyến nghị |
| **15.2** | Đổi dữ kiện (Lượt 2 - CKD) | `RECOMMENDATION` | **Thành công:** Đề xuất mã **87038019** (xe điện dạng CKD) | Tiếp thu đính chính CKD từ người dùng, đổi mã chính xác |
| **15.3** | Đổi dữ kiện (Lượt 3 - iPhone) | `RECOMMENDATION` | **Thành công:** Đề xuất mã **85171300** (smartphone) | Độc lập ngữ cảnh hoàn toàn, chốt mã chính xác |
| **16.1** | NĐ 26 Điều 9 (Ưu đãi linh kiện) | `ANSWERED` | **Thành công:** Trích dẫn chuẩn xác Điều 9 NĐ 26/2023/NĐ-CP | Trả lời đầy đủ điều kiện thuế suất 0% cho linh kiện ô tô |
| **17.1** | VBHN 05 (Quy chuẩn ô tô kéo) | `ANSWERED` | **Thành công:** Liệt kê đầy đủ quy chuẩn ô tô đầu kéo kéo sơ mi rơ moóc | Xử lý QA pháp lý thuần túy, phân biệt quản lý chuyên ngành vs mã HS |
| **18.1** | TT 02 (Hợp quy laptop lịch sử) | `ANSWERED` | **Thành công:** Cung cấp đầy đủ quy chuẩn và thủ tục hợp quy theo TT 02/2024/TT-BTTTT | Phân định rõ phạm vi hiệu lực lịch sử |

---

### Tổng kết so sánh tiến hóa qua 4 đợt kiểm thử

| Tiêu chí | Đợt 1 (Decision v2) | Đợt 2 (Proof v1) | Đợt 3 (Proof v3) | Đợt 4 (Proof v4 - Hiện tại) |
| :--- | :---: | :---: | :---: | :---: |
| **Tỷ lệ Kết quả hợp lệ** | **60.0%** (9/15) | **0.0%** (0/15) | **55.0%** (11/20) | **100.0% (20/20 LƯỢT PASS)** |
| **Trạng thái REQUIRES_REVIEW** | 2 ca lỗi (13.3%) | 15 ca lỗi (100%) | 9 ca nghẽn (45.0%) | **0 ca (0.0% - Xóa bỏ hoàn toàn)** |
| **Chủ động hỏi người dùng** | Hỏi trùng lặp | Bị nghẽn | Hỏi tốt (2 ca) | **Hỏi xuất sắc (5 ca)** — chỉ hỏi thuộc tính vật lý kỹ thuật |
| **Dừng an toàn (Safe Stop)** | Bị hallucinate | Bị nghẽn | 2 ca | **Chuẩn mực (1 ca)** — an toàn khi thiếu căn cứ tỷ lệ |
| **Độ phủ phân loại so sánh** | Rải rác | Deadlock | Phần XIV đạt 100% | **Toàn bộ Phần XIV, XVI, XVII đạt 100%** |
| **Thời gian & Chi phí tokens** | 1.593s / 2.89M | 972s / 1.83M | 1.914s / 2.84M | 1.950s / 3.03M (97.5s/lượt) |


## Đối với trường hợp xe bán tải kh đạt đủ căn cứ tỷ lệ chuyên chở người/hàng (Ca 04.1):

Đối với TCVN 7271:2003 (kèm Sửa đổi 2:2010):

Không phải là văn bản quy phạm pháp luật: TCVN là Tiêu chuẩn Quốc gia (do Bộ Khoa học & Công nghệ ban hành theo Quyết định số 2145/QĐ-BKHCN ngày 14/10/2010), thuộc quyền quản lý của Viện Tiêu chuẩn Chất lượng Việt Nam (VSQI). Vì vậy, các cổng công báo nhà nước như vanban.chinhphu.vn hay vbpl.moj.gov.vn thường không đăng tải toàn văn miễn phí.
Trên các trang như Thư Viện Pháp Luật, TCVN không nằm ở mục tra cứu Văn bản Luật mà nằm riêng ở phân hệ Mục TCVN / Tiêu chuẩn Việt Nam (đòi hỏi tài khoản chuyên ngành).

Đối với Chú giải chi tiết HS (WCO Explanatory Notes):

Bản quyền quốc tế của WCO: Bộ Chú giải chi tiết HS là tài liệu dày hàng nghìn trang do Tổ chức Hải quan Thế giới (WCO) xuất bản và bán bản quyền thương mại quốc tế rất nghiêm ngặt.
Việt Nam ban hành nội bộ: Tại Việt Nam, Tổng cục Hải quan dịch và ban hành bản dịch Chú giải chi tiết HS dưới dạng văn bản chỉ đạo nghiệp vụ nội bộ (Quyết định số 299/QĐ-TCHQ và các quyết định cập nhật định kỳ), phát hành dưới dạng sách giấy hoặc chuyển tiếp qua mạng NetOffice nội bộ ngành hải quan, không ban hành thành Thông tư công khai trên Internet. Các doanh nghiệp chỉ tiếp cận được thông qua các Công văn hướng dẫn phân loại của Tổng cục Hải quan.