# Excerpting Evaluation Review Packet

Generated: 2026-03-29T18:46:40.226946+00:00

## Campaign Summary

| Book | Status | Excerpts | Anomalies |
|------|--------|----------|-----------|
| ext_39_masala | STRUCTURALLY_CLEAN | 14 | 0 |
| ext_46_qa | STRUCTURALLY_CLEAN | 13 | 0 |
| ibn_aqil_v1 | STRUCTURALLY_CLEAN | 5 | 0 |
| ibn_aqil_v3 | STRUCTURAL_FAIL | 0 | 3 |
| taysir | STRUCTURAL_FAIL | 9 | 1 |

**Total units in ledger:** 43
**Total excerpts:** 41
**Total review cards:** 17

## Lane 1: Mandatory Observed Failures

**Denominator:** 43 units in ledger
**Selected:** 1
**Selection Rule:** All candidates with observed structural_fail anomalies. No sampling — all included.

### Card 1

**Canonical Key:** `(src_test0001, (book-level:ibn_aqil_v3), ci=0, ui=0)`
**Bucket Tags:** zero_output, book_level_failure
**Stage State:** absent
**Evidence Basis:** observed

**Context:**
- book_name: ibn_aqil_v3

**Observed Facts:**
- Final excerpt count: 0
- Phase 1 chunk count: 28
- Phase 2a time: 725.6s
- LLM trace count: 6

**Inferred Interpretation:** Run consumed 725.6s in phase2a and made 6 LLM call(s) but produced zero excerpts. 6 call-level error(s) detected.

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ibn_aqil_v3/excerpts.jsonl`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ibn_aqil_v3/timing.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ibn_aqil_v3/raw_llm_responses/`

**Review Questions:**
- Why did this book produce zero excerpts despite upstream activity?
- Is the root cause truncation, timeout, or a parsing failure?

**Anomaly IDs:** ANO-ZERO-OUTPUT

---

## Lane 2: Inferred Diagnostics

**Denominator:** 43 units in ledger
**Selected:** 2
**Selection Rule:** All candidates with inferred (high/moderate confidence) anomalies. No sampling.

### Card 2

**Canonical Key:** `(src_test0001, div_src_test0001_7_000, ci=0, ui=2)`
**Bucket Tags:** anomaly_associated
**Stage State:** grouped_only
**Evidence Basis:** inferred_moderate_confidence

**Primary Text:**
> عَنْ أمِيرِ المُؤْمِنِينَ أبي حَفْصِ " عُمَرَ بْنِ الخَطَاب" رضي الله عنه قَال: سَمِعت رسُولَ الله

**Context:**
- prev_unit: {"unit_index": 1, "text_snippet": "‌‌كتاب الطهارة\n‌‌النية وأحكامها"}
- next_unit: {"unit_index": 3, "text_snippet": "غريب الحديث:\n1- \" إنما الأعمال بالنيات \" كلمة [إنما] ، تفيد الحصر، فهو هنا قصر موصُوف على صفة"}

**Observed Facts:**
- stage_state: grouped_only
- self_containment: FULL
- Unit present in Phase 2b but absent from final excerpts

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\taysir/phase2b_groupings/chunk_div_src_test0001_7_000.json`

**Anomaly IDs:** ANO-UNIT-LOSS

---

### Card 3

**Canonical Key:** `(src_test0001, div_src_test0001_7_000, ci=0, ui=9)`
**Bucket Tags:** anomaly_associated
**Stage State:** grouped_only
**Evidence Basis:** inferred_moderate_confidence

**Primary Text:**
> 3- أن النية مَحلُّها القلب، واللفظ بها بدعة.

**Context:**
- prev_unit: {"unit_index": 8, "text_snippet": "2- أن النية شرط أساسي في العمل، ولكن بلا غُلُوّ في استحضارها يفسد على المتعبد عباد"}
- next_unit: {"unit_index": 10, "text_snippet": "4- وجوب الحذر من الرياء والسمعة والعمل لأجل الدنيا، مادام أن شيئاً من ذلك يفسد ال"}

**Observed Facts:**
- stage_state: grouped_only
- self_containment: FULL
- Unit present in Phase 2b but absent from final excerpts

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\taysir/phase2b_groupings/chunk_div_src_test0001_7_000.json`

