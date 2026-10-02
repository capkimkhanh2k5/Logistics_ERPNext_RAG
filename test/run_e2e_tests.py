#!/usr/bin/env python3
"""
run_e2e_tests.py — Auxiliary Test Runner CLI for Shipment Tracking E2E Suite
=============================================================================
Usage:
    python3 test/run_e2e_tests.py              # Runs all 4 Tiers
    python3 test/run_e2e_tests.py --tier 1     # Runs Tier 1 only (Feature Coverage)
    python3 test/run_e2e_tests.py --tier 2     # Runs Tier 2 only (Boundary & Edge Cases)
    python3 test/run_e2e_tests.py --tier 3     # Runs Tier 3 only (Cross-Feature Combinations)
    python3 test/run_e2e_tests.py --tier 4     # Runs Tier 4 only (Master Simulation IMP-2026-001)
"""

import sys
import os
import argparse
import unittest
import time

# Ensure test directory is in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

from test_shipment_tracking_e2e import (
    TestTier1FeatureCoverage,
    TestTier2BoundaryCornerCases,
    TestTier3CrossFeatureCombinations,
    TestTier4RealWorldSimulation,
)


def main():
    parser = argparse.ArgumentParser(description="Logistics Wizard E2E Test Suite Runner")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run specific tier (1, 2, 3, or 4)")
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Verbose test execution")
    args = parser.parse_args()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    tier_map = {
        1: ("Tier 1: Feature Coverage (R1, R2, R3, R4)", TestTier1FeatureCoverage),
        2: ("Tier 2: Boundary & Corner Cases", TestTier2BoundaryCornerCases),
        3: ("Tier 3: Cross-Feature Combinations", TestTier3CrossFeatureCombinations),
        4: ("Tier 4: Real-World Master Simulation (IMP-2026-001)", TestTier4RealWorldSimulation),
    }

    if args.tier:
        name, test_cls = tier_map[args.tier]
        print(f"\n=======================================================")
        print(f" EXECUTING: {name}")
        print(f"=======================================================")
        suite.addTests(loader.loadTestsFromTestCase(test_cls))
    else:
        print("\n================================================================================")
        print(" EXECUTING ALL 4 TIERS: MASTER END-TO-END VERIFICATION SUITE")
        print("================================================================================")
        for _, (_, test_cls) in tier_map.items():
            suite.addTests(loader.loadTestsFromTestCase(test_cls))

    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    t0 = time.time()
    result = runner.run(suite)
    elapsed = time.time() - t0

    print("\n" + "=" * 80)
    print(" SUMMARY")
    print("=" * 80)
    print(f" Tests Run : {result.testsRun}")
    print(f" Passed    : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Failed    : {len(result.failures)}")
    print(f" Errors    : {len(result.errors)}")
    print(f" Time      : {elapsed:.3f}s")
    print("=" * 80)

    if result.wasSuccessful():
        print(" STATUS: ALL TESTS PASSED [100%]\n")
        return 0
    else:
        print(" STATUS: FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
