# Production Batch Book Selection Strategy for the KR Arabic Scholarly Text Pipeline

## Context from the KR repository and the corpus constraints

The excerpting pipeline you are scaling is already architected as a **three-phase, one-source-at-a-time** system: deterministic assembly (Phase 1), LLM classification/grouping (Phase 2), and deterministic + LLM enrichment/verification/validation (Phase 3). fileciteturn3file0L1-L1 This matters for book selection because the highest-risk failures won’t just be “bad Arabic”; they will be **structural boundary failures** (Phase 1 chunking and layer rebasing) and **genre-misaligned excerpt boundaries or function labels** (Phase 2/3), which can surface only when a text forces the pipeline into awkward segmentation decisions. fileciteturn3file0L1-L1

The repo’s status notes confirm (a) the two validated texts are already being used as empirical anchors (“taysir + ibn_aqil”), and (b) the system is now operating in a “hardening → smoke analysis → deep hardening → multi-book run” rhythm with strict data-preservation and gating. fileciteturn4file0L1-L1 In other words: the production batch should be treated as an **instrumented “coverage+stress” run**, not as a random first slice of the library.

From the normalization corpus sweep summary (7475 texts), four corpus facts are directly selection-relevant:

- **Size variance is extreme** (content units min 1, max 14587; mean 276; median 168). This makes “page count constraints” operationally non-trivial: you must enforce 50–5000 pages (or a proxy like `content_units`) at selection-time, not after runs have already started. fileciteturn9file0L1-L1  
- **Multi-layer segments exist but are not dominant** (401/7475 ≈ 5.4% of books flagged with multi-layer segments). That implies a small number of carefully chosen multi-layer books can cover a disproportionate amount of risk. fileciteturn9file0L1-L1  
- The corpus is rich in **hadith-heavy, Quran-heavy, and verse-heavy pages** (large aggregate counts). That supports prioritizing hadith-collection structure, Qur’anic citation density, and verse handling early. fileciteturn9file0L1-L1  
- There are specific “known-problem” tails (e.g., high page loss outliers, low Arabic ratio outliers) that can be used as deliberate adversarial probes after Tier 1 stability. fileciteturn9file0L1-L1  

A key practical constraint: your **selection must be simultaneously** (i) structurally covering, (ii) difficulty-calibrating, and (iii) immediately useful to a Hanbalī-focused student. This forces a design choice: the initial batch cannot be a maximal combinatorial test set (too large), so it must be a **Pareto-balanced subset** driven by (a) coverage lower bounds, (b) canonical-curriculum centrality, and (c) failure-mode targeting.

## Branch A — Coverage testing frameworks for heterogeneous document collections

### Combinatorial coverage testing and covering arrays

In software testing, **pairwise (2-way) combinatorial testing** aims to cover all pairs of parameter values (e.g., all pairs across “science × family”, “science × layer”, “family × layer”) because many failures are triggered by interactions of only a few factors. NIST’s combinatorial testing guidance formalizes this as building **covering arrays** for t-way interaction coverage. citeturn0search2turn0search0turn0search4

Applied naively to your dimensions as independent factors:

- Sciences = 18  
- Structural families = 7  
- Layers = 4  

Then:

- Full **3-way coverage** would require covering all triples: 18×7×4 = **504** combinations. The absolute floor is 504 books (one per triple), which is far beyond your 20–50 budget.
- Full **pairwise coverage** requires covering all pairs:
  - Science×Family: 18×7 = 126  
  - Science×Layer: 18×4 = 72  
  - Family×Layer: 7×4 = 28  
  Total distinct pairs = 226.

A strict lower bound for pairwise coverage is **≥126 books**, because every test book can only instantiate **one** (science, family) pair; to cover all 126 such pairs at least once, you need at least 126 items. This shows that “full pairwise over the full cartesian product” is infeasible under the budget.

But your taxonomy is not truly independent: **science → family is largely deterministic** (e.g., Nahw is always [RUL]). So the meaningful interactions to cover are closer to:
- science×layer (does each science appear as matn/sharḥ/ḥāshiyah/taʿlīqah in the corpus and does the pipeline handle each?)
- family×layer (does the pipeline handle each structural family across layers?)

That “constrained model” is closer to **72 potential science×layer cells** and **28 family×layer cells**. Even 72 is still above the 30–50 target, so you need an explicit “minimum viable coverage” notion.

### Stratified sampling and corpus representativeness

In corpus design, “representativeness” depends less on raw sample size and more on (a) defining the target population and (b) using stratified sampling along the variables that drive variability. Biber explicitly argues that corpus building often proceeds in **cycles**: theoretical stratification → pilot corpus → empirical revision. citeturn2search0

Translating that into your pipeline setting:

- The “population” is not “all Shamela books”; it is “all distinct structural behaviors that can break excerpting.”  
- Your strata are not only (science, family, layer), but also measurable structural features already computed/available in KR artifacts: size (`content_units`), multi-layer ratio, diacritics density, and mismatch indicators (page-loss, low Arabic ratio, division overlap warnings). fileciteturn9file0L1-L1

