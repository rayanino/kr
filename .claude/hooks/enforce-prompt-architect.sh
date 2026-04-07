#!/usr/bin/env bash
# DR19 Norm 2: Prompt-Architect Enforcement Hook
# Blocks Agent dispatches and coworker Bash commands unless /prompt-architect
# was recently invoked (evidence in session state file).
#
# Matcher: PreToolUse → Agent
# Exit 0 = allow (prompt-architect evidence found)
# Exit code via JSON decision block = block (no evidence)
#
# Reference: Protocol HR-23, HR-25, CLAUDE.md Rule 14

set -euo pipefail

STATE_FILE="$CLAUDE_PROJECT_DIR/.kr/runtime/prompt_architect_state.json"

# Read tool input from stdin
input=$(cat)

# Extract tool name from the input
TOOL_NAME=$(echo "$input" | jq -r '.tool_name // ""' 2>/dev/null)

# Only enforce on Agent tool (subagent dispatches)
# Bash enforcement for codex/gemini is handled separately
if [ "$TOOL_NAME" != "Agent" ]; then
    exit 0
fi

# Check if state file exists
if [ ! -f "$STATE_FILE" ]; then
    echo "{\"decision\":\"block\",\"reason\":\"HR-23 BLOCKED: No /prompt-architect invocation this session. You MUST run /prompt-architect first, then retry the Agent dispatch. DO NOT bypass by doing the work yourself with Read/Grep/Bash — that defeats the purpose of multi-model prompt optimization. The agent dispatch exists for a reason; circumventing HR-23 by substituting direct tool calls is a rule violation.\"}"
    exit 0
fi

# Check if there's a recent invocation (within last 30 minutes)
LAST_INVOCATION=$(jq -r '.last_invocation_epoch // 0' "$STATE_FILE" 2>/dev/null)
NOW=$(date +%s)
AGE=$(( NOW - LAST_INVOCATION ))

if [ "$AGE" -gt 1800 ]; then
    echo "{\"decision\":\"block\",\"reason\":\"HR-23 BLOCKED: Last /prompt-architect was ${AGE}s ago (>1800s). Run /prompt-architect again, then retry this Agent dispatch. DO NOT bypass by doing the work yourself — circumventing HR-23 with direct tool calls is a rule violation. The prompt must be optimized before any dispatch.\"}"
    exit 0
fi

# Recent prompt-architect invocation found — allow dispatch
exit 0
