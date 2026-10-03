// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['trade-case-overview'].on_page_load = function (wrapper) {
    frappe.route_options = Object.assign({}, frappe.route_options, { tab: 'overview' });
    frappe.set_route('managementLogistic');
};
