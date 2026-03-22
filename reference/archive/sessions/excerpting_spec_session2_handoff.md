# Excerpting SPEC Writing — Session 2 Handoff

**Date:** 2026-03-22
**Session scope:** §5 (Phase 2: LLM Teaching Unit Extraction) + §6 (Domain-Specific Processing Rules)
**Commits:** `35ea54d` through `62bb0ae` (4 commits including progress updates)
**SPEC status:** 1145 lines, 6/12 sections complete

---

## What Was Done

| Section | Lines | Commit | Key Decision |
|---------|-------|--------|-------------|
| §5 Phase 2: LLM Teaching Unit Extraction | 440 | `35ea54d` | Full production prompts adapted from experiment; offset normalization algorithm; 19 verification checks (V-P2-1–19); 5 error codes (EX-C-001–005) |
| §6 Domain-Specific Processing Rules | 153 | `1f6fb7d` | 22 named rules across 6 categories (DP/LA/EV/IR/VC/QM); T-2 defense via layer attribution; evidence handling preserves grades without fabrication |

---

## Critical Findings (affect remaining sections)

### Finding 1: MAX_TOKENS Table Distinguishes Classify vs. Group Output Sizes

**Discovered during:** §5.5.1 writing, verified against experiment RUN_SUMMARY.md data.

The classify step produces far more objects than the group step for the same input text. For 2500–3100 word inputs, classify produced 125–166 segments while group produced 19–41 teaching units. The MAX_TOKENS constraint is driven entirely by the classify call.

**Resolution committed in §5.5.1:** The table explicitly separates classify segment counts from teaching unit counts. The classify call uses dynamic MAX_TOKENS (8192 for ≤2000 words, 32768 for >2000 words). The group call uses fixed 16384.

**Impact on §8:** When §8 defines error recovery for output truncation, it must account for this asymmetry — a truncated classify output is much more likely than a truncated group output.

### Finding 2: §6 Decontextualization Rules Are Already Embedded in §5.3.2 Prompt

**Verified during:** §6 writing, programmatic cross-check against §5.3.2 prompt text.

All 6 DP rules (DP-1 through DP-6) from §6.1 have corresponding instructions in the Phase 2b grouping prompt (§5.3.2). They appear in two locations: DP-2 and DP-6 are in the GROUPING RULES section; DP-1, DP-3, DP-4, DP-5 are in the DECONTEXTUALIZATION PREVENTION section.

**Impact on §10:** Test cases for decontextualization must test both the prompt behavior (integration test with real LLM) and the formal rule definitions (unit test verifying DP rules are present in the prompt text — a "prompt contract" test).

### Finding 3: Phase 3 Attribution Rules (LA-1–LA-4) Depend on text_layers Accuracy

**Discovered during:** §6.2 writing.

The layer attribution algorithm is deterministic (character overlap computation) but its correctness depends entirely on the normalization engine's `text_layers` detection accuracy. The normalization engine has known limitations (L-001 through L-012). If layer boundaries are wrong, the 80% threshold (LA-1) produces wrong attribution silently.

**Impact on §7:** Phase 3 should log which layer attribution rule was triggered (LA-1/LA-2/LA-3/LA-4) and the computed coverage percentages. When LA-3 fires (ambiguous — neither layer >60%), multi-model consensus is required. §7.3 must specify the consensus mechanism for attribution disputes.

### Finding 4: EX-M-001 Introduced in §6.2, Not §7 or §8

**Discovered during:** §6.2 writing.

The error code `EX-M-001` (attribution ambiguous) was introduced in §6.2 where the attribution rule LA-3 is defined, rather than waiting for §8's error code catalog. This is correct — the error code belongs where the triggering condition is specified — but §8.1 must list it and not re-define it with a different meaning.

**Impact on §8:** §8.1 error catalog must include EX-M-001 with a reference back to §6.2 LA-3, not invent a new definition. Continue the EX-M-* namespace for other Phase 3 errors.

---

## Accumulated ID Registries

These registries help the next session maintain consistency. All IDs verified programmatically against the SPEC.

**Invariants:**
- I-AC-1 through I-AC-7 (AssembledChunk, §2.3.2)
- I-CS-1 through I-CS-6 (ClassifiedSegment, §2.3.3)
- I-TU-1 through I-TU-9 (TeachingUnit, §2.3.4)

**Verification checks:**
- V-P1-1 through V-P1-6 (Phase 1, §4.9)
- V-P2-1 through V-P2-19 (Phase 2, §5.4.2 and §5.4.3)
- V-P2-1 to V-P2-9: segment checks; V-P2-10 to V-P2-19: unit checks

**Error codes (14 total):**
- EX-A-002, 003, 004, 005, 006, 010, 011 (Phase 1 assembly)
- EX-C-001, 002, 003, 004, 005 (Phase 2 classification/grouping)
- EX-M-001 (Phase 3 attribution ambiguity, defined in §6.2)
- EX-V-001 (validation failure, §4.9)

**Self-containment criteria:** C-SC-1 through C-SC-5 (§3.2)

