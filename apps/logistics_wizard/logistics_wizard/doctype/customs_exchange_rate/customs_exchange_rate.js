// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customs Exchange Rate", {
    valid_from: function(frm) {
        if (frm.doc.valid_from && !frm.doc.valid_to) {
            // Mặc định chu kỳ hải quan thường là 7 ngày (từ Thứ 5 đến Thứ 4 tuần sau)
            let valid_to = frappe.datetime.add_days(frm.doc.valid_from, 6);
            frm.set_value("valid_to", valid_to);
        }
    }
});
