# KR Excerpting Engine Diagnostic Scholarly Analysis

## Scope, evidence base, and working definitions

This analysis is constrained to the artifacts you specified inside the entity["company","GitHub","code hosting platform"] repo `rayanino/kr`, focusing on a single smoke run dated 2026-03-31 (Europe/Brussels). The run contains 133 extracted Arabic “teaching units” across five packages (`ibn_aqil_v1`, `ibn_aqil_v3`, `taysir`, `ext_39_masala`, `ext_46_qa`). fileciteturn25file0L1-L1

The official run summary reports 4 validation errors total, all code `EX-V-002` (3 in `taysir`, 1 in `ext_46_qa`). fileciteturn25file0L1-L1 The machine-readable summary corroborates counts, costs, and the per-package error tally. fileciteturn26file0L1-L1

The evaluation protocol defines five review dimensions that I use as the organizing frame (Quality, Structural Integrity, Consensus Quality, Coverage Analysis, Arabic Text Fidelity). fileciteturn25file0L1-L1

Model configuration needs one explicit caveat: the protocol text claims escalation is “Gemini 2.5 Pro,” fileciteturn25file0L1-L1 but the `run_metadata.json` for this run configures escalation as `mistralai/mistral-large-2411` with primary = `openai/gpt-5.4` and verify = `anthropic/claude-opus-4.6`. fileciteturn12file0L1-L1 I treat `run_metadata.json` as ground truth for “what actually ran,” and treat the protocol line as potentially stale documentation.

I read:  
- `integration_tests/smoke_api/EVALUATION_PROTOCOL.md` and `SUMMARY.json`. fileciteturn25file0L1-L1 fileciteturn26file0L1-L1  
- All `excerpts.jsonl` for the five packages (for patterns + examples). fileciteturn27file0L1-L1 fileciteturn29file0L1-L1 fileciteturn19file0L1-L1 fileciteturn20file0L1-L1 fileciteturn17file0L1-L1  
- All per-package `run_metadata.json`. fileciteturn12file0L1-L1 fileciteturn13file0L1-L1 fileciteturn14file0L1-L1 fileciteturn15file0L1-L1 fileciteturn16file0L1-L1  
- `engines/excerpting/SPEC.md` (requested sections; I rely on it mainly as the canonical spec anchor, but the most actionable prompt gaps show up directly in the code prompts). fileciteturn7file0L1-L1  
- Prompt implementations: `phase2_classify.py`, `phase2_group.py`, `phase3_enrichment.py`, `phase3_consensus.py`. fileciteturn8file0L1-L1 fileciteturn9file0L1-L1 fileciteturn10file0L1-L1 fileciteturn11file0L1-L1  

Frequencies below are computed from the excerpt outputs where the triggering signal is observable in the JSONL (e.g., specific `gate_flags`, `review_flags`, or a detectable structural motif like “11- … 12- …”). Where the “error” is inherently normative (e.g., “should the primary_function be X or Y”), I label it as an inference and keep frequency conservative.

## Excerpt quality patterns

### Error pattern: Over-asserted madhhab attribution in explicitly multi-madhhab argumentation
**Frequency:** 3/133 excerpts (2.3%), all in `taysir`, flagged as `school_consensus_disagreement`. fileciteturn27file0L1-L1

**Why this is a pattern (what the model is doing):**  
When an excerpt surveys positions across multiple schools and scholars, the enrichment step sometimes still assigns a single madhhab (notably `حنبلي`) with moderate confidence, even though the text reads like cross-school tarjīḥ. This then triggers verifier disagreement (“cross_school أو عام …”) and the system resolves via “keep enrichment but flag.” fileciteturn27file0L1-L1

**Root cause in prompts (what’s missing):**  
The enrichment prompt asks to assign `school` only when it’s “clearly representing a particular madhhab” and to be conservative, but it lacks:  
- a crisp *decision procedure* for “survey + tarjīḥ” texts where the author uses “مذهبنا” or names multiple madhāhib, and  
- a few-shot example showing that “multi-madhhab survey + preferred view” should generally be `cross_school` (or null) unless the excerpt is explicitly framed as *intra-madhhab doctrine* (e.g., “المذهب عندنا… المعتمد…” without a broader comparative survey). fileciteturn10file0L1-L1  
Compounding this, the verifier prompt schema does not enforce that its alternative must be one of the allowed enum values; it invites a “proposed correct value” but does not restrict format, so the verifier returns explanatory prose in `alternative`-like content, which makes clean consensus harder. fileciteturn11file0L1-L1

