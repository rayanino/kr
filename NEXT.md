# NEXT — Source Engine Step 2: LLM Research & Prompt Engineering

**Session type:** RESEARCH — empirical testing of LLM assumptions
**Goal:** Validate or revise the 5 [ASSUMPTION] markers in SPEC_CORE.md through real API calls against real fixtures.

---

## Context

Step 1 (SPEC hardening) is locked after 6 review passes. The SPEC's deterministic components (extraction, hashing, dedup, trust arithmetic, validation) have been verified against all 12 real fixtures. What remains untested is everything that involves LLM inference: structured output, genre classification, author identification, multi-layer detection, and multi-model consensus.

---

## IMPORTANT: Test Design Before Testing

Before making any API calls, the new session must:

### 1. Validate ground truth with the owner
`tests/fixtures/GROUND_TRUTH.json` contains expected correct answers, but 5 values are marked `_uncertain` and the rest were assigned by a non-specialist. The owner IS an Islamic studies student — ask him to validate or correct:
- Genre classifications for all 13 fixtures (especially 01, 05, 07, 10, 12)
- Multi-layer classification for fixture 05 (تعقبات على الجلالين)
- Science scope for fixture 12 (مالك بن نبي memoirs)
- Whether any fixtures need different expected values

### 2. Define scoring criteria precisely
For each field the LLM outputs, define what counts as correct:
- `genre`: exact enum match? Or is `sharh` acceptable when ground truth says `hashiyah`?
- `science_scope`: exact set match? Subset acceptable? Superset acceptable?
- `author_identification`: name match threshold? Death date within how many years?
- `is_multi_layer`: boolean exact match
- `structural_format`: exact enum match

### 3. Check fixture coverage for each assumption
- A1 (JSON reliability): 6 fixtures is fine
- A2 (multi-layer): only 1 confident multi-layer fixture (11). Is that enough? Can we add a known hashiyah? Are there sharh fixtures in the owner's collection we could add?
- A3 (name matching): deterministic — no fixtures needed, just test pairs
- A4 (trust weights): all 13 fixtures have expected trust tiers
- A5 (consensus): need enough fixtures to measure meaningful agreement rates

### 4. Build the evaluation harness
Write the scoring script BEFORE the first API call so results are automatically evaluated. This prevents subjective "close enough" judgments.

---

## The 5 Assumptions to Test

### A1: LLM Structured JSON (§4.A.4, line ~825)
**Claim:** LLM produces the full inference output schema reliably.
**Test:** Send the inference prompt to each model with extracted metadata + text_sample for ≥6 fixtures. Measure JSON parse success, enum compliance, field completeness.
**Fixtures:** 01_nahw_simple, 03_fiqh, 06_usul, 08_death_date, 11_multi_small, alfiyyah_versified
**If fails:** Simplify schema, add few-shot examples, or split into multiple calls.

### A2: Multi-Layer Detection (§4.A.4, line ~850)
**Claim:** LLM detects multi-layer composition ≥90% from genre + title + content.
**Test:** Check is_multi_layer and layers output for fixtures with known answers.
**Fixtures:** 11_multi_small (sharh → TRUE), 03_fiqh (standalone → FALSE), alfiyyah (matn → FALSE), 05_tafsir (UNCERTAIN — resolve with owner first)
**If fails (<85%):** Add human gate for multi-layer classification.

### A3: Scholar Name Matching (§4.A.5, line ~952)
**Claim:** normalized_name_similarity scoring produces correct match/no-match decisions.
**Test:** Run the utility functions (defined in SPEC §4.A.1) on name pairs. Deterministic — no LLM needed.
**If fails:** Adjust normalization rules or thresholds.

### A4: Trust Weight Calibration (§4.A.8, line ~1013)
**Claim:** Weights and 0.65 threshold produce correct verified/flagged assignments.
**Test:** Compute trust scores for each fixture using the 5-factor algorithm. Compare against ground truth expected_trust.
**If fails:** Adjust weights or threshold.

### A5: Two-Model Consensus (§6, line ~1205)
**Claim:** Two different-provider models catch more author identification errors than one.
**Test:** Run the same inference prompt through multiple models. Compare author identification accuracy per-model and in pairs.
**If fails:** Add third model, tighten human gate thresholds, or change pair.

---

## Strategic Approach (4 phases)

### Phase 0: Test Design (NO API calls)
1. Get owner validation of ground truth (genre, multi-layer, science_scope)
2. Define exact scoring criteria for each field
3. Assess fixture coverage gaps, potentially add fixtures
4. Build automated evaluation harness
5. Validate A3 (name matching) and A4 (trust weights) — these are deterministic, need no LLM

