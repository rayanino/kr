# Cumulative Overnight Findings — Excerpting Engine

Aggregated from all overnight runs. Each entry is permanent knowledge derived from paid testing.

---

## Run: 2026-03-28 — Stable Foundation Hardening

5 tasks scheduled. 4 completed with findings. 1 incomplete (phase1-error-codes hit max_turns).

### Bugs Found

| Severity | File | Line | Description | Fixed |
|----------|------|------|-------------|-------|
| MEDIUM | `engines/excerpting/src/phase3_deterministic.py` | 449 | `filter_relevant_footnotes` uses `assembled_text.find(pattern)` — first-occurrence-only semantics. If a ref_marker appears twice in assembled_text and the first occurrence is outside the unit's char range but a second is inside, the footnote is silently excluded. | No |
| LOW | `engines/excerpting/src/phase3_deterministic.py` | 163 | `compute_excerpt_id` uses `_` as both separator and valid character in source_id/div_id, making IDs non-reversible by parsing (ambiguous split). Safe for equality comparison only. | No |

### Tests Added

**Total: 142 tests added (597 → 739)**

#### `test_boundary_exhaustive.py` — 16 tests (597→613)
Boundary values for TINY_DIVISION_WORDS=50, OVERSIZED_DIVISION_WORDS=5000, LA-1 threshold=80%, gap repair limit=5 chars.
- `test_merge_49_words` — one below TINY (must merge)
- `test_merge_50_words_standalone` — exactly at TINY (must NOT merge — strict <)
- `test_merge_51_words_standalone` — one above TINY (must NOT merge)
- `test_merge_1_word` — trivially tiny
- `test_merge_0_words_with_sibling` — non-Arabic content (0 Arabic words) still merges
- `test_split_4999_words_no_split` — one below OVERSIZED (must NOT split)
- `test_split_5000_words_no_split` — exactly at OVERSIZED (must NOT split — strict >)
- `test_split_5001_words_must_split` — one above OVERSIZED (must split)
- `test_split_10001_words_recursive_three_chunks` — recursive split required (V-P1-4)
- `test_la1_at_79_point_9_percent` — falls to LA-2 (below 80% threshold)
- `test_la1_at_80_point_1_percent` — triggers LA-1 (above 80%)
- `test_la_two_layers_each_50_percent` — LA-2 (outermost layer wins)
- `test_la_three_layers_each_33_percent` — LA-3 (ambiguous, flag for consensus)
- `test_layer_gap_4_chars_repaired` — 4-char gap → auto-repair + EX-A-003
- `test_layer_gap_5_chars_repaired` — 5-char gap (exact boundary) → auto-repair
- `test_layer_gap_6_chars_fatal` — 6-char gap (one above limit) → I-AC-2 FATAL

#### `test_pathological_arabic.py` — 40 tests (613→653)
Pathological Arabic Unicode inputs across 8 classes: diacritics-only, Arabic/Latin mixed, tatweel-only, max Unicode diversity, all-identical words, ZWJ chains, BiDi overrides, empty-after-strip.
- Key classes: `TestOnlyDiacritics` (5), `TestAlternatingArabicLatin` (3), `TestOnlyTatweel` (4), `TestMaxUnicodeDiversity` (3), `TestAllIdenticalWords` (4), `TestZWJChains` (4), `TestBiDiOverrideChars` (4), `TestEmptyAfterStrip` (5), `TestSingleArabicChar` (3), `TestExtremelyLongWord` (5)

#### `test_fdet_adversarial.py` — 51 tests (653→704)
Adversarial edge cases for all 9 F-DET deterministic field computations (no LLM dependency).
- F-DET-1 (excerpt_id): 5 tests — hyphens, underscores, special chars, large indices, zero index
- F-DET-2 (text_snippet extraction): 5 tests — first word, last word, trailing whitespace, internal spaces, newlines
- F-DET-3 (layer_assignment): 6 tests — empty layers error, 80% boundary, 75% fallthrough, 100 layers, 3-layer LA-4, None-author LA-3
- F-DET-4 (content_types): 6 tests — empty segments, empty indices, non-existent indices, all 16 ScholarlyFunction values, UNCLASSIFIED, dedup order
- F-DET-5 (evidence detection): 8 tests — rawa substring, empty Quran delimiters, single-char content, marker at position 0/end, duplicate markers, ijma at start, clean prose (no false positives), all three types together
- F-DET-6 (page_range): 4 tests — unit starts/ends at exact join_point, 101-page span, unit spans all pages
- F-DET-7 (div_path): 4 tests — empty path, 10-level deep, Arabic-only headings, mixed Arabic/Latin
- F-DET-8 (filter_relevant_footnotes): 8 tests — marker at char_start/char_end boundaries, latent bug (find() first-occurrence), 100 footnotes, substring non-confusion, empty list
- F-DET-9 (quoted_scholars): 5 tests — all layers same as primary (empty), None author included, None author same type excluded, 3-layer 2 distinct, duplicate (type,author) pairs

