# Multi-layer Detection in Normalization and Its Downstream Impact on Excerpting

## Scope and evidence base

This report analyzes the branch `excerpting-foundations-hardening-20260404` of the private repository on entity["company","GitHub","code hosting platform"], focusing specifically on how the normalization engine detects interleaved scholarly layers (matn/sharh/hashiyah/taʿlīq/muḥaqqiq apparatus) and how failures propagate into layer-aware excerpting and attribution. fileciteturn14file0L1-L1 fileciteturn18file0L1-L1 fileciteturn13file0L1-L1

Primary artifacts examined:

- Normalization contracts (authoritative runtime schema for `LayerType` + `TextLayerSegment`). fileciteturn20file0L1-L1  
- Shamela normalizer pipeline (Passes 1–6, including Pass 5 dispatch into multi-layer detection). fileciteturn14file0L1-L1  
- Multi-layer detector implementation (`layer_detector.py`) and its event-state segmentation logic. fileciteturn18file0L1-L1  
- Unit tests covering multi-layer detection, including adversarial cases and an Ibn ʿAqīl Shamela fixture. fileciteturn19file0L1-L1 fileciteturn23file0L1-L1 fileciteturn24file0L1-L1  
- Excerpting engine SPEC sections that govern how `text_layers` are consumed in Phase 3 attribution and why attribution errors are treated as high-risk knowledge corruption. fileciteturn13file0L1-L1  
- The repository rule file on Arabic scholarly conventions (used here as the codified “desired behavior” reference for marginal-note/editorial indicators). fileciteturn5file0L1-L1  

Where I make inferences (e.g., “this failure mode causes misattribution downstream”), they are anchored to the excerpting SPEC’s explicit statement that Phase 3 attribution is deterministic over `text_layers` and that misattribution is a top-tier integrity failure. fileciteturn13file0L1-L1

## Current detection capabilities

The normalization boundary’s explicit contract supports five layer labels:

`matn`, `sharh`, `hashiyah`, `tahqiq_note`, and `uncertain` (via `LayerType`). Each `ContentUnit.primary_text` must be fully covered by an ordered list of `TextLayerSegment` spans, each carrying `layer_type`, an optional `author_canonical_id`, `[start,end)` offsets, and a confidence score. fileciteturn20file0L1-L1

### What the current normalization implementation actually detects (today)

In the Shamela normalizer, multi-layer detection is implemented as Pass 5 of a 6-pass pipeline, with orchestration in `ShamelaNormalizer._pass5_detect_layers()` and the per-page detector in `engines/normalization/src/layer_detector.py`. fileciteturn14file0L1-L1 fileciteturn18file0L1-L1

The effective, implemented signal set for layer segmentation is:

- **Bold spans (`<b>…</b>`) as a matn proxy**, but only when bold behaves “like a layer indicator,” not like emphasis. The detector maps bold HTML spans into `primary_text` offsets, then applies a two-level filtering rule: page-level bold coverage must be between 5% and 60%, and individual bold spans must be ≥50 characters and must *not* contain a transition marker string. Passing bold spans are treated as bounded `MATN` regions (confidence 0.75), otherwise bold is ignored and the page is treated as “emphasis-only.” fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

- **Standalone Arabic transition markers** detected by regex against `primary_text`, presently limited to four core patterns:
  - “قال المصنف:” → transition to `MATN`
  - “قال الشارح:” → transition to `SHARH`
  - “قوله:” → transition to `MATN`
  - “أي:” → transition to the *default commentary layer* (resolved at runtime)  
  The regex allows an optional conjunction prefix “و” or “ف” directly attached (e.g., “وقال المصنف:”, “فقوله:”). Colons are required for matching, and boundaries are constrained to start-of-text or whitespace before the marker. fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

- **Square-bracket regions** `[ ... ]` as matn-like quote regions, but only when bracket content length is ≥15 characters (short brackets are assumed to be references like “[التحريم: 5]”). These are treated as bounded `MATN` regions (confidence 0.65). fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

