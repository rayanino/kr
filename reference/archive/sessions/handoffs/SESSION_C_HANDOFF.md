# Session C Handoff Prompt

Paste this as the first message in a new KR project conversation.

---

You are continuing the Phase D evaluation of the KR source engine. Your job is to verify that the pipeline's metadata classifications are factually correct for 15 structurally flagged books.

<completed_sessions>
Layer 1: Programmatic validation ✅ (204 books)
Layer 2: Pattern analysis ✅ (PHASE_D_PATTERN_ANALYSIS.md)
Session A: 14 consensus disagreement books ✅ (8V 5P 1F — PHASE_D_SESSION_A_REPORT.md)
Session B: 19 author uncertainty books ✅ (4V 13P 1F 1E — PHASE_D_SESSION_B_REPORT.md)
</completed_sessions>

<your_task>
Session C: Evaluate 15 structural flag books → PHASE_D_SESSION_C_REPORT.md
Then: Session D (12 random calibration) and Layer 4 (aggregation), if context permits.
</your_task>

<startup_sequence>
Execute these steps IN ORDER before evaluating any book:

1. Clone repo: `git clone https://{github_token_from_project_files}@github.com/rayanino/kr.git /home/claude/kr`
2. Read `NEXT.md` — current state
3. Read `PHASE_D_EVALUATION_PROTOCOL.md` — verdict format, field sources, verdict scale
4. Read `PHASE_D_SESSION_ERRATA.md` — 7 mandatory rules from Session A mistakes
5. Read `EVALUATION_QUICK_REFERENCE.md` — compact per-book checklist
6. Read `SESSION_C_PREPARATION.md` — per-book investigation plan and error prevention rules
7. Read `PHASE_D_SESSION_B_REPORT.md` critical self-review section (bottom) — 9 errors to never repeat
8. Test `session_c_extract.py`: run `python3 session_c_extract.py "النكت على شرح النووي على صحيح مسلم"` and verify it outputs structural flags correctly
</startup_sequence>

<session_c_books>
15 books organized by investigation type. The investigation plan is in SESSION_C_PREPARATION.md but here is the summary:

TYPE 1 — Genre+ML structural investigation (hardest, research-intensive):
  1. أمالي الأذكار في فضل صلاة التسبيح — genre disagree (sharh vs hadith_collection), ML=True
  11. النكت على شرح النووي على صحيح مسلم — ERR-01: hashiyah + ML=False (contradiction)
  12. تفسير ابن كمال باشا — tafsir + ML=False (contradiction)

TYPE 2 — BUG-03 ML override verification (5 books, Opus=True CA=False Pipeline=False):
  4. الأدب المفرد
  7. الرسالة للشافعي (Phase C book)
  9. القسم الثالث من المعجم الأوسط (also genre disagree: mujam vs hadith_collection)
  14. مختصر صحيح مسلم (Phase C book)
  15. مسند أحمد (Phase C book)

TYPE 3 — Genre disagreement, non-ML:
  2. إعلام الموقعين ط العلمية — edition group inconsistency (other vs usul_al_fiqh)

TYPE 4 — Disputed attribution:
  5. الإبانة عن أصول الديانة - ت العصيمي — Opus says "disputed", CA says "definitive"
  6. الإبانة عن أصول الديانة - ت فوقية — same work, different tahqiq

TYPE 5 — Layer verification (ML=True, both agree, verify layers are genuine):
  3. الأحاديث الأربعين النووية مع الشرح الموجز
  8. الروضة الندية شرح الدرر البهية
  13. شرح المفصل لابن يعيش

TYPE 6 — Unknown flag reason:
  10. المسائل النحوية في كتاب التوضيح لشرح الجامع الصحيح
</session_c_books>

<error_prevention_rules>
Session B had 9 errors across 19 verdicts (47% error rate before correction). These rules are HARD CONSTRAINTS derived from those specific failures:

RULE 1 — NO MEMORY-BASED TRANSCRIPTION.
Every field value in a verdict MUST come from `session_c_extract.py` output or a tool call visible in the CURRENT message. If the data scrolled past, re-run the tool. Never write a genre, confidence, trust tier, science scope, or author name from memory.

RULE 2 — WEB SEARCH + WEB_FETCH BEFORE EVERY VERDICT.
Minimum: 1 search + 1 successful fetch per book. If fetch fails, try another URL. Document failures explicitly. Never write "source confirms" without a visible search result.

RULE 3 — VERIFY EACH VERDICT IMMEDIATELY AFTER WRITING.
After writing each verdict, re-run `session_c_extract.py "book_name"` and compare EVERY field (genre, ML, trust_tier, trust_score, science_scope, author_conf, death_date, attribution). Fix mismatches before the next book.

RULE 4 — SEARCH FOR CONTRADICTING EVIDENCE.
Before asserting any classical book's genre or attribution, search for evidence that your assessment is WRONG. The critical error in Session B was flagging a correct LLM output because the evaluator searched only for the famous namesakes, not for descendants. For every non-trivial claim, ask: "what would make this wrong?"

RULE 5 — ARITHMETIC CHECKS EVERY 5 BOOKS.
Count V/P/F/E and verify against sum of individual verdicts. Fix immediately.
</error_prevention_rules>

