#!/usr/bin/env python3
"""Check SPEC refinement status across all engines and shared components.

Usage:
    python3 scripts/refinement_status.py
"""

import re
from pathlib import Path

TARGETS = [
    "engines/source",
    "engines/normalization",
    "engines/passaging",
    "engines/atomization",
    "engines/excerpting",
    "engines/taxonomy",
    "engines/synthesis",
    "shared/consensus",
    "shared/validation",
    "shared/human_gate",
    "shared/feedback",
    "shared/user_model",
    "shared/scholar_authority",
    "interface/scholar",
]


def parse_refinement_status(claude_md_path: Path) -> dict:
    """Extract refinement status from a CLAUDE.md file."""
    if not claude_md_path.exists():
        return {"status": "NO CLAUDE.md", "cycles": 0, "ready": False}

    text = claude_md_path.read_text(encoding="utf-8")

    # Find refinement status section
    match = re.search(r"## SPEC Refinement Status\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return {"status": "NO REFINEMENT SECTION", "cycles": 0, "ready": False}

    section = match.group(1)

    # Count cycles
    cycles = len(re.findall(r"Cycle \d+(?!\s*\(not yet)", section))

    # Check if implementation-ready
    ready = "Implementation-ready: YES" in section

    # Get latest cycle info
    cycle_lines = re.findall(r"- Cycle \d+.*", section)
    latest = cycle_lines[-1] if cycle_lines else "No cycles"

    return {"status": latest.strip("- "), "cycles": cycles, "ready": ready}


def count_examples(spec_path: Path) -> int:
    """Count concrete examples in a SPEC's §4 section."""
    if not spec_path.exists():
        return -1

    text = spec_path.read_text(encoding="utf-8")

    # Count **Example patterns
    return len(re.findall(r"\*\*Example", text))


def main():
    print("KR SPEC Refinement Status")
    print("=" * 70)
    print(f"{'Component':<25} {'Cycles':>7} {'Ready':>6} {'Examples':>9} {'Status'}")
    print("-" * 70)

    total_ready = 0
    total_components = 0

    for target in TARGETS:
        component = Path(target).name
        claude_md = Path(target) / "CLAUDE.md"
        spec_md = Path(target) / "SPEC.md"

        status = parse_refinement_status(claude_md)
        examples = count_examples(spec_md)

        ready_str = "YES" if status["ready"] else "NO"
        examples_str = str(examples) if examples >= 0 else "N/A"

        print(f"  {component:<23} {status['cycles']:>7} {ready_str:>6} {examples_str:>9}   {status['status']}")

        total_components += 1
        if status["ready"]:
            total_ready += 1

    print("-" * 70)
    print(f"  Ready for implementation: {total_ready} / {total_components}")

    if total_ready == 0:
        print("\n  ⚠ No SPECs are implementation-ready. SPEC refinement must proceed before implementation.")
    elif total_ready < total_components:
        print(f"\n  ⚠ {total_components - total_ready} SPECs still need refinement.")
    else:
        print("\n  ✓ All SPECs are implementation-ready. Implementation can proceed.")


if __name__ == "__main__":
    main()
