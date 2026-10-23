#!/usr/bin/env python3
"""
test_delay_engine.py — Unit Test Suite for Milestone 2 (ETA Delay Engine & Exception Center)
=============================================================================================
Verification suite covering:
1. calculate_delay_days: positive delays, on-schedule, early arrivals, leap years, dirty inputs.
2. classify_severity: Critical (>=3 days or vessel_changed), Warning (1-2 days or is_stale), Info (0 days).
3. evaluate_eta_change: polymorphism (string, date, datetime, dict, Document), output schema.
4. create_shipment_exception: record creation, field fidelity, and idempotency protection.
5. apply_delay_to_shipment: in-place modification of shipment dict and Document objects.
6. Ingestion Integration: automatic delay detection and exception generation during sync.
"""

import os
import sys
import unittest
from datetime import datetime, date, timedelta

# Set up paths
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.dirname(TEST_DIR) if os.path.basename(TEST_DIR) == "test" else TEST_DIR
APP_DIR = os.path.join(BENCH_DIR, "apps", "logistics_wizard")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

from logistics_wizard.delay_engine import (
    parse_date_safely,
    calculate_delay_days,
    classify_severity,
    evaluate_eta_change,
    create_shipment_exception,
    apply_delay_to_shipment,
    check_and_process_delay,
)
from logistics_wizard.tracking_service import (
    sync_shipment_tracking_data,
    MockTrackingProvider,
    in_memory_db,
)


