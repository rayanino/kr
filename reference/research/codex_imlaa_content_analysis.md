# Imlaa Deep Content Analysis

## Scope Note
- Source corpus only: Stage 1 retained imlaa Shamela books
- Analyzed books: top retained books by retained-heading richness, capped at 3
- Summary statistics below are computed over the deep-analyzed imlaa chapters only

## قواعد الإملاء
- File path: `/mnt/c/Users/Rayane/Desktop/kr/shamela-export-samples/قواعد الإملاء.htm`
- Total heading count: 43
- Stage 1 retained heading count: 16
- Major chapter headings:
  1. الْبَابُ الْأَوَّلُ — الهمزة
  2. الْبَابُ الثَّانِي — الألف اللينة
  3. الْبَابُ الثَّالِثُ — الزيادة في الكتابة
  4. الْبَابُ الرَّابِعُ — الحذف من الكتابة
  5. الْبَابُ الْخَامِسُ — الوصل والفصل
  6. التاء المربوطة والتاء المفتوحة
  7. ملحق تدريبي: رسم الهمزة والألف
- Excluded front matter:
  - بسم الله الرحمن الرحيم
- Hierarchical outline:
  - الْبَابُ الْأَوَّلُ — الهمزة [major]
    - الْهَمْزَةُ أَوَّلُ الْكَلِمَةِ [recommended: attested_structural_subtopic] → الهمزة في أول الكلمة
    - الْهَمْزَةُ آخِرُ الْكَلِمَةِ [recommended: attested_structural_subtopic] → الهمزة في آخر الكلمة
    - الْهَمْزَةُ وَسَطَ الْكَلِمَةِ [recommended: attested_structural_subtopic] → الهمزة في وسط الكلمة
  - الْبَابُ الثَّانِي — الألف اللينة [major]
    - الْأَلِفُ اللَّيِّنَةُ وَسَطًا [recommended: attested_structural_subtopic] → الألف اللينة في وسط الكلمة
    - الْأَلِفُ اللَّيِّنَةُ طَرَفًا [recommended: attested_structural_subtopic] → الألف اللينة في آخر الكلمة
    - مَعْرِفَةُ الْوَاوَيّ وَالْيَائَيّ [max_only: fine_grained_but_unstable] → معرفة الأصل الواوي واليائي
    - الْأَلِفُ الْمُبَدْلَةُ مِنْ يَاءِ الْمُتَكَلِّمِ [excluded: chapter_label_or_blocked_subcase]
    - الْأَلِفُ الْمُبَدْلَةُ مِنْ نُونِ التَّوْكِيدِ الْخَفِيفَةِ [excluded: qramatic_or_language]
    - الْأَلِفُ الْمُبَدْلَةُ مِنْ نُونِ إِذَنْ [excluded: chapter_label_or_blocked_subcase]
  - الْبَابُ الثَّالِثُ — الزيادة في الكتابة [major]
    - زِيادَةُ الْأَلِفِ [max_only: fine_grained_rule_local_subcase] → زيادة الألف
    - زِيَادَةُ الْوَاوِ [max_only: fine_grained_rule_local_subcase] → زيادة الواو
  - الْبَابُ الرَّابِعُ — الحذف من الكتابة [major]
    - نَقْصُ الْأَلِفِ أَوَلًا [max_only: fine_grained_rule_local_subcase] → نقص الألف أول الكلمة
    - نَقْصُ الْأَلِفِ وَسَطًا [max_only: fine_grained_rule_local_subcase] → نقص الألف وسط الكلمة
    - نَقْصُ الْأَلِفِ آخِرً [max_only: fine_grained_rule_local_subcase] → نقص الألف آخر الكلمة
    - نَقْصُ أَلْ [max_only: fine_grained_rule_local_subcase] → نقص أل
    - نَقْصُ الْوَاوِ [max_only: fine_grained_rule_local_subcase] → نقص الواو
    - نَقْصُ الْيَاءِ [max_only: fine_grained_rule_local_subcase] → نقص الياء
    - نَقْصُ النُّونِ [max_only: fine_grained_rule_local_subcase] → نقص النون
    - النَّقْصُ لِلْرَمْزِ [max_only: fine_grained_rule_local_subcase] → النقص للرمز
  - الْبَابُ الْخَامِسُ — الوصل والفصل [major]
    - وَصْلُ (مَنْ) بِمَا قَبْلَهَا [max_only: token_level_joining_case] → وصل من بما قبلها
    - وَصْلُ (مَا) بِمَا قَبْلَهَا [max_only: token_level_joining_case] → وصل ما بما قبلها
    - وَصْلُ (لَا) بِمَا قَبْلَهَا [max_only: token_level_joining_case] → وصل لا بما قبلها
    - فَصْل [max_only: token_level_joining_case] → الفصل
  - التاء المربوطة والتاء المفتوحة [major]
  - ملحق تدريبي: رسم الهمزة والألف [major]
    - أولا: الهمزة [excluded: appendix_section_label]
      - الهمزة أول الكلمة: حقيقة أو حكما [recommended: appendix_supports_hamza_subtopic] → الهمزة في أول الكلمة
      - الهمزة وسط الكلمة [recommended: appendix_supports_hamza_subtopic] → الهمزة في وسط الكلمة
      - الهمزة آخر الكلمة [recommended: appendix_supports_hamza_subtopic] → الهمزة في آخر الكلمة
    - ثانيا: الألف اللينة [excluded: appendix_section_label]
      - الألف المتوسطة [recommended: appendix_supports_alif_subtopic] → الألف اللينة في وسط الكلمة
      - الألف المتطرفة [recommended: appendix_supports_alif_subtopic] → الألف اللينة في آخر الكلمة
