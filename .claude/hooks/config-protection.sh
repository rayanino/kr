#!/bin/bash
# PreToolUse hook: Protect .claude/ configuration files from accidental modification
# Blocks Write/Edit/MultiEdit targeting settings.json, hooks/, or settings.local.json
# Escape hatch: set KR_CONFIG_EDIT=1 to allow edits for this session

# Allow if escape hatch is set
if [ "$KR_CONFIG_EDIT" = "1" ]; then
    exit 0
fi

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then
    exit 0
fi

# Check if file is a protected configuration file
if echo "$FILE" | grep -qE '\.claude/(settings\.json|settings\.local\.json)'; then
    echo '{"decision":"block","reason":"BLOCKED: Modifying .claude/settings.json is protected. This file controls all safety hooks (Arabic checks, D-023, circuit breaker, cost guard). Set KR_CONFIG_EDIT=1 to allow edits for this session."}'
    exit 0
fi

if echo "$FILE" | grep -qE '\.claude/hooks/[^/]+\.sh$'; then
    echo '{"decision":"block","reason":"BLOCKED: Modifying hook scripts is protected. These enforce Arabic safety, metadata preservation, and test execution. Set KR_CONFIG_EDIT=1 to allow edits for this session."}'
    exit 0
fi

exit 0
