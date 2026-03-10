# Phase C Book Selection — 50 Targeted LLM Probes

**Rationale for 50 over 30:** See analysis below. Genre coverage alone requires 18 books. At 30 total, only 12 remain for all other dimensions — multi-layer complexity, author difficulty, trust calibration, disputed attribution, technical edge cases. This forces too much multi-duty per book and prevents isolating failure causes. At 50, each dimension gets enough dedicated probes to diagnose failures. Cost: ~€5–7 (negligible). Review: 10 sessions at 5 books/session.

**Important:** Some of these 50 books may already be in the owner's 2,519 collection. The owner should check each title against his local collection before downloading from shamela.ws. Books already in the collection are preferred (we have Phase A extraction data for them).

---

## GROUP A: 13 Existing Fixtures (re-processed for full result capture)

These are already tested. Re-running captures the full per-model LLM responses, consensus details, and extraction intermediates that Step 0 didn't save.

| # | Book | Fixture | Existing Ground Truth? |
|---|------|---------|----------------------|
| A01 | أخبار أبي القاسم الزجاجي | 01_nahw_simple | ✅ |
| A02 | أبنية الأسماء والأفعال والمصادر | 02_nahw_muhaqiq | ✅ |
| A03 | أحكام الاضطباع والرمل في الطواف | 03_fiqh | ✅ |
| A04 | أحاديث أيوب السختيانى | 04_hadith | ✅ |
| A05 | أنوار الهلالين في التعقبات على الجلالين | 05_tafsir | ✅ |
| A06 | آداب الفتوى والمفتي والمستفتي | 06_usul | ✅ |
| A07 | أساليب بلاغية | 07_balagha | ✅ |
| A08 | آداب الصحبة | 08_death_date | ✅ |
| A09 | أسلوب خطبة الجمعة | 09_alt_title | ✅ |
| A10 | البدر التمام بما صح من أدلة الأحكام | 10_no_author | ✅ |
| A11 | همع الهوامع في شرح جمع الجوامع | 11_multi_small | ✅ |
| A12 | مذكرات مالك بن نبي - العفن | 12_multi_muq | ✅ |
| A13 | ألفية ابن مالك (plain text) | alfiyyah_versified | ✅ |

**These 13 also serve as:**
- Genre coverage: risalah (A03, A06, A09), sharh (A11), nazm (A13), hadith_collection (A04), other (A12)
- Multi-layer: 1 sharh (A11)
- Regression baseline: any ground truth mismatch vs Step 0 = pipeline regression

---

## GROUP B: Genre Coverage Completion (11 books for the 11 missing genres)

Each book is the most prototypical, well-known example of its genre — minimizing ambiguity so genre classification failures clearly indicate a bug, not a gray area.

| # | Genre | Book | Author | Why This Book |
|---|-------|------|--------|---------------|
| B01 | **matn** | متن الأربعين النووية | النووي (ت 676هـ) | The most famous matn in Islamic education. If the pipeline can't identify this as matn, something is fundamentally broken. Also tests: short text, aqidah/hadith overlap in science_scope. |
| B02 | **hashiyah** | حاشية ابن عابدين (رد المحتار على الدر المختار) | ابن عابدين (ت 1252هـ) | The most famous hashiyah in fiqh. Tests: 3-layer detection (matn: Tanwir al-Absar → sharh: al-Durr al-Mukhtar → hashiyah: Radd al-Muhtar). Tests: multi-volume, Hanafi fiqh, late-classical era. |
| B03 | **mukhtasar** | زاد المستقنع في اختصار المقنع | الحجاوي (ت 968هـ) | Classic Hanbali abridgment. Tests: mukhtasar genre, the title literally says "اختصار", very well-known reference. |
| B04 | **taqrirat** | حاشية العطار على شرح الجلال المحلي على جمع الجوامع | العطار (ت 1250هـ) | This is actually a hashiyah that functions as taqrirat — al-Attar's marginal notes on al-Mahalli's sharh of Jam' al-Jawami'. Tests: taqrirat vs hashiyah boundary, usul al-fiqh science, multi-layer (3 layers). **If taqrirat is not available on Shamela, substitute with any taqrirat the owner can find.** |
| B05 | **mawsuah** | الموسوعة الفقهية الكويتية | وزارة الأوقاف والشؤون الإسلامية - الكويت | Institutional/collective authorship — no single author. Tests: author disambiguation when author is an institution, mawsuah genre, very large multi-volume work. |
| B06 | **fatawa** | مجموع فتاوى ابن تيمية | ابن تيمية (ت 728هـ) | Massive fatwa collection (37 volumes). Tests: fatawa genre, multi-volume at extreme scale, very famous classical scholar, compiled posthumously by student (tests compilation vs authorship distinction). |
| B07 | **mujam** | لسان العرب | ابن منظور (ت 711هـ) | The most famous Arabic dictionary. Tests: mujam genre, lugha science, massive multi-volume, distinctive dictionary structure (not prose, not commentary). |
| B08 | **tabaqat** | سير أعلام النبلاء | الذهبي (ت 748هـ) | Premier biographical dictionary. Tests: tabaqat genre, tarikh science overlap, multi-volume, well-known classical scholar. |
| B09 | **fiqh_comparative** | بداية المجتهد ونهاية المقتصد | ابن رشد الحفيد (ت 595هـ) | The classic comparative fiqh text. Tests: fiqh_comparative genre (must not classify as just "fiqh"), author with patronymic disambiguation (Ibn Rushd "al-Hafid" vs his grandfather). |
| B10 | **sirah** | الرحيق المختوم | المباركفوري (ت 1427هـ) | Modern sirah (won competition prize). Tests: sirah genre, modern author, contemporary work with high popularity. |
| B11 | **tarikh** | البداية والنهاية | ابن كثير (ت 774هـ) | The most famous universal history. Tests: tarikh genre (must not classify as tafsir despite same author known for tafsir), massive multi-volume, classical. |