- Heading counts per major chapter:
  - الْبَابُ الْأَوَّلُ — الهمزة: 4 title spans; 3 orthography-relevant spans; 3 max possible leaves; 3 recommended stable leaves
  - الْبَابُ الثَّانِي — الألف اللينة: 7 title spans; 3 orthography-relevant spans; 3 max possible leaves; 2 recommended stable leaves
  - الْبَابُ الثَّالِثُ — الزيادة في الكتابة: 3 title spans; 2 orthography-relevant spans; 2 max possible leaves; 1 recommended stable leaves
  - الْبَابُ الرَّابِعُ — الحذف من الكتابة: 9 title spans; 8 orthography-relevant spans; 8 max possible leaves; 1 recommended stable leaves
  - الْبَابُ الْخَامِسُ — الوصل والفصل: 5 title spans; 4 orthography-relevant spans; 4 max possible leaves; 1 recommended stable leaves
  - التاء المربوطة والتاء المفتوحة: 1 title spans; 1 orthography-relevant spans; 1 max possible leaves; 1 recommended stable leaves
  - ملحق تدريبي: رسم الهمزة والألف: 8 title spans; 5 orthography-relevant spans; 5 max possible leaves; 5 recommended stable leaves
- Ordering observations:
  - The book moves from hamza to alif layyina, then to addition and deletion in writing, then to joining/separation and ta marbuta, and closes with a training appendix that repeats hamza/alif material in drill-oriented form.
- Summary statistics:
  - total headings: 43
  - average sub-topics per chapter: 3.5
  - maximum possible leaves at finest reading: 21
  - recommended stable leaves after anti-overgranulation filtering: 9
  - maximum possible leaf labels: الهمزة في أول الكلمة, الهمزة في آخر الكلمة, الهمزة في وسط الكلمة, الألف اللينة في وسط الكلمة, الألف اللينة في آخر الكلمة, معرفة الأصل الواوي واليائي, زيادة الألف, زيادة الواو, نقص الألف أول الكلمة, نقص الألف وسط الكلمة, نقص الألف آخر الكلمة, نقص أل, نقص الواو, نقص الياء, نقص النون, النقص للرمز, وصل من بما قبلها, وصل ما بما قبلها, وصل لا بما قبلها, الفصل, التاء المربوطة والتاء المفتوحة
  - recommended stable leaf labels: الهمزة في أول الكلمة, الهمزة في آخر الكلمة, الهمزة في وسط الكلمة, الألف اللينة في وسط الكلمة, الألف اللينة في آخر الكلمة, الزيادة في الكتابة, الحذف من الكتابة, الوصل والفصل, التاء المربوطة والتاء المفتوحة

## الإملاء والترقيم في الكتابة العربية
- File path: `/mnt/c/Users/Rayane/Desktop/kr/shamela-export-samples/الإملاء والترقيم في الكتابة العربية.htm`
- Total heading count: 23
- Stage 1 retained heading count: 12
- Major chapter headings:
  1. الباب الأول: الإملاء في المجال التربوي
  2. الباب الثاني: الهمزة
  3. الباب الثالث: الألف اللينة
  4. الباب الرابع: الحروف التي تحذف من الكتابة
  5. الباب الخامس: الحروف التي تزاد في الكتابة
  6. الباب السادس: ما يوصل بغيره من الكلمات في الكتابة وما يكتب منفصلا عن غيره
  7. الباب السابع: هاء التأنيث وتاؤه
  8. الباب الثامن: علامات الترقيم
  9. الباب التاسع: قواعد الإملاء على بساط البحث
