// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.ui.form.on("HS Tariff Rate", {
    requires_import_permit: function(frm) {
        frm.toggle_reqd("managing_ministry", frm.doc.requires_import_permit);
    },
    refresh: function(frm) {
        frm.toggle_reqd("managing_ministry", frm.doc.requires_import_permit);
    }
});
