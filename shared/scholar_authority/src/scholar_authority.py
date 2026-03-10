"""Scholar Authority Registry — SPEC §4.A.5

Stores every scholar encountered in the library. Provides identity matching
(is this the same person?), record creation with sequential IDs, progressive
enrichment, and 5 consistency checks on updates.

Storage: library/registries/scholars.json
Locking: filelock on library/registries/scholars.json.lock
ID format: sch_{5_digit_sequence} — monotonically increasing.

The source engine creates records; other engines enrich them via update().
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from filelock import FileLock

from engines.source.contracts import MetadataHistoryEntry, ScholarAuthorityRecord
from shared.scholar_authority.src.name_matching import normalized_name_similarity


@dataclass
class ScholarMatchResult:
    """Result of looking up a scholar in the registry.

    SPEC §4.A.5 scoring thresholds:
    - match_score >= 0.85 → action = "auto_link"
    - 0.50 <= match_score < 0.85 → action = "human_gate"
    - match_score < 0.50 → action = "new_record"
    """
    found: bool
    record: Optional[ScholarAuthorityRecord]
    match_score: float
    match_detail: str
    action: str  # "auto_link" | "human_gate" | "new_record"


@dataclass
class ScholarUpdateConflict:
    """A consistency check conflict detected during update."""
    check_name: str
    severity: str  # "gate" | "blocked"
    field: str
    detail: str
    error_code: str


@dataclass
class ScholarUpdateResult:
    """Result of updating a scholar record."""
    record: ScholarAuthorityRecord
    applied: bool
    conflicts: list[ScholarUpdateConflict] = field(default_factory=list)


# The 24 biographical fields for record_completeness.
_BIOGRAPHICAL_FIELDS: list[str] = [
    "canonical_name_ar", "known_as", "name_variants", "kunya", "laqab",
    "nisba", "birth_date_hijri", "birth_date_ce", "death_date_hijri",
    "death_date_ce", "death_date_approximate", "era_century_hijri",
    "geographic_origin", "geographic_active", "school_affiliations",
    "sectarian_tradition", "teachers", "students", "known_works",
    "scholarly_standing", "methodology_notes", "methodological_stance",
    "disambiguation_notes", "genealogy_metadata",
]

_LOCK_TIMEOUT = 30  # seconds


def _load_registry(path: Path) -> dict[str, dict]:
    """Load scholars.json from disk. Returns empty dict if file doesn't exist."""
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def _save_registry(path: Path, data: dict[str, dict]) -> None:
    """Save scholars.json atomically: temp file → fsync → os.replace.
    Creates .bak before overwriting (§4.A.2 Step 7).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)

    fd = tempfile.NamedTemporaryFile(
        mode="w",
        dir=path.parent,
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    )
    try:
        fd.write(content)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()

        if path.exists():
            bak = path.with_suffix(".json.bak")
            try:
                if bak.exists():
                    bak.unlink()
                path.replace(bak)
            except OSError:
                pass  # Best-effort backup

        os.replace(fd.name, str(path))
    except BaseException:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def _next_canonical_id(registry: dict[str, dict]) -> str:
    """Compute next sequential ID by scanning for highest existing ID.

    Returns: 'sch_00001' for empty registry, 'sch_00002' if sch_00001 exists, etc.
    """
    max_num = 0
    for key in registry:
        if key.startswith("sch_") and len(key) == 9:
            try:
                num = int(key[4:])
                max_num = max(max_num, num)
            except ValueError:
                continue
    return f"sch_{max_num + 1:05d}"


def _compute_record_completeness(record: ScholarAuthorityRecord) -> float:
    """Fraction of the 24 biographical/scholarly fields with non-null values."""
    filled = 0
    for fname in _BIOGRAPHICAL_FIELDS:
        value = getattr(record, fname, None)
        if value is None:
            continue
        if isinstance(value, (list, dict)) and len(value) == 0:
            continue
        if isinstance(value, bool):
            # bool fields like death_date_approximate always count as filled
            filled += 1
            continue
        filled += 1
    return filled / len(_BIOGRAPHICAL_FIELDS)


def compute_scholar_match_score(
    candidate_name: str,
    candidate_death_date: Optional[int],
    candidate_school: Optional[str],
    candidate_known_work: Optional[str],
    existing_record: ScholarAuthorityRecord,
) -> float:
    """Compute composite match score between a candidate and an existing record.

    SPEC §4.A.5 weighted average of available signals:
    - Name match:   weight 0.50
    - Death date:   weight 0.30
    - School:       weight 0.10
    - Known works:  weight 0.10

    Only signals with data on BOTH sides contribute to the weighted average.
    If only name has data, score is capped at 0.65 (below auto_link threshold).
    """
    signals: list[tuple[float, float]] = []  # (weight, score)

    # 1. Name similarity — compare against all name variants
    all_names = [existing_record.canonical_name_ar]
    all_names.extend(existing_record.known_as)
    all_names.extend(existing_record.name_variants)

    best_name_sim = 0.0
    for name in all_names:
        sim = normalized_name_similarity(candidate_name, name)
        best_name_sim = max(best_name_sim, sim)

    signals.append((0.50, best_name_sim))

    # 2. Death date proximity
    if candidate_death_date is not None and existing_record.death_date_hijri is not None:
        diff = abs(candidate_death_date - existing_record.death_date_hijri)
        date_score = max(0.0, 1.0 - diff / 50.0)
        signals.append((0.30, date_score))

    # 3. School match
    if candidate_school is not None and existing_record.school_affiliations:
        school_values = [
            v for v in existing_record.school_affiliations.values()
            if v is not None
        ]
        school_score = 1.0 if candidate_school in school_values else 0.0
        signals.append((0.10, school_score))

    # 4. Known works match
    if candidate_known_work is not None and existing_record.known_works:
        work_score = 0.0
        for work_id in existing_record.known_works:
            sim = normalized_name_similarity(candidate_known_work, work_id)
            if sim > 0.80:
                work_score = 1.0
                break
        signals.append((0.10, work_score))

    if not signals:
        return 0.0

    total_weight = sum(w for w, _ in signals)
    weighted_sum = sum(w * s for w, s in signals)
    score = weighted_sum / total_weight

    # Cap at 0.65 when only name signal has data — prevents auto-linking on name alone
    if len(signals) == 1:
        score = min(score, 0.65)

    return score


def lookup(
    name: str,
    death_date_hijri: Optional[int] = None,
    school: Optional[str] = None,
    known_work_title: Optional[str] = None,
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarMatchResult:
    """Look up a scholar in the registry using composite scoring.

    SPEC §4.A.5 thresholds:
    - >= 0.85: auto_link (confident match)
    - 0.50-0.85: human_gate (possible match, needs owner confirmation)
    - < 0.50: new_record (no match found)
    """
    registry = _load_registry(registry_path)

    if not registry:
        return ScholarMatchResult(
            found=False,
            record=None,
            match_score=0.0,
            match_detail="Empty registry",
            action="new_record",
        )

    best_score = 0.0
    best_record: Optional[ScholarAuthorityRecord] = None
    best_id = ""

    for cid, data in registry.items():
        record = ScholarAuthorityRecord.model_validate(data)
        score = compute_scholar_match_score(
            name, death_date_hijri, school, known_work_title, record
        )
        if score > best_score:
            best_score = score
            best_record = record
            best_id = cid

    if best_score >= 0.85:
        action = "auto_link"
        detail = f"Auto-linked to {best_id} (score {best_score:.3f})"
    elif best_score >= 0.50:
        action = "human_gate"
        detail = f"Possible match to {best_id} (score {best_score:.3f}), needs review"
    else:
        action = "new_record"
        detail = (
            f"No match above 0.50 (best: {best_id} at {best_score:.3f})"
            if best_id else "No candidates"
        )
        best_record = None

    return ScholarMatchResult(
        found=best_score >= 0.50,
        record=best_record,
        match_score=best_score,
        match_detail=detail,
        action=action,
    )


def register(
    record: ScholarAuthorityRecord,
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarAuthorityRecord:
    """Create a new scholar record in the registry.

    Assigns next sequential canonical_id, computes record_completeness,
    sets data_provenance_score = 0.0, sets last_updated to UTC ISO 8601.
    """
    if not record.canonical_name_ar or not record.canonical_name_ar.strip():
        raise ValueError("canonical_name_ar must be non-empty")

    lock = FileLock(str(registry_path) + ".lock", timeout=_LOCK_TIMEOUT)
    with lock:
        registry = _load_registry(registry_path)

        new_id = _next_canonical_id(registry)
        record.canonical_id = new_id
        record.data_provenance_score = 0.0
        record.last_updated = datetime.now(timezone.utc).isoformat()
        record.record_completeness = _compute_record_completeness(record)

        if new_id in registry:
            raise ValueError(f"Duplicate canonical_id {new_id} — registry corrupted")

        registry[new_id] = record.model_dump(mode="json")
        _save_registry(registry_path, registry)

    return record


def update(
    canonical_id: str,
    updates: dict[str, Any],
    source_id: str,
    requesting_engine: str = "source",
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarUpdateResult:
    """Update an existing scholar record with new information.

    Runs 5 consistency checks. Returns ScholarUpdateResult with the record
    and any conflicts. The caller creates human gate checkpoints for conflicts.

    Blocked updates (name change, self-reference) are not applied.
    Gate-triggering updates (date drift, school change, temporal) ARE applied
    but conflicts are returned so the caller can create gates.
    """
    lock = FileLock(str(registry_path) + ".lock", timeout=_LOCK_TIMEOUT)
    with lock:
        registry = _load_registry(registry_path)

        if canonical_id not in registry:
            raise KeyError(f"Scholar {canonical_id} not found in registry")

        record = ScholarAuthorityRecord.model_validate(registry[canonical_id])
        conflicts: list[ScholarUpdateConflict] = []
        blocked = False

        # Check 1: Death date drift > 5 years
        if "death_date_hijri" in updates and updates["death_date_hijri"] is not None:
            if record.death_date_hijri is not None:
                drift = abs(record.death_date_hijri - updates["death_date_hijri"])
                if drift > 5:
                    conflicts.append(ScholarUpdateConflict(
                        check_name="death_date_drift",
                        severity="gate",
                        field="death_date_hijri",
                        detail=(
                            f"Existing: {record.death_date_hijri}, "
                            f"proposed: {updates['death_date_hijri']}, "
                            f"drift: {drift} years"
                        ),
                        error_code="SRC_SCHOLAR_DATE_CONFLICT",
                    ))

        # Check 2: School affiliation change
        if "school_affiliations" in updates and updates["school_affiliations"]:
            for science, new_school in updates["school_affiliations"].items():
                existing_school = record.school_affiliations.get(science)
                if existing_school is not None and new_school != existing_school:
                    conflicts.append(ScholarUpdateConflict(
                        check_name="school_affiliation_change",
                        severity="gate",
                        field=f"school_affiliations.{science}",
                        detail=(
                            f"Existing: {existing_school}, "
                            f"proposed: {new_school}"
                        ),
                        error_code="SRC_SCHOLAR_SCHOOL_CONFLICT",
                    ))

        # Check 3: Name change — BLOCKED
        if "canonical_name_ar" in updates:
            if updates["canonical_name_ar"] != record.canonical_name_ar:
                conflicts.append(ScholarUpdateConflict(
                    check_name="name_change_blocked",
                    severity="blocked",
                    field="canonical_name_ar",
                    detail=(
                        f"Cannot change canonical_name_ar from "
                        f"'{record.canonical_name_ar}' to "
                        f"'{updates['canonical_name_ar']}'. "
                        f"Add to known_as instead."
                    ),
                    error_code="SRC_SCHOLAR_NAME_BLOCKED",
                ))
                blocked = True

        # Check 4: Self-reference in teachers/students
        for rel_field in ("teachers", "students"):
            if rel_field in updates:
                new_ids = updates[rel_field]
                if isinstance(new_ids, list) and canonical_id in new_ids:
                    conflicts.append(ScholarUpdateConflict(
                        check_name="self_reference",
                        severity="blocked",
                        field=rel_field,
                        detail=f"Scholar {canonical_id} cannot be own {rel_field[:-1]}",
                        error_code="SRC_SCHOLAR_SELF_REFERENCE",
                    ))
                    blocked = True

        # Check 5: Temporal inconsistency — teacher death > student death + 30
        if "teachers" in updates and updates["teachers"]:
            for teacher_id in updates["teachers"]:
                if teacher_id in registry:
                    teacher = ScholarAuthorityRecord.model_validate(registry[teacher_id])
                    if (
                        teacher.death_date_hijri is not None
                        and record.death_date_hijri is not None
                        and teacher.death_date_hijri > record.death_date_hijri + 30
                    ):
                        conflicts.append(ScholarUpdateConflict(
                            check_name="temporal_inconsistency",
                            severity="gate",
                            field="teachers",
                            detail=(
                                f"Teacher {teacher_id} died {teacher.death_date_hijri} AH, "
                                f"student died {record.death_date_hijri} AH — "
                                f"gap of {teacher.death_date_hijri - record.death_date_hijri} years"
                            ),
                            error_code="SRC_SCHOLAR_TEMPORAL_INCONSISTENCY",
                        ))

        if blocked:
            return ScholarUpdateResult(
                record=record,
                applied=False,
                conflicts=conflicts,
            )

        # Apply updates — preserve old values in revision_history
        now = datetime.now(timezone.utc).isoformat()
        for field_name, new_value in updates.items():
            if field_name in (
                "canonical_id", "record_completeness",
                "data_provenance_score", "revision_history",
                "last_updated", "sources_encountered_in",
            ):
                continue  # Bookkeeping fields managed internally

            old_value = getattr(record, field_name, None)

            # For list fields: merge (append new items)
            if isinstance(old_value, list) and isinstance(new_value, list):
                merged = list(old_value)
                for item in new_value:
                    if item not in merged:
                        merged.append(item)
                new_value = merged

            # For dict fields: merge (update keys)
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                merged = dict(old_value)
                merged.update(new_value)
                new_value = merged

            if old_value != new_value:
                record.revision_history.append(MetadataHistoryEntry(
                    field=field_name,
                    old_value=json.dumps(old_value, ensure_ascii=False) if old_value is not None else None,
                    new_value=json.dumps(new_value, ensure_ascii=False),
                    changed_by=f"{requesting_engine}:{source_id}",
                    timestamp=now,
                ))
                setattr(record, field_name, new_value)

        # Append source_id to sources_encountered_in
        if source_id not in record.sources_encountered_in:
            record.sources_encountered_in.append(source_id)

        record.record_completeness = _compute_record_completeness(record)
        record.last_updated = now

        registry[canonical_id] = record.model_dump(mode="json")
        _save_registry(registry_path, registry)

    return ScholarUpdateResult(
        record=record,
        applied=True,
        conflicts=conflicts,
    )


def get_all(
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> dict[str, ScholarAuthorityRecord]:
    """Return all registered scholars as a dict keyed by canonical_id."""
    registry = _load_registry(registry_path)
    return {
        cid: ScholarAuthorityRecord.model_validate(data)
        for cid, data in registry.items()
    }
