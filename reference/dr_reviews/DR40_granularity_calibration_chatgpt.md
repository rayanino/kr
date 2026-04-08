# Recalibrating Excerpt Granularity for Leaf-Level Comparison in an Islamic Scholarly Text Pipeline

## Context and failure mode in the rejected excerpts

**Fact (from owner feedback):** The owner rejected two excerpts because they were **too broad**: they bundled multiple scholarly functions into one “teaching unit,” preventing leaf-level comparison across scholars and sources. fileciteturn3file0

**Fact (talaq definition rejection):** The pipeline merged **تعريف الطلاق لغة** and **تعريف الطلاق شرعًا** into one excerpt; the owner expects **two separate excerpts** because they map to different taxonomy leaves. The owner also emphasized that the شرعًا excerpt must not begin with a contextless fragment like “وفي الشرع...” and that the relationship sentence (“والتعريف الشرعي فَرْد من معناه اللغوي العام…”) should remain attached to the شرعًا definition to preserve meaning. fileciteturn3file0

**Fact (talaq ruling rejection):** The pipeline produced one excerpt containing: (i) a general hukm statement, and then (ii) proofs from the **Qur’an**, **Sunnah**, and **ijmāʿ**—and the owner wants this decomposed into (a) an “overall ruling” excerpt, (b) separate excerpts per evidence type, and (c) even **per-ayah** granularity for Qur’anic proofs. The stated product goal is: “open a taxonomy leaf and compare all scholars’ positions on exactly that atomic point across sources.” fileciteturn3file0

**Inference:** The rejections are not “minor boundary nitpicks.” They reveal that the current operational definition of a “teaching unit” is misaligned with the owner’s product definition of the excerpt as an **atomically classifiable scholarly function** suitable for leaf-level comparison. This is consistent with the internal postmortem that frames the same two rejections as a systemic calibration problem (not a one-off model miss). fileciteturn20file0

## What the current SPEC and prompt stack are implicitly optimizing for

**Fact:** The project’s grouping prompt explicitly defines teaching units as “self-contained scholarly segments” and then encodes a set of defaults that tend to **bind evidence to the ruling** and “complete thought” packaging. Examples include:
- “An explained object and its immediately following explanation form one teaching unit… ruling + evidence.”  
- “A position + its evidence + any counter-evidence + conclusion = one unit.”  
- “Evidence cited for a ruling MUST stay with the ruling.” fileciteturn16file0

**Fact:** The same prompt architecture also hard-codes a conflict-precedence ladder where **granularity is last** (“Granularity — lowest priority; optimize separately”), behind self-containment, textual integrity, dialogue completeness, and speaker-role correctness. fileciteturn16file0

**Fact:** The pipeline has a 16-type scholarly-function schema (definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma, etc.), but the grouping phase is allowed—by design—to emit teaching units with one `primary_function` and multiple `secondary_functions`, which is exactly the “function mixing” the owner is rejecting for taxonomy-leaf comparisons. fileciteturn17file0

**Fact:** The internal “scholarly reality check” document concludes that the SPEC rule “position + evidence = one unit” is directly in tension with the owner’s demand for fine-grained evidence splitting, and it proposes new domain rules (definition splitting, evidence-type splitting, and khilāf preservation) plus narrower “evidence must stay with ruling” constraints. fileciteturn20file0

**Inference:** Even if the LLM were “perfect,” the current instruction stack makes the rejected behavior a *reasonable compliance outcome*: it treats paragraph-coherence and “complete thought” packaging as primary, and leaf-level comparison as an optimization goal rather than a boundary constraint. fileciteturn16file0turn20file0

## Is the owner’s vision achievable without destroying self-containment, and how did classical scholars structure cross-reference?

### Achievability without breaking self-containment

**Fact (owner requirement):** The owner is not asking for blind micro-fragmentation—e.g., they explicitly reject leading-fragment starts (“وفي الشرع…”) and want enough context to avoid question-mark comprehension. fileciteturn3file0

**Fact (existing design tools):** Your own materials already encode the key technique to reconcile “atomic leaf placement” with “understandable excerpts”: include **minimal required context**, distinguish “core” vs “context,” and/or encode linkages as metadata/cross-references rather than forcing everything into one text span. The excerpt-definition document makes “comprehensibility in isolation” a core requirement while allowing context inclusion when strict topical cutting would produce dangling references. fileciteturn26file0

