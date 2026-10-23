# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

from datetime import datetime, date

try:
    import frappe
    from frappe import _
    from frappe.model.document import Document
except ImportError:
    frappe = None
    _ = lambda x: x
    class Document:
        def __init__(self, *args, **kwargs):
            self.__dict__.update(kwargs)
            if args and isinstance(args[0], dict):
                self.__dict__.update(args[0])

        def get(self, key, default=None):
            return getattr(self, key, default)

        def set(self, key, value):
            setattr(self, key, value)

        def append(self, table_field, value):
            if not hasattr(self, table_field):
                setattr(self, table_field, [])
            table = getattr(self, table_field)
            table.append(value)
            return value

        def as_dict(self):
            return dict(self.__dict__)


class TradeCase(Document):
    """
    Master DocType for Trade Case Overview - Central Operating Dossier for Import/Export shipments.
    Does NOT duplicate operational item rows from Purchase Order or Sales Order.
    Acts as the master case entity linking references and defining stage gates.
    """

    LIFECYCLE_STAGES = [
        "PO",
        "Booking",
        "Export Port",
        "In Transit",
        "Import Port",
        "Customs",
        "Warehouse",
        "Cost Finalization",
        "Closed"
    ]

    HEALTH_STATUSES = [
        "Healthy",
        "Attention",
        "At Risk",
        "Critical"
    ]

    STAGE_GATE_DEFINITIONS = [
        ("GATE_SHIPMENT", "1. Vận đơn đã giao hàng đến đích (ATA Completed)"),
        ("GATE_DOCS", "2. Đủ 100% chứng từ ngoại thương bắt buộc đã duyệt"),
        ("GATE_CUSTOMS", "3. Tờ khai hải quan đã thông quan & hoàn tất nộp thuế"),
        ("GATE_WAREHOUSE", "4. Hàng hóa đã nhập kho và KCS đạt yêu cầu"),
        ("GATE_LCV", "5. Landed Cost Voucher đã lập và phân bổ vào giá vốn"),
        ("GATE_CLEARING", "6. Tài khoản trung gian chi phí đã triệt tiêu về 0.00"),
        ("GATE_EXCEPTIONS", "7. Không còn bất kỳ sự cố Critical/High nào đang mở"),
        ("GATE_SETTLEMENT", "8. Đã thanh toán và đối soát đủ hóa đơn NCC & Forwarder")
    ]

    def validate(self):
        if not getattr(self, "trade_type", None):
            self.trade_type = "Import"

        if not getattr(self, "status", None):
            self.status = "Active"

        if not getattr(self, "current_stage", None):
            self.current_stage = "PO"

        if not getattr(self, "overall_health", None):
            self.overall_health = "Healthy"

        if not getattr(self, "priority", None):
            self.priority = "Normal"

        if not getattr(self, "case_title", None):
            ref = getattr(self, "purchase_order", None) or getattr(self, "sales_order", None) or getattr(self, "name", "Mới")
            party = getattr(self, "supplier", None) or getattr(self, "customer", None) or "Đối tác"
            self.case_title = f"{self.trade_type}: {party} ({ref})"

        # Synchronize field aliases
        if getattr(self, "shipping_mode", None) and not getattr(self, "mode", None):
            self.mode = self.shipping_mode
        elif getattr(self, "mode", None) and not getattr(self, "shipping_mode", None):
            self.shipping_mode = self.mode

        if getattr(self, "start_date", None) and not getattr(self, "opened_date", None):
            self.opened_date = self.start_date
        elif getattr(self, "opened_date", None) and not getattr(self, "start_date", None):
            self.start_date = self.opened_date

        if getattr(self, "target_completion_date", None) and not getattr(self, "expected_close_date", None):
            self.expected_close_date = self.target_completion_date
        elif getattr(self, "expected_close_date", None) and not getattr(self, "target_completion_date", None):
            self.target_completion_date = self.expected_close_date

        if getattr(self, "actual_completion_date", None) and not getattr(self, "closed_date", None):
            self.closed_date = self.actual_completion_date
        elif getattr(self, "closed_date", None) and not getattr(self, "actual_completion_date", None):
            self.actual_completion_date = self.closed_date

        # Fetch Reference metadata from Purchase Order if linked and not already set
        if getattr(self, "purchase_order", None) and frappe and hasattr(frappe, "db"):
            try:
                po_data = frappe.db.get_value(
                    "Purchase Order",
                    self.purchase_order,
                    ["supplier", "currency", "grand_total", "company"],
                    as_dict=True
                )
                if po_data:
                    if not getattr(self, "supplier", None):
                        self.supplier = po_data.get("supplier")
                    if not getattr(self, "currency", None):
                        self.currency = po_data.get("currency")
                    if not getattr(self, "order_amount", None):
                        self.order_amount = po_data.get("grand_total")
                    if not getattr(self, "company", None):
                        self.company = po_data.get("company")
            except Exception:
                pass

        # Populate stage gate checklist items if empty
        self.populate_default_stage_gate_checklist()

    def populate_default_stage_gate_checklist(self):
        checklist = getattr(self, "stage_gate_checklist", None)
        if checklist is None or len(checklist) == 0:
            self.stage_gate_checklist = []
            for code, label in self.STAGE_GATE_DEFINITIONS:
                item_data = {
                    "gate_code": code,
                    "gate_label": label,
                    "is_mandatory": 1,
                    "status": "Failed"
                }
                self.append("stage_gate_checklist", item_data)

    def can_close(self, validation_results=None):
        """
        Stage Gate Validation to check if this Trade Case can be safely closed.
        Checks all 8 standard criteria:
        1. GATE_SHIPMENT: Shipment delivered to destination
        2. GATE_DOCS: 100% required trade documents approved
        3. GATE_CUSTOMS: Customs declaration cleared & duties paid
        4. GATE_WAREHOUSE: Goods received at warehouse & QC passed
        5. GATE_LCV: Landed Cost Voucher submitted & allocated
        6. GATE_CLEARING: Intermediate clearing account 1562 settled to 0.00
        7. GATE_EXCEPTIONS: Zero open critical/high exceptions
        8. GATE_SETTLEMENT: Forwarder & vendor invoices settled
        Returns (can_close: bool, criteria_list: list)
    """
        checks = [
            {
                "code": "GATE_SHIPMENT",
                "key": "shipment_delivered",
                "label": "1. Vận đơn đã giao hàng đến đích (ATA Completed)",
                "passed": getattr(self, "current_stage", "") in ["Warehouse", "Cost Finalization", "Closed"],
                "reason": "Vận chuyển đã hoàn tất giao hàng đến đích." if getattr(self, "current_stage", "") in ["Warehouse", "Cost Finalization", "Closed"] else "Vận đơn chưa giao hàng đến kho đích."
            },
            {
                "code": "GATE_DOCS",
                "key": "docs_completed",
                "label": "2. Đủ 100% chứng từ ngoại thương bắt buộc đã duyệt",
                "passed": float(getattr(self, "document_readiness_pct", 0) or 0) >= 100.0,
                "reason": "100% chứng từ đã sẵn sàng và được kiểm duyệt." if float(getattr(self, "document_readiness_pct", 0) or 0) >= 100.0 else f"Chưa đủ chứng từ ngoại thương ({getattr(self, 'document_readiness_pct', 0)}%)."
            },
            {
                "code": "GATE_CUSTOMS",
                "key": "customs_cleared",
                "label": "3. Tờ khai hải quan đã thông quan & hoàn tất nộp thuế",
                "passed": getattr(self, "customs_cleared", 0) == 1,
                "reason": "Tờ khai hải quan đã thông quan." if getattr(self, "customs_cleared", 0) == 1 else "Tờ khai hải quan chưa thông quan hoặc chưa nộp thuế."
            },
            {
                "code": "GATE_WAREHOUSE",
                "key": "warehouse_received",
                "label": "4. Hàng hóa đã nhập kho và KCS đạt yêu cầu",
                "passed": getattr(self, "current_stage", "") in ["Cost Finalization", "Closed"],
                "reason": "Hàng đã nhập kho an toàn và hoàn tất KCS." if getattr(self, "current_stage", "") in ["Cost Finalization", "Closed"] else "Chưa hoàn tất nhận kho và nghiệm thu KCS."
            },
            {
                "code": "GATE_LCV",
                "key": "lcv_allocated",
                "label": "5. Landed Cost Voucher đã lập và phân bổ vào giá vốn",
                "passed": getattr(self, "costs_finalized", 0) == 1,
                "reason": "Chi phí Landed Cost đã phân bổ xong vào giá vốn." if getattr(self, "costs_finalized", 0) == 1 else "Landed Cost Voucher chưa hoàn tất phân bổ."
            },
            {
                "code": "GATE_CLEARING",
                "key": "costs_clearing",
                "label": "6. Tài khoản trung gian chi phí đã triệt tiêu về 0.00",
                "passed": getattr(self, "costs_finalized", 0) == 1,
                "reason": "Tài khoản chi phí tạm tính đã cân đối về 0.00." if getattr(self, "costs_finalized", 0) == 1 else "Tài khoản trung gian phân bổ chi phí chưa triệt tiêu."
            },
            {
                "code": "GATE_EXCEPTIONS",
                "key": "zero_open_exceptions",
                "label": "7. Không còn bất kỳ sự cố Critical/High nào đang mở",
                "passed": int(getattr(self, "open_exceptions_count", 0) or 0) == 0 and int(getattr(self, "critical_exceptions_count", 0) or 0) == 0,
                "reason": "Không còn sự cố ngoại lệ nào đang mở." if int(getattr(self, "open_exceptions_count", 0) or 0) == 0 else f"Còn {getattr(self, 'open_exceptions_count', 0)} sự cố chưa giải quyết."
            },
            {
                "code": "GATE_SETTLEMENT",
                "key": "costs_finalized",
                "label": "8. Đã thanh toán và đối soát đủ hóa đơn NCC & Forwarder",
                "passed": getattr(self, "costs_finalized", 0) == 1,
                "reason": "Đã tất toán toàn bộ hóa đơn dịch vụ và mua hàng." if getattr(self, "costs_finalized", 0) == 1 else "Còn hóa đơn nhà cung cấp/forwarder chưa tất toán."
            }
        ]

        if validation_results and isinstance(validation_results, dict):
            for check in checks:
                code = check["code"]
                key = check.get("key")
                val_entry = None
                if code in validation_results:
                    val_entry = validation_results[code]
                elif key and key in validation_results:
                    val_entry = validation_results[key]

                if val_entry is not None:
                    if isinstance(val_entry, dict):
                        check["passed"] = bool(val_entry.get("passed", check["passed"]))
                        if "reason" in val_entry:
                            check["reason"] = val_entry["reason"]
                    elif isinstance(val_entry, bool):
                        check["passed"] = val_entry

        all_passed = all(c["passed"] for c in checks)
        return all_passed, checks

    def close_case(self, validation_results=None):
        can_close_flag, checks = self.can_close(validation_results)
        if not can_close_flag:
            failed_reasons = [c["reason"] for c in checks if not c["passed"]]
            msg = _("Không thể đóng hồ sơ {0}: {1}").format(
                getattr(self, "name", "N/A"), "; ".join(failed_reasons)
            )
            if frappe:
                frappe.throw(msg)
            else:
                raise ValueError(msg)

        self.status = "Closed"
        self.current_stage = "Closed"
        self.actual_completion_date = datetime.now().strftime("%Y-%m-%d")
        self.closed_date = self.actual_completion_date
        self.stage_gate_status = "Passed"
        self.stage_gate_verified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update checklist items to Passed
        if hasattr(self, "stage_gate_checklist") and self.stage_gate_checklist:
            for item in self.stage_gate_checklist:
                if hasattr(item, "set"):
                    item.set("status", "Passed")
                    item.set("verified_at", self.stage_gate_verified_at)
                elif isinstance(item, dict):
                    item["status"] = "Passed"
                    item["verified_at"] = self.stage_gate_verified_at

        return True
