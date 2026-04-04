# Excerpting Foundations Hardening — Session 3 Kickoff

**You are continuing the KR excerpting foundations hardening lane, session 3.**

Session 2 did the bulk of the hardening work: 250 owner ideas processed, 22 FPs, 10 prompt rules, 5 DRs synthesized, 912 tests pass. Session 3 transitions from "hardening the rules" to "proving the rules work at scale."

---

## STOP — Read these files in this exact order before doing ANYTHING

1. `NEXT.md` — current task and next steps list (updated end of session 2)
2. `engines/excerpting/SPEC.md` §1.1b lines 30-90 — the 22 FPs (FP-1 through FP-22, each refined by 5 adversarial reviews)
3. `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` — the full ledger with all batch dispositions and coworker synthesis
4. `engines/excerpting/reference/MERGED_ATOM_QUEUE.md` — the 556-line single source of truth (250 ideas, 88 MAQ atoms, 62 red-team tests)
5. `engines/excerpting/src/phase2_group.py` lines 43-120 — GROUP_SYSTEM_PROMPT (1440/1500 words)
6. `engines/excerpting/src/phase2_classify.py` lines 41-75 — CLASSIFY_SYSTEM_PROMPT (551 words, Rule A moved here in DR-5)
7. Run: `python -m pytest engines/excerpting/tests/ -q --ignore=engines/excerpting/tests/test_phase2_integration.py --ignore=engines/excerpting/tests/test_phase3_integration.py` — must be 912+ pass, 4 xfail
8. Run: `python scripts/check_prompt_spec_sync.py` — must PASS

---

## What session 2 accomplished (DON'T redo)

- **MERGED_ATOM_QUEUE.md** built (556 lines, 250 ideas from F1-F8, zero silent drops)
- **6 batches processed:** Safety, Self-Containment, Boundary, Granularity, Tarjih/Proof, Other
- **22 FPs** in SPEC §1.1b: 4 new (FP-19/20/21/22), 3 strengthened (FP-2/3/5), all refined by 5 DRs
- **10 prompt rules** added (+402 words, then refactored to 1440 by DR-5: Rule A moved to CLASSIFY, Rule D removed as redundant, Rule B tightened, Rule C compressed)
- **10 red-team tests** created (5 pass, 4 xfail documenting real gaps, 1 gap FIXED)
- **V-P3-2 truncation fix** — condition-stripping detection (FP-21 gap closed)
- **EE-1 gharib exception** — numbered gharib items stay with hadith core
- **5 DR reviews synthesized** — ChatGPT DR×2, Claude DR×3, all findings applied
- **Empirical validation:** taysir chunk 0 produces 5 correct TUs (was 12 fragmented before)

## What session 2 got RIGHT (keep doing this)

1. **Dispatch ALL coworkers per batch.** Gemini found the Bukhari tarajim flaw. Codex found the V-P3-8 conflict. DRs found the FP-5/21 governance conflict, flag laundering, and inter-phase contradiction. NO single coworker was sufficient.
2. **DR relay was fast.** The owner relayed 5 DRs in one session — unprecedented. Each DR found genuinely new issues. Don't wait to batch DRs.
3. **Empirical validation after prompt changes.** The atom_test.py run after DR-5 refactoring CONFIRMED the changes improved quality (5 correct TUs vs 12 fragmented). Always validate empirically.
4. **Red-team tests find real bugs.** The condition-stripping test found a genuine V-P3-2 vulnerability that was fixed in the same session.
5. **MERGED_ATOM_QUEUE.md as single source of truth.** Every atom has a MAQ-ID, batch assignment, and disposition. No silent drops.

## What session 2 got WRONG (DON'T repeat)

1. **First Codex dispatch was truncated.** Used `| head -200` which killed the output before Codex produced analysis. Don't pipe CLI coworker output through head/tail.
2. **Queue-builder agent took too long.** The subagent spent 13 minutes reading all files. For cross-referencing tasks, do it yourself if you have the context loaded.
3. **Batches 4-6 had NO coworker review.** Only Batch 1 got full coworker coverage (4/4). Batches 2-3 got partial (1-2/3). Batches 4-6 got zero CLI review because the prompt was full and they're SPEC-only. This is a known gap — the 5 DRs reviewed the principles but not the per-atom implementations.
4. **SPEC §6 formalization deferred.** ~30 SPEC-only atoms are documented in the ledger but not formal SPEC text. This creates a "ledger says X, SPEC doesn't mention X" consistency gap.
5. **EE-1 FAIL flag in atom_test.py appears to be a stale check.** The grouping is correct (hadith core unified) but the test tool still reports FAIL. Not investigated.

---

## Critical state at session 3 start

### Prompt word budget

| Prompt | Words | Cap | Headroom |
|--------|-------|-----|----------|
| GROUP_SYSTEM_PROMPT | 1440 | 1500 | 60 words |
| CLASSIFY_SYSTEM_PROMPT | 551 | No formal cap | ~450 words |

The GROUP prompt is nearly full. DR-5 identified 4 strategies for remaining atoms:
1. **Compress existing rules** (unify overlapping rules, save 100-150 words)
2. **Few-shot examples** (replace verbose rules with worked examples)
3. **Multi-prompt architecture** (genre-specific overlays)
4. **Raise the cap** (benchmark 1440 vs 2000 words empirically)

DR-5 recommends Options 2+4 as a dedicated pre-Batch-3 strategy session. This should happen before adding more prompt rules.

### Red-team test state

