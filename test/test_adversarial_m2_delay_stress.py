#!/usr/bin/env python3
"""
test_adversarial_m2_delay_stress.py — Comprehensive Adversarial Stress Test Suite for Milestone 2
===================================================================================================
Thực hiện bởi: EMPIRICAL CHALLENGER 1 (teamwork_preview_challenger_m2_1)
Kiến trúc thẩm định đối kháng: delay_engine.py & tracking_service.py

Mục tiêu kiểm thử hộp trắng thực nghiệm đối kháng (Adversarial White-box Empirical Stress Testing):
1. SUITE 1: Extreme Date Format Stress & Anomaly Parsing
   - ISO-8601 variations (T, Z, space, offsets +07:00, -05:00, +00:00, microseconds .123456, .999999).
   - Format matrix (%Y-%m-%d, %Y/%m/%d, %d-%m-%Y, %d/%m/%Y).
   - Dirty / Malformed / Non-date / Corrupt inputs (None, "", "   ", "null", "undefined", "2026-99-99", "2026-02-30", numbers, objects).
   - Zero-crash robustness: no unhandled exceptions under corrupt inputs.

2. SUITE 2: Calendar Transitions, Year-End, Leap Years & Epoch Spans
   - Year rollover: 2026-12-31 -> 2027-01-01 (1d), 2026-12-31 -> 2027-01-02 (2d), 2026-12-30 -> 2027-01-02 (3d).
   - Month transitions: 2026-01-31 -> 2026-02-01, 2026-04-30 -> 2026-05-01.
   - Leap year handling:
     * 2028 Leap Year: 2028-02-28 -> 2028-03-01 MUST BE 2 days (28 -> 29 -> 1).
     * 2028 Leap Day: 2028-02-29 -> 2028-03-01 MUST BE 1 day.
     * 2024 Leap Year: 2024-02-28 -> 2024-03-01 MUST BE 2 days.
     * Century leap (2000): 2000-02-28 -> 2000-03-01 = 2 days.
     * Non-leap (2027): 2027-02-28 -> 2027-03-01 = 1 day.
   - Extreme spans: 100 days, 365 days, 366 days, 10,000 days.
   - Early / On-schedule arrivals: 2027-01-01 -> 2026-12-31 -> 0 days.

3. SUITE 3: Severity Classification & Strict Boundary Matrix
   - Complete 3D truth table testing of (delay_days, vessel_changed, is_stale):
     * 0 days -> "Info"
     * 1 day -> "Warning"
     * 2 days -> "Warning"
     * 3 days -> "Critical" (Strict boundary)
     * 4 days -> "Critical"
     * 100 days -> "Critical"
     * Negative days (-5, -1) -> "Info"
     * vessel_changed=True at delay 0 -> "Critical" (MANDATORY REQUIREMENT)
     * vessel_changed=True at delay 1, 2, 3 -> "Critical"
     * is_stale=True at delay 0 -> "Warning"
     * is_stale=True at delay 3 -> "Critical" (Precedence verification)
     * vessel_changed=True AND is_stale=True -> "Critical"

4. SUITE 4: Polymorphic Contract & State Mutation Fidelity
   - Old ETA input variants: str, date, datetime, dict('eta'), dict('current_eta'), dict('initial_eta'),
     custom Doc objects with .eta or .get().
   - Missing ETA keys in dict/Doc -> graceful zero-delay handling without crashing.
   - apply_delay_to_shipment: in-place mutations of dicts and Document objects.
   - Status update validation: only marked "Delayed" when is_delayed == 1.

5. SUITE 5: Exception Creation Idempotency & Threading Stress
   - Sequential idempotency: 50 identical calls produce exactly 1 exception in database.
   - Concurrent idempotency: 20 concurrent threads attempting duplicate exception creation.
   - Revision progression: ETA 10/10 -> 12/10 (+2d, Warning) -> ETA 15/10 (+3d, Critical).
   - Multi-type coexistence: ETA Delay vs Stale Tracking exceptions for same shipment.

6. SUITE 6: Integrated End-to-End Simulation Pipeline & Hook Resilience
   - Facade check_and_process_delay with vessel change, multi-day delays, and on-time scenarios.
   - sync_shipment_tracking_data full lifecycle with MockTrackingProvider scenarios.
"""

