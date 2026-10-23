# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
audit_engine.py — Cost Audit & Anomaly Detection Engine
======================================================
Module 5: Trade Cost & Landed Cost Management (Milestone 4)

Provides automated verification and anomaly detection for Trade Cost Sheets:
1. Duplicate Invoice & Supplier Detection:
   - Within the current cost sheet across active items.
   - Across historical cost sheets in Frappe database or passed historical context.
2. Missing Critical Costs Anomaly Check:
   - By Incoterm (FOB, EXW, FCA, CIF, CFR, DDP).
   - By dutiable HS codes / customs declaration flags (Duty, Tax).
3. Wrong-Case Association Check:
   - Verifies linked Trade Case against expected Trade Case context.
   - Verifies linked Purchase Orders, Sales Orders, and Delivery Notes.
"""

import sys
from typing import Dict, Any, List, Optional, Tuple, Set

try:
    import frappe
    from frappe import _
except ImportError:
    frappe = None
    _ = lambda x: x


def _get_field(doc: Any, fieldname: str, default: Any = None) -> Any:
    """Safely retrieves a field from a Document object, dict, or namespace."""
    if doc is None:
        return default
    if isinstance(doc, dict):
        return doc.get(fieldname, default)
    if hasattr(doc, "get"):
        val = doc.get(fieldname)
        if val is not None:
            return val
    return getattr(doc, fieldname, default)


class CostAuditEngine:
    """
    Production-grade Cost Audit Engine for verifying Trade Cost Sheets.
    """

    def __init__(self, cost_sheet: Any, trade_case: Optional[Any] = None, historical_sheets: Optional[List[Any]] = None):
        self.cost_sheet = cost_sheet
        self.trade_case = trade_case
        self.historical_sheets = historical_sheets or []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.anomalies: List[Dict[str, Any]] = []

    def run_all_checks(self) -> Dict[str, Any]:
        """Runs all audit verification checks."""
        self.errors.clear()
        self.warnings.clear()
        self.anomalies.clear()

        self.check_duplicate_invoices()
        self.check_missing_critical_costs()
        self.check_wrong_case_association()

        passed = len(self.errors) == 0
        return {
            "passed": passed,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "anomalies": list(self.anomalies),
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "anomaly_count": len(self.anomalies),
            },
        }

    def check_duplicate_invoices(self) -> None:
        """Flags duplicate invoices within the sheet and across historical records."""
        items = _get_field(self.cost_sheet, "cost_items", []) or []
        active_items = [it for it in items if _get_field(it, "status") != "Cancelled"]

        # 1. Duplicates within current sheet
        seen_invoices: Dict[Tuple[str, str], Any] = {}
        for it in active_items:
            supp = (_get_field(it, "service_provider") or "").strip().lower()
            inv = (_get_field(it, "invoice_number") or "").strip().lower()
            if supp and inv:
                key = (supp, inv)
                if key in seen_invoices:
                    inv_raw = _get_field(it, "invoice_number")
                    supp_raw = _get_field(it, "service_provider")
                    err = f"Duplicate invoice detected: '{inv_raw}' from supplier '{supp_raw}'"
                    self.errors.append(err)
                    self.anomalies.append({
                        "type": "DUPLICATE_INVOICE",
                        "severity": "CRITICAL",
                        "details": err,
                        "item": it,
                    })
                else:
                    seen_invoices[key] = it

        # 2. Duplicates across passed historical sheets
        curr_sheet_name = _get_field(self.cost_sheet, "name")
        if self.historical_sheets:
            for past_sheet in self.historical_sheets:
                if _get_field(past_sheet, "name") == curr_sheet_name:
                    continue
                for past_it in (_get_field(past_sheet, "cost_items") or []):
                    if _get_field(past_it, "status") == "Cancelled":
                        continue
                    p_supp = (_get_field(past_it, "service_provider") or "").strip().lower()
                    p_inv = (_get_field(past_it, "invoice_number") or "").strip().lower()
                    if p_supp and p_inv and (p_supp, p_inv) in seen_invoices:
                        inv_raw = _get_field(past_it, "invoice_number")
                        past_sheet_name = _get_field(past_sheet, "name")
                        err = f"Cross-case duplicate invoice: '{inv_raw}' already used in sheet '{past_sheet_name}'"
                        self.errors.append(err)
                        self.anomalies.append({
                            "type": "CROSS_CASE_DUPLICATE",
                            "severity": "CRITICAL",
                            "details": err,
                        })

        # 3. Duplicates in Frappe DB (if live Frappe bench)
        if frappe and hasattr(frappe, "db") and hasattr(frappe.db, "sql"):
            for (supp_clean, inv_clean), it in seen_invoices.items():
                try:
                    db_duplicates = frappe.db.sql(
                        """
                        SELECT parent, invoice_number, service_provider
                        FROM `tabTrade Cost Item`
                        WHERE LOWER(TRIM(invoice_number)) = %s
                          AND LOWER(TRIM(service_provider)) = %s
                          AND parent != %s
                          AND status != 'Cancelled'
                        LIMIT 5
                        """,
                        (inv_clean, supp_clean, curr_sheet_name or ""),
                        as_dict=True,
                    )
                    for dup in db_duplicates:
                        err = f"Cross-case duplicate invoice: '{dup.get('invoice_number')}' already used in sheet '{dup.get('parent')}'"
                        if err not in self.errors:
                            self.errors.append(err)
                            self.anomalies.append({
                                "type": "CROSS_CASE_DUPLICATE",
                                "severity": "CRITICAL",
                                "details": err,
                            })
                except Exception:
                    pass

    def check_missing_critical_costs(self) -> None:
        """Alerts when critical cost items are missing based on Incoterm, Trade Type, and HS Code."""
        items = _get_field(self.cost_sheet, "cost_items", []) or []
        active_items = [it for it in items if _get_field(it, "status") != "Cancelled"]
        present_cost_types: Set[str] = {(_get_field(it, "cost_type") or "").strip() for it in active_items}

        incoterm = (_get_field(self.cost_sheet, "incoterm") or (
            _get_field(self.trade_case, "incoterm") if self.trade_case else ""
        ) or "").upper().strip()

        trade_type = _get_field(self.cost_sheet, "trade_type") or (
            _get_field(self.trade_case, "trade_type") if self.trade_case else "Import"
        )
        trade_type_norm = "Export" if "EXP" in str(trade_type).upper() else "Import"

        if trade_type_norm == "Import":
            # FOB / EXW / FCA Import expects Freight
            if incoterm in ["FOB", "EXW", "FCA"] and "Freight" not in present_cost_types:
                warn = f"{incoterm} Import shipment is missing international Freight cost item"
                self.warnings.append(warn)
                self.anomalies.append({"type": "MISSING_CRITICAL_COST", "severity": "WARNING", "details": warn})

            # FOB / CIF / CFR Import expects Port or Handling
            if incoterm in ["FOB", "CIF", "CFR"] and "Port" not in present_cost_types and "Handling" not in present_cost_types:
                warn = f"{incoterm} Import is missing destination Port/THC cost item"
                self.warnings.append(warn)
                self.anomalies.append({"type": "MISSING_PORT_COST", "severity": "WARNING", "details": warn})

            # Dutiable HS Code / Goods check
            has_dutiable = _get_field(self.cost_sheet, "has_dutiable_goods", False)
            if self.trade_case:
                customs = _get_field(self.trade_case, "customs_readiness") or {}
                if _get_field(customs, "hs_classification") or _get_field(self.trade_case, "hs_code"):
                    has_dutiable = True

            if has_dutiable and "Duty" not in present_cost_types and "Tax" not in present_cost_types:
                warn = "Dutiable cargo declaration has no Duty or Tax cost line"
                self.warnings.append(warn)
                self.anomalies.append({"type": "MISSING_DUTY_TAX", "severity": "WARNING", "details": warn})

        elif trade_type_norm == "Export":
            # CIF / CFR Export expects Freight paid by exporter
            if incoterm in ["CIF", "CFR"] and "Freight" not in present_cost_types:
                warn = f"{incoterm} Export shipment is missing international Freight cost item"
                self.warnings.append(warn)
                self.anomalies.append({"type": "MISSING_CRITICAL_COST", "severity": "WARNING", "details": warn})

            # FOB / CIF / CFR Export expects origin Port or Handling
            if incoterm in ["FOB", "CIF", "CFR"] and "Port" not in present_cost_types and "Handling" not in present_cost_types:
                warn = f"{incoterm} Export is missing origin Port/THC cost item"
                self.warnings.append(warn)
                self.anomalies.append({"type": "MISSING_PORT_COST", "severity": "WARNING", "details": warn})

    def check_wrong_case_association(self) -> None:
        """Verifies that cost sheet and linked documents match the active Trade Case."""
        if not self.trade_case:
            return

        expected_case_id = _get_field(self.trade_case, "name") or _get_field(self.trade_case, "case_id")
        linked_case = _get_field(self.cost_sheet, "trade_case")

        if linked_case and expected_case_id and str(linked_case).strip() != str(expected_case_id).strip():
            err = f"Cost sheet linked to wrong Trade Case: expected '{expected_case_id}', found '{linked_case}'"
            self.errors.append(err)
            self.anomalies.append({
                "type": "WRONG_CASE_ASSOCIATION",
                "severity": "CRITICAL",
                "details": err,
            })

        # Check document links
        doc_links = _get_field(self.cost_sheet, "document_links", []) or []
        for dl in doc_links:
            dl_case = _get_field(dl, "trade_case")
            if dl_case and expected_case_id and str(dl_case).strip() != str(expected_case_id).strip():
                err = f"Document Link '{_get_field(dl, 'document_name')}' linked to mismatched Trade Case '{dl_case}'"
                self.errors.append(err)
                self.anomalies.append({
                    "type": "WRONG_CASE_ASSOCIATION",
                    "severity": "CRITICAL",
                    "details": err,
                })


def audit_cost_sheet(
    cost_sheet: Any,
    historical_sheets: Optional[List[Any]] = None,
    trade_case: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Public functional interface for auditing a Trade Cost Sheet.
    Matches test contract and returns dict with passed, errors, warnings, anomalies.
    """
    engine = CostAuditEngine(
        cost_sheet=cost_sheet,
        trade_case=trade_case,
        historical_sheets=historical_sheets
    )
    return engine.run_all_checks()
