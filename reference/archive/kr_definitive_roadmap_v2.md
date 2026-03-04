# خزانة ريان — Definitive Project Roadmap (Revised)

**Produced:** 2026-03-04  
**Status:** Final — binding project guideline  
**Revision note:** Fundamentally restructured based on the correct understanding that engine SPECs drive VISION corrections, not the reverse. VISION.md is an architectural overview that summarizes the engines; the detailed truth lives in the SPECs. The correct workflow is: deeply understand an engine → write its SPEC → correct the VISION passages that describe it.

---

## The Core Reframing

The previous plan assumed: audit VISION first → write SPECs based on audited VISION. This is backwards.

VISION.md §13.1 defines the documentation hierarchy:
- **Level 0 (VISION.md):** defines *what* the application is and *why*
- **Level 2 (SPEC.md):** defines *how* each engine works

But the *knowledge flow* during development goes upward: you cannot write an accurate architectural overview of the source engine until you've defined the source engine in detail. The SPEC-writing process is a discovery process — it forces confrontation with every concept, every edge case, every ambiguity. That deep understanding then flows back up to correct the VISION passages that summarize the engine.

**VISION sections have clear engine ownership.** The data confirms this:
- §5 (The Excerpt) → **excerpting engine** (50 mentions), taxonomy (24)
- §6 (The Entry) → **synthesizing engine** (32 mentions)
- §7.1–§7.4 → **source engine** (44 mentions in §7)
- §7.5–§7.6 → **normalization engine** (47 mentions in §7)
- §9 (Human Gates) → **taxonomy engine** (16 mentions)

When you write the excerpting engine SPEC, you develop the deepest possible understanding of what an excerpt is. *That* is when you can accurately verify and correct §5 — not before.

**The revised workflow per engine:**
```
Study engine deeply (code, reference docs, current behavior)
    ↓
Draft SPEC.md through Q&A (the discovery process)
    ↓
With that deep understanding, examine the VISION passages this engine owns
    ↓
Correct VISION where wrong or imprecise
    ↓
Update any schemas affected by corrections or SPEC decisions
```

**Cross-cutting VISION sections** (§8 Quality Architecture, §10 Implementation Strategy, §11 Design Principles, §12 Codebase Relationship) are not owned by any single engine. These are corrected *after* all engine SPECs are written, when full system understanding exists.

---

## Foundational Decisions

Unchanged from previous version. All five decisions must be resolved before Phase 1.

### Decision 1: Taxonomy Directory Structure

Conform to §13.2.6. Each science directory gets: `tree.yaml` (active version), `tree_history/` (all versions), `content/` (empty for now), `SCIENCE.md` (placeholder). The `taxonomy/` subdirectory is removed. `imlaa_v0.1.yaml` is renamed to `imlaa_v0_1.yaml` for naming consistency.

### Decision 2: The discover_structure.py / Passaging Boundary

Do not touch in Phase 1. Resolve when writing the normalization and passaging engine SPECs (Phase 2, Rounds 2–3).

### Decision 3: Gold Baseline Strategy

Existing baselines are historical ABD-era validation artifacts, preserved as-is. New KR-era gold baselines are created when KR engines produce extraction output (Milestone 1).

### Decision 4: Aqidah Taxonomy Status

Aqidah is missing from `taxonomy_registry.yaml`. Add it with `v0_2` as active and `v0_1` as historical.

### Decision 5: §12's Post-Migration Status

§12 is rewritten to past tense during Phase 2's cross-cutting corrections (Phase 2, Round 9), reflecting that the migration is complete.

---

## Phase 1 — Structural Cleanup

Identical to the previous plan's Phase 1. Claude Code CLI, single session, strictly mechanical.

**Prerequisites.** Decisions 1 and 4 resolved.

**Scope:**
1. Restructure `library/sciences/` to match §13.2.6
2. Update `taxonomy_registry.yaml` (add aqidah, fix all relpaths)
3. Fix test paths referencing taxonomy files
4. Add `__init__.py` to all engine/shared `src/` and `tests/` directories
5. Update `requirements.txt` (ABD→KR, add pytest + jsonschema)
6. Update root CLAUDE.md "Current Priorities"

**Out of scope:** Any source code behavior changes, schema modifications, or architectural decisions.

