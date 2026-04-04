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

## Current resume point

1. **START HERE:** Read `reference/handoffs/excerpting_foundations_session2_kickoff_2026-04-04.md` — the detailed kickoff prompt
2. Read `engines/excerpting/reference/ATOM_PROTOCOL.md`
2. Read the extraction docs (if they exist) at `engines/excerpting/reference/F1_F8_COMPLETE_ATOM_EXTRACTION.md` and `CRITICAL_ATOMS_NONNEGOTIABLES_AND_REDTEAM.md`
3. If extraction docs don't exist: start reading `*_nonnegotiables.jsonl` and `*_red_team_tests.jsonl` from each F-collection
4. Process atoms one at a time. Every atom gets Codex CLI + Gemini CLI + DR coworker.
5. Use `scripts/atom_test.py` for empirical validation of prompt changes.

Do not skip files. Process atoms in THEMATIC BATCHES (per ATOM_PROTOCOL.md) — not isolated one-at-a-time, not all-at-once. Do not finalize without three coworker reports.
