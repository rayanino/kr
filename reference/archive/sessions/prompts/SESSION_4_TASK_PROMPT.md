Phase C calibration, Sessions 1–3 are done. You are continuing evaluation work that previous Claude Chat sessions completed.

Your job: evaluate Phase C pipeline results for Session 4 (Multi-Layer + Commentary — 10 books), following the protocol below.

<what_was_done>
Session 0 (Calibration) evaluated 3 books, found 4 engine bugs, committed corrections.
Session 1 (Fixture Regression) evaluated 11 books (14 total with calibration).
Session 2 (Famous Works A) evaluated 8 books — all 8 VERIFIED (1 with ML field-level flag on مسند أحمد).
Session 3 (Famous Works B) evaluated 7 books — all 7 VERIFIED (1 with ML field-level flag on الرسالة).

Running totals: 25 VERIFIED, 4 PLAUSIBLE, 0 FLAG, 0 ESCALATE (29 books evaluated).

Prior reports are in the repo:
- PHASE_C_SESSION1_REPORT.md
- PHASE_C_SESSION1_DEEP_ANALYSIS.md
- PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md
- PHASE_C_SESSION2_REPORT.md
- PHASE_C_SESSION3_REPORT.md
</what_was_done>

<critical_corrections>
The evaluation framework (PHASE_C_EVALUATION_FRAMEWORK.md) has errors discovered during calibration. These corrections OVERRIDE the framework wherever they conflict:

CORRECTION 1 — LLM FILENAME:
  Framework says: llm_responses/opus_4_6.json
  Actual filename: llm_responses/claude_opus_4_6.json

CORRECTION 2 — COMMAND A DID NOT TIME OUT:
  PHASE_C_LESSONS.md claims "Command A timed out on every attempt." This is completely false.
  Reality: 0/73 books are single_model_fallback. All 73 have dual-model consensus.
  67 books used Opus + Command A. 6 books used Opus + GPT-5.4.
  The 6 GPT-5.4 books: أبنية الأسماء والأفعال والمصادر, أنوار الهلالين في التعقبات على الجلالين, الأذكار للنووي ت الأرنؤوط, المستدرك على مجموع الفتاوى, تفسير الطبري جامع البيان - ط دار التربية والتراث, حاشية العطار على شرح الجلال المحلي على جمع الجوامع.
  Framework Section 7 (Single-Model Fallback Assessment) does NOT apply. Skip it entirely.

CORRECTION 3 — AUTHOR CONFIDENCE IN result.json IS BROKEN:
  result["author"]["confidence"] is ALWAYS 1.0 for every success book. This is an engine bug.
  The real author confidence is ONLY in: llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence

CORRECTION 4 — SECOND MODEL VARIES:
  Check ls llm_responses/ for each book. The second model is either command_a.json (67 books) or gpt_5_4.json (6 books). Session 4 specific: حاشية العطار uses GPT-5.4; all other 9 use Command A.

CORRECTION 5 — VERIFIED THRESHOLD:
  Shamela-ecosystem sources (shamela.ws, ketabonline.com, turath.io, waqfeya.net) all derive from the same underlying database. They count as ONE source collectively, not multiple independent sources.
  VERIFIED requires 2+ genuinely independent sources. Independent means: Wikipedia Arabic, academic catalogs, university syllabi, publisher sites, archive.org, noor-book.com, islamway.net, alukah.net, government sites, or non-Shamela Islamic library sites.

CORRECTION 6 — TAHQIQ-AS-LAYER SYSTEMATIC BIAS:
  Opus classifies tahqiq (critical edition) notes as a multi-layer structure for non-commentary books.
  All 3 instances from Errata §9 (الرسالة, مختصر صحيح مسلم, مسند أحمد) are now confirmed through Sessions 2-3.
  Session 4 specific: 3 genuine sharh books (فتح الباري لابن رجب, شرح الورقات, شرح العقيدة الطحاوية) have tahqiq_note as an ADDITIONAL layer. Since binary ML=true is correct for these (they ARE genuine sharh works), do NOT flag them. Note the tahqiq_note but confirm binary classification is correct.

