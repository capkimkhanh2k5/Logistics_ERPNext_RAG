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


class TradeCostDocumentLink(Document):
    """
    Child DocType representing a linked operational or financial ERPNext document
    within a Trade Cost Sheet (table field: document_links).
    Supports Purchase Receipts, Purchase Invoices, Sales Orders, Delivery Notes,
    Sales Invoices, and Landed Cost Vouchers.
    """

    ALLOWED_DOC_TYPES = [
        "Purchase Receipt",
        "Purchase Invoice",
        "Sales Order",
        "Delivery Note",
        "Sales Invoice",
        "Landed Cost Voucher"
    ]

    IMPORT_DOC_TYPES = [
        "Purchase Receipt",
        "Purchase Invoice",
        "Landed Cost Voucher"
    ]

    EXPORT_DOC_TYPES = [
        "Sales Order",
        "Delivery Note",
        "Sales Invoice"
    ]

    def validate(self):
        """Validate linked document type, name, and auto-populate party metadata."""
        self.validate_document_type()
        self.validate_document_name()
        self.set_party_metadata()

    def validate_document_type(self):
        """Ensure document_type is one of the supported ERPNext document types."""
        doc_type = getattr(self, "document_type", None)
        if not doc_type:
            if frappe:
                frappe.throw(_("Document Type is required"))
            else:
                raise ValueError("Document Type is required")

        if doc_type not in self.ALLOWED_DOC_TYPES:
            msg = _("Invalid Document Type '{0}'. Must be one of: {1}").format(
                doc_type, ", ".join(self.ALLOWED_DOC_TYPES)
            )
            if frappe:
                frappe.throw(msg)
            else:
                raise ValueError(msg)

    def validate_document_name(self):
        """Ensure document_name is provided."""
        doc_name = getattr(self, "document_name", None)
        if not doc_name or not str(doc_name).strip():
            msg = _("Document Name is required")
            if frappe:
                frappe.throw(msg)
            else:
                raise ValueError(msg)

    def set_party_metadata(self):
        """Automatically set party_type based on standard ERPNext document conventions."""
        doc_type = getattr(self, "document_type", None)
        if doc_type in ["Purchase Receipt", "Purchase Invoice"]:
            self.party_type = "Supplier"
        elif doc_type in ["Sales Order", "Delivery Note", "Sales Invoice"]:
            self.party_type = "Customer"
        elif doc_type == "Landed Cost Voucher":
            self.party_type = None
            self.party = None

    def is_import_document(self) -> bool:
        """Returns True if linked document is an import transaction."""
        return getattr(self, "document_type", None) in self.IMPORT_DOC_TYPES

    def is_export_document(self) -> bool:
        """Returns True if linked document is an export transaction."""
        return getattr(self, "document_type", None) in self.EXPORT_DOC_TYPES

    def is_lcv(self) -> bool:
        """Returns True if linked document is a Landed Cost Voucher."""
        return getattr(self, "document_type", None) == "Landed Cost Voucher"
