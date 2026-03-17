#!/bin/bash
# PostToolUse hook: Run pyright on modified Python files
FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
if echo "$FILE" | grep -qE '\.py$'; then
  cd "$CLAUDE_PROJECT_DIR" && python -m pyright "$FILE" 2>&1 | tail -20
fi
