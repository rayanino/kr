# NEXT SESSION

**Written by:** Session 2026-03-04 (environment setup)
**Date:** 2026-03-04

## Immediate Task

Start the source engine SPEC (Phase 2, Round 1 per the archived roadmap).

**Output file:** `engines/source/SPEC.md` (overwrite the existing 3-line stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/source/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/source/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey
5. VISION.md §7.1–§7.4 defect ledger produced (corrections applied or queued for owner approval)
6. `schemas/source_metadata.json` has proposed updates documented (actual schema change can be deferred, but the SPEC must specify what the schema SHOULD contain)
7. `NEXT.md` is overwritten with handoff for the next session (normalization engine SPEC)
8. Self-review checklist (all 18 criteria) passed — defects fixed before commit
9. All changes committed and pushed as a single coherent commit

## Context

No SPECs have been written yet. Phase 1 (structural cleanup) is complete. The source engine is the pipeline entry point — no upstream dependencies.

The roadmap (`reference/archive/kr_definitive_roadmap_v2.md`) has detailed guidance for Round 1 under "Round 1: Source Engine", including key questions and schema impact notes. Consult it if useful, but it predates the design philosophy and scholar interface — don't let it constrain your thinking.

## Files to Read — IN THIS ORDER

The order matters. Think about what the engine SHOULD be before seeing what it currently IS.

**Step 1 — Understand the vision and the user (read these FIRST):**
1. `reference/DOMAIN.md` — the core identity ("KR IS Rayane's knowledge") and scholarly domain grounding. This shapes every design decision. Pay special attention to "Design Implications" — these are concrete requirements for the source engine.
2. `reference/USER_SCENARIOS.md` — 8 concrete scenarios showing what Rayane actually experiences. These are your acceptance tests. Every feature in your SPEC must serve at least one scenario. List which scenarios in §1.
3. `reference/ENTRY_EXAMPLE.md` — what a finished KR entry looks like. This is the END PRODUCT the entire pipeline serves. Notice what makes it transformative vs. flat — especially how metadata (author dates, teacher-student chains, school affiliations) enables the scholarly narrative.

   **Comprehension check after reading:** Can you list 5 things in the target entry that came from METADATA (not from the excerpt text itself)? If you can't, reread it. Those 5 things define what your source engine's metadata architecture must capture.

4. `reference/PIPELINE_TRACE.md` — traces one passage through ALL seven engines, showing what each stage receives, produces, and what metadata accumulates. Critical for understanding why metadata must flow through without loss (D-023). Together with the entry example, this shows the complete picture: raw source → metadata-rich entry.

**Step 2 — Understand the architecture:**
5. `VISION.md` §7.1–§7.4 and §2 → run `python3 scripts/extract_vision_sections.py 7 2`
6. `schemas/source_metadata.json` (234L) — current output schema **(ABD-era — treat as "what exists," not "what to build")**
7. `schemas/SCHEMA_ANALYSIS.md` (329L) — pipeline schema overview **(has D-019 and D-023 warnings at top)**

**Step 3 — Now look at existing code and reference (after you've formed your own vision):**

These are all ABD-era artifacts. ABD was a narrow Shamela-only tool; its decisions have zero authority (D-019). Read them to understand what code exists, NOT as a template for what to build. If your vision from Steps 1-2 conflicts with what ABD does, your vision wins.

**Context note:** Step 3 is ~37K tokens — the largest single chunk. If you've already formed a strong vision from Steps 1-2 and context is getting tight, you can skim Step 3 selectively: read `ABD_INTAKE_SPEC.md` for the metadata model outline, skim `intake.py` for the flow, and skip `enrich.py` and `corpus_audit.py`. The SPEC you write should be driven by your Steps 1-2 vision, not by ABD's implementation.

8. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L) — ABD-era spec for Shamela intake only
9. `engines/source/reference/edge_cases.md` (127L) — known edge cases (Shamela-specific)
10. `engines/source/src/intake.py` (1476L) — current source ingestion code (Shamela only)
11. `engines/source/src/enrich.py` (580L) — metadata enrichment (Shamela only)
12. `engines/source/src/corpus_audit.py` (228L) — corpus validation

**Step 4 — Research:**
13. `reference/RESOURCES.md` — cataloged tools and possibility research starting points
14. Then do web searches: resource survey + possibility research per the workflow

**CRITICAL: After Step 1 and before Step 3, pause and think.** Write down (in your working memory, not a file) what the source engine SHOULD be if you could design it from scratch for the goal of making Rayane an unprecedented scholar. THEN read the existing code and see how it compares. Don't let the existing code shrink your vision.

## Known VISION §7 Gaps (for SPEC → VISION correction step)

VISION §7 explicitly defers 8 topics to "Level 2" (the SPEC). The SPEC must resolve all of them:
- Deduplication criteria and registry structure
- Repository-specific interface logic
- Relevance evaluation criteria
- Metadata fields, data types, and validation rules
- Enrichment write-back mechanism
- Trustworthiness evaluation criteria and threshold
- Normalized package contents and schema
- Discovery strategies

VISION §7 is SILENT on topics DOMAIN.md requires:
- Work-to-work relationships (sharh→matn chains) — not mentioned at all
- Author disambiguation — not mentioned at all
- Tahqiq quality criteria — mentioned only as "editor (محقق)" in metadata
- Edition variant tracking — mentioned only as "edition information"

These are gaps the SPEC fills, not contradictions the SPEC corrects.

## Decisions Needed

- Source identity model: what is a "source"? Does `book_id` → `source_id`? Multi-volume works?
  **Known tension:** VISION §2.5 defines "Work" (مؤلَّف) narrowly as linking volumes of a multi-volume work. DOMAIN.md defines it broadly as the abstract intellectual creation (grouping different tahqiq editions). Both concepts are real — the architect must resolve whether `work_id` covers both or whether two levels of grouping are needed.
- Source engine output: just `source_metadata.json` + frozen file, or other artifacts?
- Source registry: how does `library/sources/registry.yaml` work?
- What metadata model does KR need? (The current schema has Shamela-specific fields from ABD — design from first principles for ALL source types, not from the existing schema.)
- Manual acquisition workflow: owner provides scans/photos of physical books (no digital version exists), or files manually downloaded from login-gated sites. How does the source engine ingest these? What metadata can be auto-extracted vs. what must the owner provide?
- Scholar authority interface: the source engine creates/updates scholar records in the scholar authority model. Define: what data does the source engine write? What happens when a record already exists (merge? skip? overwrite?). How does the source engine handle ambiguous authors (e.g., "ابن حجر" = two different scholars)?
- What transformative capabilities does this engine provide? (§4.B — your ideas)
- What does the source engine produce that the scholar interface (interface/scholar/) will need? Design with that consumer in mind.

**ABD legacy rule (D-019):** The existing code and reference docs are from ABD, a narrow Shamela-only tool. ABD design decisions have ZERO authority in KR. Read the code and reference docs to understand what currently exists, but design the SPEC from first principles for a system that acquires sources from ANY scholarly repository in ANY format.

**Pipeline priority (owner directive):** Don't over-engineer the source engine. The critical path starts AFTER a source is received — normalization through synthesis is where KR becomes transformative. The source engine's first version should provide a minimum viable acquisition path (accept files the owner provides + basic metadata). Autonomous discovery, multi-repository crawling, and expanded format support are expansion features for later. Spend your design energy on getting the source identity model and metadata architecture RIGHT (these affect every downstream engine), not on elaborate acquisition workflows.

**Note:** The scholar interface (interface/scholar/), user model (shared/user_model/), and scholar authority model (shared/scholar_authority/) were added as extensions beyond the original 7+4 architecture. The scholar authority model is especially relevant to the source engine — it is the centralized registry where every scholar encountered across ALL sources is mapped to a canonical identity. The source engine is the PRIMARY CREATOR of scholar authority records (when processing a new source, it creates/updates the author's canonical record). See DOMAIN.md "Scholar Identity" section. Their SPECs should be written after the 7 engine SPECs and 4 shared component SPECs, or when the architect judges it's the right time.

## Pending Owner Questions

- **Entry language:** Should entries be in Arabic, English, or bilingual? Arabic preserves scholarly precision (technical terms have exact meanings in Arabic that English translations approximate). English may be clearer for explanatory content. The SPEC needs to know: what language does the owner want to READ entries in? This affects the synthesizing engine's output format and the scholar interface's presentation.

The SPEC process will likely surface additional domain questions about Islamic scholarly source types and the owner's acquisition preferences.

## New Decisions Since Last SPEC Session

No previous SPEC sessions — this is the first. Read all of kr_decisions.md (D-001 through D-023). Pay special attention to D-018 (core identity), D-019 (ABD legacy rule), D-020 (pipeline priority), D-021 (owner's core frustration), D-022 (book briefing), and D-023 (metadata as synthesis fuel).

## What the Last Session Did

Set up the complete autonomous working environment: design philosophy (Claude as creative mind), core identity (KR IS Rayane's knowledge), domain primer, user scenarios, scholar interface, user model, 25-criterion Perfection Standard, session mechanics.

## Quality Note

This is the first SPEC. Every future session will read it and calibrate to its quality level. If this SPEC is conservative and incremental, every subsequent SPEC will be too. If this SPEC is ambitious, deeply-researched, and precisely specified, the bar rises for the entire project. Write the SPEC you'd want to read if you were Session 2.
