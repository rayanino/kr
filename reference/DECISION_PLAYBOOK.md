# Decision Playbook — كتاب القرارات

**Purpose:** Institutional memory for domain decisions. Every pattern,
heuristic, and anti-pattern discovered during the source engine build.

**Audience:** Oracle agent (`claude -p --effort max`), new Claude Chat
sessions, researcher agents verifying knowledge output.

**Format:** Trigger→action pairs. NOT narrative prose. Each section is
a decision type with explicit rules, anti-patterns with examples, and
source citations.

**Authority:** This document captures LEARNED knowledge — verified
through web research and evaluation of 204+ books. It is not the SPEC
(which governs implementation) but the evaluator's reference (which
governs judgment calls).

---

## §1. Author Attribution

### 1.1 Trigger→Action Rules

**IF** author_raw is EMPTY but muhaqiq_name_raw is present
**AND** the muhaqiq appears to be the functional author (not just an editor)
**THEN** the LLMs may correctly identify the muhaqiq as the author.
This is correct behavior. Examples: صحيح سنن النسائي (الألباني listed
as muhaqiq but is the functional author of the hadith verification
work), الأحاديث التي سقطت من المعجم الأوسط (سعد الحميد listed as
muhaqiq but is the author of the academic study).

**IF** author_raw lists classical scholars but muhaqiq_name_raw
contains a contemporary name
**AND** the book title suggests a modern reorganization or compilation
(keywords: ترتيب, تنظيم, تصنيف on a classical source)
**THEN** suspect the compiler-as-muhaqiq pattern (ERR-02). The
contemporary person may be the actual author of a derived work, not
just an editor. Example: السراج المنير lists السيوطي and الألباني as
authors, but عصام موسى هادي (muhaqiq field) is the actual compiler.
**Action:** FLAG. The pipeline has no "compiler" role concept.

**IF** both models identify the same person but the consensus module
reports disagreement
**THEN** check the author_identification objects in llm_responses/.
In 13/14 Phase D consensus disagreements, both models identified the
same person — they just described scholarly standing, methodological
stance, or name form differently. This is a cosmetic disagreement,
not a factual one.
**Action:** Compare the canonical_name_ar fields. If they refer to
the same historical person, the disagreement is cosmetic. VERIFIED
(or PLAUSIBLE if only Shamela sources found).

**IF** the title contains "رواية X" (narration of X)
**THEN** X is typically the narrator/compiler, not the originator of
the hadiths. Example: "من أحاديث سفيان الثوري - رواية السري بن يحيى"
→ السري بن يحيى is the narrator/compiler. سفيان الثوري is the
original source of the hadiths.
**Action:** Verify pipeline identifies the narrator as the author.

**IF** the book is an institutional compilation (ministry, university,
encyclopedia committee)
**THEN** author is the institution, not an individual. No death date.
Example: الموسوعة الفقهية الكويتية → وزارة الأوقاف والشئون الإسلامية.
Trust may be mechanically flagged (no death date reduces score) but
the work is high-quality.

**IF** the book has dual authors (title mentions two scholars)
**THEN** the pipeline only supports single-author attribution.
Example: فوائد ابن الصلت وأبي أحمد الفرضي — both are co-authors.
Pipeline picks one. PLAUSIBLE (partial attribution), not FLAG.

### 1.2 Anti-Patterns

**DO NOT** accept author confidence from result.json.
**WHY:** result.json author.confidence is always 1.0 (known bug — BUG-02).
Real confidence lives in llm_responses/ → author_identification_confidence.
**VERIFIED BY:** Every Phase C and Phase D evaluation session.

**DO NOT** compare scholar canonical IDs across books.
**WHY:** Each book runs in an isolated temporary library. sch_00001 in
book A ≠ sch_00001 in book B. Compare by name_arabic, not by ID.
**VERIFIED BY:** Phase D pattern analysis §3c.

**DO NOT** assume a well-known scholar's attribution is correct
without checking THIS specific title.
**WHY:** Famous scholars wrote many works. A title attributed to
"ابن تيمية" could be: genuinely his, misattributed to him (common
for controversial topics), or a modern compilation of his opinions
organized by someone else (compiler-as-muhaqiq pattern).
**VERIFIED BY:** ERR-02 (السراج المنير attributed to السيوطي when
compiler was عصام موسى هادي).

---

