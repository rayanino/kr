You are critically reviewing the Phase D evaluation of the KR source engine. Your job is NOT to trust or agree with the evaluation — it is to find everything that's wrong with it, test every claim, and give the owner an honest assessment of whether the GO verdict holds under scrutiny.

<context>
The source engine is the first of 7 engines in the KR pipeline. It processes Arabic Islamic scholarly texts from the Shamela digital library, extracting metadata (author, genre, multi-layer classification, science scope, trust tier). 204 books were processed. 60 were evaluated by Claude Chat across 4 sessions (A–D). The evaluator produced a GO verdict with 3 mandatory fixes. The evaluator also disclosed several methodology failures found during self-review — AFTER the owner had to ask for it.

The owner needs to decide: Does this evaluation support GO? Are the mandatory fixes correctly scoped? Is anything missing?
</context>

<startup_sequence>
1. Clone repo: `git clone https://{github_token_from_project_files}@github.com/rayanino/kr.git /home/claude/kr`
2. Read `PHASE_D_REVIEW_PREPARATION.md` — comprehensive guide to what needs examining, including disclosed weaknesses
3. Read `NEXT.md` — current state
4. Read `PHASE_D_AGGREGATION_REPORT.md` — the GO verdict (focus on evaluation limitations section and error classification)
5. Read `PHASE_D_SESSION_ERRATA.md` — 7 rules the evaluator was supposed to follow
</startup_sequence>

<your_mandate>
You are an adversarial reviewer. Assume the evaluation has errors until proven otherwise. Your specific tasks:

TASK 1 — SPOT-CHECK VERIFIED VERDICTS
Pick 3-5 VERIFIED books from Sessions C and D (the ones with ERRATA-02 violations). For each:
- Run the extract tool to get pipeline data
- Do your OWN web search (independent of what the evaluator claimed)
- Compare pipeline output against what you find
- Would YOU give VERIFIED, or a lower verdict?

TASK 2 — EXAMINE ALL 5 FLAG BOOKS
For each FLAG book, read the verdict in the session report, then independently verify:
- Is the flag justified? Could it be worse than flagged?
- Is the proposed fix correct? Could there be a different root cause?
- Are there books that SHOULD be flagged but weren't?

TASK 3 — DEATH DATE HALLUCINATION AUDIT
9 death date disagreements exist. The evaluator confirmed 3 are hallucinations. Check the other 6:
- Were the Session A/B evaluators' assessments of these disagreements correct?
- Verify أساليب بلاغية (Opus: 1441, CA: None) — is 1441 correct?
- Verify جزء ابن عمشليق (Opus: None, CA: 400) — is 400 correct?

TASK 4 — METHODOLOGY AUDIT
Read the session reports and check:
- Did Sessions A and B actually follow ERRATA rules better than C/D?
- Count actual web_search and web_fetch tool calls per session
- Are there verdicts where the "source" cited doesn't match any visible search result?
- Check Session B's "9 errors in 19 verdicts" — were all truly fixed?

TASK 5 — GO VERDICT CHALLENGE
Build the strongest possible case AGAINST GO. Consider:
- The 144 unevaluated books
- The 1.7% hard error rate and what it means at scale (2,519 books)
- The genre consensus failure (إعلام الموقعين)
- Whether the 3 mandatory fixes are sufficient or need expansion
Then: does the case against GO actually hold? Or is GO justified despite these concerns?

TASK 6 — OWNER DECISION SUPPORT
Present findings organized by the owner decisions listed in PHASE_D_REVIEW_PREPARATION.md §6. For each decision, provide your recommendation with reasoning.
</your_mandate>

<tools>
```bash
# Extract pipeline data for any Session C book
python3 session_c_extract.py "book_name"
python3 session_c_extract.py --all

# Extract pipeline data for any Session D book  
python3 session_d_extract.py "book_name"
python3 session_d_extract.py --all

# Read any book's full pipeline data
python3 read_book.py "book_name"

# Raw data access
cat tests/results/source_engine/phase_d/{book_name}/result.json
cat tests/results/source_engine/phase_d/{book_name}/extraction.json
cat tests/results/source_engine/phase_d/{book_name}/llm_responses/*.json
```
</tools>

<output>
Produce: `PHASE_D_CRITICAL_REVIEW.md` committed to repo.
Structure: Task-by-task findings, then overall assessment, then owner decision recommendations.
Standard: Every claim must be grounded in a tool call or web search visible in the conversation. No domain-knowledge citations without search verification.
</output>

<quality_standard>
The owner invested months and €30+ in this pipeline. A wrong GO wastes the next phase's budget on a broken foundation. A wrong NO-GO wastes time fixing things that don't need fixing. This review determines which. Be thorough. Be honest. Take all your time.
</quality_standard>
