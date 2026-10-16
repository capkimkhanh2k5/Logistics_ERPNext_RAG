# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
export_tracker.py — Export Logistics Cost Tracking & Profitability Engine
=========================================================================
Module 5: Trade Cost & Landed Cost Management (Milestone 3)

Architecture & Invariants:
1. Public Interfaces:
   - calculate_export_profitability(cost_sheet, sales_docs=None, company_currency=None) -> Dict[str, Any]
   - get_export_profitability_summary(case_id: str) -> Dict[str, Any]
2. Standard Financial Metrics:
   - Revenue (R): Net total recognized from Sales Invoices (or Sales Orders if uninvoiced)
   - COGS (C): Cost of Goods Sold from Delivery Notes (qty * incoming_rate / valuation_rate)
   - Logistics Cost Actual (L_act): Actual logistics expenses from active Trade Cost Items
   - Logistics Cost Estimated (L_est): Estimated logistics expenses from active Trade Cost Items
   - Gross Margin (GM): Revenue - COGS
   - Gross Margin %: (Gross Margin / Revenue) * 100 (safe 0.0% when Revenue <= 0)
   - Net Profit (NP): Revenue - COGS - Logistics Cost Actual
   - Net Margin %: (Net Profit / Revenue) * 100 (safe 0.0% when Revenue <= 0)
   - Variance Amount: Logistics Cost Actual - Logistics Cost Estimated
   - Variance %: (Variance Amount / Logistics Cost Estimated) * 100 (safe 0.0% when L_est <= 0)
3. 11 Standard Cost Types Breakdown:
   - Groups actual logistics costs into 11 categories: Freight, Insurance, Duty, Tax, Port,
     Handling, Storage, Demurrage/Detention, Trucking, Broker Fee, Other.
4. Non-Invasive & Multi-Currency:
   - Multi-currency conversions via conversion_rate / exchange_rate into company base currency.
   - Ignores Cancelled cost items; includes Draft, Verified, and Allocated items.
5. Dual-Mode Runtime & Standalone Mock Harness:
   - Operates inside Frappe Bench or offline (unittest / pytest) without requiring MariaDB.
   - Built-in Mock Registry for standalone unit testing and CI pipelines.
"""

import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    import frappe
    from frappe import _
except ImportError:
    frappe = None
    _ = lambda x: x


# 11 Standard Cost Types Taxonomy
STANDARD_COST_TYPES: Tuple[str, ...] = (
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
    "Other",
)


def flt(val: Any, precision: Optional[int] = 2) -> float:
    """Safe float conversion matching Frappe's flt utility."""
    try:
        res = float(val or 0.0)
    except (ValueError, TypeError):
        res = 0.0
    if precision is not None:
        return round(res, precision)
    return res


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


def _set_field(doc: Any, fieldname: str, value: Any) -> None:
    """Safely sets a field on a Document object, dict, or namespace."""
    if doc is None:
        return
    if isinstance(doc, dict):
        doc[fieldname] = value
    elif hasattr(doc, "set"):
        doc.set(fieldname, value)
    else:
        setattr(doc, fieldname, value)


def normalize_cost_type(ctype: Optional[str]) -> str:
    """Normalizes cost type string against 11 standard types."""
    if not ctype:
        return "Other"
    clean = str(ctype).strip()
    for standard in STANDARD_COST_TYPES:
        if clean.lower() == standard.lower():
            return standard
    # Fuzzy keyword mapping
    lower = clean.lower()
    if "freight" in lower or "cước" in lower:
        return "Freight"
    elif "insurance" in lower or "bảo hiểm" in lower:
        return "Insurance"
    elif "duty" in lower or "thuế nhập" in lower or "thuế xuất" in lower:
        return "Duty"
    elif "tax" in lower or "vat" in lower or "thuế" in lower:
        return "Tax"
    elif "port" in lower or "cảng" in lower or "thc" in lower or "cic" in lower:
        return "Port"
    elif "handling" in lower or "bốc xếp" in lower:
        return "Handling"
    elif "storage" in lower or "kho" in lower or "lưu kho" in lower:
        return "Storage"
    elif "demurrage" in lower or "detention" in lower or "dem" in lower or "det" in lower:
        return "Demurrage/Detention"
    elif "truck" in lower or "vận chuyển" in lower or "kéo container" in lower:
        return "Trucking"
    elif "broker" in lower or "hải quan" in lower or "khai thuê" in lower:
        return "Broker Fee"
    return "Other"


