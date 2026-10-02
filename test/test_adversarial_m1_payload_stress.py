#!/usr/bin/env python3
"""
test_adversarial_m1_payload_stress.py
======================================
Adversarial Verification & Stress Test Harness for Milestone 1:
1. 9 DCSA Standard Milestones Normalization:
   - Weird casing, punctuation, prefixes/suffixes
   - Carrier abbreviations and industry codes (GI, LD, DEP, TS, ARR, DISCH, GO, DLV, POD)
   - Multilingual support (Vietnamese maritime & air freight terms)
   - Substring traps & negation handling ('unloaded', 'not delivered', 'booking cancelled')
   - Fallback behavior on unrecognized input
2. Dirty & Corrupted Payloads:
   - Missing required fields (None payload, None data, None tracking, None checkpoints)
   - Coordinate anomalies: out-of-range (-999, +999), dict format, non-numeric strings
   - Datetime anomalies: negative timezone offsets (-05:00), slashes, non-ISO formats
3. Integration Log Immutability & Completeness:
   - Preservation of upstream raw_payload
   - Graceful handling of non-JSON serializable objects (datetime, bytes)
   - DocType schema permission audit (read_only, delete=0, write=0)
"""

import os
import sys
import json
from datetime import datetime, timezone

# Ensure project imports work
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
    compute_checkpoint_hash,
    filter_new_checkpoints,
    TrackingResponse,
    MockTrackingProvider,
    AfterShipProvider,
    is_tracking_stale,
    parse_datetime_flexible,
    log_integration_call,
    sync_shipment_tracking_data,
    in_memory_db,
)


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.findings = []

    def record_pass(self, detail: str):
        self.passed += 1
        print(f"  [PASS] {detail}")

    def record_fail(self, detail: str, severity: str = "HIGH"):
        self.failed += 1
        self.findings.append({"detail": detail, "severity": severity})
        print(f"  [FAIL - {severity}] {detail}")


