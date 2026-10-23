#!/usr/bin/env python3
"""
test_tracking_service.py — Comprehensive Unit Test Suite for Milestone 1
========================================================================
Verification suite covering:
1. 9 DCSA Standard Milestones Normalization (Ocean & Air multi-carrier mapping)
2. SHA-256 Checkpoint Deduplication (Invariant hashing & idempotency)
3. Exponential Backoff with Full Jitter (AWS architecture algorithm & retry execution)
4. Tracking Providers (MockTrackingProvider scenarios & AfterShipProvider)
5. Stale Tracking Detection (>48 hours time-diff threshold)
6. Shipment Integration Logging (Audit trail & request/response payloads)
7. End-to-End Tracking Ingestion & Normalization Pipeline
8. Whitelisted API Integration (sync_shipment_tracking & tracking_webhook)
"""

import os
import sys
import time
import json
import hmac
import hashlib
from datetime import datetime, timedelta

# Set up path resolution
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.dirname(TEST_DIR) if os.path.basename(TEST_DIR) == "test" else TEST_DIR
APP_DIR = os.path.join(BENCH_DIR, "apps", "logistics_wizard")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

from logistics_wizard.tracking_service import (
    DCSA_MILESTONES,
    MILESTONE_SYNONYMS,
    normalize_milestone,
    compute_checkpoint_hash,
    filter_new_checkpoints,
    calculate_backoff_delay,
    execute_with_retry,
    TrackingResponse,
    BaseTrackingProvider,
    MockTrackingProvider,
    AfterShipProvider,
    is_tracking_stale,
    check_and_apply_stale_flag,
    log_integration_call,
    sync_shipment_tracking_data,
    in_memory_db,
)
import logistics_wizard.api as api


