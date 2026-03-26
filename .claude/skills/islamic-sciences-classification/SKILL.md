---
name: islamic-sciences-classification
description: How each Islamic science structures its texts, what terminology signals each science, and what processing implications each has for the KR pipeline. Use when classifying genres, building division trees, detecting text layers, constructing taxonomy placements, or when uncertain which science a text belongs to.
---

# Islamic Sciences Classification — Text Processing Guide

Every Islamic science produces texts with distinctive structural patterns, terminology, and processing requirements. Misidentifying the science leads to wrong division trees, incorrect genre classification, broken layer separation, and taxonomic misplacement. This skill maps each science to its text processing implications for the KR pipeline.

**Usage:** Reference this when implementing genre classification, division tree construction, excerpting, taxonomy placement, or any domain-specific text analysis. The science of a text determines HOW to process it, not just WHERE to place it.

---

## The Classification Hierarchy

Islamic scholarly tradition organizes knowledge into a hierarchy. The primary division is:

```
العلوم الشرعية (Transmitted Sciences) — authority comes from revelation/tradition
├── علم القرآن (Quranic Sciences)
│   ├── التفسير (Exegesis)
│   ├── أصول التفسير (Hermeneutical Principles)
│   ├── علوم القرآن (Quranic Studies: asbab al-nuzul, nasikh/mansukh, qira'at)
│   └── التجويد (Recitation Science)
├── علم الحديث (Hadith Sciences)
│   ├── رواية الحديث (Hadith Transmission — the texts themselves)
│   ├── دراية الحديث / مصطلح الحديث (Hadith Criticism — methodology)
│   └── علم الرجال / الجرح والتعديل (Narrator Criticism)
├── الفقه (Jurisprudence)
│   ├── الفقه المذهبي (School-specific rulings)
│   ├── الفقه المقارن (Comparative jurisprudence)
│   └── القواعد الفقهية (Legal maxims)
├── أصول الفقه (Legal Theory)
├── العقيدة / التوحيد (Creed/Theology)
└── التزكية / التصوف (Spiritual Purification)

علوم الآلة (Instrumental Sciences) — tools for understanding transmitted sciences
├── النحو (Syntax)
├── الصرف (Morphology)
├── البلاغة (Rhetoric: معاني, بيان, بديع)
├── المنطق (Logic)
├── أصول الفقه (also instrumental — overlaps both categories)
└── الإملاء والخط (Orthography)

العلوم التاريخية (Historical Sciences)
├── السيرة النبوية (Prophetic Biography)
├── التاريخ (General History/Chronicles)
├── التراجم / الطبقات (Biographical Dictionaries)
└── الأنساب (Genealogy)
```

---

## Per-Science Processing Guide

### 1. علم الحديث — Hadith Sciences

#### Signal Terminology
حدثنا, أخبرنا, عن, سمعت, رواه, أسنده, إسناد, متن الحديث, سند, صحيح, حسن, ضعيف, موضوع, مرفوع, موقوف, مقطوع, مرسل, متواتر, آحاد, غريب

#### Structural Patterns
- **Isnad-matn structure**: Every hadith has a chain (سند/إسناد) followed by the text (متن). The chain is a sequence of `عن فلان عن فلان` or `حدثنا فلان قال حدثنا فلان`.
- **Chapter organization**: Most collections organize by fiqh chapter (كتاب الطهارة, كتاب الصلاة, etc.)
- **Numbering**: Hadith are numbered sequentially within the collection. Some editions add cross-references.
- **Commentary integration**: Many hadith collections have embedded or interleaved commentary by the compiler.

#### Processing Implications for KR
- **Division tree**: Chapter (كتاب) → Section (باب) → Individual hadith. The باب heading often contains a fiqh ruling the compiler derives.
- **Excerpting**: Each hadith is a natural teaching unit. The isnad and matn should stay together. DO NOT split a hadith across excerpts.
- **Layer detection**: Some compilations (e.g., جامع الترمذي) interleave compiler comments with hadith — these are separate layers.
- **Attribution**: The COMPILER (e.g., البخاري) is the author. The NARRATOR of each hadith is metadata, not authorship.
- **Cross-references**: Hadith frequently reference other hadith in the same or other collections.

