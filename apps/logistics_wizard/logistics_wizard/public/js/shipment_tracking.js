frappe.ui.form.on("Shipment Tracking", {
    refresh: function(frm) {
        frm.add_custom_button(__('Đồng bộ Tracking (Mô phỏng)'), function() {
            frappe.call({
                method: 'logistics_wizard.api.sync_shipment_now',
                args: {
                    shipment_name: frm.doc.name,
                    tracking_number: frm.doc.tracking_number || frm.doc.name
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('Đã đồng bộ tracking và cập nhật trạng thái thành công!'));
                        frm.reload_doc();
                    }
                }
            });
        }, __('Tracking'));
    }
});
