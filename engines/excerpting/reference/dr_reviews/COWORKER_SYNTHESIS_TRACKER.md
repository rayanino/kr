# Coworker Synthesis Tracker — Feedback Collection Strategy

**Brainstorm session:** 2026-04-06/07
**Question:** What data does the pipeline need from the owner that CANNOT be derived from code, text analysis, or LLM inference alone?

## Dispatch Status

| # | Coworker | Angle | Dispatched | Received | Archived At | Verified |
|---|----------|-------|-----------|----------|-------------|---------|
| 1 | Claude DR | Owner decision map across all 5 engines | 2026-04-06 | 2026-04-07 | `DR18_claude_owner_decision_map.md` | YES (3 agents) |
| 2 | ChatGPT DR | Pattern gap analysis from campaign + bundles | 2026-04-06 | PENDING | — | — |
| 3 | Gemini DR | Islamic madrasa curriculum perspective | 2026-04-06 | PENDING | — | — |
| 4 | Codex CLI | Schema/contract analysis for unmet data deps | 2026-04-06 | 2026-04-07 | `CODEX_CLI_data_type_analysis.md` | YES (direct) |
| 5 | Gemini CLI | Islamic pedagogy + student learning methodology | 2026-04-06 | 2026-04-07 | `GEMINI_CLI_pedagogical_analysis.md` | YES (direct) |

## Per-Coworker Unique Findings

### Claude DR (DR18) — Received 2026-04-07
**Unique contribution:** Exhaustive 42-point decision map (31 found + 11 CC-identified gaps) across all 5 engines with:
- Per-decision automatable vs permanently-dependent classification
- Training data requirements (how many labeled examples for automation)
- Cross-engine dependency chain (11 dependencies)
- Critical path: SRC-D-004 → TAX-D-001 → SYN-D-001
- Tedious/summer partition: ~5h now + ~20-30h summer
- 12 permanent preferences that NEVER automate

**Corrections needed:** 2 claims wrong (SRC-D-001 not hardcoded; TAX-D-003 no priority evidence)
**Gaps found:** 11 decisions in shared components (human_gate, consensus, user_model, feedback)
**Verification:** `DR18_verification_notes.md`, `DR18_gap_analysis.md`
**Interview cross-ref:** `DR18_interview_crossref.md`

### ChatGPT DR — PENDING
**Expected contribution:** Error patterns from v2 campaign (2,303 excerpts) that require owner input. Bundle format evaluation. Collection priority based on error severity.

### Gemini DR — PENDING
**Expected contribution:** Islamic curriculum prerequisites. Knowledge sequencing. Study method taxonomy. Excerpt quality from student perspective. Minimum viable curriculum data per science.

### Codex CLI — Received 2026-04-07
**Unique contribution:** 11 policy families (DT-01 through DT-11) with dependency chains, minimum record counts, and questionnaire gap analysis. Fundamentally different angle from DR18 — maps data TYPES rather than decision POINTS.
- DT-01 (user model) identified as ROOT dependency — all other decisions depend on it
- DT-02 (quality rubric S-1) shows "Not yet defined" — priority order among quality dimensions unmapped
- DT-05/06/07 (evidence, khilaf, genre) are entirely unique to Codex — DR18 missed these as structured data types
- DT-08 (study-readiness) correctly SEPARATED from self-containment via FP-18
- TEAM_TRANSLATION_GUIDE.md has ZERO FP-13..22 mappings (pre-hardening gap)
- FP operationalization verdict: only FP-8 and FP-18 need owner calibration
- **Two-layer insight:** Policy layer (what owner WANTS) precedes Decision layer (what pipeline NEEDS)

**Corrections:** None — all claims verified (5/5 confirmed, 1 plausible).
**Disagreements with DR18:** 4 identified and resolved (see CODEX_CLI_verification_crossref.md).
**Verification:** `CODEX_CLI_verification_crossref.md`

### Gemini CLI — Received 2026-04-07
**Unique contribution:** Student-first pedagogical analysis grounded in talaqqi/hifz/fahm. 9 findings unique to Gemini, most architecturally disruptive of the three reports:
- Per-science study MODE choices (madhhab target, munazarah vs qawa'id, shubuhat exposure)
- **CHALLENGES FP-1:** qa'idah+shahid may need separation for flashcard memorization
- Genre override rules: matn (zero truncation), hashiyah (pedagogical filtering), mukhtasar (exception-pulling)
- Proof sourcing (FP-7): book-preserved vs fetched — architectural cross-reference decision
- 2 genuine pipeline gaps: cognitive complexity grading (no difficulty dimension), active recall output format
- 10 new data types identified (GEM-01 through GEM-10): 5 TEDIOUS-NOW, 3 NON-TEDIOUS, 2 SUMMER

**Corrections applied:** Prerequisite sequencing PARTIALLY WRONG — user_model SPEC has full curriculum infrastructure (§4.A.5, §4.B.2) SPECIFIED but not implemented.
**Verification:** `GEMINI_CLI_verification_crossref.md`

## Synthesis Protocol

When all 5 (or 4 with documented gap after 48h timeout) arrive:
1. Each report: save → verify (explore agent) → annotate corrections → cross-ref with interview
2. Merge unique findings into unified decision inventory
3. Deduplicate overlapping findings (expected between Claude DR + Codex CLI)
4. Identify DISAGREEMENTS between coworkers (e.g., tedious/summer classification)
5. Produce `FINAL_DATA_REQUIREMENTS.md` — the authoritative list of all owner data needed
6. Produce `COLLECTION_ROADMAP.md` — the 3-month schedule
7. Update the requirements document at `docs/brainstorms/` for `/ce:plan` handoff
