Phase C calibration, Sessions 1–5 are done. You are continuing evaluation work that previous Claude Chat sessions completed.

Your job: evaluate Phase C pipeline results for Session 6 (Edition Groups — 17 books), following the protocol below.

<what_was_done>
Session 0 (Calibration) evaluated 3 books, found 4 engine bugs, committed corrections.
Session 1 (Fixture Regression) evaluated 11 books (14 total with calibration).
Session 2 (Famous Works A) evaluated 8 books — all 8 VERIFIED (1 with ML field-level flag on مسند أحمد).
Session 3 (Famous Works B) evaluated 7 books — all 7 VERIFIED (1 with ML field-level flag on الرسالة).
Session 4 (Multi-Layer + Commentary) evaluated 10 books — 9 VERIFIED + 1 PLAUSIBLE (التعليق على الرحيق المختوم).
Session 5 (Attribution + Trust + Obscure) evaluated 10 books — 4 VERIFIED + 6 PLAUSIBLE.

Running totals: 38 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (49 books evaluated).

Prior reports are in the repo:
- PHASE_C_SESSION1_REPORT.md
- PHASE_C_SESSION1_DEEP_ANALYSIS.md
- PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md
- PHASE_C_SESSION2_REPORT.md
- PHASE_C_SESSION3_REPORT.md
- PHASE_C_SESSION4_REPORT.md
- PHASE_C_SESSION5_REPORT.md
</what_was_done>

<critical_corrections>
The evaluation framework (PHASE_C_EVALUATION_FRAMEWORK.md) has errors discovered during calibration. These corrections OVERRIDE the framework wherever they conflict:

CORRECTION 1 — LLM FILENAME:
  Framework says: llm_responses/opus_4_6.json
  Actual filename: llm_responses/claude_opus_4_6.json

CORRECTION 2 — COMMAND A DID NOT TIME OUT:
  0/73 books are single_model_fallback. All 73 have dual-model consensus.
  16/17 Session 6 books use Opus + Command A. 1 book uses Opus + GPT-5.4.
  Framework Section 7 (Single-Model Fallback Assessment) does NOT apply. Skip it entirely.

CORRECTION 3 — AUTHOR CONFIDENCE IN result.json IS BROKEN:
  result["author"]["confidence"] is ALWAYS 1.0 for every success book. This is an engine bug.
  The real author confidence is ONLY in: llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence

CORRECTION 4 — SECOND MODEL:
  16/17 Session 6 books use command_a.json as the second model.
  1 book (تفسير الطبري جامع البيان - ط دار التربية والتراث) uses gpt_5_4.json.

CORRECTION 5 — VERIFIED THRESHOLD:
  Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) all derive from the same underlying database. They count as ONE source collectively, not multiple independent sources.
  VERIFIED requires 2+ genuinely independent sources. Independent means: Wikipedia Arabic, academic catalogs, university syllabi, publisher sites, archive.org, noor-book.com, islamway.net, alukah.net, government sites, or non-Shamela Islamic library sites.

CORRECTION 6 — CONSENSUS DOES NOT CHECK MULTI-LAYER OR ATTRIBUTION:
  consensus.agreed=true only means author + work agreement. Models can disagree on is_multi_layer, attribution_status, and authority_level and still show agreed=true. Always compare these fields between both models yourself.
  Session 6 specific: 1 book has ML disagreement (تفسير الطبري ط دار التربية — Opus=F, GPT-5.4=T). 4 books have consensus.agreed=false (see session_6_books table).
</critical_corrections>

<session_5_findings_carry_forward>
These findings from Sessions 2-5 affect how you evaluate Session 6 books:

1. Zero author identification errors across 49 books evaluated. The pipeline's author identification is the strongest field.

2. Opus attribution taxonomy confirmed: "definitive" for famous well-established works, "traditional" for conventionally-attributed works, "disputed" for genuinely contested works. CA tends toward "definitive" even for traditionally-attributed works. Session 6 has no disputed-attribution books.