### Smoke tests as document-pipeline gates

A smoke test is a *small test suite covering main functionality that determines whether the system is stable enough for deeper testing*. citeturn0search1  
For a document pipeline, the analogue is: pick a handful of books that exercise the critical path (parsing → chunk assembly → classification → enrichment → validation) across at least a few structural families, then require “no catastrophic failures” (schema violations, chunk-loss, broken layer rebasing, runaway costs) before scaling the batch.

### Published validation patterns from OCR/document analysis and text digitization evaluation

Although you are not doing OCR on page images, OCR evaluation literature is still methodologically useful because it deals with “heterogeneous document inputs” and emphasizes **end-user usefulness metrics**, not just raw correctness. Tanner et al. (British Library newspaper OCR case study) argues for measuring quality in ways tied to user tasks (e.g., word/significant-word accuracy for search usefulness). citeturn1search4  
In document analysis competitions like ICDAR, datasets are deliberately built to stress **layout complexity** and evaluate systems under varied document conditions (page segmentation, classification, table recognition). citeturn1search0turn1search8

The transferable principle for KR: your first production batch should behave like a “benchmark suite” spanning the structural phenomena that matter: dense isnād blocks, entry-boundary heavy dictionaries, poetry formatting, and multi-layer interleaving.

### Branch A implications for batch size

Given budget (20–50 books) and infeasibility of full cartesian pairwise coverage, the minimum practical target is:

- **All 7 family×layer pairs you can realistically represent**, prioritizing:
  - every family represented at least once as **Matn** and **Sharḥ** (baseline),
  - **Hashiyah** coverage for at least [ARG] and [RUL] (highest multi-layer confusion risk),
  - **Taʿlīqah** coverage at least once (format variance and editorial voice shifts).
- **All 18 sciences represented at least once** across the full batch (not necessarily Tier 1).

This leads naturally to **~40 books** (10+15+15), which is also cost-aligned ($3/book ≈ $120 total).

## Branch B — Canonical texts and the mutūn → shurūḥ → ḥawāshī architecture

### What “canonical test corpus” means operationally

In classical instruction, sciences are often taught via a progression:  
**foundational matn (memorized / mastered) → sharḥ (explication / proofs / expansions) → ḥāshiyah (meta-clarification, dispute resolution, technical refinements)**, sometimes supplemented by taʿlīqāt (marginal glosses, lecture notes, or super-commentarial notes). Your system’s layer taxonomy is effectively a computational restatement of this pedagogy.

Because publicly accessible, primary-textbook lists from the exact flagship institutions are inconsistently surfaced online, the best evidence you can practically triangulate is:

- **Deobandi-style Dars-e-Nizami sequences** (representative of the South Asian madrasa curriculum tradition associated with Darul Uloom Deoband), which explicitly lists canonical texts used across logic, usul, tafsir, hadith, and more. citeturn15search0  
- **Al-Azhar’s e-learning portal**, which at least provides structured course descriptors (e.g., “Usul al-Fiqh (1)”) showing continuity of the traditional discipline structure. citeturn19view0  
- **Islamic University of Madinah official study-plan page** showing a structured early-program distribution across Qur’an, fiqh, tawḥīd, tajwīd, sīrah, tafsīr, naḥw, ḥadīth, and muṣṭalaḥ. citeturn9view0  
- Modern ijāzah-style program syllabi that still select classic mutūn (e.g., Nuzhat al-Naẓar, Muqaddimah Ibn al-Ṣalāḥ). citeturn6search4turn6search6  

### Canonical nominations by science

Below is a **canonical nomination map** (matn → sharḥ → ḥāshiyah) intended as the “failure-if-missing” backbone. Many matūn are shorter than 50 pages; those remain canonical but may be excluded from the initial production batch under your page constraint.

- **Fiqh**
  - Hanbalī matn: Zād al-Mustaqniʿ / Dalīl al-Ṭālib (common Hanbalī teaching anchors; Zād is especially common in Hanbalī study tracks and appears directly in KR manifests). fileciteturn12file0L1-L1  
  - Sharḥ: al-Rawḍ al-Murbiʿ (on Zād) (common Hanbalī intermediate sharḥ).  
  - Ḥāshiyah: Ibn Qāsim’s marginalia on al-Rawḍ; al-Khalūṭī on Muntahā al-Irādāt (both appear in KR manifests). fileciteturn12file0L1-L1  

- **Uṣūl al-Fiqh**
  - Matn: al-Waraqāt (very common beginner matn) and/or Rawḍat al-Nāẓir (Hanbalī-leaning usul).  
  - Sharḥ: Sharḥ al-Waraqāt (al-Maḥallī) (appears in KR manifests). fileciteturn12file0L1-L1  
  - Ḥāshiyah: Ḥāshiyat al-ʿAṭṭār on Jamʿ al-Jawāmiʿ is a classical “advanced usul” hashiya pattern (also present in corpus manifests). fileciteturn12file0L1-L1  

