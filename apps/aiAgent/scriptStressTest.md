# ĐỀ XUẤT HS

Mình đề xuất 15 test case độ khó cao đến cực khó để kiểm tra hệ thống RAG phân loại HS của bạn trên cả 3 Phần XIV, XVI và XVII.

## I. Phần XVII – Phương tiện vận tải

Độ khó: Cao – Cực khó

### Test 01 – Xe điện VF 9, thiếu dữ kiện CKD/CBU

Tôi cần nhập khẩu xe VinFast VF 9, loại SUV 7 chỗ, sử dụng hoàn toàn động cơ điện, dẫn động AWD, công suất 300 kW, pin lithium-ion 123 kWh. Xe dùng để chở người, không phải xe tải hay xe buýt. Mã HS 8 chữ số chính xác là bao nhiêu?



Kỳ vọng: Nhận diện `8703.80` nhưng phải làm rõ dạng nhập khẩu CBU/CKD, không tự giả định CBU để kết luận mã 8 chữ số.

### Test 02 – Hybrid và Plug-in Hybrid khác nhau một thuộc tính

Xe SUV 5 chỗ, động cơ xăng 1.998 cc kết hợp mô-tơ điện, pin lithium-ion 18 kWh. Cả động cơ xăng và mô-tơ điện đều có thể tham gia tạo lực kéo cho xe. Xe nhập khẩu nguyên chiếc. Hãy xác định mã HS và giải thích căn cứ pháp lý.



Kỳ vọng: Phải hỏi xe có khả năng sạc từ nguồn điện ngoài hay không.

- Không sạc ngoài: xem xét `8703.40`.
- Có sạc ngoài: xem xét `8703.60`.

Không được chỉ dựa vào dung lượng pin để xác định HEV hay PHEV.

### Test 03 – Xe điện có động cơ xăng chỉ để phát điện

Xe SUV 5 chỗ sử dụng mô-tơ điện làm nguồn lực kéo duy nhất. Xe có một động cơ xăng 1.498 cc nối với máy phát điện để sạc pin khi pin yếu; động cơ xăng không truyền lực cơ học trực tiếp đến bánh xe. Xe cũng có thể sạc từ nguồn điện bên ngoài. Đây là xe điện thuần túy hay xe hybrid theo HS? Đề xuất mã HS 8 chữ số.



Kỳ vọng: Phải phân tích cơ chế tạo động lực, không được kết luận `8703.80` chỉ vì bánh xe được dẫn động bằng mô-tơ điện. Đây là trường hợp cần đối chiếu kỹ chú giải và nguyên tắc phân loại xe điện có bộ mở rộng phạm vi hoạt động (range extender).

### Test 04 – Xe bán tải vừa chở người vừa chở hàng

Xe pickup cabin kép, 5 chỗ ngồi, động cơ diesel 1.996 cc, dẫn động 4WD, có khoang hành khách kín và thùng chở hàng riêng phía sau. Trọng tải hàng hóa thiết kế 950 kg. Xe được quảng cáo là phương tiện phục vụ gia đình và vận chuyển hàng hóa. Mã HS của xe thuộc nhóm 8703 hay 8704? Xác định mã 8 chữ số nếu đủ dữ kiện.



Kỳ vọng: Không được phân loại vào `8703` chỉ vì có 5 chỗ, cũng không tự động chọn `8704` chỉ vì có thùng hàng. Cần kiểm tra thiết kế chủ yếu để chở người hay hàng và các tiêu chí pháp lý liên quan.

### Test 05 – Xe ô tô đúng ngưỡng dung tích xi-lanh

Hai xe SUV diesel 7 chỗ, nhập khẩu nguyên chiếc, cùng kiểu thân xe và hệ dẫn động 4WD. Xe A có dung tích xi-lanh chính xác 2.500 cc; xe B có dung tích 2.501 cc. Hai xe có thuộc cùng phân nhóm HS 6 chữ số hay không? Hãy phân loại từng xe và giải thích ranh giới pháp lý.



Kỳ vọng: Phân biệt `8703.32` (trên 1.500 cc đến 2.500 cc) và `8703.33` (trên 2.500 cc). Đây là test kiểm tra xử lý chính xác ranh giới số học.

## II. Phần XVI – Máy móc, điện tử

Độ khó: Cao – Cực khó

### Test 06 – Máy tính xách tay đúng ngưỡng 10 kg

