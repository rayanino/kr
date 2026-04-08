# Scholar Authority Model — سجل العلماء

**Responsibility:** Maintaining canonical scholar identities, variant name mappings, biographical data, teacher-student relationships, and school affiliations across ALL sources in the library. This is the single source of truth for "who is this scholar?"

**Type:** Shared component — used by source, excerpting, taxonomy, and synthesizing engines.

## Required Reading
1. This component's SPEC.md — the authoritative specification
2. `reference/DOMAIN.md` — "Scholar Identity" and "Scholar Authority Model" sections
3. `reference/ENTRY_EXAMPLE.md` — see how biographical metadata enables scholarly narrative
4. `engines/source/SPEC.md` §4.A.5 — the source engine creates scholar records during intake

## Current State
No code exists. SPEC complete (all 10 sections). New shared component identified during KR design phase.

Code: 0L.
Tests: 0.
Reference: SPEC.md (complete).

## Architecture Summary

**Five capabilities:** registry CRUD, record matching/disambiguation, progressive enrichment, teacher-student graph, external enrichment (OpenITI + Wikidata + LLM).

**Record matching** uses a five-signal weighted composite: name similarity (0.35), death date proximity (0.25), school overlap (0.15), works overlap (0.15), teacher-student overlap (0.10). Conservative bias: prefers creating duplicates over false merges. Name alone capped at 0.65 — always below auto-match threshold.

**Three threshold ranges:** ≥0.85 auto-match, 0.50–0.85 human gate, <0.50 new record.

**Teacher-student graph** is a first-class data structure (not just metadata arrays). Stored separately at `scholar_graph.json`. Supports chain discovery, connection queries, and subgraph extraction. Cycle detection on every edge addition.

**Progressive enrichment:** array fields accumulate, empty scalars fill, occupied scalar conflicts trigger human gate for high-impact fields. Every field has provenance tracking.

**External sources:** OpenITI metadata (primary, offline), LLM inference (secondary, for bootstrapping), Wikidata SPARQL (tertiary, opportunistic).

**Career phases** model scholars who changed positions (e.g., al-Shafi'i's qadim/jadid). Enables the synthesizer to handle retractions correctly.

## Key Constraints
1. `canonical_id` format: `sch_{5_digit_sequence}`. Never reused, even after merge.
2. Per-science school tracking — a scholar can be Hanbali in fiqh and Ash'ari in aqidah.
3. Metadata is synthesis fuel (D-023) — every field exists for what it enables in entries.
4. Conservative matching bias — false merge is worse than false duplicate.
5. Secure by design (D-033) — every conflict recorded, every enrichment provenanced, every merge audited.

## Dependencies
- CAMeL Tools: Arabic text normalization and transliteration
- NetworkX: Graph analysis (betweenness centrality for influence metrics)
- httpx: Wikidata SPARQL queries (optional, when enabled)

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation

## Claude Code Behaviour Guidelines

- **Ownership, not deflection:** When you encounter an issue, take responsibility and work towards a solution. Don't say "not caused by my changes" or "pre-existing issue." Don't give up with "known limitation" or defer to "future work." Fix it now.
- **Persistence through obstacles:** Don't stop at the first problem. Don't declare "good stopping point" or "natural checkpoint." Keep pushing until you have a complete, verified solution.
- **Initiative over permission-seeking:** If you have the knowledge and capability to solve a problem, act. Don't ask "should I continue?" or "want me to keep going?" Take initiative and drive towards the solution.
- **Plan before acting:** For multi-step work, plan which files to read, in what order, which tools to use, and what the expected outcome is — before touching anything.
- **Convention recall:** Always re-read and apply project-specific conventions from CLAUDE.md files. Don't rely on memory of what they say.
- **Self-correction loops:** Catch your own mistakes by applying reasoning loops and self-checks. Fix errors before committing or asking for help.
- **Verify, don't assume:** After reaching a conclusion or making a change, verify it against the actual state of the codebase. A conclusion you haven't verified is a guess. Run the test, read the output, check the file.
- **Trace root causes:** When something fails, trace the full causal chain. Don't patch symptoms — find and fix the underlying cause. A surface fix hides the real bug for later.

### Tool Use

- **Research-first, never edit-first:** Before using any tool, research the context and requirements. Read the relevant code, SPEC, and contracts before making changes. Understand before you act.
- **Surgical edits over rewrites:** Make targeted, minimal changes. Never rewrite whole files or make large sweeping changes when a focused edit achieves the goal.
- **Reasoning loops are mandatory:** Apply reasoning loops frequently. Don't skip them to save tokens. The cost of a wrong action far exceeds the cost of thinking.

### Thinking Depth

- Always apply the **highest level of thinking depth**. Shallow thinking leads to the cheapest available action, which is rarely the correct one. Spending more tokens on reasoning produces dramatically better outcomes.
- **Never reason from assumptions.** Always reason from actual data — read and understand the actual code, SPEC, or documentation before making decisions. Assumptions compound into errors.
