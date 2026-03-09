# NEXT — Source Engine Session 5a: Shared Components + Trust + Validation

**Session type:** BUILD — implement shared scholar_authority, human_gate, validation, trust evaluator, config
**Pipeline steps:** Step 7 (Registration prerequisites) + Step 8 (Trust Evaluation) + §5 (Validation)
**Depends on:** Sessions 1–4 (365 tests passing: extraction, format detection, inference, consensus, hashing, dedup, freezing)

---

## ⚠️ Scope Warning

Session 5 builds 10 modules — this is split into two sub-sessions:
- **Session 5a (this session):** Shared components + trust + validation (6 modules)
- **Session 5b (next session):** Registries + registration orchestrator (4 modules)

Session 5a produces the components that Session 6 (integration) blocks on.

---

## What to Read

Read these files in order before writing any code:

1. `engines/source/SPEC_CORE.md` §4.A.5 — Scholar Authority Model (full section, lines 1203–1288)
2. `engines/source/SPEC_CORE.md` §4.A.8 — Trustworthiness Evaluation (full section, lines 1311–1365)
3. `engines/source/SPEC_CORE.md` §5 — Validation and Quality (all 6 Layer 1 checks + Layer 2, lines 1441–1494)
4. `engines/source/SPEC_CORE.md` §8 — Configuration (reference lists, parameters, lines 1591–1666)
5. `engines/source/contracts.py` — `ScholarAuthorityRecord`, `TrustworthinessFactor`, `TrustTier`, `HumanGateCheckpoint`, `HumanGateTrigger`, `InferredFieldConfidence`, `ErrorCode`
6. `shared/scholar_authority/REQUIREMENTS_source.md` — Scholar authority interface spec
7. `shared/human_gate/REQUIREMENTS_source.md` — Human gate interface spec
8. `shared/validation/REQUIREMENTS_source.md` — Validation interface spec
9. `KNOWLEDGE_INTEGRITY.md` Layer 4 — What the owner CAN and CANNOT verify
10. `engines/source/docs/session5-architecture.md` — Module dependency graph and data flow
11. `engines/source/docs/session5-contracts-audit.md` — Known misalignment: HumanGateCheckpoint needs `status` field
12. `engines/source/docs/session5-test-plan.md` — Test specifications (tests 1–70)
13. `tests/fixtures/GROUND_TRUTH.json` — Expected trust values for all 13 fixtures

---

## Contracts Change Required FIRST

**Before writing any module code**, update `engines/source/contracts.py`:

Replace the `HumanGateCheckpoint` model's `resolved: bool` with `status: str`:

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
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None
    elevated_result: Optional[dict[str, Any]] = None  # Layer 3.5 output