- **A deterministic event-driven state machine** merges these signals into a single per-page segmentation. It creates an event stream of:
  - bold_enter / bold_exit
  - bracket_enter / bracket_exit
  - marker (open-ended transition)
  
  Critically, it keeps a `marker_state` (the last open-ended marker layer) so that when an “enter/exit” bounded region ends, the segmentation returns to the last marker-implied layer rather than a hardcoded default. This is a purposeful fix for “marker persistence across bounded regions.” fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

- **A conservative fallback rule**: any `MATN` segments with confidence <0.50 are reclassified to the default commentary layer. This encodes an explicit asymmetry: “wrongly attributing matn to commentary is less harmful than wrongly attributing commentary to matn.” fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

### Supported layer types vs. emitted layer types

Although the schema supports `tahqiq_note`, the current layer detector’s event generator only emits `MATN` regions (from bold/brackets/markers), commentary regions (the selected default commentary layer, i.e., `SHARH` or `HASHIYAH`), and `UNCERTAIN` gap-fill when needed. There is no implemented signal that directly emits `TAHQIQ_NOTE` segments in `primary_text` today. fileciteturn20file0L1-L1 fileciteturn18file0L1-L1

### Multi-layer enablement logic (including override)

Pass 5 can run in a forced multi-layer mode even when metadata says “single-layer”:

- If `SourceMetadata.is_multi_layer` is false, a **10-page pre-scan** checks for multi-layer signals: bold-coverage proxy (>10% based on raw bold span lengths) and presence of any transition marker regex matches. If ≥3 of the scanned pages show signals, the normalizer overrides metadata and enables multi-layer segmentation. fileciteturn14file0L1-L1 fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

This is important: the catastrophic “entire multi-layer book treated as single-layer MATN with confidence 1.0” outcome is *mitigated only when at least one of those two signal classes is present early in the book*. fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

### Demonstrated test coverage and what it implies about the intended design

The layer detector is unusually well-tested for a rule-based subsystem: `test_layer_detection.py` enumerates 19 categories spanning bold thresholds, marker-prefix edge cases, bracket-length exclusion, coverage-gap filling, metadata override, default commentary selection, confidence-based conservative fallback, and marker_state persistence. fileciteturn19file0L1-L1

A key concrete fixture is the Ibn ʿAqīl Shamela excerpt (`engines/normalization/tests/fixtures/shamela_ibn_aqil.htm`), which includes:

- a metadata page without page number (expected to be skipped),
- bold matn lines (Alfiyya verse),
- “أي:” commentary,
- footnote separators `<hr width='95'>` with numbered footnote bodies,
- a Qurʾān citation, and
- a ZWNJ heading signal. fileciteturn24file0L1-L1

Those fixture features directly correspond to the implemented signals (bold regions + transition markers + page-level plumbing), so at least one “realish” multi-layer layout is exercised end-to-end through Passes 1–5. fileciteturn14file0L1-L1 fileciteturn19file0L1-L1 fileciteturn24file0L1-L1

## Failure modes: multi-layer patterns the current system will miss or misclassify

Below are five concrete scholarly-text structures that are realistic in Islamic publishing practice but are outside (or actively conflicting with) the current detector’s signal set. For each, I specify why it fails given the present implementation, then the downstream excerpting consequences.

### Diacritized / punctuation-variant layer markers

**Structure (realistic):** layer transitions written with full tashkīl or different punctuation, e.g. “قال المُصَنِّفُ رحمه الله” or “قولهُ” or “قال المصنف ـ” or Arabic punctuation variants instead of the ASCII colon.  

**Why it fails:** transition markers are matched with literal regex strings requiring a colon and lacking diacritic-insensitive matching. The detector also preserves diacritics end-to-end rather than normalizing them away, so diacritics remain in `primary_text` and can break literal substring matches. fileciteturn18file0L1-L1 fileciteturn14file0L1-L1

