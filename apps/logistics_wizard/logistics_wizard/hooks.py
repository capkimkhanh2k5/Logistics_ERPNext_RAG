app_name = "logistics_wizard"
app_title = "Logistics Wizard"
app_publisher = "Khanh"
app_description = "Import-Export Workflow Widget and Shipment Tracking Management Hub"
app_email = "khanh@logistics.local"
app_license = "mit"

app_include_js = [
    "leaflet.bundle.js",
    "smart_workflow_widget.bundle.js"
]
app_include_css = [
    "leaflet.bundle.css",
    "smart_workflow_widget.bundle.css"
]


doctype_js = {
    "Shipment Tracking": "public/js/shipment_tracking.js"
}

doc_events = {
    "Shipment Tracking": {
        "validate": "logistics_wizard.api.on_shipment_tracking_validate"
    }
}