## §2. Death Dates

### 2.1 Source Classification

Every death date must be labeled with its source. Three categories:

**Pass-through:** A structured extraction field (author_death_hijri)
contains the date. Highest reliability — it came from Shamela's
metadata card.

**Extracted from raw text:** No structured field, but the date is
embedded in author_raw as a parenthetical. Examples: "(691 - 751)"
for ابن القيم, "ت 324هـ" for الأشعري, "[ت 1427 هـ]" for المباركفوري.
High reliability — human-written metadata, just not in a structured
field.

**Inferred:** No extraction data at all. The LLM supplied the date
from domain knowledge. VARIABLE reliability — correct for famous
scholars, hallucination-prone for modern/obscure scholars.

### 2.2 Trigger→Action Rules

**IF** death_date_source = "inferred" AND only one model provides the date
**THEN** high risk for hallucination. The pipeline adds
SRC_DEATH_DATE_UNVERIFIED to needs_review_fields.
**Action:** Web search to verify. Known Opus hallucinations: القحطاني
(+3 years, 1443→correct 1440), وافي (+6 years, 1418→correct 1412),
مطلوب (+2 years, 1441→correct 1439). All modern scholars.

**IF** CA provides a specific death date AND extraction contains an
approximate century designation ("ت ق 4هـ", "ت ق 6هـ")
**THEN** CA may have fabricated a specific year from the century.
Example: "ت ق 4هـ" (4th century = 301-400) → CA says 400 AH.
"ت ق 6هـ" (6th century = 501-600) → CA says 460 AH (wrong century!).
**Action:** FLAG if the specific date doesn't match the century range.

**IF** both models disagree on death date AND the book has multiple
author candidates
**THEN** each model may have picked a different author. Example:
السراج المنير — Opus picked السيوطي (d. 911), CA picked الألباني
(d. 1420). The disagreement was about identity, not dates.
**Action:** This is ERR-02 (author misattribution), not a death
date error. Investigate author attribution first.

**IF** the author is contemporary (no death date expected)
**THEN** death date should be absent (None). Confirm both models
agree on None or one appropriately abstains.
**Action:** If one model supplies a date for a living author, FLAG
as hallucination.

### 2.3 Anti-Patterns

**DO NOT** label every death date as "pass-through" without checking.
**WHY:** Phase D Session A Round 4 found 3 books where "pass-through"
was wrong — ابن القيم's date was embedded in raw text (not a
structured field), and تكملة حاشية ابن عابدين had a completely
inferred date (author_raw was EMPTY).
**FIX:** For each death date, check: (1) is there a structured
author_death_hijri field? If yes → pass-through. (2) Is the date
embedded in author_raw text? If yes → extracted from raw text.
(3) Neither? → inferred.

---

## §3. Genre Classification

### 3.1 Genre Definitions (Boundary-Sensitive)

These genres cause the most confusion. The definitions here are the
SPEC-authoritative meanings:

**risalah** — A focused treatise on a specific topic. Typically short.
Single-author, standalone. Example: أحكام الاضطباع والرمل في الطواف.

**matn** — A foundational reference text designed to be memorized or
commented upon. Generates commentaries. Example: المفصل في صنعة الإعراب
(الزمخشري). الأربعون النووية. ألفية ابن مالك.

**other** — Catch-all for works that don't fit any specific genre.
Should be RARE after genre enum expansion. If a book gets "other,"
check whether the LLM proposed a genre not in the enum.

**sharh** — Commentary on another scholar's text. REQUIRES multi-layer
structure (matn + sharh). Example: الروضة الندية شرح الدرر البهية.

**hashiyah** — Marginal commentary on a sharh. REQUIRES 3 layers
(matn → sharh → hashiyah). Example: تكملة حاشية ابن عابدين
(تنوير الأبصار → الدر المختار → رد المحتار).

**rihlah** — Travel literature. Example: ملء العيبة (رحلة ابن رشيد).

**usul_al_fiqh** — Islamic legal theory/methodology. Example:
إعلام الموقعين عن رب العالمين (ابن القيم).

### 3.2 Trigger→Action Rules

**IF** genre = "other" AND the LLM response proposed a genre not
in the enum
**THEN** this is the missing-enum-value bug, not a genuine "other."
Check llm_responses/ for the original genre value.
**VERIFIED BY:** Fix 1 (ERR-01) — ملء العيبة was rihlah but fell
back to "other" because rihlah wasn't in the Genre enum.

