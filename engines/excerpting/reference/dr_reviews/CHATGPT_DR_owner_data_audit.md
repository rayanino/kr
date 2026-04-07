# KR Owner-Dependent Data Audit for the Excerpting Engine

## Scope, evidence base, and operational constraint

This audit treats “owner-dependent data” as **any value, preference, threshold, definition, priority ordering, or judgment rule** that cannot be inferred safely from text alone and that materially affects excerpt correctness or what the owner can safely study from.

The evidence base is restricted to the requested branch artifacts in the entity["company","GitHub","code hosting platform"] repo, especially: the preserved owner collections (F1–F8, G1–G4, SC1), the questionnaire design + translation mapping, the v2 campaign analysis set (2,303 excerpts), and the excerpting SPEC (including §1.1b “Foundational Principles”). fileciteturn24file0 fileciteturn16file0 fileciteturn17file0 fileciteturn60file0

A key planning constraint is explicit in the repo: **Foundations Q&A (F1–F8) is complete** and additional bundles exist for granularity (G*) and self-containment/context (SC*). fileciteturn24file0

## Collected data inventory

### What “bundles” currently exist and how they differ structurally

There are two distinct “bundle/collection” shapes in the repo:

- **Canon-style / doctrine backfill bundle** (F1): a mini-canon with principles, unresolved tensions, examples, tests, and traceability, plus preserved raw artifacts. fileciteturn55file0 fileciteturn56file0 fileciteturn57file0
- **Questionnaire collection bundles (15–17 file format)** (F3–F8, G1–G4, SC1): a repeated bundle layout anchored by `00_manifest.yaml`, `01_questionnaire_answer.md`, plus structured “decision ladder”, nonnegotiables, red-team tests, and traceability. fileciteturn43file0 fileciteturn45file0 fileciteturn47file0 fileciteturn53file0 fileciteturn4file0 fileciteturn30file0 fileciteturn34file0 fileciteturn36file0 fileciteturn38file0
- **Lightweight user-model package** (F2): explicitly *not* a doctrine/canon bundle; it preserves a narrative owner answer, a machine-friendly workflow YAML, and non-authoritative inference layers with warnings. fileciteturn41file0 fileciteturn42file0

This structural heterogeneity already creates analysis friction: “F1” is a canon dossier; “F2” is a user model capture; many others are 15–17 file structured bundles. fileciteturn41file0 fileciteturn57file0

### Bundle-to-owner-data mapping

The mapping below describes **what category of owner-dependent data each bundle captures**, and **which file types** inside the bundle embody that data.

#### Foundations series (F1–F8)

**F1 — excerpt definition canon (mental model; excerpt ontology).**  
Captured data types:
- A **3-level excerpt quality model** (“excerpt candidate”, “acceptable excerpt”, “directly study-ready”) and the *tensions* that prevent freezing it. fileciteturn58file0
- A **principle set + test cases** for excerpt-definition judgements (explicitly evidence-limited and provisional in places). fileciteturn57file0 fileciteturn58file0
- Preservation of raw owner style as primary evidence artifact(s). fileciteturn55file0 fileciteturn56file0

Primary files:
- `chatgpt_f1_collection/canon/excerpt_definition/01_dossier.md` (definition + tensions + failure conditions) fileciteturn58file0
- `.../03_principles.jsonl`, `.../09_tests.jsonl`, `.../10_coverage.yaml` (canonized judgment atoms/tests) fileciteturn56file0
- `.../source_artifacts/f1_owner_original_notes_2026_04_03.txt` and repo-level `engines/excerpting/f1-owner-original-notes.txt` (raw owner style) fileciteturn2file0 fileciteturn55file0

**F2 — study workflow (user model; consumption assumptions across engines).**  
Captured data types:
- A narrative **study session workflow** (tree-first navigation; “no loose knowledge”; repetition/recall posture), defining what “usable” means in practice. fileciteturn42file0
- Explicit warning separation between owner truth vs retained implications vs non-authoritative inference. fileciteturn41file0

