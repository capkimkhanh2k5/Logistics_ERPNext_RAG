# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days

def seed_all():
    print("--- [BẮT ĐẦU NẠP DỮ LIỆU GIAI ĐOẠN 1] ---")
    seed_charge_types()
    seed_hs_tariff_rates()
    seed_customs_exchange_rates()
    frappe.db.commit()
    print("--- [HOÀN TẤT NẠP DỮ LIỆU GIAI ĐOẠN 1] ---")

def seed_charge_types():
    charges = [
        {
            "charge_name": "Cước biển quốc tế (Ocean Freight)",
            "charge_code": "OCF",
            "cost_category": "Vận chuyển quốc tế (International Freight)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 1,
            "allocation_criterion": "Theo Thể tích (CBM)",
            "description": "Chi phí cước vận tải biển quốc tế từ cảng đi về cảng đến. Phân bổ theo số khối CBM."
        },
        {
            "charge_name": "Phí nâng hạ cảng (THC - Terminal Handling Charge)",
            "charge_code": "THC",
            "cost_category": "Phí tại cảng (Port / Local Charges)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Khối lượng (Gross Weight)",
            "description": "Phí xếp dỡ container tại cầu cảng. Phân bổ theo trọng lượng Gross Weight."
        },
        {
            "charge_name": "Phí phát hành vận đơn (B/L Fee)",
            "charge_code": "BLF",
            "cost_category": "Phí tại cảng (Port / Local Charges)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Giá trị hàng (Value)",
            "description": "Phí chứng từ phát hành vận đơn đường biển của hãng tàu/forwarder."
        },
        {
            "charge_name": "Bảo hiểm hàng hải quốc tế (Marine Insurance)",
            "charge_code": "INS",
            "cost_category": "Bảo hiểm hàng hải (Marine Insurance)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 1,
            "allocation_criterion": "Theo Giá trị hàng (Value)",
            "description": "Bảo hiểm rủi ro hàng hóa trong quá trình vận chuyển quốc tế. Thuộc trị giá tính thuế HQ."
        },
        {
            "charge_name": "Thuế nhập khẩu (Import Duty)",
            "charge_code": "IDT",
            "cost_category": "Thuế & Lệ phí hải quan (Customs Duty & Tax)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Giá trị hàng (Value)",
            "description": "Thuế nhập khẩu theo tờ khai hải quan, được vốn hóa 100% vào giá trị hàng tồn kho."
        },
        {
            "charge_name": "Phí dịch vụ khai hải quan (Customs Brokerage)",
            "charge_code": "CCB",
            "cost_category": "Thủ tục hải quan & Kiểm tra chuyên ngành (Customs Brokerage & Inspection)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Giá trị hàng (Value)",
            "description": "Thù lao đại lý dịch vụ khai báo và làm thủ tục thông quan tại chi cục hải quan."
        },
        {
            "charge_name": "Phí kiểm tra chất lượng chuyên ngành / KCS",
            "charge_code": "QA_INSP",
            "cost_category": "Thủ tục hải quan & Kiểm tra chuyên ngành (Customs Brokerage & Inspection)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Giá trị hàng (Value)",
            "description": "Chi phí đo kiểm hợp quy, chứng nhận chất lượng của cơ quan kiểm định được chỉ định."
        },
        {
            "charge_name": "Cước vận tải nội địa kéo cont (Inland Trucking)",
            "charge_code": "TRK",
            "cost_category": "Vận chuyển nội địa (Inland Trucking)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Khối lượng (Gross Weight)",
            "description": "Chi phí xe đầu kéo vận chuyển container từ cảng Cát Lái về đến kho công ty."
        },
        {
            "charge_name": "Phí kho bãi và nâng hạ cont (CFS / Lift-on Lift-off)",
            "charge_code": "CFS_LOLO",
            "cost_category": "Kho bãi & Nâng hạ (Warehousing & Handling)",
            "include_in_valuation": 1,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Theo Thể tích (CBM)",
            "description": "Phí bến bãi, nâng vỏ container hạ tại bãi ICD và kho CFS."
        },
        {
            "charge_name": "Phí phạt lưu cont & lưu bãi quá hạn (Demurrage & Detention)",
            "charge_code": "DEM_DET",
            "cost_category": "Phí phạt & Lưu bãi quá hạn (Demurrage & Detention Penalties)",
            "include_in_valuation": 0,
            "include_in_customs_valuation": 0,
            "allocation_criterion": "Không phân bổ (None / Expense)",
            "description": "Khoản phạt phát sinh do vượt quá Free-time. Không được vốn hóa vào hàng tồn kho."
        }
    ]

    for item in charges:
        if not frappe.db.exists("Charge Type", item["charge_name"]):
            doc = frappe.get_doc({
                "doctype": "Charge Type",
                **item
            })
            doc.insert(ignore_permissions=True)
            print(f"  + Tạo loại phí: {item['charge_name']}")
        else:
            print(f"  * Loại phí đã tồn tại: {item['charge_name']}")