**Anomaly IDs:** ANO-UNIT-LOSS

---

## Lane 3: Self-Containment / Boundary Risk

**Denominator:** 43 units in ledger
**Selected:** 5
**Selection Rule:** All DEPENDENT units + up to 5 PARTIAL units per book (boundary cases prioritized).

### Card 4

**Canonical Key:** `(src_test0001, div_src_test0001_2_000_pre, ci=0, ui=6)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> 5 - ولا بد من الاستعجال بمثل هذه الوصية لقوله صلى الله عليه وسلم:
"ما حق امرئ مسلم يبيت ليلتين وله شيء يريد أن يوصي فيه إلا ووصيته مكتوبة عند رأسه قال ابن عمر: ما مرت علي ليلة منذ سمعت رسول الله صلى الله عليه وسلم قال ذلك إلا وعندي وصيتي.

**Context:**
- prev_unit: {"unit_index": 5, "text_snippet": "4 - وإذا كان عليه حقوق فليؤدها إلى أصحابها إن تيسر له ذلك وإلا أوصى لأمره صلى الله"}
- next_unit: {"unit_index": 7, "text_snippet": "6 - ويجب أن يوصي للأقربين الذين لا يرثون منه لقوله تبارك وتعالى: {كُتِبَ عَلَيْكُمْ"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_39_masala/phase2b_groupings/chunk_div_src_test0001_2_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_39_masala/excerpts.jsonl`

---

### Card 5

**Canonical Key:** `(src_test0001, div_src_test0001_2_000_pre, ci=0, ui=9)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> 8 - ويشهد على ذلك رجلين عدلين مسلمين فإن لم يوجدا فرجلين من غير المسلمين على أن يستوثق منهما عند الشك بشهادتهما حسبما جاء بيانه في قول الله تبارك وتعالى: {يَا أَيُّهَا الَّذِينَ آمَنُوا شَهَادَةُ بَيْنِكُمْ إِذَا حَضَرَ أَحَدَكُمُ الْمَوْتُ حِينَ الْوَصِيَّةِ اثْنَانِ ذَوَا عَدْلٍ مِنْكُمْ أَوْ آخَر...

**Context:**
- prev_unit: {"unit_index": 8, "text_snippet": "7 - صحيح وله أن يوصي بالثلث من ماله ولا يجوز الزيادة عليه بل الأفضل أن ينقص منه لحد"}
- next_unit: {"unit_index": 10, "text_snippet": "9 - وأما الوصية للوالدين والأقربين الذين يرثون من الموصي فلا تجوز لأنها منسوخة بآية"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_39_masala/phase2b_groupings/chunk_div_src_test0001_2_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_39_masala/excerpts.jsonl`

---

### Card 6

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=5)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> انتهى.
وقد أخذت من الكتاب الأول اللباب وأدخلته معزوا إليه في خلل هذا الكتاب، وضممت خلاصة الثاني في مباحث العلة.
وضممت إليه من كتابه الثاني (الأنصاف في مباحث الخلاف) جملة.
ولم أنقل من كتابه حرفا إلا مقرونا بالعزو إليه ليعرف مقام كتاب من كتابه ويتميز عند أولي التمييز جليل نصابه.
وإلى الله الضراعة في ح...

