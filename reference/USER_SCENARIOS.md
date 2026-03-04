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

## What These Scenarios Require

| Capability | Scenarios that need it |
|---|---|
| Curriculum design | 1, 2 |
| Excerpt retrieval with citation | All |
| Socratic dialogue | 1, 5 |
| Spaced repetition | 2 |
| Autonomous source discovery | 2, 4 |
| Cross-source comparison | 2, 3, 4 |
| Cross-science linking | 3 |
| Proactive alerts | 2, 3 |
| Gap detection | 4 |
| Temporal analysis | 3 |
| Writing assistance | 4 |
| Footnote generation | 4 |
| Claim verification | 4 |
| Lesson plan generation | 5 |
| Research question generation | 4 |
| School-comparative analysis | 2, 4 |
| Source acquisition on demand | 2, 4 |
| Owner-originated content (feedback loop) | 4 |