Primary files:
- `chatgpt_f2_collection/01_owner_answer.md` (authoritative owner layer) fileciteturn42file0
- `chatgpt_f2_collection/02_workflow_notes.yaml` (machine-friendly derived workflow) fileciteturn41file0

**F3–F5 — quality baseline, quality floor, self-containment gate (boundary judgement + context philosophy).**  
Captured data types:
- Boundary decisions driven by **function, not surface appearance**; explicit warning against “blind cutting”, and explicit treatment of linking words as hazards requiring intelligence. fileciteturn44file0
- Separation of **khilaf marker vs tarjih** as distinct functions (but not fully resolved systemwide). fileciteturn46file0
- A concrete stance that **context notes can be essential as a patch**, but are not the ideal remedy versus preserving source context / explained-text unity. fileciteturn48file0

Primary files:
- Each `F{3,4,5}_collection/00_manifest.yaml` for file inventory + risk families. fileciteturn43file0 fileciteturn45file0 fileciteturn47file0
- Each `01_questionnaire_answer.md` for the owner’s decision and rationale. fileciteturn44file0 fileciteturn46file0 fileciteturn48file0
- Shared file types inside these bundles: `decision_ladder`, `candidate_excerpts`, `context_dependency_analysis`, `nonnegotiables`, `red_team_tests`, `priority_matrix`, `traceability`. fileciteturn43file0 fileciteturn45file0 fileciteturn47file0

**F6 — proof-text handling and memorization policy (layering; “book-preserved proof” vs “authoritative fetched proof”).**  
Captured data types:
- Owner policy: scholar-book proof text is a **proof witness for analysis**, not the definitive memorization layer; preserve it verbatim; provide comparison layers rather than rewriting. fileciteturn50file0
- This aligns with a SPEC-level foundational principle distinguishing book-preserved proofs vs fetched proofs (and deferring fetched-proof implementation cross-engine). fileciteturn17file0 fileciteturn50file0

Primary files:
- `chatgpt_f6_collection/01_questionnaire_answer.md` + manifest indicating sub-analyses: proof-layer relationships, variant difference policy, memorization policy, text-preservation vs study structuring. fileciteturn49file0 fileciteturn50file0

**F7 — existential failure modes (trust contract; “silent corruption” intolerance).**  
Captured data types:
- Owner’s “stop-using” threshold: **one serious corruption can collapse trust globally**; silent errors are worse than loud ones; provenance and auditability are existential. fileciteturn52file0
- This is reflected in SPEC foundational principles emphasizing knowledge corruption risk, provenance classes, and fail-loud behavior. fileciteturn17file0

Primary files:
- `chatgpt_f7_collection/01_questionnaire_answer.md` + an expanded failure taxonomy + scenarios + damage paths + red team tests. fileciteturn51file0 fileciteturn52file0

**F8 — taxonomy independence and “excerpting-bias” prohibition (stage separation; corruption vs visible misplacement).**  
Captured data types:
- Owner’s central constraint: **taxonomy state must not influence excerpt boundaries**; excerpt integrity precedes taxonomic comfort; overgranulation is more harmful than undergranulation, but the deeper danger is cross-stage contamination. fileciteturn54file0
- This is explicitly mirrored in SPEC’s “taxonomy independence” and the broader anti-covert-excerpter principle. fileciteturn17file0

Primary files:
- `chatgpt_f8_collection/01_questionnaire_answer.md` plus thresholds/scenarios/failure taxonomy and red-team tests. fileciteturn53file0 fileciteturn54file0

#### Granularity series (G1–G4)

From the translation mapping, G1–G4 are the primary owner inputs for granularity and grouping behavior (min/max size, list handling, semantic coupling). fileciteturn60file0

