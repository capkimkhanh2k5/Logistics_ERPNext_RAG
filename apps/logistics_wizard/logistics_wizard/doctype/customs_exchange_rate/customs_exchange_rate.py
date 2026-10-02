# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document

class CustomsExchangeRate(Document):
    def validate(self):
        validate_customs_exchange_rate(self)

def validate_customs_exchange_rate(doc, method=None):
    """Kiểm tra tính hợp lệ của tỷ giá hải quan theo tuần"""
    if (doc.exchange_rate or 0) <= 0:
        frappe.throw(_("Tỷ giá hải quan phải lớn hơn 0."), title=_("Tỷ giá không hợp lệ"))

    if getdate(doc.valid_from) > getdate(doc.valid_to):
        frappe.throw(
            _("Ngày bắt đầu hiệu lực ({0}) không được lớn hơn ngày kết thúc ({1}).").format(
                doc.valid_from, doc.valid_to
            ),
            title=_("Khoảng thời gian không hợp lệ")
        )

    # Kiểm tra trùng lặp khoảng thời gian hiệu lực cho cùng một đồng tiền
    overlapping = frappe.db.sql("""
        SELECT name, valid_from, valid_to 
        FROM `tabCustoms Exchange Rate`
        WHERE currency = %(currency)s
          AND name != %(name)s
          AND (
              (valid_from <= %(valid_from)s AND valid_to >= %(valid_from)s)
              OR (valid_from <= %(valid_to)s AND valid_to >= %(valid_to)s)
              OR (valid_from >= %(valid_from)s AND valid_to <= %(valid_to)s)
          )
    """, {
        "currency": doc.currency,
        "name": doc.name or f"{doc.currency}-{doc.valid_from}",
        "valid_from": doc.valid_from,
        "valid_to": doc.valid_to
    }, as_dict=True)

    if overlapping:
        conflict = overlapping[0]
        frappe.throw(
            _("Khoảng thời gian ({0} đến {1}) của đồng {2} bị chồng lấn với bản ghi '{3}' ({4} đến {5}).").format(
                doc.valid_from, doc.valid_to, doc.currency, conflict.name, conflict.valid_from, conflict.valid_to
            ),
            title=_("Xung đột Khoảng thời gian Hiệu lực")
        )

@frappe.whitelist()
def get_customs_rate(currency, date=None):
    """Lấy tỷ giá hải quan có hiệu lực tại ngày khai báo (mặc định hôm nay)"""
    if not date:
        date = frappe.utils.today()

    rate = frappe.db.sql("""
        SELECT exchange_rate 
        FROM `tabCustoms Exchange Rate`
        WHERE currency = %(currency)s
          AND valid_from <= %(date)s
          AND valid_to >= %(date)s
        ORDER BY valid_from DESC
        LIMIT 1
    """, {"currency": currency, "date": date})

    if rate:
        return rate[0][0]
    return None
