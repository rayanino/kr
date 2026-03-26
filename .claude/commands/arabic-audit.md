---
description: Comprehensive Arabic text safety audit on changed files. Runs all checks from arabic-safety-check hook plus domain-specific checks from skills. Usage /arabic-audit [file|engine].
allowed-tools: Bash(python *), Bash(python3 *), Bash(grep *), Read, Glob, Grep
---
Run a comprehensive Arabic text safety audit. Parse `$ARGUMENTS` as a file path or engine name. If empty, audit all recently changed Python files.

## Scope

Determine files to audit:
```bash
# If argument is a file path, audit that file
# If argument is an engine name, audit engines/<name>/src/*.py
# If no argument, audit recently changed files
git diff --name-only HEAD~3 -- '*.py' 2>/dev/null
```

## Checks (run all, report per-file)

### Level 1: Syntax Safety (from arabic-safety-check.sh)

1. **Dangerous string methods:** `.lower()`, `.upper()`, `.title()`, `.capitalize()` on variables that could hold Arabic text
2. **Unsafe strip:** `.strip()`, `.rstrip()`, `.lstrip()` without explicit ASCII-only chars
3. **Regex digit trap:** `\d` without `# safe: intentional Unicode \d` comment
4. **Regex word trap:** `\w` without `# safe: intentional Unicode \w` comment
5. **Regex boundary trap:** `\b` used near Arabic text patterns
6. **Unicode normalization:** `unicodedata.normalize`, `NFC`, `NFD`, `NFKC`, `NFKD`
7. **Invisible Unicode:** Creation or manipulation of U+200B, U+200E/F, U+202A-202E, U+FEFF
8. **Encoding assumptions:** `encode('ascii')`, `encode('latin-1')`, `encode('cp1256')` without explicit conversion context

### Level 2: Diacritic Safety (T-1 defense)

9. **Diacritic range completeness:** If code references diacritic range, verify it includes U+0653 (maddah) and U+0670 (superscript alef)
10. **Range boundary:** Check for off-by-one in `range()` calls near diacritic constants (exclusive upper bound is common trap)
11. **String comparison:** If Arabic text is compared with `==`, check if diacritics affect the comparison intent

### Level 3: Domain Conventions (from arabic-scholarly-conventions.md)

12. **Bismillah handling:** If code detects بسم الله الرحمن الرحيم, verify it treats position-0 occurrence as muqaddimah, not Quranic
13. **Colophon attribution:** If code processes كتبه or ألفه, verify it distinguishes copyist from author
14. **Honorific stripping:** If code extracts scholar names, verify it strips الشيخ/الإمام/العلامة for matching but preserves for display
15. **Isnad atomicity:** If code splits text into passages, verify transmission formulas (حدثنا, أخبرنا) are kept as atomic units
16. **Abbreviation preservation:** If code normalizes text, verify ﷺ and other abbreviations are preserved as-is

### Level 4: Knowledge Integrity

17. **D-023 pass-through:** If function transforms data, verify all input metadata appears in output
18. **D-041 consensus:** If function makes content classification, verify it uses multi-model consensus
19. **Frozen source integrity:** If function reads from frozen sources, verify it never writes back

## Output Format

```
=== Arabic Safety Audit ===
Files audited: [N]
Date: [ISO 8601]

--- [file_path] ---
  Level 1: [N issues]
    L1.3 [line:col] \d used without safe comment — use [0-9]
    L1.6 [line:col] unicodedata.normalize() applied to Arabic text variable
  Level 2: [N issues]
    L2.1 [line:col] diacritic range 0x064B-0x0652 missing maddah (0x0653)
  Level 3: [N issues]
    (none)
  Level 4: [N issues]
    (none)

--- [file_path] ---
  All levels: CLEAN

=== Summary ===
  Level 1 (Syntax):    [N] issues across [M] files
  Level 2 (Diacritic): [N] issues across [M] files
  Level 3 (Domain):    [N] issues across [M] files
  Level 4 (Integrity): [N] issues across [M] files
  Total: [N] issues

  Verdict: CLEAN | [N] issues found (L1: [n], L2: [n], L3: [n], L4: [n])
```

## Rules
- Level 1 and 2 issues are HIGH severity (potential data corruption).
- Level 3 and 4 issues are MEDIUM severity (potential misclassification).
- Skip test files for Level 3 and 4 checks (domain conventions are tested differently).
- If a file has no Arabic text handling at all, report "N/A — no Arabic text operations detected".
- For each issue, show the exact line and suggest the fix.
