# Thiết kế hệ thống quản trị xuất nhập khẩu trên ERPNext - Claude

### [Block 0] (font-claude-response relative leading-[1.65rem] [&)

Searched the web

Searched the web
Bước này chỉ trả lời câu hỏi "ERPNext đã có gì", còn thiếu gì để sang bước 5. Dưới đây là kết quả tra tài liệu ERPNext và Frappe vừa rồi, ghép lại với phần đã tra trước đó. Chỗ nào chỉ là hiểu biết chung của mình, mình ghi rõ.
Tổng quan: câu hỏi quản trị nào được hỗ trợ đến đâu
Câu hỏi quản trị
ERPNext có sẵn
Mức đáp ứng
2. Chi phí so với kế hoạch
Ghi chi phí vào phiếu nhập hoặc Landed Cost Voucher, hóa đơn dịch vụ ghi bằng Purchase Invoice
Một phần: có chỗ ghi chi phí thực,
không có dự toán
13. Giá vốn thật
Landed Cost Voucher tính lại giá trị định giá hàng tồn, báo cáo Gross Profit
Một phần: phân bổ còn hạn chế
3. Tiến độ lô hàng
Thông báo theo ngày, báo cáo
Ít:
không có mốc vận tải
1. Chọn nhà cung cấp
RFQ, báo giá nhà cung cấp, Supplier Scorecard
Một phần: so giá mua, chưa so giá về kho
4. Mã HS
Trường mã HS ở Item (đã nêu ở phần trước)
Ít
5. Phân quyền, duyệt, truy vết
Role, User Permission, Workflow, Track Changes
Gần đủ
Tỷ giá (tài chính)
Currency Exchange, chênh lệch thực hiện và chưa thực hiện
Đủ cho kế toán,
chưa gắn với từng lô
19. Chất lượng dữ liệu
Trường bắt buộc, báo cáo tự tạo
Một phần
1. Chi phí và giá vốn (câu 2 và 13)
ERPNext coi landed cost là tổng chi phí để hàng đến tay người mua, và đưa toàn bộ chi phí áp dụng vào giá trị định giá của mặt hàng. Có hai cách ghi:
Ghi ngay trong phiếu nhập kho (Purchase Receipt):
thêm chi phí vào bảng Taxes and Charges, đánh dấu loại "Valuation" hoặc "Total and Valuation". Khi submit, hệ thống tính landed cost của các mặt hàng và đưa vào giá trị định giá theo FIFO hoặc bình quân.
Ghi sau bằng Landed Cost Voucher:
dùng khi chi phí chưa biết lúc nhận hàng, ví dụ hóa đơn vận chuyển đến sau cả tháng. Voucher tính lại giá trị định giá của hàng.
Phần voucher cần hiểu kỹ ba điều:
Nó cần một Purchase Receipt hoặc Purchase Invoice có bật Update Stock làm gốc. Từ phiên bản 16, voucher còn dùng được cho phiếu nhập Manufacture và phiếu nhận gia công.
Nếu hàng đã giao đi thì giá vốn hàng bán (COGS) vẫn giữ theo giá trị định giá cũ.
Voucher không tính lại quá khứ. Điểm này khớp với câu hỏi trước của bạn về chi phí về muộn: chi phí đến sau khi đã bán thì không làm đổi giá vốn đã ghi. Quy tắc quản trị cần đặt ra là cảnh báo bán hàng từ lô chưa đóng chi phí.
Báo cáo Gross Profit (lợi nhuận gộp) hiện giá trị theo hóa đơn, mặt hàng, nhãn hiệu, và COGS tính từ giá trị định giá nên có cả landed cost nếu voucher đã được ghi.
Các giới hạn mình đã nêu ở phần trước vẫn còn: voucher chia theo số lượng hoặc giá trị, mỗi voucher một tiêu chí.
2. Tỷ giá và ngoại tệ
Đây là phần ERPNext làm khá đầy đủ ở mức kế toán:
Tỷ giá nhập tay hoặc tự lấy:
bảng Currency Exchange lưu tỷ giá được duyệt. Nếu chưa có bản ghi phù hợp, hệ thống có thể gọi nhà cung cấp tỷ giá đã cấu hình. Chính sách nguồn tỷ giá và người duyệt do doanh nghiệp tự quy định.
Chênh lệch thực hiện:
khi tỷ giá thanh toán khác tỷ giá hóa đơn, Payment Entry tính được chênh lệch.
Chênh lệch chưa thực hiện:
số dư ngoại tệ còn mở cuối kỳ được đánh giá lại bằng Exchange Rate Revaluation. Công cụ này đổi giá trị quy ra tiền công ty của tài khoản, không đổi số dư ngoại tệ, rồi sinh bút toán. Company có cài đặt để tạo tự động. Cần khai báo trước các tài khoản lãi lỗ tỷ giá thực hiện và chưa thực hiện.
Một lưu ý: một trang quảng cáo của bên thứ ba nói ERPNext lõi chỉ có một lượt đánh giá lại thủ công. Tài liệu chính thức lại nhắc có tùy chọn tạo tự động trong Company, nên mình tin tài liệu chính thức hơn, nhưng bạn nên thử trên phiên bản của mình.
Phần này làm tốt ở
cấp tài khoản kế toán
. Nó không phân tích chênh lệch theo từng lô hàng, và trong tài liệu mình tra không thấy khái niệm tỷ giá tính thuế hải quan theo tuần như đã bàn.
3. Tiến độ lô hàng (câu 3)
Những thứ ERPNext có sẵn:
Thông báo (Notification):
có thể gửi trước hoặc sau một số ngày so với một trường ngày bất kỳ, kèm điều kiện theo dữ liệu của chứng từ. Từ phiên bản 16, tùy chọn này dùng được cả với bảng con. Có thể gửi qua email, thông báo hệ thống, SMS hoặc Slack. Có trường "Set Property After Alert" để tránh gửi lặp.
Giới hạn thời gian:
một thảo luận trên diễn đàn cho biết thông báo theo ngày chạy theo chu kỳ hằng ngày, nên không báo theo giờ.
Điểm cần cẩn thận là
hàng đi đường
. ERPNext có chức năng Goods in Transit nhưng tài liệu nói rõ chỉ dùng cho việc chuyển hàng giữa các kho nội bộ, không dùng cho phiếu nhập từ nhà cung cấp. Cách làm của chức năng này là Stock Entry loại Material Transfer, bật Add to Transit, chuyển vào kho loại "Transit", rồi kết thúc bằng End Transit. Vì vậy hàng nhập đang trên tàu không có chỗ ghi nhận sẵn. Khi nào nên ghi nhận phiếu nhập kho (lúc hàng lên tàu, lúc về cảng, hay lúc nhập kho) là quyết định thiết kế cần bàn ở bước 5.
4. Phân quyền, duyệt và truy vết (câu 5)
Đây là phần mạnh nhất của ERPNext cho bài toán quản trị:
Role Permissions Manager:
mỗi loại chứng từ có danh sách quyền theo vai trò gồm xem, sửa, tạo, submit, amend. Có thể chia trường theo "mức quyền" để vai trò khác nhau thấy nhóm trường khác nhau. Quyền chỉ Select cho phép chọn một chứng từ mà không xem được toàn bộ nó.
User Permissions:
hạn chế một người dùng chỉ truy cập những bản ghi cụ thể. Có thể dùng để giới hạn đối tác theo hồ sơ của họ.
Workflow:
cơ chế máy trạng thái gồm các trạng thái và chuyển trạng thái, mỗi trạng thái quy định vai trò được sửa, mỗi chuyển trạng thái quy định vai trò được thực hiện, có điều kiện và gửi email khi vào trạng thái. Nên kiểm tra thử việc chặn người tạo tự duyệt chứng từ của mình, vì đây là yêu cầu tách nhiệm vụ.
Track Changes:
ghi lịch sử thay đổi trên chứng từ đã bật. Quản trị viên khi đóng vai người khác (tính năng mới từ phiên bản 15) vẫn được ghi nhận người thật thực hiện.
Phiên bản 16
có thêm che dữ liệu theo trường (Data Masking).
Người dùng bên ngoài:
hệ thống phân biệt người dùng loại hệ thống với người dùng có vai trò khách hàng hoặc nhà cung cấp. Cách dùng cho forwarder hay đại lý hải quan chưa được tài liệu mô tả trực tiếp, nên cần thử.
5. Chọn và đánh giá nhà cung cấp (câu 1 và 6)
Báo giá và so giá:
quy trình RFQ, báo giá nhà cung cấp, đơn mua, phiếu nhập, hóa đơn là chức năng cơ bản (hiểu biết chung của mình, chưa tra lại).
Supplier Scorecard:
tạo riêng cho từng nhà cung cấp (mỗi nhà cung cấp một scorecard), đánh giá theo tiêu chí như thời gian phản hồi báo giá, chất lượng hàng, tính đúng hạn của giao hàng. Trọng số các tiêu chí cộng lại bằng 100, công thức dùng các biến có sẵn, và có thể thêm biến mới bằng code ở phía máy chủ.
Giới hạn: scorecard đo hiệu quả của nhà cung cấp, không tính giá về đến kho nên chưa trả lời câu "rẻ hơn thật hay không".
6. Báo cáo và trang quản trị
ERPNext có bốn cơ chế báo cáo: Report Builder, Query Report, Script Report và Query Builder. Trang tổng quan dùng Workspace, Number Card, Dashboard Chart (hiểu biết chung của mình, chưa tra lại). Báo cáo đơn giản làm bằng cấu hình, báo cáo tính toán phức tạp cần Script Report.
Những điểm bước 4 để lại cho bước 5
Từ những gì ERPNext có, mình thấy bảy khoảng trống liên quan trực tiếp đến câu hỏi quản trị:
Không có
hồ sơ lô hàng
làm khóa nối. Chi phí, hóa đơn, thanh toán, nhập kho chưa gắn về một lô.
Không có
dự toán
để so với chi phí thực.
Phân bổ chi phí
chỉ một tiêu chí trong mỗi voucher
.
Hàng nhập đang đi đường
chưa có chỗ ghi nhận.
Chênh lệch tỷ giá làm ở cấp tài khoản,
chưa tách theo lô
, và không có tỷ giá tính thuế hải quan.
Không có
mốc vận tải
, vận đơn, container, tờ khai, giấy phép, L/C, biểu thuế HS.
Chưa có cách kiểm tra
chất lượng dữ liệu
của lô (thiếu ETA thực tế, chưa đối chiếu chi phí).
Hạn chế của kết quả tra
Tài liệu ERPNext khác nhau theo phiên bản (một số tính năng chỉ từ 15 hoặc 16), nên bạn cần xác định mình dùng phiên bản nào.
Một số nguồn là diễn đàn hoặc trang bên thứ ba, và mình chỉ dùng chúng cho các điểm nhỏ.
Các chức năng mình ghi "hiểu biết chung" (RFQ, Workspace và Number Card) chưa được tra lại trong lần này.
Bạn xem bước 4 đã đủ chưa. Nếu rồi, mình sang bước 5: với mỗi khoảng trống trên, quyết định xử lý bằng cấu hình, doctype mới hay code, kèm các trường dữ liệu cần thiết để bắt đầu dựng trên ERPNext.

---

### [Block 1] (prose)

