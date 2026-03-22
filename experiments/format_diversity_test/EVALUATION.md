# Format Diversity Experiment — Architect Evaluation

**Date:** 2026-03-22
**Evaluator:** Claude Chat (Architect)
**Commit evaluated:** 0cd57a6
**Verdict:** PASS — proceed to excerpting engine SPEC
**Self-review:** Findings 1-8 from post-verdict adversarial review incorporated (see Revision History)

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
- **شواهد شعرية correctly distinguished from matn:** Poetry evidence citations within the commentary (numbered شواهد) are correctly grouped with their surrounding commentary, not treated as separate verse units or confused with ألفية matn. This was the experiment design's specific concern: "Poetry citations WITHIN commentary must not be confused with the matn."

The ألفية verses function as natural topic delimiters — each verse introduces a distinct nahw topic, and the commentary explicates it. The LLM recognizes this via topical coherence, not explicit verse identification. This is sufficient.

**Architectural implication:** Phase 1 verse-commentary preprocessing is a quality optimization, NOT mandatory. The excerpting engine SPEC designs it as deferred.

**Pure verse (ext_49) was excluded** from the CC run per the handoff directive: "heading-sparse, will produce unusable normalization output. Pure verse testing is deferred to engine evaluation." The experiment design's success criteria included pure verse, but the experiment design also states: "Simpler than verse-commentary — if this fails, verse-commentary certainly fails." By contraposition: verse-commentary's pass implies pure verse would likely pass. This remains an untested inference; pure verse should be validated during the 30-book probe (Step 3).

### Q2: Does Phase 2 quality hold on 2000-4000w divisions?

**PASS.** Boundary quality on 4 taysir divisions (2513–3111 words) is comparable to the original experiment's 536–1040w prose.

Evidence:
- 4 divisions from تيسير العلام شرح عمدة الأحكام
- Topics: باب الإمامة, باب صلاة العيدين, باب الربا والصرف, كتاب الأيمان والنذور
- Word counts: 2513, 2522, 2881, 3111
- Zero boundary degradation, zero missed obvious topic shifts, zero erroneous merges

**Important caveat:** All 4 taysir divisions have explicit structural markers (حديث, المعنى الإجمالي, اختلاف العلماء, ما يؤخذ). These function as near-explicit section headers that make boundary detection easier. **Long divisions without such markers remain untested.** The pass applies to well-structured text at length; marker-free text at 2000-4000w is an open risk.

**Architectural implication:** Phase 1 splitting threshold stays at 5000w for well-structured text. The SPEC should consider whether marker-free long divisions need a lower threshold — this is a design question, not yet an empirical finding.

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

**Both approaches produce correct boundaries across all 13 divisions.** Neither is strictly superior — they represent different granularity trade-offs. B's two-phase design provides finer-grained control but produces more atomic units at longer lengths (41 units for 3111w). A produces fewer, larger units (24 for the same division). The SPEC session should decide approach selection based on downstream requirements.

---

## Constraints for Excerpting Engine SPEC

### Empirically validated (from experiments)

**C-1: Two-phase extraction works.** Both Approach A (single-call) and Approach B (classify-then-group) produce correct teaching unit boundaries across all 23 divisions tested in 2 experiments. The SPEC session decides which approach to use as primary. B's two-phase design provides more architectural control points.

**C-2: MAX_TOKENS for classify call.** Must be 32768 minimum for divisions over 2000 words. The default 8192 is insufficient — classify produces 125-166 segments for 2500-3100w text. RUN_SUMMARY confirms this.

**C-4: Full coverage verification.** The excerpting engine must verify that the union of all teaching unit word ranges equals the total division text. No silent gaps or overlaps allowed.

**C-5: Verse-commentary Phase 1 handler — DEFERRED.** Not architecturally required based on this experiment. Can be added as quality optimization if the 30-book probe or engine evaluation reveals edge cases.

### Design questions (raised by experiments, not yet calibrated)

**C-3: Minimum teaching unit size.** The experiment revealed that Approach B produces units as small as 20-40 words at longer division lengths, which may be too atomic for useful excerpts. A minimum teaching unit size is needed — but the specific threshold requires empirical calibration during SPEC design or early build. It should NOT be treated as pre-decided.

**C-6: Phase 1 splitting threshold.** 5000w is supported for well-structured text (explicit markers). Marker-free long divisions may need a lower threshold. The SPEC must define how to detect marker presence and adjust accordingly.

### Open gaps (from architecture decision, not addressed by this experiment)

