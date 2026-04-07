#!/bin/bash
# PostToolUse hook: Consolidated code quality checks for Python files.
# Merges: ruff-format.sh + pyright-check.sh + auto-test.sh
# Phases run in order; each phase has its own scope filter.
# Set CLAUDE_RAPID_MODE=1 to skip pyright and auto-test (keeps ruff/black).

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
if ! echo "$FILE" | grep -qE '\.py$'; then exit 0; fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# ── Phase 1: Ruff + Black (all .py files, always runs) ──────────────
ruff check --fix --quiet "$FILE" 2>/dev/null || true
black "$FILE" 2>/dev/null || true

# Scope gate: remaining phases only for engine/shared/scripts source
if ! echo "$FILE" | grep -qE '(engines|shared)/[^/]+/(src|tests)/.*\.py$|scripts/.*\.py$'; then
    exit 0
fi

# ── Phase 2: Pydantic + future annotations checks ───────────────────
# Pre-flight: check for missing explicit None on Pydantic Field(None) fields
python3 "$CLAUDE_PROJECT_DIR/scripts/check_pydantic_fields.py" "$FILE" --project-dir "$CLAUDE_PROJECT_DIR" 2>&1

# Pre-flight: check for `from __future__ import annotations` in engine/shared source
if echo "$FILE" | grep -qE '(engines|shared)/.*\.py$'; then
    if ! grep -q 'from __future__ import annotations' "$FILE" 2>/dev/null; then
        echo "WARNING: $FILE is missing 'from __future__ import annotations' — required by python-code.md rules." >&2
    fi
fi

# ── Phase 3: Pyright (skip in rapid mode) ────────────────────────────
if [ -z "${CLAUDE_RAPID_MODE:-}" ]; then
    python -m pyright "$FILE" 2>&1
fi

# ── Phase 4: Auto-test (skip in rapid mode) ──────────────────────────
if [ -z "${CLAUDE_RAPID_MODE:-}" ]; then
    if echo "$FILE" | grep -qE '(engines|shared)/[^/]+/(src|tests)/.*\.py$'; then
        MODULE=$(echo "$FILE" | grep -oE '(engines|shared)/[^/]+')
        TEST_DIR="$CLAUDE_PROJECT_DIR/$MODULE/tests"
        if [ -d "$TEST_DIR" ]; then
            python -m pytest "$MODULE/tests/" -x -q --tb=short 2>&1
        fi
    fi
fi