**Excerpting consequence:** excerpting Phase 3 attribution is deterministic overlap over `text_layers` (LA-1/LA-2/LA-3/LA-4). If transitions are missed, quotations (matn lines, sharh citations, etc.) remain inside the default commentary layer (or vice versa), producing hard misattribution: the same excerpt text will be assigned to the wrong author layer with high apparent confidence. This is precisely the “silent corruption” class excerpting treats as existential risk. fileciteturn13file0L1-L1

### Hashiyah quoting “قوله:” against sharh text (chain matn→sharh→hashiyah)

**Structure (realistic):** in a 3-layer corpus, the hashiyah often quotes **the sharh** (not the matn) with “قوله:” and immediately glosses it. This is a defining property of hashiyah as supercommentary.

**Why it fails:** the current detector hardcodes “قوله:” as a `MATN` transition, regardless of whether the surrounding context is sharh or hashiyah. That is internally consistent for sharh-on-matn, but wrong for hashiyah-on-sharh. fileciteturn18file0L1-L1

**Excerpting consequence:** even if excerpting correctly groups a teaching unit conceptually, Phase 3 attribution will (a) potentially mark quoted sharh text as matn, (b) skew the layer-coverage percentages used by LA-1/LA-3, and (c) mis-populate `quoted_scholars` derived from layer overlap. In a multi-layer work, that can invert “who is teaching” versus “who is being quoted,” which excerpting explicitly frames as the highest-risk error mode. fileciteturn13file0L1-L1

### Font-size-only layer encoding (no bold, no explicit markers)

**Structure (realistic):** printed editions frequently differentiate layers by font size rather than bold; in Shamela HTML exports, this often appears as `<font size=...>` rather than `<b>`.  

**Why it fails:** the Shamela Pass 1 parser captures `font_size_spans` explicitly “for Pass 5 layer detection,” but the actual Pass 5 `layer_detector.py` does not consume font-size spans at all. Pre-scan also only looks at bold coverage and marker regex hits, so a font-size-only multi-layer work can slip into the “single-layer fast path.” fileciteturn14file0L1-L1 fileciteturn18file0L1-L1

**Excerpting consequence:** worst case, the entire book is tagged as a single `MATN` segment with confidence 1.0 (single-layer fast path), causing systematic author misattribution downstream. This is not a “small recall miss”; it is a book-scale trust collapse vector given excerpting’s emphasis on attribution correctness. fileciteturn18file0L1-L1 fileciteturn13file0L1-L1

### Inline editorial / muḥaqqiq apparatus in primary text (not footnotes)

**Structure (realistic):** muḥaqqiq notes or editorial insertions appear inline, marked by phrases like “قال المحقق…”, “في الأصل…”, “في نسخة…”, “كذا في المطبوع…”, “هامش…”, or “حاشية…”, sometimes in brackets/parentheses, sometimes as standalone lines.

**Why it fails:** (1) the layer detector’s marker set does not include editor/muhaqqiq markers, and (2) there is no code path that emits `TAHQIQ_NOTE` segments in `primary_text` even though the schema supports it. The repo’s scholarly conventions file exists precisely to codify such indicators, but the normalization detector does not appear aligned to it yet. fileciteturn20file0L1-L1 fileciteturn18file0L1-L1 fileciteturn5file0L1-L1

**Excerpting consequence:** these notes will be attributed to a commentary author layer (sharh/hashiyah) rather than a tahqiq/editorial layer. That can pollute topic keywords and downstream placement—an editor note can introduce side topics not present in the author’s argument. This directly increases the risk described by excerpting’s “leaf pollution prevention” rule (LP-1) by turning apparatus chatter into apparent “mentions” of topics. fileciteturn13file0L1-L1

### Non-square-bracket quoting conventions

