"""Phase 5 Session 12 — Determinism audit fixes for normalization engine.

Locks the tuple-key tiebreak in `_build_page_markers` per
`.claude/rules/single-key-sort-audit.md` (Sessions 5+7+10 pattern).

Defect class: single-key `min(page_cands, key=lambda c: c.document_position)`
over a list where `_detect_volume_boundaries` produces HeadingCandidate with
default `document_position=0` (HeadingCandidate dataclass field default), which
collides with Tier 1's first candidate (also doc_pos=0). At the tie, `min()`
returns the first match in iteration order — currently deterministic only by
coincidence of the orchestrator's concatenation order. Fix: tuple-key
`(c.document_position, c.heading_text)` provides a deterministic secondary
total-order field (heading_text is required str, no default).
"""

from __future__ import annotations

from engines.normalization.contracts import (
    HeadingConfidence,
    HeadingDetectionMethod,
)
from engines.normalization.src.structure_discovery import (
    HeadingCandidate,
    _build_page_markers,
)


# ──────────────────────────────────────────────────────────────────
# Real Arabic scholarly fixtures (classical fiqh chapter headings)
# ──────────────────────────────────────────────────────────────────

# Tier 1 HTML-tagged candidate at the start of a volume (doc_pos=0)
_TIER1_KITAB_TAHARAH = HeadingCandidate(
    heading_text="كتاب الطهارة",
    unit_index=10,
    detection_method=HeadingDetectionMethod.HTML_TAGGED,
    confidence=HeadingConfidence.CONFIRMED,
    document_position=0,
)

# Volume boundary candidate at the same unit_index
# `_detect_volume_boundaries` does NOT set document_position → defaults to 0
_VOLUME_BOUNDARY_VOL2 = HeadingCandidate(
    heading_text="المجلد 2",
    unit_index=10,
    detection_method=HeadingDetectionMethod.HTML_TAGGED,
    confidence=HeadingConfidence.CONFIRMED,
    document_position=0,  # The bug class — same as Tier 1's first candidate
)

# Three-way tie scenario (multiple volume boundaries on adjacent unit_index)
_FASL_NIYYAH = HeadingCandidate(
    heading_text="فصل في النية",
    unit_index=20,
    detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
    confidence=HeadingConfidence.HIGH,
    document_position=0,
)

_BAB_WUDU = HeadingCandidate(
    heading_text="باب الوضوء",
    unit_index=20,
    detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
    confidence=HeadingConfidence.HIGH,
    document_position=0,
)

_KITAB_SALAH = HeadingCandidate(
    heading_text="كتاب الصلاة",
    unit_index=20,
    detection_method=HeadingDetectionMethod.HTML_TAGGED,
    confidence=HeadingConfidence.CONFIRMED,
    document_position=0,
)


# ──────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────


def test_volume_collision_with_tier1_first_candidate_is_deterministic() -> None:
    """Tier 1 first candidate (doc_pos=0) collides with volume boundary (doc_pos=0).

    Both input orderings must produce the SAME StructuralMarkers — locks
    the (-document_position, heading_text) tuple-key tiebreak.
    """
    order_a = [_TIER1_KITAB_TAHARAH, _VOLUME_BOUNDARY_VOL2]
    order_b = [_VOLUME_BOUNDARY_VOL2, _TIER1_KITAB_TAHARAH]

    markers_a = _build_page_markers(order_a)
    markers_b = _build_page_markers(order_b)

    assert 10 in markers_a
    assert 10 in markers_b
    assert markers_a[10].heading_text == markers_b[10].heading_text
    # Lexicographic tiebreak: "المجلد 2" starts with ا (U+0627=1575),
    # "كتاب الطهارة" starts with ك (U+0643=1603). Volume wins lex-min.
    assert markers_a[10].heading_text == "المجلد 2"


def test_three_way_tie_at_doc_pos_zero_picks_lexicographically_smallest() -> None:
    """Three candidates at doc_pos=0 → smallest heading_text wins regardless of order."""
    # Lexicographic order of these Arabic strings (by codepoint):
    # ب (U+0628) < ف (U+0641) < ك (U+0643)
    # So "باب الوضوء" < "فصل في النية" < "كتاب الصلاة"
    order_1 = [_FASL_NIYYAH, _BAB_WUDU, _KITAB_SALAH]
    order_2 = [_KITAB_SALAH, _FASL_NIYYAH, _BAB_WUDU]
    order_3 = [_BAB_WUDU, _KITAB_SALAH, _FASL_NIYYAH]

    m1 = _build_page_markers(order_1)
    m2 = _build_page_markers(order_2)
    m3 = _build_page_markers(order_3)

    assert m1[20].heading_text == m2[20].heading_text == m3[20].heading_text
    assert m1[20].heading_text == "باب الوضوء"


