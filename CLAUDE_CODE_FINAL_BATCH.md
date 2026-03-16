# Claude Code Final Batch — Engine Transition Run

## Goal

Run ~50 NEW books through the source engine to produce structured input
for normalization engine development. This is the ENGINE TRANSITION batch
per the KR PRIME DIRECTIVE — the primary goal is producing normalization
engine input, secondary goal is final validation.

Budget cap: €7.00 (~50 books × €0.10/book + margin).

## Prerequisites

Read `NEXT.md`, then `CLAUDE.md` for module orientation.

Collection: `C:\Users\Rayane\Desktop\kr\shamela export samples`
Pipeline runner: `scripts/phases/run_phase_c.py`

## Step 1: Create the book selection script

Create `scripts/phases/select_final_batch.py` that:

1. **Discovers all books** in the collection directory (both directories
   and .htm files, using the same logic as `_resolve_book_path` in
   `run_phase_c.py`).

2. **Excludes already-processed books** by reading:
   - `scripts/phases/data/step4_all_books.txt` (204 Phase D books)
   - `tests/fixtures/e2e_fix_validation_books.txt` (5 e2e books)
   Strip `.htm` extension when comparing.

3. **Lightweight category extraction** for each remaining book: read the
   first 5000 bytes, extract the shamela_category from the metadata card
   using the same regex as `extractors/shamela_html.py`. Also extract
   the book title from the filename.

4. **Title-based genre heuristic**: classify each book by title keywords:
   - "شرح" or "الشرح" → likely sharh
   - "حاشية" → likely hashiyah
   - "مختصر" → likely mukhtasar
   - "نظم" or "منظومة" → likely nazm
   - "رحلة" or "الرحلة" → likely rihlah
   - "تقريرات" → likely taqrirat
   - "معجم" or "المعجم" → likely mujam
   - "سيرة" or "السيرة" → likely sirah
   - "تاريخ" or "التاريخ" or "البداية" → likely tarikh
   - "أصول الفقه" or "الأصول" → likely usul_al_fiqh
   - "أدب" or "الأدب" → likely adab
   This is heuristic — the LLM makes the actual classification.

5. **Select ~50 books** with these priorities (in order):

   **Priority 1 — Fill genre gaps (target 3+ per genre):**
   - rihlah: select 3 books with رحلة in title (need 2 more)
   - taqrirat: select 3 books with تقريرات in title (need 3)
   - sirah: select 3 books with سيرة in title (need 2 more)
   - tarikh: select 3 books with تاريخ in title (need 1 more)
   - usul_al_fiqh: select 3 books from أصول الفقه category (need 2 more)
   - mukhtasar: select 3 books with مختصر in title (need 1 more)
   - mujam: select 3 books with معجم in title (need 1 more)
   Subtotal: up to ~21 books for gap-filling.

   **Priority 2 — Multi-layer diversity (5 books):**
   - Select 5 books with حاشية in title (hashiyah implies 3-layer).
     These will likely gate_abort (Fix 2 hashiyah gate) but that's
     correct behavior — it validates the gate at scale.

   **Priority 3 — Normalization format diversity (5 books):**
   - Select 2 books with نظم or منظومة in title (verse format)
   - Select 2 books with معجم or قاموس in title (dictionary format)
   - Select 1 book from a category not yet well-represented

   **Priority 4 — Random stratified fill (~19 books):**
   - From the remaining unprocessed books, select randomly with
     stratification by shamela_category (proportional to category size).
   - Use seed 2026 for reproducibility.

   If fewer than 50 books are found after priorities 1-4, that's fine.
   Target is 45-55 books.

6. **Output:**
   - `scripts/phases/data/final_batch_books.txt` — one book name per line
   - `scripts/phases/data/FINAL_BATCH_SELECTION.md` — selection rationale
     with category/genre breakdown table

Run the script:
```bash
python scripts/phases/select_final_batch.py "C:\Users\Rayane\Desktop\kr\shamela export samples"
```

## Step 2: Run the pipeline

```bash
python scripts/phases/run_phase_c.py \
  "C:\Users\Rayane\Desktop\kr\shamela export samples" \
  --books scripts/phases/data/final_batch_books.txt \
  --output-dir tests/results/source_engine/final_batch \
  --force \
  --budget-eur 7.00
```

## Step 3: Generate summary

After the pipeline completes, the runner produces
`tests/results/source_engine/final_batch/PHASE_C_SUMMARY.json`.

Create `scripts/verify_final_batch.py` that reads the results and prints:

```
Final Batch Summary
===================
Total books: XX
Successful: XX
Gate abort: XX
Failed: XX
Total cost: €X.XX

Genre Distribution (successful books):
  [genre]: [count]
  ...

Trust Distribution:
  verified: XX
  flagged: XX

Multi-layer: XX books
Structural formats: [format]: [count], ...

Genre gap coverage:
  rihlah: [was 1, now X]
  taqrirat: [was 0, now X]
  sirah: [was 1, now X]
  tarikh: [was 2, now X]
  usul_al_fiqh: [was 1, now X]
  mukhtasar: [was 2, now X]
  mujam: [was 2, now X]
```

## Step 4: Commit

```bash
git add scripts/phases/select_final_batch.py \
        scripts/phases/data/final_batch_books.txt \
        scripts/phases/data/FINAL_BATCH_SELECTION.md \
        scripts/verify_final_batch.py \
        tests/results/source_engine/final_batch/
git commit -m "Final batch: ~50 books for engine transition

Selection: [brief stats]
Results: [copy summary]"
```

Update NEXT.md:
```
## Current position: STEP 7 — Claude Code complete, awaiting review
## What to do: Claude Chat reviews batch results
## Context: [copy summary]
## Owner action needed: No — Claude Chat reviews
```

Push to GitHub.

## What NOT to do

- Do NOT modify any engine code.
- Do NOT re-run Phase D or e2e books.
- Do NOT exceed €7.00 budget.
- Do NOT investigate individual book issues. Just report aggregate stats.
- Do NOT select books already in step4_all_books.txt or e2e validation.
