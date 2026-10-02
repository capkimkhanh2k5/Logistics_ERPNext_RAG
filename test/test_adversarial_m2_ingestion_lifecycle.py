#!/usr/bin/env python3
"""
test_adversarial_m2_ingestion_lifecycle.py — Adversarial & Lifecycle Test Harness for Milestone 2
================================================================================================
Thực hiện bởi: Empirical Challenger 2 (teamwork_preview_challenger_m2_2)

Bộ kiểm thử đối kháng thẩm định Ingestion Lifecycle & Exception Management:
1. Multi-Sync Lifecycle Simulation (Sync 1 -> 2 -> 3 -> 4):
   - Sync 1: On-time (ETA 2026-10-10) -> is_delayed=0, delay_days=0, exceptions=0
   - Sync 2: Delay +2 days (ETA 2026-10-12) -> is_delayed=1, delay_days=2, Exception Warning Open
   - Sync 3: Delay +4 days further (ETA 2026-10-16) -> is_delayed=1, Exception Critical Open
   - Sync 4: Carrier recovers on-time (ETA 2026-10-10) -> Audit is_delayed, delay_days, status, exception lifecycle
2. Child table `transit_route` DCSA milestone pollution check:
   - Audit presence of non-DCSA milestones (e.g., 'UNKNOWN', 'CUSTOMS_HOLD', 'NOISE') in child table
3. Idempotency on repeated syncs:
   - Verify duplicate exception suppression when carrier syncs repeatedly with same delay
4. Exception severity escalation:
   - Warning (1-2 days) -> Critical (>=3 days)
5. Initial sync with pre-existing delay detection audit:
   - Audit behavior when initial carrier ingestion already contains an ETA delay
"""

import os
import sys
import unittest
from datetime import datetime, date

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
)


class CustomScenarioProvider(BaseTrackingProvider):
    """Custom provider cho phép mô phỏng từng giai đoạn sync cụ thể."""
    provider_name: str = "Adversarial Carrier"

    def __init__(self,
                 eta: str,
                 initial_eta: str = "2026-10-10",
                 checkpoints: list = None,
                 status: str = "In Transit",
                 carrier: str = "Maersk"):
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