def seed_hs_tariff_rates():
    hs_data = [
        {
            "hs_code": "8517.13.00",
            "description": "Điện thoại thông minh (Smartphones - iPhone, iPad 5G...)",
            "general_duty_rate": 5.0,
            "mfn_duty_rate": 0.0,
            "vat_rate": 10.0,
            "requires_import_permit": 1,
            "managing_ministry": "Bộ Thông tin và Truyền thông (MIC)",
            "compliance_notes": "Bắt buộc thử nghiệm hợp quy QCVN 117:2020/BTTTT và QCVN 18:2014/BTTTT trước khi thông quan.",
            "preferential_rates": [
                {"trade_agreement": "Form E (ACFTA - Trung Quốc - ASEAN)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form E"},
                {"trade_agreement": "Form D (ATIGA - Nội khối ASEAN)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form D"},
                {"trade_agreement": "EUR.1 (EVFTA - Việt Nam - EU)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form EUR.1"},
                {"trade_agreement": "Form AK (AKFTA - Việt Nam - Hàn Quốc)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form AK"}
            ]
        },
        {
            "hs_code": "8471.30.20",
            "description": "Máy xử lý dữ liệu tự động số xách tay (Máy tính xách tay Laptop)",
            "general_duty_rate": 5.0,
            "mfn_duty_rate": 0.0,
            "vat_rate": 10.0,
            "requires_import_permit": 0,
            "compliance_notes": "Kiểm tra an toàn bức xạ điện từ và pin lithium theo tiêu chuẩn nhà sản xuất.",
            "preferential_rates": [
                {"trade_agreement": "Form E (ACFTA - Trung Quốc - ASEAN)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form E"},
                {"trade_agreement": "EUR.1 (EVFTA - Việt Nam - EU)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form EUR.1"}
            ]
        },
        {
            "hs_code": "8504.40.90",
            "description": "Bộ biến đổi tĩnh điện khác (Củ sạc, Adapter nguồn điện tử thoại)",
            "general_duty_rate": 10.0,
            "mfn_duty_rate": 5.0,
            "vat_rate": 10.0,
            "requires_import_permit": 1,
            "managing_ministry": "Bộ Khoa học và Công nghệ (MOST)",
            "compliance_notes": "Chứng nhận an toàn điện QCVN 4:2009/BKHCN và TCVN 11844:2017 về hiệu suất năng lượng.",
            "preferential_rates": [
                {"trade_agreement": "Form E (ACFTA - Trung Quốc - ASEAN)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form E"},
                {"trade_agreement": "Form D (ATIGA - Nội khối ASEAN)", "preferential_duty_rate": 0.0, "co_form_required": "C/O Form D"}
            ]
        }
    ]

    for item in hs_data:
        if not frappe.db.exists("HS Tariff Rate", item["hs_code"]):
            doc = frappe.get_doc({
                "doctype": "HS Tariff Rate",
                **item
            })
            doc.insert(ignore_permissions=True)
            print(f"  + Tạo biểu thuế HS: {item['hs_code']} - {item['description']}")
        else:
            print(f"  * Mã HS đã tồn tại: {item['hs_code']}")

def seed_customs_exchange_rates():
    curr_today = today()
    valid_end = add_days(curr_today, 6)

    fx_rates = [
        {"currency": "USD", "exchange_rate": 25450.0, "announcement_ref": "TB-TCHQ-2026/W40"},
        {"currency": "EUR", "exchange_rate": 27850.0, "announcement_ref": "TB-TCHQ-2026/W40"},
        {"currency": "CNY", "exchange_rate": 3580.0, "announcement_ref": "TB-TCHQ-2026/W40"},
        {"currency": "JPY", "exchange_rate": 172.5, "announcement_ref": "TB-TCHQ-2026/W40"}
    ]

    for fx in fx_rates:
        doc_name = f"{fx['currency']}-{curr_today}"
        if not frappe.db.exists("Customs Exchange Rate", doc_name):
            doc = frappe.get_doc({
                "doctype": "Customs Exchange Rate",
                "currency": fx["currency"],
                "exchange_rate": fx["exchange_rate"],
                "valid_from": curr_today,
                "valid_to": valid_end,
                "announcement_ref": fx["announcement_ref"],
                "notes": f"Tỷ giá tính thuế Hải quan áp dụng tuần hiện tại cho đồng {fx['currency']}"
            })
            doc.insert(ignore_permissions=True)
            print(f"  + Tạo tỷ giá hải quan: {fx['currency']} = {fx['exchange_rate']} VND")
        else:
            print(f"  * Tỷ giá hải quan đã tồn tại: {doc_name}")
