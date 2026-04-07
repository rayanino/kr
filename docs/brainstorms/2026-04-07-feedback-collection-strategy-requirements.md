---
date: 2026-04-07
topic: feedback-collection-strategy
---

# Feedback Collection Strategy — Owner Data Requirements for July 1 Readiness

## Problem Frame

The KR pipeline has 5 engines (Source → Normalization → Excerpting → Taxonomy → Synthesis) that process Arabic Islamic scholarly texts into a personal study library. The pipeline needs ~42 owner-dependent decisions that cannot be derived from code, text analysis, or LLM inference alone.

The owner will spend 2-3 hours/day for 3 months (Apr-Jun 2026) providing this data. On July 1 he goes full-time on development. By that date, ALL owner-dependent data must exist — zero blockers from insufficient input.

The owner's fatigue profile is critical: open-ended questions exhaust him (1 hour each). He strongly prefers structured/interactive feedback (multiple choice, highlighting, comparisons). The primary feedback mechanism must be structured; open-ended is optional.

**Origin:** 5-coworker synthesis at `engines/excerpting/reference/dr_reviews/FINAL_SYNTHESIS_5_OF_5.md`, produced from:
- DR18 (Claude DR): 42 decision points across all 5 engines
- Codex CLI: 11 policy families with dependency chains
- Gemini CLI: 9 unique pedagogical findings
- ChatGPT DR: campaign evidence + bundle format evaluation
- Gemini DR: classical curriculum framework with 21 academic citations

## Requirements

**Layer 1: User Model + Pedagogical Mode**

- R1. Formalize the owner's user model artifact from interview data: study mode (memorization-first), Arabic-first priority, "just memorize it like this" posture, 10-15 excerpts/session tolerance
- R2. Record per-science study mode decisions: Hanbali primary madhab for fiqh (with masking layer to suppress other 3 schools), munazarah vs qawa'id mode for usul, shubuhat exposure policy for aqidah
- R3. Maintain a formal 19-science ranking (18 existing + mantiq) with owner-confirmed priority order
- R4. Record grammar school terminology preference (Basran default recommended, Kufan synonym-mapping layer if needed)

**Layer 2: Quality Policies + Conflict Governance**

- R5. Collect S-1 (quality dimension priority ranking) — the universal conflict resolver when fidelity, self-containment, granularity, and study value disagree
- R6. Collect S-2 (ideal vs worst excerpt definition) with concrete Arabic examples
- R7. Complete remaining questionnaire items: K-1..K-3 (khilaf/tarjih), E-1..E-3 (evidence), D-1..D-3 (definition splitting), SC2/SC3 (self-containment), GN-1/GN-2 (genre), L-1/L-2 (layers)
- R8. Define fiqh masking policy: suppress comparative rulings during early study, progressive unlock after verified baseline mastery

**Layer 3: Engine Decisions + Parameters**

- R9. Complete DR18's 5 focused sessions: muhaqiq trust list (SRC-D-001), publisher reputation (SRC-D-002), book processing priority (SRC-D-010), science scope ranking (SRC-D-004), flag budget threshold (EXC-D-010), entry style (SYN-D-005), school lists per science (SYN-D-002), tree reviews (TAX-D-001)
- R10. Update TEAM_TRANSLATION_GUIDE.md to map FP-13 through FP-22 (currently zero mappings for the hardened FP layer)

**Layer 4: Calibration (summer, requires real output)**

- R11. Collect 100+ excerpt judgments for teaching unit quality calibration
- R12. Collect 30-100 study-readiness labels splitting FULL into acceptable vs study-ready (FP-18)
- R13. Complete the 30-book owner review gate (non-negotiable before excerpting engine completion)
- R14. Collect DEPENDENT disposition rubrics (20-30 decisions during pipeline runs)

**Cross-Cutting**

- R15. All collected data persisted as future training material with full provenance (model, prompt version, timestamp, confidence) per Rule 13
- R16. Bundle format improvements applied to remaining bundles: standardized manifest schema, final_decisions.jsonl per bundle, integrity_manifest.json, evidence/authority tagging
- R17. Cross-engine drift from owner answers auto-routed to the correct engine's data store

## Success Criteria

- By July 1: Layers 1-3 complete (all policy, governance, and engine parameter data collected)
- By July 1: Layer 4 infrastructure in place (review interface ready, calibration pipeline designed)
- Owner time expenditure: ≤30 min/day average over the 3-month window
- Zero re-collection: data captured once, reused via manifests
- All 42 decision points either RESOLVED or explicitly DEFERRED-TO-SUMMER with justification

## Scope Boundaries

- NOT in scope: Building the interactive review UI (separate implementation session)
- NOT in scope: Running the excerpting pipeline or processing books
- NOT in scope: Taxonomy engine work, synthesis engine work
- NOT in scope: Spaced repetition algorithm implementation (user_model is Cycle 0)
- NOT in scope: The 30-book probe itself (requires hardened output first)
- IN scope: Designing the collection workflow, session structures, and data formats
- IN scope: Updating the ChatGPT bundle format for remaining questions
- IN scope: Creating the structured questionnaire for Layer 3 sessions

## Key Decisions

- **Hanbali primary madhab:** Owner decision 2026-04-07. Fiqh masking layer will suppress Hanafi/Shafi'i/Maliki.
- **Mantiq = science #19:** Owner decision 2026-04-07. Foundational logic tree required before usul al-fiqh.
- **Collection order:** Layer 1 → Layer 2 → Layer 3 → Layer 4 (per 5-coworker synthesis)
- **S-1 first within Layer 2:** All 5 coworkers independently identified this as the #1 gap
- **Existing ChatGPT workflow continues:** For remaining deep questions (K, E, D, GN, L series). No workflow disruption for these.
- **Structured review interface needed:** For Layer 4 calibration (100+ excerpt judgments). This is the main implementation work.

## Outstanding Questions

### Resolve Before Planning

- [Affects R4] Basran-only or both grammar school terminologies for nahw? (Owner not yet asked)

### Deferred to Planning

- [Affects R8] How does the fiqh masking layer integrate with Phase 2b grouping? (Technical — needs excerpting contract analysis)
- [Affects R11-R14] What is the structured review interface? (Design question for `/ce:plan`)
- [Affects R16] Should bundle format changes be applied retroactively to F1-F8/G1-G4/SC1? (Cost-benefit during planning)

## Collection Calendar (from Gemini DR, grounded in tadarruj)

| Month | Science Focus | Collection Tasks |
|-------|--------------|-----------------|
| April | Imla + Sarf | Layer 1 formalization, S-1/S-2, begin Layer 3 sessions |
| May | Nahw + Balagha | K/E/D/GN/L questionnaire items, tree reviews |
| June | Fiqh + Mantiq | Fiqh masking configuration, mantiq tree seeding, Layer 4 infrastructure |
| July 1 | Usul + Aqidah | Summer build begins, Layer 4 calibration starts |

## Next Steps

→ `/ce:plan` for structured implementation planning of the collection system
