# Gold Standard Excerpts — 20 Exemplary Teaching Units
# Source: campaign_20260331 (2,303 excerpts, 5 packages)
# Selection: Architect deep review, verified boundaries + function + self-containment
# Purpose: Few-shot examples for production excerpting prompts

## Selection Criteria Applied
1. FULL self-containment (all C-SC-1 through C-SC-5 pass)
2. 50–350 words (substantial but not bloated)
3. Correct function classification (verified by Arabic reading)
4. Accurate description and topic tags
5. Clean boundaries (scholar would agree with start/end)
6. Diverse function types across packages
7. Diverse genres: hadith sharh, nahw sharh, fiqh masala, usul al-nahw

## Known Metadata Issues to Correct in Prompt Examples
- **Narrator role:** Companion narrators (صحابة) in hadith isnad are labeled "quoted_opinion" — should be "narrator" (SPEC gap SG-1). In the gold examples below, I note the correct role.
- **Author ID:** All excerpts show author_id="unknown" due to upstream layer detection absence (UE-1). The correct attribution is noted per excerpt.

---

## Package 1: taysir (فقه — حديث شرح)
### تيسير العلام شرح عمدة الأحكام — عبد الله البسام (حنبلي)

### GOLD-T1: rule_statement (100 words)
**Topic:** أحكام دعاء الاستفتاح
**Why exemplary:** Complete fawa'id block with 6 numbered rulings, clear boundaries, self-contained without the preceding hadith because each ruling stands independently.

```arabic
أحكام الحديث:
1- استحباب دعاء الاستفتاح في الصلاة.
2- أن مكانه بعد تكبيرة الإحرام وقبل قراءة الفاتحة في الركعة الأولى من كل صلاة.
3- أن يُسِرَّ به ولو كانت الصلاة جهرية.
4- أنه لا يطال فيه الدعاء، ولاسيما في الجماعة للصلوات المكتوبة.
5- حرص الصحابة رضي الله عنهم على أحوال الرسول صلى الله عليه وسلم في حركاته وسكناته.
6- أنه ينبغي في مواطن الدعاء أن يُلح الإنسان ويكثر في طلب الشيء، ولو بطريق ترادف الألفاظ.
فإن هذه الدعوات تدور كلها على مَحْو الذنوب والإبعاد عنها، ومعاني الماء والثلج، والبرد، متقاربة. والمقصود منه متحد. وهو الإنقاء من حرارة الذنوب بهذه المواد الباردة.
```

**Metadata:**
- primary_function: rule_statement ✓
- self_containment: FULL ✓
- correct_author: عبد الله البسام (sharh layer)

---

### GOLD-T2: opinion_statement (101 words)
**Topic:** ذم التزهد المتكلف
**Why exemplary:** Extended scholarly quotation from الصنعاني with clear attribution, rich content about false asceticism, complete thought.

```arabic
فائدة:
في حاشية الصنعاني على شرح العمدة ما يلي:
أخاف على الزاهد أن تكون شهوته انقلبت إلى الترك، فصار يشتتهي ألا يتناول. وللنفس في هذا مكر خفي رياء دقيق، فإن سلمت من الرياء للخلق كانت إلى خير.
ولقد دخل المتزهدون في طرق لم يسلكها النبي صلى الله عليه وسلم ولا أصحابه من إظهار التخشع الزائد عن الحد، وتخشين الملبس، وأشياء صار العوام يستحسنونها، وصارت لأقوام كالمعاش، يجتنون من ثمراتها تقبيل اليد والتوقير، وأكثر في خلوته على غير حالته في جلوته، يتناول في خلوته الشهوات، ويعكف على اللذات ويرى الناس أنه متزهد، وما تزهد إلا القميص، وإذا نظرت إلى أحواله فعنده كبر فرعون.
```

**Metadata:**
- primary_function: opinion_statement ✓
- self_containment: FULL ✓
- quoted_scholars: [{الصنعاني, role: quoted_opinion}] ✓
- correct_author: عبد الله البسام (sharh layer), quoting الصنعاني

---

### GOLD-T3: evidence_hadith (100 words)
**Topic:** تحريم حمل السلاح على المسلمين
**Why exemplary:** Complete hadith + المعنى الإجمالي pattern. Hadith text is short and self-contained, meaning section explains fully.

