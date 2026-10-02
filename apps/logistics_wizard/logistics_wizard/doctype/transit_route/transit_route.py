# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

try:
    from frappe.model.document import Document
except ImportError:
    class Document:
        def __init__(self, *args, **kwargs):
            self.__dict__.update(kwargs)
            if args and isinstance(args[0], dict):
                self.__dict__.update(args[0])

        def get(self, key, default=None):
            return getattr(self, key, default)

        def set(self, key, value):
            setattr(self, key, value)

        def as_dict(self):
            return dict(self.__dict__)


class TransitRoute(Document):
    """
    Child DocType representing a single transit route milestone/checkpoint
    in the international supply chain.
    """
    pass
