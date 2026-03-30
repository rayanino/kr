#!/usr/bin/env bash
# Stop hook: quality gate before Claude finishes a turn.
# Checks that modified Python files pass pyright and tests still pass.
# Uses stop_hook_active to prevent infinite continuation loops.
#
# Exit codes:
#   0 + no JSON = allow stop (pass)
#   0 + {"decision":"block","reason":"..."} = force continuation
#   any other = non-blocking error (logged only)

set -uo pipefail
# NOTE: intentionally NOT using set -e here. If a sub-check exits non-zero,
# we must still reach the block-decision output at the end. set -e would
# terminate the script before outputting the block JSON, making the error
# non-blocking (the hook "fails open"). This was caught by Codex audit.

INPUT=$(cat)

# CRITICAL: check stop_hook_active to prevent infinite loops.
# If Claude is already in forced continuation from a previous block,
# let it stop to avoid an endless cycle.
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [ "$STOP_ACTIVE" = "true" ]; then
    exit 0
fi

# Skip in rapid mode or overnight mode (autonomous decisions)
if [ "${CLAUDE_RAPID_MODE:-}" = "1" ] || [ "${KR_OVERNIGHT:-}" = "1" ]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Find Python files modified in this session (staged + unstaged changes)
MODIFIED_PY=$(git diff --name-only HEAD 2>/dev/null | grep -E '\.py$' || true)
STAGED_PY=$(git diff --cached --name-only 2>/dev/null | grep -E '\.py$' || true)
ALL_PY=$(echo -e "$MODIFIED_PY\n$STAGED_PY" | sort -u | grep -v '^$' || true)

# If no Python files were modified, nothing to check
if [ -z "$ALL_PY" ]; then
    exit 0
fi

# Only check engine/shared source files (not scripts, tests, etc.)
ENGINE_PY=$(echo "$ALL_PY" | grep -E '^(engines|shared)/.*\.py$' || true)
if [ -z "$ENGINE_PY" ]; then
    exit 0
fi

ERRORS=""

# Check 1: pyright type errors on modified engine files
for f in $ENGINE_PY; do
    if [ -f "$f" ]; then
        PYRIGHT_OUT=$(python -m pyright "$f" 2>&1 || true)
        ERROR_COUNT=$(echo "$PYRIGHT_OUT" | grep -c ' error:' || true)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            ERRORS="${ERRORS}pyright: $ERROR_COUNT type error(s) in $f\n"
        fi
    fi
done

# Check 2: identify affected engines and run their tests
# Use sed instead of grep -oP (Perl regex not reliable on Windows Git Bash)
ENGINES_HIT=$(echo "$ENGINE_PY" | sed -n 's|^engines/\([^/]*\)/.*|\1|p' | sort -u || true)
for eng in $ENGINES_HIT; do
    TEST_DIR="engines/$eng/tests"
    if [ -d "$TEST_DIR" ]; then
        TEST_OUT=$(python -m pytest "$TEST_DIR" -x -q --tb=line 2>&1 || true)
        if echo "$TEST_OUT" | grep -qE '(FAILED|ERROR)'; then
            FAIL_COUNT=$(echo "$TEST_OUT" | grep -cE '(FAILED|ERROR)' || echo "?")
            ERRORS="${ERRORS}pytest: $FAIL_COUNT failure(s) in $eng tests\n"
        fi
    fi
done

# Check 3: Arabic safety re-scan on all modified engine files
for f in $ENGINE_PY; do
    if [ -f "$f" ]; then
        CLAUDE_TOOL_FILE_PATH="$f" bash "$CLAUDE_PROJECT_DIR/.claude/hooks/arabic-safety-check.sh" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            ERRORS="${ERRORS}arabic-safety: BLOCKING violation in $f\n"
        fi
    fi
done

# Check 4: D-023 metadata flow (if contracts.py was modified)
# The script exits 0 on pre-existing SPEC gaps (warnings) and non-zero on
# real violations.  Previous grep for "missing" false-triggered on the
# informational "DOWNSTREAM EXPECTS BUT UPSTREAM DOESN'T PRODUCE" lines
# which are expected while engines are under construction.
CONTRACTS_HIT=$(echo "$ALL_PY" | grep 'contracts.py' || true)
if [ -n "$CONTRACTS_HIT" ]; then
    if [ -f "scripts/verify_metadata_flow.py" ]; then
        if ! python3 scripts/verify_metadata_flow.py > /dev/null 2>&1; then
            ERRORS="${ERRORS}D-023: metadata flow script failed — run scripts/verify_metadata_flow.py\n"
        fi
    fi
fi

# Check 5: Frozen source integrity (Principle 18 — immutable after freezing)
FROZEN_CHANGES=$(git diff --name-only HEAD 2>/dev/null | grep 'library/sources/.*/frozen/' || true)
if [ -n "$FROZEN_CHANGES" ]; then
    ERRORS="${ERRORS}FROZEN SOURCE MODIFIED (Principle 18 violation): ${FROZEN_CHANGES}\n"
fi

# If errors found, block stop and tell Claude to fix them
if [ -n "$ERRORS" ]; then
    REASON=$(echo -e "Quality gate FAILED. Fix before completing:\n$ERRORS")
    echo "{\"decision\":\"block\",\"reason\":$(echo "$REASON" | jq -Rs .)}"
    exit 0
fi

# All checks passed — allow stop
exit 0
