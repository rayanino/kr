# Passaging Engine Deep Research for Downstream Excerpting

## Repository reality check

The branch `excerpting-foundations-hardening-20260404` contains a **passaging SPEC that describes a full production-grade segmentation engine**, but the actual implementation under `engines/passaging/src/` is **mostly scaffolding**: nearly all core functions raise `NotImplementedError`, and the only runnable logic is a **“tracer bullet”** that outputs **one passage per content unit** (effectively, one per page). fileciteturn60file0L19-L37 fileciteturn39file0L1-L26 fileciteturn44file0L1-L150

Two implications matter for your research questions:

First, **boundary detection quality today is dominated by the tracer**, not the SPEC. The tracer creates a passage per `content_unit` and does not perform the scholarly boundary logic the SPEC requires. fileciteturn44file0L39-L140

Second, the downstream “excerpting consumption model” has an architectural mismatch: the current `engines/excerpting/SPEC.md` v2.0.0 explicitly states that deterministic chunk assembly (what the old passaging engine did) is now **Phase 1 inside excerpting**, absorbing passaging. This makes the passaging engine either (a) transitional scaffolding, or (b) a separate engine that must be reconciled with excerpting’s Phase 1 contracts and invariants. fileciteturn33file0L78-L88

Tests are effectively absent for passaging: `engines/passaging/tests/` contains only `.gitkeep`. fileciteturn32file0L1-L1

## Implementation gap analysis

This section lists **every feature explicitly tagged `[NOT YET IMPLEMENTED]` in `engines/passaging/SPEC.md`**, then evaluates impact on excerpting (based on excerpting’s constraints like chunk containment and self-containment behavior), what degrades/breaks if left unimplemented, and rough complexity.

A key downstream constraint appears in excerpting’s design: **no LLM-extracted unit can span the chunk boundary** (“division/chunk containment”; excerpting calls this D-011), so **any bad boundary becomes structurally unrepairable** during extraction—your only recourse becomes (a) “DEPENDENT/PARTIAL” labeling, (b) context hints, or (c) human gate/merging post-hoc. fileciteturn33file0L106-L114

### Core Phase A features marked not implemented in passaging SPEC

The SPEC states the following are `[NOT YET IMPLEMENTED]`: entire pipeline (§4.A.1–§4.A.10), cross-page assembly (§4.A.2), and all format-specific strategies (§4.A.4–§4.A.9). fileciteturn35file0L1-L1

In code, this correlates to all the core modules raising `NotImplementedError`: `engine.process_source`, `loader.load_and_validate`, `assembly.assemble_division_text`, `strategy.select_strategy`, all `strategies/*`, `validator.validate_passage_stream`, `emitter.emit_passage_stream`, plus argument/discourse/completeness/adaptation stubs. fileciteturn60file0L19-L37 fileciteturn39file0L18-L26 fileciteturn40file0L19-L31 fileciteturn41file0L22-L33 fileciteturn53file0L1-L25 fileciteturn43file0L18-L26 fileciteturn42file0L19-L27

**Cross-page text assembly (§4.A.2)**  
Criticality for excerpting: **critical**. Excerpting Phase 1 (in its absorbed form) explicitly depends on correct cross-page joining; if you stay with the separate passaging engine model, assembly is still the precondition for any meaningful segmentation. fileciteturn33file0L124-L132  
If unimplemented: excerpting sees page-fragmented text; in practice this yields (1) mid-sentence breaks, (2) split evidence chains (Quran/hadith citations), (3) split objection/response pairs—causing “DEPENDENT” units or silent meaning inversion depending on where the LLM cuts. fileciteturn33file0L1695-L1707  
Complexity: **medium/large**, because you must correctly handle separators, footnote marker stability, and text layer rebasing coherently.

**Passage boundary creation strategies (§4.A.4–§4.A.9)**  
Criticality: **critical** for excerpting quality even if excerpting “can” classify within a chunk, because chunk boundaries are hard containment. fileciteturn33file0L106-L114  
If unimplemented: boundaries default to page boundaries (current tracer), guaranteeing pervasive bad splits. fileciteturn44file0L39-L140  
Complexity: **large**, but you can stage implementation: prose first, commentary second, then special formats.

### Transformative capabilities marked not implemented in passaging SPEC

The SPEC marks each of the §4.B capabilities as `[NOT YET IMPLEMENTED]` (and also tags the corresponding optional output fields like `quality_prediction`, `commentary_alignment`, `argument_structure`, and `completeness_forecast`). fileciteturn35file0L1-L1

