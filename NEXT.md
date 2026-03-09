# NEXT — Source Engine Step 2 (RESEARCH)

**Session type:** RESEARCH — test 7 marked assumptions
**Goal:** Empirically validate every assumption in SPEC_CORE.md before building

---

## What happened last session

1. **Core SPEC written and audited** (SPEC_CORE.md + INTEGRITY_AUDIT.md)
2. **Owner provided 2,519 real Shamela exports** — surveyed 100% of them
3. **Critical discovery:** Real Shamela format is completely different from synthetic fixture. No info.html, no table metadata, no CSS layer classes. All extraction rules rewritten.
4. **Permanent documentation:** `reference/SHAMELA_FORMAT_ANALYSIS.md` (complete format spec from 2,519 books)
5. **12 real test fixtures** added to `tests/fixtures/shamela_real/`
6. **SPEC_CORE.md fully updated** with correct extraction pseudocode

### Owner Sanity Check Status
Questions Q1-Q3 (Shamela structure) are now answered empirically from real data — no owner input needed. Questions Q4-Q10 still await owner response. Per ENGINE_PROTOCOL: after 3 days, proceed without answers.

---

## Step 2 Plan

Test these assumptions on real fixtures from `tests/fixtures/shamela_real/` and `alfiyyah_versified`:

| ID | Assumption | Fixtures to Test | Pass Criteria |
|----|-----------|-----------------|---------------|
| A1 | LLM genre inference ≥ 85% | All 12 shamela_real + alfiyyah | ≥ 85% correct genre |
| A2 | LLM genre_chain inference ≥ 80% | Books with sharh/hashiyah titles | ≥ 80% correct base work |
| A3 | LLM multi-layer detection ≥ 90% | Genre-inferred (no CSS signal) | ≥ 90% correct is_multi_layer |
| A4 | Two-model consensus catches errors | 10+ fixtures through Claude + GPT | Agreement rate and accuracy |
| A5 | Scholar matching formula accuracy | Variant spellings from real exports | Correct match/no-match |
| A6 | Trust weights produce correct tiers | 5+ sources (verified + flagged cases) | Expected tier for each |
| A7 | Name normalization sufficiency | Real author names from exports | Correct normalization |

**Skills to use:** `kr-research` for the assumption testing.

**Key risk elevation:** A3 (multi-layer detection) is now higher risk than originally assessed because CSS classes don't exist. The LLM must infer multi-layer purely from genre + title + content. If accuracy is < 85%, the SPEC must add a human gate for all multi-layer decisions.

---

## What to read

1. `engines/source/SPEC_CORE.md` — The core SPEC (updated with real extraction rules)
2. `reference/SHAMELA_FORMAT_ANALYSIS.md` — Complete format spec from real data
3. `engines/source/INTEGRITY_AUDIT.md` — Defects + post-audit discovery
4. `tests/fixtures/shamela_real/README.md` — 12 real test fixtures
