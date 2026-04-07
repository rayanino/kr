#!/bin/bash
# PostToolUse hook: Consolidated domain safety checks for scholarly text integrity.
# Merges: arabic-safety-check.sh + diacritic-preservation.sh + boundary-check.sh
# Contains BLOCKING checks (exit 1) for .lower/.upper on Arabic and lossy .encode.
# All other checks are advisory warnings (exit 0).

FILE="$CLAUDE_TOOL_FILE_PATH"
if [ -z "$FILE" ]; then exit 0; fi
if ! echo "$FILE" | grep -qE '\.py$'; then exit 0; fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# ═══════════════════════════════════════════════════════════════════════
# Phase 1: Arabic Safety Checks (11 patterns)
# Only for engine/shared src files
# ═══════════════════════════════════════════════════════════════════════
if echo "$FILE" | grep -qE '(engines|shared)/.*src/.*\.py$'; then

    WARNINGS=""

    # Check 1: .lower()/.upper()/.casefold() — BLOCKING when file contains Arabic
    LOWER_UPPER=$(grep -nE '\.(lower|upper|casefold)\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:')
    if [ -n "$LOWER_UPPER" ]; then
        HAS_ARABIC=$(python3 -c "import sys; sys.exit(0 if any('\u0600'<=c<='\u06FF' for line in open(sys.argv[1],encoding='utf-8',errors='ignore') for c in line) else 1)" "$FILE" 2>/dev/null && echo "yes" || echo "no")
        if [ "$HAS_ARABIC" = "yes" ]; then
            echo "BLOCKED: .lower()/.upper()/.casefold() in file with Arabic content." >&2
            echo "Arabic has no case — this WILL corrupt data. Add '# safe: reason' comment to bypass." >&2
            echo "$LOWER_UPPER" >&2
            exit 1
        else
            WARNINGS="${WARNINGS}WARNING: .lower()/.upper()/.casefold() found — verify this only applies to non-Arabic text.\n$(echo "$LOWER_UPPER" | head -3)\n\n"
        fi
    fi

    # Check 2: .strip() without explicit chars
    if grep -nE '\.strip\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' > /dev/null; then
        LINES=$(grep -nE '\.strip\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | head -3)
        WARNINGS="${WARNINGS}WARNING: bare .strip() found — verify no Arabic diacritics are affected.\n${LINES}\n\n"
    fi

    # Check 3: .replace() in files containing Arabic text
    if python3 -c "import sys; sys.exit(0 if any('\u0600'<=c<='\u06FF' for line in open(sys.argv[1],encoding='utf-8',errors='ignore') for c in line) else 1)" "$FILE" 2>/dev/null; then
        if grep -nE '\.replace\(' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | grep -v '# normalize' > /dev/null; then
            LINES=$(grep -nE '\.replace\(' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | grep -v '# normalize' | head -3)
            WARNINGS="${WARNINGS}WARNING: .replace() in file with Arabic content — verify text integrity.\n${LINES}\n\n"
        fi
    fi

    # Check 4: Latin-only regex patterns
    if grep -nE "\[a-zA-Z\]|\[A-Za-z\]|\[a-z\]|\[A-Z\]" "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' > /dev/null; then
        LINES=$(grep -nE "\[a-zA-Z\]|\[A-Za-z\]|\[a-z\]|\[A-Z\]" "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:' | head -3)
        WARNINGS="${WARNINGS}WARNING: Latin-only regex — will miss Arabic text.\n${LINES}\n\n"
    fi

    # Check 5: Non-UTF-8 encoding
    if grep -nE "encoding=['\"]?(ascii|latin|iso-8859|windows-1256)" "$FILE" 2>/dev/null | grep -v '#.*noqa' > /dev/null; then
        LINES=$(grep -nE "encoding=['\"]?(ascii|latin|iso-8859|windows-1256)" "$FILE" 2>/dev/null | grep -v '#.*noqa' | head -3)
        WARNINGS="${WARNINGS}WARNING: Non-UTF-8 encoding — KR requires UTF-8.\n${LINES}\n\n"
    fi

    # Check 6: re.compile with . quantifiers without DOTALL
    if grep -nE "re\.compile\(.*\.[\*\+\{]" "$FILE" 2>/dev/null | grep -v 'DOTALL' | grep -v '# safe:' > /dev/null; then
        LINES=$(grep -nE "re\.compile\(.*\.[\*\+\{]" "$FILE" 2>/dev/null | grep -v 'DOTALL' | grep -v '# safe:' | head -3)
        WARNINGS="${WARNINGS}WARNING: regex with . quantifier may need re.DOTALL.\n${LINES}\n\n"
    fi

    # Check 7: \d matching Arabic-Indic digits
    UNSAFE_D=$(grep -nE "r['\"].*\\\\d" "$FILE" 2>/dev/null | grep -v '# safe:' | grep -v '\[0-9\]')
    if [ -n "$UNSAFE_D" ]; then
        WARNINGS="${WARNINGS}WARNING: \\d matches Arabic-Indic digits. Use [0-9] for ASCII-only.\n$(echo "$UNSAFE_D" | head -3)\n\n"
    fi

    # Check 8: Invisible Unicode characters
    INVISIBLE=$(python3 -c "
import sys
with open(sys.argv[1], encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f, 1):
        for c in line:
            if ord(c) in (0x200B, 0x200E, 0x200F, 0xFEFF, 0x2060, 0x00AD) or 0x202A <= ord(c) <= 0x202E:
                if '# safe:' not in line:
                    print(f'  {sys.argv[1]}:{i}: invisible U+{ord(c):04X}')
                    break
" "$FILE" 2>/dev/null)
    if [ -n "$INVISIBLE" ]; then
        WARNINGS="${WARNINGS}WARNING: Invisible Unicode characters found:\n${INVISIBLE}\n\n"
    fi

    # Check 9: .encode() with lossy codecs — BLOCKING
    ENCODE_LOSSY=$(grep -nE "\.encode\(['\"]?(ascii|latin|cp1252|iso-8859)" "$FILE" 2>/dev/null | grep -v '# safe:')
    if [ -n "$ENCODE_LOSSY" ]; then
        echo "BLOCKED: Lossy .encode() — will silently destroy Arabic text." >&2
        echo "Use .encode('utf-8') instead. Add '# safe: reason' comment to bypass." >&2
        echo "$ENCODE_LOSSY" >&2
        exit 1
    fi

    # Check 9b: .decode() with lossy error handlers
    DECODE_LOSSY=$(grep -nE "\.decode\(.*errors=['\"]?(ignore|replace)" "$FILE" 2>/dev/null | grep -v '# safe:')
    if [ -n "$DECODE_LOSSY" ]; then
        WARNINGS="${WARNINGS}WARNING: Lossy .decode() with errors='ignore'/'replace'.\n$(echo "$DECODE_LOSSY" | head -3)\n\n"
    fi

    # Check 9c: open() with lossy error handlers
    OPEN_LOSSY=$(grep -nE "open\(.*errors=['\"]?(ignore|replace)" "$FILE" 2>/dev/null | grep -v '# safe:')
    if [ -n "$OPEN_LOSSY" ]; then
        WARNINGS="${WARNINGS}WARNING: open() with errors='ignore'/'replace'.\n$(echo "$OPEN_LOSSY" | head -3)\n\n"
    fi

    # Check 10: NFD/NFKD decomposition of Arabic diacritics
    NFKD=$(grep -nE "normalize\(['\"]NFD|normalize\(['\"]NFKD" "$FILE" 2>/dev/null | grep -v '# safe:')
    if [ -n "$NFKD" ]; then
        WARNINGS="${WARNINGS}CRITICAL WARNING: normalize('NFKD'/'NFD') decomposes Arabic diacritics. Violates D-004.\n$(echo "$NFKD" | head -3)\n\n"
    fi

    # Check 11: re.ASCII flag excludes Arabic
    RE_ASCII=$(grep -nE 're\.ASCII|re\.A\b|flags=.*re\.A\b' "$FILE" 2>/dev/null | grep -v '# safe:')
    if [ -n "$RE_ASCII" ]; then
        WARNINGS="${WARNINGS}WARNING: re.ASCII makes \\w, \\b, \\d exclude Arabic.\n$(echo "$RE_ASCII" | head -3)\n\n"
    fi

    if [ -n "$WARNINGS" ]; then
        echo -e "ARABIC SAFETY — $FILE\n$WARNINGS" >&2
    fi
fi

# ═══════════════════════════════════════════════════════════════════════
# Phase 2: Diacritic Preservation Check
# Only for engine/shared src files containing Arabic
# ═══════════════════════════════════════════════════════════════════════
if echo "$FILE" | grep -qE '(engines|shared)/[^/]+/src/.*\.py$'; then
    HAS_ARABIC=$(python3 -c "
import sys
try:
    text = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
    print('yes' if any('\u0600' <= c <= '\u06FF' for c in text) else 'no')
except Exception:
    print('no')
" "$FILE" 2>/dev/null)

    if [ "$HAS_ARABIC" = "yes" ]; then
        DIACRITIC_COUNT=$(python3 -c "
import sys
DIACRITICS = set(range(0x064B, 0x0654)) | {0x0670} | set(range(0x0656, 0x0660))
try:
    text = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
    print(sum(1 for c in text if ord(c) in DIACRITICS))
except Exception:
    print(-1)
" "$FILE" 2>/dev/null)

        GIT_DIACRITIC_COUNT=$(python3 -c "
import os, subprocess, sys
DIACRITICS = set(range(0x064B, 0x0654)) | {0x0670} | set(range(0x0656, 0x0660))
try:
    rel_path = os.path.relpath(sys.argv[1]).replace('\\\\', '/')
    result = subprocess.run(['git', 'show', 'HEAD:' + rel_path], capture_output=True, timeout=5)
    if result.returncode != 0:
        print(-1)
    else:
        text = result.stdout.decode('utf-8', errors='ignore')
        print(sum(1 for c in text if ord(c) in DIACRITICS))
except Exception:
    print(-1)
" "$FILE" 2>/dev/null)

        if [ "$GIT_DIACRITIC_COUNT" != "-1" ] && [ "$DIACRITIC_COUNT" != "-1" ]; then
            if [ "$DIACRITIC_COUNT" -lt "$GIT_DIACRITIC_COUNT" ]; then
                LOST=$((GIT_DIACRITIC_COUNT - DIACRITIC_COUNT))
                echo "WARNING: Arabic diacritic count DECREASED in $FILE" >&2
                echo "  Before: $GIT_DIACRITIC_COUNT | After: $DIACRITIC_COUNT | Lost: $LOST" >&2
                echo "  May indicate T-1 (Silent Text Corruption)." >&2
            fi
        fi
    fi
fi

# ═══════════════════════════════════════════════════════════════════════
# Phase 3: Boundary / Metadata Flow Check (D-023)
# ═══════════════════════════════════════════════════════════════════════
if echo "$FILE" | grep -qE 'contracts\.py$'; then
    echo "--- D-023: Metadata flow verification (contracts.py changed) ---"
    python3 scripts/verify_metadata_flow.py 2>&1 | tail -15

    if [ -f "tools/check_cross_engine_contracts.py" ]; then
        echo ""
        echo "--- Cross-engine contract validation ---"
        PYTHONIOENCODING=utf-8 python3 tools/check_cross_engine_contracts.py 2>&1 | tail -10
    fi
elif echo "$FILE" | grep -qE 'engines/[^/]+/src/.*\.py$'; then
    echo "--- D-023: Verify metadata pass-through in changed functions ---"
fi

exit 0
