# CC Review Checklist — Session 7: Integration Testing & ADV Gap Closure

> **This file is the review artifact.** Fill every checkbox, commit this file, THEN deliver the verdict.
> An unfilled checklist = an incomplete review. Do NOT deliver a verdict without committing this file.
> **REVIEW_PROTOCOL.md is the authority — NOT the kr-reviewing-cc-output skill's verdict template.**

## Pre-review
- [x] Repo pulled, commit diff read (`git diff c69af30..26a5ed2`: 4 files, 605 insertions)
- [x] NEXT.md re-read — Session 7 handoff: testing-only, zero src/ changes, 25 test methods across 6 classes

## Pass 1: Structural
- [x] Every CC-modified file opened and read **in full** (not truncated) — list files:
  - [x] `engines/normalization/tests/test_integration.py` — 6 classes, 27 functions (25 test methods + 2 helpers). Verified by AST parse: TestShamelaNormalizer(9), TestContentFlagger(3), TestContentCensus(1), TestFixtureIntegration(1 parametrized x63), TestNormalizeAndWrite(3), TestAdversarialGap(8).
  - [x] `engines/normalization/tests/test_kr_output.py` — 12 skip reason updates (diff-only read, changes are string literals)
  - [x] `engines/normalization/CLAUDE.md` — 2 lines changed: Session 7 marked done, metrics updated to 420/14/37
  - [x] `engines/normalization/KNOWN_LIMITATIONS.md` — 12 lines added: L-012 (Arabic-Indic footnote markers, ADV-023)
  - **RULE 7 check:** test_integration.py read in full (579 lines, no truncation). Function/class counts verified by grep and AST parse.
- [x] All tests run: `420 passed, 14 skipped, 0 failed` (in 9.43s)
- [x] SPEC cross-reference: every function traces to a documented SPEC section or ADV case
- [x] **Cross-engine boundary check:**
  - [x] `git diff c69af30..26a5ed2 -- engines/normalization/contracts.py` -> empty (no contract modifications)
  - [x] `PYTHONIOENCODING=utf-8 python tools/check_cross_engine_contracts.py` -> result: **PASS** ("All shared field constraints are consistent across engines")
  - [x] Each downstream consumer verified: passaging imports FootnoteType, HeadingConfidence, LayerType, TextFidelityLevel — all unchanged
  - Modified types: **none** (Session 7 is testing-only)
  - Consumers checked: `engines/passaging/contracts.py` (line 17-22)

## Pass 2: Adversarial
- [x] 5 probing scripts run with constructed inputs — findings:
  - Probe 1: ADV-020 duplicate page numbers -> 2 units, idx 0+1, both page_num=12. **PASS**
  - Probe 2: ADV-022 trailing kasra -> U+0650 present in output, last codepoints match input. **PASS**
  - Probe 3: ADV-049 page number overflow -> no crash, page_number_int=999999999999999. **PASS**
  - Probe 4: ADV-034 footnote markers -> corner brackets present, (1) absent, 1 footnote extracted. **PASS**
  - Probe 5: ADV-040 Arabic filenames -> NORM_VOLUME_NUMBER_UNPARSEABLE logged, volumes [1,2]. **PASS**
- [x] 3 fixture semantic spot-checks — printed actual Arabic text:
  - Fixture 1: `04_hadith` — 36/41 hadith flags (test asserts >=30). First unit: scholarly hadith chain.
  - Fixture 2: `02_nahw_muhaqiq` — 5 multi-layer units (test asserts >=3), 19 divisions (test asserts >=5), layers: matn+sharh
  - Fixture 3: `01_nahw_simple` — 72/73 boundary continuity (test asserts >=50%), 4 distinct types (test asserts >=2), all confidence >0
- [x] Cross-engine data flow: JSON round-trip verified. NormalizedPackage serializes to valid JSON. All required fields present. Passaging types (LayerType, TextFidelityLevel) correctly used as enums.
- [x] **SPEC concrete example trace (RULE 5):**
  - [x] SPEC 4.A.2 Pass 2 (footnote separation) traced on 03_fiqh — 32/102 pages with footnotes, correctly separated. Implementation output matches SPEC intent.
  - [x] Divergences: none found
