#!/usr/bin/env python3
"""
test_export_workflow.py — Kiểm thử toàn diện Quy trình Xuất khẩu (Export Workflow)
===================================================================================
Kiểm tra chuỗi 7 bước xuất khẩu và khả năng liên kết 2 chiều:
1. Sales Order (EXP-2026-001)
2. Payment Entry (Thu cọc 30% USD)
3. Stock Entry (Chuyển kho ra cảng)
4. Delivery Note (Xuất kho giao hàng)
5. Shipment Tracking (Outbound Cát Lái -> Long Beach)
6. Sales Invoice (Hóa đơn thương mại Commercial Invoice)
7. Payment Entry (Tất toán ngoại tệ 70%)
"""

import os
import sys
import unittest

# Environment & Path setup
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.dirname(TEST_DIR) if os.path.basename(TEST_DIR) == "test" else TEST_DIR
APP_DIR = os.path.join(BENCH_DIR, "apps", "logistics_wizard")

for p in [APP_DIR, BENCH_DIR, TEST_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import frappe
    HAS_FRAPPE = True
except ImportError:
    HAS_FRAPPE = False

from logistics_wizard.workflow import (
    IMPORT_WORKFLOW_STEPS,
    EXPORT_WORKFLOW_STEPS,
    WORKFLOW_STEPS,
    detect_workflow_flow_type,
    get_workflow_chain_status,
    get_import_workflow_chain_status,
    get_export_workflow_chain_status,
)


class TestExportWorkflowDefinitions(unittest.TestCase):
    """Kiểm tra tính toàn vẹn của cấu trúc định nghĩa chuỗi Xuất khẩu"""

    def test_export_workflow_step_count(self):
        """Quy trình xuất khẩu phải có đúng 7 bước chuẩn"""
        self.assertEqual(len(EXPORT_WORKFLOW_STEPS), 7)
        expected_doctypes = [
            "Sales Order",
            "Payment Entry",
            "Stock Entry",
            "Delivery Note",
            "Shipment Tracking",
            "Sales Invoice",
            "Payment Entry",
        ]
        actual_doctypes = [s["doctype"] for s in EXPORT_WORKFLOW_STEPS]
        self.assertEqual(actual_doctypes, expected_doctypes)

    def test_export_workflow_slugs(self):
        """Kiểm tra các slug điều hướng ERPNext của quy trình xuất khẩu"""
        self.assertEqual(EXPORT_WORKFLOW_STEPS[0]["slug"], "sales-order")
        self.assertEqual(EXPORT_WORKFLOW_STEPS[1]["slug"], "payment-entry")
        self.assertEqual(EXPORT_WORKFLOW_STEPS[2]["slug"], "stock-entry")
        self.assertEqual(EXPORT_WORKFLOW_STEPS[3]["slug"], "delivery-note")
        self.assertEqual(EXPORT_WORKFLOW_STEPS[4]["slug"], "shipment-tracking-hub")
        self.assertEqual(EXPORT_WORKFLOW_STEPS[5]["slug"], "sales-invoice")
        self.assertEqual(EXPORT_WORKFLOW_STEPS[6]["slug"], "payment-entry")

    def test_auto_detection_pure_doctypes(self):
        """Kiểm tra tự động phát hiện luồng với các DocType đơn nhất"""
        # Thuần Import
        self.assertEqual(detect_workflow_flow_type("Material Request"), "import")
        self.assertEqual(detect_workflow_flow_type("Purchase Order"), "import")
        self.assertEqual(detect_workflow_flow_type("Purchase Receipt"), "import")
        self.assertEqual(detect_workflow_flow_type("Landed Cost Voucher"), "import")

        # Thuần Export
        self.assertEqual(detect_workflow_flow_type("Sales Order"), "export")
        self.assertEqual(detect_workflow_flow_type("Delivery Note"), "export")
        self.assertEqual(detect_workflow_flow_type("Sales Invoice"), "export")


class TestExportWorkflowIntegration(unittest.TestCase):
    """Kiểm thử tích hợp trên cơ sở dữ liệu Frappe/ERPNext nếu có kết nối"""

    @classmethod
    def setUpClass(cls):
        cls.connected = False
        if HAS_FRAPPE:
            try:
                if not frappe.db:
                    sites_dir = "/home/frappe/frappe-bench/sites"
                    if os.path.exists(sites_dir):
                        os.chdir(sites_dir)
                    elif os.path.exists("sites"):
                        os.chdir("sites")
                    frappe.init(site="logistics.local")
                    frappe.connect()
                cls.connected = True
            except Exception as e:
                print(f"[!] Warning: Cannot connect to frappe database: {e}")
                cls.connected = False

    def test_input_validation(self):
        """Kiểm tra xử lý đầu vào bất thường"""
        res = get_workflow_chain_status(None, None)
        self.assertFalse(res["success"])
        self.assertEqual(len(res["steps"]), 0)

        res2 = get_workflow_chain_status("", "  ")
        self.assertFalse(res2["success"])

    def test_export_chain_status_from_sales_order(self):
        """Kiểm tra duyệt chuỗi xuất khẩu bắt đầu từ Sales Order EXP-2026-001"""
        if not self.connected:
            self.skipTest("Frappe DB not connected")

        so_name = frappe.db.get_value("Shipment Tracking", "ST-EXP-2026-001", "sales_order")
        if not so_name or not frappe.db.exists("Sales Order", so_name):
            self.skipTest("Sales Order for ST-EXP-2026-001 does not exist in DB yet")

        res = get_workflow_chain_status("Sales Order", so_name)
        self.assertTrue(res["success"])
        self.assertEqual(res["flow_type"], "export")
        self.assertEqual(len(res["steps"]), 7)

        # Bước 1 phải là Sales Order hiện tại
        step1 = res["steps"][0]
        self.assertEqual(step1["doctype"], "Sales Order")
        self.assertEqual(step1["docname"], so_name)
        self.assertTrue(step1["is_current"])

        # Bước 2: Payment Entry cọc
        step2 = res["steps"][1]
        self.assertEqual(step2["doctype"], "Payment Entry")
        self.assertIsNotNone(step2["docname"])

        # Bước 3: Stock Entry chuyển cảng
        step3 = res["steps"][2]
        self.assertEqual(step3["doctype"], "Stock Entry")
        self.assertIsNotNone(step3["docname"])

        # Bước 4: Delivery Note
        step4 = res["steps"][3]
        self.assertEqual(step4["doctype"], "Delivery Note")
        self.assertIsNotNone(step4["docname"])

        # Bước 5: Shipment Tracking
        step5 = res["steps"][4]
        self.assertEqual(step5["doctype"], "Shipment Tracking")
        self.assertEqual(step5["docname"], "ST-EXP-2026-001")

        # Bước 6: Sales Invoice
        step6 = res["steps"][5]
        self.assertEqual(step6["doctype"], "Sales Invoice")
        self.assertIsNotNone(step6["docname"])

        # Bước 7: Payment Entry tất toán
        step7 = res["steps"][6]
        self.assertEqual(step7["doctype"], "Payment Entry")
        self.assertIsNotNone(step7["docname"])

    def test_export_chain_traversal_bidirectional(self):
        """Kiểm tra khả năng duyệt ngược từ Shipment Tracking sang Sales Order và các bước khác"""
        if not self.connected:
            self.skipTest("Frappe DB not connected")

        if not frappe.db.exists("Shipment Tracking", "ST-EXP-2026-001"):
            self.skipTest("Shipment Tracking ST-EXP-2026-001 does not exist in DB yet")

        res = get_workflow_chain_status("Shipment Tracking", "ST-EXP-2026-001")
        self.assertTrue(res["success"])
        self.assertEqual(res["flow_type"], "export")

        # Bước 5 phải là is_current
        step5 = res["steps"][4]
        self.assertEqual(step5["docname"], "ST-EXP-2026-001")
        self.assertTrue(step5["is_current"])

        # Bước 1 phải suy luận ra được Sales Order liên kết
        so_name = frappe.db.get_value("Shipment Tracking", "ST-EXP-2026-001", "sales_order")
        step1 = res["steps"][0]
        self.assertEqual(step1["docname"], so_name)

    def test_explicit_flow_type_override(self):
        """Kiểm tra cờ flow_type ghi đè rõ ràng khi được yêu cầu"""
        if not self.connected:
            self.skipTest("Frappe DB not connected")

        so_name = frappe.db.get_value("Shipment Tracking", "ST-EXP-2026-001", "sales_order")
        if so_name and frappe.db.exists("Sales Order", so_name):
            res = get_workflow_chain_status("Sales Order", so_name, flow_type="export")
            self.assertTrue(res["success"])
            self.assertEqual(res["flow_type"], "export")
            self.assertEqual(len(res["steps"]), 7)


if __name__ == "__main__":
    unittest.main()
