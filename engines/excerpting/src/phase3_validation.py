"""Phase 3: Output Validation (SPEC §7.4).

Runs V-P3-1 through V-P3-9 on ExcerptRecords before writing output.
Validation detects problems and emits error codes — it does NOT auto-correct,
with the sole exception of V-P3-8 (orphan footnote removal).
"""

from __future__ import annotations

import logging
import re

from engines.excerpting.contracts import (
    ExcerptRecord,
    ExcerptingErrorCodes,
    ScholarlyFunction,
    SelfContainmentLevel,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Quran reference data for V-P3-6
# ═══════════════════════════════════════════════════════════════════

# Canonical ayah counts per surah (1-indexed). Source: standard Uthmani mushaf.
QURAN_SURAH_AYAH_COUNTS: dict[int, int] = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75,
    9: 129, 10: 109, 11: 123, 12: 111, 13: 43, 14: 52, 15: 99,
    16: 128, 17: 111, 18: 110, 19: 98, 20: 135, 21: 112, 22: 78,
    23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69,
    30: 60, 31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83,
    37: 182, 38: 88, 39: 75, 40: 85, 41: 54, 42: 53, 43: 89,
    44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29,
    58: 22, 59: 24, 60: 13, 61: 14, 62: 11, 63: 11, 64: 18,
    65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44, 71: 28,
    72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40,
    79: 46, 80: 42, 81: 29, 82: 19, 83: 36, 84: 25, 85: 22,
    86: 17, 87: 19, 88: 26, 89: 30, 90: 20, 91: 15, 92: 21,
    93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8,
    100: 11, 101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4,
    107: 7, 108: 3, 109: 6, 110: 3, 111: 5, 112: 4, 113: 5, 114: 6,
}

# Valid ScholarlyFunction values for V-P3-9
_VALID_SCHOLARLY_FUNCTIONS: set[str] = {sf.value for sf in ScholarlyFunction}


# ═══════════════════════════════════════════════════════════════════
# Whitespace normalization helper for V-P3-2
# ═══════════════════════════════════════════════════════════════════


