"""E2E Fix Verification — checks 4 mandatory fixes against pipeline output.

Reads results from tests/results/source_engine/e2e_validation/ and verifies
each fix produces the expected behavioral change. See CLAUDE_CODE_E2E_VALIDATION.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RESULTS_DIR = Path("tests/results/source_engine/e2e_validation")

BOOKS = [
    {
        "num": 1,
        "name": "ملء العيبة بما جمع بطول الغيبة - ج ٥",
        "fix": "Fix 1 rihlah",
    },
    {
        "num": 2,
        "name": "النكت على شرح النووي على صحيح مسلم",
        "fix": "Fix 2 hashiyah",
    },
    {
        "num": 3,
        "name": "أساليب بلاغية",
        "fix": "Fix 3 death_date",
    },
    {
        "num": 4,
        "name": "صحيح البخاري - ن عطاءات العلم",
        "fix": "Control",
    },
    {
        "num": 5,
        "name": "إعلام الموقعين عن رب العالمين - ط العلمية",
        "fix": "Fix 1 usul_fiqh",
    },
]


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_genre_from_llm_responses(book_dir: Path) -> str:
    """Extract genre from LLM responses (for gate_abort books without genre in result.json)."""
    llm_dir = book_dir / "llm_responses"
    if not llm_dir.exists():
        return ""
    for f in llm_dir.iterdir():
        if f.suffix == ".json":
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                parsed = data.get("parsed")
                if parsed:
                    return parsed.get("genre", "")
            except (json.JSONDecodeError, KeyError):
                continue
    return ""


def load_death_dates_from_llm_responses(book_dir: Path) -> list[tuple[str, int | None]]:
    """Extract death_date_hijri from each model's LLM response."""
    llm_dir = book_dir / "llm_responses"
    results: list[tuple[str, int | None]] = []
    if not llm_dir.exists():
        return results
    for f in sorted(llm_dir.iterdir()):
        if f.suffix == ".json":
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                model_id = data.get("model_id", f.stem)
                parsed = data.get("parsed")
                if parsed:
                    author_id = parsed.get("author_identification", {})
                    death = author_id.get("death_date_hijri") if isinstance(author_id, dict) else None
                    results.append((model_id, death))
            except (json.JSONDecodeError, KeyError):
                continue
    return results


def verify_book_1(result: dict, book_dir: Path) -> tuple[str, str]:
    """Fix 1: rihlah genre."""
    genre = result.get("genre", "")
    if genre == "rihlah":
        return "PASS", f"genre={genre}"
    return "NEEDS_REVIEW", f"genre={genre} (expected rihlah)"


def verify_book_2(result: dict, book_dir: Path) -> tuple[str, str]:
    """Fix 2: hashiyah + empty layers → gate_abort."""
    status = result.get("status", "")
    error_code = result.get("error_code", "")
    gate_errors = result.get("gate_errors", [])

    # For gate_abort: gate_errors is the authoritative source of the consensus genre,
    # since individual LLM responses may disagree (one says hashiyah, other says other).
    # The consensus picks one, and the gate fires on the consensus result.
    hashiyah_gate_fired = any("hashiyah" in str(e) for e in gate_errors)

    # Get genre from result.json (success) or LLM responses (gate_abort fallback)
    if status == "gate_abort":
        genre = load_genre_from_llm_responses(book_dir)
    else:
        genre = result.get("genre", "")

    if status == "gate_abort" and hashiyah_gate_fired:
        # Fix 2 working: consensus chose hashiyah, gate fired correctly
        issues = []
        if error_code != "SRC_LOW_CONFIDENCE":
            issues.append(f"error_code={error_code} (expected SRC_LOW_CONFIDENCE)")
        if issues:
            return "FAIL", "; ".join(issues)
        return "PASS", f"consensus_genre=hashiyah, status=gate_abort, error_code=SRC_LOW_CONFIDENCE"

    if genre == "hashiyah" and status == "success":
        return "FAIL", "genre=hashiyah but status=success (fix broken — hashiyah+no-layers should gate)"

    return "NEEDS_REVIEW", f"genre={genre}, status={status} (LLM changed classification)"


