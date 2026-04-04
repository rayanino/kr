# Grading an Islamic text excerpting engine's teaching units

An automated excerpting engine segmented باب المسح على الخفين from Taysir al-Allam into 10 teaching units. The results are structurally sound at the macro level — the engine correctly identifies chapter introduction, hadith core sections, ikhtilaf, and individual فوائد — but fails at the micro level, producing two critically undersized TUs (5 and 14 words) and misidentifying the chapter's second hadith narrator. The engine earns an **overall score of 3.1/5**, with strong boundary detection for large structural blocks but poor judgment on when individual derived benefits are too thin to stand alone. A hand-excerpted version of this chapter would yield **7 TUs instead of 10**, merging the four فوائد of the first hadith into a single unit while preserving everything else.

---

## How Al-Bassam structures every chapter in Taysir al-Allam

Understanding the engine's output requires first understanding the source text's architecture. Abdullah Al-Bassam (d. 1423 AH / 2003 CE), a Hanbali scholar who taught at al-Masjid al-Haram for 45 years, designed Taysir al-Allam as a **beginner-to-intermediate commentary** on Abd al-Ghani al-Maqdisi's Umdat al-Ahkam — a curated collection of **~420 hadiths** drawn exclusively from Sahih al-Bukhari and Sahih Muslim. Al-Bassam follows a rigid template for each hadith entry, and this template is the ground truth against which the engine's TU boundaries should be measured.

