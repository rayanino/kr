# Protocol review: five structural gaps in the text extraction system

The protocol under review — governing how AI agents extract teaching units from classical Arabic scholarly texts — is architecturally sound but contains five gaps that will cause silent text corruption in specific, predictable scenarios. **Three of these gaps are critical**: the science list omits disciplines with genuinely distinct excerpting constraints, the indivisible-unit inventory misses at least five units whose splitting corrupts meaning, and the commentary family [COM] is misclassified as a peer category when it is an orthogonal structural layer. The remaining two gaps — arbitration of inter-madhhab structural disagreements and owner briefing design — are high-severity risks that compound over time. Each finding below is grounded in a governing principle from the Islamic scholarly tradition, evaluated against the protocol's current implementation, and accompanied by a concrete test case from a named text.

---

## QUESTION 1: Four sciences must be added to the sixteen

**GOVERNING PRINCIPLE:** The Islamic scholarly tradition classifies knowledge by its *mawḍūʿ* (subject matter), *masāʾil* (constitutive questions), and *manhaj* (methodology). When two disciplines share subject matter but diverge in methodology or structural architecture, they produce texts with different *anmāṭ taʾlīfiyyah* (compositional patterns). A text extraction system must respect these patterns or risk splitting what should be joined and joining what should be split.

**CURRENT STATE:** §4.3 lists 16 sciences in 6 structural families. ʿAqīdah is listed but kalām is not. Fiqh is listed but farāʾiḍ, taṣawwuf, and maqāṣid are not. Siyāsah sharʿiyyah and Islamic finance are not listed.

**ASSESSMENT:** INCOMPLETE

### ʿIlm al-kalām is distinct from ʿaqīdah and requires separate treatment

ʿAqīdah texts like *al-ʿAqīdah al-Ṭaḥāwiyyah* use a **linear, declarative architecture**: creedal statement → dalīl cascade. Each article is relatively self-contained — a belief proposition supported by Quranic verses, ḥadīth, and ijmāʿ. Kalām texts like al-Juwaynī's *al-Irshād ilā Qawāṭiʿ al-Adillah* and al-Bāqillānī's *al-Tamhīd* use a **dialectical architecture**: thesis → opponent's objection (شُبْهَة, shubhah) → refutation (رَدّ, radd), often in multi-step chains where each refutation generates a counter-objection. A University of Sydney doctoral study confirms this structural distinction: "While ʿaqāʾid lays out beliefs in creedal codes, kalām gives textual and reasoned arguments justifying those creeds... kalām refutes objections and doubts." The shubhah-radd pair is the atomic unit of kalām, and excerpting a shubhah without its radd — or a radd without its shubhah — leaves either an unanswered attack on orthodox doctrine or an ungrounded defense. The protocol's existing Radd/Iʿtirāḍ-Jawāb indivisible unit partially addresses this, but kalām's multi-level nesting (a radd that generates a new shubhah that requires a further radd) creates boundary-detection requirements absent from ʿaqīdah texts.

**Addition:** Add **ʿIlm al-Kalām** (عِلْم الكَلَام) to [ARG] family. Classification: [ARG] Argument-based, with a sub-type flag for dialectical-jadal structure requiring shubhah-radd pair preservation and nested-refutation tracking.

**Test case:** Al-Juwaynī's *al-Irshād*, chapter on the createdness of the world — a four-level nested refutation of Aristotelian eternalism where each radd generates a new philosophical counter-objection. Splitting at any interior level misrepresents both the opponent's position and al-Juwaynī's response.

### ʿIlm al-farāʾiḍ requires separate treatment from fiqh

Farāʾiḍ texts are **computationally structured** in ways that no other fiqh sub-discipline replicates. The core operations — fractional share tables (جَدَاوِل, jadāwil), proportional reduction (عَوْل, ʿawl), surplus redistribution (رَدّ, radd), and problem rectification (تَصْحِيح المَسَائِل, taṣḥīḥ al-masāʾil) using least common multiples — are mathematical procedures, not prose arguments. A worked inheritance problem (masʾalah) consists of: heir list → share assignment → conflict detection → arithmetic resolution → final distribution table. **Splitting a worked problem at any point between heir identification and final distribution produces a mathematically incomplete — and therefore legally useless — fragment.** Additionally, the *al-Raḥabiyyah* (176 verses by al-Raḥbī al-Shāfiʿī) adds the structural constraint of versified poetry (naẓm), where concepts compressed into rhyming couplets cannot be split mid-couplet without destroying both metre and meaning. The special named cases (المَسَائِل الشَّاذَّة) — al-gharrāwayn, al-akdariyyah, al-mushārakah — are complete units whose names are meaningless without their full worked solutions.

