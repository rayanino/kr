# KR Excerpting Engine — Opus versus GPT‑5.4: evidence‑based vergelijking en aanbeveling

## Context, datapunten en wat dit wél en niet bewijst

De repo bevat twee relevante runs met een natuurlijke “A/B‑achtige” overlap in bronmateriaal, maar de vergelijking is **niet** puur “model A vs model B” omdat meerdere variabelen tegelijk wisselen:

- **smoke_api** (±€3) gebruikt **GPT‑5.4 als primary** en **Opus als verify**. Het smoke‑protocol beschrijft expliciet deze stack en het doel (“sanity check” op 2 divisions per package). fileciteturn15file0L1-L1  
- **campaign_20260331** (±$97) gebruikt **Opus als primary** en **GPT‑5.4 als verify** (minstens voor de package‑config die ik kon inzien), en verwerkt een veel grotere corpus (2.303 excerpts). fileciteturn16file0L1-L1 fileciteturn33file0L1-L123  
- De campaign‑run bevat ook **pipeline/artefact‑problemen** die in smoke niet optreden (o.a. text_snippet prefix‑mismatches en word‑offset inconsistencies). Daardoor is “boundary quality” op basis van de opgeslagen JSONL niet alleen een modelvraag. fileciteturn95file0L1-L1 fileciteturn94file0L1-L1  

Wat je wél betrouwbaar kunt concluderen uit de bestaande artefacten:

- **Operationele stabiliteit/contract‑compliance**: smoke_api is op contract‑checks grotendeels “pass”, campaign_20260331 heeft meerdere “fail” checks. fileciteturn94file0L1-L1 fileciteturn95file0L1-L1  
- **Kwaliteitssignalen op schaal** (campaign): er is al een analyserapport met self‑containment verdelingen en een apart audit‑spoor voor taxonomy‑readiness en Arabic fidelity. fileciteturn70file0L1-L1 fileciteturn82file0L1-L1 fileciteturn83file0L1-L1  

Wat je níet hard kunt claimen zonder een “clean rerun” (zelfde commit + zelfde evaluator + identieke divisions + vaste verify‑policy):

- Dat Opus “betere” start/eind‑grenzen kiest dan GPT‑5.4 op inhoudelijke scholastische eenheden (nu is grenskwaliteit vermengd met contract‑bugs). fileciteturn95file0L1-L1  
- Dat Opus “nauwkeuriger” classificeert dan GPT‑5.4 op dezelfde tekst, omdat de beschikbare menselijke beoordeling in de repo vooral op **smoke taysir** zit. fileciteturn99file0L1-L1  

## Statistische kernsamenvatting van beide runs

### Corpus‑omvang en kosten

- smoke_api: **133 excerpts** over 5 packages, met kosten‑inschatting **2.93** (in het smoke‑protocol) en **errors = 0** in de smoke‑evaluatie. fileciteturn15file0L1-L1 fileciteturn17file0L1-L33  
- campaign_20260331: **2.303 excerpts** over dezelfde 5 packages, kosten‑inschatting **$96.87**. fileciteturn16file0L1-L33  

Per package (excerpt_count):

- smoke_api: ext_39_masala 22; ext_46_qa 39; ibn_aqil_v1 19; ibn_aqil_v3 25; taysir 28. fileciteturn17file0L1-L33  
- campaign_20260331: ext_39_masala 197; ext_46_qa 300; ibn_aqil_v1 241; ibn_aqil_v3 282; taysir 1283. fileciteturn16file0L1-L33  

### Contract‑/structuurchecks (boundary‑adjacent signal)

In de structural validator JSON’s zie je een sterk verschil in “mechanische correctheid”:

- smoke_api:  
  - word_offset_consistency: **pass (0 findings)**  
  - text_snippet_prefix_match: **pass (0 findings)**  
  - segment_indices_validity: **pass (0 findings)**  
  - function_taxonomy_validation: **pass (0 findings)** fileciteturn94file0L1-L1  
- campaign_20260331:  
  - word_offset_consistency: **fail (124)**  
  - text_snippet_prefix_match: **fail (1135)**  
  - segment_indices_validity: **fail (208)**  
  - physical_pages: **fail (104)**  
  - function_taxonomy_validation: **fail (283)** (o.a. secondary_functions ⊄ content_types) fileciteturn95file0L1-L1  

Belangrijk: een deel hiervan is vrijwel zeker **niet** “model boundary skill”, maar “pipeline snapshot / export completeness”. Bijvoorbeeld: segment_indices_validity faalt veelal door ontbrekende phase‑2 artefacten (“No matching Phase 2 grouping/classification file found”). fileciteturn95file0L1-L1  

### Granulariteits‑proxy: woord‑lengte distributie

De structural reports leveren per run een woord‑lengte audit:

- smoke_api: median_word_count **86**, upper_fence **331**, short_outlier_count **3**, long_outlier_count **6**. fileciteturn94file0L1-L1  
- campaign_20260331: median_word_count **64**, upper_fence **216.5**, short_outlier_count **48**, long_outlier_count **124**. fileciteturn95file0L1-L1  

Dit ondersteunt de observatie “Opus splitst gemiddeld fijner (kortere excerpts)” — maar: dit is ook beïnvloed door corpusmix. De percentages short‑outliers zijn overigens vergelijkbaar (~2%), dus het verschil zit vooral in het **median** niveau en het lagere upper_fence. fileciteturn94file0L1-L1 fileciteturn95file0L1-L1  

## Paired vergelijking Opus versus GPT‑5.4 op de overlappende packages

Hier behandel ik je zes vragen, maar ik splits expliciet: **(a) wat de repo‑artefacten hard ondersteunen** en **(b) waar de vergelijking onzuiver blijft**.

