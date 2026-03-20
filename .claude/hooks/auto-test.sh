#!/bin/bash
# PostToolUse hook: Run pytest on affected engine/shared module after src changes
# I-3: Full output (no tail truncation) + CLAUDE_RAPID_MODE skip
# Set CLAUDE_RAPID_MODE=1 to skip auto-tests during rapid iteration
if [ -n "$CLAUDE_RAPID_MODE" ]; then exit 0; fi
FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
if echo "$FILE" | grep -qE '(engines|shared)/[^/]+/(src|tests)/.*\.py$'; then
  MODULE=$(echo "$FILE" | grep -oE '(engines|shared)/[^/]+')
  TEST_DIR="$CLAUDE_PROJECT_DIR/$MODULE/tests"
  if [ -d "$TEST_DIR" ]; then
    cd "$CLAUDE_PROJECT_DIR" && python -m pytest "$MODULE/tests/" -x -q --tb=short 2>&1
  fi
fi