- **ʿAqīdah**
  - Matn: al-ʿAqīdah al-Ṭaḥāwiyyah (ubiquitous across institutions).  
  - Sharḥ: Sharḥ al-Ṭaḥāwiyyah (Ibn Abī al-ʿIzz) (present in KR manifests in multiple editions). fileciteturn12file0L1-L1  
  - Ḥāshiyah: where used, often later scholastic marginalia; in practice, for your batch, a dense sharḥ often stands in for “aqidah complexity” under your page constraint.

- **ʿIlm al-Kalām**
  - Matn: texts like Tahdhīb al-Manṭiq wa-l-Kalām (logic+kalam blend) are canonical in madrasa logic-kalam sequences. citeturn15search0  
  - Sharḥ: Sharḥ al-ʿAqāʾid al-Nasafiyyah appears explicitly in Dars-e-Nizami-style sequences. citeturn15search0  

- **ʿIlm al-Farāʾiḍ**
  - Matn: al-Sirājiyyah (classically used inheritance primer in madrasa settings), or al-Raḥbiyyah with a sharḥ (often too short as a standalone).  
  - Sharḥ/notes: use a longer sharḥ edition to satisfy the 50-page constraint.

- **Manṭiq**
  - Matn: Isāghūjī (very common) and/or Sullam al-ʿUlūm; also Tahdhīb al-Manṭiq is explicitly named in Dars-e-Nizami-style lists. citeturn15search0  
  - Sharḥ/ḥāshiyah: Qutbī / Shams Bāzigha / other scholastic layers occur in advanced madrasa logic sequences. citeturn15search0  

- **Tārīkh/Sīrah**
  - Matn: al-Raḥīq al-Makhtūm is explicitly present in KR manifests and provides immediate study value while being structurally narrative. fileciteturn12file0L1-L1  
  - Taʿlīqah: commentary/notes on sīrah texts (e.g., “taʿlīq ʿalā…”) appear as a distinct layer in KR manifests. fileciteturn12file0L1-L1  

- **Tafsīr**
  - Sharḥ layer is the default, since tafsīr functions as commentary on the Qur’an.  
  - Canonical anchors in curricula include Jalālayn and Bayḍāwī (in madrasa sequences) and Ibn Kathīr (widely read). citeturn15search0  

- **Ṭabaqāt/Tarājim**
  - Matn/entry-based: Ṭabaqāt works (e.g., Ṭabaqāt al-Ḥanābilah) are essential “entry boundary” genres and high scholarly utility for hadith/rijāl study.

- **Muṣṭalaḥ al-Ḥadīth**
  - Matn: Muqaddimah Ibn al-Ṣalāḥ is explicitly used in advanced hadith-principles curricula. citeturn6search6  
  - Sharḥ: Nuzhat al-Naẓar (Ibn Ḥajar) is used as an intermediate teaching text. citeturn6search4  

- **Takhrīj/Rijāl**
  - Entry-based narrator works like Taqrīb al-Tahdhīb are standard scaffolding for rijāl referencing.  
  - Specialized “pattern” works (e.g., al-Mudallisīn, ʿilal collections) represent advanced difficulty.

- **Ḥadīth collections**
  - Canonical collections in madrasa “dawrah” sequences include the Ṣiḥāḥ/Sunan; Dars-e-Nizami-style curricula explicitly list the Ṣiḥāḥ al-Sittah. citeturn15search0  

- **Naḥw**
  - Matn: Qaṭr al-Nadā (Ibn Hishām) is an intermediate grammar text with enough length to satisfy constraints.  
  - Sharḥ: Sharḥ Ibn ʿAqīl (already validated). fileciteturn4file0L1-L1  
  - Ḥāshiyah: dense marginalia like al-Ṣabbān’s hashiya represent the maximal “layer interleaving” stress.

- **Ṣarf**
  - Matn: Shadhā al-ʿUrf (common medium-length morphology primer).

- **Lughah/Balāghah**
  - Matn: Mukhtaṣar al-Maʿānī appears in madrasa rhetoric sequences. citeturn15search0  
  - Dictionary layer (entry-based): al-Qāmūs al-Muḥīṭ provides the “lexicon as encyclopedia” structure.

- **Qirāʾāt/Tajwīd**
  - Matn: al-Taysīr fī al-Qirāʾāt al-Sabʿ and related traditions are classical anchors.  
  - Sharḥ: Sharḥ al-Jazarīyyah appears directly in KR corpus sweep outlier lists. fileciteturn9file0L1-L1  

- **Adab/Shiʿr**
  - Matn: Maqāmāt al-Ḥarīrī (rhymed prose) and Dīwāns.  
  - Sharḥ: commentaries on Dīwāns (e.g., al-Wāḥidī on al-Mutanabbī) create explicit “poetry + commentary” structure.

