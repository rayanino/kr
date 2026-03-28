#!/bin/bash
# Merge Sprint Reviews — run AFTER both review scripts complete
# Just run: bash scripts/merge_sprint_reviews.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

CC_REVIEW="overnight/results/sprint-review-cc/review.md"
CODEX_REVIEW="overnight/results/sprint-review-codex/review.md"
MERGED="overnight/results/sprint-review-merged.md"

echo "=== Merging Sprint Reviews ==="

# Check both exist
if [ ! -f "$CC_REVIEW" ]; then
    echo "ERROR: Claude Code review not found at $CC_REVIEW"
    echo "Run: bash scripts/review_sprint_cc.sh"
    exit 1
fi

if [ ! -f "$CODEX_REVIEW" ]; then
    echo "WARNING: Codex review not found at $CODEX_REVIEW"
    echo "Proceeding with Claude Code review only."
    CODEX_CONTENT="(Codex review not available)"
else
    CODEX_CONTENT="$(cat "$CODEX_REVIEW")"
fi

claude -p "You have two independent reviews of a weekend sprint system. Compare them and produce an actionable merged report.

=== CLAUDE CODE REVIEW ===
$(cat "$CC_REVIEW")

=== CODEX REVIEW ===
$CODEX_CONTENT

=== YOUR TASK ===
Produce overnight/results/sprint-review-merged.md with:

1. CRITICAL ISSUES (both reviewers found — highest confidence, must fix)
2. HIGH ISSUES (one reviewer found, seems valid — should fix)
3. MEDIUM ISSUES (one reviewer found, debatable — investigate)
4. CONTRADICTIONS (reviewers disagree — explain both sides)
5. CONSENSUS (what both reviewers agreed works well)
6. ACTION PLAN (ordered list of fixes to make before launching)

Be specific: for each issue, state which reviewer(s) found it and quote their reasoning." \
  --model opus \
  --dangerously-skip-permissions \
  --effort max \
  --no-session-persistence \
  --output-format text \
  2>&1 | tee "$MERGED"

echo ""
echo "=== Merged review: $MERGED ==="
