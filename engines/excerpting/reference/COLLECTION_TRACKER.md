# Feedback Collection Tracker — Owner Data for July 1 Readiness

> Tracks all owner-dependent decisions across all 5 pipeline engines.
> Source: DR18 decision map (38 decisions) + Gemini DR additions (4) + questionnaire items (15) + S-1 (done).
> Governing plan: `docs/plans/2026-04-07-001-feat-feedback-collection-system-plan.md`
> 5-coworker synthesis: `engines/excerpting/reference/dr_reviews/FINAL_SYNTHESIS_5_OF_5.md`

---

## Progress Summary

| Layer | Resolved | Pending | Total | Target |
|-------|----------|---------|-------|--------|
| 1: User Model + Pedagogy | 5 | 4 | 9 | End of April |
| 2: Quality Policies + Governance | 1 | 14 | 15 | End of May |
| 3: Engine Decisions + Parameters | 7 | 16 | 23 | End of May |
| 4: Calibration | 0 | 10 | 10 | Summer |
| **TOTAL** | **13** | **44** | **57** | **July 1** |

**Hours estimated:** ~31-41 total (~20-30 min/day average over 3 months)
**Budget spent:** EUR 0.00 this workstream (all deterministic so far)

---

## Layer 1: User Model + Pedagogical Mode (~3 hours, weeks 1-2)

> "What kind of student am I? How do I study?"
> Artifact: `shared/user_model/owner_profile.yaml`

| # | Decision | Status | Source | Collection Method | Est. Time |
|---|----------|--------|--------|-------------------|-----------|
| L1-01 | Study level (beginner) | RESOLVED | Interview 2026-04-07 | — | — |
| L1-02 | Study mode (memorization-first) | RESOLVED | Interview 2026-04-07 | — | — |
| L1-03 | Science priority order (Arabic first) | RESOLVED (top 4) | Interview 2026-04-07 | Full 19-ranking: Session A | 15 min |
| L1-04 | Primary madhab (Hanbali) | RESOLVED | Owner answer 2026-04-07 | — | — |
| L1-05 | Mantiq = science #19 | RESOLVED | Owner answer 2026-04-07 | — | — |
| L1-06 | Grammar school preference (Basran) | ASSUMED | Gemini DR recommendation | Owner confirmation needed | 5 min |
| L1-07 | Per-science study mode (memorize vs dialectical) | PENDING | — | Phase A question 4 | 20 min |
| L1-08 | Shubuhat exposure policy (aqidah) | PENDING | Gemini CLI finding | Structured question | 10 min |
| L1-09 | Fiqh masking unlock conditions | PENDING | Gemini DR | Structured scenario | 15 min |

---

## Layer 2: Quality Policies + Conflict Governance (~3 hours, weeks 2-4)

> "What rules govern output? Which quality dimension wins?"
> Collection channel: ChatGPT bundle format (S-1 pattern) + existing questionnaire

| # | Decision | Status | DR18 Code | Collection Method | Est. Time |
|---|----------|--------|-----------|-------------------|-----------|
| L2-01 | S-1: Priority ranking under conflict | **RESOLVED** | DT-02 | S-1 bundle intake complete | — |
| L2-02 | S-2: Ideal vs worst excerpt definition | PENDING | — | ChatGPT session (S-2 template) | 45 min |
| L2-03 | K-1: Khilaf/tarjih deep dive (part 1) | PENDING | — | ChatGPT session (K template) | 30 min |
| L2-04 | K-2: Khilaf/tarjih deep dive (part 2) | PENDING | — | ChatGPT session (K template) | 30 min |
| L2-05 | K-3: Khilaf/tarjih deep dive (part 3) | PENDING | — | ChatGPT session (K template) | 30 min |
| L2-06 | E-1: Evidence organization (part 1) | PENDING | — | ChatGPT session (E template) | 20 min |
| L2-07 | E-2: Evidence organization (part 2) | PENDING | — | ChatGPT session (E template) | 20 min |
| L2-08 | E-3: Evidence organization (part 3) | PENDING | — | ChatGPT session (E template) | 20 min |
| L2-09 | D-1: Definition splitting (part 1) | PENDING | — | ChatGPT session (D template) | 15 min |
| L2-10 | D-2: Definition splitting (part 2) | PENDING | — | ChatGPT session (D template) | 15 min |
| L2-11 | D-3: Definition splitting (part 3) | PENDING | — | ChatGPT session (D template) | 15 min |
| L2-12 | SC-2: Self-containment remaining | PENDING | — | ChatGPT session (supplementary) | 15 min |
| L2-13 | SC-3: Self-containment remaining | PENDING | — | ChatGPT session (supplementary) | 15 min |
| L2-14 | GN-1: Genre policies | PENDING | — | ChatGPT session (supplementary) | 15 min |
| L2-15 | GN-2: Genre policies | PENDING | — | ChatGPT session (supplementary) | 15 min |

