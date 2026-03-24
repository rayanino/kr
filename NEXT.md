# NEXT — Excerpting Engine: Harden LLM Integration Infrastructure

## Current Position

- **All code complete:** 556 tests (554 passed, 2 skipped), 0 failed, 28/28 error codes wired
- **LLM Integration Test Protocol:** ✅ `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md`
- **LLM calls tested with real models:** ❌ ZERO
- **Infrastructure for running those calls:** ❌ NOT YET HARDENED

## Principle: Harden Before Call

Every bug found AFTER making real LLM calls = re-running those calls = money and time wasted.
Every prompt gap found mid-test = untrustworthy results = re-run.
Every missing field in result storage = can't review properly = re-run.

**Before spending a single API dollar, the infrastructure must be bulletproof.**

## What to Harden (across next 1-3 sessions)

### 1. Prompts
- Read every LLM prompt in the engine (Phase 2a classification, Phase 2b grouping, Phase 3 enrichment, Phase 3 verification)
- Trace each prompt against its SPEC section — does the prompt implement what the SPEC says?
- Check for Arabic-specific issues: does the prompt handle diacritics correctly? Mixed LTR/RTL? Unicode edge cases?
- Run prompts on 1-2 fixture texts with a SINGLE manual API call (curl or script) and inspect the raw response — before running the full pipeline
- Fix any prompt gaps BEFORE running integration tests

### 2. Integration Run Script
- CC writes `scripts/run_integration_test.py` per protocol Phase B
- Save ALL intermediate outputs (Phase 1 chunks, Phase 2a/2b per-chunk, Phase 3 enrichment/verification per-chunk, raw LLM responses)
- Verify the script works end-to-end with MOCKED LLM calls first
- Then verify it works with ONE real call on ONE chunk — inspect saved outputs manually

### 3. Result Storage and Review Tooling
- Can the architect actually read and review the saved outputs?
- Write a review helper script that: loads a book's results, prints each excerpt with context (200 chars before/after), shows the boundary for decontextualization checks
- Test the review helper on mock data before real runs

### 4. Pydantic Parsing Robustness
- What happens when the LLM returns slightly malformed JSON? (Extra fields, missing optional fields, wrong enum values)
- Run the Instructor parsing on a few deliberately messy responses — does it retry correctly?
- Check MAX_TOKENS scaling — is the formula correct for different division sizes?

### 5. Error Recovery
- What happens when a single chunk's LLM call fails? Does the pipeline correctly skip that chunk and continue?
- What happens when the API rate-limits? Does retry with backoff work?
- What happens when the response is valid JSON but semantically wrong (e.g., segments don't cover the full text)? Does validation catch it?

## Read Before Starting

1. `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md`
2. `engines/excerpting/SPEC.md` §5.2.2 (classification prompt), §5.3.2 (grouping prompt), §7.2.2 (enrichment prompt), §7.3.2 (verification prompt)
3. `engines/excerpting/src/phase2_classify.py` — actual prompt construction code
4. `engines/excerpting/src/phase2_group.py` — actual prompt construction code
5. `engines/excerpting/src/phase3_enrichment.py` — actual prompt construction code
6. `engines/excerpting/src/phase3_consensus.py` — actual verification call code

## When Is Infrastructure "Hardened"?

- [ ] Every prompt traced against SPEC — no gaps
- [ ] Integration run script tested with mocked calls — saves all outputs correctly
- [ ] Integration run script tested with ONE real call on ONE chunk — output inspected manually
- [ ] Review helper script works on real output — architect can read and evaluate excerpts with context
- [ ] Pydantic parsing survives deliberately messy LLM responses
- [ ] Error recovery tested: chunk failure, rate limit, semantic validation failure
- [ ] All of the above committed and pushed

Only THEN do we run Round 1 of the protocol on 5 books.
