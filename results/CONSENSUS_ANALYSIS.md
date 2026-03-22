# Consensus Disagreement Analysis

**Date:** 2026-03-22
**Total books with consensus data:** 347
**Agreed:** 320 (92%)
**Disagreed:** 27 (8%)

## Disagreements by Phase

| Phase | Disagreements | Total | Rate |
|-------|-------------|-------|------|
| phase_c | 6 | 73 | 8% |
| phase_d | 14 | 204 | 7% |
| phase_e | 7 | 70 | 10% |

## Field-Level Disagreement Frequency

| Field | Disagreement Count | % of Disagreed Books |
|-------|-------------------|---------------------|
| author_canonical_name_ar | 27 | 100% |
| science_scope | 13 | 48% |
| genre | 7 | 26% |
| structural_format | 4 | 15% |
| is_multi_layer | 1 | 4% |

### author_canonical_name_ar (27 disagreements)

| Book | Model 1 | Model 2 |
|------|---------|---------|
| أبنية الأسماء والأفعال والمصادر | علي بن جعفر بن علي السعدي الصقلي، أبو القاسم ابن ا | علي بن جعفر بن علي السعدي، ابن القطان الصقلي |
| أعلام الموقعين عن رب العالمين - ط عطاءات العلم | محمد بن أبي بكر بن أيوب بن سعد بن حريز الزرعي الدم | أبو عبد الله محمد بن أبي بكر بن أيوب ابن قيم الجوز |
| إعلام الموقعين عن رب العالمين - ت مشهور | محمد بن أبي بكر بن أيوب بن سعد الزرعي الدمشقي، شمس | أبو عبد الله محمد بن أبي بكر بن أيوب المعروف بابن  |
| تحفة المودود بأحكام المولود - ط عطاءات العلم | محمد بن أبي بكر بن أيوب بن سعد شمس الدين ابن قيم ا | أبو عبد الله محمد بن أبي بكر بن أيوب ابن قيم الجوز |
| تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد | محمد علاء الدين بن محمد أمين عابدين | محمد علاء الدين أفندي |
| من أحاديث سفيان الثوري - رواية السري بن يحيى - جوا | السري بن يحيى بن إياس بن حرملة بن إياس الشيباني ال | السرى بن يحيى بن إياس بن حرملة بن إياس الشيبانى ال |
| أعلام الموقعين عن رب العالمين - ط عطاءات العلم | محمد بن أبي بكر بن أيوب بن سعد شمس الدين ابن قيم ا | أبو عبد الله محمد بن أبي بكر بن أيوب ابن قيم الجوز |
| إعلام الموقعين عن رب العالمين - ت مشهور | محمد بن أبي بكر بن أيوب بن سعد الزرعي الدمشقي، شمس | أبو عبد الله محمد بن أبي بكر بن أيوب المعروف بابن  |
| إيجاز البيان عن معاني القرآن | محمود بن أبي الحسن بن الحسين النيسابوري، أبو القاس | محمود بن أبى الحسن بن الحسين النيسابوري أبو القاسم |
| السراج المنير في ترتيب أحاديث صحيح الجامع الصغير | جلال الدين عبد الرحمن بن أبي بكر السيوطي | محمد ناصر الدين الألباني |
| ... | (17 more) | |

### science_scope (13 disagreements)

| Book | Model 1 | Model 2 |
|------|---------|---------|
| أعلام الموقعين عن رب العالمين - ط عطاءات العلم | ['usul_al_fiqh', 'fiqh'] | ['usul_al_fiqh'] |
| إعلام الموقعين عن رب العالمين - ت مشهور | ['usul_al_fiqh', 'fiqh'] | ['usul_al_fiqh'] |
| أعلام الموقعين عن رب العالمين - ط عطاءات العلم | ['usul_al_fiqh', 'fiqh'] | ['usul_al_fiqh'] |
| إعلام الموقعين عن رب العالمين - ت مشهور | ['usul_al_fiqh', 'fiqh'] | ['usul_al_fiqh'] |
| إيجاز البيان عن معاني القرآن | ['tafsir', 'ulum_al_quran', 'nahw', 'lughah', 'fiq | ['tafsir', 'ulum_al_quran'] |
| القول المعروف في فضل المعروف | ['hadith', 'adab'] | ['adab', 'tasawwuf'] |
| معجم الشيوخ لابن عساكر | ['ulum_al_hadith', 'hadith', 'tarikh'] | ['hadith', 'ulum_al_hadith', 'tarikh'] |
| نظم ما انفرد به ابن تيمية | ['fiqh'] | ['fiqh', 'usul_al_fiqh'] |
| أثر الدعوة الوهابية في الإصلاح الديني والعمراني في | ['tarikh', 'aqidah'] | ['tarikh'] |
| أحكام عصاة المؤمنين من كلام شيخ الإسلام ابن تيمية  | ['aqidah', 'fiqh'] | ['fiqh', 'aqidah'] |
| ... | (3 more) | |

### genre (7 disagreements)

| Book | Model 1 | Model 2 |
|------|---------|---------|
| أبنية الأسماء والأفعال والمصادر | matn | other |
| أعلام الموقعين عن رب العالمين - ط عطاءات العلم | matn | usul_al_fiqh |
| أعلام الموقعين عن رب العالمين - ط عطاءات العلم | matn | usul_al_fiqh |
| أثر الدعوة الوهابية في الإصلاح الديني والعمراني في | risalah | tarikh |
| أحكام عصاة المؤمنين من كلام شيخ الإسلام ابن تيمية  | other | risalah |
| التقصي لما في الموطأ من حديث النبي صلى الله عليه و | mukhtasar | sharh |
| منتهى الإرادات في جمع المقنع مع التنقيح وزيادات -  | matn | mukhtasar |

### structural_format (4 disagreements)

| Book | Model 1 | Model 2 |
|------|---------|---------|
| تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد | commentary | prose |
| تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد | commentary | prose |
| معجم الشيوخ لابن عساكر | dictionary | prose |
| جمع الوسائل في شرح الشمائل | commentary | prose |

### is_multi_layer (1 disagreements)

| Book | Model 1 | Model 2 |
|------|---------|---------|
| السراج المنير في ترتيب أحاديث صحيح الجامع الصغير | True | False |

## Analysis

### Key Findings

1. **Most disputed field:** `author_canonical_name_ar` (27 disagreements)
2. **Overall agreement rate:** 92.2%
3. **Disagreement rate:** 7.8%

### Implications for Pipeline

The multi-model consensus mechanism (D-041) is working as designed. Disagreements 
are flagged and the canonical model's response is used as the final answer. 
Human review should focus on the most disputed fields to calibrate model selection.
