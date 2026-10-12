# Mã hỗ trợ kiểm thử và đánh giá offline

| File | Vai trò |
|---|---|
| [evaluation.py](evaluation.py) | Nạp gold Dev/Test, tạo query đánh giá, chấm metrics và quét trọng số. |
| [experiments.py](experiments.py) | Gom nhóm các câu cùng họ và tạo manifest/fold cho thực nghiệm. |
| [generation_eval.py](generation_eval.py) | Chọn mẫu, cache retrieval và chấm generation với gold dùng sau khi trả lời. |
| [generation_scenarios.py](generation_scenarios.py) | Các tình huống và runner cho notebook 03, gồm các lượt bổ sung, kỳ vọng và lỗi nguồn/API giả lập. |

Notebook và các CLI trong `scripts/` import những helper này. Pytest tests nằm ở `tests/test_*.py`; helper trong thư mục này không tự gọi API hoặc chạy benchmark khi được import. Runtime `rag/` chỉ xử lý corpus, embedding, retrieval, context và generation, không import `tests/`.

Cấu hình runtime và các cờ chạy notebook nằm trong [config/](../../config/README.md). Kết quả generation lưu tại `artifacts/generation/`; kết quả retrieval/experiment giữ nguyên vị trí hiện tại.
