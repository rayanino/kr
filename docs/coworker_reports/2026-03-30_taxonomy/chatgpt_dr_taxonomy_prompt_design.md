# Designing Arabic LLM Prompts for Scholarly Taxonomy Classification

## Repository-grounded constraints and failure modes

The taxonomy engine in `rayanino/kr` is designed to take Arabic Islamic scholarly excerpts (roughly 200–2000 words), and place each excerpt at a single leaf node in a hierarchical “science tree,” with routing logic determining whether a placement is accepted as “live” or held for review (“staged”). fileciteturn3file0L1-L1 The system uses a two-stage LLM pipeline: a branch-selection stage used only for large trees, followed by a leaf-ranking stage that assigns a 0.0–1.0 fit score to candidate leaves. fileciteturn3file0L1-L1

Three properties of your taxonomy files matter directly for prompt design:

First, the trees are Arabic-labeled but have stable ASCII IDs and full leaf paths, and they encode “overview” leaves via the `__overview` suffix (e.g., `huruf_aljar__overview`). fileciteturn5file0L1-L1 Second, the trees include policies that imply single-label classification (“single_core_node_per_excerpt”) and atomic leaves (“leaf_atomic”), meaning the prompts should not encourage multi-leaf outputs or “mixtures.” fileciteturn5file0L1-L1 Third, you have multiple tree formats in play: `nahw` and `balagha` use a v1 taxonomy schema, while `aqidah` is explicitly a v0.x schema with `_label` / `_leaf` keys; this increases the importance of presenting *normalized* candidate representations (path + title) to the LLM rather than raw YAML structures. fileciteturn5file0L1-L1 fileciteturn7file0L1-L1

Your gold fixtures and smoke excerpts show two high-leverage error patterns that prompt design must directly counter:

- **Lexical trap / polyfunctionality:** the same Arabic term appears in multiple branches with different grammatical functions (e.g., **كي** as *حرف جر* vs. **كي** as a *ناصب للمضارع*). In `nahw/tree.yaml`, **كي** exists under `alaf3al/nawasiib_almudari3/kay`, while the “meanings of prepositions” leaf is `almajrurat/huruf_aljar/ma3ani_huruf_aljar`. fileciteturn5file0L1-L1 The excerpt dataset includes a passage explicitly framed as “كي حرف جر” with an Arabic description explaining the prepositional readings. fileciteturn8file0L1-L1 The gold baseline flags this as adversarial and documents the “wrong but tempting” leaf (`alaf3al/nawasiib_almudari3/kay`). fileciteturn9file0L1-L1
- **Topic-focus vs. formal classification collisions:** an excerpt can mention items that are technically in one category, while the scholarly focus is another. Your gold baseline assigns the “واو القسم / تاء القسم” excerpt to `asaleeb_wamushaqaqat/alqasam` (oath style) rather than to the prepositions branch, noting that it is a hard case because واو/تاء can be treated as prepositions in some grammatical framings. fileciteturn9file0L1-L1

These fixtures imply a prompt strategy that (a) forces function- and discourse-focus-based decisions rather than keyword matching, and (b) teaches “overview vs. specific leaf” usage as a first-class rule, since your trees intentionally co-locate overview leaves with fine-grained ones (e.g., `huruf_aljar__overview` vs. `ma3ani_huruf_aljar` vs. `zawaid_huruf_aljar`). fileciteturn5file0L1-L1 fileciteturn9file0L1-L1

## Prompt language choice for Arabic classification

You have an inherent language asymmetry: the *data* (excerpt text, headings, topics, descriptions, labels) is Arabic, but the *instruction-following substrate* of many frontier LLMs is often strongest in English. Recent multilingual prompting research suggests there is no universal answer; optimal “prompt language” depends on model, task type, and the prompt components being translated vs. kept in the original language. citeturn1search4

Two empirical strands are most relevant:

- **“English instructions can be sufficient” for multilingual understanding tasks.** A recent study on multilingual transcript understanding found English prompts often achieved performance comparable to native-language prompts across languages and tasks, implying that instructions can remain English while content stays in the target language (depending on language and task). citeturn1search5  
- **“Prompt language can materially change outcomes,” sometimes favoring non-English prompts.** Work on crosslingual metalinguistic QA shows prompting language can significantly affect performance, and that prompts in a different language can sometimes outperform English even when the *content* is English—evidence that the relationship is not simply “English always best.” citeturn1search11