**Recommendation:** Treat “self-containment” as **function-relative**, not “topic-encyclopedia complete.” Concretely:
- A `definition` unit is self-contained if it states the definiendum and the definition (and includes small bridging language to avoid a “وفي…” fragment).
- An `evidence_quran` unit is self-contained if it includes (i) the verse citation or verse text as present, and (ii) the scholar’s stated inference/istidlāl for the *specific* hukm leaf (or else a structured link to the hukm excerpt it supports).  
This preserves the owner’s desire not to “solve puzzles” while still allowing evidence units to remain separate. fileciteturn3file0turn26file0

### What classical organization implies for paragraph-level vs function-level cross-reference

Classical Islamic literature is not monolithic; different genres carve the knowledge space differently.

**Fact (hadith compilation structures):** Hadith collections vary in organization: some (musnad-type) arrange reports by **Companion/transmitter**, while later canonical collections are more often arranged by **subject headings**, making them easier for topical legal retrieval. This indicates that “atomic proof units” (individual hadiths) are a recognized organizational primitive, and that book-level structure was explicitly engineered for cross-reference use-cases. citeturn1search0

**Fact (mukhtaṣar genre):** The genre of **mukhtaṣar** functions as concise legal manuals (often used pedagogically for memorization), while later layers (commentaries) expand, dispute, and evidence the same base text. This is essentially a **function-layer separation** across works: “rulings-only” presentation in one layer/genre, evidence and reasoning in another. citeturn3search0

**Fact (sharḥ and ḥāshiya traditions):** In later scholarly cultures, significant intellectual work often appears as **sharḥ** (commentary) and **ḥāshiya** (gloss) on a base text, rather than as brand-new monographs—again creating a de facto decomposition between “base propositions” and “explanatory/critical apparatus.” citeturn2search0turn2search4

**Fact (verse-centered legal exegesis):** The existence of “legal verse” traditions (e.g., tafsīr works focusing on verses of rulings, and modern scholarship describing “Ayat al-Ahkam” works as selecting legal verses and organizing them thematically) supports the idea that **per-ayah granularity** is not an alien abstraction—it is a historically meaningful indexing primitive. citeturn1search3turn3search4

**Inference:** Classical authors often *write* in mixed-function paragraphs (especially in fiqh discussions), but the broader ecosystem creates cross-reference via **genre decomposition** (mukhtaṣar vs sharḥ), and by using **atomic proof objects** (one hadith; one verse) as retrieval units in hadith/tafsīr contexts. That makes the owner’s “one scholarly function per excerpt; per-ayah for Qur’anic proofs” vision historically plausible—provided the pipeline carries the linking metadata needed to keep each atomic unit interpretable. citeturn1search0turn3search0turn1search3turn3search4

## Recalibrating FP-1, FP-9, and FP-13 without collapsing the product vision

### FP-9 vs FP-13: taxonomy granularity is not excerpt boundary granularity

**Fact (current behavior):** The grouping prompt currently embeds both (a) an overgranulation warning (“overgranulation is more harmful than undergranulation”) and (b) a precedence ladder that makes granularity the last priority. fileciteturn16file0

**Fact (owner reality):** The owner’s rejections show that, for this product, the *dominant risk* is **undergranulation at the excerpt boundary**, because it destroys leaf-level comparison. fileciteturn3file0

**Fact (internal analysis):** The internal decision memo explicitly distinguishes “tree-agnostic excerpting” from tree design, and argues that fine-grained excerpting is the correct architectural response (not intra-excerpt spans), stating that under-granularity blocks synthesis and leaf comparison. fileciteturn20file0

**Recommendation (principle-level):** Split the overloaded idea of “granularity” into two separately governed axes:
1. **Taxonomy granularity (tree depth / leaf carving):** FP-9 can still hold here—over-splitting the tree can create navigation and maintenance debt.
2. **Excerpt granularity (segmentation boundaries):** invert the presumption for this axis: undergranulation at boundaries is often worse, because it prevents leaf-level comparison and forces later re-processing.  
This aligns with the internal position: “over-granularity is recoverable; under-granularity is not” for synthesis at fine leaves. fileciteturn20file0

### FP-1 “teaching unit unity” should be redefined, not dropped

