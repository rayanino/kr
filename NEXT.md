# NEXT SESSION

**Written by:** Session 2026-03-06 (Consensus SPEC)
**Date:** 2026-03-06

## Immediate Task

Begin shared/validation SPEC — the validation component that provides algorithmic checks (Layer 2 of the quality architecture). Or, if the architect judges human_gate or feedback is higher priority based on implementation dependencies, start with that instead.

**Definition of done — this session is complete when:**
1. One shared component SPEC written with all 10 sections per SPEC template
2. RESOURCES.md updated with any new tools discovered during research
3. Any new decisions recorded in kr_decisions.md
4. Changes committed and pushed

## Context

The consensus SPEC is complete (405 lines, D-041). It defines the multi-model agreement service using LiteLLM + Instructor with parallel independent comparison, three comparison strategies (categorical, numerical, structured), full audit logging, and two transformative capabilities (calibration intelligence, difficulty estimation).

Remaining shared component SPECs needed before implementation can begin:
- **shared/validation** — algorithmic validation tools: schema validation, structural integrity checks (VISION.md §8.1 Layer 2). Used by all engines for output self-validation. Existing ABD code: `shared/validation/src/cross_validate.py`, `shared/validation/src/run_all_validations.py`.
- **shared/human_gate** — human approval gates for irreversible library changes (VISION.md §9). Existing ABD code: `shared/human_gate/src/human_gate.py`.
- **shared/feedback** — feedback loop infrastructure: correction storage, pattern analysis, regression testing coordination (VISION.md §8.3). Spans all engines with human gates. No existing code.
- **shared/user_model** — persistent user state (D-017). No existing code.
- **shared/scholar_authority** — canonical scholar identities (D-025). No existing code beyond what the source engine references.
- **interface/scholar/** — user-facing intelligence layer (D-016). No existing code.

After all shared component SPECs: the first SCIENCE.md (إملاء for Milestone 1).

## Files to Read — IN THIS ORDER

1. `shared/consensus/SPEC.md` — just completed; reference for shared component SPEC quality level
2. Whichever shared component is chosen: its `CLAUDE.md` and any existing `src/` code
3. Engine SPECs that reference the chosen component (grep for its mentions)
4. `VISION.md` §8 (quality architecture), §9 (human gates) — use extract_vision_sections.py
5. `reference/RESOURCES.md` — existing tool research

## Decisions Needed

- Which shared component to tackle next (validation, human_gate, or feedback)? Consider implementation dependency order: validation is referenced by every engine's §5; human_gate is referenced by every engine that has gates; feedback depends on human_gate.

## Pending Owner Questions

None.

## What This Session Did

Completed shared/consensus/SPEC.md (405 lines, all 10 sections). Key design: LiteLLM + Instructor for parallel independent model comparison (D-041), three comparison strategies (categorical, numerical, structured), five verdict types, complete audit logging. Two transformative capabilities: consensus calibration intelligence (model agreement profiling + drift detection) and decision difficulty estimation. Updated RESOURCES.md with consensus-specific research findings. Updated STATUS.md and consensus CLAUDE.md.

## New Decisions

D-041: Consensus technology stack — LiteLLM + Instructor with parallel independent comparison.