**Exit criteria:** ≥1022 tests passing, 9 previously-skipping taxonomy tests now pass, 1 API-key test still fails (acceptable), ≤14 corpus-data skips (acceptable), zero regressions.

**Claude Code prompt:** Same as previous plan's prompt (with aqidah active version specified).

---

## Phase 2 — Engine-by-Engine SPEC Writing + VISION Correction

**Why this phase exists.** This is the core intellectual work of the project's documentation phase. Each round deeply studies one engine, produces its SPEC.md, and uses that understanding to correct the VISION passages the engine owns. By the end, every engine has a SPEC and every VISION section has been examined with the relevant engine expertise.

**Who executes.** Claude Chat (SPEC drafter + VISION corrector) + You (Q&A partner, decision-maker, domain expert).

**Prerequisites.** Phase 1 complete.

**Method per round:**

Each round is a dedicated session (or multiple sessions for complex engines). The workflow:

**Step 1 — Context loading.** Claude Chat reads:
- The engine's CLAUDE.md
- The engine's `reference/` directory (ABD-era specs, runbooks, binding decisions, edge cases — these encode months of trial-and-error knowledge)
- The engine's current source code
- The engine's current tests
- The relevant boundary schemas (input and output)
- `reference/kr_decisions.md` (growing decision log)
- Previously written SPECs for upstream engines (in pipeline order, these exist by the time each engine is reached)

**Step 2 — SPEC drafting through Q&A.** Claude Chat drafts the SPEC.md following the standard template. Every behavioral question surfaces as a question to you. You make the final call on ambiguous points. Decisions are recorded in `reference/kr_decisions.md`.

**Step 3 — VISION correction.** With the deep understanding gained from SPEC writing, Claude Chat examines every VISION.md passage that this engine owns. Corrections are proposed as a defect ledger (same format as the forensic audit methodology). You review and approve corrections. VISION.md is updated.

**Step 4 — Schema update.** If SPEC writing or VISION correction revealed schema issues, the affected schema(s) are updated immediately. Changes are noted in `schemas/SCHEMA_ANALYSIS.md`.

**Step 5 — Commit.** SPEC.md, VISION.md corrections, and any schema changes are committed together as one coherent unit.

**SPEC template — every SPEC.md follows this structure:**

```markdown
# {Engine Name} — {Arabic Name} — Specification

## 1. Purpose and Scope
What this engine does. What is NOT this engine's responsibility.
Phase classification. Normalization boundary relationship.

## 2. Input Contract
Reference to input schema. What the engine expects.
Validation performed on input.

## 3. Output Contract
Reference to output schema. What the engine produces.
Guarantees about output.

## 4. Processing Specification
Behavioral rules governing input→output transformation.
Edge cases with explicit resolution rules.
Subsections as needed.

## 5. Validation and Quality
Self-validation (§8 Layer 1). Automated checks (§8 Layer 2).
Human gate integration (§9), if applicable.

## 6. Consensus Integration
Which decisions use multi-model consensus.
Consensus configuration for this engine.

## 7. Error Handling
Malformed input. Partial failures. Consensus disagreement.

## 8. Configuration
Parameters controlling engine behavior.
Per-science configuration hooks (Level 3).

## 9. Current Implementation State
Files, line counts, what works, what needs building.
Known gaps between current code and this spec.

## 10. Test Requirements
Test coverage requirements. Gold baseline usage.
Regression testing strategy.
```

**Round execution order:**

### Round 1: Source Engine

| Aspect | Detail |
|---|---|
| **Existing code** | `intake.py` (1476L), `enrich.py` (580L), `corpus_audit.py` — 3081 total lines across src + tests |
| **Reference docs** | 2 files in `engines/source/reference/` |
| **Input schema** | None (pipeline entry point — receives raw files and manual input) |
| **Output schema** | `schemas/source_metadata.json` |
| **VISION sections to correct** | §7.1 (pipeline overview, source half), §7.2 (discovery/acquisition), §7.3 (documentation/metadata), §7.4 (trustworthiness) |

**Key questions this round must resolve:**
- The source identity model: what is a "source"? Does `book_id` become `source_id`? How are multi-volume works represented? How is manual input represented?
- What constitutes the source engine's output? Is it just `source_metadata.json` + a frozen file, or does it include other artifacts?
- How does the source registry (`library/sources/registry.yaml`) work?
- What does the current `intake_metadata.json` format (with Shamela-specific fields) evolve into for KR?

