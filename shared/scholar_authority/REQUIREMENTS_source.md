# Scholar Authority — Source Engine Requirements

**Component:** `shared/scholar_authority/`
**Consumer:** Source engine (Session 4), Normalization engine (layer attribution)
**SPEC authority:** `engines/source/SPEC_CORE.md` §4.A.5, §4.A.6; `engines/source/contracts.py` ScholarAuthorityRecord

---

## Purpose

The scholar authority registry stores every scholar encountered in the library. It provides identity matching (is this the same person?), record creation, progressive enrichment, and consistency checking. The source engine is the primary writer; other engines enrich records via the enrichment write-back path.

---

## Interface

### `lookup()`

```python
from typing import Optional
from engines.source.contracts import ScholarAuthorityRecord


@dataclass
class ScholarMatchResult:
    """Result of looking up a scholar."""
    found: bool                          # Whether any match met the threshold
    record: Optional[ScholarAuthorityRecord]  # The matched record, if found
    match_score: float                   # Composite score (0.0–1.0)
    match_detail: str                    # Human-readable explanation of the match
    action: str                          # One of: "auto_link", "human_gate", "new_record"


def lookup(
    name: str,
    death_date_hijri: Optional[int] = None,
    school: Optional[str] = None,
    known_work_title: Optional[str] = None,
) -> ScholarMatchResult:
    """Look up a scholar in the registry.

    Searches all existing records for the best match using the composite
    scoring algorithm (§4.A.5). Returns the best match with its score
    and the recommended action.

    Parameters
    ----------
    name : str
        The scholar's name as extracted/inferred. Arabic text with or
        without diacritics. The function normalizes internally.
    death_date_hijri : int, optional
        Hijri death date if known. Improves matching accuracy significantly.
    school : str, optional
        School affiliation if known (e.g., "shafii" for nahw).
    known_work_title : str, optional
        Title of a known work by this scholar, if available. Used for
        disambiguation when name and dates are insufficient.

    Returns
    -------
    ScholarMatchResult
        - action="auto_link" when match_score ≥ 0.85: confident match.
        - action="human_gate" when 0.50 ≤ match_score < 0.85: possible match,
          needs owner confirmation.
        - action="new_record" when match_score < 0.50 or no existing records:
          create a new scholar record.

    Thread Safety
    -------------
    This function reads scholars.json. When used in the acquisition pipeline,
    the caller must hold the scholars.json file lock (acquired in Step 4,
    held through record creation — SPEC §4.A.2).
    """
```

### Matching Algorithm (SPEC §4.A.5)

```python
def compute_scholar_match_score(
    candidate_name: str,
    candidate_death_date: Optional[int],
    candidate_school: Optional[str],
    candidate_known_work: Optional[str],
    existing_record: ScholarAuthorityRecord,
) -> float:
    """Compute composite match score between a candidate and an existing record.
    
    Weighted average of available signals:
    - Name match:   weight 0.50
    - Death date:   weight 0.30
    - School:       weight 0.10
    - Known works:  weight 0.10
    
    Only signals with data contribute to the average. If only name is
    available (typical for first encounter), the score is purely name-based.
    """
```

**Name matching MUST use token-based approach** from `eval_harness.py`, NOT `difflib.SequenceMatcher`. Implementation:

```python
from shared.scholar_authority.src.name_matching import (
    normalize_arabic_name,
    _extract_name_tokens,
    normalized_name_similarity,
)
```

These functions are copied from `tests/eval_harness.py` (lines 22–95) into `shared/scholar_authority/src/name_matching.py` as the production implementation. The token-based approach:
1. Normalizes both names (strip diacritics, normalize hamza/taa marbuta, strip definite article).
2. Extracts significant tokens (removes بن/ابن particles).
3. Computes overlap: `len(shared_tokens) / min(len(tokens_a), len(tokens_b))`.
4. If shorter name's tokens are a subset of longer → score ≥ 0.85 (handles A3-1).
5. Substring fallback for compound-word mismatches → 0.40.

Name comparison checks ALL name variants: `canonical_name_ar`, `known_as`, `name_variants`. Returns the best score across all variants.

**Death date scoring:** Exact match = 1.0. Linear decay: `max(0.0, 1.0 - diff / 50.0)`. Difference of 50+ years = 0.0. This is generous because death dates are approximate in many sources (e.g., "d. around 670 AH").

**School scoring:** Binary — either the candidate school appears in the record's `school_affiliations` values, or it doesn't.

**Known works scoring:** Check if `candidate_known_work` matches any title in `existing_record.known_works` using `normalized_title_similarity() > 0.80`.

### `register()`

```python
def register(record: ScholarAuthorityRecord) -> ScholarAuthorityRecord:
    """Create a new scholar record in the registry.

    Parameters
    ----------
    record : ScholarAuthorityRecord
        The record to create. Must have:
        - canonical_id: assigned by this function (next in sequence sch_NNNNN)
        - canonical_name_ar: the full Arabic name (immutable after creation)
        All other fields may be partially populated.

    Returns
    -------
    ScholarAuthorityRecord
        The record as persisted, with canonical_id assigned.

    Validation
    ----------
    - Validates against ScholarAuthorityRecord Pydantic model.
    - Checks canonical_name_ar is non-empty.
    - Verifies no existing record with the same canonical_id (collision).

    Side Effects
    ------------
    Writes to library/registries/scholars.json.
    Logs the creation to library/logs/source_engine.jsonl.
    """
```

