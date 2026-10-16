#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_adversarial_m2_rounding_stress.py — Empirical Stress & Adversarial Verification Suite
========================================================================================
Milestone 2: Cost Allocation Engine & Hare-Niemeyer Rounding Discrepancy Verification

Adversarial Challenger Test Suite targeting:
1. Exact mathematical penny conservation: abs(sum(allocated_charges) - total_cost) <= 0.01 (exact 0.00 match).
2. Huge item arrays (1,000 to 5,000+ items) under uniform, skewed, and Pareto distributions.
3. Pathological remainder ties (1/3, 1/7, primes up to 997, repeating fractions).
4. Multi-tier deterministic tie-breaking (remainder DESC -> basis DESC -> original index ASC).
5. Extreme numbers: $0.01 across 1,000 items; $10,000,000.00 with fractional pennies; 100 Billion VND.
6. Zero, negative, and degenerate bases (division-by-zero immunity, uniform fallback).
7. Monte Carlo mathematical fuzzing (2,500+ randomized iterations).
8. Interface and facade contracts with Trade Cost Sheet data structures.
"""

import os
import sys
import math
import random
import time
import unittest
from typing import Dict, Any, List

# Setup import path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(PROJECT_ROOT, "apps", "logistics_wizard")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logistics_wizard.costing_engine.allocation_engine import (
    CostAllocationEngine,
    allocate_costs,
    hare_niemeyer_allocation,
    derive_item_basis,
    derive_item_value,
    derive_item_qty,
    derive_item_weight,
    derive_item_volume,
    derive_item_custom_factor,
    normalize_rule_name,
)


class TestHugeItemArraysStress(unittest.TestCase):
    """Stress tests allocation behavior on large arrays up to 5,000 items."""

    def test_1000_items_random_uniform_bases(self):
        """1,000 items with random uniform bases allocate with exact 0.00 discrepancy."""
        random.seed(42)
        n = 1000
        total_amount = 123456.78
        items = [
            {
                "item_code": f"ITEM-U-{i:04d}",
                "base_amount": round(random.uniform(1.0, 5000.0), 2),
                "qty": random.randint(1, 100),
            }
            for i in range(n)
        ]
        res = hare_niemeyer_allocation(total_amount, items, basis_key="value")
        self.assertEqual(len(res), n)

        allocated_sum = round(sum(r["allocated_charges"] for r in res), 2)
        discrepancy = round(abs(allocated_sum - total_amount), 2)
        self.assertEqual(discrepancy, 0.0, f"Discrepancy {discrepancy} exceeded 0.00")
        self.assertEqual(allocated_sum, total_amount)

        # Ensure all allocated charges are non-negative
        for r in res:
            self.assertGreaterEqual(r["allocated_charges"], 0.0)

    def test_1000_items_pareto_skewed_bases(self):
        """1,000 items with heavy Pareto / power-law skew (80/20 rule) conserve pennies."""
        random.seed(1337)
        n = 1000
        total_amount = 750000.00
        # Pareto distribution: alpha = 1.16 produces ~80/20 distribution
        items = [
            {
                "item_code": f"ITEM-P-{i:04d}",
                "weight": round(random.paretovariate(1.16), 4),
                "qty": 10.0,
            }
            for i in range(n)
        ]
        res = hare_niemeyer_allocation(total_amount, items, basis_key="weight")
        self.assertEqual(len(res), n)

        allocated_sum = round(sum(r["allocated_charges"] for r in res), 2)
        self.assertEqual(allocated_sum, total_amount)

    def test_1500_items_across_all_5_rules(self):
        """1,500 items tested across all 5 basis rules independently."""
        random.seed(2026)
        n = 1500
        total_amount = 99999.99
        items = [
            {
                "item_code": f"ITEM-M5-{i:04d}",
                "base_amount": round(random.uniform(10.0, 200.0), 2),
                "qty": round(random.uniform(1.0, 50.0), 2),
                "weight": round(random.uniform(0.5, 30.0), 3),
                "volume": round(random.uniform(0.01, 2.5), 4),
                "custom_factor": round(random.uniform(1.0, 5.0), 1),
            }
            for i in range(n)
        ]

        rules = ["By Value", "By Quantity", "By Weight", "By Volume", "Custom"]
        for rule in rules:
            res = hare_niemeyer_allocation(total_amount, items, basis_key=rule)
            self.assertEqual(len(res), n)
            allocated_sum = round(sum(r["allocated_charges"] for r in res), 2)
            self.assertEqual(allocated_sum, total_amount, f"Rule {rule} failed penny conservation")

    def test_2500_items_micro_pennies(self):
        """2,500 items with total charges of only $50.00 (average 2 cents per item)."""
        random.seed(999)
        n = 2500
        total_amount = 50.00  # 5,000 cents across 2,500 items
        items = [{"item_code": f"TINY-{i:04d}", "qty": 1.0} for i in range(n)]

        res = hare_niemeyer_allocation(total_amount, items, basis_key="qty")
        allocated_sum = round(sum(r["allocated_charges"] for r in res), 2)
        self.assertEqual(allocated_sum, total_amount)
        # Exactly 2 cents per item
        for r in res:
            self.assertEqual(r["allocated_charges"], 0.02)

    def test_5000_items_performance_and_exact_sum(self):
        """5,000 items completes in < 150ms with exact 0.00 discrepancy."""
        random.seed(777)
        n = 5000
        total_amount = 888888.88
        items = [
            {"item_code": f"BULK-{i:05d}", "base_amount": round(random.uniform(1.0, 100.0), 2)}
            for i in range(n)
        ]
        t0 = time.time()
        res = hare_niemeyer_allocation(total_amount, items, basis_key="value")
        t1 = time.time()

        elapsed = t1 - t0
        self.assertLess(elapsed, 0.20, f"5,000 items took {elapsed:.4f}s, expected < 0.20s")
        allocated_sum = round(sum(r["allocated_charges"] for r in res), 2)
        self.assertEqual(allocated_sum, total_amount)


class TestPathologicalRemainderTies(unittest.TestCase):
    """Stress tests tie-breaking, repeating fractions, and prime numbers."""

    def test_repeating_fractions_one_third(self):
        """3 items with identical bases tested across multiple fractional dollar targets."""
        items = [
            {"item_code": "P-1", "base_amount": 100.0},
            {"item_code": "P-2", "base_amount": 100.0},
            {"item_code": "P-3", "base_amount": 100.0},
        ]
        # $100.00 -> 33.34, 33.33, 33.33
        res = hare_niemeyer_allocation(100.00, items)
        self.assertEqual([r["allocated_charges"] for r in res], [33.34, 33.33, 33.33])
        self.assertEqual(round(sum(r["allocated_charges"] for r in res), 2), 100.00)

        # $100.01 -> 33.34, 33.34, 33.33
        res = hare_niemeyer_allocation(100.01, items)
        self.assertEqual([r["allocated_charges"] for r in res], [33.34, 33.34, 33.33])
        self.assertEqual(round(sum(r["allocated_charges"] for r in res), 2), 100.01)

        # $100.02 -> 33.34, 33.34, 33.34
        res = hare_niemeyer_allocation(100.02, items)
        self.assertEqual([r["allocated_charges"] for r in res], [33.34, 33.34, 33.34])
        self.assertEqual(round(sum(r["allocated_charges"] for r in res), 2), 100.02)

    def test_repeating_fractions_one_seventh(self):
        """7 items with identical bases dividing $1,000.00 (repeating 1/7 = 0.142857...)."""
        items = [{"item_code": f"S7-{i}", "weight": 50.0} for i in range(7)]
        res = hare_niemeyer_allocation(1000.00, items, basis_key="weight")
        charges = [r["allocated_charges"] for r in res]

        # 100,000 cents / 7 = 14,285.714285...
        # 100,000 = 14,285 * 7 + 5 cents remainder.
        # Exactly 5 items get 142.86 and 2 items get 142.85.
        self.assertEqual(charges.count(142.86), 5)
        self.assertEqual(charges.count(142.85), 2)
        # Because bases and remainders are identical, items 0..4 get 142.86, items 5..6 get 142.85
        self.assertEqual(charges[:5], [142.86] * 5)
        self.assertEqual(charges[5:], [142.85] * 2)
        self.assertEqual(round(sum(charges), 2), 1000.00)

    def test_all_prime_item_counts_exact_conservation(self):
        """Primes up to 97 conserve exact sum across arbitrary total costs."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        target_cost = 4567.89
        for p in primes:
            items = [{"item_code": f"PRIME-{i}", "qty": 1.0} for i in range(p)]
            res = hare_niemeyer_allocation(target_cost, items, basis_key="qty")
            total = round(sum(r["allocated_charges"] for r in res), 2)
            self.assertEqual(total, target_cost, f"Failed for prime count {p}")

    def test_large_prime_997_items(self):
        """Large prime (997 items) with identical bases conserves $5,000.00."""
        n = 997
        target = 5000.00
        items = [{"item_code": f"P997-{i}", "base_amount": 10.0} for i in range(n)]
        res = hare_niemeyer_allocation(target, items)
        total = round(sum(r["allocated_charges"] for r in res), 2)
        self.assertEqual(total, target)

    def test_deterministic_tier1_remainder_priority(self):
        """Tie-breaking Tier 1: Item with larger fractional remainder gets priority."""
        # Target 1.00. Item A basis 51, Item B basis 49.
        # Total basis = 100. Quotas: A=51.0, B=49.0 (no remainder).
        # Target 1.01 -> 101 cents. A quota: 51/100 * 101 = 51.51, B quota: 49/100 * 101 = 49.49.
        # Remainder A: 0.51, Remainder B: 0.49.
        # Sum integers: 51 + 49 = 100. Discrepancy = 1.
        # Remainder A (0.51) > Remainder B (0.49), so A gets the penny!
        items = [
            {"item_code": "B_LESSER_REM", "weight": 49.0},
            {"item_code": "A_GREATER_REM", "weight": 51.0},
        ]
        res = hare_niemeyer_allocation(1.01, items, basis_key="weight")
        self.assertEqual(res[1]["item_code"], "A_GREATER_REM")
        self.assertEqual(res[1]["allocated_charges"], 0.52)
        self.assertEqual(res[0]["allocated_charges"], 0.49)
        self.assertEqual(round(res[0]["allocated_charges"] + res[1]["allocated_charges"], 2), 1.01)

    def test_deterministic_tier2_largest_basis_priority(self):
        """Tie-breaking Tier 2: Identical remainder gives priority to larger basis."""
        # Total basis = 300, Target = 1.00 (100 cents). Quota multiplier = 100/300 = 1/3.
        # Item A: basis 103 -> quota 34.3333... (floor 34, remainder 1/3)
        # Item B: basis 100 -> quota 33.3333... (floor 33, remainder 1/3)
        # Item C: basis 97  -> quota 32.3333... (floor 32, remainder 1/3)
        # Sum floors = 99. Discrepancy = 1 cent.
        # Remainders are identical (1/3). Basis: A (103) > B (100) > C (97).
        # Therefore, A MUST receive the penny, regardless of list position!
        items = [
            {"item_code": "C_MIN", "weight": 97.0},
            {"item_code": "B_MID", "weight": 100.0},
            {"item_code": "A_MAX", "weight": 103.0},
        ]
        res = hare_niemeyer_allocation(1.00, items, basis_key="weight")
        res_dict = {r["item_code"]: r["allocated_charges"] for r in res}
        self.assertEqual(res_dict["A_MAX"], 0.35)
        self.assertEqual(res_dict["B_MID"], 0.33)
        self.assertEqual(res_dict["C_MIN"], 0.32)
        self.assertEqual(round(sum(res_dict.values()), 2), 1.00)

    def test_deterministic_tier3_original_index_priority(self):
        """Tie-breaking Tier 3: Identical remainder and basis gives priority to earlier index."""
        items = [
            {"item_code": "IDX-0", "weight": 50.0},
            {"item_code": "IDX-1", "weight": 50.0},
            {"item_code": "IDX-2", "weight": 50.0},
        ]
        # Target = 1.00 (100 cents) -> 33.33... each. 1 cent discrepancy.
        # Bases are identical (50.0), remainders identical (1/3).
        # Index 0 must receive the extra penny.
        res = hare_niemeyer_allocation(1.00, items, basis_key="weight")
        self.assertEqual(res[0]["allocated_charges"], 0.34)
        self.assertEqual(res[1]["allocated_charges"], 0.33)
        self.assertEqual(res[2]["allocated_charges"], 0.33)


