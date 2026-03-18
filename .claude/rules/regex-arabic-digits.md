---
globs: ["engines/*/src/**/*.py", "shared/*/src/**/*.py"]
---
- When writing regex for text that may contain Arabic, NEVER use `\d` or `\D` to match ASCII-only digits. Python 3's `\d` matches Unicode digits including Arabic-Indic (٠-٩, U+0660–U+0669) and Eastern Arabic-Indic (۰-۹, U+06F0–U+06F9). Use `[0-9]` explicitly.
- Common trap: `\((\d+)\)` intended for footnote refs `(1)` will also match hadith numbers `(٢٣٤٥)`, verse numbers `(٣)`, and date patterns `(٧٦٩)`.
- Similarly: `\w` matches Arabic letters. Use `[a-zA-Z]` or `[a-zA-Z0-9]` for Latin/ASCII-only word characters.
- `\b` (word boundary) does NOT work reliably at Arabic word boundaries — Arabic has clitics (prefixed ال, و, ب, ك, ل) that don't create \b boundaries.
- Use explicit Unicode ranges for Arabic character matching: `[\u0600-\u06FF]` (Arabic block), `[\u0750-\u077F]` (supplement), `[\uFB50-\uFDFF\uFE70-\uFEFF]` (presentation forms).
- If you genuinely need `\d` to match all Unicode digits, add a `# safe: intentional Unicode \d` comment to suppress warnings.
