# Format Diversity Experiment — Architect Evaluation

**Date:** 2026-03-22
**Evaluator:** Claude Chat (Architect)
**Commit evaluated:** 0cd57a6
**Verdict:** PASS — proceed to excerpting engine SPEC

---

## Questions Answered

### Q1: Can Phase 2 handle verse-commentary text?

**PASS.** The LLM correctly identifies verse + commentary as unified teaching units in 6/6 verse-commentary divisions, across both Approach A and Approach B.

Evidence:
- 6 divisions from شرح ابن عقيل على ألفية ابن مالك (3 from vol 1, 3 from vol 3)
- Topics ranged from تعريفات (العلم, المعرف بأداة التعريف) to أحكام (إعمال اسم الفاعل) to خلافات نحوية (نعم وبئس, أفعل التفضيل)
- Word counts: 836–1376
- Zero instances of verse fragmentation (ألفية verse separated from its commentary)
- Zero instances of cross-verse merging (commentary on one verse merged with commentary on another)
- Both A and B correctly handle complex structural features: حواشي, numbered lists with dependencies (الأول/الثاني/الثالث), شواهد شعرية, manuscript variant discussions

The ألفية verses function as natural topic delimiters — each verse introduces a distinct nahw topic, and the commentary explicates it. The LLM recognizes this via topical coherence, not explicit verse identification. This is sufficient.

**Architectural implication:** Phase 1 verse-commentary preprocessing is a quality optimization, NOT mandatory. The excerpting engine SPEC designs it as deferred.

### Q2: Does Phase 2 quality hold on 2000-4000w divisions?

**PASS.** Boundary quality on 4 taysir divisions (2513–3111 words) is comparable to the original experiment's 500–1000w prose.

Evidence:
- 4 divisions from تيسير العلام شرح عمدة الأحكام
- Topics: باب الإمامة, باب صلاة العيدين, باب الربا والصرف, كتاب الأيمان والنذور
- Word counts: 2513, 2522, 2881, 3111
- Zero boundary degradation, zero missed obvious topic shifts, zero erroneous merges
- Structural markers (حديث, المعنى الإجمالي, اختلاف العلماء, ما يؤخذ) help but quality holds even in sections without explicit markers

**Architectural implication:** Phase 1 splitting threshold stays at 5000w. No evidence that 2000-4000w degrades.

### Q3 (secondary): QA/masala format confirmation

**PASS.** 2 masala divisions (ext_39) and 1 QA division (ext_46) handled correctly. Explicit structural markers (مسألة numbers, أولا/ثانيا ordinals, فالسائل/والمسئول transitions) make these formats easier than prose.

---

## Approach A vs B Comparison

| Metric | Approach A | Approach B |
|--------|-----------|------------|
| Average units (verse-commentary) | 11.3 | 12.2 |
| Average units (longer prose) | 21.5 | 29.0 |
| Fragmentation errors | 0 | 0 |
| Merge errors | 0 | 0 |
| self_contained flag accuracy | Correct in all checked cases | Correct in all checked cases |

**Key observation:** B becomes significantly more granular at longer division lengths. The 3111w division produces 41 B-units (~76 words/unit average) vs 24 A-units (~130 words/unit). This is a granularity difference, not a quality difference.

**Recommendation:** Approach B confirmed as primary approach. Its higher granularity produces more modular teaching units. But a minimum unit size floor is needed to prevent over-atomization.

---

## Constraints for Excerpting Engine SPEC

From this experiment, the following constraints MUST be incorporated:

### C-1: Approach B as primary approach
Two-phase (classify-then-group) produces equal or better results than single-call (A) in 13/13 divisions. B's granularity is higher, which is desirable for excerpt modularity.

### C-2: MAX_TOKENS for classify call
Must be 32768 minimum for divisions over 2000 words. The default 8192 is insufficient — classify produces 125-166 segments for 2500-3100w text. RUN_SUMMARY confirms this.

### C-3: Minimum teaching unit size
The SPEC must define a floor (~50 words suggested). B's tendency to produce very atomic units (20-40 words) at longer division lengths needs a merging pass or minimum-size constraint. Adjacent sub-threshold units should be merged with their nearest neighbor.

### C-4: Full coverage verification
The excerpting engine must verify that the union of all teaching unit word ranges equals the total division text. No silent gaps or overlaps allowed.

### C-5: Verse-commentary Phase 1 handler — DEFERRED
Not architecturally required based on this experiment. Can be added as quality optimization if the 30-book targeted probe (Step 3) reveals edge cases.

### C-6: Same-model evaluation bias — UNRESOLVED
Gap 3 from the architecture decision remains open. Opus 4.6 evaluated text that Opus 4.6 processed. The owner's spot-checks during Step 3 (targeted LLM probes) are the planned mitigation.

---

## Evaluation Methodology

### Round 1: Structural Read
- Read all 5 governing files in specified order
- Read full Arabic text for all 13 divisions in the workbook
- Stated initial observations per division
- Checked verse-commentary divisions for verse fragmentation
- Compared boundary quality between verse-commentary and longer prose

### Round 2: Adversarial Probing
7 probes conducted:
1. **Verse recognition mechanism** — LLM uses topical coherence, not explicit verse identification. Sufficient.
2. **Hard case (1376w division with حاشية)** — Both approaches correctly identify editorial apparatus as distinct from main sharh.
3. **Dependency flagging (نعم وبئس numbered list)** — A correctly flags self_contained:- on dependent sub-units. B avoids the issue by incorporating more context.
4. **Merge detection at length (3111w)** — No incorrect merges found. A's boundaries align with author's structural markers.
5. **Cross-format quality comparison** — Quality comparable between verse-commentary and prose. No format-specific degradation.
6. **Failure mode search** — Searched all divisions for units under 30 words that could be verse fragments. None found.
7. **MAX_TOKENS tracing** — Confirmed 32768 needed: 200 segments × ~100 tokens + 4000 tokens input = ~24000 minimum.

### Round 3: Self-Verification + Verdict
- Verified all factual claims against source data
- Checked for rationalization patterns (3 potential rationalizations examined, 1 produced a real constraint: minimum unit size)
- Unconstrained adversarial pass found 4 things the protocol wasn't checking: pedagogical vs structural coherence, description accuracy, silent omissions, same-model bias
- Synthesized verdict with 6 constraints

---

## Open Risks

1. **Atypical verse-commentary:** This experiment tested the canonical case (Ibn Aqil on Alfiyyah). Books with less regular verse-commentary interleaving might behave differently. Mitigated by Step 3 (30-book probe).

2. **Text without structural markers at length:** Taysir has explicit markers (حديث, المعنى, etc.). A 3000w division from a text without such markers might degrade. Mitigated by Step 3.

3. **B's over-atomization:** 41 units for 3111w is extreme. If the excerpting engine doesn't enforce a minimum size, some excerpts will be too small to be useful. Addressed by constraint C-3.

4. **Same-model evaluation bias:** Unaddressed. Gap 3 remains open. Addressed at Step 3.
