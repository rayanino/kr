# NEXT — Phase C Aggregation

## Status: ALL EVALUATION SESSIONS COMPLETE

| Session | Scope | Books | VERIFIED | PLAUSIBLE | FLAG | ESCALATE | Report |
|---------|-------|-------|----------|-----------|------|----------|--------|
| 0 (Calibration) | 3 calibration books | 3 | 1 | 2 | 0 | 0 | PHASE_C_ERRATA.md §12 |
| 1 (Fixture Regression) | Fixtures + 3 additional | 14 | — | — | — | — | PHASE_C_SESSION1_REPORT.md |
| 2 (Famous Works A) | Major reference works | 14 | — | — | — | — | PHASE_C_SESSION2_REPORT.md |
| 3 (Famous Works B) | Famous works continued | 7 | 7 | 0 | 0 | 0 | PHASE_C_SESSION3_REPORT.md |
| 4 (Multi-Layer + Commentary) | sharh/hashiyah works | 10 | 9 | 1 | 0 | 0 | PHASE_C_SESSION4_REPORT.md |
| 5 (Attribution + Trust + Obscure) | Edge cases | 10 | 4 | 6 | 0 | 0 | PHASE_C_SESSION5_REPORT.md |
| 6 (Edition Groups) | Cross-edition consistency | 17 | 17 | 0 | 0 | 0 | PHASE_C_SESSION6_REPORT.md |
| 7 (Remaining) | Final 10 unevaluated | 10 | 4 | 6 | 0 | 0 | PHASE_C_SESSION7_REPORT.md |
| **TOTAL** | | **76 verdicts** | **59** | **17** | **0** | **0** | |

**73 unique books** evaluated (3 books appear in two sessions for cross-edition checks). **0 FLAG, 0 ESCALATE** across the entire corpus.

Note: Sessions 1-2 per-verdict breakdowns are in their reports but were not tracked in the running-total format used from Session 3 onward. The pre-Session 4 cumulative was 34V + 5P = 39 books (verified in Session 4 report). Sessions 1-2 individual V/P splits should be counted from their reports during aggregation.

---

## What the Aggregation Session Must Do

### 1. Produce the definitive verdict list

Read each session report and extract every per-book verdict into a single canonical table:

| Book (exact directory name) | Session | Status | Verdict | Author correct? | Genre correct? | ML correct? | Key issue |

For the 3 books evaluated twice (شرح العقيدة الطحاوية ط الرسالة in Sessions 4+6, and any others), use the later session's verdict (it had the benefit of cross-edition comparison).

### 2. Produce aggregate statistics

From the canonical table:
- Total V/P/F/E counts (verify they match 59/17/0/0)
- Verdict distribution by genre, by session, by status (success vs gate_abort)
- Author confidence distribution: min, max, mean, median — does confidence discriminate?
- Genre confidence distribution: same analysis
- Trust tier distribution for success books

### 3. Document all systematic findings

The findings below were discovered incrementally across sessions. The aggregation must present them as a unified picture.

### 4. Produce recommendations for engine improvements

Based on the systematic findings, what should be fixed before Step 4 (calibration run)?

---

## Systematic Findings (carry-forward from all sessions)

### FINDING 1: Zero Author Identification Errors

**0 author errors across 76 verdicts (73 unique books).** This is the pipeline's strongest field. Every book — from famous (ابن تيمية, النووي, ابن حجر) to obscure (هاني فقيه, أحمد قشاش) to institutional (اللجنة الدائمة) — was correctly identified. The pipeline correctly handles:
- Compiler vs author distinction (مجموع الفتاوى: ابن تيمية not ابن القاسم; المستدرك: same)
- Father vs son disambiguation (حاشية ابن عابدين vs تكملة حاشية — Session 6)
- Same author across different works (النووي ×3, ابن القيم ×5, ابن معين ×2)
- Narrator vs compiler for musnad works (مسند أبي حنيفة: أبو حنيفة not الحصكفي)

### FINDING 2: Tahqiq-Note-as-Layer Bias (5 instances)

Opus (and once GPT-5.4) classifies tahqiq editorial notes as a scholarly commentary layer, setting is_multi_layer=true when it should be false.

| # | Book | Session | Model | Muhaqiq |
|---|------|---------|-------|---------|
| 1 | الرسالة للشافعي | 2 | Opus | أحمد شاكر |
| 2 | مختصر صحيح مسلم | Errata §9 | Opus | الألباني |
| 3 | مسند أحمد ت شاكر | 2 | Opus | أحمد شاكر |
| 4 | تفسير الطبري ط التربية | 6 | GPT-5.4 | محمود شاكر |
| 5 | مختصر صحيح مسلم ت الألباني | 7 | Opus | الألباني |

Model rates: Opus 4/73 (5.5%), GPT-5.4 1/6 (16.7%), Command A 0/67+ (0% — appears immune). Can be detected mechanically: `is_multi_layer==true AND layers contains only [matn, tahqiq_note] AND muhaqiq present in extraction → flag as false positive`.

**Recommendation:** Add a post-inference validation rule to auto-correct this pattern.

### FINDING 3: Authority-Level Divergence on Classical Commentary Works

For classical sharh/hashiyah works, Opus consistently classifies as `reference` while Command A classifies as `primary`. Observed in 9/11 sharh works across Sessions 4-6. One exception: تكملة حاشية (reversed — Opus=primary, CA=reference, because it's a completion work). Modern sharh works (e.g., Session 7 Book #1, المحسن's 1984 sharh) get `modern_compilation` from Opus, not `reference` — the pattern is specific to classical works.

**Recommendation:** Document this as a known calibration difference; authority_level is not consensus-checked by the engine.

### FINDING 4: Genre Taxonomy Limitations

