#!/bin/bash
# PostToolUse hook: Run ruff check --fix then black on modified Python files
# Replaces inline black-only formatting
FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
if echo "$FILE" | grep -qE '\.py$'; then
  # Ruff: fix unused imports, sort imports, upgrade syntax, catch bugbear issues
  ruff check --fix --quiet "$FILE" 2>/dev/null || true
  # Black: format code style
  black "$FILE" 2>/dev/null || true
fi
exit 0
