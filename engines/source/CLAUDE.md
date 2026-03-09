# Source Engine — محرك المصادر

**Responsibility:** Acquiring raw sources, assigning identifiers, extracting and inferring metadata, freezing originals, evaluating trustworthiness, and producing the metadata record that every downstream engine consumes.
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Authoritative Files

| File | Role | Lines |
|------|------|-------|
| `SPEC_CORE.md` | **THE** specification. Behavioral authority. | ~1810 |
| `contracts.py` | Schema authority. Pydantic models for all data structures. | ~1020 |
| `prompts/inference_v1.py` | Draft LLM inference prompt (Step 2 iterates on this). | ~110 |

**⚠ `SPEC.md` is SUPERSEDED.** It is the pre-core-extraction full spec, kept only as an archive of deferred (Stage 2) capability descriptions. Do NOT read it for current architecture — read `SPEC_CORE.md`.

## Current State (as of 2026-03-09)

**Step 1 (SPEC hardening): COMPLETE.** 8 review passes, all defects resolved. SPEC_CORE.md is locked. Deterministic assumptions (A3 name matching, A4 trust weights) validated.

**Step 2 (LLM assumption testing): NEXT.** See `/NEXT.md` at repo root for the full test plan. Phase 0 (ground truth validation, eval harness, deterministic tests) is complete. Pre-flight readiness verified — see `/tests/STEP2_READINESS_VERIFICATION.md`. Phases 1–3 (API calls, multi-model testing, consensus pair selection) are pending.

**Pre-flight verification found and fixed:**
- 2 invalid Anthropic model IDs in test runner (fabricated snapshot dates)
- Scoring bug: name comparison penalized by death dates in ground truth (8/13 fixtures affected)
- Missing enum compliance checks for Step 1 fields (attribution_status, context_richness)
- Stale SPEC line number references in NEXT.md (sections shifted during Step 1)

**Step 3 (build prep): BLOCKED on Step 2.**

## Required Reading (for Claude Code)

1. `SPEC_CORE.md` — the specification (NOT SPEC.md)
2. `contracts.py` — Pydantic schemas, enums, all data models
3. `/NEXT.md` — current task directive with detailed test plan
4. `/KNOWLEDGE_INTEGRITY.md` — 7 corruption threats this engine must prevent
5. `/tests/SCORING_CRITERIA.md` — how to score LLM inference results
6. `/tests/eval_harness.py` — automated scoring script (run this, don't score manually)
7. `/tests/fixtures/GROUND_TRUTH.json` — expected answers (owner-validated)
8. `/tests/fixtures/EXTRACTED_DATA.json` — pre-extracted fixture data for prompts

## Review History (reference/)

Review artifacts from Step 1 are archived in `review/`. They document the audit trail but are not required reading for implementation:
- INTEGRITY_AUDIT.md, DOWNSTREAM_CONTRACT_AUDIT.md, STEP1_HARDENING.md, etc.
- CORE_VS_DEFERRED.md — classification of core vs Stage 2 features
- OWNER_SANITY_CHECK*.md — domain validation by the owner

## What This Engine Does (Core Only)

- Acquires sources from Shamela HTML exports and plain text (2 formats for Stage 1)
- Assigns three-tier identity: source_id, work_id, canonical_id (D-024)
- Extracts metadata from format-specific markup
- Infers metadata via LLM when extraction is insufficient (multi-model consensus)
- Detects duplicates via composite key matching
- Freezes the raw source immediately upon acquisition (SHA-256 hash)
- Evaluates trustworthiness: 3-tier classification (verified / flagged / owner_override)
- Produces metadata.json consumed by the normalization engine

## Key Domain Concepts

- **tahqiq**: Critical scholarly edition. The muhaqiq (editor) is NOT the author.
- **source_format**: Shamela HTML has specific structure (info.html + content.html)
- **trust_tier**: Based on publisher reputation, tahqiq quality, manuscript lineage
- **Three-tier ID**: source_id (this specific file), work_id (this book), canonical_id (this scholar's identity)

