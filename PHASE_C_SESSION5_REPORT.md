# Phase C Session 5 Report — Attribution + Trust + Obscure

**Date:** 2026-03-11
**Evaluator:** Claude Chat (Opus 4.6)
**Books evaluated:** 10
**Models:** All 10 use Opus + Command A (no GPT-5.4 in this session)
**Running totals (pre-session):** 34 VERIFIED, 5 PLAUSIBLE, 0 FLAG, 0 ESCALATE (39 books)

## Summary

| # | Book | Status | Verdict | Key finding |
|---|------|--------|---------|-------------|
| 1 | الفقه الأكبر | gate_abort | PLAUSIBLE | Attribution genuinely disputed; Opus "disputed" is correct |
| 2 | الإبانة - ت العصيمي | gate_abort | PLAUSIBLE | Attribution debate is about text integrity, not authorship; death 324 genuine inference CORRECT |
| 3 | الإبانة - ت فوقية | gate_abort | PLAUSIBLE | Same attribution debate; death 324 pass-through; genre differs from ت العصيمي |
| 4 | البيان والتبيين | success | VERIFIED | Straightforward; الجاحظ (ت 255), famous adab masterwork |
| 5 | الورقة النحوية | success | VERIFIED | Author حازم خنفر confirmed as living modern scholar (b. 1970); low conf justified |
| 6 | حديث الضب | gate_abort | PLAUSIBLE | الطبراني (ت 360) correct; 1 page, content_minimal; only Shamela-ecosystem independent |
| 7 | نصيحة لطالب الحق | gate_abort | PLAUSIBLE | المعلمي اليماني (ت 1386) correct; 2 pages, content_minimal |
| 8 | أدب النفوس للآجري | gate_abort | PLAUSIBLE | الآجري (ت 360) correct; truncated 24/271 pages |
| 9 | أحاديث العطار عن شيوخه | gate_abort | VERIFIED | ابن مقسم العطار (ت 354) confirmed by multiple independent biographical sources |
| 10 | الكلام على حديث الإستلقاء | success | VERIFIED | أبو موسى المديني (ت 581) confirmed; obscure but straightforward |

**Session totals:** 4 VERIFIED, 6 PLAUSIBLE, 0 UNVERIFIABLE, 0 FLAG, 0 ESCALATE
**Cumulative totals:** 38 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (49 books)

---

## Per-Book Verdicts

### Book 1: الفقه الأكبر

Book: الفقه الأكبر
Status: gate_abort
Models: opus + command_a
Verdict: PLAUSIBLE

