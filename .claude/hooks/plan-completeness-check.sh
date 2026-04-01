#!/usr/bin/env bash
# F4 enforcement: PostToolUse hook that validates NEXT.md completeness after edits.
# Advisory only — warns about gaps but does not block.

FILE="$CLAUDE_TOOL_FILE_PATH"

# Only trigger for NEXT.md
if [ -z "$FILE" ]; then exit 0; fi
if ! echo "$FILE" | grep -q 'NEXT\.md'; then exit 0; fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

if [ -f "scripts/enforcement/validate_plan_completeness.py" ]; then
    echo "=== PLAN COMPLETENESS CHECK ==="
    python3 scripts/enforcement/validate_plan_completeness.py "$FILE" 2>&1 || true
    echo "=== END PLAN CHECK ==="
fi

exit 0
