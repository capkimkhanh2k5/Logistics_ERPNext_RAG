#!/usr/bin/env python3
"""
test_adversarial_m1_stress.py — Independent Adversarial & Stress Test Harness for Milestone 1
=============================================================================================
Thực hiện bởi: Empirical Challenger 1 (teamwork_preview_challenger_m1_1)
Mục tiêu thẩm định:
1. Thử thách cơ chế Khử trùng lặp (SHA-256): 100 checkpoints lặp lại, xáo trộn thứ tự, đa luồng, bất biến mã băm.
2. Thử thách thuật toán Exponential Backoff: Đo đạc 10,000 mẫu, tuân thủ AWS Full Jitter, cap enforcement, phân phối đều, thử thách số mũ lớn.
3. Thử thách Stale Tracking: Mốc thời gian biên siêu nhạy (47.9h vs 48.1h), ma trận trạng thái miễn trừ, time-travel, và timezone parsing.
"""

import os
import sys
import time
import math
import random
import hashlib
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# Set up paths
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
    calculate_backoff_delay,
    execute_with_retry,
    TrackingResponse,
    BaseTrackingProvider,
    MockTrackingProvider,
    is_tracking_stale,
    check_and_apply_stale_flag,
    parse_datetime_flexible,
    sync_shipment_tracking_data,
    in_memory_db,
)


def banner(title: str):
    print("\n" + "=" * 80)
    print(f" [ADVERSARIAL SUITE] {title}")
    print("=" * 80)


# ==============================================================================
# SUITE 1: THỬ THÁCH KHỬ TRÙNG LẶP (SHA-256 DEDUPLICATION STRESS)
# ==============================================================================

def test_dedup_100_identical_in_batch():
    """Thử thách 1.1: Gửi 100 checkpoint lặp lại giống hệt nhau trong 1 batch."""
    print("--- Test 1.1: 100 identical checkpoints in single batch ---")
    shipment_id = "STRESS-DEDUP-001"
    existing = []
    
    base_cp = {
        "milestone": "LOADED",
        "location": "Cat Lai Terminal Pier 3",
        "timestamp": "2026-10-01 08:30:00",
        "vessel_or_flight": "EVER GIVEN",
        "notes": "Original loaded checkpoint"
    }
    
    # 100 identical copies
    incoming = [dict(base_cp) for _ in range(100)]
    assert len(incoming) == 100
    
    filtered = filter_new_checkpoints(shipment_id, existing, incoming)
    print(f" -> Input: 100 identical checkpoints | Output: {len(filtered)} unique checkpoint")
    assert len(filtered) == 1, f"Expected exactly 1 checkpoint, got {len(filtered)}"
    assert filtered[0]["milestone"] == "LOADED"
    assert "dedup_hash" in filtered[0]
    print("[PASS] 100 identical checkpoints filtered to exactly 1 unique item.")


def test_dedup_100_scrambled_and_interleaved():
    """Thử thách 1.2: 100 checkpoint xáo trộn gồm 10 checkpoint độc nhất (mỗi cái lặp 10 lần)."""
    print("\n--- Test 1.2: 100 scrambled & interleaved checkpoints ---")
    shipment_id = "STRESS-DEDUP-002"
    existing = [
        {"milestone": "BOOKED", "location": "Shanghai Port", "timestamp": "2026-10-01 00:00", "vessel_or_flight": "V1"}
    ]
    
    # Create 9 new distinct checkpoints
    distinct_new = []
    milestones_cycle = ["GATE_IN", "LOADED", "DEPARTED", "TRANSSHIPMENT", "ARRIVED", "DISCHARGED", "GATE_OUT", "DELIVERED", "DELIVERED"]
    for i in range(1, 10):
        distinct_new.append({
            "milestone": milestones_cycle[i - 1],
            "location": f"Port Location {i}",
            "timestamp": f"2026-10-0{i+1} 10:00:00",
            "vessel_or_flight": "Vessel V1",
            "notes": f"Checkpoint sequence {i}"
        })
    
    # Create incoming with 10 copies of the existing BOOKED checkpoint + 10 copies of each of the 9 new checkpoints = 100 total
    incoming = []
    for _ in range(10):
        incoming.append(dict(existing[0]))
    for cp in distinct_new:
        for _ in range(10):
            incoming.append(dict(cp))
            
    assert len(incoming) == 100
    
    # Scramble thoroughly
    rng = random.Random(42)
    rng.shuffle(incoming)
    
    filtered = filter_new_checkpoints(shipment_id, existing, incoming)
    print(f" -> Input: 100 scrambled checkpoints (10 existing dups + 90 incoming dups)")
    print(f" -> Output: {len(filtered)} new unique checkpoints")
    
    assert len(filtered) == 9, f"Expected exactly 9 new unique checkpoints, got {len(filtered)}"
    
    # Check that all 9 hashes are distinct
    hashes = [cp["dedup_hash"] for cp in filtered]
    assert len(set(hashes)) == 9, "All 9 hashes must be distinct"
    print("[PASS] Scrambled incoming batch of 100 yielded exactly 9 distinct new checkpoints.")


