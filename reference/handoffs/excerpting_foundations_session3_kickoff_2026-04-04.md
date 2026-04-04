# Excerpting Foundations Hardening — Session 3 Kickoff

**You are continuing the KR excerpting foundations hardening lane, session 3.**

Session 2 did the bulk of the hardening work: 250 owner ideas processed, 22 FPs, 10 prompt rules, 5 DRs synthesized, 912 tests pass, 1 code fix (V-P3-2 truncation), 1 prompt fix (EE-1 gharib exception). Session 3 transitions from "hardening the rules" to "proving the rules work at scale."

The owner is available 24/7 with Codex CLI, Gemini CLI, ChatGPT DR, Claude DR, and Gemini DR ready.

---

## STOP — Read these files in this exact order before doing ANYTHING

1. `NEXT.md` — current task and next steps (updated end of session 2)
2. `engines/excerpting/SPEC.md` §1.1b lines 30-90 — the 22 FPs (each refined by up to 5 adversarial reviews)
3. `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` — full ledger: all batch dispositions, coworker synthesis, DR findings
4. `engines/excerpting/reference/MERGED_ATOM_QUEUE.md` — the 556-line single source of truth (250 ideas, 88 MAQ atoms, 62 red-team tests, 0 silent drops)
5. `engines/excerpting/src/phase2_group.py` lines 43-120 — GROUP_SYSTEM_PROMPT (1440/1500 words)
6. `engines/excerpting/src/phase2_classify.py` lines 41-75 — CLASSIFY_SYSTEM_PROMPT (551 words, Rule A moved here by DR-5)
7. Run: `python -m pytest engines/excerpting/tests/ -q --ignore=engines/excerpting/tests/test_phase2_integration.py --ignore=engines/excerpting/tests/test_phase3_integration.py` — must be 912+ pass, 4 xfail
8. Run: `python scripts/check_prompt_spec_sync.py` — must PASS

**Do NOT start implementing until all 8 checks pass.**

---

## The Coworker Mandate — Session 3

**Every major task gets ALL available coworkers before finalization.** Session 2 proved this: Gemini found the Bukhari tarajim flaw. Codex found the V-P3-8 conflict. Five DRs found the FP-5/21 governance conflict, flag laundering, inter-phase contradiction, decoy confession, and severity deflation. NO single coworker was sufficient.

| Coworker | Primary Role | Unique Strength | How to Dispatch |
|----------|-------------|-----------------|-----------------|
| **Codex CLI** | Contract Guardian | Traces contracts, tests, regressions, file:line refs | `codex exec "..."` (direct) |
| **Gemini CLI** | Scholarly Auditor + System Architect | Arabic depth, Islamic methodology, cross-engine impact | `gemini -p "..."` (direct) |
| **DR (ChatGPT/Claude/Gemini)** | Adversarial Reasoner | Extended thinking, failure scenarios, what CLIs missed | Write prompt → owner relays |
| **CC (Claude Code)** | Orchestrator | Owns context, makes decisions, writes code, synthesizes | Does NOT self-review. Always dispatches coworkers. |

### Dispatch requirements PER PHASE

| Phase | Codex | Gemini | DR | Minimum |
|-------|-------|--------|-----|---------|
| A: Empirical validation | ✅ Verify test results | ✅ Validate Arabic quality of TUs | Optional | 2/3 |
| B: SPEC §6 formalization | ✅ Contract consistency | ✅ Scholarly accuracy BEFORE writing | ✅ At least 1 | 3/3 |
| C: Smoke run | ✅ All 5 NEXT.md teams | ✅ All 5 teams | ✅ All 3 DR sources | 5/5 teams |
| D: Owner review | CC renders | CC translates feedback | All 6 sources evaluate | 6/6 |

### Hard rules

- **No SPEC §6 entry is finalized without Gemini scholarly review.**
- **No prompt change without Codex contract check.**
- **No phase transition without at least 1 DR adversarial review.**
- **CC solo analysis is NEVER sufficient for content quality conclusions.** (mandatory-coworker-dispatch.md)

---

## Research First — Implementation Second