- **Taṣawwuf**
  - Matn: al-Risālah al-Qushayriyyah is a widely taught classical tasawwuf manual and a strong “sequential-progressive” exemplar.

## Branch C — Processing difficulty drivers and likely failure modes

Branch C is about *why* certain genres are hard for machines. Here, “hard” means: high likelihood of boundary ambiguity, layer confusion, or information loss that violates excerpt self-containment or metadata integrity.

### Hadith isnād complexity and long-structure limits

Hadith texts embed isnāds (chains of narrators) that behave like structured citations. Contemporary NLP work on automatic isnād extraction treats isnāds as a distinct detection task and notes practical constraints for full-document modeling in long texts. citeturn3search2  
Datasets like Multi-IsnadSet explicitly describe hadith as consisting of isnād, opening segment, and matn, and represent isnād structure as graphs—evidence that the structure is non-trivial and inherently relational. citeturn3search0turn3search5

**Likely KR failure modes:** splitting a hadith across chunk boundaries; misclassifying isnād-heavy passages as “biography-like” or “argument”; dropping narrator sequences due to formatting; or producing excerpts that omit the legal “point” because the chain overwhelms the excerpt window.

### Multi-layer interleaving in sharḥ/ḥāshiyah

Even without OCR, sharḥ/ḥāshiyah texts feature:
- inconsistent “qāla/aqūlu” markers,
- embedded quotations,
- alternating voices with minimal explicit attribution.

This aligns with the KR corpus fact that only ~5% of books are detected as multi-layer, so **multi-layer texts should be treated as high-risk special cases** rather than “more of the same.” fileciteturn9file0L1-L1  

**Likely failure modes:** layer rebasing errors, merged voices inside a single excerpt, or excerpt boundaries that capture half of an objection but not its resolution (high “puzzle excerpt” risk).

### Entry-boundary detection in dictionaries, ṭabaqāt, and tarājim

OpenITI’s schema explicitly treats “dictionary units” and “biographies” as distinct structural objects that benefit from markup, underscoring how important entry segmentation is for Arabic historical/biographical genres. citeturn5search0  
Arabic biographical dictionaries (tarājim) are a massive genre where the “tarjamah” is a characteristic short notice unit, distinct from longer “sīrah.” citeturn5search3  

**Likely failure modes:** entry boundary bleed (two biographies merged), mis-detecting headers, lost dates/nisbahs, and misgrouping into teaching units that don’t align with a tarjamah’s atomicity.

### Poetry as structure and meter

Arabic poetic processing is difficult enough that specialized systems exist purely to identify meter/rhyme; even meter identification is described as a complicated task requiring expertise. citeturn3search3  

**Likely KR failure modes:** breaking bayt boundaries, stripping punctuation/diacritics that distinguish readings, treating hemistich separations as “noise,” or misclassifying poetic sections as prose argument.

### Tables and calculation structure (farāʾiḍ)

Farāʾiḍ texts frequently include tabular or quasi-tabular layouts for inheritance cases. Table extraction/recognition is a major subfield in document analysis and is benchmarked directly in ICDAR table detection/recognition tasks. citeturn1search8  

**Likely failure modes:** loss of column alignment in normalization, numeric/ratio corruption, and boundaries that separate the “case statement” from its computed shares.

### Waqf markers and qirāʾāt signals

Waqf signs (e.g., ج، قلى، صلى، لا، م) guide recitation pauses and differ across muṣḥafs due to scholarly and regional variation. citeturn4search3  
Dataset practice also exists for using Unicode waqf markers as segmentation points, implying they are computationally meaningful but also script-dependent. citeturn4search2  

**Likely failure modes:** mis-tokenization of special symbols, normalization stripping/altering waqf markers, or inconsistent segmentation if markers differ across editions.

## Synthesis — A ranked 40-book production batch with tiers and coverage matrix

### Synthesis logic

This list is built to satisfy three constraints simultaneously:

- **Structural coverage:** every structural family appears early, and every science appears at least once across the full 40.  
- **Difficulty calibration:** Tier 1 avoids “max difficulty” while still including at least one boundary-challenging genre; Tier 2 introduces hadith collections + entry-based dictionaries; Tier 3 concentrates multi-layer hawāshī and ʿilal/rijāl edge cases.  
- **Immediate scholarly value:** Tier 1 is weighted toward **Hanbalī fiqh**, **hadith sciences**, and **Arabic grammar**, consistent with the owner’s study priorities.

A crucial operational note: page limits (50–5000) should be enforced using your existing sweep metadata (`content_units` proxy), not human guessing. The repo already contains selection tooling patterns that rely on `content_units` and `multi_layer_units` in the corpus sweep JSONL. fileciteturn11file0L1-L1

### Tier one

