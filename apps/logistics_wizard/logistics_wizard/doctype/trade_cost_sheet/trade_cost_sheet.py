# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

from datetime import datetime, date
from typing import Dict, Any, List, Optional

try:
    import frappe
    from frappe import _
    from frappe.model.document import Document
except ImportError:
    frappe = None
    _ = lambda x: x

    class Document:
        """
        Standalone mock fallback for Frappe Document model.
        Allows unittests to execute in pure Python environments without bench/frappe runtime.
        """
        def __init__(self, *args, **kwargs):
            self.__dict__.update(kwargs)
            if args and isinstance(args[0], dict):
                self.__dict__.update(args[0])
            for key in ["cost_items", "document_links"]:
                if not hasattr(self, key):
                    setattr(self, key, [])
                else:
                    raw_list = getattr(self, key)
                    wrapped = []
                    for it in raw_list:
                        if isinstance(it, dict):
                            wrapped.append(Document(it))
                        else:
                            wrapped.append(it)
                    setattr(self, key, wrapped)

        def get(self, key, default=None):
            return getattr(self, key, default)

        def set(self, key, value):
            setattr(self, key, value)

        def append(self, table_field, value):
            if not hasattr(self, table_field):
                setattr(self, table_field, [])
            table = getattr(self, table_field)
            if isinstance(value, dict):
                value = Document(value)
            table.append(value)
            return value

        def as_dict(self):
            d = {}
            for k, v in self.__dict__.items():
                if isinstance(v, list):
                    d[k] = [it.as_dict() if hasattr(it, "as_dict") else it for it in v]
                else:
                    d[k] = v
            return d

        def save(self, *args, **kwargs):
            if hasattr(self, "validate"):
                self.validate()
            return self


def flt(val: Any, precision: Optional[int] = None) -> float:
    """Safe float conversion matching Frappe's flt utility."""
    try:
        res = float(val or 0.0)
    except (ValueError, TypeError):
        res = 0.0
    if precision is not None:
        return round(res, precision)
    return res


def _get_item_field(item: Any, fieldname: str, default: Any = None) -> Any:
    """Safely retrieves a field value from either a Document object or a dictionary."""
    if hasattr(item, "get"):
        val = item.get(fieldname)
        if val is not None:
            return val
    return getattr(item, fieldname, default)


def _set_item_field(item: Any, fieldname: str, value: Any) -> None:
    """Safely assigns a field value to either a Document object or a dictionary."""
    if hasattr(item, "set"):
        item.set(fieldname, value)
    elif isinstance(item, dict):
        item[fieldname] = value
    else:
        setattr(item, fieldname, value)