**IF** genre ∈ {sharh, hashiyah} AND is_multi_layer = False
**THEN** internal contradiction. Sharh/hashiyah structurally require
layers. Check 5e fires as warning (sharh) or gate (hashiyah).
Example: النكت على شرح النووي — genre=hashiyah, ML=false, 0 layers.
**Action:** The genre or the ML classification is wrong. Web search
to determine the actual structure.

**IF** two models disagree on the risalah/matn/other boundary
**THEN** this is the most common genre disagreement (14/39 in
Phase D). It has ZERO downstream impact — none of these genres
trigger structural processing differences.
**Action:** PLAUSIBLE. Note the disagreement but do not FLAG.

**IF** the same work has different genres across editions
**THEN** this is a known limitation of per-edition processing.
Example: إعلام الموقعين has genre=matn (ط عطاءات), genre=other
(ت مشهور), genre=other (ط العلمية) — three editions, three genres.
**Action:** Note the inconsistency. The normalization engine's
work deduplication will reconcile this.

**IF** Opus and CA disagree on genre AND CA has higher confidence
**THEN** the pipeline may still choose Opus's answer (Opus is
canonical ~90% of the time due to author identification strength).
Example: إعلام الموقعين — CA had usul_al_fiqh (0.95), Opus had
other (0.75). Pipeline chose Opus's wrong answer.
**Action:** Check whether the genre consensus resolution chose
correctly. If wrong, FLAG.

**IF** genre = "tafsir" AND ML = false
**THEN** this is NOT automatically an error. Standalone tafsirs
(one author commenting directly on the Quran) correctly have
ML=false. ML=true for tafsir only when the work is a commentary
on ANOTHER SCHOLAR'S tafsir.
Example: تفسير ابن كمال باشا — standalone tafsir, ML=false correct.

### 3.3 Anti-Patterns

**DO NOT** flag every risalah/matn/other disagreement.
**WHY:** Zero downstream impact. These genres don't trigger different
processing. The distinction is aesthetic, not functional.
**VERIFIED BY:** Phase D pattern analysis §1a — 14 such disagreements,
all classified as "PROMPT BOUNDARY ISSUE, NOT ENGINE BUG."

**DO NOT** accept genre=hashiyah without verifying 3 layers.
**WHY:** Hashiyah structurally requires matn → sharh → hashiyah.
**VERIFIED BY:** ERR-01 (النكت — hashiyah + 0 layers).

---

## §4. Multi-Layer Detection

### 4.1 Trigger→Action Rules

**IF** Opus says ML=true AND the only non-matn layer is tahqiq_note
**THEN** this is the Opus tahqiq-note bias (BUG-03). The pipeline's
override correctly sets ML=false.
**VERIFIED BY:** 12/12 Phase D cases, plus الأدب المفرد, الرسالة
للشافعي, مسند أحمد, السراج المنير, مختصر صحيح مسلم, and القسم
الثالث من المعجم الأوسط.
**Action:** VERIFIED (override working correctly).

**IF** Opus says ML=true AND there is a genuine scholarly layer
alongside tahqiq_note (e.g., matn + sharh + tahqiq_note)
**THEN** ML=true is correct. The tahqiq_note layer is alongside real
scholarly layers. The override does NOT fire (correctly — it only
fires when tahqiq_note is the SOLE non-matn layer).
**VERIFIED BY:** شرح العقيدة الطحاوية, شرح الورقات, فتح الباري,
همع الهوامع.

**IF** both models agree ML=true AND layers include genuine matn/sharh
**THEN** verify the layers are REAL scholarly layers, not just:
- Tahqiq notes misclassified as sharh
- Section headings misclassified as a separate layer
- Publisher introductions misclassified as a layer
**Action:** Check the text_layers array. Each layer should have a
distinct historical author. If layers share the same author, suspect
misclassification.

**IF** the title contains "على" (on/upon) connecting two scholars
**THEN** likely multi-layer. "شرح ابن عقيل على ألفية ابن مالك" →
matn (ابن مالك) + sharh (ابن عقيل).
Similarly, "حاشية X على شرح Y على Z" → 3 layers.

**IF** the title contains "تعليق" or "نكت" or "تعقبات"
**THEN** genre/ML is ambiguous. These can be:
- A multi-layer text where the annotations are interleaved with
  the original → ML=true