**Context:**
- prev_unit: {"unit_index": 4, "text_snippet": "وأما الذي في جدل النحو، فإنه في كراسة لطيفة، سماه بـ (الإغراب في جدل الإعراب) ورتبه"}
- next_unit: {"unit_index": 6, "text_snippet": "الكلام في‌‌ المقدمات\nفيها مسائل الأولى\nأصول النحو: علم يبحث فيه عن أدلة النحو الإجمال"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/phase2b_groupings/chunk_div_src_test0001_3_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/excerpts.jsonl`

---

### Card 7

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=8)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> وقولي (الإجمالية) احتراز في البحث عن التفصيلية، كالبحث عن دليل خاص بجواز العطف على الضمير المجرور من غير إعادة الجار، وبجواز الإضمار قبل
الذكر في باب الفاعل والمفعول، وبجواز مجيء التمييز مؤكدا، ونحو ذلك، فهذه وظيفة علم النحو نفسه، لا أصوله.

**Context:**
- prev_unit: {"unit_index": 7, "text_snippet": "وأدلة النحو الغالبة أربعة.\nقال ابن جني في الخصائص: \" أدلة النحو ثلاثة: السماع، والإ"}
- next_unit: {"unit_index": 9, "text_snippet": "وقولي (من حيث هي أدلته) بيان لجهة البحث عنها، أي البحث عن القرآن بأنه حجة في النحو،"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/phase2b_groupings/chunk_div_src_test0001_3_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/excerpts.jsonl`

---

### Card 8

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=9)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> وقولي (من حيث هي أدلته) بيان لجهة البحث عنها، أي البحث عن القرآن بأنه حجة في النحو، لأنه أفصح الكلام، سواء كان متواترا أم آحادا، وعن السنة كذلك بشرطتها الآتي، وعن كلام من يوثق بعربيته كذلك وعن إجماع أهل البلين كذلك، أي إن كلا مما ذكر يجوز الاحتجاج به دون غيره، وعن القياس وما يجوز من العلل فيه وما لا...