Bước này chỉ trả lời câu hỏi "ERPNext đã có gì", còn thiếu gì để sang bước 5. Dưới đây là kết quả tra tài liệu ERPNext và Frappe vừa rồi, ghép lại với phần đã tra trước đó. Chỗ nào chỉ là hiểu biết chung của mình, mình ghi rõ.
Tổng quan: câu hỏi quản trị nào được hỗ trợ đến đâu
Câu hỏi quản trị
ERPNext có sẵn
Mức đáp ứng
2. Chi phí so với kế hoạch
Ghi chi phí vào phiếu nhập hoặc Landed Cost Voucher, hóa đơn dịch vụ ghi bằng Purchase Invoice
Một phần: có chỗ ghi chi phí thực,
không có dự toán
13. Giá vốn thật
Landed Cost Voucher tính lại giá trị định giá hàng tồn, báo cáo Gross Profit
Một phần: phân bổ còn hạn chế
3. Tiến độ lô hàng
Thông báo theo ngày, báo cáo
Ít:
không có mốc vận tải
1. Chọn nhà cung cấp
RFQ, báo giá nhà cung cấp, Supplier Scorecard
Một phần: so giá mua, chưa so giá về kho
4. Mã HS
Trường mã HS ở Item (đã nêu ở phần trước)
Ít
5. Phân quyền, duyệt, truy vết
Role, User Permission, Workflow, Track Changes
Gần đủ
Tỷ giá (tài chính)
Currency Exchange, chênh lệch thực hiện và chưa thực hiện
Đủ cho kế toán,
chưa gắn với từng lô
19. Chất lượng dữ liệu
Trường bắt buộc, báo cáo tự tạo
Một phần
1. Chi phí và giá vốn (câu 2 và 13)
ERPNext coi landed cost là tổng chi phí để hàng đến tay người mua, và đưa toàn bộ chi phí áp dụng vào giá trị định giá của mặt hàng. Có hai cách ghi:
Ghi ngay trong phiếu nhập kho (Purchase Receipt):
thêm chi phí vào bảng Taxes and Charges, đánh dấu loại "Valuation" hoặc "Total and Valuation". Khi submit, hệ thống tính landed cost của các mặt hàng và đưa vào giá trị định giá theo FIFO hoặc bình quân.
Ghi sau bằng Landed Cost Voucher:
dùng khi chi phí chưa biết lúc nhận hàng, ví dụ hóa đơn vận chuyển đến sau cả tháng. Voucher tính lại giá trị định giá của hàng.
Phần voucher cần hiểu kỹ ba điều:
Nó cần một Purchase Receipt hoặc Purchase Invoice có bật Update Stock làm gốc. Từ phiên bản 16, voucher còn dùng được cho phiếu nhập Manufacture và phiếu nhận gia công.
Nếu hàng đã giao đi thì giá vốn hàng bán (COGS) vẫn giữ theo giá trị định giá cũ.
Voucher không tính lại quá khứ. Điểm này khớp với câu hỏi trước của bạn về chi phí về muộn: chi phí đến sau khi đã bán thì không làm đổi giá vốn đã ghi. Quy tắc quản trị cần đặt ra là cảnh báo bán hàng từ lô chưa đóng chi phí.
Báo cáo Gross Profit (lợi nhuận gộp) hiện giá trị theo hóa đơn, mặt hàng, nhãn hiệu, và COGS tính từ giá trị định giá nên có cả landed cost nếu voucher đã được ghi.
Các giới hạn mình đã nêu ở phần trước vẫn còn: voucher chia theo số lượng hoặc giá trị, mỗi voucher một tiêu chí.
2. Tỷ giá và ngoại tệ
Đây là phần ERPNext làm khá đầy đủ ở mức kế toán:
Tỷ giá nhập tay hoặc tự lấy:
bảng Currency Exchange lưu tỷ giá được duyệt. Nếu chưa có bản ghi phù hợp, hệ thống có thể gọi nhà cung cấp tỷ giá đã cấu hình. Chính sách nguồn tỷ giá và người duyệt do doanh nghiệp tự quy định.
Chênh lệch thực hiện:
khi tỷ giá thanh toán khác tỷ giá hóa đơn, Payment Entry tính được chênh lệch.
Chênh lệch chưa thực hiện:
số dư ngoại tệ còn mở cuối kỳ được đánh giá lại bằng Exchange Rate Revaluation. Công cụ này đổi giá trị quy ra tiền công ty của tài khoản, không đổi số dư ngoại tệ, rồi sinh bút toán. Company có cài đặt để tạo tự động. Cần khai báo trước các tài khoản lãi lỗ tỷ giá thực hiện và chưa thực hiện.
Một lưu ý: một trang quảng cáo của bên thứ ba nói ERPNext lõi chỉ có một lượt đánh giá lại thủ công. Tài liệu chính thức lại nhắc có tùy chọn tạo tự động trong Company, nên mình tin tài liệu chính thức hơn, nhưng bạn nên thử trên phiên bản của mình.
Phần này làm tốt ở
cấp tài khoản kế toán
. Nó không phân tích chênh lệch theo từng lô hàng, và trong tài liệu mình tra không thấy khái niệm tỷ giá tính thuế hải quan theo tuần như đã bàn.
3. Tiến độ lô hàng (câu 3)
Những thứ ERPNext có sẵn:
Thông báo (Notification):
có thể gửi trước hoặc sau một số ngày so với một trường ngày bất kỳ, kèm điều kiện theo dữ liệu của chứng từ. Từ phiên bản 16, tùy chọn này dùng được cả với bảng con. Có thể gửi qua email, thông báo hệ thống, SMS hoặc Slack. Có trường "Set Property After Alert" để tránh gửi lặp.
Giới hạn thời gian:
một thảo luận trên diễn đàn cho biết thông báo theo ngày chạy theo chu kỳ hằng ngày, nên không báo theo giờ.
Điểm cần cẩn thận là
hàng đi đường
. ERPNext có chức năng Goods in Transit nhưng tài liệu nói rõ chỉ dùng cho việc chuyển hàng giữa các kho nội bộ, không dùng cho phiếu nhập từ nhà cung cấp. Cách làm của chức năng này là Stock Entry loại Material Transfer, bật Add to Transit, chuyển vào kho loại "Transit", rồi kết thúc bằng End Transit. Vì vậy hàng nhập đang trên tàu không có chỗ ghi nhận sẵn. Khi nào nên ghi nhận phiếu nhập kho (lúc hàng lên tàu, lúc về cảng, hay lúc nhập kho) là quyết định thiết kế cần bàn ở bước 5.
4. Phân quyền, duyệt và truy vết (câu 5)
Đây là phần mạnh nhất của ERPNext cho bài toán quản trị:
Role Permissions Manager:
mỗi loại chứng từ có danh sách quyền theo vai trò gồm xem, sửa, tạo, submit, amend. Có thể chia trường theo "mức quyền" để vai trò khác nhau thấy nhóm trường khác nhau. Quyền chỉ Select cho phép chọn một chứng từ mà không xem được toàn bộ nó.
User Permissions:
hạn chế một người dùng chỉ truy cập những bản ghi cụ thể. Có thể dùng để giới hạn đối tác theo hồ sơ của họ.
Workflow:
cơ chế máy trạng thái gồm các trạng thái và chuyển trạng thái, mỗi trạng thái quy định vai trò được sửa, mỗi chuyển trạng thái quy định vai trò được thực hiện, có điều kiện và gửi email khi vào trạng thái. Nên kiểm tra thử việc chặn người tạo tự duyệt chứng từ của mình, vì đây là yêu cầu tách nhiệm vụ.
Track Changes:
ghi lịch sử thay đổi trên chứng từ đã bật. Quản trị viên khi đóng vai người khác (tính năng mới từ phiên bản 15) vẫn được ghi nhận người thật thực hiện.
Phiên bản 16
có thêm che dữ liệu theo trường (Data Masking).
Người dùng bên ngoài:
hệ thống phân biệt người dùng loại hệ thống với người dùng có vai trò khách hàng hoặc nhà cung cấp. Cách dùng cho forwarder hay đại lý hải quan chưa được tài liệu mô tả trực tiếp, nên cần thử.
5. Chọn và đánh giá nhà cung cấp (câu 1 và 6)
Báo giá và so giá:
quy trình RFQ, báo giá nhà cung cấp, đơn mua, phiếu nhập, hóa đơn là chức năng cơ bản (hiểu biết chung của mình, chưa tra lại).
Supplier Scorecard:
tạo riêng cho từng nhà cung cấp (mỗi nhà cung cấp một scorecard), đánh giá theo tiêu chí như thời gian phản hồi báo giá, chất lượng hàng, tính đúng hạn của giao hàng. Trọng số các tiêu chí cộng lại bằng 100, công thức dùng các biến có sẵn, và có thể thêm biến mới bằng code ở phía máy chủ.
Giới hạn: scorecard đo hiệu quả của nhà cung cấp, không tính giá về đến kho nên chưa trả lời câu "rẻ hơn thật hay không".
6. Báo cáo và trang quản trị
ERPNext có bốn cơ chế báo cáo: Report Builder, Query Report, Script Report và Query Builder. Trang tổng quan dùng Workspace, Number Card, Dashboard Chart (hiểu biết chung của mình, chưa tra lại). Báo cáo đơn giản làm bằng cấu hình, báo cáo tính toán phức tạp cần Script Report.
Những điểm bước 4 để lại cho bước 5
Từ những gì ERPNext có, mình thấy bảy khoảng trống liên quan trực tiếp đến câu hỏi quản trị:
Không có
hồ sơ lô hàng
làm khóa nối. Chi phí, hóa đơn, thanh toán, nhập kho chưa gắn về một lô.
Không có
dự toán
để so với chi phí thực.
Phân bổ chi phí
chỉ một tiêu chí trong mỗi voucher
.
Hàng nhập đang đi đường
chưa có chỗ ghi nhận.
Chênh lệch tỷ giá làm ở cấp tài khoản,
chưa tách theo lô
, và không có tỷ giá tính thuế hải quan.
Không có
mốc vận tải
, vận đơn, container, tờ khai, giấy phép, L/C, biểu thuế HS.
Chưa có cách kiểm tra
chất lượng dữ liệu
của lô (thiếu ETA thực tế, chưa đối chiếu chi phí).
Hạn chế của kết quả tra
Tài liệu ERPNext khác nhau theo phiên bản (một số tính năng chỉ từ 15 hoặc 16), nên bạn cần xác định mình dùng phiên bản nào.
Một số nguồn là diễn đàn hoặc trang bên thứ ba, và mình chỉ dùng chúng cho các điểm nhỏ.
Các chức năng mình ghi "hiểu biết chung" (RFQ, Workspace và Number Card) chưa được tra lại trong lần này.
Bạn xem bước 4 đã đủ chưa. Nếu rồi, mình sang bước 5: với mỗi khoảng trống trên, quyết định xử lý bằng cấu hình, doctype mới hay code, kèm các trường dữ liệu cần thiết để bắt đầu dựng trên ERPNext.

---

### [Block 2] (_blocks_4za3l_47 standard-markdown grid-cols-1 gri)