```arabic
الحديث التاسع عشر
عَن أبى مُوسَى (عَبْدِ الله بْنِ قيْس) عَنِ النبي صلى الله عليه وسلم قَالَ: "مَنْ حَمَل علينا السلاح فَلَيْسَ مِنَّا".
المعنى الإجمالي:
يبين النبي صلى الله عليه وسلم أن المؤمنين إخوة يتألم بعضهم لألم بعضهم الآخر ويفرح لفرحه، وأن كلمتهم واحدة فهم يد على من عاداهم.
فيلزمهم الاجتماع والطاعة لإمامهم، وإعانته على من بغى وخرج عليه، لأن هذا الخارج. شق عصا المسلمين، وحمل عليهم السلاح، وأخافهم.
فيجب قتاله، حتى يرجع ويفئ إلى أمر الله تعالى.
لأن الخارج عليهم والباغي عليهم، ليس في قلبه، لهم الرحمة الإنسانية، ولا المحبة الإسلامية، فهو خارج عن سبيلهم فليس منهم، فيجب قتاله وتأديبه.
```

**Metadata:**
- primary_function: evidence_hadith ✓
- self_containment: FULL ✓
- quoted_scholars: [{أبو موسى الأشعري, role: **narrator** (not quoted_opinion — SG-1 fix needed)}]
- correct_author: عبد الله البسام (sharh layer), hadith from عبد الغني المقدسي (matn)

---

### GOLD-T4: definition (97 words)
**Topic:** تعريف الهبة وأنواعها
**Why exemplary:** Complete definition with 5 subtypes clearly distinguished. Begins with chapter heading naturally attached to content. Textbook-quality categorization.

```arabic
‌‌باَبُ الهِبَة
الهبة: - بكسر الهاء وتخفيف الباء. وهى- شرعا- تمليك في الحياة بلا عوض. ولفظ الهبة يشمل أنواعا كثيرة:
منها: - الهدية المطلقة، والإبراء من الدين، والصدقة، والعطية، وهبة الثواب. ولكنْ بينها فروق.
فالهبة المطلقة: - ما قصد بها التودد إلى الموهوب له.
والصدقة: - ما قصد بها محض ثواب الآخرة.
والعطية: - هي الهبة في مرض الموت المخوف، وتشارك الوصية في أكثر أحكامها.
وهبة الدين: - هي إبراء المدين من الدين.
وهبة الثواب: - وهى ما قصد بها أخذ عوضها، وهى من أنواع البيع ولها أحكامه.
ولكن إذا أطلقت الهبة، فالمراد بها الأولى من هذه الأنواع.
```

**Metadata:**
- primary_function: definition ✓
- self_containment: FULL ✓
- correct_author: عبد الله البسام (sharh layer)

---

## Package 2: ibn_aqil_v1 (نحو — شرح ألفية)
### شرح ابن عقيل على ألفية ابن مالك

### GOLD-IA1-1: rule_statement (100 words)
**Topic:** تثنية الذي والتي
**Why exemplary:** Complete grammar rule with morphological detail, multiple cases (رفع/نصب/جر), and notes the Kufan school's alternative.

```arabic
وأما الموصول الاسمي ف الذي للمفرد المذكر والتي للمفرد المؤنثة فإن ثنيت أسقطت الياء وأتيت مكانها بالألف في حالة الرفع نحو اللذان واللتان والياء في حالتي الجر والنصب فتقول اللذين واللتين وإن شئت شددت النون عوضا عن الياء المحذوفة فقلت اللذان واللتان وقد قرئ واللذان يأتيانها منكم ويجوز التشديد أيضا مع الياء وهو مذهب الكوفيين فتقول اللذين واللتين وقد قرئ {ربنا أرنا اللذين} بتشديد النون وهذا التشديد يجوز أيضا في تثنية ذا وتا اسمي الإشارة فتقول ذان وتان وكذلك مع الياء فتقول ذين وتين وهو مذهب الكوفيين والمقصود بالتشديد أن يكون عوضا عن الألف المحذوفة كما تقدم في الذي والتي.
```

**Metadata:**
- primary_function: rule_statement ✓
- self_containment: FULL ✓
- correct_author: ابن عقيل (sharh), verse from ابن مالك (matn)

---

### GOLD-IA1-2: opinion_statement (98 words)
**Topic:** أل في الموصولات
**Why exemplary:** Complete scholarly debate with two positions + evidence + refutation of counter-evidence. The hallmark of a well-extracted opinion excerpt.