### Phase 1: Prompt Engineering (Anthropic — Claude Sonnet 4.6)
Use `claude-sonnet-4-6` via Anthropic direct API for fast, cheap iteration on prompt structure.
1. Draft the inference prompt from SPEC §4.A.4 requirements
2. Run against 6 diverse fixtures, auto-score results
3. Iterate until JSON parse rate ≥95%, enum compliance ≥95%
4. Sonnet is correct here: we're testing prompt quality, not model capability. If the prompt works on Sonnet, it works better on Opus.

### Phase 2: Multi-Model Accuracy (strongest tier from each provider)
Run the validated prompt through the STRONGEST model from each provider.
**Rationale:** Production will use the strongest models. Testing weaker models would give misleading accuracy/agreement numbers.

**Models (verified available):**
- `claude-opus-4-6` (Anthropic direct) — strongest Claude
- `openai/gpt-5.4` (OpenRouter) — strongest GPT. Note: the direct OpenAI key only has GPT-4o; GPT-5.x requires OpenRouter.
- `google/gemini-3.1-pro-preview` (OpenRouter) — strongest Gemini, very strong multilingual
- `mistralai/mistral-large-2512` (OpenRouter or Mistral direct key) — strongest Mistral
- `cohere/command-a` (OpenRouter) — Cohere's strongest

**Cost estimate:** ~3500 input tokens per fixture × 13 fixtures × 5 models = ~230K tokens. At strongest-tier pricing, total ≈ $2-5. Cost is not a constraint.

For each model, measure on all 13 fixtures:
- JSON parse success rate
- Per-field accuracy vs ground truth
- Author identification accuracy
- Multi-layer detection accuracy

### Phase 3: Consensus Pair Selection
Pick the pair that maximizes "at least one got it right" rate.
Run full consensus flow on all fixtures with the production-tier pair.

---

## Pre-built Resources

**`tests/fixtures/EXTRACTED_DATA.json`** — Pre-extracted metadata and text samples for all 13 fixtures. Each entry has `prompt_context` (formatted metadata string) and `text_sample` (2000 chars of body text). Run `python3 scripts/extract_fixtures.py` to regenerate.

**`tests/fixtures/GROUND_TRUTH.json`** — Expected answers. MUST BE VALIDATED BY OWNER before use.

**`engines/source/contracts.py`** — Enum values the LLM must output:
- Genre: matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, mawsuah, fatawa, mujam, tabaqat, fiqh_comparative, hadith_collection, tafsir, sirah, tarikh, adab, other
- StructuralFormat: prose, verse, qa_format, tabular_khilaf, dictionary, commentary, mixed
- AuthorityLevel: primary, reference, modern_compilation
- WorkLevel: beginner, intermediate, advanced, specialist

---

## API Access

Keys in project knowledge files:
- `anthropic_api_key` → Anthropic direct (Sonnet 4.6 for Phase 1, Opus 4.6 for Phase 2)
- `openai_api_key` → OpenAI direct (has GPT-4o only — NOT sufficient for Phase 2)
- `openrouter_api_key` → OpenRouter (GPT-5.x, Gemini 3.x, Mistral, Cohere — USE THIS for Phase 2 non-Anthropic models)
- `mistral_api_key` → Mistral direct (alternative to OpenRouter for Mistral)

**Important:** The direct OpenAI key lacks GPT-5. Use OpenRouter for GPT-5.4 and all non-Anthropic models in Phase 2.

All four APIs verified working.

---

## What to Read First

1. `NEXT.md` (this file)
2. `tests/fixtures/GROUND_TRUTH.json` — validate with owner FIRST
3. `tests/fixtures/EXTRACTED_DATA.json` — pre-extracted data for prompts
4. `engines/source/SPEC_CORE.md` §4.A.4 lines 750-860 — LLM inference spec
5. `engines/source/SPEC_CORE.md` §6 lines 1170-1210 — consensus spec
6. `engines/source/contracts.py` lines 115-160 — enum values

---

## Done When

- [ ] Ground truth validated by owner (Phase 0)
- [ ] Scoring criteria defined and evaluation harness built (Phase 0)
- [ ] A3 (name matching) validated deterministically (Phase 0)
- [ ] A4 (trust weights) validated deterministically (Phase 0)
- [ ] A1: Inference prompt ≥95% JSON parse, ≥90% enum compliance (Phase 1)
- [ ] A2: Multi-layer detection correct on all test cases or gated (Phase 1)
- [ ] A5: Best consensus pair identified on production-tier models (Phase 2-3)
- [ ] Final prompt templates saved to `engines/source/prompts/`
- [ ] All [ASSUMPTION] markers in SPEC resolved

After Step 2: Move to Step 3 (BUILD PREP — use kr-build-prep skill).