| Book (Arabic; transliteration) | Author | Science | Family | Layer | Why included | Difficulty (1–5) | Validated? |
|---|---|---|---|---|---|---:|---|
| entity["book","تيسير الكريم الرحمن في تفسير كلام المنان","al-sa'di tafsir"]; *Taysīr al-Karīm al-Raḥmān fī Tafsīr Kalām al-Mannān* | entity["people","عبد الرحمن بن ناصر السعدي","tafsir scholar 1889-1956"] | Tafsīr | NAR | Sharḥ | B (high utility tafsīr); A (baseline narrative commentary); anchor already used in KR hardening fileciteturn4file0L1-L1 | 2 | Yes |
| entity["book","شرح ابن عقيل على ألفية ابن مالك","arabic grammar commentary"]; *Sharḥ Ibn ʿAqīl ʿalā Alfiyyat Ibn Mālik* | entity["people","ابن عقيل","grammarian 1294-1367"] | Naḥw | RUL | Sharḥ | B (standard grammar sharḥ); A (validated RUL+Sharḥ anchor); high owner relevance fileciteturn4file0L1-L1 | 3 | Yes |
| entity["book","زاد المستقنع في اختصار المقنع","hanbali fiqh matn"]; *Zād al-Mustaqniʿ fī Ikhtiṣār al-Muqniʿ* | entity["people","موسى بن أحمد الحجاوي","hanbali jurist d. 1577"] | Fiqh | ARG | Matn | B (Hanbalī cornerstone); A (ARG+Matn unvalidated) | 2 | No |
| entity["book","الروض المربع شرح زاد المستقنع","hanbali fiqh commentary"]; *al-Rawḍ al-Murbiʿ Sharḥ Zād al-Mustaqniʿ* | entity["people","منصور بن يونس البهوتي","hanbali jurist d. 1641"] | Fiqh | ARG | Sharḥ | B (core Hanbalī sharḥ); A (stress ARG boundaries in applied fiqh) | 3 | No |
| entity["book","روضة الناظر وجنة المناظر","usul al-fiqh treatise"]; *Rawḍat al-Nāẓir wa-Junnat al-Manāẓir* | entity["people","ابن قدامة","hanbali scholar 1147-1223"] | Uṣūl al-Fiqh | ARG | Matn | B (canonical usul anchor, Hanbalī-leaning); A (ARG+Matn) | 3 | No |
| entity["book","شرح الورقات في أصول الفقه","al-mahalli commentary"]; *Sharḥ al-Waraqāt fī Uṣūl al-Fiqh* | entity["people","جلال الدين المحلي","egyptian scholar 1389-1460"] | Uṣūl al-Fiqh | ARG | Sharḥ | B (widely taught intro usul sharḥ; appears in KR manifests) fileciteturn12file0L1-L1 | 2 | No |
| entity["book","نزهة النظر شرح نخبة الفكر","hadith methodology commentary"]; *Nuzhat al-Naẓar Sharḥ Nukhbat al-Fikar* | entity["people","ابن حجر العسقلاني","hadith scholar 1372-1449"] | Muṣṭalaḥ al-Ḥadīth | ENT | Sharḥ | B (common intermediate mustalaḥ); C (hadith-technical terminology) citeturn6search4 | 3 | No |
| entity["book","رياض الصالحين","hadith collection nawawi"]; *Riyāḍ al-Ṣāliḥīn* | entity["people","النووي","shafi'i hadith scholar 1233-1277"] | Ḥadīth collections | ENT | Matn | B (immediate study utility); A (ENT structure without maximal isnād) | 2 | No |
| entity["book","قطر الندى وبل الصدى","ibn hisham grammar"]; *Qaṭr al-Nadā wa-Ball al-Ṣadā* | entity["people","ابن هشام الأنصاري","arabic grammarian 1309-1360"] | Naḥw | RUL | Matn | B (classic intermediate naḥw); A (RUL+Matn unvalidated) | 2 | No |
| entity["book","بلوغ المرام من أدلة الأحكام","hadith fiqh evidences"]; *Bulūgh al-Marām min Adillat al-Aḥkām* | (same as Ibn Ḥajar, above) | Ḥadīth collections | ENT | Matn | B (high utility for fiqh+hadith); C (evidence-structured hadith excerpts) | 3 | No |

### Tier two

