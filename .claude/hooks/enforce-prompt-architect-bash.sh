#!/usr/bin/env bash
# DR19 Norm 2 Extension: Prompt-Architect Enforcement for Bash CLI Dispatches
# Blocks codex exec and gemini -p commands unless /prompt-architect was recently invoked.
# Also auto-logs dispatch to dispatch_log.jsonl (R2).
#
# Matcher: PreToolUse → Bash
# Exit 0 = allow (not a coworker dispatch, or prompt-architect evidence found)
# JSON block decision = block (coworker dispatch without optimization)
#
# Reference: Protocol HR-23, HR-28, CLAUDE.md Rule 14

set -euo pipefail

STATE_FILE="$CLAUDE_PROJECT_DIR/.kr/runtime/prompt_architect_state.json"
DISPATCH_LOG="$CLAUDE_PROJECT_DIR/.kr/runtime/dispatch_log.jsonl"

# Read tool input from stdin
input=$(cat)

# Extract the command from Bash tool input
CMD=$(echo "$input" | jq -r '.tool_input.command // ""' 2>/dev/null)

if [ -z "$CMD" ]; then
    exit 0
fi

# Check if this is a coworker CLI dispatch
TARGET=""
if echo "$CMD" | grep -qE 'codex\s+exec'; then
    TARGET="codex"
elif echo "$CMD" | grep -qE 'gemini\s+(-p|--prompt)'; then
    TARGET="gemini"
fi

# Not a coworker dispatch — allow through
if [ -z "$TARGET" ]; then
    exit 0
fi

# This IS a coworker dispatch. Check prompt-architect state.
if [ ! -f "$STATE_FILE" ]; then
    echo "{\"decision\":\"block\",\"reason\":\"HR-23 violation: $TARGET CLI dispatch blocked. No /prompt-architect invocation recorded this session. Run /prompt-architect to optimize your dispatch prompt first. State file not found.\"}"
    exit 0
fi

# Check recency (within 30 minutes)
LAST_INVOCATION=$(jq -r '.last_invocation_epoch // 0' "$STATE_FILE" 2>/dev/null)
NOW=$(date +%s)
AGE=$(( NOW - LAST_INVOCATION ))

if [ "$AGE" -gt 1800 ]; then
    echo "{\"decision\":\"block\",\"reason\":\"HR-23 violation: $TARGET CLI dispatch blocked. Last /prompt-architect invocation was ${AGE}s ago (>1800s). Run /prompt-architect again before dispatching to $TARGET.\"}"
    exit 0
fi

# Prompt-architect evidence found. Auto-log the dispatch (R2).
mkdir -p "$(dirname "$DISPATCH_LOG")"
NOW_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')
CMD_HASH=$(echo "$CMD" | sha256sum 2>/dev/null | cut -d' ' -f1 || echo "unknown")
PA_USED="true"

echo "{\"timestamp\":\"$NOW_ISO\",\"target_agent\":\"$TARGET\",\"command_hash\":\"$CMD_HASH\",\"prompt_architect_used\":$PA_USED,\"source\":\"bash_hook_auto\"}" >> "$DISPATCH_LOG" 2>/dev/null || true

# Allow the dispatch
exit 0