- [x] F1-F4 critical fix verification:
  - [x] F1 (page-loss check): BeautifulSoup + lxml imports raw HTML, counts PageText divs, compares to content_units with tolerance 5. **SUBSTANTIVE**
  - [x] F2 (boundary continuity): Tests >=50% coverage, >=2 distinct types, confidence >0 on real 01_nahw_simple output. **SUBSTANTIVE**
  - [x] F3 (plain text write): Calls normalize_and_write() with source_format='plain_text', verifies manifest.json + content.jsonl exist, verifies content. **SUBSTANTIVE**
  - [x] F4 (Do NOT Do #5): _discover_fixtures() only searches shamela_real + shamela_extended. grep confirmed zero shamela-export-samples references. **COMPLIANT**
- [x] ADV tautology check: 8 ADV tests verified against catalog. None tautological. ADV-019 weakest (real fixtures vs adversarial malformed input) but follows handoff design and catalog's own detection method.
- [x] Edge case probes with constructed inputs: 5 run, 0 findings

## Pass 3: Self-verification (RULES 6-7)
- [x] Every factual claim in Passes 1-2 verified against code with tool calls:
  - [x] "9 test methods in TestShamelaNormalizer" — verified by AST parse (returns 9)
  - [x] "3 test methods in TestContentFlagger" — verified by AST parse (returns 3)
  - [x] "8 test methods in TestAdversarialGap" — verified by AST parse (returns 8)
  - [x] "63 fixture PASSED" — verified by grep count (returns 63)
  - [x] "37 ADV cases" — verified by grep sort -u wc -l (returns 37)
  - [x] "Zero src/ changes" — verified by git diff (empty)
  - [x] "lxml in requirements.txt" — verified by grep (returns lxml>=4.9)
  - [x] "ADV-038 covered by test_writer.py" — verified by reading test_writer.py line 149-153
  - [x] "_resolve_input_files handles directories" — verified by reading shamela.py line 523-577
  - [x] "L-012 references shamela.py line 115-122" — verified by grep
  - [x] "_make_source_metadata accepts source_format/source_id" — verified by reading conftest.py line 59
- [x] Check for rationalization patterns: 7 "not a finding" conclusions re-examined. All grounded in tool-verified evidence. No rationalization detected.
- [x] Review Notes drafted — each Note verified against code before writing

## Findings

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| — | — | No findings | — | — |

## Fixes committed
- [x] ALL findings above have `Fixed? [x]` (N/A — zero findings)
- [x] Fix commits pushed to repo (N/A — zero fixes needed)
- [x] Tests re-run after fixes: 420 passed (N/A — no changes)
- [x] `python tools/check_cross_engine_contracts.py` re-run after fixes -> PASS (N/A — no changes)

## Verdict

**Verdict: ACCEPT**

## Build metrics (cumulative)
```
Implementation: ~7,130 lines (+0 this session — testing only)
Tests: 420 passing (+85 this session, of which 63 parametrized fixture tests)
Skipped: 14 (12 superseded in test_kr_output.py + 1 census deferred + 1 ADV-038 covered elsewhere)
Test-to-code ratio: 5.9 tests per 100 impl lines
ADV covered: 37/51 (Session 7 added: ADV-019, 020, 022, 034, 038 documented, 040, 048, 049)
Known limitations: L-001 through L-012
SPEC sections implemented: 4.A.1-9, 4.B.8, 5.1-10
SPEC sections remaining: 4.B.1-7, 4.B.9-10 (all deferred per CORE_EXTRACTION.md)
```

## Post-ACCEPT housekeeping
- [x] CLAUDE.md build session table updated (Session 7 marked done, metrics updated)
- [x] Any SPEC inconsistencies found: none
- [x] NEXT.md updated for next session (handoff prepared)

## Observations (not findings — informational only)

1. **ADV-048 text_fidelity not downgraded:** The normalizer keeps text_fidelity `high` after Windows-1256 encoding fallback. The ADV catalog suggests it should be `low`. Pre-existing implementation behavior — Session 7 scope was testing-only (no src/ changes). Recommend addressing in a future maintenance pass.

2. **test_content_flags adapted from handoff:** NEXT.md said "verify 0 or very few hadith flags in 01_nahw_simple." Actual is 28/73 (38.4%) because grammar texts cite hadith for grammatical illustration. CC correctly adapted to a density ratio comparison (38.4% < 87.8%). Domain-appropriate.

3. **CLAUDE.md line count approximations:** "~7,797 impl lines" is inherited from Session 6 and overcounts by ~10%. "~400 integration test lines" undercounts (actual: 579). Both use tilde (~) prefix. Informational, no behavioral impact.

4. **html5lib not in requirements.txt:** CLAUDE.md mentions "Dependency: html5lib" but it's not in requirements.txt. Pre-existing — unrelated to Session 7.