**Addition:** Add **ʿIlm al-Farāʾiḍ** (عِلْم الفَرَائِض) to a new sub-type within [ARG] or as a hybrid [ARG+RUL], with mandatory indivisibility flags for worked problems, share tables, and ʿawl/radd calculation sequences.

**Test case:** *Sharḥ al-Sirājiyyah* (Ḥanafī inheritance), the al-akdariyyah problem — a six-step calculation involving ʿawl from 6 to 9, then adjustment for the grandfather's share. Splitting after step 3 produces a legally and mathematically wrong distribution.

### Taṣawwuf has a unique sequential-dependency structure

Taṣawwuf texts like al-Qushayrī's *al-Risālah al-Qushayriyyah* organize spiritual development as a **progression through stations** (مَقَامَات, maqāmāt), where each station has explicit prerequisites in the preceding station. Repentance (tawbah) must precede turning toward God (inābah); patience (ṣabr) must precede trust (tawakkul). Al-Ghazālī's *Iḥyāʾ ʿUlūm al-Dīn* structures its 40 books across four quarters representing a staged spiritual journey: external worship → ethical conduct → purging vices (muhlikāt) → cultivating saving virtues (munjiyyāt). **Excerpting a later station without its prerequisite, or a saving virtue without prior purging of its corresponding vice, corrupts the spiritual pedagogy** — it presents the destination without the path, which the tradition considers not merely incomplete but potentially harmful (a student attempting advanced spiritual practices without foundational purification). No existing science in the protocol captures this sequential-dependency constraint. Fiqh chapters are largely independent of each other; ʿaqīdah articles are self-contained; ḥadīth collections are entry-based. The maqāmāt structure is genuinely novel.

**Addition:** Add **Taṣawwuf / ʿIlm al-Sulūk** (تَصَوُّف / عِلْم السُّلُوك) as a new structural family type: **[SEQ] Sequential-progressive**, or as a member of a new sub-family within [ARG] with a mandatory sequential-dependency flag requiring prerequisite-chain tracking.

**Test case:** Al-Qushayrī's *al-Risālah*, the chapter on tawakkul (trust in God) — which explicitly references and builds upon the prior chapters on ṣabr (patience) and riḍā (contentment). Excerpting tawakkul alone presents a spiritual virtue stripped of its foundational conditions.

### Maqāṣid is a borderline case, best handled as a sub-type of uṣūl al-fiqh

Al-Shāṭibī's *al-Muwāfaqāt* does have a distinctive hierarchical structure (ḍarūriyyāt → ḥājiyyāt → taḥsīniyyāt) and a unique inductive methodology (istiqrāʾ). However, its subject matter, methodology, and readership overlap heavily with uṣūl al-fiqh. The hierarchical maqāṣid framework can be handled by the existing Taqsīm indivisible unit (USUALLY INDIVISIBLE tier) combined with an additional cross-reference preservation rule for inductive argument chains. **Recommendation:** Do not add maqāṣid as a separate science, but add a processing note to the [ARG] family that inductive-cumulative arguments (istiqrāʾ maʿnawī) require preservation of the full evidence base — the existing Qāʿidah/Farʿ unit should be extended to cover principle-hierarchy structures.

### Siyāsah sharʿiyyah and classical Islamic finance are subsets of fiqh

Ibn Taymiyyah's *al-Siyāsah al-Sharʿiyyah* uses standard dalīl-based legal reasoning applied to governance topics — the same prose-argument architecture as any fiqh text. Classical Islamic finance (fiqh al-muʿāmalāt) similarly follows standard fiqh patterns: definition → arkān → shurūṭ → prohibited elements → examples. Modern Islamic finance texts with process-flow diagrams and accounting treatments are a different matter, but these are not classical scholarly texts. **Coverage is complete under the existing fiqh entry.**

**SPECIFIC ADDITIONS:**
1. Add ʿIlm al-Kalām (عِلْم الكَلَام) → [ARG], with shubhah-radd pair tracking
2. Add ʿIlm al-Farāʾiḍ (عِلْم الفَرَائِض) → [ARG+RUL] hybrid, with mathematical-sequence indivisibility
3. Add Taṣawwuf / ʿIlm al-Sulūk (تَصَوُّف / عِلْم السُّلُوك) → new [SEQ] or [ARG] sub-type with sequential-dependency tracking
4. Add processing note for maqāṣid-style inductive arguments under existing uṣūl al-fiqh entry

**SEVERITY:** CRITICAL — kalām and farāʾiḍ texts will be silently corrupted without these additions. Taṣawwuf is HIGH.

---

## QUESTION 2: Five indivisible units must be added, one reclassified

