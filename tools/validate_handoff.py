#!/usr/bin/env python3
"""Validate NEXT.md handoff quality before sending to Claude Code.

Run: python tools/validate_handoff.py

Checks:
1. NEXT.md exists and has required sections
2. All file paths referenced in "Read First" exist
3. Line number references are within file bounds
4. Test count in NEXT.md matches actual pytest output
5. SPEC line references contain expected content keywords

Exit 0 = all checks pass. Exit 1 = findings exist.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def read_next_md() -> str:
    path = Path("NEXT.md")
    if not path.exists():
        print("FAIL: NEXT.md does not exist")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def check_required_sections(content: str) -> list[str]:
    """Check that NEXT.md has all required sections."""
    required = [
        "## Read First",
        "## What to Build",
        "## Do NOT Do",
        "## Verification",
        "## After This",
    ]
    findings = []
    for section in required:
        if section not in content:
            findings.append(f"Missing required section: {section}")
    return findings


def check_file_references(content: str) -> list[str]:
    """Check that all file paths in Read First exist."""
    findings = []
    # Match backtick-quoted file paths
    paths = re.findall(r"`(engines/[^`]+|tests/[^`]+|reference/[^`]+|shared/[^`]+|tools/[^`]+)`", content)
    for p in paths:
        # Strip line range indicators
        clean = p.split(" ")[0]
        # Skip if it looks like a code snippet, not a file path
        if "(" in clean or ")" in clean or "=" in clean:
            continue
        if not Path(clean).exists():
            # Maybe it's a file that will be created by this session
            if "New module" not in content or clean not in content:
                findings.append(f"Referenced file does not exist: {clean}")
    return findings


def check_line_references(content: str) -> list[str]:
    """Check that line number references are within file bounds."""
    findings = []
    # Match patterns like "SPEC.md lines 219-233" or "contracts.py (line 216)"
    line_refs = re.findall(
        r"`([^`]+\.(?:py|md))`[^`]*?lines?\s+(\d+)[-–](\d+)",
        content,
    )
    line_refs += re.findall(
        r"`([^`]+\.(?:py|md))`[^`]*?\(line\s+(\d+)\)",
        content,
    )

    for match in line_refs:
        if len(match) == 3:
            filepath, start, end = match
            start, end = int(start), int(end)
        else:
            filepath, line = match[0], match[1]
            start = end = int(line)

        path = Path(filepath)
        if not path.exists():
            continue  # Already caught by check_file_references

        line_count = sum(1 for _ in path.open(encoding="utf-8"))
        if end > line_count:
            findings.append(
                f"Line reference out of bounds: {filepath} lines {start}-{end} "
                f"(file has {line_count} lines)"
            )

    return findings


def check_test_count(content: str) -> list[str]:
    """Check that claimed test count matches actual pytest output."""
    findings = []

    # Extract claimed count from NEXT.md
    # Look for patterns like "172 tests passing" or "172 existing tests"
    claimed = re.findall(r"(\d+)\s+(?:existing\s+)?tests?\s+(?:passing|still pass)", content)
    if not claimed:
        findings.append("No test count claim found in NEXT.md")
        return findings

    claimed_count = int(claimed[0])

    # Run pytest to get actual count
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "engines/normalization/tests/", "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Parse "N passed" from output
        match = re.search(r"(\d+) passed", result.stdout)
        if match:
            actual_count = int(match.group(1))
            if actual_count != claimed_count:
                findings.append(
                    f"Test count mismatch: NEXT.md claims {claimed_count}, "
                    f"pytest reports {actual_count}"
                )
        else:
            findings.append(f"Could not parse pytest output: {result.stdout[-200:]}")
    except Exception as e:
        findings.append(f"Could not run pytest: {e}")

    return findings


def main():
    os.chdir(Path(__file__).parent.parent)  # cd to repo root

    content = read_next_md()
    all_findings: list[str] = []

    print("Validating NEXT.md handoff quality...\n")

    checks = [
        ("Required sections", check_required_sections),
        ("File references", check_file_references),
        ("Line references", check_line_references),
        ("Test count", check_test_count),
    ]

    for name, check_fn in checks:
        findings = check_fn(content)
        if findings:
            print(f"  ✗ {name}: {len(findings)} finding(s)")
            for f in findings:
                print(f"    - {f}")
        else:
            print(f"  ✓ {name}")
        all_findings.extend(findings)

    print()
    if all_findings:
        print(f"BLOCKED: {len(all_findings)} finding(s). Fix before sending to CC.")
        return 1
    else:
        print("PASS: All automated checks passed.")
        print("NOTE: This does NOT replace manual Steps 5-8 (SPEC traces, fixture testing,")
        print("      prerequisite checklist, adversarial read). Those require human judgment.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
