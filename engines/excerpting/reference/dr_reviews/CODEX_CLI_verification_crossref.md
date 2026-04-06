# Codex CLI — Verification Notes and DR18 Cross-Reference

**Verified by:** CC direct inspection (Grep + Read)
**Date:** 2026-04-07

## Verification Results

| Claim | Verdict | Evidence |
|-------|---------|----------|
| TEAM_TRANSLATION_GUIDE has no FP-13..22 mapping | **CONFIRMED** | `grep FP-` returns zero matches in the file |
| G-1/CJ-4/S-1 show pre-hardening defaults | **CONFIRMED** | Lines 24/45/46: "No minimum defined", "All available fields", "Not yet defined" |
| FP-18 needs empirical calibration | **CONFIRMED** | SPEC.md:69: "the operational threshold is not yet calibrated" |
| FP-8 defers to K-1/K-2/K-3 | **CONFIRMED** | SPEC.md:48: "Full resolution is deferred to questionnaire items K-1 through K-3" |
| Only FP-8 and FP-18 need owner calibration | **PLAUSIBLE** | FP-15: "deferred to corpus expansion"; FP-7/16/17 similar. Remaining FPs have sufficient specificity for implementation. |
| DT dependency chain order | **PLAUSIBLE** | Follows SPEC structure: user model → quality rubric → granularity → self-containment → special cases → calibration |

## Key Disagreements with DR18

### 1. Collection Root: User Model (Codex) vs Science Scope (DR18)
- **Codex:** DT-01 (user model) must come first — "every later owner judgment depends on what the library is optimizing for"
- **DR18:** SRC-D-004 (science scope) is the critical path root
- **Resolution:** Codex is conceptually more correct — the user model IS the root. But practically, the interview already provides user model signals ("present everything, just memorize"). Science scope needs explicit 18-science ranking and is the first UNRESOLVED root. **Action: formalize user model from interview data first (quick), then collect science scope ranking.**

### 2. Granularity Timing: Tedious-Now (Codex) vs Summer (DR18)
- **Codex:** DT-03 is TEDIOUS — collect policy now from existing bundles (G-1 through G-4 already answered)
- **DR18:** EXC-D-001 is SUMMER — needs 100+ labeled excerpts from real output
- **Resolution:** Both right about different layers. POLICY (what the owner wants) can be collected now from bundles. CALIBRATION (does the engine do what the owner wants) needs real output. **Action: two-phase approach — policy now, calibration summer.**

### 3. Study-Readiness: Separate (Codex) vs Conflated (DR18)
- **Codex:** DT-08 is DISTINCT from DT-04. FP-18 explicitly separates acceptable from study-ready.
- **DR18:** EXC-D-002 conflates both under "self-containment calibration"
- **Resolution:** Codex is more precise. FP-18 at SPEC.md:69 explicitly says FULL conflates two levels. **Action: treat study-readiness calibration (DT-08) as a separate collection item requiring ~30 labeled judgments.**

### 4. Tedious Item Count: 4 (Codex) vs 13 (DR18)
- **Codex:** Only DT-03, DT-04, DT-08, DT-11 are tedious (high exemplar density)
- **DR18:** 13 items across 5 sessions (~5 hours)
- **Resolution:** Not a real disagreement — different thresholds. Codex counts only HIGH-EXEMPLAR items (many sub-decisions). DR18 includes quick-but-needs-thought items. **Action: use DR18's 5-session structure but flag Codex's 4 TEDIOUS items as the ones needing most owner time.**

## Cross-Reference: Codex DTs → DR18 Decisions

| Codex DT | DR18 Equivalent(s) | Codex Unique Contribution |
|----------|-------------------|--------------------------|
| DT-01 (User model) | UM-D-001/002 (CC gaps) | "Root dependency" framing |
| DT-02 (Quality rubric) | EXC-D-009/010 (partial) | Priority ORDER among quality dimensions (S-1 unmapped) |
| DT-03 (Granularity) | EXC-D-001 | Maps to G-1/G-2/G-3/G-4/CJ-1; identifies as TEDIOUS-NOW |
| DT-04 (Self-containment) | EXC-D-002/003 | Maps to F-5/SC-1/SC-2/SC-3 |
| DT-05 (Evidence) | — (NONE in DR18) | **Entirely unique.** E-1/E-2/E-3 policies. |
| DT-06 (Khilaf) | — (NEXT.md refs only) | **Largely unique.** K-1/K-2/K-3 policies. |
| DT-07 (Genre/layer) | — (NONE in DR18) | **Entirely unique.** GN-1/GN-2/L-1/L-2 policies. |
| DT-08 (Study-readiness) | EXC-D-002 (conflated) | **Separates** study-ready from self-contained via FP-18 |
| DT-09 (Metadata visibility) | — (FP-21 refs only) | **Largely unique.** Study-surface concept. |
| DT-10 (Source policy) | SRC-D-001/002/003/006/007 | Bundles as single policy family |
| DT-11 (Human gate rubrics) | EXC-D-006/007/008, HG-D-001 | Adds RUBRIC concept (reusable, not per-gate) |

## DR18 Decisions with NO Codex Equivalent

- SRC-D-004 (science scope), SRC-D-005 (study focus), SRC-D-010 (book priority)
- ALL taxonomy decisions (TAX-D-001 through TAX-D-007)
- ALL synthesis decisions (SYN-D-001 through SYN-D-006)
- ALL normalization decisions (NORM-D-001 through NORM-D-005)

Expected — Codex was scoped to excerpting contracts + TEAM_TRANSLATION_GUIDE, not all engines.

## Merged Insight

Together, DR18 + Codex reveal a **two-layer data collection structure:**
1. **Policy layer** (Codex DT-01 through DT-11): What the owner WANTS — principles, priorities, rules
2. **Decision layer** (DR18 SRC/EXC/TAX/SYN-D-*): What the pipeline NEEDS — thresholds, lists, rankings

The policy layer PRECEDES the decision layer. You can't set a flag budget threshold (DR18 EXC-D-010) until you've defined the quality rubric (Codex DT-02) that determines what counts as a flag-worthy issue.
