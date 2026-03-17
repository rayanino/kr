# NEXT — Repo Cleanup + Agent Team Discussion

## Current position: Deliverables 1-2 COMPLETE → Repo cleanup next
## What to do: Clean up repo for normalization engine project
## Context: Blueprint and Playbook committed. Repo has ~27 .md files at root from Phase D evaluation. Need to archive/remove stale files.
## Owner action needed: YES — This is a Claude Code task. Hand off with the prompt below.

---

## Completed

1. ✅ `reference/ENGINE_BUILD_BLUEPRINT.md` (1,018 lines) — Concrete
   engine build recipe distilled from source engine experience
2. ✅ `reference/DECISION_PLAYBOOK.md` (700 lines) — Domain decision
   institutional memory (trigger→action pairs)

## Remaining

3. **Repo cleanup** — Claude Code task. Remove stale files, archive
   completed work, ensure the repo is clean and navigable for the
   normalization engine project.

4. **After cleanup:** Discuss agent team architecture for autonomous
   building (Claude Chat discussion).

---

## Claude Code Handoff — Repo Cleanup

### Context

The repo root has ~27 .md files, most from the Phase D evaluation.
Many should be archived. The source engine is COMPLETE — its files
should be organized for reference, not cluttering the working
directory.

### Read First

1. `NEXT.md` (this file)
2. `ls -la *.md` at repo root — see what's there
3. `reference/archive/` — existing archive structure

### Tasks

1. **Archive Phase D evaluation files at root.** Move to
   `reference/archive/sessions/phase_d/`:
   - All `PHASE_D_*.md` files from root
   - `EVALUATION_QUICK_REFERENCE.md`

2. **Archive Claude Code handoff files.** Move to
   `reference/archive/sessions/handoffs/`:
   - All `CLAUDE_CODE_*.md` files from root

3. **Archive completed reference docs that are no longer active.** Move to
   `reference/archive/`:
   - `STEP4_PREPARATION_PLAN.md` (if at root — completed)

4. **Keep at root (do NOT archive):**
   - `NEXT.md` — always at root
   - `CLAUDE.md` — always at root
   - `KNOWLEDGE_INTEGRITY.md` — governing document
   - `RESULT_PRESERVATION.md` — governing document
   - `SILENT_FAILURES.md` — governing document
   - `COST_LOG.json` — active tracking
   - `OPEN_PROBLEMS.md` — active

5. **Verify no broken references.** After moves, grep for moved
   filenames in active .md files at root and in `reference/`. Fix
   any broken paths.

6. **Update root CLAUDE.md** if it references files that moved.

### Verification

After cleanup:
- `ls *.md` at root should show ≤10 files
- `reference/` should be well-organized
- `git status` should show moves, not deletes (use `git mv`)
- No broken references in active documents

### Commit

`git commit -m "Repo cleanup: archive Phase D evaluation and completed handoff files"`
