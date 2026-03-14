Phase C calibration, Sessions 1–6 are done. You are continuing evaluation work that previous Claude Chat sessions completed.

Your job: evaluate Phase C pipeline results for Session 7 (Remaining — 10 books). This is the FINAL evaluation session before aggregation.

<what_was_done>
Session 0 (Calibration) evaluated 3 books, found 4 engine bugs, committed corrections.
Session 1 (Fixture Regression) evaluated 14 books.
Session 2 (Famous Works A) evaluated 14 books.
Session 3 (Famous Works B) evaluated 7 books — all 7 VERIFIED (2 with ML field-level flags).
Session 4 (Multi-Layer + Commentary) evaluated 10 books — 9 VERIFIED + 1 PLAUSIBLE.
Session 5 (Attribution + Trust + Obscure) evaluated 10 books — 4 VERIFIED + 6 PLAUSIBLE.
Session 6 (Edition Groups) evaluated 17 books — all 17 VERIFIED (4 review rounds).

Running totals: 55 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (66 verdicts across 63 unique books).

Prior reports are in the repo:
- PHASE_C_SESSION1_REPORT.md through PHASE_C_SESSION6_REPORT.md
- PHASE_C_ERRATA.md (corrections that override the framework)
- EVALUATION_QUICK_REFERENCE.md (compact per-book checklist)
</what_was_done>

<critical_corrections>
The evaluation framework (PHASE_C_EVALUATION_FRAMEWORK.md) has errors discovered during calibration. These corrections OVERRIDE the framework wherever they conflict:

CORRECTION 1 — LLM FILENAME:
  Framework says: llm_responses/opus_4_6.json
  Actual filename: llm_responses/claude_opus_4_6.json

CORRECTION 2 — ALL BOOKS HAVE DUAL-MODEL CONSENSUS:
  0/73 books are single_model_fallback. Framework Section 7 does NOT apply. Skip it entirely.
  9/10 Session 7 books use Opus + Command A. 1 book (المستدرك على مجموع الفتاوى) uses Opus + GPT-5.4.

CORRECTION 3 — AUTHOR CONFIDENCE IN result.json IS BROKEN:
  result["author"]["confidence"] is ALWAYS 1.0 for every success book. This is an engine bug.
  The real author confidence is ONLY in: llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence

CORRECTION 4 — VERIFIED THRESHOLD:
  Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) all derive from the same database. They count as ONE source collectively.
  VERIFIED requires 2+ genuinely independent sources: Wikipedia Arabic, academic catalogs, university syllabi, publisher sites, archive.org, noor-book.com, islamway.net, alukah.net, government sites.

CORRECTION 5 — CONSENSUS DOES NOT CHECK MULTI-LAYER OR ATTRIBUTION:
  consensus.agreed=true only means author + work agreement. Models can disagree on is_multi_layer, attribution_status, and authority_level and still show agreed=true. Always compare these fields between both models yourself.

CORRECTION 6 — CONSENSUS DISAGREEMENT (Session 7):
  1/10 books has consensus.agreed=false:
  - من أحاديث سفيان الثوري - رواية السري بن يحيى: Name format only (same person: السري بن يحيى) — not substantive
</critical_corrections>

<session_findings_carry_forward>
These findings from Sessions 2-6 affect how you evaluate Session 7 books:

1. Zero author identification errors across 66 verdicts (63 unique books). The pipeline's author identification is the strongest field.

2. Opus attribution taxonomy: "definitive" for famous well-established works, "traditional" for conventionally-attributed works, "disputed" for genuinely contested works. CA tends toward "definitive" even for traditional works.

