#!/bin/bash
# Async test runner — fires after Write/Edit on Python files
# Identifies which engine was modified and runs its tests in background
# Does NOT block the editing loop

FILE="$CLAUDE_TOOL_FILE_PATH"
PROJECT="$CLAUDE_PROJECT_DIR"

# Only run for Python files in engine src directories
if ! echo "$FILE" | grep -qE '\.py$'; then exit 0; fi
if ! echo "$FILE" | grep -q 'engines/'; then exit 0; fi

# Extract engine name from path (e.g., engines/source/src/foo.py → source)
ENGINE=$(echo "$FILE" | sed -n 's|.*/engines/\([^/]*\)/.*|\1|p')
if [ -z "$ENGINE" ]; then exit 0; fi

TEST_DIR="$PROJECT/engines/$ENGINE/tests"
if [ ! -d "$TEST_DIR" ]; then exit 0; fi

# Run tests in background, capture result
(
  cd "$PROJECT"
  RESULT=$(python -m pytest "$TEST_DIR" -q --tb=line 2>&1 | tail -5)
  if echo "$RESULT" | grep -q "failed"; then
    echo "⚠️ [$ENGINE] tests have failures:" >&2
    echo "$RESULT" >&2
  fi
) &>/dev/null &

exit 0
