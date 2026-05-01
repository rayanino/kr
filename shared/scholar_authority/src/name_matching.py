"""Scholar name matching — conservative production baseline.

The source engine needs a comparison helper for Arabic scholarly names, but it
must avoid destructive normalization that could silently merge distinct
scholars. This module therefore keeps a narrow comparison policy:

- strip parenthetical metadata and tashkeel
- remove tatweel and punctuation
- preserve taa marbuta and the definite article
- normalize only alef/hamza forms at the codepoint level
- treat honorifics and patronymic connectors explicitly instead of with regex

INV-SRC-0014 (Phase 5 Session 2) extends this module with
:func:`strip_invisible_unicode` so that the Phase 5 match-key construction
can apply the strict 3-stage ordering (invisible-Unicode strip → honorific
normalization → match-key construction). The function is an additive
helper — existing callers of :func:`normalize_arabic_name` and
:func:`normalized_name_similarity` keep their current semantics.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass


logger = logging.getLogger(__name__)


_PARENTHETICAL_RE = re.compile(r"\([^)]*\)")
_TASHKEEL_RE = re.compile(
    "[\u0610-\u061A\u064B-\u065F\u0670]"
)
_PUNCTUATION_RE = re.compile(r"[،؛,;:.!؟?\u00BB\u00AB\-\u2013\u2014/]")
_WHITESPACE_RE = re.compile(r"\s+")

_ALEF_HAMZA_TRANSLATION = str.maketrans({
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
})

_SINGLE_HONORIFICS = {
    "الشيخ",
    "شيخ",
    "الامام",
    "امام",
    "الإمام",
    "العلامة",
    "علامة",
    "الحافظ",
    "حافظ",
    "القاضي",
    "قاضي",
    "المحقق",
    "محقق",
    "المحدث",
    "محدث",
    "الفقيه",
    "فقيه",
    "المفسر",
    "مفسر",
    "المقرئ",
    "مقرئ",
    "الاصولي",
    "الأصولي",
    "اصولي",
    "الأستاذ",
    "الاستاذ",
    "استاذ",
    "الدكتور",
    "دكتور",
}
_MULTI_HONORIFICS = {
    ("شيخ", "الاسلام"),
    ("شيخ", "الإسلام"),
    ("حجة", "الاسلام"),
    ("حجة", "الإسلام"),
    ("امام", "الحرمين"),
    ("إمام", "الحرمين"),
    ("شيخ", "المفسرين"),
    ("شيخ", "المحدثين"),
    ("خاتم", "الحفاظ"),
}
_KUNYA_PREFIXES = {"ابو", "أبو", "ام", "أم"}
_KNOWN_KUNYA_ONLY = {
    "ابو هريرة",
    "أبو هريرة",
    "ابو بكر الصديق",
    "أبو بكر الصديق",
    "ابو حنيفة",
    "أبو حنيفة",
    "ام سلمة",
    "أم سلمة",
}
_CONNECTOR_TOKENS = {"بن", "بنت", "ابن"}


def normalize_arabic_name(name: str) -> str:
    """Return a conservative comparison string for Arabic scholar names."""
    result = _PARENTHETICAL_RE.sub("", name)
    result = _TASHKEEL_RE.sub("", result)
    result = result.replace("\u0640", "")
    result = result.translate(_ALEF_HAMZA_TRANSLATION)
    result = _PUNCTUATION_RE.sub(" ", result)
    result = _WHITESPACE_RE.sub(" ", result).strip(" \t\n\r")
    return result


def _strip_leading_honorifics(tokens: list[str]) -> list[str]:
    """Remove leading honorific tokens only; preserve the remaining name."""
    remaining = list(tokens)
    while remaining:
        if len(remaining) >= 2 and tuple(remaining[:2]) in _MULTI_HONORIFICS:
            remaining = remaining[2:]
            continue
        if remaining[0] in _SINGLE_HONORIFICS:
            remaining = remaining[1:]
            continue
        break
    return remaining


def _normalize_kunya_case(tokens: list[str]) -> list[str]:
    """Strip leading kunya only when enough identifying material remains."""
    if len(tokens) >= 3 and tokens[0] in _KUNYA_PREFIXES:
        normalized_full = " ".join(tokens)
        if normalized_full not in _KNOWN_KUNYA_ONLY:
            return tokens[2:]
    return tokens


def _extract_name_tokens(name: str) -> set[str]:
    """Extract identifying tokens from a scholarly Arabic name."""
    normalized = normalize_arabic_name(name)
    if not normalized:
        return set()

    tokens = normalized.split()
    tokens = _strip_leading_honorifics(tokens)
    tokens = _normalize_kunya_case(tokens)

    extracted: list[str] = []
    for token in tokens:
        if token in _CONNECTOR_TOKENS:
            continue
        extracted.append(token)
    return set(extracted)


def normalized_name_similarity(a: str, b: str) -> float:
    """Compare two Arabic scholarly names conservatively."""
    norm_a = normalize_arabic_name(a)
    norm_b = normalize_arabic_name(b)

    if not norm_a or not norm_b:
        return 0.0

    tokens_a = _extract_name_tokens(a)
    tokens_b = _extract_name_tokens(b)

    if not tokens_a or not tokens_b:
        return 0.0

    if tokens_a == tokens_b:
        return 1.0

    shorter = tokens_a if len(tokens_a) <= len(tokens_b) else tokens_b
    longer = tokens_b if len(tokens_a) <= len(tokens_b) else tokens_a

    if shorter.issubset(longer):
        return 0.85 if len(shorter) == 1 else 0.95

    shared = tokens_a & tokens_b
    if shared:
        min_size = min(len(tokens_a), len(tokens_b))
        return len(shared) / min_size

    # Substring fallback for compact-vs-split spellings such as عبدالله.
    for ta in tokens_a:
        for tb in tokens_b:
            if len(ta) >= 3 and len(tb) >= 3 and (ta in tb or tb in ta):
                return 0.4

    return 0.0


# ---------------------------------------------------------------------------
# INV-SRC-0014 Stage 1 — invisible-Unicode strip
# ---------------------------------------------------------------------------
#
# Per .claude/rules/input-sanitization.md, dangerous invisible characters at
# the ingestion boundary are: U+200B zero-width space, U+200C zero-width
# non-joiner (Persian/Urdu carve-out), U+200D zero-width joiner (Persian/Urdu/
# Kurdish carve-out), U+200E LTR mark, U+200F RTL mark, U+202A-202E bidi
# overrides (LRE/RLE/PDF/LRO/RLO), U+FEFF BOM, U+2060 word joiner, U+00AD
# soft hyphen.
#
# INV-SRC-0014 calls out U+200E, U+200F, U+202A-202E for the bidi-strip path.
# The strict-strip default (Arabic scholarly text) ALSO removes U+200C and
# U+200D because Arabic doesn't need them for shaping (lam-alef ligatures are
# automatic from base characters); they are formatting noise from HTML exports
# or OCR. Persian/Urdu/Kurdish texts (preserve_persian_urdu_zwj=True) keep
# U+200C and U+200D because compound-letter shaping there is meaning-bearing.
#
# Per Critical Rule 4 (errors fail loudly): every occurrence is logged with
# byte offset for the audit trail (T-1 corruption vector — invisible-character
# contamination masking surface that should match).

# Bidi direction-reset marks. Per INV-SRC-0014 AC-2 these MUST act as
# token-separators on strip — replacing with a single space (rather than
# bare removal) preserves the surrounding token boundary and prevents
# accidental gluing (e.g., "الإمام‎البخاري" must yield "الإمام البخاري"
# post-Stage-1 so Stage-2 honorific strip can isolate "البخاري").
_BIDI_DIRECTION_MARKS: frozenset[str] = frozenset(
    {
        chr(0x200E),  # LTR mark
        chr(0x200F),  # RTL mark
        chr(0x202A),  # LRE
        chr(0x202B),  # RLE
        chr(0x202C),  # PDF
        chr(0x202D),  # LRO
        chr(0x202E),  # RLO
    }
)

# Within-token zero-width / formatting noise. Stripped without replacement
# because they live INSIDE tokens (BOM at file start, word joiner between
# letters, soft hyphen as line-break hint, zero-width space inserted by
# OCR / HTML export tooling).
_WITHIN_TOKEN_INVISIBLES: frozenset[str] = frozenset(
    {
        chr(0x200B),  # zero-width space
        chr(0xFEFF),  # BOM / zero-width no-break space
        chr(0x2060),  # word joiner
        chr(0x00AD),  # soft hyphen
    }
)

# Aggregate of both classes — used as the membership probe in the
# strict-strip default.
_BIDI_STRICT_INVISIBLE_CODEPOINTS: frozenset[str] = (
    _BIDI_DIRECTION_MARKS | _WITHIN_TOKEN_INVISIBLES
)

# Optional carve-out characters: stripped along with the strict set unless the
# caller explicitly opts in (Persian/Urdu/Kurdish source markers). Arabic
# scholarly text (KR's dominant corpus) does not need ZWJ for shaping; lam-alef
# ligatures are produced from base characters automatically by the rendering
# engine.
_OPTIONAL_INVISIBLE_CODEPOINTS: frozenset[str] = frozenset(
    {
        "‌",  # zero-width non-joiner
        "‍",  # zero-width joiner
    }
)


@dataclass(frozen=True)
class InvisibleStripOccurrence:
    """One stripped invisible-Unicode occurrence (audit trail per T-1)."""

    codepoint: str
    byte_offset: int
    char_index: int


def strip_invisible_unicode(
    text: str,
    *,
    preserve_persian_urdu_zwj: bool = False,
) -> tuple[str, list[InvisibleStripOccurrence]]:
    """Stage 1 of INV-SRC-0014 — strip dangerous invisible Unicode characters.

    Returns the cleaned text plus a per-occurrence audit log capturing the
    codepoint, the BYTE offset (UTF-8) into the original text, and the
    CHARACTER index. Per Critical Rule 4 every removal is loggable for
    correlation with the upstream source bytes.

    By default U+200C and U+200D are stripped along with the bidi marks. Set
    ``preserve_persian_urdu_zwj=True`` only when the caller has detected
    Persian / Urdu / Kurdish source markers (one of پ U+067E, چ U+0686,
    گ U+06AF, ژ U+0698 in the surrounding context AND the compound-letter
    shaping is documented).
    """
    target_codepoints: frozenset[str] = (
        _BIDI_STRICT_INVISIBLE_CODEPOINTS
        if preserve_persian_urdu_zwj
        else _BIDI_STRICT_INVISIBLE_CODEPOINTS | _OPTIONAL_INVISIBLE_CODEPOINTS
    )
    if not any(ch in target_codepoints for ch in text):
        return text, []

    occurrences: list[InvisibleStripOccurrence] = []
    cleaned_chars: list[str] = []
    byte_offset = 0
    for char_index, ch in enumerate(text):
        ch_byte_len = len(ch.encode("utf-8"))
        if ch in target_codepoints:
            occurrences.append(
                InvisibleStripOccurrence(
                    codepoint=f"U+{ord(ch):04X}",
                    byte_offset=byte_offset,
                    char_index=char_index,
                )
            )
            logger.debug(
                "INV-SRC-0014 invisible-Unicode strip: %s at byte_offset=%d "
                "char_index=%d (T-1 audit)",
                f"U+{ord(ch):04X}",
                byte_offset,
                char_index,
            )
            # Bidi direction-reset marks act as token separators — replace
            # with single ASCII space so downstream tokenization preserves
            # the surrounding boundary (INV-SRC-0014 AC-2). Within-token
            # invisibles (BOM / ZWSP / WJ / soft hyphen) are removed
            # without replacement.
            if ch in _BIDI_DIRECTION_MARKS:
                cleaned_chars.append(" ")
        else:
            cleaned_chars.append(ch)
        byte_offset += ch_byte_len

    return "".join(cleaned_chars), occurrences
