#!/usr/bin/env bash
# Circuit Breaker Hook for KR Overnight Sessions
# Tracks consecutive failures and blocks after 3+ on same operation type.
# Prevents infinite retry loops during autonomous work.
#
# Wiring (add to settings.json PreToolUse → Bash matcher):
#   See .claude/HOOK_WIRING.md for exact JSON.
#
# Usage: Reads stdin (tool input JSON), checks failure count, decides block/allow.

set -euo pipefail

FAILURE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/.circuit_breaker_state"
MAX_FAILURES=3

mkdir -p "$FAILURE_DIR"

# Read tool input from stdin
input=$(cat)

# Extract command from tool input
CMD=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [ -z "$CMD" ]; then
    exit 0  # No command to check
fi

# Create a hash of the command pattern (first 2 words) for grouping
CMD_PATTERN=$(echo "$CMD" | awk '{print $1, $2}' | md5sum | cut -d' ' -f1)
COUNTER_FILE="$FAILURE_DIR/$CMD_PATTERN"

# Check current failure count
if [ -f "$COUNTER_FILE" ]; then
    COUNT=$(cat "$COUNTER_FILE")
    if [ "$COUNT" -ge "$MAX_FAILURES" ]; then
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] CIRCUIT BREAKER: Blocked after $COUNT failures on pattern: $(echo "$CMD" | head -c 80)" >> "$CLAUDE_PROJECT_DIR/.claude/circuit_breaker.log" 2>/dev/null || true
        echo "{\"decision\":\"block\",\"reason\":\"Circuit breaker: $COUNT consecutive failures on this operation type. Move to next task. Reset with: rm $COUNTER_FILE\"}"
        exit 0
    fi
fi

# Allow the command (failure tracking happens via a separate post-tool hook)
exit 0
