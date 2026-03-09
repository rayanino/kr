# Owner Sanity Check — Answers from Empirical Analysis + Domain Reasoning

**Date:** 2026-03-09
**Method:** Structural survey of 2,519 real Shamela exports, trust formula computation on 7 test cases, Islamic scholarship domain analysis, multi-angle evaluation per thinking-frameworks skill
**Confidence calibration:** Each answer rated HIGH / MODERATE / LOW with reasoning

---

## Q1–Q3: Shamela HTML Structure → ANSWERED EMPIRICALLY

See `reference/SHAMELA_FORMAT_ANALYSIS.md`. The survey of all 2,519 books answered these definitively. Every extraction rule in the original SPEC was wrong and has been rewritten.

---

## Q4: Does the genre list cover your library?

**Answer: ✓ Adequate. No changes needed for Stage 1.**

**Confidence: HIGH**

The 18 genres (matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, mawsuah, fatawa, mujam, tabaqat, fiqh_comparative, hadith_collection, tafsir, sirah, tarikh, adab, other) were checked against the 9 Shamela categories in the collection and the title patterns of 1,932 single-file books.

The mapping works as follows. Every Shamela category maps to one or more genres:
- كتب السنة (1,015 books) → `hadith_collection` for the major collections, `sharh` for hadith commentaries, `risalah` for topical hadith monographs, `tabaqat` for rijal works
- التفسير (122) → `tafsir`, or `sharh` when it's a commentary on another tafsir
- النحو والصرف (145) → `matn`, `sharh`, `hashiyah`, `nazm` depending on the specific work
- الفقه العام (141) → `matn`, `sharh`, `mukhtasar`, `fiqh_comparative`, `risalah`
- كتب عامة (330) → distributed across `risalah`, `tarikh`, `adab`, `other`
- كتب اللغة (71) → `mujam` for dictionaries, `matn`/`sharh` for grammar treatises
- أصول الفقه (39) → `matn`, `sharh`, `risalah`
- البلاغة (30) → `matn`, `sharh`, `risalah`
- الفتاوى (39) → `fatawa`

I searched for genre gaps — common scholarly work types that don't map to any of the 18 genres. The candidates I considered:

**خطب (sermons/khutab):** Present in the collection but rare. Maps to `risalah` or `other` without loss. Not common enough to warrant its own genre.

**تخريج (hadith source-tracing):** Works like "تخريج أحاديث الإحياء" that trace hadith sources. Structurally distinct from sharh — they authenticate rather than explain. But functionally they're reference works that don't affect downstream processing differently from `other`. Stage 2 candidate at most.

**تعقبات (scholarly corrections/objections):** One of the fixtures (أنوار الهلالين في التعقبات على الجلالين) is exactly this type. These are point-by-point critiques of another work. They map to `risalah` with a `responds_to` relationship to the target work. The genre doesn't need to be separate because the relationship type captures the scholarly function.

**مذكرات (memoirs/intellectual diaries):** The fixture مذكرات مالك بن نبي is this type. Maps to `other`. Rare in classical Islamic scholarship.

**Why no changes are needed:** The `other` catch-all exists precisely for edge cases. More importantly, the genre affects downstream processing only through a few specific channels: the synthesis engine uses genre for narrative framing, the normalization engine uses `structural_format` (not genre) for processing strategy, and the passaging engine uses `structural_format`. Adding more genres would increase classification complexity without changing how any engine processes the text.

---

## Q5: Is "commentary" the right structural_format for a sharh?

**Answer: ✓ "commentary" is correct.**

**Confidence: HIGH**

A sharh like شرح ابن عقيل interleaves quoted matn text (ألفية verses) with the sharh author's explanatory prose. This alternating structure — reference text followed by explanation — is the defining characteristic of the `commentary` structural format. The normalization and passaging engines need this classification to:

1. **Normalization:** Detect text layer boundaries (where does matn end and sharh begin within a page). With `commentary`, the normalizer knows to look for layer transitions.
2. **Passaging:** Use commentary-aware splitting that keeps matn + its explanation together in the same passage, rather than splitting mid-explanation.

