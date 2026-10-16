# Copyright (c) 2026, Logistics Wizard and contributors
# For license information, please see license.txt

"""
costing_engine — Module 5: Trade Cost & Landed Cost Management
==============================================================
Subpackage providing:
- CostAllocationEngine: 5 basis rules (Value, Qty, Weight, Volume, Custom),
  Hare-Niemeyer largest remainder rounding adjustment (difference <= 0.01 / exact 0.00).
- LCVIntegrator: Non-invasive ERPNext Landed Cost Voucher synchronization with
  'Distribute Manually' mode and 1 consolidated tax line.
"""

from logistics_wizard.costing_engine.allocation_engine import (
    CostAllocationEngine,
    allocate_costs,
    hare_niemeyer_allocation,
    derive_item_basis,
    derive_item_weight,
    derive_item_volume,
    derive_item_value,
    derive_item_qty,
    derive_item_custom_factor,
    normalize_rule_name,
    extract_receipt_items,
)

from logistics_wizard.costing_engine.lcv_integrator import (
    LCVIntegrator,
    create_or_update_lcv,
    generate_lcv_payload,
    get_company_expense_account,
)

from logistics_wizard.costing_engine.export_tracker import (
    ExportTracker,
    calculate_export_profitability,
    get_export_profitability_summary,
)

from logistics_wizard.costing_engine.audit_engine import (
    CostAuditEngine,
    audit_cost_sheet,
)

from logistics_wizard.costing_engine.api import (
    get_case_cost_summary,
    get_case_export_profitability,
    audit_case_costs,
    allocate_and_sync_lcv,
    format_case_cost_summary,
)

__all__ = [
    "CostAllocationEngine",
    "allocate_costs",
    "hare_niemeyer_allocation",
    "derive_item_basis",
    "derive_item_weight",
    "derive_item_volume",
    "derive_item_value",
    "derive_item_qty",
    "derive_item_custom_factor",
    "normalize_rule_name",
    "extract_receipt_items",
    "LCVIntegrator",
    "create_or_update_lcv",
    "generate_lcv_payload",
    "get_company_expense_account",
    "ExportTracker",
    "calculate_export_profitability",
    "get_export_profitability_summary",
    "CostAuditEngine",
    "audit_cost_sheet",
    "get_case_cost_summary",
    "get_case_export_profitability",
    "audit_case_costs",
    "allocate_and_sync_lcv",
    "format_case_cost_summary",
]
