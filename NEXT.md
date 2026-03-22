# NEXT — Format Diversity Experiment (Pre-SPEC Validation)

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (5 engines, 3 remaining)
- Architecture C experiment: ✅ 10 prose divisions tested, LLM teaching-unit extraction validated
- **Gap:** All 10 tested divisions were prose, ≤1040 words. Non-prose formats and longer divisions are untested.
- This experiment fills the gap BEFORE the excerpting engine SPEC is written.

## What to Do

Run the **same LLM teaching-unit extraction** from the Architecture C experiment on **verse-commentary and longer prose divisions**. The goal is to answer: (1) does the LLM handle verse-commentary text? (2) does quality hold on 2000-4000w divisions?

You produce 4 deliverables:
1. Normalized packages for new fixtures
2. Extracted divisions (10-14 total)
3. LLM test results (Approach A and B for each division)
4. Evaluation workbook (full Arabic text + results for architect review)

## Context

- The architect evaluated the Architecture C experiment and found 4 gaps (see `reference/archive/sessions/architecture_decision_handoff.md`)
- This experiment targets Gap 1 (non-prose formats) and Gap 2 (longer divisions)
- Use the SAME LLM prompts, schemas, and model from `experiments/architecture_test/run_tests.py`
- Full experiment design: `experiments/format_diversity_test/EXPERIMENT_DESIGN.md`
- API routing: ALL calls through OpenRouter. Model: anthropic/claude-opus-4.6

## Read First

1. `experiments/format_diversity_test/EXPERIMENT_DESIGN.md` — what to test and why
2. `experiments/architecture_test/produce_packages.py` — how packages were built (ADAPT)
3. `experiments/architecture_test/extract_divisions.py` — division extraction logic (ADAPT)
4. `experiments/architecture_test/run_tests.py` — LLM test runner (REUSE)
5. `experiments/architecture_test/generate_workbook.py` — workbook generation (ADAPT)
6. `engines/normalization/tests/conftest.py` — `_make_source_metadata()` factory
7. `engines/normalization/src/normalizers/shamela.py` lines 93-95 — double-quote heading detection (important context for understanding fixture structure)

## Fixtures Already in the Repo

The architect has already extracted and placed these:

### Primary: شرح ابن عقيل على ألفية ابن مالك (verse-commentary)
- Location: `experiments/format_diversity_test/fixtures/ibn_aqil/001.htm` through `004.htm`
- 4 volumes. Vol 001: 392 pages, 13 chapter headings. Vol 003: 329 pages, 27 chapter headings.
- **Structure:** Content headings use `class="title"` (double quotes). The normalization engine's shamela parser explicitly handles this — see line 93 of `engines/normalization/src/normalizers/shamela.py`.
- **Content:** Classical verse-commentary — Ibn Aqil's sharh on Ibn Malik's Alfiyyah. Each chapter heading corresponds to a nahw topic (المعرب والمبني, النكرة والمعرفة, etc.). Within each division, the text interleaves quoted ألفية verses with prose commentary.
- **Process vol 001 and vol 003.** These give us the most headings → most divisions to select from.
- **For normalization:** `is_multi_layer=True` — this is a 2-layer text (matn verse + sharh prose).

### Secondary: تيسير العلام شرح عمدة الأحكام (longer prose divisions)
- Location: `experiments/format_diversity_test/fixtures/taysir_al_ilam/book.htm`
- 742 pages, 139 chapter headings — very well structured.
- **Structure:** Same double-quote heading pattern.
- **Content:** Fiqh sharh with hadith evidence chains. Many divisions in the 2000-3500 word range (from the Shamela division analysis: 24 divisions in the 2000-3500w bucket, median 1101w).
- **For normalization:** `is_multi_layer=False`.

### Optional: Extended fixtures (already in repo at `tests/fixtures/shamela_extended/`)
- ext_39 (تلخيص أحكام الجنائز) — masala format, 91 pages
- ext_46 (الاقتراح في أصول النحو) — QA format, 406 pages
- **WARNING:** These files have NO content headings — only single-quote PartName page headers. The normalization engine will likely produce very few divisions. Attempt normalization, but if fewer than 5 leaf divisions result, skip the fixture and note it in the extraction report. **Do NOT spend time debugging normalization for these — they are secondary targets.**

## What to Build

### Deliverable 1: Normalize Fixtures

Adapt `experiments/architecture_test/produce_packages.py`. Write packages to `experiments/format_diversity_test/packages/{fixture_name}/`.

Fixtures to normalize (in order of priority):

| Fixture name | Source .htm | is_multi_layer | Priority |
|---|---|---|---|
| `ibn_aqil_v1` | `experiments/format_diversity_test/fixtures/ibn_aqil/001.htm` | True | PRIMARY |
| `ibn_aqil_v3` | `experiments/format_diversity_test/fixtures/ibn_aqil/003.htm` | True | PRIMARY |
| `taysir` | `experiments/format_diversity_test/fixtures/taysir_al_ilam/book.htm` | False | PRIMARY |
| `ext_39_masala` | `tests/fixtures/shamela_extended/ext_39/book.htm` | False | OPTIONAL |
| `ext_46_qa` | `tests/fixtures/shamela_extended/ext_46/book.htm` | False | OPTIONAL |

