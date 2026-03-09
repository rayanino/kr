# Contracts Audit — Session 5

Comparison of `contracts.py` (schema authority) against SPEC §4.A.5, §4.A.8, §4.A.9, §5, and shared component REQUIREMENTS files.

## Status: 2 misalignments found, 1 missing field, 1 missing config file

### ✅ Aligned

| Model | Status | Notes |
|-------|--------|-------|
| `ScholarAuthorityRecord` | ✅ All 30 fields match SPEC §4.A.5 | 24 biographical + 6 bookkeeping + 2 extension hooks. `canonical_id` format `sch_NNNNN` documented. |
| `WorkRegistryEntry` | ✅ All fields match SPEC §4.A.9 | `relationships: list[WorkRelationshipEdge]`, `status`, `source_ids`, `preferred_source_id`. |
| `SourceRegistryEntry` | ✅ All fields match SPEC §4.A.2 Step 7 | `frozen_hash`, `processing_status`, `trust_tier`. |
| `TrustworthinessFactor` | ✅ 4 fields: name, weight, score, reason | Matches §4.A.8 worked example. |
| `TrustTier` | ✅ 3 values: verified, flagged, owner_override | Matches §4.A.8. |
| `WorkRelationshipEdge` | ✅ Fields: from_work_id, to_work_id, relation_type, confidence, discovered_by | Matches §4.A.9. |
| `GenreRelationType` | ✅ 7 values match §4.A.9 exhaustive list | sharh_of, hashiyah_on, mukhtasar_of, nazm_of, taqrirat_on, responds_to, cites. |
| `RegistryPendingWrite` | ✅ Fields: source_id, timestamp, intended_changes, completed_files | Matches §4.A.2 Step 7 write-ahead log. |
| `ErrorCode` | ✅ All 27 core + 9 deferred codes present | Checked all §7 codes. Names use short form (e.g., `SCHOLAR_DATE_CONFLICT` not `SRC_SCHOLAR_DATE_CONFLICT`), values include `SRC_` prefix. |
| `SourceMetadata.trust_*` fields | ✅ trust_tier, trust_score, trust_factors, trust_reason all present | Matches §4.A.8 output. |
| `InferredFieldConfidence` | ✅ Per-field confidence tracking | Used by validation Check 3. |
| `ProcessingStatus` | ✅ 8 values match §4.A.10 | staging → acquired → ... → complete, error, withdrawn. |

### ⚠️ Misalignment 1: `HumanGateCheckpoint` lacks `status` enum

**contracts.py current:** `resolved: bool`, `resolution: Optional[str]`, `resolved_at: Optional[str]`

**REQUIREMENTS_source.md (SPEC §5 Layer 2 + KNOWLEDGE_INTEGRITY.md Layer 4):** `status: Literal["pending", "approved", "rejected", "unsure", "elevated", "auto_approved"]`, `decision: Optional[str]`, `elevated_result: Optional[dict]`

**Impact:** The `unsure` → `elevated` workflow (Layer 3.5: 3+ model consensus when owner says "unsure") cannot be represented with a boolean `resolved`. The auto-approve mode for build/test also needs distinct representation from owner approval.

**Recommended fix:** Replace `resolved: bool` with `status: str` (one of: pending, approved, rejected, unsure, elevated, auto_approved). Keep `resolution` for the owner's freeform notes. Add `elevated_result: Optional[dict]` for Layer 3.5 output. Keep `resolved_at` as-is.

**contracts.py change needed:**
```python
class HumanGateCheckpoint(BaseModel):
    checkpoint_id: str
    source_id: str
    trigger: HumanGateTrigger
    trigger_detail: str
    fields_to_review: list[str]
    current_values: dict[str, Any]
    alternatives: Optional[list[dict[str, Any]]] = None
    created_at: str
    status: str = "pending"  # pending|approved|rejected|unsure|elevated|auto_approved
    resolution: Optional[str] = None  # Owner's notes or corrected value
    resolved_at: Optional[str] = None
    elevated_result: Optional[dict[str, Any]] = None  # Layer 3.5 output
```

### ⚠️ Misalignment 2: `HumanGateCheckpoint` field naming vs REQUIREMENTS

| contracts.py | REQUIREMENTS | Resolution |
|-------------|-------------|------------|
| `trigger` (HumanGateTrigger) | `gate_type` (str) | Keep `trigger` — contracts.py is authority. REQUIREMENTS describes interface, not schema. |
| `trigger_detail` | `reason` | Keep `trigger_detail`. More precise name. |
| `current_values` + `alternatives` | `context` (free-form dict) | Keep split fields — more structured, better for the review UI. |
| `created_at` | `created_utc` | Keep `created_at`. Both are ISO 8601 UTC. |

**Action:** The shared `human_gate` implementation should use contracts.py field names. The REQUIREMENTS describes the conceptual interface; `create_checkpoint()` function parameters can use descriptive names that map to contracts.py fields internally.

### ❌ Missing: `MISSING_REQUIRED_INPUT` trigger

**SPEC §7 (SRC_FORMAT_STRUCTURE_MISSING recovery):** "Fall back to minimal extraction + LLM inference. Flag all fields `needs_review`." The session-5-plan.md (from engines/source/src/human_gate.py docstring) lists `MISSING_REQUIRED_INPUT` as a trigger, but it's not in the `HumanGateTrigger` enum.

**Recommendation:** This is a Session 6 concern (error paths). Not needed for Session 5. The 9 existing triggers cover all Session 5 use cases.

### ⚠️ Misalignment 3: SPEC §4.A.8 author_standing formula broken for first intake

**SPEC text:** "Classical scholar (death_date_hijri ≤ 1000 AH AND scholarly_standing non-null AND the scholar's sources_encountered_in contains at least one source_id other than the current source): 0.90."

**Reality:** On first intake, every author has 0 prior sources → `author_standing` = 0.30 for ALL scholars → 6/13 fixtures produce incorrect trust tiers (classical scholars flagged instead of verified).

**Root cause:** The "prior sources" condition was added during HARDENING but never re-validated against the 13 fixtures. The Phase 0 validation (13/13 correct) used only death_date ≤ 1000 for the classical tier.

**Validated formula:** death_date ≤ 1000 → 0.90; death_date > 1000 → 0.70; no death date → 0.30. Re-verified: 13/13 correct.

**Fix:** Build trust evaluator using the validated formula for initial intake. The "prior sources" check applies only during trust re-evaluation on enrichment (§4.A.8 last paragraph). Documented in trust_evaluator.py stub and NEXT.md.

### ❌ Missing config files

The following config files are referenced in SPEC §8 but don't exist yet:
- `library/config/recognized_muhaqiqs.json` — needed by trust evaluator
- `library/config/known_publishers.json` — needed by trust evaluator  
- `library/config/transliteration.json` — needed by §4.A.1 slug generation (already built in staging.py, but may use hardcoded values)

`genre_synonyms.json` already exists and is correct.

**Action:** Create these config files in Session 5, populated from SPEC §8.
