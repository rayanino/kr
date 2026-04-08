# Atomization Engine — محرك التذرية

**Responsibility:** Breaking passages into typed atoms — the smallest indivisible text units — classified by structural type and scholarly function.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Fourth engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (1,205 lines — the authoritative specification)
2. This engine's `contracts.py` (676 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. Input boundary: passage stream from passaging engine
6. Output boundary: atom stream → excerpting engine

## Current State

**SPEC:** 1,205 lines. Has been through PRECISION (partially). Has 9 HIGH-severity defects. Needs core extraction and defect resolution at Step 1.

**Contracts:** 676 lines.

**Code:** 26 pre-protocol stub files, 866 total lines. Most extensive stubs in the repo. Includes advanced features (fingerprinting, distribution analytics, rhetorical analysis) that are deferred. Must be pruned to core during Step 3.

**Tests:** None.

## What This Engine Does (Core Only)

- Receives passage stream from passaging engine
- Segments each passage into non-overlapping atoms via a multi-phase pipeline
- Classifies each atom on two dimensions: structural type + scholarly function
- The LLM does the primary classification work — Step 2 research is critical to verify LLM accuracy on scholarly function classification before building
- Produces atom stream consumed by excerpting engine

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
