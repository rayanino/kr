# DR Relay Prompts: System Prompt Final Review

Three prompts below — one each for ChatGPT DR, Claude DR, and Gemini DR.
Send each to a separate Deep Research session.

---

## 1. ChatGPT DR — Adversarial Stress Test

> Read the file `.claude/system-prompt.md` in the KR repo (branch: clean-start).
>
> This is a custom system prompt that replaces Claude Code's default behavioral instructions. It's designed for the KR project — an Islamic scholarly library pipeline.
>
> YOUR TASK: Try to break it. Construct 5 realistic scenarios where an agent following this system prompt would produce WRONG behavior. Focus on:
>
> 1. A scenario where the coworker dispatch table creates a deadlock (e.g., dispatch required to commit, but dispatch itself produces code changes that need dispatch).
> 2. A scenario where "fix adjacent broken code" causes the agent to change code it shouldn't, in a way that's hard to detect.
> 3. A scenario where Arabic text rules conflict with each other (e.g., "strip kashida" vs "preserve byte-for-byte").
> 4. A scenario where the "inform rather than ask" commit pattern leads to an unwanted commit on master.
> 5. A scenario where context pressure + dispatch mandate creates an unresolvable conflict.
>
> For each scenario: describe the setup, the agent's likely behavior, why it's wrong, and how to fix the system prompt to prevent it.

---

## 2. Claude DR — Scholarly Integrity Review

> Read `.claude/system-prompt.md` in the KR repo (branch: clean-start).
>
> This system prompt governs an AI agent processing classical Arabic Islamic scholarly texts (fiqh, hadith, tafsir, aqidah, etc.).
>
> YOUR TASK: Review the Arabic Text Awareness section for scholarly completeness. Consider whether it adequately protects:
>
> 1. Quranic text integrity (ayah boundaries, bismillah handling, citation formulas like قال تعالى)
> 2. Hadith chain (isnad) preservation across processing boundaries
> 3. Scholar name disambiguation (كنية, نسبة, لقب components)
> 4. Multi-layer text detection (matn, sharh, hashiyah, ta'liq)
> 5. Colophon processing (copyist vs author, date extraction, manuscript provenance)
> 6. Cross-reference formulas (كما تقدم, سيأتي, انظر) that must be preserved in excerpts
>
> Also evaluate: Is the "Coworker Dispatch" section strong enough to prevent a single AI model from making content quality judgments about Islamic scholarly texts without peer review?
>
> Provide specific additions or amendments with exact text to insert.

---

## 3. Gemini DR — Islamic Pedagogy & Methodology Review

> I'm uploading the file `.claude/system-prompt.md` from the KR project.
>
> [UPLOAD THE FILE: C:\Users\Rayane\Desktop\kr\.claude\system-prompt.md]
>
> This system prompt controls an AI agent building a personal Islamic scholarly library. The pipeline processes classical Arabic texts and extracts teaching units.
>
> YOUR TASK: Review from an Islamic studies methodology perspective:
>
> 1. Does the prompt adequately protect against misattribution of scholarly opinions? (e.g., confusing a student's view with the teacher's, or a madhab position with the author's personal preference)
> 2. Are the Arabic text rules complete from an Islamic sciences perspective? What would a مُحَقِّق (critical editor) find missing?
> 3. The "Coworker Dispatch" section requires multi-model consensus for content decisions. Is this appropriate for Islamic scholarly content? Are there decisions that should NEVER be automated even with consensus?
> 4. Does the prompt protect the distinction between: Quranic text, Prophetic hadith, athar (companion sayings), scholarly opinions, and editorial additions?
> 5. What would you add to ensure the pipeline never presents a weak hadith as sahih, or a minority opinion as the majority view?
>
> Provide specific text additions with placement guidance.
