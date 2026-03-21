# Phase E Book Selection

**Total books selected:** 70
**Date:** 2026-03-21
**Selection criteria:** 6 strategic categories targeting Phase D blind spots
**Excluded:** 204 Phase D books (from MASTER_MANIFEST.json)

## Summary

| Category | Count | Purpose |
|----------|-------|---------|
| Genre Diversity Gaps | 25 | Fill Shamela categories with ≤2 Phase D books to reach ≥3 each |
| Multi-Layer Candidates | 15 | Test LLM is_multi_layer vs normalization auto-detection across diverse ratios |
| Source Extraction Anomalies | 10 | Stress-test LLM inference on books with sparse extraction metadata |
| Extreme Metrics | 8 | Test pipeline at scale extremes (largest, smallest, highest diacritics) |
| Formerly Zero-Content | 7 | Verify LLM metadata works on hadith compilations fixed in Task 2 |
| Previously Unknown | 5 | Maximum novelty — books not in any prior results |

## Genre Diversity Gaps

| # | Book | Shamela Category | Rationale |
|---|------|-----------------|-----------|
| 1 | القسم الثاني من المعجم الأوسط للطبراني | (الطبراني) | Fills thin category '(الطبراني)' (1 PD books → needs ≥3) |
| 2 | أخبار قبائل الخزرج | الأنساب | Fills thin category 'الأنساب' (0 PD books → needs ≥3) |
| 3 | تسمية الإخوة الذين روي عنهم الحديث.htm | الأنساب | Fills thin category 'الأنساب' (0 PD books → needs ≥3) |
| 4 | نهاية الأرب في معرفة أنساب العرب.htm | الأنساب | Fills thin category 'الأنساب' (0 PD books → needs ≥3) |
| 5 | أثر الدعوة الوهابية في الإصلاح الديني والعمراني في جزيرة العرب وغيرها.htm | التاريخ | Fills thin category 'التاريخ' (2 PD books → needs ≥3) |
| 6 | آيات متشابهات الألفاظ في القرآن الكريم وكيف التمييز بينها.htm | التجويد والقراءات | Fills thin category 'التجويد والقراءات' (0 PD books → needs ≥3) |
| 7 | الوافي في كيفية ترتيل القرآن الكريم.htm | التجويد والقراءات | Fills thin category 'التجويد والقراءات' (0 PD books → needs ≥3) |
| 8 | ورد الطائف في شرح روضة الطرائف في رسم المصحف.htm | التجويد والقراءات | Fills thin category 'التجويد والقراءات' (0 PD books → needs ≥3) |
| 9 | أحاديث القصاص - ت الصباغ.htm | التخريج والأطراف | Fills thin category 'التخريج والأطراف' (0 PD books → needs ≥3) |
| 10 | تحفة الأبرار بنكت الأذكار للنووي.htm | التخريج والأطراف | Fills thin category 'التخريج والأطراف' (0 PD books → needs ≥3) |
| 11 | نقد «نصوص حديثية في الثقافة العامة».htm | التخريج والأطراف | Fills thin category 'التخريج والأطراف' (0 PD books → needs ≥3) |
| 12 | أبراج الزجاج في سيرة الحجاج.htm | التراجم والطبقات | Fills thin category 'التراجم والطبقات' (1 PD books → needs ≥3) |
| 13 | تاريخ بغداد - ت بشار | التراجم والطبقات | Fills thin category 'التراجم والطبقات' (1 PD books → needs ≥3) |
| 14 | آداب الأكل.htm | الرقائق والآداب والأذكار | Fills thin category 'الرقائق والآداب والأذكار' (0 PD books → needs ≥3) |
| 15 | تعس عبد الشهوات.htm | الرقائق والآداب والأذكار | Fills thin category 'الرقائق والآداب والأذكار' (0 PD books → needs ≥3) |
| 16 | يقظة أولي الاعتبار.htm | الرقائق والآداب والأذكار | Fills thin category 'الرقائق والآداب والأذكار' (0 PD books → needs ≥3) |
| 17 | آداب الحسبة.htm | السياسة الشرعية والقضاء | Fills thin category 'السياسة الشرعية والقضاء' (0 PD books → needs ≥3) |
| 18 | النظام القضائي في الفقه الإسلامي.htm | السياسة الشرعية والقضاء | Fills thin category 'السياسة الشرعية والقضاء' (0 PD books → needs ≥3) |
| 19 | وظيفة القضاء في التعامل مع الإرهاب.htm | السياسة الشرعية والقضاء | Fills thin category 'السياسة الشرعية والقضاء' (0 PD books → needs ≥3) |
| 20 | أخلاق النبي وآدابه - أبو الشيخ الأصبهاني | السيرة النبوية | Fills thin category 'السيرة النبوية' (0 PD books → needs ≥3) |
| 21 | جمع الوسائل في شرح الشمائل | السيرة النبوية | Fills thin category 'السيرة النبوية' (0 PD books → needs ≥3) |
| 22 | يوم في بيت الرسول.htm | السيرة النبوية | Fills thin category 'السيرة النبوية' (0 PD books → needs ≥3) |
| 23 | [شرح] تسهيل العقيدة الإسلامية - ط ٢ | العقيدة | Fills thin category 'العقيدة' (1 PD books → needs ≥3) |
| 24 | تحذير المسلمين من السب والاستهزاء بالدين.htm | العقيدة | Fills thin category 'العقيدة' (1 PD books → needs ≥3) |
| 25 | أحاديث مختارة من موضوعات الجورقاني وابن الجوزي.htm | العلل والسؤلات الحديثية | Fills thin category 'العلل والسؤلات الحديثية' (0 PD books → needs ≥3) |

