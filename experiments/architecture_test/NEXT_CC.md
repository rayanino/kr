# NEXT — Architecture C Empirical Validation (CC Session)

## Current Position

Source engine: **COMPLETE**
Normalization engine: **COMPLETE** (470 passed, 14 skipped)

The architect has proposed merging atomization + excerpting into a single engine (Architecture C). Before committing, we need empirical validation. This session produces all test infrastructure AND runs the full experiment. The architect evaluates results in a separate chat.

## What To Do

Four deliverables. Build and verify in order.

---

### Deliverable 1: Normalized Packages

Run `normalize_source()` on 5 fixtures. Write each package to disk.

**Fixtures to process:**

| Fixture | HTM Path | is_multi_layer |
|---------|----------|----------------|
| 03_fiqh | `tests/fixtures/shamela_real/03_fiqh/book.htm` | False |
| 07_balagha | `tests/fixtures/shamela_real/07_balagha/book.htm` | False |
| 06_usul | `tests/fixtures/shamela_real/06_usul/book.htm` | False |
| 02_nahw_muhaqiq | `tests/fixtures/shamela_real/02_nahw_muhaqiq/book.htm` | True |
| 10_no_author | `tests/fixtures/shamela_real/10_no_author/book.htm` | False |

**How to produce each package:**

```python
from pathlib import Path
from engines.normalization.tests.conftest import _make_source_metadata
from engines.normalization.src.dispatcher import normalize_source

path = Path("tests/fixtures/shamela_real/{fixture_name}/{htm_file}")
meta = _make_source_metadata(is_multi_layer={True or False per table above})
pkg = normalize_source(path, meta)
```

**How to write each package to disk:**

```python
out_dir = Path("experiments/architecture_test/packages/{fixture_name}")
out_dir.mkdir(parents=True, exist_ok=True)

with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
    f.write(pkg.manifest.model_dump_json(indent=2))

with open(out_dir / "content.jsonl", "w", encoding="utf-8") as f:
    for cu in pkg.content_units:
        f.write(cu.model_dump_json())
        f.write("\n")
```

Write as `experiments/architecture_test/produce_packages.py`. Run it.

**Verification:** Each directory has manifest.json + content.jsonl. Print per-fixture: content unit count, leaf division count.

---

### Deliverable 2: Division Extraction (CRITICAL — read carefully)

Write `experiments/architecture_test/extract_divisions.py` that selects high-quality divisions for the LLM test.

**The normalization engine has a known limitation (L-003): same-page headings get chained, causing division heading ↔ content misalignment.** Up to 60% of leaf divisions have content that doesn't match their heading. The experiment MUST filter these out or the LLM test results are garbage.

#### Step-by-step algorithm:

**1. Load packages:** For each fixture, read manifest.json (division tree) and content.jsonl (content units).

**2. Walk division tree to find leaf divisions:** Nodes with empty `children` array.

**3. Assemble cross-page text per leaf division:**

Content units are at indices `[start_unit_index, end_unit_index]` (inclusive). Join their `primary_text` fields using `boundary_continuity` signals from each unit:

| boundary_continuity.type | Join behavior |
|--------------------------|---------------|
| `mid_sentence` | Empty string (no separator) |
| `mid_paragraph` | Single newline `\n` |
| `mid_argument` | Single newline `\n` |
| `section_break` | Double newline `\n\n` |
| `division_break` | Double newline `\n\n` |
| `unknown` | Single newline `\n` |
| None (absent) | Single newline `\n` |

These are the ONLY values in `BoundaryContinuityType` enum (verified: engines/normalization/contracts.py line 238).

**4. Compute Arabic word count:** `len([w for w in text.split() if any('\u0600' <= c <= '\u06FF' for c in w)])`

**5. Filter to 300-2000 Arabic word range.**

**6. STRICT ALIGNMENT CHECK (mandatory — do not skip):**

```python
import re

def strip_arabic_noise(text):
    """Strip ZWNJ, ZWJ, diacritics, tatweel for comparison."""
    text = text.replace('\u200c', '').replace('\u200d', '')
    text = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

heading_clean = strip_arabic_noise(heading_text)[:15]
text_clean = strip_arabic_noise(assembled_text)[:100]
aligned = heading_clean in text_clean if heading_clean else False
```

REJECT any division where `aligned` is False. This filters out L-003 artifacts.

**7. Exclude non-scholarly divisions:** Reject divisions whose heading contains any of: `مصادر`, `مراجع`, `فهرس`, `ثبت المصادر`, `المراجع`. These are bibliography/index pages, not scholarly content.

