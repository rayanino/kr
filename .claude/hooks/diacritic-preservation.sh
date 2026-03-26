#!/bin/bash
# PostToolUse hook: Verify Arabic diacritic count is preserved after edits
# Prevents T-1 (Silent Text Corruption) by detecting diacritic loss
# Only fires on Python files in engines/shared that contain Arabic text

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi

# Only check engine/shared source files
if ! echo "$FILE" | grep -qE '(engines|shared)/[^/]+/src/.*\.py$'; then
    exit 0
fi

# Check if file contains Arabic characters
HAS_ARABIC=$(python3 -c "
import sys
try:
    text = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
    has = any('\u0600' <= c <= '\u06FF' for c in text)
    print('yes' if has else 'no')
except Exception:
    print('no')
" "$FILE" 2>/dev/null)

if [ "$HAS_ARABIC" != "yes" ]; then
    exit 0
fi

# Count diacritics in current version
DIACRITIC_COUNT=$(python3 -c "
import sys
DIACRITICS = set(range(0x064B, 0x0654)) | {0x0670} | set(range(0x0656, 0x0660))
try:
    text = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
    count = sum(1 for c in text if ord(c) in DIACRITICS)
    print(count)
except Exception:
    print(-1)
" "$FILE" 2>/dev/null)

# Compare against git version (pre-edit)
GIT_DIACRITIC_COUNT=$(python3 -c "
import subprocess, sys
DIACRITICS = set(range(0x064B, 0x0654)) | {0x0670} | set(range(0x0656, 0x0660))
try:
    result = subprocess.run(['git', 'show', 'HEAD:' + sys.argv[1]], capture_output=True, timeout=5)
    if result.returncode != 0:
        print(-1)  # file is new, no comparison needed
    else:
        text = result.stdout.decode('utf-8', errors='ignore')
        count = sum(1 for c in text if ord(c) in DIACRITICS)
        print(count)
except Exception:
    print(-1)
" "$FILE" 2>/dev/null)

# If no git version exists (new file), skip comparison
if [ "$GIT_DIACRITIC_COUNT" = "-1" ] || [ "$DIACRITIC_COUNT" = "-1" ]; then
    exit 0
fi

# Compare: diacritics should not decrease
if [ "$DIACRITIC_COUNT" -lt "$GIT_DIACRITIC_COUNT" ]; then
    LOST=$((GIT_DIACRITIC_COUNT - DIACRITIC_COUNT))
    echo "WARNING: Arabic diacritic count DECREASED in $FILE" >&2
    echo "  Before: $GIT_DIACRITIC_COUNT diacritics | After: $DIACRITIC_COUNT diacritics | Lost: $LOST" >&2
    echo "  This may indicate T-1 (Silent Text Corruption). Verify the edit preserved Arabic text integrity." >&2
fi

exit 0
