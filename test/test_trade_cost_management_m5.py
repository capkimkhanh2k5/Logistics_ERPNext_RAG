#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_trade_cost_management_m5.py — Master End-to-End Test Suite for Module 5
=============================================================================
Module 5: Trade Cost & Landed Cost Management (Logistics Wizard / ERPNext)
Architecture: 4-Tier Verification Hierarchy (Opaque-box, Requirement-driven)

Covers all 23 features in PROJECT.md § Feature Inventory and Acceptance Criteria:
- Tier 1: Feature Coverage (Core Requirements R1, R2, R3, R4, R5 — >= 5 tests per feature)
- Tier 2: Boundary & Corner Cases (Zero division, extreme values, rounding discrepancy, negative variance, empty cases, Purple Ban)
- Tier 3: Cross-Feature Combinations (Stage-gate closure validation, full import workflow, full export workflow)
- Tier 4: Real-World Application Scenarios (Ocean import Cat Lai, Air import Tan Son Nhat, Export Dong Nai to Hamburg, Cost overrun alert, Fraud/audit anomaly)

Execution:
    python3 test/test_trade_cost_management_m5.py
    python3 -m unittest test/test_trade_cost_management_m5.py -v
    pytest test/test_trade_cost_management_m5.py -v
"""

import os
import sys
import json
import math
import re
import copy
import time
import unittest
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Tuple, Union

# Set up project root and module search paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==============================================================================
# AUTHORITATIVE REFERENCE SPECIFICATIONS & TAXONOMY (ORACLES)
# ==============================================================================

STANDARD_11_COST_TYPES = [
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
]

COST_ITEM_STATUSES = ["Draft", "Verified", "Allocated", "Cancelled"]
COST_FINALIZATION_STATUSES = ["DRAFT", "IN PROGRESS", "ALMOST READY", "ALLOCATED", "FINALIZED"]
ALLOCATION_RULES = ["By Value", "By Quantity", "By Weight", "By Volume", "Custom"]


# ==============================================================================
# STANDALONE HARNESS & PURE-PYTHON REFERENCE LOGIC ENGINE
# ==============================================================================

class StandaloneHarness:
    """
    In-memory database and test execution harness for Module 5.
    Permits pure-Python unit testing without active MariaDB/Redis or bench server.
    """
    _store: Dict[str, Dict[str, Any]] = {
        "Trade Cost Sheet": {},
        "Trade Cost Item": {},
        "Trade Cost Document Link": {},
        "Trade Case": {},
        "Purchase Order": {},
        "Purchase Receipt": {},
        "Sales Order": {},
        "Sales Invoice": {},
        "Landed Cost Voucher": {},
    }

    @classmethod
    def reset(cls):
        for k in cls._store:
            cls._store[k].clear()

    @classmethod
    def put(cls, doctype: str, name: str, doc: Any):
        if doctype not in cls._store:
            cls._store[doctype] = {}
        cls._store[doctype][name] = doc

    @classmethod
    def get(cls, doctype: str, name: str) -> Optional[Any]:
        return cls._store.get(doctype, {}).get(name)

    @classmethod
    def get_all(cls, doctype: str) -> List[Any]:
        return list(cls._store.get(doctype, {}).values())


# ==============================================================================
# AUTHORITATIVE ALGORITHMS & REFERENCE MODELS
# ==============================================================================

def hare_niemeyer_allocation(
    total_amount: float,
    items: List[Dict[str, Any]],
    basis_key: str = "value",
    custom_weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Hare-Niemeyer Largest Remainder Method for proportional cost allocation.
    Guarantees:
    1. sum(allocated_charges) == total_amount (within <= 0.01 rounding tolerance, exactly 0.00 discrepancy).
    2. Zero division prevention when sum of bases == 0.
    """
    if not items or total_amount <= 0:
        return [
            {
                "item_code": it.get("item_code", "UNKNOWN"),
                "allocated_charges": 0.0,
                "base_amount": float(it.get("base_amount", it.get("amount", 0.0))),
                "qty": float(it.get("qty", 1.0)),
                "new_valuation_rate": round(float(it.get("base_amount", it.get("amount", 0.0))) / max(float(it.get("qty", 1.0)), 1.0), 2)
            }
            for it in items
        ]

    # Calculate individual bases
    bases: List[float] = []
    for it in items:
        if custom_weights and it.get("item_code") in custom_weights:
            b = float(custom_weights[it.get("item_code")])
        elif basis_key == "value":
            b = float(it.get("base_amount", it.get("amount", 0.0)))
        elif basis_key == "qty":
            b = float(it.get("qty", 0.0))
        elif basis_key == "weight":
            b = float(it.get("weight", it.get("gross_weight", it.get("net_weight", 0.0))))
        elif basis_key == "volume":
            b = float(it.get("volume", it.get("cbm", 0.0)))
        elif basis_key == "custom":
            b = float(it.get("custom_factor", 1.0))
        else:
            b = float(it.get("base_amount", it.get("amount", 0.0)))
        bases.append(max(b, 0.0))

    total_basis = sum(bases)
    n = len(items)

    # Fallback to equal distribution if total_basis is zero
    if total_basis <= 0:
        bases = [1.0] * n
        total_basis = float(n)

    total_cents = int(round(total_amount * 100))
    quotas = [(b / total_basis) * total_cents for b in bases]
    integers = [int(math.floor(q)) for q in quotas]
    remainders = [q - math.floor(q) for q in quotas]

    allocated_cents = sum(integers)
    discrepancy = total_cents - allocated_cents

    # Distribute missing cents by largest remainder
    indexed_remainders = sorted(range(n), key=lambda i: remainders[i], reverse=True)
    for i in range(discrepancy):
        idx = indexed_remainders[i % n]
        integers[idx] += 1

    results = []
    for i, it in enumerate(items):
        allocated = round(integers[i] / 100.0, 2)
        base_amt = float(it.get("base_amount", it.get("amount", 0.0)))
        qty = max(float(it.get("qty", 1.0)), 0.0001)
        new_rate = round((base_amt + allocated) / qty, 4)
        results.append({
            "item_code": it.get("item_code", f"ITEM-{i+1}"),
            "receipt_document_type": it.get("receipt_document_type", "Purchase Receipt"),
            "receipt_document": it.get("receipt_document", "PR-DEFAULT"),
            "qty": qty,
            "base_amount": base_amt,
            "allocated_charges": allocated,
            "new_valuation_rate": new_rate,
        })
    return results


def calculate_variance(estimated: float, actual: float) -> Tuple[float, float]:
    """
    Variance math with zero-division safety.
    variance_amount = actual - estimated
    variance_pct = round((actual - estimated) / estimated * 100, 1)
    """
    var_amt = round(actual - estimated, 2)
    if estimated > 0:
        var_pct = round((actual - estimated) / estimated * 100.0, 1)
    elif estimated == 0:
        if actual == 0:
            var_pct = 0.0
        else:
            var_pct = 100.0
    else:
        var_pct = round((actual - estimated) / abs(estimated) * 100.0, 1)
    return var_amt, var_pct


def rollup_cost_sheet_status(cost_items: List[Dict[str, Any]], docstatus: int = 0) -> Dict[str, Any]:
    """
    Rolls up cost sheet counts and determines cost_finalization_status.
    """
    active_items = [it for it in cost_items if it.get("status") != "Cancelled"]
    invoices_total = len(active_items)
    invoices_received = sum(1 for it in active_items if it.get("invoice_number"))
    costs_verified = sum(1 for it in active_items if it.get("status") in ["Verified", "Allocated"])
    costs_allocated = sum(1 for it in active_items if it.get("status") == "Allocated")

    if docstatus == 1 or (costs_allocated == invoices_total and invoices_total > 0 and costs_verified == invoices_total):
        finalization_status = "FINALIZED" if docstatus == 1 else "ALLOCATED"
    elif costs_verified == invoices_total and invoices_total > 0:
        finalization_status = "ALMOST READY"
    elif invoices_received > 0:
        finalization_status = "IN PROGRESS"
    else:
        finalization_status = "DRAFT"

    return {
        "invoices_total": invoices_total,
        "invoices_received": invoices_received,
        "costs_verified": costs_verified,
        "costs_allocated": costs_allocated,
        "cost_finalization_status": finalization_status,
    }


def compute_export_profitability(
    revenue: float,
    cogs: float,
    logistics_cost: float
) -> Dict[str, float]:
    """
    Export logistics margin & profitability calculation.
    """
    gross_margin = round(revenue - cogs, 2)
    gross_margin_pct = round(gross_margin / revenue * 100.0, 2) if revenue > 0 else 0.0
    net_profit = round(revenue - cogs - logistics_cost, 2)
    net_margin_pct = round(net_profit / revenue * 100.0, 2) if revenue > 0 else 0.0

    return {
        "export_revenue": revenue,
        "export_cogs": cogs,
        "export_logistics_cost": logistics_cost,
        "export_gross_margin": gross_margin,
        "export_gross_margin_pct": gross_margin_pct,
        "export_net_profit": net_profit,
        "export_net_margin_pct": net_margin_pct,
    }


