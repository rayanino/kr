# NEXT — Passaging Engine SPEC Design (Architect Session)

## Current Position

Source engine: **COMPLETE** (transition gate APPROVED, 2026-03-22)
Normalization engine: **COMPLETE** (transition gate APPROVED, 2026-03-22)

Both engines' output is proven at scale:
- Source: 566 tests, 274 LLM-probed books, €36.70 spent
- Normalization: 470 tests, 7,475 books at 100% success, 70/70 cross-engine validated
- Total: 1,036 tests, 0 failures

## What To Do

Begin passaging engine SPEC design per ENGINE_BUILD_BLUEPRINT.md Step 1.

The passaging engine has an existing 1,037-line SPEC draft (`engines/passaging/SPEC.md`) and stub implementation files from the initial design phase. These predate the normalization engine build and the established methodology — they need the full Blueprint Step 1 treatment.

### Step 1a: Cold Read and Defect Inventory

Read `engines/passaging/SPEC.md` in full. Check every section against the 7 silent failure patterns (`SILENT_FAILURES.md`). Create a defect inventory with CORRECTNESS vs STYLE classification.

### Step 1b: Owner Domain Comments

Check `engines/owner_comments.md` for any passaging-relevant comments.

### Step 1c: Research-Backed Resolution

For each CORRECTNESS defect: research before resolving. The passaging engine is deterministic (no LLM) — the SPEC should be tight enough that Claude Code can implement without judgment calls.

### Step 1d: Integrity Audit

Use `kr-integrity` on the resolved SPEC.

### Step 1e: Core vs Deferred Classification

Use `kr-core-extract`. The passaging engine's core is: take normalization output (content units) and produce passages suitable for excerpting. Deferred capabilities include adaptive passaging, cross-edition alignment, discourse optimization, etc.

### Step 1f: Build Prep

Use `kr-build-prep` to prepare stubs, test fixtures, and CLAUDE.md for Claude Code.

## Skills to Use

- `kr-integrity` — SPEC technical audit
- `kr-core-extract` — core vs deferred classification
- `kr-build-prep` — implementation preparation
- `kr-research` — if any SPEC capability requires technology research
- `critical-review` — self-review on every output
- `thinking-frameworks` — for architecture decisions

## Read First

1. This file (NEXT.md)
2. `engines/passaging/SPEC.md` — existing SPEC draft (1,037 lines)
3. `engines/passaging/contracts.py` — existing contract definitions
4. `engines/normalization/SPEC.md` §3 — normalization output contract (passaging input)
5. `engines/normalization/contracts.py` — NormalizedPackage, ContentUnit
6. `reference/ENGINE_BUILD_BLUEPRINT.md` §Step 1 — SPEC design methodology
7. `SILENT_FAILURES.md` — the 7 patterns to check against
8. `KNOWLEDGE_INTEGRITY.md` — corruption threats T-1 through T-7
9. `engines/normalization/LESSONS.md` — recommendations for passaging engine

## Pending Items (not blocking passaging SPEC)

- OpenRouter routing change: deferred until next LLM probes
- $95 LLM expansion: deferred, not needed for passaging
- 9 multi-layer disagreements: monitor during full collection run
- Source engine consolidated LESSONS.md: DONE (engines/source/LESSONS.md)
- Diacritics SPEC range: KEEP AS-IS (U+0656-U+065F are non-Arabic)
- Pageless books quality flag: defer to full collection run

## Do NOT Do

1. Do NOT spend money on LLM probes — passaging is deterministic
2. Do NOT modify source or normalization engine code — both are COMPLETE
3. Do NOT start Claude Code sessions without completing SPEC design first
4. Do NOT assume the existing passaging stubs are correct — they predate the methodology
