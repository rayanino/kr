# Claude Code Task: Phase A Bug Fixes

**Context:** Phase A (deterministic sweep) completed: 2,519/2,519 success, zero crashes, 28.5 seconds. The pipeline is structurally sound. But the data reveals bugs in `shamela_html.py` that must be fixed before Step 3 (LLM probes). Every bug here will compound in Step 3 — a wrong muhaqiq value feeds into the LLM prompt, producing wrong inferences that we then spend time and money debugging.

**Read first:** `engines/source/CLAUDE.md`, `engines/source/src/extractors/shamela_html.py`

**Phase A results are at:** `tests/results/source_engine/phase_a/` (2,519 per-book JSONs + PHASE_A_SUMMARY.json). Use these to verify fixes.

---

## BUG 1 — CRITICAL: Category falsely assigned as muhaqiq (32 books)

### What happens

When a book title contains muhaqiq-related keywords (تحقيق, تخريج, تعليق, etc.), the MUHAQIQ_KEYWORDS pattern matching in `_parse_bibliographic_fields()` catches the **card header line** and assigns the Shamela **category** as `muhaqiq_name_raw`.

### Concrete examples

| Book | muhaqiq_name_raw | _field_source | What happened |
|------|-----------------|---------------|---------------|
| التحقيق في أحاديث الخلاف | `كتب السنة` | `التحقيق في أحاديث الخلاف   (ابن الجوزي)القسم` | Title contains "التحقيق", category "كتب السنة" assigned as muhaqiq |
| التعليق على تفسير الجلالين | `التفسير` | `التعليق على تفسير الجلالين...القسم` | Title contains "التعليق", category "التفسير" assigned as muhaqiq |
| أثر العلماء في تحقيق رسالة المسجد | `كتب عامة` | `أثر العلماء في تحقيق رسالة المسجد...القسم` | Title contains "تحقيق", category "كتب عامة" assigned as muhaqiq |

### Root cause

`_RE_FIELD` matches the card header line as a field. The header line format is roughly `TITLE&nbsp;&nbsp;&nbsp;(AUTHOR_SHORT)القسم: CATEGORY`. When the regex parses this, the "label" includes the title text, and the "value" is whatever follows. The MUHAQIQ_KEYWORDS check sees تحقيق/تخريج/تعليق in the label and assigns the value (which is the category name) as muhaqiq.

### Detection signal

Every bad case has `القسم` in `_field_source_muhaqiq_name_raw`. No legitimate muhaqiq field source ever contains `القسم`.

### Fix

In `_parse_bibliographic_fields()`, when the MUHAQIQ_KEYWORDS fallback fires, reject the match if:
- The label contains `القسم` (category marker — means this is the header line, not a real muhaqiq field), OR
- The value matches a known Shamela category name

Add `القسم` to `MUHAQIQ_EXCLUSIONS`.

### Verification

After the fix, re-run Phase A on the full collection. The 32 books should now have `muhaqiq_name_raw` absent (null) instead of containing a category name. Check: zero books should have a Shamela category string as their muhaqiq.

---

## BUG 2 — CRITICAL: 64 books have المؤلف in card but author_name_raw is null

### What happens

64 books have `المؤلف` present in their metadata card HTML, but `_RE_FIELD` fails to parse it correctly. The field ends up in `extra_card_fields` with a malformed key like:
```
key: "المؤلف : عبد الرحمن بن حسن حَبَنَّكَة الميداني الدمشقي (المتوفى"
val: "1425هـ)"
```

### Root cause

The `_RE_FIELD` regex expects: `<span class='title'>LABEL:</span> VALUE`. But in these books, the colon that the regex matches is NOT the field separator — it's a colon elsewhere in the text (like `المتوفى:` or `أ. د.:`). The regex grabs everything between `<span class='title'>` and that later colon as the "label", so the label includes the author name, and the "value" is just a fragment (like the death date).

### How to investigate

