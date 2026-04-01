#!/usr/bin/env bash
# F2 enforcement: Stop hook that detects passive leadership patterns.
#
# Cannot inspect response text directly (Stop hooks only see external state).
# Instead, checks for the SYMPTOM: CC stopped without updating NEXT.md
# with next-step proposals after modifying engine/shared code.
#
# The UserPromptSubmit hook (prompt-context.sh) handles the REMINDER side.
# This hook handles the ENFORCEMENT side.
#
# Exit:
#   0 + no JSON = allow stop
#   0 + {"decision":"block","reason":"..."} = force continuation

set -uo pipefail

INPUT=$(cat)

# CRITICAL: prevent infinite loop
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [ "$STOP_ACTIVE" = "true" ]; then
    exit 0
fi

# Skip in overnight/rapid mode
if [ "${KR_OVERNIGHT:-}" = "1" ] || [ "${CLAUDE_RAPID_MODE:-}" = "1" ]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Check if substantial work was done (engine/shared code modified)
SUBSTANTIAL_WORK=$(git diff --name-only HEAD 2>/dev/null | grep -E '^(engines|shared)/.*\.(py|md)$' | head -1 || true)

if [ -z "$SUBSTANTIAL_WORK" ]; then
    exit 0  # No substantial work — no enforcement needed
fi

# Check if NEXT.md was also modified (indicates CC updated the plan)
NEXT_MODIFIED=$(git diff --name-only HEAD 2>/dev/null | grep -E '^NEXT\.md$' || true)

if [ -n "$NEXT_MODIFIED" ]; then
    exit 0  # NEXT.md was updated — CC is being proactive
fi

# Substantial work was done but NEXT.md wasn't updated
# This is a signal of passive behavior (did work, didn't plan next steps)
REASON="LEADERSHIP CHECK: You modified engine/shared files but didn't update NEXT.md with next steps. Per post-milestone-protocol: (1) summarize what was accomplished, (2) identify what's needed next, (3) propose next 2-3 steps. Update NEXT.md or explain why no update is needed."
echo "{\"decision\":\"block\",\"reason\":$(echo "$REASON" | jq -Rs .)}"
exit 0
