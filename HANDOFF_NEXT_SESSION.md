# Next Session Handoff — Excerpting Engine: compute_page_range Fix + First Real LLM Call

## What Just Happened (Previous Session Summary)

**Preamble gap fix: ACCEPTED.** Commits `1705ca5a` (CC implementation) + `b6b72d28` (review fixes) + `2baec633` (review checklist). All 5 experiment packages now produce valid Phase 1 chunks. 588 tests passing, 2 skipped, 0 failed.

The fix: `_complete_division_tree()` in `phase1_assembly.py` inserts synthetic leaf DivisionNodes for parent content not covered by children (preamble gaps). Previously 2–29% of content per source was silently lost. Two review findings were found and fixed: F-1 (suppress spurious EX-A-006 warnings on synthetic preambles) and F-3 (add oversized preamble split test).

**Critical self-assessment from the outgoing session** (read these — they are real failures to avoid repeating):
1. **Standing Order 7 was never run during the review.** The unconstrained adversarial pass that catches issues outside the protocol was skipped. Run it in every review.
2. **Independent discovery was compromised.** CC's adversarial audit was in context from the start, so all "findings" were actually confirmations. If CC's audit arrives at session start, read it ONLY during Pass 3 cross-reference — do Pass 1 and Pass 2 independently first.
3. **F-1 fix scope is narrower than designed.** CC implemented `_pre`-only check; the architect specified `_pre`, `_gap_`, `_post`. Acceptable today (zero gap/post instances), but should be broadened for defensive consistency.
4. **Tasks 2 and 3 from the previous session were silently dropped.** Always enumerate all tasks at session start and explicitly address each.

## Current State

- **Commit:** `2baec633` (master HEAD)
- **Tests:** 588 passed, 2 skipped (Phase 2 integration — need LLM)
- **CLAUDE.md:** STALE — says 519 tests, actual is 588. Update after current tasks.
- **NEXT.md:** STALE — still references the preamble fix. Must be updated.

## Blocking Bug: compute_page_range IndexError

The mock integration test crashes in Phase 3:

```
File "engines/excerpting/src/phase3_deterministic.py", line 388, in compute_page_range
    page_start = offsets[i - 1] if i > 0 else 0
                 ~~~~~~~^^^^^^^
IndexError: list index out of range
```

**Root cause:** `compute_page_range()` (line 354) assumes `len(join_points) == len(physical_pages) - 1`. This holds for unsplit chunks but NOT for split chunks. When `split_oversized_division` splits a chunk, it partitions `join_points` between the split halves but copies ALL `physical_pages` to each half (this is correct — I-AC-4 requires all split chunks share constituent_unit_indices). Result: chunk_0 gets 73 physical_pages but only 39 join_points.

**The crashing chunk in ibn_aqil_v1:**
```
div_src_test0001_2_008 ("الابتداء") — 73 pages, split into 2 chunks:
  chunk_0: 73 pages, 39 join_points, 3160 words
  chunk_1: 73 pages, 33 join_points, 3120 words
```

**Fix approach:** The function uses join_point offsets to determine which physical page contains a given character position. For split chunks, the join_points only cover the chunk's text slice, but physical_pages covers the entire original division. The fix should either: (a) filter physical_pages to only those relevant to this chunk's text range, or (b) build page boundaries from join_points without assuming 1:1 correspondence with physical_pages. Option (a) is cleaner — the split function should assign only the relevant physical pages to each split chunk.

## Your Tasks (in order)

### TASK 1: Prepare CC handoff for compute_page_range fix

Use `kr-preparing-cc-handoffs` skill. Follow `reference/protocols/HANDOFF_PROTOCOL.md` (9 steps). Write NEXT.md with:
- Root cause explanation (above)
- Exact file and line numbers
- The fix approach (choose between option a and b, or design a better one)
- Tests to add (split chunk with mismatched page/join_point counts)
- Verification: mock integration test must pass on all 5 packages