**GOVERNING PRINCIPLE:** The principle of *ḥifẓ al-maʿnā* (preservation of meaning) in the manuscript tradition (taḥqīq) holds that any textual unit whose components are semantically co-dependent — where removing one component renders the remainder either meaningless, misleading, or doctrinally dangerous — must be treated as indivisible. The strength of indivisibility correlates with the degree of semantic dependency: complete dependency (the component *cannot be understood* alone) warrants ALWAYS INDIVISIBLE; contextual dependency (the component *can be understood* but may mislead) warrants USUALLY or CONDITIONALLY.

**CURRENT STATE:** §4.3 lists 23 indivisible units across 3 tiers (15 ALWAYS, 4 USUALLY, 4 CONDITIONALLY).

**ASSESSMENT:** INCOMPLETE

### Mujmal/Mubayyan (المُجْمَل والمُبَيَّن) — ALWAYS INDIVISIBLE

This unit is **structurally stronger** than the already-listed Muṭlaq/Muqayyad. In the muṭlaq/muqayyad pair, both texts have independently comprehensible meanings — the question is about scope qualification. In the mujmal/mubayyan pair, the mujmal text is in a state of *tawaqquf* (تَوَقُّف) — suspension of action — and **literally cannot be understood or acted upon** without its bayān. The word "ṣalāh" in the Quran is mujmal; without the Prophet's bayān showing the prayer's form, timing, and conditions, the command is semantically incomplete. Al-Jaṣṣāṣ, al-Bāqillānī, and al-Qāḍī ʿAbd al-Jabbār all treat the mujmal-mubayyan relationship as one of semantic dependency. Separating the mujmal from its clarification produces an excerpt that the entire uṣūl tradition unanimously holds to be inactionable.

**Tier:** ALWAYS INDIVISIBLE. **Section:** Add to §4.3 Atomic Integrity Risk.

**Test case:** Al-Ghazālī's *al-Mustaṣfā*, discussion of the Quranic command "وَآتُوا الزَّكَاةَ" (pay zakāh) — mujmal until the Sunnah specifies amounts, niṣāb thresholds, and eligible recipients. Excerpting the command without the bayān presents an unactionable legal obligation.

### Dalīl and its Wajh al-Dalālah (الدَّلِيل وَوَجْه الدَّلَالَة) — ALWAYS INDIVISIBLE

In uṣūl al-fiqh texts, a dalīl (evidence) is never cited in isolation — it is always accompanied by its wajh al-dalālah (وَجْه الدَّلَالَة): the specific angle through which the evidence yields its legal conclusion. The same Quranic verse may serve as dalīl for entirely different rulings depending on the wajh. This is distinct from Qāʿidah/Farʿ, which connects a general principle to its specific application; here, the dalīl itself is a raw text (a verse, ḥadīth, or ijmāʿ report) and the wajh is the hermeneutic key that extracts a specific legal meaning from it. **Presenting a dalīl without its wajh strips the evidence of its argumentative force; presenting a wajh without its dalīl leaves a legal interpretation floating without textual grounding.**

**Tier:** ALWAYS INDIVISIBLE. **Section:** Add to §4.3 Atomic Integrity Risk.

**Test case:** Al-Rāzī's *al-Maḥṣūl*, discussion of the ḥadīth "لَا ضَرَرَ وَلَا ضِرَارَ" (no harm and no reciprocal harm) — used as dalīl for at least four different rulings depending on whether the wajh al-dalālah is ʿumūm al-nafy, or nafy al-ḍarar al-fāḥish, or the principle of lā ḍarar applied to contractual relations. Excerpting the ḥadīth without specifying which wajh is operative makes the excerpt useless for understanding the author's argument.

### Tarjīḥ block (التَّرْجِيح) — ALWAYS INDIVISIBLE

A tarjīḥ block in comparative fiqh follows a rigid five-part structure: (1) statement of the masʾalah, (2) presentation of competing views with madhhab attribution, (3) evidence for each view, (4) systematic weighing, (5) verdict. Ibn Qudāmah's *al-Mughnī* is built entirely on this architecture. **The verdict derives its scholarly authority exclusively from the displayed reasoning** — a verdict without its evidence chain is a bare assertion with no legal weight, while evidence without a verdict is an incomplete argument. The protocol's existing Khilāf register (USUALLY INDIVISIBLE) partially overlaps, but the tarjīḥ block is specifically the *resolution* of khilāf, not just its presentation. Khilāf can exist without tarjīḥ (when the author presents views without choosing); tarjīḥ always includes khilāf but adds the weighing and verdict. They are related but structurally distinct.

**Tier:** ALWAYS INDIVISIBLE. **Section:** Add to §4.3 Atomic Integrity Risk.

**Test case:** *al-Mughnī* by Ibn Qudāmah, the masʾalah of whether the basmala is a verse of al-Fātiḥah — presents four madhhab positions, seven ḥadīth evidences, three rational arguments, and concludes with tarjīḥ for the Ḥanbalī position. Excerpting only the verdict ("it is not a verse of al-Fātiḥah") without the weighing misrepresents Ibn Qudāmah as issuing an unsupported assertion.

