#!/bin/bash
# Arabic text safety check — PostToolUse hook for Python files in engine/shared src
# Scans modified Python files for common Arabic text corruption patterns.
# Non-blocking: outputs warnings to stderr, always exits 0.

FILE="$CLAUDE_TOOL_FILE_PATH"

# Only check Python source files in engines/ and shared/
if [ -z "$FILE" ]; then
    exit 0
fi
if ! echo "$FILE" | grep -qE '\.(py)$'; then
    exit 0
fi
if ! echo "$FILE" | grep -qE '(engines|shared)/.*src/'; then
    exit 0
fi

WARNINGS=""

# Check 1: .lower()/.upper() — destroys Arabic text (Arabic has no case)
if grep -nE '\.(lower|upper)\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' > /dev/null; then
    LINES=$(grep -nE '\.(lower|upper)\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | head -3)
    WARNINGS="${WARNINGS}WARNING: .lower()/.upper() found — Arabic has no case. Verify this only applies to non-Arabic text.\n${LINES}\n\n"
fi

# Check 2: .strip() without explicit chars — may strip Arabic diacritics
if grep -nE '\.strip\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' > /dev/null; then
    LINES=$(grep -nE '\.strip\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | head -3)
    WARNINGS="${WARNINGS}WARNING: bare .strip() found — safe for whitespace but verify no Arabic diacritics are affected.\n${LINES}\n\n"
fi

# Check 3: .replace() calls in files containing Arabic text
# Use python for Arabic detection — grep -P with Unicode ranges fails on Windows Git Bash
if python3 -c "import sys; sys.exit(0 if any('\u0600'<=c<='\u06FF' for line in open(sys.argv[1],encoding='utf-8',errors='ignore') for c in line) else 1)" "$FILE" 2>/dev/null; then
    if grep -nE '\.replace\(' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | grep -v '# normalize' > /dev/null; then
        LINES=$(grep -nE '\.replace\(' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | grep -v '# normalize' | head -3)
        WARNINGS="${WARNINGS}WARNING: .replace() in file with Arabic content — verify this preserves text integrity.\n${LINES}\n\n"
    fi
fi

# Check 4: Hardcoded Latin-only regex patterns that might miss Arabic
if grep -nE "\[a-zA-Z\]|\[A-Za-z\]|\[a-z\]|\[A-Z\]" "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' > /dev/null; then
    LINES=$(grep -nE "\[a-zA-Z\]|\[A-Za-z\]|\[a-z\]|\[A-Z\]" "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | head -3)
    WARNINGS="${WARNINGS}WARNING: Latin-only regex pattern found — will miss Arabic text. Use Unicode categories (\\p{L}) instead.\n${LINES}\n\n"
fi

# Check 5: Encoding assumptions (ascii, latin-1 on files that should be utf-8)
if grep -nE "encoding=['\"]?(ascii|latin|iso-8859|windows-1256)" "$FILE" 2>/dev/null | grep -v '#.*noqa' > /dev/null; then
    LINES=$(grep -nE "encoding=['\"]?(ascii|latin|iso-8859|windows-1256)" "$FILE" 2>/dev/null | grep -v '#.*noqa' | head -3)
    WARNINGS="${WARNINGS}WARNING: Non-UTF-8 encoding found — KR requires UTF-8 for all text. Verify this is intentional (e.g., converting FROM this encoding).\n${LINES}\n\n"
fi

# Output warnings if any
if [ -n "$WARNINGS" ]; then
    echo -e "ARABIC SAFETY CHECK — $FILE\n$WARNINGS" >&2
fi

exit 0