CORRECTION 7 — CONSENSUS DOES NOT CHECK MULTI-LAYER:
  consensus.agreed=true only means author + work agreement. Models can disagree on is_multi_layer and still show agreed=true. Always compare ML between both models yourself.
  Session 4 specific: all 10 books have ML agreement between both models. No ML disagreements in this batch.
</critical_corrections>

<session_3_findings_carry_forward>
These findings from Sessions 2-3 affect how you evaluate Session 4 books:

1. Tahqiq-as-layer pattern fully characterized: non-commentary book + muhaqiq in extraction → Opus says ML=true with tahqiq_note, CA says false. On genuine sharh/hashiyah books, the tahqiq_note layer is harmless. Muhaqiq presence is necessary but NOT sufficient for the bias (الأذكار has muhaqiq but ML=false correctly). The differentiating mechanism is unknown.

2. Attribution: Opus says "definitive" for famous classical works, "traditional" for mediated-transmission works (e.g., الأم which was dictated/compiled). Only flag "disputed" — those are genuine scholarly disputes.

3. Death date "real inferences" from strategic analysis: at least 4/10 were false positives (dates embedded in author_name_raw text). Always check raw text before classifying as genuine inference.

4. For success books: result.json model source matters. CA consistently has higher author confidence (1.0 vs Opus 0.97-0.99), so CA's values often appear in result.json when models disagree.

5. CA's layer structure can be wrong even when binary ML is correct (Session 2: حاشية ابن عابدين — CA conflated matn and sharh authors). Verify BOTH models' layer structures, not just Opus.

6. Genre confidence correlates with genuine ambiguity (الأذكار 0.85 was genuinely ambiguous). Good calibration signal.
</session_3_findings_carry_forward>

<session_4_books>
10 books — Multi-Layer + Commentary:

| # | Book (exact directory name) | Status | Models | ML | Genre (Opus) |
|---|---------------------------|--------|--------|----|--------------|
| 1 | فتح الباري لابن رجب | gate_abort | opus + command_a | true (agree) | sharh |
| 2 | شرح الورقات في أصول الفقه - المحلي | gate_abort | opus + command_a | true (agree) | sharh |
| 3 | حاشية العطار على شرح الجلال المحلي على جمع الجوامع | gate_abort | opus + gpt_5_4 | true (agree) | hashiyah |
| 4 | شرح العقيدة الطحاوية - ط الرسالة | gate_abort | opus + command_a | true (agree) | sharh |
| 5 | مقامات الحريري | success | opus + command_a | false (agree) | adab |
| 6 | شرح مقامات الحريري | gate_abort | opus + command_a | true (agree) | sharh |
| 7 | شرح ديوان المتنبي للواحدي | gate_abort | opus + command_a | true (agree) | sharh |
| 8 | اللامع العزيزي شرح ديوان المتنبي | gate_abort | opus + command_a | true (agree) | sharh |
| 9 | المآخذ على شراح ديوان أبي الطيب المتنبي | success | opus + command_a | false (agree) | other |
| 10 | التعليق على الرحيق المختوم | success | opus + command_a | true (agree) | hashiyah |

3 SUCCESS books (مقامات, المآخذ, التعليق): check result.json for trust_tier, model source, confidence_scores.
7 GATE_ABORT books: get all classification data from llm_responses/, not result.json.
0 ML disagreements in this batch.
1 GPT-5.4 book (حاشية العطار).
</session_4_books>

<pre_identified_risks>
From NEXT.md, strategic analysis, and pipeline data pre-scan:

HIGH PRIORITY:
- المآخذ على شراح ديوان أبي الطيب المتنبي: Genre must NOT be sharh. This is literary criticism OF commentators, not itself a commentary. Title المآخذ على شراح = "criticisms of the commentators." Opus=other, CA=adab. Result.json carries genre=adab. Trust=verified (0.7175).
- التعليق على الرحيق المختوم: Genre disagreement — Opus=hashiyah (but only 2 layers: matn+sharh, internally contradictory), CA=sharh. Result.json carries genre=sharh. Trust=flagged (0.4625). ALSO: death date genuine inference candidate (الملاح has no date in extraction or raw text).
- حاشية العطار: Only genuine hashiyah (3 distinct layers). Verify chain: matn=تاج الدين السبكي (جمع الجوامع), sharh=جلال الدين المحلي, hashiyah=حسن العطار (ت 1250). Both Opus and GPT-5.4 agree on the chain.
- فتح الباري لابن رجب: DIFFERENT author from Session 2's فتح الباري بشرح البخاري. Session 2 = ابن حجر العسقلاني (ت 852). This = ابن رجب الحنبلي (ت 795). Same matn (صحيح البخاري), different sharh author. Must NOT confuse these two.