```arabic
ومثل أيضا ب الذين واللات والمراد بهما ما دخل عليه أل من الموصولات وهو مبني على أن تعريف الموصول بالصلة فتكون الألف واللام زائدة وهو مذهب قوم واختاره المصنف وذهب قوم إلى أن تعريف الموصول ب أل إن كانت فيه نحو الذي فإن لم تكن فيه فبنيتها نحو من وما إلا أيا فإنها تتعرف بالإضافة فعلى هذا المذهب لا تكون الألف واللام زائدة وأما حذفها في قراءة من قرأ صراط لذين أنعمت عليهم فلا يدل على أنها زائدة إذ يحتمل أن تكون حذفت شذوذا وإن كانت معرفة كما حذفت من قولهم سلام عليكم من غير تنوين يريدون السلام عليكم.
```

**Metadata:**
- primary_function: opinion_statement ✓
- self_containment: FULL ✓
- quoted_scholars: [{المصنف = ابن مالك, role: classification_frame}] ✓

---

### GOLD-IA1-3: definition (99 words)
**Topic:** الشبه المعنوي في بناء الأسماء
**Why exemplary:** Explains an abstract grammatical concept (semantic resemblance to particles) with two subtypes and concrete examples. Perfect definition structure.

```arabic
والثاني: شبه الاسم له في المعنى وهو قسمان أحدهما ما أشبه حرفا موجودا والثاني ما أشبه حرفا غير موجود فمثال الأول متى فإنها مبنية
لشبهها الحرف في المعنى فإنها تستعمل للاستفهام نحو متى تقوم وللشرط نحو متى تقم أقم وفي الحالتين هي مشبهة لحرف موجود لأنها في الاستفهام كالهمزة وفي الشرط كإن ومثال الثاني هنا فإنها مبنية لشبهها حرفا كان ينبغي أن يوضع فلم يوضع وذلك لأن الإشارة معنى من المعاني فحقها أن يوضع لها حرف يدل عليها كما وضعوا للنفي ما وللنهي لا وللتمني ليت وللترجي لعل ونحو ذلك فبنيت أسماء الإشارة لشبهها في المعنى حرفا مقدرا.
```

**Metadata:**
- primary_function: definition ✓
- self_containment: FULL ✓
- correct_author: ابن عقيل (sharh)

---

### GOLD-IA1-4: narration (78 words)
**Topic:** مقدمة الألفية — خطبة ابن مالك
**Why exemplary:** The iconic opening of the most important Arabic grammar text. Shows how the engine handles verse + muqaddimah. Preserved bismillah + hamdala correctly.

```arabic
بسم الله الرحمن الرحيم
‌‌الكلام وما يتألف منه
قال محمد هو ابن مالك … أحمد ربي الله خير مالك (1)
مصليا على النبي المصطفى … وآله المستكملين الشرفا (2) وأستعين الله في ألفيه … مقاصد النحو بها محويه (1)
تقرب الأقصى بلفظ موجز … وتبسط البذل بوعد منجز (2)
وتقتضي رضا بغير سخط … فائقة ألفية ابن معط (3) وهو بسبق حائز تفضيلا … مستوجب ثنائي الجميلا (1)
والله يقضي بهبات وافره … لي وله في درجات الآخره (2)
```

**Metadata:**
- primary_function: narration ✓ (muqaddimah/khutba)
- self_containment: FULL ✓
- correct_author: ابن مالك (matn — these are HIS verses)

---

## Package 3: ibn_aqil_v3 (نحو — شرح ألفية)

### GOLD-IA3-1: rule_statement (100 words)
**Topic:** منع صرف الصفة مع زيادة الألف والنون (فَعْلان)
**Why exemplary:** Complete grammar rule with Alfiyyah verse + clear explanation + example + counter-example + condition boundary.

```arabic
وزائدا فعلان في وصف سلم … من أن يرى بتاء تأنيث ختم
أي يمنع الاسم من الصرف للصفة وزيادة الألف والنون بشرط أن لا
يكون المؤنث في ذلك مختوما بتاء التأنيث وذلك نحو سكران وعطشان وغضبان فتقول هذا سكران ورأيت سكران ومررت بسكران فتمنعه من الصرف للصفة وزيادة الألف والنون والشرط موجود فيه لأنك لا تقول للمؤنثة سكرانة وإنما تقول سكرى وكذلك عطشان وغضبان فتقول امرأة عطشى وغضبى ولا تقول عطشانة ولا غضبانة فإن كان المذكر على فعلان والمؤنث على فعلانة صرفت فتقول هذا رجل سيفان أي طويل ورأيت رجلا سيفانا ومررت برجل سيفان فتصرفه لأنك تقول للمؤنثة سيفانة أي طويلة.
```

