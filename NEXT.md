# NEXT — Source Engine Step 2: LLM Research & Prompt Engineering

**Session type:** RESEARCH — empirical testing of LLM assumptions
**Goal:** Validate or revise the 5 [ASSUMPTION] markers in SPEC_CORE.md through real API calls against real fixtures.

---

## Context

Step 1 (SPEC hardening) is locked after 6 review passes. The SPEC's deterministic components (extraction, hashing, dedup, trust arithmetic, validation) have been verified against all 12 real fixtures. What remains untested is everything that involves LLM inference: structured output, genre classification, author identification, multi-layer detection, and multi-model consensus.

These are not theoretical concerns. The text_sample extraction bug found in the last session (nested div regex) would have caused every LLM call to receive page headers instead of scholarly content. That's fixed now, but the actual LLM prompts have never been run.

---

## Pre-built Resources (ready to use)

**`tests/fixtures/EXTRACTED_DATA.json`** — Pre-extracted metadata and text samples for all 13 fixtures. Each entry contains:
- `extracted_metadata`: what the Shamela/plain text extractor produces
- `text_sample`: first 2000 chars of actual body text (correctly extracted)
- `prompt_context`: pre-formatted metadata string for the LLM prompt

Run `python3 scripts/extract_fixtures.py` to regenerate if fixtures change.

**`tests/fixtures/GROUND_TRUTH.json`** — Expected correct answers for each fixture: genre, science_scope, structural_format, is_multi_layer, level, authority_level, expected_trust. Some values marked `_uncertain` need owner validation during testing.

**`engines/source/contracts.py`** — All enum values the LLM must output:
- Genre: matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, mawsuah, fatawa, mujam, tabaqat, fiqh_comparative, hadith_collection, tafsir, sirah, tarikh, adab, other
- StructuralFormat: prose, verse, qa_format, tabular_khilaf, dictionary, commentary, mixed
- AuthorityLevel: primary, reference, modern_compilation
- WorkLevel: beginner, intermediate, advanced, specialist

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
**Fixtures:** 11_multi_small (multi-layer sharh → TRUE), 03_fiqh (standalone → FALSE), alfiyyah_versified (standalone matn → FALSE), 05_tafsir (corrections on Jalalayn → UNCERTAIN)
**If fails (<85%):** Add human gate for multi-layer classification.

### A3: Scholar Name Matching (§4.A.5, line ~952)
**Claim:** normalized_name_similarity scoring produces correct match/no-match decisions.
**Test:** Run the utility functions (defined in SPEC §4.A.1) on name pairs. This is deterministic — no LLM needed.
**Test cases:** See the [ASSUMPTION] marker for specific pairs.
**If fails:** Adjust normalization rules or thresholds.

### A4: Trust Weight Calibration (§4.A.8, line ~1013)
**Claim:** Weights and 0.65 threshold produce correct verified/flagged assignments.
**Test:** Compute trust scores for each fixture using the 5-factor algorithm. Compare against GROUND_TRUTH.json expected_trust.
**Fixtures:** All 13.
**If fails:** Adjust weights or threshold.

### A5: Two-Model Consensus (§6, line ~1205)
**Claim:** Two different-provider models catch more author identification errors than one.
**Test:** Run the same inference prompt through multiple models. Compare author identification accuracy per-model and in pairs.
**Fixtures:** All Shamela fixtures + alfiyyah.
**If fails:** Add a third model, tighten human gate thresholds, or change pair.

---

## Strategic Approach (3 phases)

### Phase 1: Prompt Engineering (Anthropic direct)
Use Claude Sonnet via Anthropic API for fast iteration.
1. Draft the inference prompt from SPEC §4.A.4 requirements (7 required elements)
2. Run against 6 diverse fixtures
3. Evaluate: JSON valid? Enums correct? Genre right? Author identified?
4. Revise prompt, repeat until ≥90% accuracy on the test set
5. This validates A1 and partially validates A2

### Phase 2: Multi-Model Accuracy (OpenRouter)
Run the validated prompt through 4-5 architecturally diverse models.
Candidates:
- Claude Sonnet (Anthropic) — baseline from Phase 1
- GPT-4o-mini (OpenAI) — different training, cheap
- Gemini 2.0 Flash (Google via OpenRouter) — very different architecture
- Mistral Large (Mistral via direct key or OpenRouter) — European training
- Command R+ (Cohere via OpenRouter) — different approach

For each model, measure on all 13 fixtures:
- JSON parse success rate
- Enum compliance rate
- Genre accuracy vs ground truth
- Author identification accuracy
- Multi-layer detection accuracy

### Phase 3: Consensus Pair Selection
From Phase 2 results, pick the pair that maximizes "at least one got it right" rate. Run the full consensus flow (both models independently → compare → agree/disagree) on all fixtures. This validates A5.

Also in this phase: validate A3 (deterministic name matching) and A4 (trust weights) — these don't need LLM calls but should be tested while we have ground truth loaded.

---

## API Access

Keys are in project knowledge files. Read them at session start:
- `anthropic_api_key` → Anthropic direct API
- `openai_api_key` → OpenAI direct API
- `openrouter_api_key` → OpenRouter (access to Gemini, Mistral, Command R+, etc.)
- `mistral_api_key` → Mistral direct API

Network egress is unrestricted. All four APIs verified working as of this session.

---

## What to Read First

1. `NEXT.md` (this file)
2. `tests/fixtures/EXTRACTED_DATA.json` — pre-extracted data for all fixtures
3. `tests/fixtures/GROUND_TRUTH.json` — expected correct answers
4. `engines/source/SPEC_CORE.md` §4.A.4 lines 700-860 — LLM inference specification
5. `engines/source/SPEC_CORE.md` §6 lines 1170-1210 — consensus specification
6. `engines/source/contracts.py` — enum values (lines 115-160)

## Ground Truth Values Needing Owner Input

During testing, ask the owner about these uncertain classifications:
- 01_nahw_simple: is أخبار أبي القاسم الزجاجي genre=tabaqat or genre=other?
- 05_tafsir: is تعقبات على الجلالين genre=sharh or genre=hashiyah? Is it multi-layer?
- 07_balagha: is a modern balagha textbook genre=matn or genre=risalah?
- 10_no_author: is a hadith evidence compilation genre=hadith_collection or fiqh_comparative?
- 12_multi_muq: what science_scope for مالك بن نبي's memoirs?

---

## Done When

- [ ] A1: Inference prompt achieves ≥95% JSON parse rate, ≥90% enum compliance
- [ ] A2: Multi-layer detection correct on all 4 test cases (or human gate added)
- [ ] A3: Name matching produces correct decisions on all test pairs
- [ ] A4: Trust scores match expected tiers for ≥11/13 fixtures
- [ ] A5: Best consensus pair identified, agreement rate measured
- [ ] Final prompt templates saved to `engines/source/prompts/`
- [ ] All [ASSUMPTION] markers in SPEC resolved (confirmed, revised, or gated)
- [ ] Per-model accuracy data saved for future reference

After Step 2: Move to Step 3 (BUILD PREP — use kr-build-prep skill).
