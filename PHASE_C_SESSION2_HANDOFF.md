Phase C calibration and Session 1 are done. You are continuing evaluation work that previous Claude Chat sessions completed. 

Your job: evaluate Phase C pipeline results for Session 2 (Famous Works A — 8 books), following the protocol below.

<what_was_done>
Session 0 (Calibration) evaluated 3 books, found 4 engine bugs, committed corrections.
Session 1 (Fixture Regression) evaluated 11 books (14 total with calibration).
Verdicts so far: 10 VERIFIED, 4 PLAUSIBLE, 0 FLAG, 0 ESCALATE.

Session 1 also produced a deep self-review and strategic analysis that identified methodology weaknesses and cross-book patterns. Read these files from the repo:
- PHASE_C_SESSION1_REPORT.md — per-book verdicts
- PHASE_C_SESSION1_DEEP_ANALYSIS.md — methodology fixes (IMPORTANT)
- PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md — predictions for Sessions 2-7, risk map
</what_was_done>

<critical_corrections>
The evaluation framework (PHASE_C_EVALUATION_FRAMEWORK.md) has errors discovered during calibration. These corrections OVERRIDE the framework wherever they conflict:

CORRECTION 1 — LLM FILENAME:
  Framework says: llm_responses/opus_4_6.json
  Actual filename: llm_responses/claude_opus_4_6.json

CORRECTION 2 — COMMAND A DID NOT TIME OUT:
  PHASE_C_LESSONS.md claims "Command A timed out on every attempt" and "all books fell back to single-model mode." This is completely false.
  Reality: 0/73 books are single_model_fallback. All 73 have dual-model consensus.
  67 books used Opus + Command A. 6 books used Opus + GPT-5.4.
  The 6 GPT-5.4 books: أبنية الأسماء والأفعال والمصادر, أنوار الهلالين في التعقبات على الجلالين, الأذكار للنووي ت الأرنؤوط, المستدرك على مجموع الفتاوى, تفسير الطبري جامع البيان - ط دار التربية والتراث, حاشية العطار على شرح الجلال المحلي على جمع الجوامع.
  Framework Section 7 (Single-Model Fallback Assessment) does NOT apply. Skip it entirely.

CORRECTION 3 — AUTHOR CONFIDENCE IN result.json IS BROKEN:
  result["author"]["confidence"] is ALWAYS 1.0 for every success book. This is an engine bug — it's the scholar registry's "new record" score, not the LLM's identification confidence.
  The real author confidence is ONLY in: llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence
  Observed range: 0.55 (الورقة النحوية) to 0.99 (famous books).

CORRECTION 4 — SECOND MODEL VARIES:
  Check ls llm_responses/ for each book. The second model is either command_a.json (67 books) or gpt_5_4.json (6 books). Read whichever exists.

CORRECTION 5 — VERIFIED THRESHOLD:
  Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) all derive from the same underlying database. They count as ONE source collectively, not multiple independent sources.
  VERIFIED requires 2+ genuinely independent sources. Independent means: Wikipedia Arabic, academic catalogs, university syllabi, publisher sites, or non-Shamela Islamic library sites.
  When only Shamela-ecosystem sources confirm a book, the ceiling is PLAUSIBLE.

CORRECTION 6 — TAHQIQ-AS-LAYER SYSTEMATIC BIAS:
  Opus classifies tahqiq (critical edition) notes as a multi-layer structure (matn + tahqiq_note) for 3 non-commentary books. Command A says ML=false for all 3. The framework expects false.
  When you see ML=true with layer_type="tahqiq_note" on a non-sharh/non-hashiyah book, FLAG it — this is a known Opus bias.
  The 11 sharh and 4 hashiyah ML=true classifications ARE correct.

CORRECTION 7 — CONSENSUS DOES NOT CHECK MULTI-LAYER:
  consensus.agreed=true only means author + work agreement. Models can disagree on is_multi_layer and still show agreed=true. Always compare ML between both models yourself.
</critical_corrections>

<methodology_fixes>
Session 1 self-review identified weaknesses. APPLY these fixes in Session 2:

FIX 1 — SEARCH BEFORE WRITING: Do web search for EVERY book BEFORE writing its verdict. Never skip. Never say "universally known."

FIX 2 — USE web_fetch: For at least 1 URL per book, actually fetch the page content. Search snippets are often insufficient for genre verification.

FIX 3 — SHAMELA CATEGORY CROSS-CHECK: For every book, compare extraction.json shamela_category against pipeline genre. Note agreement or disagreement in the verdict. When they disagree, investigate which is correct.

FIX 4 — DEATH DATE PASS-THROUGH VS INFERENCE: Check whether extraction.json already had the death date. If yes, the LLM is parroting — low diagnostic value for calibration. If no, the LLM is genuinely inferring — high diagnostic value. Mark which case applies in each verdict.

FIX 5 — RESULT.JSON MODEL SOURCE: For every success book, check which model "won" (higher author confidence) and whether result.json fields come from Opus or the second model.

FIX 6 — CONSISTENCY SELF-CHECK: At session end, do a SEPARATE pass reviewing all verdicts together. Don't just check inline while writing.
</methodology_fixes>

