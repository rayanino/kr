# Deep research on a synthetic adversarial data strategy for Arabic text-processing engines

## Repository context and threat alignment

KR’s pipeline (Source → Normalization → Excerpting → Taxonomy → Synthesis) is explicitly framed as a nightly “factory” whose job is to surface *pathological failures* that ordinary tests won’t catch. The draft decision D‑H010 (“Synthetic Adversarial Data Strategy”) sits inside that factory hardening decision log, and positions adversarial fixtures as a primary mechanism for exposing rare-but-catastrophic bugs. fileciteturn3file0L1-L1

The most valuable anchor for adversarial data design in this repo is the **Knowledge Integrity Protocol**, which defines seven corruption threats (T‑1…T‑7) and treats them as a *real scholarship* threat model (not hypothetical). fileciteturn15file0L1-L1 These threats create a clean “coverage contract” for adversarial data generation: if a generated (or mined) adversarial case doesn’t probe at least one corruption path, you can treat it as low priority.

In condensed terms (using the repo’s definitions), the threats adversarial data must directly target are: **silent text corruption** (T‑1), **attribution error** (T‑2), **taxonomic misplacement** (T‑3), **context loss / self-containment failure** (T‑4), **synthesis hallucination** (T‑5), **metadata poisoning** (T‑6), and **duplication/contradiction** (T‑7). fileciteturn15file0L1-L1

Finally, the excerpting engine is explicitly the “hardest” component and (by protocol) is implicated in mitigating self‑containment failures and excerpt‑level similarity/duplication detection. fileciteturn15file0L1-L1 The excerpting engine’s own spec is therefore the single best place to discover *which adversarial cases are likely to matter*, because it describes edge conditions and invariants the engine must honor. fileciteturn14file0L1-L1

## What has actually been built for adversarial Arabic NLP

Arabic adversarial NLP is smaller and more fragmented than English, but there is now a visible cluster of *implemented* approaches that map well to KR’s needs—especially at the Unicode/orthography/morphology layers.

### Adversarial methodologies demonstrated in Arabic research

A recent survey-style paper in **Scientific Reports** (2026) explicitly characterizes Arabic adversarial NLP as “limited” and identifies the core families that have been implemented: character substitution, synonym substitution, and diacritic manipulations—then adds a new method (“dialectal substitution”) as a black‑box token‑level attack. citeturn1search1turn3search3 This is important for KR because it shows the *field’s practical center of gravity*: real attacks are mostly **token/character perturbations that preserve human interpretability**, rather than fully synthetic longform generation. citeturn1search1turn3search3

Concrete implemented families and evidence:
- **Diacritic-based attacks**: A 2025 journal article proposes “diacritical manipulation” as a black‑box token‑level adversarial strategy that adds diacritics to non‑diacritized Arabic to degrade model performance. citeturn1search3turn1search4 A 2024 paper on robustness for Arabic AI-generated text detection also stresses that diacritics are widespread in Arabic religious texts and can change meaning, giving concrete examples of meaning shifts caused by diacritization. citeturn1search5
- **Synonym substitution attacks**: An EACL 2024 workshop paper introduces synonym (word‑level) adversarial examples for Arabic text classification using an MLM/BERT mechanism. citeturn0search15 Additionally, the 2026 Scientific Reports paper summarizes prior work that uses Arabic WordNet for black‑box substitution and also discusses stronger white‑box variants. citeturn3search3turn8search8
- **Dialectal substitution attacks (diglossia as adversarial shift)**: **entity["people","Basemah Alshemali","arabic nlp researcher"]**’s 2026 *Scientific Reports* article implements a token‑level attack that replaces key MSA tokens with dialectal equivalents via a dialectizer, demonstrating performance drops from minimal changes. citeturn1search1turn1search13 This matters for KR even though KR is classical rather than dialectal: it’s an existence proof that **distribution shifts inside Arabic varieties** are routinely used as adversarial tests in practice. citeturn1search1
- **Character-level “spelling mistake / visually-similar letter” attacks**: The same 2026 *Scientific Reports* paper summarizes prior Arabic work that builds black‑box character flips “spawned from common spelling mistakes” and uses visually similar letter substitutions, reporting substantial accuracy drops. citeturn3search3 The dot-centric nature of many Arabic letters is exactly why this class of attack is plausible and repeatedly studied. citeturn3search3turn3search0
- **Deletion / perturbation robustness studies**: A 2026 paper (as indexed) evaluates robustness of AraBERT models to black‑box deletions and perturbations, reinforcing that Arabic robustness work often uses simple edit operations (delete/insert/modify) that preserve gross readability but break tokenization/embeddings. citeturn3search5

