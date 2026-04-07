"""Phase 3: Output Validation (SPEC §7.4).

Runs V-P3-1 through V-P3-9 on ExcerptRecords before writing output.
Validation detects problems and emits error codes — it does NOT auto-correct,
with the sole exception of V-P3-8 (orphan footnote removal).
"""

from __future__ import annotations

import logging
import re
from typing import Optional

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
# V-P3-10: Pronoun-suffix SC check (Session 17 campaign finding)
# ═══════════════════════════════════════════════════════════════════

_PRONOUN_SC_WORD_CEILING = 30

# 3rd-person pronoun suffixes that indicate unresolved anaphora.
# Multi-char suffixes only — single ه excluded because root-final ه words
# (فقه, وجه, شبه, مكره) are extremely common in fiqh texts and cause
# systematic false positives. Arabic-auditor + code-reviewer finding.
# Use explicit Unicode ranges, NOT \b (fails for Arabic clitics).
_PRONOUN_SUFFIX_RE = re.compile(
    r"[\u0600-\u06FF]"  # preceded by Arabic char (attached suffix)
    r"(?:هما|هم|هن|ها)"  # 3rd-person suffixes (no single ه)
    r"(?:\s|$|[^\u0600-\u06FF])"  # followed by space, end, or non-Arabic
)

# Named entity patterns: nominal antecedents that resolve pronoun reference.
# Only genuine person/role nouns — NOT الله (appears in ~100% of Islamic
# texts), NOT ابن/أبو (scholar citation fragments, not antecedents).
# Arabic-auditor + code-reviewer + architect finding.
_ANTECEDENT_MARKERS: list[str] = [
    "النبي",
    "الرسول",
    "رسول الله",
    "المرأة",
    "الرجل",
    "الزوج",
    "الزوجة",
    "المطلقة",
    "المطلق",
    "عمر",
    "عائشة",
]


def _check_pronoun_suffix_sc(
    excerpt: ExcerptRecord,
    errors: list[str],
) -> ExcerptRecord:
    """Flag FULL excerpts under 30 words with unresolved pronoun suffixes.

    Session 17 campaign finding: 82 excerpts rated FULL but containing
    attached 3rd-person pronoun suffixes (ها/هم/هما/هن) without a
    named entity antecedent. These are not self-contained for a reader.

    Architect review: emits review_flag (not error code) because content
    quality judgments belong in consensus, not deterministic validation.
    Phase 2 LLM had full context when it assigned FULL — this heuristic
    is advisory, not authoritative.
    """
    if excerpt.self_containment != SelfContainmentLevel.FULL:
        return excerpt

    word_count = excerpt.end_word - excerpt.start_word + 1
    if word_count >= _PRONOUN_SC_WORD_CEILING:
        return excerpt

    text = excerpt.primary_text
    if not _PRONOUN_SUFFIX_RE.search(text):
        return excerpt

    # Check if a named entity antecedent exists in the text
    for marker in _ANTECEDENT_MARKERS:
        if marker in text:
            return excerpt  # antecedent found — pronoun is likely resolved

    # Emit as review_flag, not error code — advisory signal for human review
    if "pronoun_anaphora_risk" not in excerpt.review_flags:
        flags = list(excerpt.review_flags)
        flags.append("pronoun_anaphora_risk")
        excerpt = excerpt.model_copy(update={"review_flags": flags})
        logger.info(
            "V-P3-10: FULL excerpt %s has %d words with unresolved pronoun "
            "suffix — flagged for review (pronoun_anaphora_risk).",
            excerpt.excerpt_id,
            word_count,
        )

    return excerpt


# ═══════════════════════════════════════════════════════════════════
# Function 1: validate_excerpt
# ═══════════════════════════════════════════════════════════════════


