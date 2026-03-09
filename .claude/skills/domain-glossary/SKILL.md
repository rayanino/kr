---
name: domain-glossary
description: Comprehensive glossary of Islamic scholarly terminology mapped to KR data models. Use when classifying genres, identifying scholars, processing Arabic text structure, or when uncertain about domain vocabulary.
---

# KR Domain Glossary — Islamic Scholarly Terminology

This glossary maps Islamic scholarly terms to KR pipeline concepts and data model types. Terms are grouped by domain. Each entry includes: Arabic term, transliteration, precise definition, KR mapping, and common confusion points.

**Usage:** Reference this glossary when implementing genre classification, author identification, commentary hierarchy detection, science scope assignment, or any domain-specific logic. Precision in these terms directly prevents metadata corruption.

---

## 1. Genre Terminology (→ `Genre` enum in contracts.py)

### متن (matn)
**Definition:** A foundational, standalone text that serves as the base for a scholarly tradition. Other works (sharh, hashiyah, nazm) are built upon it. Typically concise, authoritative, and widely memorized.
**KR mapping:** `Genre.MATN`
**Examples:** متن الآجرومية (nahw), عمدة الأحكام (hadith/fiqh), متن ابن عاشر (fiqh maliki)
**Confusion:** Not every short work is a matn. A matn implies an ecosystem of commentaries built upon it. A modern risalah that nobody commented on is NOT a matn.

### شرح (sharh)
**Definition:** A commentary that explains a matn line-by-line or section-by-section. The sharh typically quotes the matn text then provides explanation. This creates a multi-layer structure.
**KR mapping:** `Genre.SHARH`, `is_multi_layer: true`, `structural_format: commentary`
**Genre chain:** `sharh_of` → the matn it explains
**Examples:** شرح ابن عقيل على ألفية ابن مالك, فتح الباري شرح صحيح البخاري
**Confusion:** A sharh is NOT merely "about" the same topic. It must directly engage with the matn's text, quoting and explaining it.

### حاشية (hashiyah)
**Definition:** A marginal gloss or super-commentary written on a sharh (NOT on the matn directly). Hashiyah engages with the sharh's explanations, correcting, elaborating, or adding nuances.
**KR mapping:** `Genre.HASHIYAH`, `is_multi_layer: true`, `structural_format: commentary`
**Genre chain:** `hashiyah_on` → the sharh it glosses
**Layer hierarchy:** matn → sharh → hashiyah → ta'liqat (up to 4+ layers in some traditions)
**Examples:** حاشية الصبان على شرح الأشموني على ألفية ابن مالك (3 layers)
**Confusion:** hashiyah vs sharh — the hashiyah comments on the SHARH, not on the matn. If it primarily explains the matn directly, it's a sharh even if called حاشية in the title.

### تعليق (ta'liq)
**Definition:** Brief annotations or notes on a text, less systematic than a hashiyah. Often by a student or later scholar adding clarifications.
**KR mapping:** Currently mapped to `Genre.HASHIYAH` (closest equivalent). Mark with a note.
**Confusion:** More informal than hashiyah; may not follow the text sequentially.

### تقريرات (taqrirat)
**Definition:** Lecture notes or oral explanations of a text, typically transcribed by students. Records a scholar's live teaching on a matn or sharh.
**KR mapping:** `Genre.TAQRIRAT`, `is_multi_layer: true`
**Genre chain:** `taqrirat_on` → the text being taught
**Examples:** تقريرات الشيخ ابن عثيمين على زاد المستقنع
**Confusion:** Unlike sharh, taqrirat are typically unpolished and may contain asides, questions, digressions.

### مختصر (mukhtasar)
**Definition:** An abridgment that condenses a longer work into essential points, preserving core content in fewer words.
**KR mapping:** `Genre.MUKHTASAR`
**Genre chain:** `mukhtasar_of` → the work it abridges
**Examples:** مختصر خليل (fiqh maliki), بلوغ المرام (mukhtasar of larger hadith compilations — loosely)
**Confusion:** A mukhtasar of a matn IS itself a matn if it becomes a base text for its own commentary tradition.

