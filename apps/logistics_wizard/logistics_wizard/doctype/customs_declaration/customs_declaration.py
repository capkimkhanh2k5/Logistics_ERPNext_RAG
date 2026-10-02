# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today
from frappe.model.document import Document

class CustomsDeclaration(Document):
    def validate(self):
        validate_customs_declaration(self)

    def on_update(self):
        on_update_customs_declaration(self)

def validate_customs_declaration(doc, method=None):
    """Xử lý tính thuế và kiểm tra mã VNACCS"""
    validate_vnaccs_number(doc)
    fetch_customs_exchange_rate(doc)
    calculate_customs_taxes(doc)

def on_update_customs_declaration(doc, method=None):
    """Đồng bộ trạng thái thông quan sang Shipment"""
    sync_with_shipment(doc)


def validate_vnaccs_number(doc):
    """Xác thực số tờ khai hải quan điện tử VNACCS/VCIS (chuẩn 11 chữ số)"""
    if doc.declaration_no:
        clean_no = doc.declaration_no.strip()
        if not (clean_no.isdigit() and len(clean_no) == 11):
            frappe.throw(
                _("Số tờ khai VNACCS/VCIS không hợp lệ: '{0}'. Số tờ khai chuẩn quốc gia phải bao gồm đúng 11 chữ số.").format(clean_no),
                title=_("Sai Quy chuẩn Tờ khai VNACCS")
            )
        doc.declaration_no = clean_no

def fetch_customs_exchange_rate(doc):
    """Tự động tra cứu Tỷ giá tính thuế Hải quan theo tuần của Bộ Tài chính"""
    if not doc.declaration_date or not doc.currency:
        return

    rates = frappe.get_all(
        "Customs Exchange Rate",
        filters={
            "currency": doc.currency,
            "valid_from": ["<=", doc.declaration_date]
        },
        fields=["exchange_rate", "valid_from", "valid_to"],
        order_by="valid_from desc",
        limit=1
    )

    if rates:
        doc.customs_exchange_rate = flt(rates[0].exchange_rate)
    elif not doc.customs_exchange_rate:
        doc.customs_exchange_rate = 25400.0

def calculate_customs_taxes(doc):
    """Tính toán trị giá tính thuế, thuế nhập khẩu và thuế GTGT theo luật Hải quan Việt Nam"""
    fx = flt(doc.customs_exchange_rate) or 1.0
    tot_val = 0.0
    tot_duty = 0.0
    tot_vat = 0.0

    for item in doc.get("items", []):
        q = flt(item.qty)
        p = flt(item.unit_price)
        if not item.customs_value_cur and q and p:
            item.customs_value_cur = round(q * p, 2)

        item.customs_value_vnd = round(flt(item.customs_value_cur) * fx, 2)
        item.import_duty_amount = round(item.customs_value_vnd * (flt(item.import_duty_rate) / 100.0), 2)
        
        # Căn cứ tính thuế GTGT = Trị giá tính thuế + Thuế nhập khẩu
        vat_base = item.customs_value_vnd + item.import_duty_amount
        item.vat_amount = round(vat_base * (flt(item.vat_rate) / 100.0), 2)
        item.total_tax = round(item.import_duty_amount + item.vat_amount, 2)

        tot_val += item.customs_value_vnd
        tot_duty += item.import_duty_amount
        tot_vat += item.vat_amount

    doc.total_customs_value_vnd = round(tot_val, 2)
    doc.total_import_duty_vnd = round(tot_duty, 2)
    doc.total_vat_vnd = round(tot_vat, 2)
    doc.total_tax_vnd = round(tot_duty + tot_vat, 2)

def sync_with_shipment(doc):
    """Đồng bộ trạng thái thông quan và mã tờ khai sang chuyến hàng Trade Shipment"""
    if not doc.trade_shipment or not frappe.db.exists("Trade Shipment", doc.trade_shipment):
        return

    shipment = frappe.get_doc("Trade Shipment", doc.trade_shipment)
    dirty = False

    if doc.declaration_no and shipment.customs_declaration_no != doc.declaration_no:
        shipment.customs_declaration_no = doc.declaration_no
        dirty = True

    # Cập nhật mốc đăng ký hải quan M06
    if doc.clearance_status in ("Registered", "Inspected", "Tax Paid", "Cleared"):
        for m in shipment.get("milestones", []):
            if m.milestone_code == "M06_CUSTOMS_REG" and m.status != "Completed":
                m.actual_date = doc.declaration_date or today()
                m.status = "Completed"
                m.variance_days = 0
                dirty = True

    # Cập nhật mốc thông quan hoàn tất M07
    if doc.clearance_status == "Cleared":
        for m in shipment.get("milestones", []):
            if m.milestone_code == "M07_CUSTOMS_CLEAR" and m.status != "Completed":
                m.actual_date = doc.clearance_date or today()
                m.status = "Completed"
                m.variance_days = 0
                dirty = True
        if shipment.status == "Customs Clearance":
            shipment.status = "Completed"
            dirty = True

    if dirty:
        shipment.save(ignore_permissions=True)