#### Common Misclassification Traps
- **أحاديث الأحكام** (hadith organized by rulings) is hadith_collection, NOT fiqh
- **تخريج** (hadith source tracing) is hadith methodology, NOT the hadith text itself
- **شرح حديث** (explanation of a single hadith) is Genre.SHARH with science=hadith, NOT hadith_collection
- A fiqh book that quotes many hadith is still fiqh — the science is determined by the author's PURPOSE, not the content quoted

---

### 2. التفسير — Quranic Exegesis

#### Signal Terminology
قوله تعالى, ﴿...﴾, سورة, آية, نزلت في, أسباب النزول, قراءة, وجه, إعراب الآية, معنى, تأويل, ناسخ, منسوخ

#### Structural Patterns
- **Verse-by-verse**: Primary structure follows the Quran's order (surah then ayah)
- **Multi-approach**: May combine linguistic analysis (إعراب), legal extraction (استنباط), narrative (قصص), and theological reflection
- **Quotation-heavy**: Extensively quotes Quran, hadith, companion opinions, and prior mufassirun
- **Layer integration**: Some tafsir (e.g., حاشية الجمل على الجلالين) are multi-layer commentary ON commentary

#### Processing Implications for KR
- **Division tree**: Surah → Ayah group → Discussion. The Quran's own structure IS the division tree.
- **Excerpting**: Each ayah discussion is a natural teaching unit. However, some discussions span multiple ayahs.
- **Quranic text preservation**: Quranic verses embedded in tafsir MUST be preserved exactly. Apply `quranic_text: true` tag. NEVER normalize, trim, or modify.
- **Attribution complexity**: The mufassir cites earlier scholars extensively. Each cited opinion needs attribution to its original source, not to the tafsir author.
- **Science scope**: `science_scope: ["tafsir"]` even when the tafsir discusses fiqh rulings derived from verses — the science is tafsir, not fiqh.

#### Common Misclassification Traps
- **أحكام القرآن** (legal rulings from Quran) is tafsir with fiqh focus, NOT fiqh
- **إعراب القرآن** (Quran parsing) is tafsir with nahw focus, NOT nahw
- A book that frequently quotes Quran verses is NOT tafsir unless it is organized by and explains verses

---

### 3. الفقه — Jurisprudence

#### Signal Terminology
يجب, يحرم, يستحب, يكره, يباح, مسألة, فرع, تنبيه, فائدة, الراجح, والصحيح, وعندنا, وقال أبو حنيفة/الشافعي/مالك/أحمد, دليلنا, ولنا

#### Structural Patterns
- **Chapter-section**: كتاب (major topic) → باب (sub-topic) → مسألة (specific ruling)
- **School-specific**: Each madhab has its own internal organization and terminology
- **Five-ruling framework**: Every action classified as واجب/فرض, مستحب/سنة, مباح, مكروه, حرام
- **Evidence citation**: Rulings backed by Quran, hadith, ijma', qiyas, often in that order
- **Conditions and exceptions**: شروط (conditions), أركان (pillars), واجبات (obligations), مبطلات (nullifiers)

#### Processing Implications for KR
- **Division tree**: كتاب → باب → فصل → مسألة. Very deep nesting is common (5+ levels).
- **Excerpting**: A مسألة (specific ruling) is the natural teaching unit. Include the evidence with the ruling.
- **School identification**: Critical metadata. Detect from: author's known madhab, terminology patterns (Hanafi uses يجوز/لا يجوز, Shafi'i uses الأصح/المذهب, Hanbali uses الصحيح/المذهب, Maliki uses المشهور/المعتمد).
- **Comparative detection**: If a fiqh text systematically presents multiple madhab opinions with وقال, وعند, وذهب, it is `fiqh_comparative` not school-specific.
- **Fatwa vs. systematic**: Fatawa are organized by question-answer, not systematic chapter structure.

#### Common Misclassification Traps
- **Fiqh rules (قواعد فقهية)** are a separate sub-genre from applied fiqh
- **أصول الفقه** is a DIFFERENT science (legal theory vs. applied law)
- A comparative text from one author doesn't become fiqh_comparative just because it mentions other opinions occasionally — it must be SYSTEMATIC comparison

---

### 4. أصول الفقه — Legal Theory (Usul al-Fiqh)

