"""Structured test failure diagnosis.

Given pytest output (piped or from a file), produces a structured diagnosis
including failing test, assertion, SPEC references, and related git changes.

Usage:
    python -m pytest engines/norm/tests/ --tb=short 2>&1 | python scripts/diagnose_failure.py
    python scripts/diagnose_failure.py --file pytest_output.txt
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def run_git(args: list[str]) -> str:
    """Run git command, return stdout or empty string."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def parse_failures(output: str) -> list[dict[str, str]]:
    """Parse pytest output for failing tests."""
    failures: list[dict[str, str]] = []

    # Match FAILED lines: FAILED tests/test_foo.py::test_bar - AssertionError
    for match in re.finditer(
        r"FAILED\s+([^\s]+)::([^\s]+)(?:\s*-\s*(.+))?",
        output,
    ):
        failures.append({
            "file": match.group(1),
            "test": match.group(2),
            "error": match.group(3) or "unknown",
        })

    # Fall back to ERROR lines
    if not failures:
        for match in re.finditer(
            r"ERROR\s+([^\s]+)::([^\s]+)(?:\s*-\s*(.+))?",
            output,
        ):
            failures.append({
                "file": match.group(1),
                "test": match.group(2),
                "error": match.group(3) or "collection error",
            })

    return failures


def extract_assertion_detail(output: str, test_name: str) -> str | None:
    """Extract assertion detail for a specific test from tb=short output."""
    lines = output.split("\n")
    in_section = False
    details: list[str] = []

    for line in lines:
        if test_name in line and ("FAILED" in line or "___" in line):
            in_section = True
            continue
        if in_section:
            if line.startswith("FAILED") or line.startswith("===="):
                break
            stripped = line.strip()
            if "assert" in stripped.lower() or "Error" in stripped:
                details.append(stripped)
            elif stripped.startswith(">"):
                details.append(stripped)
            if len(details) >= 5:
                break

    return "\n".join(details) if details else None


def find_spec_reference(test_file: Path, test_name: str) -> str | None:
    """Look for SPEC section references in the test's docstring."""
    if not test_file.exists():
        return None

    try:
        content = test_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    # Multi-line docstring
    pattern = (
        rf'def\s+{re.escape(test_name)}\s*\([^)]*\).*?:\s*\n'
        r'\s*"""(.*?)"""'
    )
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        # Single-line docstring
        pattern = (
            rf'def\s+{re.escape(test_name)}\s*\([^)]*\).*?:\s*\n'
            r'\s*"([^"]*)"'
        )
        match = re.search(pattern, content)

    if not match:
        return None

    docstring = match.group(1)
    refs = re.findall(r"[^a-zA-Z0-9]([0-9]+(?:\.[A-Za-z0-9]+)*)", docstring)
    adv_refs = re.findall(r"ADV-[A-Z][0-9]+", docstring)

    all_refs = refs + adv_refs
    return ", ".join(all_refs) if all_refs else None


def find_related_changes(test_file: Path) -> list[str]:
    """Find recent git changes in files related to the failing test."""
    if not test_file.exists():
        return []

    test_dir = test_file.parent
    engine_dir = test_dir.parent

    recent = run_git([
        "log",
        "--oneline",
        "-5",
        "--name-only",
        "--",
        str(engine_dir),
    ])

    changed: list[str] = []
    for line in recent.split("\n"):
        if line and not line[0].isspace() and "/" in line:
            changed.append(line)

    return changed[:10]


def diagnose(output: str) -> str:
    """Produce structured diagnosis from pytest output."""
    failures = parse_failures(output)

    if not failures:
        return "No test failures detected in the provided output."

    lines: list[str] = []
    lines.append(
        f"=== Test Failure Diagnosis ({len(failures)} failure(s)) ===\n"
    )

    for i, failure in enumerate(failures, 1):
        test_file = Path(failure["file"])
        test_name = failure["test"]

        lines.append(f"--- Failure {i}: {test_name} ---")
        lines.append(f"  File: {failure['file']}")
        lines.append(f"  Error: {failure['error']}")

        detail = extract_assertion_detail(output, test_name)
        if detail:
            lines.append("  Assertion:")
            for d in detail.split("\n"):
                lines.append(f"    {d}")

        spec_ref = find_spec_reference(test_file, test_name)
        if spec_ref:
            lines.append(f"  SPEC: {spec_ref}")
        else:
            lines.append("  SPEC: (no reference in docstring)")

        changes = find_related_changes(test_file)
        if changes:
            lines.append("  Recent changes in area:")
            for c in changes[:5]:
                lines.append(f"    {c}")

        lines.append("")

    lines.append("--- Investigation Order ---")
    seen_files: set[str] = set()
    for failure in failures:
        if failure["file"] not in seen_files:
            lines.append(f"  1. Read {failure['file']}")
            seen_files.add(failure["file"])
    lines.append("  2. Check recent git changes: git log --oneline -10")
    lines.append(
        "  3. Re-run with verbose: python -m pytest <file> -v --tb=long"
    )

    return "\n".join(lines)


def main() -> int:
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            path = Path(sys.argv[idx + 1])
            if not path.exists():
                print(f"File not found: {path}")
                return 1
            output = path.read_text(encoding="utf-8", errors="ignore")
        else:
            print("Usage: --file <path>")
            return 1
    elif not sys.stdin.isatty():
        output = sys.stdin.read()
    else:
        print(
            "Usage:\n"
            "  python -m pytest ... 2>&1 | python scripts/diagnose_failure.py\n"
            "  python scripts/diagnose_failure.py --file pytest_output.txt"
        )
        return 1

    print(diagnose(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
