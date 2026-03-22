# Excerpting SPEC Writing — Session 1 Handoff

**Date:** 2026-03-22
**Session scope:** Setup + §2.3 + §2.1 + §3 + §4 (4 of 12 sections)
**Commits:** `7d4a501` through `cda0d93` (7 commits including progress updates)
**SPEC status:** 547 lines, 4 sections complete

---

## What Was Done

| Section | Lines | Commit | Key Decision |
|---------|-------|--------|-------------|
| Setup | — | `7d4a501` | Archived both old SPECs to `reference/archive/abd_code/excerpting/` |
| §2.3 Internal Data Model | ~200 | `7d4a501` | 4 intermediate types, 22 invariants, LLM offset normalization |
| §2.1 Input Contract | ~84 | `a8f8f08` | Full D-023 coverage verified programmatically |
| §3 Self-Containment Standard | ~87 | `1edf2c4` | 5 criteria (C-SC-1–5), 3 levels, T-4 defense |
| §4 Phase 1: Deterministic Preprocessing | ~164 | `fd5088e` | 9 subsections, 6 validation checks, 7 error codes |

---

## Critical Findings (affect remaining sections)

### Finding 1: LLM Word Offsets Don't Match Python Tokenization

**Discovered during:** §2.3 writing, verified against real experiment data.

The LLM produces internally contiguous word offsets (0 gaps across 162 segment boundaries in Taysir div_661) but its word numbering doesn't match `text.split()`. Example: a 3643-token text (by Python split) produced segments ending at word 4172 (by LLM counting).

**Resolution committed in §2.3:** Added `total_tokens` field on `AssembledChunk` (`len(assembled_text.split())`), separate from `word_count` (Arabic-only count). Specified a mandatory **offset normalization step** in §5.4 that uses `text_snippet` fields as alignment anchors to remap LLM offsets to canonical Python tokenization. All invariants (I-CS-*, I-TU-*) describe the post-normalization state.

**Impact on §5:** §5.4 (Coverage Verification) must specify the offset normalization algorithm in detail. The §5.2 and §5.3 LLM prompts should instruct the LLM to include `text_snippet` fields (already in the experiment prompts). The normalization step must handle edge cases: what if a snippet appears multiple times in the text? What if the LLM's snippet doesn't match exactly (whitespace differences)?

### Finding 2: description_arabic Range Is Tighter Than Experiment Data

**Discovered during:** §2.3 verification, programmatic check against 226 experiment results.

The outline specified 10–30 Arabic words. Experiment data showed: min=7, max=30, mean=15.9. 2.2% of outputs (5/226) had 7–9 words.

**Resolution committed in §2.3:** Relaxed to 5–35 range. Made I-TU-8 a soft constraint (warning, not rejection).

### Finding 3: verse_info Not on AssembledChunk

**Discovered during:** §2.1 cross-referencing against §2.3 field tables.

§2.1 initially claimed verse_info was "passed through on AssembledChunk" but §2.3's AssembledChunk field table doesn't include verse_info. Corrected: verse_info is accessible by re-reading constituent ContentUnit records via `assembly_metadata.constituent_unit_indices`, not carried directly on the chunk.

**Impact on §6.5:** Verse-commentary handling cannot access verse_info directly from the chunk. If §6.5 (deferred) needs it, Phase 1 would need to add a `verse_info` field to AssembledChunk — or the deferred implementation re-reads content units. This is a design choice for later.

---

## Quality Patterns Established

### Pattern: Programmatic Verification After Every Section

Every section committed was verified with at least one Python script checking:
- Type references exist in contracts.py
- Field names match actual schema
- D-023 coverage (all fields accounted for)
- Empirical data matches thresholds (description_arabic range)

**The next session must maintain this pattern.** Specifically:
- §5: Verify the LLM prompts in the SPEC match the experiment prompts (diff them)
- §5: Verify the Pydantic response schemas match experiment schemas
- §5: Verify the FUNCTION_ENUM values match what's in §2.3.1 ScholarlyFunction
- §6: Verify domain rule references match §3 criteria numbers
- §7: Verify Phase 3 output fields will match §2.2 when it's written

### Pattern: Every Design Extension Marked

