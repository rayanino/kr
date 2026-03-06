# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Taxonomy engine PRECISION session.** The taxonomy SPEC now has 6 §4.B capabilities (3 original + 3 new from creative session). The PRECISION session must: fix all vague language flagged by `check_spec_quality.py` (47 defects), add concrete examples to §4.A rules, ensure contracts.py matches §3 exactly, and run the self-audit protocol.

## What to Read

1. `engines/taxonomy/SPEC.md` — The full SPEC. Primary target.
2. `engines/taxonomy/contracts.py` — Verify against §3.
3. `DEEP_REASONING_PROTOCOL.md` §Tier 1–2 — Checklist for precision fixes.

**Do NOT read:** ENTRY_EXAMPLE.md, USER_SCENARIOS.md, other engine SPECs, DOMAIN.md, KNOWLEDGE_INTEGRITY.md — save context for precision work.

## Definition of Done

1. `check_spec_quality.py` shows 0 high-severity defects
2. Every "multiple", "many", "some", "appropriate" replaced with specific numbers or conditions
3. Every LLM prompt in §4.A has: model specification, prompt template, structured output schema
4. contracts.py validated: every §3 field has a Pydantic model, every model matches the SPEC text
5. Self-audit performed: ≥4 structural/semantic defects found and fixed (per DEEP_REASONING_PROTOCOL example)
6. §4.A examples added: at least 2 concrete examples showing placement decision flow
7. NEXT.md written (for taxonomy HARDENING session)
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Session Did (Creative)

- Added 3 new transformative capabilities to §4.B:
  - **§4.B.4 — Scholarly Disagreement Topology (خريطة الخلاف):** Computes per-leaf disagreement classification (ijma/khilaf/apparent consensus), aggregates to branch/science level, detects recurring disagreement axes with root cause hypotheses. Output: disagreement_topology.json per science.
  - **§4.B.5 — Proactive Tree Evolution Prediction (استشراف التطور):** Predicts tree evolution needs from source TOC structure BEFORE excerpting. Aligns source division trees against taxonomy tree, detects many-to-one (split needed) and unmapped (gap) patterns. Aggregates across sources for high-confidence signals.
  - **§4.B.6 — Scholarly Landscape Reconstruction (المشهد العلمي):** Pre-computes per-leaf narrative scaffold: chronological position timeline, scholar influence graph, discourse transitions (refinement/opposition/synthesis), evidence evolution map, school positioning summaries. This is the metadata backbone enabling ENTRY_EXAMPLE.md quality.
- Created `engines/taxonomy/contracts.py` with Pydantic models for all §2/§3 schemas plus §4.B output schemas
- Updated §9 implementation state table with new capabilities
- Research: Arabic NLP text classification, Islamic knowledge ontologies, scholarly knowledge graphs, disagreement detection approaches
- `check_spec_quality.py`: 47 defects (same 39 pre-existing + 8 new from added sections)
- `creative_verification.py`: 90/100 (up from 75)

## Defects Noted for PRECISION Session

Key defects from `check_spec_quality.py` and manual review:

1. **L183, L184, L192, etc. — VAGUE_QUANTIFIER "multiple"/"many":** Throughout §4.A.3 (Tree Construction), §4.A.5 (Evolution), §4.B.4 (Disagreement). Each instance needs a specific count or range.
2. **L368 — HANDWAVE_LLM "using the LLM":** §4.B.1 references "the LLM" without specifying which model, interface, or prompt template.
3. **L400 — VAGUE_SUFFICIENT "sufficient":** §6 (Consensus) needs explicit threshold for what makes agreement "sufficient."
4. **L404 — MISSING_THRESHOLD "high confidence":** Needs explicit numeric threshold.
5. **§4.A.1 has no concrete example** of placement decision flow with real Arabic content.
6. **§4.A.3 validation phase** says "3–5 representative sources" — should this be configurable?
7. **§4.B.4 ijma detection** needs explicit minimum excerpt count per school for confidence (currently just "3+ schools represented" but no minimum excerpts per school).
8. **§4.B.6 period clustering** says "gaps of ≥100 hijri years" — this should be configurable.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
