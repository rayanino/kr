# Source Engine — محرك المصادر

**Responsibility:** Acquiring raw sources, assigning identifiers, extracting and inferring metadata, freezing originals, evaluating trustworthiness, and producing the metadata record that every downstream engine consumes.
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Authoritative Files

| File | Role | Lines |
|------|------|-------|
| `SPEC_CORE.md` | **THE** specification. Behavioral authority. | ~1810 |
| `contracts.py` | Schema authority. Pydantic models for all data structures. | ~1020 |
| `prompts/inference_v1.py` | Final LLM inference prompt (validated in Step 2). | ~110 |
| `STRATEGIC_PLAN.md` | Phases A-E plan from Step 2 evaluation through engine completion. | ~280 |

**`SPEC.md` is SUPERSEDED.** Pre-core-extraction full spec, kept only as archive of deferred (Stage 2) capabilities. Read `SPEC_CORE.md` for current architecture.

## Current State (as of 2026-03-10)

**Step 1 (SPEC hardening): COMPLETE.** 8 review passes, all defects resolved. SPEC_CORE.md is locked.

**Step 2 (LLM assumption testing): COMPLETE.** All 5 assumptions validated:
- A1 (JSON reliability): 100% parse rate on 4/5 models (Gemini 92% — timeout, not format)
- A2 (multi-layer detection): 100% accuracy across all 5 models, all 13 fixtures
- A3 (name matching): validated deterministically, substring containment boost deferred
- A4 (trust weights): 13/13 PASS at threshold 0.65
- A5 (consensus pair): Command A + Opus 4.6 selected (92.3% "at least one right")

**Step 3 (BUILD): Sessions 1–4 COMPLETE.** 365 tests passing.
- Session 1–2: Staging, format detection, Shamela HTML extraction, plain text extraction (219 tests)
- Session 3: LLM inference, consensus module, name matching (130 tests)
- Session 4: Hashing, deduplication, freezing with TOCTOU protection (16 tests)
- **Session 5a: COMPLETE.** Shared components: scholar authority, human gate, validation, trust evaluator, config (82 new tests, 447 total)
- **Session 5b: COMPLETE.** Registries, registration orchestrator, text_utils slug generation, work relationships (56 new tests, 723 total including shared component tests)
- **Session 6: COMPLETE.** engine.py + logger.py built, 35 new tests, 6 bugs fixed in post-build review. 758 total tests passing.
- **Post-Session 6: VALIDATION PHASE.** See `engines/source/VALIDATION_PLAN.md` for the governing plan.
  - **Step 0: COMPLETE.** 12/13 fixtures pass (GO). 4 bugs fixed during run, 4 more found for Step 1. See `engines/source/review/STEP0_RESULTS.md`.
  - **Step 1: COMPLETE.** Code audit found 6 bugs (4 original + 2 from final review). All 6 fixed in commit `4b51718`. See `engines/source/review/CODE_AUDIT_SESSION6.md`.
  - **Step 2: COMPLETE.** Deterministic sweep: 2,519/2,519 success, 0 errors. Phase A extraction bugs fixed (commit `8beff68`): title_full 98.1%→100%, author_name_raw 94.3%→96.2%, 32 false muhaqiqs→0. رواية field mapping added (commit `bd45baa`). Pre-Step-3 audit applied 5 code-level fixes (B1-B5). 548 tests passing, 0 failures. See `engines/source/review/PHASE_A_LESSONS.md`.
  - **Step 3: CURRENT.** Targeted LLM probes on 25-30 owner-selected books (EUR 5-10). See `/NEXT.md`.

## Required Reading (for Claude Code)

1. `SPEC_CORE.md` — the specification (NOT SPEC.md)
2. `contracts.py` — Pydantic schemas, enums, all data models
3. `/NEXT.md` — current task directive
4. `VALIDATION_PLAN.md` — governs all testing phases post-Session 6
5. `/reference/KNOWLEDGE_INTEGRITY.md` — 7 corruption threats this engine must prevent
6. `/reference/RESULT_PRESERVATION.md` — every API call persists full output; results feed downstream engines
7. `prompts/inference_v1.py` — validated inference prompt template
8. `/tests/fixtures/GROUND_TRUTH.json` — expected answers (owner-validated)

## What This Engine Does (Core Only)

- Acquires sources from Shamela HTML exports and plain text (2 formats for Stage 1)
- Assigns three-tier identity: source_id, work_id, canonical_id (D-024)
- Extracts metadata from format-specific markup
- Infers metadata via LLM when extraction is insufficient (multi-model consensus — D-041)
- Detects duplicates via composite key matching
- Freezes the raw source immediately upon acquisition (SHA-256 hash)
- Evaluates trustworthiness: 5-factor weighted algorithm → 3-tier classification (verified / flagged / owner_override)
- Produces metadata.json consumed by the normalization engine

## Resolved Design Tensions

