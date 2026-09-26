# HS Index Audit Report

## Kết luận

- WCO index được kiểm tra đủ **21 Phần / 97 Chương**.
- Chapter code **01–97 liên tục, không thiếu Chapter**.
- Phân cấp Section → Chapter được giữ nguyên theo WCO HS 2022.
- Tên tiếng Việt **không dịch bằng LLM**; dùng wording của Danh mục Việt Nam theo TT31/2022/TT-BTC.
- Chỉ **Chương 84 và 85** được đánh dấu `IN_SCOPE`.
- File cuối giữ song song `name_vi` và `name_en` để audit.

## Các lỗi của index cũ đã phát hiện/sửa

### Chapter 15 — wco_ref
- Cũ: `0315-2022E`
- Mới: `0315-02022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 28 — chapter_name_en
- Cũ: `Inorganic chemicals; organic or inorganic compounds of precious metals, of rare- earth metals, of radioactive elements or of isotopes.`
- Mới: `Inorganic chemicals; organic or inorganic compounds of precious metals, of rare-earth metals, of radioactive elements or of isotopes.`
- Lý do: Spacing/hyphen extraction artifact corrected against WCO PDF.

### Chapter 44 — wco_ref
- Cũ: `0944-2022E`
- Mới: `0844-2022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 45 — wco_ref
- Cũ: `0945-2022E`
- Mới: `0845-2022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 46 — wco_ref
- Cũ: `0946-2022E`
- Mới: `0846-2022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 47 — wco_ref
- Cũ: `1047-2022E`
- Mới: `0847-2022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 48 — wco_ref
- Cũ: `1048-2022E`
- Mới: `0848-2022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 49 — wco_ref
- Cũ: `1049-2022E`
- Mới: `0849-2022E`
- Lý do: Corrected to the reference displayed in the uploaded WCO HS 2022 PDF.

### Chapter 86 — chapter_name_en
- Cũ: `Railway or tramway locomotives, rolling-stock and parts thereof; railway or tramway track fixtures and fittings and parts thereof; mechanical (including electro- mechanical) traffic signalling equipment of all kinds.`
- Mới: `Railway or tramway locomotives, rolling-stock and parts thereof; railway or tramway track fixtures and fittings and parts thereof; mechanical (including electro-mechanical) traffic signalling equipment of all kinds.`
- Lý do: Spacing/hyphen extraction artifact corrected against WCO PDF.

## Kiểm soát Chapter 85

Text layer của PDF WCO làm vỡ mô tả Chapter 85 giữa trang 3 và trang 4. Bản cuối sử dụng tiêu đề đầy đủ đã đối chiếu trực quan trên PDF.

## Cách dùng cho RAG

Index này nên ưu tiên làm **Scope Router / metadata lookup**, không phải corpus pháp lý chính.

```text
Product query
  ↓
Vietnamese scope lookup
  ↓
Chapter 84 / 85 ?
  ├─ Yes → RAG Section XVI
  └─ No  → OUT_OF_SCOPE
```

Nếu semantic search được dùng trên index, query field đề xuất là `search_text_vi`.