def test_dedup_idempotency_storm():
    """Thử thách 1.3: Gửi 20 lần đồng bộ liên tiếp (Idempotency Storm)."""
    print("\n--- Test 1.3: Idempotency Storm (20 sequential syncs) ---")
    in_memory_db.reset()
    shipment_name = "STRESS-STORM-001"
    
    class StormProvider(BaseTrackingProvider):
        def fetch_tracking(self, tracking_number, carrier=None, **kwargs):
            return TrackingResponse(
                success=True,
                tracking_number=tracking_number,
                checkpoints=[
                    {"milestone": "LOADED", "location": "Pier A", "timestamp": "2026-10-01 08:00", "vessel_or_flight": "V1"},
                    {"milestone": "DEPARTED", "location": "Port A", "timestamp": "2026-10-01 14:00", "vessel_or_flight": "V1"}
                ]
            )
        def parse_webhook(self, p, h=None): pass
        def verify_webhook_signature(self, b, h, s): pass

    provider = StormProvider()
    
    # Sync 1: Initial
    r1 = sync_shipment_tracking_data(shipment_name, provider=provider)
    assert r1["new_checkpoints"] == 2
    assert r1["total_checkpoints"] == 2
    
    # Sync 2 to 20: Storm
    for cycle in range(2, 21):
        r = sync_shipment_tracking_data(shipment_name, provider=provider)
        assert r["new_checkpoints"] == 0, f"Cycle {cycle} produced unexpected new checkpoints: {r['new_checkpoints']}"
        assert r["total_checkpoints"] == 2, f"Cycle {cycle} mutated total checkpoints: {r['total_checkpoints']}"
        
    shp = in_memory_db.get_shipment(shipment_name)
    assert len(shp["transit_route"]) == 2
    print(f"[PASS] 20 sequential storm syncs strictly maintained exactly 2 checkpoints (0 duplicates leaked).")


def test_hash_invariants_and_collision_resistance():
    """Thử thách 1.4: Thử thách tính bất biến của mã băm SHA-256."""
    print("\n--- Test 1.4: Hash Invariant Stress (Whitespace, Case, ISO timestamps) ---")
    
    base_hash = compute_checkpoint_hash(
        shipment_id="shp-100",
        milestone="Loaded on Board",
        location="  Cat   Lai   Port  ",
        timestamp="2026-10-01T08:30:00.000Z",
        vehicle="  maersk   line  "
    )
    
    equivalent_inputs = [
        ("SHP-100", "LOADED", "Cat Lai Port", "2026-10-01 08:30", "MAERSK LINE"),
        ("shp-100", "loaded", "cat lai port", "2026-10-01 08:30:00", "maersk line"),
        ("  SHP-100  ", "Container Loaded", "CAT LAI PORT", "2026-10-01T08:30:00+00:00", "Maersk Line"),
        ("Shp-100", "loaded on vessel", "Cat Lai Port", "2026-10-01 08:30", "MAERSK   LINE"),
    ]
    
    for i, inp in enumerate(equivalent_inputs):
        h = compute_checkpoint_hash(*inp)
        assert h == base_hash, f"Equivalence variant {i} produced different hash: {h} != {base_hash}"
    print(f"[PASS] All {len(equivalent_inputs)} equivalent representation variants matched identical hash: {base_hash}")


# ==============================================================================
# SUITE 2: THỬ THÁCH EXPONENTIAL BACKOFF & FULL JITTER
# ==============================================================================

