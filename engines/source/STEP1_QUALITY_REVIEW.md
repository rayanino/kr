# Step 1 Quality Review — Deep Analysis

**Date:** 2026-03-09
**Method:** Systematic review across 8 dimensions: contract alignment, extraction correctness, workflow consistency, stale references, field mapping, error handling, test coverage, and logical coherence. All findings verified against real fixtures and contracts.py.

---

## Critical Findings (must fix before Step 2)

### F1: Workflow Step Ordering Contradiction
**Location:** §4.A.2 Steps 5-6 vs §4.A.7
**Problem:** Step 5 is "Duplicate detection" and Step 6 is "Freezing." But §4.A.7 says "After freezing (Step 6), the composite SHA-256 hash is compared..." Dedup can't use the hash if it hasn't been computed yet. Additionally, `source_id = src_{first 8 chars of hash}` is needed at Step 6 to create the frozen directory, but the hash is computed AS PART OF Step 6.
**Fix:** Restructure the workflow. The correct order is:
1. Compute staging hashes (before dedup, before freeze)
2. Derive source_id from staging hashes
3. Check dedup using staging hash
4. If not duplicate: copy to `library/sources/{source_id}/frozen/`, verify frozen hashes match staging hashes
This means Step 5 should be "Hashing + Dedup" and Step 6 should be "Copy + Verify + Permissions."

### F2: `text_fidelity_reason` Required in Contracts But Missing from SPEC
**Location:** contracts.py `SourceMetadata.text_fidelity_reason: str` (required, no default)
**Problem:** The SPEC never mentions `text_fidelity_reason` or how to populate it. Claude Code would not know what to put in this required field.
**Fix:** Add to §4.A.4: "The `text_fidelity_reason` field is set deterministically alongside `text_fidelity`: 'Shamela structured HTML export — digital text, not OCR' for shamela_html, 'Plain text file — digital text, no structural markup' for plain_text."

### F3: `confidence_scores` Field Not Documented in SPEC
**Location:** contracts.py `SourceMetadata.confidence_scores: InferredFieldConfidence` (required)
**Problem:** The SPEC discusses confidence scoring extensively but never explicitly says how to construct the `InferredFieldConfidence` object that populates the `confidence_scores` field. The LLM returns per-field confidences (genre_confidence, science_scope_confidence, etc.) but the mapping from LLM output → InferredFieldConfidence is implicit.
**Fix:** Add explicit mapping section after the LLM output schema: "After LLM inference, construct `confidence_scores: InferredFieldConfidence` from: `genre` ← genre_confidence, `science_scope` ← science_scope_confidence, `structural_format` ← structural_format_confidence, `authority_level` ← authority_level_confidence, `level` ← level_confidence, `multi_layer` ← multi_layer_confidence, `genre_chain` ← genre_chain_confidence. Author identification confidence goes into `author.confidence` (ScholarReference), not into InferredFieldConfidence."

### F4: Death Date Regex Misses Birth-Death Range Format
**Location:** §4.A.3 extraction pseudocode, death date parsing
**Problem:** The regex `\(.*?(?:المتوفى|ت)\s*:?\s*(\d+)\s*هـ` handles "(ت 515 هـ)" and "(المتوفى: 769 هـ)" but NOT "(631 - 676 هـ)" — a birth-death range format found in real fixture 06_usul (النووي). This means النووي's death date would not be extracted.
**Fix:** Add a second regex pattern for the birth-death range:
```python
# Also try birth-death range: (NNN - NNN هـ)
if not death_match:
    range_match = re.search(r'\((\d+)\s*-\s*(\d+)\s*هـ', result['author_name_raw'])
    if range_match:
        result['author_birth_hijri'] = int(range_match.group(1))
        result['author_death_hijri'] = int(range_match.group(2))
```

### F5: Stale Reference to CSS Layer Classes in Prompt Element #4
**Location:** §4.A.4, Required prompt elements, item #4
**Problem:** Says "For Shamela sources: whether CSS layer classes (matn, sharh, hashiyah) were detected in the content." But the Shamela survey confirmed these classes DO NOT EXIST. This prompt element would always report "no classes detected" — it's useless information that wastes prompt tokens.
**Fix:** Replace with: "4. For Shamela sources: the Shamela category (القسم) from the metadata card, and whether the book is single-volume or multi-volume."

---

## Important Findings (should fix before Step 2)

