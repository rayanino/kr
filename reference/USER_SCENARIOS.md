# KR User Scenarios

These scenarios make the application concrete. Every design decision should serve at least one of these. When the architect writes any SPEC, these scenarios answer "but what does the user actually experience?"

---

## Scenario 1: Day 1 — First Launch

Rayane opens KR for the first time. The library has been seeded with a small collection of Arabic language science texts (Nahw, Sarf, Balagha).

**KR:** "Welcome to خزانة ريان. I have 12 sources in the library across 3 Arabic language sciences. You mentioned wanting to start with Arabic language sciences. I've designed a study curriculum based on the classical pedagogical progression:

**Nahw (Grammar):**
1. متن الآجرومية — foundational text, 30 topics
2. قطر الندى — Ibn Hisham's intermediate grammar, 85 topics
3. ألفية ابن مالك with شرح ابن عقيل — advanced, 1002 lines of verse with commentary

I recommend starting with الآجرومية. Shall I open the first topic?"

Rayane: "Yes."

**KR** opens the first excerpt — the definition of الكلام — displayed with:
- The primary text (from the original source, with full citation)
- A synthesized entry explaining the concept with positions from multiple grammarians
- A note: "This topic connects to: Usul al-Fiqh (how legal texts are interpreted relies on this grammatical foundation)"

After Rayane reads, **KR** asks: "Can you explain the difference between الكلام and الكلم in your own words?" (Socratic check)

---

## Scenario 2: Day 30 — Active Study

Rayane has been studying Nahw through الآجرومية for a month. He's 60% through.

**KR** (daily briefing): "Good morning. Today's review: 3 positions from باب المبتدأ والخبر are due for spaced repetition. You also have a new source alert: I found a Shamela copy of شرح الآجرومية by الكفراوي that adds 47 new excerpts with explanatory examples not in your current sources. Shall I acquire it?"

Rayane: "Yes, acquire it. Also — what's the difference between how Basran and Kufan grammarians define الفاعل?"

