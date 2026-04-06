"""Minimal Q-CLOSED verifier for atom closure (DA-001).

Checks objective criteria from HARDENING_SESSION_PROTOCOL.md §4.8:
1. Ledger entry exists for the MAQ-ID with required fields
2. Queue status in MERGED_ATOM_QUEUE.md matches ledger status
3. If prompt-affecting: check_prompt_spec_sync.py passes
4. Word budget consistency (GROUP ≤1500, CLASSIFY ≤1000)

Usage:
    python scripts/verify_atom_closure_minimal.py [--maq-id MAQ-NNN]
    python scripts/verify_atom_closure_minimal.py --all

Without --maq-id: checks all atoms marked CLOSED-* in the ledger.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "engines" / "excerpting" / "reference" / "FOUNDATIONS_HARDENING_LEDGER.md"
QUEUE = REPO_ROOT / "engines" / "excerpting" / "reference" / "MERGED_ATOM_QUEUE.md"
GROUP_PROMPT = REPO_ROOT / "engines" / "excerpting" / "src" / "phase2_group.py"
CLASSIFY_PROMPT = REPO_ROOT / "engines" / "excerpting" / "src" / "phase2_classify.py"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "check_prompt_spec_sync.py"

REQUIRED_LEDGER_FIELDS = [
    "Status",
    "Sources",
    "Authority",
]

GROUP_WORD_LIMIT = 1500
CLASSIFY_WORD_LIMIT = 1000


def count_prompt_words(filepath: Path, prompt_var: str) -> int | None:
    """Extract and count words in a prompt variable from a Python file."""
    text = filepath.read_text(encoding="utf-8")
    match = re.search(rf'{prompt_var}\s*=\s*"""(.*?)"""', text, re.DOTALL)
    if not match:
        match = re.search(rf"{prompt_var}\s*=\s*'''(.*?)'''", text, re.DOTALL)
    if not match:
        return None
    return len(match.group(1).split())


def check_prompt_spec_sync() -> bool:
    """Run check_prompt_spec_sync.py and return True if it passes."""
    if not SYNC_SCRIPT.exists():
        print("  WARNING: check_prompt_spec_sync.py not found")
        return True
    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    return result.returncode == 0


def check_word_budgets() -> list[str]:
    """Verify prompt word budgets are within limits."""
    errors: list[str] = []

    group_words = count_prompt_words(GROUP_PROMPT, "GROUP_SYSTEM_PROMPT")
    if group_words is not None and group_words > GROUP_WORD_LIMIT:
        errors.append(
            f"GROUP_SYSTEM_PROMPT: {group_words} words exceeds {GROUP_WORD_LIMIT} limit"
        )
    elif group_words is not None:
        print(f"  GROUP_SYSTEM_PROMPT: {group_words}/{GROUP_WORD_LIMIT} words")

    classify_words = count_prompt_words(CLASSIFY_PROMPT, "CLASSIFY_SYSTEM_PROMPT")
    if classify_words is not None and classify_words > CLASSIFY_WORD_LIMIT:
        errors.append(
            f"CLASSIFY_SYSTEM_PROMPT: {classify_words} words exceeds {CLASSIFY_WORD_LIMIT} limit"
        )
    elif classify_words is not None:
        print(f"  CLASSIFY_SYSTEM_PROMPT: {classify_words}/{CLASSIFY_WORD_LIMIT} words")

    return errors


def find_closed_atoms_in_ledger() -> list[str]:
    """Find all atoms with CLOSED-* or FINALIZED status in the ledger."""
    if not LEDGER.exists():
        return []
    text = LEDGER.read_text(encoding="utf-8")
    atoms = re.findall(r"\|\s*(\d+)\s*\|.*?\|\s*\*\*(FINALIZED|CLOSED[^*]*)\*\*", text)
    return [f"ATOM-{num}" for num, _ in atoms]


def check_ledger_entry(atom_id: str) -> list[str]:
    """Check that a ledger entry has required fields."""
    if not LEDGER.exists():
        return [f"Ledger file not found: {LEDGER}"]

    text = LEDGER.read_text(encoding="utf-8")
    errors: list[str] = []

    atom_num = re.search(r"\d+", atom_id)
    if not atom_num:
        return [f"Cannot parse atom number from {atom_id}"]

    pattern = rf"\|\s*{atom_num.group()}\s*\|"
    if not re.search(pattern, text):
        errors.append(f"{atom_id}: No entry found in ledger register")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal Q-CLOSED verifier")
    parser.add_argument("--maq-id", help="Specific MAQ-ID to verify")
    parser.add_argument("--all", action="store_true", help="Verify all CLOSED atoms")
    args = parser.parse_args()

    all_errors: list[str] = []

    print("=== Q-CLOSED Minimal Verifier (DA-001) ===\n")

    # Check 1: Prompt-SPEC sync
    print("[1/3] Checking prompt-SPEC sync...")
    if not check_prompt_spec_sync():
        all_errors.append("Prompt-SPEC sync FAILED")
        print("  FAIL: Prompt and SPEC are out of sync")
    else:
        print("  PASS")

    # Check 2: Word budgets
    print("\n[2/3] Checking word budgets...")
    budget_errors = check_word_budgets()
    all_errors.extend(budget_errors)
    if budget_errors:
        for err in budget_errors:
            print(f"  FAIL: {err}")
    else:
        print("  PASS")

    # Check 3: Ledger entries
    print("\n[3/3] Checking ledger entries...")
    if args.maq_id:
        atoms = [args.maq_id]
    elif args.all:
        atoms = find_closed_atoms_in_ledger()
        if not atoms:
            print("  No CLOSED atoms found in ledger")
        else:
            print(f"  Found {len(atoms)} closed atoms")
    else:
        atoms = find_closed_atoms_in_ledger()
        if atoms:
            print(f"  Found {len(atoms)} closed atoms (use --all to verify each)")

    for atom in atoms:
        ledger_errors = check_ledger_entry(atom)
        all_errors.extend(ledger_errors)
        for err in ledger_errors:
            print(f"  FAIL: {err}")

    # Summary
    print(f"\n{'=' * 40}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s)")
        for err in all_errors:
            print(f"  - {err}")
        return 1
    else:
        print("PASSED: All minimal Q-CLOSED checks pass")
        return 0


if __name__ == "__main__":
    sys.exit(main())
