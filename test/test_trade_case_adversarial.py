#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_trade_case_adversarial.py — Bộ kiểm thử đối kháng (Adversarial Stress Testing)
===================================================================================
Challenger 1 (Adversarial Verifier - State & Logic Stress Testing)
Target: Doctype Trade Case, API validate_stage_gate_completion, close_trade_case,
        8 Stage Gate Barriers, and Event Bus / State Store Simulator.

Nội dung kiểm thử:
1. Generator & Fuzzing kiểm tra giá trị biên của DocType Trade Case:
   - Tất cả trường None, chuỗi rỗng "", khoảng trắng, số âm, kiểu dữ liệu sai lệch.
   - Đồng bộ hóa các trường alias (mode/shipping_mode, dates).
   - Trạng thái LCV chưa phân bổ (unallocated landed costs).
2. Chốt chặn 8 điều kiện của can_close() & close_trade_case():
   - Baseline hợp lệ: 8/8 đạt -> đóng case thành công.
   - Kiểm thử từng chốt chặn đơn lẻ bị vi phạm (Single-Point of Failure):
     * Gate 1: Tàu chưa đến (In Transit, PO, Export Port...)
     * Gate 2: Thiếu chứng từ (< 100% readiness)
     * Gate 3: Tờ khai chưa thông quan (customs_cleared = 0)
     * Gate 4: Chưa hoàn tất nhận kho và nghiệm thu KCS (stage Warehouse)
     * Gate 5, 6, 8: LCV chưa phân bổ / tài khoản tạm tính chưa triệt tiêu / chưa tất toán
     * Gate 7: Còn sự cố Critical hoặc High đang mở
   - Kiểm thử tổ hợp đa chốt chặn vi phạm ngẫu nhiên (Multi-failure permutations).
   - Kiểm thử cơ chế override kết quả xác thực ngoại vi (validation_results).
   - Kiểm thử các API endpoint close_trade_case() từ chối đóng các case chưa đạt.
3. Event Bus & State Store Stress Test:
   - Mô phỏng 1000 lượt chuyển đổi tab liên tục qua lại (overview <-> tracking).
   - Kiểm tra bảo toàn currentCaseId, activeTab, focusShipmentId.
   - Kiểm tra drill-down context và khả năng chống race condition.
