# NEXT SESSION

## Session Type
IMPLEMENTATION_PREP (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine IMPLEMENTATION_PREP session.** The atomization SPEC has completed all refinement phases: CREATIVE (8 §4.B capabilities), PRECISION (vague quantifiers fixed, Arabic examples added), and HARDENING (12 adversarial scenarios, 2 failure cascades, 6 invariants verified, 4 new error codes, 6 new review flags, V-9 density check added, 8 new test cases).

The SPEC is now at 1206 lines with 20 check_spec_quality.py defects (9 HIGH — all false positives: 3× "few-shot" ML term, 1× "some but not all" precise phrase, 1× "that many" pronoun, 2× narrative language in CASCADE analyses, 1× "multiple voices" in V-6, 1× UNVALIDATED_WRITE flagging a quote from the SPEC itself).

The engine needs IMPLEMENTATION_PREP: contracts verification, module stub creation, build plan, test plan, CLAUDE.md rewrite, and milestone decomposition.

## What to Read

1. `engines/atomization/SPEC.md` — Full SPEC (especially §2-§3 for contracts, §7 for error codes, §9 for implementation state, §10 for test plan).
2. `engines/atomization/contracts.py` — Current contracts (494 lines). Verify against SPEC §3 — 6 new review flag values were added this session.
3. `engines/passaging/` — Reference the passaging IMPLEMENTATION_PREP output as a template (module stubs, build plan structure, CLAUDE.md format).

**Do NOT read:** VISION.md, kr_decisions.md, CREATIVE_MANDATE.md, KNOWLEDGE_INTEGRITY.md, other engine SPECs.

## Definition of Done

1. `engines/atomization/contracts.py` verified complete against SPEC §3 (all fields, all enums, all new error codes from hardening).
2. Module stubs created in `engines/atomization/src/` with SPEC docstrings (one stub per major processing phase).
3. Build plan document created with milestones decomposed (M-level → sub-milestones).
4. Test plan document created referencing §10's 38 test cases with priority ordering.
5. `engines/atomization/CLAUDE.md` rewritten to match current SPEC (not the 67-line ABD-era version).
6. `check_spec_quality.py` shows no regression from current 20 defects.
7. Self-audit performed.
8. NEXT.md written (pointing to atomization IMPLEMENTATION session).
9. SESSION_LOG.md updated.
10. Committed and pushed.

## Notes for Next Architect

- The contracts.py already includes the 6 new review flag values (evidence_type_conflict, orphaned_footnote_marker, atom_reordering_applied, over_segmented, single_layer_in_commentary, nfc_normalization_applied). Verify the 4 new error codes (ATOM_ATTRIBUTION_MARKER_MISSING, ATOM_EVIDENCE_TYPE_CONFLICT, ATOM_FOOTNOTE_INDEX_OUT_OF_RANGE, ATOM_OVER_SEGMENTATION) are reflected in contracts.
- The passaging IMPLEMENTATION_PREP (commit 201569f) is the best template: 556-line contracts, 17 module stubs, build plan, test plan, rewritten CLAUDE.md, milestones decomposed.
- V-9 (atom density check) is a new validation check added this session — needs a module stub.
- The attribution marker verification rule (ADV-3 defense) runs during post-processing — ensure it's part of the post-processing module stub.
- The SPEC now has 38 test cases in §10 (30 original + 8 from hardening). Priority ordering: tests 1-2 (offset integrity + coverage) are highest priority, followed by 31-37 (hardening defense tests).

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
