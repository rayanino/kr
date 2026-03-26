# NEXT — Excerpting Engine: Fix compute_page_range + First Real LLM Call

## Current Position

- **Baseline:** 588 tests passing (2 skipped), 0 failed
- **Commit:** `720b3ce3` (preamble gap fix ACCEPTED, review committed)
- **Blocker:** Mock integration test crashes in Phase 3 (`compute_page_range` IndexError on split chunks). Must fix before ANY LLM testing.

## Detailed Handoff

See `HANDOFF_NEXT_SESSION.md` in repo root for full context, including:
- Root cause analysis of the compute_page_range bug
- Task list with priority ordering
- Lessons from the previous session's self-critique
- Key file references

## Quick Summary of Tasks

1. **Prepare CC handoff** for compute_page_range fix (use `kr-preparing-cc-handoffs`)
2. **Review CC's fix** (use `kr-reviewing-cc-output`)
3. **Run mock integration test** end-to-end on ibn_aqil_v1
4. **First real LLM call** — ONE chunk, verify API wiring
5. **Housekeeping** — update CLAUDE.md, NEXT.md

## The Bug

```python
# engines/excerpting/src/phase3_deterministic.py:388
page_start = offsets[i - 1] if i > 0 else 0
# IndexError: list index out of range
```

Split chunks have `len(physical_pages) >> len(join_points) + 1` because split_oversized_division copies ALL physical_pages to each half but partitions join_points. The ibn_aqil_v1 crash: 73 pages, 39 join_points in chunk_0.

## Read First

1. `HANDOFF_NEXT_SESSION.md` — full handoff with all context
2. `engines/excerpting/src/phase3_deterministic.py:354-416` — the crashing function
3. `engines/excerpting/src/phase1_assembly.py:683-780` — split function that creates the mismatch
4. `reference/protocols/HANDOFF_PROTOCOL.md` — for writing the CC directive
5. `reference/protocols/REVIEW_PROTOCOL.md` — for reviewing CC's fix
