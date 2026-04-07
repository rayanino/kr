# Vocabulary decision for KR excerpting outputs: “Teaching Units” vs “Excerpts”

## Scope, artifacts, and evidence base

This report resolves a vocabulary decision for the KR scholarly text processing pipeline in the `excerpting-foundations-hardening-20260404` branch of the project hosted on entity["company","GitHub","code hosting platform"]. The pipeline currently uses “excerpt” widely (engine name, `ExcerptRecord`, evaluation tooling, prompts, and the SPEC), while the system owner has repeatedly stated that the output should be called “teaching units” (الوحدة التعليمية).

Evidence used:

- **Direct inspection of the codebase artifacts** in the referenced branch (not publicly indexable via web search during this run). Key inspected files include:
  - `engines/excerpting/contracts.py` (contains `TeachingUnit` as a Phase 2b output model and `ExcerptRecord` as the downstream record model).
  - `engines/excerpting/SPEC.md` (defines “teaching units” as the conceptual product in multiple places while still using “excerpt” extensively).
  - `engines/excerpting/src/phase2_group.py` and `engines/excerpting/src/phase3_enrichment.py` (LLM prompts and enrichment scaffolding already frame the product as “teaching units”).
  - `tools/evaluate_excerpts.py` (evaluation is strongly “excerpt”-named at the artifact and schema level).
- **Web research (cited)** for Stage 1, focusing on:
  - Traditional Islamic pedagogy units (matn–sharḥ–ḥāshiyah teaching architecture; lesson practices).
  - Modern Arabic pedagogy meaning of “الوحدة التعليمية”.
  - Western educational technology terminology (“learning object”) as a contrast class.

Important limitation: the user referenced `HARDENING_SESSION_PROTOCOL.md §4.3` as the location of the “Natural Teaching Unit (NTU)” field, but that file was not present in the repository snapshot accessible in this branch. The collision analysis therefore treats the NTU field **as defined in the user’s prompt** (i.e., “the organic knowledge unit for this genre — mas’alah in fiqh, tarjamah in hadith encyclopedias, bayt+qa’idah+shawahid in nahw”) as the authoritative definition for Stage 2.

## Meaning of “teaching unit” in Islamic pedagogical tradition

### What the classical tradition actually “units” around

In the pre-modern madrasa / study-circle paradigm, “unit of teaching” is less a single standardized “curriculum unit” and more a **context-dependent boundary** that emerges from (a) live instruction practices and (b) genre-native textual segmentation.

A strong proxy for how instruction is chunked comes from ethnographic + textual scholarship on traditional study circles at entity["organization","Al-Azhar","Islamic institution Cairo, Egypt"] and entity["organization","Dār al-ʿUlūm","higher education Cairo, Egypt"]: instruction often centers on **a matn (متن)**—a concise, memorizable base text—and then expands via layered commentary. The matn is intentionally compressed, often short and sometimes in verse, requiring unpacking via commentary. citeturn15view0

Crucially for “unit” boundaries: in traditional transmission, a teacher reciting a matn **pauses after every line (sometimes after every word)** to add commentary; this produces a natural micro-granularity where “a teachable unit” can be “one line of matn + its commentary expansion,” rather than a Western-style multi-lesson unit. The same source explicitly describes multiple commentary layers: first-order commentary (sharḥ), then ḥāshiyah as a subsequent layer, and a further (third-order) commentary (taqrīr). citeturn15view0turn15view3

This matters because the KR pipeline’s extraction rule EE-1 (“explained object + immediately following explanation default to one unit”) mirrors this matn→commentary teaching reality. The “natural unit” in many Islamic scholarly genres is not “a themed instructional module”; it is often **the smallest coherent reasoning chunk** that preserves (i) the statement and (ii) what makes it intelligible (definition, proof, refutation, etc.).

### Mapping “teaching unit” to common Islamic textual units

From the standpoint of Islamic textual architecture, several classical labels correspond to different levels of granularity:

- **dars (درس)**: a lesson/lecture session; often tied to a teacher-led reading and explanation practice (not necessarily aligned 1:1 with textual chapter boundaries). In a study of Mauritanian mahdara pedagogy, “the traditional religious lecture (al-dars al-dīnī)” is described as a predominant pedagogy, with explicit references to “daily lesson” practices. citeturn9view1  
  *Implication:* “dars” is plausible as a “unit of instruction,” but it is more **sessional** than **text-segment** by default.
