# CLIProxyAPI trong stack aiagent-rag

CLIProxyAPI chạy thành service `cliproxyapi` cùng Compose project `aiagent-rag`.
Image nền chính thức được khóa ở `eceasy/cli-proxy-api:v8.0.29`; Dockerfile chỉ
thêm `curl` để healthcheck `/healthz`. Service không phụ thuộc PostgreSQL.

Từ thư mục `frappe-bench/apps/aiAgent`:

```bash
python3 scripts/init_cliproxyapi.py
docker compose -f docker-compose.rag.yml config --quiet
docker compose -f docker-compose.rag.yml up -d --build --no-deps cliproxyapi
```

Script tạo `local/config.yaml` và `local/credentials.env` với quyền `600` trong
thư mục `700`. Chạy lại giữ nguyên các file và key. Thư mục `local/` được
gitignore và loại khỏi build context; không đưa key thật vào template.

## Mở giao diện và kết nối tài khoản

1. Mở <http://localhost:8317/management.html>.
2. Dùng giá trị `MANAGEMENT_PASSWORD` trong `local/credentials.env` để đăng nhập.
3. Vào **Auth files & OAuth / OAuth**, chọn **Antigravity**, rồi hoàn tất đăng nhập
   Google trên trình duyệt. Hoặc thêm Gemini API key trong trang **AI providers**.
4. Xem model và quota sau khi tài khoản được kết nối.

Nếu muốn đăng nhập Antigravity bằng CLI:

```bash
docker compose -f docker-compose.rag.yml exec cliproxyapi \
  /CLIProxyAPI/CLIProxyAPI -config /CLIProxyAPI/config/config.yaml \
  -no-browser -antigravity-login
```

Host chỉ mở cổng `8317` và callback Antigravity `51121` qua `127.0.0.1`.
`management.allow-remote: true` cho phép request đi qua Docker bridge; API quản trị
vẫn yêu cầu management password. Có thể đổi riêng cổng web/API bằng
`CLIPROXYAPI_PORT` trong `.env`; cổng nội bộ vẫn là `8317`.

## Kết nối ứng dụng

- Ứng dụng trên máy host: base URL `http://127.0.0.1:8317/v1`.
- Container trong stack: base URL `http://cliproxyapi:8317/v1`.
- Client API key: lấy trong **Configuration / Client keys** trên Web UI; key ban đầu
  cũng được ghi ở `CLIPROXYAPI_CLIENT_API_KEY` trong `local/credentials.env`.
- Management password chỉ dùng quản trị; không dùng thay client API key.

`routing.session-affinity: true` ưu tiên giữ credential cho cùng session khi có
session identity. Thiết lập này không lưu lịch sử hội thoại thay cho ứng dụng.
Terminal RAG và notebook 03 thử Gemini, rồi GPT-OSS 120B qua CLIProxyAPI; chỉ dùng
Groq sau khi cả hai model CLI lỗi hoặc hết quota. `CLIProxyConfig` tự đọc client key ban đầu từ file local
này; nếu đổi key qua UI thì cập nhật `CLIPROXYAPI_API_KEY` trong `.env`. Các thiết
lập `CLIPROXYAPI_*` và chính sách fallback được mô tả trong [cấu hình RAG](../README.md).
Phần này chưa triển khai bộ nhớ chat mới hoặc import tài khoản từ 9router.

GPT-OSS qua Antigravity trên phiên bản `v8.0.29` trả HTTP 400 khi dùng
`response_format: json_schema` hoặc `json_object`. Client RAG gửi schema trong
system prompt riêng cho các model `gpt-oss-*`, rồi kiểm tra JSON/schema, trích dẫn
và ranh giới chứng cứ bằng cùng validator và tối đa một lượt sửa như trước.
Gemini vẫn dùng `response_format: json_schema`. Đây là tương thích định dạng;
không bỏ bước kiểm tra kết quả của RAG.

## Vận hành

```bash
docker compose -f docker-compose.rag.yml ps
docker compose -f docker-compose.rag.yml logs --tail=100 cliproxyapi
docker compose -f docker-compose.rag.yml restart cliproxyapi
docker compose -f docker-compose.rag.yml stop cliproxyapi
```

Web UI và backend dùng cùng phiên bản cấu hình v8. `local/config.yaml` được mount
cả thư mục có quyền ghi để Web UI có thể lưu cấu hình. Sửa template không tự đổi
cấu hình local đã tạo. Nếu đổi `credentials.env`, chạy lại `up -d --no-deps
cliproxyapi` để Docker nạp lại biến môi trường.

OAuth credentials, log, Web UI tải về và plugins nằm trong các named volumes riêng
`aiagent-rag_cliproxyapi-*`, được giữ khi recreate/restart container. Log ứng dụng
bị giới hạn 100 MB; full request logging mặc định tắt. Để gỡ riêng dịch vụ, dùng
`stop cliproxyapi` rồi `rm -f cliproxyapi`. Tránh `down -v` vì lệnh đó xóa cả volume
PostgreSQL của stack. Sao lưu `local/` và volume auth trước khi chuyển máy.

Nguồn: [Docker Compose chính thức](https://help.router-for.me/docker/docker-compose),
[Web UI](https://github.com/router-for-me/Cli-Proxy-API-Management-Center),
[release v8.0.29](https://github.com/router-for-me/CLIProxyAPI/releases/tag/v8.0.29).