### F6: Stale "info.html" References
**Location:** §1 line 16, §7 error table (SRC_FORMAT_STRUCTURE_MISSING description)
**Problem:** §1 still says "Extract metadata from format-specific structure (Shamela info.html, plain text first line)" — but info.html doesn't exist. The error code description also references "Expected structural file absent (e.g., Shamela without info.html)."
**Fix:** §1: change to "Extract metadata from format-specific structure (Shamela embedded metadata card, plain text first line)". Error table: change to "Expected structural element absent (e.g., Shamela file without PageText metadata card)".

### F7: Test Requirements Reference Deprecated Fixture
**Location:** §10, tests 1 and 12
**Problem:** Test 1 says "Verify on `html_export_minimal` and `alfiyyah_versified`" and Test 12 says "Run on multi-layer fixture (html_export_minimal)." But html_export_minimal is deprecated.
**Fix:** Test 1: change to "Verify on `shamela_real/02_nahw_muhaqiq` and `alfiyyah_versified`". Test 12: change to "Run on `shamela_real/11_multi_small` (multi-layer sharh) and `alfiyyah_versified` (single-layer matn)."

### F8: Extractor → SourceMetadata Mapping Not Documented
**Problem:** The SPEC defines the extractor output (a dict with keys like `title_full`, `author_name_raw`, etc.) and the SourceMetadata model (fields like `title_arabic`, `author: ScholarReference`, etc.) but never explicitly documents how the extractor dict maps to the SourceMetadata fields. An implementer would need to infer:
- `display_title` or `title_full` → `title_arabic`
- `author_name_raw` → construct `ScholarReference` → `author`
- `muhaqiq_name_raw` → construct `ScholarReference` → `muhaqiq`
- `shamela_category` → `format_specific_metadata` (NOT `science_scope` — that comes from LLM)
- LLM `science_scope` → `science_scope`
**Fix:** Add a mapping table after the extraction section or at the beginning of §4.A.4.

### F9: `_parse_arabic_ordinal` Function Referenced But Not Defined
**Location:** §4.A.3 extraction pseudocode
**Problem:** The extraction code calls `_parse_arabic_ordinal(result['edition_raw'])` but this function is never defined in the SPEC. The tracer.py has a similar function, but the SPEC's pseudocode should be self-contained enough for Claude Code.
**Fix:** Add inline definition or note: "Maps Arabic ordinal words to integers: الأولى→1, الثانية→2, ... العشرون→20. Falls back to extracting digits from the string."

### F10: `needs_review_fields` Construction Logic Missing
**Problem:** The contracts.py has `needs_review_fields: list[str]` as a required field on SourceMetadata, and the SPEC mentions that fields with confidence < 0.70 are added to it, but the actual construction logic (which step builds this list, from which confidence values) is not spelled out.
**Fix:** Add after confidence scoring: "Construct `needs_review_fields` by checking each field in `confidence_scores`: if the confidence value is < 0.70, add the field name to the list. Also add any fields that the extractor flagged (e.g., 'author' when no المؤلف field was found)."

---

## Minor Findings (can fix opportunistically)

### F11: Publisher List Inconsistency
The OWNER_SANITY_CHECK_ANSWERS.md says دار الكتب العلمية should score 0.55, but the SPEC text (line ~1011) says it's "intentionally excluded from the trusted list" and gets default 0.40. These need reconciliation. Recommendation: keep the SPEC's more conservative 0.40 (excluded) — the reasoning in the SPEC text is sound.

### F12: `work_relationships` Type Distinction Not Documented
SourceMetadata has `work_relationships: list[GenreChain]` (this source's genre chain relationships) while WorkRegistryEntry has `relationships: list[WorkRelationshipEdge]` (the graph edges). These are related but different things — the SPEC should note this distinction to prevent confusion.

### F13: Text Sample Extraction Logic Bug
The pseudocode for extracting the first 2000 chars of body text has an inverted skip condition. It checks `if '<PageHead>' not in page[:50] and "<span class='title'>الكتاب" not in page[:200]: continue` — this would skip body pages instead of skipping the metadata card. The condition should identify the metadata card and skip IT, not skip everything else.

### F14: `strip_tags` and `strip_diacritics` Referenced But Not Defined
Multiple pseudocode blocks reference `strip_tags()`, `strip_diacritics()`, `transliterate_chars()`, and `normalized_name_similarity()` without defining them. These are implementation details, but Claude Code needs at least a one-line spec for each.

---

## Summary

| Severity | Count | Impact |
|----------|-------|--------|
| Critical | 5 (F1-F5) | Would cause wrong implementation or runtime failures |
| Important | 5 (F6-F10) | Missing information that Claude Code would need to guess |
| Minor | 4 (F11-F14) | Quality improvements and consistency fixes |