**G1 — minimum excerpt size / “minimum viable unit”.**  
Captured data types:
- Owner preference on minimum viable excerpt length and whether “tiny” units are acceptable (drives merge rules / viability floor). fileciteturn60file0
- Bundle structure includes analyses for added benefit, harmlessness, objectivity vs preference, and context dependency, suggesting the data model is aimed at “how small is too small” and “when small is harmless vs deceptive.” fileciteturn4file0

Primary files:
- `chatgpt_g1_collection/00_manifest.yaml` (schema + file inventory) fileciteturn4file0
- `01_questionnaire_answer.md` (owner decision) fileciteturn3file0

**G2 — maximum excerpt size / long excerpt splitting; hadith-layer stratification.**  
Captured data types:
- Owner boundary preference for long “multi-layer” hadith blocks: treat hadith text, gharib, and overall-meaning as distinct layers; avoid hiding multi-function structure inside one unit. fileciteturn31file0
- Additional subfiles indicate capture of: candidate split map, explanation layers taxonomy, hadith chunking strategy, proof relationship structure, proof identifier strategy, and cross-topic proof reuse. fileciteturn30file0

Primary files:
- `chatgpt_g2_collection/00_manifest.yaml` (file inventory + risk families) fileciteturn30file0
- `01_questionnaire_answer.md` (explicit split boundaries at “غريب الحديث:” and “المعنى الإجمالي:”) fileciteturn31file0

**G3 — numbered list handling (numbering diagnostic vs decisive).**  
Captured data types:
- Owner stance: numbering must **never be the deciding criterion**; separation depends on content/function; numbering mainly increases reassurance/context needs. fileciteturn35file0
- Bundle files target “numbering-noncriterion”, “point identity”, “function multiplicity”, “context reassurance pressures”, and “multi-leaf placement,” signaling the data collected is meant to disambiguate list item identity and prevent “numbering bias.” fileciteturn34file0

Primary files:
- `chatgpt_g3_collection/00_manifest.yaml` + `01_questionnaire_answer.md`. fileciteturn34file0 fileciteturn35file0

**G4 — semantic coupling in condition blocks (don’t overmerge; don’t leave hanging continuation).**  
Captured data types:
- Owner preference: keep conditions separate (each شرط has its own place), but continuation phrases (“تقدم بعضها”) create a real dependency; require stronger continuation support than a minimal note; allow “short harmless” carryover only when truly harmless. fileciteturn37file0
- Bundle targets: condition excerpts, proximity rules, continued topic detection, naming vocabulary pressures, and condition branching map. fileciteturn36file0

Primary files:
- `chatgpt_g4_collection/00_manifest.yaml` + `01_questionnaire_answer.md`. fileciteturn36file0 fileciteturn37file0

#### Self-containment and context series (SC1)

**SC1 — context hint sufficiency for excerpt-library (book-reading sufficiency ≠ excerpt-library sufficiency).**  
Captured data types:
- Owner stance: in an excerpt-library, “reference back” notes are often not sufficient; sufficiency requires either immediate linkage to the exact referenced passage or enough restored context so the owner is not forced into hunting/guessing. fileciteturn39file0
- Bundle explicitly labels risk families around “book-context sufficiency misapplied to excerpt-library” and “reference back without context restoration.” fileciteturn38file0

Primary files:
- `chatgpt_sc1_collection/00_manifest.yaml` + `01_questionnaire_answer.md`. fileciteturn38file0 fileciteturn39file0

## Gap analysis against SPEC requirements and campaign error patterns

### What the SPEC already “locks in” from owner-dependent data

The SPEC states that §1.1b’s 22 foundational principles were extracted and hardened from owner Q&A F1–F8 and now constrain implementation decisions. This means **a large portion of “foundational owner-dependent doctrine” is already integrated into the authoritative spec**, not merely stored in bundles. fileciteturn17file0

In particular, the following high-impact owner-dependent constraints appear as foundational principles:

- **Explained + explanation default unity (EE-1)** as the default boundary rule. fileciteturn17file0
- **Context resolution hierarchy** with an explicit anti-“silent rescue” prohibition: if surrounding context is needed, it should not be quietly treated as FULL; it’s PARTIAL/DEPENDENT. fileciteturn17file0
- **Taxonomy independence** (excerpt output invariant to taxonomy state). fileciteturn17file0
- **“Silent corruption is existential”** and a provenance scheme that distinguishes engine-introduced corruption from source ambiguity; governance rules for halts/gates. fileciteturn17file0
- **Overgranulation worse than undergranulation** as a safety/learnability constraint. fileciteturn17file0
- **Book-preserved proof vs fetched proof** as separate layers; fetched-proof layer deferred (cross-engine). fileciteturn17file0

These align strongly with the owner’s foundations answers (F5–F8 especially), implying the “highest-stakes values” (trust, corruption intolerance, stage separation) are largely present by July 1 *if the SPEC is treated as authoritative*. fileciteturn48file0 fileciteturn52file0 fileciteturn54file0 fileciteturn17file0

### Campaign error patterns that remain blocked by missing owner-dependent data

The v2 campaign processed **2,303 excerpts** with **189 errors** total; the `taysir` package dominates the error count (164 errors) in the campaign run fingerprint. fileciteturn16file0  
The repo also records that campaign analysis includes large flag sets for Arabic fidelity and taxonomy readiness (e.g., hundreds of Arabic fidelity flags, dozens of taxonomy readiness flags), indicating systemic quality issues that require either stronger rules, better gating, or different tolerances. fileciteturn24file0

Based on the SPEC’s explicitly deferred areas and the questionnaire translation table, the **owner-dependent data still missing** that would resolve *recurring* error families is:

**Missing data family: conflict resolution priorities across dimensions (S-1).**  
Why it matters: The SPEC explicitly acknowledges real conflicts among principles and introduces precedence logic (e.g., FP-13), but the translation guide still treats “priority ranking / dimension hierarchy” as a separate owner interaction (S-1) mapping into conflict resolution rules. Without a completed owner priority ordering, engineering will repeatedly face ambiguous tradeoffs: e.g., “avoid grammatical bleeding” vs “preserve khilaf integrity,” or “maximize self-containment” vs “avoid overgranulation.” fileciteturn17file0 fileciteturn60file0

**Missing data family: acceptable vs directly study-ready boundary calibration (quality-grade split).**  
Why it matters: The excerpt-definition canon and SPEC both highlight the distinction and explicitly note that the operational boundary is not yet calibrated. This is owner-dependent because it defines what the owner can safely study from without “backward hunting” under real study conditions. It is also centrally tied to the project’s stated existential risk: memorizing from deceptively “FULL” but not study-ready units. fileciteturn58file0 fileciteturn17file0

**Missing data family: khilaf/tarjih deep dive (K-1..K-3).**  
Why it matters: The SPEC explicitly defers full resolution of khilaf vs tarjih separation (FP-8), and the translation table treats K-1..K-3 as required to calibrate DR-3. This is not an edge case: dialectical and disagreement passages are a primary source of silent attribution inversion risk (speaker-role inversion). fileciteturn17file0 fileciteturn60file0  
The Gemini adversarial review also argues that simple length thresholds (e.g., “800 words”) are arbitrary and that structural logic, not length, should decide splitting—creating a concrete decision demand likely requiring owner preference (and/or explicit acceptance of “grammatical bleeding” vs “structural cohesion”). fileciteturn59file0

**Missing data family: evidence organization (E-1..E-3 / DR-2) and its acceptability under Arabic cohesion constraints.**  
Why it matters: The Gemini adversarial review’s critique is precisely about whether metadata (`cross_reference`, `description_arabic`) can compensate for linguistically fractured fragments (e.g., “فأما …”). If the project demands linguistically intact primary text excerpts as “study units,” then DR-2-style splitting must be constrained or replaced (e.g., multi-leaf tagging). Whether that trade is acceptable is not purely engineering; it’s owner-dependent because it governs what the owner will tolerate as a study object. fileciteturn59file0 fileciteturn60file0