def extract_sales_documents(
    cost_sheet: Optional[Union[Dict[str, Any], Any]] = None,
    case_id: Optional[str] = None,
    sales_docs: Optional[Union[Dict[str, Any], List[Any]]] = None,
) -> Dict[str, List[Any]]:
    """
    Extracts linked Sales Orders, Delivery Notes, and Sales Invoices from:
    1. Direct sales_docs dictionary / list passed by caller.
    2. Trade Cost Sheet's document_links child table.
    3. Frappe ORM queries (when live DB is available).
    """
    extracted: Dict[str, List[Any]] = {
        "sales_orders": [],
        "delivery_notes": [],
        "sales_invoices": [],
    }

    # 1. Direct sales_docs argument
    if sales_docs:
        if isinstance(sales_docs, dict):
            for k in ("sales_orders", "sales_order", "so"):
                if k in sales_docs and isinstance(sales_docs[k], list):
                    extracted["sales_orders"].extend(sales_docs[k])
                elif k in sales_docs and isinstance(sales_docs[k], dict):
                    extracted["sales_orders"].append(sales_docs[k])

            for k in ("delivery_notes", "delivery_note", "dn"):
                if k in sales_docs and isinstance(sales_docs[k], list):
                    extracted["delivery_notes"].extend(sales_docs[k])
                elif k in sales_docs and isinstance(sales_docs[k], dict):
                    extracted["delivery_notes"].append(sales_docs[k])

            for k in ("sales_invoices", "sales_invoice", "si"):
                if k in sales_docs and isinstance(sales_docs[k], list):
                    extracted["sales_invoices"].extend(sales_docs[k])
                elif k in sales_docs and isinstance(sales_docs[k], dict):
                    extracted["sales_invoices"].append(sales_docs[k])
        elif isinstance(sales_docs, (list, tuple)):
            for doc in sales_docs:
                dtype = _get_field(doc, "doctype") or _get_field(doc, "document_type")
                if dtype == "Sales Order":
                    extracted["sales_orders"].append(doc)
                elif dtype == "Delivery Note":
                    extracted["delivery_notes"].append(doc)
                elif dtype == "Sales Invoice":
                    extracted["sales_invoices"].append(doc)

    # 2. Extract from cost_sheet.document_links
    if cost_sheet:
        links = _get_field(cost_sheet, "document_links") or []
        for link in links:
            if not _get_field(link, "is_active", 1):
                continue
            dtype = _get_field(link, "document_type")
            dname = _get_field(link, "document_name")
            if not dname:
                continue

            # Check if document object is embedded or needs to be fetched
            if dtype == "Sales Order":
                if not any(_get_field(d, "name") == dname for d in extracted["sales_orders"]):
                    if frappe and hasattr(frappe, "db") and frappe.db and frappe.db.exists("Sales Order", dname):
                        try:
                            extracted["sales_orders"].append(frappe.get_doc("Sales Order", dname))
                        except Exception:
                            extracted["sales_orders"].append(link)
                    else:
                        extracted["sales_orders"].append(link)
            elif dtype == "Delivery Note":
                if not any(_get_field(d, "name") == dname for d in extracted["delivery_notes"]):
                    if frappe and hasattr(frappe, "db") and frappe.db and frappe.db.exists("Delivery Note", dname):
                        try:
                            extracted["delivery_notes"].append(frappe.get_doc("Delivery Note", dname))
                        except Exception:
                            extracted["delivery_notes"].append(link)
                    else:
                        extracted["delivery_notes"].append(link)
            elif dtype == "Sales Invoice":
                if not any(_get_field(d, "name") == dname for d in extracted["sales_invoices"]):
                    if frappe and hasattr(frappe, "db") and frappe.db and frappe.db.exists("Sales Invoice", dname):
                        try:
                            extracted["sales_invoices"].append(frappe.get_doc("Sales Invoice", dname))
                        except Exception:
                            extracted["sales_invoices"].append(link)
                    else:
                        extracted["sales_invoices"].append(link)

    # 3. Live DB query by Trade Case ID if documents are still empty
    active_case_id = case_id or _get_field(cost_sheet, "trade_case")
    if (
        active_case_id
        and frappe
        and hasattr(frappe, "db")
        and frappe.db
        and not (extracted["sales_orders"] or extracted["delivery_notes"] or extracted["sales_invoices"])
    ):
        try:
            # Check Trade Case for direct Sales Order link
            so_name = frappe.db.get_value("Trade Case", active_case_id, "sales_order")
            if so_name and frappe.db.exists("Sales Order", so_name):
                extracted["sales_orders"].append(frappe.get_doc("Sales Order", so_name))

                # Find Delivery Notes against Sales Order
                dn_names = frappe.db.get_all(
                    "Delivery Note Item",
                    filters={"against_sales_order": so_name, "docstatus": 1},
                    fields=["distinct parent as name"]
                )
                for row in dn_names:
                    if frappe.db.exists("Delivery Note", row.name):
                        extracted["delivery_notes"].append(frappe.get_doc("Delivery Note", row.name))

                # Find Sales Invoices against Sales Order
                si_names = frappe.db.get_all(
                    "Sales Invoice Item",
                    filters={"sales_order": so_name, "docstatus": 1},
                    fields=["distinct parent as name"]
                )
                for row in si_names:
                    if frappe.db.exists("Sales Invoice", row.name):
                        extracted["sales_invoices"].append(frappe.get_doc("Sales Invoice", row.name))
        except Exception:
            pass

    return extracted


