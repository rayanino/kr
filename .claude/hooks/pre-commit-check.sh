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

# 0. BLOCKING: Frozen source integrity (Principle 18 — frozen sources are immutable)
FROZEN_FILES=$(git diff --cached --name-only | grep -E 'library/sources/[^/]+/(frozen/|source\.)' 2>/dev/null)
if [ -n "$FROZEN_FILES" ]; then
    echo "BLOCKED: Attempting to modify frozen/immutable source files (Principle 18):"
    echo "$FROZEN_FILES"
    echo ""
    echo "Frozen sources are NEVER modified after extraction. If the source is wrong,"
    echo "re-extract and create a new version — do not edit in place."
    BLOCK=1
fi

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

# 4. ADVISORY: Regex \d in engine source (matches Arabic-Indic digits)
if [ -n "$MODIFIED_PY" ]; then
    for pyfile in $MODIFIED_PY; do
        # Look for \d in regex patterns (r-strings containing \d)
        UNSAFE_D=$(grep -nE "r['\"].*\\\\d" "$pyfile" 2>/dev/null | grep -v '# safe:' | grep -v '\[0-9\]')
        if [ -n "$UNSAFE_D" ]; then
            echo "  WARNING: $pyfile uses \\d in regex — Python \\d matches Arabic-Indic digits (٠-٩)."
            echo "           Use [0-9] for ASCII-only. Add '# safe:' comment if intentional."
            echo "$UNSAFE_D" | head -5
        fi
    done
fi

# 5. Advisory: SPEC quality check
MODIFIED_SPECS=$(git diff --cached --name-only | grep "SPEC.md$")
if [ -n "$MODIFIED_SPECS" ]; then
    for spec in $MODIFIED_SPECS; do
        echo ""
        echo "--- SPEC modified: $spec ---"
        python3 scripts/check_spec_quality.py "$spec" 2>/dev/null | head -8
    done
fi

# 6. Advisory: SPEC value validation (I-4)
if [ -n "$MODIFIED_SRC" ]; then
    CHECKED_ENGINE=""
    for src_file in $MODIFIED_SRC; do
        ENGINE_DIR=$(echo "$src_file" | grep -oE 'engines/[^/]+')
        if [ -n "$ENGINE_DIR" ] && [ -z "$CHECKED_ENGINE" ] && [ -f "$ENGINE_DIR/SPEC.md" ]; then
            echo ""
            echo "--- SPEC value validation: $ENGINE_DIR ---"
            python3 scripts/validate_spec_values.py "$ENGINE_DIR" 2>/dev/null | head -15
            CHECKED_ENGINE="$ENGINE_DIR"
        fi
    done
fi

# 7. Advisory: print() detection in engine source files
if [ -n "$MODIFIED_PY" ]; then
    for pyfile in $MODIFIED_PY; do
        # Find bare print() calls, excluding test files and # safe: comments
        PRINTS=$(grep -nE '^\s*print\s*\(' "$pyfile" 2>/dev/null | grep -v '# safe:' | grep -v 'def.*print')
        if [ -n "$PRINTS" ]; then
            echo "  WARNING: $pyfile has print() statements — use logging.getLogger(__name__) instead"
            echo "$PRINTS" | head -3
        fi
    done
fi

# 8. BLOCKING: Secret/API key detection in staged files
STAGED_PY=$(git diff --cached --name-only | grep '\.py$')
if [ -n "$STAGED_PY" ]; then
    for pyfile in $STAGED_PY; do
        SECRETS=$(grep -nE '(sk-ant-|sk-or-|sk-[a-zA-Z0-9]{20,}|ANTHROPIC_API_KEY\s*=\s*["\x27]|OPENROUTER.*KEY\s*=\s*["\x27])' "$pyfile" 2>/dev/null | grep -v '# safe:' | grep -v '\.example' | grep -v '\.template')
        if [ -n "$SECRETS" ]; then
            echo "BLOCKED: Possible API key/secret in $pyfile"
            echo "$SECRETS" | head -3
            BLOCK=1
        fi
    done
fi

# 9. Advisory: Long function detection (>50 lines) in modified src/ files
if [ -n "$MODIFIED_PY" ]; then
    for pyfile in $MODIFIED_PY; do
        LONG_FUNCS=$(python3 -c "
import ast, sys
try:
    with open(sys.argv[1]) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = node.end_lineno - node.lineno + 1
            if length > 50:
                print(f'  {sys.argv[1]}:{node.lineno}: {node.name}() is {length} lines (>50)')
except Exception:
    pass
" "$pyfile" 2>/dev/null)
        if [ -n "$LONG_FUNCS" ]; then
            echo "  WARNING: Long functions detected (consider splitting):"
            echo "$LONG_FUNCS"
        fi
    done
fi

# 10. Advisory: TODO/FIXME/HACK count in modified files
if [ -n "$MODIFIED_PY" ]; then
    TODO_COUNT=0
    for pyfile in $MODIFIED_PY; do
        COUNT=$(grep -cE '\b(TODO|FIXME|HACK|XXX)\b' "$pyfile" 2>/dev/null || echo 0)
        TODO_COUNT=$((TODO_COUNT + COUNT))
    done
    if [ $TODO_COUNT -gt 0 ]; then
        echo "  INFO: $TODO_COUNT TODO/FIXME/HACK markers in modified files"
    fi
fi

echo "=== End Pre-Commit ==="

if [ $BLOCK -ne 0 ]; then
    echo ""
    echo "COMMIT BLOCKED — fix the issues above before committing."
    exit 1
fi
