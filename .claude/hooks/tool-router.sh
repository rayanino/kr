#!/bin/bash
# PostToolUse hook: Suggest relevant skills/commands/agents based on edited file.
# ACTIVATION hook (not enforcement) — outputs suggestions, never blocks.
# Fast: pure pattern matching, no external scripts, no python calls.

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi

SUGGESTIONS=""

# --- Engine source code ---
if echo "$FILE" | grep -qE 'engines/[^/]+/src/.*\.py$'; then
    ENGINE=$(echo "$FILE" | grep -oE 'engines/[^/]+' | cut -d/ -f2)
    SUGGESTIONS="Tools for $ENGINE src: /quality-gate $ENGINE | code-reviewer agent | arabic-text skill"

    # Engine-specific additions
    case "$ENGINE" in
        excerpting)
            SUGGESTIONS="$SUGGESTIONS | consensus-pattern skill | /excerpt-status"
            ;;
        normalization)
            SUGGESTIONS="$SUGGESTIONS | /verify-boundaries | arabic-text-quality skill"
            ;;
        passaging)
            SUGGESTIONS="$SUGGESTIONS | /verify-boundaries"
            ;;
        atomization)
            SUGGESTIONS="$SUGGESTIONS | /verify-boundaries"
            ;;
        taxonomy)
            SUGGESTIONS="$SUGGESTIONS | islamic-sciences-classification skill | domain-glossary skill"
            ;;
        synthesis)
            SUGGESTIONS="$SUGGESTIONS | scholarly-design skill"
            ;;
        source)
            SUGGESTIONS="$SUGGESTIONS | /verify-boundaries | technology-survey skill"
            ;;
    esac
fi

# --- Test files ---
if echo "$FILE" | grep -qE '(engines|shared)/[^/]+/tests/.*\.py$'; then
    SUGGESTIONS="Tools for tests: test-engineer agent | spec-examples skill | /regression-check"
fi

# --- SPEC files ---
if echo "$FILE" | grep -qE 'SPEC\.md$'; then
    SUGGESTIONS="Tools for SPEC: /check-spec | spec-writer agent | spec-adversary agent | spec-examples skill"
fi

# --- Contract files ---
if echo "$FILE" | grep -qE 'contracts\.py$'; then
    SUGGESTIONS="Tools for contracts: /verify-boundaries | boundary-validator agent"
fi

# --- Claude Code infrastructure ---
if echo "$FILE" | grep -qE '^\.(claude|codex)/'; then
    SUGGESTIONS="Tools for harness: /harness-audit"
fi

# --- Shared modules ---
if echo "$FILE" | grep -qE 'shared/[^/]+/src/.*\.py$'; then
    MODULE=$(echo "$FILE" | grep -oE 'shared/[^/]+' | cut -d/ -f2)
    SUGGESTIONS="Tools for shared/$MODULE: /quality-gate | code-reviewer agent | /verify-boundaries"
    case "$MODULE" in
        consensus)
            SUGGESTIONS="$SUGGESTIONS | consensus-pattern skill"
            ;;
        scholar_authority)
            SUGGESTIONS="$SUGGESTIONS | scholarly-attribution skill | domain-glossary skill"
            ;;
    esac
fi

# --- Integration tests ---
if echo "$FILE" | grep -qE '^integration_tests/.*\.py$'; then
    SUGGESTIONS="Tools for integration tests: /regression-check | test-engineer agent"
fi

# --- Planning files ---
if echo "$FILE" | grep -qE '(^NEXT\.md|^\.kr/|^docs/plans/)'; then
    SUGGESTIONS="Tools for planning: /catchup | /excerpt-status"
fi

# --- Library files ---
if echo "$FILE" | grep -qE '^library/'; then
    SUGGESTIONS="Tools for library: library-integrity-checker agent | knowledge-safety skill"
fi

# Output suggestion if any matched
if [ -n "$SUGGESTIONS" ]; then
    echo "$SUGGESTIONS"
fi

exit 0
