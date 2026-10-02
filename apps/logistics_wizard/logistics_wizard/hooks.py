app_name = "logistics_wizard"
app_title = "Logistics Wizard"
app_publisher = "Khanh"
app_description = "Import-Export Workflow Widget and AfterShip API integration"
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

# Overriding Whitelisted methods
override_whitelisted_methods = {
    "logistics_wizard.api.sync_aftership": "logistics_wizard.api.sync_aftership"
}

doctype_js = {
    "Shipment Tracking": "public/js/shipment_tracking.js",
    "Charge Type": "doctype/charge_type/charge_type.js",
    "HS Tariff Rate": "doctype/hs_tariff_rate/hs_tariff_rate.js",
    "Customs Exchange Rate": "doctype/customs_exchange_rate/customs_exchange_rate.js",
    "Trade Shipment": "doctype/trade_shipment/trade_shipment.js"
}

doc_events = {
    "Shipment Tracking": {
        "validate": "logistics_wizard.api.on_shipment_tracking_validate"
    },
    "Purchase Receipt": {
        "before_submit": "logistics_wizard.api.validate_purchase_receipt_shipment_status"
    },
    "Charge Type": {
        "validate": "logistics_wizard.doctype.charge_type.charge_type.validate_charge_type"
    },
    "HS Tariff Rate": {
        "validate": "logistics_wizard.doctype.hs_tariff_rate.hs_tariff_rate.validate_hs_tariff_rate"
    },
    "Customs Exchange Rate": {
        "validate": "logistics_wizard.doctype.customs_exchange_rate.customs_exchange_rate.validate_customs_exchange_rate"
    },
    "Trade Shipment": {
        "validate": "logistics_wizard.doctype.trade_shipment.trade_shipment.validate_trade_shipment"
    },
    "Trade Case": {
        "validate": "logistics_wizard.doctype.trade_case.trade_case.validate_trade_case"
    },
    "Customs Declaration": {
        "validate": "logistics_wizard.doctype.customs_declaration.customs_declaration.validate_customs_declaration",
        "on_update": "logistics_wizard.doctype.customs_declaration.customs_declaration.on_update_customs_declaration"
    },
    "Import Permit": {
        "validate": "logistics_wizard.doctype.import_permit.import_permit.validate_import_permit"
    }
}

