"""REQ-SRC-0043 admission step: register / promote / disambiguate provisional scholars.

Phase 5 Session 9 (2026-05-08): consumes ``ProvisionalScholarRegistration``
records emitted by ``scholar_match_cell`` during deliberation Step 50
(when ``stage_1_score_breakdown`` is empty → "new identity" interpretation
per Phase 5 amendment 2026-04-30 to REQ-SRC-0043) and creates
``status=provisional`` ``ScholarAuthorityRecord`` entries in the
``library/registries/scholars.json`` registry via the shared
``shared.scholar_authority.src.scholar_authority.register`` API.

Phase 5 Session 11 (2026-05-08) extends the consumer to handle the
remaining REQ-SRC-0043 acceptance criteria:

  - **AC-2 promotion** (integration): when a second registration arrives
    whose ``display_name`` and ``death_hijri`` match an existing
    ``status=provisional`` entry AND the combined evidence across the two
    sources satisfies INV-SRC-0013 ≥2-non-name floor, the existing entry
    is promoted to ``status=confirmed``, ``source_book_ids`` is extended
    with the new source, and ``authority_level`` is re-evaluated from
    ``UNKNOWN`` (heuristic: ≥2 non-name corroboration → ``REFERENCE``;
    ≥4 → ``PRIMARY``).
  - **AC-2 floor-not-met fallback**: when ``display_name`` + ``death_hijri``
    match but the combined evidence falls short of the ≥2-non-name floor,
    a separate ``status=provisional`` entry is created with cross-
    disambiguation notes referencing the existing entry. Conservative
    semantics per "library never refuses knowledge" — the second source
    is accepted but NOT silently merged when corroboration is weak.
  - **AC-3 near-collision** (deterministic): when ``display_name`` matches
    an existing entry but ``death_hijri`` differs by >0 years (or one is
    null and the other populated), a separate entry is created with its
    own ``canonical_id``; both entries get ``disambiguation_notes``
    referencing the other. Conservative-by-design: divergent ``death_hijri``
    on a name match is the canonical AC-3 trigger and overrides AC-2.

Per REQ-SRC-0043 AC-1 postconditions (Session 9 baseline, preserved):
  - ``status=provisional``
  - ``authority_level=AuthorityLevel.UNKNOWN``
  - ``source_book_ids=[source_book_id]`` (the triggering source)
  - ``evidence_sources`` populated from the registration's raw evidence list
  - The source's ``case_complexity`` is forced to NOT-fast_track via
    ``partial_fragment_author_identity=True`` (REQ-SRC-0028 Phase 5
    amendment); see ``engines/source/src/deliberation.py:assess_case_complexity``.

INV-SRC-0013 corroboration scope: ``ProvisionalScholarRegistration`` carries
``primary_science`` and ``death_hijri`` (→ ``century_active_hijri``) as the
only two non-name attributes among the 6 INV-SRC-0013-eligible classes
(school_affiliations, attributed_works, region_origin, region_active are
not carried). PSR-only AC-2 promotion therefore tops out at corroboration
count = 2 (REFERENCE tier). PRIMARY-tier promotion via AC-2 alone is
unreachable from PSR; richer corroboration arrives through other admission
paths (owner-supplied corrections, OpenITI imports, scholar-graph enrichment).

File-level read+write atomicity is delegated to the underlying
``register()`` and ``update()`` calls which use ``FileLock`` + tempfile +
``os.replace`` + ``.bak`` backup per
``shared/scholar_authority/src/scholar_authority.py:_save_registry``.
The two-step write in AC-3 disambiguation (register the new entry, then
update the existing entry's disambiguation_notes back-reference) is NOT
atomic across the two calls — each is independently atomic. A crash
between the calls leaves a one-sided disambiguation (forward reference
present, back-reference absent) — recoverable, not data loss.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from engines.source.contracts import (
    AuthorityLevel,
    ProvisionalScholarRegistration,
    ScholarAuthorityRecord,
    ScholarEvidenceSource,
)
from shared.scholar_authority.src.scholar_authority import (
    get_all,
    register,
    update,
)


_DEFAULT_REGISTRY_PATH = Path("library/registries/scholars.json")


_KNOWN_EVIDENCE_TYPES: frozenset[str] = frozenset(
    {"metadata_card", "title_page", "colophon", "agent_inference"}
)


_DISAMBIGUATION_NOTE_DATE_FORMAT = "%Y-%m-%d"


@dataclass(frozen=True)
class ProvisionalRegistrationOutcome:
    """Outcome of ``register_provisional_scholars`` dispatching AC-1/AC-2/AC-3 paths.

    Phase 5 Session 11 (2026-05-08) per REQ-SRC-0043 AC-2 + AC-3.

    Attributes:
      registered: NEW ``ScholarAuthorityRecord`` entries created in this
        admission (``status=provisional``). Includes AC-1 path entries,
        AC-3 disambiguation new entries, AND AC-2 floor-not-met fallback
        entries. Excludes AC-2 promotions (those are existing entries
        whose status changed; see ``promoted``).
      promoted: EXISTING ``ScholarAuthorityRecord`` entries promoted from
        ``status=provisional`` to ``status=confirmed`` in this admission
        (AC-2 happy path). Records returned reflect post-update state
        (``status=confirmed``, extended ``source_book_ids``, re-evaluated
        ``authority_level``).
      near_collision_disambiguations: pairs ``(existing, new_record)``
        where AC-3 (or AC-2 floor-not-met fallback) created a separate
        entry alongside an existing one with cross-references via
        ``disambiguation_notes``. ``existing`` reflects post-update state
        (back-reference applied). ``new_record`` is also present in
        ``registered``; this list provides the typed pairing for the
        admission consumer.
    """

    registered: list[ScholarAuthorityRecord] = field(default_factory=list)
    promoted: list[ScholarAuthorityRecord] = field(default_factory=list)
    near_collision_disambiguations: list[
        tuple[ScholarAuthorityRecord, ScholarAuthorityRecord]
    ] = field(default_factory=list)


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


def _century_from_death_hijri(year: int) -> int:
    """Compute the Hijri century containing year ``year``.

    Convention: century N covers years (N-1)*100 + 1 through N*100 inclusive.
    Year 1 → century 1; year 100 → century 1; year 101 → century 2.
    """
    return ((year - 1) // 100) + 1


def _count_combined_non_name_attributes(
    existing: ScholarAuthorityRecord,
    new_reg: ProvisionalScholarRegistration,
) -> int:
    """Count INV-SRC-0013 corroborating non-name attribute classes shared between sources.

    Per INV-SRC-0013, name-class signals (display_name, full_name_lineage,
    nasab, nisba, kunyah, laqab) are NOT eligible for the ≥2-non-name
    floor — they are the same kind of signal as the input fragment.
    Eligible non-name classes (8 total per the SPEC; 6 implementable;
    2 deferred per shared/scholar_authority/src/threshold_compounding.py):
      - century_active_hijri (derived from death_date_hijri)
      - school_affiliations[science]
      - primary_science
      - attributed_works
      - region_origin
      - region_active
      - secondary_sciences (DEFERRED — no PSR field)
      - teacher_student_link (DEFERRED — no PSR field)

    ``ProvisionalScholarRegistration`` carries only two of the eligible
    classes via non-name fields: death_hijri (→century_active_hijri) and
    primary_science. The other 4 implementable classes are not carried
    by PSR and therefore cannot be corroborated at AC-2 admission time
    via PSR alone. Existing-record fields enriched by other admission
    paths (owner corrections, OpenITI imports, scholar-graph enrichment)
    can grow the corroboration count post-creation; AC-2 then sees the
    enriched existing record.

    Counts a class only when BOTH sources provide a non-empty value AND
    they agree. Disagreement counts as 0 (conservative — disagreement is
    not corroboration).
    """
    count = 0
    # Class: century_active_hijri (derived from death_date_hijri)
    if (
        existing.death_date_hijri is not None
        and new_reg.death_hijri is not None
        and _century_from_death_hijri(existing.death_date_hijri)
        == _century_from_death_hijri(new_reg.death_hijri)
    ):
        count += 1
    # Class: primary_science
    if (
        existing.primary_science is not None
        and new_reg.primary_science is not None
        and existing.primary_science == new_reg.primary_science
    ):
        count += 1
    return count


def _re_evaluate_authority_level_after_promotion(
    corroboration_count: int,
) -> AuthorityLevel:
    """Heuristic re-evaluation of ``authority_level`` upon AC-2 promotion.

    REQ-SRC-0043 AC-2 postcondition: ``authority_level`` is re-evaluated
    from ``UNKNOWN`` upon promotion. Heuristic:
      - ≥4 corroborating non-name attributes → ``PRIMARY``
      - ≥2 corroborating non-name attributes → ``REFERENCE``
      - else → ``UNKNOWN`` (promotion does not fire below 2)

    PSR can contribute at most 2 classes (century + primary_science), so
    PRIMARY-tier promotion via AC-2 alone is currently unreachable; the
    PRIMARY branch remains in place for future sessions where richer
    corroboration arrives through other admission paths.
    """
    if corroboration_count >= 4:
        return AuthorityLevel.PRIMARY
    if corroboration_count >= 2:
        return AuthorityLevel.REFERENCE
    return AuthorityLevel.UNKNOWN


def _format_disambiguation_note(
    other_canonical_id: str,
    *,
    reason: str,
    on_date: Optional[datetime] = None,
) -> str:
    """Format a disambiguation note pointing to ``other_canonical_id``.

    Format: ``[YYYY-MM-DD] Distinct from {other_canonical_id} — {reason}``.
    Multiple notes accumulate via newline-separator append per
    ``_append_disambiguation_note``.
    """
    when = (on_date or datetime.now(timezone.utc)).strftime(
        _DISAMBIGUATION_NOTE_DATE_FORMAT
    )
    return f"[{when}] Distinct from {other_canonical_id} — {reason}"


def _append_disambiguation_note(
    existing_value: Optional[str], new_note: str
) -> str:
    """Append ``new_note`` to ``existing_value`` with newline separator.

    Empty/None ``existing_value`` returns ``new_note`` alone. Existing
    notes are preserved as a multi-line history per Critical Rule 4
    (errors fail loudly; never silently overwrite scholarly metadata).
    """
    if not existing_value:
        return new_note
    return f"{existing_value}\n{new_note}"


def _describe_near_collision_reason(
    existing: ScholarAuthorityRecord,
    new_reg: ProvisionalScholarRegistration,
) -> str:
    """Describe WHY two display_name-matching entries are kept distinct."""
    new_dh = new_reg.death_hijri
    existing_dh = existing.death_date_hijri
    if new_dh is None and existing_dh is not None:
        return (
            f"display_name match but death_hijri null vs populated "
            f"({existing_dh})"
        )
    if new_dh is not None and existing_dh is None:
        return (
            f"display_name match but death_hijri populated ({new_dh}) "
            f"vs null"
        )
    if new_dh is not None and existing_dh is not None:
        diff = abs(new_dh - existing_dh)
        return (
            f"display_name match but death_hijri differs by {diff} years "
            f"({existing_dh} vs {new_dh})"
        )
    # Both None — defensive fallback; _lookup_existing_match would have
    # routed this to exact_provisional, not near_collision.
    return "display_name match but distinct identity asserted by combined evidence"


def _lookup_existing_match(
    registry: dict[str, ScholarAuthorityRecord],
    new_reg: ProvisionalScholarRegistration,
) -> tuple[
    Literal["exact_provisional", "near_collision", "none"],
    Optional[ScholarAuthorityRecord],
]:
    """Find an existing registry entry matching ``new_reg`` by display_name + death_hijri.

    Iterates the registry in deterministic ``canonical_id`` order. When
    multiple entries share ``new_reg.display_name``, prefers an exact
    ``death_hijri`` match (or both-null) for AC-2; otherwise returns the
    smallest-canonical-id match as a near-collision target for AC-3.

    Match types returned:
      - ``"exact_provisional"``: display_name match AND (both
        ``death_hijri`` null OR ``death_hijri`` equal). Caller routes to
        AC-2 (promotion if floor met; floor-not-met fallback otherwise).
      - ``"near_collision"``: display_name match AND death_hijri null/
        populated mismatch OR diff > 0. Caller routes to AC-3 (separate
        entry with cross-disambiguation).
      - ``"none"``: no display_name match. Caller routes to AC-1 (Session
        9 logic — create a new provisional entry).

    Display-name comparison uses ``record.display_name`` if non-None,
    falling back to ``canonical_name_ar``. PSR-created entries have both
    set to the same value per ``_build_provisional_record``; entries
    from other paths may differ.

    "Near-collision" includes the gray zone of 0 < diff ≤ 50 years (which
    REQ-SRC-0043's error_conditions atom doesn't explicitly cover). Per
    Owner Principle 3 (zero-tolerance for attribution errors) and the
    "false-merge is worse than false-duplicate" matching bias, any
    death_hijri divergence on a name match routes to AC-3 — separate
    entries with cross-disambiguation. The owner can later merge via an
    explicit-replay path if the divergence is ruled to be a date-variant
    in sources rather than two distinct scholars.
    """
    matches: list[tuple[str, ScholarAuthorityRecord]] = []
    for cid in sorted(registry.keys()):
        record = registry[cid]
        existing_display = record.display_name or record.canonical_name_ar
        if existing_display == new_reg.display_name:
            matches.append((cid, record))
    if not matches:
        return ("none", None)
    new_dh = new_reg.death_hijri
    for _, record in matches:
        existing_dh = record.death_date_hijri
        if (new_dh is None and existing_dh is None) or (
            new_dh is not None and new_dh == existing_dh
        ):
            return ("exact_provisional", record)
    _, near_collision_record = matches[0]
    return ("near_collision", near_collision_record)


def _promote_provisional_to_confirmed(
    existing: ScholarAuthorityRecord,
    new_reg: ProvisionalScholarRegistration,
    *,
    registry_path: Path,
    corroboration_count: int,
) -> ScholarAuthorityRecord:
    """Promote ``existing`` to ``status=confirmed``; merge ``new_reg`` evidence.

    Per REQ-SRC-0043 AC-2 postcondition: ``source_book_ids`` is extended
    with the new source; ``authority_level`` is re-evaluated from
    ``UNKNOWN``. Combined evidence has been pre-validated to satisfy
    INV-SRC-0013 ≥2-non-name floor by ``_count_combined_non_name_attributes``
    returning ≥2.

    Idempotency: if ``existing.status == "confirmed"`` already, the call
    still succeeds; the underlying ``update()`` deduplicates list-field
    merges (source_book_ids, evidence_sources) so re-applying the same
    registration is a no-op on those fields. ``status="confirmed"`` is
    a no-op assignment when already confirmed.

    Multi-write atomicity: the ``update()`` call uses ``FileLock`` to
    serialize against concurrent registry writers. Within the call,
    register reload + field merge + write are atomic.
    """
    new_authority_level = _re_evaluate_authority_level_after_promotion(
        corroboration_count
    )
    updates: dict[str, object] = {
        "status": "confirmed",
        "source_book_ids": [new_reg.source_book_id],
        "evidence_sources": _build_evidence_sources(new_reg),
        "authority_level": new_authority_level,
    }
    result = update(
        existing.canonical_id,
        updates,
        source_id=new_reg.source_book_id,
        requesting_engine="source",
        registry_path=registry_path,
    )
    if not result.applied:
        # update() returns applied=False only on BLOCKED conflicts
        # (canonical_name change or self-reference). Neither applies to
        # AC-2 promotion; if this fires, the registry state diverged from
        # the snapshot we read. Per Critical Rule 4, fail loud.
        raise RuntimeError(
            f"AC-2 promotion update for {existing.canonical_id} blocked "
            f"by unexpected conflicts: "
            f"{[c.detail for c in result.conflicts]}"
        )
    return result.record


def _register_with_near_collision_disambiguation(
    existing: ScholarAuthorityRecord,
    new_reg: ProvisionalScholarRegistration,
    *,
    registry_path: Path,
    reason: str,
) -> tuple[ScholarAuthorityRecord, ScholarAuthorityRecord]:
    """Create a NEW provisional entry alongside ``existing`` with cross-disambiguation.

    Per REQ-SRC-0043 AC-3 postcondition (and AC-2 floor-not-met fallback):
    creates a separate entry with its own ``canonical_id``; both entries
    receive ``disambiguation_notes`` referencing the other.

    Returns ``(existing_post_update, new_record)``. ``existing_post_update``
    reflects the back-reference applied by the secondary ``update()``
    call; ``new_record`` carries the forward reference set on its
    initial ``register()``.

    The two writes (register + update) are NOT atomic across each other
    — each is independently atomic via ``shared.scholar_authority``'s
    ``FileLock``. A crash between them leaves a one-sided disambiguation
    (forward reference present on the new entry; back-reference absent
    on the existing entry). The forward reference is sufficient to
    later detect and repair the back-reference; the failure mode is a
    one-sided disambiguation, not data loss.
    """
    new_record = _build_provisional_record(new_reg)
    forward_note = _format_disambiguation_note(
        existing.canonical_id, reason=reason
    )
    new_record.disambiguation_notes = forward_note
    created = register(new_record, registry_path=registry_path)
    backward_note = _format_disambiguation_note(
        created.canonical_id, reason=reason
    )
    appended = _append_disambiguation_note(
        existing.disambiguation_notes, backward_note
    )
    result = update(
        existing.canonical_id,
        {"disambiguation_notes": appended},
        source_id=new_reg.source_book_id,
        requesting_engine="source",
        registry_path=registry_path,
    )
    if not result.applied:
        raise RuntimeError(
            f"AC-3 disambiguation back-reference update for "
            f"{existing.canonical_id} blocked by unexpected conflicts: "
            f"{[c.detail for c in result.conflicts]}"
        )
    return (result.record, created)


def register_provisional_scholars(
    registrations: list[ProvisionalScholarRegistration],
    *,
    registry_path: Optional[Path] = None,
) -> ProvisionalRegistrationOutcome:
    """Register / promote / disambiguate scholars per REQ-SRC-0043 AC-1/AC-2/AC-3.

    Phase 5 Session 11 (2026-05-08) extends the Session 9 AC-1-only
    consumer to dispatch each registration through the lookup →
    match-type → action chain:

      - **AC-1 (no match)**: create a new ``status=provisional`` entry —
        Session 9 logic, preserved unchanged.
      - **AC-2 (exact match, ≥2-non-name floor met)**: promote the
        existing entry from ``status=provisional`` to ``status=confirmed``;
        extend ``source_book_ids``; re-evaluate ``authority_level``.
      - **AC-2 fallback (exact match, floor not met)**: create a separate
        ``status=provisional`` entry with cross-disambiguation. Conservative
        per "library never refuses knowledge" — the new source is
        accepted but NOT merged into a weakly-corroborated existing entry.
      - **AC-3 (near collision: display_name match + death_hijri
        divergence > 0 OR null/populated mismatch)**: create a separate
        ``status=provisional`` entry with cross-disambiguation referencing
        the existing entry. AC-3 takes priority over AC-2 because
        divergent ``death_hijri`` defeats the AC-2 precondition.

    Returns a ``ProvisionalRegistrationOutcome`` with three lists. Empty
    input returns an empty outcome and does NOT touch the registry file
    — keeps the source-admission path side-effect-free for sources that
    did not trigger a NEW IDENTITY emission.

    File-level read+write atomicity is provided by the underlying
    ``register()`` and ``update()`` calls (each takes a ``FileLock`` per
    ``shared/scholar_authority/src/scholar_authority.py:_save_registry``).
    Multi-registration atomicity (all-or-nothing across N registrations
    in one source) is NOT guaranteed at this layer. A crash mid-batch
    leaves a partial state where some registrations succeeded and the
    rest did not — the surviving records are valid scholar entries by
    themselves (``ScholarAuthorityRecord`` invariants apply per-record).
    """
    if not registrations:
        return ProvisionalRegistrationOutcome()
    path = registry_path if registry_path is not None else _DEFAULT_REGISTRY_PATH
    registered: list[ScholarAuthorityRecord] = []
    promoted: list[ScholarAuthorityRecord] = []
    near_collisions: list[
        tuple[ScholarAuthorityRecord, ScholarAuthorityRecord]
    ] = []
    for reg in registrations:
        # Reload the registry on every iteration so prior in-batch
        # operations are visible (e.g., a second registration matching
        # a just-created entry from the same batch).
        registry = get_all(registry_path=path)
        match_type, existing = _lookup_existing_match(registry, reg)
        if match_type == "exact_provisional" and existing is not None:
            count = _count_combined_non_name_attributes(existing, reg)
            if count >= 2:
                # AC-2 happy path — promote
                updated = _promote_provisional_to_confirmed(
                    existing,
                    reg,
                    registry_path=path,
                    corroboration_count=count,
                )
                promoted.append(updated)
            else:
                # AC-2 floor not met — conservative fallback per
                # "library never refuses knowledge"
                reason = (
                    f"display_name match but combined evidence below "
                    f"≥2-non-name floor ({count} corroborating "
                    f"attribute{'s' if count != 1 else ''})"
                )
                existing_post, new_record = (
                    _register_with_near_collision_disambiguation(
                        existing,
                        reg,
                        registry_path=path,
                        reason=reason,
                    )
                )
                registered.append(new_record)
                near_collisions.append((existing_post, new_record))
        elif match_type == "near_collision" and existing is not None:
            # AC-3 path
            reason = _describe_near_collision_reason(existing, reg)
            existing_post, new_record = (
                _register_with_near_collision_disambiguation(
                    existing,
                    reg,
                    registry_path=path,
                    reason=reason,
                )
            )
            registered.append(new_record)
            near_collisions.append((existing_post, new_record))
        else:
            # AC-1 path — no match, create new provisional
            new_record = _build_provisional_record(reg)
            created = register(new_record, registry_path=path)
            registered.append(created)
    return ProvisionalRegistrationOutcome(
        registered=registered,
        promoted=promoted,
        near_collision_disambiguations=near_collisions,
    )