Pick one of the 64 affected books (e.g., `أجنحة المكر الثلاثة.htm` from the owner's collection at `C:\Users\Rayane\Desktop\kr\shamela export samples`). Read the raw HTML of the first PageText div. Compare the HTML structure of the `المؤلف` field against a book where extraction works (e.g., any of the 12 test fixtures). The difference will reveal the variant format.

### Known affected pattern

The extra_card_fields keys show the pattern — the المؤلف label is followed by ` : ` (space-colon-space) instead of `:` (colon only), or the colon is wrapped in different HTML. Examples:
- `المؤلف : عبد الرحمن بن حسن ...` — note the spaces around the colon
- `المؤلف: أ. د.` — the field value has a secondary colon that the regex matches instead
- `المؤلف: ابن عبد الهادي (ت` — the `(ت:` pattern inside the death date has a colon

### Fix

Investigate the raw HTML, then fix `_RE_FIELD` to handle the variant colon format. The fix must not break the 2,455 books where extraction currently works.

### Verification

After the fix, re-run Phase A. The 64 books should now have `author_name_raw` populated. Total `author_name_raw` count should go from 2,375 to ~2,439.

---

## BUG 3 — MODERATE: 32 books have no title_full (but have display_title)

### What happens

32 books lack a `الكتاب:` field in the expected format, so `title_full` is null. But all 32 have a correct `display_title` from the card header extraction. Some also have `الكتاب` as a malformed extra_card_field (same root cause as Bug 2 — variant colon format).

### Fix

Two-part fix:
1. If Bug 2's regex fix also fixes the `الكتاب` parsing, some of these 32 will be resolved.
2. Add a fallback in `extract_shamela_metadata()`: after all field parsing, if `title_full` is still absent but `display_title` is present, set `title_full = display_title`. This is safe because `display_title` comes from the card header, which is the authoritative title display.

### Verification

After the fix, `title_full` count should go from 2,472 to 2,504 (all 32 resolved, either by regex fix or fallback). Some may now have richer titles from the `الكتاب` field rather than just the `display_title`.

---

## FIX 4 — MINOR: Add 4 unmapped metadata labels to FIELD_MAP

These labels appear in the collection but aren't in `FIELD_MAP`, causing them to fall into `extra_card_fields` instead of their proper fields:

| Label | Count | Should map to | Rationale |
|-------|-------|--------------|-----------|
| `تأليف` | 3 | `author_name_raw` | Synonym for المؤلف |
| `بعناية` | 3 | `muhaqiq_name_raw` | Editorial care variant |
| `جمعها` | 3 | `compiler_name_raw` | Collection/compilation |
| `تاريخ النشر` | 4 | `publication_year_raw` | Publication date variant |

Also consider: `رواية` (26 books) — this means "narration/transmission" and is specific to hadith texts. Map to a new `_riwayah` key in `format_specific_metadata`, or capture in `extra_card_fields`. It is NOT a muhaqiq label. `انتقاء` (8 books, "selection") — similar to جمع, could map to `compiler_name_raw`.

### Fix

Add the labels to `FIELD_MAP` in `shamela_html.py`. Follow the existing pattern and add frequency comments.

### Verification

After fix, these 13+ books should have their fields extracted to proper internal names instead of `extra_card_fields`.

---

## FIX 5 — COSMETIC: Header line captured as extra_card_field (2,193 books)

### What happens

The card header line (`TITLE&nbsp;&nbsp;&nbsp;(AUTHOR_SHORT)القسم: CATEGORY`) is parsed by both `_parse_header()` (correctly, extracting `display_title` + `author_short`) and `_RE_FIELD` (incorrectly, as a bibliographic field). The `_RE_FIELD` match lands in `extra_card_fields` with a key like:
```
"أجنحة المكر الثلاثة   (عبد الرحمن حبنكة الميداني)القسم"
```

This is redundant data that clutters `extra_card_fields` in 87% of all books.

### Fix

In `_parse_bibliographic_fields()`, skip any `_RE_FIELD` match where the label contains `القسم`. This is safe because no real bibliographic field label ever contains `القسم` — it's always part of the header format.

Note: This fix overlaps with Bug 1's fix (both check for `القسم` in the label). Combine them into a single guard at the top of the field-processing loop.

### Verification

After fix, `extra_card_fields` should only contain genuinely unmapped fields. The `القسم`-containing keys should disappear from all 2,193 books.

---

## Testing strategy

### Step 1: Fix the code

All fixes are in `engines/source/src/extractors/shamela_html.py`. Bugs 1 and 5 share a fix point (reject `القسم` labels in the field loop). Bug 2 requires regex investigation on raw HTML. Bug 3 is a fallback. Fix 4 is a FIELD_MAP addition.

### Step 2: Run existing unit tests

```bash
python -m pytest tests/ -x -q
```

All 768+ tests must still pass. No regressions.

### Step 3: Re-run Phase A on the full collection

```bash
python scripts/run_phase_a.py "C:\Users\Rayane\Desktop\kr\shamela export samples"
```

### Step 4: Compare results

Compare the new PHASE_A_SUMMARY.json against the baseline:

| Metric | Before | Expected After |
|--------|--------|----------------|
| successful | 2,519 | 2,519 (no regressions) |
| errors | 0 | 0 |
| title_full count | 2,472 (98.1%) | ≥2,504 (≥99.4%) |
| author_name_raw count | 2,375 (94.3%) | ≥2,439 (≥96.9%) |
| muhaqiq_name_raw count | 1,372 (54.5%) | ~1,340 (32 false positives removed, some real ones added) |
| Books with category-as-muhaqiq | 32 | 0 |

### Step 5: Spot-check affected books

Pick 5 books from each bug category and verify the extraction is now correct:
- Bug 1: Verify "التحقيق في أحاديث الخلاف" has muhaqiq_name_raw = null (not "كتب السنة")
- Bug 2: Verify "أجنحة المكر الثلاثة.htm" has author_name_raw populated
- Bug 3: Verify "الإغراب للنسائي.htm" has title_full populated
- Fix 4: Verify any book with `تأليف` label has author_name_raw populated from it
- Fix 5: Verify extra_card_fields no longer contains القسم-pattern keys

### Step 6: Write PHASE_A_LESSONS.md

After all fixes are verified, create `tests/results/source_engine/phase_a/PHASE_A_LESSONS.md` documenting:
- Bugs found and fixed (with commit hashes)
- Field distribution patterns discovered
- Quality issue patterns (90 page mismatches, 32 truncations, 10 minimal content)
- Recommendations for Step 3 (LLM probes)
- The 57 books with author_short only (no card field) — these need LLM inference in Step 3
- The zero duplicates finding

## What NOT to do

- Do NOT modify `run_phase_a.py` — the script worked correctly, the bugs are in the extractor
- Do NOT modify any module outside `shamela_html.py` for Bugs 1–3 and Fix 5
- Do NOT change the quality inspection logic — it correctly identified all 90+32+10 issues
- Do NOT attempt to fix the 90 page count mismatches or 32 truncations — those are real data quality issues in the Shamela exports, not extraction bugs