- **bāb (باب) / faṣl (فصل) / kitāb (كتاب)**: structural divisions inside authored works. These are often too coarse for the KR pipeline’s goal (self-contained, atomic study items), though in some traditions a bāb heading itself can carry substantive legal meaning (e.g., fiqh-structured chapter headings, or hadith collection tarājim).
- **mas’alah (مسألة)**: issue/problem unit in fiqh and legal theory writing; frequently close to the “atomic (but not too atomic) knowledge piece.”
- **bayt (بيت) + qāʿidah (قاعدة) + shawāhid (شواهد)**: in grammar/poetry-based instruction, the “unit” is often a verse with its rule and evidences rather than an arbitrary paragraph.

This supports a key distinction that becomes central in Stage 2 and Stage 3:

- **There are “genre-native knowledge atoms”** (mas’alah, hadith item, bayt+rule+shawāhid, etc.).
- **There are “extracted instances”** produced by a segmentation system, which ideally align with those atoms but sometimes must merge/split to preserve self-containment and avoid decontextualization.

The phrase “Natural Teaching Unit” (NTU) as defined in your protocol template is therefore conceptually consistent with Islamic textual practice: it describes the *native atom type* for a genre.

### What “الوحدة التعليمية” usually means in modern Arabic pedagogy

The Arabic phrase **الوحدة التعليمية** is strongly associated with **modern curriculum/instructional design**, typically meaning an integrated package organized around a topic or problem that includes learning objectives, content, teaching methods, activities, and evaluation.

An Arabic pedagogy PDF hosted by entity["organization","Al-Mustansiriyah University","Baghdad, Iraq"] describes the teaching unit as a set of integrated learning activities around a topic/problem and explicitly lists typical components (objectives, content, teaching methods, educational tools, activities, evaluation). citeturn4search48

This modern meaning is closer to Western “unit plan” usage than to the classical study-circle micro-unit described above.

### Western educational technology contrast: “learning object”

Modern Western edtech often uses “learning object” for reusable learning resources. The IEEE Learning Object Metadata standard defines a “learning object” very broadly as **any entity, digital or non-digital, used for learning, education, or training**. citeturn5search0turn5search2

This is not identical to “teaching unit,” but it’s a useful contrast: Western edtech terms often emphasize (a) packaging for reuse/discovery and (b) metadata schemas—both of which the KR pipeline is explicitly building.

### Stage 1 conclusion

- In **classical Islamic pedagogical practice**, the closest concept to the pipeline’s output is not “الوحدة التعليمية” as used in modern school curriculum design; it is closer to *a coherent, teachable chunk* that preserves the minimal context required for correct understanding—often aligned to the genre’s native atom (mas’alah / hadith item / bayt+rule+shawāhid) and to matn→commentary pairing practices. citeturn15view0turn15view3turn9view1
- In **modern Arabic pedagogy**, “الوحدة التعليمية” commonly implies a broader instructional package (multiple lessons + objectives/activities/assessment), which the KR pipeline does **not** literally produce. citeturn4search48
- A classical-adjacent Arabic label for “a self-contained extracted piece of text” would commonly be “مقتطف” (excerpt) in general Arabic lexicon usage. citeturn11search1  
  The problem is that “excerpt” / “مقتطف” carries a strong implication of *arbitrary snippet*, which conflicts with the pipeline’s intent to produce *self-contained teachable units*.

So semantically, “teaching unit” is *directionally aligned with the design intent* (self-contained, study-ready), but “الوحدة التعليمية” is *not a classical term of art* and may import modern curriculum connotations unless defined carefully.

## Collision risk between output “teaching unit” and the NTU field

Your protocol’s NTU field (“Natural Teaching Unit”) and the pipeline output concept are currently separable in logic but dangerously close in naming:

- **NTU (as defined)** = “the organic knowledge unit for this genre” (mas’alah in fiqh, etc.). This is a *type of unit* or *native boundary primitive*.
- **Output segment** = the *extracted instance* (what the pipeline produces: a concrete text span + metadata + self-containment evaluation).

If you call both of these “teaching unit,” you create a common ambiguity pattern:

- “What is the teaching unit?” could mean “What is the genre-native unit type?” or “What is the concrete extracted span?”
- In documentation and prompts, “make outputs match the teaching unit” becomes circular: do you mean “match the NTU primitive” or “construct one extracted unit”?

This ambiguity is not hypothetical: the repository already contains a `TeachingUnit` data model (Phase 2 grouping output) and an `ExcerptRecord` model (final output record) while prompts and spec text already foreground “teaching units.” That is already a duality; adding a second “teaching unit” label for NTU maximizes confusion.

### Is context enough to distinguish them?

