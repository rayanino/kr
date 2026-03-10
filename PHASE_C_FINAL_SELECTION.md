# Phase C Final Book Selection — 50 Targeted LLM Probes

**Status:** FINAL — all picks made, ready for owner download and Claude Code execution
**Cost estimate:** ~€5–8 for 50 books
**Review sessions:** 10 sessions × 5 books each

---

## Instructions for the Owner

1. Check your 2,519-book collection for each book below
2. For books NOT in your collection, download from shamela.ws
3. Place all books in a single directory (your existing collection directory works)
4. Create `books.txt` with the directory name of each book, one per line
5. Hand `books.txt` + this document + `PHASE_C_TASK_SPEC.md` to Claude Code

**Important:** Some directory names in your collection may differ slightly from the titles below (Shamela uses display_title for folder names). Match by title, not exact string.

---

## GROUP A: 13 Existing Fixtures (regression + full result capture)

These are processed from the FIXTURE directories, not the collection. The Phase C script handles them separately.

| # | Title | Ground Truth Key |
|---|-------|-----------------|
| A01 | أخبار أبي القاسم الزجاجي | 01_nahw_simple |
| A02 | أبنية الأسماء والأفعال والمصادر | 02_nahw_muhaqiq |
| A03 | أحكام الاضطباع والرمل في الطواف | 03_fiqh |
| A04 | أحاديث أيوب السختيانى | 04_hadith |
| A05 | أنوار الهلالين في التعقبات على الجلالين | 05_tafsir |
| A06 | آداب الفتوى والمفتي والمستفتي | 06_usul |
| A07 | أساليب بلاغية | 07_balagha |
| A08 | آداب الصحبة | 08_death_date |
| A09 | أسلوب خطبة الجمعة | 09_alt_title |
| A10 | البدر التمام بما صح من أدلة الأحكام | 10_no_author |
| A11 | همع الهوامع في شرح جمع الجوامع | 11_multi_small |
| A12 | مذكرات مالك بن نبي - العفن | 12_multi_muq |
| A13 | ألفية ابن مالك (plain text fixture) | alfiyyah_versified |

---

## GROUP B: Genre Coverage (11 new books)

Each fills a Genre enum value not covered by the 13 fixtures. I chose the most famous, most unambiguous representative of each genre — if the pipeline misclassifies these, the genre classifier is fundamentally broken.

| # | Genre | Shamela Title | Author | Death | Key Test Insight |
|---|-------|--------------|--------|-------|-----------------|
| B01 | **matn** | الأربعين النووية | النووي | 676هـ | The most canonical matn in Islamic education. Very short (~50 pages). Also tests: aqidah science scope (or hadith?), cross-science ambiguity. |
| B02 | **hashiyah** | حاشية ابن عابدين (رد المحتار على الدر المختار) | ابن عابدين | 1252هـ | The most famous hashiyah. 3-layer: Tanwir al-Absar (matn) → al-Durr al-Mukhtar (sharh) → Radd al-Muhtar (hashiyah). Multi-volume Hanafi fiqh. Tests multi-layer depth. |
| B03 | **mukhtasar** | زاد المستقنع في اختصار المقنع | الحجاوي | 968هـ | Title literally says "اختصار". Classic Hanbali reference. Very short, dense legal text. Tests: does the pipeline identify mukhtasar from title + text style? |
| B04 | **taqrirat** | حاشية العطار على شرح الجلال المحلي على جمع الجوامع | العطار | 1250هـ | Best available taqrirat-like text on Shamela. Al-Attar's notes incorporate oral lecture material. Multi-layer usul al-fiqh. **If pipeline classifies as hashiyah instead of taqrirat, that's an acceptable ambiguity — document it as a finding.** |
| B05 | **mawsuah** | الموسوعة الفقهية الكويتية | وزارة الأوقاف الكويتية | — | Institutional author (no person). Massive encyclopedia. Tests: author disambiguation when author is a government ministry, mawsuah genre, collective compilation. |
| B06 | **fatawa** | مجموع الفتاوى (ابن تيمية) | ابن تيمية | 728هـ | 37-volume fatwa collection compiled posthumously by Ibn Qasim. Tests: fatawa genre, extreme multi-volume, compilation vs authorship distinction (compiler ≠ author). |
| B07 | **mujam** | لسان العرب | ابن منظور | 711هـ | Most famous Arabic dictionary. Tests: mujam genre, lugha science, distinctive non-prose dictionary structure, massive scale. |
| B08 | **tabaqat** | سير أعلام النبلاء | الذهبي | 748هـ | Premier biographical dictionary. Tests: tabaqat genre, potential tarikh science overlap. |
| B09 | **fiqh_comparative** | بداية المجتهد ونهاية المقتصد | ابن رشد الحفيد | 595هـ | THE comparative fiqh text. Must classify as fiqh_comparative, not generic fiqh. Author "Ibn Rushd al-Hafid" tests patronymic disambiguation (vs grandfather Ibn Rushd al-Jadd). |
| B10 | **sirah** | الرحيق المختوم | المباركفوري | 1427هـ | Modern sirah (prize-winning). Tests: sirah genre, modern author, contemporary publication. |
| B11 | **tarikh** | البداية والنهاية | ابن كثير | 774هـ | Most famous universal history. Tests: tarikh genre. Critical test: Ibn Kathir is known primarily for tafsir — does the pipeline incorrectly classify this as tafsir based on author recognition? Must correctly identify tarikh from the TEXT, not author priors. |