#### Signal Terminology
الأمر يقتضي الوجوب, العام والخاص, المطلق والمقيد, النسخ, الإجماع, القياس, الاستصحاب, سد الذرائع, المصلحة المرسلة, الدلالة, المنطوق, المفهوم, حجة

#### Structural Patterns
- **Principle-based**: Organized by methodological principle, not by legal topic
- **Abstract reasoning**: Discusses HOW to derive rulings, not specific rulings themselves
- **Definition-heavy**: Extensive حد (definitions) and تقسيم (categorizations)
- **Evidence hierarchies**: Ordered discussion of evidence types (Quran, Sunnah, Ijma', Qiyas, secondary sources)

#### Processing Implications for KR
- **Division tree**: Major methodology section → Principle → Sub-principles → Examples
- **Excerpting**: Each principle with its examples forms a teaching unit. Abstract principles without examples are INCOMPLETE teaching units.
- **Science scope**: `science_scope: ["usul_al_fiqh"]` — distinct from fiqh
- **Cross-science references**: Usul texts cite nahw (for Arabic interpretation rules), hadith methodology (for sunnah evaluation), and logic (for reasoning structures)

#### Common Misclassification Traps
- **Usul al-fiqh ≠ fiqh.** Usul discusses methodology; fiqh applies it. A text about "how to determine that prayer is obligatory" is usul; "prayer is obligatory" is fiqh.
- مقاصد الشريعة (higher objectives of Islamic law) is usul_al_fiqh, not a separate science

---

### 5. العقيدة / التوحيد — Creed and Theology

#### Signal Terminology
التوحيد, الإيمان, أركان الإيمان, صفات الله, القدر, الشفاعة, الكفر, الإرجاء, المعتزلة, الأشاعرة, أهل السنة والجماعة, منهج, عقيدة, اعتقاد

#### Structural Patterns
- **Creedal statement**: Many aqidah texts start with a concise creed (e.g., العقيدة الطحاوية) then explain each point
- **Polemical**: Often structured as refutation of opposing views (رد على)
- **Categorical**: Organized by creedal topics: توحيد الربوبية, توحيد الألوهية, الأسماء والصفات, اليوم الآخر, القدر
- **Sect-aware**: Positions are often framed relative to theological schools (أهل السنة vs المعتزلة vs الأشاعرة)

#### Processing Implications for KR
- **Division tree**: Creedal topic → Sub-topic → Position → Evidence → Counter-argument
- **Excerpting**: Each creedal position with its evidence is a teaching unit
- **Sensitivity**: Theological positions vary between schools. KR must RECORD the position, NOT evaluate it. Attribution of theological positions to specific scholars is HIGH-RISK for T-2.
- **Layer detection**: Many aqidah works are commentaries on creedal mutun (e.g., شرح العقيدة الواسطية)

#### Common Misclassification Traps
- A book about names and attributes of God is aqidah, not tafsir, even if it cites many Quran verses
- كتاب الإيمان chapters within hadith collections are hadith, not aqidah
- رسالة in aqidah is still aqidah, not generic risalah

---

### 6. النحو — Arabic Syntax

#### Signal Terminology
الفاعل, المفعول به, المبتدأ, الخبر, الحال, التمييز, الإعراب, مرفوع, منصوب, مجرور, مبني, معرب, الجملة الاسمية, الجملة الفعلية, العامل, المعمول

#### Structural Patterns
- **Grammar topic organization**: Parts of speech → case theory → sentence types → dependent clauses
- **Example-heavy**: Every rule illustrated with Quran verses, hadith, poetry (شواهد)
- **Multi-layer tradition**: Extremely deep commentary chains (matn → sharh → hashiyah → ta'liqat, up to 5+ layers)

#### Processing Implications for KR
- **Division tree**: Grammar section → Rule → Sub-rules → Examples/Exceptions
- **Excerpting**: Each grammar rule with its examples forms a teaching unit. Examples (شواهد) MUST stay with their rules.
- **Poetry preservation**: شواهد نحوية (grammatical evidence verses) must preserve meter and diacritics exactly
- **Layer separation**: Nahw commentary traditions are the most deeply layered in all Islamic sciences. Ibn Aqil's sharh on the Alfiyyah, then al-Sabban's hashiyah on al-Ashmuni's sharh — each layer must be correctly attributed.

---

### 7. الصرف — Arabic Morphology

#### Signal Terminology
الميزان الصرفي, وزن, فعل/يفعل/افعل, الأبواب, المجرد, المزيد, التصريف, الإبدال, الإعلال, الإدغام, اسم الفاعل, اسم المفعول, المصدر

#### Structural Patterns
- **Pattern-based**: Organized by verb patterns (أوزان) and derivation rules
- **Tabular**: Extensive conjugation tables and pattern charts
- **Technical**: Highly technical Arabic terminology with precise definitions

#### Processing Implications for KR
- **Division tree**: Verb type → Pattern → Derivation rules → Irregular forms
- **Tables**: Sarf texts contain conjugation tables that must be preserved structurally, not flattened into prose
- **Diacritics**: CRITICAL in sarf. The difference between فَعَلَ and فُعِلَ is the entire meaning. Diacritic loss is catastrophic.
- **Science scope**: Often combined with nahw in a single curriculum but distinct — sarf = word-internal, nahw = word-external

---

### 8. البلاغة — Rhetoric

#### Signal Terminology
المعاني, البيان, البديع, التشبيه, الاستعارة, المجاز, الكناية, الحقيقة, الفصاحة, البلاغة, الإسناد, الخبر والإنشاء

#### Structural Patterns
- **Three-branch division**: علم المعاني (meaning), علم البيان (expression), علم البديع (embellishment)
- **Literary examples**: Extensive quotation of Quran, hadith, and poetry as examples of rhetorical devices
- **Analytical**: Each device is defined, categorized, then illustrated

#### Processing Implications for KR
- **Division tree**: Branch → Device → Sub-types → Examples
- **Excerpting**: Each rhetorical device with examples is a teaching unit
- **Literary sensitivity**: The examples ARE the content — they must preserve all stylistic features
- **Science scope**: `science_scope: ["balagha"]` — not adab (literature), not nahw (syntax)

---

## Cross-Science Processing Rules

### Rule 1: Science Determines Processing Strategy
The identified science of a text determines the division tree structure, excerpting boundaries, and layer separation approach. Do NOT apply fiqh processing patterns to a hadith collection or vice versa.

### Rule 2: Multi-Science Texts
Some texts span multiple sciences. Examples:
- **أحكام القرآن** → primary: tafsir, secondary: fiqh
- **فتح الباري** → primary: hadith (sharh of Bukhari), secondary: fiqh, aqidah, nahw
- **زاد المعاد** → primary: sirah, secondary: fiqh (extensive legal discussions)
Assign `science_scope` as a list, ordered by dominance. The PRIMARY science determines processing strategy.

### Rule 3: Commentary Inherits Base Text Science
A sharh on a nahw matn is science=nahw, not a separate genre. The science follows the BASE TEXT, not the commentary style. Exception: if the sharh significantly expands into another science (e.g., a hashiyah on a nahw text that primarily discusses usul), flag for human review.

### Rule 4: Terminology Meaning Shifts Between Sciences
The same word means different things in different sciences:
- **حكم**: In fiqh = legal ruling. In nahw = grammatical governance. In aqidah = divine decree.
- **عامل**: In nahw = grammatical governor. In fiqh = general principle. In logic = cause.
- **أصل**: In usul = foundational source. In fiqh = default ruling. In nahw = underlying form.
- **فرع**: In fiqh = derived ruling. In usul = secondary source. In nahw = derived form.
- **صحيح**: In hadith = authenticated (grade). In fiqh = the preponderant view. In nahw = grammatically correct.
Always interpret terminology IN THE CONTEXT of the text's science, not generically.

### Rule 5: Historical Period Affects Classification
- Pre-5th century AH: Sciences less differentiated. A single work may freely mix nahw, tafsir, and fiqh.
- 5th-8th century AH: Golden age of specialization. Clear genre boundaries. This period produced the canonical texts.
- Post-8th century AH: Commentary tradition dominates. Most works are sharh/hashiyah on earlier texts.
- Modern (post-1300 AH): Academic format, sometimes with Western organizational influence. May not follow traditional chapter structure.

Processing should adapt to the historical period of the text.
