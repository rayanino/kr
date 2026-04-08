# Passaging Engine — محرك التقطيع

**Responsibility:** Segmenting normalized content into passages for downstream processing.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Third engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (1,037 lines — the authoritative specification)
2. This engine's `contracts.py` (556 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. Input boundary: normalized package from normalization engine
6. Output boundary: passage stream → atomization engine

## Current State

**SPEC:** 1,037 lines. Has been through multiple refinement passes but has 25 HIGH-severity defects (highest in the repo). Needs substantive Step 1 work, not just core extraction. §4.A requires rewriting for core-only focus and defect resolution.

**Contracts:** 556 lines. Imports from normalization contracts (the only cross-engine import currently).

**Code:** 22 pre-protocol stub files, 544 total lines. Includes 6 strategy variants (prose, verse, Q&A, masala, dictionary, commentary) — only prose and commentary-with-layers are core. Deferred strategies must be pruned or disabled during Step 3.

**Tests:** None.

## What This Engine Does (Core Only)

- Receives normalized packages (manifest.json + content.jsonl)
- Selects strategy based on structural_format: prose or commentary-with-layers
- Splits text into passages targeting 200-800 Arabic words
- Preserves heading hierarchy, page boundaries, footnote associations
- Aligns commentary spans to base text segments (for multi-layer texts)
- Produces passage stream consumed by atomization engine

## Claude Code Behaviour Guidelines

- **Ownership, not deflection:** When you encounter an issue, take responsibility and work towards a solution. Don't say "not caused by my changes" or "pre-existing issue." Don't give up with "known limitation" or defer to "future work." Fix it now.
- **Persistence through obstacles:** Don't stop at the first problem. Don't declare "good stopping point" or "natural checkpoint." Keep pushing until you have a complete, verified solution.
- **Initiative over permission-seeking:** If you have the knowledge and capability to solve a problem, act. Don't ask "should I continue?" or "want me to keep going?" Take initiative and drive towards the solution.
- **Plan before acting:** For multi-step work, plan which files to read, in what order, which tools to use, and what the expected outcome is — before touching anything.
- **Convention recall:** Always re-read and apply project-specific conventions from CLAUDE.md files. Don't rely on memory of what they say.
- **Self-correction loops:** Catch your own mistakes by applying reasoning loops and self-checks. Fix errors before committing or asking for help.
- **Verify, don't assume:** After reaching a conclusion or making a change, verify it against the actual state of the codebase. A conclusion you haven't verified is a guess. Run the test, read the output, check the file.
- **Trace root causes:** When something fails, trace the full causal chain. Don't patch symptoms — find and fix the underlying cause. A surface fix hides the real bug for later.

### Tool Use

- **Research-first, never edit-first:** Before using any tool, research the context and requirements. Read the relevant code, SPEC, and contracts before making changes. Understand before you act.
- **Surgical edits over rewrites:** Make targeted, minimal changes. Never rewrite whole files or make large sweeping changes when a focused edit achieves the goal.
- **Reasoning loops are mandatory:** Apply reasoning loops frequently. Don't skip them to save tokens. The cost of a wrong action far exceeds the cost of thinking.

### Thinking Depth

- Always apply the **highest level of thinking depth**. Shallow thinking leads to the cheapest available action, which is rarely the correct one. Spending more tokens on reasoning produces dramatically better outcomes.
- **Never reason from assumptions.** Always reason from actual data — read and understand the actual code, SPEC, or documentation before making decisions. Assumptions compound into errors.
