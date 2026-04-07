#!/bin/bash
# PostToolUse hook: Consolidated SPEC and planning document validation.
# Merges: spec-validate.sh + spec-coverage-check.sh + plan-completeness-check.sh
# Advisory only — warns about issues but never blocks.

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# ── Phase 1: SPEC validation (exact SPEC.md filename only) ──────────
if echo "$FILE" | grep -qE '(^|/)SPEC\.md$'; then
    if [ -f "scripts/check_spec_quality.py" ]; then
        echo "=== SPEC VALIDATION ==="
        python3 scripts/check_spec_quality.py "$FILE" 2>&1 || true
        echo "=== END SPEC VALIDATION ==="
    fi
fi

# ── Phase 2: SPEC coverage tracking (test files only) ───────────────
if echo "$FILE" | grep -qE '(engines|shared)/[^/]+/tests/.*\.py$'; then
    CURRENT_REFS=$(grep -cE '§[0-9]+\.' "$FILE" 2>/dev/null || true)
    CURRENT_REFS=${CURRENT_REFS:-0}
    GIT_REFS=$(git show "HEAD:$FILE" 2>/dev/null | grep -cE '§[0-9]+\.' || true)
    GIT_REFS=${GIT_REFS:-0}

    if [ "$GIT_REFS" = "0" ] && [ "$CURRENT_REFS" -gt "0" ] 2>/dev/null; then
        echo "SPEC coverage: $CURRENT_REFS rule references in new test file" >&2
    elif [ "$CURRENT_REFS" -lt "$GIT_REFS" ] 2>/dev/null; then
        LOST=$((GIT_REFS - CURRENT_REFS))
        echo "WARNING: SPEC rule references DECREASED in $FILE" >&2
        echo "  Before: $GIT_REFS | After: $CURRENT_REFS | Lost: $LOST" >&2
        echo "  Verify test docstrings still cite their SPEC rules." >&2
    fi
fi

# ── Phase 3: Plan completeness (exact NEXT.md at repo root only) ─────
if echo "$FILE" | grep -qE '(^|/)NEXT\.md$'; then
    if [ -f "scripts/enforcement/validate_plan_completeness.py" ]; then
        echo "=== PLAN COMPLETENESS CHECK ==="
        python3 scripts/enforcement/validate_plan_completeness.py "$FILE" 2>&1 || true
        echo "=== END PLAN CHECK ==="
    fi
fi

exit 0