3. Opus genre=hashiyah contradiction: Opus can label a book "hashiyah" when only 2 layers exist (should require 3). Watch for this on the 2 hashiyah books (حاشية ابن عابدين, تكملة حاشية). Verify that the layer chain actually has 3 distinct layers with 3 distinct authors.

4. Tahqiq_note ML=true pattern: 3 confirmed instances (Errata §9: الرسالة, مختصر صحيح مسلم, مسند أحمد). Session 6 has 1 new instance: تفسير الطبري ط دار التربية (GPT-5.4 says ML=true with tahqiq_note layer). Cumulative: 4 instances. Do NOT treat tahqiq_note as a correct multi-layer classification — it is editorial apparatus, not a scholarly commentary layer.

5. Death date genuine inference running total: 2 confirmed correct (مجموع الفتاوى 728, الإبانة ت العصيمي 324), 1 confirmed wrong (أساليب بلاغية 1432 vs actual 1439), 6 confirmed false positives (dates embedded in author_name_raw). Session 6 has 1 new genuine inference (تكملة حاشية 1306) and 2 new false positives (أعلام ط عطاءات 751, تحفة ط عطاءات 751 — "691 - 751" is embedded in author_raw).

6. Authority_level disagreements: Session 4 had 6/10 (Opus=reference vs CA=primary on sharh works). Session 5 had 0/10 (no sharh works). Session 6 has 4 sharh/hashiyah works — check for this pattern.

7. Cross-edition genre inconsistency: الإبانة had risalah vs matn across 2 editions in Session 5. إعلام الموقعين in Session 6 has the worst genre scatter: matn vs other vs usul_al_fiqh across 3 editions.

8. web_fetch compliance: Session 4: 0/10. Session 5: 1/10. Aim for at least 3/17 in Session 6 — prioritize the critical-risk books.
</session_5_findings_carry_forward>

<session_6_books>
17 books — Edition Groups. **This is the largest session.**

The PRIMARY question for Session 6 is **cross-edition consistency**, not individual identification (which was tested in Sessions 2-5). For each edition group: do author, genre, ML, and science match across editions? Document inconsistencies.

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| **إعلام الموقعين (3 editions)** |||||
| 1 | أعلام الموقعين عن رب العالمين - ط عطاءات العلم | gate_abort | opus + command_a | matn | F | **Consensus DISAGREED** (genre + name format) |
| 2 | إعلام الموقعين عن رب العالمين - ت مشهور | gate_abort | opus + command_a | other | F | Consensus DISAGREED (name format only) |
| 3 | إعلام الموقعين عن رب العالمين - ط العلمية | gate_abort | opus + command_a | other | F | — |
| **البداية والنهاية (2 editions)** |||||
| 4 | البداية والنهاية - ت التركي | **success** | opus + command_a | tarikh | F | trust=verified |
| 5 | البداية والنهاية - ط السعادة | **success** | opus + command_a | tarikh | F | trust=verified |
| **تفسير الطبري (2 editions)** |||||
| 6 | تفسير الطبري جامع البيان - ت التركي | gate_abort | opus + command_a | tafsir | F | — |
| 7 | تفسير الطبري جامع البيان - ط دار التربية والتراث | gate_abort | opus + **GPT-5.4** | tafsir | **F/T disagree** | **ML disagreement: Opus=F, GPT-5.4=T (tahqiq_note)** |
| **تحفة المودود (2 editions)** |||||
| 8 | تحفة المودود بأحكام المولود - ت الأرنؤوط | gate_abort | opus + command_a | risalah | F | — |
| 9 | تحفة المودود بأحكام المولود - ط عطاءات العلم | gate_abort | opus + command_a | risalah | F | **Consensus DISAGREED** (name format only) |
| **فتاوى اللجنة الدائمة (2 editions)** |||||
| 10 | فتاوى اللجنة الدائمة - المجموعة الأولى | **success** | opus + command_a | fatawa | F | Institutional author, no death date |
| 11 | فتاوى اللجنة الدائمة - المجموعة الثانية | gate_abort | opus + command_a | fatawa | F | Institutional author, science scope broader |
| **ألفية ابن مالك (2 editions)** |||||
| 12 | ألفية ابن مالك - ت القاسم | **success** | opus + command_a | nazm | F | genre=nazm (not matn) — verify |
| 13 | ألفية ابن مالك - ط التعاون | gate_abort | opus + command_a | nazm | F | — |
| **شرح العقيدة الطحاوية (2 editions)** |||||
| 14 | شرح العقيدة الطحاوية - ط الأوقاف السعودية - بتعليقات أحمد شاكر | gate_abort | opus + command_a | sharh | T | Cross-check with Session 4 |
| 15 | شرح العقيدة الطحاوية - ط الرسالة | gate_abort | opus + command_a | sharh | T | **Already evaluated Session 4: VERIFIED** |
| **حاشية ابن عابدين + تكملة (author verification pair — NOT an edition group)** |||||
| 16 | حاشية ابن عابدين = رد المحتار - ط الحلبي | gate_abort | opus + command_a | hashiyah | T | FATHER: ابن عابدين (ت 1252) |
| 17 | تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد المحتار - ط الفكر | gate_abort | opus + command_a | hashiyah | T | **SON: علاء الدين (ت ~1306); consensus DISAGREED; death GENUINE INFERENCE; author_raw EMPTY** |

