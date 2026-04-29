"""Phase 5b follow-up 36 closure 2026-04-29 — HadithSubgenre.ADHKAR and ADAB additions.

4-evaluator cross-provider dispatch (Codex CLI gpt-5.4 + Gemini Run A/B gemini-2.5-pro
+ arabic-reviewer Anthropic Agent, all through /prompt-architect with CAI Critique-Revise
+ Step-Back + TIDD-EC hybrid framework — same framework vindicated by FU-37). 3-of-3
cross-provider scholarly convergence on ADD-EXCLUDED for both Q-B (ADHKAR) and Q-C (ADAB):
the works tag correctly at subgenre level but Axis 3 carve-back BLOCKS — owner override
is REJECTED under Axis 1 per the SHAMAIL precedent.

Q-A (is_abridgement orthogonal property) was BLOCKED at 2-of-4 cross-provider convergence
(Codex + arabic-reviewer): all enumerated PROCEED paths failed to wire into the level
gate or dispute path; documented limitations L-FU36-1 (_extract_target narrowness) and
L-FU36-2 (gate-semantics gap requiring future architectural path-5) added to INV-SRC-0012.
"""
from __future__ import annotations

import pytest

from engines.source.contracts import (
    Genre,
    HadithSubgenre,
    LEVELED_HADITH_SUBGENRES,
)
from engines.source.src.deliberation import _infer_hadith_subgenre


# ---------------------------------------------------------------------------
# AC-FU36-1: bare "الأذكار" returns None subgenre under compound-rule discipline
# (preserves the existing test_step_50_deliberation.py:977 assertion that
# "كتاب الأذكار" -> None and extends it to bare al-Nawawī title)
# ---------------------------------------------------------------------------


def test_ac_fu36_1_bare_adhkar_title_returns_none():
    """al-Nawawī's *al-Adhkār* with bare title returns None subgenre.

    Per FU-36 compound-rule discipline: bare "أذكار" / "ذكر" / "دعاء" are
    FORBIDDEN as standalone inference triggers due to false-positive collisions
    with non-hadith taṣawwuf works, sermon collections, and fiqh chapter
    headings. This preserves the test_step_50_deliberation.py:977 behavior.
    """
    result = _infer_hadith_subgenre(
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        title="الأذكار",
    )
    assert result is None, (
        "Bare 'الأذكار' must return None subgenre per FU-36 compound-rule discipline; "
        "an explicit ADHKAR rule would require a compound co-occurrence."
    )


# ---------------------------------------------------------------------------
# AC-FU36-2: ADHKAR compound rules — positive matches
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title",
    [
        "عمل اليوم والليلة",  # Ibn al-Sunnī d. 364 AH
        "عمل اليوم",
        "عمل الليلة",
        "الحصن الحصين",  # al-Jazarī d. 833 AH
        "الكلم الطيب",  # Ibn Taymiyyah d. 728 AH
        "كلم طيب",
        "أذكار الصباح",  # occasion compound
        "أذكار المساء",
        "أذكار اليوم والليلة",
        "أذكار النوم",
        "أذكار السفر",
    ],
)
def test_ac_fu36_2_adhkar_compound_positives(title: str):
    """ADHKAR compound-rule positive matches.

    Per al-Kattānī, *al-Risālah al-Mustaṭrafah* p. 119-120 (*Aʿmāl al-Yawm
    wa-l-Laylah*); Ḥājī Khalīfa, *Kashf al-Ẓunūn* on *علم الأوراد المشهورة
    والأدعية المأثورة*; al-Khaṭīb al-Baghdādī, *al-Jāmiʿ li-Akhlāq al-Rāwī*
    riwāyah/taʿlīm distinction.
    """
    result = _infer_hadith_subgenre(
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        title=title,
    )
    assert result is HadithSubgenre.ADHKAR, (
        f"Title {title!r} should infer HadithSubgenre.ADHKAR, got {result!r}"
    )


# ---------------------------------------------------------------------------
# AC-FU36-2 (continued): ADHKAR is EXCLUDED from LEVELED_HADITH_SUBGENRES
# ---------------------------------------------------------------------------


def test_ac_fu36_2_adhkar_excluded_from_leveled_set():
    """ADHKAR enters the enum but is EXCLUDED from LEVELED_HADITH_SUBGENRES.

    SHAMAIL precedent: chain-preservation in Ibn al-Sunnī's canonical *ʿAmal
    al-Yawm wa-l-Laylah* (riwāyah-class per al-Khaṭīb al-Baghdādī) blocks
    LEVELED inclusion. Owner override on an ADHKAR-tagged hadith_collection
    is REJECTED under Axis 1.
    """
    assert HadithSubgenre.ADHKAR.value == "adhkar"
    assert "adhkar" not in LEVELED_HADITH_SUBGENRES, (
        "ADHKAR must NOT be in LEVELED_HADITH_SUBGENRES per FU-36 closure "
        "(chain-preservation in Ibn al-Sunnī's canonical anchor blocks "
        "LEVELED inclusion per SHAMAIL precedent)."
    )