class TestAdversarialM2Lifecycle(unittest.TestCase):
    def setUp(self):
        in_memory_db.reset()

    # ==========================================================================
    # TEST 1: 4-STAGE MULTI-SYNC LIFECYCLE (SYNC 1 -> 2 -> 3 -> 4)
    # ==========================================================================
    def test_multi_sync_lifecycle_and_flags(self):
        """
        KỊCH BẢN ĐỐI KHÁNG 1:
        Mô phỏng carrier sync 4 lần liên tiếp:
        - Lần 1: On-time (ETA 10/10)
        - Lần 2: Delay +2 ngày (ETA 12/10) -> sinh Exception Warning
        - Lần 3: Delay tiếp +4 ngày (ETA 16/10) -> sinh Exception Critical
        - Lần 4: Cập nhật lại On-time (ETA 10/10) -> kiểm tra trạng thái exception lifecycle, cờ is_delayed, delay_days
        """
        shipment_name = "IMP-ADV-LIFECYCLE-001"

        # --- LẦN 1: On-Time ---
        p1 = CustomScenarioProvider(
            initial_eta="2026-10-10",
            eta="2026-10-10",
            status="In Transit",
            checkpoints=[
                {"milestone": "LOADED", "activity": "Container Loaded", "location": "Port of Long Beach", "timestamp": "2026-10-01 08:00"},
                {"milestone": "DEPARTED", "activity": "Vessel Departed", "location": "Port of Long Beach", "timestamp": "2026-10-01 12:00"}
            ]
        )
        r1 = sync_shipment_tracking_data(shipment_name, provider=p1)
        s1 = in_memory_db.get_shipment(shipment_name)

        self.assertEqual(s1.get("delay_days"), 0, "Sync 1: delay_days must be 0")
        self.assertEqual(s1.get("is_delayed"), 0, "Sync 1: is_delayed must be 0")
        self.assertEqual(s1.get("status"), "In Transit", "Sync 1: status must be 'In Transit'")
        self.assertEqual(len(in_memory_db.exceptions), 0, "Sync 1: No exceptions should exist")

        # --- LẦN 2: Delay +2 ngày (ETA = 2026-10-12) ---
        p2 = CustomScenarioProvider(
            initial_eta="2026-10-10",
            eta="2026-10-12",
            status="In Transit",
            checkpoints=[
                {"milestone": "TRANSSHIPMENT", "activity": "Transshipment Port Call", "location": "Busan Port", "timestamp": "2026-10-05 10:00"}
            ]
        )
        r2 = sync_shipment_tracking_data(shipment_name, provider=p2)
        s2 = in_memory_db.get_shipment(shipment_name)

        self.assertEqual(s2.get("delay_days"), 2, "Sync 2: delay_days must be 2")
        self.assertEqual(s2.get("is_delayed"), 1, "Sync 2: is_delayed must be 1")
        self.assertEqual(s2.get("status"), "Delayed", "Sync 2: status must be 'Delayed'")
        self.assertEqual(len(in_memory_db.exceptions), 1, "Sync 2: Exactly 1 exception should exist")
        exc_1 = list(in_memory_db.exceptions.values())[0]
        self.assertEqual(exc_1.get("severity"), "Warning", "Sync 2: Exception severity must be Warning (+2 days)")
        self.assertEqual(exc_1.get("delay_days"), 2, "Sync 2: Exception delay_days must be 2")
        self.assertEqual(exc_1.get("status"), "Open", "Sync 2: Exception status must be Open")

        # --- LẦN 3: Delay tiếp +4 ngày (ETA = 2026-10-16) ---
        p3 = CustomScenarioProvider(
            initial_eta="2026-10-10",
            eta="2026-10-16",
            status="In Transit",
            checkpoints=[
                {"milestone": "TRANSSHIPMENT", "activity": "Vessel Congestion Delay", "location": "Busan Port Outer Anchorage", "timestamp": "2026-10-07 14:00"}
            ]
        )
        r3 = sync_shipment_tracking_data(shipment_name, provider=p3)
        s3 = in_memory_db.get_shipment(shipment_name)

        self.assertEqual(s3.get("is_delayed"), 1, "Sync 3: is_delayed must be 1")
        self.assertEqual(s3.get("status"), "Delayed", "Sync 3: status must be 'Delayed'")
        critical_excs = [e for e in in_memory_db.exceptions.values() if e.get("severity") == "Critical"]
        self.assertGreaterEqual(len(critical_excs), 1, "Sync 3: Must produce a Critical exception (delay >= 3 days)")

        # --- LẦN 4: Cập nhật lại On-Time (ETA = 2026-10-10) ---
        p4 = CustomScenarioProvider(
            initial_eta="2026-10-10",
            eta="2026-10-10",
            status="In Transit",
            checkpoints=[
                {"milestone": "ARRIVED", "activity": "Vessel Arrived on Schedule", "location": "Cat Lai Port", "timestamp": "2026-10-10 06:00"}
            ]
        )
        r4 = sync_shipment_tracking_data(shipment_name, provider=p4)
        s4 = in_memory_db.get_shipment(shipment_name)

        # Record findings
        print("\n" + "=" * 80)
        print(" [OBSERVATION LOG] SYNC 4 (CARRIER RECOVERS TO ON-TIME)")
        print(f" ETA on Shipment: {s4.get('eta')} (Expected: 2026-10-10)")
        print(f" delay_days on Shipment: {s4.get('delay_days')} (Actual vs Expected: 0)")
        print(f" is_delayed on Shipment: {s4.get('is_delayed')} (Actual vs Expected: 0)")
        print(f" status on Shipment: {s4.get('status')} (Actual vs Expected: In Transit)")
        print(f" Total Exceptions in DB: {len(in_memory_db.exceptions)}")
        for eid, exc in in_memory_db.exceptions.items():
            print(f"   Exception {eid}: severity={exc.get('severity')}, status={exc.get('status')}, delay={exc.get('delay_days')}, new_eta={exc.get('new_eta')}")
        print("=" * 80)

        # Defect 1: is_delayed flag not cleared in shipment_dict when ETA returns on-time
        self.defect_is_delayed_stuck = (s4.get("is_delayed") == 1)
        # Defect 2: delay_days not reset to 0 in shipment_dict when ETA returns on-time
        self.defect_delay_days_stuck = (s4.get("delay_days") > 0)
        # Defect 3: Exception lifecycle does not auto-resolve or update open exceptions
        self.defect_exceptions_remain_open = all(e.get("status") == "Open" for e in in_memory_db.exceptions.values())

        print(f"Defect 1 (is_delayed stuck as 1): {self.defect_is_delayed_stuck}")
        print(f"Defect 2 (delay_days stuck as >0): {self.defect_delay_days_stuck}")
        print(f"Defect 3 (Exceptions remain Open): {self.defect_exceptions_remain_open}")

    # ==========================================================================
    # TEST 2: CHILD TABLE TRANSIT_ROUTE DCSA HYGIENE & POLLUTION
    # ==========================================================================
    def test_transit_route_child_table_dcsa_hygiene(self):
        """
        KỊCH BẢN ĐỐI KHÁNG 2:
        Kiểm tra child table `transit_route` có bị ô nhiễm các mốc ngoài 9 chuẩn DCSA không.
        Gửi các checkpoint với:
        - "Customs Hold at Port"
        - "Schedule Delay"
        - "Noise event in system"
        - "Order Cancelled"
        - "Container Discharged" (hợp lệ DCSA)
        - "Delivered to Consignee" (hợp lệ DCSA)
        """
        shipment_name = "IMP-ADV-HYGIENE-002"

        adversarial_checkpoints = [
            {
                "milestone": "Customs Hold at Port",
                "activity": "Container held by customs for physical inspection",
                "location": "Cat Lai Port Customs Area",
                "timestamp": "2026-10-08 09:00"
            },
            {
                "milestone": "Schedule Delay",
                "activity": "ETA postponed by carrier +2 days",
                "location": "Carrier System",
                "timestamp": "2026-10-08 10:00"
            },
            {
                "milestone": "Noise event in system",
                "activity": "Random carrier internal noise event",
                "location": "Unknown Station",
                "timestamp": "2026-10-08 11:00"
            },
            {
                "milestone": "Order Cancelled",
                "activity": "Booking cancelled by forwarder",
                "location": "Origin Station",
                "timestamp": "2026-10-08 12:00"
            },
            {
                "milestone": "Container Discharged from Vessel",
                "activity": "Discharged safely to yard",
                "location": "Cat Lai Port Yard B",
                "timestamp": "2026-10-10 14:00"
            },
            {
                "milestone": "Delivered to Consignee",
                "activity": "Proof of delivery signed",
                "location": "Customer Warehouse",
                "timestamp": "2026-10-11 16:00"
            }
        ]

        p = CustomScenarioProvider(
            initial_eta="2026-10-11",
            eta="2026-10-11",
            checkpoints=adversarial_checkpoints
        )

        r = sync_shipment_tracking_data(shipment_name, provider=p)
        shipment = in_memory_db.get_shipment(shipment_name)
        transit_route = shipment.get("transit_route", [])

        print("\n" + "=" * 80)
        print(" [OBSERVATION LOG] TRANSIT_ROUTE DCSA HYGIENE AUDIT")
        polluted_items = []
        for i, cp in enumerate(transit_route):
            m = cp.get("milestone")
            is_valid = m in DCSA_MILESTONES
            print(f"   CP #{i+1}: milestone='{m}', activity='{cp.get('activity')}', is_valid_dcsa={is_valid}")
            if not is_valid:
                polluted_items.append(cp)
        print(f" Total polluted checkpoints in transit_route: {len(polluted_items)}")
        print("=" * 80)

        # Defect 4: transit_route child table is polluted by 'UNKNOWN' milestone
        self.defect_transit_route_polluted = len(polluted_items) > 0
        print(f"Defect 4 (transit_route polluted with non-DCSA milestone): {self.defect_transit_route_polluted}")

    # ==========================================================================
    # TEST 3: EXCEPTION IDEMPOTENCY ON REPEATED IDENTICAL SYNCS
    # ==========================================================================
    def test_exception_idempotency_repeated_sync(self):
        """
        KỊCH BẢN ĐỐI KHÁNG 3:
        Khởi tạo shipment on-time, sau đó sync 10 lần liên tiếp với cùng dữ liệu ETA delay (ETA = 2026-10-12).
        Hệ thống không được tạo 10 exceptions trùng lặp.
        """
        shipment_name = "IMP-ADV-IDEMPOTENCY-003"
        # 1. Sync on-time
        p_init = CustomScenarioProvider(initial_eta="2026-10-10", eta="2026-10-10")
        sync_shipment_tracking_data(shipment_name, provider=p_init)

        # 2. Sync delay 10 times
        p_delayed = CustomScenarioProvider(
            initial_eta="2026-10-10",
            eta="2026-10-12",
            status="In Transit",
            checkpoints=[{"milestone": "DEPARTED", "location": "USLGB", "timestamp": "2026-10-01 10:00"}]
        )

        for i in range(10):
            sync_shipment_tracking_data(shipment_name, provider=p_delayed)

        excs = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shipment_name]
        print(f"\n[IDEMPOTENCY AUDIT] 10 repeated syncs with same delay -> Exception count = {len(excs)}")
        self.assertEqual(len(excs), 1, "Idempotency verified: exactly 1 exception exists, no duplicates")

    # ==========================================================================
    # TEST 4: PRE-EXISTING DELAY ON FIRST INGESTION AUDIT
    # ==========================================================================
    def test_preexisting_delay_on_first_ingestion(self):
        """
        KỊCH BẢN ĐỐI KHÁNG 4:
        Lô hàng mới được ingest lần đầu tiên, nhưng hãng vận chuyển đã báo ETA bị delay:
        initial_eta = 2026-10-10, eta = 2026-10-13 (delay +3 ngày).
        Kiểm tra hệ thống có nhận diện được delay ngay lần sync đầu tiên hay không.
        """
        shipment_name = "IMP-ADV-FIRST-DELAY-004"
        p = CustomScenarioProvider(
            initial_eta="2026-10-10",
            eta="2026-10-13",
            status="In Transit",
            checkpoints=[{"milestone": "DEPARTED", "location": "USLGB", "timestamp": "2026-10-01 10:00"}]
        )

        r = sync_shipment_tracking_data(shipment_name, provider=p)
        s = in_memory_db.get_shipment(shipment_name)
        excs = [e for e in in_memory_db.exceptions.values() if e.get("shipment_tracking") == shipment_name]

        print("\n" + "=" * 80)
        print(" [OBSERVATION LOG] FIRST INGESTION WITH PRE-EXISTING DELAY (+3 DAYS)")
        print(f" Shipment initial_eta: {s.get('initial_eta')}")
        print(f" Shipment current eta: {s.get('eta')}")
        print(f" Shipment delay_days: {s.get('delay_days')}")
        print(f" Shipment is_delayed: {s.get('is_delayed')}")
        print(f" Exceptions created count: {len(excs)}")
        print("=" * 80)

        # Defect 5: Initial sync with delay does NOT create exception because old_eta was None before assignment
        self.defect_first_sync_delay_missed = (len(excs) == 0 and s.get("delay_days") == 0)
        print(f"Defect 5 (First ingestion delay missed): {self.defect_first_sync_delay_missed}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