- A standalone list of corrections/notes → ML=false
**Action:** PLAUSIBLE or FLAG depending on whether the Shamela text
embeds the original work.

### 4.2 Definitions

**Tahqiq notes (تحقيق):** Editorial apparatus — footnotes, variant
readings, manuscript authentication, biographical lookups. Added by a
modern editor (muhaqiq). NOT a scholarly commentary layer. Does NOT
make a text multi-layer.

**Sharh (شرح):** Scholarly commentary where the commentator explains,
analyzes, or expands on the base text. IS a scholarly layer. Makes the
text multi-layer.

**Hashiyah (حاشية):** Marginal commentary on a sharh. The hashiyah
author comments on the commentator's explanation of the base text.
Requires 3 layers.

### 4.3 Anti-Patterns

**DO NOT** say "ML correct" when tahqiq notes are the only basis.
**WHY:** Tahqiq notes are editorial apparatus, not scholarly layers.
**VERIFIED BY:** BUG-03 — Opus systematically misclassifies tahqiq as
scholarly layers. 12 confirmed cases.

**DO NOT** assert that muhaqiq presence causes the ML bias.
**WHY:** الأذكار has muhaqiq (الأرنؤوط) but Opus correctly says
ML=false. Muhaqiq correlates with the bias but is not sufficient.
The differentiating mechanism is unknown.
**VERIFIED BY:** Evaluation Quick Reference error examples.

---

## §5. Trust Evaluation

### 5.1 Trigger→Action Rules

**IF** trust_tier = "flagged" AND the book is a famous classical work
**THEN** the flagging is likely mechanical — caused by missing
metadata fields in the extraction (no muhaqiq, no death date, no
publisher), not by genuine quality concerns.
**Action:** PLAUSIBLE. Note the mechanical cause. The trust formula
is correct; the extraction data is sparse.

**IF** trust_score clusters at exactly 0.4325
**THEN** this is the score for modern works with no death date, no
muhaqiq, and no known publisher. 24 books shared this exact score
in Phase D. Correct behavior, not a bug.

**IF** trust_tier = "flagged" for an institutional work (encyclopedia,
ministry publication)
**THEN** mechanical flagging. Institutional authors have no death date,
which reduces trust score. But the works are often high-quality.
Example: الموسوعة الفقهية الكويتية — trust=flagged, but it's one of
the most authoritative fiqh references.

**IF** attribution_status shows disagreement (definitive vs traditional)
**THEN** the pipeline resolves to "traditional" per SPEC §6.3. This
is correct and intentional — 47/47 cases in Phase D resolved
correctly. Both values are defensible for well-known classical works.
NOT a quality issue.

### 5.2 Anti-Patterns

**DO NOT** write "trust=flagged is correct per SPEC rules" without
tracing the mechanism.
**WHY:** The trust formula is a 5-factor weighted calculation. The
specific factors that caused flagging matter for the verdict.
**FIX:** State which factor(s) caused the flagging: missing death
date? Missing muhaqiq? Unknown publisher? Low confidence?

---

## §6. Verification Sources

### 6.1 Source Hierarchy (reliability order)

1. **ar.wikipedia.org** — Most reliable for well-known classical
   works and major scholars. Usually has death dates, school
   affiliations, and major work listings. Independently maintained.

2. **archive.org** — Independent. Full text often available. Good
   for confirming authorship and edition details. Sometimes blocked
   by robots.txt.

3. **islamway.net** — Independent. Author and death date
   confirmations. Moderate reliability.

4. **alukah.net** — Independent. Scholarly articles, sometimes
   detailed attribution analysis.

5. **tarajm.com** — Independent biographical database. Good for
   obscure scholars. Often cites classical biographical sources
   (الذهبي, ابن حجر, etc.).

6. **noor-book.com** — Semi-independent. Book catalog with author
   data.

7. **shamela.ws** — Shamela ecosystem. Same data source as the input.
   USE CAUTIOUSLY for genre and metadata verification (circular).
   Useful for confirming author names and finding related works.

8. **ketabonline.com, turath.io, waqfeya.net** — All part of the
   Shamela ecosystem. Count collectively as ONE source with shamela.ws.

### 6.2 Independence Rules

**VERIFIED threshold:** 2+ genuinely independent sources.