3. Tahqiq_note ML=true pattern: 4 cumulative instances where a model classifies non-commentary books as multi-layer because of tahqiq notes. Opus: 3 instances (الرسالة, مختصر صحيح مسلم, مسند أحمد). GPT-5.4: 1 instance (تفسير الطبري ط التربية). Command A: 0 instances in 67 books — appears immune. Session 7 has 1 new expected instance: مختصر صحيح مسلم ت الألباني (#9). When a non-sharh/hashiyah book has ML=true with layer_type="tahqiq_note", note the known pattern — do NOT treat it as correct.

4. Authority_level disagreements: Opus=reference vs CA=primary on sharh works persists (9/11 across Sessions 4-6). Session 7 has 1 sharh work (#1 الأحاديث الأربعين) — check for this pattern.

5. Death date genuine inference running total: 3 confirmed correct (728, 324, 1306), 1 confirmed wrong (1432 vs actual 1439), 9 confirmed false positives (dates embedded in author_name_raw). Session 7: check author_name_raw text for embedded dates BEFORE classifying any inference as "genuine."

6. web_fetch compliance: Sessions 4-6 had 0-1/N actual web_fetch. Session 7 must achieve at least 3/10 web_fetch calls on high-priority books.
</session_findings_carry_forward>

<session_7_books>
10 books — the final batch. 4 SUCCESS, 6 GATE_ABORT. 1 GPT-5.4 book. 1 consensus-DISAGREED.

| # | Book (exact directory name) | Status | Models | Genre (Opus) | ML | Key risk |
|---|---------------------------|--------|--------|--------------|-----|----------|
| **Framework VERIFY books (5)** |||||
| 1 | الأحاديث الأربعين النووية مع ما زاد عليها ابن رجب وعليها الشرح الموجز المفيد | success | opus + command_a | sharh | T | **VERIFY.** trust=flagged (0.4325). Author conf=0.82. death=None. Genre=sharh, ML=true. Cross-check: Session 0 evaluated الأربعون النووية (the base matn) |
| 2 | الإبدال في لغات الأزد دراسة صوتية في ضوء علم اللغة الحديث | success | opus + command_a | risalah | F | **VERIFY.** trust=flagged (0.455). **Page mismatch: 73 of 494 physical (15%).** Modern academic. conf=0.92 |
| 3 | المستدرك على مجموع الفتاوى | gate_abort | opus + **GPT-5.4** | fatawa | F | **VERIFY.** GPT-5.4 second model. Cross-check Session 0's مجموع الفتاوى — المستدرك is a DIFFERENT work by a DIFFERENT compiler. death=728 |
| 4 | النكت على شرح النووي على صحيح مسلم | gate_abort | opus + command_a | other | F | **VERIFY.** Author=هاني فقيه (modern), conf=**0.75** (lowest in corpus). death=None. **Genre disagreement: Opus=other, CA=hashiyah.** Gate error: "is_multi_layer=true but text_layers is empty" |
| 5 | معالم بيانية في آيات قرآنية | success | opus + command_a | tafsir | F | **VERIFY.** trust=flagged (0.4325). **Only 2 content pages.** Author=المغامسي. DIFFERENT BOOK from Session 3's "معالم بيانية في أحاديث نبوية" |
| **Riwayah + hadith books (3)** |||||
| 6 | تاريخ ابن معين - رواية الدارمي | gate_abort | opus + command_a | tabaqat | F | author=ابن معين (ت 233). Genre=tabaqat (biographical, not hadith_collection) |
| 7 | حديث يحيى بن معين رواية أبي منصور الشيباني | gate_abort | opus + command_a | hadith_collection | F | Same author as #6 (ابن معين ت 233) but DIFFERENT work. Riwayah field present. 43 pages |
| 8 | مسند أبي حنيفة رواية الحصكفي | gate_abort | opus + command_a | hadith_collection | F | author=أبو حنيفة (ت 150), conf=0.92. Verify: pipeline author = original narrator or compiler? |
| **Edition / riwayah variants (2)** |||||
| 9 | مختصر صحيح مسلم للمنذري ت الألباني | gate_abort | opus + command_a | mukhtasar | **T** | **Opus ML=true (tahqiq_note) — same pattern as Session 2.** CA ML=false. Cross-edition check |
| 10 | من أحاديث سفيان الثوري - رواية السري بن يحيى - جوامع الكلم | success | opus + command_a | hadith_collection | F | **Consensus DISAGREED** (name format only). trust=verified (0.6925). Riwayah variant of Session 1 book |
</session_7_books>

<pre_identified_risks>
From NEXT.md pre-scan:

CRITICAL PRIORITY:
- النكت على شرح النووي (#4): Lowest confidence in entire 73-book corpus (0.75). Genre disagreement (Opus=other 0.82, CA=hashiyah 0.90). Unusual gate error: "is_multi_layer=true but text_layers is empty." Modern author (هاني فقيه), no death date. Needs deepest investigation — verify the author exists and identify the work's actual scholarly structure.
- المستدرك على مجموع الفتاوى (#3): GPT-5.4 as second model. المستدرك compiles fatwas MISSED in the original مجموع. Verify: is the pipeline author ابن تيمية (original fatwa issuer) or the compiler (ابن القاسم)?

HIGH PRIORITY:
- معالم بيانية في آيات قرآنية (#5): Only 2 content pages (content_minimal). DIFFERENT BOOK from Session 3's "أحاديث نبوية" version. With only 2 pages, all classification is minimal evidence.
- الأحاديث الأربعين مع ابن رجب (#1): Author conf=0.82, death=None. Cross-check with Session 0's الأربعون النووية. Identify the actual sharh author and verify the layer chain.
- مختصر صحيح مسلم ت الألباني (#9): Tahqiq_note ML=true pattern (5th Opus instance). Cross-edition check with Session 2.

MEDIUM PRIORITY:
- مسند أبي حنيفة (#8): Author attribution ambiguity (أبو حنيفة vs compiler الحصكفي).
- ابن معين pair (#6, #7): Same author, different works and genres. Verify genre distinction.
- من أحاديث سفيان الثوري (#10): Riwayah variant. Cross-check with Session 1.
</pre_identified_risks>

<corrected_per_book_workflow>
For EVERY book, follow this exact sequence. Do not skip steps or reorder them.

STEP 1 — Re-read EVALUATION_QUICK_REFERENCE.md (before each book, not just the first).
  Then: python3 read_book.py "book_directory_name" — reads all pipeline data.

STEP 2 — Check extraction quality FIRST (before looking at LLM output):
  From read_book.py output, note:
    - author_name_raw: present? Does it contain an embedded death date?
    - shamela_category: note for cross-check against pipeline genre
    - muhaqiq_name_raw: present or null?
    - _quality_issues: any flags?
    - fields_present vs fields_absent

STEP 3 — Extract pipeline values from BOTH models:
  For gate_abort books: read ALL fields from llm_responses/.
  For success books: read result.json for genre, ML, science, trust. Read llm_responses/ for author confidence.
  Compare Opus vs second model on: genre, author, death_date, ML, science_scope, attribution, authority_level.
  Note ALL disagreements — consensus does NOT check ML, attribution, or authority_level.

STEP 4 — Web search (BEFORE writing verdict):
  For VERIFY books (#1-5): at minimum 2 searches + 1 web_fetch per book.
  For other books (#6-10): at minimum 1 search per book.

STEP 5 — Check consensus:
  Read consensus.json: agreed (bool), successful_models.
  For the 1 DISAGREED book (#10): note the disagreement type (name format only — not substantive).

STEP 6 — For cross-edition books (#9, #10): compare with the prior session's verdict.

STEP 7 — Produce structured verdict using this exact format:

  Book: [Arabic name]
  Status: [success | gate_abort]
  Models: [opus + command_a | opus + gpt_5_4]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value] / Death source: [pass-through | inferred | absent | false-positive]
  Genre: [verdict] — Pipeline: [value] / Expected: [value] / Shamela cat: [value] / Agreement: [yes | no — explain]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value] / Model agreement: [yes | no — explain]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Attribution: [verdict] — Opus: [value] / Second model: [value]
  Trust: [For success books] Pipeline: [value] / Score: [value]. [For gate_abort] SKIPPED (gate_abort)
  Consensus: agreed=[bool], models=[list]
  Extraction quality: [clean | issues noted — specify]
  Result.json model source: [For success books: which model's values appear] / N/A (gate_abort)
  Web Sources: [specific URLs visited, marking Shamela-ecosystem vs independent, note any fetched]
  Notes: [anything notable, cross-edition checks, cross-session references]
</corrected_per_book_workflow>

<after_all_verdicts>
After completing all 10 verdicts:

1. Consistency self-check (as a SEPARATE pass — not inline):
   - Same standards applied to book 1 and book 10?
   - Source independence counts honest?
   - Shamela-ecosystem excluded everywhere?
   - Success books checked for trust + model source?
   - Cross-edition checks done for #9 and #10?

2. Confidence calibration section:
   - Table of all author/genre confidence scores
   - Any high-confidence + wrong cases?
   - Do scores discriminate between easy and hard cases?

3. Cross-book patterns:
   - Genre disagreements — which books have them?
   - Authority_level for the 1 sharh work — does the Opus=reference vs CA=primary pattern persist?
   - Any new findings?

4. Final session summary:
   - Updated running totals (Sessions 0-7 combined)
   - List of all books evaluated across all sessions with verdict counts
   - Anything the aggregation session needs to know

5. Commit and push the report as PHASE_C_SESSION7_REPORT.md. The owner will run review rounds after this.
</after_all_verdicts>

<task>
Clone the repo. Read these files in this order:
1. NEXT.md — current status and Session 7 specifics (DEEP READ — primary handoff)
2. PHASE_C_ERRATA.md — corrections that override framework (DEEP READ — especially §6, §9)
3. PHASE_C_EVALUATION_FRAMEWORK.md — full protocol (SKIM — expected values table, verdict scale)
4. PHASE_C_SESSION2_REPORT.md — (READ مختصر صحيح مسلم verdict for cross-edition check on Book #9)
5. PHASE_C_SESSION1_REPORT.md — (READ من أحاديث سفيان الثوري verdict for cross-edition check on Book #10)
6. PHASE_C_SESSION6_REPORT.md — (READ findings + cross-book patterns)
7. EVALUATION_QUICK_REFERENCE.md — compact checklist (DEEP READ — re-read before EACH book)

HELPER TOOL: python3 read_book.py "book_directory_name" reads all data for any book.

Then evaluate all 10 Session 7 books. For each book, re-read the quick reference, then follow the corrected per-book workflow exactly.

RECOMMENDED ORDER:
- Start with CRITICAL books while context is fresh: النكت (#4), المستدرك (#3)
- Then remaining VERIFY books: الأحاديث الأربعين (#1), الإبدال (#2), معالم بيانية (#5)
- Then riwayah books: تاريخ ابن معين (#6), حديث يحيى (#7), مسند أبي حنيفة (#8)
- Then edition/riwayah variants: مختصر صحيح مسلم (#9), من أحاديث سفيان (#10)

After book 6: pause and run the mid-session quality gate from EVALUATION_QUICK_REFERENCE.md.

After all 10 verdicts: produce the consistency self-check, confidence calibration, cross-book patterns, and final session summary. Commit the report.

This is the FINAL evaluation session. The report must include everything needed for aggregation.
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip web search for any book — training data alone is insufficient
- Do NOT skip web_fetch for VERIFY books (#1-5) — search snippets alone are insufficient
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — all LLM data is captured (6/10 books are gate_abort)
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- Do NOT classify death dates as "genuine inference" when dates are visible in author_name_raw
- Do NOT assume ML agreement because consensus.agreed=true — consensus does not check ML
- Do NOT conflate معالم بيانية في آيات قرآنية with Session 3's معالم بيانية في أحاديث نبوية
- Do NOT conflate المستدرك على مجموع الفتاوى with Session 0's مجموع الفتاوى
- Do NOT invent verdict categories — only VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated, STOP and tell me rather than degrading quality silently
</guardrails>
