#!/bin/bash
# Pre-commit quality gate for KR
# Runs automatically before every git commit via .claude/settings.json
#
# BLOCKING checks (exit 1 = abort commit):
#   - Tests fail for any modified engine
#   - Arabic .lower()/.upper() in src files with Arabic content
# ADVISORY checks (warnings only):
#   - Session quality gate
#   - SPEC quality
#   - Arabic .strip()/.replace() warnings

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || cd "$(git rev-parse --show-toplevel)"
BLOCK=0

echo "=== KR Pre-Commit Checks ==="

# 1. Session quality gate (advisory)
python3 scripts/session_quality_gate.py 2>/dev/null

# 2. BLOCKING: Run tests for every modified engine/shared module
MODIFIED_SRC=$(git diff --cached --name-only | grep -E '(engines|shared)/[^/]+/.*\.py$')
if [ -n "$MODIFIED_SRC" ]; then
    TESTED_MODULES=""
    for src_file in $MODIFIED_SRC; do
        MODULE=$(echo "$src_file" | grep -oE '(engines|shared)/[^/]+')
        # Skip if already tested this module
        if echo "$TESTED_MODULES" | grep -q "$MODULE"; then continue; fi
        TESTED_MODULES="$TESTED_MODULES $MODULE"
        TEST_DIR="$MODULE/tests"
        if [ -d "$TEST_DIR" ]; then
            echo ""
            echo "--- Running tests: $TEST_DIR ---"
            python -m pytest "$TEST_DIR" -x -q --tb=short 2>&1
            if [ $? -ne 0 ]; then
                echo "BLOCKED: Tests failed in $TEST_DIR. Fix before committing."
                BLOCK=1
            fi
        fi
    done
fi

# 3. BLOCKING: Arabic .lower()/.upper() in src files with Arabic content
MODIFIED_PY=$(git diff --cached --name-only | grep "\.py$" | grep "src/")
if [ -n "$MODIFIED_PY" ]; then
    echo ""
    echo "--- Arabic text safety check ---"
    for pyfile in $MODIFIED_PY; do
        LOWER_UPPER=$(grep -nE '\.(lower|upper)\(\)' "$pyfile" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:')
        if [ -n "$LOWER_UPPER" ]; then
            HAS_ARABIC=$(python3 -c "import sys; sys.exit(0 if any('\u0600'<=c<='\u06FF' for line in open(sys.argv[1],encoding='utf-8',errors='ignore') for c in line) else 1)" "$pyfile" 2>/dev/null && echo "yes" || echo "no")
            if [ "$HAS_ARABIC" = "yes" ]; then
                echo "BLOCKED: .lower()/.upper() in $pyfile which contains Arabic text."
                echo "$LOWER_UPPER"
                BLOCK=1
            fi
        fi
        # Advisory: .strip()/.replace() warnings
        if grep -n "\.strip()\|\.replace(" "$pyfile" 2>/dev/null | grep -v "^#" | grep -v '# safe:' | head -3 | grep -q .; then
            echo "  WARNING: $pyfile has .strip()/.replace() — verify Arabic text safety"
        fi
    done
fi

# 4. Advisory: SPEC quality check
MODIFIED_SPECS=$(git diff --cached --name-only | grep "SPEC.md$")
if [ -n "$MODIFIED_SPECS" ]; then
    for spec in $MODIFIED_SPECS; do
        echo ""
        echo "--- SPEC modified: $spec ---"
        python3 scripts/check_spec_quality.py "$spec" 2>/dev/null | head -8
    done
fi

echo "=== End Pre-Commit ==="

if [ $BLOCK -ne 0 ]; then
    echo ""
    echo "COMMIT BLOCKED — fix the issues above before committing."
    exit 1
fi
