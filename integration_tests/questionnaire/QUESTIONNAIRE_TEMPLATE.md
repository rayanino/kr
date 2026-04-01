# Owner Q&A Questionnaire — Excerpting Engine Calibration

> **Instructions for the owner:** For each section, read the example excerpts and answer the questions honestly. There are no wrong answers — your reactions tell us exactly what the library should do. Take your time. Answer in Arabic or English, whichever feels natural.
>
> **Instructions for the team:** After the owner fills this in, each answer maps to a SPEC rule or prompt calibration. The "Translation" section under each question explains how to convert the answer.

---

## 1. Granularity — How Big Should an Excerpt Be?

**Example excerpts to review:**
- Open `integration_tests/campaign_20260331/taysir/excerpts.jsonl` — pick 3 excerpts of different lengths (short: <200 words, medium: 200-500 words, long: >500 words)
- Show them to the owner as rendered text (not JSON)

**Questions:**
a) When you read the SHORT excerpt, is it enough to understand the point? Or does it feel like a fragment?

> _Owner response:_

b) When you read the LONG excerpt, is it all one topic? Or does it feel like it covers too many things?

> _Owner response:_

c) If you had to choose: would you rather excerpts are too short (missing context) or too long (covering multiple topics)?

> _Owner response:_

**Translation:** Answer (a) calibrates the minimum excerpt length threshold. Answer (b) calibrates the maximum / topic-splitting sensitivity. Answer (c) sets the bias direction for edge cases.

---

## 2. Self-Containment — How Much Context Do You Need?

**Example excerpts to review:**
- Pick an excerpt with a `context_hint` field (partial excerpt with external context)
- Pick an excerpt that references "as mentioned earlier" (backward reference)

**Questions:**
a) Read this excerpt without looking at anything else. Can you understand the main point?

> _Owner response:_

b) What would you need to see alongside this excerpt to fully understand it? (e.g., the definition from the previous page, the ruling being commented on)

> _Owner response:_

c) Is it okay if an excerpt says "as mentioned earlier" without showing what was mentioned? Or is that frustrating?

> _Owner response:_

**Translation:** Answer (a) tests current self-containment quality. Answer (b) identifies what context_hint should contain. Answer (c) determines whether cross-references need resolution or just preservation.

---

## 3. Comparison Experience — Side-by-Side Excerpts

**Example excerpts to review:**
- Pick 3 excerpts from DIFFERENT books on the SAME fiqh topic (if available in campaign data)

**Questions:**
a) When you see three different scholars' positions on the same topic, is this useful?

> _Owner response:_

b) What makes the comparison work or not work? (e.g., are the excerpts at the same level of detail?)

> _Owner response:_

**Translation:** Answers inform whether excerpts need to be normalized for comparability, and what metadata (scholar name, school, date) should be prominently displayed.

---

## 4. Definition Handling — Together or Separate?

**Example excerpts to review:**
- Pick an excerpt that contains both a linguistic definition (لغة) and a legal definition (شرعا/اصطلاحا)
- Show it as-is, then show it split into two excerpts

**Questions:**
a) When you see the linguistic and legal definitions together, does that feel complete?

> _Owner response:_

b) If they were separate excerpts, would you want to see them linked? Or is separate fine?

> _Owner response:_

c) When studying, do you usually look up the linguistic meaning first, then the legal one? Or do you want both at once?

> _Owner response:_

**Translation:** Answers calibrate DR-1 (definition pair splitting). Answer (a) tests the current behavior. Answer (b) determines the companion-link requirement. Answer (c) reveals the study workflow expectation.

---

## 5. Evidence Handling — Ruling + Evidence

**Example excerpts to review:**
- Pick an excerpt with a fiqh ruling that includes its Quran/hadith evidence
- Show the ruling alone, then the ruling+evidence together

**Questions:**
a) When you read a ruling, do you always want to see the evidence (Quran verse, hadith) right there?

> _Owner response:_

b) Or would you prefer to see the ruling first, and tap to see the evidence separately?

> _Owner response:_