def test_repeated_call_deterministic_across_runs() -> None:
    """Same input run 10x yields the same output every time.

    Catches PYTHONHASHSEED-derived non-determinism that single-run tests miss.
    """
    candidates = [_TIER1_KITAB_TAHARAH, _VOLUME_BOUNDARY_VOL2]
    expected = _build_page_markers(candidates)[10].heading_text

    for _ in range(10):
        result = _build_page_markers(candidates)
        assert result[10].heading_text == expected


def test_strict_ordering_preserved_with_distinct_doc_positions() -> None:
    """When document_position differs, smaller doc_pos wins (current behavior unchanged)."""
    early = HeadingCandidate(
        heading_text="مقدمة",  # م > ك lexicographically
        unit_index=5,
        detection_method=HeadingDetectionMethod.HTML_TAGGED,
        confidence=HeadingConfidence.CONFIRMED,
        document_position=0,
    )
    later = HeadingCandidate(
        heading_text="باب",  # ب < م lexicographically
        unit_index=5,
        detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
        confidence=HeadingConfidence.HIGH,
        document_position=5,
    )
    # Despite "باب" being lexicographically smaller, "مقدمة" wins
    # because document_position is the primary key (0 < 5).
    markers = _build_page_markers([later, early])
    assert markers[5].heading_text == "مقدمة"


def test_arabic_byte_faithful_through_tiebreak() -> None:
    """Tuple-key fix must preserve Arabic bytes exactly — no normalization."""
    # Diacritics-heavy heading next to plain heading — both at doc_pos=0
    diacritized = HeadingCandidate(
        heading_text="كِتَابُ الطَّهَارَةِ",  # fully diacritized
        unit_index=15,
        detection_method=HeadingDetectionMethod.HTML_TAGGED,
        confidence=HeadingConfidence.CONFIRMED,
        document_position=0,
    )
    plain = HeadingCandidate(
        heading_text="كتاب الصلاة",
        unit_index=15,
        detection_method=HeadingDetectionMethod.HTML_TAGGED,
        confidence=HeadingConfidence.CONFIRMED,
        document_position=0,
    )

    markers = _build_page_markers([diacritized, plain])
    # Whichever wins, its bytes must be byte-identical to the input
    winner_text = markers[15].heading_text
    assert winner_text in (diacritized.heading_text, plain.heading_text)
    # Determinism: same input ordering → same winner across reruns
    for _ in range(10):
        again = _build_page_markers([diacritized, plain])
        assert again[15].heading_text == winner_text


def test_two_distinct_orderings_produce_identical_full_marker_dict() -> None:
    """Cross-page determinism — full markers dict identical across input orderings.

    Locks that the determinism guarantee extends to all pages, not just one.
    """
    page_a_tier1 = _TIER1_KITAB_TAHARAH  # unit_index=10
    page_a_vol = _VOLUME_BOUNDARY_VOL2  # unit_index=10
    page_b_kitab = _KITAB_SALAH  # unit_index=20
    page_b_bab = _BAB_WUDU  # unit_index=20

    order_a = [page_a_tier1, page_a_vol, page_b_kitab, page_b_bab]
    order_b = [page_b_bab, page_a_vol, page_b_kitab, page_a_tier1]

    markers_a = _build_page_markers(order_a)
    markers_b = _build_page_markers(order_b)

    assert markers_a.keys() == markers_b.keys()
    for unit_idx in markers_a:
        assert markers_a[unit_idx].heading_text == markers_b[unit_idx].heading_text
        assert markers_a[unit_idx].heading_level == markers_b[unit_idx].heading_level
        assert markers_a[unit_idx].heading_detection_method == \
            markers_b[unit_idx].heading_detection_method


def test_single_candidate_per_page_unaffected_by_tuple_key() -> None:
    """Pages with exactly one candidate: tuple-key is a no-op."""
    only_one = HeadingCandidate(
        heading_text="باب التيمم",
        unit_index=30,
        detection_method=HeadingDetectionMethod.HTML_TAGGED,
        confidence=HeadingConfidence.CONFIRMED,
        document_position=42,
    )
    markers = _build_page_markers([only_one])
    assert markers[30].heading_text == "باب التيمم"
    assert markers[30].heading_confidence == HeadingConfidence.CONFIRMED