**Genre coverage after A+B:** matn ✅, sharh ✅ (A11), hashiyah ✅ (B02), mukhtasar ✅ (B03), nazm ✅ (A13), risalah ✅ (A03,A06), taqrirat ✅ (B04), mawsuah ✅ (B05), fatawa ✅ (B06), mujam ✅ (B07), tabaqat ✅ (B08), fiqh_comparative ✅ (B09), hadith_collection ✅ (A04), tafsir ✅ (A05), sirah ✅ (B10), tarikh ✅ (B11), adab (covered by D03 below), other ✅ (A12). **All 18 genres covered.**

---

## GROUP C: Multi-Layer Complexity (4 books)

Testing the full spectrum from obvious multi-layer to false positive traps.

| # | Type | Shamela Title | What It Tests |
|---|------|--------------|---------------|
| C01 | **Dense sharh with heavy matn quotation** | فتح الباري شرح صحيح البخاري (ط. السلفية) | The most famous sharh in Islam. 13 volumes. Both matn author (al-Bukhari d. 256) and sharh author (Ibn Hajar d. 852) must be correctly identified. Matn is quoted extensively — tests layer detection accuracy. |
| C02 | **Short sharh that might read as risalah** | شرح الورقات في أصول الفقه (المحلي) | Very short sharh on a very short matn (al-Waraqat by al-Juwayni). Tests: does multi-layer detection work when the text is short and sharh dominates? Multiple editions on Shamela — tests correct muhaqiq attribution. |
| C03 | **FALSE POSITIVE TRAP: heavy quotation, NOT multi-layer** | إعلام الموقعين عن رب العالمين | ابن القيم (d. 751) quotes Ibn Taymiyyah extensively throughout but this is an ORIGINAL composition, not a sharh. If pipeline says `is_multi_layer: true`, it's a false positive. Genre should be risalah or other. This may be the single most valuable probe in the set — false positive multi-layer classification silently corrupts metadata for hundreds of books. |
| C04 | **Tahqiq apparatus as pseudo-layer** | تفسير الطبري (جامع البيان) - ت. أحمد شاكر | Tafsir al-Tabari edited by Ahmad Shakir, whose tahqiq footnotes are extensive and substantive. Tests: does the pipeline treat editorial footnotes as a text layer (wrong) or correctly identify them as tahqiq apparatus (right)? Muhaqiq is NOT a layer author. Also covers tafsir genre at proper depth. |

---

## GROUP D: Disputed Attribution & Author Difficulty (6 books)

The highest-value probes. Wrong attribution metadata becomes wrong owner beliefs.