**Structure (realistic):** matn is often delimited by:
- Arabic guillemets «…»,
- parentheses ( … ),
- Qurʾānic brackets ﴿…﴾ (when the matn is the verse),
- or typographic ornaments (lines, special glyphs).  

**Why it fails:** bracket-region detection only looks for literal square brackets `[...]` and uses a length heuristic. No other quoting delimiters are recognized as layer signals. fileciteturn18file0L1-L1 fileciteturn19file0L1-L1

**Excerpting consequence:** the matn/sharh interleave becomes invisible to deterministic layer attribution, increasing LA-2/LA-3 ambiguity and (worse) producing confident but wrong LA-1 dominance outcomes if other signals bias the segmentation. Downstream, excerpting treats wrong author attribution as a “knowledge corruption is the worst failure” class. fileciteturn13file0L1-L1

## Detection approach comparison under the D-041 multi-model consensus constraint

The current normalization implementation is already a pure rule-based detector with a state machine (essentially option (a) in your comparison). fileciteturn18file0L1-L1

Given your constraint that **any** LLM call requires D-041-style multi-model consensus (i.e., the “unit cost” of an LLM decision is multiplied), the comparative trade space looks like this:

### Rule-based pattern matching plus state machine

This is the current approach: deterministic signals (bold/markers/brackets) fed into an event-driven segment builder with explicit confidence rules and conservative fallbacks. Its strengths are:

- cheap enough to run on every page,
- fully unit-testable with adversarial cases (already present),
- stable outputs (no model drift), and
- easy to integrate into cross-engine contracts (`TextLayerSegment` coverage invariants). fileciteturn18file0L1-L1 fileciteturn19file0L1-L1 fileciteturn20file0L1-L1

Its structural weakness is brittleness: it can only detect what it was told to detect, and it currently ignores several fields it already captures (notably font size spans). fileciteturn14file0L1-L1 fileciteturn18file0L1-L1

### LLM-based classification of layers in text chunks

An LLM could, in principle, learn a much richer marker set and infer layer transitions from discourse cues (e.g., “تعليق:”, “قال المحقق”, “قلت”, “وفي الحاشية”, etc.), even when typography is missing.

But applying this at normalization scale is expensive: normalization is per-page (or per segment) for entire books. Under D-041, “just run an LLM classifier” becomes operationally heavy and adds failure modes that are not easily unit-tested (model drift, provider differences, consensus conflicts). This clashes with excerpting’s own emphasis on deterministic provenance and “fail loud” constraints—especially because layer errors are upstream and can poison everything downstream. fileciteturn13file0L1-L1

### Hybrid: deterministic first pass + LLM only for ambiguous residue

This aligns best with the realities of the codebase and the D-041 constraint:

- The current detector already emits confidences and has an `UNCERTAIN` layer type available in the schema. fileciteturn18file0L1-L1 fileciteturn20file0L1-L1  
- The excerpting engine already treats certain decisions as consensus-worthy and separates deterministic fields from LLM-enriched ones. The same architectural separation can be copied into normalization: deterministic segmentation + “LLM rescue” only when uncertainty is both high-impact and rare. fileciteturn13file0L1-L1  

In practice, the hybrid strategy is:

1) Keep the existing state machine as the baseline for high-precision markers and typography. fileciteturn18file0L1-L1  
2) Define *explicit ambiguity triggers* (e.g., high `UNCERTAIN` share, contradictory signals, 3-layer nesting patterns, editor-marker presence).  
3) Only then invoke the D-041 consensus LLM call to label ambiguous spans or propose additional boundaries.

This minimizes cost while expanding recall exactly where the current signal set is weakest.

## Hashiyah-specific challenges: what distinguishes hashiyah from sharh

The structural distinction you care about—hashiyah commenting on sharh (not directly on matn)—creates a detection problem that is partly **structural** and partly **fundamentally ambiguous without context**.

