#!/usr/bin/env bash
# DR27 Enforcement: Stop Hook DR Deployment Check
# Warns (does not block) if a session modified engine/script files
# but deployed zero Deep Research reports.
#
# Matcher: Stop
# Exit 0 always (warning only — DR depends on owner relay availability)
#
# Reference: Protocol HR-27, CLAUDE.md Rule 15

set -euo pipefail

DISPATCH_LOG="$CLAUDE_PROJECT_DIR/.kr/runtime/dispatch_log.jsonl"

# Check if engine or script files were modified this session
MODIFIED_ENGINE=$(cd "$CLAUDE_PROJECT_DIR" && git diff --name-only HEAD 2>/dev/null | grep -cE '^(engines/|scripts/)' || echo "0")

# If no engine/script files modified, no DR check needed
if [ "$MODIFIED_ENGINE" = "0" ]; then
    exit 0
fi

# Engine/script files were modified. Check for DR dispatches.
DR_COUNT=0
if [ -f "$DISPATCH_LOG" ]; then
    DR_COUNT=$(grep -c '"dr"' "$DISPATCH_LOG" 2>/dev/null || echo "0")
    # Also check for dr in target_agent field specifically
    DR_COUNT2=$(grep -oP '"target_agent"\s*:\s*"[^"]*dr[^"]*"' "$DISPATCH_LOG" 2>/dev/null | wc -l || echo "0")
    if [ "$DR_COUNT2" -gt "$DR_COUNT" ]; then
        DR_COUNT="$DR_COUNT2"
    fi
fi

if [ "$DR_COUNT" = "0" ]; then
    echo "DR DEPLOYMENT WARNING (HR-27): This session modified $MODIFIED_ENGINE engine/script files but deployed ZERO Deep Research reports."
    echo ""
    echo "DR reports are the highest-ROI activity in this project (owner ALL-CAPS directive)."
    echo "Consider deploying DR for topics related to this session's work."
    echo ""
    echo "Suggested DR topics (based on modified files):"

    # Suggest topics based on what was modified
    if cd "$CLAUDE_PROJECT_DIR" && git diff --name-only HEAD 2>/dev/null | grep -q 'HARDENING_SESSION_PROTOCOL'; then
        echo "  1. Protocol governance: how do other multi-session agent systems enforce behavioral norms?"
    fi
    if cd "$CLAUDE_PROJECT_DIR" && git diff --name-only HEAD 2>/dev/null | grep -q 'engines/excerpting/src/'; then
        echo "  2. Excerpting engine: best practices for [specific topic from changes]"
    fi
    if cd "$CLAUDE_PROJECT_DIR" && git diff --name-only HEAD 2>/dev/null | grep -q 'scripts/'; then
        echo "  3. Tooling: prior art for [specific script category]"
    fi
    echo ""
    echo "To deploy: draft prompt → /prompt-architect → generate_promptcard.py → relay to owner"
fi

# Always exit 0 (warning only, not blocking)
exit 0