class TestDelayEngine(unittest.TestCase):
    def setUp(self):
        in_memory_db.reset()

    # ==========================================================================
    # 1. calculate_delay_days & parse_date_safely
    # ==========================================================================
    def test_calculate_delay_days_positive(self):
        """Verify positive delay days are computed accurately."""
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-12"), 2)
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-13"), 3)
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-17"), 7)
        self.assertEqual(calculate_delay_days("2026-01-01", "2027-01-01"), 365)

    def test_calculate_delay_days_same_and_early(self):
        """Verify on-schedule and early arrivals return 0 delay days."""
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-10"), 0)
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-08"), 0)
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-09-01"), 0)

    def test_calculate_delay_days_date_types_and_formats(self):
        """Verify support for date, datetime, ISO string with T, Z, and whitespace."""
        d1 = date(2026, 10, 10)
        d2 = date(2026, 10, 15)
        self.assertEqual(calculate_delay_days(d1, d2), 5)

        dt1 = datetime(2026, 10, 10, 14, 30)
        dt2 = datetime(2026, 10, 14, 8, 0)
        self.assertEqual(calculate_delay_days(dt1, dt2), 4)

        iso1 = "2026-10-10T14:30:00Z"
        iso2 = "2026-10-12T08:00:00"
        self.assertEqual(calculate_delay_days(iso1, iso2), 2)

    def test_calculate_delay_days_leap_year(self):
        """Verify 2028 leap year crossing February 28 to March 01 yields 2 days."""
        self.assertEqual(calculate_delay_days("2028-02-28", "2028-03-01"), 2)

    def test_calculate_delay_days_malformed_and_none(self):
        """Verify malformed and None inputs gracefully return 0 without raising exceptions."""
        self.assertEqual(calculate_delay_days(None, "2026-10-12"), 0)
        self.assertEqual(calculate_delay_days("2026-10-10", None), 0)
        self.assertEqual(calculate_delay_days(None, None), 0)
        self.assertEqual(calculate_delay_days("invalid-date", "2026-10-12"), 0)
        self.assertEqual(calculate_delay_days("2026-10-10", "corrupt"), 0)
        self.assertEqual(calculate_delay_days("", ""), 0)

    # ==========================================================================
    # 2. classify_severity
    # ==========================================================================
    def test_classify_severity_boundaries(self):
        """Verify classification boundaries for Warning, Critical, and Info."""
        # Warning: 1 or 2 days delay
        self.assertEqual(classify_severity(1), "Warning")
        self.assertEqual(classify_severity(2), "Warning")

        # Critical: >= 3 days delay
        self.assertEqual(classify_severity(3), "Critical")
        self.assertEqual(classify_severity(4), "Critical")
        self.assertEqual(classify_severity(10), "Critical")

        # Info: no delay
        self.assertEqual(classify_severity(0), "Info")
        self.assertEqual(classify_severity(-1), "Info")

    def test_classify_severity_flags(self):
        """Verify vessel_changed and is_stale impact on severity."""
        # vessel_changed escalates to Critical even if delay is 0 or 1
        self.assertEqual(classify_severity(0, vessel_changed=True), "Critical")
        self.assertEqual(classify_severity(1, vessel_changed=True), "Critical")

        # is_stale produces Warning when delay is 0
        self.assertEqual(classify_severity(0, is_stale=True), "Warning")
        # But if delay >= 3, Critical takes precedence
        self.assertEqual(classify_severity(3, is_stale=True), "Critical")

    # ==========================================================================
    # 3. evaluate_eta_change
    # ==========================================================================
    def test_evaluate_eta_change_string_inputs(self):
        """Verify evaluate_eta_change with string inputs produces compliant dict."""
        res = evaluate_eta_change("2026-10-10", "2026-10-12")
        self.assertEqual(res["delay_days"], 2)
        self.assertEqual(res["is_delayed"], 1)
        self.assertEqual(res["severity"], "Warning")
        self.assertTrue(res["create_exception"])
        self.assertIn("postponed by 2 days", res["description"])
        self.assertEqual(res["old_eta"], "2026-10-10")
        self.assertEqual(res["new_eta"], "2026-10-12")

    def test_evaluate_eta_change_polymorphism_dict_and_doc(self):
        """Verify evaluate_eta_change accepts dictionary or Document objects."""
        # Dict with 'eta'
        shipment_dict = {
            "name": "SHIP-001",
            "eta": "2026-10-10",
            "purchase_order": "PO-100"
        }
        res_dict = evaluate_eta_change(shipment_dict, "2026-10-14")
        self.assertEqual(res_dict["delay_days"], 4)
        self.assertEqual(res_dict["severity"], "Critical")
        self.assertTrue(res_dict["create_exception"])

        # Dict with 'current_eta'
        shipment_dict_alias = {
            "name": "SHIP-002",
            "current_eta": "2026-10-10",
        }
        res_alias = evaluate_eta_change(shipment_dict_alias, "2026-10-11")
        self.assertEqual(res_alias["delay_days"], 1)
        self.assertEqual(res_alias["severity"], "Warning")

        # Object with attribute
        class FakeDoc:
            def __init__(self):
                self.eta = "2026-10-10"
        res_obj = evaluate_eta_change(FakeDoc(), "2026-10-13")
        self.assertEqual(res_obj["delay_days"], 3)
        self.assertEqual(res_obj["severity"], "Critical")

    def test_evaluate_eta_change_on_time_and_early(self):
        """Verify no delay scenario returns create_exception=False and severity=None."""
        res_same = evaluate_eta_change("2026-10-10", "2026-10-10")
        self.assertEqual(res_same["delay_days"], 0)
        self.assertEqual(res_same["is_delayed"], 0)
        self.assertIsNone(res_same["severity"])
        self.assertFalse(res_same["create_exception"])

        res_early = evaluate_eta_change("2026-10-10", "2026-10-07")
        self.assertEqual(res_early["delay_days"], 0)
        self.assertEqual(res_early["is_delayed"], 0)
        self.assertFalse(res_early["create_exception"])

    # ==========================================================================
    # 4. create_shipment_exception & Idempotency
    # ==========================================================================
    def test_create_shipment_exception_and_idempotency(self):
        """Verify exception creation, field linkage, and prevention of duplicate exceptions."""
        exc1 = create_shipment_exception(
            shipment_tracking="SHIP-TEST-EXC",
            exception_type="ETA Delay",
            severity="Warning",
            old_eta="2026-10-10",
            new_eta="2026-10-12",
            delay_days=2,
            purchase_order="PO-TEST-EXC",
            carrier="Maersk Line",
            container_id="CONT999"
        )
        self.assertEqual(len(in_memory_db.exceptions), 1)
        self.assertEqual(exc1["shipment_tracking"], "SHIP-TEST-EXC")
        self.assertEqual(exc1["purchase_order"], "PO-TEST-EXC")
        self.assertEqual(exc1["delay_days"], 2)
        self.assertEqual(exc1["severity"], "Warning")

        # Calling again with identical parameters must not add a second exception
        exc2 = create_shipment_exception(
            shipment_tracking="SHIP-TEST-EXC",
            exception_type="ETA Delay",
            severity="Warning",
            old_eta="2026-10-10",
            new_eta="2026-10-12",
            delay_days=2,
            purchase_order="PO-TEST-EXC"
        )
        self.assertEqual(len(in_memory_db.exceptions), 1, "Idempotent re-sync must not duplicate exception")

    # ==========================================================================
    # 5. apply_delay_to_shipment
    # ==========================================================================
    def test_apply_delay_to_shipment(self):
        """Verify shipment dict/doc fields update correctly upon delay application."""
        shipment = {
            "name": "SHIP-APPLY",
            "eta": "2026-10-10",
            "status": "In Transit",
            "delay_days": 0,
            "is_delayed": 0
        }
        eval_res = {
            "delay_days": 3,
            "is_delayed": 1,
            "severity": "Critical",
            "new_eta": "2026-10-13"
        }
        apply_delay_to_shipment(shipment, eval_res)
        self.assertEqual(shipment["eta"], "2026-10-13")
        self.assertEqual(shipment["delay_days"], 3)
        self.assertEqual(shipment["is_delayed"], 1)
        self.assertEqual(shipment["status"], "Delayed")

    # ==========================================================================
    # 6. Ingestion Pipeline Hook Integration
    # ==========================================================================
    def test_ingestion_pipeline_delay_hook(self):
        """Verify full sync_shipment_tracking_data triggers delay engine and creates exception."""
        # 1. Initial departed sync
        p1 = MockTrackingProvider(scenario="departed")
        r1 = sync_shipment_tracking_data(
            shipment_name="IMP-TEST-DELAY-SYNC",
            provider=p1,
            current_time=datetime(2026, 10, 1, 12, 0)
        )
        self.assertTrue(r1["success"])
        self.assertEqual(r1["delay_days"], 0)
        self.assertFalse(r1["exception_created"])
        self.assertEqual(len(in_memory_db.exceptions), 0)

        # 2. Delayed sync (ETA moves from 10/10 to 12/10)
        p2 = MockTrackingProvider(scenario="eta_delayed")
        r2 = sync_shipment_tracking_data(
            shipment_name="IMP-TEST-DELAY-SYNC",
            provider=p2,
            current_time=datetime(2026, 10, 6, 10, 0)
        )
        self.assertTrue(r2["success"])
        self.assertEqual(r2["delay_days"], 2)
        self.assertEqual(r2["is_delayed"], 1)
        self.assertTrue(r2["exception_created"])
        self.assertEqual(r2["status"], "Delayed")

        # Verify exception was stored
        self.assertEqual(len(in_memory_db.exceptions), 1)
        exc = list(in_memory_db.exceptions.values())[0]
        self.assertEqual(exc["shipment_tracking"], "IMP-TEST-DELAY-SYNC")
        self.assertEqual(exc["delay_days"], 2)
        self.assertEqual(exc["severity"], "Warning")
        self.assertEqual(exc["status"], "Open")

        # 3. Delivered sync (Status should update to Completed)
        p3 = MockTrackingProvider(scenario="delivered")
        r3 = sync_shipment_tracking_data(
            shipment_name="IMP-TEST-DELAY-SYNC",
            provider=p3,
            current_time=datetime(2026, 10, 12, 18, 0)
        )
        self.assertTrue(r3["success"])
        self.assertEqual(r3["status"], "Completed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
