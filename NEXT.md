# NEXT — Excerpting Engine SPEC: Section-by-Section Writing

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis)
- Experiments: ✅ 23 divisions validated across 7 formats
- Format diversity evaluation: ✅ PASS (commit 1690cdf, revised 8035e01)
- SPEC review: BLOCKED → driving rewrite (16 findings in `reference/archive/sessions/reviews/excerpting_spec_review.md`)
- **SPEC Outline: ✅ COMPLETE** (`engines/excerpting/SPEC_OUTLINE.md`)
- **Step 0 (evaluation): ✅** — Architect independently verified EVALUATION.md findings by reading Arabic text
- **Step 1 (outline): ✅** — 763-line outline with source mapping, finding resolution, data model decision

## What to Do — Step 2: Write Sections in Dependency Order

Write `engines/excerpting/SPEC.md` section by section. The outline (`SPEC_OUTLINE.md`) defines the section structure, content, source material, and writing order.

**Writing order (dependency-driven):**

1. **§2.3** Internal Data Model — everything else references these types
2. **§2.1** Input Contract — what we receive
3. **§3** Self-Containment Standard — the quality criterion
4. **§4** Phase 1: Deterministic Preprocessing — read old passaging SPEC §4.A.2–§4.A.10
5. **§5** Phase 2: Teaching Unit Extraction — read old atomization SPEC §4.A + experiment run_tests.py
6. **§6** Domain-Specific Rules — read old excerpting SPEC §4.A.2–§4.A.7
7. **§7** Phase 3: Metadata Enrichment — read old excerpting SPEC Phase 3
8. **§2.2** Output Contract — now fully specified by Phase 3 output
9. **§8** Error Handling and Configuration
10. **§1** Purpose and Scope — written last, after all content known
11. **§9** Deferred Capabilities
12. **§10** Test Requirements

**One section per prompt.** For each section:
1. Read the relevant old SPEC sections + normalization contracts + experiment data
2. Analyze: alignment with architecture? best design? future regrets? evidence-grounded? edge cases?
3. Write the new section
4. Commit to `engines/excerpting/SPEC.md`
5. Fix everything within a section before moving to the next

## Key Design Decisions (already made in outline)

**Internal data model: Option C (Hybrid)**
- Phase 1 → `AssembledChunk` (assembled text + metadata from division/chunk)
- Phase 2a → `ClassifiedSegment[]` (word offsets + 16-type scholarly function)
- Phase 2b → `TeachingUnit[]` (grouped segments + self-containment)
- Phase 3 → `ExcerptRecord` (enriched teaching unit with all metadata)

**Self-containment: 3-level system** (FULL / PARTIAL / DEPENDENT) — extends the experiment's binary flag with actionable levels for Phase 3 and human gates. Design extension, must be validated in build.

**D-011: Division/chunk containment** — structurally enforced (LLM only sees one chunk).

## Read First (per section)

**For §2.3 + §2.1:**
- `engines/normalization/contracts.py` — authoritative input schema
- `experiments/architecture_test/run_tests.py` — validated experiment schemas

**For §3:**
- `KNOWLEDGE_INTEGRITY.md` — T-4 (Context Loss)
- Old excerpting SPEC §5 — quality layers

**For §4:**
- Old passaging SPEC §4.A.1–§4.A.10 — Phase 1 source material
- `experiments/architecture_test/extract_divisions.py` — validated prototype

**For §5:**
- Old atomization SPEC §4.A.1–§4.A.5 — classification taxonomy
- `experiments/architecture_test/run_tests.py` — validated prompts + schemas

**For §6:**
- Old excerpting SPEC §4.A.2–§4.A.7 — domain design
- Evaluation workbook — verse-commentary empirical results

**For §7:**
- Old excerpting SPEC §4.A.1 Phase 3 — metadata enrichment
- `KNOWLEDGE_INTEGRITY.md` — consensus and gates

**For §8-§10:**
- Old SPECs §7-§8 and §10 — error handling, config, test patterns
- Normalization engine patterns for consistency

## Context Management

The source material exceeds 400KB (passaging 148KB + atomization 178KB + excerpting 98KB). Read ONLY what the current section needs. **Do NOT front-load all reading.**

If context degrades past prompt 6-7 in a chat, **start a new chat**. The SPEC_OUTLINE.md ensures continuity — the new session reads the outline and continues from the next section.

## Critical Constraints

- **Budget: UNLIMITED.** Never mention cost as a factor.
- **All LLM calls through OpenRouter.** Model: anthropic/claude-opus-4.6.
- **D-011 = division/chunk containment.** Excerpts cannot span boundaries.
- **§4.B capabilities are deferred.** Core engine first (§9 in new SPEC).
- **No implementation code.** Stubs with type hints acceptable.

## Skills to Invoke

At session start, explicitly invoke ALL of these:
- `kr-spec-review` — for analyzing old SPEC sections being absorbed
- `kr-research` — for domain research on design choices (8+ searches per decision)
- `thinking-frameworks` — for multi-angle analysis (3+ perspectives per design decision)
- `kr-integrity` — for T-1 through T-7 threat analysis on each section
- `critical-review` — for self-verification of produced sections
- `prompt-engineer` — for Phase 2 LLM prompt specification

## Do NOT Do

- Do NOT "rewrite the old SPEC" — write a NEW SPEC that synthesizes three old SPECs + experiments
- Do NOT read all 400KB of source material at session start
- Do NOT preserve passage_id, atom_ids, or the atom-as-input model
- Do NOT write implementation code
- Do NOT include §4.B capabilities in core sections (separate §9)
- Do NOT defer findings within a section — fix before moving to next
- Do NOT skip the outline's dependency order — sections depend on each other