<per_book_workflow>
For EACH of the 15 books, execute this exact sequence. Do not skip or reorder steps.

STEP 1: Run `python3 session_c_extract.py "book_name"` — produces the COPY-PASTE BLOCK
STEP 2: Read the STRUCTURAL FLAGS section of the output — know what you're investigating
STEP 3: Web search (strategy depends on book type — see investigation plan)
STEP 4: Web_fetch at least 1 URL from search results
STEP 5: Write verdict — use the COPY-PASTE BLOCK as the skeleton. Only add your assessment, source citations, and verdicts. Do NOT retype any pipeline data values.
STEP 6: Re-run `python3 session_c_extract.py "book_name"` and verify every field matches what you wrote
STEP 7: Fix any discrepancy before moving on

After books 5 and 10: count verdicts and verify arithmetic.
After all 15: full critical self-review using systematic data verification.
</per_book_workflow>

<verdict_format>
Use this exact 14-field format for every book:

### Book N: {title}

- **Status:** {from extract tool}
- **Pipeline author:** {from extract tool} ({death date from extract tool})
- **Author verdict:** VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- **Author source:** {actual web sources found — cite URLs}
- **Pipeline genre:** {from extract tool, include both models}
- **Genre verdict:** VERIFIED/PLAUSIBLE/FLAG + reasoning
- **Pipeline ML:** {from extract tool, include both models}
- **ML verdict:** VERIFIED/PLAUSIBLE/FLAG + reasoning about layers
- **Pipeline science:** {from extract tool}
- **Science verdict:** VERIFIED/PLAUSIBLE
- **Trust tier:** {from extract tool — EXACT value}
- **Death date:** {value} — source: pass-through/extracted-from-raw/inferred/none
- **Model agreement:** {from extract tool}
- **Overall verdict:** VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- **Notes:** {structural flag analysis, layer verification, BUG-03 assessment}

VERIFIED = 2+ genuinely independent sources confirm
PLAUSIBLE = 1 source or extraction cross-check
UNVERIFIABLE = no sources found
FLAG = evidence suggests pipeline may be wrong
ESCALATE = cannot resolve
</verdict_format>

<source_independence_reminder>
shamela.ws + ketabonline.com + turath.io + waqfeya.net = ONE collective Shamela-ecosystem source.
Independent sources: ar.wikipedia.org, archive.org, noor-book.com, islamway.net, alukah.net, academic catalogs, publisher sites, government sites.
VERIFIED requires 2+ genuinely INDEPENDENT sources.
</source_independence_reminder>

<session_b_error_examples>
THESE ARE REAL ERRORS from the prior session. Study them to avoid repeating them.

ERROR TYPE: Memory transcription
WHAT HAPPENED: Book 10's verdict said muhaqiq="الألباني" when the actual muhaqiq was "سعد الحميد" — contamination from a different book.
PREVENTION: Copy-paste from extract tool output. Never write muhaqiq values from memory.

ERROR TYPE: Wrong pipeline field
WHAT HAPPENED: Book 5's verdict said trust_tier="flagged" when result.json shows trust_tier="verified" (0.7175). Also said science_scope=['nahw','sarf'] when actual is ['nahw','lughah'] (confused with Book 6).
PREVENTION: Re-run extract tool AFTER writing verdict. Compare every field.

ERROR TYPE: Insufficient research
WHAT HAPPENED: Book 4 (ابن العربي المتأخر) was flagged as "death date 617 doesn't match any known ابن العربي" — but tarajm.com confirms a grandson who died in 617 AH. The LLMs were correct.
PREVENTION: Always search for contradicting evidence. For classical scholars, search for family members and descendants, not just the famous namesake.

ERROR TYPE: False criticism of pipeline
WHAT HAPPENED: Book 8's verdict claimed "pipeline chose attribution=definitive which is wrong" — but result.json actually says "traditional." The pipeline was correct; the evaluator didn't check.
PREVENTION: Verify claims about pipeline behavior against actual result.json data before criticizing.
</session_b_error_examples>

<critical_self_review_requirement>
After completing all 15 verdicts, you MUST perform a systematic critical self-review:

1. Re-run `session_c_extract.py --all` and pipe to a file
2. For EACH book, verify: genre, ML, trust_tier, trust_score, science_scope, author_conf, death_date, attribution all match between your verdict and the extract tool output
3. Count verdicts (V/P/U/F/E) and verify against header claim
4. Check summary table book names match actual verdicts
5. Verify every "source confirms" claim maps to an actual search/fetch in the conversation
6. Fix ALL discrepancies found

This is not optional. Session B's critical review found 9 errors. The review is where quality is enforced.
</critical_self_review_requirement>

<output>
Produce: PHASE_D_SESSION_C_REPORT.md (committed to repo)
Update: NEXT.md with Session C results
If context remains: proceed to Session D (12 random calibration books) and/or Layer 4 aggregation.
Git: configure, commit, and push after completing Session C (don't wait until the end).
</output>

<quality_standard>
The owner invested €30+ and months of work in this pipeline. Every verdict you write becomes part of the GO/NO-GO decision for the source engine. A wrong FLAG wastes investigation effort. A missed error corrupts the library. Depth and accuracy over speed. Take all your time. Use all available tools. If you're uncertain, mark it UNVERIFIABLE — never guess.
</quality_standard>