| # | Difficulty | Shamela Title | Author (per Shamela) | What It Tests |
|---|-----------|--------------|---------------------|---------------|
| D01 | **Explicitly disputed** | الفقه الأكبر | "ينسب لأبي حنيفة" (ت 150هـ) | Shamela itself says "attributed to" — not definitive. Pipeline MUST detect `attribution_status: disputed` or `attributed`. If it says `definitive`, it's propagating a contested claim as fact. Short aqidah text. |
| D02 | **Disputed text/modification** | الإبانة عن أصول الديانة | أبو الحسن الأشعري (ت 324هـ) | Authenticity of the CURRENT TEXT is disputed — some scholars argue the version we have was modified by later Hanbali editors from al-Ash'ari's original. Tests: can the LLM detect this textual dispute? Aqidah text. |
| D03 | **Common-name author + adab genre** | البيان والتبيين | الجاحظ (ت 255هـ) | Tests adab genre (last uncovered genre). Al-Jahiz's full name (عمرو بن بحر بن محبوب الكناني) is complex — tests nasab reconstruction from kunyah. Also: literary/rhetorical text, not traditional Islamic science — tests science_scope correctly being empty or [adab]. |
| D04 | **Author-short-only (hadith)** | حديث الضب الذي تكلم بين يدي النبي للطبراني | الطبراني (from author_short) | From the Phase A "content_minimal" list (1 page!). Author_short is probably just "الطبراني" — LLM must infer: al-Tabarani (Sulayman ibn Ahmad, d. 360). Minimal text makes this a hard inference task. |
| D05 | **Author-short-only (different science)** | الورقة النحوية | Unknown (from Phase A tiny books) | 2-page nahw text from Phase A tiny books. Very likely has minimal author metadata. Tests: author inference on a non-hadith tiny text. If author cannot be identified, the pipeline should say so (low confidence), NOT hallucinate a name. |
| D06 | **Institutional author** | فتاوى اللجنة الدائمة للبحوث العلمية والإفتاء | اللجنة الدائمة | Compiled by a permanent committee, not an individual scholar. Tests: does the pipeline correctly handle institutional authorship without inventing a person? Should produce a committee identifier. Available on Shamela. |

---

## GROUP E: Trust Calibration (4 books)

Testing the 5-factor trust algorithm at extremes and boundaries.

| # | Expected Trust | Shamela Title | Reasoning |
|---|---------------|--------------|-----------|
| E01 | **Clearly verified** (>>0.65) | صحيح مسلم بشرح النووي | Classical hadith collection (highest source authority) + major classical sharh (highest author standing) + established publisher. Every trust factor should score high. If this gets flagged, trust algorithm is broken. |
| E02 | **Clearly flagged** (<<0.65) | نصيحة لطالب الحق (ضمن آثار المعلمي) | From Phase A tiny books (2 pages). Modern compilation, no independent tahqiq, minimal content. Low author standing (lesser-known), low text fidelity (very short), no publisher reputation signal. Should score well below 0.65. |
| E03 | **Borderline** (~0.65) | أدب النفوس للآجري | From Phase A page_mismatch list (24 digital vs 271 physical — partial export). Classical author (al-Ajurri, d. 360) with good standing, BUT text fidelity is poor (truncated export). Tests: does high author standing + poor text fidelity land near the 0.65 boundary? |
| E04 | **Famous author, degraded edition** | One of the page_mismatch hadith books | أحاديث العطار عن شيوخه (10 digital vs 279 physical pages — 4% complete). Even if the attributed author has standing, a 4% complete export should drag text_fidelity to rock bottom. Tests: does the trust algorithm correctly penalize incomplete exports despite author prestige? |

---

## GROUP F: Technical Edge Cases (8 books)

Targeting known pipeline vulnerabilities from Phase A findings.