### Istidrāk/Tanbīh (الاسْتِدْرَاك / التَّنْبِيه) — ALWAYS INDIVISIBLE with its referent

Istidrāk creates a **backward-pointing dependency**: it modifies, corrects, or supplements a preceding statement. The istidrāk without its referent passage is meaningless; the referent passage without its istidrāk propagates the very error the author intended to correct. In taḥqīq practice, editors like ʿAbd al-Fattāḥ Abū Ghuddah place istidrāk sections at the end of volumes linked to the main text via symbol markers — the link is part of the text's integrity. Tanbīh functions similarly as an inline qualifier: "tanbīh: this ruling applies only when..." — excerpting the ruling without its tanbīh produces an overly broad or inaccurate statement of the law.

**Tier:** ALWAYS INDIVISIBLE (istidrāk + its referent passage as a unit). **Section:** Add to §4.3 Atomic Integrity Risk.

**Test case:** Al-Nawawī's *al-Majmūʿ*, where tanbīh notes frequently restrict a general fiqh ruling to specific conditions — e.g., a ruling on the permissibility of combining prayers, followed by "tanbīh: this applies only in travel, not residence." Excerpting the ruling without the tanbīh produces a false generalization.

### Waqf markers in Quranic/Tajwīd texts (عَلَامَات الوَقْف) — ALWAYS INDIVISIBLE with their textual context

Waqf markers are **the Quranic tradition's own indivisibility annotations**. The marker وقف لازم (م) — mandatory stop — marks points where continuing recitation past that point would **corrupt theological meaning**. The marker لا (lā) — stopping forbidden — marks points where pausing would create doctrinal error (e.g., stopping after "لا إله" before "إلا الله"). The marker muʿānaqah (∴) marks paired alternatives where stopping at one of two points is required but not both. **For Qirāʾāt/Tajwīd texts specifically, waqf markers encode the minimum semantic unit boundaries determined by centuries of scholarly analysis.** Any text extraction from these works that splits at a لا (no-stop) marker, or separates a muʿānaqah pair, produces doctrinally dangerous fragments.

**Tier:** ALWAYS INDIVISIBLE (for Qirāʾāt/Tajwīd texts). **Section:** Add to §4.3 Atomic Integrity Risk, with a note that these apply specifically within the [RUL] family for Qirāʾāt/Tajwīd.

**Test case:** Quran 6:36 — "إِنَّمَا يَسْتَجِيبُ الَّذِينَ يَسْمَعُونَ ۘ وَالْمَوْتَىٰ يَبْعَثُهُمُ اللَّهُ" — there is a mandatory waqf (م) after "yasmaʿūn" because continuing without pause would incorrectly include "the dead" among those who respond. A tajwīd text discussing this marker must preserve both the marker and its surrounding text as a unit.

### Taḥqīq apparatus (الجِهَاز التَّحْقِيقِي) — CONDITIONALLY INDIVISIBLE

The critical apparatus in scholarly editions (Muʾassasat al-Risālah, Dār al-Minhāj) contains three types of material with different dependency strengths: (a) **variant readings** (فَوَارِق النُّسَخ) that may fundamentally alter meaning — strongly dependent; (b) **ḥadīth takhrīj notes** identifying sources — supplementary; (c) **editorial corrections/istidrāk** — dependent (falls under the istidrāk rule above). The main text retains its original meaning without the apparatus, but for scholarly use, separating variant readings from the established text undermines the critical edition's entire purpose. The condition: when the variant reading alters legal or doctrinal meaning, the apparatus note is indivisible from its passage; when it records orthographic variants with no semantic impact, it is separable.

**Tier:** CONDITIONALLY INDIVISIBLE. **Condition:** indivisible when variant readings alter legal, doctrinal, or interpretive meaning. **Section:** Add to §4.3 Atomic Integrity Risk.

**Test case:** The Shuʿayb al-Arnaʾūṭ edition of *Musnad Aḥmad* — where a footnote records that manuscript B reads "لا يجوز" (impermissible) where manuscript A reads "يجوز" (permissible). Separating this variant note from the main text passage conceals a legal ruling reversal.

### Reclassification: Taʿlīl is already partially covered by Qiyās but needs explicit treatment

The existing Qiyās (4 arkān) indivisible unit implicitly covers the ʿillah-ḥukm pair, since ʿillah is one of the four arkān. However, **taʿlīl reasoning** (التَّعْلِيل) as a standalone discursive unit — where a scholar identifies, tests, and validates a legal cause through the three-stage process of takhrīj al-manāṭ → tanqīḥ al-manāṭ → taḥqīq al-manāṭ — extends beyond the four-pillar qiyās structure. **Recommendation:** Expand the existing Qiyās entry to explicitly include the full taʿlīl reasoning chain (the three manāṭ stages) as part of its indivisibility scope, rather than adding a separate entry.