<session_2_books>
8 books — Famous Works A:

1. حاشية ابن عابدين = رد المحتار - ط الحلبي
2. لسان العرب
3. سير أعلام النبلاء - ط الحديث
4. فتح الباري بشرح البخاري - ط السلفية
5. بداية المجتهد ونهاية المقتصد
6. الموسوعة الفقهية الكويتية
7. مسند أحمد - ت شاكر - ط دار الحديث
8. زاد المستقنع في اختصار المقنع - ت العسكر
</session_2_books>

<pre_identified_risks>
From the strategic analysis, these Session 2 books have pre-identified concerns:

- مسند أحمد: HIGH RISK — ML disagreement (Opus=true with tahqiq_note, CA=false). Known tahqiq-as-layer bias. Expected: ML=false.
- فتح الباري بشرح البخاري: tahqiq-as-layer bias possible. Check layers carefully.
- حاشية ابن عابدين: REAL death date inference (extraction had no death date, Opus inferred 1252). Verify independently — this is a genuine calibration data point.
- بداية المجتهد: REAL death date inference (extraction had no death date, Opus inferred 595). Verify independently.
- الموسوعة الفقهية الكويتية: Institutional author (وزارة الأوقاف). Unusual case — no death date, no individual author.
</pre_identified_risks>

<corrected_per_book_workflow>
For EVERY book, follow this exact sequence. Do not skip steps or reorder them.

STEP 1 — Identify book status and model pair:
  cat {book}/result.json | check status (success or gate_abort)
  ls {book}/llm_responses/ | note filenames (claude_opus_4_6.json + command_a.json or gpt_5_4.json)

STEP 2 — Check extraction quality FIRST (before looking at LLM output):
  Read {book}/extraction.json:
    - author_name_raw: is it present and plausible?
    - _quality_issues: any flags?
    - muhaqiq_name_raw: present or null?
    - display_title: matches directory name?
    - shamela_category: note for cross-check against pipeline genre (FIX 3)
    - author_death_hijri: present or null? If present, LLM will parrot it (FIX 4)
  Read {book}/prompt_sent.json:
    - metadata_fields_present vs metadata_fields_absent: how much context did the LLM have?

STEP 3 — Extract pipeline values:
  For SUCCESS books: read fields from result.json (genre, science_scope, is_multi_layer, trust_tier, attribution_status, structural_format, author.name_arabic)
    EXCEPT author confidence — read that from llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence
    AND death_date_hijri — always from llm_responses/claude_opus_4_6.json → parsed.author_identification.death_date_hijri
    NOTE: result.json may reflect COMMAND A's values when CA had higher author confidence. Check which model won (FIX 5).
  For GATE_ABORT books: read ALL classification fields from llm_responses/claude_opus_4_6.json → parsed.*
    Trust tier: NOT AVAILABLE for gate_abort books — skip it.
  Also read the second model (command_a.json or gpt_5_4.json) for comparison.

STEP 4 — Check consensus:
  Read {book}/consensus.json: agreed (bool), successful_models (list)
  If agreed=false, compare the two models' outputs on genre, author, multi-layer. Note the specific disagreement.
  IMPORTANT: Even if agreed=true, compare is_multi_layer between both models — consensus does NOT check ML (Correction 7).

STEP 5 — Independent web verification (MANDATORY — do not skip):
  Search for the book title + author in Arabic. Use web_fetch on at least one URL (FIX 2).
  For author: confirm name and death date from 2+ sources.
  For genre: cross-check against shamela_category (FIX 3). Prefer title analysis and non-Shamela sources.
  List the specific URLs you visited in your verdict.

STEP 6 — Produce structured verdict:
  Use this exact format:

  Book: [Arabic name]
  Status: success | gate_abort
  Models: [opus + command_a | opus + gpt_5_4]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value] / Death source: [pass-through | inferred]
  Genre: [verdict] — Pipeline: [value] / Expected: [value] / Shamela cat: [value] / Agreement: [yes | no — explain]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value] / Model agreement: [yes | no]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Trust: [verdict] — Pipeline: [value] (or SKIPPED for gate_abort)
  Consensus: agreed=[bool], models=[list], disagreement=[if any]
  Extraction quality: [clean | issues noted]
  Result.json model source: [opus | command_a] (success books only)
  Web Sources: [specific URLs visited, with at least 1 fetched]
  Notes: [anything notable]
</corrected_per_book_workflow>

<task>
Clone the repo. Read these files in this order:
1. NEXT.md — current status and Session 2 specifics
2. PHASE_C_EVALUATION_FRAMEWORK.md — the full protocol (but remember the corrections above override it)
3. PHASE_C_ERRATA.md — detailed correction document
4. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md — predictions to test against

HELPER TOOL: python3 read_book.py "book_directory_name" reads all data for any book.

Then evaluate all 8 Session 2 books. For each book, follow the corrected per-book workflow above exactly. Produce the structured verdict for each book. Report the batch when Session 2 is complete.

After completing all 8 verdicts, do a separate consistency self-check pass (FIX 6).
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip web search for any book — training data alone is insufficient
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — all LLM data is captured
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated, STOP and tell me rather than degrading quality silently
</guardrails>