Several work types strain the genre enum:
- **Nukat/istidrak** (Session 7, النكت): scholarly corrections on another work — not sharh, not hashiyah, closest to risalah or other
- **Major methodological treatises** (Session 6, إعلام الموقعين): genre drifts across 3 editions (matn/other/usul_al_fiqh)
- **Lecture transcriptions** (Session 7, معالم بيانية): Shamela converts oral lectures to text; genre classification works but content_minimal limits evidence
- **Jarh wa ta'dil** (Session 7, تاريخ ابن معين): tabaqat is the closest label but not precise

**Recommendation:** Consider adding genre labels for nukat/istidrak and jarh_wa_tadil, or document that tabaqat and risalah serve as catch-all categories.

### FINDING 5: Death Date Inference Performance

Across all sessions:
- **Genuine inferences (from training data, not extraction):** 4 total — 3 correct (728 ابن تيمية, 324 الأشعري, 1306 ابن عابدين الصغير), 1 wrong (1432 vs actual 1439)
- **False positives (dates visible in author_raw text, misclassified as inferences):** 9 total
- **Pass-through (from structured extraction fields):** majority of books
- **Absent (correct):** modern/living/institutional authors

Genuine inference accuracy: 3/4 (75%). The 1 wrong case (1432 vs 1439) is within ±10 year tolerance but should still be flagged.

### FINDING 6: Gate Error Mechanism for Genre/ML Contradiction

Discovered in Session 7 (Book #4, النكت). Engine code at `validation.py:232-240` auto-corrects `is_multi_layer=false` to `true` when genre is sharh or hashiyah. If the winning model's genre is hashiyah but both models said ML=false, no layers are generated, creating the gate error "is_multi_layer=true but text_layers is empty." Root cause: incorrect genre classification by one model.

### FINDING 7: High-Confidence Wrong Cases

The most dangerous pattern — a model is confident AND wrong:
- **CA genre=hashiyah at 0.90** for النكت (Session 7) — should be risalah/other
- **Opus ML=true at 0.85-0.90** for tahqiq_note books (5 instances) — should be false
- **No high-confidence author errors** in any session — author identification confidence is well-calibrated

### FINDING 8: Consensus Module Limitations

The consensus module checks ONLY: author agreement (name similarity + death date), work agreement (genre chain), and attribution status. It does NOT check: is_multi_layer, authority_level, science_scope, or layer chains. This means `consensus.agreed=true` can coexist with disagreements on these fields.

### FINDING 9: Content Quality Limitations

- **content_minimal** (≤2 pages): affects classification confidence but not identification accuracy
- **page_count_mismatch** (partial Shamela exports): 1 book (الإبدال, 15% of content)
- **Lecture transcriptions masquerading as books** (معالم بيانية): Shamela data quality issue

---

## Engine Bugs Documented

| Bug | Severity | Sessions | Status |
|-----|----------|----------|--------|
| result.json author confidence always 1.0 | Medium | All | Known, documented in Errata §4 |
| Gate: author-science mismatch fires on broad science lists | Low | All gate_abort books | Known — registry starts empty |
| LESSONS.md factual errors about Command A availability | Info | N/A | Documented in Errata §1 |
| Genre/ML auto-correction creates impossible state | Medium | Session 7 | Documented in Session 7 report |

---

## Governing Documents the Aggregation Session Must Read

Read in this order:
1. **This file (NEXT.md)** — primary handoff
2. **PHASE_C_ERRATA.md** — corrections that override the framework (especially §4 author confidence bug, §9 tahqiq_note pattern, §10 consensus limitations)
3. **PHASE_C_EVALUATION_FRAMEWORK.md** — verdict scale definitions, field paths
4. **Session reports** (PHASE_C_SESSION1_REPORT.md through SESSION7_REPORT.md) — individual verdicts

## Key Corrections from Errata (still apply)

1. LLM filename is `claude_opus_4_6.json` NOT `opus_4_6.json`
2. All 73 books have dual-model consensus (0 single_model_fallback)
3. result.json author confidence is always 1.0 — read from llm_responses/ only
4. VERIFIED requires 2+ genuinely independent sources (Shamela-ecosystem counts as 1 collectively)
5. Consensus does NOT check multi-layer, authority_level, or science_scope
6. 6 consensus-disagreed books: 3 name-format only, 3 substantive — all documented in Errata §6

## Books Already Evaluated in Prior Sessions (13 books)

These were initially listed as unevaluated but found in prior session reports. They must NOT be re-evaluated — count from their original sessions:

| Book | Evaluated in |
|------|-------------|
| أبنية الأسماء والأفعال والمصادر | Session 1 |
| الرحيق المختوم | Session 3 |
| الرسالة للشافعي | Session 3 |
| الموسوعة الفقهية الكويتية | Session 2 |
| بداية المجتهد ونهاية المقتصد | Session 2 |
| زاد المستقنع في اختصار المقنع - ت العسكر | Session 2 |
| سير أعلام النبلاء - ط الحديث | Session 2 |
| شرح النووي على مسلم | Session 3 |
| فتح الباري بشرح البخاري - ط السلفية | Session 2 |
| لسان العرب | Session 2 |
| مذكرات مالك بن نبي - العفن | Session 1 |
| مسند أحمد - ت شاكر - ط دار الحديث | Session 2 |
| همع الهوامع في شرح جمع الجوامع | Session 1 |

---

## What Comes After Aggregation

Once the aggregation report is complete:
1. Owner reviews the aggregate findings and resolves any remaining questions
2. Systematic findings feed into engine bug fixes (Step 4 preparation)
3. The VERIFIED books become ground truth candidates for calibration
4. Phase C is CLOSED — the source engine moves to Step 4 (calibration run, 150 books, €20-30)
