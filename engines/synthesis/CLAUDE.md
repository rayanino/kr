# Synthesis Engine — محرك التركيب

**Responsibility:** Generating encyclopedic scholarly entries from placed excerpts. This is the engine that produces the knowledge products the owner actually reads.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Seventh and final engine in pipeline order.

## Required Reading

1. This engine's `SPEC.md` (918 lines — the authoritative specification)
2. This engine's `contracts.py` (565 lines — Pydantic schemas)
3. `skills/shared/ENGINE_PROTOCOL.md` — the development process
4. `reference/TESTING_FRAMEWORK.md` — test architecture
5. `reference/ENTRY_EXAMPLE.md` — THE quality target. Shows what a finished entry looks like.
6. `reference/DOMAIN.md` — scholarly methodology concepts
7. Input boundary: placed excerpts + tree structure from taxonomy engine
8. Output boundary: entries → Scholar Interface (Stage 2)

## Current State

**SPEC:** 918 lines. Has been through 3 refinement stages (CREATIVE, PRECISION, HARDENING). Has 6 HIGH-severity defects. Core extraction needed — full scholarly narrative quality is the target even for v0.0.1, but advanced features (staleness detection, versioning, regeneration) are deferred.

**Contracts:** 565 lines.

**Code:** No implementation code. Only an empty __init__.py.

**Tests:** None.

## What This Engine Does (Core Only)

- Compiles placed excerpts into scholarly entries with temporal ordering, school attribution, and traceability (all claims to excerpt IDs)
- Every claim tagged with grounding_type: source_grounded | metadata_derived | analytical (D-040)
- Cross-provider entailment verification: the model that generates cannot also verify (T-5 prevention)
- Quality bar: structured compilation with narrative, not flat bullet-point compilation
- Builds a minimal entry viewer (scripts/render_entry.py) at Step 4 for owner review

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