**8. Select 2 divisions per fixture from the remaining candidates:**

Selection priority: sort by distance from 700 words (ascending). Skip divisions at index 0 of the tree (introductions). Take the 2 closest to 700 words.

**Exception for 03_fiqh:** If any aligned candidate has its last content unit's `boundary_continuity.type == "mid_argument"`, prefer that division as one of the two (for D-011 cross-boundary test).

**Exception for 02_nahw_muhaqiq:** If any aligned candidate contains content units with `len(cu.text_layers) > 1`, prefer that division (for multi-layer test).

If a fixture has fewer than 2 aligned candidates, take whatever is available and log a warning.

**9. For each selected division, extract context:**

- `context_before`: Assemble text from content units at indices `max(0, start_unit_index - 3)` through `start_unit_index - 1`. Empty string if `start_unit_index` is 0.
- `context_after`: Assemble text from content units at indices `end_unit_index + 1` through `min(last_unit_index, end_unit_index + 3)`. Empty string if at end.
- Use the same boundary_continuity join rules.

**10. Write output per division:**

File: `experiments/architecture_test/divisions/{fixture_name}/div_{start_unit_index}.json`

```json
{
  "fixture_name": "03_fiqh",
  "div_start_unit": 4,
  "div_end_unit": 9,
  "heading_text": "المطلب الأول: تعريف الاضطباع والرمل",
  "heading_path": ["مقدمة", "المطلب الأول"],
  "assembled_text": "...",
  "arabic_word_count": 539,
  "text_layers": [...],
  "content_flags_aggregated": {
    "has_hadith": false,
    "has_quran": true,
    "has_verse": false
  },
  "boundary_continuity_last_unit": {
    "type": "section_break",
    "confidence": 0.9
  },
  "context_before": "...",
  "context_after": "...",
  "selection_reason": "closest to 700w target"
}
```

`heading_path`: walk from tree root to this leaf, collecting each ancestor's `heading_text`.

