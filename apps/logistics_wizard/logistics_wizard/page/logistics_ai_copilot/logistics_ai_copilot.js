// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['logistics-ai-copilot'] = frappe.pages['logistics-ai-copilot'] || {};

frappe.pages['logistics-ai-copilot'].on_page_load = function (wrapper) {
    frappe.route_options = Object.assign({}, frappe.route_options, { tab: 'copilot' });
    frappe.set_route('managementLogistic');
};

frappe.pages['logistics-ai-copilot'].on_page_show = function (wrapper) {
    frappe.route_options = Object.assign({}, frappe.route_options, { tab: 'copilot' });
    frappe.set_route('managementLogistic');
};