**After Group A + B: all 18 Genre enum values have at least one probe.**

---

## GROUP C: Multi-Layer Complexity Spectrum (4 books)

Group A gives 1 sharh (A11). Group B gives 2 hashiyah/taqrirat (B02, B04). This group adds deeper complexity testing.

| # | Complexity | Book | What It Tests |
|---|-----------|------|---------------|
| C01 | **Sharh with dense matn quotation** | فتح الباري شرح صحيح البخاري (ابن حجر العسقلاني) | The most famous sharh in Islam. Tests: multi-layer detection in sharh where the matn (Sahih al-Bukhari) is quoted extensively. Also tests: 13-volume work, hadith science, extremely well-known author. The LLM should identify both al-Bukhari (matn author) and Ibn Hajar (sharh author). |
| C02 | **Sharh that might confuse as risalah** | شرح الورقات (الجويني / المحلي) | Short sharh on a very short matn (al-Waraqat). Tests: does the pipeline still detect multi-layer when the text is short and the sharh dominates? Edge case: many editions on Shamela attributed to different commentators — tests author disambiguation. |
| C03 | **False positive trap: heavy quotation but NOT multi-layer** | إعلام الموقعين عن رب العالمين (ابن القيم) | Ibn al-Qayyim quotes extensively from Ibn Taymiyyah throughout this work, but it's an ORIGINAL composition, not a sharh. Tests: does the pipeline correctly identify this as NOT multi-layer despite extensive quotation? Genre should be risalah or other, not sharh. |
| C04 | **tahqiq apparatus as pseudo-layer** | أي كتاب بتحقيق عبد السلام هارون أو أحمد شاكر | Any well-known tahqiq where the muhaqiq's footnotes are extensive. Tests: does the pipeline treat muhaqiq footnotes as a text layer, or correctly identify them as editorial apparatus? The muhaqiq is NOT a layer author. |

---

## GROUP D: Disputed Attribution & Author Difficulty (6 books)

These are the highest-value probes in the entire set. Disputed attribution is where the pipeline is most likely to produce wrong answers that become wrong beliefs.

