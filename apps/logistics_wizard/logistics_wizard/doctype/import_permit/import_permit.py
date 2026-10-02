# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today
from frappe.model.document import Document

class ImportPermit(Document):
    def validate(self):
        validate_import_permit(self)

def validate_import_permit(doc, method=None):
    """Kiểm tra thời hạn hiệu lực của giấy phép chuyên ngành"""
    check_expiry_status(doc)


def check_expiry_status(doc):
    """Tự động cảnh báo giấy phép chuyên ngành đã hết hạn"""
    if doc.valid_until and getdate(doc.valid_until) < getdate(today()):
        if doc.status == "Granted":
            doc.status = "Expired"