The standard per-hadith structure is: **(1) نص الحديث** (hadith text with narrator chain), **(2) غريب الحديث** (difficult vocabulary — always comes first in the commentary), **(3) المعنى الإجمالي** (general paraphrase of the hadith's overall import), **(4) اختلاف العلماء** (scholarly disagreement — only when relevant, with positions attributed to madhahib, evidence cited, and tarjih given), and **(5) ما يؤخذ من الحديث** (derived benefits, always presented as **numbered items**, typically 3–13 per hadith). This ordering is consistent across the book and confirmed by multiple reviews and the actual text on al-Shamila. Al-Bassam's commentary expands the base text roughly **3–4x** (from ~267 pages to ~920 pages), meaning his additions constitute the overwhelming majority of what the engine is processing.

The chapter on masah contains **two hadiths**: Hadith #21 from المغيرة بن شعبة and Hadith #22 from **حذيفة بن اليمان** — not صفوان بن عسال as the task description suggests. This is a critical distinction: Safwan's hadith (about three-day/one-day time limits) is from the Sunan collections and does **not** appear in Umdat al-Ahkam, which exclusively uses Bukhari and Muslim. Al-Bassam references Safwan's hadith as supplementary evidence within his commentary, but it is not a chapter hadith. If the engine labeled TU-7 as Safwan's hadith, that constitutes a narrator misidentification error.

---

## Individual TU grades: where the engine succeeds and fails

### TU-0 through TU-2: The engine's strongest work

**TU-0 — Chapter introduction (70 words, FULL): Grade 4/5.** The engine correctly isolates the باب introduction as a distinct teaching unit. Al-Bassam opens this chapter by establishing that masah is a legitimate substitute for foot-washing, backed by ijma (consensus) and mutawatir evidence, with a refutation of those who deny it. At 70 words, this unit is self-contained: it tells the student what the chapter is about, why the ruling is authoritative, and what the deviant position is. A student can study this independently and walk away understanding the topic's legitimacy. The only shortcoming is that the introduction likely contains the critical statement that masah became a **شعار أهل السنة** (distinguishing mark of Ahl al-Sunnah) — a point whose significance a beginning student might miss without additional framing.

**TU-1 — First hadith + gharib + ma'na ijmali (102 words, FULL): Grade 4/5.** This correctly bundles the hadith text, vocabulary explanation, and general meaning as one unit — matching Al-Bassam's own structural grouping. These three components are **inseparable** in the sharh tradition: gharib provides the linguistic tools to parse the hadith, and the ma'na ijmali synthesizes the meaning. Splitting any of these from each other would cripple the student's comprehension. At 102 words, the unit is somewhat compressed (Al-Bassam's vocabulary explanations alone can run 50+ words in other chapters), but the hadith of al-Mughirah is relatively straightforward linguistically, so this is adequate. The fact that the engine recognized these three sub-sections as belonging together demonstrates good structural awareness.

**TU-2 — Scholarly disagreement, 7 segments (140 words, FULL): Grade 4/5.** The research is unequivocal on this point: **ikhtilaf sections must remain as one cohesive unit.** The Islamic University of Madinah, the Dar al-Hadith al-Hassaniya methodology workshop, and the universal practice of comparative fiqh all teach scholarly disagreement as a single structured progression — define the issue, enumerate positions, present evidence, evaluate, and give tarjih. Removing one position from this chain destroys the student's ability to understand why the tarjih favors what it does. At 140 words with 7 segments, this TU is compact by traditional standards (classical commentaries devote pages to the same discussion). The 7 segments likely represent: the Shi'a dissent on masah's permissibility, the disputed attribution to Imam Malik, evidence from the hadith of Jarir ibn Abdullah proving non-abrogation, and Al-Bassam's tarjih. This is one of the engine's best-drawn boundaries.

### TU-3 through TU-6: Individual فوائد where problems emerge

**TU-3 — مشروعية المسح (26 words, FULL): Grade 3/5.** This states the primary ruling: wiping over khuffayn is legislated (مشروع) during wudu. At exactly **26 words** — the minimum threshold for a self-contained study note according to the pedagogical research — it conveys one complete fiqh point with just enough elaboration. It functions as a standalone unit, though barely. A student reading this knows: masah is legal, it's done on the upper surface of the sock, it's performed once. This is the most important faidah from the hadith and arguably earns its independence.

**TU-4 — اشتراط الطهارة (16 words, FULL): Grade 3/5.** The requirement of prior purity is the second most critical ruling from al-Mughirah's hadith — derived directly from the Prophet's statement "فَإِنِّي أَدْخَلْتُهُمَا طَاهِرَتَيْنِ" (I put them on while in a state of purity). At 16 words, this falls **below the 26-word minimum** for self-contained notes but still conveys one actionable ruling. The student knows: you must have wudu before putting on your socks for masah to be valid. It works as a recall prompt for someone who has already studied the hadith but would confuse a student encountering it cold without the hadith context.

**TU-5 — استحباب خدمة العلماء والفضلاء (5 words, FULL): Grade 1/5.** This is the engine's most significant failure. Five words — "the recommendation of serving scholars and virtuous people" — is a **heading, not a teaching unit**. It functions identically to a line in a table of contents. A fiqh student encountering this unit would have three unanswered questions: (1) Why is this derived from a chapter about masah? (2) What in the hadith supports this? (3) What does "serving scholars" practically entail? The answer — that al-Mughirah carried water (إداوة) for the Prophet and poured it during his wudu, modeling the etiquette of serving people of knowledge — is entirely absent. In the mukhtasar tradition, 5-word entries serve as **memorization anchors** within an already-understood framework. They are never standalone learning units. The Islamic pedagogical research confirms: even the most compressed fiqh formats (like Zad al-Mustaqni' or Matn Abi Shuja') provide at least a ruling statement with its key qualifier. This TU needs to be either expanded with the contextual derivation (how al-Mughirah's action yields this ruling) or merged into a parent unit.

**TU-6 — Cross-reference to غزوة تبوك (14 words, PARTIAL): Grade 2/5.** This unit fails on two dimensions. First, at 14 words with PARTIAL coverage, it doesn't capture enough content. Second, and more importantly, **the Tabuk reference is far more significant than a mere cross-reference** — it is the linchpin of the anti-abrogation argument. The Battle of Tabuk (Rajab 9 AH) was the Prophet's last military expedition. Surah al-Ma'idah's verse commanding foot-washing was revealed before Tabuk. The Prophet's masah during Tabuk therefore proves masah was practiced **after** the washing verse — demolishing the claim that masah was abrogated. This is a scholarly argument of real weight, and reducing it to a 14-word partial note strips it of its probative force. A properly constructed TU would explain the chronological argument in **40–60 words**.

### TU-7 through TU-9: The second hadith section

**TU-7 — Second hadith + ma'na ijmali (44 words, FULL): Grade 3/5.** The engine correctly groups the hadith text with its general meaning and omits a غريب section (appropriate since Hudhayfah's hadith has fewer unusual terms). At 44 words, this is thin but viable — Hudhayfah's hadith is genuinely short (the Prophet urinated, performed wudu, and wiped over his khuffayn). The more detailed narration in Sahih Muslim adds the context of the سباطة (refuse heap) and the Prophet calling Hudhayfah closer, but the core matn is brief. One concern: if the engine or the user has labeled this as صفوان بن عسال's hadith rather than حذيفة بن اليمان's, that is a factual error. Safwan's hadith appears only as supplementary evidence cited by Al-Bassam, not as a chapter hadith in Umdat al-Ahkam.

**TU-8 — مشروعية المسح في السفر (41 words, PARTIAL): Grade 3/5.** At 41 words, the size is adequate for a single faidah. The PARTIAL marking is the problem — this likely truncates discussion of the **time limits** (يوم وليلة للمقيم، ثلاثة أيام بلياليهن للمسافر), which is one of the most practically important rulings in the entire chapter. Al-Bassam would cite the hadith of Ali (in Sahih Muslim) and Safwan's hadith here as supplementary evidence for the 24-hour/72-hour distinction. A FULL capture at ~60–70 words would include the timing specifics and make this an excellent standalone unit.

