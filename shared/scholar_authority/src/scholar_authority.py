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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from filelock import FileLock

from engines.source.contracts import ScholarAuthorityRecord
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


def _load_registry(path: Path) -> dict[str, dict]:
    """Load scholars.json from disk. Returns empty dict if file doesn't exist."""
    raise NotImplementedError


def _save_registry(path: Path, data: dict[str, dict]) -> None:
    """Save scholars.json atomically: temp file → fsync → os.replace.
    Creates .bak before overwriting (§4.A.2 Step 7).
    """
    raise NotImplementedError


def _next_canonical_id(registry: dict[str, dict]) -> str:
    """Compute next sequential ID by scanning for highest existing ID.
    
    SPEC §4.A.5: 'The next available ID is determined by scanning the
    registry for the highest existing ID.'
    
    Returns: 'sch_00001' for empty registry, 'sch_00002' if sch_00001 exists, etc.
    """
    raise NotImplementedError


def _compute_record_completeness(record: ScholarAuthorityRecord) -> float:
    """Fraction of the 24 biographical/scholarly fields with non-null values.
    Excludes the 6 bookkeeping fields (SPEC §4.A.5).
    
    Biographical fields (24): canonical_name_ar, known_as, name_variants, kunya,
    laqab, nisba, birth_date_hijri, birth_date_ce, death_date_hijri, death_date_ce,
    death_date_approximate, era_century_hijri, geographic_origin, geographic_active,
    school_affiliations, sectarian_tradition, teachers, students, known_works,
    scholarly_standing, methodology_notes, methodological_stance, disambiguation_notes,
    genealogy_metadata.
    
    Bookkeeping fields (6): sources_encountered_in, record_completeness,
    data_provenance_score, record_sources, revision_history, last_updated.
    """
    raise NotImplementedError


def compute_scholar_match_score(
    candidate_name: str,
    candidate_death_date: Optional[int],
    candidate_school: Optional[str],
    candidate_known_work: Optional[str],
    existing_record: ScholarAuthorityRecord,
) -> float:
    """Compute composite match score between a candidate and an existing record.
    
    SPEC §4.A.5 weighted average of available signals:
    - Name match:   weight 0.50 (compare against canonical_name_ar + known_as + name_variants)
    - Death date:   weight 0.30 (exact = 1.0, linear decay over 50 years)
    - School:       weight 0.10 (binary: candidate school in record's school_affiliations values)
    - Known works:  weight 0.10 (title similarity > 0.80 against record's known_works)
    
    Only signals with data contribute to the weighted average.
    """
    raise NotImplementedError


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
    
    Compares against ALL name variants: canonical_name_ar, known_as, name_variants.
    Returns the best-scoring match.
    
    Thread safety: caller must hold scholars.json file lock (SPEC §4.A.2).
    """
    raise NotImplementedError


def register(
    record: ScholarAuthorityRecord,
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarAuthorityRecord:
    """Create a new scholar record in the registry.
    
    SPEC §4.A.5:
    - Assigns next sequential canonical_id (sch_NNNNN).
    - Validates against ScholarAuthorityRecord Pydantic model.
    - Checks canonical_name_ar is non-empty.
    - Verifies no existing record with the same canonical_id.
    - Computes record_completeness.
    - Sets data_provenance_score = 0.0 (Stage 1: all LLM-inferred).
    - Sets last_updated to current UTC ISO 8601 timestamp.
    
    Returns the record as persisted, with canonical_id assigned.
    """
    raise NotImplementedError


def update(
    canonical_id: str,
    updates: dict[str, Any],
    source_id: str,
    requesting_engine: str = "source",
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarAuthorityRecord:
    """Update an existing scholar record with new information.
    
    SPEC §4.A.5 — runs 5 consistency checks before applying:
    
    1. Death date drift: existing differs from proposed by > 5 years
       → SRC_SCHOLAR_DATE_CONFLICT → human gate.
    2. School affiliation change: existing school would change
       → SRC_SCHOLAR_SCHOOL_CONFLICT → human gate.
    3. Name change: canonical_name_ar modification → BLOCKED.
       New name variants go to known_as instead.
    4. Teacher/student self-reference: scholar as own teacher/student → rejected.
    5. Temporal consistency: proposed teacher's death date > student's + 30 years
       → SRC_SCHOLAR_TEMPORAL_INCONSISTENCY → human gate.
    
    On success:
    - Preserves overwritten values in revision_history.
    - Appends source_id to sources_encountered_in.
    - Recalculates record_completeness.
    - Updates last_updated timestamp.
    
    Returns: ConsistencyCheckResult with the updated record and any gate triggers.
    """
    raise NotImplementedError


def get_all(
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> dict[str, ScholarAuthorityRecord]:
    """Return all registered scholars as a dict keyed by canonical_id."""
    raise NotImplementedError