Bước này chỉ trả lời câu hỏi "ERPNext đã có gì", còn thiếu gì để sang bước 5. Dưới đây là kết quả tra tài liệu ERPNext và Frappe vừa rồi, ghép lại với phần đã tra trước đó. Chỗ nào chỉ là hiểu biết chung của mình, mình ghi rõ.
Tổng quan: câu hỏi quản trị nào được hỗ trợ đến đâu
Câu hỏi quản trị
ERPNext có sẵn
Mức đáp ứng
2. Chi phí so với kế hoạch
Ghi chi phí vào phiếu nhập hoặc Landed Cost Voucher, hóa đơn dịch vụ ghi bằng Purchase Invoice
Một phần: có chỗ ghi chi phí thực,
không có dự toán
13. Giá vốn thật
Landed Cost Voucher tính lại giá trị định giá hàng tồn, báo cáo Gross Profit
Một phần: phân bổ còn hạn chế
3. Tiến độ lô hàng
Thông báo theo ngày, báo cáo
Ít:
không có mốc vận tải
1. Chọn nhà cung cấp
RFQ, báo giá nhà cung cấp, Supplier Scorecard
Một phần: so giá mua, chưa so giá về kho
4. Mã HS
Trường mã HS ở Item (đã nêu ở phần trước)
Ít
5. Phân quyền, duyệt, truy vết
Role, User Permission, Workflow, Track Changes
Gần đủ
Tỷ giá (tài chính)
Currency Exchange, chênh lệch thực hiện và chưa thực hiện
Đủ cho kế toán,
chưa gắn với từng lô
19. Chất lượng dữ liệu
Trường bắt buộc, báo cáo tự tạo
Một phần
1. Chi phí và giá vốn (câu 2 và 13)
ERPNext coi landed cost là tổng chi phí để hàng đến tay người mua, và đưa toàn bộ chi phí áp dụng vào giá trị định giá của mặt hàng. Có hai cách ghi:
Ghi ngay trong phiếu nhập kho (Purchase Receipt):
thêm chi phí vào bảng Taxes and Charges, đánh dấu loại "Valuation" hoặc "Total and Valuation". Khi submit, hệ thống tính landed cost của các mặt hàng và đưa vào giá trị định giá theo FIFO hoặc bình quân.
Ghi sau bằng Landed Cost Voucher:
dùng khi chi phí chưa biết lúc nhận hàng, ví dụ hóa đơn vận chuyển đến sau cả tháng. Voucher tính lại giá trị định giá của hàng.
Phần voucher cần hiểu kỹ ba điều:
Nó cần một Purchase Receipt hoặc Purchase Invoice có bật Update Stock làm gốc. Từ phiên bản 16, voucher còn dùng được cho phiếu nhập Manufacture và phiếu nhận gia công.
Nếu hàng đã giao đi thì giá vốn hàng bán (COGS) vẫn giữ theo giá trị định giá cũ.
Voucher không tính lại quá khứ. Điểm này khớp với câu hỏi trước của bạn về chi phí về muộn: chi phí đến sau khi đã bán thì không làm đổi giá vốn đã ghi. Quy tắc quản trị cần đặt ra là cảnh báo bán hàng từ lô chưa đóng chi phí.
Báo cáo Gross Profit (lợi nhuận gộp) hiện giá trị theo hóa đơn, mặt hàng, nhãn hiệu, và COGS tính từ giá trị định giá nên có cả landed cost nếu voucher đã được ghi.
Các giới hạn mình đã nêu ở phần trước vẫn còn: voucher chia theo số lượng hoặc giá trị, mỗi voucher một tiêu chí.
2. Tỷ giá và ngoại tệ
Đây là phần ERPNext làm khá đầy đủ ở mức kế toán:
Tỷ giá nhập tay hoặc tự lấy:
bảng Currency Exchange lưu tỷ giá được duyệt. Nếu chưa có bản ghi phù hợp, hệ thống có thể gọi nhà cung cấp tỷ giá đã cấu hình. Chính sách nguồn tỷ giá và người duyệt do doanh nghiệp tự quy định.
Chênh lệch thực hiện:
khi tỷ giá thanh toán khác tỷ giá hóa đơn, Payment Entry tính được chênh lệch.
Chênh lệch chưa thực hiện:
số dư ngoại tệ còn mở cuối kỳ được đánh giá lại bằng Exchange Rate Revaluation. Công cụ này đổi giá trị quy ra tiền công ty của tài khoản, không đổi số dư ngoại tệ, rồi sinh bút toán. Company có cài đặt để tạo tự động. Cần khai báo trước các tài khoản lãi lỗ tỷ giá thực hiện và chưa thực hiện.
Một lưu ý: một trang quảng cáo của bên thứ ba nói ERPNext lõi chỉ có một lượt đánh giá lại thủ công. Tài liệu chính thức lại nhắc có tùy chọn tạo tự động trong Company, nên mình tin tài liệu chính thức hơn, nhưng bạn nên thử trên phiên bản của mình.
Phần này làm tốt ở
cấp tài khoản kế toán
. Nó không phân tích chênh lệch theo từng lô hàng, và trong tài liệu mình tra không thấy khái niệm tỷ giá tính thuế hải quan theo tuần như đã bàn.
3. Tiến độ lô hàng (câu 3)
Những thứ ERPNext có sẵn:
Thông báo (Notification):
có thể gửi trước hoặc sau một số ngày so với một trường ngày bất kỳ, kèm điều kiện theo dữ liệu của chứng từ. Từ phiên bản 16, tùy chọn này dùng được cả với bảng con. Có thể gửi qua email, thông báo hệ thống, SMS hoặc Slack. Có trường "Set Property After Alert" để tránh gửi lặp.
Giới hạn thời gian:
một thảo luận trên diễn đàn cho biết thông báo theo ngày chạy theo chu kỳ hằng ngày, nên không báo theo giờ.
Điểm cần cẩn thận là
hàng đi đường
. ERPNext có chức năng Goods in Transit nhưng tài liệu nói rõ chỉ dùng cho việc chuyển hàng giữa các kho nội bộ, không dùng cho phiếu nhập từ nhà cung cấp. Cách làm của chức năng này là Stock Entry loại Material Transfer, bật Add to Transit, chuyển vào kho loại "Transit", rồi kết thúc bằng End Transit. Vì vậy hàng nhập đang trên tàu không có chỗ ghi nhận sẵn. Khi nào nên ghi nhận phiếu nhập kho (lúc hàng lên tàu, lúc về cảng, hay lúc nhập kho) là quyết định thiết kế cần bàn ở bước 5.
4. Phân quyền, duyệt và truy vết (câu 5)
Đây là phần mạnh nhất của ERPNext cho bài toán quản trị:
Role Permissions Manager:
mỗi loại chứng từ có danh sách quyền theo vai trò gồm xem, sửa, tạo, submit, amend. Có thể chia trường theo "mức quyền" để vai trò khác nhau thấy nhóm trường khác nhau. Quyền chỉ Select cho phép chọn một chứng từ mà không xem được toàn bộ nó.
User Permissions:
hạn chế một người dùng chỉ truy cập những bản ghi cụ thể. Có thể dùng để giới hạn đối tác theo hồ sơ của họ.
Workflow:
cơ chế máy trạng thái gồm các trạng thái và chuyển trạng thái, mỗi trạng thái quy định vai trò được sửa, mỗi chuyển trạng thái quy định vai trò được thực hiện, có điều kiện và gửi email khi vào trạng thái. Nên kiểm tra thử việc chặn người tạo tự duyệt chứng từ của mình, vì đây là yêu cầu tách nhiệm vụ.
Track Changes:
ghi lịch sử thay đổi trên chứng từ đã bật. Quản trị viên khi đóng vai người khác (tính năng mới từ phiên bản 15) vẫn được ghi nhận người thật thực hiện.
Phiên bản 16
có thêm che dữ liệu theo trường (Data Masking).
Người dùng bên ngoài:
hệ thống phân biệt người dùng loại hệ thống với người dùng có vai trò khách hàng hoặc nhà cung cấp. Cách dùng cho forwarder hay đại lý hải quan chưa được tài liệu mô tả trực tiếp, nên cần thử.
5. Chọn và đánh giá nhà cung cấp (câu 1 và 6)
Báo giá và so giá:
quy trình RFQ, báo giá nhà cung cấp, đơn mua, phiếu nhập, hóa đơn là chức năng cơ bản (hiểu biết chung của mình, chưa tra lại).
Supplier Scorecard:
tạo riêng cho từng nhà cung cấp (mỗi nhà cung cấp một scorecard), đánh giá theo tiêu chí như thời gian phản hồi báo giá, chất lượng hàng, tính đúng hạn của giao hàng. Trọng số các tiêu chí cộng lại bằng 100, công thức dùng các biến có sẵn, và có thể thêm biến mới bằng code ở phía máy chủ.
Giới hạn: scorecard đo hiệu quả của nhà cung cấp, không tính giá về đến kho nên chưa trả lời câu "rẻ hơn thật hay không".
6. Báo cáo và trang quản trị
ERPNext có bốn cơ chế báo cáo: Report Builder, Query Report, Script Report và Query Builder. Trang tổng quan dùng Workspace, Number Card, Dashboard Chart (hiểu biết chung của mình, chưa tra lại). Báo cáo đơn giản làm bằng cấu hình, báo cáo tính toán phức tạp cần Script Report.
Những điểm bước 4 để lại cho bước 5
Từ những gì ERPNext có, mình thấy bảy khoảng trống liên quan trực tiếp đến câu hỏi quản trị:
Không có
hồ sơ lô hàng
làm khóa nối. Chi phí, hóa đơn, thanh toán, nhập kho chưa gắn về một lô.
Không có
dự toán
để so với chi phí thực.
Phân bổ chi phí
chỉ một tiêu chí trong mỗi voucher
.
Hàng nhập đang đi đường
chưa có chỗ ghi nhận.
Chênh lệch tỷ giá làm ở cấp tài khoản,
chưa tách theo lô
, và không có tỷ giá tính thuế hải quan.
Không có
mốc vận tải
, vận đơn, container, tờ khai, giấy phép, L/C, biểu thuế HS.
Chưa có cách kiểm tra
chất lượng dữ liệu
của lô (thiếu ETA thực tế, chưa đối chiếu chi phí).
Hạn chế của kết quả tra
Tài liệu ERPNext khác nhau theo phiên bản (một số tính năng chỉ từ 15 hoặc 16), nên bạn cần xác định mình dùng phiên bản nào.
Một số nguồn là diễn đàn hoặc trang bên thứ ba, và mình chỉ dùng chúng cho các điểm nhỏ.
Các chức năng mình ghi "hiểu biết chung" (RFQ, Workspace và Number Card) chưa được tra lại trong lần này.
Bạn xem bước 4 đã đủ chưa. Nếu rồi, mình sang bước 5: với mỗi khoảng trống trên, quyết định xử lý bằng cấu hình, doctype mới hay code, kèm các trường dữ liệu cần thiết để bắt đầu dựng trên ERPNext.

---

### [Block 3] (md-table-scroll prose-scroll print:overflow-x-visi)

Câu hỏi quản trị
ERPNext có sẵn
Mức đáp ứng
2. Chi phí so với kế hoạch
Ghi chi phí vào phiếu nhập hoặc Landed Cost Voucher, hóa đơn dịch vụ ghi bằng Purchase Invoice
Một phần: có chỗ ghi chi phí thực,
không có dự toán
13. Giá vốn thật
Landed Cost Voucher tính lại giá trị định giá hàng tồn, báo cáo Gross Profit
Một phần: phân bổ còn hạn chế
3. Tiến độ lô hàng
Thông báo theo ngày, báo cáo
Ít:
không có mốc vận tải
1. Chọn nhà cung cấp
RFQ, báo giá nhà cung cấp, Supplier Scorecard
Một phần: so giá mua, chưa so giá về kho
4. Mã HS
Trường mã HS ở Item (đã nêu ở phần trước)
Ít
5. Phân quyền, duyệt, truy vết
Role, User Permission, Workflow, Track Changes
Gần đủ
Tỷ giá (tài chính)
Currency Exchange, chênh lệch thực hiện và chưa thực hiện
Đủ cho kế toán,
chưa gắn với từng lô
19. Chất lượng dữ liệu
Trường bắt buộc, báo cáo tự tạo
Một phần

---

### [Block 4] (font-claude-response relative leading-[1.65rem] [&)

Phân công vai trò, quy trình duyệt và thiết kế thông báo cảnh báo.

Phân công vai trò, quy trình duyệt và thiết kế thông báo cảnh báo.
Bước này chuyển từ "ERPNext có gì" sang "cần dựng gì". Mình đi theo thứ tự: nguyên tắc thiết kế, sơ đồ dữ liệu, xử lý từng khoảng trống, trường dữ liệu tối thiểu, vai trò và quy trình, các quyết định cần chốt.
Ba nguyên tắc thiết kế
Mọi thứ gắn về một hồ sơ lô hàng (Trade Shipment).
Đây là thứ giải quyết khoảng trống số 1, và các khoảng trống khác dựa vào nó.
Sổ sách vẫn do chứng từ chuẩn của ERPNext đảm nhiệm
(Purchase Receipt, Purchase Invoice, Landed Cost Voucher, Payment Entry). Doctype mới chỉ giữ thông tin quản trị mà ERPNext không có, và không tự ghi bút toán.
Code chỉ dùng cho tính toán và kiểm tra
: phân bổ chi phí, tra thuế và tỷ giá, chặn các thao tác sai. Còn lại làm bằng cấu hình.
Sơ đồ dữ liệu
V
visualize

V
visualize
show_widget

