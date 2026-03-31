# Campaign Analysis: campaign_20260331

## Executive Summary

| Metric | Value |
|--------|-------|
| Total excerpts | 2,303 |
| Packages | 5 (all succeeded) |
| Total cost | $96.87 |
| Total time | 10.3 hours |
| LLM traces | 1,100 calls |
| Git commit | `80ffccff` (pre-hardening) |
| Model config | Opus primary (accidental), GPT-5.4 verify, Mistral escalation |

**Key finding:** This campaign ran with Opus as primary (accidental — intended GPT-5.4). This inverted the cost structure ($97 vs expected ~$3) but produced the richest Arabic scholarly excerpt dataset in the project. The data is reusable as a BEFORE baseline for the hardened-prompt comparison.

**Known issue:** The campaign ran BEFORE prompt hardening (commit `16a5bb2e`) and model default swap (commit `9c074239`). Results reflect OLD prompts.

---

## Per-Package Quality Scorecard

| Package | Excerpts | Drops | P2a Fail | Cost | FULL % | Notes |
|---------|----------|-------|----------|------|--------|-------|
| taysir | 1,283 | 161 | 62 | $58.12 | 68.7% | Largest; most errors; fiqh sharh |
| ext_46_qa | 300 | 1 | 1 | $10.60 | 81.0% | Cleanest run; usul al-nahw |
| ibn_aqil_v3 | 282 | 15 | 0 | $10.47 | 94.3% | High quality; nahw sharh |
| ibn_aqil_v1 | 241 | 4 | 0 | $11.04 | 93.4% | High quality; nahw sharh |
| ext_39_masala | 197 | 3 | 0 | $6.65 | 84.3% | Good quality; fiqh masala |

**Observations:**
- **Taysir** dominates in both size (56% of excerpts) and errors (85% of drops). Its fiqh sharh genre has inherent complexity: hadith text + commentary + evidence interleaving.
- **ibn_aqil** packages have the highest FULL self-containment (93-94%), consistent with grammar sharh's clean rule-by-rule structure.
- **ext_46_qa** is the cleanest run: 300 excerpts, 1 validation drop, 1 phase2a failure.

---

## Top 10 Issues by Frequency

| # | Issue | Count | Severity | Affected Packages |
|---|-------|-------|----------|-------------------|
| 1 | Diacritic density mismatch (snippet vs full) | 234 | Low | All |
| 2 | text_snippet prefix mismatch (EX-V-002) | 1,135 | Fail | All |
| 3 | Taysir phase2a chunk failures | 62 | High | taysir |
| 4 | Function taxonomy validation errors | 283 | Fail | All |
| 5 | Duplicate detection (coordinate keys) | 192 | Fail | All |
| 6 | Short/long word count outliers | 172 | Warn | All |
| 7 | Word offset consistency errors | 124 | Fail | All |
| 8 | Physical page range mismatches | 104 | Fail | All |
| 9 | Double ZWNJ sequences | 80 | Low | All |
| 10 | Missing prophet honorific (SAS) | 65 | High | All |

**Root causes:**
- Issues 1-8 are **structural validator findings** from pre-hardening code. The text_snippet fix (EX-V-002) and model default swap are already committed.
- Issue 9 (ZWNJ debris) is a **known normalization artifact** from Shamela HTML — `\u200c\u200c` appears in source text.
- Issue 10 (missing honorific) needs **scholarly review** — some "محمد" mentions are personal names, not Prophet references.

---

## Structural Validator Results

| Check | Status | Findings |
|-------|--------|----------|
| Required Fields | PASS | 0 |
| Word Offset Consistency | FAIL | 124 |
| text_snippet Prefix Match | FAIL | 1,135 |
| segment_indices Validity | FAIL | 208 |
| excerpt_id Format | PASS | 0 |
| Empty Field Detection | PASS | 0 |
| Consensus Structure | PASS | 0 |
| ZWNJ Scan | WARN | 100 |
| Duplicate Detection | FAIL | 192 |
| Gate Cross-Reference | FAIL | 3 |
| Short/Long Outliers | WARN | 172 |
| author_id Audit | WARN | 2,302 |
| Consensus Coverage | PASS | 0 |
| Physical Pages | FAIL | 104 |
| Function Taxonomy Validation | FAIL | 283 |

