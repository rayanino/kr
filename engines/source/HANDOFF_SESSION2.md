# Source Engine Spec Discovery — Session 2 Handoff

**Date:** 2026-04-15
**From:** Claude Code (Session 2 — deep spec hardening + 5 DRs + 6 coworker reviews)
**To:** Next CC session (continuing spec freeze gate)
**Branch:** `clean-start` (pushed to remote)

---

## Accomplished

**Spec grew from 81 → 98 atoms, 0 validation errors.** Every atom machine-validated against schema.json.

| Category | Count |
|---|---|
| New atoms created | 17 (REQ-0028–0043, INV-0009, CON-0006, CON-0007, DEC-0013, DEC-0017) |
| Atoms amended | ~20 (REQ-0004, 0006, 0008, 0009, 0011, 0013, 0014, 0015, 0019, 0021, 0026, 0027, DEC-0009, INV-0001, 0002, 0006, CON-0004, REQ-0035, 0040, schema.json) |
| DRs incorporated | 5 (ChatGPT agent architecture, Gemini research sources, Gemini display metadata, Claude spec audit, Claude source lifecycle) |
| Coworker reviews | 6 (adversary, contract architect, domain validator — first round on full spec, second round on author attribution) |
| Owner directives | 3 (Zero Knowledge Loss INV-0009, display metadata REQ-0035, format-agnostic multi-volume REQ-0041) |
| Open questions resolved | 3 → 0 draft (OQ-0003 agent architecture, OQ-0007 research sources, both superseded) |
| PDF empirical analysis | 285 files characterized — 100% Presentation Forms, 0% scans, NFKC mandatory |

