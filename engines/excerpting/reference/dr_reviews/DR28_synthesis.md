# DR28 Synthesis — Prompt Architecture for Complex Behavioral Rules

**Sources:** ChatGPT DR (7 questions, 10+ citations) + Claude DR (7 questions, 60+ sources, 2023-2026)
**Date:** 2026-04-07
**Status:** SYNTHESIZED — coworker validation dispatched (Codex: architecture compatibility, Gemini: Arabic scholarly safety)

## Cross-Provider Convergence (7/7 questions answered)

| Question | Converged Answer | Confidence |
|---|---|---|
| Q1 System/user split | Split by function: system=constitution, user=dynamic rules+input | HIGH (both DRs agree, backed by instruction hierarchy research) |
| Q2 Structured formats | XML tags improve parsing. Claude fine-tuned for XML. Don't over-specify for GPT-5 class | HIGH (40% performance variation from format, Anthropic guidance) |
| Q3 Progressive disclosure | **Essential.** Irrelevant rules demonstrably hurt. Load only genre-relevant rules | VERY HIGH (strongest evidence: ICML 2023, IFScale NeurIPS 2025, MoP 81% win rate) |
| Q4 Rule hierarchy | Instruction sandwich: critical at beginning AND end. Middle = stable definitions | HIGH (Lost in the Middle confirmed through 2026, Claude shows recency advantage) |
| Q5 Reference appendix | Viable for large reference docs (97.9% accuracy on 400+ pages). Place at top, instructions at end | HIGH (Claude DR more favorable than ChatGPT DR) |
| Q6 Multi-turn | **Avoid.** 39% degradation from multi-turn splitting. 2-message pattern optimal | VERY HIGH (Laban et al. 2025, 200K conversations, all flagship models affected) |
| Q7 Arabic | English instructions + Arabic content. Budget 3x tokens. Arabic 2-4x token overhead | HIGH (197-experiment study confirms English outperforms Arabic instructions) |

## Key Divergence Resolved

ChatGPT DR proposed a 3-message "handshake" pattern. Claude DR proved this harmful (39% degradation, no proven benefit from pre-fabricated messages). **Resolution: 2-message pattern wins.**

## The Converged Architecture

```
MESSAGE 1 (system) — STABLE, CACHED (90% cost reduction):
  <constitution>
    Role definition + task framing
    Hard invariants (Arabic preservation, schema compliance, D-011)
    Conflict resolution precedence (FP-13 stack)
  </constitution>
  
MESSAGE 2 (user) — DYNAMIC PER CHUNK:
  <active_rules>
    Core rules (always loaded): EE-1, DECONTEXTUALIZATION, SELF-CONTAINMENT
    Conditional modules (loaded by flag): HADITH_RULES, VERSE_RULES, FIQH_RULES
  </active_rules>
  <input>
    <text>{assembled_text}</text>
    <classified_segments>{segment_summary}</classified_segments>
  </input>
  <critical_reminders>
    Top 3-5 cannot-fail rules restated (instruction sandwich)
  </critical_reminders>
```

## Progressive Disclosure Rule Modules

Based on chunk content flags, load only relevant rule modules:

| Flag | Module | Rules Loaded |
|---|---|---|
| Always | CORE | EE-1, CONFLICT RESOLUTION, DECONTEXTUALIZATION (6 rules), SELF-CONTAINMENT (C-SC-1..5), OUTPUT FORMAT |
| `has_hadith_content` | HADITH | DERIVED BENEFITS, NUMBERED ITEMS, hadith inseparable core, isnad-matn unity |
| `has_verse_content` | VERSE | Verse-commentary unity (VC-1), title retention for tarajim |
| `has_fiqh_content` | FIQH | MULTI-FUNCTION SPLIT, PROOF STRUCTURE, verdict/tarjih rules |
| `has_dialectical` | DIALECTICAL | فإن قيل/قلنا → FP-14, objection-response pairs |
| `has_introduction` | INTRO | INTRODUCTION SCOPE, MENTION IS NOT EXCERPT |

**Estimated per-call rule count:** 8-12 rules (down from 25) depending on genre. This is the key compliance improvement — P ≈ p^N means reducing from 25 to 10 rules roughly triples full-compliance probability.

## Implementation Units

| # | Unit | File(s) | Effort |
|---|---|---|---|
| IU-1 | Extract shared constitution from GROUP/CLASSIFY/ENRICH | New: `prompts.py` with CONSTITUTION constant | Medium |
| IU-2 | Add XML tags to constitution | `prompts.py` | Small |
| IU-3 | Split GROUP rules into core + 5 conditional modules | `prompts.py` + `phase2_group.py` | Large |
| IU-4 | Implement flag computation from chunk metadata | `phase2_group.py` (pre-call analysis) | Medium |
| IU-5 | Compose dynamic user message with active_rules + critical_reminders | `phase2_group.py` | Medium |
| IU-6 | Apply same architecture to CLASSIFY prompt | `phase2_classify.py` | Medium |
| IU-7 | Apply same architecture to ENRICH prompt | `phase3_enrichment.py` | Medium |
| IU-8 | Update SPEC §5.3.2, §5.2.2 to reflect new architecture | `SPEC.md` | Medium |
| IU-9 | Update test assertions for XML-tagged prompt | `test_phase2_group.py` et al | Small |
| IU-10 | A/B test: monolithic vs progressive on 50+ inputs | Script + budget (~EUR 10) | Large |

## Dependencies on Pending Validation

- **Codex CLI:** Must confirm Instructor + XML compatibility before IU-2
- **Gemini CLI:** Must confirm English-instruction safety before IU-3

## What This Means for DR21

DR21's compression research was directionally correct on ONE point: reducing rule COUNT improves compliance. But its approach (compress the WORDS) was wrong — the right approach is progressive disclosure (reduce the RULES the model sees per call). DR21 can be retired as superseded by DR28.

## Next Steps

1. Wait for Codex + Gemini validation results
2. If no BLOCKERs: implement IU-1 through IU-5 (GROUP prompt refactor) in a dedicated session
3. A/B test against current monolithic prompt
4. If results positive: implement IU-6, IU-7 (CLASSIFY, ENRICH)
5. Update SPEC (IU-8)
