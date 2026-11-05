#!/usr/bin/env python3
"""
Vyasa Mahabharata Android Application - Opaque-Box E2E Test Runner.
Executes 4 Systematic Testing Tiers covering all 21 Features:
  - Tier 1: Feature Coverage (>=105 tests)
  - Tier 2: Boundary & Corner Cases (>=105 tests)
  - Tier 3: Cross-Feature Interactions & Combinatorial Coverage (>=16 tests)
  - Tier 4: Real-World Application User Scenarios (>=16 tests)
Total: 246 Executable Tests (exceeds requirement >= 242).
"""

import argparse
import io
import json
import os
import sys
import time
import unittest
from typing import Dict, List, Optional, Any

# Ensure tests/e2e directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tier1_feature_coverage import Tier1FeatureCoverageTests
from tier2_boundary_corner import Tier2BoundaryCornerTests
from tier3_cross_feature import Tier3CrossFeatureTests
from tier4_real_world import Tier4RealWorldScenarioTests


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GRAY = "\033[90m"


def format_header(title: str) -> str:
    line = "=" * 78
    return f"\n{Color.CYAN}{Color.BOLD}{line}\n  {title}\n{line}{Color.RESET}\n"


def run_test_suite(
    suite: unittest.TestSuite,
    verbose: bool = False,
    failfast: bool = False
) -> Tuple[unittest.TestResult, float]:
    """Runs a unittest TestSuite and returns (result, elapsed_seconds)."""
    stream = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2 if verbose else 1,
        failfast=failfast
    )
    t0 = time.perf_counter()
    result = runner.run(suite)
    elapsed = time.perf_counter() - t0
    return result, elapsed


def build_filtered_suite(
    test_class: type,
    feature_num: Optional[int] = None
) -> unittest.TestSuite:
    """Builds a test suite from test_class, optionally filtering by feature number."""
    loader = unittest.TestLoader()
    all_names = loader.getTestCaseNames(test_class)
    
    if feature_num is not None:
        target_prefix = f"test_f{feature_num:02d}"
        filtered_names = [n for n in all_names if n.startswith(target_prefix)]
        suite = unittest.TestSuite()
        for name in filtered_names:
            suite.addTest(test_class(name))
        return suite
    else:
        return loader.loadTestsFromTestCase(test_class)