**Context:**
- prev_unit: {"unit_index": 8, "text_snippet": "وقولي (الإجمالية) احتراز في البحث عن التفصيلية، كالبحث عن دليل خاص بجواز العطف على"}
- next_unit: {"unit_index": 10, "text_snippet": "وقولي (وكيفية الاستدلال بها) ، أي عند تعارضها ونحوه، كتقديم السماع على القياس واللغة"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/phase2b_groupings/chunk_div_src_test0001_3_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/excerpts.jsonl`

---

## Lane 4: Sentinel Audit Sample

**Denominator:** 43 units in ledger
**Selected:** 4
**Selection Rule:** Random sample independent of anomaly ranking. seed=42. At least 1 per book, total = max(3, 10% of excerpts).

### Card 9

**Canonical Key:** `(src_test0001, div_src_test0001_2_000_pre, ci=0, ui=11)`
**Bucket Tags:** sentinel_audit
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> 10 - ويحرم الإضرار في الوصية كأن يوصي بحرمان بعض الورثة من حقهم من الإرث أو يفضل بعضهم على بعض فيه لقوله تبارك وتعالى: {لِلرِّجَالِ نَصِيبٌ مِمَّا تَرَكَ الْوَالِدَانِ وَالْأَقْرَبُونَ. . . . مِمَّا قَلَّ مِنْهُ أَوْ كَثُرَ نَصِيباً مَفْرُوضاً. . .ثم قال: {مِنْ بَعْدِ وَصِيَّةٍ يُوصَى بِهَا أَوْ دَي...

**Context:**
- primary_function: rule_statement
- self_containment: FULL
- div_path: ['مقدمة', 'مقدمة']

**Observed Facts:**
- primary_function: rule_statement
- self_containment: FULL
- word_count: 76

**Review Questions:**
- Is this excerpt a genuinely useful teaching unit?
- Is the self-containment assessment correct?

---

### Card 10

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=0)`
**Bucket Tags:** sentinel_audit
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> بسم الله الرحمن الرحيم

قال العبد الفقير إلى الله تعالى، عبد الرحمن بن أبي بكر السيوطي:

الحمد لله الذي أرشد لابتكار هذا النمط وتفضل بالعفو عما صدر عن العبد على وجه السهو والغلط، وأشهد أن لا إله إلا الله وحده لا شريك له، شهادة لا وكس فيها ولا شطط، وأشهد أن سيدنا محمدا عبده ورسوله، أفضل من عليه جبرئي...

**Context:**
- primary_function: structural_transition
- self_containment: FULL
- div_path: ['المقدمات', 'مقدمة']

**Observed Facts:**
- primary_function: structural_transition
- self_containment: FULL
- word_count: 73

**Review Questions:**
- Is this excerpt a genuinely useful teaching unit?
- Is the self-containment assessment correct?

---

### Card 11

**Canonical Key:** `(src_test0001, div_src_test0001_2_000_pre, ci=0, ui=5)`
**Bucket Tags:** sentinel_audit
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> 4 - وإذا كان عليه حقوق فليؤدها إلى أصحابها إن تيسر له ذلك وإلا أوصى لأمره صلى الله عليه وسلم بذلك.

**Context:**
- primary_function: rule_statement
- self_containment: FULL
- div_path: ['مقدمة', 'مقدمة']

**Observed Facts:**
- primary_function: rule_statement
- self_containment: FULL
- word_count: 21

**Review Questions:**
- Is this excerpt a genuinely useful teaching unit?
- Is the self-containment assessment correct?

---

### Card 12

**Canonical Key:** `(src_test0001, div_src_test0001_7_000, ci=0, ui=0)`
**Bucket Tags:** sentinel_audit
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> تيسير العلام شرح عمدة الأحكام
للبسام

**Context:**
- primary_function: editorial_note
- self_containment: FULL
- div_path: ['كتاب الطهارة', 'النية وأحكامها']

**Observed Facts:**
- primary_function: editorial_note
- self_containment: FULL
- word_count: 6

**Review Questions:**
- Is this excerpt a genuinely useful teaching unit?
- Is the self-containment assessment correct?

---

## Lane 5: Stratified Positive Controls

**Denominator:** 43 units in ledger
**Selected:** 2
**Selection Rule:** Cleanest FULL excerpts with no flags. Up to 2 per book, diverse functions.

### Card 13

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=6)`
**Bucket Tags:** positive_control
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> الكلام في‌‌ المقدمات
فيها مسائل الأولى
أصول النحو: علم يبحث فيه عن أدلة النحو الإجمالية، من حيث هي أدلته، وكيفية الاستدلال بها، وحال المستدل.

فقولي (علم) ، أي صناعة فلا يرد ما أورد على التعليل به في حد أصول الفقه، من كونه يلزم عليه فقده، إذا فقد العالم به، لأنه صناعة مدونة، مقررة وجد العالم به، أم ...

**Context:**
- primary_function: definition
- self_containment: FULL
- div_path: ['المقدمات', 'مقدمة']

**Observed Facts:**
- primary_function: definition
- self_containment: FULL
- word_count: 68

**Review Questions:**
- Is this excerpt a genuinely useful teaching unit?
- Is the self-containment assessment correct?

---

### Card 14

**Canonical Key:** `(src_test0001, div_src_test0001_2_000, ci=0, ui=4)`
**Bucket Tags:** positive_control
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> وقد أردت أن أقوم لهذا الكتاب بعمل أتقرب به إلى الله تعالى، فرأيت - في أول الأمر - أن أتمم ما قصر فيه من البحث: فأبين اختلاف النحويين واستدلالاتهم ثم نظرت فإذا ذلك يخرج بالكتاب عن أصل الغرض منه، وقد يكون الإطناب باعثا على الازورار عنه، ونحن في زمن أقل ما فيه من عاب أنك لا تجد راغبا في علوم العرب إلا ...

**Context:**
- primary_function: editorial_note
- self_containment: FULL
- div_path: ['مقدمة الطبعة الثانية']

**Observed Facts:**
- primary_function: editorial_note
- self_containment: FULL
- word_count: 265

**Review Questions:**
- Is this excerpt a genuinely useful teaching unit?
- Is the self-containment assessment correct?

---

## Lane 6: Ambiguity / Near-Threshold Cases

**Denominator:** 43 units in ledger
**Selected:** 3
**Selection Rule:** Consensus disagreement or PARTIAL with context_hint. Up to 3 per book.

### Card 15

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=10)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> وقولي (وكيفية الاستدلال بها) ، أي عند تعارضها ونحوه، كتقديم السماع على القياس واللغة الحجازية على التميمية إلا لمانع، وأقوى العلتين على أضعفهما، وأخف الأقبحين على أشدهما قبحا، إلى غير ذلك. وهذا هو المعقود له من الكتاب السادس.

**Context:**
- prev_unit: {"unit_index": 9, "text_snippet": "وقولي (من حيث هي أدلته) بيان لجهة البحث عنها، أي البحث عن القرآن بأنه حجة في النحو،"}
- next_unit: {"unit_index": 11, "text_snippet": "وقولي (وحال المستدل) ، أي المستنبط للمسائل من الأدلة المذكورة، أي صفاته وشروطه، وما"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/phase2b_groupings/chunk_div_src_test0001_3_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/excerpts.jsonl`

