import sys

__version__ = "0.0.1"

# Expose self as submodule 'logistics_wizard.logistics_wizard' so Frappe's
# get_module_path("Logistics Wizard", ...) can resolve app.module correctly
# when app and module share the same scrubbed name without nested directories.
_self = sys.modules.get(__name__)
if _self:
    sys.modules[f"{__name__}.{__name__}"] = _self
    setattr(_self, __name__, _self)

try:
    import frappe
    if hasattr(frappe, "local"):
        if getattr(frappe.local, "module_app", None) is not None and isinstance(frappe.local.module_app, dict):
            frappe.local.module_app.setdefault("logistics_wizard", "logistics_wizard")
        if getattr(frappe.local, "app_modules", None) is not None and isinstance(frappe.local.app_modules, dict):
            frappe.local.app_modules.setdefault("logistics_wizard", ["logistics_wizard"])
except Exception:
    pass
