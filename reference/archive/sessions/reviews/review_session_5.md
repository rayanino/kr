# CC Review Checklist — Session 5: Pass 6 Assembly (Content Flagging, Boundary Continuity, Output)

> **This file is the review artifact.** Fill every checkbox, commit this file, THEN deliver the verdict.  
> An unfilled checklist = an incomplete review. Do NOT deliver a verdict without committing this file.  
> **REVIEW_PROTOCOL.md is the authority — NOT the kr-reviewing-cc-output skill's verdict template.**

## Pre-review
- [x] Repo pulled, commit diff read
- [x] NEXT.md re-read — what was requested?

## Pass 1: Structural
- [x] Every CC-modified file opened and read **in full** (not truncated) — list files:
  - [x] `src/content_flagger.py` (153L) — 4 functions (verified: `grep -c "^def " → 4`)
  - [x] `src/boundary_continuity.py` (266L) — 7 functions (verified: `grep -n "^def "` lists 7)
  - [x] `src/normalizers/shamela.py` (+202L) — 1 new method `_pass6_assemble` (verified at line 1050)
  - [x] `src/structure_discovery.py` (+4L) — `toc_page_indices` field added to `StructureResult` + populated in return
  - [x] `tests/conftest.py` (188L) — shared test infrastructure extracted from test_layer_detection.py
  - [x] `tests/test_content_flagger.py` (247L) — 30 tests (verified by pytest --co)
  - [x] `tests/test_boundary_continuity.py` (335L) — 28 tests (verified by pytest --co)
  - [x] `tests/test_pass6_assembly.py` (259L) — 18 tests (verified by pytest --co)
  - [x] `tests/test_layer_detection.py` (-177L) — extraction to conftest only, no logic changes
  - [x] `KNOWN_LIMITATIONS.md` (+18L) — L-008, L-009 added
  - **RULE 7 check:** shamela.py was viewed in ranges (469-520, 943-960, 1050-1244). No truncation issues — all ranges read completely.
- [x] All tests run: `253 passed, 22 skipped, 0 failed`
- [x] SPEC cross-reference: every function traces to a § rule
  - `compute_content_flags` → §4.A.9
  - `classify_boundary` → §4.B.8
  - `_pass6_assemble` → §4.A.2 Pass 6
  - `StructureResult.toc_page_indices` → §4.A.9 (TOC page detection)
- [x] **Cross-engine boundary check:**
  - [x] `grep -rn` for every modified contract type across ALL engines
  - [x] `python tools/check_cross_engine_contracts.py` → result: `PASS`
  - [x] Each downstream consumer verified to accept the new shape
  - Modified types: `StructureResult` (added `toc_page_indices: list[int]` with default_factory=list)
  - Consumers checked: `grep -rn "StructureResult" engines/` — only normalization-internal (structure_discovery.py, test_structure_discovery.py). Zero downstream consumers.

## Pass 2: Adversarial
- [x] 3+ probing scripts run with constructed inputs — findings:
  - Probe A: SPEC §4.B.8 concrete example trace → type=mid_argument, method=argument_flow match SPEC. Confidence=0.80 vs SPEC example 0.90 (SPEC internal contradiction — definition says 0.60–0.80, example says 0.90). See SPEC-NOTE-1.
  - Probe B: Marker table comparison → SPEC vs impl divergence quantified. `لأن` fires 17% tafsir, `وقال` fires 4.1-7.1%. **FINDING 1.**
  - Probe C: `_find_argument_marker` leading boundary → `ولنا` matches inside `فقولنا` on ibn_aqil page 0. 29/211 (13.7%) false positives corpus-wide. **FINDING 2.**
  - Probe D: Connective hint rate → 34.3% of pages. Advisory-only, acceptable.
  - Probe E: Regex edge cases → guillemet 50-char boundary correct, ornate brackets correct, multi-space قال تعالى correct.
- [x] 2+ fixture semantic spot-checks — printed actual Arabic text:
  - Fixture 1: ibn_aqil — full pipeline produces 5 content units, page 0 has matn [0:79] + sharh [79:270], footnote type=TAHQIQ_EDITOR with Arabic ref text. Text looks correct semantically.
  - Fixture 2: 05_tafsir — ≥2 content units with has_quran_citation=True (confirmed via test).
  - Fixture 3: 03_fiqh — mid_argument on 25.5% of pages (inflated by وقال/لأن, see FINDING 1).
- [x] Cross-engine data flow: `check_cross_engine_contracts.py` passes. NormalizedPackage schema unchanged. Passaging imports (FootnoteType, HeadingConfidence, LayerType, TextFidelityLevel) not modified.
- [x] **SPEC concrete example trace (RULE 5):** For each SPEC section with a worked example:
  - [x] SPEC §4.A.9 example traced — all 7 flags match expected output field-by-field. **PASS.**
  - [x] SPEC §4.B.8 example traced — type and method match. Confidence 0.80 vs 0.90. Divergence: SPEC internal contradiction (SPEC-NOTE-1).
  - [x] Divergences: SPEC-NOTE-1 (confidence 0.80 vs 0.90). Classified as: SPEC maintenance, not code finding. The code follows the definition range (0.60–0.80), the example's 0.90 requires an unspecified blending mechanism.
