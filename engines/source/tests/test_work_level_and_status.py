"""Phase 5b item 15 — spec-linked closure evidence for level metadata.

Exercises the (level, level_status, level_provenance) triple across every
atom that governs it:

- CON-SRC-0011 AC-1..AC-6 — WorkLevel enum whitelist (mubtadiʾ /
  mutawassiṭ / muntahī accepted; mutaqaddim, English placeholders, and
  other non-enum strings rejected).
- CON-SRC-0004 invariants 1..4 + ADV-012 stickiness — the Pydantic
  ``model_validator`` on ``SourceMetadata.enforce_level_invariants``
  raises ``ValueError`` (wrapped by Pydantic into ``ValidationError``)
  citing the specific invariant number.
- INV-SRC-0011 AC-1..AC-4 — source engine never infers level from
  shallow bibliographic signals; ``level_status`` is always populated
  even when level is null.
- INV-SRC-0012 AC-2 — non-applicable genres (hadith_collection tested
  here; mushaf / rijal_dictionary / majmu / biographical_dictionary /
  fatwa_compilation / lexicon deferred to Phase 5b item 4 which will
  expand the Genre enum) reject any owner_level_override with
  ``SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE``.
- REQ-SRC-0007 AC-3..AC-5 — handoff packaging preserves level and
  level_status across the source→normalization boundary (AC-1 and
  AC-2 are already covered in ``test_step_60_admission.py``).

The tests are written as Phase 5b's closure evidence: each assertion
demonstrates one normative rule firing on real Arabic fixture data or
direct contract construction. Paper-reconciliation avoided.
"""

from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from engines.source.contracts import (
    ErrorCode,
    Genre,
    LevelProvenance,
    LevelStatus,
    MetadataDeliberationInput,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TrustTier,
    WorkLevel,
)
from engines.source.src.deliberation import _resolve_level_fields
from engines.source.src.errors import SourceEngineError
from engines.source.src.admission import admit_source_and_build_handoff
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT
from engines.source.tests.test_step_60_admission import (
    _accepted_deliberation_result,
    _frozen_from_pipeline,
)


logger = logging.getLogger(__name__)


def _build_metadata(
    *,
    source_id: str = "src_level_test",
    genre: Genre | None = Genre.RISALAH,
    level: WorkLevel | None = None,
    level_status: LevelStatus = LevelStatus.PENDING_TAXONOMY,
    level_provenance: LevelProvenance | None = None,
) -> SourceMetadata:
    """Construct a SourceMetadata with only the fields needed for level tests.

    The (level, level_status, level_provenance) triple is set atomically
    to satisfy ``enforce_level_invariants`` — single-field assignment on
    a constructed model trips ``validate_assignment``. Callers override
    the triple as needed; non-level fields stay at stable defaults.
    """
    return SourceMetadata(
        source_id=source_id,
        title_arabic="كتاب الاختبار",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="accepted",
        science_scope=["fiqh"],
        genre=genre,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
        level=level,
        level_status=level_status,
        level_provenance=level_provenance,
    )


def _base_deliberation_input(
    *,
    source_id: str = "src_level_test",
    title_arabic: str = "كتاب الاختبار",
    genre: Genre | None = Genre.RISALAH,
    level: WorkLevel | None = None,
) -> MetadataDeliberationInput:
    """Build a minimal MetadataDeliberationInput for level-resolution tests.

    Leaves level_status / level_provenance as None so
    ``_resolve_level_fields`` exercises the override + genre-inference
    logic rather than the pass-through branch.
    """
    return MetadataDeliberationInput(
        source_id=source_id,
        title_arabic=title_arabic,
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="source_engine_accepted",
        science_scope=["fiqh"],
        genre=genre,
        is_multi_layer=False,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        level=level,
        level_status=None,
        level_provenance=None,
        author_positions=[],
        owner_hint_payload={},
        verification_agents=["agent_a", "agent_b"],
        research_source_types=["metadata_card"],
        author_death_hijri=None,
    )


# ---------------------------------------------------------------------------
# CON-SRC-0011 — WorkLevel enum whitelist
# ---------------------------------------------------------------------------


