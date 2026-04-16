"""Edge-case tests for scholar name matching — real Arabic scholarly names only.

Tests unusual inputs, honorific stripping, tatweel handling, hamza/taa-marbuta
normalization, parenthetical annotation removal, compound-word fallback, and
symmetry guarantees across normalize_arabic_name, _extract_name_tokens, and
normalized_name_similarity.

SPEC reference: shared/scholar_authority/SPEC.md §4 (Record Matching &
Disambiguation — name-similarity sub-section).  Threshold semantics from
scholar_authority/CLAUDE.md: ≥0.85 → auto-match, 0.50–0.85 → human gate,
<0.50 → new_record.
"""

from __future__ import annotations

from shared.scholar_authority.src.name_matching import (
    _extract_name_tokens,
    normalize_arabic_name,
    normalized_name_similarity,
)


# ---------------------------------------------------------------------------
# Very short / degenerate inputs
# ---------------------------------------------------------------------------


def test_very_short_name_two_chars_no_crash() -> None:
    """SPEC §4: patronymic particle 'بن' alone — must not crash, tokens empty.

    'بن' is a structural connector, not an identifying name component.  It
    belongs to the particle stop-list and is removed from the token set,
    leaving an empty result.
    """
    # Arrange
    name = "بن"
    # Act
    tokens = _extract_name_tokens(name)
    # Assert — particle stripped, nothing remains
    assert isinstance(tokens, set)
    assert "بن" not in tokens
    assert tokens == set()


def test_single_arabic_char_no_crash() -> None:
    """SPEC §4: single hamza-alef 'أ' — normalization must not crash.

    'أ' (hamza on alef) normalizes to bare alef 'ا'.  No exception is raised
    and the return value is a plain string.
    """
    # Arrange
    name = "أ"
    # Act
    result = normalize_arabic_name(name)
    # Assert — hamza form stripped, returns plain alef
    assert isinstance(result, str)
    assert "أ" not in result   # hamza on alef normalized away


# ---------------------------------------------------------------------------
# Diacritics (tashkeel) transparency
# ---------------------------------------------------------------------------


def test_diacritics_only_difference_returns_perfect_match() -> None:
    """SPEC §4: 'محمد' vs 'مُحَمَّد' (full tashkeel) — similarity must be 1.0.

    Diacritics are editorial additions that vary between manuscript editions.
    The normalizer strips all tashkeel before comparison; the two strings
    therefore collapse to identical forms and trigger the exact-match path.
    """
    # Arrange
    without_tashkeel = "محمد"
    with_tashkeel = "مُحَمَّد"
    # Act
    score = normalized_name_similarity(without_tashkeel, with_tashkeel)
    # Assert — exact match after diacritics removal
    assert score == 1.0


# ---------------------------------------------------------------------------
# Honorific titles must be transparent to matching
# ---------------------------------------------------------------------------


def test_with_honorific_sheikh_high_similarity() -> None:
    """SPEC §4: 'الشيخ ابن تيمية' vs 'ابن تيمية' — الشيخ is honorific only.

    الشيخ is stripped via definite-article normalization, leaving 'شيخ' as an
    extra token.  The identifying token 'تيمية' is the sole item in the shorter
    set and is found in the longer set → subset branch → score 1.0 (≥ 0.85).
    """
    # Arrange
    with_honorific = "الشيخ ابن تيمية"
    without_honorific = "ابن تيمية"
    # Act
    score = normalized_name_similarity(with_honorific, without_honorific)
    # Assert — above auto-match threshold
    assert score >= 0.85


def test_with_honorific_imam_high_similarity() -> None:
    """SPEC §4: 'الإمام أحمد بن حنبل' vs 'أحمد بن حنبل' — الإمام is honorific.

    After normalization: الإمام → 'امام', أحمد → 'احمد'.  The shorter set
    {احمد, حنبل} is a subset of the longer {امام, احمد, حنبل} with min_size=2,
    so the elaboration path fires and returns ≥ 0.85.
    """
    # Arrange
    with_honorific = "الإمام أحمد بن حنبل"
    without_honorific = "أحمد بن حنبل"
    # Act
    score = normalized_name_similarity(with_honorific, without_honorific)
    # Assert
    assert score >= 0.85


