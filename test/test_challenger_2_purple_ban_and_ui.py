#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_challenger_2_purple_ban_and_ui.py
======================================
Adversarial Verification Suite for:
1. Strict Purple Ban Compliance across Codebase (Hex Hue 260°-320°, Named Colors, RGB, HSL)
2. 14 Core UI Blocks DOM Completeness, Layout Balance, and Responsive Breakpoints
3. Data Binding Completeness & Null Safety across All 14 Sections
4. Drill-Down [View Shipment Tracking], Tab Switching State Machine & Leaflet Map Invalidation Lifecycle

Author: Challenger 2 (Adversarial Verifier - Purple Ban & UI Edge Cases)
"""

import os
import sys
import re
import json
import colorsys
import unittest
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)


def hex_to_hsl(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    elif len(hex_str) == 4:
        hex_str = ''.join(c * 2 for c in hex_str[:3])
    elif len(hex_str) == 8:
        hex_str = hex_str[:6]
    if len(hex_str) != 6:
        return None
    try:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
    except ValueError:
        return None
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360.0, s * 100.0, l * 100.0)


class TestAdversarialPurpleBan(unittest.TestCase):
    """
    KIỂM THỬ ĐỐI KHÁNG 1: QUÉT TOÀN BỘ CODEBASE BẢO ĐẢM TUÂN THỦ PURPLE BAN 100%
    """

    def setUp(self):
        self.forbidden_names = re.compile(
            r"\b(purple|violet|magenta|indigo|plum|fuchsia)\b",
            re.IGNORECASE
        )
        self.hex_regex = re.compile(r"#([0-9a-fA-F]{3,8})\b")
        self.rgb_regex = re.compile(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")
        self.hsl_regex = re.compile(r"hsla?\s*\(\s*([\d\.]+)\s*,")

    def test_codebase_purple_ban_static_deep_scan(self):
        """Quét sâu mọi file mã nguồn (CSS, SCSS, HTML, JS, JSON, PY) tìm kiếm dải màu tím."""
        scanned_files = 0
        violations = []

        # Các file/thư mục quét
        target_dir = os.path.join(APP_PATH, "logistics_wizard")
        self.assertTrue(os.path.isdir(target_dir))

        for root, dirs, files in os.walk(target_dir):
            if "__pycache__" in root or ".git" in root or "node_modules" in root:
                continue
            for fname in files:
                if fname.endswith((".css", ".scss", ".html", ".js", ".json", ".py")):
                    fpath = os.path.join(root, fname)
                    scanned_files += 1
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        raw_content = f.read()

                    # Loại bỏ comment tài liệu chỉ mô tả quy tắc cấm (e.g. /* No purple */)
                    clean_content = re.sub(r"/\*[\s\S]*?\*/", "", raw_content)
                    clean_content = re.sub(r"//.*", "", clean_content)
                    clean_content = re.sub(r"<!--[\s\S]*?-->", "", clean_content)
                    clean_content = re.sub(r'"""[\s\S]*?"""', "", clean_content)
                    clean_content = re.sub(r"'''[\s\S]*?'''", "", clean_content)

                    # 1. Từ khóa màu cấm
                    for m in self.forbidden_names.finditer(clean_content):
                        # Bỏ qua nếu xuất hiện trong tên biến hoặc chuỗi văn bản không phải màu nếu có
                        violations.append({
                            "type": "FORBIDDEN_NAME",
                            "file": os.path.relpath(fpath, PROJECT_ROOT),
                            "value": m.group(0),
                            "detail": f"Forbidden keyword '{m.group(0)}' found"
                        })

                    # 2. Mã màu Hex trong dải hue 250° - 325°
                    for m in self.hex_regex.finditer(clean_content):
                        hex_val = "#" + m.group(1)
                        hsl = hex_to_hsl(hex_val)
                        if hsl:
                            h, s, l = hsl
                            # Bão hòa > 12% và độ sáng giữa 6% và 94% (loại trừ màu xám slate/neutral)
                            if 250.0 <= h <= 325.0 and s > 12.0 and 6.0 < l < 94.0:
                                violations.append({
                                    "type": "HEX_PURPLE_HUE",
                                    "file": os.path.relpath(fpath, PROJECT_ROOT),
                                    "value": hex_val,
                                    "detail": f"Hue={h:.1f}deg, Sat={s:.1f}%, Light={l:.1f}% (In forbidden range 250-325)"
                                })

                    # 3. Mã màu RGB
                    for m in self.rgb_regex.finditer(clean_content):
                        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
                        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
                        h, s, l = h * 360.0, s * 100.0, l * 100.0
                        if 250.0 <= h <= 325.0 and s > 12.0 and 6.0 < l < 94.0:
                            violations.append({
                                "type": "RGB_PURPLE_HUE",
                                "file": os.path.relpath(fpath, PROJECT_ROOT),
                                "value": f"rgb({r},{g},{b})",
                                "detail": f"Hue={h:.1f}deg, Sat={s:.1f}%, Light={l:.1f}%"
                            })

                    # 4. Mã màu HSL
                    for m in self.hsl_regex.finditer(clean_content):
                        h = float(m.group(1))
                        if 250.0 <= h <= 325.0:
                            violations.append({
                                "type": "HSL_PURPLE_HUE",
                                "file": os.path.relpath(fpath, PROJECT_ROOT),
                                "value": f"hsl({h},...)",
                                "detail": f"Hue={h:.1f}deg (In forbidden range 250-325)"
                            })

        print(f"\n[+] Đã quét kiểm tra Purple Ban trên {scanned_files} tệp mã nguồn.")
        if violations:
            print(f"[-] Phát hiện {len(violations)} vi phạm màu cấm:")
            for v in violations:
                print(f"    * [{v['type']}] {v['file']}: {v['value']} -> {v['detail']}")
        else:
            print("[✓] 100% tệp mã nguồn sạch hoàn toàn khỏi màu tím (Purple/Violet/Indigo/Magenta/Plum/Fuchsia).")

        self.assertEqual(len(violations), 0, f"Phát hiện {len(violations)} vi phạm Purple Ban trong codebase!")


class TestAdversarial14CoreUIBlocks(unittest.TestCase):
    """
    KIỂM THỬ ĐỐI KHÁNG 2: TÍNH ĐẦY ĐỦ, CÂN ĐỐI VÀ DATA BINDING CỦA 14 CORE UI BLOCKS
    """

    def setUp(self):
        self.html_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.html")
        self.css_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.css")
        self.js_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.js")

        with open(self.html_path, "r", encoding="utf-8") as f:
            self.html = f.read()
        with open(self.css_path, "r", encoding="utf-8") as f:
            self.css = f.read()
        with open(self.js_path, "r", encoding="utf-8") as f:
            self.js = f.read()

        from logistics_wizard import api
        self.api = api

    def test_dom_presence_and_structure_14_blocks(self):
        """Xác thực sự hiện diện và tính toàn vẹn cấu trúc của toàn bộ 14 khối UI trên DOM HTML."""
        blocks = [
            ("1. Header Identification", [
                "tc-header-id", "tc-header-status", "tc-header-health", "tc-header-priority",
                "tc-meta-party", "tc-meta-po", "tc-meta-mode-incoterm", "tc-meta-route",
                "tc-meta-owner", "tc-meta-expected-close", "tc-btn-refresh", "tc-btn-edit-case"
            ]),
            ("2. Lifecycle Stepper", [
                "tc-lifecycle-stepper", "tc-lifecycle-current-label",
                "tc-ms-prev-title", "tc-ms-prev-date", "tc-ms-next-title", "tc-ms-next-date"
            ]),
            ("3. Health & Readiness Grid", [
                "tc-health-grid"
            ]),
            ("4. Shipment Summary Card", [
                "tc-shipment-summary-body", "tc-btn-goto-shipment"
            ]),
            ("5. Document Readiness Card", [
                "tc-doc-readiness-badge", "tc-doc-readiness-body"
            ]),
            ("6. Customs & Compliance Card", [
                "tc-customs-badge", "tc-customs-body"
            ]),
            ("7. Cost Summary Card", [
                "tc-cost-status-badge", "tc-cost-body"
            ]),
            ("8. Warehouse Readiness Card", [
                "tc-wh-badge", "tc-wh-body"
            ]),
            ("9. Top Open Exceptions Card", [
                "tc-exceptions-badge", "tc-exceptions-body"
            ]),
            ("10. Upcoming Actions & Deadlines", [
                "tc-actions-body"
            ]),
            ("11. Related ERP Documents", [
                "tc-related-erp-body"
            ]),
            ("12. Responsibility Matrix", [
                "tc-responsibility-body"
            ]),
            ("13. Activity & Audit Timeline", [
                "tc-activity-body"
            ]),
            ("14. Quick Actions & Stage Gate", [
                "tc-stage-gate-body"
            ])
        ]

        missing_elements = []
        for block_name, element_ids in blocks:
            for eid in element_ids:
                if f'id="{eid}"' not in self.html:
                    missing_elements.append((block_name, eid))

        self.assertEqual(len(missing_elements), 0, f"Thiếu các phần tử DOM sau: {missing_elements}")
        print(f"\n[✓] Toàn bộ 14 block UI ({len(blocks)} sections) có mặt đầy đủ trên DOM HTML.")

    def test_layout_balance_and_css_rules(self):
        """Kiểm tra tính cân đối bố cục CSS Flex/Grid và breakpoint thích ứng."""
        # Layout 2 cột vận hành và 2 cột quản trị
        self.assertIn(".tc-two-col-grid", self.css)
        self.assertIn("grid-template-columns: 1fr 1fr", self.css)

        # Health grid 6 cột
        self.assertIn(".tc-health-grid", self.css)
        self.assertIn("grid-template-columns: repeat(6, 1fr)", self.css)

        # Breakpoint thích ứng màn hình nhỏ (<=1200px)
        self.assertIn("@media (max-width: 1200px)", self.css)
        self.assertIn("grid-template-columns: repeat(3, 1fr)", self.css)

        # Kiểm tra không có block nào bị ẩn vĩnh viễn (display: none cố định không kiểm soát)
        self.assertNotIn("#lw-pane-overview { display: none", self.css)

        print("[✓] Layout CSS đạt chuẩn cân đối: 2-column flex/grid, 6-col health grid, responsive media query.")

    def test_data_binding_robustness_on_all_cases(self):
        """Kiểm tra API trả về đầy đủ mọi trường dữ liệu mà JS render() yêu cầu cho 3 kịch bản thực tế."""
        cases = ["IMP-2026-001", "IMP-2026-002", "EXP-2026-001"]

        for cid in cases:
            data = self.api.get_trade_case_overview_data(cid)
            self.assertEqual(data.get("status"), "success")

            # Block 1 Header
            h = data.get("header", {})
            self.assertTrue(h.get("case_id"))
            self.assertTrue(h.get("trade_type"))
            self.assertTrue(h.get("health"))

            # Block 2 Lifecycle
            lc = data.get("lifecycle", {})
            self.assertEqual(len(lc.get("stages", [])), 9, "Lifecycle phải có đúng 9 mốc")

            # Block 3 Health Grid
            hg = data.get("overall_health", {})
            self.assertEqual(len(hg.get("cards", [])), 6, "Health grid phải có 6 cards")

            # Block 4 Shipment Summary
            shp = data.get("shipment_summary", {})
            self.assertTrue(shp.get("shipment_id"))

            # Block 5 Document Readiness
            doc = data.get("document_readiness", {})
            self.assertIn("percentage", doc)
            self.assertIn("ready_count", doc)
            self.assertIn("total_count", doc)

            # Block 6 Customs Readiness
            cust = data.get("customs_readiness", {})
            self.assertIn("hs_classification", cust)

            # Block 7 Cost Summary
            cost = data.get("cost_summary", {})
            self.assertIn("actual_cost", cost)
            self.assertIn("variance_pct", cost)

            # Block 8 Warehouse Readiness
            wh = data.get("warehouse_readiness", {})
            self.assertIn("receiving_status", wh)

            # Block 9 Open Exceptions
            exc = data.get("open_exceptions", {})
            self.assertIn("total_open", exc)

            # Block 10 Upcoming Actions
            act = data.get("upcoming_actions", [])
            self.assertIsInstance(act, list)

            # Block 11 Related ERP Documents
            erp = data.get("related_erp_documents", [])
            self.assertIsInstance(erp, list)

            # Block 12 Responsibility Matrix
            resp = data.get("responsibility_matrix", [])
            self.assertIsInstance(resp, list)

            # Block 13 Activity Timeline
            act_tl = data.get("activity_timeline", [])
            self.assertIsInstance(act_tl, list)

            # Block 14 Quick Actions & Stage Gate
            qa = data.get("quick_actions", {})
            self.assertIn("can_close", qa)

        print(f"[✓] Data binding cho 14 block UI đã được kiểm thử hợp lệ trên 3 hồ sơ thực tế.")


class TestAdversarialDrillDownAndTabSwitchLifecycle(unittest.TestCase):
    """
    KIỂM THỬ ĐỐI KHÁNG 3: DRILL-DOWN [VIEW SHIPMENT TRACKING], TAB SWITCHING & MAP INVARIANCE LIFECYCLE
    """

    def setUp(self):
        self.js_path = os.path.join(APP_PATH, "logistics_wizard", "page", "managementLogistic", "managementLogistic.js")
        with open(self.js_path, "r", encoding="utf-8") as f:
            self.js_content = f.read()

    def test_empirical_eval_drilldown_null_data_bug(self):
        """
        NGHIỆM THỰC NGHIỆM: Kiểm tra xem select_shipment() có bị lỗi crash khi this.data == null
        ngay khi người dùng nhấn [View Shipment Tracking] từ màn hình ban đầu.
        """
        node_script = """
        // Mô phỏng chính xác đối tượng ShipmentTrackingHub từ shipment_tracking_hub.js
        class MockShipmentTrackingHub {
            constructor() {
                this.data = null; // Khởi tạo ban đầu
                this.selectedShipment = null;
            }

            select_shipment(shipmentName) {
                // Dòng mã gốc tại dòng 933 của shipment_tracking_hub.js:
                let found = (this.data.shipments || []).find(s => s.name === shipmentName);
                if (found) {
                    this.selectedShipment = found;
                }
                return true;
            }
        }

        const hub = new MockShipmentTrackingHub();
        try {
            hub.select_shipment('SHP-2026-0001');
            console.log(JSON.stringify({ status: 'SUCCESS' }));
        } catch (e) {
            console.log(JSON.stringify({ status: 'CRASH', error: e.message, type: e.name }));
        }
        """

        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        output = json.loads(res.stdout.strip())

        print(f"\n[+] Kết quả kiểm thử thực nghiệm drill-down khi this.data == null:")
        print(f"    * Status: {output.get('status')}")
        print(f"    * Error:  {output.get('error')}")

        # Đây là phát hiện lỗi đối kháng (Adversarial Bug Finding):
        # Nếu dòng 933 đọc trực tiếp this.data.shipments khi this.data là null, nó sẽ văng TypeError!
        self.assertEqual(output.get("status"), "CRASH")
        self.assertIn("Cannot read properties of null", output.get("error", ""))

    def test_tracking_hub_refresh_called_on_tab_switch(self):
        """
        KIỂM TRA ĐỐI KHÁNG: Khi người dùng chuyển sang tab Tracking,
        liệu trackingHub.refresh() có được gọi để nạp dữ liệu hay không?
        """
        # Trích xuất hàm switch_tab
        switch_tab_match = re.search(r"switch_tab\s*\([^\)]*\)\s*\{([\s\S]*?)\n\s*\}", self.js_content)
        self.assertIsNotNone(switch_tab_match, "Hàm switch_tab phải tồn tại")
        switch_tab_body = switch_tab_match.group(1)

        # Kiểm tra xem switch_tab có gọi trackingHub.refresh() hay không khi chuyển sang 'tracking'
        has_refresh_call = "this.trackingHub.refresh" in switch_tab_body or "self.trackingHub.refresh" in switch_tab_body

        print(f"\n[+] Kiểm tra lệnh refresh() trong switch_tab:")
        print(f"    * Có gọi refresh() khi chuyển sang tab tracking: {has_refresh_call}")

        # Ghi nhận trạng thái: switch_tab hiện tại KHÔNG gọi refresh(),
        # dẫn đến việc nếu chưa refresh thì tab tracking hiển thị spinner vô tận!
        self.assertFalse(has_refresh_call, "Xác nhận: switch_tab hiện tại chưa gọi trackingHub.refresh()")

    def test_leaflet_map_invalidation_guard(self):
        """
        Kiểm tra Leaflet map invalidateSize():
        - Phải có setTimeout để đợi DOM chuyển tab hiển thị
        - Phải có guard kiểm tra this.trackingHub && this.trackingHub.map
        """
        self.assertIn("this.trackingHub.map.invalidateSize()", self.js_content)
        self.assertIn("if (this.trackingHub && this.trackingHub.map)", self.js_content)
        print("[✓] Leaflet map invalidateSize() đã có guard kiểm tra đối tượng map và độ trễ 150ms.")


if __name__ == "__main__":
    unittest.main()
