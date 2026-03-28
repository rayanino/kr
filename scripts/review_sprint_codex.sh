#!/bin/bash
# Sprint Review — Codex Session
# Just run: bash scripts/review_sprint_codex.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

OUTDIR="overnight/results/sprint-review-codex"
mkdir -p "$OUTDIR"

echo "=== Sprint Review: Codex ==="
echo "Output: $OUTDIR/review.md"
echo ""

codex exec "Review the weekend sprint autonomous system in this KR project repository. This is a code review — be critical and specific.

READ THESE FILES:
- scripts/weekend_parallel.py (parallel coordinator — 3 readonly + 1 write worker)
- scripts/generate_sprint_tasks.py (task generator for bughunt/edgecase/contract tasks)
- scripts/start_sprint.sh (launch script)
- overnight/sprint_manifest.json (105 tasks — skim 10-15 representative ones)
- scripts/overnight_orchestrator.py (search for SPRINT_ANALYSIS_PROMPT to find the new sprint code)

CONTEXT:
- KR is a 5-engine Islamic scholarly text pipeline: Source > Normalization > Excerpting > Taxonomy > Synthesis
- 3 engines complete, 2 unbuilt. Excerpting is under active CLI backend transformation — must not be modified.
- Passaging and Atomization engine directories exist but are STALE artifacts from an old plan. They should NOT be referenced anywhere.
- The sprint runs 105 tasks autonomously for 20 hours: 53 readonly (3 parallel workers) + 52 write (sequential).

CHECK FOR:
1. Safety — could any task corrupt data, modify frozen sources, or break excerpting engine?
2. Parallelism — could 3 concurrent claude -p processes conflict? File access races? API rate limits?
3. Task prompt quality — are bughunt prompts specific enough for real bugs? Sample 3-4 and evaluate.
4. Stale references — any tasks mentioning passaging or atomization engines?
5. Windows issues — encoding, paths, subprocess management on Windows 11?
6. Biggest risk during 20-hour unattended run?
7. What valuable work is missing?

Write your complete review to overnight/results/sprint-review-codex/review.md with specific file paths and line numbers for every issue found." \
  2>&1 | tee "$OUTDIR/review.md"

echo ""
echo "=== Review complete: $OUTDIR/review.md ==="