Sometimes yes (e.g., a field label “Natural Teaching Unit” inside an expansion template is clearly meta), but in a system with:
- heavy prompt engineering,
- a SPEC that is meant to be the “authority,”
- and tooling and tests that reason about these items,

the cost of ambiguity is high. Your own collision scenario is a strong indicator: a reader can plausibly interpret NTU as “the thing we output,” because you intend outputs to align with natural units.

### Naming strategies that avoid collision

The cleanest way to avoid cognitive collision is to name the two concepts by their **ontological role**:

- **Unit Type / Boundary Primitive** (genre-native): what kind of “atom” exists in this genre?
- **Extracted Unit Instance / Record**: what did this system actually cut out?

Concrete proposals (ordered by clarity-to-change-cost ratio):

- **Keep output as “Teaching Unit” (TU)**, rename NTU field to **“Natural Unit Type” (NUT)** or **“Genre-Native Unit” (GNU/NGU)**.  
  This preserves the owner-favored term for the product while making the template field explicitly a *type*, not an instance.
- **Keep NTU as-is**, rename output to **“Extracted Teaching Unit” (ETU)**.  
  This is semantically accurate and keeps “teaching unit” in the product name, but adds a modifier that distinguishes instance vs type.
- **Keep “excerpt” internally, use “teaching unit” externally** (UI + owner docs), and reframe NTU as “Natural Teaching Unit” only in internal prompt templates.  
  This minimizes refactor but perpetuates the internal/external split.

Stage 2 conclusion: there is a **real and high-likelihood collision** if both concepts retain near-identical names, especially given the KR pipeline already contains both `TeachingUnit` and `ExcerptRecord` and uses “teaching unit” heavily in prompts and spec prose. The best fix is to rename *one* of the two concepts so that one reads as “unit type” and the other as “unit instance.”

## Pipeline implementation implications

### Blast radius of a system-wide term change

A strict “excerpt → teaching unit everywhere” refactor would touch:

- **Contracts / types**: `ExcerptRecord` (and likely fields like `excerpt_id`, `excerpt_topic`, etc.).
- **Docs**: `engines/excerpting/SPEC.md` uses “excerpt” heavily (you estimate ~200 occurrences) and already defines “teaching units” conceptually.
- **Prompts**: classification + grouping + enrichment prompts and examples; at least in `phase2_group.py` and `phase3_enrichment.py`, terms are mixed (“teaching units” is dominant, but “excerpt” still appears in at least one binding rule).
- **Test suite**: you report ~900 tests referencing “excerpt”.
- **Evaluation tooling**: `tools/evaluate_excerpts.py` is excerpt-schema-native (file names, expected JSONL names like `excerpts.jsonl`, field expectations keyed to `ExcerptRecord`, report headings “Structural Excerpt Report,” etc.).
- **Future owner-facing UI**: naming here is important because it anchors the student’s conceptual model of the library.

This is a large refactor by *string count*, but it is also **highly mechanical** if you keep the serialized schema stable during the first migration step.

### Is it “just a rename,” or does it change the conceptual model?

The answer depends on whether you change only identifiers or also change the semantics in prompts and invariants.

**Mechanically renaming identifiers (class names, docs, variable names)** does not change behavior, assuming:
- prompt content that drives segmentation behavior remains the same,
- the evaluation checks remain structurally identical (just renamed),
- and serialized field names remain backward-compatible.

However, in LLM-driven pipelines, **labels inside prompts are behavior-bearing**, so any rename that touches prompt instructions can change outputs.

Your codebase already demonstrates this: the grouping system prompt explicitly defines TEACHING UNITS and then applies self-containment criteria and decontextualization prevention. That means the system’s behavior is already “teaching unit–shaped,” not “arbitrary excerpt–shaped,” regardless of the `ExcerptRecord` type name.

The highest-risk behavioral change is not the Python rename; it’s prompt language changes like:
- removing “excerpt” as a negative constraint (“Mention is not excerpt…”),
- replacing it with “Mention is not a teaching unit…,”
- or changing how “unit” is framed (student-learning completeness vs simple extraction).

These are plausible behavior diffs:
- “Excerpt” framing can nudge the model toward **shorter spans** and more aggressive splitting.
- “Teaching unit” framing can nudge toward **more complete spans**, more context retention, and fewer “micro-excerpts,” because “teachability” implies closure.

Given your current prompts already emphasize “self-contained” teaching, the incremental behavioral delta from renaming is likely *moderate*, but it is not zero—especially because you have explicit heuristics tied to the word “excerpt” (e.g., “Mention is not excerpt”). That specific lexical cue is doing work; swapping it is an intervention.