**Missing data family: definition splitting calibration (D-1..D-3 / DR-1) under “orphaned conjunction” risk.**  
Why it matters: The same adversarial critique applies to “وفي الشرع …” / “واصطلاحاً …” fragments: if split yields grammar-fractured excerpts, the owner needs to decide which layer is authoritative (text integrity vs atomic granularity). The translation table shows D-1..D-3 are still owner interactions. fileciteturn59file0 fileciteturn60file0

**Missing data family: genre-specific policy toggles (GN-1, GN-2, L-1, L-2).**  
Why it matters: The adversarial review explicitly warns that rules optimized for fiqh evidence splitting can break in nahw/balagha/usul/aqidah. The translation guide makes genre policy and shaahid handling explicit owner-dependent dimensions, and layer handling (editor note ownership; sharh+matn splitting) similarly. Without these answers, “prompt engineering alone” risks baking in fiqh-centric assumptions. fileciteturn59file0 fileciteturn60file0

### Pattern gaps inside already-collected bundles

Even where bundles exist, some “owner-dependent” items remain structurally underdetermined:

- **F1 canon is explicitly evidence-limited, provisional, and tension-heavy**, and it lists multiple “dangerously underdefined” domains that are directly connected to the most dangerous failure modes (e.g., quote-layer handling beyond one case; footnote policy; omission signaling method; “mention vs true topic” threshold). This is a *data gap*, not just an engineering gap: those domains require owner decision or owner-tolerated defaults. fileciteturn58file0 fileciteturn57file0
- **SC1 establishes insufficiency of simple context hints in excerpt-library mode**, but it does not yet provide a complete owner-defined threshold for when a partial excerpt becomes unacceptable (i.e., a precise “context-restoration sufficiency” rule across genres), and the translation guide treats SC2 and SC3 as additional interactions still needed. fileciteturn39file0 fileciteturn60file0

## Error-pattern owner dependency

This section classifies error categories into those that require **owner input to resolve safely** vs those that are primarily solvable via **prompting/engineering** once owner constraints are known.

### Category-level classification

**Boundary errors (where one unit ends and another begins).**  
- Owner-dependent when the boundary is a **preference tradeoff** (e.g., split vs keep together for pedagogy, minimum viable unit, how much “harmless carryover” is acceptable). These are directly targeted by G1–G4 and parts of F3–F5. fileciteturn60file0 fileciteturn31file0 fileciteturn35file0 fileciteturn37file0 fileciteturn44file0
- Mostly prompt/engineering-solvable when the failure is an **objective self-containment breach** (e.g., isolated refutation without the refuted view; question without answer), because the SPEC already defines decontextualization prevention patterns (DP-*) and self-containment criteria (C-SC-*). fileciteturn17file0

**Classification errors (wrong scholarly function tags).**  
- Mostly prompt/engineering-solvable once the taxonomy of functions is stable, because the SPEC defines the ScholarlyFunction enum and classification prompt constraints; owner input is secondary except where classification determines study presentation or triggers the “study readiness” threshold. fileciteturn17file0
- Owner-dependent mainly in the sense that the owner must define what misclassifications are *existential* vs tolerable (ties back to F7/F8 severity philosophy). fileciteturn52file0 fileciteturn17file0

**Context/self-containment errors (FULL vs PARTIAL vs DEPENDENT; sufficiency of notes/cross-refs).**  
- Strongly owner-dependent because the owner’s study posture is “trust the library; don’t hunt; memorize safely” (F2, F7), and SC1 explicitly states book-reading sufficiency does not carry over to excerpt-library. The boundary between “acceptable with hint” and “unsafe to study” is fundamentally a user-model decision. fileciteturn42file0 fileciteturn52file0 fileciteturn39file0
- Engineering can implement gates and context mechanisms, but the threshold and acceptable failure rate are owner-dependent because they affect trust collapse risk. fileciteturn17file0