- Excluded front matter:
  - مقدمة
- Hierarchical outline:
  - الباب الأول: الإملاء في المجال التربوي [major]
    - تمهيد [excluded: meta_or_example]
    - أهداف درس الإملاء [excluded: meta_or_support_material]
    - منزلة الإملاء بين فروع اللغة [excluded: meta_or_support_material]
    - عوامل التهجي الصحيح [excluded: meta_or_support_material]
    - مادة الإملاء [excluded: meta_or_support_material]
    - أنواع الإملاء [excluded: meta_or_support_material]
    - أساليب التدريب الفردي [excluded: meta_or_support_material]
    - تصحيح الإملاء [excluded: meta_or_support_material]
  - الباب الثاني: الهمزة [major]
    - تمهيد [excluded: meta_or_example]
    - الهمزة في أول الكلمة [recommended: attested_structural_subtopic] → الهمزة في أول الكلمة
    - الهمزة في وسط الكلمة [recommended: attested_structural_subtopic] → الهمزة في وسط الكلمة
    - الهمزة في آخر الكلمة [recommended: attested_structural_subtopic] → الهمزة في آخر الكلمة
    - مفردات منوعة للتدريب على الهمزة [excluded: meta_or_example]
  - الباب الثالث: الألف اللينة [major]
  - الباب الرابع: الحروف التي تحذف من الكتابة [major]
  - الباب الخامس: الحروف التي تزاد في الكتابة [major]
  - الباب السادس: ما يوصل بغيره من الكلمات في الكتابة وما يكتب منفصلا عن غيره [major]
  - الباب السابع: هاء التأنيث وتاؤه [major]
  - الباب الثامن: علامات الترقيم [major]
  - الباب التاسع: قواعد الإملاء على بساط البحث [major]
- Heading counts per major chapter:
  - الباب الأول: الإملاء في المجال التربوي: 9 title spans; 0 orthography-relevant spans; 0 max possible leaves; 0 recommended stable leaves
  - الباب الثاني: الهمزة: 6 title spans; 3 orthography-relevant spans; 3 max possible leaves; 3 recommended stable leaves
  - الباب الثالث: الألف اللينة: 1 title spans; 1 orthography-relevant spans; 1 max possible leaves; 1 recommended stable leaves
  - الباب الرابع: الحروف التي تحذف من الكتابة: 1 title spans; 1 orthography-relevant spans; 1 max possible leaves; 1 recommended stable leaves
  - الباب الخامس: الحروف التي تزاد في الكتابة: 1 title spans; 1 orthography-relevant spans; 1 max possible leaves; 1 recommended stable leaves
  - الباب السادس: ما يوصل بغيره من الكلمات في الكتابة وما يكتب منفصلا عن غيره: 1 title spans; 1 orthography-relevant spans; 1 max possible leaves; 1 recommended stable leaves
  - الباب السابع: هاء التأنيث وتاؤه: 1 title spans; 1 orthography-relevant spans; 1 max possible leaves; 1 recommended stable leaves
  - الباب الثامن: علامات الترقيم: 1 title spans; 0 orthography-relevant spans; 0 max possible leaves; 0 recommended stable leaves
  - الباب التاسع: قواعد الإملاء على بساط البحث: 1 title spans; 0 orthography-relevant spans; 0 max possible leaves; 0 recommended stable leaves
- Ordering observations:
  - The book opens with pedagogy and classroom framing, then moves into core orthography chapters in the sequence hamza, alif layyina, deletion, addition, joining/separation, taa marbuta, punctuation, and a closing meta-discussion chapter.
- Summary statistics:
  - total headings: 23
  - average sub-topics per chapter: 1.14
  - maximum possible leaves at finest reading: 8
  - recommended stable leaves after anti-overgranulation filtering: 8
  - maximum possible leaf labels: الهمزة في أول الكلمة, الهمزة في وسط الكلمة, الهمزة في آخر الكلمة, الألف اللينة, الحذف من الكتابة, الزيادة في الكتابة, الوصل والفصل, التاء المربوطة والتاء المفتوحة
  - recommended stable leaf labels: الهمزة في أول الكلمة, الهمزة في وسط الكلمة, الهمزة في آخر الكلمة, الألف اللينة, الحذف من الكتابة, الزيادة في الكتابة, الوصل والفصل, التاء المربوطة والتاء المفتوحة