## Multi-Layer Candidates

| # | Book | Shamela Category | Rationale |
|---|------|-----------------|-----------|
| 1 | تدارك بقية العمر في تدبير سورة النصر | التفسير | Multi-layer low ratio: 10.0% (3/30 units) |
| 2 | شرح الوصية الكبرى لابن تيمية - الراجحي | العقيدة | Multi-layer low ratio: 13.6% (3/22 units) |
| 3 | فتح الباقي على منظومة المراقي | أصول الفقه | Multi-layer low ratio: 19.2% (53/276 units) |
| 4 | السواك وسنن الفطرة - المقدم | مسائل فقهية | Multi-layer low ratio: 23.5% (4/17 units) |
| 5 | أصول أهل السنة والجماعة | العقيدة | Multi-layer low ratio: 33.3% (3/9 units) |
| 6 | ألقاب الشعراء ومن يعرف منهم بأمه - ضمن نوادر المخطوطات | التراجم والطبقات | Multi-layer medium ratio: 50.0% (16/32 units) |
| 7 | الفوائد الأصولية - ضمن «آثار المعلمي» | أصول الفقه | Multi-layer medium ratio: 52.4% (11/21 units) |
| 8 | حصول المأمول بشرح ثلاثة الأصول | العقيدة | Multi-layer medium ratio: 58.3% (119/204 units) |
| 9 | شرح العقيدة الطحاوية - ناصر العقل | العقيدة | Multi-layer medium ratio: 62.5% (5/8 units) |
| 10 | إرشاد العباد إلى معاني لمعة الاعتقاد | العقيدة | Multi-layer medium ratio: 67.2% (90/134 units) |
| 11 | أصل الزراري شرح صحيح البخاري - مخطوط | شروح الحديث | Multi-layer high ratio: 85.5% (641/750 units) |
| 12 | مزيد فتح الباري بشرح البخاري - مخطوط | شروح الحديث | Multi-layer high ratio: 89.9% (508/565 units) |
| 13 | حاشية الخلوتي على منتهى الإرادات | الفقه الحنبلي | Multi-layer high ratio: 91.5% (473/517 units) |
| 14 | السيل الجرار المتدفق على حدائق الأزهار | الفقه العام | Multi-layer high ratio: 93.6% (1009/1078 units) |
| 15 | حاشية الصبان على شرح الأشمونى لألفية ابن مالك | النحو والصرف | Multi-layer high ratio: 97.0% (419/432 units) |

## Source Extraction Anomalies

| # | Book | Shamela Category | Rationale |
|---|------|-----------------|-----------|
| 1 | أحاديث المناديلي.htm | كتب السنة | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 2 | أحاديث منصور بن عمار.htm | كتب السنة | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 3 | أحاديث يزيد بن أبي حبيب المصري - ضمن «أحاديث الشيوخ الكبار».htm | كتب السنة | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 4 | أحكام النساء - من «الجامع» للخلال.htm | الفقه الحنبلي | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 5 | أحكام عصاة المؤمنين من كلام شيخ الإسلام ابن تيمية - كجك.htm | مسائل فقهية | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 6 | أخبار في النحو = أخبار النحويين - أبو طاهر بن أبي هاشم - ت الدالي.htm | كتب السنة | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 7 | أربعون حديثا عن أربعين شيخا في أربعين لابن المقرب.htm | كتب السنة | Sparse metadata: missing_author_name_raw — tests LLM inference from limited extraction |
| 8 | آداب العلماء والمتعلمين.htm | الرقائق والآداب والأذكار | Sparse metadata: missing_publisher_and_edition — tests LLM inference from limited extraction |
| 9 | آداب العمرة وأحكامها - حطيبة | الفقه العام | Sparse metadata: missing_publisher_and_edition — tests LLM inference from limited extraction |
| 10 | آراء السمعاني العقدية.htm | العقيدة | Sparse metadata: missing_publisher_and_edition — tests LLM inference from limited extraction |

