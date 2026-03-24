# Excerpting Engine — LLM Integration Testing Protocol

**Purpose:** Verify the excerpting engine produces correct, scholarly-sound output when processing real Arabic Islamic texts with real LLM calls. This protocol governs the multi-session evaluation that determines whether the engine is ready for production use.

**Authority:** This document is the governing protocol for all excerpting integration testing sessions. It overrides ad-hoc evaluation plans. Every session must follow the structure defined here.

**Critical context:** The owner has zero Islamic scholarly knowledge. The architect (Claude Chat) is the sole evaluator of domain correctness. Every review criterion in this document must be evaluable by the architect using: (a) the Arabic text itself, (b) web research into Islamic scholarly conventions, (c) cross-referencing with source metadata from the normalization engine, and (d) structural consistency checks. The architect cannot delegate domain evaluation to the owner — "does this look right?" is a banned question because the owner cannot answer it.

---

## Architecture of the Test

### What We're Testing

The excerpting engine makes **5 distinct LLM calls** per chunk of text:

| Call | Phase | Model | What It Does |
|------|-------|-------|-------------|
| Classification | 2a | Opus via OpenRouter | Segments text by scholarly function |
| Grouping | 2b | Opus via OpenRouter | Groups segments into self-contained teaching units |
| Enrichment | 3.2 | Opus via OpenRouter | Adds topic, school, scholars, evidence, terminology |
| Verification | 3.3 | GPT-4.1 via OpenRouter | Cross-checks school, attribution, self-containment |
| Escalation | 3.3 | Command A via OpenRouter | Tie-breaks when enrichment and verifier disagree |

Each call can fail in three ways: (1) the API fails (timeout, rate limit, parsing error), (2) the output is structurally valid but semantically wrong (wrong scholarly function, wrong school), or (3) the output triggers a downstream invariant failure (coverage gap, offset mismatch). The integration test must surface all three failure modes.

### What We're NOT Testing

Phase 1 (deterministic assembly) and all validation checks have 554 passing unit tests. We trust the deterministic infrastructure. The integration test focuses on: do the LLM prompts produce correct results on real Arabic text, and does the pipeline handle real LLM output correctly end-to-end?

---

## Prerequisites

### 1. Normalization Output

The excerpting engine takes `NormalizedPackage` as input. Before we can test excerpting, we need normalized output for each test book.

**Option A (preferred):** Run the normalization pipeline on test books and serialize the NormalizedPackage to JSON. The test runner loads these.

**Option B (fallback):** Build a `shamela_to_normalized.py` script that runs both normalization and excerpting in sequence, using the same Shamela HTML files from `shamela-export-samples/`.

The test runner script (built by CC) must handle both options.

### 2. API Keys

All calls go through OpenRouter. Required environment variable: `OPENROUTER_API_KEY`.

The verification model (GPT-4.1) and escalation model (Command A) are also accessed through OpenRouter. No direct API calls to Anthropic, OpenAI, or Cohere.

### 3. Output Directory

All integration test output is saved to `experiments/excerpting_integration/` with per-book subdirectories. Every intermediate result is preserved for review.

---

## Test Runner Script Design

CC builds `scripts/run_excerpting_integration.py` with these capabilities:

### Input
- Path to one or more Shamela `.htm` files OR pre-normalized `.json` packages
- Output directory (default: `experiments/excerpting_integration/`)
- `--phase1-only` flag: run only Phase 1 (deterministic) to verify assembly before spending on LLM calls
- `--dry-run` flag: run Phase 1 and print chunk statistics without LLM calls
- `--book-id` filter: process only specific books by Shamela ID

### Per-Book Output (saved to `experiments/excerpting_integration/{book_id}/`)

