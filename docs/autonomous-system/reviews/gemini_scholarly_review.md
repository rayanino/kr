# Gemini CLI — Scholarly Workflow Alignment Review of DESIGN.md

**Reviewer:** CC Agent (Gemini-style scholarly review)
**Date:** 2026-04-07
**Verdict:** PARTIALLY_ALIGNED

## Top 5 Recommendations (Scholarly Impact Order)

1. **Add "Scholarly Edge Case" gap scanner** mining FP-1 through FP-22, ADV-E-01 through ADV-E-22, and 23 domain rules. Currently the generic [OPEN] scanner misses the majority of scholarly edge cases encoded in foundational principles. Estimated yield: 50-100 high-value DR prompts.

2. **Add Arabic text safety requirements to DR relay and creative engine data flows.** Prompt generation and response processing must mandate: no Unicode normalization, byte-for-byte diacritic preservation, UTF-8 validation on file bundles, same \d/\b/.strip() prohibitions from AGENTS.md.

3. **Restructure hardening around genre-sensitive severity map (FP-21):** (a) hadith first (isnad errors = existential), (b) fiqh second (school misattribution = existential), (c) multi-layer third (layer conflation = existential), (d) nahw/usul fourth (terminological polysemy).

4. **Add DC-01 through DC-16 (deferred capabilities) as systematic Pillar 3 idea source.** The SPEC catalogs 16 deferred capabilities — each should generate 2-3 DR prompts evaluating feasibility, scholarly impact, and implementation sketch.

5. **Expand dashboard with scholarly learning content** — 6 dimensions: science discovery, scholar networks, madhab distribution, scholarly disagreement highlights, evidence type awareness, self-containment as learning signal.

## Top 5 Hardening Edge Cases (by danger)

1. Speaker-role inversion in dialectical structures (فإن قيل / قلنا) — FP-14 "#1 blind spot"
2. Isnad integrity across chunk boundaries — FP-11 sanad-matn awareness
3. Multi-layer attribution at layer transitions — SQ-1 80% threshold flipping authorship
4. Clipped tarjih (ترجيح) producing attribution corruption — FP-8 ALL-CAPS
5. Terminological polysemy across schools — FP-20 category 6 (واجب/فرض Hanafi vs Shafi'i)

## Missing Gap Scanner Sources (6)

1. Genre-specific processing gaps (7+ genres, each with unique challenges)
2. Deferred capability maturity assessment (DC-01 through DC-16)
3. Scholar authority and disambiguation (shared/scholar_authority/)
4. Foundational principle conflict resolution (FP-13 precedence stack)
5. Per-science hardening research (FP-20 categories, FP-21 severity maps)
6. Hadith variant-mismatch calibration (FP-7 MAQ-056/072)