| # | Difficulty | Book | What It Tests |
|---|-----------|------|---------------|
| D01 | **Explicitly disputed on Shamela** | الفقه الأكبر | Shamela metadata itself says "ينسب لأبي حنيفة" (attributed to Abu Hanifa, d. 150). Tests: does the pipeline detect `attribution_status: "disputed"` or `"attributed"`? Does the LLM know this is disputed? Critical: if the pipeline says `definitive` here, it's propagating a contested claim as fact. |
| D02 | **Disputed compilation** | نهج البلاغة | Attributed to Ali ibn Abi Talib (ت 40هـ) but compiled by al-Sharif al-Radi (ت 406هـ). Tests: who does the pipeline identify as author? The attributed speaker (Ali) or the compiler (al-Radi)? Both answers have scholarly support. The pipeline should flag this for human review. Also tests: adab genre, tasawwuf/balagha science overlap. |
| D03 | **Common name author** | Any book by "أحمد بن محمد" without further disambiguation | There are hundreds of scholars named "Ahmad ibn Muhammad." Tests: does the pipeline attempt to disambiguate using death date, science, and other contextual clues, or does it confidently pick the wrong Ahmad? Owner selects a specific example from his collection. |
| D04 | **Author known only by kunyah/laqab** | Book from the 96 missing author_name_raw | From the 96 books that Phase A found with only author_short (e.g., "أبو عبيد" or "النووي" without full name). Tests: can the LLM infer the full nasab name from a kunyah + text sample + science context? |
| D05 | **Another author-short-only book** | Different book from the 96, different science | Second test of author_short-only inference, from a different science/era to test whether success on D04 generalizes. |
| D06 | **Institutional/collective author** | Book by لجنة علمية or مجموعة من العلماء | Tests: how does the pipeline handle authorship when there's no individual author? Should produce a specific institutional identifier, not hallucinate a scholar name. |

---

## GROUP E: Trust Calibration (4 books)

The trust algorithm uses 5 weighted factors (author standing 0.30, tahqiq quality 0.25, publisher 0.15, source authority 0.15, text fidelity 0.15) with threshold 0.65 (verified/flagged). These probes test the boundaries.

| # | Expected Trust | Book | What It Tests |
|---|---------------|------|---------------|
| E01 | **Clearly verified** (should score well above 0.65) | صحيح مسلم بشرح النووي (ط. دار إحياء التراث) | Classical hadith collection + major classical sharh + reputable publisher + excellent tahqiq apparatus. Every trust factor should score high. If this gets flagged, the algorithm is broken. |
| E02 | **Clearly flagged** (should score well below 0.65) | Any modern popular Islamic pamphlet without tahqiq | A small booklet by a contemporary author, printed by a minor publisher, no critical apparatus. Every trust factor should score low except possibly text fidelity. |
| E03 | **Borderline** (should be near 0.65 threshold) | Classical text with mediocre modern tahqiq | A well-known matn or sharh published by a lesser-known publisher with basic tahqiq. High author standing, low tahqiq quality, moderate publisher. Tests: do the weights produce a score near the boundary? |
| E04 | **Surprising case: famous author, poor edition** | Any well-known scholar's work in a known-poor Shamela export | Tests: does high author standing override low text fidelity? The trust algorithm should still flag if the edition quality is bad, even for a major scholar. |

---

## GROUP F: Technical Edge Cases (8 books)

These specifically target known pipeline vulnerabilities and data quality issues found in Phase A.

