# GIR Final Cleaning Report

## Trạng thái

**READY_FOR_RAG**

## Kết quả xử lý

- Core GIR rule/subrule: **11 chunks**
- Chú giải ban đầu: **114 chunks**
- Chú giải sau khi nối boundary: **104 chunks**
- Tổng dataset combined: **115 chunks**
- Lỗi chữ/dấu đã sửa theo PDF: **9 chunks**
- Continuation do ngắt trang đã bổ sung: **1 chunk**
- Nhóm boundary/context đã nối: **8 groups / 18 raw chunks**

## Nguyên tắc chỉnh sửa

Chỉ thực hiện ba loại thay đổi:

1. Sửa lỗi ký tự/dấu đã xác nhận trực quan trên PDF.
2. Ghép phần tiếp nối bị cắt bởi ngắt trang.
3. Nối các chunk cùng một câu/đoạn bị tách do layout trang.

Không:
- dịch lại nội dung;
- diễn giải lại văn bản;
- thay đổi thuật ngữ pháp lý;
- tự bổ sung kiến thức ngoài nguồn.

## File dùng cho hệ thống

### `GIR_1_6_CORE_VI_FINAL.jsonl`
Core GIR để Rule Engine / retrieval ưu tiên P0.

### `GIR_EXPLANATORY_VI_CLEAN.jsonl`
Chú giải GIR đã làm sạch, dùng cho RAG giải thích và reasoning.

### `GIR_RAG_VI_COMBINED.jsonl`
File combined có thể ingest trực tiếp:
- `GIR_CORE` → P0
- `GIR_EXPLANATORY` → P1

## Khuyến nghị

Nếu kiến trúc hỗ trợ nhiều namespace, ưu tiên tách:
- `gir_rules` ← Core
- `gir_explanatory` ← Chú giải

Nếu muốn ingest nhanh một collection duy nhất, dùng `GIR_RAG_VI_COMBINED.jsonl` và filter/rerank theo `dataset_layer` + `retrieval_priority`.
