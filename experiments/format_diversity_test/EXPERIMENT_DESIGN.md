# Format Diversity Experiment — Pre-SPEC Validation

**Date:** 2026-03-22
**Purpose:** Validate that the LLM teaching-unit extraction (Phase 2 of excerpting) works on non-prose formats and longer divisions, before writing the excerpting engine SPEC.
**Duration:** 1 CC session (normalize + extract + run LLM) + 1 architect session (evaluate)
**Estimated cost:** ~€3-5 (same model, similar division count)
**Prerequisite:** Owner makes `shamela-export-samples/` directory available in the repo root

---

## Why This Experiment Exists

The Architecture C experiment (commit fced538) validated that an LLM can identify teaching units from division-level text — but all 10 tested divisions were prose, all ≤1040 words. The excerpting engine SPEC's internal architecture depends on two unvalidated assumptions:

1. **Format assumption:** The same LLM prompt works for verse-commentary, Q&A, and masala-block formats. If it doesn't, Phase 1 of the excerpting engine MUST restructure non-prose text before Phase 2 sees it — this is a load-bearing architectural constraint.

2. **Length assumption:** LLM quality holds on 2000-4000 word divisions. If it degrades, the Phase 1 splitting threshold must be set lower — more divisions get split before Phase 2.

These two questions are answered cheaply now (1-2 sessions, ~€3) or expensively later (rebuild affected modules if the evaluation reveals problems after weeks of build work).

---

## What This Experiment Decides

### Q1: Can Phase 2 handle verse-commentary text?

**Pass:** LLM identifies coherent teaching units (verse group + commentary = 1 unit) in ≥3/4 verse-commentary divisions.
**Fail:** LLM treats verse lines and commentary as unrelated segments, or produces incoherent groupings.
**If pass:** Phase 1 verse-commentary preprocessing is a quality optimization, not mandatory. SPEC designs it as "nice to have."
**If fail:** Phase 1 verse-commentary preprocessing is mandatory. SPEC must define restructuring before Phase 2 runs.

### Q2: Does Phase 2 quality degrade on longer divisions?

**Pass:** Teaching unit identification on 2000-4000w divisions is comparable quality to 500-1000w.
**Fail:** Boundary quality visibly degrades (missed obvious boundaries, merged unrelated topics).
**If pass:** Phase 1 splitting threshold stays at 5000w.
**If fail:** Phase 1 splitting threshold drops to 2000w. More divisions get split.

### Q3 (secondary): QA/masala format confirmation

**Expected pass.** These formats have explicit markers. Running 2-3 divisions provides cheap confirmation and prevents embarrassment if the assumption is wrong.

---

## Fixture Selection

### Verse-commentary (PRIMARY TARGET — 3-4 divisions)

**Source:** شرح ابن عقيل على الألفية from `shamela-export-samples/`

This is THE canonical verse-commentary text: Ibn Aqil's sharh on Ibn Malik's Alfiyyah. Every page interleaves quoted verse (matn) with prose commentary (sharh). This is the hardest non-prose format because:
- Verse lines are quoted (sometimes with قوله:, sometimes not)
- Commentary prose follows each verse or verse group
- The teaching unit is verse+commentary together
- Poetry citations WITHIN commentary (as evidence) must not be confused with the matn

**Division selection criteria:**
- Leaf divisions in the 300-2000 word range
- Prefer divisions with visible verse-commentary interleaving (not pure prose introductions)
- Avoid first/last divisions (introductory/closing material)

**Backup:** If شرح ابن عقيل cannot be located, use:
- فتح الأقفال وحل الإشكال بشرح لامية الأفعال (exists in 20K collection, 37 divisions in range)
- الكوكب المنير في شرح الألفية بالتشطير (98 divs, 31 in range)

### Pure verse (1-2 divisions)

**Source:** ext_49 (لامية الأفعال — 114 بيت by Ibn Malik), already in repo at `tests/fixtures/shamela_extended/ext_49/book.htm`

Tests whether the LLM can identify verse-only teaching units (groups of related verses). Simpler than verse-commentary — if this fails, verse-commentary certainly fails.

### QA/masala format (2-3 divisions)

**Source options (already in repo):**
- ext_39 (تلخيص أحكام الجنائز — 29 مسألة markers, 91 pages)
- ext_46 (الاقتراح في أصول النحو — 46 QA markers, 406 pages)

**Division selection:** Prefer divisions containing ≥2 QA pairs or ≥2 مسألة blocks.

### Longer prose divisions (3-4 divisions, 2000-4000w)

**Source:** Identifiable books from `shamela-export-samples/` with well-structured headings and divisions in the 2000-4000w range.