**Do NOT implement before researching.** This is the discipline session 2 got right. Every batch was dispatched to coworkers BEFORE implementation.

### Ready-to-use coworker prompts from DR-5

DR-5 (the self-hardened Claude review) provided 3 pre-written coworker relay prompts at `claude-adversarial_review_batch1_batch2_HARDENED.md` §9:

| Prompt | Target | Purpose | Location |
|--------|--------|---------|----------|
| §9.1 Codex | Contract verification | Verify 4 proposed changes against code | DR-5 §9.1 |
| §9.2 Gemini | Scholarly validation | Causal particles, Arabic markers, title retention, intro criterion | DR-5 §9.2 |
| §9.3 DR | Word budget strategy | Research prompt length vs accuracy, few-shot vs rules, compression | DR-5 §9.3 |

**Before word budget strategy:** Dispatch DR with the §9.3 prompt — this is research, not implementation.
**Before SPEC §6 formalization:** Dispatch Gemini to validate scholarly accuracy of each subsection.
**Before smoke run:** Dispatch Codex to verify integration test configuration.

---

## When to End Session 3 and Hand Off to Session 4

**Session 2 ran to near-exhaustion of context. Don't repeat this.**

### Natural handoff points (stop after completing one of these)

1. **After Phase A (validation) completes** — if validation reveals major regressions, STOP, document, hand off
2. **After Phase B (SPEC §6) completes** — natural milestone. Write session 4 kickoff and exit.
3. **After Phase C smoke run launches** — waiting for API results is dead context. Hand off immediately after launch.

### Context management triggers

- **At ~60% context:** Use `/smart-compact` proactively. After compaction, re-read: (1) SPEC §1.1b, (2) active phase checkpoint, (3) MERGED_ATOM_QUEUE active section, (4) ledger recent entries, (5) current GROUP_SYSTEM_PROMPT
- **At ~80% context:** STOP current work immediately. Write session 4 handoff (same structure as this document: reading order, coworker mandate, what went right/wrong, session-end triggers). Commit. Push. EXIT.
- **One engine per session** — no cross-engine work.

### Session 4 handoff requirements

The session 4 handoff MUST include:
- "STOP — read in this exact order" block
- Coworker mandate with per-phase dispatch table
- What session 3 got RIGHT and WRONG
- Session-boundary triggers
- Updated state tables
- All DR findings that remain unimplemented

---

## What the Owner Does (and Doesn't Do)

The owner is the CLIENT, not the project lead.

**Owner IS available to:**
- Relay DR prompts (owner relayed 5 DRs in session 2 — unprecedented)
- Answer non-technical study-experience questions ("when you study fiqh, do you read proofs before or after the ruling?")
- Enable/top up API keys
- React to rendered excerpts: "good / bad / confusing"

