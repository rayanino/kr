"""Phase 5b follow-up 24 (2026-04-28) — constituent-level placeholder surface.

Closes INV-SRC-0012 AC-3/AC-4 promise ("constituent-rasāʾil leveling tracked
as Phase 5b item 24") via the (a-lite) hybrid-resolution path:

- Extend ``SubWorkInventoryEntry`` with optional level / level_status /
  level_provenance placeholder fields (defaults: None / PENDING_SYNTHESIS / None)
- Enforce per-constituent IFF pair-consistency (mirrors SourceMetadata
  invariants 1-2)
- Propagate ``IntakeDossier.sub_work_inventory`` onto ``SourceMetadata``
  via ``_populate_deterministic_metadata`` so the constituent surface
  flows through the source→normalization handoff via the existing
  dispatcher ``model_copy(deep=True)`` (D-023)
- Container Axis 2 firing on ``composite_work_type=="majmu"`` remains
  unchanged (regression guard)

Owner-override-entrance widening to per-constituent keying is OUT OF
SCOPE for FU-24 (tracked as Phase 5b item 37). The (a-lite) closure
bounds FU-24 to the boundary widening; FU-37 carries the
REQ-SRC-0047/REQ-SRC-0048 entrance and PendingLevelOverride keyspace
expansion, plus the arabic-reviewer Agent retroactive validation that
failed this session due to Anthropic billing quota.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engines.source.contracts import (
    LevelProvenance,
    LevelStatus,
    SubWorkInventoryEntry,
    WorkLevel,
)


# ---------------------------------------------------------------------------
# SubWorkInventoryEntry pair-consistency: positive cases
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0038", "AC-FU24-1")
@pytest.mark.parametrize(
    ("level", "level_status", "level_provenance"),
    [
        # Default placeholder triple at intake (source engine never writes level)
        (None, LevelStatus.PENDING_SYNTHESIS, None),
        # Synthesis-written ASSIGNED state (each provenance source)
        (WorkLevel.MUBTADI, LevelStatus.ASSIGNED, LevelProvenance.SYNTHESIS_ENGINE),
        (WorkLevel.MUTAWASSIT, LevelStatus.ASSIGNED, LevelProvenance.SYNTHESIS_ENGINE),
        (WorkLevel.MUNTAHI, LevelStatus.ASSIGNED, LevelProvenance.SYNTHESIS_ENGINE),
        (WorkLevel.MUNTAHI, LevelStatus.ASSIGNED, LevelProvenance.OWNER_OVERRIDE),
        # Synthesis post-attempt non-applicable / unprocessable states
        (None, LevelStatus.NON_APPLICABLE_REFERENCE, None),
        (None, LevelStatus.UNPROCESSABLE_ERROR, None),
    ],
)
def test_sub_work_inventory_entry_accepts_pair_consistent_states(
    level: WorkLevel | None,
    level_status: LevelStatus,
    level_provenance: LevelProvenance | None,
) -> None:
    """Pair-consistent SubWorkInventoryEntry constructions succeed."""
    entry = SubWorkInventoryEntry(
        sub_title="رسالة في فضل علم السلف",
        volume_number=1,
        page_start=10,
        page_end=42,
        detection_method="toc_entry",
        level=level,
        level_status=level_status,
        level_provenance=level_provenance,
    )
    assert entry.level == level
    assert entry.level_status == level_status
    assert entry.level_provenance == level_provenance


@pytest.mark.spec("REQ-SRC-0038", "AC-FU24-2")
def test_sub_work_inventory_entry_default_placeholder_triple() -> None:
    """Bare SubWorkInventoryEntry construction yields the placeholder triple.

    The source engine emits each detected constituent with the default
    ``(level=None, level_status=PENDING_SYNTHESIS, level_provenance=None)``;
    synthesis writes authoritative level later per DEC-SRC-0003.
    """
    entry = SubWorkInventoryEntry(
        sub_title="جامع العلوم والحكم",
        volume_number=None,
        page_start=None,
        page_end=None,
        detection_method="toc_entry",
    )
    assert entry.level is None
    assert entry.level_status == LevelStatus.PENDING_SYNTHESIS
    assert entry.level_provenance is None


# ---------------------------------------------------------------------------
# SubWorkInventoryEntry pair-consistency: negative cases
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0038", "AC-FU24-3")
@pytest.mark.parametrize(
    ("level", "level_status", "level_provenance", "expected_fragment"),
    [
        # ASSIGNED without level
        (
            None,
            LevelStatus.ASSIGNED,
            LevelProvenance.SYNTHESIS_ENGINE,
            "level_status='assigned' requires level to be non-null",
        ),
        # ASSIGNED without level_provenance
        (
            WorkLevel.MUNTAHI,
            LevelStatus.ASSIGNED,
            None,
            "level_status='assigned' requires level_provenance to be non-null",
        ),
        # PENDING_SYNTHESIS with non-null level
        (
            WorkLevel.MUBTADI,
            LevelStatus.PENDING_SYNTHESIS,
            None,
            "requires level to be null",
        ),
        # NON_APPLICABLE_REFERENCE with non-null level
        (
            WorkLevel.MUTAWASSIT,
            LevelStatus.NON_APPLICABLE_REFERENCE,
            None,
            "requires level to be null",
        ),
        # PENDING_SYNTHESIS with non-null level_provenance
        (
            None,
            LevelStatus.PENDING_SYNTHESIS,
            LevelProvenance.OWNER_OVERRIDE,
            "requires level_provenance to be null",
        ),
    ],
)
def test_sub_work_inventory_entry_rejects_pair_inconsistent_states(
    level: WorkLevel | None,
    level_status: LevelStatus,
    level_provenance: LevelProvenance | None,
    expected_fragment: str,
) -> None:
    """Pair-inconsistent SubWorkInventoryEntry constructions raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        SubWorkInventoryEntry(
            sub_title="رسالة",
            volume_number=None,
            page_start=None,
            page_end=None,
            detection_method="toc_entry",
            level=level,
            level_status=level_status,
            level_provenance=level_provenance,
        )
    assert expected_fragment in str(exc_info.value), (
        f"expected error message to contain {expected_fragment!r}, "
        f"got {exc_info.value!s}"
    )