**Proposed fix:**  
Add a short rule + few-shot in `phase3_enrichment.py` (and a matching verifier few-shot in `phase3_consensus.py`) that explicitly maps “comparative fiqh survey (multiple madhāhib named) + tarjīḥ” to `school=cross_school`, unless the excerpt is explicitly *presenting madhhab doctrine*.

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt (from `taysir`, excerpt `exc_src_test0001_div_src_test0001_6_000_0_8`): fileciteturn27file0L1-L1  
> **اختلاف العلماء…**  
> … *فذهب المالكية… وذهب الحنابلة… وذهب بعض العلماء…*  
> … *وظاهر النهى… لكن يخصص من ذلك… باتفاق العلماء.*

Correct enrichment fields to demonstrate in-prompt:  
```json
{
  "school": "cross_school",
  "school_confidence": 0.85,
  "description_arabic": "عرض خلاف الفقهاء في دلالة النهي بين التحريم والكراهة مع ترجيح ظاهر النهي."
}
```
And in the verifier few-shot (to prevent prose alternatives):  
```json
{
  "decision_type": "school_attribution",
  "agree": false,
  "issues": ["النص يعرض خلاف مذاهب متعددة فلا ينسب لمذهب واحد"],
  "alternative": "cross_school"
}
```

### Error pattern: Hadith-lesson composites default to `primary_function=evidence_hadith` even when the pedagogical payload is extracted rulings
**Frequency:** At least 3/133 (≥2.3%), all in `taysir`, where the same excerpt contains a “ما يؤخذ من الحديث” rulings list but `primary_function` remains `evidence_hadith`. fileciteturn27file0L1-L1  
This likely occurs more broadly, but I’m only counting cases where the “rulings list” marker is explicit in the unit text.

**Why this is a pattern:**  
The grouping/classification stack appears to anchor `primary_function` on the *front-matter cue* (“الحديث الأول… عن فلان… قال رسول الله…”) rather than the *dominant learning unit function* in the full unit. In these composites, the excerpt includes: hadith text + “غريب الحديث” + “المعنى الإجمالي” + “ما يؤخذ من الحديث” (explicit rulings). In scholarly-library terms, the “teaching unit” is closer to a rulings/derivation unit with embedded evidence than “pure hadith evidence.” fileciteturn27file0L1-L1

**Root cause in prompts:**  
Neither the Phase 2 classification prompt nor the Phase 2 grouping prompt includes an explicit “tie-break rule” for composite pedagogical blocks of the form:  
- evidence (hadith) + explanation + extracted lessons/rulings.  
The prompts list labels and general heuristics, but lack a worked example showing that “ما يؤخذ من الحديث” should flip the `primary_function` to `rule_statement` (or `opinion_statement` if it’s primarily tarjīḥ), keeping `evidence_hadith` in secondary/content types. fileciteturn8file0L1-L1 fileciteturn9file0L1-L1

**Proposed fix:**  
Add to `phase2_group.py` a prioritization rule:

- If a unit contains an explicit extracted-lessons scaffold (“ما يؤخذ من الحديث”، “فوائد”، “مسائل”، “يستفاد منه”) and the unit enumerates rulings/conditions, then set `primary_function` to `rule_statement` (or `condition_exception` if it is structurally about conditions/exceptions), and keep `evidence_hadith` in `secondary_functions` / `content_types`.

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt (from `taysir`, excerpt `exc_src_test0001_div_src_test0001_6_000_0_2`): fileciteturn27file0L1-L1  
> **الحديث الأول** … “لا يقبل الله صلاة أحدكم…”  
> … **ما يؤخذ من الحديث:**  
> 1- أن صلاة المحدث لا تقبل…  
> 2- أن الحدث ناقض…  
> 3- المراد بعدم القبول…  
> 4- الحديث يدل على أن الطهارة شرط…

Correct grouping-stage label fields to demonstrate in-prompt:  
```json
{
  "primary_function": "rule_statement",
  "secondary_functions": ["evidence_hadith", "definition", "evidence_rational", "structural_transition"],
  "content_types": ["rule_statement", "evidence_hadith", "definition", "evidence_rational", "structural_transition"],
  "self_containment": "FULL"
}
```

## Structural integrity patterns