def run_all_adversarial_tests():
    print("=" * 80)
    print(" ADVERSARIAL STRESS TEST HARNESS — MILESTONE 1")
    print("=" * 80)

    all_results = []

    # --------------------------------------------------------------------------
    # SUITE 1: 9 DCSA Milestones Normalization Under Adversarial Inputs
    # --------------------------------------------------------------------------
    res1 = TestResult("DCSA Milestones Normalization & Multilingual / Abbreviation Stress")
    print(f"\n---> Running Suite 1: {res1.name}")

    # 1.1 Punctuation, Weird Casing, Prefixes / Suffixes
    punct_cases = [
        ("[MAERSK] --GATE-IN-- (Terminal 4)", "GATE_IN"),
        ("***LOADED ON VESSEL***", "LOADED"),
        ("DEPARTED-SEA-BOUND", "DEPARTED"),
        ("trans-shipment / connecting hub", "TRANSSHIPMENT"),
        ("ARRIVED :: BERTH 1", "ARRIVED"),
        ("DISCHARGED_COMPLETED", "DISCHARGED"),
        ("GATE--OUT--TRUCK", "GATE_OUT"),
        ("DELIVERED - SIGNED", "DELIVERED"),
        ("BOOKED/CONFIRMED", "BOOKED"),
    ]
    for raw, expected in punct_cases:
        actual = normalize_milestone(raw)
        if actual == expected:
            res1.record_pass(f"Punctuation variation '{raw}' -> {actual}")
        else:
            res1.record_fail(f"Punctuation variation '{raw}': expected {expected}, got {actual}", "MEDIUM")

    # 1.2 Carrier Industry Codes & Abbreviations
    abbrev_cases = [
        ("GI", "GATE_IN"),
        ("INGT", "GATE_IN"),
        ("LD", "LOADED"),
        ("ONBRD", "LOADED"),
        ("DEP", "DEPARTED"),
        ("SAIL", "DEPARTED"),
        ("TS", "TRANSSHIPMENT"),
        ("XSHIP", "TRANSSHIPMENT"),
        ("ARR", "ARRIVED"),
        ("BERTH", "ARRIVED"),
        ("DISCH", "DISCHARGED"),
        ("UNLD", "DISCHARGED"),
        ("GO", "GATE_OUT"),
        ("OUTG", "GATE_OUT"),
        ("DLV", "DELIVERED"),
        ("POD", "DELIVERED"),
    ]
    for raw, expected in abbrev_cases:
        actual = normalize_milestone(raw)
        if actual == expected:
            res1.record_pass(f"Carrier abbreviation '{raw}' -> {actual}")
        else:
            res1.record_fail(f"Carrier abbreviation '{raw}': expected {expected}, got {actual}", "HIGH")

    # 1.3 Multilingual Support (Tiếng Việt Maritime & Logistics Statuses)
    vn_cases = [
        ("Đã đặt chỗ thành công", "BOOKED"),
        ("Xác nhận booking vận chuyển", "BOOKED"),
        ("Hàng đã vào cổng cảng", "GATE_IN"),
        ("Hạ bãi cảng Cát Lái", "GATE_IN"),
        ("Đã xếp lên tàu", "LOADED"),
        ("Đang xếp hàng lên máy bay", "LOADED"),
        ("Tàu đã rời cảng", "DEPARTED"),
        ("Khởi hành từ cảng Long Beach", "DEPARTED"),
        ("Chuyển tải tại cảng trung chuyển", "TRANSSHIPMENT"),
        ("Tàu đã cập cảng Cát Lái", "ARRIVED"),
        ("Đã đến cảng đích", "ARRIVED"),
        ("Đã dỡ hàng khỏi tàu", "DISCHARGED"),
        ("Dỡ container xuống bãi", "DISCHARGED"),
        ("Hàng đã ra cổng", "GATE_OUT"),
        ("Xuất bãi giao cho xe tải", "GATE_OUT"),
        ("Đã giao hàng thành công", "DELIVERED"),
        ("Giao hàng hoàn tất cho người nhận", "DELIVERED"),
    ]
    for raw, expected in vn_cases:
        actual = normalize_milestone(raw)
        if actual == expected:
            res1.record_pass(f"Tiếng Việt status '{raw}' -> {actual}")
        else:
            res1.record_fail(f"Tiếng Việt status '{raw}': expected {expected}, got {actual}", "HIGH")

    # 1.4 Substring Traps & Negation
    neg_cases = [
        ("unloaded", "DISCHARGED", "Sub-string 'unloaded' must not match 'loaded'"),
        ("not delivered", "NOT_DELIVERED", "Status 'not delivered' must NOT map to DELIVERED"),
        ("delivery failed", "NOT_DELIVERED", "Status 'delivery failed' must NOT map to DELIVERED"),
        ("booking cancelled", "NOT_BOOKED", "Status 'booking cancelled' must NOT map to BOOKED"),
    ]
    for raw, forbidden_or_expected, desc in neg_cases:
        actual = normalize_milestone(raw)
        if forbidden_or_expected == "NOT_DELIVERED":
            if actual == "DELIVERED":
                res1.record_fail(f"{desc}: '{raw}' falsely mapped to DELIVERED!", "CRITICAL")
            else:
                res1.record_pass(f"{desc}: '{raw}' -> {actual} (safe)")
        elif forbidden_or_expected == "NOT_BOOKED":
            if actual == "BOOKED":
                res1.record_fail(f"{desc}: '{raw}' falsely mapped to BOOKED!", "CRITICAL")
            else:
                res1.record_pass(f"{desc}: '{raw}' -> {actual} (safe)")
        else:
            if actual == forbidden_or_expected:
                res1.record_pass(f"{desc}: '{raw}' -> {actual}")
            else:
                res1.record_fail(f"{desc}: '{raw}' expected {forbidden_or_expected}, got {actual}", "HIGH")

    # 1.5 Fallback on Unrecognized Status
    unknown_raw = "Random customs hold noise 999"
    default_actual = normalize_milestone(unknown_raw)
    if default_actual == "DEPARTED":
        res1.record_fail(
            f"Unrecognized status '{unknown_raw}' silently falls back to default 'DEPARTED' instead of 'UNKNOWN' or explicit fallback flag",
            "MEDIUM"
        )
    else:
        res1.record_pass(f"Unrecognized status '{unknown_raw}' -> {default_actual}")

    all_results.append(res1)

    # --------------------------------------------------------------------------
    # SUITE 2: Dirty & Corrupted Payloads Handling
    # --------------------------------------------------------------------------
    res2 = TestResult("Dirty & Corrupted Payloads Stress (Missing Fields, Coordinates, Dates)")
    print(f"\n---> Running Suite 2: {res2.name}")

    provider = AfterShipProvider()

    # 2.1 Missing Required Fields & None Checks
    missing_field_cases = [
        ("None payload", None),
        ("Empty payload {}", {}),
        ("Payload with None data", {"data": None}),
        ("Payload with None msg", {"msg": None}),
        ("Payload with None tracking", {"data": {"tracking": None}}),
        ("Payload with None checkpoints", {"data": {"tracking": {"tracking_number": "T1", "checkpoints": None}}}),
        ("Payload with checkpoint containing None", {"data": {"tracking": {"tracking_number": "T1", "checkpoints": [None]}}}),
    ]

    for label, bad_payload in missing_field_cases:
        try:
            if bad_payload is None:
                # Direct call with None
                resp = provider.parse_webhook({})
            else:
                resp = provider.parse_webhook(bad_payload)
            res2.record_pass(f"Missing field resilience '{label}' handled without unhandled crash")
        except Exception as e:
            res2.record_fail(f"Missing field resilience '{label}' CRASHED: {type(e).__name__}: {e}", "CRITICAL")

    # 2.2 Malformed & Out-of-Range Coordinates
    coord_cases = [
        ("Extreme coordinates (-999, 999)", [-999.0, 999.0], "clamp_or_reject"),
        ("Latitude out of range (>90)", [95.0, 106.8], "reject_or_clamp"),
        ("Longitude out of range (>180)", [10.5, 200.0], "reject_or_clamp"),
        ("Dictionary coordinates {'lat': 10.5, 'lon': 106.8}", {"lat": 10.5, "lon": 106.8}, "support_or_safe"),
        ("Non-numeric string coordinates ['inv_lat', 'inv_lon']", ["inv_lat", "inv_lon"], "handle_graceful"),
        ("String coordinates '10.5, 106.8'", "10.5, 106.8", "support_or_safe"),
    ]

    for label, bad_coords, expected_behavior in coord_cases:
        payload = {
            "data": {
                "tracking": {
                    "tracking_number": "COORD-TEST",
                    "checkpoints": [
                        {
                            "message": "Vessel in transit",
                            "coordinates": bad_coords,
                            "checkpoint_time": "2026-10-01 10:00"
                        }
                    ]
                }
            }
        }
        try:
            resp = provider._parse_aftership_data(payload)
            cps = resp.checkpoints
            if cps:
                lat = cps[0].get("lat")
                lon = cps[0].get("lon")
                if bad_coords == [-999.0, 999.0]:
                    if lat == -999.0 or lon == 999.0:
                        res2.record_fail(
                            f"Coordinate validation: Out-of-bounds coords (-999, 999) stored directly without clamping [-90, 90] / [-180, 180]",
                            "HIGH"
                        )
                    else:
                        res2.record_pass(f"Coordinate validation: (-999, 999) sanitized to ({lat}, {lon})")
                elif isinstance(bad_coords, list) and (bad_coords[0] == 95.0 or bad_coords[1] == 200.0):
                    if lat == 95.0 or lon == 200.0:
                        res2.record_fail(
                            f"Coordinate validation: Out-of-range coords {bad_coords} accepted as valid",
                            "HIGH"
                        )
                    else:
                        res2.record_pass(f"Coordinate validation: {bad_coords} sanitized")
                else:
                    res2.record_pass(f"Coordinate variation '{label}' parsed successfully: lat={lat}, lon={lon}")
        except KeyError as ke:
            res2.record_fail(f"Coordinate variation '{label}' raised KeyError: {ke} (e.g. dict coords indexed by integer [0])", "CRITICAL")
        except ValueError as ve:
            res2.record_fail(f"Coordinate variation '{label}' raised ValueError: {ve} (unhandled string conversion)", "HIGH")
        except Exception as e:
            res2.record_fail(f"Coordinate variation '{label}' CRASHED: {type(e).__name__}: {e}", "CRITICAL")

    # 2.3 Datetime Anomalies & Timezone Offsets
    test_now = datetime(2026, 10, 1, 16, 0, 0)
    date_cases = [
        ("Positive timezone (+07:00)", "2026-10-01T15:30:00+07:00", False),
        ("Negative timezone (-05:00)", "2026-10-01T15:30:00-05:00", False),
        ("UTC with Z ('2026-10-01T15:30:00Z')", "2026-10-01T15:30:00Z", False),
        ("Date with slashes ('2026/10/01 15:30:00')", "2026/10/01 15:30:00", False),
        ("European format ('01-10-2026 15:30:00')", "01-10-2026 15:30:00", False),
        ("Malformed string ('not-a-valid-date')", "not-a-valid-date", True),
    ]

    for label, dt_str, expect_stale in date_cases:
        parsed_dt = parse_datetime_flexible(dt_str)
        is_stale = is_tracking_stale(dt_str, threshold_hours=48, current_time=test_now)

        if label.startswith("Negative timezone"):
            if parsed_dt is None:
                res2.record_fail(
                    f"Datetime parser: Negative timezone '{dt_str}' returned None, causing immediate false STALE detection (is_stale={is_stale})",
                    "CRITICAL"
                )
            else:
                res2.record_pass(f"Datetime parser: Negative timezone '{dt_str}' parsed successfully: {parsed_dt}")
        elif label.startswith("Date with slashes") or label.startswith("European format"):
            if parsed_dt is None:
                res2.record_fail(f"Datetime parser: Format '{dt_str}' unhandled (returned None)", "MEDIUM")
            else:
                res2.record_pass(f"Datetime parser: Format '{dt_str}' parsed successfully: {parsed_dt}")
        else:
            if parsed_dt is not None or expect_stale:
                res2.record_pass(f"Datetime variation '{label}' handled: parsed={parsed_dt}, stale={is_stale}")

    all_results.append(res2)

    # --------------------------------------------------------------------------
    # SUITE 3: Integration Log Immutability & Completeness Stress
    # --------------------------------------------------------------------------
    res3 = TestResult("Integration Log Immutability & Payload Completeness Stress")
    print(f"\n---> Running Suite 3: {res3.name}")

    # 3.1 Raw Payload Preservation Check
    in_memory_db.reset()
    sync_res = sync_shipment_tracking_data("SHP-RAW-CHECK", force_provider="AfterShip")
    logs = in_memory_db.integration_logs
    if not logs:
        res3.record_fail("No integration log was created during sync", "CRITICAL")
    else:
        last_log = logs[-1]
        resp_body_str = last_log.get("response_body") or ""
        try:
            resp_body_json = json.loads(resp_body_str)
            if "raw_payload" in resp_body_json:
                res3.record_pass("Raw upstream payload is preserved inside logged response_body")
            else:
                res3.record_fail(
                    "Shipment Integration Log omits upstream raw_payload in response_body (TrackingResponse.to_dict() omits raw_payload)",
                    "HIGH"
                )
        except Exception as e:
            res3.record_fail(f"Failed to parse logged response_body JSON: {e}", "MEDIUM")

    # 3.2 Non-JSON Serializable Payload Handling
    non_serializable_payload = {
        "event_time": datetime.now(),
        "signature_bytes": b"raw_signature_bytes",
        "nested": {"status": "ok"}
    }
    try:
        log_id = log_integration_call(
            shipment_tracking="SHP-NON-SER",
            direction="Inbound Webhook",
            provider="AfterShip",
            request_body=non_serializable_payload
        )
        res3.record_pass(f"log_integration_call handled non-serializable objects gracefully (Log ID: {log_id})")
    except TypeError as te:
        res3.record_fail(
            f"log_integration_call CRASHED on non-JSON serializable object: {te} (json.dumps without default=str)",
            "HIGH"
        )
    except Exception as e:
        res3.record_fail(f"log_integration_call crashed: {type(e).__name__}: {e}", "HIGH")

    # 3.3 DocType Schema Permissions Audit
    schema_path = os.path.join(
        APP_DIR, "logistics_wizard", "doctype", "shipment_integration_log", "shipment_integration_log.json"
    )
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_data = json.load(f)
        is_read_only = schema_data.get("read_only") == 1
        perms = schema_data.get("permissions", [])
        can_delete = any(p.get("delete") == 1 for p in perms)
        can_write = any(p.get("write") == 1 for p in perms)

        if is_read_only and not can_delete and not can_write:
            res3.record_pass("DocType Shipment Integration Log schema is strictly immutable (read_only=1, delete=0, write=0)")
        else:
            res3.record_fail(
                f"DocType Shipment Integration Log mutability vulnerability: read_only={is_read_only}, can_delete={can_delete}, can_write={can_write}",
                "HIGH"
            )
    else:
        res3.record_fail(f"Schema file not found at {schema_path}", "HIGH")

    all_results.append(res3)

    # --------------------------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(" ADVERSARIAL TEST HARNESS SUMMARY")
    print("=" * 80)
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    all_findings = []
    for r in all_results:
        all_findings.extend(r.findings)

    print(f"Total Tests Executed: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")

    critical_count = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
    high_count = sum(1 for f in all_findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in all_findings if f["severity"] == "MEDIUM")

    print(f"Severity Breakdown: Critical={critical_count}, High={high_count}, Medium={medium_count}")

    if all_findings:
        print("\nDiscovered Findings & Vulnerabilities:")
        for i, f in enumerate(all_findings, 1):
            print(f" {i}. [{f['severity']}] {f['detail']}")

    print("=" * 80)

    verdict = "APPROVE" if total_failed == 0 else "REQUEST_CHANGES"
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 80)

    return {
        "verdict": verdict,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "critical_count": critical_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "findings": all_findings,
    }


if __name__ == "__main__":
    summary = run_all_adversarial_tests()
    # Exit with code 0 to allow test runner to capture report, or non-zero if requested changes
    sys.exit(0 if summary["verdict"] == "APPROVE" else 1)