| # | Edge Case | Shamela Title | Source | What It Tests |
|---|-----------|--------------|--------|---------------|
| F01 | **Minimal content** (1 page) | حديث الضب الذي تكلم بين يدي النبي للطبراني | Phase A tiny books | Already used as D04. 1 page of content. Tests: is text_sample long enough for LLM inference? Does confidence correctly drop for sparse data? **Dual-use: also tests author-short-only.** |
| F02 | **Large multi-volume** (>10 vols) | مجموع الفتاوى (ابن تيمية) | Group B06 | Already selected as B06. 37 volumes. Tests processing at scale. **Dual-use.** |
| F03 | **Format B HTML** | *Owner must verify* — pick one of the 64 books that triggered Bug 2 | Phase A Bug 2 | I cannot identify specific Format B books from audit data. **Owner action:** when running Phase C, if any of the 50 books happens to be Format B, the extraction will confirm the fix. Additionally, the synthetic Format B fixture (created as a pre-req by Claude Code) covers this. Mark as "opportunistic" — if no Format B book is among the 50, we add one in Phase D. |
| F04 | **رواية field** | *Pick from the 26 riwayah books* | Phase A | Cannot identify specific names from audit data. **Mitigation:** the 1,228 books in كتب السنة likely include most of the 26 رواية books. Some of our hadith picks (A04, C01, E01, D04) may include one. During Phase C execution, check the extraction.json for riwayah field presence. If none of the 50 books has it, add one in Phase D. |
| F05 | **Truncated export** | أحاديث العطار عن شيوخه | Phase A page_mismatch | Already used as E04. 10 digital vs 279 physical pages. Tests: pipeline behavior on severely incomplete text. Quality_issues should flag truncation. **Dual-use.** |
| F06 | **Page count mismatch** | الإبدال في لغات الأزد | Phase A page_mismatch | 73 digital vs 494 physical pages (15% complete). Less severe truncation than F05 — still has substantial text. Tests: does moderate truncation affect LLM inference quality? Does quality_issues correctly flag it? |
| F07 | **Multiple muhaqiqs** | تفسير الطبري (جامع البيان) - ت. أحمد شاكر | Group C04 | Ahmad Shakir's tahqiq was completed by others after his death. Tests: how does the pipeline handle partial tahqiq with multiple editors? **Dual-use with C04.** |
| F08 | **Multi-science scope** | بداية المجتهد ونهاية المقتصد | Group B09 | Already selected as B09. Should produce `science_scope: ["fiqh", "usul_al_fiqh"]` or similar multi-entry. Tests: does the LLM correctly output multiple science entries when appropriate? **Dual-use.** |

**Note on dual-use:** F01/F02/F05/F07/F08 overlap with other groups. This is by design — they serve their primary group purpose while also exercising the technical edge case. The distinct book count remains 50. F03 and F04 are marked as "opportunistic" because I cannot identify specific books from the available audit data.

---

## GROUP G: Consensus Stress (4 books)

Chosen because the two models (Opus 4.6 + Command A) are likely to disagree, testing consensus.

| # | Stress Type | Shamela Title | Why Models Will Disagree |
|---|-----------|--------------|------------------------|
| G01 | **Obscure work** | الكلام على حديث الإستلقاء لأبي موسى المديني | Phase A tiny book (2 pages). Abu Musa al-Madini (d. 581) is a relatively obscure hadith scholar. With only 2 pages of text and an uncommon author, both models will have weak priors. Tests: do models express low confidence? Does consensus correctly trigger human gate? |
| G02 | **Genre-ambiguous** | إعلام الموقعين عن رب العالمين | Already used as C03. Ibn al-Qayyim's masterwork blends fatawa, fiqh, usul, and legal theory. Is it risalah? fatawa? fiqh_comparative? other? Models may disagree on genre. Tests: consensus behavior on genuine genre ambiguity. **Dual-use.** |
| G03 | **School-dependent classification** | شرح العقيدة الطحاوية | ابن أبي العز الحنفي (d. 792). The aqidah text of al-Tahawi is near-universally accepted, but the sharh by Ibn Abi al-'Izz takes positions that different scholarly traditions classify differently. Tests: do models give different school_affiliations? How does consensus handle it? Multi-layer (matn + sharh). |
| G04 | **Structural format ambiguity** | مقامات الحريري | الحريري (d. 516). Literary maqamat — prose interspersed with poetry (sajʿ). Neither pure prose nor pure verse. Tests: structural_format should be "mixed" or "prose". Is genre adab or other? Models may disagree. |

---

## Final Deduplicated Book List (37 distinct books + 13 fixtures = 50 total)

After resolving dual-use overlaps, here are the 37 NEW books to process from Shamela (in addition to the 13 fixtures):