### Key architectural decisions made this session:
1. **DEC-SRC-0013:** Deterministic orchestrator with deliberation cells (not LLM supervisor)
2. **DEC-SRC-0017:** NFKC normalization allowed at PDF extraction boundary (distinct from Critical Rule #8)
3. **REQ-SRC-0004 status rename:** agent_consensus/agent_disagreement/agent_no_evidence/co_authored (avoids collision with scholarly terminology)
4. **REQ-SRC-0015 overhaul:** 9 acceptance criteria covering null death dates, kunya-only scholars, institutional authorship, laqab-as-primary, female scholars, death date tolerance, صاحب convention
5. **INV-SRC-0009:** Zero Knowledge Loss — NEVER hide/compress/simplify knowledge (owner ALL-CAPS directive)

## Errors and Corrections

1. **Asked the owner whether to hide/show disputes** — Should have derived from existing principles that the answer is always "show everything." Owner corrected with Zero Knowledge Loss directive.
2. **PDF atoms originally assumed all Arabic PDFs need OCR** — Empirical analysis of 285 real PDFs proved the opposite: all have usable text layers in Presentation Forms encoding. NFKC normalization recovers clean text without OCR.
3. **REQ-SRC-0015 was insufficient for real Arabic naming** — 3 independent coworker reviews found 8 fundamental gaps (name collision, null dates, kunya-only, institutional, laqab, female, صاحب, display precedence). All fixed.
4. **Status enum "disputed" appeared in both REQ-0004 and REQ-0040 with different meanings** — Renamed REQ-0004's values to avoid confusion.

## Learnings

1. **DRs are transformative at every stage.** The 5 DRs this session each revealed categories of complexity no coworker review caught. The Claude DR found 7 Islamic text patterns (majmu', mukhtasar chains, tafsir layers) that restructured the spec. The Gemini DR on display metadata grounded the source card in 1000-year-old scholarly tradition (الرؤوس الثمانية / المبادئ العشرة).
2. **Author attribution is the deepest single subsystem.** 22 findings from 3 focused coworker reviews. The combination of Arabic naming complexity + absent death dates + institutional authorship + multi-level honorifics makes this the hardest metadata problem.
3. **Empirical PDF analysis pays for itself immediately.** The Presentation Forms discovery changed the entire PDF routing model from OCR-only to text-extraction-primary.
4. **The "specs-as-data" format works.** 98 YAML atoms, machine-validated, with structured behavior/postconditions/acceptance_criteria. Build agents can consume individual atoms without interpreting prose.

## Blockers

1. **ChatGPT DR on source lifecycle** — dispatched but not yet returned. Will provide the second independent model for how submissions merge into works over time. Claude DR already returned with FRBR-aligned model.
2. **Source lifecycle model not yet formalized into atoms** — The Claude DR provides the conceptual framework (Submission→Source→Edition→Publication→Volume with MARC 866-style holdings), but no spec atoms define this yet. This blocks finalizing Area 1 of the freeze gate.

## Next Steps (for next CC session)

### Priority 1: Incorporate lifecycle DRs into spec atoms
- Read ChatGPT DR when available
- Synthesize with Claude DR's FRBR-aligned model
- Create atoms for: entity model (5 levels), holdings tracking, supersession model, progressive completeness
- Update vocabulary (01-vocabulary/README.md) with the new entity hierarchy

### Priority 2: Continue freeze gate (Areas 2-7)
The freeze gate was interrupted at Area 1 (owner raised lifecycle edge cases → DR dispatched). Resume:
- **Area 1:** Re-present with lifecycle model incorporated
- **Area 2:** Re-present with all 22 author-attribution fixes
- **Areas 3-7:** Genre/science, source card, risk gate, agent architecture, future-proofing

### Priority 3: Final review round
After all freeze gate areas confirmed:
- Dispatch final adversary review on the complete 98+ atom spec
- Move confirmed atoms from `proposed` → `confirmed`
- Generate final views

## Owner Actions

1. **When ChatGPT DR returns:** Share the file path so next session can incorporate it
2. **Review SPEC_OVERVIEW.md** at `engines/source/SPEC_OVERVIEW.md` — it's the visual overview of the spec (needs updating to reflect 98 atoms, will be done next session)
3. **Continue freeze gate discussion** — Areas 2-7 ready for one-at-a-time confirmation

## Key Files

| File | Purpose |
|---|---|
| `engines/source/spec/INDEX.yaml` | 98-atom registry |
| `engines/source/SPEC_OVERVIEW.md` | Visual overview (needs update to 98 atoms) |
| `engines/source/HANDOFF_SESSION2.md` | This handoff |
| `engines/source/HANDOFF.md` | Session 1 handoff (still valid for context) |
| `engines/source/reference/pdf_collection_characterization_2026-04-14.md` | PDF round 1 (10 files) |
| `engines/source/reference/pdf_collection_sampling_round2_2026-04-15.md` | PDF round 2 (285 files) |
| `engines/source/reference/DR_SPEC_AUDIT_CLAUDE_2026-04-15.md` | Claude DR: 7 Islamic text patterns |
| `engines/source/reference/DR_SOURCE_LIFECYCLE_CLAUDE_2026-04-15.md` | Claude DR: FRBR-aligned lifecycle model |
| `engines/source/reference/DR_DISPLAY_METADATA_GEMINI_2026-04-14.md` | Gemini DR: source card design |
| `engines/source/spec/60-evidence/dr-prompts/DR_SOURCE_LIFECYCLE.md` | ChatGPT DR prompt (dispatched, pending) |

## Commits This Session (6)

```
9b8d349e0 feat(source): fix 22 author-attribution gaps + lifecycle DR (96→98 atoms)
fd73754ef feat(source): format-agnostic multi-volume + source lifecycle DR prompt (95→96 atoms)
ef4559849 feat(source): incorporate Claude DR spec audit — 7 Islamic text patterns (92→95 atoms)
57f183330 feat(source): incorporate Gemini DR display metadata design into REQ-SRC-0035
9c83e277e feat(source): empirical PDF characterization + Presentation Forms discovery (91→92 atoms)
bd8d534da feat(source): harden spec with 2 DRs, 3 coworker reviews, owner directives (81→91 atoms)
```