## الطريق المستقيم في نظم علامات الترقيم
- File path: `/mnt/c/Users/Rayane/Desktop/kr/shamela-export-samples/الطريق المستقيم في نظم علامات الترقيم.htm`
- Total heading count: 16
- Stage 1 retained heading count: 9
- Major chapter headings:
  1. علامات الترقيم
- Excluded front matter:
  - الطريقُ المستقيمُ فِي نظم علاماتِ الترقيم
- Hierarchical outline:
  - علامات الترقيم [major]
    - الفصلة [recommended: closed_class_punctuation_sign] → الفاصلة
    - تنبيهٌ [excluded: meta_or_example]
    - الفصلة المنقوطة [recommended: closed_class_punctuation_sign] → الفاصلة المنقوطة
    - الوقفة أو النقطة [recommended: closed_class_punctuation_sign] → النقطة
    - الوصلة أو الشرطة [recommended: closed_class_punctuation_sign] → الشرطة
    - القوسان [recommended: closed_class_punctuation_sign] → القوسان
    - علامة التنصيص [recommended: closed_class_punctuation_sign] → علامات التنصيص
    - النقطتان الرأسيتان [recommended: closed_class_punctuation_sign] → النقطتان الرأسيتان
    - تنبيه [excluded: meta_or_example]
    - علامة الاستفهام [recommended: closed_class_punctuation_sign] → علامة الاستفهام
    - عَلامَة الانفعال أو التعجب [recommended: closed_class_punctuation_sign] → علامة التعجب
    - الاستفهام التعجبي [excluded: meta_or_example]
    - علامة الحذف [recommended: closed_class_punctuation_sign] → علامة الحذف
    - الخاتمة [excluded: meta_or_example]
- Heading counts per major chapter:
  - علامات الترقيم: 15 title spans; 10 orthography-relevant spans; 10 max possible leaves; 10 recommended stable leaves
- Ordering observations:
  - This is a narrow punctuation-only text. After a title preface it enumerates punctuation signs one by one in a compact poetic sequence, with brief interjected tanbih notes and a closing khatima.
- Summary statistics:
  - total headings: 16
  - average sub-topics per chapter: 10
  - maximum possible leaves at finest reading: 10
  - recommended stable leaves after anti-overgranulation filtering: 10
  - maximum possible leaf labels: الفاصلة, الفاصلة المنقوطة, النقطة, الشرطة, القوسان, علامات التنصيص, النقطتان الرأسيتان, علامة الاستفهام, علامة التعجب, علامة الحذف
  - recommended stable leaf labels: الفاصلة, الفاصلة المنقوطة, النقطة, الشرطة, القوسان, علامات التنصيص, النقطتان الرأسيتان, علامة الاستفهام, علامة التعجب, علامة الحذف

## Corpus-Wide Summary
- Total analyzed books: 3
- Total headings: 82
- Average sub-topics per major chapter: 2.79
- Maximum possible leaves at finest reading: 35
- Recommended stable leaves after anti-overgranulation filtering: 20
- Maximum possible leaf labels: الهمزة في أول الكلمة, الهمزة في آخر الكلمة, الهمزة في وسط الكلمة, الألف اللينة في وسط الكلمة, الألف اللينة في آخر الكلمة, معرفة الأصل الواوي واليائي, زيادة الألف, زيادة الواو, نقص الألف أول الكلمة, نقص الألف وسط الكلمة, نقص الألف آخر الكلمة, نقص أل, نقص الواو, نقص الياء, نقص النون, النقص للرمز, وصل من بما قبلها, وصل ما بما قبلها, وصل لا بما قبلها, الفصل, التاء المربوطة والتاء المفتوحة, الألف اللينة, الحذف من الكتابة, الزيادة في الكتابة, الوصل والفصل, الفاصلة, الفاصلة المنقوطة, النقطة, الشرطة, القوسان, علامات التنصيص, النقطتان الرأسيتان, علامة الاستفهام, علامة التعجب, علامة الحذف
- Recommended stable leaf labels: الهمزة في أول الكلمة, الهمزة في آخر الكلمة, الهمزة في وسط الكلمة, الألف اللينة في وسط الكلمة, الألف اللينة في آخر الكلمة, الزيادة في الكتابة, الحذف من الكتابة, الوصل والفصل, التاء المربوطة والتاء المفتوحة, الألف اللينة, الفاصلة, الفاصلة المنقوطة, النقطة, الشرطة, القوسان, علامات التنصيص, النقطتان الرأسيتان, علامة الاستفهام, علامة التعجب, علامة الحذف