| Test | Status | Gap |
|------|--------|-----|
| Diacritic injection (shadda removal) | PASS | — |
| Diacritic injection (alef maqsura swap) | PASS | — |
| Diacritic injection (ZWSP) | xfail | V-P3-2 normalizes away ZWSP |
| Diacritic injection (final damma) | xfail | V-P3-2 min(len) prefix match |
| Identical text baseline | PASS | — |
| Segment contiguity | xfail | TeachingUnit doesn't validate |
| Boundary ordering | xfail | validate_excerpt() doesn't check |
| Empty text fails loud | PASS | — |
| Condition-stripped ruling | PASS | V-P3-2 length ratio check (FIXED in session 2) |
| EE-1 gharib exception | in prompt | Empirically validated |

### DR findings NOT yet implemented (documented only)

| DR | Finding | Status | Implementation |
|----|---------|--------|---------------|
| DR-2 | Context-window silent truncation | DOCUMENTED | Phase 1 chunking handles this; verify threshold alignment |
| DR-2 | Model version drift | DOCUMENTED | Model pinned in config; formal versioning FP deferred |
| DR-2 | Prompt injection through source text | DOCUMENTED | Input sanitization rules exist; need hardening |
| DR-4 | FP-20 needs external comparator (source-text diff) | DOCUMENTED | V-P3-2 partially addresses; full diff deferred |
| DR-4 | FP-22 needs decision log | DOCUMENTED | Expensive in tokens; deferred to Phase 3 build |
| DR-5 | Phase 1 assemble_text() silent page skip | DOCUMENTED | Medium priority; normalization boundary concern |
| DR-5 | FP-21 operational circularity | DOCUMENTED | Add connection to Phase 3 consensus + owner review |
| DR-5 | FP-5 blast radius protocol stub | DOCUMENTED | Need before 30-book probe |
| DR-5 | Word budget strategy session | NOT DONE | Blocking for Batch 3+ prompt additions |

### Coworker dispatch status

| Batch | Codex | Gemini | DR | Fully Confirmed? |
|-------|-------|--------|-----|-----------------|
| B1: Safety | ✅ | ✅ | ✅ (5 DRs) | **YES (4/4+)** |
| B2: Self-Containment | ✅ | ✅ | ✅ (2 DRs) | **YES** |
| B3: Boundary | ❌ | ✅ | Partially | NO — needs Codex |
| B4-B6 | ❌ | ❌ | Partially | NO — SPEC-only, lower priority |

---

## The 5 DR reports (archived for reference)

All DR files are in the repo root (untracked, owner's files):

1. `chatgpt-Adversarial Review of Proposed Foundational Principles for KR Excerpting Safety & Integrity Batch.md` — DR-1 (ChatGPT, Batch 1)
2. `claude-Adversarial review.md` — DR-2 (Claude, Batch 1)
3. `chatgpt-Adversarial Review of Excerpting Foundations Hardening Batches 1 and 2.md` — DR-3 (ChatGPT, Batch 1+2)
4. `claude-Excerpting foundations hardening, Batches 1 & 2.md` — DR-4 (Claude, Batch 1+2)
5. `claude-adversarial_review_batch1_batch2_HARDENED.md` — DR-5 (Claude, self-hardened final)

These should be moved to `reference/dr_reports/` and committed.

---

## Session 3 task sequence

### Phase A: Validation & Cleanup (1-2 hours)

1. **Empirical validation on more chunks.** Run atom_test.py on ibn_aqil_v1 chunk 0 and taysir chunks 1-3. Verify the refactored prompt produces correct TU counts and the hardened rules don't cause regressions.
2. **Investigate EE-1 FAIL flag.** The atom_test.py reports FAIL_ORPHANED_EXPLANATION on taysir chunk 0 TU-0, but the grouping is actually correct (hadith core unified in one 385-word unit). The test check may be stale.
3. **Fix remaining 4 xfail red-team tests.** The ZWSP and damma truncation tests document real V-P3-2 gaps. The segment contiguity and boundary ordering tests document contract gaps.
4. **Archive DR reports.** Move the 5 DR files from repo root to `reference/dr_reports/` and commit.

### Phase B: SPEC Formalization (2-3 hours)

5. **Formalize SPEC §6 entries.** ~30 SPEC-only atoms from Batches 4-6 are documented in the ledger but need formal SPEC subsection text. This is the largest remaining documentation debt.
6. **Word budget strategy.** Before any more prompt additions, decide: compress, few-shot, multi-prompt, or raise cap. DR-5 recommends a full-team session with Codex + Gemini input.

### Phase C: Smoke Run Preparation (2-3 hours)

7. **Prepare Phase 1 smoke run.** The prompt is hardened. Run the full integration test on 2 packages (taysir + ibn_aqil_v1) with the hardened prompts. Compare against the campaign baseline (2,303 excerpts, old prompts, Opus).
8. **Set up the 5-team analysis.** Per NEXT.md Phase 1 plan, spawn analysis subagents for boundary quality, classification, Arabic fidelity, consensus/metadata, and coverage.

### Phase D: Owner Review (when smoke run completes)

9. **Render 20 excerpts for owner.** Select 10 best + 10 worst from the smoke run. Render as readable Arabic text. Ask: "good, bad, or confusing?"

---

## The ultimate standard (unchanged from session 2)

An atom is NOT finalized unless: the raw owner source was read, the structured collection files were read, counterexamples were searched, at least 3 coworkers reviewed, implementation was made, tests pass, empirical validation passed, and the ledger was updated. There is no "soft finalized."

**THE LIBRARY IS THE MIND OF A SCHOLAR PUT ON A SCREEN.**