**Fact:** The excerpt-definition document formalizes “comprehensibility in isolation” and allows context expansion when strict cutting would produce dangling references. This is the non-negotiable content-integrity core behind FP-1. fileciteturn26file0

**Fact:** The owner explicitly agrees with that core by rejecting cut-off fragments and requiring self-contained context for “شرعًا” definitions. fileciteturn3file0

**Recommendation (redefinition):** Reframe FP-1 from “complete thought” to “complete *scholarly act*.”  
A unit should be “complete” with respect to its `primary_function` **and its target leaf**, not necessarily complete as a mini-lesson containing every supporting proof. Concretely: a rule_statement unit can be complete without all proofs attached, if the proof units link back. fileciteturn17file0turn26file0

### FP-13 precedence stack: move “leaf comparability” up, but keep the safety rails

**Fact:** The current precedence stack in the prompt system makes granularity last. fileciteturn16file0

**Recommendation:** Keep the top safety invariants (speaker-role correctness; dialogue completeness; textual integrity) but promote leaf-level comparability above the current “bundle everything for completeness” heuristics. A practical replacement stack for *boundary decisions* could be:
1. Attribution/speaker-role correctness (avoid false beliefs)
2. Dialogue integrity (objection + response stay together)
3. Textual/grammatical integrity (no fragments)
4. **Leaf-atomicity constraint:** one excerpt → one leaf (by function + scope), with limited, explicitly sanctioned context carryover
5. Pedagogical packaging (optional, UI-layer concern, not boundary-layer concern)

This preserves the safety-critical priorities already encoded while making the owner’s leaf-compareability a boundary constraint rather than an afterthought. fileciteturn16file0turn3file0

## Closing the loop from owner rejections to segmentation decisions

### What exists today

**Fact:** The repository includes a review server that writes `owner_feedback.jsonl` entries keyed by `excerpt_id` and includes a content hash to detect stale feedback. However, this is currently a *collection mechanism*; it does not automatically drive prompt/rule changes or regression tests. fileciteturn19file0

**Fact:** The internal “scholarly reality check” already uses the two owner rejections to motivate concrete rule changes (DR-1/DR-2/DR-3) and a schema extension for cross-references, indicating there is an existing path from feedback → spec change, but it is a document-level manual loop rather than an automated production loop. fileciteturn20file0

### How production NLP/IR systems usually operationalize segmentation feedback

**Fact (segmentation evaluation):** Text segmentation has established evaluation metrics and framing. Work on segmentation includes both algorithmic approaches (e.g., lexical cohesion / topic change segmentation) and statistical boundary models trained from labeled boundaries. citeturn0search1turn8search2

**Fact (metrics):** The literature highlights pitfalls in segmentation metrics (e.g., Pk) and introduces alternatives like **WindowDiff**, which penalizes boundary-mismatch within moving windows and is widely implemented (e.g., in NLTK). citeturn8search9turn8search7

**Fact (human-in-the-loop):** Active learning is a standard approach when labels are expensive: the learner selects which instances to query from a human “oracle” to improve accuracy with fewer labels. This is particularly relevant when owner time is scarce and segmentation mistakes are heterogeneous. citeturn8search0turn8search48

### A concrete mechanism for this pipeline

**Recommendation (data model for feedback):** Extend owner feedback from “freeform rejection text” to a minimally structured boundary-correction schema that is still lightweight for humans:
- `reject_reason_code`: e.g., `needs_split_by_function`, `fragment_start`, `evidence_granularity_too_coarse`
- `expected_units`: list of expected unit spans (segment-index ranges) *or* “must-split between segment i and i+1”
- `must_link`: optional links that must remain together (e.g., “relationship sentence stays with شرعًا definition”)

This directly connects the rejection to the pipeline decision point: grouping boundaries over classified segments. fileciteturn17file0turn3file0

**Recommendation (regression harness):** Treat each rejected excerpt as a regression fixture:
1. Re-run Phase 2a/2b on the original chunk.
2. Assert the produced unit boundaries match the `expected_units` constraints.
3. Track acceptance as a CI gate for prompt/rule changes.

This is especially compatible with your architecture because grouping outputs are already JSON-structured by `segment_indices` and validated by invariants. fileciteturn17file0turn4file0

**Recommendation (metrics + sampling):** Add an offline evaluation job that computes WindowDiff (or similar) between “gold boundary” fixtures and pipeline output. Then use active-learning style sampling: surface “high disagreement / high uncertainty” chunks to the owner for labeling, instead of random review. citeturn8search9turn8search0

