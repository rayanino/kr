# KR Library — Can the Synthesis Engine Solve the Granularity Problem?

## Context and the owner’s “granularity” demand

The owner’s feedback makes the core need unambiguous: they want to open a topic like **مشروعية الطلاق** and compare scholars *by evidence type*—especially “Evidence from Quran” (and ideally “per ayah”), side-by-side across sources, without wading through excerpts that mix everything together. fileciteturn11file0L1-L1

In the second review comment, the owner argues that keeping “ruling + all proofs + specific Quran proofs + Sunnah proofs …” in one excerpt scales badly: a leaf would accumulate thousands of mixed excerpts, undermining the point of excerpting. They propose an explicit breakdown: (a) leaf for “الحكم إجمالا” (general ruling statements), and (b) leaves for “الاستدلال” subdivided into “من الكتاب” and even “آية” (one excerpt per verse). fileciteturn11file0L1-L1

At the same time, they highlight a second constraint that matters as much as granularity: **context preservation**. They do not want a “puzzle” workflow where an evidence excerpt is detached from the ruling it supports. They explicitly warn that users might accidentally interpret an evidence excerpt using the wrong contextual/ruling excerpt (“CORRUPTION in my knowledge”). fileciteturn11file0L1-L1

That tension—*fine comparison granularity* vs *anti-decontextualization / self-containment*—is the architectural bottleneck.

## What the docs actually commit to: excerpts as self-contained teaching units, not taxonomy-shaped atoms

### Self-containment and decontextualization prevention are excerpting’s primary constraints

The excerpting engine spec defines a teaching unit/excerpt as the smallest self-contained scholarly thought; it explicitly lists “a ruling with its evidence” as a canonical teaching unit form. fileciteturn20file0L1-L1

Its self-containment criteria are formalized (C‑SC‑1 through C‑SC‑5). Two are directly relevant:

- **C‑SC‑4 (Argument Completeness):** evidence without stating what it is evidence for cannot be `FULL`. fileciteturn20file0L1-L1  
- **C‑SC‑3 (Evidence Completeness):** evidence citations must carry enough identifying information to stand alone, or be flagged as missing context. fileciteturn20file0L1-L1

Then §6.1 (Decontextualization Prevention) turns this into hard grouping constraints. Most importantly for this question:

- **DP‑4 (Evidence + Ruling):** “Evidence cited for a ruling MUST stay with the ruling.” fileciteturn20file0L1-L1

So, per the excerpting engine’s own integrity model, splitting “ruling” away from “Quran evidence” is not a harmless refactor; it is *a direct collision with the anti-decontextualization invariant* unless some other mechanism preserves “what this evidence is for” within the evidence-level unit. fileciteturn20file0L1-L1

### Taxonomy-agnostic excerpting is an explicit boundary in the architecture

The excerpting spec also draws a hard responsibility boundary: excerpting produces content-derived metadata (topic keywords); the taxonomy engine owns structure and placement. It explicitly removed the older idea of excerpting proposing a taxonomy path, to keep excerpting unbiased with respect to taxonomy evolution. fileciteturn20file0L1-L1

This matches the tension you called out from VISION §5.2 (“excerpts should NOT be split by taxonomy needs”): the guiding intent is that taxonomy should not dictate excerpt boundaries; excerpt boundaries are governed by pedagogical coherence + integrity constraints (self-containment / decontextualization prevention). fileciteturn7file0L1-L1

**Implication:** the owner’s proposed “taxonomy leaves by evidence type → per ayah excerpts” is architecturally *suspect* if interpreted literally as “change excerpt boundaries so that the taxonomy can have these leaves.” It is much more compatible with the architecture if interpreted as “create the *comparison view* the owner wants, using metadata and synthesis, without reshaping the primary excerpt units.” fileciteturn20file0L1-L1

## What synthesis is designed to do (and what it already expects from excerpts)

Your hypothesis is not only plausible; it aligns strongly with the synthesis engine spec’s declared input contract and content model.

### The synthesis engine is explicitly an “entry from placed excerpts at a leaf” generator