c) If the evidence is from a well-known hadith, do you still want it shown? Or is the reference enough?

> _Owner response:_

**Translation:** Answers determine whether evidence stays within the excerpt or becomes a linked reference. This calibrates whether DR-2 (evidence-type splitting, currently deferred) should be reconsidered.

---

## 6. Scholarly Debate — Full Khilaf or Individual Positions?

**Example excerpts to review:**
- Pick a khilaf passage (scholarly disagreement) with multiple madhab positions
- Show it as one full excerpt, then show individual positions as separate excerpts

**Questions:**
a) When studying a topic, do you want to see all scholarly positions together in one place?

> _Owner response:_

b) Or would you prefer each position as its own excerpt that you can navigate between?

> _Owner response:_

c) Is it important to see WHO holds each position (which scholar, which school)?

> _Owner response:_

**Translation:** Answers calibrate DR-3 (khilaf preservation). Answer (a) vs (b) determines whether khilaf passages stay unified or get split. Answer (c) determines metadata granularity requirements.

---

## 7. Genre Differences — Does Science Matter?

**Example excerpts to review:**
- Pick one fiqh excerpt, one nahw (grammar) excerpt, one hadith excerpt

**Questions:**
a) Do these feel like the same kind of "excerpt" to you? Or do they feel fundamentally different?

> _Owner response:_

b) For grammar (nahw), do you want the example sentence (shaahid) inside the excerpt or separate?

> _Owner response:_

c) For hadith, do you want the full chain of narrators (isnad) in the excerpt? Or just the content (matn)?

> _Owner response:_

**Translation:** Answers determine whether excerpting prompts need genre-specific behavior or if one-size-fits-all works. This has major implications for prompt complexity.

---

## 8. Navigation — What Comes Next?

**Questions:**
a) When you finish reading one excerpt, what do you want to see next? (Options: next excerpt from same book, related excerpts from other books, back to table of contents, nothing specific)

> _Owner response:_

b) If you're studying a fiqh topic, do you want to jump to what other scholars say about the same topic? Or continue reading the same author's text?

> _Owner response:_

c) Do you ever want to "go deeper" — like seeing the commentary on a commentary (hashiyah on sharh)?

> _Owner response:_

**Translation:** Answers inform cross-reference design and the taxonomy engine's linking requirements. This feeds into synthesis engine (engine 7) design decisions.

---

## 9. The "No Puzzle" Rule — Partial Excerpts

**Example excerpts to review:**
- Pick an excerpt that has a `context_hint` (meaning it's partial and needs context)

**Questions:**
a) Read this excerpt with the context hint. Is the hint enough to understand what's going on?

> _Owner response:_

b) Would you rather have a longer excerpt that includes the context directly, even if it means mixing topics?

> _Owner response:_

c) Is a partial excerpt ever acceptable? Or do you always want the complete thought?

> _Owner response:_

**Translation:** Answer (c) is the critical one — it determines whether the "no puzzle excerpts" principle is absolute or has acceptable exceptions. This directly calibrates the self-containment gate.

---

## 10. Study Workflow — A Day in the Library

**Questions:**
a) Walk me through a typical study session. What do you open first? What are you trying to learn?

> _Owner response:_

b) When you have a question about a fiqh topic (e.g., how to do wudu), what do you want to see?

> _Owner response:_

c) Do you study one book at a time, or do you want to study a TOPIC across multiple books?

> _Owner response:_

d) How important is it to you that the library shows you the ORIGINAL text exactly as the author wrote it, versus a cleaned-up summary?

> _Owner response:_

**Translation:** These answers define the user model for the entire system. Answer (d) is critical — it determines whether the library is a reference tool (show originals) or a learning tool (show summaries). This has implications for every engine.

---

## After Filling In

1. Each answer gets translated into a SPEC rule or prompt calibration by the engineering team
2. Every technical decision traces back to a specific owner answer (traceability requirement)
3. The questionnaire itself is preserved as a project artifact — it IS the requirements document for the excerpting engine's quality definition