import os
import sys
import time
import unittest
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor

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


class TestAdversarialM2DelayStress(unittest.TestCase):
    def setUp(self):
        in_memory_db.reset()

    # ==========================================================================
    # SUITE 1: EXTREME DATE FORMAT STRESS & ANOMALY PARSING
    # ==========================================================================
    def test_s1_01_iso8601_timezone_variations(self):
        """S1.01: Stress-test ISO-8601 variations with positive/negative timezone offsets and Z."""
        test_cases = [
            ("2026-10-10T14:30:00Z", date(2026, 10, 10)),
            ("2026-10-10T23:59:59+07:00", date(2026, 10, 10)),
            ("2026-10-10T00:00:01-05:00", date(2026, 10, 10)),
            ("2026-10-10T12:00:00+00:00", date(2026, 10, 10)),
            ("2026-10-10 14:30:00", date(2026, 10, 10)),
            ("2026-10-10 23:59:59.999999", date(2026, 10, 10)),
            ("2026-10-10T08:00:00.123456Z", date(2026, 10, 10)),
        ]
        for raw_val, expected_date in test_cases:
            parsed = parse_date_safely(raw_val)
            self.assertEqual(parsed, expected_date, f"Failed parsing ISO format: {raw_val}")

    def test_s1_02_slash_and_dash_international_formats(self):
        """S1.02: Stress-test standard date format separators: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, DD/MM/YYYY."""
        self.assertEqual(parse_date_safely("2026-10-25"), date(2026, 10, 25))
        self.assertEqual(parse_date_safely("2026/10/25"), date(2026, 10, 25))
        self.assertEqual(parse_date_safely("25-10-2026"), date(2026, 10, 25))
        self.assertEqual(parse_date_safely("25/10/2026"), date(2026, 10, 25))

    def test_s1_03_datetime_and_date_object_passthrough(self):
        """S1.03: Verify native Python date and datetime instances pass through safely."""
        d = date(2026, 12, 15)
        dt = datetime(2026, 12, 15, 18, 45, 30, 500)
        self.assertEqual(parse_date_safely(d), d)
        self.assertEqual(parse_date_safely(dt), d)

    def test_s1_04_dirty_and_malformed_inputs_zero_crash(self):
        """S1.04: Verify zero-crash policy for malformed, corrupt, or adversarial inputs."""
        corrupt_inputs = [
            None,
            "",
            "   ",
            "\t\n",
            "null",
            "NULL",
            "None",
            "none",
            "undefined",
            "UNDEFINED",
            "invalid-date-string",
            "2026-99-99",
            "2026-02-30",
            "2026-13-01",
            "0000-00-00",
            123456789,
            1791590400.0,
            True,
            False,
            [],
            {},
            object(),
        ]
        for bad_input in corrupt_inputs:
            # parse_date_safely must return None and never raise exception
            try:
                res = parse_date_safely(bad_input)
                self.assertIsNone(res, f"Expected None for dirty input: {bad_input!r}, got: {res}")
            except Exception as e:
                self.fail(f"parse_date_safely crashed on input {bad_input!r} with error: {e}")

            # calculate_delay_days must return 0 and never raise exception
            try:
                delay = calculate_delay_days(bad_input, "2026-10-10")
                self.assertEqual(delay, 0, f"Expected 0 delay for bad old_eta {bad_input!r}")
                delay2 = calculate_delay_days("2026-10-10", bad_input)
                self.assertEqual(delay2, 0, f"Expected 0 delay for bad new_eta {bad_input!r}")
            except Exception as e:
                self.fail(f"calculate_delay_days crashed on input {bad_input!r} with error: {e}")

    # ==========================================================================
    # SUITE 2: CALENDAR TRANSITIONS, LEAP YEARS & EPOCH SPANS
    # ==========================================================================
    def test_s2_01_year_boundary_crossover(self):
        """S2.01: Verify year boundary transition (New Year rollover)."""
        # 31/12/2026 -> 01/01/2027 (1 day delay)
        self.assertEqual(calculate_delay_days("2026-12-31", "2027-01-01"), 1)
        # 31/12/2026 -> 02/01/2027 (2 days delay)
        self.assertEqual(calculate_delay_days("2026-12-31", "2027-01-02"), 2)
        # 30/12/2026 -> 02/01/2027 (3 days delay)
        self.assertEqual(calculate_delay_days("2026-12-30", "2027-01-02"), 3)
        # 31/12/2026 -> 15/01/2027 (15 days delay)
        self.assertEqual(calculate_delay_days("2026-12-31", "2027-01-15"), 15)

    def test_s2_02_month_boundary_transitions(self):
        """S2.02: Verify month boundary transitions for 28, 30, and 31-day months."""
        # Jan 31 -> Feb 01 (1 day)
        self.assertEqual(calculate_delay_days("2026-01-31", "2026-02-01"), 1)
        # Feb 28 -> Mar 01 in non-leap year 2026 (1 day)
        self.assertEqual(calculate_delay_days("2026-02-28", "2026-03-01"), 1)
        # Apr 30 -> May 01 (1 day)
        self.assertEqual(calculate_delay_days("2026-04-30", "2026-05-01"), 1)
        # Dec 31 -> Jan 01 (1 day)
        self.assertEqual(calculate_delay_days("2025-12-31", "2026-01-01"), 1)

    def test_s2_03_leap_year_2028_empirical_verification(self):
        """S2.03: Comprehensive empirical verification of Leap Year 2028."""
        # In 2028, Feb 29 exists!
        # Feb 28 to Mar 01 must be EXACTLY 2 days (28 -> 29 -> 1)
        self.assertEqual(calculate_delay_days("2028-02-28", "2028-03-01"), 2)
        # Feb 28 to Feb 29 is 1 day
        self.assertEqual(calculate_delay_days("2028-02-28", "2028-02-29"), 1)
        # Feb 29 to Mar 01 is 1 day
        self.assertEqual(calculate_delay_days("2028-02-29", "2028-03-01"), 1)
        # Feb 27 to Mar 01 is 3 days
        self.assertEqual(calculate_delay_days("2028-02-27", "2028-03-01"), 3)

        # Contrast with non-leap year 2027
        self.assertEqual(calculate_delay_days("2027-02-28", "2027-03-01"), 1)

    def test_s2_04_century_leap_year_rules(self):
        """S2.04: Verify century leap year rules (2000 is leap, 1900 is not leap)."""
        # 2000 was a leap year (divisible by 400)
        self.assertEqual(calculate_delay_days("2000-02-28", "2000-03-01"), 2)
        # 2024 was a leap year
        self.assertEqual(calculate_delay_days("2024-02-28", "2024-03-01"), 2)

    def test_s2_05_extreme_multi_year_spans(self):
        """S2.05: Verify calculation over massive multi-month and multi-year spans."""
        # 100 days delay
        d_start = date(2026, 1, 1)
        d_100 = d_start + timedelta(days=100)
        self.assertEqual(calculate_delay_days(d_start, d_100), 100)

        # 365 days (non-leap year 2026)
        self.assertEqual(calculate_delay_days("2026-01-01", "2027-01-01"), 365)
        # 366 days (leap year 2028)
        self.assertEqual(calculate_delay_days("2028-01-01", "2029-01-01"), 366)
        # 10,000 days span
        d_10k = d_start + timedelta(days=10000)
        self.assertEqual(calculate_delay_days(d_start, d_10k), 10000)

    def test_s2_06_on_schedule_and_early_arrivals(self):
        """S2.06: Verify on-schedule and early arrivals consistently return 0 delay."""
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-10"), 0)
        self.assertEqual(calculate_delay_days("2026-10-10", "2026-10-09"), 0)
        self.assertEqual(calculate_delay_days("2027-01-01", "2026-12-31"), 0)
        self.assertEqual(calculate_delay_days("2028-03-01", "2028-02-28"), 0)

    # ==========================================================================
    # SUITE 3: SEVERITY CLASSIFICATION & BOUNDARY VALUE MATRIX
    # ==========================================================================
    def test_s3_01_severity_exact_threshold_matrix(self):
        """S3.01: Stress-test exact boundary values (0, 1, 2, 3, 100 days)."""
        # 0 days -> Info
        self.assertEqual(classify_severity(0), "Info")
        # Negative days -> Info
        self.assertEqual(classify_severity(-1), "Info")
        self.assertEqual(classify_severity(-10), "Info")

        # 1 day -> Warning
        self.assertEqual(classify_severity(1), "Warning")
        # 2 days -> Warning
        self.assertEqual(classify_severity(2), "Warning")

        # 3 days -> Critical (Strict threshold boundary!)
        self.assertEqual(classify_severity(3), "Critical")
        # 4 days -> Critical
        self.assertEqual(classify_severity(4), "Critical")
        # 100 days -> Critical
        self.assertEqual(classify_severity(100), "Critical")
        # 10,000 days -> Critical
        self.assertEqual(classify_severity(10000), "Critical")

    def test_s3_02_vessel_changed_override_to_critical(self):
        """S3.02: Verify vessel_changed=True enforces Critical severity under all delay values."""
        # Vessel changed with 0 days delay -> MUST BE CRITICAL
        self.assertEqual(classify_severity(0, vessel_changed=True), "Critical")
        # Vessel changed with negative delay -> MUST BE CRITICAL
        self.assertEqual(classify_severity(-2, vessel_changed=True), "Critical")
        # Vessel changed with 1 day delay (normally Warning) -> Escalates to CRITICAL
        self.assertEqual(classify_severity(1, vessel_changed=True), "Critical")
        # Vessel changed with 2 days delay (normally Warning) -> Escalates to CRITICAL
        self.assertEqual(classify_severity(2, vessel_changed=True), "Critical")
        # Vessel changed with 3+ days delay -> CRITICAL
        self.assertEqual(classify_severity(3, vessel_changed=True), "Critical")
        self.assertEqual(classify_severity(10, vessel_changed=True), "Critical")

    def test_s3_03_is_stale_flag_severity_interaction(self):
        """S3.03: Verify is_stale=True yields Warning when delay is 0, but Critical takes precedence."""
        # Stale with 0 delay -> Warning
        self.assertEqual(classify_severity(0, is_stale=True), "Warning")
        # Stale with 1-2 days delay -> Warning
        self.assertEqual(classify_severity(1, is_stale=True), "Warning")
        self.assertEqual(classify_severity(2, is_stale=True), "Warning")
        # Stale with 3+ days delay -> Critical dominates
        self.assertEqual(classify_severity(3, is_stale=True), "Critical")
        # Stale AND vessel_changed -> Critical dominates
        self.assertEqual(classify_severity(0, vessel_changed=True, is_stale=True), "Critical")

    # ==========================================================================
    # SUITE 4: POLYMORPHIC CONTRACT & STATE MUTATION FIDELITY
    # ==========================================================================
    def test_s4_01_evaluate_eta_change_polymorphic_signatures(self):
        """S4.01: Verify evaluate_eta_change accepts strings, date/datetime objects, dicts, and Doc objects."""
        # 1. Strings
        r1 = evaluate_eta_change("2026-10-10", "2026-10-13")
        self.assertEqual(r1["delay_days"], 3)
        self.assertEqual(r1["severity"], "Critical")
        self.assertEqual(r1["is_delayed"], 1)
        self.assertTrue(r1["create_exception"])

        # 2. Date objects
        r2 = evaluate_eta_change(date(2026, 10, 10), date(2026, 10, 12))
        self.assertEqual(r2["delay_days"], 2)
        self.assertEqual(r2["severity"], "Warning")
        self.assertTrue(r2["create_exception"])

        # 3. Dict with 'eta'
        doc_eta = {"name": "SH-01", "eta": "2026-10-10"}
        r3 = evaluate_eta_change(doc_eta, "2026-10-11")
        self.assertEqual(r3["delay_days"], 1)
        self.assertEqual(r3["severity"], "Warning")

        # 4. Dict with 'current_eta'
        doc_cur = {"name": "SH-02", "current_eta": "2026-10-10"}
        r4 = evaluate_eta_change(doc_cur, "2026-10-14")
        self.assertEqual(r4["delay_days"], 4)
        self.assertEqual(r4["severity"], "Critical")

        # 5. Dict with 'initial_eta'
        doc_init = {"name": "SH-03", "initial_eta": "2026-10-10"}
        r5 = evaluate_eta_change(doc_init, "2026-10-12")
        self.assertEqual(r5["delay_days"], 2)

        # 6. Object with .eta attribute
        class CustomDoc:
            def __init__(self, eta_val):
                self.eta = eta_val
        r6 = evaluate_eta_change(CustomDoc("2026-10-10"), "2026-10-15")
        self.assertEqual(r6["delay_days"], 5)
        self.assertEqual(r6["severity"], "Critical")

    def test_s4_02_vessel_changed_with_zero_delay_in_evaluate(self):
        """S4.02: Verify evaluate_eta_change correctly creates Critical exception when vessel changes without delay."""
        res = evaluate_eta_change("2026-10-10", "2026-10-10", vessel_changed=True)
        self.assertEqual(res["delay_days"], 0)
        self.assertEqual(res["is_delayed"], 0)
        self.assertEqual(res["severity"], "Critical")
        self.assertTrue(res["create_exception"])
        self.assertIn("Vessel change detected", res["description"])

    def test_s4_03_missing_or_corrupt_dates_in_evaluate(self):
        """S4.03: Verify evaluate_eta_change returns clean no-op dict when inputs are missing/corrupt."""
        res_none = evaluate_eta_change(None, "2026-10-12")
        self.assertEqual(res_none["delay_days"], 0)
        self.assertEqual(res_none["is_delayed"], 0)
        self.assertIsNone(res_none["severity"])
        self.assertFalse(res_none["create_exception"])

        res_corrupt = evaluate_eta_change("corrupt-date", "another-bad-date")
        self.assertEqual(res_corrupt["delay_days"], 0)
        self.assertFalse(res_corrupt["create_exception"])

    def test_s4_04_apply_delay_state_mutations(self):
        """S4.04: Verify apply_delay_to_shipment accurately mutates status and delay fields."""
        # Dict scenario with positive delay
        shipment_dict = {
            "name": "SHIP-MUTATE-1",
            "eta": "2026-10-10",
            "status": "In Transit",
            "delay_days": 0,
            "is_delayed": 0
        }
        eval_res = {
            "new_eta": "2026-10-13",
            "delay_days": 3,
            "is_delayed": 1
        }
        apply_delay_to_shipment(shipment_dict, eval_res)
        self.assertEqual(shipment_dict["eta"], "2026-10-13")
        self.assertEqual(shipment_dict["delay_days"], 3)
        self.assertEqual(shipment_dict["is_delayed"], 1)
        self.assertEqual(shipment_dict["status"], "Delayed")

        # Object with .set() method (Frappe-like)
        class MockFrappeDoc:
            def __init__(self):
                self.data = {"eta": "2026-10-10", "status": "In Transit", "delay_days": 0, "is_delayed": 0}
            def set(self, k, v):
                self.data[k] = v
            def get(self, k, default=None):
                return self.data.get(k, default)

        doc = MockFrappeDoc()
        apply_delay_to_shipment(doc, eval_res)
        self.assertEqual(doc.data["eta"], "2026-10-13")
        self.assertEqual(doc.data["delay_days"], 3)
        self.assertEqual(doc.data["is_delayed"], 1)
        self.assertEqual(doc.data["status"], "Delayed")

        # Zero delay scenario: status must NOT be changed to Delayed
        shipment_on_time = {
            "name": "SHIP-ONTIME",
            "eta": "2026-10-10",
            "status": "In Transit",
            "delay_days": 0,
            "is_delayed": 0
        }
        eval_zero = {
            "new_eta": "2026-10-10",
            "delay_days": 0,
            "is_delayed": 0
        }
        apply_delay_to_shipment(shipment_on_time, eval_zero)
        self.assertEqual(shipment_on_time["status"], "In Transit", "On-time arrival must keep In Transit status")
        self.assertEqual(shipment_on_time["delay_days"], 0)
        self.assertEqual(shipment_on_time["is_delayed"], 0)

    # ==========================================================================
    # SUITE 5: EXCEPTION CREATION IDEMPOTENCY & CONCURRENCY STRESS
    # ==========================================================================
    def test_s5_01_sequential_idempotency_50_iterations(self):
        """S5.01: Call create_shipment_exception 50 consecutive times with identical data."""
        shipment_name = "SHIP-IDEMP-SEQ"
        for i in range(50):
            create_shipment_exception(
                shipment_tracking=shipment_name,
                exception_type="ETA Delay",
                severity="Warning",
                old_eta="2026-10-10",
                new_eta="2026-10-12",
                delay_days=2,
                purchase_order="PO-IDEMP"
            )

        # Database must contain exactly 1 exception
        self.assertEqual(len(in_memory_db.exceptions), 1, "Idempotency violated: duplicate exceptions created!")
        exc = list(in_memory_db.exceptions.values())[0]
        self.assertEqual(exc["shipment_tracking"], shipment_name)
        self.assertEqual(exc["delay_days"], 2)
        self.assertEqual(exc["severity"], "Warning")

    def test_s5_02_concurrent_idempotency_multithreaded_burst(self):
        """S5.02: 20 threads simultaneously executing create_shipment_exception."""
        shipment_name = "SHIP-IDEMP-CONCUR"

        def worker_task(thread_id):
            return create_shipment_exception(
                shipment_tracking=shipment_name,
                exception_type="ETA Delay",
                severity="Critical",
                old_eta="2026-10-10",
                new_eta="2026-10-14",
                delay_days=4,
                purchase_order="PO-CONCUR",
                carrier="Maersk Line"
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(worker_task, range(20)))

        self.assertEqual(len(results), 20)
        # Note: in_memory_db is dictionary-based in single process
        matching = [e for e in in_memory_db.exceptions.values() if e["shipment_tracking"] == shipment_name]
        self.assertEqual(len(matching), 1, f"Concurrency race condition: expected 1 exception, got {len(matching)}")

    def test_s5_03_multiple_revisions_create_distinct_exceptions(self):
        """S5.03: Verify distinct revisions (different new_eta) properly record sequential exceptions."""
        shipment_name = "SHIP-REVISIONS"

        # Revision 1: +2 days delay (Warning)
        create_shipment_exception(
            shipment_tracking=shipment_name,
            exception_type="ETA Delay",
            severity="Warning",
            old_eta="2026-10-10",
            new_eta="2026-10-12",
            delay_days=2
        )
        self.assertEqual(len(in_memory_db.exceptions), 1)

        # Re-sync of Revision 1 (must NOT duplicate)
        create_shipment_exception(
            shipment_tracking=shipment_name,
            exception_type="ETA Delay",
            severity="Warning",
            old_eta="2026-10-10",
            new_eta="2026-10-12",
            delay_days=2
        )
        self.assertEqual(len(in_memory_db.exceptions), 1)

        # Revision 2: Carrier pushes further to 2026-10-16 (+4 days, Critical)
        create_shipment_exception(
            shipment_tracking=shipment_name,
            exception_type="ETA Delay",
            severity="Critical",
            old_eta="2026-10-12",
            new_eta="2026-10-16",
            delay_days=4
        )
        # Now there should be exactly 2 distinct exceptions
        self.assertEqual(len(in_memory_db.exceptions), 2)

        # Exception of different type (e.g., Stale Tracking)
        create_shipment_exception(
            shipment_tracking=shipment_name,
            exception_type="Stale Tracking",
            severity="Warning",
            description="Carrier signal silence > 48h"
        )
        self.assertEqual(len(in_memory_db.exceptions), 3)

    # ==========================================================================
    # SUITE 6: INTEGRATED PIPELINE & FACADE RESILIENCE
    # ==========================================================================
    def test_s6_01_check_and_process_delay_facade(self):
        """S6.01: Test high-level check_and_process_delay facade in on-time, delayed, and vessel-changed scenarios."""
        # 1. On-time scenario
        ship1 = {"name": "SH-F-1", "eta": "2026-10-10", "status": "In Transit"}
        r1 = check_and_process_delay(ship1, "2026-10-10")
        self.assertFalse(r1["exception_created"])
        self.assertEqual(ship1["status"], "In Transit")
        self.assertEqual(len(in_memory_db.exceptions), 0)

        # 2. Delayed scenario (+3 days)
        ship2 = {"name": "SH-F-2", "eta": "2026-10-10", "status": "In Transit"}
        r2 = check_and_process_delay(ship2, "2026-10-13")
        self.assertTrue(r2["exception_created"])
        self.assertEqual(r2["severity"], "Critical")
        self.assertEqual(ship2["status"], "Delayed")
        self.assertEqual(ship2["eta"], "2026-10-13")
        self.assertEqual(len(in_memory_db.exceptions), 1)

        # 3. Vessel changed with zero delay
        ship3 = {"name": "SH-F-3", "eta": "2026-10-10", "status": "In Transit"}
        r3 = check_and_process_delay(ship3, "2026-10-10", vessel_changed=True)
        self.assertTrue(r3["exception_created"])
        self.assertEqual(r3["severity"], "Critical")
        self.assertEqual(r3["delay_days"], 0)
        self.assertEqual(len(in_memory_db.exceptions), 2)

    def test_s6_02_full_ingestion_lifecycle_idempotent_syncs(self):
        """S6.02: Verify tracking_service sync with repeated identical payloads does not duplicate exceptions."""
        shipment_name = "IMP-M2-STRESS-LIFECYCLE"

        # Step 1: Initial Departed
        p1 = MockTrackingProvider(scenario="departed")
        r1 = sync_shipment_tracking_data(shipment_name, provider=p1)
        self.assertTrue(r1["success"])
        self.assertEqual(len(in_memory_db.exceptions), 0)

        # Step 2: Delayed (+2 days)
        p2 = MockTrackingProvider(scenario="eta_delayed")
        r2 = sync_shipment_tracking_data(shipment_name, provider=p2)
        self.assertTrue(r2["success"])
        self.assertEqual(r2["delay_days"], 2)
        self.assertTrue(r2["exception_created"])
        self.assertEqual(len(in_memory_db.exceptions), 1)

        # Step 3: Sync again with identical delayed data (re-sync idempotency)
        r3 = sync_shipment_tracking_data(shipment_name, provider=p2)
        self.assertTrue(r3["success"])
        self.assertEqual(len(in_memory_db.exceptions), 1, "Re-syncing identical delay duplicated exception!")

    # ==========================================================================
    # SUITE 7: MASSIVE RANDOM DATE FUZZING & ORACLE DIFFERENTIAL VERIFICATION
    # ==========================================================================
    def test_s7_01_random_10000_date_pairs_oracle_verification(self):
        """S7.01: Generate 10,000 random date pairs across 1970-2100 with random formatting and compare with oracle."""
        import random
        base_epoch = date(1970, 1, 1)
        max_days = (date(2100, 1, 1) - base_epoch).days

        formatters = [
            lambda d: d.isoformat(),
            lambda d: f"{d.year}/{d.month:02d}/{d.day:02d}",
            lambda d: f"{d.day:02d}-{d.month:02d}-{d.year}",
            lambda d: f"{d.day:02d}/{d.month:02d}/{d.year}",
            lambda d: f"{d.isoformat()}T14:30:00Z",
            lambda d: f"{d.isoformat()} 08:15:30.123456",
            lambda d: f"{d.isoformat()}T23:59:59+07:00",
            lambda d: d, # native date object
            lambda d: datetime.combine(d, datetime.min.time()), # native datetime object
        ]

        random.seed(42)
        for _ in range(10000):
            offset1 = random.randint(0, max_days)
            offset2 = random.randint(0, max_days)
            d1 = base_epoch + timedelta(days=offset1)
            d2 = base_epoch + timedelta(days=offset2)

            expected_delay = (d2 - d1).days if (d2 - d1).days > 0 else 0

            fmt1 = random.choice(formatters)
            fmt2 = random.choice(formatters)

            input1 = fmt1(d1)
            input2 = fmt2(d2)

            actual_delay = calculate_delay_days(input1, input2)
            self.assertEqual(
                actual_delay,
                expected_delay,
                f"Oracle mismatch: {input1} -> {input2}: expected {expected_delay}, got {actual_delay}"
            )

    # ==========================================================================
    # SUITE 8: CHAOS & TOXIC PAYLOAD INJECTION (ZERO-CRASH DEFENSE)
    # ==========================================================================
    def test_s8_01_toxic_and_chaos_payload_injection(self):
        """S8.01: Inject SQLi, XSS, unicode control chars, emojis, buffer overruns, format strings."""
        toxic_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE tabShipmentException; --",
            "<script>alert('pwned')</script>",
            "<img src=x onerror=alert(1)>",
            "\u202e2026-10-10", # RTL override
            "\u200b2026\u200b-\u200b10\u200b-\u200b10", # Zero-width space
            "🚢📦 2026-10-10 ⏰🚢",
            "2026-10-10\x00extra-data",
            "-2026-10-10",
            "999999999999-99-99",
            "%s%s%s%s%s%n%x",
            "A" * 10000,
            "\n\r\t" * 50,
            "NaN",
            "Infinity",
            "-Infinity",
            "{'eta': '2026-10-10'}",
            "['2026-10-10']",
            "b'2026-10-10'",
            "2026.10.10",
            "2026-Oct-10",
            "October 10, 2026",
            "10 Oct 2026",
        ]

        for payload in toxic_payloads:
            # 1. parse_date_safely
            res = parse_date_safely(payload)
            # Must return date or None, never crash
            self.assertTrue(res is None or isinstance(res, date))

            # 2. calculate_delay_days as old_eta
            d1 = calculate_delay_days(payload, "2026-10-12")
            self.assertIsInstance(d1, int)
            self.assertGreaterEqual(d1, 0)

            # 3. calculate_delay_days as new_eta
            d2 = calculate_delay_days("2026-10-10", payload)
            self.assertIsInstance(d2, int)
            self.assertGreaterEqual(d2, 0)

            # 4. evaluate_eta_change
            eval_res = evaluate_eta_change(payload, "2026-10-12")
            self.assertIsInstance(eval_res, dict)
            self.assertIn("delay_days", eval_res)
            self.assertIn("create_exception", eval_res)

    # ==========================================================================
    # SUITE 9: HIGH-CONCURRENCY MULTI-THREADED IDEMPOTENCY (100 WORKERS)
    # ==========================================================================
    def test_s9_01_high_concurrency_100_workers_idempotency(self):
        """S9.01: 100 concurrent workers hammering create_shipment_exception on same shipment and ETA."""
        shipment_name = "SHIP-HIGH-CONCUR-100"

        def hammer_worker(worker_id):
            return create_shipment_exception(
                shipment_tracking=shipment_name,
                exception_type="ETA Delay",
                severity="Critical",
                old_eta="2026-10-10",
                new_eta="2026-10-15",
                delay_days=5,
                purchase_order="PO-STRESS-100"
            )

        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(pool.map(hammer_worker, range(100)))

        self.assertEqual(len(results), 100)
        matching = [e for e in in_memory_db.exceptions.values() if e["shipment_tracking"] == shipment_name]
        self.assertEqual(len(matching), 1, f"High concurrency race: expected exactly 1 exception, got {len(matching)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