For each, print: fixture name, content units count, leaf division count, median division word count.

**If normalization fails** on any PRIMARY fixture: stop and report. This blocks the experiment.
**If normalization fails** on any OPTIONAL fixture: log the error, skip it, continue.

### Deliverable 2: Extract Divisions

Adapt `experiments/architecture_test/extract_divisions.py`. Write to `experiments/format_diversity_test/divisions/{fixture_name}/{div_index}.json`.

**Division selection:**

| Fixture | Target count | Word range | Special criteria |
|---|---|---|---|
| ibn_aqil_v1 | 2-3 | 300-2000w | MUST contain verse-commentary interleaving: look for short lines (≤20 Arabic words) surrounded by longer prose paragraphs, OR lines starting with verse quotation markers (قال ابن مالك, ومنه قوله, or numbered verse text). If alignment filter (L-003) rejects too many, relax to first-30-in-first-200. |
| ibn_aqil_v3 | 2-3 | 300-2000w | Same as v1 |
| taysir | 3-4 | 2000-4000w | Standard prose. Apply L-003 strict alignment. Select from different kitab sections for genre diversity. |
| ext_39_masala | 1-2 (if available) | 300-2000w | Must contain ≥2 مسألة markers in assembled text |
| ext_46_qa | 1-2 (if available) | 300-2000w | Must contain ≥2 QA markers (سؤال/فأجاب/سُئل) |

**Total target: 10-14 divisions.** Minimum viable: 8 (if OPTIONAL fixtures fail).

**For each extracted division, also extract:**
- context_before: last 200 words of previous division
- context_after: first 200 words of next division
- boundary_continuity data from the last content unit
- All fields from the original extract_divisions.py schema

Write `experiments/format_diversity_test/EXTRACTION_REPORT.md`:
- Per-fixture: normalization stats, total leaf divisions, divisions in range, selected divisions with rationale
- For ibn_aqil: note which divisions contain visible verse content vs. pure prose commentary
- Any issues encountered

### Deliverable 3: Run LLM Tests

Reuse `experiments/architecture_test/run_tests.py` logic. Run **Approach A and B only** (no Approach C).

For each extracted division:
- Approach A: single-call joint extraction
- Approach B: two-call classify-then-group
- Model: anthropic/claude-opus-4.6 via OpenRouter
- Temperature: 0

Save to `experiments/format_diversity_test/results/{fixture_name}/{div_index}_{approach}.json`

Write `experiments/format_diversity_test/results/RUN_SUMMARY.md` (same format as original).

### Deliverable 4: Evaluation Workbook

Adapt `experiments/architecture_test/generate_workbook.py`. Write to `experiments/format_diversity_test/EVALUATION_WORKBOOK.md`.

For each division:
- Full Arabic text (the architect reads this — do not truncate)
- Approach A results table (unit #, word range, function, self-contained, snippet)
- Approach B results table (same)
- Per-unit Arabic descriptions from both approaches

## Design Decisions (already made)

1. **Approach A and B only.** No Approach C (cross-boundary). Not testing D-011 here.
2. **Same prompts.** Exact same system prompts and Pydantic schemas from `run_tests.py`. Do NOT modify.
3. **Same model.** anthropic/claude-opus-4.6 via OpenRouter. Temperature 0.
4. **Qualitative evaluation.** No gold references, no F1 metric. The architect reads Arabic and judges.
5. **Ibn aqil is multi-layer.** Set `is_multi_layer=True` when calling `_make_source_metadata()`.
6. **L-003 relaxation allowed for ibn_aqil.** If strict heading alignment (first 15 stripped chars in first 100 stripped chars) rejects >80% of leaf divisions, relax to moderate (first 30 in first 200). Note in extraction report.
7. **OPTIONAL fixtures are expendable.** If ext_39/46 normalization produces <5 leaf divisions, skip. The experiment is not blocked.

## Do NOT Do

- Do NOT modify the normalization engine code.
- Do NOT modify any files in `experiments/architecture_test/`.
- Do NOT create gold reference files.
- Do NOT run Approach C (cross-boundary context).
- Do NOT modify the LLM prompts or schemas.
- Do NOT use any API other than OpenRouter.
- Do NOT normalize ext_49 (pure verse — heading-sparse, will produce unusable normalization output. Pure verse testing is deferred to engine evaluation).
- Do NOT spend more than 5 minutes debugging normalization failures on OPTIONAL fixtures. Skip and move on.

## Verification

Before declaring done:
1. ≥3 PRIMARY fixtures normalized successfully with >5 leaf divisions each
2. 10-14 divisions extracted (minimum 8 from PRIMARY fixtures)
3. Ibn aqil divisions contain visible verse-commentary content (check for short verse lines in the text)
4. Taysir divisions are in the 2000-4000w range
5. LLM tests run on every extracted division (both A and B), zero errors
6. Evaluation workbook contains full Arabic text for every division — not truncated
7. RUN_SUMMARY.md has zero errors
8. EXTRACTION_REPORT.md documents all decisions

## After This

The architect evaluates the workbook in a fresh session. Based on results:
- If verse-commentary passes → begin excerpting engine SPEC
- If verse-commentary fails → design Phase 1 verse restructuring before SPEC
- If longer divisions degrade → adjust Phase 1 splitting threshold in SPEC
