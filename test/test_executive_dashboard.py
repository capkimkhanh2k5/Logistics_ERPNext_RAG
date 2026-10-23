import unittest
import os
import re
from apps.logistics_wizard.logistics_wizard.api import get_executive_dashboard_summary

class TestExecutiveDashboard(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.page_dir = os.path.join(self.base_dir, "apps", "logistics_wizard", "logistics_wizard", "page", "managementlogistic")
        self.html_path = os.path.join(self.page_dir, "managementlogistic.html")
        self.js_path = os.path.join(self.page_dir, "managementlogistic.js")
        self.css_path = os.path.join(self.page_dir, "managementlogistic.css")

    def test_executive_dashboard_api(self):
        """Verify get_executive_dashboard_summary returns full data contract."""
        res = get_executive_dashboard_summary()
        self.assertEqual(res.get("status"), "success")
        data = res.get("data", {})
        
        # 1. Metrics
        self.assertIn("metrics", data)
        metrics = data["metrics"]
        self.assertIn("total_cases", metrics)
        self.assertIn("in_transit_shipments", metrics)
        self.assertIn("active_exceptions", metrics)
        self.assertIn("total_spend", metrics)

        # 2. Pipeline Funnel
        self.assertIn("pipeline", data)
        self.assertEqual(len(data["pipeline"]), 5)

        # 3. Health Donut
        self.assertIn("health_donut", data)
        self.assertIn("score_pct", data["health_donut"])
        self.assertIn("segments", data["health_donut"])

        # 4. Cost Breakdown
        self.assertIn("cost_breakdown", data)
        self.assertIn("categories", data["cost_breakdown"])

        # 5. Corridors & Alerts
        self.assertIn("corridors", data)
        self.assertGreater(len(data["corridors"]), 0)
        self.assertIn("action_alerts", data)
        self.assertGreater(len(data["action_alerts"]), 0)

    def test_executive_dashboard_html_dom(self):
        """Verify Tab 1 Executive Dashboard DOM elements exist."""
        with open(self.html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Nav button
        self.assertIn('id="btn-tab-executive"', html)
        self.assertIn('data-tab="executive"', html)

        # Main Pane
        self.assertIn('id="tab-pane-executive"', html)
        self.assertIn('exec-header-bar', html)
        self.assertIn('exec-kpi-grid', html)
        self.assertIn('exec-pipeline-flow', html)
        self.assertIn('exec-donut-svg', html)
        self.assertIn('exec-cost-breakdown-list', html)
        self.assertIn('exec-corridors-container', html)
        self.assertIn('exec-alerts-container', html)

    def test_executive_dashboard_js_controller(self):
        """Verify ExecutiveDashboardController is declared and wired."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn('class ExecutiveDashboardController', js)
        self.assertIn('wrapper.executive_dashboard = new ExecutiveDashboardController(wrapper)', js)
        self.assertIn("wrapper.unifiedHub.switch_tab('executive')", js)
        self.assertIn('logistics_wizard.api.get_executive_dashboard_summary', js)

    def test_executive_dashboard_css_and_purple_ban(self):
        """Verify CSS classes and Purple Ban compliance."""
        with open(self.css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn('.exec-header-bar', css)
        self.assertIn('.exec-kpi-card', css)
        self.assertIn('.exec-pipeline-flow', css)
        self.assertIn('.exec-donut-svg', css)
        self.assertIn('.corridor-item', css)
        self.assertIn('.exec-alert-card', css)

        # Check no purple hex colors
        purple_hexes = ['#7c3aed', '#8b5cf6', '#6d28d9', '#a855f7', '#9333ea', '#c084fc', '#4f46e5', '#6366f1', '#4338ca']
        for hex_code in purple_hexes:
            self.assertNotIn(hex_code, css.lower())

if __name__ == '__main__':
    unittest.main()
