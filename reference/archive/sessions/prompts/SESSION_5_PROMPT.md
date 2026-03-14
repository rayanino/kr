Phase C calibration, Sessions 1–4 are done. You are continuing evaluation work that previous Claude Chat sessions completed.

Your job: evaluate Phase C pipeline results for Session 5 (Attribution + Trust + Obscure — 10 books), following the protocol below.

<what_was_done>
Session 0 (Calibration) evaluated 3 books, found 4 engine bugs, committed corrections.
Session 1 (Fixture Regression) evaluated 11 books (14 total with calibration).
Session 2 (Famous Works A) evaluated 8 books — all 8 VERIFIED (1 with ML field-level flag on مسند أحمد).
Session 3 (Famous Works B) evaluated 7 books — all 7 VERIFIED (1 with ML field-level flag on الرسالة).
Session 4 (Multi-Layer + Commentary) evaluated 10 books — 9 VERIFIED + 1 PLAUSIBLE (التعليق على الرحيق المختوم).

Running totals: 34 VERIFIED, 5 PLAUSIBLE, 0 FLAG, 0 ESCALATE (39 books evaluated).

Prior reports are in the repo:
- PHASE_C_SESSION1_REPORT.md
- PHASE_C_SESSION1_DEEP_ANALYSIS.md
- PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md
- PHASE_C_SESSION2_REPORT.md
- PHASE_C_SESSION3_REPORT.md
- PHASE_C_SESSION4_REPORT.md
</what_was_done>

<critical_corrections>
The evaluation framework (PHASE_C_EVALUATION_FRAMEWORK.md) has errors discovered during calibration. These corrections OVERRIDE the framework wherever they conflict:

CORRECTION 1 — LLM FILENAME:
  Framework says: llm_responses/opus_4_6.json
  Actual filename: llm_responses/claude_opus_4_6.json

CORRECTION 2 — COMMAND A DID NOT TIME OUT:
  0/73 books are single_model_fallback. All 73 have dual-model consensus.
  All 10 Session 5 books use Opus + Command A. No GPT-5.4 books in this session.
  Framework Section 7 (Single-Model Fallback Assessment) does NOT apply. Skip it entirely.

CORRECTION 3 — AUTHOR CONFIDENCE IN result.json IS BROKEN:
  result["author"]["confidence"] is ALWAYS 1.0 for every success book. This is an engine bug.
  The real author confidence is ONLY in: llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence

CORRECTION 4 — SECOND MODEL:
  All 10 Session 5 books use command_a.json as the second model.

CORRECTION 5 — VERIFIED THRESHOLD:
  Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) all derive from the same underlying database. They count as ONE source collectively, not multiple independent sources.
  VERIFIED requires 2+ genuinely independent sources. Independent means: Wikipedia Arabic, academic catalogs, university syllabi, publisher sites, archive.org, noor-book.com, islamway.net, alukah.net, government sites, or non-Shamela Islamic library sites.

CORRECTION 6 — CONSENSUS DOES NOT CHECK MULTI-LAYER OR ATTRIBUTION:
  consensus.agreed=true only means author + work agreement. Models can disagree on is_multi_layer, attribution_status, and authority_level and still show agreed=true. Always compare these fields between both models yourself.
  Session 5 specific: all 10 books have ML=false agreement. But 6/10 have attribution disagreements — you MUST check attribution independently for each book.
</critical_corrections>

<session_4_findings_carry_forward>
These findings from Sessions 2-4 affect how you evaluate Session 5 books:

1. Zero author identification errors across 39 books evaluated. The pipeline's author identification is the strongest field.

2. Opus genre=hashiyah contradiction: Opus can label a book "hashiyah" when only 2 layers exist (should require 3). CA correctly resolves. Cumulative wrong-at-high-confidence: 2 ML cases (0.85-0.90), 1 genre case (0.82). Session 5 has no ML=true books, so the ML bias is not relevant. But watch for genre mismatches between models.

3. Attribution pattern across Sessions 3-4: Opus says "definitive" for famous well-established works, "traditional" for obscure conventionally-attributed works, "disputed" for genuinely contested works. CA tends toward "definitive" even for traditional works. Only flag when Opus says "disputed" — those are the genuine scholarly disputes requiring independent investigation. Session 5 has 3 "disputed" books (الفقه الأكبر, الإبانة ×2) — the first time this category appears.