For Arabic specifically, benchmark work consistently shows that Arabic evaluation surfaces gaps (especially in deeper linguistic competence), and that performance varies substantially across models and settings. citeturn12search13 citeturn13view0 This matters because your task is *linguistically grounded* (e.g., nahw function distinctions), not just topical similarity; Arabic linguistic benchmarks explicitly highlight that models can look competent on surface tasks while being weaker on grammar/syntax reasoning. citeturn12search12

**Recommendation (mixed language, with strict role separation):**

- Keep **all taxonomy labels, excerpts, and evidence snippets in Arabic** (never translate). This prevents the model from “solving the wrong task” by translating label semantics and drifting. It also ensures disambiguation uses Arabic function cues like “حرف جر” vs. “ناصب” rather than English glosses. fileciteturn8file0L1-L1 fileciteturn5file0L1-L1
- Write **instructions and scoring mechanics in English**, but inject **Arabic “decision triggers”** for core disambiguations (e.g., “جر/مجرور/حروف الجر” vs. “نصب/المضارع/أنْ مضمرة”). This follows the “selective pre-translation” framing: translate the *instruction layer* while keeping the *content layer* Arabic. citeturn1search4
- Require **Arabic citations as extracted evidence** (short phrases copied from the excerpt metadata/text), but keep the “why” explanation minimal and structured; this improves auditability without relying on long free-form reasoning. Evidence-first prompting is consistent with structured prompting practices in production pipelines, and helps reduce ungrounded keyword matches. citeturn2search3

This mixed strategy is not a guarantee for every model, but it is the most robust default given (1) multilingual prompting findings that instruction language can be separated from content language, and (2) your need to preserve Arabic functional distinctions that are often lost under translation. citeturn1search4 citeturn1search5 citeturn12search12

## Presenting the taxonomy tree to the model

Your prompt needs to help an LLM reason over *hundreds* of mutually confusable classes, while remaining within context limits and avoiding “lost in the middle” effects. The long-context literature shows that model performance can degrade when relevant information is in the middle of a long context rather than near the beginning or end, even for models designed for long contexts. citeturn0search4 That is directly applicable to “score 129 leaves in one list,” where the correct leaf might land in the middle of a large candidate block.

Separately, hierarchical text classification work that leverages LLMs emphasizes that **category names alone can be ambiguous**, and that enriching labels with additional information (prototypes, descriptors, class-indicative terms) improves results. citeturn6view0 citeturn11view0 Your trees already include relatively descriptive Arabic titles (often longer than mere names), but ambiguity remains (e.g., overlapping rhetorical/nahw terms; overview vs specific nodes; polyfunctional particles). fileciteturn5file0L1-L1

Given your options (indented text, flat list with paths, Markdown table, JSON), the key tradeoff is: **hierarchy visibility vs. cognitive load and token mass**.

- **Indented tree text (YAML-like):** maximizes hierarchical context, but is token-heavy and can cause attention diffusion across nested levels. It also makes it harder to reference a candidate unambiguously in output unless you add stable IDs anyway. This format is best for humans, not necessarily for “choose one leaf” scoring at scale. (Inference grounded in long-context degradation findings.) citeturn0search4
- **JSON structure:** structurally explicit but extremely verbose, especially for 300+ leaves; it tends to spend tokens on braces and nesting rather than discriminating information. It also encourages the model to “analyze the tree” rather than “classify the excerpt,” raising cost and error risk. TELEClass explicitly notes that including a large, structured label space in a prompt is ineffective for hierarchical classification, motivating selective presentation and enrichment instead. citeturn11view0
- **Markdown table:** can be readable, but tables often add delimiter noise (pipes, alignment) and can be brittle under some model formatting behaviors. They’re best used when the table is compact and columns are essential. Evidence for structured output reliability is stronger on the *output* side than the *input* side, but it supports keeping representations regular and schema-like. citeturn2search3
- **Numbered flat list with full path + Arabic title (+ optional parent title):** the best balance for LLM classification because it (a) provides a stable reference key (`leaf_path`), (b) keeps each candidate to one line, (c) can be chunked and regrouped easily, and (d) supports explicit “choose among these” behavior.

**Recommendation (two different “views,” tuned to each stage):**

Stage 1 (branch selection) should see **only the top-level branches** (and, optionally, a *very small* teaser of what’s inside each branch). In `nahw/tree.yaml`, the top level includes branches like `almajrurat` (المجرورات), `alaf3al` (مباحث الفعل), and `asaleeb_wamushaqaqat` (أساليب ومسائل جامعة), which are exactly the units Stage 1 should choose among. fileciteturn5file0L1-L1

