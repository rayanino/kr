# Session 4 Kickoff — Excerpting Foundations Hardening

## STOP — Read in this exact order:
1. `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` (§0 + §0.1 Autonomous Doctrine)
2. This handoff document
3. `engines/excerpting/CLAUDE.md`
4. `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` (recent entries only)
5. Continue from the NEXT SESSION DIRECTIVE below

## NEXT SESSION DIRECTIVE (v5.0 — autonomous)
- **Session type:** `batch-verification` (gate 5A in §1.6 — F-series intake complete but BCV never run)
- **First action:** Run `batch_inventory.py` on ALL 8 F-series collections (F1 already done: 16 files, F2: 8 files). Then begin muqabalah bi-l-asl on F1/F2 raw .txt files (Hafiz standard per §3A.4).
- **Decision framework:** Protocol §3A (Batch Lifecycle), §3B (Completion Gate), §3A.4 (4-factor threshold). SPEC §1.1b FPs for atom content decisions.
- **Owner involvement needed:** NONE for verification. Owner needed ONLY if a preference question arises during F1/F2 review.
- **Estimated scope:** 8 batches (F1-F8), ~139 total files. F1/F2 are Hafiz (100% sentence-level). F3-F8 are Faqih (15% sample + all flagged).

BEGIN IMMEDIATELY after reading. Do not wait for owner confirmation.

## Session 3 Accomplishments
- **Protocol v5.0 COMPLETE:** +331 lines. NEW §3A (Batch Lifecycle), §3B (Completion Gate), §3C (Ijazah). §4.3 fidelity indicator. §4.6 istidrak chain. §4.18 regression gate. §4.19 doctrine coherence. §5.4 variant preservation. §5.8 role separation. §8.5 calibration file. §0.1 Autonomous Operations Doctrine.
- **8 scripts built:** batch_inventory, batch_verification_init, batch_compute_coverage, batch_generate_trace_report, verify_batch_completion_gate, run_regression_suite, prompt_coherence_lint, atom_impact_diff
- **DR17 (Claude DR) analyzed:** Classical Islamic manuscript verification scholarly reference. 8 new requirements (R-19-R-26) integrated. Gemini CLI validated (5 corrections accepted).
- **Codex code review:** 4 CRITICAL + 7 HIGH findings fixed. Stubs now fail-closed. Schema aligned with protocol.
- **Gemini protocol review:** 6 HIGH consistency findings fixed (prompt-architect optimized RCoT prompt). Q-13/Q-14 added to Q-CLOSED. Lock-to-certificate mapping added.
- **Autonomous Doctrine committed:** NEXT.md top block + §0.1 + handoff template directive
- **6 commits pushed,** 915 tests pass, all checks green

## What Session 3 Got RIGHT (keep these patterns)
1. Prompt-architect before coworker dispatches — dramatically better output from both Codex and Gemini
2. Parallel exploration agents for DR17 analysis — cross-reference + concept extraction simultaneously
3. Gemini corrections accepted immediately and integrated — no defensiveness about DR17 mapping errors

## What Session 3 Got WRONG (avoid these)
1. Initial Codex dispatch with raw prompt produced shallow output. Always use prompt-architect first.
2. Codex structural review (first dispatch) timed out reading files. Give Codex focused scope, not "read 3 large files."
3. Scripts were stubs that exited 0 — Codex caught this as CRITICAL. Future stubs must fail-closed from the start.

## Context Management Report
- Peak context estimate: ~75% (approaching Zone 3)
- Compactions: 0
- Dispatch efficiency: ~60% of reads delegated to subagents
- Worktree agents: 1 (script building), general agents: 3 (DR analysis, script fixes)

## What Remains (Roadmap)
1. **THIS SESSION (4): BCV on F1-F8** — First real exercise of v5.0. batch_inventory.py already run on F1/F2. Complete inventory for F3-F8, then begin muqabalah.
2. **Session 5: Intake G1-G4 + SC1-SC3** — 7 new bundles at repo root
3. **Session 6: BCV on G/SC batches**
4. **Session 7: Debt clearance for B1-B3 PRELIMINARY atoms**
5. **Session 8: Prompt refactor** — 1474/1500 words, §4.11 nearly tripped
6. **Session 9+: Full-atom processing** — G/SC atoms through 7-stage lifecycle

## Budget Update
- EUR spent this session: 0.00 (protocol/script work, no API calls)
- EUR total: 36.70 / 100
- Budget remaining: 63.30

## Branch
`excerpting-foundations-hardening-20260404`

## Process Improvements Discovered (for protocol §8)
1. **Prompt-architect before dispatches** is now a saved feedback memory and should become a Hard Rule
2. **Stubs must fail-closed** — exit 1 with "not implemented" rather than exit 0 with fake success
3. **Gemini with RCoT framework** finds structural inconsistencies that flat prompts miss entirely
