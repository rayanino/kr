# LLM Integration Test Protocol — بروتوكول اختبار التكامل مع النماذج اللغوية

**Purpose:** Verify that the excerpting engine produces correct, scholarly-sound output when processing real Arabic Islamic texts with real LLM calls. This is the protocol that determines whether the engine actually works — not the 554 unit tests (which use mocked LLM responses), not the structural validation (which checks data shapes), but whether real Arabic scholarly text gets correctly segmented, classified, grouped, attributed, and enriched.

**Authority:** This protocol governs all LLM integration testing for the excerpting engine. It supersedes any informal "looks good" assessments. The engine is not complete until this protocol's exit criteria are met.

**Critical context:** The owner has zero Islamic studies knowledge. Claude Chat (Architect) is the sole domain reviewer. Every error the architect misses becomes a wrong belief in the owner's mind. There is no safety net beyond this protocol.

**C-7 mitigation (same-model evaluation bias):** Claude Opus 4.6 produces the excerpting output AND Claude Chat evaluates it. To mitigate self-reinforcing bias: (1) every factual claim about authors, schools, and dates is independently verified via web search; (2) mechanical checks are used wherever possible instead of judgment; (3) CC runs adversarial spot-checks from a separate context; (4) decontextualization checks use the structural test (read boundary context) rather than asking "does this seem right."

---

## Phase A: Fixture Selection

### Principles

Fixture selection must cover the **failure modes that matter**, not just genre diversity. A test set of 5 fiqh books and 5 hadith books covers genre diversity but might miss every multi-layer attribution failure. The selection matrix below ensures coverage of specific risk dimensions.

### Selection Matrix

Select **5 books** for the first integration round. Each book must fill at least one cell that no other book fills. The goal is maximum failure-mode coverage in minimum books.

| Dimension | Why It Matters | Minimum Coverage |
|---|---|---|
| **Multi-layer (sharh/hashiyah)** | T-2 attribution risk — wrong author on every excerpt if layer detection fails | ≥2 books |
| **Single-layer (standalone work)** | Baseline — no layer complexity, tests pure classification/grouping | ≥1 book |
| **Verse-commentary (نظم)** | VC-1/VC-2 — verse+commentary must stay together | ≥1 book |
| **Hadith-heavy text** | Evidence handling — isnad+matn bonding, takhrij extraction | ≥1 book |
| **Fiqh with ikhtilaf** | Decontextualization risk — positions+refutations, DP-1/DP-5 | ≥1 book |
| **Long divisions (>2000 words)** | Scaling — does quality degrade at length? | ≥1 book |
| **Short divisions (<500 words)** | Minimum viable excerpts — can the LLM produce useful teaching units from small text? | ≥1 book |
| **Known fixtures (from experiment)** | Regression — do books that worked in the experiment still work in production? | ≥1 book |

### Source of Test Books

Use the normalized packages from the experiment (`experiments/format_diversity_test/packages/`) as the starting point — these have known-good normalization output. For books not in the experiment, run them through the normalization engine first and verify the normalized package is well-formed before feeding to excerpting.

The 20,000+ Shamela exports in `shamela-export-samples/` are the book pool. The experiment already normalized 5 packages (ibn_aqil_v1, ibn_aqil_v3, taysir, ext_39_masala, ext_46_qa). Additional books need normalization first.

### First Round Selection (5 books)

The architect selects 5 specific books at the start of the integration test session, documenting for each: the Shamela ID, title, author, genre, which matrix cells it covers, and which specific divisions will be tested. Selection criteria:

1. **At least one book the architect can deeply verify** — a well-known text with extensive online scholarly discussion (e.g., شرح ابن عقيل, رياض الصالحين, عمدة الأحكام) so that author attributions, school classifications, and topic keywords can be cross-referenced.
2. **At least one book with known multi-layer structure** — to test LA-1 through LA-4 attribution rules.
3. **At least one book with heavy ikhtilaf** — to test DP-1 (position+refutation) and DP-5 (counter-argument+original).
4. **At least one book from the experiment** — regression check.
5. **At least one book NOT from the experiment** — to test generalization beyond the fixture set.

---

## Phase B: Integration Run Configuration

### Run Script

CC writes a run script (`scripts/run_integration_test.py`) that:

