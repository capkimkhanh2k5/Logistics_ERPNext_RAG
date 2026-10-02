# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import re
import frappe
from frappe import _
from frappe.model.document import Document

class HSTariffRate(Document):
    def validate(self):
        validate_hs_tariff_rate(self)

def validate_hs_tariff_rate(doc, method=None):
    """Kiểm tra tính hợp lệ của mã HS, thuế suất và các hiệp định FTA"""
    # 1. Kiểm tra mã HS phải có từ 8 đến 10 chữ số
    raw_digits = re.sub(r"[^0-9]", "", doc.hs_code or "")
    if len(raw_digits) < 8 or len(raw_digits) > 10:
        frappe.throw(
            _("Mã HS không hợp lệ: '{0}'. Biểu thuế Hải quan Việt Nam quy định mã HS phân nhóm cấp độ 8 hoặc 10 chữ số.").format(doc.hs_code),
            title=_("Lỗi Định dạng Mã HS")
        )

    # 2. Thuế suất phải nằm trong khoảng từ 0% đến 100%
    for field, label in [
        ("general_duty_rate", "Thuế suất Thông thường"),
        ("mfn_duty_rate", "Thuế suất MFN"),
        ("vat_rate", "Thuế suất GTGT")
    ]:
        val = doc.get(field) or 0
        if val < 0 or val > 100:
            frappe.throw(_("{0} phải nằm trong khoảng từ 0% đến 100% (Hiện tại: {1}%).").format(label, val))

    # 3. Nếu yêu cầu giấy phép / KCS chuyên ngành, bắt buộc phải chọn Bộ quản lý
    if doc.requires_import_permit and not doc.managing_ministry:
        frappe.throw(
            _("Hàng hóa có cờ 'Yêu cầu Giấy phép' bắt buộc phải chọn 'Bộ / Cơ quan quản lý chuyên ngành'."),
            title=_("Thiếu Thông tin Pháp lý")
        )

    # 4. Không cho phép trùng lặp Hiệp định FTA trong bảng ưu đãi
    seen_agreements = set()
    for row in doc.get("preferential_rates", []):
        if row.trade_agreement in seen_agreements:
            frappe.throw(
                _("Hiệp định '{0}' bị khai báo trùng lặp trong bảng Thuế suất Ưu đãi FTA.").format(row.trade_agreement),
                title=_("Trùng lặp Hiệp định")
            )
        seen_agreements.add(row.trade_agreement)
        if (row.preferential_duty_rate or 0) < 0 or (row.preferential_duty_rate or 0) > 100:
            frappe.throw(_("Thuế suất ưu đãi của hiệp định {0} phải từ 0% đến 100%.").format(row.trade_agreement))