- [x] Edge case probes with constructed inputs: 6 regex edge cases run, all correct.

## Pass 3: Self-verification (RULES 6-7)
- [x] Every factual claim in Passes 1-2 verified against code with tool calls:
  - [x] "4 functions in content_flagger" — verified: `grep -n "^def " → 4 results`
  - [x] "7 functions in boundary_continuity" — verified: `grep -n "^def " → 7 results`
  - [x] "253 tests pass, 80 new" — verified: pytest re-run → 253 passed; new-only re-run → 80 passed
  - [x] "لأن fires 17% on tafsir" — verified: re-run → 8/47 = 17.0%
  - [x] "ولنا matches inside فقولنا" — verified: re-run → pos=83, char before=[ق]
  - [x] "29/211 false positives" — verified: re-run → 29/211 = 13.7%
  - [x] "SPEC §4.A.9 all flags match" — verified: re-run all 7 assertions pass
  - [x] "StructureResult internal only" — verified: grep returns 0 results outside normalization/
  - [x] "normalization_warnings defaults to []" — verified: `Field(default_factory=list)` at line 693
  - [x] "cross-engine contracts pass" — verified: re-run → "All shared field constraints are consistent"
- [x] Check for rationalization patterns: any finding I downplayed or explained away?
  - CONCERN 3 (connective particles): Not rationalized — hints are genuinely advisory-only, do not change boundary type.
  - CONCERN 5 (normalization_warnings): Not rationalized — SPEC says "engine-level warnings," no specific warnings mandated for Shamela.
  - SPEC-NOTE-1 (confidence 0.80 vs 0.90): Not rationalized — code follows the definition range (0.60–0.80); the example's 0.90 requires an unspecified blending mechanism not in the SPEC.
  - FINDINGS 1-2: Not manufactured — backed by quantified empirical data (17% fire rate, 13.7% FP rate).
- [x] Review Notes drafted — each Note verified against code before writing

## Findings
> List ALL findings. There are no "non-blocking" findings. Every finding listed here must be FIXED before the verdict line below is filled.

| # | File | Finding | Fix | Fixed? |
|---|------|---------|-----|--------|
| 1 | `src/boundary_continuity.py` | Over-broad markers `لأن` (evidence_chain) and `وقال` (position_statement) not in SPEC table, fire on 4.1–17% of fixture pages, account for 82% of all opener hits. Inflates mid_argument classifications. | Remove `لأن` from evidence_chain.opening_patterns. Remove `وقال` from position_statement.opening_patterns. | [x] Fixed in e07ac6e. Post-fix rates: fiqh 11.8%, tafsir 0%, nahw 1.0–1.4%. |
| 2 | `src/boundary_continuity.py` | `_find_argument_marker` only checks trailing word boundary (`_has_word_boundary_after`), not leading. 29/211 occurrences (13.7%) are substring false positives (e.g., `ولنا` inside `فقولنا`). | Add `_has_word_boundary_before(text, match_start)` check: verify `pos == 0 or text[pos-1]` is space/punct/line boundary. Apply to all marker matches alongside existing trailing check. | [x] Fixed in e07ac6e. فقولنا/ولنا returns False, standalone ولنا returns True, فقلنا/قلنا returns False. 3 new tests. |

## SPEC notes (for SPEC maintenance — not code fixes)

- **SPEC-NOTE-1:** §4.B.8 definition says mid_argument confidence 0.60–0.80. §4.B.8 concrete example says 0.90 via unspecified blending. Reconcile in next SPEC pass.
- **SPEC-NOTE-2:** §4.B.8 concrete example uses `ولنا حديث` as evidence opener but `ولنا` is absent from the SPEC marker table. Add to SPEC table.

## Fixes committed
- [x] ALL findings above have `Fixed? [x]`
- [x] Fix commits pushed to repo (commit e07ac6e)
- [x] Tests re-run after fixes: `256 passed, 22 skipped, 0 failed`
- [x] `python tools/check_cross_engine_contracts.py` re-run after fixes → `PASS`

## Verdict
> Fill this line ONLY after Passes 1, 2, AND 3 are complete, every checkbox is checked, and every finding is fixed.
> The verdict is NEVER delivered in the same response as Pass 2 probes (RULE 8).
> **ACCEPT** = zero unfixed findings, repo clean.  
> **BLOCKED** = findings exist that couldn't be fixed in this review.  
> "ACCEPT WITH FIXES" does not exist. "Non-blocking" does not exist.

**Verdict: ACCEPT — Both findings fixed in e07ac6e. Re-verified: 256 tests pass, false positive rate eliminated, SPEC §4.A.9 and §4.B.8 concrete examples trace correctly, ibn_aqil boundary types now semantically correct, cross-engine contracts PASS.**

## Build metrics (cumulative)
```
Implementation: ~6,285 lines (+~637 net new this session including fix)
Tests: 256 passing (+83 this session)
Test-to-code ratio: ~4.1 tests per 100 impl lines
ADV covered: ADV-001–018, ADV-024, ADV-026, ADV-050, ADV-051 (22/51)
Known limitations: L-001 through L-009
SPEC sections implemented: §4.A.1–§4.A.9, §4.B.1, §4.B.8
SPEC sections remaining: §5 validation, §6 output, plain text normalizer
```
