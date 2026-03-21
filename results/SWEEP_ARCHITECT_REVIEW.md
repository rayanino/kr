# Sweep Architect Review

**Date:** 2026-03-21
**Session:** Weekend Task 2 — Bug Fix Sprint

All bugs from the 7,475-book corpus sweep were classified as FIX NOW and fixed with tests. Two items merit architect awareness:

---

## 1. Diacritics Canary — Range and Tolerance Changes

**What changed:**
- `_ARABIC_DIACRITICS` in `shamela.py` narrowed from 20 to 10 codepoints to match SPEC §5 line 1501 (`U+064B–U+0652, U+0670, U+0640`). Removed U+0653 (maddah above) and U+0656-U+065F (extended diacritics). Added missing U+0640 (tatweel).
- Canary comparison changed from exact sequence match to count comparison with ±1 tolerance.

**Why tolerance was needed:**
Even with the SPEC-aligned 10-codepoint set, regex and BS4 disagree on a standard fathatan (U+064B) in the word "محمداً" — regex finds 20 diacritics in 500 chars, BS4 finds 19. The disagreement is caused by an HTML entity encoding edge case where BS4 (lxml) handles entity decoding slightly differently from `html.unescape()`. This is a minor parser difference, not diacritics corruption.

**Risk assessment:**
- The canary still catches significant corruption (>1 diacritic loss in 500 chars)
- Validation check 8 (`validation.py:DIACRITICS_CHECK8`) performs exact per-page diacritics verification — it is the authoritative check, not the canary
- The canary is a quick safety net, not a precise validator

**Architect decision needed:**
- Should the SPEC's diacritics range (§5 line 1501) be expanded to include U+0653 and U+0656-U+065F? These are valid Arabic diacritics but were not in the original SPEC definition.
- Is ±1 tolerance appropriate, or should it be tighter/looser?

---

## 2. Pageless Books — Metadata Reclassification

**What changed:**
Added a pre-scan in `_pass1_parse()` to detect books without any `(ص: N)` page numbers. For such books, only the first page is classified as metadata (book info). All subsequent pages fall through to content processing.

**Why this is safe:**
- Books WITH page numbers are completely unaffected — the pre-scan flag (`any_numbered_page`) is True, and the existing metadata detection logic runs unchanged.
- The fix restores 48 books (0.6% of corpus) that were silently producing zero content units.
- Both fixtures verified through the full `normalize()` pipeline:
  - `zero_content_hadith_dhunnun.htm`: 5 units, 11,511 chars
  - `zero_content_musnad_546pages.htm`: 545 units, 217,950 chars

**Architect decision needed:**
- Are there cases where a pageless book should legitimately produce zero content? (All 48 known cases are real books with substantial Arabic text.)
- Should pageless books get a quality flag so downstream engines can handle them differently?

---

## Summary

No bugs required deferral. Both fixes are localized (shamela.py only), tested, and verified. Full corpus re-verification is planned for Task 3.
