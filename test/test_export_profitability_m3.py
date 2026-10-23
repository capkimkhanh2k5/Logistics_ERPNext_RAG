#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_export_tracker.py — Empirical Verification Suite for proposed_export_tracker.py
======================================================================================
Tests all 12 test suites designed for Milestone 3 (test_export_profitability_m3.py).
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

from logistics_wizard.costing_engine.export_tracker import (
    ExportTracker,
    calculate_export_profitability,
    get_export_profitability_summary,
    compute_margins,
    extract_sales_documents,
    derive_export_revenue,
    derive_export_cogs,
    derive_export_logistics_costs,
    normalize_cost_type,
    STANDARD_COST_TYPES,
)


class TestExportProfitabilityStandard(unittest.TestCase):
    """Suite 1: Happy path standard export shipment calculation."""

    def test_standard_happy_path(self):
        """F15.1: Compute Revenue $100k, COGS $60k, Logistics $15k -> Gross $40k (40%), Net $25k (25%)."""
        res = calculate_export_profitability(
            revenue=100000.0,
            cogs=60000.0,
            logistics_cost=15000.0,
            logistics_cost_estimated=15000.0,
            currency="USD"
        )
        self.assertEqual(res["revenue"], 100000.0)
        self.assertEqual(res["cogs"], 60000.0)
        self.assertEqual(res["logistics_cost_actual"], 15000.0)
        self.assertEqual(res["gross_margin"], 40000.0)
        self.assertEqual(res["gross_margin_pct"], 40.0)
        self.assertEqual(res["net_profit"], 25000.0)
        self.assertEqual(res["net_margin_pct"], 25.0)
        self.assertEqual(res["variance_amount"], 0.0)
        self.assertEqual(res["variance_pct"], 0.0)
        self.assertEqual(res["currency"], "USD")

    def test_zero_logistics_cost_net_matches_gross(self):
        """F15.3: Zero logistics cost makes net profit match gross margin."""
        res = calculate_export_profitability(revenue=80000.0, cogs=50000.0, logistics_cost=0.0)
        self.assertEqual(res["gross_margin"], 30000.0)
        self.assertEqual(res["net_profit"], 30000.0)
        self.assertEqual(res["net_margin_pct"], 37.5)


class TestPartialShipmentsAndMultiDocs(unittest.TestCase):
    """Suite 2: Partial shipments, multi-delivery notes, multi-invoices."""

    def test_multiple_delivery_notes_and_invoices(self):
        """Partial shipments across 2 Delivery Notes and 2 Sales Invoices."""
        sales_docs = {
            "sales_invoices": [
                {"name": "SI-001", "base_net_total": 40000.0, "docstatus": 1},
                {"name": "SI-002", "base_net_total": 60000.0, "docstatus": 1},
            ],
            "delivery_notes": [
                {
                    "name": "DN-001",
                    "docstatus": 1,
                    "items": [
                        {"item_code": "SOLAR-100", "qty": 40.0, "incoming_rate": 600.0},  # 24,000
                    ]
                },
                {
                    "name": "DN-002",
                    "docstatus": 1,
                    "items": [
                        {"item_code": "SOLAR-100", "qty": 60.0, "incoming_rate": 600.0},  # 36,000
                    ]
                }
            ]
        }
        cost_sheet = {
            "currency": "USD",
            "cost_items": [
                {"cost_type": "Freight", "actual_cost": 8000.0, "status": "Verified"},
                {"cost_type": "Port", "actual_cost": 2000.0, "status": "Verified"},
            ]
        }
        res = calculate_export_profitability(cost_sheet=cost_sheet, sales_docs=sales_docs)
        self.assertEqual(res["revenue"], 100000.0)
        self.assertEqual(res["cogs"], 60000.0)
        self.assertEqual(res["logistics_cost_actual"], 10000.0)
        self.assertEqual(res["gross_margin"], 40000.0)
        self.assertEqual(res["gross_margin_pct"], 40.0)
        self.assertEqual(res["net_profit"], 30000.0)
        self.assertEqual(res["net_margin_pct"], 30.0)