1. Takes a normalized package path as input
2. Runs the full excerpting pipeline with real LLM calls (Opus 4.6 via OpenRouter)
3. Saves ALL intermediate outputs to a timestamped directory:
   - `phase1_chunks.json` — assembled chunks (Phase 1 output)
   - `phase2a_classifications/chunk_{id}.json` — raw classification result per chunk
   - `phase2b_groupings/chunk_{id}.json` — raw grouping result per chunk
   - `phase3_enrichments/chunk_{id}.json` — raw enrichment result per chunk
   - `phase3_verifications/chunk_{id}.json` — raw verification result per chunk (if consensus triggered)
   - `excerpts.jsonl` — final ExcerptRecords
   - `gate_queue.jsonl` — human gate entries (if any)
   - `processing_log.jsonl` — run telemetry
   - `raw_llm_responses/` — raw API responses (JSON) for every LLM call, keyed by call ID
4. Saves timing data per phase and per chunk
5. Does NOT catch exceptions silently — crashes are informative

### Run Configuration

| Parameter | Value |
|---|---|
| Model (classification, grouping) | `anthropic/claude-opus-4.6` via OpenRouter |
| Model (enrichment) | `anthropic/claude-opus-4.6` via OpenRouter |
| Model (verification) | `cohere/command-a-03-2025` via OpenRouter |
| Temperature | 0 (all calls) |
| Retries | 2 per chunk |
| Output directory | `integration_tests/run_{timestamp}/` |

### Pre-Run Checklist

Before running on any book:
- [ ] Normalized package exists and passes `validate_normalized_package()`
- [ ] API keys are valid (test with a 10-token call)
- [ ] Output directory is clean
- [ ] Git commit is clean (no uncommitted changes)
- [ ] Record the exact commit hash in the run metadata

---

## Phase C: Review Protocol

This is the core of the protocol. Every claim below is an instruction the architect follows mechanically — not a suggestion.

### C.1 — Structural Integrity Check (automated, every book)

Run immediately after each book completes. These are pass/fail — any failure is a BLOCKING finding.

1. **Pipeline completion:** Did the pipeline complete without crashes? Check `processing_log.jsonl` for errors.
2. **Excerpt count sanity:** Number of excerpts should be roughly proportional to book size. A 10,000-word book producing 2 excerpts or 500 excerpts is suspicious. Document expected range before running.
3. **Offset alignment:** For every excerpt, verify `text_snippet` matches the first 80 characters of `primary_text` (whitespace-normalized). This is V-P3-2 — if it fails, the offset normalization is broken and EVERY excerpt has wrong text boundaries.
4. **Field completeness:** Every ExcerptRecord has non-null values for: `excerpt_id`, `source_id`, `div_id`, `primary_text`, `primary_author_layer`, `self_containment`, `scholarly_function`, `excerpt_topic`.
5. **Error code audit:** Read `processing_log.jsonl`. List every error code emitted. For each ERROR-severity code: is the affected excerpt missing from output? For each WARNING: is the excerpt flagged appropriately?
6. **Gate queue consistency:** If EX-G-001/002/003 appear in any excerpt's `gate_flags`, verify the corresponding gate_queue.jsonl entry exists (V-P3-7).

### C.2 — Per-Excerpt Scholarly Review (manual, stratified)

This is where the architect reads Arabic text and evaluates scholarly correctness. The review depth varies by round:

**Round 1 (first 3 books): EVERY excerpt reviewed.** This is exhaustive because we have zero prior evidence of LLM call quality. Every failure mode needs to be discovered, not sampled.

**Round 2+ (subsequent books): Stratified sample.** Review all excerpts flagged with warnings/gates, all multi-layer excerpts, all excerpts with `self_containment != FULL`, and a random 30% of remaining excerpts.

For EACH reviewed excerpt, the architect completes this checklist:

#### C.2.1 — Boundary Quality

Read the excerpt's `primary_text` in full. Then read 200 characters before and after the excerpt in the `assembled_text` (reconstruct from Phase 1 chunks).