### Implementation strategy to reduce risk

If you decide to adopt “teaching unit,” the lowest-risk migration is:

- **Step 1: Vocabulary alignment without schema break**
  - Rename internal types *at the Python level* (`ExcerptRecord` → `TeachingUnitRecord`) but keep JSON field names (`excerpt_id`, `excerpt_topic`, `excerpts.jsonl`) initially for backward compatibility (Pydantic aliases / `populate_by_name` patterns).
  - Update docs and prompts to use a unified conceptual framing (“teaching unit”) but avoid rewriting behavioral rules; treat prompt wording changes as a controlled experiment, not a global find/replace.
- **Step 2: Collision resolution**
  - Rename NTU to a type/primitive label (e.g., “Natural Unit Type”) in the protocol templates and docs.
- **Step 3: Schema v2 (optional)**
  - Only after you have stable evaluation baselines should you rename serialized fields/files to “unit_*” and `teaching_units.jsonl` if desired.

This makes the refactor mostly compile/test-driven and reduces the risk that a vocabulary decision silently changes extraction boundaries.

Stage 3 conclusion: the change is *mostly a rename-refactor* at the code/doc level, but it becomes a **conceptual model change** the moment prompt language is altered. The safe approach is to separate “naming migration” from “prompt semantics migration” and treat the latter as an evaluated change.

## Recommendation and decision matrix

### Options evaluated

**Option A — Adopt “teaching unit” system-wide with a rename refactor**

- Implementation effort (estimated): **10–18 hours**  
  Rationale: pervasive rename across contracts, docs, prompts, tests, and tooling; additional work needed to resolve the existing internal `TeachingUnit` vs output-record naming and the NTU collision cleanly. (If you also rename serialized schema keys and artifact filenames, add a second migration day.)
- Risk of behavioral regression: **Low–Moderate**  
  Low if prompts and schema semantics are kept stable during the rename. Moderate if you rewrite prompt text beyond superficial label swaps, because prompt lexemes can shift boundary selection behavior.
- Alignment with owner’s stated vision: **High**  
  Directly matches the owner’s consistent preference and the pipeline’s already teaching-unit-shaped intent.

**Option B — Keep “excerpt” internally but use “teaching unit” in owner-facing UI and documentation only**

- Implementation effort (estimated): **3–6 hours**
- Risk of behavioral regression: **Low**
- Alignment with owner’s stated vision: **Medium**  
  The owner still encounters “excerpt” in logs, schema, evaluation outputs, and internal docs unless you carefully partition what the owner sees. In a solo-owner project, “internal” vs “external” boundaries are porous.

**Option C — Adopt a different Arabic term that better captures the concept**

- Implementation effort (estimated): **6–12 hours**
- Risk of behavioral regression: **Low–Moderate** (depends on prompt edits)
- Alignment with owner’s stated vision: **Low–Medium**  
  This contradicts repeated explicit preference unless you treat it as a translation/display-layer adjustment only.  
  Substantive justification exists: “الوحدة التعليمية” is commonly a modern curriculum package (objectives/activities/assessment) rather than a single extracted passage. citeturn4search48

**Option D — Keep “excerpt” everywhere and document the owner’s preference as a future UI consideration**

- Implementation effort (estimated): **1–2 hours**
- Risk of behavioral regression: **Very low**
- Alignment with owner’s stated vision: **Low**  
  This preserves a persistent conceptual mismatch the owner has already flagged repeatedly.

### Single recommendation

**Choose Option A, but implement it as a two-layer vocabulary fix:**

- Adopt **“Teaching Unit” as the domain product name system-wide**, and rename the output record type to something like **`TeachingUnitRecord`** (so you keep a clear distinction from the existing Phase 2 `TeachingUnit` object).
- Rename the NTU concept to a **type/primitive name** (e.g., “Natural Unit Type” / “Genre-Native Unit”) so the template clearly asks for a *unit kind* rather than the *unit instance*.
- Treat **prompt wording changes as a controlled, evaluated change**: keep behavioral rules stable and only adjust “excerpt”-wording when you can A/B compare outputs.

This recommendation is justified because the pipeline’s extraction logic already operationalizes “teachability” (self-containment, decontextualization prevention, matn+commentary pairing) in a way that tracks classical Islamic teaching chunking more than arbitrary excerpting. citeturn15view0turn15view3turn9view1 The primary risk—semantic drift in LLM boundary selection—can be bounded by separating the rename from any substantive prompt rewrite.