def verify_book_3(result: dict, book_dir: Path) -> tuple[str, str]:
    """Fix 3: death_date_hijri in needs_review_fields."""
    status = result.get("status", "")
    if status != "success":
        return "FAIL", f"status={status} (expected success)"

    needs_review = result.get("needs_review_fields", [])
    if "death_date_hijri" in needs_review:
        return "PASS", f"needs_review_fields contains death_date_hijri"

    # Check if ERR-03 pattern still applies
    death_dates = load_death_dates_from_llm_responses(book_dir)
    detail = f"needs_review_fields={needs_review} (missing death_date_hijri). "
    if death_dates:
        models_with_date = [(m, d) for m, d in death_dates if d is not None]
        models_without_date = [(m, d) for m, d in death_dates if d is None]
        if models_with_date and models_without_date:
            detail += (
                f"ERR-03 pattern PRESENT: {models_with_date[0][0]}={models_with_date[0][1]}, "
                f"{models_without_date[0][0]}=None. Fix should have fired."
            )
            return "FAIL", detail
        elif len(models_with_date) == len(death_dates):
            detail += "Both models agree on death date — ERR-03 pattern no longer applies."
        elif len(models_without_date) == len(death_dates):
            detail += "Neither model returned death date — ERR-03 pattern no longer applies."
        else:
            detail += f"Death dates: {death_dates}"
    return "NEEDS_REVIEW", detail


def verify_book_4(result: dict, book_dir: Path) -> tuple[str, str]:
    """Control: no fix should change behavior."""
    status = result.get("status", "")
    genre = result.get("genre", "")
    if status == "success" and genre == "hadith_collection":
        return "PASS", f"status=success, genre=hadith_collection"
    return "FAIL", f"status={status}, genre={genre} (expected success + hadith_collection)"


def verify_book_5(result: dict, book_dir: Path) -> tuple[str, str]:
    """Fix 1: usul_al_fiqh genre."""
    genre = result.get("genre", "")
    if genre == "usul_al_fiqh":
        return "PASS", f"genre={genre}"
    return "NEEDS_REVIEW", f"genre={genre} (expected usul_al_fiqh)"


VERIFIERS = {
    1: verify_book_1,
    2: verify_book_2,
    3: verify_book_3,
    4: verify_book_4,
    5: verify_book_5,
}


def main() -> None:
    results: list[tuple[int, str, str, str]] = []

    # Read total cost from COST_LOG.json (pipeline tracks cumulative cost)
    cost_log_path = Path("tests/results/source_engine/COST_LOG.json")
    cost_log = load_json(cost_log_path)
    # The pipeline added this run's cost to the "C" phase entry.
    # Approximate: 5 books * ~0.10 EUR/book = ~0.50 EUR
    phase_c_cost = cost_log.get("phases", {}).get("C", {}).get("cost_eur", 0) if cost_log else 0

    for book in BOOKS:
        num = book["num"]
        name = book["name"]
        fix = book["fix"]
        book_dir = RESULTS_DIR / name

        result = load_json(book_dir / "result.json")
        if result is None:
            results.append((num, fix, "FAIL", f"result.json not found at {book_dir}"))
            continue

        verdict, detail = VERIFIERS[num](result, book_dir)
        results.append((num, fix, verdict, detail))

    # Sum per-book costs: gate_abort books have cost in result.json,
    # success books lack it (cost is only in the tracking dict, not the metadata dump).
    # Use 0.10 EUR per book (pipeline default estimate) for books missing the field.
    total_cost = 0.0
    for book in BOOKS:
        r = load_json(RESULTS_DIR / book["name"] / "result.json")
        if r:
            total_cost += r.get("cost_estimate_eur", 0.10)

    # Print summary
    print()
    print("E2E Fix Validation Results")
    print("=" * 60)
    for num, fix, verdict, detail in results:
        label = f"Book {num} ({fix}):"
        print(f"  {label:<30} {verdict}")
        if verdict != "PASS":
            print(f"    -> {detail}")

    print()
    print(f"  Total cost: \u20ac{total_cost:.2f}")

    all_pass = all(v == "PASS" for _, _, v, _ in results)
    has_fail = any(v == "FAIL" for _, _, v, _ in results)
    print(f"  All fixes verified: {'YES' if all_pass else 'NO'}")

    if has_fail:
        print("\n  FAILURES detected — see details above.")

    # Print detailed results for non-PASS
    needs_detail = [(n, f, v, d) for n, f, v, d in results if v != "PASS"]
    if needs_detail:
        print()
        print("Detailed Results")
        print("-" * 60)
        for num, fix, verdict, detail in needs_detail:
            print(f"  Book {num} ({fix}): {verdict}")
            print(f"    {detail}")

    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