4. Death date genuine inference running total: 1 confirmed correct (مجموع الفتاوى 728), 1 confirmed wrong (أساليب بلاغية 1432 vs actual 1439), 4 confirmed false positives (dates embedded in author_name_raw). Session 5 has 1 genuine inference: الإبانة ت العصيمي (324 — no death date in extraction or raw text). All others in Session 5 are pass-through.

5. Authority_level disagreements: systematic pattern where Opus says "reference" or "modern_compilation" while CA says "primary." Not checked by consensus. Document when present but do not flag.

6. web_fetch compliance was 0/10 in Session 4. Aim for at least 5/10 in Session 5 — the disputed-attribution and VERIFY-author books genuinely require fetching full pages, not just search snippets.
</session_4_findings_carry_forward>

<session_5_books>
10 books — Attribution + Trust + Obscure. **Strategic analysis rates this HIGH difficulty.**

| # | Book (exact directory name) | Status | Models | Genre (Opus) | Key risk |
|---|---------------------------|--------|--------|--------------|----------|
| 1 | الفقه الأكبر | gate_abort | opus + command_a | matn | **attrib: Opus=disputed, CA=traditional** |
| 2 | الإبانة عن أصول الديانة - ت العصيمي | gate_abort | opus + command_a | risalah | **attrib: Opus=disputed, CA=definitive; death 324 GENUINE INFERENCE** |
| 3 | الإبانة عن أصول الديانة - ت فوقية | gate_abort | opus + command_a | matn | **attrib: Opus=disputed, CA=definitive** |
| 4 | البيان والتبيين | success | opus + command_a | adab | Low risk |
| 5 | الورقة النحوية | success | opus + command_a | matn | **Lowest author conf in corpus: Opus 0.55, CA 0.70** |
| 6 | حديث الضب الذي تكلم بين يدي النبي للطبراني | gate_abort | opus + command_a | hadith_collection | 1 page, content_minimal |
| 7 | نصيحة لطالب الحق - ضمن «آثار المعلمي» | gate_abort | opus + command_a | risalah | 2 pages, content_minimal |
| 8 | أدب النفوس للآجري | gate_abort | opus + command_a | risalah | **Truncated: 24 of 271 pages** |
| 9 | أحاديث العطار عن شيوخه | gate_abort | opus + command_a | hadith_collection | **Truncated + truncation flag; author=VERIFY** |
| 10 | الكلام على حديث الإستلقاء لأبي موسى المديني | success | opus + command_a | risalah | 2 pages, obscure |

3 SUCCESS books (البيان والتبيين, الورقة النحوية, الكلام على حديث): check result.json for trust_tier, model source, confidence_scores.
7 GATE_ABORT books: get all classification data from llm_responses/, not result.json.
0 ML=true books. All 10 agree ML=false.
6/10 books have attribution disagreements between models.
</session_5_books>

<pre_identified_risks>
From NEXT.md, strategic analysis, and pipeline data pre-scan:

CRITICAL PRIORITY:
- الفقه الأكبر: Extraction explicitly says "ينسب لأبي حنيفة" (attributed to). title_full includes "المنسوبين لأبي حنيفة." Opus=disputed, CA=traditional. This is a famous scholarly debate. Genre disagreement: Opus=matn(0.90), CA=risalah(0.90) — both acceptable. The evaluator MUST independently research the attribution debate.
- الإبانة (2 editions): One of the most debated texts in Islamic intellectual history. Ash'ari scholars question whether the surviving text was altered. Opus=disputed for both, CA=definitive. CRITICAL: ت العصيمي has NO death date in extraction (author_name_raw="أبو الحسن علي بن إسماعيل الأشعري" — no embedded date). Opus death=324 is a GENUINE INFERENCE. ت فوقية has death=324 in extraction (pass-through). Genre differs between editions: ت العصيمي=risalah, ت فوقية=matn.
- الورقة النحوية: Author حازم خنفر — Opus conf 0.55, CA conf 0.70. No death date. Framework says VERIFY. Only 2 pages. trust=flagged(0.4325). This may be a modern author with zero online presence. If unfindable, use UNVERIFIABLE.

HIGH PRIORITY:
- أحاديث العطار عن شيوخه: Framework says author=VERIFY. ابن مقسم العطار (ت 354). Truncated: 10 of 279 pages with truncation_with_mismatch flag.
- أدب النفوس للآجري: 24 of 271 pages (9%). title_full says "مجموعة أجزاء حديثية - أدب النفوس." Science disagreement: Opus=['tasawwuf','aqidah'], CA=['tasawwuf','adab'].

