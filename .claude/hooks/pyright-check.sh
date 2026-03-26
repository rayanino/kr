#!/bin/bash
# PostToolUse hook: Run pyright on modified Python files
# I-1: Pydantic Field(None) pre-flight check before pyright
# I-3: Full output (no tail truncation)
# 7A: RAPID_MODE skip + scope filter (only engine/shared/scripts)
if [ -n "$CLAUDE_RAPID_MODE" ]; then exit 0; fi
FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
# Only check engine/shared/scripts source files — skip experiments/ and other dirs
if ! echo "$FILE" | grep -qE '(engines|shared)/[^/]+/(src|tests)/.*\.py$|scripts/.*\.py$'; then
  exit 0
fi
if echo "$FILE" | grep -qE '\.py$'; then
  # Pre-flight: check for missing explicit None on Pydantic Field(None) fields
  python3 "$CLAUDE_PROJECT_DIR/scripts/check_pydantic_fields.py" "$FILE" --project-dir "$CLAUDE_PROJECT_DIR" 2>&1

  # Pre-flight: check for `from __future__ import annotations` in engine/shared source
  if echo "$FILE" | grep -qE '(engines|shared)/.*\.py$'; then
    if ! grep -q 'from __future__ import annotations' "$FILE" 2>/dev/null; then
      echo "WARNING: $FILE is missing 'from __future__ import annotations' — required by python-code.md rules." >&2
    fi
  fi

  # Run pyright with full output
  cd "$CLAUDE_PROJECT_DIR" && python -m pyright "$FILE" 2>&1
fi
