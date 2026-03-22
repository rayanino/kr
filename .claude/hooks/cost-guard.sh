#!/usr/bin/env bash
# Cost Overspend Guard for KR
# Checks COST_LOG.json before API calls and blocks if budget exceeded.
#
# Wiring (add to settings.json PreToolUse → Bash matcher for python.*openrouter):
#   See .claude/HOOK_WIRING.md for exact JSON.
#
# Budget threshold: $100 (configurable via KR_BUDGET_LIMIT env var)

set -euo pipefail

BUDGET_LIMIT="${KR_BUDGET_LIMIT:-100}"
COST_LOG="$CLAUDE_PROJECT_DIR/tests/results/source_engine/COST_LOG.json"

# Read tool input from stdin
input=$(cat)

# Extract command
CMD=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [ -z "$CMD" ]; then
    exit 0
fi

# Only check for commands that might make API calls
if ! echo "$CMD" | grep -qiE 'openrouter|litellm|instructor|api.*call|run_pipeline'; then
    exit 0
fi

# Check current spending
if [ -f "$COST_LOG" ]; then
    TOTAL_COST=$(python3 -c "
import json, sys
try:
    with open('$COST_LOG') as f:
        data = json.load(f)
    total = sum(p.get('cost_eur', 0) for p in data.get('phases', {}).values())
    print(f'{total:.2f}')
except Exception:
    print('0.00')
" 2>/dev/null)

    if [ -n "$TOTAL_COST" ]; then
        OVER=$(python3 -c "print('yes' if float('$TOTAL_COST') >= float('$BUDGET_LIMIT') else 'no')" 2>/dev/null)
        if [ "$OVER" = "yes" ]; then
            TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
            echo "[$TIMESTAMP] COST GUARD: Blocked API call. Current spend: €$TOTAL_COST >= limit: €$BUDGET_LIMIT" >> "$CLAUDE_PROJECT_DIR/.claude/cost_guard.log" 2>/dev/null || true
            echo "{\"decision\":\"block\",\"reason\":\"Cost guard: Budget limit reached (€$TOTAL_COST / €$BUDGET_LIMIT). Do not make additional API calls.\"}"
            exit 0
        fi
    fi
fi

exit 0