```
{book_id}/
  metadata.json          # Source metadata from normalization
  phase1_chunks.json     # All AssembledChunks (for review of assembly)
  phase2a_raw/           # Raw LLM classification responses (one per chunk)
    chunk_{n}_classify.json
  phase2b_raw/           # Raw LLM grouping responses (one per chunk)
    chunk_{n}_group.json
  phase3_raw/            # Raw LLM enrichment + verification responses
    chunk_{n}_enrich.json
    chunk_{n}_verify.json
    chunk_{n}_escalate.json  # Only if escalation triggered
  excerpts.jsonl         # Final ExcerptRecords
  gate_queue.jsonl       # Human gate entries (if any)
  processing_log.jsonl   # Processing telemetry
  review_summary.json    # Statistics for architect review (auto-generated)
```

### review_summary.json (auto-generated per book)

```json
{
  "book_id": "...",
  "source_metadata": {
    "title": "...",
    "author": "...",
    "science": "...",
    "school": "...",
    "format": "..."
  },
  "phase1": {
    "total_chunks": 0,
    "total_content_units": 0,
    "skipped_divisions": 0,
    "avg_chunk_words": 0,
    "max_chunk_words": 0
  },
  "phase2": {
    "total_segments": 0,
    "total_teaching_units": 0,
    "avg_unit_words": 0,
    "min_unit_words": 0,
    "max_unit_words": 0,
    "self_containment_distribution": {"FULL": 0, "PARTIAL": 0, "DEPENDENT": 0},
    "function_distribution": {"definition": 0, "rule_statement": 0, ...},
    "coverage_errors": [],
    "retries": {"classify": 0, "group": 0}
  },
  "phase3": {
    "total_excerpts": 0,
    "attribution_rules": {"LA-1": 0, "LA-2": 0, "LA-3": 0, "LA-4": 0},
    "school_distribution": {},
    "gate_entries": 0,
    "consensus_triggered": 0,
    "consensus_disagreements": 0,
    "errors": [],
    "retries": {"enrich": 0, "verify": 0}
  },
  "timings": {},
  "cost_estimate_usd": 0.0
}
```

### Review Viewer Script

CC also builds `scripts/view_excerpts.py` — renders excerpting output as readable terminal output for architect review:

```
scripts/view_excerpts.py experiments/excerpting_integration/{book_id}/

Output for each excerpt:
──────────────────────────────────────
Excerpt: exc_{source_id}_{div_id}_{chunk}_{unit}
Division path: كتاب الطهارة > باب الوضوء > فصل
Pages: Vol 1, pp 23-24
Attribution: Ibn Aqil (sharh layer, LA-1, 94% coverage)
Function: rule_statement + evidence_quran
Self-containment: FULL
School: حنفي (confidence: 0.85)
Topics: شروط الوضوء, الترتيب في الوضوء

TEXT (first 500 chars):
وأما الترتيب في الوضوء فقد اختلف العلماء فيه...

QUOTED SCHOLARS:
- أبو حنيفة (quoted_opinion, confidence: 0.9)
- الشافعي (refuted_position, confidence: 0.85)

EVIDENCE:
- quran: سورة المائدة آية 6

FLAGS: []
GATE: []
──────────────────────────────────────
```

This viewer is essential — the architect cannot review raw JSON effectively.

---

## Phased Testing Approach

### Phase A: Smoke Test (3 books, ~€1-2)

**Goal:** Does the pipeline run without crashing? Do prompts produce parseable output? Do basic invariants hold?

**Book selection:** 3 books, one from each category:
1. A single-layer fiqh text (simplest case — one author, no layer attribution complexity)
2. A multi-layer sharh text (tests layer attribution, LA-1/LA-2/LA-3 rules)
3. A hadith commentary (tests evidence extraction, takhrij, isnad handling)

**Selection method:** The architect picks books from the extended fixtures or from `shamela-export-samples/` based on the normalization manifest metadata. Books must have at least 5 divisions and be under 100 pages (to keep costs manageable).

**Review depth:** Structural only.
- Did Phase 1 produce chunks? How many?
- Did Phase 2 produce segments and teaching units without crashes?
- Did Phase 3 produce ExcerptRecords with all fields populated?
- What error codes fired? Any FATAL?
- What is the self-containment distribution?
- What is the teaching unit size distribution?
- Were any LLM retries needed? How many?