### Error pattern: `text_snippet` normalization (newline collapse / character loss) undermines exact-prefix invariants and triggers `EX-V-002` drops
**Frequency:** 4/133 excerpts failed validation as `EX-V-002` in this run. fileciteturn25file0L1-L1 fileciteturn26file0L1-L1  
Separately, even among “accepted” excerpts, there are visible cases where `text_snippet` collapses newlines into spaces (a latent structural mismatch risk). fileciteturn29file0L1-L1

**Why this is a pattern:**  
In `ibn_aqil_v3` excerpt `exc_src_test0001_div_src_test0001_3_000_0_0`, the `primary_text` begins with multi-line formatting, but `text_snippet` is rendered as a mostly single-line string with spaces, which is precisely the kind of transformation that breaks strict “prefix equals first N chars” checks. fileciteturn29file0L1-L1  
Given the evaluation protocol explicitly calls out `EX-V-002` as a key validation issue to investigate, this strongly suggests the prompts are not reliably achieving “copy exact bytes” behavior at scale. fileciteturn25file0L1-L1

**Root cause in prompts:**  
Phase 2 prompts do instruct exact copying (“copy the first 50/80 chars exactly”), but they do not include a few-shot example demonstrating that:  
- newlines **must** remain newlines (not spaces),  
- zero-width Arabic markers (e.g., “‌‌”) must be preserved, and  
- punctuation like ellipses “…” and footnote glyphs must remain byte-for-byte. fileciteturn8file0L1-L1 fileciteturn9file0L1-L1

**Proposed fix:**  
Add a “copy fidelity” few-shot at the top of both Phase 2 prompts showing a tricky RTL + newline + zero-width case, plus a hard rule: “Do not reflow whitespace. Do not normalize punctuation. Do not remove tatweel/zero-width markers.”

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt opening (from `ibn_aqil_v3`, excerpt `exc_src_test0001_div_src_test0001_3_000_0_0`): fileciteturn29file0L1-L1  
> بسم الله الرحمن الرحيم  
> ‌‌حروف الجر  
> هاك حروف الجر وهي من إلى  
> …

Correct snippet field (demonstration-style; include newlines, do not collapse):  
```json
{
  "text_snippet": "بسم الله الرحمن الرحيم\n‌‌حروف الجر\nهاك حروف الجر وهي من إلى\n…"
}
```
(Exactly-as-copied newlines are the point of this example; the prompt can still specify the precise character count requirement right above it.)

### Error pattern: Numbered list items merged into a single teaching unit despite clean “one item = one unit” affordances
**Frequency:** At least 1/133 excerpts (≥0.8%) shows this failure mode clearly (more may exist, but this is the unambiguous case). fileciteturn19file0L1-L1  

**Why this is a pattern:**  
In `ext_39_masala`, excerpt `exc_src_test0001_div_src_test0001_2_000_pre_0_11` contains two distinct numbered rulings (“11- …” and “12- …”) combined into one `primary_text`. fileciteturn19file0L1-L1  
This violates the implicit “atomicity” expectation in the evaluation protocol’s definition of “self-contained teaching unit,” because each numbered item is already a strong segmentation boundary in Arabic fiqh prose. fileciteturn25file0L1-L1

**Root cause in prompts:**  
`phase2_group.py` emphasizes “coherent teaching unit” but does not include:  
- an explicit rule that Arabic numbered rulings (“١- / 1- / 11- … 12- …”) are **default split points**, and  
- a few-shot showing the correct behavior for back-to-back numbered rulings on related but distinct points. fileciteturn9file0L1-L1

**Proposed fix:**  
Add a grouping rule:  
- “If you see a new numbered item that introduces a new claim/ruling, split into a new unit unless the second line is clearly a subpoint of the first.”

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt (from `ext_39_masala`, excerpt `…_0_11`): fileciteturn19file0L1-L1  
> 11 - الوصية الجائرة باطلة …  
> 12 - ولما كان الغالب على الناس اليوم … يُوصى أن يُدفن …

Correct grouping output should produce **two** teaching units (illustrative; segment indices would map accordingly):  
```json
[
  {
    "primary_text": "11 - الوصية الجائرة باطلة ...",
    "primary_function": "rule_statement"
  },
  {
    "primary_text": "12 - ولما كان الغالب على الناس اليوم ... يُوصى أن يُدفن ...",
    "primary_function": "rule_statement"
  }
]
```

## Consensus quality patterns

