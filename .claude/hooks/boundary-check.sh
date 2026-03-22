#!/bin/bash
# PostToolUse hook: Validate metadata flow and contract boundaries
# Triggers on:
#   1. contracts.py changes → full metadata flow verification (D-023)
#   2. Any engines/*/src/*.py change → metadata flow check (D-023 expansion)
#   3. contracts.py changes → cross-engine contract validation
FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# D-023: Metadata flow verification on contracts.py OR any engine src/ change
if echo "$FILE" | grep -qE 'contracts\.py$'; then
  echo "--- D-023: Metadata flow verification (contracts.py changed) ---"
  python3 scripts/verify_metadata_flow.py 2>&1 | tail -15

  # Cross-engine contract validation
  if [ -f "tools/check_cross_engine_contracts.py" ]; then
    echo ""
    echo "--- Cross-engine contract validation ---"
    PYTHONIOENCODING=utf-8 python3 tools/check_cross_engine_contracts.py 2>&1 | tail -10
  fi
elif echo "$FILE" | grep -qE 'engines/[^/]+/src/.*\.py$'; then
  echo "--- D-023: Metadata flow advisory (engine src/ changed) ---"
  echo "Reminder: verify metadata pass-through (D-023) in changed functions."
  echo "Run: python3 scripts/verify_metadata_flow.py"
fi
