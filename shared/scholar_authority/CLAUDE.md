# Scholar Authority Model — سجل العلماء

**Responsibility:** Maintaining canonical scholar identities, variant name mappings, biographical data, teacher-student relationships, and school affiliations across ALL sources in the library. This is the single source of truth for "who is this scholar?"

**Type:** Shared component — used by source, excerpting, taxonomy, and synthesizing engines.

## Required Reading
1. This component's SPEC.md
2. `reference/DOMAIN.md` — "Scholar Identity" and "Scholar Authority Model" sections
3. `reference/ENTRY_EXAMPLE.md` — see how biographical metadata enables scholarly narrative
4. `reference/PIPELINE_TRACE.md` — see how the authority model feeds the synthesizer

## Current State
No code exists. No ABD equivalent. This is a new shared component identified during the KR design phase. DOMAIN.md (lines 127-140) describes the concept; the SPEC will define the implementation.

Code: 0L.
Tests: 0.
Reference: 0 docs.

## Why This Component Is Critical

Without it, the synthesizer cannot:
- Know that "سيبويه" in source A and "عمرو بن عثمان بن قنبر" in source B are the same person
- Reconstruct teacher-student chains across sources
- Order scholarly positions chronologically (requires death dates)
- Attribute positions to the correct school (requires school affiliation)
- Detect when a scholar changed positions over their career (requires career timeline)

Without it, the source engine cannot:
- Deduplicate authors across different name spellings
- Link works to their correct authors when names are ambiguous
- Build the "author profile" portion of book briefings (D-022)

Without it, the excerpting engine cannot:
- Resolve implicit references ("الإمام" in a Shafi'i text = al-Shafi'i himself)
- Distinguish "Scholar A reports Scholar B's view" from "Scholar A's own view"

## Key Constraints
1. **Canonical identity with variant mappings.** Each scholar has ONE canonical record with multiple name variants. "ابن حجر" maps to TWO canonical records (al-Asqalani d.852 AH vs al-Haytami d.974 AH) — disambiguation requires context (science, time period, nisba).
2. **Incremental enrichment.** The model grows richer with every source processed. The 100th source mentioning al-Nawawi may add details the first 99 didn't have. Records are never finalized — they accumulate.
3. **Per-science school tracking.** A scholar can be Hanbali in fiqh, Ash'ari in aqidah, and Basran in nahw. School affiliation is per-science, not global.
4. **Teacher-student graph.** This is a directed graph that enables intellectual genealogy reconstruction. The synthesizer uses it to explain WHY positions are related.
5. **Career timeline.** Some scholars changed positions (الشافعي had قديم and جديد positions). The model must support temporal career phases so the synthesizer presents the FINAL position as primary.
6. **Scale.** Tens of thousands of scholars across 14 centuries. Must work at scale from the start.
7. **Metadata is synthesis fuel (D-023).** Everything in the authority model exists to enable richer synthesis. Every field earns its place by what it enables in the entry.
