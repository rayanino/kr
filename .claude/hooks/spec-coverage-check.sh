#!/bin/bash
# PostToolUse hook: Track SPEC rule coverage in test files
# Warns when a test file edit reduces SPEC rule references (§4.X citations)
# This catches accidental deletion of SPEC-tracing docstrings

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi

# Only check test files in engines/shared
if ! echo "$FILE" | grep -qE '(engines|shared)/[^/]+/tests/.*\.py$'; then
    exit 0
fi

# Count SPEC references in current version
CURRENT_REFS=$(grep -cE '§[0-9]+\.' "$FILE" 2>/dev/null || echo 0)

# Count SPEC references in git version
GIT_REFS=$(git show "HEAD:$FILE" 2>/dev/null | grep -cE '§[0-9]+\.' 2>/dev/null || echo 0)

# If no git version, this is a new file — just report current coverage
if [ "$GIT_REFS" = "0" ] && [ "$CURRENT_REFS" -gt "0" ]; then
    echo "SPEC coverage: $CURRENT_REFS rule references in new test file" >&2
    exit 0
fi

# Warn if SPEC references decreased
if [ "$CURRENT_REFS" -lt "$GIT_REFS" ]; then
    LOST=$((GIT_REFS - CURRENT_REFS))
    echo "WARNING: SPEC rule references DECREASED in $FILE" >&2
    echo "  Before: $GIT_REFS references | After: $CURRENT_REFS | Lost: $LOST" >&2
    echo "  Verify test docstrings still cite their §4.X SPEC rules." >&2
fi

exit 0