A. Bảy khoảng trống và cách xử lý
#
Khoảng trống
Cách xử lý
Loại việc
1
Không có hồ sơ lô hàng
Doctype
Trade Shipment
. Thêm trường liên kết "Lô hàng" vào Purchase Order, Purchase Receipt, Purchase Invoice
Doctype và custom field, không code
2
Không có dự toán so với thực tế
Bảng con
Dòng chi phí
trong lô hàng, có cột dự toán và thực tế. Danh mục
Charge Type
Doctype, ít code (tổng hợp số)
3
Phân bổ chỉ một tiêu chí
Nút "Phân bổ chi phí": code tính phần của từng mặt hàng theo tiêu chí của từng loại phí, lưu vào bảng
Phân bổ
, rồi tạo Landed Cost Voucher chuẩn
Code
4
Hàng đi đường chưa có chỗ ghi
Quyết định thiết kế, xem phần D
Quyết định, ít code
5
Tỷ giá chưa tách theo lô, không có tỷ giá tính thuế
Mỗi dòng chi phí lưu tỷ giá riêng. Doctype
Customs Exchange Rate
theo tuần. Báo cáo tách chênh lệch "do số tiền" và "do tỷ giá"
Doctype và Script Report
6
Không có mốc vận tải, vận đơn, tờ khai, giấy phép, mã HS
Trường vận đơn và bảng
Mốc thời gian
trong lô hàng. Doctype
Customs Declaration
(bản nhẹ),
HS Tariff Rate
,
Import Permit
,
Document Checklist
Doctype, ít code
7
Không kiểm soát chất lượng dữ liệu
Trường bắt buộc theo trạng thái, kiểm tra khi lưu, báo cáo "lô thiếu dữ liệu"
Cấu hình và code nhỏ
B. Trường dữ liệu tối thiểu
Kiểu viết tắt: Link là liên kết tới bản ghi khác, Table là bảng con.
Trade Shipment (hồ sơ lô hàng)
Trường
Kiểu
Ghi chú
Số lô
Tự đánh số
Khóa nối cho toàn bộ chứng từ
Nhà cung cấp
Link Supplier
Incoterm, địa điểm
Link Incoterm, Data
Dùng trường Incoterm có sẵn của ERPNext
Loại vận tải
Select
Biển nguyên container, biển hàng lẻ, hàng không
Forwarder
Link Supplier
Lọc theo Supplier Group "Forwarder"
Hãng vận chuyển
Link Supplier
Lọc theo Supplier Group "Hãng tàu/bay"
Số vận đơn nhà, số vận đơn hãng
Data
Hai số riêng như đã bàn
Cảng đi, cảng đến
Data
Đơn mua trong lô
Table
Mỗi dòng một Purchase Order
Tiền tệ, tỷ giá kế hoạch
Link Currency, Float
Dùng cho dự toán
Trạng thái
Select
Tự cập nhật theo mốc cuối cùng có ngày thực tế
Tình trạng chi phí
Select
Đang mở, chờ duyệt đóng, đã đóng
Tổng dự toán, tổng thực tế
Currency, chỉ đọc
Tổng hợp từ dòng chi phí
Mốc thời gian (bảng con)
Trường
Kiểu
Ghi chú
Tên mốc
Select
Đặt hàng, hàng sẵn sàng, chuyển rủi ro, tàu rời (ETD), tàu đến (ETA), đăng ký tờ khai, thông quan, hạn miễn phí lưu container, nhập kho
Ngày dự kiến, ngày thực tế
Date
Ngày thực tế bắt buộc khi trạng thái đi tới mốc đó
Người cập nhật, ghi chú
Link User, Text
Dòng chi phí (bảng con)
Trường
Kiểu
Ghi chú
Loại phí
Link Charge Type
Nhà cung cấp dịch vụ
Link Supplier
Loại tiền
Link Currency
Số tiền dự toán, tỷ giá dự toán
Currency, Float
Số tiền thực tế, tỷ giá thực tế, ngày áp tỷ giá
Currency, Float, Date
Ngày này quyết định tỷ giá lấy ở đâu
Thực tế VND
Currency, tự tính
Hóa đơn
Link Purchase Invoice
Dùng cho phí dịch vụ
Tờ khai
Link Customs Declaration
Dùng cho dòng thuế
Trạng thái
Select
Dự toán, đã về, đã đối chiếu
Chênh lệch do số tiền, do tỷ giá
Currency, tự tính
Theo công thức đã bàn ở phần tỷ giá
Charge Type (danh mục loại phí)
Trường
Kiểu
Ghi chú
Tên, nhóm
Data, Select
Hàng hóa, vận tải quốc tế, cảng, thuế, nội địa, tài chính, giám định, khác
Vào giá vốn
Check
VAT nhập khẩu được khấu trừ thì không đánh dấu
Vào trị giá hải quan
Check
Cước và bảo hiểm đến cửa khẩu thì có
Tiêu chí phân bổ
Select
Giá trị, số lượng, trọng lượng, thể tích, theo từng mặt hàng
Tài khoản chi phí
Link Account
Dùng khi tạo Landed Cost Voucher
Phân bổ theo mặt hàng (bảng con)
Trường
Kiểu
Ghi chú
Mặt hàng, dòng phiếu nhập
Link Item, Data
Loại phí, tiêu chí
Link, Select
Hệ số phân bổ
Float
Ví dụ tỷ trọng giá trị hoặc trọng lượng
Số tiền phân bổ (VND)
Currency
Nên có báo cáo cộng theo mặt hàng để ra giá vốn đơn vị cuối cùng.
Customs Declaration (bản nhẹ)
Trường
Kiểu
Ghi chú
Số tờ khai, ngày đăng ký, loại hình
Data, Date, Select
Lô hàng
Link Trade Shipment
Luồng
Select
Xanh, vàng, đỏ
Trạng thái
Select
Đã đăng ký, đang xử lý, bổ sung, thông quan
Tuần tỷ giá
Link Customs Exchange Rate
Tự tra theo ngày đăng ký
Dòng hàng (bảng con)
Table
Mặt hàng, mã HS, xuất xứ, trị giá hải quan, thuế suất thường, thuế suất áp dụng, căn cứ ưu đãi, thuế nhập khẩu, VAT
Tổng thuế phải nộp, ngày nộp
Currency, Date
Nhập từ tờ khai thực tế
Đại lý khai, file đính kèm
Link, Attach
HS Tariff Rate và Customs Exchange Rate
Doctype
Trường chính
HS Tariff Rate
Mã HS, mô tả, thuế suất thường, bảng con thuế suất theo hiệp định (tên hiệp định, mức thuế), hiệu lực từ, hiệu lực đến, chính sách quản lý (có yêu cầu giấy phép hoặc chuyên ngành không), nguồn văn bản
Customs Exchange Rate
Ngoại tệ, tỷ giá VND, tuần áp dụng từ và đến, ngày công bố làm căn cứ, nguồn
Custom field trên chứng từ chuẩn
Doctype
Trường thêm
Item
Mã HS (Link HS Tariff Rate), thể tích mỗi đơn vị, yêu cầu giấy phép (Check), mô tả thành phần và công dụng kỹ thuật (Text)
Purchase Order Item, Purchase Receipt Item
Mã HS (tự lấy từ Item), xuất xứ hàng
Purchase Order, Purchase Receipt, Purchase Invoice
Lô hàng (Link Trade Shipment)
Supplier
Incoterm mặc định. Phân loại đối tác dùng Supplier Group
Hai ghi chú nhỏ:
ERPNext đã có trường mã HS (Customs Tariff Number) ở Item. Bạn kiểm tra xem dùng lại được không, hay thay bằng liên kết tới HS Tariff Rate. Mình nghiêng về thay, vì cần thuế suất và hiệu lực theo ngày.
Trường mô tả thành phần và công dụng kỹ thuật của Item cần có ngay từ đầu, để sau này chatbot gợi ý mã HS có dữ liệu đọc.
C. Vai trò, quy trình duyệt, thông báo, báo cáo
Vai trò
Vai trò
Làm gì trong hệ thống
Duyệt gì
Thu mua quốc tế
Tạo đơn mua, tạo lô hàng, nhập dự toán
Đề xuất mã HS
Tuân thủ XNK
Quản lý HS Tariff Rate, giấy phép
Duyệt mã HS
Chứng từ XNK
Quản lý checklist chứng từ, gắn file
Điều phối logistics
Cập nhật mốc, container, vận đơn
Khai báo hải quan
Nhập tờ khai
Kế toán giá thành
Nhập chi phí thực, bấm phân bổ
Đối chiếu chi phí
Tài chính
Thanh toán, tỷ giá, đánh giá lại
Thủ kho
Nhận hàng, kiểm hàng
Giám đốc / kế toán trưởng
Xem tổng quan
Duyệt đóng chi phí khi vượt ngưỡng
Đối tác bên ngoài (forwarder, đại lý)
Xem hoặc cập nhật lô của mình
Cần thử, xem phần E
Nguyên tắc tách nhiệm vụ: người đề xuất mã HS không duyệt mã đó, và người nhập chi phí thực không tự duyệt đóng chi phí khi vượt ngưỡng.
Quy trình duyệt (Workflow)
Chỉ dùng Workflow ở những điểm cần duyệt thật, không dùng cho toàn bộ trạng thái lô hàng. Trạng thái lô nên tự cập nhật từ bảng mốc, vì Workflow gắn chặt với trạng thái nộp (docstatus) của chứng từ.
Duyệt mã HS:
nháp → chờ duyệt → đã duyệt, vai trò duyệt là Tuân thủ XNK.
Đóng chi phí lô:
đang mở → (nếu lệch dự toán quá ngưỡng) chờ duyệt → đã đóng. Có thao tác "mở lại" cần người có quyền duyệt.
Duyệt đơn mua ngoại tệ lớn
(nếu thấy cần).
Thông báo (Notification)
Sự kiện
Gửi cho
ETA đổi hoặc đã qua mà chưa đến
Thu mua, thủ kho
Sắp hết hạn miễn phí lưu container (trước N ngày)
Điều phối logistics
Giấy phép sắp hết hạn
Tuân thủ XNK
Sắp đến ETA mà checklist chứng từ còn thiếu
Chứng từ XNK
Hàng đã nhập kho nhưng còn dòng chi phí chưa có thực tế
Kế toán giá thành
Chi phí thực tế vượt dự toán quá ngưỡng
Kế toán giá thành, giám đốc
Báo cáo, đối chiếu với câu hỏi quản trị
Câu hỏi
Báo cáo
2
Dự toán so với thực tế theo lô và theo loại phí. Báo cáo tách chênh lệch do số tiền và do tỷ giá
13
Giá vốn đơn vị theo sản phẩm qua các lô, kèm biên lợi nhuận
3
Lô hàng đang đi đường, lô trễ, giá trị hàng chưa về
1
So sánh giá về kho giữa các nhà cung cấp, dựa trên lô ở trạng thái kế hoạch
4
Mã HS chờ duyệt, giấy phép và chứng từ sắp hết hạn
19
Lô thiếu dữ liệu (thiếu ETA thực tế, chưa đối chiếu chi phí)
D. Các quyết định cần chốt trước khi dựng
1. Hàng đang đi đường ghi nhận thế nào.
Mình đề xuất hai cách:
Cách
Làm gì
Ưu
Nhược
A (khuyến nghị cho đồ án)
Chưa tạo phiếu nhập kho cho đến khi hàng thật sự nhập kho. Hàng đang đi đường nằm trong lô ở trạng thái "đang vận chuyển". Giá trị hàng đi đường lấy từ báo cáo trên đơn mua chưa nhận
Đơn giản, không đụng sổ kho
Sổ sách chưa thấy hàng đi đường
B
Ghi phiếu nhập kho vào một kho loại Transit khi chuyển rủi ro, rồi chuyển sang kho thật khi hàng về
Số liệu nằm trong sổ kho
Chức năng Goods in Transit có sẵn chỉ dành cho chuyển kho nội bộ, dùng cho phiếu nhập từ nhà cung cấp là tự ghép, chưa kiểm chứng và làm phức tạp việc phân bổ chi phí
2. Bảng loại phí mặc định.
Mình đề xuất khởi đầu như sau, các dòng có dấu hỏi cần xác nhận với giảng viên hoặc kế toán:
Loại phí
Vào giá vốn
Vào trị giá hải quan
Tiêu chí phân bổ
Cước vận tải quốc tế
Có
Có
Giá trị
Bảo hiểm hàng hóa
Có
Có
Giá trị
Thuế nhập khẩu
Có
Không
Theo từng mặt hàng
VAT nhập khẩu
Không (khấu trừ)
Không
Không áp dụng
Phí cảng, THC
Có
Không
Trọng lượng hoặc thể tích
Vận chuyển nội địa
Có
Không
Trọng lượng
Phí giám định bắt buộc
Có
Không
Giá trị
Phí lưu container, lưu bãi do chậm
?
Không
?
Phí ngân hàng
?
Không
?
Chênh lệch tỷ giá khi thanh toán
Không (tài chính)
Không
Không áp dụng
3. Khi nào đóng chi phí lô, và mở lại thế nào.
Gợi ý: đóng khi mọi dòng chi phí cần vào giá vốn đã có thực tế. Chi phí về sau khi đã đóng thì tạo dòng điều chỉnh, có duyệt, và phần hàng đã bán không tính lại quá khứ (như đã thấy ở bước 4).
4. Tỷ giá kế hoạch lấy ở đâu.
Gợi ý: nhập tay khi tạo lô, lấy từ tỷ giá gần nhất.
5. Chênh lệch dòng chi phí vượt ngưỡng nào thì cần duyệt.
Chọn một con số khởi đầu, ví dụ 10%, và để người quản trị chỉnh.
E. Điểm kỹ thuật cần thử sớm trên ERPNext
Làm trước khi dựng phần còn lại, vì kết quả có thể đổi thiết kế:
Landed Cost Voucher phân bổ thủ công:
có chạy đúng không, và tạo được bằng code không. Đây là điểm rủi ro nhất, dùng lô ví dụ ở phần đầu (giá vốn A 7.373, B 4.740) làm đáp án kiểm tra.
Quy tắc tạo voucher từ code:
có bị buộc phải lấy mặt hàng qua nút "Get Items from Purchase Receipts" không.
Gross Profit
có phản ánh giá vốn sau voucher đúng như mong đợi không.
Người dùng bên ngoài
(forwarder, đại lý) có xem và cập nhật được riêng lô của họ bằng User Permission không.
Thông báo trên bảng con
(ngày hạn miễn phí lưu container trong bảng Mốc): có dùng được trên phiên bản của bạn không. Từ phiên bản 16 có hỗ trợ.
Phiên bản ERPNext đang dùng.
Nhiều tính năng khác nhau giữa 14, 15 và 16.
Thứ tự dựng
Charge Type, HS Tariff Rate, Customs Exchange Rate (danh mục).
Trade Shipment và các bảng con, custom field trên chứng từ chuẩn.
Thử điểm kỹ thuật số 1 và 2 ở trên.
Nút phân bổ và báo cáo dự toán so với thực tế.
Vai trò, Workflow, Notification.
Customs Declaration, Import Permit, Document Checklist.
Báo cáo giá vốn, tách chênh lệch tỷ giá, chất lượng dữ liệu.
L/C và phần AI để sau.
Bạn xem bước 5 đã đủ ý chưa, nhất là mục D: những quyết định ở đó cần bạn hoặc giảng viên chốt. Nếu rồi, bước 6 mình đề xuất làm bộ dữ liệu mẫu và kịch bản kiểm thử từ lô ví dụ (có cả phần tỷ giá), để bạn dựng xong là chạy thử được ngay.