The synthesis spec defines the engine’s core job as generating encyclopedic entries from placed excerpts at taxonomy leaves, with a factual layer (excerpt-traceable) and an analytical layer. fileciteturn19file0L1-L1

Crucially, it explicitly names what it expects from placed excerpts, and it lists **`content_types` and `evidence_refs` as expected fields**; if they are missing, synthesis proceeds “with degraded synthesis,” and it states directly that without `evidence_refs` “the entry cannot describe the evidence base.” fileciteturn19file0L1-L1

This is extremely load-bearing: it indicates that “synthesis organizes evidence” is part of the intended architecture, not an afterthought.

### The synthesis output model already has “evidence” hooks per position

The synthesis spec’s entry content structure includes a `scholarly_positions` array where each position carries:

- `evidence_types`  
- `evidence_refs` fileciteturn19file0L1-L1

Even if the prose sections don’t yet prescribe an “Evidence from Quran” heading, the structured representation is already designed to capture and expose evidence at the level where comparison matters: **per scholarly position**. fileciteturn19file0L1-L1

It also includes a per-science “evidence hierarchy” customization hook (explicitly listing fiqh’s ordering: `quran, hadith, ijma, qiyas...`). That’s essentially the schema-level permission slip for your intended organization. fileciteturn19file0L1-L1

### ENTRY_EXAMPLE doesn’t show “evidence-type sections,” but it does validate deep re-organization at entry level

`reference/ENTRY_EXAMPLE.md` is a calibration example (for nahw), not fiqh evidence. It does not demonstrate Quran/Sunnah sections specifically. fileciteturn15file0L1-L1

But it *does* demonstrate the key pattern you need: entries are expected to be deeply structured and to go far beyond “flat” excerpt concatenation, and it explicitly argues that rich metadata is what enables the synthesizer to produce narrative structure, not just summaries. fileciteturn15file0L1-L1

So while ENTRY_EXAMPLE doesn’t prove “Evidence from Quran” is already implemented, it supports the general principle: **entry organization is where you should do transformative structuring**. fileciteturn15file0L1-L1

## Can synthesis meet the owner’s side-by-side Quran-evidence comparison goal without pre-splitting excerpts?

### Architectural soundness relative to VISION and the excerpting/synthesis specs

Under the architecture described above, the cleanest interpretation is:

- Excerpting produces **self-contained teaching units**, often including “ruling + evidence bundle,” because DP‑4 and C‑SC‑4 strongly push toward keeping “what this evidence is for” co-located. fileciteturn20file0L1-L1  
- Taxonomy places those excerpts by topic. fileciteturn20file0L1-L1  
- Synthesis produces entries that can **restructure** the material to serve study needs—while staying excerpt-grounded and citation-traceable. fileciteturn19file0L1-L1

Given that, the hypothesis is architecturally sound: **synthesis is the right layer to provide evidence-type comparative views, because excerpting is constrained to preserve self-contained thought units and avoid decontextualization.** fileciteturn20file0L1-L1

This also directly addresses the owner’s *context puzzle* concern: if you do not split evidence away from rulings in the primary stored excerpts, you preserve the “what is this evidence supporting?” relationship by construction, and synthesis can then present “Evidence from Quran” in a way that still references the associated ruling/position. fileciteturn11file0L1-L1

### What makes it work in practice: invert from “per excerpt bundle” to “per evidence-type map”

To satisfy the owner’s comparison workflow, synthesis needs to produce an *inverted index* inside the entry:

- Instead of: excerpt → (ruling + quran + sunnah + ijma …)  
- Produce: entry → “Evidence from Quran” → verse → list of scholars/positions citing it (with citations back to their excerpts)

That is exactly the kind of transformation synthesis is designed for, and it can remain fully traceable if every aggregated “verse cited” statement points to the excerpt(s) that contained the citation. fileciteturn19file0L1-L1

### Where parsing should happen: “internal parsing” is acceptable, but metadata-first is materially safer

Your hypothesis step (2)—synthesis “internally parsing the evidence types from each excerpt”—is plausible because synthesis is LLM-driven.

However, there is a better way that is already consistent with both specs:

- Excerpting already classifies evidence segments (`evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, etc.) and aggregates them into `content_types`. fileciteturn20file0L1-L1  
- Excerpting also extracts structured `evidence_refs` (at least for Quran/hadith/ijma), with validation hooks (e.g., surah/ayah bounds checking). fileciteturn20file0L1-L1  
- Synthesis explicitly expects to consume `content_types` / `evidence_refs`. fileciteturn19file0L1-L1

So, architecturally, **synthesis should not rely primarily on ad-hoc text parsing**, except as a fallback when metadata is incomplete. It should use excerpt-produced evidence metadata as its primary evidence signal. This reduces hallucination risk and improves deterministic debuggability. fileciteturn19file0L1-L1

## What metadata excerpts must carry for synthesis to do evidence-type aggregation correctly

This question is where the design tightens: “Evidence from Quran” aggregation is only as good as the evidence identifiers and the mapping of evidence → position.

### Baseline required fields already named by the synthesis spec

The synthesis spec’s input contract is explicit that these fields materially affect synthesis quality:

- `content_types` (expected; needed for tagging excerpt role) fileciteturn19file0L1-L1  
- `evidence_refs` (expected; needed to describe evidence base) fileciteturn19file0L1-L1  
- plus attribution/school fields so synthesis can produce per-school or cross-school comparisons correctly. fileciteturn19file0L1-L1

From the excerpting spec side, these are already in the `ExcerptRecord` output contract:

- `content_types` is deterministic aggregation of segment functions (so Quran evidence segments become a machine-readable tag). fileciteturn20file0L1-L1  
- `evidence_refs` exists and is extracted deterministically via pattern matching + canonical lookup (with partial/unresolved states allowed). fileciteturn20file0L1-L1  
- `takhrij_data` exists for hadith details (collections, numbers, grade statements), which can support hadith-evidence grouping. fileciteturn20file0L1-L1

So “what metadata is needed?” is largely answered by the current contracts: the architecture already anticipates evidence-aware synthesis.

### The missing piece for the owner’s “per ayah” comparison: stable, canonical verse IDs at high recall

The owner’s “per ayah” aspiration is fragile if `evidence_refs` frequently comes through as `{surah: null, ayah_start: null}` (partial quotes, paraphrases, “opening words only” references). fileciteturn20file0L1-L1

The excerpting spec explicitly allows unresolved Quran references in `evidence_refs` (and notes that LLM-assisted resolution is deferred). fileciteturn20file0L1-L1

If you want synthesis to reliably produce “Evidence from Quran → Verse X → all scholars who cited it,” you need **high-recall canonicalization** of Quran citations into stable keys (e.g., `quran:2:229-230`). Without that, synthesis will end up clustering by fuzzy verse text snippets, which will be inconsistent across scholars and sources.

A practical metadata requirement, therefore, is:

- **`evidence_refs` should include a canonical evidence key** whenever possible:
  - Quran: `(surah, ayah_start, ayah_end)` (already in schema) fileciteturn20file0L1-L1  
  - Hadith: canonical collection + number where available (currently in `takhrij_data`, not `evidence_refs`) fileciteturn20file0L1-L1  
  - Ijma: a structured “scope” and claim type (already hinted via `scope`) fileciteturn20file0L1-L1  
  - Qiyas: the excerpting spec classifies `evidence_qiyas` as a scholarly function, but `evidence_refs` enumerates only `quran/hadith/ijma` in the described structure—so synthesis will likely need either (a) an expanded `evidence_refs.type` enum to include `qiyas`, or (b) treat qiyas as “non-canonical evidence” referenced via `content_types` + position text. fileciteturn20file0L1-L1

### The second missing piece: mapping evidence items to the position they support

Even with perfect verse IDs, the owner’s “no puzzle” constraint means the UI/entry must clarify: **this verse is being used to support which ruling/position**.

Synthesis already produces a `scholarly_positions` array and associates each position with supporting excerpts, plus evidence types/refs. fileciteturn19file0L1-L1

To enable the strongest “side-by-side evidence comparison” view, the synthesis engine should produce (in structured form, even if not shown verbatim):

- `position_id → evidence_ref_ids[] → supporting_excerpt_ids[]`

This can be done entirely within synthesis Phase 2/Phase 3, because Phase 2 already identifies positions and tracks supporting excerpts. fileciteturn19file0L1-L1

If you find this mapping too fuzzy to infer purely in synthesis, the excerpting spec already anticipates a deferred capability for “Evidence chain reconstruction” (DC‑05), which is exactly the kind of upstream signal that could anchor evidence-to-claim mapping more deterministically. fileciteturn20file0L1-L1

## Risks and tradeoffs: smarter synthesis vs finer excerpt granularity

### Risks of pushing evidence granularity into synthesis

The main risks are real, but they are mostly *metadata quality risks*, not architectural ones:

1. **Evidence canonicalization gaps become synthesis failures.** If `evidence_refs` is often unresolved for Quran citations, synthesis can’t reliably aggregate “per ayah,” and you regress to fuzzy clustering. fileciteturn20file0L1-L1

2. **LLM mis-association risk (evidence → wrong position).** If a single excerpt includes multiple positions or multiple sub-arguments, synthesis must correctly attribute which evidence supports which position. The synthesis spec mitigates hallucination with attribution-first generation + entailment verification, but that framework still needs high-quality attribution targets. fileciteturn19file0L1-L1

3. **Complexity concentration.** Synthesis becomes “the place where everything hard happens”: position detection, khilaf analysis, evidence aggregation, integrity checks. This can slow iteration and create a large surface area for subtle bugs. The spec acknowledges that the entire engine is unimplemented (“0 lines of engine logic”), so this is also a schedule/engineering risk. fileciteturn19file0L1-L1

4. **UI expectations vs entry schema.** The current synthesis entry schema example emphasizes `core_treatment` and `scholarly_positions`. To meet the owner’s “open a leaf and instantly compare Quran evidence,” you likely need either:
   - a richer structured sub-object (e.g., an “evidence map” section), or  
   - a scholar-interface feature that renders a comparison view from `scholarly_positions[].evidence_refs`.  
   Either way, you must ensure the data needed is emitted structurally, not only as prose. fileciteturn19file0L1-L1

### Risks of changing excerpt granularity to “per evidence type / per ayah” at excerpting time

This path appears to satisfy the owner’s “leaf browsing” mental model directly, but it collides with integrity constraints and creates second-order problems:

1. **Direct conflict with DP‑4 and C‑SC‑4 unless you duplicate context.** Evidence-only excerpts become decontextualized unless each includes the claim/ruling it supports. That either forces duplication (“every ayah excerpt repeats the ruling”) or requires link-outs that recreate the “puzzle” workflow the owner explicitly rejects. fileciteturn20file0L1-L1 fileciteturn11file0L1-L1

2. **Taxonomy-driven splitting violates the excerpting/taxonomy boundary.** Excerpting is intentionally designed not to be steered by taxonomy structure (“no proposed_leaf; taxonomy owns structure”). Evidence-type leaves and per-ayah leaves are closer to a *faceted dimension* than a topic taxonomy; encoding them as primary taxonomy structure will pressure excerpting to chase tree shapes. fileciteturn20file0L1-L1

3. **Excerpt explosion and maintenance burden.** “Per verse per scholar per source” can balloon excerpt counts dramatically. That amplifies downstream work (placement, deduplication, synthesis) and increases the chance of misplacement or inconsistency. The owner’s own first review comment shows they are already sensitive to harmful over-granularity. fileciteturn11file0L1-L1

4. **It still doesn’t solve “compare across scholars” cleanly without synthesis.** Even if you pre-split excerpts, the act of comparing scholars’ evidence is inherently a synthesis-like operation: you need clustering (same verse across sources), normalization (verse ID), and presentation (side-by-side). Pre-splitting reduces one dimension of work but does not eliminate the need for an evidence-aware comparison layer.

## Concrete recommendation

### Recommendation

Do **not** change excerpt granularity to satisfy evidence-type comparison. Keep excerpts as **self-contained teaching units** (often “ruling + evidence together”) and make synthesis (and/or the scholar interface fed by synthesis’ structured output) explicitly produce the owner’s desired comparison view.

This is the most architecturally coherent choice because:

- It respects excerpting’s integrity constraints (self-containment + DP‑4). fileciteturn20file0L1-L1  
- It uses synthesis for the kind of transformation it is explicitly designed for, and for which it already expects `content_types` / `evidence_refs`. fileciteturn19file0L1-L1  
- It addresses the owner’s “avoid puzzles” requirement by preserving context in the primary units while still allowing evidence-type aggregation in the entry. fileciteturn11file0L1-L1  

### What to build (minimal, high-leverage changes)

First, treat this as an “evidence map” feature inside synthesis rather than a debate about excerpt boundaries.

**Make these changes first (bottleneck-first):**

1. **Guarantee evidence metadata completeness enough for Quran aggregation.**  
   The excerpting spec already defines `evidence_refs` with `(surah, ayah_start, ayah_end)` and validity checks, but it allows unresolved cases. If the owner’s “per ayah” view is a priority, you need an implementation plan to resolve most Quran references into canonical IDs—either:
   - implement the deferred “LLM-assisted evidence resolution” hinted by the excerpting spec (so unresolved Quran snippets become resolved IDs upstream), or  
   - implement Quran-reference resolution inside synthesis as a deterministic helper that turns excerpt text snippets into canonical IDs *with strict traceability and validation*, and writes them back into the entry’s structured evidence map (not back into the excerpt). fileciteturn20file0L1-L1 fileciteturn19file0L1-L1

2. **Extend synthesis’ structured output with an inverted evidence index.**  
   The synthesis spec already supports evidence per position (`scholarly_positions[].evidence_refs`). Add an additional structured object (even if initially “internal-only” for UI) that inverts this:
   - `evidence_type → evidence_item → [ (position_id, scholar_ids, excerpt_ids, citation_ids) ]`  
   This directly powers the owner’s “side-by-side” display without pre-splitting excerpts. fileciteturn19file0L1-L1

3. **Treat “evidence-type browsing” as a facet, not taxonomy structure.**  
   The owner describes evidence-type leaves, but given the architecture, implement this as a *view/filter* at a leaf (or within an entry) driven by excerpt `content_types` / `evidence_refs`, not as a taxonomy branching decision that pressures excerpt boundaries. fileciteturn20file0L1-L1

### A crisp decision rule for future disputes

If a proposed excerpt split’s primary motivation is “so that taxonomy can have a leaf for it,” default to **no**—unless you can show the split preserves `FULL` self-containment **without introducing context puzzles** and without violating DP‑4 in practice. That burden is high by design. fileciteturn20file0L1-L1 fileciteturn11file0L1-L1

If the goal is “the owner needs to compare X across scholars,” default to **synthesis/UI restructuring** supported by richer metadata, because comparison is inherently a multi-source, cross-excerpt operation. fileciteturn19file0L1-L1

### Summary answer to your evaluation prompts

- **Architecturally sound per VISION?** Yes: excerpting is meant to preserve self-contained scholarly thoughts and resist taxonomy-driven splitting; synthesis is explicitly designed to reorganize placed excerpts into study-optimized entries, and it already expects evidence metadata. fileciteturn7file0L1-L1 fileciteturn20file0L1-L1 fileciteturn19file0L1-L1  
- **What metadata must excerpts carry?** At minimum: `content_types` and high-recall `evidence_refs` (canonical Quran IDs), plus attribution/school metadata so comparisons remain correct. For best results: a position↔evidence mapping emitted by synthesis (or upstream DC‑05 evidence chain reconstruction). fileciteturn19file0L1-L1 fileciteturn20file0L1-L1  
- **Does ENTRY_EXAMPLE already show the organization?** Not specifically for evidence types; it shows that entries must be richly structured and that metadata enables transformative organization beyond flat excerpt lists. fileciteturn15file0L1-L1  
- **Risks of pushing responsibility to synthesis vs excerpting?** Synthesis risk is evidence-ID and evidence→position attribution quality; excerpting risk is violating self-containment/DP‑4 or forcing duplication/link puzzles, plus taxonomy-driven distortion and excerpt explosion. fileciteturn19file0L1-L1 fileciteturn20file0L1-L1 fileciteturn11file0L1-L1