# NEXT SESSION

**Written by:** Session 2026-03-06 (Validation SPEC)
**Date:** 2026-03-06

## Immediate Task

Begin shared/human_gate SPEC — the human approval gates component (VISION.md §9). This is the next shared component in dependency order: feedback depends on human_gate, so human_gate must come first.

**Definition of done — this session is complete when:**
1. shared/human_gate SPEC written with all 10 sections per SPEC template
2. RESOURCES.md updated with any new tools discovered
3. Any new decisions recorded in kr_decisions.md
4. Changes committed and pushed

## Context

The validation SPEC is complete (406 lines). It defines four categories of algorithmic checks (schema validation via jsonschema, structural validators for domain invariants, referential integrity validators, and hash-chain integrity verification), a background sweep for library-wide integrity (VISION.md §8.4), and two transformative capabilities (validation failure pattern intelligence, provenance completeness scoring).

Remaining shared component SPECs needed before implementation:
- **shared/human_gate** — human approval gates for irreversible library changes (VISION.md §9). Existing ABD code: `shared/human_gate/src/human_gate.py` (881L). Multiple engines reference human gates in their SPECs §5 and §9.3.
- **shared/feedback** — feedback loop infrastructure: correction storage, pattern analysis, regression testing coordination (VISION.md §8.3). Depends on human_gate. No existing code.
- **shared/user_model** — persistent user state (D-017). No existing code.
- **shared/scholar_authority** — canonical scholar identities (D-025). No existing code beyond what the source engine references.
- **interface/scholar/** — user-facing intelligence layer (D-016). No existing code.

After all shared component SPECs: the first SCIENCE.md (إملاء for Milestone 1).

## Files to Read — IN THIS ORDER

1. `shared/human_gate/CLAUDE.md` and `shared/human_gate/src/human_gate.py` — existing ABD code to understand what exists
2. Engine SPECs that reference human gates: grep for "human gate" or "human_gate" in all engine SPECs. Key sections: each engine's §5 (Layer 3), §9 mentions.
3. `VISION.md` §9 (Human Gates) — use `python3 scripts/extract_vision_sections.py 9`
4. `shared/validation/SPEC.md` — just completed; reference for how validation results feed into human gate triggering
5. `reference/RESOURCES.md` — existing tool research

## Decisions Needed

- How should the human gate present information to the owner? Is it a CLI interface, a web UI, a notification system? This is an architectural decision that affects the scholar interface too.
- Should the human gate component own the presentation layer, or should it just manage the gate state (pending/approved/rejected) and delegate presentation to the scholar interface?

## Pending Owner Questions

None.

## What This Session Did

Completed shared/validation/SPEC.md (406 lines, all 10 sections). Key design: four validation categories (schema, structural, referential integrity, hash-chain), 12 structural checks covering all engine boundary invariants, background sweep with 4-phase library-wide integrity verification, validation orchestration with dependency ordering. Two transformative capabilities: failure pattern intelligence (clusters errors to detect systematic issues) and provenance completeness scoring (0.0–1.0 continuous provenance signal for excerpts). Updated RESOURCES.md with validation-specific tools (jsonschema, Pydantic v2, hashlib). Updated STATUS.md and validation CLAUDE.md.

## New Decisions

None — the validation SPEC does not introduce new architectural decisions beyond what existing engine SPECs and VISION.md §8 already established. It implements and specifies the mechanisms those decisions call for.