| Book (Arabic; transliteration) | Author | Science | Family | Layer | Why included | Difficulty (1–5) | Validated? |
|---|---|---|---|---|---|---:|---|
| entity["book","تفسير القرآن العظيم","tafsir ibn kathir"]; *Tafsīr al-Qurʾān al-ʿAẓīm* | entity["people","ابن كثير","historian and exegete 1300-1373"] | Tafsīr | NAR | Sharḥ | B (canonical widely read tafsīr); C (narration density, isnād-like citations) | 4 | No |
| entity["book","الرحيق المختوم","seerah safiur rahman"]; *al-Raḥīq al-Makhtūm* | entity["people","صفي الرحمن المباركفوري","seerah scholar 1943-2006"] | Tārīkh/Sīrah | NAR | Matn | B (accessible sīrah, high student utility); A (narrative base case) fileciteturn12file0L1-L1 | 2 | No |
| entity["book","شرح العقيدة الطحاوية","ibn abi al-izz commentary"]; *Sharḥ al-ʿAqīdah al-Ṭaḥāwiyyah* | entity["people","ابن أبي العز الحنفي","hanafi scholar d. 1390"] | ʿAqīdah | ARG | Sharḥ | B (canonical aqidah sharḥ; present in KR manifests) fileciteturn12file0L1-L1 | 3 | No |
| entity["book","شرح العقائد النسفية","taftazani commentary"]; *Sharḥ al-ʿAqāʾid al-Nasafiyyah* | entity["people","التفتازاني","scholar 1322-1390"] | ʿIlm al-Kalām | ARG | Sharḥ | B (explicitly listed in madrasa curricula); C (scholastic terminology) citeturn15search0 | 4 | No |
| entity["book","تهذيب المنطق والكلام","taftazani logic"]; *Tahdhīb al-Manṭiq wa-l-Kalām* | (same as al-Taftāzānī, above) | Manṭiq | ARG | Matn | B (curricular logic anchor); C (high abstraction + dense argument) citeturn15search0 | 4 | No |
| entity["book","السراجية في الفرائض","inheritance primer"]; *al-Sirājiyyah fī ʿIlm al-Farāʾiḍ* | entity["people","سراج الدين السجاوندي","jurist d. 1291"] | ʿIlm al-Farāʾiḍ | ARG | Matn | B (classic farāʾiḍ anchor); C (calculation/table-like structures) | 4 | No |
| entity["book","مقدمة ابن الصلاح في علوم الحديث","hadith methodology classic"]; *Muqaddimat Ibn al-Ṣalāḥ fī ʿUlūm al-Ḥadīth* | entity["people","ابن الصلاح","hadith scholar 1181-1245"] | Muṣṭalaḥ al-Ḥadīth | ENT | Matn | B (explicitly used in advanced hadith curricula) citeturn6search6 | 4 | No |
| entity["book","تقريب التهذيب","rijal dictionary ibn hajar"]; *Taqrīb al-Tahdhīb* | (same as Ibn Ḥajar, above) | Takhrīj/Rijāl | ENT | Entry-based | B (core rijāl reference); C (name disambiguation + entry segmentation) | 4 | No |
| entity["book","طبقات الحنابلة","biographical dictionary hanbali"]; *Ṭabaqāt al-Ḥanābilah* | entity["people","ابن أبي يعلى","hanbali judge d. 1133"] | Ṭabaqāt/Tarājim | ENT | Entry-based | B (high scholarly utility for Hanbalī study); C (entry boundaries) | 4 | No |
| entity["book","صحيح البخاري","hadith collection"]; *Ṣaḥīḥ al-Bukhārī* | entity["people","البخاري","hadith scholar 810-870"] | Ḥadīth collections | ENT | Entry-based | B (canonical “must-process” collection); C (max isnād complexity) citeturn3search2 | 5 | No |
| entity["book","شذا العرف في فن الصرف","morphology primer"]; *Shadhā al-ʿUrf fī Fann al-Ṣarf* | entity["people","أحمد الحملاوي","egyptian scholar d. 1932"] | Ṣarf | RUL | Matn | B (common sarf text); A (RUL+Matn coverage) | 2 | No |
| entity["book","مختصر المعاني","taftazani rhetoric"]; *Mukhtaṣar al-Maʿānī* | (same as al-Taftāzānī, above) | Lughah/Balāghah | RUL | Matn | B (curricular balāghah anchor); C (dense technical prose) citeturn15search0 | 4 | No |
| entity["book","فتح رب البرية شرح المقدمة الجزرية","tajwid commentary"]; *Fatḥ Rabb al-Barīyah Sharḥ al-Muqaddimah al-Jazarīyah* | entity["people","عبد الفتاح القاضي","quran recitation scholar 1907-1992"] | Qirāʾāt/Tajwīd | RUL | Sharḥ | B (tajwīd sharḥ); C (waqf/marker/symbol preservation) fileciteturn9file0L1-L1 | 3 | No |
| entity["book","مقامات الحريري","literary maqamat"]; *Maqāmāt al-Ḥarīrī* | entity["people","الحريري","arabic maqamat author 1054-1122"] | Adab/Shiʿr | ART | Matn | B (canonical adab genre); C (rhymed prose + segmentation) | 4 | No |
| entity["book","الرسالة القشيرية","sufi manual"]; *al-Risālah al-Qushayriyyah* | entity["people","القشيري","sufi scholar 986-1072"] | Taṣawwuf | SEQ | Matn | B (canonical tasawwuf manual); A (SEQ family baseline) | 3 | No |

### Tier three

