# Normalization Engine — Lessons Learned

**Engine:** Normalization (محرك التطبيع)
**Build:** 7 sessions, March 2026
**Evaluation:** 1 session, March 2026
**Final metrics:** 420 tests (14 skipped), 37/51 ADV, ~7,797 impl lines, 63/63 fixtures passing

---

## Bugs Found During Build

- **S2 F1 (HIGH):** `_detect_fn_section_format()` correctly classified bare-number footnotes but `FN_BOUNDARY_RE` requires `(N)` pattern — bare-number pages get no structured footnotes. Documented as L-001.
- **S4 F1 (HIGH):** Bold threshold of 80 chars from SPEC would produce zero matn segments because real ibn_aqil verses are 79 and 71 chars. Recalibrated to 50. Only found by running actual pipeline and printing output.
- **S5 F1 (HIGH):** Leading word-boundary needed for short markers: `ولنا` inside `فقولنا` (13.7% FP), `قلنا` inside `فقلنا` (33.3% FP). Both leading AND trailing boundaries required.
- **S6 F1 (HIGH):** CRLF line endings — `'\r\n\r\n'.split('\n\n')` returns 1 part on Windows. Systemic risk across all 7 engines. Every file-reading module needs CRLF normalization.
- **S7 F1 (MEDIUM):** Tautological test — parametrized test checked manifest == content_units (same code sets both). Would NOT catch silent page loss. Fixed by comparing against raw HTML PageText div count.
- **S7 F2 (MEDIUM):** Session 5 boundary continuity and Session 6 plain text normalizer had zero integration coverage until caught.

## Patterns Observed

### Arabic Text Processing

- **Conjunction prefix false positives are pervasive.** Any Arabic marker that is also a common verb stem (وذهب, ولنا, قلنا) will match inside conjugated forms. Always require word boundaries on both sides for markers under ~10 characters. Longer phrases (واعترض عليه بأن) are safe.
- **Bold span lengths cluster bimodally.** Emphasis bold in Shamela is typically 10-40 chars. Layer-indicator bold (matn verses) is typically 50-150 chars. The gap between 40 and 50 provides a clean separation threshold.
- **Quran citations in brackets trigger false multi-layer detection.** Texts with heavy bracket-quoted Quran citations (`[النساء: الآية 59]`) can trigger the auto-upgrade heuristic. The confidence levels (0.62-0.66) correctly reflect the uncertainty. Downstream engines should treat confidence < 0.70 as unreliable layer boundaries.
- **Diacritics preservation works.** The pipeline never applies Unicode normalization. Hadith texts with full tashkeel (04_hadith: 11,120 diacritics in 41 pages, ~271 per page) come through perfectly.

### Structure Discovery

- **Same-page headings are inherently ambiguous.** Page-level granularity cannot represent multiple same-level headings on one page as siblings. The chaining solution (L-003) is semantically wrong but structurally necessary. Sub-page offsets would fix this but require a SPEC-level design change.
- **HTML-tagged headings are highly reliable.** All `HTML_TAGGED` / `CONFIRMED` divisions in the test corpus are correct. Keyword heuristic headings (`HIGH` confidence) are also reliable. The risk is in `MEDIUM` and `LOW` confidence headings.
- **Division overlap is always from same-page headings.** All 22 overlap warnings across 5 fixtures trace to L-003. There are zero "real" overlaps from misdetection.

### Boundary Continuity

- **Punctuation analysis covers 97% of pages.** BC coverage averages 97.1%. The remaining 3% are last pages, blank pages, and the single 1-page fixture.
- **mid_argument detection fires on 35% of fixtures.** 22/63 fixtures have at least one mid_argument boundary, showing the argument flow markers are active and useful.
- **Conditional markers (إذا, لو, إن) are too frequent for BC.** إذا alone appears in 15-19% of pages. Excluding them was correct.

### Build Process