What follows evaluates each §4.B capability as a distinct “NYI feature” (even though some are also referenced as schema fields).

### §4.B.1 Passage quality prediction

Spec status: `[NOT YET IMPLEMENTED]`. Code file exists but contains only a docstring; no functions. fileciteturn46file0L1-L11

Downstream criticality: **medium**. It does not affect correctness, but it materially affects *operations and gating*: excerpting’s human gate and review flags are designed to prevent silent corruption; quality prediction lets you triage review toward risky chunks, reducing trust collapse. fileciteturn33file0L62-L70

If left unimplemented: excerpting still runs, but (a) you’ll waste LLM budget on low-extractability transitions, (b) you’ll lack early warning for fragmentation risk, increasing downstream “DEPENDENT” rates and gate load. fileciteturn33file0L967-L975

Complexity: **medium** if embedding-based only; **large** if you add feedback loops from excerpting outcomes.

### §4.B.2 Implicit structure discovery

Spec status: `[NOT YET IMPLEMENTED]`. Code file exists but only docstring. fileciteturn47file0L1-L10

Downstream criticality: **high for “minimal-structure” books**, low otherwise. Excerpting Phase 1 relies on the division tree; when structure is minimal, chunk sizes become huge unless you infer boundaries. fileciteturn33file0L124-L132

If unimplemented: you’ll produce oversized chunks or arbitrary splits, increasing (a) overlong LLM inputs (cost + truncation risk), (b) higher probability of splitting explained/explanation pairs (EE-1 violation), and (c) more “DEPENDENT” units. fileciteturn33file0L1695-L1707

Complexity: **large**, because robust topic-shift inference is hard; however, an MVP can be embedding-window change-point detection plus conservative paragraph-only splits.

### §4.B.3 Commentary–matn precision alignment

Spec status: `[NOT YET IMPLEMENTED]`. Code file exists but docstring only. fileciteturn48file0L1-L9

Downstream criticality: **high for multi-layer sources**. Excerpting’s attribution rules depend on correct layer spans, and the engine treats multi-layer attribution errors as among the most dangerous corruption modes. fileciteturn33file0L1826-L1834

If unimplemented: degradations occur in two forms:
- The coarse failure: matn and sharh get separated across passages → excerpting cannot regroup across chunk boundaries → “DEPENDENT” or semantically incoherent units.
- The subtle failure: matn and sharh are in the same chunk but without explicit alignment metadata; downstream comparison of commentaries “explaining the same matn span” becomes unreliable even if units are acceptable. fileciteturn33file0L1826-L1834

Complexity: **medium/large**. Many cases are solvable deterministically with `text_layers` + quotation markers; hashiyah edge cases push it toward large.

### §4.B.4 Cross-edition passage correspondence

Spec status: `[NOT YET IMPLEMENTED]`. Code file exists but docstring only. fileciteturn52file0L1-L10

Downstream criticality: **low for excerpting itself** (excerpting can operate on single sources), but **medium for verification workflows**: edition alignment supports detecting editorial artifacts and can help confirm whether excerpt boundaries are stable across editions.

If unimplemented: excerpting quality is mostly unaffected, but later capabilities (variant comparison, synthesis notes, edition selection) lose leverage.

Complexity: **large**, because it’s a full alignment subsystem (even if the primitive is “character n-gram overlap”).

### §4.B.5 Content census-driven adaptive passaging

Spec status: `[NOT YET IMPLEMENTED]` (in SPEC), and `adapt_config` is `NotImplementedError` in code. fileciteturn51file0L1-L22

Downstream criticality: **medium**. Excerpting can still work with static sizing thresholds, but adaptation can be the difference between “stable extraction” and “constant boundary failures” in dense technical texts.

If unimplemented: you’ll see systematic mis-sizing:
- Dense usul/nahw: chunks too large → multi-topic units → more overgranulation or mis-grouping.
- High-footnote tahqiq: chunk assembly has more “apparatus noise” to manage; without adaptation you may overmerge. fileciteturn33file0L124-L132

Complexity: **medium** (pure deterministic math), assuming normalization produces `content_census`.

### §4.B.6 Scholarly argument boundary detection

Spec status: `[NOT YET IMPLEMENTED]` in SPEC and code functions are `NotImplementedError`. fileciteturn45file0L1-L28

Downstream criticality: **very high**. Excerpting’s self-containment standard explicitly penalizes fragments of arguments and incomplete dialogue (objection without response; ruling without evidence). Argument-aware boundaries prevent the most catastrophic silent corruption: extracting a refuted position as if it were endorsed, or extracting an objection without its answer. fileciteturn33file0L1695-L1707 fileciteturn33file0L1463-L1470

