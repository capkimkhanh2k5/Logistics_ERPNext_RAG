# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class ChargeType(Document):
    def validate(self):
        validate_charge_type(self)

def validate_charge_type(doc, method=None):
    """Kiểm tra hợp lệ loại phí theo quy định kế toán và logistics"""
    # 1. Nếu tính vào giá vốn, bắt buộc phải chọn tiêu chí phân bổ
    if doc.include_in_valuation and doc.allocation_criterion == "Không phân bổ (None / Expense)":
        frappe.throw(
            _("Chi phí được tính vào giá vốn hàng tồn kho bắt buộc phải chọn Tiêu chí phân bổ (Theo CBM, Theo Gross Weight hoặc Theo Giá trị hàng)."),
            title=_("Quy định Phân bổ Chi phí")
        )

    # 2. Phí phạt lưu cont/bãi không được vốn hóa vào hàng tồn kho (VAS 02 / IAS 2)
    if "Phí phạt" in (doc.cost_category or "") and doc.include_in_valuation:
        frappe.throw(
            _("Theo chuẩn mực kế toán (VAS 02 / IAS 2), chi phí phạt lưu bãi/lưu vỏ cont quá hạn (Demurrage/Detention) là tổn thất do chậm trễ, không được vốn hóa vào giá trị hàng tồn kho. Vui lòng bỏ tích chọn 'Tính vào giá vốn hàng tồn kho'."),
            title=_("Vi phạm Chuẩn mực Kế toán")
        )
