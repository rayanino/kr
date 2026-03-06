# NEXT SESSION

**Written by:** Session 2026-03-06 (User Model SPEC)
**Date:** 2026-03-06

## Immediate Task

Begin shared/scholar_authority SPEC — the canonical scholar identity component (D-025). This is the last shared component before the scholar interface SPEC.

**Definition of done — this session is complete when:**
1. shared/scholar_authority SPEC written with all 10 sections per SPEC template
2. RESOURCES.md updated with any new tools discovered
3. Any new decisions recorded in kr_decisions.md
4. Human gate SPEC §4.A.4 updated to reference user model for confidence data (minor update from D-042)
5. Changes committed and pushed

## Context

The user model SPEC is complete (370+ lines). It defines: six-level engagement tracking (unseen → viewed → read → studied → assessed → mastered → retained), knowledge state estimation via a four-signal weighted confidence score, FSRS v6 spaced repetition with parameter optimization, scholarly profile with expertise levels that subsume the human gate's confidence calibration (D-042), multi-dimensional gap analysis (topic, school, temporal, science), curriculum state management with taxonomy evolution detection, bookmarks and annotations (tarjih annotations as scholarly production), alert management with relevance scoring, and three transformative capabilities (scholarly growth trajectory analysis, prerequisite readiness prediction, knowledge decay prediction with prerequisite cascade). Key design decision: confidence calibration moves from human gate to user model (D-042).

Remaining shared component SPECs needed before the scholar interface:
- **shared/scholar_authority** — canonical scholar identities (D-025). The source engine SPEC §4.A.5 defines the source engine as the primary CREATOR of scholar records. The scholar authority component manages the REGISTRY: deduplication, enrichment, relationship tracking (teacher-student chains), and serving identity data to all consumers. No existing code.

After scholar_authority: the scholar interface SPEC (interface/scholar/), then the first SCIENCE.md.

## Files to Read — IN THIS ORDER

1. `reference/DOMAIN.md` — particularly the sections on scholars, teacher-student chains, and madhhab affiliations
2. `reference/USER_SCENARIOS.md` — Scenarios 2, 3, 4, 6 all reference scholar identity data (author profiles, teacher-student chains, scholarly standing)
3. `engines/source/SPEC.md` §4.A.5 — the source engine's scholar record creation rules. The scholar authority component must be compatible with what the source engine produces.
4. `engines/synthesis/SPEC.md` — the synthesizer consumes scholar metadata for entry generation. §4.A.4 (metadata-enriched synthesis) and §4.A.5 (verification) reference scholar identity.
5. `shared/scholar_authority/CLAUDE.md` — existing orientation file (if it exists)
6. `reference/RESOURCES.md` — check for Islamic scholar databases, OpenITI, and identity resolution tools
7. `VISION.md` — grep for "scholar authority", "canonical", "author", "teacher-student". Use extract_vision_sections.py for §7 (source architecture).

## Decisions Needed

- What is the canonical schema for a scholar record? The source engine SPEC §4.A.5 defines fields (canonical name, variants, kunya, laqab, nisba, dates, geographic data, school affiliations, teachers, students, known works, scholarly standing). But does the scholar authority component add anything beyond what the source engine captures?
- How does the scholar authority handle disambiguation? Islamic scholars often share names (there are many "ابن قدامة" figures across centuries). The source engine creates records; the scholar authority must prevent duplicates and resolve conflicts.
- Should teacher-student chains be a first-class data structure (a graph) or metadata on individual scholar records? The synthesizer uses these chains for narrative (see ENTRY_EXAMPLE.md: "Sibawayhi's student → الأخفش → الجرمي → المبرد → ابن السراج").

## Pending Owner Questions

None.

## What This Session Did

Completed shared/user_model SPEC (370+ lines, all 10 sections). Key designs: six-level engagement tracking, four-signal confidence scoring, FSRS v6 integration, expertise levels subsuming human gate confidence calibration (D-042), multi-dimensional gap analysis, curriculum state with taxonomy evolution detection, three transformative capabilities (growth trajectories, readiness prediction, decay prediction). Updated RESOURCES.md (py-fsrs, fsrs-optimizer, pyBKT evaluation), CLAUDE.md, STATUS.md.

## New Decisions

D-042: Owner confidence calibration moves from human gate to user model. Minor update needed to human gate SPEC §4.A.4 (can be done when starting scholar_authority, as a quick fix before the main work).
