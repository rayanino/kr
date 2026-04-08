# Excerpting Engine — محرك الاقتطاف

**Position:** Source ✅ → Normalization ✅ → **Excerpting** → Taxonomy → Synthesis.
**Absorbs:** passaging (Phase 1) + atomization (Phase 2). Architecture rationale: `experiments/architecture_test/ARCHITECTURE_DECISION.md`.

## Commands

```bash
test:  python -m pytest engines/excerpting/tests/ -x -v
lint:  ruff check engines/excerpting/
check: python -c "from engines.excerpting.src.phase1_assembly import run_phase1"
```

## Architecture

Three-phase pipeline. One source at a time. See `engines/excerpting/docs/architecture.md` for full data flow.

```
NormalizedPackage → Phase 1 (deterministic) → Phase 2 (LLM) → Phase 3 (enrichment) → ExcerptRecords
```

**Phase 1** (`phase1_assembly.py`): §4. Walk division tree → assemble text → merge tiny → split oversized → aggregate metadata → rebase layers → validate. No LLM. Fully testable.

**Phase 2** (`phase2_classify.py` + `phase2_group.py`): §5. Classify segments by scholarly function (16-type taxonomy) → group into teaching units. Two LLM calls per chunk via Instructor + OpenRouter.

**Phase 3** (`phase3_deterministic.py` + `phase3_enrichment.py` + `phase3_consensus.py` + `phase3_validation.py`): §7. Nine deterministic fields (F-DET-1–9) → LLM enrichment (one call per chunk) → consensus verification (different-provider model) → human gates → output validation.

Output: `writer.py` → `excerpts.jsonl` + `gate_queue.jsonl`.

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `SPEC.md` | 2856 | Behavioral authority (12 sections, §6 has 23 domain rules, §10.6 has 22 adversarial tests) |
| `contracts.py` | 1111 | All types: 2 enums, 12 sub-types, 4 main types, 7 LLM schemas, 28 error codes, 18 config params |
| `tests/conftest.py` | 184 | 4 factories: AssembledChunk, ClassifiedSegment, TeachingUnit, ExcerptRecord |
| `docs/architecture.md` | — | Module structure, data flow, build session plan |
| `docs/testing.md` | — | Test categories per file, fixture requirements |
| `docs/llm_trustworthiness_defenses.md` | — | **Sessions 4–6 MANDATORY.** Failure-mode matrix, Tier 1 deterministic defenses, empirical scan requirements |
| `docs/technology_survey.md` | — | Verified tool/library capabilities |
| `session-1-plan.md` | — | CC Session 1 directive (Phase 1 build) |

## Critical Constraints

- **Arabic diacritics:** Preserve byte-for-byte. No Unicode normalization (NFC/NFD/NFKC/NFKD).
- **Metadata:** Never delete upstream fields (D-023). Pass through everything from normalization.
- **Errors:** Fail loudly with SPEC §8 error codes. Never silently drop data.
- **OpenRouter only:** All LLM calls via OpenRouter. Pattern: `instructor.from_openai(openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=KEY), mode=instructor.Mode.JSON)`.
- **D-011:** No excerpt spans a chunk boundary. Enforced by construction (LLM sees one chunk).
- **EX-M-008:** Gate write failure → HALT. Invisible uncertainty > visible stop.
- **Step ordering (§4.1):** Footnote renumbering (§4.7) BEFORE text layer rebasing (§4.6).

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

## Model Configuration

Model roles verified empirically on 2026-03-28 against actual KR Arabic scholarly text via OpenRouter.

| Role | Model | Provider | Purpose |
|------|-------|----------|---------|
| Primary (classify + enrich) | `openai/gpt-5.4` | OpenAI | Phase 2 classification, Phase 2 grouping, Phase 3 enrichment |
| Verify | `anthropic/claude-opus-4.6` | Anthropic | Phase 3 consensus verification |
| Escalation | `mistralai/mistral-large-2411` | Mistral | Phase 3 disagreement adjudication |

Three-provider diversity (Anthropic → OpenAI → Mistral) ensures no single-provider outage blocks the pipeline. Gemini 3.1 Pro was rejected (fails structured output). Command A was rejected (no tool-use on OpenRouter).

## Current State