Best candidates from the division analysis:
- تيسير العلام شرح عمدة الأحكام (136 headings, 25 mid-range divs, fiqh/hadith)
- كفاية الأخيار في حل غاية الاختصار (157 headings, 24 mid-range, fiqh)
- السياسة الشرعية (158 headings, 29 mid-range, siyasah)

CC should search `shamela-export-samples/` for these by filename pattern.

**Fallback:** If specific books aren't found, use any well-structured fiqh book with 2000-4000w divisions and ≥30 headings.

---

## Experiment Procedure

### Phase 1: Normalize and Extract (CC)

1. **Locate fixtures.** Search `shamela-export-samples/` for:
   - شرح ابن عقيل (filename likely contains `عقيل` or `ابن عقيل`)
   - One of the longer-division candidates listed above
   - (ext_49 and ext_39/ext_46 are already in repo)

2. **Copy to experiment directory.** Copy found .htm files to `experiments/format_diversity_test/fixtures/`

3. **Normalize.** For each fixture, run `normalize_source()` from `engines/normalization/src/dispatcher.py`. Write packages to `experiments/format_diversity_test/packages/{fixture_name}/`

4. **Extract divisions.** Adapt `experiments/architecture_test/extract_divisions.py` to:
   - Work with the new packages directory
   - For verse-commentary: select divisions with visible verse markers (check for `●` or بيت-like patterns in assembled text)
   - For QA/masala: select divisions containing QA/masala markers
   - For longer prose: select divisions in 2000-4000w range
   - Write to `experiments/format_diversity_test/divisions/`

5. **Target: 10-14 divisions total:**
   - 3-4 verse-commentary (from شرح ابن عقيل)
   - 1-2 pure verse (from ext_49)
   - 2-3 QA/masala (from ext_39 or ext_46)
   - 3-4 longer prose (from candidate books, 2000-4000w)

### Phase 2: Run LLM Tests (CC)

Use the SAME prompts and schemas from `experiments/architecture_test/run_tests.py`:
- Approach A (single-call joint extraction)
- Approach B (two-call classify-then-group)
- No Approach C (cross-boundary context) — not testing D-011 here

**Model:** anthropic/claude-opus-4.6 via OpenRouter
**Temperature:** 0

Save results to `experiments/format_diversity_test/results/{fixture_name}/{div}_{approach}.json`

### Phase 3: Build Evaluation Workbook (CC)

Same format as `experiments/architecture_test/EVALUATION_WORKBOOK.md`:
- Full Arabic text for each division
- Approach A and B results tables
- Per-unit descriptions in Arabic

Write to `experiments/format_diversity_test/EVALUATION_WORKBOOK.md`

### Phase 4: Evaluate (Architect — separate session)

The architect reads each division's Arabic text and judges:
1. **Verse-commentary:** Does the LLM correctly identify verse+commentary as a single teaching unit? Or does it treat verse lines as separate from commentary?
2. **Pure verse:** Does the LLM group related verses into topical units?
3. **QA/masala:** Does the LLM respect Q&A pair boundaries?
4. **Longer divisions:** Is boundary quality comparable to 500-1000w divisions?

No formal F1 metric (no gold references). This is a qualitative viability check, same as the architecture experiment. The architect reads Arabic text and makes a judgment.

---

## Success Criteria

| Format | Pass | Fail |
|--------|------|------|
| Verse-commentary | ≥3/4 divisions have coherent verse+commentary grouping | LLM fragments verse-commentary pairs |
| Pure verse | Verse lines grouped into topical units | Verse lines treated as individual units or random grouping |
| QA/masala | QA pair / masala boundaries respected | QA pairs split or merged incorrectly |
| Longer prose | Quality comparable to 500-1000w | Visible degradation (missed boundaries, merged topics) |

---

## Risk Mitigation

**Risk: Normalization fails on new fixtures.**
Mitigation: 50/50 extended fixtures passed normalization (S6). If a specific fixture fails, CC logs the error and selects an alternative. The experiment is not blocked by one fixture.

**Risk: شرح ابن عقيل not found in shamela-export-samples.**
Mitigation: Backup verse-commentary candidates identified (see above). CC searches by filename patterns.

**Risk: Extended fixtures (ext_49, ext_39, ext_46) have different HTML structure (no Heading1/2 classes).**
Mitigation: These are already in the repo and passed normalization in S6. If they produce packages with very few divisions, we extract text at the PageText level and use the full page text as a "division."

**Risk: Same-model evaluation bias (Gap 3).**
Mitigation: Not addressed by this experiment. The owner will spot-check 5+ divisions during the architect evaluation session (gap 3 mitigation from the original plan).