class TradeCostSheet(Document):
    """
    Parent DocType for Module 5 — Trade Cost & Landed Cost Management.
    Governs logistics expenses across 11 standard categories, estimated vs. actual figures,
    multi-currency exchange rates, landed cost rollups, and audit anomaly states.
    """

    STANDARD_COST_TYPES = [
        "Freight",
        "Insurance",
        "Duty",
        "Tax",
        "Port",
        "Handling",
        "Storage",
        "Demurrage/Detention",
        "Trucking",
        "Broker Fee",
        "Other"
    ]
    COST_TYPES = STANDARD_COST_TYPES

    ALLOCATION_RULES = [
        "By Value",
        "By Quantity",
        "By Weight",
        "By Volume",
        "Custom Factor"
    ]

    STATUS_OPTIONS = [
        "Draft",
        "Submitted",
        "Verified",
        "Allocated",
        "Finalized",
        "Cancelled"
    ]

    FINALIZATION_STATUSES = [
        "DRAFT",
        "IN PROGRESS",
        "ALMOST READY",
        "ALLOCATED",
        "FINALIZED"
    ]

    def validate(self):
        """Lifecycle validation hook called before saving or submitting."""
        self.set_default_values()
        self.sync_from_trade_case()
        self.calculate_item_bases()
        self.calculate_totals()
        self.calculate_status_rollups()
        if getattr(self, "trade_type", "Import") == "Export":
            self.calculate_export_profitability()
        self.run_cost_audit()
        self.sync_to_trade_case()

    def on_submit(self):
        """
        Lifecycle hook when Trade Cost Sheet is submitted/approved.
        Automatically synchronizes import landed costs into ERPNext Landed Cost Voucher
        if receipt documents are linked and LCV has not been created yet.
        """
        if str(getattr(self, "trade_type", "Import")).strip() == "Import":
            if not getattr(self, "landed_cost_voucher", None):
                doc_links = getattr(self, "document_links", []) or []
                has_receipts = any(
                    _get_item_field(dl, "document_type") in ("Purchase Receipt", "Purchase Invoice")
                    and _get_item_field(dl, "is_active", 1)
                    for dl in doc_links
                )
                if has_receipts or getattr(self, "purchase_receipts", None):
                    try:
                        self.sync_to_lcv(auto_submit=True)
                    except Exception:
                        pass
        self.calculate_status_rollups()
        self.sync_to_trade_case()

    def set_default_values(self):
        """Ensures all header and numeric fields have valid default values."""
        if not getattr(self, "trade_type", None):
            self.trade_type = "Import"

        if not getattr(self, "status", None):
            self.status = "Draft"

        if not getattr(self, "posting_date", None):
            if frappe and hasattr(frappe, "utils") and hasattr(frappe.utils, "today"):
                self.posting_date = frappe.utils.today()
            else:
                self.posting_date = date.today().isoformat()

        if not getattr(self, "currency", None):
            self.currency = "USD"

        conv_rate = getattr(self, "conversion_rate", None)
        if conv_rate is None or flt(conv_rate) <= 0:
            self.conversion_rate = 1.0
        else:
            self.conversion_rate = flt(conv_rate)

        if not getattr(self, "allocation_rule", None):
            self.allocation_rule = "By Value"

        if not getattr(self, "naming_series", None):
            self.naming_series = "TCS-.YYYY.-."

        if getattr(self, "cost_items", None) is None:
            self.cost_items = []

        if getattr(self, "document_links", None) is None:
            self.document_links = []

        if getattr(self, "total_purchase_value", None) is None:
            self.total_purchase_value = 0.0
        else:
            self.total_purchase_value = flt(self.total_purchase_value)

    def sync_from_trade_case(self):
        """Fetches company, currency, trade_type, and purchase order amount from linked Trade Case."""
        tc_id = getattr(self, "trade_case", None)
        if tc_id and frappe and hasattr(frappe, "db") and frappe.db:
            try:
                tc = frappe.db.get_value(
                    "Trade Case",
                    tc_id,
                    ["company", "currency", "order_amount", "trade_type", "case_title"],
                    as_dict=True
                )
                if tc:
                    if not getattr(self, "company", None) and tc.get("company"):
                        self.company = tc.get("company")
                    if not getattr(self, "currency", None) and tc.get("currency"):
                        self.currency = tc.get("currency")
                    if not getattr(self, "case_title", None) and tc.get("case_title"):
                        self.case_title = tc.get("case_title")
                    if (not getattr(self, "total_purchase_value", None) or flt(self.total_purchase_value) == 0.0) and tc.get("order_amount"):
                        self.total_purchase_value = flt(tc.get("order_amount") or 0.0)
                    if not getattr(self, "trade_type", None) and tc.get("trade_type"):
                        self.trade_type = tc.get("trade_type")
            except Exception:
                pass

    def calculate_item_bases(self):
        """
        Calculates item-level base currency amounts and line-level variances for child items.
        Handles multi-currency conversion with exchange rate.
        estimated_amount_base = round(estimated_amount * exchange_rate, 2)
        actual_amount_base = round(actual_amount * exchange_rate, 2)
        Line Variance Amount = Actual - Estimated
        Line Variance % = ((Actual - Estimated) / Estimated) * 100
        """
        sheet_rate = flt(getattr(self, "conversion_rate", 1.0)) or 1.0
        items = getattr(self, "cost_items", []) or []

        for item in items:
            item_status = _get_item_field(item, "status", "Draft")
            if item_status == "Cancelled":
                continue

            rate = flt(_get_item_field(item, "exchange_rate", 0.0))
            if rate <= 0.0:
                rate = sheet_rate
                _set_item_field(item, "exchange_rate", rate)

            # Support both estimated_cost and estimated_amount
            est = _get_item_field(item, "estimated_cost", None)
            if est is None:
                est = _get_item_field(item, "estimated_amount", 0.0)
            est = flt(est)

            # Support both actual_cost and actual_amount
            act = _get_item_field(item, "actual_cost", None)
            if act is None:
                act = _get_item_field(item, "actual_amount", 0.0)
            act = flt(act)

            base_est = round(est * rate, 2)
            base_act = round(act * rate, 2)

            _set_item_field(item, "estimated_cost", est)
            _set_item_field(item, "estimated_amount", est)
            _set_item_field(item, "actual_cost", act)
            _set_item_field(item, "actual_amount", act)
            _set_item_field(item, "base_estimated_cost", base_est)
            _set_item_field(item, "estimated_amount_base", base_est)
            _set_item_field(item, "base_actual_cost", base_act)
            _set_item_field(item, "actual_amount_base", base_act)

            var_amt = round(base_act - base_est, 2)
            if base_est > 0:
                var_pct = round((var_amt / base_est) * 100.0, 1)
            elif base_est == 0 and base_act == 0:
                var_pct = 0.0
            else:
                var_pct = 100.0

            _set_item_field(item, "variance_amount", var_amt)
            _set_item_field(item, "variance_pct", var_pct)

    def calculate_variance(self):
        """Alias and compatibility hook for calculating line item base variances."""
        self.calculate_item_bases()

    def calculate_totals(self):
        """
        Aggregates financial totals:
        - total_estimated_cost: sum of active item base_estimated_cost
        - total_actual_cost: sum of active item base_actual_cost
        - actual_landed_cost: total_purchase_value + total_actual_cost
        - variance_amount: total_actual_cost - total_estimated_cost
        - variance_pct: round((variance_amount / total_estimated_cost) * 100, 1)
        """
        items = getattr(self, "cost_items", []) or []
        active_items = [
            it for it in items
            if _get_item_field(it, "status", "Draft") != "Cancelled"
        ]

        total_est = round(sum(flt(_get_item_field(it, "base_estimated_cost", 0.0)) for it in active_items), 2)
        total_act = round(sum(flt(_get_item_field(it, "base_actual_cost", 0.0)) for it in active_items), 2)

        self.total_estimated_cost = total_est
        self.total_actual_cost = total_act

        purchase_val = round(flt(getattr(self, "total_purchase_value", 0.0)), 2)
        self.actual_landed_cost = round(purchase_val + self.total_actual_cost, 2)

        var_amt = round(self.total_actual_cost - self.total_estimated_cost, 2)
        self.variance_amount = var_amt

        if self.total_estimated_cost > 0:
            self.variance_pct = round((var_amt / self.total_estimated_cost) * 100.0, 1)
        elif self.total_estimated_cost == 0 and self.total_actual_cost == 0:
            self.variance_pct = 0.0
        else:
            self.variance_pct = 100.0

    def calculate_status_rollups(self):
        """
        Calculates status rollup metrics across active child cost items:
        - invoices_total: total active (non-cancelled) cost items
        - invoices_received: items with non-empty invoice_number
        - costs_verified: items with status in ['Verified', 'Allocated']
        - costs_allocated: items with status == 'Allocated'
        - cost_finalization_status: State machine (DRAFT, IN PROGRESS, ALMOST READY, ALLOCATED, FINALIZED)
        """
        items = getattr(self, "cost_items", []) or []
        active_items = [
            it for it in items
            if _get_item_field(it, "status", "Draft") != "Cancelled"
        ]

        inv_total = len(active_items)
        inv_rcv = sum(
            1 for it in active_items
            if bool(str(_get_item_field(it, "invoice_number") or "").strip())
        )
        c_ver = sum(
            1 for it in active_items
            if _get_item_field(it, "status") in ["Verified", "Allocated"]
        )
        c_alloc = sum(
            1 for it in active_items
            if _get_item_field(it, "status") == "Allocated"
        )

        if inv_total == 0:
            status = "DRAFT"
        elif c_alloc == inv_total and inv_total > 0:
            if getattr(self, "status", "") in ["Finalized", "Closed", "Submitted"] or getattr(self, "docstatus", 0) == 1:
                status = "FINALIZED"
            else:
                status = "ALLOCATED"
        elif inv_rcv == inv_total and c_ver == inv_total and inv_total > 0:
            status = "ALMOST READY"
        elif inv_rcv > 0 or c_ver > 0 or c_alloc > 0:
            status = "IN PROGRESS"
        else:
            status = "DRAFT"

        self.invoices_total = inv_total
        self.invoices_received = inv_rcv
        self.costs_verified = c_ver
        self.costs_allocated = c_alloc
        self.cost_finalization_status = status

    def calculate_export_profitability(self):
        """
        Computes Export case profitability using export_tracker engine when linked sales documents
        exist, or direct field values:
        - Gross Margin = Export Revenue - Export COGS
        - Gross Margin % = (Gross Margin / Export Revenue) * 100
        - Net Profit = Export Revenue - Export COGS - Total Logistics Cost
        - Net Margin % = (Net Profit / Export Revenue) * 100
        """
        rev = flt(getattr(self, "export_revenue", 0.0))
        cogs = flt(getattr(self, "export_cogs", 0.0))
        logistics = flt(getattr(self, "total_actual_cost", 0.0))

        # Delegate to export_tracker if document_links or sales_docs are present and rev/cogs not set
        doc_links = getattr(self, "document_links", []) or []
        has_sales_docs = any(
            _get_item_field(dl, "document_type") in ("Sales Order", "Delivery Note", "Sales Invoice")
            for dl in doc_links
        ) or bool(getattr(self, "sales_invoices", None) or getattr(self, "sales_orders", None) or getattr(self, "delivery_notes", None))

        if has_sales_docs and (rev == 0.0 or cogs == 0.0):
            try:
                from logistics_wizard.costing_engine.export_tracker import calculate_export_profitability as calc_exp
                res = calc_exp(self)
                if rev == 0.0 and flt(res.get("export_revenue", 0.0)) > 0:
                    rev = flt(res.get("export_revenue", 0.0))
                    self.export_revenue = rev
                if cogs == 0.0 and flt(res.get("export_cogs", 0.0)) > 0:
                    cogs = flt(res.get("export_cogs", 0.0))
                    self.export_cogs = cogs
            except Exception:
                pass

        self.export_logistics_cost = round(logistics, 2)
        gross_margin = rev - cogs
        self.export_gross_margin = round(gross_margin, 2)
        self.export_gross_margin_pct = round((gross_margin / rev * 100.0), 2) if rev > 0 else 0.0

        net_profit = rev - cogs - logistics
        self.export_net_profit = round(net_profit, 2)
        self.export_net_margin_pct = round((net_profit / rev * 100.0), 2) if rev > 0 else 0.0

    def run_cost_audit(
        self,
        historical_sheets: Optional[List[Any]] = None,
        trade_case: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Executes CostAuditEngine (M4) on this cost sheet:
        - Duplicate invoice & supplier check
        - Missing critical costs by Incoterm & HS code
        - Wrong-case association check
        Stores combined warnings/errors into `self.audit_warnings`.
        """
        try:
            from logistics_wizard.costing_engine.audit_engine import audit_cost_sheet
            res = audit_cost_sheet(self, historical_sheets=historical_sheets, trade_case=trade_case)
            messages = list(res.get("errors", [])) + list(res.get("warnings", []))
            self.audit_warnings = "\n".join(messages) if messages else ""
            self._audit_result = res
            return res
        except Exception:
            if not getattr(self, "audit_warnings", None):
                self.audit_warnings = ""
            return {"passed": True, "errors": [], "warnings": [], "anomalies": []}

    def allocate_import_costs(
        self,
        items: Optional[List[Dict[str, Any]]] = None,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Runs Custom Cost Allocation Engine (M2) across linked Purchase Receipt / Invoice items.
        Computes exact landed cost and new valuation rate per item using Hare-Niemeyer rounding.
        """
        from logistics_wizard.costing_engine.allocation_engine import allocate_costs
        rule = getattr(self, "allocation_rule", None) or "By Value"
        allocated = allocate_costs(
            self,
            rule=rule,
            items=items,
            custom_weights=custom_weights,
        )
        self.allocated_items_preview = allocated
        return allocated

    def sync_to_lcv(
        self,
        auto_submit: bool = False,
        items: Optional[List[Dict[str, Any]]] = None,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Allocates import costs per item and synchronizes into ERPNext Landed Cost Voucher (M2).
        Marks verified cost items as Allocated and updates status rollups.
        """
        from logistics_wizard.costing_engine.lcv_integrator import create_or_update_lcv
        allocated_items = self.allocate_import_costs(items=items, custom_weights=custom_weights)
        raw_res = create_or_update_lcv(self, allocated_items, auto_submit=auto_submit)
        if isinstance(raw_res, str):
            res: Dict[str, Any] = {"success": bool(raw_res), "lcv_name": raw_res}
        elif isinstance(raw_res, dict):
            res = dict(raw_res)
            res.setdefault("success", bool(res.get("lcv_name") or res.get("name")))
        else:
            res = {"success": False, "lcv_name": None}

        if res.get("success") or res.get("lcv_name"):
            lcv_name = res.get("lcv_name") or res.get("name")
            if lcv_name:
                self.landed_cost_voucher = lcv_name
            for it in (getattr(self, "cost_items", []) or []):
                if _get_item_field(it, "status") == "Verified":
                    _set_item_field(it, "status", "Allocated")
            self.calculate_status_rollups()
        res["allocated_items"] = allocated_items
        return res

    def get_breakdown(self) -> List[Dict[str, Any]]:
        """
        Groups actual base costs by 11 standard cost types for dashboard presentation.
        """
        items = getattr(self, "cost_items", []) or []
        breakdown_map: Dict[str, float] = {}

        for it in items:
            if _get_item_field(it, "status") == "Cancelled":
                continue
            ctype = _get_item_field(it, "cost_type") or "Other"
            amt = flt(_get_item_field(it, "base_actual_cost") or _get_item_field(it, "actual_cost") or 0.0)
            breakdown_map[ctype] = round(breakdown_map.get(ctype, 0.0) + amt, 2)

        return [{"label": k, "amount": v} for k, v in breakdown_map.items()]

    def get_cost_breakdown(self) -> List[Dict[str, Any]]:
        """Alias for get_breakdown() to ensure full interoperability."""
        return self.get_breakdown()

    def get_cost_summary_payload(self) -> Dict[str, Any]:
        """
        Produces payload strictly adhering to todoTradeCase.md section 3.3 and
        logistics_wizard.costing_engine.api.get_case_cost_summary(case_id).
        """
        return {
            "purchase_value": flt(getattr(self, "total_purchase_value", 0.0)),
            "estimated_cost": flt(getattr(self, "total_estimated_cost", 0.0)),
            "actual_cost": flt(getattr(self, "total_actual_cost", 0.0)),
            "variance_amount": flt(getattr(self, "variance_amount", 0.0)),
            "variance_pct": flt(getattr(self, "variance_pct", 0.0)),
            "actual_landed_cost": flt(getattr(self, "actual_landed_cost", 0.0)),
            "currency": getattr(self, "currency", "USD") or "USD",
            "breakdown": self.get_breakdown(),
            "invoices_received": int(getattr(self, "invoices_received", 0)),
            "invoices_total": int(getattr(self, "invoices_total", 0)),
            "costs_verified": int(getattr(self, "costs_verified", 0)),
            "costs_allocated": int(getattr(self, "costs_allocated", 0)),
            "cost_finalization_status": getattr(self, "cost_finalization_status", "DRAFT")
        }

    def get_summary_payload(self) -> Dict[str, Any]:
        """Alias for get_cost_summary_payload() for interoperability."""
        return self.get_cost_summary_payload()

    def sync_to_trade_case(self):
        """Synchronizes calculated costing metrics back to the linked Trade Case document."""
        tc_id = getattr(self, "trade_case", None)
        if tc_id and frappe and hasattr(frappe, "db") and frappe.db:
            try:
                tc = frappe.get_doc("Trade Case", tc_id)
                if tc:
                    tc.estimated_landed_cost = (flt(getattr(tc, "order_amount", 0.0))) + self.total_estimated_cost
                    tc.actual_landed_cost = self.actual_landed_cost
                    tc.cost_variance_pct = self.variance_pct
                    if self.cost_finalization_status in ["ALLOCATED", "FINALIZED"]:
                        tc.costs_finalized = 1
                    tc.save(ignore_permissions=True)
            except Exception:
                pass
