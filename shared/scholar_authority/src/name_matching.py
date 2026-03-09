"""Scholar name matching — production location.

Arabic scholarly name normalization and comparison. Handles patronymic
particles (بن, ابن), short-vs-long form matching (النووي vs full nasab chain),
and token-based overlap scoring.

Copied from tests/eval_harness.py (validated in Step 2) to production location.
"""

from __future__ import annotations

import re


def normalize_arabic_name(name: str) -> str:
    """Normalize Arabic name for comparison."""
    result = name
    # Strip parenthetical annotations — ground truth includes death dates
    # like "(ت 337هـ)" or "(631-676 هـ)" that are metadata, not name parts.
    result = re.sub(r'\([^)]*\)', '', result)
    # Strip common diacritics (tashkeel)
    diacritics = '\u0610\u0611\u0612\u0613\u0614\u0615\u0616\u0617\u0618\u0619\u061A\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0657\u0658\u0659\u065A\u065B\u065C\u065D\u065E\u065F\u0670'
    for d in diacritics:
        result = result.replace(d, '')
    # Normalize hamza forms
    result = result.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    # Normalize taa marbuta
    result = result.replace('ة', 'ه')
    # Strip definite article
    result = re.sub(r'\bال[ـ]?', '', result)
    # Collapse whitespace
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def _extract_name_tokens(name: str) -> set[str]:
    """Extract significant tokens from a normalized Arabic scholarly name.

    Removes patronymic particles (بن, ابن) which are structural connectors,
    not identifying components. Keeps kunya, laqab, ism, nasab names, and nisba.
    """
    normalized = normalize_arabic_name(name)
    particles = {'بن', 'ابن'}
    return {t for t in normalized.split() if t not in particles}


def normalized_name_similarity(a: str, b: str) -> float:
    """Compare two Arabic scholarly names by semantic component overlap.

    Handles the common case where the same scholar is referred to by
    different subsets of name components (e.g., nisba-only vs full nasab chain).
    Uses token overlap relative to the shorter name to reward elaboration matches.
    Falls back to substring containment for compound-word mismatches.
    """
    norm_a = normalize_arabic_name(a)
    norm_b = normalize_arabic_name(b)

    if norm_a == norm_b:
        return 1.0
    if not norm_a or not norm_b:
        return 0.0

    tokens_a = _extract_name_tokens(a)
    tokens_b = _extract_name_tokens(b)

    if not tokens_a or not tokens_b:
        return 0.0

    shared = tokens_a & tokens_b

    if not shared:
        # Substring fallback for compound-word mismatches (عبدالله vs عبد الله)
        for ta in tokens_a:
            for tb in tokens_b:
                if len(ta) >= 3 and len(tb) >= 3 and (ta in tb or tb in ta):
                    return 0.4
        return 0.0

    min_size = min(len(tokens_a), len(tokens_b))
    overlap = len(shared) / min_size

    # If all of shorter name's tokens found in longer → strict elaboration
    shorter = tokens_a if len(tokens_a) <= len(tokens_b) else tokens_b
    longer = tokens_b if len(tokens_a) <= len(tokens_b) else tokens_a
    if shorter.issubset(longer) and min_size >= 2:
        return max(0.85, overlap)

    return overlap