### Boundary quality

**Hard bewijs uit de validator:** in smoke_api zijn woord‑offsets en snippet‑prefixes consistent; in campaign_20260331 niet. fileciteturn94file0L1-L1 fileciteturn95file0L1-L1  

Dat zegt twee dingen:

- De **smoke output is betrouwbaarder als “ground truth” voor start_word/end_word mechanica** (wat je nodig hebt om boundary‑vergelijking überhaupt eerlijk te doen). fileciteturn94file0L1-L1  
- De **campaign output kan inhoudelijk prima zijn**, maar is als “boundary‑evidence” vervuild door export/normalisatieproblemen (bv. prefix‑normalisatie rond “‌‌”/ZWNJ). fileciteturn95file0L1-L1  

**Inhoudelijke boundary‑kwaliteit (scholastische eenheden):** de repo bevat voor smoke_api een boundary‑/conventie‑diagnostic die echte “scholarly boundary” failure modes benoemt (zoals te lange muqaddimah/editorial_note blokken, isnad‑fragmenten aan randen, enz.). fileciteturn54file0L1-L1  

Maar: er is geen symmetrische, menselijke boundary‑review voor campaign_20260331 per overlappende div_id’s. Daardoor kan ik niet met hoge zekerheid zeggen “Opus heeft betere grenzen” vs “GPT‑5.4 heeft betere grenzen” op inhoudelijke units. Wat ik wel kan zeggen: **de grootste grens‑gerelateerde risico’s die de tooling nu detecteert zitten in campaign_20260331**, maar dat is (waarschijnlijk) grotendeels pipeline‑gerelateerd. fileciteturn95file0L1-L1  

### Classification accuracy op dezelfde tekst

De meest directe menselijke evaluatie in de repo is een **Gemini‑review van de 28 smoke_api taysir excerpts** (dus: GPT‑5.4 primary output). Die review zegt:

- Primary_function meestal correct; vooral `evidence_hadith` en `definition` goed. fileciteturn99file0L1-L1  
- Concrete misclassificaties, o.a. “ما يؤخذ من الحديث” als `condition_exception` terwijl het primair `rule_statement` moest zijn, en “المعنى الإجمالي” foutief als `evidence_rational`. fileciteturn99file0L1-L1  

Voor campaign_20260331 is er geen vergelijkbare “28 excerpts hand‑graded” bijgevoegd; wél zie je op schaal taxonomy‑readiness flags die vaak **klassificatie‑adjacent** zijn. Bijvoorbeeld: zeer lange `editorial_note` en `structural_transition` blocks die waarschijnlijk inhoud dragen (“hidden rulings”) en narrators die als quoted_opinion behandeld worden. fileciteturn93file0L1-L1  

Conclusie (evidence‑based):  
- **GPT‑5.4 primary (smoke)** is “goed genoeg” qua taxonomy‑keuze, maar heeft voorspelbare failure modes rond “takeaways” en “general meaning” secties. fileciteturn99file0L1-L1  
- **Opus primary (campaign)** toont via flags dat er nog veel mis‑routing van “editorial/muqaddimah” en narrator‑rollen is (dit raakt function labeling en downstream retrieval), maar er ontbreekt een gelijke menselijke scorekaart om te zeggen “Opus is systematisch beter/slechter”. fileciteturn93file0L1-L1  

Pragmatisch: dit oordeel ondersteunt eerder **prompt‑hardening + few‑shot** (voor bekende failure classes) dan een dure model‑swap als primaire interventie.

### Self‑containment: FULL versus PARTIAL

Voor smoke_api taysir zegt de Gemini‑review expliciet dat self_containment labeling “high accuracy” is, met voorbeelden waar PARTIAL correct is (lijst‑achtige “additional benefits” zonder voorafgaande context; hadith‑text‑only). fileciteturn99file0L1-L1  

Voor campaign_20260331 is self_containment verdeling op schaal gerapporteerd in de campaign analysis (hier zit je 71–96% FULL per package). fileciteturn70file0L1-L1  

Wat ik wél “paired” kan inschatten uit consensus‑metadata:

- smoke_api: consensus_record_count **42**, met **24** self_containment decisions. fileciteturn94file0L1-L1  
- campaign_20260331: consensus_record_count **788**, met **521** self_containment decisions. fileciteturn95file0L1-L1  

Dit suggereert dat self‑containment een van de grootste bronnen van model‑disagreement is (zeker op grote corpora), dus “Opus scoort hoger FULL” kan deels zijn: *Opus labelt optimistischer*, niet noodzakelijk *Opus is feitelijk self‑contained*. Zonder een hand‑graded paired sample (FULL vs PARTIAL op exact dezelfde excerpt) is “wie heeft gelijk?” niet hard te beantwoorden.

Wat je wél al kunt automatiseren, en wat de repo al deels doet (taxonomy_readiness_flags):

- `orphaned_evidence` (hadith zonder takhrij/evidence_refs) is een sterke indicator dat een excerpt **functioneel PARTIAL** is in de kennislaag, zelfs als het tekstueel “begrijpelijk” is. fileciteturn93file0L1-L1  

### Scholar resolution: quoted_scholars

Op smoke_api taysir is de Gemini‑review expliciet positief over scholar resolution (meerdere grote namen correct gemapt). fileciteturn99file0L1-L1  

Op campaign_20260331 zie je op schaal een belangrijk probleem dat direct raakt aan “scholar resolution correctness”: **narrator_as_opinion** flags (bijv. entity["people","ابن عمر","companion narrator"], entity["people","أبي هريرة","companion narrator"], entity["people","علي","companion narrator"]) waar transmission‑formules in de buurt staan en de rol dus vermoedelijk “narrator” hoort te zijn, niet “quoted_opinion”. fileciteturn93file0L1-L1  