### Ijāzah chain (سِلْسِلَة الإِجَازَة) — USUALLY INDIVISIBLE

Ijāzah chains are structurally distinct from isnād: isnād authenticates specific content (a ḥadīth), while ijāzah authorizes transmission rights for entire texts. In ṭabaqāt works, ijāzah information is biographical metadata — it belongs to the scholar's entry. However, the chain itself must not be split internally. It is "usually" rather than "always" indivisible because an ijāzah that appears as a prefatory wrapper around a text can sometimes be treated as separable metadata, whereas an ijāzah embedded in a biographical entry in a ṭabaqāt work is integral to that entry.

**Tier:** USUALLY INDIVISIBLE. **Section:** Add to §4.3 Atomic Integrity Risk.

**Test case:** Al-Dhahabī's *Siyar Aʿlām al-Nubalāʾ*, biographical entry for a scholar whose authority rests on a specific ijāzah chain from al-Bukhārī → intermediate transmitters → the scholar in question. Splitting the chain mid-way destroys the scholarly authority record.

**SPECIFIC ADDITIONS to §4.3:**
- ALWAYS INDIVISIBLE (add 5): Mujmal/Mubayyan, Dalīl + Wajh al-Dalālah, Tarjīḥ block, Istidrāk/Tanbīh + referent, Waqf markers + context
- USUALLY INDIVISIBLE (add 1): Ijāzah chain
- CONDITIONALLY INDIVISIBLE (add 1): Taḥqīq apparatus (when variant alters meaning)
- Expand existing Qiyās entry to include full taʿlīl (3-stage manāṭ) reasoning chain

**New totals:** 20 ALWAYS, 5 USUALLY, 5 CONDITIONALLY = **30 indivisible units in 3 tiers**

**SEVERITY:** CRITICAL — Mujmal/Mubayyan splitting produces inactionable legal texts; Tarjīḥ splitting misattributes scholarly positions; Istidrāk separation propagates the exact errors authors intended to correct.

---

## QUESTION 3: Arbitration needs a madhhab-awareness layer and three additional coverage domains

**GOVERNING PRINCIPLE:** The principle of *iḥtirām al-ikhtilāf al-muʿtabar* (respecting legitimate scholarly disagreement) is foundational to Islamic jurisprudence. The four Sunni schools represent equally valid methodological approaches, and a text from one school must be processed according to that school's own structural norms. Al-Āmidī (Shāfiʿī) excluded ḥukm al-farʿ from qiyās's arkān; al-Isnawī (also Shāfiʿī) included it as a fifth. The Ḥanafī tradition counts four arkān. **There is no single "scholarly correctness" for structural boundaries — the correct structure depends on the madhhab and sometimes the individual author.**

**CURRENT STATE:** §4.13 states "Scholarly Integrity > Owner Intent when the implementation would corrupt text structure." It assumes a single definition of structural correctness. Coverage: isnād chains, attribution integrity, indivisible textual units, Quranic citation boundaries.

**ASSESSMENT:** STRUCTURALLY FLAWED

### The protocol needs a madhhab-context parameter

The current rule assumes that "text structure" is an objective, universal property. It is not. The qiyās example demonstrates this concretely: if the system processes al-Āmidī's *al-Iḥkām* (which treats qiyās as having four effective components, excluding ḥukm al-farʿ as merely a result) using a Ḥanafī four-arkān template, the output may appear correct but will have silently imposed an alien structural framework. Conversely, if it processes al-Isnawī's five-component analysis using the four-arkān template, it will truncate a component the author considered essential.

**Addition:** §4.13 must include a **madhhab-context rule**: "When the protocol's structural templates admit variant definitions across legitimate schools (madhāhib), the system MUST identify the madhhab context of the source text and apply that school's structural norms. When the madhhab cannot be determined, the system MUST flag the ambiguity rather than defaulting to any single school's framework." This can be detected via the school attribution signals already catalogued in arabic-scholarly-conventions.md (وَعِنْدَنَا, وَالمَذْهَب, وَالرَّاجِح).

**Test case:** Processing a passage from al-Sarakhsī's *Uṣūl* (Ḥanafī) and al-Āmidī's *al-Iḥkām* (Shāfiʿī) about qiyās structure — the system must not normalize both to the same template.

### Three additional coverage domains are needed

