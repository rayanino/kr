# NEXT — Source Engine Step 1 Final Hardening

**Session type:** SPEC hardening (final pass before Step 2)
**Goal:** Close 4 identified blind spots from quality review. Bounded checklist — not open-ended.

---

## Context

Step 1 has been through three review passes:
1. **Integrity audit** (kr-integrity): found 11 defects, 8 fixed
2. **Shamela survey** (2,519 real exports): revealed all extraction rules were wrong, complete rewrite
3. **Deep quality review** (8-dimension analysis): found 14 more defects, 10 fixed

Each pass found critical problems the previous pass missed. Four specific blind spots remain unexamined.

---

## The 4 Blind Spots to Close

### 1. Cross-Boundary Contract Verification (source → normalization)
Read `engines/normalization/contracts.py` field by field. For every field the normalization engine's input expects, verify:
- The source engine's output contract (SourceMetadata) provides it
- The SPEC has a rule that populates it
- The types match exactly (not just "close enough")

### 2. contracts.py Sync Audit
The SPEC has been rewritten 3 times since contracts.py was last updated. Check:
- Does the SPEC describe any data structures that contracts.py doesn't have models for?
- Are there enum values the SPEC uses that aren't in the contract enums?
- Do the publisher scoring structure and name variants need a new model?
- Does the extractor output dict need a contract model, or is it intentionally untyped?

### 3. Edge Case Testing on Real Fixtures
Run the extraction logic (as defined in SPEC pseudocode) against specific edge cases in the 12 real fixtures:
- Multi-volume book where المقدمة.htm sorts before 001.htm alphabetically
- Book with zero body pages (if any exist in fixtures)
- Books where المؤلف field uses إعداد alternative
- Books where multiple muhaqiq-equivalent fields appear in the same card

### 4. Enrichment Invariants After Workflow Reorder
The workflow was reordered (hash moved to Step 5, freeze to Step 6). Verify:
- The 9 enrichment invariants still reference correct steps
- The staging lock timing still makes sense
- Registry locking still covers the right steps

---

## What to read first

1. `NEXT.md` (this file)
2. `engines/source/SPEC_CORE.md` — The core SPEC (~1120 lines)
3. `engines/source/STEP1_QUALITY_REVIEW.md` — Previous review findings
4. `engines/source/contracts.py` — Source engine Pydantic models (825 lines)
5. `engines/normalization/contracts.py` — Normalization engine input contract
6. `reference/SHAMELA_FORMAT_ANALYSIS.md` — Real Shamela format spec
7. `tests/fixtures/shamela_real/` — 12 real test fixtures

## Done when

- [ ] Cross-boundary: every normalization input field traced to a source output rule
- [ ] contracts.py: no mismatches between SPEC and models
- [ ] Edge cases: extraction pseudocode handles all 12 fixtures without errors
- [ ] Enrichment: invariants verified consistent with reordered workflow
- [ ] Any defects found are fixed in SPEC_CORE.md and documented

After this pass: Step 1 is locked. Move to Step 2 (RESEARCH).
