"""Phase 5 Session 2 — Scholar fragment normalization (REQ-SRC-0050).

Implements the 5-component name parser (ism / kunyah / nasab_chain / laqab /
nisba_list) feeding the Stage-1 deterministic narrowing of REQ-SRC-0051. The
strict 3-stage ordering of INV-SRC-0014 is enforced inside ``parse_fragment``:

    Stage 1 — invisible-Unicode strip (delegated to ``name_matching``)
    Stage 2 — honorific normalization (existing 28-single + 8-multi list)
    Stage 3 — match-key construction (alef-variant unification, matching only)

Compound-name preservation per ``.claude/rules/arabic-scholarly-conventions.md``
"عبد + divine attribute" is a single semantic unit and MUST NOT be split at
whitespace. F-5 closure surface per Phase 5 synthesis §1.4.

Byte-faithfulness per Critical Rule 2: ``display_fragment`` is byte-identical
to the caller's input. ``parsed_components`` preserves hamza forms (أ vs ا
vs إ vs آ) — alef-variant unification is applied ONLY to ``match_key`` for
candidate-generation lookup. Connector tokens (بن, بنت, ابن) are preserved
in ``nasab_chain`` exactly as supplied by the caller.
"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from engines.source.contracts import ErrorCode
from shared.scholar_authority.src.match_contracts import NormalizedFragment
from shared.scholar_authority.src.name_matching import (
    InvisibleStripOccurrence,
    _CONNECTOR_TOKENS,
    _KUNYA_PREFIXES,
    _MULTI_HONORIFICS,
    _SINGLE_HONORIFICS,
    strip_invisible_unicode,
)


# Arabic block detection per .claude/rules/regex-arabic-digits.md.
# Matches Arabic, Arabic Supplement, Arabic Presentation Forms-A, Arabic
# Presentation Forms-B (covers Persian/Urdu/Kurdish base letters too).
_ARABIC_RANGE_RE = re.compile(
    "[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]"
)

# Latin letter detection — used for AC-5 explicit transliteration rejection.
_LATIN_LETTER_RE = re.compile(r"[A-Za-z]")

# Mirror name_matching's tashkeel/punctuation regexes — Phase 5 parsing has
# different post-processing semantics from name_matching.normalize_arabic_name
# (which collapses alef-hamza and is destructive of hamza information). The
# fragment parser preserves hamza forms; only the match_key applies alef-
# variant unification.
_TASHKEEL_RE = re.compile(
    "["
    + chr(0x0610) + "-" + chr(0x061A)  # Arabic signs
    + chr(0x064B) + "-" + chr(0x065F)  # tashkeel marks
    + chr(0x0670)                       # superscript alef
    + "]"
)
_TATWEEL = "ـ"
_PARENTHETICAL_RE = re.compile(r"\([^)]*\)")
_PUNCTUATION_RE = re.compile(
    r"[،؛,;:.!؟?»«\-–—/]"
)
_WHITESPACE_RE = re.compile(r"\s+")

# Alef-variant unification — applied to match_key ONLY. REQ-SRC-0051
# postconditions explicitly authorize this for the matching key while
# FORBIDDING it on stored display strings.
_MATCH_KEY_ALEF_TRANSLATION = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
    }
)

# Compound name lexicon per .claude/rules/arabic-scholarly-conventions.md.
# The general rule is: token "عبد" + token starting with "ال" → glue as a
# single token (the divine-attribute compound). REQ-SRC-0050 lines 86-90
# enumerate ten explicit examples plus "etc."; the conservative
# implementation applies the structural rule and treats the explicit
# enumeration as a sanity-check anchor, not an exhaustive lexicon.
_ABD_PREFIX_TOKEN = "عبد"


class FragmentNotArabicError(ValueError):
    """SRC-E-FRAGMENT-NOT-ARABIC — caller supplied non-Arabic text.

    Raised when ``parse_fragment`` is called with empty, whitespace-only,
    Latin-transliteration, or non-Arabic-character-only input. Per
    REQ-SRC-0050 preconditions a fragment must be in Arabic; the match call
    cannot proceed without a well-formed Arabic name.
    """

    error_code: ErrorCode = ErrorCode.FRAGMENT_NOT_ARABIC


class HonorificOnlyNameError(ValueError):
    """SRC-E-HONORIFIC-ONLY-NAME — fragment is honorific-shell after strip.

    Reuses the existing error code at ``engines/source/contracts.py:579`` per
    ChatGPT DR finding (do not duplicate). F-6 closure surface per Phase 5
    synthesis §1.4.
    """

    error_code: ErrorCode = ErrorCode.HONORIFIC_ONLY_NAME


class CompoundNameSplitError(ValueError):
    """SRC-E-COMPOUND-NAME-SPLIT — bare 'عبد' without divine attribute.

    Defensive guard: if the parser tokenization yields a "عبد" token that is
    not followed by a token starting with "ال", the orchestrator may have
    received a corrupted source (truncation upstream). Attribution to the
    wrong scholar is a critical risk if the compound has been split, so
    fail loud per Critical Rule 4. F-5 closure surface.
    """

    error_code: ErrorCode = ErrorCode.COMPOUND_NAME_SPLIT


class FragmentParseResult(BaseModel):
    """Output of ``parse_fragment`` — feeds CON-SRC-0009 ScholarEvidencePacket.

    Carries the four ``ScholarEvidencePacket`` text fields plus the audit log
    of stripped invisible-Unicode occurrences (T-1 audit trail). The caller
    (Stage-1 narrowing in REQ-SRC-0051) reads this result and the dossier
    context, then assembles the ``ScholarEvidencePacket`` with candidates.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    normalized_fragment: str = Field(min_length=1)
    display_fragment: str = Field(min_length=1)
    match_key: str = Field(min_length=1)
    parsed_components: NormalizedFragment
    invisible_strip_log: list[InvisibleStripOccurrence] = Field(
        default_factory=list
    )


