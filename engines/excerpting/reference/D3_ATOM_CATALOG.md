# D3 Atom Catalog — Full Lifecycle Extraction

**Source:** `engines/excerpting/chatgpt_d3_collection/` (22 files, 97 atomic records)
**Question:** D3 — A Multi-Layered Definition (الكلالة case)
**Session:** 11 (proper intake — Session 10 read only 8/22 files)
**Date:** 2026-04-07

---

## Summary Counts

| Category | Count | Target |
|----------|-------|--------|
| Already covered by §6.18-6.20 | 41 | No action |
| Strengthening for existing §6.18-6.20 | 6 | Amend §6.18, §6.19 |
| NEW SPEC sections needed | 3 | §6.21, §6.22, §6.23 |
| Red-team tests | 10 | §10.6 (ADV-E-13 to ADV-E-22) |
| Open questions | 4 | [OPEN] markers |
| Process/meta (terms, traceability) | 33 | Informational only |
| **Total** | **97** | |

---

## Category A — Already Covered by §6.18-6.20 (no action)

| Atom ID | Source File | Content | Covered By |
|---------|------------|---------|------------|
| LP-001 | 10_leaf_pollution | Short proof mention potentially non-leaf-worthy | §6.18 LP-1 |
| LP-002 | 10_leaf_pollution | Proof mention later treated in fuller form | §6.18 LP-1 |
| LP-003 | 10_leaf_pollution | Mixed short stretch may remain packaged | §6.18 LP-1 + §6.19 PO-1 |
| SH-001 | 08_short_harmless | Short proof phrase in definition | §6.19 PO-1 |
| SH-002 | 08_short_harmless | Definition/proof in attribution | §6.19 PO-1 |
| SH-003 | 08_short_harmless | Attribution in proof excerpt | §6.19 PO-1 |
| SH-004 | 08_short_harmless | Generalizing carry-over too aggressively | §6.19 PO-1 |
| SHI-001 | 11_source_hints | Author flow/continuity | §6.20 SH-1 |
| SHI-002 | 11_source_hints | Commas/punctuation | §6.20 SH-1 |
| SHI-003 | 11_source_hints | Diacritics | §6.20 SH-1 |
| SHI-004 | 11_source_hints | References/cross-references | §6.20 SH-1 |
| SHI-005 | 11_source_hints | Table of contents/layout | §6.20 SH-1 |
| NN-004 | 13_nonnegotiables | Packaging != ontology | §6.19 PO-1 |
| NN-005 | 13_nonnegotiables | Not every mention = excerpt | §6.18 LP-1 |
| NN-006 | 13_nonnegotiables | Source hints non-deciding | §6.20 SH-1 |
| NN-007 | 13_nonnegotiables | No text loss | FP rules (§1.1b) |
| DL-001..DL-007 | 04_decision_ladder | Decision steps 1-7 | Existing SPEC rules |
| HD-001,HD-002 | 05_hypothetical_layers | Linguistic/technical separation | Existing SPEC rules |
| CL-001..CL-004 | 06_current_layers | Excerpt function layers | Existing classification concepts |

## Category B — Strengthening Needed in Existing Sections

### §6.18 LP-1 amendments:
| Atom ID | Content | Amendment |
|---------|---------|-----------|
| LP-004 | Significance threshold unresolved beyond D3 case | Add [OPEN] marker |
| OQ-002 | How far can significance logic generalize? | Add [OPEN] marker |

### §6.19 PO-1 amendments:
| Atom ID | Content | Amendment |
|---------|---------|-----------|
| AP-003 | Proof×attribution especially important in proof excerpts | Add direction note |
| AP-004 | Attribution dragging too much proof = packaging risk | Add packaging-limit guidance |
| OQ-003 | When should context-fill replace carried text? | Add [OPEN] marker |
| NN-008 | Unresolved distinctions must stay unresolved | Add general [OPEN] note |

## Category C — NEW SPEC Sections Needed