| Book (Arabic; transliteration) | Author | Science | Family | Layer | Why included | Difficulty (1–5) | Validated? |
|---|---|---|---|---|---|---:|---|
| entity["book","التعليق على الرحيق المختوم","mubarakpuri seerah notes"]; *al-Taʿlīq ʿalā al-Raḥīq al-Makhtūm* | (varies by edition) | Tārīkh/Sīrah | NAR | Taʿlīqah | A (layer coverage: Taʿlīqah); C (editorial voice shifts) fileciteturn12file0L1-L1 | 3 | No |
| entity["book","أنوار التنزيل وأسرار التأويل","tafsir baydawi"]; *Anwār al-Tanzīl wa-Asrār al-Taʾwīl* | entity["people","البيضاوي","exegete d. 1286"] | Tafsīr | NAR | Sharḥ | B (madrasa-standard tafsīr); C (high density, terse style) citeturn15search0 | 5 | No |
| entity["book","منتهى الإرادات في جمع المقنع مع التنقيح وزيادات","hanbali fiqh manual"]; *Muntahā al-Irādāt…* | entity["people","منصور بن يونس البهوتي","hanbali jurist d. 1641"] | Fiqh | ARG | Matn | B (advanced Hanbalī anchor); C (scale + density) fileciteturn12file0L1-L1 | 4 | No |
| entity["book","حاشية الخلوتي على منتهى الإرادات","hanbali marginalia"]; *Ḥāshiyat al-Khalūṭī ʿalā Muntahā al-Irādāt* | entity["people","محمد بن أحمد الخلوتي","hanbali jurist d. 1701"] | Fiqh | ARG | Ḥāshiyah | A (multi-layer stress); C (max layer interleaving) fileciteturn12file0L1-L1 | 5 | No |
| entity["book","حاشية ابن قاسم على الروض المربع","hanbali marginalia"]; *Ḥāshiyat Ibn Qāsim ʿalā al-Rawḍ al-Murbiʿ* | entity["people","عبد الرحمن بن محمد بن قاسم","hanbali editor 1900-1972"] | Fiqh | ARG | Ḥāshiyah | A (hard multi-layer); B (Hanbalī study utility) | 5 | No |
| entity["book","الشرح الصوتي لزاد المستقنع","uthaymeen transcript"]; *al-Sharḥ al-Ṣawtī li Zād al-Mustaqniʿ* | entity["people","محمد بن صالح العثيمين","saudi scholar 1925-2001"] | Fiqh | ARG | Taʿlīqah | A (Taʿlīqah layer + spoken-style text); C (format drift vs authored prose) fileciteturn12file0L1-L1 | 4 | No |
| entity["book","تدريب الراوي في شرح تقريب النواوي","suyuti hadith terminology"]; *Tadrīb al-Rāwī fī Sharḥ Taqrīb al-Nawāwī* | entity["people","السيوطي","egyptian scholar 1445-1505"] | Muṣṭalaḥ al-Ḥadīth | ENT | Sharḥ | B (classical advanced mustalaḥ); C (dense taxonomy and examples) citeturn15search0 | 4 | No |
| entity["book","معجم المدلسين","narrator deception categories"]; *Muʿjam al-Mudallisīn* | (varies) | Takhrīj/Rijāl | ENT | Entry-based | C (name-pattern complexity, rijāl entries); A (ENT+Entry stress) fileciteturn9file0L1-L1 | 4 | No |
| entity["book","علل الدارقطني","hadith defects"]; *ʿIlal al-Dāraquṭnī* | entity["people","الدارقطني","hadith scholar 918-995"] | Takhrīj/Rijāl | ENT | Entry/discussion | C (max isnād-variant complexity); high bug-surfacing value fileciteturn12file0L1-L1 | 5 | No |
| entity["book","حاشية الصبان على شرح الأشموني لألفية ابن مالك","nahw supercommentary"]; *Ḥāshiyat al-Ṣabbān ʿalā Sharḥ al-Ashmūnī…* | entity["people","الصبان","egyptian scholar d. 1791"] | Naḥw | RUL | Ḥāshiyah | A/C (max multi-layer in grammar); specific layer-rebasing stress fileciteturn12file0L1-L1 | 5 | No |
| entity["book","التيسير في القراءات السبع","qiraat manual al-dani"]; *al-Taysīr fī al-Qirāʾāt al-Sabʿ* | entity["people","أبو عمرو الداني","qiraat scholar 981-1053"] | Qirāʾāt/Tajwīd | RUL | Matn | C (qirāʾāt-specific markers + segmentation); fills RUL+Matn niche for qirāʾāt | 4 | No |
| entity["book","الوقف والابتداء","quran pause rules"]; *al-Waqf wa-l-Ibtidāʾ* | (often attributed to al-Dānī in classical tradition) | Qirāʾāt/Tajwīd | RUL | Matn | C (waqf sign logic and markers; segmentation hazards) citeturn4search3 | 4 | No |
| entity["book","القاموس المحيط","arabic dictionary fayruzabadi"]; *al-Qāmūs al-Muḥīṭ* | entity["people","الفيروزآبادي","lexicographer 1329-1414"] | Lughah/Balāghah | RUL | Entry-based | A/C (dictionary entry segmentation, headword noise) | 4 | No |
| entity["book","ديوان المتنبي","arabic poetry diwan"]; *Dīwān al-Mutanabbī* | entity["people","المتنبي","arabic poet 915-965"] | Adab/Shiʿr | ART | Matn | C (poetry line boundaries, meter/rhyme constraints) citeturn3search3 | 5 | No |
| entity["book","شرح ديوان المتنبي للواحدي","poetry commentary"]; *Sharḥ Dīwān al-Mutanabbī (al-Wāḥidī)* | entity["people","الواحدي","exegete and philologist 1003-1075"] | Adab/Shiʿr | ART | Sharḥ | C (poetry + commentary boundary interleaving; hardest ART case) | 5 | No |

