# NEXT SESSION

**Written by:** Session 2026-03-06 (Feedback SPEC)
**Date:** 2026-03-06

## Immediate Task

Begin shared/user_model SPEC — the persistent user state component (D-017). This is the next shared component in dependency order: the scholar interface depends heavily on the user model for personalization.

**Definition of done — this session is complete when:**
1. shared/user_model SPEC written with all 10 sections per SPEC template
2. RESOURCES.md updated with any new tools discovered
3. Any new decisions recorded in kr_decisions.md
4. Changes committed and pushed

## Context

The feedback SPEC is complete (461+ lines). It defines: correction recording from human gate resolutions and direct owner corrections, pattern analysis with 7 systemic pattern types (type_concentration, science_concentration, source_concentration, model_concentration, confidence_miscalibration, recurring_pair, correction_cascade_needed), DSPy-compatible training data management with engine registration, regression test coordination with gold baseline management and model change monitoring, and three transformative capabilities (correction cascade intelligence, cross-engine root cause analysis, learning velocity tracking). Key design decision: the feedback component provides structured correction data; each engine owns its own DSPy prompt optimization.

Remaining shared component SPECs needed before implementation:
- **shared/user_model** — persistent user state (D-017). Tracks: study history, demonstrated knowledge, knowledge gaps, current focus, preferences, bookmarks/annotations. Read by scholar interface for personalization. Written to by scholar interface (interactions) and processing engines (new content alerts). No existing code.
- **shared/scholar_authority** — canonical scholar identities (D-025). No existing code beyond what the source engine references.
- **interface/scholar/** — user-facing intelligence layer (D-016). No existing code.

After all shared component SPECs: the first SCIENCE.md (إملاء for Milestone 1).

## Files to Read — IN THIS ORDER

1. `reference/DOMAIN.md` — particularly the "User model must" section (~line 710+) and the "Core Identity" section for how KR IS the user's knowledge
2. `reference/USER_SCENARIOS.md` — all scenarios involve user state (study history, knowledge gaps, current focus). The user model serves ALL scenarios.
3. `VISION.md` — search for user model references. Use `python3 scripts/extract_vision_sections.py 6` for synthesis (entries track what user has studied), and `python3 scripts/extract_vision_sections.py 9` for human gates (confidence calibration is user state). Also grep for "user model", "study history", "knowledge gap", "spaced repetition".
4. `shared/user_model/CLAUDE.md` — existing orientation file
5. `engines/synthesis/SPEC.md` — the synthesis engine produces entries that the user model tracks consumption of
6. `shared/human_gate/SPEC.md` §4.A.4 — owner confidence calibration per science, which IS user model state that the human gate currently stores independently (should it be part of the user_model instead?)
7. `reference/RESOURCES.md` — check for spaced repetition, knowledge graph, and personalization tools

## Decisions Needed

- Should owner confidence calibration (currently in human gate as confidence.json) be moved to the user model? Argument for: it's user state, and the user model is the canonical place for user state. Argument against: it's gate-specific behavior, and keeping it in the human gate avoids coupling. Likely answer: the user model owns the data; the human gate reads it. This may require a minor update to the human gate SPEC.
- What constitutes "demonstrated knowledge" vs. "has seen"? The domain requires distinguishing between "Rayane has read about topic X" and "Rayane can demonstrate understanding of topic X." Socratic assessment is part of the scholar interface, but the state lives in the user model.
- How does the user model interact with spaced repetition? Is spaced repetition a scholar interface feature using user model data, or a user model responsibility?

## Pending Owner Questions

None.

## What This Session Did

Completed shared/feedback SPEC (461+ lines, all 10 sections). Key design: the feedback component owns correction storage, pattern analysis, training data management, and regression test coordination. Each engine owns its own DSPy prompt optimization using data the feedback component provides. Three transformative capabilities: correction cascade intelligence (one correction triggers review of related artifacts via 5 cascade rules), cross-engine root cause analysis (detects when downstream corrections trace to upstream causes), and learning velocity tracking (identifies stagnant error patterns where prompt optimization has plateaued). Updated CLAUDE.md, RESOURCES.md (added SIMBA, GEPA, DeepEval), STATUS.md.

## New Decisions

None — the feedback SPEC resolves the NEXT.md decision about DSPy ownership (each engine owns its own optimization; feedback provides data) but this was an internal design choice, not a project-level architectural decision requiring a kr_decisions.md entry.