---

## Layer 3: Engine Decisions + Parameters (~5 hours, weeks 1-3)

> "What configures each engine?"
> Collection: DR18's 5 focused sessions (structured/interactive)

### Source Engine (SRC)

| # | Decision | Status | DR18 Code | Classification | Est. Time |
|---|----------|--------|-----------|----------------|-----------|
| L3-01 | Muhaqiq trust list | PARTIAL | SRC-D-001 | TEDIOUS | 30 min |
| L3-02 | Publisher reputation list | PENDING | SRC-D-002 | TEDIOUS | 20 min |
| L3-03 | Muhaqiq watchlist (commercial) | PENDING | SRC-D-003 | TEDIOUS | 10 min |
| L3-04 | Science scope (19 sciences) | PARTIAL | SRC-D-004 | TEDIOUS | 15 min |
| L3-05 | Study focus / curriculum position | PENDING | SRC-D-005 | TEDIOUS | 10 min |
| L3-06 | School preference for editions | DEFERRED | SRC-D-006 | SUMMER | — |
| L3-07 | Trust tier override authority | RESOLVED | SRC-D-007 | Design | — |
| L3-08 | Partial-relevance policy | PENDING | SRC-D-008 | TEDIOUS | 5 min |
| L3-09 | Confidence thresholds | RESOLVED | SRC-D-009 | N/A | — |
| L3-10 | Book processing priority | PARTIAL | SRC-D-010 | TEDIOUS | 60 min |

### Normalization Engine (NORM)

| # | Decision | Status | DR18 Code | Classification | Est. Time |
|---|----------|--------|-----------|----------------|-----------|
| L3-11 | Layer detection threshold | RESOLVED | NORM-D-001 | N/A | — |
| L3-12 | Structure format override | RESOLVED | NORM-D-002 | Design | — |
| L3-13 | Page order conflicts | RESOLVED | NORM-D-003 | Design | — |
| L3-14 | Layer fingerprint review | RESOLVED | NORM-D-004 | Design | — |
| L3-15 | OCR engine selection | RESOLVED | NORM-D-005 | N/A | — |

### Excerpting Engine (EXC)

| # | Decision | Status | DR18 Code | Classification | Est. Time |
|---|----------|--------|-----------|----------------|-----------|
| L3-16 | Complete scholarly thought definition | PARTIAL | EXC-D-001 | SUMMER | — |
| L3-17 | Self-containment calibration | DEFERRED | EXC-D-002 | SUMMER | — |
| L3-18 | Forgiving retention (FP-3) | RESOLVED | EXC-D-003 | N/A | — |
| L3-19 | Hadith title retention | PARTIAL | EXC-D-004 | TEDIOUS | 5 min |
| L3-20 | 30-book owner review gate | DEFERRED | EXC-D-005 | SUMMER | — |
| L3-21 | DEPENDENT excerpt handling | RESOLVED | EXC-D-006 | Design | — |
| L3-22 | Author attribution disambiguation | RESOLVED | EXC-D-007 | Design | — |
| L3-23 | School attribution conflict | RESOLVED | EXC-D-008 | Design | — |
| L3-24 | Error class calibration | PARTIAL | EXC-D-009 | TEDIOUS | 5 min |
| L3-25 | Flag budget threshold | PENDING | EXC-D-010 | TEDIOUS | 5 min |

### Taxonomy Engine (TAX)

| # | Decision | Status | DR18 Code | Classification | Est. Time |
|---|----------|--------|-----------|----------------|-----------|
| L3-26 | Science tree structures (4 remaining) | PARTIAL | TAX-D-001 | TEDIOUS | 2h total |
| L3-27 | Placement confidence thresholds | RESOLVED | TAX-D-002 | N/A | — |
| L3-28 | Per-science tree priority | PARTIAL | TAX-D-003 | TEDIOUS | 5 min |
| L3-29 | Topic-not-school branching | RESOLVED | TAX-D-004 | N/A | — |
| L3-30 | Staged excerpt review | RESOLVED | TAX-D-005 | Design | — |
| L3-31 | Science scope per book | PARTIAL | TAX-D-006 | SUMMER | — |
| L3-32 | Additional science trees | PENDING | TAX-D-007 | TEDIOUS | 10 min |

