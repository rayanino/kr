# NEXT — Probe 2 build prep (Architect session)

## Current position: Probe 1 COMPLETE. All 17 findings resolved (15 original + 2 from deep review). Probe 1→2 transition gate APPROVED (commit c966e93). Ready to prepare for building the normalization engine.
## What to do: Architect runs build preparation per ENGINE_BUILD_BLUEPRINT.md §2a — core extraction, MUST-FIX resolution, technology survey, module architecture, and CC handoff.
## Context: Probe 2 = Build Team probe. The deliverable is a BUILT normalization engine with tests. This session prepares everything CC needs to start building. No CC involvement until the handoff is written at the end.
## Owner action needed: NO during this session. YES after — to give the build handoff to CC.

---

## Read First (in this order)

1. `reference/AGENT_ARCHITECTURE.md` (360L) — §5 defines Probe 2: "Build the normalization engine (5-7 sessions)." §2.2 defines Build Team agents. §6 has normalization-specific notes.
2. `reference/ENGINE_BUILD_BLUEPRINT.md` — §2a (Build Preparation) is the governing procedure. Read the full section, not just the summary.
3. `engines/normalization/SPEC.md` (2049L) — The full SPEC. You will classify every §4 capability as core vs deferred. §4.A is "Core Processing" (10 subsections). §4.B is "Transformative Capabilities" (10 subsections). Not everything in §4.A is necessarily core, and some §4.B capabilities (especially §4.B.2 structural format detection and §4.B.4 footnote classification) may belong in core — investigate each one.
4. `reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md` — The integrity audit (CONDITIONAL PASS). Contains 3 MUST-FIX items that must be resolved before build begins. See below for descriptions.
5. `engines/normalization/contracts.py` (697L) — Current Pydantic schemas. The MUST-FIX items involve contract changes.
6. `engines/source/contracts.py` — Upstream boundary. Needed for contract alignment verification.
7. `engines/normalization/CLAUDE.md` (37L) — Exists but is stale. You will rewrite it after core extraction.
8. `engines/normalization/src/` — Pre-existing stub files (dispatcher, shamela normalizer, layer detector, content census, writer, validation, errors). Assess against the SPEC after core extraction — keep what aligns, flag what doesn't.
9. `engines/passaging/SPEC.md` (1037L) — The downstream engine. Skim its §2 Input Contract to identify which normalization output fields the passaging engine actually consumes. This determines whether §4.B.2 (structural_format), §4.B.8 (boundary_continuity), and other §4.B capabilities are core.
10. `engines/passaging/contracts.py` (556L) — The passaging engine's Pydantic input models. Cross-reference with normalization output contract for field alignment.
11. `reference/SPEC_ADVERSARY_NORMALIZATION.md` (861L) — 51 adversarial test cases. NOTE: ADV-043/044 (§4.B.2) and ADV-046 (§4.B.9) have deferred annotations — their core/deferred status depends on the core extraction you'll do in Task 1.

## The 3 MUST-FIX Items (from integrity audit)

These are contract alignment issues, not redesign. All must be resolved before CC starts building.

**MF-1 (M-14): DivisionNode field count.** The SPEC's DivisionNode has 7 fields in one place and 14 in another. Resolve by deciding the correct field set and updating both the SPEC §9.1 and contracts.py. This is the only one requiring a design decision — the others are mechanical.

**MF-2 (M-13): LayerMapEntry field name mismatch.** The SPEC says one name, contracts.py says another. Rename in contracts.py to match the SPEC, and add the `markers` field that the SPEC references but contracts.py doesn't have.

**MF-3 (M-09): §5 check 14 vocalization_level.** Check 14 references a `vocalization_level` field that the upstream source engine doesn't produce. Either add the field to the source engine contracts (ripple effect — check carefully) or change the check to derive vocalization from data the normalizer already has.

## Tasks (in dependency order)

### Task 1: Core extraction (use kr-core-extract)