### Error pattern: Author-attribution consensus breaks because verifier “alternative” is free-form prose, not a canonical author_id
**Frequency:** 12/44 excerpts in `ibn_aqil_v3` (27.3% of that package; 9.0% of total 133) contain `gate_flags=["EX-G-001"]` and `review_flags=["attribution_consensus_escalated"]`, with consensus resolution method `no_majority_gate`. fileciteturn29file0L1-L1

**Why this is a pattern:**  
The consensus records show a consistent pathology:  
- `enrichment_value` is `"unknown"`,  
- `escalation_value` is the canonical author name (e.g., `"ابن عقيل"`),  
- but `verifier_value` is a full English explanation sentence beginning “This should be attributed to ابن عقيل…” rather than the bare canonical string `"ابن عقيل"`.  
Because voting compares raw strings, the escalation vote cannot match the verifier vote, so there is “no majority,” and the system gates. This is visible repeatedly, e.g., in `ibn_aqil_v3` excerpt `exc_src_test0001_div_src_test0001_3_000_0_8`. fileciteturn29file0L1-L1

**Root cause in prompts:**  
The Phase 3 verifier item schema allows `alternative` to be essentially any string and does not constrain it to “one of the allowed enumerated IDs.” The system prompt also invites explanation (“brief”), which encourages prose. There is no few-shot example showing that `alternative` must be a single token/value. fileciteturn11file0L1-L1  
This is not “model stupidity”; it is a schema/prompt contract mismatch: consensus expects a canonical value, the verifier prompt elicits a justification blob. fileciteturn11file0L1-L1

**Proposed fix:**  
In `phase3_consensus.py`, change the contract so the verifier returns:
- `alternative_value` (strict enum or strict author_id string), and
- `rationale` (free-form), explicitly separated.  
Also add a few-shot showing “BAD: prose in alternative” vs “GOOD: single canonical value.”

**Proposed few-shot example (from actual excerpts; show correct output):**  
Problematic real consensus case (from `ibn_aqil_v3`, excerpt `…_3_000_0_8`): the text contains clear sharh markers like “وهذا معنى قوله…”. fileciteturn29file0L1-L1

Correct verifier output (to include as few-shot):  
```json
{
  "decision_type": "author_attribution",
  "agree": false,
  "issues": ["النص شرحٌ على نظم ابن مالك وفيه: «وهذا معنى قوله»"],
  "alternative": "ابن عقيل"
}
```
And (optionally) a separate rationale field if you adopt the schema split:  
```json
{
  "rationale": "وجود ألفاظ الشرح والإحالة على «قول المصنف» يدل على طبقة الشرح لا المتن."
}
```

### Error pattern: School-attribution verifier alternatives are not normalized to enum values, producing “keep enrichment but flag” outcomes
**Frequency:** 3/133 (2.3%), all in `taysir`, with consensus decisions `resolution_method=enrichment_kept_flagged` and review flag `school_consensus_disagreement`. fileciteturn27file0L1-L1

**Why this is a pattern:**  
In these cases the verifier returns values like “cross_school أو عام (لا ينسب لمذهب بعينه)” instead of a canonical `cross_school`, preventing clean machine comparison and forcing a non-resolving flagged state. fileciteturn27file0L1-L1

**Root cause in prompts:**  
Same schema issue as author attribution, but on `school_attribution`: the verifier prompt does not enumerate allowed values in a “must choose exactly one” format, and provides no few-shot demonstrating strict normalization. fileciteturn11file0L1-L1

**Proposed fix:**  
Add explicit enum list for school attribution in the verifier prompt and forbid conjunctions/Arabic commentary inside the value.

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt (from `taysir`, excerpt `exc_src_test0001_div_src_test0001_6_000_0_15`) includes broad statements (“وقد خص العلماء…”) plus an attribution to “مذهبنا” while also mentioning other madhāhib, which is the typical trigger for disagreement. fileciteturn27file0L1-L1  

Correct verifier snippet:  
```json
{
  "decision_type": "school_attribution",
  "agree": false,
  "issues": ["النص لا يقرر مذهبًا واحدًا بل يعمم ويذكر (العلماء) دون قصر على مذهب"],
  "alternative": "cross_school"
}
```

## Coverage patterns