MEDIUM PRIORITY:
- حديث الضب: 1 page. الطبراني (ت 360) well-known. content_minimal flag.
- نصيحة لطالب الحق: المعلمي اليماني (1313-1386 هـ), death pass-through. 2 pages. Modern author.
- الكلام على حديث الإستلقاء: أبو موسى المديني (ت 581). Success, trust=verified(0.6925). 2 pages. Obscure but straightforward.

LOW PRIORITY:
- البيان والتبيين: الجاحظ (ت 255). Famous. Success, trust=verified(0.6925). Straightforward.
</pre_identified_risks>

<attribution_investigation_protocol>
Session 5 is the FIRST session with genuinely disputed attributions. This protocol is MANDATORY for الفقه الأكبر and الإبانة (3 books total).

For each disputed-attribution book:
1. Search for the SPECIFIC attribution debate (e.g., "الفقه الأكبر نسبة أبو حنيفة خلاف" or "الإبانة الأشعري تحريف")
2. web_fetch at least 1 scholarly source discussing the dispute
3. Identify: Who accepts the attribution? Who disputes it? What are the arguments on each side?
4. Compare Opus (disputed) vs CA (traditional/definitive) — which better reflects the range of scholarly opinion?
5. Take a position: Is the attribution genuinely disputed, traditionally accepted, or definitively established?
6. Reflect the honest uncertainty in your verdict:
   - If scholars genuinely disagree → attribution field = "disputed is correct" → overall PLAUSIBLE or VERIFIED depending on other fields
   - If the dispute is fringe/rejected by mainstream → attribution field = "traditional/definitive is more accurate" → no downgrade
   - If you cannot determine the state of the debate → UNVERIFIABLE for the attribution field

WORKED EXAMPLE — how to handle a disputed-attribution book:

Suppose the pipeline says الكتاب X is by المؤلف Y with attribution=disputed (Opus) / definitive (CA).
Step 1: Search "الكتاب X نسبة المؤلف Y" → find 3 sources
Step 2: web_fetch a scholarly article → it says "most scholars accept the attribution, but [specific scholar] argued in [year] that [specific evidence] suggests otherwise"
Step 3: Assess — the dispute exists but is a minority position
Step 4: Verdict = "Attribution: Opus=disputed is technically correct (a dispute exists), but the mainstream consensus accepts the attribution. CA=definitive overstates certainty. 'traditional' would be the most precise label. This does not downgrade the overall verdict."

This is NOT a template to copy — it shows the DEPTH of investigation required. Each book's attribution debate is different and requires its own research.
</attribution_investigation_protocol>

<corrected_per_book_workflow>
For EVERY book, follow this exact sequence. Do not skip steps or reorder them.

STEP 1 — Read EVALUATION_QUICK_REFERENCE.md (re-read before each book, not just the first).
  Then: python3 read_book.py "book_directory_name" — reads all pipeline data.

STEP 2 — Check extraction quality FIRST (before looking at LLM output):
  From read_book.py output, note:
    - author_name_raw: present? Does it contain an embedded death date like "[ت XXX هـ]" or "(XXX - XXX هـ)"?
    - shamela_category: note for cross-check against pipeline genre
    - muhaqiq_name_raw: present or null?
    - _quality_issues: any flags? (content_minimal, page_count_mismatch, truncation_with_mismatch)
    - fields_present vs fields_absent: how much context did the LLM have?

STEP 3 — Extract pipeline values from BOTH models:
  For gate_abort books: read ALL fields from llm_responses/.
  For success books: read result.json for genre, ML, science, trust. Read llm_responses/ for author confidence.
  Compare Opus vs CA on: genre, author, death_date, ML, science_scope, attribution, authority_level.
  Note ALL disagreements — especially attribution (6/10 books disagree on this).

STEP 4 — For disputed-attribution books (الفقه الأكبر, الإبانة ×2): follow the attribution_investigation_protocol above. This replaces the generic web search step for these 3 books.

STEP 5 — For VERIFY-author books (الورقة النحوية, أحاديث العطار): search for the specific author name independently. Do not assume both models agreeing means correct — both may share the same training-data gap.

STEP 6 — For all other books: web search (BEFORE writing verdict) — at minimum 1 search per book.
  Use web_fetch on at least 1 URL per book for the high-priority books.

STEP 7 — Check consensus:
  Read consensus.json: agreed (bool), successful_models.
  Remember: consensus does NOT check attribution or authority_level.

