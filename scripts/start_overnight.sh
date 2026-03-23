#!/bin/bash
# KR Overnight Autonomous Session Launcher
# Usage: bash scripts/start_overnight.sh [manifest.json]
set -euo pipefail

cd "$(dirname "$0")/.."
export KR_OVERNIGHT=1
export PYTHONIOENCODING=utf-8

echo "=== KR Overnight Session Launcher ==="
echo "Project: $(pwd)"
echo "Time: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo ""

# Pre-flight: verify clean git state (Python check — matches orchestrator's git_is_clean)
DIRTY=$(git status --porcelain | python -c "
import sys
ignored = ('overnight/', 'results/', '.claude/scheduled_tasks', '.claude/session_state')
for line in sys.stdin:
    line = line.rstrip()
    if not line: continue
    path = line[3:] if len(line) > 3 else line.strip()
    if not any(path.startswith(p) for p in ignored):
        print(path)
")
if [ -n "$DIRTY" ]; then
    echo "ERROR: Uncommitted changes detected. Commit or stash before starting."
    echo "$DIRTY"
    exit 1
fi

# Generate task manifest (or use provided one)
MANIFEST="${1:-}"
if [ -z "$MANIFEST" ]; then
    echo "Generating task manifest..."
    python scripts/overnight_task_generator.py --output overnight/manifest.json
    MANIFEST="overnight/manifest.json"
    echo ""
fi

echo "Starting overnight session with: $MANIFEST"
echo "Press Ctrl+C to stop gracefully."
echo ""

# Run orchestrator
python scripts/overnight_orchestrator.py \
    --manifest "$MANIFEST" \
    --hours 8.5 \
    --max-cost-usd 50.0

echo ""
echo "Overnight session complete. See overnight/MORNING_REPORT.md"