Stage 2 (leaf ranking) should see a **flat candidate list**, each entry containing:

- `leaf_path` (full path from root branch IDs)
- `leaf_title_ar` (Arabic title)
- `parent_title_ar` (one level up, to reintroduce local hierarchy without full nesting)

Your current system already stores/uses paths like `almajrurat/huruf_aljar/ma3ani_huruf_aljar` in fixtures, which is exactly the right “handle” to put in the prompt. fileciteturn9file0L1-L1

If you adopt label enrichment (recommended for the hardest branches), add **one short descriptor line per leaf** (Arabic, ≤12–15 words) generated offline and version-controlled alongside the tree. This mirrors the “taxonomy enrichment” direction in hierarchical classification research: enrich labels with class-indicative cues rather than dumping full structures into prompts. citeturn11view0 citeturn6view0

## Disambiguation for polyfunctional Arabic terms

Your **كي** case is a canonical “polyfunctionality” trap: the same surface form labels different functions in different branches. The excerpt text and metadata explicitly frame “كي” as a preposition: `"فأما كي فتكون حرف جر في موضعين..."` and the description reiterates “كون «كي» حرف جر”. fileciteturn8file0L1-L1 The gold baseline uses this to assert the correct leaf is `almajrurat/huruf_aljar/ma3ani_huruf_aljar`, and explicitly records `alaf3al/nawasiib_almudari3/kay` as the adversarial wrong choice. fileciteturn9file0L1-L1

A prompt that merely says “pick the best label” will often fail here because **keyword overlap dominates** unless you force functional grounding.

**Prompt instruction to add (general pattern, not كي-specific):**

- Treat every candidate leaf title as a *claim about function and scope*, not a bag of keywords.
- Use metadata fields (`excerpt_topic`, `description_arabic`, `div_path`, and any function tags) as *explicit disambiguation evidence*; in your dataset these fields are rich and often already encode the intended functional frame (e.g., “كي حرف جر”). fileciteturn8file0L1-L1
- Require the model to extract 1–3 short Arabic “evidence phrases” that justify the function (e.g., “حرف جر”, “مجرورة بكى”, “معاني مِن”, “مِن الزائدة”, “ينصب المضارع”). If it can’t produce evidence, cap the score.

This approach aligns with the broader finding in hierarchical classification research that label names alone are often imprecise and ambiguity requires contextual enrichment. citeturn6view0

**Concrete disambiguation rule for particles shared across branches:**

- If the excerpt frames the particle with **جر/مجرور/حروف الجر/معاني الحروف/زيادة الحروف** language, treat it as a preposition/`almajrurat` topic. Your nahw tree explicitly separates “meanings of prepositions” from “extra/redundant prepositions” leaves (`ma3ani_huruf_aljar` vs `zawaid_huruf_aljar`), and your gold fixtures show both patterns in real excerpts. fileciteturn5file0L1-L1 fileciteturn9file0L1-L1  
- If the excerpt frames the particle with **نصب/ناصب/المضارع/إضمار أن/نواصب المضارع** language, treat it under `alaf3al/nawasiib_almudari3/...` (including `.../kay`). fileciteturn5file0L1-L1

Finally, ensure the prompt includes a “focus override” rule for cases like oath particles: even if an item appears in a list of prepositions, an excerpt whose *core discussion* is the mechanics and restrictions of oath usage should route to the `القسم` leaf (as your gold baseline does). fileciteturn9file0L1-L1

## Controlling overview versus specific leaf bias

Your trees intentionally contain “overview” leaves, and the gold baseline demonstrates that overview is *sometimes* correct even when a more specific leaf exists. For example:

- Excerpt 0 enumerates the 20 prepositions and their general properties; gold assigns `huruf_aljar__overview`. fileciteturn8file0L1-L1 fileciteturn9file0L1-L1  
- Excerpt 11 is explicitly about “مِن الزائدة / شروط زيادة مِن”; gold assigns `zawaid_huruf_aljar` (not overview). fileciteturn9file0L1-L1  
- Excerpt 1 is about “كي حرف جر”; gold assigns `ma3ani_huruf_aljar` (specific meanings-by-preposition leaf). fileciteturn9file0L1-L1

So you need a prompt rule that prefers specificity *only when the excerpt itself is specific*.

**Recommendation: encode a two-step specificity test in the prompt**