### Tooling that exists (not Arabic-only, but used for multilingual attack generation)

Arabic does not yet have a single “canonical” adversarial toolkit the way English does, but several mature NLP adversarial toolkits are directly usable for Arabic if you provide Arabic-specific transformations and constraints:
- **entity["organization","TextAttack","nlp adversarial toolkit"]** is a modular framework for adversarial attacks and augmentation, designed to compose transformations/constraints/search methods; it is widely cited and implemented as an extensible toolkit rather than a single attack. citeturn5search2turn0search18
- **entity["organization","OpenAttack","text adversarial attack toolkit"]** is an open-source textual adversarial attack toolkit with a multi-attack architecture and evaluation components; it is explicitly designed for extensibility and integration with model wrappers. citeturn0search5turn0search6turn0search2
- **entity["organization","CheckList","behavioral testing methodology"]** is not an “attack generator” per se; it is a behavioral testing methodology and tool for rapidly generating large test suites that expose bugs even in heavily tested NLP systems. Its premise—capability matrices + templated test generation—maps unusually well onto KR’s factory goals. citeturn5search4turn5search0

For KR, these toolkits are best treated as *frameworks* into which you plug Arabic-specific transforms (diacritics, joiners, Arabic-Persian letter variants, matn/sharh boundary markers, etc.), rather than as ready-made Arabic solutions. citeturn5search2turn0search5turn5search4

### Arabic resources that support adversarial generation

Several concrete Arabic linguistic resources exist that can drive controlled perturbations:
- **entity["organization","CAMeL Tools","arabic nlp toolkit"]** includes a documented morphological **generator** capable of producing surface forms from a lemma plus feature bundles. This is directly useful for *morphological adversarial examples* (controlled inflection changes, cliticization variants, etc.). citeturn1search0turn1search2
- **Arabic WordNet** is available through the Open Multilingual Wordnet project, listing Arabic WordNet v2 with a CC BY-SA license; this is a practical resource for synonym substitution attacks that have already been used in Arabic robustness research. citeturn8search2turn8search8
- A newly announced **Arabic WordNet 4.0** (Jan 2026) claims much larger scale and CC BY 4.0 licensing, distributed via GitHub/Zenodo, which could materially improve synonym-attack coverage if the resource quality holds up. citeturn8search3

## Arabic-specific attack surfaces relevant to KR’s engines

Your prompt lists several Arabic-adjacent adversarial surfaces (Unicode, diacritics, BiDi, OCR noise, classical-vs-modern ambiguity). The key point—validated by both the Unicode security ecosystem and Arabic adversarial NLP literature—is that many high-impact adversarial cases are **not semantic paraphrases**; they are *encoding- and orthography-level perturbations* that exploit how Arabic is written and rendered. citeturn3search3turn6search0turn2search2

### Unicode and BiDi control attacks (Arabic-heavy risk)