**Shamela ecosystem counts as ONE source.** shamela.ws + ketabonline.com
+ turath.io + waqfeya.net = 1 collective source. Need at least 1 more
independent source for VERIFIED.

**Publisher sites are independent** if they are the publisher's own
website (not a reseller). Example: bohoth.awqaf.gov.kw (official
Kuwaiti government site) is independent.

**Academic catalogs are independent.** University library catalogs,
JSTOR references, Google Scholar citations.

**Google Books listings are semi-independent.** The listing itself
confirms the book exists with that title and author. The metadata
comes from publishers but is independently hosted.

### 6.3 Trigger→Action Rules

**IF** only Shamela-ecosystem sources confirm the attribution
**THEN** PLAUSIBLE (not VERIFIED). Even if 4 Shamela sites all agree,
they are one collective source.

**IF** the book is universally famous (البخاري, مسلم, القرآن الكريم)
**THEN** VERIFIED without extensive search. State the obvious:
"universally known, no further sourcing needed." Reserve research
time for obscure works.

**IF** web_search finds results but web_fetch returns 403/blocked
**THEN** search snippets may provide enough information for PLAUSIBLE.
For VERIFIED, at least one source must be fetched successfully to
confirm content matches snippet claims.

### 6.4 Anti-Patterns

**DO NOT** count Shamela-ecosystem as multiple independent sources.
**WHY:** Phase C Correction 5. All Shamela-derivative sites share
the same data provenance.

**DO NOT** cite sources you did not actually search for or fetch.
**WHY:** Phase D Session A Round 3 found a protocol violation where
sources like archive.org were cited without any web_search call.
Retroactive checking revealed 2 false citations.

**DO NOT** rely on search snippets alone for VERIFIED verdicts.
**WHY:** Snippets can be misleading. Phase D Session A showed that
web_fetch revealed information contradicting the snippet's implication
in 1 of 14 books (Book 10 downgraded from VERIFIED to PLAUSIBLE).

---

## §7. Arabic Text Handling

### 7.1 Rules

**NFC normalization only.** Never NFD, never NFKC. NFC is the composed
form — combining characters into precomposed codepoints. This preserves
diacritics while standardizing representation.

**Arabic comma (،) in name matching.** LLM-generated nasab names
include Arabic commas: "الزجاجي، أبو القاسم". The extraction may not.
Name matching must be punctuation-insensitive.
**VERIFIED BY:** Source engine Phase A — name matching bug fixed.

**Ya/alef maqsura (ي vs ى).** These are different characters but
frequently interchanged in Arabic digital texts. Field stability
across reruns showed ي/ى variation: لسان العرب had "الرويفعي" in
Phase C → "الرويفعى" in Phase D. This is cosmetic, not an error.
**Action:** Treat ي/ى variation as cosmetic. Do not FLAG.

**Diacritics alter meaning.** حَرَّمَ (prohibited) vs حَرَمَ (deprived).
A normalization bug that strips diacritics destroys legal distinctions.
Primary text is NEVER modified after extraction.

**Century designations ("ت ق Xهـ").** These appear in author_raw and
mean "died in the Xth century AH." They are approximate — not a
specific year. Example: "ت ق 6هـ" = died sometime between 501 and
600 AH.

### 7.2 Anti-Patterns

**DO NOT** apply any string transformation to primary Arabic text.
**WHY:** Even "whitespace normalization" can remove meaningful spaces
in classical Arabic typesetting.

**DO NOT** treat ي and ى as errors in author names.
**WHY:** Both are conventional in different regional traditions. Phase D
field stability analysis confirmed this is cosmetic variation.

---

## §8. Evaluation Methodology

### 8.1 Verdict Definitions (Strict)

Only these 5 verdicts exist. No variations, no combinations.

| Verdict | Meaning | Requires |
|---------|---------|----------|
| VERIFIED | Confirmed correct | 2+ independent web sources |
| PLAUSIBLE | Likely correct, no red flags | 1 source OR consistent extraction cross-check |
| UNVERIFIABLE | Cannot confirm or deny | No sources found, output looks reasonable |
| FLAG | Probably wrong | Evidence of error documented |
| ESCALATE | Cannot resolve | Beyond evaluator's ability, needs owner |

### 8.2 Trigger→Action Rules