---

### [Block 5] (prose)

Bước này chuyển từ "ERPNext có gì" sang "cần dựng gì". Mình đi theo thứ tự: nguyên tắc thiết kế, sơ đồ dữ liệu, xử lý từng khoảng trống, trường dữ liệu tối thiểu, vai trò và quy trình, các quyết định cần chốt.
Ba nguyên tắc thiết kế
Mọi thứ gắn về một hồ sơ lô hàng (Trade Shipment).
Đây là thứ giải quyết khoảng trống số 1, và các khoảng trống khác dựa vào nó.
Sổ sách vẫn do chứng từ chuẩn của ERPNext đảm nhiệm
(Purchase Receipt, Purchase Invoice, Landed Cost Voucher, Payment Entry). Doctype mới chỉ giữ thông tin quản trị mà ERPNext không có, và không tự ghi bút toán.
Code chỉ dùng cho tính toán và kiểm tra
: phân bổ chi phí, tra thuế và tỷ giá, chặn các thao tác sai. Còn lại làm bằng cấu hình.
Sơ đồ dữ liệu

---

### [Block 6] (_blocks_4za3l_47 standard-markdown grid-cols-1 gri)

Bước này chuyển từ "ERPNext có gì" sang "cần dựng gì". Mình đi theo thứ tự: nguyên tắc thiết kế, sơ đồ dữ liệu, xử lý từng khoảng trống, trường dữ liệu tối thiểu, vai trò và quy trình, các quyết định cần chốt.
Ba nguyên tắc thiết kế
Mọi thứ gắn về một hồ sơ lô hàng (Trade Shipment).
Đây là thứ giải quyết khoảng trống số 1, và các khoảng trống khác dựa vào nó.
Sổ sách vẫn do chứng từ chuẩn của ERPNext đảm nhiệm
(Purchase Receipt, Purchase Invoice, Landed Cost Voucher, Payment Entry). Doctype mới chỉ giữ thông tin quản trị mà ERPNext không có, và không tự ghi bút toán.
Code chỉ dùng cho tính toán và kiểm tra
: phân bổ chi phí, tra thuế và tỷ giá, chặn các thao tác sai. Còn lại làm bằng cấu hình.
Sơ đồ dữ liệu

---

### [Block 7] (prose)