### Why it is structurally hard

The current detector is effectively built for a 2-layer worldview: “quotations are matn, everything else is commentary.” This is encoded in:

- bold/bracket regions → `MATN`,
- “قوله:” → `MATN`,
- default commentary → one layer (`SHARH` or `HASHIYAH`), chosen globally. fileciteturn18file0L1-L1

That works on Ibn ʿAqīl-style sharh-of-matn, which the fixture demonstrates: bold verse lines as matn and subsequent explanation as sharh. fileciteturn24file0L1-L1

But hashiyah introduces **nested quoting**:

- Hashiyah (outer) quotes Sharh (middle) quotes Matn (inner).  
- The same surface marker “قوله:” can refer to either the matn (if you’re in sharh) or the sharh (if you’re in hashiyah).  

A single-layer-state machine with one `marker_state` cannot represent this nesting; it needs a *stack* (or at minimum context-sensitive interpretation of “قوله” based on the currently active layer). fileciteturn18file0L1-L1

### Are there reliable markers?

Some markers can help but are not universally reliable:

- Strong: “قال الشارح:” can mark entry into sharh text inside a hashiyah (the detector already supports this). fileciteturn18file0L1-L1  
- Weak/ambiguous: “قوله:” is ambiguous across the sharh/hashiyah boundary (and currently hardcoded to matn). fileciteturn18file0L1-L1  
- Typography can help (e.g., different font size for hashiyah versus sharh), but the current implementation does not consume font-size spans. fileciteturn14file0L1-L1 fileciteturn18file0L1-L1  

So: **hashiyah is not fundamentally impossible**, but it does require either (a) nested-state modeling plus more typographic signals, or (b) broader context (cross-line or cross-page) plus additional marker vocabulary—otherwise ambiguity is intrinsic.

From the excerpting side, even with perfect boundary detection, hashiyah attribution has higher epistemic impact because it changes “whose teaching voice” is being recorded; excerpting explicitly treats attribution correctness as top-priority. fileciteturn13file0L1-L1

## Hardening recommendations: the highest-impact changes for excerpting quality

These are ordered by expected impact on downstream excerpt attribution quality and on reducing silent corruption risk, while staying grounded in the current implementation structure.

### Extend marker matching to be diacritic- and punctuation-robust, and align marker vocabulary to scholarly conventions

**Why highest impact:** transition markers are one of only three signal classes; they are currently brittle (colon required, diacritic-sensitive). Fixing this increases recall substantially without changing architecture. fileciteturn18file0L1-L1

**Concrete code changes:**
- In `TRANSITION_MARKER_PATTERNS`, either:
  - make regex tolerate Arabic diacritics between letters, and tolerate common punctuation alternatives to “:”, or
  - precompute a diacritic-stripped shadow string for marker detection only (while preserving the original text for storage, consistent with the system’s immutability principle). fileciteturn18file0L1-L1 fileciteturn14file0L1-L1
- Expand marker patterns to include editor/marginal-note indicators from the conventions file as candidates for `TAHQIQ_NOTE` (or at least for triggering `UNCERTAIN` + a warn flag). fileciteturn5file0L1-L1 fileciteturn20file0L1-L1

**Tests to add:** augment `test_layer_detection.py` with diacritized marker variants and punctuation variants, parallel to existing tests that assert “no colon → not matched.” fileciteturn19file0L1-L1

### Consume font-size spans as first-class layer signals

**Why high impact:** the code already extracts `font_size_spans` “for Pass 5,” suggesting the spec/intent expects this, but the detector ignores them. This is the single biggest “available but unused” capability. fileciteturn14file0L1-L1

**Concrete code changes:**
- Add a `_map_fontsize_to_primary()` analogous to `_map_bold_to_primary()`.
- Add a font-size classifier similar to `_classify_bold_signal()` (page-level distribution + per-span heuristics), then emit bounded-region events in `_build_segments()` (e.g., `font_enter/font_exit` with confident layer assignments). fileciteturn18file0L1-L1

