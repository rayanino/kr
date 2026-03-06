#!/usr/bin/env bash
# Pre-commit quality gate for KR
# Runs before git commit to catch common issues
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
cd "$PROJECT_DIR"

ISSUES=0
MSG=""

add_issue() {
    ISSUES=$((ISSUES + 1))
    MSG="${MSG}\n⚠ $1"
}

# Check 1: No API keys or tokens in staged files
if git diff --cached --diff-filter=ACM | grep -qiE '(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{48}|api[_-]?key\s*[:=])'; then
    add_issue "SECURITY: Possible API key or token in staged changes. Review before committing."
fi

# Check 2: No TODO without SPEC reference in new Python code
TODOS_WITHOUT_SPEC=$(git diff --cached --diff-filter=ACM -- '*.py' | grep -c '^\+.*#.*TODO' | grep -v '§' || echo 0)
if [ "$TODOS_WITHOUT_SPEC" -gt 0 ]; then
    add_issue "QUALITY: $TODOS_WITHOUT_SPEC TODO comments without SPEC section reference (§). Link TODOs to SPEC sections."
fi

# Check 3: Source files modified — remind about tests and CLAUDE.md
SRC_CHANGED=$(git diff --cached --name-only | grep -c 'engines/.*/src/\|shared/.*/src/' || echo 0)
if [ "$SRC_CHANGED" -gt 0 ]; then
    MSG="${MSG}\nREMINDER: $SRC_CHANGED source file(s) staged. Verify: tests pass, CLAUDE.md updated, SPEC.md consistent."
fi

# Check 4: SPEC modified — remind about consistency check
SPEC_CHANGED=$(git diff --cached --name-only | grep -c 'SPEC.md' || echo 0)
if [ "$SPEC_CHANGED" -gt 0 ]; then
    MSG="${MSG}\nREMINDER: SPEC.md modified. Run /check-spec to verify consistency."
fi

# Check 5: Schema modified — remind about boundary check
SCHEMA_CHANGED=$(git diff --cached --name-only | grep -c 'schemas/' || echo 0)
if [ "$SCHEMA_CHANGED" -gt 0 ]; then
    MSG="${MSG}\nREMINDER: Schema modified. Run python3 scripts/verify_metadata_flow.py to check boundaries."
fi

# Output
if [ -n "$MSG" ]; then
    echo -e "$MSG"
fi

# Don't block commits (exit 0) — these are reminders, not gates
# Block would be exit 2, which stops the tool
exit 0