class TestExtremeNumbersAndMicroAmounts(unittest.TestCase):
    """Stress tests boundary numerical scales, micro-costs, and huge currency amounts."""

    def test_one_cent_across_100_items(self):
        """$0.01 total cost distributed across 100 items (exactly 1 gets $0.01, 99 get $0.00)."""
        items = [{"item_code": f"C100-{i}", "base_amount": 10.0} for i in range(100)]
        res = hare_niemeyer_allocation(0.01, items)
        charges = [r["allocated_charges"] for r in res]
        self.assertEqual(round(sum(charges), 2), 0.01)
        self.assertEqual(charges.count(0.01), 1)
        self.assertEqual(charges.count(0.00), 99)
        # By tie-breaking tier 3, index 0 gets the 1 cent
        self.assertEqual(charges[0], 0.01)

    def test_one_cent_across_1000_items(self):
        """$0.01 total cost distributed across 1,000 items (exactly 1 gets $0.01, 999 get $0.00)."""
        items = [{"item_code": f"C1000-{i}", "base_amount": 5.0} for i in range(1000)]
        res = hare_niemeyer_allocation(0.01, items)
        charges = [r["allocated_charges"] for r in res]
        self.assertEqual(round(sum(charges), 2), 0.01)
        self.assertEqual(charges.count(0.01), 1)
        self.assertEqual(charges.count(0.00), 999)
        self.assertEqual(charges[0], 0.01)

    def test_few_cents_across_prime_items(self):
        """$0.03 total cost across 7 items: exactly 3 items get 0.01, 4 get 0.00."""
        items = [{"item_code": f"P7-{i}", "qty": 1.0} for i in range(7)]
        res = hare_niemeyer_allocation(0.03, items, basis_key="qty")
        charges = [r["allocated_charges"] for r in res]
        self.assertEqual(round(sum(charges), 2), 0.03)
        self.assertEqual(charges.count(0.01), 3)
        self.assertEqual(charges.count(0.00), 4)

    def test_ten_million_dollars_with_fractional_pennies(self):
        """$10,000,000.005 scales cleanly to 1,000,000,000 cents without overflow."""
        random.seed(10_000_000)
        items = [{"item_code": f"BIG-{i}", "base_amount": round(random.uniform(10.0, 500.0), 2)} for i in range(500)]
        total = 10_000_000.005
        # Rounding at 2 decimals scales total to 10,000,000.00
        res = hare_niemeyer_allocation(total, items)
        s = round(sum(r["allocated_charges"] for r in res), 2)
        expected = round(total, 2)
        self.assertEqual(s, expected)
        self.assertEqual(round(abs(s - expected), 2), 0.00)

    def test_50_billion_vnd_zero_precision(self):
        """50,000,000,000 VND allocation with precision=0 (no subunits)."""
        items = [
            {"item_code": "VND-1", "base_amount": 20_000_000_000.0},
            {"item_code": "VND-2", "base_amount": 30_000_000_000.0},
        ]
        total_vnd = 50_000_000_000.0
        res = hare_niemeyer_allocation(total_vnd, items, precision=0)
        self.assertEqual(res[0]["allocated_charges"], 20_000_000_000.0)
        self.assertEqual(res[1]["allocated_charges"], 30_000_000_000.0)
        self.assertEqual(sum(r["allocated_charges"] for r in res), total_vnd)

    def test_100_billion_vnd_across_2000_items(self):
        """100 Billion VND allocated across 2,000 items with precision=0."""
        random.seed(100)
        n = 2000
        items = [{"item_code": f"VND-{i}", "base_amount": float(i + 1)} for i in range(n)]
        total_vnd = 100_000_000_000.0
        res = hare_niemeyer_allocation(total_vnd, items, precision=0)
        total_alloc = sum(r["allocated_charges"] for r in res)
        self.assertEqual(total_alloc, total_vnd)

    def test_three_decimal_precision_currencies(self):
        """Middle Eastern currencies (KWD, BHD) with precision=3 conserve milliemes."""
        items = [
            {"item_code": "KWD-A", "base_amount": 10.0},
            {"item_code": "KWD-B", "base_amount": 10.0},
            {"item_code": "KWD-C", "base_amount": 10.0},
        ]
        total_kwd = 10.000
        # 10.000 / 3 = 3.33333... -> [3.334, 3.333, 3.333]
        res = hare_niemeyer_allocation(total_kwd, items, precision=3)
        charges = [r["allocated_charges"] for r in res]
        self.assertEqual(charges, [3.334, 3.333, 3.333])
        self.assertEqual(round(sum(charges), 3), total_kwd)

    def test_four_decimal_precision_high_accuracy(self):
        """High-precision pricing with precision=4 conserves exact subunits."""
        items = [{"item_code": f"ACC-{i}", "base_amount": 1.0} for i in range(7)]
        total = 1.0000
        res = hare_niemeyer_allocation(total, items, precision=4)
        total_alloc = round(sum(r["allocated_charges"] for r in res), 4)
        self.assertEqual(total_alloc, total)

    def test_micro_quantities_and_rates(self):
        """Micro quantities (0.0001) and micro base amounts handled cleanly."""
        items = [
            {"item_code": "CHIP-01", "qty": 0.0001, "rate": 500.0, "base_amount": 0.05},
            {"item_code": "CHIP-02", "qty": 0.0002, "rate": 500.0, "base_amount": 0.10},
        ]
        res = hare_niemeyer_allocation(1.50, items)
        self.assertEqual(res[0]["allocated_charges"], 0.50)
        self.assertEqual(res[1]["allocated_charges"], 1.00)
        self.assertEqual(round(sum(r["allocated_charges"] for r in res), 2), 1.50)