def derive_export_revenue(
    sales_docs: Dict[str, List[Any]],
    cost_sheet: Optional[Union[Dict[str, Any], Any]] = None,
    target_currency: Optional[str] = None,
) -> float:
    """
    Derives total realized export revenue in company base currency.
    Hierarchy:
    1. Active Sales Invoices: sum of base_net_total (or net_total * conversion_rate).
       Accounts for returns/credit notes (is_return == 1).
    2. Fallback to Sales Orders: sum of base_net_total (or net_total * conversion_rate).
    3. Fallback to cost_sheet.export_revenue or direct revenue field.
    4. Default 0.0.
    """
    # 1. Sales Invoices
    sis = sales_docs.get("sales_invoices", [])
    if sis:
        total_rev = 0.0
        has_valid_si = False
        for si in sis:
            if _get_field(si, "docstatus") == 2:  # Cancelled
                continue
            is_return = flt(_get_field(si, "is_return", 0)) == 1

            # Determine base net total
            amt = _get_field(si, "base_net_total")
            if amt is None:
                net_tot = _get_field(si, "net_total") or _get_field(si, "grand_total") or _get_field(si, "amount") or 0.0
                rate = _get_field(si, "conversion_rate") or 1.0
                amt = flt(net_tot) * flt(rate)
            else:
                amt = flt(amt)

            if is_return:
                total_rev -= amt
            else:
                total_rev += amt
            has_valid_si = True

        if has_valid_si:
            return flt(total_rev, 2)

    # 2. Sales Orders fallback (uninvoiced shipments)
    sos = sales_docs.get("sales_orders", [])
    if sos:
        total_rev = 0.0
        has_valid_so = False
        for so in sos:
            if _get_field(so, "docstatus") == 2:
                continue
            amt = _get_field(so, "base_net_total")
            if amt is None:
                net_tot = _get_field(so, "net_total") or _get_field(so, "grand_total") or _get_field(so, "amount") or 0.0
                rate = _get_field(so, "conversion_rate") or 1.0
                amt = flt(net_tot) * flt(rate)
            else:
                amt = flt(amt)
            total_rev += amt
            has_valid_so = True

        if has_valid_so:
            return flt(total_rev, 2)

    # 3. Direct cost_sheet field fallback
    if cost_sheet:
        val = _get_field(cost_sheet, "export_revenue")
        if val is not None and flt(val) > 0:
            return flt(val, 2)
        val2 = _get_field(cost_sheet, "revenue")
        if val2 is not None and flt(val2) > 0:
            return flt(val2, 2)

    return 0.0


