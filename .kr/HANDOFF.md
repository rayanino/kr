> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff

## Session purpose
Foundations hardening session 1: initial SPEC hardening from F1-F8 owner feedback, empirical validation, 5 DR coworker reports, environment preparation for session 2.

## What this session completed

### SPEC Hardening (SPEC grew from 2387 to 2530 lines)
- FP-1 through FP-18 in §1.1b (18 foundational principles)
- EE-1 (explained+explanation unity) as §6.4b
- NC-1 (context resolution hierarchy) in §3
- MV-1 (minimum viability, 25-word floor) in §5.3
- Hadith sequence fix in §6.3, tarjih softened, C-SC-2 expanded with taqdir

### Prompt Changes (phase2_group.py)
- EE-1 general unity rule, expanded C-SC-2, tarjih MAY, FP-9 scope

### Empirical Validation
- Taysir: EE-1 2/2 PASS. Ibn Aqil: 32/32 PASS.

### Tools: `scripts/atom_test.py`, `scripts/check_prompt_spec_sync.py`

### 5 DR Reports archived at `evaluation_reports/dispatch_packets/foundations_hardening_2026_04_04/`

### Critical Discovery
F1-F8 collections contain 139 files of deep analysis. Session 1 only processed ~15. Remaining 124 files contain nonnegotiables, red-team tests, decision ladders, linking dependencies, and open questions that must be processed atom-by-atom.

## Session 2 completed (2026-04-04, 17 commits)

- Merged all F1-F8 owner feedback into MERGED_ATOM_QUEUE.md (250 ideas, 88 MAQ atoms, 0 silent drops)
- Processed 6 thematic batches: Safety (17 atoms), Self-Containment (5), Boundary (10), Granularity (17), Tarjih/Proof (21), Other (9)
- 22 FPs (FP-1 through FP-22) in SPEC §1.1b, hardened by 5 adversarial DR reviews
- 10 prompt rules in GROUP_SYSTEM_PROMPT (1440/1500 words) + 1 in CLASSIFY_SYSTEM_PROMPT
- 10 red-team tests (5 pass, 4 xfail documenting real gaps, 1 gap fixed)
- V-P3-2 truncation fix + EE-1 gharib exception
- Empirical validation: taysir chunk 0 = 5 correct TUs (was 12 fragmented)

## Current resume point

1. **START HERE:** Read `reference/handoffs/excerpting_foundations_session3_kickoff_2026-04-04.md`
2. Read SPEC §1.1b (22 FPs), MERGED_ATOM_QUEUE.md, FOUNDATIONS_HARDENING_LEDGER.md
3. Run tests (expect 912+ pass, 4 xfail) + check_prompt_spec_sync.py (expect PASS)
4. Follow the session 3 task sequence (Phase A-D)

Branch: `excerpting-foundations-hardening-20260404`. Do not finalize without coworker reports.
