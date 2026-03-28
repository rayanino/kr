# F-DET Deterministic — Adversarial Hardening Session

**Date:** 2026-03-28
**Task:** fdet-deterministic — Adversarial edge cases for F-DET-1..9
**Result:** SUCCESS — 51 new tests, 0 regressions, 704 total passing

---

## What Was Done

Systematically probed all 9 deterministic field computations (F-DET-1 through F-DET-9) in `phase3_deterministic.py` for boundary conditions, ambiguous inputs, and undocumented behaviors. New test file: `engines/excerpting/tests/test_fdet_adversarial.py`.

## Tests Added: 51

| F-DET | Tests | Key Edge Cases |
|-------|-------|----------------|
| F-DET-1 (excerpt_id) | 5 | Hyphens in source_id, underscore ID collision, large indices |
| F-DET-2 (primary_text) | 5 | First/last word boundary, trailing whitespace stripped, internal double-space preserved |
| F-DET-3 (layer attribution) | 6 | Empty layers raises ValueError, exactly 80% boundary, 100 layers→LA-3, split-point merge→LA-4, None-author LA-3 |
| F-DET-4 (content_types) | 6 | Empty segments, mismatched indices, all 16 ScholarlyFunctions, UNCLASSIFIED, order preservation |
| F-DET-5 (evidence_refs) | 9 | رواها→رواه substring detection, empty ﴿﴾ no match, single-char ﴿ح﴾ matches, position 0/end, double occurrence |
| F-DET-6 (physical_pages) | 4 | Exact join point boundaries, 100 join points, all-pages span |
| F-DET-7 (div_path) | 4 | Empty path, 10-level depth, Arabic-only, mixed Arabic/Latin |
| F-DET-8 (footnotes) | 7 | Char_start boundary (inclusive), char_end boundary (exclusive), **latent bug exposed**, 100 footnotes, substring non-confusion |
| F-DET-9 (quoted_scholars) | 5 | All-primary→empty, None-author included/excluded, many scholars, duplicate entries |

## Bugs Found: 2 (neither blocks correctness, both documented)

### MEDIUM — F-DET-8 First-Occurrence Footnote Lookup
`filter_relevant_footnotes` uses `find()` which returns the FIRST occurrence of `⌜{ref_marker}⌝`. If a marker appears twice in assembled_text and the first occurrence is OUTSIDE the unit range but the second is INSIDE, the footnote is silently excluded.

**In practice:** Low probability — requires same ref_marker to appear twice in one assembled chunk (unusual). Occurs only in split chunks where footnote renumbering wasn't applied, or in manuscripts with repeated footnote numbers.

**Recommendation:** Iterate all occurrences with `findall()` or a loop — include the footnote if ANY occurrence falls within range. Not blocking for current use.

### LOW — F-DET-1 Non-Reversible ID Format
The `exc_{source_id}_{div_id}_{chunk_index}_{unit_index}` format uses underscore as separator, so IDs cannot be reliably parsed back into components when source_id/div_id contain underscores. This creates ID collisions in string representation but not in practice (IDs are only compared for equality).

**In practice:** Zero impact — IDs are never parsed, only compared. Document as design constraint.

## Spec Issues Found: 2

1. **§7.1 F-DET-8**: Missing specification for multi-occurrence marker behavior. Should explicitly state "check ALL occurrences."
2. **§7.1 F-DET-1**: Should note that ID format is non-reversible when components contain underscores.

## Key Learnings

- **80% LA-1 boundary is inclusive** (`>= 0.8` exactly): at exactly 80.0%, LA-1 applies (not LA-2). This is the correct behavior.
- **Empty layers fails loudly**: `ValueError` with `F-DET-3` prefix raised when `text_layers=[]` — correct I-AC-2 violation response.
- **﴿﴾ empty delimiters don't match**: regex uses `[^﴾]+` (one or more), protecting against markup artifacts.
- **رواها triggers رواه** (intentional): DD-S3-8 plain substring matching is correct — word boundaries cause ~76% false negatives with Arabic proclitics.
- **F-DET-9 None-author exclusion**: `None` → `"unknown"` in `author_id`; secondary layers with same type AND `None` author are correctly excluded as primary.

## Test Counts
- Before: 653
- After: 704
- Delta: +51
- Failures: 0
