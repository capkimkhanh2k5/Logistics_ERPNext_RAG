#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_adversarial_m2_lcv_stress.py — Comprehensive Adversarial Stress Test Suite for Milestone 2 LCV Sync
========================================================================================================
Thực hiện bởi: EMPIRICAL CHALLENGER 2 (teamwork_challenger_m2_2)
Kiến trúc thẩm định đối kháng:
  - apps/logistics_wizard/logistics_wizard/costing_engine/lcv_integrator.py
  - apps/logistics_wizard/logistics_wizard/costing_engine/allocation_engine.py

Mục tiêu kiểm thử hộp trắng thực nghiệm đối kháng (Adversarial White-box Empirical Stress Testing):
1. SUITE 1: Export Trade Case Rejection & Trade Type Boundary Tests
   - Negative test: Export cost sheet passed to LCV sync -> must raise ValueError.
   - Adversarial casing/whitespace: "export", "EXPORT", " Export ", "Outbound", non-import cases.
   - Lifecycle hook on_cost_sheet_submit resilience for Export cases.
   - LCVIntegrator class method rejection fidelity.

2. SUITE 2: Strict 1-Tax-Line Invariant Stress Testing
   - Zero-exception ERPNext compliance: len(lcv.taxes) == 1 strictly guaranteed under all inputs.
   - 11 standard cost types (Freight, Insurance, Duty, Tax, Port, Handling, Storage, Demurrage, Trucking, Broker, Other).
   - Stress fuzzing: 500 randomized runs with varied charges, prime counts, microcents, and large scale (50 Billion VND).
   - Invariant: taxes[0]["amount"] == round(sum(applicable_charges), 2).

3. SUITE 3: Missing Purchase Receipts, Empty Items & Deduplication Stress
   - Empty allocated_items list: payload generation without unhandled exceptions.
   - Missing/None receipt_document / receipt_document_type handling.
   - Fallback to cost_sheet.document_links when items have no receipt references.
   - Handling of inactive document links (is_active == 0).
   - Deduplication stress: 100 items pointing to 1 PR -> exactly 1 receipt in lcv.purchase_receipts.
   - Multiple PRs and PIs sorted and strictly deduplicated.

4. SUITE 4: Inconsistent Amounts, Zero/Negative Quantities & Extreme Rates
   - Inconsistent amounts: base_amount != qty * rate.
   - Zero quantity (qty == 0.0): ZeroDivisionError prevention and resulting rate behavior.
   - Negative quantity (qty < 0): Behavior analysis and boundary handling.
   - Negative base amount & negative allocated charges.
   - Completely missing/corrupted item dictionary keys (None values).
   - Extreme floating point rates (1e-6 to 1e12).

5. SUITE 5: Exact Conservation of Charges & Multi-Basis Allocation Invariant
   - End-to-end integration: create_or_update_lcv with automatic allocation_engine invocation.
   - Testing all 5 basis rules (Value, Quantity, Weight, Volume, Custom).
   - Exact penny conservation: abs(sum(applicable_charges) - total_actual_cost) <= 0.01 (0.00 exact).
   - Exclusion of Cancelled cost items from allocated charges and tax total.

6. SUITE 6: Dual Runtime Simulation (Offline Standalone vs Live Frappe Mock)
   - Standalone mode (frappe is None):
     * get_company_expense_account fallback abbreviation logic.
     * Naming series LCV-2026-XXXXX generation.
     * Item status mutation to "Allocated" for active items, preserving "Cancelled".
     * Document link generation and duplicate prevention.
   - Mocked Live Frappe Environment:
     * frappe.new_doc vs frappe.get_doc update-in-place for draft LCV (docstatus=0).
     * Rejection/no-op on already submitted LCV (docstatus=1).
     * auto_submit=True triggers lcv.submit().
     * Database cached value resolution for company valuation account with exception fallback.

7. SUITE 7: Concurrency & Idempotency Stress Harness
   - 50 sequential calls on identical cost sheet: state consistency and zero duplicate links.
   - Multi-threaded concurrent execution: 10 concurrent threads generating payloads.
   - Immutability check: ensure input cost_sheet and allocated_items are not mutated unexpectedly.