**Note:** 6/15 checks pass, 7 fail, 3 warn. The author_id warning (2,302/2,303) reflects the Opus model's tendency to use "unknown" for author attribution — a model-specific behavior that should improve with GPT-5.4 as primary.

---

## Taxonomy Readiness Audit

54 flags total across 5 packages.

| Flag Type | Count | Severity | Action Required |
|-----------|-------|----------|-----------------|
| editorial_note_long | 24 | Medium | Review: may be misclassified muqaddimah |
| narrator_as_opinion | 14 | High | Prompt fix: transmission formula detection |
| structural_transition_long | 11 | Medium | Review: may contain hidden rulings |
| orphaned_evidence | 5 | High | Link to takhrij or evidence_refs |

**Gemini's prediction confirmed:** The `narrator_as_opinion` flags validate Gemini's warning about "Function Confusion" — scholars in isnad chains are being mislabeled as `quoted_opinion` when transmission formulas (حدثنا, عن) are present. This is a Tier-1 prompt fix for the hardened re-run.

---

## Arabic Fidelity Audit

382 flags total across 5 packages.

| Flag Type | Count | Severity | Notes |
|-----------|-------|----------|-------|
| diacritic_density_mismatch | 234 | Low | Expected: snippet truncation artifacts |
| double_zwnj | 80 | Low | Known normalization artifact from Shamela |
| missing_honorific | 65 | High | Needs scholarly review (false positive risk) |
| unmatched_curly_brackets | 2 | Medium | Check source text for bracket integrity |
| isnad_truncation | 1 | Medium | Single instance, low impact |

**Key insight:** The 65 missing honorific flags should be reviewed by the owner. The audit checks for "محمد" or "النبي" without "صلى الله عليه وسلم" within 80 characters. False positives include: (a) "محمد" as a common personal name (محمد بن عبد الحميد), (b) the honorific appearing in a different form (ﷺ ligature), (c) the honorific split across an excerpt boundary.

---

## Gold Standard Candidates

100 candidates selected (97 Tier A, 3 Tier B).

| Package | Target | Selected | Eligible Pool |
|---------|--------|----------|---------------|
| taysir | 30 | 30 | 922 |
| ibn_aqil_v1 | 15 | 15 | 212 |
| ibn_aqil_v3 | 15 | 15 | 264 |
| ext_39_masala | 20 | 20 | 158 |
| ext_46_qa | 20 | 20 | 217 |

**Selection criteria applied:** Word count 30-350, FULL or PARTIAL self-containment, no validation drops, all metadata fields present, stratified by primary_function.

### Preview: 5 Best Excerpts

**1. taysir — rule_statement (118 words, FULL)**
Topic: الأضحية عن الأحياء والأموات, الوصية بالأضحية

> والأصل في الأضحية أنها للأحياء. ويجوز أن تجعل صدقة عن الموتى، وفيها ثواب وأجر لهم. لكن يوجد في بعض البلاد، أنهم لا يكادون يجعلونها إلا للموتى فقط...

**2. ibn_aqil_v1 — rule_statement (120 words, FULL)**
Topic: عمل أفعال المقاربة, خبر كاد وعسى

> وكلها تدخل على المبتدأ والخبر فترفع المبتدأ اسما لها ويكون خبره خبرا لها في موضع نصب...

**3. ibn_aqil_v3 — rule_statement (118 words, FULL)**
Topic: إعمال اسم الفاعل المحلى بأل, صلة أل

> وإن يكن صلة أل ففي المضى … وغيره إعماله قد ارتضى. إذا وقع اسم الفاعل صلة للألف واللام عمل ماضيا ومستقبلا وحالا...

**4. ext_39_masala — rule_statement (119 words, FULL)**
Topic: تكفين الجماعة في كفن واحد, قتلى أحد

> وإذا قلت الأكفان وكثرت الموتى جاز تكفين الجماعة منهم في الكفن الواحد بأن يقسم بينهم ويقدم أكثرهم قرآنا إلى القبلة...

**5. ext_46_qa — rule_statement (120 words, FULL)**
Topic: شرط العلة الموجبة للحكم, علة إعراب المضارع

> من شرط العلة أن تكون هي الموجبة للحكم في المقيس عليه ومن ثم خطأ ابن مالك البصريين في قولهم...

---

## Function Distribution (Top 15)

