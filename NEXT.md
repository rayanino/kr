# NEXT — Source Engine Step 3: BUILD

**Session type:** BUILD — implementing the source engine
**Goal:** Build the source engine from SPEC_CORE.md, starting with the staging pipeline and format detection.

---

## Context

Step 1 (SPEC hardening) and Step 2 (LLM assumption testing) are both complete. All assumptions validated. The consensus pair (Command A + Opus 4.6) is selected. The inference prompt (inference_v1.py draft-3) is locked. Build begins now.

**Key results from Step 2:**
- All 5 models achieve 100% JSON parse rate and 0 enum violations
- Multi-layer detection: 100% accuracy across all models
- Consensus pair: Command A (Cohere) + Opus 4.6 (Anthropic), 92.3% coverage
- Re-scored model aggregates (with corrected name scoring): Opus 0.890, Command A 0.883, GPT-5.4 0.873, Mistral 0.863, Gemini 0.788

**Step 2 Summary (evaluated in `engines/source/review/STEP2_EVALUATION.md`):**
- A1 (JSON reliability): 100% parse, 0 enum violations across 6 models. Single-call prompt confirmed.
- A2 (Multi-layer detection): 100% accuracy across 5 production models.
- A3 (Name matching): Partially validated. KNOWN ISSUE: substring containment boost needed (A3-1).
- A4 (Trust weights): 13/13 correct at threshold 0.65 (uniquely optimal). 900→1000 AH cutpoint resolved.
- A5 (Consensus pair): Command A (Cohere) + Opus 4.6 (Anthropic). 92.3% "at least one right". Fallback: GPT-5.4 + Opus 4.6.

**Two mandatory build-phase tasks from Step 2:**
1. **Confidence calibration analysis** — extract confidence scores from Step 2 results, check correlation with accuracy. If models produce >0.90 on wrong answers, raise thresholds.
2. **Name matching substring boost** — implement A3-1 fix in `normalized_name_similarity`.

## Build Strategy

The source engine is built in sessions, each tackling one SPEC section. One session = one focused implementation block. Use `/smart-compact` proactively. Re-read SPEC_CORE.md section before implementing.

### Session 1: Staging Pipeline + Format Detection (§4.A.2)

**Read first:** SPEC_CORE.md §4.A.2 (Step 1: Staging, Step 2: Format Detection)

**Build:**
1. `engines/source/src/staging.py` — File staging: copy to staging area, compute SHA-256, generate source_id
2. `engines/source/src/format_detection.py` — Detect Shamela HTML vs plain text (2 Stage 1 formats)
3. Tests: `engines/source/tests/test_deterministic.py` — staging + format detection against real fixtures

**Contracts used:** `AcquisitionPath`, `SourceFormat`, `ProcessingStatus.STAGING`

### Session 2: Shamela HTML Extraction (§4.A.3)

**Read first:** SPEC_CORE.md §4.A.3, `reference/SHAMELA_FORMAT_ANALYSIS.md`

**Build:**
1. `engines/source/src/extractors/shamela_html.py` — Parse بطاقة الكتاب metadata card, extract title, author, publisher, muhaqiq, page count
2. `engines/source/src/extractors/plain_text.py` — Minimal extraction from plain text files
3. Tests against all 12 Shamela fixtures + 1 plain text fixture (alfiyyah_versified)

**Contracts used:** `FormatSpecificMetadata`, extraction-related fields in `SourceMetadata`

### Session 3: LLM Inference Integration (§4.A.4)

**Read first:** SPEC_CORE.md §4.A.4, `prompts/inference_v1.py`, consensus-pattern skill

**Build:**
1. `engines/source/src/inference.py` — Multi-model consensus using Command A + Opus 4.6
2. Uses the validated prompt template from inference_v1.py
3. Uses Instructor + LiteLLM for structured output (see `.claude/skills/consensus-pattern/SKILL.md`)
4. Human gate fallback when models disagree
5. Tests: `engines/source/tests/test_llm_inference.py` — against 3+ fixtures with mocked responses

**Contracts used:** Full `InferenceOutput` model, `InferredFieldConfidence`

### Session 4: Identity Assignment + Dedup (§4.A.5, §4.A.6)

**Build:**
1. `engines/source/src/identity.py` — Three-tier ID (source_id, work_id, canonical_id)
2. `engines/source/src/dedup.py` — Composite key duplicate detection
3. Scholar name matching using normalized comparison

### Session 5: Trust Evaluation + Freeze (§4.A.8, §4.A.7)

**Build:**
1. `engines/source/src/trust.py` — 5-factor trust scoring (threshold 0.65)
2. `engines/source/src/freeze.py` — Freeze raw source, write metadata.json
3. Final output: complete SourceMetadata record for normalization engine

### Session 6: Pipeline Orchestration + Integration Tests

**Build:**
1. `engines/source/src/pipeline.py` — Orchestrate all steps: stage → detect → extract → infer → identify → dedup → trust → freeze
2. End-to-end integration test: feed a real fixture through the full pipeline
3. Verify output matches normalization engine's input contract

---

## What to Read First

1. `NEXT.md` (this file)
2. `engines/source/CLAUDE.md` — engine state + canonical examples
3. `engines/source/SPEC_CORE.md` — the relevant section for the current session
4. `engines/source/contracts.py` — Pydantic schemas
5. `/KNOWLEDGE_INTEGRITY.md` — corruption threats to prevent

---

## Critical Rules for Build

1. **Multi-model consensus for ALL content decisions** (D-041). Use the consensus-pattern skill. Never single-LLM calls for genre, author, science_scope, multi-layer.
2. **Metadata flows forward, never deleted** (D-023). Every function that transforms data must pass through ALL upstream metadata fields.
3. **Arabic text is fragile.** Check the arabic-text skill before writing any text processing code.
4. **Real fixtures in all tests.** Use tests/fixtures/ data, never synthetic English text.
5. **Fail loud** (D-033). Raise specific exceptions, never silently drop data.
6. **Frozen sources are immutable.** Once SHA-256 hash is computed, bytes never change.
7. **The muhaqiq is NOT the author.** Always store them separately.

---

## Done When

- [ ] Session 1: Staging + format detection implemented and tested
- [ ] Session 2: Shamela HTML + plain text extraction implemented and tested
- [ ] Session 3: LLM inference with consensus integrated and tested
- [ ] Session 4: Identity assignment + dedup implemented and tested
- [ ] Session 5: Trust evaluation + freeze implemented and tested
- [ ] Session 6: Full pipeline orchestrated + integration tests pass
- [ ] All [ASSUMPTION] markers removed from SPEC_CORE.md
- [ ] Output passes `python3 scripts/verify_metadata_flow.py`
