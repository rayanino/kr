---
name: kr-evaluate
description: Review engine test results across deterministic (5a), LLM-worker (5b), LLM-evaluator (5c). Use for "evaluate results", "check output", or reviewing any engine build cycle.
---

# KR Evaluate — تقييم النتائج

You are collaboratively reviewing test results from a KR engine build cycle with the owner. Your job is to categorize every issue, distinguish engine bugs from SPEC gaps from data problems, help the owner spot-check Arabic output, and gather evidence for the inter-engine gate decision: "Is this engine's output trustworthy enough to feed the next engine?"

---

## The Three Test Dimensions

### 5a — Deterministic Checks
These are automated, binary pass/fail tests. No judgment required.

**What they test:**
- Schema conformance (Pydantic validation)
- Text integrity (Arabic characters, diacritics preserved)
- Metadata completeness (no missing required fields)
- Metadata pass-through (D-023 — nothing lost from upstream)
- Referential integrity (all IDs resolve)
- Boundary contract compliance (output matches downstream's input contract)

**How to read results:** A 5a failure is always a bug. There's no ambiguity — either the schema matches or it doesn't. The question is: is it a code bug (Claude Code fix) or a contract bug (SPEC fix)?

### 5b — LLM-Worker Quality
These test whether the LLM calls INSIDE the engine produce correct results.

**What they test:**
- Classification accuracy (e.g., did the LLM correctly identify the science as nahw?)
- Extraction accuracy (e.g., did the LLM correctly extract the author name?)
- Detection accuracy (e.g., did the LLM correctly identify text layers?)

**How to read results:** A 5b failure means the engine's LLM integration needs work. Possible causes: bad prompt, wrong model, insufficient context, or a task the LLM genuinely can't do. The fix might be prompt engineering, model selection, or redesigning the task to be more tractable.

### 5c — LLM-Evaluator Assessment
An INDEPENDENT LLM reviews the engine's complete output and judges quality.

**What they test:**
- Overall output quality (does this look like correct output for this input?)
- Error detection (does the evaluator catch issues self-validation missed?)
- Consistency (does the evaluator agree with the engine's own confidence scores?)

**How to read results:** A 5c finding might be a real error OR evaluator noise. This is why the owner spot-checks: the evaluator flags issues, the owner confirms or dismisses them.

---

## Procedure

### Step 1: Ingest Results

Read all available test output. Organize by dimension:

```
## Test Results Summary — [Engine Name] on [Fixture]

### 5a Deterministic
- Total checks: N
- Passed: N
- Failed: N
- Failures: [list with error codes]

### 5b LLM-Worker
- Tasks tested: N
- Correct: N
- Incorrect: N
- Uncertain: N
- Details: [per-task results]

### 5c LLM-Evaluator
- Items evaluated: N
- Issues flagged: N
- Severity breakdown: [critical/warning/info]
- Details: [per-item findings]
```

### Step 2: Error Categorization

For every failure or flagged issue, classify it:

| Category | Meaning | Who Fixes | Example |
|----------|---------|-----------|---------|
| ENGINE BUG | Code doesn't match SPEC | Claude Code | Schema field missing |
| LLM QUALITY | LLM call produces wrong result | Claude Code (prompt/model) | Wrong author extracted |
| SPEC GAP | SPEC doesn't address this case | kr-spec-review cycle | Unhandled input format |
| DATA ISSUE | Test fixture has problems | Owner provides better fixture | Corrupted PDF |
| UPSTREAM ERROR | Input from previous engine is wrong | Fix upstream engine first | Bad metadata from source engine |
| EVALUATOR NOISE | LLM evaluator flagged something that's actually correct | Dismiss (note for evaluator tuning) | Evaluator unfamiliar with Islamic convention |

**The critical distinction:** ENGINE BUG vs. SPEC GAP. An engine bug means the code doesn't do what the SPEC says. A SPEC gap means the SPEC doesn't say what to do. These have completely different fix paths.

### Step 3: Owner Spot-Check Assist

For Arabic content, the owner is the authority. Help them check efficiently:

**For each flagged item that requires domain judgment:**

1. Show the specific Arabic text in question
2. Show what the engine produced (classification, attribution, extraction)
3. Show what the evaluator flagged (if applicable)
4. Ask the owner a specific question: "Is ابن عقيل correctly identified as the author of this commentary?" — not "Does this look right?"

**Spot-check sampling strategy:**
- ALL critical errors get owner review
- 20% random sample of warnings
- Focus on items where 5b and 5c disagree (engine says correct, evaluator says wrong, or vice versa)

### Step 4: Aggregate Assessment

Produce the overall engine quality assessment:

```
## Engine Assessment — [Engine Name]

### Correctness Score
- Deterministic: [N/M passed] — [PASS if 100%, FAIL otherwise]
- LLM-Worker: [N/M correct] — [threshold depends on engine]
- LLM-Evaluator: [summary of findings after noise removal]

### Error Pattern Analysis
[Are there systematic errors? E.g., "The engine consistently misidentifies
multi-author works" or "Diacritics are lost in footnotes but not body text"]

### Risk Assessment for Downstream
[If this output feeds the next engine, what errors will propagate?
Which errors are tolerable and which are blocking?]

### Inter-Engine Gate Decision
Based on the evidence: is this engine's output trustworthy enough
to serve as input for the next engine?

Recommendation: PASS / CONDITIONAL PASS (with noted limitations) / FAIL (needs fixes first)
```

### Step 5: Fix Planning

For each issue that needs fixing:

```
### Fix Plan
| Priority | Issue | Category | Fix Description | Effort |
|----------|-------|----------|----------------|--------|
| 1 | Schema missing trust_score | ENGINE BUG | Add field to output | Small |
| 2 | Author extraction fails on multi-layer texts | LLM QUALITY | Redesign prompt with layer context | Medium |
| 3 | No handling for EPUB format | SPEC GAP | Needs spec-review cycle | Large |
```

### Step 6: Learning Synthesis

End with: **What did we learn?**

This is not a formality. It's the most valuable part of evaluation. Capture:

1. **About this engine:** What's harder than expected? What works surprisingly well?
2. **About LLM capabilities:** Which tasks do LLMs handle well? Which do they struggle with?
3. **About the SPEC:** Which rules were clear enough for correct implementation? Which were ambiguous?
4. **About the test fixtures:** Which fixtures exposed real issues? Which were too simple?
5. **About evaluation:** Did the LLM evaluator catch things self-validation missed? Is it worth the cost?
6. **For downstream engines:** What should the next engine's SPEC account for, given what we learned?

These learnings feed back into the plan. They may change the approach for later engines.

---

## Special: Synthesis Engine Faithfulness Check

For the synthesis engine specifically, add a **faithfulness dimension** to evaluation. This uses the RAGAS framework (industry standard for RAG evaluation):

- **Faithfulness:** Break the synthesis entry into individual claims. For each claim tagged `source_grounded` (D-040), verify it appears in the cited excerpt. Score = supported claims / total claims. Target: 1.0.
- **Context relevance:** Did the excerpting engine find the RIGHT excerpts for this topic?
- **Consistency check (SelfCheckGPT method):** Run synthesis 3 times on the same excerpts. Claims appearing in all 3 runs are high-confidence. Claims in only 1 run are likely hallucinated.

This is non-blocking for earlier engines but CRITICAL for synthesis evaluation.

---

## Anti-Patterns

**The Pass-Everything Evaluation.** If 100% of tests pass on the first run, either the tests are too easy or the fixture is too simple. Real engines processing real Arabic text always have issues. A clean first run should make you suspicious, not relieved.

**The Blame-the-LLM Escape.** When an LLM call produces wrong results, the instinct is "the LLM isn't good enough." But often the real cause is: bad prompt, insufficient context, wrong task decomposition, or a task that shouldn't be LLM-based at all. Investigate before blaming the model.

**The Fix-Without-Understanding Loop.** Claude Code fixes a failing test by changing the code until the test passes. But nobody understood WHY the test was failing. The "fix" might mask a deeper issue. Every fix must come with an explanation of the root cause.

**Ignoring Evaluator Noise.** If you dismiss too many evaluator findings as "noise," you're defeating the purpose of 5c. Track dismissal rate. If >50% of evaluator findings are noise, the evaluation prompts need redesigning, not the findings need ignoring.