class TestMissingDocumentsAndFallbacks(unittest.TestCase):
    """Suite 3: Missing documents, uninvoiced shipments, undelivered goods."""

    def test_missing_invoice_falls_back_to_sales_order(self):
        """When uninvoiced, revenue derives from Sales Order."""
        sales_docs = {
            "sales_orders": [
                {"name": "SO-001", "base_net_total": 50000.0, "docstatus": 1}
            ],
            "delivery_notes": [
                {"name": "DN-001", "docstatus": 1, "items": [{"qty": 100.0, "incoming_rate": 200.0}]}
            ]
        }
        cost_sheet = {
            "cost_items": [{"cost_type": "Trucking", "actual_cost": 3000.0, "status": "Verified"}]
        }
        res = calculate_export_profitability(cost_sheet=cost_sheet, sales_docs=sales_docs)
        self.assertEqual(res["revenue"], 50000.0)
        self.assertEqual(res["cogs"], 20000.0)
        self.assertEqual(res["logistics_cost_actual"], 3000.0)
        self.assertEqual(res["net_profit"], 27000.0)

    def test_missing_delivery_note_falls_back_to_cost_sheet_cogs(self):
        """When Delivery Note is absent, falls back to cost_sheet.export_cogs."""
        cost_sheet = {
            "export_revenue": 70000.0,
            "export_cogs": 40000.0,
            "export_logistics_cost": 5000.0,
        }
        res = calculate_export_profitability(cost_sheet=cost_sheet)
        self.assertEqual(res["revenue"], 70000.0)
        self.assertEqual(res["cogs"], 40000.0)
        self.assertEqual(res["logistics_cost_actual"], 5000.0)
        self.assertEqual(res["net_profit"], 25000.0)

    def test_unknown_case_id_returns_safe_zero_payload(self):
        """Non-existent case ID returns safe zero-initialized payload without raising exception."""
        res = get_export_profitability_summary("NON-EXISTENT-CASE")
        self.assertEqual(res["revenue"], 0.0)
        self.assertEqual(res["cogs"], 0.0)
        self.assertEqual(res["net_profit"], 0.0)
        self.assertEqual(res["gross_margin_pct"], 0.0)


class TestZeroRevenueAndDivisionSafety(unittest.TestCase):
    """Suite 4: Zero revenue, zero COGS, zero estimated costs."""

    def test_zero_revenue_division_safety(self):
        """Zero revenue returns 0.0% margins without ZeroDivisionError."""
        res = calculate_export_profitability(revenue=0.0, cogs=1000.0, logistics_cost=500.0)
        self.assertEqual(res["gross_margin"], -1000.0)
        self.assertEqual(res["gross_margin_pct"], 0.0)
        self.assertEqual(res["net_profit"], -1500.0)
        self.assertEqual(res["net_margin_pct"], 0.0)

    def test_zero_estimated_logistics_cost_division_safety(self):
        """Zero estimated logistics cost returns 0.0% variance without ZeroDivisionError."""
        res = calculate_export_profitability(
            revenue=10000.0,
            cogs=5000.0,
            logistics_cost=1200.0,
            logistics_cost_estimated=0.0
        )
        self.assertEqual(res["variance_amount"], 1200.0)
        self.assertEqual(res["variance_pct"], 0.0)


class TestLossMakingAndNegativeMargins(unittest.TestCase):
    """Suite 5: Negative profits and unprofitable export shipments."""

    def test_excessive_logistics_cost_negative_net_margin(self):
        """F15.2: Excessive logistics cost causes net margin loss (-6%)."""
        res = calculate_export_profitability(revenue=50000.0, cogs=45000.0, logistics_cost=8000.0)
        self.assertEqual(res["gross_margin"], 5000.0)
        self.assertEqual(res["gross_margin_pct"], 10.0)
        self.assertEqual(res["net_profit"], -3000.0)
        self.assertEqual(res["net_margin_pct"], -6.0)

    def test_gross_loss_shipment(self):
        """Selling below COGS produces negative gross and net margins."""
        res = calculate_export_profitability(revenue=40000.0, cogs=50000.0, logistics_cost=5000.0)
        self.assertEqual(res["gross_margin"], -10000.0)
        self.assertEqual(res["gross_margin_pct"], -25.0)
        self.assertEqual(res["net_profit"], -15000.0)
        self.assertEqual(res["net_margin_pct"], -37.5)


