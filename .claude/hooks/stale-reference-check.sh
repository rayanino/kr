#!/usr/bin/env bash
# F5 enforcement: Pre-commit check for stale file references in .claude/ files.
# Runs check_stale_references.py when .claude/ files are staged for commit.
# Advisory only — warns but does not block.

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Only run if .claude/ files are staged
CLAUDE_FILES=$(git diff --cached --name-only 2>/dev/null | grep '^\.claude/' || true)
if [ -z "$CLAUDE_FILES" ]; then
    exit 0
fi

if [ -f "scripts/enforcement/check_stale_references.py" ]; then
    echo ""
    echo "--- Stale reference check (.claude/ files modified) ---"
    python3 scripts/enforcement/check_stale_references.py 2>&1 | tail -20
fi

exit 0