The alternatives don't fit:
- `prose` would be correct for a standalone work, but a sharh has internal structure (reference + explanation) that prose splitting would not respect.
- `mixed` implies sections in fundamentally different formats (e.g., some prose, some tabular). A sharh is uniformly commentary throughout.
- `verse` only applies to works that are entirely versified (like the Alfiyyah itself).

One nuance: some shuruh have long muqaddimas (introductions) in plain prose before the commentary begins. The structural_format should still be `commentary` because the dominant structure is commentary. The normalization engine handles the muqaddima as an introductory section before the commentary structure begins.

---

## Q6: Do you recognize these muhaqiqs as trusted editors?

**Answer: ✓ The list is sound. Two additions recommended.**

**Confidence: MODERATE** (the core list is solid; the additions are judgment calls)

Each muhaqiq on the current list is genuinely recognized as a trusted editor in Islamic scholarship:

| Muhaqiq | Specialty | Verdict |
|---------|-----------|---------|
| شعيب الأرناؤوط | Hadith (Musnad Ahmad, Sahih Ibn Hibban, many others) | ✓ Indisputable |
| أحمد شاكر | Hadith + Arabic literature (Musnad Ahmad, Tirmidhi) | ✓ Indisputable |
| عبد السلام هارون | Classical Arabic (al-Kitab of Sibawayhi, al-Muqtadab) | ✓ Indisputable |
| عبد الله التركي | Hanbali fiqh (al-Mughni, many Hanbali texts) | ✓ Indisputable |
| محمد فؤاد عبد الباقي | Hadith (standard Sahih Muslim edition, Ibn Majah) | ✓ Indisputable |
| عبد القادر الأرناؤوط | Hadith (various collections) | ✓ Recognized |
| محمد ناصر الدين الألباني | Hadith grading (the most widely-used hadith authentication) | ✓ Indisputable |
| محمد محيي الدين عبد الحميد | Nahw (Ibn Aqil, Awdah al-Masalik, Qatr al-Nada) | ✓ Indisputable |

**Recommended additions:**

**عبد الرحمن بن يحيى المعلمي اليماني** — One of the most rigorous muhaqiqs of the 20th century. His methodology in critical editing (especially al-Fawa'id al-Majmu'ah, al-Tankil) set the standard for modern tahqiq. His omission from the list is the most notable gap.

**بشار عواد معروف** — Edited the Risalah edition of Sunan al-Tirmidhi (widely considered the best modern edition), Tarikh Baghdad, and many other works. Iraqi scholar with exceptional reputation for thorough critical editing.

Both are as widely recognized as anyone on the current list. The list is stored in a configurable JSON file, so additions are low-risk.

---

## Q7: Do you recognize these publishers as scholarly?

**Answer: ✓ with one removal and three additions.**

**Confidence: MODERATE** (publisher quality is inherently more subjective than muhaqiq quality)

| Publisher | Verdict | Reasoning |
|-----------|---------|-----------|
| دار الرسالة / مؤسسة الرسالة | ✓ Keep | Top-tier. Shuaib al-Arnaout's editions published here. |
| دار التراث | ✓ Keep | Established. Ibn Aqil/Abd al-Hamid edition from here. |
| دار الكتب العلمية | **✗ Remove** | Controversial. DKI Beirut publishes massive quantities of classical texts, but their tahqiq quality is widely criticized as commercial rather than scholarly. Many of their "tahqiq" editions are actually unedited reprints with new covers. Some specific titles are acceptable (when they reprint established tahqiqs), but the publisher as a whole should not confer trust. Recommend: move to neutral (score 0.50) rather than "known scholarly." |
| المكتب الإسلامي | ✓ Keep | Zuhayr al-Shawish. Published Albani's major works. Respected. |
| دار ابن حزم | ✓ Keep | Modern publisher with generally good quality. |
| دار ابن الجوزي | ✓ Keep | Saudi-based. Known for quality hadith editions. |

**Recommended additions:**

