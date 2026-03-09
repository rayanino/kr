# NEXT — Source Engine Step 2: Research

**Session type:** RESEARCH (deep investigation before build)
**Goal:** Validate all [ASSUMPTION — NEEDS STEP 2 TESTING] markers in SPEC_CORE.md through real LLM testing and prompt engineering.

---

## Context

Step 1 is locked. The SPEC has been through four review passes:
1. **Integrity audit** (kr-integrity): found 11 defects, 8 fixed
2. **Shamela survey** (2,519 real exports): revealed all extraction rules were wrong, complete rewrite
3. **Deep quality review** (8-dimension analysis): found 14 more defects, 10 fixed
4. **Final hardening** (4 blind spots): found 8 defects, 7 fixed, 1 documented

The SPEC is now implementation-ready for deterministic components. The remaining unknowns are all LLM-dependent: prompt accuracy, consensus reliability, and confidence calibration.

---

## Step 2 Scope: Test Every ASSUMPTION Marker

The SPEC contains 5 explicit assumptions that need empirical validation:

### A1: LLM Structured JSON Reliability (§4.A.4)
"The LLM can produce this structured JSON reliably for well-known Islamic scholarly works."
**Test:** Run inference prompt on ≥5 real fixtures. Measure: JSON parse success rate, enum compliance, field completeness.

### A2: LLM Multi-Layer Detection Accuracy (§4.A.4)
"LLM multi-layer detection from genre + title + content achieves ≥ 90% accuracy."
**Test:** Run on fixture 11 (multi-layer sharh: همع الهوامع), alfiyyah plain text (single-layer), standalone fiqh work. Measure: correct classification rate.

### A3: Scholar Name Matching Accuracy (§4.A.5)
"The name normalization and similarity scoring produce accurate matches."
**Test:** Exact match, variant spelling, different-scholar-similar-names cases with real data.

### A4: Trust Evaluation Weight Calibration (§4.A.8)
"The weights (0.30, 0.25, 0.15, 0.15, 0.15) and threshold (0.65) produce sensible results."
**Test:** Run trust evaluation on ≥5 fixtures with known expected outcomes. Measure: correct tier assignment rate.

### A5: Two-Model Consensus Effectiveness (§6)
"Two-model consensus catches most attribution errors."
**Test:** Run the same prompt through Claude and GPT on ≥5 fixtures. Measure: agreement rate, per-model accuracy.

---

## What to read first

1. `NEXT.md` (this file)
2. `engines/source/SPEC_CORE.md` — The locked SPEC
3. `engines/source/STEP1_FINAL_HARDENING.md` — Final review findings
4. `tests/fixtures/shamela_real/` — Real test fixtures
5. `tests/fixtures/alfiyyah_versified/` — Plain text fixture

## Done when

- [ ] A1: Inference prompt tested on ≥5 fixtures, JSON parse rate ≥95%
- [ ] A2: Multi-layer detection correct on ≥3 test cases
- [ ] A3: Scholar matching tested on exact, variant, and adversarial cases
- [ ] A4: Trust weights validated or adjusted on ≥5 fixtures
- [ ] A5: Consensus tested on ≥5 fixtures, agreement rate measured
- [ ] All ASSUMPTION markers in SPEC_CORE.md either validated or SPEC adjusted
- [ ] Prompt templates drafted and tested

After this pass: Move to Step 3 (BUILD PREP — kr-build-prep skill).
