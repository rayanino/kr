# Source Engine — Strategic Plan (Steps 2→4 + Handoff)

**Created:** 2026-03-09
**Scope:** From Step 2 evaluation through source engine completion and normalization engine handoff
**Status:** Active — start Phase A when Claude Code finishes Step 2

---

## Overview

The source engine has 4 steps. Step 0 (tracer bullet) and Step 1 (SPEC hardening) are complete. Step 2 (LLM assumption testing) is running in Claude Code. This plan covers everything from evaluating Step 2 results through completing the source engine and starting the normalization engine.

**Estimated total:** 10-14 sessions across Phases A-E, depending on core gaps found in Phase D.

---

## Phase A: Evaluate Step 2 Results

**Who:** Claude Chat (1 session)
**Skill:** `use kr-evaluate`
**Input:** Claude Code's Step 2 output in `tests/results/`

### Work

1. **Categorize every finding** using kr-evaluate's taxonomy: CORE GAP / ENGINE BUG / LLM QUALITY / DATA ISSUE / EXTENSION OPPORTUNITY / LESSON LEARNED / EVALUATOR NOISE.

2. **Make 5 binding architectural decisions:**

   **Decision 1 — Single-call or split prompt?** If JSON parse rate ≥95% across models with the single-call schema (42 fields), keep it. If below 95%, split into two calls: classification fields in call 1, scholarly_context in call 2. This changes consensus architecture and cost model.

   **Decision 2 — Which consensus pair?** Select the pair that maximizes "at least one got it right" rate across fixtures. Check specifically that the pair has complementary error profiles on author identification (weight 0.30). A pair that agrees on everything provides no consensus value.

   **Decision 3 — Confidence threshold calibration.** SPEC says 0.70 → needs_review, 0.50 → blocks write. Step 2 reveals what confidence scores models actually produce. If models output 0.85+ even when wrong, raise thresholds. If appropriately calibrated, keep SPEC values.

   **Decision 4 — Multi-layer detection reliability.** SPEC assumes ≥90% accuracy. If below 85%, add mandatory human gate for every multi-layer/single-layer decision. This adds a checkpoint type to human_gate design.

   **Decision 5 — SPEC updates needed?** If any pipeline-critical field (genre, author, is_multi_layer) is unreliable, scrutinize SPEC fallback paths.

3. **Resolve the 900 AH cutpoint.** Raise to 1000 AH. Evidence: al-Suyuti (d. 911 AH) is fixture 11, one of the most recognized scholars in Islamic history. The 900 cutpoint misclassifies him as non-classical, giving author_standing = 0.70 instead of 0.90.

4. **Decide attribution_status testing gap.** All 13 fixtures are "definitive" — the directed comparison mechanism can't be tested. Decision: document as known limitation, defer to Step 4 empirical testing on the owner's full 2,519-book Shamela collection, which almost certainly includes works with contested attribution.

5. **Resolve all ASSUMPTION markers** in SPEC_CORE.md with evidence from Step 2 results. There are 9 markers; A3, A4, and the readiness verification are already resolved. The remaining ones (A1 JSON reliability, A2 multi-layer, A5 consensus, attribution_status comparison, 900 AH cutpoint) should all have data from Step 2.

### Output Artifacts

| File | Purpose |
|------|---------|
| `engines/source/review/STEP2_EVALUATION.md` | Categorized findings, 5 decisions with evidence |
| `engines/source/SPEC_CORE.md` | ASSUMPTION markers resolved |
| `engines/source/prompts/inference_v1.py` | Finalized prompt (or `inference_v2_split.py` if split) |
| `NEXT.md` | Rewritten for Step 3 scope |
| `OPEN_PROBLEMS.md` | Updated to reflect Steps 0-2 complete |
| Handoff doc per `skills/shared/HANDOFF_PROTOCOL.md` | Context for build prep session |

---

## Phase B: Build Prep

**Who:** Claude Chat (1 session)
**Skill:** `use kr-build-prep`
**Input:** Finalized SPEC_CORE.md, contracts.py, validated prompt template

### Work

