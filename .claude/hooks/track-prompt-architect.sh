#!/usr/bin/env bash
# DR19: Track prompt-architect invocations for enforcement hook.
# Records timestamp when /prompt-architect skill is used.
#
# Matcher: PostToolUse → Skill
# Writes to .kr/runtime/prompt_architect_state.json

set -euo pipefail

# Read tool input from stdin
input=$(cat)

# Check if the Skill tool was "prompt-architect" (accepts plugin-namespaced forms
# like "prompt-architect:prompt-architect" and any "<namespace>:prompt-architect").
SKILL_NAME=$(echo "$input" | jq -r '.tool_input.skill // ""' 2>/dev/null)

case "$SKILL_NAME" in
    prompt-architect|*:prompt-architect)
        ;;
    *)
        exit 0
        ;;
esac

# Record the invocation
STATE_DIR="$CLAUDE_PROJECT_DIR/.kr/runtime"
STATE_FILE="$STATE_DIR/prompt_architect_state.json"

mkdir -p "$STATE_DIR"

NOW_EPOCH=$(date +%s)
NOW_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')

# Read existing state or create new
if [ -f "$STATE_FILE" ]; then
    INVOCATION_COUNT=$(jq -r '.invocation_count // 0' "$STATE_FILE" 2>/dev/null)
else
    INVOCATION_COUNT=0
fi

NEW_COUNT=$((INVOCATION_COUNT + 1))

# Write updated state
cat > "$STATE_FILE" <<EOJSON
{
  "last_invocation_epoch": $NOW_EPOCH,
  "last_invocation_iso": "$NOW_ISO",
  "invocation_count": $NEW_COUNT,
  "session_id": "${CLAUDE_SESSION_ID:-unknown}"
}
EOJSON

exit 0