def parse_fragment(raw_fragment: str) -> FragmentParseResult:
    """REQ-SRC-0050 — parse a scholar fragment into the 5-component shape.

    Applies INV-SRC-0014 strict 3-stage ordering: bidi-strip → honorific
    normalization → match-key construction. Decomposes the post-honorific-
    strip tokens into the 5 classical name components per
    arabic-scholarly-conventions.md.

    Raises ``FragmentNotArabicError`` (Latin / empty / non-Arabic),
    ``HonorificOnlyNameError`` (only honorifics remain after strip), or
    ``CompoundNameSplitError`` (bare 'عبد' without divine attribute).
    """
    if not raw_fragment or not raw_fragment.strip():
        raise FragmentNotArabicError(
            "Fragment is empty or whitespace-only. REQ-SRC-0050 "
            "preconditions require non-empty Arabic text "
            "(SRC-E-FRAGMENT-NOT-ARABIC)."
        )

    # Display fragment — byte-identical input per Critical Rule 2 + AC-1.
    display_fragment = raw_fragment

    # Stage 1 — invisible-Unicode strip per INV-SRC-0014. The strict-strip
    # default removes bidi marks, ZWJ, ZWNJ, and other formatting noise; the
    # Persian/Urdu/Kurdish carve-out is applied at the work-title channel
    # in Stage-1 narrowing (REQ-SRC-0051) where source language is known,
    # not at fragment parsing where context is absent.
    cleaned, strip_log = strip_invisible_unicode(raw_fragment)

    # Validate Arabic content — the fragment must contain at least one
    # character in the Arabic Unicode blocks. AC-5 of REQ-SRC-0050
    # explicitly rejects Latin transliteration ("Sibawayh") with
    # SRC-E-FRAGMENT-NOT-ARABIC.
    if not _ARABIC_RANGE_RE.search(cleaned):
        raise FragmentNotArabicError(
            f"Fragment {raw_fragment!r} contains no Arabic characters in "
            "[U+0600-U+06FF, U+0750-U+077F, U+FB50-U+FDFF, U+FE70-U+FEFF]. "
            "REQ-SRC-0050 preconditions require Arabic; Latin transliteration "
            "is rejected at this boundary (SRC-E-FRAGMENT-NOT-ARABIC)."
        )

    # AC-5 also rejects mixed Arabic + Latin where the Latin signal dominates.
    # Conservative rule: if ANY Latin letter appears, reject — caller should
    # have transliterated to Arabic before reaching the match boundary.
    if _LATIN_LETTER_RE.search(cleaned):
        raise FragmentNotArabicError(
            f"Fragment {raw_fragment!r} contains Latin letters. The match-call "
            "boundary requires pure Arabic input; transliterate or normalize "
            "upstream (SRC-E-FRAGMENT-NOT-ARABIC)."
        )

    # Conservative pre-tokenization normalization (preserves hamza forms):
    #   - strip parentheticals (parenthetical metadata)
    #   - strip tashkeel (diacritics)
    #   - strip tatweel (kashida U+0640)
    #   - punctuation → whitespace
    #   - collapse whitespace
    # NB: alef-variant unification is applied LATER on the match_key only.
    normalized_fragment = _PARENTHETICAL_RE.sub("", cleaned)
    normalized_fragment = _TASHKEEL_RE.sub("", normalized_fragment)
    normalized_fragment = normalized_fragment.replace(_TATWEEL, "")
    normalized_fragment = _PUNCTUATION_RE.sub(" ", normalized_fragment)
    normalized_fragment = _WHITESPACE_RE.sub(" ", normalized_fragment).strip()

    if not normalized_fragment:
        raise FragmentNotArabicError(
            f"Fragment {raw_fragment!r} normalized to empty string after "
            "tashkeel + punctuation strip (only non-Arabic content). "
            "REQ-SRC-0050 preconditions require an Arabic name token "
            "(SRC-E-FRAGMENT-NOT-ARABIC)."
        )

    # Tokenize and apply compound-name gluing BEFORE honorific strip.
    raw_tokens = normalized_fragment.split()
    raw_tokens = _glue_compound_abd_names(raw_tokens, raw_fragment=raw_fragment)

    # Stage 2 — honorific strip (uses existing _SINGLE_HONORIFICS +
    # _MULTI_HONORIFICS lexicons from name_matching.py, both of which carry
    # hamza-preserved AND alef-normalized variants so this matches the
    # hamza-preserved tokens here).
    post_honorific_tokens = _strip_leading_honorifics_preserving_hamza(raw_tokens)

    if not post_honorific_tokens:
        raise HonorificOnlyNameError(
            f"Fragment {raw_fragment!r} contains only honorifics; no name "
            "token remains after Stage-2 strip (REQ-SRC-0050 AC-4 + "
            "INV-SRC-0014 AC-3, F-6 closure surface; "
            "SRC-E-HONORIFIC-ONLY-NAME)."
        )

    # 5-component decomposition (preserves hamza forms in components).
    components = _decompose_into_5_components(post_honorific_tokens)

    # Stage 3 — match_key construction (alef-variant unified for matching only).
    match_key = _construct_match_key(post_honorific_tokens)

    if not match_key:
        # Defense in depth: if post_honorific_tokens is non-empty, this
        # cannot trigger. The asymmetric-validator pattern review (Session 1
        # learning §5) flagged this exact class of state-machine gap, so
        # the guard is cheap and useful.
        raise HonorificOnlyNameError(
            f"Fragment {raw_fragment!r} produced empty match_key after "
            "Stage-3 construction (defensive guard; "
            "SRC-E-HONORIFIC-ONLY-NAME)."
        )

    return FragmentParseResult(
        normalized_fragment=normalized_fragment,
        display_fragment=display_fragment,
        match_key=match_key,
        parsed_components=components,
        invisible_strip_log=strip_log,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _glue_compound_abd_names(
    tokens: list[str],
    *,
    raw_fragment: str,
) -> list[str]:
    """Glue 'عبد + ال[X]' into a single compound token (F-5 closure).

    Per arabic-scholarly-conventions.md: عبد + divine attribute is a single
    semantic unit. NEVER split at whitespace. The conservative rule is
    "عبد + token-starting-with-ال" — a structural pattern that catches all
    enumerated divine-attribute compounds in REQ-SRC-0050 lines 86-90 and
    extends to less-common compounds without false positives in scholar
    name corpora.

    Raises ``CompoundNameSplitError`` if a bare 'عبد' appears WITHOUT a
    following ال-prefix token: that's a structural anomaly (truncation
    upstream) and attribution to the wrong scholar is a critical risk.
    """
    glued: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        next_token: Optional[str] = tokens[i + 1] if i + 1 < len(tokens) else None
        if token == _ABD_PREFIX_TOKEN:
            if (
                next_token is None
                or not next_token.startswith("ال")
                or len(next_token) < 3
            ):
                raise CompoundNameSplitError(
                    f"Fragment {raw_fragment!r} contains bare 'عبد' without "
                    "a following ال-prefix divine-attribute token. عبد + "
                    "divine attribute is a compound semantic unit per "
                    "arabic-scholarly-conventions.md; the orchestrator may "
                    "have received truncated input. F-5 closure surface "
                    "(SRC-E-COMPOUND-NAME-SPLIT)."
                )
            glued.append(f"{token} {next_token}")
            i += 2
        else:
            glued.append(token)
            i += 1
    return glued


def _strip_leading_honorifics_preserving_hamza(tokens: list[str]) -> list[str]:
    """Stage 2 honorific strip — extends ``name_matching._strip_leading_honorifics``.

    Reuses the existing 28-single + 8-multi lexicons exported as
    ``_SINGLE_HONORIFICS`` and ``_MULTI_HONORIFICS``. Both lexicons already
    carry hamza-preserved (الإمام) AND alef-normalized (الامام) variants so
    matching works on hamza-preserved tokens here.
    """
    remaining = list(tokens)
    while remaining:
        # Multi-token honorifics first (longer match wins).
        if (
            len(remaining) >= 2
            and (remaining[0], remaining[1]) in _MULTI_HONORIFICS
        ):
            remaining = remaining[2:]
            continue
        if remaining[0] in _SINGLE_HONORIFICS:
            remaining = remaining[1:]
            continue
        break
    return remaining


def _decompose_into_5_components(tokens: list[str]) -> NormalizedFragment:
    """Decompose post-honorific tokens into the 5 classical name components.

    Heuristic decomposition per arabic-scholarly-conventions.md:
      - kunyah: tokens[0] in _KUNYA_PREFIXES → kunyah = tokens[0..1]
      - ism: first non-kunyah, non-connector, non-nisba token
      - nasab_chain: consecutive (بن / ابن / بنت) + name pairs
      - nisba_list: tokens matching the ال + ≥2 chars + ي/ية/ى pattern
      - laqab: residue tokens that are neither nisba-shaped nor connectors
    """
    if not tokens:
        return NormalizedFragment()

    cursor = 0
    n = len(tokens)

    # Step 1 — kunyah: [أبو/ابو/أم/ام] + ism-of-the-firstborn (2 tokens).
    kunyah: Optional[str] = None
    if cursor < n and tokens[cursor] in _KUNYA_PREFIXES and cursor + 1 < n:
        kunyah = f"{tokens[cursor]} {tokens[cursor + 1]}"
        cursor += 2

    # Step 2 — ism: first non-connector, non-nisba token after kunyah.
    ism: Optional[str] = None
    if cursor < n:
        token = tokens[cursor]
        if (
            not _looks_like_nisba(token)
            and token not in _CONNECTOR_TOKENS
            and not token.startswith("ابن")
        ):
            ism = token
            cursor += 1

    # Step 3 — nasab_chain: consecutive (connector + name) pairs.
    nasab_chain: list[str] = []
    while cursor < n:
        token = tokens[cursor]
        if token in _CONNECTOR_TOKENS and cursor + 1 < n:
            nasab_chain.append(f"{token} {tokens[cursor + 1]}")
            cursor += 2
            continue
        if token.startswith("ابن") and len(token) > 3:
            # Compact form ابنSomething (rare; usually whitespace-separated).
            nasab_chain.append(token)
            cursor += 1
            continue
        break

    # Step 4 — laqab + nisba_list from the residue.
    laqab: list[str] = []
    nisba_list: list[str] = []
    while cursor < n:
        token = tokens[cursor]
        if _looks_like_nisba(token):
            nisba_list.append(token)
        else:
            laqab.append(token)
        cursor += 1

    return NormalizedFragment(
        ism=ism,
        kunyah=kunyah,
        nasab_chain=nasab_chain,
        laqab=laqab,
        nisba_list=nisba_list,
    )


def _looks_like_nisba(token: str) -> bool:
    """Heuristic: a nisba is "ال" + stem + "ي" / "ية" / "ى" suffix.

    Conservative — covers the common cases (البخاري, الكوفي, النووي, الحنفي,
    الشافعي, البصرة-derivative variants) without false-positiving on ال +
    ism (النعمان ends in ن; my الحرمين ends in ن — neither match).
    """
    if not token.startswith("ال"):
        return False
    if len(token) < 4:
        return False
    return (
        token.endswith("ي")
        or token.endswith("ية")
        or token.endswith("ى")
    )


def _construct_match_key(tokens: list[str]) -> str:
    """Stage 3 — alef-variant unified, tatweel-stripped match key.

    Joins post-honorific tokens with single-space separator. Alef-hamza
    forms (أ / إ / آ / ٱ) are unified to ا for matching key only —
    REQ-SRC-0051 postconditions explicitly authorize this for the matching
    key while FORBIDDING it on stored display strings.
    """
    parts: list[str] = []
    for token in tokens:
        normalized = token.translate(_MATCH_KEY_ALEF_TRANSLATION)
        normalized = normalized.replace(_TATWEEL, "")
        parts.append(normalized)
    return " ".join(parts)


__all__ = [
    "FragmentNotArabicError",
    "HonorificOnlyNameError",
    "CompoundNameSplitError",
    "FragmentParseResult",
    "parse_fragment",
]