#### `test_writer_arabic_roundtrip.py` — 35 tests (704→739)
Byte-level Arabic Unicode preservation through full write→JSONL→json.loads cycle.
- Diacritics (8 forms): fathah, dammah, kasrah, sukun, shadda, tanwin fath/damm/kasr
- Stacked diacritics: shadda+kasrah on same letter
- ZWNJ (U+200C): position preservation, not-escaped as \u200c, multiple positions
- Tatweel (U+0640): inside word, not stripped, count preserved
- Superscript alef (U+0670): byte-level, not escaped, not normalized to U+0627
- Presentation forms (U+FDFD ﷽, U+FB50, U+FDFA ﷺ): not normalized to base, not escaped
- Field coverage: text_snippet, context_hint, evidence_refs, description_arabic, div_path, gate_queue
- Combined: single record exercising all 5 corruption vectors simultaneously

### SPEC Issues

| Section | Issue | Recommendation |
|---------|-------|----------------|
| §4 (Phase 1 general) | BiDi override chars (U+202A–U+202E) pass through Phase 1 unchanged — not covered by `_ARABIC_NOISE_RE`. If upstream normalization misses them, they reach Phase 1 unstripped. | Boundary gap, not a bug. SPEC §4 should note BiDi overrides are out-of-scope for Phase 1 and must be handled upstream. No code change needed. |
| §4.3 + `contracts._count_arabic_words` | Diacritics-only tokens (U+064B–U+0652) are counted as Arabic words because diacritics fall within U+0600–U+06FF. Can inflate word_count from OCR artifacts. | Document in KNOWN_LIMITATIONS.md as L-XXX. A stricter counter requires base letter presence — this changes SPEC-defined behavior and needs deliberate decision. |
| §7.1 F-DET-8 | SPEC says "locate footnote by searching assembled_text for pattern ⌜{ref_marker}⌝" but doesn't specify behavior when pattern appears multiple times. Implementation uses `find()` (first occurrence). | Add: "If pattern appears more than once, check ALL occurrences — if ANY falls within unit range, the footnote is relevant." Fix: use `findall()` or iterate occurrences. |
| §7.1 F-DET-1 | `excerpt_id` format uses `_` as both separator and valid character in source_id/div_id — non-reversible by parsing. | SPEC should note this constraint. If ID parsing ever becomes needed, use a different separator or base64-encode components. Safe for equality comparison. |

### Dead Code

None found across all 4 sessions.

### Learnings

**Threshold semantics (boundary-exhaustive):**
- All three predicates are strict: merge uses `< 50` (not `<= 50`), split uses `> 5000` (not `>= 5000`), gap repair uses `<= 5` (not `< 5`). Exactly-at-boundary behaves as non-triggering for merge/split, triggering for gap repair.
- The 5000-word no-split test is the most valuable: guards against `>` being accidentally changed to `>=`, which would split valid 5000-word chunks.

**Arabic Unicode robustness (pathological-arabic):**
- Phase 1 is crash-proof and corruption-proof across all 40 pathological inputs.
- Arabic supplement (U+0750), Extended-A (U+08A0), and Presentation Forms (U+FB50, U+FE70) chars are NOT counted as Arabic words — only basic Arabic block U+0600–U+06FF is checked.
- ZWJ (U+200D) is removed by `strip_arabic_noise` but preserved byte-for-byte in `assembled_text` — correct per `input-sanitization.md`.
- BiDi override chars surviving `strip_arabic_noise` is documented behavior — sanitization belongs at the ingestion boundary.
- `merge_tiny_divisions` with a single zero-word chunk returns the chunk as-is (no sibling to merge with) — no crash.

**F-DET adversarial (fdet-deterministic):**
- F-DET-3 80% boundary: `>= 0.8` exactly applies LA-1 (inclusive). A `> 0.8` would silently fail the boundary case.
- F-DET-5 rawa substring: `رواها` triggers `رواه` match — intentional per DD-S3-8 (plain substring, no word boundaries).
- F-DET-5 empty Quran delimiters: `﴿﴾` don't match because regex uses `+` not `*` — correct (empty brackets are markup artifacts).
- F-DET-9 None-author: `author_canonical_id=None` maps to `'unknown'` — a secondary layer with None author and same type as primary is correctly excluded.
- 0 implementation bugs causing wrong output found; 2 design limitations documented.

**Arabic serialization (probe-json-arabic-roundtrip):**
- Pydantic v2 `model_dump(mode='json')` does NOT apply Unicode normalization — strings pass through as-is.
- `json.dumps(ensure_ascii=False)` preserves all Arabic chars including presentation forms (U+FB50–U+FDFF), superscript alef (U+0670), ZWNJ (U+200C), and tatweel (U+0640) without escaping.
- The full write→disk→read cycle is byte-for-byte safe for all tested Arabic Unicode.
- The writer is correct: no Arabic corruption occurs in the serialization path.

### Metrics

| Metric | Value |
|--------|-------|
| Tests before (session start) | 597 |
| Tests after (session end) | 739 |
| Delta | +142 |
| Tasks completed with findings | 4 / 5 |
| Tasks incomplete (max_turns) | 1 (phase1-error-codes) |
| Bugs found — MEDIUM | 1 |
| Bugs found — LOW | 1 |
| Bugs fixed | 0 |
| SPEC issues | 4 |
| Dead code | 0 |
| Estimated session cost | ~$1.11 USD (phase1-error-codes alone) |