**Test/fixture strategy:** create a new fixture page where matn is `<font size='3'>` and commentary is `<font size='2'>` without bold, and ensure pre-scan sees it (you’ll likely need to extend `pre_scan_multi_layer` too). fileciteturn18file0L1-L1

### Implement nested-layer modeling for hashiyah via a stack, not a single marker_state

**Why high impact:** without nested modeling, “قوله:” in hashiyah contexts will remain structurally ambiguous and frequently wrong. This directly targets the “hardest layer to detect” problem you flagged. fileciteturn18file0L1-L1

**Concrete code changes:**
- Replace `marker_state = (layer, confidence)` with a small stack representing the active commentary context (e.g., `[HASHIYAH, SHARH, MATN]` levels), where:
  - markers can push or switch context,
  - bounded quote regions (bold/brackets/font) can push to “quoted” layer,
  - exiting a bounded region pops back to the previous context.  

This generalizes the current “restore to marker_state on exit” into a higher-fidelity nesting model. fileciteturn18file0L1-L1

**Test requirement:** add targeted unit tests for a 3-layer scenario: default commentary = `HASHIYAH`, encountering “قال الشارح:” enters sharh, encountering “قوله:” inside sharh enters matn, then exiting restores correctly. The repo already has the scaffolding to test marker persistence; extend it to stack depth >1. fileciteturn19file0L1-L1

### Activate `TAHQIQ_NOTE` as an emitted layer for inline apparatus, not just a schema option

**Why high impact:** the schema includes `TAHQIQ_NOTE`, and excerpting explicitly distinguishes editorial notes as a separate scholarly function (`editorial_note`) and treats apparatus as integrity-sensitive. If tahqiq notes are misattributed as author commentary, you get both attribution corruption and topic/leaf pollution. fileciteturn20file0L1-L1 fileciteturn13file0L1-L1

**Concrete code changes:**
- Add marker patterns for editor phrases (from conventions) that transition to `TAHQIQ_NOTE` (open-ended) and/or bound editor notes (e.g., bracketed “زيادة من المحقق”). fileciteturn5file0L1-L1 fileciteturn18file0L1-L1  
- Ensure `_build_layer_map()` includes `TAHQIQ_NOTE` and maps author identity when present in `metadata.text_layers`. fileciteturn18file0L1-L1 fileciteturn20file0L1-L1

**Fixture-driven coverage:** extend the Ibn ʿAqīl fixture (or add a second fixture) with a short inline muhaqqiq note to validate detection, not only footnote classification. fileciteturn24file0L1-L1

### Add “attribution risk gates” based on layer statistics and ambiguity signals

**Why high impact:** even with better detection, some cases will remain ambiguous. The system needs fail-loud behavior because excerpting treats silent misattribution as existential. fileciteturn13file0L1-L1

**Concrete code changes (normalization-side):**
- Extend Pass 5 / Pass 6 reporting beyond the existing “matn ratio > 40%” warning to include:
  - percent `UNCERTAIN`,
  - transition density,
  - “marker contradiction” counts (e.g., frequent toggles without bounded quote signals). fileciteturn14file0L1-L1 fileciteturn18file0L1-L1

**Concrete integration (excerpting-side):**
- Treat high normalization layer uncertainty as a first-class reason to trigger LA-3-style consensus/human gate more often, because excerpting attribution is deterministic and inherits upstream errors. This is aligned with excerpting’s consensus/gate philosophy for high-epistemic-impact decisions. fileciteturn13file0L1-L1

This recommendation aligns with excerpting’s “packaging vs ontology” principle: when layer boundaries are uncertain, you must not silently treat packaging convenience (a merged span) as an ontological claim about whose voice is speaking. Strong uncertainty signals are how you prevent that slide. fileciteturn13file0L1-L1