| # | Shamela Title | Groups | Primary Test |
|---|--------------|--------|-------------|
| 1 | الأربعين النووية | B01 | matn genre |
| 2 | حاشية ابن عابدين (رد المحتار) | B02 | hashiyah + 3-layer |
| 3 | زاد المستقنع في اختصار المقنع | B03 | mukhtasar genre |
| 4 | حاشية العطار على شرح المحلي على جمع الجوامع | B04 | taqrirat/hashiyah boundary |
| 5 | الموسوعة الفقهية الكويتية | B05 | mawsuah + institutional author |
| 6 | مجموع الفتاوى (ابن تيمية) | B06, F02 | fatawa + large multi-volume |
| 7 | لسان العرب | B07 | mujam genre |
| 8 | سير أعلام النبلاء | B08 | tabaqat genre |
| 9 | بداية المجتهد ونهاية المقتصد | B09, F08 | fiqh_comparative + multi-science |
| 10 | الرحيق المختوم | B10 | sirah genre + modern |
| 11 | البداية والنهاية | B11 | tarikh (must not classify as tafsir) |
| 12 | فتح الباري شرح صحيح البخاري | C01 | dense sharh + multi-layer |
| 13 | شرح الورقات (المحلي) | C02 | short sharh + multi-layer |
| 14 | إعلام الموقعين عن رب العالمين | C03, G02 | FALSE POSITIVE multi-layer trap + genre ambiguity |
| 15 | تفسير الطبري (جامع البيان) ت. شاكر | C04, F07 | tahqiq ≠ layer + multiple muhaqiqs |
| 16 | الفقه الأكبر | D01 | disputed attribution |
| 17 | الإبانة عن أصول الديانة | D02 | disputed text modification |
| 18 | البيان والتبيين | D03 | adab genre + complex nasab |
| 19 | حديث الضب الذي تكلم بين يدي النبي للطبراني | D04, F01, G01-adjacent | author-short-only + minimal content |
| 20 | الورقة النحوية | D05 | author-short-only (nahw) |
| 21 | فتاوى اللجنة الدائمة للبحوث العلمية والإفتاء | D06 | institutional author |
| 22 | صحيح مسلم بشرح النووي | E01 | trust: clearly verified |
| 23 | نصيحة لطالب الحق (ضمن آثار المعلمي) | E02 | trust: clearly flagged |
| 24 | أدب النفوس للآجري | E03 | trust: borderline + partial export |
| 25 | أحاديث العطار عن شيوخه | E04, F05 | trust: degraded + severely truncated |
| 26 | الإبدال في لغات الأزد | F06 | moderate page mismatch |
| 27 | الكلام على حديث الاستلقاء لأبي موسى المديني | G01 | obscure work + consensus stress |
| 28 | شرح العقيدة الطحاوية (ابن أبي العز) | G03 | school-dependent classification + multi-layer |
| 29 | مقامات الحريري | G04 | structural format ambiguity |

**Count: 29 distinct new books + 8 dual-use overlaps resolved = 29 new + 13 fixtures = 42 total processing units.** 

Wait — I need 50 total. Let me add 8 more strategically selected books to reach 50.

---

## GROUP H: Additional Coverage (8 books)

These fill remaining gaps and add depth where single probes are insufficient.

| # | Shamela Title | Rationale |
|---|--------------|-----------|
| 30 | مختصر صحيح مسلم للمنذري | A mukhtasar of a hadith collection — tests mukhtasar genre when the content is hadith (does genre follow form or content?). Al-Mundhiri (d. 656). |
| 31 | الرسالة (الشافعي) | The foundational usul al-fiqh text by al-Shafi'i (d. 204). Tests: risalah vs matn boundary (it's called "al-Risalah" but is a foundational work). Very famous author, early classical. |
| 32 | ديوان المتنبي | Poetry collection (diwan). Tests: structural_format = "verse", genre = nazm or other/adab. Different from A13 (alfiyyah is didactic nazm; al-Mutanabbi is pure literary poetry). |
| 33 | الأذكار (النووي) | Second book by the same author as B01 (al-Nawawi). Tests: does the pipeline handle two books by the same author without scholar registry collision? Different genre (this is a compilation/risalah, not a matn). |
| 34 | مسند الإمام أحمد | The largest hadith collection. Tests hadith_collection genre at massive scale. Author: Ahmad ibn Hanbal (d. 241). Multiple muhaqiqs (Shu'ayb al-Arna'ut team). |
| 35 | تحفة المودود بأحكام المولود (ابن القيم) | Second book by Ibn al-Qayyim (also C03). Tests: scholar registry handles same author's different works correctly. Risalah genre, fiqh science. |
| 36 | الأم (الشافعي) | Al-Shafi'i's major fiqh work. Multi-volume. Tests: does the pipeline link this to the same canonical_id as #31 (also al-Shafi'i)? Both should map to the same scholar. |
| 37 | معالم بيانية في آيات قرآنية | Phase A tiny book (2 pages). Modern-looking title, minimal content. Tests: pipeline on modern minimal-content tafsir/balagha text. May have unusual metadata card. |

---