**Schema impact:** `source_metadata.json` may be updated based on source identity decisions. Any field renames (e.g., `book_id` → `source_id`) are documented but only applied to this schema now; downstream schemas note the pending rename.

### Round 2: Normalization Engine

| Aspect | Detail |
|---|---|
| **Existing code** | `normalize_shamela.py` (1123L), `discover_structure.py` (2896L), `validate_structure.py` — 7914 total lines |
| **Reference docs** | 15 files (the largest reference collection of any engine) |
| **Input schema** | `schemas/source_metadata.json` + frozen source files |
| **Output schema** | `schemas/normalized_package.json` |
| **VISION sections to correct** | §7.5 (source normalization), §7.6 (normalization boundary) |

**Key questions this round must resolve:**
- **The boundary question** (Decision 2): Does `discover_structure.py`'s `build_passages()` stay in normalization, or does passage construction belong to the passaging engine? This is the session where the decision is made, informed by deep code understanding.
- What exactly does the normalized package contain? Does it include a division tree? Passage boundaries? Just pages?
- How do normalizer-specific extensions work? (The Shamela normalizer discovers different structure than a future PDF normalizer would.)
- The `library/sources/` internal structure: `stage1_output/`, `stage2_output/` — what do these become?

**Schema impact:** `normalized_package.json` may be substantially revised based on what the normalized package actually contains. The source identity rename (`book_id` → `source_id`) is applied here if it flows through the normalized package.

### Round 3: Passaging Engine

| Aspect | Detail |
|---|---|
| **Existing code** | `scaffold_passage.py` (279L) — ABD scaffold tool only, no real passaging logic |
| **Reference docs** | None |
| **Input schema** | `schemas/normalized_package.json` |
| **Output schema** | `schemas/passage.json` |
| **VISION sections to correct** | §2.2 passaging definition (if the boundary decision changed what passaging means) |

