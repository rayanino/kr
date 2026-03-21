# Sweep Bug Triage

**Date:** 2026-03-21
**Source:** Normalization corpus sweep (7,475 books) + Source engine deterministic sweep (7,475 items)

## Source Engine

**Zero bugs found.** 100% success rate on 7,475 items. No triage needed.

## Normalization Engine

| # | Engine | Crash Pattern | Error Type | Books Affected | Classification | Rationale |
|---|--------|---------------|------------|----------------|----------------|-----------|
| 1 | Normalization | All pages classified as metadata in books without `(ص: N)` page numbers | Silent failure (status=OK, 0 content units) | 48 | FIX NOW | Root cause clear: `_pass1_parse()` metadata detection requires at least one numbered page. Fix is ~8 lines in 1 file. Test uses existing fixtures. |
| 2 | Normalization | `NORM_DIACRITICS_ENTITY_CORRUPTION` — regex found 20 diacritics, BS4 found 19 in first 500 chars | NormalizationError (CRASH) | 1 | FIX NOW | Root cause clear: `_ARABIC_DIACRITICS` uses 20 codepoints (broader than SPEC's 10). Regex/BS4 disagree on extended diacritics not in SPEC range. Fix is 3 lines in 1 file. |

## Summary

- **FIX NOW:** 2 bugs (49 books total)
- **ARCHITECT REVIEW:** 0
- **DEFER:** 0