MEDIUM PRIORITY:
- المتنبي cluster (3 books): شرح الواحدي (ت 468) and اللامع المعري (ت 449) are DIFFERENT commentators on the same poet. Both should have matn=المتنبي (أبو الطيب أحمد بن الحسين). المآخذ by الأزدي (ت 644) is NOT a sharh.
- شرح العقيدة الطحاوية: One of 2 editions (second in Session 6). Note findings for cross-comparison.
- Cross-check: التعليق's matn author must match Session 3's verified الرحيق المختوم author (المباركفوري ت 1427).

LOW PRIORITY:
- مقامات الحريري: Genre=adab, ML=false, trust=verified. Straightforward.
- شرح مقامات الحريري: Author IS in extraction (الشريشي ت 619, conf 0.97). Framework says VERIFY but extraction has the data.
</pre_identified_risks>

<corrected_per_book_workflow>
For EVERY book, follow this exact sequence. Do not skip steps or reorder them.

STEP 1 — Read EVALUATION_QUICK_REFERENCE.md (re-read before each book, not just the first).
  Then: python3 read_book.py "book_directory_name" — reads all pipeline data.

STEP 2 — Check extraction quality FIRST (before looking at LLM output):
  From read_book.py output, note:
    - author_name_raw: present? Does it contain an embedded death date like "[ت XXX هـ]"?
    - shamela_category: note for cross-check against pipeline genre
    - muhaqiq_name_raw: present or null?
    - _quality_issues: any flags?
    - fields_present vs fields_absent: how much context did the LLM have?

STEP 3 — Extract pipeline values from BOTH models:
  For gate_abort books: read ALL fields from llm_responses/.
  For success books: read result.json for genre, ML, science, trust. Read llm_responses/ for author confidence.
  Compare Opus vs second model on: genre, author, death_date, ML, science_scope, attribution, layers.
  Note any disagreements — especially on layer structure (this is the multi-layer session).

STEP 4 — LAYER CHAIN VERIFICATION (NEW for Session 4):
  For every ML=true book (7/10 in this session):
    a. Read layer structure from BOTH models (Opus and CA/GPT)
    b. For each layer: note the layer_type and author_name
    c. If genre=hashiyah: verify 3 distinct layers with 3 distinct authors
    d. If tahqiq_note layer present on a genuine sharh: note it, do NOT flag (binary ML correct)
    e. Cross-check matn authors across related books (المتنبي cluster shares matn author)

STEP 5 — Check consensus:
  Read consensus.json: agreed (bool), successful_models.
  All 10 books in Session 4 have consensus.agreed=true and ML agreement.

STEP 6 — Independent web verification (MANDATORY):
  Search for the book title + author in Arabic. Use web_fetch on at least 1 URL.
  For ML=true books: verify layer chain (who wrote the matn? who wrote the sharh?) from external source.
  For author: confirm name and death date from 2+ independent sources.
  For genre: cross-check against shamela_category.

