# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

import json
import os
import frappe

def install_all_doctypes():
    print("=== [BẮT ĐẦU CÀI ĐẶT DOCTYPES GIAI ĐOẠN 1 & 2] ===")

    doctype_files = [
        # Giai đoạn 1
        ("HS Preferential Rate", "hs_preferential_rate", "hs_preferential_rate.json"),
        ("Charge Type", "charge_type", "charge_type.json"),
        ("HS Tariff Rate", "hs_tariff_rate", "hs_tariff_rate.json"),
        ("Customs Exchange Rate", "customs_exchange_rate", "customs_exchange_rate.json"),

        # Giai đoạn 2 - Child Tables trước
        ("Trade Shipment Milestone", "trade_shipment_milestone", "trade_shipment_milestone.json"),
        ("Trade Shipment Container", "trade_shipment_container", "trade_shipment_container.json"),
        ("Trade Shipment Cost Item", "trade_shipment_cost_item", "trade_shipment_cost_item.json"),
        ("Trade Shipment Item Allocation", "trade_shipment_item_allocation", "trade_shipment_item_allocation.json"),

        # Giai đoạn 2 - Master DocType sau
        ("Trade Shipment", "trade_shipment", "trade_shipment.json")
    ]

    base_path = frappe.get_app_path("logistics_wizard")

    for dt_name, folder, json_file in doctype_files:
        json_abs_path = os.path.join(base_path, "doctype", folder, json_file)

        with open(json_abs_path, "r", encoding="utf-8") as f:
            dt_data = json.load(f)

        dt_data["custom"] = 1

        if frappe.db.exists("DocType", dt_name):
            print(f"  * Cập nhật DocType hiện có: {dt_name}")
            doc = frappe.get_doc("DocType", dt_name)
            doc.set("fields", [])
            for field in dt_data.get("fields", []):
                doc.append("fields", field)
            for k in ["field_order", "search_fields", "sort_field", "sort_order", "track_changes"]:
                if k in dt_data:
                    setattr(doc, k, dt_data[k])
            doc.save(ignore_permissions=True)
        else:
            print(f"  + Tạo mới DocType: {dt_name}")
            doc = frappe.get_doc(dt_data)
            doc.insert(ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache()
    print("=== [HOÀN TẤT CÀI ĐẶT VÀ ĐỒNG BỘ DOCTYPES] ===")

if __name__ == "__main__":
    install_all_doctypes()