**Owner is NOT available to:**
- Drive technical direction (that's your job)
- Identify the next task (that's your job)
- Catch gaps in the plan (that's what coworkers are for)
- Review SPEC rules or code

**Take full authority. Make decisions. Execute. Report results. Never ask "should we do X or Y?" — decide and do.**

The owner said: "you are the strict 250 IQ boss with his business on the line." Act like it.

---

## Budget

| Category | Spent | Remaining | Notes |
|----------|-------|-----------|-------|
| Source engine | EUR 36.70 | EUR 63.30 / EUR 100 | Complete. No further spend. |
| OpenRouter v2 smoke | ~$55 | ~EUR 45 of dev budget | taysir + ibn_aqil completed |
| Empirical validation | ~$0.50 | ~$0.10-0.50 per atom_test.py chunk | Low cost |
| Phase 2 smoke (2 pkg re-run) | — | ~$6 per re-run | Budget for 3 iterations = ~$18 |
| Phase 3 full 5-book | — | ~$15-25 | One run. No re-runs budgeted. |

**Check budget BEFORE launching any API-calling script.** The `cost-guard.sh` hook provides automatic enforcement.

---

## What session 2 accomplished (DON'T redo)

- **MERGED_ATOM_QUEUE.md** built (556 lines, 250 ideas from F1-F8, zero silent drops)
- **6 batches processed:** Safety, Self-Containment, Boundary, Granularity, Tarjih/Proof, Other
- **22 FPs** in SPEC §1.1b: 4 new (FP-19/20/21/22), 3 strengthened (FP-2/3/5), all refined by 5 DRs
- **10 prompt rules** added, then refactored by DR-5: Rule A moved to CLASSIFY, Rule D removed (redundant), Rule B tightened, Rule C compressed. GROUP prompt: 1440/1500 words.
- **10 red-team tests** in `test_red_team_mutations.py` (5 pass, 4 xfail = real gaps, 1 gap FIXED)
- **V-P3-2 truncation fix** — condition-stripping detection (FP-21 gap closed)
- **EE-1 gharib exception** — numbered gharib items stay with hadith core
- **5 DR reviews synthesized** — each found genuinely new issues (see DR table below)
- **Empirical validation:** taysir chunk 0 produces 5 correct TUs (was 12 fragmented before refactoring)

## What session 2 got RIGHT (keep doing this)

1. **Dispatch ALL coworkers per task.** Every DR found issues CLIs missed. Every CLI found issues DRs missed.
2. **DR relay was fast.** 5 DRs in one session. Don't wait to batch DRs — send them immediately.
3. **Empirical validation after prompt changes.** atom_test.py confirmed DR-5 refactoring improved quality.
4. **Red-team tests find real bugs.** The condition-stripping test found a genuine vulnerability, fixed same session.
5. **Synthesize across all coworkers before implementing.** 3-column comparison (Codex | Gemini | DR) produces better decisions than any single source.

## What session 2 got WRONG (DON'T repeat)

1. **First Codex dispatch truncated by `| head -200`.** Don't pipe CLI coworker output through head/tail.
2. **Queue-builder agent took too long (13 min).** For cross-referencing tasks, do it yourself if you have context loaded.
3. **Batches 4-6 had ZERO coworker review.** Only Batch 1 got full coverage (4/4). This is a known gap.
4. **SPEC §6 formalization deferred.** ~30 SPEC-only atoms need formal text. This is the largest documentation debt.
5. **Ran to near-exhaustion of context.** Next session should hand off at ~80%, not at depletion.
6. **EE-1 FAIL flag in atom_test.py not investigated.** The grouping is correct but the test tool still reports FAIL. Stale check.

---

## The 5 DR Reports — What Each Contains

These files are at the repo root (to be archived in `engines/excerpting/reference/dr_reviews/`):

| DR | File | Unique Contribution | Use When |
|----|------|-------------------|----------|
| DR-1 | `chatgpt-Adversarial Review of Proposed Foundational Principles...md` | FP-19 text mutation trap (NEVER insert markers into primary_text). Tamper-evident provenance gap. | Implementing FP-19 display-layer |
| DR-2 | `claude-Adversarial review.md` | FP-5/FP-21 governance CONFLICT (blocking). 3-class error provenance (A/B/C). Genre-sensitive severity. Tashkeel phantom cascade. | Severity classification, error handling |
| DR-3 | `chatgpt-Adversarial Review of Excerpting Foundations Hardening Batches 1 and 2.md` | Flag laundering / alarm fatigue. Rule A over-aggression. Rule B exploitation. Priority ranking (D>C>A>B). | Operational safety, prompt tuning |
| DR-4 | `claude-Excerpting foundations hardening, Batches 1 & 2.md` | Decoy confession. Severity-deflation incentive. Closed-loop self-validation. FP-22 unverifiable without decision log. | LLM behavioral gaming defense |
| DR-5 | `claude-adversarial_review_batch1_batch2_HARDENED.md` | Inter-phase contradiction (Rule A). Rule B 3 exploits. Rule D 80% redundant. SPEC-prompt drift. Word budget crisis. **3 ready-to-use coworker prompts (§9).** | Prompt architecture, word budget, next dispatches |

---

## DR Findings NOT Yet Implemented

| DR | Finding | Status | Action for Session 3 |
|----|---------|--------|---------------------|
| DR-2 | Context-window silent truncation | DOCUMENTED | Verify Phase 1 split threshold ≤ model context window |
| DR-2 | Model version drift | DOCUMENTED | Model pinned in config; consider formal versioning FP |
| DR-2 | Prompt injection through source text | DOCUMENTED | Input sanitization rules exist; need hardening |
| DR-4 | FP-20 needs external comparator (source-text diff) | DOCUMENTED | V-P3-2 partially addresses; full diff deferred to Phase 3 |
| DR-4 | FP-22 needs decision log | DOCUMENTED | Expensive in tokens; deferred to Phase 3 build |
| DR-5 | Phase 1 assemble_text() silent page skip | DOCUMENTED | Medium priority; normalization boundary concern |
| DR-5 | FP-21 operational circularity — connect to detection mechanisms | DOCUMENTED | Add connection to Phase 3 consensus + owner review |
| DR-5 | FP-5 blast-radius protocol stub | DOCUMENTED | **Need before 30-book probe** |
| DR-5 | SPEC-prompt causal particle drift (2 vs 4 particles) | DOCUMENTED | Expand SPEC to match prompt, or trim; needs Gemini review |
| DR-5 | **Word budget strategy session** | **NOT DONE** | **BLOCKING for any more prompt additions. Use §9.3 DR prompt.** |

---

## Prompt Word Budget Crisis

**GROUP prompt: 1440/1500 words (60 headroom). CLASSIFY prompt: 551 words (~450 headroom).**

19 remaining prompt-affecting atoms from MERGED_ATOM_QUEUE.md cannot fit at ~3 words each. DR-5 identified 4 strategies:

1. **Compress existing rules** — unify overlapping rules in GROUP prompt, save 100-150 words
2. **Few-shot examples** — replace verbose rules with 2-3 worked examples of correct grouping
3. **Multi-prompt architecture** — genre-specific overlays (~200-300 words, selected at runtime)
4. **Raise the cap** — benchmark 1440 vs 2000 words empirically on same Arabic fixtures

**DR-5 recommends Options 2+4 as a dedicated pre-Batch-3 session.** This requires full coworker team input. Use the §9.3 DR prompt (research-based, not opinion-based).

**This must be resolved BEFORE adding more prompt rules.**

---

## Tools

| Tool | When to Use | Command |
|------|------------|---------|
| `atom_test.py` | After any prompt change | `python scripts/atom_test.py --package taysir --chunk 0` |
| `check_prompt_spec_sync.py` | After ANY prompt OR SPEC change | `python scripts/check_prompt_spec_sync.py` |
| `promptfoo` | For batch-level prompt regression testing | `promptfoo eval` (configure per phase) |
| `pytest` | Full deterministic suite (expect 912+ pass, 4 xfail) | `python -m pytest engines/excerpting/tests/ -q --ignore=..._integration.py` |
| `pyright` | Type-check modified files | `python -m pyright <modified_file>` |

**Run check_prompt_spec_sync.py after EVERY prompt or SPEC change. This is not optional.**

---

## Critical State at Session 3 Start

### Red-team test state

| Test | Status | Gap |
|------|--------|-----|
| Diacritic injection: shadda removal | PASS | — |
| Diacritic injection: alef maqsura swap | PASS | — |
| Diacritic injection: ZWSP | xfail | V-P3-2 normalizes away ZWSP |
| Diacritic injection: final damma | xfail | V-P3-2 min(len) prefix match |
| Identical text baseline | PASS | — |
| Segment contiguity | xfail | TeachingUnit doesn't validate contiguity |
| Boundary ordering | xfail | validate_excerpt() doesn't check start<end |
| Empty text fails loud | PASS | — |
| Condition-stripped ruling | PASS | **V-P3-2 length ratio check (FIXED session 2)** |
| EE-1 gharib exception | In prompt | Empirically validated, test tool FAIL flag may be stale |

### Coworker dispatch status

| Batch | Codex | Gemini | DR | Status |
|-------|-------|--------|-----|--------|
| B1: Safety | ✅ | ✅ | ✅ (5 DRs) | **CONFIRMED (4/4+)** |
| B2: Self-Containment | ✅ | ✅ | ✅ (2 DRs) | **CONFIRMED** |
| B3: Boundary | ❌ | ✅ | Partially | Needs Codex |
| B4-B6 | ❌ | ❌ | Partially | SPEC-only, lower priority |

### The 139 golden files

The owner's F1-F8 collections at `engines/excerpting/chatgpt_f{1-8}_collection/` contain 139 files of deep analysis. Session 2 processed these into 88 MAQ atoms. If session 3 discovers gaps during SPEC §6 formalization, GO BACK TO THE ORIGINAL FILES. The extraction is a starting point, not a cap.

---

## Session 3 Task Sequence

### Phase A: Validation & Cleanup (1-2 hours)

1. **Empirical validation on more chunks.** Run atom_test.py on ibn_aqil_v1 chunk 0 and taysir chunks 1-3. Verify refactored prompt produces correct TU counts.
   - Dispatch Codex: verify test results structurally
   - Dispatch Gemini: validate Arabic quality of produced TUs
2. **Investigate EE-1 FAIL flag.** The flag may be stale — grouping is correct but test tool reports FAIL.
3. **Fix remaining 4 xfail red-team tests.** Real V-P3-2 and contract gaps.
4. **Archive DR reports.** Move 5 DR files from repo root to `engines/excerpting/reference/dr_reviews/`.

### Phase B: SPEC §6 Formalization (2-3 hours)

5. **Formalize SPEC §6 entries** for ~30 SPEC-only atoms from Batches 4-6.
   - **BEFORE WRITING:** Dispatch Gemini for scholarly validation of each subsection
   - **BEFORE WRITING:** Dispatch Codex for contract consistency check
   - After writing: run check_prompt_spec_sync.py + full pytest
6. **Word budget strategy session.**
   - Dispatch DR with §9.3 prompt (research-based, evidence-backed)
   - Dispatch Codex + Gemini for technical and scholarly input
   - ONLY THEN decide: compress, few-shot, multi-prompt, or raise cap

### Phase C: Smoke Run Preparation (2-3 hours)

7. **Prepare Phase 1 smoke run** with hardened prompts.
   - Verify --max-chunks flag actually limits processing (known bug from NEXT.md)
   - Run on 2 packages (taysir + ibn_aqil_v1)
   - Dispatch Codex to verify integration test configuration
8. **Set up 5-team analysis.** Per NEXT.md Phase 1 plan: Boundary Quality, Classification, Arabic Fidelity, Consensus/Metadata, Coverage.

### Phase D: Owner Review (when smoke run completes)

9. **Render 20 excerpts for owner.** 10 best + 10 worst. Readable Arabic text, NOT JSON.
10. **Owner reacts:** "good / bad / confusing?" — CC translates reactions into technical actions.
11. **Dispatch all 6 sources** for the Phase 1 analysis.

---

## Deferred Work (Not Session 3's Problem Unless Needed)

- **Questionnaire phases 2-4** (30 remaining interactions): paused pending foundations hardening completion
- **Book digester vision** (F1 lines 409-430): multi-level preservation architecture, deferred
- **Linked-list excerpt chaining** (F1 lines 87-88): contracts enhancement, deferred
- **52 non-automated red-team tests**: backlog, prioritize during evaluation phase
- **Taxonomy engine session 2**: waiting on excerpting to stabilize

---

## The Ultimate Standard

An atom/task is NOT finalized unless:
- The raw owner source was read (if applicable)
- The structured collection files were read (if applicable)
- Counterexamples were searched
- Codex CLI reviewed and reported
- Gemini CLI reviewed and reported
- At least one DR reviewed and reported
- Implementation was made (SPEC/prompt/contract/test)
- Tests pass (pytest + pyright + sync check)
- Empirical validation passed (if prompt-affecting)
- The ledger was updated with full disposition and residual risks
- Cross-atom regression was checked

There is no "soft finalized." There is no "good enough." There is no "we'll come back later."

**THE LIBRARY IS THE MIND OF A SCHOLAR PUT ON A SCREEN.**