### `update()`

```python
def update(
    canonical_id: str,
    updates: dict[str, Any],
    source_id: str,
    requesting_engine: str = "source",
) -> ScholarAuthorityRecord:
    """Update an existing scholar record with new information.

    Runs the 5 consistency checks (§4.A.5) before applying any update.
    Preserves overwritten values in revision_history.

    Parameters
    ----------
    canonical_id : str
        The scholar's canonical_id.
    updates : dict
        Field name → new value mappings.
    source_id : str
        The source that triggered this update (for provenance).
    requesting_engine : str
        Which engine is requesting the update.

    Consistency Checks (run before applying)
    -----------------------------------------
    1. Death date drift: existing differs from proposed by > 5 years
       → SRC_SCHOLAR_DATE_CONFLICT → human gate.
    2. School affiliation change: existing school would change
       → SRC_SCHOLAR_SCHOOL_CONFLICT → human gate.
    3. Name change: canonical_name_ar modification → BLOCKED.
       New name variants go to known_as instead.
    4. Teacher/student self-reference: scholar as own teacher/student → rejected.
    5. Temporal consistency: proposed teacher's death date > student's death
       date + 30 years → SRC_SCHOLAR_TEMPORAL_INCONSISTENCY → human gate.

    Returns
    -------
    ScholarAuthorityRecord
        The updated record.
    """
```

---

## Storage

**Registry file:** `library/registries/scholars.json`

Format: JSON object mapping `canonical_id` → `ScholarAuthorityRecord` (serialized).

```json
{
  "sch_00001": {
    "canonical_id": "sch_00001",
    "canonical_name_ar": "بهاء الدين عبد الله بن عقيل الهمداني المصري",
    "known_as": ["ابن عقيل"],
    "name_variants": [],
    "death_date_hijri": 769,
    "school_affiliations": {"nahw": null, "fiqh": null},
    "sources_encountered_in": ["src_a7c3e91f"],
    "record_completeness": 0.42,
    ...
  }
}
```

**ID generation:** `sch_{5_digit_sequence}` — monotonically increasing. The next available ID is determined by scanning the registry for the highest existing ID and incrementing.

**`record_completeness`:** Fraction of the 24 biographical/scholarly fields with non-null values. Excludes the 6 bookkeeping fields. Updated whenever the record is modified.

**`data_provenance_score`:** Fraction of biographical fields corroborated by non-LLM sources. 0.0 for all records in Stage 1 (everything is LLM-inferred). Extension hook for Stage 2 external enrichment.

---

## Progressive Enrichment

Each time a source mentions an existing scholar, the engine checks whether the new source provides information the existing record lacks. If so, `update()` is called with the new fields:

- New `known_as` entries are appended (not replaced).
- New `school_affiliations` are merged (only if they don't conflict with existing — conflicts trigger SCHOLAR_CONFLICT human gate).
- `sources_encountered_in` is appended with the new source_id.
- `record_completeness` is recalculated.
- All overwritten values are preserved in `revision_history`.

---

## Cross-Engine Reuse

The normalization engine needs `lookup()` for layer attribution — when it detects text layers, it resolves layer author names to `canonical_id` values. The interface is ready for this:

- `lookup()` takes a name string and optional death date — the normalization engine can call it with the layer author name extracted during normalization.
- The normalization engine does NOT need `register()` or `update()` — it only reads scholar identity.
- If the normalization engine encounters a name not in the registry (unlikely, since the source engine runs first), it should create a sparse record via the source engine's enrichment write-back path, not directly.

---

## Muhaqiq Records

Tahqiq editors are scholars and get full `ScholarAuthorityRecord` entries. The source engine creates muhaqiq records during Step 4 (metadata inference) when a muhaqiq name is extracted. The source metadata links to both the original author's `canonical_id` (via `author.canonical_id`) and the muhaqiq's `canonical_id` (via `muhaqiq.canonical_id`).

---

## Edge Cases

**Short-vs-long name (A3-1).** "النووي" vs "أبو زكريا يحيى بن شرف النووي" — the token-based approach handles this (shorter name's tokens are a subset → score ≥ 0.85 → auto-link). This was the primary deficiency of the SequenceMatcher approach.

**Ambiguous names.** "ابن حجر" could be al-Asqalani (d. 852) or al-Haytami (d. 974). Without a death date, name matching alone cannot distinguish them. The death date signal (weight 0.30) is the primary disambiguation tool. If no death date is available, the score relies on school and known-work signals. If still ambiguous (0.50–0.85 range), human gate is triggered.

**Sparse records.** Records created from genre chain references (e.g., the author of a referenced base work) may have only a name — no death date, no school, no works. These records have very low `record_completeness` (~0.10). They are stubs that get enriched when the referenced work is actually acquired.