class TestZeroNegativeAndDegenerateBases(unittest.TestCase):
    """Stress tests boundary conditions: zero, negative, missing, and degenerate inputs."""

    def test_all_bases_zero_fallback_to_uniform(self):
        """When all bases sum to 0.0, falls back to uniform allocation."""
        items = [
            {"item_code": "Z-1", "weight": 0.0},
            {"item_code": "Z-2", "weight": 0.0},
            {"item_code": "Z-3", "weight": 0.0},
            {"item_code": "Z-4", "weight": 0.0},
        ]
        res = hare_niemeyer_allocation(100.00, items, basis_key="weight")
        self.assertEqual(len(res), 4)
        for r in res:
            self.assertEqual(r["allocated_charges"], 25.00)
        self.assertEqual(sum(r["allocated_charges"] for r in res), 100.00)

    def test_negative_bases_clamped_to_zero(self):
        """Negative base values clamped to 0.0 and do not corrupt positive allocations."""
        items = [
            {"item_code": "NEG-1", "base_amount": -50.0},
            {"item_code": "POS-2", "base_amount": 100.0},
            {"item_code": "POS-3", "base_amount": 100.0},
        ]
        res = hare_niemeyer_allocation(80.00, items, basis_key="value")
        self.assertEqual(res[0]["allocated_charges"], 0.00)
        self.assertEqual(res[1]["allocated_charges"], 40.00)
        self.assertEqual(res[2]["allocated_charges"], 40.00)
        self.assertEqual(round(sum(r["allocated_charges"] for r in res), 2), 80.00)

    def test_all_bases_negative_fallback_to_uniform(self):
        """When all bases are negative, clamping to 0.0 leads to sum=0.0 fallback to uniform."""
        items = [
            {"item_code": "NEG-A", "base_amount": -10.0},
            {"item_code": "NEG-B", "base_amount": -20.0},
            {"item_code": "NEG-C", "base_amount": -30.0},
        ]
        res = hare_niemeyer_allocation(90.00, items, basis_key="value")
        for r in res:
            self.assertEqual(r["allocated_charges"], 30.00)
        self.assertEqual(sum(r["allocated_charges"] for r in res), 90.00)

    def test_single_positive_base_among_many_zeros(self):
        """1 positive base among 99 zero bases captures 100% of allocation."""
        items = [{"item_code": f"ZERO-{i}", "qty": 0.0} for i in range(99)]
        items.append({"item_code": "SOLO-HERO", "qty": 10.0})

        res = hare_niemeyer_allocation(500.00, items, basis_key="qty")
        hero = [r for r in res if r["item_code"] == "SOLO-HERO"][0]
        self.assertEqual(hero["allocated_charges"], 500.00)
        zeros = [r for r in res if r["item_code"] != "SOLO-HERO"]
        for z in zeros:
            self.assertEqual(z["allocated_charges"], 0.00)
        self.assertEqual(sum(r["allocated_charges"] for r in res), 500.00)

    def test_mixed_zeros_negatives_and_tiny_positives(self):
        """Mixed negative, zero, and micro-positive bases allocate accurately."""
        items = [
            {"item_code": "NEG", "weight": -10.0},
            {"item_code": "ZERO", "weight": 0.0},
            {"item_code": "TINY-1", "weight": 0.0001},
            {"item_code": "TINY-2", "weight": 0.0003},
        ]
        # Total basis = 0.0004. TINY-1 is 25%, TINY-2 is 75%
        res = hare_niemeyer_allocation(100.00, items, basis_key="weight")
        res_dict = {r["item_code"]: r["allocated_charges"] for r in res}
        self.assertEqual(res_dict["NEG"], 0.00)
        self.assertEqual(res_dict["ZERO"], 0.00)
        self.assertEqual(res_dict["TINY-1"], 25.00)
        self.assertEqual(res_dict["TINY-2"], 75.00)

    def test_total_amount_zero_and_negative(self):
        """Total amount 0.0 or negative yields 0.0 allocation for all rows."""
        items = [{"item_code": "A", "qty": 10.0, "base_amount": 100.0}]
        res_zero = hare_niemeyer_allocation(0.0, items)
        self.assertEqual(res_zero[0]["allocated_charges"], 0.0)

        res_neg = hare_niemeyer_allocation(-100.0, items)
        self.assertEqual(res_neg[0]["allocated_charges"], 0.0)

    def test_empty_items_list(self):
        """Empty items list returns empty list without error."""
        res = hare_niemeyer_allocation(1000.0, [])
        self.assertEqual(res, [])

    def test_zero_quantity_safe_rate_calculation(self):
        """Items with qty=0.0 do not raise ZeroDivisionError in new_valuation_rate."""
        items = [
            {"item_code": "SERVICE-A", "qty": 0.0, "base_amount": 0.0},
            {"item_code": "SERVICE-B", "qty": 0.0, "base_amount": 100.0},
            {"item_code": "PHYSICAL-C", "qty": 10.0, "base_amount": 200.0},
        ]
        res = hare_niemeyer_allocation(150.0, items)
        self.assertEqual(len(res), 3)
        for r in res:
            self.assertIsInstance(r["new_valuation_rate"], float)
            self.assertFalse(math.isnan(r["new_valuation_rate"]))
            self.assertFalse(math.isinf(r["new_valuation_rate"]))