**Granularity errors (over/under-splitting; list items; condition blocks; “too small to matter”).**  
- Strongly owner-dependent: the SPEC itself elevates overgranulation harm and the owner explicitly prioritizes “no scattering” and “each condition has its own place” while rejecting “numbering decides.” These are not purely technical; they define the library’s learning unit identity. fileciteturn17file0 fileciteturn54file0 fileciteturn35file0 fileciteturn37file0

### Error families that can be fixed without new owner data

These are “prompt engineering / deterministic validation” targets because the owner stance is already clear enough and/or the SPEC already codifies the rule:

- Text mutation / diacritic loss / silent changes: owner already requires verbatim preservation; SPEC encodes immutability and corruption intolerance. fileciteturn50file0 fileciteturn17file0
- Taxonomy-driven excerpting (“excerpting-bias”): owner explicitly forbids; SPEC codifies taxonomy independence and anti-covert-excerpter. fileciteturn54file0 fileciteturn17file0
- Basic decontextualization patterns (question+answer, position+refutation, condition+exception) where the SPEC already defines the rule; remaining work is enforcement quality, not owner preference. fileciteturn17file0

### Error families that remain blocked without new owner data

These cannot be “prompt-fixed” responsibly because the correct behavior depends on unresolved owner tradeoffs:

- Evidence splitting vs grammatical cohesion: whether metadata compensation is acceptable for fragments like “فأما …” or “وفي الشرع …”, and whether multi-leaf tagging is preferable to physical splitting. fileciteturn59file0 fileciteturn60file0
- Khilaf/tarjih structuring rules: the SPEC defers full resolution, and adversarial feedback disputes current heuristics. fileciteturn17file0 fileciteturn59file0 fileciteturn60file0
- The operational acceptability threshold (“acceptable” vs “study-ready”): both the canon dossier and SPEC mark this as real but not calibrated. fileciteturn58file0 fileciteturn17file0
- Cross-genre policy divergence: how the same structural signals should behave in nahw/usul/aqidah vs fiqh/hadith commentary. fileciteturn59file0 fileciteturn60file0

## Bundle format evaluation

### What the 15–17 file format gets right

The recurring bundle pattern (manifest → owner answer → structured sub-analyses → nonnegotiables → red team tests → priority matrix → traceability) has high analytic leverage:

- It separates **raw owner reaction** from **processed decision** and from **engineering expansion**, at least in intent (manifest “source_basis” and raw layer paths). fileciteturn30file0 fileciteturn34file0 fileciteturn38file0
- It produces **machine-extractable sub-structures** that are directly usable for gap analysis: decision ladders, candidate split maps, terminology inventories, and explicit high-risk issue families. fileciteturn30file0 fileciteturn43file0 fileciteturn45file0
- It includes **traceability artifacts** designed to connect owner answers to later SPEC/prompt changes (a necessary invariant for auditing correctness in a “trust collapse” risk model). fileciteturn38file0 fileciteturn51file0

### Format weaknesses that hinder cross-bundle analysis

**Inconsistent manifest schemas across bundles.**  
Examples:
- `source_basis` appears as a list in some manifests but as a key-description map in others, and bundle IDs / status fields vary (`collection_preservation`, `questionnaire_collection`, `collection_preservation_bundle`, etc.). This blocks automated inventory queries (“show me all bundles with model_expansion items > 0” or “show all bundles that depend on inferred_from_prior_chat”). fileciteturn30file0 fileciteturn36file0 fileciteturn38file0
- Final choice field names vary: `final_questionnaire_choice`, `selected_questionnaire_choice`, and “MC choice: none” conventions differ, making it difficult to aggregate at scale. fileciteturn30file0 fileciteturn49file0 fileciteturn53file0

**Raw-layer path conventions are not stable.**  
Some manifests reference raw artifacts within the same bundle; others reference paths in a different directory (e.g., G3 manifest points at `engines/excerpting/chatgpt_g3_collection/...` while the bundle itself is under `..._bundle/.../chatgpt_g3_collection/...`). That complicates “single-bundle integrity checks” and automated portability. fileciteturn34file0