**Domain rules (§6):**
- DP-1 through DP-6 (decontextualization prevention)
- LA-1 through LA-4 (layer attribution)
- EV-1 through EV-3 (evidence handling)
- IR-1 through IR-3 (implicit reference resolution)
- VC-1 through VC-3 (verse-commentary)
- QM-1 through QM-3 (Q&A/masala format)

The next session adds:
- V-P3-* checks for Phase 3 validation (§7)
- EX-M-002+ for additional Phase 3 errors (§8.1)
- EX-G-* for human gate trigger codes (§7.3, §8.1)

---

## Quality Patterns to Continue

### Pattern: Programmatic Verification After Every Section

Session 1 established this; session 2 continued it. Every section was verified with Python scripts checking:
- Cross-reference resolution (all I-CS-*, I-TU-*, C-SC-* refs point to definitions)
- Rule ID sequentiality (V-P2-1 through V-P2-19 with no gaps)
- Error code namespace consistency (EX-{letter}-{number})
- Experiment data claim accuracy (162 boundaries, 14.5% offset mismatch, 41 max units)
- Prompt content verification (DP rules present in §5.3.2 grouping prompt text)

**For session 3, verify:**
- §7: Phase 3 output fields will match §2.2 when §2.2 is written
- §7: LA-1–LA-4 references are consistent with §6.2 definitions
- §7: Consensus mechanism is consistent with KNOWLEDGE_INTEGRITY.md Layer 3.5
- §2.2: Every field in ExcerptRecord is traceable to a Phase 3 enrichment step in §7
- §8: Error catalog includes all codes already defined in §4–§7

### Pattern: Prompt Text Specified in Full

Both production prompts (§5.2.2 classify, §5.3.2 group) are specified as full text with documented adaptation notes listing every difference from the experiment prompts. This is important because the prompts are the primary behavioral specification for Phase 2 — the rest of §5 defines validation and infrastructure around them.

**For session 3:** §7.2 will define an LLM enrichment call. Its prompt text should also be specified in full, following the same pattern: adapt from existing source material (old excerpting SPEC Phase 3 enrichment), document every change, verify key instructions are present.

### Pattern: Design Extension Notes