Dat betekent: zelfs als Opus “meer scholars” zou vinden, is “meer” niet automatisch “beter” zolang rol‑classificatie (narrator vs scholar/opinion) niet robuust is. De tooling toont dat dit probleem in campaign reëel en frequent genoeg is om high‑severity flags te genereren. fileciteturn93file0L1-L1  

### Granulariteit: over‑splitting versus juiste atomisatie

De median woord‑lengte is lager in campaign dan in smoke, wat wijst op fijnere atomisatie in de Opus‑run. fileciteturn95file0L1-L1 fileciteturn94file0L1-L1  

De echte vraag is: “is dit over‑splitting?” Het beste evidence in de repo hiervoor zijn de **taxonomy_readiness_flags**:

- zeer lange `editorial_note_long` en `structural_transition_long` excerpts worden geflagd omdat ze “verborgen rulings” kunnen bevatten (dus *onder‑splitting*), niet over‑splitting. fileciteturn93file0L1-L1  
- Tegelijk zijn er ook short‑outliers (campagne) en heel lange outliers (campagne), wat betekent dat de pipeline soms te agressief en soms te conservatief splitst. fileciteturn95file0L1-L1  

Mijn synthese: de data wijst eerder op **inconsistente granulariteit** dan op “Opus splitst altijd te veel”. In een 30‑book probe is consistentie belangrijker dan marginale per‑excerpt boundary “finesse”.

### Cost‑quality tradeoff en de rol van prompt‑improvements

De repo‑artefacten ondersteunen een strategie waarin je kwaliteit verhoogt zonder “Opus overal primary” te hoeven draaien:

- smoke_api laat zien dat de pipeline met GPT‑5.4 primary **contract‑sterk** kan draaien (veel checks pass) met lage kosten. fileciteturn94file0L1-L1 fileciteturn15file0L1-L1  
- campaign_20260331 toont dat de grootste problemen momenteel niet “inhoudelijk grensgevoel”, maar **artefact‑/validatie‑mismatches** en **taxonomy readiness issues** zijn — dingen die je eerder met prompt‑regels, validators en few‑shot kunt corrigeren. fileciteturn95file0L1-L1 fileciteturn93file0L1-L1  

Daarnaast bevat de repo al concrete prompt‑fixes voor GPT‑5.4 (bv. “ما يؤخذ من الحديث ⇒ rule_statement” en “المعنى الإجمالي ≠ evidence_rational”). fileciteturn99file0L1-L1  

## Campaign deep scholarly review en convention compliance op schaal

### Taysir: inhoudelijk patroon en classificatie‑risico’s

Wat we inhoudelijk wél hard hebben (zonder 1.283 excerpts handmatig te herlezen):

- De smoke taysir Gemini‑review bevestigt dat `hadith → gharib/definition → meaning → takeaways` vaak herkenbaar is, maar dat “takeaways” (ما يؤخذ من الحديث) een bekende failure class is voor primary_function. fileciteturn99file0L1-L1  
- In campaign (op schaal) zie je veel `editorial_note_long` flags in taysir, wat erop wijst dat “muqaddimah/samenvatting” soms als editorial_note wordt gevat terwijl het mogelijk substantieel fiqh‑materiaal bevat. fileciteturn93file0L1-L1  

Dat impliceert een bottleneck: **de prompt moet expliciet hadith‑sharh sub‑segments scheiden** (hadithtekst, gharib, maʿnā ijmālī, masāʾil/ فوائد) met vaste mapping naar primary_function/secondary_functions, anders blijft de output intern inconsistent zelfs als grenzen redelijk zijn.

### Convention compliance op schaal: wat tool‑audits al aantonen

Er zijn twee relevante audit‑sporen:

- Arabic fidelity (o.a. honorifics, isnad‑truncation): de flags file bevat concrete voorbeelden van missing honorifics en isnad‑fragmenten aan grenzen. fileciteturn92file0L1-L1  
- Taxonomy readiness (o.a. narrator_as_opinion, orphaned_evidence, long structural transitions): dit raakt rechtstreeks aan “companion narrator vs scholar role classification” en “evidence linkability”. fileciteturn93file0L1-L1  

Concreet bewijs dat deze issues bestaan in campaign:

- `narrator_as_opinion` high severity bij meerdere packages (ext_39_masala, taysir, ext_46_qa) met contexts die transmission‑taal hebben. fileciteturn93file0L1-L1  
- `orphaned_evidence` high severity in taysir (evidence_hadith zonder takhrij_data/evidence_refs). fileciteturn93file0L1-L1  
- Mis‑segmenteerde of te lange structurals (`structural_transition_long`) die mogelijk inhoud bevatten. fileciteturn93file0L1-L1  

Wat ik níet hard kan bewijzen uit de huidige audits: “bismillah/hamdala handling across all book openings” en “cross‑reference formula preservation” zijn niet als aparte audit‑categorieën zichtbaar in de meegecommit‑te summary JSON’s; als dit beleidskritisch is voor de 30‑book probe, moet er een expliciete audit‑regel voor worden toegevoegd (de conventies file geeft de norm, maar niet de meting). fileciteturn14file0L1-L1  

## Gold standard set: 20 exemplar excerpts voor few‑shot prompting

Onderstaande 20 exemplaren komen uit `integration_tests/campaign_20260331/analysis/gold_candidates.jsonl` (Tier A selectie). fileciteturn97file0L1-L1  
Formaat: JSONL‑achtig (één object per exemplar), geschikt om als few‑shot “correct output” te plakken in prompts.