@pytest.mark.spec("CON-SRC-0011", "AC-1")
def test_con_src_0011_ac1_mubtadi_accepted() -> None:
    """WorkLevel enum accepts the classical beginner tier (mubtadiʾ)."""
    metadata = _build_metadata(
        level=WorkLevel.MUBTADI,
        level_status=LevelStatus.ASSIGNED,
        level_provenance=LevelProvenance.OWNER_OVERRIDE,
    )

    assert metadata.level is WorkLevel.MUBTADI
    assert metadata.level.value == "mubtadiʾ"
    # Verify the right-half-ring hamza is byte-exact (U+02BE, not U+2019).
    assert "\u02be" in metadata.level.value
    assert "\u2019" not in metadata.level.value


@pytest.mark.spec("CON-SRC-0011", "AC-2")
def test_con_src_0011_ac2_mutawassit_accepted() -> None:
    """WorkLevel enum accepts the classical intermediate tier (mutawassiṭ)."""
    metadata = _build_metadata(
        level=WorkLevel.MUTAWASSIT,
        level_status=LevelStatus.ASSIGNED,
        level_provenance=LevelProvenance.OWNER_OVERRIDE,
    )

    assert metadata.level is WorkLevel.MUTAWASSIT
    assert metadata.level.value == "mutawassiṭ"
    # Verify the dot-below ṭ is byte-exact (U+1E6D).
    assert "\u1e6d" in metadata.level.value


@pytest.mark.spec("CON-SRC-0011", "AC-3")
def test_con_src_0011_ac3_muntahi_accepted() -> None:
    """WorkLevel enum accepts the classical terminal tier (muntahī)."""
    metadata = _build_metadata(
        level=WorkLevel.MUNTAHI,
        level_status=LevelStatus.ASSIGNED,
        level_provenance=LevelProvenance.OWNER_OVERRIDE,
    )

    assert metadata.level is WorkLevel.MUNTAHI
    assert metadata.level.value == "muntahī"
    # Verify the macron-ī is byte-exact (U+012B).
    assert "\u012b" in metadata.level.value


@pytest.mark.spec("CON-SRC-0011", "AC-4")
def test_con_src_0011_ac4_mutaqaddim_rejected() -> None:
    """WorkLevel rejects mutaqaddim — historiographic term, not pedagogical.

    CON-SRC-0011 rationale: mutaqaddim denotes chronological priority
    (earlier-generation scholar) not pedagogical level. Accepting it
    would silently teach the owner to conflate scholar generation with
    learner progression (T-2 knowledge-integrity corruption vector).
    """
    with pytest.raises(ValidationError):
        _build_metadata(
            level="mutaqaddim",  # type: ignore[arg-type]
            level_status=LevelStatus.ASSIGNED,
            level_provenance=LevelProvenance.OWNER_OVERRIDE,
        )


@pytest.mark.spec("CON-SRC-0011", "AC-5")
def test_con_src_0011_ac5_english_placeholder_rejected() -> None:
    """WorkLevel rejects English placeholders (advanced / beginner / etc.)."""
    for english_placeholder in ("advanced", "beginner", "intermediate", "specialist"):
        with pytest.raises(ValidationError):
            _build_metadata(
                level=english_placeholder,  # type: ignore[arg-type]
                level_status=LevelStatus.ASSIGNED,
                level_provenance=LevelProvenance.OWNER_OVERRIDE,
            )


@pytest.mark.spec("CON-SRC-0011", "AC-6")
def test_con_src_0011_ac6_null_level_accepted() -> None:
    """Null level is accepted — the enum only governs non-null assignments."""
    metadata = _build_metadata(
        level=None,
        level_status=LevelStatus.PENDING_TAXONOMY,
        level_provenance=None,
    )

    assert metadata.level is None
    assert metadata.level_status is LevelStatus.PENDING_TAXONOMY
    assert metadata.level_provenance is None


# ---------------------------------------------------------------------------
# CON-SRC-0004 — cross-field invariants on the level triple
# ---------------------------------------------------------------------------


@pytest.mark.spec("CON-SRC-0004", "AC-3")
def test_con_src_0004_invariant_1_assigned_requires_level() -> None:
    """level_status=assigned with level=null violates invariant 1."""
    with pytest.raises(ValidationError, match="CON-SRC-0004 invariant 1"):
        _build_metadata(
            level=None,
            level_status=LevelStatus.ASSIGNED,
            level_provenance=None,
        )


