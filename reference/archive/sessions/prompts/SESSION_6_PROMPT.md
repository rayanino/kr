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
  1 book (تفسير الطبري جامع البيان - ط دار التربية والتراث) uses gpt_5_4.json as the second model.

CORRECTION 5 — VERIFIED THRESHOLD:
  Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) all derive from the same underlying database. They count as ONE source collectively, not multiple independent sources.
  VERIFIED requires 2+ genuinely independent sources. Independent means: Wikipedia Arabic, academic catalogs, university syllabi, publisher sites, archive.org, noor-book.com, islamway.net, alukah.net, government sites, or non-Shamela Islamic library sites.

CORRECTION 6 — CONSENSUS DOES NOT CHECK MULTI-LAYER OR ATTRIBUTION:
  consensus.agreed=true only means author + work agreement. Models can disagree on is_multi_layer, attribution_status, and authority_level and still show agreed=true. Always compare these fields between both models yourself.
  Session 6 specific: 1/17 books has an ML disagreement (تفسير الطبري ط دار التربية — Opus=F, GPT-5.4=T). You MUST catch this by comparing models manually.

CORRECTION 7 — CONSENSUS DISAGREEMENT DETAILS (Errata §6):
  4/17 Session 6 books have consensus.agreed=false:
  - أعلام الموقعين ط عطاءات العلم: Genre (matn vs usul_al_fiqh) + name format — partially substantive
  - إعلام الموقعين ت مشهور: Name format only (same person: ابن القيم) — not substantive
  - تحفة المودود ط عطاءات العلم: Name format only (same person: ابن القيم) — not substantive
  - تكملة حاشية ابن عابدين: Name format + death date (1306 vs null) — SUBSTANTIVE
</critical_corrections>

<session_5_findings_carry_forward>
These findings from Sessions 2-5 affect how you evaluate Session 6 books:

1. Zero author identification errors across 49 books evaluated. The pipeline's author identification is the strongest field.

2. Opus attribution taxonomy: "definitive" for famous well-established works, "traditional" for conventionally-attributed works, "disputed" for genuinely contested works. CA tends toward "definitive" even for traditional works.

3. Tahqiq_note ML=true pattern: Errata §9 documents 3 instances where a model classifies non-commentary books as multi-layer because of tahqiq notes (الرسالة, مختصر صحيح مسلم, مسند أحمد). Session 6 has 1 new instance: تفسير الطبري ط دار التربية (GPT-5.4 says ML=true with tahqiq_note layer). When a non-sharh/hashiyah book has ML=true with layer_type="tahqiq_note", note the known pattern — do NOT treat it as correct multi-layer classification.

4. Authority_level disagreements: Session 4 had 6/10 (Opus=reference vs CA=primary on sharh works). Session 5 had 0/10 (no sharh works). Session 6 has 4 sharh/hashiyah works (شرح الطحاوية ×2, حاشية ابن عابدين, تكملة حاشية) — check for this pattern on each.

5. Cross-edition genre inconsistency: Session 5 found risalah vs matn for الإبانة editions (same text, different genre labels). Session 6 will likely find similar patterns — the genre boundary between matn, risalah, and other is fuzzy for certain text types.

6. Death date genuine inference running total: 2 confirmed correct (مجموع الفتاوى 728, الإبانة ت العصيمي 324), 1 confirmed wrong (أساليب بلاغية 1432 vs actual 1439), 6 confirmed false positives (dates embedded in author_name_raw). Session 6 has 1 new genuine inference: تكملة حاشية ابن عابدين (1306 — empty author_raw, no death in extraction). Also 2 new false positives: أعلام ط عطاءات and تحفة ط عطاءات (both have "691 - 751" embedded in author_name_raw).

7. شرح العقيدة الطحاوية ط الرسالة was already evaluated in Session 4 as VERIFIED. Session 6 must cross-reference that verdict when evaluating the ط الأوقاف edition.
</session_5_findings_carry_forward>

