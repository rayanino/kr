# NEXT — Engine Factory Design Session

## Current position: Source engine COMPLETE → Design the autonomous build system
## What to do: Discuss and improve reference/ENGINE_FACTORY_PLAN.md
## Context: Source engine done (reference/SOURCE_ENGINE_COMPLETION.md). 6 engines remaining. The plan exists but needs critical review and refinement before implementation.
## Owner action needed: YES — This is a discussion session (Claude Chat + owner)

**CRITICAL CONTEXT:** The owner is an Islamic studies STUDENT who has NOT
studied Islamic texts yet. KR exists to CREATE that study environment.
The owner CANNOT validate domain correctness. All "human gate" and "owner
review" steps mean the owner triggers AI-assisted research (via Oracle or
Claude Chat), NOT that the owner independently evaluates scholarly metadata.
The ENGINE_FACTORY_PLAN.md was written with this understanding (see the
Oracle section and three-tier gate model).

## Key documents to read
- `reference/ENGINE_FACTORY_PLAN.md` — the current plan (~800 lines)
- `reference/SOURCE_ENGINE_COMPLETION.md` — what we just finished
- `KNOWLEDGE_INTEGRITY.md` — corruption threats the factory must prevent
- `RESULT_PRESERVATION.md` — how results feed downstream

## Questions for the discussion
1. Is the multi-agent architecture (Builder/Reviewer/Verifier/Oracle) the
   right approach, or is it over-engineered?
2. Should we start with Option A (Claude Code native) or go straight to
   Option B (OpenClaw)?
3. Is the Decision Playbook the right way to transfer Claude Chat's
   accumulated knowledge to the Oracle?
4. Are the quality gates realistic or will they create bottlenecks?
5. What's the minimum viable factory — what can we cut without sacrificing
   correctness?

## Budget
- Spent: €30.60
- Remaining: ~€69.40