**(a) Variant readings between printed editions:** The Arabic publishing landscape has a well-documented quality hierarchy. Dār al-Kutub al-ʿIlmiyyah editions are widely regarded as unreliable — the Sunnah Project was created specifically because modern editions "contained errors or were missing aḥādīth found in the original handwritten manuscripts, in some cases this ran into the hundreds." **§4.13 must require edition metadata tracking** (publisher, editor, edition year) and should flag known-problematic publishers. When two editions of the same text disagree on content (e.g., "يجوز" vs. "لا يجوز"), the system must preserve the variant as a Class B provenance note per FP-5, not silently choose one reading.

**(b) Disputed authorship:** Texts attributed to major scholars frequently have contested provenance. Al-Ghazālī has "several hundred attributed works, many of them duplicates because of varying titles, that are doubtful or spurious." Ibn Taymiyyah's *Majmūʿ al-Fatāwā* was compiled posthumously by ʿAbd al-Raḥmān ibn Qāsim — questions of arrangement and completeness are inherent. Ibn ʿArabī's corpus includes only ~400 extant works of ~700 authenticated from ~850 attributed. **§4.13 must require authorship-confidence metadata**: verified, attributed-with-scholarly-consensus, attributed-with-dispute, or compilation (posthumous). This prevents the system from presenting contested attributions as settled facts.

**(c) Genre-boundary disputes:** Many texts resist neat genre classification. *Al-Mughnī* by Ibn Qudāmah is technically a sharḥ on *Mukhtaṣar al-Khiraqī* but functions as an independent encyclopedia of comparative fiqh. *Al-Sharḥ al-Kabīr* by Shams al-Dīn Ibn Qudāmah is simultaneously a sharḥ and a mukhtaṣar of *al-Mughnī*. **§4.13 should add a genre-flexibility rule**: "When a text's genre classification is ambiguous or multi-layered, the system MUST apply the structural rules of the *most restrictive* applicable genre to prevent under-protection of indivisible units."

**SPECIFIC ADDITIONS to §4.13:**
1. Madhhab-context parameter with school-detection via attribution signals
2. Edition metadata tracking with publisher-reliability flagging
3. Authorship-confidence metadata (verified / attributed / disputed / compiled)
4. Genre-flexibility rule defaulting to most restrictive classification

**SEVERITY:** HIGH — the madhhab-context gap will produce systematic structural misrepresentation across any multi-school corpus; the edition and authorship gaps create silent Class B provenance corruption per FP-5.

---

## QUESTION 4: [COM] is a layer type, not a structural family — the taxonomy needs revision

**GOVERNING PRINCIPLE:** The Islamic commentary tradition (شَرْح / حَاشِيَة / تَعْلِيقَة) operates through a universal architecture of **layered parasitic texts**: the sharḥ references the matn; the ḥāshiyah references the sharḥ; the taʿlīqah annotates any layer. This architecture is **discipline-invariant**. The same matn → sharḥ → ḥāshiyah → taʿlīqah layering, the same three interleaving types (qāla/aqūlu full embedding; qawluhu-marked partial embedding; sequential mīm/shīn alternation), and the same visual conventions (red ink for matn, overlining, marginal placement) appear identically across fiqh, ḥadīth, naḥw, ʿaqīdah, falsafah, and tafsīr. Robert Wisnovsky's research documents **~450 first-order commentaries, ~300 second-order, and ~150 third-order commentaries** in philosophy alone — all using the same structural patterns as ḥadīth sharḥ or fiqh sharḥ.

**CURRENT STATE:** [COM] Commentary-structured is listed as a peer of [ARG], [NAR], [ENT], [RUL], and [ART], containing only "Ḥadīth collections + sharḥ."

**ASSESSMENT:** STRUCTURALLY FLAWED

### The evidence for reclassification is overwhelming

The protocol's current structure implies that commentary is a property of ḥadīth texts. In reality, the Islamic scholarly tradition produced commentary chains in every discipline:

- **Fiqh:** Matn Abī Shujāʿ → Fatḥ al-Qarīb (sharḥ) → Ḥāshiyat al-Bājūrī
- **Naḥw:** Alfiyyat Ibn Mālik → Sharḥ Ibn ʿAqīl → multiple ḥawāshī
- **ʿAqīdah:** al-ʿAqīdah al-Ṭaḥāwiyyah → Sharḥ Ibn Abī al-ʿIzz; al-Nasafiyyah → al-Taftāzānī's sharḥ → **54+ ḥawāshī** documented by Wisnovsky
- **Ḥadīth:** Ṣaḥīḥ al-Bukhārī → Fatḥ al-Bārī (over 70 commentaries total on the Ṣaḥīḥ)
- **Falsafah:** al-Ishārāt → al-Rāzī's sharḥ → al-Ṭūsī's Ḥall → further layers

The interleaving patterns are consistent across all these. The choice of Type 1 vs. Type 2 vs. Type 3 depends on the commentator's approach, not on the discipline. **Commentary is an orthogonal dimension — a layer type that can combine with any structural family.**

