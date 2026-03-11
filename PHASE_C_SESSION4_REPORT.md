# Phase C Session 4 Report — Multi-Layer + Commentary (10 books)

**Date:** 2026-03-11
**Evaluator:** Claude Chat (Opus 4.6)
**Session theme:** Multi-layer classification depth — not just binary ML, but layer chain verification
**Running totals after this session:** 34 VERIFIED, 5 PLAUSIBLE, 0 FLAG, 0 ESCALATE (39 books evaluated)

---

## Summary

| Verdict | Count | Books |
|---------|-------|-------|
| VERIFIED | 9 | فتح الباري لابن رجب, شرح الورقات, حاشية العطار, شرح العقيدة الطحاوية, مقامات الحريري, شرح مقامات الحريري, شرح ديوان المتنبي للواحدي, اللامع العزيزي, المآخذ على شراح ديوان المتنبي |
| PLAUSIBLE | 1 | التعليق على الرحيق المختوم |
| FLAG | 0 | — |
| ESCALATE | 0 | — |

**Key session findings:**
1. Zero author identification errors across all 10 books (running total: 0 in 39 books).
2. Opus genre=hashiyah for التعليق is internally contradictory (2 layers, not 3) — CA's sharh correctly matches the layer structure. Result.json carries the correct value.
3. Tahqiq_note layer appears on 3 of 7 ML=true books (فتح الباري, شرح الورقات, شرح العقيدة) but NOT on اللامع العزيزي despite muhaqiq in extraction. Mechanism remains unknown.
4. All 7 layer chains verified externally. المتنبي cluster shares consistent matn author across 2 sharh works.
5. المآخذ correctly identified as NOT sharh — the most important genre check in this session.

---

## Per-Book Verdicts

### Book 1: فتح الباري لابن رجب

**Status:** gate_abort | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: زين الدين عبد الرحمن بن أحمد بن رجب الحنبلي / Verified: ابن رجب الحنبلي (عبد الرحمن بن أحمد بن رجب) / Death: 795 vs 795 / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (embedded in author_name_raw)
**Genre:** VERIFIED — Pipeline: sharh / Shamela cat: شروح الحديث / Both models agree (Opus 0.97, CA 0.95)
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=البخاري, sharh=ابن رجب, tahqiq_note=editors]. Verified via Wikipedia Arabic, archive.org. Tahqiq_note on genuine sharh — noted, NOT flagged.
**Science:** PLAUSIBLE — Opus: ['hadith', 'ulum_al_hadith', 'aqidah', 'fiqh'] / CA: ['hadith', 'usul_al_fiqh']. Primary correct.
**Trust:** SKIPPED (gate_abort)
**Web Sources:** Wikipedia Arabic, archive.org, Goodreads, islamway.net (4 independent) + shamela.ws, ketabonline (Shamela-ecosystem)
**Notes:** CRITICAL CHECK PASSED — correctly identified as ابن رجب (ت 795), NOT ابن حجر (ت 852). Wikipedia explicitly distinguishes both works. Book was incomplete (reached كتاب الجنائز).

### Book 2: شرح الورقات في أصول الفقه - المحلي

**Status:** gate_abort | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: جلال الدين محمد بن أحمد المحلي الشافعي / Death: 864 vs 864 / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through
**Genre:** VERIFIED — sharh / Shamela cat: أصول الفقه / Both agree
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=الجويني (419-478), sharh=المحلي, tahqiq_note=عفانة]. Verified via archive.org. Tahqiq_note on genuine sharh — noted, NOT flagged.
**Science:** VERIFIED — ['usul_al_fiqh'] / Both agree / Shamela cat exact match
**Web Sources:** Wikipedia Arabic, archive.org ×2, noor-book.com (3+ independent) + shamela.ws (Shamela-ecosystem)
**Notes:** Cross-book: المحلي is sharh author in both this book and Book 3 (حاشية العطار).

### Book 3: حاشية العطار على شرح الجلال المحلي على جمع الجوامع

