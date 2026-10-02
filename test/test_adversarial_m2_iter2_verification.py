#!/usr/bin/env python3
"""
test_adversarial_m2_iter2_verification.py
Adversarial Verification Suite for Milestone 2 - Iteration 2 Challenger
Testing BUG-M2-01, BUG-M2-02, BUG-M2-03, BUG-M2-04 and Extended Adversarial Edge Cases.
"""

import os
import sys
import unittest
from datetime import datetime, date

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.dirname(TEST_DIR) if os.path.basename(TEST_DIR) == "test" else TEST_DIR
APP_DIR = os.path.join(BENCH_DIR, "apps", "logistics_wizard")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

from logistics_wizard.tracking_service import (
    DCSA_MILESTONES,
    normalize_milestone,
    TrackingResponse,
    BaseTrackingProvider,
    sync_shipment_tracking_data,
    in_memory_db,
)
from logistics_wizard.delay_engine import (
    calculate_delay_days,
    classify_severity,
    evaluate_eta_change,
    create_shipment_exception,
    apply_delay_to_shipment,
    auto_resolve_shipment_exceptions,
)


class MockCarrier(BaseTrackingProvider):
    provider_name = "Mock Carrier"

    def __init__(self, eta, initial_eta="2026-10-10", checkpoints=None, status="In Transit", carrier="Maersk"):
        self.eta = eta
        self.initial_eta = initial_eta
        self.checkpoints = checkpoints or []
        self.status = status
        self.carrier = carrier

    def fetch_tracking(self, tracking_number: str, carrier: str = None, **kwargs) -> TrackingResponse:
        return TrackingResponse(
            success=True,
            tracking_number=tracking_number,
            carrier=self.carrier,
            status=self.status,
            etd="2026-10-01",
            atd="2026-10-01",
            initial_eta=self.initial_eta,
            eta=self.eta,
            checkpoints=list(self.checkpoints),
            http_status_code=200
        )

    def parse_webhook(self, payload: dict, headers: dict = None) -> TrackingResponse:
        return self.fetch_tracking(payload.get("tracking_number", ""))

    def verify_webhook_signature(self, payload_bytes: bytes, headers: dict, secret: str) -> bool:
        return True