**Metadata:**
- primary_function: rule_statement ✓
- self_containment: FULL ✓

---

### GOLD-IA3-2: opinion_statement (98 words)
**Topic:** الخلاف في فعلية نعم وبئس
**Why exemplary:** Two-school debate (Basrans vs Kufans) with evidence on both sides + refutation of counter-evidence. Perfect scholarly dispute excerpt.

```arabic
مذهب جمهور النحويين أن نعم وبئس فعلان بدليل دخول تاء التأنيث الساكنة عليهما نحو نعمت المرأة هند وبئست المرأة دعد وذهب جماعة من الكوفيين ومنهم الفراء إلى أنهما اسمان واستدلوا بدخول حرف الجر عليهما في قول بعضهم نعم السير على بئس العير وقول
الآخر: والله ما هي بنعم الولد نصرها بكاء وبرها سرقة وخرج على جعل نعم وبئس مفعولين لقول محذوف واقع صفة لموصوف محذوف وهو المجرور بالحرف لا نعم وبئس والتقدير نعم السير على غير مقول فيه بئس العير وما هي بولد مقول فيه نعم الولد فحذف الموصوف والصفة وأقيم المعمول مقامهما مع بقاء نعم وبئس على فعليتهما
```

**Metadata:**
- primary_function: opinion_statement ✓
- self_containment: FULL ✓

---

### GOLD-IA3-3: definition (98 words)
**Topic:** تعريف الإضافة
**Why exemplary:** Complete grammatical definition covering the construct state: what gets deleted, what gets inflected, and the scholarly disagreement about the source of genitive case.

```arabic
‌‌الإضافة
نونا تلي الإعراب أو تنوينا … مما تضيف أحذف كطور سينا
والثاني أجرر وأنو من أو في إذا … لم يصلح إلا ذاك واللام خذا
لما سوى ذينك وأخصص أولا … أو أعطه التعريف بالذي تلا إذا أريد إضافة اسم إلى آخر حذف ما في المضاف من نون تلي الإعراب وهي نون التثنية أو نون الجمع وكذا ما ألحق بهما أو تنوين وجر المضاف إليه فتقول هذان غلاما زيد وهؤلاء بنوه وهذا صاحبه واختلف في الجار للمضاف إليه فقيل هو مجرور بحرف مقدر وهو اللام أو من أو في وقيل هو مجرور بالمضاف وهو الصحيح من هذه الأقوال
```

**Metadata:**
- primary_function: definition ✓
- self_containment: FULL ✓

---

### GOLD-IA3-4: rule_statement (136 words)
**Topic:** اكتساب المضاف التأنيث أو التذكير من المضاف إليه
**Why exemplary:** Explains a nuanced grammatical phenomenon (gender transfer in annexation) with Alfiyyah verse, rule, conditions, examples, and Quranic evidence.

```arabic
وربما أكسب ثان أولا … تأنيثا أن كان لحذف موهلا
قد يكتسب المضاف المذكر من المؤمث المضاف إليه التأنيث بشرط أن يكون المضاف صالحا للحذف وإقامة المضاف إليه مقامه نحو قطعت بعض أصابعه فبعض مذكر وقد أسند إليه قطعت بالتأنيث لأن بعض صالح للحذف إذ يصح أن تقول قطعت أصابعه والتأنيث أولى من التذكير لأن المضاف هنا بعض المضاف إليه ومثله {تلتقطه بعض السيارة} فبعض مذكر وقد أسند إليه الفعل بتاء التأنيث لأنه صالح للحذف وإقامة السيارة مقامه والتأنيث أولى لأن التقطت يعني الذين التقطوه هم بعض السيارة فاعتبر الأصل فكذا ما نحن فيه.
```

**Metadata:**
- primary_function: rule_statement ✓
- self_containment: FULL ✓

---

## Package 4: ext_39_masala (فقه — مسائل الجنائز)

### GOLD-M1: rule_statement (102 words)
**Topic:** الكفن أو ثمنه من مال الميت
**Why exemplary:** Complete masala with ruling + hadith evidence + narrative context (story of مصعب بن عمير at Uhud). Shows masala format at its best.