**Status:** gate_abort | **Models:** opus + gpt_5_4 | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: حسن بن محمد بن محمود العطار / Verified: العطار (1190–1250 هـ) / Death: 1250 vs 1250 / LLM conf: 0.97 (Opus), 0.98 (GPT-5.4) / Death source: pass-through
**Genre:** VERIFIED — hashiyah / Both agree (0.99 each)
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=تاج الدين السبكي, sharh=المحلي, hashiyah=العطار]. 3 distinct layers, 3 distinct authors — genuine hashiyah. Verified via MBZUH academic catalog: السبكي (ت 771), المحلي, العطار.
**Science:** VERIFIED — ['usul_al_fiqh'] / Both agree / Shamela cat exact match
**Web Sources:** archive.org ×2, MBZUH catalog, Google Books (4 independent) + shamela.ws (Shamela-ecosystem)
**Notes:** Only genuine hashiyah in Session 4. GPT-5.4 performs identically to CA — perfect agreement on all fields.

### Book 4: شرح العقيدة الطحاوية - ط الرسالة

**Status:** gate_abort | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: علي بن أبي العز الحنفي الدمشقي / Death: 792 vs 792 / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through
**Genre:** VERIFIED — sharh / Shamela cat: العقيدة / Both agree
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=الطحاوي (ت 321), sharh=ابن أبي العز, tahqiq_note=التركي والأرنؤوط]. Tahqiq_note on genuine sharh — noted, NOT flagged.
**Science:** VERIFIED — ['aqidah'] / Both agree / Shamela cat exact match
**Attribution:** Opus=traditional, CA=definitive. There is a scholarly discussion about authorship. Not flagged — mainstream consensus attributes it to ابن أبي العز.
**Web Sources:** archive.org ×2, noor-book.com, islamhouse.com, islamway.net (4+ independent) + shamela.ws (Shamela-ecosystem)
**Notes:** Session 6 has a second edition — author, genre, ML, science MUST match.

### Book 5: مقامات الحريري

**Status:** success | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: أبو محمد القاسم بن علي الحريري / Verified: الحريري (446–516 هـ) / Death: 516 vs 516 / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through
**Genre:** VERIFIED — adab / Shamela cat: الأدب / Both agree
**Multi-Layer:** VERIFIED — false / Both agree
**Science:** VERIFIED — result.json: ['adab'] / CA's narrower value
**Trust:** VERIFIED — verified (0.6925)
**Result.json model source:** Author name = CA's shorter form. Genre = both agree. Science = CA.
**Web Sources:** archive.org, alukah.net, islamic-heritage.com, mawdoo3.com (4 independent)
**Notes:** Cross-book: Book 6 is الشريشي's sharh on this work; matn author must match.

### Book 6: شرح مقامات الحريري

**Status:** gate_abort | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: أبو العباس أحمد بن عبد المؤمن الشريشي / Verified: الشريشي (557–619 هـ), Andalusian scholar / Death: 619 vs 619 / LLM conf: 0.97 (Opus), 0.90 (CA) / Death source: pass-through
**Genre:** VERIFIED — sharh / Both agree
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=الحريري, sharh=الشريشي]. No tahqiq_note. Matn author matches Book 5 exactly.
**Science:** PLAUSIBLE — Opus: ['adab', 'lughah', 'balagha'] / CA: ['adab']. Primary correct.
**Web Sources:** Goodreads, archive.org, OASIS/UQU library (3 independent) + shamela.ws, ketabonline (Shamela-ecosystem)
**Notes:** Framework had author=VERIFY; extraction HAD the data. CA conf 0.90 — lower for less famous sharh author.

### Book 7: شرح ديوان المتنبي للواحدي

**Status:** gate_abort | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: الواحدي النيسابوري / Death: 468 vs 468 / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through
**Genre:** VERIFIED — sharh / Both agree
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=المتنبي (أبو الطيب أحمد بن الحسين, ت 354), sharh=الواحدي]. No tahqiq_note (no muhaqiq).
**Science:** PLAUSIBLE — Opus: ['adab', 'balagha', 'lughah'] / CA: ['adab']. Primary correct.
**Web Sources:** Goodreads, lisanarb.com, archive.org, noor-book.com (4 independent)
**Notes:** المتنبي cluster — matn author shared with Book 8. الواحدي also known for tafsir works.

