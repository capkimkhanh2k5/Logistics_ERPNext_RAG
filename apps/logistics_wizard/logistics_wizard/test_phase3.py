# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
import random
from frappe.utils import today, add_days, flt
from frappe.exceptions import ValidationError

class Phase3TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.supplier = "Apple Inc." if frappe.db.exists("Supplier", "Apple Inc.") else "Apple Inc"
        self.test_case_name = None
        self.test_shipment_name = None
        self.run_suffix = f"{random.randint(10, 99)}"

    def record_pass(self, test_name, msg=""):
        self.passed += 1
        self.results.append((True, test_name, msg))
        print(f"  [PASS] {test_name}: {msg}")

    def record_fail(self, test_name, error=""):
        self.failed += 1
        self.results.append((False, test_name, error))
        print(f"  [FAIL] {test_name}: {error}")

    def run_all(self):
        print("\n=======================================================")
        print(" BẮT ĐẦU CHẠY BỘ KIỂM THỬ GIAI ĐOẠN 3 (PHASE 3 TEST SUITE)")
        print(" [Hồ sơ Thương mại Trade Case & Phân hệ Hải quan VNACCS]")
        print("=======================================================\n")

        self.test_case_1_create_trade_case_series()
        self.test_case_2_auto_generate_standard_documents()
        self.test_case_3_stage_gate_document_readiness_transition()
        self.test_case_4_link_child_shipment_to_trade_case()
        self.test_case_5_rollup_shipment_costs_to_trade_case()
        self.test_case_6_customs_declaration_vnaccs_validation()
        self.test_case_7_auto_lookup_customs_exchange_rate()
        self.test_case_8_customs_duty_and_vat_tax_math()
        self.test_case_9_customs_clearance_sync_to_shipment_milestones()
        self.test_case_10_import_permit_validity_check()

        print("\n=======================================================")
        print(f" KẾT QUẢ KIỂM THỬ GIAI ĐOẠN 3: {self.passed} ĐẠT / {self.passed + self.failed} TRƯỜNG HỢP")
        print("=======================================================\n")
        return self.failed == 0

    def test_case_1_create_trade_case_series(self):
        """TC1: Tạo Hồ sơ Thương mại Trade Case với Naming Series chuẩn IMP-.YYYY.-.#####"""
        try:
            doc = frappe.get_doc({
                "doctype": "Trade Case",
                "case_title": f"Hồ sơ Nhập khẩu Apple Tết 2026 #{self.run_suffix}",
                "trade_type": "Import",
                "supplier": self.supplier,
                "incoterm": "CIF",
                "currency": "USD",
                "exchange_rate": 25400.0,
                "total_contract_amount": 1000000.0,
                "total_budget_vnd": 25500000000.0,
                "status": "Active"
            })
            doc.insert(ignore_permissions=True)
            self.test_case_name = doc.name

            assert doc.name.startswith("IMP-2026-"), f"Mã Trade Case không đúng quy chuẩn: {doc.name}"
            assert doc.trade_type == "Import"
            assert doc.stage_gate_status == "Not Ready"

            self.record_pass("TC1 - Tạo Hồ sơ Thương mại Trade Case", f"Đã sinh mã {doc.name} theo series IMP-.YYYY.-.#####")
        except Exception as e:
            self.record_fail("TC1 - Tạo Hồ sơ Thương mại Trade Case", str(e))

    def test_case_2_auto_generate_standard_documents(self):
        """TC2: Tự động khởi tạo Danh mục 8 chứng từ kiểm soát chuẩn khi bảng documents để trống"""
        try:
            assert self.test_case_name, "Cần TC1 thành công để chạy TC2"
            doc = frappe.get_doc("Trade Case", self.test_case_name)

            doc_types = [d.document_type for d in doc.documents]
            assert "Contract" in doc_types, "Thiếu chứng từ Hợp đồng"
            assert "Commercial Invoice" in doc_types, "Thiếu chứng từ Commercial Invoice"
            assert "Packing List" in doc_types, "Thiếu chứng từ Packing List"
            assert "Bill of Lading" in doc_types, "Thiếu chứng từ B/L"
            assert "Certificate of Origin" in doc_types, "Thiếu chứng từ C/O"
            assert "Customs Declaration" in doc_types, "Thiếu chứng từ Tờ khai Hải quan"

            mandatory_count = len([d for d in doc.documents if d.is_mandatory])
            assert mandatory_count >= 6, f"Kỳ vọng ít nhất 6 chứng từ bắt buộc, thực tế {mandatory_count}"

            self.record_pass("TC2 - Tự động tạo Checklist Chứng từ", f"Đã sinh sẵn {len(doc.documents)} chứng từ kiểm soát ({mandatory_count} bắt buộc)")
        except Exception as e:
            self.record_fail("TC2 - Tự động tạo Checklist Chứng từ", str(e))

    def test_case_3_stage_gate_document_readiness_transition(self):
        """TC3: Kiểm tra chuyển đổi trạng thái Stage Gate dựa trên % phê duyệt chứng từ bắt buộc"""
        try:
            assert self.test_case_name, "Cần TC1 thành công"
            doc = frappe.get_doc("Trade Case", self.test_case_name)

            # Ban đầu tất cả Pending -> readiness = 0% -> Not Ready
            assert doc.document_readiness_pct == 0.0
            assert doc.stage_gate_status == "Not Ready"

            # Phê duyệt toàn bộ các chứng từ bắt buộc
            for row in doc.documents:
                if row.is_mandatory:
                    row.status = "Approved"

            doc.save(ignore_permissions=True)

            assert doc.document_readiness_pct == 100.0, f"Readiness kỳ vọng 100%, thực tế: {doc.document_readiness_pct}"
            assert doc.stage_gate_status == "Document Ready", f"Stage Gate kỳ vọng Document Ready, thực tế: {doc.stage_gate_status}"

            self.record_pass("TC3 - Cơ chế Cổng kiểm soát Stage Gate 1", "Khi duyệt đủ 100% chứng từ bắt buộc, trạng thái tự chuyển sang Document Ready")
        except Exception as e:
            self.record_fail("TC3 - Cơ chế Cổng kiểm soát Stage Gate 1", str(e))

    def test_case_4_link_child_shipment_to_trade_case(self):
        """TC4: Gắn Chuyến tàu con (Trade Shipment) vào Hồ sơ Thương mại mẹ (Mô hình Partial Shipment)"""
        try:
            shipment = frappe.get_doc({
                "doctype": "Trade Shipment",
                "shipment_name": f"Đợt giao 1 - Vessel Maersk #{self.run_suffix}",
                "supplier": self.supplier,
                "trade_type": "Import",
                "trade_case": self.test_case_name,
                "incoterm": "CIF",
                "transport_mode": "Ocean FCL",
                "status": "In Transit",
                "cost_items": [
                    {
                        "charge_type": "Cước vận tải biển quốc tế (Ocean Freight)",
                        "budgeted_amount_cur": 3000.0,
                        "budgeted_fx_rate": 25400.0,
                        "actual_amount_cur": 3100.0,
                        "actual_fx_rate": 25450.0
                    }
                ]
            })
            shipment.insert(ignore_permissions=True)
            self.test_shipment_name = shipment.name

            assert shipment.trade_case == self.test_case_name
            assert shipment.trade_type == "Import"

            self.record_pass("TC4 - Mô hình Đợt giao hàng con (Partial Shipment)", f"Chuyến hàng {shipment.name} đã liên kết thành công vào Case {self.test_case_name}")
        except Exception as e:
            self.record_fail("TC4 - Mô hình Đợt giao hàng con (Partial Shipment)", str(e))

    def test_case_5_rollup_shipment_costs_to_trade_case(self):
        """TC5: Tổng hợp chi phí thực tế và kiểm tra chênh lệch ngân sách từ các Chuyến hàng con lên Case"""
        try:
            assert self.test_case_name and self.test_shipment_name
            case_doc = frappe.get_doc("Trade Case", self.test_case_name)
            case_doc.save(ignore_permissions=True)

            # 3100 USD * 25450 = 78,895,000 VND
            assert case_doc.total_actual_cost_vnd == 78895000.0, f"Chi phí thực tế kỳ vọng 78,895,000, thực tế {case_doc.total_actual_cost_vnd}"
            assert case_doc.cost_variance_vnd < 0
            assert case_doc.cost_variance_pct < 0

            self.record_pass("TC5 - Tổng hợp Chi phí Con lên Hồ sơ Mẹ", f"Tổng hợp chính xác: Chi phí thực tế {case_doc.total_actual_cost_vnd:,.0f} VND từ các chuyến tàu con")
        except Exception as e:
            self.record_fail("TC5 - Tổng hợp Chi phí Con lên Hồ sơ Mẹ", str(e))

    def test_case_6_customs_declaration_vnaccs_validation(self):
        """TC6: Kiểm tra xác thực tính hợp lệ của Số Tờ khai Hải quan điện tử VNACCS (chuẩn 11 chữ số)"""
        try:
            # 1. Thử số tờ khai không đúng 11 chữ số -> Phải bị chặn
            invalid_doc = frappe.get_doc({
                "doctype": "Customs Declaration",
                "declaration_no": "123456",
                "declaration_date": today(),
                "customs_office": "Chi cục Hải quan Cát Lái (02CI)",
                "customs_channel": "Luồng Xanh (Green)"
            })
            blocked = False
            try:
                invalid_doc.insert(ignore_permissions=True)
            except Exception:
                blocked = True

            assert blocked, "Hệ thống không chặn số tờ khai VNACCS sai quy chuẩn độ dài!"

            # 2. Nhập chuẩn 11 chữ số -> Thành công
            dec_no = f"1058249{self.run_suffix}0"
            if len(dec_no) < 11:
                dec_no = dec_no.ljust(11, "0")
            elif len(dec_no) > 11:
                dec_no = dec_no[:11]

            frappe.db.delete("Customs Declaration", {"declaration_no": dec_no})

            valid_doc = frappe.get_doc({
                "doctype": "Customs Declaration",
                "declaration_no": dec_no,
                "declaration_date": today(),
                "customs_office": "Chi cục Hải quan Cửa khẩu Cảng Sài Gòn KV1 (02CI)",
                "customs_channel": "Luồng Xanh (Green)",
                "trade_case": self.test_case_name,
                "trade_shipment": self.test_shipment_name,
                "clearance_status": "Draft"
            })
            valid_doc.insert(ignore_permissions=True)
            assert valid_doc.declaration_no == dec_no

            self.record_pass("TC6 - Kiểm tra Số Tờ khai VNACCS", f"Đã chặn số sai và chấp thuận số 11 chữ số chuẩn quốc gia: {dec_no}")
        except Exception as e:
            self.record_fail("TC6 - Kiểm tra Số Tờ khai VNACCS", str(e))

    def test_case_7_auto_lookup_customs_exchange_rate(self):
        """TC7: Tự động tra cứu Tỷ giá tính thuế Hải quan theo tuần của Bộ Tài chính"""
        try:
            dec_no = f"1058249{self.run_suffix}1"
            if len(dec_no) < 11:
                dec_no = dec_no.ljust(11, "0")
            elif len(dec_no) > 11:
                dec_no = dec_no[:11]

            frappe.db.delete("Customs Declaration", {"declaration_no": dec_no})

            doc = frappe.get_doc({
                "doctype": "Customs Declaration",
                "declaration_no": dec_no,
                "declaration_date": "2026-10-02",
                "currency": "USD",
                "customs_office": "Chi cục HQ Cát Lái",
                "customs_channel": "Luồng Vàng (Yellow)"
            })
            doc.insert(ignore_permissions=True)

            # Tỷ giá tuần 2026-10-02 trong DB là 25,450 VND/USD
            assert doc.customs_exchange_rate == 25450.0, f"Kỳ vọng tỷ giá 25450, thực tế: {doc.customs_exchange_rate}"

            self.record_pass("TC7 - Tra cứu Tỷ giá Hải quan Tự động", f"Ngày 2026-10-02 tự động khớp tỷ giá tuần của BTC: {doc.customs_exchange_rate:,.0f} VND/USD")
        except Exception as e:
            self.record_fail("TC7 - Tra cứu Tỷ giá Hải quan Tự động", str(e))

    def test_case_8_customs_duty_and_vat_tax_math(self):
        """TC8: Thuật toán tính Trị giá tính thuế Hải quan, Thuế Nhập khẩu và Thuế GTGT (VAT)"""
        try:
            dec_no = f"1058249{self.run_suffix}2"
            if len(dec_no) < 11:
                dec_no = dec_no.ljust(11, "0")
            elif len(dec_no) > 11:
                dec_no = dec_no[:11]

            frappe.db.delete("Customs Declaration", {"declaration_no": dec_no})

            doc = frappe.get_doc({
                "doctype": "Customs Declaration",
                "declaration_no": dec_no,
                "declaration_date": "2026-10-02",
                "currency": "USD",
                "customs_office": "Chi cục Hải quan Tân Sơn Nhất",
                "customs_channel": "Luồng Xanh (Green)",
                "items": [
                    {
                        "hs_code": "8517.13.00",
                        "item_name": "Điện thoại thông minh iPhone 16 Pro Max 256GB",
                        "qty": 100.0,
                        "unit_price": 1000.0,
                        "import_duty_rate": 0.0,
                        "vat_rate": 10.0
                    }
                ]
            })
            doc.insert(ignore_permissions=True)

            item = doc.items[0]
            assert item.customs_value_vnd == 2545000000.0, f"Trị giá tính thuế dòng sai: {item.customs_value_vnd}"
            assert item.import_duty_amount == 0.0, f"Thuế NK sai: {item.import_duty_amount}"
            assert item.vat_amount == 254500000.0, f"Thuế VAT sai: {item.vat_amount}"
            assert item.total_tax == 254500000.0, f"Tổng thuế dòng sai: {item.total_tax}"

            # Header totals
            assert doc.total_customs_value_vnd == 2545000000.0
            assert doc.total_import_duty_vnd == 0.0
            assert doc.total_vat_vnd == 254500000.0
            assert doc.total_tax_vnd == 254500000.0

            self.record_pass("TC8 - Thuật toán Tính Thuế Hải quan", "Trị giá 2,545,000,000 VND, Thuế NK (0%): 0 VND, Thuế GTGT (10%): 254,500,000 VND chuẩn xác 100%")
        except Exception as e:
            self.record_fail("TC8 - Thuật toán Tính Thuế Hải quan", str(e))

    def test_case_9_customs_clearance_sync_to_shipment_milestones(self):
        """TC9: Tự động cập nhật số Tờ khai và mốc thông quan M07 sang Chuyến hàng Trade Shipment"""
        try:
            assert self.test_shipment_name, "Cần test_shipment_name từ TC4"

            dec_no = f"1058249{self.run_suffix}3"
            if len(dec_no) < 11:
                dec_no = dec_no.ljust(11, "0")
            elif len(dec_no) > 11:
                dec_no = dec_no[:11]

            frappe.db.delete("Customs Declaration", {"declaration_no": dec_no})

            doc = frappe.get_doc({
                "doctype": "Customs Declaration",
                "declaration_no": dec_no,
                "declaration_date": today(),
                "currency": "USD",
                "customs_office": "Chi cục HQ Cát Lái",
                "customs_channel": "Luồng Xanh (Green)",
                "trade_shipment": self.test_shipment_name,
                "clearance_status": "Cleared",
                "clearance_date": today()
            })
            doc.insert(ignore_permissions=True)

            # Kiểm tra shipment được đồng bộ
            shipment = frappe.get_doc("Trade Shipment", self.test_shipment_name)
            assert shipment.customs_declaration_no == dec_no, f"Số tờ khai trên shipment không khớp: {shipment.customs_declaration_no}"

            m07 = next((m for m in shipment.milestones if m.milestone_code == "M07_CUSTOMS_CLEAR"), None)
            assert m07 and m07.status == "Completed", "Mốc M07 chưa được chuyển thành Completed"

            self.record_pass("TC9 - Đồng bộ Thông quan sang Lô hàng", f"Số tờ khai {dec_no} và mốc M07_CUSTOMS_CLEAR đã tự động cập nhật Completed trên {shipment.name}")
        except Exception as e:
            self.record_fail("TC9 - Đồng bộ Thông quan sang Lô hàng", str(e))

    def test_case_10_import_permit_validity_check(self):
        """TC10: Quản trị Giấy phép chuyên ngành (Import Permit) và cơ chế cảnh báo hết hạn"""
        try:
            p_active = f"GP-MIC-{self.run_suffix}-01"
            p_expired = f"GP-MIC-{self.run_suffix}-99"

            frappe.db.delete("Import Permit", {"permit_number": ["in", [p_active, p_expired]]})

            active_permit = frappe.get_doc({
                "doctype": "Import Permit",
                "permit_number": p_active,
                "permit_name": "Giấy phép Nhập khẩu Thiết bị Vô tuyến Viễn thông (Cục Viễn thông)",
                "issuing_authority": "Bộ Thông tin và Truyền thông",
                "trade_case": self.test_case_name,
                "status": "Granted",
                "issue_date": "2026-01-01",
                "valid_until": "2026-12-31",
                "hs_code": "8517.13.00"
            })
            active_permit.insert(ignore_permissions=True)
            assert active_permit.status == "Granted"

            expired_permit = frappe.get_doc({
                "doctype": "Import Permit",
                "permit_number": p_expired,
                "permit_name": "Chứng thư Hợp quy Lô cũ hết hạn",
                "issuing_authority": "Cục Viễn thông",
                "trade_case": self.test_case_name,
                "status": "Granted",
                "issue_date": "2025-01-01",
                "valid_until": "2025-06-30",
                "hs_code": "8517.13.00"
            })
            expired_permit.insert(ignore_permissions=True)
            assert expired_permit.status == "Expired", f"Kỳ vọng Expired, thực tế: {expired_permit.status}"

            self.record_pass("TC10 - Kiểm soát Giấy phép Chuyên ngành", f"Giấy phép {active_permit.permit_number} hợp lệ (Granted) và {expired_permit.permit_number} quá hạn tự chuyển Expired")
        except Exception as e:
            self.record_fail("TC10 - Kiểm soát Giấy phép Chuyên ngành", str(e))

def run_tests():
    runner = Phase3TestRunner()
    return runner.run_all()