# ---------------------------------------------------------------------------
# Propagation through deliberation → SourceMetadata
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0038", "AC-FU24-4")
def test_sub_work_inventory_propagates_from_dossier_to_source_metadata() -> None:
    """``_populate_deterministic_metadata`` copies ``dossier.sub_work_inventory``
    onto SourceMetadata so the constituent placeholder surface flows forward
    via the existing dispatcher ``model_copy(deep=True)`` (D-023).

    The (a-lite) closure relies on this propagation step — without it, the
    constituent inventory dies at the IntakeDossier→SourceMetadata boundary
    that the main-thread DIM-AR2 structural cross-provider check identified
    as the load-bearing FU-24 propagation gap.
    """
    from engines.source.contracts import (
        CompletenessStatus,
        IntakeDossier,
        IntegrityStatus,
        SourceFormat,
        SourceMetadata,
        StructuralFormat,
        TextFidelity,
        TrustTier,
    )
    from engines.source.src.deliberation import _populate_deterministic_metadata

    constituents = [
        SubWorkInventoryEntry(
            sub_title="رسالة في فضل علم السلف",
            volume_number=1,
            page_start=10,
            page_end=42,
            detection_method="toc_entry",
        ),
        SubWorkInventoryEntry(
            sub_title="جامع العلوم والحكم — مقتطفات",
            volume_number=1,
            page_start=43,
            page_end=120,
            detection_method="toc_entry",
        ),
    ]
    dossier = IntakeDossier(
        dossier_id="dossier_majmu_ibn_rajab",
        source_id="src_majmu_ibn_rajab",
        source_format=SourceFormat.SHAMELA_HTML,
        completeness_status=CompletenessStatus.COMPLETE,
        integrity_status=IntegrityStatus.SOUND,
        composite_work_type="majmu",
        sub_work_inventory=constituents,
    )
    metadata = SourceMetadata(
        source_id="src_majmu_ibn_rajab",
        title_arabic="مجموع رسائل ابن رجب",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_majmu_ibn_rajab/frozen",
        frozen_hash="b" * 64,
        frozen_file_hashes={"book.htm": "b" * 64},
        status="source_engine_accepted",
        composite_work_type="majmu",
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        # Container Axis 2 firing requires NON_APPLICABLE_REFERENCE here
        # (composite_work_type=="majmu" → INV-SRC-0012 Axis 2)
        level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
    )

    # Act: deterministic enrichment populates sub_work_inventory from dossier
    _populate_deterministic_metadata(metadata, dossier)

    # Assert: constituent surface lives on SourceMetadata for cross-engine
    # propagation via NormalizationHandoffBundle.source_metadata
    assert len(metadata.sub_work_inventory) == 2
    assert metadata.sub_work_inventory[0].sub_title == "رسالة في فضل علم السلف"
    assert metadata.sub_work_inventory[0].level is None
    assert metadata.sub_work_inventory[0].level_status == LevelStatus.PENDING_SYNTHESIS
    assert metadata.sub_work_inventory[0].level_provenance is None
    assert metadata.sub_work_inventory[1].sub_title == "جامع العلوم والحكم — مقتطفات"
    # Container Axis 2 unchanged: composite_work_type=="majmu" still fires
    assert metadata.composite_work_type == "majmu"
    assert metadata.level_status == LevelStatus.NON_APPLICABLE_REFERENCE