### نظم (nazm)
**Definition:** A versified rendering of a prose text, putting the content into rajaz or other meter for memorization.
**KR mapping:** `Genre.NAZM`, `structural_format: verse`
**Genre chain:** `nazm_of` → the prose original
**Examples:** ألفية ابن مالك (nazm of nahw principles), لامية الأفعال (sarf)
**Confusion:** Not all Arabic poetry is nazm. Nazm specifically versifies scholarly content. Qasidah poetry is `Genre.ADAB` or `Genre.OTHER`.

### رسالة (risalah)
**Definition:** A short treatise on a specific topic. Standalone, focused, does not serve as a base text for commentaries.
**KR mapping:** `Genre.RISALAH`
**Examples:** آداب الفتوى (النووي), أحكام الاضطباع والرمل
**Confusion:** Any modern academic paper or short monograph is a risalah. NOT a matn (no commentary ecosystem). NOT a sharh (doesn't comment on another text).

### موسوعة (mawsuah)
**Definition:** An encyclopedia or comprehensive reference work covering a broad field.
**KR mapping:** `Genre.MAWSUAH`
**Examples:** الموسوعة الفقهية الكويتية
**Confusion:** Large compilations are not always mawsuah — المغني لابن قدامة is fiqh_comparative, not mawsuah.

### فتاوى (fatawa)
**Definition:** Collections of legal rulings/opinions, typically organized by fiqh chapter.
**KR mapping:** `Genre.FATAWA`
**Examples:** مجموع فتاوى ابن تيمية, فتاوى اللجنة الدائمة
**Confusion:** Individual fatwas embedded in a risalah don't make the work fatawa — it's the collection format that matters.

### معجم (mujam)
**Definition:** A dictionary or lexicon, alphabetically or thematically organized.
**KR mapping:** `Genre.MUJAM`
**Examples:** لسان العرب, المعجم الوسيط, معجم مقاييس اللغة
**Confusion:** Tabaqat organized alphabetically by name are NOT mujam — they're tabaqat.

### طبقات (tabaqat)
**Definition:** Biographical dictionaries organized by generation (tabaqah = generational layer) or alphabetically. Document scholars' lives, teachers, students, and works.
**KR mapping:** `Genre.TABAQAT`
**Examples:** طبقات الشافعية الكبرى, سير أعلام النبلاء
**Confusion:** Not every biographical work is tabaqat — tarikh (chronological history) and sirah (biography of one person) are different genres.

### فقه مقارن (fiqh_comparative)
**Definition:** Comparative jurisprudence that systematically presents multiple madhab opinions on each issue.
**KR mapping:** `Genre.FIQH_COMPARATIVE`
**Examples:** المغني لابن قدامة, بداية المجتهد
**Confusion:** A Hanbali fiqh text that occasionally mentions other opinions is NOT fiqh_comparative — it must systematically compare across madhabs.

### حديث (hadith_collection)
**Definition:** A compiled collection of prophetic traditions, organized by topic, narrator, or other scheme.
**KR mapping:** `Genre.HADITH_COLLECTION`
**Sub-types (not separate enums but important context):**
- **مصنَّف (musannaf):** Organized by fiqh chapter, includes non-prophetic athar. Example: مصنف ابن أبي شيبة
- **مسنَد (musnad):** Organized by narrator (companion). Example: مسند الإمام أحمد
- **سنن (sunan):** Organized by fiqh chapter, prophetic hadith only. Example: سنن أبي داود
- **جامع (jami'):** Comprehensive, covers all eight major topics of hadith. Example: جامع الترمذي, صحيح البخاري
- **جزء (juz'):** Small collection on a specific topic or from one narrator. Example: جزء فيه من أحاديث الإمام أيوب
**Confusion:** أحاديث الأحكام (hadith organized by fiqh rulings) is hadith_collection, NOT fiqh. The content is hadith texts; the organizing principle is fiqh.

### تفسير (tafsir)
**Definition:** Quranic exegesis — explanation of the Quran verse by verse.
**KR mapping:** `Genre.TAFSIR`
**Examples:** تفسير ابن كثير, تفسير الجلالين
**Confusion:** A work that quotes Quran verses is NOT tafsir unless its primary structure is organized by and explains the Quran.

### سيرة (sirah)
**Definition:** Biography, especially of the Prophet Muhammad.
**KR mapping:** `Genre.SIRAH`
**Examples:** سيرة ابن هشام, الرحيق المختوم
**Confusion:** Autobiographies/memoirs of non-prophetic figures are `Genre.OTHER` or `Genre.TARIKH`.

### تاريخ (tarikh)
**Definition:** Historical chronicle, typically organized chronologically.
**KR mapping:** `Genre.TARIKH`
**Examples:** تاريخ الطبري, البداية والنهاية
**Confusion:** Tabaqat are biographical, not chronological — don't confuse them.

### أدب (adab)
**Definition:** Literary works including belles-lettres, literary compilations, anecdotes, and rhetorical works.
**KR mapping:** `Genre.ADAB`
**Examples:** أخبار أبي القاسم الزجاجي, البيان والتبيين, الأمالي
**Confusion:** "adab" in modern Arabic means "literature" broadly, but in classical context it specifically means the أمالي/أخبار literary compilation tradition.

---

## 2. Commentary Hierarchy (→ `is_multi_layer`, `GenreRelationType`)

The Islamic scholarly tradition has a distinctive multi-layer commentary system:

```
Layer 0: متن (matn) — base text
Layer 1: شرح (sharh) — explains the matn
Layer 2: حاشية (hashiyah) — glosses the sharh
Layer 3: تعليقات / تقريرات — notes on any layer
```

**KR detection rule:** If a work contains embedded text from another work AND provides commentary on that embedded text → `is_multi_layer: true`.

**Key relationships (GenreRelationType):**
| Relation | Arabic | Meaning |
|----------|--------|---------|
| `sharh_of` | شرح على | This work explains that matn |
| `hashiyah_on` | حاشية على | This work glosses that sharh |
| `mukhtasar_of` | مختصر ل | This work abridges that text |
| `nazm_of` | نظم ل | This work versifies that prose |
| `taqrirat_on` | تقريرات على | This work records lectures on that text |
| `responds_to` | رد على / تعقبات على | This work critiques/responds to that text |

**Detection signals for multi-layer:**
- Title contains شرح, حاشية, تعليق, تقريرات + name of another text
- Text alternates between quoted matn (often in bold or brackets) and commentary
- Structural format is `commentary` (interleaved base + explanation)

**NOT multi-layer:**
- A work that merely CITES another (responds_to is NOT multi-layer unless text is interleaved)
- A work "about" another topic — reference is not embedding

---

## 3. Hadith Science Terms

### إسناد (isnad)
**Definition:** Chain of transmitters connecting the reporter to the Prophet or earlier authority. Each link is a narrator (rawi).
**KR relevance:** Source engine preserves isnad text exactly. Atomization must never split an isnad chain.

### متن الحديث (matn al-hadith)
**Definition:** The actual content of the hadith (what was said/done), as opposed to the isnad.
**KR relevance:** Do NOT confuse with متن (matn) as a genre. In hadith science, matn refers to the hadith text itself.

### سند (sanad)
**Definition:** Synonym for isnad. Used interchangeably in most contexts.

### تخريج (takhrij)
**Definition:** Tracing a hadith to all the collections that report it, with full isnad analysis.
**KR relevance:** May appear as a genre_chain relation or in science_scope.

### جرح وتعديل (jarh wa ta'dil)
**Definition:** The science of narrator criticism — evaluating transmitters as reliable or unreliable.
**KR relevance:** Maps to `science_scope: ["hadith"]` (sub-field, not separate science in our model).

---

## 4. Fiqh Structure Terms

### فروع (furu')
**Definition:** Applied jurisprudence — specific rulings on acts of worship, transactions, etc.
**KR relevance:** Most fiqh texts in the library are furu'. Maps to `science_scope: ["fiqh"]`.

### أصول الفقه (usul al-fiqh)
**Definition:** Legal theory — methodology for deriving rulings from sources (Quran, Sunnah, ijma', qiyas).
**KR relevance:** Maps to `science_scope: ["usul_al_fiqh"]`. Different from fiqh proper.
**Confusion:** أصول in common usage can mean "basics" — but أصول الفقه is a specific discipline.

### مسألة (mas'alah)
**Definition:** A specific legal question or case discussed in fiqh.
**KR relevance:** Relevant to atomization — each mas'alah may become a separate atom.

### خلاف (khilaf)
**Definition:** Scholarly disagreement on a mas'alah. Texts that document khilaf are often fiqh_comparative.
**KR relevance:** `structural_format: tabular_khilaf` when formatted as comparison tables.

### راجح (rajih)
**Definition:** The preponderant/strongest opinion among competing views.
**KR relevance:** Important for excerpting engine — the rajih is the core claim.

### دليل (dalil)
**Definition:** Evidence from Quran, Sunnah, ijma', or qiyas supporting a ruling.
**KR relevance:** Excerpts should preserve the dalil alongside the claim.

---

## 5. Scholar Identification Terms (→ author_identification scoring)

### اسم (ism)
**Definition:** Given/personal name. Example: محمد, يحيى, عبد الله
**KR relevance:** Low discriminating power — many scholars share common isms.

### نسب (nasab)
**Definition:** Patronymic chain using بن/ابن (son of). Example: محمد بن إدريس بن العباس
**KR relevance:** Full nasab chains are highly identifying but models often abbreviate them.

### كنية (kunya)
**Definition:** Teknonym using أبو/أم + name. Example: أبو حنيفة, أبو القاسم
**KR relevance:** Some scholars are known primarily by kunya. The kunya IS identifying.

### لقب (laqab)
**Definition:** Honorific title or epithet. Example: جلال الدين, شمس الدين, الحافظ, القاضي
**KR relevance:** Important for recognition but less discriminating alone.

### نسبة (nisba)
**Definition:** Attribution to place, tribe, school, or profession. Example: البغدادي, الشافعي, الزجاجي
**KR relevance:** Highly discriminating — often the single most identifying component. The eval harness `_extract_name_tokens` function relies heavily on nisba matching.

### طبقة (tabaqah)
**Definition:** Generational cohort of scholars. Example: "scholars of the 3rd century hijri"
**KR relevance:** Death date (وفاة) is the primary tabaqah indicator. Combined with nisba, uniquely identifies a scholar.

### وفاة (wafat / death date)
**Definition:** Death date in Hijri calendar. Written as ت followed by year, e.g., ت 911هـ
**KR relevance:** `author_death_hijri` field. Exact match + any name component match → same person.

---

## 6. Text Format Terms

### شاملة (Shamela)
**Definition:** المكتبة الشاملة — the largest digital Islamic library software. Exports as .bok (binary) or .htm (HTML).
**KR mapping:** `SourceFormat.SHAMELA_HTML`
**HTML structure:** Single .htm file per volume. First PageText div contains metadata card (بطاقة الكتاب). Subsequent PageText divs contain text pages.

### OpenITI mARkdown
**Definition:** Machine-readable format developed by the OpenITI project for Arabic texts. Uses special markers for structural elements.
**KR mapping:** `SourceFormat.PLAIN_TEXT` (treat as enriched plain text)
**Note:** Not yet supported in Stage 1. Future import format.

### تحقيق (tahqiq)
**Definition:** Critical scholarly edition. The muhaqqiq (editor/researcher) is NOT the author — they produce the scholarly apparatus (footnotes, variant readings, manuscript comparison).
**KR mapping:** The muhaqqiq is stored in `ScholarReference` as `muhaqiq`, separate from the author.
**Confusion:** NEVER list the muhaqqiq as the author. If a source says "تحقيق أحمد شاكر", أحمد شاكر is the muhaqqiq, not the author.

### محقق (muhaqqiq)
**Definition:** The scholar who prepared the tahqiq (critical edition).
**KR mapping:** `SourceMetadata.muhaqiq: ScholarReference`
**Confusion:** Same as above — muhaqqiq ≠ author.

---

## 7. Science Tree Terms (→ `science_scope` values)

| Arabic | Transliteration | English | KR Value |
|--------|----------------|---------|----------|
| نحو | nahw | Arabic grammar (syntax) | `nahw` |
| صرف | sarf | Arabic morphology | `sarf` |
| بلاغة | balagha | Arabic rhetoric | `balagha` |
| فقه | fiqh | Islamic jurisprudence | `fiqh` |
| أصول الفقه | usul al-fiqh | Legal theory/methodology | `usul_al_fiqh` |
| حديث | hadith | Prophetic traditions | `hadith` |
| تفسير | tafsir | Quranic exegesis | `tafsir` |
| عقيدة | aqidah | Islamic theology/creed | `aqidah` |
| تصوف | tasawwuf | Islamic spirituality/Sufism | `tasawwuf` |
| سيرة | sirah | Prophetic biography | `sirah` |
| تاريخ | tarikh | Islamic history | `tarikh` |
| أدب | adab | Arabic literature | `adab` |

**Multi-scope rule:** A work can belong to multiple sciences. Example: بلوغ المرام → `["hadith", "fiqh"]` (hadith texts organized by fiqh topics).

**Empty scope rule:** Non-Islamic-scholarship works (autobiography, fiction, general knowledge) have `science_scope: []`.

---

## 8. Authority Level Terms (→ `AuthorityLevel` enum)

### أصلي / مصدر أولي (primary)
**Definition:** Original composition by the attributed author. Classical or modern.
**KR mapping:** `AuthorityLevel.PRIMARY`
**Examples:** الرسالة للشافعي (classical), المغني لابن قدامة (classical)

### مرجع (reference)
**Definition:** Recognized scholarly edition with scholarly apparatus (tahqiq, footnotes, variant readings).
**KR mapping:** `AuthorityLevel.REFERENCE`
**Examples:** تفسير الطبري (tahqiq عبد الله التركي)

### تأليف حديث (modern_compilation)
**Definition:** Modern work that compiles, summarizes, or presents classical material for contemporary audiences.
**KR mapping:** `AuthorityLevel.MODERN_COMPILATION`
**Examples:** الملخص الفقهي (contemporary fiqh summary), university textbooks

---

## Common Claude Confusion Points

1. **sharh vs hashiyah:** sharh explains the matn directly; hashiyah comments on the sharh. If you see "حاشية على شرح X", the hashiyah is on the sharh, not on the matn.

2. **matn vs risalah:** A matn becomes a matn because scholars write commentaries on it. A standalone short work with no commentary ecosystem is a risalah, even if old.

3. **تعقبات (ta'qubat) vs sharh:** Ta'qubat are critical corrections/refutations of another work. They CITE the other work but don't EXPLAIN it. Genre = `risalah` with relation `responds_to`, NOT `sharh`. is_multi_layer = false (citation, not interleaving).

4. **hadith_collection vs fiqh:** If the primary content is hadith texts and the organizing principle is fiqh topics → hadith_collection with `science_scope: ["hadith", "fiqh"]`. If the primary content is fiqh discussion that quotes hadith as evidence → fiqh with `science_scope: ["fiqh"]`.

5. **Author death date format:** Always Hijri calendar. ت = توفي (died). If a range like "(631-676 هـ)" appears, the death year is the second number (676).

6. **Modern vs classical boundary:** Roughly 1300 هـ / 1900 CE. Scholars before this are classical (likely `authority_level: primary`). Authors after are modern (likely `modern_compilation` unless clearly a primary work).

7. **Shamela categories are UNRELIABLE for genre/science_scope.** Shamela categorizes by author's primary field, not by the specific work's content. Example: الزجاجي is filed under النحو والصرف because he's a grammarian, but أخبار أبي القاسم الزجاجي is actually أدب.
