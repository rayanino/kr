> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff

## Session purpose
Promote the preserved F1 excerpt-definition canon from collection material into the authoritative excerpting doctrine lane.

## What this session completed

### Canon promotion
- Preserved the validated 12-file F1 canon bundle under `engines/excerpting/chatgpt_f1_collection/canon/excerpt_definition/`
- Promoted a byte-identical authoritative copy to `engines/excerpting/reference/excerpt_definition_canon/`
- Added `engines/excerpting/reference/excerpt_definition_canon/README.md` to define authority, provenance, read order, and closure boundaries

### Authority cleanup
- Demoted `engines/excerpting/reference/ABD_EXCERPT_DEFINITION.md` from its stale "single source of truth" claim to historical-reference status
- Added an explicit authority note to `engines/excerpting/reference/ABD_EXCERPTING_SPEC.md` pointing to the promoted canon
- Updated `engines/excerpting/CLAUDE.md` so future excerpting work reads the canon dossier when touching boundaries, self-containment, function, or study-readiness

### Control-plane update
- Added `OPS-DEC-007` in `.kr/DECISIONS.md` making `engines/excerpting/reference/excerpt_definition_canon/` the authoritative current excerpt-definition doctrine lane

## What this means

- The raw collection/backfill phase of F1 is now preserved and promoted.
- The current excerpt-definition doctrine is authoritative in its promoted location.
- This does **not** mean every excerpt-definition question is fully resolved.

The live unresolved doctrine remains explicitly recorded in:
- `engines/excerpting/reference/excerpt_definition_canon/04_unresolved.jsonl`
- `engines/excerpting/reference/excerpt_definition_canon/10_coverage.yaml`
- `engines/excerpting/reference/excerpt_definition_canon/11_hard_judgment.md`

## Current resume point

Resume from `ACTIVE.md`.

For any further excerpting hardening, owner-review synthesis, or prompt/spec work that depends on "what an excerpt is", use:

1. `engines/excerpting/reference/excerpt_definition_canon/01_dossier.md`
2. `engines/excerpting/reference/excerpt_definition_canon/11_hard_judgment.md`
3. `engines/excerpting/reference/excerpt_definition_canon/02_terms.yaml`

Do not start from `ABD_EXCERPT_DEFINITION.md` except for historical comparison.
