"""Verify argument flow marker false positive rates on all fixtures.

Usage: python tools/verify_boundary_markers.py

Runs all argument markers against all fixture pages, reporting:
- Per-marker fire rate in last-200-char tails
- Leading/trailing boundary false positive counts
- Overall mid_argument classification rate per fixture
- SPEC concrete example trace

This script codifies the empirical probes from the Session 5 review
so they can be re-run instantly after any marker change.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
from engines.normalization.src.boundary_continuity import (
    _check_argument_flow,
    _find_argument_marker,
    _has_terminal_punct,
    _ARGUMENT_CATEGORIES,
    classify_boundary,
)
from engines.normalization.contracts import StructuralMarkers


def _full_pipeline(htm: str) -> list:
    n = ShamelaNormalizer()
    raw = n._pass1_parse(htm, volume=1, seq_offset=0)
    sep = n._pass2_separate(raw)
    return n._pass3_clean(sep)


def main() -> None:
    FIXTURES = Path("tests/fixtures/shamela_real")
    if not FIXTURES.exists():
        print(f"ERROR: {FIXTURES} not found. Run from repo root.")
        sys.exit(1)

    # Collect all markers
    all_openers = []
    all_closers = []
    for cat in _ARGUMENT_CATEGORIES:
        for p in cat.opening_patterns:
            all_openers.append((cat.name, p))
        for p in cat.closing_patterns:
            all_closers.append((cat.name, p))

    total_pages = 0
    total_mid_arg = 0
    per_fixture: list[tuple[str, int, int]] = []

    # Per-marker stats
    marker_hits: dict[str, int] = {}
    marker_fp: dict[str, int] = {}

    for fixture_dir in sorted(FIXTURES.iterdir()):
        if not fixture_dir.is_dir():
            continue
        book = fixture_dir / "book.htm"
        if not book.exists():
            continue
        htm = book.read_text(encoding="utf-8")
        cleaned = _full_pipeline(htm)
        n_pages = len(cleaned)
        total_pages += n_pages

        mid_arg = 0
        for page in cleaned:
            if _check_argument_flow(page.primary_text):
                mid_arg += 1

            # Check all markers in tail
            tail = page.primary_text[-200:] if len(page.primary_text) > 200 else page.primary_text
            for _, marker in all_openers + all_closers:
                pos = 0
                while True:
                    idx = tail.find(marker, pos)
                    if idx == -1:
                        break
                    marker_hits[marker] = marker_hits.get(marker, 0) + 1
                    # Check leading boundary
                    if idx > 0 and tail[idx - 1] not in (
                        " ", "\t", "\n", "\r", ".", "؟", "!", "؛", "،", ":"
                    ):
                        marker_fp[marker] = marker_fp.get(marker, 0) + 1
                    pos = idx + 1

        total_mid_arg += mid_arg
        per_fixture.append((fixture_dir.name, n_pages, mid_arg))

    # Report
    print("=" * 60)
    print("  Boundary Marker Verification Report")
    print("=" * 60)
    print()

    print(f"Total pages across fixtures: {total_pages}")
    print(f"Total mid_argument pages: {total_mid_arg} ({total_mid_arg/total_pages*100:.1f}%)")
    print()

    print("── Per-fixture mid_argument rates ──")
    for name, pages, mid in per_fixture:
        pct = mid / pages * 100 if pages else 0
        flag = " ⚠️" if pct > 15 else ""
        if mid > 0:
            print(f"  {name:25s}: {mid:3d}/{pages:4d} ({pct:5.1f}%){flag}")
    print()

    print("── Per-marker fire rates (last 200 chars) ──")
    for marker in sorted(marker_hits, key=lambda m: -marker_hits[m]):
        hits = marker_hits[marker]
        fps = marker_fp.get(marker, 0)
        pct = hits / total_pages * 100
        fp_pct = fps / hits * 100 if hits else 0
        flag = " ⚠️ FP!" if fp_pct > 5 else ""
        print(f"  {marker:20s}: {hits:4d} hits ({pct:5.1f}%), {fps} FP ({fp_pct:.0f}%){flag}")
    print()

    # SPEC §4.B.8 concrete example trace
    print("── SPEC §4.B.8 Concrete Example Trace ──")
    from engines.normalization.src.normalizers.shamela import CleanedPage

    page234 = CleanedPage(
        unit_index=233, volume=1,
        primary_text="ولنا حديث ابن عباس رضي الله عنهما أن النبي \uFDFA قال:",
        bold_spans=[],
    )
    page235 = CleanedPage(
        unit_index=234, volume=1,
        primary_text="«لا تُنكح الأيم حتى تُستأمر» متفق عليه.\nوالأيم هي الثيب.",
        bold_spans=[],
    )
    markers = StructuralMarkers(
        heading_detected=False, heading_text=None, heading_confidence=None,
    )
    result = classify_boundary(page234, page235, None, markers, is_volume_boundary=False)
    type_ok = result.type.value == "mid_argument"
    method_ok = result.detection_method.value == "argument_flow"
    conf_ok = 0.60 <= result.confidence <= 0.80
    print(f"  type={result.type.value} (expect mid_argument): {'✓' if type_ok else '✗ FAIL'}")
    print(f"  method={result.detection_method.value} (expect argument_flow): {'✓' if method_ok else '✗ FAIL'}")
    print(f"  confidence={result.confidence} (expect 0.60-0.80): {'✓' if conf_ok else '✗ FAIL'}")
    print()

    if all([type_ok, method_ok, conf_ok]) and total_mid_arg > 0:
        print("✓ All checks pass.")
    else:
        print("✗ Issues detected — review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
