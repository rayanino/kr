# Gemini CLI — Verification Notes and Cross-Reference

**Verified by:** CC direct inspection (Grep + Read against SPEC files and user_model)
**Date:** 2026-04-07

## Verification Results

| Claim | Verdict | Evidence |
|-------|---------|----------|
| All FP references (7,9,12,15,18,19,20) | **CONFIRMED** | All found at correct SPEC.md lines |
| FP-18 = study-ready calibration gap | **CONFIRMED** | SPEC.md:69: "not yet calibrated" |
| **Prerequisite sequencing absent** | **PARTIALLY WRONG** | `shared/user_model/SPEC.md §4.A.5` has full curriculum state + `§4.B.2` prerequisite readiness prediction. SPECIFIED, NOT YET IMPLEMENTED. |
| **Cognitive complexity grading absent** | **CONFIRMED** | No difficulty field in ExcerptRecord or any pipeline output. Genuine gap. |
| **Active recall absent** | **PARTIALLY CONFIRMED** | user_model §4.A.3 has FSRS spaced repetition scheduling. But OUTPUT FORMAT (cloze/Q&A/recitation shape) is undefined. |
| Target madhhab changes Phase 2b | **PLAUSIBLE** | Phase 2b uses one-size-fits-all grouping, no per-school filtering |

### CRITICAL CORRECTION: Gemini Did Not Read user_model SPEC

Gemini claims the pipeline "lacks a mechanism for prerequisite sequencing." This is **PARTIALLY WRONG.**

`shared/user_model/SPEC.md` contains:
- **§4.A.5 Curriculum State:** Full curriculum management with structured learning paths, position tracking, prerequisite-respecting sequences, taxonomy evolution detection
- **§4.B.2 Prerequisite Readiness Prediction:** Predicts topic readiness from prerequisite knowledge state, computes optimal study paths, identifies lacking prerequisites
- **§4.A.3 Spaced Repetition:** FSRS v6 scheduling with decay prediction and prerequisite cascading
- **§4.A.4 Scholarly Profile:** Per-science expertise levels (none/beginner/intermediate/advanced/researcher)

**Status:** "Cycle 0 (not yet started)" per `shared/user_model/CLAUDE.md`. SPECIFIED but NOT IMPLEMENTED. The design exists; the code doesn't.

**What Gemini correctly identified despite this:**
- Cognitive complexity grading is a genuine gap (no specification exists)
- Active recall output FORMAT is unspecified (scheduling exists, shape of study material doesn't)
- The taxonomy engine (v1) explicitly defers prerequisite edge management

## Cross-Reference: Gemini → DR18 + Codex

| Gemini Finding | DR18 | Codex | Gemini Unique |
|---------------|------|-------|---------------|
| Target madhhab | SYN-D-002 | DT-06 | "Cognitive pollution" framing; per-BOOK strategy |
| Qa'idah vs shahid | — | DT-07 GN-2 | **Challenges FP-1** for memorization mode |
| Munazarah vs qawa'id | — | — | Pedagogical mode choice for usul |
| Shubuhat exposure | — | — | Knowledge safety for beginners |
| FP-18 calibration | EXC-D-002 | DT-08 | "Cognitive threshold" — brain acceptance testing |
| Proof sourcing FP-7 | — | DT-05 loosely | Cross-reference infrastructure decision |
| Visible omission | — | DT-09 loosely | Pipeline vs UI split |
| Matn override | — | DT-07 loosely | Self-containment exemption for mutun |
| Hashiyah filtering | — | — | Level-based layer exclusion |
| Mukhtasar exceptions | — | — | Cross-passage reassembly |
| Prerequisite seq. | — | — | DESIGNED in user_model (§4.A.5, §4.B.2), not built |
| Complexity grading | UM-D-001 loosely | DT-01 loosely | **GENUINE GAP** — no difficulty dimension anywhere |
| Active recall format | — | — | FSRS scheduling exists; output shape undefined |

## Three-Coworker Synthesis (3/5 reports)

```
Layer 1: USER MODEL (Codex DT-01 + Gemini pedagogical params)
  "What is the library optimizing for?"
  Owner items: study mode per science, madhhab choice, memorization style,
               shubuhat policy, proof sourcing, genre overrides
  ↓
Layer 2: QUALITY POLICIES (Codex DT-02..09 + DR18 PP-001..012)
  "What rules govern pipeline output?"
  Owner items: quality rubric priority, granularity thresholds,
               self-containment policy, evidence packaging, genre exceptions
  ↓
Layer 3: ENGINE DECISIONS (DR18 SRC/EXC/TAX/SYN-D-*)
  "What parameters configure each engine?"
  Owner items: muhaqiq list, science scope, book priority,
               flag budget, tree reviews, entry style
  ↓
Layer 4: CALIBRATION (Gemini FP-18 + DR18 EXC-D-001/002 + Codex DT-08/11)
  "Does the engine match the owner's brain?"
  Owner items: 100+ excerpt judgments, study-readiness labels,
               DEPENDENT disposition rubrics, 30-book probe
```

## New Data Types Unique to Gemini (to add to unified inventory)

| ID | Name | Engine(s) | Status | Tedious? |
|----|------|----------|--------|----------|
| GEM-01 | Target madhhab per comparative book | Excerpting (Phase 2b) | MISSING | TEDIOUS (NOW) |
| GEM-02 | Memorization atomicity (qa'idah+shahid) | Excerpting | MISSING | TEDIOUS (NOW) |
| GEM-03 | Dialectical training mode per science | Excerpting, Taxonomy | MISSING | TEDIOUS (NOW) |
| GEM-04 | Shubuhat exposure policy per science | Excerpting | MISSING | TEDIOUS (NOW) |
| GEM-05 | Proof sourcing methodology (FP-7) | Excerpting, Source | MISSING | TEDIOUS (NOW — architectural) |
| GEM-06 | Matn genre override rules | Excerpting | MISSING | NON-TEDIOUS |
| GEM-07 | Hashiyah filtering threshold | Excerpting, Normalization | MISSING | NON-TEDIOUS |
| GEM-08 | Mukhtasar exception-pulling policy | Excerpting | MISSING | NON-TEDIOUS (deferred) |
| GEM-09 | Cognitive complexity grading model | Excerpting, Taxonomy | MISSING | SUMMER |
| GEM-10 | Active recall output format | Synthesis, user_model | MISSING | SUMMER |
