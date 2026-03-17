<project_state>
Step 4 of source engine validation. 204 books ran through the pipeline (100% success). Programmatic validation (Layer 1), pattern analysis (Layer 2), and consensus disagreement review (Session A) are COMPLETE. Per-book evaluation continues with Sessions B, C, D, then Layer 4 aggregation.
</project_state>

<task>
You are continuing the Phase D evaluation of the KR source engine. Your job is to verify that the pipeline's metadata classifications (author, genre, multi-layer, science scope, trust) are factually correct — by independently researching each book and comparing against the pipeline's output.

Sessions completed by prior conversations:
- Layer 2: PHASE_D_PATTERN_ANALYSIS.md (committed)
- Session A: PHASE_D_SESSION_A_REPORT.md (committed, 14 books: 8V/5P/1F, ERR-02 confirmed)

Sessions remaining (do them IN ORDER, as many as you can at full quality):
- Session B: 19 author uncertainty books → PHASE_D_SESSION_B_REPORT.md
- Session C: 15 structural flag books → PHASE_D_SESSION_C_REPORT.md
- Session D: 12 random calibration books → PHASE_D_SESSION_D_REPORT.md
- Layer 4: aggregation across all sessions → PHASE_D_AGGREGATION_REPORT.md (only after ALL sessions complete)
</task>

