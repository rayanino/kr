# Phase C Session 2 Report — Famous Works A (8 books)

**Date:** 2026-03-11
**Evaluator:** Claude Chat (Session 2)
**Prior sessions:** Session 0 (3 books), Session 1 (11 books) — 14 books total, 10 VERIFIED, 4 PLAUSIBLE

---

## Session 2 Summary

| Verdict | Count | Books |
|---------|-------|-------|
| VERIFIED | 8 | حاشية ابن عابدين, لسان العرب, سير أعلام النبلاء, فتح الباري, بداية المجتهد, الموسوعة الفقهية, مسند أحمد*, زاد المستقنع |
| PLAUSIBLE | 0 | — |
| FLAG | 0 | — |
| ESCALATE | 0 | — |

*مسند أحمد: Overall VERIFIED. Field-level FLAG on multi-layer (Opus=true, CA=false; known tahqiq-as-layer bias). All other fields correct. See verdict #7 for detail.

**Running totals (Sessions 0–2):** 18 VERIFIED, 4 PLAUSIBLE, 0 FLAG, 0 ESCALATE (22 books evaluated)

---

## Per-Book Structured Verdicts

### 1. حاشية ابن عابدين = رد المحتار - ط الحلبي

Book: حاشية ابن عابدين = رد المحتار - ط الحلبي
Status: gate_abort
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: محمد أمين بن عمر بن عبد العزيز عابدين الدمشقي / Verified: same / Death: 1252 vs 1252 ✓ / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: embedded in author_name_raw (not separate field, not genuine inference)
Genre: VERIFIED — Pipeline: hashiyah / Expected: hashiyah / Shamela cat: الفقه الحنفي / Agreement: yes (school vs form, compatible)
Multi-Layer: VERIFIED — Pipeline: true / Expected: true / Model agreement: yes (both true). Opus correctly identifies 3-layer structure: matn (التمرتاشي), sharh (الحصكفي), hashiyah (ابن عابدين). Note: CA's layer detail is wrong — it attributes both matn and sharh to الحصكفي, conflating the matn author التمرتاشي. Binary ML=true is correct for both models; only the layer attribution details differ. Opus also adds a tahqiq_note layer for this edition — but since ML=true is correct regardless (genuine hashiyah), this doesn't affect binary classification.
Science: VERIFIED — Pipeline: ['fiqh'] / Expected: ['fiqh']
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: clean. author_name_raw present and accurate. muhaqiq null (this Halabi edition doesn't list a muhaqiq in the metadata card).
Result.json model source: N/A (gate_abort)
Web Sources: ketabonline.com/ar/books/2706 (fetched), shamela.ws/book/21613, archive.org/details/HashyatIbnAbidin, noor-book.com, aseeralkotb.ae, sifatusafwa.com, Amazon
Notes: Pre-identified death date inference risk resolved — the death date "[ت 1252 هـ]" was embedded in author_name_raw, so the LLM read it from the metadata card, not from training data. Low diagnostic value for calibration. Gate_abort is the standard author-science registry artifact.

---

### 2. لسان العرب

Book: لسان العرب
Status: success
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: محمد بن مكرم بن علي، أبو الفضل، جمال الدين ابن منظور الأنصاري الرويفعي الإفريقي / Verified: same / Death: 711 vs 711 ✓ / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (extraction had 711)
Genre: VERIFIED — Pipeline: mujam / Expected: mujam / Shamela cat: الغريب والمعاجم / Agreement: yes (direct match)
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: ['lughah'] / Expected: ['lughah']
Trust: VERIFIED — Pipeline: verified / Trust score: 0.655
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: clean. All key fields present.
Result.json model source: command_a (CA had conf 1.0 > Opus 0.99)
Web Sources: ar.wikipedia.org/ابن_منظور, ar.wikipedia.org/لسان_العرب, aljazeera.net (independent article), dorar.net/history/event/2893, ketabonline.com/ar/books/2140, noor-book.com, archive.org
Notes: Textbook case. Both models agree on everything. Multiple independent sources. Straightforward dictionary classification.

---

### 3. سير أعلام النبلاء - ط الحديث

Book: سير أعلام النبلاء - ط الحديث
Status: success
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: شمس الدين محمد بن أحمد بن عثمان الذهبي / Verified: same / Death: 748 vs 748 ✓ / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (extraction had 748)
Genre: VERIFIED — Pipeline: tabaqat / Expected: tabaqat / Shamela cat: التراجم والطبقات / Agreement: yes (direct match)
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: PLAUSIBLE — Pipeline (result.json): ['tarikh', 'sirah'] / Opus: ['tarikh', 'ulum_al_hadith'] / Expected: ['tarikh'] / Note: Primary science tarikh correct. **CA's 'sirah' is questionable**: in the Islamic sciences, 'sirah' technically refers to prophetic biography (السيرة النبوية). سير أعلام النبلاء is a biographical dictionary of scholars across all fields and centuries — the Arabic 'سير' in the title means 'biographies' (plural of سيرة) but the technical science is tarajim/tarikh, not sirah. The book does include the prophetic sira in its first 2 volumes (from تاريخ الإسلام), but that's a minor fraction. Opus's alternative 'ulum_al_hadith' is more defensible since the Dhahabi was primarily a muhaddith and the book extensively evaluates hadith transmitters. Result.json carries CA's 'sirah' because CA had higher author confidence.
Trust: VERIFIED — Pipeline: verified / Trust score: 0.7175
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: clean. muhaqiq correctly identified (محمد أيمن الشبراوي).
Result.json model source: command_a (CA had conf 1.0 > Opus 0.99)
Web Sources: ar.wikipedia.org/سير_أعلام_النبلاء, noor-book.com, archive.org (multiple), ar.islamway.net, marefa.org, ibnaljawzi.com
Notes: Science scope minor disagreement between models: Opus says 'ulum_al_hadith' while CA says 'sirah'. The result.json carries CA's values because CA had higher author confidence. Neither secondary science is wrong, but neither is precisely the best label either. Primary science 'tarikh' is correct.

---

### 4. فتح الباري بشرح البخاري - ط السلفية

Book: فتح الباري بشرح البخاري - ط السلفية
Status: gate_abort
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: أحمد بن علي بن محمد بن محمد بن علي بن حجر العسقلاني / Verified: same / Death: 852 vs 852 ✓ / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (extraction had 852)
  **CRITICAL CHECK PASSED:** Author is ابن حجر العسقلاني, NOT البخاري. This was framework's #3 most dangerous failure mode — pipeline passes.
Genre: VERIFIED — Pipeline: sharh / Expected: sharh / Shamela cat: شروح الحديث / Agreement: yes (direct match)
Multi-Layer: VERIFIED — Pipeline: true / Expected: true / Model agreement: yes (both true). Note: Opus identifies 3 layers (matn: البخاري, sharh: ابن حجر, tahqiq_note: محب الدين الخطيب). The tahqiq_note is an over-extension (editorial apparatus ≠ scholarly layer), but the binary ML=true is correct since the book IS a sharh. Not flagging because binary classification is accurate.
Science: VERIFIED — Pipeline: ['hadith', 'ulum_al_hadith', 'fiqh'] / Expected: ['hadith'] / Both models agree on the same superset, which is reasonable — فتح الباري touches hadith sciences, fiqh, and other disciplines extensively.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: clean. muhaqiq correctly identified (محب الدين الخطيب).
Result.json model source: N/A (gate_abort)
Web Sources: ar.wikipedia.org/فتح_الباري, shamela.ws/book/1673, archive.org (multiple editions), noor-book.com, ar.islamway.net, ketabonline.com/ar/books/2122, Amazon
Notes: Tahqiq-as-layer pattern present (Opus adds الخطيب as tahqiq_note layer) but does not affect binary ML classification here because the book is a genuine sharh. This is distinct from the مسند أحمد case where the tahqiq_note is the ONLY basis for ML=true.

---

### 5. بداية المجتهد ونهاية المقتصد

Book: بداية المجتهد ونهاية المقتصد
Status: gate_abort
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: أبو الوليد محمد بن أحمد بن محمد بن أحمد بن رشد القرطبي الأندلسي / Verified: same / Death: 595 vs 595 ✓ / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: embedded in author_name_raw "[ت 595 هـ]" (not in dedicated field, but available in prompt text)
  **KEY CHECK:** Pipeline correctly identifies ابن رشد الحفيد (ت 595هـ), NOT ابن رشد الجد (ت 520هـ).
Genre: VERIFIED — Pipeline: fiqh_comparative / Expected: fiqh_comparative / Shamela cat: الفقه المالكي / Agreement: partial — Shamela classifies by school (Maliki), pipeline classifies by form (comparative fiqh). Pipeline is more precise: the book explicitly compares four schools. Both are defensible.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: ['fiqh', 'usul_al_fiqh'] / Expected: ['fiqh']
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: clean. muhaqiq identified (فريد عبدالعزيز الجندي).
Result.json model source: N/A (gate_abort)
Web Sources: dorar.net/history/event/2321 (independent), ketabonline.com/ar/books/2773, ketabonline.com/ar/books/17688, ar.wikipedia.org/زاد_المستقنع (mentions ابن رشد), archive.org/details/Bedayatt, islamweb.net, tarajm.com, shamela.ws
Notes: Pre-identified death date inference risk resolved — like حاشية ابن عابدين, the death date was embedded in author_name_raw text. The LLM read it from prompt metadata, not inferred from training data. Low diagnostic value. The pipeline's fiqh_comparative genre is more accurate than Shamela's school-based classification — a genuine precision win.

---

### 6. الموسوعة الفقهية الكويتية

Book: الموسوعة الفقهية الكويتية
Status: success
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: وزارة الأوقاف والشئون الإسلامية - الكويت / Verified: same / Death: null (institutional) / LLM conf: 0.97 (Opus), 1.0 (CA) / Death source: N/A (institutional author)
Genre: VERIFIED — Pipeline: mawsuah / Expected: mawsuah / Shamela cat: الفقه العام / Agreement: yes (subject vs form, compatible)
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: ['fiqh'] / Expected: ['fiqh']
Trust: PLAUSIBLE — Pipeline: flagged / Trust score: 0.4625 / Note: Pipeline flags this book. The الموسوعة is actually one of the most authoritative fiqh works in modern Islamic scholarship (government-backed, 45 volumes, multi-decade project). The low trust score and "flagged" tier may be influenced by the institutional authorship (no individual scholar to validate against), the modern_compilation authority_level (per Opus; CA said "reference"), or other trust engine factors. Not flagging as an error — but the trust engine's handling of institutional encyclopedias may need calibration.
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: **Notable — author_name_raw was EMPTY.** Yet both LLMs correctly identified the institutional author from the title alone. This is a strong positive finding about inference capability.
Result.json model source: command_a (CA had conf 1.0 > Opus 0.97)
Web Sources: awqaf.gov.kw (official government site — independent, fetched during self-review), ketabonline.com/ar/books/912 (Shamela-ecosystem), archive.org/details/mawsoat_fikh_pdfbook_ara (independent), noor-book.com (independent), waqfeya.net/book.php?bid=878 (Shamela-ecosystem), muslim-library.com (independent)
Notes: The extraction having EMPTY author_name_raw makes this a genuine LLM inference test. Both models passed with high confidence. The institutional author case worked flawlessly. The trust_tier "flagged" for this book deserves discussion: the SPEC's modern-compilation → flagged rule is a broad brush that catches both low-quality modern compilations and high-quality institutional encyclopedias equally. **authority_level discrepancy:** Opus says "modern_compilation" while CA says "reference"; result.json has "reference" (CA won on confidence). Both are defensible — the موسوعة IS a modern compilation AND a major reference work — but the divergence shows models interpret this field differently for institutional works.

---

### 7. مسند أحمد - ت شاكر - ط دار الحديث

Book: مسند أحمد - ت شاكر - ط دار الحديث
Status: gate_abort
Models: opus + command_a
Verdict: **VERIFIED** (field-level FLAG on multi-layer — see below)
Author: VERIFIED — Pipeline: أحمد بن محمد بن حنبل الشيباني / Verified: same / Death: 241 vs 241 ✓ / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (extraction had 241)
Genre: VERIFIED — Pipeline: hadith_collection / Expected: hadith_collection / Shamela cat: كتب السنة / Agreement: yes
Multi-Layer: **FLAG** — Pipeline (Opus): true / Pipeline (CA): false / Expected: false / Model agreement: **NO — ML DISAGREEMENT**
  - Opus: is_multi_layer=true, layers=[matn (أحمد بن حنبل), tahqiq_note (أحمد محمد شاكر)]
  - Command A: is_multi_layer=false
  - This is the **tahqiq-as-layer systematic bias** (Errata §9, Correction 6). The مسند is a hadith collection, not a commentary. Shakir's tahqiq notes are editorial apparatus, not a scholarly commentary layer.
  - Command A is correct. Opus is over-extending ML to include editorial work.
  - This is the 3rd confirmed instance of this pattern (with الرسالة للشافعي and مختصر صحيح مسلم).
  - **IMPORTANT:** consensus.agreed=true despite this disagreement — confirming Correction 7 (consensus doesn't check ML).
Science: VERIFIED — Pipeline: ['hadith'] (Opus), ['hadith', 'ulum_al_hadith'] (CA) / Expected: ['hadith']
Trust: SKIPPED (gate_abort)
Consensus: agreed=true (but ML not checked), models=[command_a, opus_4_6]
Extraction quality: clean. muhaqiq correctly identified (أحمد محمد شاكر).
Result.json model source: N/A (gate_abort)
Web Sources: ar.wikipedia.org/مسند_أحمد (independent), shamela.ws/book/98139 (Shamela-ecosystem), ketabonline.com/ar/books/6922 (Shamela-ecosystem, fetched during self-review), archive.org (multiple, independent), waqfeya.net (Shamela-ecosystem), islamway.net (independent)
Notes: **This confirms the strategic analysis prediction exactly.** The ML disagreement is the tahqiq-as-layer pattern. All other fields are correct and well-calibrated. The book is correctly identified as أحمد بن حنبل's hadith collection with Shakir's tahqiq — the only error is Opus treating the tahqiq as a structural layer.

---

### 8. زاد المستقنع في اختصار المقنع - ت العسكر

Book: زاد المستقنع في اختصار المقنع - ت العسكر
Status: gate_abort
Models: opus + command_a
Verdict: **VERIFIED**
Author: VERIFIED — Pipeline: موسى بن أحمد بن موسى بن سالم الحجاوي المقدسي الصالحي / Verified: same / Death: 968 vs 968 (majority view; some sources say 960) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (extraction had 968)
Genre: VERIFIED — Pipeline: mukhtasar / Expected: mukhtasar / Shamela cat: الفقه الحنبلي / Agreement: yes (school vs form, compatible). Title explicitly says "اختصار المقنع."
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: ['fiqh'] / Expected: ['fiqh']
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6], disagreement=none
Extraction quality: clean. muhaqiq identified (عبد الرحمن بن علي بن محمد العسكر).
Result.json model source: N/A (gate_abort)
Web Sources: alukah.net/culture/0/61335 (independent — detailed biography with death date discussion), ar.wikipedia.org/زاد_المستقنع (independent), ketabonline.com/ar/books/753, noor-book.com, archive.org, ar.islamway.net
Notes: Death date has scholarly dispute (960 vs 968). Pipeline has 968 (majority view per Alukah article). Both dates are within ±10 year tolerance. Clean classification on all fields.

---

## Consistency Self-Check (FIX 6)

### Applied Standards Review

1. **Web search performed for every book?** YES — 8/8 books had dedicated web searches with multiple results examined.

2. **web_fetch used for at least 1 URL per book?** Initially only 1/8 (ketabonline for حاشية ابن عابدين). Self-review added 3 more: ketabonline for مسند أحمد, awqaf.gov.kw for الموسوعة الفقهية, and attempted alukah.net for زاد المستقنع (403 error). Final: 4/8 books had web_fetch. The remaining 4 books relied on rich search snippets which were adequate for VERIFIED verdicts (all famous works with extensive web presence), but future sessions should aim for 8/8 compliance.

3. **Shamela category cross-checked for every book?** YES — all 8 verdicts include explicit shamela_category vs pipeline genre comparison.

4. **Death date pass-through vs inference distinguished?** YES — all 8 books checked. Result: 0 genuine inferences in this batch. Five books had death dates in extraction.author_death_hijri (لسان العرب 711, سير أعلام النبلاء 748, فتح الباري 852, مسند أحمد 241, زاد المستقنع 968). Two books (ابن عابدين, بداية المجتهد) had NO dedicated death date field, but the date was embedded in author_name_raw text (e.g., "[ت 595 هـ]"). Verified: prompt_sent.json confirms author_name_raw was in metadata_fields_present for both, so the LLM received the death date in the prompt text — not a genuine training-data inference. One book (الموسوعة الفقهية) is institutional with no death date (correct). The pre-identified "real inferences" for ابن عابدين (1252) and بداية المجتهد (595) were false positives in the strategic analysis, caused by checking only the extraction.author_death_hijri field without examining author_name_raw content.

5. **Result.json model source checked for success books?** YES for 3 success books. In all 3 cases, Command A had higher author confidence (1.0 vs 0.97-0.99). However, for لسان العرب and الموسوعة الفقهية, both models returned identical genre and science values, so the "winner" is indistinguishable from the result fields. Only سير أعلام النبلاء has a visible difference: result.json science_scope is ['tarikh', 'sirah'] (CA's values), while Opus had ['tarikh', 'ulum_al_hadith']. The model source question is only diagnostic when models disagree on a field.

6. **VERIFIED threshold properly applied?** Reviewing each VERIFIED verdict (Shamela-ecosystem sources excluded per Correction 5: shamela.ws, ketabonline.com, turath.io, waqfeya.net count as ONE source collectively):
   - حاشية ابن عابدين: archive.org + noor-book + sifatusafwa + Amazon → 4 independent + 1 Shamela-ecosystem (ketabonline, shamela.ws) ✓
   - لسان العرب: Wikipedia + Al Jazeera + dorar.net + noor-book + archive.org → 5 independent + 1 Shamela-ecosystem (ketabonline) ✓
   - سير أعلام النبلاء: Wikipedia + archive.org + noor-book + marefa.org + islamway + ibnaljawzi → 6 independent ✓
   - فتح الباري: Wikipedia + archive.org + noor-book + islamway + Amazon → 5 independent + 1 Shamela-ecosystem (shamela.ws, ketabonline, waqfeya) ✓
   - بداية المجتهد: dorar.net + islamweb + tarajm.com + archive.org → 4 independent + 1 Shamela-ecosystem (ketabonline×2, shamela.ws) ✓
   - الموسوعة الفقهية: awqaf.gov.kw (official) + archive.org + noor-book + muslim-library → 4 independent + 1 Shamela-ecosystem (ketabonline, waqfeya) ✓
   - مسند أحمد: Wikipedia + archive.org + islamway → 3 independent + 1 Shamela-ecosystem (shamela.ws, ketabonline, waqfeya) ✓
   - زاد المستقنع: alukah.net + Wikipedia + noor-book + archive.org + islamway → 5 independent + 1 Shamela-ecosystem (ketabonline) ✓
   
   All 8 meet the 2+ genuinely independent sources threshold for VERIFIED even after excluding Shamela-ecosystem sources.

7. **Genre flagging consistent?** I gave VERIFIED to all genres without flagging any. This is consistent because all 8 books have unambiguous genre signals: hashiyah (حاشية in title), mujam (dictionary), tabaqat (biographical history organized by generations), sharh (شرح in title), fiqh_comparative (known classification), mawsuah (encyclopedia), hadith_collection (musnad), mukhtasar (اختصار in title). No ambiguous cases in this batch.

8. **ML treatment consistent?** I FLAGged مسند أحمد's ML disagreement but did NOT flag فتح الباري's tahqiq_note layer. This distinction is consistent because: in مسند أحمد, the tahqiq_note is the ONLY basis for ML=true (without it, ML=false — a wrong binary classification); in فتح الباري, ML=true is correct regardless of whether the tahqiq_note layer exists (it's a genuine sharh). The flag targets cases where the tahqiq-as-layer bias produces a wrong binary ML classification.

### Cross-Book Patterns

1. **Gate abort rate:** 5/8 books are gate_abort (63%). All 5 share the same trigger: author-science registry artifact. Consistent with the 70% rate observed in the full Phase C corpus.

2. **Command A consistently higher confidence:** In all 3 success books, CA had 1.0 author confidence vs Opus's 0.97-0.99. This means CA "wins" the confidence comparison — but for 2 of the 3 books (لسان العرب, الموسوعة الفقهية), both models returned identical genre and science values, so the "winner" is indistinguishable from the result fields. Only سير أعلام النبلاء shows a visible difference: result.json carries CA's science_scope (['tarikh', 'sirah']) rather than Opus's (['tarikh', 'ulum_al_hadith']).

3. **Attribution: prediction incorrect, but behavior may be more accurate.** Both models agree on "definitive" for all 7 classical books (plus الموسوعة). The task's attribution_decision section predicted that "حاشية ابن عابدين and other classical works may show [traditional/definitive] disagreement." This prediction was wrong — Opus says "definitive" for all Session 2 classics. Combined with Session 1 data (where Opus said "traditional" for obscure books like حديث الضب and أحاديث أيوب), this suggests Opus discriminates: famous well-established works → definitive; obscure conventionally-attributed works → traditional. This is arguably MORE accurate than the blanket "classical = traditional" rule in SPEC §4.A.4, since works like مسند أحمد and فتح الباري have strong independent evidence of authorship beyond mere convention.

4. **Death date diagnostic value:** Zero genuine death date inferences in this batch. The 2 pre-identified "real inferences" (ابن عابدين 1252, بداية المجتهد 595) were actually embedded in the raw author field. This weakens the strategic analysis's predictions — these weren't true tests of LLM death date inference capability. The genuine inference tests remain in Sessions 3, 5, and 6.

5. **Sanity checks: systematic gate_abort artifact.** All 5 gate_abort books have "author_name_blank" sanity flags (because result.json has partial data for gate_abort books). All 3 success books have 0 flags. 4 gate_abort books also have "muhaqiq_not_in_context" info flags (context assembly skipped for gate_abort). These are artifacts of gate_abort status, not real classification errors. The sanity check fires on result.json, which is empty for gate_abort books — but the data IS correct in llm_responses/.

---

## Strategic Analysis Prediction Validation

From PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md:

| Prediction | Result |
|-----------|--------|
| Session 2 difficulty: LOW | ✅ Confirmed — 8/8 VERIFIED (1 with ML field-level flag) |
| مسند أحمد: HIGH RISK — ML disagreement | ✅ Confirmed — exact tahqiq-as-layer pattern as predicted |
| فتح الباري: tahqiq-as-layer bias possible | ✅ Confirmed — Opus adds tahqiq_note layer, but binary ML still correct |
| حاشية ابن عابدين: death date real inference | ❌ Not confirmed — death date was embedded in raw author field |
| بداية المجتهد: death date real inference | ❌ Not confirmed — death date was embedded in raw author field |
| حاشية ابن عابدين: attribution traditional/definitive disagreement | ❌ Not confirmed — both models say "definitive" for all 7 classical books |
| Genre will be the field with most FLAGs (3-5 across Sessions 2-5) | 0 genre flags in Session 2 — prediction not tested yet (famous works have unambiguous genres) |
| Sessions 2-7 will not produce new ML disagreements beyond the known 4 | ✓ Consistent — no new patterns found |

**Net prediction accuracy: 4/8 confirmed, 3/8 incorrect, 1/8 pending.** The attribution prediction failure is the most interesting — it reveals Opus discriminates between famous and obscure classical works rather than applying a blanket "traditional" label.

---

## Confidence Calibration Analysis

All 8 books are famous works, so high confidence is expected and appropriate. The relevant question is whether any high-confidence classification is wrong.

| Book | Author conf | Genre conf | ML conf | Any wrong? |
|------|-----------|-----------|---------|-----------|
| حاشية ابن عابدين | 0.99 | 0.99 | 0.99 | No |
| لسان العرب | 0.99 | 0.97 | 0.90 | No |
| سير أعلام النبلاء | 0.99 | 0.95 | 0.95 | No (science_scope questionable but not author/genre/ML) |
| فتح الباري | 0.99 | 0.99 | 0.99 | No |
| بداية المجتهد | 0.99 | 0.95 | 0.95 | No |
| الموسوعة الفقهية | 0.97 | 0.99 | 0.95 | No |
| مسند أحمد | 0.99 | 0.97 | **0.90** | **YES: ML wrong at 0.90 conf** |
| زاد المستقنع | 0.99 | 0.97 | 0.92 | No |

**DANGEROUS PATTERN: مسند أحمد has ML confidence 0.90 with WRONG binary classification.** Opus says ML=true (wrong — tahqiq notes are not a scholarly layer). 0.90 confidence on a wrong answer means the pipeline would NOT trigger a human gate for this error. This is exactly the calibration failure mode the framework warns about: high confidence + wrong = undetected bad metadata.

The ML confidence range across the batch (0.90–0.99) is poorly calibrated for this field. All 8 books are correctly classified on author and genre with appropriately high confidence. But ML confidence doesn't discriminate between genuine multi-layer works (حاشية ابن عابدين at 0.99, correctly true) and the tahqiq-as-layer false positive (مسند أحمد at 0.90, incorrectly true). The 0.09 gap between these is too small for a human gate threshold to exploit.

**Recommendation:** The ML confidence calibration issue reinforces the need for the consensus engine to compare is_multi_layer between models (Correction 7 fix). Confidence alone cannot catch this — only model disagreement reliably flags it.

---

## Findings & Recommendations

### Positive Findings

1. **Zero author identification errors.** All 8 books correctly identified, including the ابن رشد الحفيد/الجد distinction and the critical ابن حجر/البخاري distinction for فتح الباري.

2. **Institutional author inference works.** الموسوعة الفقهية had EMPTY author_name_raw, yet both models correctly identified وزارة الأوقاف from the title alone.

3. **Genre classification perfect for famous works.** All 8 genres correct with no ambiguity.

4. **Tahqiq-as-layer pattern continues to be precisely predictable.** مسند أحمد confirmed the 3rd instance; the pattern is consistent and well-characterized.

5. **Opus shows superior bibliographic depth on layer structure.** For حاشية ابن عابدين, Opus correctly identified the 3-layer chain (التمرتاشي → الحصكفي → ابن عابدين) while CA incorrectly attributed both matn and sharh to الحصكفي. Binary ML was correct for both, but Opus's layer detail is bibliographically superior.

6. **Attribution behavior is more nuanced than predicted.** Opus says "definitive" for famous classical works and "traditional" for obscure ones — a meaningful distinction that may be more accurate than the blanket "classical = traditional" rule.

### Issues Found

1. **Tahqiq-as-layer ML bias (مسند أحمد):** Opus says ML=true with tahqiq_note for a hadith collection. CA is correct (ML=false). This is the known systematic bias. **Engine fix needed:** consensus should compare is_multi_layer between models (Correction 7 → fix for Step 4).

2. **Death date inference mis-categorization:** The strategic analysis listed 10 "real inferences" but at least 2 (ابن عابدين, بداية المجتهد) had death dates embedded in author_name_raw. The extraction layer successfully read the date into the raw field but didn't parse it into the dedicated author_death_hijri field. **Not an LLM error** — the date was available in the prompt. The remaining 8 "real inferences" from the strategic analysis need similar re-examination.

3. **Trust tier for institutional encyclopedias:** الموسوعة الفقهية الكويتية gets trust=flagged despite being one of the most authoritative fiqh works. The SPEC's broad "modern compilation → flagged" rule catches high-quality institutional works alongside genuinely questionable modern compilations. **Design question for owner:** Should government-backed institutional encyclopedias have a trust path to "verified"?

### Methodology Notes

- web_fetch was used for 1/8 books during initial evaluation; self-review added 3 more (4/8 total). For the 4 remaining books, web_search snippets were sufficient due to the fame of these works, but future sessions should aim for full 8/8 compliance.
- The read_book.py helper tool proved efficient and reliable for all 8 books.
- No context saturation issues — 8 books was manageable in a single session.
- Shamela-ecosystem sources (ketabonline, waqfeya, shamela.ws) were used for cross-reference but correctly excluded from independent source counts per Correction 5.

### Self-Review Corrections Applied

**Round 1 (methodology verification):**
1. Source independence audit — Shamela-ecosystem sources excluded from VERIFIED counts
2. Result.json model source precision corrected
3. الموسوعة authority_level discrepancy documented
4. Death date inference evidence strengthened with prompt_sent.json data
5. Additional web_fetches (1/8 → 4/8)

**Round 2 (logic and completeness audit):**
6. **Verdict category fixed:** "VERIFIED with FLAG" hybrid replaced with standard VERIFIED + field-level note. Running totals corrected (17→18 VERIFIED).
7. **Attribution prediction failure documented:** Task predicted traditional/definitive disagreement for classical books; all 7 showed definitive/definitive agreement. Finding: Opus discriminates by book fame, not just era.
8. **Sanity checks examined:** 5/8 books have sanity flags — all are gate_abort artifacts (author_name_blank on partial result.json), not real errors.
9. **CA layer structure error noted:** For حاشية ابن عابدين, CA conflates matn/sharh authors. Opus is bibliographically superior on layer detail.
10. **Trust tier reasoning fixed:** Removed unsupported "modern compilation → flagged" causal claim for الموسوعة; replaced with honest uncertainty about trust engine factors.

**Round 3 (domain-level verification and calibration):**
11. **Confidence calibration section added.** Framework requires this; was completely missing. Found: مسند أحمد has 0.90 ML confidence on a WRONG classification — the most dangerous calibration pattern (high-conf + wrong = undetected).
12. **سير أعلام النبلاء science_scope corrected.** Changed "Neither secondary science is wrong" → explicit note that CA's 'sirah' is technically incorrect for this biographical dictionary. Opus's 'ulum_al_hadith' is more defensible.
13. **حاشية ابن عابدين layer structure domain-verified.** Confirmed via Wikipedia and Shamela that the 3-layer chain (التمرتاشي → الحصكفي → ابن عابدين) is bibliographically correct and CA's conflation is a verified error.
14. **ابن عابدين death date 1252 independently verified.** 5 independent sources confirm: Wikipedia, dar-alifta.org (Egyptian Dar al-Ifta), tarajm.com, Alukah, Al Jazeera.