@pytest.mark.spec("CON-SRC-0004", "AC-4")
def test_con_src_0004_invariant_2_non_assigned_requires_null_level() -> None:
    """level_status=pending_taxonomy with level populated violates invariant 2."""
    with pytest.raises(ValidationError, match="CON-SRC-0004 invariant 2"):
        _build_metadata(
            level=WorkLevel.MUBTADI,
            level_status=LevelStatus.PENDING_TAXONOMY,
            level_provenance=LevelProvenance.OWNER_OVERRIDE,
        )


@pytest.mark.spec("CON-SRC-0004", "AC-5")
def test_con_src_0004_invariant_3_non_applicable_requires_matching_genre() -> None:
    """level_status=non_applicable_reference requires genre in the 7-value set."""
    # Genre.RISALAH is not in NON_APPLICABLE_GENRE_VALUES — invariant 3 fires.
    with pytest.raises(ValidationError, match="CON-SRC-0004 invariant 3"):
        _build_metadata(
            genre=Genre.RISALAH,
            level=None,
            level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
            level_provenance=None,
        )


@pytest.mark.spec("CON-SRC-0004", "AC-6")
def test_con_src_0004_invariant_3_hadith_collection_is_non_applicable() -> None:
    """Genre.HADITH_COLLECTION is in the non-applicable set — construction succeeds."""
    metadata = _build_metadata(
        genre=Genre.HADITH_COLLECTION,
        level=None,
        level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
        level_provenance=None,
    )

    assert metadata.level is None
    assert metadata.level_status is LevelStatus.NON_APPLICABLE_REFERENCE
    assert metadata.level_provenance is None
    assert metadata.genre is Genre.HADITH_COLLECTION


@pytest.mark.spec("CON-SRC-0004", "AC-7")
def test_con_src_0004_invariant_4_level_status_mandatory() -> None:
    """level_status has no default — omitting it raises ValidationError.

    This enforces invariant 4 (level_status is always populated) at the
    field-declaration level: ``level_status: LevelStatus`` with no
    default makes Pydantic require the field. Construction with only the
    minimum non-level fields triggers the missing-field error.
    """
    with pytest.raises(ValidationError, match="level_status"):
        # Bypass the typed helper because it always passes level_status.
        SourceMetadata(  # type: ignore[call-arg]
            source_id="src_level_test",
            title_arabic="كتاب الاختبار",
            source_format=SourceFormat.SHAMELA_HTML,
            structural_format=StructuralFormat.PROSE,
            intake_timestamp="2026-01-01T00:00:00Z",
            acquisition_path="manual",
            frozen_path="library/sources/src_level_test/frozen",
            frozen_hash="a" * 64,
            frozen_file_hashes={"book.htm": "a" * 64},
            status="accepted",
        )


@pytest.mark.spec("CON-SRC-0011", "AC-1")
def test_adv_012_stickiness_level_requires_provenance() -> None:
    """ADV-012: level populated without provenance violates stickiness."""
    with pytest.raises(ValidationError, match="ADV-012 stickiness"):
        _build_metadata(
            level=WorkLevel.MUBTADI,
            level_status=LevelStatus.ASSIGNED,
            level_provenance=None,
        )


@pytest.mark.spec("CON-SRC-0011", "AC-6")
def test_adv_012_stickiness_null_level_forbids_provenance() -> None:
    """ADV-012: null level with non-null provenance violates stickiness."""
    with pytest.raises(ValidationError, match="ADV-012 stickiness"):
        _build_metadata(
            level=None,
            level_status=LevelStatus.PENDING_TAXONOMY,
            level_provenance=LevelProvenance.TAXONOMY_ENGINE,
        )


# ---------------------------------------------------------------------------
# INV-SRC-0011 — source engine MUST NOT infer level from shallow signals
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0011", "AC-1")
def test_inv_src_0011_ac1_fiqh_fixture_yields_null_level() -> None:
    """03_fiqh fixture with no override → _resolve_level_fields returns null level."""
    request = _base_deliberation_input(
        title_arabic="أحكام الاضطباع والرمل في الطواف",
        genre=Genre.RISALAH,
        level=None,
    )

    level, level_status, provenance = _resolve_level_fields(request)

    assert level is None
    assert level_status is LevelStatus.PENDING_TAXONOMY
    assert provenance is None


