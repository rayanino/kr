#!/bin/bash
# KR Weekend Sprint Launcher
# Runs the overnight orchestrator with the sprint manifest for extended autonomous work.
#
# Usage:
#   bash scripts/start_sprint.sh              # Full 20-hour sprint
#   bash scripts/start_sprint.sh --hours 8    # Custom duration
#   bash scripts/start_sprint.sh --dry-run    # Verify without executing
set -euo pipefail
cd "$(dirname "$0")/.."

HOURS="${1:---hours}"
HOURS_VAL="${2:-20}"
DRY_RUN=""

# Parse args
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN="--dry-run" ;;
        --hours) ;;
        *) HOURS_VAL="$arg" ;;
    esac
done

echo "╔═══════════════════════════════════════════════════╗"
echo "║           KR Weekend Sprint System                ║"
echo "╠═══════════════════════════════════════════════════╣"
echo "║ Pipeline: Source→Norm→Excerpting→Taxonomy→Synth  ║"
echo "║ Tasks:    55 across 6 waves                      ║"
echo "║ Duration: ${HOURS_VAL} hours target                        ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "Start: $(date)"
echo ""

# Verify manifest exists
MANIFEST="overnight/sprint_manifest.json"
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: Sprint manifest not found at $MANIFEST"
    exit 1
fi

# Count tasks in manifest
TASK_COUNT=$(python3 -c "import json; print(len(json.load(open('$MANIFEST'))['tasks']))")
echo "Sprint manifest: $TASK_COUNT tasks loaded"

# Pre-flight: verify tests pass
echo ""
echo "=== Pre-flight: Running baseline test suite ==="
if ! python -m pytest engines/source/tests/ engines/normalization/tests/ -x -q --tb=line 2>&1 | tail -5; then
    echo "ERROR: Baseline tests failed. Aborting sprint."
    exit 1
fi
echo "Pre-flight: PASSED"

# Record safety snapshot
GIT_SNAPSHOT=$(git rev-parse HEAD)
echo ""
echo "Safety snapshot: $GIT_SNAPSHOT"
echo "To rollback: git reset --hard $GIT_SNAPSHOT"
echo ""

# Record baseline test count
BASELINE_TESTS=$(python -m pytest engines/source/tests/ engines/normalization/tests/ engines/excerpting/tests/ --co -q --no-header 2>/dev/null | tail -1 || echo "unknown")
echo "Baseline test count: $BASELINE_TESTS"
echo ""

# Launch orchestrator
echo "=== Launching Sprint Orchestrator ==="
echo ""
python scripts/overnight_orchestrator.py \
    --manifest "$MANIFEST" \
    --hours "$HOURS_VAL" \
    $DRY_RUN

echo ""
echo "=== Sprint Complete ==="
echo "End: $(date)"
echo "Safety snapshot was: $GIT_SNAPSHOT"

# Post-sprint summary
if [ -z "$DRY_RUN" ]; then
    echo ""
    echo "=== Post-Sprint Summary ==="
    FINAL_TESTS=$(python -m pytest engines/source/tests/ engines/normalization/tests/ engines/excerpting/tests/ --co -q --no-header 2>/dev/null | tail -1 || echo "unknown")
    echo "Final test count: $FINAL_TESTS"
    echo "Commits since snapshot:"
    git log --oneline "$GIT_SNAPSHOT"..HEAD 2>/dev/null || echo "(none)"
    echo ""
    if [ -f overnight/WEEKEND_REPORT.md ]; then
        echo "Weekend report: overnight/WEEKEND_REPORT.md"
    fi
fi