```arabic
34 - والكفن أو ثمنه من مال الميت ولو لم يخلف غيره لحديث خباب بن الأرت قال:
صحيح هاجرنا مع رسول الله صلى الله عليه وسلم في سبيل الله نبتغي وجه الله فوجب أجرنا على الله فمنا من مضى لم يأكل من أجره شيئا منهم مصعب بن عمير قتل يوم أحد فلم يوجد له شيء وفي رواية: ولم يترك إلا نمرة فكنا إذا وضعناها على رأسه خرجت رجلاه وإذا وضعناها على رجليه خرج رأسه فقال رسول الله صلى الله عليه وسلم:
"ضعوها مما يلي رأسه وفي رواية: غطوا بها رأسه واجعلوا على رجليه الإذخر"
ومنا من أينعت له ثمرته فهو يهديها أي يجتنيها.
```

**Metadata:**
- primary_function: rule_statement ✓
- self_containment: FULL ✓
- quoted_scholars: [{خباب بن الأرت, role: **narrator**}, {مصعب بن عمير, role: **narrator**}]

---

### GOLD-M2: opinion_statement (66 words)
**Topic:** الاغتسال من غسل الميت
**Why exemplary:** Concise masala with ruling + evidence + counter-evidence + precedent. Shows how البسام resolves apparent contradictions between hadith.

```arabic
31 - ويستحب لمن غسله أن يغتسل لقوله صلى الله عليه وسلم:
"من غسل ميتا فليغتسل ومن حمله فليتوضأ".
وظاهر الأمر يفيد الوجوب وإنما لم نقل به لحديثين:
الأول: قوله صلى الله عليه وسلم: "ليس عليكم في غسل ميتكم غسل إذا غسلتموه فإن ميتكم ليس بنجس فحسبكم أن تغسلوا أيديكم".
الثاني: قول ابن عمر رضي الله عنه:
كنا نغسل الميت فمنا من يغتسل ومنا من لا يغتسل.
```

**Metadata:**
- primary_function: opinion_statement ✓
- self_containment: FULL ✓

---

### GOLD-M3: evidence_hadith (101 words)
**Topic:** مشروعية الصلاة على المقتول حداً
**Why exemplary:** Powerful hadith narrative (the Juhayna woman) with ruling + emotional depth. Complete story with beginning and end.

```arabic
الثالث: من قتل في حد من حدود الله لحديث عامر بن حصين:
أن امرأة من جهينة أتت نبي الله صلى الله عليه وسلم وهي حبلى من الزنا فقالت: يا نبي الله أصبت حدا فأقمه علي فدعا نبي الله صلى الله عليه وسلم وليها فقال:
"أحسن إليها فإذا وضعت فأتني بها. ففعل فأمر بها نبي الله صلى الله عليه وسلم فشكت عليها ثيابها ثم أمر بها فرجمت ثم صلى عليها فقال له عمر: تصلي عليها يا نبي الله وقد زنت؟ فقال: "لقد تابت توبة لو قسمت بين سبعين من أهل المدينة لوسعتهم وهل وجدت توبة أفضل من أن جادت بنفسها لله تعالى؟ "
```

**Metadata:**
- primary_function: evidence_hadith ✓
- self_containment: FULL ✓

---

### GOLD-M4: evidence_rational (247 words)
**Topic:** عدم مشروعية قراءة القرآن عند القبور
**Why exemplary:** Masterful scholarly argument with multiple evidence types: absence-of-evidence argument, hadith, Quranic implications, and consensus of early scholars. Shows the fiqh masala genre at its most rigorous.

