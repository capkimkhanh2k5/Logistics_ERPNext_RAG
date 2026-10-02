# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days

def seed_shipment():
    print("--- [BẮT ĐẦU NẠP DỮ LIỆU 2 LÔ HÀNG ĐỂ SO SÁNH GIAI ĐOẠN PHÂN BỔ] ---")

    # 1. Đảm bảo có nhà cung cấp & Forwarder
    ensure_suppliers()
    supplier = "Apple Inc." if frappe.db.exists("Supplier", "Apple Inc.") else "Apple Inc"

    curr_today = today()

    # =========================================================================
    # LÔ HÀNG 1: TS-2026-00001 (ĐANG VẬN CHUYỂN - BẢNG PHÂN BỔ ĐỂ TRỐNG)
    # Lý do: Hàng đang trên biển, chi phí thực tế chưa có đủ, chưa thể tính Landed Cost
    # =========================================================================
    title_1 = "Lô 1 (ĐANG ĐI ĐƯỜNG): Chưa chốt chi phí -> Bảng Phân Bổ TRỐNG"
    if frappe.db.exists("Trade Shipment", "TS-2026-00001"):
        doc1 = frappe.get_doc("Trade Shipment", "TS-2026-00001")
        doc1.shipment_name = title_1
        doc1.status = "In Transit"
        doc1.cost_status = "Open"
        # Xóa trắng bảng phân bổ để thể hiện giai đoạn hàng chưa về kho
        doc1.set("item_allocations", [])
        
        # Cập nhật mốc tiến độ: mới xong mốc 1-4 (đang trên biển)
        doc1.set("milestones", [])
        doc1.append("milestones", {"milestone_code": "M01_PO_ISSUED", "milestone_name": "Phát hành Đơn mua hàng (PO Issued)", "planned_date": add_days(curr_today, -10), "actual_date": add_days(curr_today, -10), "status": "Completed"})
        doc1.append("milestones", {"milestone_code": "M02_CARGO_READY", "milestone_name": "Hàng sẵn sàng đóng gói (Cargo Ready Date)", "planned_date": add_days(curr_today, -5), "actual_date": add_days(curr_today, -4), "status": "Completed"})
        doc1.append("milestones", {"milestone_code": "M03_RISK_TRANSFER", "milestone_name": "Chuyển giao rủi ro Incoterm (Risk Transfer Point)", "planned_date": add_days(curr_today, -2), "actual_date": add_days(curr_today, -2), "status": "Completed"})
        doc1.append("milestones", {"milestone_code": "M04_ETD", "milestone_name": "Tàu rời cảng xuất phát (Departure POL)", "planned_date": add_days(curr_today, -1), "actual_date": add_days(curr_today, -1), "status": "Completed"})
        doc1.append("milestones", {"milestone_code": "M05_ETA", "milestone_name": "Tàu cập cảng đến (Arrival POD)", "planned_date": add_days(curr_today, 8), "status": "Pending"})
        doc1.append("milestones", {"milestone_code": "M06_CUSTOMS_REG", "milestone_name": "Đăng ký mở tờ khai hải quan (Customs Registered)", "planned_date": add_days(curr_today, 9), "status": "Pending"})
        doc1.append("milestones", {"milestone_code": "M07_CUSTOMS_CLEAR", "milestone_name": "Thông quan hải quan hoàn tất (Customs Cleared)", "planned_date": add_days(curr_today, 11), "status": "Pending"})
        doc1.append("milestones", {"milestone_code": "M08_DEM_DET_DEADLINE", "milestone_name": "Hạn chót miễn phí lưu bãi/cont (Free-time Deadline)", "planned_date": add_days(curr_today, 15), "status": "Pending"})
        doc1.append("milestones", {"milestone_code": "M09_WH_RECEIPT", "milestone_name": "Nhập kho hoàn tất (Warehouse Receipt)", "planned_date": add_days(curr_today, 12), "status": "Pending"})

        doc1.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"  + [LÔ 1] Cập nhật {doc1.name}: Trạng thái '{doc1.status}', Cost '{doc1.cost_status}' -> Bảng phân bổ TRỐNG.")
    else:
        doc1 = frappe.get_doc({
            "doctype": "Trade Shipment",
            "name": "TS-2026-00001",
            "shipment_name": title_1,
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
                    "remarks": "Mới nhận booking note và tạm tính cước tàu"
                },
                {
                    "charge_type": "Phí nâng hạ cảng (THC - Terminal Handling Charge)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 5200000.0,
                    "budgeted_fx_rate": 1.0
                },
                {
                    "charge_type": "Phí phát hành vận đơn (B/L Fee)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 1100000.0,
                    "budgeted_fx_rate": 1.0
                },
                {
                    "charge_type": "Bảo hiểm hàng hải quốc tế (Marine Insurance)",
                    "budgeted_currency": "USD",
                    "budgeted_amount_cur": 250.0,
                    "budgeted_fx_rate": 25400.0
                },
                {
                    "charge_type": "Phí dịch vụ khai hải quan (Customs Brokerage)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 2500000.0,
                    "budgeted_fx_rate": 1.0
                },
                {
                    "charge_type": "Cước vận tải nội địa kéo cont (Inland Trucking)",
                    "budgeted_currency": "VND",
                    "budgeted_amount_cur": 4800000.0,
                    "budgeted_fx_rate": 1.0
                }
            ],
            "milestones": [
                {"milestone_code": "M01_PO_ISSUED", "milestone_name": "Phát hành Đơn mua hàng (PO Issued)", "planned_date": add_days(curr_today, -10), "actual_date": add_days(curr_today, -10), "status": "Completed"},
                {"milestone_code": "M02_CARGO_READY", "milestone_name": "Hàng sẵn sàng đóng gói (Cargo Ready Date)", "planned_date": add_days(curr_today, -5), "actual_date": add_days(curr_today, -4), "status": "Completed"},
                {"milestone_code": "M03_RISK_TRANSFER", "milestone_name": "Chuyển giao rủi ro Incoterm (Risk Transfer Point)", "planned_date": add_days(curr_today, -2), "actual_date": add_days(curr_today, -2), "status": "Completed"},
                {"milestone_code": "M04_ETD", "milestone_name": "Tàu rời cảng xuất phát (Departure POL)", "planned_date": add_days(curr_today, -1), "actual_date": add_days(curr_today, -1), "status": "Completed"},
                {"milestone_code": "M05_ETA", "milestone_name": "Tàu cập cảng đến (Arrival POD)", "planned_date": add_days(curr_today, 8), "status": "Pending"},
                {"milestone_code": "M06_CUSTOMS_REG", "milestone_name": "Đăng ký mở tờ khai hải quan (Customs Registered)", "planned_date": add_days(curr_today, 9), "status": "Pending"},
                {"milestone_code": "M07_CUSTOMS_CLEAR", "milestone_name": "Thông quan hải quan hoàn tất (Customs Cleared)", "planned_date": add_days(curr_today, 11), "status": "Pending"},
                {"milestone_code": "M08_DEM_DET_DEADLINE", "milestone_name": "Hạn chót miễn phí lưu bãi/cont (Free-time Deadline)", "planned_date": add_days(curr_today, 15), "status": "Pending"},
                {"milestone_code": "M09_WH_RECEIPT", "milestone_name": "Nhập kho hoàn tất (Warehouse Receipt)", "planned_date": add_days(curr_today, 12), "status": "Pending"}
            ],
            "item_allocations": []
        })
        doc1.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  + [LÔ 1] Tạo mới {doc1.name}: Bảng phân bổ TRỐNG (Đang đi đường)")

    # =========================================================================
    # LÔ HÀNG 2: TS-2026-00002 (ĐÃ HOÀN THÀNH - BẢNG PHÂN BỔ ĐÃ ĐIỀN ĐỦ CHI TIẾT)
    # Lý do: Đã thông quan, cont đã hạ trả vỏ, chi phí đã chốt xong -> Đã phân bổ Landed Cost
    # =========================================================================
    title_2 = "Lô 2 (ĐÃ HOÀN THÀNH): Đã về kho & chốt chi phí -> Bảng Phân Bổ ĐÃ ĐIỀN ĐỦ"
    if frappe.db.exists("Trade Shipment", "TS-2026-00002"):
        doc2 = frappe.get_doc("Trade Shipment", "TS-2026-00002")
    else:
        doc2 = frappe.new_doc("Trade Shipment")
        doc2.name = "TS-2026-00002"

    doc2.shipment_name = title_2
    doc2.supplier = supplier
    doc2.incoterm = "CIF"
    doc2.named_place = "Cát Lái Port, TP.HCM"
    doc2.transport_mode = "Ocean FCL"
    doc2.shipping_line = "Maersk Line"
    doc2.forwarder = "Maersk Line"
    doc2.master_bl = "MAEU881122334"
    doc2.origin_port = "Shenzhen Port (CNSZX)"
    doc2.destination_port = "Cat Lai Port (VNCLI)"
    doc2.status = "Completed"
    doc2.cost_status = "Closed"
    doc2.planned_currency = "USD"
    doc2.planned_exchange_rate = 25400.0

    # Container đã hoàn tất trả vỏ
    doc2.set("containers", [])
    doc2.append("containers", {
        "container_no": "MSKU9988776",
        "container_type": "40ft HC",
        "seal_no": "ML-VN556677",
        "gross_weight_kg": 18500.0,
        "volume_cbm": 58.5,
        "demurrage_free_days": 7,
        "detention_free_days": 14,
        "discharge_date": add_days(curr_today, -10),
        "gate_out_date": add_days(curr_today, -8),
        "empty_return_date": add_days(curr_today, -6),
        "demurrage_days": 0,
        "detention_days": 0,
        "status": "Empty Returned"
    })

    # Đầy đủ 6 khoản chi phí thực tế kèm hoá đơn
    doc2.set("cost_items", [])
    doc2.append("cost_items", {
        "charge_type": "Cước biển quốc tế (Ocean Freight)",
        "budgeted_currency": "USD",
        "budgeted_amount_cur": 3000.0,
        "budgeted_fx_rate": 25400.0,
        "actual_currency": "USD",
        "actual_amount_cur": 3200.0,
        "actual_fx_rate": 25450.0,
        "invoice_reference": "INV-MAEU-101",
        "remarks": "Cước tàu biển chốt quyết toán"
    })
    doc2.append("cost_items", {
        "charge_type": "Phí nâng hạ cảng (THC - Terminal Handling Charge)",
        "budgeted_currency": "VND",
        "budgeted_amount_cur": 5200000.0,
        "budgeted_fx_rate": 1.0,
        "actual_currency": "VND",
        "actual_amount_cur": 5200000.0,
        "actual_fx_rate": 1.0,
        "invoice_reference": "INV-MAEU-102"
    })
    doc2.append("cost_items", {
        "charge_type": "Phí phát hành vận đơn (B/L Fee)",
        "budgeted_currency": "VND",
        "budgeted_amount_cur": 1100000.0,
        "budgeted_fx_rate": 1.0,
        "actual_currency": "VND",
        "actual_amount_cur": 1100000.0,
        "actual_fx_rate": 1.0,
        "invoice_reference": "INV-MAEU-103"
    })
    doc2.append("cost_items", {
        "charge_type": "Bảo hiểm hàng hải quốc tế (Marine Insurance)",
        "budgeted_currency": "USD",
        "budgeted_amount_cur": 250.0,
        "budgeted_fx_rate": 25400.0,
        "actual_currency": "USD",
        "actual_amount_cur": 250.0,
        "actual_fx_rate": 25450.0,
        "invoice_reference": "POL-BAOVIET-990"
    })
    doc2.append("cost_items", {
        "charge_type": "Phí dịch vụ khai hải quan (Customs Brokerage)",
        "budgeted_currency": "VND",
        "budgeted_amount_cur": 2500000.0,
        "budgeted_fx_rate": 1.0,
        "actual_currency": "VND",
        "actual_amount_cur": 2500000.0,
        "actual_fx_rate": 1.0,
        "invoice_reference": "INV-LOG-104"
    })
    doc2.append("cost_items", {
        "charge_type": "Cước vận tải nội địa kéo cont (Inland Trucking)",
        "budgeted_currency": "VND",
        "budgeted_amount_cur": 4800000.0,
        "budgeted_fx_rate": 1.0,
        "actual_currency": "VND",
        "actual_amount_cur": 4800000.0,
        "actual_fx_rate": 1.0,
        "invoice_reference": "INV-TRK-105"
    })

    # Cả 9 mốc tiến độ đều Completed
    doc2.set("milestones", [])
    doc2.append("milestones", {"milestone_code": "M01_PO_ISSUED", "milestone_name": "Phát hành Đơn mua hàng (PO Issued)", "planned_date": add_days(curr_today, -30), "actual_date": add_days(curr_today, -30), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M02_CARGO_READY", "milestone_name": "Hàng sẵn sàng đóng gói (Cargo Ready Date)", "planned_date": add_days(curr_today, -25), "actual_date": add_days(curr_today, -24), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M03_RISK_TRANSFER", "milestone_name": "Chuyển giao rủi ro Incoterm (Risk Transfer Point)", "planned_date": add_days(curr_today, -22), "actual_date": add_days(curr_today, -22), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M04_ETD", "milestone_name": "Tàu rời cảng xuất phát (Departure POL)", "planned_date": add_days(curr_today, -20), "actual_date": add_days(curr_today, -20), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M05_ETA", "milestone_name": "Tàu cập cảng đến (Arrival POD)", "planned_date": add_days(curr_today, -10), "actual_date": add_days(curr_today, -10), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M06_CUSTOMS_REG", "milestone_name": "Đăng ký mở tờ khai hải quan (Customs Registered)", "planned_date": add_days(curr_today, -9), "actual_date": add_days(curr_today, -9), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M07_CUSTOMS_CLEAR", "milestone_name": "Thông quan hải quan hoàn tất (Customs Cleared)", "planned_date": add_days(curr_today, -8), "actual_date": add_days(curr_today, -8), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M08_DEM_DET_DEADLINE", "milestone_name": "Hạn chót miễn phí lưu bãi/cont (Free-time Deadline)", "planned_date": add_days(curr_today, -3), "actual_date": add_days(curr_today, -6), "status": "Completed"})
    doc2.append("milestones", {"milestone_code": "M09_WH_RECEIPT", "milestone_name": "Nhập kho hoàn tất (Warehouse Receipt)", "planned_date": add_days(curr_today, -7), "actual_date": add_days(curr_today, -7), "status": "Completed"})

    # BẢNG PHÂN BỔ MẶT HÀNG & GIÁ VỐN (ITEM ALLOCATIONS) - ĐÃ ĐIỀN ĐẦY ĐỦ 2 MẶT HÀNG
    doc2.set("item_allocations", [])
    doc2.append("item_allocations", {
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
    doc2.append("item_allocations", {
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

    if doc2.is_new():
        doc2.insert(ignore_permissions=True)
    else:
        doc2.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"  + [LÔ 2] Tạo/Cập nhật {doc2.name}: Trạng thái '{doc2.status}', Cost '{doc2.cost_status}' -> Bảng phân bổ ĐÃ ĐIỀN ĐỦ 2 mặt hàng!")

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