STEP 7 — Produce structured verdict using this exact format:

  Book: [Arabic name]
  Status: [success | gate_abort]
  Models: [opus + command_a | opus + gpt_5_4]
  Verdict: VERIFIED | PLAUSIBLE | UNVERIFIABLE | FLAG | ESCALATE
  Author: [verdict] — Pipeline: [value] / Verified: [value] / Death: [pipeline] vs [verified] / LLM conf: [value] / Death source: [pass-through | inferred]
  Genre: [verdict] — Pipeline: [value] / Expected: [value] / Shamela cat: [value] / Agreement: [yes | no — explain]
  Multi-Layer: [verdict] — Pipeline: [value] / Expected: [value] / Model agreement: [yes | no]
  Layers: [For ML=true only] Opus: [layer_type=author for each layer] / M2: [same] / Verified: [external source]
  Science: [verdict] — Pipeline: [values] / Expected: [values]
  Trust: [For success books] Pipeline: [value] / Score: [value]. [For gate_abort] SKIPPED (gate_abort)
  Consensus: agreed=[bool], models=[list], disagreement=[if any]
  Extraction quality: [clean | issues noted]
  Result.json model source: [For success books: which model's values appear] / N/A (gate_abort)
  Web Sources: [specific URLs visited, marking Shamela-ecosystem vs independent, at least 1 fetched]
  Notes: [anything notable, including authority_level disagreements, tahqiq_note observations, cross-book cross-checks]
</corrected_per_book_workflow>

<after_all_verdicts>
After completing all 10 verdicts:

1. Consistency self-check (as a SEPARATE pass — not inline while writing):
   - Same standards applied to book 1 and book 10?
   - Source independence counts honest?
   - Shamela-ecosystem excluded everywhere?
   - Layer chains verified for all ML=true books?
   - Success books checked for trust + model source?

2. Confidence calibration section:
   - Table of all author/genre/ML confidence scores
   - Any high-confidence + wrong cases? (Most dangerous pattern)
   - Any low-confidence + right cases? (Good calibration)

3. Cross-book patterns:
   - المتنبي cluster: are matn authors consistent across the 2 sharh books?
   - فتح الباري: correctly different author from Session 2 version?
   - Edition group note for شرح العقيدة الطحاوية (second edition in Session 6)

4. Strategic prediction validation from PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md.

5. Commit and push the report as PHASE_C_SESSION4_REPORT.md. Note: the owner will run 5 review rounds after this.
   - Rounds 1-4: Review the report (each round attacks from a different angle). The report is finalized after Round 4.
   - After Round 4: Write the handoff (NEXT.md) for Session 5 with pre-scanned pipeline data.
   - Round 5: Verify the handoff against pipeline data and governing documents. The final commit happens after Round 5.
</after_all_verdicts>

<task>
Clone the repo. Read these files in this order:
1. NEXT.md — current status and Session 4 specifics (DEEP READ — this is the primary handoff)
2. PHASE_C_ERRATA.md — corrections that override framework (DEEP READ — these are the actual rules)
3. PHASE_C_EVALUATION_FRAMEWORK.md — full protocol (SKIM for context — verdict scale §Verdict Scale, expected values table for Session 4 books, worked examples §Worked Example)
4. PHASE_C_SESSION3_REPORT.md — prior session (READ findings + cross-book patterns, SKIM per-book details)
5. PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md — predictions and risk map (READ Session 4 risk prediction)
6. EVALUATION_QUICK_REFERENCE.md — compact checklist (DEEP READ — re-read before EACH book)

HELPER TOOL: python3 read_book.py "book_directory_name" reads all data for any book.

Then evaluate all 10 Session 4 books. For each book, re-read the quick reference, then follow the corrected per-book workflow exactly. Produce the structured verdict for each book.

After book 6 or 7: pause and run the mid-session quality gate from EVALUATION_QUICK_REFERENCE.md.

After all 10 verdicts: produce the consistency self-check, confidence calibration, and cross-book patterns sections. Commit the report.
</task>

<guardrails>
- Do NOT re-run any books or modify engine code — evaluate what exists
- Do NOT skip web search for any book — training data alone is insufficient
- Do NOT read author confidence from result.json — it's always 1.0 (engine bug)
- Do NOT treat gate_abort as a negative signal — all LLM data is captured (7/10 books are gate_abort)
- Do NOT give VERIFIED to books with only Shamela-ecosystem sources — ceiling is PLAUSIBLE
- Do NOT invent verdict categories — only VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- Do NOT flag tahqiq_note layer on genuine sharh/hashiyah books — binary ML=true is correct for these
- Do NOT confuse فتح الباري لابن رجب (ت 795) with فتح الباري بشرح البخاري by ابن حجر (ت 852) — different authors
- If genuinely unsure, use UNVERIFIABLE — honest uncertainty beats confident mistakes
- If context gets saturated, STOP and tell me rather than degrading quality silently
</guardrails>