```arabic
120 - وأما قراءة القرآن عند زيارتها فمما لا أصل له في السنة بل الأحاديث المذكورة في المسألة السابقة تشعر بعدم مشروعيتها إذ لو كانت مشروعة لفعلها رسول الله صلى الله عليه وسلم وعلمها أصحابه لا سيما وقد سألته عائشة رضي الله عنها وهي من أحب الناس إليه صلى الله عليه وسلم عما تقول إذا زارت القبور؟ فعلمها السلام والدعاء ولم يعلمها أن تقرأ الفاتحة أو غيرها من القرآن فلو أن القراءة كانت مشروعة لما كتم ذلك عنها كيف وتأخير البيان عن وقت الحاجة لا يجوز كما تقرر في علم الأصول فكيف بالكتمان؟ ولو أنه صلى الله عليه وسلم علمهم شيئا من ذلك لنقل إلينا فإذا لم ينقل بالسند الثابت دل على أنه لم يقع.
ومما يقوي عدم المشروعية قوله صلى الله عليه وسلم:
"لا تجعلوا بيوتكم مقابر فإن الشيطان يفر من البيت الذي يقرأ فيه سورة البقرة" فقد أشار صلى الله عليه وسلم إلى أن القبور ليست موضعا للقراءة شرعا فلذلك حض على قراءة القرآن في البيوت ونهى عن جعلها كالمقابر التي لا يقرأ فيها كما أشار في الحديث الآخر إلى أنها ليست موضعا للصلاة أيضا وهو قوله:
"صلوا في بيوتكم ولا تتخذوها قبورا".
وترجم له البخاري بقوله: باب كراهية الصلاة في المقابر فأشار به إلى أنه يفيد كراهة الصلاة في المقابر فكذلك الحديث الذي قبله يفيد كراهة قراءة القرآن في المقابر ولا فرق ولذلك كان مذهب جمهور السلف كأبي حنيفة ومالك وغيرهم كراهة القراءة عند القبور وهو قول الإمام أحمد فقال أبو داود في مسائله ص 158:
سمعت أحمد سئل عن القراءة عند القبر؟ فقال: لا
```

**Metadata:**
- primary_function: evidence_rational ✓
- self_containment: FULL ✓

---

## Package 5: ext_46_qa (أصول النحو — سؤال وجواب)

### GOLD-Q1: rule_statement (101 words)
**Topic:** شروط الاحتجاج بكلام العرب
**Why exemplary:** Scholarly discussion about conditions for accepting Arabic linguistic evidence, with named authorities from multiple centuries. Shows usul al-nahw methodology.

```arabic
الفرع الثاني

قال الشيخ عز الدين بن عبد السلام من كبار أصحابنا الشافعية:
" اعتمد في العربية على أشعار العرب وهم كفار لبعد التدليس فيها كما اعتمد في الطب وهو في الأصل مأخوذ عن قوم كفار لذلك ".
فعلم أن العربي الذي يحتج بقوله لا بشترط فيه العدالة نعم تشترط في رواي ذلك.
وكثيرا ما يقع في (كتاب سيبويه) وغيره: " حدثني من لا أتهم " و " من لا أثق به " وينبغي الاكتفاء بذلك.
وعدم التوقف في القبول ويحتمل المنع.
وقد ذكر المرزباني عن أبي زيد النحوي قال: " كل ما قال سيبويه في كتابه (أخبرني الثقة) فأنا أخبرته ".
```

**Metadata:**
- primary_function: rule_statement ✓
- self_containment: FULL ✓

---

### GOLD-Q2: opinion_statement (100 words)
**Topic:** مصادر العلوم: السماع والاستنباط والانتزاع
**Why exemplary:** Brilliant interdisciplinary overview comparing how different sciences (fiqh, medicine, astronomy, music, grammar) derive knowledge. Unique content rarely excerpted this well.

```arabic
وقال صاحب (المستوفي) كل علم فبعضه مأخوذ بالسماع والنصوص، وبعضه بالاستنباط والقياس، وبعضه بالانتزاع من علم آخر.
قال (فالفقه بعضه بالنصوص الواردة في الكتاب والسنة، وبعضه بالاستنباط والقياس، والطب بعضه مستفاد من التجربة، وبعضه من علوم أخر، والهيئة بعضها من علم التقدير، وبعضها تجربة يشهد بها الرصد، والموسيقى جلها منتزع من علم الحساب، والنحو بعضه مسموع مأخوذ من العرب، وبعضه مستنبط بالفكر والروية، وهو التعليلات، وبعضه يؤخذ من صناعة أخرى.
كقولهم: الحرف الذي تختلس حركته هو في حكم المتحرك لا الساكن، فإنه مأخوذ من علم العروض.
وكقولهم: الحركات أنواع: صاعد عال، ومنحدر سافل ومتوسط بينهما، فإنه مأخوذ من صناعة الموسيقى) انتهى.
```

**Metadata:**
- primary_function: opinion_statement ✓
- self_containment: FULL ✓

---

### GOLD-Q3: evidence_hadith (53 words)
**Topic:** الإيماء إلى العلة اللغوية
**Why exemplary:** Hadith used as linguistic evidence (not legal evidence) — shows how usul al-nahw uses prophetic speech to derive grammar rules. Unique genre crossover.