### Synthesis Engine (SYN)

| # | Decision | Status | DR18 Code | Classification | Est. Time |
|---|----------|--------|-----------|----------------|-----------|
| L3-33 | Entry format preferences | DEFERRED | SYN-D-001 | SUMMER | — |
| L3-34 | School list per science | PENDING | SYN-D-002 | TEDIOUS | 20 min |
| L3-35 | Factual vs analytical boundary | DEFERRED | SYN-D-003 | SUMMER | — |
| L3-36 | Owner corrections as constraints | RESOLVED | SYN-D-004 | Design | — |
| L3-37 | Entry language and tone | PENDING | SYN-D-005 | TEDIOUS | 15 min |
| L3-38 | Cross-science reference policy | DEFERRED | SYN-D-006 | SUMMER | — |

---

## Layer 4: Calibration (~20-30 hours, weeks 4-12 + summer)

> "Does the engine match the owner's brain?"
> Requires real pipeline output. Infrastructure designed now, execution in summer.

| # | Decision | Status | Related | Collection Method | Est. Time |
|---|----------|--------|---------|-------------------|-----------|
| L4-01 | 100+ excerpt teaching-unit quality judgments | DEFERRED | R11, EXC-D-001 | Structured review (tools/review.py) | ~15h |
| L4-02 | 30-100 study-readiness labels (FP-18 split) | DEFERRED | R12, EXC-D-002 | Binary classification | ~5h |
| L4-03 | 30-book owner review gate | DEFERRED | R13, EXC-D-005 | Review sessions | ~5h |
| L4-04 | DEPENDENT disposition rubrics | DEFERRED | R14, EXC-D-006 | Per-decision during runs | ~3h |
| L4-05 | L-1: Layer policies | PENDING | — | ChatGPT session | 15 min |
| L4-06 | L-2: Layer policies | PENDING | — | ChatGPT session | 15 min |
| L4-07 | TEAM_TRANSLATION_GUIDE FP-13..22 | PENDING | R10 | CC-only (no owner) | 30 min |
| L4-08 | Entry style confirmation | PENDING | SYN-D-005 | Owner reads ENTRY_EXAMPLE.md | 15 min |
| L4-09 | Cognitive complexity grading spec | PENDING | Gemini CLI gap | Design + owner calibration | 1h |
| L4-10 | Active recall output format | PENDING | Gemini CLI gap | Design + owner preference | 30 min |

---

## Calendar Milestones

| Date | Milestone | Gate |
|------|-----------|------|
| **April 30** | Layer 1 COMPLETE. L1-01..09 all RESOLVED. | owner_profile.yaml fully populated |
| **May 15** | Layer 2 50% done. S-2 + K-series complete. | 8/15 Layer 2 items RESOLVED |
| **May 31** | Layer 2+3 COMPLETE (TEDIOUS items). | All non-SUMMER items RESOLVED |
| **June 15** | Layer 4 infrastructure ready. | Calibration pipeline tested |
| **July 1** | All non-SUMMER items RESOLVED. Layer 4 calibration in progress. | Zero blockers from insufficient input |

---

## DR18 Session Mapping

| Session | Focus | Decision Codes | Est. Owner Time |
|---------|-------|---------------|-----------------|
| A | Science scope + ranking + study modes | SRC-D-004, SRC-D-005, TAX-D-003, TAX-D-007 | 60 min |
| B | Muhaqiq trust + publisher reputation | SRC-D-001, SRC-D-002, SRC-D-003 | 60 min |
| C | Book processing priority | SRC-D-010 | 60 min |
| D | Thresholds (error class, flag budget, partial-relevance) | EXC-D-009, EXC-D-010, SRC-D-008, EXC-D-004 | 30 min |
| E | Entry style + school lists + hadith titles | SYN-D-002, SYN-D-005, SRC-D-006 | 45 min |

---

*Last updated: 2026-04-07, Session 11. S-1 intake complete. 13/57 resolved.*
