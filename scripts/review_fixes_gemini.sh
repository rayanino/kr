#!/bin/bash
# Review ONLY the fixes applied after Codex + CC reviews.
# Run: bash scripts/review_fixes_gemini.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

OUTDIR="overnight/results/sprint-review-gemini"
mkdir -p "$OUTDIR"

echo "=== Sprint Fix Review: Gemini ==="

# Get the orchestrator diff (tracked file)
ORCH_DIFF=$(git diff HEAD -- scripts/overnight_orchestrator.py)

# Get key sections of the new files (they're untracked)
PARALLEL_KEY=$(sed -n '165,230p' scripts/weekend_parallel.py)
BOOKEND_KEY=$(sed -n '395,440p' scripts/weekend_parallel.py)
GENERATOR_KEY=$(sed -n '130,155p' scripts/generate_sprint_tasks.py)

gemini -p "FOCUSED REVIEW: Fixes applied to weekend sprint system after Codex and Claude Code reviews found 14 issues.

FIXES APPLIED (verify each actually solves the problem):

1. Bash removed from readonly workers — tool list now Read,Glob,Grep only:
$GENERATOR_KEY

2. Budget cap added — always pass --max-budget-usd:
$PARALLEL_KEY

3. Bookend tasks separated from parallel pool — run sequentially after:
$BOOKEND_KEY

4. Cross-queue dependencies removed — 4 validation tasks no longer depend on readonly task (done in manifest JSON)

5. Excerpting L2 protection widened:
$ORCH_DIFF

6. Edge case test paths moved from tests/ to engines/source/tests/
7. Bughunt prompts tightened — excerpting gets no fix suggestions
8. Contract targets fixed for shared modules

CHECK:
1. Does the batch scheduling logic in weekend_parallel.py correctly enforce deadlines? The while loop should check time between batches.
2. Does the bookend separation work? regular_readonly vs bookend_readonly split, bookends run after pool.
3. Is the budget cap correct? effective_budget = max(task.max_budget_usd, 5.0) should always produce >= 5.0.
4. Could the readonly tool restriction (Read,Glob,Grep only — no Bash) prevent any legitimate analysis work?
5. Any new bugs introduced by these fixes?

Write your review to $OUTDIR/review.md" \
  2>&1 | tee "$OUTDIR/review.md"

echo ""
echo "=== Gemini review: $OUTDIR/review.md ==="
