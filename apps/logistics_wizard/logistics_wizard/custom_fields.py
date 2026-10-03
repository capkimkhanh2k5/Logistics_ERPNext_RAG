# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
    "Item": [
        {
            "fieldname": "custom_hs_code",
            "label": "Mã HS Biểu thuế XNK",
            "fieldtype": "Link",
            "options": "HS Tariff Rate",
            "insert_after": "item_name",
        },
        {
            "fieldname": "unit_cbm",
            "label": "Thể tích đơn vị (CBM)",
            "fieldtype": "Float",
            "precision": "4",
            "insert_after": "custom_hs_code",
        },
        {
            "fieldname": "unit_gross_weight",
            "label": "Trọng lượng gộp đơn vị (KGS)",
            "fieldtype": "Float",
            "precision": "4",
            "insert_after": "unit_cbm",
        },
        {
            "fieldname": "technical_description",
            "label": "Mô tả công dụng kỹ thuật chuyên ngành",
            "fieldtype": "Small Text",
            "insert_after": "unit_gross_weight",
        }
    ],
    "Purchase Order": [
        {
            "fieldname": "trade_case",
            "label": "Hồ sơ Thương mại (Trade Case)",
            "fieldtype": "Link",
            "options": "Trade Case",
            "insert_after": "supplier",
        },
        {
            "fieldname": "trade_shipment",
            "label": "Chuyến tàu / Vận đơn (Trade Shipment)",
            "fieldtype": "Link",
            "options": "Trade Shipment",
            "insert_after": "trade_case",
        }
    ],
    "Purchase Order Item": [
        {
            "fieldname": "custom_hs_code",
            "label": "Mã HS",
            "fieldtype": "Link",
            "options": "HS Tariff Rate",
            "fetch_from": "item_code.custom_hs_code",
            "insert_after": "item_code",
        },
        {
            "fieldname": "unit_cbm",
            "label": "CBM/Đơn vị",
            "fieldtype": "Float",
            "precision": "4",
            "fetch_from": "item_code.unit_cbm",
            "insert_after": "custom_hs_code",
        },
        {
            "fieldname": "unit_gross_weight",
            "label": "KGS/Đơn vị",
            "fieldtype": "Float",
            "precision": "4",
            "fetch_from": "item_code.unit_gross_weight",
            "insert_after": "unit_cbm",
        },
        {
            "fieldname": "total_cbm",
            "label": "Tổng CBM",
            "fieldtype": "Float",
            "precision": "4",
            "read_only": 1,
            "insert_after": "unit_gross_weight",
        },
        {
            "fieldname": "total_gross_weight",
            "label": "Tổng Gross Weight (KGS)",
            "fieldtype": "Float",
            "precision": "4",
            "read_only": 1,
            "insert_after": "total_cbm",
        }
    ],
    "Purchase Receipt": [
        {
            "fieldname": "trade_case",
            "label": "Hồ sơ Thương mại (Trade Case)",
            "fieldtype": "Link",
            "options": "Trade Case",
            "insert_after": "supplier",
        },
        {
            "fieldname": "trade_shipment",
            "label": "Chuyến tàu / Vận đơn (Trade Shipment)",
            "fieldtype": "Link",
            "options": "Trade Shipment",
            "insert_after": "trade_case",
        }
    ],
    "Purchase Receipt Item": [
        {
            "fieldname": "custom_hs_code",
            "label": "Mã HS",
            "fieldtype": "Link",
            "options": "HS Tariff Rate",
            "fetch_from": "item_code.custom_hs_code",
            "insert_after": "item_code",
        },
        {
            "fieldname": "unit_cbm",
            "label": "CBM/Đơn vị",
            "fieldtype": "Float",
            "precision": "4",
            "fetch_from": "item_code.unit_cbm",
            "insert_after": "custom_hs_code",
        },
        {
            "fieldname": "unit_gross_weight",
            "label": "KGS/Đơn vị",
            "fieldtype": "Float",
            "precision": "4",
            "fetch_from": "item_code.unit_gross_weight",
            "insert_after": "unit_cbm",
        },
        {
            "fieldname": "total_cbm",
            "label": "Tổng CBM",
            "fieldtype": "Float",
            "precision": "4",
            "read_only": 1,
            "insert_after": "unit_gross_weight",
        },
        {
            "fieldname": "total_gross_weight",
            "label": "Tổng Gross Weight (KGS)",
            "fieldtype": "Float",
            "precision": "4",
            "read_only": 1,
            "insert_after": "total_cbm",
        }
    ],
    "Purchase Invoice": [
        {
            "fieldname": "trade_case",
            "label": "Hồ sơ Thương mại (Trade Case)",
            "fieldtype": "Link",
            "options": "Trade Case",
            "insert_after": "supplier",
        },
        {
            "fieldname": "trade_shipment",
            "label": "Chuyến tàu / Vận đơn (Trade Shipment)",
            "fieldtype": "Link",
            "options": "Trade Shipment",
            "insert_after": "trade_case",
        }
    ],
    "Trade Shipment": [
        {
            "fieldname": "purchase_order",
            "label": "Đơn mua hàng liên kết (Purchase Order)",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "insert_after": "supplier",
        },
        {
            "fieldname": "purchase_receipt",
            "label": "Phiếu nhập kho (Purchase Receipt)",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "insert_after": "purchase_order",
        }
    ]
}

def setup_custom_fields():
    """Tự động cài đặt toàn bộ Custom Fields cho Giai đoạn 4"""
    print("=== [BẮT ĐẦU CÀI ĐẶT CUSTOM FIELDS GIAI ĐOẠN 4] ===")
    create_custom_fields(CUSTOM_FIELDS, update=True)
    frappe.db.commit()
    print("=== [HOÀN TẤT CÀI ĐẶT CUSTOM FIELDS GIAI ĐOẠN 4] ===")