- **SPEC:** COMPLETE + HARDENING (2856 lines, FP-1 through FP-22 in §1.1b, §6.1-6.23 domain rules, ADV-E-01 through ADV-E-22)
- **Contracts:** COMPLETE (1111 lines, independently reviewed)
- **Phase 1:** COMPLETE (117 tests, 1,531 lines) — deterministic assembly + hardening
- **Phase 2:** COMPLETE (141 tests, 854 lines) — LLM classification + grouping + hardening
- **Phase 3.1:** COMPLETE (86 tests, 637 lines) — deterministic metadata assembly (10 functions, review + bugfix + hardening)
- **Phase 3.2:** COMPLETE (27 tests, ~300 impl lines) — LLM enrichment (enrich_chunk, apply_enrichment, run_phase3_enrichment, _merge_scholars)
- **Phase 3.3:** COMPLETE (33 tests, ~450 impl lines) — Consensus verification + human gates (verify_chunk, resolve_consensus, check_gate_triggers, run_consensus)
- **Phase 3.4:** COMPLETE (50 tests, ~350 impl lines) — validation (V-P3-1–9) + output writer (excerpts.jsonl, gate_queue.jsonl, V-P3-7 paranoid verification)
- **Phase 3 Orchestrator:** COMPLETE (25 integration tests, ~300 impl lines) — phase3_orchestrator.py + pipeline.py + end-to-end tests
- **Overnight Hardening:** 40+ additional edge case tests across all phases
- **DR28 Prompt Architecture:** COMPLETE (IU-1–IU-9) — CONSTITUTION in system, rules+input+reminders in user. Progressive disclosure for GROUP. 9 new tests.
- **Total:** 970+ tests, ~5,000 impl lines, 0 failures (970 deterministic, ~10 LLM integration)

### Recent Sessions (post-overnight hardening)
- **Preamble gap fix:** `_complete_division_tree()` inserts synthetic leaf nodes for parent content gaps (2-29% content was silently lost). ACCEPTED.
- **compute_page_range fix:** Partition `physical_pages` alongside `join_points` in split chunks. Defensive guard in `compute_page_range`. ACCEPTED.
- **EX-V-002 fix:** Compare `text_snippet` at min(snippet_len, 80) instead of fixed 80 — LLMs produce 51-74 chars, not exactly 80.
- **--max-chunks:** CLI argument for `run_integration_test.py` to limit LLM phases to N chunks.
- **First real LLM call:** Smoke test passed — 5 excerpts from ibn_aqil_v1 preface, 0 errors, 88s total via OpenRouter/Opus 4.6.

## Build Metrics Target

| Session | Scope | Est. impl lines | Est. tests |
|---------|-------|-----------------|-----------|
| 1 | Phase 1 (§4) | 800–1200 | ≥55 |
| 2 | Phase 2 (§5) | 600–900 | ≥40 |
| 3 | Phase 3 deterministic (§7.1) | 400–600 | ≥30 |
| 4 | Phase 3 LLM + consensus (§7.2–3) | 600–800 | ≥30 |
| 5 | Pipeline + writer + validation (§7.4) | 300–500 | ≥25 |
| 6 | Integration + cross-engine | — | ≥20 |

## Test Patterns

Follow normalization conventions:
- `conftest.py` factories for all complex types (ContentUnit, DivisionNode, NormalizedPackage)
- Real Arabic text from Shamela for domain tests; synthetic only for structural tests
- Regression baselines from `experiments/` directories (do NOT modify)
- Adversarial cases: ADV-E-01 through ADV-E-22 (§10.6)
- Error code tests verify: (a) code emitted, (b) message context, (c) recovery per §8.2

## Required Reading

**If working on foundations hardening (the current active lane):**
1. `reference/handoffs/excerpting_foundations_session3_kickoff_2026-04-04.md` — **START HERE**
2. `engines/excerpting/reference/HARDENING_SESSION_PROTOCOL.md` — the governing protocol (v4.0)
3. `SPEC.md` §1.1b — the 22 foundational principles (FP-1 through FP-22)
4. `engines/excerpting/reference/F1_F8_COMPLETE_ATOM_EXTRACTION.md` — the atom queue
5. `engines/excerpting/reference/QUEUE_AUDIT_RAW_VS_EXTRACTION.md` — 124 gaps to address

**For general excerpting work:**
1. `NEXT.md` — current task
2. `SPEC.md` — relevant section only (do NOT read all 2856 lines)
3. `contracts.py` — type signatures
4. `engines/normalization/contracts.py` — upstream types consumed
5. `experiments/architecture_test/extract_divisions.py` — validated reference implementations
6. `docs/llm_trustworthiness_defenses.md` — **MANDATORY for Sessions 4–6.**
7. `reference/excerpt_definition_canon/01_dossier.md` when the task touches excerpt boundaries, self-containment, function, study-readiness, or owner-facing excerpt quality.