```json
{"package":"taysir","genre":"fiqh_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_6_005_0_7","primary_function":"rule_statement","self_containment":"FULL","primary_text":"المعنى الإجمالي:\nهذا الحديث- كما ذكر النووي رحمه الله من قواعد الإسلام العامة وأصوله التي تبنى عليها الأحكام الكثيرة الجليلة.\nوهى أن الأصل بقاء الأشياء المتيقنة على حكمها، فلا يعدل عنها لمجرد الشكوك والظنون، سواء قويت الشكوك، أو ضعفت، مادامت لم تصل إلى درجة اليقين، وأمثلة ذلك كثيرة لا تخفى. ومنها هذا الحديث.\nفما دام الإنسان متيقنا للطهارة، ثم شك في الحدث فالأصل بقاء طهارته، وبالعكس فمن تيقن الحدث، وشك في الطهارة فالأصل بقاء الحدث، ومن هذا الثياب والأمكنة، فالأصل فيها الطهارة، إلا بيقين نجاستها.\nومن ذلك عدد الركعات في الصلاة، فمن تيقن ثلاثا مثلا، وشك في الرابعة، فالأصل عدمها.\nومن ذلك، من شك في طلاق زوجته. فالأصل بقاء النكاح. وهكذا من المسائل الكثيرة التي لا تخفى."}
{"package":"taysir","genre":"fiqh_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_6_018_0_34","primary_function":"opinion_statement","self_containment":"FULL","primary_text":"واختلفوا فيما عداها من التكبيرات.\nفذهب أكثر الفقهاء، إلى عدم وجوبها، لأن الواجب عندهم من أعمال الصلاة، ما ذكر في حديث المسيء في صلاته، وهذه التكبيرات لم تذكر فيه. قال في فتح الباري: الجمهور على ندبية ماعدا تكبيرة الإحرام.\nوذهب الإمام أحمد، وداود الظاهري، إلى وجوب تكبيرات الانتقال، مستدلين بإدامة النبي صلى الله عليه وسلم لها وقوله: \"صلوا كما رأيتموني أصلى\".\nولما روى أبو داود عن على بن يحيى بن خلاد عن عمه: أن النبي صلى الله عليه وسلم قال: \" لا تتم الصلاة لأحد من الناس حتى يتوضأ\" فذكر الحديث، وفيه ذكر التكبيرات وهو نص فيها.\nوأجابوا عن حديث المسيء، بأنه أتى في طريق أبي داود، والترمذي، والنسائي، أنه قال للمسيء: \" ثم يقول: الله اكبر، ثم يركع \" وذكر بقية التكبيرات."}
{"package":"taysir","genre":"fiqh_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_1_003_pre_0_9","primary_function":"evidence_hadith","self_containment":"FULL","primary_text":"الحديث الرابع\nوَعَنْهَا قالَت: دَخَلَ عَلَي رسول الله صلى الله عليه وسلم وعندي رجل، فَقَالَ: يَا عَاِئشَةُ، مَنْ هذَا؟ قُلْتُ: أخِي مِنَ الرضَاعَةِ.\nفَقالَ: \"يَا عَائشَة، انظُرنَ مَنْ إخْوَانكُن، فإنمَا الرضَاعَةُ مِنَ المجَاعَةِ\".\nالمعنى الإجمالي:\nدخل النبي صلى الله عليه وسلم على عائشة، فوجد عندها أخاها في الرضاعة- وهو لا يعلم عنه- فتغير وجهه صلى الله عليه وسلم، كراهةً لتك الحال، وغيرة على محارمه.\nفعلمت السبب الذي غيَّر وجهه، فأخبرته: أنه أخوها من الرضاعة.\nفقال: يا عائشة انظرْن وتثبتنَ في الرضاعة، فإن منها ما لا يسبب المحرمية، فلا بد من رضاعة ينبت عليها اللحم وتشتد بها العظام، وذلك أن تكون من المجاعة، حين يكون الطفل محتاجا إلى اللبن، فلا يتقوت بغيره، فيكون حينئذ كالجزء من المرضعة، فيصير كأحد أولادها، فّتثبت المحرمية."}
{"package":"taysir","genre":"fiqh_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_6_109_0_1","primary_function":"definition","self_containment":"FULL","primary_text":"فائدة:\nما هي الرضعة التي يحصل بها العدد، وما مقدارها؟\nالشارع ذكر الرضعة وأطلقها إلى ما يعرفه الناس ويعدونه رضعة، والرضعة، معناها، المرة من الرضعات، كالأكلة من الأكلات، والشربة من الشربات.\nوالناس لا يعدون الأكلة: إلا الوجبة التامة، سواء تخللها قيام، أو اشتغال يسير، أو قطعها لعارض، ثم رجع إليها، لأنه لم يكملها. فهكذا الرضعة.\nفالصحيح أنها لا تحسب رضعة إلا ما رضعه الصبي، ثم تركه لغير عارض ولا شاغل، بل عن طيب نفس وري.\nوهو مذهب الشافعي، وهى الرواية الثانية عن الإمام أحمد ونصرها (ابن القيم) في (الهدى) واختارها شيخنا (عبد الرحمن آل سعدي) .\nأما إذا نقلته المرضعة من ثدي إلى ثدي، أو جاءه ما يلهيه ثم تركه، أو نحو ذلك، فالصحيح أن هذه المصة، لا تعد رضعة."}

{"package":"ibn_aqil_v1","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_2_001_0_1","primary_function":"definition","self_containment":"FULL","primary_text":"الكلام وما يتألف منه ⌜1⌝\nكلامنا لفظ مفيد كاستقم … واسم وفعل ثم حرف الكلم (2)\nواحده كلمة والقول عم … وكلمة بها كلام قد يؤم (3) الكلام المصطلح عليه عند النحاة: عبارة عن اللفظ المفيد فائدة يحسن السكوت عليها فاللفظ جنس يشمل الكلام والكلمة والكلم ويشمل المهمل ك ديز والمستعمل ك عمرو ومفيد أخرج المهمل وفائدة يحسن السكوت عليها أخرج الكلمة وبعض الكلم وهو ما تركب من ثلاث كلمات فأكثر ولم يحسن السكوت عليه نحو إن قام زيد ولا يتركب الكلام إلا من اسمين نحو زيد قائم أو من فعل واسم كـ\" قام زيد\" وكقول المصنف \"استقم\" فإنه كلام مركب من فعل أمر وفاعل مستتر والتقدير استقم أنت فاستغنى بالمثال عن أن يقول: \"فائدة يحسن السكوت عليها فكأنه قال الكلام:هو اللفظ المفيد فائدة كفائدة استقم\"."}
{"package":"ibn_aqil_v1","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_2_002_0_9","primary_function":"rule_statement","self_containment":"FULL","primary_text":"وكل حرف مستحق للبنا … والأصل في المبني أن يسكنا (2)\nومنه ذو فتح وذو كسر وضم … كأين أمس حيث والساكن كم (3)\nالحروف كلها مبنية إذ لا يعتورها ما تفتقر في دلالتها عليه إلى إعراب نحو أخذت من الدراهم فالتبعيض مستفاد من لفظ من بدون الإعراب والأصل في البناء أن يكون على السكون لأنه أخف من الحركة ولا يحرك المبني إلا لسبب كالتخلص من التقاء الساكنين وقد تكون الحركة فتحة كأين وقام وإنّ وقد تكون كسرة كأمس وجير وقد تكون ضمة كحيث وهو اسم ومنذ وهو حرف إذا جررت به وأما السكون فنحو\n\"كم واضرب وأجل\".\nوعلم مما مثلنا به أن البناء على الكسر والضم لا يكون في الفعل بل في الاسم والحرف وأن البناء على الفتح أو السكون يكون في الاسم والفعل والحرف ⌜9⌝"}
{"package":"ibn_aqil_v1","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_2_009_pre_0_10","primary_function":"opinion_statement","self_containment":"FULL","primary_text":"وذكر ابن معط أن خبر دام لا يتقدم على اسمها فلا تقول لا أصاحبك ما دام قائما زيد والصواب جوازه قال الشاعر:\n66 - لا طيب للعيش ما دامت منغصة … لذاته بادكار الموت والهرم وأشار بقوله وكل سبقه دام حظر إلى أن كل العرب أو كل النحاة منع سبق خبر دام عليها وهذا إن أراد به أنهم منعوا تقديم خبر دام على ما المتصلة بها نحو لا أصحبك قائما ما دام زيد فمسلم وإن أراد أنهم منعوا تقديمه على دام وحدها نحو لا أصحبك ما قائما دام زيد وعلى ذلك حمله ولده في شرحه - ففيه\nنظر والذي يظهر أنه لا يمتنع تقديم خبر دام على دام وحدها فتقول لا أصحبك ما قائما دام زيد كما تقول لا أصحبك ما زيدا كلمت."}
{"package":"ibn_aqil_v1","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_2_000_0_5","primary_function":"editorial_note","self_containment":"FULL","primary_text":"وقد أردت أن أقوم لهذا الكتاب بعمل أتقرب به إلى الله تعالى، فرأيت - في أول الأمر - أن أتمم ما قصر فيه من البحث: فأبين اختلاف النحويين واستدلالاتهم ثم نظرت فإذا ذلك يخرج بالكتاب عن أصل الغرض منه، وقد يكون الإطناب باعثا على الازورار عنه، ونحن في زمن أقل ما فيه من عاب أنك لا تجد راغبا في علوم العرب إلا في القليل النادر، لأنهم قوم ذهبت مدنيتهم، ودالت دولتهم، وأصبحت الغلبة لغيرهم.\nفاكتفيت بما لا بد منه، من إعراب أبيات الألفية، وشرح الشواهد شرحا وسطا بين الاقتصار والإسهاب، وبيان بعض المباحث التي أشار إليها الشارح أو أغفلها بتة في عبارة واضحة وفي إيجاز دقيق، والتذييل بخلاصة مختصرة في تصريف الأفعال، فإن ابن مالك قد أغفل ذلك في \" ألفيته \", ووضع له لامية خاصة، سماها \" لامية الأفعال \"."}

{"package":"ibn_aqil_v3","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_3_001_0_3","primary_function":"definition","self_containment":"FULL","primary_text":"وإن يشابه المضاف يفعل … وصفا فعن تنكيره لا يعذل\nكرب راجينا عظيم الأمل … مروع القلب قليل الحيل وذي الإضافة اسمها لفظية … وتلك محضة ومعنوية\nهذا هو القسم الثاني من قسمي الإضافة وهو غير المحضة وضبطها المصنف بما إذا كان المضاف وصفا يشبه يفعل أي الفعل المضارع وهو كل اسم فاعل أو مفعول بمعنى الحال أو الاستقبال أو صفة مشبهة ولا تكون إلا بمعنى الحال فمثال اسم الفاعل هذا ضارب زيد الآن أو غدا وهذا راجينا ومثال اسم المفعول هذا مضروب الأب وهذا مروع القلب ومثال الصفة المشبهة هذا حسن الوجه وقليل الحيل وعظيم الأمل فإن كان المضاف غير وصف أو وصفا غير عامل فالإضافة محضة كالمصدر نحو عجبت من ضرب زيد واسم الفاعل بمعنى الماضي نحو هذا ضارب زيد أمس."}
{"package":"ibn_aqil_v3","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_3_004_0_3","primary_function":"rule_statement","self_containment":"FULL","primary_text":"وإن يكن صلة أل ففي المضى … وغيره إعماله قد ارتضى\nإذا وقع اسم الفاعل صلة للألف واللام عمل ماضيا ومستقبلا وحالا لوقوعه حينئذ موقع الفعل إذ حق الصلة أن تكون جملة فتقول هذا الضارب زيدا الآن أو غدا أو أمس هذا هو المشهور من قول النحويين وزعم جماعة من النحويين منهم الرماني أنه إذا وقع صلة لأل لا يعمل إلا ماضيا ولا يعمل مستقبلا ولا حال وزعم بعضهم أنه لا يعمل مطلقا وأن المنصوب بعده منصوب بإضمار فعل والعجب أن هذين المذهبين ذكرهما المصنف في التسهيل وزعم ابنه بدر الدين في شرحه أن اسم الفاعل إذا وقع صلة للألف واللام\nعمل ماضيا ومستقبلا وحالا باتفاق وقال بعد هذا أيضا ارتضى جميع النحويين إعماله يعني إذا كان صلة لأل."}
{"package":"ibn_aqil_v3","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_3_006_0_8","primary_function":"opinion_statement","self_containment":"FULL","primary_text":"وزعم ابن المصنف أن نيابة فعيل عن مفعول كثيرة وليست مقيسة بالإجماع وفي دعواه الإجماع على ذلك نظر فقد قال والده في التسهيل في باب اسم الفاعل عند ذكره نيابة فعيل عن مفعول وليس مقيسا خلافا لبعضهم وقال في شرحه وزعم بعضهم أنه مقيس في كل فعل ليس له فعيل بمعنى فاعل كجريح فإن كان للفعل فعيل بمعنى فاعل لم يتب قياسا كعليم وقال في باب التذكير والتأنيث وصوغ فعيل بمعنى مفعول على كثرته غير مقيس فجزم بأصح القولين كما جزم به هنا وهذا لا يقتضي نفي الخلاف.\nوقد يعتذر عن ابن المصنف بأنه ادعى الإجماع على أن فعيلا لا ينوب عن مفعول يعني نيابة مطلقة أي من كل فعل وهو كذلك بناء على ما ذكره والده في شرح التسهيل من أن القائل بقياسه يخصه بالفعل الذي ليس له فعيل بمعنى فاعل."}
{"package":"ibn_aqil_v3","genre":"nahw_sharh","excerpt_id":"exc_src_test0001_div_src_test0001_3_014_0_10","primary_function":"rule_statement","self_containment":"FULL","primary_text":"خير أبح قسم بأو وأبهم … وأشكك وإضراب بها أيضا نمى أي تستعمل أو للتخيير نحو خذ من مالي درهما أو دينارا وللإباحة نحو جالس الحسن أو ابن سيرين والفرق بين الإباحة والتخيير أن الإباحة لا تمنع الجمع والتخيير يمنعه وللتقسيم نحو الكلمة اسم أو فعل أو حرف وللإبهام على السامع نحو جاء زيد أو عمرو إذا كنت عالما بإلجائي منهما وقصدت الإبهام على السامع ومنه قوله تعالى: {وَإِنَّا أَوْ إِيَّاكُمْ لَعَلَى هُدىً أَوْ فِي ضَلالٍ مُبِينٍ} وللشك نحو جاء زيد أو عمرو إذا كنت شاكا في إلجائي منهما وللإضراب كقوله:\n295 - ماذا ترى في عيال قد برمت بهم … لم أحص عدتهم إلا بعداد كانوا ثمانين أو زادوا ثمانية … لولا رجاؤك قد قتلت أولادي\nأي بل زادوا."}

{"package":"ext_39_masala","genre":"fiqh_masala","excerpt_id":"exc_src_test0001_div_src_test0001_2_000_pre_0_14","primary_function":"rule_statement","self_containment":"FULL","primary_text":"12 - ولما كان الغالب على كثير من الناس في هذا الزمان الابتداع في دينهم ولا سيما فيما يتعلق بالجنائز كان من الواجب أن يوصي المسلم بأن يجهز ويدفن على السنة عملا بقوله تعالى: {يَا أَيُّهَا الَّذِينَ آمَنُوا قُوا أَنْفُسَكُمْ وَأَهْلِيكُمْ نَاراً وَقُودُهَا النَّاسُ وَالْحِجَارَةُ عَلَيْهَا مَلائِكَةٌ غِلاظٌ شِدَادٌ لا يَعْصُونَ اللَّهَ مَا أَمَرَهُمْ وَيَفْعَلُونَ مَا يُؤْمَرُونَ} .\nولذلك كان أصحاب رسول الله صلى الله عليه وسلم يوصون بذلك والآثار عنهم بما ذكرنا كثيرة تراجع في الأصل منها: عن حذيفة قال:\nإذا أنا مت فلا تؤذنوا بي أحدا فإني أخاف أن يكون نعيا وإني سمعت رسول الله صلى الله عليه وسلم ينهى عن النعي.\nولهذا قال النووي رحمه الله تعالى في الأذكار:\nويستحب له استحبابا مؤكدا أن يوصيهم باجتناب ما جرت العادة به من البدع في الجنائز ويؤكد العهد بذلك."}
{"package":"ext_39_masala","genre":"fiqh_masala","excerpt_id":"exc_src_test0001_div_src_test0001_3_010_0_3","primary_function":"evidence_hadith","self_containment":"FULL","primary_text":"الثاني: الشهيد وفيه أحاديث كثيرة أكتفي بذكر بعضها:\n1 - حسن عن عبد الله بن الزبير:\nأن رسول الله صلى الله عليه وسلم أمر يوم أحد بحمزة فسجي ببردة ثم صلى عليه فكبر تسع تكبيرات ثم أتي بالقتلى يصفون ويصلي عليهم وعليه معهم\n2 - عن عقبة بن عامر الجهني:\nأن النبي صلى الله عليه وسلم خرج يوما فصلى على أهل أحد صلاته على الميت بعد ثمان سنين كالمودع للأحياء والأموات ثم انصرف إلى المنبر فحمد الله وأثنى عليه فقال:\n\"إني فرط لكم وأنا شهيد عليكم وإن موعدكم الحوض وإني والله لأنظر إلى حوضي الآن وإن عرضه كما بين أيلة إلى الجحفة وإني أعطيت مفاتيح خزائن الأرض أو مفاتيح الأرض وإني والله ما أخاف عليكم أن تشركوا بعدي ولكن أخاف عليكم الدنيا أن تتنافسوا فيها وتقتتلوا فتهلكوا كما هلك من كان قبلكم\".\nقال: فكانت آخر نظرة نظرتها إلى رسول الله صلى الله عليه وسلم."}
{"package":"ext_39_masala","genre":"fiqh_masala","excerpt_id":"exc_src_test0001_div_src_test0001_3_007_0_6","primary_function":"condition_exception","self_containment":"FULL","primary_text":"ثالث عشر: ويستثنى أيضا مما ورد في تاسعا الزوجان فغنه يجوزك لكل منهما أن يتولى غسل الآخر إذ لا دليل يمنع منه والأصل الجواز ولا سيما انه مؤيد بحديثين:\nالأول: صحيح قول عائشة رضي الله عنها في حديثها المتقدم:\nلو كنت استقبلت من أمري ما استدبرت ما غسل النبي صلى الله عليه وسلم غير نسائه.\nالثاني: عنها أيضا قالت:\nرجع إلي رسول الله صلى الله عليه وسلم من جنازة بالبقيع وأنا أجد صداعا في رأسي وأقول: وارأساه فقال:\nبل أنا وارأساه ما ضرك لو مت قبلي فغسلتك وكفنتك ثم صليت عليك ودفنتك."}
{"package":"ext_39_masala","genre":"fiqh_masala","excerpt_id":"exc_src_test0001_div_src_test0001_3_008_0_12","primary_function":"rule_statement","self_containment":"FULL","primary_text":"42 - ولا يجوز المغالاة في الكفن ولا الزيادة فيه على الثلاثة لأنه خلاف ما كفن فيه رسول الله صلى الله عليه وسلم كما تقدم في المسألة السابقة وفيه إضاعة للمال وهو منهي عنه ولا سيما والحي أولى به قال رسول الله صلى الله عليه وسلم:\n\"إن الله كره لكم ثلاثا: قيل وقال وإضاعة المال وكثرة السؤال\".\nويعجبني بهذه المناسبة ما قاله العلامة أو الطيب في الروضة الندية 1 / 165.\nوليس تكثير الأكفان والمغالاة في أثمانها بمحمود فإنه لولا ورود الشرع به لكان من إضاعة المال لأنه لا ينتفع به الميت ولا يعود نفعه على الحي ورحم الله أبا بكر الصديق حيث قال: إن الحي أحق بالجديد لما قيل له عند تعيينه لثوب من أثوابه في كفنه: إن هذا خلق."}

{"package":"ext_46_qa","genre":"usul_al_nahw","excerpt_id":"exc_src_test0001_div_src_test0001_5_000_0_0","primary_function":"definition","self_containment":"FULL","primary_text":"المسألة الثانية\n\nللنحو حدود شتى، وأليقها بهذا الكتاب قول ابن جني (في الخصائص):\n\" هو انتحاء سمت كلام العرب في تصرفه من إعراب وغيره كالتثنية، والجمع، والتحقير، والتكسير، والإضافة، والنسب، والتركيب، وغير ذلك ليلحق من ليس من أهل اللغة العربية بأهلها في الفصاحة، فينطق بها، وإن لم يكن منهم، وإن شد بعضهم عنها رد به إليها.\nوهو في الأصل مصدر شائع، أي نحوت نحوا، كقولك، قصدت قصدا ثم خص به انتحاء هذا هذا القبيل من العلم، كما أن الفقه، في الأصل مصدر فقهت الشيء، أي عرفته، ثم خص به علم الشريعة من التحليل والتحريم، وكما أن بيت الله خص به الكعبة، وإن كانت البيوت كلها لله، وله نظائر في قصر ما كان شائعا في جنسه على أحد أنواعه. وقد استعملته العرب ظرفا، وأصله المصدر. انتهى.\""}
{"package":"ext_46_qa","genre":"usul_al_nahw","excerpt_id":"exc_src_test0001_div_src_test0001_3_010_0_29","primary_function":"rule_statement","self_containment":"FULL","primary_text":"الثالثة\n\nقال في الخصائص:\nأكثر العلل عندنا مبناها على الإيجاب بها كنصب الفضلة أو ما شابهها ورفع العمدة وجر المضاف إليه وغير ذلك وعلى هذا مفاد كلام العرب.\nوضرب آخر يسمى علة وإنما هو في الحقيقة سبب يجوزه ولا يوجبه.\nومن ذلك أسباب الإمالة فإنها علة الجواز لا الوجوب.\nوكذا علة قلب واو (وقتت) همزة وهي كونها انضمت ضما لازما فإنها مع ذلك يجوز إبقاؤها واو فعلتها مجوزة لا موجبة \"\nقال:\nوكذا كل موضع جاز فيه إعرابان فأكثر كالذي يجوز جعله بدلا وحالا وذلك النكرة بعد معرفة هي في المعنى هي نحو مررت بزيد رجل صالح ورجلا صالحا فإن علته لجواز ما جاز لا لوجوبه \" انتهى\nفظهر بهذا الفرق بين العلة والسبب وأن ما كان موجبا يسمى علة وما كان مجوزا يسمى سببا."}
{"package":"ext_46_qa","genre":"usul_al_nahw","excerpt_id":"exc_src_test0001_div_src_test0001_3_010_0_33","primary_function":"opinion_statement","self_containment":"FULL","primary_text":"وقال بعضهم يثبت في محل النص بالنص وفيما عداه بالعلة وذلك نحو النصوص المنفولة عن العرب المقيس عليها بالعلة الجامعة في جميع أبواب العربية.\nواستدل لذلك بأن النص مقطوع به والعلة مظنونة وإحالة الحكم على المقطوع له أولى من إحالته على المظنون.\nولا يجوز أن يكون الحكم ثابتا بالنص والعلة معا لأنه يؤدي\nإلى أن يكون الحكم مقطوعا به مظنونا في حال واحدة محال.\nوأجيب عن هذا الاستدلال بأن الحكم إ نما يثبت بطريق مقطوع به وهو النص ولكن العلة هي التي دعت إلى إثبات الحكم فنحن نقطع على الحكم بكلام العرب ونظن أن العلة هي التي دعت الواضع إلى الحكم فالظن لم يرجع إلى ما يرجع إليه القطع بل هما متغايران فلا منافاة \".\nانتهى كلام ابن الأنباري."}
{"package":"ext_46_qa","genre":"usul_al_nahw","excerpt_id":"exc_src_test0001_div_src_test0001_6_001_0_0","primary_function":"refutation","self_containment":"FULL","primary_text":"تنبيه\nكان قوم من النحاة المتقدمين يعيبون على عاصم وحمزة وابن عامر قراءات بعيدة في العربية وينسبونهم إلى اللحن.\nوهم مخطئون في ذلك، فإن قراءاتهم ثابتة بالاسانيد المتواترة الصحيحة التي لا مطعن فيها، وثبوت ذلك دليل على جوازه في العربية، وقد رد المتأخرون منهم ابن مالك، على من عاب عليهم ذلك بأبلغ رد، واختار جواز ما وردت به قراءاتهم في العربية، وإن منعه الأكثرون مستدلا به من ذلك احتجاجه على جواز العطف على الضمير المجرور من غير إعادة الجار بقراءة حمزة: (تساءلون به والأرحام).\nوعلى جواز الفصل بين المضاف والمضاف إليه بمفعوله بقراءة ابن عامر:\n(قتل أولادهم شركائهم).\nوعلى جواز سكون لام الأمر بعد (ثم) بقراءة حمزة:\n(ثم ليقطع)"}
```

