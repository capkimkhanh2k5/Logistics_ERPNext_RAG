app_name = "logistics_wizard"
app_title = "Logistics"
app_publisher = "Khanh"
app_description = "Import-Export Workflow Widget and Shipment Tracking Management Hub"
app_email = "khanh@logistics.local"
app_license = "mit"

app_logo_url = "/assets/logistics_wizard/images/logistics-wizard-logo.svg"
app_home = "/desk/logistics-wizard/trade-case-overview"

add_to_apps_screen = [
    {
        "name": app_name,
        "logo": app_logo_url,
        "title": "Logistics",
        "route": app_home,
        "sequence_id": 2,
    }
]

app_include_js = [
    "leaflet.bundle.js",
    "smart_workflow_widget.bundle.js",
    "unified_logistics_hub.bundle.js"
]
app_include_css = [
    "leaflet.bundle.css",
    "smart_workflow_widget.bundle.css",
    "unified_logistics_hub.bundle.css"
]


doctype_js = {
    "Shipment Tracking": "public/js/shipment_tracking.js",
    "Trade Cost Sheet": "doctype/trade_cost_sheet/trade_cost_sheet.js"
}

doc_events = {
    "Shipment Tracking": {
        "validate": "logistics_wizard.api.on_shipment_tracking_validate"
    },
    "Purchase Receipt": {
        "before_submit": "logistics_wizard.api.validate_purchase_receipt_shipment_status"
    }
}