## Extreme Metrics

| # | Book | Shamela Category | Rationale |
|---|------|-----------------|-----------|
| 1 | الجامع الصغير وزيادته | كتب السنة | Largest book: 14,587 content units — tests pipeline at scale |
| 2 | الشرح الصوتي لزاد المستقنع - ابن عثيمين | الفقه الحنبلي | Largest book: 8,426 content units — tests pipeline at scale |
| 3 | موسوعة الرقائق والأدب - ياسر الحمداني | الرقائق والآداب والأذكار | Largest book: 8,319 content units — tests pipeline at scale |
| 4 | الروض الأنيق في فضل الصديق | التراجم والطبقات | Smallest non-trivial: 3 content units — tests minimal input |
| 5 | الطبقات للنسائي | التراجم والطبقات | Smallest non-trivial: 3 content units — tests minimal input |
| 6 | الفسخ بالإعسار - ضمن «آثار المعلمي» | مسائل فقهية | Smallest non-trivial: 3 content units — tests minimal input |
| 7 | منتهى الإرادات في جمع المقنع مع التنقيح وزيادات - ت التركي | الفقه الحنبلي | Highest diacritic density: 40.1% (85,105/212,094) — tests diacritic handling |
| 8 | قواعد ابن رجب - ط الخانجي | علوم الفقه والقواعد الفقهية | Highest diacritic density: 39.9% (607,258/1,521,261) — tests diacritic handling |

## Formerly Zero-Content

| # | Book | Shamela Category | Rationale |
|---|------|-----------------|-----------|
| 1 | الأول من الخلعيات | كتب السنة | Formerly zero-content (الخلعيات vol 1 (الأول)) — fixed in Task 2, verify LLM inference works |
| 2 | الخامس عشر من الخلعيات | كتب السنة | Formerly zero-content (الخلعيات vol 15 (الخامس عشر)) — fixed in Task 2, verify LLM inference works |
| 3 | الرابع من معجم شيوخ الدمياطي | كتب السنة | Formerly zero-content (معجم شيوخ الدمياطي vol 4) — fixed in Task 2, verify LLM inference works |
| 4 | الثاني من المصباح في عيون الصحاح | كتب السنة | Formerly zero-content (المصباح في عيون الصحاح vol 2) — fixed in Task 2, verify LLM inference works |
| 5 | حديث ذي النون المصري | كتب السنة | Formerly zero-content (Individual hadith compilation) — fixed in Task 2, verify LLM inference works |
| 6 | فوائد ابن دحيم | كتب السنة | Formerly zero-content (Individual hadith compilation) — fixed in Task 2, verify LLM inference works |
| 7 | حديث عباس الترقفي | كتب السنة | Formerly zero-content (Individual hadith compilation) — fixed in Task 2, verify LLM inference works |

## Previously Unknown

| # | Book | Shamela Category | Rationale |
|---|------|-----------------|-----------|
| 1 | آثار حجج التوحيد في مؤاخذة العبيد | العقيدة | Previously unknown — max novelty. Shamela category: العقيدة |
| 2 | التقصي لما في الموطأ من حديث النبي صلى الله عليه وسلم = تجريد التمهيد لما في الموطأ من المعاني والأسانيد | شروح الحديث | Previously unknown — max novelty. Shamela category: شروح الحديث |
| 3 | المسلم في عالم الاقتصاد | كتب عامة | Previously unknown — max novelty. Shamela category: كتب عامة |
| 4 | حكم الغناء في مذهب المالكية | مسائل فقهية | Previously unknown — max novelty. Shamela category: مسائل فقهية |
| 5 | فقه الصيام والحج من دليل الطالب | الفقه الحنبلي | Previously unknown — max novelty. Shamela category: الفقه الحنبلي |