4 SUCCESS books (البداية ×2, فتاوى اللجنة الأولى, ألفية ت القاسم): check result.json for trust_tier, genre, model source.
13 GATE_ABORT books: get all classification data from llm_responses/, not result.json.
1 GPT-5.4 book (تفسير الطبري ط دار التربية). All others use Command A.
4 consensus-DISAGREED books (from Errata §6): أعلام ط عطاءات, إعلام ت مشهور, تحفة ط عطاءات, تكملة حاشية.
</session_6_books>

<pre_identified_risks>
From NEXT.md and pipeline data pre-scan:

CRITICAL PRIORITY:
- تكملة حاشية ابن عابدين: author_raw is EMPTY. Death 1306 is a GENUINE INFERENCE (Opus only — CA gives null). Consensus DISAGREED. Must be the SON (علاء الدين), NOT the father (محمد أمين ت 1252). Cross-check with Book 16 to confirm different authors.
- إعلام الموقعين: worst cross-edition genre scatter in the corpus. 3 editions → 3 different genres (matn, other, usul_al_fiqh). ML=false for all 3 ✓ (CRITICAL framework check). Author=ابن القيم for all 3 ✓.
- تفسير الطبري ط دار التربية: ML disagreement (Opus=F, GPT-5.4=T with tahqiq_note). 4th tahqiq_note instance. Other edition (ت التركي) has ML=false from both models.

HIGH PRIORITY:
- شرح العقيدة الطحاوية: cross-session check with Session 4 verdict (VERIFIED: ابن أبي العز ت 792, sharh, ML=true, aqidah, Opus=traditional/CA=definitive). Verify ط الأوقاف matches.
- حاشية ابن عابدين: 3-layer hashiyah. Verify layer chain: تنوير الأبصار (matn, التمرتاشي ت 1004) → الدر المختار (sharh, الحصكفي ت 1088) → رد المحتار (hashiyah, ابن عابدين ت 1252). Death 1252: embedded in author_raw as "ت 1252 هـ" — false positive inference.
- Death dates for ابن القيم ط عطاءات editions: extraction death=None but "691 - 751" embedded in author_raw. These are FALSE POSITIVES, not genuine inferences.

MEDIUM PRIORITY:
- البداية والنهاية: MUST be tarikh, NOT tafsir. Pre-scan: clean ✓.
- ألفية ابن مالك: genre=nazm (more precise than matn for versified grammar). Pre-scan: clean ✓.
- فتاوى اللجنة الدائمة: institutional author (اللجنة الدائمة), no death date. Science scope differs between editions.
</pre_identified_risks>