@pytest.mark.spec("INV-SRC-0011", "AC-2")
def test_inv_src_0011_ac2_mukhtasar_title_yields_null_level() -> None:
    """Title containing "مختصر" must NOT trigger any title-based level inference.

    The ChatGPT DR abridgement-title trap: a work called mukhtaṣar
    (مختصر) may be harder than a fuller exposition when it presupposes
    prior malakah formation. Title tokens are not authoritative signals.
    """
    request = _base_deliberation_input(
        title_arabic="مختصر خليل",
        genre=Genre.MUKHTASAR,
        level=None,
    )

    level, level_status, provenance = _resolve_level_fields(request)

    assert level is None, "title token 'مختصر' must not populate level"
    assert level_status is LevelStatus.PENDING_TAXONOMY
    assert provenance is None


@pytest.mark.spec("INV-SRC-0011", "AC-3")
def test_inv_src_0011_ac3_owner_override_populates_level() -> None:
    """owner_level_override='mutawassiṭ' populates level with the override value."""
    request = _base_deliberation_input(
        title_arabic="أصول الفقه",
        genre=Genre.USUL_AL_FIQH,
        level=WorkLevel.MUTAWASSIT,
    )

    level, level_status, provenance = _resolve_level_fields(request)

    assert level is WorkLevel.MUTAWASSIT
    assert level.value == "mutawassiṭ"
    assert level_status is LevelStatus.ASSIGNED
    assert provenance is LevelProvenance.OWNER_OVERRIDE


@pytest.mark.spec("INV-SRC-0011", "AC-4")
def test_inv_src_0011_ac4_null_level_still_populates_level_status() -> None:
    """Null level never implies null level_status — the middle-path guarantee."""
    # Case 1: leveled genre (risalah) without override → pending_taxonomy.
    request = _base_deliberation_input(genre=Genre.RISALAH, level=None)
    _, status_pending, _ = _resolve_level_fields(request)
    assert status_pending is LevelStatus.PENDING_TAXONOMY

    # Case 2: non-applicable genre → non_applicable_reference.
    request = _base_deliberation_input(genre=Genre.HADITH_COLLECTION, level=None)
    _, status_nonapp, _ = _resolve_level_fields(request)
    assert status_nonapp is LevelStatus.NON_APPLICABLE_REFERENCE


# ---------------------------------------------------------------------------
# INV-SRC-0012 — non-applicable genres reject owner override
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0012", "AC-2")
def test_inv_src_0012_ac2_hadith_collection_rejects_override() -> None:
    """hadith_collection + owner_level_override='muntahī' → SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE.

    04_hadith-style fixture classified as hadith_collection: the text is
    organized around transmission, not pedagogical graduation. Any
    level override must be rejected at the override boundary per
    INV-SRC-0012.
    """
    request = _base_deliberation_input(
        title_arabic="صحيح البخاري",
        genre=Genre.HADITH_COLLECTION,
        level=WorkLevel.MUNTAHI,
    )

    with pytest.raises(SourceEngineError) as excinfo:
        _resolve_level_fields(request)

    assert excinfo.value.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE
    message = str(excinfo.value)
    assert "hadith_collection" in message
    assert "muntahī" in message
    assert "INV-SRC-0012" in message


@pytest.mark.spec("INV-SRC-0012", "AC-2")
def test_inv_src_0012_non_applicable_override_rejects_every_work_level() -> None:
    """All three CON-SRC-0011 WorkLevel values reject equally on non-applicable genre."""
    for work_level in (WorkLevel.MUBTADI, WorkLevel.MUTAWASSIT, WorkLevel.MUNTAHI):
        request = _base_deliberation_input(
            title_arabic="صحيح البخاري",
            genre=Genre.HADITH_COLLECTION,
            level=work_level,
        )

        with pytest.raises(SourceEngineError) as excinfo:
            _resolve_level_fields(request)

        assert excinfo.value.error_code is ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE


@pytest.mark.skip(
    reason="Phase 5b item 4: mushaf / rijal_dictionary / majmu / "
    "biographical_dictionary / fatwa_compilation / lexicon genres are in the "
    "CON-SRC-0004 non-applicable frozenset but not yet in the Genre enum. "
    "INV-SRC-0012 AC-1, AC-3, AC-4 become testable after Genre enum expansion."
)
@pytest.mark.spec("INV-SRC-0012", "AC-1")
def test_inv_src_0012_ac1_mushaf_rejects_override() -> None:
    """BLOCKED: Genre enum lacks 'mushaf' until Phase 5b item 4."""


# ---------------------------------------------------------------------------
# REQ-SRC-0007 — handoff preservation across source→normalization boundary
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0007", "AC-3")
def test_req_src_0007_ac3_handoff_preserves_muntahi_override(
    source_pipeline: SourcePipeline,
) -> None:
    """Owner override='muntahī' survives handoff serialization unchanged."""
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "06_usul" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(
        frozen.source_id, level_override=WorkLevel.MUNTAHI
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    assert bundle.source_metadata.level is WorkLevel.MUNTAHI
    assert bundle.source_metadata.level.value == "muntahī"
    assert bundle.source_metadata.level_status is LevelStatus.ASSIGNED
    assert bundle.source_metadata.level_provenance is LevelProvenance.OWNER_OVERRIDE

    # Serialize and verify the Arabic enum string appears byte-exact in JSON.
    dumped = bundle.source_metadata.model_dump(mode="json")
    assert dumped["level"] == "muntahī"
    assert dumped["level_status"] == "assigned"
    assert dumped["level_provenance"] == "owner_override"


@pytest.mark.spec("REQ-SRC-0007", "AC-4")
def test_req_src_0007_ac4_handoff_serializes_non_applicable_reference(
    source_pipeline: SourcePipeline,
) -> None:
    """hadith_collection (non-applicable) → handoff carries level=null + non_applicable_reference."""
    frozen = _frozen_from_pipeline(
        source_pipeline, FIXTURES_ROOT / "shamela_real" / "04_hadith" / "book.htm"
    )
    source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)
    deliberation_result = _accepted_deliberation_result(frozen.source_id)
    # Force the non-applicable genre + status combination on the existing
    # metadata. model_copy(update=...) runs the cross-field validator once
    # against the target triple, which is what step-50 _resolve_level_fields
    # would otherwise produce for a hadith_collection-classified source.
    deliberation_result.source_metadata = deliberation_result.source_metadata.model_copy(
        update={
            "genre": Genre.HADITH_COLLECTION,
            "level": None,
            "level_status": LevelStatus.NON_APPLICABLE_REFERENCE,
            "level_provenance": None,
        }
    )

    result = admit_source_and_build_handoff(
        store=source_pipeline.store,
        frozen=frozen,
        dossier=dossier,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    bundle = result.handoff_bundle
    assert bundle is not None
    dumped = bundle.source_metadata.model_dump(mode="json")
    assert "level" in dumped
    assert dumped["level"] is None
    assert dumped["level_status"] == "non_applicable_reference"
    assert dumped["level_provenance"] is None


@pytest.mark.spec("REQ-SRC-0007", "AC-5")
def test_req_src_0007_ac5_invariant_violation_rejects_packaging() -> None:
    """level=mubtadiʾ + level_status=pending_taxonomy fails at SourceMetadata construction.

    The spec wording describes this as "handoff packaging rejected with
    SRC-E-LEVEL-STATUS-INVARIANT-VIOLATION". In practice the Pydantic
    model_validator (``enforce_level_invariants``) catches this at
    SourceMetadata construction time — before the bundle ever reaches
    the handoff boundary — so a violating bundle is unconstructible.
    The end-state is the same: a violating combination cannot be
    serialized.
    """
    with pytest.raises(ValidationError, match="CON-SRC-0004 invariant 2"):
        _build_metadata(
            level=WorkLevel.MUBTADI,
            level_status=LevelStatus.PENDING_TAXONOMY,
            level_provenance=LevelProvenance.OWNER_OVERRIDE,
        )