**KR** retrieves excerpts from multiple sources, presents them side by side:
- Basran position (from سيبويه's الكتاب and ابن السراج's الأصول)
- Kufan position (from الكسائي via transmitted quotes, ثعلب's المجالس)
- Each position with its evidence and the names of scholars who held it
- A note: "The Basran definition became dominant. 8 of 10 sources in your library follow it. The Kufan position survives primarily in الفراء's معاني القرآن."

---

## Scenario 3: Day 180 — Cross-Science Insight

Rayane is now studying both Nahw and Usul al-Fiqh. He's intermediate in both.

**KR** (proactive discovery): "I found an interesting connection. In Nahw, you studied how الاستثناء (exception) works grammatically (excerpt from ألفية ابن مالك, line 221). In Usul al-Fiqh, the concept of الاستثناء is a legal principle with its own rules (excerpt from الورقات by الجويني). The grammatical rules directly affect how legal exceptions are interpreted. Would you like me to generate a cross-science analysis showing how Nahw positions on الاستثناء affected specific Fiqh rulings?"

Rayane: "Yes."

**KR** generates a comparative entry that no single book contains — it synthesizes across:
- 3 Nahw sources defining الاستثناء grammatically
- 2 Usul sources defining الاستثناء as a legal tool
- 4 Fiqh sources showing rulings where the grammatical interpretation was decisive
- A timeline showing how this interaction was discussed from the 3rd to 8th century hijri

---

## Scenario 4: Day 365 — Scholarly Production

Rayane is advanced in Nahw and intermediate in Fiqh, Aqidah, and Usul. He wants to write a research paper.

Rayane: "I want to write about how different grammatical interpretations of Quran 2:228 led to different fiqh rulings on the iddah period."

**KR** (research mode): "This is a well-documented case. Here's what I found in the library:

**The grammatical question:** Does القروء in the verse refer to menstrual periods (حيض) or purity periods (طهر)? This is a Nahw question (semantics of a plural form).

**The fiqh consequences:** Hanafi and Hanbali schools say حيض (3 menstrual cycles). Shafi'i and Maliki schools say طهر (3 purity periods). The practical difference affects the iddah duration by days.

**Sources in your library:** 14 excerpts from 9 sources. [Lists them with citations]

**Gap detected:** I have no source from the Zahiri school on this verse. Ibn Hazm likely addresses it in المحلى — I found a Waqfeya PDF but haven't acquired it yet. Shall I?

**Research question suggestion:** 'Did any scholar change their position on this verse over their career? I have 2 cases: [cites them].' This angle hasn't been explored in any source in your library."

Rayane writes the paper. KR assists with:
- Auto-generating footnotes from library excerpts
- Verifying every claim against the library: "You wrote 'the majority hold X' — I count 6 sources for X and 4 for Y. 'Majority' is accurate but you may want to be more precise."
- Flagging unsourced claims: "This sentence makes a claim I cannot find in any library source."

When the paper is complete, **KR absorbs it back into the library.** Rayane's tarjih on Quran 2:228 becomes an owner-originated entry at the relevant taxonomy leaf, alongside the classical scholarly entries. Future queries on this topic now include Rayane's own conclusion: "You previously concluded that the Basran grammatical interpretation is stronger because..."

---

## Scenario 5: Year 3 — Teaching Mode

Rayane is now advanced across multiple sciences. A student asks him about a topic.

Rayane: "I need to teach someone about أحكام النون الساكنة والتنوين in Tajwid. Generate a lesson plan."

**KR** (teaching mode): "Here's a lesson plan based on your library's sources and the classical teaching progression:

**Lesson structure (45 minutes):**
1. Definition and introduction (5 min) — from تحفة الأطفال, lines 10-15
2. The four rules with examples (20 min) — إظهار، إدغام، إقلاب، إخفاء
3. Quran examples for each rule (10 min) — sourced from your Tafsir excerpts
4. Common mistakes and edge cases (10 min) — from الشاطبية commentary

**Anticipated student questions with answers:**
- 'Why is ي treated differently in إدغام?' → [answer with source]
- 'Does the rule change in Warsh recitation?' → [answer comparing Hafs and Warsh]

**Your knowledge check:** Before teaching this, can you explain why إقلاب specifically turns the noon into a meem and not another letter? [Tests Rayane's depth before he teaches]"

---

---

## Scenario 6: New Book Briefing

Rayane just purchased حاشية ابن عابدين (a 12-volume Hanafi fiqh hashiyah) from a bookstore. He photographs the title page, table of contents, and introduction with his iPhone and uploads them to KR.

**KR** (source engine): "Processing 3 photographs... OCR complete. I've identified this as:

**رد المحتار على الدر المختار** — commonly known as حاشية ابن عابدين
- **Author:** محمد أمين بن عمر بن عبد العزيز عابدين (ابن عابدين) — d. 1252 AH / 1836 CE
- **Type:** حاشية (marginal commentary) on الدر المختار by الحصكفي, which is itself a شرح of تنوير الأبصار by التمرتاشي
- **Genre chain:** تنوير الأبصار (matn) → الدر المختار (sharh) → رد المحتار (hashiyah)
- **Science:** Fiqh — Hanafi school
- **Level:** Advanced specialist. This is the primary reference work (المرجع الأساسي) of the Hanafi school for fatwa purposes.
- **Reputation:** Considered the most authoritative late Hanafi fiqh reference. When Hanafi scholars say 'the mu'tamad position,' they often mean Ibn Abidin's conclusion here.

**Before reading this, you should know:**
- Prerequisites: at least intermediate Hanafi fiqh (you're currently at: beginner+). I recommend finishing متن القدوري first (you're 40% through).
- This is NOT an introductory text. It presumes familiarity with Hanafi terminology, usul methodology, and the positions of earlier Hanafi scholars (Abu Hanifa, Abu Yusuf, Muhammad al-Shaybani).
- 12 volumes, ~6000 pages. Most scholars study it chapter by chapter alongside their area of research, not cover to cover.

**This edition:** Publisher appears to be دار الفكر, Beirut. This is the standard scholarly edition. I found 2 other editions in Shamela — comparing tables of contents to check for content differences...

**Recommended approach:** Don't read sequentially. Use this as a reference alongside your study of القدوري. When you encounter a fiqh topic in القدوري, I'll pull the relevant section from ابن عابدين to show you how the position was refined over the centuries.

Shall I acquire the full text (I'll need you to photograph or scan the remaining pages), or would you like to use the Shamela digital version for the text and keep your physical copy as the verified edition?"

---

## Scenario 7: "Show Me the Whole Science"

Rayane has been studying Nahw for 6 months. He feels lost — he knows individual topics but can't see how they connect.

Rayane: "Draw me a map of Nahw. I want to see the whole science — every topic, how they connect, what I've studied, what's left."

**KR** (taxonomy engine + scholar interface): Generates an interactive visualization:

**The Nahw Map** — 247 topics across 12 major chapters (أبواب)

[Visual: a structured tree/graph where:]
- **Green nodes** = topics Rayane has studied and passed Socratic checks on (87 topics)
- **Yellow nodes** = topics Rayane has seen but not mastered (23 topics)
- **Gray nodes** = topics not yet studied (137 topics)
- **Solid arrows** = prerequisite dependencies ("you must understand X before Y")
- **Dashed arrows** = conceptual connections ("X is related to Y but neither requires the other")
- **Node size** = topic significance (how many other topics depend on it)
- **Red highlights** = coverage gaps ("no Kufan source for this topic in your library")

Rayane taps on باب الحال (the chapter on circumstantial expressions). The map zooms in:

"**باب الحال** — 15 topics. You've studied 3.

**This chapter depends on:** المفعول به (direct object), النعت (adjective), الفاعل (subject) — all green ✓

**Current topic:** تعريف الحال. Here's where it sits: الحال is one of the five منصوبات (accusative constructions). It answers the question 'in what state/condition?' about the subject or object. It connects to النعت (both describe nouns, but النعت is permanent while الحال is temporary) and to التمييز (both are منصوب, but التمييز specifies kind while الحال specifies state).

**Scholarly landscape:** 4 schools of thought on whether الحال can precede what it describes. 11 excerpts from 7 sources in your library cover this topic."

---

## Scenario 8: KR Gets It Wrong

Rayane is reading an entry on المفعول المطلق (absolute object) and notices an error.

Rayane: "This entry says that Ibn Malik considers المصدر and المفعول المطلق to be the same thing. That's wrong — he distinguishes them in the Alfiyyah, line 199."

**KR** (correction mode): "Let me check. Pulling the excerpt this claim came from...

You're right. The excerpt from شرح ابن عقيل says 'وهو المصدر المنتصب' — which means the المفعول المطلق IS a مصدر (verbal noun), but not that every مصدر is a مفعول مطلق. The entry incorrectly generalized this as equivalence.

**What went wrong:** The excerpting engine captured the correct text, but the synthesizing engine misinterpreted the relationship as bidirectional equivalence when it's actually a subset relationship (every مفعول مطلق is a مصدر, but not every مصدر is a مفعول مطلق).

**Corrections applied:**
1. ✓ Entry regenerated with corrected relationship
2. ✓ Your correction saved as an owner note at this leaf — future synthesis will check against it
3. ✓ Pattern flagged: the synthesizer will now be more careful about subset vs. equivalence relationships across ALL entries, not just this one

**Verification:** Here's the corrected passage — does this match your understanding?

'ابن مالك defines المفعول المطلق as a subset of المصدر: specifically, the مصدر that appears in the accusative case to confirm, specify, or quantify the verb's action. The المصدر is a broader concept that includes non-accusative uses (e.g., المصدر المضاف إليه).'"

---

## What These Scenarios Require

| Capability | Scenarios that need it |
|---|---|
| Curriculum design | 1, 2 |
| Excerpt retrieval with citation | All |
| Socratic dialogue | 1, 5 |
| Spaced repetition | 2 |
| Autonomous source discovery | 2, 4, 6 |
| Cross-source comparison | 2, 3, 4 |
| Cross-science linking | 3 |
| Proactive alerts | 2, 3 |
| Gap detection | 4, 7 |
| Temporal analysis | 3 |
| Writing assistance | 4 |
| Footnote generation | 4 |
| Claim verification | 4, 8 |
| Lesson plan generation | 5 |
| Research question generation | 4 |
| School-comparative analysis | 2, 4 |
| Source acquisition on demand | 2, 4, 6 |
| Owner-originated content (feedback loop) | 4, 8 |
| Book briefing (pre-reading intelligence) | 6 |
| Science map / structural visualization | 7 |
| Prerequisite tracking and display | 6, 7 |
| OCR / image-to-text pipeline | 6 |
| Error correction and system learning | 8 |
| Pattern-level error propagation | 8 |
