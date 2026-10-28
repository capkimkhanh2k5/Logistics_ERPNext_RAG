// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['trade-cost-dashboard'] = frappe.pages['trade-cost-dashboard'] || {};

frappe.pages['trade-cost-dashboard'].on_page_load = function (wrapper) {
    if (window.init_logistics_hub_page) {
        window.init_logistics_hub_page('trade-cost-dashboard', 'cost', wrapper);
    }
};

frappe.pages['trade-cost-dashboard'].on_page_show = function (wrapper) {
    if (window.show_logistics_hub_page) {
        window.show_logistics_hub_page(wrapper, 'cost');
    }
};