def derive_export_cogs(
    sales_docs: Dict[str, List[Any]],
    cost_sheet: Optional[Union[Dict[str, Any], Any]] = None,
    target_currency: Optional[str] = None,
) -> float:
    """
    Derives total Cost of Goods Sold (COGS) for shipped export products.
    Hierarchy:
    1. Active Delivery Notes: sum of item inventory valuation (qty * incoming_rate / valuation_rate).
    2. Fallback to Sales Invoices (if update_stock was enabled or valuation rates available).
    3. Fallback to Sales Orders items (if valuation rates available).
    4. Fallback to cost_sheet.export_cogs or direct cogs field.
    5. Default 0.0.
    """
    # 1. Delivery Notes
    dns = sales_docs.get("delivery_notes", [])
    if dns:
        total_cogs = 0.0
        has_items = False
        for dn in dns:
            if _get_field(dn, "docstatus") == 2:
                continue
            # If line items are present
            items = _get_field(dn, "items") or []
            if items:
                for item in items:
                    qty = flt(_get_field(item, "qty") or _get_field(item, "stock_qty") or 0.0)
                    rate = flt(
                        _get_field(item, "incoming_rate")
                        or _get_field(item, "valuation_rate")
                        or _get_field(item, "base_rate")
                        or 0.0
                    )
                    # Master item DB lookup if rate is 0
                    if rate == 0.0 and frappe and hasattr(frappe, "db") and frappe.db:
                        icode = _get_field(item, "item_code")
                        if icode:
                            rate = flt(frappe.db.get_value("Item", icode, "valuation_rate") or 0.0)

                    total_cogs += qty * rate
                    has_items = True
            else:
                # Direct field on DN or document link
                c_val = _get_field(dn, "cogs") or _get_field(dn, "total_cogs")
                if c_val is not None:
                    total_cogs += flt(c_val)
                    has_items = True

        if has_items:
            return flt(total_cogs, 2)

    # 2. Sales Invoices with valuation rates
    sis = sales_docs.get("sales_invoices", [])
    if sis:
        total_cogs = 0.0
        has_items = False
        for si in sis:
            if _get_field(si, "docstatus") == 2:
                continue
            items = _get_field(si, "items") or []
            for item in items:
                qty = flt(_get_field(item, "qty") or _get_field(item, "stock_qty") or 0.0)
                rate = flt(_get_field(item, "incoming_rate") or _get_field(item, "valuation_rate") or 0.0)
                if rate > 0:
                    total_cogs += qty * rate
                    has_items = True

        if has_items:
            return flt(total_cogs, 2)

    # 3. Direct cost_sheet field fallback
    if cost_sheet:
        val = _get_field(cost_sheet, "export_cogs")
        if val is not None and flt(val) > 0:
            return flt(val, 2)
        val2 = _get_field(cost_sheet, "cogs")
        if val2 is not None and flt(val2) > 0:
            return flt(val2, 2)

    return 0.0