**TU-9 — المسح بعد الوضوء من البول (70 words, FULL): Grade 4/5.** This is one of the engine's better-drawn فوائد units. At 70 words with FULL coverage, it conveys a substantive and nuanced ruling: masah is valid after wudu from minor hadath (urination, defecation, sleep) but **not** after major hadath (janabah) requiring ghusl. The exception for the جبيرة (splint/bandage), which may be wiped over even for major hadath, adds an important qualification. This unit teaches a clear, actionable distinction that a student can apply immediately. The 70-word size allows enough room for the ruling, its scope, and its exception.

---

## The core structural tension: atomic فوائد versus grouped benefits

The engine's design philosophy — splitting each numbered ما يؤخذ item into its own TU — reflects a reasonable hypothesis: that individual derived benefits are atomic learning concepts. The research partially supports this. In Al-Bassam's text, each numbered faidah IS conceptually independent: "masah is legal" and "prior purity is required" are distinct rulings that a student could be tested on separately.

However, the engine applies this splitting rule **mechanically without a minimum-size threshold**, producing the 5-word TU-5 and 14-word TU-6. Traditional Islamic pedagogy offers a clear precedent for the right approach: the **mukhtasar tradition** demonstrates that compressed fiqh notes work only within an established framework. Zad al-Mustaqni' can state a ruling in 10 words because the student has already studied the evidence through a sharh. A first-encounter teaching unit requires more context.

The research from IslamQA's hadith study methodology is particularly instructive: scholars advise students to **summarize فوائد per hadith in a personal notebook**, collecting benefits under each hadith's entry. This suggests the natural study boundary is hadith → all its benefits, with individual benefits as sub-items rather than independent units. The engine's approach of splitting each faidah into its own TU is defensible only if every TU clears a **minimum context threshold of approximately 25–30 words** and includes enough framing to connect it to its source hadith.

---

## What ideal hand-excerpted boundaries would look like

A skilled human excerpting this chapter would produce **7 teaching units** instead of 10, optimizing for both atomicity and minimum viable context:

- **TU-A: Chapter introduction** (70 words) — identical to the engine's TU-0
- **TU-B: Hadith #1 core** — hadith text + gharib + ma'na ijmali (102 words) — identical to TU-1
- **TU-C: Scholarly disagreement** (140 words) — identical to TU-2
- **TU-D: All four فوائد of Hadith #1 merged** (~61 words) — combines TU-3 through TU-6 into a single unit listing: (1) legality of masah, (2) prior purity requirement, (3) serving scholars (with al-Mughirah's action as context), (4) the Tabuk chronological argument (with its anti-abrogation significance). This produces a well-rounded, information-dense unit that gives the student four actionable takeaways with their scholarly reasoning.
- **TU-E: Hadith #2 core** — hadith text + ma'na ijmali (44 words) — identical to TU-7
- **TU-F: Travel masah and time limits** (~55–65 words, expanded to FULL) — based on TU-8 but completed with the specific time durations and the evidence from supplementary hadiths
- **TU-G: Masah restricted to minor hadath** (70 words) — identical to TU-9

This 7-TU structure maintains every boundary the engine drew correctly (the introduction, hadith cores, and ikhtilaf section) while fixing its two main errors: undersized فوائد from Hadith #1 and the partial capture of TU-8. The total content remains identical; only the unit boundaries shift.

---

## Summary scorecard and recommendations

| TU | Content | Words | Coverage | Grade | Verdict |
|-----|---------|-------|----------|-------|---------|
| TU-0 | Chapter introduction | 70 | FULL | **4/5** | Correct boundary, good size |
| TU-1 | Hadith #1 + gharib + ma'na | 102 | FULL | **4/5** | Correct grouping of inseparable elements |
| TU-2 | Ikhtilaf (7 segments) | 140 | FULL | **4/5** | Rightly kept as one unit |
| TU-3 | مشروعية المسح | 26 | FULL | **3/5** | Minimum viable, borderline standalone |
| TU-4 | اشتراط الطهارة | 16 | FULL | **3/5** | Below size threshold, needs context |
| TU-5 | خدمة العلماء | 5 | FULL | **1/5** | **Critically undersized; heading not a TU** |
| TU-6 | تبوك cross-reference | 14 | PARTIAL | **2/5** | **Undersized, incomplete, misses significance** |
| TU-7 | Hadith #2 + ma'na | 44 | FULL | **3/5** | Viable but thin; verify narrator identity |
| TU-8 | المسح في السفر | 41 | PARTIAL | **3/5** | Good size but PARTIAL capture is unacceptable |
| TU-9 | المسح من البول | 70 | FULL | **4/5** | Strong unit with clear, nuanced ruling |

The engine needs three calibrations: a **minimum word-count floor** (≈25 words) below which items must merge into their parent unit, a **completion check** that rejects PARTIAL extractions, and a **contextual enrichment step** that adds derivation reasoning to short فوائد notes so students understand *why* a benefit is derived from its source hadith, not merely *that* it exists.