### Coverage matrix by tier

Key: the cell shows which tier first provides that **science × family × layer** coverage (1/2/3). Blank means “not covered in this 40-book batch.”

| Science (Family) | Matn | Sharḥ | Ḥāshiyah | Taʿlīqah |
|---|---:|---:|---:|---:|
| Fiqh (ARG) | 1 | 1 | 3 | 3 |
| Uṣūl al-Fiqh (ARG) | 1 | 1 |  |  |
| ʿAqīdah (ARG) |  | 2 |  |  |
| ʿIlm al-Kalām (ARG) | 2 | 2 |  |  |
| ʿIlm al-Farāʾiḍ (ARG) | 2 |  |  |  |
| Manṭiq (ARG) | 2 |  |  |  |
| Tārīkh/Sīrah (NAR) | 2 |  |  | 3 |
| Tafsīr (NAR) |  | 1 |  |  |
| Ṭabaqāt/Tarājim (ENT) |  |  |  |  |
| Muṣṭalaḥ al-Ḥadīth (ENT) | 2 | 1 |  |  |
| Takhrīj/Rijāl (ENT) |  |  |  |  |
| Ḥadīth collections (ENT) | 1 |  |  |  |
| Naḥw (RUL) | 1 | 1 | 3 |  |
| Ṣarf (RUL) | 2 |  |  |  |
| Lughah/Balāghah (RUL) | 2 |  | 3 |  |
| Qirāʾāt/Tajwīd (RUL) | 3 | 2 |  |  |
| Adab/Shiʿr (ART) | 2 | 3 |  |  |
| Taṣawwuf (SEQ) | 2 |  |  |  |

Interpretation: The batch is intentionally **front-loaded** with Hanbalī fiqh + hadith methodology + grammar, while still guaranteeing that by Tier 2 you have at least one exemplar for every family and most sciences, and by Tier 3 you hit the truly failure-prone layer phenomena (ḥawāshī and taʿlīqāt) and hardest hadith/poetry edge cases.

## Operational selection method inside KR

### A bottleneck-first, auditable selection workflow

1. **Start from the 40-title target list above** as a *semantic candidate set* (goal alignment + theory of risk).  
2. **Resolve to corpus-exact IDs/names** using your normalized inventory (the 7,475-book list). This step is critical because Shamela often contains multiple editions/prints, and your repo already shows edition-tagged variants in manifests. fileciteturn12file0L1-L1  
3. **Enforce page constraints deterministically** using normalization sweep metadata (recommended proxy: `content_units`), filtered to 50–5000. The repository already has scripts that load the sweep JSONL and use `content_units`, `diacritic_count`, and `multi_layer_units` as decision variables, so you are not designing this from scratch. fileciteturn11file0L1-L1  
4. **Dedupe by pedagogical redundancy**, not by title similarity. Example: if you keep both al-Rawḍ al-Murbiʿ and a different Zād sharḥ, justify it as layer/voice diversity; otherwise collapse to one.  
5. **Stage the run as smoke → expansion**, consistent with software QA: run Tier 1 first as your “document smoke suite,” require stable cost and no catastrophic structural failures, then proceed to Tier 2 and Tier 3. citeturn0search1

### Why this is the single best next move

A weak assumption to reject early is: “we can just pick 30–50 books randomly across sciences.” Random selection will undersample the highest-risk structural phenomena (multi-layer, long isnād density, entry dictionaries) because they are relatively rare in the corpus (e.g., multi-layer only ~5.4%). fileciteturn9file0L1-L1 The leverage move is to pick a batch that is *deliberately unrepresentative* in the direction of **failure modes**, while still being academically useful.

This synthesis delivers that: Tier 1 is immediately study-valuable and stabilizes core flows; Tier 2 closes the “science coverage” gap and introduces the major hard genres; Tier 3 contains the adversarial layer and structure edge cases most likely to surface failures before a full-scale run.