A. Bảy khoảng trống và cách xử lý
#
Khoảng trống
Cách xử lý
Loại việc
1
Không có hồ sơ lô hàng
Doctype
Trade Shipment
. Thêm trường liên kết "Lô hàng" vào Purchase Order, Purchase Receipt, Purchase Invoice
Doctype và custom field, không code
2
Không có dự toán so với thực tế
Bảng con
Dòng chi phí
trong lô hàng, có cột dự toán và thực tế. Danh mục
Charge Type
Doctype, ít code (tổng hợp số)
3
Phân bổ chỉ một tiêu chí
Nút "Phân bổ chi phí": code tính phần của từng mặt hàng theo tiêu chí của từng loại phí, lưu vào bảng
Phân bổ
, rồi tạo Landed Cost Voucher chuẩn
Code
4
Hàng đi đường chưa có chỗ ghi
Quyết định thiết kế, xem phần D
Quyết định, ít code
5
Tỷ giá chưa tách theo lô, không có tỷ giá tính thuế
Mỗi dòng chi phí lưu tỷ giá riêng. Doctype
Customs Exchange Rate
theo tuần. Báo cáo tách chênh lệch "do số tiền" và "do tỷ giá"
Doctype và Script Report
6
Không có mốc vận tải, vận đơn, tờ khai, giấy phép, mã HS
Trường vận đơn và bảng
Mốc thời gian
trong lô hàng. Doctype
Customs Declaration
(bản nhẹ),
HS Tariff Rate
,
Import Permit
,
Document Checklist
Doctype, ít code
7
Không kiểm soát chất lượng dữ liệu
Trường bắt buộc theo trạng thái, kiểm tra khi lưu, báo cáo "lô thiếu dữ liệu"
Cấu hình và code nhỏ
B. Trường dữ liệu tối thiểu
Kiểu viết tắt: Link là liên kết tới bản ghi khác, Table là bảng con.
Trade Shipment (hồ sơ lô hàng)
Trường
Kiểu
Ghi chú
Số lô
Tự đánh số
Khóa nối cho toàn bộ chứng từ
Nhà cung cấp
Link Supplier
Incoterm, địa điểm
Link Incoterm, Data
Dùng trường Incoterm có sẵn của ERPNext
Loại vận tải
Select
Biển nguyên container, biển hàng lẻ, hàng không
Forwarder
Link Supplier
Lọc theo Supplier Group "Forwarder"
Hãng vận chuyển
Link Supplier
Lọc theo Supplier Group "Hãng tàu/bay"
Số vận đơn nhà, số vận đơn hãng
Data
Hai số riêng như đã bàn
Cảng đi, cảng đến
Data
Đơn mua trong lô
Table
Mỗi dòng một Purchase Order
Tiền tệ, tỷ giá kế hoạch
Link Currency, Float
Dùng cho dự toán
Trạng thái
Select
Tự cập nhật theo mốc cuối cùng có ngày thực tế
Tình trạng chi phí
Select
Đang mở, chờ duyệt đóng, đã đóng
Tổng dự toán, tổng thực tế
Currency, chỉ đọc
Tổng hợp từ dòng chi phí
Mốc thời gian (bảng con)
Trường
Kiểu
Ghi chú
Tên mốc
Select
Đặt hàng, hàng sẵn sàng, chuyển rủi ro, tàu rời (ETD), tàu đến (ETA), đăng ký tờ khai, thông quan, hạn miễn phí lưu container, nhập kho
Ngày dự kiến, ngày thực tế
Date
Ngày thực tế bắt buộc khi trạng thái đi tới mốc đó
Người cập nhật, ghi chú
Link User, Text
Dòng chi phí (bảng con)
Trường
Kiểu
Ghi chú
Loại phí
Link Charge Type
Nhà cung cấp dịch vụ
Link Supplier
Loại tiền
Link Currency
Số tiền dự toán, tỷ giá dự toán
Currency, Float
Số tiền thực tế, tỷ giá thực tế, ngày áp tỷ giá
Currency, Float, Date
Ngày này quyết định tỷ giá lấy ở đâu
Thực tế VND
Currency, tự tính
Hóa đơn
Link Purchase Invoice
Dùng cho phí dịch vụ
Tờ khai
Link Customs Declaration
Dùng cho dòng thuế
Trạng thái
Select
Dự toán, đã về, đã đối chiếu
Chênh lệch do số tiền, do tỷ giá
Currency, tự tính
Theo công thức đã bàn ở phần tỷ giá
Charge Type (danh mục loại phí)
Trường
Kiểu
Ghi chú
Tên, nhóm
Data, Select
Hàng hóa, vận tải quốc tế, cảng, thuế, nội địa, tài chính, giám định, khác
Vào giá vốn
Check
VAT nhập khẩu được khấu trừ thì không đánh dấu
Vào trị giá hải quan
Check
Cước và bảo hiểm đến cửa khẩu thì có
Tiêu chí phân bổ
Select
Giá trị, số lượng, trọng lượng, thể tích, theo từng mặt hàng
Tài khoản chi phí
Link Account
Dùng khi tạo Landed Cost Voucher
Phân bổ theo mặt hàng (bảng con)
Trường
Kiểu
Ghi chú
Mặt hàng, dòng phiếu nhập
Link Item, Data
Loại phí, tiêu chí
Link, Select
Hệ số phân bổ
Float
Ví dụ tỷ trọng giá trị hoặc trọng lượng
Số tiền phân bổ (VND)
Currency
Nên có báo cáo cộng theo mặt hàng để ra giá vốn đơn vị cuối cùng.
Customs Declaration (bản nhẹ)
Trường
Kiểu
Ghi chú
Số tờ khai, ngày đăng ký, loại hình
Data, Date, Select
Lô hàng
Link Trade Shipment
Luồng
Select
Xanh, vàng, đỏ
Trạng thái
Select
Đã đăng ký, đang xử lý, bổ sung, thông quan
Tuần tỷ giá
Link Customs Exchange Rate
Tự tra theo ngày đăng ký
Dòng hàng (bảng con)
Table
Mặt hàng, mã HS, xuất xứ, trị giá hải quan, thuế suất thường, thuế suất áp dụng, căn cứ ưu đãi, thuế nhập khẩu, VAT
Tổng thuế phải nộp, ngày nộp
Currency, Date
Nhập từ tờ khai thực tế
Đại lý khai, file đính kèm
Link, Attach
HS Tariff Rate và Customs Exchange Rate
Doctype
Trường chính
HS Tariff Rate
Mã HS, mô tả, thuế suất thường, bảng con thuế suất theo hiệp định (tên hiệp định, mức thuế), hiệu lực từ, hiệu lực đến, chính sách quản lý (có yêu cầu giấy phép hoặc chuyên ngành không), nguồn văn bản
Customs Exchange Rate
Ngoại tệ, tỷ giá VND, tuần áp dụng từ và đến, ngày công bố làm căn cứ, nguồn
Custom field trên chứng từ chuẩn
Doctype
Trường thêm
Item
Mã HS (Link HS Tariff Rate), thể tích mỗi đơn vị, yêu cầu giấy phép (Check), mô tả thành phần và công dụng kỹ thuật (Text)
Purchase Order Item, Purchase Receipt Item
Mã HS (tự lấy từ Item), xuất xứ hàng
Purchase Order, Purchase Receipt, Purchase Invoice
Lô hàng (Link Trade Shipment)
Supplier
Incoterm mặc định. Phân loại đối tác dùng Supplier Group
Hai ghi chú nhỏ:
ERPNext đã có trường mã HS (Customs Tariff Number) ở Item. Bạn kiểm tra xem dùng lại được không, hay thay bằng liên kết tới HS Tariff Rate. Mình nghiêng về thay, vì cần thuế suất và hiệu lực theo ngày.
Trường mô tả thành phần và công dụng kỹ thuật của Item cần có ngay từ đầu, để sau này chatbot gợi ý mã HS có dữ liệu đọc.
C. Vai trò, quy trình duyệt, thông báo, báo cáo
Vai trò
Vai trò
Làm gì trong hệ thống
Duyệt gì
Thu mua quốc tế
Tạo đơn mua, tạo lô hàng, nhập dự toán
Đề xuất mã HS
Tuân thủ XNK
Quản lý HS Tariff Rate, giấy phép
Duyệt mã HS
Chứng từ XNK
Quản lý checklist chứng từ, gắn file
Điều phối logistics
Cập nhật mốc, container, vận đơn
Khai báo hải quan
Nhập tờ khai
Kế toán giá thành
Nhập chi phí thực, bấm phân bổ
Đối chiếu chi phí
Tài chính
Thanh toán, tỷ giá, đánh giá lại
Thủ kho
Nhận hàng, kiểm hàng
Giám đốc / kế toán trưởng
Xem tổng quan
Duyệt đóng chi phí khi vượt ngưỡng
Đối tác bên ngoài (forwarder, đại lý)
Xem hoặc cập nhật lô của mình
Cần thử, xem phần E
Nguyên tắc tách nhiệm vụ: người đề xuất mã HS không duyệt mã đó, và người nhập chi phí thực không tự duyệt đóng chi phí khi vượt ngưỡng.
Quy trình duyệt (Workflow)
Chỉ dùng Workflow ở những điểm cần duyệt thật, không dùng cho toàn bộ trạng thái lô hàng. Trạng thái lô nên tự cập nhật từ bảng mốc, vì Workflow gắn chặt với trạng thái nộp (docstatus) của chứng từ.
Duyệt mã HS:
nháp → chờ duyệt → đã duyệt, vai trò duyệt là Tuân thủ XNK.
Đóng chi phí lô:
đang mở → (nếu lệch dự toán quá ngưỡng) chờ duyệt → đã đóng. Có thao tác "mở lại" cần người có quyền duyệt.
Duyệt đơn mua ngoại tệ lớn
(nếu thấy cần).
Thông báo (Notification)
Sự kiện
Gửi cho
ETA đổi hoặc đã qua mà chưa đến
Thu mua, thủ kho
Sắp hết hạn miễn phí lưu container (trước N ngày)
Điều phối logistics
Giấy phép sắp hết hạn
Tuân thủ XNK
Sắp đến ETA mà checklist chứng từ còn thiếu
Chứng từ XNK
Hàng đã nhập kho nhưng còn dòng chi phí chưa có thực tế
Kế toán giá thành
Chi phí thực tế vượt dự toán quá ngưỡng
Kế toán giá thành, giám đốc
Báo cáo, đối chiếu với câu hỏi quản trị
Câu hỏi
Báo cáo
2
Dự toán so với thực tế theo lô và theo loại phí. Báo cáo tách chênh lệch do số tiền và do tỷ giá
13
Giá vốn đơn vị theo sản phẩm qua các lô, kèm biên lợi nhuận
3
Lô hàng đang đi đường, lô trễ, giá trị hàng chưa về
1
So sánh giá về kho giữa các nhà cung cấp, dựa trên lô ở trạng thái kế hoạch
4
Mã HS chờ duyệt, giấy phép và chứng từ sắp hết hạn
19
Lô thiếu dữ liệu (thiếu ETA thực tế, chưa đối chiếu chi phí)
D. Các quyết định cần chốt trước khi dựng
1. Hàng đang đi đường ghi nhận thế nào.
Mình đề xuất hai cách:
Cách
Làm gì
Ưu
Nhược
A (khuyến nghị cho đồ án)
Chưa tạo phiếu nhập kho cho đến khi hàng thật sự nhập kho. Hàng đang đi đường nằm trong lô ở trạng thái "đang vận chuyển". Giá trị hàng đi đường lấy từ báo cáo trên đơn mua chưa nhận
Đơn giản, không đụng sổ kho
Sổ sách chưa thấy hàng đi đường
B
Ghi phiếu nhập kho vào một kho loại Transit khi chuyển rủi ro, rồi chuyển sang kho thật khi hàng về
Số liệu nằm trong sổ kho
Chức năng Goods in Transit có sẵn chỉ dành cho chuyển kho nội bộ, dùng cho phiếu nhập từ nhà cung cấp là tự ghép, chưa kiểm chứng và làm phức tạp việc phân bổ chi phí
2. Bảng loại phí mặc định.
Mình đề xuất khởi đầu như sau, các dòng có dấu hỏi cần xác nhận với giảng viên hoặc kế toán:
Loại phí
Vào giá vốn
Vào trị giá hải quan
Tiêu chí phân bổ
Cước vận tải quốc tế
Có
Có
Giá trị
Bảo hiểm hàng hóa
Có
Có
Giá trị
Thuế nhập khẩu
Có
Không
Theo từng mặt hàng
VAT nhập khẩu
Không (khấu trừ)
Không
Không áp dụng
Phí cảng, THC
Có
Không
Trọng lượng hoặc thể tích
Vận chuyển nội địa
Có
Không
Trọng lượng
Phí giám định bắt buộc
Có
Không
Giá trị
Phí lưu container, lưu bãi do chậm
?
Không
?
Phí ngân hàng
?
Không
?
Chênh lệch tỷ giá khi thanh toán
Không (tài chính)
Không
Không áp dụng
3. Khi nào đóng chi phí lô, và mở lại thế nào.
Gợi ý: đóng khi mọi dòng chi phí cần vào giá vốn đã có thực tế. Chi phí về sau khi đã đóng thì tạo dòng điều chỉnh, có duyệt, và phần hàng đã bán không tính lại quá khứ (như đã thấy ở bước 4).
4. Tỷ giá kế hoạch lấy ở đâu.
Gợi ý: nhập tay khi tạo lô, lấy từ tỷ giá gần nhất.
5. Chênh lệch dòng chi phí vượt ngưỡng nào thì cần duyệt.
Chọn một con số khởi đầu, ví dụ 10%, và để người quản trị chỉnh.
E. Điểm kỹ thuật cần thử sớm trên ERPNext
Làm trước khi dựng phần còn lại, vì kết quả có thể đổi thiết kế:
Landed Cost Voucher phân bổ thủ công:
có chạy đúng không, và tạo được bằng code không. Đây là điểm rủi ro nhất, dùng lô ví dụ ở phần đầu (giá vốn A 7.373, B 4.740) làm đáp án kiểm tra.
Quy tắc tạo voucher từ code:
có bị buộc phải lấy mặt hàng qua nút "Get Items from Purchase Receipts" không.
Gross Profit
có phản ánh giá vốn sau voucher đúng như mong đợi không.
Người dùng bên ngoài
(forwarder, đại lý) có xem và cập nhật được riêng lô của họ bằng User Permission không.
Thông báo trên bảng con
(ngày hạn miễn phí lưu container trong bảng Mốc): có dùng được trên phiên bản của bạn không. Từ phiên bản 16 có hỗ trợ.
Phiên bản ERPNext đang dùng.
Nhiều tính năng khác nhau giữa 14, 15 và 16.
Thứ tự dựng
Charge Type, HS Tariff Rate, Customs Exchange Rate (danh mục).
Trade Shipment và các bảng con, custom field trên chứng từ chuẩn.
Thử điểm kỹ thuật số 1 và 2 ở trên.
Nút phân bổ và báo cáo dự toán so với thực tế.
Vai trò, Workflow, Notification.
Customs Declaration, Import Permit, Document Checklist.
Báo cáo giá vốn, tách chênh lệch tỷ giá, chất lượng dữ liệu.
L/C và phần AI để sau.
Bạn xem bước 5 đã đủ ý chưa, nhất là mục D: những quyết định ở đó cần bạn hoặc giảng viên chốt. Nếu rồi, bước 6 mình đề xuất làm bộ dữ liệu mẫu và kịch bản kiểm thử từ lô ví dụ (có cả phần tỷ giá), để bạn dựng xong là chạy thử được ngay.

---

### [Block 8] (_blocks_4za3l_47 standard-markdown grid-cols-1 gri)

