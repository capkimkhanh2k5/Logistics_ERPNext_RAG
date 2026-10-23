// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['shipment-tracking-hub'].on_page_load = function (wrapper) {
    frappe.route_options = Object.assign({}, frappe.route_options, { tab: 'tracking' });
    frappe.set_route('managementLogistic');
};
