# NEXT — Source Engine Step 2 (RESEARCH)

**Session type:** RESEARCH — test 7 marked assumptions
**Goal:** Empirically validate every assumption in SPEC_CORE.md before building

---

## What happened in previous sessions

### Session 1: Core extraction + SPEC writing + integrity audit
- CORE_VS_DEFERRED.md: 68 core / 32 deferred
- SPEC_CORE.md: ~1100 lines at architecture-decision depth
- INTEGRITY_AUDIT.md: 11 defects found, 8 fixed

### Session 2: Shamela survey + sanity check
- Surveyed ALL 2,519 real Shamela exports → rewrote extraction rules
- 12 real test fixtures added to tests/fixtures/shamela_real/
- All 10 sanity check questions answered empirically
- reference/SHAMELA_FORMAT_ANALYSIS.md: complete format spec

### Session 3: Deep quality review
- STEP1_QUALITY_REVIEW.md: 14 findings across 8 dimensions
- 5 critical defects fixed (workflow ordering, text_fidelity_reason, confidence_scores mapping, death date regex, stale CSS prompt)
- 5 important defects fixed (stale references, field mapping table, test fixtures, etc.)
- All 25+ required SourceMetadata fields confirmed covered in SPEC

---

## Step 2 Plan

Test these assumptions on real fixtures from `tests/fixtures/shamela_real/` and `alfiyyah_versified`:

| ID | Assumption | Fixtures to Test | Pass Criteria |
|----|-----------|-----------------|---------------|
| A1 | LLM genre inference ≥ 85% | All 12 shamela_real + alfiyyah | ≥ 85% correct genre |
| A2 | LLM genre_chain inference ≥ 80% | shamela_real/11_multi_small (sharh) | ≥ 80% correct base work |
| A3 | LLM multi-layer detection ≥ 90% | Genre-inferred (no CSS signal) | ≥ 90% correct is_multi_layer |
| A4 | Two-model consensus catches errors | 10+ fixtures through Claude + GPT | Agreement rate + accuracy |
| A5 | Scholar matching formula accuracy | Variant spellings from real exports | Correct match/no-match |
| A6 | Trust weights produce correct tiers | 5+ sources (verified + flagged) | Expected tier for each |
| A7 | Name normalization sufficiency | Real author names from exports | Correct normalization |

**Key risk:** A3 (multi-layer detection) is the highest-risk assumption — no CSS signal available, purely LLM-inferred.

**Skills:** `kr-research` for assumption testing.
**Max sessions:** 3 (per ENGINE_PROTOCOL).

---

## What to read

1. `engines/source/SPEC_CORE.md` — The core SPEC (fully reviewed and fixed)
2. `engines/source/STEP1_QUALITY_REVIEW.md` — Quality review findings
3. `reference/SHAMELA_FORMAT_ANALYSIS.md` — Real Shamela format spec
4. `tests/fixtures/shamela_real/MANIFEST.json` — 12 test fixtures
5. `engines/source/OWNER_SANITY_CHECK_ANSWERS.md` — Domain answers
