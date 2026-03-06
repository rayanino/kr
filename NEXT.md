# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Synthesis engine PRECISION session.** The CREATIVE session produced the synthesis SPEC draft with 6 transformative capabilities, attribution-first generation design, and contracts.py. The PRECISION session must: reduce high-severity defects to 0, add worked examples to all §4 subsections missing them, specify the exact LLM prompt templates for key calls, and ensure every rule passes the "mental function signature" test for Claude Code.

## What to Read

1. `engines/synthesis/SPEC.md` — The SPEC to refine. Focus on §4 (processing rules) and §5 (validation).
2. `engines/synthesis/contracts.py` — Verify contracts match SPEC exactly. Fix any divergence.
3. `reference/ENTRY_EXAMPLE.md` — Re-read to verify the SPEC's processing rules would actually produce an entry of this quality.
4. `scripts/check_spec_quality.py` output — Current: 20 high defects (mostly VAGUE_QUANTIFIER and MISSING_EXAMPLE). Target: 0 high.
5. `engines/taxonomy/SPEC.md` §4.B.6 — Scholarly landscape output. Verify the synthesis engine's landscape consumption matches the taxonomy engine's landscape output exactly.

**Do NOT read:** VISION.md, DOMAIN.md (already consumed in CREATIVE session). Do NOT read other engine SPECs except §3 output contracts.

## Definition of Done

1. `check_spec_quality.py` shows 0 high-severity defects
2. Every §4.A subsection has at least one worked example with real Arabic text showing input → processing → output
3. §4.A.3 (Phase 2) and §4.A.4.1 (Phase 3 factual layer) have exact prompt templates (not just descriptions)
4. §4.B.5 (Khilaf Disambiguation) has a worked example showing decomposition of a real disagreement (e.g., المبتدأ definitions)
5. §4.B.6 (Socratic Self-Verification) has a worked example showing question generation + self-verification cycle
6. contracts.py and SPEC agree perfectly — no schema field in one but not the other
7. §5 (Validation) maps all KNOWLEDGE_INTEGRITY.md threats to synthesis-specific vectors (like the taxonomy SPEC does)
8. §7 (Error Handling) has complete error codes for all failure modes
9. §9 (Current Implementation State) updated with accurate file list
10. Self-audit: ≥3 structural/semantic defects found and fixed
11. NEXT.md written (for synthesis HARDENING session)
12. SESSION_LOG.md updated
13. Committed and pushed

## Key Issues from CREATIVE Session

- **20 high-severity defects remaining** — mostly VAGUE_QUANTIFIER ("multiple", "many", "some") in existing text. Replace each with specific numbers or ranges.
- **7 §4 subsections missing worked examples** — §4.A.1, §4.A.5, §4.A.6, §4.A.8, §4.A.9, §4.A.10, §4.A.11. Each needs an Arabic example.
- **3 UNVALIDATED_WRITE warnings** — writes to library need pre-write validation specified.
- **Prompt templates not yet specified** — §4.A.3 describes what the LLM does but the exact system prompts, user messages, and few-shot examples are not written. The PRECISION session should add these for the 3 most critical LLM calls: (1) position identification, (2) attribution-first claim planning, (3) entailment verification.
- **§5 threat mapping incomplete** — the taxonomy SPEC has a detailed §5.4 mapping KNOWLEDGE_INTEGRITY.md threats to engine-specific vectors. The synthesis SPEC should do the same.

## What the Previous Session Did (Creative — Synthesis)

- Researched 8 sources on LLM multi-document synthesis, attribution-first generation, hallucination rates
- Redesigned §4.A.4.1 as Attribution-First generation pipeline (plan → attribute → generate conditioned → verify entailment)
- Added §4.B.5 Khilaf Disambiguation Engine (atomic sub-claim decomposition + agreement matrix)
- Added §4.B.6 Socratic Self-Verification and Assessment Generation (dual-purpose quality + assessment)
- Improved §4.A.3 with precise Pydantic schemas and formulas
- Created contracts.py with all input/output models
- Updated RESOURCES.md with 7 new research entries
- Self-audit: 4 defects found and fixed

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