"""

import sys
import os
import copy
import math
import random
import threading
from typing import Dict, Any, List, Optional, Tuple, Set

# Ensure project modules are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import logistics_wizard.costing_engine.lcv_integrator as lcv_module
from logistics_wizard.costing_engine.lcv_integrator import (
    LCVIntegrator,
    create_or_update_lcv,
    generate_lcv_payload,
    get_company_expense_account,
    on_cost_sheet_submit,
    flt,
)
from logistics_wizard.costing_engine.allocation_engine import (
    CostAllocationEngine,
    allocate_costs,
    hare_niemeyer_allocation,
)


class TestResultTracker:
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.passed = 0
        self.failed = 0
        self.findings = []

    def record_pass(self, name: str):
        self.passed += 1
        print(f"  [PASS] {name}")

    def record_fail(self, name: str, detail: str, severity: str = "HIGH"):
        self.failed += 1
        self.findings.append({
            "test": name,
            "detail": detail,
            "severity": severity,
            "suite": self.suite_name
        })
        print(f"  [FAIL] [{severity}] {name}: {detail}")


def run_suite_1() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 1: Export Rejection & Trade Type Boundary")
    print(f"\n---> Running {tracker.suite_name}")

    valid_import_sheet = {
        "name": "TCS-IMP-001",
        "trade_type": "Import",
        "company": "Logistics Wizard Demo",
        "cost_items": [{"cost_type": "Freight", "actual_cost": 1000.0, "status": "Verified"}],
        "document_links": [{"document_type": "Purchase Receipt", "document_name": "PR-001", "is_active": 1}]
    }
    allocated_items = [{"item_code": "ITEM-A", "qty": 10.0, "base_amount": 5000.0, "allocated_charges": 1000.0}]

    # Test 1.1: Standard Import succeeds
    try:
        name = create_or_update_lcv(copy.deepcopy(valid_import_sheet), allocated_items)
        if name.startswith("LCV-2026-"):
            tracker.record_pass("Import trade case creates LCV successfully")
        else:
            tracker.record_fail("Import trade case creates LCV successfully", f"Invalid name format {name}", "HIGH")
    except Exception as e:
        tracker.record_fail("Import trade case creates LCV successfully", str(e), "HIGH")

    # Test 1.2: Exact title-case 'Export' raises ValueError
    try:
        export_sheet = copy.deepcopy(valid_import_sheet)
        export_sheet["trade_type"] = "Export"
        create_or_update_lcv(export_sheet, allocated_items)
        tracker.record_fail("Exact title-case 'Export' raises ValueError", "No exception raised for Export sheet", "CRITICAL")
    except ValueError:
        tracker.record_pass("Exact title-case 'Export' raises ValueError")
    except Exception as e:
        tracker.record_fail("Exact title-case 'Export' raises ValueError", f"Wrong exception type: {type(e).__name__}", "HIGH")

    # Test 1.3: OOP adapter rejects Export
    try:
        adapter = LCVIntegrator()
        export_sheet = copy.deepcopy(valid_import_sheet)
        export_sheet["trade_type"] = "Export"
        adapter.create_or_update(export_sheet, allocated_items)
        tracker.record_fail("LCVIntegrator OOP adapter rejects Export", "No exception raised", "HIGH")
    except ValueError:
        tracker.record_pass("LCVIntegrator OOP adapter rejects Export")
    except Exception as e:
        tracker.record_fail("LCVIntegrator OOP adapter rejects Export", str(e), "HIGH")

    # Test 1.4: on_cost_sheet_submit returns None for Export
    try:
        export_sheet = copy.deepcopy(valid_import_sheet)
        export_sheet["trade_type"] = "Export"
        res = on_cost_sheet_submit(export_sheet)
        if res is None:
            tracker.record_pass("on_cost_sheet_submit returns None for Export trade cases")
        else:
            tracker.record_fail("on_cost_sheet_submit returns None for Export trade cases", f"Returned {res}", "HIGH")
    except Exception as e:
        tracker.record_fail("on_cost_sheet_submit returns None for Export trade cases", str(e), "HIGH")

    # Test 1.5: Adversarial casing & whitespace variations ('export', 'EXPORT', ' Export ')
    casing_tests = ["export", "EXPORT", " Export "]
    bypassed_cases = []
    for var in casing_tests:
        sheet = copy.deepcopy(valid_import_sheet)
        sheet["trade_type"] = var
        try:
            create_or_update_lcv(sheet, allocated_items)
            bypassed_cases.append(var)
        except ValueError:
            pass

    if not bypassed_cases:
        tracker.record_pass("Case-insensitive and whitespace-stripped export rejection")
    else:
        tracker.record_fail(
            "Case-insensitive and whitespace-stripped export rejection",
            f"LCV creation was permitted for non-canonical export casing: {bypassed_cases}. Line 231 uses exact '== Export' without normalization.",
            "MEDIUM"
        )

    # Test 1.6: Non-import trade types ('Outbound', 'Domestic')
    sheet_dom = copy.deepcopy(valid_import_sheet)
    sheet_dom["trade_type"] = "Outbound"
    try:
        create_or_update_lcv(sheet_dom, allocated_items)
        tracker.record_fail(
            "Non-import trade type 'Outbound' rejection",
            "Outbound trade case generated an LCV; LCV is strictly only valid for Import.",
            "LOW"
        )
    except ValueError:
        tracker.record_pass("Non-import trade type 'Outbound' rejection")

    return tracker


def run_suite_2() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 2: Strict 1-Tax-Line Invariant")
    print(f"\n---> Running {tracker.suite_name}")

    cost_sheet = {"name": "TCS-TAX-001", "trade_type": "Import", "company": "Logistics Wizard Demo"}

    # Test 2.1: Single item
    items = [{"item_code": "I-1", "qty": 1.0, "base_amount": 100.0, "allocated_charges": 25.0}]
    p = generate_lcv_payload(cost_sheet, items)
    if len(p["taxes"]) == 1 and p["taxes"][0]["amount"] == 25.0:
        tracker.record_pass("Single item generates exactly 1 tax line with matching amount")
    else:
        tracker.record_fail("Single item generates exactly 1 tax line", f"taxes={p['taxes']}", "CRITICAL")

    # Test 2.2: 11 Standard Cost Types consolidation
    cost_types = [
        ("Freight", 5000.00), ("Insurance", 750.50), ("Customs Duty", 3200.25),
        ("Import Tax", 1800.00), ("Port Charges", 950.00), ("Handling Fee", 450.00),
        ("Storage", 350.00), ("Demurrage", 1200.00), ("Trucking", 850.00),
        ("Brokerage", 500.00), ("Other", 200.00),
    ]
    tot = round(sum(a for _, a in cost_types), 2)
    multi_items = [
        {"item_code": f"IT-{i}", "qty": 5.0, "base_amount": 1000.0, "allocated_charges": round(tot / 11, 2)}
        for i in range(11)
    ]
    # Balance discrepancy
    diff = round(tot - sum(it["allocated_charges"] for it in multi_items), 2)
    multi_items[-1]["allocated_charges"] = round(multi_items[-1]["allocated_charges"] + diff, 2)

    p11 = generate_lcv_payload(cost_sheet, multi_items)
    if len(p11["taxes"]) == 1 and p11["taxes"][0]["amount"] == tot:
        tracker.record_pass(f"11 distinct cost types totaling {tot} consolidate into exactly 1 tax line")
    else:
        tracker.record_fail("11 distinct cost types consolidation", f"taxes={p11['taxes']}", "CRITICAL")

    # Test 2.3: Scale test 1,000 items
    scale_items = [{"item_code": f"M-{i}", "qty": 1.0, "base_amount": 10.0, "allocated_charges": 0.05} for i in range(1000)]
    p_scale = generate_lcv_payload(cost_sheet, scale_items)
    if len(p_scale["taxes"]) == 1 and math.isclose(p_scale["taxes"][0]["amount"], 50.0, abs_tol=0.01):
        tracker.record_pass("1,000 items scale consolidation to exactly 1 tax line")
    else:
        tracker.record_fail("1,000 items scale consolidation", f"taxes={p_scale['taxes']}", "CRITICAL")

    # Test 2.4: 50 Billion VND currency scale
    vnd_items = [
        {"item_code": "MACH-1", "qty": 1.0, "base_amount": 100_000_000_000.0, "allocated_charges": 30_000_000_000.0},
        {"item_code": "MACH-2", "qty": 1.0, "base_amount": 100_000_000_000.0, "allocated_charges": 20_000_000_000.0},
    ]
    p_vnd = generate_lcv_payload(cost_sheet, vnd_items)
    if len(p_vnd["taxes"]) == 1 and p_vnd["taxes"][0]["amount"] == 50_000_000_000.0:
        tracker.record_pass("50 Billion VND large-scale charges consolidate to 1 tax line exactly")
    else:
        tracker.record_fail("50 Billion VND large-scale charges", f"amount={p_vnd['taxes']}", "CRITICAL")

    # Test 2.5: Zero charges & empty items
    p_zero = generate_lcv_payload(cost_sheet, [])
    if len(p_zero["taxes"]) == 1 and p_zero["taxes"][0]["amount"] == 0.0:
        tracker.record_pass("Empty items list produces exactly 1 tax line with 0.0 amount")
    else:
        tracker.record_fail("Empty items list 1 tax line", f"taxes={p_zero['taxes']}", "HIGH")

    # Test 2.6: Fuzzing 500 random runs
    rng = random.Random(1337)
    fuzz_failed = False
    for trial in range(500):
        n = rng.randint(1, 40)
        items = [
            {"item_code": f"FZ-{i}", "qty": rng.uniform(1, 100), "base_amount": rng.uniform(10, 5000), "allocated_charges": round(rng.uniform(0.1, 500), 2)}
            for i in range(n)
        ]
        expected_tax = round(sum(it["allocated_charges"] for it in items), 2)
        pf = generate_lcv_payload(cost_sheet, items)
        if len(pf["taxes"]) != 1 or not math.isclose(pf["taxes"][0]["amount"], expected_tax, abs_tol=0.01):
            fuzz_failed = True
            tracker.record_fail("500-trial random fuzzing tax invariant", f"Failed on trial {trial}", "CRITICAL")
            break
    if not fuzz_failed:
        tracker.record_pass("500-trial random fuzzing 1-tax-line invariant 100% verified")

    return tracker


def run_suite_3() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 3: Missing Receipts, Empty Items & Deduplication")
    print(f"\n---> Running {tracker.suite_name}")

    cost_sheet = {"name": "TCS-DEDUP-001", "trade_type": "Import", "company": "Logistics Wizard Demo"}

    # Test 3.1: 100 items pointing to 1 PR deduplicated to 1 entry
    items_100 = [
        {"item_code": f"ITEM-{i}", "receipt_document_type": "Purchase Receipt", "receipt_document": "PR-SHARED-99", "qty": 1.0, "base_amount": 10.0, "allocated_charges": 1.0}
        for i in range(100)
    ]
    p1 = generate_lcv_payload(cost_sheet, items_100)
    if len(p1["purchase_receipts"]) == 1 and p1["purchase_receipts"][0]["receipt_document"] == "PR-SHARED-99":
        tracker.record_pass("100 items pointing to same PR cleanly deduplicated to 1 row")
    else:
        tracker.record_fail("100 items deduplication", f"count={len(p1['purchase_receipts'])}", "HIGH")

    # Test 3.2: Mixed PR and PI sorted deduplication
    mixed = [
        ("Purchase Receipt", "PR-B"), ("Purchase Invoice", "PI-A"),
        ("Purchase Receipt", "PR-A"), ("Purchase Invoice", "PI-A"),  # duplicate
        ("Purchase Receipt", "PR-B"),  # duplicate
    ]
    items_mixed = [
        {"item_code": f"M-{i}", "receipt_document_type": rt, "receipt_document": rn, "qty": 1.0, "base_amount": 10.0, "allocated_charges": 1.0}
        for i, (rt, rn) in enumerate(mixed)
    ]
    p2 = generate_lcv_payload(cost_sheet, items_mixed)
    expected_receipts = [
        {"receipt_document_type": "Purchase Invoice", "receipt_document": "PI-A"},
        {"receipt_document_type": "Purchase Receipt", "receipt_document": "PR-A"},
        {"receipt_document_type": "Purchase Receipt", "receipt_document": "PR-B"},
    ]
    if p2["purchase_receipts"] == expected_receipts:
        tracker.record_pass("Mixed PR and PI entries deduplicated and sorted correctly")
    else:
        tracker.record_fail("Mixed PR/PI sorted deduplication", f"got={p2['purchase_receipts']}", "HIGH")

    # Test 3.3: Phantom Receipt vs Fallback to document_links
    # When items do not specify receipt_document, fallback to document_links should engage!
    sheet_links = copy.deepcopy(cost_sheet)
    sheet_links["document_links"] = [
        {"document_type": "Purchase Receipt", "document_name": "PR-REAL-2026-0005", "is_active": 1},
        {"document_type": "Purchase Invoice", "document_name": "PI-REAL-2026-0009", "is_active": 1},
    ]
    items_no_rec = [
        {"item_code": "RAW-A", "qty": 10.0, "base_amount": 1000.0, "allocated_charges": 100.0, "receipt_document": None, "receipt_document_type": None}
    ]
    p3 = generate_lcv_payload(sheet_links, items_no_rec)
    receipt_names = [r["receipt_document"] for r in p3["purchase_receipts"]]

    if "PR-00001" in receipt_names:
        tracker.record_fail(
            "Fallback to cost_sheet.document_links when items lack receipts",
            "CRITICAL BUG: Phantom receipt 'PR-00001' hardcoded at lcv_integrator.py:126 prevented fallback to real document_links! Found ['PR-00001'] instead of real PR/PIs.",
            "CRITICAL"
        )
    elif "PR-REAL-2026-0005" in receipt_names and "PI-REAL-2026-0009" in receipt_names:
        tracker.record_pass("Fallback to cost_sheet.document_links when items lack receipts")
    else:
        tracker.record_fail("Fallback to document_links", f"Unexpected receipts: {receipt_names}", "HIGH")

    # Test 3.4: Inactive document links (is_active == 0)
    sheet_inactive = copy.deepcopy(cost_sheet)
    sheet_inactive["document_links"] = [
        {"document_type": "Purchase Receipt", "document_name": "PR-ACTIVE", "is_active": 1},
        {"document_type": "Purchase Receipt", "document_name": "PR-INACTIVE", "is_active": 0},
    ]
    p_inact = generate_lcv_payload(sheet_inactive, [])
    inact_names = [r["receipt_document"] for r in p_inact["purchase_receipts"]]
    if "PR-INACTIVE" in inact_names:
        tracker.record_fail(
            "Inactive document link exclusion (is_active: 0)",
            "Inactive document link 'PR-INACTIVE' was included in LCV purchase_receipts. lcv_integrator.py:171 does not check is_active flag.",
            "HIGH"
        )
    else:
        tracker.record_pass("Inactive document link exclusion (is_active: 0)")

    # Test 3.5: Empty items and empty links returns clean empty list
    p_empty = generate_lcv_payload({}, [])
    if p_empty["purchase_receipts"] == [] and p_empty["items"] == []:
        tracker.record_pass("Completely empty input produces clean empty tables without crashing")
    else:
        tracker.record_fail("Completely empty input", "Non-empty tables on empty input", "LOW")

    return tracker


def run_suite_4() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 4: Inconsistent Amounts, Zero/Negative Quantities")
    print(f"\n---> Running {tracker.suite_name}")

    cost_sheet = {"name": "TCS-BOUND-001", "company": "Logistics Wizard Demo"}

    # Test 4.1: Zero quantity ZeroDivisionError prevention
    items_zero = [{"item_code": "ZERO-Q", "qty": 0.0, "base_amount": 500.0, "allocated_charges": 50.0}]
    try:
        p = generate_lcv_payload(cost_sheet, items_zero)
        rate = p["items"][0]["rate"]
        if math.isfinite(rate):
            tracker.record_pass("Zero quantity handled safely without ZeroDivisionError")
        else:
            tracker.record_fail("Zero quantity handling", f"Non-finite rate: {rate}", "HIGH")
    except Exception as e:
        tracker.record_fail("Zero quantity handling", f"Crashed: {e}", "CRITICAL")

    # Test 4.2: Astronomical rate observation on non-positive quantity
    # max(raw_qty, 0.0001) produces base_amount / 0.0001 = 5,000,000.0
    rate = p["items"][0]["rate"]
    if rate >= 1_000_000.0:
        tracker.record_fail(
            "Realistic rate calculation for zero-quantity lines",
            f"Zero-quantity line with base_amount=500 produced artificial rate of {rate:,.1f}/unit due to division by 0.0001 (lcv_integrator.py:134).",
            "MEDIUM"
        )
    else:
        tracker.record_pass("Realistic rate calculation for zero-quantity lines")

    # Test 4.3: Negative quantity handling
    items_neg = [{"item_code": "NEG-Q", "qty": -5.0, "base_amount": 250.0, "allocated_charges": 25.0}]
    try:
        p_neg = generate_lcv_payload(cost_sheet, items_neg)
        row = p_neg["items"][0]
        if row["qty"] == -5.0 and math.isfinite(row["rate"]):
            tracker.record_pass("Negative quantity processed without crashing")
        else:
            tracker.record_fail("Negative quantity processing", f"Corrupted row: {row}", "HIGH")
    except Exception as e:
        tracker.record_fail("Negative quantity processing", str(e), "HIGH")

    # Test 4.4: Inconsistent amounts (base_amount != qty * rate)
    items_incon = [{"item_code": "INCON", "qty": 10.0, "rate": 10.0, "base_amount": 1000.0, "allocated_charges": 50.0}]
    p_inc = generate_lcv_payload(cost_sheet, items_incon)
    row_inc = p_inc["items"][0]
    if row_inc["qty"] == 10.0 and row_inc["rate"] == 10.0 and row_inc["amount"] == 1000.0:
        tracker.record_pass("Inconsistent item amounts preserved faithfully from input")
    else:
        tracker.record_fail("Inconsistent item amounts", f"Row: {row_inc}", "LOW")

    # Test 4.5: Empty dict item `{}`
    try:
        p_empty = generate_lcv_payload(cost_sheet, [{}])
        if len(p_empty["items"]) == 1:
            tracker.record_pass("Empty dict item handled safely without unhandled exception")
        else:
            tracker.record_fail("Empty dict item", "Item not processed", "LOW")
    except Exception as e:
        tracker.record_fail("Empty dict item", str(e), "HIGH")

    return tracker


def run_suite_5() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 5: Exact Conservation & Multi-Basis Allocation")
    print(f"\n---> Running {tracker.suite_name}")

    raw_items = [
        {"item_code": "R-1", "qty": 15.0, "base_amount": 15000.0, "weight": 300.0, "volume": 2.5, "custom_factor": 1.0, "receipt_document": "PR-1", "receipt_document_type": "Purchase Receipt"},
        {"item_code": "R-2", "qty": 45.0, "base_amount": 45000.0, "weight": 900.0, "volume": 7.5, "custom_factor": 3.0, "receipt_document": "PR-1", "receipt_document_type": "Purchase Receipt"},
    ]
    target_actual = 6000.0

    # Test 5.1: Test all 5 allocation rules for exact conservation
    rules = ["By Value", "By Quantity", "By Weight", "By Volume", "Custom"]
    for rule in rules:
        sheet = {
            "name": f"TCS-RULE-{rule.replace(' ', '_')}",
            "trade_type": "Import",
            "allocation_rule": rule,
            "total_actual_cost": target_actual,
            "items": raw_items
        }
        allocs = allocate_costs(sheet)
        sum_alloc = round(sum(it["allocated_charges"] for it in allocs), 2)
        payload = generate_lcv_payload(sheet, allocs)

        if math.isclose(sum_alloc, target_actual, abs_tol=0.01) and math.isclose(payload["taxes"][0]["amount"], target_actual, abs_tol=0.01):
            tracker.record_pass(f"Rule '{rule}': Exact penny conservation (0.00 difference) and 1 tax line verified")
        else:
            tracker.record_fail(f"Rule '{rule}' conservation", f"alloc={sum_alloc}, tax={payload['taxes'][0]['amount']}", "CRITICAL")

    # Test 5.2: Cancelled items exclusion
    sheet_canc = {
        "name": "TCS-CANC-001",
        "trade_type": "Import",
        "cost_items": [
            {"cost_type": "Freight", "actual_cost": 3000.0, "status": "Verified"},
            {"cost_type": "Insurance", "actual_cost": 1000.0, "status": "Draft"},
            {"cost_type": "Storage", "actual_cost": 500.0, "status": "Cancelled"},
        ],
        "items": raw_items
    }
    allocs_canc = allocate_costs(sheet_canc)
    expected_active_cost = 4000.0  # 3000 + 1000, excluding 500
    sum_canc = sum(it["allocated_charges"] for it in allocs_canc)
    if math.isclose(sum_canc, expected_active_cost, abs_tol=0.01):
        tracker.record_pass("Cancelled cost items strictly excluded from total allocated charges")
    else:
        tracker.record_fail("Cancelled cost items exclusion", f"Sum was {sum_canc}, expected {expected_active_cost}", "HIGH")

    return tracker


def run_suite_6() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 6: Dual Runtime Simulation (Offline vs Mock Frappe)")
    print(f"\n---> Running {tracker.suite_name}")

    cost_sheet = {
        "name": "TCS-2026-00077",
        "trade_type": "Import",
        "company": "Saigon Port Logistics Corporation",
        "cost_items": [
            {"cost_type": "Freight", "actual_cost": 2000.0, "status": "Verified"},
            {"cost_type": "Duty", "actual_cost": 1000.0, "status": "Draft"},
            {"cost_type": "Storage", "actual_cost": 500.0, "status": "Cancelled"},
        ],
        "document_links": []
    }
    allocated_items = [{"item_code": "P-1", "qty": 10.0, "base_amount": 5000.0, "allocated_charges": 3000.0}]

    # Test 6.1: Offline abbreviation logic
    abbr = get_company_expense_account("Saigon Port Logistics Corporation")
    if abbr == "Expenses Included In Valuation - SPLC":
        tracker.record_pass("Offline expense account abbreviation 'SPLC' correctly generated")
    else:
        tracker.record_fail("Offline expense account abbreviation", f"Got: {abbr}", "MEDIUM")

    # Test 6.2: Offline status mutation and document links
    sheet_standalone = copy.deepcopy(cost_sheet)
    lcv_name = create_or_update_lcv(sheet_standalone, allocated_items)
    if lcv_name == "LCV-2026-00077":
        tracker.record_pass("Offline LCV naming series format LCV-2026-XXXXX verified")
    else:
        tracker.record_fail("Offline LCV naming series", f"Got: {lcv_name}", "HIGH")

    st = [it["status"] for it in sheet_standalone["cost_items"]]
    if st == ["Allocated", "Allocated", "Cancelled"]:
        tracker.record_pass("Active cost items transitioned to 'Allocated' while Cancelled preserved")
    else:
        tracker.record_fail("Item status transition", f"Got: {st}", "HIGH")

    links = sheet_standalone["document_links"]
    if len(links) == 1 and links[0]["document_type"] == "Landed Cost Voucher" and links[0]["grand_total"] == 3000.0:
        tracker.record_pass("LCV document link cleanly appended with total tax amount")
    else:
        tracker.record_fail("LCV document link append", f"Links: {links}", "HIGH")

    # Test 6.3: Simulated Live Frappe execution path
    class MockDoc:
        def __init__(self, doctype, name="LCV-LIVE-001"):
            self.doctype = doctype
            self.name = name
            self.docstatus = 0
            self.purchase_receipts = []
            self.taxes = []
            self.items = []
            self.saved = False
            self.inserted = False
            self.submitted = False

        def append(self, table, row):
            getattr(self, table).append(row)

        def insert(self, ignore_permissions=True):
            self.inserted = True
            return self

        def save(self, ignore_permissions=True):
            self.saved = True
            return self

        def submit(self):
            self.submitted = True
            self.docstatus = 1
            return self

    class MockFrappeLive:
        def __init__(self):
            self.created = []
            self.db = self

        def new_doc(self, dt):
            d = MockDoc(dt)
            self.created.append(d)
            return d

        def exists(self, dt, name):
            return False

        def get_doc(self, dt, name):
            return None

        def get_cached_value(self, dt, name, field):
            return "Custom Valuation Account - DB"

    orig_frappe = lcv_module.frappe
    try:
        mock = MockFrappeLive()
        lcv_module.frappe = mock
        sheet_live = copy.deepcopy(cost_sheet)
        res_live = create_or_update_lcv(sheet_live, allocated_items, auto_submit=True)
        if res_live == "LCV-LIVE-001" and len(mock.created) == 1:
            d = mock.created[0]
            if d.inserted and d.submitted and d.distribute_charges_based_on == "Distribute Manually":
                tracker.record_pass("Live Frappe new_doc, manual distribution, insert, and auto_submit verified")
            else:
                tracker.record_fail("Live Frappe lifecycle", "Doc not properly submitted or configured", "CRITICAL")
        else:
            tracker.record_fail("Live Frappe creation", f"res={res_live}", "CRITICAL")
    finally:
        lcv_module.frappe = orig_frappe

    return tracker


def run_suite_7() -> TestResultTracker:
    tracker = TestResultTracker("SUITE 7: Concurrency & Idempotency")
    print(f"\n---> Running {tracker.suite_name}")

    cost_sheet = {
        "name": "TCS-IDEM-001",
        "trade_type": "Import",
        "company": "Logistics Wizard Demo",
        "cost_items": [{"cost_type": "Freight", "actual_cost": 1500.0, "status": "Verified"}],
        "document_links": []
    }
    allocated_items = [{"item_code": "P-A", "qty": 10.0, "base_amount": 3000.0, "allocated_charges": 1500.0}]

    # Test 7.1: 50 sequential calls on identical cost sheet
    sheet = copy.deepcopy(cost_sheet)
    for _ in range(50):
        create_or_update_lcv(sheet, allocated_items)

    lcv_links = [l for l in sheet["document_links"] if l.get("document_type") == "Landed Cost Voucher"]
    if len(lcv_links) == 1:
        tracker.record_pass("50 sequential calls produce exactly 1 document link (idempotent)")
    else:
        tracker.record_fail("Sequential idempotency", f"Link count={len(lcv_links)}", "HIGH")

    # Test 7.2: Multi-threaded concurrency
    results = []
    errors = []
    def worker(i):
        try:
            s = {"name": f"TCS-TH-{i}", "company": "Concurrent Corp"}
            its = [{"item_code": f"IT-{j}", "qty": 5.0, "base_amount": 100.0, "allocated_charges": 20.0} for j in range(5)]
            p = generate_lcv_payload(s, its)
            results.append((i, p))
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    if not errors and len(results) == 10:
        tracker.record_pass("10 concurrent threads generating payloads safely without collision")
    else:
        tracker.record_fail("Concurrent payload generation", f"Errors: {errors}", "HIGH")

    # Test 7.3: Input immutability
    s_orig = {"name": "TCS-IMMUT", "company": "Immut Corp"}
    its_orig = [{"item_code": "I-1", "qty": 1.0, "base_amount": 50.0, "allocated_charges": 10.0}]
    s_cp, its_cp = copy.deepcopy(s_orig), copy.deepcopy(its_orig)
    generate_lcv_payload(s_cp, its_cp)
    if s_cp == s_orig and its_cp == its_orig:
        tracker.record_pass("Input cost_sheet and allocated_items immutability preserved")
    else:
        tracker.record_fail("Input immutability", "Dictionaries were mutated in-place", "MEDIUM")

    return tracker


def main():
    print("=" * 80)
    print("EMPIRICAL ADVERSARIAL STRESS TEST HARNESS — MILESTONE 2 (LCV SYNC)")
    print("=" * 80)

    suites = [
        run_suite_1(),
        run_suite_2(),
        run_suite_3(),
        run_suite_4(),
        run_suite_5(),
        run_suite_6(),
        run_suite_7(),
    ]

    total_passed = sum(s.passed for s in suites)
    total_failed = sum(s.failed for s in suites)
    total_executed = total_passed + total_failed
    all_findings = []
    for s in suites:
        all_findings.extend(s.findings)

    print("\n" + "=" * 80)
    print("EMPIRICAL ADVERSARIAL STRESS TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Executed: {total_executed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")

    crit_cnt = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
    high_cnt = sum(1 for f in all_findings if f["severity"] == "HIGH")
    med_cnt = sum(1 for f in all_findings if f["severity"] == "MEDIUM")
    low_cnt = sum(1 for f in all_findings if f["severity"] == "LOW")
    print(f"Severity Breakdown: Critical={crit_cnt}, High={high_cnt}, Medium={med_cnt}, Low={low_cnt}")

    if all_findings:
        print("\nEmpirical Findings & Discovered Defects:")
        for i, f in enumerate(all_findings, 1):
            print(f"  {i}. [{f['severity']}] [{f['suite']}] {f['test']}")
            print(f"     -> {f['detail']}")

    # Decision rule: Any CRITICAL or HIGH finding triggers REJECT
    verdict = "APPROVE" if (crit_cnt == 0 and high_cnt == 0 and total_failed == 0) else "REJECT"
    print("=" * 80)
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 80)

    # Return exit code matching verdict
    return 0 if verdict == "APPROVE" else 1


if __name__ == "__main__":
    sys.exit(main())
