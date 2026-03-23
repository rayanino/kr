# Excerpting SPEC Writing — Session 4 Handoff

**Date:** 2026-03-23
**Session scope:** §9 (Deferred Capabilities) + §10 (Test Requirements) + §1 (Purpose and Scope) + Coherence Review
**Commits:** `11c1eee` through `a6068f6` (3 section commits + coherence fix + CLAUDE.md + NEXT.md rewrite)
**SPEC status:** 2343 lines, 12/12 sections COMPLETE. Status updated from DRAFT to COMPLETE.

---

## What Was Done

| Section | Lines | Commit | Key Content |
|---------|-------|--------|-------------|
| §9 Deferred Capabilities | 77 | `11c1eee` | 16 capabilities cataloged (DC-01–DC-16), extension hook contract, activation model, absorbed-vs-deferred table |
| §10 Test Requirements | 233 | `58aff02` | Coverage rule for 34 checks + 29 invariants + 27 errors + 22 domain rules; 12 adversarial cases (ADV-E-01–12); C-7 mitigation; cross-engine contracts |
| §1 Purpose and Scope | 63 | `ac1c241` | Pipeline position, 3-phase architecture, D-011 structural enforcement, T-1–T-7 defense mapping, 5 scope exclusions |
| Coherence review | — | `ea82cfb` | Fixed 7 scrambled error code trigger conditions in §10 (EX-A-002–011, EX-C-001–005, EX-M-001–002, EX-V-001); status DRAFT→COMPLETE |
| CLAUDE.md update | 108 | `567c039` | Rewritten to reflect complete SPEC: 12-section reference table, current state, test patterns |
| NEXT.md rewrite | 110 | `a6068f6` | Rewritten for post-SPEC phase: integrity audit → contracts.py → build prep |

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

## What's Next — Step 3: Integrity Audit → contracts.py → Build Prep

NEXT.md has been rewritten with full instructions. The sequence is:

### 1. kr-integrity Audit (Architect — 1 session, new chat)

Run the 8-lens audit on the complete SPEC. Audit in chunks (§1–§3, §4–§5, §6–§8, §9–§10) to avoid context degradation. Every finding blocks. Fix findings before proceeding.

### 2. Rewrite `engines/excerpting/contracts.py` (CC task — 1 session)

The existing `contracts.py` (557 lines) was written for the old blocked SPEC. Prepare a CC handoff via kr-preparing-cc-handoffs after the integrity audit passes.

### 3. Build Prep (Architect — 1 session)

Run kr-build-prep: technology survey, architecture stubs, test skeleton, CLAUDE.md with implementation guidance.

**CLAUDE.md** — ✅ DONE (updated in this session to reflect complete SPEC).

---

## Session End Retrospective

**What went wrong:** The §10 error code trigger conditions were scrambled — I wrote plausible-sounding descriptions but assigned them to the wrong error codes (7 out of 27 were wrong). The coherence review's programmatic cross-check caught this. Without the check, the §8 catalog and §10 test requirements would have been inconsistent, and CC would have written tests for the wrong conditions.

**Root cause:** When writing §10, I composed trigger descriptions from memory of what each code meant instead of reading the §8 catalog line by line. The descriptions were semantically reasonable but mapped to the wrong code IDs. This is the same class of error as "never assign from memory" — the fix is always to copy from the source.

**Lesson:** When any section references IDs defined in another section (§10 referencing §8 error codes, §7 referencing §2.2 fields), the writing process must have the source section open and copy IDs verbatim. The coherence review's programmatic cross-check is the safety net, not the primary mechanism.

**Stale memory entries:** The "KR EXCERPTING ENGINE STATE" memory entry should be updated: SPEC is now COMPLETE (2343 lines, 12 sections), not BLOCKED. Contracts.py and CLAUDE.md update pending.

**Protocol changes to propose:** Add a "copy from source" step to the section writing protocol: before writing any section that references IDs from another section, open that section and keep it visible. This prevents the scrambled-description class of errors.

**What next session needs:** A new Claude Chat session. Start by cloning the repo, reading NEXT.md, reading this handoff file. Task: run kr-integrity 8-lens audit on the complete SPEC (2343 lines). Audit in 2–4 chunks to avoid context degradation. Fix all findings. Then prepare CC handoff for contracts.py rewrite.
