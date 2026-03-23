# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Transforming normalized text divisions into self-contained, attributed, metadata-rich excerpts — the building blocks of Rayane's knowledge library.
**Position:** Third engine in the pipeline: Source ✅ → Normalization ✅ → **Excerpting** → Taxonomy → Synthesis.

## What This Engine Absorbs

The excerpting engine absorbs two previously separate engines:
- **Passaging** (deterministic): cross-page text assembly, division merging, splitting → Phase 1
- **Atomization** (LLM-driven): segment classification by scholarly function, teaching unit grouping → Phase 2

Architecture rationale: `experiments/architecture_test/ARCHITECTURE_DECISION.md`

## SPEC

**`engines/excerpting/SPEC.md`** — 2343 lines, 12 sections, COMPLETE.

| Section | What It Specifies |
|---------|-------------------|
| §1 | Purpose, scope, pipeline position, D-011 constraint, T-1–T-7 defense mapping |
| §2.1 | Input contract: NormalizedPackage fields consumed |
| §2.2 | Output contract: ExcerptRecord (33 fields, 7 invariants), downstream consumer requirements |
| §2.3 | Internal data model: AssembledChunk → ClassifiedSegment → TeachingUnit → ExcerptRecord |
| §3 | Self-containment standard: FULL/PARTIAL/DEPENDENT, 5 formal criteria (C-SC-1–5) |
| §4 | Phase 1 — deterministic preprocessing: assembly, merge, split, rebase, validate (V-P1-1–6) |
| §5 | Phase 2 — LLM teaching unit extraction: classify (2a) + group (2b), offset normalization (V-P2-1–19) |
| §6 | Domain-specific rules: 22 rules across DP/LA/EV/IR/VC/QM categories |
| §7 | Phase 3 — metadata enrichment: 9 deterministic fields, LLM enrichment, consensus verification (V-P3-1–9) |
| §8 | Error handling (27 codes) and configuration (20 parameters) |
| §9 | Deferred capabilities: 16 capabilities (DC-01–DC-16) with extension hooks |
| §10 | Test requirements: fixture specs, adversarial cases (ADV-E-01–12), C-7 mitigation |

**The SPEC is the behavioral authority.** When code behavior and SPEC conflict, the SPEC governs.

## Input Boundary

Normalized packages from the normalization engine:
- `library/sources/{source_id}/normalized/manifest.json` — NormalizedManifest (division tree, layer map, structural format, quality report)
- `library/sources/{source_id}/normalized/content.jsonl` — ContentUnit stream (one per physical page)

Schema: `engines/normalization/contracts.py`

## Output Boundary

Excerpt stream consumed by the taxonomy engine:
- `library/sources/{source_id}/excerpts/excerpts.jsonl` — one ExcerptRecord per line (§2.2)
- `library/sources/{source_id}/excerpts/gate_queue.jsonl` — human gate entries (EX-G-001/002/003)

Schema: `engines/excerpting/contracts.py`

## Internal Architecture (Three Phases)

**Phase 1 — Deterministic Preprocessing (§4):**
- Walk division tree → identify leaf divisions
- Assemble text from content units using boundary_continuity
- Merge tiny divisions (< TINY_DIVISION_WORDS) with adjacent siblings
- Split oversized divisions (> OVERSIZED_DIVISION_WORDS) at structural markers
- Rebase text_layers to assembled-text offsets
- Aggregate content_flags, collect footnotes, align headings
- Self-validation: V-P1-1 through V-P1-6
- Fully deterministic, no LLM calls, independently unit-testable

**Phase 2 — LLM Teaching Unit Extraction (§5):**
- Phase 2a: classify segments by scholarly function (16-type taxonomy)
- Phase 2b: group segments into self-contained teaching units
- Offset normalization: align LLM word boundaries to actual tokens
- Coverage verification: V-P2-1 through V-P2-19
- D-011 enforced structurally: LLM sees one chunk at a time

**Phase 3 — Metadata Enrichment (§7):**
- Deterministic assembly: 9 fields (F-DET-1–9) computed without LLM
- LLM enrichment: per-chunk call adding topic, school, evidence, cross-refs
- Consensus verification: different-provider model verifies attribution + school
- Human gates: EX-G-001 (attribution), EX-G-002 (dependent SC), EX-G-003 (school conflict)
- Self-validation: V-P3-1 through V-P3-9

## Key Constraints

- **D-011:** No excerpt spans a division or chunk boundary. Enforced by construction, not by validation.
- **OpenRouter only:** All LLM calls go through OpenRouter. Direct API calls are not permitted.
- **Domain rules (§6):** 22 rules that constrain Phase 2 behavior. §6 is the formal spec; the Phase 2 prompt implements it.
- **Self-containment (§3):** Every teaching unit is evaluated FULL/PARTIAL/DEPENDENT. DEPENDENT triggers a human gate.
- **Error severity:** EX-M-008 (gate entry not written) halts processing. Invisible uncertainty is more dangerous than a visible stop.

## Current State

- **SPEC:** COMPLETE (2343 lines, 12 sections). Pending: kr-integrity audit → contracts.py update → implementation.
- **Contracts:** Stale — written for old 7-engine architecture. Needs rewrite to match new SPEC (§2.3 data model + §2.2 output contract).
- **Code:** None. ABD-era files in `reference/archive/abd_code/excerpting/` are historical reference only.
- **Tests:** None.

## Test Patterns (from normalization engine)

When building tests, follow normalization conventions:
- `conftest.py`: factory helpers (`_make_source_metadata()`, `_make_normalized_package()`)
- Fixtures: real Arabic text from Shamela exports; synthetic text only for structural tests
- Regression baselines: `experiments/format_diversity_test/fixtures/` and `experiments/architecture_test/`
- Adversarial cases: ADV-E-01 through ADV-E-12 (§10.6)

## Required Reading

1. `NEXT.md` — current task directive
2. `engines/excerpting/SPEC.md` — **the behavioral authority** (2343 lines)
3. `engines/excerpting/SPEC_OUTLINE.md` — architectural blueprint and source mapping
4. `engines/normalization/contracts.py` — upstream schema (what this engine receives)
5. `KNOWLEDGE_INTEGRITY.md` — the 7 threats this engine must defend against
6. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — why this architecture
7. `experiments/architecture_test/run_tests.py` — validated LLM approach and prompts