**IF** the book is universally famous AND both models agree on all
key fields AND extraction cross-checks are consistent
**THEN** VERIFIED. Minimal search needed. Example: الأربعون النووية,
الأدب المفرد, الرسالة للشافعي.

**IF** author confidence < 0.50 (from llm_responses/, not result.json)
**THEN** author verdict should be PLAUSIBLE at best, FLAG if
contradicting evidence found.

**IF** you find an error during evaluation AND the error is in the
random calibration sample
**THEN** the protocol says "expand sample." Whether to actually expand
depends on the error type: secondary field errors (death date) do not
block GO, core field errors (author, genre) require expansion.

**IF** a book was VERIFIED in Phase C AND it was re-run in Phase D
with the same result
**THEN** ACCEPT. No need to re-evaluate. Regression check is
sufficient.

### 8.3 Anti-Patterns

**DO NOT** invent verdict categories.
**WHY:** "VERIFIED with FLAG" or "MOSTLY VERIFIED" are not valid.
Each field can have its own sub-verdict, but the overall must be
one of the 5.

**DO NOT** accept field values without checking which model produced them.
**WHY:** For success books, result.json carries the winning model's
values. If Opus is canonical, result.json has Opus's values. If CA
won a specific field, result.json has CA's value for that field.
Reading result.json genre and assuming it came from Opus is an error.

**DO NOT** skip web_fetch and rely only on search snippets.
**WHY:** Search snippets truncate and can mislead. At least 1
web_fetch per book is required by protocol. Phase D Session A found
this violation in Round 3 self-review.

---

## §9. Consensus Module Behavior

### 9.1 What the Consensus Module Actually Checks

The consensus module compares the author_identification objects between
models. It does NOT check genre, ML, or science_scope agreement.

**Consequence:** Genre and ML errors pass through the consensus check
silently. BUG-03 override provides a safety net for ML. There is NO
corresponding safety net for genre misclassification.

### 9.2 Trigger→Action Rules

**IF** consensus.agreed = True
**THEN** the author_identification objects matched. Genre, ML, and
science_scope may still disagree — check llm_responses/ manually.

**IF** consensus.agreed = False AND both models identify the same
person (same canonical_name_ar, same death date)
**THEN** cosmetic disagreement. 13/14 Phase D cases. The models
described the same person differently.
**Action:** Not a quality concern.

**IF** canonical_model = "unknown" in consensus.json
**THEN** this is WARN-04 (recording bug, 190/204 books in Phase D).
Does not affect output correctness — the canonical model selection
still happened, just wasn't recorded.

**IF** pipeline genre matches neither model's genre
**THEN** this is the ملء العيبة consensus module bug. The consensus
module produced a genre that was not proposed by either model.
**Action:** FLAG. Investigate at code level.

### 9.3 Opus Canonical Concentration

Opus is canonical ~90% of the time (based on field comparison in
Phase D). This means any undetected Opus systematic bias affects most
of the library.

**Known mitigated biases:** Tahqiq-note ML bias (BUG-03 override).
**Monitored:** Death date hallucination (ERR-03 warning).
**Unmonitored risk:** Any other systematic Opus tendency.

---

## §10. Known Patterns and Edge Cases

### 10.1 The "من أحاديث X - رواية Y" Pattern
Small hadith manuscripts where Y narrated hadiths from X. The author
is Y (the narrator), not X (the original source). Title structure is
the key indicator.

### 10.2 The "المتأخر" (the Later One) Pattern
When a title includes "المتأخر," it distinguishes a scholar from an
earlier family member with the same name. Example: ابن العربي المتأخر
(d. 617 AH, grandson) vs القاضي ابن العربي (d. 543 AH, grandfather).

### 10.3 The Pseudonymous Author Pattern
Authors using كنية (pen names) like أبو عبد الله المصري are
deliberately unidentifiable. Pipeline correctly assigns low confidence
(0.30). Trust=flagged. Attribution=traditional. ESCALATE to owner.

### 10.4 The "آثار" (Collected Works) Pattern
Books published as part of a scholar's collected works (آثار X) are
correctly attributed to X. The individual piece may be short (a single
fatwa, a grammatical analysis). Genre varies by content, not by
collection format.

### 10.5 The Edition Group Pattern
The same work in different editions can get different genre labels
because LLMs respond to edition-specific signals (tahqiq quality,
introduction content, publication framing). This is a known limitation,
not a bug. Normalization engine's work deduplication will reconcile.