**F-series structural discontinuity.**  
F1 is canon-style; F2 is explicitly a different kind of package; others are 15–17 structured bundles. This is not inherently wrong, but it prevents uniform tooling without an explicit “bundle_type” discriminator and schema registry. fileciteturn41file0 fileciteturn57file0

### What’s missing vs redundant, strictly as data artifacts

**Missing (high leverage for cross-bundle analysis):**
- A single, standardized **machine-readable “final decisions” file** per bundle (key/value with stable IDs that downstream code/tests can consume), distinct from narrative answer and from the decision ladder. Right now, “decision ladder” and “hard judgment” exist, but there is no guaranteed single source-of-truth for the final resolved values across bundles. fileciteturn30file0 fileciteturn38file0
- A standardized **evidence/authority tagging scheme** for each atomic claim (explicit owner, inferred, model expansion). Manifests summarize counts (`total_explicit_draft_items`, etc.), but the per-atom labeling consistency is not guaranteed by a shared schema. fileciteturn30file0 fileciteturn34file0
- An `inventory.json`-style **integrity manifest** (hashes, line counts, file count) appears for F1 and F2 but is not uniformly present for the 15–17 bundles, making provenance auditing harder. fileciteturn56file0 fileciteturn41file0

**Potentially redundant (or at least structurally overlapping):**
- In the 15–17 bundles, both `case_dossier.md` and `hard_judgment.md` often serve as narrative “why” with examples. Without a strict schema boundary between them, they can become duplicative and harder to diff across bundles. The manifests list both consistently but do not specify non-overlap rules. fileciteturn30file0 fileciteturn45file0
- Terms inventories (`terms.yaml`) are repeated per bundle; that is useful locally, but for cross-bundle analytics it creates duplication unless there is an explicit global term registry and per-bundle term deltas. (This is a data-structure note, not a UX suggestion.) fileciteturn30file0 fileciteturn43file0

## Tedious-now vs defer-to-summer classification for remaining owner-dependent gaps

The translation guide makes clear that many **owner interactions beyond F/G/SC** exist and map to SPEC rules and DR decisions (D*, E*, K*, GN*, L*, CJ*, S*). fileciteturn60file0

The key discriminator here is whether the owner must provide **deep judgment / extended reasoning** (tedious) versus simple selection or numeric tolerance (non-tedious).

### Tedious gaps that should be collected within the Apr–Jun window

These require nuanced tradeoffs, deep domain reasoning, or stable personal preferences that cannot be safely inferred:

- **S-1 priority ranking (dimension hierarchy / conflict resolution).** This is the universal tie-breaker when owner desires conflict (self-containment vs cohesion; granularity vs integrity; etc.). fileciteturn60file0
- **S-2 ideal excerpt vs worst excerpt definition** with concrete examples and why (needed to calibrate review metrics and “study-ready” thresholds, especially given F1’s unresolved acceptability/study-ready boundary). fileciteturn60file0 fileciteturn58file0
- **K-1..K-3 khilaf/tarjih deep dive.** Required because the SPEC defers full resolution and because adversarial review disputes simplistic thresholds. fileciteturn17file0 fileciteturn59file0 fileciteturn60file0
- **E-1..E-3 evidence structuring (DR-2) decisions** because they trade off atomic granularity against Arabic cohesion and pedagogical integrity; this is a core owner-dependent acceptability choice, not a mere prompt tweak. fileciteturn59file0 fileciteturn60file0
- **D-1..D-3 definition splitting calibration (DR-1) decisions**, for the same “orphaned marker” reason and cross-genre safety. fileciteturn59file0 fileciteturn60file0
- **GN-1 / GN-2 genre policy, including shaahid handling**, because the owner tolerance for splitting vs keeping examples is highly science-dependent and can silently corrupt meaning if mishandled in nahw/balagha/usul. fileciteturn59file0 fileciteturn60file0
- **L-1 / L-2 layer handling judgments** in cases where deterministic layer metadata conflicts with pedagogical coherence (e.g., editor note ownership and sharh/matn split expectations). fileciteturn60file0