Hai máy tính xử lý dữ liệu tự động dạng xách tay, có CPU, bàn phím và màn hình tích hợp, chạy Windows, có pin và cùng công dụng. Máy A nặng chính xác 10,000 kg, máy B nặng 10,100 kg. Cả hai có được phân loại vào phân nhóm 8471.30 hay không? Xác định điều kiện pháp lý và hướng phân loại từng máy.



Kỳ vọng: Máy A đáp ứng điều kiện khối lượng không quá 10 kg; máy B không đáp ứng điều kiện đó. Không được tự động áp mã laptop `84713020` cho cả hai.

### Test 07 – Laptop tháo rời toàn bộ để vận chuyển

Một lô hàng gồm 100 bộ laptop hoàn chỉnh, mỗi bộ được đóng gói dưới dạng tháo rời: màn hình, mainboard có CPU và RAM, bàn phím, SSD, pin, vỏ máy và ốc vít. Tất cả các bộ phận cần thiết đều được nhập cùng một lô, chưa lắp ráp. Hàng không có linh kiện dự phòng. Có thể phân loại toàn bộ mỗi bộ theo mã HS của laptop nguyên chiếc 84713020 hay phải phân loại từng linh kiện riêng biệt? Áp dụng GIR nào?



Kỳ vọng: Phải xem xét GIR 2(a) về hàng chưa lắp ráp hoặc tháo rời và đặc trưng cơ bản của hàng hoàn chỉnh. Không được mặc định mọi lô linh kiện đều là laptop nguyên chiếc; điều kiện nhập khẩu và tính đầy đủ của bộ hàng vẫn phải được đối chiếu.

### Test 08 – Máy tính bảng có SIM 5G và chức năng gọi điện

Thiết bị màn hình cảm ứng 11 inch, chạy Android, có CPU 8 nhân, RAM 12GB, SSD 256GB, Wi-Fi, Bluetooth, SIM 5G, có thể thực hiện cuộc gọi thoại qua mạng di động, nhắn tin và cài đặt ứng dụng. Thiết bị không có bàn phím vật lý tích hợp, được nhà sản xuất bán dưới tên Tablet Pro 5G. Hàng nên thuộc nhóm 8471 hay 8517? Có đủ điều kiện để xem là smartphone 85171300 không?



Kỳ vọng: Không được chọn `85171300` chỉ vì có SIM và Android, cũng không loại trừ nhóm `8471` chỉ vì thiếu bàn phím vật lý. Phải phân tích đặc tính kỹ thuật, công năng và chú giải liên quan.

### Test 09 – Pin ô tô điện nhập riêng

Doanh nghiệp nhập khẩu riêng bộ pin lithium-ion 123 kWh dành cho xe điện VinFast VF 9. Bộ pin có các module cell, hệ thống quản lý pin BMS, vỏ bảo vệ và hệ thống làm mát tích hợp. Không nhập kèm thân xe, mô-tơ hoặc hệ truyền động. Hàng được khai là "phụ tùng ô tô điện". Nên phân loại theo 8507 hay 8708? Hãy xác định mã HS phù hợp dựa trên bản chất hàng hóa và chú giải pháp lý.



Kỳ vọng: Ưu tiên xem xét nhóm `8507`, phân nhóm `8507.60` cho bộ ắc quy lithium-ion. Không được mặc định là `8708` chỉ vì pin được sản xuất riêng cho VF 9. Mã 8 chữ số phải đối chiếu tiếp các nhánh chi tiết.

