# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

from typing import Optional, Dict, Any

try:
    import frappe
    from frappe import _
    from frappe.model.document import Document
except ImportError:
    frappe = None
    _ = lambda x: x

    class Document:
        def __init__(self, *args, **kwargs):
            self.__dict__.update(kwargs)
            if args and isinstance(args[0], dict):
                self.__dict__.update(args[0])

        def __getattr__(self, key):
            return self.__dict__.get(key, None)

        def get(self, key, default=None):
            return getattr(self, key, default)

        def set(self, key, value):
            setattr(self, key, value)

        def as_dict(self):
            return dict(self.__dict__)


class TradeCostItem(Document):
    """
    Child DocType representing an individual logistics/trade cost line item.
    Belongs to parent Trade Cost Sheet (table field: cost_items).
    Covers the 11 standard cost types, estimated vs actual costs,
    multi-currency conversion, and variance calculations.
    """

    COST_TYPES = [
        "Freight",
        "Insurance",
        "Duty",
        "Tax",
        "Port",
        "Handling",
        "Storage",
        "Demurrage/Detention",
        "Trucking",
        "Broker Fee",
        "Other"
    ]

    STATUSES = [
        "Draft",
        "Verified",
        "Allocated",
        "Cancelled"
    ]

    def validate(self):
        """Validate cost item fields, calculate base costs and line variance."""
        self.validate_cost_type()
        self.validate_status()
        self.validate_exchange_rate()
        self.sync_amounts()
        self.calculate_base_amounts()
        self.calculate_variance()

    def validate_cost_type(self):
        """Ensure cost_type is one of the 11 standard taxonomy options."""
        cost_type = getattr(self, "cost_type", None)
        if not cost_type:
            if frappe:
                frappe.throw(_("Cost Type is required"))
            else:
                raise ValueError("Cost Type is required")

        if cost_type not in self.COST_TYPES:
            msg = _("Invalid Cost Type '{0}'. Must be one of: {1}").format(
                cost_type, ", ".join(self.COST_TYPES)
            )
            if frappe:
                frappe.throw(msg)
            else:
                raise ValueError(msg)

    def validate_status(self):
        """Ensure status is within valid lifecycle states."""
        status = getattr(self, "status", None)
        if not status:
            self.status = "Draft"
        elif self.status not in self.STATUSES:
            msg = _("Invalid Status '{0}'. Must be one of: {1}").format(
                self.status, ", ".join(self.STATUSES)
            )
            if frappe:
                frappe.throw(msg)
            else:
                raise ValueError(msg)

    def validate_exchange_rate(self):
        """Ensure exchange rate is a positive float."""
        try:
            rate = float(getattr(self, "exchange_rate", 1.0) or 1.0)
            if rate <= 0:
                self.exchange_rate = 1.0
            else:
                self.exchange_rate = rate
        except (ValueError, TypeError):
            self.exchange_rate = 1.0

    def sync_amounts(self):
        """Keep estimated_cost/estimated_amount and actual_cost/actual_amount in sync."""
        est = getattr(self, "estimated_cost", None)
        if est is None:
            est = getattr(self, "estimated_amount", 0.0)
        self.estimated_cost = float(est or 0.0)
        self.estimated_amount = self.estimated_cost

        act = getattr(self, "actual_cost", None)
        if act is None:
            act = getattr(self, "actual_amount", 0.0)
        self.actual_cost = float(act or 0.0)
        self.actual_amount = self.actual_cost

    def calculate_base_amounts(self):
        """
        Convert estimated and actual costs in transaction currency to base company currency.
        base_cost = transaction_cost * exchange_rate
        """
        rate = float(getattr(self, "exchange_rate", 1.0) or 1.0)
        est = float(getattr(self, "estimated_cost", 0.0) or 0.0)
        act = float(getattr(self, "actual_cost", 0.0) or 0.0)

        base_est = round(est * rate, 2)
        base_act = round(act * rate, 2)

        self.base_estimated_cost = base_est
        self.estimated_amount_base = base_est
        self.base_actual_cost = base_act
        self.actual_amount_base = base_act

    def calculate_variance(self):
        """
        Compute line-level variance:
        - variance_amount = actual_cost - estimated_cost
        - variance_pct = ((actual_cost - estimated_cost) / estimated_cost) * 100
        Handles zero-division safely.
        """
        est = float(getattr(self, "estimated_cost", 0.0) or 0.0)
        act = float(getattr(self, "actual_cost", 0.0) or 0.0)

        self.variance_amount = round(act - est, 2)

        if est > 0:
            self.variance_pct = round(((act - est) / est) * 100.0, 2)
        elif est == 0 and act > 0:
            self.variance_pct = 100.0
        else:
            self.variance_pct = 0.0

    def has_invoice(self) -> bool:
        """Returns True if item has an assigned invoice number and is not cancelled."""
        inv = getattr(self, "invoice_number", None)
        status = getattr(self, "status", "Draft")
        return bool(inv and str(inv).strip()) and status != "Cancelled"

    def is_verified(self) -> bool:
        """Returns True if cost line is verified or already allocated."""
        return getattr(self, "status", None) in ["Verified", "Allocated"]

    def is_allocated(self) -> bool:
        """Returns True if cost line is allocated."""
        return getattr(self, "status", None) == "Allocated"

    def is_cancelled(self) -> bool:
        """Returns True if cost line is cancelled."""
        return getattr(self, "status", None) == "Cancelled"