def validate_excerpt(
    excerpt: ExcerptRecord,
) -> tuple[Optional[ExcerptRecord], list[str]]:
    """Run per-excerpt V-P3 checks (§7.4).

    Returns (possibly modified excerpt or None if dropped, list of emitted error codes).
    Returns None when V-P3-2 fails — corrupt excerpts must not reach output.
    V-P3-1 and V-P3-7 are batch-level checks — not run here.
    """
    errors: list[str] = []
    modified = excerpt
    drop = False

    # V-P3-2: Primary text integrity
    # Compare text_snippet against primary_text prefix after whitespace
    # normalization. text_snippet is now deterministically derived as
    # primary_text[:80] (DR29 fix), so mismatches indicate corruption.
    # FP-19/FP-21 hardening: also catch truncation attacks where snippet
    # is a prefix of primary but significantly shorter (condition stripping).
    snippet_normalized = _normalize_whitespace(excerpt.text_snippet)
    primary_normalized = _normalize_whitespace(excerpt.primary_text[:80])
    compare_len = min(len(snippet_normalized), len(primary_normalized))
    # Length ratio check: if snippet is <50% of primary[:80], it is
    # suspiciously truncated (FP-21: condition-stripped ruling detection).
    length_ratio_ok = (
        len(primary_normalized) == 0
        or len(snippet_normalized) / len(primary_normalized) >= 0.5
    )
    # Short-text policy (DR29 #1): if the primary text itself is < 20 chars,
    # compare the full available overlap and accept exact matches. The old
    # compare_len < 20 threshold was designed to catch LLM-miscounted snippets;
    # with deterministic derivation, short compare_len means a genuinely short
    # micro-unit (e.g. "الثالثة", "المسألة الخامسة") — not corruption.
    snippet_too_short = compare_len < 20 and len(primary_normalized) >= 20
    prefix_mismatch = (
        compare_len > 0
        and snippet_normalized[:compare_len] != primary_normalized[:compare_len]
    )
    if (
        snippet_too_short
        or prefix_mismatch
        or compare_len == 0  # empty snippet and/or primary = corrupt
        or not length_ratio_ok
    ):
        drop = True
        errors.append(ExcerptingErrorCodes.EX_V_002)
        logger.error(
            "%s: Text integrity check failed for %s — DROPPED. "
            "snippet_len=%d primary80_len=%d compare_len=%d "
            "snippet=%r primary=%r",
            ExcerptingErrorCodes.EX_V_002,
            excerpt.excerpt_id,
            len(snippet_normalized),
            len(primary_normalized),
            compare_len,
            snippet_normalized[:80],
            primary_normalized[:80],
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
    # DD-S56-1: Uses marker substring search (⌜ref_marker⌝ in primary_text)
    # instead of offset range check. Correct because Phase 1 assembly embeds
    # footnote markers at their positions in primary_text.
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

    # V-P3-10: Pronoun-suffix self-containment check (Session 17 finding)
    # Short FULL excerpts with 3rd-person pronoun suffixes likely have
    # unresolved anaphora — the reader cannot tell who "ها/هم" refers to.
    # Emits review_flag, not error code (architect review finding).
    modified = _check_pronoun_suffix_sc(modified, errors)

    # V-P3-9: Content type consistency
    for ct in excerpt.content_types:
        if not isinstance(ct, ScholarlyFunction):
            errors.append(ExcerptingErrorCodes.EX_M_010)
            logger.warning(
                "%s: Non-enum content type %r in %s.",
                ExcerptingErrorCodes.EX_M_010,
                ct,
                excerpt.excerpt_id,
            )
        elif ct.value not in _VALID_SCHOLARLY_FUNCTIONS:
            errors.append(ExcerptingErrorCodes.EX_M_010)
            logger.warning(
                "%s: Unknown content type %s in %s.",
                ExcerptingErrorCodes.EX_M_010,
                ct.value,
                excerpt.excerpt_id,
            )

    if drop:
        return None, errors

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
    # DD-S56-2: Batch-level check (exceeds SPEC's per-chunk requirement —
    # catches cross-chunk duplicates too).
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for exc in excerpts:
        if exc.excerpt_id in seen_ids:
            duplicate_ids.add(exc.excerpt_id)
        seen_ids.add(exc.excerpt_id)

    if duplicate_ids:
        raise ValueError(
            f"V-P3-1: Duplicate excerpt IDs detected — "
            f"this is a bug in the ID generation algorithm: {duplicate_ids}"
        )

    # Per-excerpt checks (V-P3-2 through V-P3-9, except V-P3-7)
    dropped_count = 0
    for exc in excerpts:
        modified_exc, exc_errors = validate_excerpt(exc)
        all_errors.extend(exc_errors)
        if modified_exc is not None:
            validated.append(modified_exc)
        else:
            dropped_count += 1

    if dropped_count > 0:
        logger.error(
            "V-P3-2: Dropped %d excerpts with text integrity failure.",
            dropped_count,
        )

    return validated, all_errors