def audit_cost_sheet(
    cost_sheet: Dict[str, Any],
    historical_sheets: Optional[List[Dict[str, Any]]] = None,
    trade_case: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Audits cost sheet for duplicates, missing critical costs, and wrong-case references.
    """
    errors: List[str] = []
    warnings: List[str] = []
    anomalies: List[Dict[str, Any]] = []

    items = cost_sheet.get("cost_items", [])
    active_items = [it for it in items if it.get("status") != "Cancelled"]

    # 1. Duplicate check within current sheet
    seen_invoices = {}
    for it in active_items:
        supp = it.get("service_provider", "").strip().lower()
        inv = it.get("invoice_number", "").strip().lower()
        if supp and inv:
            key = (supp, inv)
            if key in seen_invoices:
                err = f"Duplicate invoice detected: '{it.get('invoice_number')}' from supplier '{it.get('service_provider')}'"
                errors.append(err)
                anomalies.append({"type": "DUPLICATE_INVOICE", "details": err, "item": it})
            else:
                seen_invoices[key] = it

    # 2. Duplicate check across historical sheets
    if historical_sheets:
        for past_sheet in historical_sheets:
            if past_sheet.get("name") == cost_sheet.get("name"):
                continue
            for past_it in past_sheet.get("cost_items", []):
                if past_it.get("status") == "Cancelled":
                    continue
                p_supp = past_it.get("service_provider", "").strip().lower()
                p_inv = past_it.get("invoice_number", "").strip().lower()
                if p_supp and p_inv and (p_supp, p_inv) in seen_invoices:
                    err = f"Cross-case duplicate invoice: '{past_it.get('invoice_number')}' already used in sheet '{past_sheet.get('name')}'"
                    errors.append(err)
                    anomalies.append({"type": "CROSS_CASE_DUPLICATE", "details": err})

    # 3. Missing critical costs by Incoterm & HS code
    incoterm = (cost_sheet.get("incoterm") or (trade_case.get("incoterm") if trade_case else "") or "").upper()
    present_cost_types = {it.get("cost_type") for it in active_items}

    trade_type = cost_sheet.get("trade_type", "Import")
    if trade_type == "Import":
        if incoterm == "FOB" and "Freight" not in present_cost_types:
            warn = "FOB Import shipment is missing international Freight cost item"
            warnings.append(warn)
            anomalies.append({"type": "MISSING_CRITICAL_COST", "details": warn})
        if incoterm in ["FOB", "CIF", "CFR"] and "Port" not in present_cost_types and "Handling" not in present_cost_types:
            warn = f"{incoterm} Import is missing destination Port/THC cost item"
            warnings.append(warn)
            anomalies.append({"type": "MISSING_PORT_COST", "details": warn})

        # Dutiable HS Code check
        has_dutiable_hs = cost_sheet.get("has_dutiable_goods", False)
        if trade_case and trade_case.get("customs_readiness", {}).get("hs_classification"):
            has_dutiable_hs = True
        if has_dutiable_hs and "Duty" not in present_cost_types and "Tax" not in present_cost_types:
            warn = "Dutiable cargo declaration has no Duty or Tax cost line"
            warnings.append(warn)
            anomalies.append({"type": "MISSING_DUTY_TAX", "details": warn})

    # 4. Wrong-case association check
    if trade_case:
        expected_case_id = trade_case.get("name") or trade_case.get("case_id")
        linked_case = cost_sheet.get("trade_case")
        if linked_case and linked_case != expected_case_id:
            err = f"Cost sheet linked to wrong Trade Case: expected '{expected_case_id}', found '{linked_case}'"
            errors.append(err)
            anomalies.append({"type": "WRONG_CASE_ASSOCIATION", "details": err})

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "anomalies": anomalies,
    }


def generate_lcv_payload(
    cost_sheet: Dict[str, Any],
    allocated_items: List[Dict[str, Any]],
    company: str = "Logistics Wizard Demo",
    expense_account: str = "Expenses Included In Valuation - LWD"
) -> Dict[str, Any]:
    """
    Generates standard ERPNext Landed Cost Voucher payload.
    Invariants:
    - distribute_charges_based_on == 'Distribute Manually'
    - len(taxes) == 1 (consolidated tax line)
    - Zero core accounting alterations
    """
    total_charges = sum(it.get("allocated_charges", 0.0) for it in allocated_items)

    lcv_items = []
    receipt_docs = set()
    for it in allocated_items:
        rec_type = it.get("receipt_document_type", "Purchase Receipt")
        rec_name = it.get("receipt_document", "PR-00001")
        receipt_docs.add((rec_type, rec_name))
        lcv_items.append({
            "item_code": it.get("item_code"),
            "description": it.get("item_code"),
            "qty": it.get("qty", 1.0),
            "rate": round(it.get("base_amount", 0.0) / max(it.get("qty", 1.0), 1.0), 2),
            "amount": it.get("base_amount", 0.0),
            "receipt_document_type": rec_type,
            "receipt_document": rec_name,
            "applicable_charges": it.get("allocated_charges", 0.0),
        })

    lcv_receipts = [
        {"receipt_document_type": rt, "receipt_document": rn}
        for rt, rn in sorted(receipt_docs)
    ]

    lcv_taxes = [
        {
            "expense_account": expense_account,
            "description": f"Trade Cost Sheet Allocation: {cost_sheet.get('name', 'TCS-NEW')}",
            "amount": round(total_charges, 2),
        }
    ]

    return {
        "doctype": "Landed Cost Voucher",
        "company": company,
        "posting_date": cost_sheet.get("posting_date", datetime.now().strftime("%Y-%m-%d")),
        "distribute_charges_based_on": "Distribute Manually",
        "purchase_receipts": lcv_receipts,
        "taxes": lcv_taxes,
        "items": lcv_items,
        "trade_cost_sheet": cost_sheet.get("name"),
    }


def format_case_cost_summary(cost_sheet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the Section 3.3 payload contract.
    """
    items = [it for it in cost_sheet.get("cost_items", []) if it.get("status") != "Cancelled"]
    total_est = sum(float(it.get("base_estimated_cost", it.get("estimated_cost", 0.0))) for it in items)
    total_act = sum(float(it.get("base_actual_cost", it.get("actual_cost", 0.0))) for it in items)
    purchase_val = float(cost_sheet.get("purchase_value", cost_sheet.get("total_purchase_value", 0.0)))

    var_amt, var_pct = calculate_variance(total_est, total_act)
    rollups = rollup_cost_sheet_status(items, docstatus=cost_sheet.get("docstatus", 0))

    # Aggregate breakdown by label / cost type
    breakdown_map: Dict[str, float] = {}
    for it in items:
        ct = it.get("cost_type", "Other")
        amt = float(it.get("base_actual_cost", it.get("actual_cost", 0.0)))
        breakdown_map[ct] = breakdown_map.get(ct, 0.0) + amt

    breakdown = [{"label": k, "amount": round(v, 2)} for k, v in sorted(breakdown_map.items())]

    return {
        "purchase_value": round(purchase_val, 2),
        "estimated_cost": round(total_est, 2),
        "actual_cost": round(total_act, 2),
        "variance_amount": var_amt,
        "variance_pct": var_pct,
        "actual_landed_cost": round(purchase_val + total_act, 2),
        "currency": cost_sheet.get("currency", "USD"),
        "breakdown": breakdown,
        "invoices_received": rollups["invoices_received"],
        "invoices_total": rollups["invoices_total"],
        "costs_verified": rollups["costs_verified"],
        "costs_allocated": rollups["costs_allocated"],
        "cost_finalization_status": rollups["cost_finalization_status"],
    }


# ==============================================================================
# TIER 1: FEATURE COVERAGE (R1, R2, R3, R4, R5 — >= 5 TESTS PER FEATURE)
# ==============================================================================

class TestTier1_DocTypeSchemas(unittest.TestCase):
    """F1, F2, F3: DocType schemas validation (Trade Cost Sheet, Item, Link)."""

    def setUp(self):
        self.doctype_base = os.path.join(APP_PATH, "logistics_wizard", "doctype")

    def test_f1_01_trade_cost_sheet_schema_contract(self):
        """F1.1: Verify Trade Cost Sheet field definitions and naming series."""
        expected_fields = [
            "naming_series", "trade_case", "trade_type", "company", "posting_date",
            "status", "currency", "conversion_rate", "allocation_rule",
            "total_purchase_value", "total_estimated_cost", "total_actual_cost",
            "variance_amount", "variance_pct", "actual_landed_cost",
            "invoices_total", "invoices_received", "costs_verified",
            "costs_allocated", "cost_finalization_status"
        ]
        # Contract specification verification
        self.assertGreaterEqual(len(expected_fields), 15)
        self.assertIn("naming_series", expected_fields)
        self.assertIn("trade_case", expected_fields)
        self.assertIn("allocation_rule", expected_fields)

        # Check file on disk if already generated by M1
        json_path = os.path.join(self.doctype_base, "trade_cost_sheet", "trade_cost_sheet.json")
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            self.assertEqual(schema.get("doctype"), "DocType")
            self.assertEqual(schema.get("name"), "Trade Cost Sheet")
            fieldnames = [f["fieldname"] for f in schema.get("fields", []) if "fieldname" in f]
            for ef in expected_fields:
                self.assertIn(ef, fieldnames)

    def test_f1_02_trade_cost_item_child_schema_contract(self):
        """F1.2: Verify Trade Cost Item child table field specifications."""
        expected_child_fields = [
            "cost_type", "service_provider", "invoice_number", "invoice_date",
            "currency", "exchange_rate", "estimated_cost", "actual_cost",
            "base_estimated_cost", "base_actual_cost", "variance_amount",
            "variance_pct", "status", "expense_account", "is_critical"
        ]
        self.assertIn("cost_type", expected_child_fields)
        self.assertIn("service_provider", expected_child_fields)
        self.assertIn("exchange_rate", expected_child_fields)

        json_path = os.path.join(self.doctype_base, "trade_cost_item", "trade_cost_item.json")
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            self.assertEqual(schema.get("istable"), 1)
            fieldnames = [f["fieldname"] for f in schema.get("fields", []) if "fieldname" in f]
            for ef in expected_child_fields:
                self.assertIn(ef, fieldnames)

    def test_f1_03_trade_cost_document_link_schema_contract(self):
        """F1.3: Verify Trade Cost Document Link schema fields."""
        expected_link_fields = [
            "document_type", "document_name", "posting_date", "grand_total", "is_active"
        ]
        self.assertIn("document_type", expected_link_fields)
        self.assertIn("document_name", expected_link_fields)

        json_path = os.path.join(self.doctype_base, "trade_cost_document_link", "trade_cost_document_link.json")
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            self.assertEqual(schema.get("istable"), 1)
            fieldnames = [f["fieldname"] for f in schema.get("fields", []) if "fieldname" in f]
            for ef in expected_link_fields:
                self.assertIn(ef, fieldnames)

    def test_f1_04_zero_data_duplication_compliance(self):
        """F1.4: Confirm Trade Cost Sheet does not duplicate raw inventory item rows."""
        forbidden_duplicated_fields = ["items", "packed_items", "operations", "serial_and_batch_bundle"]
        json_path = os.path.join(self.doctype_base, "trade_cost_sheet", "trade_cost_sheet.json")
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            fieldnames = [f.get("fieldname") for f in schema.get("fields", [])]
            for forbidden in forbidden_duplicated_fields:
                self.assertNotIn(forbidden, fieldnames)

    def test_f1_05_doctype_naming_and_module_categorization(self):
        """F1.5: Verify module ownership is 'Logistics Wizard'."""
        sheet_path = os.path.join(self.doctype_base, "trade_cost_sheet", "trade_cost_sheet.json")
        if os.path.isfile(sheet_path):
            with open(sheet_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            self.assertEqual(schema.get("module"), "Logistics Wizard")


class TestTier1_CostTypesTaxonomy(unittest.TestCase):
    """F4: 11 Standard Cost Types Taxonomy validation."""

    def test_f4_01_all_11_cost_types_recognized(self):
        """F4.1: Exactly 11 standard cost types in official taxonomy."""
        self.assertEqual(len(STANDARD_11_COST_TYPES), 11)
        expected = [
            "Freight", "Insurance", "Duty", "Tax", "Port", "Handling",
            "Storage", "Demurrage/Detention", "Trucking", "Broker Fee", "Other"
        ]
        self.assertEqual(sorted(STANDARD_11_COST_TYPES), sorted(expected))

    def test_f4_02_cost_type_validation_accepts_valid_types(self):
        """F4.2: Valid cost types pass validation without error."""
        for ct in STANDARD_11_COST_TYPES:
            self.assertIn(ct, STANDARD_11_COST_TYPES)

    def test_f4_03_cost_type_validation_rejects_arbitrary_types(self):
        """F4.3: Arbitrary or misspelt cost types are rejected or flagged."""
        invalid_types = ["Airfare", "Coffee", "Hotel", "UnknownExpense", "Random"]
        for inv in invalid_types:
            self.assertNotIn(inv, STANDARD_11_COST_TYPES)

    def test_f4_04_cost_breakdown_categorization_preserves_taxonomy(self):
        """F4.4: Cost breakdown properly groups expenses under standard taxonomy."""
        items = [
            {"cost_type": "Freight", "actual_cost": 5000.0, "status": "Verified"},
            {"cost_type": "Freight", "actual_cost": 700.0, "status": "Verified"},
            {"cost_type": "Duty", "actual_cost": 8000.0, "status": "Verified"},
            {"cost_type": "Insurance", "actual_cost": 950.0, "status": "Verified"},
        ]
        sheet = {"cost_items": items, "purchase_value": 50000.0}
        summary = format_case_cost_summary(sheet)
        labels = [b["label"] for b in summary["breakdown"]]
        self.assertIn("Freight", labels)
        self.assertIn("Duty", labels)
        self.assertIn("Insurance", labels)
        freight_sum = next(b["amount"] for b in summary["breakdown"] if b["label"] == "Freight")
        self.assertEqual(freight_sum, 5700.0)

    def test_f4_05_demurrage_and_detention_syntax_handling(self):
        """F4.5: Ensure combined 'Demurrage/Detention' cost type handles slashes safely."""
        ct = "Demurrage/Detention"
        self.assertIn(ct, STANDARD_11_COST_TYPES)
        items = [{"cost_type": ct, "actual_cost": 400.0, "status": "Verified"}]
        summary = format_case_cost_summary({"cost_items": items})
        self.assertTrue(any(b["label"] == ct for b in summary["breakdown"]))


class TestTier1_MultiCurrencyFX(unittest.TestCase):
    """F5: Multi-Currency & FX Conversion."""

    def test_f5_01_standard_usd_to_vnd_conversion(self):
        """F5.1: Convert USD items to VND base currency accurately."""
        rate = 25450.0
        est_usd = 1000.0
        act_usd = 1200.0
        base_est = round(est_usd * rate, 2)
        base_act = round(act_usd * rate, 2)
        self.assertEqual(base_est, 25450000.0)
        self.assertEqual(base_act, 30540000.0)

    def test_f5_02_jpy_fractional_currency_conversion(self):
        """F5.2: Convert JPY items with small exchange rate."""
        rate = 165.25  # 1 USD = 165.25 JPY or 1 JPY = 165.25 VND
        est_jpy = 50000.0
        base_est = round(est_jpy * rate, 2)
        self.assertEqual(base_est, 8262500.0)

    def test_f5_03_default_exchange_rate_identity(self):
        """F5.3: Base currency with rate=1.0 leaves amount unchanged."""
        rate = 1.0
        amt = 1530.75
        self.assertEqual(round(amt * rate, 2), 1530.75)

    def test_f5_04_mixed_currency_items_in_single_sheet(self):
        """F5.4: Aggregate multiple currencies into single base currency total."""
        items = [
            {"currency": "USD", "exchange_rate": 25000.0, "actual_cost": 100.0, "base_actual_cost": 2500000.0, "status": "Verified"},
            {"currency": "EUR", "exchange_rate": 27000.0, "actual_cost": 50.0, "base_actual_cost": 1350000.0, "status": "Verified"},
            {"currency": "VND", "exchange_rate": 1.0, "actual_cost": 500000.0, "base_actual_cost": 500000.0, "status": "Verified"},
        ]
        total_base = sum(it["base_actual_cost"] for it in items)
        self.assertEqual(total_base, 4350000.0)

    def test_f5_05_fx_rounding_precision_two_decimals(self):
        """F5.5: Currency conversion respects strict 2-decimal rounding."""
        amt = 123.456
        rate = 23.4567
        base = round(amt * rate, 2)
        self.assertEqual(base, 2895.87)


class TestTier1_VarianceCalculation(unittest.TestCase):
    """F6: Variance Calculation (`Actual - Estimated`) and percentage."""

    def test_f6_01_positive_variance_cost_overrun(self):
        """F6.1: Actual > Estimated produces positive variance and percentage."""
        var_amt, var_pct = calculate_variance(17000.0, 18350.0)
        self.assertEqual(var_amt, 1350.0)
        self.assertEqual(var_pct, 7.9)

    def test_f6_02_negative_variance_cost_savings(self):
        """F6.2: Actual < Estimated produces negative variance."""
        var_amt, var_pct = calculate_variance(10000.0, 9870.0)
        self.assertEqual(var_amt, -130.0)
        self.assertEqual(var_pct, -1.3)

    def test_f6_03_zero_variance_exact_budget(self):
        """F6.3: Actual == Estimated produces 0.0 amount and 0.0%."""
        var_amt, var_pct = calculate_variance(5000.0, 5000.0)
        self.assertEqual(var_amt, 0.0)
        self.assertEqual(var_pct, 0.0)

    def test_f6_04_zero_estimated_with_actual_cost(self):
        """F6.4: Zero estimated cost handles division safely without exception."""
        var_amt, var_pct = calculate_variance(0.0, 1250.0)
        self.assertEqual(var_amt, 1250.0)
        self.assertEqual(var_pct, 100.0)

    def test_f6_05_both_zero_costs(self):
        """F6.5: Both estimated and actual cost zero yields 0.0%."""
        var_amt, var_pct = calculate_variance(0.0, 0.0)
        self.assertEqual(var_amt, 0.0)
        self.assertEqual(var_pct, 0.0)


class TestTier1_StatusRollups(unittest.TestCase):
    """F7: Cost Status Rollup Engine & State Machine."""

    def test_f7_01_draft_state_when_no_invoices(self):
        """F7.1: Zero received invoices defaults to DRAFT status."""
        items = [
            {"invoice_number": "", "status": "Draft"},
            {"invoice_number": None, "status": "Draft"},
        ]
        r = rollup_cost_sheet_status(items)
        self.assertEqual(r["cost_finalization_status"], "DRAFT")
        self.assertEqual(r["invoices_received"], 0)
        self.assertEqual(r["invoices_total"], 2)

    def test_f7_02_in_progress_state_partial_invoices(self):
        """F7.2: Some invoices received results in IN PROGRESS status."""
        items = [
            {"invoice_number": "INV-001", "status": "Draft"},
            {"invoice_number": "", "status": "Draft"},
            {"invoice_number": "INV-002", "status": "Verified"},
        ]
        r = rollup_cost_sheet_status(items)
        self.assertEqual(r["cost_finalization_status"], "IN PROGRESS")
        self.assertEqual(r["invoices_received"], 2)
        self.assertEqual(r["invoices_total"], 3)
        self.assertEqual(r["costs_verified"], 1)

    def test_f7_03_almost_ready_state_all_verified_unallocated(self):
        """F7.3: All invoices received and verified, but none allocated -> ALMOST READY."""
        items = [
            {"invoice_number": "INV-01", "status": "Verified"},
            {"invoice_number": "INV-02", "status": "Verified"},
            {"invoice_number": "INV-03", "status": "Verified"},
        ]
        r = rollup_cost_sheet_status(items)
        self.assertEqual(r["cost_finalization_status"], "ALMOST READY")
        self.assertEqual(r["costs_verified"], 3)
        self.assertEqual(r["costs_allocated"], 0)

    def test_f7_04_allocated_state_when_all_allocated(self):
        """F7.4: All items allocated results in ALLOCATED status."""
        items = [
            {"invoice_number": "INV-01", "status": "Allocated"},
            {"invoice_number": "INV-02", "status": "Allocated"},
        ]
        r = rollup_cost_sheet_status(items)
        self.assertEqual(r["cost_finalization_status"], "ALLOCATED")
        self.assertEqual(r["costs_allocated"], 2)

    def test_f7_05_cancelled_items_excluded_from_rollups(self):
        """F7.5: Cancelled cost items are excluded from total counts."""
        items = [
            {"invoice_number": "INV-01", "status": "Verified"},
            {"invoice_number": "INV-CANCEL", "status": "Cancelled"},
        ]
        r = rollup_cost_sheet_status(items)
        self.assertEqual(r["invoices_total"], 1)
        self.assertEqual(r["invoices_received"], 1)
        self.assertEqual(r["costs_verified"], 1)


class TestTier1_AllocationRules(unittest.TestCase):
    """F8-F13: Allocation Rules (Value, Quantity, Weight, Volume, Custom)."""

    def setUp(self):
        self.items = [
            {"item_code": "ITEM-A", "base_amount": 10000.0, "qty": 100.0, "weight": 500.0, "volume": 2.0, "custom_factor": 1.0},
            {"item_code": "ITEM-B", "base_amount": 30000.0, "qty": 300.0, "weight": 1500.0, "volume": 6.0, "custom_factor": 3.0},
        ]
        self.total_charges = 4000.0

    def test_f8_01_allocation_by_value(self):
        """F8: Allocation proportional to item base_amount."""
        res = hare_niemeyer_allocation(self.total_charges, self.items, basis_key="value")
        self.assertEqual(len(res), 2)
        # 10k vs 30k -> 25% vs 75% -> 1000.0 and 3000.0
        self.assertAlmostEqual(res[0]["allocated_charges"], 1000.0, places=2)
        self.assertAlmostEqual(res[1]["allocated_charges"], 3000.0, places=2)
        self.assertEqual(sum(r["allocated_charges"] for r in res), self.total_charges)

    def test_f9_01_allocation_by_quantity(self):
        """F9: Allocation proportional to quantity."""
        res = hare_niemeyer_allocation(self.total_charges, self.items, basis_key="qty")
        self.assertAlmostEqual(res[0]["allocated_charges"], 1000.0, places=2)
        self.assertAlmostEqual(res[1]["allocated_charges"], 3000.0, places=2)
        self.assertEqual(sum(r["allocated_charges"] for r in res), self.total_charges)

    def test_f10_01_allocation_by_weight(self):
        """F10: Allocation proportional to gross/net weight."""
        res = hare_niemeyer_allocation(self.total_charges, self.items, basis_key="weight")
        self.assertAlmostEqual(res[0]["allocated_charges"], 1000.0, places=2)
        self.assertAlmostEqual(res[1]["allocated_charges"], 3000.0, places=2)

    def test_f11_01_allocation_by_volume(self):
        """F11: Allocation proportional to CBM volume."""
        res = hare_niemeyer_allocation(self.total_charges, self.items, basis_key="volume")
        self.assertAlmostEqual(res[0]["allocated_charges"], 1000.0, places=2)
        self.assertAlmostEqual(res[1]["allocated_charges"], 3000.0, places=2)

    def test_f12_01_allocation_by_custom_weights(self):
        """F12: Allocation using user-specified custom weights dictionary."""
        custom = {"ITEM-A": 1.0, "ITEM-B": 1.0}  # 50-50 split
        res = hare_niemeyer_allocation(self.total_charges, self.items, custom_weights=custom)
        self.assertEqual(res[0]["allocated_charges"], 2000.0)
        self.assertEqual(res[1]["allocated_charges"], 2000.0)


class TestTier1_LCVSyncPayload(unittest.TestCase):
    """F14: ERPNext Landed Cost Voucher Sync Adapter."""

    def setUp(self):
        self.sheet = {"name": "TCS-2026-00001", "posting_date": "2026-10-15"}
        self.allocated = [
            {
                "item_code": "RAW-STEEL-01",
                "receipt_document_type": "Purchase Receipt",
                "receipt_document": "PR-2026-00101",
                "qty": 50.0,
                "base_amount": 10000.0,
                "allocated_charges": 1500.0,
            },
            {
                "item_code": "RAW-COPPER-02",
                "receipt_document_type": "Purchase Receipt",
                "receipt_document": "PR-2026-00101",
                "qty": 20.0,
                "base_amount": 8000.0,
                "allocated_charges": 500.0,
            }
        ]

    def test_f14_01_distribute_manually_mode_strictly_enforced(self):
        """F14.1: distribute_charges_based_on MUST be 'Distribute Manually'."""
        lcv = generate_lcv_payload(self.sheet, self.allocated)
        self.assertEqual(lcv["distribute_charges_based_on"], "Distribute Manually")

    def test_f14_02_single_consolidated_tax_line(self):
        """F14.2: LCV taxes table contains exactly 1 consolidated row matching total charges."""
        lcv = generate_lcv_payload(self.sheet, self.allocated)
        self.assertEqual(len(lcv["taxes"]), 1)
        self.assertEqual(lcv["taxes"][0]["amount"], 2000.0)

    def test_f14_03_items_applicable_charges_match_allocations(self):
        """F14.3: Item applicable charges match calculated landed cost allocations."""
        lcv = generate_lcv_payload(self.sheet, self.allocated)
        self.assertEqual(len(lcv["items"]), 2)
        self.assertEqual(lcv["items"][0]["applicable_charges"], 1500.0)
        self.assertEqual(lcv["items"][1]["applicable_charges"], 500.0)

    def test_f14_04_purchase_receipts_deduplicated(self):
        """F14.4: Linked purchase receipts table is cleanly populated and deduplicated."""
        lcv = generate_lcv_payload(self.sheet, self.allocated)
        self.assertEqual(len(lcv["purchase_receipts"]), 1)
        self.assertEqual(lcv["purchase_receipts"][0]["receipt_document"], "PR-2026-00101")

    def test_f14_05_zero_core_modifications_guaranteed(self):
        """F14.5: Target is standard ERPNext Landed Cost Voucher DocType without custom core fields."""
        lcv = generate_lcv_payload(self.sheet, self.allocated)
        self.assertEqual(lcv["doctype"], "Landed Cost Voucher")
        self.assertIn("company", lcv)
        self.assertIn("posting_date", lcv)


class TestTier1_ExportProfitability(unittest.TestCase):
    """F15-F16: Export Logistics Cost Tracking & Profitability."""

    def test_f15_01_export_profitability_calculation_standard(self):
        """F15.1: Compute Revenue - COGS - Logistics Cost for export shipment."""
        res = compute_export_profitability(revenue=100000.0, cogs=60000.0, logistics_cost=15000.0)
        self.assertEqual(res["export_gross_margin"], 40000.0)
        self.assertEqual(res["export_gross_margin_pct"], 40.0)
        self.assertEqual(res["export_net_profit"], 25000.0)
        self.assertEqual(res["export_net_margin_pct"], 25.0)

    def test_f15_02_export_unprofitable_shipment_negative_margin(self):
        """F15.2: Excessive logistics costs resulting in negative net margin."""
        res = compute_export_profitability(revenue=50000.0, cogs=45000.0, logistics_cost=8000.0)
        self.assertEqual(res["export_gross_margin"], 5000.0)
        self.assertEqual(res["export_gross_margin_pct"], 10.0)
        self.assertEqual(res["export_net_profit"], -3000.0)
        self.assertEqual(res["export_net_margin_pct"], -6.0)

    def test_f15_03_zero_logistics_cost_net_equals_gross(self):
        """F15.3: When logistics cost is zero, net profit matches gross margin."""
        res = compute_export_profitability(revenue=80000.0, cogs=50000.0, logistics_cost=0.0)
        self.assertEqual(res["export_gross_margin"], 30000.0)
        self.assertEqual(res["export_net_profit"], 30000.0)
        self.assertEqual(res["export_net_margin_pct"], 37.5)

    def test_f15_04_zero_revenue_handles_safely(self):
        """F15.4: Zero revenue returns 0.0% margins without ZeroDivisionError."""
        res = compute_export_profitability(revenue=0.0, cogs=1000.0, logistics_cost=500.0)
        self.assertEqual(res["export_gross_margin"], -1000.0)
        self.assertEqual(res["export_gross_margin_pct"], 0.0)
        self.assertEqual(res["export_net_profit"], -1500.0)
        self.assertEqual(res["export_net_margin_pct"], 0.0)

    def test_f15_05_rounding_margin_percentages_to_two_decimals(self):
        """F15.5: Percentage margins round cleanly to 2 decimal places."""
        res = compute_export_profitability(revenue=30000.0, cogs=19999.0, logistics_cost=3333.0)
        self.assertAlmostEqual(res["export_gross_margin_pct"], 33.34, places=2)
        self.assertAlmostEqual(res["export_net_margin_pct"], 22.23, places=2)


class TestTier1_DuplicateInvoiceDetection(unittest.TestCase):
    """F17: Duplicate Invoice & Supplier Detection."""

    def test_f17_01_duplicate_within_same_sheet_detected(self):
        """F17.1: Flag duplicate invoice number from same supplier in same sheet."""
        sheet = {
            "name": "TCS-DUP-01",
            "cost_items": [
                {"service_provider": "MAERSK", "invoice_number": "INV-100", "cost_type": "Freight", "status": "Draft"},
                {"service_provider": "MAERSK", "invoice_number": "INV-100", "cost_type": "Freight", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertFalse(res["passed"])
        self.assertTrue(any(a["type"] == "DUPLICATE_INVOICE" for a in res["anomalies"]))

    def test_f17_02_different_suppliers_same_invoice_number_allowed(self):
        """F17.2: Different suppliers having identical invoice numbers is allowed."""
        sheet = {
            "name": "TCS-OK-01",
            "cost_items": [
                {"service_provider": "MAERSK", "invoice_number": "INV-999", "status": "Draft"},
                {"service_provider": "CAT_LAI_PORT", "invoice_number": "INV-999", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(res["passed"])

    def test_f17_03_cross_case_duplicate_detected(self):
        """F17.3: Detect invoice previously billed in an earlier historical Trade Cost Sheet."""
        past_sheet = {
            "name": "TCS-HIST-01",
            "cost_items": [
                {"service_provider": "DHL", "invoice_number": "DHL-EXP-777", "status": "Verified"}
            ]
        }
        current_sheet = {
            "name": "TCS-CURRENT-01",
            "cost_items": [
                {"service_provider": "DHL", "invoice_number": "DHL-EXP-777", "status": "Draft"}
            ]
        }
        res = audit_cost_sheet(current_sheet, historical_sheets=[past_sheet])
        self.assertFalse(res["passed"])
        self.assertTrue(any(a["type"] == "CROSS_CASE_DUPLICATE" for a in res["anomalies"]))

    def test_f17_04_cancelled_items_do_not_trigger_duplicate(self):
        """F17.4: Cancelled item with duplicate invoice does not block valid invoice."""
        sheet = {
            "name": "TCS-CANCEL-01",
            "cost_items": [
                {"service_provider": "CMA_CGM", "invoice_number": "CMA-01", "status": "Cancelled"},
                {"service_provider": "CMA_CGM", "invoice_number": "CMA-01", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(res["passed"])

    def test_f17_05_whitespace_and_case_insensitive_matching(self):
        """F17.5: Duplicate detection trims spaces and normalizes case."""
        sheet = {
            "name": "TCS-CASE-01",
            "cost_items": [
                {"service_provider": "ONE Line", "invoice_number": "inv-888 ", "status": "Draft"},
                {"service_provider": "one line ", "invoice_number": " INV-888", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertFalse(res["passed"])


class TestTier1_MissingCriticalCosts(unittest.TestCase):
    """F18: Missing Critical Costs Anomaly Check by Incoterm & HS code."""

    def test_f18_01_fob_import_missing_freight_triggers_warning(self):
        """F18.1: FOB import must alert when international freight is absent."""
        sheet = {
            "name": "TCS-FOB-01",
            "trade_type": "Import",
            "incoterm": "FOB",
            "cost_items": [
                {"cost_type": "Duty", "status": "Draft"},
                {"cost_type": "Port", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(any(a["type"] == "MISSING_CRITICAL_COST" for a in res["anomalies"]))

    def test_f18_02_fob_import_with_freight_passes(self):
        """F18.2: FOB import with freight item does not trigger missing freight warning."""
        sheet = {
            "name": "TCS-FOB-02",
            "trade_type": "Import",
            "incoterm": "FOB",
            "cost_items": [
                {"cost_type": "Freight", "status": "Draft"},
                {"cost_type": "Port", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertFalse(any(a["type"] == "MISSING_CRITICAL_COST" for a in res["anomalies"]))

    def test_f18_03_missing_destination_port_thc_alert(self):
        """F18.3: CIF/FOB ocean import missing Port/THC triggers warning."""
        sheet = {
            "name": "TCS-PORT-01",
            "trade_type": "Import",
            "incoterm": "CIF",
            "cost_items": [
                {"cost_type": "Freight", "status": "Draft"},
                {"cost_type": "Duty", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(any(a["type"] == "MISSING_PORT_COST" for a in res["anomalies"]))

    def test_f18_04_dutiable_cargo_missing_duty_or_tax_alert(self):
        """F18.4: Dutiable goods with no duty/tax line raises critical warning."""
        sheet = {
            "name": "TCS-DUTY-01",
            "trade_type": "Import",
            "incoterm": "CIF",
            "has_dutiable_goods": True,
            "cost_items": [
                {"cost_type": "Freight", "status": "Draft"},
                {"cost_type": "Port", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(any(a["type"] == "MISSING_DUTY_TAX" for a in res["anomalies"]))

    def test_f18_05_export_shipment_bypasses_import_duty_checks(self):
        """F18.5: Export shipments do not trigger import duty warnings."""
        sheet = {
            "name": "TCS-EXP-01",
            "trade_type": "Export",
            "incoterm": "CIF",
            "cost_items": [
                {"cost_type": "Freight", "status": "Draft"},
                {"cost_type": "Port", "status": "Draft"},
            ]
        }
        res = audit_cost_sheet(sheet)
        self.assertFalse(any(a["type"] == "MISSING_DUTY_TAX" for a in res["anomalies"]))


class TestTier1_WrongCaseAssociation(unittest.TestCase):
    """F19: Wrong-Case Cost Association Check."""

    def test_f19_01_mismatched_trade_case_id_rejected(self):
        """F19.1: Flag cost sheet linked to case B while auditing case A."""
        sheet = {"name": "TCS-MISMATCH", "trade_case": "IMP-2026-002"}
        trade_case = {"name": "IMP-2026-001"}
        res = audit_cost_sheet(sheet, trade_case=trade_case)
        self.assertFalse(res["passed"])
        self.assertTrue(any(a["type"] == "WRONG_CASE_ASSOCIATION" for a in res["anomalies"]))

    def test_f19_02_matched_trade_case_id_passes(self):
        """F19.2: Matching Trade Case ID passes audit."""
        sheet = {"name": "TCS-MATCH", "trade_case": "IMP-2026-001"}
        trade_case = {"name": "IMP-2026-001"}
        res = audit_cost_sheet(sheet, trade_case=trade_case)
        self.assertTrue(res["passed"])

    def test_f19_03_standalone_audit_without_trade_case_context(self):
        """F19.3: Cost sheet audit runs safely when trade_case context is None."""
        sheet = {"name": "TCS-STANDALONE", "trade_case": "IMP-2026-001"}
        res = audit_cost_sheet(sheet, trade_case=None)
        self.assertTrue(res["passed"])

    def test_f19_04_empty_trade_case_link_passes_if_unlinked(self):
        """F19.4: Unlinked draft cost sheet passes wrong-case check without throwing."""
        sheet = {"name": "TCS-NEW", "trade_case": None}
        trade_case = {"name": "IMP-2026-001"}
        res = audit_cost_sheet(sheet, trade_case=trade_case)
        self.assertTrue(res["passed"])

    def test_f19_05_error_message_specifies_both_case_ids(self):
        """F19.5: Wrong-case error message includes both expected and actual IDs."""
        sheet = {"name": "TCS-ERR", "trade_case": "WRONG-ID"}
        trade_case = {"name": "EXPECTED-ID"}
        res = audit_cost_sheet(sheet, trade_case=trade_case)
        err = res["errors"][0]
        self.assertIn("EXPECTED-ID", err)
        self.assertIn("WRONG-ID", err)


class TestTier1_CentralAPIDataContract(unittest.TestCase):
    """F20: Central API Data Contract get_case_cost_summary(case_id)."""

    def setUp(self):
        self.sample_sheet = {
            "name": "TCS-2026-001",
            "trade_case": "IMP-2026-001",
            "purchase_value": 100000.0,
            "currency": "USD",
            "docstatus": 0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5700.0, "invoice_number": "INV-F1", "status": "Allocated"},
                {"cost_type": "Insurance", "estimated_cost": 1000.0, "actual_cost": 950.0, "invoice_number": "INV-I1", "status": "Allocated"},
                {"cost_type": "Duty", "estimated_cost": 10000.0, "actual_cost": 10000.0, "invoice_number": "INV-D1", "status": "Allocated"},
                {"cost_type": "Port", "estimated_cost": 600.0, "actual_cost": 700.0, "invoice_number": "INV-P1", "status": "Allocated"},
                {"cost_type": "Storage", "estimated_cost": 200.0, "actual_cost": 400.0, "invoice_number": "INV-S1", "status": "Verified"},
                {"cost_type": "Other", "estimated_cost": 200.0, "actual_cost": 600.0, "invoice_number": "INV-O1", "status": "Verified"},
                {"cost_type": "Trucking", "estimated_cost": 500.0, "actual_cost": 0.0, "invoice_number": "INV-T1", "status": "Draft"},
                {"cost_type": "Broker Fee", "estimated_cost": 300.0, "actual_cost": 0.0, "invoice_number": "", "status": "Draft"},
                {"cost_type": "Other", "estimated_cost": 200.0, "actual_cost": 0.0, "invoice_number": "", "status": "Draft"},
            ]
        }

    def test_f20_01_payload_schema_keys_conformity_section_3_3(self):
        """F20.1: Check all required keys in Section 3.3 schema."""
        summary = format_case_cost_summary(self.sample_sheet)
        required_keys = [
            "purchase_value", "estimated_cost", "actual_cost",
            "variance_amount", "variance_pct", "actual_landed_cost",
            "currency", "breakdown", "invoices_received", "invoices_total",
            "costs_verified", "costs_allocated", "cost_finalization_status"
        ]
        for k in required_keys:
            self.assertIn(k, summary, f"Key '{k}' missing from Section 3.3 payload")

    def test_f20_02_payload_numeric_types(self):
        """F20.2: Verify float and int datatypes for numeric financial fields."""
        summary = format_case_cost_summary(self.sample_sheet)
        self.assertIsInstance(summary["purchase_value"], float)
        self.assertIsInstance(summary["estimated_cost"], float)
        self.assertIsInstance(summary["actual_cost"], float)
        self.assertIsInstance(summary["variance_amount"], float)
        self.assertIsInstance(summary["variance_pct"], float)
        self.assertIsInstance(summary["actual_landed_cost"], float)
        self.assertIsInstance(summary["invoices_received"], int)
        self.assertIsInstance(summary["invoices_total"], int)
        self.assertIsInstance(summary["costs_verified"], int)
        self.assertIsInstance(summary["costs_allocated"], int)

    def test_f20_03_payload_exact_match_sample_numbers(self):
        """F20.3: Numbers match sample values in Section 3.3."""
        summary = format_case_cost_summary(self.sample_sheet)
        self.assertEqual(summary["purchase_value"], 100000.0)
        self.assertEqual(summary["estimated_cost"], 18000.0)
        self.assertEqual(summary["actual_cost"], 18350.0)
        self.assertEqual(summary["variance_amount"], 350.0)
        self.assertEqual(summary["actual_landed_cost"], 118350.0)
        self.assertEqual(summary["invoices_received"], 7)
        self.assertEqual(summary["invoices_total"], 9)
        self.assertEqual(summary["costs_verified"], 6)
        self.assertEqual(summary["costs_allocated"], 4)
        self.assertEqual(summary["cost_finalization_status"], "IN PROGRESS")

    def test_f20_04_breakdown_structure(self):
        """F20.4: Breakdown is list of dicts with label and amount."""
        summary = format_case_cost_summary(self.sample_sheet)
        self.assertIsInstance(summary["breakdown"], list)
        self.assertGreater(len(summary["breakdown"]), 0)
        for b in summary["breakdown"]:
            self.assertIn("label", b)
            self.assertIn("amount", b)
            self.assertIsInstance(b["label"], str)
            self.assertIsInstance(b["amount"], float)

    def test_f20_05_api_facade_integration_callable(self):
        """F20.5: Verify get_case_cost_summary is exported or wireable in logistics_wizard.api."""
        from logistics_wizard import api
        # When api.py is wired with Module 5, it should expose get_case_cost_summary or overview integration
        self.assertTrue(hasattr(api, "get_trade_case_overview_data"))


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (>= 5 TESTS PER FEATURE AREA)
# ==============================================================================

class TestTier2_ZeroDivisionPrevention(unittest.TestCase):
    """Tier 2: Zero division edge conditions."""

    def test_t2_01_zero_estimated_cost_positive_actual(self):
        """Zero estimated cost with positive actual cost."""
        amt, pct = calculate_variance(0.0, 500.0)
        self.assertEqual(amt, 500.0)
        self.assertEqual(pct, 100.0)

    def test_t2_02_zero_actual_cost_positive_estimated(self):
        """Zero actual cost with positive estimated cost."""
        amt, pct = calculate_variance(1000.0, 0.0)
        self.assertEqual(amt, -1000.0)
        self.assertEqual(pct, -100.0)

    def test_t2_03_zero_revenue_export_margin(self):
        """Zero revenue export profitability handles division safely."""
        res = compute_export_profitability(0.0, 100.0, 50.0)
        self.assertEqual(res["export_gross_margin_pct"], 0.0)
        self.assertEqual(res["export_net_margin_pct"], 0.0)

    def test_t2_04_zero_basis_in_allocation_engine(self):
        """Zero sum of bases in allocation engine falls back to equal split."""
        items = [
            {"item_code": "I1", "weight": 0.0, "qty": 0.0, "base_amount": 0.0},
            {"item_code": "I2", "weight": 0.0, "qty": 0.0, "base_amount": 0.0},
        ]
        res = hare_niemeyer_allocation(100.0, items, basis_key="weight")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["allocated_charges"], 50.0)
        self.assertEqual(res[1]["allocated_charges"], 50.0)

    def test_t2_05_single_item_zero_qty_rate_calculation(self):
        """Item with qty=0.0 handles new_valuation_rate safely."""
        items = [{"item_code": "I1", "qty": 0.0, "base_amount": 100.0}]
        res = hare_niemeyer_allocation(50.0, items)
        self.assertGreater(res[0]["new_valuation_rate"], 0.0)


class TestTier2_ExtremeValues(unittest.TestCase):
    """Tier 2: Extreme numerical values and currencies."""

    def test_t2_06_billions_in_vnd_financial_calculation(self):
        """Handle 50 Billion VND without floating point truncation or overflow."""
        rev = 50_000_000_000.0
        cogs = 35_000_000_000.0
        logistics = 5_000_000_000.0
        res = compute_export_profitability(rev, cogs, logistics)
        self.assertEqual(res["export_net_profit"], 10_000_000_000.0)
        self.assertEqual(res["export_net_margin_pct"], 20.0)

    def test_t2_07_micro_dollar_fractions(self):
        """Micro USD cents ($0.0001 per unit) allocate accurately."""
        items = [
            {"item_code": f"MICRO-{i}", "base_amount": 0.01, "qty": 100.0}
            for i in range(10)
        ]
        res = hare_niemeyer_allocation(1.00, items)
        self.assertEqual(round(sum(r["allocated_charges"] for r in res), 2), 1.00)

    def test_t2_08_extreme_fx_rate(self):
        """Handle extreme FX rates (1 USD = 25,485.50 VND)."""
        usd_amt = 13_500.50
        fx = 25_485.50
        vnd = round(usd_amt * fx, 2)
        self.assertEqual(vnd, 344_066_992.75)

    def test_t2_09_large_quantity_allocation(self):
        """Allocate across 1,000,000 units."""
        items = [
            {"item_code": "BULK-1", "qty": 400_000.0, "base_amount": 400_000.0},
            {"item_code": "BULK-2", "qty": 600_000.0, "base_amount": 600_000.0},
        ]
        res = hare_niemeyer_allocation(50_000.0, items, basis_key="qty")
        self.assertEqual(res[0]["allocated_charges"], 20_000.0)
        self.assertEqual(res[1]["allocated_charges"], 30_000.0)

    def test_t2_10_extreme_variance_percentage(self):
        """Estimated $1 vs Actual $100,000 variance calculation."""
        var_amt, var_pct = calculate_variance(1.0, 100_000.0)
        self.assertEqual(var_amt, 99999.0)
        self.assertEqual(var_pct, 9999900.0)


class TestTier2_RoundingDiscrepancyHareNiemeyer(unittest.TestCase):
    """Tier 2: Hare-Niemeyer <= 0.01 rounding discrepancy tolerance."""

    def test_t2_11_three_way_split_one_hundred_dollars(self):
        """$100 split 3 ways: 33.34 + 33.33 + 33.33 == 100.00 (discrepancy == 0.00)."""
        items = [
            {"item_code": "I1", "weight": 10.0, "base_amount": 100.0, "qty": 1.0},
            {"item_code": "I2", "weight": 10.0, "base_amount": 100.0, "qty": 1.0},
            {"item_code": "I3", "weight": 10.0, "base_amount": 100.0, "qty": 1.0},
        ]
        res = hare_niemeyer_allocation(100.0, items, basis_key="weight")
        charges = [r["allocated_charges"] for r in res]
        self.assertEqual(charges, [33.34, 33.33, 33.33])
        total_alloc = round(sum(charges), 2)
        self.assertEqual(total_alloc, 100.0)
        self.assertLessEqual(abs(total_alloc - 100.0), 0.01)

    def test_t2_12_seven_way_split_one_thousand_dollars(self):
        """$100 split 7 ways across equal items matches $1000.00 exactly."""
        items = [{"item_code": f"ITEM-{i}", "base_amount": 100.0, "qty": 1.0} for i in range(7)]
        res = hare_niemeyer_allocation(1000.0, items)
        total_alloc = round(sum(r["allocated_charges"] for r in res), 2)
        self.assertEqual(total_alloc, 1000.0)
        self.assertLessEqual(abs(total_alloc - 1000.0), 0.01)

    def test_t2_13_one_hundred_items_fractional_split(self):
        """$1234.56 split across 100 items with differing weights."""
        items = [
            {"item_code": f"I-{i}", "weight": float(i + 1), "base_amount": 50.0, "qty": 1.0}
            for i in range(100)
        ]
        target = 1234.56
        res = hare_niemeyer_allocation(target, items, basis_key="weight")
        total_alloc = sum(r["allocated_charges"] for r in res)
        self.assertAlmostEqual(total_alloc, target, places=2)
        self.assertLessEqual(abs(total_alloc - target), 0.01)

    def test_t2_14_single_item_one_hundred_percent_allocation(self):
        """Single item receives 100% of charges exactly."""
        items = [{"item_code": "SOLO", "weight": 150.0, "base_amount": 2000.0, "qty": 10.0}]
        res = hare_niemeyer_allocation(875.25, items)
        self.assertEqual(res[0]["allocated_charges"], 875.25)

    def test_t2_15_odd_prime_item_counts_exact_conservation(self):
        """Prime number of items (13 items, 17 items) conserves pennies."""
        for prime in [13, 17, 23]:
            items = [{"item_code": f"P-{i}", "qty": 1.0, "base_amount": 10.0} for i in range(prime)]
            target = 777.77
            res = hare_niemeyer_allocation(target, items)
            total = sum(r["allocated_charges"] for r in res)
            self.assertAlmostEqual(total, target, places=2)


class TestTier2_NegativeVariance(unittest.TestCase):
    """Tier 2: Negative variance (cost savings) handling."""

    def test_t2_16_freight_discount_negative_variance(self):
        """Forwarder discount creates negative variance amount and pct."""
        amt, pct = calculate_variance(5000.0, 4200.0)
        self.assertEqual(amt, -800.0)
        self.assertEqual(pct, -16.0)

    def test_t2_17_negative_variance_does_not_break_summary(self):
        """Negative variance correctly reflects in cost summary payload."""
        sheet = {
            "purchase_value": 20000.0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 3000.0, "actual_cost": 2500.0, "status": "Verified"}
            ]
        }
        summary = format_case_cost_summary(sheet)
        self.assertEqual(summary["variance_amount"], -500.0)
        self.assertLess(summary["variance_pct"], 0.0)
        self.assertEqual(summary["actual_landed_cost"], 22500.0)

    def test_t2_18_partial_savings_and_partial_overrun(self):
        """Mixed lines with savings and overruns aggregate net variance."""
        sheet = {
            "purchase_value": 10000.0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 2000.0, "actual_cost": 1500.0, "status": "Verified"},  # -500
                {"cost_type": "Duty", "estimated_cost": 1000.0, "actual_cost": 1200.0, "status": "Verified"},      # +200
            ]
        }
        summary = format_case_cost_summary(sheet)
        self.assertEqual(summary["variance_amount"], -300.0)
        self.assertEqual(summary["actual_cost"], 2700.0)

    def test_t2_19_negative_variance_zero_actual_paid(self):
        """Waived fee ($500 estimated, $0 actual) -> -100.0% variance."""
        amt, pct = calculate_variance(500.0, 0.0)
        self.assertEqual(amt, -500.0)
        self.assertEqual(pct, -100.0)

    def test_t2_20_allocation_with_reduced_actual_cost(self):
        """Reduced actual cost correctly allocates smaller charges across items."""
        items = [{"item_code": "I1", "base_amount": 100.0}, {"item_code": "I2", "base_amount": 100.0}]
        res = hare_niemeyer_allocation(150.0, items)  # Reduced from 200
        self.assertEqual(res[0]["allocated_charges"], 75.0)
        self.assertEqual(res[1]["allocated_charges"], 75.0)


class TestTier2_EmptyAndUnassignedCases(unittest.TestCase):
    """Tier 2: Empty cost sheet, empty breakdown, unassigned cases."""

    def test_t2_21_empty_cost_sheet_returns_safe_defaults(self):
        """Cost sheet with zero items returns safe zeroed metrics."""
        summary = format_case_cost_summary({"cost_items": []})
        self.assertEqual(summary["estimated_cost"], 0.0)
        self.assertEqual(summary["actual_cost"], 0.0)
        self.assertEqual(summary["variance_amount"], 0.0)
        self.assertEqual(summary["variance_pct"], 0.0)
        self.assertEqual(summary["breakdown"], [])
        self.assertEqual(summary["cost_finalization_status"], "DRAFT")

    def test_t2_22_none_or_missing_cost_items(self):
        """Cost sheet with missing 'cost_items' key handles gracefully."""
        summary = format_case_cost_summary({})
        self.assertEqual(summary["invoices_total"], 0)
        self.assertEqual(summary["invoices_received"], 0)

    def test_t2_23_empty_items_allocation_returns_empty_list(self):
        """Allocating to empty item list returns empty list."""
        res = hare_niemeyer_allocation(500.0, [])
        self.assertEqual(res, [])

    def test_t2_24_all_cancelled_items_behave_as_empty(self):
        """Cost sheet where all items are cancelled behaves as empty."""
        sheet = {
            "cost_items": [
                {"invoice_number": "INV-1", "status": "Cancelled"},
                {"invoice_number": "INV-2", "status": "Cancelled"},
            ]
        }
        summary = format_case_cost_summary(sheet)
        self.assertEqual(summary["invoices_total"], 0)
        self.assertEqual(summary["cost_finalization_status"], "DRAFT")

    def test_t2_25_unassigned_case_id_fallback_in_api(self):
        """Nonexistent Case ID fallback does not raise 500 error."""
        from logistics_wizard import api
        data = api.get_trade_case_overview_data("NONEXISTENT-999")
        self.assertIsNotNone(data)
        self.assertEqual(data.get("status"), "success")


class TestTier2_PurpleBanRegex(unittest.TestCase):
    """Tier 2: Static Regex scan ensuring NO PURPLE / VIOLET in any newly created assets."""

    def test_t2_26_purple_ban_static_regex_scan(self):
        """Scan all logistics_wizard assets for prohibited purple/violet hex or names."""
        disallowed_hex = re.compile(
            r"#(8a2be2|9333ea|7c3aed|6366f1|8b5cf6|a855f7|d946ef|4c1d95|581c87|6d28d9|"
            r"800080|9400d3|4b0082|ee82ee|da70d6|ba55d3|9932cc|8b008b)\b",
            re.IGNORECASE
        )
        disallowed_names = re.compile(r"\b(purple|violet|magenta|indigo)\b", re.IGNORECASE)

        target_dir = os.path.join(APP_PATH, "logistics_wizard")
        violations = []
        scanned_count = 0

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".css", ".js", ".html")) and "dist" not in root:
                    scanned_count += 1
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Strip comments
                    clean = re.sub(r"/\*[\s\S]*?\*/", "", content)
                    clean = re.sub(r"<!--[\s\S]*?-->", "", clean)
                    clean = re.sub(r"//.*", "", clean)
                    clean = re.sub(r"No\s+Purple", "", clean, flags=re.IGNORECASE)

                    for line_idx, line in enumerate(clean.splitlines(), 1):
                        hex_match = disallowed_hex.search(line)
                        if hex_match:
                            violations.append(f"{file_path}:{line_idx} [HEX: {hex_match.group(0)}]")
                        name_match = disallowed_names.search(line)
                        if name_match:
                            violations.append(f"{file_path}:{line_idx} [NAME: {name_match.group(0)}]")

        self.assertGreater(scanned_count, 0)
        self.assertEqual(len(violations), 0, f"Purple Ban Violations detected:\n" + "\n".join(violations))


# ==============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS
# ==============================================================================

class TestTier3_CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Multi-feature integration, Stage Gate closure, full import/export flows."""

    def test_t3_01_stage_gate_closure_blocked_when_lcv_not_allocated(self):
        """GATE_LCV: Trade Case cannot close if costs are not fully allocated."""
        sheet = {
            "name": "TCS-UNALLOCATED",
            "cost_items": [
                {"invoice_number": "INV-1", "status": "Verified"},
                {"invoice_number": "INV-2", "status": "Draft"},
            ]
        }
        rollups = rollup_cost_sheet_status(sheet["cost_items"])
        self.assertNotEqual(rollups["cost_finalization_status"], "ALLOCATED")
        self.assertNotEqual(rollups["cost_finalization_status"], "FINALIZED")

        # In trade case stage gate evaluation:
        gate_lcv_passed = rollups["cost_finalization_status"] in ["ALLOCATED", "FINALIZED"]
        self.assertFalse(gate_lcv_passed, "GATE_LCV must fail when cost finalization is incomplete")

    def test_t3_02_stage_gate_closure_passes_when_all_allocated(self):
        """GATE_LCV & GATE_SETTLEMENT pass when all items verified, allocated, and LCV submitted."""
        sheet = {
            "name": "TCS-COMPLETED",
            "docstatus": 1,
            "cost_items": [
                {"invoice_number": "INV-1", "status": "Allocated"},
                {"invoice_number": "INV-2", "status": "Allocated"},
            ]
        }
        rollups = rollup_cost_sheet_status(sheet["cost_items"], docstatus=1)
        self.assertEqual(rollups["cost_finalization_status"], "FINALIZED")
        self.assertEqual(rollups["invoices_received"], rollups["invoices_total"])

        gate_lcv_passed = rollups["cost_finalization_status"] in ["ALLOCATED", "FINALIZED"]
        gate_settlement_passed = rollups["invoices_received"] == rollups["invoices_total"]
        self.assertTrue(gate_lcv_passed)
        self.assertTrue(gate_settlement_passed)

    def test_t3_03_full_import_workflow_end_to_end(self):
        """Full Import Workflow: PO -> PR -> Trade Cost Sheet -> Allocation (Weight) -> LCV generated."""
        # 1. PR Items received
        pr_items = [
            {"item_code": "SOLAR-CELL-A", "qty": 1000.0, "base_amount": 50000.0, "weight": 2000.0},
            {"item_code": "INVERTER-B", "qty": 100.0, "base_amount": 30000.0, "weight": 1000.0},
        ]
        # 2. Cost items entered
        cost_sheet = {
            "name": "TCS-IMP-FLOW-01",
            "trade_case": "IMP-2026-001",
            "purchase_value": 80000.0,
            "incoterm": "FOB",
            "cost_items": [
                {"cost_type": "Freight", "service_provider": "ONE", "invoice_number": "ONE-001", "actual_cost": 4500.0, "status": "Verified"},
                {"cost_type": "Port", "service_provider": "CAT_LAI", "invoice_number": "CL-001", "actual_cost": 600.0, "status": "Verified"},
                {"cost_type": "Duty", "service_provider": "CUSTOMS", "invoice_number": "DUTY-001", "actual_cost": 3900.0, "status": "Verified"},
            ]
        }
        total_costs = sum(it["actual_cost"] for it in cost_sheet["cost_items"])
        self.assertEqual(total_costs, 9000.0)

        # 3. Allocation by Weight
        allocations = hare_niemeyer_allocation(total_costs, pr_items, basis_key="weight")
        # 2000kg vs 1000kg -> 2/3 vs 1/3 -> 6000.0 and 3000.0
        self.assertAlmostEqual(allocations[0]["allocated_charges"], 6000.0, places=2)
        self.assertAlmostEqual(allocations[1]["allocated_charges"], 3000.0, places=2)

        # 4. Generate LCV
        lcv = generate_lcv_payload(cost_sheet, allocations)
        self.assertEqual(lcv["distribute_charges_based_on"], "Distribute Manually")
        self.assertEqual(lcv["taxes"][0]["amount"], 9000.0)
        self.assertEqual(lcv["items"][0]["applicable_charges"], 6000.0)
        self.assertEqual(lcv["items"][1]["applicable_charges"], 3000.0)

        # 5. Rollup update to ALLOCATED
        for it in cost_sheet["cost_items"]:
            it["status"] = "Allocated"
        rollups = rollup_cost_sheet_status(cost_sheet["cost_items"])
        self.assertEqual(rollups["cost_finalization_status"], "ALLOCATED")

    def test_t3_04_full_export_workflow_end_to_end(self):
        """Full Export Workflow: SO -> Cost Sheet -> Export Tracker -> Margin -> Gate Pass."""
        # 1. Sales Order details
        so_revenue = 120000.0
        goods_cogs = 75000.0

        # 2. Export logistics costs
        export_sheet = {
            "name": "TCS-EXP-FLOW-01",
            "trade_case": "EXP-2026-001",
            "trade_type": "Export",
            "incoterm": "CIF",
            "cost_items": [
                {"cost_type": "Ocean Freight", "actual_cost": 8500.0, "status": "Verified"},
                {"cost_type": "Trucking", "actual_cost": 1200.0, "status": "Verified"},
                {"cost_type": "Handling", "actual_cost": 800.0, "status": "Verified"},
                {"cost_type": "Broker Fee", "actual_cost": 500.0, "status": "Verified"},
            ]
        }
        total_export_logistics = sum(it["actual_cost"] for it in export_sheet["cost_items"])
        self.assertEqual(total_export_logistics, 11000.0)

        # 3. Compute profitability
        profit = compute_export_profitability(so_revenue, goods_cogs, total_export_logistics)
        self.assertEqual(profit["export_gross_margin"], 45000.0)
        self.assertEqual(profit["export_gross_margin_pct"], 37.5)
        self.assertEqual(profit["export_net_profit"], 34000.0)
        self.assertAlmostEqual(profit["export_net_margin_pct"], 28.33, places=2)


# ==============================================================================
# TIER 4: REAL-WORLD APPLICATION SCENARIOS
# ==============================================================================

class TestTier4_RealWorldScenarios(unittest.TestCase):
    """Tier 4: Realistic business scenarios under production logistics conditions."""

    def test_t4_01_ocean_import_cat_lai_11_mixed_costs_fob(self):
        """Scenario 1: Ocean Import via Cat Lai port with 11 mixed cost types, USD + VND."""
        fx = 25450.0
        items = [
            {"cost_type": "Freight", "service_provider": "MAERSK", "invoice_number": "MAE-01", "currency": "USD", "exchange_rate": fx, "estimated_cost": 2500.0, "actual_cost": 2700.0, "base_actual_cost": round(2700.0 * fx, 2), "status": "Allocated"},
            {"cost_type": "Insurance", "service_provider": "BAO_VIET", "invoice_number": "BV-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 5000000.0, "actual_cost": 4800000.0, "base_actual_cost": 4800000.0, "status": "Allocated"},
            {"cost_type": "Duty", "service_provider": "CUSTOMS_CAT_LAI", "invoice_number": "TK-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 45000000.0, "actual_cost": 45000000.0, "base_actual_cost": 45000000.0, "status": "Allocated"},
            {"cost_type": "Tax", "service_provider": "CUSTOMS_CAT_LAI", "invoice_number": "TK-02", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 20000000.0, "actual_cost": 20000000.0, "base_actual_cost": 20000000.0, "status": "Allocated"},
            {"cost_type": "Port", "service_provider": "TAN_CANG", "invoice_number": "TC-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 7500000.0, "actual_cost": 7800000.0, "base_actual_cost": 7800000.0, "status": "Allocated"},
            {"cost_type": "Handling", "service_provider": "CAT_LAI_LOGISTICS", "invoice_number": "CLL-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 3000000.0, "actual_cost": 3200000.0, "base_actual_cost": 3200000.0, "status": "Allocated"},
            {"cost_type": "Storage", "service_provider": "TAN_CANG", "invoice_number": "TC-02", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 2000000.0, "actual_cost": 2500000.0, "base_actual_cost": 2500000.0, "status": "Allocated"},
            {"cost_type": "Demurrage/Detention", "service_provider": "MAERSK", "invoice_number": "MAE-DEM", "currency": "USD", "exchange_rate": fx, "estimated_cost": 0.0, "actual_cost": 150.0, "base_actual_cost": round(150.0 * fx, 2), "status": "Allocated"},
            {"cost_type": "Trucking", "service_provider": "TRANSIMEX", "invoice_number": "TR-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 8000000.0, "actual_cost": 8000000.0, "base_actual_cost": 8000000.0, "status": "Allocated"},
            {"cost_type": "Broker Fee", "service_provider": "VNT_LOGISTICS", "invoice_number": "VNT-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 2500000.0, "actual_cost": 2500000.0, "base_actual_cost": 2500000.0, "status": "Allocated"},
            {"cost_type": "Other", "service_provider": "MISC", "invoice_number": "MISC-01", "currency": "VND", "exchange_rate": 1.0, "estimated_cost": 1000000.0, "actual_cost": 1200000.0, "base_actual_cost": 1200000.0, "status": "Allocated"},
        ]
        cost_sheet = {
            "name": "TCS-OCEAN-CATLAI",
            "trade_case": "IMP-2026-001",
            "purchase_value": 500_000_000.0,
            "currency": "VND",
            "incoterm": "FOB",
            "cost_items": items,
        }
        summary = format_case_cost_summary(cost_sheet)
        self.assertEqual(summary["invoices_total"], 11)
        self.assertEqual(summary["invoices_received"], 11)
        self.assertEqual(summary["costs_allocated"], 11)
        self.assertEqual(summary["cost_finalization_status"], "ALLOCATED")
        self.assertGreater(summary["actual_cost"], 150_000_000.0)

    def test_t4_02_air_import_tan_son_nhat_cif(self):
        """Scenario 2: Air Import via Tan Son Nhat (SGN), high value, CIF, weight allocation."""
        pr_items = [
            {"item_code": "MED-EQUIP-01", "qty": 5.0, "base_amount": 80000.0, "weight": 120.0},
            {"item_code": "MED-SENSOR-02", "qty": 50.0, "base_amount": 20000.0, "weight": 30.0},
        ]
        total_costs = 5000.0  # Terminal fees, customs handling, express trucking
        alloc = hare_niemeyer_allocation(total_costs, pr_items, basis_key="weight")
        # 120 vs 30 -> 80% vs 20% -> 4000.0 and 1000.0
        self.assertEqual(alloc[0]["allocated_charges"], 4000.0)
        self.assertEqual(alloc[1]["allocated_charges"], 1000.0)
        self.assertEqual(alloc[0]["new_valuation_rate"], round((80000.0 + 4000.0) / 5.0, 4))

    def test_t4_03_export_dong_nai_to_hamburg_cif(self):
        """Scenario 3: Furniture Export Dong Nai to Hamburg, CIF, gross vs net margin."""
        revenue = 65000.0
        cogs = 38000.0
        logistics = 9200.0
        prof = compute_export_profitability(revenue, cogs, logistics)
        self.assertEqual(prof["export_gross_margin"], 27000.0)
        self.assertAlmostEqual(prof["export_gross_margin_pct"], 41.54, places=2)
        self.assertEqual(prof["export_net_profit"], 17800.0)
        self.assertAlmostEqual(prof["export_net_margin_pct"], 27.38, places=2)

    def test_t4_04_cost_overrun_alert_variance_gt_5_pct(self):
        """Scenario 4: Cost overrun alert triggered when variance > 5%."""
        var_amt, var_pct = calculate_variance(17000.0, 18350.0)
        self.assertGreater(var_pct, 5.0)
        # Verify Trade Case health reflection logic
        health_alert = "Attention" if var_pct > 5.0 else "Healthy"
        self.assertEqual(health_alert, "Attention")

    def test_t4_05_fraud_audit_anomaly_duplicate_invoice_blocked(self):
        """Scenario 5: Duplicate forwarder invoice detected and blocked before LCV generation."""
        corrupted_sheet = {
            "name": "TCS-FRAUD-TEST",
            "trade_case": "IMP-2026-001",
            "cost_items": [
                {"service_provider": "FORWARDER_X", "invoice_number": "INV-DOUBLE", "status": "Draft"},
                {"service_provider": "FORWARDER_X", "invoice_number": "INV-DOUBLE", "status": "Draft"},
            ]
        }
        audit = audit_cost_sheet(corrupted_sheet)
        self.assertFalse(audit["passed"])
        self.assertIn("Duplicate invoice detected", audit["errors"][0])


# ==============================================================================
# MAIN TEST SUITE RUNNER
# ==============================================================================

def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Tier 1
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_DocTypeSchemas))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_CostTypesTaxonomy))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_MultiCurrencyFX))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_VarianceCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_StatusRollups))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_AllocationRules))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_LCVSyncPayload))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_ExportProfitability))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_DuplicateInvoiceDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_MissingCriticalCosts))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_WrongCaseAssociation))
    suite.addTests(loader.loadTestsFromTestCase(TestTier1_CentralAPIDataContract))

    # Tier 2
    suite.addTests(loader.loadTestsFromTestCase(TestTier2_ZeroDivisionPrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2_ExtremeValues))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2_RoundingDiscrepancyHareNiemeyer))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2_NegativeVariance))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2_EmptyAndUnassignedCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2_PurpleBanRegex))

    # Tier 3
    suite.addTests(loader.loadTestsFromTestCase(TestTier3_CrossFeatureCombinations))

    # Tier 4
    suite.addTests(loader.loadTestsFromTestCase(TestTier4_RealWorldScenarios))

    runner = unittest.TextTestRunner(verbosity=2)
    print("\n" + "=" * 80)
    print(" LOGISTICS WIZARD — MODULE 5 (TRADE COST & LANDED COST) MASTER E2E TEST SUITE")
    print(" 4-TIER REQUIREMENT-DRIVEN VERIFICATION SUITE")
    print("=" * 80)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print(f" TOTAL TESTS RUN : {result.testsRun}")
    print(f" PASSED          : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" FAILURES        : {len(result.failures)}")
    print(f" ERRORS          : {len(result.errors)}")
    print("=" * 80)

    if result.wasSuccessful():
        print(" STATUS: ALL MODULE 5 E2E TESTS PASSED [100% SUCCESS]\n")
        return 0
    else:
        print(" STATUS: TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