@pytest.mark.spec("REQ-SRC-0038", "AC-FU24-5")
def test_sub_work_inventory_propagates_empty_when_dossier_empty() -> None:
    """Non-majmu dossier (no constituents) yields empty sub_work_inventory.

    Regression guard: the propagation must not invent constituents for
    non-composite sources.
    """
    from engines.source.contracts import (
        CompletenessStatus,
        IntakeDossier,
        IntegrityStatus,
        SourceFormat,
        SourceMetadata,
        StructuralFormat,
        TextFidelity,
        TrustTier,
    )
    from engines.source.src.deliberation import _populate_deterministic_metadata

    dossier = IntakeDossier(
        dossier_id="dossier_standalone",
        source_id="src_standalone",
        source_format=SourceFormat.SHAMELA_HTML,
        completeness_status=CompletenessStatus.COMPLETE,
        integrity_status=IntegrityStatus.SOUND,
    )
    metadata = SourceMetadata(
        source_id="src_standalone",
        title_arabic="كتاب التوحيد",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_standalone/frozen",
        frozen_hash="c" * 64,
        frozen_file_hashes={"book.htm": "c" * 64},
        status="source_engine_accepted",
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        level_status=LevelStatus.PENDING_SYNTHESIS,
    )

    _populate_deterministic_metadata(metadata, dossier)

    assert metadata.sub_work_inventory == []


# ---------------------------------------------------------------------------
# Cross-engine D-023 propagation: dispatcher pass-through regression
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0007", "AC-FU24-6")
def test_normalization_dispatcher_preserves_sub_work_inventory() -> None:
    """``engines/normalization/src/dispatcher.py:74`` ``model_copy(deep=True)``
    preserves SourceMetadata.sub_work_inventory.

    Codex CRIT-1 latent gap: ``normalize_handoff_bundle`` clones only
    ``bundle.source_metadata``, discarding all other bundle fields. By
    carrying ``sub_work_inventory`` on ``SourceMetadata`` (NOT on
    ``NormalizationHandoffBundle`` directly), the constituent surface
    rides through the dispatcher hop for free. This regression guard
    locks that architectural choice — moving ``sub_work_inventory`` off
    ``SourceMetadata`` would require widening the dispatcher in tandem.
    """
    from engines.source.contracts import SourceFormat, SourceMetadata, StructuralFormat

    metadata = SourceMetadata(
        source_id="src_majmu_test",
        title_arabic="مجموع رسائل اختبار",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_majmu_test/frozen",
        frozen_hash="d" * 64,
        frozen_file_hashes={"book.htm": "d" * 64},
        status="source_engine_accepted",
        composite_work_type="majmu",
        level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
        sub_work_inventory=[
            SubWorkInventoryEntry(
                sub_title="رسالة الأولى",
                volume_number=None,
                page_start=None,
                page_end=None,
                detection_method="toc_entry",
            ),
            SubWorkInventoryEntry(
                sub_title="رسالة الثانية",
                volume_number=None,
                page_start=None,
                page_end=None,
                detection_method="toc_entry",
            ),
        ],
    )

    # Mirror dispatcher.py:74 behaviour
    cloned = metadata.model_copy(deep=True)

    assert len(cloned.sub_work_inventory) == 2
    assert cloned.sub_work_inventory[0].sub_title == "رسالة الأولى"
    assert cloned.sub_work_inventory[0].level_status == LevelStatus.PENDING_SYNTHESIS
    assert cloned.sub_work_inventory[1].sub_title == "رسالة الثانية"
    # Deep-copy isolates the inventory list
    cloned.sub_work_inventory[0].sub_title = "modified"
    assert metadata.sub_work_inventory[0].sub_title == "رسالة الأولى"