def derive_export_logistics_costs(
    cost_sheet: Optional[Union[Dict[str, Any], Any]] = None,
    target_currency: Optional[str] = None,
) -> Tuple[float, float, List[Dict[str, Any]]]:
    """
    Extracts actual and estimated logistics expenses and groups by 11 standard cost types.
    Active filter: Ignores rows where status == 'Cancelled'.
    Returns: (logistics_cost_actual, logistics_cost_estimated, breakdown_list)
    """
    if not cost_sheet:
        return 0.0, 0.0, []

    items = _get_field(cost_sheet, "cost_items") or []
    sheet_fx = flt(_get_field(cost_sheet, "conversion_rate") or 1.0)
    sheet_currency = str(target_currency or _get_field(cost_sheet, "currency") or "USD")

    breakdown_map: Dict[str, float] = {}
    total_actual = 0.0
    total_estimated = 0.0
    has_items = False

    for it in items:
        # Ignore Cancelled items
        if _get_field(it, "status") == "Cancelled":
            continue

        item_fx = flt(_get_field(it, "exchange_rate") or sheet_fx or 1.0)

        # Actual cost in base currency
        base_act = _get_field(it, "base_actual_cost")
        if base_act is not None and flt(base_act) != 0.0:
            actual_amt = flt(base_act)
        else:
            raw_act = flt(_get_field(it, "actual_cost") or 0.0)
            actual_amt = raw_act * item_fx

        # Estimated cost in base currency
        base_est = _get_field(it, "base_estimated_cost")
        if base_est is not None and flt(base_est) != 0.0:
            est_amt = flt(base_est)
        else:
            raw_est = flt(_get_field(it, "estimated_cost") or 0.0)
            est_amt = raw_est * item_fx

        ctype = normalize_cost_type(_get_field(it, "cost_type"))
        breakdown_map[ctype] = flt(breakdown_map.get(ctype, 0.0) + actual_amt, 2)

        total_actual += actual_amt
        total_estimated += est_amt
        has_items = True

    # Fallback to header totals if child items were empty
    if not has_items:
        hdr_act = _get_field(cost_sheet, "export_logistics_cost")
        if hdr_act is None or flt(hdr_act) == 0.0:
            hdr_act = _get_field(cost_sheet, "total_actual_cost") or _get_field(cost_sheet, "logistics_cost") or 0.0
        total_actual = flt(hdr_act)

        hdr_est = _get_field(cost_sheet, "total_estimated_cost") or 0.0
        total_estimated = flt(hdr_est)

    # Format breakdown list
    breakdown = [
        {"label": k, "amount": v, "currency": sheet_currency}
        for k, v in breakdown_map.items()
    ]

    return flt(total_actual, 2), flt(total_estimated, 2), breakdown


def compute_margins(
    revenue: float,
    cogs: float,
    logistics_cost_actual: float,
    logistics_cost_estimated: float = 0.0,
) -> Dict[str, float]:
    """
    Computes all standard margin, profit, and variance figures with division-by-zero protection.
    """
    rev = flt(revenue, 2)
    cg = flt(cogs, 2)
    l_act = flt(logistics_cost_actual, 2)
    l_est = flt(logistics_cost_estimated, 2)

    gross_margin = flt(rev - cg, 2)
    gross_margin_pct = flt((gross_margin / rev * 100.0), 2) if rev > 0 else 0.0

    net_profit = flt(rev - cg - l_act, 2)
    net_margin_pct = flt((net_profit / rev * 100.0), 2) if rev > 0 else 0.0

    variance_amount = flt(l_act - l_est, 2)
    variance_pct = flt((variance_amount / l_est * 100.0), 2) if l_est > 0 else 0.0

    return {
        "revenue": rev,
        "export_revenue": rev,
        "cogs": cg,
        "export_cogs": cg,
        "logistics_cost_actual": l_act,
        "export_logistics_cost": l_act,
        "logistics_cost_estimated": l_est,
        "gross_margin": gross_margin,
        "export_gross_margin": gross_margin,
        "gross_margin_pct": gross_margin_pct,
        "export_gross_margin_pct": gross_margin_pct,
        "net_profit": net_profit,
        "export_net_profit": net_profit,
        "net_margin_pct": net_margin_pct,
        "export_net_margin_pct": net_margin_pct,
        "variance_amount": variance_amount,
        "variance_pct": variance_pct,
    }