---

### Card 16

**Canonical Key:** `(src_test0001, div_src_test0001_3_000_pre, ci=0, ui=11)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> وقولي (وحال المستدل) ، أي المستنبط للمسائل من الأدلة المذكورة، أي صفاته وشروطه، وما يتبع ذلك من صفة المقلد والسائل. وهذا هو الموضوع له الكتاب السابع.

**Context:**
- prev_unit: {"unit_index": 10, "text_snippet": "وقولي (وكيفية الاستدلال بها) ، أي عند تعارضها ونحوه، كتقديم السماع على القياس واللغة"}
- next_unit: {"unit_index": 12, "text_snippet": "وبعد أن حررت هذا الحد بفكري وشرحته، وجدت ابن الأنباري قال: \" أصول النحو أدلة النحو ا"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/phase2b_groupings/chunk_div_src_test0001_3_000_pre.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\ext_46_qa/excerpts.jsonl`

---

### Card 17

**Canonical Key:** `(src_test0001, div_src_test0001_7_000, ci=0, ui=3)`
**Bucket Tags:** partial_self_containment, near_threshold
**Stage State:** final_excerpt
**Evidence Basis:** observed

**Primary Text:**
> غريب الحديث:
1- " إنما الأعمال بالنيات " كلمة [إنما] ، تفيد الحصر، فهو هنا قصر موصُوف على صفة، وهو إثبات حكم الأعمال بالنيات، فهو في قوة [ما الأعمال إلا بالنيات] وينفى الحكم عما عداه.
2- " النية " لغة: القصد. ووقع بالإفراد في أكثر الروايات. قال البيضاوي النية عبارة عن انبعاث القلب نحو ما يراه موافقا...

**Context:**
- prev_unit: {"unit_index": 2, "text_snippet": "عَنْ أمِيرِ المُؤْمِنِينَ أبي حَفْصِ \" عُمَرَ بْنِ الخَطَاب\" رضي الله عنه قَال: سَمِعت رسُولَ الله"}
- next_unit: {"unit_index": 4, "text_snippet": "المعنى الإجمالي:\nهذا حديث عظيم وقاعدة جليلة من قواعد الإسلام هي القياس الصحيح لوزن الأعمال"}

**Observed Facts:**
- stage_state: final_excerpt
- self_containment: PARTIAL

**Artifact Pointers:**
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\taysir/phase2b_groupings/chunk_div_src_test0001_7_000.json`
- `C:\Users\Rayane\Desktop\kr\integration_tests\run_20260328\taysir/excerpts.jsonl`

---