- **Empirical calibration beats theoretical thresholds.** Every threshold that was calibrated against real fixture data (bold=50, marker boundaries, distance heuristics) works correctly. Every threshold that was set theoretically (SPEC's bold=80) needed revision.
- **CC self-review catches cosmetic issues, not design flaws.** For architect-designed fixes, skip CC self-review — just run pytest. The quality gate is architect re-verification, not CC reviewing its own work.
- **Context degradation is real.** The quality of the last output in a long conversation is always the worst. Start new sessions for reviews, transitions, and any verification of prior work.
- **Post-protocol adversarial pass found issues every time.** S6: CRLF. S7: tautological tests + missing coverage. Evaluation: auto-upgrade false positives + CRLF untested on Windows + plain text untested in integration. The unconstrained pass is the most effective quality mechanism after tool-based verification.

## What Went Wrong

- **S4: SPEC example trace skipped.** 16 probing scripts ran but the most obvious test (trace the SPEC's own example through the code) was skipped. When finally run, it found L-007. Volume of probes ≠ completeness.
- **S5: Markers added without data (لأن, وقال).** Both had 4-17% fire rates — too broad. Don't add markers not in SPEC without empirical validation.
- **S7: Test counted coverage by session but not BY FEATURE.** Sessions 5 and 6 had zero integration coverage until the adversarial pass caught it. Coverage must be tracked per feature, not per session.

## What Worked

- **Test factory pattern (conftest.py).** `_make_source_metadata(**overrides)` with 23 sensible defaults eliminated boilerplate across all test files. Every new session reused it.
- **Extended fixtures (50 books).** Added at S6 as smoke test targets. Found L-010 (14% overlap rate), confirmed CRLF fix, and validated at scale. Cost: 0 (deterministic).
- **3-round review protocol.** Pass 1 (structural) → Pass 2 (adversarial) → Pass 3 (self-verify + verdict). The context break between rounds consistently found issues the previous round missed.
- **Silent page loss check.** Comparing raw PageText div count against content unit count catches the most dangerous normalization failure. Added to every integration test.

## Recommendations for Passaging Engine

1. **Treat layer confidence < 0.70 as unreliable.** The auto-upgrade heuristic produces low-confidence layers on bracket-heavy texts. Passaging should flag `mixed_layers` on passages with low-confidence layer boundaries.
2. **Division overlap fallback is already handled.** Passaging SPEC §2 check 6 correctly falls back to flat passaging for inconsistent divisions. No additional work needed.
3. **boundary_continuity is the primary joining signal.** 97% coverage with correct classifications. Passaging should prefer BC signals over character-level heuristics whenever BC confidence ≥ 0.70.
4. **Content flags are pass-through.** has_hadith, has_quran, has_verse are per-page booleans. Passaging aggregates them per passage (OR across constituent pages). No special handling needed.
5. **Footnote renumbering is passaging's responsibility.** Normalization produces per-page `⌜N⌝` markers. Passaging must renumber when assembling cross-page passages.
6. **CRLF: test on actual Windows data.** The fix is in place but untested on real CRLF files. Verify during first full-collection run.
7. **Monitor auto-upgrade false positives at scale.** When running on 2,519 books, spot-check any book that auto-upgrades to multi-layer when source metadata says single-layer.

## Impact on Downstream Engines

### For Passaging

- **Normalization output is reliable.** 63/63 fixtures produce valid packages. Zero fatals. Contract alignment verified.
- **Division tree is advisory.** Use for boundary guidance but don't assume non-overlapping siblings (L-010). Flat passaging fallback handles the rare overlap case.
- **Layer segments are informational.** Confidence reflects detection quality. Low confidence = uncertain boundaries.

### For Excerpting (further downstream)

- **L-001 limits footnote granularity.** Bare-number footnotes are unstructured. Excerpting won't be able to cite individual footnotes for these pages.
- **L-006 limits 3-layer attribution.** Hashiyah quotations of sharh text are misattributed until hashiyah detection is implemented.
- **L-007 limits matn boundary precision.** Marker-only matn over-extension may cause some sharh text to carry matn attribution.
