# KR CC Handoff Protocol — 9-Step Mandatory Process

**Authority:** GOVERNING — mandatory before committing ANY NEXT.md. Supersedes PRE_HANDOFF_VERIFICATION.md (Session 2) which is now archived.

**Failure history:**
- Session 2: handoff committed without verification → 4 foundation bugs (regex range, metadata page conflation, missing CleanedPage field, image-only pages dropped). All caught by pre-commit tool-based review.
- Session 5: improvised review produced 25 findings but skipped formal protocol → missed worst bug (confidence 0.70 vs SPEC 0.90) until 3rd pass after owner pushback. Volume of findings ≠ completeness.
- Session 6: completed all 9 steps, declared ready. Owner-forced deep review found 8 issues (1 HIGH — CRLF splitting breaks plain text on Windows). Root cause: the protocol tests specification-level issues but not assumption-level issues (platform, import chains, data flow, silent drops). Steps 6 and 8 updated to close this gap.
- Session 7: completed all 9 steps including S6 improvements, declared ready. Owner-forced critical review found 4 issues (1 HIGH — parametrized test couldn't detect silent page loss, 2 MEDIUM — boundary continuity and plain text normalizer had zero integration coverage, 1 MEDIUM — Do NOT Do contradicted Verification). Root cause: protocol asks "is the handoff correct?" but not "is the handoff complete?" Steps 8.8, 8.9, and 8b added.

**Rule:** Follow steps 1–9 in order. Do not skip, reorder, or "cover the spirit" without following the letter. Reading this protocol then improvising is NOT following it.

---

## Step 1: Establish context

Answer from files read in THIS session (not memory):
1. What phase? (SPEC design / Build / Evaluate / Harden / Complete)
2. Previous session output? (git log)
3. AGENT_ARCHITECTURE.md requirements for this phase?
4. ENGINE_BUILD_BLUEPRINT.md requirements for this step?

## Step 2: Run test baseline

```bash
python -m pytest engines/{engine}/tests/ -v --tb=short
```

Record exact count: `N passed, M skipped`. Goes in NEXT.md header AND pass criteria. Never use count from memory (S5: memory said 172, actual was 173).

## Step 3: Verify every file reference

For each Read First file: `ls` to verify exists, `view` the referenced lines to verify content, `git log -1` to verify not stale. Line numbers are especially fragile — they shift after every commit.

## Step 4: Write the NEXT.md

Required sections: Current position (with verified test count), What to do, Context, Owner action needed, Read First, What to Build (with SPEC section refs), Design Decisions (pre-resolved), Do NOT Do, Verification (with `python tools/validate_handoff.py` as first check), After This.

## Step 5: Trace SPEC concrete examples (NON-NEGOTIABLE)

For every SPEC section referenced in the handoff: find its concrete example, construct the exact input, walk through the algorithm step by step with **tool execution** (Python, not mental simulation), compare output field-by-field against SPEC expected.

S4: skipped → missed L-007. S5: skipped twice → missed confidence corroboration (0.70 vs 0.90). This single step has caught the worst bug in every session where it was eventually run.

## Step 6: Test algorithm on real fixture data

For any new detection logic (markers, patterns, heuristics), run against ALL fixture pages:

```python
for fixture in os.listdir('tests/fixtures/shamela_real'):
    # count matches, false positives, false negatives
```

Check: false positive rate (S5: إذا at 12.6% → excluded), substring collisions (S5: وذهب matching وذهبت → word-boundary added), false negatives against known positives.

Also from Session 2: for any regex, construct match/no-match/edge-case inputs and run them. For any parser/library, test the exact use case with Arabic text (diacritics, entities, Unicode).

**Even if no new detection logic was added:** run the pipeline end-to-end on ALL repo fixtures (shamela_real + shamela_extended) as a smoke test. This catches integration failures, import errors, and assumption bugs that unit tests miss. S6: the CRLF bug would have been caught by running the plain text normalizer on a single Windows-encoded fixture.

## Step 7: Automated + manual checks

Run automated validation:
```bash
python tools/validate_handoff.py
```

Then fill `reference/protocols/HANDOFF_CHECKLIST_TEMPLATE.md`:
- Test baseline verified (Step 2)
- All Read First files exist with verified line numbers
- SPEC sections referenced specifically
- Do NOT Do covers scope creep
- Verification has concrete pass/fail
- AGENT_ARCHITECTURE.md checked
- ENGINE_BUILD_BLUEPRINT.md checked
- Fixture claims verified by running code
- SPEC thresholds copy-pasted with line numbers
- All SPEC examples traced (Step 5)
- New detection logic tested on fixtures (Step 6)
- Cross-engine contracts verified (separate enums, compatible values)

Every box must be checked. Do not rationalize skipping a box.

## Step 8: Adversarial read

Re-read NEXT.md as CC seeing it for the first time:
1. Any judgment call not covered by SPEC or Design Decisions?
2. Any file needed that isn't in Read First?
3. Any ambiguity about what "done" means?
4. Could CC follow instructions and produce wrong output that passes verification?
5. Any unverified claim about fixtures or SPEC values?
6. Any missing test helpers CC will need?
7. What platform assumptions does this code make? (CRLF line endings, path separators, encoding defaults, OS-specific behavior.) The owner is on Windows. S6: `'\r\n\r\n'.split('\n\n')` returns 1 part — a HIGH-severity bug missed by questions 1-6.
8. Do the "Do NOT Do" items contradict anything in the Verification section? S7: "Do NOT run against shamela-export-samples/" contradicted the smoke test verification command which samples from that directory.
9. For every test assertion: what BROKEN implementation would still pass it? If it checks only internal consistency (field A matches field B, both set by the same code), it's tautological. S7: `manifest.total_content_units == len(content_units)` would not catch silent page loss — both values set by the same code path.

## Step 8b: Coverage completeness (integration/final sessions only)

For each prior build session (1..N-1), name the specific integration test that exercises that session's primary output. If none exists, add one. This step exists because S7's handoff had zero integration coverage for Session 5 (boundary continuity) and Session 6 (plain text normalizer) — caught only when the owner forced a deep critical review.

| Prior Session | Primary Output | Integration Test |
|---|---|---|
| Session 1 | contracts.py | (tested by all integration tests that use contracts) |
| Session 2 | Passes 1-3 | test_content_preservation, test_footnote_separation |
| Session 3 | Structure discovery | test_structure_discovery |
| Session 4 | Layer detection | test_multi_layer_detection |
| Session 5 | Boundary continuity | ??? ← if empty, add one |
| Session 6 | Plain text normalizer | ??? ← if empty, add one |

## Step 9: Commit and declare

Only after Steps 1–8 complete. Run `python tools/validate_handoff.py` one final time on the committed version. Push. State commit hash.

**The momentum trap:** The urge to declare "ready" is strongest after finding many issues. That feeling is the signal to re-check Steps 5–7, not to commit.