| Package | Function | Count | Median Words | FULL Rate | Topic Fill |
|---------|----------|-------|-------------|-----------|------------|
| taysir | rule_statement | 556 | 36 | 0.68 | 1.00 |
| taysir | opinion_statement | 228 | 72 | 0.71 | 1.00 |
| ibn_aqil_v3 | rule_statement | 226 | 74 | 0.96 | 1.00 |
| taysir | evidence_hadith | 160 | 80 | 0.90 | 1.00 |
| ext_39_masala | rule_statement | 154 | 70 | 0.84 | 1.00 |
| ibn_aqil_v1 | rule_statement | 147 | 114 | 0.98 | 1.00 |
| taysir | definition | 105 | 47 | 0.63 | 1.00 |
| ext_46_qa | rule_statement | 88 | 64 | 0.78 | 1.00 |
| ext_46_qa | opinion_statement | 71 | 79 | 0.82 | 1.00 |
| taysir | evidence_rational | 71 | 71 | 0.54 | 1.00 |
| taysir | narration | 41 | 89 | 0.80 | 1.00 |
| ext_46_qa | definition | 40 | 59 | 0.75 | 1.00 |
| taysir | editorial_note | 35 | 134 | 0.83 | 1.00 |
| ext_46_qa | evidence_rational | 35 | 72 | 0.71 | 1.00 |
| taysir | condition_exception | 33 | 66 | 0.64 | 1.00 |

**Key insight:** Topic fill rate is 1.00 across all groups — every excerpt has at least one topic tag. FULL rate varies by genre: grammar sharh (ibn_aqil) achieves 96-98%, while fiqh sharh (taysir) is 54-90% depending on function type. This is expected: fiqh commentary inherently references hadith and prior context.

---

## Self-Containment Distribution

| Package | FULL | PARTIAL | DEPENDENT |
|---------|------|---------|-----------|
| taysir | 882 (68.7%) | 387 (30.2%) | 14 (1.1%) |
| ext_46_qa | 243 (81.0%) | 55 (18.3%) | 2 (0.7%) |
| ibn_aqil_v3 | 266 (94.3%) | 16 (5.7%) | 0 |
| ibn_aqil_v1 | 225 (93.4%) | 16 (6.6%) | 0 |
| ext_39_masala | 166 (84.3%) | 31 (15.7%) | 0 |

**Overall:** 1,782/2,303 FULL (77.4%), 505 PARTIAL (21.9%), 16 DEPENDENT (0.7%).

---

## Comparison Readiness Checklist (for hardened-prompt re-run)

- [x] Campaign BEFORE data preserved (2,303 excerpts, 1,100 LLM traces)
- [x] Structural report baseline established (7 fail, 3 warn)
- [x] Gold standard candidates selected (100 excerpts, 97 Tier A)
- [x] Taxonomy readiness risks documented (54 flags)
- [x] Arabic fidelity baseline documented (382 flags)
- [x] Model defaults fixed (commit `9c074239`: GPT-5.4 primary, Opus verify)
- [x] Prompt hardening committed (commit `16a5bb2e`: 8 Tier-1 fixes)
- [ ] Re-run with hardened prompts + correct model config
- [ ] Compare BEFORE vs AFTER on gold_core_100 excerpts
- [ ] Owner review of gold candidates for scholarly correctness
- [ ] Address 14 narrator_as_opinion misclassifications in prompts
- [ ] Address 24 editorial_note_long potential muqaddimah misclassifications
- [ ] Investigate 65 missing honorific flags (filter false positives)

---

## Analysis Artifacts

| File | Description |
|------|-------------|
| `structural_report.json` / `.md` | 15-check structural validation |
| `run_fingerprint.json` | Campaign identity + config |
| `package_summary.json` | Per-package metrics |
| `excerpt_catalog.jsonl` | 2,303 rows, all key fields |
| `trace_catalog.jsonl` | 1,100 LLM call traces |
| `function_summary.json` | 52 (package, function) groups |
| `self_containment_summary.json` | 12 (package, SC level) groups |
| `gold_candidates.jsonl` | 100 gold standard candidates |
| `taxonomy_readiness_flags.jsonl` | 54 taxonomy risk flags |
| `taxonomy_readiness_summary.json` | Taxonomy risk summary |
| `arabic_fidelity_flags.jsonl` | 382 Arabic fidelity flags |
| `arabic_fidelity_summary.json` | Arabic fidelity summary |
| `campaign_analysis.md` | This report |

---

*Generated: 2026-03-31 | Campaign: campaign_20260331 | Analyzer: Claude Code (CC)*
