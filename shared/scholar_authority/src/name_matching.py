"""Scholar name matching — conservative production baseline.

The source engine needs a comparison helper for Arabic scholarly names, but it
must avoid destructive normalization that could silently merge distinct
scholars. This module therefore keeps a narrow comparison policy:

- strip parenthetical metadata and tashkeel
- remove tatweel and punctuation
- preserve taa marbuta and the definite article
- normalize only alef/hamza forms at the codepoint level
- treat honorifics and patronymic connectors explicitly instead of with regex
"""

from __future__ import annotations

import re


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
