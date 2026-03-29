#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8

echo "=== KR Overnight Codex Launcher ==="
echo "Project: $(pwd)"
echo "Start: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo ""

python scripts/overnight_codex_task_generator.py --output overnight_codex/manifest.json
python scripts/overnight_codex_orchestrator.py --manifest overnight_codex/manifest.json --hours 8.0

echo ""
echo "Morning report: overnight_codex/MORNING_REPORT.md"
