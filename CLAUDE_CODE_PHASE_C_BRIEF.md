# Claude Code Phase C Brief — Read This First

**What:** Implement 6 pre-requisites, write `scripts/run_phase_c.py`, test on 3 books.
**Why:** First validation step that costs real API money (~€11 for 73 books). Every preventable bug wastes €10+.
**Budget ceiling:** €50. Expected spend: €10-15.

---

## Execution Order

```
1. Read PHASE_C_TASK_SPEC.md (the detailed spec — 810 lines, read it all)
2. Read CLAUDE.md (project conventions)
3. Implement pre-requisites 0a → 0b → 1 → 2 → 3 → 4 (in order)
4. Run full test suite after each pre-req (768+ tests must pass)
5. Write scripts/run_phase_c.py
6. Test on 3 books (fixture + clean new + gate-trigger)
7. Verify all 14 items in the 3-Book Test Checklist pass
8. Commit the validated script — owner runs the full 73 on Windows
```

## Critical Things That Will Waste Money If Wrong

**Pre-Req 0a (BLOCKER):** `build_prompt_context` uses wrong field names. 54% of books have muhaqiq data the LLM never sees. Fix FIRST.

**Gate abort (BLOCKER):** Books with disputed attribution (الفقه الأكبر) trigger `SourceEngineError(LOW_CONFIDENCE)` at Step 11. This is EXPECTED — catch it, save as `status: "gate_abort"`, not `status: "error"`. Otherwise `--resume` re-processes them.

**Human gate config:** Each temp library needs `configure_gate(gates_dir=..., auto_approve=True)`. Without it, gate checkpoints silently pollute the project's permanent files.

**Monkey-patch scope:** Patch `engine_mod.infer_metadata`, NOT `consensus_mod.evaluate`. Python's `from X import Y` creates a local copy — patching the source module doesn't work. The `global _captured_inference` declaration is required inside `process_book`.

## Architecture Decisions (Already Made)

- **Sequential processing** — no parallelism. Rate limits + monkey-patch pattern require it.
- **Pre-Req 0b is revertible** — if the system message change (compiler/commentator/riwayah guidance) causes regressions in the 3-book test, revert 0b and keep 0a.
- **Edition groups** computed post-run in PHASE_C_SUMMARY.json, not per-book.
- **Deterministic sanity checks** run after each book (see PHASE_C_TASK_SPEC.md auto-review section). No additional LLM calls for validation.

## Files to Read

| Priority | File | What |
|----------|------|------|
| 1 | `PHASE_C_TASK_SPEC.md` | Full spec: pre-reqs, script spec, output format, error handling, checklists |
| 2 | `CLAUDE.md` | Project conventions |
| 3 | `scripts/phase_c_books.txt` | 73 book names |
| 4 | `tests/fixtures/phase_c_fixture_mappings.json` | 12 ground-truth mappings |
| 5 | `RESULT_PRESERVATION.md` | How every API result must be saved |
| 6 | `PHASE_C_PREFLIGHT_AUDIT.md` | Risk register, cost model, verified findings |

## What NOT to Do

- Do NOT run the full 73 books. Test on 3, commit, owner runs the rest.
- Do NOT parallelize book processing. Sequential only.
- Do NOT use agent teams or subagents for this task.
- Do NOT reimplement the pipeline. Use `acquire_source()` and capture via monkey-patch.
- Do NOT strip the schema text from the user message (even though it's redundant for Opus). Command A needs it.

## Done When

The script passes the 3-Book Test Checklist (14 items), all 768+ tests pass, and the script is committed. The owner handles the full 73-book run on Windows.
