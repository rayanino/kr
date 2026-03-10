Phase C calibration is done. You are continuing evaluation work that a previous Claude Chat session started. That session evaluated 3 books (calibration), found critical bugs in the documentation and engine, committed fixes to the repo, and established the corrected protocol for evaluating all remaining books.

Your job: evaluate Phase C pipeline results for 70 remaining books across Sessions 1–7, following the protocol below.

<what_was_done>
A previous session (Session 0 — Calibration) completed Phase 1:
- Read the full evaluation framework (PHASE_C_EVALUATION_FRAMEWORK.md, 632 lines)
- Verified the Phase C run: 73 book directories, 22 success, 51 gate_abort, 0 errors
- Evaluated 3 calibration books with full web search verification
- Discovered 4 engine bugs and 3 factual errors in LESSONS.md
- Committed PHASE_C_ERRATA.md and PHASE_C_CALIBRATION_BUGS.md to the repo
- Updated NEXT.md

The 3 calibration verdicts (include these in final aggregation):

1. أحكام الاضطباع والرمل في الطواف — success — PLAUSIBLE
   Author: عبد الله بن إبراهيم الزاحم (no death date). Opus conf: 0.72. Modern academic, obscure.
   Genre: risalah ✓. ML: false ✓. Science: ["fiqh"] ✓. Trust: flagged ✓. Consensus: agreed.

2. الأربعون النووية — gate_abort — VERIFIED
   Author: النووي (ت 676هـ). Opus conf: 0.99. Both models agree.
   Genre: hadith_collection ✓. ML: false ✓. Science: PLAUSIBLE (Opus overly broad).
   Sources: ar.wikipedia.org, noor-book.com, shamela.ws/book/12836

3. مجموع الفتاوى — gate_abort — VERIFIED
   Author: ابن تيمية (ت 728هـ), NOT ابن القاسم (compiler). Opus conf: 0.99. Both models agree.
   Genre: fatawa ✓. ML: false ✓. Science: PLAUSIBLE (broad superset of 37-vol scope).
   Sources: ketabonline.com/ar/books/5564, ar.wikipedia.org, goodreads, archive.org
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
  Read {book}/prompt_sent.json:
    - metadata_fields_present vs metadata_fields_absent: how much context did the LLM have?
  This tells you whether extraction was clean or garbled BEFORE you see what the LLM did with it.

STEP 3 — Extract pipeline values:
  For SUCCESS books: read fields from result.json (genre, science_scope, is_multi_layer, trust_tier, attribution_status, structural_format, author.name_arabic)
    EXCEPT author confidence — read that from llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence
    AND death_date_hijri — always from llm_responses/claude_opus_4_6.json → parsed.author_identification.death_date_hijri
    NOTE: result.json may reflect COMMAND A's values, not Opus's, when Command A had higher author confidence (3 books). If result.json genre differs from Opus genre, check Command A — result.json uses the canonical (winning) model's output. This is correct behavior, not a bug.
  For GATE_ABORT books: read ALL classification fields from llm_responses/claude_opus_4_6.json → parsed.*
    Trust tier: NOT AVAILABLE for gate_abort books — skip it.
  Also read the second model (command_a.json or gpt_5_4.json) for comparison.

STEP 4 — Check consensus:
  Read {book}/consensus.json: agreed (bool), successful_models (list)
  If agreed=false, compare the two models' outputs on genre, author, multi-layer. Note the specific disagreement.
  IMPORTANT: Even if agreed=true, compare is_multi_layer between both models — consensus does NOT check ML (Correction 7).

STEP 5 — Independent web verification (MANDATORY — do not skip):
  Search for the book title + author in Arabic. Visit at least one actual URL.
  For author: confirm name and death date from 2+ sources.
  For genre: prefer title analysis (شرح→sharh, حاشية→hashiyah) and non-Shamela sources.
  List the specific URLs you visited in your verdict.

STEP 6 — Produce structured verdict:
  Use this exact format:

  Book: [Arabic name]
  Status: success | gate_abort
  Models: [opus + command_a | opus + gpt_5_4]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value]
  Genre: [verdict] — Pipeline: [value] / Expected: [value]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Trust: [verdict] — Pipeline: [value] (or SKIPPED for gate_abort)
  Consensus: agreed=[bool], models=[list], disagreement=[if any]
  Extraction quality: [clean | issues noted]
  Web Sources: [specific URLs visited]
  Notes: [anything notable — poor extraction, interesting finding, etc.]
</corrected_per_book_workflow>

<worked_example>
Here is exactly what evaluating a gate_abort fixture book looks like. Pattern-match against this.

Book: أخبار أبي القاسم الزجاجي (fixture 01_nahw_simple, gate_abort, Opus + Command A)