### Error pattern: Under-splitting of “textbook scaffold” sections reduces atomic coverage (single excerpt spans hadith + glossary + global meaning + extracted rulings)
**Frequency:** Common in `taysir`; conservatively ≥5/28 excerpts in that package contain at least 3 of these scaffold headers inside one unit (“غريب الحديث”، “المعنى الإجمالي”، “ما يؤخذ…”). fileciteturn27file0L1-L1  
(Exact counting is straightforward but not encoded as flags; this conservative estimate is based on repeated visible structure in the `taysir` outputs.)

**Why this is a pattern:**  
From a retrieval / library perspective, these scaffolds are natural split points because each section is a different pedagogical function. Keeping them merged reduces searchability and can inflate “self_containment=FULL” even though parts are deictic (“الحديث الذي معنا…”, “كما تقدم…”). The evaluation protocol explicitly asks whether a unit is “a valid, self-contained teaching unit,” which implies an atomicity preference. fileciteturn25file0L1-L1

**Root cause in prompts:**  
The grouping prompt says to keep units coherent, but does not provide domain-specific split heuristics for standard Arabic sharḥ layouts (Hadith → Gharib → Meaning → Lessons). Without few-shot, the model treats the entire lesson page as one unit. fileciteturn9file0L1-L1

**Proposed fix:**  
Add a few-shot in `phase2_group.py` demonstrating that “lesson scaffold” sections should typically become separate teaching units unless the later sections are extremely short and strictly dependent.

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt (from `taysir`, excerpt `exc_src_test0001_div_src_test0001_6_000_0_2`): it contains Hadith text + “غريب الحديث” + “المعنى الإجمالي” + “ما يؤخذ من الحديث”. fileciteturn27file0L1-L1  

Correct grouping output sketch (three units):  
```json
[
  {
    "primary_text": "الحديث الأول ... \"لا يقبل الله صلاة أحدكم...\"",
    "primary_function": "evidence_hadith",
    "self_containment": "FULL"
  },
  {
    "primary_text": "غريب الحديث: ... \"أحدث\" ... \"الحدث\" ...",
    "primary_function": "definition",
    "self_containment": "FULL"
  },
  {
    "primary_text": "ما يؤخذ من الحديث: 1- ... 2- ... 3- ... 4- ...",
    "primary_function": "rule_statement",
    "self_containment": "FULL"
  }
]
```

### Error pattern: Over-extraction of purely bibliographic / heading-only fragments inflates excerpt count with low-teaching-value units
**Frequency:** At least 2/133 excerpts are clearly “title/heading only”: one in `taysir` (`تيسير العلام شرح عمدة الأحكام\nللبسام`) and one in `ext_46_qa` (`الكلام في‌‌ المقدمات\nفيها مسائل الأولى`). fileciteturn27file0L1-L1 fileciteturn20file0L1-L1  
There are likely more (basmala-only, chapter lists), but these two are unambiguous minimal-content cases.

**Why this is a pattern:**  
The pipeline is extracting them as “teaching units,” with `primary_function=editorial_note` and often `self_containment=FULL` (titles) or `PARTIAL` (headings). That may be intended for navigation/metadata, but it competes with the “teaching unit” objective stated in the evaluation protocol. fileciteturn25file0L1-L1

**Root cause in prompts:**  
The grouping prompt does not explicitly decide whether to:  
- exclude purely bibliographic lines/headings, or  
- keep them but tag them for a different downstream use (index/navigation).  
Without a few-shot, the model behaves inconsistently: sometimes emits titles, sometimes not. fileciteturn9file0L1-L1

**Proposed fix:**  
Add an explicit “include/exclude” policy in `phase2_group.py`, ideally:  
- “Only extract headings/titles if they add scholarly meaning (e.g., a mas’ala statement) OR if the product wants navigational stubs; otherwise skip.”  
If you want them, require a distinct function label (e.g., keep `editorial_note` but add a flag like `is_navigation_stub=true`).

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input excerpt (from `taysir`, excerpt `exc_src_test0001_div_src_test0001_7_000_0_0`): fileciteturn27file0L1-L1  
> تيسير العلام شرح عمدة الأحكام  
> للبسام

If **excluding** (teaching-unit-only mode), the correct grouping output is:  
```json
[]
```
If **including** (navigation mode), enforce explicit stub tagging:  
```json
{
  "primary_function": "editorial_note",
  "description_arabic": "عنوان الكتاب واسم المؤلف.",
  "is_navigation_stub": true
}
```

## Arabic fidelity patterns

