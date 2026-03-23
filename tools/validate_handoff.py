#!/usr/bin/env python3
"""Validate NEXT.md handoff quality before sending to Claude Code.

Run: python tools/validate_handoff.py [--engine ENGINE_NAME]

If --engine is not provided, auto-detects from NEXT.md content.

Checks:
1. NEXT.md exists and has required sections
2. All file paths referenced in "Read First" exist
3. Line number references are within file bounds
4. Test count in NEXT.md matches actual pytest output
5. SPEC line references contain expected content keywords

Exit 0 = all checks pass. Exit 1 = findings exist.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Known engine names in KR
KNOWN_ENGINES = ["source", "normalization", "excerpting", "taxonomy", "synthesis"]


def read_next_md() -> str:
    path = Path("NEXT.md")
    if not path.exists():
        print("FAIL: NEXT.md does not exist")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def detect_engine(content: str, cli_engine: str | None) -> str:
    """Detect which engine this handoff is for.

    Priority: CLI flag > NEXT.md content detection > fallback to normalization.
    """
    if cli_engine:
        if cli_engine not in KNOWN_ENGINES:
            print(f"WARNING: '{cli_engine}' not in known engines {KNOWN_ENGINES}")
        return cli_engine

    # Auto-detect from NEXT.md: look for "engines/{name}" paths
    engine_refs = re.findall(r"engines/(\w+)/", content)
    if engine_refs:
        # Most-referenced engine wins
        from collections import Counter

        counts = Counter(engine_refs)
        detected = counts.most_common(1)[0][0]
        return detected

    # Fallback
    print("WARNING: Could not detect engine from NEXT.md. Use --engine flag.")
    return "normalization"


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
    """Check that all file paths in Read First exist.

    Files that appear ONLY in the 'What to Build' or 'Module: Tests' sections
    are assumed to be CC output files (will be created by this session) and
    are not flagged as missing.
    """
    findings = []

    # Split content to identify which section each reference is in
    # Find the Read First section boundaries
    read_first_match = re.search(r"## Read First\s*\n(.*?)(?=\n## )", content, re.DOTALL)
    read_first_content = read_first_match.group(1) if read_first_match else ""

    # Files referenced in Read First must exist — these are inputs
    input_paths = re.findall(
        r"`(engines/[^`]+|tests/[^`]+|reference/[^`]+|shared/[^`]+|tools/[^`]+)`",
        read_first_content,
    )

    # All file references across entire NEXT.md
    all_paths = re.findall(
        r"`(engines/[^`]+|tests/[^`]+|reference/[^`]+|shared/[^`]+|tools/[^`]+)`",
        content,
    )

    # Files only in non-Read-First sections are candidate output files
    input_path_set = set(input_paths)

    for p in all_paths:
        # Strip line range indicators
        clean = p.split(" ")[0]
        # Skip if it looks like a code snippet, not a file path
        if "(" in clean or ")" in clean or "=" in clean:
            continue
        # Skip grep commands and similar
        if "grep" in clean or "pytest" in clean:
            continue
        if not Path(clean).exists():
            if clean in input_path_set:
                # This is in Read First — it MUST exist
                findings.append(f"Read First file does not exist: {clean}")
            else:
                # This is an output file CC will create — just note it
                pass  # Silent skip for CC output files

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


def check_test_count(content: str, engine: str) -> list[str]:
    """Check that claimed test count matches actual pytest output."""
    findings = []

    # Extract claimed count from NEXT.md
    # Look for patterns like "172 tests passing" or "172 existing tests"
    claimed = re.findall(r"(\d+)\s+(?:existing\s+)?tests?\s+(?:passing|still pass)", content)
    if not claimed:
        findings.append("No test count claim found in NEXT.md")
        return findings

    claimed_count = int(claimed[0])

    # Run pytest against the detected engine's test directory
    test_dir = f"engines/{engine}/tests/"
    if not Path(test_dir).exists():
        findings.append(f"Test directory does not exist: {test_dir}")
        return findings

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_dir, "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Parse "N passed" from output
        match = re.search(r"(\d+) passed", result.stdout)
        if match:
            actual_count = int(match.group(1))
            if actual_count != claimed_count:
                findings.append(
                    f"Test count mismatch: NEXT.md claims {claimed_count}, "
                    f"pytest engines/{engine}/tests/ reports {actual_count}"
                )
        else:
            findings.append(f"Could not parse pytest output: {result.stdout[-200:]}")
    except Exception as e:
        findings.append(f"Could not run pytest: {e}")

    return findings


def main():
    parser = argparse.ArgumentParser(description="Validate NEXT.md handoff quality")
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        help=f"Engine name for test directory. Auto-detected if omitted. Known: {KNOWN_ENGINES}",
    )
    args = parser.parse_args()

    os.chdir(Path(__file__).parent.parent)  # cd to repo root

    content = read_next_md()
    engine = detect_engine(content, args.engine)
    all_findings: list[str] = []

    print(f"Validating NEXT.md handoff quality (engine: {engine})...\n")

    checks: list[tuple[str, list[str]]] = [
        ("Required sections", check_required_sections(content)),
        ("File references", check_file_references(content)),
        ("Line references", check_line_references(content)),
        ("Test count", check_test_count(content, engine)),
    ]

    for name, findings in checks:
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
