# NEXT SESSION

**Written by:** Session 2026-03-06 (Human Gate SPEC)
**Date:** 2026-03-06

## Immediate Task

Begin shared/feedback SPEC — the feedback loop infrastructure component (VISION.md §8.3). This is the next shared component in dependency order: feedback depends on human_gate (which is now complete), and the scholar interface depends on feedback.

**Definition of done — this session is complete when:**
1. shared/feedback SPEC written with all 10 sections per SPEC template
2. RESOURCES.md updated with any new tools discovered
3. Any new decisions recorded in kr_decisions.md
4. Changes committed and pushed

## Context

The human gate SPEC is complete (413 lines). It defines: checkpoint lifecycle management (create/query/resolve/expire), 18 gate types across all engines, pre-approval policy management with restricted types, bidirectional validation (structural + consistency + cross-reference), owner confidence calibration per science with 4 levels, and three transformative capabilities (gate learning/policy suggestion, review efficiency intelligence, library consistency checking).

Remaining shared component SPECs needed before implementation:
- **shared/feedback** — feedback loop infrastructure: correction storage, pattern analysis, regression testing coordination (VISION.md §8.3). The human gate SPEC §3 guarantees a complete audit trail. The feedback component consumes this trail plus the owner's corrections to detect systematic patterns and trigger engine rule updates. No existing code.
- **shared/user_model** — persistent user state (D-017). No existing code.
- **shared/scholar_authority** — canonical scholar identities (D-025). No existing code beyond what the source engine references.
- **interface/scholar/** — user-facing intelligence layer (D-016). No existing code.

After all shared component SPECs: the first SCIENCE.md (إملاء for Milestone 1).

## Files to Read — IN THIS ORDER

1. `VISION.md` §8.3 (Feedback Loops and Self-Improvement) — use `python3 scripts/extract_vision_sections.py 8` (already extracted above, §8.3 is the relevant subsection)
2. Engine SPECs that reference feedback: grep for "feedback" or "correction" or "DSPy" or "prompt optimization" in all engine SPECs. Key sections: each engine's §5 (quality), §8 (configuration for DSPy baselines).
3. `shared/human_gate/SPEC.md` — just completed; reference for how the audit trail feeds into feedback analysis
4. `shared/human_gate/src/human_gate.py` lines 400-600 — the ABD-era pattern detection code (reference for feedback component's pattern analysis approach)
5. `reference/RESOURCES.md` — existing tool research, particularly DSPy
6. `reference/DOMAIN.md` — correction cascade section (~lines 690-700)

## Decisions Needed

- Should the feedback component own DSPy prompt optimization, or should each engine own its own prompt optimization with the feedback component providing correction data? Likely answer: the feedback component provides structured correction data and pattern analysis; each engine owns its own DSPy optimization using that data. The feedback component does not know what prompts look like.
- What constitutes a "systemic pattern" (VISION.md §8.3)? What threshold of occurrences? The feedback component SPEC must define this precisely.

## Pending Owner Questions

None.

## What This Session Did

Completed shared/human_gate SPEC (413 lines, all 10 sections). Key design decisions: the human gate manages checkpoint state while the scholar interface manages presentation (clean separation of concerns); checkpoints stored as JSON files with pending/resolved separation; 18 gate types registered across all engines; 4 gate types restricted from pre-approval (tax_evolution_proposal, tax_rollback, source_trust_evaluation, gate_policy_suggestion); bidirectional validation with three categories (structural, consistency, cross-reference) that warn but never block; owner confidence calibration with 4 levels affecting policy thresholds. Three transformative capabilities: gate learning suggests policies from approval patterns, review efficiency intelligence produces behavioral metadata for the scholar interface, and library consistency checking performs deep semantic validation of owner decisions. Updated CLAUDE.md, RESOURCES.md, STATUS.md.

## New Decisions

None — the human gate SPEC does not introduce new architectural decisions beyond what VISION.md §9 and existing engine SPECs already established. The design choices (state management vs. presentation, file-based storage, restricted gate types, non-blocking validation) are component-internal specifications, not project-level architectural decisions.