1. **Technology survey.** Verify stack decisions:
   - BeautifulSoup4 + lxml → Shamela HTML parsing
   - hashlib → SHA-256 freezing (stdlib)
   - LiteLLM + Instructor → LLM inference via OpenRouter
   - Pydantic → schema validation (contracts.py exists)
   - Research: PyArabic vs CAMeL Tools for Arabic name normalization. The eval harness has a basic `normalize_arabic_name()` — determine if it's production-quality or needs replacement.
   - Verify: does Instructor's structured output mode work with all models in the validated consensus pair?

2. **Deferred code quarantine.** The `engines/source/src/` directory has 28 Python files. Only ~19 are core. The following must be explicitly excluded from the build (moved to `src/_deferred/` or marked in CLAUDE.md):
   - Extractors: `pdf.py`, `image.py`, `word.py`, `owner_authored.py`
   - Modules: `citation_discovery.py`, `gap_analysis.py`, `openiti_enrichment.py`, `enrichment.py`
   - Step 0 artifact: `tracer.py`

3. **Shared component requirements.** Produce `shared/{component}/REQUIREMENTS_source.md` for each of 4 components. METHOD SIGNATURES from ENGINE_PROTOCOL:
   - `consensus.evaluate(task, models, threshold) → {agreed, result, scores}`
   - `human_gate.create_checkpoint(source_id, reason, context) → checkpoint_id`
   - `human_gate.resolve(checkpoint_id, decision)`
   - `scholar_authority.lookup(name) → Optional[ScholarRecord]`
   - `scholar_authority.register(record)`
   - `validation.validate_output(data, schema) → list[ValidationError]`

   **Critical:** Cross-check these against what the normalization engine will need. Normalization uses `validation` heavily (§5 Layer 1 checks) and `scholar_authority` for layer attribution. Design shared interfaces to be reusable by both engines without rebuild.

4. **Resolve trust evaluation tension.** ENGINE_PROTOCOL says "keep trust simple — 3-tier classification." SPEC_CORE has the full 5-factor weighted algorithm, empirically validated in Step 2 (A4: 13/13 PASS). **Resolution: SPEC_CORE wins.** It's the behavioral authority after 8 hardening passes. ENGINE_PROTOCOL was general guidance written before validation. Document this decision explicitly so Claude Code doesn't get confused by contradictory guidance.

5. **Architecture doc** mapping the 9-step acquisition pipeline to modules.

6. **Session plans** — one per build session, narrow scope, following the SPEC's pipeline order (staging → format detection → extraction → inference → dedup → freezing → registration → trust → handoff).

### Output Artifacts

| File | Purpose |
|------|---------|
| `engines/source/docs/architecture.md` | Module structure, 9-step pipeline mapping |
| `engines/source/docs/technology-inventory.md` | Use/build/test decisions |
| `shared/consensus/REQUIREMENTS_source.md` | What source engine needs from consensus |
| `shared/human_gate/REQUIREMENTS_source.md` | What source engine needs from human_gate |
| `shared/scholar_authority/REQUIREMENTS_source.md` | What source engine needs from scholar_authority |
| `shared/validation/REQUIREMENTS_source.md` | What source engine needs from validation |
| Updated `engines/source/CLAUDE.md` | Build instructions, deferred file list |
| `engines/source/session-{1-6}-plan.md` | Per-session build plans |

---

## Phase C: Build

**Who:** Claude Code (5-6 sessions)
**Input:** Build prep artifacts, session plans

Sessions follow the SPEC's 9-step acquisition workflow order. Each session ends with committed code, passing tests, and an updated NEXT.md for the next session.

### Session 1: Pipeline Steps 1-3 (Staging + Format Detection + Extraction)

**Scope:** Staging intake, format detection (`shamela_html` and `plain_text` only), Shamela HTML metadata extraction via BeautifulSoup4.

**Fixture:** `tests/fixtures/shamela_real/01_nahw_simple/book.htm` (single-volume Shamela)

**Note on .claudeignore:** The `tests/fixtures/` directory is in `.claudeignore` to save context. Claude Code must be told the exact fixture paths in the session plan — it won't discover them through codebase exploration.

**Done when:** Extracted metadata dict matches contracts.py field names. Schema validation passes. Arabic text integrity preserved (diacritics byte-for-byte). Error paths for missing files, empty input, unsupported format exercised.