If unimplemented: excerpting will frequently output “DEPENDENT” or, worse, output plausible-looking “FULL” units whose speaker-role context was severed (especially in dialectical texts). This directly violates excerpting’s foundational “knowledge corruption is the worst failure.” fileciteturn33file0L62-L70

Complexity: **large** if you rely on `discourse_flow` which itself may be unimplemented upstream; **medium** for an MVP keyword/state-machine detector that simply blocks splitting at known catastrophic markers.

### §4.B.7 Discourse-aware boundary optimization

Spec status: `[NOT YET IMPLEMENTED]` and code is `NotImplementedError`. fileciteturn49file0L1-L24

Downstream criticality: **high once you have any candidate boundaries**, because it chooses the least destructive boundary among them. It’s an optimization layer, not a base correctness layer.

If unimplemented: you fall back to size/paragraph heuristics, which are acceptable for many prose texts but fail badly in dense argumentation where “best boundary” is *not* the midpoint.

Complexity: **medium** given discourse segments (compute a cost table + slide within window); **large** if discourse segmentation isn’t available.

### §4.B.8 Scholarly completeness forecast

Spec status: `[NOT YET IMPLEMENTED]` and code is `NotImplementedError`. fileciteturn50file0L1-L28

Downstream criticality: **high** because it’s specifically designed to address the containment constraint: when a chunk is predicted to be fragmentary, the passaging layer can merge/adjust boundaries *before* excerpting is forced to decide between truncation and broken units. Excerpting’s spec itself acknowledges the damage of splitting explained/explanation across chunk boundaries and treats it as a known limitation. fileciteturn33file0L1695-L1707

If unimplemented: you’ll discover fragmentation only after excerpting runs—too late to repair without re-passaging or implementing post-hoc merges (which are riskier).

Complexity: **medium** if it’s rule-based on discourse types; **large** if it needs upstream discourse annotation.

## Boundary detection quality

### What boundary logic exists today

The only operational segmentation logic is `engines/passaging/src/tracer.py::process`, which creates **one passage per `content_unit`**. That means the “boundary detector” is effectively:  
> boundary = “every page boundary (every content unit boundary)”.

Evidence:
- It iterates `for i, unit in enumerate(content_units)` and constructs one `passage` per unit, with `unit_range.start == unit_range.end == unit["unit_index"]`. fileciteturn44file0L39-L45 fileciteturn44file0L98-L101  
- No attempt is made to join cross-page text or consult `boundary_continuity`, division tree leaf structure, paragraph breaks, headings, Q&A markers, or masala markers. fileciteturn44file0L39-L45

The tracer does include two weak “pattern-ish” behaviors, but neither affects splitting:
- It sets `heading_text` from `unit["structural_markers"].heading_text` if present, but still emits the passage per page. fileciteturn44file0L79-L80 fileciteturn44file0L96-L97
- It sets `structural_format` to `"commentary_unit"` if any layer in the same page is `layer_type == "sharh"`. fileciteturn44file0L110-L112

### What scholarly boundary patterns it misses

Because boundaries are page-based, it misses essentially all scholarly-natural units the passaging SPEC demands. Representative misses:

- **Mid-sentence and mid-paragraph continuity**: page breaks in Shamela are not scholarly boundaries; excerpting spec’s Phase 1 assembly makes correct boundary mapping a first-class requirement. fileciteturn33file0L124-L132
- **Argument cycle boundaries** (مسألة → دليل → اعتراض → جواب → ترجيح): missing these produces incomplete refutations and the speaker-role inversion failure mode excerpting calls existentially dangerous. fileciteturn33file0L1463-L1470
- **Isnad-to-matn transitions**: hadith chains and their text must not be split arbitrarily; excerpting includes explicit sanad-matn awareness principles. fileciteturn33file0L114-L118
- **Commentary layer shifts** (matn → sharh → hashiyah): the tracer neither groups matn + explanation nor produces alignment metadata. fileciteturn44file0L110-L138
- **Section markers and ordinals** (باب/فصل/تنبيه/فائدة/الأول/الثاني): these are classic boundary anchors in the SPEC, but the code ignores them. (Strategy implementations are empty stubs.) fileciteturn53file0L19-L25

### What causes a “bad split” that corrupts excerpting

Given excerpting’s containment constraint (no cross-chunk units), a “bad split” is not just “annoying”; it creates structural impossibility for correct extraction. fileciteturn33file0L106-L114