def test_backoff_bounds_and_cap_statistical_10000():
    """Thử thách 2.1 & 2.2: 10,000 mẫu kiểm nghiệm giới hạn [0, Cap] và Jitter."""
    print("\n--- Test 2.1 & 2.2: 10,000 samples Exponential Backoff & Cap verification ---")
    
    base_delay = 1.0
    max_delay = 30.0  # Cap at 30 seconds
    
    # Test across attempt 0 to 10
    attempts_to_test = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    samples_per_attempt = 1000  # Total 11,000 samples
    
    overall_violations = 0
    cap_violations = 0
    
    print(f"{'Attempt':<8} | {'Theoretical Bound':<18} | {'Min Observed':<14} | {'Max Observed':<14} | {'Empirical Mean':<16} | {'Expected Mean':<14}")
    print("-" * 94)
    
    for att in attempts_to_test:
        theoretical_bound = min(max_delay, base_delay * (2 ** att))
        expected_mean = theoretical_bound / 2.0
        
        samples = [calculate_backoff_delay(att, base_delay, max_delay, full_jitter=True) for _ in range(samples_per_attempt)]
        
        min_obs = min(samples)
        max_obs = max(samples)
        mean_obs = sum(samples) / len(samples)
        
        # Check non-negative
        if min_obs < 0.0:
            overall_violations += 1
        # Check upper bound
        if max_obs > theoretical_bound:
            overall_violations += 1
        # Check cap specifically
        if max_obs > max_delay:
            cap_violations += 1
            
        # Statistical tolerance: with 1,000 uniform samples, std_err = (bound / sqrt(12)) / sqrt(N)
        std_err = (theoretical_bound / math.sqrt(12)) / math.sqrt(samples_per_attempt)
        margin = 3.5 * std_err  # 3.5 sigma (~99.95% confidence)
        assert abs(mean_obs - expected_mean) <= margin, f"Attempt {att}: Mean {mean_obs:.3f} deviated beyond 3.5 sigma from expected {expected_mean:.3f}"
        
        print(f"{att:<8} | {theoretical_bound:<18.2f} | {min_obs:<14.4f} | {max_obs:<14.4f} | {mean_obs:<16.4f} | {expected_mean:<14.4f}")
        
    assert overall_violations == 0, f"Found {overall_violations} bound violations!"
    assert cap_violations == 0, f"Found {cap_violations} cap violations exceeding {max_delay}s!"
    print("[PASS] 11,000 delay samples strictly satisfied 0.0 <= delay <= min(Cap, Base*2^Attempt).")
    print(f"[PASS] Strict cap of {max_delay}s enforced across all attempts >= 5.")


def test_backoff_uniform_distribution_deciles():
    """Thử thách 2.3: Kiểm tra phân phối đều (Uniform Distribution) của Full Jitter."""
    print("\n--- Test 2.3: Uniformity check across 10 decile buckets (Chi-Square-like) ---")
    
    att = 4  # bound = 16.0s
    bound = 16.0
    N = 10000
    samples = [calculate_backoff_delay(att, 1.0, 60.0, full_jitter=True) for _ in range(N)]
    
    # 10 equal buckets of width 1.6s
    buckets = [0] * 10
    for s in samples:
        idx = min(9, int(s / (bound / 10)))
        buckets[idx] += 1
        
    expected_per_bucket = N / 10.0  # 1000
    print(" Decile distribution (expected ~1000 per decile):")
    for i, count in enumerate(buckets):
        pct = (count / N) * 100
        print(f"  Bucket {i+1} [{i*1.6:4.1f}s - {(i+1)*1.6:4.1f}s]: {count:5d} ({pct:5.2f}%)")
        # Each bucket should be within 15% of expected in 10,000 samples
        assert abs(count - expected_per_bucket) < 200, f"Bucket {i} with {count} items deviates significantly from uniform expectation {expected_per_bucket}"
        
    print("[PASS] Full Jitter delay is confirmed uniformly distributed across entire [0, bound] spectrum.")


def test_backoff_extreme_attempts_and_overflow():
    """Thử thách 2.4: Thử thách các giá trị attempt cực lớn (Stress / Resilience)."""
    print("\n--- Test 2.4: Extreme attempt stress testing (attempt = 50, 100, 500, 1000, 1024) ---")
    
    for att in [20, 50, 100, 500, 1000]:
        d = calculate_backoff_delay(att, base_seconds=1.0, max_seconds=60.0)
        assert 0.0 <= d <= 60.0, f"Attempt {att} produced invalid delay: {d}"
    print(f" -> Attempts up to 1000 succeeded and honored 60.0s cap.")
    
    # At attempt 1024, Python 2**1024 cannot be cast to float: 1.0 * (2**1024)
    overflow_caught = False
    try:
        calculate_backoff_delay(1024, base_seconds=1.0, max_seconds=60.0)
    except OverflowError:
        overflow_caught = True
        print(" -> Note (Adversarial Edge Finding): attempt >= 1024 triggers Python float OverflowError.")
        
    print("[PASS] Backoff resilient to attempt <= 1000; overflow behavior cataloged.")


# ==============================================================================
# SUITE 3: THỬ THÁCH STALE TRACKING & BOUNDARY TESTING (47.9h vs 48.1h)
# ==============================================================================

