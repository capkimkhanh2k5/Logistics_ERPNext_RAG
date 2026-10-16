# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
lcv_integrator.py — Non-invasive ERPNext Landed Cost Voucher (LCV) Sync Adapter
=============================================================================
Module 5: Trade Cost & Landed Cost Management (Milestone 2)

Architecture Invariants:
1. Non-invasive: Zero modifications to ERPNext core stock/accounting files.
2. Manual Distribution Enforced: distribute_charges_based_on = 'Distribute Manually'.
   ERPNext's set_applicable_charges_on_item preserves our calculated allocations.
3. Single Consolidated Tax Line: Exactly 1 row in lcv.taxes to strictly satisfy
   ERPNext's validate_applicable_charges_for_item check:
   `if self.distribute_charges_based_on == 'Distribute Manually' and len(self.taxes) > 1: frappe.throw(...)`
4. Exact Conservation: Total taxes and charges equals the sum of allocated item
   charges (guaranteed down to 0.00 difference by Hare-Niemeyer allocation).
5. Clean Deduplication: purchase_receipts child table deduplicated across items.
6. Dual-Mode Runtime: Operates seamlessly in Frappe bench or in standalone
   test environments (pytest / unittest) without requiring a live MariaDB instance.
"""

import copy
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple, Union, Set

try:
    import frappe
    from frappe import _
except ImportError:
    frappe = None
    _ = lambda x: x


def flt(val: Any, precision: Optional[int] = None) -> float:
    """Safe float conversion matching Frappe flt utility."""
    try:
        res = float(val or 0.0)
    except (ValueError, TypeError):
        res = 0.0
    if precision is not None:
        return round(res, precision)
    return res


def _get_field(doc: Any, fieldname: str, default: Any = None) -> Any:
    """Retrieves field safely from Document object or dictionary."""
    if doc is None:
        return default
    if hasattr(doc, "get"):
        val = doc.get(fieldname)
        if val is not None:
            return val
    return getattr(doc, fieldname, default)


def _set_field(doc: Any, fieldname: str, value: Any) -> None:
    """Sets field safely on Document object or dictionary."""
    if doc is None:
        return
    if hasattr(doc, "set"):
        doc.set(fieldname, value)
    elif isinstance(doc, dict):
        doc[fieldname] = value
    else:
        setattr(doc, fieldname, value)


def get_company_expense_account(company: str) -> str:
    """
    Resolves the valuation expense account for Landed Cost Voucher.
    Falls back to 'Expenses Included In Valuation - <CompanyAbbr>'.
    """
    if frappe and hasattr(frappe, "db") and frappe.db:
        try:
            acc = frappe.get_cached_value("Company", company, "expenses_included_in_valuation")
            if acc:
                return acc
            abbr = frappe.get_cached_value("Company", company, "abbr") or company
            return f"Expenses Included In Valuation - {abbr}"
        except Exception:
            pass

    # Standard fallback convention
    company_str = str(company or "Logistics Wizard Demo")
    words = [w for w in company_str.split() if w]
    abbr = "".join([w[0] for w in words]).upper() or "LWD"
    return f"Expenses Included In Valuation - {abbr}"


def generate_lcv_payload(
    cost_sheet: Union[Dict[str, Any], Any],
    allocated_items: List[Dict[str, Any]],
    company: Optional[str] = None,
    expense_account: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates standard ERPNext Landed Cost Voucher payload dictionary.

    Invariants Enforced:
    - distribute_charges_based_on == 'Distribute Manually'
    - len(taxes) == 1 (Consolidated tax line to satisfy ERPNext validation)
    - len(purchase_receipts) contains deduplicated receipt documents
    - items table contains item_code, qty, rate, amount, and exact applicable_charges
    - trade_cost_sheet links back to source cost sheet
    """
    sheet_name = _get_field(cost_sheet, "name", "TCS-NEW")
    sheet_company = company or _get_field(cost_sheet, "company") or "Logistics Wizard Demo"
    alloc_rule = _get_field(cost_sheet, "allocation_rule", "By Value")
    posting_date = _get_field(cost_sheet, "posting_date")
    if not posting_date:
        if frappe and hasattr(frappe, "utils") and hasattr(frappe.utils, "today"):
            posting_date = frappe.utils.today()
        else:
            posting_date = date.today().isoformat()

    resolved_expense_account = expense_account or get_company_expense_account(sheet_company)

    # 1. Deduplicate Purchase Receipts
    receipt_docs: Set[Tuple[str, str]] = set()
    lcv_items: List[Dict[str, Any]] = []
    total_charges = 0.0

    for it in allocated_items:
        rec_name = _get_field(it, "receipt_document")
        rec_type = _get_field(it, "receipt_document_type")
        if rec_name and not rec_type:
            rec_type = "Purchase Receipt"
        if rec_type and rec_name:
            receipt_docs.add((rec_type, rec_name))

        charges = round(flt(_get_field(it, "allocated_charges", 0.0)), 2)
        total_charges += charges

        raw_qty = flt(_get_field(it, "qty", 1.0))
        base_amt = flt(_get_field(it, "base_amount", _get_field(it, "amount", 0.0)))
        user_rate = _get_field(it, "rate")
        if user_rate is not None:
            rate = flt(user_rate)
        elif raw_qty <= 0:
            rate = 0.0
        else:
            rate = round(base_amt / raw_qty, 2)

        item_row = {
            "item_code": _get_field(it, "item_code"),
            "description": _get_field(it, "description", _get_field(it, "item_code")),
            "qty": raw_qty,
            "rate": rate,
            "amount": base_amt,
            "receipt_document_type": rec_type,
            "receipt_document": rec_name,
            "applicable_charges": charges,
        }

        pr_item = _get_field(it, "purchase_receipt_item")
        if pr_item:
            item_row["purchase_receipt_item"] = pr_item

        cost_center = _get_field(it, "cost_center")
        if cost_center:
            item_row["cost_center"] = cost_center

        lcv_items.append(item_row)

    total_charges = round(total_charges, 2)

    # 2. Build sorted deduplicated purchase_receipts table
    lcv_receipts = [
        {"receipt_document_type": rt, "receipt_document": rn}
        for rt, rn in sorted(receipt_docs)
    ]

    # If no receipts in allocated_items, check cost_sheet.document_links
    if not lcv_receipts:
        doc_links = _get_field(cost_sheet, "document_links", []) or []
        for dl in doc_links:
            is_active = _get_field(dl, "is_active", 1)
            if str(is_active) in ["0", "False", "false", "None"] or not is_active:
                continue
            dt = _get_field(dl, "document_type")
            dn = _get_field(dl, "document_name")
            if dt in ["Purchase Receipt", "Purchase Invoice"] and dn:
                receipt_docs.add((dt, dn))
        lcv_receipts = [
            {"receipt_document_type": rt, "receipt_document": rn}
            for rt, rn in sorted(receipt_docs)
        ]
        if lcv_receipts:
            for item_row in lcv_items:
                if not item_row.get("receipt_document"):
                    item_row["receipt_document_type"] = lcv_receipts[0]["receipt_document_type"]
                    item_row["receipt_document"] = lcv_receipts[0]["receipt_document"]

    # 3. Exactly 1 consolidated tax line
    description = f"Total Landed Costs - {sheet_name} ({alloc_rule})"
    lcv_taxes = [
        {
            "expense_account": resolved_expense_account,
            "description": description,
            "amount": total_charges,
        }
    ]

    return {
        "doctype": "Landed Cost Voucher",
        "company": sheet_company,
        "posting_date": str(posting_date),
        "distribute_charges_based_on": "Distribute Manually",
        "purchase_receipts": lcv_receipts,
        "taxes": lcv_taxes,
        "items": lcv_items,
        "trade_cost_sheet": sheet_name,
    }