# ---------------------------------------------------------------------------
# AC-FU36-3: ADAB compound rules — positive matches
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title",
    [
        "الأدب المفرد",  # al-Bukhārī d. 256 AH — canonical anchor
        "روضة العقلاء",  # Ibn Ḥibbān d. 354 AH
        "الجامع لأخلاق الراوي",  # al-Khaṭīb al-Baghdādī d. 463 AH
        "الجامع لأخلاق الراوي وآداب السامع",
    ],
)
def test_ac_fu36_3_adab_compound_positives(title: str):
    """ADAB compound-rule positive matches.

    Per al-Suyūṭī, *Tadrīb al-Rāwī* Muqaddimah on *aqsām al-kutub al-muṣannafah*
    (novel anchor — surfaced by arabic-reviewer DIM-AR1, not cited by either
    Gemini in FU-35): al-Adab al-Mufrad is *muṣannaf*-class in the *aʿmāl
    wa-l-ādāb* sub-category, NOT *jāmiʿ*-class. The compound rule "الأدب" +
    "المفرد" fires correctly; the al-Khaṭīb compound "الجامع" + "لأخلاق"
    fires BEFORE the generic "جامع" catch-all (ordering hazard managed per
    Codex DIM-CDX4 finding).
    """
    result = _infer_hadith_subgenre(
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        title=title,
    )
    assert result is HadithSubgenre.ADAB, (
        f"Title {title!r} should infer HadithSubgenre.ADAB, got {result!r}"
    )


def test_ac_fu36_3_adab_excluded_from_leveled_set():
    """ADAB enters the enum but is EXCLUDED from LEVELED_HADITH_SUBGENRES.

    Chain-preservation in al-Bukhārī's canonical *al-Adab al-Mufrad* blocks
    LEVELED inclusion per SHAMAIL precedent. Owner override on an ADAB-tagged
    hadith_collection is REJECTED under Axis 1.
    """
    assert HadithSubgenre.ADAB.value == "adab"
    assert "adab" not in LEVELED_HADITH_SUBGENRES, (
        "ADAB must NOT be in LEVELED_HADITH_SUBGENRES per FU-36 closure "
        "(chain-preservation in al-Bukhārī's canonical *al-Adab al-Mufrad* "
        "blocks LEVELED inclusion per SHAMAIL precedent)."
    )


def test_ac_fu36_3_adab_naming_collision_documented():
    """CRIT-FU36-1: Genre.ADAB and HadithSubgenre.ADAB share the string value 'adab'.

    Both enums have value 'adab' but operate at different dimensions:
    - Genre.ADAB = a work whose primary classification is adab literature
      (e.g., al-Mubarrad's al-Kāmil)
    - HadithSubgenre.ADAB = a hadith collection with adab thematic focus
      (e.g., al-Bukhārī's al-Adab al-Mufrad, with genre=HADITH_COLLECTION)

    Display layers MUST disambiguate by enum-class context. JSON serialization
    without type context is ambiguous and forbidden (T-1 risk).
    """
    assert Genre.ADAB.value == "adab"
    assert HadithSubgenre.ADAB.value == "adab"
    # Different enum classes: the naming collision is a documented risk,
    # NOT a fatal problem at the Pydantic model layer (fields have distinct
    # enum types). The risk is at the display/serialization boundary.
    assert Genre.ADAB is not HadithSubgenre.ADAB
    assert type(Genre.ADAB) is not type(HadithSubgenre.ADAB)


# ---------------------------------------------------------------------------
# AC-FU36-4: Q-C path-2 (KEEP-AS-JAMI-VIA-NEW-KEYWORD) UNANIMOUSLY REJECTED
# regression guard
# ---------------------------------------------------------------------------


def test_ac_fu36_4_al_adab_al_mufrad_is_not_jami():
    """Path-2 (KEEP-AS-JAMI-VIA-NEW-KEYWORD) was UNANIMOUSLY REJECTED by all 4 evaluators.

    Per al-Suyūṭī, *Tadrīb al-Rāwī* Muqaddimah, a *jāmiʿ* must cover all
    eight traditional Islamic subjects; *al-Adab al-Mufrad* is a *muṣannaf*
    in the *aʿmāl wa-l-ādāb* sub-category, bounded to the adab/akhlaq
    domain. Path-1 (NEW-SUBGENRE-ADAB) is the converged action. This test
    is a REGRESSION GUARD: any future implementation that tries to map
    al-Adab al-Mufrad to JAMI must fail this test.
    """
    result = _infer_hadith_subgenre(
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        title="الأدب المفرد",
    )
    assert result is HadithSubgenre.ADAB, (
        "al-Adab al-Mufrad MUST infer HadithSubgenre.ADAB (path-1), "
        "NOT HadithSubgenre.JAMI (path-2 unanimously rejected by all 4 "
        f"FU-36 evaluators). Got {result!r}."
    )
    assert result is not HadithSubgenre.JAMI, (
        "Regression guard: al-Adab al-Mufrad must NEVER be classified as "
        "HadithSubgenre.JAMI. Per al-Suyūṭī's muṣannaf vs jāmiʿ taxonomy, "
        "al-Adab al-Mufrad is muṣannaf-class. Any future code that assigns "
        "JAMI to this work is a T-4 scope-distortion regression."
    )