## FINAL COUNT: 50

- Group A: 13 fixtures
- Group B: 11 genre coverage
- Group C: 4 multi-layer
- Group D: 6 attribution/author
- Group E: 4 trust calibration
- Group F: 8 edge cases (6 dual-use, 2 "opportunistic")
- Group G: 4 consensus stress (2 dual-use)
- Group H: 8 additional coverage

Distinct new books from Shamela: **37**
Fixtures: **13**
**Total: 50**

---

## Dimension Coverage Verification

| Dimension | Probes | Assessment |
|-----------|--------|------------|
| Genre (18 values) | All 18 covered | ✅ Complete |
| Multi-layer variants | A11 (sharh), B02 (hashiyah), B04 (taqrirat), C01 (dense sharh), C02 (short sharh), C03 (false positive), C04 (tahqiq pseudo-layer), G03 (aqidah sharh) | ✅ 8 probes including false positive |
| Disputed attribution | D01, D02, D03 (partially) | ✅ 3 probes |
| Author difficulty | D04 (short-only hadith), D05 (short-only nahw), D06 (institutional), B05 (institutional), B09 (patronymic), A10 (no author field) | ✅ 6 probes |
| Trust calibration | E01 (high), E02 (low), E03 (borderline), E04 (degraded) | ✅ 4 probes at all extremes |
| Technical edge cases | F01 (minimal), F02 (large), F05 (truncated), F06 (mismatch), F07 (multi-muhaqiq) | ✅ 5+ confirmed |
| Consensus stress | G01 (obscure), G02 (genre ambiguous), G03 (school-dependent), G04 (format ambiguous) | ✅ 4 probes |
| Era coverage | Pre-300 (D01 150, A04 282), 300-700 (D03 255, D02 324, B09 595, A08 412), 700-1000 (B06 728, B08 748, B11 774, C01 852, B04 1250), Post-1200 (B10 1427, A12 1393, A03 modern) | ✅ All eras |
| Sciences | fiqh, hadith, tafsir, nahw, balagha, usul, aqidah, tarikh, sirah, lugha, adab, sarf | ✅ 12+ sciences |
| Same-author pairs | النووي (B01 + #33), ابن القيم (C03 + #35), الشافعي (#31 + #36) | ✅ Tests scholar registry dedup |
| Scale range | 1 page (#19) to 37 volumes (B06) | ✅ Full range |

---

## books.txt Template

After verifying which books are in the collection (directory name matching), create this file:

```
# Group A fixtures are handled separately by the Phase C script
# Group B — Genre Coverage
الأربعين النووية
حاشية ابن عابدين = رد المحتار - ط الحلبي
زاد المستقنع في اختصار المقنع
حاشية العطار على شرح الجلال المحلي على جمع الجوامع
الموسوعة الفقهية الكويتية
مجموع الفتاوى
لسان العرب
سير أعلام النبلاء
بداية المجتهد ونهاية المقتصد
الرحيق المختوم
البداية والنهاية
# Group C — Multi-Layer
فتح الباري شرح صحيح البخاري - ط السلفية
شرح الورقات في أصول الفقه
إعلام الموقعين عن رب العالمين
تفسير الطبري = جامع البيان ط هجر
# Group D — Attribution
الفقه الأكبر
الإبانة عن أصول الديانة - ت فوقية
البيان والتبيين
حديث الضب الذي تكلم بين يدي النبي للطبراني
الورقة النحوية
فتاوى اللجنة الدائمة - المجموعة الأولى
# Group E — Trust
صحيح مسلم بشرح النووي
نصيحة لطالب الحق - ضمن آثار المعلمي
أدب النفوس للآجري
أحاديث العطار عن شيوخه
# Group F — Edge Cases
الإبدال في لغات الأزد
# Group G — Consensus
الكلام على حديث الاستلقاء لأبي موسى المديني
شرح العقيدة الطحاوية
مقامات الحريري
# Group H — Additional
مختصر صحيح مسلم للمنذري
الرسالة للشافعي
ديوان المتنبي
الأذكار للنووي
مسند الإمام أحمد
تحفة المودود بأحكام المولود
الأم للشافعي
معالم بيانية في آيات قرآنية
```

**NOTE:** Directory names in your collection will differ from these titles. The Phase C script resolves by fuzzy matching. The owner should verify/correct each line against actual directory names in his collection before running.