| # | Edge Case | Book Selection Criteria | What It Tests |
|---|-----------|------------------------|---------------|
| F01 | **Very short juz'** (<10 pages) | One of the 10 "content_minimal" books from Phase A | Pipeline behavior on minimal text. Is the text_sample long enough for meaningful LLM inference? Does confidence correctly drop for sparse data? |
| F02 | **Very large multi-volume** (>10 volumes) | Any work with 10+ volumes (e.g., فتاوى ابن تيمية covers this if B06 is selected) | Already covered by B06/B07/B08 (skip if redundant). If those are <10 volumes, pick a dedicated large work. |
| F03 | **Format B HTML book** | One of the 64 books that triggered Bug 2 (colon-in-label) | Verifies that the Phase A fix works through the full pipeline with LLM. The extraction should produce correct fields that the LLM then infers from. |
| F04 | **Book with رواية field** | One of the 26 books with رواية in extra_card_fields | Tests: does the riwayah field reach the LLM prompt context? Does it affect genre classification (should lean toward hadith_collection)? |
| F05 | **Truncated export** | One of the 32 books with truncation_with_mismatch from Phase A | Tests: pipeline behavior when the text is incomplete. Does quality_issues get set? Does confidence drop appropriately? |
| F06 | **Page count mismatch** | One of the 90 books with page_count_mismatch from Phase A | Tests: does the digital vs physical page count anomaly affect any downstream processing? |
| F07 | **Multiple muhaqiqs listed** | Book where the metadata card lists 2+ muhaqiqs | Tests: does `muhaqiq_name_raw` correctly capture multiple editors? Does scholar registration handle it? |
| F08 | **Book with unusual science scope** | A book spanning multiple sciences (e.g., a tafsir that's also usul al-fiqh) | Tests: science_scope should be a list with 2+ entries. Does the LLM produce multiple science entries when appropriate? |

---

## GROUP G: Consensus Stress Cases (4 books)

These are chosen because the two LLM models (Opus 4.6 and Command A) are likely to DISAGREE, testing the consensus mechanism.

| # | Stress Type | Book Selection Criteria | What It Tests |
|---|-----------|------------------------|---------------|
| G01 | **Obscure work** | A rarely-cited text that neither model likely has strong training data on | When both models are uncertain, do they express low confidence? Does consensus correctly trigger human gate? |
| G02 | **Ambiguous genre boundary** | A text that's arguably both mukhtasar AND risalah, or both sharh AND risalah | When reasonable people disagree on genre, do the models also disagree? Does the pipeline handle disagreement gracefully? |
| G03 | **Aqidah text with school-dependent classification** | A classical aqidah text (e.g., شرح العقيدة الطحاوية or similar) | Different scholarly traditions classify these differently. Tests: do the models give different school_affiliations? How does consensus resolve school-dependent metadata? |
| G04 | **Mixed structural format** | A book that mixes prose sections with verse sections (e.g., adab literature with embedded poetry) | Tests: does structural_format resolve to "mixed"? Do models agree on the mix? |

---

## Summary: Dimension Coverage Matrix

| Dimension | Books Covering It | Minimum Needed | Surplus |
|-----------|------------------|----------------|---------|
| Genre (18 values) | A01-A13 + B01-B11 | 18 | +6 (some fixtures cover genres, leaving spares) |
| Multi-layer variants | A11, B02, B04, C01-C04 | 5 | +2 (including false positive trap) |
| Disputed attribution | D01-D02, D03 | 3 | +3 (D04-D06 cover related author difficulty) |
| Author difficulty spectrum | D03-D06, A10, B05 | 5 | +1 |
| Trust calibration | E01-E04 | 3 | +1 |
| Technical edge cases | F01-F08 | 5 | +3 |
| Consensus stress | G01-G04 | 2 | +2 |
| Era coverage | Pre-500 (D01), 500-900 (B09,C01), 900-1200 (B02,B06), Post-1200 (B10,A12) | 4 eras | covered |
| Sciences | fiqh, hadith, tafsir, nahw, balagha, usul, aqidah, tarikh, sirah, lugha, adab | 8+ | covered |

---

## What the Owner Needs to Do

### Already Resolved (no owner action):
- Group A (13 fixtures): already in the repo
- Group B (well-known books): names are specific enough to find on Shamela

### Owner Decisions Needed:
1. **D03**: Pick a book by "أحمد بن محمد" (or similar extremely common name) from his collection
2. **D04, D05**: Pick 2 books from the 96 that lack author_name_raw — check local Phase A results or I can try to identify them from the audit data
3. **D06**: Pick a book with institutional/collective authorship
4. **E02**: Pick a modern popular Islamic pamphlet (non-scholarly, no tahqiq)
5. **E03, E04**: Pick borderline trust books from his collection
6. **F01**: Pick one of the 10 minimal-content books from Phase A
7. **F03**: Pick one of the 64 Format B books
8. **F04**: Pick one of the 26 رواية books
9. **F05**: Pick one of the 32 truncated exports
10. **F07**: Pick a book with multiple muhaqiqs
11. **G01**: Pick an obscure, rarely-cited text
12. **G02**: Pick a genre-ambiguous text

### Downloads from Shamela.ws (if not in collection):
The owner should check his 2,519 collection for each Group B book. Many well-known works should already be there. Those missing need downloading from shamela.ws.

---

## Final Count

- Group A: 13 (fixture re-runs)
- Group B: 11 (genre completion)
- Group C: 4 (multi-layer)
- Group D: 6 (attribution/author)
- Group E: 4 (trust)
- Group F: 8 (technical edge cases)
- Group G: 4 (consensus stress)

**Total: 50 books**

Overlap: B02 is also a multi-layer test (C-series redundancy). B06 is also an edge case (F02 redundancy). B09 is also an author difficulty test. After deduplication of explicit overlaps, the distinct book count remains 50 because the overlap books serve their primary GROUP purpose while also covering a secondary dimension.

**Expected cost: 50 × €0.10 = ~€5. With retries and fallbacks: ~€7–8.**
**Review sessions: 10 sessions at 5 books/session.**