**Pass criteria:** Zero crashes. All books produce excerpts. No FATAL errors that aren't caught and handled. All 5a deterministic checks pass on the output.

**If Phase A fails:** Fix infrastructure bugs before proceeding. Do NOT proceed to Phase B with known crashes.

### Phase B: Quality Probe (5-8 books, ~€5-10)

**Goal:** Is the LLM output semantically correct? This is the critical phase.

**Book selection:** 5-8 books covering genre diversity:
1. Hanafi fiqh (tests school attribution for Hanafi positions)
2. Shafi'i fiqh (tests school attribution in a different tradition)
3. Nahw/grammar sharh (tests verse-commentary handling, VC-1/VC-2/VC-3)
4. Tafsir (tests Quran evidence extraction, surah/ayah resolution)
5. Hadith collection commentary (tests takhrij, hadith grading, isnad)
6. Usul al-fiqh (tests complex argument structure, DP-1 through DP-6)
7. (Optional) Aqeedah/kalam text (tests cross-school comparison)
8. (Optional) Mixed-format text with masala blocks (tests QM-1/QM-2/QM-3)

**Selection method:** The architect researches well-known books in each genre via web search, then checks if they're in the Shamela collection. Preferred: books the architect can verify against known scholarly content (e.g., a well-known commentary where the matn/sharh structure is documented).

**Review depth:** Full semantic review using the Review Protocol below.

The architect reviews EVERY excerpt from the first 2 books (deep review). For the remaining books, the architect reviews: all excerpts from 2 randomly selected divisions per book + all gate entries + all excerpts with review flags.

**Pass criteria (per the kr-evaluate skill):**
- 5a deterministic: 100% pass
- 5b LLM quality: ≥85% correct (measured per review criterion below)
- 5c cross-check: <30% evaluator noise (if an independent evaluation is run)
- Zero CORE GAP findings
- All ENGINE BUG findings fixed before Phase C

**If Phase B finds issues:** Categorize per kr-evaluate. Fix CORE GAPs and ENGINE BUGs. Re-run affected books. Do not proceed to Phase C with unfixed findings.

### Phase C: Scale Probe (15-20 books, ~€15-25)

**Goal:** Does the engine work at scale? Are there systematic patterns in failures?

**Book selection:** Stratified random sample from the full Shamela collection:
- 4 books from each major genre (fiqh, hadith, tafsir, grammar, aqeedah/misc)
- Include at least 2 very long books (>200 pages) and 2 very short books (<20 pages)
- Include at least 2 books with known complex structures (multi-hashiyah, manuscript variants)

**Review depth:** Statistical + targeted.
- Review `review_summary.json` for every book — flag anomalies (unusual distributions, high error rates, extreme unit sizes)
- Deep review 2 random excerpts per book
- Deep review ALL gate entries across all books
- Deep review ALL excerpts with review flags
- Deep review ALL excerpts from the 2 longest and 2 shortest books

**Pass criteria:**
- Overall crash rate: 0% (every book produces output)
- Gate rate: <15% of excerpts (higher means the engine is too uncertain)
- LLM retry rate: <20% of chunks needed retries
- Error code distribution: no systematic pattern (e.g., "all hadith books fail on EX-C-003")
- Semantic quality on spot-checks: ≥90% correct

**After Phase C:** The engine is ready for the owner's 30-book probe (Task E). The owner's probe is a human gate — but by Phase C, the engine should be producing reliably correct output that the owner can engage with as a student, not as a debugger.

---

## The Review Protocol — How the Architect Evaluates Each Excerpt

This is the most critical section. Every finding must be traceable to a specific criterion.

### Review Criterion 1: Teaching Unit Boundaries (Phase 2b quality)

**Question:** Does this excerpt start and end at a natural scholarly boundary?

