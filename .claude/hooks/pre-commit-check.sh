#!/bin/bash
# Pre-commit quality gate for KR
# Runs automatically before every git commit via .claude/settings.json

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || cd "$(git rev-parse --show-toplevel)"

echo "=== KR Pre-Commit Checks ==="

# 1. Session quality gate
python3 scripts/session_quality_gate.py 2>/dev/null

# 2. If a SPEC was modified, run quality checker
MODIFIED_SPECS=$(git diff --cached --name-only | grep "SPEC.md$")
if [ -n "$MODIFIED_SPECS" ]; then
    for spec in $MODIFIED_SPECS; do
        echo ""
        echo "--- SPEC modified: $spec ---"
        python3 scripts/check_spec_quality.py "$spec" 2>/dev/null | head -8
        echo ""
        python3 scripts/creative_verification.py "$spec" 2>/dev/null | tail -10
    done
fi

# 3. Check for Arabic text handling issues in modified Python files
MODIFIED_PY=$(git diff --cached --name-only | grep "\.py$" | grep "src/")
if [ -n "$MODIFIED_PY" ]; then
    echo ""
    echo "--- Arabic text safety check ---"
    for pyfile in $MODIFIED_PY; do
        # Check for common Arabic text mistakes
        if grep -n "\.lower()\|\.upper()\|\.strip()\|replace.*['\"]" "$pyfile" 2>/dev/null | grep -v "^#" | head -3; then
            echo "  ⚠ $pyfile: String operations on potentially Arabic text. Check .claude/skills/arabic-text/SKILL.md"
        fi
    done
fi

echo "=== End Pre-Commit ==="