### Session 2: Pipeline Step 4 (LLM Metadata Inference)

**Scope:** Wire the validated prompt template into the pipeline via LiteLLM + Instructor. Build the consensus wrapper (shared/consensus MVP). Map LLM output fields to SourceMetadata:
- `layers` → `text_layers`
- `author_identification.canonical_name_ar` → `ScholarReference` construction
- Top-level confidence fields → `InferredFieldConfidence`

**Fixtures:** 01_nahw_simple, 06_usul, 11_multi_small (diverse: simple, well-known author, multi-layer)

**Done when:** LLM inference produces valid SourceMetadata fields. Consensus returns agreed/disagreed results. Confidence scores populate InferredFieldConfidence.

### Session 3: Pipeline Steps 5-6 (Hashing + Dedup + Freezing)

**Scope:** SHA-256 hashing, composite key computation, source_id derivation (§4.A.1), duplicate detection (§4.A.7), freezing (copy to `library/sources/{source_id}/frozen/` + verify hashes).

All deterministic, no LLM involvement.

**Fixtures:** Multiple (hash same fixture twice to test dedup, hash different fixtures to verify uniqueness).

**Done when:** Frozen files are byte-identical to originals. Composite hashes are deterministic. Duplicate detection catches exact duplicates and rejects them. source_id derivation is correct.

### Session 4: Pipeline Step 7 (Registration + Scholar Authority)

**Scope:** Scholar authority MVP (`lookup` + `register`), work registry, source registry. Atomic write-ahead log for registry updates (§4.A.2 Step 7). Three-tier identity assignment: source_id (from hash), work_id (from author+title), canonical_id (from scholar matching).

Builds 2 shared components: scholar_authority, work_registry.

**Fixtures:** All 13 — registration should work for every fixture.

**Done when:** All three registries populated correctly. Scholar records created with correct fields. Work-to-source mapping correct. Write-ahead log written and cleaned up on success.

### Session 5: Pipeline Step 8 (Trust Evaluation + Human Gate + Validation)

**Scope:** Full 5-factor trust evaluation algorithm from SPEC §4.A.8 (NOT the simplified ENGINE_PROTOCOL version — see Phase B decision). Human gate MVP (`create_checkpoint` + `resolve`). Validation MVP (`validate_output`). Wire confidence thresholds to gate triggers (< 0.70 → needs_review, < 0.50 → blocks write).

Builds 3 shared components: human_gate, validation, trust evaluation logic.

**Fixtures:** All 13 — trust scores should match GROUND_TRUTH.json `expected_trust` values.

**Done when:** Trust scores computed correctly. Human gate checkpoints created for low-confidence fields. Validation catches schema violations. Trust re-evaluation path exists (for enrichment updates).

### Session 6: Pipeline Step 9 (Integration + Plain Text + Error Paths)

**Scope:** Full pipeline run on all 13 fixtures. Plain text extractor for `alfiyyah_versified`. All error paths from SPEC §7 exercised. Verify deferred error codes don't fire. End-to-end: staging directory → complete SourceMetadata + frozen files + registry entries.

**Done when:** All 13 fixtures produce valid SourceMetadata. All SPEC §7 error codes that CAN fire in core are tested. Pipeline orchestrator (`engine.py`) coordinates all 9 steps correctly.

---

## Phase D: Test and Prove

**Who:** Claude Code (runs tests) + Claude Chat (evaluates findings, uses kr-evaluate) + Owner (sanity check)
**Sessions:** 2-3

### Claude Code Work
- Run full 5a/5b/5c test suite on all fixtures
- Create gold baselines: `engines/source/tests/gold_baselines/{fixture}.json`
- Fix core gaps identified during evaluation
- Re-test until clean

### Claude Chat Work (kr-evaluate)
- Categorize every finding: CORE GAP / EXTENSION OPPORTUNITY / LESSON LEARNED
- Critical distinction: "would the pipeline produce wrong knowledge entries without this?" → core gap. Otherwise → extension opportunity.
- Verify 5a = 100% pass, 5b ≥ 90% accuracy, 5c findings are not real errors

### Owner Work (10-15 minutes)
Experiential sanity check on recognizable fixtures:
- "Is this the right book?"
- "Is this the right author?"
- "Does this text look like what you uploaded?"
- "Does this entry seem useful for your study?"
- "I'm not sure" is valid — triggers deeper automated verification

