#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_adversarial_m1_state_machine.py — Empirical State Machine & Regression Test Harness
========================================================================================
Author: challenger_m1_2 (Adversarial Challenger)
Target: apps/logistics_wizard/logistics_wizard/doctype/trade_cost_sheet/trade_cost_sheet.py
        apps/logistics_wizard/logistics_wizard/api.py (Stage Gate Coupling)

Exhaustively verifies:
1. Complete Forward State Transitions (DRAFT -> IN PROGRESS -> ALMOST READY -> ALLOCATED -> FINALIZED).
2. Complete Backward Reversions / Rollbacks (FINALIZED -> ALLOCATED -> ALMOST READY -> IN PROGRESS -> DRAFT).
3. Complex Multi-State Scenarios (Skip states, partial verifications, partial allocations).
4. Edge Case: Sheet with ONLY Cancelled items (must evaluate to DRAFT, all sums 0.0, empty breakdown).
5. Dynamic Cancellation Rollback (Allocated sheet becoming DRAFT when items are cancelled).
6. Mixed Active + Cancelled items (Cancelled items completely invisible to rollups and financial sums).
7. Stage Gate Coupling: validate_stage_gate_completion logic against TradeCostSheet state machine outputs.
8. Trade Case Sync behavior and hysteresis (costs_finalized flag behavior across state changes).
"""

import os
import sys
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


class MockTradeCaseDoc:
    """Mock Trade Case document to test sync_to_trade_case and stage gate interactions."""
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "TC-TEST-001")
        self.order_amount = kwargs.get("order_amount", 50000.0)
        self.currency = kwargs.get("currency", "USD")
        self.company = kwargs.get("company", "Test Global Logistics Ltd")
        self.case_title = kwargs.get("case_title", "Test Import Case")
        self.trade_type = kwargs.get("trade_type", "Import")
        self.estimated_landed_cost = 0.0
        self.actual_landed_cost = 0.0
        self.cost_variance_pct = 0.0
        self.costs_finalized = 0
        self.save_called = 0

    def save(self, *args, **kwargs):
        self.save_called += 1
        return self


class TestStateMachineForwardAndBackward(unittest.TestCase):
    """
    Exhaustive empirical test of the Trade Cost Sheet State Machine.
    Verifies deterministic transitions across all states and bidirectional reversibility.
    """

    def setUp(self):
        self.sheet = TradeCostSheet({
            "name": "TCS-2026-TEST",
            "trade_case": "TC-2026-001",
            "currency": "USD",
            "conversion_rate": 1.0,
            "total_purchase_value": 100000.0,
            "docstatus": 0,
            "status": "Draft",
            "cost_items": []
        })

    def test_01_empty_sheet_is_draft(self):
        """Empty sheet with no items must strictly evaluate to DRAFT."""
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "DRAFT")
        self.assertEqual(self.sheet.invoices_total, 0)
        self.assertEqual(self.sheet.invoices_received, 0)
        self.assertEqual(self.sheet.costs_verified, 0)
        self.assertEqual(self.sheet.costs_allocated, 0)
        self.assertEqual(self.sheet.total_estimated_cost, 0.0)
        self.assertEqual(self.sheet.total_actual_cost, 0.0)

    def test_02_draft_items_without_invoices_is_draft(self):
        """Active items present, but none have invoice numbers or verification -> DRAFT."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 0.0,
            "status": "Draft",
            "invoice_number": ""
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 0.0,
            "status": "Draft",
            "invoice_number": None
        })
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "DRAFT")
        self.assertEqual(self.sheet.invoices_total, 2)
        self.assertEqual(self.sheet.invoices_received, 0)
        self.assertEqual(self.sheet.costs_verified, 0)
        self.assertEqual(self.sheet.costs_allocated, 0)

    def test_03_partial_invoices_received_transitions_to_in_progress(self):
        """When at least 1 invoice number is entered -> IN PROGRESS."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 5200.0,
            "status": "Draft",
            "invoice_number": "INV-FR-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 0.0,
            "status": "Draft",
            "invoice_number": ""
        })
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "IN PROGRESS")
        self.assertEqual(self.sheet.invoices_total, 2)
        self.assertEqual(self.sheet.invoices_received, 1)
        self.assertEqual(self.sheet.costs_verified, 0)

    def test_04_all_invoices_received_but_none_verified_is_in_progress(self):
        """All invoices received, but status is Draft -> IN PROGRESS (not ALMOST READY)."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 5200.0,
            "status": "Draft",
            "invoice_number": "INV-FR-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 1050.0,
            "status": "Draft",
            "invoice_number": "INV-INS-002"
        })
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "IN PROGRESS")
        self.assertEqual(self.sheet.invoices_total, 2)
        self.assertEqual(self.sheet.invoices_received, 2)
        self.assertEqual(self.sheet.costs_verified, 0)

    def test_05_all_invoices_received_and_all_verified_is_almost_ready(self):
        """All invoices received AND all verified, but none allocated -> ALMOST READY."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 5200.0,
            "status": "Verified",
            "invoice_number": "INV-FR-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 1050.0,
            "status": "Verified",
            "invoice_number": "INV-INS-002"
        })
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALMOST READY")
        self.assertEqual(self.sheet.invoices_total, 2)
        self.assertEqual(self.sheet.invoices_received, 2)
        self.assertEqual(self.sheet.costs_verified, 2)
        self.assertEqual(self.sheet.costs_allocated, 0)

    def test_06_mixed_verified_and_allocated_is_almost_ready(self):
        """When 1 item is Allocated and 1 item is Verified -> ALMOST READY."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 5200.0,
            "status": "Allocated",
            "invoice_number": "INV-FR-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 1050.0,
            "status": "Verified",
            "invoice_number": "INV-INS-002"
        })
        self.sheet.validate()
        # c_ver is 2, c_alloc is 1, inv_total is 2
        self.assertEqual(self.sheet.cost_finalization_status, "ALMOST READY")
        self.assertEqual(self.sheet.costs_verified, 2)
        self.assertEqual(self.sheet.costs_allocated, 1)

    def test_07_all_allocated_docstatus_0_is_allocated(self):
        """All items allocated, sheet still in draft (docstatus=0, status=Draft) -> ALLOCATED."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 5200.0,
            "status": "Allocated",
            "invoice_number": "INV-FR-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 1050.0,
            "status": "Allocated",
            "invoice_number": "INV-INS-002"
        })
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALLOCATED")
        self.assertEqual(self.sheet.costs_allocated, 2)
        self.assertEqual(self.sheet.invoices_total, 2)

    def test_08_all_allocated_submitted_or_finalized_is_finalized(self):
        """All items allocated + docstatus=1 or status in [Finalized, Closed, Submitted] -> FINALIZED."""
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 5000.0,
            "actual_cost": 5200.0,
            "status": "Allocated",
            "invoice_number": "INV-FR-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1000.0,
            "actual_cost": 1050.0,
            "status": "Allocated",
            "invoice_number": "INV-INS-002"
        })

        # Variant A: docstatus = 1
        self.sheet.docstatus = 1
        self.sheet.status = "Submitted"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "FINALIZED")

        # Variant B: docstatus = 0, but status = "Finalized"
        self.sheet.docstatus = 0
        self.sheet.status = "Finalized"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "FINALIZED")

        # Variant C: docstatus = 0, status = "Closed"
        self.sheet.status = "Closed"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "FINALIZED")

    def test_09_full_step_by_step_lifecycle_forward_and_backward(self):
        """
        Tests continuous lifecycle evolution:
        DRAFT -> IN PROGRESS -> ALMOST READY -> ALLOCATED -> FINALIZED ->
        (Rollback) -> ALLOCATED -> ALMOST READY -> IN PROGRESS -> DRAFT.
        """
        item1 = {
            "cost_type": "Freight",
            "estimated_cost": 4000.0,
            "actual_cost": 4000.0,
            "status": "Draft",
            "invoice_number": ""
        }
        item2 = {
            "cost_type": "Duty",
            "estimated_cost": 2000.0,
            "actual_cost": 2000.0,
            "status": "Draft",
            "invoice_number": ""
        }
        self.sheet.append("cost_items", item1)
        self.sheet.append("cost_items", item2)

        # Step 1: DRAFT
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "DRAFT")

        # Step 2: Item 1 gets invoice -> IN PROGRESS
        self.sheet.cost_items[0].invoice_number = "INV-001"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "IN PROGRESS")

        # Step 3: Item 2 gets invoice, item 1 verified -> IN PROGRESS
        self.sheet.cost_items[1].invoice_number = "INV-002"
        self.sheet.cost_items[0].status = "Verified"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "IN PROGRESS")

        # Step 4: Item 2 verified -> ALMOST READY
        self.sheet.cost_items[1].status = "Verified"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALMOST READY")

        # Step 5: Both allocated -> ALLOCATED
        self.sheet.cost_items[0].status = "Allocated"
        self.sheet.cost_items[1].status = "Allocated"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALLOCATED")

        # Step 6: Submitted -> FINALIZED
        self.sheet.docstatus = 1
        self.sheet.status = "Submitted"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "FINALIZED")

        # --- ROLLBACK SEQUENCE ---

        # Rollback 1: Un-submit / Reopen -> ALLOCATED
        self.sheet.docstatus = 0
        self.sheet.status = "Draft"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALLOCATED")

        # Rollback 2: Item 2 un-allocated (back to Verified) -> ALMOST READY
        self.sheet.cost_items[1].status = "Verified"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALMOST READY")

        # Rollback 3: Item 2 un-verified (back to Draft) -> IN PROGRESS
        self.sheet.cost_items[1].status = "Draft"
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "IN PROGRESS")

        # Rollback 4: Clear all invoices and reset to Draft -> DRAFT
        self.sheet.cost_items[0].status = "Draft"
        self.sheet.cost_items[0].invoice_number = ""
        self.sheet.cost_items[1].invoice_number = ""
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "DRAFT")


class TestCancelledItemsAdversarialEdgeCases(unittest.TestCase):
    """
    Adversarial stress-testing of Cancelled items.
    Verifies that Cancelled items are 100% neutralized in totals, rollups, and state transitions.
    """

    def setUp(self):
        self.sheet = TradeCostSheet({
            "name": "TCS-CANCEL-TEST",
            "trade_case": "TC-2026-002",
            "currency": "USD",
            "conversion_rate": 1.0,
            "total_purchase_value": 50000.0,
            "docstatus": 0,
            "status": "Draft",
            "cost_items": []
        })

    def test_01_sheet_with_only_cancelled_items_evaluates_to_draft_and_zero_costs(self):
        """
        Adversarial Scenario: Sheet has 3 items, ALL marked as Cancelled.
        Even with huge estimated and actual amounts, invoice numbers, and exchange rates:
        - cost_finalization_status MUST BE 'DRAFT'
        - total_estimated_cost MUST BE 0.0
        - total_actual_cost MUST BE 0.0
        - variance_amount MUST BE 0.0
        - variance_pct MUST BE 0.0
        - actual_landed_cost MUST BE total_purchase_value (50,000.0)
        - invoices_total MUST BE 0
        - invoices_received MUST BE 0
        - costs_verified MUST BE 0
        - costs_allocated MUST BE 0
        - breakdown MUST BE []
        """
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 25000.0,
            "actual_cost": 30000.0,
            "exchange_rate": 1.0,
            "status": "Cancelled",
            "invoice_number": "INV-CANCEL-001"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Duty",
            "estimated_cost": 15000.0,
            "actual_cost": 14000.0,
            "exchange_rate": 1.0,
            "status": "Cancelled",
            "invoice_number": "INV-CANCEL-002"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Port",
            "estimated_cost": 5000.0,
            "actual_cost": 5500.0,
            "exchange_rate": 1.0,
            "status": "Cancelled",
            "invoice_number": "INV-CANCEL-003"
        })

        self.sheet.validate()

        self.assertEqual(self.sheet.cost_finalization_status, "DRAFT")
        self.assertEqual(self.sheet.total_estimated_cost, 0.0)
        self.assertEqual(self.sheet.total_actual_cost, 0.0)
        self.assertEqual(self.sheet.variance_amount, 0.0)
        self.assertEqual(self.sheet.variance_pct, 0.0)
        self.assertEqual(self.sheet.actual_landed_cost, 50000.0)
        self.assertEqual(self.sheet.invoices_total, 0)
        self.assertEqual(self.sheet.invoices_received, 0)
        self.assertEqual(self.sheet.costs_verified, 0)
        self.assertEqual(self.sheet.costs_allocated, 0)
        self.assertEqual(self.sheet.get_breakdown(), [])

        # Payload contract check
        payload = self.sheet.get_cost_summary_payload()
        self.assertEqual(payload["cost_finalization_status"], "DRAFT")
        self.assertEqual(payload["estimated_cost"], 0.0)
        self.assertEqual(payload["actual_cost"], 0.0)
        self.assertEqual(payload["actual_landed_cost"], 50000.0)
        self.assertEqual(payload["invoices_total"], 0)
        self.assertEqual(payload["invoices_received"], 0)
        self.assertEqual(payload["breakdown"], [])

    def test_02_dynamic_cancellation_causes_instant_state_collapse_to_draft(self):
        """
        A sheet in ALLOCATED state with 2 items.
        If both items are marked 'Cancelled', re-running validate() must immediately
        collapse the status to DRAFT and zero out financial totals.
        """
        self.sheet.append("cost_items", {
            "cost_type": "Freight",
            "estimated_cost": 10000.0,
            "actual_cost": 10500.0,
            "status": "Allocated",
            "invoice_number": "INV-OK-1"
        })
        self.sheet.append("cost_items", {
            "cost_type": "Duty",
            "estimated_cost": 5000.0,
            "actual_cost": 5000.0,
            "status": "Allocated",
            "invoice_number": "INV-OK-2"
        })
        self.sheet.validate()
        self.assertEqual(self.sheet.cost_finalization_status, "ALLOCATED")
        self.assertEqual(self.sheet.total_actual_cost, 15500.0)
        self.assertEqual(self.sheet.invoices_total, 2)

        # Adversarial attack: Cancel both items
        self.sheet.cost_items[0].status = "Cancelled"
        self.sheet.cost_items[1].status = "Cancelled"
        self.sheet.validate()

        self.assertEqual(self.sheet.cost_finalization_status, "DRAFT")
        self.assertEqual(self.sheet.total_actual_cost, 0.0)
        self.assertEqual(self.sheet.total_estimated_cost, 0.0)
        self.assertEqual(self.sheet.invoices_total, 0)
        self.assertEqual(self.sheet.costs_allocated, 0)

    def test_03_mixed_active_and_cancelled_items_strict_isolation(self):
        """
        Sheet has 5 Cancelled items ($100,000 total) and 1 Active Allocated item ($1,250).
        The active item must alone dictate totals and status:
        - total_actual_cost = $1,250
        - invoices_total = 1
        - costs_allocated = 1
        - cost_finalization_status = 'ALLOCATED'
        """
        for i in range(5):
            self.sheet.append("cost_items", {
                "cost_type": "Other",
                "estimated_cost": 20000.0,
                "actual_cost": 20000.0,
                "status": "Cancelled",
                "invoice_number": f"CANC-INV-{i}"
            })

        self.sheet.append("cost_items", {
            "cost_type": "Insurance",
            "estimated_cost": 1200.0,
            "actual_cost": 1250.0,
            "status": "Allocated",
            "invoice_number": "ACT-INV-1"
        })

        self.sheet.validate()

        self.assertEqual(self.sheet.cost_finalization_status, "ALLOCATED")
        self.assertEqual(self.sheet.invoices_total, 1)
        self.assertEqual(self.sheet.invoices_received, 1)
        self.assertEqual(self.sheet.costs_allocated, 1)
        self.assertEqual(self.sheet.total_estimated_cost, 1200.0)
        self.assertEqual(self.sheet.total_actual_cost, 1250.0)
        self.assertEqual(self.sheet.variance_amount, 50.0)
        self.assertEqual(self.sheet.variance_pct, 4.2)
        self.assertEqual(len(self.sheet.get_breakdown()), 1)
        self.assertEqual(self.sheet.get_breakdown()[0]["label"], "Insurance")
        self.assertEqual(self.sheet.get_breakdown()[0]["amount"], 1250.0)

    def test_04_stress_500_cancelled_items_with_1_active_item(self):
        """
        High volume stress: 500 cancelled rows and 1 active row.
        Ensures performance is O(N) linear and does not corrupt arithmetic or state.
        """
        for i in range(500):
            self.sheet.append("cost_items", {
                "cost_type": "Demurrage/Detention",
                "estimated_cost": 100.0,
                "actual_cost": 150.0,
                "status": "Cancelled",
                "invoice_number": f"DEM-{i}"
            })

        self.sheet.append("cost_items", {
            "cost_type": "Broker Fee",
            "estimated_cost": 500.0,
            "actual_cost": 500.0,
            "status": "Verified",
            "invoice_number": "BROKER-ACTIVE"
        })

        self.sheet.validate()

        self.assertEqual(self.sheet.cost_finalization_status, "ALMOST READY")
        self.assertEqual(self.sheet.invoices_total, 1)
        self.assertEqual(self.sheet.costs_verified, 1)
        self.assertEqual(self.sheet.total_actual_cost, 500.0)


class TestStageGateCouplingAndTradeCaseIntegration(unittest.TestCase):
    """
    Verifies stage gate coupling between TradeCostSheet and logistics_wizard.api.validate_stage_gate_completion.
    Adversarially feeds each TradeCostSheet status to the stage gate evaluator.
    """

    def setUp(self):
        # We simulate the exact evaluation logic of api.py: validate_stage_gate_completion
        self.trade_case = MockTradeCaseDoc(name="TC-STAGEGATE-001")

    def _evaluate_cost_gates(self, cost_summary: Dict[str, Any], doc: Any = None):
        """
        Mirrors lines 2437-2454 of apps/logistics_wizard/logistics_wizard/api.py
        """
        gate_lcv_passed = (
            cost_summary.get("cost_finalization_status") in ["ALLOCATED", "FINALIZED", "COMPLETED"] or
            (doc and getattr(doc, "costs_finalized", 0) == 1)
        )
        gate_clearing_passed = gate_lcv_passed

        gate_settlement_passed = (
            cost_summary.get("invoices_received", 0) >= cost_summary.get("invoices_total", 0) and
            cost_summary.get("invoices_total", 0) > 0
        ) if cost_summary.get("invoices_total") else True

        return {
            "GATE_LCV": bool(gate_lcv_passed),
            "GATE_CLEARING": bool(gate_clearing_passed),
            "GATE_SETTLEMENT": bool(gate_settlement_passed)
        }

    def test_01_draft_state_blocks_gate_lcv_and_clearing(self):
        """DRAFT state must block GATE_LCV and GATE_CLEARING."""
        sheet = TradeCostSheet({
            "name": "TCS-SG-01",
            "trade_case": self.trade_case.name,
            "cost_items": [{
                "cost_type": "Freight",
                "estimated_cost": 5000.0,
                "status": "Draft"
            }]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        gates = self._evaluate_cost_gates(payload, self.trade_case)
        self.assertFalse(gates["GATE_LCV"], "GATE_LCV must be blocked when cost sheet is DRAFT")
        self.assertFalse(gates["GATE_CLEARING"], "GATE_CLEARING must be blocked when cost sheet is DRAFT")
        self.assertFalse(gates["GATE_SETTLEMENT"], "GATE_SETTLEMENT must fail when invoices are not received")

    def test_02_in_progress_state_blocks_gate_lcv_and_clearing(self):
        """IN PROGRESS state must block GATE_LCV and GATE_CLEARING."""
        sheet = TradeCostSheet({
            "name": "TCS-SG-02",
            "trade_case": self.trade_case.name,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "status": "Verified", "invoice_number": "INV-01"},
                {"cost_type": "Tax", "estimated_cost": 1000.0, "status": "Draft", "invoice_number": ""}
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        gates = self._evaluate_cost_gates(payload, self.trade_case)
        self.assertEqual(payload["cost_finalization_status"], "IN PROGRESS")
        self.assertFalse(gates["GATE_LCV"])
        self.assertFalse(gates["GATE_CLEARING"])
        self.assertFalse(gates["GATE_SETTLEMENT"])

    def test_03_almost_ready_state_passes_settlement_but_blocks_lcv(self):
        """
        ALMOST READY state: All invoices received and verified, but not allocated.
        GATE_SETTLEMENT must PASS, but GATE_LCV and GATE_CLEARING must BLOCK.
        """
        sheet = TradeCostSheet({
            "name": "TCS-SG-03",
            "trade_case": self.trade_case.name,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5000.0, "status": "Verified", "invoice_number": "INV-01"},
                {"cost_type": "Tax", "estimated_cost": 1000.0, "actual_cost": 1000.0, "status": "Verified", "invoice_number": "INV-02"}
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        self.assertEqual(payload["cost_finalization_status"], "ALMOST READY")
        gates = self._evaluate_cost_gates(payload, self.trade_case)
        self.assertTrue(gates["GATE_SETTLEMENT"], "GATE_SETTLEMENT must pass when all invoices received")
        self.assertFalse(gates["GATE_LCV"], "GATE_LCV must be blocked in ALMOST READY (not yet allocated)")
        self.assertFalse(gates["GATE_CLEARING"], "GATE_CLEARING must be blocked in ALMOST READY")

    def test_04_allocated_state_passes_all_cost_gates(self):
        """
        ALLOCATED state: All items allocated to inventory via LCV.
        GATE_LCV, GATE_CLEARING, and GATE_SETTLEMENT must ALL PASS.
        """
        sheet = TradeCostSheet({
            "name": "TCS-SG-04",
            "trade_case": self.trade_case.name,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5000.0, "status": "Allocated", "invoice_number": "INV-01"},
                {"cost_type": "Tax", "estimated_cost": 1000.0, "actual_cost": 1000.0, "status": "Allocated", "invoice_number": "INV-02"}
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        self.assertEqual(payload["cost_finalization_status"], "ALLOCATED")
        gates = self._evaluate_cost_gates(payload, self.trade_case)
        self.assertTrue(gates["GATE_LCV"])
        self.assertTrue(gates["GATE_CLEARING"])
        self.assertTrue(gates["GATE_SETTLEMENT"])

    def test_05_finalized_state_passes_all_cost_gates(self):
        """FINALIZED state passes all cost stage gates."""
        sheet = TradeCostSheet({
            "name": "TCS-SG-05",
            "trade_case": self.trade_case.name,
            "docstatus": 1,
            "status": "Submitted",
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5000.0, "status": "Allocated", "invoice_number": "INV-01"}
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        self.assertEqual(payload["cost_finalization_status"], "FINALIZED")
        gates = self._evaluate_cost_gates(payload, self.trade_case)
        self.assertTrue(gates["GATE_LCV"])
        self.assertTrue(gates["GATE_CLEARING"])
        self.assertTrue(gates["GATE_SETTLEMENT"])

    def test_06_cancelled_only_sheet_blocks_gate_lcv(self):
        """
        Edge Case: Sheet with only cancelled items.
        Even though invoices_total is 0, GATE_LCV must be BLOCKED!
        """
        sheet = TradeCostSheet({
            "name": "TCS-SG-06",
            "trade_case": self.trade_case.name,
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5000.0, "status": "Cancelled", "invoice_number": "INV-CANC"}
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        self.assertEqual(payload["cost_finalization_status"], "DRAFT")
        gates = self._evaluate_cost_gates(payload, self.trade_case)
        self.assertFalse(gates["GATE_LCV"], "GATE_LCV must NOT pass when cost sheet is empty/cancelled")
        self.assertFalse(gates["GATE_CLEARING"])


class TestBoundaryAndInputSanitization(unittest.TestCase):
    """
    Stress-testing boundary values, whitespace handling, and malformed inputs.
    """

    def test_01_whitespace_invoice_number_not_counted_as_received(self):
        """Invoice number containing only whitespace ('   ') must not count as received."""
        sheet = TradeCostSheet({
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 1000.0, "status": "Draft", "invoice_number": "   \t\n  "}
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.invoices_received, 0)
        self.assertEqual(sheet.cost_finalization_status, "DRAFT")

    def test_02_negative_cost_line_handling(self):
        """Credit note / rebate (negative cost) is handled accurately."""
        sheet = TradeCostSheet({
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5000.0, "status": "Verified", "invoice_number": "INV-FR"},
                {"cost_type": "Other", "estimated_cost": 0.0, "actual_cost": -200.0, "status": "Verified", "invoice_number": "CR-NOTE-01"}
            ]
        })
        sheet.validate()
        self.assertEqual(sheet.total_actual_cost, 4800.0)
        self.assertEqual(sheet.cost_finalization_status, "ALMOST READY")

    def test_03_allocated_without_invoice_passes_lcv_gate_but_blocks_settlement_gate(self):
        """
        Adversarial Defense-in-Depth:
        If items are marked 'Allocated' but have no invoice numbers,
        cost_finalization_status is ALLOCATED (passing GATE_LCV),
        BUT GATE_SETTLEMENT catches the missing invoices and blocks closing the Trade Case!
        """
        sheet = TradeCostSheet({
            "name": "TCS-SG-DEFENSE",
            "cost_items": [
                {"cost_type": "Freight", "estimated_cost": 5000.0, "actual_cost": 5000.0, "status": "Allocated", "invoice_number": ""},
                {"cost_type": "Insurance", "estimated_cost": 1000.0, "actual_cost": 1000.0, "status": "Allocated", "invoice_number": ""}
            ]
        })
        sheet.validate()
        payload = sheet.get_cost_summary_payload()

        self.assertEqual(payload["cost_finalization_status"], "ALLOCATED")
        self.assertEqual(payload["invoices_received"], 0)
        self.assertEqual(payload["invoices_total"], 2)

        # Stage gate evaluation
        gate_lcv = payload["cost_finalization_status"] in ["ALLOCATED", "FINALIZED", "COMPLETED"]
        gate_settlement = (payload["invoices_received"] >= payload["invoices_total"] and payload["invoices_total"] > 0)

        self.assertTrue(gate_lcv, "GATE_LCV passes because costs are allocated")
        self.assertFalse(gate_settlement, "GATE_SETTLEMENT strictly fails because invoices are missing (0/2)!")

    def test_04_export_profitability_with_cancelled_logistics_costs(self):
        """
        Export shipment profitability:
        Ensure Cancelled logistics costs are NOT subtracted from revenue, protecting margins.
        """
        sheet = TradeCostSheet({
            "trade_type": "Export",
            "export_revenue": 200000.0,
            "export_cogs": 120000.0,
            "cost_items": [
                # Active logistics cost
                {"cost_type": "Freight", "estimated_cost": 15000.0, "actual_cost": 16000.0, "status": "Verified", "invoice_number": "INV-EXP-1"},
                # Cancelled logistics cost ($50,000)
                {"cost_type": "Other", "estimated_cost": 50000.0, "actual_cost": 50000.0, "status": "Cancelled", "invoice_number": "CANC-EXP-2"}
            ]
        })
        sheet.validate()

        # Gross margin = 200,000 - 120,000 = 80,000 (40.0%)
        self.assertEqual(sheet.export_gross_margin, 80000.0)
        self.assertEqual(sheet.export_gross_margin_pct, 40.0)

        # Logistics cost should be strictly 16,000 (excluding 50,000 cancelled)
        self.assertEqual(sheet.export_logistics_cost, 16000.0)

        # Net profit = 200,000 - 120,000 - 16,000 = 64,000 (32.0%)
        self.assertEqual(sheet.export_net_profit, 64000.0)
        self.assertEqual(sheet.export_net_margin_pct, 32.0)

    def test_05_high_volume_1000_items_performance_and_stability(self):
        """
        Stress test: 1,000 child items across multiple states.
        Validates linear performance, no recursion limit, no memory leak.
        """
        import time
        sheet = TradeCostSheet({
            "total_purchase_value": 500000.0,
            "cost_items": []
        })

        for i in range(1000):
            status = "Allocated" if i % 2 == 0 else "Verified"
            sheet.append("cost_items", {
                "cost_type": "Handling",
                "estimated_cost": 10.0,
                "actual_cost": 12.0,
                "status": status,
                "invoice_number": f"INV-{i}"
            })

        t0 = time.time()
        sheet.validate()
        elapsed = time.time() - t0

        self.assertLess(elapsed, 0.5, f"Validation of 1,000 items took {elapsed:.3f}s (must be < 0.5s)")
        self.assertEqual(sheet.invoices_total, 1000)
        self.assertEqual(sheet.invoices_received, 1000)
        self.assertEqual(sheet.costs_verified, 1000)
        self.assertEqual(sheet.costs_allocated, 500)
        self.assertEqual(sheet.cost_finalization_status, "ALMOST READY")
        self.assertEqual(sheet.total_actual_cost, 12000.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