### 10.6 The Level Field Pattern
Both models consistently underestimate scholarly level for modern
academic works (classifying "intermediate" as "beginner"). 31/32
confidence outliers in Phase D had low confidence on the level field.
This is a prompt calibration issue, not an engine bug.

### 10.7 The Disputed Attribution Pattern
Some classical works have genuinely disputed authorship. Example:
الإبانة عن أصول الديانة — attributed to الأشعري by the majority of
classical scholars, but modern scholars debate whether the surviving
text has been altered. Both "disputed" and "definitive" are correct
depending on perspective. The SPEC resolves to the more conservative
value.

---

## §11. Source Engine Specific Knowledge

These items are specific to the source engine's implementation and
data characteristics. They may not apply to other engines.

### 11.1 Shamela HTML Formats
Two formats exist in the extraction:
- **Format A (standard):** `<span class='title'>LABEL<font>:</font></span> VALUE`
- **Format B (variant):** Value inside the span tag, colon embedded in label
The extractor handles both after Phase A bug fixes.

### 11.2 Field Coverage in Shamela Exports
- title_full: 100% (after Phase A fixes)
- author_name_raw: 96.2%
- muhaqiq_name_raw: 53.6% (roughly half have editorial attribution)
- author_death_hijri: 67.8%
- publisher: 88.1%

### 11.3 Budget Reference
- Cost per book (full pipeline): ~€0.10
- Phase A (deterministic only): €0
- Phase C (73 books): €7.00
- Phase D (204 books): €20.40
- Total source engine: €30.60 of €100 budget

### 11.4 The Gate Abort Pattern
gate_abort means validation flagged an issue AFTER inference completed.
All LLM data is preserved and reusable. gate_abort books are NOT
re-processed on resume (they already have complete inference data).
Phase C: 51/73 gate_abort (70%) — caused by sparse scholar registry.
Phase D: 0/204 gate_abort (0%) — after registry enrichment.

---

## §12. When to ESCALATE

Use ESCALATE only when the evaluator genuinely cannot resolve the
question. It is not a hedge for uncertainty — that's what PLAUSIBLE
and UNVERIFIABLE are for.

**Escalate when:**
- The question requires inspecting the actual Shamela HTML file
  (evaluator cannot read Arabic book content in chat)
- The author is pseudonymous and no web source reveals identity
- The genre/ML question depends on the internal structure of the
  Shamela export (interleaved text vs standalone annotations)
- The domain question exceeds what web search can resolve

**Do NOT escalate when:**
- You're unsure but the pipeline output looks reasonable → PLAUSIBLE
- You can't find sources → UNVERIFIABLE
- The pipeline output contradicts web sources → FLAG

---

## Appendix: Error Registry

Errors confirmed during the source engine build. Reference for
pattern recognition.

| ID | Type | Book | Description | Fix |
|----|------|------|-------------|-----|
| ERR-01 | Validation gap | النكت على شرح النووي | hashiyah + ML=false contradiction not caught | Added gate-severity check for hashiyah+no-layers |
| ERR-02 | Author misattribution | السراج المنير | Compiler (عصام موسى هادي) in muhaqiq field, classical authors in author field | Documented as known limitation (compiler pattern) |
| ERR-03 | Death date hallucination | القحطاني, وافي, مطلوب | Opus inferred dates 2-6 years off for modern scholars | Added SRC_DEATH_DATE_UNVERIFIED warning for single-model death dates |
| BUG-01 | Gate abort rate | 51/73 books | Sparse scholar registry caused 70% gate_abort | Populated science_scope for major scholars |
| BUG-02 | Confidence bug | All books | author.confidence in result.json always 1.0 | Known, documented. Read from llm_responses/ instead |
| BUG-03 | ML bias | 12 books | Opus classifies tahqiq notes as scholarly layers | Override: tahqiq_note as sole non-matn layer → ML=false |
| BUG-C01 | Edition groups | 9 groups | Edition group names mismatched directory names | Fixed name matching in compute_edition_groups() |
| BUG-C02 | Data loss | 51 books | Edition groups excluded gate_abort books | Fixed to include gate_abort books with data from llm_responses/ |
| Fix-1 | Missing enum | ملء العيبة + others | rihlah and usul_al_fiqh not in Genre enum | Added to enum, prompt, and synonym table |