# ---------------------------------------------------------------------------
# DEC-SRC-0021 rule (vii) — legacy migration coverage
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-vii-c")
def test_dec_src_0021_vii_c_legacy_majmu_empty_inventory_is_ambiguous() -> None:
    """Legacy ``composite_work_type=="majmu"`` with no inventory carrier:
    sub_work_inventory defaults to [], audit-logged with ambiguous_fields,
    NO human_gate routing (system functions without inventory; re-intake
    recovers).

    Codex CRIT-3 closure: pre-FU-24 SourceMetadata schema had no
    sub_work_inventory field, so legacy majmu records lack the carrier.
    Empty default is LOSSY but documented; the audit trail's
    ambiguous_fields entry is the persistent record so re-intake can
    resurface the original IntakeDossier inventory.
    """
    from engines.source.src.migration import migrate_source_metadata_payload

    payload = {
        "source_id": "src_legacy_majmu_no_inventory",
        "title_arabic": "مجموع فتاوى ابن تيمية",
        "composite_work_type": "majmu",
        # level_status / level_provenance / sub_work_inventory all missing —
        # pre-FU-24 schema state
    }

    migrated = migrate_source_metadata_payload(payload)

    # Defaults applied
    assert migrated["sub_work_inventory"] == []
    # Audit event present with ambiguous flag for the lossy default
    events = migrated["legacy_migration_events"]
    assert isinstance(events, list)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, dict)
    assert "sub_work_inventory" in event["fields_defaulted"]
    assert event["ambiguous_fields"] == ["sub_work_inventory"]
    # Lossy default is NOT human_gate routed — the system functions without
    # the inventory; re-intake recovers it
    assert event["human_gate_routed"] is False
    assert event["human_gate_checkpoint_id"] is None


@pytest.mark.spec("DEC-SRC-0021", "OPT-B-vii-a")
def test_dec_src_0021_vii_a_legacy_non_majmu_empty_inventory_unambiguous() -> None:
    """Legacy non-majmu records also default sub_work_inventory to [], but
    without the ambiguous_fields flag (non-composite sources have no
    constituent inventory by design — the empty default is correct).
    """
    from engines.source.src.migration import migrate_source_metadata_payload

    payload = {
        "source_id": "src_legacy_standalone",
        "title_arabic": "كتاب التوحيد",
        "composite_work_type": None,
        # sub_work_inventory missing
    }

    migrated = migrate_source_metadata_payload(payload)

    assert migrated["sub_work_inventory"] == []
    events = migrated["legacy_migration_events"]
    assert isinstance(events, list)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, dict)
    assert "sub_work_inventory" in event["fields_defaulted"]
    # Non-majmu: empty inventory is correct, NOT ambiguous
    assert event["ambiguous_fields"] == []


# ---------------------------------------------------------------------------
# INV-SRC-0012 container Axis 2 regression: firing unchanged
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0012", "AC-FU24-7")
def test_inv_src_0012_axis_2_fires_unchanged_when_sub_work_inventory_present() -> None:
    """Container-level Axis 2 firing on ``composite_work_type=="majmu"``
    remains unchanged when ``sub_work_inventory`` is populated.

    The constituent placeholder surface is independent of the container's
    non-applicability gate. This regression guard ensures FU-24 did not
    accidentally couple the container Axis 2 logic to the new constituent
    surface.
    """
    from engines.source.contracts import SourceFormat, SourceMetadata, StructuralFormat

    metadata = SourceMetadata(
        source_id="src_majmu_axis_2_regression",
        title_arabic="مجموع رسائل",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        intake_timestamp="2026-04-28T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_majmu_axis_2_regression/frozen",
        frozen_hash="e" * 64,
        frozen_file_hashes={"book.htm": "e" * 64},
        status="source_engine_accepted",
        composite_work_type="majmu",
        level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
        sub_work_inventory=[
            SubWorkInventoryEntry(
                sub_title="رسالة الأولى",
                volume_number=None,
                page_start=None,
                page_end=None,
                detection_method="toc_entry",
            ),
        ],
    )
    # Construction succeeds → invariant 3 (Axis 2) fires correctly
    assert metadata.composite_work_type == "majmu"
    assert metadata.level_status == LevelStatus.NON_APPLICABLE_REFERENCE
    assert metadata.level is None
    assert metadata.level_provenance is None
    assert len(metadata.sub_work_inventory) == 1