<edition_group_protocol>
This protocol is MANDATORY for every edition group (7 groups, 15 books). It replaces the individual deep-dive approach used in Sessions 2-5.

For EACH edition group:
1. Run read_book.py for EVERY edition in the group.
2. Create a comparison table with these fields: author, death, genre, ML, science, attribution. Mark each as MATCH or MISMATCH.
3. For MATCH fields: one web search per group (not per edition) confirms the shared value.
4. For MISMATCH fields: investigate which edition is correct (or whether both are acceptable).
5. Apply the Edition Group verdict: CONSISTENT (all mandatory fields match) or INCONSISTENT (at least one mandatory mismatch).
6. Each book still gets an individual VERIFIED/PLAUSIBLE/etc. verdict, but the edition group comparison is the primary analytical output.

Mandatory-match fields: author, genre, ML, science.
May-differ fields: muhaqiq, trust_tier, authority_level, confidence scores.

WORKED EXAMPLE — how to handle an edition group:

البداية والنهاية (2 editions):
| Field | ت التركي | ط السعادة | Match? |
|-------|----------|-----------|--------|
| Author | ابن كثير (ت 774) | ابن كثير (ت 774) | ✓ |
| Genre | tarikh | tarikh | ✓ |
| ML | false | false | ✓ |
| Science | ['tarikh', 'sirah'] (Opus) / ['tarikh'] (CA) | ['tarikh', 'sirah'] (Opus) / ['tarikh'] (CA) | ✓ |
Edition Group Verdict: CONSISTENT
Then: 1 web search confirms "البداية والنهاية ابن كثير tarikh" → both VERIFIED.

This is NOT a template to copy — it shows the comparison structure. Apply it to all 7 groups.
</edition_group_protocol>

<author_verification_protocol>
For Books 16-17 (حاشية ابن عابدين + تكملة), this is NOT an edition group — these are TWO DIFFERENT WORKS by TWO DIFFERENT AUTHORS (father and son).

1. Read both books' pipeline data.
2. Confirm Book 16 author = محمد أمين ابن عابدين (FATHER, ت 1252).
3. Confirm Book 17 author = علاء الدين ابن عابدين (SON, ت ~1306) — NOT the father.
4. Web search to verify both authors' identities and the father/son relationship.
5. For Book 17: note that author_raw is EMPTY (extraction failed), death 1306 is a GENUINE INFERENCE from Opus only, and consensus DISAGREED.
6. Each book gets its own independent verdict.
</author_verification_protocol>

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
  Compare Opus vs second model on: genre, author, death_date, ML, science_scope, attribution, authority_level.
  Note ALL disagreements.

STEP 4 — For edition groups: complete the comparison table BEFORE writing individual verdicts.

STEP 5 — Web search (BEFORE writing verdict) — at minimum 1 search per edition group.
  Use web_fetch on at least 1 URL for high-priority books.

STEP 6 — Check consensus:
  Read consensus.json: agreed (bool), successful_models.
  For the 4 DISAGREED books: note what specifically disagrees (from Errata §6).

