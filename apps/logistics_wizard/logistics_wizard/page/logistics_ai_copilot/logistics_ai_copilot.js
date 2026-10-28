// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

frappe.pages['logistics-ai-copilot'] = frappe.pages['logistics-ai-copilot'] || {};

frappe.pages['logistics-ai-copilot'].on_page_load = function (wrapper) {
    if (window.init_logistics_hub_page) {
        window.init_logistics_hub_page('logistics-ai-copilot', 'copilot', wrapper);
    }
};

frappe.pages['logistics-ai-copilot'].on_page_show = function (wrapper) {
    if (window.show_logistics_hub_page) {
        window.show_logistics_hub_page(wrapper, 'copilot');
    }
};