Author: PLAUSIBLE — Pipeline: أبو حنيفة النعمان بن ثابت بن زوطى (Opus) / Verified: أبو حنيفة النعمان (ت 150) is the traditional attribution / Death: 150 (pipeline) vs 150 (verified) / LLM conf: 0.90 (Opus), 0.85 (CA) / Death source: pass-through (embedded in author_raw as "ت 150هـ")
Genre: PLAUSIBLE — Pipeline: Opus=matn (0.90), CA=risalah (0.90) / Expected: risalah/matn / Shamela cat: العقيدة / Agreement: no (matn vs risalah), but both acceptable per framework for short aqidah texts
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: both ['aqidah'] / Expected: aqidah
Attribution: PLAUSIBLE — Opus: disputed / CA: traditional / Investigated: The attribution of الفقه الأكبر to أبو حنيفة is a well-documented scholarly debate. The Shamela extraction itself uses the language "ينسب لأبي حنيفة" (attributed to) and the title_full includes "المنسوبين لأبي حنيفة" (attributed to). Scholars who dispute the attribution include الألباني (who argued it represents his students' views, not a written work by أبو حنيفة himself), محمد أبو زهرة (who noted scholars never agreed on the attribution), and الكشميري. The main isnad goes through أبو مطيع البلخي, who is considered weak by hadith scholars (ابن معين, البخاري, النسائي all weakened him). Counter-position: ابن تيمية, ابن القيم, عبد القاهر البغدادي (d. 429 AH), and ابن النديم all accepted the attribution. Multiple Hanafi scholars have commented on it. / Position: The attribution is genuinely disputed among major scholars. Opus's "disputed" is the most accurate label. CA's "traditional" understates the scholarly disagreement. The extraction's own use of "ينسب" (attributed to) reflects the cautious scholarly position. This does not downgrade the author identification (both correctly point to أبو حنيفة as the attributed author), but the overall verdict is PLAUSIBLE because the attribution field reflects genuine uncertainty.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: clean; extraction language "ينسب" is itself evidence of the attribution debate
Result.json model source: N/A (gate_abort)
Web Sources: islamqa.info/ar/answers/490331 (independent, fetched), islamweb.net/ar/fatwa/62923 (independent), ar.wikipedia.org/wiki/الفقه_الأكبر (independent), shamela.ws (Shamela-ecosystem)
Notes: Gate_abort reason is author-science mismatch (registry has "primary", no overlap with aqidah). Both models correctly identify أبو حنيفة; the disagreement is only on genre (matn vs risalah) and attribution (disputed vs traditional). Authority_level: both say "primary" — no disagreement for this book.

### Book 2: الإبانة عن أصول الديانة - ت العصيمي

Book: الإبانة عن أصول الديانة - ت العصيمي
Status: gate_abort
Models: opus + command_a
Verdict: PLAUSIBLE

Author: VERIFIED — Pipeline: أبو الحسن علي بن إسماعيل الأشعري / Verified: الأشعري (ت 324هـ) / Death: 324 (pipeline) vs 324 (verified — al-Ash'ari's death in 324 AH is well-established) / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: **GENUINE INFERENCE** — extraction has author_death=N/A and author_name_raw contains NO embedded death date. Both models inferred 324 independently. This is CORRECT.
Genre: PLAUSIBLE — Pipeline: Opus=risalah (0.82), CA=risalah (0.90) / Expected: risalah / Shamela cat: العقيدة / Agreement: yes (both risalah). Note: ت فوقية edition has genre=matn for the SAME text — cross-edition genre inconsistency documented below.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: both ['aqidah'] / Expected: aqidah
Attribution: PLAUSIBLE — Opus: disputed / CA: definitive / Investigated: The الإبانة's attribution debate is different from الفقه الأكبر. The basic authorship attribution to الأشعري is well-established and supported by multiple scholars across centuries: البيهقي, الصابوني, ابن عساكر (who quotes from it extensively in تبيين كذب المفتري), ابن تيمية, ابن القيم, and even الأهوازي (a critic of الأشعري who did not deny the attribution). Multiple manuscript traditions (5+ copies) agree. The dispute centers on TEXT INTEGRITY — whether the surviving editions faithfully represent what الأشعري originally wrote. Later Ash'ari scholars (particularly الكوثري and وهبي غاوجي) argued that passages were interpolated by later copyists, because the book's theological positions differ from what later Ash'ari school adopted. The فوقية edition manuscript is specifically noted as having variants from other manuscripts. / Position: The basic authorship attribution is well-established (closer to "definitive"). The genuine scholarly debate concerns textual integrity, not authorship. CA's "definitive" is more accurate for the "who wrote this" question. Opus's "disputed" captures a real phenomenon (the text integrity debate) but applies the wrong attribution category — the book IS by الأشعري, the question is whether all passages in surviving editions are authentic. Overall PLAUSIBLE because the attribution field requires nuance that neither model fully captures.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: clean; muhaqiq present (صالح بن مقبل بن عبد الله العصيمي التميمي)
Result.json model source: N/A (gate_abort)
Web Sources: islamqa.info/ar/answers/154936 (independent), salafcenter.org/6864 (independent), ar.wikipedia.org/wiki/الإبانة_عن_أصول_الديانة (independent), alukah.net/culture/0/138053 (independent)
Notes: Death date 324 is a GENUINE INFERENCE — one of the last remaining test cases from the strategic analysis. Both models inferred it correctly with high confidence (0.97/0.95). This is the 2nd confirmed correct genuine inference (after مجموع الفتاوى 728). Running total: 2 correct, 1 wrong, 4 false positives.

### Book 3: الإبانة عن أصول الديانة - ت فوقية

Book: الإبانة عن أصول الديانة - ت فوقية
Status: gate_abort
Models: opus + command_a
Verdict: PLAUSIBLE

Author: VERIFIED — Pipeline: أبو الحسن علي بن إسماعيل بن إسحاق بن سالم بن إسماعيل بن عبد الله بن موسى بن أبي بردة بن أبي موسى الأشعري (full nasab preserved) / Verified: same scholar as ت العصيمي — الأشعري (ت 324) / Death: 324 (pipeline) vs 324 (verified) / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through (embedded in author_name_raw as "ت 324هـ")
Genre: PLAUSIBLE — Pipeline: Opus=matn (0.90), CA=matn (0.95) / Expected: risalah (framework) / Shamela cat: العقيدة / Agreement: yes (both matn). NOTE: ت العصيمي has genre=risalah while ت فوقية has genre=matn — the SAME text classified differently across editions. Both are acceptable for a short standalone aqidah text. The difference may reflect content scope: ت فوقية has 246 pages vs ت العصيمي's 674, but the genre label should reflect the genre of the original work, not the edition size.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: both ['aqidah'] / Expected: aqidah
Attribution: PLAUSIBLE — Opus: disputed / CA: definitive / Investigated: Same debate as ت العصيمي — see Book 2 investigation above. The فوقية edition is specifically mentioned in scholarly discussions as having manuscript variants from other traditions. الأشعري's authorship is well-established; text integrity is debated. / Position: Same as Book 2 — CA's "definitive" is more accurate for authorship, but the text integrity debate is real. Note that the فوقية manuscript has known variants, which is relevant to the pipeline's handling of different editions.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: clean; muhaqiq present (د. فوقية حسين محمود); full nasab in author_name_raw
Result.json model source: N/A (gate_abort)
Web Sources: same sources as Book 2 (الإبانة research applies to both editions)
Notes: Cross-edition check with ت العصيمي: Author=consistent (الأشعري ✓), Death=consistent (324 ✓), Attribution=consistent (Opus=disputed, CA=definitive for both ✓), Science=consistent (aqidah ✓), ML=consistent (false ✓). Genre INCONSISTENT: ت العصيمي=risalah, ت فوقية=matn — noted but not flagged (both acceptable per framework).

### Book 4: البيان والتبيين

Book: البيان والتبيين
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: عمرو بن بحر بن محبوب الكناني بالولاء، الليثي، أبو عثمان، الشهير بالجاحظ / Verified: الجاحظ (ت 255هـ), one of the most famous classical Arabic prose writers / Death: 255 (pipeline) vs 255 (verified) / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (embedded in author_raw as "ت 255هـ")
Genre: VERIFIED — Pipeline: adab (result.json) / Expected: adab/other / Shamela cat: الأدب / Agreement: yes (both adab). ابن خلدون listed it as one of the 4 pillars of Arabic adab literature.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline (result.json): ['adab', 'lughah'] / Expected: adab / Opus superset: ['adab', 'balagha', 'lughah']. Primary science correct. The book genuinely covers rhetoric/balagha alongside adab.
Attribution: VERIFIED — Both models: definitive. No dispute.
Trust: VERIFIED — Pipeline: trust_tier=verified, trust_score=0.6925
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: clean; no quality issues
Result.json model source: CA values (genre=adab, science=['adab', 'lughah'], attribution=definitive)
Web Sources: ar.wikipedia.org/wiki/البيان_والتبيين (independent), hindawi.org (independent), archive.org (independent), goodreads.com (independent), shamela.ws (Shamela-ecosystem)
Notes: Straightforward. One of the most famous books in Arabic literature. Zero concerns.

### Book 5: الورقة النحوية

Book: الورقة النحوية
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: حازم خنفر / Verified: أبو البهاء، حازم أحمد حسني خنفر, modern Jordanian scholar, born 23/11/1970 in Kuwait. Active author with numerous publications on Shamela, archive.org, noor-book.com, ketabpedia.com. The الورقة النحوية is a 1-page grammar summary published in 2022, derived from his متن البرعومة في النحو. / Death: null (pipeline) vs null (correct — he is alive) / LLM conf: 0.55 (Opus), 0.70 (CA) / Death source: absent (correct — no death date for a living author)
Genre: PLAUSIBLE — Pipeline (result.json): risalah / Opus: matn (0.90), CA: risalah (0.90) / Expected: risalah/matn / Shamela cat: النحو والصرف / Agreement: no (matn vs risalah). Result.json carries CA's risalah. For a 1-page grammar summary, "matn" (concise foundational text) is arguably more precise, but risalah is acceptable.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: ['nahw', 'sarf'] / Expected: nahw. The book covers both nahw (syntax) and sarf (morphology) — pipeline superset is accurate.
Attribution: VERIFIED — Both models: definitive.
Trust: PLAUSIBLE — Pipeline: trust_tier=flagged, trust_score=0.4325. The "flagged" tier is appropriate — this is a modern author with a very short text (2 pages) and low author confidence. The mechanism for flagged status aligns with the quality signals.
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: content_minimal (only 2 content pages); no muhaqiq, no publisher, no edition info
Result.json model source: CA values (genre=risalah, science=['nahw', 'sarf'], attribution=definitive, level=beginner)
Web Sources: shamela.ws/author/2315 (Shamela-ecosystem — includes full biography), lisanarb.com (independent), noor-book.com (independent), archive.org (independent), ketabpedia.com (Shamela-ecosystem)
Notes: This was the lowest-confidence author in the entire corpus (Opus 0.55, CA 0.70). The low confidence is WELL-CALIBRATED — this is a modern author with limited general online presence (no Wikipedia article, no academic institution page), though he has multiple published works. The pipeline correctly identified him despite the low confidence. Authority_level: both say modern_compilation (no disagreement). Reasonable characterization of a 2022 1-page grammar summary.

### Book 6: حديث الضب الذي تكلم بين يدي النبي للطبراني

Book: حديث الضب الذي تكلم بين يدي النبي للطبراني
Status: gate_abort
Models: opus + command_a
Verdict: PLAUSIBLE

Author: VERIFIED — Pipeline: سليمان بن أحمد بن أيوب بن مطير اللخمي الشامي، أبو القاسم الطبراني / Verified: الطبراني (260-360 هـ), one of the most prolific hadith collectors / Death: 360 (pipeline) vs 360 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (embedded in author_raw as "ت 360هـ")
Genre: VERIFIED — Pipeline: hadith_collection (both agree, Opus 0.85, CA 0.95) / Expected: hadith_collection / Shamela cat: كتب السنة / Agreement: yes
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: both ['hadith'] / Expected: hadith
Attribution: PLAUSIBLE — Opus: traditional / CA: definitive / This follows the standard Opus=traditional vs CA=definitive pattern for conventionally-attributed works. Not a genuine dispute. Opus's "traditional" is reasonable for a specific juz' (part) — such small hadith collections are traditionally attributed to their narrators but rarely undergo the same scrutiny as major works.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: content_minimal (only 1 content page); muhaqiq present (عبد الله ضيف الله العامري)
Result.json model source: N/A (gate_abort)
Web Sources: shamela.ws (Shamela-ecosystem). الطبراني is universally known; the specific juz' is too obscure for independent scholarly commentary.
Notes: Overall verdict is PLAUSIBLE (not VERIFIED) because: (a) only Shamela-ecosystem sources found for this specific juz', (b) 1-page content makes all classification data minimally supported. The author identification is solid (الطبراني is one of the most famous hadith scholars), but the specific work is too obscure for independent verification beyond Shamela.

---

**MID-SESSION QUALITY GATE (after Book 6):**
- web_fetch: 1/6 (islamqa.info for الفقه الأكبر). Below target but search snippets have been rich.
- Both models checked for all 6 books: yes
- Death source (pass-through/inferred) marked for all 6: yes
- Verdict format complete: yes
- No drift detected. Continuing.

---

### Book 7: نصيحة لطالب الحق - ضمن «آثار المعلمي»

Book: نصيحة لطالب الحق - ضمن «آثار المعلمي»
Status: gate_abort
Models: opus + command_a
Verdict: PLAUSIBLE

Author: VERIFIED — Pipeline: عبد الرحمن بن يحيى المعلمي اليماني / Verified: المعلمي اليماني (1313-1386 هـ), well-known muhaddith and textual critic / Death: 1386 (pipeline) vs 1386 (verified) / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through (embedded in author_raw as "1313 - 1386 هـ")
Genre: VERIFIED — Pipeline: risalah (both agree, 0.90) / Expected: risalah/other / Shamela cat: كتب عامة / Agreement: yes
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: PLAUSIBLE — Opus: ['ulum_al_hadith', 'usul_al_fiqh'] / CA: ['usul_al_fiqh', 'aqidah'] / The title "نصيحة لطالب الحق" suggests methodological advice — المعلمي is famous for hadith criticism methodology. Opus's ulum_al_hadith is plausible given المعلمي's expertise. CA's aqidah is less precise for this specific work. Without reading the full 2-page text, PLAUSIBLE.
Attribution: VERIFIED — Both models: definitive. Part of آثار المعلمي compilation.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: content_minimal (only 2 content pages); muhaqiq present (محمد أجمل الإصلاحي)
Result.json model source: N/A (gate_abort)
Web Sources: shamela.ws (Shamela-ecosystem). المعلمي is well-known in hadith circles but this specific 2-page risalah is too short for independent reviews.
Notes: PLAUSIBLE because only Shamela-ecosystem sources for this specific risalah. The author is well-known but the specific work is a minor 2-page extract from a larger compilation.

### Book 8: أدب النفوس للآجري

Book: أدب النفوس للآجري
Status: gate_abort
Models: opus + command_a
Verdict: PLAUSIBLE

Author: VERIFIED — Pipeline: أبو بكر محمد بن الحسين بن عبد الله الآجُرِّيّ البغدادي / Verified: الآجري (ت 360هـ), well-known muhaddith and author of كتاب الشريعة / Death: 360 (pipeline) vs 360 (verified) / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through (embedded in author_raw as "ت 360هـ")
Genre: PLAUSIBLE — Pipeline: risalah (both agree, Opus 0.88, CA 0.95) / Expected: risalah/other / Shamela cat: كتب السنة / Agreement: yes (both risalah). Title_full is "مجموعة أجزاء حديثية - أدب النفوس" — the "مجموعة أجزاء حديثية" framing suggests this is a hadith compilation containing the أدب النفوس section. "risalah" captures the individual work's genre.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: PLAUSIBLE — Opus: ['tasawwuf', 'aqidah'] / CA: ['tasawwuf', 'adab'] / Disagreement on secondary science. "أدب النفوس" (discipline of souls) overlaps tasawwuf, adab, and aqidah. Primary science (tasawwuf) agreed. Neither is wrong.
Attribution: PLAUSIBLE — Opus: traditional / CA: definitive. Standard pattern. Not a genuine dispute.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: page_count_mismatch warning — digital pages (24) are 9% of claimed physical pages (271). This is a significantly truncated export. The LLM saw only 24 pages of a 271-page work.
Result.json model source: N/A (gate_abort)
Web Sources: shamela.ws (Shamela-ecosystem). الآجري is known but this specific work within "مجموعة أجزاء حديثية" is not independently reviewed.
Notes: PLAUSIBLE because: (a) only Shamela-ecosystem sources for this specific work, (b) severely truncated (9% of content) — genre and science classification based on partial data. The truncation means the LLM classified based on a fragment.

### Book 9: أحاديث العطار عن شيوخه

Book: أحاديث العطار عن شيوخه
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: محمد بن الحسن بن يعقوب بن الحسن بن مِقْسَم العطار, أبو بكر / Verified: ابن مقسم العطار (265-354 هـ), a well-documented Baghdadi scholar of Qur'anic recitations and Arabic grammar. Described by الذهبي as "العلامة المقرئ" and by أبو عمرو الداني as "مشهور بالضبط والإتقان". Multiple independent biographical sources confirm: shamela.ws/author/1611, tarajm.com/people/33538, taraajem.com/persons/9890 (encyclopedic biographical database), hadithtransmitters.hawramani.com (hadith transmitter encyclopedia), tulayhah.wordpress.com (English translation of الذهبي's entry). / Death: 354 (pipeline) vs 354 (verified — multiple sources confirm: ربيع الآخر سنة 354 هـ) / LLM conf: 0.92 (Opus), 0.90 (CA) / Death source: pass-through (embedded in author_raw as "ت 354هـ")
Genre: VERIFIED — Pipeline: hadith_collection (both agree, 0.95) / Expected: hadith_collection / Shamela cat: كتب السنة / Agreement: yes. Title_full confirms: "الجزء فيه من حديث أبي بكر محمد بن الحسن بن يعقوب بن مقسم العطار عن شيوخه"
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: PLAUSIBLE — Opus: ['hadith', 'ulum_al_hadith'] / CA: ['hadith'] / Primary science correct. Opus adds ulum_al_hadith — this is a hadith juz' with isnad chains, so the superset is reasonable.
Attribution: VERIFIED — Both models: traditional. Consistent with a conventionally-attributed hadith juz'.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: TWO quality warnings — page_count_mismatch (10 of 279 pages, 4%) AND truncation_with_mismatch (last page ends without sentence-ending punctuation). Severely truncated.
Result.json model source: N/A (gate_abort)
Web Sources: shamela.ws/author/1611 (Shamela-ecosystem), tarajm.com (independent biographical database), taraajem.com (independent encyclopedic source), hadithtransmitters.hawramani.com (independent hadith transmitter database)
Notes: VERIFY-author book — both models agreed on ابن مقسم العطار and both were CORRECT. Independent verification from multiple biographical databases confirms identity and death date. Despite severe truncation (4% of content), the author identification is solid because the full title in the extraction names the author explicitly. The truncation affects genre/science reliability but not author identification.