## Aanbeveling voor de 30‑book probe

Mijn aanbeveling is expliciet gebaseerd op de *meest load‑bearing* feiten uit de repo:

1. **Kies GPT‑5.4 als primary voor de 30‑book probe, met Opus als gerichte verify/escalation**, niet als primary‑default.  
   Reden: smoke_api met GPT‑5.4 primary is contract‑stabiel (meerdere kernchecks “pass”), en de kwalitatieve tekortkomingen die we expliciet zien (taysir misclassificaties) zijn **promptbaar** (duidelijke error classes met eenvoudige regels/few‑shot). fileciteturn94file0L1-L1 fileciteturn99file0L1-L1  

2. **Behandel campaign_20260331 niet als doorslaggevend bewijs “Opus is beter”, maar als signaal dat je evaluator + audits op schaal waardevol zijn.**  
   Reden: campaign heeft veel structurele fails (prefix/offset, segment provenance) die de boundary‑vergelijking vervuilen; tegelijk leveren taxonomy_readiness/audits op campaign wél nuttige kwaliteits‑bottlenecks op (narrator_as_opinion, orphaned_evidence, long editorial/structural blocks). fileciteturn95file0L1-L1 fileciteturn93file0L1-L1  

3. **Investeer eerst in prompt‑hardening + gold set (boven) + audit‑gates, vóór je 3× kosten accepteert.**  
   Concreet: neem de Gemini‑regels uit smoke taysir (takeaways ≠ condition_exception; meaning ≠ evidence_rational) als harde regels en voeg de 20 Tier‑A exemplaren toe als few‑shot. fileciteturn99file0L1-L1 fileciteturn97file0L1-L1  

4. **Gebruik Opus doelgericht waar de audit‑severities “high” zijn**, met name:
   - narrator_as_opinion (rol‑disambiguatie rond isnad/transmission) fileciteturn93file0L1-L1  
   - orphaned_evidence (linkability naar takhrij/evidence refs) fileciteturn93file0L1-L1  
   - lange structural_transition/editorial_note blokken die mogelijk inhoud verbergen fileciteturn93file0L1-L1  

Als je één duidelijke “model‑keuze” moet maken voor de probe: **GPT‑5.4 primary**. De kwaliteitssprong die je nodig hebt ligt (volgens de repo‑evidence) meer in **prompt/validator/audit‑sturing** dan in “duurste model overal”. fileciteturn99file0L1-L1 fileciteturn93file0L1-L1