<reading_order>
Before evaluating ANY book, read these files in this exact order:
1. `NEXT.md` — current state, completed vs pending sessions
2. `PHASE_D_EVALUATION_PROTOCOL.md` — complete methodology: verdict format (14 fields), field source rules, web search strategy, anti-patterns, known biases
3. `PHASE_D_SESSION_ERRATA.md` — **CRITICAL: 7 lessons from Session A mistakes. Read every word. These are mandatory rules, not suggestions.**
4. `EVALUATION_QUICK_REFERENCE.md` — compact per-book checklist (re-read before EACH book)
5. `PHASE_D_PROGRAMMATIC_ANALYSIS.md` — Layer 1 deep analysis: genre patterns, ML bias, trust root causes, specific errors
6. `PHASE_D_SESSION_A_REPORT.md` — prior session results (skim for patterns, don't re-evaluate these books)
7. `tests/results/source_engine/phase_d/PHASE_D_TRIAGE.json` — every book's session allocation
</reading_order>

<errata_summary>
Session A's critical self-review found 7 errors that MUST NOT be repeated. The full details are in PHASE_D_SESSION_ERRATA.md, but here are the rules distilled:

1. **web_fetch is MANDATORY.** For every book, after web_search, you MUST call web_fetch on at least one URL. Search snippets alone are insufficient for verdicts. If web_fetch fails on one URL, try another.

2. **Never fabricate sources.** Only cite sources that appeared in your actual search results or that you fetched. If you didn't find it, don't write "archive.org confirms" or "Wikipedia confirms."

3. **Death date labels must be precise.** Three categories:
   - "pass-through" = structured field `author_death_hijri` exists in extraction.json
   - "extracted from raw text" = no structured field, but date is embedded in `author_name_raw` (e.g., "(ت 751 هـ)")
   - "inferred" = no date anywhere in extraction; LLM supplied it from domain knowledge
   Check extraction.json for each book to determine which category applies.

4. **Self-review must use tools, not re-read text.** When verifying "did I call web_fetch?", check the actual conversation history, don't just re-read your report.

5. **Mark speculation as speculation.** When describing how engine internals work without reading the code, write "inferred from behavior" not "the mechanism is..."

6. **Check prompt_sent.json** for metadata_fields_present and metadata_fields_absent. Especially important when extraction is sparse.

7. **Check for pipeline-genre-matches-neither-model.** If result.json genre ≠ Opus genre AND ≠ CA genre, flag as a potential anomaly.
</errata_summary>

<per_book_procedure>
For EACH book, execute these steps in order. Do not skip or reorder.

Step 1 — Read pipeline data:
```
python3 read_book.py "{book_name}"
```
This outputs all fields in evaluation order. Note: status, model pair, extraction quality, author confidence (from llm_responses, NOT result.json).

Step 2 — Check extraction.json details:
Look at author_name_raw (does it contain death dates?), shamela_category, muhaqiq, quality_issues. Check whether extraction has a structured author_death_hijri field.

Step 3 — Check prompt_sent.json:
Note metadata_fields_present vs metadata_fields_absent. If key fields were absent, the LLM was working with less information.

Step 4 — Compare both models:
Check llm_responses/ for both models on: genre, ML, science_scope, attribution, layers, death_date, author_confidence. Note any disagreement. For ML disagreements, check if Opus has tahqiq_note layers (known bias).

Step 5 — Web search (BEFORE writing the verdict):
Minimum 1 search per book. Search strategy by book type:
- Famous classical works: `"{title}" {author}` — but VERIFY the snippet by fetching
- Obscure works: search shamela.ws, then author separately, then archive.org
- Modern works: author name + university/institution affiliation

Step 6 — web_fetch at least 1 URL:
Pick the most informative result from Step 5 and fetch it. Read the actual page content. This is not optional.

Step 7 — Write the structured 14-field verdict:
Use the exact format from PHASE_D_EVALUATION_PROTOCOL.md. Mark death date source precisely (pass-through / extracted from raw text / inferred).

Step 8 — Source independence check before assigning VERIFIED:
VERIFIED requires 2+ genuinely INDEPENDENT sources. shamela.ws + ketabonline.com + turath.io + waqfeya.net = ONE collective Shamela-ecosystem source. If you only have Shamela-ecosystem sources, the verdict is PLAUSIBLE, not VERIFIED — even for famous books.
</per_book_procedure>

<example_good_verdict>
Here is a correctly executed verdict showing all the requirements met:

### Book N: شرح النووي على مسلم

- **Status:** success
- **Pipeline author:** يحيى بن شرف بن مري النووي (d. 676 AH)
- **Author verdict:** VERIFIED
- **Author source:** ar.wikipedia.org (النووي article, fetched — confirms authorship and death date 676 AH), archive.org (full text available, independent). Shamela ecosystem also lists it. 2 independent + 1 ecosystem.
- **Pipeline genre:** sharh (0.95)
- **Genre verdict:** VERIFIED — universally classified as a sharh on Sahih Muslim.
- **Pipeline ML:** True (layers: matn صحيح مسلم, sharh النووي)
- **ML verdict:** VERIFIED — genuinely multi-layer: Muslim's hadith text (matn) + Nawawi's commentary (sharh). Both models agree.
- **Pipeline science:** ['hadith', 'ulum_al_hadith', 'fiqh']
- **Science verdict:** VERIFIED
- **Trust tier:** verified (0.78)
- **Death date:** 676 AH — pass-through from extraction (author_death_hijri=676 in extraction.json).
- **Model agreement:** Agreed on all fields.
- **Overall verdict:** VERIFIED
- **Notes:** No issues. prompt_sent.json shows all metadata fields present.
</example_good_verdict>

<session_specific_context>
**Session B (19 books) — Author Uncertainty:**
These books have no extracted author (pure LLM inference), low author confidence (<0.75), or death date disagreement. Pay special attention to:
- Whether the author name is genuinely verifiable or just plausible
- Whether low confidence reflects genuine uncertainty or just extraction sparseness
- Death date disagreements may indicate author misidentification (like ERR-02 in Session A)

**Session C (15 books) — Structural Flags:**
These include ML-affecting genre disagreements, genre-structure inconsistencies, and books needing layer verification. Key items:
- أمالي الأذكار في فضل صلاة التسبيح: Opus=sharh+ML=true, CA=hadith_collection+ML=false. Pipeline took Opus's side. Web-search to determine if genuinely multi-layer.
- النكت على شرح النووي (ERR-01): genre=hashiyah but ML=false. Web-search to determine correct genre.
- Several ML disagreement books where BUG-03 override fired — verify the override was correct.
- الإبانة عن أصول الديانة (2 editions): genuinely disputed attribution (Opus correctly flags "disputed")
- الرسالة للشافعي, مختصر صحيح مسلم, مسند أحمد: Phase C books now with BUG-03 ML fix — verify improvement.

**Session D (12 books) — Random Calibration:**
Stratified random from the 82 unflagged books. Primary purpose: detect unknown systematic biases (especially Opus biases, since Opus is canonical ~90% of the time). If ANY error is found in the random sample, flag that the sample should be expanded.
</session_specific_context>

<quality_requirements>
- Web search + web_fetch is MANDATORY for every per-book verdict. No exceptions.
- Use the verdict scale exactly: VERIFIED (2+ independent sources), PLAUSIBLE (1 source or extraction cross-check), UNVERIFIABLE (no sources found), FLAG (evidence suggests error), ESCALATE (cannot resolve).
- Author confidence must be read from llm_responses/, NOT result.json (result.json has BUG-02: always 1.0).
- Shamela-ecosystem sources count as ONE collective source.
- Scholar canonical IDs (sch_00001) are NOT consistent across books — compare by name, never by ID.
- After completing your books, run 4 self-review rounds. Round 3 must verify web_fetch was actually called (check your conversation, don't just re-read the report).
- If you find ANY error in Session D's random sample, flag that the sample should be expanded.
</quality_requirements>

<session_outputs>
Each session produces a report file committed to the repo:
- Session B: `PHASE_D_SESSION_B_REPORT.md`
- Session C: `PHASE_D_SESSION_C_REPORT.md`
- Session D: `PHASE_D_SESSION_D_REPORT.md`
- Layer 4: `PHASE_D_AGGREGATION_REPORT.md`

After committing each report, update NEXT.md: mark completed sessions, note totals, flag findings that affect subsequent sessions.

**Partial work is fine.** If you run out of context mid-session, commit whatever verdicts you have, mark which books remain, and the next conversation picks up. Quality over quantity — 8 rigorous verdicts beat 15 sloppy ones.

**Git operations:** Configure git, commit, and push after each completed session. Don't wait until the end.
</session_outputs>

<constraints>
- Do NOT skip web_fetch to save time or context. This was the biggest error in Session A.
- Do NOT invent verdict categories beyond the 5 defined.
- Do NOT treat the programmatic triage as verdicts — it identified WHICH books to review, not WHETHER they are correct.
- Do NOT assume Phase C verdicts carry forward without checking — the pipeline version changed.
- Do NOT describe engine mechanisms without reading the code — mark behavioral inferences as such.
- Mark genuine uncertainty as UNVERIFIABLE, not as a guess. The owner makes decisions based on your verdicts.
</constraints>

Work step by step. Take all your time. Depth and accuracy over speed.