STEP 7 — Produce structured verdict using this exact format:

  Book: [Arabic name]
  Status: [success | gate_abort]
  Models: [opus + command_a | opus + gpt_5_4]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value] / Death source: [pass-through | inferred | false-positive-inferred | absent]
  Genre: [verdict] — Pipeline: [value] / Expected: [value] / Shamela cat: [value] / Agreement: [yes | no — explain]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value] / Model agreement: [yes | no]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Attribution: [verdict] — Opus: [value] / CA: [value]
  Trust: [For success books] Pipeline: [value] / Score: [value]. [For gate_abort] SKIPPED (gate_abort)
  Consensus: agreed=[bool], models=[list]
  Extraction quality: [clean | issues noted — specify]
  Result.json model source: [For success books: which model's values appear] / N/A (gate_abort)
  Web Sources: [specific URLs visited, marking Shamela-ecosystem vs independent, note any fetched]
  Edition Group: [group name] / Consistency: [MATCH | MISMATCH on field X]
  Notes: [anything notable]
</corrected_per_book_workflow>

<after_all_verdicts>
After completing all 17 verdicts:

1. Edition Group Summary Table:
   For each of the 7 groups, one row: group name, # editions, mandatory fields match/mismatch, group verdict.

2. Consistency self-check (as a SEPARATE pass — not inline while writing):
   - Same standards applied to book 1 and book 17?
   - Source independence counts honest?
   - Shamela-ecosystem excluded everywhere?
   - Success books checked for trust + model source?

3. Confidence calibration section:
   - Table of all author/genre confidence scores
   - Any high-confidence + wrong cases?
   - Cross-edition confidence comparison: do the same work's editions get similar confidence?

4. Cross-book patterns:
   - Edition consistency: which groups are perfectly consistent? Which have mismatches?
   - Cross-session checks: شرح الطحاوية Session 4 vs Session 6, الإبانة Session 5 cross-edition findings
   - Death date inference: update running totals with new false positives + the تكملة genuine inference

5. Commit and push the report as PHASE_C_SESSION6_REPORT.md. Note: the owner will run 5 review rounds after this.
   - Rounds 1-4: Review the report (each round attacks from a different angle). The report is finalized after Round 4.
   - After Round 4: Write the handoff (NEXT.md) for Session 7 with pre-scanned pipeline data.
   - Round 5: Verify the handoff against pipeline data and governing documents. The final commit happens after Round 5.
</after_all_verdicts>

<task>
Clone the repo. Read these files in this order:
1. NEXT.md — current status and Session 6 specifics (DEEP READ — this is the primary handoff)
2. PHASE_C_ERRATA.md — corrections that override framework (DEEP READ — especially §6 on the 4 consensus-disagreed books, §9 on tahqiq_note)
3. PHASE_C_EVALUATION_FRAMEWORK.md — Edition Group Protocol + expected values table (READ these sections; SKIM the rest)
4. PHASE_C_SESSION4_REPORT.md — شرح العقيدة الطحاوية verdict (READ this specific verdict for cross-session check)
5. PHASE_C_SESSION5_REPORT.md — findings and cross-book patterns (READ findings section, SKIM per-book details)
6. EVALUATION_QUICK_REFERENCE.md — compact checklist (DEEP READ — re-read before EACH book)

HELPER TOOL: python3 read_book.py "book_directory_name" reads all data for any book.

Then evaluate all 17 Session 6 books. Process them BY EDITION GROUP:
1. إعلام الموقعين (3 editions) — highest risk, do first
2. حاشية + تكملة ابن عابدين (author verification pair) — critical risk
3. تفسير الطبري (2 editions) — ML disagreement
4. شرح العقيدة الطحاوية (2 editions) — cross-session check
5. البداية والنهاية (2 editions)
6. تحفة المودود (2 editions)
7. فتاوى اللجنة الدائمة (2 editions)
8. ألفية ابن مالك (2 editions)

For each group: read ALL editions first, build the comparison table, THEN write individual verdicts.

After book 10 or 11: pause and run the mid-session quality gate from EVALUATION_QUICK_REFERENCE.md.

After all 17 verdicts: produce the edition group summary, consistency self-check, confidence calibration, and cross-book patterns sections. Commit the report.
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip the edition group comparison table for ANY group — this is the primary analytical output
- Do NOT skip web search for any edition group — training data alone is insufficient
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — all LLM data is captured (13/17 books are gate_abort)
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- Do NOT classify death dates as "genuine inference" when embedded in author_name_raw — check the raw text
- Do NOT assume تكملة حاشية is the same author as حاشية — they are FATHER and SON
- Do NOT accept ML=true when the only layer is tahqiq_note — this is the known bias pattern
- Do NOT invent verdict categories — only VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- Do NOT treat شرح العقيدة الطحاوية ط الرسالة as a new evaluation — it was VERIFIED in Session 4. Confirm consistency with the new edition only.
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated, STOP and tell me rather than degrading quality silently
</guardrails>
