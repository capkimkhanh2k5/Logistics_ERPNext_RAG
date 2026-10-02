# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days

def seed_shipment():
    print("--- [BẮT ĐẦU NẠP DỮ LIỆU LÔ HÀNG GIAI ĐOẠN 2] ---")

    # 1. Đảm bảo có nhà cung cấp & Forwarder
    ensure_suppliers()

    # 2. Tạo Lô hàng chuẩn mẫu
    shipment_title = "Lô 1,000 iPhone 16 Pro Max T10/2026 (Apple Inc)"
    existing = frappe.db.get_value("Trade Shipment", {"shipment_name": shipment_title}, "name")

    supplier = "Apple Inc." if frappe.db.exists("Supplier", "Apple Inc.") else "Apple Inc"

    if not existing:
        doc = frappe.get_doc({
            "doctype": "Trade Shipment",
            "naming_series": "TS-.YYYY.-.#####",
            "shipment_name": shipment_title,
            "supplier": supplier,
            "incoterm": "CIF",
            "named_place": "Cát Lái Port, TP.HCM",
            "transport_mode": "Ocean FCL",
            "shipping_line": "Maersk Line",
            "forwarder": "Maersk Line",
            "master_bl": "MAEU987654321",
            "origin_port": "Shanghai Port (CNSHA)",
            "destination_port": "Cat Lai Port (VNCLI)",
            "status": "In Transit",
            "cost_status": "Open",
            "planned_currency": "USD",
            "planned_exchange_rate": 25400.0,
            "containers": [
                {
                    "container_no": "MSKU1234567",
                    "container_type": "40ft HC",
                    "seal_no": "ML-VN889900",
                    "gross_weight_kg": 18500.0,
                    "volume_cbm": 58.5,
                    "demurrage_free_days": 7,
                    "detention_free_days": 14,
                    "status": "On Vessel"
                }
            ],
            "cost_items": [
                {
                    "charge_type": "Cước biển quốc tế (Ocean Freight)",
                    "budgeted_currency": "USD",
                    "budgeted_amount_cur": 3000.0,
                    "budgeted_fx_rate": 25400.0,
                    "actual_currency": "USD",
                    "actual_amount_cur": 3200.0,
                    "actual_fx_rate": 25450.0,
                    "invoice_reference": "INV-MAEU-001",
                    "remarks": "Cước tàu biển thực tế tăng 200 USD và tỷ giá tăng 50 VND"
                },
                {
                    "charge_type": "Phí nâng hạ cảng (THC - Terminal Handling Charge)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 5200000.0,
                    "budgeted_fx_rate": 1.0,
                    "actual_currency": "VND",
                    "actual_amount_cur": 5200000.0,
                    "actual_fx_rate": 1.0,
                    "invoice_reference": "INV-MAEU-002"
                },
                {
                    "charge_type": "Phí phát hành vận đơn (B/L Fee)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 1100000.0,
                    "budgeted_fx_rate": 1.0,
                    "actual_currency": "VND",
                    "actual_amount_cur": 1100000.0,
                    "actual_fx_rate": 1.0,
                    "invoice_reference": "INV-MAEU-003"
                },
                {
                    "charge_type": "Bảo hiểm hàng hải quốc tế (Marine Insurance)",
                    "budgeted_currency": "USD",
                    "budgeted_amount_cur": 250.0,
                    "budgeted_fx_rate": 25400.0,
                    "actual_currency": "USD",
                    "actual_amount_cur": 250.0,
                    "actual_fx_rate": 25450.0,
                    "invoice_reference": "POL-BAOVIET-889"
                },
                {
                    "charge_type": "Phí dịch vụ khai hải quan (Customs Brokerage)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 2500000.0,
                    "budgeted_fx_rate": 1.0,
                    "actual_currency": "VND",
                    "actual_amount_cur": 2500000.0,
                    "actual_fx_rate": 1.0,
                    "invoice_reference": "INV-LOG-004"
                },
                {
                    "charge_type": "Cước vận tải nội địa kéo cont (Inland Trucking)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 4800000.0,
                    "budgeted_fx_rate": 1.0,
                    "actual_currency": "VND",
                    "actual_amount_cur": 4800000.0,
                    "actual_fx_rate": 1.0,
                    "invoice_reference": "INV-TRK-005"
                }
            ]
        })

        # Thiết lập lịch trình 9 mốc
        curr_today = today()
        doc.append("milestones", {"milestone_code": "M01_PO_ISSUED", "milestone_name": "Phát hành Đơn mua hàng (PO Issued)", "planned_date": add_days(curr_today, -10), "actual_date": add_days(curr_today, -10), "status": "Completed"})
        doc.append("milestones", {"milestone_code": "M02_CARGO_READY", "milestone_name": "Hàng sẵn sàng đóng gói (Cargo Ready Date)", "planned_date": add_days(curr_today, -5), "actual_date": add_days(curr_today, -4), "status": "Completed"}) # Trễ 1 ngày
        doc.append("milestones", {"milestone_code": "M03_RISK_TRANSFER", "milestone_name": "Chuyển giao rủi ro Incoterm (Risk Transfer Point)", "planned_date": add_days(curr_today, -2), "actual_date": add_days(curr_today, -2), "status": "Completed"})
        doc.append("milestones", {"milestone_code": "M04_ETD", "milestone_name": "Tàu rời cảng xuất phát (Departure POL)", "planned_date": add_days(curr_today, -1), "actual_date": add_days(curr_today, -1), "status": "Completed"})
        doc.append("milestones", {"milestone_code": "M05_ETA", "milestone_name": "Tàu cập cảng đến (Arrival POD)", "planned_date": add_days(curr_today, 8), "status": "Pending"})
        doc.append("milestones", {"milestone_code": "M06_CUSTOMS_REG", "milestone_name": "Đăng ký mở tờ khai hải quan (Customs Registered)", "planned_date": add_days(curr_today, 9), "status": "Pending"})
        doc.append("milestones", {"milestone_code": "M07_CUSTOMS_CLEAR", "milestone_name": "Thông quan hải quan hoàn tất (Customs Cleared)", "planned_date": add_days(curr_today, 11), "status": "Pending"})
        doc.append("milestones", {"milestone_code": "M08_DEM_DET_DEADLINE", "milestone_name": "Hạn chót miễn phí lưu bãi/cont (Free-time Deadline)", "planned_date": add_days(curr_today, 15), "status": "Pending"})
        doc.append("milestones", {"milestone_code": "M09_WH_RECEIPT", "milestone_name": "Nhập kho hoàn tất (Warehouse Receipt)", "planned_date": add_days(curr_today, 12), "status": "Pending"})

        # 4. Bảng phân bổ mặt hàng & giá vốn
        doc.append("item_allocations", {
            "item_code": "IPHONE-16-PROMAX",
            "item_name": "Apple iPhone 16 Pro Max 256GB Desert Titanium",
            "qty": 800.0,
            "uom": "Nos",
            "volume_cbm": 40.0,
            "gross_weight_kg": 14000.0,
            "goods_value_vnd": 20360000000.0,
            "allocated_freight_vnd": 57008000.0,
            "allocated_other_cost_vnd": 14000000.0,
            "total_allocated_cost_vnd": 71008000.0,
            "final_unit_landed_cost_vnd": 25538760.0
        })
        doc.append("item_allocations", {
            "item_code": "AIRPODS-PRO-2",
            "item_name": "Apple AirPods Pro 2 MagSafe USB-C (2nd Gen)",
            "qty": 1000.0,
            "uom": "Nos",
            "volume_cbm": 18.5,
            "gross_weight_kg": 4500.0,
            "goods_value_vnd": 5090000000.0,
            "allocated_freight_vnd": 24432000.0,
            "allocated_other_cost_vnd": 6000000.0,
            "total_allocated_cost_vnd": 30432000.0,
            "final_unit_landed_cost_vnd": 5120432.0
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  + Tạo thành công Lô hàng mẫu: {doc.name} - {shipment_title}")
        print(f"    • Tổng dự toán: {doc.total_budgeted_cost:,.0f} VND")
        print(f"    • Tổng thực tế: {doc.total_actual_cost:,.0f} VND")
        print(f"    • Chênh lệch: +{doc.cost_variance_amount:,.0f} VND ({doc.cost_variance_pct}%)")
    else:
        # Cập nhật thêm bảng phân bổ vào lô hàng hiện có
        doc = frappe.get_doc("Trade Shipment", existing)
        if not doc.item_allocations:
            doc.append("item_allocations", {
                "item_code": "IPHONE-16-PROMAX",
                "item_name": "Apple iPhone 16 Pro Max 256GB Desert Titanium",
                "qty": 800.0,
                "uom": "Nos",
                "volume_cbm": 40.0,
                "gross_weight_kg": 14000.0,
                "goods_value_vnd": 20360000000.0,
                "allocated_freight_vnd": 57008000.0,
                "allocated_other_cost_vnd": 14000000.0,
                "total_allocated_cost_vnd": 71008000.0,
                "final_unit_landed_cost_vnd": 25538760.0
            })
            doc.append("item_allocations", {
                "item_code": "AIRPODS-PRO-2",
                "item_name": "Apple AirPods Pro 2 MagSafe USB-C (2nd Gen)",
                "qty": 1000.0,
                "uom": "Nos",
                "volume_cbm": 18.5,
                "gross_weight_kg": 4500.0,
                "goods_value_vnd": 5090000000.0,
                "allocated_freight_vnd": 24432000.0,
                "allocated_other_cost_vnd": 6000000.0,
                "total_allocated_cost_vnd": 30432000.0,
                "final_unit_landed_cost_vnd": 5120432.0
            })
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"  + Đã cập nhật Bảng Phân Bổ Mặt Hàng vào lô {existing} thành công!")
        else:
            print(f"  * Lô hàng đã tồn tại và đã có phân bổ mặt hàng: {existing}")

def ensure_suppliers():
    """Tạo nhanh nhà cung cấp và hãng tàu nếu chưa có"""
    if not frappe.db.exists("Supplier", "Maersk Line"):
        s = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": "Maersk Line",
            "supplier_group": "Services",
            "supplier_type": "Company"
        })
        s.insert(ignore_permissions=True)
        print("  + Tạo nhà cung cấp/hãng tàu: Maersk Line")