**C-7: Same-model evaluation bias (Gap 3).** Opus 4.6 processed text was evaluated by an Opus-based architect. The evaluation itself may be biased. **The architect must design structural mitigations for the 30-book probe** — e.g., adversarial probes with known-boundary divisions, explicit criteria that can be checked mechanically, or use of a different model for spot-check verification. The owner's spot-checks supplement but do not replace architect-designed verification.

**C-8: Books with empty/minimal division trees (Gap 4).** 5,901 books in Shamela had <5 headings. These will produce few or no leaf divisions from the normalization engine. The excerpting engine SPEC must define what happens when it receives an empty or near-empty normalized package. This gap was identified in the architecture decision but not addressed by this experiment.

---

## Evaluation Methodology

### Round 1: Structural Read
- Read all 5 governing files in specified order
- Read full Arabic text for all 13 divisions in the workbook
- Stated initial observations per division
- Checked verse-commentary divisions for verse fragmentation
- Compared boundary quality between verse-commentary and longer prose

### Round 2: Adversarial Probing
8 probes conducted:
1. **Verse recognition mechanism** — LLM uses topical coherence, not explicit verse identification. Sufficient.
2. **Hard case (1376w division with حاشية)** — Both approaches correctly identify editorial apparatus as distinct from main sharh.
3. **Dependency flagging (نعم وبئس numbered list)** — A correctly flags self_contained:- on dependent sub-units. B avoids the issue by incorporating more context.
4. **Merge detection at length (3111w)** — No incorrect merges found. A's boundaries align with author's structural markers.
5. **Cross-format quality comparison** — Quality comparable between verse-commentary and prose. No format-specific degradation.
6. **Failure mode search** — Searched all divisions for units under 30 words that could be verse fragments. None found.
7. **MAX_TOKENS tracing** — Confirmed 32768 needed: 200 segments × ~100 tokens + 4000 tokens input = ~24000 minimum.
8. **شواهد شعرية distinction** — Verified that poetry evidence citations within the commentary (e.g., شاهد 256-265 in إعمال اسم الفاعل) are correctly grouped with their surrounding commentary, not confused with ألفية matn verses.

### Round 3: Self-Verification + Verdict
- Verified all factual claims against source data
- Checked for rationalization patterns (3 potential rationalizations examined, 1 produced a real constraint: minimum unit size)
- Unconstrained adversarial pass found 4 things the protocol wasn't checking: pedagogical vs structural coherence, description accuracy, silent omissions, same-model bias
- Synthesized verdict with constraints

### Post-Verdict Self-Review (same chat — structural limitation acknowledged)
Owner requested deep critical self-review before proceeding. Found 8 findings:
1. Pure verse (ext_49) exclusion not documented
2. Marker-free long-division quality overstated
3. 50w minimum threshold presented as validated when it's a design guess
4. "B confirmed as primary" forecloses SPEC design decisions
5. Gap 4 (empty division trees) silently dropped
6. Gap 3 mitigation attributed to owner (violates QUALITY_AXIOM SO-5)
7. شواهد شعرية probe done but not documented
8. Same-chat review has structural limitations (QUALITY_AXIOM SO-8)

None change the verdict. All incorporated into this revision.

---

## Open Risks

1. **Atypical verse-commentary:** This experiment tested the canonical case (Ibn Aqil on Alfiyyah). Books with less regular verse-commentary interleaving might behave differently. Mitigated by Step 3 (30-book probe).

2. **Pure verse untested:** ext_49 was excluded from the experiment. Verse-commentary's pass implies pure verse would likely pass (contrapositive of design doc's claim), but this is inference, not evidence. Validate during Step 3.

3. **Long divisions without structural markers:** All 4 taysir divisions had explicit markers. A 3000w division from classical tafsir or lengthy fiqh discussion without such markers might degrade. Untested.

4. **B's over-atomization:** 41 units for 3111w is extreme. Minimum unit size needed but threshold requires calibration.

5. **Same-model evaluation bias (Gap 3):** Unaddressed structurally. Architect must design mitigations for Step 3.

6. **Books with empty/minimal division trees (Gap 4):** 5,901 books with <5 headings. Excerpting engine must handle empty/near-empty packages. Not addressed by this experiment.

---

## Revision History

- **v1 (1690cdf):** Initial evaluation. PASS verdict with 6 constraints.
- **v2 (this version):** Post-verdict adversarial self-review incorporated 8 findings. Constraints reframed: C-3 moved from "validated" to "design question"; C-1 reframed from "B confirmed" to "both validated, SPEC decides"; C-6 reframed from owner-dependent to architect-designed; Gap 4 added as C-8; Q2 evidence qualified with marker caveat; pure verse exclusion documented.
