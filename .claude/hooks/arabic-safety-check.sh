#!/bin/bash
# Arabic text safety check — PostToolUse hook for Python files in engine/shared src
# Scans modified Python files for common Arabic text corruption patterns.
# Check 1 (.lower/.upper/.casefold) is BLOCKING when file contains Arabic.
# Check 9 (lossy encode) is BLOCKING — silently destroys Arabic.
# Checks 2-8, 10 are non-blocking warnings (exit 0).

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

# Check 1: .lower()/.upper()/.casefold() — BLOCKING when file contains Arabic text
# .casefold() is Python's aggressive case-folding — equally destructive to Arabic
LOWER_UPPER=$(grep -nE '\.(lower|upper|casefold)\(\)' "$FILE" 2>/dev/null | grep -v '#.*noqa' | grep -v '# safe:')
if [ -n "$LOWER_UPPER" ]; then
    # Reuse the same Arabic detection as Check 3
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

# Check 6: re.DOTALL on regex patterns with . quantifiers (I-5)
# Patterns with .{0,N} or .* applied to primary_text may miss newlines without DOTALL
if grep -nE "re\.compile\(.*\.[\*\+\{]" "$FILE" 2>/dev/null | grep -v 'DOTALL' | grep -v '# safe:' > /dev/null; then
    LINES=$(grep -nE "re\.compile\(.*\.[\*\+\{]" "$FILE" 2>/dev/null | grep -v 'DOTALL' | grep -v '# safe:' | head -3)
    WARNINGS="${WARNINGS}WARNING: regex with . quantifier may need re.DOTALL if text contains newlines.\n${LINES}\n\n"
fi

# Check 7: \d in regex patterns — matches Arabic-Indic digits (٠-٩)
# Python 3's \d matches Unicode digits including U+0660-0669 and U+06F0-06F9.
# Use [0-9] for ASCII-only digit matching.
UNSAFE_D=$(grep -nE "r['\"].*\\\\d" "$FILE" 2>/dev/null | grep -v '# safe:' | grep -v '\[0-9\]')
if [ -n "$UNSAFE_D" ]; then
    WARNINGS="${WARNINGS}WARNING: \\d in regex — Python \\d matches Arabic-Indic digits (٠-٩). Use [0-9] for ASCII-only.\n$(echo "$UNSAFE_D" | head -3)\n\n"
fi

# 8. Invisible Unicode detection (WARNING) — zero-width spaces, BOM, bidi overrides
# These can silently corrupt Arabic scholarly text at ingestion boundaries
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
    WARNINGS="${WARNINGS}WARNING: Invisible Unicode characters found (may corrupt Arabic text):\n${INVISIBLE}\n\n"
fi

# Check 9: .encode() with lossy codecs — BLOCKING
# .encode('ascii', errors='ignore') silently drops ALL Arabic characters
# .encode('latin-1') / .encode('cp1252') converts unmappable Arabic to '?'
ENCODE_LOSSY=$(grep -nE "\.encode\(['\"]?(ascii|latin|cp1252|iso-8859)" "$FILE" 2>/dev/null | grep -v '# safe:')
if [ -n "$ENCODE_LOSSY" ]; then
    echo "BLOCKED: Lossy .encode() found — will silently destroy Arabic text." >&2
    echo "Use .encode('utf-8') instead. Add '# safe: reason' comment to bypass." >&2
    echo "$ENCODE_LOSSY" >&2
    exit 1
fi

# Check 9b: .decode() with lossy error handlers (Codex audit finding)
# bytes.decode('utf-8', errors='ignore') silently drops malformed Arabic sequences
DECODE_LOSSY=$(grep -nE "\.decode\(.*errors=['\"]?(ignore|replace)" "$FILE" 2>/dev/null | grep -v '# safe:')
if [ -n "$DECODE_LOSSY" ]; then
    WARNINGS="${WARNINGS}WARNING: Lossy .decode() with errors='ignore'/'replace' — may silently drop Arabic characters.\n$(echo "$DECODE_LOSSY" | head -3)\n\n"
fi

# Check 9c: open() with lossy error handlers (Codex audit finding)
OPEN_LOSSY=$(grep -nE "open\(.*errors=['\"]?(ignore|replace)" "$FILE" 2>/dev/null | grep -v '# safe:')
if [ -n "$OPEN_LOSSY" ]; then
    WARNINGS="${WARNINGS}WARNING: open() with errors='ignore'/'replace' — may silently drop Arabic characters on read.\n$(echo "$OPEN_LOSSY" | head -3)\n\n"
fi

# Check 10: unicodedata.normalize('NFKD'/'NFD') — decomposes Arabic diacritics
# NFKD/NFD decompose Arabic combining marks (fatha, damma, kasra, shadda, sukun)
# into separate code points, violating D-004 (primary text bytes never modified).
# NFC/NFKC are generally safe (they compose, not decompose).
NFKD=$(grep -nE "normalize\(['\"]NFD|normalize\(['\"]NFKD" "$FILE" 2>/dev/null | grep -v '# safe:')
if [ -n "$NFKD" ]; then
    WARNINGS="${WARNINGS}CRITICAL WARNING: unicodedata.normalize('NFKD'/'NFD') decomposes Arabic diacritics into separate combining chars.\nThis violates D-004 (primary text immutability). Use NFC if normalization is needed.\n$(echo "$NFKD" | head -3)\n\n"
fi

# Check 11: re.ASCII flag — makes \w, \b, \d exclude all Arabic characters
RE_ASCII=$(grep -nE 're\.ASCII|re\.A\b|flags=.*re\.A\b' "$FILE" 2>/dev/null | grep -v '# safe:')
if [ -n "$RE_ASCII" ]; then
    WARNINGS="${WARNINGS}WARNING: re.ASCII flag makes \\w, \\b, \\d exclude Arabic characters entirely.\n$(echo "$RE_ASCII" | head -3)\n\n"
fi

# Output warnings if any
if [ -n "$WARNINGS" ]; then
    echo -e "ARABIC SAFETY CHECK — $FILE\n$WARNINGS" >&2
fi

exit 0
