#!/usr/bin/env bash
# UserPromptSubmit hook: injects active task context before each prompt.
# Lightweight — runs on every user message, so must be fast (<1s).
# Output goes to additionalContext, which Claude sees alongside the prompt.

set -euo pipefail

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

CONTEXT=""

# Active task from NEXT.md (first non-empty, non-comment line)
if [ -f "NEXT.md" ]; then
    TASK=$(head -1 NEXT.md 2>/dev/null | sed 's/^# //' || true)
    if [ -n "$TASK" ]; then
        CONTEXT="Active task: $TASK"
    fi
fi

# Active engine (detect from NEXT.md content or recent git changes)
ACTIVE_ENGINE=""
if [ -f "NEXT.md" ]; then
    ACTIVE_ENGINE=$(grep -oP '(?<=engines/)\w+' NEXT.md 2>/dev/null | head -1 || true)
fi
if [ -z "$ACTIVE_ENGINE" ]; then
    # Fallback: most recently modified engine
    ACTIVE_ENGINE=$(git diff --name-only HEAD 2>/dev/null | grep -oP '(?<=engines/)\w+' | head -1 || true)
fi
if [ -n "$ACTIVE_ENGINE" ]; then
    CONTEXT="$CONTEXT | Engine: $ACTIVE_ENGINE"
fi

# Budget status (fast: just read the JSON)
if [ -f "tests/results/source_engine/COST_LOG.json" ]; then
    BUDGET=$(python3 -c "
import json, os
try:
    d = json.load(open('tests/results/source_engine/COST_LOG.json'))
    t = sum(v.get('cost_eur', 0) for v in d.values() if isinstance(v, dict))
    b = float(os.environ.get('KR_BUDGET_LIMIT', '100'))
    print(f'EUR {t:.1f}/{b:.0f}')
except: pass
" 2>/dev/null || true)
    if [ -n "$BUDGET" ]; then
        CONTEXT="$CONTEXT | Budget: $BUDGET"
    fi
fi

# Excerpting hardening phase detection
if [ -d "integration_tests/v2_final" ]; then
    CONTEXT="$CONTEXT | Phase: 3 (Full run)"
elif [ -d "integration_tests/smoke_api_v2" ] && find "integration_tests/smoke_api_v2" -name "*.jsonl" -print -quit 2>/dev/null | grep -q .; then
    CONTEXT="$CONTEXT | Phase: 1-2 (Smoke/Hardening)"
elif [ -d "integration_tests/questionnaire" ] && [ ! -f "integration_tests/questionnaire/COMPLETE" ]; then
    CONTEXT="$CONTEXT | Phase: 0 (Q&A)"
fi

# Modified files count (quick orientation)
MOD_COUNT=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ' || echo "0")
if [ "$MOD_COUNT" -gt 0 ]; then
    CONTEXT="$CONTEXT | Modified: $MOD_COUNT files"
fi


# F1 ENFORCEMENT: Dispatch state reminder
if [ -f ".kr/runtime/dispatch_log.jsonl" ]; then
    LAST_DISPATCH_AGO=$(python3 -c "
import json, sys
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
try:
    lines = open('.kr/runtime/dispatch_log.jsonl').readlines()
    if lines:
        last = json.loads(lines[-1].strip())
        ts = datetime.fromisoformat(last.get('timestamp','').replace('Z','+00:00'))
        delta = now - ts
        hours = delta.total_seconds() / 3600
        if hours > 2:
            print(f'NO DISPATCH in {hours:.0f}h')
except: pass
" 2>/dev/null)
    if [ -n "$LAST_DISPATCH_AGO" ]; then
        CONTEXT="$CONTEXT | DISPATCH: $LAST_DISPATCH_AGO — dispatch coworkers before any major conclusion"
    fi
else
    CONTEXT="$CONTEXT | DISPATCH: No dispatch log found — create .kr/runtime/dispatch_log.jsonl"
fi

# F2 ENFORCEMENT: Leadership reminder (always injected, compaction-proof)
CONTEXT="$CONTEXT | ROLE: Senior engineer. After milestones: propose + execute next steps. NEVER say standing by/waiting/should I."

# Only output if we have context to inject
if [ -n "$CONTEXT" ]; then
    echo "$CONTEXT"
fi

exit 0
