---
name: kr-core-extract
description: Separates core engine architecture from extension features in a KR engine SPEC. Activate when starting work on a new engine, when asked to classify core vs deferred, or when rewriting a SPEC for core-only focus. Produces a classification table for owner review, then rewrites the SPEC with exhaustive depth on core only.
---

# KR Core Extract — استخلاص الجوهر

You are identifying the fundamental architecture of a KR engine — the minimum set of behaviors without which the engine would not fulfill its purpose in the pipeline. Everything else is an extension that builds on this core.

This matters because the project builds engines in two stages. Stage 1 builds all 7 engine cores into a narrow but reliable pipeline. Stage 2 adds extensions on proven foundations. A SPEC that mixes core architecture with extension features dilutes the depth that core behaviors need and wastes effort on features that depend on an unproven foundation.

---

## Two-Part Workflow

This skill runs in two distinct parts. Do not combine them — the owner reviews Part 1 output before Part 2 begins.

### Part 1: Classify

Read the full SPEC. For every capability, behavior, feature, and design element, produce a classification table.

**How to decide CORE vs DEFERRED:**

The core is the engine's identity. Ask: "If I removed this behavior, would the engine still do its fundamental job?" If no, it's core. If yes, it's an extension.

A second test: "Does this behavior depend on the core working first?" If it builds on top of basic functionality (like citation network discovery building on top of basic metadata extraction), it's an extension.

For the source engine as a concrete example: freezing a file is core (without it, there's no immutable source). Tahqiq apparatus fingerprinting is an extension (it enriches metadata, but the engine works without it). Shamela HTML intake is core (it's the primary test format). Audio transcription is an extension (it adds a new input path but doesn't affect the core processing logic).

Format constraints for supported input formats: identify the minimum set needed to validate the core. Usually 2 formats — one structured (like Shamela HTML), one simple (like plain text). All others are deferred.

**Output format:**

```
## [Engine Name] — Core vs Deferred Classification

### §[section] — [Title]

| Capability | Classification | Reason |
|-----------|---------------|--------|
| [specific behavior] | CORE | [why it's fundamental] |
| [specific behavior] | DEFERRED | [what it depends on] |
```

Organize by SPEC section. Cover everything — do not skip features just because they seem obviously core or obviously deferred. The owner needs to see every judgment call to catch mistakes.

After the table, add a summary:

```
## Summary
- Core capabilities: [count]
- Deferred capabilities: [count]
- Core input formats: [list the 2-3 formats]
- Deferred input formats: [list]

## Items I'm Uncertain About
[List any where the classification could go either way, with your reasoning for each side]
```

**Stop here.** Present the classification to the owner. Wait for corrections before proceeding.

---

### Part 2: Rewrite

After the owner approves (and corrects) the classification, rewrite the SPEC.

**For core items:** Write with exhaustive depth. Every data structure — exact fields, types, constraints, and why each field exists. Every LLM call — exact input, prompt structure, expected output format, model recommendation, fallback behavior. Every error path — code, severity, recovery action. Every decision point — exact threshold, exact logic. The goal: Claude Code reads this and has zero questions.

**For deferred items:** Replace the detailed content with a single line:

```
[DEFERRED TO STAGE 2] — [one-sentence description of what this will do]
```

Preserve the section structure so deferred items remain visible as placeholders. Future sessions know they exist and where they belong.

**Quality check before finishing:** Read the rewritten SPEC as if you were Claude Code about to implement it. For each core rule, verify you could write a function signature and pseudocode from the description alone. If any rule is too vague for that, add detail until it isn't.

---

## Engine-Specific Guidance

The classification question is slightly different for each engine:

**Source engine:** Core = format detection + metadata extraction + metadata inference + freezing + deduplication + registration + trust evaluation. On the minimum set of formats. Deferred = additional formats, citation discovery, advanced scholar matching, source difficulty prediction.

**Normalization engine:** Core = defining exactly what the normalized structure looks like + transforming the core source formats into that structure. Deferred = additional format normalizers, advanced layer detection, content census.

**Passaging engine:** Core = dividing normalized text into coherent passages using the simplest reliable strategy (heading-based for structured text, fixed-size for unstructured). Deferred = advanced strategies (commentary alignment, argument detection, quality prediction).

**Atomization engine:** Core = breaking passages into atomic scholarly units with basic function labels. Deferred = advanced rhetorical analysis, cross-reference detection, distribution analytics.

**Excerpting engine:** Core = extracting self-contained scholarly claims with attribution. Deferred = implicit reference resolution, cross-text linking, advanced self-containment analysis.

**Taxonomy engine:** Core = placing excerpts into the science tree with basic topic matching. Deferred = tree evolution, coverage analysis, prerequisite chain detection.

**Synthesis engine:** Core = producing a grounded knowledge entry from placed excerpts. Deferred = multi-model panel evaluation, consistency oracle, advanced narrative generation.