- [ ] **Natural break:** Does the excerpt start and end at a natural scholarly boundary? (New topic, new ruling, new evidence, new speaker — not mid-sentence, not mid-argument)
- [ ] **DP-1 check (position+refutation):** If the excerpt contains a reported position ("قال" + scholar name + position), does it also contain the response/refutation? If the refutation is in the NEXT excerpt, this is a CRITICAL decontextualization failure.
- [ ] **DP-2 check (Q+A):** If the excerpt contains a question marker (سؤال, فإن قيل, مسألة), does it also contain the answer?
- [ ] **DP-3 check (rule+exception):** If the excerpt contains a rule with "إلا" or "لكن" or similar exception markers, are both the rule and exception included?
- [ ] **DP-4 check (evidence+ruling):** If the excerpt contains evidence ("لقوله تعالى", "لحديث", "والدليل"), is the ruling it supports included?
- [ ] **DP-5 check (counter-argument+original):** If the excerpt opens with a counter-argument ("وأما قول", "ورد عليه"), is enough of the original argument included to understand what's being countered?
- [ ] **DP-6 check (condition+result):** If the excerpt contains "إذا...فـ" or similar conditional, are both parts included?

**Scoring:** PASS (no decontextualization), PARTIAL (minor context loss, excerpt still understandable), FAIL (critical context loss, excerpt misleading or unintelligible).

#### C.2.2 — Classification Quality

For each segment within the teaching unit (from Phase 2a output):

- [ ] **Scholarly function correct:** Read the segment text. Does the label match? Is a "refutation" really a refutation? Is "evidence_quran" really a Quran citation? Is "rule_statement" really a rule?
- [ ] **No gross misclassification:** Watch for: editorial notes classified as opinions, structural transitions classified as rulings, narration chains classified as evidence.

