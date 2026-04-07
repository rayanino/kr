# Gemini DR — Verification Notes and Cross-Reference

**Verified by:** CC codebase inspection (earlier exploration agents + direct Grep/Read)
**Date:** 2026-04-07

## Verification Results

| Claim | Verdict | Evidence |
|-------|---------|----------|
| nahw_v2_0 has 183 leaves | **CONFIRMED** | taxonomy_registry.yaml:38 |
| aqidah_v0_2 exists | **CONFIRMED** | taxonomy_registry.yaml:61 |
| SCIENCE.md files are placeholders | **CONFIRMED** | All 5 say "Status: Placeholder" |
| user_model has FSRS + curriculum | **CONFIRMED** | shared/user_model/SPEC.md §4.A.3, §4.A.5 |
| FPs referenced (3,12,14,15,16,18,19,20,21) | **CONFIRMED** | All verified in SPEC.md §1.1b |
| Mantiq NOT in current sciences | **CONFIRMED** | taxonomy_registry.yaml: only nahw, sarf, balagha, imlaa, aqidah |
| No per-madhab filtering in excerpting | **CONFIRMED** | Phase 2b grouping is one-size-fits-all |
| Fiqh masking layer doesn't exist | **CONFIRMED** | No school-based filtering in excerpting contracts or config |
| Basran/Kufan distinction not addressed | **CONFIRMED** | No terminology school preference in nahw taxonomy or SPEC |

## Critical Pedagogical Claims (require owner reaction, not CC judgment)

These are SCHOLARLY claims backed by academic citations. CC cannot verify or reject them — only the owner can react:

1. **"Introducing comparative fiqh to a beginner represents a catastrophic pedagogical failure"** — Gemini DR cites classical pedagogy requiring single-madhab mastery before comparative study. The owner chose this book specifically. He needs to decide: accept the masking recommendation, or override with his own pedagogical reasoning.

2. **"Mantiq is a non-negotiable prerequisite for usul al-fiqh"** — This adds a science (#19) not in the current inventory. The owner needs to decide if he accepts this classical requirement or considers it outdated for his study goals.

3. **"The Basran school's universal rules map flawlessly to deterministic algorithmic processing"** — This is a design recommendation grounded in Islamic linguistics, not a technical constraint. The owner must decide his grammar school preference.

## 5 Unique Findings (not in any other coworker)

| # | Finding | Impact | Status |
|---|---------|--------|--------|
| 1 | Basran terminology default + Kufan synonym-mapping | Taxonomy + normalization | NEW architecture |
| 2 | Mantiq as science #19 | Taxonomy tree building | NEW science discovery |
| 3 | Fiqh masking layer (suppress other schools) | Excerpting Phase 2b | NEW architecture |
| 4 | Monthly collection calendar (Apr=imla+sarf, May=nahw+balagha, Jun=fiqh+mantiq) | Collection strategy | NEW operational plan |
| 5 | Fiqh-before-Usul as structural dependency | Processing order | NEW constraint |

## Cross-Reference: Gemini DR → Other 4 Coworkers

| Finding | DR18 | Codex | Gemini CLI | ChatGPT DR |
|---------|------|-------|------------|------------|
| Basran default | — | — | — | — |
| Fiqh masking | SYN-D-002 | DT-06 | Madhhab target | — |
| Mantiq | — | — | — | — |
| Monthly calendar | — | — | — | — |
| Fiqh before Usul | — | — | Munazarah mode | — |
| Mulazamah | — | — | FP-14/16 | — |
| 'Ard/FSRS | — | — | Active recall | — |
| Study-ready arch | EXC-D-002 | DT-08 | FP-18 | Study-ready gap |
| Flag protection | EXC-D-010 | DT-09 | — | S-1 |

**Gemini DR is the most architecturally disruptive report.** It adds 3 new architectural requirements (masking layer, synonym mapping, mantiq tree) that no other coworker identified. It also provides the only evidence-based monthly collection schedule.
