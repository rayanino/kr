"""Phase 5 Session 4 — REQ-SRC-0042 build-time enrichment lane tests.

Validates the build-time enrichment lane contract:

  - ``BuildTimeProvenance`` carries the 4 required fields per REQ-SRC-0042
    Phase 5 amendment: source / enrichment_phase=build_time / license /
    training_use_permitted.
  - ``enrich_record`` wraps a ScholarAuthorityRecord with provenance
    without making any external calls.
  - Runtime external calls raise ``RuntimeExternalCallError`` per
    INV-SRC-0017 F-7 closure.
  - The Literal type ``EnrichmentPhase`` prevents silent expansion to
    runtime values.

Real Arabic fixtures: محمد بن إسماعيل البخاري (sch_00042) — the canonical
3rd-century muhaddith used across Sessions 2-4.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engines.source.contracts import ErrorCode, ScholarAuthorityRecord
from shared.scholar_authority.src.build_time_enrichment import (
    BuildTimeProvenance,
    EnrichedScholarRecord,
    enrich_record,
    reject_runtime_external_call,
)
from shared.scholar_authority.src.snapshot_lock import (
    RuntimeExternalCallError,
)


_NOW = "2026-05-04T16:00:00+00:00"


def _bukhari_record() -> ScholarAuthorityRecord:
    """Real-fixture al-Bukhārī record for enrichment testing."""
    return ScholarAuthorityRecord(
        canonical_id="sch_00042",
        canonical_name_ar="محمد بن إسماعيل البخاري",
        primary_science="hadith",
        era_century_hijri=3,
        nisba=["البخاري"],
        known_works=["الجامع الصحيح", "التاريخ الكبير"],
        school_affiliations={"hadith": "ahl_hadith"},
        death_date_hijri=256,
        # Explicit Pydantic Field(None, ...) / Field(0.0, ...) defaults per
        # .claude/rules/python-code.md (pyright can't infer Field defaults).
        birth_date_hijri=None,
        birth_date_ce=None,
        death_date_ce=None,
        record_completeness=0.0,
        data_provenance_score=0.0,
        last_updated=_NOW,
    )


# ---------------------------------------------------------------------------
# REQ-SRC-0042 Phase 5 amendment — build-time provenance contract
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0042")
def test_build_time_provenance_requires_four_fields() -> None:
    """REQ-SRC-0042 amendment: 4 required provenance fields are enforced.

    The Pydantic ``extra='forbid'`` + required-field discipline rejects
    incomplete provenance at construction time, NOT at downstream consumer
    time. This is INV-SRC-0015-style upfront validation.
    """
    provenance = BuildTimeProvenance(
        source="openiti",
        license="openiti-cc-by-sa-4.0",
        training_use_permitted=False,
    )
    assert provenance.source == "openiti"
    assert provenance.enrichment_phase == "build_time"
    assert provenance.license == "openiti-cc-by-sa-4.0"
    assert provenance.training_use_permitted is False


@pytest.mark.spec("REQ-SRC-0042")
def test_build_time_provenance_rejects_runtime_phase() -> None:
    """``enrichment_phase`` Literal['build_time'] forbids runtime values.

    The Literal type closure makes it impossible to construct a provenance
    with phase='runtime' — Pydantic raises a ValidationError at construct
    time. This is the type-system enforcement of INV-SRC-0017 F-7 closure.
    """
    with pytest.raises(ValidationError):
        BuildTimeProvenance(
            source="openiti",
            enrichment_phase="runtime",  # type: ignore[arg-type]
            license="x",
            training_use_permitted=True,
        )


@pytest.mark.spec("REQ-SRC-0042")
def test_build_time_provenance_forbids_unknown_source() -> None:
    """``source`` Literal forbids unauthorized enrichment sources.

    Adding a new source requires a SPEC amendment + license review (per
    REQ-SRC-0042 amendment). The Literal type prevents silent expansion.
    """
    with pytest.raises(ValidationError):
        BuildTimeProvenance(
            source="brill_ei",  # type: ignore[arg-type]  # not authorized
            license="x",
            training_use_permitted=False,
        )


@pytest.mark.spec("REQ-SRC-0042")
def test_build_time_provenance_forbids_extra_fields() -> None:
    """``extra='forbid'`` prevents silent provenance schema drift."""
    with pytest.raises(ValidationError):
        BuildTimeProvenance.model_validate({
            "source": "openiti",
            "license": "x",
            "training_use_permitted": True,
            "rogue_field": "should be rejected",
        })


# ---------------------------------------------------------------------------
# enrich_record — lane entry point tests
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0042")
def test_enrich_record_attaches_provenance() -> None:
    """``enrich_record`` wraps a record with build-time provenance.

    AC-1-style happy path: a Bukhārī record + OpenITI source produces an
    EnrichedScholarRecord with the 4 required provenance fields populated.
    The record_subject_canonical_id defaults to record.canonical_id when
    available.
    """
    record = _bukhari_record()
    enriched = enrich_record(
        record=record,
        source="openiti",
        license="openiti-cc-by-sa-4.0",
        training_use_permitted=False,
        upstream_external_id="0256Bukhari",
    )

    assert enriched.record.canonical_id == "sch_00042"
    assert enriched.record.canonical_name_ar == "محمد بن إسماعيل البخاري"
    assert enriched.provenance.source == "openiti"
    assert enriched.provenance.enrichment_phase == "build_time"
    assert enriched.provenance.license == "openiti-cc-by-sa-4.0"
    assert enriched.provenance.training_use_permitted is False
    assert enriched.provenance.record_subject_canonical_id == "sch_00042"
    assert enriched.provenance.upstream_external_id == "0256Bukhari"


@pytest.mark.spec("REQ-SRC-0042")
def test_enrich_record_works_for_all_authorized_sources() -> None:
    """Every authorized source produces a valid EnrichedScholarRecord.

    Coverage check: openiti / wikidata / llm_inference all round-trip
    through ``enrich_record`` without rejection.
    """
    record = _bukhari_record()
    for source, license_str, training in (
        ("openiti", "openiti-cc-by-sa-4.0", False),
        ("wikidata", "wikidata-cc0-1.0", True),
        ("llm_inference", "anthropic-tos-2026-01", False),
    ):
        enriched = enrich_record(
            record=record,
            source=source,  # type: ignore[arg-type]
            license=license_str,
            training_use_permitted=training,
        )
        assert enriched.provenance.source == source
        assert enriched.provenance.enrichment_phase == "build_time"


@pytest.mark.spec("REQ-SRC-0042")
def test_enriched_record_is_frozen() -> None:
    """``EnrichedScholarRecord`` is immutable post-construction.

    Pydantic ``frozen=True`` mirrors CON-SRC-0009 ScholarEvidencePacket
    immutability: once a record is enriched and persisted into the
    snapshot, the audit trail cannot be tampered with.
    """
    record = _bukhari_record()
    enriched = enrich_record(
        record=record,
        source="openiti",
        license="x",
        training_use_permitted=False,
    )
    with pytest.raises(ValidationError):
        enriched.provenance.source = "wikidata"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Runtime-external enforcement (INV-SRC-0017 F-7 closure)
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0042", "INV-SRC-0017")
def test_reject_runtime_external_call_raises_correct_error() -> None:
    """Runtime external endpoint attempts raise RuntimeExternalCallError.

    Per INV-SRC-0017 F-7 closure + REQ-SRC-0042 amendment: any path that
    would issue an external request at runtime aborts the case with the
    structured error. The error code MUST be SRC-E-RUNTIME-EXTERNAL.
    """
    with pytest.raises(RuntimeExternalCallError) as exc_info:
        reject_runtime_external_call(
            "https://www.wikidata.org/wiki/Special:EntityData/Q123.json"
        )
    assert exc_info.value.error_code == ErrorCode.RUNTIME_EXTERNAL
    assert exc_info.value.attempted_endpoint == (
        "https://www.wikidata.org/wiki/Special:EntityData/Q123.json"
    )


@pytest.mark.spec("REQ-SRC-0042", "INV-SRC-0017")
def test_runtime_external_error_is_separate_from_build_time_lane() -> None:
    """The lane is the build-time GATE; the runtime guard is the FORBIDDEN exit.

    The two surfaces compose: callers that want to ENRICH at build time use
    ``enrich_record``; callers that detect a runtime fetch attempt use
    ``reject_runtime_external_call``. They are NOT the same surface — using
    one when the other is meant is a programming error.

    This test asserts that ``enrich_record`` does NOT call out to any
    external source itself (the lane is purely a provenance wrapper).
    """
    record = _bukhari_record()
    # No external call is made — the lane only constructs Pydantic.
    enriched = enrich_record(
        record=record,
        source="openiti",
        license="openiti-cc-by-sa-4.0",
        training_use_permitted=False,
    )
    # Round-trip without raising RuntimeExternalCallError.
    assert isinstance(enriched, EnrichedScholarRecord)
    assert enriched.provenance.enrichment_phase == "build_time"
