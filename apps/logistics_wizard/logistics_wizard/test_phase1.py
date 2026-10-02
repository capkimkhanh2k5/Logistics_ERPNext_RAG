# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days
from logistics_wizard.doctype.customs_exchange_rate.customs_exchange_rate import get_customs_rate

class Phase1TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

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
        print(" BẮT ĐẦU CHẠY BỘ KIỂM THỬ GIAI ĐOẠN 1 (PHASE 1 TEST SUITE)")
        print("=======================================================\n")

        self.test_case_1_seed_data_integrity()
        self.test_case_2_valuation_criterion_validation()
        self.test_case_3_penalty_not_in_valuation()
        self.test_case_4_invalid_hs_code()
        self.test_case_5_tax_rate_bounds()
        self.test_case_6_permit_missing_ministry()
        self.test_case_7_duplicate_fta()
        self.test_case_8_customs_rate_invalid_dates()
        self.test_case_9_customs_rate_overlapping()
        self.test_case_10_customs_rate_api_lookup()

        print("\n=======================================================")
        print(f" KẾT QUẢ KIỂM THỬ: {self.passed} ĐẠT / {self.passed + self.failed} TRƯỜNG HỢP")
        print("=======================================================\n")
        return self.failed == 0

    def test_case_1_seed_data_integrity(self):
        """TC1: Kiểm tra tính đầy đủ và toàn vẹn của Dữ liệu Nền tảng (Seed Data)"""
        try:
            charge_count = frappe.db.count("Charge Type")
            assert charge_count >= 10, f"Kỳ vọng >= 10 loại phí, thực tế: {charge_count}"

            hs_doc = frappe.get_doc("HS Tariff Rate", "8517.13.00")
            assert hs_doc.requires_import_permit == 1, "Mã 8517.13.00 phải có cờ yêu cầu giấy phép"
            assert len(hs_doc.preferential_rates) >= 4, "Mã 8517.13.00 phải có ít nhất 4 hiệp định FTA"

            usd_rate = frappe.db.get_value("Customs Exchange Rate", {"currency": "USD"}, "exchange_rate")
            assert usd_rate and usd_rate > 20000, f"Tỷ giá USD không hợp lệ: {usd_rate}"

            self.record_pass("TC1 - Dữ liệu Nền tảng Seed Data", f"Đủ 10 loại phí, mã HS iPhone và tỷ giá USD = {usd_rate:,.0f} VND")
        except Exception as e:
            self.record_fail("TC1 - Dữ liệu Nền tảng Seed Data", str(e))

    def test_case_2_valuation_criterion_validation(self):
        """TC2: Bắt lỗi nếu tính vào giá vốn nhưng không chọn tiêu chí phân bổ"""
        try:
            doc = frappe.get_doc({
                "doctype": "Charge Type",
                "charge_name": "Phí Test Lỗi Phân Bổ",
                "cost_category": "Vận chuyển quốc tế (International Freight)",
                "include_in_valuation": 1,
                "allocation_criterion": "Không phân bổ (None / Expense)"
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC2 - Chặn Tính giá vốn không có tiêu chí phân bổ", "Hệ thống không chặn lỗi!")
            except frappe.ValidationError:
                self.record_pass("TC2 - Chặn Tính giá vốn không có tiêu chí phân bổ", "Đã chặn thành công theo đúng chuẩn kế toán.")
        except Exception as e:
            self.record_fail("TC2 - Chặn Tính giá vốn không có tiêu chí phân bổ", str(e))

    def test_case_3_penalty_not_in_valuation(self):
        """TC3: Chặn hạch toán phí phạt lưu cont/bãi vào giá vốn hàng tồn kho (VAS 02 / IAS 2)"""
        try:
            doc = frappe.get_doc({
                "doctype": "Charge Type",
                "charge_name": "Phí Test Phạt Cấm Vào Giá Vốn",
                "cost_category": "Phí phạt & Lưu bãi quá hạn (Demurrage & Detention Penalties)",
                "include_in_valuation": 1,
                "allocation_criterion": "Theo Giá trị hàng (Value)"
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC3 - Chặn Phí phạt vốn hóa vào hàng tồn kho", "Hệ thống không chặn phí phạt!")
            except frappe.ValidationError:
                self.record_pass("TC3 - Chặn Phí phạt vốn hóa vào hàng tồn kho", "Đã chặn đúng chuẩn VAS 02 / IAS 2.")
        except Exception as e:
            self.record_fail("TC3 - Chặn Phí phạt vốn hóa vào hàng tồn kho", str(e))

    def test_case_4_invalid_hs_code(self):
        """TC4: Chặn mã HS không đủ 8 đến 10 chữ số"""
        try:
            doc = frappe.get_doc({
                "doctype": "HS Tariff Rate",
                "hs_code": "8517", # Chỉ có 4 số -> Không hợp lệ
                "description": "Mã HS Thiếu Số Test"
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC4 - Chặn Mã HS sai định dạng", "Hệ thống không chặn mã HS 4 số!")
            except frappe.ValidationError:
                self.record_pass("TC4 - Chặn Mã HS sai định dạng", "Đã chặn mã ngắn < 8 chữ số thành công.")
        except Exception as e:
            self.record_fail("TC4 - Chặn Mã HS sai định dạng", str(e))

    def test_case_5_tax_rate_bounds(self):
        """TC5: Chặn thuế suất vượt quá 100% hoặc nhỏ hơn 0%"""
        try:
            doc = frappe.get_doc({
                "doctype": "HS Tariff Rate",
                "hs_code": "9999.99.99",
                "description": "Hàng Test Thuế Bất Thường",
                "vat_rate": 150.0 # Vượt 100%
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC5 - Chặn Thuế suất vượt biên độ", "Hệ thống cho phép thuế suất 150%!")
            except frappe.ValidationError:
                self.record_pass("TC5 - Chặn Thuế suất vượt biên độ", "Đã chặn thuế suất vượt 100% thành công.")
        except Exception as e:
            self.record_fail("TC5 - Chặn Thuế suất vượt biên độ", str(e))

    def test_case_6_permit_missing_ministry(self):
        """TC6: Chặn hàng yêu cầu giấy phép nhưng không chỉ định Bộ quản lý chuyên ngành"""
        try:
            doc = frappe.get_doc({
                "doctype": "HS Tariff Rate",
                "hs_code": "8888.88.88",
                "description": "Hàng KCS Test",
                "requires_import_permit": 1,
                "managing_ministry": "" # Để trống Bộ
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC6 - Bắt buộc khai báo Bộ quản lý chuyên ngành", "Hệ thống cho phép để trống Bộ!")
            except frappe.ValidationError:
                self.record_pass("TC6 - Bắt buộc khai báo Bộ quản lý chuyên ngành", "Đã kiểm tra ràng buộc pháp lý thành công.")
        except Exception as e:
            self.record_fail("TC6 - Bắt buộc khai báo Bộ quản lý chuyên ngành", str(e))

    def test_case_7_duplicate_fta(self):
        """TC7: Chặn khai báo trùng lặp cùng một hiệp định thương mại FTA trong cùng 1 mã HS"""
        try:
            doc = frappe.get_doc({
                "doctype": "HS Tariff Rate",
                "hs_code": "7777.77.77",
                "description": "Hàng Test Trùng FTA",
                "preferential_rates": [
                    {"trade_agreement": "Form E (ACFTA - Trung Quốc - ASEAN)", "preferential_duty_rate": 0.0},
                    {"trade_agreement": "Form E (ACFTA - Trung Quốc - ASEAN)", "preferential_duty_rate": 5.0}
                ]
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC7 - Chặn Trùng lặp Hiệp định FTA", "Hệ thống cho phép 2 dòng cùng 1 hiệp định!")
            except frappe.ValidationError:
                self.record_pass("TC7 - Chặn Trùng lặp Hiệp định FTA", "Đã chặn trùng lặp dòng Form E thành công.")
        except Exception as e:
            self.record_fail("TC7 - Chặn Trùng lặp Hiệp định FTA", str(e))

    def test_case_8_customs_rate_invalid_dates(self):
        """TC8: Chặn ngày hiệu lực bắt đầu lớn hơn ngày kết thúc"""
        try:
            doc = frappe.get_doc({
                "doctype": "Customs Exchange Rate",
                "currency": "USD",
                "exchange_rate": 25500.0,
                "valid_from": "2026-10-20",
                "valid_to": "2026-10-10" # Ngày kết thúc trước ngày bắt đầu!
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC8 - Chặn Ngày hiệu lực tỷ giá đảo ngược", "Hệ thống cho phép ngày bắt đầu > kết thúc!")
            except frappe.ValidationError:
                self.record_pass("TC8 - Chặn Ngày hiệu lực tỷ giá đảo ngược", "Đã chặn khoảng ngày không hợp lệ.")
        except Exception as e:
            self.record_fail("TC8 - Chặn Ngày hiệu lực tỷ giá đảo ngược", str(e))

    def test_case_9_customs_rate_overlapping(self):
        """TC9: Chặn khai báo tỷ giá bị chồng lấn (overlapping) thời gian với bản ghi có sẵn"""
        try:
            curr_today = today()
            doc = frappe.get_doc({
                "doctype": "Customs Exchange Rate",
                "currency": "USD",
                "exchange_rate": 25600.0,
                "valid_from": add_days(curr_today, 2), # Bắt đầu sau 2 ngày (Trùng trong khoảng tuần hiện tại)
                "valid_to": add_days(curr_today, 8)
            })
            try:
                doc.insert(ignore_permissions=True)
                self.record_fail("TC9 - Chặn Chồng lấn thời gian Tỷ giá", "Hệ thống cho phép trùng khoảng thời gian!")
            except frappe.ValidationError:
                self.record_pass("TC9 - Chặn Chồng lấn thời gian Tỷ giá", "Đã chặn bản ghi tỷ giá bị trùng tuần.")
        except Exception as e:
            self.record_fail("TC9 - Chặn Chồng lấn thời gian Tỷ giá", str(e))

    def test_case_10_customs_rate_api_lookup(self):
        """TC10: Kiểm thử hàm API tra cứu tỷ giá có hiệu lực tại thời điểm khai báo"""
        try:
            usd_rate = get_customs_rate("USD")
            assert usd_rate == 25450.0, f"Tỷ giá USD tra cứu kỳ vọng 25,450, nhận được: {usd_rate}"

            gbp_rate = get_customs_rate("GBP")
            assert gbp_rate is None, f"Đồng GBP chưa khai báo phải trả về None, nhận được: {gbp_rate}"

            self.record_pass("TC10 - API Tra cứu Tỷ giá Hiệu lực", f"USD trả về {usd_rate:,.0f} VND chuẩn xác; GBP trả về None")
        except Exception as e:
            self.record_fail("TC10 - API Tra cứu Tỷ giá Hiệu lực", str(e))

def run_tests():
    runner = Phase1TestRunner()
    return runner.run_all()
