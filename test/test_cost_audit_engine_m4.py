#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cost_audit_engine_m4.py — Unit Test Suite for Milestone 4 (Cost Audit Engine)
==================================================================================
Tests:
- Duplicate invoice detection within sheet and cross-case
- Cancelled invoice handling
- Missing critical costs by Incoterm & HS code
- Wrong-case association detection
- Clean passes on valid data
"""

import sys
import os
import unittest
from typing import Dict, Any, List

# Ensure apps/logistics_wizard is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
APP_PATH = os.path.join(REPO_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from logistics_wizard.costing_engine.audit_engine import (
    CostAuditEngine,
    audit_cost_sheet,
)


class TestCostAuditEngine(unittest.TestCase):
    """Unit tests for CostAuditEngine."""

    def test_clean_cost_sheet_passes_audit(self):
        """Valid cost sheet with all expected costs passes audit with no errors or warnings."""
        sheet = {
            "name": "TCS-IMP-2026-001",
            "trade_case": "TC-2026-001",
            "incoterm": "FOB",
            "trade_type": "Import",
            "cost_items": [
                {"cost_type": "Freight", "service_provider": "Maersk", "invoice_number": "INV-001", "status": "Verified"},
                {"cost_type": "Port", "service_provider": "Cat Lai Port", "invoice_number": "INV-002", "status": "Verified"},
                {"cost_type": "Trucking", "service_provider": "Transimex", "invoice_number": "INV-003", "status": "Verified"},
            ],
        }
        trade_case = {"name": "TC-2026-001", "incoterm": "FOB"}
        res = audit_cost_sheet(sheet, trade_case=trade_case)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(len(res["warnings"]), 0)

    def test_duplicate_invoice_within_sheet(self):
        """Duplicate (supplier, invoice) within the same sheet is detected."""
        sheet = {
            "name": "TCS-IMP-2026-002",
            "trade_case": "TC-2026-002",
            "incoterm": "CIF",
            "cost_items": [
                {"cost_type": "Handling", "service_provider": "Saigon Port", "invoice_number": "INV-999", "status": "Verified"},
                {"cost_type": "Storage", "service_provider": "saigon port", "invoice_number": "  inv-999 ", "status": "Verified"},
            ],
        }
        res = audit_cost_sheet(sheet)
        self.assertFalse(res["passed"])
        self.assertEqual(len(res["errors"]), 1)
        self.assertIn("Duplicate invoice detected", res["errors"][0])

    def test_cancelled_items_do_not_trigger_duplicate_error(self):
        """A cancelled duplicate invoice does not cause validation failure."""
        sheet = {
            "name": "TCS-IMP-2026-003",
            "cost_items": [
                {"cost_type": "Freight", "service_provider": "CMA CGM", "invoice_number": "INV-100", "status": "Cancelled"},
                {"cost_type": "Freight", "service_provider": "CMA CGM", "invoice_number": "INV-100", "status": "Verified"},
            ],
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(res["passed"])

    def test_cross_case_duplicate_invoice(self):
        """Invoice used in a past sheet is flagged as cross-case duplicate."""
        past_sheet = {
            "name": "TCS-HIST-001",
            "cost_items": [
                {"cost_type": "Port", "service_provider": "Haiphong Port", "invoice_number": "HP-8888", "status": "Allocated"}
            ],
        }
        curr_sheet = {
            "name": "TCS-CURR-001",
            "cost_items": [
                {"cost_type": "Port", "service_provider": "Haiphong Port", "invoice_number": "HP-8888", "status": "Verified"}
            ],
        }
        res = audit_cost_sheet(curr_sheet, historical_sheets=[past_sheet])
        self.assertFalse(res["passed"])
        self.assertEqual(len(res["errors"]), 1)
        self.assertIn("Cross-case duplicate invoice", res["errors"][0])

    def test_missing_fob_import_freight(self):
        """FOB Import missing Freight produces a warning."""
        sheet = {
            "name": "TCS-FOB-01",
            "incoterm": "FOB",
            "trade_type": "Import",
            "cost_items": [
                {"cost_type": "Port", "service_provider": "Port Corp", "invoice_number": "INV-1"}
            ],
        }
        res = audit_cost_sheet(sheet)
        self.assertTrue(res["passed"])  # Warnings don't fail audit, only errors fail
        self.assertEqual(len(res["warnings"]), 1)
        self.assertIn("missing international Freight", res["warnings"][0])

    def test_missing_port_thc_cost(self):
        """CIF Import missing Port/THC produces a warning."""
        sheet = {
            "name": "TCS-CIF-01",
            "incoterm": "CIF",
            "trade_type": "Import",
            "cost_items": [
                {"cost_type": "Trucking", "service_provider": "Trucking Corp", "invoice_number": "INV-1"}
            ],
        }
        res = audit_cost_sheet(sheet)
        self.assertEqual(len(res["warnings"]), 1)
        self.assertIn("missing destination Port/THC", res["warnings"][0])

    def test_dutiable_goods_missing_duty_tax(self):
        """Dutiable goods declaration without Duty or Tax produces a warning."""
        sheet = {
            "name": "TCS-DUTY-01",
            "has_dutiable_goods": True,
            "trade_type": "Import",
            "cost_items": [
                {"cost_type": "Freight", "service_provider": "Ocean Line", "invoice_number": "INV-1"},
                {"cost_type": "Port", "service_provider": "Port Line", "invoice_number": "INV-2"},
            ],
        }
        res = audit_cost_sheet(sheet)
        self.assertEqual(len(res["warnings"]), 1)
        self.assertIn("Dutiable cargo declaration has no Duty or Tax", res["warnings"][0])

    def test_wrong_case_association(self):
        """Cost sheet linked to TC-002 audited under TC-001 fails with wrong case error."""
        sheet = {
            "name": "TCS-WRONG-01",
            "trade_case": "TC-002",
            "cost_items": [],
        }
        trade_case = {"name": "TC-001"}
        res = audit_cost_sheet(sheet, trade_case=trade_case)
        self.assertFalse(res["passed"])
        self.assertEqual(len(res["errors"]), 1)
        self.assertIn("Cost sheet linked to wrong Trade Case", res["errors"][0])

    def test_standalone_audit_without_trade_case(self):
        """Audit runs cleanly without trade_case context."""
        sheet = {"name": "TCS-STANDALONE", "cost_items": []}
        res = audit_cost_sheet(sheet, trade_case=None)
        self.assertTrue(res["passed"])


if __name__ == "__main__":
    unittest.main()