| Publisher | Reasoning |
|-----------|-----------|
| مكتبة الرشد | Major Saudi scholarly publisher. Widely used in academic circles. |
| دار طيبة | Known for quality Quran and hadith editions. |
| عالم الكتب | Important reference work publisher. |

The دار الكتب العلمية removal is the strongest recommendation here. This publisher is genuinely controversial among Islamic studies scholars — placing it on the "trusted" list would give verified status to editions that experienced scholars would question. The conservative approach (flagging rather than verifying) is more appropriate.

---

## Q8: Does the trust scoring make sense?

**Answer: ✓ The outcomes are correct across all tested cases.**

**Confidence: HIGH** (computed using the actual formula on 7 test cases)

I ran the exact trust formula on 7 representative cases:

| Case | Score | Tier | Correct? |
|------|-------|------|----------|
| Classical author + recognized muhaqiq + known publisher (Ibn Aqil) | 0.878 | verified | ✓ Exactly right. This is a gold-standard source. |
| Unknown modern + no muhaqiq + unknown publisher | 0.420 | flagged | ✓ Exactly right. Should require human review. |
| Classical author + unknown muhaqiq + unknown publisher | 0.718 | verified | ✓ The author's standing carries the score. A well-known classical scholar's work is trustworthy even without a recognized modern editor — the text has been transmitted through centuries of scholarly tradition. |
| Classical author + NO muhaqiq (pre-modern) + unknown publisher | 0.693 | verified | ✓ Pre-modern works without modern editors are normal and acceptable. The slightly lower score reflects that no modern editor has checked the text, but the threshold is still met. |
| Contemporary scholar + recognized muhaqiq + known publisher | 0.750 | verified | ✓ Good modern edition. The lower author_standing (0.70 vs 0.90 for classical) is compensated by strong tahqiq and publisher. |
| Classical hadith imam + no muhaqiq + commercial publisher | 0.693 | verified | ✓ Borderline but correct. A work by a major hadith imam like al-Bukhari is inherently trustworthy. The commercial publisher lowers the score but doesn't flip the tier. |
| Unknown thesis author + no muhaqiq + no publisher | 0.420 | flagged | ✓ Theses from unknown authors without editorial review should be flagged. |

The scoring produces exactly one potentially uncomfortable outcome: a classical work from an unknown publisher with no muhaqiq still gets `verified` (0.693). This is actually correct for Islamic scholarship — pre-modern works that have been transmitted through the scholarly tradition for centuries have an inherent authority that doesn't depend on modern editorial apparatus. The conservative bias kicks in for truly unknown or modern authors where the scholarly tradition hasn't yet vetted the content.

The 0.65 threshold separates the cases correctly. No case that should intuitively be verified ends up flagged, and no case that should be flagged ends up verified.

---

## Q9: Are the 7 relationship types complete?

**Answer: ✓ Adequate for Stage 1. One gap noted for Stage 2.**

**Confidence: MODERATE**

The 7 types (sharh_of, hashiyah_on, mukhtasar_of, nazm_of, taqrirat_on, responds_to, cites) cover the standard Islamic scholarly genre relationships. I checked each against the owner's collection:

- **sharh_of:** Very common. شرح ابن عقيل على ألفية ابن مالك, شرح الأشموني على الألفية, etc. ✓
- **hashiyah_on:** Common. حاشية الصبان على شرح الأشموني, حاشية الدسوقي, etc. ✓
- **mukhtasar_of:** Common. مختصر صحيح البخاري, مختصر سنن أبي داود, etc. ✓
- **nazm_of:** Present. ألفية ابن مالك (versification of Tashil al-Fawa'id), المنظومة البيقونية. ✓
- **taqrirat_on:** Less common but present in lecture-based works. ✓
- **responds_to:** Covers refutations and corrections. التعقبات على الجلالين maps here. ✓
- **cites:** Populated by downstream citation discovery. ✓

**One gap worth noting:** **تذييل / تكملة (supplement/continuation)** — works that continue where another work left off. Example: "ذيل طبقات الحنابلة" continues Ibn Rajab's continuation of al-Qadi Abu Ya'la's biographical dictionary. This is a genuine scholarly relationship (work_a continues work_b chronologically) that doesn't map cleanly to any of the 7 types. It's not a sharh (no explanation), not responds_to (no disagreement), not mukhtasar (no abridgment).

However, this relationship type is rare in the owner's collection (no fixtures exhibit it), and it can be approximated by responds_to with a note in the relationship metadata for Stage 1. A proper `supplement_of` or `continuation_of` type should be considered for Stage 2.

The `cites` type handles the remaining ad-hoc relationships discovered during text processing.

---

## Q10: Is plain text useful as the second core format?

**Answer: ✓ Plain text is correct for Stage 1. PDF should be the first Stage 2 format.**

**Confidence: HIGH**

This question has a clear analytical answer that doesn't depend on the owner's preferences. The choice between plain text and PDF as the second core format affects build complexity, architectural coverage, and Stage 1 timeline.

**Why plain text is architecturally valuable:**

Plain text is the "opposite extreme" from Shamela HTML. Shamela provides rich structured metadata (author, title, category, muhaqiq, publisher, edition, page count — all extracted from the metadata card). Plain text provides almost nothing — just a title from the first line and raw text content. This means the plain text pathway exercises the **pure LLM inference** code path: the LLM must identify the author, genre, science, and everything else from the text content alone. This code path is critical because it's the fallback for ALL formats when metadata extraction fails. Building and testing it in Stage 1 ensures the LLM inference pipeline is robust before any additional formats are added.

**Why PDF should wait:**

PDF intake requires: a PDF parsing library (Docling), Arabic OCR capability (for scanned PDFs), text extraction logic, and handling of the enormous variety of PDF structures (text-embedded vs. scanned, single-column vs. multi-column, footnotes-as-text vs. footnotes-as-images). This is 3-5 sessions of additional build work. None of this complexity helps validate the core source engine architecture — it's format-specific plumbing.

**The practical test:**

The owner's entire current library is from Shamela. The plain text fixture (alfiyyah_versified — ألفية ابن مالك copy-pasted from a blog) represents a realistic secondary intake path: a student copies text from a website or digital source. The owner CAN use this for any text he wants to ingest quickly. PDFs require actual PDF files, which the owner has but which add no architectural insight beyond what Shamela + plain text already cover.

**Stage 2 priority:** PDF should be the FIRST format added in Stage 2 because the owner has 3 PDF fixtures already (waraqat, ibn_aqil PDF volumes, mughni docs) and PDFs are the most common non-Shamela format for Arabic scholarly texts.

---

## Self-Review Notes

**Verified:**
- Trust scores computed using the actual SPEC formula on 7 cases (not estimated)
- Genre coverage checked against all 9 Shamela categories from the 2,519-book survey
- Muhaqiq reputations verified against established Islamic scholarship knowledge
- Publisher assessments cross-checked (the DKI controversy is well-documented)
- Relationship types checked against fixture titles for coverage

**Revised:**
- Q6: Initially considered adding 4 muhaqiqs, narrowed to 2 (المعلمي and بشار عواد) after evaluating which are truly "indisputably recognized" vs. "respected but not universally known"
- Q7: Initially kept دار الكتب العلمية with a note. Changed to recommend removal after considering the conservative-bias principle: flagging a good DKI edition is correctable, verifying a bad one contaminates the library
- Q8: Added the borderline case analysis (classical + unknown publisher = 0.693 = verified) after realizing this is the case most likely to feel uncomfortable but is actually correct

**Flagged:**
- Q6/Q7: These are the most subjective answers. The owner may have different views on specific muhaqiqs or publishers based on his study circle's conventions. The lists are configurable — disagreements are resolved by editing `library/config/recognized_muhaqiqs.json` and `library/config/known_publishers.json`.
- Q9: The تذييل gap is noted but classified as non-blocking. If the owner knows of a supplement/continuation relationship in his collection, this assessment should be revisited.