### Proposed revised taxonomy

**Remove [COM] as a peer family.** Instead, create a two-dimensional classification:

**Dimension 1 — Structural family** (determines content-level organization):
- [ARG] Argument-based: Fiqh, Uṣūl al-fiqh, ʿAqīdah, Manṭiq, **ʿIlm al-Kalām, ʿIlm al-Farāʾiḍ**
- [NAR] Narrative-based: Tārīkh/Sīrah, Tafsīr, Fatāwā/Nawāzil
- [ENT] Entry-based: Ṭabaqāt/Tarājim, Muṣṭalaḥ al-ḥadīth, Takhrīj/Rijāl, **Ḥadīth collections**
- [RUL] Rule-based: Naḥw, Ṣarf, Lughah/Balāghah, Qirāʾāt/Tajwīd
- [ART] Artistic/literary: Adab/Shiʿr
- **[SEQ] Sequential-progressive: Taṣawwuf / ʿIlm al-Sulūk** (new)

**Dimension 2 — Text layer** (determines structural relationship to other texts):
- **[M] Matn** (base text — no commentary relationship)
- **[S] Sharḥ** (first-order commentary — requires matn-tracking)
- **[H] Ḥāshiyah** (second-order commentary — requires sharḥ-tracking and matn-tracking)
- **[T] Taʿlīqah/Taqrīr** (annotation/lecture notes — requires referent-tracking)

**Interleaving type** (determines extraction strategy):
- Type 1: qāla/aqūlu full embedding — matn embedded in sharḥ; extract via discourse markers
- Type 2: qawluhu-marked partial embedding — matn separately presented; extract by position
- Type 3: Sequential mīm/shīn alternation — extract by marker symbols

Every text gets classified on both dimensions: *Fatḥ al-Bārī* = [ENT]+[S], Type 2. *Ḥāshiyat al-Bājūrī* on Sharḥ Ibn Qāsim on Matn Abī Shujāʿ = [ARG]+[H], Type 3. Ṣaḥīḥ al-Bukhārī (standalone) = [ENT]+[M].

**This two-dimensional system eliminates the current anomaly** where [COM] awkwardly holds only ḥadīth sharḥ while fiqh sharḥ is implicitly under [ARG] and naḥw sharḥ is implicitly under [RUL]. It also provides the extraction system with actionable structural information: knowing the interleaving type tells the system exactly how to separate matn from sharḥ content.

**SEVERITY:** CRITICAL — the current [COM] classification causes the system to apply commentary-aware processing only to ḥadīth sharḥ texts while silently processing fiqh, naḥw, and ʿaqīdah sharḥ texts without commentary-layer awareness, corrupting the matn-sharḥ boundary in those disciplines.

---

## QUESTION 5: Batched owner briefing contradicts the tradition's core verification principles

**GOVERNING PRINCIPLE:** The Islamic text transmission tradition established a clear hierarchy where **per-unit, specialist-led verification** is the gold standard. The ʿarḍ (عَرْض) method — where the student reads the text back to the teacher who corrects errors — verified texts at the **word level**; Quranic transmission verified at the phoneme level. The scholarly tradition ranked methods by verification granularity: ʿarḍ + samāʿ (combined) > samāʿ (hearing) > ʿarḍ (reading back) > ijāzah (authorization) > munāwalah (handing over) > wijādah (finding). **Each decrease in granularity corresponds to decreased confidence in textual integrity.** As Yaḥyā ibn Abī Kathīr memorably stated: "He who writes and does not collate (يُقَابِل) is like one who uses the toilet and does not clean himself afterwards."

**CURRENT STATE:** §4.15 allows batched owner delivery after 50 atoms — the owner sees a 5-atom summary, though per-atom ledger artifacts are maintained.

**ASSESSMENT:** STRUCTURALLY FLAWED for the specific owner profile described

### (a) Cross-science batching creates unresolvable cognitive overload for a non-specialist

A 5-atom batch that mixes, say, an isnād boundary question (ḥadīth science), a farāʾiḍ table integrity question (inheritance mathematics), and a taṣawwuf maqāmāt sequencing question (spiritual pedagogy) requires **three completely separate domains of expertise** to evaluate. The traditional madrasa system taught these as separate subjects under separate teachers. Audition certificates (samāʿāt) from 550–750 AH show that **95% of documented reading sessions were devoted to a single discipline**. There is no precedent in the tradition for multi-discipline review sessions, because the tradition understood that meaningful verification requires domain competence. **A non-specialist owner cannot meaningfully evaluate a cross-science batch.** The owner described in the protocol — "a Muslim student with minimum Islamic knowledge" — operating at the wijādah level (finding texts without specialist authorization) is, by the tradition's own classification, at the **lowest confidence tier**.