When the SPEC extends beyond what experiments validated, each extension is marked with "Design extension note" and the requirement to validate during build evaluation. Session 2 additions:
- SelfContainmentLevel 3-level enum in §5.3.2 (experiment used binary)
- segment_indices on TeachingUnit in §5.3.2 (experiment didn't have this)
- Over-segmentation threshold left uncalibrated in §5.5.5

---

## What's Next — Session 3 Sections

From the progress tracker (6 remaining):

| Order | Section | Estimated Lines | Source Material | Complexity |
|-------|---------|----------------|-----------------|------------|
| 1 | §7 Phase 3: Metadata Enrichment | ~150 | Old excerpting SPEC lines 241–270, KNOWLEDGE_INTEGRITY.md layers 3.5+4 | MEDIUM — deterministic + LLM enrichment + consensus + gates |
| 2 | §2.2 Output Contract | ~120 | §2.3.5 ExcerptRecord placeholder + all §7 output fields | MEDIUM — fully defined by what Phase 3 produces |
| 3 | §8 Error Handling and Config | ~120 | All error codes from §4–§7, normalization engine patterns | LOW — systematic enumeration |
| 4 | §1 Purpose and Scope | ~80 | Everything above | LOW — written last, summary |
| 5 | §9 Deferred Capabilities | ~100 | Old SPECs §4.B sections (all three engines) | LOW — table + hooks |
| 6 | §10 Test Requirements | ~150 | §4/§5/§6/§7, experiment fixtures, normalization test patterns | MEDIUM — adversarial cases |

**Chat allocation estimate:**
- Session 3: §7, §2.2, §8 (3 sections — the remaining processing content)
- Session 4: §1, §9, §10, coherence review (4 lighter sections + final pass)

---

## §7 Reading Instructions (for next session)

§7 is moderately complex — it defines how teaching units become fully enriched excerpt records.

Read these files IN THIS ORDER before writing:

1. **`engines/excerpting/SPEC_OUTLINE.md` lines 460–500** — §7 outline with §7.1, §7.2, §7.3 subsection structure
2. **`reference/archive/abd_code/excerpting/SPEC_old_original.md` lines 241–270** — Old SPEC Phase 3 metadata enrichment (deterministic + LLM enrichment lists)
3. **`reference/archive/abd_code/excerpting/SPEC_old_original.md` lines 873–879** — Old SPEC consensus design (what uses consensus, what doesn't)
4. **`KNOWLEDGE_INTEGRITY.md` lines 143–180** — Layer 3.5 cross-provider verification + Layer 4 human gates
5. **`engines/excerpting/SPEC.md`** — Read §6.2 (LA-1–LA-4 attribution rules), §6.3 (EV-1–EV-3 evidence rules), §6.4 (IR-1–IR-3 reference resolution). These are Phase 3's primary inputs from §6.
6. **`engines/excerpting/SPEC.md`** — Read §2.3.5 (ExcerptRecord placeholder) — the current summary of what ExcerptRecord will contain. §7's output must produce exactly these fields.

**Critical for §7:**
- The old SPEC's consensus design says self-containment and school attribution use 2-model consensus; topic classification and evidence extraction don't (they have downstream validation). The new SPEC should evaluate whether this still makes sense given the architecture change (no atom-level processing, LLM does both classification and grouping).
- Layer 3.5 from KNOWLEDGE_INTEGRITY.md says the same provider must never both generate and verify. This means if Opus classifies segments and groups teaching units (Phase 2), the consensus verifier for attribution and self-containment should be a DIFFERENT provider (GPT, Mistral, or Command A). The SPEC must name the providers or specify the selection rule.
- The old SPEC lists `proposed_leaf` (taxonomy placement) as LLM-enriched. Consider whether this belongs in the excerpting engine or the taxonomy engine. The taxonomy engine is downstream and may have its own placement logic.

## §2.2 Reading Instructions

§2.2 is the output contract — it specifies what the excerpting engine delivers to the taxonomy engine.

Read these files:
1. **`engines/excerpting/SPEC.md` §2.3.5** — ExcerptRecord placeholder (the summary to expand)
2. **`engines/excerpting/SPEC.md` §7`** — What Phase 3 produces (just written in §7)
3. **`engines/normalization/contracts.py`** — For contract field naming patterns and style consistency

**Critical for §2.2:** Every field must be traceable to either (a) a Phase 3 enrichment step from §7, or (b) inherited from TeachingUnit (§2.3.4). No orphan fields.

## §8 Reading Instructions

§8 catalogs all errors and defines configuration.

Read these files:
1. **`engines/excerpting/SPEC.md`** — grep for all `EX-` codes already defined (14 total, listed above)
2. **`engines/excerpting/SPEC_OUTLINE.md` §8** — outline for §8.1 (codes), §8.2 (recovery), §8.3 (config)
3. **`engines/normalization/` error code patterns** — for naming consistency

---

## Traps to Avoid

1. **Don't re-read §5 and §6 in full at session start.** The next session reads §7 source material, not the sections already written. The outline maps source material per section. If §7 references a §6 rule (like LA-1), read that specific rule, not all of §6.

2. **Don't let §7.3 consensus design become too elaborate.** The old SPEC had a detailed consensus mechanism (2-model, agreement threshold 0.2, etc.). The new SPEC needs to specify what decisions use consensus, which providers, and what happens on disagreement — but exact thresholds are build-time calibration. Specify the mechanism structure; leave thresholds as configurable parameters for §8.3.

3. **Don't forget that §2.2 is defined BY §7.** Write §7 first, then §2.2 is a straightforward enumeration of everything §7 produces. If you write §2.2 before §7, you'll invent fields and then discover they don't match Phase 3.

4. **Don't duplicate error codes.** EX-M-001 already exists in §6.2 (LA-3 attribution ambiguity). §8.1 catalogs it, doesn't redefine it. Same for all EX-A-*, EX-C-*, EX-V-* codes.

5. **The `proposed_leaf` field from the old SPEC may not belong in the excerpting engine.** The taxonomy engine is downstream and may have its own classification logic. Consider: does the excerpting engine propose taxonomy placement, or does it produce topic keywords that the taxonomy engine uses? This is an architecture decision — make it in §7 with reasoning, not implicitly.

6. **Don't skip the coherence check between §7 and §6.** §6 defines rules (LA-*, EV-*, IR-*) that §7 implements. Every §6 rule must have a corresponding §7 step. Run a programmatic cross-check: grep for all LA-*, EV-*, IR-* rule IDs in §7 to ensure none are missed.

---

## Session End Retrospective

**What went wrong:** The initial MAX_TOKENS table in §5.5.1 conflated classify segment counts with teaching unit counts. The values (8–21) were actually teaching unit counts from Approach B, but the column header said "Segments produced." This was caught during self-verification (a Python script analyzing experiment data) and corrected before commit.

**Root cause:** The RUN_SUMMARY.md only reports teaching unit counts per approach (A_units, B_units), not classify segment counts. The classify segment counts (125–166) are mentioned only in a note about MAX_TOKENS. When writing the table, I pulled from the B_units column thinking it was the classify output. The verification step caught this because it independently computed the numbers.

**Lesson:** When building tables with data from experiments, trace each number to its specific source field. "B_units" ≠ "classify segments" — one is Phase 2b output, the other is Phase 2a output. The experiment naming contributed to the confusion (both are called "segments" or "units" loosely).

**Stale memory entries:** None identified — session 2 memory entries are all current.

**Protocol changes to propose:** None — the section-by-section writing with programmatic verification continues to work well. The post-write cross-reference check (Python script verifying all rule IDs, invariant refs, error codes) should become a standard step documented in the session handoff.

**What next session needs:** A new Claude Chat session with the same system prompt. Start by cloning the repo, reading NEXT.md, reading this handoff file, then reading the §7 source material listed above. Begin writing §7.
