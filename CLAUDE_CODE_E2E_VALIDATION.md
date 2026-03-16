# Claude Code E2E Validation — Fix Verification

## Goal

Run 5 specific books through the fixed source engine pipeline and verify
each of the 4 mandatory fixes produces the expected behavioral change.
Budget cap: €2.00.

## Prerequisites

Read `NEXT.md`, then `CLAUDE.md` for module orientation.

The pipeline runner is `scripts/phases/run_phase_c.py`. The Shamela
collection is at `C:\Users\Rayane\Desktop\kr\shamela export samples`.

## Step 1: Create the book list

Create `tests/fixtures/e2e_fix_validation_books.txt`:

```
ملء العيبة بما جمع بطول الغيبة - ج ٥
النكت على شرح النووي على صحيح مسلم
أساليب بلاغية
صحيح البخاري - ن عطاءات العلم
إعلام الموقعين عن رب العالمين - ط العلمية
```

## Step 2: Run the pipeline

```bash
python scripts/phases/run_phase_c.py \
  "C:\Users\Rayane\Desktop\kr\shamela export samples" \
  --books tests/fixtures/e2e_fix_validation_books.txt \
  --output-dir tests/results/source_engine/e2e_validation \
  --force \
  --budget-eur 2.00
```

Use `--force` to re-process even if results exist.
Use the e2e_validation output directory (NOT phase_c or phase_d).

## Step 3: Create and run the verification script

Create `scripts/verify_e2e_fixes.py` that checks the following assertions
against the output in `tests/results/source_engine/e2e_validation/`:

### Book 1: ملء العيبة بما جمع بطول الغيبة - ج ٥ (Fix 1: rihlah genre)

**Phase D result:** genre=other, status=success
**Expected after fix:** genre=rihlah (LLM prompt now includes rihlah;
title contains رحلة pattern "ملء العيبة" which is a famous rihlah text)
**Assertion:** result.json → genre == "rihlah"
**If genre is still "other":** This means the LLM didn't classify it as
rihlah even with the updated prompt. This is an LLM behavior issue, not a
code bug. Mark as NEEDS_REVIEW rather than FAIL.

### Book 2: النكت على شرح النووي على صحيح مسلم (Fix 2: hashiyah gate)

**Phase D result:** genre=hashiyah, is_multi_layer=False, text_layers=[],
status=success
**Phase D LLM data:** Opus said genre=other, CA said genre=hashiyah.
Consensus picked hashiyah. LLM non-determinism means re-run may differ.
**Expected after fix:** IF consensus still picks hashiyah → status=gate_abort
(check 5 consistency_hashiyah_no_layers fires with severity="gate").
**Assertions (3-way):**
- IF result.json → genre == "hashiyah" AND status == "gate_abort":
  → PASS (fix working correctly)
- IF result.json → genre == "hashiyah" AND status == "success":
  → FAIL (fix is broken — hashiyah+no-layers should gate)
- IF result.json → genre != "hashiyah":
  → NEEDS_REVIEW (LLM changed classification; fix didn't apply because
  the precondition wasn't met. Print the actual genre.)

When PASS, also verify:
- result.json → error_code == "SRC_LOW_CONFIDENCE"
- result.json → gate_errors contains string "hashiyah"

### Book 3: أساليب بلاغية (Fix 3: death date warning)

**Phase D result:** needs_review_fields=[], status=success
**Phase D LLM data:** Opus death_date=1441, CA death_date=None,
extraction death_date=None → ERR-03 pattern
**Expected after fix:** "death_date_hijri" appears in needs_review_fields
**Assertions:**
- result.json → status == "success" (not gate_abort — this is a warning)
- result.json → needs_review_fields contains "death_date_hijri"

**If needs_review_fields does NOT contain death_date_hijri:** Check
consensus.json to verify one model still returns a death date and the
other doesn't. If the LLM behavior changed (both now agree), the ERR-03
pattern no longer applies and the fix correctly doesn't fire.

### Book 4: صحيح البخاري - ن عطاءات العلم (Control)

**Phase D result:** genre=hadith_collection, status=success
**Expected:** Identical outcome — no fix should change this book's behavior.
**Assertions:**
- result.json → status == "success"
- result.json → genre == "hadith_collection"

### Book 5: إعلام الموقعين عن رب العالمين - ط العلمية (Fix 1: usul_al_fiqh)

**Phase D result:** genre=other, status=success
**Expected after fix:** genre=usul_al_fiqh (LLM prompt now includes it;
this is Ibn Qayyim's famous usul_al_fiqh work)
**Assertion:** result.json → genre == "usul_al_fiqh"
**If genre is still "other":** Same as Book 1 — LLM behavior issue, not
code bug. Mark NEEDS_REVIEW.

### Verification script output format

The script should print a summary table:

```
E2E Fix Validation Results
==========================
Book 1 (Fix 1 rihlah):     PASS / FAIL / NEEDS_REVIEW
Book 2 (Fix 2 hashiyah):   PASS / FAIL
Book 3 (Fix 3 death_date): PASS / FAIL / NEEDS_REVIEW
Book 4 (Control):           PASS / FAIL
Book 5 (Fix 1 usul_fiqh):  PASS / FAIL / NEEDS_REVIEW

Total cost: €X.XX
All fixes verified: YES / NO
```

For any FAIL or NEEDS_REVIEW, print the actual vs expected values.

## Step 4: Commit results

```bash
git add tests/results/source_engine/e2e_validation/ \
        tests/fixtures/e2e_fix_validation_books.txt \
        scripts/verify_e2e_fixes.py
git commit -m "E2E fix validation: 5 books through fixed pipeline

Results: [copy the summary table here]"
```

Update NEXT.md:
```
## Current position: STEP 5 — Claude Code complete, awaiting verification
## What to do: Claude Chat verifies e2e results
## Context: [copy summary table]
## Owner action needed: No — Claude Chat reviews
```

Push to GitHub.

## What NOT to do

- Do NOT modify any engine code. This is a read-only validation run.
- Do NOT re-run Phase C or Phase D books. Only the 5 listed books.
- Do NOT exceed the €2.00 budget. If 4 books hit the budget, skip the 5th.
- Do NOT investigate or fix any issues found. Just report them.