`text_layers`: union of text_layer segments from all content units, with `start_char`/`end_char` rebased to the assembled_text. Rebasing: for each unit after the first, add cumulative character offset (sum of preceding units' `primary_text` lengths + join separator lengths).

`content_flags_aggregated`: OR across all constituent units' content_flags fields.

**11. Also write a READABLE text file per division:**

File: `experiments/architecture_test/divisions/{fixture_name}/div_{start_unit_index}_text.md`

```markdown
# Division: المطلب الأول: تعريف الاضطباع والرمل
**Fixture:** 03_fiqh | **Words:** 539 | **Units:** 4-9
**Selection reason:** closest to 700w target
**BC last unit:** section_break (0.9)

---

[FULL ARABIC TEXT HERE - the complete assembled_text, unmodified]

---

## Context Before (previous 3 units)
[context_before text]

## Context After (next 3 units)
[context_after text]
```

This readable file is the PRIMARY input for the architect's evaluation. It must contain the COMPLETE Arabic text, no truncation.

**Verification:**
- Print summary table: fixture, div_start_unit, heading (50 chars), word count, aligned (must all be True), selection_reason
- Confirm 10 total divisions (2 per fixture). If any fixture has <2, log warning.
- Print first 60 STRIPPED chars of each division's text alongside its heading — visual alignment confirmation.

---

### Deliverable 3: LLM Test Runner (run on ALL divisions)

Write `experiments/architecture_test/run_tests.py`.

**API Configuration:**
- Read API key from `ANTHROPIC_API_KEY` environment variable. If not set, raise clear error.
- Model: `claude-sonnet-4-20250514`
- Temperature: 0
- Max tokens: 4096
- Dependencies: `pip install anthropic instructor pydantic --break-system-packages`

**Pydantic output schemas:**

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

FUNCTION_ENUM = Literal[
    "definition", "rule_statement", "evidence_quran", "evidence_hadith",
    "evidence_ijma", "evidence_qiyas", "evidence_rational",
    "opinion_statement", "refutation", "example", "condition_exception",
    "cross_reference", "narration", "editorial_note", "structural_transition",
    "unclassified"
]

class TeachingUnit(BaseModel):
    unit_index: int = Field(description="0-based index within this division")
    start_word: int = Field(description="Approximate start word offset in assembled text")
    end_word: int = Field(description="Approximate end word offset in assembled text")
    text_snippet: str = Field(description="First 80 characters of this unit's text")
    description_arabic: str = Field(description="Brief Arabic description of what this unit teaches, 10-30 words")
    primary_function: FUNCTION_ENUM
    secondary_functions: list[str] = Field(default_factory=list)
    self_contained: bool = Field(description="Can this unit be understood without surrounding context?")
    self_containment_notes: Optional[str] = None

class ExtractionResult(BaseModel):
    teaching_units: list[TeachingUnit]
    total_units: int
    notes: Optional[str] = None

class ClassifiedSegment(BaseModel):
    segment_index: int
    start_word: int
    end_word: int
    text_snippet: str = Field(description="First 50 chars of segment text")
    scholarly_function: FUNCTION_ENUM
    confidence: float = Field(ge=0.0, le=1.0)

class ClassificationResult(BaseModel):
    segments: list[ClassifiedSegment]
    total_segments: int
```

**Approach A — Single-call joint extraction:**

System prompt:
```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You will receive Arabic scholarly text from a single division of a book. Your task:

1. Identify the natural TEACHING UNITS — self-contained scholarly segments that each teach one distinct concept, ruling, or argument. A teaching unit is the smallest segment a student could study and learn something complete from. Examples:
   - A definition with its explanation
   - A scholarly position (مسألة) with its evidence and conclusion
   - A hadith with its chain and commentary
   - A grammatical rule with its examples

2. For each teaching unit, classify its PRIMARY scholarly function from this list:
   definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
   evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
   condition_exception, cross_reference, narration, editorial_note,
   structural_transition, unclassified

3. Evaluate whether each teaching unit is SELF-CONTAINED: can a student with general familiarity of the science understand what is being taught without reading the surrounding text?

Important rules:
- Never split an argument (position + evidence + counter-evidence + conclusion) across units
- Never split an isnad chain from its matn
- A reported position ("قال أبو حنيفة") and its refutation ("ورد عليه بأن") belong in the same unit
- Consecutive definitions of related terms may be separate units if each is independently understandable
- Include text_snippet: the first 80 characters of each unit's text (copy exactly from input)
```

User message: the division's `assembled_text`

Use Instructor with `response_model=ExtractionResult`.

**Approach B — Two-call classify-then-group:**

Call 1 system prompt:
```
You are an expert in classical Islamic scholarly text analysis.

Classify each sentence or closely bonded group of sentences in this Arabic text by scholarly function:
definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
condition_exception, cross_reference, narration, editorial_note,
structural_transition, unclassified

Rules:
- An isnad chain + its matn = one segment (narration or evidence_hadith)
- A position marker ("قال X") + the stated position = one segment
- Each Quran citation with its introduction = one segment
- Each distinct sentence or bonded group gets exactly one classification
- Include text_snippet: the first 50 characters of each segment
```

Call 1 user message: the division's `assembled_text`
Call 1 response_model: `ClassificationResult`

Call 2 system prompt:
```
You are an expert in classical Islamic scholarly text analysis.

You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained scholarly
segments that each teach one distinct concept, ruling, or argument.

Rules:
- A position (opinion_statement) + its evidence + any counter-evidence + conclusion = one unit
- A definition + its examples = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- Each unit should be self-contained: a student can learn from it without the surrounding text
- Include text_snippet: the first 80 characters of each unit
```

Call 2 user message: `"Classified segments:\n" + classification_result.model_dump_json(indent=2) + "\n\nOriginal text:\n" + assembled_text`
Call 2 response_model: `ExtractionResult`

**Approach C — With cross-boundary context:**

Same as Approach B, but Call 2 user message has this prefix:
```
[PREVIOUS DIVISION — for context only, do not extract units from this]
{context_before}

[MAIN TEXT — extract teaching units from this only]
{assembled_text}

[NEXT DIVISION — for context only, do not extract units from this]
{context_after}

If any argument at the start or end of the MAIN TEXT is incomplete, note this
in the teaching unit's self_containment_notes and mark self_contained=False.

Classified segments (for MAIN TEXT only):
{classification_result json}
```

Run Approach C on ALL divisions from 03_fiqh, plus any division from other fixtures where `boundary_continuity_last_unit.type == "mid_argument"`.

**Execution:**

Run ALL approaches on ALL 10 divisions. Not verification on one — the full run.

```python
for each division JSON file:
    result_a = run_approach_a(division)
    save("results/{fixture}/div_{start_unit}_approach_a.json", result_a)

    result_b = run_approach_b(division)
    save("results/{fixture}/div_{start_unit}_approach_b.json", result_b)

    if should_run_c(division):
        result_c = run_approach_c(division)
        save("results/{fixture}/div_{start_unit}_approach_c.json", result_c)
```

Save each result as the Pydantic model's `.model_dump_json(indent=2)`.

**Error handling:**
- If Instructor validation fails after 2 retries, save to `{path}_error.json` with `{"error": str(e), "raw_response": ...}`. Continue to next.
- Log every API call: fixture, div, approach, model, input_tokens, output_tokens, latency_ms.

**After all runs, write `experiments/architecture_test/results/RUN_SUMMARY.md`:**
- Per-division: fixture, heading, word count, approach A units, approach B units, approach C units (if run), any errors
- Total: API calls made, tokens used, estimated cost (input × $3/MTok + output × $15/MTok for Sonnet)
- Any divisions that failed all retries

---

### Deliverable 4: Evaluation Workbook

Write `experiments/architecture_test/EVALUATION_WORKBOOK.md` — the architect's primary evaluation input.

For each of the 10 divisions, produce a section:

```markdown
## Division: {heading_text}
**Fixture:** {fixture_name} | **Words:** {word_count} | **Units:** {start}-{end}

### Full Arabic Text
{complete assembled_text — no truncation}

### Approach A Results ({N} teaching units)
| # | Words | Function | Self-contained | Snippet |
|---|-------|----------|----------------|---------|
| 0 | 0-85 | definition | ✓ | {text_snippet} |
| 1 | 86-210 | opinion_statement | ✓ | {text_snippet} |

**Description per unit:**
- Unit 0: {description_arabic}
- Unit 1: {description_arabic}

### Approach B Results ({N} teaching units)
[same table format]

### Approach C Results ({N} teaching units) [if applicable]
[same table format]

### Comparison Notes
- A produced {N_a} units, B produced {N_b} units
- Boundary differences: [list where A and B disagree on unit boundaries]

---
```

This workbook MUST be complete — every division, every approach result, full Arabic text. The architect needs to read the Arabic and judge whether the LLM's unit identification makes sense.

---

## Read First

1. This file
2. `experiments/architecture_test/EXPERIMENT_DESIGN.md`
3. `engines/normalization/src/dispatcher.py` — `normalize_source()` (line 32)
4. `engines/normalization/contracts.py` — `NormalizedPackage` (line 716), `ContentUnit` (line 427), `DivisionNode` (line 484), `BoundaryContinuity` (line 257), `BoundaryContinuityType` enum (line 238): values are `mid_sentence`, `mid_paragraph`, `mid_argument`, `section_break`, `division_break`, `unknown`
5. `engines/normalization/tests/conftest.py` — `_make_source_metadata()` factory

## Design Decisions

**DD-1: Sonnet not Opus.** Floor test. If Sonnet works, Opus will work better.

**DD-2: Strict alignment check.** L-003 causes 40-60% of divisions to have misaligned headings. Only divisions where heading matches content are usable. The `strip_arabic_noise` + first 100 chars check is empirically validated by the architect.

**DD-3: Full run, not verification-only.** CC runs all approaches on all divisions. The architect evaluates in a separate chat with all results available.

**DD-4: text_snippet in output schema.** The LLM returns the first 80 chars of each teaching unit's text. This lets the architect verify unit boundaries without re-reading the full text.

**DD-5: No consensus.** Single-model calls. Consensus is orthogonal to the architecture question.

## Do NOT Do

1. Do NOT modify any normalization engine code or tests.
2. Do NOT create gold references — that is the architect's job.
3. Do NOT evaluate LLM output quality — save results, report counts and costs.
4. Do NOT use Opus — use Sonnet (`claude-sonnet-4-20250514`).
5. Do NOT skip the alignment check. Misaligned divisions produce garbage results.
6. Do NOT truncate Arabic text in the evaluation workbook. Full text is required.

## Verification

After all 4 deliverables:
1. `packages/` — 5 directories, each with manifest.json + content.jsonl
2. `divisions/` — 5 directories, each with 2 `.json` + 2 `_text.md` files
3. `results/` — at least 20 JSON files (10 divisions × 2 approaches minimum) + RUN_SUMMARY.md
4. `EVALUATION_WORKBOOK.md` — complete, with full Arabic text for all 10 divisions
5. All scripts execute without errors
6. Print final summary table: fixture | div | heading | words | A units | B units | C units | errors

## After This

The architect opens a NEW chat, reads the EVALUATION_WORKBOOK.md, and makes the architecture decision. CC is not involved in evaluation.