A. Bảy khoảng trống và cách xử lý
#
Khoảng trống
Cách xử lý
Loại việc
1
Không có hồ sơ lô hàng
Doctype
Trade Shipment
. Thêm trường liên kết "Lô hàng" vào Purchase Order, Purchase Receipt, Purchase Invoice
Doctype và custom field, không code
2
Không có dự toán so với thực tế
Bảng con
Dòng chi phí
trong lô hàng, có cột dự toán và thực tế. Danh mục
Charge Type
Doctype, ít code (tổng hợp số)
3
Phân bổ chỉ một tiêu chí
Nút "Phân bổ chi phí": code tính phần của từng mặt hàng theo tiêu chí của từng loại phí, lưu vào bảng
Phân bổ
, rồi tạo Landed Cost Voucher chuẩn
Code
4
Hàng đi đường chưa có chỗ ghi
Quyết định thiết kế, xem phần D
Quyết định, ít code
5
Tỷ giá chưa tách theo lô, không có tỷ giá tính thuế
Mỗi dòng chi phí lưu tỷ giá riêng. Doctype
Customs Exchange Rate
theo tuần. Báo cáo tách chênh lệch "do số tiền" và "do tỷ giá"
Doctype và Script Report
6
Không có mốc vận tải, vận đơn, tờ khai, giấy phép, mã HS
Trường vận đơn và bảng
Mốc thời gian
trong lô hàng. Doctype
Customs Declaration
(bản nhẹ),
HS Tariff Rate
,
Import Permit
,
Document Checklist
Doctype, ít code
7
Không kiểm soát chất lượng dữ liệu
Trường bắt buộc theo trạng thái, kiểm tra khi lưu, báo cáo "lô thiếu dữ liệu"
Cấu hình và code nhỏ
B. Trường dữ liệu tối thiểu
Kiểu viết tắt: Link là liên kết tới bản ghi khác, Table là bảng con.
Trade Shipment (hồ sơ lô hàng)
Trường
Kiểu
Ghi chú
Số lô
Tự đánh số
Khóa nối cho toàn bộ chứng từ
Nhà cung cấp
Link Supplier
Incoterm, địa điểm
Link Incoterm, Data
Dùng trường Incoterm có sẵn của ERPNext
Loại vận tải
Select
Biển nguyên container, biển hàng lẻ, hàng không
Forwarder
Link Supplier
Lọc theo Supplier Group "Forwarder"
Hãng vận chuyển
Link Supplier
Lọc theo Supplier Group "Hãng tàu/bay"
Số vận đơn nhà, số vận đơn hãng
Data
Hai số riêng như đã bàn
Cảng đi, cảng đến
Data
Đơn mua trong lô
Table
Mỗi dòng một Purchase Order
Tiền tệ, tỷ giá kế hoạch
Link Currency, Float
Dùng cho dự toán
Trạng thái
Select
Tự cập nhật theo mốc cuối cùng có ngày thực tế
Tình trạng chi phí
Select
Đang mở, chờ duyệt đóng, đã đóng
Tổng dự toán, tổng thực tế
Currency, chỉ đọc
Tổng hợp từ dòng chi phí
Mốc thời gian (bảng con)
Trường
Kiểu
Ghi chú
Tên mốc
Select
Đặt hàng, hàng sẵn sàng, chuyển rủi ro, tàu rời (ETD), tàu đến (ETA), đăng ký tờ khai, thông quan, hạn miễn phí lưu container, nhập kho
Ngày dự kiến, ngày thực tế
Date
Ngày thực tế bắt buộc khi trạng thái đi tới mốc đó
Người cập nhật, ghi chú
Link User, Text
Dòng chi phí (bảng con)
Trường
Kiểu
Ghi chú
Loại phí
Link Charge Type
Nhà cung cấp dịch vụ
Link Supplier
Loại tiền
Link Currency
Số tiền dự toán, tỷ giá dự toán
Currency, Float
Số tiền thực tế, tỷ giá thực tế, ngày áp tỷ giá
Currency, Float, Date
Ngày này quyết định tỷ giá lấy ở đâu
Thực tế VND
Currency, tự tính
Hóa đơn
Link Purchase Invoice
Dùng cho phí dịch vụ
Tờ khai
Link Customs Declaration
Dùng cho dòng thuế
Trạng thái
Select
Dự toán, đã về, đã đối chiếu
Chênh lệch do số tiền, do tỷ giá
Currency, tự tính
Theo công thức đã bàn ở phần tỷ giá
Charge Type (danh mục loại phí)
Trường
Kiểu
Ghi chú
Tên, nhóm
Data, Select
Hàng hóa, vận tải quốc tế, cảng, thuế, nội địa, tài chính, giám định, khác
Vào giá vốn
Check
VAT nhập khẩu được khấu trừ thì không đánh dấu
Vào trị giá hải quan
Check
Cước và bảo hiểm đến cửa khẩu thì có
Tiêu chí phân bổ
Select
Giá trị, số lượng, trọng lượng, thể tích, theo từng mặt hàng
Tài khoản chi phí
Link Account
Dùng khi tạo Landed Cost Voucher
Phân bổ theo mặt hàng (bảng con)
Trường
Kiểu
Ghi chú
Mặt hàng, dòng phiếu nhập
Link Item, Data
Loại phí, tiêu chí
Link, Select
Hệ số phân bổ
Float
Ví dụ tỷ trọng giá trị hoặc trọng lượng
Số tiền phân bổ (VND)
Currency
Nên có báo cáo cộng theo mặt hàng để ra giá vốn đơn vị cuối cùng.
Customs Declaration (bản nhẹ)
Trường
Kiểu
Ghi chú
Số tờ khai, ngày đăng ký, loại hình
Data, Date, Select
Lô hàng
Link Trade Shipment
Luồng
Select
Xanh, vàng, đỏ
Trạng thái
Select
Đã đăng ký, đang xử lý, bổ sung, thông quan
Tuần tỷ giá
Link Customs Exchange Rate
Tự tra theo ngày đăng ký
Dòng hàng (bảng con)
Table
Mặt hàng, mã HS, xuất xứ, trị giá hải quan, thuế suất thường, thuế suất áp dụng, căn cứ ưu đãi, thuế nhập khẩu, VAT
Tổng thuế phải nộp, ngày nộp
Currency, Date
Nhập từ tờ khai thực tế
Đại lý khai, file đính kèm
Link, Attach
HS Tariff Rate và Customs Exchange Rate
Doctype
Trường chính
HS Tariff Rate
Mã HS, mô tả, thuế suất thường, bảng con thuế suất theo hiệp định (tên hiệp định, mức thuế), hiệu lực từ, hiệu lực đến, chính sách quản lý (có yêu cầu giấy phép hoặc chuyên ngành không), nguồn văn bản
Customs Exchange Rate
Ngoại tệ, tỷ giá VND, tuần áp dụng từ và đến, ngày công bố làm căn cứ, nguồn
Custom field trên chứng từ chuẩn
Doctype
Trường thêm
Item
Mã HS (Link HS Tariff Rate), thể tích mỗi đơn vị, yêu cầu giấy phép (Check), mô tả thành phần và công dụng kỹ thuật (Text)
Purchase Order Item, Purchase Receipt Item
Mã HS (tự lấy từ Item), xuất xứ hàng
Purchase Order, Purchase Receipt, Purchase Invoice
Lô hàng (Link Trade Shipment)
Supplier
Incoterm mặc định. Phân loại đối tác dùng Supplier Group
Hai ghi chú nhỏ:
ERPNext đã có trường mã HS (Customs Tariff Number) ở Item. Bạn kiểm tra xem dùng lại được không, hay thay bằng liên kết tới HS Tariff Rate. Mình nghiêng về thay, vì cần thuế suất và hiệu lực theo ngày.
Trường mô tả thành phần và công dụng kỹ thuật của Item cần có ngay từ đầu, để sau này chatbot gợi ý mã HS có dữ liệu đọc.
C. Vai trò, quy trình duyệt, thông báo, báo cáo
Vai trò
Vai trò
Làm gì trong hệ thống
Duyệt gì
Thu mua quốc tế
Tạo đơn mua, tạo lô hàng, nhập dự toán
Đề xuất mã HS
Tuân thủ XNK
Quản lý HS Tariff Rate, giấy phép
Duyệt mã HS
Chứng từ XNK
Quản lý checklist chứng từ, gắn file
Điều phối logistics
Cập nhật mốc, container, vận đơn
Khai báo hải quan
Nhập tờ khai
Kế toán giá thành
Nhập chi phí thực, bấm phân bổ
Đối chiếu chi phí
Tài chính
Thanh toán, tỷ giá, đánh giá lại
Thủ kho
Nhận hàng, kiểm hàng
Giám đốc / kế toán trưởng
Xem tổng quan
Duyệt đóng chi phí khi vượt ngưỡng
Đối tác bên ngoài (forwarder, đại lý)
Xem hoặc cập nhật lô của mình
Cần thử, xem phần E
Nguyên tắc tách nhiệm vụ: người đề xuất mã HS không duyệt mã đó, và người nhập chi phí thực không tự duyệt đóng chi phí khi vượt ngưỡng.
Quy trình duyệt (Workflow)
Chỉ dùng Workflow ở những điểm cần duyệt thật, không dùng cho toàn bộ trạng thái lô hàng. Trạng thái lô nên tự cập nhật từ bảng mốc, vì Workflow gắn chặt với trạng thái nộp (docstatus) của chứng từ.
Duyệt mã HS:
nháp → chờ duyệt → đã duyệt, vai trò duyệt là Tuân thủ XNK.
Đóng chi phí lô:
đang mở → (nếu lệch dự toán quá ngưỡng) chờ duyệt → đã đóng. Có thao tác "mở lại" cần người có quyền duyệt.
Duyệt đơn mua ngoại tệ lớn
(nếu thấy cần).
Thông báo (Notification)
Sự kiện
Gửi cho
ETA đổi hoặc đã qua mà chưa đến
Thu mua, thủ kho
Sắp hết hạn miễn phí lưu container (trước N ngày)
Điều phối logistics
Giấy phép sắp hết hạn
Tuân thủ XNK
Sắp đến ETA mà checklist chứng từ còn thiếu
Chứng từ XNK
Hàng đã nhập kho nhưng còn dòng chi phí chưa có thực tế
Kế toán giá thành
Chi phí thực tế vượt dự toán quá ngưỡng
Kế toán giá thành, giám đốc
Báo cáo, đối chiếu với câu hỏi quản trị
Câu hỏi
Báo cáo
2
Dự toán so với thực tế theo lô và theo loại phí. Báo cáo tách chênh lệch do số tiền và do tỷ giá
13
Giá vốn đơn vị theo sản phẩm qua các lô, kèm biên lợi nhuận
3
Lô hàng đang đi đường, lô trễ, giá trị hàng chưa về
1
So sánh giá về kho giữa các nhà cung cấp, dựa trên lô ở trạng thái kế hoạch
4
Mã HS chờ duyệt, giấy phép và chứng từ sắp hết hạn
19
Lô thiếu dữ liệu (thiếu ETA thực tế, chưa đối chiếu chi phí)
D. Các quyết định cần chốt trước khi dựng
1. Hàng đang đi đường ghi nhận thế nào.
Mình đề xuất hai cách:
Cách
Làm gì
Ưu
Nhược
A (khuyến nghị cho đồ án)
Chưa tạo phiếu nhập kho cho đến khi hàng thật sự nhập kho. Hàng đang đi đường nằm trong lô ở trạng thái "đang vận chuyển". Giá trị hàng đi đường lấy từ báo cáo trên đơn mua chưa nhận
Đơn giản, không đụng sổ kho
Sổ sách chưa thấy hàng đi đường
B
Ghi phiếu nhập kho vào một kho loại Transit khi chuyển rủi ro, rồi chuyển sang kho thật khi hàng về
Số liệu nằm trong sổ kho
Chức năng Goods in Transit có sẵn chỉ dành cho chuyển kho nội bộ, dùng cho phiếu nhập từ nhà cung cấp là tự ghép, chưa kiểm chứng và làm phức tạp việc phân bổ chi phí
2. Bảng loại phí mặc định.
Mình đề xuất khởi đầu như sau, các dòng có dấu hỏi cần xác nhận với giảng viên hoặc kế toán:
Loại phí
Vào giá vốn
Vào trị giá hải quan
Tiêu chí phân bổ
Cước vận tải quốc tế
Có
Có
Giá trị
Bảo hiểm hàng hóa
Có
Có
Giá trị
Thuế nhập khẩu
Có
Không
Theo từng mặt hàng
VAT nhập khẩu
Không (khấu trừ)
Không
Không áp dụng
Phí cảng, THC
Có
Không
Trọng lượng hoặc thể tích
Vận chuyển nội địa
Có
Không
Trọng lượng
Phí giám định bắt buộc
Có
Không
Giá trị
Phí lưu container, lưu bãi do chậm
?
Không
?
Phí ngân hàng
?
Không
?
Chênh lệch tỷ giá khi thanh toán
Không (tài chính)
Không
Không áp dụng
3. Khi nào đóng chi phí lô, và mở lại thế nào.
Gợi ý: đóng khi mọi dòng chi phí cần vào giá vốn đã có thực tế. Chi phí về sau khi đã đóng thì tạo dòng điều chỉnh, có duyệt, và phần hàng đã bán không tính lại quá khứ (như đã thấy ở bước 4).
4. Tỷ giá kế hoạch lấy ở đâu.
Gợi ý: nhập tay khi tạo lô, lấy từ tỷ giá gần nhất.
5. Chênh lệch dòng chi phí vượt ngưỡng nào thì cần duyệt.
Chọn một con số khởi đầu, ví dụ 10%, và để người quản trị chỉnh.
E. Điểm kỹ thuật cần thử sớm trên ERPNext
Làm trước khi dựng phần còn lại, vì kết quả có thể đổi thiết kế:
Landed Cost Voucher phân bổ thủ công:
có chạy đúng không, và tạo được bằng code không. Đây là điểm rủi ro nhất, dùng lô ví dụ ở phần đầu (giá vốn A 7.373, B 4.740) làm đáp án kiểm tra.
Quy tắc tạo voucher từ code:
có bị buộc phải lấy mặt hàng qua nút "Get Items from Purchase Receipts" không.
Gross Profit
có phản ánh giá vốn sau voucher đúng như mong đợi không.
Người dùng bên ngoài
(forwarder, đại lý) có xem và cập nhật được riêng lô của họ bằng User Permission không.
Thông báo trên bảng con
(ngày hạn miễn phí lưu container trong bảng Mốc): có dùng được trên phiên bản của bạn không. Từ phiên bản 16 có hỗ trợ.
Phiên bản ERPNext đang dùng.
Nhiều tính năng khác nhau giữa 14, 15 và 16.
Thứ tự dựng
Charge Type, HS Tariff Rate, Customs Exchange Rate (danh mục).
Trade Shipment và các bảng con, custom field trên chứng từ chuẩn.
Thử điểm kỹ thuật số 1 và 2 ở trên.
Nút phân bổ và báo cáo dự toán so với thực tế.
Vai trò, Workflow, Notification.
Customs Declaration, Import Permit, Document Checklist.
Báo cáo giá vốn, tách chênh lệch tỷ giá, chất lượng dữ liệu.
L/C và phần AI để sau.
Bạn xem bước 5 đã đủ ý chưa, nhất là mục D: những quyết định ở đó cần bạn hoặc giảng viên chốt. Nếu rồi, bước 6 mình đề xuất làm bộ dữ liệu mẫu và kịch bản kiểm thử từ lô ví dụ (có cả phần tỷ giá), để bạn dựng xong là chạy thử được ngay.

---

### [Block 9] (md-table-scroll prose-scroll print:overflow-x-visi)

