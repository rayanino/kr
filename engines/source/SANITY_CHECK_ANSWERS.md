# Owner Sanity Check — Answers from Empirical Analysis + Domain Reasoning

**Date:** 2026-03-09
**Method:** Structural survey of 2,519 real Shamela exports, trust formula computation on 7 test cases, Islamic scholarship domain analysis, multi-angle evaluation per thinking-frameworks skill

---

## Q1–Q3: Shamela HTML Structure → ANSWERED EMPIRICALLY

See `reference/SHAMELA_FORMAT_ANALYSIS.md`. Every extraction rule was wrong and has been rewritten from real data.

## Q4: Does the genre list cover your library?

**Answer: ✓ Adequate. No changes needed.**

**Confidence: HIGH.** Checked all 18 genres against 9 Shamela categories across 2,519 books. Every category maps to one or more existing genres. Gaps considered (خطب, تخريج, تعقبات, مذكرات) are all covered by `risalah`, `other`, or relationship types rather than needing separate genres. The `other` catch-all handles edge cases. Genre affects downstream processing only through synthesis narrative framing — the normalization and passaging engines use `structural_format`, not genre.

## Q5: Is "commentary" the right structural_format for a sharh?

**Answer: ✓ Correct.**

**Confidence: HIGH.** A sharh interleaves quoted matn text with explanatory prose — this alternating reference+explanation structure IS what "commentary" means. The normalization engine needs this to detect layer transitions. The passaging engine needs this to keep matn+explanation together. `prose` would miss the internal structure; `mixed` implies format diversity not present in a typical sharh.

## Q6: Muhaqiq list — trusted editors?

**Answer: ✓ Sound. Two additions applied to SPEC.**

**Confidence: MODERATE.** All 8 original muhaqiqs verified as indisputably recognized. Added عبد الرحمن بن يحيى المعلمي اليماني (exceptional critical methodology, standard-setter for modern tahqiq) and بشار عواد معروف (Risalah Tirmidhi edition, Tarikh Baghdad, widely respected). Both are as universally recognized as anyone on the original list. The list is configurable — owner can adjust.

## Q7: Publisher list — scholarly?

**Answer: ✓ with changes applied to SPEC.**

**Confidence: MODERATE.** Key change: **دار الكتب العلمية removed from trusted list** — their mass-production model means variable quality, and the conservative principle says uncertain quality should not confer trust. Now scores as unknown (0.40). Added دار طيبة (0.75) and عالم الكتب (0.70). Publisher quality is inherently more subjective than muhaqiq quality — the list is configurable.

## Q8: Trust scoring outcomes?

**Answer: ✓ Correct across all cases.**

**Confidence: HIGH.** Computed exact scores on 7 test cases using the SPEC formula:

| Case | Score | Tier |
|------|-------|------|
| Classical + recognized muhaqiq + known publisher | 0.878 | verified |
| Unknown modern + no muhaqiq + unknown publisher | 0.420 | flagged |
| Classical + unknown muhaqiq + unknown publisher | 0.718 | verified |
| Classical + no muhaqiq (pre-modern) + unknown publisher | 0.693 | verified |
| Contemporary + recognized muhaqiq + known publisher | 0.750 | verified |
| Classical hadith imam + no muhaqiq + commercial publisher | 0.693 | verified |
| Unknown thesis author + no muhaqiq + no publisher | 0.420 | flagged |

The borderline case (classical author, no muhaqiq, unknown publisher = 0.693 → verified) is correct: pre-modern works transmitted through centuries of scholarly tradition have inherent authority independent of modern editorial apparatus.

## Q9: Relationship types complete?

**Answer: ✓ Adequate for Stage 1.**

**Confidence: MODERATE.** The 7 types cover standard Islamic scholarly relationships. One gap: تذييل/تكملة (supplement/continuation) — works that continue where another left off. This is rare in the owner's collection and can be approximated by `responds_to` for Stage 1. Consider adding `continuation_of` in Stage 2.

## Q10: Plain text as second format?

**Answer: ✓ Correct.**

**Confidence: HIGH.** Plain text exercises the pure-LLM-inference code path (minimal format-extracted metadata, LLM does all the work) — architecturally critical as the fallback for all formats when extraction fails. Trivial to implement (10 lines). PDF should be the first Stage 2 format — it requires Docling, OCR, and handling of enormous structural variety, adding 3-5 sessions of build work without validating any new core architecture.

---

## Self-Review

**Verified:** Trust scores computed with actual formula. Genre coverage checked against all 9 Shamela categories. Muhaqiq/publisher assessments grounded in Islamic scholarship knowledge. Relationship types checked against fixture titles.

**Revised:** Initially kept DKI at 0.55; changed to removal (0.40) after applying conservative-bias principle. Initially considered 4 additional muhaqiqs; narrowed to 2 after evaluating "universally recognized" threshold.

**Flagged:** Q6/Q7 are most subjective — configurable lists make disagreements easy to resolve. Q9 تذييل gap is non-blocking but should be tracked for Stage 2.