High-risk split classes:

A split between **objection and response** (فإن قيل / قلنا; اعترض / أجيب): excerpting treats this as the #1 blind spot and a catastrophic error mode (speaker-role inversion). fileciteturn33file0L1463-L1470

A split between **ruling and its exception/qualification** (إلا / إن لم / لكن / غير أن): excerpting forbids losing qualifiers because it inverts meaning (turning concessions into absolutes). fileciteturn33file0L2045-L2053

A split between **explained object and explanation** (verse/hadith/matn and its sharh): excerpting treats explained+explanation unity as default (EE-1) and explicitly warns that if Phase 1 splits them into different chunks, regrouping becomes impossible; downstream must mark partial/dependent and rely on context hints. fileciteturn33file0L1695-L1707

A split within **evidence chains** (Quran citation brackets ﴿…﴾; hadith citations with grading in footnotes): excerpting’s evidence extraction and self-containment evaluation assume evidence segments cohere with the claim. fileciteturn33file0L2005-L2013 fileciteturn33file0L1695-L1707

## Commentary alignment

### What current code handles

Today’s passaging “commentary handling” is limited to a single heuristic: mark a per-page passage as `"commentary_unit"` if any layer segment on that same page has `layer_type == "sharh"`. fileciteturn44file0L110-L112

It does not:
- group matn + its sharh as a unit,
- detect matn quotation markers like “قوله:”,
- align matn spans to commentary spans,
- handle three-layer texts (matn/sharh/hashiyah),
- preserve matn segments as indivisible units.

All the intended commentary alignment logic exists only as a spec and docstrings. fileciteturn58file0L1-L15 fileciteturn48file0L1-L9

### Commentary structures that would break it

With page-splitting, almost every real multi-layer workflow breaks, but the worst offenders are:

Interleaved matn/sharh where the matn quote begins at the end of a page and commentary continues on the next—your current boundary guarantees separation.

Hashiyah texts with frequent layer switches (very high transition density): the tracer collapses everything to “one page,” while the real unit is “a small matn fragment + multi-layer commentary that may span multiple pages.”

Commentary that quotes long matn blocks: your future “matn never split across passages” rule (SPEC §4.A.9) is completely unimplemented, and excerpting’s EE-1 rule would be violated by forcing splits at pages. fileciteturn33file0L1695-L1707

### Minimum viable commentary alignment for a summer build

The bottleneck-first MVP is not “perfect mapping”; it is **preventing unrepairable chunk splits** and enabling attribution integrity.

A minimum viable alignment that meaningfully improves downstream excerpting quality would include:

Implement **commentary-unit passaging** (SPEC §4.A.9) so that each passage contains:
- one matn span (or small group) plus
- all commentary text up to (but not including) the next matn span.

Implement **alignment records** sufficient for excerpting’s needs:
- `matn_segment: {text, start, end, verse_number?}`
- `commentary_span: {start, end}`
- confidence (even a simple deterministic 0.9 is fine for MVP; make low-confidence explicit).

This matches the `CommentaryAlignmentRecord` schema already defined (though tagged NYI). fileciteturn38file0L148-L177

Algorithmically, the MVP can be deterministic and still high leverage:
- Use `text_layers` transitions as the primary segmentation: each contiguous matn block starts a unit; its following sharh/hashiyah blocks belong to that unit until the next matn. (This aligns naturally with excerpting’s deterministic attribution approach based on layer overlap.) fileciteturn33file0L1826-L1834  
- Use quotation markers (“قوله:”, “قال المصنف:”) only as *secondary confirmation* and to catch mis-layered cases.

If you do only one thing for summer: ensure **matn + its immediate explanation is never separated across passages**, because excerpting cannot fix that later due to containment. fileciteturn33file0L1695-L1707

## Hardening priorities

Below are the **top 10 specific improvements**, ordered by expected impact on downstream excerpting quality. Each item is phrased as an implementable engineering deliverable, not a wish.

First: almost everything important is currently missing; the real “priority ordering” is dominated by *making the engine real* and eliminating the tracer’s page-splitting. fileciteturn44file0L39-L140

1) Replace the tracer bullet as the default path  
Make `engines/passaging/src/engine.py::process_source` the entry point and remove/disable tracer in any production pipeline wiring. Today `process_source` is a stub. fileciteturn60file0L19-L37

2) Implement strict input loading + validation  
Implement `loader.load_and_validate` to enforce ordering, detect gaps, and validate division ranges. This is the earliest point to prevent downstream corruption and to enable deterministic coverage guarantees. fileciteturn39file0L18-L26

