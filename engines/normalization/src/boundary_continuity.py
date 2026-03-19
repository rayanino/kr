"""Cross-page boundary continuity — SPEC §4.B.8.

Classifies the boundary between consecutive content units:
  - mid_sentence: no terminal punctuation, text continues
  - mid_paragraph: sentence ends, paragraph continues
  - mid_argument: scholarly argument structure spans boundary
  - section_break: heading detected on next page
  - division_break: volume boundary
  - unknown: insufficient signal

Signal priority: heading > argument > punctuation.
D7: Conditional reasoning markers (إذا) excluded — too frequent (L-008).

Arabic-safe rules: no \\b, no \\d, no \\w for Arabic text.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from engines.normalization.contracts import (
    BoundaryContinuity,
    BoundaryContinuityType,
    ContinuityDetectionMethod,
    HeadingConfidence,
    StructuralMarkers,
)
from engines.normalization.src.errors import NormErrorCode

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from engines.normalization.src.normalizers.shamela import CleanedPage


# ──────────────────────────────────────────────────────────────────
# Terminal punctuation (sentence-ending)
# ──────────────────────────────────────────────────────────────────

_TERMINAL_PUNCT = frozenset({".", "۔", "؟", "?", "!", "؛"})

# ──────────────────────────────────────────────────────────────────
# Connective particles at page start
# ──────────────────────────────────────────────────────────────────

_CONNECTIVE_PARTICLES = ("و", "ف", "ثم")

# ──────────────────────────────────────────────────────────────────
# Argument markers — 3 categories (D7: conditionals excluded)
# ──────────────────────────────────────────────────────────────────


@dataclass
class _ArgumentCategory:
    """A category of scholarly argument markers."""
    name: str
    opening_patterns: list[str] = field(default_factory=list)
    closing_patterns: list[str] = field(default_factory=list)


_ARGUMENT_CATEGORIES: list[_ArgumentCategory] = [
    _ArgumentCategory(
        name="evidence_chain",
        opening_patterns=[
            "ولنا", "واستدل", "والدليل", "لأن", "بدليل",
            "ودليله", "واحتجوا",
        ],
        closing_patterns=[
            "فثبت", "فدل", "وهذا يدل", "فظهر",
            "ونوقش",  # "it was discussed/critiqued" — closes evidence
        ],
    ),
    _ArgumentCategory(
        name="position_statement",
        opening_patterns=[
            "وذهب", "وقال", "ومذهب", "واختار",
            "القول الأول",
        ],
        closing_patterns=[
            "والراجح", "والصواب", "والمختار", "والأظهر",
            "والصحيح",
        ],
    ),
    _ArgumentCategory(
        name="objection_response",
        opening_patterns=["فإن قيل", "واعترض", "وأورد"],
        closing_patterns=["قلنا", "والجواب", "فالجواب", "ويرد عليه"],
    ),
]


def _has_word_boundary_after(text: str, match_end: int) -> bool:
    """Check that the character after match_end is space, punct, or end.

    Arabic lacks reliable \\b — clitics (و, ب, ك, ل) attach without
    whitespace. We check for word-ending conditions manually.
    """
    if match_end >= len(text):
        return True
    ch = text[match_end]
    return ch in (" ", "\t", "\n", "\r") or ch in _TERMINAL_PUNCT or ch in ("،", ":", "؛")


def _find_argument_marker(
    text: str, patterns: list[str],
) -> bool:
    """Check if any pattern appears in text with proper word boundary."""
    for pattern in patterns:
        idx = 0
        while True:
            pos = text.find(pattern, idx)
            if pos == -1:
                break
            if _has_word_boundary_after(text, pos + len(pattern)):
                return True
            idx = pos + 1
    return False


def _check_argument_flow(
    current_text: str,
) -> str | None:
    """Check if an argument opener in last 200 chars has no closer on page.

    Returns the category name if mid-argument, None otherwise.
    """
    tail = current_text[-200:] if len(current_text) > 200 else current_text

    for cat in _ARGUMENT_CATEGORIES:
        if _find_argument_marker(tail, cat.opening_patterns):
            # Check if there's a closer ANYWHERE on the page
            if not _find_argument_marker(current_text, cat.closing_patterns):
                return cat.name
    return None


def _check_next_page_continuation(
    next_text: str,
) -> str | None:
    """Check if first 200 chars of next page contain a continuation marker.

    SPEC: "OR when the first 200 characters of the next page contain
    an argument continuation marker."
    """
    head = next_text[:200] if len(next_text) > 200 else next_text
    for cat in _ARGUMENT_CATEGORIES:
        if _find_argument_marker(head, cat.closing_patterns):
            return cat.name
    return None


def _has_terminal_punct(text: str) -> bool:
    """Check if text ends with terminal punctuation (ignoring trailing whitespace)."""
    stripped = text.rstrip()
    if not stripped:
        return False
    return stripped[-1] in _TERMINAL_PUNCT


def _get_connective_hint(next_text: str) -> str | None:
    """Check if next page starts with a connective particle."""
    stripped = next_text.lstrip()
    for particle in _CONNECTIVE_PARTICLES:
        if stripped.startswith(particle):
            return f"next page starts with '{particle}'"
    return None


# ──────────────────────────────────────────────────────────────────
# Heading confidence → boundary confidence mapping
# ──────────────────────────────────────────────────────────────────

_HEADING_CONFIDENCE_MAP: dict[HeadingConfidence, float] = {
    HeadingConfidence.CONFIRMED: 0.95,
    HeadingConfidence.HIGH: 0.95,
    HeadingConfidence.MEDIUM: 0.85,
    HeadingConfidence.LOW: 0.75,
    HeadingConfidence.MINIMAL: 0.65,
}


# ──────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────


def classify_boundary(
    current_page: CleanedPage,
    next_page: CleanedPage,
    current_markers: StructuralMarkers | None,
    next_markers: StructuralMarkers | None,
    is_volume_boundary: bool,
) -> BoundaryContinuity:
    """Classify the boundary between current_page and next_page.

    Signal priority: heading > argument > punctuation.
    """
    hint = _get_connective_hint(next_page.primary_text)

    # Priority 0: next page blank/image-only
    if next_page.is_blank or next_page.is_image_only or len(next_page.primary_text.strip()) == 0:
        logger.info(
            "%s: boundary after unit %d — next page blank/image",
            NormErrorCode.CONTINUITY_UNKNOWN.value,
            current_page.unit_index,
        )
        return BoundaryContinuity(
            type=BoundaryContinuityType.UNKNOWN,
            confidence=0.30,
            detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
            continuation_hint=hint,
        )

    # Priority 1: volume boundary
    if is_volume_boundary:
        return BoundaryContinuity(
            type=BoundaryContinuityType.DIVISION_BREAK,
            confidence=0.95,
            detection_method=ContinuityDetectionMethod.STRUCTURAL_MARKER,
            continuation_hint=hint,
        )

    # Priority 2: heading on next page
    if next_markers is not None and next_markers.heading_detected:
        conf_level = next_markers.heading_confidence or HeadingConfidence.MEDIUM
        boundary_conf = _HEADING_CONFIDENCE_MAP.get(conf_level, 0.85)
        return BoundaryContinuity(
            type=BoundaryContinuityType.SECTION_BREAK,
            confidence=boundary_conf,
            detection_method=ContinuityDetectionMethod.STRUCTURAL_MARKER,
            continuation_hint=hint,
        )

    # Priority 3: argument flow (current page opener OR next page continuation)
    arg_category = _check_argument_flow(current_page.primary_text)
    if arg_category is None:
        arg_category = _check_next_page_continuation(next_page.primary_text)
    if arg_category is not None:
        has_terminal = _has_terminal_punct(current_page.primary_text)
        return BoundaryContinuity(
            type=BoundaryContinuityType.MID_ARGUMENT,
            # SPEC range: 0.60-0.80. Terminal punct lowers confidence.
            confidence=0.70 if has_terminal else 0.80,
            detection_method=ContinuityDetectionMethod.ARGUMENT_FLOW,
            continuation_hint=hint or f"open {arg_category}",
        )

    # Priority 4: punctuation analysis
    if _has_terminal_punct(current_page.primary_text):
        # 4a: terminal punct present → mid_paragraph
        return BoundaryContinuity(
            type=BoundaryContinuityType.MID_PARAGRAPH,
            confidence=0.75,
            detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
            continuation_hint=hint,
        )
    else:
        # 4b: no terminal punct → mid_sentence
        return BoundaryContinuity(
            type=BoundaryContinuityType.MID_SENTENCE,
            confidence=0.90,
            detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
            continuation_hint=hint,
        )
