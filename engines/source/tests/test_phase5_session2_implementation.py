"""Phase 5 Session 2 implementation — spec-linked tests.

Covers the three Session 2 atoms feeding the Stage-1 deterministic
narrowing layer:

  - REQ-SRC-0050 Scholar fragment normalization + 5-component parsing (5 ACs)
  - REQ-SRC-0051 Deterministic candidate generation w/ work-title channel (6 ACs)
  - INV-SRC-0014 Matching-key honorific exclusion + bidi-strip ordering (4 ACs)

Each test carries ``@pytest.mark.spec(atom_id, ac_id)`` so failures identify
the exact spec violation. Real Arabic fixture data is used per
``.claude/rules/testing.md``: الإمام البخاري, عبد الله بن المبارك, أبو حنيفة
النعمان بن ثابت الكوفي, الإمام النووي with شرح صحيح مسلم, الكاساني with
بدائع الصنائع, Persian گيلاني preserving U+06AF.

Defensive negative cases per Session 1 §5 learning (asymmetric-validator
pattern as a generalizable defect class) are added throughout — every state-
machine branch is exercised against its symmetric counterpart.
"""

from __future__ import annotations

import pytest

from engines.source.contracts import ErrorCode, ScholarAuthorityRecord
from shared.scholar_authority.src.fragment_parser import (
    CompoundNameSplitError,
    FragmentNotArabicError,
    HonorificOnlyNameError,
    parse_fragment,
)
from shared.scholar_authority.src.match_contracts import (
    K_CAP_DEGRADED,
    K_CAP_STANDARD,
    DossierContext,
    ScholarEvidencePacket,
)
from shared.scholar_authority.src.name_matching import (
    InvisibleStripOccurrence,
    strip_invisible_unicode,
)
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshotDriftError,
    pin_registry_snapshot,
)
from shared.scholar_authority.src.stage1_narrowing import (
    WORK_TITLE_LIST_SIZE_GUARD,
    Registry,
    decompose_compound_title,
    narrow_candidates,
    normalize_work_title_for_index,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_RV = "2026-04-15.r1"
_NOW = "2026-04-30T16:00:00+00:00"


def _scholar(
    canonical_id: str, name: str, **kwargs: object
) -> ScholarAuthorityRecord:
    """Build a ScholarAuthorityRecord with sane Phase-5 defaults."""
    return ScholarAuthorityRecord(
        canonical_id=canonical_id,
        canonical_name_ar=name,
        last_updated=_NOW,
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.fixture
def core_registry() -> Registry:
    """Registry covering REQ-SRC-0051 ACs 1-6 (al-Kasani, al-Nawawi, Muslim,
    Gilani, polysemic Hanafi cluster, kunyah-only Abu Hanifa cluster)."""
    scholars = [
        _scholar(
            "sch_00010",
            "علاء الدين الكاساني",
            nisba=["الكاساني", "الحنفي"],
            known_works=["بدائع الصنائع"],
            era_century_hijri=6,
            death_date_hijri=587,
            school_affiliations={"fiqh": "hanafi"},
        ),
        _scholar(
            "sch_00020",
            "يحيى بن شرف النووي",
            kunya="أبو زكريا",
            nisba=["النووي", "الشافعي"],
            known_works=["شرح صحيح مسلم", "رياض الصالحين"],
            era_century_hijri=7,
            death_date_hijri=676,
            school_affiliations={"fiqh": "shafii"},
        ),
        _scholar(
            "sch_00021",
            "مسلم بن الحجاج النيسابوري",
            nisba=["النيسابوري"],
            known_works=["صحيح مسلم"],
            era_century_hijri=3,
            death_date_hijri=261,
        ),
        _scholar(
            "sch_00050",
            "عبد القادر الجيلاني",
            nisba=["الجيلاني", "الكيلاني"],
            known_works=["الفتوحات الغيبية", "گلستان الفقه"],
            era_century_hijri=6,
        ),
        # Polysemic Hanafi cluster — 7 scholars share known_works=["مختصر"]
        # and nisba=["الحنفي"] for AC-2 list-size guard testing.
        *[
            _scholar(
                f"sch_002{i:02d}",
                f"عالم حنفي {i}",
                nisba=["الحنفي"],
                known_works=["مختصر"],
                era_century_hijri=5 + (i % 4),
            )
            for i in range(1, 8)
        ],
        # 12 distinct scholars carrying kunya="أبو حنيفة" (AC-5 K-cap test).
        *[
            _scholar(
                f"sch_003{i:02d}",
                f"عالم {i} أبو حنيفة",
                kunya="أبو حنيفة",
                era_century_hijri=2 + i,
            )
            for i in range(1, 13)
        ],
    ]
    return Registry(release_version=_RV, scholars=scholars)


# ---------------------------------------------------------------------------
# REQ-SRC-0050 — 5-component fragment normalization
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0050", "AC-1")
def test_full_honorific_plus_nisba_strips_to_match_key() -> None:
    """AC-1: 'الإمام البخاري' → match_key='البخاري', nisba_list=['البخاري']."""
    result = parse_fragment("الإمام البخاري")
    assert result.display_fragment == "الإمام البخاري"
    assert result.match_key == "البخاري"
    assert result.parsed_components.nisba_list == ["البخاري"]
    assert result.parsed_components.ism is None
    assert result.parsed_components.kunyah is None
    # Display preserves the honorific (Critical Rule 2 byte-faithfulness).
    assert "الإمام" in result.display_fragment
    # No bidi marks → empty audit log.
    assert result.invisible_strip_log == []


@pytest.mark.spec("REQ-SRC-0050", "AC-2")
def test_compound_name_preserved_as_single_token() -> None:
    """AC-2: 'عبد الله بن المبارك' → ism='عبد الله' (compound preserved),
    nasab_chain=['بن المبارك']. Compound rule enforced; connector form
    preserved byte-faithfully per the atom's connector-preservation
    postcondition (same rule as AC-3)."""
    result = parse_fragment("عبد الله بن المبارك")
    assert result.parsed_components.ism == "عبد الله"
    # The compound stays a single semantic unit (NOT split into "عبد" / "الله").
    assert "عبد" not in result.parsed_components.nisba_list
    assert "الله" not in result.parsed_components.nisba_list
    # Nasab detected as patronymic chain link (preserves input connector form).
    assert result.parsed_components.nasab_chain == ["بن المبارك"]
    # No SRC-E-COMPOUND-NAME-SPLIT raised — happy path.


@pytest.mark.spec("REQ-SRC-0050", "AC-3")
def test_kunyah_ism_nasab_nisba_full_decomposition() -> None:
    """AC-3: 'أبو حنيفة النعمان بن ثابت الكوفي' → all 4 components populated."""
    result = parse_fragment("أبو حنيفة النعمان بن ثابت الكوفي")
    assert result.parsed_components.kunyah == "أبو حنيفة"
    assert result.parsed_components.ism == "النعمان"
    assert result.parsed_components.nasab_chain == ["بن ثابت"]
    assert result.parsed_components.nisba_list == ["الكوفي"]
    # laqab is allowed to be empty per the atom (any-null permitted).
    assert result.parsed_components.laqab == []
    # match_key contains all 4 components; alef-translation has been applied
    # (أبو → ابو) per REQ-SRC-0051 line 92-93 ALLOWED for matching key only.
    assert "ابو" in result.match_key
    assert "حنيفة" in result.match_key
    assert "النعمان" in result.match_key
    assert "ثابت" in result.match_key
    assert "الكوفي" in result.match_key


@pytest.mark.spec("REQ-SRC-0050", "AC-4")
def test_honorific_only_aborts_with_existing_error_code() -> None:
    """AC-4: 'الشيخ' (honorific-shell only) → SRC-E-HONORIFIC-ONLY-NAME.
    Reuses existing error code at contracts.py:579 per ChatGPT DR finding."""
    with pytest.raises(HonorificOnlyNameError) as excinfo:
        parse_fragment("الشيخ")
    assert excinfo.value.error_code == ErrorCode.HONORIFIC_ONLY_NAME


@pytest.mark.spec("REQ-SRC-0050", "AC-5")
def test_latin_fragment_rejected_with_not_arabic_error() -> None:
    """AC-5: 'Sibawayh' → SRC-E-FRAGMENT-NOT-ARABIC."""
    with pytest.raises(FragmentNotArabicError) as excinfo:
        parse_fragment("Sibawayh")
    assert excinfo.value.error_code == ErrorCode.FRAGMENT_NOT_ARABIC


# Defensive negative cases (asymmetric-validator pattern — Session 1 §5 learning)


@pytest.mark.spec("REQ-SRC-0050", "AC-5")
def test_empty_fragment_rejected() -> None:
    """Empty input must fail loud (Critical Rule 4)."""
    with pytest.raises(FragmentNotArabicError):
        parse_fragment("")


@pytest.mark.spec("REQ-SRC-0050", "AC-5")
def test_whitespace_only_fragment_rejected() -> None:
    """Whitespace-only input must fail loud."""
    with pytest.raises(FragmentNotArabicError):
        parse_fragment("   \t\n  ")


@pytest.mark.spec("REQ-SRC-0050", "AC-5")
def test_mixed_arabic_latin_fragment_rejected() -> None:
    """Mixed Arabic + Latin must fail at the match-call boundary."""
    with pytest.raises(FragmentNotArabicError):
        parse_fragment("الإمام Bukhari")


@pytest.mark.spec("REQ-SRC-0050", "F-5")
def test_bare_abd_without_divine_attribute_raises_compound_split() -> None:
    """F-5 closure: bare 'عبد' without ال-prefix divine attribute is a
    structural anomaly (truncation upstream); fail loud with
    SRC-E-COMPOUND-NAME-SPLIT."""
    with pytest.raises(CompoundNameSplitError) as excinfo:
        parse_fragment("عبد")
    assert excinfo.value.error_code == ErrorCode.COMPOUND_NAME_SPLIT


@pytest.mark.spec("REQ-SRC-0050", "F-5")
def test_abd_followed_by_non_al_token_raises_compound_split() -> None:
    """F-5 closure: 'عبد' followed by non-ال-prefix token is a split."""
    with pytest.raises(CompoundNameSplitError):
        parse_fragment("عبد ربه")


@pytest.mark.spec("REQ-SRC-0050", "AC-2")
def test_compound_abd_extended_divine_attributes() -> None:
    """Compound rule generalizes — every عبد + ال[X] preserves as a unit."""
    for divine_attr in ("الرحمن", "الرحيم", "العزيز", "الكريم", "الجبار"):
        fragment = f"عبد {divine_attr}"
        result = parse_fragment(fragment)
        assert result.parsed_components.ism == fragment, (
            f"Compound {fragment!r} was split"
        )


@pytest.mark.spec("REQ-SRC-0050", "AC-1")
def test_display_fragment_byte_identical_under_normalization() -> None:
    """Critical Rule 2: display_fragment is byte-identical to caller input
    even after Stage 1 / Stage 2 / Stage 3 mutate the analytical surface."""
    raw = "  الإمام البخاري  "  # leading/trailing whitespace
    result = parse_fragment(raw)
    assert result.display_fragment == raw  # NOT trimmed


@pytest.mark.spec("REQ-SRC-0050", "AC-3")
def test_kunyah_only_fragment_populates_kunyah_field() -> None:
    """REQ-SRC-0051 AC-5 precondition: kunyah-only fragment yields kunyah
    populated, ism null, nisba_list empty."""
    result = parse_fragment("أبو حنيفة")
    assert result.parsed_components.kunyah == "أبو حنيفة"
    assert result.parsed_components.ism is None
    assert result.parsed_components.nisba_list == []
    assert result.parsed_components.nasab_chain == []


# ---------------------------------------------------------------------------
# REQ-SRC-0051 — Stage-1 deterministic candidate generation
# ---------------------------------------------------------------------------


def _packet_for(
    fragment: str, dossier: DossierContext, registry: Registry
) -> ScholarEvidencePacket:
    """Helper: parse + narrow with default snapshot."""
    parse_result = parse_fragment(fragment)
    snapshot = pin_registry_snapshot(registry.release_version)
    return narrow_candidates(parse_result, dossier, snapshot, registry)


@pytest.mark.spec("REQ-SRC-0051", "AC-1")
def test_work_title_channel_resolves_single_canonical_id(
    core_registry: Registry,
) -> None:
    """AC-1: 'الكاساني' + 'بدائع الصنائع' (size 1, ≤N=3) → al-Kasani top-1
    with both work-title-channel + nisba-channel contributions."""
    dossier = DossierContext(
        primary_science="fiqh",
        school_affiliation_hints={"fiqh": "hanafi"},
        attributed_works=["بدائع الصنائع"],
        century_active_hijri_estimates=[6],
    )
    packet = _packet_for("الكاساني", dossier, core_registry)
    assert len(packet.candidate_set) >= 1
    top = packet.candidate_set[0]
    assert top.canonical_id == "sch_00010"
    # Both channels MUST appear in score_breakdown per AC-1.
    assert "work_title" in top.score_breakdown
    assert "nisba" in top.score_breakdown
    # Provenance lists both channels.
    assert "work_title" in top.provenance_for_inclusion
    assert "nisba" in top.provenance_for_inclusion


@pytest.mark.spec("REQ-SRC-0051", "AC-2")
def test_work_title_size_above_n_reverts_to_stage2_signal(
    core_registry: Registry,
) -> None:
    """AC-2: 'الحنفي' + 'مختصر' (resolves to 7 canonical_ids > N=3) →
    work-title channel reverts; no candidates have work_title in their
    score_breakdown."""
    dossier = DossierContext(
        primary_science="fiqh",
        attributed_works=["مختصر"],
    )
    packet = _packet_for("الحنفي", dossier, core_registry)
    # K cap (=8 standard) applies after channel merge.
    assert len(packet.candidate_set) <= K_CAP_STANDARD
    # Reverted channel: NO candidate has work_title in its score_breakdown.
    for cand in packet.candidate_set:
        assert "work_title" not in cand.score_breakdown, (
            f"Candidate {cand.canonical_id} has work_title score "
            f"despite list-size guard reversion"
        )


@pytest.mark.spec("REQ-SRC-0051", "AC-3")
def test_compound_title_decomposition_two_authors(
    core_registry: Registry,
) -> None:
    """AC-3: 'الإمام النووي' + 'شرح صحيح مسلم' → BOTH al-Nawawi (sharh
    author) and Muslim ibn al-Hajjaj (base-work author) appear in
    candidate_set with distinct provenance."""
    dossier = DossierContext(
        primary_science="hadith",
        attributed_works=["شرح صحيح مسلم"],
    )
    packet = _packet_for("الإمام النووي", dossier, core_registry)
    ids = {c.canonical_id for c in packet.candidate_set}
    assert "sch_00020" in ids, "al-Nawawi (sharh author) missing"
    assert "sch_00021" in ids, "Muslim (base-work author) missing"
    # Distinct channel labels: compound-work via 'work_title', base-work
    # via 'work_title_base'.
    nawawi = next(c for c in packet.candidate_set if c.canonical_id == "sch_00020")
    muslim = next(c for c in packet.candidate_set if c.canonical_id == "sch_00021")
    assert "work_title" in nawawi.score_breakdown
    assert "work_title_base" in muslim.score_breakdown


@pytest.mark.spec("REQ-SRC-0051", "AC-4")
def test_persian_kaf_preserved_in_work_title_match_key(
    core_registry: Registry,
) -> None:
    """AC-4: گ U+06AF + taa-marbuta + Persian/Urdu/Kurdish characters MUST
    NOT be normalized in the work-title match key."""
    # Direct unit test on the normalization function.
    title = "گلستان الفقه"
    normalized = normalize_work_title_for_index(title)
    assert chr(0x06AF) in normalized, "Persian گ U+06AF was collapsed"
    # Verify integration: registry entry with گ-preserving title is
    # surfaced when the dossier supplies the same title.
    dossier = DossierContext(attributed_works=["گلستان الفقه"])
    packet = _packet_for("الكيلاني", dossier, core_registry)
    ids = {c.canonical_id for c in packet.candidate_set}
    assert "sch_00050" in ids, "Persian-preserving Gilani not surfaced"


@pytest.mark.spec("REQ-SRC-0051", "AC-4")
def test_taa_marbuta_preserved_in_work_title_match_key() -> None:
    """AC-4 sub-claim: ة (taa marbuta U+0629) MUST NOT be normalized to ه."""
    # 'الهداية' (the famous Hanafi treatise) ends in taa-marbuta.
    # Normalizing to 'الهدايه' would silently merge with a different word.
    # The word legitimately contains an interior ه (الهـداية) — the
    # critical check is that the FINAL character is still ة, not ه.
    normalized = normalize_work_title_for_index("الهداية")
    assert normalized.endswith("ة"), (
        f"taa-marbuta was normalized; got {normalized!r}"
    )
    assert normalized == "الهداية"  # full byte-faithful preservation
    # Verify the contrapositive: a deliberately ه-ending variant remains
    # distinct from the ة-ending form (no merge across the distinction).
    haa_variant = normalize_work_title_for_index("الهدايه")
    assert haa_variant != normalized


@pytest.mark.spec("REQ-SRC-0051", "AC-4")
def test_unicode_normalization_forbidden() -> None:
    """Critical: NO Unicode NFC/NFD/NFKC/NFKD applied to stored titles per
    REQ-SRC-0051 line 99-100. Verified by checking that pre-composed forms
    are NOT decomposed into combining sequences (and vice versa)."""
    import unicodedata

    title = "بدائع الصنائع"
    normalized = normalize_work_title_for_index(title)
    # Result must NOT equal NFKD-decomposed form (decomposition would split
    # combined glyphs).
    assert normalized != unicodedata.normalize("NFKD", title)
    # Result must NOT equal NFKC if NFKC differs from input — the ALLOWED
    # transforms (tashkeel + tatweel + alef-variant) leave this title
    # unchanged, so the result equals the input here.
    assert normalized == title


@pytest.mark.spec("REQ-SRC-0051", "AC-5")
def test_kunyah_only_k_cap_truncation(core_registry: Registry) -> None:
    """AC-5: 'أبو حنيفة' kunyah-only with 12 carriers → K cap = 8 standard
    truncates the candidate set."""
    packet = _packet_for("أبو حنيفة", DossierContext(), core_registry)
    assert len(packet.candidate_set) <= K_CAP_STANDARD
    # Every candidate carries the kunyah channel hit.
    for cand in packet.candidate_set:
        assert "kunyah" in cand.score_breakdown


@pytest.mark.spec("REQ-SRC-0051", "AC-6")
def test_single_token_ism_routes_to_insufficient_evidence(
    core_registry: Registry,
) -> None:
    """AC-6 — sub-claim 1: 'محمد' single-ism on a registry with NO Muhammads,
    no dossier → no channel surfaces a candidate, candidate_set is empty.

    AC-6 is a two-claim AC. Sub-claim 1 (this test): empty result when no
    channel can surface a candidate. Sub-claim 2 (next test): when fuzzy
    name search WOULD surface many candidates, the K cap truncates to 8 and
    none satisfies the ≥2-non-name floor (Session-3 routing concern, but
    Session-2 must not pre-emptively prune the K-cap path)."""
    packet = _packet_for("محمد", DossierContext(), core_registry)
    # The K cap doesn't help when no channel surfaces anything.
    assert len(packet.candidate_set) == 0


@pytest.mark.spec("REQ-SRC-0051", "AC-6")
def test_single_token_ism_with_many_muhammads_truncates_to_k_cap() -> None:
    """AC-6 — sub-claim 2: 'محمد' single-ism on a registry with many
    canonical_ids whose canonical_name_ar starts with محمد → fuzzy name
    channel surfaces them, K cap = 8 standard truncates to top 8 by
    similarity. Each surviving candidate carries ONLY the name channel
    score (no nisba/kunyah/work_title) — INV-SRC-0013's ≥2-non-name floor
    will reject definitive at REQ-SRC-0053 routing in Session 3, but
    Stage-1 correctly produces the K-capped candidate_set per the atom's
    'fuzzy channels would return thousands; the K cap truncates to 8
    standard' specification."""
    # Build a registry with 20 distinct Muhammads — exceeds K_CAP_STANDARD=8
    # so the fuzzy name channel must over-fetch then truncate.
    scholars = [
        _scholar(
            f"sch_050{i:02d}",
            f"محمد بن {chr(0x0623 + (i % 20))} رقم {i}",  # distinct trailing tokens
            era_century_hijri=2 + (i % 13),
        )
        for i in range(1, 21)
    ]
    registry = Registry(release_version=_RV, scholars=scholars)
    parse_result = parse_fragment("محمد")
    snapshot = pin_registry_snapshot(_RV)
    packet = narrow_candidates(parse_result, DossierContext(), snapshot, registry)
    # K cap truncates to 8 standard.
    assert len(packet.candidate_set) == K_CAP_STANDARD
    # Each survivor surfaces ONLY via the name channel (single-token ism
    # → no other channel can fire without dossier signals).
    for cand in packet.candidate_set:
        assert "name" in cand.score_breakdown
        # No nisba / kunyah / work_title hits — fuzzy-only path.
        assert "nisba" not in cand.score_breakdown
        assert "kunyah" not in cand.score_breakdown
        assert "work_title" not in cand.score_breakdown
        assert "work_title_base" not in cand.score_breakdown
        assert "century_active" not in cand.score_breakdown


# Defensive negative cases for REQ-SRC-0051


@pytest.mark.spec("REQ-SRC-0051", "F-1")
def test_empty_attributed_works_does_not_call_work_title_channel(
    core_registry: Registry,
) -> None:
    """F-1: when no attributed_works are supplied, the work-title channel
    contributes nothing — only nisba/name channels surface candidates."""
    dossier = DossierContext()  # All fields empty
    packet = _packet_for("الكاساني", dossier, core_registry)
    for cand in packet.candidate_set:
        assert "work_title" not in cand.score_breakdown
        assert "work_title_base" not in cand.score_breakdown


@pytest.mark.spec("REQ-SRC-0051", "AC-2")
def test_work_title_at_threshold_n_3_still_contributes(
    core_registry: Registry,
) -> None:
    """List-size guard activates ABOVE N=3, not AT N=3. A title resolving
    to exactly 3 canonical_ids should still contribute candidates."""
    # Build a registry where exactly 3 scholars share a work-title.
    scholars = [
        _scholar(
            f"sch_010{i:02d}",
            f"عالم {i}",
            known_works=["كتاب التوحيد"],
            era_century_hijri=4 + i,
        )
        for i in range(1, 4)
    ]
    reg = Registry(release_version=_RV, scholars=scholars)
    dossier = DossierContext(attributed_works=["كتاب التوحيد"])
    packet = _packet_for("عالم 1", dossier, reg)
    # All 3 should appear with work_title channel hits.
    work_title_count = sum(
        1 for c in packet.candidate_set if "work_title" in c.score_breakdown
    )
    assert work_title_count == 3, (
        f"At N={WORK_TITLE_LIST_SIZE_GUARD} the channel should still "
        f"contribute; got {work_title_count} candidates"
    )


@pytest.mark.spec("REQ-SRC-0051", "AC-2")
def test_work_title_at_threshold_n_plus_1_reverts(
    core_registry: Registry,
) -> None:
    """List-size guard activates strictly above N=3 (i.e., size ≥ 4)."""
    scholars = [
        _scholar(
            f"sch_011{i:02d}",
            f"باحث {i}",
            known_works=["مختصر"],
            era_century_hijri=4 + i,
        )
        for i in range(1, 5)  # 4 scholars > N=3
    ]
    reg = Registry(release_version=_RV, scholars=scholars)
    dossier = DossierContext(attributed_works=["مختصر"])
    packet = _packet_for("باحث 1", dossier, reg)
    for cand in packet.candidate_set:
        assert "work_title" not in cand.score_breakdown


@pytest.mark.spec("REQ-SRC-0051", "AC-1")
def test_packet_is_immutable_and_frozen(core_registry: Registry) -> None:
    """ScholarEvidencePacket is locked at end of REQ-SRC-0051 — caller
    cannot mutate fields. CON-SRC-0009 contract."""
    dossier = DossierContext(attributed_works=["بدائع الصنائع"])
    packet = _packet_for("الكاساني", dossier, core_registry)
    with pytest.raises((TypeError, ValueError)):  # Pydantic frozen=True
        packet.match_key = "tampered"  # type: ignore[misc]


@pytest.mark.spec("REQ-SRC-0051", "F-1")
def test_registry_drift_raises_explicit_error() -> None:
    """REQ-SRC-0049 + INV-SRC-0017: snapshot drift between pin and observed
    registry version aborts narrowing with REGISTRY_SNAPSHOT_DRIFT."""
    reg = Registry(release_version="2026-04-15.r1", scholars=[])
    snapshot = pin_registry_snapshot("2026-05-01.r2")  # Different version
    parse_result = parse_fragment("البخاري")
    with pytest.raises(RegistrySnapshotDriftError) as excinfo:
        narrow_candidates(parse_result, DossierContext(), snapshot, reg)
    assert excinfo.value.error_code == ErrorCode.REGISTRY_SNAPSHOT_DRIFT


@pytest.mark.spec("REQ-SRC-0051", "AC-2")
def test_degraded_case_complexity_uses_larger_k_cap(
    core_registry: Registry,
) -> None:
    """Degraded case complexity uses K_CAP_DEGRADED=12 instead of standard 8."""
    parse_result = parse_fragment("أبو حنيفة")
    snapshot = pin_registry_snapshot(core_registry.release_version)
    packet = narrow_candidates(
        parse_result,
        DossierContext(),
        snapshot,
        core_registry,
        case_complexity="degraded",
    )
    assert len(packet.candidate_set) <= K_CAP_DEGRADED
    assert len(packet.candidate_set) >= 8, (
        "degraded should surface more than standard K=8 when 12 carriers exist"
    )


# ---------------------------------------------------------------------------
# INV-SRC-0014 — strict 3-stage bidi-strip ordering
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0014", "AC-1")
def test_clean_three_stage_ordering() -> None:
    """AC-1: clean 'الإمام البخاري' → Stage 1 produces unchanged text;
    Stage 2 strips honorific; Stage 3 builds key on remaining nisba."""
    result = parse_fragment("الإمام البخاري")
    assert result.invisible_strip_log == []  # Stage 1 no-op
    assert result.match_key == "البخاري"  # Stage 2 strip + Stage 3 key
    assert result.parsed_components.nisba_list == ["البخاري"]


@pytest.mark.spec("INV-SRC-0014", "AC-2")
def test_bidi_contaminated_three_stage_recovery() -> None:
    """AC-2: bidi-contaminated 'الإمام‎البخاري' (U+200E LTR mark between
    honorific and name token, NO surrounding whitespace) recovers
    correctly via Stage-1 strip-and-replace-with-space."""
    contaminated = "الإمام" + chr(0x200E) + "البخاري"
    result = parse_fragment(contaminated)
    # Stage 1 logs the U+200E occurrence (T-1 audit trail).
    assert len(result.invisible_strip_log) == 1
    occ = result.invisible_strip_log[0]
    assert occ.codepoint == "U+200E"
    assert isinstance(occ, InvisibleStripOccurrence)
    # Stage 2 + Stage 3 produce the same match key as the clean input.
    clean_result = parse_fragment("الإمام البخاري")
    assert result.match_key == clean_result.match_key
    # Display fragment preserves the original contaminated bytes per
    # Critical Rule 2.
    assert result.display_fragment == contaminated


@pytest.mark.spec("INV-SRC-0014", "AC-3")
def test_empty_match_key_aborts_with_honorific_only_name() -> None:
    """AC-3: honorific-shell-only fragment aborts via Stage 2 + Stage 3
    with SRC-E-HONORIFIC-ONLY-NAME (existing code from contracts.py:579).
    Overlaps REQ-SRC-0050 AC-4."""
    with pytest.raises(HonorificOnlyNameError) as excinfo:
        parse_fragment("الإمام")
    assert excinfo.value.error_code == ErrorCode.HONORIFIC_ONLY_NAME


@pytest.mark.spec("INV-SRC-0014", "AC-4")
def test_reversed_ordering_documents_wrong_behavior() -> None:
    """AC-4 contrapositive: documents the WRONG ordering's failure mode.

    If Stage 2 (honorific-strip) ran BEFORE Stage 1 (bidi-strip) on a
    bidi-contaminated fragment, the regex match for 'الإمام' would not
    match 'الإمام<U+200E>' (literal char sequence differs), the honorific
    would NOT be stripped, and the match_key would contain it — producing
    a false negative in candidate generation.

    This test verifies the CORRECT ordering recovers correctly (any
    implementation that fails to recover here is using the wrong ordering).
    """
    contaminated = "الإمام" + chr(0x200E) + "البخاري"
    result = parse_fragment(contaminated)
    # The honorific MUST be absent from the match_key — proves Stage 1 ran
    # before Stage 2.
    assert "الإمام" not in result.match_key
    assert "الامام" not in result.match_key  # post-alef-translation form
    assert "البخاري" in result.match_key


# Defensive negative cases for INV-SRC-0014


@pytest.mark.spec("INV-SRC-0014", "AC-2")
def test_multiple_bidi_marks_logged_with_distinct_offsets() -> None:
    """Every stripped invisible occurrence is logged with byte offset for
    audit per .claude/rules/input-sanitization.md."""
    contaminated = (
        "الشيخ" + chr(0x200E) + " " + chr(0x200F) + "البخاري" + chr(0xFEFF)
    )
    result = parse_fragment(contaminated)
    assert len(result.invisible_strip_log) == 3
    codepoints = {occ.codepoint for occ in result.invisible_strip_log}
    assert codepoints == {"U+200E", "U+200F", "U+FEFF"}
    # Byte offsets are monotonically increasing.
    offsets = [occ.byte_offset for occ in result.invisible_strip_log]
    assert offsets == sorted(offsets)


@pytest.mark.spec("INV-SRC-0014", "AC-1")
def test_strip_invisible_unicode_preserves_clean_text() -> None:
    """Unit test: clean Arabic text passes through strip_invisible_unicode
    unchanged with empty audit log."""
    cleaned, log = strip_invisible_unicode("الإمام البخاري")
    assert cleaned == "الإمام البخاري"
    assert log == []


@pytest.mark.spec("INV-SRC-0014", "AC-2")
def test_strip_invisible_unicode_persian_zwj_carve_out() -> None:
    """Persian/Urdu/Kurdish ZWJ carve-out: when caller opts in, U+200D
    (ZWJ) is preserved (compound-letter shaping is meaning-bearing)."""
    text = "خان" + chr(0x200D) + "زاده"
    cleaned_strict, log_strict = strip_invisible_unicode(
        text, preserve_persian_urdu_zwj=False
    )
    assert chr(0x200D) not in cleaned_strict
    assert len(log_strict) == 1

    cleaned_lenient, log_lenient = strip_invisible_unicode(
        text, preserve_persian_urdu_zwj=True
    )
    assert chr(0x200D) in cleaned_lenient
    assert log_lenient == []


# ---------------------------------------------------------------------------
# Helper-function unit tests
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0051", "AC-3")
def test_decompose_compound_title_recognizes_all_four_prefixes() -> None:
    """compound decomposition recognizes شرح / حاشية / تهذيب / مختصر prefixes."""
    cases = [
        ("شرح صحيح البخاري", ("شرح", "صحيح البخاري")),
        ("حاشية ابن عابدين", ("حاشية", "ابن عابدين")),
        ("تهذيب التهذيب", ("تهذيب", "التهذيب")),
        ("مختصر المنتهى", ("مختصر", "المنتهى")),
    ]
    for title, expected in cases:
        assert decompose_compound_title(title) == expected, (
            f"decomposition failed for {title!r}"
        )


@pytest.mark.spec("REQ-SRC-0051", "AC-3")
def test_decompose_compound_title_rejects_non_compound() -> None:
    """Non-compound titles return None (no false positives)."""
    for title in ("بدائع الصنائع", "صحيح مسلم", "الموطأ", "الفقه الأكبر"):
        assert decompose_compound_title(title) is None


@pytest.mark.spec("REQ-SRC-0051", "AC-4")
def test_normalize_work_title_idempotent() -> None:
    """The normalization function is idempotent — running it twice equals
    running it once."""
    titles = [
        "بَدائِع الصَنائِع",  # tashkeel
        "الـهداية",  # tatweel
        "آداب الـبحث",  # alef + tatweel
        "گلستان الفقه",  # Persian
    ]
    for title in titles:
        once = normalize_work_title_for_index(title)
        twice = normalize_work_title_for_index(once)
        assert once == twice, f"non-idempotent on {title!r}"


@pytest.mark.spec("REQ-SRC-0051", "AC-4")
def test_normalize_work_title_unifies_alef_variants() -> None:
    """Alef-variant unification (ا → آ / إ / أ / ٱ) for matching key."""
    inputs = ["آداب", "أداب", "إداب", "ٱداب"]
    expected_unified = "اداب"
    for inp in inputs:
        assert normalize_work_title_for_index(inp) == expected_unified