**Method:** Read the Arabic text of each segment. Compare the scholarly function label against the actual content. Web search specific terms if uncertain (e.g., search the Quran reference to verify it's real).

**Scoring:** CORRECT (label matches content), ACCEPTABLE (label is reasonable though not the architect's first choice), WRONG (label is clearly incorrect).

#### C.2.3 — Attribution Quality

- [ ] **Primary author correct:** For multi-layer texts, does `primary_author_layer` match reality? Read the excerpt — is this the commentator's analysis (sharh) or the original author's text (matn)? Cross-reference with the text_layers overlap computation.
- [ ] **Author identity correct:** Web search the author name. Does the `primary_author` field match the actual author of this layer of the text?
- [ ] **Quoted scholars correct:** If `quoted_scholars` is non-empty, verify: (a) the named scholar is actually quoted in the text, (b) the quote type (opinion, frame, refuted) is correct.
- [ ] **School attribution plausible:** If `school` is assigned, verify via web search that the author/text is actually associated with that school. A Hanbali text attributed to the Shafi'i school is a T-6 metadata poisoning failure.

**Method:** Web search "[author name] [book title]" in Arabic. Cross-reference with known scholarly databases (e.g., shamela.ws book pages, islamweb.net, al-maktaba.org).

**Scoring:** CORRECT, WRONG (factual error), UNVERIFIABLE (cannot confirm or deny via available sources).

#### C.2.4 — Enrichment Quality

- [ ] **Topic keywords meaningful:** Are the 1-3 `excerpt_topic` keywords meaningful Arabic scholarly terms that accurately describe the excerpt's content? Not too generic ("فقه" for every fiqh excerpt) and not too specific (hallucinated subtopics).
- [ ] **Evidence references valid:** For each `evidence_refs` entry: if Quran, verify surah/ayah numbers are real. If hadith, verify the narrator/collection attribution is plausible. This is a mechanical check — wrong Quran references are verifiable errors.
- [ ] **Self-containment level correct:** Read the excerpt as if you know nothing else about the book. Can you understand the scholarly point? If yes → FULL is correct. If you need context → PARTIAL is correct. If unintelligible → DEPENDENT is correct.
- [ ] **Context hint useful (if PARTIAL):** If self_containment is PARTIAL, does the context_hint actually explain what context is missing? A hint that says "refers to previous discussion" without specifying WHAT discussion is useless.

### C.3 — Cross-Book Analysis (after reviewing all books in a round)

After reviewing all individual books, the architect performs these cross-cutting checks:

1. **Attribution consistency:** If the same author appears in multiple books, are their details consistent? (Same school, same era, same canonical name)
2. **Classification consistency:** Do similar types of text get classified the same way across books? (A Quran citation in Book A and Book B should both be "evidence_quran")
3. **Systematic error patterns:** Are there error patterns that appear across multiple books? (e.g., all counter-arguments misclassified, all hadith isnad broken from matn) Systematic errors indicate prompt or code bugs — not one-off LLM mistakes.
4. **Gate rate:** What percentage of excerpts triggered human gates? A rate >20% suggests the pipeline is too uncertain; <2% suggests gates may not be triggering when they should.
5. **Error rate by phase:** Which phase produces the most errors? This guides fix prioritization.

### C.4 — CC Adversarial Audit

After the architect completes their review for a round, CC receives a bug-hunt prompt:

```
I've reviewed N excerpts across M books. Here is a summary of my findings: [summary].
Your job is to find things I missed. Read the raw LLM responses and the final excerpts for [specific book].
Look for:
1. Cases where the LLM returned something that LOOKS correct but is subtly wrong
2. Offset alignment issues that passed V-P3-2 but produce slightly wrong text boundaries
3. Teaching unit boundaries that technically don't violate DP rules but would confuse a reader
4. Enrichment fields that are plausible but factually wrong (verify author names, school attributions via web search)
5. Cases where consensus was NOT triggered but should have been (verifier agreed when it shouldn't have)
Report each finding with: file, excerpt_id, what's wrong, evidence, severity.
```

This dual-reviewer pattern (architect + CC) was validated during the normalization engine build: the architect found findings CC missed, and CC found findings the architect missed. Neither alone catches everything.

---

## Phase D: Finding Taxonomy

Every finding from the review is categorized using this taxonomy. Severity is measured by **epistemic impact** (does the owner learn something false?), not technical impact (does the pipeline crash?).

### CRITICAL — Wrong Belief

The owner would learn something false from this excerpt. Examples:
- Author attribution is wrong (T-2)
- A refutation is separated from the position it refutes, making the position appear to be the author's view (T-4 via DP-1)
- School attribution is wrong (T-6)
- A Quran reference cites the wrong surah/ayah

**Action:** Fix immediately. Re-run affected book. This category blocks progression to the next round.

### HIGH — Degraded Quality

The excerpt is usable but suboptimal. The owner wouldn't learn something false, but would miss something important. Examples:
- Self-containment is PARTIAL when it should be FULL (the excerpt IS self-contained, but the LLM was overly cautious)
- Topic keywords are too generic to be useful
- A multi-sentence teaching unit could have been split into two better units
- Context hint exists but is unhelpful

**Action:** Track. Fix if the pattern is systematic (appears in >20% of excerpts). Defer if isolated.

### MEDIUM — Cosmetic / Non-Epistemic

The excerpt is correct but could be improved. No wrong beliefs result. Examples:
- Scholarly function label is "acceptable" but not the most precise choice
- An excerpt is slightly too long (could have been split) but is self-contained
- A quoted scholar is correctly identified but the quote type is debatable

**Action:** Track. Fix only if systematic and if a code change (not prompt change) can address it.

### LOW — Expected Limitation

A known limitation producing the expected suboptimal result. Examples:
- L-001 through L-012 known limitations manifesting as expected
- A division with no clear structure producing coarser-grained excerpts
- An unusual text format producing less precise classification

**Action:** Document. No fix needed unless the frequency is unexpectedly high.

---

## Phase E: Fix-Rerun Cycle

### After Each Round

1. **Triage findings:** Categorize every finding per Phase D taxonomy.
2. **Root-cause analysis:** For each CRITICAL and HIGH finding, trace back to the specific cause:
   - **Code bug:** A specific function produces wrong output for a specific input. Fix in code.
   - **Prompt gap:** The LLM prompt doesn't constrain or guide a specific behavior. Fix in prompt.
   - **SPEC gap:** The SPEC doesn't define how to handle this case. Update SPEC, then fix code.
   - **Model limitation:** The LLM fundamentally cannot do this task reliably. Design a mitigation (deterministic fallback, additional validation, human gate).
3. **Fix:** CC implements fixes. Architect reviews.
4. **Re-run affected books:** Only the books where CRITICAL findings were found. Not the entire set.
5. **Verify fixes:** Re-review the specific excerpts that had findings. Confirm the fix resolves the issue without introducing regressions.

### Iteration Cadence

- **Round 1:** 5 books, exhaustive review, expect many findings (this is the first real test)
- **Round 2:** Fix CRITICAL findings from Round 1, re-run the 5 books, review fixes + spot-check
- **Round 3:** If Round 2 has zero CRITICAL findings, add 5 more books (different genres/structures). Review per stratified sampling.
- **Round 4+:** Continue adding books and fixing until exit criteria are met.

---

## Phase F: Exit Criteria

The excerpting engine LLM integration is COMPLETE when ALL of the following are true:

1. **Zero CRITICAL findings in the latest round.** No wrong beliefs in any reviewed excerpt.
2. **≥10 books tested across ≥3 rounds.** Sufficient diversity to trust generalization.
3. **All matrix cells covered.** Every dimension in the Selection Matrix (Phase A) has at least one book that passed with zero CRITICAL findings.
4. **Gate rate between 2-15%.** Below 2% suggests gates aren't triggering; above 15% suggests the pipeline is too uncertain for production use.
5. **Systematic HIGH findings resolved.** No HIGH-severity pattern appears in >10% of excerpts.
6. **CC adversarial audit found zero CRITICAL findings** in the latest round.
7. **Cross-book consistency checks pass.** Same authors get same attributions, same text types get same classifications.

When exit criteria are met, the engine is ready for the **owner's 30-book probe** (Task E) — which is a separate gate focused on the owner's subjective experience of the output quality, not on the architect's systematic verification.

---

## Appendix: Review Worksheet Template

For each book, the architect fills this worksheet and commits it to `integration_tests/reviews/`.

```markdown
# Integration Test Review — [Book Title]

**Book:** [title] by [author]
**Shamela ID:** [id]
**Run:** [commit hash] / [timestamp]
**Reviewer:** Claude Chat (Architect)
**Round:** [N]

## Structural Integrity (C.1)
- Pipeline completion: PASS / FAIL
- Excerpt count: [N] (expected: [range])
- Offset alignment (V-P3-2): [N]/[N] passed
- Field completeness: PASS / FAIL
- Error codes emitted: [list]
- Gate queue consistency: PASS / FAIL

## Per-Excerpt Review (C.2)
| excerpt_id | Boundary | Classification | Attribution | Enrichment | Self-Containment | Verdict |
|---|---|---|---|---|---|---|
| [id] | PASS/PARTIAL/FAIL | CORRECT/ACCEPTABLE/WRONG | CORRECT/WRONG/UNVERIFIABLE | [notes] | CORRECT/WRONG | [finding ID or OK] |

## Findings
| ID | Severity | Excerpt | Description | Root Cause | Fix |
|---|---|---|---|---|---|
| F-1 | CRITICAL | [id] | [what's wrong] | [code/prompt/spec/model] | [action] |

## Summary
- Total excerpts: [N]
- Reviewed: [N] ([%])
- CRITICAL: [N]
- HIGH: [N]
- MEDIUM: [N]
- LOW: [N]
- Verdict: PASS (0 CRITICAL) / BLOCKED ([N] CRITICAL)
```

---

## Appendix: Decontextualization Spot-Check Method

This is the single most important check in the protocol. Decontextualization is T-2 with epistemic consequences — the owner reads an excerpt and forms a wrong understanding of who holds what position.

**Method (for each excerpt boundary):**

1. Find the excerpt's position in the assembled text using `char_start` and `char_end` (from the teaching unit's word range mapped back to character offsets).
2. Extract 200 characters BEFORE `char_start` from the assembled text. Call this `pre_context`.
3. Extract 200 characters AFTER `char_end` from the assembled text. Call this `post_context`.
4. Read `pre_context` → excerpt → `post_context` as continuous Arabic text.
5. Ask: **"Does the excerpt, read alone, give a DIFFERENT impression than the excerpt read with context?"**
   - If the impression changes: the boundary is a decontextualization risk. Check which DP rule was violated.
   - If the impression is the same: the boundary is safe.

This is a structural check, not a judgment call. The "different impression" test is binary: either reading the context changes your understanding of who said what, or it doesn't.

**Example of a FAIL:**
- Excerpt text: "قال أبو حنيفة: لا يجب الترتيب في الوضوء"
- Post-context starts with: "ورد عليه ابن قدامة بأن..."
- Read alone: Abu Hanifa's position is presented as a standalone fact.
- Read with context: Abu Hanifa's position is being set up for refutation by Ibn Qudamah.
- **Verdict: FAIL (DP-1 violation).** The refutation must be in the same excerpt.

**Example of a PASS:**
- Excerpt text: Full discussion of wudu ordering including Abu Hanifa's position AND the response.
- Post-context starts with: "مسألة: في نواقض الوضوء" (new topic — nullifiers of wudu)
- Read alone: Complete scholarly discussion.
- Read with context: Same understanding — the next text is a new topic.
- **Verdict: PASS.** Natural boundary at topic shift.
