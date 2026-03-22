# NEXT — Excerpting Engine SPEC Design (Fresh Start)

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis)
- Experiments: ✅ 23 divisions validated across 7 formats (10 original + 13 format diversity)
- **Excerpting SPEC review: BLOCKED** — 16 findings, 3 CRITICAL (architecture mismatch)
- **Format diversity workbook: NOT YET EVALUATED** — Arabic text quality unreviewed

## Strategic Assessment

The old excerpting SPEC (98KB) was written for the 7-engine architecture. It cannot be patched — the structural framework is wrong. But it contains excellent domain design (decontextualization, multi-layer handling, evidence/hadith, implicit references, verse format, adversarial cases).

**Critical resource the previous NEXT.md missed:** The old passaging SPEC (`engines/passaging/SPEC.md`, 148KB) contains detailed specifications for the exact functionality the excerpting engine's Phase 1 must implement — cross-page text assembly, 6 format-specific strategies (prose, verse, Q&A, masala-block, dictionary, commentary), Arabic joining rules, scholarly argument boundary detection, and 11 self-validation checks. The old atomization SPEC (`engines/atomization/SPEC.md`, 178KB) contains the classification taxonomy and relation detection rules that Phase 2 needs internally. These are not "historical references" — they are PRIMARY DESIGN INPUTS.

**This is NOT a "rewrite of the old SPEC section by section."** It is writing a NEW SPEC that synthesizes three inputs:
- **Phase 1 (Deterministic Preprocessing):** Absorbs the old passaging SPEC's core processing (§4.A.2–§4.A.10), adapted for the new architecture
- **Phase 2 (LLM Teaching Unit Extraction):** Based on the validated experiment approach (Approach B: classify-then-group), incorporating the scholarly function taxonomy from the old atomization SPEC
- **Phase 3 (Metadata Enrichment):** From the old excerpting SPEC's §4.A.2–§4.A.7, adapted to operate on teaching units instead of atoms

## What to Do — Sequenced Precisely

### Step 0: Evaluate Format Diversity Workbook (FIRST)

Before writing any SPEC, evaluate the format diversity workbook to ground Phase 2 design in empirical observation. Read Arabic text from:
- 2-3 verse-commentary divisions (Ibn Aqil) — the untested format gap
- 2 longest prose divisions (Taysir, 3000w+) — where over-segmentation was observed
- 1 masala-format division (ext_39) — structural pattern test

For each, evaluate: Are the teaching unit boundaries sensible? Does Approach B's over-segmentation on longer texts produce pedagogically useless fragments? Do verse-commentary divisions need different prompting than prose?

**Deliverable:** 1-page evaluation summary committed to `experiments/format_diversity_test/EVALUATION.md`. This informs Phase 2 design decisions.

### Step 1: Produce New SPEC Outline

Design the new SPEC's table of contents. This is the ARCHITECTURE of the document — getting it right prevents coherence problems later. The outline must:
- Map every piece of the three old SPECs to its new location (or mark as excluded)
- Define the internal intermediate representation (what replaces "atoms"?)
- Identify cross-cutting concerns that span multiple sections
- Establish the §-numbering that all sections will reference

**Deliverable:** The outline is committed to `engines/excerpting/SPEC_OUTLINE.md` before any section writing begins.

### Step 2: Write Sections in Dependency Order

One section per prompt. For each section, the architect:
1. Reads the relevant old SPEC sections + normalization contracts + experiment data
2. Analyzes: alignment with architecture? best design? future regrets? evidence-grounded? edge cases?
3. Produces the new section text
4. Commits to `engines/excerpting/SPEC.md` (replacing old content incrementally)

**Dependency order:**
1. §1 Purpose and Scope — what this engine does, what it absorbs, what it doesn't do
2. §2 Input Contract — normalized packages (reference normalization contracts.py directly)
3. §3 Deterministic Preprocessing (Phase 1) — from old passaging SPEC: assembly, merging, splitting, format strategies
4. §4 LLM Teaching Unit Extraction (Phase 2) — from experiments: classify-then-group, scholarly function taxonomy
5. §5 Self-Containment & Quality Standards — formally defined, referenceable
6. §6 Domain-Specific Handling — decontextualization, multi-layer, evidence, implicit refs, verse format (from old excerpting SPEC, adapted to new model)
7. §7 Metadata Enrichment (Phase 3) — attribution, school, topic, evidence, takhrij
8. §8 Output Contract — excerpt record schema, guarantees, provenance
9. §9 Consensus, Error Handling, Configuration
10. §10 Deferred Capabilities — clearly separated §4.B content
11. §11 Test Requirements — grounded in real data, not theoretical cases

