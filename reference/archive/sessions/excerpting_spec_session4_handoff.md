# Excerpting SPEC Writing — Session 4 Handoff

**Date:** 2026-03-23
**Session scope:** §9 (Deferred Capabilities) + §10 (Test Requirements) + §1 (Purpose and Scope) + Coherence Review
**Commits:** `11c1eee` through `ea82cfb` (3 section commits + coherence fix + progress update)
**SPEC status:** 2343 lines, 12/12 sections COMPLETE. Status updated from DRAFT to COMPLETE.

---

## What Was Done

| Section | Lines | Commit | Key Content |
|---------|-------|--------|-------------|
| §9 Deferred Capabilities | 77 | `11c1eee` | 16 capabilities cataloged (DC-01–DC-16), extension hook contract, activation model, absorbed-vs-deferred table |
| §10 Test Requirements | 233 | `58aff02` | Coverage rule for 34 checks + 29 invariants + 27 errors + 22 domain rules; 12 adversarial cases (ADV-E-01–12); C-7 mitigation; cross-engine contracts |
| §1 Purpose and Scope | 63 | `ac1c241` | Pipeline position, 3-phase architecture, D-011 structural enforcement, T-1–T-7 defense mapping, 5 scope exclusions |
| Coherence review | — | `ea82cfb` | Fixed 7 scrambled error code trigger conditions in §10 (EX-A-002–011, EX-C-001–005, EX-M-001–002, EX-V-001); status DRAFT→COMPLETE |

**Coherence review findings (all fixed):**
- 7 error code trigger descriptions in §10 did not match §8 catalog (scrambled during writing — descriptions were plausible but assigned to wrong codes)
- All 27 error codes now aligned between §8 and §10
- All other cross-section checks passed: section references resolve, §6 rules referenced from §5/§7, C-SC criteria in §5, T-1–T-7 mapped in §1

---

## Accumulated ID Registries (Final)

All IDs verified programmatically against the SPEC (2343 lines, 12 sections).

**Verification checks (34):**
- V-P1-1 through V-P1-6 (Phase 1, §4.9)
- V-P2-1 through V-P2-19 (Phase 2, §5.4.2 and §5.4.3)
- V-P3-1 through V-P3-9 (Phase 3, §7.4)

**Invariants (29):**
- I-AC-1 through I-AC-7 (AssembledChunk, §2.3.2)
- I-CS-1 through I-CS-6 (ClassifiedSegment, §2.3.3)
- I-TU-1 through I-TU-9 (TeachingUnit, §2.3.4)
- I-ER-1 through I-ER-7 (ExcerptRecord output, §2.2.3)

**Error codes (27):**
- EX-A-002, 003, 004, 005, 006, 010, 011 (Phase 1 assembly)
- EX-C-001, 002, 003, 004, 005 (Phase 2 classification/grouping)
- EX-M-001, 002, 003, 004, 005, 006, 007, 008, 009, 010 (Phase 3 metadata)
- EX-V-001, 002 (validation)
- EX-G-001, 002, 003 (human gates)

**Self-containment criteria:** C-SC-1 through C-SC-5 (§3.2)

**Domain rules (22):**
- DP-1 through DP-6, LA-1 through LA-4, EV-1 through EV-3
- IR-1 through IR-3, VC-1 through VC-3, QM-1 through QM-3

**Deterministic enrichment fields:** F-DET-1 through F-DET-9 (§7.1)

**Configuration parameters:** 20 total in §8.3

**Deferred capabilities:** DC-01 through DC-16 (§9.1)

**Adversarial test cases:** ADV-E-01 through ADV-E-12 (§10.6)

---

## What's Next — Step 3: contracts.py and CLAUDE.md

NEXT.md Step 3 requires two updates before the SPEC is ready for kr-integrity audit:

### 1. Update `engines/excerpting/contracts.py`

The existing `contracts.py` (22KB) was written for the old blocked SPEC. It needs to be rewritten to match the new SPEC's data model:

- `AssembledChunk` (§2.3.2): 12 fields + 7 invariants
- `ClassifiedSegment` (§2.3.3): 7 fields + 6 invariants
- `TeachingUnit` (§2.3.4): 11 fields + 9 invariants
- `ExcerptRecord` (§2.2.2): 33 fields + 7 invariants
- Enumerations: `ScholarlyFunction` (16 types), `SelfContainmentLevel` (3 levels), `StructuralFormat` (7 types)
- Error codes: all 27 as an enum or constants

This is a CC task — delegate via kr-preparing-cc-handoffs.

### 2. Update `engines/excerpting/CLAUDE.md`

CLAUDE.md is the module guide for CC. It needs to reflect:
- The 3-phase architecture
- File locations and what each module does
- Which SPEC sections are authoritative for which modules
- Testing patterns (conftest.py helpers, fixture locations)
- The D-011 constraint as a structural invariant

This can be drafted by the architect and committed directly (it's prose, not code).

### 3. kr-integrity audit

After contracts.py and CLAUDE.md are updated, run the kr-integrity 8-lens audit on the complete SPEC. This is the quality gate before the SPEC is declared implementation-ready.

---

## Session End Retrospective

**What went wrong:** The §10 error code trigger conditions were scrambled — I wrote plausible-sounding descriptions but assigned them to the wrong error codes (7 out of 27 were wrong). The coherence review's programmatic cross-check caught this. Without the check, the §8 catalog and §10 test requirements would have been inconsistent, and CC would have written tests for the wrong conditions.

**Root cause:** When writing §10, I composed trigger descriptions from memory of what each code meant instead of reading the §8 catalog line by line. The descriptions were semantically reasonable but mapped to the wrong code IDs. This is the same class of error as "never assign from memory" — the fix is always to copy from the source.

**Lesson:** When any section references IDs defined in another section (§10 referencing §8 error codes, §7 referencing §2.2 fields), the writing process must have the source section open and copy IDs verbatim. The coherence review's programmatic cross-check is the safety net, not the primary mechanism.

**Stale memory entries:** The "KR EXCERPTING ENGINE STATE" memory entry should be updated: SPEC is now COMPLETE (2343 lines, 12 sections), not BLOCKED. Contracts.py and CLAUDE.md update pending.

**Protocol changes to propose:** Add a "copy from source" step to the section writing protocol: before writing any section that references IDs from another section, open that section and keep it visible. This prevents the scrambled-description class of errors.

**What next session needs:** A new Claude Chat session. Start by cloning the repo, reading NEXT.md, reading this handoff file. Tasks: (1) Draft CLAUDE.md update, (2) Prepare CC handoff for contracts.py rewrite, (3) Run kr-integrity 8-lens audit on complete SPEC. If all three complete, the SPEC is implementation-ready and the engine moves to the build phase.
