#!/usr/bin/env bash
# F1 enforcement: Stop hook that blocks when analysis files are modified
# without recent coworker dispatch evidence.
#
# Checks:
#   1. Are there modified analysis/report/evaluation .md files in git?
#   2. Is there a recent entry in .kr/runtime/dispatch_log.jsonl?
#   3. If (1) YES and (2) NO → block with dispatch reminder
#
# Exit:
#   0 + no JSON = allow stop
#   0 + {"decision":"block","reason":"..."} = force continuation

set -uo pipefail

INPUT=$(cat)

# CRITICAL: prevent infinite loop (same guard as stop-quality-gate.sh)
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [ "$STOP_ACTIVE" = "true" ]; then
    exit 0
fi

# Skip in overnight/rapid mode
if [ "${KR_OVERNIGHT:-}" = "1" ] || [ "${CLAUDE_RAPID_MODE:-}" = "1" ]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Check for modified analysis files
ANALYSIS_FILES=$(git diff --name-only HEAD 2>/dev/null | grep -iE '(report|findings|evaluation|analysis|assessment|PHASE_.*SUMMARY)\.md$' || true)

if [ -z "$ANALYSIS_FILES" ]; then
    exit 0  # No analysis files modified — no enforcement needed
fi

# Check dispatch log for recent entries (within last 4 hours)
DISPATCH_LOG="$CLAUDE_PROJECT_DIR/.kr/runtime/dispatch_log.jsonl"
if [ -f "$DISPATCH_LOG" ]; then
    RECENT=$(python3 -c "
import json, sys
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=4)
for line in open('$DISPATCH_LOG', encoding='utf-8'):
    try:
        e = json.loads(line.strip())
        ts = datetime.fromisoformat(e.get('timestamp','').replace('Z','+00:00'))
        if ts > cutoff:
            print('RECENT')
            sys.exit(0)
    except: pass
" 2>/dev/null)
    if [ "$RECENT" = "RECENT" ]; then
        exit 0  # Recent dispatch found — OK
    fi
fi

# Block: analysis files modified without dispatch
REASON="DISPATCH REQUIRED: Analysis file(s) modified without recent coworker dispatch (>4h). Modified: $(echo "$ANALYSIS_FILES" | tr '\n' ', '). Dispatch coworkers before concluding, or mark findings as [PRELIMINARY]."
echo "{\"decision\":\"block\",\"reason\":$(echo "$REASON" | jq -Rs .)}"
exit 0