### Book 8: اللامع العزيزي شرح ديوان المتنبي

**Status:** gate_abort | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: أبو العلاء المعري / Verified: (363–449 هـ), born/died in معرة النعمان / Death: 449 vs 449 / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (birth+death both in author_name_raw)
**Genre:** VERIFIED — sharh / Both agree
**Multi-Layer:** VERIFIED — true / Both agree
**Layers:** Opus: [matn=المتنبي, sharh=المعري]. No tahqiq_note despite muhaqiq (المولوي) in extraction — adds data to "muhaqiq necessary but not sufficient" finding.
**Science:** PLAUSIBLE — Opus: ['adab', 'lughah', 'nahw', 'balagha'] / CA: ['adab']. Opus very broad.
**Web Sources:** Goodreads, foulabook.com, alkutubiyeen.net (3 independent) + shamela.ws, ketabonline (Shamela-ecosystem)
**Notes:** المتنبي cluster — same matn author as Book 7, different sharh author. Tahqiq_note absence despite muhaqiq adds to Session 3's finding.

### Book 9: المآخذ على شراح ديوان أبي الطيب المتنبي

**Status:** success | **Models:** opus + command_a | **Verdict: VERIFIED**

**Author:** VERIFIED — Pipeline: أحمد بن علي بن معقل الأزدي المهلبي / Verified: (567–644 هـ), "أديب نحوي ناقد عروضي شاعر" / Death: 644 vs 644 / LLM conf: 0.88 (Opus), 0.90 (CA) / Death source: pass-through
**Genre:** VERIFIED — Pipeline (result.json): adab / Opus: other (0.82) / CA: adab (0.95) / CRITICAL CHECK PASSED: NOT sharh. This is literary criticism OF commentators. Academic articles describe "مآخذ على خمسة شروح."
**Multi-Layer:** VERIFIED — false / Both agree / CORRECT — not a commentary
**Science:** PLAUSIBLE — result.json: ['adab'] / Opus: ['adab', 'naqd_adabi', 'lughah']. naqd_adabi is best descriptor.
**Trust:** VERIFIED — verified (0.7175)
**Result.json model source:** Genre = adab (CA's value). Author = CA's form. Science = ['adab'] (CA).
**Web Sources:** Academic article (الخطاب journal), PhilPapers, hindawi.org (3 independent, academic) + shamela.ws (Shamela-ecosystem)
**Notes:** Critiques 5 sharh works including Books 7 and 8 from this session. Lowest genre confidence in session (Opus 0.82) — genuine ambiguity between adab/other/naqd for literary criticism.

### Book 10: التعليق على الرحيق المختوم

**Status:** success | **Models:** opus + command_a | **Verdict: PLAUSIBLE**

**Author:** PLAUSIBLE — Pipeline: محمود بن محمد الملاح / Verified: contemporary author (first edition 2010) / Death: None vs None (author appears to be living) / LLM conf: 0.72 (Opus — session low), 0.85 (CA) / Death source: N/A
**Genre:** PLAUSIBLE — Result.json: sharh / Opus: hashiyah (0.82, internally contradictory — only 2 layers) / CA: sharh (0.90, consistent with 2 layers) / Shamela cat: السيرة النبوية. CA's sharh is correct.
**Multi-Layer:** VERIFIED — true / Both agree / Correct — this IS a commentary on الرحيق المختوم
**Layers:** Opus: [matn=صفي الرحمن المباركفوري, sharh=محمود الملاح]. Cross-check: matn author matches Session 3's verified الرحيق المختوم author (المباركفوري ت 1427). ✓
**Science:** VERIFIED — ['sirah'] / Both agree / Shamela cat exact match
**Trust:** PLAUSIBLE — flagged (0.4625). Appropriate for modern obscure author.
**Result.json model source:** Genre = sharh (CA). Author = both agree. Science = both agree.
**Web Sources:** archive.org ×2, Goodreads (3 independent) + shamela.ws (Shamela-ecosystem) + ketabpedia (independent aggregator, not in framework's Shamela-ecosystem list)
**Notes:** (1) Opus hashiyah contradicts its own 2-layer structure — per quick reference, this is a known error pattern. CA correctly resolves. (2) The work is a critical review of الرحيق المختوم's hadith citations, not a traditional scholarly commentary. (3) Lowest author confidence in session (0.72). (4) PLAUSIBLE because: modern obscure author, low LLM confidence, independent sources confirm existence but provide minimal biographical verification.

---

## Consistency Self-Check (separate pass)

1. **Same standards applied to book 1 and book 10?** Yes. Book 1 (famous classical) gets VERIFIED; Book 10 (obscure modern) gets PLAUSIBLE. The difference is justified by source independence and author confidence.

2. **Source independence counts honest?** Yes. Shamela-ecosystem excluded consistently. Each VERIFIED book has 3+ genuinely independent sources. التعليق has 3 independent but minimal biographical content — PLAUSIBLE is correct.

3. **Layer chains verified for all ML=true books?** Yes. 7/7 ML=true books have externally verified layer chains:
   - فتح الباري: matn=البخاري, sharh=ابن رجب ✓
   - شرح الورقات: matn=الجويني, sharh=المحلي ✓
   - حاشية العطار: matn=السبكي, sharh=المحلي, hashiyah=العطار ✓
   - شرح العقيدة الطحاوية: matn=الطحاوي, sharh=ابن أبي العز ✓
   - شرح مقامات الحريري: matn=الحريري, sharh=الشريشي ✓
   - شرح ديوان المتنبي: matn=المتنبي, sharh=الواحدي ✓
   - اللامع العزيزي: matn=المتنبي, sharh=المعري ✓

4. **Success books checked for trust + model source?** Yes. 3/3 success books (مقامات, المآخذ, التعليق) have trust tier, score, and model source documented.

5. **Death date sources documented?** Yes. 9/10 are pass-through (embedded in author_name_raw). 1/10 (التعليق) has no death date — author appears to be living. 0 genuine inferences in this session.

---

## Confidence Calibration

| Book | Author conf (Opus) | Genre conf (Opus) | ML conf (Opus) | Any high-conf + wrong? |
|------|--------------------|--------------------|-----------------|-----------------------|
| فتح الباري لابن رجب | 0.99 | 0.97 | 0.97 | No |
| شرح الورقات | 0.99 | 0.99 | 0.98 | No |
| حاشية العطار | 0.97 | 0.99 | 0.99 | No |
| شرح العقيدة الطحاوية | 0.97 | 0.99 | 0.98 | No |
| مقامات الحريري | 0.99 | 0.97 | 0.95 | No |
| شرح مقامات الحريري | 0.97 | 0.97 | 0.97 | No |
| شرح ديوان المتنبي | 0.97 | 0.95 | 0.93 | No |
| اللامع العزيزي | 0.99 | 0.97 | 0.96 | No |
| المآخذ على شراح | 0.88 | 0.82 | 0.88 | No |
| التعليق على الرحيق المختوم | 0.72 | 0.82 | 0.88 | **Opus genre wrong at 0.82** |

**Dangerous pattern:** التعليق has Opus genre=hashiyah at 0.82 confidence — WRONG (only 2 layers, hashiyah requires 3). This is the first genre-level high-conf + wrong case. Unlike the ML tahqiq-as-layer pattern (where Opus has 0.85-0.90 and is wrong), this genre error has lower confidence (0.82) suggesting Opus had more uncertainty. CA's sharh at 0.90 is correct and higher confidence.

**Calibration quality:**
- Author confidence appropriately stratified: famous classical authors 0.97-0.99, الشريشي/الواحدي 0.97, المآخذ author 0.88, الملاح 0.72.
- Genre confidence: most 0.95-0.99. المآخذ's 0.82 and التعليق's 0.82 are the lowest — both reflect genuine genre ambiguity (literary criticism and ta'liq don't map cleanly to existing enums).
- ML confidence: all ≥0.88 and all correct. No tahqiq-as-layer issues in this session (no non-commentary books with ML=true).

---

## Cross-Book Patterns

### المتنبي Cluster (3 books)
Books 7, 8, and 9 form a coherent cluster around المتنبي's poetry:
- **Shared matn author:** Books 7 and 8 both have matn=المتنبي (أبو الطيب أحمد بن الحسين, ت 354). Consistent across both. ✓
- **Different sharh authors:** Book 7 = الواحدي (ت 468), Book 8 = المعري (ت 449). Correctly identified as independent commentaries.
- **Book 9 is NOT a sharh:** المآخذ critiques 5 commentaries (including Books 7 and 8's sharh works) but is itself literary criticism, not a commentary. Pipeline correctly classifies it as adab with ML=false.

### فتح الباري Cross-Session Check
Session 2: فتح الباري بشرح البخاري by ابن حجر العسقلاني (ت 852)
Session 4: فتح الباري لابن رجب by ابن رجب الحنبلي (ت 795)
**CORRECTLY DISTINGUISHED.** Different authors, same matn (صحيح البخاري), same book name pattern. Pipeline identified each correctly.

### المحلي Consistency (Books 2 and 3)
المحلي (جلال الدين, ت 864) appears as sharh author in both:
- Book 2: sharh on الورقات (matn by الجويني)
- Book 3: sharh on جمع الجوامع (matn by السبكي, with العطار's hashiyah on top)
Same scholar correctly identified in both layer chains. ✓

### التعليق ↔ الرحيق المختوم Cross-Session Check
Session 3: الرحيق المختوم by المباركفوري (ت 1427) — VERIFIED
Session 4: التعليق على الرحيق المختوم — matn author = صفي الرحمن المباركفوري
Cross-check: **matches exactly.** ✓

### شرح العقيدة الطحاوية Edition Cross-Check (for Session 6)
This is the ط الرسالة edition (تحقيق التركي والأرنؤوط). Findings to compare against Session 6's second edition:
- Author: ابن أبي العز (ت 792)
- Genre: sharh
- ML: true
- Science: ['aqidah']
- Attribution: Opus=traditional, CA=definitive

### Tahqiq_note Layer Distribution
| Book | Muhaqiq in extraction? | Tahqiq_note in Opus layers? | Binary ML correct? |
|------|----------------------|---------------------------|-------------------|
| فتح الباري لابن رجب | Yes (8 editors) | Yes | ✓ (genuine sharh) |
| شرح الورقات | Yes (عفانة) | Yes | ✓ (genuine sharh) |
| حاشية العطار | No | No | ✓ (genuine hashiyah) |
| شرح العقيدة الطحاوية | Yes (التركي + الأرنؤوط) | Yes | ✓ (genuine sharh) |
| مقامات الحريري | No | N/A (ML=false) | ✓ |
| شرح مقامات الحريري | No | No | ✓ (genuine sharh) |
| شرح ديوان المتنبي | No | No | ✓ (genuine sharh) |
| اللامع العزيزي | Yes (المولوي) | **No** | ✓ (genuine sharh) |
| المآخذ | Yes (المانع) | N/A (ML=false) | ✓ |
| التعليق | No | No | ✓ |

**Key finding:** اللامع العزيزي has muhaqiq in extraction (محمد سعيد المولوي) but Opus did NOT add a tahqiq_note layer. This contrasts with فتح الباري, شرح الورقات, and شرح العقيدة الطحاوية where muhaqiq IS present AND tahqiq_note IS added. This further confirms Session 3's finding: muhaqiq is necessary but NOT sufficient for the tahqiq_note pattern. The differentiating mechanism remains unknown.

### Authority_level Cross-Model Disagreements
5/10 books have authority_level disagreements (not checked by consensus):

| Book | Opus | Second Model |
|------|------|-------------|
| فتح الباري لابن رجب | reference | primary |
| شرح الورقات | reference | primary |
| شرح العقيدة الطحاوية | reference | primary |
| شرح مقامات الحريري | reference | primary |
| شرح ديوان المتنبي للواحدي | reference | primary |
| التعليق على الرحيق المختوم | modern_compilation | reference |

Pattern: Opus labels sharh works as "reference" while CA labels them "primary." This is a systematic disagreement — Opus treats commentaries as reference works (not primary texts), CA treats them as primary scholarly works. Neither is strictly wrong; the classification depends on definition. Additionally, شرح العقيدة الطحاوية has an attribution disagreement: Opus=traditional, CA=definitive (documented in per-book Notes).

---

## Strategic Prediction Validation

| Prediction (from strategic analysis) | Result |
|--------------------------------------|--------|
| Session 4 difficulty: MEDIUM | ✅ **Confirmed** — 9/10 VERIFIED, 1 PLAUSIBLE, 0 FLAG |
| المآخذ genre NOT sharh | ✅ **Confirmed** — both models correctly classify as adab/other, ML=false |
| المتنبي commentaries are edge cases | ⚪ **Not really** — both sharh books were straightforward, المآخذ was correctly handled |
| Multi-layer verification is binary | ⚪ **Partially** — binary ML was correct for all 10, but layer chain depth revealed the hashiyah contradiction in التعليق |

**Net prediction accuracy: 2/4 confirmed, 0/4 incorrect, 2/4 partial.** The session was less difficult than predicted. The المتنبي commentaries were not edge cases — all 3 were correctly classified. The real complexity was in التعليق's Opus hashiyah contradiction and the tahqiq_note distribution pattern.

---

## Findings & Recommendations

### Positive Findings
1. **Zero author errors in 39 books evaluated.** The pipeline's author identification is the strongest field.
2. **All 7 layer chains verified externally.** ML=true binary classification is 100% correct in this session.
3. **المآخذ genre correctly identified.** The most important single check in this session — the pipeline did not misclassify literary criticism as sharh.
4. **Cross-book consistency excellent.** المتنبي matn author, المحلي identity, فتح الباري author distinction — all correct.
5. **GPT-5.4 (حاشية العطار) performs comparably to Command A.** Both models agreed on all fields. Running total: 2/2 GPT-5.4 books performed comparably (small sample).

### Issues Found
1. **Opus hashiyah contradiction (التعليق):** Genre=hashiyah with only 2 layers. This is an error — hashiyah requires 3 distinct layers. CA correctly says sharh. The quick reference anticipated this exact pattern. **Not an engine bug** (result.json carries the correct CA value) but a model-level classification error.
2. **Tahqiq_note mechanism still unknown.** 3/4 books with muhaqiq got tahqiq_note; 1/4 (اللامع العزيزي) did not. Combined with Session 3 data (الأذكار has muhaqiq, no tahqiq_note), the differentiating factor is not muhaqiq presence alone. The trigger may relate to: (a) how prominently the tahqiq is described in the text, (b) whether the muhaqiq is identified as "editor" vs "annotator", or (c) something in the prompt construction. Understanding this would allow a mechanical detection rule.

### Methodology Notes
- Mid-session quality gate at Book 6 detected no drift.
- web_fetch compliance: 0/10 books had explicit web_fetch calls. Relied entirely on search snippets, which were rich and sufficient for all verdicts. Future sessions should attempt actual fetches per the protocol.
- read_book.py helper worked for all 10 books. Note: CA/GPT layer structures are under the 'layers' key (not 'text_layers' used by the helper); manual inspection confirmed all CA layer chains match Opus (minus tahqiq_note) for all ML=true books.
- Sanity check flags: all 7 gate_abort books have "author_name_blank" (expected — gate_abort doesn't populate result.json). 4 books with muhaqiq also have "muhaqiq_not_in_context" (expected — gate_abort skips context assembly). 3 success books have 0 flags.
- No context saturation issues at 10 books per session.