Classify every §4 capability. The SPEC has §4.A.1 through §4.A.10 and §4.B.1 through §4.B.10. For each: is it CORE (engine cannot fulfill its fundamental purpose without it) or DEFERRED (extends core but engine works without it)?

Key judgment calls to investigate:
- **§4.B.2 (Structural Format Auto-Detection):** The passaging engine may need `structural_format` to choose passage boundary strategies. Check `engines/passaging/SPEC.md` §2 and `engines/passaging/contracts.py` for references to this field. If consumed downstream, this is core.
- **§4.B.4 (Footnote Apparatus Classification):** Coarse classification (tahqiq vs author) is in §4.A already. Fine-grained classification (variant_reading, hadith_takhrij, etc.) may or may not be needed by the passaging engine. Investigate.
- **§4.B.8 (Cross-Page Continuity):** The passaging engine almost certainly needs `boundary_continuity` to join pages. Check `engines/passaging/contracts.py` for this field. If consumed downstream, this is core.
- **§4.B.5 (Content Census):** Several other §4.B capabilities depend on census data. If any dependent capability is core, census may need to be core too.

Produce a classification table. Owner reviews it (quick yes/no — the owner trusts your judgment on technical classification).

### Task 2: Resolve MUST-FIX items

After core extraction (because MF-1's field set depends on which capabilities are core), resolve MF-1, MF-2, MF-3. For each: describe the exact change, which files are affected, and verify no ripple effects.

### Task 3: Technology survey (use kr-research for anything uncertain)

For each CORE capability that involves external tools or libraries, verify the tool exists, works for Arabic, and has the API the SPEC assumes. The Blueprint warns: "This is NOT optional. Evidence: the source engine's initial SPEC referenced sentence-transformers for Arabic semantic search; actual Arabic support was poor."

Key areas to survey for the normalization engine:
- HTML parsing (BeautifulSoup — well-known, but verify Arabic entity handling)
- Arabic morphological analysis (if any core capability needs it)
- Any OCR-related tools (likely deferred, but verify)

### Task 4: Module architecture and stubs

Design the module structure. Pre-existing stubs in `engines/normalization/src/` exist — assess each against the core-extracted SPEC. Keep what aligns, restructure what doesn't. Write complete type signatures referencing SPEC sections.

### Task 5: Rewrite CLAUDE.md

The current CLAUDE.md is 37 lines and stale. Rewrite it as the CC orientation doc (<200 lines) reflecting the core-only SPEC, the module architecture, and the build session plan.

### Task 6: Write Build Session 1 NEXT.md

Following the Blueprint §2b template (handoff prompt), write the first CC build session directive. Session 1 should be: contracts alignment (MUST-FIX resolution) + core Pydantic model updates. This is the foundation everything else builds on.

## Do NOT Do

- Do NOT start implementing engine code. This session produces PLANS and HANDOFFS, not code.
- Do NOT modify contracts.py or any source files. The MUST-FIX resolutions are DESIGNED here and IMPLEMENTED by CC.
- Do NOT skip the technology survey. The Blueprint says it's not optional.
- Do NOT rewrite §4.A SPEC content — CLAUDE.md warns this has been through PRECISION and HARDENING.
- Do NOT classify all §4.B as deferred by default. Some §4.B capabilities may be needed by downstream engines and belong in core. Investigate each one.

## Verification

This session produces files that the Architect commits to the repo:
- [ ] Core extraction classification table (in SPEC.md or a separate reference doc)
- [ ] MUST-FIX resolution designs (can be in NEXT.md for CC or a separate doc)
- [ ] Technology survey results (documented)
- [ ] Updated CLAUDE.md (<200 lines, reflects core-only scope)
- [ ] Build Session 1 NEXT.md for CC (follows Blueprint §2b template)

## After This

Owner gives Build Session 1 NEXT.md to CC. CC begins building. The Architect is not involved until CC finishes Session 1, at which point the Architect reviews (use kr-reviewing-cc-output) and writes Session 2's handoff.
