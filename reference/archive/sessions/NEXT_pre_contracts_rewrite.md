# NEXT — Excerpting Engine: SPEC Complete → Integrity Audit → Build Prep

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED at 5636ceb (Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis)
- Experiments: ✅ 23 divisions validated across 7 formats
- Format diversity evaluation: ✅ PASS (commit 1690cdf, revised 8035e01)
- **SPEC: ✅ COMPLETE** — 2387 lines, 12 sections. Coherence review passed.
- **CLAUDE.md: ✅ UPDATED** — reflects complete SPEC
- **contracts.py: STALE** — written for old 7-engine architecture, needs rewrite

## What to Do — Step 3: Integrity Audit → contracts.py → Build Prep

### Step 3a: kr-integrity Audit (Architect — 1 session)

Run the kr-integrity 8-lens audit on the complete SPEC. This is the quality gate between "SPEC is written" and "SPEC is implementation-ready."

**How:**
1. Invoke `kr-integrity` skill
2. Read `KNOWLEDGE_INTEGRITY.md` and `SILENT_FAILURES.md`
3. Audit the SPEC in chunks to avoid context degradation:
   - Chat 1: §1–§3 (Purpose, Contracts, Self-Containment)
   - Chat 2: §4–§5 (Phase 1, Phase 2 — the longest sections)
   - Chat 3: §6–§8 (Domain Rules, Phase 3, Error Handling)
   - Chat 4: §9–§10 (Deferred, Tests)
4. Every finding blocks. Fix findings in the SPEC before proceeding.

**Gate:** 0 unresolved findings from kr-integrity audit.

### Step 3b: Rewrite contracts.py (CC task — 1 session)

After the SPEC passes integrity audit, rewrite `engines/excerpting/contracts.py` to match the new SPEC. This is a CC task — prepare a handoff via kr-preparing-cc-handoffs.

**What contracts.py must define:**
- Enumerations: `ScholarlyFunction` (16 types from §2.3.1), `SelfContainmentLevel` (3 levels), `StructuralFormat` (7 types)
- Internal types: `AssembledChunk` (§2.3.2, 12 fields), `ClassifiedSegment` (§2.3.3, 7 fields), `TeachingUnit` (§2.3.4, 11 fields)
- Output type: `ExcerptRecord` (§2.2.2, 33 fields)
- Error codes: all 27 (EX-A/C/M/V/G) as constants or enum
- Invariant validators: functions that check I-AC-*, I-CS-*, I-TU-*, I-ER-*

**CC must also:**
- Keep Pydantic models for schema validation
- Ensure ExcerptRecord validates against §2.2.3 output invariants
- Add factory helpers for tests (following normalization `conftest.py` patterns)

### Step 3c: Build Prep (Architect — 1 session)

After contracts.py is updated, run `kr-build-prep` to prepare for implementation:
- Technology survey (what libraries for offset handling, Arabic word counting, etc.)
- Architecture stubs with type hints and docstrings
- Initial test skeleton (conftest.py, fixture structure)
- Updated CLAUDE.md with implementation guidance

**Gate:** NEXT.md updated to a build-phase directive for CC.

## After Step 3 — Build Phase

The excerpting engine build follows the normalization engine pattern:
- Session-based: one processing phase per CC session
- Phase 1 first (deterministic, unit-testable without LLM)
- Phase 2 after Phase 1 passes (requires mock LLM for testing)
- Phase 3 after Phase 2 passes (requires mock LLM + consensus logic)
- Integration testing after all 3 phases

Estimated: 5–7 build sessions + 1 code audit + 3-probe evaluation.

## Key Design Decisions (finalized in SPEC)

- **Internal data model: Option C (Hybrid)** — Phase 1→AssembledChunk, Phase 2a→ClassifiedSegment[], Phase 2b→TeachingUnit[], Phase 3→ExcerptRecord
- **Self-containment: 3-level** — FULL/PARTIAL/DEPENDENT
- **D-011: Division/chunk containment** — structurally enforced (LLM sees one chunk)
- **Phase 3 LLM: Per-chunk enrichment call** — inter-unit context improves quality
- **No proposed_leaf** — topic keywords only, taxonomy engine does placement
- **Consensus models:** enrichment=Opus 4.6, verification=GPT-4.1, escalation=Command A

## Critical Constraints

- **Budget: UNLIMITED.** Never mention cost as a factor.
- **All LLM calls through OpenRouter.** Model: anthropic/claude-opus-4.6.
- **D-011 = division/chunk containment.** Excerpts cannot span boundaries.
- **§4.B capabilities are deferred.** Core engine first (§9 in SPEC).
- **SPEC is behavioral authority.** When code and SPEC conflict, SPEC governs.

## Skills to Invoke

- For integrity audit: `kr-integrity` + `critical-review`
- For CC handoff: `kr-preparing-cc-handoffs` + `critical-review`
- For build prep: `kr-build-prep` + `kr-research` + `thinking-frameworks`

## Session History

- Session 0: SPEC_OUTLINE.md evaluation (Step 0)
- Session 1: §2.3, §2.1, §3, §4, §5 (5 sections, 1316 lines)
- Session 2: §6 (1 section, 155 lines)
- Session 3: §7, §2.2, §8 (3 sections, 826 lines)
- Session 4: §9, §10, §1 + coherence review + CLAUDE.md update (3 sections, 373 lines)

Total: 4 sessions, 12 sections, 2387 lines.

## Progress Tracker

- [x] Step 0: Evaluate SPEC_OUTLINE.md
- [x] Step 1: Write SPEC_OUTLINE.md
- [x] Step 2: Write all 12 SPEC sections + coherence review
- [x] Step 2 bonus: Update CLAUDE.md
- [x] Step 3a: kr-integrity audit (10 HIGH, 12 MEDIUM, 2 LOW findings — all fixed, 28 error codes)
- [ ] Step 3b: Rewrite contracts.py (CC task)
- [ ] Step 3c: Build prep (architecture stubs, test skeleton)
- [ ] Step 4+: Build (Phase 1 → Phase 2 → Phase 3 → integration)
