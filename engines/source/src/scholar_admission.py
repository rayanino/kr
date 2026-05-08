"""REQ-SRC-0043 admission step: register provisional scholars from match-cell INSUFFICIENT_EVIDENCE NEW IDENTITY emissions.

Phase 5 Session 9 (2026-05-08): consumes ``ProvisionalScholarRegistration``
records emitted by ``scholar_match_cell`` during deliberation Step 50
(when ``stage_1_score_breakdown`` is empty → "new identity" interpretation
per Phase 5 amendment 2026-04-30 to REQ-SRC-0043) and creates
``status=provisional`` ``ScholarAuthorityRecord`` entries in the
``library/registries/scholars.json`` registry via the shared
``shared.scholar_authority.src.scholar_authority.register`` API.

Per REQ-SRC-0043 AC-1 postconditions:
  - ``status=provisional``
  - ``authority_level=AuthorityLevel.UNKNOWN``
  - ``source_book_ids=[source_book_id]`` (the triggering source)
  - ``evidence_sources`` populated from the registration's raw evidence list
  - The source's ``case_complexity`` is forced to NOT-fast_track via
    ``partial_fragment_author_identity=True`` (REQ-SRC-0028 Phase 5
    amendment); see ``engines/source/src/deliberation.py:assess_case_complexity``.

File-level read+write atomicity is delegated to the underlying
``register()`` call which uses ``FileLock`` + tempfile + ``os.replace`` +
``.bak`` backup per ``shared/scholar_authority/src/scholar_authority.py:_save_registry``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from engines.source.contracts import (
    AuthorityLevel,
    ProvisionalScholarRegistration,
    ScholarAuthorityRecord,
    ScholarEvidenceSource,
)
from shared.scholar_authority.src.scholar_authority import register


_DEFAULT_REGISTRY_PATH = Path("library/registries/scholars.json")


_KNOWN_EVIDENCE_TYPES: frozenset[str] = frozenset(
    {"metadata_card", "title_page", "colophon", "agent_inference"}
)


def _classify_evidence_type(raw: str) -> str:
    """Classify a raw evidence string into one of the REQ-SRC-0043 evidence_type values.

    Per REQ-SRC-0043 postconditions: evidence_type is one of
    ``metadata_card``, ``title_page``, ``colophon``, or ``agent_inference``.
    Inputs that match a known tag verbatim are preserved; anything else is
    classified as ``agent_inference`` (the fall-back inference category).

    The raw evidence string is preserved byte-faithfully in
    ``raw_evidence`` regardless of classification — Critical Rule 4
    (errors fail loudly; never silently corrupt data) and the project-wide
    Arabic byte-faithful invariant both forbid mutating the source string.
    """
    return raw if raw in _KNOWN_EVIDENCE_TYPES else "agent_inference"


def _build_evidence_sources(
    registration: ProvisionalScholarRegistration,
) -> list[ScholarEvidenceSource]:
    """Build ``ScholarEvidenceSource`` records from the registration's raw evidence list.

    Each entry binds the evidence to the triggering ``source_book_id`` so the
    registry preserves provenance per REQ-SRC-0043 postcondition: "evidence
    sources as an array of objects each containing book_id, evidence_type,
    and the raw evidence string."
    """
    return [
        ScholarEvidenceSource(
            book_id=registration.source_book_id,
            evidence_type=_classify_evidence_type(raw),
            raw_evidence=raw,
        )
        for raw in registration.evidence
    ]


def _build_provisional_record(
    registration: ProvisionalScholarRegistration,
) -> ScholarAuthorityRecord:
    """Build a ``status=provisional`` record from a registration request.

    Per REQ-SRC-0043 AC-1 postconditions: status=provisional,
    authority_level=AuthorityLevel.UNKNOWN, source_book_ids=[source_book_id],
    evidence_sources populated. ``canonical_id`` and ``last_updated`` are
    placeholders here — the underlying ``register()`` overwrites them with
    a sequential ``sch_NNNNN`` id and a UTC ISO 8601 timestamp respectively.
    """
    # Explicit defaults required by `.claude/rules/python-code.md` —
    # pyright cannot infer Pydantic Field(None, ...) defaults at the call
    # site, so every Optional/numeric-default field must be passed
    # explicitly.
    return ScholarAuthorityRecord(
        canonical_id="sch_pending",
        canonical_name_ar=registration.display_name,
        status="provisional",
        display_name=registration.display_name,
        full_name_lineage=registration.full_name_lineage,
        nisba=list(registration.nisba_tokens),
        birth_date_hijri=None,
        birth_date_ce=None,
        death_date_hijri=registration.death_hijri,
        death_date_ce=None,
        era_century_hijri=None,
        primary_science=registration.primary_science,
        authority_level=AuthorityLevel.UNKNOWN,
        source_book_ids=[registration.source_book_id],
        sources_encountered_in=[registration.source_book_id],
        evidence_sources=_build_evidence_sources(registration),
        record_completeness=0.0,
        data_provenance_score=0.0,
        last_updated=datetime.now(timezone.utc).isoformat(),
    )


def register_provisional_scholars(
    registrations: list[ProvisionalScholarRegistration],
    *,
    registry_path: Optional[Path] = None,
) -> list[ScholarAuthorityRecord]:
    """Register status=provisional scholars in scholars.json per REQ-SRC-0043 AC-1.

    For each ``ProvisionalScholarRegistration`` emitted by
    ``scholar_match_cell`` under INSUFFICIENT_EVIDENCE NEW IDENTITY
    routing (Phase 5 amendment 2026-04-30), creates a
    ``status=provisional`` ``ScholarAuthorityRecord`` with auto-assigned
    ``canonical_id``, ``AuthorityLevel.UNKNOWN``, and ``source_book_ids``
    containing the triggering source. Returns the list of newly-created
    records (with their final canonical_ids assigned by ``register()``).

    Empty input returns an empty list and does NOT touch the registry
    file — keeps the existing source-admission path side-effect-free for
    sources that did not trigger a NEW IDENTITY emission.

    File-level read+write atomicity is provided by the underlying
    ``register()`` call (``FileLock`` + tempfile + ``os.replace`` +
    ``.bak`` backup per
    ``shared/scholar_authority/src/scholar_authority.py:_save_registry``).
    Multi-registration atomicity (all-or-nothing across N registrations
    in one source) is NOT guaranteed at this layer; each ``register()``
    call is independently atomic. A crash mid-loop leaves a partial
    state where some registrations succeeded and the rest did not —
    the surviving records are valid scholar entries by themselves
    (``ScholarAuthorityRecord`` invariants apply per-record).
    """
    if not registrations:
        return []
    path = registry_path if registry_path is not None else _DEFAULT_REGISTRY_PATH
    registered: list[ScholarAuthorityRecord] = []
    for request in registrations:
        record = _build_provisional_record(request)
        created = register(record, registry_path=path)
        registered.append(created)
    return registered
