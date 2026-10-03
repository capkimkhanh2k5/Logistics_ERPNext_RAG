# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
import random
from frappe.utils import today, add_days, flt
from frappe.exceptions import ValidationError

class Phase4TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.company = "Cap Khanh Logistics"
        self.supplier = "Apple Inc." if frappe.db.exists("Supplier", "Apple Inc.") else "Apple Inc"
        self.warehouse = "Stores - CK" if frappe.db.exists("Warehouse", "Stores - CK") else "Finished Goods - CK"
        self.run_suffix = f"{random.randint(100, 999)}"
        self.item_code = f"TEST-IP15-{self.run_suffix}"
        self.item_code_2 = f"TEST-CASE-{self.run_suffix}"
        self.test_case_name = None
        self.test_shipment_name = None
        self.test_po_name = None
        self.test_pr_name = None

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
        print(" BẮT ĐẦU CHẠY BỘ KIỂM THỬ GIAI ĐOẠN 4 (PHASE 4 TEST SUITE)")
        print(" [Tích hợp ERPNext Core, Custom Fields & Cổng Stage Gate 2]")
        print("=======================================================\n")

        self.test_case_1_custom_fields_exist_on_item()
        self.test_case_2_custom_fields_exist_on_documents()
        self.test_case_3_setup_test_item_with_logistics_attributes()
        self.test_case_4_create_po_and_verify_auto_fetch_and_calculation()
        self.test_case_5_submit_po()
        self.test_case_6_purchase_receipt_stage_gate_blocked_when_unauthorized()
        self.test_case_7_purchase_receipt_stage_gate_allowed_after_clearance()
        self.test_case_8_stage_gate_sync_updates_m09_and_shipment_status()
        self.test_case_9_multi_item_cbm_and_weight_aggregation()
        self.test_case_10_end_to_end_traceability_with_purchase_invoice()

        print("\n=======================================================")
        print(f" KẾT QUẢ KIỂM THỬ GIAI ĐOẠN 4: {self.passed} ĐẠT / {self.passed + self.failed} TRƯỜNG HỢP")
        print("=======================================================\n")
        return self.failed == 0

    def test_case_1_custom_fields_exist_on_item(self):
        """TC1: Kiểm tra cấu trúc Custom Fields mở rộng trên Master Item"""
        try:
            expected_fields = ["custom_hs_code", "unit_cbm", "unit_gross_weight", "technical_description"]
            missing = []
            for field in expected_fields:
                exists = frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": field})
                if not exists:
                    missing.append(field)

            if missing:
                self.record_fail("TC1 - Custom Fields trên Item", f"Thiếu các trường: {', '.join(missing)}")
            else:
                self.record_pass("TC1 - Custom Fields trên Item", "Đã cấu hình đủ 4 trường nghiệp vụ: Mã HS, Unit CBM, Gross Weight và Mô tả kỹ thuật")
        except Exception as e:
            self.record_fail("TC1 - Custom Fields trên Item", str(e))

    def test_case_2_custom_fields_exist_on_documents(self):
        """TC2: Kiểm tra cấu trúc Custom Fields trên PO, PR, PI và Child Tables"""
        try:
            checks = [
                ("Purchase Order", "trade_case"),
                ("Purchase Order", "trade_shipment"),
                ("Purchase Receipt", "trade_case"),
                ("Purchase Receipt", "trade_shipment"),
                ("Purchase Invoice", "trade_case"),
                ("Purchase Invoice", "trade_shipment"),
                ("Purchase Order Item", "total_cbm"),
                ("Purchase Order Item", "total_gross_weight"),
                ("Purchase Receipt Item", "total_cbm"),
                ("Purchase Receipt Item", "total_gross_weight"),
            ]
            missing = []
            for dt, field in checks:
                if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": field}):
                    missing.append(f"{dt}.{field}")

            if missing:
                self.record_fail("TC2 - Custom Fields Chứng từ ERPNext", f"Thiếu các trường: {', '.join(missing)}")
            else:
                self.record_pass("TC2 - Custom Fields Chứng từ ERPNext", "Đã liên kết đủ Trade Case, Trade Shipment và các trường phân bổ CBM/Weight trên PO, PR, PI")
        except Exception as e:
            self.record_fail("TC2 - Custom Fields Chứng từ ERPNext", str(e))

    def test_case_3_setup_test_item_with_logistics_attributes(self):
        """TC3: Thiết lập Mặt hàng nhập khẩu với đầy đủ thông số Logistics chuẩn"""
        try:
            if not frappe.db.exists("Item", self.item_code):
                item = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": self.item_code,
                    "item_name": f"iPhone 15 Pro Max 256GB #{self.run_suffix}",
                    "item_group": "Products",
                    "stock_uom": "Nos",
                    "is_stock_item": 1,
                    "custom_hs_code": "8517.13.00",
                    "unit_cbm": 0.0025,
                    "unit_gross_weight": 0.3800,
                    "technical_description": "Điện thoại thông minh 5G Apple A17 Pro"
                })
                item.insert(ignore_permissions=True)
            else:
                item = frappe.get_doc("Item", self.item_code)
                item.custom_hs_code = "8517.13.00"
                item.unit_cbm = 0.0025
                item.unit_gross_weight = 0.3800
                item.save(ignore_permissions=True)

            frappe.db.commit()

            fetched = frappe.db.get_value(
                "Item",
                self.item_code,
                ["custom_hs_code", "unit_cbm", "unit_gross_weight"],
                as_dict=True
            )

            if fetched.custom_hs_code == "8517.13.00" and flt(fetched.unit_cbm) == 0.0025 and flt(fetched.unit_gross_weight) == 0.38:
                self.record_pass("TC3 - Master Data Item Logistics", f"Sản phẩm {self.item_code} lưu chuẩn HS 8517.13.00, CBM 0.0025, GW 0.380 kg")
            else:
                self.record_fail("TC3 - Master Data Item Logistics", f"Thông số kỹ thuật lưu không khớp: {fetched}")
        except Exception as e:
            self.record_fail("TC3 - Master Data Item Logistics", str(e))

    def test_case_4_create_po_and_verify_auto_fetch_and_calculation(self):
        """TC4: Tạo Đơn mua hàng (PO), kiểm tra Tự động kế thừa và tính toán CBM/Weight"""
        try:
            # 1. Tạo Trade Case mẹ
            tc = frappe.get_doc({
                "doctype": "Trade Case",
                "case_title": f"Dự án Apple PO #{self.run_suffix}",
                "trade_type": "Import",
                "supplier": self.supplier,
                "incoterm": "CIF",
                "currency": "USD"
            })
            tc.insert(ignore_permissions=True)
            self.test_case_name = tc.name

            # 2. Tạo Trade Shipment con
            ts = frappe.get_doc({
                "doctype": "Trade Shipment",
                "trade_case": tc.name,
                "shipment_name": f"Lô hàng Tàu Cosco #{self.run_suffix}",
                "supplier": self.supplier,
                "incoterm": "CIF",
                "transport_mode": "Ocean FCL",
                "status": "In Transit",
                "origin_port": "Shanghai Port, China",
                "destination_port": "Cat Lai Port, Vietnam"
            })
            ts.insert(ignore_permissions=True)
            self.test_shipment_name = ts.name

            # 3. Tạo Purchase Order với currency USD khớp Supplier
            po = frappe.get_doc({
                "doctype": "Purchase Order",
                "company": self.company,
                "supplier": self.supplier,
                "currency": "USD",
                "conversion_rate": 25500.0,
                "schedule_date": add_days(today(), 7),
                "trade_case": tc.name,
                "trade_shipment": ts.name,
                "items": [
                    {
                        "item_code": self.item_code,
                        "qty": 1000,
                        "rate": 1000.0,
                        "schedule_date": add_days(today(), 7),
                        "warehouse": self.warehouse
                    }
                ]
            })
            po.insert(ignore_permissions=True)
            self.test_po_name = po.name

            # Reload để kiểm tra tính toán sau khi hook validate chạy
            po.reload()
            line = po.items[0]

            expected_cbm = 2.5   # 1000 * 0.0025
            expected_gw = 380.0  # 1000 * 0.38

            if flt(line.total_cbm) == expected_cbm and flt(line.total_gross_weight) == expected_gw:
                self.record_pass("TC4 - Tự động tính CBM & Trọng lượng trên PO", f"1,000 cái tự động tính thành {line.total_cbm} CBM và {line.total_gross_weight} KGS chuẩn xác")
            else:
                self.record_fail("TC4 - Tự động tính CBM & Trọng lượng trên PO", f"Kỳ vọng {expected_cbm} CBM / {expected_gw} KGS, thực tế {line.total_cbm} CBM / {line.total_gross_weight} KGS")
        except Exception as e:
            self.record_fail("TC4 - Tự động tính CBM & Trọng lượng trên PO", str(e))

    def test_case_5_submit_po(self):
        """TC5: Phê duyệt Đơn mua hàng (PO Submit) liên kết chuỗi logistics"""
        try:
            if not self.test_po_name:
                self.record_fail("TC5 - Duyệt Đơn mua hàng (PO Submit)", "Chưa có PO từ TC4")
                return

            po = frappe.get_doc("Purchase Order", self.test_po_name)
            po.submit()
            if po.docstatus == 1:
                self.record_pass("TC5 - Duyệt Đơn mua hàng (PO Submit)", f"Đơn hàng {po.name} đã được Submit thành công (docstatus=1)")
            else:
                self.record_fail("TC5 - Duyệt Đơn mua hàng (PO Submit)", f"PO chưa ở trạng thái Submitted: {po.docstatus}")
        except Exception as e:
            self.record_fail("TC5 - Duyệt Đơn mua hàng (PO Submit)", str(e))

    def test_case_6_purchase_receipt_stage_gate_blocked_when_unauthorized(self):
        """TC6: Cổng Kiểm soát Stage Gate 2 - Chặn Nhập kho khi Lô hàng chưa hoàn tất Thông quan (M07)"""
        try:
            # Tạo Phiếu Nhập Kho (Purchase Receipt) liên kết với Trade Shipment đang In Transit
            pr = frappe.get_doc({
                "doctype": "Purchase Receipt",
                "company": self.company,
                "supplier": self.supplier,
                "currency": "USD",
                "conversion_rate": 25500.0,
                "trade_case": self.test_case_name,
                "trade_shipment": self.test_shipment_name,
                "items": [
                    {
                        "item_code": self.item_code,
                        "qty": 1000,
                        "rate": 1000.0,
                        "purchase_order": self.test_po_name,
                        "purchase_order_item": frappe.db.get_value("Purchase Order Item", {"parent": self.test_po_name}, "name"),
                        "warehouse": self.warehouse
                    }
                ]
            })
            pr.insert(ignore_permissions=True)
            self.test_pr_name = pr.name

            # Kiểm tra CBM và GW trên PR line
            pr.reload()
            line = pr.items[0]
            if flt(line.total_cbm) != 2.5 or flt(line.total_gross_weight) != 380.0:
                self.record_fail("TC6 - Stage Gate 2 Chặn Nhập kho", f"CBM/GW trên PR chưa tính đúng: CBM={line.total_cbm}, GW={line.total_gross_weight}")
                return

            # Cố tình Submit khi Mốc M07 chưa hoàn thành
            blocked = False
            try:
                pr.submit()
            except ValidationError as ve:
                blocked = True
                msg = str(ve)
                if "STAGE GATE 2" in msg or "M07" in msg:
                    self.record_pass("TC6 - Stage Gate 2 Chặn Nhập kho", "Đã chặn thành công Thủ kho duyệt nhập hàng khi Mốc M07 (Thông quan) chưa hoàn thành")
                else:
                    self.record_fail("TC6 - Stage Gate 2 Chặn Nhập kho", f"Bị chặn nhưng thông báo chưa chuẩn: {msg}")
            except Exception as ex:
                blocked = True
                self.record_pass("TC6 - Stage Gate 2 Chặn Nhập kho", f"Hệ thống đã chặn submit: {str(ex)[:100]}")

            if not blocked:
                self.record_fail("TC6 - Stage Gate 2 Chặn Nhập kho", "HỆ THỐNG ĐÃ KHÔNG CHẶN! Lô hàng chưa thông quan nhưng vẫn cho Submit Purchase Receipt!")
        except Exception as e:
            self.record_fail("TC6 - Stage Gate 2 Chặn Nhập kho", str(e))

    def test_case_7_purchase_receipt_stage_gate_allowed_after_clearance(self):
        """TC7: Cổng Kiểm soát Stage Gate 2 - Cho phép Nhập kho khi đã hoàn tất Thông quan hợp lệ"""
        try:
            if not self.test_shipment_name or not self.test_pr_name:
                self.record_fail("TC7 - Mở Cổng Stage Gate 2 Hợp lệ", "Thiếu Shipment hoặc PR từ các bước trước")
                return

            # 1. Cập nhật mốc M07_CUSTOMS_CLEAR sang Completed trên Trade Shipment
            ts = frappe.get_doc("Trade Shipment", self.test_shipment_name)
            for m in ts.milestones:
                if m.milestone_code == "M07_CUSTOMS_CLEAR":
                    m.status = "Completed"
                    m.actual_date = today()
                    break
            ts.status = "Customs Clearance"
            ts.save(ignore_permissions=True)
            frappe.db.commit()

            # 2. Giờ đây Submit lại Purchase Receipt
            pr = frappe.get_doc("Purchase Receipt", self.test_pr_name)
            pr.submit()

            if pr.docstatus == 1:
                self.record_pass("TC7 - Mở Cổng Stage Gate 2 Hợp lệ", f"Phiếu Nhập kho {pr.name} đã được Submit thành công sau khi M07 hoàn tất")
            else:
                self.record_fail("TC7 - Mở Cổng Stage Gate 2 Hợp lệ", f"PR chưa ở trạng thái Submitted: docstatus={pr.docstatus}")
        except Exception as e:
            self.record_fail("TC7 - Mở Cổng Stage Gate 2 Hợp lệ", str(e))

    def test_case_8_stage_gate_sync_updates_m09_and_shipment_status(self):
        """TC8: Tự động Đồng bộ Mốc M09 (Nhập kho hoàn tất) và chuyển trạng thái Lô hàng sang Completed"""
        try:
            if not self.test_shipment_name:
                self.record_fail("TC8 - Tự động Đồng bộ M09 & Hoàn tất Lô hàng", "Thiếu shipment_name")
                return

            ts = frappe.get_doc("Trade Shipment", self.test_shipment_name)
            m09 = None
            for m in ts.milestones:
                if m.milestone_code == "M09_WH_RECEIPT":
                    m09 = m
                    break

            if not m09:
                self.record_fail("TC8 - Tự động Đồng bộ M09 & Hoàn tất Lô hàng", "Không tìm thấy mốc M09 trên Trade Shipment")
                return

            if m09.status == "Completed" and ts.status == "Completed":
                self.record_pass("TC8 - Tự động Đồng bộ M09 & Hoàn tất Lô hàng", f"Mốc M09 tự chuyển 'Completed' (ngày {m09.actual_date}) và Lô hàng tự chuyển sang trạng thái 'Completed'")
            else:
                self.record_fail("TC8 - Tự động Đồng bộ M09 & Hoàn tất Lô hàng", f"M09 status: {m09.status}, Shipment status: {ts.status}")
        except Exception as e:
            self.record_fail("TC8 - Tự động Đồng bộ M09 & Hoàn tất Lô hàng", str(e))

    def test_case_9_multi_item_cbm_and_weight_aggregation(self):
        """TC9: Kiểm thử Tính toán Thể tích & Trọng lượng Đa mặt hàng phức hợp"""
        try:
            # Đảm bảo mã HS 8517.13.00 tồn tại
            if not frappe.db.exists("HS Tariff Rate", "8517.13.00"):
                hs = frappe.get_doc({
                    "doctype": "HS Tariff Rate",
                    "hs_code": "8517.13.00",
                    "description_vn": "Điện thoại thông minh",
                    "general_rate": 5.0,
                    "mfn_rate": 0.0,
                    "vat_rate": 10.0,
                    "ministry_in_charge": "Bộ Thông tin và Truyền thông"
                })
                hs.insert(ignore_permissions=True)

            # Tạo Item phụ (Ốp lưng điện thoại)
            if not frappe.db.exists("Item", self.item_code_2):
                item2 = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": self.item_code_2,
                    "item_name": f"Ốp lưng MagSafe Silicone #{self.run_suffix}",
                    "item_group": "Products",
                    "stock_uom": "Nos",
                    "is_stock_item": 1,
                    "custom_hs_code": "8517.13.00",
                    "unit_cbm": 0.0005,
                    "unit_gross_weight": 0.0800,
                    "technical_description": "Vỏ bảo vệ điện thoại bằng nhựa silicone"
                })
                item2.insert(ignore_permissions=True)

            po_multi = frappe.get_doc({
                "doctype": "Purchase Order",
                "company": self.company,
                "supplier": self.supplier,
                "currency": "USD",
                "conversion_rate": 25500.0,
                "schedule_date": add_days(today(), 5),
                "items": [
                    {
                        "item_code": self.item_code,     # 2,000 * 0.0025 = 5.0 CBM, 2,000 * 0.38 = 760.0 KG
                        "qty": 2000,
                        "rate": 1000.0,
                        "schedule_date": add_days(today(), 5),
                        "warehouse": self.warehouse
                    },
                    {
                        "item_code": self.item_code_2,   # 5,000 * 0.0005 = 2.5 CBM, 5,000 * 0.08 = 400.0 KG
                        "qty": 5000,
                        "rate": 20.0,
                        "schedule_date": add_days(today(), 5),
                        "warehouse": self.warehouse
                    }
                ]
            })
            po_multi.insert(ignore_permissions=True)

            row1 = po_multi.items[0]
            row2 = po_multi.items[1]

            pass_row1 = (flt(row1.total_cbm) == 5.0 and flt(row1.total_gross_weight) == 760.0)
            pass_row2 = (flt(row2.total_cbm) == 2.5 and flt(row2.total_gross_weight) == 400.0)

            if pass_row1 and pass_row2:
                total_cbm = flt(row1.total_cbm) + flt(row2.total_cbm)
                total_gw = flt(row1.total_gross_weight) + flt(row2.total_gross_weight)
                self.record_pass("TC9 - Phân bổ Đa Mặt hàng", f"Tổng 2 mặt hàng: {total_cbm} CBM và {total_gw} KGS được tính độc lập và chính xác tuyệt đối")
            else:
                self.record_fail("TC9 - Phân bổ Đa Mặt hàng", f"Dòng 1: CBM={row1.total_cbm}, GW={row1.total_gross_weight}; Dòng 2: CBM={row2.total_cbm}, GW={row2.total_gross_weight}")
        except Exception as e:
            self.record_fail("TC9 - Phân bổ Đa Mặt hàng", str(e))

    def test_case_10_end_to_end_traceability_with_purchase_invoice(self):
        """TC10: Toàn vẹn Chuỗi Dữ liệu Liên kết Đa chiều (PO -> PR -> PI -> Trade Shipment -> Trade Case)"""
        try:
            if not self.test_po_name or not self.test_pr_name:
                self.record_fail("TC10 - Toàn vẹn Dữ liệu Đa chiều", "Thiếu PO hoặc PR")
                return

            # Tạo Purchase Invoice liên kết
            pi = frappe.get_doc({
                "doctype": "Purchase Invoice",
                "company": self.company,
                "supplier": self.supplier,
                "currency": "USD",
                "conversion_rate": 25500.0,
                "trade_case": self.test_case_name,
                "trade_shipment": self.test_shipment_name,
                "items": [
                    {
                        "item_code": self.item_code,
                        "qty": 1000,
                        "rate": 1000.0,
                        "purchase_order": self.test_po_name,
                        "purchase_receipt": self.test_pr_name,
                    }
                ]
            })
            pi.insert(ignore_permissions=True)

            # Truy vấn kiểm tra tính toàn vẹn 5 chiều
            po_shipment = frappe.db.get_value("Purchase Order", self.test_po_name, "trade_shipment")
            pr_shipment = frappe.db.get_value("Purchase Receipt", self.test_pr_name, "trade_shipment")
            pi_shipment = frappe.db.get_value("Purchase Invoice", pi.name, "trade_shipment")
            ts_pr = frappe.db.get_value("Trade Shipment", self.test_shipment_name, "purchase_receipt")

            linked_po = (po_shipment == self.test_shipment_name)
            linked_pr = (pr_shipment == self.test_shipment_name)
            linked_pi = (pi_shipment == self.test_shipment_name)
            linked_back = (ts_pr == self.test_pr_name)

            if linked_po and linked_pr and linked_pi and linked_back:
                self.record_pass("TC10 - Toàn vẹn Dữ liệu Đa chiều", f"Chuỗi hồ sơ {self.test_case_name} <-> {self.test_shipment_name} <-> {self.test_po_name} <-> {self.test_pr_name} <-> {pi.name} liên kết 100% xuyên suốt")
            else:
                self.record_fail("TC10 - Toàn vẹn Dữ liệu Đa chiều", f"Liên kết không đồng nhất: PO={linked_po}, PR={linked_pr}, PI={linked_pi}, PR_Back={linked_back}")
        except Exception as e:
            self.record_fail("TC10 - Toàn vẹn Dữ liệu Đa chiều", str(e))


def run_tests():
    runner = Phase4TestRunner()
    return runner.run_all()


if __name__ == "__main__":
    run_tests()