### §6.21 — School-Specific Branching (SSB-1)
**Source atoms:** SB-001, SB-002, SB-003, SB-004, HD-003, HD-004, OQ-001, NN-003, DL-008
**Core rule:** School-specific meanings must not be auto-merged into generic technical meaning. Three scenarios:
1. Genuinely distinct → branch under technical with own definition entry
2. Merely attributing same definition → attribution, not new definition
3. Narrower specification → sub-branch under technical
**Open:** OQ-001 — When is a school-specific meaning distinct enough for its own entry vs attribution?

### §6.22 — Pre-Excerpt Structural Analysis (PA-1)
**Source atoms:** GV-001, GV-002, TR-007, TR-008, NN-009, T-016, T-017
**Core rule:** Deeper analysis/pattern recognition BEFORE excerpting to gather structural hints. These are NON-DECIDING confirmation — they may increase confidence but must not replace core excerpting logic.
**Rationale:** Owner demand: "WE CAN STILL DO WAY MORE ANALYSIS AND PATTERN RECOGNITION before officially sending passages off to be excerpted"

### §6.23 — Attribution Coupling Rules (AC-1)
**Source atoms:** AP-001, AP-002, AP-003, AP-004, TR-012, TR-013, TR-014, OQ-003
**Core rule:** Attribution excerpts may carry short definition/proof text when harmless. But:
- proof×attribution is especially important in proof excerpts (AP-003)
- If proof is long, attribution should use context-fill instead (AP-004)
- "Context can be replaced with actual text in cases where the text is short and harmless" (owner)
**Open:** OQ-003 — When should context-fill replace carried text?

## Category D — Red-Team Tests → §10.6

| Test ID | D3 ID | Attack | What Correct Handling Requires |
|---------|-------|--------|-------------------------------|
| ADV-E-13 | RT-001 | School repeats generic technical definition unchanged | Reclassify as attribution, not new definition |
| ADV-E-14 | RT-002 | School-specific meaning genuinely distinct | Preserve distinction as branch |
| ADV-E-15 | RT-003 | Forced menu suggests flat A/B/C | Preserve hierarchy caveat |
| ADV-E-16 | RT-004 | Definition + proof + attribution misread as three meanings | Separate menu answer from local structure |
| ADV-E-17 | RT-005 | Short proof phrase in definition | Allow packaging, preserve ontology |
| ADV-E-18 | RT-006 | Extended proof phrase no longer harmless | Switch to context-fill or separate |
| ADV-E-19 | RT-007 | Proof mention later treated in fuller form | Apply significance threshold, avoid pollution |
| ADV-E-20 | RT-008 | Source layout/diacritics suggest false nesting | Use hints as non-deciding only |
| ADV-E-21 | RT-009 | Attribution dragging too much proof | Differentiate tight packaging from overlong drag |
| ADV-E-22 | RT-010 | Every support mention = excerpt | Require significance before excerpt creation |

## Category E — Open Questions (tag [OPEN])

| OQ ID | Question | Target Section |
|-------|----------|---------------|
| OQ-001 | When is school-specific meaning distinct enough for own entry vs attribution? | §6.21 SSB-1 |
| OQ-002 | How far can significance/leaf-pollution logic generalize from D3? | §6.18 LP-1 |
| OQ-003 | When should context-fill replace carried text? | §6.23 AC-1 |
| OQ-004 | How strongly may pre-excerpt analysis shape decisions without becoming deciding authority? | §6.22 PA-1 |

## Category F — Process/Meta (informational, no SPEC action)

- **Terms (T-001 to T-017):** Working definitions for the D3 case. These inform understanding but don't create new SPEC rules.
- **Traceability (TR-001 to TR-017):** Internal routing map. Verified that all raw points are accounted for.
- **Priority matrix (9 families):** Guides prioritization, captured in the section ordering above.
- **Decision ladder (DL-008):** School-specific boundary unresolved — captured in OQ-001.
- **Nonnegotiable NN-010:** Don't silently upgrade model expansions to owner truth — process rule, already in collection protocol.
- **Nonnegotiable NN-001:** Don't let menu replace actual structure — specific to questionnaire design, not SPEC-actionable.
- **Nonnegotiable NN-002:** Linguistic/technical separation — already in SPEC (existing rules).