When the SPEC extends beyond what the experiment validated:
- SelfContainmentLevel 3-level enum (experiment used binary)
- segment_indices on TeachingUnit (experiment didn't have this)
- total_tokens field (experiment didn't separate Arabic vs total count)

Each is marked with a note: "Design extension — must be validated during build evaluation."

### Pattern: Invariant IDs Are Hierarchical

- I-AC-*: AssembledChunk invariants (7 total)
- I-CS-*: ClassifiedSegment invariants (6 total)
- I-TU-*: TeachingUnit invariants (9 total)
- V-P1-*: Phase 1 validation checks (6 total)
- C-SC-*: Self-containment criteria (5 total)
- EX-A-*: Phase 1 error codes (002, 003, 004, 005, 006, 010, 011)

The next session adds:
- V-P2-*: Phase 2 validation checks (§5.4, outline defines V-P2-1 through V-P2-5)
- EX-C-*: Phase 2 error codes (§8.1)
- EX-M-*: Phase 3 error codes (§8.1)
- EX-V-*: Validation error codes (§8.1)
- EX-G-*: Gate trigger codes (§8.1)

---

## What's Next — Section Writing Order

From the progress tracker (8 remaining):

| Order | Section | Estimated Lines | Source Material | Complexity |
|-------|---------|----------------|-----------------|------------|
| 1 | §5 Phase 2 | ~300 | atomization SPEC §4.A.1–§4.A.10, run_tests.py prompts | HIGH — full LLM prompt text + schemas + offset normalization |
| 2 | §6 Domain Rules | ~200 | old excerpting SPEC §4.A.2–§4.A.7, EVALUATION_WORKBOOK.md | MEDIUM — cross-cutting rules, experiment grounding |
| 3 | §7 Phase 3 | ~150 | old excerpting SPEC Phase 3, KNOWLEDGE_INTEGRITY.md | MEDIUM — consensus, human gates |
| 4 | §2.2 Output Contract | ~120 | §2.3 ExcerptRecord + all processing phases | MEDIUM — defined by what Phase 3 produces |
| 5 | §8 Error + Config | ~120 | old SPECs §7-§8, normalization patterns | LOW — systematic enumeration |
| 6 | §1 Purpose | ~80 | everything above | LOW — written last, summary |
| 7 | §9 Deferred | ~100 | old SPECs §4.B sections | LOW — table + hooks |
| 8 | §10 Tests | ~150 | §4/§5/§6/§7, old SPECs §10 | MEDIUM — adversarial cases |

**Chat allocation estimate:**
- Chat 2 (next): §5 and §6 (2 sections — §5 is the hardest single section)
- Chat 3: §7, §2.2, §8 (3 moderate sections)
- Chat 4: §1, §9, §10, coherence review (4 lighter sections + final pass)

---

## §5 Reading Instructions (for next session)

§5 is the most complex section. Read these files IN THIS ORDER before writing:

1. **`engines/excerpting/SPEC_OUTLINE.md` lines 281–377** — §5 outline with all subsection structure
2. **`experiments/architecture_test/run_tests.py` lines 36–152** — Pydantic schemas + LLM prompts (APPROACH_B_CLASSIFY_SYSTEM, APPROACH_B_GROUP_SYSTEM). These are the validated prompts that must be adapted for production.
3. **`experiments/format_diversity_test/results/RUN_SUMMARY.md`** — MAX_TOKENS finding, over-segmentation data
4. **`experiments/format_diversity_test/EVALUATION.md` lines 70–88** — Constraints C-1 through C-8
5. **`engines/atomization/SPEC.md` lines 169–520** — §4.A.1 through §4.A.10 (old atomization core processing). The segment boundary rules and classification approach come from here, but are simplified: LLM does it all, no rule-based pre-detection.
6. **`engines/excerpting/SPEC.md`** — Read §2.3.3 (ClassifiedSegment) and §2.3.4 (TeachingUnit) definitions and invariants. §5 must produce output satisfying these invariants.

**Critical for §5:** The prompts in `run_tests.py` are the experiment-validated versions. The SPEC §5.2 and §5.3 prompts should be adapted from these (not invented from scratch), with production additions:
- The classify prompt needs to explicitly request `text_snippet` (first 50 chars, copied exactly)
- The group prompt needs: `segment_indices` (new field), `self_containment` (3-level enum, not binary), `text_snippet` (first 80 chars)
- Both prompts need the self-containment criteria (C-SC-1 through C-SC-5) from §3 embedded in the group prompt

**§5.4 offset normalization algorithm:** This needs careful specification. The basic approach: for each segment, find its `text_snippet` in the canonical token stream (`assembled_text.split()`), determine the token index of the match, and set `start_word` to that index. Then use contiguity (I-CS-2) to infer boundaries between segments. Edge cases: duplicate snippets (use order — segments are LLM-ordered), snippets with whitespace variation, snippets that don't match (retry or reject).

---

## Traps to Avoid

1. **Don't re-read all 400KB of source material at session start.** Read only what §5 needs (listed above). The outline maps source material per section.

2. **Don't invent prompts from scratch.** The experiment prompts are validated. Adapt them with documented changes.

3. **Don't skip the programmatic verification.** Every section in this session was verified with Python scripts against the actual contracts.py schemas. §5 prompts must be verified against experiment prompts (diff the classify/group system messages).

4. **Don't forget offset normalization.** §5.4 is where the LLM offset → canonical offset mapping is specified. Without this, the invariants in §2.3 are unenforceable.

5. **Don't use the old atomization SPEC's rule-based pre-detection.** The outline explicitly says: "§4.A.4 Rule-based pre-detection → Replaced by LLM classification" (line 667). The LLM does all classification in Phase 2a. No marker-matching pre-pass.

6. **The over-segmentation threshold is NOT pre-decided.** The outline says `[TO BE CALIBRATED]` for minimum teaching unit size. The SPEC defines the concern and measurement; the threshold is calibrated during build. Don't commit a number.

---

## Session End Retrospective

**What went wrong:** The first version of §2.3 had `total_word_count` in invariants but no field defining it. Caught during self-review, but should have been caught during initial writing by asking "what field does this invariant reference?"

**Root cause:** Writing invariants in terms of concepts ("total word count") rather than field names. Fix: every invariant must reference a specific field on a specific type.

**Stale memory entries:** None identified — this is the first session.

**Protocol changes to propose:** None — the section-by-section writing with programmatic verification worked well. The pattern of "write section → verify references → verify empirical data → commit" should continue.

**What next session needs:** A new Claude Chat session with the same system prompt. Start by cloning the repo, reading NEXT.md, reading this handoff file, then reading SPEC_OUTLINE.md §5 section. Begin writing §5.