class TestM2Iter2EmpiricalChallenger(unittest.TestCase):
    def setUp(self):
        in_memory_db.reset()

    def test_bug_m2_01_state_desynchronization_strict(self):
        """BUG-M2-01: Verify is_delayed and delay_days reset to 0, status restored to In Transit."""
        name = "SHP-BUG01-TEST"
        # 1. Sync on-time
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))
        s1 = in_memory_db.get_shipment(name)
        self.assertEqual(s1["is_delayed"], 0)
        self.assertEqual(s1["delay_days"], 0)
        self.assertEqual(s1["status"], "In Transit")

        # 2. Sync delayed by 3 days
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-13"))
        s2 = in_memory_db.get_shipment(name)
        self.assertEqual(s2["is_delayed"], 1)
        self.assertEqual(s2["delay_days"], 3)
        self.assertEqual(s2["status"], "Delayed")

        # 3. Sync recovery on-time
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))
        s3 = in_memory_db.get_shipment(name)
        self.assertEqual(s3["is_delayed"], 0, "is_delayed must be 0 after recovery")
        self.assertEqual(s3["delay_days"], 0, "delay_days must be 0 after recovery")
        self.assertEqual(s3["status"], "In Transit", "status must be restored to In Transit")

    def test_bug_m2_02_exception_lifecycle_resolution_and_isolation(self):
        """BUG-M2-02: Verify Open exceptions are Resolved when recovered, without affecting other shipments."""
        shp_a = "SHP-RECOVER-A"
        shp_b = "SHP-STILL-DELAYED-B"

        # Both delayed
        sync_shipment_tracking_data(shp_a, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-14"))
        sync_shipment_tracking_data(shp_b, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-15"))

        excs_a_before = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shp_a]
        excs_b_before = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shp_b]
        self.assertEqual(len(excs_a_before), 1)
        self.assertEqual(excs_a_before[0]["status"], "Open")
        self.assertEqual(len(excs_b_before), 1)
        self.assertEqual(excs_b_before[0]["status"], "Open")

        # Now shp_a recovers to on-time
        sync_shipment_tracking_data(shp_a, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))

        excs_a_after = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shp_a]
        excs_b_after = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shp_b]

        self.assertEqual(excs_a_after[0]["status"], "Resolved", "shp_a exception must be Resolved")
        self.assertIn("recovered on schedule", excs_a_after[0].get("resolution_notes", "").lower())
        self.assertTrue(bool(excs_a_after[0].get("resolved_at")))

        # shp_b MUST STILL BE OPEN (isolation check)
        self.assertEqual(excs_b_after[0]["status"], "Open", "shp_b exception must remain Open")

    def test_bug_m2_03_child_table_dcsa_hygiene_strict(self):
        """BUG-M2-03: Verify transit_route excludes all non-DCSA checkpoints (0 UNKNOWN)."""
        name = "SHP-DCSA-HYGIENE"
        noisy_checkpoints = [
            {"milestone": "Customs Hold at Port", "activity": "Held by customs", "timestamp": "2026-10-01 10:00"},
            {"milestone": "LOADED", "activity": "Container Loaded", "timestamp": "2026-10-01 12:00"},
            {"milestone": "Order Cancelled", "activity": "Cancelled", "timestamp": "2026-10-01 14:00"},
            {"milestone": "Vessel Departed", "activity": "Vessel departed origin", "timestamp": "2026-10-01 16:00"},
            {"milestone": "System Noise Alert", "activity": "Noise in tracking telemetry", "timestamp": "2026-10-01 18:00"},
            {"milestone": "Container Discharged", "activity": "Discharged", "timestamp": "2026-10-05 10:00"},
            {"milestone": "DELIVERED", "activity": "Delivered", "timestamp": "2026-10-06 12:00"},
        ]

        sync_shipment_tracking_data(name, provider=MockCarrier(
            initial_eta="2026-10-06",
            eta="2026-10-06",
            checkpoints=noisy_checkpoints
        ))

        s = in_memory_db.get_shipment(name)
        route = s.get("transit_route", [])

        # Check milestones in route
        milestones = [cp.get("milestone") for cp in route]
        self.assertNotIn("UNKNOWN", milestones)
        self.assertNotIn("Customs Hold at Port", milestones)
        self.assertNotIn("Order Cancelled", milestones)
        self.assertNotIn("System Noise Alert", milestones)

        # All items must be valid DCSA
        for m in milestones:
            self.assertIn(m, DCSA_MILESTONES, f"Milestone '{m}' is not in DCSA_MILESTONES!")

        # Exactly 4 valid checkpoints should survive: LOADED, DEPARTED, DISCHARGED, DELIVERED
        self.assertEqual(len(route), 4)

    def test_bug_m2_04_first_ingestion_delay_detection_strict(self):
        """BUG-M2-04: Verify first sync with pre-existing delay creates exception and sets delay flags."""
        name = "SHP-FIRST-DELAY"
        p = MockCarrier(
            initial_eta="2026-10-10",
            eta="2026-10-14",  # +4 days delay
            checkpoints=[{"milestone": "LOADED", "activity": "Loaded", "timestamp": "2026-10-01 10:00"}]
        )
        sync_shipment_tracking_data(name, provider=p)

        s = in_memory_db.get_shipment(name)
        excs = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name]

        self.assertEqual(s.get("delay_days"), 4, "First sync delay_days must be 4")
        self.assertEqual(s.get("is_delayed"), 1, "First sync is_delayed must be 1")
        self.assertEqual(s.get("status"), "Delayed", "First sync status must be Delayed")
        self.assertEqual(len(excs), 1, "Exactly 1 exception must be created on first sync delay")
        self.assertEqual(excs[0]["severity"], "Critical", "4 days delay must be Critical severity")
        self.assertEqual(excs[0]["status"], "Open")

    def test_redelay_oscillation_lifecycle(self):
        """Adversarial Test: Delay -> Recover -> Delay Again -> Recover Again."""
        name = "SHP-OSCILLATE"
        # 1. Init on-time
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))
        # 2. Delay +2
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-12"))
        s2 = in_memory_db.get_shipment(name)
        self.assertEqual(s2["is_delayed"], 1)
        self.assertEqual(s2["delay_days"], 2)
        excs_1 = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name]
        self.assertEqual(len(excs_1), 1)
        self.assertEqual(excs_1[0]["status"], "Open")

        # 3. Recover to on-time
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))
        s3 = in_memory_db.get_shipment(name)
        self.assertEqual(s3["is_delayed"], 0)
        self.assertEqual(s3["delay_days"], 0)
        self.assertEqual(s3["status"], "In Transit")
        excs_2 = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name]
        self.assertEqual(excs_2[0]["status"], "Resolved")

        # 4. Re-delayed +5 days
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-15"))
        s4 = in_memory_db.get_shipment(name)
        self.assertEqual(s4["is_delayed"], 1)
        self.assertEqual(s4["delay_days"], 5)
        self.assertEqual(s4["status"], "Delayed")
        excs_3 = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name]
        self.assertEqual(len(excs_3), 2, "Second delay must generate a second exception")
        open_excs = [e for e in excs_3 if e["status"] == "Open"]
        self.assertEqual(len(open_excs), 1, "Only the new exception should be Open")
        self.assertEqual(open_excs[0]["severity"], "Critical")

        # 5. Recover again
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))
        s5 = in_memory_db.get_shipment(name)
        self.assertEqual(s5["is_delayed"], 0)
        self.assertEqual(s5["delay_days"], 0)
        self.assertEqual(s5["status"], "In Transit")
        excs_4 = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name]
        open_excs_final = [e for e in excs_4 if e["status"] == "Open"]
        self.assertEqual(len(open_excs_final), 0, "All exceptions should now be Resolved")

    def test_first_ingestion_edge_dates_early_and_exact(self):
        """Stress Test: First ingestion with early arrival or exact match."""
        # Case 1: Early arrival (2 days early)
        name_early = "SHP-EARLY-FIRST"
        sync_shipment_tracking_data(name_early, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-08"))
        s_early = in_memory_db.get_shipment(name_early)
        self.assertEqual(s_early["delay_days"], 0)
        self.assertEqual(s_early["is_delayed"], 0)
        self.assertEqual(s_early["status"], "In Transit")
        excs_early = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name_early]
        self.assertEqual(len(excs_early), 0)

        # Case 2: Exact on-time
        name_ontime = "SHP-ONTIME-FIRST"
        sync_shipment_tracking_data(name_ontime, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))
        s_ontime = in_memory_db.get_shipment(name_ontime)
        self.assertEqual(s_ontime["delay_days"], 0)
        self.assertEqual(s_ontime["is_delayed"], 0)
        excs_ontime = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name_ontime]
        self.assertEqual(len(excs_ontime), 0)

    def test_year_rollover_leap_year_recovery(self):
        """Stress Test: Leap year crossing 2028 with massive delay and subsequent on-time recovery."""
        name = "SHP-LEAP-ROLLOVER"
        # 1. First sync on-time: 2027-12-31
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2027-12-31", eta="2027-12-31"))

        # 2. Delayed into leap year 2028-03-01 (61 days delay)
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2027-12-31", eta="2028-03-01"))
        s_delayed = in_memory_db.get_shipment(name)
        self.assertEqual(s_delayed["delay_days"], 61)
        self.assertEqual(s_delayed["is_delayed"], 1)
        self.assertEqual(s_delayed["status"], "Delayed")
        excs = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == name]
        self.assertEqual(len(excs), 1)
        self.assertEqual(excs[0]["severity"], "Critical")
        self.assertEqual(excs[0]["status"], "Open")

        # 3. Recover to original date
        sync_shipment_tracking_data(name, provider=MockCarrier(initial_eta="2027-12-31", eta="2027-12-31"))
        s_recovered = in_memory_db.get_shipment(name)
        self.assertEqual(s_recovered["delay_days"], 0)
        self.assertEqual(s_recovered["is_delayed"], 0)
        self.assertEqual(s_recovered["status"], "In Transit")
        self.assertEqual(excs[0]["status"], "Resolved")

    def test_mass_concurrency_multi_shipments_recovery(self):
        """Stress Test: 20 distinct shipments, 10 remain delayed, 10 recover on-time."""
        for i in range(20):
            shp_id = f"SHP-MASS-{i:03d}"
            # All start delayed +3 days
            sync_shipment_tracking_data(shp_id, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-13"))

        # Now recover the first 10
        for i in range(10):
            shp_id = f"SHP-MASS-{i:03d}"
            sync_shipment_tracking_data(shp_id, provider=MockCarrier(initial_eta="2026-10-10", eta="2026-10-10"))

        # Verify state separation
        recovered_count = 0
        still_delayed_count = 0
        for i in range(20):
            shp_id = f"SHP-MASS-{i:03d}"
            s = in_memory_db.get_shipment(shp_id)
            excs = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shp_id]
            if i < 10:
                self.assertEqual(s["is_delayed"], 0)
                self.assertEqual(s["delay_days"], 0)
                self.assertEqual(s["status"], "In Transit")
                self.assertEqual(excs[0]["status"], "Resolved")
                recovered_count += 1
            else:
                self.assertEqual(s["is_delayed"], 1)
                self.assertEqual(s["delay_days"], 3)
                self.assertEqual(s["status"], "Delayed")
                self.assertEqual(excs[0]["status"], "Open")
                still_delayed_count += 1

        self.assertEqual(recovered_count, 10)
        self.assertEqual(still_delayed_count, 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