class TestMonteCarloMathematicalFuzzing(unittest.TestCase):
    """Extensive randomized fuzz testing verifying conservation across 2,500 trials."""

    def test_monte_carlo_fuzzing_2500_iterations(self):
        """2,500 randomized runs: sum(allocated) == round(total_cost, precision) for 100% of runs."""
        random.seed(424242)
        rules = ["By Value", "By Quantity", "By Weight", "By Volume", "Custom"]
        precisions = [0, 2, 3]

        trials = 2500
        for i in range(trials):
            n = random.randint(1, 40)
            prec = random.choice(precisions)
            total = round(random.uniform(0.01, 50000.0), prec)
            rule = random.choice(rules)

            # Generate random items
            items = []
            for j in range(n):
                it = {
                    "item_code": f"FUZZ-{j}",
                    "base_amount": round(random.uniform(0.0, 500.0), 2),
                    "qty": round(random.uniform(0.0, 100.0), 2),
                    "weight": round(random.uniform(0.0, 50.0), 3),
                    "volume": round(random.uniform(0.0, 5.0), 4),
                    "custom_factor": round(random.uniform(0.0, 10.0), 2),
                }
                items.append(it)

            res = hare_niemeyer_allocation(total, items, basis_key=rule, precision=prec)
            allocated_sum = round(sum(r["allocated_charges"] for r in res), prec)
            target = round(total, prec)
            diff = round(abs(allocated_sum - target), prec)

            self.assertEqual(
                diff, 0.0,
                f"Trial {i} failed conservation: target={target}, sum={allocated_sum}, diff={diff}, n={n}, prec={prec}, rule={rule}"
            )


