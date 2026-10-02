# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
Unit & Integration Tests for Shipment Tracking Hub API
Endpoints:
- logistics_wizard.api.get_shipment_tracking_hub_data
- logistics_wizard.api.sync_shipment_now
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# Ensure repo & app root are on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "apps", "logistics_wizard")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from logistics_wizard.api import (
    get_shipment_tracking_hub_data,
    sync_shipment_now,
    get_in_memory_db,
)
from logistics_wizard.tracking_service import (
    sync_shipment_tracking_data,
    MockTrackingProvider,
)
from logistics_wizard.delay_engine import (
    evaluate_eta_change,
    create_shipment_exception,
)


class TestShipmentTrackingHubAPI(unittest.TestCase):
    def setUp(self):
        # Reset and seed in-memory database
        self.db = get_in_memory_db()
        self.db.reset()

        # Seed Shipments
        self.db.shipments["SH-TEST-001"] = {
            "name": "SH-TEST-001",
            "tracking_number": "TRK-001",
            "container_id": "CONT-001",
            "carrier": "Maersk Line",
            "shipping_method": "Ocean",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "is_stale": 0,
            "etd": "2026-10-01",
            "atd": "2026-10-01",
            "initial_eta": "2026-10-10",
            "eta": "2026-10-10",
            "origin_port": "Shanghai Port",
            "destination_port": "Cat Lai Port",
            "purchase_order": "PO-2026-001",
            "transit_route": [
                {"milestone": "BOOKED", "activity": "Booking confirmed", "date": "2026-09-28"},
                {"milestone": "GATE_IN", "activity": "Gate in Shanghai", "date": "2026-09-29"},
                {"milestone": "LOADED", "activity": "Loaded on vessel", "date": "2026-09-30"},
                {"milestone": "DEPARTED", "activity": "Departed Shanghai", "date": "2026-10-01"},
            ]
        }

        self.db.shipments["SH-TEST-002"] = {
            "name": "SH-TEST-002",
            "tracking_number": "TRK-002",
            "container_id": "CONT-002",
            "carrier": "Vietnam Airlines Cargo",
            "shipping_method": "Air",
            "status": "Delayed",
            "is_delayed": 1,
            "delay_days": 2,
            "is_stale": 0,
            "etd": "2026-10-02",
            "atd": "2026-10-02",
            "initial_eta": "2026-10-05",
            "eta": "2026-10-07",
            "origin_port": "San Francisco Airport",
            "destination_port": "Tan Son Nhat Airport",
            "purchase_order": "PO-2026-002",
            "transit_route": [
                {"milestone": "BOOKED", "activity": "Cargo booked", "date": "2026-10-01"},
                {"milestone": "DEPARTED", "activity": "Flight departed", "date": "2026-10-02"},
            ]
        }

        self.db.shipments["SH-TEST-003"] = {
            "name": "SH-TEST-003",
            "tracking_number": "TRK-003",
            "container_id": "CONT-003",
            "carrier": "ONE Line",
            "shipping_method": "Ocean",
            "status": "In Transit",
            "is_delayed": 0,
            "delay_days": 0,
            "is_stale": 1,
            "etd": "2026-09-20",
            "atd": "2026-09-20",
            "initial_eta": "2026-10-15",
            "eta": "2026-10-15",
            "origin_port": "Los Angeles Port",
            "destination_port": "Hai Phong Port",
            "purchase_order": "PO-2026-003",
            "transit_route": [
                {"milestone": "DEPARTED", "activity": "Departed LA", "date": "2026-09-20"},
            ]
        }

        self.db.shipments["SH-TEST-004"] = {
            "name": "SH-TEST-004",
            "tracking_number": "TRK-004",
            "container_id": "CONT-004",
            "carrier": "DHL Global Forwarding",
            "shipping_method": "Road",
            "status": "Delivered",
            "is_delayed": 0,
            "delay_days": 0,
            "is_stale": 0,
            "etd": "2026-09-10",
            "atd": "2026-09-10",
            "initial_eta": "2026-09-15",
            "eta": "2026-09-15",
            "origin_port": "Huu Nghi Border",
            "destination_port": "Stores - CK",
            "purchase_order": "PO-2026-004",
            "transit_route": [
                {"milestone": "DELIVERED", "activity": "Delivered to warehouse", "date": "2026-09-15"},
            ]
        }

        # Seed Exceptions
        self.db.exceptions["EXC-TEST-001"] = {
            "name": "EXC-TEST-001",
            "shipment_tracking": "SH-TEST-002",
            "purchase_order": "PO-2026-002",
            "exception_type": "ETA Delay",
            "severity": "Warning",
            "status": "Open",
            "old_eta": "2026-10-05",
            "new_eta": "2026-10-07",
            "delay_days": 2,
            "description": "Chuyến bay hoãn do thời tiết tại SFO."
        }

    def test_01_hub_data_structure(self):
        """Verify get_shipment_tracking_hub_data returns full required dictionary schema."""
        res = get_shipment_tracking_hub_data()
        self.assertEqual(res["status"], "success")
        self.assertIn("kpis", res)
        self.assertIn("shipments", res)
        self.assertIn("active_exceptions", res)
        self.assertIn("selected_shipment", res)

    def test_02_kpis_calculation(self):
        """Verify accurate calculation of 4 KPI metrics."""
        res = get_shipment_tracking_hub_data()
        kpis = res["kpis"]
        self.assertEqual(kpis["total_shipments"], 4)
        self.assertEqual(kpis["in_transit"], 2)  # SH-001 and SH-003
        self.assertEqual(kpis["delayed_exceptions"], 1)  # SH-002
        self.assertEqual(kpis["stale_tracking"], 1)  # SH-003

    def test_03_shipment_list_filtering(self):
        """Verify filter_status properly subsets the shipment records."""
        # Filter In Transit
        res_transit = get_shipment_tracking_hub_data(filter_status="In Transit")
        self.assertEqual(len(res_transit["shipments"]), 2)

        # Filter Delayed
        res_delayed = get_shipment_tracking_hub_data(filter_status="Delayed")
        self.assertEqual(len(res_delayed["shipments"]), 1)
        self.assertEqual(res_delayed["shipments"][0]["name"], "SH-TEST-002")

        # Filter Stale
        res_stale = get_shipment_tracking_hub_data(filter_status="Stale")
        self.assertEqual(len(res_stale["shipments"]), 1)
        self.assertEqual(res_stale["shipments"][0]["name"], "SH-TEST-003")

        # Filter Delivered
        res_delivered = get_shipment_tracking_hub_data(filter_status="Delivered")
        self.assertEqual(len(res_delivered["shipments"]), 1)
        self.assertEqual(res_delivered["shipments"][0]["name"], "SH-TEST-004")

    def test_04_search_term_filtering(self):
        """Verify search_term matches across carrier, container, tracking number, PO."""
        res_carrier = get_shipment_tracking_hub_data(search_term="Maersk")
        self.assertEqual(len(res_carrier["shipments"]), 1)
        self.assertEqual(res_carrier["shipments"][0]["name"], "SH-TEST-001")

        res_cont = get_shipment_tracking_hub_data(search_term="CONT-002")
        self.assertEqual(len(res_cont["shipments"]), 1)
        self.assertEqual(res_cont["shipments"][0]["name"], "SH-TEST-002")

        res_po = get_shipment_tracking_hub_data(search_term="PO-2026-003")
        self.assertEqual(len(res_po["shipments"]), 1)
        self.assertEqual(res_po["shipments"][0]["name"], "SH-TEST-003")

    def test_05_selected_shipment_selection(self):
        """Verify selecting a shipment returns enriched details and route."""
        res = get_shipment_tracking_hub_data(shipment="SH-TEST-001")
        sel = res["selected_shipment"]
        self.assertIsNotNone(sel)
        self.assertEqual(sel["name"], "SH-TEST-001")
        self.assertIn("transit_route", sel)
        self.assertEqual(len(sel["transit_route"]), 4)

    def test_06_active_exceptions_content(self):
        """Verify active_exceptions contains open exceptions and excludes resolved."""
        # Add a resolved exception
        self.db.exceptions["EXC-TEST-RESOLVED"] = {
            "name": "EXC-TEST-RESOLVED",
            "shipment_tracking": "SH-TEST-001",
            "status": "Resolved",
            "severity": "Info"
        }

        res = get_shipment_tracking_hub_data()
        exceptions = res["active_exceptions"]
        self.assertEqual(len(exceptions), 1)
        self.assertEqual(exceptions[0]["name"], "EXC-TEST-001")

    def test_07_sync_shipment_now_endpoint(self):
        """Verify sync_shipment_now whitelisted endpoint triggers sync and returns fresh state."""
        res = sync_shipment_now(shipment="SH-TEST-001")
        self.assertTrue(res.get("success", False) or res.get("status") == "success")
        self.assertIn("fresh_hub_data", res)
        self.assertEqual(res["fresh_hub_data"]["status"], "success")


if __name__ == "__main__":
    unittest.main()
