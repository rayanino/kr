"""Smoke test: run normalize + validate on all available fixtures.

Run after Session 6 build to verify validation doesn't false-positive
on real Shamela data.

Sources:
  1. tests/fixtures/shamela_real/ (13 original fixtures)
  2. tests/fixtures/shamela_extended/ (50 extended fixtures)
  3. shamela-export-samples/ (20K+ local samples — if directory exists, sample 50 randomly)

Usage:
  python tools/smoke_test_validation.py
"""

from __future__ import annotations

import io
import random
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.src.validation import validate_package
from engines.source.contracts import (
    InferredFieldConfidence,
    ScholarReference,
    SourceMetadata,
    TrustworthinessFactor,
)


def _make_smoke_metadata(source_id: str) -> SourceMetadata:
    """Build a SourceMetadata with sensible defaults for smoke testing."""
    return SourceMetadata(
        source_id=source_id,
        work_id=f"wrk_{source_id}",
        human_label=f"Smoke test: {source_id}",
        title_arabic="كتاب الاختبار",
        author=ScholarReference(
            canonical_id="sch_00001",
            name_arabic="المؤلف",
            confidence=1.0,
            source_of_identification="smoke_test",
        ),
        science_scope=["nahw"],
        genre="sharh",
        source_format="shamela_html",
        authority_level="primary",
        structural_format="prose",
        is_multi_layer=False,
        text_layers=[],
        trust_tier="verified",
        trust_score=0.85,
        trust_factors=[
            TrustworthinessFactor(
                name="author_standing", weight=0.3, score=0.9, reason="smoke_test",
            ),
        ],
        trust_reason="smoke_test",
        text_fidelity="high",
        text_fidelity_reason="smoke_test",
        confidence_scores=InferredFieldConfidence(
            genre=1.0, science_scope=1.0, structural_format=1.0, authority_level=1.0,
        ),
        status="acquired",
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen/",
        frozen_hash="smoke_test",
        frozen_file_hashes={"test.htm": "smoke_test"},
    )


def run_fixture(fixture_path: Path, source_id: str) -> tuple[str, str, int, str]:
    """Run normalize + validate on a single fixture.

    Returns: (source_id, status, warning_count, error_detail)
    """
    try:
        metadata = _make_smoke_metadata(source_id)
        package = normalize_source(fixture_path, metadata)
        result = validate_package(package, metadata)

        if not result.passed:
            error_msgs = "; ".join(e.message for e in result.fatal_errors)
            return source_id, "FATAL", len(result.warnings), error_msgs
        elif result.warnings:
            return source_id, "WARN", len(result.warnings), ""
        else:
            return source_id, "PASS", 0, ""
    except Exception as e:
        return source_id, "ERROR", 0, f"{type(e).__name__}: {e}"


def main() -> int:
    project_root = Path(__file__).parent.parent
    real_dir = project_root / "tests" / "fixtures" / "shamela_real"
    extended_dir = project_root / "tests" / "fixtures" / "shamela_extended"
    local_dir = project_root / "shamela-export-samples"

    results: list[tuple[str, str, int, str]] = []

    # 1. Real fixtures (13)
    print("=" * 60)
    print("Smoke Test: Normalization + Validation on Real Fixtures")
    print("=" * 60)

    if real_dir.exists():
        fixture_dirs = sorted(
            d for d in real_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
        print(f"\nReal fixtures: {len(fixture_dirs)}")
        for fdir in fixture_dirs:
            htm_files = list(fdir.glob("*.htm"))
            if not htm_files:
                print(f"  {fdir.name}: SKIP (no .htm file)")
                continue
            source_id, status, warns, error = run_fixture(htm_files[0], fdir.name)
            results.append((source_id, status, warns, error))
            marker = {"PASS": "OK", "WARN": "!!", "FATAL": "XX", "ERROR": "EE"}[status]
            line = f"  [{marker}] {source_id}: {status}"
            if warns:
                line += f" ({warns} warnings)"
            if error:
                line += f" - {error[:100]}"
            print(line)
    else:
        print(f"\nReal fixture dir not found: {real_dir}")

    # 2. Extended fixtures (50)
    if extended_dir.exists():
        ext_dirs = sorted(
            d for d in extended_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
        print(f"\nExtended fixtures: {len(ext_dirs)}")
        for fdir in ext_dirs:
            htm_files = list(fdir.glob("*.htm"))
            if not htm_files:
                continue
            source_id, status, warns, error = run_fixture(htm_files[0], fdir.name)
            results.append((source_id, status, warns, error))
            marker = {"PASS": "OK", "WARN": "!!", "FATAL": "XX", "ERROR": "EE"}[status]
            line = f"  [{marker}] {source_id}: {status}"
            if warns:
                line += f" ({warns} warnings)"
            if error:
                line += f" - {error[:100]}"
            print(line)
    else:
        print(f"\nExtended fixture dir not found: {extended_dir}")

    # 3. Local 20K sample (if available)
    if local_dir.exists():
        all_htm = list(local_dir.rglob("*.htm"))
        sample_size = min(50, len(all_htm))
        sample = random.sample(all_htm, sample_size) if len(all_htm) > sample_size else all_htm
        print(f"\nLocal samples: {sample_size} of {len(all_htm)} available")
        local_results: list[tuple[str, str, int, str]] = []
        for htm_file in sample:
            source_id = htm_file.stem
            sid, status, warns, error = run_fixture(htm_file, source_id)
            local_results.append((sid, status, warns, error))
            marker = {"PASS": "OK", "WARN": "!!", "FATAL": "XX", "ERROR": "EE"}[status]
            line = f"  [{marker}] {sid}: {status}"
            if warns:
                line += f" ({warns} warnings)"
            if error:
                line += f" - {error[:80]}"
            print(line)

        local_pass = sum(1 for _, s, _, _ in local_results if s in ("PASS", "WARN"))
        local_fatal = sum(1 for _, s, _, _ in local_results if s == "FATAL")
        local_error = sum(1 for _, s, _, _ in local_results if s == "ERROR")
        print(f"\n  Local summary: {local_pass}/{sample_size} passed, "
              f"{local_fatal} fatals, {local_error} errors")
    else:
        print(f"\nLocal samples: not found (shamela-export-samples/)")

    # Summary
    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(1 for _, s, _, _ in results if s in ("PASS", "WARN"))
    warnings = sum(w for _, _, w, _ in results)
    fatals = sum(1 for _, s, _, _ in results if s == "FATAL")
    errors = sum(1 for _, s, _, _ in results if s == "ERROR")

    print(f"SUMMARY: {passed}/{total} passed, {warnings} total warnings, "
          f"{fatals} fatals, {errors} errors")

    if fatals > 0:
        print("\nFATAL FAILURES:")
        for sid, status, _, error in results:
            if status == "FATAL":
                print(f"  {sid}: {error}")

    if errors > 0:
        print("\nERRORS:")
        for sid, status, _, error in results:
            if status == "ERROR":
                print(f"  {sid}: {error}")

    print("=" * 60)

    # Exit code: 0 if no fatals on standard fixtures
    if fatals == 0 and errors == 0:
        print("RESULT: PASS")
        return 0
    else:
        print("RESULT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