def calculate_export_profitability(
    cost_sheet: Optional[Union[Dict[str, Any], Any]] = None,
    sales_docs: Optional[Union[Dict[str, Any], List[Any]]] = None,
    company_currency: Optional[str] = None,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """
    Public API: Calculates export profitability and logistics variance for an export case.

    Supported flexible invocations:
    - calculate_export_profitability(cost_sheet, sales_docs, company_currency)
    - calculate_export_profitability("TC-EXP-001", cost_sheet)
    - calculate_export_profitability(revenue=100000.0, cogs=60000.0, logistics_cost=15000.0)
    """
    # If first argument is string, treat as case_id
    case_id = None
    if isinstance(cost_sheet, str):
        case_id = cost_sheet
        if args and len(args) > 0:
            cost_sheet = args[0]
        else:
            cost_sheet = kwargs.get("cost_sheet")

    # Direct keyword arguments shortcut when NO cost_sheet is provided
    if cost_sheet is None and ("revenue" in kwargs or "export_revenue" in kwargs):
        rev = flt(kwargs.get("revenue", kwargs.get("export_revenue", 0.0)))
        cg = flt(kwargs.get("cogs", kwargs.get("export_cogs", 0.0)))
        l_act = flt(kwargs.get("logistics_cost", kwargs.get("logistics_cost_actual", kwargs.get("export_logistics_cost", 0.0))))
        l_est = flt(kwargs.get("logistics_cost_estimated", 0.0))
        curr = str(company_currency or kwargs.get("currency") or "USD")

        metrics = compute_margins(rev, cg, l_act, l_est)
        metrics["currency"] = curr
        metrics["breakdown"] = kwargs.get("breakdown", [])
        return metrics

    # Determine presentation currency
    curr = str(
        company_currency
        or _get_field(cost_sheet, "currency")
        or kwargs.get("currency")
        or "USD"
    )

    # 1. Extract documents
    docs = extract_sales_documents(cost_sheet=cost_sheet, case_id=case_id, sales_docs=sales_docs)

    # 2. Derive financial components
    if "revenue" in kwargs or "export_revenue" in kwargs:
        revenue = flt(kwargs.get("revenue", kwargs.get("export_revenue", 0.0)))
    else:
        revenue = derive_export_revenue(docs, cost_sheet=cost_sheet, target_currency=curr)

    if "cogs" in kwargs or "export_cogs" in kwargs:
        cogs = flt(kwargs.get("cogs", kwargs.get("export_cogs", 0.0)))
    else:
        cogs = derive_export_cogs(docs, cost_sheet=cost_sheet, target_currency=curr)

    l_act, l_est, breakdown = derive_export_logistics_costs(cost_sheet, target_currency=curr)

    # If explicit keyword overrides exist for logistics
    if "logistics_cost" in kwargs or "export_logistics_cost" in kwargs:
        l_act = flt(kwargs.get("logistics_cost", kwargs.get("export_logistics_cost", 0.0)))
    if "logistics_cost_estimated" in kwargs:
        l_est = flt(kwargs["logistics_cost_estimated"])

    # 3. Compute profitability metrics
    metrics = compute_margins(revenue, cogs, l_act, l_est)
    metrics["currency"] = curr
    metrics["breakdown"] = breakdown
    metrics["sales_documents_count"] = {
        "sales_orders": len(docs.get("sales_orders", [])),
        "delivery_notes": len(docs.get("delivery_notes", [])),
        "sales_invoices": len(docs.get("sales_invoices", [])),
    }

    return metrics


def get_export_profitability_summary(case_id: str) -> Dict[str, Any]:
    """
    Public API: Fetches linked Trade Cost Sheet and Sales Documents for a Trade Case,
    computes full profitability payload, and returns the standardized contract dictionary.
    """
    if not case_id:
        return calculate_export_profitability()

    # 1. Check Mock Registry (for standalone testing / CI)
    if case_id in ExportTracker.mock_registry:
        entry = ExportTracker.mock_registry[case_id]
        return calculate_export_profitability(
            cost_sheet=entry.get("cost_sheet"),
            sales_docs=entry.get("sales_docs"),
            company_currency=entry.get("currency"),
            case_id=case_id,
        )

    cost_sheet = None
    sales_docs = None
    currency = "USD"

    # 2. Live Frappe Database Lookup
    if frappe and hasattr(frappe, "db") and frappe.db:
        try:
            # Lookup linked Trade Cost Sheet
            sheet_names = frappe.db.get_all(
                "Trade Cost Sheet",
                filters={"trade_case": case_id, "docstatus": ["!=", 2]},
                order_by="modified desc",
                limit=1
            )
            if sheet_names:
                cost_sheet = frappe.get_doc("Trade Cost Sheet", sheet_names[0].name)
                currency = cost_sheet.currency or "USD"

            # Check Trade Case for currency
            if frappe.db.exists("Trade Case", case_id):
                tc = frappe.db.get_value("Trade Case", case_id, ["currency"], as_dict=True)
                if tc and tc.get("currency"):
                    currency = tc["currency"]
        except Exception:
            pass

    return calculate_export_profitability(
        cost_sheet=cost_sheet,
        sales_docs=sales_docs,
        company_currency=currency,
        case_id=case_id,
    )


class ExportTracker:
    """
    Object-oriented facade and mock registry manager for Export Cost Tracking & Profitability.
    """
    mock_registry: Dict[str, Dict[str, Any]] = {}

    def __init__(self, company_currency: str = "USD"):
        self.company_currency = company_currency

    def calculate(
        self,
        cost_sheet: Optional[Union[Dict[str, Any], Any]] = None,
        sales_docs: Optional[Union[Dict[str, Any], List[Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Instance method calculating profitability using default currency."""
        return calculate_export_profitability(
            cost_sheet=cost_sheet,
            sales_docs=sales_docs,
            company_currency=self.company_currency,
            **kwargs
        )

    def get_summary(self, case_id: str) -> Dict[str, Any]:
        """Instance method retrieving summary for a case."""
        return get_export_profitability_summary(case_id=case_id)

    @classmethod
    def calculate_static(
        cls,
        revenue: float,
        cogs: float,
        logistics_cost: float,
        currency: str = "USD",
        **kwargs
    ) -> Dict[str, Any]:
        """Convenience static method for direct calculation without instantiation."""
        return calculate_export_profitability(
            revenue=revenue,
            cogs=cogs,
            logistics_cost=logistics_cost,
            currency=currency,
            **kwargs
        )

    @classmethod
    def register_mock_case(
        cls,
        case_id: str,
        cost_sheet: Optional[Dict[str, Any]] = None,
        sales_docs: Optional[Dict[str, Any]] = None,
        currency: str = "USD"
    ) -> None:
        """Registers mock case data in the standalone mock harness."""
        cls.mock_registry[case_id] = {
            "cost_sheet": cost_sheet or {},
            "sales_docs": sales_docs or {},
            "currency": currency,
        }

    @classmethod
    def clear_mock_registry(cls) -> None:
        """Clears all mock registrations."""
        cls.mock_registry.clear()


# Whitelisted API Endpoint for Frappe RPC
if frappe and hasattr(frappe, "whitelist"):
    @frappe.whitelist()
    def get_export_profitability_summary_api(case_id: str) -> Dict[str, Any]:
        """Exposes export profitability to Desk UI and overview cards."""
        return get_export_profitability_summary(case_id=case_id)
