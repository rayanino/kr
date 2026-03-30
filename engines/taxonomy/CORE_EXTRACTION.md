# Taxonomy Engine — Core vs Deferred Classification

**Date:** 2026-03-30
**SPEC version:** engines/taxonomy/SPEC.md (945 lines)
**Analyst:** Architect (Claude Chat)

---

## §1 — Purpose and Scope

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Responsibility 1: Excerpt placement | CORE | This IS the engine's fundamental job — placing excerpts at leaves |
| Responsibility 2: Tree lifecycle management | DEFERRED | Trees already exist (5 sciences, 922 leaves). Evolution/rollback not needed for v1 |
| Responsibility 3: Coverage analytics | DEFERRED | Nice to have but not required for placement |
| Responsibility 4: Structural knowledge graph | DEFERRED | Cross-science links, prerequisites, synonyms are enrichment on top of placement |

## §2 — Input Contract

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §2.1 Draft excerpt validation (required fields) | CORE | Must validate incoming excerpts |
| §2.1 Draft excerpt validation (expected fields) | CORE | Needed for placement quality — warn on absence |
| §2.1 `proposed_leaf` validation | DEFERRED | Excerpting engine doesn't currently produce `proposed_leaf`. Taxonomy does independent classification |
| §2.1 `science_id` validation | CORE (MODIFIED) | Required, but must come from run context/source metadata, NOT from excerpt record (excerpting doesn't produce it) |
| §2.2 Tree management commands (evolution) | DEFERRED | No tree evolution in v1 |
| §2.2 Human gate decisions | CORE (SIMPLIFIED) | Placement review needed, but evolution/coverage review gates are deferred |
| §2.2 Excerpt relocation requests | DEFERRED | Correction mechanism for post-v1 |

## §3 — Output Contract

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §3.1 Placed excerpts (core fields) | CORE | `confirmed_leaf`, `placement_confidence`, `placed_utc`, `lifecycle_stage: placed` |
| §3.1 Placed excerpts (`review_metadata`) | CORE (SIMPLIFIED) | Only `auto_approved` for v1 (no human gate queue yet) |
| §3.1 Placed excerpts (`placement_reasoning`) | CORE | Auditability — must know WHY this leaf was chosen |
| §3.1 Placed excerpts (`taxonomy_version_at_placement`) | CORE | Even without evolution, record the tree version for future-proofing |
| §3.1 Placed excerpts (`verified_flagged_status`) | DEFERRED | Source trust tiers not implemented upstream yet |
| §3.1 Provenance preservation (D-023) | CORE | All upstream fields pass through — taxonomy adds, never strips |
| §3.2 Science tree files (read) | CORE | Must read existing tree.yaml files |
| §3.2 Science tree files (write/modify) | DEFERRED | No tree construction or evolution in v1 |
| §3.2 Prerequisite edges | DEFERRED | Knowledge graph enrichment |
| §3.2 Narrative ordering | DEFERRED | Study path feature, not placement |
| §3.2 Cross-science links | DEFERRED | Knowledge graph enrichment |
| §3.2 Terminology synonyms | DEFERRED | Enrichment — nice for accuracy but not essential for v1 |
| §3.3 Coverage analytics | DEFERRED | All coverage computation |
| §3.4 Evolution artifacts | DEFERRED | No evolution in v1 |

## §4.A — Core Processing

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §4.A.1 Stage 1a: Excerpting engine proposal | DEFERRED | Excerpting doesn't produce `proposed_leaf` currently |
| §4.A.1 Stage 1b: Topic-based LLM search | CORE | Primary mechanism for finding the right leaf — LLM compares `excerpt_topic` against tree structure |
| §4.A.1 Stage 1c: Embedding similarity | DEFERRED | Adds accuracy but requires embedding infrastructure (multilingual-e5-large, precomputed leaf embeddings). LLM search alone is sufficient for v1 |
| §4.A.1 Stage 2: Candidate ranking | CORE | LLM scores candidates using excerpt text + tree context |
| §4.A.1 Placement decision rules (≥0.8 auto, 0.5-0.8 escalate, <0.5 unplaceable) | CORE (SIMPLIFIED) | Keep thresholds. Simplify: all placements auto-approve for v1 (no human gate queue). Log confidence for later review |
| §4.A.1 Pre-approval policies | DEFERRED | Requires human gate infrastructure |
| §4.A.1 Hierarchical search (>200 leaves) | CORE | Nahw has 226 leaves, Sarf has 226 — need this to work |
| §4.A.2 Placement validation (leaf exists check) | CORE | Must verify confirmed_leaf resolves to a real leaf |
| §4.A.2 One-excerpt-per-source diagnostic | DEFERRED | Diagnostic, not blocking for v1 |
| §4.A.2 Verified/flagged consistency | DEFERRED | No trust tiers upstream |
| §4.A.2 Leaf capacity check | DEFERRED | Diagnostic |
| §4.A.3 Tree construction (all 4 phases) | DEFERRED | Trees already exist |
| §4.A.4 Primary topic determination | CORE | When excerpt mentions 2+ topics, must pick the right one for placement |
| §4.A.5 Evolution signal detection | DEFERRED | No evolution in v1 |
| §4.A.6 Coverage gap detection | DEFERRED | Analytics |
| §4.A.7 Evolution application and migration | DEFERRED | No evolution in v1 |
| §4.A.8 Semantic deduplication detection | DEFERRED | Enrichment for synthesis |
| §4.A.9 Cross-science link management | DEFERRED | Knowledge graph |
| §4.A.10 Terminology synonym management | DEFERRED | Enrichment |

## §4.B — Transformative Capabilities

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §4.B.1 Topic significance scoring | DEFERRED | Enrichment |
| §4.B.2 Difficulty estimation / study path | DEFERRED | Scholar interface feature |
| §4.B.3 Entry depth recommendation | DEFERRED | Synthesis concern |
| §4.B.4 Disagreement topology | DEFERRED | Synthesis enrichment |
| §4.B.5 Scholarly landscape position clustering | DEFERRED | Synthesis enrichment |
| §4.B.6 Scholarly landscape full structure | DEFERRED | Synthesis enrichment |

## §5 — Validation and Quality

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §5.1 Placement self-validation (file write + fidelity check) | CORE | Must verify placed excerpt written correctly, primary_text byte-identical |
| §5.1 Tree integrity validation | DEFERRED | Only needed after tree modifications (none in v1) |
| §5.1 Evolution invariant enforcement | DEFERRED | No evolution |
| §5.2 Coverage consistency check | DEFERRED | No coverage analytics |
| §5.2 Cross-version placement validity | DEFERRED | No tree versions |
| §5.2 Duplicate cluster staleness | DEFERRED | No deduplication |
| §5.3 Human gate: placement review | DEFERRED (for v1) | All placements auto-approved, logged for later review |
| §5.3 Human gate: evolution review | DEFERRED | No evolution |
| §5.4 T-1 prevention (Arabic text fidelity) | CORE | Knowledge Integrity Axiom — byte-identical primary_text through placement |
| §5.4 T-2 prevention (attribution consistency check) | DEFERRED | Enrichment-level validation |
| §5.4 T-3 prevention (misplacement) — LLM + ranking | CORE | This is the core placement algorithm |
| §5.4 T-3 prevention (human gate for <0.8) | DEFERRED for v1 | Log for later human review |
| §5.4 T-4 prevention (context loss logging) | DEFERRED | Diagnostic |
| §5.4 T-5 prevention (landscape hallucination) | DEFERRED | No landscape in v1 |

## §6 — Consensus Integration

| Capability | Classification | Reason |
|-----------|---------------|--------|
| Multi-model consensus for ambiguous placements | DEFERRED | Single-model placement for v1. Consensus adds quality but complexity |

## §7 — Error Handling

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §7.1 Input errors (missing fields, bad format) | CORE | Must reject malformed excerpts |
| §7.2 Processing errors (LLM failure, timeout) | CORE | Must handle gracefully with retries |
| §7.3 Evolution errors | DEFERRED | No evolution |
| §7.4 Fail-loud principle | CORE | No silent data loss |

## §8 — Configuration

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §8.1 Global parameters (confidence thresholds) | CORE | Placement thresholds |
| §8.2 Per-science config (SCIENCE.md) | CORE (SIMPLIFIED) | Just science_id → tree.yaml path mapping for v1 |
| §8.3 Hardcoded constraints | CORE | Whatever applies to placement |

## §9 — Implementation State

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §9.1 Existing code (tracer.py) | CORE | Build on it |
| §9.3 External dependencies | CORE | Must identify what we need |

## §10 — Test Requirements

| Capability | Classification | Reason |
|-----------|---------------|--------|
| §10.1 Placement accuracy | CORE | Must test placement quality |
| §10.1 Tree integrity | DEFERRED | No tree modification |
| §10.1 Coverage accuracy | DEFERRED | No coverage |
| §10.1 Migration correctness | DEFERRED | No evolution |
| §10.2 Gold baselines (50 excerpts) | CORE | Need this to validate placement |
| §10.4 Upstream integration test | CORE | Must consume real excerpting output |
| §10.4 Downstream integration test | DEFERRED | No synthesis engine |
| §10.5.1 Systematic bias test | CORE | Critical — catches LLM misclassification patterns |
| §10.5.2 Evolution orphan test | DEFERRED | No evolution |
| §10.5.3 Crash recovery test | DEFERRED | No evolution |
| §10.5.4 Rollback test | DEFERRED | No evolution |
| §10.5.5 Duplicate gate decision test | DEFERRED | No human gate |
| §10.5.6 Arabic text fidelity test | CORE | Knowledge Integrity Axiom |

---

## Summary

- **Core capabilities:** 24
- **Deferred capabilities:** 42
- **Core removes ~70% of SPEC complexity**

### What Core v1 Taxonomy Actually Does

1. **Reads** existing science trees from `library/sciences/{science_id}/tree.yaml`
2. **Receives** excerpts from the excerpting engine (with `science_id` from run context)
3. **Classifies** each excerpt to a leaf via LLM topic matching (hierarchical for large trees)
4. **Ranks** candidate leaves via LLM scoring of excerpt text vs leaf context
5. **Writes** placed excerpts to `library/sciences/{science_id}/content/{leaf_path}/excerpts/`
6. **Validates** placement (leaf exists, file written, primary_text byte-identical)
7. **Logs** placement reasoning and confidence for future human review

That's it. No evolution, no coverage, no knowledge graph, no scholarly landscape.

---

## Extension Hooks

| Deferred Capability | Core Must Not Assume |
|---------------------|---------------------|
| Tree evolution | Core must record `taxonomy_version_at_placement` on every placed excerpt even though the version is static for v1 |
| Embedding similarity (Stage 1c) | Core's candidate generation must accept additional candidates from a pluggable source — don't hardcode "only LLM search" |
| Coverage analytics | Core must store placed excerpts in a structure that allows post-hoc counting (the file-per-excerpt-per-leaf layout already enables this) |
| Human gate queue | Core must record `placement_confidence` on every placement so a future human gate can filter by confidence |
| Cross-science links | Core must not merge trees or assume science isolation in the data model |
| Proposed_leaf from excerpting | Core must accept `proposed_leaf` if present (as first candidate) but not require it |
| Synonyms | Core must not assume canonical terminology — it must work with `excerpt_topic` text matching, which handles variant terminology through LLM understanding |
| Multi-model consensus | Core must use the CLI adapter's model routing, not hardcode a single model — so consensus can be added later |

---

## Critical Contract Gap (BLOCKING — Must Resolve Before Build)

The taxonomy SPEC §2.1 declares these fields REQUIRED on incoming excerpts:
- `science_id` — **MISSING** from excerpting output (must come from source metadata / run context)
- `lifecycle_stage` — **MISSING** (excerpting doesn't set this; taxonomy must assume `draft`)
- `passage_id` — **MISSING** (passaging engine not built; field doesn't exist yet)
- `atom_ids` — **MISSING** (atomization engine not built; field doesn't exist yet)

The taxonomy SPEC was written assuming all upstream engines exist. They don't.
The passaging and atomization engines are not built, so `passage_id` and `atom_ids` will not exist on any excerpt for v1.

**Decision needed:** Either:
- **(A)** Remove `passage_id` and `atom_ids` from taxonomy REQUIRED fields for v1 (they're not used by placement)
- **(B)** Have the excerpting engine add synthetic values (e.g., `passage_id = div_id`, `atom_ids = segment_indices`)

I recommend **(A)** — clean removal. These fields serve provenance tracing through engines that don't exist yet. Adding synthetic values creates false provenance.

For `science_id`: add it as a parameter passed to the taxonomy engine at invocation time (from source metadata), not as a field on each excerpt. The taxonomy engine for v1 processes one science at a time.

For `lifecycle_stage`: the taxonomy engine sets it to `placed` on output. It can assume all incoming excerpts are `draft` without requiring the field.

---

## Items I'm Uncertain About

**1. Embedding similarity (§4.A.1 Stage 1c) — CORE or DEFERRED?**
- Case for CORE: It catches terminology mismatches the LLM might miss (e.g., "الفاعل المعنوي" vs "نائب الفاعل"). Arabic scholarly terminology varies heavily across schools and periods.
- Case for DEFERRED: Requires additional infrastructure (embedding model, precomputed leaf embeddings, numpy dependency). LLM search already handles this reasonably since the LLM knows scholarly Arabic terminology.
- **My call:** DEFERRED. The LLM's Arabic knowledge is strong enough for v1. If placement accuracy is poor on the gold baseline, we add embeddings in a targeted fix.

**2. Terminology synonym management (§4.A.10) — CORE or DEFERRED?**
- Case for CORE: Nahw terminology genuinely varies. If the LLM can't map "الفاعل المعنوي" → "نائب الفاعل", placement fails.
- Case for DEFERRED: The LLM handles this implicitly through its training on Arabic grammatical texts.
- **My call:** DEFERRED. Same reasoning as embeddings — test first, add if needed.

**3. Human gate for <0.8 confidence — CORE or DEFERRED?**
- Case for CORE: Low-confidence placements are exactly where errors happen. Without human review, errors accumulate silently.
- Case for DEFERRED: Building a human gate queue is substantial infrastructure. For v1 with 5 books, we can log low-confidence placements and review them manually in the evaluation phase.
- **My call:** DEFERRED for v1 infrastructure, but the logging is CORE. Every placement confidence < 0.8 must be logged prominently for post-hoc human review.
