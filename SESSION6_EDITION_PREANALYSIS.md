# Session 6 Edition Group Pre-Analysis

**Created by:** Claude Chat (Architect), Calibration Session
**Purpose:** Pre-researched analysis of all 9 edition groups to accelerate Session 6 evaluation.

---

## Summary

| Group | Editions | Genre | Author | ML | Verdict |
|-------|----------|-------|--------|-----|---------|
| إعلام الموقعين | 3 | ⚠ inconsistent | same person | ✓ | Known ambiguity |
| البداية والنهاية | 2 | ✓ | ✓ | ✓ | Clean |
| شرح العقيدة الطحاوية | 2 | ✓ | same person | ✓ | Clean (name format) |
| تفسير الطبري | 2 | ✓ | ✓ | ✓ | Clean |
| حاشية ابن عابدين | 2 | ✓ | **different people** | ✓ | **GROUPING BUG** |
| تحفة المودود | 2 | ✓ | ✓ | ✓ | Clean |
| الإبانة | 2 | ⚠ inconsistent | same person | ✓ | Known ambiguity |
| فتاوى اللجنة الدائمة | 2 | ✓ | ✓ | ✓ | Clean |
| ألفية ابن مالك | 2 | ✓ | same person | ✓ | Clean (name format) |

**5 clean, 2 known ambiguities, 1 grouping bug, 1 correct non-group.**

---

## Inconsistent Group 1: إعلام الموقعين (3 editions)

### Data

| Edition | Opus genre | CA genre | Consensus |
|---------|-----------|----------|-----------|
| ط عطاءات العلم | matn | usul_al_fiqh | disagreed |
| ت مشهور | other | other | disagreed* |
| ط العلمية | other | matn | agreed** |

*Disagreed on author name format, not genre.
**Agreed on author, but genre differs between models — consensus doesn't check genre.

All 3 editions: author = ابن القيم (ت 751هـ), ML = false ✓, science = usul_al_fiqh + fiqh

### Research

Wikipedia Arabic describes this work as combining fiqh, usul al-fiqh, maqasid al-shariah, tarikh al-tashri', and siyasah shar'iyyah. Islamway classifies it under "الفقه وأصوله". Shamela categorizes it under "أصول الفقه". Ketabonline lists it as usul al-fiqh.

This book genuinely resists single-genre classification. It's a multi-volume encyclopedic work on fatwa methodology, legal reasoning, and judicial procedure — part treatise, part legal reference, part intellectual history. The framework expected "risalah/other" and listed this as a known acceptable ambiguity.

### Verdict for Session 6

**Genre inconsistency is NOT a pipeline bug.** Both "other" and "risalah" are acceptable. "matn" is incorrect — this is not a study text. The framework's classification of "risalah" is the best fit, but "other" (what 2 of 3 editions settled on) is also defensible.

**Author inconsistency is pure name format variation.** All three name the same person (ابن القيم) with different nasab chain lengths. The `normalized_name_similarity` threshold of 0.90 correctly identifies these as "close but not identical" — the consensus system flags them appropriately.

**ML consistency is correct**: all false ✓. This is the framework's #1 critical check for this group.

**Sources:** https://ar.wikipedia.org/wiki/أعلام_الموقعين_عن_رب_العالمين, https://shamela.ws/book/11496, https://ketabonline.com/ar/books/2353, https://ar.islamway.net/book/30812

---

## Inconsistent Group 2: الإبانة (2 editions)

### Data

| Edition | Opus genre | CA genre | Consensus |
|---------|-----------|----------|-----------|
| ت العصيمي | risalah (0.82) | risalah (0.90) | agreed |
| ت فوقية | matn (0.90) | matn (0.95) | agreed |

Both editions: author = الأشعري (ت 324هـ), ML = false ✓, science = aqidah ✓

Interesting: Opus says attribution = "disputed" for both, CA says "definitive" for both.