**Evaluation method:**
1. Read the `primary_text` of the excerpt.
2. Read the `primary_text` of the preceding and following excerpts (if they exist in the same division).
3. Check: does the excerpt begin mid-sentence or mid-argument? Does it end mid-sentence or mid-argument?
4. Check: would moving the boundary one segment earlier or later improve the excerpt?

**Criteria:**
- PASS: The excerpt captures a complete scholarly thought. It starts where a new topic/argument/ruling begins and ends where it concludes.
- BOUNDARY_SHIFT: The boundary is close but off by one sentence or clause. Minor — the excerpt is still understandable.
- SPLIT_ERROR: A single argument/ruling is split across two excerpts. The first excerpt ends mid-argument and the second begins mid-argument. This is a grouping failure.
- MERGE_ERROR: Two unrelated topics are merged into one excerpt. The teaching unit should have been two separate units.

**Severity:** SPLIT_ERROR and MERGE_ERROR are LLM QUALITY findings. BOUNDARY_SHIFT is a warning.

### Review Criterion 2: Self-Containment (Phase 2b quality)

**Question:** Can someone read this excerpt alone and understand the scholarly point being made?

**Evaluation method:**
1. Read the `primary_text` without looking at surrounding excerpts.
2. Can you identify what the excerpt is teaching?
3. Are there unresolved references ("as mentioned above", "the previous ruling") that make the excerpt unintelligible?
4. Is there a refutation without the position being refuted?
5. Is there a condition without the rule it modifies?

