# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, date_diff, add_days, flt
from frappe.model.document import Document

STANDARD_MILESTONES = [
    ("M01_PO_ISSUED", "Phát hành Đơn mua hàng (PO Issued)"),
    ("M02_CARGO_READY", "Hàng sẵn sàng đóng gói (Cargo Ready Date)"),
    ("M03_RISK_TRANSFER", "Chuyển giao rủi ro Incoterm (Risk Transfer Point)"),
    ("M04_ETD", "Tàu rời cảng xuất phát (Departure POL)"),
    ("M05_ETA", "Tàu cập cảng đến (Arrival POD)"),
    ("M06_CUSTOMS_REG", "Đăng ký mở tờ khai hải quan (Customs Registered)"),
    ("M07_CUSTOMS_CLEAR", "Thông quan hải quan hoàn tất (Customs Cleared)"),
    ("M08_DEM_DET_DEADLINE", "Hạn chót miễn phí lưu bãi/cont (Free-time Deadline)"),
    ("M09_WH_RECEIPT", "Nhập kho hoàn tất (Warehouse Receipt)")
]

class TradeShipment(Document):
    def validate(self):
        validate_trade_shipment(self)

def validate_trade_shipment(doc, method=None):
    """Bộ xử lý logic nghiệp vụ toàn diện cho Hồ sơ Lô hàng (Trade Shipment)"""
    ensure_default_milestones(doc)
    calculate_milestone_variances(doc)
    calculate_container_deadlines(doc)
    calculate_cost_item_variances(doc)
    validate_closure_governance(doc)

def ensure_default_milestones(doc):
    """Tự động sinh đủ 9 mốc kiểm soát tiến độ nếu bảng con đang trống"""
    if not doc.get("milestones"):
        for code, name in STANDARD_MILESTONES:
            doc.append("milestones", {
                "milestone_code": code,
                "milestone_name": name,
                "status": "Pending",
                "variance_days": 0
            })

def calculate_milestone_variances(doc):
    """Tính toán số ngày lệch tiến độ (Thực tế vs Kế hoạch) cho từng mốc"""
    for row in doc.get("milestones", []):
        if row.actual_date and row.planned_date:
            row.variance_days = date_diff(row.actual_date, row.planned_date)
            if row.variance_days > 0 and row.status != "Completed":
                row.status = "Delayed"
            elif row.status != "Delayed":
                row.status = "Completed"
        elif row.actual_date:
            row.status = "Completed"
            row.variance_days = 0

def calculate_container_deadlines(doc):
    """Tự động tính ngày hết hạn Free-time lưu bãi và giữ vỏ theo ngày tàu cập cảng (M05)"""
    eta_date = None
    for m in doc.get("milestones", []):
        if m.milestone_code == "M05_ETA":
            eta_date = m.actual_date or m.planned_date
            break

    if eta_date:
        for cont in doc.get("containers", []):
            if cont.demurrage_free_days and not cont.demurrage_deadline:
                cont.demurrage_deadline = add_days(eta_date, cont.demurrage_free_days)
            if cont.detention_free_days and not cont.empty_return_deadline:
                cont.empty_return_deadline = add_days(eta_date, cont.detention_free_days)

def calculate_cost_item_variances(doc):
    """Bóc tách chênh lệch Dự toán vs Thực tế thành: Lệch Đơn giá và Lệch Tỷ giá"""
    total_budget_vnd = 0.0
    total_actual_vnd = 0.0

    for item in doc.get("cost_items", []):
        b_cur = flt(item.budgeted_amount_cur)
        b_fx = flt(item.budgeted_fx_rate) or 1.0
        item.budgeted_amount_vnd = round(b_cur * b_fx, 2)
        total_budget_vnd += item.budgeted_amount_vnd

        a_cur = flt(item.actual_amount_cur)
        a_fx = flt(item.actual_fx_rate) or 1.0
        item.actual_amount_vnd = round(a_cur * a_fx, 2)
        total_actual_vnd += item.actual_amount_vnd

        item.variance_vnd = round(item.actual_amount_vnd - item.budgeted_amount_vnd, 2)
        # Bóc tách:
        # 1. Lệch tỷ giá = Thực tế ngoại tệ * (Tỷ giá thực tế - Tỷ giá dự toán)
        item.fx_variance_vnd = round(a_cur * (a_fx - b_fx), 2)
        # 2. Lệch đơn giá = (Thực tế ngoại tệ - Dự toán ngoại tệ) * Tỷ giá dự toán
        item.price_variance_vnd = round((a_cur - b_cur) * b_fx, 2)

    doc.total_budgeted_cost = round(total_budget_vnd, 2)
    doc.total_actual_cost = round(total_actual_vnd, 2)
    doc.cost_variance_amount = round(total_actual_vnd - total_budget_vnd, 2)

    if total_budget_vnd > 0:
        doc.cost_variance_pct = round((doc.cost_variance_amount / total_budget_vnd) * 100, 2)
    else:
        doc.cost_variance_pct = 0.0

def validate_closure_governance(doc):
    """Chặn quyết toán đóng lô hàng nếu vượt ngân sách > 10% mà chưa có phê duyệt cấp cao"""
    if doc.cost_status == "Closed" and doc.cost_variance_pct > 10.0:
        user_roles = frappe.get_roles()
        if "System Manager" not in user_roles and "CFO" not in user_roles:
            frappe.throw(
                _("Lô hàng vượt dự toán ngân sách {0}% (> 10%). Yêu cầu phê duyệt của Ban Giám đốc / Giám đốc Tài chính (CFO) trước khi đóng quyết toán lô hàng.").format(doc.cost_variance_pct),
                title=_("Vượt Ngân sách Cần Phê duyệt Cấp cao")
            )