### (b) Disengagement becomes self-reinforcing — the tradition predicts this

The principle of *tadarruj* (تَدَرُّج) — gradual progression — exists precisely because the tradition recognized that overwhelming a learner causes withdrawal. Al-Ghazālī emphasized adapting instruction to the student's capacity. When the owner is presented with batches they cannot meaningfully evaluate, the predicted outcome is exactly the cycle described: fewer objections → less scrutiny → more errors pass → owner loses confidence in their ability to contribute → rubber-stamping. This is not speculative — it is the direct consequence of violating tadarruj by presenting material above the evaluator's competence level. **The tradition calls this taklīf mā lā yuṭāq** (تَكْلِيف مَا لَا يُطَاق) — imposing what cannot be borne — and considers it both ineffective and unjust.

### (c) Traditional methodology suggests discipline-homogeneous batching with graduated complexity

The ʿarḍ + samāʿ model suggests three reforms:

**First**, batches must be **discipline-homogeneous** — never mix atoms from different sciences in a single batch. A 5-atom batch of fiqh questions is evaluable by someone with basic fiqh knowledge; a 5-atom batch mixing ḥadīth, naḥw, and taṣawwuf is evaluable by no one short of a polymath.

**Second**, the batch summary must be **graduated by complexity**: earlier batches should present simpler, more self-evident decisions (e.g., "Should this colophon be kept with its preceding text?" — an obvious yes) before progressing to subtler ones (e.g., "Does this tarjīḥ block's verdict belong with its evidence chain?" — requires understanding of comparative fiqh methodology). This follows the tadarruj principle.

**Third**, any atom involving a **Tier 1 indivisible unit** (ALWAYS INDIVISIBLE) should revert to Phase A per-atom briefing regardless of position in the sequence. The tradition's own approach — where ʿarḍ of the Quran required word-level verification from memory, while less critical texts allowed less granular checking — supports a **risk-tiered verification granularity** rather than a purely position-based (atoms 1–50 vs. 51+) batching threshold.

**SPECIFIC ADDITIONS to §4.15:**
1. **Discipline-homogeneous batching rule:** Atoms from different structural families [ARG], [NAR], [ENT], [RUL], [SEQ], [ART] must never appear in the same owner batch
2. **Graduated complexity ordering:** Within batches, present lower-risk decisions first, higher-risk decisions last
3. **Tier 1 reversion rule:** Any atom involving an ALWAYS INDIVISIBLE unit reverts to Phase A per-atom briefing regardless of sequence position
4. **Owner competence signal tracking:** If owner approval rate exceeds 95% across 3+ consecutive batches, flag for possible rubber-stamping and trigger a competence-check prompt

**SEVERITY:** HIGH — the current design creates conditions for systematic, silent owner disengagement that the per-atom ledger artifacts cannot compensate for, because the artifacts are only as valuable as the verification process that produces them. An unchecked ledger is, in the tradition's terms, an uncollated manuscript — present but unreliable.

---

## Conclusion: the protocol's architecture is sound but its inventories are incomplete

The protocol demonstrates genuine sophistication — the three-tier indivisibility system, the structural family taxonomy, the scholarly integrity arbitration rule, and the provenance classification (FP-5) all reflect serious engagement with the Islamic textual tradition. The five gaps identified here are not design failures but **inventory gaps and classification errors** that can be resolved with targeted additions.

**Three changes are critical and should block deployment** until resolved: adding the three missing sciences (kalām, farāʾiḍ, taṣawwuf) to §4.3, adding the five missing indivisible units (mujmal/mubayyan, dalīl/wajh, tarjīḥ, istidrāk/tanbīh, waqf markers) to §4.3, and reclassifying [COM] from a peer family to an orthogonal layer dimension. Without these, the system will silently corrupt every kalām text it processes (splitting shubhah from radd), every farāʾiḍ text (splitting worked problems mid-calculation), every sharḥ text outside ḥadīth (failing to track matn-sharḥ boundaries), and every uṣūl passage containing mujmal/mubayyan or tarjīḥ blocks.

**Two changes are high-severity and should be implemented before scaling**: the madhhab-context parameter for §4.13 and the discipline-homogeneous batching rule for §4.15. These prevent systematic misrepresentation of school-specific structures and systematic owner disengagement, respectively.

The deepest lesson from this review is one the Islamic scholarly tradition articulated fourteen centuries ago: **textual integrity is not a feature — it is a prerequisite.** The tradition built the most rigorous pre-modern system of text verification precisely because it understood that silent corruption is worse than no text at all. The protocol's FP-5 already states this ("Knowledge corruption is the worst failure. Silent corruption worse than visible"). The additions proposed here are what FP-5 requires when applied to the full scope of the classical Arabic scholarly corpus.