### Non-tedious gaps that can plausibly be deferred

These are closer to “parameter selection” than deep doctrine, and can be collected later without forcing extended writing—*provided* the system has safe defaults that block unsafe study surfaces:

- Numeric or categorical calibration that is already framed as **prompt parameters** (e.g., min/max thresholds, simple gating strictness) once the deeper doctrine is decided. The translation guide explicitly maps many dimensions to prompt parameters and defaults, implying these can be iterated without re-asking deep questions if the owner’s doctrine is fixed. fileciteturn60file0
- **Metadata display field selection (CJ-4)** could be deferred if the pipeline can store all metadata and postpone the “default surfaced set” decision. (This is arguably “non-tedious” because it can be chosen from a list, but it does still depend on the owner’s study posture.) fileciteturn60file0

## Collection priority order

This priority order is derived from (a) existential risk to trust (F7), (b) whether prompt/engineering can proceed without the decision, and (c) cross-cutting leverage (one decision resolves many downstream ambiguities).

### Highest priority: unblock correctness governance and calibration

**Priority: S-1 (priority ranking / conflict resolution).**  
This is the global resolver for contradictions and is explicitly referenced as the conflict resolution mechanism when owner answers collide. Without it, the team cannot safely “decide for the owner” in edge cases without risking trust collapse. fileciteturn60file0

**Priority: S-2 (ideal vs worst excerpt definition) + “study-ready” threshold calibration.**  
The excerpt definition canon and SPEC both mark “study-ready vs merely understandable” as real but not operationally calibrated, and the owner’s workflow + failure intolerance makes this the practical safety boundary for what can be studied without hunting. fileciteturn58file0 fileciteturn42file0 fileciteturn52file0 fileciteturn17file0

### Next: resolve the biggest semantic-corruption risk clusters

**Priority: K-1..K-3 (khilaf/tarjih) decisions.**  
Dialectical integrity failures can invert speaker roles (catastrophic under the project’s corruption model). The SPEC already elevates speaker-role correctness and dialogue completeness, and explicitly defers full khilaf/tarjih resolution to these questions. fileciteturn17file0 fileciteturn60file0

**Priority: E-1..E-3 (evidence splitting / DR-2) decisions.**  
Adversarial analysis shows a sharp tension: computational soundness vs linguistic/pedagogical integrity of the excerpt text. Owner acceptance is required because this affects what is a valid “teaching unit” to study. fileciteturn59file0 fileciteturn60file0

**Priority: D-1..D-3 (definition splitting / DR-1) decisions.**  
Same structural risk: orphaned conjunctions and semantically hollow splits, plus cross-genre hazards. fileciteturn59file0 fileciteturn60file0

### Then: lock genre and layer invariants before scaling

**Priority: GN-1 / GN-2 (genre policy; shaahid handling).**  
The cross-genre warning is explicit: rules good for fiqh may break in nahw/balagha/usul/aqidah. Owner-dependent policy decisions here prevent systematic corruption once the corpus broadens. fileciteturn59file0 fileciteturn60file0

**Priority: L-1 / L-2 (layer handling).**  
Layer attribution mistakes are a top “silent failure” class (misattribution is existential in the corruption model). Even where deterministic layer overlap exists, the owner may need to define how to handle editor insertions and sharh/matn packaging at the excerpt level. fileciteturn17file0 fileciteturn60file0

### Lower priority: parameter refinement after doctrine is fixed

Only after the above are resolved should the team spend owner time on incremental parameter tuning (because these can often be iterated via engineering and re-run evaluation once doctrine is fixed):

- Remaining SC interactions (SC2, SC3) and any “CJ” calibration questions that become purely comparative once a stable doctrine exists. fileciteturn60file0