STEP 8 — Produce structured verdict using this exact format:

  Book: [Arabic name]
  Status: [success | gate_abort]
  Models: [opus + command_a]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value] / Death source: [pass-through | inferred | absent]
  Genre: [verdict] — Pipeline: [value] / Expected: [value] / Shamela cat: [value] / Agreement: [yes | no — explain]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value] / Model agreement: [yes | no]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Attribution: [verdict] — Opus: [value] / CA: [value] / Investigated: [summary of what you found] / Position: [your assessment]
  Trust: [For success books] Pipeline: [value] / Score: [value]. [For gate_abort] SKIPPED (gate_abort)
  Consensus: agreed=[bool], models=[list]
  Extraction quality: [clean | issues noted — specify]
  Result.json model source: [For success books: which model's values appear] / N/A (gate_abort)
  Web Sources: [specific URLs visited, marking Shamela-ecosystem vs independent, note any fetched]
  Notes: [anything notable]
</corrected_per_book_workflow>

<after_all_verdicts>
After completing all 10 verdicts:

1. Consistency self-check (as a SEPARATE pass — not inline while writing):
   - Same standards applied to book 1 and book 10?
   - Source independence counts honest?
   - Shamela-ecosystem excluded everywhere?
   - Success books checked for trust + model source?
   - Attribution investigated (not just noted) for all 3 disputed books?

2. Confidence calibration section:
   - Table of all author/genre confidence scores
   - Any high-confidence + wrong cases? (Most dangerous pattern)
   - Session 5 specific: do the LOW-confidence scores (الورقة 0.55, الملاح from Session 4 at 0.72) correspond to genuinely hard cases? Good calibration = low confidence on hard cases.

3. Cross-book patterns:
   - الإبانة editions: are author/death consistent across both? Note genre inconsistency (risalah vs matn).
   - Attribution pattern: how do the 3 disputed books relate to the Opus attribution taxonomy from Sessions 3-4?
   - Obscure vs famous: do confidence scores discriminate appropriately?

4. Strategic prediction validation from PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md.

5. Commit and push the report as PHASE_C_SESSION5_REPORT.md. Note: the owner will run 5 review rounds after this.
   - Rounds 1-4: Review the report (each round attacks from a different angle). The report is finalized after Round 4.
   - After Round 4: Write the handoff (NEXT.md) for Session 6 with pre-scanned pipeline data.
   - Round 5: Verify the handoff against pipeline data and governing documents. The final commit happens after Round 5.
</after_all_verdicts>

<task>
Clone the repo. Read these files in this order:
1. NEXT.md — current status and Session 5 specifics (DEEP READ — this is the primary handoff)
2. PHASE_C_ERRATA.md — corrections that override framework (DEEP READ — these are the actual rules)
3. PHASE_C_EVALUATION_FRAMEWORK.md — full protocol (SKIM for context — verdict scale §Verdict Scale, expected values table for Session 5 books, worked examples §Worked Example)
4. PHASE_C_SESSION4_REPORT.md — prior session (READ findings + cross-book patterns, SKIM per-book details)
5. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md — predictions and risk map (READ Session 5 risk prediction + death date inference list)
6. EVALUATION_QUICK_REFERENCE.md — compact checklist (DEEP READ — re-read before EACH book)

HELPER TOOL: python3 read_book.py "book_directory_name" reads all data for any book.

Then evaluate all 10 Session 5 books. For each book, re-read the quick reference, then follow the corrected per-book workflow exactly. Produce the structured verdict for each book.

IMPORTANT: Start with the 3 disputed-attribution books (الفقه الأكبر, الإبانة ×2) while context is fresh. These require the deepest investigation. Then do the remaining 7.

After book 6 or 7: pause and run the mid-session quality gate from EVALUATION_QUICK_REFERENCE.md.

After all 10 verdicts: produce the consistency self-check, confidence calibration, and cross-book patterns sections. Commit the report.
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip web search for any book — training data alone is insufficient
- Do NOT skip the attribution investigation for الفقه الأكبر and الإبانة — noting "Opus=disputed" without researching the actual debate is insufficient
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — all LLM data is captured (7/10 books are gate_abort)
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- Do NOT give VERIFIED to books where you cannot find the author online — use UNVERIFIABLE honestly
- Do NOT invent verdict categories — only VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- Do NOT assume "both models agree" means correct for VERIFY-author books — both may be wrong
- Do NOT classify الإبانة ت العصيمي death date 324 as "pass-through" — extraction has NO death date and author_name_raw has no embedded date. This is a GENUINE INFERENCE.
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated, STOP and tell me rather than degrading quality silently
</guardrails>
