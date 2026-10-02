// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.ui.form.on("Charge Type", {
    cost_category: function(frm) {
        if (frm.doc.cost_category && frm.doc.cost_category.includes("Phí phạt")) {
            frm.set_value("include_in_valuation", 0);
            frm.set_value("allocation_criterion", "Không phân bổ (None / Expense)");
            frappe.show_alert({
                message: __("Phí phạt không được tính vào giá vốn hàng tồn kho theo quy định kế toán."),
                indicator: "orange"
            });
        }
    },
    include_in_valuation: function(frm) {
        if (frm.doc.include_in_valuation && frm.doc.allocation_criterion === "Không phân bổ (None / Expense)") {
            frm.set_value("allocation_criterion", "Theo Giá trị hàng (Value)");
        }
    }
});
