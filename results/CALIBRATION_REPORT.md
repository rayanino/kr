# Normalization Calibration Report

**Generated:** 2026-03-21 20:05 UTC
**Input:** `results\normalization_sweep_v2\corpus_sweep.jsonl`
**Total entries:** 7475
**OK books:** 7475 | **Crashes:** 0

---
## B.1: Corpus Statistics

| Metric | Value |
| ------ | ----- |
| Total books processed | 7,475 |
| OK | 7,475 (100.0%) |
| CRASH | 0 (0.0%) |
| Total content units | 2,059,924 |
| Total raw pages | 2,069,347 |

**Processing time:**

| Metric | Value |
| ------ | ----- |
| Total | 1099s (18.3 min) |
| Mean per-book | 0.15s |
| Median | 0.08s |
| P95 | 0.45s |
| Max | 9.16s |

**Book size (content units):**

| Metric | Value |
| ------ | ----- |
| Mean | 275.58 |
| Median | 168 |
| P95 | 714.00 |
| Max | 14,587 |

## B.2: Multi-Layer Detection at Scale

Books with `auto_upgraded_multi == true`: **401** (5.4%)

> Note: `auto_upgraded_multi` is set when `multi_layer_units > 0` — it indicates
> the presence of any multi-layer content units, not necessarily a metadata upgrade.

**Multi-layer units distribution (auto-upgraded books):**

| Metric | Value |
| ------ | ----- |
| Mean | 76.87 |
| Median | 17 |
| P95 | 393.30 |
| Max | 1,186 |

**Suspected false positives** (multi_layer_units > 50% of content_units): **85** (21.2% of auto-upgraded)

> Caveat: The JSONL does not record per-unit detection method. The bracket-detection
> filter from NEXT.md could not be applied. This heuristic uses the 50% threshold only.

**Top 20 auto-upgraded books by multi_layer_units:**

| Book | Multi-layer units | Total units | Ratio |
| ---- | ----------------- | ----------- | ----- |
| الشرح الصوتي لزاد المستقنع - ابن عثيمين | 1,186 | 8,426 | 14.1% |
| السيل الجرار المتدفق على حدائق الأزهار | 1,009 | 1,078 | 93.6% |
| حاشية الطحطاوي على مراقي الفلاح شرح نور الإيضاح | 788 | 818 | 96.3% |
| أصل الزراري شرح صحيح البخاري - مخطوط | 641 | 750 | 85.5% |
| التمهيد لشرح كتاب التوحيد | 610 | 610 | 100.0% |
| فتح الرحمن بشرح زبد ابن رسلان | 600 | 924 | 64.9% |
| حاشية الصاوي على الشرح الصغير ط الحلبي | 530 | 530 | 100.0% |
| الهداية إلى أوهام الكفاية | 522 | 594 | 87.9% |
| مزيد فتح الباري بشرح البخاري - مخطوط | 508 | 565 | 89.9% |
| تيسير العزيز الحميد في شرح كتاب التوحيد الذى هو حق الله على العبيد | 490 | 700 | 70.0% |
| حاشية الخلوتي على منتهى الإرادات | 473 | 517 | 91.5% |
| تفسير الكشاف - ومعه الانتصاف ومشاهد الإنصاف والكافي الشاف | 466 | 697 | 66.9% |
| الدلائل والإشارات على أخصر المختصرات | 442 | 601 | 73.5% |
| مختصر خليل - ومعه شفاء الغليل في حل مقفل خليل | 436 | 480 | 90.8% |
| منحة السلوك في شرح تحفة الملوك | 432 | 463 | 93.3% |
| حاشية الصبان على شرح الأشمونى لألفية ابن مالك | 419 | 432 | 97.0% |
| إعراب القرآن العظيم المنسوب لزكريا الانصارى | 412 | 415 | 99.3% |
| المداوي لعلل الجامع الصغير وشرحي المناوي | 410 | 642 | 63.9% |
| حاشية الشهاب على تفسير البيضاوي = عناية القاضي وكفاية الراضي | 399 | 422 | 94.5% |
| تطريز رياض الصالحين | 394 | 1,090 | 36.1% |