### Done When
- All 5a deterministic checks pass
- 5b LLM-worker accuracy ≥ 90%
- 5c independent review finds no errors self-validation missed
- Owner sanity check passed
- All core gaps fixed
- Lessons and extension opportunities documented in `engines/source/LESSONS.md`

---

## Phase E: Pipeline Integration + Handoff

**Who:** Claude Code (1 session)

1. Feed source engine output into normalization engine's tracer bullet stub
2. Run `scripts/run_pipeline.py` from source output through remaining stubs
3. Verify contract boundary holds with real (not mocked) data
4. Fix any contract mismatches
5. Document lessons in `engines/source/LESSONS.md`
6. Update `OPEN_PROBLEMS.md` — source engine complete, normalization engine next

**Done when:** Source engine output feeds into normalization stub without errors. Contract boundary verified with real data. Then begin normalization engine Step 1.

---

## Known Issues and Decisions

### Resolved

| Issue | Resolution | Evidence |
|-------|-----------|----------|
| 900 AH classical scholar cutpoint | Raise to 1000 AH | al-Suyuti (d. 911, fixture 11) is unambiguously classical |
| Trust evaluation: ENGINE_PROTOCOL vs SPEC_CORE | SPEC_CORE wins (full 5-factor algorithm) | Empirically validated: A4 13/13 PASS at threshold 0.65 |
| Attribution_status testing gap | Known limitation for Step 2; test empirically in Step 4 | All 13 fixtures are "definitive"; owner's full collection (2,519 books) will have disputed works |
| Deferred module confusion risk | Quarantine deferred stubs during build prep | 9 of 28 src/ files are deferred; explicit exclusion list needed |

### Pending (Decided in Phase A)

| Issue | Decision Criteria |
|-------|------------------|
| Single-call vs split prompt | JSON parse rate ≥95% → keep single-call |
| Consensus pair selection | Maximize complementary error profiles on author identification |
| Confidence threshold calibration | Do models produce appropriately calibrated scores? |
| Multi-layer detection reliability | ≥85% → trust LLM; <85% → mandatory human gate |
| SPEC updates needed | Determined by Step 2 accuracy on pipeline-critical fields |

---

## Context Budget Note

SPEC_CORE.md is ~36K tokens. contracts.py is ~11K tokens. Together they consume ~47K tokens of Claude Code's context. During build sessions, Claude Code should NOT read the full SPEC — the session plans and architecture doc extract the relevant sections. SPEC_CORE.md should be referenced for specific section lookups, not loaded whole.

---

## File Index

Files a future session needs to find:

| What | Where |
|------|-------|
| This plan | `engines/source/STRATEGIC_PLAN.md` |
| Current task directive | `NEXT.md` (rewritten each phase) |
| SPEC (behavioral authority) | `engines/source/SPEC_CORE.md` |
| Schema (data authority) | `engines/source/contracts.py` |
| Inference prompt | `engines/source/prompts/inference_v1.py` |
| Step 2 results | `tests/results/` |
| Step 2 readiness verification | `tests/STEP2_READINESS_VERIFICATION.md` |
| Scoring criteria | `tests/SCORING_CRITERIA.md` |
| Eval harness | `tests/eval_harness.py` |
| Ground truth | `tests/fixtures/GROUND_TRUTH.json` |
| Extracted fixture data | `tests/fixtures/EXTRACTED_DATA.json` |
| Raw Shamela fixtures | `tests/fixtures/shamela_real/` |
| Plain text fixture | `tests/fixtures/alfiyyah_versified/alfiyyah.txt` |
| Engine protocol | `skills/shared/ENGINE_PROTOCOL.md` |
| Handoff protocol | `skills/shared/HANDOFF_PROTOCOL.md` |
| Build prep skill | `skills/kr-build-prep/` |
| Evaluate skill | `skills/kr-evaluate/` |
| Shamela format analysis | `reference/SHAMELA_FORMAT_ANALYSIS.md` |
| Corruption threats | `KNOWLEDGE_INTEGRITY.md` |
| Project roadmap | `OPEN_PROBLEMS.md` |