<session_6_books>
17 books — Edition Groups. **This is the largest session.**

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| **إعلام الموقعين (3 editions)** |||||
| 1 | أعلام الموقعين عن رب العالمين - ط عطاءات العلم | gate_abort | opus + command_a | matn | F | Consensus DISAGREED (genre + name format) |
| 2 | إعلام الموقعين عن رب العالمين - ت مشهور | gate_abort | opus + command_a | other | F | Consensus DISAGREED (name format only) |
| 3 | إعلام الموقعين عن رب العالمين - ط العلمية | gate_abort | opus + command_a | other | F | — |
| **البداية والنهاية (2 editions)** |||||
| 4 | البداية والنهاية - ت التركي | success | opus + command_a | tarikh | F | trust=verified |
| 5 | البداية والنهاية - ط السعادة | success | opus + command_a | tarikh | F | trust=verified |
| **تفسير الطبري (2 editions)** |||||
| 6 | تفسير الطبري جامع البيان - ت التركي | gate_abort | opus + command_a | tafsir | F | — |
| 7 | تفسير الطبري جامع البيان - ط دار التربية والتراث | gate_abort | opus + **GPT-5.4** | tafsir | **F/T disagree** | ML disagreement: Opus=F, GPT-5.4=T (tahqiq_note) |
| **تحفة المودود (2 editions)** |||||
| 8 | تحفة المودود بأحكام المولود - ت الأرنؤوط | gate_abort | opus + command_a | risalah | F | — |
| 9 | تحفة المودود بأحكام المولود - ط عطاءات العلم | gate_abort | opus + command_a | risalah | F | Consensus DISAGREED (name format only) |
| **فتاوى اللجنة الدائمة (2 editions)** |||||
| 10 | فتاوى اللجنة الدائمة - المجموعة الأولى | success | opus + command_a | fatawa | F | Institutional author, no death date |
| 11 | فتاوى اللجنة الدائمة - المجموعة الثانية | gate_abort | opus + command_a | fatawa | F | Science scope broader than المجموعة الأولى |
| **ألفية ابن مالك (2 editions)** |||||
| 12 | ألفية ابن مالك - ت القاسم | success | opus + command_a | nazm | F | genre=nazm (not matn) — verify |
| 13 | ألفية ابن مالك - ط التعاون | gate_abort | opus + command_a | nazm | F | — |
| **شرح العقيدة الطحاوية (2 editions)** |||||
| 14 | شرح العقيدة الطحاوية - ط الأوقاف السعودية - بتعليقات أحمد شاكر | gate_abort | opus + command_a | sharh | T | Cross-check with Session 4 |
| 15 | شرح العقيدة الطحاوية - ط الرسالة | gate_abort | opus + command_a | sharh | T | Already evaluated Session 4: VERIFIED |
| **حاشية ابن عابدين + تكملة (author verification pair)** |||||
| 16 | حاشية ابن عابدين = رد المحتار - ط الحلبي | gate_abort | opus + command_a | hashiyah | T | FATHER: ابن عابدين (ت 1252); 3-layer verification needed |
| 17 | تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد المحتار - ط الفكر | gate_abort | opus + command_a | hashiyah | T | **SON: علاء الدين (ت ~1306); consensus DISAGREED; death GENUINE INFERENCE; author_raw EMPTY** |

4 SUCCESS books (البداية ×2, فتاوى اللجنة الأولى, ألفية ت القاسم): check result.json for trust_tier, model source, confidence_scores.
13 GATE_ABORT books: get all classification data from llm_responses/, not result.json.
1 GPT-5.4 book (تفسير الطبري ط دار التربية). All others use Command A.
4 consensus-DISAGREED books. 1 ML disagreement book.
</session_6_books>

<pre_identified_risks>
From NEXT.md and pipeline data pre-scan:

CRITICAL PRIORITY:
- تكملة حاشية ابن عابدين: MUST be the SON (علاء الدين), NOT the father (محمد أمين). author_raw is EMPTY. death 1306 is GENUINE INFERENCE. Consensus DISAGREED. Cross-check against Book 16 (حاشية — the FATHER's book).
- إعلام الموقعين: Genre varies across 3 editions (matn / other / usul_al_fiqh). Critical framework check: ALL 3 MUST have ML=false. All 3 pre-confirmed ML=false.
- تفسير الطبري ط دار التربية: GPT-5.4 says ML=true (tahqiq_note layer by محمود شاكر). Opus says ML=false. Known pattern (4th instance). Other edition (ت التركي) has ML=false from both models.

HIGH PRIORITY:
- شرح العقيدة الطحاوية: Cross-session check with Session 4 (ط الرسالة was VERIFIED).
- حاشية ابن عابدين: Verify 3-layer hashiyah chain (تنوير الأبصار → الدر المختار → رد المحتار).
- Death date false positives: أعلام ط عطاءات and تحفة ط عطاءات both have "691 - 751" in author_name_raw but extraction death=None. These are NOT genuine inferences.

MEDIUM PRIORITY:
- البداية والنهاية: Both editions must be tarikh, NOT tafsir (ابن كثير also wrote tafsir). Pre-confirmed clean.
- ألفية ابن مالك: Genre=nazm (versified grammar) — more precise than matn. Pre-confirmed consistent across editions.
- فتاوى اللجنة الدائمة: Institutional author (اللجنة الدائمة), no death date. Science scope differs between المجموعة الأولى and الثانية.
</pre_identified_risks>

<edition_group_protocol>
Session 6 is the ONLY session focused on edition groups. This protocol is MANDATORY for all 7 edition groups.

For each edition group:
1. Read pipeline data for ALL editions in the group
2. Compare author, genre, ML, and science across editions — these MUST match
3. Muhaqiq and trust MAY differ (different editions have different editors)
4. Document any cross-edition inconsistency with the EXACT values from each edition
5. For the GROUP verdict: if all editions are consistent and individually correct → VERIFIED at group level. If any edition has a field-level disagreement → note it and assess whether it's a genuine classification error or a fuzzy-boundary issue.

SPECIAL CASE — Books 16 and 17 (حاشية + تكملة):
These are NOT an edition group. They are a DIFFERENT-AUTHOR pair (father vs son). The protocol is:
1. Verify Book 16's author is the FATHER (محمد أمين ابن عابدين, ت 1252)
2. Verify Book 17's author is the SON (علاء الدين, ت ~1306)
3. Both should have genre=hashiyah, ML=true, science=['fiqh']
4. The authors MUST be DIFFERENT people — do not allow the pipeline to conflate them

SPECIAL CASE — Book 15 (شرح الطحاوية ط الرسالة):
Already evaluated in Session 4 as VERIFIED. Re-use that verdict. The purpose of including it here is to cross-check against Book 14 (ط الأوقاف) — confirm both editions match.
</edition_group_protocol>

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
  Note ALL disagreements — consensus does NOT check ML, attribution, or authority_level.

STEP 4 — For edition groups: AFTER evaluating individual books, compare across editions.
  Run the edition group protocol (above) for the group this book belongs to.
  Note: evaluate each book individually FIRST, then cross-compare. Do not pre-judge a book based on its sibling edition.

STEP 5 — Web search (BEFORE writing verdict) — at minimum 1 search per edition group.
  For famous works (البداية, الطبري, إعلام الموقعين, ألفية, فتاوى اللجنة), 1 search per group suffices.
  For high-priority books (تكملة حاشية, حاشية ابن عابدين), search specifically for the author/layer chain.
  Use web_fetch on at least 1 URL per high-priority book.

STEP 6 — Check consensus:
  Read consensus.json: agreed (bool), successful_models.
  For the 4 DISAGREED books: note the disagreement type (Correction 7 above).
  Remember: consensus does NOT check attribution, ML, or authority_level.

STEP 7 — Produce structured verdict using this exact format:

  Book: [Arabic name]
  Status: [success | gate_abort]
  Models: [opus + command_a | opus + gpt_5_4]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value] / Death source: [pass-through | inferred | absent | false-positive (date in raw text)]
  Genre: [verdict] — Pipeline: [value] / Expected: [value] / Shamela cat: [value] / Agreement: [yes | no — explain]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value] / Model agreement: [yes | no — explain]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Attribution: [verdict] — Opus: [value] / Second model: [value]
  Trust: [For success books] Pipeline: [value] / Score: [value]. [For gate_abort] SKIPPED (gate_abort)
  Consensus: agreed=[bool], models=[list]
  Extraction quality: [clean | issues noted — specify]
  Result.json model source: [For success books: which model's values appear] / N/A (gate_abort)
  Web Sources: [specific URLs visited, marking Shamela-ecosystem vs independent, note any fetched]
  Notes: [anything notable, including edition group cross-check results]
</corrected_per_book_workflow>

<after_all_verdicts>
After completing all 17 verdicts:

1. Edition Group Consistency Summary (REQUIRED — this is the main deliverable of Session 6):
   For each of the 7 edition groups + the author-verification pair, produce a cross-edition consistency table:
   | Field | Edition 1 | Edition 2 | (Edition 3) | Consistent? |
   Document: author match, genre match, ML match, science match, death date match. Flag all inconsistencies.

2. Consistency self-check (as a SEPARATE pass — not inline while writing):
   - Same standards applied to book 1 and book 17?
   - Source independence counts honest?
   - Shamela-ecosystem excluded everywhere?
   - Success books checked for trust + model source?
   - Edition group protocol run for all 7 groups + the author pair?

3. Confidence calibration section:
   - Table of all author/genre confidence scores
   - Any high-confidence + wrong cases?
   - Do scores discriminate between easy and hard cases?

4. Cross-book patterns:
   - Genre inconsistency across edition groups — which groups are clean, which have drift?
   - Authority_level for sharh/hashiyah works — does the Opus=reference vs CA=primary pattern persist?
   - ML=true consistency for sharh/hashiyah works across editions

5. Commit and push the report as PHASE_C_SESSION6_REPORT.md. Note: the owner will run 5 review rounds after this.
   - Rounds 1-4: Review the report (each round attacks from a different angle). The report is finalized after Round 4.
   - After Round 4: Write the handoff (NEXT.md) for Session 7 with pre-scanned pipeline data.
   - Round 5: Verify the handoff against pipeline data and governing documents. The final commit happens after Round 5.
</after_all_verdicts>

<task>
Clone the repo. Read these files in this order:
1. NEXT.md — current status and Session 6 specifics (DEEP READ — this is the primary handoff)
2. PHASE_C_ERRATA.md — corrections that override framework (DEEP READ — especially §6 on consensus disagreements, §9 on tahqiq_note)
3. PHASE_C_EVALUATION_FRAMEWORK.md — full protocol (SKIM — Edition Group Protocol, expected values table for Session 6 books, verdict scale)
4. PHASE_C_SESSION4_REPORT.md — prior session (READ شرح العقيدة الطحاوية verdict for cross-session check)
5. PHASE_C_SESSION5_REPORT.md — prior session (READ findings + cross-book patterns)
6. EVALUATION_QUICK_REFERENCE.md — compact checklist (DEEP READ — re-read before EACH book)

HELPER TOOL: python3 read_book.py "book_directory_name" reads all data for any book.

Then evaluate all 17 Session 6 books. For each book, re-read the quick reference, then follow the corrected per-book workflow exactly.

RECOMMENDED ORDER:
- Start with the CRITICAL books (تكملة حاشية #17, then حاشية #16) while context is fresh — these require the deepest investigation.
- Then إعلام الموقعين (3 editions, #1-3) — genre inconsistency analysis.
- Then تفسير الطبري (#6-7) — ML disagreement.
- Then the remaining groups in any order.
- After each edition group is complete, immediately write the cross-edition consistency table for that group before moving to the next.

After book 10 or 11: pause and run the mid-session quality gate from EVALUATION_QUICK_REFERENCE.md.

After all 17 verdicts: produce the edition group consistency summary, consistency self-check, confidence calibration, and cross-book patterns sections. Commit the report.
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip web search for any edition group — training data alone is insufficient
- Do NOT skip the edition group cross-comparison — noting "both editions agree" without a structured table is insufficient
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — all LLM data is captured (13/17 books are gate_abort)
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- Do NOT classify death dates as "genuine inference" when dates are visible in author_name_raw — those are false positives
- Do NOT assume ML agreement because consensus.agreed=true — consensus does not check ML
- Do NOT conflate father and son ابن عابدين — they are DIFFERENT people (ت 1252 vs ت ~1306)
- Do NOT treat genre inconsistency across editions as automatically wrong — for fuzzy genre boundaries (matn/risalah/other), note the inconsistency without necessarily flagging it
- Do NOT invent verdict categories — only VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated (this is a 17-book session), STOP and tell me rather than degrading quality silently
</guardrails>