**Criteria:**
- FULL_CORRECT: The excerpt is self-contained and marked FULL.
- PARTIAL_CORRECT: The excerpt needs some context and is correctly marked PARTIAL with an appropriate `context_hint`.
- DEPENDENT_CORRECT: The excerpt cannot stand alone and is correctly marked DEPENDENT.
- FALSE_FULL: The excerpt is marked FULL but actually requires context. **This is the dangerous error** — the owner studies a fragment believing it's complete.
- FALSE_PARTIAL: The excerpt is marked PARTIAL but is actually FULL (conservative but wastes the owner's time with unnecessary context hints).
- FALSE_DEPENDENT: The excerpt is marked DEPENDENT but is actually PARTIAL or FULL (overly conservative — may exclude usable content).
- MISSING_CONTEXT_HINT: The excerpt is PARTIAL but the `context_hint` is missing, empty, or unhelpful.

**Severity:** FALSE_FULL is a CORE GAP if systematic. FALSE_PARTIAL is a warning. MISSING_CONTEXT_HINT is an ENGINE BUG.

### Review Criterion 3: Author Attribution (Phase 3 deterministic + consensus)

**Question:** Is the excerpt attributed to the correct author?

**Evaluation method:**
1. Check `primary_author_layer` — which author is credited.
2. Read the `primary_text` — who is actually speaking/writing in this passage?
3. For multi-layer texts: does the text sound like commentary (sharh) or original text (matn)?
4. Cross-reference with `text_layers` coverage percentage and `rule_applied` (LA-1 through LA-4).

**Criteria:**
- CORRECT: The right author is attributed.
- WRONG_AUTHOR: The excerpt is attributed to the wrong author. **This is T-2 (Attribution Error)** — the most dangerous silent failure. The owner studies text believing it was written by the wrong person.
- AMBIGUOUS_UNRESOLVED: The attribution is genuinely ambiguous and correctly flagged via EX-G-001 or LA-3.

**Severity:** WRONG_AUTHOR is always a CORE GAP. It doesn't matter how rare it is — one wrong attribution means the owner learns something false.

### Review Criterion 4: Scholarly Function Classification (Phase 2a quality)

**Question:** Is the `primary_function` correct for what this excerpt actually contains?

**Evaluation method:**
1. Read the `primary_text`.
2. Identify what the text is actually doing: stating a rule? Presenting evidence? Defining a term? Refuting a position?
3. Compare against the assigned `primary_function` and `secondary_functions`.

**Criteria:**
- CORRECT: The function matches what the text is doing.
- WRONG_FUNCTION: The function is incorrect. E.g., a refutation classified as `opinion_statement`, or evidence classified as `narration`.
- PARTIALLY_CORRECT: The `primary_function` is wrong but the correct function appears in `secondary_functions` (or vice versa).

**Severity:** WRONG_FUNCTION is an LLM QUALITY finding. It affects downstream taxonomy placement but doesn't create false knowledge.

### Review Criterion 5: Topic Keywords (Phase 3 enrichment)

**Question:** Do the `excerpt_topic` keywords accurately describe what this excerpt is about?

**Evaluation method:**
1. Read the `primary_text`.
2. In your own words, what is this excerpt about?
3. Do the assigned topic keywords match? Are they specific enough to distinguish this excerpt from other excerpts in the same chapter?

**Criteria:**
- CORRECT: Keywords accurately capture the specific topic.
- TOO_BROAD: Keywords are correct but too general (e.g., "فقه" for a specific ruling about wudu conditions).
- TOO_NARROW: Keywords miss the broader topic.
- WRONG_TOPIC: Keywords describe something the excerpt is not about.
- MISSING: No keywords assigned (and enrichment did not fail).

**Severity:** WRONG_TOPIC is an LLM QUALITY finding. TOO_BROAD is a warning (affects taxonomy precision). TOO_NARROW and MISSING are warnings.

### Review Criterion 6: School Attribution (Phase 3 enrichment + consensus)

**Question:** Is the `school` field correct for the position presented in this excerpt?

**Evaluation method:**
1. Read the `primary_text`. Does it present a position from a specific madhhab?
2. Check if the attributed `school` matches the position, not the author. (A Hanbali author may present the Shafi'i position for comparison.)
3. If `school` is null, is that correct? (Grammar texts, tafsir, etc. may not have school attribution.)
4. If `school` is `cross_school`, does the excerpt actually compare multiple schools?

**Criteria:**
- CORRECT: School attribution matches the position presented.
- WRONG_SCHOOL: The excerpt presents one school's position but attributes it to another.
- SHOULD_BE_NULL: A school is attributed but the text doesn't present a school-specific position.
- SHOULD_NOT_BE_NULL: No school is attributed but the text clearly presents a school-specific position.
- AUTHOR_NOT_POSITION: The school is attributed based on the author's school rather than the position in the text (the exact error the SPEC warns against in §7.2.2).

**Severity:** WRONG_SCHOOL is an LLM QUALITY finding (T-2 adjacent — wrong tradition attribution). AUTHOR_NOT_POSITION is a prompt quality issue.

### Review Criterion 7: Decontextualization (Phase 2b quality — DP-1 through DP-6)

**Question:** Has context been lost in a way that changes the meaning of the excerpt?

**Evaluation method:**
1. Read the `primary_text`.
2. Read the surrounding excerpts in the same division.
3. Check each DP rule:
   - DP-1: Is a reported position separated from its refutation?
   - DP-2: Is a question separated from its answer?
   - DP-3: Is a rule separated from its exception?
   - DP-4: Is evidence separated from the ruling it supports?
   - DP-5: Is a counter-argument presented without the original argument?
   - DP-6: Is a conditional statement split into condition and result?

**Criteria:**
- NO_DECONTEXTUALIZATION: Context is preserved.
- DP_VIOLATION: One of the DP rules is violated. Specify which one (DP-1 through DP-6).
- SUBTLE_DECONTEXTUALIZATION: No DP rule is formally violated, but the excerpt's meaning is changed by the separation from its context. This is the hardest case to catch.

**Severity:** DP_VIOLATION is a CORE GAP if systematic across multiple books. SUBTLE_DECONTEXTUALIZATION is an LLM QUALITY finding.

### Review Criterion 8: Evidence References (Phase 3 deterministic)

**Question:** Are Quran verses, hadith citations, and ijma references correctly identified?

**Evaluation method:**
1. Read the `primary_text` and find every evidence citation.
2. Compare against `evidence_refs`. Is every citation captured? Are surah/ayah numbers correct?
3. Check `takhrij_data` for hadith excerpts — are the collections and numbers correct?
4. Check for false positives — is something marked as evidence that isn't?

**Criteria:**
- CORRECT: All evidence is captured with correct references.
- MISSED_EVIDENCE: A citation in the text is not in `evidence_refs`.
- WRONG_REFERENCE: The reference is captured but the surah/ayah/collection is wrong.
- FALSE_POSITIVE: Something is marked as evidence that isn't.

**Severity:** WRONG_REFERENCE is an ENGINE BUG (deterministic detection should be correct). MISSED_EVIDENCE for Quran is a warning (pattern matching may miss unusual citation formats). MISSED_EVIDENCE for hadith is expected in some cases (not all hadith citations have clear markers).

### Review Criterion 9: Quoted Scholar Resolution (Phase 3 enrichment)

**Question:** Are scholars mentioned in the text correctly identified in `quoted_scholars`?

**Evaluation method:**
1. Read the `primary_text` and find every scholar mention (by name or epithet).
2. Compare against `quoted_scholars`. Is each mention captured?
3. For epithet resolution: is "الإمام" resolved to the correct person given the text's school context?
4. Is the `role` correct? (quoted_opinion vs classification_frame vs refuted_position)

**Criteria:**
- CORRECT: All scholars identified with correct names and roles.
- MISSED_SCHOLAR: A scholar mentioned in the text is not in `quoted_scholars`.
- WRONG_RESOLUTION: An epithet is resolved to the wrong person.
- WRONG_ROLE: The scholar is identified but their role is wrong (e.g., a refuted scholar marked as quoted_opinion).

**Severity:** WRONG_RESOLUTION is an LLM QUALITY finding. WRONG_ROLE is a warning. MISSED_SCHOLAR is a warning (complete resolution is hard).

---

## How the Architect Conducts a Review Session

### Before Starting

1. Pull the repo.
2. Run `scripts/view_excerpts.py experiments/excerpting_integration/{book_id}/` for each book.
3. Open `review_summary.json` for each book — check for anomalies.
4. Open the original Shamela HTML for cross-reference (if available).

### Deep Review Process (for Phase B full reviews)

For each excerpt in the book (or sampled set):

1. Read the rendered excerpt from the viewer.
2. Score each of the 9 review criteria. Record: criterion, verdict, notes.
3. If any criterion scores as a failure: open the raw LLM response (`phase2a_raw/`, `phase2b_raw/`, `phase3_raw/`) to identify which LLM call produced the error.
4. For domain-uncertain judgments: use web search to verify. E.g., "is الإمام in a Hanbali context referring to Ahmad ibn Hanbal?" — search for confirmation.

### Recording Findings

Each finding is recorded in `experiments/excerpting_integration/{book_id}/review_findings.jsonl`:

```json
{
  "excerpt_id": "exc_...",
  "criterion": "RC-3 (author attribution)",
  "verdict": "WRONG_AUTHOR",
  "severity": "CORE_GAP",
  "notes": "Excerpt attributed to Ibn Aqil (sharh) but the text is a direct quote from the Alfiyya (matn). Coverage was 78% sharh, triggering LA-1, but the quoted verse portion is the teaching content.",
  "raw_response_file": "phase3_raw/chunk_2_enrich.json",
  "fix_category": "LLM_QUALITY"
}
```

### Aggregation

After reviewing all sampled excerpts, aggregate:

```
Total excerpts reviewed: N
Per-criterion pass rates:
  RC-1 (boundaries):    X/N (Y%)
  RC-2 (self-contain):  X/N (Y%)
  RC-3 (attribution):   X/N (Y%)
  RC-4 (function):      X/N (Y%)
  RC-5 (topics):        X/N (Y%)
  RC-6 (school):        X/N (Y%)
  RC-7 (decontext):     X/N (Y%)
  RC-8 (evidence):      X/N (Y%)
  RC-9 (scholars):      X/N (Y%)

Findings by category:
  CORE_GAP:     N
  ENGINE_BUG:   N
  LLM_QUALITY:  N
  DATA_ISSUE:   N
  UPSTREAM_ERR: N
```

---

## Fix Cycle

After each review phase:

1. **Categorize** every finding using kr-evaluate categories.
2. **Prioritize:** CORE_GAP > ENGINE_BUG > LLM_QUALITY.
3. **Design fixes:**
   - ENGINE_BUG → CC fixes code, architect reviews.
   - LLM_QUALITY → Architect redesigns prompt, CC implements, re-run affected books.
   - CORE_GAP → Architect assesses if SPEC change is needed. If yes, update SPEC first.
4. **Re-run** affected books after fixes. Compare before/after.
5. **Proceed** to next phase only when current phase pass criteria are met.

The fix cycle may take multiple sessions. That is expected and correct. Rushing to Phase C with unfixed Phase B findings is the "momentum trap" — the same anti-pattern the review protocol guards against.

---

## Cost Management

All calls go through OpenRouter. Estimated costs per book (rough, based on experiment data):

| Book Size | Phase 2 | Phase 3 | Total |
|-----------|---------|---------|-------|
| Small (5-10 divisions) | ~€0.15 | ~€0.20 | ~€0.35 |
| Medium (20-40 divisions) | ~€0.50 | ~€0.70 | ~€1.20 |
| Large (80+ divisions) | ~€1.50 | ~€2.00 | ~€3.50 |

Phase A (3 books): ~€2-4
Phase B (5-8 books): ~€5-15
Phase C (15-20 books): ~€15-40
Total estimated: ~€25-60

Budget is unlimited (per memory). These estimates are for planning, not for constraining.

---

## Session Structure

Each integration testing session follows this pattern:

1. **Clone/pull.** Read this protocol. Read `experiments/excerpting_integration/STATUS.md` (maintained by the architect across sessions).
2. **Check where we are** in the phased approach (A, B, or C).
3. **If running tests:** CC runs the test script on selected books. Architect reviews output.
4. **If reviewing results:** Architect conducts deep review per the Review Protocol above.
5. **If fixing:** CC implements fixes. Architect reviews. Re-run affected books.
6. **Update STATUS.md** with: what was done, findings, next steps.
7. **Session-end retrospective:** What went wrong, what to improve.

### STATUS.md Template

```markdown
# Excerpting Integration Testing — Status

## Current Phase: [A / B / C]

## Books Processed
| Book ID | Title | Genre | Phase | Status | Findings |
|---------|-------|-------|-------|--------|----------|

## Open Findings
| Finding ID | Book | Criterion | Severity | Status |
|------------|------|-----------|----------|--------|

## Completed Fix Cycles
| Cycle | Findings Fixed | Books Re-run | Result |
|-------|---------------|-------------|--------|

## Next Session
[What to do next]
```

---

## Anti-Patterns to Watch For

1. **"All excerpts look reasonable"** — If you're not finding any issues, your review is too shallow. Real Arabic text processing always has edge cases.

2. **"The LLM is just bad at this"** — Before blaming the model, check: is the prompt clear? Is the input well-formed? Is the task decomposed correctly? Most "LLM quality" issues are actually prompt issues.

3. **"We'll catch it in the 30-book probe"** — The owner cannot catch domain errors. If the architect doesn't catch it here, nobody catches it.

4. **"This is an edge case"** — If the same edge case appears in 2+ books, it's a pattern, not an edge case. Patterns need fixes.

5. **"Let's move on to Phase C, we'll fix this later"** — No. Fix it now. Phase C is a scale test, not a quality test. Quality must be established in Phase B.

6. **Reviewing only `review_summary.json`** — Statistics hide specific failures. The architect must read actual Arabic text from actual excerpts. The viewer script exists for this reason.
