# Architecture C Empirical Validation — Experiment Design

**Date:** 2026-03-22
**Purpose:** Validate that Architecture C (merge atomization+excerpting, keep passaging, soften D-011) is viable before committing to it.
**Duration:** 2 sessions (CC: produce packages + run tests | Architect: evaluate results in fresh chat)

---

## What This Experiment Decides

Three binary questions, each with clear pass/fail criteria:

**Q1: Can an LLM identify teaching units from normalized division text?**
Pass: Boundary F1 ≥ 0.70 averaged across 8-10 test divisions.
Fail: Boundary F1 < 0.70 → Architecture C is not viable; revert to Architecture B (7 engines).

**Q2: Is two-phase LLM (classify then group) better than single-phase (joint)?**
Result: If two-phase classification accuracy exceeds single-phase by >10 percentage points → use two-phase internally (C-1). Otherwise → use single-phase (C-2, simpler).

**Q3: Does cross-boundary context improve split argument detection?**
Result: If providing adjacent-division context catches ≥1 argument split that within-division processing missed → soft D-011 is empirically validated. Otherwise → D-011 relaxation provides no measured benefit (keep it hard or defer the question).

---

## Book Selection (5 books, 2 divisions each = 10 test divisions)

| # | Fixture | Title | Science | Pages | Why selected |
|---|---------|-------|---------|-------|--------------|
| 1 | 03_fiqh | أحكام الاضطباع والرمل في الطواف | Fiqh | 102 | Scholarly positions with evidence chains, مسائل structure, 12 mid_argument BC signals. Primary D-011 test source. |
| 2 | 07_balagha | أساليب بلاغية (أحمد مطلوب) | Balagha | 288 | Definitions + scholarly positions on rhetoric. 57 in-range divisions. Diverse scholarly functions. |
| 3 | 06_usul | آداب الفتوى والمفتي والمستفتي (النووي) | Usul | 74 | Definition-heavy with rules. Classical author. Tests definition identification + rule extraction. |
| 4 | 02_nahw_muhaqiq | أبنية الأسماء والأفعال والمصادر | Nahw (muhaqiq) | 295 | **Only confirmed multi-layer fixture** (2 layers: sharh + matn). Tests layer attribution. |
| 5 | 10_no_author | البدر التمام بما صح من أدلة الأحكام | Fiqh+Hadith | 140 | Mixed evidence chains with scholarly positions + hadith citations. Tests combined classification. |

**Empirically verified fixture suitability (tool-executed):**
- 03_fiqh: 22 leaf divs, 13 in 300-2000w range, 12 mid_argument BC signals
- 07_balagha: 99 leaf divs, 57 in range, 1 mid_argument
- 06_usul: 9 leaf divs, 5 in range, 0 mid_argument
- 02_nahw_muhaqiq: 21 leaf divs, 2 layers (sharh+matn), needs word count check with multi-layer
- 10_no_author: 77 leaf divs, 24 in range, 0 mid_argument

**Division selection criteria (CC selects, architect verifies):**
- Leaf divisions between 300 and 2000 Arabic words after assembly
- Prefer divisions with diverse scholarly content (not pure narrative)
- For Book 4 (commentary): select a division with visible matn/sharh transitions
- For the D-011 test: select at least 3 divisions where the last sentence appears to continue into the next division (CC checks boundary_continuity signals)

---

## Phase 1: CC Produces Normalized Packages + Division Extractions

CC produces:

### 1a. Normalized packages
For each of the 5 fixtures, run `normalize_source()` and write the package to:
`experiments/architecture_test/packages/{fixture_name}/manifest.json`
`experiments/architecture_test/packages/{fixture_name}/content.jsonl`

### 1b. Division extraction script
CC writes `experiments/architecture_test/extract_divisions.py` that:

1. For each normalized package, reads manifest.json (division tree) and content.jsonl
2. Walks the division tree to find leaf divisions
3. For each leaf division, assembles cross-page text from constituent content units:
   - Join content units in order by `unit_index`
   - Use `boundary_continuity.type` to determine join behavior:
     - `mid_sentence` or `mid_word`: join with no separator
     - `mid_paragraph`: join with single newline
     - `section_break` or `division_break`: join with double newline
     - `unknown` or absent: join with single newline (conservative)
   - Compute Arabic word count (whitespace split, filter to Arabic-containing tokens)
