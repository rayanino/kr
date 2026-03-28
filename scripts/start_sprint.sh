#!/bin/bash
# KR Weekend Sprint v2 — Parallel Launcher
# Runs 3 readonly workers + 1 write orchestrator concurrently.
#
# Usage:
#   bash scripts/start_sprint.sh              # Full 20-hour sprint, 3 workers
#   bash scripts/start_sprint.sh --hours 8    # Custom duration
#   bash scripts/start_sprint.sh --workers 4  # Custom worker count
#   bash scripts/start_sprint.sh --dry-run    # Verify without executing
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

HOURS_VAL="20"
WORKERS_VAL="3"
DRY_RUN=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN="--dry-run"; shift ;;
        --hours) HOURS_VAL="$2"; shift 2 ;;
        --workers) WORKERS_VAL="$2"; shift 2 ;;
        *) shift ;;
    esac
done

MANIFEST="overnight/sprint_manifest.json"

# Count tasks
TASK_COUNT=$(python3 -c "import json; print(len(json.load(open('$MANIFEST', encoding='utf-8'))['tasks']))")

echo "=============================================="
echo "  KR Weekend Sprint v2 — Parallel Mode"
echo "=============================================="
echo "  Pipeline: Source > Norm > Excerpting > Taxonomy > Synthesis"
echo "  Tasks:    $TASK_COUNT"
echo "  Workers:  $WORKERS_VAL readonly + 1 write"
echo "  Duration: ${HOURS_VAL}h target"
echo "  Start:    $(date)"
echo "=============================================="
echo ""

# Verify manifest
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: Sprint manifest not found at $MANIFEST"
    exit 1
fi

# Pre-flight
echo "=== Pre-flight: baseline test suite ==="
if ! python -m pytest engines/source/tests/ engines/normalization/tests/ -x -q --tb=line 2>&1 | tail -3; then
    echo "ERROR: Baseline tests failed. Aborting."
    exit 1
fi
echo "Pre-flight: PASSED"
echo ""

# Safety snapshot
GIT_SNAPSHOT=$(git rev-parse HEAD)
echo "Safety snapshot: $GIT_SNAPSHOT"
echo "To rollback:     git reset --hard $GIT_SNAPSHOT"
echo ""

# Launch parallel coordinator
python scripts/weekend_parallel.py \
    --manifest "$MANIFEST" \
    --hours "$HOURS_VAL" \
    --workers "$WORKERS_VAL" \
    $DRY_RUN

echo ""
echo "=== Sprint Complete ==="
echo "End: $(date)"
echo "Safety snapshot: $GIT_SNAPSHOT"

if [ -z "$DRY_RUN" ]; then
    echo ""
    echo "=== Post-Sprint ==="
    git log --oneline "$GIT_SNAPSHOT"..HEAD 2>/dev/null | head -20 || echo "(no commits)"
    echo ""
    [ -f overnight/WEEKEND_REPORT.md ] && echo "Report: overnight/WEEKEND_REPORT.md"
    [ -f overnight/weekend_state.json ] && python3 -c "
import json
s = json.load(open('overnight/weekend_state.json'))
print(f\"Readonly: {s['readonly_completed']} done, {s['readonly_failed']} failed\")
print(f\"Write:    {s['write_completed']} done, {s['write_failed']} failed\")
"
fi