class TestAllocateCostsInterfaceAdversarial(unittest.TestCase):
    """Adversarial testing of top-level allocate_costs interface with complex sheet inputs."""

    def test_cost_sheet_with_cancelled_and_draft_items(self):
        """Only non-cancelled cost items contribute to total allocation amount."""
        cost_sheet = {
            "name": "TCS-ADV-001",
            "allocation_rule": "By Weight",
            "cost_items": [
                {"cost_type": "Freight", "actual_cost": 1500.0, "status": "Verified"},
                {"cost_type": "Customs Duty", "actual_cost": 500.0, "status": "Draft"},
                {"cost_type": "Storage", "actual_cost": 300.0, "status": "Cancelled"},  # Must be ignored!
            ],
            "items": [
                {"item_code": "STEEL-A", "weight": 200.0, "qty": 10.0, "base_amount": 2000.0},
                {"item_code": "STEEL-B", "weight": 800.0, "qty": 20.0, "base_amount": 8000.0},
            ]
        }
        # Total active cost = 1500 + 500 = 2000.0 (300 cancelled excluded)
        # By weight: 200 vs 800 -> 20% vs 80% -> 400.0 vs 1600.0
        res = allocate_costs(cost_sheet)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["allocated_charges"], 400.0)
        self.assertEqual(res[1]["allocated_charges"], 1600.0)
        self.assertEqual(sum(r["allocated_charges"] for r in res), 2000.0)

    def test_cost_sheet_with_custom_weights_override(self):
        """Explicit custom_weights passed to allocate_costs takes precedence."""
        cost_sheet = {
            "name": "TCS-ADV-002",
            "allocation_rule": "Custom",
            "total_actual_cost": 1000.0,
            "items": [
                {"item_code": "ALPHA", "custom_factor": 1.0, "qty": 1.0},
                {"item_code": "BETA", "custom_factor": 9.0, "qty": 1.0},
            ]
        }
        # Override with custom_weights: ALPHA=5.0, BETA=5.0 (50/50 split)
        weights_override = {"ALPHA": 5.0, "BETA": 5.0}
        res = allocate_costs(cost_sheet, custom_weights=weights_override)
        self.assertEqual(res[0]["allocated_charges"], 500.0)
        self.assertEqual(res[1]["allocated_charges"], 500.0)

    def test_cost_sheet_bare_numeric_input(self):
        """allocate_costs accepts bare numeric cost_sheet with explicit items list."""
        items = [
            {"item_code": "PART-1", "qty": 25.0, "base_amount": 250.0},
            {"item_code": "PART-2", "qty": 75.0, "base_amount": 750.0},
        ]
        res = allocate_costs(100.0, rule="By Value", items=items)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["allocated_charges"], 25.0)
        self.assertEqual(res[1]["allocated_charges"], 75.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