### Error pattern: Footnote types default to `unknown_footnote_type` for common editor notes (ضعف typing taxonomy without exemplars)
**Frequency:** At least 3/133 occurrences in `taysir` where `footnotes_relevant[].footnote_type` is `unknown_footnote_type` despite the footnote being a recognizable editor/tahqīq note. fileciteturn27file0L1-L1

**Why this is a pattern:**  
Examples include footnotes that clearly function as editorial commentary or provenance notes (e.g., about limits/variants or about “إعداد الكتاب للشاملة”), but the system assigns `unknown_footnote_type` with low confidence. This is a fidelity problem because correct footnote typing is part of preserving how Arabic scholarly texts encode citation, tashīḥ, and taḥqīq layers. fileciteturn27file0L1-L1

**Root cause in prompts:**  
The enrichment prompt includes a complex multi-type footnote schema, but without few-shot examples mapping common Arabic footnote idioms to `footnote_type` labels. When a taxonomy is long and the text is heterogeneous, the no-few-shot baseline tends to overuse “unknown.” fileciteturn10file0L1-L1

**Proposed fix:**  
Add 3–5 micro few-shots for footnote typing (each one a single footnote marker + footnote text + correct `footnote_type`). Focus on the most common Arabic patterns:
- “قال المحقق…” → `tahqiq_editor`  
- “هذه رواية أحمد…” / “في الصحيحين…” → `takhrij` or `tahqiq_editor` (depending on your taxonomy)  
- “قال مُعِدُّ الكتاب للشاملة…” → `editorial_note` / `tahqiq_editor` (again depending on enum)  

**Proposed few-shot example (from actual excerpts; show correct output):**  
Footnote text (from `taysir`, excerpt `exc_src_test0001_div_src_test0001_6_000_0_19`, marker ⌜7⌝): fileciteturn27file0L1-L1  
> (*) قال مُعِدُّ الكتاب للشاملة: …

Correct enrichment footnote object:  
```json
{
  "ref_marker": "7",
  "text": "(*) قال مُعِدُّ الكتاب للشاملة: ...",
  "footnote_type": "tahqiq_editor",
  "confidence": 0.85
}
```

### Error pattern: Arabic lexical ambiguity in “hadith marker” detection produces false positives and spurious review flags
**Frequency:** 1/133 clear case in `ibn_aqil_v3` where `evidence_refs` marks a hadith reference due to the substring “أخرجه/أخرجها” even though the text is not citing hadith. fileciteturn29file0L1-L1  

**Why this is a pattern:**  
In `ibn_aqil_v3` excerpt `exc_src_test0001_div_src_test0001_3_000_0_3`, the phrase is “ومن كلامهم أخرجها متى كمه…” (meaning “take it out of his sleeve”), yet the pipeline produces `evidence_refs.type=hadith` with marker “أخرجه” and then flags `hadith_evidence_no_takhrij`. fileciteturn29file0L1-L1  
This is an Arabic fidelity trap: the same root can be ordinary prose or technical hadith-citation jargon.

**Root cause (important nuance):**  
This appears to be primarily a *heuristic/regex* ambiguity rather than an LLM misread, because the marker is auto-derived from a substring match and then cascades into a review flag. The prompt’s “conservatism rule” correctly avoids hallucinating takhrij, but the earlier detection is already wrong. fileciteturn29file0L1-L1 fileciteturn10file0L1-L1  
So: the missing piece is not only “few-shot,” but a safer detector spec (or an LLM-in-the-loop verification step for hadith markers in non-fiqh genres like nahw).

**Proposed fix:**  
Tighten hadith-marker detection to require at least one of:  
- an explicit collector name (البخاري/مسلم/أبو داود/…), or  
- a hadith-specific frame (“رواه… عن… قال رسول الله…”) near the marker, or  
- a canonical isnād pattern.  
Optionally, in enrichment prompt, add a defensive rule: “If the hadith marker is an ordinary verb usage (أخرجها من كمه), do not treat it as hadith evidence; add no takhrij and remove the hadith review flag.”

**Proposed few-shot example (from actual excerpts; show correct output):**  
Arabic input fragment (from `ibn_aqil_v3`, excerpt `…_0_3`): fileciteturn29file0L1-L1  
> ومن كلامهم **أخرجها متى كمه** يريدون من كمه

Correct behavior example to include in a prompt (or detector spec test):  
```json
{
  "evidence_refs": [],
  "review_flags": []
}
```

