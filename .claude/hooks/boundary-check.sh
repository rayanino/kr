#!/bin/bash
# PostToolUse hook: Validate metadata flow after contracts.py changes
FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
if echo "$FILE" | grep -qE 'contracts\.py$'; then
  cd "$CLAUDE_PROJECT_DIR" && python3 scripts/verify_metadata_flow.py 2>&1 | tail -15
fi