**Key questions this round must resolve:**
- What does the passaging engine receive from normalization? (Directly depends on Round 2's boundary decision.)
- How are passage boundaries determined? (If Round 2 decided that `build_passages()` stays in normalization, what's left for the passaging engine?)
- Is the passaging engine substantive or thin? (Honest answer based on the boundary decision — if normalization outputs passages directly, the passaging engine may be a thin validator/enricher rather than the thing that creates passages from scratch.)

**Schema impact:** `passage.json` may need updates. Source identity rename propagated.

### Round 4: Atomization Engine

| Aspect | Detail |
|---|---|
| **Existing code** | 0 dedicated source files (logic lives in `engines/excerpting/src/extract_passages.py`) |
| **Reference docs** | `ABD_ATOMIZATION_SPEC.md`, `ABD_ZOOM_BRIEF.md` in `engines/atomization/reference/` |
| **Input schema** | `schemas/passage.json` |
| **Output schema** | `schemas/atoms.json` |
| **VISION sections to correct** | §2.4 (atom definition, content type) — if SPEC writing reveals that the glossary definition needs refinement |

**Key questions this round must resolve:**
- What exactly is the atomization→excerpting boundary? Which parts of `extract_passages.py` are atomization vs. excerpting?
- The atom type taxonomy: what types exist, what determines type?
- How do character offsets work? (Referenced in §2.2 but not detailed in VISION.)
- Does atomization use consensus? The current code runs atomization + excerpting together through consensus — when separated, which engine owns the consensus call?

**Schema impact:** `atoms.json` updates. Source identity rename propagated.

### Round 5: Excerpting Engine

| Aspect | Detail |
|---|---|
| **Existing code** | `extract_passages.py` (2288L), `assemble_excerpts.py` (1021L) — the pipeline's core |
| **Reference docs** | 9 files including `ABD_EXCERPTING_SPEC.md`, `ABD_EXCERPT_DEFINITION.md`, `ABD_EXTRACTION_PROTOCOL.md`, `ABD_BINDING_DECISIONS.md`, `ABD_RUNBOOK.md`, `edge_cases.md` |
| **Input schema** | `schemas/atoms.json` |
| **Output schema** | `schemas/excerpt.json` |
| **VISION sections to correct** | **§5 in its entirety** (self-containment, creation rules, boundaries, metadata extensions, one-per-source diagnostic) |

**This is the most complex round.** The excerpting engine is the intellectual core of the application. §5 is 93 lines of architectural specification that must precisely match what the engine actually does. The `reference/` directory contains 9 documents encoding months of extraction experience.

**Key questions this round must resolve:**
- Is the self-containment definition in §5.1 correct and complete? Does it match what the code actually evaluates?
- The metadata model: §5.1 lists metadata categories (primary text, derived text, author, school, source reference, topic context, content type, verified/flagged). The schema has 30+ fields. How do these map?
- Excerpt boundary rules (§5.3): are the three rules (context retained, extensive treatment split, integrity priority) accurate? Do they match how `extract_passages.py` actually handles multi-topic content?
- The taxonomy-independence rule (§5.2): is it enforced in the code?
- Science-specific metadata extensions (§5.4): how does the extension mechanism work concretely?

**Schema impact:** `excerpt.json` may need substantial reconciliation. This is where most schema changes concentrate.

### Round 6: Taxonomy Engine

| Aspect | Detail |
|---|---|
| **Existing code** | `evolve_taxonomy.py` (2377L) — evolution logic with solid test coverage |
| **Reference docs** | `ABD_TAXONOMY_SPEC.md` in `engines/taxonomy/reference/` |
| **Input schema** | `schemas/excerpt.json` (draft excerpts) |
| **Output schema** | `schemas/placed_excerpt.json` |
| **VISION sections to correct** | §4.4 (evolution governance — re-verify with SPEC knowledge), §5.5 (one-per-source diagnostic — taxonomy engine implements this), §9.3 (human gate locations — taxonomy engine is the primary gate site) |

**Key questions this round must resolve:**
- Placement algorithm: how does the taxonomy engine decide which leaf an excerpt belongs at?
- Evolution governance: what triggers evolution? What approval is needed? How does the human gate work?
- The relationship between the taxonomy engine and human_gate shared component
- How does the taxonomy engine manage tree versioning? (tree.yaml vs tree_history/)
- The excerpt lifecycle transition: draft → reviewed → placed. How does the taxonomy engine execute the reviewed→placed transition?

**Schema impact:** `placed_excerpt.json` updates. Source identity rename propagated.

### Round 7: Synthesizing Engine

| Aspect | Detail |
|---|---|
| **Existing code** | None — completely new engine |
| **Reference docs** | None |
| **Input schema** | `schemas/placed_excerpt.json` (placed excerpts at leaves) |
| **Output schema** | `schemas/entry.json` |
| **VISION sections to correct** | **§6 in its entirety** (entry definition, structure, staleness, quality) |

**This round is fundamentally different** from the others. There's no existing code and no reference docs. The SPEC must be written from §6 and first principles. Since there's nothing to deeply study first, the SPEC-writing IS the discovery process — and the Q&A must be more thorough than other rounds.

**Key questions this round must resolve:**
- Entry structure at a leaf: one entry per school group? How does school grouping work?
- Staleness model: when is an entry stale? What triggers regeneration?
- Entry quality criteria: what makes a good entry?
- The synthesizing engine's science-awareness: it reads SCIENCE.md (Level 3). What specifically does it need from Level 3?

**This is the one round where a minimal SCIENCE.md is a prerequisite.** At least إملاء's SCIENCE.md should exist (even if minimal) so the synthesizing engine SPEC can reference concrete examples. إملاء has no schools, which simplifies the school-grouping question — but the SPEC must handle sciences that DO have schools.

**Schema impact:** `entry.json` updates.

### Round 8: Shared Components

Four shared components, drafted in a single extended session (or two sessions if needed). Each component follows the same SPEC template, adapted for infrastructure rather than pipeline processing.

| Component | Existing code | SPEC focus |
|---|---|---|
| **shared/consensus** | `consensus.py` (1749L), solid tests | API contract, model configuration, confidence scoring, retry logic |
| **shared/human_gate** | `human_gate.py` (881L), 28 passing tests, existing 32L SPEC | Extend existing SPEC to full template. Checkpoint workflow, correction records, pattern detection |
| **shared/validation** | `cross_validate.py` (779L), tests | Validation layers (algorithmic, LLM), schema validation, field checks |
| **shared/feedback** | No code | Interface definition only. Target: §8.3 feedback loop architecture. Defer internals. |

**VISION sections to correct after this round:** §8 (quality architecture — now understood through validation + feedback SPECs), §9 (human gates — now understood through human_gate SPEC + taxonomy engine's gate integration).

### Round 9: Cross-Cutting VISION Corrections

With all engine SPECs written and all engine-specific VISION passages corrected, this round examines the remaining VISION sections that no single engine owns:

| Section | Lines | What to do |
|---|---|---|
| §8 (Quality Architecture) | 71 | Verify against the full set of engine SPECs — does the defense-in-depth model accurately describe how engines actually validate? |
| §10 (Implementation Strategy) | 133 | Update codebase inventory (§10.3) with accurate file paths and counts. Verify milestone definitions against what's actually buildable. |
| §11 (Design Principles) | 59 | Consistency check against all SPECs — does each principle hold as described? |
| §12 (Codebase Relationship) | 53 | Rewrite to past tense. Migration is complete. Reference the migration commit. |
| §0–§4, §13 | — | Light re-verification pass. These were audited before, but engine-deep-dive knowledge may reveal issues the earlier audit missed. Not a full re-audit — a targeted check informed by SPEC work. |

**Decision log finalization.** Review `reference/kr_decisions.md` for completeness. Every architectural decision made during Rounds 1–8 should be recorded.

---

## Phase 3 — Cross-SPEC Consistency Verification

**Why this phase exists.** SPECs were written in 8 separate rounds. Cross-engine inconsistencies — where Engine A's output description doesn't match Engine B's input description — may exist despite pipeline ordering.

**Who executes.** Claude Chat, in a single focused session.

**Prerequisites.** Phase 2 complete (all SPECs written, all VISION corrections applied).

**Method:**

1. **Verify output→input chain.** For each engine boundary:
   - Producing engine's SPEC §3 (Output Contract)
   - Consuming engine's SPEC §2 (Input Contract)
   - Shared schema
   - Do all three agree?

2. **Verify shared component integration.** Each engine that uses consensus/human_gate/validation: check both sides of the integration match.

3. **Verify VISION alignment.** Spot-check 5 key concepts (self-containment, normalization boundary, content type, school, source-agnostic) across all SPECs.

4. **Produce consistency report** at `reference/spec_consistency_report.md`.

**Exit criteria:** All boundaries verified. Mismatches resolved or flagged for owner.

---

## Phase 4 — Owner Review

**Why this phase exists.** Final quality gate. The owner reads the complete documentation stack and confirms it's ready to guide agent builders.

**Who executes.** You.

**Prerequisites.** Phase 3 complete.

**Method — top-down:**

**Pass 1: VISION.md integrity scan.** Full read for cross-section coherence. The sections were corrected at different times during Phase 2 — do they read as a unified document?

**Pass 2: Schema verification.** Sign off on every schema's field list.

**Pass 3: Engine SPEC review.** For each SPEC: does it describe a system that correctly implements VISION's intent? Does §9 (Current Implementation State) accurately describe what code exists?

**Pass 4: Shared component SPEC review.** Same method.

**Pass 5: CLAUDE.md alignment.** Do the operational guides match their SPECs?

**Discovered issues:** Typos → fix directly. SPEC defects → Claude Chat corrects. VISION defects → Claude Chat corrects, then re-check dependent SPECs. Architectural questions → logged in decisions.md, resolved, dependent docs updated.

**SPEC update protocol (applies here and during all future building):**
When a SPEC needs adjustment:
1. Document the issue in the engine's CLAUDE.md under `## Spec Clarifications Needed`
2. Work on the affected feature pauses
3. Owner reviews and approves the SPEC change or provides guidance
4. SPEC.md is updated first, then code follows
5. The `## Spec Clarifications Needed` entry is removed once resolved

SPECs are never silently diverged from.

**Exit criteria:** Owner confirms: documentation is complete and correct for agent-guided building.

---

## Phase 5 — Build Infrastructure Planning

**Why this phase exists.** Phases 1–4 answered "what to build." This phase answers "how."

**Who executes.** You, with Claude Chat as thinking partner.

**Prerequisites.** Phase 4 complete.

**Decisions to make:**

| Area | Questions |
|---|---|
| **Claude Code agents** | Which subagents (`.claude/agents/`), what each does, tool permissions |
| **Slash commands** | Reusable prompts (`.claude/commands/`) for common ops |
| **Hooks** | Automated checks in `.claude/settings.json` (tests after code changes, schema validation) |
| **MCPs** | Which external tools Claude Code gets access to |
| **CI/CD** | GitHub Actions? Pre-commit hooks? Branch strategy? |
| **API keys** | How to provide keys for consensus tests (unblocks the 1 failing test) |
| **Corpus data** | How to make "Other Books" accessible (unblocks 14 skipping tests). Git LFS? Download script? |
| **Python packaging** | Evolve `_paths.py` → `pyproject.toml`? When? |
| **Build order** | Engine order within Milestone 1, session structure |
| **SCIENCE.md** | إملاء's minimal Level 3 doc (needed for synthesizing engine). Other sciences deferred to their milestones. |
| **Integration tests** | End-to-end test strategy (source → … → entry) |
| **Documentation versioning** | How SPEC changes are tracked going forward |

**Deliverables:** Populated `.claude/` directory. Documented build plan. Resolved infrastructure decisions. إملاء `SCIENCE.md` (minimal).

**Exit criteria:** Claude Code can start the first engine-building session with a clear prompt, access to all necessary resources, and automated quality gates.

---

## Phase 6+ — Engine Building (Directional Sketch)

Fully planned during Phase 5. Follows VISION.md §10.2 milestone sequence.

**Milestone 1: Prove Phase 2 end-to-end on إملاء.**

Build order follows pipeline: normalization → passaging → atomization → excerpting → taxonomy → synthesizing. Each engine is built to its SPEC.md with schema validation on output. End-to-end validation produces the first KR-era gold baselines.

**Subsequent milestones:** Multi-source (M2) → Islamic sciences (M3) → second source type (M4) → autonomous discovery (M5) → full source diversity (M6) → comprehensive coverage (M7).

---

## Risk Register

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | SPEC writing reveals fundamental VISION concept is wrong | Medium | The SPEC-writing process IS the mitigation. Defects surface with implementation context, making fixes higher-quality than abstract auditing would produce. |
| R2 | Source identity decision (Round 1) cascades through all downstream schemas | Medium | Cascade is documented per-round. Each round applies the rename to its schema. By Round 6, all schemas are updated. |
| R3 | discover_structure.py boundary decision (Round 2) makes the passaging engine nearly empty | Low | An honest answer is better than a forced split. If passaging is thin, the SPEC says so. §13.2.4 already allows engine directories to exist for their conceptual role. |
| R4 | Phase 2 takes longer than expected (9 rounds) | Low impact (delays but no wasted work) | Rounds vary in weight: source (medium), normalization (heavy), passaging (light), atomization (medium), excerpting (heavy), taxonomy (medium), synthesis (light — no code), shared (medium), cross-cutting (light). Budget accordingly. |
| R5 | Claude Code introduces regressions in Phase 1 | Medium | Exit criteria require ≥1022 passing tests. Strict scope prevents behavior changes. |
| R6 | Already-audited §0–§4/§13 have issues visible only with engine expertise | Low | Phase 2 Round 9 includes a targeted re-check of previously audited sections. |
| R7 | Cross-SPEC inconsistencies despite pipeline ordering | Medium | Phase 3 is dedicated to catching these. Pipeline ordering minimizes but doesn't eliminate the risk. |
| R8 | Synthesizing engine SPEC is speculative (no code, no reference docs) | Medium | Keep it minimal — interface-focused. The SPEC's §9 (Current Implementation State) honestly says "no code exists." Detailed processing spec evolves when the engine is built. |

---

## Verification Matrix

| Phase | Verification |
|---|---|
| **Phase 1** | `pytest` shows ≥1022 pass, 1 fail (API), ≤14 skip. `ls library/sciences/imlaa/` shows tree.yaml, tree_history/, content/, SCIENCE.md. |
| **Phase 2 per round** | SPEC.md committed (non-stub, follows template). VISION corrections committed. Schema updates committed. `reference/kr_decisions.md` updated with any decisions. |
| **Phase 2 complete** | All 11 SPECs written. All VISION sections §5–§12 have been examined and corrected. `reference/kr_decisions.md` contains at least the source identity decision, the normalization/passaging boundary decision, and the atomization/excerpting separation decision. |
| **Phase 3** | `grep -r 'FORWARD-REF' engines/ shared/` returns 0. `reference/spec_consistency_report.md` exists with all boundaries verified. |
| **Phase 4** | Owner sign-off. No known defects. |
| **Phase 5** | `.claude/` populated. Build plan documented. First engine session can start. |