# ---------------------------------------------------------------------------
# AC-FU36-5: ADHKAR + ADAB false-positive guards (compound-keyword discipline)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title,science_scope,genre",
    [
        # Bare "أذكار" / "ذكر" / "دعاء" without compound disambiguators in
        # non-hadith contexts — pre-condition guard at deliberation.py:627
        # blocks these.
        ("ذكر الله في القلب", ["tasawwuf"], Genre.MATN),
        ("الأدب الكبير", ["adab"], Genre.MATN),
        # Bare "الأدب" / "أدب" in hadith context but without "المفرد"
        # disambiguator — compound-rule discipline blocks false positive.
        ("الأدب الصغير", ["hadith"], Genre.HADITH_COLLECTION),
        # Bare "الأدب" without compound — would match Genre.ADAB pattern
        # but not HadithSubgenre.ADAB compound rule.
        ("كتاب الأدب", ["hadith"], Genre.HADITH_COLLECTION),
    ],
)
def test_ac_fu36_5_compound_keyword_false_positive_guards(
    title: str,
    science_scope: list[str],
    genre: Genre,
) -> None:
    """Bare keywords without compound disambiguators MUST NOT fire ADHKAR or ADAB.

    The pre-condition guard at deliberation.py:627 + compound-keyword discipline
    prevent false positives. Non-hadith contexts return None subgenre via the
    pre-condition early-exit. Hadith contexts return None subgenre via failure
    of all compound rules.
    """
    result = _infer_hadith_subgenre(
        science_scope=science_scope,
        genre=genre,
        title=title,
    )
    assert result is None or result not in (
        HadithSubgenre.ADHKAR,
        HadithSubgenre.ADAB,
    ), (
        f"False-positive: title={title!r} (science_scope={science_scope}, "
        f"genre={genre.value}) must NOT fire ADHKAR or ADAB; got {result!r}"
    )


# ---------------------------------------------------------------------------
# Inference-rule ordering hazard regression guard (Codex DIM-CDX4):
# sharḥ on adhkār / al-Adab al-Mufrad must be tagged HADITH_COMMENTARY,
# NOT ADHKAR / ADAB
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title",
    [
        "شرح الأذكار",  # sharḥ on al-Nawawī's al-Adhkār
        "شرح عمل اليوم والليلة",  # sharḥ on Ibn al-Sunnī
        "شرح الأدب المفرد",  # sharḥ on al-Bukhārī's al-Adab al-Mufrad
    ],
)
def test_fu36_inference_ordering_hazard_sharh_takes_precedence(title: str):
    """Codex DIM-CDX4: sharḥ on ADHKAR/ADAB works must precede ADHKAR/ADAB rules.

    Per the inference rule ordering at deliberation.py:622-756, the
    HADITH_COMMENTARY branch (genre==Genre.SHARH AND science_scope contains
    'hadith') fires BEFORE the FU-36 compound rules. A sharḥ on al-Adhkār /
    al-Adab al-Mufrad is correctly tagged HADITH_COMMENTARY, NOT ADHKAR / ADAB.
    """
    result = _infer_hadith_subgenre(
        science_scope=["hadith"],
        genre=Genre.SHARH,
        title=title,
    )
    assert result is HadithSubgenre.HADITH_COMMENTARY, (
        f"Sharḥ on FU-36 work {title!r} must be tagged HADITH_COMMENTARY "
        f"(sharḥ branch precedes ADHKAR/ADAB compound rules per Codex DIM-CDX4 "
        f"ordering analysis); got {result!r}"
    )


# ---------------------------------------------------------------------------
# Pre-condition guard: non-hadith science_scope blocks ADHKAR/ADAB inference
# ---------------------------------------------------------------------------


def test_fu36_pre_condition_guard_blocks_non_hadith_science_scope():
    """deliberation.py:627 pre-condition guard prevents non-hadith works from
    entering ADHKAR/ADAB compound-rule chain.
    """
    # Non-hadith science_scope, non-HADITH_COLLECTION genre → early-exit
    result = _infer_hadith_subgenre(
        science_scope=["tasawwuf"],
        genre=Genre.MATN,
        title="عمل اليوم والليلة",  # would fire ADHKAR if reached
    )
    assert result is None, (
        "Pre-condition guard at deliberation.py:627 must early-exit for "
        "non-hadith context, preventing ADHKAR/ADAB false positives."
    )
