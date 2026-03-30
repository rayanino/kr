#!/usr/bin/env bash
# PreCompact: save critical working state before context is compressed.
# Compaction destroys context — this checkpoint lets PostCompact recovery
# restore the most important pieces (active engine, modified files, budget).

set -euo pipefail

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

CHECKPOINT_FILE="$CLAUDE_PROJECT_DIR/.claude/.pre_compact_checkpoint.json"

python3 -c "
import json, subprocess, os

state = {}

# Active task from NEXT.md
try:
    with open('NEXT.md') as f:
        state['active_task'] = f.readline().strip()
except Exception:
    pass

# Active engines (from git diff)
try:
    diff = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], text=True, timeout=5)
    engines = set()
    for line in diff.strip().split('\n'):
        if line.startswith('engines/'):
            parts = line.split('/')
            if len(parts) >= 2:
                engines.add(parts[1])
    state['active_engines'] = sorted(engines)
except Exception:
    pass

# Modified files list
try:
    diff = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], text=True, timeout=5)
    state['modified_files'] = [f for f in diff.strip().split('\n') if f]
except Exception:
    pass

# Budget
try:
    with open('tests/results/source_engine/COST_LOG.json') as f:
        d = json.load(f)
    state['budget_eur'] = sum(v.get('cost_eur', 0) for v in d.values() if isinstance(v, dict))
except Exception:
    pass

with open('$CHECKPOINT_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print(f'Pre-compaction checkpoint saved: {len(state)} fields')
" 2>/dev/null || true

exit 0