### Book 10: الكلام على حديث الإستلقاء لأبي موسى المديني

Book: الكلام على حديث الإستلقاء لأبي موسى المديني
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: محمد بن عمر بن أحمد بن عمر بن محمد الأصبهاني المديني، أبو موسى / Verified: أبو موسى المديني (501-581 هـ), described by الذهبي as "الإمام العلامة، الحافظ الكبير، الثقة، شيخ المحدثين". From أصبهان. Multiple independent sources confirm. / Death: 581 (pipeline) vs 581 (verified) / LLM conf: 0.92 (Opus), 0.95 (CA) / Death source: pass-through (embedded in author_raw as "ت 581هـ")
Genre: VERIFIED — Pipeline (result.json): risalah / Expected: risalah/hadith / Shamela cat: كتب السنة / Agreement: yes (both risalah). A short hadith commentary — risalah is appropriate.
Multi-Layer: VERIFIED — Pipeline: false / Expected: false / Model agreement: yes
Science: VERIFIED — Pipeline: ['hadith', 'ulum_al_hadith'] / Expected: hadith. Both models agree. Appropriate for a hadith commentary.
Attribution: PLAUSIBLE — Opus: traditional / CA: definitive / Result.json: traditional (Opus value carried for success book — this is notable). Standard Opus=traditional vs CA=definitive pattern.
Trust: VERIFIED — Pipeline: trust_tier=verified, trust_score=0.6925
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: content_minimal (only 2 content pages); marked as مخطوط (manuscript)
Result.json model source: For this success book, result.json carries Opus values for attribution (traditional, not CA's definitive). Genre=risalah matches both models. Science=['hadith', 'ulum_al_hadith'] matches Opus.
Web Sources: ar.wikipedia.org/wiki/أبو_موسى_المديني (independent), shamela.ws/author/1292 (Shamela-ecosystem, includes this specific book), islamweb.net سير أعلام النبلاء (independent), dorar.net (independent), tarajm.com (independent)
Notes: Obscure work but straightforward evaluation. أبو موسى المديني is well-documented despite being less famous than scholars like الطبراني or الآجري. The title explicitly names him, and the extraction title_full says "مخطوط" (manuscript) — interesting metadata preserved through the pipeline.

---

## Consistency Self-Check (separate pass)

1. **Same standards applied to book 1 and book 10?** Yes. PLAUSIBLE threshold applied consistently: books with only Shamela-ecosystem sources or genuinely disputed attribution = PLAUSIBLE; books with 2+ genuinely independent sources = VERIFIED.

2. **Source independence counts honest?**
   - Books 1-3 (disputed attribution): Multiple independent sources (islamqa.info, alukah.net, salafcenter.org, Wikipedia Arabic) → but verdict PLAUSIBLE due to attribution uncertainty, not source count.
   - Book 4 (البيان والتبيين): Wikipedia, Hindawi, archive.org, Goodreads → VERIFIED ✓
   - Book 5 (الورقة): noor-book.com + archive.org (independent) + Shamela author page → VERIFIED ✓
   - Book 6 (حديث الضب): Only Shamela-ecosystem for the specific juz' → PLAUSIBLE ✓
   - Book 7 (نصيحة): Only Shamela-ecosystem for the specific risalah → PLAUSIBLE ✓
   - Book 8 (أدب النفوس): Only Shamela-ecosystem for the specific work → PLAUSIBLE ✓
   - Book 9 (أحاديث العطار): tarajm.com + taraajem.com + hawramani.com (all independent) → VERIFIED ✓
   - Book 10 (الكلام): Wikipedia + islamweb.net + dorar.net + tarajm.com (independent) → VERIFIED ✓

3. **Shamela-ecosystem excluded everywhere?** Yes. shamela.ws, ketabonline.com counted as ecosystem throughout.

4. **Success books checked for trust + model source?** Books 4 (trust=verified ✓), 5 (trust=flagged ✓), 10 (trust=verified ✓). Model source checked for all 3.

5. **Attribution investigated (not just noted) for all 3 disputed books?** Yes. Books 1, 2, 3 all have detailed investigation with scholarly positions identified, sources cited, and positions taken.

---

## Confidence Calibration

| Book | Author (Opus) | Author (CA) | Genre (Opus) | Genre (CA) | Correct? |
|------|---------------|-------------|--------------|------------|----------|
| الفقه الأكبر | 0.90 | 0.85 | 0.90 | 0.90 | Author ✓, Genre acceptable |
| الإبانة ت العصيمي | 0.97 | 0.95 | 0.82 | 0.90 | All ✓ |
| الإبانة ت فوقية | 0.97 | 0.95 | 0.90 | 0.95 | All ✓ |
| البيان والتبيين | 0.99 | 1.00 | 0.95 | 1.00 | All ✓ |
| الورقة النحوية | **0.55** | **0.70** | 0.90 | 0.90 | All ✓ |
| حديث الضب | 0.99 | 0.95 | 0.85 | 0.95 | All ✓ |
| نصيحة لطالب الحق | 0.97 | 0.95 | 0.90 | 0.90 | All ✓ |
| أدب النفوس | 0.97 | 0.95 | 0.88 | 0.95 | All ✓ |
| أحاديث العطار | 0.92 | 0.90 | 0.95 | 0.95 | All ✓ |
| الكلام على حديث | 0.92 | 0.95 | 0.85 | 0.90 | All ✓ |

**Key finding: Zero author identification errors in Session 5.** Running total: 0 errors in 49 books evaluated. The pipeline's author identification remains the strongest field.

**High-confidence + wrong:** No new cases in Session 5. Cumulative: 2 ML cases (0.85-0.90), 1 genre case (0.82) from Sessions 2-4. Session 5 has no ML=true books.

**Low-confidence calibration:** الورقة النحوية (0.55/0.70) was the lowest-confidence author in the entire corpus. This is WELL-CALIBRATED: the author is a modern scholar with limited general web presence (no Wikipedia, no academic institution page), living (no death date), with a very short text (2 pages). The low confidence correctly reflects genuine uncertainty — both models identified him correctly, but honestly signaled that they were less sure. This is exactly what good calibration looks like.

**Death date genuine inference update:**
- الإبانة ت العصيمي: death=324, GENUINE INFERENCE (no death date in extraction, no embedded date in author_name_raw). Verified CORRECT.
- Updated running total: 2 correct (728, 324), 1 wrong (1432 vs 1439), 4 false positives. Accuracy on genuine inferences: 2/3 (67%).

---

## Cross-Book Patterns

### الإبانة editions consistency check
| Field | ت العصيمي | ت فوقية | Consistent? |
|-------|-----------|---------|-------------|
| Author | الأشعري | الأشعري | ✓ |
| Death | 324 (inferred) | 324 (pass-through) | ✓ |
| Attribution (Opus) | disputed | disputed | ✓ |
| Attribution (CA) | definitive | definitive | ✓ |
| Science | aqidah | aqidah | ✓ |
| ML | false | false | ✓ |
| Genre (Opus) | risalah (0.82) | matn (0.90) | ✗ |
| Genre (CA) | risalah (0.90) | matn (0.95) | ✗ |

Genre inconsistency across editions: the same text gets risalah in one edition and matn in the other. Both labels are defensible for a short standalone aqidah text. The inconsistency likely arises from: (a) different edition framing (العصيمي edition has 674 pages vs فوقية's 246), (b) different prompt context (العصيمي has muhaqiq name in prompt, فوقية has full nasab). This is not an error per se, but a calibration observation — the genre boundary between risalah and matn is fuzzy for this type of text.

### Attribution pattern: Session 5 vs Sessions 3-4 taxonomy
Session 5 introduces the first genuinely disputed attributions to the evaluation. The Opus attribution taxonomy from Sessions 3-4 holds:
- **definitive** (both agree): البيان والتبيين, الورقة النحوية, نصيحة لطالب الحق
- **traditional** (both agree): أحاديث العطار
- **traditional** (Opus) vs **definitive** (CA): حديث الضب, أدب النفوس, الكلام على حديث — standard Opus→CA escalation pattern
- **disputed** (Opus) vs traditional/definitive (CA): الفقه الأكبر, الإبانة ×2 — genuinely contested works

The 3 "disputed" books all have documented scholarly debates. Opus's use of "disputed" demonstrates genuine domain knowledge about Islamic attribution controversies. CA's tendency to override to "definitive" or "traditional" is less nuanced for these cases.

### Obscure vs famous: confidence discrimination
| Category | Books | Avg Opus author conf | Avg CA author conf |
|----------|-------|---------------------|-------------------|
| Famous | البيان والتبيين, الفقه الأكبر, الإبانة ×2 | 0.96 | 0.94 |
| Known classical | الطبراني, الآجري, المعلمي, المديني | 0.96 | 0.95 |
| Obscure | أحاديث العطار, الورقة النحوية | 0.74 | 0.80 |

Confidence scores appropriately discriminate between famous/known scholars (0.94+) and obscure/modern authors (0.55-0.92). This is good calibration.

### Attribution disagreement distribution
6/10 books have Opus vs CA attribution disagreements. This is the highest concentration in any session:
- 3 genuine disputes: الفقه الأكبر (disputed vs traditional), الإبانة ×2 (disputed vs definitive)
- 3 standard pattern: حديث الضب, أدب النفوس, الكلام (traditional vs definitive)

The standard pattern (Opus=traditional, CA=definitive) is now confirmed across 9+ books in Sessions 3-5. It represents a systematic calibration difference, not per-book errors.

### Authority_level disagreements
0/10 books have authority_level disagreements in Session 5. All books agree: 9/10 say "primary" (both models), 1/10 (الورقة النحوية) says "modern_compilation" (both models). This contrasts with Session 4's 6/10 disagreement rate, where Opus labeled sharh works as "reference" while CA said "primary." Session 5 has no sharh works, which explains the absence of disagreements.

---

## Strategic Prediction Validation

| Prediction (from strategic analysis) | Result |
|--------------------------------------|--------|
| Session 5 difficulty: HIGH | ✅ **Confirmed** — 6/10 PLAUSIBLE (highest PLAUSIBLE rate in any session) |
| الفقه الأكبر attribution is genuinely disputed | ✅ **Confirmed** — multiple major scholars on both sides |
| الإبانة text authenticity debated | ✅ **Confirmed** — though the debate is about text integrity, not basic authorship |
| الورقة النحوية author unfindable | ✗ **Wrong** — author is findable with multiple sources; low confidence was well-calibrated |
| Death date 324 genuine inference for الإبانة ت العصيمي | ✅ **Confirmed** correct |

Net prediction accuracy: 4/5 confirmed, 1/5 incorrect. The strategic analysis correctly predicted the session difficulty and the attribution debates. The الورقة prediction was too pessimistic — the author exists online, just not on Wikipedia.

---

## Findings & Recommendations

### Positive Findings
1. **Zero author errors in 49 books.** This remains the strongest pipeline field.
2. **Opus's attribution taxonomy shows genuine domain knowledge.** The "disputed" label was correctly applied to الفقه الأكبر (a famous scholarly debate) and الإبانة (where a text integrity debate exists).
3. **Death date genuine inference correct (324 for الأشعري).** Running total: 2/3 correct on genuine inferences.
4. **Low-confidence calibration excellent.** الورقة النحوية (0.55) correctly flagged a genuinely hard case, but the identification was correct.
5. **VERIFY-author protocol validated.** Both VERIFY-author books (الورقة النحوية, أحاديث العطار) were independently confirmed correct.

### Issues Found
1. **Cross-edition genre inconsistency (الإبانة).** Same text classified as risalah in one edition and matn in another. Both labels are defensible but the inconsistency reveals a fuzzy boundary in the genre taxonomy for short standalone aqidah texts.
2. **Attribution field lacks nuance for الإبانة.** The debate is about text integrity (whether surviving editions are altered), not authorship. Neither "disputed" (Opus) nor "definitive" (CA) fully captures this. The attribution enum may need a finer-grained category for "authorship accepted, text integrity debated."
3. **Result.json model source inconsistency (Book 10).** الكلام على حديث is a success book where result.json carries attribution=traditional (Opus value), not CA's definitive. The model-selection mechanism for populating result.json fields is not fully transparent.

### Methodology Notes
- Mid-session quality gate at Book 6 detected no drift.
- web_fetch compliance: 1/10 books (islamqa.info for الفقه الأكبر). Search snippets were sufficient for the remaining books, but the protocol target was higher.
- Attribution investigation protocol executed for all 3 disputed books with scholarly sources identified and positions taken.
- VERIFY-author protocol executed for both VERIFY books with independent biographical sources.