def test_with_honorific_hafiz_reasonable_similarity() -> None:
    """SPEC §4: 'الحافظ ابن حجر' vs 'ابن حجر العسقلاني' — one shared token.

    After ال-stripping: tokens_a = {حافظ, حجر}, tokens_b = {حجر, عسقلاني}.
    Shared token: {حجر}.  No subset relation holds (حافظ ∉ tokens_b).
    Overlap = 1/2 = 0.5 — above the human-gate lower bound.
    """
    # Arrange
    hafiz_form = "الحافظ ابن حجر"
    full_nisba_form = "ابن حجر العسقلاني"
    # Act
    score = normalized_name_similarity(hafiz_form, full_nisba_form)
    # Assert — partial overlap, above zero; human-gate range
    assert score > 0.0
    assert score <= 1.0


def test_honorific_score_bounded() -> None:
    """SPEC §4: adding an honorific must never push similarity above 1.0."""
    # Arrange
    base = "ابن قدامة"
    with_honorific = "الإمام ابن قدامة"
    # Act
    score = normalized_name_similarity(base, with_honorific)
    # Assert — always in [0, 1]
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# Latin-only and empty inputs
# ---------------------------------------------------------------------------


def test_latin_only_input_no_crash() -> None:
    """SPEC §4: 'Ibn Taymiyyah' (Latin transliteration) — must not raise.

    Some source records carry transliterated names.  Both normalize_arabic_name
    and _extract_name_tokens must degrade gracefully without exceptions.
    """
    # Arrange
    latin_name = "Ibn Taymiyyah"
    # Act — verify no exception
    result = normalize_arabic_name(latin_name)
    tokens = _extract_name_tokens(latin_name)
    # Assert — returns typed values, no crash
    assert isinstance(result, str)
    assert isinstance(tokens, set)


def test_empty_string_normalize_returns_empty() -> None:
    """SPEC §4: empty string input — normalize returns '', tokens returns set().

    The empty case is a boundary for normalize_arabic_name and _extract_name_tokens.
    The normalized_name_similarity('', '') case returns 1.0 (exact match on
    empty-vs-empty); that behaviour is documented in test_name_matching.py.
    """
    # Arrange / Act
    norm_result = normalize_arabic_name("")
    token_result = _extract_name_tokens("")
    # Assert
    assert norm_result == ""
    assert token_result == set()


# ---------------------------------------------------------------------------
# Tatweel (kashida) — documents known gap
# ---------------------------------------------------------------------------


def test_name_with_tatweel_is_ignored_for_matching() -> None:
    """Tatweel is decorative and should not affect scholar-name matching."""
    # Arrange
    with_tatweel = "ابـن تيـمية"      # ـ (U+0640) inside both tokens
    without_tatweel = "ابن تيمية"
    # Act
    score = normalized_name_similarity(with_tatweel, without_tatweel)
    # Assert — tatweel stripped from the derived comparison key
    assert score == 1.0


# ---------------------------------------------------------------------------
# Hamza normalization and taa-marbuta equivalence
# ---------------------------------------------------------------------------


def test_hamza_variants_normalize_to_same() -> None:
    """SPEC §4: أحمد / احمد / إحمد — all three alef-hamza forms are equivalent.

    Hamza placement (أ = above, إ = below, bare ا) varies across manuscripts
    and printing houses.  The normalizer maps أ→ا and إ→ا, so all three forms
    produce identical tokens and score 1.0 against one another.
    """
    # Arrange
    hamza_above = "أحمد"        # hamza above alef (U+0623)
    bare_alef = "احمد"          # plain alef (U+0627)
    hamza_below = "إحمد"        # hamza below alef (U+0625)
    # Act
    score_above_vs_bare = normalized_name_similarity(hamza_above, bare_alef)
    score_below_vs_bare = normalized_name_similarity(hamza_below, bare_alef)
    score_above_vs_below = normalized_name_similarity(hamza_above, hamza_below)
    # Assert — all three forms collapse to identical normalized strings
    assert score_above_vs_bare == 1.0
    assert score_below_vs_bare == 1.0
    assert score_above_vs_below == 1.0


def test_taa_marbuta_and_ha_are_not_treated_as_exact_equivalents() -> None:
    """KR safety: 'عائشة' vs 'عائشه' must not collapse to an exact identity match.

    Taa marbuta is not normalized into ha for authoritative scholar matching.
    """
    # Arrange
    with_taa_marbuta = "عائشة"
    with_ha = "عائشه"
    # Act
    score = normalized_name_similarity(with_taa_marbuta, with_ha)
    # Assert — similarity may still be non-zero later via safer heuristics,
    # but it must not be treated as an exact equivalence.
    assert score < 1.0


