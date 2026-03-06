# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Synthesis engine CREATIVE session.** The synthesis engine is the final engine in the pipeline — it produces the entries that ARE Rayane's knowledge. This is the most important engine to get right because its output is what the owner reads, studies, and internalizes. The CREATIVE session must: research state-of-the-art in LLM-based scholarly synthesis, design the core processing rules (§4.A), and invent transformative capabilities (§4.B) that produce entries matching the quality target in ENTRY_EXAMPLE.md.

## What to Read

1. `reference/ENTRY_EXAMPLE.md` — The quality target. Study the GOOD entry (not the flat one). Understand what makes it a scholarly narrative rather than a compilation.
2. `reference/DOMAIN.md` — Islamic scholarly conventions that the synthesizer must respect.
3. `engines/taxonomy/SPEC.md` §3 (Output Contract) and §4.B.6 (Scholarly Landscape) — the synthesizer's primary input. The scholarly landscape is the narrative scaffold.
4. `engines/excerpting/SPEC.md` §3 (Output Contract) — what excerpt metadata is available.
5. `CREATIVE_MANDATE.md` — The invention protocol. Follow it.
6. `reference/RESOURCES.md` — Available tools and libraries.

**Do NOT read:** Other engine SPECs beyond §3 output contracts. Do NOT read KNOWLEDGE_INTEGRITY.md (save for HARDENING). Do NOT read full VISION.md — use `python3 scripts/extract_vision_sections.py` for §7 (synthesis) and §12 (entries) only.

## Definition of Done

1. `engines/synthesis/SPEC.md` draft exists with all 10 template sections
2. §4.A has concrete processing rules for: entry structure generation, excerpt integration, grounding verification, narrative construction
3. §4.B has at least 2 architect-originated transformative capabilities (not from VISION.md)
4. Every §4.A rule passes the "mental function signature" test — Claude Code can implement without clarifying questions
5. Web search research performed: at least 3 searches on LLM synthesis techniques, scholarly narrative generation, or multi-source compilation
6. `engines/synthesis/contracts.py` created with Pydantic models for input/output
7. check_spec_quality.py shows 0 high-severity defects
8. creative_verification.py shows invention ratio > 0%
9. Self-audit performed: ≥3 structural/semantic defects found and fixed
10. NEXT.md written (for synthesis PRECISION session)
11. SESSION_LOG.md updated
12. Committed and pushed

## What the Previous Session Did (Hardening — Taxonomy)

- Mapped all 7 KNOWLEDGE_INTEGRITY.md threats to taxonomy-specific prevention mechanisms (§5.4)
- Added error cascade analysis for 5 failure propagation paths (§5.5)
- Added 6 adversarial test cases to §10.5 (systematic bias, evolution orphan, crash recovery, rollback with post-evolution excerpts, duplicate gate decisions, Arabic text fidelity)
- Self-audit: 6 structural/semantic defects found and fixed:
  - Leaf embedding cache lifecycle unspecified → specified compute/update/staleness rules
  - Post-write text fidelity check missing → added byte-for-byte primary_text verification
  - Rollback failure scenario missing → added TAX_ROLLBACK_FAILURE with diagnostic + manual recovery
  - Human gate decision idempotency missing → added duplicate detection via gate_log
  - Pre-approval "consecutive" scope ambiguous → clarified per source-science pair
  - "reviewed" status referenced (doesn't exist in taxonomy contract) → fixed to "draft" + re-placement queue
- Added WAL (write-ahead log) mechanism for crash-safe evolution
- Added 4 new error codes: TAX_METADATA_INCONSISTENCY, TAX_LOW_SELF_CONTAINMENT, TAX_EMBEDDING_DEGRADED, TAX_ROLLBACK_FAILURE
- Final: 0 high, 6 medium (false-positive concept terms), 2 low

## Creative Focus for Synthesis

The synthesizer's job is NOT "compile excerpts into entries." It is: produce scholarly narratives that transform raw excerpt data + scholarly landscape metadata into the kind of entry shown in ENTRY_EXAMPLE.md. Key questions:

1. **How does the synthesizer use the scholarly landscape?** The landscape provides chronological timelines, influence chains, discourse transitions, evidence evolution. How does the synthesizer transform these data structures into prose?
2. **What is the entry's structure?** Not just "introduction + body + conclusion." The target entry has: definitional core, historical development, school comparison, evidence analysis, cross-reference network. How is this structure determined per topic?
3. **How does the synthesizer handle grounding?** Every claim must be traceable (T-5, D-040). The entry must distinguish source_grounded claims from analytical claims. How does the synthesizer mark this distinction in the output?
4. **What makes one entry better than another?** Can the synthesizer self-evaluate entry quality? Can it detect when an entry is flat vs. narrative?

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