class TestMultiCurrencyAndFXConversions(unittest.TestCase):
    """Suite 6: Multi-currency conversion into company base currency."""

    def test_fx_conversion_to_base_currency_vnd(self):
        """Sales in USD ($10,000) converted at 25,450 to VND 254,500,000."""
        fx = 25450.0
        sales_docs = {
            "sales_invoices": [
                {"name": "SI-USD-01", "net_total": 10000.0, "conversion_rate": fx, "docstatus": 1}
            ],
            "delivery_notes": [
                {"name": "DN-01", "docstatus": 1, "items": [{"qty": 10.0, "incoming_rate": 15000000.0}]}  # 150,000,000 VND
            ]
        }
        cost_sheet = {
            "currency": "VND",
            "conversion_rate": 1.0,
            "cost_items": [
                {"cost_type": "Freight", "actual_cost": 1000.0, "exchange_rate": fx, "status": "Verified"},  # 25,450,000 VND
                {"cost_type": "Trucking", "actual_cost": 5000000.0, "exchange_rate": 1.0, "status": "Verified"},  # 5,000,000 VND
            ]
        }
        res = calculate_export_profitability(cost_sheet=cost_sheet, sales_docs=sales_docs, company_currency="VND")
        self.assertEqual(res["revenue"], 254500000.0)
        self.assertEqual(res["cogs"], 150000000.0)
        self.assertEqual(res["logistics_cost_actual"], 30450000.0)
        self.assertEqual(res["gross_margin"], 104500000.0)
        self.assertEqual(res["net_profit"], 74050000.0)
        self.assertEqual(res["currency"], "VND")


class TestCostItemFilteringAndCancelledItems(unittest.TestCase):
    """Suite 7: Active vs Cancelled cost item filtering."""

    def test_cancelled_cost_items_excluded_from_logistics_cost(self):
        """Cancelled cost items are strictly ignored and do not affect profit."""
        cost_sheet = {
            "export_revenue": 200000.0,
            "export_cogs": 120000.0,
            "cost_items": [
                {"cost_type": "Freight", "actual_cost": 16000.0, "status": "Verified"},
                {"cost_type": "Other", "actual_cost": 50000.0, "status": "Cancelled"},
            ]
        }
        res = calculate_export_profitability(cost_sheet=cost_sheet)
        self.assertEqual(res["logistics_cost_actual"], 16000.0)
        self.assertEqual(res["net_profit"], 64000.0)
        self.assertEqual(res["net_margin_pct"], 32.0)
        # Breakdown must not contain Cancelled items
        self.assertEqual(len(res["breakdown"]), 1)
        self.assertEqual(res["breakdown"][0]["label"], "Freight")
        self.assertEqual(res["breakdown"][0]["amount"], 16000.0)


class Test11StandardCostTypesBreakdown(unittest.TestCase):
    """Suite 8: Breakdown grouping across 11 standard cost types."""

    def test_breakdown_grouping_and_sum_equality(self):
        """All 11 standard cost types grouped and sum equals total actual logistics."""
        cost_sheet = {
            "currency": "USD",
            "cost_items": [
                {"cost_type": "Freight", "actual_cost": 5000.0, "status": "Verified"},
                {"cost_type": "Insurance", "actual_cost": 800.0, "status": "Verified"},
                {"cost_type": "Duty", "actual_cost": 1200.0, "status": "Verified"},
                {"cost_type": "Tax", "actual_cost": 600.0, "status": "Verified"},
                {"cost_type": "Port", "actual_cost": 450.0, "status": "Verified"},
                {"cost_type": "Handling", "actual_cost": 300.0, "status": "Verified"},
                {"cost_type": "Storage", "actual_cost": 250.0, "status": "Verified"},
                {"cost_type": "Demurrage/Detention", "actual_cost": 700.0, "status": "Verified"},
                {"cost_type": "Trucking", "actual_cost": 1100.0, "status": "Verified"},
                {"cost_type": "Broker Fee", "actual_cost": 500.0, "status": "Verified"},
                {"cost_type": "Other", "actual_cost": 100.0, "status": "Verified"},
            ]
        }
        res = calculate_export_profitability(cost_sheet=cost_sheet, revenue=50000.0, cogs=25000.0)
        self.assertEqual(res["logistics_cost_actual"], 11000.0)
        self.assertEqual(len(res["breakdown"]), 11)
        self.assertEqual(sum(b["amount"] for b in res["breakdown"]), res["logistics_cost_actual"])