The Unicode Bidirectional Algorithm explicitly defines directional formatting characters (e.g., RLO U+202E, PDF U+202C, isolates U+2066..U+2069) and warns that reordering affects display rather than logical order. citeturn6search0turn6search1 The **Trojan Source** vulnerability class (tracked as CVE‑2021‑42574) documents how attackers can embed bidirectional control sequences to make displayed token order diverge from logical order, and references the Unicode Consortium’s mitigation guidance (UTS #39, UAX #9 HL4, etc.). citeturn7search0turn7search11

Why this matters for KR specifically:
- Your pipeline processes Arabic (RTL) plus embedded digits, citations, and possibly Latin transliterations—exactly the mixed-direction environment the UBA is designed for. citeturn6search0
- Even when the “Trojan Source” narrative is framed around source code, the underlying attack primitive is **text display vs text bytes**. Excerpting, normalization diffs, review UIs, and LLM prompts can all be affected when adversarial authors embed Bidi controls inside Arabic text (or inside metadata fields). citeturn7search0turn5search15
- There are production-oriented detectors that *specifically* scan for Trojan Source/Bidi control spans (for example, a “Trojan Source detection” module in a prompt-security library), indicating that this is not purely theoretical. citeturn5search15

### Confusables and mixed-script spoofing tailored to Arabic

Unicode’s security standard UTS #39 provides a formal mechanism (and data files like confusables.txt) for detecting visually confusable strings and mixed-script confusables—explicitly meant for security problems caused by Unicode’s large character inventory. citeturn2search2turn2search3 For Arabic processing, this maps directly onto real-world spoofing patterns like:
- Arabic vs Persian code points for “same-looking” letters (e.g., Arabic Yeh vs Farsi Yeh, Arabic Kaf vs Keheh) in corpora that mix Arabic/Persian content.
- Arabic-Indic digits vs European digits (relevant to isnād numbering, page/volume notation, and SHamela-style metadata).
- Presentation forms and compatibility characters.

The key here is that UTS #39 doesn’t just describe risks; it provides concrete detection mechanisms and reference data. citeturn2search2turn2search3

### Diacritics, orthography, and morphology as adversarial levers

Arabic diacritics (tashkīl) are a repeatedly validated robustness weakness: diacritic insertion/manipulation is published as a black-box adversarial strategy in Arabic NLP (2025), and diacritics are also repeatedly cited as meaning-changing and common in religious texts. citeturn1search3turn1search5turn1search1

For KR, diacritics are not only an “NLP model robustness” issue; they map directly to **T‑1 (silent text corruption)** because tiny arabic mark changes can invert meaning (the repo explicitly gives a diacritic-based meaning inversion example). fileciteturn15file0L1-L1

Morphology and cliticization are also explicitly raised in the Arabic adversarial literature as an axis of vulnerability (“agglutinative nature,” “several morphemes per word”), and you have practical tooling to exploit that axis via a morphological generator. citeturn1search1turn1search0

### OCR error patterns and “noisy Arabic” data that actually exists

Arabic OCR noise is unusually relevant to KR because:
- Shamela-like corpora often contain digitization artifacts, and OCR noise is a standard vector in Arabic text corruption threat models. fileciteturn15file0L1-L1
- Arabic OCR error correction is an established research topic (e.g., EMNLP 2006 work on Arabic OCR error correction using character segment correction + language models + shallow morphology). citeturn4search5
- There are now large OCR corpora and pipelines for Arabic books:
  - **entity["organization","Qatar National Library","doha, qatar"]** released an “Arabic OCR Corpus v2” consisting of ~2,894 OCR text files derived from digitized printed works, with metadata and checksums. citeturn4search3turn4search0
  - The **KITAB/OpenITI** ecosystem describes an OCR pipeline based on Kraken and eScriptorium, explicitly noting that OCR output still requires manual post-correction and that pipeline versions/models are documented via metadata. citeturn4search2

In addition to OCR-specific sources, there is a deep ecosystem of Arabic error corpora and synthetic “noising” methods from grammatical-/spelling-error correction work:
- The QALB shared task corpus documents error type taxonomies (including morphology edits) and supports building realistic noise models. citeturn3search6turn3search8
- A large-scale synthetic noising method for Arabic GEC is described in a 2022 paper (ScienceDirect index), generating extremely large synthetic error datasets and explicitly listing error-type generation procedures. citeturn3search10
- An Applied Sciences review notes the existence of a massive synthetic spelling-error dataset (SPIRAL) derived from newspapers and open Arabic corpora including Maktabah Shamela, describing multiple generated error types (including “Tachkil errors”). citeturn4search6

Even if these resources are not “Shamela Islamic classical” in genre, they are operationally important because they provide *implemented noise models* and *empirical error distributions* you can adapt. citeturn3search10turn4search6

## Is Layer 3 LLM-generated fixture books feasible, or should KR mine its corpus?

D‑H010’s Layer 3 (“Codex/Gemini generates adversarial fixture books”) is *directionally* aligned with modern test generation trends, but the particular target you describe—**realistic classical Arabic scholarly prose with precise adversarial semantics** (e.g., “refutation that looks like endorsement,” ambiguous sharḥ/matn boundaries)—is a much harder generation/control problem than typical adversarial NLP examples, which are usually token-level perturbations rather than longform discourse engineering. fileciteturn3file0L1-L1 citeturn3search3turn5search4

### What the evidence suggests about feasibility

Most published Arabic adversarial methods that *actually work* are:
- black-box,
- local (character/token edits),
- constrained to preserve readability/meaning,
- and evaluated as small perturbations over real data. citeturn1search1turn0search15turn1search3

That empirical pattern strongly suggests that LLM-generated *full* “fixture books” are not the **highest-leverage** first move, because they concentrate risk in two places:
1. **Distribution mismatch risk**: synthetic longform may not exercise the same formatting conventions, citation styles, and “Shamela idiosyncrasies” that the excerpting engine will face nightly.
2. **Specification-control risk**: even if an LLM can output plausible classical Arabic, reliably embedding *exact* adversarial properties (in a way that triggers your targeted failure mode without adding confounders) is non-trivial—and requires extensive scaffolding and post-hoc verification.

The strongest evidence-based alternative is to treat LLM generation as **secondary scaffolding**, and prioritize:
- **Corpus mining for natural adversarial cases**, plus
- **mutation-based adversarial generation** that starts from real corpus spans and applies controlled transforms drawn from known Arabic adversarial families (diacritics, confusables, joiners, OCR-like noise, synonym substitution using Arabic WordNet, etc.). citeturn5search4turn3search3turn2search2

This is not “anti‑LLM.” It is consistent with how adversarial testing toolkits and behavioral methods are typically used: start with real examples and expand coverage via templating/transformation rather than relying on unconstrained longform generation. citeturn5search4turn5search2turn0search5

### A more defensible Layer 3 framing

A more evidence-backed Layer 3 would be:

**Layer 3 (reframed): “LLM-assisted adversarial fixture synthesis over mined seeds.”**  
Instead of “generate books,” use LLMs to:
- **select** candidate spans (from Shamela corpus mining) likely to stress excerpting boundaries,
- **rewrite locally** (paragraph-scale) under tight constraints,
- **label** expected outcomes (e.g., “this paragraph is a refutation; expected stance=reject”),
- and then **verify** against a second model/provider (which your repo already treats as the correct safety pattern for content decisions). fileciteturn15file0L1-L1

This delivers two advantages:
- You stay grounded in real formatting/rhetorical distributions.
- You keep the unit of control small enough that verification and “adversarial property satisfaction” is feasible.

## What’s missing from D‑H010, and concrete ways to strengthen it

D‑H010 is already pointed in a strong direction (multi-layer adversarial strategy integrated into a nightly factory), but the draft—as you flagged—has gaps that are likely to matter for a classical Arabic pipeline and for LLM-facing stages. fileciteturn3file0L1-L1

### Missing LLM-facing adversarial prompts and prompt-in-text threats

KR’s excerpting/taxonomy/synthesis phases are LLM-mediated (at least in part), so adversarial data must include *prompt-level attack* fixtures, not only text-level linguistic pathologies. T‑5 (synthesis hallucination) is explicitly an LLM failure mode in your threat model, and the protocol already treats cross-provider verification as a required mitigation pattern. fileciteturn15file0L1-L1

What an “LLM-facing adversarial fixture” library should include (evidence-backed primitives):
- **Prompt injection embedded in Arabic text**: E.g., Arabic instructions that try to override the system prompt (“تجاهل التعليمات السابقة…”) and cause the model to emit malformed JSON or omit required fields. This is a known class of LLM failure even outside Arabic; for Arabic, the *embedding inside RTL script* plus mixed punctuation increases parsing fragility. (The need to consider prompts/templates is explicitly raised in Trojan Source prompt-security guidance.) citeturn5search15
- **Trojan Source / BiDi injection in prompt-visible text**: Bidirectional control characters can reorder display without changing logical order (Unicode UAX #9) and are a documented vulnerability class (CVE‑2021‑42574). This means a malicious string could *look* like harmless Arabic prose in a review UI, but contain hidden instruction fragments when interpreted. citeturn6search0turn7search0turn5search15
- **Refusal triggers and safety boundary stressors**: Because your corpus includes religious/legal content, you want fixtures that induce: refusal cascades, over-cautious filtering, or “safe completion” drift that drops required extraction outputs. (Even without a single canonical dataset, prompt‑security libraries now treat these as first-class threats precisely because they are operationally common.) citeturn5search15

The key D‑H010 enhancement is not “add jailbreaks” in the abstract; it’s adding a **prompt attack taxonomy mapped to T‑threats** (especially T‑2/T‑5/T‑6) so the LLM-mediated engines can be hardened with regression fixtures. fileciteturn15file0L1-L1

### Missing scale targets and coverage metrics

D‑H010 describes layers, but “how many fixtures is enough?” is not only a planning question—it’s essential for avoiding false confidence.

A defensible metric system (grounded in adversarial testing practice) would combine:
- **Risk-weighted coverage matrix**: (Threat T‑1…T‑7) × (Engine boundary) × (Attack family). This mirrors CheckList’s “capability matrix + test types” methodology. citeturn5search4turn5search0
- **Adversarial family saturation metrics**: Track unique “edit families” and parameter ranges covered (e.g., for diacritics: insertion/removal at different positions; for BiDi: well-formed vs unterminated overrides; for confusables: same-script vs mixed-script confusables per UTS #39). citeturn1search3turn2search2turn6search0
- **Differential failure yield**: A factory KPI that measures “bugs per N new adversarial fixtures” and decays over time. When yield collapses for a family, you either expand the family’s parameter space or reallocate to higher-yield families.

If you want an initial scale target that is *operationally plausible* (without pretending there is a universal number), the literature suggests that templated generation can rapidly create “large and diverse” suites, and that even mature systems continue to yield bugs under behavioral test generation. citeturn5search0turn5search4 In KR terms, that favors **many small fixtures** (span/section-level) over a few huge synthetic books, because the objective is failure discovery rate, not literary realism.

### Missing “real Shamela adversarial” grounding

You asked for real-world adversarial examples from Shamela itself. I cannot extract or quote your local 2,519-book corpus from here, but there is strong external evidence that:
- “Shamela” (as a corpus source) is already used in error/noise dataset construction (SPIRAL is described as being derived from open corpora including Maktabah Shamela). citeturn4search6
- OCR pipelines and Arabic book OCR corpora are readily available at scale (QNL OCR corpus; KITAB OCR pipeline), reinforcing that book-like Arabic text has systematic noise modes that can be modeled and injected. citeturn4search3turn4search2

So, the missing piece in D‑H010 should be a **“mined-fixture lane”** with explicit targets:
- Collect naturally occurring cases that are already likely to break excerpting (multi-layer sharḥ/matn, dense quotation chains, editorial brackets, marginalia/footnote structures, isnād chains, poetry blocks, and “قلت/قال” discourse shifts).
- Store them as gold fixtures tagged by which T‑threat they probe.
- Use LLMs only to *label* and *cluster* mined cases (and to propose minimal edits), not to fabricate full books.

This aligns with the core experimental design in Arabic adversarial papers, which typically start from real corpora and apply controlled substitutions/edits. citeturn1search1turn0search15turn3search3

### Missing Arabic-specific tooling inventory inside the draft

D‑H010 would be stronger if it explicitly named the Arabic-specific resources that can be operationalized, because those resources determine what kinds of adversarial transforms you can implement reliably:
- Morphology generation via CAMeL Tools (for systematic inflection/cliticization adversaries). citeturn1search0
- Arabic WordNet resources (OMW Arabic WordNet v2; Arabic WordNet 4.0 announcement) for synonym-based adversarial substitutions. citeturn8search2turn8search3
- Unicode security guidance (UAX #9; UTS #39) and concrete vulnerability artifacts (CVE‑2021‑42574) for BiDi/confusable attacks. citeturn6search0turn2search2turn7search0
- OCR corpora and OCR pipelines for realistic OCR-noise modeling (QNL Arabic OCR Corpus; KITAB Kraken-based OCR pipeline; historical OCR correction research). citeturn4search3turn4search2turn4search5

## A concrete adversarial strategy blueprint for KR’s nightly factory

This section translates “what exists” + “what the repo needs” into a strategy that directly challenges the weak points of “LLM generates fixture books,” while still keeping the spirit of D‑H010’s layered approach. fileciteturn3file0L1-L1

### A threat-indexed adversarial family library

Build a library of adversarial transforms and mined seeds, each tagged with:
- target engine(s),
- target threat(s) T‑1…T‑7,
- expected invariants (e.g., “primary text must not change” for T‑1 defenses). fileciteturn15file0L1-L1

Prioritize families with strong external evidence of impact in Arabic:
- **Diacritics family (T‑1 + excerpting fragility)**: insertion/removal, shadda/sukun perturbations, tanwīn confusion, “legitimate vs arbitrary” diacritics. citeturn1search3turn1search5
- **Dot/letter-shape confusions (T‑1 + tokenization errors)**: exploit letter-dot identity (ب/ت/ث, ج/ح/خ, ن/ي) and mimic “non-native spelling mistakes,” consistent with published Arabic character-level attacks. citeturn3search3turn3search0
- **Unicode BiDi/control (T‑1 + UI/prompt integrity)**: embed RLO/PDF/isolate sequences, including malformed sequences (unterminated) and mixing with digits/Latin. citeturn6search0turn7search0turn5search15
- **Confusables / mixed-script (T‑1 + T‑6)**: Arabic/Persian variants, numerals variants, characters whose visual form collides; drive detection/normalization decisions using UTS #39 mappings. citeturn2search2
- **OCR-noise family (T‑1)**: generate OCR-like errors informed by book OCR corpora and OCR correction literature; validate against real OCR corpora when possible. citeturn4search3turn4search5turn3search10
- **Synonym/dialect/morphology families (T‑3 + T‑4 + T‑2)**: substitute synonyms using Arabic WordNet; morphologically re-inflect key tokens using a generator; optionally apply dialectal substitutions as “variety shift” tests even if not your primary domain. citeturn8search2turn1search0turn1search1

### Replace “fixture books” with “seed mining + constrained synthesis + verification”

A practical process that is more likely to work than unconstrained longform generation:

1. **Mine seeds from the 2,519-book corpus**  
   Identify and store spans likely to trigger excerpting ambiguity (matn/sharḥ boundaries, nested quotation scaffolds, “قال/قلت” discourse shifts, “فائدة/تنبيه” sections, heavy isnād lists). This directly targets excerpting complexity described in your spec and the protocol’s self-containment requirements. fileciteturn14file0L1-L1 fileciteturn15file0L1-L1

2. **Apply deterministic Arabic transforms**  
   Use the evidence-backed adversarial families above (diacritics, BiDi, confusables, OCR-like noise, morphology). These are precisely the perturbations repeatedly used to evaluate Arabic robustness in the literature. citeturn1search3turn3search3turn7search0turn4search5

3. **Use LLMs for constrained local rewrites and labeling**  
   Have one model generate a *minimal rewrite* that embeds a specific adversarial semantic property (“refutation looks like endorsement”) and require a second provider/model to verify that the property holds—matching the repo’s cross-provider verification principle. fileciteturn15file0L1-L1

4. **Run differential checks and metamorphic invariants**  
   Many failures won’t be “wrong answer”; they’ll be *invariant breaks* across pipeline boundaries (metadata drop, excerpt self-containment drift, primary_text mutation). Those are exactly the “fail loudly” integrity rules in the protocol. fileciteturn15file0L1-L1

### How many fixtures, and when is “enough”?

A defensible stopping rule is not a fixed number; it is a combination of:
- coverage completeness of the threat×engine×family matrix (modeled after behavioral testing matrices), and citeturn5search4turn5search0
- a diminishing-returns curve in bug yield per marginal fixture in each family.

D‑H010 can become operationally stronger by adopting these measurable gates rather than relying on qualitative notions that the fixture library is “large.” fileciteturn3file0L1-L1