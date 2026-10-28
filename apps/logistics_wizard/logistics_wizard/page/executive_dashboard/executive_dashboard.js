// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['executive-dashboard'] = frappe.pages['executive-dashboard'] || {};

frappe.pages['executive-dashboard'].on_page_load = function (wrapper) {
    if (window.init_logistics_hub_page) {
        window.init_logistics_hub_page('executive-dashboard', 'executive', wrapper);
    }
};

frappe.pages['executive-dashboard'].on_page_show = function (wrapper) {
    if (window.show_logistics_hub_page) {
        window.show_logistics_hub_page(wrapper, 'executive');
    }
};