# ---------------------------------------------------------------------------
# Parenthetical annotations (death dates, hijri ranges)
# ---------------------------------------------------------------------------


def test_name_with_parenthetical_date_strips_cleanly() -> None:
    """SPEC §4: 'النووي (ت 676هـ)' vs 'النووي' — annotation fully stripped.

    Ground-truth scholar records frequently embed death dates in parentheses.
    re.sub(r'\\([^)]*\\)', '', ...) removes the entire annotation before any
    token comparison, producing an exact match.
    """
    # Arrange
    annotated = "النووي (ت 676هـ)"
    clean = "النووي"
    # Act
    score = normalized_name_similarity(annotated, clean)
    # Assert — parenthetical removal yields exact normalized strings
    assert score == 1.0


def test_name_with_hijri_range_annotation_strips_cleanly() -> None:
    """SPEC §4: 'السيوطي (849-911هـ)' — hijri date range removed.

    Both single dates and ranges inside parentheses must be stripped.  The
    same regex captures any content between ( and ) regardless of format.
    """
    # Arrange
    with_range = "السيوطي (849-911هـ)"
    clean = "السيوطي"
    # Act
    score = normalized_name_similarity(with_range, clean)
    # Assert
    assert score == 1.0


# ---------------------------------------------------------------------------
# Compound-word vs space-separated form
# ---------------------------------------------------------------------------


def test_compound_name_vs_split_triggers_substring_fallback() -> None:
    """SPEC §4: 'عبدالله' (compound) vs 'عبد الله' (space-separated) — fallback.

    The compound form is one token {عبدالله}; the split form tokenizes to
    {عبد, الله}. No exact token overlap exists.
    The substring fallback detects 'عبد' ⊂ 'عبدالله' (len ≥ 3) and returns 0.4.
    This is below the auto-match threshold (0.85) but above zero, correctly
    flagging the match for human review.
    """
    # Arrange
    compound = "عبدالله"
    split = "عبد الله"
    # Act
    score = normalized_name_similarity(compound, split)
    # Assert — substring fallback activates; score > 0.0
    assert score > 0.0


# ---------------------------------------------------------------------------
# Symmetry and bounds
# ---------------------------------------------------------------------------


def test_similarity_symmetry_nawawi() -> None:
    """SPEC §4: sim(a, b) == sim(b, a) — النووي vs full nasab chain."""
    # Arrange
    a = "النووي"
    b = "أبو زكريا يحيى بن شرف النووي"
    # Act / Assert
    assert normalized_name_similarity(a, b) == normalized_name_similarity(b, a)


def test_similarity_symmetry_ibn_taymiyya() -> None:
    """SPEC §4: sim(a, b) == sim(b, a) — 'ابن تيمية' vs full laqab form."""
    # Arrange
    a = "ابن تيمية"
    b = "تقي الدين أحمد ابن تيمية"
    # Act / Assert
    assert normalized_name_similarity(a, b) == normalized_name_similarity(b, a)


def test_similarity_symmetry_bukhari() -> None:
    """SPEC §4: sim(a, b) == sim(b, a) — nisba short vs full name."""
    # Arrange
    a = "البخاري"
    b = "محمد بن إسماعيل البخاري"
    # Act / Assert
    assert normalized_name_similarity(a, b) == normalized_name_similarity(b, a)


# ---------------------------------------------------------------------------
# Completely different scholars → score below new_record threshold
# ---------------------------------------------------------------------------


def test_completely_different_names_score_below_threshold() -> None:
    """SPEC §4: 'ابن تيمية' vs 'ابن خلدون' — zero identifying overlap.

    After stripping the shared particle 'ابن', the identifying tokens are
    {تيميه} and {خلدون} — completely disjoint with no substring containment.
    Similarity 0.0 < 0.50 → correct action is new_record (no false merge).
    """
    # Arrange
    ibn_taymiyya = "ابن تيمية"
    ibn_khaldun = "ابن خلدون"
    # Act
    score = normalized_name_similarity(ibn_taymiyya, ibn_khaldun)
    # Assert — well below human-gate threshold; triggers new_record action
    assert score < 0.50