## B.3: Division Tree

**Division count distribution:**

| Metric | Value |
| ------ | ----- |
| Mean | 14.00 |
| Median | 1 |
| P95 | 67.00 |
| Max | 1,924 |

**Books with zero divisions:** 0 (0.0%)

**Books with division overlap warnings:** 1148 (15.4%)

| Source | Overlap rate |
| ------ | ------------ |
| 63-fixture evaluation | 14.0% |
| Full corpus (this report) | 15.4% |

## B.4: Boundary Continuity

**Mean BC coverage:** 98.0%

**Aggregate BC type distribution:**

| Type | Count | Percentage |
| ---- | ----- | ---------- |
| mid_sentence | 959,990 | 46.8% |
| section_break | 541,911 | 26.4% |
| mid_paragraph | 524,397 | 25.6% |
| mid_argument | 25,845 | 1.3% |
| unknown | 66 | 0.0% |

**Books with 0% BC coverage:** 3 (0.0%)

## B.5: Content Flags

| Flag | Total pages | % of corpus pages |
| ---- | ----------- | ----------------- |
| has_hadith | 784,946 | 38.1% |
| has_quran | 416,847 | 20.2% |
| has_verse | 326,028 | 15.8% |

**Books with zero content flags:** 43 (0.6%)

## B.6: Arabic Text Quality

**Arabic ratio distribution:**

| Metric | Value |
| ------ | ----- |
| Mean | 80.1% |
| Median | 79.8% |
| P5 (bottom 5%) | 74.8% |
| Min | 51.2% |

**Books with arabic_ratio < 70%:** 58 (0.8%)

Top 20 by lowest ratio:

| Book | Arabic ratio |
| ---- | ------------ |
| معجم شيوخ الطبري | 51.2% |
| سنن سعيد بن منصور - بداية التفسير - ت الحميد | 54.6% |
| تخريج أحاديث شواهد التوضيح وملاحظات على طبعة فؤاد عبد الباقي - ضمن «آثار المعلمي» | 55.4% |
| أسامي الضعفاء - أبو زرعة الرازي - ت الأزهري | 56.3% |
| مصباح الأريب في تقريب الرواة الذين ليسوا في تقريب التهذيب | 57.2% |
| تنبيهات على الجزء الأول من معجم الأدباء ط أحمد فريد الرفاعي. - ضمن «آثار المعلمي» | 58.3% |
| مختصر تلخيص الذهبي لمستدرك الحاكم | 58.5% |
| أصل صفة صلاة النبي صلى الله عليه وسلم | 60.7% |
| فائت تسهيل السابلة | 61.5% |
| تاريخ ابن يونس المصرى | 62.4% |
| بيان خطا البخاري في تاريخه | 62.6% |
| فوائد في كتاب «العلل» لابن أبي حاتم - ضمن «آثار المعلمي» | 62.6% |
| معجم المؤلفين | 63.5% |
| المجرد في أسماء رجال سنن ابن ماجه | 64.0% |
| التبيان في تفسير غريب القرآن | 64.0% |
| ضبط من غبر فيمن قيده ابن حجر | 64.3% |
| المختلطين للعلائي | 64.7% |
| شرح القواعد الأربع | 64.8% |
| تسمية الإخوة الذين روي عنهم الحديث | 64.9% |
| تسمية من روي عنه من أولاد العشرة - ت الجوابرة | 64.9% |

**Diacritic density (diacritics per 1,000 chars):**

| Metric | Value |
| ------ | ----- |
| Mean | 116.24 |
| Median | 51.47 |
| P95 | 377.12 |

**Books with zero diacritics:** 43 (0.6%)

## B.7: Warning Patterns at Scale

**Total warnings across corpus:** 15,413

**Warning type distribution:**