4. Filters to divisions in the 300-2000 word range
5. Selects 2 divisions per book (prefer content diversity; avoid first/last divisions which are often introductory/closing)
6. For each selected division, also extracts:
   - The last 200 words of the PREVIOUS division (for D-011 test)
   - The first 200 words of the NEXT division (for D-011 test)
   - `boundary_continuity` data on the last content unit of the division
   - Division heading text and path
   - Text layer information (for multi-layer book)
   - Content flags aggregated across constituent units

Output per division: `experiments/architecture_test/divisions/{fixture_name}/{div_index}.json`
```json
{
  "fixture_name": "03_fiqh",
  "div_index": 5,
  "heading_text": "المبحث الثاني: حكم الاضطباع",
  "heading_path": ["كتاب الحج", "الباب الأول", "المبحث الثاني"],
  "assembled_text": "...",
  "arabic_word_count": 847,
  "content_unit_indices": [15, 16, 17, 18],
  "text_layers": [...],
  "content_flags": {"has_hadith": true, "has_quran": false, ...},
  "boundary_continuity_last": {"type": "mid_argument", "confidence": 0.82},
  "context_before": "... last 200 words of previous division ...",
  "context_after": "... first 200 words of next division ..."
}
```

### 1c. Summary report
CC writes `experiments/architecture_test/EXTRACTION_REPORT.md`:
- Per-book: total divisions, divisions in range, selected divisions with rationale
- Any normalization warnings or issues
- Division size distribution statistics
- Which divisions have `mid_argument` boundary continuity (candidates for D-011 test)

---

## Phase 2: Architect Creates Gold Reference

Before seeing any LLM output, the architect reads each extracted division's Arabic text and creates a gold reference file:
`experiments/architecture_test/gold/{fixture_name}/{div_index}_gold.json`

```json
{
  "teaching_units": [
    {
      "unit_id": "tu_1",
      "description": "Definition of اضطباع with linguistic derivation",
      "start_approx_word": 0,
      "end_approx_word": 85,
      "primary_scholarly_function": "definition",
      "secondary_functions": ["example"],
      "self_contained": true,
      "notes": "Complete definition unit — stands alone"
    },
    {
      "unit_id": "tu_2",
      "description": "Scholarly positions on the ruling of اضطباع",
      "start_approx_word": 86,
      "end_approx_word": 450,
      "primary_scholarly_function": "opinion_statement",
      "secondary_functions": ["evidence_hadith", "refutation"],
      "self_contained": true,
      "notes": "Complete مسألة: position + evidence + counter + conclusion"
    }
  ],
  "cross_boundary_argument": false,
  "notes": "Clean division with well-separated units"
}
```

If the division text continues an argument from the previous division or starts one that continues into the next:
```json
{
  "cross_boundary_argument": true,
  "cross_boundary_notes": "The last teaching unit (tu_3) contains an objection (اعتراض) with no response — the response appears in the next division's context_after text"
}
```

---

## Phase 3: LLM Extraction Tests

CC writes `experiments/architecture_test/run_tests.py` that runs three approaches on each division:

### Approach A — Single-call joint extraction

One LLM call per division. Prompt asks the LLM to simultaneously:
1. Identify natural teaching units (boundaries + description)
2. Classify each sentence by scholarly function
3. Evaluate self-containment of each unit

**System prompt:**
```
You are an expert in classical Islamic scholarly text analysis. You will receive 
Arabic scholarly text from a single division of a book. Your task:

1. Identify the natural TEACHING UNITS — self-contained scholarly segments that 
   each teach one concept, ruling, or argument. A teaching unit might be a 
   definition, a scholarly position with evidence, a hadith with commentary, 
   or a complete مسألة.

2. For each teaching unit, classify its PRIMARY scholarly function:
   definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
   opinion_statement, refutation, example, condition_exception, narration,
   cross_reference, editorial_note

3. Evaluate whether each teaching unit is SELF-CONTAINED: can it be understood
   alone without the surrounding text?

Return a JSON array of teaching units.
```

**Structured output schema:** (via Instructor)
```python
class TeachingUnit(BaseModel):
    unit_index: int
    start_word: int  # approximate word offset
    end_word: int
    description_arabic: str  # brief Arabic description
    primary_function: Literal[...scholarly function enum...]
    secondary_functions: list[str]
    self_contained: bool
    self_containment_notes: str | None

class ExtractionResult(BaseModel):
    teaching_units: list[TeachingUnit]
    total_units: int
```