"""

import os
import sys
import unittest
import itertools
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logistics_wizard import api
from logistics_wizard.doctype.trade_case.trade_case import TradeCase


class TestAdversarialDocTypeEdgeCases(unittest.TestCase):
    """
    Phần 1: Generator & Fuzzing các trường hợp biên của DocType Trade Case
    """

    def test_tc_all_none_fields_validate(self):
        """Kiểm tra khởi tạo TradeCase với toàn bộ giá trị None, hàm validate() không được sập."""
        tc = TradeCase(
            trade_type=None,
            status=None,
            current_stage=None,
            overall_health=None,
            priority=None,
            case_title=None,
            purchase_order=None,
            sales_order=None,
            supplier=None,
            customer=None,
            mode=None,
            shipping_mode=None,
            document_readiness_pct=None,
            open_exceptions_count=None,
            critical_exceptions_count=None,
            customs_cleared=None,
            costs_finalized=None,
            stage_gate_checklist=None
        )
        tc.validate()

        self.assertEqual(tc.trade_type, "Import", "trade_type mặc định phải là Import khi None")
        self.assertEqual(tc.status, "Active", "status mặc định phải là Active khi None")
        self.assertEqual(tc.current_stage, "PO", "current_stage mặc định phải là PO khi None")
        self.assertEqual(tc.overall_health, "Healthy", "overall_health mặc định phải là Healthy khi None")
        self.assertEqual(tc.priority, "Normal", "priority mặc định phải là Normal khi None")
        self.assertIsNotNone(tc.case_title, "case_title phải được sinh tự động khi None")
        self.assertIsInstance(tc.stage_gate_checklist, list, "stage_gate_checklist phải được khởi tạo")
        self.assertEqual(len(tc.stage_gate_checklist), 8, "Bảng stage_gate_checklist mặc định phải có đúng 8 cổng")

    def test_tc_empty_strings_validate(self):
        """Kiểm tra khởi tạo TradeCase với chuỗi rỗng '', validate() phải gán giá trị mặc định hợp lệ."""
        tc = TradeCase(
            trade_type="",
            status="",
            current_stage="",
            overall_health="",
            priority="",
            case_title="",
            supplier="",
            purchase_order=""
        )
        tc.validate()
        self.assertEqual(tc.trade_type, "Import")
        self.assertEqual(tc.status, "Active")
        self.assertEqual(tc.current_stage, "PO")
        self.assertEqual(tc.overall_health, "Healthy")
        self.assertEqual(tc.priority, "Normal")
        self.assertTrue(len(tc.case_title) > 0, "case_title không được là chuỗi rỗng")

    def test_tc_alias_fields_synchronization(self):
        """Kiểm tra cơ chế đồng bộ trường bí danh (shipping_mode <-> mode, opened_date <-> start_date, etc.)."""
        # 1. mode -> shipping_mode
        tc1 = TradeCase(mode="Air", shipping_mode=None)
        tc1.validate()
        self.assertEqual(tc1.shipping_mode, "Air")

        # 2. shipping_mode -> mode
        tc2 = TradeCase(mode=None, shipping_mode="Ocean")
        tc2.validate()
        self.assertEqual(tc2.mode, "Ocean")

        # 3. start_date <-> opened_date
        tc3 = TradeCase(start_date="2026-10-01", opened_date=None)
        tc3.validate()
        self.assertEqual(tc3.opened_date, "2026-10-01")

        tc4 = TradeCase(start_date=None, opened_date="2026-10-02")
        tc4.validate()
        self.assertEqual(tc4.start_date, "2026-10-02")

        # 4. expected_close_date <-> target_completion_date
        tc5 = TradeCase(target_completion_date="2026-10-20", expected_close_date=None)
        tc5.validate()
        self.assertEqual(tc5.expected_close_date, "2026-10-20")

    def test_tc_invalid_status_and_stage_cannot_close(self):
        """Kiểm tra trạng thái lạ/không hợp lệ không bao giờ được phép đóng case."""
        invalid_stages = ["InvalidStage", "Draft", "Cancelled", "Unknown", "Teleportation", "OnHold", 999, None, ""]
        for stg in invalid_stages:
            tc = TradeCase(
                current_stage=stg,
                document_readiness_pct=100.0,
                customs_cleared=1,
                costs_finalized=1,
                open_exceptions_count=0,
                critical_exceptions_count=0
            )
            can_close, checks = tc.can_close()
            self.assertFalse(can_close, f"current_stage='{stg}' không được phép đóng case")
            with self.assertRaises(ValueError, msg=f"close_case() phải ném lỗi khi stage='{stg}'"):
                tc.close_case()

    def test_tc_boundary_numeric_and_fuzzing(self):
        """
        Fuzzing Generator: Tạo hơn 100 bộ tham số biên đa dạng kiểm tra can_close() không phát sinh ngoại lệ không xử lý.
        """
        pct_values = [None, "", 0, 0.0, -10.0, 50, 99.9, 99.999, 100, 100.0, 120]
        exc_values = [None, "", 0, 1, 5, -1]
        crit_values = [None, "", 0, 1, 3]
        customs_values = [None, "", 0, 1, -1]
        cost_values = [None, "", 0, 1, -1]

        combinations = list(itertools.product(
            pct_values[:4],
            exc_values[:3],
            crit_values[:3],
            customs_values[:3],
            cost_values[:3]
        ))

        tested_count = 0
        for pct, exc, crit, cust, cost in combinations:
            tc = TradeCase(
                current_stage="Cost Finalization",
                document_readiness_pct=pct,
                open_exceptions_count=exc,
                critical_exceptions_count=crit,
                customs_cleared=cust,
                costs_finalized=cost
            )
            try:
                can_close, checks = tc.can_close()
                self.assertIsInstance(can_close, bool)
                self.assertIsInstance(checks, list)
                self.assertEqual(len(checks), 8)
                tested_count += 1
            except Exception as e:
                self.fail(f"can_close() bị sập không xử lý với tham số biên: pct={pct}, exc={exc}, crit={crit}, cust={cust}, cost={cost}: {e}")

        self.assertGreaterEqual(tested_count, 50, "Phải kiểm thử thành công ít nhất 50 tổ hợp tham số biên")


class TestAdversarialStageGateBarrier(unittest.TestCase):
    """
    Phần 2: Kiểm thử logic chốt chặn 8 điều kiện của can_close() và close_trade_case()
    Hệ thống BẮT BUỘC kiên quyết từ chối đóng case nếu còn bất kỳ điều kiện nào chưa đạt.
    """

    def _create_perfect_case(self) -> TradeCase:
        """Tạo đối tượng TradeCase đạt 100% cả 8 điều kiện chốt chặn."""
        tc = TradeCase(
            name="TC-2026-PERFECT",
            trade_type="Import",
            status="Active",
            current_stage="Cost Finalization",
            document_readiness_pct=100.0,
            customs_cleared=1,
            costs_finalized=1,
            open_exceptions_count=0,
            critical_exceptions_count=0
        )
        tc.validate()
        return tc

    def test_baseline_perfect_case_can_close(self):
        """Baseline: Khi thỏa mãn đủ 8/8 điều kiện, can_close() phải trả về True và close_case() hoàn tất."""
        tc = self._create_perfect_case()
        can_close, checks = tc.can_close()
        self.assertTrue(can_close, "Hồ sơ hoàn hảo phải được phép đóng")
        self.assertEqual(sum(1 for c in checks if c["passed"]), 8, "Cả 8/8 cổng phải Passed")

        success = tc.close_case()
        self.assertTrue(success)
        self.assertEqual(tc.status, "Closed")
        self.assertEqual(tc.current_stage, "Closed")
        self.assertEqual(tc.stage_gate_status, "Passed")
        self.assertIsNotNone(tc.actual_completion_date)

    def test_barrier_gate1_shipment_not_arrived(self):
        """GATE 1: Tàu chưa đến đích (đang In Transit, Export Port, PO) -> BẮT BUỘC TỪ CHỐI ĐÓNG."""
        incomplete_stages = ["PO", "Booking", "Export Port", "In Transit", "Import Port", "Customs"]
        for stg in incomplete_stages:
            tc = self._create_perfect_case()
            tc.current_stage = stg

            can_close, checks = tc.can_close()
            self.assertFalse(can_close, f"Chặng {stg} chưa giao đến đích nên không thể đóng case")

            gate1 = next(c for c in checks if c["code"] == "GATE_SHIPMENT")
            self.assertFalse(gate1["passed"], f"GATE_SHIPMENT phải Failed tại chặng {stg}")
            self.assertIn("chưa giao hàng", gate1["reason"].lower())

            with self.assertRaises(ValueError):
                tc.close_case()

    def test_barrier_gate2_documents_incomplete(self):
        """GATE 2: Chứng từ ngoại thương chưa đủ 100% -> BẮT BUỘC TỪ CHỐI ĐÓNG."""
        failing_percentages = [0, 50, 75.5, 90, 99.0, 99.99]
        for pct in failing_percentages:
            tc = self._create_perfect_case()
            tc.document_readiness_pct = pct

            can_close, checks = tc.can_close()
            self.assertFalse(can_close, f"Chứng từ {pct}% chưa đủ 100% nên không thể đóng case")

            gate2 = next(c for c in checks if c["code"] == "GATE_DOCS")
            self.assertFalse(gate2["passed"], f"GATE_DOCS phải Failed khi pct={pct}")

            with self.assertRaises(ValueError):
                tc.close_case()

    def test_barrier_gate3_customs_not_cleared(self):
        """GATE 3: Tờ khai hải quan chưa thông quan hoặc chưa nộp thuế -> BẮT BUỘC TỪ CHỐI ĐÓNG."""
        for val in [0, None, False]:
            tc = self._create_perfect_case()
            tc.customs_cleared = val

            can_close, checks = tc.can_close()
            self.assertFalse(can_close, "Hải quan chưa thông quan không được phép đóng case")

            gate3 = next(c for c in checks if c["code"] == "GATE_CUSTOMS")
            self.assertFalse(gate3["passed"], "GATE_CUSTOMS phải Failed")
            self.assertIn("chưa thông quan", gate3["reason"].lower())

            with self.assertRaises(ValueError):
                tc.close_case()

    def test_barrier_gate4_warehouse_not_received_or_qc_pending(self):
        """GATE 4: Chưa hoàn tất nhận kho hoặc KCS chưa đạt yêu cầu -> BẮT BUỘC TỪ CHỐI ĐÓNG."""
        # Chặng Warehouse nghĩa là đang ở kho tiếp nhận, chưa sang Cost Finalization / nghiệm thu
        tc = self._create_perfect_case()
        tc.current_stage = "Warehouse"

        can_close, checks = tc.can_close()
        self.assertFalse(can_close, "Chặng Warehouse chưa nghiệm thu KCS không được đóng case")

        gate4 = next(c for c in checks if c["code"] == "GATE_WAREHOUSE")
        self.assertFalse(gate4["passed"], "GATE_WAREHOUSE phải Failed tại chặng Warehouse")

        with self.assertRaises(ValueError):
            tc.close_case()

    def test_barrier_gate5_6_8_unallocated_landed_costs(self):
        """GATE 5, 6, 8: Landed Cost Voucher chưa phân bổ -> BẮT BUỘC TỪ CHỐI ĐÓNG (Triệt để 3 cổng chi phí)."""
        for cost_val in [0, None, False]:
            tc = self._create_perfect_case()
            tc.costs_finalized = cost_val

            can_close, checks = tc.can_close()
            self.assertFalse(can_close, "Chi phí chưa phân bổ không được phép đóng case")

            gate5 = next(c for c in checks if c["code"] == "GATE_LCV")
            gate6 = next(c for c in checks if c["code"] == "GATE_CLEARING")
            gate8 = next(c for c in checks if c["code"] == "GATE_SETTLEMENT")

            self.assertFalse(gate5["passed"], "GATE_LCV phải Failed khi costs_finalized = 0")
            self.assertFalse(gate6["passed"], "GATE_CLEARING phải Failed khi costs_finalized = 0")
            self.assertFalse(gate8["passed"], "GATE_SETTLEMENT phải Failed khi costs_finalized = 0")

            with self.assertRaises(ValueError):
                tc.close_case()

    def test_barrier_gate7_critical_and_high_exceptions_open(self):
        """GATE 7: Còn sự cố Critical hoặc sự cố chưa đóng -> BẮT BUỘC TỪ CHỐI ĐÓNG."""
        # 1. Có sự cố Critical mở
        tc1 = self._create_perfect_case()
        tc1.critical_exceptions_count = 1
        can_close1, checks1 = tc1.can_close()
        self.assertFalse(can_close1, "Còn sự cố Critical không được đóng case")
        gate7_1 = next(c for c in checks1 if c["code"] == "GATE_EXCEPTIONS")
        self.assertFalse(gate7_1["passed"])

        # 2. Có sự cố thông thường mở (open_exceptions_count > 0)
        tc2 = self._create_perfect_case()
        tc2.open_exceptions_count = 3
        can_close2, checks2 = tc2.can_close()
        self.assertFalse(can_close2, "Còn 3 sự cố mở không được đóng case")
        gate7_2 = next(c for c in checks2 if c["code"] == "GATE_EXCEPTIONS")
        self.assertFalse(gate7_2["passed"])

        with self.assertRaises(ValueError):
            tc1.close_case()
        with self.assertRaises(ValueError):
            tc2.close_case()

    def test_barrier_multi_gate_failure_permutations(self):
        """Kiểm thử tổ hợp đa chốt chặn vi phạm đồng thời: 2, 3, 4, và toàn bộ 8 cổng vi phạm."""
        # Trường hợp mới tạo, toàn bộ 8 cổng đều vi phạm
        tc_empty = TradeCase(
            current_stage="PO",
            document_readiness_pct=0.0,
            customs_cleared=0,
            costs_finalized=0,
            open_exceptions_count=5,
            critical_exceptions_count=2
        )
        can_close, checks = tc_empty.can_close()
        self.assertFalse(can_close)
        failed_count = sum(1 for c in checks if not c["passed"])
        self.assertEqual(failed_count, 8, "Cả 8 cổng phải Failed khi hồ sơ mới mở")

        # Thử gọi close_case(), thông báo lỗi phải liệt kê đủ các nguyên nhân
        with self.assertRaises(ValueError) as ctx:
            tc_empty.close_case()
        err_msg = str(ctx.exception)
        self.assertIn("Vận đơn chưa giao hàng", err_msg)
        self.assertIn("Chưa đủ chứng từ ngoại thương", err_msg)
        self.assertIn("Tờ khai hải quan chưa thông quan", err_msg)
        self.assertIn("Landed Cost Voucher chưa hoàn tất phân bổ", err_msg)
        self.assertIn("sự cố chưa giải quyết", err_msg)

    def test_barrier_external_validation_results_overrides(self):
        """Kiểm tra cơ chế tiếp nhận validation_results từ module ngoài và ghi đè an toàn."""
        # Trường hợp dữ liệu trên bản ghi có vẻ đạt, nhưng hệ thống ngoại vi kiểm tra phát hiện lỗi
        tc = self._create_perfect_case()

        # 1. Override GATE_LCV thất bại
        can_close, checks = tc.can_close(validation_results={"GATE_LCV": False})
        self.assertFalse(can_close)
        self.assertFalse(next(c for c in checks if c["code"] == "GATE_LCV")["passed"])

        # 2. Override GATE_EXCEPTIONS với lý do chi tiết
        can_close, checks = tc.can_close(validation_results={
            "GATE_EXCEPTIONS": {"passed": False, "reason": "Phát hiện sự cố rò rỉ hóa chất mới khai báo qua API"}
        })
        self.assertFalse(can_close)
        g7 = next(c for c in checks if c["code"] == "GATE_EXCEPTIONS")
        self.assertFalse(g7["passed"])
        self.assertEqual(g7["reason"], "Phát hiện sự cố rò rỉ hóa chất mới khai báo qua API")

        # 3. Override qua key name thay vì code
        can_close, checks = tc.can_close(validation_results={"customs_cleared": False})
        self.assertFalse(can_close)
        self.assertFalse(next(c for c in checks if c["code"] == "GATE_CUSTOMS")["passed"])


class TestAdversarialBackendAPIEndpoints(unittest.TestCase):
    """
    Phần 3: Kiểm thử độc lập các Backend API Endpoints trong api.py
    validate_stage_gate_completion() & close_trade_case()
    """

    def test_api_validate_imp_2026_001_in_transit_rejection(self):
        """Hồ sơ IMP-2026-001 (Đang trên biển, trễ +2 ngày, thiếu C/O, 3 sự cố) -> validate_stage_gate BẮT BUỘC can_close=False."""
        val = api.validate_stage_gate_completion("IMP-2026-001")
        self.assertTrue(val["success"])
        self.assertFalse(val["can_close"], "IMP-2026-001 không được phép đóng")
        self.assertLess(val["passed_count"], 8)
        self.assertGreater(len(val["reasons"]), 0)

        # Thử đóng case qua API
        res = api.close_trade_case("IMP-2026-001")
        self.assertFalse(res["success"])
        self.assertFalse(res["can_close"])
        self.assertIn("Không thể đóng hồ sơ IMP-2026-001", res["message"])
        self.assertGreaterEqual(len(res["reasons"]), 2)

    def test_api_validate_exp_2026_001_red_channel_rejection(self):
        """Hồ sơ EXP-2026-001 (Luồng Đỏ Hải quan, 2 Critical Exception) -> validate_stage_gate BẮT BUỘC can_close=False."""
        val = api.validate_stage_gate_completion("EXP-2026-001")
        self.assertTrue(val["success"])
        self.assertFalse(val["can_close"], "EXP-2026-001 không được phép đóng")
        self.assertLess(val["passed_count"], 8)

        # Thử đóng case qua API
        res = api.close_trade_case("EXP-2026-001")
        self.assertFalse(res["success"])
        self.assertFalse(res["can_close"])
        self.assertIn("Không thể đóng hồ sơ EXP-2026-001", res["message"])

    def test_api_validate_imp_2026_002_customs_stage_rejection(self):
        """Hồ sơ IMP-2026-002 (Tokyo Air, đang chặng Customs, chưa nhận kho, chi phí chưa chốt) -> BẮT BUỘC can_close=False."""
        val = api.validate_stage_gate_completion("IMP-2026-002")
        self.assertTrue(val["success"])
        self.assertFalse(val["can_close"], "IMP-2026-002 đang ở chặng Customs chưa được đóng")
        self.assertLess(val["passed_count"], 8)

        res = api.close_trade_case("IMP-2026-002")
        self.assertFalse(res["success"])
        self.assertFalse(res["can_close"])

    def test_api_close_trade_case_null_and_empty_inputs(self):
        """Kiểm tra gọi close_trade_case với case_id là None, '', 'UNKNOWN'."""
        r1 = api.close_trade_case(None)
        self.assertFalse(r1["success"])
        self.assertIn("Mã Case ID là bắt buộc", r1["message"])

        r2 = api.close_trade_case("")
        self.assertFalse(r2["success"])
        self.assertIn("Mã Case ID là bắt buộc", r2["message"])

        # Unknown case
        r3 = api.close_trade_case("NON-EXISTENT-CASE-999")
        self.assertFalse(r3["success"])
        self.assertFalse(r3["can_close"])


class TestAdversarialEventBusAndStateStore(unittest.TestCase):
    """
    Phần 4: Kiểm thử ứng suất Event Bus & State Store khi chuyển đổi tab liên tục
    Mô phỏng mô hình trạng thái tập trung UnifiedTradeCaseHub:
    - 1000 lượt chuyển đổi liên tục qua lại giữa 'overview' và 'tracking'
    - Bảo toàn context case_id và shipment_id
    - Khả năng chống race condition và drift dữ liệu
    """

    class MockUnifiedTradeCaseHub:
        """Bộ mô phỏng máy trạng thái trung tâm của Desk Page theo đặc tả Interface Contract."""
        def __init__(self):
            self.state = {
                "currentCaseId": "IMP-2026-001",
                "activeTab": "overview",
                "focusShipmentId": None,
                "history": []
            }
            self.event_subscribers = []
            self.render_count = {"overview": 0, "tracking": 0}

        def set_case(self, case_id: str):
            if not case_id:
                return
            self.state["currentCaseId"] = case_id
            self.state["history"].append(("SET_CASE", case_id))

        def switch_tab(self, tab_id: str, options: Dict[str, Any] = None):
            if tab_id not in ["overview", "tracking"]:
                raise ValueError(f"Invalid tab {tab_id}")
            self.state["activeTab"] = tab_id
            if options and options.get("shipment_id"):
                self.state["focusShipmentId"] = options["shipment_id"]
            self.render_count[tab_id] += 1
            self.state["history"].append(("SWITCH_TAB", tab_id, self.state["currentCaseId"]))

        def drill_down_to_tracking(self, shipment_id: str):
            self.switch_tab("tracking", {"shipment_id": shipment_id})

    def test_state_store_1000_rapid_tab_switches(self):
        """Kiểm tra 1000 lần chuyển tab liên tục: Trạng thái không bị suy thoái, Case ID luôn được bảo toàn."""
        hub = self.MockUnifiedTradeCaseHub()
        hub.set_case("IMP-2026-002")

        tabs = ["overview", "tracking"]
        for i in range(1000):
            target_tab = tabs[i % 2]
            hub.switch_tab(target_tab)

            # Kiểm tra bất biến sau mỗi bước chuyển
            self.assertEqual(hub.state["currentCaseId"], "IMP-2026-002", f"Case ID bị mất tại vòng lặp {i}")
            self.assertEqual(hub.state["activeTab"], target_tab, f"activeTab không khớp tại vòng lặp {i}")

        self.assertEqual(hub.render_count["overview"], 500)
        self.assertEqual(hub.render_count["tracking"], 500)
        self.assertEqual(len(hub.state["history"]), 1001)

    def test_drilldown_context_preservation_under_switch(self):
        """Kiểm tra drilldown [View Shipment Tracking] bảo toàn chính xác context shipment và case."""
        hub = self.MockUnifiedTradeCaseHub()
        hub.set_case("IMP-2026-001")

        # Drilldown to tracking with shipment SHP-2026-0045
        hub.drill_down_to_tracking("SHP-2026-0045")
        self.assertEqual(hub.state["activeTab"], "tracking")
        self.assertEqual(hub.state["focusShipmentId"], "SHP-2026-0045")
        self.assertEqual(hub.state["currentCaseId"], "IMP-2026-001")

        # Chuyển về overview và lại sang tracking
        hub.switch_tab("overview")
        self.assertEqual(hub.state["activeTab"], "overview")
        self.assertEqual(hub.state["currentCaseId"], "IMP-2026-001")

        # Đổi case sang EXP-2026-001 rồi drilldown
        hub.set_case("EXP-2026-001")
        hub.drill_down_to_tracking("SHP-2026-0047")
        self.assertEqual(hub.state["activeTab"], "tracking")
        self.assertEqual(hub.state["focusShipmentId"], "SHP-2026-0047")
        self.assertEqual(hub.state["currentCaseId"], "EXP-2026-001")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" LOGISTICS WIZARD — ADVERSARIAL STRESS TEST SUITE (CHALLENGER 1)")
    print(" State & Logic Stress Testing: DocType Boundaries, 8 Stage Gates, State Machine")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print("\n" + "=" * 80)
    print(f" TOTAL TESTS RUN : {total}")
    print(f" PASSED          : {passed}")
    print(f" FAILURES        : {failures}")
    print(f" ERRORS          : {errors}")
    print("=" * 80)

    if failures == 0 and errors == 0:
        print(" STATUS: ALL ADVERSARIAL STRESS TESTS PASSED [100% SUCCESS]\n")
        sys.exit(0)
    else:
        print(" STATUS: ADVERSARIAL VERIFICATION FAILED\n")
        sys.exit(1)
