# consensus — Multi-Model Agreement Component

Shared service called by engines that need independent LLM verification of high-stakes decisions.

## What It Does
Accepts a consensus request (prompt + schema + comparison strategy), dispatches to two LLMs in parallel via LiteLLM, compares structured responses via Instructor/Pydantic, returns a verdict (AGREE/DISAGREE/PARTIAL_AGREE/SINGLE_MODEL/FAILURE) with full audit trail.

## Consumers
- Source engine: author identification, work matching (categorical)
- Excerpting engine: self-containment (numerical, threshold 0.2), school attribution (categorical)
- Taxonomy engine: ambiguous placement 0.5–0.8 range (categorical)
- Atomization engine: explicitly NOT a consumer (D-035)

## Key Design Choices
- LiteLLM SDK (not proxy) for provider abstraction — one integration point for all LLM providers
- Instructor for structured output extraction with automatic schema validation retries
- Async parallel dispatch via asyncio.gather — both models called simultaneously
- Provider diversity mandatory — two models must be from different providers
- Three comparison strategies: categorical, numerical, structured
- Complete audit logging of every consensus round

## External Dependencies
LiteLLM, Instructor, Pydantic, PyYAML, asyncio (stdlib)

## Current State
ABD-era code (1749L consensus.py) — to be replaced entirely. Arabic text utils to be extracted to shared/arabic_text/. Everything in SPEC is [NOT YET IMPLEMENTED].

## Config
`config/consensus.yaml` — model roster, per-decision-type overrides, per-science hooks.

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation

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
