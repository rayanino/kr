"""Step 4 Pre-Run Verification — checks book lists, collection dirs, budget.

Run: python scripts/verify_step4_books.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Paths ---
PHASE_C_BOOKS = PROJECT_ROOT / "scripts" / "phase_c_books.txt"
PHASE_D_BOOKS = PROJECT_ROOT / "scripts" / "phase_d_books.txt"
COMBINED_BOOKS = PROJECT_ROOT / "scripts" / "step4_all_books.txt"
DISTRIBUTION_JSON = (
    PROJECT_ROOT / "tests" / "results" / "source_engine" / "PHASE_D_CATEGORY_DISTRIBUTION.json"
)
PHASE_C_RESULTS = PROJECT_ROOT / "tests" / "results" / "source_engine" / "phase_c"
COST_LOG = PROJECT_ROOT / "tests" / "results" / "source_engine" / "COST_LOG.json"
PHASE_C_COLLECTION = PROJECT_ROOT / "phase_c_collection"
PHASE_D_COLLECTION = PROJECT_ROOT / "phase_d_collection"

COST_PER_BOOK = 0.15  # EUR, conservative (matches run_phase_c.py:70)


def load_books(path: Path) -> list[str]:
    """Same logic as run_phase_c.py:106-114."""
    lines = path.read_text(encoding="utf-8").splitlines()
    books: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            books.append(stripped)
    return books


def check_category_distribution(
    phase_c: list[str], phase_d: list[str]
) -> tuple[bool, list[str]]:
    """Check books against PHASE_D_CATEGORY_DISTRIBUTION.json.

    Phase D books: STRICT (must all appear — they were selected from it).
    Phase C books: INFORMATIONAL (some are uncategorized in Shamela).
    """
    with open(DISTRIBUTION_JSON, encoding="utf-8") as f:
        dist = json.load(f)

    all_dist_books: set[str] = set()
    for cat_data in dist["categories"].values():
        all_dist_books.update(cat_data["books"])

    phase_d_missing = [b for b in phase_d if b not in all_dist_books]
    phase_c_missing = [b for b in phase_c if b not in all_dist_books]
    phase_c_found = len(phase_c) - len(phase_c_missing)

    messages: list[str] = []
    ok = True

    if phase_d_missing:
        ok = False
        messages.append(
            f"  FAIL: {len(phase_d_missing)} Phase D books missing from distribution:"
        )
        for b in phase_d_missing:
            messages.append(f"    - {b}")
    else:
        messages.append(f"  Phase D: 131/131 in distribution")

    messages.append(
        f"  Phase C: {phase_c_found}/73 in distribution "
        f"({len(phase_c_missing)} uncategorized — expected, not an error)"
    )

    return ok, messages


def check_zero_overlap(
    phase_c: list[str], phase_d: list[str]
) -> tuple[bool, list[str]]:
    overlap = set(phase_c) & set(phase_d)
    if overlap:
        msgs = [f"  FAIL: {len(overlap)} books appear in both lists:"]
        for b in sorted(overlap):
            msgs.append(f"    - {b}")
        return False, msgs
    return True, [f"  0 duplicates between Phase C ({len(phase_c)}) and Phase D ({len(phase_d)})"]


def check_total_count(
    phase_c: list[str], phase_d: list[str], combined: list[str]
) -> tuple[bool, list[str]]:
    msgs: list[str] = []
    ok = True

    if len(phase_c) != 73:
        ok = False
        msgs.append(f"  FAIL: phase_c_books.txt has {len(phase_c)} books (expected 73)")
    if len(phase_d) != 131:
        ok = False
        msgs.append(f"  FAIL: phase_d_books.txt has {len(phase_d)} books (expected 131)")
    if len(combined) != 204:
        ok = False
        msgs.append(f"  FAIL: step4_all_books.txt has {len(combined)} books (expected 204)")

    expected_combined = set(phase_c) | set(phase_d)
    actual_combined = set(combined)
    if expected_combined != actual_combined:
        ok = False
        extra = actual_combined - expected_combined
        missing = expected_combined - actual_combined
        if extra:
            msgs.append(f"  FAIL: {len(extra)} books in combined but not in source lists")
        if missing:
            msgs.append(f"  FAIL: {len(missing)} books in source lists but not in combined")

    if ok:
        msgs.append(f"  {len(combined)} = {len(phase_c)} + {len(phase_d)}")

    return ok, msgs


def check_phase_c_results(phase_c: list[str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for book in phase_c:
        book_dir = PHASE_C_RESULTS / book
        if not book_dir.is_dir():
            missing.append(book)

    if missing:
        msgs = [f"  FAIL: {len(missing)}/73 Phase C books have no result directory:"]
        for b in missing[:10]:
            msgs.append(f"    - {b}")
        if len(missing) > 10:
            msgs.append(f"    ... and {len(missing) - 10} more")
        return False, msgs

    return True, [f"  73/73 have result directories in {PHASE_C_RESULTS.name}/"]


def check_collection_dirs(
    phase_c: list[str], phase_d: list[str]
) -> tuple[bool, list[str]]:
    msgs: list[str] = []
    ok = True

    # Check phase_c_collection
    if PHASE_C_COLLECTION.is_dir():
        c_missing = [b for b in phase_c if not (PHASE_C_COLLECTION / b).is_dir()]
        if c_missing:
            ok = False
            msgs.append(f"  FAIL: phase_c_collection: {len(c_missing)}/73 missing")
            for b in c_missing[:5]:
                msgs.append(f"    - {b}")
        else:
            msgs.append(f"  phase_c_collection: 73/73 OK")
    else:
        ok = False
        msgs.append(f"  FAIL: phase_c_collection/ directory not found")

    # Check phase_d_collection
    if PHASE_D_COLLECTION.is_dir():
        d_missing = [b for b in phase_d if not (PHASE_D_COLLECTION / b).is_dir()]
        if d_missing:
            ok = False
            msgs.append(f"  FAIL: phase_d_collection: {len(d_missing)}/131 missing")
            for b in d_missing[:5]:
                msgs.append(f"    - {b}")
        else:
            msgs.append(f"  phase_d_collection: 131/131 OK")
    else:
        ok = False
        msgs.append(f"  FAIL: phase_d_collection/ directory not found")

    return ok, msgs


def check_budget() -> tuple[bool, list[str]]:
    with open(COST_LOG, encoding="utf-8") as f:
        cost_data = json.load(f)

    spent = cost_data["total_eur"]
    ceiling = cost_data["budget_ceiling_eur"]
    estimated_run = 204 * COST_PER_BOOK
    projected_total = spent + estimated_run
    per_run_ceiling = 50.0  # run_phase_c.py default

    msgs = [
        f"  Already spent:    EUR {spent:.2f}",
        f"  Estimated run:    EUR {estimated_run:.2f} (204 books x EUR {COST_PER_BOOK})",
        f"  Projected total:  EUR {projected_total:.2f}",
        f"  Per-run ceiling:  EUR {per_run_ceiling:.2f}  -- {'PASS' if estimated_run < per_run_ceiling else 'FAIL'}",
        f"  Overall ceiling:  EUR {ceiling:.2f} -- {'PASS' if projected_total < ceiling else 'FAIL'}",
    ]

    ok = estimated_run < per_run_ceiling and projected_total < ceiling
    return ok, msgs


def main() -> int:
    print("=== Step 4 Book List Verification ===\n")

    phase_c = load_books(PHASE_C_BOOKS)
    phase_d = load_books(PHASE_D_BOOKS)
    combined = load_books(COMBINED_BOOKS)

    checks: list[tuple[str, bool, list[str]]] = []

    # Check 1: Category distribution
    ok, msgs = check_category_distribution(phase_c, phase_d)
    checks.append(("Category distribution", ok, msgs))

    # Check 2: Zero overlap
    ok, msgs = check_zero_overlap(phase_c, phase_d)
    checks.append(("Zero overlap", ok, msgs))

    # Check 3: Total count
    ok, msgs = check_total_count(phase_c, phase_d, combined)
    checks.append(("Total count (204 = 73 + 131)", ok, msgs))

    # Check 4: Phase C results exist
    ok, msgs = check_phase_c_results(phase_c)
    checks.append(("Phase C results exist", ok, msgs))

    # Check 5: Collection directories
    ok, msgs = check_collection_dirs(phase_c, phase_d)
    checks.append(("Collection directories", ok, msgs))

    # Check 6: Budget
    ok, msgs = check_budget()
    checks.append(("Budget", ok, msgs))

    all_pass = True
    for i, (name, ok, msgs) in enumerate(checks, 1):
        status = "PASS" if ok else "FAIL"
        print(f"[{i}/6] {name} {'.' * (40 - len(name))} {status}")
        for msg in msgs:
            print(msg)
        print()
        if not ok:
            all_pass = False

    overall = "PASS" if all_pass else "FAIL"
    print(f"=== OVERALL: {overall} ===")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
