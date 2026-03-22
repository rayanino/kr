#!/usr/bin/env bash
# No-Ask-Human Hook for KR Overnight Sessions
# Blocks AskUserQuestion tool when KR_OVERNIGHT=1.
# Forces autonomous decisions logged to pending_decisions.log.
#
# Wiring (add to settings.json PreToolUse → AskUserQuestion matcher):
#   See .claude/HOOK_WIRING.md for exact JSON.
#
# Activation: Set KR_OVERNIGHT=1 in environment before starting session.
# Deactivation: Unset KR_OVERNIGHT or set to 0.

set -euo pipefail

# Only active when overnight mode is on
if [ "${KR_OVERNIGHT:-0}" != "1" ]; then
    exit 0
fi

# Read tool input from stdin
input=$(cat)

# Extract the question being asked
QUESTION=$(echo "$input" | jq -r '.tool_input.question // .tool_input.questions[0].question // "unknown question"' 2>/dev/null)

# Log the blocked question
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] BLOCKED QUESTION (overnight mode): $QUESTION" >> "$CLAUDE_PROJECT_DIR/.claude/pending_decisions.log" 2>/dev/null || true

# Block with explanation
echo "{\"decision\":\"block\",\"reason\":\"Overnight mode active (KR_OVERNIGHT=1). Cannot ask questions. Make an independent decision and log to .claude/pending_decisions.log.\"}"
