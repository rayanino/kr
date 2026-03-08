---
name: kr-evaluate
description: Reviews engine test results and categorizes every finding. Activate when reviewing test output, checking engine quality, or when the owner says "evaluate results", "check output", or "review tests." Distinguishes core gaps from extension opportunities and documents lessons learned.
---

# KR Evaluate — تقييم النتائج

You are reviewing test results from a KR engine with the owner. Your job: categorize every finding, distinguish core gaps from extensions, help the owner spot-check Arabic output, and determine whether this engine is reliable enough to feed the next one.

---

## The Three Test Dimensions

### 5a — Deterministic Checks
Automated pass/fail tests. Schema conformance, Arabic text integrity (diacritics preserved), metadata completeness, D-023 pass-through, referential integrity, boundary contract compliance.

A 5a failure is always a bug — either in the code (doesn't match SPEC) or in the contract (SPEC is wrong).

### 5b — LLM-Worker Quality
Tests whether the LLM calls inside the engine produce correct results. Classification accuracy, extraction accuracy, detection accuracy.

A 5b failure means the engine's LLM integration needs work — bad prompt, wrong model, insufficient context, or a task the LLM can't do reliably.

### 5c — LLM-Evaluator Assessment
An independent LLM (different model family) reviews the engine's complete output. Catches errors that self-validation missed.

A 5c finding might be a real error or evaluator noise. The owner spot-checks to confirm or dismiss.

---

## Procedure

### Step 1: Ingest and Summarize

Read all test output. Organize by dimension:

```
## Test Results — [Engine Name] on [Fixture]

### 5a Deterministic: [N/M passed]
Failures: [list with error codes]

### 5b LLM-Worker: [N/M correct]
Details: [per-task results]

### 5c LLM-Evaluator: [N issues flagged]
Details: [per-item findings]
```

### Step 2: Categorize Every Finding

This is the most important step. Each finding gets exactly one category:

| Category | What It Means | Who Fixes |
|----------|--------------|-----------|
| **CORE GAP** | Something fundamental is wrong or missing. The pipeline would produce corrupt or incomplete output without a fix. | Fix before moving to next engine. May require SPEC change. |
| **ENGINE BUG** | Code doesn't match the SPEC. | Claude Code fixes it. |
| **LLM QUALITY** | LLM call produces wrong results. | Prompt redesign, model change, or task restructuring. |
| **DATA ISSUE** | Test fixture has problems. | Owner provides better fixture. |
| **UPSTREAM ERROR** | Input from the previous engine is wrong. | Fix upstream engine first. |
| **EXTENSION OPPORTUNITY** | Something that would improve the engine but isn't needed for the core pipeline to work. | Document for Stage 2. |
| **LESSON LEARNED** | An insight about LLM reliability, data structures, testing, or architecture. | Document in LESSONS.md. |
| **EVALUATOR NOISE** | LLM evaluator flagged something that's actually correct. | Dismiss, note for evaluator tuning. |

The critical distinctions:

**CORE GAP vs EXTENSION OPPORTUNITY.** "The engine doesn't capture the muhaqiq's name, but downstream engines need it for attribution" is a core gap. "The engine doesn't detect citation networks between sources" is an extension opportunity. The test: would the pipeline produce wrong or incomplete knowledge entries without this? If yes, core gap. If no, extension.

**ENGINE BUG vs SPEC GAP (= CORE GAP).** An engine bug means the code doesn't do what the SPEC says. A SPEC gap means the SPEC doesn't say what to do. If the SPEC is silent on a case the engine encounters, that's a core gap — the SPEC needs updating, not just the code.

### Step 3: Owner Spot-Check

For Arabic content, the owner is the authority. For each flagged item requiring domain judgment:

1. Show the specific Arabic text
2. Show what the engine produced
3. Ask a specific question: "Is ابن عقيل correctly identified as the author of this commentary?" — not "Does this look right?"

Sampling: all critical findings get owner review. 20% random sample of warnings. Focus on items where 5b and 5c disagree.

### Step 4: Aggregate Assessment

```
## Engine Assessment — [Engine Name]

### Reliability
- 5a: [N/M passed] — [PASS if 100%]
- 5b: [accuracy %] — [PASS if ≥90%]
- 5c: [findings after noise removal]

### Core Gaps Found
[List each with severity and fix plan]

### Extension Opportunities
[List each — these go in LESSONS.md for Stage 2]

### Lessons Learned
[Insights about LLM reliability, data structures, testing]

### Verdict
PASS — engine is reliable enough for the next engine
CONDITIONAL PASS — reliable with noted limitations
FAIL — core gaps must be fixed first
```

### Step 5: Document for LESSONS.md

Every evaluation session contributes to the engine's LESSONS.md:

- What LLM tasks worked reliably and what didn't
- What data structures worked and what needed changing
- What testing approaches caught real issues
- Architectural decisions that affect downstream engines
- Extension opportunities identified for Stage 2
- What the next engine should account for

These lessons accumulate across engines. By engine 7, they form a comprehensive body of evidence about the pipeline.

---

## Synthesis Engine: Additional Checks

For the synthesis engine only, add faithfulness evaluation:

- Break the entry into individual claims. For each claim tagged as source-grounded, verify it appears in the cited excerpt.
- Run synthesis 3 times on the same excerpts. Claims in all 3 runs are high-confidence. Claims in only 1 run are likely hallucinated.

This is non-blocking for earlier engines but critical for synthesis.

---

## Common Mistakes to Avoid

**The pass-everything evaluation.** If 100% pass on the first run, the tests are probably too easy or the fixture too simple. Real Arabic text processing always has issues.

**The blame-the-LLM escape.** When an LLM call produces wrong results, often the real cause is a bad prompt, insufficient context, or wrong task decomposition — not the model itself. Investigate before blaming.

**The fix-without-understanding loop.** Every fix needs a root cause explanation. Changing code until a test passes, without understanding why it was failing, masks deeper issues.

**Over-dismissing evaluator findings.** If you dismiss >50% of 5c findings as noise, the evaluation prompts need redesigning.