[image](https://www.google.com/s2/favicons?domain=https://vbpl.moj.gov.vn\&sz=32)

VBPL

+1



## III. Phần XIV – Đá quý, kim loại quý

Độ khó: Cực khó

### Test 10 – Kim cương tự nhiên và kim cương nuôi cấy

Hai viên kim cương có cùng trọng lượng 2 carat, cùng độ tinh khiết VS1, cùng kiểu cắt brilliant và chưa được gắn vào trang sức. Viên A hình thành tự nhiên trong lòng đất; viên B được sản xuất trong phòng thí nghiệm bằng công nghệ CVD. Cả hai đều có cấu trúc tinh thể carbon và độ cứng tương đương. Chúng có được phân loại chung mã HS không? Xác định nhóm và mã chi tiết nếu đủ thông tin.



Kỳ vọng: Kim cương tự nhiên cần xem xét nhóm `7102`, còn kim cương tổng hợp nhóm `7104`. Không được dựa vào độ cứng, chất lượng hoặc giá trị thương mại để gộp hai loại.

### Test 11 – Trang sức vàng thật và trang sức mạ vàng

Hai chiếc nhẫn có thiết kế giống hệt nhau, cùng được quảng cáo là "nhẫn vàng 18K". Nhẫn A có thân nhẫn bằng hợp kim vàng 18K (75% vàng theo khối lượng). Nhẫn B có thân bằng thép không gỉ, phủ một lớp vàng 18K dày 2 micromet bằng phương pháp mạ điện. Cả hai đều không gắn đá quý. Hai sản phẩm có thuộc cùng nhóm HS 7113 không? Hãy phân tích và đề xuất hướng phân loại chính xác.



Kỳ vọng: Phân biệt trang sức bằng kim loại quý thuộc nhóm `7113` và đồ trang sức giả thuộc nhóm `7117` trong điều kiện mô tả trên. Không được dựa vào chữ "vàng 18K" trong tên thương mại.

### Test 12 – Bạc 925 mạ vàng 18K và thép mạ vàng

Hai chiếc dây chuyền được phủ vàng 18K bên ngoài và có màu sắc giống hệt nhau. Dây chuyền A được chế tác từ bạc Sterling 925, sau đó mạ vàng 18K. Dây chuyền B được chế tác từ thép không gỉ, sau đó mạ vàng 18K. Cả hai không đính đá và dùng làm trang sức đeo cổ. Hãy xác định nhóm HS của từng sản phẩm và giải thích vai trò của kim loại nền.



Kỳ vọng: Dây A cần xem xét nhóm `7113`; dây B cần xem xét nhóm `7117`. Test này kiểm tra việc phân biệt kim loại quý thật với kim loại cơ bản được mạ điện.

### Test 13 – Đá sapphire tự nhiên và tổng hợp đã cắt giác

Hai viên sapphire màu xanh, mỗi viên 5 carat, đều đã cắt giác hoàn thiện, đánh bóng và chưa gắn vào trang sức. Viên A được khai thác tự nhiên và có giấy kiểm định đá quý. Viên B là sapphire tổng hợp được tạo bằng phương pháp Verneuil, có thành phần hóa học tương tự. Hãy xác định nhóm HS của từng viên, phân tích yếu tố nguồn gốc và trạng thái gia công.



Kỳ vọng: Phân biệt nhóm `7103` (đá quý tự nhiên phù hợp mô tả) và `7104` (đá quý tổng hợp). Cần đi tiếp xuống mã 8 chữ số khi dữ liệu và chú giải cho phép.

[image](https://www.google.com/s2/favicons?domain=https://vbpl.moj.gov.vn\&sz=32)

VBPL

+2



## IV. Test nâng cao – Kiểm tra suy luận và trạng thái hội thoại

Độ khó: Cực khó

### Test 14 – Drone gắn camera: Thiết bị bay hay máy quay?

Một thiết bị bay không người lái có 4 động cơ điện, tích hợp camera 4K, GPS, cảm biến tránh vật cản và bộ điều khiển từ xa. Thiết bị chủ yếu dùng để quay phim trên không, có thể bay và điều hướng độc lập. Hãy xác định thiết bị thuộc nhóm 8806 hay 8525. Những thông số nào cần thiết để phân loại đến mã HS 8 chữ số?



Kỳ vọng: Xem xét nhóm `8806` dành cho phương tiện bay không người lái. Không được mặc định phân loại thành camera `8525` vì mục đích sử dụng là quay phim. Phải xem xét các thông số phân nhóm, đặc biệt là trọng lượng cất cánh tối đa và cấu hình thiết bị.

[image](https://www.google.com/s2/favicons?domain=https://vbpl.moj.gov.vn\&sz=32)

VBPL

+1



### Test 15 – Người dùng thay đổi dữ kiện đã cung cấp

Test này cần nhập tuần tự cả 3 lượt trong cùng một phiên hội thoại.

Lượt 1

Tôi nhập khẩu xe điện VinFast VF 9 SUV 7 chỗ, động cơ thuần điện, xe nguyên chiếc CBU. Hãy đề xuất mã HS.



Lượt 2 – Đính chính

Tôi đính chính, xe không nhập nguyên chiếc CBU mà nhập dưới dạng bộ linh kiện CKD đầy đủ để lắp ráp thành xe hoàn chỉnh. Các thông số khác không thay đổi. Hãy phân loại lại.



Lượt 3 – Chuyển sản phẩm

Bây giờ tôi muốn phân loại một điện thoại iPhone 18 Pro Max nguyên chiếc. Mã HS là bao nhiêu?



Kỳ vọng:

- Lượt 1: Xem xét mã `87038098`.
- Lượt 2: Phải thay thế dữ kiện CBU bằng CKD, đánh giá lại theo GIR 2(a) và xem xét mã `87038018` nếu đáp ứng điều kiện nhánh CKD.
- Lượt 3: Tự nhận diện `NEW_QUERY`, xóa dữ kiện phân loại VF 9 khỏi truy vấn hiện tại và đề xuất `85171300` cho smartphone.



# HỎI LEGAL

Dưới đây là 5 câu hỏi LEGAL mức độ khó đến cực khó, được thiết kế riêng để kiểm thử hệ thống RAG pháp luật hải quan của bạn.

Bộ test tập trung vào Thông tư 85/2026/TT-BTC, Thông tư 31/2022/TT-BTC và các văn bản liên quan. Các tình huống bám theo quy định đã đối chiếu, nhưng khả năng hệ thống trả lời đầy đủ vẫn phụ thuộc vào tài liệu thực tế trong Corpus.

Mỗi câu hỏi có thể sao chép trực tiếp vào RAG. Phần kỳ vọng chỉ dùng để đánh giá, không đưa vào prompt.

## Test LEGAL 01 – Hiệu lực và thay thế văn bản

Cực khó · Temporal Legal Reasoning

Một doanh nghiệp nhập khẩu hàng hóa có hai tờ khai đăng ký vào ngày 14/09/2026 và 16/09/2026. Doanh nghiệp cho rằng cả hai tờ khai đều phải áp dụng Thông tư 85/2026/TT-BTC vì văn bản này đã được ban hành từ tháng 6/2026.

Hãy xác định văn bản điều chỉnh hoạt động phân loại hàng hóa tại từng thời điểm, phân biệt ngày ban hành với ngày có hiệu lực, xác định các thông tư bị thay thế và giải thích liệu Thông tư 31/2022/TT-BTC có tự động hết hiệu lực khi Thông tư 85/2026/TT-BTC bắt đầu có hiệu lực hay không.

Yêu cầu viện dẫn cụ thể điều, khoản và văn bản pháp luật làm căn cứ.



Kỳ vọng: Xử lý đúng hiệu lực theo thời gian, phân biệt văn bản quy định quy trình phân loại và văn bản ban hành Danh mục HS, không suy luận rằng hai thông tư thay thế nhau chỉ vì cùng liên quan đến mã HS.

## Test LEGAL 02 – Mâu thuẫn giữa các nguồn pháp lý

Cực khó · Legal Conflict Resolution

Giả sử khi phân loại một mặt hàng nhập khẩu, doanh nghiệp phát hiện ba vấn đề: mô tả hàng hóa trong Danh mục hàng hóa xuất khẩu, nhập khẩu Việt Nam khác với mô tả tương ứng trong Danh mục HS hoặc AHTN; mã số tại một Danh mục quản lý chuyên ngành khác với mã xác định theo Danh mục hàng hóa xuất khẩu, nhập khẩu Việt Nam; và sau khi áp dụng các quy tắc phân loại vẫn chưa xác định được một mã HS duy nhất.

Theo Thông tư 85/2026/TT-BTC, từng tình huống phải được xử lý như thế nào? Những tài liệu bổ trợ nào được sử dụng để phân loại, căn cứ pháp lý nào được ưu tiên trong từng trường hợp, và có được tự ý lựa chọn mã thuận lợi nhất về thuế hay không?

Hãy trình bày riêng từng tình huống, dẫn đúng điều, khoản và giải thích giới hạn áp dụng của mỗi quy định.



Kỳ vọng: Retrieval đúng Điều 4 và Điều 6 Thông tư 85, xử lý được nhiều tình huống trong cùng một câu hỏi mà không trộn lẫn quy tắc hoặc tự đặt ra thứ bậc pháp lý không có trong nguồn.

[image](https://www.google.com/s2/favicons?domain=https://thuvienphapluat.vn\&sz=32)

THƯ VIỆN PHÁP LUẬT



## Test LEGAL 03 – Máy móc nhập khẩu nhiều đợt, nhiều cửa khẩu

Cực khó · Multi-hop Legal Retrieval

Công ty A nhập khẩu một dây chuyền sản xuất tự động gồm nhiều máy móc và thiết bị điện thuộc Chương 84 và 85. Các thiết bị được mua từ ba nhà cung cấp, vận chuyển thành bốn chuyến hàng, làm thủ tục tại hai đơn vị hải quan khác nhau trong khoảng thời gian ba tháng. Một số máy được nhập dưới dạng tháo rời để thuận tiện vận chuyển.

Theo Thông tư 85/2026/TT-BTC, doanh nghiệp có thể lựa chọn phân loại từng máy riêng biệt hoặc phân loại theo tổ hợp máy không? Khi nào phải áp dụng GIR 2(a), Chú giải 3, 4, 5 Phần XVI và thủ tục đăng ký Danh mục máy móc, thiết bị?

Hãy xác định thành phần hồ sơ, thời điểm phải đăng ký, cơ quan tiếp nhận, cách thực hiện Phiếu theo dõi trừ lùi và trách nhiệm của cơ quan hải quan khi các chuyến hàng làm thủ tục tại những địa điểm khác nhau. Dẫn đầy đủ điều, khoản và văn bản được viện dẫn.



Kỳ vọng: Kết nối Điều 7, 8, 9 Thông tư 85 với GIR và Chú giải Phần XVI, giải thích đúng điều kiện áp dụng từng phương án, không mặc định hàng đi nhiều chuyến phải phân loại riêng lẻ.

[image](https://www.google.com/s2/favicons?domain=https://thuvienphapluat.vn\&sz=32)

THƯ VIỆN PHÁP LUẬT



## Test LEGAL 04 – Tranh chấp kết quả phân tích, phân loại

Cực khó · Procedural Legal Reasoning

Một doanh nghiệp nhập khẩu nguyên liệu sản xuất và bị cơ quan hải quan lấy mẫu phân tích để xác định mã HS. Sau khi nhận Thông báo kết quả phân tích, phân loại, doanh nghiệp không đồng ý với kết luận vì cho rằng kết quả không phản ánh đúng thành phần thực tế của hàng hóa.

Hãy phân tích trình tự pháp lý từ lúc lấy mẫu đến lúc ban hành Thông báo kết quả, bao gồm điều kiện lấy và niêm phong mẫu, thời hạn giải quyết trong trường hợp thông thường và trường hợp phức tạp, thời hạn lưu mẫu, khả năng yêu cầu giám định lại hoặc khiếu nại.

Nếu doanh nghiệp yêu cầu nhận lại mẫu trong thời hạn lưu mẫu, đã công nhận kết quả phân tích rồi sau đó lại muốn khiếu nại kết quả đó, hậu quả pháp lý là gì? Phân biệt rõ quyền khiếu nại thông thường với trường hợp đã nhận lại mẫu và công nhận kết quả. Dẫn căn cứ pháp lý cho từng kết luận.



Kỳ vọng: Truy xuất và phối hợp đúng Điều 10–12 Thông tư 85, không nhầm thời hạn phân tích với thời hạn lưu mẫu hoặc suy luận mọi trường hợp nhận lại mẫu đều mất quyền khiếu nại.

[image](https://www.google.com/s2/favicons?domain=https://thuvienphapluat.vn\&sz=32)

THƯ VIỆN PHÁP LUẬT



## Test LEGAL 05 – Phân biệt mã HS, thuế suất và chính sách quản lý

Cực khó · Cross-document Legal Reasoning

Một doanh nghiệp nhập khẩu điện thoại thông minh và đã xác định được mã HS 85171300 theo Danh mục hàng hóa xuất khẩu, nhập khẩu Việt Nam. Doanh nghiệp cho rằng chỉ cần có mã HS này là có thể kết luận ngay mức thuế nhập khẩu, thuế giá trị gia tăng và toàn bộ nghĩa vụ kiểm tra chuyên ngành, không cần đối chiếu thêm bất kỳ văn bản pháp luật nào.

Nhận định trên đúng hay sai? Hãy phân biệt rõ giá trị pháp lý của Danh mục mã HS, Biểu thuế xuất khẩu, nhập khẩu và các Danh mục quản lý chuyên ngành. Giải thích vì sao một mã HS được xác định đúng chưa đủ để kết luận mức thuế phải nộp hoặc nghĩa vụ quản lý chuyên ngành.

Nếu chưa có thông tin về xuất xứ, thời điểm đăng ký tờ khai và điều kiện hưởng thuế suất ưu đãi, hệ thống có được đưa ra một mức thuế chính xác hay không? Hãy dẫn điều, khoản và văn bản pháp luật làm căn cứ; trường hợp Corpus chưa chứa văn bản thuế liên quan, phải chỉ rõ giới hạn của kết luận.



Kỳ vọng: Phân biệt chính xác chức năng của mã HS với việc áp dụng thuế và chính sách quản lý, truy xuất Điều 5 Thông tư 85 cùng văn bản liên quan. Không tự bịa thuế suất hoặc nghĩa vụ pháp lý khi thiếu căn cứ.

[image](https://www.google.com/s2/favicons?domain=https://thuvienphapluat.vn\&sz=32)

THƯ VIỆN PHÁP LUẬT
