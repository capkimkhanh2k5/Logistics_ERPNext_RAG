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


class ShipmentTracking(Document):
    """
    Master DocType for tracking logistics shipments across international routes.
    Includes container/BL identifiers, schedule tracking (ETD, ATD, ETA, ATA),
    delay calculation, and 9-milestone DCSA normalization.
    """

    def validate(self):
        # Auto-synchronize alias fields for backward compatibility
        if hasattr(self, "container_id") and self.container_id:
            self.container_no = self.container_id
        elif hasattr(self, "container_no") and self.container_no:
            self.container_id = self.container_no

        if hasattr(self, "bill_of_lading") and self.bill_of_lading:
            self.bl_awb_number = self.bill_of_lading
        elif hasattr(self, "bl_awb_number") and self.bl_awb_number:
            self.bill_of_lading = self.bl_awb_number

        if hasattr(self, "flight_number") and self.flight_number:
            self.flight_no = self.flight_number
        elif hasattr(self, "flight_no") and self.flight_no:
            self.flight_number = self.flight_no

        if hasattr(self, "current_lat") and self.current_lat is not None:
            self.current_latitude = self.current_lat
        elif hasattr(self, "current_latitude") and self.current_latitude is not None:
            self.current_lat = self.current_latitude

        if hasattr(self, "current_lon") and self.current_lon is not None:
            self.current_longitude = self.current_lon
        elif hasattr(self, "current_longitude") and self.current_longitude is not None:
            self.current_lon = self.current_longitude