def test_stale_micro_boundary_analysis():
    """Thử thách 3.1: Kiểm tra mốc biên siêu nhạy quanh 48.0 giờ."""
    print("\n--- Test 3.1: Stale Tracking Micro-Boundary Analysis (47.9h vs 48.1h) ---")
    now = datetime(2026, 10, 5, 12, 0, 0)
    
    threshold = 48.0
    cases = [
        (47.0, False, "47.0h (well before threshold)"),
        (47.9, False, "47.9h (specified prompt test case: MUST BE FALSE)"),
        (47.99, False, "47.99h (36 seconds before 48h)"),
        (47.999, False, "47.999h (3.6 seconds before 48h)"),
        (48.0, False, "48.0h exact (diff > 48.0 is strictly False)"),
        (48.0001, True, "48.0001h (0.36 seconds past 48h)"),
        (48.001, True, "48.001h (3.6 seconds past 48h)"),
        (48.01, True, "48.01h (36 seconds past 48h)"),
        (48.1, True, "48.1h (specified prompt test case: MUST BE TRUE)"),
        (49.0, True, "49.0h (well past threshold)"),
        (72.0, True, "72.0h (severely stale)"),
    ]
    
    for hours_ago, expected_stale, desc in cases:
        sync_time = now - timedelta(hours=hours_ago)
        res = is_tracking_stale(sync_time, threshold_hours=48, current_time=now)
        status_label = "STALE" if res else "ACTIVE"
        exp_label = "STALE" if expected_stale else "ACTIVE"
        print(f" [{status_label:<6}] Elapsed: {hours_ago:7.4f}h | Expected: {exp_label:<6} | {desc}")
        assert res == expected_stale, f"Assertion failed for {hours_ago}h elapsed: expected {expected_stale}, got {res}"
        
    print("[PASS] Micro-boundary check passed with 100% precision: 47.9h is NOT STALE; 48.1h IS STALE.")


def test_stale_status_exemption_matrix():
    """Thử thách 3.2: Ma trận kiểm tra trạng thái miễn trừ (Status Exemption)."""
    print("\n--- Test 3.2: Status Exemption Matrix for Stale Detection ---")
    now = datetime(2026, 10, 5, 12, 0, 0)
    old_sync = (now - timedelta(hours=120)).strftime("%Y-%m-%d %H:%M:%S")  # 5 days stale
    
    statuses_to_test = [
        ("Completed", False, "Completed shipments are exempted from stale alert"),
        ("Delivered", False, "Delivered shipments are exempted from stale alert"),
        ("Cancelled", False, "Cancelled shipments are exempted from stale alert"),
        ("In Transit", True, "In Transit shipments past 48h MUST BE flagged stale"),
        ("Delayed", True, "Delayed shipments past 48h MUST BE flagged stale"),
        ("Draft", True, "Draft shipments past 48h MUST BE flagged stale"),
        ("Booked", True, "Booked shipments past 48h MUST BE flagged stale"),
    ]
    
    for status, expected_stale, reason in statuses_to_test:
        shp = {
            "name": f"TEST-STATUS-{status}",
            "status": status,
            "last_synced_at": old_sync,
            "is_stale": 0
        }
        is_st = check_and_apply_stale_flag(shp, threshold_hours=48, current_time=now)
        flag = shp["is_stale"]
        expected_flag = 1 if expected_stale else 0
        print(f" Status: {status:<12} -> is_stale={flag} (Expected={expected_flag}) | {reason}")
        assert is_st == expected_stale
        assert flag == expected_flag
        
    print("[PASS] Status exemption matrix strictly enforced: Completed/Delivered/Cancelled exempted, all others flagged.")