### Research

الإبانة عن أصول الديانة by أبو الحسن الأشعري is a classical aqidah text. Whether to classify it as "matn" (foundational study text) or "risalah" (treatise) depends on pedagogical vs historical framing:
- As *matn*: it's studied as a foundational text in aqidah, like other mutun
- As *risalah*: it's an authored argumentative treatise, not a study text in the traditional sense

The attribution dispute is real — some scholars (particularly Ash'ari school adherents) have questioned whether the text as we have it accurately represents al-Ash'ari's views, especially the passages that align closely with Hanbali theology. This is a genuine scholarly debate. Opus's "disputed" classification picks up on this. CA's "definitive" reflects the mainstream attribution.

### Verdict for Session 6

**Genre inconsistency is NOT a pipeline bug.** Both "risalah" and "matn" are defensible. Internal consistency within each edition is perfect (both models agree per edition). The editions diverge because the models weight different features: ت العصيمي may have textual cues favoring "risalah", ت فوقية may have cues favoring "matn". Without reading the actual tahqiq notes of each edition, we can't determine which is "more correct" — and the answer is arguably both.

**Author inconsistency is name format variation.** One edition extracted the short form, the other the full nasab chain. Same person.

**Attribution:** Opus's "disputed" is actually the more scholarly answer for this particular text. The Session 5 evaluator should note this when evaluating the editions individually.

---

## Grouping Bug: حاشية ابن عابدين

The algorithm groups these as 2 editions of the same work:
- حاشية ابن عابدين = رد المحتار — by محمد أمين عابدين (father, ت 1252هـ)
- تكملة حاشية ابن عابدين = قرة عيون الأخيار — by محمد علاء الدين عابدين (son, ت ~1306هـ)

**These are NOT the same work.** The تكملة is a continuation written by the son after the father's death. Different author, different text, different scope. The framework explicitly states: "NOT a group: حاشية ابن عابدين vs تكملة — Different authors (father/son)."

The pipeline CORRECTLY identified different authors. The edition grouping algorithm incorrectly merged them because both titles contain "حاشية ابن عابدين". This is a **BUG in compute_edition_groups()** — it should be filed as BUG-C08.

**For Session 6:** Evaluate these as separate works, not as editions. Verify the father/son distinction (محمد أمين vs محمد علاء الدين). The pipeline got this right; only the grouping is wrong.

---

## Clean Groups (quick reference)

### البداية والنهاية (2 editions) ✓
Both: tarikh, ابن كثير (ت 774هـ), ML=false. Fully consistent. Critical check passed: NOT tafsir.

### شرح العقيدة الطحاوية (2 editions) ✓
Both: sharh, ابن أبي العز الحنفي, ML=true. Author "inconsistency" is name format only (one includes صدر الدين laqab, the other doesn't). Same person.

### تفسير الطبري (2 editions) ✓
Both: tafsir, الطبري (ت 310هـ), ML consistent. Fully consistent.

### تحفة المودود (2 editions) ✓
Both: risalah, ابن القيم (ت 751هـ), ML=false. Fully consistent.

### فتاوى اللجنة الدائمة (2 editions) ✓
Both: fatawa, اللجنة الدائمة (institutional, no death date), ML=false. Fully consistent.

### ألفية ابن مالك (2 editions) ✓
Both: nazm, ابن مالك (ت 672هـ), ML=false. Author "inconsistency" is name format only. Same person.

---

## New Bug: BUG-C08

**Edition grouping false positive for حاشية ابن عابدين + تكملة حاشية ابن عابدين.**

Root cause: `compute_edition_groups()` matches on partial title overlap ("حاشية ابن عابدين") without verifying that different-author books can't be editions of each other.

Fix: If the pipeline identifies different authors with different death dates (>50 year gap), they cannot be editions of the same work. Exclude from edition group.

This is LOW priority — the grouping is metadata only, not used in any pipeline decision.
