#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_trade_cost_dashboard_and_widget.py
=======================================
Verification suite for:
1. Dedicated Trade Cost & Landed Cost Dashboard (Page files, DOM, controller)
2. Global Desk PopUp Floating ChatBot Widget (FAB, Drawer, hooks.py registration)
3. Logistics Wizard Workspace definition (Shortcuts, Links, DocTypes)
"""

import os
import json
import unittest
import re

BENCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(BENCH_ROOT, "apps", "logistics_wizard", "logistics_wizard")
DASH_PAGE_DIR = os.path.join(APP_DIR, "page", "trade_cost_dashboard")
CHAT_PAGE_DIR = os.path.join(APP_DIR, "page", "logistics_ai_chatbot")
WORKSPACE_DIR = os.path.join(APP_DIR, "workspace", "logistics_wizard")


class TestTradeCostDashboardAndWidget(unittest.TestCase):
    def test_01_dashboard_page_files_exist(self):
        """Kiểm tra sự hiện diện của 4 tệp DocType Page Trade Cost Dashboard"""
        files = [
            "trade_cost_dashboard.json",
            "trade_cost_dashboard.html",
            "trade_cost_dashboard.css",
            "trade_cost_dashboard.js"
        ]
        for f in files:
            path = os.path.join(DASH_PAGE_DIR, f)
            self.assertTrue(os.path.exists(path), f"Thiếu tệp: {f}")
            self.assertGreater(os.path.getsize(path), 100)

    def test_02_dashboard_json_spec(self):
        """Xác thực cấu hình Page JSON trade-cost-dashboard"""
        json_path = os.path.join(DASH_PAGE_DIR, "trade_cost_dashboard.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("doctype"), "Page")
        self.assertEqual(data.get("page_name"), "trade-cost-dashboard")
        self.assertEqual(data.get("title"), "Trade Cost & Landed Cost Dashboard")

    def test_03_dashboard_html_dom_elements(self):
        """Kiểm tra các thành phần cốt lõi của Dashboard: 4 KPI, 11 Cost Types, Allocation Sandbox, Export, Ledger"""
        html_path = os.path.join(DASH_PAGE_DIR, "trade_cost_dashboard.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        core_elements = [
            'id="trade-cost-dashboard-app"',
            'id="filter-case-type"',
            'id="select-active-case"',
            'id="kpi-actual-cost"',
            'id="kpi-surcharge-rate"',
            'id="kpi-allocation-status"',
            'id="kpi-anomalies-count"',
            'id="table-cost-items"',
            'id="section-allocation-engine"',
            'class="allocation-rule-selector"',
            'id="table-allocation-items"',
            'id="section-export-tracker"',
            'id="table-cost-sheets-ledger"'
        ]
        for el in core_elements:
            self.assertIn(el, content, f"Dashboard HTML thiếu thành phần: {el}")

    def test_04_dashboard_css_purple_ban(self):
        """Đảm bảo CSS Dashboard không chứa bất kỳ từ khóa màu tím nào"""
        css_path = os.path.join(DASH_PAGE_DIR, "trade_cost_dashboard.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        forbidden = re.compile(r"\b(purple|violet|magenta|indigo|plum|fuchsia)\b", re.IGNORECASE)
        clean_css = re.sub(r"/\*[\s\S]*?\*/", "", content)
        matches = forbidden.findall(clean_css)
        self.assertEqual(matches, [], f"Phát hiện màu tím trong CSS Dashboard: {matches}")

    def test_05_floating_widget_files_and_hooks(self):
        """Kiểm tra Widget Floating Action Button và khai báo trong hooks.py"""
        js_path = os.path.join(APP_DIR, "public", "js", "logistics_chatbot_widget.js")
        css_path = os.path.join(APP_DIR, "public", "css", "logistics_chatbot_widget.css")
        hooks_path = os.path.join(APP_DIR, "hooks.py")

        self.assertTrue(os.path.exists(js_path), "Thiếu logistics_chatbot_widget.js")
        self.assertTrue(os.path.exists(css_path), "Thiếu logistics_chatbot_widget.css")

        with open(hooks_path, "r", encoding="utf-8") as f:
            hooks_content = f.read()

        self.assertIn('"logistics_chatbot_widget.js"', hooks_content, "hooks.py app_include_js thiếu logistics_chatbot_widget.js")
        self.assertIn('"logistics_chatbot_widget.css"', hooks_content, "hooks.py app_include_css thiếu logistics_chatbot_widget.css")

        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        self.assertIn("logistics-ai-fab-container", js_content)
        self.assertIn("logistics-ai-drawer", js_content)
        self.assertIn("btn-drawer-fullscreen", js_content)

    def test_06_workspace_definition(self):
        """Kiểm tra cấu hình Workspace Logistics Wizard có đầy đủ Shortcut đến ChatBot và Cost Dashboard"""
        ws_path = os.path.join(WORKSPACE_DIR, "logistics_wizard.json")
        self.assertTrue(os.path.exists(ws_path), "Thiếu tệp Workspace logistics_wizard.json")

        with open(ws_path, "r", encoding="utf-8") as f:
            ws_data = json.load(f)

        self.assertEqual(ws_data.get("doctype"), "Workspace")
        self.assertEqual(ws_data.get("label"), "Logistics Wizard")

        shortcuts = [s.get("link_to") for s in ws_data.get("shortcuts", [])]
        self.assertIn("logistics-ai-chatbot", shortcuts, "Thiếu shortcut đến logistics-ai-chatbot")
        self.assertIn("trade-cost-dashboard", shortcuts, "Thiếu shortcut đến trade-cost-dashboard")
        self.assertIn("Trade Cost Sheet", shortcuts, "Thiếu shortcut đến Trade Cost Sheet")


if __name__ == "__main__":
    unittest.main()