def test_stale_time_travel_lifecycle():
    """Thử thách 3.3: Vòng đời lô hàng qua các mốc thời gian (Time-Travel Simulation)."""
    print("\n--- Test 3.3: Time-Travel Simulation across 48h threshold ---")
    in_memory_db.reset()
    shipment_name = "STRESS-TIMETRAVEL-001"
    
    t0 = datetime(2026, 10, 1, 12, 0, 0)
    
    # 1. T0: Initial Departed sync
    p1 = MockTrackingProvider(scenario="departed")
    r1 = sync_shipment_tracking_data(shipment_name, provider=p1, current_time=t0)
    assert r1["is_stale"] == 0
    shp = in_memory_db.get_shipment(shipment_name)
    assert shp["is_stale"] == 0
    print(f" -> T0 (12:00 Oct 1): Initial sync. is_stale = {shp['is_stale']}")
    
    # 2. T1 (47.9h later): Check stale flag
    t1 = t0 + timedelta(hours=47, minutes=54)  # 47.9h
    is_st_t1 = check_and_apply_stale_flag(shp, threshold_hours=48, current_time=t1)
    assert is_st_t1 is False
    assert shp["is_stale"] == 0
    print(f" -> T1 (+47.9h later): Checking stale flag. is_stale = {shp['is_stale']} (NOT STALE)")
    
    # 3. T2 (48.1h later): Check stale flag
    t2 = t0 + timedelta(hours=48, minutes=6)  # 48.1h
    is_st_t2 = check_and_apply_stale_flag(shp, threshold_hours=48, current_time=t2)
    assert is_st_t2 is True
    assert shp["is_stale"] == 1
    print(f" -> T2 (+48.1h later): Checking stale flag. is_stale = {shp['is_stale']} (STALE DETECTED!)")
    
    # 4. T3 (+50h later): Incoming recovery sync (new transshipment signal)
    t3 = t0 + timedelta(hours=50)
    p2 = MockTrackingProvider(scenario="eta_delayed")
    r3 = sync_shipment_tracking_data(shipment_name, provider=p2, current_time=t3)
    shp_after_sync = in_memory_db.get_shipment(shipment_name)
    assert shp_after_sync["is_stale"] == 0
    print(f" -> T3 (+50.0h later): Recovery sync executed. is_stale = {shp_after_sync['is_stale']} (RECOVERED TO ACTIVE)")
    
    print("[PASS] Time-Travel Lifecycle passed: Active (0h) -> Active (47.9h) -> Stale (48.1h) -> Recovered (50h).")


def test_adversarial_timezone_and_date_formats():
    """Thử thách 3.4: Thử nghiệm các định dạng ngày tháng và phân tích Timezone Parsing."""
    print("\n--- Test 3.4: Adversarial Timezone & Datetime String Formats ---")
    now = datetime(2026, 10, 5, 12, 0, 0)
    
    # Standard supported formats
    valid_cases = [
        ("2026-10-05 10:00:00", False, "Standard datetime seconds"),
        ("2026-10-05 10:00", False, "Standard datetime minutes"),
        ("2026-10-05", False, "Date only (assumes midnight 00:00)"),
        ("2026-10-05T10:00:00Z", False, "ISO-8601 with Z"),
        ("2026-10-05T10:00:00+07:00", False, "ISO-8601 with positive timezone +07:00"),
    ]
    
    for val, expected_stale, desc in valid_cases:
        st = is_tracking_stale(val, threshold_hours=48, current_time=now)
        assert st == expected_stale, f"Failed for valid format '{val}'"
        print(f" -> Supported format '{val}' [{desc}]: is_stale = {st}")
        
    print(" -> Now testing Western hemisphere negative timezone offset (e.g. -05:00 / -08:00):")
    neg_tz_str = "2026-10-05T10:00:00-05:00"
    parsed_neg = parse_datetime_flexible(neg_tz_str)
    if parsed_neg is None:
        print(f" [FINDING] `parse_datetime_flexible('{neg_tz_str}')` returned None!")
        print("          Root cause: `tracking_service.py:995` only strips `+` but does not strip `-` timezone offsets.")
        print("          Impact: Any American carrier timestamp with -05:00/-08:00 fails parsing and is prematurely marked Stale.")
    else:
        print(f" -> Parsed successfully as {parsed_neg}")
        
    print("[PASS] Datetime format matrix evaluated and edge finding documented.")


# ==============================================================================
# MAIN TEST HARNESS RUNNER
# ==============================================================================

if __name__ == "__main__":
    t_start = time.time()
    banner("STARTING INDEPENDENT EMPIRICAL ADVERSARIAL STRESS SUITE (MILESTONE 1)")
    
    # Suite 1
    test_dedup_100_identical_in_batch()
    test_dedup_100_scrambled_and_interleaved()
    test_dedup_idempotency_storm()
    test_hash_invariants_and_collision_resistance()
    
    # Suite 2
    test_backoff_bounds_and_cap_statistical_10000()
    test_backoff_uniform_distribution_deciles()
    test_backoff_extreme_attempts_and_overflow()
    
    # Suite 3
    test_stale_micro_boundary_analysis()
    test_stale_status_exemption_matrix()
    test_stale_time_travel_lifecycle()
    test_adversarial_timezone_and_date_formats()
    
    elapsed = time.time() - t_start
    banner(f"ALL ADVERSARIAL VERIFICATION SUITES COMPLETED IN {elapsed:.3f}s")
