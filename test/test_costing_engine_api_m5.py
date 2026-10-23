#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_costing_engine_api_m5.py — Unit Test Suite for Milestone 5 (Central API & Data Contract)
=============================================================================================
Tests:
- get_case_cost_summary conforms 100% to Section 3.3 schema
- Accurate calculations & breakdown structure
- Safe handling of missing cost sheets
- Mock registry integration for testability
"""

import sys
import os
import unittest

# Ensure apps/logistics_wizard is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
APP_PATH = os.path.join(REPO_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from logistics_wizard.costing_engine.api import (
    get_case_cost_summary,
    get_case_export_profitability,
    audit_case_costs,
    register_mock_cost_sheet,
    clear_mock_cost_sheet_registry,
)


class TestCostingEngineAPI(unittest.TestCase):
    """Tests for costing_engine.api."""

    def setUp(self):
        clear_mock_cost_sheet_registry()
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
        register_mock_cost_sheet("IMP-2026-001", self.sample_sheet)

    def tearDown(self):
        clear_mock_cost_sheet_registry()

    def test_schema_conformance_section_3_3(self):
        """All 13 keys specified in todoTradeCase.md Section 3.3 must be present."""
        summary = get_case_cost_summary("IMP-2026-001")
        required_keys = [
            "purchase_value", "estimated_cost", "actual_cost",
            "variance_amount", "variance_pct", "actual_landed_cost",
            "currency", "breakdown", "invoices_received", "invoices_total",
            "costs_verified", "costs_allocated", "cost_finalization_status"
        ]
        for key in required_keys:
            self.assertIn(key, summary)

    def test_numeric_types(self):
        """Financial and count fields must have correct types."""
        summary = get_case_cost_summary("IMP-2026-001")
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

    def test_exact_calculation_numbers(self):
        """Calculated values match expectations."""
        summary = get_case_cost_summary("IMP-2026-001")
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

    def test_breakdown_format(self):
        """Breakdown is formatted as a list of dicts with label and amount."""
        summary = get_case_cost_summary("IMP-2026-001")
        self.assertIsInstance(summary["breakdown"], list)
        self.assertGreater(len(summary["breakdown"]), 0)
        labels = [b["label"] for b in summary["breakdown"]]
        self.assertIn("Freight", labels)
        self.assertIn("Duty", labels)

    def test_unknown_case_safe_zero_payload(self):
        """Unknown case ID returns a safe, zero-initialized Section 3.3 payload."""
        summary = get_case_cost_summary("NON-EXISTENT-CASE")
        self.assertEqual(summary["purchase_value"], 0.0)
        self.assertEqual(summary["estimated_cost"], 0.0)
        self.assertEqual(summary["actual_cost"], 0.0)
        self.assertEqual(summary["actual_landed_cost"], 0.0)
        self.assertEqual(summary["cost_finalization_status"], "DRAFT")
        self.assertEqual(summary["breakdown"], [])

    def test_audit_case_costs_invocation(self):
        """audit_case_costs runs and returns audit verdict."""
        res = audit_case_costs("IMP-2026-001")
        self.assertIn("passed", res)
        self.assertIn("errors", res)
        self.assertIn("warnings", res)

    def test_controller_end_to_end_audit_and_lcv_sync(self):
        """TradeCostSheet controller integrates M2 (Allocation + LCV), M3 (Export), and M4 (Audit)."""
        from logistics_wizard.doctype.trade_cost_sheet.trade_cost_sheet import TradeCostSheet
        from logistics_wizard.costing_engine.api import allocate_and_sync_lcv

        sheet = TradeCostSheet({
            "name": "TCS-INT-2026-001",
            "trade_case": "IMP-INT-001",
            "trade_type": "Import",
            "incoterm": "FOB",
            "total_purchase_value": 50000.0,
            "currency": "USD",
            "allocation_rule": "By Value",
            "cost_items": [
                {"cost_type": "Freight", "service_provider": "Maersk", "invoice_number": "INV-M1", "estimated_cost": 2000.0, "actual_cost": 2200.0, "status": "Verified"},
                {"cost_type": "Port", "service_provider": "Cat Lai", "invoice_number": "INV-C1", "estimated_cost": 300.0, "actual_cost": 300.0, "status": "Verified"},
            ],
            "document_links": [
                {"document_type": "Purchase Receipt", "document_name": "PR-INT-001", "is_active": 1}
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.total_actual_cost, 2500.0)
        self.assertEqual(sheet.actual_landed_cost, 52500.0)
        self.assertEqual(sheet.cost_finalization_status, "ALMOST READY")
        self.assertEqual(sheet.audit_warnings, "")

        # Register sheet and run allocate_and_sync_lcv
        register_mock_cost_sheet("TCS-INT-2026-001", sheet)
        pr_items = [
            {"item_code": "ITEM-A", "qty": 100, "amount": 30000.0, "receipt_document_type": "Purchase Receipt", "receipt_document": "PR-INT-001"},
            {"item_code": "ITEM-B", "qty": 50, "amount": 20000.0, "receipt_document_type": "Purchase Receipt", "receipt_document": "PR-INT-001"},
        ]
        res = allocate_and_sync_lcv("TCS-INT-2026-001", auto_submit=False, items=pr_items)
        self.assertTrue(res.get("success"))
        self.assertEqual(len(res["allocated_items"]), 2)
        # ITEM-A gets 60% of 2500 = 1500 -> new valuation rate = (30000 + 1500)/100 = 315.0
        self.assertEqual(res["allocated_items"][0]["allocated_charges"], 1500.0)
        self.assertEqual(res["allocated_items"][0]["new_valuation_rate"], 315.0)
        # ITEM-B gets 40% of 2500 = 1000 -> new valuation rate = (20000 + 1000)/50 = 420.0
        self.assertEqual(res["allocated_items"][1]["allocated_charges"], 1000.0)
        self.assertEqual(res["allocated_items"][1]["new_valuation_rate"], 420.0)
        # Status automatically transitions from ALMOST READY -> ALLOCATED
        self.assertEqual(sheet.cost_finalization_status, "ALLOCATED")

    def test_controller_duplicate_invoice_populates_audit_warnings(self):
        """TradeCostSheet.validate() automatically flags duplicate invoices in audit_warnings."""
        from logistics_wizard.doctype.trade_cost_sheet.trade_cost_sheet import TradeCostSheet

        sheet = TradeCostSheet({
            "name": "TCS-DUP-001",
            "trade_case": "IMP-DUP-001",
            "trade_type": "Import",
            "cost_items": [
                {"cost_type": "Freight", "service_provider": "ONE Line", "invoice_number": "DUP-99", "actual_cost": 1000.0, "status": "Verified"},
                {"cost_type": "Handling", "service_provider": "one line", "invoice_number": "dup-99", "actual_cost": 200.0, "status": "Verified"},
            ]
        })
        sheet.validate()
        self.assertIn("Duplicate invoice detected", sheet.audit_warnings)


if __name__ == "__main__":
    unittest.main()