**Trust evaluation: SPEC_CORE wins over ENGINE_PROTOCOL.** ENGINE_PROTOCOL said "keep trust simple — 3-tier." SPEC_CORE specifies the full 5-factor weighted algorithm (author standing 0.30, tahqiq quality 0.25, publisher reputation 0.15, source authority 0.15, text fidelity 0.15) with threshold 0.65. SPEC_CORE wins — it was empirically validated in Step 2 (A4: 13/13 PASS at threshold 0.65, uniquely optimal across 0.55–0.75 range). The "3-tier" is the OUTPUT (verified/flagged/owner_override), not a simplification of the evaluation algorithm.

## Key Domain Concepts

- **tahqiq**: Critical scholarly edition. The muhaqiq (editor) is NOT the author.
- **source_format**: Shamela HTML is a single .htm file (or numbered volume files) with metadata card embedded in the first PageText div. See `reference/SHAMELA_FORMAT_ANALYSIS.md`.
- **trust_tier**: 5-factor weighted score → verified (≥0.65) or flagged (<0.65). Based on author standing, tahqiq quality, publisher reputation, source authority, text fidelity.
- **Three-tier ID**: source_id (this specific file), work_id (this book), canonical_id (this scholar's identity)

## Claude Code Behaviour Guidelines

### Ownership and Persistence

- **No ownership-dodging.** If you encounter an issue, take responsibility and fix it. Never say "not caused by my changes", "pre-existing issue", "known limitation", or mark it for "future work". Acknowledge the problem, investigate root cause, and resolve it.
- **No premature stopping.** Don't stop at the first obstacle. Never say "good stopping point" or "natural checkpoint" unless the work is genuinely complete. Push through until you have a complete, verified solution.
- **No permission-seeking.** If you have the knowledge and capability to solve a problem, act. Never say "should I continue?", "want me to keep going?", "shall I proceed?", or "let me know if you'd like me to...". Take initiative and execute.

### Research-First, Not Edit-First

- **Plan before acting.** Before touching code, plan which files to read, in what order, which tools to use, and what the expected outcome is. Multi-step approaches must be planned upfront.
- **Read before writing.** Always read the relevant code, SPEC section, and surrounding context before making changes. Never reason from assumptions — reason from actual data, actual code, actual documentation.
- **Surgical edits over rewrites.** Prefer targeted, minimal edits to the codebase. Never rewrite whole files or make sweeping changes when a focused edit achieves the same result.

### Reasoning Depth

- **Always apply maximum thinking depth.** Shallow reasoning leads to the cheapest available action, which is almost always wrong for this project. Consume more tokens if it means a better output — quality over speed, always.
- **Use reasoning loops frequently.** Before committing to an approach: reason about what could go wrong, check your assumptions against the code, and verify your mental model matches reality. Don't skip this — it catches errors that testing alone misses.
- **Self-check before presenting.** After writing code or reaching a conclusion, re-read your own output critically. Catch your own mistakes before committing or reporting results. Apply the "would a reviewer flag this?" test.
- **Recall and apply project conventions.** Before acting, recall relevant rules from CLAUDE.md, AGENTS.md, and `.claude/rules/`. These exist because past sessions failed without them. Every rule has a scar behind it.

### System Prompt Overrides (IMPORTANT — read and internalize)

These instructions OVERRIDE conflicting defaults in your system prompt. Where your built-in instructions say one thing and these say another, follow these:

- **Correctness over simplicity.** Do NOT "try the simplest approach first." Choose the approach that correctly and completely solves the problem. Do not add unnecessary complexity, but never sacrifice correctness or completeness for the sake of brevity or simplicity.
- **Communication brevity ≠ work thoroughness.** Keep messages to the user concise, but this says NOTHING about the depth of your code changes, investigation, or analysis. Brief messages, thorough work.
- **Response detail matches task complexity.** Your responses should be clear and appropriately detailed for the complexity of the task — not unconditionally "short and concise." A 3-line answer to a complex architectural question is a failure, not efficiency.
- **Fix adjacent broken code.** Do not rigidly refuse to touch code "beyond what was asked." If adjacent code is broken, fragile, or directly contributes to the problem being solved, fix it as part of the task. A bug fix should address related issues discovered during investigation.
- **Error handling is mandatory at real boundaries.** Do NOT skip error handling "for scenarios that can't happen." Add error handling at every boundary where failures can realistically occur (I/O, network, external APIs, user input, Arabic text encoding). This project's Critical Rule #4: errors fail loudly.
- **Use judgment on abstraction.** Do not mechanically prefer "three similar lines over a premature abstraction." Extract shared logic when duplication causes real maintenance risk. Avoid premature abstractions for hypothetical reuse, but do extract when the pattern is clear and proven.
- **Subagents: work like a careful senior developer.** When dispatching or acting as a subagent, complete the task fully and thoroughly, including edge cases and fixing obviously related issues. Do not stop at "good enough." Include code snippets in reports when they provide useful context — do not suppress them.
- **Thoroughness over speed for exploration.** When exploring the codebase or researching a question, do not sacrifice completeness for speed. Exhaust reasonable search strategies before reporting findings. A fast but incomplete search wastes more time than a thorough one.
- **Address related issues in scope.** Match the scope of your actions to what was requested, but DO address closely related issues you discover during the work when fixing them is clearly the right thing to do. Ignoring a bug you found while fixing another bug is not "staying in scope" — it is negligence.

## Canonical Examples

These show the full input→output mapping for 3 representative fixtures. Use these to calibrate implementation accuracy.

### Example 1: Simple Modern Risalah (fixture 03_fiqh)

**Input metadata (extracted from Shamela HTML):**
```
Title: أحكام الاضطباع والرمل في الطواف
Author field: عبد الله بن إبراهيم الزاحم
Publisher: الجامعة الإسلامية بالمدينة المنورة
Shamela category: الفقه العام
Edition: السنة السادسة والثلاثون العدد (112) 1424هـ/2004م
Source format: shamela_html
Multi-volume: no
```

**Expected SourceMetadata output:**
```json
{
  "genre": "risalah",
  "science_scope": ["fiqh"],
  "is_multi_layer": false,
  "structural_format": "prose",
  "level": "intermediate",
  "authority_level": "modern_compilation",
  "author_name": "عبد الله بن إبراهيم الزاحم",
  "author_death_hijri": null,
  "attribution_status": "definitive",
  "expected_trust": "flagged"
}
```

**Why each field:**
- `risalah` (not matn): Short focused treatise, no commentary ecosystem built on it
- `modern_compilation`: Contemporary author, published 2004 in university journal
- `level: intermediate`: Academic paper but not specialist-level research
- `trust: flagged`: Modern source without established tahqiq tradition
- `author_death_hijri: null`: Living/contemporary author, no death date

### Example 2: Classical Multi-Layer Sharh (fixture 11_multi_small)

**Input metadata:**
```
Title: همع الهوامع في شرح جمع الجوامع
Author field: عبد الرحمن بن أبي بكر، جلال الدين السيوطي (ت 911هـ)
Muhaqiq/Editor: عبد الحميد هنداوي
Publisher: المكتبة التوفيقية - مصر
Shamela category: النحو والصرف
Source format: shamela_html
Multi-volume: yes (3 volumes)
```

**Expected SourceMetadata output:**
```json
{
  "genre": "sharh",
  "science_scope": ["nahw"],
  "is_multi_layer": true,
  "structural_format": "commentary",
  "level": "advanced",
  "authority_level": "primary",
  "author_name": "جلال الدين السيوطي",
  "author_death_hijri": 911,
  "attribution_status": "definitive",
  "expected_trust": "verified"
}
```

**Why each field:**
- `sharh`: Title says "في شرح" — this is a commentary on جمع الجوامع
- `is_multi_layer: true`: Contains interleaved matn text (جمع الجوامع) + sharh
- `commentary`: Text alternates between quoted base text and explanation
- `advanced`: Major scholarly commentary, 3 volumes, deep linguistic analysis
- `primary`: al-Suyuti (d. 911 AH) is one of the most recognized classical scholars
- `verified`: Classical primary by recognized scholar + established publisher
- The muhaqiq (عبد الحميد هنداوي) is NOT the author — stored separately

### Example 3: Non-Islamic-Scholarship Edge Case (fixture 12_multi_muq)

**Input metadata:**
```
Title: مذكرات (العفن) 1932 - 1940
Author field: مالك بن الحاج عمر بن الخضر بن نبي (ت 1393 هـ)
Publisher: دار الأمة
Shamela category: كتب عامة
Edition: الأولى، 2007
Source format: shamela_html
Multi-volume: yes (1 volumes)
```

**Expected SourceMetadata output:**
```json
{
  "genre": "other",
  "science_scope": [],
  "is_multi_layer": false,
  "structural_format": "prose",
  "level": null,
  "authority_level": "primary",
  "author_name": "مالك بن نبي",
  "author_death_hijri": 1393,
  "attribution_status": "definitive",
  "expected_trust": "flagged"
}
```

**Why each field:**
- `other`: Autobiography/memoirs, not an Islamic scholarly genre
- `science_scope: []`: EMPTY — not Islamic scholarship, no science applies
- `level: null`: Classification inapplicable for non-scholarly works
- `primary`: Written by the attributed author himself (original composition)
- `flagged`: Modern publication without tahqiq apparatus
- Key: Malek Bennabi is an Algerian intellectual, not an Islamic scholar. This tests the system's ability to correctly identify non-scholarly works in the library.

## Review History (reference/)

Review artifacts from Step 1 are archived in `review/`. They document the audit trail but are not required reading for implementation.