1) **Specificity detection (about the excerpt):** ask the model to classify the excerpt as one of:
- “Single concept focus” (one particle / one rhetorical device / one rule family)
- “Small set focus” (2–5 closely related particles/rules, still coherent)
- “General overview / survey / enumeration / cross-reference / editorial”

You already have strong hints for this in the excerpt metadata: `primary_function` and `content_types` distinguish rule statements vs. cross references, and your gold baseline calls out a cross_reference excerpt as “closest match is overview.” fileciteturn9file0L1-L1

2) **Leaf selection policy (about the tree):**
- If “single concept focus” && a corresponding specific leaf exists, penalize overview leaves (cap overview at 0.6 unless the leaf is truly a “single concept overview” node).
- If “general overview” or “cross-reference,” prefer overview leaves, and cap specific leaves (e.g., 0.4) unless the excerpt repeatedly develops a single subtopic in depth.

This is consistent with “decision principles” style prompts used in fine-grained classification frameworks: injecting boundary constraints and decision rules helps zero-shot classification in specialized domains. citeturn0search0

## Scaling and score calibration for large candidate sets

### Managing the 129-leaf branch problem

`balagha/tree.yaml` contains a very large `3ilm_alma3ani` branch (علم المعاني), and the entire balagha tree is 335+ leaves. fileciteturn6file0L1-L1 Your research question is whether Stage 2 can reliably score 129 options in one pass, and what the upper limit is.

The strongest evidence available is indirect but highly relevant:

- Long-context work shows models are not uniformly sensitive across long inputs; performance can drop when pertinent information is in the middle of the context. A 129-item candidate list is exactly the kind of structure where many items land “in the middle.” citeturn0search4
- TELEClass explicitly argues that straightforward zero-shot prompting “performs poorly in the hierarchical setting” because it is ineffective to include a large structured label space in a prompt—pointing toward *hierarchical narrowing and enrichment* rather than “show all labels.” citeturn11view0
- Empirical prompting studies show that increasing prompt complexity can degrade performance, but the degradation pattern depends on model architecture and task; this supports treating “129-way scoring in one pass” as a model-dependent risk rather than a safe default. citeturn4search0

**Practical recommendation:** treat ~50–80 candidate leaves as the *default safe ceiling* for single-pass scoring, and add a narrowing step for any branch whose candidate set exceeds that ceiling. (This ceiling is a judgment call informed by long-context robustness concerns, not a hard fact.) citeturn0search4

Concretely, add **Stage 1.5 (sub-branch selection)** when Stage 1 selects a very large branch such as `3ilm_alma3ani`:

- Input: excerpt metadata + list of **immediate children** under `3ilm_alma3ani` (e.g., `alinsha`, `alkhabar`, `alqasr`, etc.) with short Arabic titles and 2–4 example leaves per child. fileciteturn6file0L1-L1
- Output: 1–3 sub-branches.
- Stage 2: score only leaves under selected sub-branches.

This mirrors the consistent theme in hierarchical classification research: use the hierarchy to reduce the effective label space, and enrich the remaining candidates. citeturn6view0 citeturn11view0

If you cannot add a Stage 1.5 for architectural reasons, the next-best option is a **two-pass tournament** within Stage 2:

- Pass A: group leaves by parent; ask the model to pick top 1–2 leaves per group (or top 5 overall) with evidence.
- Pass B: rescore only the union of shortlisted leaves (typically 10–25), produce final calibrated scores.

This structure reduces lost-in-the-middle risk by shrinking the decisive comparison set. citeturn0search4

### Designing a calibrated 0.0–1.0 scoring rubric

Two challenges are easy to conflate:

1) **Ranking quality** (is the top leaf correct?)  
2) **Score calibration** (does “0.8” mean ~80% correctness?)

There is strong evidence (in high-stakes reasoning domains) that LLM self-reported confidence can be poorly calibrated and remain high even when accuracy drops on harder questions. citeturn4search2 While your task is different (taxonomy placement, not clinical reasoning), the core warning generalizes: treat raw self-reported confidence as *an output feature that must be calibrated empirically*, not as truth. citeturn4search2

**Recommendation: anchored, evidence-capped scoring (absolute + constrained by competition)**

Use a five-anchor rubric, and instruct the model that it may not exceed an anchor unless it can cite explicit Arabic evidence from the excerpt:

- **0.00** — Contradiction: the leaf clearly mismatches the excerpt’s subject/function.
- **0.20** — Keyword-only: surface overlap (a shared term) but wrong function/scope.
- **0.50** — Plausible: consistent with some content, but missing explicit signals; competing leaves plausibly better.
- **0.80** — Strong fit: multiple explicit signals (topic framing + textual evidence) align with the leaf.
- **0.95–1.00** — Near-certain: the excerpt explicitly defines/discusses exactly the leaf topic (e.g., “مِن الزائدة” for `zawaid_huruf_aljar`, or “كي حرف جر” for `ma3ani_huruf_aljar`), and alternatives are clearly weaker. fileciteturn8file0L1-L1 fileciteturn9file0L1-L1

Then impose two additional constraints to force more stable calibration:

- **Evidence cap:** if the model cannot quote (shortly) at least one Arabic evidence phrase supporting the function/scope, the score must be ≤0.60.
- **Competition check:** if the top two leaves are both plausible and the excerpt is ambiguous, cap the top score at ≤0.80 and raise the runner-up, instead of producing a spurious 0.95.

This design aligns with classification prompt research showing that injecting explicit boundary constraints and decision principles improves fine-grained classification in specialized domains. citeturn0search0

**On “explain before scoring” (chain-of-thought):** for your use case, the highest-leverage move is not long reasoning traces, but **short, structured “evidence bullets”**. Long free-form reasoning increases token cost and may introduce rationalization. A structured-output benchmark shows that even strong models have deficiencies in structured outputs in general (though GPT-4 tends to be stronger), so keeping reasoning fields short reduces both failure surface and output-token pressure. citeturn2search3

## Prompt templates for Stage 1 and Stage 2

Below are rough templates designed to reflect the repository constraints: (a) Arabic input and labels, (b) stable leaf paths, (c) forced disambiguation by function and focus, and (d) evidence-capped scoring.

### Stage 1 prompt template (branch selection)

```text
SYSTEM:
You are an expert Arabic scholarly text router. Your job is to choose 1–3 likely TOP-LEVEL branches of the taxonomy where this excerpt belongs.
You must use meaning, function, and scholarly focus — not keyword matching.
Do NOT translate Arabic. Do NOT invent branches.

USER:
Task:
Given the excerpt metadata (Arabic) and the taxonomy top-level branches, select 1 to 3 best-fit branches.

Disambiguation rule (important):
Many Arabic terms are polyfunctional (same word, different grammatical function).
Choose branches based on the function discussed (e.g., حرف جر vs ناصب vs أسلوب القسم), as signaled by the excerpt’s description/topic/context.

Input excerpt metadata:
- excerpt_topic (Arabic list): {{excerpt_topic_list}}
- description_arabic (Arabic): {{description_arabic}}
- div_path (Arabic headings): {{div_path}}
- primary_function: {{primary_function}}
- content_types: {{content_types}}

Taxonomy top-level branches (ID — Arabic title — tiny hint examples):
{{for each top_level_branch}}
{{index}}) {{branch_id}} — {{branch_title_ar}}
    Examples (from inside this branch): {{example_leaf_titles_ar_1}} | {{example_leaf_titles_ar_2}} | {{example_leaf_titles_ar_3}}
{{end}}

Output JSON ONLY (no markdown, no extra keys):
{
  "selected_branch_ids": ["...","..."],
  "rationale_arabic": {
    "<branch_id>": "Arabic reason in 1–2 sentences, citing function/focus cues",
    "...": "..."
  }
}
```

This template uses selective enrichment (a few example leaves per branch) rather than dumping the full subtree, consistent with findings that large structured label spaces are ineffective to include wholesale in prompts. citeturn11view0

### Stage 2 prompt template (leaf scoring)