def _normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace to single space for comparison."""
    return re.sub(r"\s+", " ", text).strip()


# ═══════════════════════════════════════════════════════════════════
# Function 1: validate_excerpt
# ═══════════════════════════════════════════════════════════════════


def validate_excerpt(
    excerpt: ExcerptRecord,
) -> tuple[ExcerptRecord, list[str]]:
    """Run per-excerpt V-P3 checks (§7.4).

    Returns (possibly modified excerpt, list of emitted error codes).
    V-P3-1 and V-P3-7 are batch-level checks — not run here.
    """
    errors: list[str] = []
    modified = excerpt

    # V-P3-2: Primary text integrity
    # First 80 chars of primary_text should match text_snippet after
    # whitespace normalization (collapse runs to single space).
    snippet_normalized = _normalize_whitespace(excerpt.text_snippet)
    primary_first80 = _normalize_whitespace(excerpt.primary_text[:80])
    if snippet_normalized != primary_first80:
        errors.append(ExcerptingErrorCodes.EX_V_002)
        logger.warning(
            "%s: Text integrity check failed for %s. "
            "snippet=%r vs primary_first80=%r",
            ExcerptingErrorCodes.EX_V_002,
            excerpt.excerpt_id,
            snippet_normalized[:40],
            primary_first80[:40],
        )

    # V-P3-3: Author attribution completeness
    if excerpt.primary_author_layer is None:
        errors.append(ExcerptingErrorCodes.EX_M_004)
        logger.error(
            "%s: Null primary_author_layer on %s — this indicates a bug.",
            ExcerptingErrorCodes.EX_M_004,
            excerpt.excerpt_id,
        )

    # V-P3-4: Topic keyword validity
    has_enrichment_failed = "llm_enrichment_failed" in excerpt.review_flags
    topic_count = len(excerpt.excerpt_topic)
    if not has_enrichment_failed and (topic_count < 1 or topic_count > 3):
        errors.append(ExcerptingErrorCodes.EX_M_005)
        logger.warning(
            "%s: Topic keyword count=%d (expected 1-3) for %s.",
            ExcerptingErrorCodes.EX_M_005,
            topic_count,
            excerpt.excerpt_id,
        )

    # V-P3-5: Self-containment consistency
    if (
        excerpt.context_hint is not None
        and excerpt.self_containment != SelfContainmentLevel.PARTIAL
    ):
        errors.append(ExcerptingErrorCodes.EX_M_006)
        logger.warning(
            "%s: context_hint non-null but self_containment=%s for %s.",
            ExcerptingErrorCodes.EX_M_006,
            excerpt.self_containment.value,
            excerpt.excerpt_id,
        )
    elif (
        excerpt.self_containment == SelfContainmentLevel.PARTIAL
        and excerpt.context_hint is None
        and not has_enrichment_failed
    ):
        errors.append(ExcerptingErrorCodes.EX_M_006)
        logger.warning(
            "%s: PARTIAL self_containment but context_hint is null for %s.",
            ExcerptingErrorCodes.EX_M_006,
            excerpt.self_containment.value,
            excerpt.excerpt_id,
        )

    # V-P3-6: Evidence reference integrity (Quran refs)
    for ref in excerpt.evidence_refs:
        if ref.type != "quran":
            continue
        if ref.surah is not None:
            if ref.surah < 1 or ref.surah > 114:
                errors.append(ExcerptingErrorCodes.EX_M_007)
                logger.warning(
                    "%s: Invalid surah=%d for %s.",
                    ExcerptingErrorCodes.EX_M_007,
                    ref.surah,
                    excerpt.excerpt_id,
                )
            elif ref.ayah_start is not None:
                max_ayah = QURAN_SURAH_AYAH_COUNTS.get(ref.surah, 0)
                if ref.ayah_start < 1 or ref.ayah_start > max_ayah:
                    errors.append(ExcerptingErrorCodes.EX_M_007)
                    logger.warning(
                        "%s: Invalid ayah_start=%d for surah %d "
                        "(max=%d) in %s.",
                        ExcerptingErrorCodes.EX_M_007,
                        ref.ayah_start,
                        ref.surah,
                        max_ayah,
                        excerpt.excerpt_id,
                    )
                if ref.ayah_end is not None and (
                    ref.ayah_end < 1 or ref.ayah_end > max_ayah
                ):
                    errors.append(ExcerptingErrorCodes.EX_M_007)
                    logger.warning(
                        "%s: Invalid ayah_end=%d for surah %d "
                        "(max=%d) in %s.",
                        ExcerptingErrorCodes.EX_M_007,
                        ref.ayah_end,
                        ref.surah,
                        max_ayah,
                        excerpt.excerpt_id,
                    )

    # V-P3-8: Footnote relevance — remove orphan footnotes
    # Check if ⌜ref_marker⌝ pattern appears in primary_text.
    # If not, the footnote belongs to a different excerpt.
    if excerpt.footnotes_relevant:
        kept = []
        removed = False
        for fn in excerpt.footnotes_relevant:
            marker = f"\u231C{fn.ref_marker}\u231D"
            if marker in excerpt.primary_text:
                kept.append(fn)
            else:
                removed = True
                errors.append(ExcerptingErrorCodes.EX_M_009)
                logger.warning(
                    "%s: Orphan footnote ref_marker=%s removed from %s.",
                    ExcerptingErrorCodes.EX_M_009,
                    fn.ref_marker,
                    excerpt.excerpt_id,
                )
        if removed:
            modified = excerpt.model_copy(
                update={"footnotes_relevant": kept}
            )

    # V-P3-9: Content type consistency
    for ct in excerpt.content_types:
        if ct.value not in _VALID_SCHOLARLY_FUNCTIONS:
            errors.append(ExcerptingErrorCodes.EX_M_010)
            logger.warning(
                "%s: Unknown content type %s in %s.",
                ExcerptingErrorCodes.EX_M_010,
                ct.value,
                excerpt.excerpt_id,
            )

    return modified, errors


# ═══════════════════════════════════════════════════════════════════
# Function 2: validate_batch
# ═══════════════════════════════════════════════════════════════════


def validate_batch(
    excerpts: list[ExcerptRecord],
) -> tuple[list[ExcerptRecord], list[str]]:
    """Run all V-P3 checks on a batch of excerpts (§7.4).

    Includes V-P3-1 (ID uniqueness) at batch level.
    Returns (validated excerpts, all error codes).
    """
    all_errors: list[str] = []
    validated: list[ExcerptRecord] = []

    # V-P3-1: Excerpt ID uniqueness
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for exc in excerpts:
        if exc.excerpt_id in seen_ids:
            duplicate_ids.add(exc.excerpt_id)
        seen_ids.add(exc.excerpt_id)

    if duplicate_ids:
        error_code = ExcerptingErrorCodes.EX_V_002
        all_errors.append(error_code)
        logger.error(
            "V-P3-1: Duplicate excerpt IDs found: %s",
            duplicate_ids,
        )

    # Per-excerpt checks (V-P3-2 through V-P3-9, except V-P3-7)
    for exc in excerpts:
        modified_exc, exc_errors = validate_excerpt(exc)
        validated.append(modified_exc)
        all_errors.extend(exc_errors)

    return validated, all_errors
