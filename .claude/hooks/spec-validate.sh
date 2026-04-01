#!/usr/bin/env bash
# PostToolUse hook: auto-validates SPEC.md files after edit.
# Runs check_spec_quality.py on any modified SPEC.md file.
# Advisory only — does not block edits.

set -euo pipefail

FILE="$CLAUDE_TOOL_FILE_PATH"

# Only trigger for SPEC.md files
if [ -z "$FILE" ]; then exit 0; fi
if ! echo "$FILE" | grep -q 'SPEC.md'; then exit 0; fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Run SPEC quality check if the script exists
if [ -f "scripts/check_spec_quality.py" ]; then
    echo "=== SPEC VALIDATION ==="
    python3 scripts/check_spec_quality.py "$FILE" 2>&1 || true
    echo "=== END SPEC VALIDATION ==="
fi

exit 0