**Options (how to “learn” from feedback):**
- **Prompt/rule iteration (fastest):** Implement DR-1/DR-2/DR-3-like domain rules as *explicit grouping constraints* and iterate via regression tests. fileciteturn20file0turn16file0  
- **Deterministic post-processor (high leverage):** After LLM grouping, automatically split any unit that contains multiple evidence types or multiple ayah_refs into separate units, then re-check self-containment and attach cross-reference metadata. This reduces dependence on prompting the LLM to “remember” every granularity rule. fileciteturn17file0turn20file0  
- **Supervised boundary model (longer-term):** Convert grouping to a boundary prediction problem over segments and train from accumulated labeled boundaries. This is the “Beeferman/Berger/Lafferty” style framing (“features correlated with boundaries in labeled training text”). citeturn8search2

## Small divisions and the supposed “pre-chunk bypass” issue

### What the current branch actually does

**Fact:** In the referenced branch, the pipeline orchestrator runs Phase 2 classification and grouping for all chunks whenever an LLM client is provided; the only “skip” is global (no LLM client → no Phase 2). There is no evidence in the orchestrator of a production-path that bypasses function-level grouping *because a chunk is small*. fileciteturn14file0

**Fact:** Phase 1 creates synthetic `_pre` divisions to cover uncovered parent ranges (e.g., chapter preambles) and marks them as synthetic for alignment-check purposes, but it still emits them as normal chunks for downstream Phase 2 processing. fileciteturn12file0

**Inference:** The “13.4% of excerpts bypass LLM grouping” claim looks like either (a) a statistic from a different experiment/version, or (b) a confusion with the unrelated “13.4% diacritics ratio” statistic appearing in corpus reporting. If a bypass exists elsewhere, it is not visible in the branch files reviewed here. fileciteturn14file0turn12file0turn10file0

### Should there ever be a shortcut for small chunks?

**Recommendation:** If cost/latency motivates shortcuts, **do not skip function-level analysis solely based on size**. The internal analysis shows that even short spans can contain fused multi-topic or multi-function content, and that boundary ambiguity is genre-structured rather than length-structured. fileciteturn20file0

**Safer shortcut (if needed):** Allow a bypass only after classification, when a chunk’s segment sequence is provably trivial, e.g.:
- exactly 1 segment, or
- all segments share the same `ScholarlyFunction`, and no evidence refs are present, and no dependency markers (مثل: فإن/لأن/وأما) indicate likely multi-unit structure

This preserves correctness-first behavior while still reducing grouping calls in clearly trivial cases. fileciteturn17file0turn16file0

## Synthesis: a calibrated design that satisfies both self-containment and leaf-level comparison

**Core conclusion:** The owner’s vision is achievable if “self-contained” is treated as “function-complete with resolvable targets,” and if the pipeline encodes explicit linkages between separated units (definition pairs; hukm ↔ evidence units). fileciteturn3file0turn26file0turn20file0

**Concrete recommended changes (minimum viable set):**
1. **Replace the default “ruling + evidence stays together” rule** with a conditional: keep together only when syntactically inseparable or when splitting would violate dialogue/refutation integrity; otherwise split by evidence type and by ayah/hadith where feasible. This matches the internal DR-2 direction and directly remedies rejection #2. fileciteturn20file0turn16file0  
2. **Hard-rule definition pair splitting** (لغة vs شرعًا) while allowing relationship sentences to attach to the “شرعًا” excerpt as context (owner request), remedying rejection #1. fileciteturn3file0turn20file0  
3. **Add explicit relationship links** between resulting excerpts (e.g., `companion_definition`, `evidence_for`). The internal memo’s suggested cross-reference schema extension is a good starting point. fileciteturn20file0turn17file0  
4. **Re-rank priorities** so leaf-atomicity is not last: keep attribution/dialogue/text integrity as the top constraints, then enforce leaf-atomicity, then optimize pedagogical “complete thought” packaging via UI composition and cross-links. fileciteturn16file0turn3file0  
5. **Operationalize owner feedback** into regression fixtures and measured segmentation quality (WindowDiff + targeted active-learning review), closing the loop from rejection → boundary-rule change → validated improvement. fileciteturn19file0turn3file0turn8search9turn8search0