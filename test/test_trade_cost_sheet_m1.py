#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_trade_cost_sheet_m1.py — Master Unit Test Suite for Milestone 1
=============================================================================
Module 5: Trade Cost & Landed Cost Management (Logistics Wizard / ERPNext)
Milestone 1: Trade Cost Sheet, Trade Cost Item, Trade Cost Document Link DocTypes

Verifies:
1. DocType JSON schemas (Trade Cost Sheet, Trade Cost Item, Trade Cost Document Link).
2. Standalone execution compatibility (pure Python without active bench/MariaDB).
3. Happy path with positive variance (cost overrun, e.g. +7.9%).
4. Happy path with negative variance (cost savings, e.g. -1.3%).
5. Zero division safety across variance calculations and export margins.
6. Multi-currency exchange rate conversions and 2-decimal precision.
7. 11 standard cost types taxonomy enforcement.
8. Status rollup engine and deterministic state machine transitions (DRAFT -> IN PROGRESS -> ALMOST READY -> ALLOCATED -> FINALIZED).
9. Strict exclusion of Cancelled items from totals, variances, counts, and breakdowns.
10. Export shipment profitability tracking (Gross Margin, Net Margin %, zero revenue protection).
11. Central Section 3.3 API summary payload contract compliance.
12. PURPLE BAN static scan on Desk form script trade_cost_sheet.js.
"""

import os
import sys
import json
import re
import unittest
from datetime import date
from typing import Dict, Any, List

# Setup project root and module paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logistics_wizard.doctype.trade_cost_sheet.trade_cost_sheet import TradeCostSheet, flt
from logistics_wizard.doctype.trade_cost_item.trade_cost_item import TradeCostItem
from logistics_wizard.doctype.trade_cost_document_link.trade_cost_document_link import TradeCostDocumentLink


class TestTradeCostSheetSchemas(unittest.TestCase):
    """Verifies Frappe v15 DocType JSON schemas for M1 DocTypes."""

    def setUp(self):
        self.doctype_base = os.path.join(APP_PATH, "logistics_wizard", "doctype")

    def test_trade_cost_sheet_schema(self):
        """Verify Trade Cost Sheet parent DocType schema properties and field definitions."""
        json_path = os.path.join(self.doctype_base, "trade_cost_sheet", "trade_cost_sheet.json")
        self.assertTrue(os.path.isfile(json_path), f"File not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        self.assertEqual(schema.get("doctype"), "DocType")
        self.assertEqual(schema.get("name"), "Trade Cost Sheet")
        self.assertEqual(schema.get("module"), "Logistics Wizard")
        self.assertEqual(schema.get("autoname"), "naming_series:")

        fieldnames = [f["fieldname"] for f in schema.get("fields", []) if "fieldname" in f]

        expected_fields = [
            "naming_series", "trade_case", "trade_type", "company", "posting_date",
            "status", "currency", "conversion_rate", "allocation_rule",
            "total_purchase_value", "total_estimated_cost", "total_actual_cost",
            "variance_amount", "variance_pct", "actual_landed_cost",
            "invoices_total", "invoices_received", "costs_verified",
            "costs_allocated", "cost_finalization_status",
            "cost_items", "document_links",
            "export_revenue", "export_cogs", "export_logistics_cost",
            "export_gross_margin", "export_gross_margin_pct",
            "export_net_profit", "export_net_margin_pct"
        ]
        for ef in expected_fields:
            self.assertIn(ef, fieldnames, f"Expected field '{ef}' missing in Trade Cost Sheet")

        # Zero data duplication check: raw stock items must not be duplicated
        forbidden = ["items", "packed_items", "operations", "serial_and_batch_bundle"]
        for fld in forbidden:
            self.assertNotIn(fld, fieldnames)

        # Check permissions
        roles = [p.get("role") for p in schema.get("permissions", [])]
        self.assertIn("System Manager", roles)
        self.assertIn("Stock User", roles)
        self.assertIn("Accounts User", roles)

    def test_trade_cost_item_child_schema(self):
        """Verify Trade Cost Item child table schema."""
        json_path = os.path.join(self.doctype_base, "trade_cost_item", "trade_cost_item.json")
        self.assertTrue(os.path.isfile(json_path), f"File not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        self.assertEqual(schema.get("doctype"), "DocType")
        self.assertEqual(schema.get("name"), "Trade Cost Item")
        self.assertEqual(schema.get("module"), "Logistics Wizard")
        self.assertEqual(schema.get("istable"), 1)
        self.assertEqual(schema.get("editable_grid"), 1)
        self.assertEqual(schema.get("permissions"), [])

        fieldnames = [f["fieldname"] for f in schema.get("fields", []) if "fieldname" in f]
        expected_child_fields = [
            "cost_type", "service_provider", "invoice_number", "invoice_date",
            "currency", "exchange_rate", "estimated_cost", "actual_cost",
            "base_estimated_cost", "base_actual_cost", "variance_amount",
            "variance_pct", "status", "expense_account", "is_critical"
        ]
        for ef in expected_child_fields:
            self.assertIn(ef, fieldnames, f"Expected child field '{ef}' missing in Trade Cost Item")

        # Verify 11 cost types options in cost_type field
        ct_field = next(f for f in schema.get("fields", []) if f.get("fieldname") == "cost_type")
        options = [o.strip() for o in ct_field.get("options", "").split("\n") if o.strip()]
        expected_types = [
            "Freight", "Insurance", "Duty", "Tax", "Port", "Handling",
            "Storage", "Demurrage/Detention", "Trucking", "Broker Fee", "Other"
        ]
        self.assertEqual(sorted(options), sorted(expected_types))

    def test_trade_cost_document_link_child_schema(self):
        """Verify Trade Cost Document Link child table schema."""
        json_path = os.path.join(self.doctype_base, "trade_cost_document_link", "trade_cost_document_link.json")
        self.assertTrue(os.path.isfile(json_path), f"File not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        self.assertEqual(schema.get("doctype"), "DocType")
        self.assertEqual(schema.get("name"), "Trade Cost Document Link")
        self.assertEqual(schema.get("istable"), 1)
        self.assertEqual(schema.get("editable_grid"), 1)

        fieldnames = [f["fieldname"] for f in schema.get("fields", []) if "fieldname" in f]
        expected_link_fields = ["document_type", "document_name", "posting_date", "grand_total", "is_active"]
        for ef in expected_link_fields:
            self.assertIn(ef, fieldnames, f"Expected link field '{ef}' missing in Trade Cost Document Link")


class TestTradeCostSheetVarianceAndMath(unittest.TestCase):
    """Verifies variance calculations, landed cost math, and zero-division handling."""

    def test_happy_path_positive_variance_overrun(self):
        """Cost overrun scenario: Estimated $17,000, Actual $18,350 -> Variance $1,350 (+7.9%)."""
        sheet = TradeCostSheet({
            "total_purchase_value": 100000.0,
            "currency": "USD",
            "conversion_rate": 1.0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5700.0, "status": "Verified", "invoice_number": "INV-F01"},
                {"cost_type": "Insurance", "estimated_cost": 1000.0, "actual_cost": 950.0, "status": "Verified", "invoice_number": "INV-I01"},
                {"cost_type": "Duty", "estimated_cost": 9000.0, "actual_cost": 10000.0, "status": "Verified", "invoice_number": "INV-D01"},
                {"cost_type": "Port", "estimated_cost": 800.0, "actual_cost": 700.0, "status": "Verified", "invoice_number": "INV-P01"},
                {"cost_type": "Storage", "estimated_cost": 500.0, "actual_cost": 400.0, "status": "Verified", "invoice_number": "INV-S01"},
                {"cost_type": "Other", "estimated_cost": 700.0, "actual_cost": 600.0, "status": "Verified", "invoice_number": "INV-O01"},
            ]
        })
        sheet.validate()

        self.assertEqual(sheet.total_estimated_cost, 17000.0)
        self.assertEqual(sheet.total_actual_cost, 18350.0)
        self.assertEqual(sheet.variance_amount, 1350.0)
        self.assertEqual(sheet.variance_pct, 7.9)
        self.assertEqual(sheet.actual_landed_cost, 118350.0)

    def test_happy_path_negative_variance_savings(self):
        """Cost savings scenario: Estimated $5,200, Actual $5,130 -> Variance -$70 (-1.3%)."""
        sheet = TradeCostSheet({
            "total_purchase_value": 45000.0,
            "currency": "USD",
            "conversion_rate": 1.0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 3200.0, "actual_cost": 3200.0, "status": "Verified", "invoice_number": "INV-01"},
                {"cost_type": "Insurance", "estimated_cost": 400.0, "actual_cost": 380.0, "status": "Verified", "invoice_number": "INV-02"},
                {"cost_type": "Duty", "estimated_cost": 1150.0, "actual_cost": 1100.0, "status": "Verified", "invoice_number": "INV-03"},
                {"cost_type": "Port", "estimated_cost": 350.0, "actual_cost": 350.0, "status": "Verified", "invoice_number": "INV-04"},
                {"cost_type": "Broker Fee", "estimated_cost": 100.0, "actual_cost": 100.0, "status": "Verified", "invoice_number": "INV-05"},
            ]
        })
        sheet.validate()

        self.assertEqual(sheet.total_estimated_cost, 5200.0)
        self.assertEqual(sheet.total_actual_cost, 5130.0)
        self.assertEqual(sheet.variance_amount, -70.0)
        self.assertEqual(sheet.variance_pct, -1.3)
        self.assertEqual(sheet.actual_landed_cost, 50130.0)

    def test_zero_variance_exact_budget(self):
        """Exact budget scenario: Actual == Estimated -> Variance $0.00 (0.0%)."""
        sheet = TradeCostSheet({
            "total_purchase_value": 20000.0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 2500.0, "actual_cost": 2500.0, "status": "Verified", "invoice_number": "INV-1"}
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.variance_amount, 0.0)
        self.assertEqual(sheet.variance_pct, 0.0)

    def test_zero_division_safety(self):
        """Zero estimated cost must not raise ZeroDivisionError and bounded to 100.0% or 0.0%."""
        # 1. Zero estimated, positive actual
        sheet1 = TradeCostSheet({
            "total_purchase_value": 10000.0,
            "cost_items": [
                {"cost_type": "Handling", "estimated_cost": 0.0, "actual_cost": 1250.0, "status": "Verified", "invoice_number": "INV-H1"}
            ]
        })
        sheet1.validate()
        self.assertEqual(sheet1.variance_amount, 1250.0)
        self.assertEqual(sheet1.variance_pct, 100.0)
        self.assertEqual(sheet1.cost_items[0].variance_pct, 100.0)

        # 2. Both zero estimated and zero actual
        sheet2 = TradeCostSheet({
            "total_purchase_value": 10000.0,
            "cost_items": [
                {"cost_type": "Storage", "estimated_cost": 0.0, "actual_cost": 0.0, "status": "Draft"}
            ]
        })
        sheet2.validate()
        self.assertEqual(sheet2.variance_amount, 0.0)
        self.assertEqual(sheet2.variance_pct, 0.0)
        self.assertEqual(sheet2.cost_items[0].variance_pct, 0.0)

        # 3. Completely empty cost items list
        sheet3 = TradeCostSheet({"total_purchase_value": 5000.0, "cost_items": []})
        sheet3.validate()
        self.assertEqual(sheet3.total_estimated_cost, 0.0)
        self.assertEqual(sheet3.total_actual_cost, 0.0)
        self.assertEqual(sheet3.variance_amount, 0.0)
        self.assertEqual(sheet3.variance_pct, 0.0)
        self.assertEqual(sheet3.actual_landed_cost, 5000.0)


class TestMultiCurrencyFX(unittest.TestCase):
    """Verifies multi-currency conversions and 2-decimal rounding."""

    def test_standard_usd_to_vnd_conversion(self):
        """Convert USD items to VND base currency accurately."""
        rate = 25450.0
        sheet = TradeCostSheet({
            "currency": "VND",
            "conversion_rate": rate,
            "total_purchase_value": 500000000.0,
            "cost_items": [
                {
                    "cost_type": "Freight",
                    "currency": "USD",
                    "exchange_rate": rate,
                    "estimated_cost": 1000.0,
                    "actual_cost": 1200.0,
                    "status": "Verified",
                    "invoice_number": "INV-USD-1"
                }
            ]
        })
        sheet.validate()

        item = sheet.cost_items[0]
        self.assertEqual(item.base_estimated_cost, 25450000.0)
        self.assertEqual(item.base_actual_cost, 30540000.0)
        self.assertEqual(item.variance_amount, 5090000.0)
        self.assertEqual(item.variance_pct, 20.0)
        self.assertEqual(sheet.total_actual_cost, 30540000.0)

    def test_mixed_currency_aggregation(self):
        """Aggregate USD, EUR, and VND lines in a single sheet."""
        sheet = TradeCostSheet({
            "currency": "VND",
            "conversion_rate": 1.0,
            "total_purchase_value": 1000000.0,
            "cost_items": [
                {"cost_type": "Freight", "currency": "USD", "exchange_rate": 25000.0, "actual_cost": 100.0, "status": "Verified", "invoice_number": "INV-1"},
                {"cost_type": "Insurance", "currency": "EUR", "exchange_rate": 27000.0, "actual_cost": 50.0, "status": "Verified", "invoice_number": "INV-2"},
                {"cost_type": "Handling", "currency": "VND", "exchange_rate": 1.0, "actual_cost": 500000.0, "status": "Verified", "invoice_number": "INV-3"},
            ]
        })
        sheet.validate()

        # 100 * 25k (2.5M) + 50 * 27k (1.35M) + 500k = 4,350,000 VND
        self.assertEqual(sheet.total_actual_cost, 4350000.0)

    def test_default_rate_fallback(self):
        """Item with unspecified or zero exchange_rate inherits sheet conversion_rate."""
        sheet = TradeCostSheet({
            "conversion_rate": 25000.0,
            "cost_items": [
                {"cost_type": "Freight", "exchange_rate": 0.0, "actual_cost": 10.0, "status": "Draft"}
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.cost_items[0].exchange_rate, 25000.0)
        self.assertEqual(sheet.cost_items[0].base_actual_cost, 250000.0)


class TestStatusRollupStateMachine(unittest.TestCase):
    """Verifies invoice count rollups, verification status, and state transitions."""

    def test_state_draft_when_no_invoices(self):
        """No received invoices results in DRAFT state."""
        sheet = TradeCostSheet({
            "cost_items": [
                {"cost_type": "Freight", "invoice_number": "", "status": "Draft"},
                {"cost_type": "Insurance", "invoice_number": None, "status": "Draft"},
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.invoices_total, 2)
        self.assertEqual(sheet.invoices_received, 0)
        self.assertEqual(sheet.costs_verified, 0)
        self.assertEqual(sheet.costs_allocated, 0)
        self.assertEqual(sheet.cost_finalization_status, "DRAFT")

    def test_state_in_progress_partial_invoices(self):
        """Some invoices received or verified -> IN PROGRESS."""
        sheet = TradeCostSheet({
            "cost_items": [
                {"cost_type": "Freight", "invoice_number": "INV-001", "status": "Draft"},
                {"cost_type": "Insurance", "invoice_number": "", "status": "Draft"},
                {"cost_type": "Duty", "invoice_number": "INV-002", "status": "Verified"},
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.invoices_total, 3)
        self.assertEqual(sheet.invoices_received, 2)
        self.assertEqual(sheet.costs_verified, 1)
        self.assertEqual(sheet.costs_allocated, 0)
        self.assertEqual(sheet.cost_finalization_status, "IN PROGRESS")

    def test_state_almost_ready_all_verified_unallocated(self):
        """All invoices received and verified, but none allocated -> ALMOST READY."""
        sheet = TradeCostSheet({
            "cost_items": [
                {"cost_type": "Freight", "invoice_number": "INV-1", "status": "Verified"},
                {"cost_type": "Insurance", "invoice_number": "INV-2", "status": "Verified"},
                {"cost_type": "Port", "invoice_number": "INV-3", "status": "Verified"},
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.invoices_total, 3)
        self.assertEqual(sheet.invoices_received, 3)
        self.assertEqual(sheet.costs_verified, 3)
        self.assertEqual(sheet.costs_allocated, 0)
        self.assertEqual(sheet.cost_finalization_status, "ALMOST READY")

    def test_state_allocated_when_all_allocated_docstatus_0(self):
        """All items allocated with draft sheet -> ALLOCATED."""
        sheet = TradeCostSheet({
            "docstatus": 0,
            "status": "Draft",
            "cost_items": [
                {"cost_type": "Freight", "invoice_number": "INV-1", "status": "Allocated"},
                {"cost_type": "Duty", "invoice_number": "INV-2", "status": "Allocated"},
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.invoices_total, 2)
        self.assertEqual(sheet.costs_allocated, 2)
        self.assertEqual(sheet.cost_finalization_status, "ALLOCATED")

    def test_state_finalized_when_all_allocated_and_submitted(self):
        """All items allocated with submitted or finalized sheet -> FINALIZED."""
        sheet = TradeCostSheet({
            "docstatus": 1,
            "status": "Submitted",
            "cost_items": [
                {"cost_type": "Freight", "invoice_number": "INV-1", "status": "Allocated"},
                {"cost_type": "Duty", "invoice_number": "INV-2", "status": "Allocated"},
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.cost_finalization_status, "FINALIZED")

    def test_cancelled_items_strictly_excluded(self):
        """Cancelled items are excluded from totals, counts, variance, and breakdown."""
        sheet = TradeCostSheet({
            "total_purchase_value": 10000.0,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 2000.0, "actual_cost": 2100.0, "status": "Verified", "invoice_number": "INV-OK"},
                {"cost_type": "Storage", "estimated_cost": 5000.0, "actual_cost": 9999.0, "status": "Cancelled", "invoice_number": "INV-CANCEL"},
            ]
        })
        sheet.validate()

        # Totals should only reflect Freight ($2,000 / $2,100)
        self.assertEqual(sheet.total_estimated_cost, 2000.0)
        self.assertEqual(sheet.total_actual_cost, 2100.0)
        self.assertEqual(sheet.variance_amount, 100.0)
        self.assertEqual(sheet.invoices_total, 1)
        self.assertEqual(sheet.invoices_received, 1)

        # Breakdown must not contain Storage
        breakdown = sheet.get_breakdown()
        labels = [b["label"] for b in breakdown]
        self.assertIn("Freight", labels)
        self.assertNotIn("Storage", labels)


class TestTradeCostItemController(unittest.TestCase):
    """Verifies Trade Cost Item controller validations and methods."""

    def test_11_standard_cost_types_allowed(self):
        """Ensure all 11 cost types pass validation."""
        for ct in TradeCostItem.COST_TYPES:
            item = TradeCostItem({"cost_type": ct, "status": "Draft", "estimated_cost": 100.0})
            item.validate()
            self.assertEqual(item.cost_type, ct)

    def test_invalid_cost_type_raises_error(self):
        """Invalid cost type must raise ValueError."""
        item = TradeCostItem({"cost_type": "UnknownExpense", "status": "Draft"})
        with self.assertRaises(ValueError):
            item.validate()

    def test_invalid_status_raises_error(self):
        """Invalid status must raise ValueError."""
        item = TradeCostItem({"cost_type": "Freight", "status": "InvalidStatus"})
        with self.assertRaises(ValueError):
            item.validate()

    def test_amount_alias_sync(self):
        """estimated_amount and actual_amount sync with estimated_cost and actual_cost."""
        item = TradeCostItem({
            "cost_type": "Freight",
            "estimated_amount": 1500.0,
            "actual_amount": 1650.0,
            "exchange_rate": 1.0,
            "status": "Verified"
        })
        item.validate()
        self.assertEqual(item.estimated_cost, 1500.0)
        self.assertEqual(item.actual_cost, 1650.0)
        self.assertEqual(item.base_estimated_cost, 1500.0)
        self.assertEqual(item.estimated_amount_base, 1500.0)
        self.assertEqual(item.base_actual_cost, 1650.0)
        self.assertEqual(item.actual_amount_base, 1650.0)

    def test_helper_inspection_methods(self):
        """Test has_invoice, is_verified, is_allocated, is_cancelled."""
        it1 = TradeCostItem({"cost_type": "Freight", "invoice_number": "INV-1", "status": "Draft"})
        self.assertTrue(it1.has_invoice())
        self.assertFalse(it1.is_verified())

        it2 = TradeCostItem({"cost_type": "Freight", "invoice_number": "INV-2", "status": "Verified"})
        self.assertTrue(it2.is_verified())
        self.assertFalse(it2.is_allocated())

        it3 = TradeCostItem({"cost_type": "Freight", "invoice_number": "INV-3", "status": "Allocated"})
        self.assertTrue(it3.is_verified())
        self.assertTrue(it3.is_allocated())

        it4 = TradeCostItem({"cost_type": "Freight", "invoice_number": "INV-4", "status": "Cancelled"})
        self.assertFalse(it4.has_invoice())
        self.assertTrue(it4.is_cancelled())


class TestTradeCostDocumentLinkController(unittest.TestCase):
    """Verifies Trade Cost Document Link controller validations and party detection."""

    def test_allowed_document_types(self):
        """Allowed document types pass validation."""
        for dt in TradeCostDocumentLink.ALLOWED_DOC_TYPES:
            link = TradeCostDocumentLink({"document_type": dt, "document_name": "DOC-001"})
            link.validate()
            self.assertEqual(link.document_type, dt)

    def test_invalid_document_type_raises_error(self):
        """Invalid document type raises ValueError."""
        link = TradeCostDocumentLink({"document_type": "InvalidDocType", "document_name": "DOC-001"})
        with self.assertRaises(ValueError):
            link.validate()

    def test_missing_document_name_raises_error(self):
        """Missing document name raises ValueError."""
        link = TradeCostDocumentLink({"document_type": "Purchase Receipt", "document_name": ""})
        with self.assertRaises(ValueError):
            link.validate()

    def test_party_metadata_auto_set(self):
        """Party type is auto set based on ERP document convention."""
        pr = TradeCostDocumentLink({"document_type": "Purchase Receipt", "document_name": "PR-01"})
        pr.validate()
        self.assertEqual(pr.party_type, "Supplier")
        self.assertTrue(pr.is_import_document())
        self.assertFalse(pr.is_export_document())

        so = TradeCostDocumentLink({"document_type": "Sales Order", "document_name": "SO-01"})
        so.validate()
        self.assertEqual(so.party_type, "Customer")
        self.assertTrue(so.is_export_document())
        self.assertFalse(so.is_import_document())

        lcv = TradeCostDocumentLink({"document_type": "Landed Cost Voucher", "document_name": "LCV-01"})
        lcv.validate()
        self.assertIsNone(lcv.party_type)
        self.assertTrue(lcv.is_lcv())


class TestExportProfitabilityAnalysis(unittest.TestCase):
    """Verifies export margin, profit, and zero-revenue handling."""

    def test_standard_export_margin(self):
        """Standard export shipment margin calculation."""
        sheet = TradeCostSheet({
            "trade_type": "Export",
            "export_revenue": 100000.0,
            "export_cogs": 60000.0,
            "cost_items": [
                {"cost_type": "Trucking", "actual_cost": 5000.0, "status": "Verified"},
                {"cost_type": "Freight", "actual_cost": 8000.0, "status": "Verified"},
                {"cost_type": "Broker Fee", "actual_cost": 2000.0, "status": "Verified"},
            ]
        })
        sheet.validate()

        self.assertEqual(sheet.export_logistics_cost, 15000.0)
        self.assertEqual(sheet.export_gross_margin, 40000.0)
        self.assertEqual(sheet.export_gross_margin_pct, 40.0)
        self.assertEqual(sheet.export_net_profit, 25000.0)
        self.assertEqual(sheet.export_net_margin_pct, 25.0)

    def test_zero_revenue_export_margin_safety(self):
        """Zero revenue export must produce 0.0% margins without ZeroDivisionError."""
        sheet = TradeCostSheet({
            "trade_type": "Export",
            "export_revenue": 0.0,
            "export_cogs": 0.0,
            "cost_items": [
                {"cost_type": "Port", "actual_cost": 500.0, "status": "Verified"}
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.export_gross_margin_pct, 0.0)
        self.assertEqual(sheet.export_net_margin_pct, 0.0)
        self.assertEqual(sheet.export_net_profit, -500.0)


class TestCentralAPIDataContract(unittest.TestCase):
    """Verifies payload conforming to Section 3.3 in todoTradeCase.md and PROJECT.md § 5."""

    def test_payload_schema_and_types(self):
        """Verifies all 13 keys and their types."""
        sheet = TradeCostSheet({
            "total_purchase_value": 45000.0,
            "currency": "USD",
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 3200.0, "actual_cost": 3200.0, "status": "Verified", "invoice_number": "INV-1"},
                {"cost_type": "Insurance", "estimated_cost": 380.0, "actual_cost": 380.0, "status": "Verified", "invoice_number": "INV-2"},
                {"cost_type": "Duty", "estimated_cost": 1100.0, "actual_cost": 1100.0, "status": "Verified", "invoice_number": "INV-3"},
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        expected_keys = [
            "purchase_value", "estimated_cost", "actual_cost", "variance_amount",
            "variance_pct", "actual_landed_cost", "currency", "breakdown",
            "invoices_received", "invoices_total", "costs_verified",
            "costs_allocated", "cost_finalization_status"
        ]
        for key in expected_keys:
            self.assertIn(key, payload, f"Missing key '{key}' in Section 3.3 payload")

        self.assertIsInstance(payload["purchase_value"], float)
        self.assertIsInstance(payload["estimated_cost"], float)
        self.assertIsInstance(payload["actual_cost"], float)
        self.assertIsInstance(payload["variance_amount"], float)
        self.assertIsInstance(payload["variance_pct"], float)
        self.assertIsInstance(payload["actual_landed_cost"], float)
        self.assertIsInstance(payload["currency"], str)
        self.assertIsInstance(payload["breakdown"], list)
        self.assertIsInstance(payload["invoices_received"], int)
        self.assertIsInstance(payload["invoices_total"], int)
        self.assertIsInstance(payload["costs_verified"], int)
        self.assertIsInstance(payload["costs_allocated"], int)
        self.assertIsInstance(payload["cost_finalization_status"], str)

        # Check breakdown structure
        for b in payload["breakdown"]:
            self.assertIn("label", b)
            self.assertIn("amount", b)
            self.assertIsInstance(b["amount"], float)


class TestPurpleBanCompliance(unittest.TestCase):
    """Enforces zero purple/violet colors in trade_cost_sheet.js."""

    def test_trade_cost_sheet_js_purple_ban(self):
        js_path = os.path.join(APP_PATH, "logistics_wizard", "doctype", "trade_cost_sheet", "trade_cost_sheet.js")
        self.assertTrue(os.path.isfile(js_path), f"File not found: {js_path}")

        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove comments
        clean_content = re.sub(r"/\*[\s\S]*?\*/", "", content)
        clean_content = re.sub(r"//.*", "", clean_content)

        forbidden_names = re.compile(r"\b(purple|violet|indigo|magenta|plum|fuchsia)\b", re.IGNORECASE)
        m = forbidden_names.search(clean_content)
        self.assertIsNone(m, f"Forbidden color name found in trade_cost_sheet.js: {m.group(0) if m else ''}")


if __name__ == "__main__":
    unittest.main()
