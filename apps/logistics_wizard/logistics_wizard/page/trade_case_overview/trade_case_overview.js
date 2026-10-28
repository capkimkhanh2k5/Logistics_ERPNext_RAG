// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['trade-case-overview'] = frappe.pages['trade-case-overview'] || {};

frappe.pages['trade-case-overview'].on_page_load = function (wrapper) {
    if (window.init_logistics_hub_page) {
        window.init_logistics_hub_page('trade-case-overview', 'overview', wrapper);
    }
};

frappe.pages['trade-case-overview'].on_page_show = function (wrapper) {
    if (window.show_logistics_hub_page) {
        window.show_logistics_hub_page(wrapper, 'overview');
    }
};