3) Implement cross-page assembly with boundary_continuity support  
Implement `assembly.assemble_division_text` including:
- join logic using `boundary_continuity` when present,
- conservative fallback when absent,
- Quran bracket integrity,
- footnote renumbering,
- layer rebasing.  
This is the single biggest correctness driver for excerpting. fileciteturn40file0L1-L31 fileciteturn33file0L124-L132

4) Implement ProseStrategy first, with “never split catastrophic structures” rules  
Implement `strategies/prose.py::create_prose_passages` using:
- leaf-division boundaries as candidates,
- paragraph boundaries as preferred splits,
- explicit blocks for objection/response and ruling/exception markers to avoid splitting,
- hard max fallback. fileciteturn53file0L19-L25  
Tie its correctness assertions to excerpting’s self-containment risks: argument completeness and dialogue completeness. fileciteturn33file0L1695-L1707

5) Implement CommentaryStrategy second, with matn preservation  
Implement `strategies/commentary.py::create_commentary_passages` so matn spans are atomic and stay glued to their commentary. Excerpting’s attribution regime assumes layer correctness is paramount; this must be correct before adding fancy features. fileciteturn58file0L1-L15 fileciteturn33file0L1826-L1834

6) Implement self-validation as a hard gate before emission  
Implement `validator.validate_passage_stream` with fatal vs warning checks to enforce:
- unit coverage,
- non-overlap,
- text integrity,
- layer coverage,
- predecessor/successor consistency,
- author preservation. fileciteturn43file0L1-L26  
This aligns with excerpting’s “fail loud” anti-corruption posture. fileciteturn33file0L62-L70

7) Implement emission to the v2 passage schema and eradicate schema drift  
Implement `emitter.emit_passage_stream` to write **JSONL** records matching `PassageRecord` (`schema_version: passage_v2.0`). The tracer currently emits `"schema_version": "0.1.0"` and a different `passage_id` format, which would break any downstream consumer relying on the spec’d schema. fileciteturn42file0L1-L27 fileciteturn44file0L86-L90

8) Add an MVP argument-boundary protector even without discourse_flow  
Implement `arguments.detect_arguments_keyword` first as a conservative state machine that blocks splits on:
- objection/response markers,
- tarif/definition + explanation patterns,
- tarjih markers requiring preceding alternatives.  
Even a crude protector will significantly reduce DEPENDENT and misattribution risks. fileciteturn45file0L16-L28 fileciteturn33file0L1463-L1470

9) Implement a minimal completeness forecast + corrective merge  
Implement `forecast_completeness` and `apply_corrective_merges` to merge obvious fragments (e.g., “objection ends chunk; response begins next”) when merge stays under hard max. This is directly targeted at the containment limitation excerpting calls out. fileciteturn50file0L15-L28 fileciteturn33file0L1695-L1707

10) Create a deterministic Phase 1 test suite (starting with assembly)  
There are no passaging tests at all. Start with fixtures for:
- cross-page joining,
- Quran bracket spanning pages,
- footnote renumbering stability,
- layer rebasing coverage invariants,
- commentary-unit segmentation. fileciteturn32file0L1-L1  
This is not optional: excerpting’s Phase 1 equivalent is intended to be “fully deterministic and independently unit-testable”; passaging should meet that bar if it remains a separate engine. fileciteturn33file0L124-L132

## Appendix: the single biggest strategic risk

The largest “downstream risk” is not an algorithmic detail—it’s **contract/architecture divergence**:

- Passaging SPEC says downstream engines consume a `passages.jsonl` stream and are constrained by “passage containment rule D-011.”  
- Excerpting SPEC v2 says passaging was absorbed as excerpting Phase 1 and the constraint is “division/chunk containment” (also labeled D-011 but semantically different: chunk boundaries derive directly from division assembly decisions inside excerpting). fileciteturn33file0L78-L88 fileciteturn33file0L106-L114

You likely need an explicit decision for the summer build:

If passaging remains separate, excerpting must (a) accept passaging’s `PassageRecord` schema as its Phase 1 input, and (b) treat passaging boundaries as its D-011 containment boundaries.

If excerpting Phase 1 is the real pipeline, passaging should either be deprecated or re-scoped into a tool that generates **diagnostics / suggested split points** rather than a canonical segmentation artifact.

Until that decision is made, “implementation gaps” in passaging are ambiguous in priority: some features are critical only if passaging is on the hot path, but optional if excerpting Phase 1 owns the deterministic assembly contract.