def main():
    parser = argparse.ArgumentParser(
        description="Vyasa Mahabharata Android App - Opaque-Box E2E Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tests/e2e/test_runner.py                  # Run complete test suite (all tiers)
  python3 tests/e2e/test_runner.py --tier 1         # Run only Tier 1 (Feature Coverage)
  python3 tests/e2e/test_runner.py --tier 2         # Run only Tier 2 (Boundary & Corner Cases)
  python3 tests/e2e/test_runner.py --tier 3         # Run only Tier 3 (Cross-Feature Interactions)
  python3 tests/e2e/test_runner.py --tier 4         # Run only Tier 4 (Real-World Scenarios)
  python3 tests/e2e/test_runner.py --feature 3      # Run tests for Feature 3 across tiers
  python3 tests/e2e/test_runner.py -v               # Verbose output with test names
  python3 tests/e2e/test_runner.py --json out.json  # Export test execution report as JSON
  python3 tests/e2e/test_runner.py --failfast       # Stop immediately on first failure
        """
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run only tests from the specified tier (1, 2, 3, or 4)"
    )
    parser.add_argument(
        "--feature", "-f",
        type=int,
        help="Filter tests by feature number (1 through 21)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print verbose test execution details"
    )
    parser.add_argument(
        "--failfast",
        action="store_true",
        help="Stop on first test error or failure"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="Output structured test results as JSON to the specified file"
    )

    args = parser.parse_args()

    # Validate feature number if specified
    if args.feature is not None and not (1 <= args.feature <= 21):
        print(f"{Color.RED}Error: --feature must be between 1 and 21 (received {args.feature}){Color.RESET}")
        sys.exit(1)

    print(format_header("🕉️  VYASA MAHABHARATA ANDROID APP — E2E TEST RUNNER  🕉️"))
    print(f"  Target Features: 21 Features (M1 to M5)")
    print(f"  Tiers: 1 (Feature), 2 (Boundary), 3 (Combinatorial), 4 (Real-World)")
    print(f"  Mode: Opaque-Box Black-Box System Verification")
    if args.tier:
        print(f"  Filtered to Tier: {args.tier}")
    if args.feature:
        print(f"  Filtered to Feature: F{args.feature:02d}")
    print(f"{Color.CYAN}{'=' * 78}{Color.RESET}\n")

    tier_specs = [
        (1, "Tier 1: Feature Coverage", Tier1FeatureCoverageTests),
        (2, "Tier 2: Boundary & Corner Cases", Tier2BoundaryCornerTests),
        (3, "Tier 3: Cross-Feature Interactions", Tier3CrossFeatureTests),
        (4, "Tier 4: Real-World Scenarios", Tier4RealWorldScenarioTests),
    ]

    selected_tiers = [t for t in tier_specs if (args.tier is None or t[0] == args.tier)]
    if args.feature is not None:
        # Tier 3 & Tier 4 test cross-cutting interactions, only Tiers 1 and 2 are strictly partitioned by feature prefix
        selected_tiers = [t for t in selected_tiers if t[0] in (1, 2)]

    tier_results = []
    total_tests_run = 0
    total_failures = 0
    total_errors = 0
    total_duration = 0.0

    overall_start_time = time.perf_counter()

    for tier_id, tier_name, test_class in selected_tiers:
        suite = build_filtered_suite(test_class, feature_num=args.feature)
        count = suite.countTestCases()
        
        if count == 0:
            continue
            
        print(f"{Color.BOLD}Running {tier_name} ({count} test cases)...{Color.RESET}")
        
        t0 = time.perf_counter()
        result, elapsed = run_test_suite(suite, verbose=args.verbose, failfast=args.failfast)
        t_elapsed = time.perf_counter() - t0
        
        passed = result.testsRun - len(result.failures) - len(result.errors)
        status_color = Color.GREEN if (len(result.failures) == 0 and len(result.errors) == 0) else Color.RED
        status_text = "PASSED" if (len(result.failures) == 0 and len(result.errors) == 0) else "FAILED"
        
        print(f"  {status_color}[{status_text}]{Color.RESET} {passed}/{result.testsRun} passed in {t_elapsed:.3f}s")
        
        if result.failures:
            for test_case, trace in result.failures:
                print(f"    {Color.RED}FAIL:{Color.RESET} {test_case}")
                print(f"{Color.GRAY}{trace.strip()}{Color.RESET}\n")
        if result.errors:
            for test_case, trace in result.errors:
                print(f"    {Color.RED}ERROR:{Color.RESET} {test_case}")
                print(f"{Color.GRAY}{trace.strip()}{Color.RESET}\n")

        total_tests_run += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        total_duration += t_elapsed

        tier_results.append({
            "tier_id": tier_id,
            "name": tier_name,
            "total": result.testsRun,
            "passed": passed,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "duration_seconds": round(t_elapsed, 4),
            "status": status_text
        })

    overall_duration = time.perf_counter() - overall_start_time

    # Print summary table
    print(f"\n{Color.CYAN}{'=' * 78}")
    print(f"{Color.BOLD}  TEST EXECUTION SUMMARY TABLE{Color.RESET}")
    print(f"{Color.CYAN}{'=' * 78}{Color.RESET}")
    print(f"  {'Tier Name':<40} {'Tests':<8} {'Passed':<8} {'Failed':<8} {'Time (s)':<10}")
    print(f"  {'-' * 74}")

    for tr in tier_results:
        color = Color.GREEN if tr["failed"] == 0 and tr["errors"] == 0 else Color.RED
        print(f"  {tr['name']:<40} {tr['total']:<8} {color}{tr['passed']:<8}{Color.RESET} {color}{tr['failed'] + tr['errors']:<8}{Color.RESET} {tr['duration_seconds']:<10.3f}")

    print(f"  {'-' * 74}")
    passed_total = total_tests_run - total_failures - total_errors
    final_color = Color.GREEN if total_failures == 0 and total_errors == 0 else Color.RED
    print(f"  {'TOTAL':<40} {total_tests_run:<8} {final_color}{passed_total:<8}{Color.RESET} {final_color}{total_failures + total_errors:<8}{Color.RESET} {overall_duration:<10.3f}\n")

    if total_failures == 0 and total_errors == 0:
        print(f"{Color.GREEN}{Color.BOLD}🎉 ALL {total_tests_run} TESTS PASSED PERFECTLY IN {overall_duration:.3f} SECONDS! 🎉{Color.RESET}\n")
    else:
        print(f"{Color.RED}{Color.BOLD}❌ {total_failures + total_errors} TEST(S) FAILED. Inspect details above.{Color.RESET}\n")

    # Export JSON report if requested
    if args.json:
        report_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total": total_tests_run,
            "passed": passed_total,
            "failed": total_failures,
            "errors": total_errors,
            "duration_seconds": round(overall_duration, 4),
            "status": "PASSED" if (total_failures == 0 and total_errors == 0) else "FAILED",
            "tiers": tier_results
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"Report written to {args.json}")

    sys.exit(0 if (total_failures == 0 and total_errors == 0) else 1)


if __name__ == "__main__":
    main()