**Read first before writing the handoff:**
1. `engines/excerpting/src/phase3_deterministic.py` lines 354–416 (`compute_page_range`)
2. `engines/excerpting/src/phase1_assembly.py` lines 683–780 (`split_oversized_division`)
3. `engines/excerpting/tests/test_phase3_deterministic.py` — existing compute_page_range tests (search for "F-DET-6")

**Include in NEXT.md — explicit stop clause:** "Do NOT implement anything beyond what is specified here. After completing the fix, commit and push. Do NOT proceed to the next task."

### TASK 2: Review CC's fix (after CC completes Task 1)

Use `kr-reviewing-cc-output` skill. Follow `reference/protocols/REVIEW_PROTOCOL.md`. This is a small fix (likely <30 lines), so the review should be focused:
- Verify the fix handles split AND merged AND unsplit chunks correctly
- Run mock integration test on all 5 packages
- Verify 0 crashes, sensible PageRange output
- Remember: read CC's audit ONLY in Pass 3, not before

### TASK 3: Run mock integration test end-to-end

After Task 2 is ACCEPTED:
```bash
cd /home/claude/kr
PYTHONPATH=. python scripts/run_integration_test.py \
  --mock \
  --package-path experiments/format_diversity_test/packages/ibn_aqil_v1 \
  --output-dir /tmp/mock_integration_run
```
Should complete without errors. Inspect the output: `phase1_chunks.json`, `phase2a_classifications/`, `phase2b_groupings/`, Phase 3 excerpts. This proves the full pipeline works end-to-end with mock LLM responses.

### TASK 4: First real LLM call smoke test

After Task 3 passes, make ONE real LLM call to verify API wiring:
- Pick the smallest chunk from ibn_aqil_v1 (likely one of the preamble chunks)
- Run the integration test with `--real` instead of `--mock` on just that one chunk (or modify the script to run a single chunk)
- The goal is NOT quality evaluation — just verify: OpenRouter connection works, Opus 4.6 responds, Instructor parsing succeeds, output has correct schema
- If this works, the next session can begin the full 5-book LLM integration test per `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md`

### TASK 5: Housekeeping

- Update `engines/excerpting/CLAUDE.md` build metrics (588 tests, actual line counts)
- Update `NEXT.md` for the next session (5-book LLM integration test — Phase A fixture selection)
- If the F-1 fix scope issue bugs you, broaden the `_pre`-only check in `phase1_assembly.py:1505` to also cover `_gap_` and `_post` (one-line change, commit directly)

## Session Start Protocol (do these FIRST — no exceptions)

1. Clone or pull the repo
2. Read `NEXT.md` (will be stale — that's expected, use this handoff instead)
3. `git log --oneline -5`
4. `ls /mnt/skills/user/` — pick relevant skills
5. Read `reference/protocols/QUALITY_AXIOM.md` — governing principle
6. DRIFT CHECK: "Does this still serve the goal — a study companion where the owner reads an entry and sees what every scholar said, where they agree/differ/why, all cited to frozen sources?" Answer with evidence from the repo.

## Key File References

| File | What | Why |
|------|------|-----|
| `engines/excerpting/src/phase3_deterministic.py:354` | `compute_page_range()` | The crashing function |
| `engines/excerpting/src/phase1_assembly.py:683` | `split_oversized_division()` | Creates the mismatched page/join_point state |
| `engines/excerpting/src/phase1_assembly.py:1505` | F-1 fix location | The `_pre`-only check that could be broadened |
| `scripts/run_integration_test.py` | Mock/real integration test | Use `PYTHONPATH=. python scripts/run_integration_test.py --mock --package-path ...` |
| `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md` | Full test protocol | For after the smoke test succeeds |
| `reference/archive/sessions/reviews/review_preamble_fix.md` | Last review checklist | Shows what was verified |