### Approach B — Two-call classify-then-group

**Call 1 (classify):** LLM receives the division text and classifies each sentence by scholarly function. Returns a list of classified segments with character offsets.

**Call 2 (group):** LLM receives the classified segments and groups them into teaching units, evaluating self-containment.

### Approach C — With cross-boundary context (for selected divisions)

Same as Approach B, but Call 2 also receives:
- The last 200 words of the previous division (prefixed with "[PREVIOUS DIVISION CONTEXT]")
- The first 200 words of the next division (suffixed with "[NEXT DIVISION CONTEXT]")
- Instruction: "The main text to process is between the context markers. Use the context to determine if any argument at the start or end of the main text is incomplete."

Run Approach C only on divisions where `boundary_continuity_last.type == "mid_argument"` or the gold reference flags `cross_boundary_argument: true`. Target: 3-4 divisions.

### Configuration

- Model: `anthropic/claude-opus-4.6` via OpenRouter
- Temperature: 0 (deterministic)
- Max tokens: 8192
- Retries: 2 (if structured output validation fails)
- All results saved to `experiments/architecture_test/results/{fixture_name}/{div_index}_{approach}.json`

---

## Phase 4: Evaluation

The architect compares LLM results against gold reference.

### Metric 1: Boundary F1

A predicted teaching unit MATCHES a gold teaching unit if their word ranges overlap by ≥60%.

```
Precision = matched_predicted / total_predicted
Recall = matched_gold / total_gold
F1 = 2 * P * R / (P + R)
```

Compute per-division and averaged across all divisions.

### Metric 2: Classification Accuracy

For each matched unit pair, compare `primary_function`. Exact match = correct.

```
Accuracy = correct_classifications / total_matched_pairs
```

### Metric 3: Self-Containment Agreement

For each matched unit pair, compare `self_contained` boolean.

```
Agreement = matching_self_containment / total_matched_pairs
```

### Metric 4: D-011 Test (qualitative)

For divisions tested with Approach C:
- Did the context cause the LLM to merge/adjust any unit boundaries compared to Approach B?
- Did it correctly identify a split argument flagged in the gold reference?

### Decision Matrix

| Outcome | Action |
|---------|--------|
| Q1 Pass (F1 ≥ 0.70) + Q2 two-phase wins | Commit Architecture C with two-phase internal LLM (C-1) |
| Q1 Pass + Q2 single-phase wins or tie | Commit Architecture C with single-phase LLM (C-2) |
| Q1 Pass + Q3 context helps | Also commit soft D-011 |
| Q1 Pass + Q3 context doesn't help | Keep D-011 hard for now; revisit later |
| Q1 Fail (F1 < 0.70) | Abort Architecture C. Revert to Architecture B. Investigate why. |

---

## Risks and Mitigations

**Risk: Division heading-content misalignment (L-003).**
Discovery: 40-60% of leaf divisions have content that doesn't match their heading due to same-page heading chaining. The strict alignment check (heading's first 15 stripped chars in text's first 100 stripped chars) empirically filters these out.
Mitigation: CC's extract_divisions.py enforces strict alignment. Architect verifies visually in the evaluation workbook.

**Risk: Gold reference is created by an LLM (the architect), compared against LLM output.**
Mitigation: This IS a limitation. However: the architect (Opus in this chat, careful analysis) creates references in a separate session with full context. The test LLM (Opus via OpenRouter, prompt-constrained) operates under structured output constraints. The evaluation is primarily qualitative — the architect reads the Arabic and judges whether boundaries are sensible.

**Risk: 10 divisions is too small a sample.**
Mitigation: This is a viability test, not a final evaluation. If it passes, the full engine build will have its own evaluation with 50+ gold baselines per the Blueprint. If it fails, we avoided building the wrong architecture.

**Risk: Fixtures are small books, not representative of المغني (2.5M words).**
Mitigation: We're testing per-division extraction. Division size (300-2000 words) is representative regardless of book size.

**Risk: Bibliography/index divisions pass the word count filter.**
Mitigation: CC's selection algorithm excludes divisions whose heading contains مصادر, مراجع, فهرس.

**Risk: Same model family for test and evaluation.**
Mitigation: The evaluation is structured and qualitative — the architect reads Arabic text and judges whether unit boundaries are sensible. Quantitative metrics are secondary. If boundary placements are clearly wrong to a careful reader, no metric can save them.
