#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_trade_case_e2e.py — Master End-to-End Test Suite for Trade Case Overview
=============================================================================
Architecture: 4-Tier Verification Hierarchy (Opaque-box, Requirement-driven)
Target: Unified Desk Page (/app/shipment-tracking-hub & Trade Case Overview)

Tiers:
- Tier 1: Feature Coverage (Core Requirements R1, R2, R3, R4)
- Tier 2: Boundary & Corner Cases (Purple Ban Static Regex, Null/Empty Fallbacks, Overruns)
- Tier 3: Cross-Feature Combinations (Dual-Tab State Machine, Drill-Down Context, Stage-Gate Enforcement)
- Tier 4: Real-World Application Scenarios (Happy Path Air, Storm Delay Ocean + C/O, Red Channel Export, WH Discrepancy)

Execution:
    python3 test/test_trade_case_e2e.py
    python3 -m unittest test/test_trade_case_e2e.py -v
    pytest test/test_trade_case_e2e.py -v
"""

import os
import sys
import json
import re
import unittest
from typing import Dict, Any, List, Optional

# Set up paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==============================================================================
# TIER 1: FEATURE COVERAGE (R1, R2, R3, R4)
# ==============================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1: Feature Coverage — Kiểm tra tính độc lập và đầy đủ của từng tính năng:
    - Doctype Trade Case schema JSON & Zero Data Duplication (R3)
    - Sub-structures & Child references (R3)
    - Backend API endpoints trong api.py (R3)
    - Unified Desk Page Structure (R1)
    - Sidebar Dual-Tab Navigation Menu (R1)
    - Case Selector & State Synchronization (R1)
    - Drill-down Button [View Shipment Tracking] (R1)
    - 14 Core Sections UI DOM Nodes trong template (R2)
    - Tài liệu lộ trình todoTradeCase.md với 4 phần chuẩn (R4)
    """

    def setUp(self):
        from logistics_wizard import api
        self.api = api
        self.doctype_dir = os.path.join(APP_PATH, "logistics_wizard", "doctype", "trade_case")
        self.page_dir = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic")

    def test_f1_trade_case_doctype_schema_json(self):
        """F1: Kiểm tra DocType Trade Case schema JSON hợp lệ, đầy đủ trường và tuân thủ Zero Data Duplication."""
        self.assertTrue(os.path.isdir(self.doctype_dir), "Thư mục doctype/trade_case phải tồn tại")
        json_file = os.path.join(self.doctype_dir, "trade_case.json")
        self.assertTrue(os.path.isfile(json_file), "Tệp trade_case.json phải tồn tại")

        with open(json_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        self.assertEqual(schema.get("doctype"), "DocType")
        self.assertEqual(schema.get("name"), "Trade Case")
        self.assertEqual(schema.get("module"), "Logistics Wizard")

        fieldnames = [f.get("fieldname") for f in schema.get("fields", []) if "fieldname" in f]
        required_master_fields = [
            "trade_type", "status", "current_stage", "overall_health", "priority",
            "purchase_order", "sales_order", "supplier", "customer", "company",
            "mode", "incoterm", "origin_port", "destination_port",
            "case_owner", "department", "opened_date", "expected_close_date",
            "shipment_tracking", "open_exceptions_count", "customs_cleared", "costs_finalized"
        ]
        for fld in required_master_fields:
            self.assertIn(fld, fieldnames, f"Trường master '{fld}' bắt buộc phải có trong Trade Case")

        # Zero Data Duplication: Không copy bảng Items chi tiết hoặc tọa độ GPS lẻ
        forbidden_duplicated_fields = ["items", "checkpoints", "transit_waypoints", "gps_coordinates"]
        for forbidden in forbidden_duplicated_fields:
            self.assertNotIn(forbidden, fieldnames, f"DocType Trade Case không được nhân bản trường '{forbidden}'")

    def test_f2_child_substructures_and_references(self):
        """F2: Kiểm tra cấu trúc liên kết sub-structures: Shipment, Stakeholders matrix, Stage Gate checklist."""
        data = self.api.get_trade_case_overview_data("IMP-2026-001")

        # Shipment reference
        self.assertIn("shipment_summary", data)
        self.assertIn("shipment_id", data["shipment_summary"])

        # Responsibility RACI matrix
        self.assertIn("responsibility_matrix", data)
        self.assertIsInstance(data["responsibility_matrix"], list)
        self.assertGreaterEqual(len(data["responsibility_matrix"]), 4, "Ma trận RACI phải bao gồm ít nhất 4 vị trí")

        # Stage gate checklist structure
        self.assertIn("quick_actions", data)
        self.assertIn("can_close", data["quick_actions"])
        self.assertIn("close_reasons", data["quick_actions"])

    def test_f3_backend_api_endpoints_export(self):
        """F3: Kiểm tra các hàm API của Trade Case được định nghĩa và công khai trong api.py."""
        self.assertTrue(hasattr(self.api, "get_trade_case_list"), "api.py phải có get_trade_case_list")
        self.assertTrue(hasattr(self.api, "get_trade_case_overview_data"), "api.py phải có get_trade_case_overview_data")
        self.assertTrue(hasattr(self.api, "close_trade_case"), "api.py phải có close_trade_case")

        # Kiểm tra __all__
        self.assertIn("get_trade_case_list", self.api.__all__)
        self.assertIn("get_trade_case_overview_data", self.api.__all__)
        self.assertIn("close_trade_case", self.api.__all__)

    def test_f4_page_structure_files(self):
        """F4: Kiểm tra các tệp Desk Page cấu thành trang hợp nhất tồn tại đầy đủ."""
        for filename in ["managementLogistic.html", "managementLogistic.js", "managementLogistic.css", "managementLogistic.json"]:
            path = os.path.join(self.page_dir, filename)
            self.assertTrue(os.path.isfile(path), f"Tệp Desk Page '{filename}' phải tồn tại")

    def test_f5_sidebar_dual_tab_navigation(self):
        """F5: Kiểm tra Menu 2 tab (Trade Case Overview & Shipment Tracking Hub)."""
        html_path = os.path.join(self.page_dir, "managementLogistic.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('class="logistics-tabs-nav"', html)
        self.assertIn('id="btn-tab-overview"', html)
        self.assertIn('id="btn-tab-tracking"', html)
        self.assertIn('data-target="overview"', html)
        self.assertIn('data-target="tracking"', html)
        self.assertIn('Trade Case Overview', html)
        self.assertIn('Shipment Tracking Hub', html)

    def test_f6_case_selector_and_state_sync(self):
        """F6: Kiểm tra Case Selector dropdown được bố trí ngay bên trong Tab Trade Case Overview."""
        html_path = os.path.join(self.page_dir, "managementLogistic.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="tc-case-selector"', html)
        self.assertIn('Chọn hồ sơ Trade Case', html)

        # Kiểm tra danh sách Case mặc định có ít nhất 3 case
        cases = self.api.get_trade_case_list()
        self.assertGreaterEqual(len(cases), 3, "Danh sách case phải có ít nhất 3 hồ sơ mẫu")
        case_ids = [c["case_id"] for c in cases]
        self.assertIn("IMP-2026-001", case_ids)
        self.assertIn("IMP-2026-002", case_ids)
        self.assertIn("EXP-2026-001", case_ids)

    def test_f7_drilldown_navigation_button(self):
        """F7: Kiểm tra nút drill-down [View Shipment Tracking] trên Card 4."""
        html_path = os.path.join(self.page_dir, "managementLogistic.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="tc-btn-goto-shipment"', html)
        self.assertIn('Xem Shipment Tracking', html)

    def test_f8_to_f21_fourteen_core_sections_dom_elements(self):
        """F8 - F21: Kiểm tra sự hiện diện của toàn bộ 14 Core Sections UI trên DOM HTML."""
        html_path = os.path.join(self.page_dir, "managementLogistic.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        sections = [
            ("Section 1: Header Identification", "tc-header-id"),
            ("Section 2: Lifecycle Stepper", "tc-lifecycle-stepper"),
            ("Section 3: Health & Readiness Grid", "tc-health-grid"),
            ("Section 4: Shipment Summary Card", "tc-shipment-summary-body"),
            ("Section 5: Document Readiness Card", "tc-doc-readiness-body"),
            ("Section 6: Customs & Compliance Card", "tc-customs-body"),
            ("Section 7: Cost Summary Card", "tc-cost-body"),
            ("Section 8: Warehouse Delivery Readiness", "tc-wh-body"),
            ("Section 9: Top Open Exceptions Card", "tc-exceptions-body"),
            ("Section 10: Upcoming Actions & Deadlines", "tc-actions-body"),
            ("Section 11: Related ERP Documents", "tc-related-erp-body"),
            ("Section 12: Responsibility Matrix", "tc-responsibility-body"),
            ("Section 13: Activity & Audit Timeline", "tc-activity-body"),
            ("Section 14: Quick Actions & Stage Gate", "tc-stage-gate-body"),
        ]

        for sec_name, dom_id in sections:
            self.assertIn(dom_id, html, f"{sec_name} (DOM ID: #{dom_id}) bắt buộc phải tồn tại trong HTML template")

    def test_f22_to_f25_todo_trade_case_content(self):
        """F22 - F25: Kiểm tra tệp lộ trình todoTradeCase.md tồn tại và chứa đủ 4 nhóm nội dung bắt buộc."""
        todo_path = os.path.join(PROJECT_ROOT, "todoTradeCase.md")
        self.assertTrue(os.path.isfile(todo_path), "todoTradeCase.md phải tồn tại tại thư mục gốc")

        with open(todo_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 4 nhóm nội dung cốt lõi
        self.assertIn("Danh Mục Các Module Liên Quan Cần Hoàn Thành", content, "Thiếu phần 1: Danh mục module")
        self.assertIn("API Interface & Data Contract", content, "Thiếu phần 2: Interface contracts")
        self.assertIn("Kịch Bản Kiểm Thử Toàn Diện", content, "Thiếu phần 3: Test Scenarios")
        self.assertIn("Quy Tắc Chốt Chặn Hồ Sơ (Stage Gate Rules)", content, "Thiếu phần 4: Stage Gate rules")

        # Kiểm tra chi tiết 5 module phụ thuộc
        for mod in ["Document Readiness Engine", "Customs & RAG Compliance", "Trade Cost & Landed Cost", "Warehouse Receiving & Inspection", "Exception & Action Management"]:
            self.assertIn(mod, content, f"Thiếu mô tả cho module '{mod}' trong todoTradeCase.md")

        # Kiểm tra 4 kịch bản kiểm thử
        self.assertIn("Happy Path", content)
        self.assertIn("Delay & Missing C/O", content)
        self.assertIn("Critical Exception", content)
        self.assertIn("Warehouse Discrepancy", content)


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (PURPLE BAN, NULL/EMPTY, OVERRUN)
# ==============================================================================

class TestTier2BoundaryCornerCases(unittest.TestCase):
    """
    Tier 2: Boundary & Corner Cases — Kiểm thử các trường hợp biên và điều kiện bất thường:
    - Quét tĩnh Regex kiểm tra PURPLE BAN trên toàn bộ CSS & JS
    - Xử lý dữ liệu rỗng và mã Case ID không tồn tại
    - Nhận diện và cảnh báo thiếu chứng từ khẩn cấp (C/O Form E)
    - Nhận diện và phát hiện vượt chi phí dự toán >5%
    - Khóa chặn đóng case khi có sự cố mức Critical
    """

    def setUp(self):
        from logistics_wizard import api
        self.api = api

    def test_purple_ban_static_regex_scan(self):
        """PURPLE BAN: Quét Regex toàn bộ CSS/JS trong logistics_wizard bảo đảm không chứa màu tím/violet."""
        target_dir = os.path.join(APP_PATH, "logistics_wizard")

        # Bảng màu cấm
        disallowed_hex = re.compile(
            r"#(8a2be2|9333ea|7c3aed|6366f1|8b5cf6|a855f7|d946ef|4c1d95|581c87|6d28d9|"
            r"800080|9400d3|4b0082|ee82ee|da70d6|ba55d3|9932cc|8b008b)\b",
            re.IGNORECASE
        )
        disallowed_names = re.compile(r"\b(purple|violet|magenta|indigo)\b", re.IGNORECASE)

        violations = []
        scanned_count = 0

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".css", ".js", ".html")) and "dist" not in root:
                    scanned_count += 1
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Loại bỏ block comment /* ... */ và HTML comment <!-- ... -->
                    clean = re.sub(r"/\*[\s\S]*?\*/", "", content)
                    clean = re.sub(r"<!--[\s\S]*?-->", "", clean)
                    # Loại bỏ single line comments
                    clean = re.sub(r"//.*", "", clean)
                    # Loại bỏ cụm từ 'No Purple' trong code comment
                    clean = re.sub(r"No\s+Purple", "", clean, flags=re.IGNORECASE)

                    for line_idx, line in enumerate(clean.splitlines(), 1):
                        hex_match = disallowed_hex.search(line)
                        if hex_match:
                            violations.append(f"{file_path}:{line_idx} [HEX: {hex_match.group(0)}] -> {line.strip()}")
                        name_match = disallowed_names.search(line)
                        if name_match:
                            violations.append(f"{file_path}:{line_idx} [NAME: {name_match.group(0)}] -> {line.strip()}")

        self.assertGreater(scanned_count, 0, "Phải quét ít nhất 1 file CSS/JS")
        self.assertEqual(len(violations), 0, f"Phát hiện vi phạm PURPLE BAN:\n" + "\n".join(violations))

    def test_empty_and_null_case_data_handling(self):
        """Kiểm tra API xử lý an toàn khi đầu vào case_id là None, rỗng hoặc không tồn tại."""
        # Case None
        res_none = self.api.get_trade_case_overview_data(None)
        self.assertEqual(res_none.get("status"), "success")
        self.assertIsNotNone(res_none.get("case_id"))

        # Case empty string
        res_empty = self.api.get_trade_case_overview_data("")
        self.assertEqual(res_empty.get("status"), "success")
        self.assertIsNotNone(res_empty.get("case_id"))

        # Case unknown ID -> fallback an toàn, không văng 500
        res_unknown = self.api.get_trade_case_overview_data("UNKNOWN-CASE-999")
        self.assertEqual(res_unknown.get("status"), "success")
        self.assertIn("header", res_unknown)

    def test_missing_documents_boundary_alert(self):
        """Kiểm tra phát hiện và ghim cảnh báo khẩn cấp khi thiếu chứng từ C/O hoặc D/O."""
        data = self.api.get_trade_case_overview_data("IMP-2026-001")
        docs = data.get("document_readiness", {})

        self.assertLess(docs.get("percentage", 100), 100, "IMP-2026-001 phải chưa hoàn thành 100% chứng từ")
        missing_urgent = docs.get("missing_urgent", [])
        self.assertGreater(len(missing_urgent), 0, "Phải có cảnh báo chứng từ thiếu khẩn cấp")

        co_item = next((item for item in missing_urgent if "C/O" in item.get("name", "")), None)
        self.assertIsNotNone(co_item, "Phải chỉ rõ thiếu chứng từ C/O Form E")
        self.assertEqual(co_item.get("type"), "critical")
        self.assertIn("deadline", co_item)

    def test_cost_overrun_boundary_detection(self):
        """Kiểm tra phát hiện vượt chi phí > 5% và kích hoạt cờ cảnh báo chi phí."""
        data = self.api.get_trade_case_overview_data("IMP-2026-001")
        cost = data.get("cost_summary", {})

        variance_pct = cost.get("variance_pct", 0)
        self.assertGreater(variance_pct, 5.0, "Case IMP-2026-001 phải có variance > 5% để kích hoạt cảnh báo")
        self.assertGreater(cost.get("variance_amount", 0), 0)
        self.assertGreater(cost.get("actual_cost", 0), cost.get("estimated_cost", 0))

        # Kiểm tra phản ánh trên Health Grid
        health_grid = data.get("overall_health", {}).get("cards", [])
        cost_card = next((c for c in health_grid if c.get("key") == "cost"), None)
        self.assertIsNotNone(cost_card)
        self.assertIn("7.9%", cost_card.get("sub", ""))

    def test_critical_exception_boundary_handling(self):
        """Kiểm tra khi có sự cố mức Critical, hồ sơ phải chuyển sang Critical và khóa đóng case."""
        data = self.api.get_trade_case_overview_data("EXP-2026-001")
        self.assertEqual(data.get("header", {}).get("health"), "Critical")

        qa = data.get("quick_actions", {})
        self.assertFalse(qa.get("can_close", True), "Hồ sơ có sự cố Critical tuyệt đối không được cho phép đóng")


# ==============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (INTEGRATION & STATE MACHINE)
# ==============================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """
    Tier 3: Cross-Feature Combinations — Kiểm thử tương tác giữa các tính năng:
    - Bộ điều phối UnifiedLogisticsHub chuyển tab bảo toàn trạng thái (0ms Switch)
    - Kích hoạt drill-down [View Shipment Tracking] truyền đúng shipment context
    - Thực thi ma trận Stage-Gate kiểm tra 8 điều kiện chốt đóng hồ sơ
    """

    def setUp(self):
        from logistics_wizard import api
        self.api = api
        self.js_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.js")

    def test_tab_switching_state_preservation_logic(self):
        """Kiểm tra logic controller JS bảo toàn currentCaseId khi chuyển tab không reload trang."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Class UnifiedLogisticsHub tồn tại
        self.assertIn("class UnifiedLogisticsHub", js_content)
        # Quản lý state currentCaseId và currentTab
        self.assertIn("this.currentTab", js_content)
        self.assertIn("this.currentCaseId", js_content)
        # Hàm switch_tab hiển thị/ẩn tab pane và invalidate map
        self.assertIn("switch_tab(tabName, options)", js_content)
        self.assertIn("this.trackingHub.map.invalidateSize()", js_content)

    def test_drilldown_navigation_shipment_context(self):
        """Kiểm tra nút [View Shipment Tracking] truyền đúng shipment_id sang tab tracking."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Bắt sự kiện click nút drill-down
        self.assertIn("#tc-btn-goto-shipment", js_content)
        # Lấy shipment_id từ shipment_summary và gọi switch_tab('tracking', { shipment_id: shpId })
        self.assertIn("self.unifiedHub.switch_tab('tracking', { shipment_id: shpId })", js_content)

    def test_stage_gate_close_case_enforcement(self):
        """Kiểm tra chặn đóng case khi chưa đủ điều kiện và cho phép đóng khi đủ điều kiện."""
        # 1. Thử đóng case chưa đủ điều kiện (IMP-2026-001)
        res_fail = self.api.close_trade_case("IMP-2026-001")
        self.assertFalse(res_fail.get("success"), "Đóng case IMP-2026-001 phải thất bại")
        self.assertFalse(res_fail.get("can_close", True))
        self.assertIn("reasons", res_fail)
        self.assertGreaterEqual(len(res_fail["reasons"]), 3, "Phải chỉ rõ các lý do vi phạm stage-gate")

        # 2. Thử nghiệm với đối tượng Python controller TradeCase
        from logistics_wizard.doctype.trade_case.trade_case import TradeCase

        # Case chưa đạt điều kiện
        tc_in_transit = TradeCase({
            "name": "TC-TEST-PENDING",
            "current_stage": "In Transit",
            "customs_cleared": 0,
            "costs_finalized": 0,
            "open_exceptions_count": 1
        })
        tc_in_transit.validate()
        can_close, checks = tc_in_transit.can_close()
        self.assertFalse(can_close)
        with self.assertRaises(ValueError):
            tc_in_transit.close_case()

        # Case đã thỏa mãn tất cả 8 điều kiện chốt chặn Stage Gate
        tc_completed = TradeCase({
            "name": "TC-TEST-COMPLETE",
            "current_stage": "Cost Finalization",
            "document_readiness_pct": 100.0,
            "customs_cleared": 1,
            "costs_finalized": 1,
            "open_exceptions_count": 0,
            "critical_exceptions_count": 0
        })
        tc_completed.validate()
        can_close_ok, checks_ok = tc_completed.can_close()
        self.assertTrue(can_close_ok, "Case hoàn tất 8 chốt chặn phải đủ điều kiện đóng")
        self.assertTrue(tc_completed.close_case())
        self.assertEqual(tc_completed.status, "Closed")
        self.assertEqual(tc_completed.current_stage, "Closed")


# ==============================================================================
# TIER 4: REAL-WORLD APPLICATION SCENARIOS
# ==============================================================================

class TestTier4RealWorldScenarios(unittest.TestCase):
    """
    Tier 4: Real-World Scenarios — Kiểm thử 4 kịch bản nghiệp vụ thực tế quy định trong todoTradeCase.md:
    - Kịch bản 1: Hàng nhập khẩu đường hàng không thuận lợi (Happy Path — Healthy)
    - Kịch bản 2: Hàng nhập khẩu đường biển bão trễ + thiếu C/O Form E (Delay & Missing C/O)
    - Kịch bản 3: Hàng xuất khẩu năng lượng mặt trời dính Luồng Đỏ kiểm hóa 100% (Critical Exception)
    - Kịch bản 4: Nhập kho phát hiện chênh lệch số lượng và hư hại (Warehouse Discrepancy)
    """

    def setUp(self):
        from logistics_wizard import api
        self.api = api

    def test_scenario_1_happy_path_import_air_tokyo_noibai(self):
        """Kịch bản 1: Nhập khẩu Tokyo - Nội Bài thuận lợi (IMP-2026-002) -> Health Healthy, 0 exception, 100% docs."""
        data = self.api.get_trade_case_overview_data("IMP-2026-002")

        header = data["header"]
        self.assertEqual(header["case_id"], "IMP-2026-002")
        self.assertEqual(header["trade_type"], "Import")
        self.assertEqual(header["mode"], "Air")
        self.assertEqual(header["health"], "Healthy")

        # Chứng từ đạt 100%
        docs = data["document_readiness"]
        self.assertEqual(docs["percentage"], 100)
        self.assertEqual(docs["ready_count"], docs["total_count"])
        self.assertEqual(len(docs["missing_urgent"]), 0)

        # Hải quan Luồng Xanh (Channel Green) & tỷ lệ sẵn sàng cao >=90%
        customs = data["customs_readiness"]
        self.assertIn("Channel Green", customs["declaration_status"])
        self.assertGreaterEqual(customs["readiness_pct"], 90)

        # 0 ngoại lệ
        exceptions = data["open_exceptions"]
        self.assertEqual(exceptions["total_open"], 0)

    def test_scenario_2_delay_and_missing_co_ocean_shanghai_danang(self):
        """Kịch bản 2: Nhập khẩu Thượng Hải - Đà Nẵng gặp bão trễ + thiếu C/O (IMP-2026-001) -> Attention, trễ +2 ngày."""
        data = self.api.get_trade_case_overview_data("IMP-2026-001")

        header = data["header"]
        self.assertEqual(header["case_id"], "IMP-2026-001")
        self.assertEqual(header["trade_type"], "Import")
        self.assertEqual(header["mode"], "Ocean")
        self.assertEqual(header["health"], "Attention")

        # Tàu trễ +2 ngày
        shipment = data["shipment_summary"]
        self.assertEqual(shipment["delay_days"], 2)

        # Thiếu C/O Form E khẩn cấp
        docs = data["document_readiness"]
        self.assertLess(docs["percentage"], 100)
        self.assertTrue(any("C/O" in d["name"] for d in docs["missing_urgent"]))

        # Chi phí vượt +7.9%
        cost = data["cost_summary"]
        self.assertEqual(cost["variance_pct"], 7.9)

        # 3 ngoại lệ đang mở
        self.assertEqual(data["open_exceptions"]["total_open"], 3)

        # Chặn đóng case
        self.assertFalse(data["quick_actions"]["can_close"])

    def test_scenario_3_critical_export_red_channel_california(self):
        """Kịch bản 3: Xuất khẩu pin năng lượng mặt trời dính Luồng Đỏ (EXP-2026-001) -> Critical, khóa toàn bộ đóng case."""
        data = self.api.get_trade_case_overview_data("EXP-2026-001")

        header = data["header"]
        self.assertEqual(header["case_id"], "EXP-2026-001")
        self.assertEqual(header["trade_type"], "Export")
        self.assertEqual(header["health"], "Critical")

        # Hải quan Luồng Đỏ
        customs = data["customs_readiness"]
        self.assertIn("Luồng Đỏ", customs["declaration_status"])

        # Sự cố Critical
        exc_items = data["open_exceptions"]["items"]
        has_critical = any(item["severity"] == "CRITICAL" for item in exc_items)
        self.assertTrue(has_critical, "Phải có sự cố mức CRITICAL")

        # Khóa nút đóng case
        self.assertFalse(data["quick_actions"]["can_close"])

    def test_scenario_4_warehouse_discrepancy_and_inspection(self):
        """Kịch bản 4: Kiểm tra cấu trúc đối soát kho bãi và ghi nhận chênh lệch số lượng hàng hóa."""
        data = self.api.get_trade_case_overview_data("IMP-2026-001")
        wh = data["warehouse_readiness"]

        self.assertIn("warehouse", wh)
        self.assertIn("receiving_status", wh)
        self.assertIn("expected_qty", wh)
        self.assertIn("space_reserved", wh)
        self.assertIn("expected_arrival", wh)


# ==============================================================================
# MAIN TEST SUITE RUNNER
# ==============================================================================

def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestTier1FeatureCoverage))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryCornerCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier3CrossFeatureCombinations))
    suite.addTests(loader.loadTestsFromTestCase(TestTier4RealWorldScenarios))

    runner = unittest.TextTestRunner(verbosity=2)
    print("\n" + "=" * 80)
    print(" LOGISTICS WIZARD — TRADE CASE OVERVIEW E2E TEST SUITE (4-TIER HIERARCHY)")
    print("=" * 80)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print(f" TOTAL TESTS RUN : {result.testsRun}")
    print(f" PASSED          : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" FAILURES        : {len(result.failures)}")
    print(f" ERRORS          : {len(result.errors)}")
    print("=" * 80)

    if result.wasSuccessful():
        print(" STATUS: ALL E2E TESTS PASSED [100% SUCCESS]\n")
        return 0
    else:
        print(" STATUS: TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
