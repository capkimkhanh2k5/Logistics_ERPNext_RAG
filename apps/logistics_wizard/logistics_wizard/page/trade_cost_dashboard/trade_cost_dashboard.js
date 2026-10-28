// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['trade-cost-dashboard'] = frappe.pages['trade-cost-dashboard'] || {};

frappe.pages['trade-cost-dashboard'].on_page_load = function (wrapper) {
    frappe.route_options = Object.assign({}, frappe.route_options, { tab: 'cost' });
    frappe.set_route('managementLogistic');
};

frappe.pages['trade-cost-dashboard'].on_page_show = function (wrapper) {
    frappe.route_options = Object.assign({}, frappe.route_options, { tab: 'cost' });
    frappe.set_route('managementLogistic');
};