| Warning type | Count | Percentage |
| ------------ | ----- | ---------- |
| char_run | 8,260 | 53.6% |
| low_arabic_ratio | 4,530 | 29.4% |
| division_overlap | 2,544 | 16.5% |
| other | 79 | 0.5% |

**Top 10 most-warned books:**

| Book | Warning count |
| ---- | ------------- |
| موسوعة الرقائق والأدب - ياسر الحمداني | 1,812 |
| تفسير الجلالين | 692 |
| شرح الزرقاني على الموطأ | 482 |
| ديوان الضعفاء | 393 |
| غاية المريد شرح كتاب التوحيد | 339 |
| إحكام الأحكام شرح عمدة الأحكام | 330 |
| القول المفيد على كتاب التوحيد | 249 |
| أصل صفة صلاة النبي صلى الله عليه وسلم | 226 |
| شرح التصريح على التوضيح أو التصريح بمضمون التوضيح في النحو | 223 |
| كتاب التوحيد وقرة عيون الموحدين في تحقيق دعوة الأنبياء والمرسلين | 222 |

## B.8: Passaging Contract Alignment

| Check | Failures | Percentage |
| ----- | -------- | ---------- |
| check4_count_match | 0 | 0.0% |
| check5 (ordered + no_gaps) | 0 | 0.0% |
| check6_division_consistent | 1,148 | 15.4% |

**Books passing ALL checks:** 6327 (84.6%)


## B.9: Page Loss

> Note: `page_loss = abs(content_units - raw_page_divs)`. A value of 1 typically
> represents the Shamela table-of-contents page (expected, not data loss).

**Page loss distribution:**

| Metric | Value |
| ------ | ----- |
| Mean | 1.26 |
| Median | 1 |
| P95 | 2.00 |
| Max | 62 |

**Books with page_loss == 0:** 0 (0.0%)

**Books with page_loss <= 1 (near-perfect):** 5913 (79.1%)

**Books with page_loss > 5:** 25

| Book | Page loss |
| ---- | --------- |
| التهذيب في اختصار المدونة | 62 |
| تفسير ابن عاشور التحرير والتنوير | 36 |
| المختصر المفيد في عقائد أئمة التوحيد | 22 |
| أجنحة المكر الثلاثة | 19 |
| أدب الاختلاف في الإسلام | 13 |
| مصباح الظلام في الرد على من كذب الشيخ الإمام ونسبه إلى تكفير أهل الإيمان والإسلام | 12 |
| مطلع الأنوار ونزهة البصائر والأبصار | 12 |
| التسوية بين حدثنا وأخبرنا | 11 |
| طبقات الشافعيين | 11 |
| جمع القرآن - دراسة تحليلية لمروياته | 10 |
| التضمين النحوي في القرآن الكريم | 9 |
| الحاكم الجشمي ومنهجه في التفسير | 9 |
| اللؤلؤ والمرجان فيما اتفق عليه الشيخان | 9 |
| مؤتمر النجف = الحجج القطعية لاتفاق الفرق الإسلامية | 9 |
| آراء ابن الجوزي التربوية | 8 |
| تاج التراجم في طبقات الحنفية | 8 |
| قادة الغرب يقولون دمروا الإسلام أبيدوا أهله | 8 |
| الأصول العلمية للدعوة السلفية | 7 |
| التوهم في وصف أحوال الآخرة | 7 |
| رمي الجمرات في ضوء الكتاب والسنة وآثار الصحابة رضي الله عنهم | 7 |
| رياض الصالحين - ت الفحل | 7 |
| متن الشاطبية = حرز الأماني ووجه التهاني في القراءات السبع | 7 |
| رواية صحيح مسلم من طريق ابن ماهان مقارنة برواية ابن سفيان | 6 |
| فتح رب البرية شرح المقدمة الجزرية في علم التجويد | 6 |
| مفيد الأنام ونور الظلام في تحرير الأحكام لحج بيت الله الحرام | 6 |
