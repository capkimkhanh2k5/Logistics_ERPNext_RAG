# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

STANDARD_DOCUMENTS = [
    ("Contract", "Hợp đồng Ngoại thương (Sale Contract)", 1),
    ("Commercial Invoice", "Hóa đơn Thương mại (Commercial Invoice)", 1),
    ("Packing List", "Phiếu đóng gói chi tiết (Packing List)", 1),
    ("Bill of Lading", "Vận tải đơn (Bill of Lading / Airway Bill)", 1),
    ("Certificate of Origin", "Chứng nhận Xuất xứ hàng hóa (C/O)", 1),
    ("Customs Declaration", "Tờ khai Hải quan thông quan", 1),
    ("Cargo Insurance", "Đơn bảo hiểm hàng hóa quốc tế", 0),
    ("Quality Inspection", "Chứng thư giám định chất lượng / Kiểm dịch", 0),
]

class TradeCase(Document):
    def validate(self):
        validate_trade_case(self)

def validate_trade_case(doc, method=None):
    """Xử lý toàn diện logic nghiệp vụ cho Hồ sơ Thương mại (Trade Case)"""
    ensure_default_documents(doc)
    calculate_document_readiness(doc)
    rollup_shipment_costs(doc)


def ensure_default_documents(doc):
    """Tự động thiết lập danh mục chứng từ kiểm soát nếu bảng đang rỗng"""
    if not doc.get("documents"):
        for doc_type, doc_name, is_req in STANDARD_DOCUMENTS:
            doc.append("documents", {
                "document_type": doc_type,
                "document_name": doc_name,
                "is_mandatory": is_req,
                "status": "Pending"
            })

def calculate_document_readiness(doc):
    """Đánh giá điều kiện sẵn sàng của bộ chứng từ (Stage Gate 1)"""
    mandatory_docs = [d for d in doc.get("documents", []) if d.is_mandatory]
    if not mandatory_docs:
        doc.document_readiness_pct = 100.0
        return

    approved_docs = [d for d in mandatory_docs if d.status == "Approved"]
    doc.document_readiness_pct = round((len(approved_docs) / len(mandatory_docs)) * 100, 2)

    if doc.document_readiness_pct == 100.0:
        if doc.stage_gate_status == "Not Ready":
            doc.stage_gate_status = "Document Ready"
    else:
        if doc.stage_gate_status in ("Document Ready", "Customs Ready"):
            doc.stage_gate_status = "Not Ready"

def rollup_shipment_costs(doc):
    """Tổng hợp chi phí thực tế và chênh lệch từ các chuyến tàu (Trade Shipment) con"""
    if not doc.name or doc.is_new():
        return

    shipments = frappe.get_all(
        "Trade Shipment",
        filters={"trade_case": doc.name},
        fields=["total_actual_cost", "total_budgeted_cost"]
    )

    if shipments:
        total_actual = sum(flt(s.total_actual_cost) for s in shipments)
        doc.total_actual_cost_vnd = round(total_actual, 2)
        budget = flt(doc.total_budget_vnd)
        doc.cost_variance_vnd = round(doc.total_actual_cost_vnd - budget, 2)
        if budget > 0:
            doc.cost_variance_pct = round((doc.cost_variance_vnd / budget) * 100, 2)
        else:
            doc.cost_variance_pct = 0.0