```text
SYSTEM:
You are an expert Arabic scholarly text classifier.
You will receive: (1) excerpt metadata, (2) excerpt text (Arabic), (3) candidate leaf list.
Score EACH candidate leaf from 0.0 to 1.0 using the rubric below.
Do NOT translate Arabic. Do NOT pick based on keyword overlap alone.

Scoring rubric (anchors):
- 0.00 = contradicts the excerpt’s function/topic
- 0.20 = keyword overlap only; function/scope mismatch
- 0.50 = plausible but not clearly supported; competing leaves likely
- 0.80 = strong fit with multiple explicit signals
- 0.95–1.00 = near-certain; excerpt explicitly focuses on this leaf topic

Evidence cap:
If you cannot cite at least one short Arabic evidence phrase from the excerpt metadata/text confirming the function/scope, the score MUST be <= 0.60.

Overview rule:
If the excerpt is broadly definitional, enumerative, cross-reference, or covers multiple subtopics without deep focus, prefer __overview leaves.
If the excerpt is about one specific concept/particle/rule family, prefer the most specific leaf (not __overview).

Polyfunctionality rule:
If a term exists in multiple leaves (e.g., a particle with different functions), choose the leaf matching the function discussed (جر vs نصب vs بلاغة…),
as signaled by phrases like: "حرف جر", "مجرور", "معاني", "الزائدة", "ينصب المضارع", "إضمار أن", "القسم", etc.

USER:
Input excerpt metadata:
- excerpt_topic: {{excerpt_topic_list}}
- description_arabic: {{description_arabic}}
- div_path: {{div_path}}
- primary_function: {{primary_function}}
- content_types: {{content_types}}

Excerpt text (Arabic):
{{primary_text_truncated}}

Candidate leaves:
(Each item has leaf_path; use leaf_path exactly in output.)
{{for each candidate}}
{{index}}) leaf_path="{{leaf_path}}"
    leaf_title_ar="{{leaf_title_ar}}"
    parent_title_ar="{{parent_title_ar}}"
{{end}}

Output JSON ONLY:
{
  "rankings": [
    {
      "leaf_path": "...",
      "score": 0.0,
      "evidence_phrases_ar": ["...","..."],
      "short_reason_ar": "Arabic, <= 20 words"
    }
    ...
  ],
  "top_leaf_path": "...",
  "top_score": 0.0,
  "runner_up_leaf_path": "...",
  "runner_up_score": 0.0,
  "ambiguity_note_ar": "Arabic, optional; mention if polyfunctionality/overview ambiguity exists"
}
```

This template encodes the exact disambiguation pressures surfaced by your own adversarial fixture for **كي**, and the “focus override” from the oath-particle hard case. fileciteturn9file0L1-L1 It also borrows from structured prompting principles: enforce a strict JSON schema and keep free-form text short to reduce parsing instability. citeturn2search3

### Scaling adaptation for `3ilm_alma3ani` (recommended Stage 1.5 trigger)

Add a deterministic trigger in orchestration (not inside the LLM prompt): if the candidate set would exceed ~80 leaves, run a sub-branch selector. The need for this is motivated by long-context robustness limitations and hierarchical classification research warning against dumping large label spaces into prompts. citeturn0search4 citeturn11view0

A Stage 1.5 prompt can reuse the Stage 1 template, but with “children of the selected branch” as the branch list (e.g., children of `3ilm_alma3ani` in your balagha tree). fileciteturn6file0L1-L1

## Diacritics as a disambiguation signal

Arabic diacritics (tashkīl) can disambiguate heterophonic homographs and clarify pronunciation/meaning, but they are typically omitted in ordinary Arabic text, and appear mainly in pedagogical contexts or where ambiguity would otherwise persist. citeturn14search0 This matches what you will see in classical/edited texts: diacritics may be present in quoted lines or carefully typeset passages, but not reliably across all excerpts. citeturn14search1

**Recommendation:** explicitly instruct the model:

- “If diacritics are present, treat them as a *strong* hint for meaning/function.”
- “Do not penalize missing diacritics; rely on surrounding context and the excerpt description/topic.”

This avoids adding noise when diacritics are inconsistently present, while preserving their value when they appear in function-bearing phrases. citeturn14search0 citeturn14search1

## Contextualizing with existing Islamic library categorization

Existing digital Islamic libraries often use **coarse, book-level subject categories** (e.g., “العقيدة,” “النحو والصرف,” “البلاغة,” “علوم الحديث”), which provides a sanity check on your top-level branch design but not on leaf-level granularity. For example, a large online interface labeled as “أقسام المكتبة الشاملة” exposes categories including “النحو والصرف” and “البلاغة” and “العقيدة” as high-level browsing sections. citeturn5search0 More broadly, descriptions of entity["organization","Al-Maktaba al-Shamela","arabic digital library"] characterize it as organizing books into traditional Islamic topical “departments” (Aqidah, Tafsir, Hadith, etc.), reinforcing that the *industry norm* is coarse ontology at the browsing layer. citeturn5search42turn5search10

Your system is intentionally finer-grained (leaf-level rule/topic placement inside a science), so prompts must compensate for the fact that “standard library categorization intuition” is too broad—another reason to keep Stage 1 coarse (branch routing) but make Stage 2 explicitly functional and evidence-grounded. citeturn5search0turn11view0