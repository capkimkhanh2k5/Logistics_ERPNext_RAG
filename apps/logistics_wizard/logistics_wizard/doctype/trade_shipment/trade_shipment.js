// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.ui.form.on("Trade Shipment", {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Hiển thị indicator trạng thái vượt ngân sách
            if (frm.doc.cost_variance_pct > 10) {
                frm.dashboard.set_headline(
                    __("⚠️ CẢNH BÁO: Lô hàng đang vượt ngân sách {0}% (+{1} VND)", [
                        frm.doc.cost_variance_pct,
                        format_currency(frm.doc.cost_variance_amount, "VND")
                    ]),
                    "orange"
                );
            } else if (frm.doc.cost_variance_pct <= 0 && frm.doc.total_actual_cost > 0) {
                frm.dashboard.set_headline(
                    __("✅ Chi phí thực tế nằm trong định mức dự toán ({0}% tiết kiệm)", [
                        Math.abs(frm.doc.cost_variance_pct)
                    ]),
                    "green"
                );
            }
        }
    },
    planned_currency: function(frm) {
        if (frm.doc.planned_currency === "USD" && (!frm.doc.planned_exchange_rate || frm.doc.planned_exchange_rate === 1)) {
            frm.set_value("planned_exchange_rate", 25450);
        }
    }
});
