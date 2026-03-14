# Phase C Evaluation Framework — Autonomous Claude Chat Review

**Purpose:** Enable Claude Chat sessions to evaluate Phase C pipeline results autonomously, with the owner providing input only where Claude genuinely cannot do better.

**Design principle:** Open-ended review ("is this correct?") is the worst review format. It's slow, inconsistent, and the reviewer's confidence creates false certainty. Instead: Claude Chat independently researches expected values, compares against pipeline output, and produces a structured verdict. The owner answers specific targeted questions only when escalated.

**Why minimize owner input:** The owner is an Islamic studies student with deep but imperfect knowledge. His spot-checks can introduce errors — saying "looks right" to 60 books while missing 3 subtle mistakes creates false ground truth that calibrates the pipeline for 2,500 books. Claude Chat with web search is more consistent, more thorough, and documents its reasoning.

---

## Domain Context (evaluation sessions: read this first)

**What is KR (خزانة ريان)?** A personal Islamic scholarly library system with 7 processing engines. The source engine is the entry point — it ingests raw book files, extracts metadata, uses LLMs to classify the book (genre, author, science, multi-layer structure), and produces a metadata record consumed by 6 downstream engines.

**Why accuracy matters:** Metadata errors here cascade. If the pipeline says البداية والنهاية by ابن كثير is genre "tafsir" (wrong — it's tarikh), every downstream engine treats it as tafsir: the normalization engine applies tafsir-specific processing, the indexing engine places it in tafsir collections, and the owner's navigation shows it alongside Quran commentaries instead of history books. The error becomes a wrong belief.

**What you're evaluating:** Phase C ran the full pipeline on 73 books with real LLM calls. Each book produced a set of output files. You verify that the pipeline's classifications match reality.

**Two possible book statuses:**
- `"success"` — full pipeline completed, result.json has complete SourceMetadata
- `"gate_abort"` — LLM inference completed but validation flagged an issue (disputed attribution, low confidence). result.json has partial data only. Get classification data from llm_responses/ instead.

---

## Output File Structure and Field Paths

Each book's results are in `tests/results/source_engine/phase_c/{book_name}/`. Know exactly what's in each file:

### result.json — SUCCESS books

For books with `"status": "success"`, this is the full SourceMetadata. Key paths:

```
result["status"]                             → "success"
result["genre"]                              → enum string: "sharh", "risalah", "fatawa", etc.
result["science_scope"]                      → list: ["fiqh", "usul_al_fiqh"]
result["is_multi_layer"]                     → boolean
result["text_layers"]                        → list of {layer_type, author} (if multi-layer)
result["structural_format"]                  → "prose", "verse", "commentary", "mixed"
result["authority_level"]                    → "primary", "modern_compilation", "institutional"
result["level"]                              → "beginner"/"intermediate"/"advanced"/"specialist"/null
result["trust_tier"]                         → "verified" or "flagged"
result["trust_score"]                        → float 0.0–1.0
result["attribution_status"]                 → "definitive"/"traditional"/"attributed"/"disputed"/"unknown"
result["author"]["name_arabic"]              → Arabic name string
result["author"]["confidence"]               → float 0.0–1.0
result["confidence_scores"]["genre"]         → float
result["confidence_scores"]["science_scope"] → float
result["confidence_scores"]["multi_layer"]   → float or null
result["title_arabic"]                       → Arabic title
```

**CRITICAL: death_date_hijri is NOT in result.json.** ScholarReference does not include death dates. To verify death dates, read llm_responses/ files.

### result.json — GATE_ABORT books

Different structure — NO full SourceMetadata fields:

```
result["status"]                                    → "gate_abort"
result["error_code"]                                → e.g. "SRC_LOW_CONFIDENCE"
result["gate_errors"]                               → list of strings
result["partial_data"]["extraction_completed"]       → true/false
result["partial_data"]["inference_completed"]         → true/false
```

For gate_abort books, get classification from llm_responses/ instead.

### llm_responses/opus_4_6.json and command_a.json

Full per-model LLM output. These are the PRIMARY source for gate_abort books and for death_date on ALL books:

```
response["parsed"]["genre"]                                       → string
response["parsed"]["genre_confidence"]                            → float
response["parsed"]["author_identification"]["canonical_name_ar"]  → full Arabic name
response["parsed"]["author_identification"]["death_date_hijri"]   → int or null
response["parsed"]["author_identification"]["known_as"]           → list of alternate names
response["parsed"]["author_identification_confidence"]            → float
response["parsed"]["is_multi_layer"]                              → boolean
response["parsed"]["multi_layer_confidence"]                      → float
response["parsed"]["science_scope"]                               → list of strings
response["parsed"]["attribution_status"]                          → string
response["parsed"]["structural_format"]                           → string
```

### extraction.json

Raw Shamela metadata card extraction:

```
extraction["display_title"]         → Title as shown in Shamela
extraction["author_name_raw"]       → Author from metadata card
extraction["author_death_hijri"]    → Death date from card (int or null)
extraction["muhaqiq_name_raw"]      → Editor (or null)
extraction["shamela_category"]      → Shamela's category
extraction["riwayah"]               → Riwayah/transmission (or null)
extraction["_quality_issues"]       → List of quality problems
```

### consensus.json

```
consensus["agreed"]                 → boolean
consensus["single_model_fallback"]  → boolean
consensus["needs_human_gate"]       → boolean
consensus["successful_models"]      → list
consensus["failed_models"]          → list
```

### sanity_checks.json

```
sanity["total_flags"]   → int
sanity["flags"]         → list of {check, severity, detail}
```

---

## Worked Example: Complete Book Evaluation

This shows the EXACT workflow. Pattern-match against this.

### Example A: مجموع الفتاوى (success book)

```
STEP 1 — Read result.json, check status
  status: "success" → full SourceMetadata available

STEP 2 — Extract pipeline values
  Author:      result["author"]["name_arabic"] = "ابن تيمية"
  Genre:       result["genre"] = "fatawa"
  Multi-layer: result["is_multi_layer"] = false
  Science:     result["science_scope"] = ["fiqh", "aqidah"]
  Trust:       result["trust_tier"] = "verified"
  Attribution: result["attribution_status"] = "definitive"
  
  Death date (from llm_responses/opus_4_6.json, NOT result.json):
    opus["parsed"]["author_identification"]["death_date_hijri"] = 728

STEP 3 — Web search verification
  Search "مجموع الفتاوى ابن تيمية shamela"
  → shamela.ws: المؤلف: ابن تيمية (ت 728هـ), جمع: ابن القاسم
  Search "مجموع الفتاوى" ketabonline
  → Confirms ابن تيمية, compiler ابن القاسم
  
  KEY CHECK: Pipeline identified ابن تيمية as author, NOT ابن القاسم (compiler). ✓
  Two independent sources confirm. ✓

STEP 4 — Verdict
  Author: VERIFIED (2 sources, compiler/author distinction correct)
  Genre: VERIFIED (fatawa confirmed)
  Multi-layer: VERIFIED (false — fatwa collection, not commentary)
  Science: PLAUSIBLE (["fiqh","aqidah"] reasonable but fatawa touch many sciences)
  Trust: VERIFIED
  Confidence 0.95: justified — extremely famous book
  Overall: VERIFIED
```

### Example B: الأربعون النووية (gate_abort book)

```
STEP 1 — Read result.json, check status
  status: "gate_abort" → NO full SourceMetadata!
  Must read from llm_responses/ instead.

STEP 2 — Extract pipeline values FROM llm_responses/
  opus = llm_responses/opus_4_6.json
  Author:    opus["parsed"]["author_identification"]["canonical_name_ar"] = "النووي"
  Death:     opus["parsed"]["author_identification"]["death_date_hijri"] = 676
  Genre:     opus["parsed"]["genre"] = "matn"
  ML:        opus["parsed"]["is_multi_layer"] = false
  Science:   opus["parsed"]["science_scope"] = ["hadith"]
  
  Also check command_a.json — do both models agree?

STEP 3 — Web search, same as success books

STEP 4 — Verdict  
  Author: VERIFIED — النووي (676هـ)
  Genre: VERIFIED — matn (hadith_collection also acceptable)
  Multi-layer: VERIFIED — false
  Trust: SKIPPED (gate_abort — no trust_tier in result.json)
  Gate reason: author-science mismatch — pipeline calibration issue, not classification error
  Overall: VERIFIED
```

---

## Verdict Scale

Do NOT use simple PASS/FAIL. Use this 5-level scale:

**VERIFIED** — 2+ independent web sources confirm the pipeline's output. High confidence. Ground truth candidate.

**PLAUSIBLE** — 1 source confirms, OR extraction.json cross-check is consistent. No red flags but not fully confirmed. NOT a ground truth candidate.

**UNVERIFIABLE** — No independent sources found. Output looks reasonable but cannot be confirmed. NOT a ground truth candidate. NOT an error.

**FLAG** — Evidence suggests output may be wrong. Specific concern documented with reasoning.

**ESCALATE** — Contradictory evidence found OR requires domain expertise. Specific multiple-choice question for owner.

**Critical rule: Only VERIFIED books become ground truth candidates.** This prevents the framework from generating false ground truth from unverified evaluations.

---

## Anti-Anchoring Warning

**The expected values in this framework may contain errors.** They were written by the architect based on general knowledge and the book selection document, NOT by independent verification.

Your independent web search OVERRIDES the expected values. If the framework says "genre should be risalah" but shamela.ws and two other sources classify it as "matn", the pipeline's output of "matn" is correct and the framework was wrong.

Do NOT treat the expected values table as ground truth. Treat it as a starting hypothesis to be confirmed or refuted.

---

## Circular Verification Warning

Shamela.ws is the database these books were exported from. It is authoritative for AUTHOR and DEATH DATE (bibliographic facts). However, using Shamela's category field to verify the pipeline's GENRE classification is partially circular — both the pipeline and Shamela draw from the same metadata card.

For genre verification, prefer:
1. Title analysis (شرح → sharh, حاشية → hashiyah, etc.) — fully independent
2. Academic catalogs, university course syllabi, or WorldCat Arabic entries — truly independent
3. ketabonline.com book descriptions — semi-independent
4. Shamela category — least independent, use only as weak confirmation

---

## Arabic Name Matching Rules

Arabic scholar names have many valid forms. DO NOT flag correct answers as mismatches.

**A name is a MATCH if:**
- Shorter or longer form of the same person (ابن القيم = ابن قيم الجوزية = شمس الدين محمد بن أبي بكر الزرعي)
- Uses kunyah vs ism (أبو حنيفة = النعمان بن ثابت)
- Includes or omits nisbah (الحنفي, الشافعي, الدمشقي)
- Includes or omits laqab (شيخ الإسلام ابن تيمية = ابن تيمية)
- Death date matches within ±10 years

**A name is a MISMATCH if:**
- Completely different person (الجاحظ ≠ ابن المقفع)
- Confuses compiler with author (ابن القاسم ≠ ابن تيمية for مجموع الفتاوى)
- Confuses sharh author with matn author (البخاري ≠ ابن حجر for فتح الباري)
- Confuses father and son (ابن عابدين ≠ علاء الدين عابدين for تكملة الحاشية)
- Death date differs by >30 years

---

## Web Search Strategy

### For well-known books (Groups B, C, H):
1. Search `"{exact book title}" shamela.ws` — Shamela's own page is reliable
2. Search `"{book title}" المؤلف` — library/bookstore pages
3. Cross-reference at least 2 sources

### For obscure books (Groups D, E, F, G):
1. Search shamela.ws first
2. If no results, search `"{author name from extraction.json}" وفاة` to verify author independently
3. **Fallback: cross-check extraction.json against llm_responses/.** Did the LLM correctly process the metadata card? If extraction says "الطبراني" and LLM says "سليمان بن أحمد الطبراني" — that's correct expansion, PASS. If extraction says "الطبراني" and LLM says "البخاري" — hallucination, FLAG.
4. If nothing resolves it → ESCALATE with specific question

### For riwayah books (Group F):
Primary check is extraction.json: verify `extraction["riwayah"]` is non-null and contains the expected riwayah name.

---

## Field Evaluation Protocol

Data sources differ by book status:

| Field | Source (success) | Source (gate_abort) |
|-------|-----------------|-------------------|
| Author name | result["author"]["name_arabic"] | llm_responses/*["parsed"]["author_identification"]["canonical_name_ar"] |
| Death date | llm_responses/*["parsed"]["author_identification"]["death_date_hijri"] | Same |
| Genre | result["genre"] | llm_responses/*["parsed"]["genre"] |
| Multi-layer | result["is_multi_layer"] | llm_responses/*["parsed"]["is_multi_layer"] |
| Science | result["science_scope"] | llm_responses/*["parsed"]["science_scope"] |
| Trust | result["trust_tier"] | NOT AVAILABLE — skip |
| Attribution | result["attribution_status"] | llm_responses/*["parsed"]["attribution_status"] |
| Author confidence | result["author"]["confidence"] | llm_responses/*["parsed"]["author_identification_confidence"] |

### 1. Author (CRITICAL)

**VERIFIED:** Name matches per Arabic Name Matching Rules AND confirmed by 2+ independent web sources. Death date ±10 years. Attribution correct.
**PLAUSIBLE:** Name matches extraction.json cross-check or 1 web source. Death date ±10 years. No red flags.
**FLAG:** Partial match with concerns. Death date off 11–30 years. Pipeline says "definitive" but sources show dispute.
**ESCALATE:** Wrong person. Death date off >30 years. Genuinely unresolvable.

### 2. Genre (CRITICAL)

**VERIFIED:** Matches title signals AND at least 1 non-Shamela web source confirms.
**PLAUSIBLE:** Matches title signals. Reasonable alternative classification.
**FLAG:** Contradicts strong title signals or known classification.

**Known acceptable ambiguities (do NOT flag):**
حاشية العطار (hashiyah/taqrirat), الأربعون النووية (matn/hadith_collection), إعلام الموقعين (risalah/fatawa/other), مقامات الحريري (adab/other), الأم للشافعي (any reasonable genre)

### 3. Multi-Layer (CRITICAL)

**Deterministic:** sharh/hashiyah/taqrirat genre → true. Standalone genres → false. شرح in title → true.
**CRITICAL false-positive watchlist:** إعلام الموقعين (all 3 editions) MUST be false. fatawa/tarikh/mawsuah MUST be false.

### 4. Science Scope (MODERATE)

**VERIFIED:** Primary science correct and confirmed by web source. Superset acceptable. Empty for non-Islamic works correct.
**PLAUSIBLE:** Looks reasonable from title/genre, not independently confirmed.

### 5. Trust Tier (MODERATE — success books only)

**VERIFIED:** Classical primary → verified. Modern/unknown/truncated → flagged.

### 6. Confidence Calibration (check across session)

After evaluating all books:
- **High confidence + wrong = DANGEROUS.** Flag immediately.
- **Low confidence + right = acceptable.** Pipeline is appropriately cautious.
- Note any patterns.

### 7. Single-Model Fallback Assessment

**Phase C specific:** Command A timed out for most/all books. Most results are Opus-only with `single_model_fallback: true`. This means:
- `consensus["agreed"]` is meaningless — there was no second model to agree with
- Author confidence is capped at 0.85 per SPEC §6 (single-model biographical inference)
- The evaluation is still valid — Opus is the stronger model
- Do NOT treat single_model_fallback as a quality problem. Treat it as a data limitation.
- DO note if any books had both models succeed (Command A occasionally worked). Those have stronger consensus backing.

---

## Pre-Populated Expected Values

Starting points only — Claude Chat MUST still verify independently via web search.

### Group A Fixtures: read ground_truth_comparison.json. If all_match: true → PASS.

### All Other Books

| Book | Author | Death | Genre | ML | Science | Key Check |
|------|--------|-------|-------|----|---------|-----------|
| ألفية ابن مالك (2 eds) | ابن مالك | 672 | matn/nazm | F | nahw,sarf | Editions must agree |
| الأربعون النووية | النووي | 676 | matn | F | hadith | hadith_collection also OK |
| حاشية ابن عابدين | ابن عابدين | 1252 | hashiyah | T | fiqh | 3-layer |
| زاد المستقنع | الحجاوي | 968 | mukhtasar | F | fiqh | — |
| حاشية العطار | العطار | 1250 | hashiyah/taqrirat | T | usul_al_fiqh | — |
| الموسوعة الفقهية | وزارة الأوقاف | null | mawsuah | F | fiqh | Institutional |
| مجموع الفتاوى | ابن تيمية NOT ابن القاسم | 728 | fatawa | F | fiqh,aqidah | Compiler≠author |
| لسان العرب | ابن منظور | 711 | mujam | F | lugha | — |
| سير أعلام النبلاء | الذهبي | 748 | tabaqat | F | tarikh | — |
| بداية المجتهد | ابن رشد الحفيد | 595 | fiqh_comparative | F | fiqh | NOT الجد |
| الرحيق المختوم | المباركفوري | 1427 | sirah | F | sirah | Modern |
| البداية والنهاية (2 eds) | ابن كثير | 774 | tarikh NOT tafsir | F | tarikh | Critical |
| فتح الباري بشرح البخاري | ابن حجر NOT البخاري | 852 | sharh | T | hadith | — |
| فتح الباري لابن رجب | ابن رجب | 795 | sharh | T | hadith | Different author |
| شرح الورقات | المحلي | 864 | sharh | T | usul_al_fiqh | — |
| إعلام الموقعين (3 eds) | ابن القيم | 751 | risalah/other | **F** | fiqh | MUST NOT be ML |
| تفسير الطبري (2 eds) | الطبري | 310 | tafsir | verify | tafsir | — |
| الفقه الأكبر | أبو حنيفة | 150 | risalah/matn | F | aqidah | attrib=disputed |
| الإبانة (2 eds) | الأشعري | 324 | risalah | F | aqidah | Text disputed |
| البيان والتبيين | الجاحظ | 255 | adab/other | F | adab | — |
| حديث الضب | الطبراني | 360 | hadith_collection | F | hadith | 1 page |
| الورقة النحوية | VERIFY | — | risalah/matn | F | nahw | Low conf OK |
| فتاوى اللجنة الدائمة (2) | اللجنة الدائمة | null | fatawa | F | fiqh | Institutional |
| شرح النووي على مسلم | النووي | 676 | sharh | T | hadith | trust=verified |
| نصيحة لطالب الحق | المعلمي | ~1386 | risalah/other | F | — | trust=flagged |
| أدب النفوس | الآجري | 360 | risalah/other | F | — | Truncated |
| أحاديث العطار | VERIFY | — | hadith_collection | F | hadith | trust=flagged |
| شرح العقيدة الطحاوية (2 eds) | ابن أبي العز | 792 | sharh | T | aqidah | — |
| مقامات الحريري | الحريري | 516 | adab/other | F | adab | Mixed format |
| شرح مقامات الحريري | VERIFY | — | sharh | T | adab | — |
| الكلام على حديث الإستلقاء | أبو موسى المديني | 581 | risalah/hadith | F | hadith | Obscure |
| الأذكار | النووي | 676 | risalah/other | F | hadith/fiqh | Same author as أربعون |
| الأم للشافعي | الشافعي | 204 | verify | F | fiqh | — |
| الرسالة للشافعي | الشافعي | 204 | risalah/matn | F | usul_al_fiqh | — |
| تحفة المودود (2 eds) | ابن القيم | 751 | risalah | F | fiqh | — |
| مختصر صحيح مسلم | المنذري | 656 | mukhtasar | F | hadith | — |
| مسند أحمد | أحمد بن حنبل | 241 | hadith_collection | F | hadith | — |
| معالم بيانية | VERIFY | — | risalah/other | F | tafsir/balagha | Modern |
| تكملة حاشية ابن عابدين | علاء الدين عابدين (SON) | ~1306 | hashiyah | T | fiqh | ≠ father |
| التعليق على الرحيق المختوم | VERIFY | — | sharh/risalah | verify | sirah | — |
| المستدرك على مجموع الفتاوى | VERIFY | — | fatawa | F | fiqh | — |
| الأحاديث الأربعين + ابن رجب | VERIFY | — | sharh/matn | verify | hadith | — |
| النكت على شرح النووي | VERIFY | — | risalah/sharh | verify | hadith | — |
| اللامع العزيزي شرح ديوان المتنبي | VERIFY | — | sharh | T | adab | — |
| المآخذ على شراح ديوان المتنبي | VERIFY | — | risalah/other | F | adab | NOT sharh |
| شرح ديوان المتنبي للواحدي | الواحدي | 468 | sharh | T | adab | — |
| الإبدال في لغات الأزد | VERIFY | — | risalah/other | F | lugha | Page mismatch |

ML = Multi-Layer, T = true, F = false

### Riwayah Books: check extraction["riwayah"] is non-null

أمالي المحاملي, تاريخ ابن معين, حديث يحيى بن معين, مسند أبي حنيفة, من أحاديث سفيان الثوري

---

## Edition Group Protocol

Compare all editions of same work. Author/genre/multi-layer/science MUST match. Muhaqiq/trust MAY differ.

| Group | Critical Check |
|-------|---------------|
| إعلام الموقعين (3) | ALL is_multi_layer: false |
| البداية والنهاية (2) | Both tarikh, NOT tafsir |
| شرح العقيدة الطحاوية (2) | Author + genre agree |
| تفسير الطبري (2) | Author + genre agree |
| تحفة المودود (2) | Must agree |
| الإبانة (2) | Must agree |
| فتاوى اللجنة الدائمة (2) | Same institution |
| ألفية ابن مالك (2) | Must agree |
| NOT a group: حاشية ابن عابدين vs تكملة | Different authors (father/son) |

---

## Calibration Step — DO THIS FIRST

Test framework on 3 books before scaling: أحكام الاضطباع والرمل في الطواف (fixture), الأربعون النووية (likely gate_abort), مجموع الفتاوى (compiler vs author test).

Verify:
1. Can Claude Chat find files? (`ls tests/results/source_engine/phase_c/` — Arabic directory names must render)
2. Can it read JSON with Arabic content? (Read result.json, verify Arabic text displays correctly)
3. Does it correctly handle gate_abort? (الأربعون النووية reads from llm_responses/ not result.json)
4. Does web search return useful results for Arabic queries?
5. Is the output format usable for aggregation?

If the calibration session reveals issues, fix the framework before scaling.

---

## Self-Check Protocol (EVERY session must do this)

### At session start:
```bash
# Verify you can read Arabic directory names
ls tests/results/source_engine/phase_c/ | head -10
# Verify you can read a result file
cat tests/results/source_engine/phase_c/الأربعون\ النووية/result.json | python3 -m json.tool | head -5
```
If Arabic paths don't work, try: `cd tests/results/source_engine/phase_c && ls` and work from there.

### After every 3 books:
Re-read the Field Path table above. Confirm you're reading from the correct paths for success vs gate_abort books.

### At session end — consistency self-check:
Review all your verdicts together. Ask:
- Did I apply the same standard to book 1 and book 10?
- Did I flag a genre for one book but pass the same genre for a similar book?
- Did I actually do web searches for every book, or did I start relying on training data after the first few?
- For VERIFIED verdicts: did I actually find 2+ independent sources, or am I over-counting?

If you find inconsistencies, revise the affected verdicts before submitting.

---

## Session Design — Reduced Batch Sizes

**Maximum 10 books per session.** At 15 books × 5 files each, context gets saturated and evaluation quality degrades. 10 books keeps Claude Chat within reliable context range.

### Session 0: CALIBRATION (3 books)
أحكام الاضطباع والرمل في الطواف, الأربعون النووية, مجموع الفتاوى

### Session 1: Fixture Regression (12 books)
All Group A fixture books. Primarily automated — read ground_truth_comparison.json. Exception to batch size limit because these require less tool use.

### Session 2: Famous Works A (8 books)
حاشية ابن عابدين, لسان العرب, سير أعلام النبلاء, فتح الباري - ط السلفية, بداية المجتهد, الموسوعة الفقهية الكويتية, مسند أحمد, زاد المستقنع

### Session 3: Famous Works B (7 books)
الرحيق المختوم, الأم للشافعي, الرسالة للشافعي, الأذكار للنووي, شرح النووي على مسلم, مجموع الفتاوى, الأربعون النووية

### Session 4: Multi-Layer + Commentary (10 books)
فتح الباري لابن رجب, شرح الورقات, حاشية العطار, شرح العقيدة الطحاوية - ط الرسالة, مقامات الحريري, شرح مقامات الحريري, شرح ديوان المتنبي, اللامع العزيزي, المآخذ على شراح ديوان المتنبي, التعليق على الرحيق المختوم

### Session 5: Attribution + Trust + Obscure (10 books)
الفقه الأكبر, الإبانة - ت العصيمي, الإبانة - ت فوقية, البيان والتبيين, الورقة النحوية, حديث الضب, نصيحة لطالب الحق, أدب النفوس, أحاديث العطار, الكلام على حديث الإستلقاء

### Session 6: Edition Groups (cross-comparison only, all editions)
Focus: consistency across editions. Compare: إعلام الموقعين (3), البداية والنهاية (2), تفسير الطبري (2), تحفة المودود (2), فتاوى اللجنة الدائمة (2), ألفية ابن مالك (2), شرح العقيدة الطحاوية (2). Also: تكملة حاشية ابن عابدين (verify DIFFERENT author from حاشية).

### Session 7: Riwayah + Remaining (10 books)
5 riwayah books + معالم بيانية + مختصر صحيح مسلم + المستدرك على مجموع الفتاوى + الأحاديث الأربعين مع ابن رجب + النكت على شرح النووي + الإبدال في لغات الأزد

**Overlap between sessions is intentional.** Books appear in independent evaluation sessions (2-5) AND in the edition group session (6). Different questions tested differently.

---

## Practical Logistics

Each evaluation session = new Claude Chat conversation in the same KR project. Clone repo, read this framework, evaluate assigned books.

**Prerequisites:** CC has committed all results. Owner verified git push. This framework committed to repo.

**Timeline:** Calibration (~20 min) → Fix bugs (~10 min) → 7 sessions (overlap OK, ~30 min each) → Aggregation (~15 min) → Owner answers escalations (~15-30 min). **Total owner time: ~1 hour.**

### Aggregation Prompt

After all sessions, paste reports into final session:

```
Clone the KR repo. Read PHASE_C_EVALUATION_FRAMEWORK.md.

Here are evaluation reports from all sessions: [paste]

Aggregate into PHASE_C_EVALUATION_REPORT.md:
1. Summary counts per verdict level (VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE)
2. Fixture regression results
3. Edition group consistency
4. All per-book verdicts
5. Systematic findings (patterns across sessions)
6. Confidence calibration: any high-confidence wrong answers?
7. Owner escalation queue (numbered, specific, multiple-choice)
8. Proposed GROUND_TRUTH.json entries (VERIFIED books only, with source URLs)
```

---

## Ground Truth Proposal Criteria

A book qualifies for ground truth proposal ONLY if ALL of these are true:
1. Overall verdict is VERIFIED (not PLAUSIBLE or UNVERIFIABLE)
2. Author name + death date confirmed by 2+ independent sources (at least one non-Shamela)
3. Genre verified by title analysis AND at least one external classification
4. Multi-layer status is deterministic from genre/title (no ambiguity)
5. The pipeline's confidence scores are reasonably calibrated (not wildly over/under-confident)
6. If both models ran: consensus["agreed"] = true. If single-model fallback: author confidence ≥ 0.80

Each proposed entry must include the JSON in this EXACT format (matches existing GROUND_TRUTH.json entries):

```json
{
  "new_key_name": {
    "title": "العنوان بالعربي",
    "author_identified": "اسم المؤلف (ت XXXهـ)",
    "author_death_hijri": 728,
    "genre": "fatawa",
    "science_scope": ["fiqh", "aqidah"],
    "structural_format": "prose",
    "is_multi_layer": false,
    "level": "advanced",
    "authority_level": "primary",
    "expected_trust": "verified",
    "notes": "Brief justification. Sources: [URL1], [URL2].",
    "attribution_status": "definitive"
  }
}
```

**key_name convention:** Use the book's directory name from the collection, e.g. `"مجموع_الفتاوى"` (spaces to underscores).

The owner reviews ONLY these proposals — pre-vetted, documented, structured. Much faster and more reliable than open-ended review.

---

## Web Search Enforcement

**Claude Chat MUST actually perform web searches. It must NOT rely on training data.**

To verify compliance, every book evaluation MUST include a "Web Sources" field listing specific URLs visited. Acceptable sources:
- shamela.ws/book/XXXXX or shamela.ws/author/XXXXX (specific pages, not homepage)
- ketabonline.com/ar/books/XXXXX
- islamicbook.ws, al-maktaba.org, or similar Islamic library sites
- ar.wikipedia.org for well-known scholars/works
- University course syllabi or academic catalog entries

**NOT acceptable as sole source:**
- No URL listed (used training data)
- Only shamela.ws homepage (didn't actually search)
- Only the expected values table from this framework

If Claude Chat cannot find ANY web source for a book, the verdict must be UNVERIFIABLE (not PLAUSIBLE or VERIFIED). Training data alone is insufficient for verification because it may contain the same errors as the pipeline.

---

## Extraction Quality Check

Before evaluating the LLM's output, check whether the INPUT was reasonable:

1. Read `extraction.json` — does it have a non-empty `author_name_raw`? If the metadata card was blank or garbled, the LLM was working blind.
2. Read `prompt_sent.json` — check `metadata_fields_present` vs `metadata_fields_absent`. Books with 3+ absent fields are harder to classify.
3. Check `extraction["_quality_issues"]` — any flagged issues?

**If extraction was poor but the LLM still got the right answer:** that's actually impressive — note it as a positive finding.
**If extraction was poor and the LLM got the wrong answer:** that's expected — FLAG but note "poor extraction input" as a mitigating factor. The fix is upstream (better extraction), not the LLM.

---

## Expected Gate Abort Rate

Phase C's 3-book test showed 2/3 gate_abort. The full run is showing ~58% gate_abort. This is NOT a pipeline failure — it's the validation layer being conservative with single-model inference and isolated temp libraries (no scholar registry context). 

**Do not treat gate_abort as a negative signal about book quality.** Gate_abort means "the validation layer wants human review." The LLM classification inside may be perfectly correct.

For evaluation purposes: gate_abort books are evaluated identically to success books, just from different file paths (llm_responses/ instead of result.json).

---

## Most Dangerous Failure: Both Models Wrong Together

If both LLM models agree on a wrong answer, the pipeline produces high-confidence wrong metadata. This is worse than disagreement (which triggers human gates).

**How to detect:** Your web search returns a different author, genre, or attribution status than BOTH models produced.

**What to do:**
1. Mark as FLAG with severity "SYSTEMATIC"
2. Document exactly what both models said vs what's correct
3. Check: is this the same type of error on other books? (e.g., both models consistently confuse compilers with authors)
4. In the session summary, call this out prominently — systematic model agreement on wrong answers is the #1 priority finding

**Example of dangerous agreement:** Both models say مجموع الفتاوى author is "ابن القاسم" with 0.90 confidence. Both wrong — ابن القاسم is the compiler, ابن تيمية is the author. If this passes undetected, the library attributes one of the most important Islamic works to the wrong person.

---

## Failure Modes Prevented

1. Owner says "looks right" to wrong answer → Claude Chat verifies via web search
2. Reviewer fatigue → Claude Chat doesn't fatigue; batch size capped at 10
3. Inconsistent criteria → Standardized protocol + session-end consistency self-check
4. Systematic pipeline errors missed → Cross-book pattern analysis + "SYSTEMATIC" flag severity
5. Owner time on obvious books → Tiered auto-pass for fixtures
6. Owner ground truth errors → Only VERIFIED books (2+ sources) become GT candidates
7. Wrong field paths → Exact paths documented with success/gate_abort distinction + worked examples
8. Gate_abort panic → Expected rate documented; gate_abort ≠ failure
9. Arabic name false flags → Explicit matching rules with examples
10. Framework bugs multiplied → Calibration step catches first
11. Expected values anchoring → Anti-anchoring warning; web search overrides framework
12. Circular verification → Source quality hierarchy; Shamela category = weak evidence for genre
13. Context fatigue → Batch sizes ≤10; mid-session refresh protocol
14. False ground truth from unverified books → Strict 6-point GT criteria with JSON format example
15. Claude Chat skips web search → Web Search Enforcement section; URL requirement per book
16. Both models wrong together → Explicit detection protocol + SYSTEMATIC flag severity
17. Poor extraction blamed on LLM → Extraction Quality Check distinguishes input vs inference problems
18. Single-model fallback misread → Explicit section on single-model scenario; confidence cap noted
