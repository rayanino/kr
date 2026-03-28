#!/bin/bash
# Sprint Review — Claude Code Session
# Just run: bash scripts/review_sprint_cc.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

OUTDIR="overnight/results/sprint-review-cc"
mkdir -p "$OUTDIR"

echo "=== Sprint Review: Claude Code ==="
echo "Output: $OUTDIR/review.md"
echo ""

claude -p "REVIEW REQUEST: Weekend Sprint Autonomous System

I built a parallel autonomous work system for this KR project. Before launching it for a 20-hour run, I need your independent review. You have NO context from the session that built this — review it fresh.

FILES TO REVIEW (read all of them):
1. scripts/weekend_parallel.py — parallel coordinator (3 readonly workers + 1 write orchestrator)
2. scripts/generate_sprint_tasks.py — generates bughunt/edgecase/contract tasks
3. scripts/start_sprint.sh — launch script
4. overnight/sprint_manifest.json — 105 tasks (skim 10-15 representative tasks across different categories, dont read all 105)
5. The modifications to scripts/overnight_orchestrator.py — search for SPRINT_ANALYSIS_PROMPT, SPRINT_TEST_PROMPT, SPRINT_SCRIPT_PROMPT to find the new code

CONTEXT:
- 5-engine pipeline: Source (done) > Normalization (done) > Excerpting (done, CLI transformation in progress) > Taxonomy (unbuilt) > Synthesis (unbuilt)
- Passaging/atomization directories exist but are STALE from an old 7-engine plan — should never be referenced
- Excerpting src/ must not be modified by any task
- System runs 3 parallel readonly workers (bughunt/analysis via claude -p) + 1 sequential write worker (tests/scripts via overnight_orchestrator.py)
- Target: 20 hours of autonomous work

REVIEW CHECKLIST — be thorough on each:
1. SAFETY: Could any task corrupt data, modify frozen sources, or break the excerpting engine?
2. PARALLELISM: Are readonly tasks truly isolated? Could 3 concurrent claude -p processes conflict on file access or API rate limits?
3. TASK QUALITY: Are the bughunt prompts specific enough to find real bugs (not just style nits)? Sample 3-4 bughunt task prompts and evaluate.
4. EDGE CASES: Are the Arabic edge case tasks generating realistic test inputs? Will they actually test the code or just create standalone scripts?
5. STALE REFERENCES: Any tasks referencing passaging/atomization (stale engines that should not exist)?
6. SAFETY PROMPTS: Are the 3 new orchestrator safety prompts (SPRINT_ANALYSIS, SPRINT_TEST, SPRINT_SCRIPT) comprehensive enough? Any gaps?
7. RISK: What could go wrong during a 20-hour unattended run? Rate each risk HIGH/MEDIUM/LOW.
8. MISSING: What valuable work is NOT being done that should be?
9. WINDOWS: Any Windows-specific issues (encoding, paths, subprocess management)?
10. COST: Will 105 tasks with 3 parallel workers actually consume significant Max plan usage?

Write your complete review to overnight/results/sprint-review-cc/review.md
Be critical and specific. Quote file paths and line numbers. I want real issues, not reassurance." \
  --model opus \
  --dangerously-skip-permissions \
  --effort max \
  --no-session-persistence \
  --output-format text \
  2>&1 | tee "$OUTDIR/review.md"

echo ""
echo "=== Review complete: $OUTDIR/review.md ==="
