# ChatGPT DR — Verification Notes and Cross-Reference

**Verified by:** CC direct inspection
**Date:** 2026-04-07

## Verification Results

| Claim | Verdict | Evidence |
|-------|---------|----------|
| S-1 "Not yet defined" | **CONFIRMED** | TEAM_TRANSLATION_GUIDE.md:46 |
| S-2 exists as named interaction | **CONFIRMED** | TEAM_TRANSLATION_GUIDE.md:47 |
| Campaign has 2,303 excerpts | **CONFIRMED** | 20+ files in campaign_20260331/ |
| F1 canon differs structurally from F3-F8 | **CONFIRMED** | F1 has canon/ subdirectory |
| Bundle schema inconsistency | **CONFIRMED** | G1: `final_questionnaire_choice`, SC1: different variant |
| FPs encode highest-stakes doctrine | **CONFIRMED** | FP-1..FP-22 hardened in SPEC.md §1.1b |
| 189 errors total in campaign | **PLAUSIBLE** | Campaign files contain error tracking; exact count not independently verified |

## Unique Contributions (not found in other 3 coworkers)

1. **What's ALREADY collected** — Only coworker to inventory existing bundles. Others focused on what's needed.
2. **"Highest-stakes already integrated"** — Maturity assessment: foundational doctrine IS in the SPEC. Remaining work is calibration + special cases.
3. **Campaign error evidence** — Concrete error counts (2,303 excerpts, 189 errors) backing up why each gap matters.
4. **Bundle format weaknesses** — 4 specific issues + 3 proposed additions. Other coworkers didn't evaluate the bundle format.
5. **Error-to-owner-dependency mapping** — 4-category classification of which errors need owner input vs prompt engineering.

## Cross-Reference: ChatGPT DR → Other Coworkers

| ChatGPT DR Finding | DR18 | Codex | Gemini CLI |
|-------------------|------|-------|------------|
| S-1 priority ranking | — | DT-02 (EXACT match) | — |
| Study-ready calibration | EXC-D-002 | DT-08 | FP-18 calibration |
| K-1..K-3 khilaf | — (NEXT.md refs) | DT-06 | — |
| E-1..E-3 evidence | — | DT-05 | — |
| D-1..D-3 definition | — | DT-03 partially | — |
| GN-1/GN-2 genre | — | DT-07 | Matn/sharh/hashiyah overrides |
| L-1/L-2 layer | — | DT-07 partially | Hashiyah filtering |
| Bundle format issues | — | — | — (UNIQUE) |
| Error classification | — | — | — (UNIQUE) |
| Already-collected inventory | — | — | — (UNIQUE) |

## Resolution of Apparent Priority Disagreements

All 4 coworkers named different "#1 priorities" — resolved as 4 levels of one hierarchy:

| Priority Level | Coworker | Item | Why It's This Level |
|---------------|----------|------|-------------------|
| Layer 1 (root) | Codex + Gemini | User model + study mode | Everything depends on WHO studies HOW |
| Layer 2 | ChatGPT DR | S-1 quality priority | Resolves conflicts BETWEEN quality dimensions |
| Layer 3 | DR18 | Science scope + book priority | Configures WHAT the pipeline processes |
| Layer 4 | All four | FP-18 calibration | Requires REAL OUTPUT + owner judgment |