```bash
# STEP 1: Status and models
cd /home/claude/kr/tests/results/source_engine/phase_c
python3 -c "import json; r=json.load(open('أخبار أبي القاسم الزجاجي/result.json')); print('status:', r['status'])"
ls "أخبار أبي القاسم الزجاجي/llm_responses/"

# STEP 2: Extraction quality
python3 -c "
import json
e=json.load(open('أخبار أبي القاسم الزجاجي/extraction.json'))
print('author_raw:', e.get('author_name_raw'))
print('quality_issues:', e.get('_quality_issues'))
print('display_title:', e.get('display_title'))
p=json.load(open('أخبار أبي القاسم الزجاجي/prompt_sent.json'))
print('fields_present:', p.get('metadata_fields_present'))
print('fields_absent:', p.get('metadata_fields_absent'))
"

# STEP 3: Pipeline values (gate_abort → read from llm_responses/)
python3 -c "
import json
opus=json.load(open('أخبار أبي القاسم الزجاجي/llm_responses/claude_opus_4_6.json'))
p=opus['parsed']; ai=p['author_identification']
print('genre:', p['genre'], '| conf:', p['genre_confidence'])
print('author:', ai['canonical_name_ar'], '| conf:', p['author_identification_confidence'])
print('death:', ai['death_date_hijri'])
print('ML:', p['is_multi_layer'], '| science:', p['science_scope'])
print('attribution:', p['attribution_status'])
# Also check second model
ca=json.load(open('أخبار أبي القاسم الزجاجي/llm_responses/command_a.json'))
cp=ca['parsed']; cai=cp['author_identification']
print('--- Command A ---')
print('genre:', cp['genre'], '| author:', cai['canonical_name_ar'], '| death:', cai['death_date_hijri'])
"

# STEP 4: Consensus
python3 -c "
import json
c=json.load(open('أخبار أبي القاسم الزجاجي/consensus.json'))
print('agreed:', c['agreed'], '| models:', c['successful_models'])
"

# STEP 5: Web search (mandatory)
# → Search "أخبار أبي القاسم الزجاجي" + author name
# → Visit at least one URL, note it in verdict

# STEP 6: Verdict (see format above)
```

This is the exact pattern. Every book follows this. For success books, Step 3 reads from result.json instead (except author confidence and death date, which always come from llm_responses/).
</worked_example>

<session_plan>
Start with Session 1: Fixture Regression. Then proceed through Sessions 2–7 in order.
If context gets long and you notice quality degrading, STOP and tell me — we'll continue in a fresh chat.
Report after each session batch.

Session 1 — Fixture Regression (11 remaining books):
  14 GROUND_TRUTH.json entries exist. 12 are present in Phase C (2 absent: 13_format_b, alfiyyah_versified). 1 was evaluated in calibration (أحكام الاضطباع). 11 remain.
  Note: أحاديث أيوب السختيانى IS fixture 04_hadith — the GT comparison failed because the GT title ("جزء فيه من أحاديث الإمام أيوب السختياني") doesn't match the directory name.
  4 of the 11 remaining have ground_truth_comparison.json:
    - أساليب بلاغية (success, mismatch: level only)
    - أسلوب خطبة الجمعة (success, mismatch: level only)
    - البدر التمام (success, mismatch: level only)
    - مذكرات مالك بن نبي (success, all_match: true)
    For these 4: read the GT comparison, confirm it, then do a quick web check to assign overall verdict.
  The other 7 need full manual evaluation:
    - آداب الصحبة لأبي عبد الرحمن السلمي (gate_abort)
    - آداب الفتوى والمفتي والمستفتي (gate_abort)
    - أبنية الأسماء والأفعال والمصادر (gate_abort, uses GPT-5.4, consensus DISAGREED)
    - أحاديث أيوب السختيانى (gate_abort — this IS fixture 04_hadith, GT comparison missing due to title mismatch)
    - أنوار الهلالين في التعقبات على الجلالين (gate_abort, uses GPT-5.4)
    - أخبار أبي القاسم الزجاجي (gate_abort)
    - همع الهوامع في شرح جمع الجوامع (gate_abort, fixture 11_multi_small, no GT comparison file)
  That makes 7 full evaluations + 4 GT-assisted = 11 total.

Sessions 2–7 follow the framework's session assignments (read PHASE_C_EVALUATION_FRAMEWORK.md for book lists).
After all sessions, produce the final aggregation per the framework's aggregation template.
</session_plan>

<task>
Clone the repo. Read these files in this order:
1. PHASE_C_EVALUATION_FRAMEWORK.md — the full protocol (but remember the corrections above override it)
2. PHASE_C_ERRATA.md — detailed correction document committed by the calibration session
3. PHASE_C_CALIBRATION_BUGS.md — engine bugs found, with workarounds

HELPER TOOL: A script `read_book.py` in the repo root reads all data for any book in one command:
  python3 read_book.py "book_directory_name"
It outputs extraction, both models, consensus, and result.json in the corrected evaluation order. Use it as Step 1-4 of the workflow, then do Steps 5-6 (web search + verdict) yourself.

Then begin Session 1 evaluation. For each book, follow the corrected per-book workflow above exactly. Produce the structured verdict for each book. Report the batch when Session 1 is complete.
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip web search for any book — training data alone is insufficient (circular verification risk)
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — it's a calibration issue, all LLM data is captured
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated, STOP and tell me rather than degrading quality silently
</guardrails>
