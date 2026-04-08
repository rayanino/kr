# Shared Infrastructure

Cross-engine components used by two or more engines. Code belongs here only when it serves multiple engines.

## Process

Follow `skills/shared/ENGINE_PROTOCOL.md`. Shared components are bootstrapped during the source engine's Step 3 (BUILD) — the source engine builds minimum viable implementations. Later engines extend as needed.

## Components

- **consensus/** — Multi-model LLM agreement (Instructor `from_provider()`). Used by source, atomization, excerpting, taxonomy.
- **validation/** — Schema validation, structural integrity checks. Used by all engines.
- **human_gate/** — Owner approval gates for irreversible library changes. Used by all engines.
- **feedback/** — Correction storage, pattern analysis, regression coordination. Spans all engines.
- **user_model/** — Owner's study history, knowledge gaps, preferences. Used by scholar interface (Stage 2).
- **scholar_authority/** — Canonical scholar identities, biographical data, teacher-student graph. Used by source, excerpting, taxonomy, synthesis.

## Current State

Each component has a SPEC.md (400-460 lines) but no implementation code and no contracts.py. The tracer bullet (Step 0) creates trivial stubs. The source engine's Step 3 builds minimum viable versions (see ENGINE_PROTOCOL.md engine-specific notes for method signatures). Later engines extend what exists.

Four engines (source, normalization, passaging, atomization) have pre-protocol src/ stubs — these are placeholder code from before ENGINE_PROTOCOL.md existed. The tracer bullet reconciles and uses them as starting points.

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