```arabic
الثالث: الإيماء:
كما روي أن قوما من العرب أتوا النبي صلى الله عليه وسلم فقال: من أنتم؟
فقالوا نحن بنوا غيان.
فقال: بل أنتم بنو رشدان قال ابن جني: أشار إلى أن الألف والنون زائدتان، وإن كان لم يتفوه بذلك، غير أن اشتقاقه إياه من الغي بمنزلة قولنا نحن: إن الألف والنون فيه زائدتان.
```

**Metadata:**
- primary_function: evidence_hadith ✓ (hadith as linguistic evidence)
- self_containment: FULL ✓

---

### GOLD-Q4: definition (97 words)
**Topic:** الضرورة المستقبحة في الشعر
**Why exemplary:** Complete definition with multiple subtypes, scholarly authority (حازم), and poetic examples. Shows how usul al-nahw categorizes grammatical licenses.

```arabic
والضرورة المستقبحة: ما تستوحش منه النفس، كالأسماء المعدولة وما أدى إلى التباس جمع بجمع، كرد مطاعم إلى مطاعيم، او عكسه فإنه يؤدي إلى التباس مطعم بمطعام
قال حازم في (منهاج البلغاء):
" وأشد ما تستوحش منه النفس تنوين (أفعل من) "
قال: وأقبح ضرائر: الزيادة المؤدية لما ليس أصلا في كلامهم، كقوله: من حيث ما سلكوا أدنو فأنظور
أي أنظر.
أو الزيادة المؤدية لما يقل في الكلام، كقوله:
طأطأت شيمالي
أراد: شمالي.
وكذلك يستقبح النقص المجحف كقول لبيد:
درس المنا بمتالع فأبان أراد المنازل.
وكذلك العدول عن صيغة لأخرى كقول الحطيئة:
جدلاء محكمة من نسج سلام
أراد سليمان.
```

**Metadata:**
- primary_function: definition ✓
- self_containment: FULL ✓

---

## Summary Table

| ID | Package | Function | Words | Genre | Topic |
|----|---------|----------|-------|-------|-------|
| GOLD-T1 | taysir | rule_statement | 100 | hadith sharh | دعاء الاستفتاح |
| GOLD-T2 | taysir | opinion_statement | 101 | hadith sharh | التزهد المتكلف |
| GOLD-T3 | taysir | evidence_hadith | 100 | hadith sharh | حمل السلاح |
| GOLD-T4 | taysir | definition | 97 | hadith sharh | الهبة |
| GOLD-IA1-1 | ibn_aqil_v1 | rule_statement | 100 | nahw sharh | تثنية الموصول |
| GOLD-IA1-2 | ibn_aqil_v1 | opinion_statement | 98 | nahw sharh | أل الموصولية |
| GOLD-IA1-3 | ibn_aqil_v1 | definition | 99 | nahw sharh | الشبه المعنوي |
| GOLD-IA1-4 | ibn_aqil_v1 | narration | 78 | nahw sharh | خطبة الألفية |
| GOLD-IA3-1 | ibn_aqil_v3 | rule_statement | 100 | nahw sharh | فعلان وصرفه |
| GOLD-IA3-2 | ibn_aqil_v3 | opinion_statement | 98 | nahw sharh | نعم وبئس |
| GOLD-IA3-3 | ibn_aqil_v3 | definition | 98 | nahw sharh | الإضافة |
| GOLD-IA3-4 | ibn_aqil_v3 | rule_statement | 136 | nahw sharh | اكتساب التأنيث |
| GOLD-M1 | ext_39 | rule_statement | 102 | fiqh masala | الكفن |
| GOLD-M2 | ext_39 | opinion_statement | 66 | fiqh masala | غسل الميت |
| GOLD-M3 | ext_39 | evidence_hadith | 101 | fiqh masala | الصلاة على المحدود |
| GOLD-M4 | ext_39 | evidence_rational | 247 | fiqh masala | القراءة عند القبور |
| GOLD-Q1 | ext_46 | rule_statement | 101 | usul nahw | الاحتجاج |
| GOLD-Q2 | ext_46 | opinion_statement | 100 | usul nahw | مصادر العلوم |
| GOLD-Q3 | ext_46 | evidence_hadith | 53 | usul nahw | الإيماء |
| GOLD-Q4 | ext_46 | definition | 97 | usul nahw | الضرورة المستقبحة |