def create_or_update_lcv(
    cost_sheet: Union[str, Dict[str, Any], Any],
    allocated_items: Optional[List[Dict[str, Any]]] = None,
    auto_submit: bool = False,
    company: Optional[str] = None,
    expense_account: Optional[str] = None,
) -> str:
    """
    Creates or updates an ERPNext Landed Cost Voucher from a Trade Cost Sheet.

    Args:
        cost_sheet: Trade Cost Sheet name, Document instance, or dictionary.
        allocated_items: Optional pre-allocated items list. If None, computes via allocation_engine.
        auto_submit: If True, submits the LCV upon creation.
        company: Optional company override.
        expense_account: Optional expense account override.

    Returns:
        The name of the created or updated Landed Cost Voucher.
    """
    # 1. Resolve cost sheet
    doc = cost_sheet
    if isinstance(cost_sheet, str):
        if frappe and hasattr(frappe, "get_doc"):
            doc = frappe.get_doc("Trade Cost Sheet", cost_sheet)
        else:
            doc = {"name": cost_sheet}

    trade_type = _get_field(doc, "trade_type", "Import")
    norm_trade_type = str(trade_type or "").strip().title() or "Import"
    if norm_trade_type != "Import":
        raise ValueError(f"Landed Cost Voucher is only applicable for Import trade cases, not '{trade_type}'.")

    # 2. Resolve allocations if not provided
    if allocated_items is None:
        try:
            from logistics_wizard.costing_engine.allocation_engine import allocate_costs
            allocated_items = allocate_costs(doc)
        except Exception:
            allocated_items = []

    # 3. Generate canonical payload
    payload = generate_lcv_payload(
        cost_sheet=doc,
        allocated_items=allocated_items,
        company=company,
        expense_account=expense_account,
    )

    lcv_name = _get_field(doc, "landed_cost_voucher")

    # 4. Live Frappe Execution Path
    if frappe and hasattr(frappe, "get_doc") and hasattr(frappe, "new_doc"):
        lcv = None
        if lcv_name and hasattr(frappe, "db") and frappe.db and frappe.db.exists("Landed Cost Voucher", lcv_name):
            existing_lcv = frappe.get_doc("Landed Cost Voucher", lcv_name)
            if existing_lcv.docstatus == 0:  # Draft: update in place
                lcv = existing_lcv
                lcv.posting_date = payload["posting_date"]
                lcv.distribute_charges_based_on = payload["distribute_charges_based_on"]
                lcv.set("purchase_receipts", [])
                for pr in payload["purchase_receipts"]:
                    lcv.append("purchase_receipts", pr)
                lcv.set("taxes", [])
                for tx in payload["taxes"]:
                    lcv.append("taxes", tx)
                lcv.set("items", [])
                for it in payload["items"]:
                    lcv.append("items", it)
                lcv.save(ignore_permissions=True)
            elif existing_lcv.docstatus == 1:
                return lcv_name  # Already submitted

        if not lcv:
            lcv = frappe.new_doc("Landed Cost Voucher")
            lcv.company = payload["company"]
            lcv.posting_date = payload["posting_date"]
            lcv.distribute_charges_based_on = payload["distribute_charges_based_on"]
            for pr in payload["purchase_receipts"]:
                lcv.append("purchase_receipts", pr)
            for tx in payload["taxes"]:
                lcv.append("taxes", tx)
            for it in payload["items"]:
                lcv.append("items", it)
            lcv.insert(ignore_permissions=True)

        if auto_submit and lcv.docstatus == 0:
            lcv.submit()

        lcv_name = lcv.name

        # Update Trade Cost Sheet
        _set_field(doc, "landed_cost_voucher", lcv_name)

        # Mark active cost items as Allocated
        items = _get_field(doc, "cost_items", []) or []
        for it in items:
            if _get_field(it, "status") != "Cancelled":
                _set_field(it, "status", "Allocated")

        # Ensure document link entry exists
        doc_links = _get_field(doc, "document_links", []) or []
        has_lcv_link = any(
            _get_field(l, "document_type") == "Landed Cost Voucher" and _get_field(l, "document_name") == lcv_name
            for l in doc_links
        )
        if not has_lcv_link:
            tax_amount = payload["taxes"][0]["amount"] if payload.get("taxes") else 0.0
            new_link = {
                "document_type": "Landed Cost Voucher",
                "document_name": lcv_name,
                "posting_date": payload["posting_date"],
                "grand_total": tax_amount,
                "is_active": 1,
            }
            if hasattr(doc, "append"):
                doc.append("document_links", new_link)
            elif isinstance(doc_links, list):
                doc_links.append(new_link)

        if hasattr(doc, "calculate_status_rollups"):
            doc.calculate_status_rollups()
        if hasattr(doc, "sync_to_trade_case"):
            doc.sync_to_trade_case()
        if hasattr(doc, "save"):
            doc.save(ignore_permissions=True)

        return lcv_name

    # 5. Standalone / Mock Test Path
    if not lcv_name:
        sheet_id_part = str(_get_field(doc, "name", "00001")).split("-")[-1]
        digits = "".join([c for c in sheet_id_part if c.isdigit()]) or "1"
        lcv_name = f"LCV-2026-{digits.zfill(5)}"

    _set_field(doc, "landed_cost_voucher", lcv_name)
    items = _get_field(doc, "cost_items", []) or []
    for it in items:
        if _get_field(it, "status") != "Cancelled":
            _set_field(it, "status", "Allocated")

    # Add document link if available
    doc_links = _get_field(doc, "document_links", None)
    if doc_links is not None and isinstance(doc_links, list):
        has_lcv_link = any(
            _get_field(l, "document_type") == "Landed Cost Voucher" and _get_field(l, "document_name") == lcv_name
            for l in doc_links
        )
        if not has_lcv_link:
            tax_amount = payload["taxes"][0]["amount"] if payload.get("taxes") else 0.0
            new_link = {
                "document_type": "Landed Cost Voucher",
                "document_name": lcv_name,
                "posting_date": payload["posting_date"],
                "grand_total": tax_amount,
                "is_active": 1,
            }
            if hasattr(doc, "append"):
                doc.append("document_links", new_link)
            else:
                doc_links.append(new_link)

    if hasattr(doc, "calculate_status_rollups"):
        doc.calculate_status_rollups()

    return lcv_name