```

This is needed because the `unsure → elevated` workflow (KNOWLEDGE_INTEGRITY.md Layer 4) cannot be represented with a boolean. No existing tests create HumanGateCheckpoint instances, so this change has no test impact.

---

## SPEC Defect Fix: Author Standing First-Intake Formula

**CRITICAL — must understand before building trust evaluator.**

The SPEC §4.A.8 author_standing tier says: "Classical scholar (death_date_hijri ≤ 1000 AH AND scholarly_standing non-null AND the scholar's sources_encountered_in contains at least one source_id other than the current source): 0.90."

The "prior sources" condition was added during HARDENING but **never re-validated**. On first intake, every author has 0 prior sources, making `author_standing` = 0.30 for ALL scholars. This causes **6 of 13 fixtures to produce INCORRECT trust tiers** — classical scholars like al-Suyuti (d. 911) and al-Bukhari (d. 256) get flagged instead of verified.

The **validated formula** (Phase 0: 13/13 correct at threshold 0.65) uses ONLY the death date for first intake:
- `death_date_hijri ≤ 1000` → 0.90 (classical)
- `death_date_hijri > 1000` (known date) → 0.70 (post-classical)
- `death_date_hijri is None` → 0.30 (unknown/contemporary)

**Build the trust evaluator using this validated formula.** The "prior sources" and "scholarly_standing non-null" checks belong in the **trust re-evaluation** path (§4.A.8, "Trust re-evaluation on enrichment") where prior sources actually exist. For initial intake, they must not be required.

The trust_evaluator.py stub documents this with the full explanation. See its module docstring.

---

## What to Build (in dependency order)

### Module 1: `engines/source/src/config.py` (~50 lines)
Replace the stub. Load all 4 config files from `library/config/`:
- `recognized_muhaqiqs.json` → `list[str]`
- `known_publishers.json` → `dict[str, dict]` (each entry has `score` and `variants`)
- `transliteration.json` → `dict[str, dict[str, str]]` (keys: "scholars", "titles")
- `genre_synonyms.json` → `dict[str, str]`

Return a `SourceEngineConfig` dataclass. Missing files produce empty defaults (not errors). Malformed JSON raises with the filename in the error message.

**Test:** `engines/source/tests/test_config.py` (5 tests)

### Module 2: `shared/scholar_authority/src/scholar_authority.py` (~250 lines)
Replace the tracer stub at `shared/scholar_authority/src/__init__.py`. The new implementation lives in `scholar_authority.py` and the `__init__.py` should re-export the public API.

Implement:
- `compute_scholar_match_score()` — SPEC §4.A.5 weighted algorithm. Use `normalized_name_similarity()` from `name_matching.py` (already built, 22 tests passing). Weight 0.50 name, 0.30 death date, 0.10 school, 0.10 known works. Only available signals contribute to the weighted average.
- `lookup()` — Iterate all records, compute match score, return best. Thresholds: ≥ 0.85 auto_link, 0.50–0.85 human_gate, < 0.50 new_record. Compare against canonical_name_ar + known_as + name_variants.
- `register()` — Assign next sequential ID (`sch_NNNNN`). Validate with Pydantic. Compute `record_completeness`. Set `data_provenance_score = 0.0`. Set `last_updated` to UTC ISO 8601.
- `update()` — Run 5 consistency checks before applying. Preserve old values in `revision_history`. Recalculate `record_completeness`.
- `_next_canonical_id()` — Scan registry for highest existing ID, increment.
- `_compute_record_completeness()` — 24 biographical fields fraction.

**Storage:** `library/registries/scholars.json`. Use `filelock` for locking. Use atomic write pattern (temp file → fsync → os.replace).

**Important:** The old `__init__.py` tracer stub is imported by `shared/scholar_authority/tests/test_name_matching.py` (4 tests use `from shared.scholar_authority.src import clear, lookup, register`). The tracer stub API differs from the new module:
- Old: `register(name: str, record: dict) → str`
- New: `register(record: ScholarAuthorityRecord) → ScholarAuthorityRecord`
- Old: `lookup(name: str, death_date: int | None = None) → Optional[dict]`
- New: `lookup(name, death_date_hijri, ...) → ScholarMatchResult`
- Old: `clear()` — resets in-memory dict

After creating `scholar_authority.py`, update `__init__.py` to re-export the new public API (`lookup`, `register`, `update`, `get_all`, `ScholarMatchResult`, `compute_scholar_match_score`). The 4 existing integration tests in `test_name_matching.py` that use the old API must be **rewritten** to use the new API — they test name matching within the context of lookup/register, which is now handled differently. Alternatively, add backward-compatible wrappers in `__init__.py`, but rewriting is preferred since the old tests are simple.

**Test:** `shared/scholar_authority/tests/test_scholar_authority.py` (20 tests)

### Module 3: `shared/human_gate/src/human_gate.py` (~150 lines)
Replace the tracer stub.

Implement:
- `create_checkpoint()` — Generate `hg_{uuid4_hex[:8]}` ID. Persist to `library/gates/pending/{source_id}.json` (list of checkpoints per source). Update `library/gates/index.json`. If `auto_approve=True`, set status to `auto_approved` immediately (SAME code path as real review).
- `resolve()` — Update checkpoint status. Move from pending/ to resolved/ on approve/reject. On `unsure`: set status to `elevated` (Layer 3.5 placeholder for future sessions).
- `get_pending()` — Read all files in pending/, filter by source_id if provided.
- `get_checkpoint()` — Look up in index.json, read from pending or resolved.
- `get_pending_count()` — Sum checkpoints across all pending files.
- `configure()` — Set gates_dir and auto_approve mode.

**Persistence format (pending/{source_id}.json):**
```json
[
  {
    "checkpoint_id": "hg_1a2b3c4d",
    "source_id": "src_abc12345",
    "trigger": "author_disambiguation",
    ...
  }
]
```

**Critical:** Auto-approve must use the SAME code path. Create the checkpoint, persist it, then immediately resolve it with decision="approve". This ensures the real workflow is tested.

**Test:** `shared/human_gate/tests/test_human_gate.py` (8 tests)

### Module 4: `shared/validation/src/validation.py` (~100 lines)
Replace the tracer stub.

Implement 3 generic functions:
- `validate_schema()` — `schema.model_validate(data)`, catch `PydanticValidationError`, convert to `list[ValidationError]`.
- `validate_referential_integrity()` — For each `(field_path, registry_name)`, resolve nested field path in data, check it exists in `registries[registry_name]`.
- `validate_enrichment_passthrough()` — Compare `before` and `after` dicts. Any key in `before` that was non-null and is now null or missing in `after` → `SRC_INVALID_ENRICHMENT`.

**Test:** Tested as part of `engines/source/tests/test_validation.py` (tests 34-36, 49-50)

### Module 5: `engines/source/src/trust_evaluator.py` (~200 lines)
Replace the stub.

Implement `evaluate_trust()` with 5 sub-functions:
- `_score_author_standing()` — **Use the VALIDATED formula, NOT the SPEC §4.A.8 text.** death_date ≤ 1000 → 0.90 (classical); death_date > 1000 → 0.70 (post-classical); death_date None → 0.30 (unknown). See "SPEC Defect Fix" section above and the trust_evaluator.py stub docstring.
- `_score_tahqiq_quality()` — Check muhaqiq name against recognized_muhaqiqs list using `normalized_name_similarity >= 0.85`. Recognized → 0.90. Unknown → 0.50. No muhaqiq + pre-modern (≤1300) → 0.40. No muhaqiq + unknown death → 0.35. No muhaqiq + modern (>1300) → 0.30.
- `_score_publisher_reputation()` — Check publisher name AND all variants using substring matching. Known → configured score. Unknown → 0.40.
- `_score_source_authority()` — primary → 0.85, reference → 0.60, modern_compilation → 0.40.
- `_score_text_fidelity()` — high → 0.90, medium → 0.60, low → 0.30, unknown → 0.40.

Combined score = Σ(factor_weight × factor_score). Tier: ≥ 0.65 → verified; < 0.65 → flagged. Also flagged if author_standing < 0.30 AND tahqiq_quality < 0.40.

**Critical verification:** Run against ALL 13 fixtures using GROUND_TRUTH.json expected_trust values. All 13 must match. This was validated in Step 2 — the implementation just needs to reproduce the validated algorithm.

**Test:** `engines/source/tests/test_trust_evaluator.py` (13 tests)

### Module 6: `engines/source/src/validation.py` (~250 lines)
Replace the stub.

Implement `validate_source_metadata()` calling all 6 checks in order:
1. `validate_schema(data, SourceMetadata)` — delegated to shared
2. `validate_referential_integrity(data, registries, [...])` — delegated to shared
3. `_check_confidence_thresholds(data)` — author, genre, science_scope < 0.50 → gate
4. `_check_duplicates(data, registries)` — post-inference dedup (warning only)
5. `_check_consistency(data, registries, prior_sources)` — 5 sub-checks:
   - 5a: nazm→verse, sharh→commentary|prose, hashiyah→commentary
   - 5b: hashiyah should not be beginner
   - 5c: author↔science scope mismatch → HUMAN GATE (only consistency check that gates)
   - 5d: attribution_status vs prior sources → warning
   - 5e: sharh/hashiyah must be multi-layer → auto-correct
6. `_check_multi_layer_coherence(data, registries)` — 3 sub-checks:
   - 6a: multi_layer=true + empty layers → gate
   - 6b: multi_layer=false + has layers → auto-correct
   - 6c: layer author refs resolve in scholars

**Important for Check 5e → 6 chain:** When auto-correcting `is_multi_layer` from false to true in Check 5e, the data dict is modified in-place. Then Check 6 verifies `text_layers` is non-empty. If the LLM identified genre as sharh but produced no layers, Check 6a triggers a human gate.

**Test:** `engines/source/tests/test_validation.py` (17 tests)

---

## What NOT to Build

- **Registries (source/work/scholar CRUD)** — Session 5b
- **Registration orchestrator** — Session 5b
- **engine.py pipeline orchestrator** — Session 6
- **logger.py** — Session 6
- **Work relationship tracking** — Session 5b
- **Source-engine human_gate wrapper** (`engines/source/src/human_gate.py`) — Session 5b

---

## Done When

- [ ] **contracts.py updated:** `HumanGateCheckpoint.resolved` → `status` field, existing tests updated
- [ ] **Config:** `load_config()` loads all 4 JSON files, returns typed `SourceEngineConfig`
- [ ] **Scholar authority lookup:** Finds existing records with correct thresholds (≥0.85 auto-link, 0.50–0.85 gate, <0.50 new)
- [ ] **Scholar authority lookup:** Short-vs-long name (A3-1): "النووي" vs full name scores ≥0.85 → auto_link
- [ ] **Scholar authority lookup:** Ambiguous "ابن حجر" without death date → human_gate zone
- [ ] **Scholar authority register:** Creates records with sequential IDs (sch_00001, sch_00002, ...)
- [ ] **Scholar authority update:** 5 consistency checks all tested:
  - Death date drift > 5 years → gate
  - School affiliation change → gate
  - Name change → blocked (added to known_as)
  - Self-reference → rejected
  - Temporal inconsistency → gate
- [ ] **Scholar authority update:** Preserves old values in revision_history
- [ ] **Scholar authority:** record_completeness correctly computed (24-field fraction)
- [ ] **Human gate:** Checkpoints persist to `library/gates/pending/{source_id}.json`
- [ ] **Human gate:** Auto-approve mode creates + immediately resolves (same code path)
- [ ] **Human gate:** `get_pending()` returns correct checkpoints filtered by source_id
- [ ] **Human gate:** `resolve()` moves checkpoint from pending/ to resolved/
- [ ] **Shared validation:** Schema compliance catches missing required fields
- [ ] **Shared validation:** Referential integrity catches broken canonical_id references
- [ ] **Shared validation:** D-023 passthrough catches deleted upstream fields
- [ ] **Trust evaluation:** 13/13 fixtures match GROUND_TRUTH.json expected_trust
- [ ] **Trust evaluation:** 5 factors computed with correct weights (0.30, 0.25, 0.15, 0.15, 0.15)
- [ ] **Trust evaluation:** Threshold 0.65 for verified/flagged boundary
- [ ] **Trust evaluation:** Classical scholar cutpoint at 1000 AH (not 900)
- [ ] **Trust evaluation:** First-intake formula uses ONLY death_date (NOT prior-sources check — see SPEC Defect Fix section)
- [ ] **Trust evaluation:** Recognized muhaqiq matching uses name_matching (not exact string compare)
- [ ] **Trust evaluation:** Publisher variant matching via substring
- [ ] **Source validation:** All 6 Layer 1 checks implemented
- [ ] **Source validation:** Genre↔multi-layer auto-correction (Check 5e) chains to Check 6
- [ ] **Source validation:** Author↔science mismatch triggers human gate (only consistency check that gates)
- [ ] **Source validation:** Multi-layer + empty layers → gate (prevents T-2 attribution error)
- [ ] **All new tests pass** (target: ~70 new tests + 365 existing = ~435 total)

---

## API Keys

Not needed for Session 5a. All modules are deterministic — no LLM calls.

---

## Build Tips

1. **Start with config.** Every other module reads config. Get it working first.
2. **Then scholar_authority.** The trust evaluator and validation both depend on scholar records.
3. **Then human_gate.** The scholar authority update() creates gate checkpoints.
4. **Then trust_evaluator.** Uses config (muhaqiqs, publishers) + scholar records.
5. **Then shared validation.** Generic functions.
6. **Last: source validation.** Composes all the above.
7. **Test each module before moving to the next.** Don't write all 6 then test — you'll hit cascading failures.