def log_header(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


# ==============================================================================
# TEST 1: 9 DCSA Standard Milestones Normalization
# ==============================================================================
def test_dcsa_milestone_normalization():
    log_header("TEST 1: 9 DCSA Standard Milestones Normalization")

    # 1. Exact match check for all 9 milestones
    for m in DCSA_MILESTONES:
        assert normalize_milestone(m) == m
        assert normalize_milestone(m.lower()) == m
        assert normalize_milestone(f"  {m}  ") == m
    print("[PASS] 100% exact match for 9 DCSA standard milestones")

    # 2. Ocean Carrier status mapping
    ocean_cases = [
        ("Booking Confirmed by Carrier", "BOOKED"),
        ("Space Confirmed and SO Issued", "BOOKED"),
        ("Container Gate In at Terminal Pier 400", "GATE_IN"),
        ("Cargo Drop-Off at Origin CFS", "GATE_IN"),
        ("Loaded on Vessel", "LOADED"),
        ("Container Loaded on Board", "LOADED"),
        ("Vessel Departed Port of Loading", "DEPARTED"),
        ("At Sea en route to Singapore", "DEPARTED"),
        ("Transshipment Arrival at Transit Port", "TRANSSHIPMENT"),
        ("Connecting Feeder Vessel Loading", "TRANSSHIPMENT"),
        ("Vessel Arrived at Port of Discharge", "ARRIVED"),
        ("Berthed at Cat Lai Berth 3", "ARRIVED"),
        ("Container Discharged to Terminal Yard", "DISCHARGED"),
        ("Cargo Unloaded from Vessel", "DISCHARGED"),
        ("Container Gate Out for Inland Delivery", "GATE_OUT"),
        ("Customs Cleared and Released", "GATE_OUT"),
        ("Cargo Delivered to Consignee Warehouse", "DELIVERED"),
        ("Proof of Delivery Signed by Receiver", "DELIVERED"),
    ]

    for raw, expected in ocean_cases:
        res = normalize_milestone(raw)
        assert res == expected, f"Failed for '{raw}': expected {expected}, got {res}"
    print(f"[PASS] Ocean Carrier statuses correctly mapped ({len(ocean_cases)} test cases)")

    # 3. Air Freight status mapping
    air_cases = [
        ("Air Waybill Issued / Order Created", "BOOKED"),
        ("Cargo Received at Airport Terminal", "GATE_IN"),
        ("Loaded on Aircraft ULD Pallet", "LOADED"),
        ("Flight Departed SFO Airborne", "DEPARTED"),
        ("Connecting Flight Transfer Hub", "TRANSSHIPMENT"),
        ("Flight Landed at Destination Airport", "ARRIVED"),
        ("Cargo De-van and Offloaded from Aircraft", "DISCHARGED"),
        ("Loaded on Truck for Last-Mile Delivery", "GATE_OUT"),
        ("Cargo Received at Destination Warehouse", "DELIVERED"),
    ]

    for raw, expected in air_cases:
        res = normalize_milestone(raw)
        assert res == expected, f"Failed for '{raw}': expected {expected}, got {res}"
    print(f"[PASS] Air Freight statuses correctly mapped ({len(air_cases)} test cases)")

    # 4. Fallback for completely unknown text
    assert normalize_milestone("Random Unknown Unmapped Text") == "DEPARTED"
    assert normalize_milestone("Random Unknown Unmapped Text", default="BOOKED") == "BOOKED"
    assert normalize_milestone(None) == "DEPARTED"
    assert normalize_milestone("") == "DEPARTED"
    print("[PASS] Fallback behavior verified for unknown/empty text")


# ==============================================================================
# TEST 2: SHA-256 Deduplication Engine
# ==============================================================================
def test_checkpoint_deduplication():
    log_header("TEST 2: SHA-256 Checkpoint Deduplication Engine")

    # 1. Deterministic hashing for identical inputs
    h1 = compute_checkpoint_hash("SHP-001", "DEPARTED", "Port of Long Beach", "2026-10-01 14:30", "MAERSK MC-KINNEY MOLLER")
    h2 = compute_checkpoint_hash("SHP-001", "DEPARTED", "Port of Long Beach", "2026-10-01 14:30", "MAERSK MC-KINNEY MOLLER")
    assert h1 == h2, "Hash must be strictly deterministic"
    assert len(h1) == 32, "Hash must be 32 hex characters"

    # 2. Case insensitivity and whitespace normalization
    h3 = compute_checkpoint_hash("shp-001", "departed", "  PORT   OF   LONG   BEACH  ", "2026-10-01 14:30", "maersk mc-kinney moller")
    assert h1 == h3, f"Whitespace & case normalization failed: {h1} vs {h3}"

    # 3. ISO timestamp variant normalization (with seconds or T separator)
    h4 = compute_checkpoint_hash("SHP-001", "DEPARTED", "Port of Long Beach", "2026-10-01T14:30:00.000Z", "MAERSK MC-KINNEY MOLLER")
    assert h1 == h4, f"ISO timestamp normalization failed: {h1} vs {h4}"

    # 4. Hash differentiation for distinct checkpoints
    h_diff_milestone = compute_checkpoint_hash("SHP-001", "ARRIVED", "Port of Long Beach", "2026-10-01 14:30", "MAERSK MC-KINNEY MOLLER")
    h_diff_loc = compute_checkpoint_hash("SHP-001", "DEPARTED", "Cat Lai Port", "2026-10-01 14:30", "MAERSK MC-KINNEY MOLLER")
    h_diff_time = compute_checkpoint_hash("SHP-001", "DEPARTED", "Port of Long Beach", "2026-10-02 14:30", "MAERSK MC-KINNEY MOLLER")
    h_diff_veh = compute_checkpoint_hash("SHP-001", "DEPARTED", "Port of Long Beach", "2026-10-01 14:30", "EVER GIVEN")

    assert h1 != h_diff_milestone
    assert h1 != h_diff_loc
    assert h1 != h_diff_time
    assert h1 != h_diff_veh
    print("[PASS] Hash collision avoidance and field sensitivity verified")

    # 5. Checkpoint list filtering (filter_new_checkpoints)
    existing = [
        {"milestone": "LOADED", "location": "Long Beach Pier 400", "timestamp": "2026-10-01 08:00", "vessel_or_flight": "V1", "dedup_hash": "hash_1"},
        {"milestone": "DEPARTED", "location": "Port of Long Beach", "timestamp": "2026-10-01 14:30", "vessel_or_flight": "V1", "dedup_hash": "hash_2"},
    ]

    # Incoming contains 2 existing duplicates and 1 new checkpoint
    incoming = [
        {"milestone": "LOADED", "location": "Long Beach Pier 400", "timestamp": "2026-10-01 08:00", "vessel_or_flight": "V1", "dedup_hash": "hash_1"},
        {"milestone": "DEPARTED", "location": "Port of Long Beach", "timestamp": "2026-10-01 14:30", "vessel_or_flight": "V1", "dedup_hash": "hash_2"},
        {"milestone": "TRANSSHIPMENT", "location": "Guam Oceanic Corridor", "timestamp": "2026-10-06 10:00", "vessel_or_flight": "V1"},
    ]

    filtered = filter_new_checkpoints("SHP-001", existing, incoming)
    assert len(filtered) == 1, f"Expected exactly 1 new checkpoint, got {len(filtered)}"
    assert filtered[0]["milestone"] == "TRANSSHIPMENT"
    assert "dedup_hash" in filtered[0]
    print("[PASS] Deduplication filter correctly rejected 2 duplicates and accepted 1 new checkpoint")


# ==============================================================================
# TEST 3: Exponential Backoff with Full Jitter
# ==============================================================================
def test_exponential_backoff_jitter():
    log_header("TEST 3: Exponential Backoff with Full Jitter")

    base = 1.0
    max_d = 32.0

    # 1. Delay bounds verification for attempts 0 to 5
    for attempt in range(6):
        upper_bound = min(max_d, base * (2 ** attempt))
        delays = [calculate_backoff_delay(attempt, base, max_d, full_jitter=True) for _ in range(50)]
        for d in delays:
            assert 0.0 <= d <= upper_bound, f"Delay {d} exceeded bound [0, {upper_bound}] on attempt {attempt}"

        # Jitter variance check (must not be all identical values)
        assert len(set(delays)) > 1, f"Jitter failed to randomize delays on attempt {attempt}"

    print("[PASS] Full Jitter delay adheres strictly to AWS formula (0 <= d <= min(max, base * 2^attempt))")

    # 2. execute_with_retry: transient failure recovery
    attempt_tracker = {"calls": 0}

    def flaky_network_call():
        attempt_tracker["calls"] += 1
        if attempt_tracker["calls"] < 3:
            raise ConnectionResetError("Remote server closed connection")
        return "SUCCESS_DATA"

    # Use a mock sleep function to avoid sleeping during tests
    slept_durations = []

    def mock_sleep(d):
        slept_durations.append(d)

    res, attempts, errors = execute_with_retry(
        func=flaky_network_call,
        max_retries=4,
        base_delay=0.1,
        max_delay=1.0,
        retryable_exceptions=(ConnectionResetError,),
        sleep_fn=mock_sleep
    )

    assert res == "SUCCESS_DATA"
    assert attempts == 2  # 0-indexed attempt index (attempt 0 failed, attempt 1 failed, attempt 2 succeeded)
    assert len(errors) == 2
    assert len(slept_durations) == 2
    print(f"[PASS] Retry mechanism recovered after 2 failures; simulated sleep durations: {slept_durations}")

    # 3. execute_with_retry: exceeding max retries
    def always_fail_call():
        raise TimeoutError("Gateway Timeout 504")

    failed = False
    try:
        execute_with_retry(
            func=always_fail_call,
            max_retries=2,
            base_delay=0.01,
            max_delay=0.1,
            retryable_exceptions=(TimeoutError,),
            sleep_fn=lambda d: None
        )
    except TimeoutError:
        failed = True

    assert failed is True, "Must raise after max retries exceeded"
    print("[PASS] Exhausted retries correctly raises underlying exception")


# ==============================================================================
# TEST 4: Tracking Providers (Mock & AfterShip)
# ==============================================================================
def test_tracking_providers():
    log_header("TEST 4: Tracking Providers (Mock & AfterShip)")

    # 1. Mock Tracking Provider - Scenario "departed"
    mock_p = MockTrackingProvider(scenario="departed")
    resp_dep = mock_p.fetch_tracking("TRK-TEST-001", carrier="Maersk Line")
    assert resp_dep.success is True
    assert resp_dep.tracking_number == "TRK-TEST-001"
    assert resp_dep.status == "In Transit"
    assert resp_dep.atd == "2026-10-01"
    assert resp_dep.eta == "2026-10-10"
    assert len(resp_dep.checkpoints) == 2
    assert resp_dep.checkpoints[0]["milestone"] == "LOADED"
    assert resp_dep.checkpoints[1]["milestone"] == "DEPARTED"
    assert resp_dep.checkpoints[1]["is_current"] is True
    print("[PASS] MockProvider 'departed' scenario verified")

    # 2. Mock Tracking Provider - Scenario "eta_delayed"
    mock_p.set_scenario("eta_delayed")
    resp_delay = mock_p.fetch_tracking("TRK-TEST-001", carrier="Maersk Line")
    assert resp_delay.eta == "2026-10-12"
    assert len(resp_delay.checkpoints) == 3
    assert resp_delay.checkpoints[2]["milestone"] == "TRANSSHIPMENT"
    print("[PASS] MockProvider 'eta_delayed' scenario verified (ETA=2026-10-12)")

    # 3. Mock Tracking Provider - Scenario "delivered"
    mock_p.set_scenario("delivered")
    resp_deliv = mock_p.fetch_tracking("TRK-TEST-001", carrier="Maersk Line")
    assert resp_deliv.status == "Completed"
    assert resp_deliv.ata == "2026-10-12"
    assert len(resp_deliv.checkpoints) == 7
    assert resp_deliv.checkpoints[-1]["milestone"] == "DELIVERED"
    print("[PASS] MockProvider 'delivered' scenario verified")

    # 4. Mock Tracking Provider - Scenario "air_flight"
    mock_p.set_scenario("air_flight")
    resp_air = mock_p.fetch_tracking("AWB-TEST-888", carrier="Vietnam Airlines")
    assert resp_air.flight_number == "VN001"
    assert len(resp_air.checkpoints) == 3
    assert resp_air.checkpoints[0]["milestone"] == "BOOKED"
    assert resp_air.checkpoints[1]["milestone"] == "LOADED"
    assert resp_air.checkpoints[2]["milestone"] == "DEPARTED"
    print("[PASS] MockProvider 'air_flight' scenario verified")

    # 5. AfterShip Signature Verification
    aftership_p = AfterShipProvider()
    secret = "secret_key_12345"
    payload_body = b'{"event":"tracking_update","msg":{"tracking_number":"1Z9999999999999999"}}'
    valid_sig = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()

    assert aftership_p.verify_webhook_signature(payload_body, {"aftership-hmac-sha256": valid_sig}, secret) is True
    assert aftership_p.verify_webhook_signature(payload_body, {"aftership-hmac-sha256": "wrong_signature"}, secret) is False
    print("[PASS] AfterShip HMAC SHA-256 signature verification verified")

    # 6. AfterShip Webhook Parsing
    webhook_payload = {
        "event": "tracking_update",
        "msg": {
            "tracking_number": "1Z9999999999999999",
            "slug": "ups",
            "tag": "InTransit",
            "shipment_pickup_date": "2026-10-01T09:00:00",
            "expected_delivery": "2026-10-10T17:00:00",
            "checkpoints": [
                {
                    "tag": "InfoReceived",
                    "message": "Shipping Label Created",
                    "checkpoint_time": "2026-10-01T07:00:00",
                    "city": "Cupertino"
                },
                {
                    "tag": "InTransit",
                    "message": "Vessel Departed Port",
                    "checkpoint_time": "2026-10-01T14:00:00",
                    "city": "Long Beach"
                }
            ]
        }
    }

    parsed = aftership_p.parse_webhook(webhook_payload)
    assert parsed.tracking_number == "1Z9999999999999999"
    assert parsed.status == "In Transit"
    assert parsed.etd == "2026-10-01"
    assert parsed.eta == "2026-10-10"
    assert len(parsed.checkpoints) == 2
    assert parsed.checkpoints[0]["milestone"] == "BOOKED"
    assert parsed.checkpoints[1]["milestone"] == "DEPARTED"
    print("[PASS] AfterShip webhook payload correctly converted to DCSA 9 milestones")


# ==============================================================================
# TEST 5: Stale Tracking Detection (>48 Hours)
# ==============================================================================
def test_stale_tracking_detection():
    log_header("TEST 5: Stale Tracking Detection (>48 Hours)")

    now = datetime(2026, 10, 5, 12, 0, 0)

    # 1. Fresh sync (10 hours ago) -> NOT Stale
    t_10h_ago = now - timedelta(hours=10)
    assert is_tracking_stale(t_10h_ago, threshold_hours=48, current_time=now) is False

    # 2. Boundary sync (47.5 hours ago) -> NOT Stale
    t_47h_ago = now - timedelta(hours=47, minutes=30)
    assert is_tracking_stale(t_47h_ago, threshold_hours=48, current_time=now) is False

    # 3. Stale sync (48.5 hours ago) -> STALE
    t_49h_ago = now - timedelta(hours=48, minutes=30)
    assert is_tracking_stale(t_49h_ago, threshold_hours=48, current_time=now) is True

    # 4. Long stale sync (5 days ago) -> STALE
    t_5d_ago = now - timedelta(days=5)
    assert is_tracking_stale(t_5d_ago, threshold_hours=48, current_time=now) is True

    # 5. String format parsing
    assert is_tracking_stale("2026-10-05 02:00:00", threshold_hours=48, current_time=now) is False
    assert is_tracking_stale("2026-10-01 12:00:00", threshold_hours=48, current_time=now) is True
    print("[PASS] Time difference calculation and 48-hour boundary check verified")

    # 6. Check and apply stale flag logic
    shipment_in_transit = {
        "status": "In Transit",
        "last_synced_at": (now - timedelta(hours=50)).strftime("%Y-%m-%d %H:%M:%S"),
        "is_stale": 0
    }
    stale_res = check_and_apply_stale_flag(shipment_in_transit, threshold_hours=48, current_time=now)
    assert stale_res is True
    assert shipment_in_transit["is_stale"] == 1
    print("[PASS] In Transit shipment past 48h automatically flagged is_stale = 1")

    # 7. Completed shipment should NEVER be flagged stale
    shipment_completed = {
        "status": "Completed",
        "last_synced_at": (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
        "is_stale": 0
    }
    stale_comp = check_and_apply_stale_flag(shipment_completed, threshold_hours=48, current_time=now)
    assert stale_comp is False
    assert shipment_completed["is_stale"] == 0
    print("[PASS] Completed shipment is exempted from Stale status")


# ==============================================================================
# TEST 6: Shipment Integration Logging
# ==============================================================================
def test_shipment_integration_logging():
    log_header("TEST 6: Shipment Integration Logging (Audit Trail)")

    in_memory_db.reset()

    log_id = log_integration_call(
        shipment_tracking="IMP-2026-001",
        direction="Outbound Polling",
        provider="Mock Provider",
        http_method="GET",
        endpoint_url="/api/trackings/maersk/IMP-2026-001",
        http_status_code=200,
        sync_status="Success",
        duration_ms=145,
        request_body={"tracking_number": "IMP-2026-001"},
        response_body={"status": "In Transit", "checkpoints_count": 2}
    )

    assert log_id.startswith("TRK-LOG-2026-")
    assert len(in_memory_db.integration_logs) == 1
    entry = in_memory_db.integration_logs[0]

    assert entry["shipment_tracking"] == "IMP-2026-001"
    assert entry["direction"] == "Outbound Polling"
    assert entry["provider"] == "Mock Provider"
    assert entry["http_status_code"] == 200
    assert entry["sync_status"] == "Success"
    assert entry["duration_ms"] == 145

    # Check JSON stringification
    req_json = json.loads(entry["request_body"])
    resp_json = json.loads(entry["response_body"])
    assert req_json["tracking_number"] == "IMP-2026-001"
    assert resp_json["checkpoints_count"] == 2
    print("[PASS] Shipment Integration Log recorded with complete payloads and metadata")


# ==============================================================================
# TEST 7: End-to-End Tracking Pipeline & Simulation Cycle
# ==============================================================================
def test_e2e_tracking_pipeline():
    log_header("TEST 7: End-to-End Tracking Ingestion & Normalization Cycle")

    in_memory_db.reset()

    # Step 1: Initial Sync (Vessel Departed, ATD 01/10, ETA 10/10)
    provider = MockTrackingProvider(scenario="departed")
    res1 = sync_shipment_tracking_data(
        shipment_name="IMP-2026-001",
        provider=provider,
        current_time=datetime(2026, 10, 1, 15, 0)
    )

    assert res1["success"] is True
    assert res1["new_checkpoints"] == 2
    assert res1["total_checkpoints"] == 2
    assert res1["is_stale"] == 0
    assert res1["eta"] == "2026-10-10"
    assert res1["atd"] == "2026-10-01"

    saved1 = in_memory_db.get_shipment("IMP-2026-001")
    assert saved1 is not None
    assert saved1["container_id"] == "ABC123"
    assert saved1["bill_of_lading"] == "BL-2026-MAERSK-01"
    assert saved1["vessel_name"] == "MAERSK MC-KINNEY MOLLER"
    assert len(saved1["transit_route"]) == 2
    assert saved1["transit_route"][1]["is_current"] == 1
    print("[PASS] Phase 1: Initial Ingestion synced 2 checkpoints (LOADED, DEPARTED)")

    # Step 2: Idempotent Re-sync (Duplicate Ingestion)
    res2 = sync_shipment_tracking_data(
        shipment_name="IMP-2026-001",
        provider=provider,
        current_time=datetime(2026, 10, 1, 15, 5)
    )
    assert res2["success"] is True
    assert res2["new_checkpoints"] == 0, "No duplicate checkpoints should be added"
    assert res2["total_checkpoints"] == 2, "Total checkpoints must remain 2"
    print("[PASS] Phase 2: Deduplication correctly prevented duplicate checkpoints")

    # Step 3: Updated ETA & Milestone (Transshipment & ETA = 12/10)
    provider.set_scenario("eta_delayed")
    res3 = sync_shipment_tracking_data(
        shipment_name="IMP-2026-001",
        provider=provider,
        current_time=datetime(2026, 10, 6, 11, 0)
    )
    assert res3["success"] is True
    assert res3["new_checkpoints"] == 1, "Only TRANSSHIPMENT checkpoint should be newly added"
    assert res3["total_checkpoints"] == 3
    assert res3["eta"] == "2026-10-12"

    saved3 = in_memory_db.get_shipment("IMP-2026-001")
    assert len(saved3["transit_route"]) == 3
    assert saved3["transit_route"][2]["milestone"] == "TRANSSHIPMENT"
    assert saved3["transit_route"][2]["is_current"] == 1
    assert saved3["transit_route"][1]["is_current"] == 0
    print("[PASS] Phase 3: Schedule update ingested TRANSSHIPMENT and updated ETA to 2026-10-12")

    # Step 4: Stale Condition Fast-Forward (>48h later)
    # Fast forward current time to 2026-10-09 (70 hours later without new sync)
    time_future = datetime(2026, 10, 9, 11, 0)
    stale_flag = check_and_apply_stale_flag(saved3, threshold_hours=48, current_time=time_future)
    assert stale_flag is True
    assert saved3["is_stale"] == 1
    print("[PASS] Phase 4: Stale condition (>48h elapsed) correctly flagged is_stale = 1")

    # Step 5: Final Delivery Ingestion
    provider.set_scenario("delivered")
    res5 = sync_shipment_tracking_data(
        shipment_name="IMP-2026-001",
        provider=provider,
        current_time=datetime(2026, 10, 12, 18, 0)
    )
    assert res5["success"] is True
    assert res5["status"] == "Completed"
    assert res5["total_checkpoints"] == 7
    assert res5["is_stale"] == 0

    saved5 = in_memory_db.get_shipment("IMP-2026-001")
    assert saved5["status"] == "Completed"
    assert saved5["transit_route"][-1]["milestone"] == "DELIVERED"
    assert saved5["transit_route"][-1]["is_current"] == 1
    print("[PASS] Phase 5: Final delivery completed with 7 milestones and is_stale reset to 0")


# ==============================================================================
# TEST 8: Whitelisted API Endpoints
# ==============================================================================
def test_whitelisted_api_endpoints():
    log_header("TEST 8: Whitelisted API Endpoints (sync_shipment_tracking & webhook)")

    # 1. sync_shipment_tracking API function
    res_api = api.sync_shipment_tracking(shipment_name="IMP-2026-001")
    assert res_api["success"] is True
    assert res_api["shipment"] == "IMP-2026-001"
    print("[PASS] api.sync_shipment_tracking executed successfully")

    # 2. tracking_webhook with Mock provider
    secret = "test-mock-secret-key"
    os.environ["MOCK_WEBHOOK_SECRET"] = secret

    payload_data = {
        "tracking_number": "IMP-2026-001",
        "scenario": "delivered"
    }
    payload_bytes = json.dumps(payload_data).encode("utf-8")
    valid_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    class MockRequest:
        def __init__(self, signature):
            self.headers = {"X-Mock-Signature": signature}
        def get_data(self):
            return payload_bytes

    # A. Valid signature -> Accepted
    api.frappe.request = MockRequest(valid_sig)
    res_wh = api.tracking_webhook(provider="mock")
    assert res_wh["success"] is True, f"Webhook with valid signature failed: {res_wh}"
    print("[PASS] api.tracking_webhook processed incoming event with valid signature")

    # B. Invalid signature -> Rejected
    api.frappe.request = MockRequest("forged_signature_12345")
    res_invalid = api.tracking_webhook(provider="mock")
    assert res_invalid["success"] is False, "Webhook with invalid signature must be rejected"
    assert "Chữ ký" in res_invalid.get("error", "") or "Signature" in res_invalid.get("error", "")
    print("[PASS] api.tracking_webhook correctly rejected invalid HMAC signature")


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================
if __name__ == "__main__":
    t_start = time.time()
    test_dcsa_milestone_normalization()
    test_checkpoint_deduplication()
    test_exponential_backoff_jitter()
    test_tracking_providers()
    test_stale_tracking_detection()
    test_shipment_integration_logging()
    test_e2e_tracking_pipeline()
    test_whitelisted_api_endpoints()

    elapsed = time.time() - t_start
    log_header(f"ALL MILESTONE 1 UNIT TESTS PASSED SUCCESSFULLY! (8/8 in {elapsed:.3f}s)")
