# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
costing_engine.api — Public API Facade & Data Contract Implementation
======================================================================
Module 5: Trade Cost & Landed Cost Management (Milestone 5)

Implements the public API facade conforming 100% to todoTradeCase.md Section 3.3:
- get_case_cost_summary(case_id: str) -> Dict[str, Any]
- get_case_export_profitability(case_id: str) -> Dict[str, Any]
- audit_case_costs(case_id: str) -> Dict[str, Any]
- allocate_and_sync_lcv(cost_sheet_name: str, auto_submit: bool = False) -> Dict[str, Any]
- format_case_cost_summary(cost_sheet: Any) -> Dict[str, Any]
"""

import sys
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    import frappe
    from frappe import _
except ImportError:
    frappe = None
    _ = lambda x: x

from logistics_wizard.costing_engine.allocation_engine import (
    CostAllocationEngine,
    allocate_costs,
    extract_receipt_items,
)
from logistics_wizard.costing_engine.lcv_integrator import (
    LCVIntegrator,
    create_or_update_lcv,
)
from logistics_wizard.costing_engine.export_tracker import (
    ExportTracker,
    calculate_export_profitability,
    get_export_profitability_summary,
)
from logistics_wizard.costing_engine.audit_engine import (
    CostAuditEngine,
    audit_cost_sheet,
)

# Registry for testing/offline mock injection
_MOCK_COST_SHEET_REGISTRY: Dict[str, Any] = {}


def register_mock_cost_sheet(case_id: str, cost_sheet_data: Any) -> None:
    """Registers a mock or test cost sheet for offline tests."""
    cid = str(case_id).strip()
    _MOCK_COST_SHEET_REGISTRY[cid] = cost_sheet_data
    # Also index by cost_sheet name if present
    sheet_name = (
        cost_sheet_data.get("name")
        if isinstance(cost_sheet_data, dict)
        else getattr(cost_sheet_data, "name", None)
    )
    if sheet_name:
        _MOCK_COST_SHEET_REGISTRY[str(sheet_name).strip()] = cost_sheet_data


def clear_mock_cost_sheet_registry() -> None:
    """Clears the mock registry."""
    _MOCK_COST_SHEET_REGISTRY.clear()


def calculate_variance(estimated: float, actual: float) -> Tuple[float, float]:
    """
    Calculates variance amount (Actual - Estimated) and variance percentage (1 decimal place).
    Matches todoTradeCase.md Section 3.3 (e.g. 1350 / 17000 = 7.9%) and TradeCostSheet controller.
    """
    amt = round(float(actual or 0.0) - float(estimated or 0.0), 2)
    est_val = float(estimated or 0.0)
    act_val = float(actual or 0.0)
    if est_val > 0.0:
        pct = round((amt / est_val) * 100.0, 1)
    elif est_val == 0.0:
        pct = 100.0 if act_val > 0.0 else 0.0
    else:
        pct = round((amt / abs(est_val)) * 100.0, 1)
    return amt, pct


def rollup_cost_sheet_status(
    items: List[Dict[str, Any]],
    docstatus: int = 0,
    sheet_status: str = "",
) -> Dict[str, Any]:
    """
    Rolls up status metrics across active cost items.
    State machine: DRAFT -> IN PROGRESS -> ALMOST READY -> ALLOCATED -> FINALIZED.
    """
    active_items = [it for it in items if it.get("status") != "Cancelled"]
    total = len(active_items)

    invoices_received = sum(1 for it in active_items if bool(str(it.get("invoice_number") or "").strip()))
    costs_verified = sum(1 for it in active_items if it.get("status") in ("Verified", "Allocated"))
    costs_allocated = sum(1 for it in active_items if it.get("status") == "Allocated")

    if total == 0:
        status = "DRAFT" if docstatus == 0 else "FINALIZED"
    elif docstatus == 1:
        status = "FINALIZED"
    elif costs_allocated == total and total > 0:
        if sheet_status in ("Finalized", "Closed", "Submitted"):
            status = "FINALIZED"
        else:
            status = "ALLOCATED"
    elif costs_verified == total and total > 0:
        status = "ALMOST READY"
    elif invoices_received > 0 or costs_verified > 0 or costs_allocated > 0:
        status = "IN PROGRESS"
    else:
        status = "DRAFT"

    return {
        "invoices_received": invoices_received,
        "invoices_total": total,
        "costs_verified": costs_verified,
        "costs_allocated": costs_allocated,
        "cost_finalization_status": status,
    }


def format_case_cost_summary(cost_sheet: Any) -> Dict[str, Any]:
    """
    Formats a Trade Cost Sheet (Document or dict) into the exact Section 3.3 payload contract.
    """
    if isinstance(cost_sheet, dict):
        raw_items = cost_sheet.get("cost_items", []) or []
        purchase_val = float(
            cost_sheet.get("purchase_value", cost_sheet.get("total_purchase_value", 0.0)) or 0.0
        )
        currency = cost_sheet.get("currency", "USD") or "USD"
        docstatus = int(cost_sheet.get("docstatus", 0) or 0)
        sheet_status = str(cost_sheet.get("status", "") or "")
        sheet_rate = float(cost_sheet.get("conversion_rate", 1.0) or 1.0)
    else:
        raw_items = getattr(cost_sheet, "cost_items", []) or []
        purchase_val = float(
            getattr(cost_sheet, "purchase_value", getattr(cost_sheet, "total_purchase_value", 0.0)) or 0.0
        )
        currency = getattr(cost_sheet, "currency", "USD") or "USD"
        docstatus = int(getattr(cost_sheet, "docstatus", 0) or 0)
        sheet_status = str(getattr(cost_sheet, "status", "") or "")
        sheet_rate = float(getattr(cost_sheet, "conversion_rate", 1.0) or 1.0)

    if sheet_rate <= 0.0:
        sheet_rate = 1.0

    active_items = []
    for it in raw_items:
        st = it.get("status") if isinstance(it, dict) else getattr(it, "status", None)
        if st != "Cancelled":
            active_items.append(it)

    total_est = 0.0
    total_act = 0.0
    breakdown_map: Dict[str, float] = {}

    for it in active_items:
        if isinstance(it, dict):
            rate = float(it.get("exchange_rate", 0.0) or 0.0) or sheet_rate
            base_est = it.get("base_estimated_cost", it.get("estimated_amount_base", None))
            if base_est is None:
                raw_est = float(it.get("estimated_cost", it.get("estimated_amount", 0.0)) or 0.0)
                base_est = round(raw_est * rate, 2)
            else:
                base_est = float(base_est or 0.0)

            base_act = it.get("base_actual_cost", it.get("actual_amount_base", None))
            if base_act is None:
                raw_act = float(it.get("actual_cost", it.get("actual_amount", 0.0)) or 0.0)
                base_act = round(raw_act * rate, 2)
            else:
                base_act = float(base_act or 0.0)

            ctype = it.get("cost_type") or "Other"
        else:
            rate = float(getattr(it, "exchange_rate", 0.0) or 0.0) or sheet_rate
            base_est = getattr(it, "base_estimated_cost", getattr(it, "estimated_amount_base", None))
            if base_est is None:
                raw_est = float(getattr(it, "estimated_cost", getattr(it, "estimated_amount", 0.0)) or 0.0)
                base_est = round(raw_est * rate, 2)
            else:
                base_est = float(base_est or 0.0)

            base_act = getattr(it, "base_actual_cost", getattr(it, "actual_amount_base", None))
            if base_act is None:
                raw_act = float(getattr(it, "actual_cost", getattr(it, "actual_amount", 0.0)) or 0.0)
                base_act = round(raw_act * rate, 2)
            else:
                base_act = float(base_act or 0.0)

            ctype = getattr(it, "cost_type", None) or "Other"

        total_est += base_est
        total_act += base_act
        breakdown_map[ctype] = breakdown_map.get(ctype, 0.0) + base_act

    total_est = round(total_est, 2)
    total_act = round(total_act, 2)
    var_amt, var_pct = calculate_variance(total_est, total_act)

    dict_items = [
        it if isinstance(it, dict) else {
            "status": getattr(it, "status", None),
            "invoice_number": getattr(it, "invoice_number", None),
        }
        for it in active_items
    ]
    rollups = rollup_cost_sheet_status(dict_items, docstatus=docstatus, sheet_status=sheet_status)

    breakdown = [{"label": k, "amount": round(v, 2)} for k, v in sorted(breakdown_map.items())]

    return {
        "purchase_value": round(purchase_val, 2),
        "estimated_cost": total_est,
        "actual_cost": total_act,
        "variance_amount": var_amt,
        "variance_pct": var_pct,
        "actual_landed_cost": round(purchase_val + total_act, 2),
        "currency": currency,
        "breakdown": breakdown,
        "invoices_received": rollups["invoices_received"],
        "invoices_total": rollups["invoices_total"],
        "costs_verified": rollups["costs_verified"],
        "costs_allocated": rollups["costs_allocated"],
        "cost_finalization_status": rollups["cost_finalization_status"],
    }


def _frappe_whitelist():
    """Conditional decorator for frappe.whitelist."""
    if frappe and hasattr(frappe, "whitelist"):
        return frappe.whitelist()
    return lambda f: f


@_frappe_whitelist()
def get_case_cost_summary(case_id: str) -> Dict[str, Any]:
    """
    Returns the exact Section 3.3 payload contract for Trade Case Overview.
    """
    cid = str(case_id or "").strip()
    cost_sheet: Optional[Any] = None

    # 1. Check offline mock registry
    if cid in _MOCK_COST_SHEET_REGISTRY:
        cost_sheet = _MOCK_COST_SHEET_REGISTRY[cid]

    # 2. Check Frappe DB
    if cost_sheet is None and frappe and hasattr(frappe, "db") and hasattr(frappe.db, "get_value"):
        try:
            sheet_name = frappe.db.get_value(
                "Trade Cost Sheet",
                {"trade_case": cid, "docstatus": ["!=", 2]},
                "name",
            )
            if sheet_name:
                cost_sheet = frappe.get_doc("Trade Cost Sheet", sheet_name)
        except Exception:
            pass

    # 3. Fallback if no cost sheet exists for the case
    if cost_sheet is None:
        purchase_val = 0.0
        currency = "USD"
        if frappe and hasattr(frappe, "db") and hasattr(frappe.db, "get_value"):
            try:
                case_info = frappe.db.get_value(
                    "Trade Case",
                    cid,
                    ["order_amount", "currency"],
                    as_dict=True,
                )
                if case_info:
                    purchase_val = float(case_info.get("order_amount") or 0.0)
                    currency = case_info.get("currency") or "USD"
            except Exception:
                pass

        return {
            "purchase_value": round(purchase_val, 2),
            "estimated_cost": 0.0,
            "actual_cost": 0.0,
            "variance_amount": 0.0,
            "variance_pct": 0.0,
            "actual_landed_cost": round(purchase_val, 2),
            "currency": currency,
            "breakdown": [],
            "invoices_received": 0,
            "invoices_total": 0,
            "costs_verified": 0,
            "costs_allocated": 0,
            "cost_finalization_status": "DRAFT",
        }

    return format_case_cost_summary(cost_sheet)


@_frappe_whitelist()
def get_case_export_profitability(case_id: str) -> Dict[str, Any]:
    """Returns export profitability breakdown and margins for an Export Trade Case."""
    cid = str(case_id or "").strip()
    if cid in _MOCK_COST_SHEET_REGISTRY:
        return calculate_export_profitability(_MOCK_COST_SHEET_REGISTRY[cid])
    return get_export_profitability_summary(cid)


@_frappe_whitelist()
def audit_case_costs(case_id: str) -> Dict[str, Any]:
    """Runs full audit verification on the active Cost Sheet of a Trade Case."""
    cid = str(case_id or "").strip()
    cost_sheet = None

    if cid in _MOCK_COST_SHEET_REGISTRY:
        cost_sheet = _MOCK_COST_SHEET_REGISTRY[cid]
    elif frappe and hasattr(frappe, "db") and hasattr(frappe.db, "get_value"):
        try:
            sheet_name = frappe.db.get_value(
                "Trade Cost Sheet",
                {"trade_case": cid, "docstatus": ["!=", 2]},
                "name",
            )
            if sheet_name:
                cost_sheet = frappe.get_doc("Trade Cost Sheet", sheet_name)
        except Exception:
            pass

    if not cost_sheet:
        return {
            "passed": True,
            "errors": [],
            "warnings": [f"No active Trade Cost Sheet found for Trade Case {cid}"],
            "anomalies": [],
        }

    trade_case = None
    if frappe and hasattr(frappe, "get_doc"):
        try:
            trade_case = frappe.get_doc("Trade Case", cid)
        except Exception:
            trade_case = None

    if not trade_case:
        tc_id = (
            cost_sheet.get("trade_case")
            if isinstance(cost_sheet, dict)
            else getattr(cost_sheet, "trade_case", None)
        ) or cid
        trade_case = {"name": tc_id}

    return audit_cost_sheet(cost_sheet, trade_case=trade_case)


@_frappe_whitelist()
def allocate_and_sync_lcv(
    cost_sheet_name: str,
    auto_submit: bool = False,
    items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Allocates import landed costs per item using Custom Cost Allocation Engine
    and synchronizes into ERPNext Landed Cost Voucher (LCV).
    Supports both live Frappe documents and registered mock cost sheets.
    """
    sheet_key = str(cost_sheet_name or "").strip()
    cost_sheet = None

    if sheet_key in _MOCK_COST_SHEET_REGISTRY:
        cost_sheet = _MOCK_COST_SHEET_REGISTRY[sheet_key]
    elif frappe and hasattr(frappe, "get_doc"):
        try:
            cost_sheet = frappe.get_doc("Trade Cost Sheet", sheet_key)
        except Exception:
            cost_sheet = None

    if cost_sheet is None:
        return {"success": False, "error": f"Trade Cost Sheet '{sheet_key}' not found"}

    # Prefer delegating to TradeCostSheet.sync_to_lcv if available on controller
    if hasattr(cost_sheet, "sync_to_lcv") and callable(cost_sheet.sync_to_lcv):
        return cost_sheet.sync_to_lcv(auto_submit=auto_submit, items=items)

    rule = (
        cost_sheet.get("allocation_rule")
        if isinstance(cost_sheet, dict)
        else getattr(cost_sheet, "allocation_rule", None)
    ) or "By Value"

    allocated_items = allocate_costs(cost_sheet, rule=rule, items=items)
    raw_res = create_or_update_lcv(cost_sheet, allocated_items, auto_submit=auto_submit)
    if isinstance(raw_res, str):
        res: Dict[str, Any] = {"success": bool(raw_res), "lcv_name": raw_res}
    elif isinstance(raw_res, dict):
        res = dict(raw_res)
        res.setdefault("success", bool(res.get("lcv_name") or res.get("name")))
    else:
        res = {"success": False, "lcv_name": None}
    res["allocated_items"] = allocated_items
    return res
