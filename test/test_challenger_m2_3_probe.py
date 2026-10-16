#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_challenger_m2_3_probe.py — Independent Deep Probe on Remediated lcv_integrator.py
Conducted by: challenger_m2_3
"""

import sys
import os
import math
import random
import copy

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logistics_wizard.costing_engine.lcv_integrator import (
    LCVIntegrator,
    create_or_update_lcv,
    generate_lcv_payload,
    get_company_expense_account,
    on_cost_sheet_submit,
    flt,
)
from logistics_wizard.costing_engine.allocation_engine import (
    allocate_costs,
    CostAllocationEngine,
)

def test_trade_type_boundary_matrix():
    print("Test 1: Trade Type Boundary Matrix...")
    allowed_cases = ["Import", "import", "IMPORT", " Import ", "  iMPort  ", None, ""]
    # When trade_type is None or "", default fallback is "Import"
    for tc in allowed_cases:
        sheet = {"name": "TCS-TT-OK", "trade_type": tc, "company": "Test Co"}
        name = create_or_update_lcv(sheet, [])
        assert name.startswith("LCV-2026-"), f"Failed on trade_type='{tc}': {name}"

    rejected_cases = [
        "Export", "export", "EXPORT", " Export ", "  eXPOrT  ",
        "Outbound", "Domestic", "Transshipment", "Transit", "RandomString", 123
    ]
    for tc in rejected_cases:
        sheet = {"name": "TCS-TT-REJ", "trade_type": tc, "company": "Test Co"}
        try:
            create_or_update_lcv(sheet, [])
            assert False, f"Expected ValueError for trade_type='{tc}', but succeeded"
        except ValueError:
            pass
    print("  -> Passed all trade type boundary tests.")

def test_document_links_active_status_matrix():
    print("Test 2: Document Links Active Status Matrix...")
    sheet = {
        "name": "TCS-LINKS",
        "trade_type": "Import",
        "document_links": [
            {"document_type": "Purchase Receipt", "document_name": "PR-ACT-1", "is_active": 1},
            {"document_type": "Purchase Receipt", "document_name": "PR-ACT-TRUE", "is_active": True},
            {"document_type": "Purchase Receipt", "document_name": "PR-ACT-STR1", "is_active": "1"},
            {"document_type": "Purchase Receipt", "document_name": "PR-INACT-0", "is_active": 0},
            {"document_type": "Purchase Receipt", "document_name": "PR-INACT-FALSE", "is_active": False},
            {"document_type": "Purchase Receipt", "document_name": "PR-INACT-STR0", "is_active": "0"},
            {"document_type": "Purchase Receipt", "document_name": "PR-ACT-DEFAULT"}, # Missing is_active -> defaults to 1
            {"document_type": "Sales Order", "document_name": "SO-001", "is_active": 1}, # Non-PR/PI
        ]
    }
    payload = generate_lcv_payload(sheet, [])
    receipts = [r["receipt_document"] for r in payload["purchase_receipts"]]
    assert "PR-ACT-1" in receipts
    assert "PR-ACT-TRUE" in receipts
    assert "PR-ACT-STR1" in receipts
    assert "PR-ACT-DEFAULT" in receipts
    assert "PR-INACT-0" not in receipts
    assert "PR-INACT-FALSE" not in receipts
    assert "PR-INACT-STR0" not in receipts
    assert "SO-001" not in receipts
    print(f"  -> Filtered receipts: {receipts}")
    print("  -> Passed all document links active status tests.")

def test_extreme_quantities_and_rates():
    print("Test 3: Extreme Quantities and Rates...")
    items = [
        {"item_code": "ZERO-1", "qty": 0.0, "base_amount": 0.0, "allocated_charges": 10.0},
        {"item_code": "ZERO-2", "qty": 0.0, "base_amount": 500.0, "allocated_charges": 10.0},
        {"item_code": "ZERO-3", "qty": 0.0, "base_amount": 500.0, "rate": 50.0, "allocated_charges": 10.0},
        {"item_code": "NEG-1", "qty": -10.0, "base_amount": -1000.0, "allocated_charges": 0.0},
        {"item_code": "LARGE-1", "qty": 10_000_000.0, "base_amount": 100_000_000_000.0, "allocated_charges": 5000.0},
    ]
    sheet = {"name": "TCS-EXTREME", "trade_type": "Import"}
    payload = generate_lcv_payload(sheet, items)
    assert len(payload["items"]) == 5
    # Item 1: qty 0, base 0 -> rate 0.0
    assert payload["items"][0]["rate"] == 0.0
    # Item 2: qty 0, base 500 -> rate 0.0 (safe guard against division by zero)
    assert payload["items"][1]["rate"] == 0.0
    # Item 3: user specified rate 50.0 preserved
    assert payload["items"][2]["rate"] == 50.0
    # Item 4: negative qty -> rate 0.0
    assert payload["items"][3]["rate"] == 0.0
    # Item 5: rate 10,000.0
    assert payload["items"][4]["rate"] == 10000.0
    print("  -> Passed extreme quantities and rates tests.")

def test_large_scale_batch_conservation():
    print("Test 4: Large Scale Batch Conservation (2,000 items)...")
    rng = random.Random(42)
    n = 2000
    total_cost = 123456.78
    raw_items = [
        {
            "item_code": f"ITEM-{i}",
            "qty": rng.randint(1, 50),
            "base_amount": round(rng.uniform(10.0, 500.0), 2),
            "weight": round(rng.uniform(1.0, 50.0), 2),
            "receipt_document": f"PR-{i % 5}",
            "receipt_document_type": "Purchase Receipt"
        }
        for i in range(n)
    ]
    sheet = {
        "name": "TCS-SCALE-2000",
        "trade_type": "Import",
        "allocation_rule": "By Weight",
        "total_actual_cost": total_cost,
        "items": raw_items,
        "company": "Scale Enterprise Ltd"
    }
    allocations = allocate_costs(sheet)
    sum_alloc = round(sum(it["allocated_charges"] for it in allocations), 2)
    assert math.isclose(sum_alloc, total_cost, abs_tol=0.01), f"Allocation discrepancy: {sum_alloc} vs {total_cost}"
    payload = generate_lcv_payload(sheet, allocations)
    assert len(payload["taxes"]) == 1
    assert math.isclose(payload["taxes"][0]["amount"], total_cost, abs_tol=0.01)
    assert len(payload["purchase_receipts"]) == 5
    print("  -> Passed 2,000 items scale conservation test.")

if __name__ == "__main__":
    test_trade_type_boundary_matrix()
    test_document_links_active_status_matrix()
    test_extreme_quantities_and_rates()
    test_large_scale_batch_conservation()
    print("ALL PROBE TESTS PASSED SUCCESSFULLY!")