#
Khoảng trống
Cách xử lý
Loại việc
1
Không có hồ sơ lô hàng
Doctype
Trade Shipment
. Thêm trường liên kết "Lô hàng" vào Purchase Order, Purchase Receipt, Purchase Invoice
Doctype và custom field, không code
2
Không có dự toán so với thực tế
Bảng con
Dòng chi phí
trong lô hàng, có cột dự toán và thực tế. Danh mục
Charge Type
Doctype, ít code (tổng hợp số)
3
Phân bổ chỉ một tiêu chí
Nút "Phân bổ chi phí": code tính phần của từng mặt hàng theo tiêu chí của từng loại phí, lưu vào bảng
Phân bổ
, rồi tạo Landed Cost Voucher chuẩn
Code
4
Hàng đi đường chưa có chỗ ghi
Quyết định thiết kế, xem phần D
Quyết định, ít code
5
Tỷ giá chưa tách theo lô, không có tỷ giá tính thuế
Mỗi dòng chi phí lưu tỷ giá riêng. Doctype
Customs Exchange Rate
theo tuần. Báo cáo tách chênh lệch "do số tiền" và "do tỷ giá"
Doctype và Script Report
6
Không có mốc vận tải, vận đơn, tờ khai, giấy phép, mã HS
Trường vận đơn và bảng
Mốc thời gian
trong lô hàng. Doctype
Customs Declaration
(bản nhẹ),
HS Tariff Rate
,
Import Permit
,
Document Checklist
Doctype, ít code
7
Không kiểm soát chất lượng dữ liệu
Trường bắt buộc theo trạng thái, kiểm tra khi lưu, báo cáo "lô thiếu dữ liệu"
Cấu hình và code nhỏ

---

### [Block 10] (md-table-scroll prose-scroll print:overflow-x-visi)

Trường
Kiểu
Ghi chú
Số lô
Tự đánh số
Khóa nối cho toàn bộ chứng từ
Nhà cung cấp
Link Supplier
Incoterm, địa điểm
Link Incoterm, Data
Dùng trường Incoterm có sẵn của ERPNext
Loại vận tải
Select
Biển nguyên container, biển hàng lẻ, hàng không
Forwarder
Link Supplier
Lọc theo Supplier Group "Forwarder"
Hãng vận chuyển
Link Supplier
Lọc theo Supplier Group "Hãng tàu/bay"
Số vận đơn nhà, số vận đơn hãng
Data
Hai số riêng như đã bàn
Cảng đi, cảng đến
Data
Đơn mua trong lô
Table
Mỗi dòng một Purchase Order
Tiền tệ, tỷ giá kế hoạch
Link Currency, Float
Dùng cho dự toán
Trạng thái
Select
Tự cập nhật theo mốc cuối cùng có ngày thực tế
Tình trạng chi phí
Select
Đang mở, chờ duyệt đóng, đã đóng
Tổng dự toán, tổng thực tế
Currency, chỉ đọc
Tổng hợp từ dòng chi phí

---

### [Block 11] (md-table-scroll prose-scroll print:overflow-x-visi)

Trường
Kiểu
Ghi chú
Tên mốc
Select
Đặt hàng, hàng sẵn sàng, chuyển rủi ro, tàu rời (ETD), tàu đến (ETA), đăng ký tờ khai, thông quan, hạn miễn phí lưu container, nhập kho
Ngày dự kiến, ngày thực tế
Date
Ngày thực tế bắt buộc khi trạng thái đi tới mốc đó
Người cập nhật, ghi chú
Link User, Text

---

### [Block 12] (md-table-scroll prose-scroll print:overflow-x-visi)

Trường
Kiểu
Ghi chú
Loại phí
Link Charge Type
Nhà cung cấp dịch vụ
Link Supplier
Loại tiền
Link Currency
Số tiền dự toán, tỷ giá dự toán
Currency, Float
Số tiền thực tế, tỷ giá thực tế, ngày áp tỷ giá
Currency, Float, Date
Ngày này quyết định tỷ giá lấy ở đâu
Thực tế VND
Currency, tự tính
Hóa đơn
Link Purchase Invoice
Dùng cho phí dịch vụ
Tờ khai
Link Customs Declaration
Dùng cho dòng thuế
Trạng thái
Select
Dự toán, đã về, đã đối chiếu
Chênh lệch do số tiền, do tỷ giá
Currency, tự tính
Theo công thức đã bàn ở phần tỷ giá

---

### [Block 13] (md-table-scroll prose-scroll print:overflow-x-visi)

Trường
Kiểu
Ghi chú
Tên, nhóm
Data, Select
Hàng hóa, vận tải quốc tế, cảng, thuế, nội địa, tài chính, giám định, khác
Vào giá vốn
Check
VAT nhập khẩu được khấu trừ thì không đánh dấu
Vào trị giá hải quan
Check
Cước và bảo hiểm đến cửa khẩu thì có
Tiêu chí phân bổ
Select
Giá trị, số lượng, trọng lượng, thể tích, theo từng mặt hàng
Tài khoản chi phí
Link Account
Dùng khi tạo Landed Cost Voucher

---

### [Block 14] (md-table-scroll prose-scroll print:overflow-x-visi)

Trường
Kiểu
Ghi chú
Mặt hàng, dòng phiếu nhập
Link Item, Data
Loại phí, tiêu chí
Link, Select
Hệ số phân bổ
Float
Ví dụ tỷ trọng giá trị hoặc trọng lượng
Số tiền phân bổ (VND)
Currency

---

### [Block 15] (md-table-scroll prose-scroll print:overflow-x-visi)

Trường
Kiểu
Ghi chú
Số tờ khai, ngày đăng ký, loại hình
Data, Date, Select
Lô hàng
Link Trade Shipment
Luồng
Select
Xanh, vàng, đỏ
Trạng thái
Select
Đã đăng ký, đang xử lý, bổ sung, thông quan
Tuần tỷ giá
Link Customs Exchange Rate
Tự tra theo ngày đăng ký
Dòng hàng (bảng con)
Table
Mặt hàng, mã HS, xuất xứ, trị giá hải quan, thuế suất thường, thuế suất áp dụng, căn cứ ưu đãi, thuế nhập khẩu, VAT
Tổng thuế phải nộp, ngày nộp
Currency, Date
Nhập từ tờ khai thực tế
Đại lý khai, file đính kèm
Link, Attach

---

### [Block 16] (md-table-scroll prose-scroll print:overflow-x-visi)

Doctype
Trường chính
HS Tariff Rate
Mã HS, mô tả, thuế suất thường, bảng con thuế suất theo hiệp định (tên hiệp định, mức thuế), hiệu lực từ, hiệu lực đến, chính sách quản lý (có yêu cầu giấy phép hoặc chuyên ngành không), nguồn văn bản
Customs Exchange Rate
Ngoại tệ, tỷ giá VND, tuần áp dụng từ và đến, ngày công bố làm căn cứ, nguồn

---

### [Block 17] (md-table-scroll prose-scroll print:overflow-x-visi)

Doctype
Trường thêm
Item
Mã HS (Link HS Tariff Rate), thể tích mỗi đơn vị, yêu cầu giấy phép (Check), mô tả thành phần và công dụng kỹ thuật (Text)
Purchase Order Item, Purchase Receipt Item
Mã HS (tự lấy từ Item), xuất xứ hàng
Purchase Order, Purchase Receipt, Purchase Invoice
Lô hàng (Link Trade Shipment)
Supplier
Incoterm mặc định. Phân loại đối tác dùng Supplier Group

---

### [Block 18] (md-table-scroll prose-scroll print:overflow-x-visi)

Vai trò
Làm gì trong hệ thống
Duyệt gì
Thu mua quốc tế
Tạo đơn mua, tạo lô hàng, nhập dự toán
Đề xuất mã HS
Tuân thủ XNK
Quản lý HS Tariff Rate, giấy phép
Duyệt mã HS
Chứng từ XNK
Quản lý checklist chứng từ, gắn file
Điều phối logistics
Cập nhật mốc, container, vận đơn
Khai báo hải quan
Nhập tờ khai
Kế toán giá thành
Nhập chi phí thực, bấm phân bổ
Đối chiếu chi phí
Tài chính
Thanh toán, tỷ giá, đánh giá lại
Thủ kho
Nhận hàng, kiểm hàng
Giám đốc / kế toán trưởng
Xem tổng quan
Duyệt đóng chi phí khi vượt ngưỡng
Đối tác bên ngoài (forwarder, đại lý)
Xem hoặc cập nhật lô của mình
Cần thử, xem phần E

---

### [Block 19] (md-table-scroll prose-scroll print:overflow-x-visi)

Sự kiện
Gửi cho
ETA đổi hoặc đã qua mà chưa đến
Thu mua, thủ kho
Sắp hết hạn miễn phí lưu container (trước N ngày)
Điều phối logistics
Giấy phép sắp hết hạn
Tuân thủ XNK
Sắp đến ETA mà checklist chứng từ còn thiếu
Chứng từ XNK
Hàng đã nhập kho nhưng còn dòng chi phí chưa có thực tế
Kế toán giá thành
Chi phí thực tế vượt dự toán quá ngưỡng
Kế toán giá thành, giám đốc

---

### [Block 20] (md-table-scroll prose-scroll print:overflow-x-visi)

Câu hỏi
Báo cáo
2
Dự toán so với thực tế theo lô và theo loại phí. Báo cáo tách chênh lệch do số tiền và do tỷ giá
13
Giá vốn đơn vị theo sản phẩm qua các lô, kèm biên lợi nhuận
3
Lô hàng đang đi đường, lô trễ, giá trị hàng chưa về
1
So sánh giá về kho giữa các nhà cung cấp, dựa trên lô ở trạng thái kế hoạch
4
Mã HS chờ duyệt, giấy phép và chứng từ sắp hết hạn
19
Lô thiếu dữ liệu (thiếu ETA thực tế, chưa đối chiếu chi phí)

---

### [Block 21] (md-table-scroll prose-scroll print:overflow-x-visi)

Cách
Làm gì
Ưu
Nhược
A (khuyến nghị cho đồ án)
Chưa tạo phiếu nhập kho cho đến khi hàng thật sự nhập kho. Hàng đang đi đường nằm trong lô ở trạng thái "đang vận chuyển". Giá trị hàng đi đường lấy từ báo cáo trên đơn mua chưa nhận
Đơn giản, không đụng sổ kho
Sổ sách chưa thấy hàng đi đường
B
Ghi phiếu nhập kho vào một kho loại Transit khi chuyển rủi ro, rồi chuyển sang kho thật khi hàng về
Số liệu nằm trong sổ kho
Chức năng Goods in Transit có sẵn chỉ dành cho chuyển kho nội bộ, dùng cho phiếu nhập từ nhà cung cấp là tự ghép, chưa kiểm chứng và làm phức tạp việc phân bổ chi phí

---

### [Block 22] (md-table-scroll prose-scroll print:overflow-x-visi)

Loại phí
Vào giá vốn
Vào trị giá hải quan
Tiêu chí phân bổ
Cước vận tải quốc tế
Có
Có
Giá trị
Bảo hiểm hàng hóa
Có
Có
Giá trị
Thuế nhập khẩu
Có
Không
Theo từng mặt hàng
VAT nhập khẩu
Không (khấu trừ)
Không
Không áp dụng
Phí cảng, THC
Có
Không
Trọng lượng hoặc thể tích
Vận chuyển nội địa
Có
Không
Trọng lượng
Phí giám định bắt buộc
Có
Không
Giá trị
Phí lưu container, lưu bãi do chậm
?
Không
?
Phí ngân hàng
?
Không
?
Chênh lệch tỷ giá khi thanh toán
Không (tài chính)
Không
Không áp dụng

---

### [Block 23] (font-claude-response relative leading-[1.65rem] [&)

Created 3 files, read a file, ran a command

Created 3 files, read a file, ran a command
Mình đang soạn tài liệu Word. Hai phần đầu đã xong, giờ viết phần thiết kế bổ sung, tỷ giá và lộ trình rồi dựng file.
Content part 3: design, exchange rates, decisions, roadmap, sources
part3.js
Content part 3: design, exchange rates, decisions, roadmap, sources part3.js

---

### [Block 24] (prose)

Mình đang soạn tài liệu Word. Hai phần đầu đã xong, giờ viết phần thiết kế bổ sung, tỷ giá và lộ trình rồi dựng file.

---

### [Block 25] (_blocks_4za3l_47 standard-markdown grid-cols-1 gri)

Mình đang soạn tài liệu Word. Hai phần đầu đã xong, giờ viết phần thiết kế bổ sung, tỷ giá và lộ trình rồi dựng file.

---

### [Block 26] (flex items-start gap-xs py-md font-sans text-body )

You are out of free
messages
(opens in new tab)
until 5:00 PM
Upgrade

---

### [Block 27] (bg-surface-3 [--cmp-pad-x:0.5rem] compact:[--cmp-p)

Write a message…





---