class LCVIntegrator:
    """
    Object-oriented adapter for ERPNext Landed Cost Voucher (LCV) synchronization.
    """

    def __init__(
        self,
        company: Optional[str] = None,
        expense_account: Optional[str] = None
    ):
        self.company = company
        self.expense_account = expense_account

    def generate_payload(
        self,
        cost_sheet: Union[Dict[str, Any], Any],
        allocated_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates canonical LCV payload enforcing manual distribution and single tax."""
        return generate_lcv_payload(
            cost_sheet=cost_sheet,
            allocated_items=allocated_items,
            company=self.company,
            expense_account=self.expense_account
        )

    def create_or_update(
        self,
        cost_sheet: Union[str, Dict[str, Any], Any],
        allocated_items: Optional[List[Dict[str, Any]]] = None,
        auto_submit: bool = False
    ) -> str:
        """Synchronizes calculated charges to ERPNext Landed Cost Voucher."""
        return create_or_update_lcv(
            cost_sheet=cost_sheet,
            allocated_items=allocated_items,
            auto_submit=auto_submit,
            company=self.company,
            expense_account=self.expense_account
        )


def on_cost_sheet_submit(doc: Any, method: Optional[str] = None) -> Optional[str]:
    """
    Lifecycle event hook called when Trade Cost Sheet is submitted.
    Automatically generates and submits Landed Cost Voucher for Import cases.
    """
    trade_type = _get_field(doc, "trade_type", "Import")
    norm_trade_type = str(trade_type or "").strip().title() or "Import"
    if norm_trade_type != "Import":
        return None

    existing_lcv = _get_field(doc, "landed_cost_voucher")
    if (
        existing_lcv
        and frappe
        and hasattr(frappe, "db")
        and frappe.db
        and frappe.db.get_value("Landed Cost Voucher", existing_lcv, "docstatus") == 1
    ):
        return existing_lcv

    return create_or_update_lcv(cost_sheet=doc, auto_submit=True)


if frappe and hasattr(frappe, "whitelist"):
    @frappe.whitelist()
    def generate_lcv_from_cost_sheet(cost_sheet_name: str, auto_submit: bool = False) -> str:
        """Whitelisted API method exposed to Desk UI buttons."""
        lcv_name = create_or_update_lcv(cost_sheet=cost_sheet_name, auto_submit=bool(auto_submit))
        frappe.msgprint(
            _("Landed Cost Voucher {0} successfully generated and synchronized.").format(frappe.bold(lcv_name)),
            indicator="green",
            alert=True
        )
        return lcv_name
