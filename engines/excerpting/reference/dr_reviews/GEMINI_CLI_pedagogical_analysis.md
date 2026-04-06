# Gemini CLI — Pedagogical Analysis for Owner Feedback Collection

**Source:** Gemini CLI (`gemini -p`) — Islamic pedagogy perspective, Gemini 3.1 Pro
**Date:** 2026-04-07
**Scope:** Analyzed pipeline from talaqqi (traditional knowledge reception) perspective, specifically for a student seeking to bypass preparation and move directly to hifz (memorization) and fahm (comprehension).

---

## A. STUDENT_DEFINED_DATA

What ONLY the student can define for each science:

### Fiqh (Priority #1)
Primary book: الفقه على المذاهب الأربعة (Comparative Fiqh). A four-school text cannot tell the system which school the student acts upon. The student MUST define:
- **Target madhhab** — which school he memorizes/acts upon
- **Intent for other three schools** — strip entirely (prevent cognitive pollution) OR retain for muqaranah (comparative awareness)
- FP-8 (Khilaf-tarjih) identifies disputes, but only the student decides: study the khilaf or just the tarjih?

### Nahw / Sarf / Balagha / Imlaa (Arabic Sciences)
In instrumental sciences (علوم الآلة), the relationship between rule (qa'idah) and witness-text (shahid) is critical. The student must define:
- **Memorization target** — the grammatical rule, the Arabic poetry/Quranic verse, or both as atomic unit
- FP-1 assumes they belong together, but for flashcard-style rote memorization, separation may be needed

### Usul al-Fiqh (#2)
Highly dialectical (FP-20 warns of فإن قيل / قلنا trap). The student must define:
- **Pedagogical goal** — memorize foundational principles (qawa'id) only, OR train dialectical reasoning (munazarah) with arguments and counter-arguments

### Aqidah (#3)
Texts frequently quote heterodox views to refute them (FP-15: Rhetorical posture). The student must define:
- **Shubuhat exposure policy** — exposure to doubts (to learn refutation) OR sanitized orthodox-only extraction for foundational belief

## B. STUDY_METHOD_PARAMS

### FP-18 Calibration ("Study-Ready" Threshold)
The student's goal is "tell me 'just memorize it like this'" — he must define his cognitive threshold. Does a 15-word implied context (taqdir, FP-12) mentally burden him? If so, the pipeline must aggressively synthesize context_hints.

### Proof Sourcing (FP-7)
Does the student memorize:
- **Book-Preserved Proof** — exact wording the author used (possibly truncated/narrated by meaning)
- **Fetched Proof** — full verified matn from canonical hadith collections (Bukhari/Muslim)

This is a massive architectural decision if fetched proofs require cross-reference infrastructure.

### Granularity vs Cohesion (FP-9 vs FP-1)
Memorization style choice: one large cohesive paragraph (FP-1 unity) OR 5 hyper-atomized disconnected sentences (FP-9 granularity)?

### Visible Omission Tolerance (FP-19)
When the engine cuts a digression: explicit visual markers ([...]) for honesty, or "deceptive cleanliness" for rote memorization ease?

## C. GENRE_SPECIFIC_NEEDS

- **Matn** (Alfiyyah, Waraqat): Zero truncation, zero summarization, absolute tashkeel fidelity — even if it violates self-containment. Poetry cannot be modified to "make sense" alone.
- **Sharh** (Ibn Aqil): Matn fragment embedded inline as sharih wrote it, or cleanly separated (matn top, explanation bottom)?
- **Hashiyah** (Marginalia): "Pedagogical poison" for beginners. Strict filtering threshold to ignore hashiyah layers unless they resolve direct ambiguity.
- **Mukhtasar** (Fiqh Manuals): Dense, relies on deferred exceptions (الاستثناء المنفصل, FP-20). Should the pipeline "pull" exceptions from chapter end and attach to the primary ruling?

## D. TEDIOUS_VS_SUMMER

### Tedious (Collect NOW):
- FP-18 Calibration: 100+ raw Arabic excerpts graded "I can memorize this instantly" vs "needs too much prep"
- Target Madhhab & Fiqh Strategy: Changes Phase 2b grouping for الفقه على المذاهب الأربعة
- Proof Sourcing (FP-7): Architectural decision for cross-reference infrastructure

### Non-Tedious (Defer to Summer):
- Review frequencies & spaced repetition intervals (mathematical UI-layer tuning)
- Visual formatting of omissions (frontend CSS/UI decision)
- Taxonomy naming (engine maps topics; tree can be renamed later)

## E. PEDAGOGICAL_GAPS

### 1. Prerequisite Sequencing (Tadarruj)
Taxonomy is a reference structure, not a curriculum. Pipeline lacks mechanism for the student to define learning order (e.g., "do not show exceptions to Mubtada until I've memorized the definition").

### 2. Cognitive Complexity Grading
Self-containment ≠ difficulty. A perfectly self-contained advanced usul paragraph may be pedagogically inappropriate for a beginner. No mechanism to grade excerpts by difficulty.

### 3. Active Recall (Al-Ikhtibar)
"Tell me 'just memorize it like this'" requires testing (tasmee'). Pipeline lacks output testing format: cloze deletions, Q&A pairs, speech-to-text verification?
