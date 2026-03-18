# NEXT — Probe 2 build prep (Architect session)

## Current position: Probe 1 COMPLETE. All 17 findings resolved (15 original + 2 from deep review). Transition gate APPROVED. Ready for Probe 2.
## What to do: Architect begins Probe 2 build preparation — technology survey, core-extraction classification, module architecture, MUST-FIX resolution, and first build session handoff.
## Owner action needed: YES — start a new Claude Chat session for Architect build prep.

Architect reads:
- reference/ENGINE_BUILD_BLUEPRINT.md §2a (Build Preparation)
- engines/normalization/SPEC.md (full — for core extraction classification)
- reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md (3 MUST-FIX items to resolve)
- engines/normalization/contracts.py (current state)
- engines/source/contracts.py (upstream boundary)

The Architect will:
1. Run kr-core-extract on the normalization SPEC (classify §4.A/§4.B as core vs deferred)
2. Resolve the 3 MUST-FIX items from the integrity audit (M-14, M-13, M-09)
3. Do the technology survey for core capabilities
4. Design module architecture and write stubs
5. Write CLAUDE.md for the normalization engine
6. Write Build Session 1 NEXT.md for Claude Code
