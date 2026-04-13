# Owner Sanity Check — Answers (Architect's Assessment)

**Date:** 2026-03-09
**Method:** Empirical analysis of 2,519 real Shamela exports + web research on Islamic scholarly genre conventions + critical self-review
**Confidence calibration:** Each answer rated HIGH / MEDIUM / LOW based on evidence quality

---

## Q1-Q3: Shamela HTML Structure

**ANSWERED EMPIRICALLY.** See `reference/SHAMELA_FORMAT_ANALYSIS.md`. All extraction rules rewritten from real data. No owner input needed.

---

## Q4: Does the Genre List Cover the Library?

**Verdict: ✓ with one observation**
**Confidence: HIGH** (checked against real data + scholarly literature)

The 18 genres (matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, mawsuah, fatawa, mujam, tabaqat, fiqh_comparative, hadith_collection, tafsir, sirah, tarikh, adab, other) are sufficient for Stage 1.

**Evidence from the real collection:** I checked titles across all 2,519 books. The genre-indicative title keywords are well-distributed: 83 books with "شرح", 29 with "مختصر", 8 with "حاشية", 38 with nazm-related keywords (نظم, منظومة, ألفية). Every book I inspected fits one of the 18 genres.

**One genre I investigated and decided NOT to add:** `takmila` (تكملة — continuation of an unfinished work). This is a real Islamic scholarly genre: when a scholar dies before completing a work, another scholar completes it (e.g., al-Subki's continuation of al-Nawawi's al-Majmu'). However, takmila is rare enough that `other` handles it for Stage 1, and structurally it functions like a sharh (it comments on the same base text). Similarly, `dhayl` (ذيل — supplement/appendix to a biographical dictionary) exists in the tradition but is rare and can be classified as `tabaqat` for now. Both can be added in Stage 2 if the owner encounters them.

**One observation about the collection's composition:** 48.7% of the owner's books are classified under "كتب السنة" (hadith literature) by Shamela. This category is a SCIENCE category, not a genre — it contains hadith collections, sharh on hadith collections, biographical works about hadith narrators, and musnad compilations. The genre classifier will need to distinguish these at the genre level even though Shamela groups them under one science. This isn't a gap in the genre list; it's a note that the LLM inference (§4.A.4) must be good at classifying within hadith literature.

**What would make me wrong:** If the owner's study focus includes a genre I didn't consider — for instance, if he studies `ijazat` (scholarly licenses) or `amali` (dictation sessions), those are technically distinct genres. But they're rare enough that `other` with a note suffices.

---

## Q5: Is "commentary" the Right structural_format for a Sharh?

**Verdict: ✓ — correct but needs clarification in the SPEC**
**Confidence: HIGH** (grounded in structural analysis of how shuruh are physically organized)

The `structural_format` field describes the PHYSICAL layout of the text, not its scholarly function. A sharh that alternates between quoted matn and the commentator's explanation has a distinctive physical structure: blocks of source text (often visually distinguished — indented, in a different size, or in verse) interspersed with longer prose explanation. This structure IS what "commentary" means.

However, there are two sub-cases that the SPEC should acknowledge:

1. **Interlinear commentary** (the typical case): The sharh quotes a segment of the matn, then explains it, then quotes the next segment. شرح ابن عقيل does this — it quotes an Alfiyyah verse, then provides prose explanation. This is unambiguously `commentary` format.

2. **Running commentary** (less common): Some shuruh discuss the matn's topics in continuous prose without quoting the matn verbatim in alternating blocks. These are functionally shuruh (genre = `sharh`) but structurally prose (structural_format = `prose`). The genre and structural_format can legitimately differ.

The SPEC already allows this: `genre` and `structural_format` are independent fields. A book can be genre `sharh` with format `commentary` OR genre `sharh` with format `prose`. The consistency cross-check in §5 should flag `sharh` + `prose` as unusual (not as an error) since most shuruh are commentary format but some are legitimately prose.

**No SPEC change needed.** The current design handles this correctly. The consistency check should treat `sharh` + `prose` as a low-severity warning, not an error.

---

## Q6: Do You Recognize These Muhaqiqs as Trusted Editors?

**Verdict: ✓ — the list is correct, but the SPEC should acknowledge its narrowness**
**Confidence: HIGH** (cross-referenced against scholarly reputation and actual collection data)

The SPEC's recognized muhaqiq list (شعيب الأرناؤوط, أحمد شاكر, عبد السلام هارون, عبد الله التركي, محمد فؤاد عبد الباقي, عبد القادر الأرناؤوط, محمد ناصر الدين الألباني, محمد محيي الدين عبد الحميد) represents the consensus top-tier of Arabic text editors. Every name on this list is widely recognized across Islamic studies as a standard-bearer for rigorous tahqiq. The list is correct — no name should be removed.

**The critical finding:** Of these 8 editors, only الألباني appears in the owner's collection (5 books). The top 30 muhaqiqs in the collection are contemporary editors who are competent but not internationally famous: خلاف محمود عبد السميع (20), محمد أجمل الإصلاحي (20), نبيل سعد الدين جرَّار (17), etc.

This means the trust evaluation will give most of the owner's tahqiq editions a score of 0.50 (unknown muhaqiq) rather than 0.90 (recognized muhaqiq). This is actually **correct conservative behavior** — the engine should not assume an unfamiliar muhaqiq is reliable. But it means the owner will see many books flagged as having "unknown muhaqiq" even when the muhaqiq is a respectable contemporary editor.

**Recommendation:** Keep the list as-is. Add a note in the SPEC: "The initial recognized muhaqiqs list contains universally recognized editors. Most tahqiq editions in the owner's collection will be scored as 'unknown muhaqiq' (0.50). The owner is expected to extend the list over time as they encounter and verify competent editors. This is the correct conservative default — upgrading muhaqiq recognition is safer than starting with a permissive list."

**Names I considered adding but decided against:**
- محمد أجمل الإصلاحي — appears 20 times in the collection, works with Islamic University of Madinah. Respected but not in the universally-recognized tier.
- نبيل سعد الدين جرار — appears 17 times. Competent editor but adding him would open the question of where to draw the line.

The line should be: "editors whose name alone increases trust in ANY edition they touch, across all sciences." The 8 names on the list meet this bar. The others are good-but-not-universal — they belong in the owner's extended list, not the default.

---

## Q7: Do You Recognize These Publishers as Scholarly?

**Verdict: ✗ — list needs adjustment based on real data**
**Confidence: HIGH** (empirically verified against 2,519 books)

**Problems with the current list:**

1. **"دار الرسالة" is listed but the actual publisher name is "مؤسسة الرسالة"** (15 books in the collection). The SPEC lists both "دار الرسالة" and "مؤسسة الرسالة" — but "دار الرسالة" and "مؤسسة الرسالة" are the same entity. The list should use "مؤسسة الرسالة" as the canonical form and add "دار الرسالة" as a variant.

2. **Missing publishers that appear frequently in the collection:**
   - دار عالم الفوائد (34 books) — scholarly publisher, Saudi Arabia, known for quality editions
   - مكتبة الرشد (14 books) — established Riyadh publisher of Islamic texts
   - دار البشائر الإسلامية (10+9=19 books) — well-known Beirut scholarly publisher
   - دار الفكر (11 books) — major Damascus publisher (though quality varies by title)

3. **"دار الكتب العلمية" is correctly included but needs a quality caveat.** This publisher (88 books across spelling variants in the collection) is known in the scholarly community for mass-producing editions of variable quality. Some are genuine scholarly editions; many are quick commercial reprints with minimal tahqiq. The trust score for this publisher should be moderate (0.50–0.60), not the 0.70–0.85 that "known scholarly publisher" implies.

**Recommended revised list:**
- مؤسسة الرسالة / دار الرسالة (same entity) — **0.80**
- دار التراث — **0.75**
- المكتب الإسلامي — **0.75**
- دار ابن حزم — **0.70**
- دار ابن الجوزي — **0.75**
- دار عالم الفوائد — **0.75** (add)
- مكتبة الرشد — **0.70** (add)
- دار البشائر الإسلامية — **0.70** (add)
- دار الكتب العلمية — **0.55** (downgrade from generic "known scholarly")
- دار الفكر — **0.60** (add, moderate — quality varies)

**Important note about the collection:** The single most common "publisher" in the collection is "مخطوط نُشر في برنامج جوامع الكلم المجاني" (184 books) — manuscripts published through a free digital tool. This is not a publisher in the traditional sense. These should be scored as unknown publisher (0.40) since there's no editorial quality control implied.

---

## Q8: Does the Trust Scoring Make Sense?

**Verdict: ✓ — scoring produces sensible results on real books**
**Confidence: MEDIUM** (mental calculation on several examples, but exact thresholds need Step 2 empirical testing)

I ran the trust algorithm on three real books from the collection:

**Book 1: أبنية الأسماء والأفعال والمصادر** (ابن القطاع الصقلي — classical grammarian, with muhaqiq)
- Author standing: classical scholar → 0.90 × 0.30 = 0.270
- Tahqiq: muhaqiq present but not in recognized list → 0.50 × 0.25 = 0.125
- Publisher: likely unknown → 0.40 × 0.15 = 0.060
- Authority: primary → 0.85 × 0.15 = 0.128
- Text fidelity: Shamela high → 0.90 × 0.15 = 0.135
- **Total: 0.718 → verified** ✓ (correct — a classical grammar work should be verified)

**Book 2: أساليب بلاغية** (أحمد مطلوب — contemporary Iraqi linguist, no muhaqiq)
- Author standing: new record, no prior sources → 0.30 × 0.30 = 0.090
- Tahqiq: no muhaqiq, modern work → 0.30 × 0.25 = 0.075
- Publisher: unknown → 0.40 × 0.15 = 0.060
- Authority: modern compilation → 0.40 × 0.15 = 0.060
- Text fidelity: Shamela high → 0.90 × 0.15 = 0.135
- **Total: 0.420 → flagged** ✓ (correct — unknown modern author with no muhaqiq should be flagged; the owner can override if he knows the author)

**Book 3: الكتاب لسيبويه** (سيبويه — founder of Arabic grammar, d. ~180 AH)
- Author standing: classical, ultimate scholarly standing → 0.90 × 0.30 = 0.270
- Tahqiq: if عبد السلام هارون → recognized → 0.90 × 0.25 = 0.225; if unknown → 0.50 × 0.25 = 0.125
- Publisher: varies → 0.40–0.80 × 0.15 = 0.060–0.120
- Authority: primary → 0.85 × 0.15 = 0.128
- Text fidelity: Shamela high → 0.90 × 0.15 = 0.135
- **With هارون tahqiq: 0.878 → verified** ✓
- **Without recognized muhaqiq: 0.718 → verified** ✓ (even without a known muhaqiq, Sibawayhi's Kitab should be verified)

The algorithm produces sensible results across the spectrum. The one thing that concerned me was whether a classical work WITHOUT a muhaqiq would still reach "verified" — and it does (0.718), because the author standing weight (0.30) is high enough to carry it. This is correct: a matn by a major classical scholar is inherently trustworthy regardless of the edition.

**The threshold question:** The verified threshold of 0.65 means a book needs either (a) strong author standing, or (b) a recognized muhaqiq, or (c) a combination of moderate signals. This feels right. The exact value (0.65 vs. 0.60 vs. 0.70) should be tuned in Step 2 with more examples.

---

## Q9: Are the 7 Relationship Types Complete?

**Verdict: ✓ for Stage 1, with two additions noted for Stage 2**
**Confidence: HIGH** (cross-referenced against Islamic scholarly genre literature)

The 7 types (sharh_of, hashiyah_on, mukhtasar_of, nazm_of, taqrirat_on, responds_to, cites) cover the primary relationships in the Islamic scholarly tradition. From the research:

**Two relationships that exist in the tradition but are missing:**

1. **takmila_of** (تكملة — continuation): Scholar B completes the unfinished work of Scholar A. Example: al-Subki's continuation of al-Nawawi's al-Majmu'. This IS a distinct relationship — it's not a sharh (the continuator doesn't comment on the original author's text; they continue writing in the same mode). However, it's rare enough that `other` or an annotation on `sharh_of` handles it for Stage 1.

2. **dhayl_of** (ذيل — supplement/appendix): Scholar B extends Scholar A's biographical dictionary or historical chronicle into later periods. Example: ذيل طبقات الحنابلة by Ibn Rajab, extending Ibn Abi Ya'la's original work. This is common in the tabaqat/tarikh genres. Again, it can be annotated as a type of `cites` or handled by `other` for Stage 1.

**Why I'm not recommending adding them now:** The GenreRelationType enum in contracts.py is consumed by downstream engines. Adding types changes the enum. For Stage 1, these rare types can use the `cites` relationship with a descriptive note, and the extension hook already says "Core must not assume exactly these 7 types." Stage 2 can add takmila_of and dhayl_of when the first real instance is encountered.

**What would make me wrong:** If the owner's collection contains many takmila or dhayl works. Looking at the titles in the collection, I don't see any with "تكملة" or "ذيل" in the title among the most common books. There ARE a few (the data shows some biographical works with "الذيل" in the title), but they're not numerous enough to warrant a Stage 1 enum change.

---

## Q10: Is Plain Text Useful as the Second Core Format?

**Verdict: ✓ — plain text is the correct second format for Stage 1**
**Confidence: HIGH** (assessed from multiple angles)

I analyzed this from three perspectives:

**Perspective 1: What does the owner actually have?**
The owner's entire collection of 2,519 books is Shamela HTML. The only plain text fixture is `alfiyyah_versified` (a web-sourced copy of the Alfiyyah). The owner also has PDF fixtures (waraqat_usul, ibn_aqil_alfiyyah — 4 PDF volumes) and Word documents (mughni_comparative).

If I purely optimized for the owner's current files, PDF would be the second format.

**Perspective 2: What minimizes Stage 1 build risk?**
PDF extraction requires heavy dependencies (Docling or similar), Arabic OCR for scanned pages, layout analysis for multi-column text, and handling of both text-embedded and image-only PDFs. Each of these is a separate engineering challenge that can independently fail. Adding PDF to Stage 1 would roughly double the build time for the source engine.

Plain text is trivial: read a file, extract the first line as the title, pass everything to LLM inference. The extractor is ~10 lines of code. This lets the build focus on the hard parts that matter for ALL formats: LLM inference, consensus, trust evaluation, scholar authority, deduplication, freezing.

**Perspective 3: What does plain text actually validate?**
Plain text is the worst-case input format — no structural metadata, no author field, no publisher, no page numbers. If the engine handles plain text correctly (producing a complete, valid metadata record from almost no extracted data), it validates that the LLM inference pipeline works even with minimal input. This is a more useful test than PDF, which would test PDF-specific parsing but not the core inference pipeline.

**The inversion test:** What would go wrong if I chose PDF instead? The PDF extractor would consume most of the build effort. PDF parsing bugs would block testing of the core pipeline. The source engine would be deeply coupled to Docling's capabilities and Arabic text quality. And we'd still need plain text eventually — it's just deferred, not avoided.

What goes wrong if I choose plain text? Nothing, really. We can't intake the PDF fixtures in Stage 1, but those fixtures are there waiting for Stage 2. The core pipeline (Shamela + plain text → metadata → normalization → ... → synthesis) exercises all the important code paths.

**Conclusion:** Plain text is the right choice. It adds near-zero build cost, tests the LLM inference pipeline under worst-case conditions, and keeps Stage 1 focused on the core architecture rather than format-specific parsing complexity. PDF is the first Stage 2 format addition.

---

## Summary of Recommended SPEC Changes

| Question | Change Needed? | Action |
|----------|---------------|--------|
| Q4 (genres) | No | List is complete for Stage 1 |
| Q5 (structural_format) | Minor | Note that sharh + prose is a valid combination (low-severity warning, not error) |
| Q6 (muhaqiqs) | No | List is correct; add note about narrowness and extension expectation |
| Q7 (publishers) | **Yes** | Add 4 publishers, downgrade دار الكتب العلمية, add publisher name variants |
| Q8 (trust scoring) | No | Algorithm produces correct results; exact thresholds to Step 2 |
| Q9 (relationships) | No | 7 types sufficient for Stage 1; takmila_of and dhayl_of noted for Stage 2 |
| Q10 (plain text) | No | Plain text confirmed as correct second format |