### Step 3: Update Contracts and CLAUDE.md

After all sections are written, update `contracts.py` to match the new SPEC and verify CLAUDE.md is current.

## Key Design Decision: What Replaces "Atoms"?

The old SPEC's atom concept (typed segments with relations, bonds, and embedded references) was the atomization engine's output. Under the new architecture, the excerpting engine must define its own internal intermediate representation.

The experiments used `ClassifiedSegment` (start_word, end_word, scholarly_function, confidence) — a much simpler model than atoms. The old excerpting SPEC's decontextualization prevention relies on `atom_relations` (responds_to, illustrates, etc.) and `bonded_reason`. 

**Decision needed in Step 1:** Should the internal representation be:
- (A) Simple segments (experiment model) — word-offset ranges with classifications, no relations
- (B) Rich segments (adapted atom model) — segments with typed relations detected during classification  
- (C) Hybrid — simple segments for Phase 2, enriched with relations during Phase 3

The answer depends on whether decontextualization prevention works without pre-computed relations. The workbook evaluation (Step 0) may inform this.

## Critical Constraints

- **Budget: UNLIMITED.** Never mention cost as a factor.
- **All LLM calls through OpenRouter.** Model: anthropic/claude-opus-4.6.
- **MAX_TOKENS ≥ 32768** for classify step on >2000w divisions (empirically validated).
- **D-011 = division containment.** Excerpts cannot span division/chunk boundaries.
- **§4.B capabilities are deferred.** Core engine first.

## Read First (Fresh Session)

Priority-ordered by when they're needed:

**For Step 0 (workbook evaluation):**
1. `experiments/format_diversity_test/EVALUATION_WORKBOOK.md` (207KB) — read selectively: 2-3 verse-commentary + 2 longest prose divisions
2. `experiments/format_diversity_test/results/RUN_SUMMARY.md` — the numbers

**For Step 1 (outline):**
3. `reference/archive/sessions/reviews/excerpting_spec_review.md` — the 16 findings
4. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — committed three-phase model
5. `engines/normalization/contracts.py` — the ACTUAL input schemas

**For Step 2 (section writing) — read as needed per section:**
6. `engines/passaging/SPEC.md` (148KB) — Phase 1 source material (§4.A.2–§4.A.10 especially)
7. `engines/atomization/SPEC.md` (178KB) — classification taxonomy, relation detection
8. `engines/excerpting/SPEC.md` (98KB) — domain design in §4.A.2–§4.A.7, adversarial cases in §10
9. `experiments/architecture_test/run_tests.py` — validated LLM approach (prompts + schemas)
10. `KNOWLEDGE_INTEGRITY.md` — T-1 through T-7 threats

## Context Management Warning

The source material for this SPEC exceeds 400KB (passaging 148KB + atomization 178KB + excerpting 98KB + normalization contracts 32KB + experiments). Do NOT front-load all reading. Read what's needed for the current step:
- Step 0: workbook only
- Step 1: review findings + architecture decision + normalization contracts
- Step 2 per section: the old SPEC section(s) that inform the current new section

If context degrades (you're past prompt 6-7 in the same chat), **start a new chat** for the remaining sections. The SPEC_OUTLINE.md ensures continuity across chats.

## Do NOT Do

- Do NOT "rewrite the old SPEC" — write a NEW SPEC that synthesizes three old SPECs + experiments
- Do NOT read all 400KB of source material in one prompt
- Do NOT skip the workbook evaluation — Phase 2 design depends on it
- Do NOT skip the outline step — it prevents coherence problems across sections
- Do NOT preserve passage_id, atom_ids, or the atom-as-input model
- Do NOT write implementation code
- Do NOT include §4.B capabilities in the core SPEC sections (separate §10)
- Do NOT defer findings within a section — fix before moving to next section

## Skills to Invoke

At session start, explicitly invoke ALL of these:
- `kr-spec-review` — for analyzing old SPEC sections being absorbed
- `kr-research` — for domain research on design choices (8+ searches per decision)
- `thinking-frameworks` — for multi-angle analysis (3+ perspectives per design decision)
- `kr-integrity` — for T-1 through T-7 threat analysis on each section
- `critical-review` — for self-verification of produced sections
- `prompt-engineer` — for Phase 2 LLM prompt specification
