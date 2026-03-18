---
name: kr-core-extract
description: Separates core engine architecture from extension features in a KR engine SPEC. Activate when starting work on a new engine, when asked to classify core vs deferred, or when rewriting a SPEC for core-only focus. Produces a classification table with extension hooks for owner review, then rewrites the SPEC focused on core only.
---

# KR Core Extract — استخلاص الجوهر

You are identifying the fundamental architecture of a KR engine — the minimum set of behaviors without which the engine would not fulfill its purpose in the pipeline. Everything else is an extension that builds on this core.

This matters because the project builds engines in two stages. Stage 1 builds all 7 engine cores into a narrow but reliable pipeline. Stage 2 adds extensions on proven foundations. A SPEC that mixes core architecture with extension features dilutes the depth that core behaviors need and wastes effort on features that depend on an unproven foundation.

---

## Classification Methodology: Bottom-Up First, Top-Down Verify

**CRITICAL: Classify bottom-up, then verify top-down. Never classify by reading a capability description and making a gut call.**

### Bottom-up (primary): What does the downstream engine require?

1. Read the DOWNSTREAM engine's input contract first (the engine's SPEC.md §2 and contracts.py).
2. List every field the downstream engine reads from this engine's output.
3. For each field: is it `Optional` with a graceful-absence fallback ("if absent, use defaults"), or is it required?
4. For required fields: trace back to which §4 capability PRODUCES that field. That capability is a core candidate.
5. For optional fields with graceful-absence: the producing capability is a deferral candidate.

This catches the §4.B.8 pattern: a capability classified as "transformative" that actually produces a field the downstream engine uses as a "primary signal." Reading the downstream consumer first makes this obvious; reading the capability description first hides it.

### Top-down (verification): Would the engine still work?

After the bottom-up pass, verify each classification with two questions:
1. "If I removed this capability, would the engine still fulfill its fundamental purpose?" If no → CORE.
2. "Does this capability depend on the core working first?" If yes → it's an extension that builds on core → DEFERRED.

### Implementation cost check (tiebreaker)

For capabilities at the core/deferred boundary, check: how much does this cost to implement? A capability that's 50 lines of pattern matching (like §4.B.8 boundary continuity) should be core even if the downstream engine has a fallback. A capability that requires an LLM call per page with per-science calibration (like §4.B.10 discourse flow) is expensive and should be deferred even if the downstream engine uses it.

The tiebreaker is NOT "is this useful?" (everything in the SPEC is useful). The tiebreaker is: "Does the implementation cost justify deferral, given that the downstream engine has a fallback?"

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

## Extension Hooks
For each deferred capability, state what the core must NOT assume:
| Deferred Capability | Core Must Not Assume |
|---------------------|---------------------|
| [capability] | [architectural constraint to preserve the extension path] |

## Items I'm Uncertain About
[List any where the classification could go either way, with your reasoning for each side]
```

**BEFORE presenting the classification:** Run the quality pipeline. Verify every "DEFERRED" classification against the downstream engine's input contract — does the downstream engine truly have a fallback for this field? Open the downstream contracts.py and check the field's type. If it's not `Optional`, it's not deferrable. This is the adversarial check that catches the §4.B.8 pattern.

**Stop here.** Present the classification to the owner. Wait for corrections before proceeding.

---

### Part 2: Rewrite

After the owner approves (and corrects) the classification, rewrite the SPEC.

**First: assess SPEC maturity.** Not all SPECs need the same depth of rewrite.

- **Mature SPECs** (normalization, atomization, excerpting, taxonomy, synthesis — those that have been through PRECISION, HARDENING, or IMPL_PREP passes): Core extraction is surgical. Move §4.B to deferred with extension hooks. Verify §4.A is implementation-ready. Do NOT rewrite refined §4.A content — that work has already been done. Fix specific defects if found, but preserve the existing quality.
- **Immature SPECs** (source, passaging — those with known defects or vague §4.A content): Rewrite §4.A to significant-decisions depth as described below.

**For core items:** Write with depth sufficient for implementation. Every data structure — exact fields, types, constraints, and why each field exists. Every LLM call — input, prompt strategy, expected output format, model recommendation, fallback behavior. Every error path — code, severity, recovery action. Every decision point — threshold, logic. Where exact thresholds or prompt templates are uncertain, mark them as `[ASSUMPTION — NEEDS STEP 2 TESTING]` rather than guessing. The goal: Claude Code can build the right architecture with zero questions about *what* to build. Step 4 (TEST) will reveal where more edge case detail is needed — the SPEC deepens iteratively.

**For deferred items:** Replace the detailed content with two lines:

```
[DEFERRED TO STAGE 2] — [one-sentence description of what this will do]
[EXTENSION HOOK] — Core must not assume [constraint], to preserve this extension path.
```

Preserve the section structure so deferred items remain visible as placeholders. Future sessions know they exist and where they belong.

**Quality check before finishing:** Read the rewritten SPEC as if you were Claude Code about to implement it. For each core rule, verify you know *what* to build — the data structures, the processing logic, the error handling. Where a rule is too vague to implement, add detail. Where a threshold or prompt template is uncertain, mark it as `[ASSUMPTION — NEEDS STEP 2 TESTING]` rather than inventing a precise value.

---

## Engine-Specific Guidance

The classification question is slightly different for each engine:

**Source engine:** Core = format detection + metadata extraction + metadata inference + freezing + deduplication + registration + trust evaluation (simple 3-tier: verified/flagged/unknown). On the minimum set of formats. Deferred = additional formats, citation discovery, advanced scholar matching, source difficulty prediction, elaborate trust scoring algorithm.

**Normalization engine:** Core = defining exactly what the normalized structure looks like + transforming the core source formats into that structure + basic layer detection (matn vs sharh vs hashiyah) using format-specific CSS classes. Basic layer detection is CORE because every downstream engine depends on knowing which text layer an atom/excerpt comes from. Deferred = additional format normalizers, advanced layer detection (inferring layers when markup is absent), content census.

**Passaging engine:** Core = dividing normalized text into coherent passages using the simplest reliable strategy (heading-based for structured text, fixed-size for unstructured). Core structural formats: prose and commentary-with-layers. Deferred = verse and dictionary formats, advanced strategies (commentary alignment, argument detection, quality prediction). Fast-track candidate — light spec work if §4.A is mature.

**Atomization engine:** Core = breaking passages into atomic scholarly units with basic function labels. Deferred = advanced rhetorical analysis, cross-reference detection, distribution analytics. Note: this engine's Step 2 research is critical — if LLM classification accuracy is below 70%, the approach may need redesign.

**Excerpting engine:** Core = extracting self-contained scholarly claims with attribution. Deferred = implicit reference resolution, cross-text linking, advanced self-containment analysis. Note: self-containment evaluation is the highest-risk LLM task in the pipeline.

**Taxonomy engine:** Core = placing excerpts into the science tree with basic topic matching. Deferred = tree evolution, coverage analysis, prerequisite chain detection. **Prerequisite:** The engine needs a parsed science tree data structure before Step 3 can begin. The owner must define at minimum the nahw (grammar) tree structure; the architect translates it into the engine's format.

**Synthesis engine:** Core = producing a grounded knowledge entry from placed excerpts with temporal ordering, school attribution, and full traceability (every claim tagged with excerpt IDs). Core quality bar: structured compilation, NOT the flat compilation shown as unacceptable in ENTRY_EXAMPLE.md. Deferred = multi-model panel evaluation, consistency oracle, full narrative generation (intellectual genealogy, "why scholars disagreed", "what to read next").
