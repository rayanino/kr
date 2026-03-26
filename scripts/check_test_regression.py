"""Compare test results between two git refs to detect regressions.

Usage:
    python scripts/check_test_regression.py [baseline_ref]

Default baseline: HEAD~1
Compares pytest outcomes at baseline vs current working tree.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestResults:
    """Parsed pytest results."""

    ref: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    failed_names: list[str] = field(default_factory=list)
    passed_names: list[str] = field(default_factory=list)


def run_tests(ref: str | None = None) -> TestResults:
    """Run pytest and parse results. If ref is None, run on current state."""
    label = ref or "HEAD (working tree)"
    results = TestResults(ref=label)

    cmd = [
        sys.executable, "-m", "pytest",
        "engines/", "shared/",
        "-q", "--tb=no", "--no-header",
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )
        output = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        print(f"  WARNING: Tests timed out for {label}")
        return results

    # Parse summary line: "N passed, M failed, K skipped"
    summary_match = re.search(
        r"(\d+) passed", output
    )
    if summary_match:
        results.passed = int(summary_match.group(1))

    failed_match = re.search(r"(\d+) failed", output)
    if failed_match:
        results.failed = int(failed_match.group(1))

    skipped_match = re.search(r"(\d+) skipped", output)
    if skipped_match:
        results.skipped = int(skipped_match.group(1))

    error_match = re.search(r"(\d+) error", output)
    if error_match:
        results.errors = int(error_match.group(1))

    results.total = results.passed + results.failed + results.skipped + results.errors

    # Parse individual FAILED test names
    for match in re.finditer(r"FAILED (.+?)(?:\s|$)", output):
        results.failed_names.append(match.group(1).strip())

    return results


def checkout_and_test(ref: str) -> TestResults:
    """Stash, checkout ref, run tests, restore."""
    # Stash
    stash_result = subprocess.run(
        ["git", "stash", "--include-untracked", "-q"],
        capture_output=True, text=True,
    )
    stashed = stash_result.returncode == 0

    try:
        # Checkout baseline
        checkout_result = subprocess.run(
            ["git", "checkout", ref, "-q"],
            capture_output=True, text=True,
        )
        if checkout_result.returncode != 0:
            print(f"  ERROR: Cannot checkout {ref}: {checkout_result.stderr.strip()}")
            return TestResults(ref=ref)

        try:
            results = run_tests(ref)
        finally:
            # Return to previous branch
            subprocess.run(["git", "checkout", "-", "-q"], capture_output=True)
    finally:
        # Restore stash
        if stashed:
            subprocess.run(
                ["git", "stash", "pop", "-q"],
                capture_output=True, text=True,
            )

    return results


def main() -> int:
    """Run regression check."""
    baseline_ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1"

    # Handle numeric shorthand: "5" -> "HEAD~5"
    if baseline_ref.isdigit():
        baseline_ref = f"HEAD~{baseline_ref}"

    print(f"=== Test Regression Check ===")
    print(f"Baseline: {baseline_ref}")
    print(f"Current:  HEAD (working tree)")
    print()

    # Run current tests first
    print("Running current tests...")
    current = run_tests()
    print(f"  Current: {current.passed} passed, {current.failed} failed, {current.skipped} skipped")
    print()

    # Run baseline tests
    print(f"Running baseline tests at {baseline_ref}...")
    baseline = checkout_and_test(baseline_ref)
    print(f"  Baseline: {baseline.passed} passed, {baseline.failed} failed, {baseline.skipped} skipped")
    print()

    # Compare
    delta_passed = current.passed - baseline.passed
    delta_failed = current.failed - baseline.failed

    print("--- Delta ---")
    print(f"  Passed:  {delta_passed:+d}")
    print(f"  Failed:  {delta_failed:+d}")
    print(f"  Skipped: {current.skipped - baseline.skipped:+d}")
    print()

    # Identify regressions (tests that were passing and now fail)
    new_failures = set(current.failed_names) - set(baseline.failed_names)
    recovered = set(baseline.failed_names) - set(current.failed_names)

    if new_failures:
        print("--- REGRESSIONS (new failures) ---")
        for name in sorted(new_failures):
            print(f"  {name}")
        print()

    if recovered:
        print("--- RECOVERED (were failing, now pass) ---")
        for name in sorted(recovered):
            print(f"  {name}")
        print()

    persistent = set(current.failed_names) & set(baseline.failed_names)
    if persistent:
        print("--- PERSISTENT FAILURES (still failing) ---")
        for name in sorted(persistent):
            print(f"  {name}")
        print()

    # Verdict
    if new_failures:
        print(f"=== Verdict: REGRESSED ({len(new_failures)} new failures) ===")
        return 1
    elif recovered:
        print(f"=== Verdict: IMPROVED (+{len(recovered)} recovered) ===")
        return 0
    else:
        print("=== Verdict: STABLE ===")
        return 0


if __name__ == "__main__":
    sys.exit(main())
