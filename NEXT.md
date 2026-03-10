# NEXT — Phase C Implementation (Claude Code Session)

**READ FIRST:** `CLAUDE_CODE_PHASE_C_BRIEF.md` — 60-line executive summary.
**THEN READ:** `PHASE_C_TASK_SPEC.md` — full implementation spec (850+ lines).

---

## Context

The source engine pipeline is built and tested. Steps 0-2 are complete:
- **Step 0:** 12/13 fixtures pass with real LLM calls. Cost €1.80.
- **Step 1:** Code audit + 6 bug fixes. 768 tests passing.
- **Step 2:** Deterministic sweep on 2,519 books: zero crashes. 5 bugs fixed.
- **Deep audit:** 10 findings across prompt, consensus, inference, and engine code. 4 fixes queued as pre-requisites below.

Phase C is the first step that spends real API money: ~€11 for 73 books at ~$0.15/book.

## Your Task

Implement pre-requisites, write `scripts/run_phase_c.py`, test on 3 books, commit.

### Step 1: Pre-Requisites (do these first, in order)

| # | What | File | Why |
|---|------|------|-----|
| 0a | Fix `build_prompt_context` field names + add 5 fields | `metadata_inference.py` | 54% of books have muhaqiq data the LLM never sees |
| 0b | Add compiler/commentator/riwayah guidance to SYSTEM_MESSAGE | `inference_v1.py` | LLM may confuse compiler with author without guidance |
| 1 | Add `temperature=0` to consensus `_call_model` | `consensus.py` | Deterministic output, reduces token waste |
| 2 | Add `_full_consensus_result` field to MetadataInferenceResult | `metadata_inference.py` | Phase C script needs per-model LLM responses |
| 3 | Create Format B test fixture | `tests/fixtures/` | Bug fix has no regression test |
| 4 | Create `COST_LOG.json` | `tests/results/source_engine/` | Budget tracking infrastructure |

Run full test suite (768+) after each. See PHASE_C_TASK_SPEC.md for exact code changes.

### Step 2: Write `scripts/run_phase_c.py`

Sequential book processing. No parallelism. Full spec in PHASE_C_TASK_SPEC.md including:
- Processing flow (pre-pipeline extraction → pipeline via acquire_source → post-pipeline save)
- Monkey-patch for capturing per-model LLM responses
- Human gate configuration for temp libraries
- Budget protection with hard ceiling
- Resume/force/dry-run modes
- Per-book sanity checks (deterministic, no LLM calls)
- Gate abort handling (status: "gate_abort", not "error")
- Edition group analysis in PHASE_C_SUMMARY.json

### Step 3: Test on 3 Books

1. `أحكام الاضطباع والرمل في الطواف` — fixture 03_fiqh, has ground truth
2. `الأربعون النووية` — famous book, clean run expected
3. `الفقه الأكبر` — disputed attribution, should trigger gate abort

All 14 items in the 3-Book Test Checklist (end of PHASE_C_TASK_SPEC.md) must pass.

### Step 4: Commit

Commit the validated script. The owner runs `python scripts/run_phase_c.py` on all 73 books on his Windows machine.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE_CODE_PHASE_C_BRIEF.md` | Executive summary (read first) |
| `PHASE_C_TASK_SPEC.md` | Full implementation spec |
| `PHASE_C_PREFLIGHT_AUDIT.md` | Risk register, cost model, 10 verified findings |
| `PHASE_C_FINAL_SELECTION.md` | Book selection rationale |
| `scripts/phase_c_books.txt` | 73 book names |
| `tests/fixtures/phase_c_fixture_mappings.json` | 12 ground-truth mappings |
| `RESULT_PRESERVATION.md` | How every API result must be saved |

## Budget

€98 remaining (€100 ceiling − €1.80 Step 0). Phase C estimate: €10-15. Ceiling: €50.
The 3-book test costs ~€0.45. The full 73-book run costs ~€11.

## Do NOT

- Run the full 73 books (owner does that)
- Parallelize processing
- Use agent teams or subagents
- Reimplement the pipeline (use `acquire_source`)
- Strip schema text from user message (Command A needs it)
