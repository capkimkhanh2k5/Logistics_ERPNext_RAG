#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite: Trade Case Overview & Unified Desk Page Architecture
================================================================
Verifies:
1. Trade Case DocType schema integrity (Zero Data Duplication).
2. TradeCase Python Controller validations and Stage-Gate enforcement.
3. Central Dossier API (get_trade_case_overview_data) payload completeness for all 14 core sections.
4. Multiple scenarios (Warning/Attention, Healthy, Critical Export).
5. Stage Gate close_trade_case validation logic.
6. Strict Purple Ban compliance in CSS stylesheet.
7. HTML & JS Dual-Tab structure and syntax integrity.
8. Completeness of todoTradeCase.md roadmap specification.
"""

import os
import sys
import json
import re
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)


class TestTradeCaseOverview(unittest.TestCase):

    def setUp(self):
        from logistics_wizard import api
        self.api = api

    # --------------------------------------------------------------------------
    # 1. DocType Schema & Data Model Integrity (R3)
    # --------------------------------------------------------------------------
    def test_trade_case_doctype_files_exist(self):
        doctype_dir = os.path.join(APP_PATH, "logistics_wizard", "doctype", "trade_case")
        self.assertTrue(os.path.isdir(doctype_dir), "DocType trade_case directory must exist")
        self.assertTrue(os.path.isfile(os.path.join(doctype_dir, "__init__.py")))
        self.assertTrue(os.path.isfile(os.path.join(doctype_dir, "trade_case.py")))
        self.assertTrue(os.path.isfile(os.path.join(doctype_dir, "trade_case.json")))

    def test_trade_case_schema_zero_data_duplication(self):
        json_path = os.path.join(APP_PATH, "logistics_wizard", "doctype", "trade_case", "trade_case.json")
        with open(json_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        self.assertEqual(schema.get("doctype"), "DocType")
        self.assertEqual(schema.get("name"), "Trade Case")
        self.assertEqual(schema.get("module"), "Logistics Wizard")

        fieldnames = [f.get("fieldname") for f in schema.get("fields", []) if "fieldname" in f]
        # Must contain master fields
        required_master_fields = [
            "trade_type", "status", "current_stage", "overall_health", "priority",
            "purchase_order", "supplier", "mode", "incoterm", "origin_port",
            "destination_port", "case_owner", "opened_date", "expected_close_date"
        ]
        for field in required_master_fields:
            self.assertIn(field, fieldnames, f"Master field '{field}' must exist in Trade Case schema")

        # Zero Data Duplication check: Trade Case should NOT duplicate item tables or GPS checkpoints
        forbidden_duplicated_fields = ["items", "checkpoints", "transit_waypoints", "gps_coordinates"]
        for field in forbidden_duplicated_fields:
            self.assertNotIn(field, fieldnames, f"Trade Case must NOT duplicate '{field}' from child modules")

    # --------------------------------------------------------------------------
    # 2. Python Controller & Stage Gate Logic (R2 & R3)
    # --------------------------------------------------------------------------
    def test_trade_case_controller_stage_gates(self):
        from logistics_wizard.doctype.trade_case.trade_case import TradeCase

        tc = TradeCase({
            "name": "TC-TEST-001",
            "trade_type": "Import",
            "status": "Active",
            "current_stage": "In Transit",
            "customs_cleared": 0,
            "costs_finalized": 0,
            "open_exceptions_count": 2
        })
        tc.validate()

        can_close, checks = tc.can_close()
        self.assertFalse(can_close, "Trade Case in transit with open exceptions cannot be closed")

        passed_keys = [c["key"] for c in checks if c["passed"]]
        failed_keys = [c["key"] for c in checks if not c["passed"]]

        self.assertIn("shipment_delivered", failed_keys)
        self.assertIn("customs_cleared", failed_keys)
        self.assertIn("costs_finalized", failed_keys)
        self.assertIn("zero_open_exceptions", failed_keys)

        # Attempting close_case must throw error
        with self.assertRaises(ValueError):
            tc.close_case()

        # Satisfy all criteria
        tc.current_stage = "Cost Finalization"
        tc.document_readiness_pct = 100.0
        tc.customs_cleared = 1
        tc.costs_finalized = 1
        tc.open_exceptions_count = 0
        tc.critical_exceptions_count = 0

        can_close_ok, checks_ok = tc.can_close()
        self.assertTrue(can_close_ok, "Trade Case should be eligible to close when all 8 stage gates pass")
        self.assertTrue(tc.close_case())
        self.assertEqual(tc.status, "Closed")

    # --------------------------------------------------------------------------
    # 3. Central Dossier API Completeness - 14 Core Sections (R2)
    # --------------------------------------------------------------------------
    def test_get_trade_case_overview_data_14_sections(self):
        data = self.api.get_trade_case_overview_data("IMP-2026-001")
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("case_id"), "IMP-2026-001")

        # 1. Header Identification
        header = data.get("header")
        self.assertIsNotNone(header)
        for key in ["case_id", "trade_type", "status", "health", "supplier", "purchase_order", "mode", "incoterm", "origin", "destination", "owner"]:
            self.assertIn(key, header, f"Header missing key '{key}'")

        # 2. Lifecycle Stepper
        lifecycle = data.get("lifecycle")
        self.assertIsNotNone(lifecycle)
        self.assertEqual(len(lifecycle.get("stages", [])), 9, "Lifecycle must include exactly 9 milestones")
        self.assertIn("previous_milestone", lifecycle)
        self.assertIn("next_milestone", lifecycle)

        # 3. Overall Health / Readiness Grid
        health = data.get("overall_health")
        self.assertIsNotNone(health)
        self.assertEqual(len(health.get("cards", [])), 6, "Health grid must contain 6 readiness cards")
        card_keys = [c["key"] for c in health["cards"]]
        expected_cards = ["shipment", "documents", "customs", "warehouse", "cost", "exceptions"]
        self.assertEqual(sorted(card_keys), sorted(expected_cards))

        # 4. Shipment Summary
        shipment = data.get("shipment_summary")
        self.assertIsNotNone(shipment)
        for key in ["shipment_id", "carrier", "vessel", "container_count", "pol", "pod", "atd", "current_eta", "delay_days"]:
            self.assertIn(key, shipment)

        # 5. Document Readiness
        docs = data.get("document_readiness")
        self.assertIsNotNone(docs)
        self.assertIn("ready_count", docs)
        self.assertIn("total_count", docs)
        self.assertIn("percentage", docs)
        self.assertIn("missing_urgent", docs)
        self.assertEqual(len(docs.get("categories", [])), 4)

        # 6. Customs & Compliance Summary
        customs = data.get("customs_readiness")
        self.assertIsNotNone(customs)
        for key in ["status", "readiness_pct", "hs_classification", "hs_approval_status", "declaration_status", "clearance_status"]:
            self.assertIn(key, customs)

        # 7. Cost Summary
        cost = data.get("cost_summary")
        self.assertIsNotNone(cost)
        for key in ["purchase_value", "estimated_cost", "actual_cost", "variance_amount", "variance_pct", "actual_landed_cost", "breakdown"]:
            self.assertIn(key, cost)

        # 8. Warehouse Readiness
        wh = data.get("warehouse_readiness")
        self.assertIsNotNone(wh)
        for key in ["expected_arrival", "warehouse", "receiving_status", "expected_qty", "space_reserved"]:
            self.assertIn(key, wh)

        # 9. Top Open Exceptions
        exc = data.get("open_exceptions")
        self.assertIsNotNone(exc)
        self.assertIn("total_open", exc)
        self.assertIn("items", exc)
        for item in exc.get("items", []):
            for key in ["severity", "title", "owner", "due_date", "status"]:
                self.assertIn(key, item)

        # 10. Upcoming Actions & Deadlines
        actions = data.get("upcoming_actions")
        self.assertIsNotNone(actions)
        self.assertGreater(len(actions), 0)
        for a in actions:
            self.assertIn("date", a)
            self.assertIn("action", a)
            self.assertIn("department", a)
            self.assertIn("owner", a)

        # 11. Related ERP Documents
        erp_docs = data.get("related_erp_documents")
        self.assertIsNotNone(erp_docs)
        doc_types = [d["doctype"] for d in erp_docs]
        self.assertIn("Purchase Order", doc_types)

        # 12. Responsibility Matrix
        resp = data.get("responsibility_matrix")
        self.assertIsNotNone(resp)
        roles = [r["role"] for r in resp]
        self.assertIn("Case Owner", roles)
        self.assertIn("Customs Specialist", roles)

        # 13. Activity Timeline
        timeline = data.get("activity_timeline")
        self.assertIsNotNone(timeline)
        self.assertGreater(len(timeline), 0)

        # 14. Quick Actions & Stage Gate
        qa = data.get("quick_actions")
        self.assertIsNotNone(qa)
        self.assertIn("can_close", qa)
        self.assertIn("close_reasons", qa)
        self.assertIn("allowed_actions", qa)

    def test_multi_scenario_cases(self):
        # Case 2: Air freight Healthy case
        data_air = self.api.get_trade_case_overview_data("IMP-2026-002")
        self.assertEqual(data_air["header"]["health"], "Healthy")
        self.assertEqual(data_air["document_readiness"]["percentage"], 100)
        self.assertEqual(data_air["open_exceptions"]["total_open"], 0)

        # Case 3: Ocean export Critical case
        data_exp = self.api.get_trade_case_overview_data("EXP-2026-001")
        self.assertEqual(data_exp["header"]["trade_type"], "Export")
        self.assertEqual(data_exp["header"]["health"], "Critical")
        self.assertEqual(data_exp["customs_readiness"]["declaration_status"], "Luồng Đỏ - Kiểm hóa 100%")

    def test_close_trade_case_api(self):
        res = self.api.close_trade_case("IMP-2026-001")
        self.assertFalse(res.get("success"), "IMP-2026-001 must not be allowed to close due to stage gate rules")
        self.assertIn("reasons", res)
        self.assertGreater(len(res["reasons"]), 0)

    # --------------------------------------------------------------------------
    # 4. Strict PURPLE BAN Compliance in CSS (Tier 2 Design Rule)
    # --------------------------------------------------------------------------
    def test_purple_ban_compliance(self):
        css_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # Loại bỏ tất cả comment /* ... */
        clean_css = re.sub(r"/\*[\s\S]*?\*/", "", css_content)

        purple_pattern = re.compile(r"#(8a2be2|9333ea|7c3aed|6366f1|8b5cf6|a855f7|d946ef|4c1d95|581c87|6d28d9)\b", re.IGNORECASE)
        purple_words = re.compile(r"\b(purple|violet|magenta|indigo)\b", re.IGNORECASE)

        match_hex = purple_pattern.search(clean_css)
        self.assertIsNone(match_hex, "Purple Ban violation: found disallowed hex code in CSS rules")

        match_word = purple_words.search(clean_css)
        self.assertIsNone(match_word, "Purple Ban violation: found disallowed color name in CSS rules")

    # --------------------------------------------------------------------------
    # 5. Dual-Tab HTML Shell Structure (R1)
    # --------------------------------------------------------------------------
    def test_unified_html_shell_structure(self):
        html_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Top Tab Bar and In-tab Case Selector checks
        self.assertIn("logistics-tabs-nav", html)
        self.assertIn("tc-case-selector", html)
        self.assertIn("btn-tab-overview", html)
        self.assertIn("btn-tab-tracking", html)

        # Tab pane checks
        self.assertIn("tab-pane-trade-case", html)
        self.assertIn("tab-pane-shipment-tracking", html)

        # Overview 14 block anchors
        self.assertIn("tc-header-id", html)
        self.assertIn("tc-lifecycle-stepper", html)
        self.assertIn("tc-health-grid", html)
        self.assertIn("tc-btn-goto-shipment", html)
        self.assertIn("tc-doc-readiness-body", html)
        self.assertIn("tc-customs-body", html)
        self.assertIn("tc-cost-body", html)
        self.assertIn("tc-wh-body", html)
        self.assertIn("tc-exceptions-body", html)
        self.assertIn("tc-actions-body", html)
        self.assertIn("tc-related-erp-body", html)
        self.assertIn("tc-responsibility-body", html)
        self.assertIn("tc-activity-body", html)
        self.assertIn("tc-stage-gate-body", html)

        # Tracking Hub preservation
        self.assertIn("shipment-tracking-hub-container", html)
        self.assertIn("lw-hub-map", html)
        self.assertIn("hub-shipments-table", html)

    # --------------------------------------------------------------------------
    # 6. Roadmap todoTradeCase.md Completeness (R4)
    # --------------------------------------------------------------------------
    def test_todo_trade_case_roadmap_content(self):
        todo_path = os.path.join(PROJECT_ROOT, "todoTradeCase.md")
        self.assertTrue(os.path.isfile(todo_path), "todoTradeCase.md must exist at project root")

        with open(todo_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 4 required sections
        self.assertIn("Danh Mục Các Module Liên Quan Cần Hoàn Thành", content)
        self.assertIn("API Interface & Data Contract", content)
        self.assertIn("Kịch Bản Kiểm Thử Toàn Diện", content)
        self.assertIn("Quy Tắc Chốt Chặn Hồ Sơ (Stage Gate Rules)", content)


if __name__ == "__main__":
    unittest.main()