class TestLogisticsCostVariance(unittest.TestCase):
    """Suite 9: Logistics variance analysis (estimated vs actual)."""

    def test_variance_positive_overrun(self):
        """Actual cost exceeds estimated cost (Overrun)."""
        res = calculate_export_profitability(
            revenue=50000.0,
            cogs=30000.0,
            logistics_cost=12000.0,
            logistics_cost_estimated=10000.0
        )
        self.assertEqual(res["variance_amount"], 2000.0)
        self.assertEqual(res["variance_pct"], 20.0)

    def test_variance_negative_underrun(self):
        """Actual cost below estimated cost (Savings / Underrun)."""
        res = calculate_export_profitability(
            revenue=50000.0,
            cogs=30000.0,
            logistics_cost=8500.0,
            logistics_cost_estimated=10000.0
        )
        self.assertEqual(res["variance_amount"], -1500.0)
        self.assertEqual(res["variance_pct"], -15.0)


class TestPayloadContractInvariants(unittest.TestCase):
    """Suite 10: Schema keys, value types, and backward compatibility."""

    def test_payload_schema_keys(self):
        """All 12 DISPATCH contract keys and compatibility aliases are present."""
        res = calculate_export_profitability(revenue=30000.0, cogs=18000.0, logistics_cost=4000.0)
        required_keys = [
            "revenue",
            "cogs",
            "logistics_cost_estimated",
            "logistics_cost_actual",
            "gross_margin",
            "gross_margin_pct",
            "net_profit",
            "net_margin_pct",
            "variance_amount",
            "variance_pct",
            "currency",
            "breakdown",
        ]
        for k in required_keys:
            self.assertIn(k, res, f"Missing required key: {k}")

        alias_keys = [
            "export_revenue",
            "export_cogs",
            "export_logistics_cost",
            "export_gross_margin",
            "export_gross_margin_pct",
            "export_net_profit",
            "export_net_margin_pct",
        ]
        for ak in alias_keys:
            self.assertIn(ak, res, f"Missing compatibility alias key: {ak}")

    def test_rounding_precision_two_decimals(self):
        """F15.5: Percentage margins round cleanly to 2 decimal places."""
        res = calculate_export_profitability(revenue=30000.0, cogs=19999.0, logistics_cost=3333.0)
        self.assertEqual(res["gross_margin_pct"], 33.34)
        self.assertEqual(res["net_margin_pct"], 22.23)


class TestStandaloneMockHarness(unittest.TestCase):
    """Suite 11: In-memory mock harness when Frappe DB is offline."""

    def setUp(self):
        ExportTracker.clear_mock_registry()

    def tearDown(self):
        ExportTracker.clear_mock_registry()

    def test_mock_registry_registration_and_lookup(self):
        """Registering mock case in ExportTracker mock_registry resolves get_export_profitability_summary."""
        case_id = "EXP-MOCK-2026-001"
        cost_sheet = {
            "currency": "EUR",
            "export_revenue": 80000.0,
            "export_cogs": 45000.0,
            "cost_items": [
                {"cost_type": "Freight", "actual_cost": 7500.0, "status": "Verified"}
            ]
        }
        ExportTracker.register_mock_case(case_id=case_id, cost_sheet=cost_sheet, currency="EUR")

        res = get_export_profitability_summary(case_id)
        self.assertEqual(res["revenue"], 80000.0)
        self.assertEqual(res["cogs"], 45000.0)
        self.assertEqual(res["logistics_cost_actual"], 7500.0)
        self.assertEqual(res["net_profit"], 27500.0)
        self.assertEqual(res["currency"], "EUR")


class TestClassAndFunctionalFacades(unittest.TestCase):
    """Suite 12: Class and functional facades."""

    def test_oop_instance_calculate(self):
        """ExportTracker instance calculates profitability."""
        tracker = ExportTracker(company_currency="VND")
        res = tracker.calculate(revenue=200000000.0, cogs=120000000.0, logistics_cost=25000000.0)
        self.assertEqual(res["currency"], "VND")
        self.assertEqual(res["net_profit"], 55000000.0)

    def test_static_calculate(self):
        """ExportTracker.calculate_static direct invocation."""
        res = ExportTracker.calculate_static(revenue=1000.0, cogs=600.0, logistics_cost=150.0)
        self.assertEqual(res["net_profit"], 250.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
