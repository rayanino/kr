# Pre-flight Prompt Review for KR Excerpting Engine on Classical Arabic Scholarly Texts

## What the current prompts actually enforce

Phase 2a classification is constrained to a fixed 16-type “ScholarlyFunction” inventory and a short set of segment-boundary heuristics: isnād+matn as one segment; “قال X” + the position as one segment; each Qurʾān citation with its introduction as one segment; and “إذا … فـ” condition+result as one segment. The prompt emphasizes that offsets are approximate but `text_snippet` must be copied *exactly* from the input, with diacritics/punctuation/whitespace preserved, because snippet anchoring is the offset-normalization mechanism. fileciteturn17file0L1-L1

Phase 2b grouping defines “teaching units” primarily by pedagogical cohesion and self-containment, with a small set of grouping patterns (position+evidence+counterevidence+conclusion; definition+examples; hadith+chain+commentary; Q&A together; rule+exceptions). It includes a short “decontextualization prevention” block and then the C‑SC‑1…C‑SC‑5 self-containment criteria, mapping them to FULL / PARTIAL / DEPENDENT. fileciteturn18file0L1-L1

Phase 3 enrichment asks the LLM to add: topic keywords; a “school” label (limited set + `cross_school` + null); resolution of scholar mentions (including a small, school-based epithet mapping for “الإمام”); hadith takhrīj info (explicitly forbidding grade invention); terminology variants; cross-references (“كما تقدم …”); and context hints for PARTIAL units. fileciteturn19file0L1-L1

Phase 3 consensus verification, as implemented, uses a **two-sentence** system prompt (“You are verifying… independently assess whether the decision is correct.”) and pushes almost all operational instructions (agree/disagree, provide alternative, confidence) into the user message template; verification sees only the first 500 characters of `unit_text` per item. fileciteturn20file0L1-L1 The SPEC’s design intent is broader: consensus is triggered for non-null school, ambiguous author attribution (LA-3), and non-FULL self-containment; it embeds a longer verification template and defines conservative downgrade behavior when models disagree. fileciteturn16file0L1-L1

The rest of this report is about **where these constraints are too underspecified for classical Arabic scholarly writing**, and how that manifests as predictable corruption modes (T‑2 attribution error, T‑4 context loss) when the text’s native rhetoric is more implicit than the prompts assume. fileciteturn16file0L1-L1

## Classical Arabic scholarly structures the prompts do not explicitly cover

A key pattern across premodern genres is that “what belongs together” is often signaled **implicitly** (by discourse conventions) rather than by the explicit markers your grouping prompt names (“قال أبو حنيفة…”, “ورد عليه بأن…”, “إلا …”). fileciteturn18file0L1-L1 When you combine that with (a) a classification prompt that has only four boundary heuristics and (b) a grouping prompt whose decontextualization rules are a short list, there are several genre-typical structures that are likely to fragment.

### Matn–sharḥ–ḥāshiya anchoring by “قوله” (commentary-by-lemma)

In many commentary traditions, the commentary is structured as **lemma anchoring**: “قوله: …” (or just an unmarked lemma) followed by explanation, objections, and resolutions. A classical example is the common Wikisource presentation of *Sharḥ al-ʿAqīda al-Ṭaḥāwiyya* sections titled by the lemma (“قوله: (… )”), with the body explaining “الإشارة إلى ما تقدم…” etc. citeturn17view6turn16view6

Failure mode: your grouping prompt does not include an explicit rule like “lemma (قوله/يعني/أي) + explanation must stay together,” and C‑SC‑2 only says “pronouns/demonstratives resolve within the unit.” fileciteturn18file0L1-L1 In lemma-based sharḥ, the lemma itself can be **short**, while the commentary uses dense anaphora (“هذا”، “المراد”، “فيه”) referring back to the lemma. If grouping splits the lemma into its own unit (often a `rule_statement` or `definition`) and the explanation into a second unit (often `evidence_rational` or `refutation`), you get a *false FULL* risk: the explanation unit can look internally coherent to a model that “fills in” the lemma mentally, even though it violates the excerpt’s navigability for a human reader. fileciteturn16file0L1-L1

Concrete exemplar of the structure (nahw): in *Sharḥ Ibn ʿAqīl*, a one-line matn verse (“كلامنا لفظ مفيد كاستقم”) is immediately followed by multi-sentence unpacking (“الكلام المصطلح عليه…” and “وكقول المصنف ‘استقم’…”) where the explanation relies on the cited lemma and the example being present. citeturn16view0 If the verse line is segmented away from the explanatory prose, the prose becomes partially orphaned even if it contains a restated definition, because the pedagogical frame (“what exactly is being glossed?”) is diminished. citeturn16view0

### Tafsīr “layer-cake” reporting + tarjīḥ by the mufassir

A common tafsīr pattern is: multiple reported glosses (sometimes with isnād), then the author’s synthesis: “والصواب…” / “وأولى الأقوال…” etc. In al-Ṭabarī’s tafsīr, you can see layered reports (“وقال آخرون… ذكر من قال ذلك… حدثني…” repeated) followed by a decisive tarjīḥ: “والصواب من القول…” and even linguistic/poetic attestation. citeturn17view2

Failure mode: the taxonomy has no explicit “tarjīḥ / authorial selection” function, and the grouping rules do not explicitly require “reported glosses + tarjīḥ conclusion” to stay together—only “position + evidence + counter-evidence + conclusion,” framed in fiqh-like terms. fileciteturn18file0L1-L1 In tafsīr, the partial reports are not always “positions” in the same rhetorical sense as madhhab disputes; they are often *athar* glosses or lexical readings. The model may (a) treat each reported gloss as a standalone “narration,” (b) treat “والصواب…” as a new `rule_statement` or `opinion_statement`, and (c) split the tarjīḥ away from the reports that it is adjudicating. The excerpt then fails C‑SC‑4/5, but the prompt does not explicitly warn the model that “tarjīḥ phrases are decontextualizing unless you include the alternatives being weighed.” fileciteturn16file0L1-L1

### Uṣūl al-fiqh: qiyās structures and “taqsīm → shurūṭ → manāqiḍ” blocks

In uṣūl texts, qiyās is presented as a compact definition plus subdivisions and conditions. The *Waraqāt* example shows the canonical compact definition (“وأما القياس فهو رد الفرع إلى الأصل بعلة تجمعهما في الحكم”) followed immediately by a tripartite division and then chains of conditions (“ومن شرط الفرع…” “ومن شرط الأصل…” “ومن شرط العلة…”). citeturn18view0

Failure mode: classification has only a generic `evidence_qiyas` type and boundary rules keyed to isnād, Qurʾān citations, “قال X”, and “إذا … فـ”; nothing signals that *this* is a “definition + taxonomic division + constraints” macro-structure that should likely remain one unit for self-containment. fileciteturn17file0L1-L1 Grouping has “definition + examples” but not “definition + divisions + conditions,” and the decontext rules do not mention “taqsīm blocks” at all. fileciteturn18file0L1-L1 The predictable over-fragmentation is: one excerpt for the definition, then three more for “قياس علة/دلالة/شبه,” then several for the “conditions,” each of which presupposes the object being conditioned (e.g., “ومن شرط العلة…” without restating “العلة” in a way a reader can track). That can yield DEPENDENT/PARTIAL units, but the prompt doesn’t explicitly name “ومن شرط…” as a self-containment hazard marker to be handled conservatively. fileciteturn16file0L1-L1

### Mustalaḥ al-ḥadīth: definition-dense “guarded” definitions with enumerated exclusions

Mustalaḥ works define categories by stacking technical constraints and then enumerating excluded types. Ibn al-Ṣalāḥ’s definition of ṣaḥīḥ is characteristic: it’s a definition plus multiple technical exclusion labels (“المرسل… المنقطع… المعضل… الشاذ… معلل…”). citeturn17view0

Failure mode: C‑SC‑1 says “technical term is OK if standard for a student of the science,” but in mustalaḥ a “student” is expected to know these categories *after* study; they are exactly what beginners are learning. fileciteturn18file0L1-L1 The grouping prompt does not instruct: “In definition-heavy sciences, assume novice reader; treat undefined category labels as C‑SC‑1 failures unless locally glossed.” The result can be a systematic inflation of FULL for excerpts that are only self-contained for an advanced mustalaḥ student, not for the intended “general familiarity” reader described in the SPEC. fileciteturn16file0L1-L1

## ScholarlyFunction taxonomy gaps for Islamic scholarly genres

The 16-type taxonomy is intentionally flat and coarse, and it does cover many cross-genre primitives: definition, rule, several evidence types, named opinions, refutation/objection, examples, exceptions/conditions, cross-references, narration/isnād, editorial notes, transitions. fileciteturn16file0L1-L1 But “coverage” is not the same as “failure-safe expressivity”: what matters is whether the missing distinctions are exactly the ones that trigger decontextualization or mis-attribution in classical Arabic rhetorical practice. fileciteturn16file0L1-L1

### Missing function: explicit tarjīḥ / preference-resolution

Across fiqh, tafsīr, and uṣūl, texts often list alternatives and then mark an authoritative preference with words like: “والصواب…”, “والراجح…”, “الأصح…”, “المعتمد…”. citeturn17view2turn19view1 Today these must be mapped into `rule_statement`, `opinion_statement`, or `refutation`, but none of those cleanly captures “selecting among stated options,” and that matters because grouping rules currently guarantee cohesion primarily around “position + refutation” and “evidence + ruling,” not “alternatives + preference.” fileciteturn18file0L1-L1 The risk is *systematic decontextualization of tarjīḥ markers*: an excerpt containing only “والراجح …” can look like a complete “rule_statement” while actually missing the alternatives being adjudicated (C‑SC‑4/5 failure). fileciteturn16file0L1-L1

### Missing function: linguistic attestation as evidence (shawāhid, qirāʾāt, lughah)

In nahw and many tafsīr works, the “evidence” is not Qurʾān/hadith/ijmāʿ/qiyās, but **linguistic attestation**: Qurʾānic iʿrāb, poetic shawāhid, or dialectal usage “تقول العرب…”. Al-Ṭabarī even uses poetic evidence in the cited passage (after “والصواب…” he cites a line as attestation). citeturn17view2 The taxonomy forces these into `example` or `narration`, which loses the “evidentiary” intent; that can reduce grouping robustness because DP-4 only protects “evidence cited for a ruling,” but the model’s internal concept of “evidence” is nudged by the explicit evidence types list. fileciteturn18file0L1-L1

### Missing function: explicit “question/objection” as its own role

You do have `refutation`, but the classical objection-response pattern (“فإن قيل… قلنا…”, “اعترض… وأجيب…”) often contains a *question* that is not itself a refutation; it is a prompted premise that the answer depends on. fileciteturn16file0L1-L1 The grouping prompt includes “question+answer together,” but classification lacks any explicit encouragement to label question segments distinctly; as a result, questions can become `unclassified`, `refutation`, or `opinion_statement`, which can make later grouping harder in “dense objection cycles” (multiple “فإن قيل” in sequence). fileciteturn17file0L1-L1

### School taxonomy mismatch for ʿaqīdah and even for fiqh-adjacent uses

The enrichment prompt’s school field is explicitly limited to five legal madhāhib plus `cross_school` and null. fileciteturn19file0L1-L1 That is not “complete for the main genres of Islamic scholarship” if you intend aqīdah excerpts to be school-attributed (Ashʿarī/Māturīdī/Atharī/Muʿtazilī, etc.), and it is ambiguous even for uṣūl where “school” can mean uṣūlī methodologies (Hanafī uṣūl vs Shāfiʿī uṣūl) rather than just fiqh madhhab. fileciteturn16file0L1-L1 If you actually intend “school” to mean “fiqh madhhab only,” the prompt should say that explicitly; otherwise, models will sometimes force-fit theological cues into a fiqh label or return null inconsistently. fileciteturn19file0L1-L1

## Decontextualization prevention and self-containment: where the current rules will fail in Arabic texts

Your Phase 2b prompt contains four explicit decontextualization bullets (position+refutation, include enough of original argument, evidence+ruling, rule+إلا). fileciteturn18file0L1-L1 The SPEC’s domain rules are broader (DP‑1 through DP‑6), including question+answer and condition+result as decontextualization-critical patterns. fileciteturn16file0L1-L1 That mismatch matters because the prompt is what the grouping model actually “sees” as critical.

### Pattern: tarjīḥ markers that look self-contained but are not

In tafsīr and fiqh alike, “والصواب…” or “الراجح…” is the end of an adjudication. Al-Ṭabarī’s “والصواب من القول…” is only meaningful relative to the immediately preceding set of reported views. citeturn17view2 In your current DP list, nothing forces “tarjīḥ conclusion + alternatives” to stay together, so the model can legally split: (Unit A) a chain of reports, (Unit B) “والصواب…” plus a supporting poetic line, which then reads like a standalone `rule_statement` or `opinion_statement` even though the “what was contested?” is missing. fileciteturn18file0L1-L1

What I would add as an explicit DP rule: “Verdict/tarjīḥ phrases (الصواب، الأصح، الراجح، المعتمد، الأقوى، الأقرب…) MUST remain with the alternatives they judge, unless the unit restates the alternatives in brief.” This is exactly the kind of “Arabic scholastic shorthand” that causes silent context loss. fileciteturn16file0L1-L1

### Pattern: lemma-only anchoring (“قوله…”) as anaphora, not quotation

C‑SC‑2 focuses on pronouns/demonstratives like “هذا، المذكور، ما تقدم.” fileciteturn18file0L1-L1 In lemma-commentary writing, the key anaphor is often **structural** (“قوله: …”, “يعني…”, “أي…”, “أراد…”, “مراده…”) and can be extremely short, while the explanation is long. The sharḥ/ḥāshiya tradition is full of this. citeturn17view6turn16view6

Failure mode: the model can treat “قوله: (…short lemma…)” as “structural_transition” or “rule_statement” and then peel off the explanation as a separate unit; the explanation may not contain any explicit “dangling demonstrative” that triggers C‑SC‑2, so it can still be labeled FULL incorrectly. fileciteturn18file0L1-L1

What I would add to self-containment criteria: a criterion specifically for **lemma anchoring**. For example: “If the unit contains lemma markers (قوله، يعني، أي، المراد) then the lemma text must be present in the unit; otherwise it is at best PARTIAL.” citeturn17view6

### Pattern: “ومن شرط…” / “ينقسم…” blocks that presuppose an object outside the excerpt

In the *Waraqāt* qiyās block, several consecutive sentences begin “ومن شرط …”. citeturn18view0 If segmentation or grouping produces a unit beginning in the middle of that chain, it will be syntactically complete but semantically dependent: “ومن شرط العلة…” is meaningless unless “العلة” is established as the qiyās ʿilla being discussed and the reader knows which concept’s conditions are being listed. citeturn18view0

Your C‑SC‑4 says “argument complete, not fragment whose premise elsewhere.” fileciteturn18file0L1-L1 In Arabic scholastic style, these “premises” are often encoded as *topic headers inside the prose* (“وأما القياس…”) followed by bare condition lists. Without an explicit instruction to treat “ومن شرط…” as a fragment marker (like you treat “ورد عليه”), you will get false FULL/PARTIAL inflation. fileciteturn16file0L1-L1

### Pattern: non-إلا exceptions and soft qualifications

Your decontext rule explicitly mentions “rule + إلا clause,” but Arabic legal qualification is often done with “لكن…”, “غير أن…”, “إلا أن…”, “على خلاف…”, “إنما…”, “لولا…” and similar. fileciteturn16file0L1-L1 If those qualifiers detach, the excerpt becomes actively misleading (a classic T‑4 context loss). The prompt does not name these markers, so the model may not treat them as “must keep with the rule.” fileciteturn18file0L1-L1

I would add a rule in DP language: “keep qualifications/disclaimers introduced by لكن/غير أن/إلا أن/إنما/لولا/على خلاف/الأصح/في الأظهر with the statement they qualify.”

### Pattern: “student of the science” is underspecified for Arabic technical terms

C‑SC‑1’s “standard term any student of the science would know” is hard to operationalize, and it matters most in mustalaḥ and uṣūl, where the excerpt itself often introduces *what counts as standard*. Ibn al-Ṣalāḥ’s “ولا يكون شاذا ولا معللا” is compressed and presupposes a taxonomy the reader may not yet have. citeturn17view0 The grouping prompt does not calibrate the assumed student level by science (beginner vs intermediate), so FULL assignments will drift toward the model’s own internal notion of “standard.” fileciteturn18file0L1-L1

A concrete addition that is cheap but high-impact: tie C‑SC‑1 to the provided `science`/format context (which you already supply elsewhere) and instruct: “In mustalaḥ/uṣūl texts, treat category labels (مرسل، معضل، شاذ، معلل…) as non-standard unless locally defined or briefly glossed; otherwise mark PARTIAL with notes.” citeturn17view0turn16file0

## The verification prompt is not getting enough guidance to catch high-risk errors

As implemented, the verifier’s *system* instruction is only two sentences, while the enrichment system prompt is long and highly structured. fileciteturn20file0L1-L1 fileciteturn19file0L1-L1 Even though the **user message** contains a template with “agree/disagree… alternative… confidence,” there are four practical failure modes:

### The verifier is not instructed on the known corruption patterns you most need it to catch

The SPEC explicitly frames decontextualization and attribution as core integrity risks (T‑2/T‑4), and DP/LA/IR rules are central. fileciteturn16file0L1-L1 But the verifier system prompt does not mention: quoting conventions, epithets, “tarjīḥ marker orphaning,” lemma anchoring (“قوله”), or the asymmetry-of-harm principle you encode elsewhere (“be conservative”). fileciteturn20file0L1-L1 In practice, this increases “agree by default” behavior, especially on short, classical-looking Arabic where the model can plausibly rationalize either side.

### 500-character truncation is structurally hostile to Arabic scholarly sentences

For SCHOOL and SELF_CONTAINMENT verification, the decisive cue often appears *later*: evidence phrases, “لكن” qualifications, “والصواب” conclusions, or the actual madhhab attribution phrase can come after long isnād or long definitional scaffolding. fileciteturn20file0L1-L1 citeturn17view2 With truncation, the verifier can be forced to “hallucinate certainty” from partial text unless explicitly instructed to treat “insufficient context due to truncation” as a reason to disagree or lower confidence.

### The verifier is not asked to apply the same formal criteria the grouper uses

Your group prompt embeds C‑SC‑1…C‑SC‑5. fileciteturn18file0L1-L1 The verification call for self-containment, however, asks only: “Is this assessment correct?” with no restatement of the criteria in the verifier’s instruction hierarchy. fileciteturn20file0L1-L1 A verifier that does not re-run the same checklist will mostly validate surface plausibility.

### What the verifier system prompt should contain, concretely

If you want the verifier to catch *real* errors (not just rephrase the enrichment model), the system prompt needs explicit, testable instructions aligned to the corruption threats. The following additions are directly motivated by the DP/IR/LA risks in the SPEC and the gaps above:

- **Conservatism rule for disagreement:** “If evidence is insufficient (e.g., truncation) or ambiguity is plausible, prefer DISAGREE and propose `unknown` / `null` with low confidence, rather than guessing.” fileciteturn16file0L1-L1
- **School attribution checklist:** Require explicit cues that the unit asserts a madhhab position (e.g., “عند الشافعية…”, “مذهب…”, “قال أصحابنا…”). If the text is comparative (multiple schools), force `cross_school`. If no explicit cues, force null. fileciteturn19file0L1-L1
- **Epithet ambiguity warning:** Instruct the verifier to treat “الإمام/الشيخ/الشيخان/الصاحبان” as ambiguous unless the science + school + context resolves it, and to penalize confident resolutions without textual anchors. citeturn19view0turn17view4
- **Self-containment markers:** Provide a list of “fragment openers” that should generally prevent FULL: “ورد عليه…”, “وأما قول…”, “والجواب…”, “ومن شرط…”, “الأول/الثاني…”, “كما تقدم…”, “قوله… (lemma anchoring)” unless the needed referent is present. fileciteturn16file0L1-L1
- **Tarjīḥ cohesion rule:** Explicitly warn that “والصواب/الراجح/الأصح” requires the alternatives being judged, else DEPENDENT/PARTIAL. citeturn17view2turn19view1

Right now, none of that is in the verifier’s system-level instruction, even though these are the dominant classical-text corruption channels. fileciteturn20file0L1-L1

## Epithet resolution: the current prompt misses common classical patterns

Your enrichment prompt only gives explicit mapping guidance for “الإمام” (by source school) and mentions “الشيخ” and “صاحب الكتاب/المصنف.” fileciteturn19file0L1-L1 Classical Arabic scholarly texts use a much wider epithet system, and several are **highly ambiguous across sciences and madhāhib**, which makes “best guess with low confidence” a hazardous instruction because it produces a *plausible but false* canonical name. fileciteturn19file0L1-L1

### “الشيخان” is not one thing

In hadith usage, “رواه الشيخان” and “متفق عليه” refer to al-Bukhārī and Muslim; this is explicitly stated in the referenced explanation. citeturn17view4 But “الشيخان” is also used as a madhhab-internal shorthand for two jurists and differs by madhhab (e.g., in Shāfiʿī fiqh it can mean al-Rāfiʿī and al-Nawawī). citeturn19view0turn19view1

Failure mode: the enrichment prompt does not mention “الشيخان” at all, so the model is likely to:
- incorrectly resolve “الشيخان” to Bukhārī/Muslim in a fiqh context,
- or incorrectly resolve it to Rāfiʿī/Nawawī in a hadith context,
- or “pin” it to the source madhhab without considering that the *science* or the phrase “متفق عليه” indicates hadith usage. fileciteturn19file0L1-L1

Given how common “متفق عليه” is in fiqh argumentation, this is not an edge case; it is a routine pattern that will silently poison scholar metadata at scale if not explicitly handled. citeturn17view4turn19view0

### Other high-frequency epithets not covered that matter for classical corpora

Even staying within mainstream Sunni fiqh/hadith usage, highly common shorthands include (examples, not an exhaustive list): “الصاحبان”, “الثلاثة”, “الأئمة”, “شيخ الإسلام”, “القاضي”, “الحافظ”, “صاحب …” (by book title), and “أصحابنا” / “مشايخنا” (school-internal collectives). fileciteturn16file0L1-L1 Your prompt does not instruct how to treat collective attributions (“أصحابنا”) or book-title metonyms (“صاحب المغني”), which are pervasive in fiqh and uṣūl. fileciteturn19file0L1-L1

A safer instruction than “best guess” would be: **prefer leaving `resolved_name=null` unless the referent can be justified by explicit textual anchors or by (science + school + very specific epithet).** The dictionary entry itself demonstrates that “الشيخان” changes referent by domain (hadith vs madhhab vs ʿaqīdah usage), which is exactly why guessing is risky. citeturn19view0turn17view4

## Additional cross-genre concerns for real classical Arabic corpora

### The snippet anchoring mechanism is brittle to non-diacritic copying errors common in Arabic

Offset normalization depends on the LLM reproducing the first 50 characters “exactly,” with fallbacks only for whitespace normalization and diacritic stripping. fileciteturn17file0L1-L1 Classical Arabic texts frequently contain non-diacritic special characters that models sometimes normalize: Qurʾān brackets (﴿ ﴾), ﷺ ligatures, and inline footnote markers (your pipeline preserves `⌜N⌝`). fileciteturn16file0L1-L1 If the first 50 characters include any of these and the model normalizes or drops them, your fallback match will still fail (because you don’t strip punctuation/ornaments, only diacritics). The net effect is an EX‑C‑003 spike (snippet-not-found) concentrated in exactly the texts you care about most (hadith/tafsir with citation markers; critical editions with dense footnote markers). fileciteturn17file0L1-L1

### Verse-commentary cohesion is not explicitly enforced in the grouping prompt

The SPEC discusses verse-commentary handling (VC rules) as a domain reality, but the actual GROUP_SYSTEM_PROMPT shown in code does not include a “verse + its commentary must stay together” rule. fileciteturn16file0L1-L1 fileciteturn18file0L1-L1 In nahw corpora like *Ibn ʿAqīl*, verse lines and explanations are interleaved; the excerpt above shows a verse line followed by extended commentary and examples. citeturn16view0 Without explicit constraints, this is a classic place where over-segmentation produces orphaned pedagogical units (either unexplained verses or commentary missing its lemma). citeturn16view0turn18file0

### The “school” field’s semantics will drift unless you pin it to science

Right now the enrichment prompt says “null if no school attribution is identifiable (grammar, tafsir, etc.).” fileciteturn19file0L1-L1 This leaves ambiguous what should happen for aqīdah (where “school” is meaningful but not a fiqh madhhab) and for uṣūl (where “school” can be either madhhab-based or methodology-based). fileciteturn16file0L1-L1 The result in practice is inconsistent output: different models (or even the same model across runs) will alternate between always-null and forced madhhab labels based on faint cues. Given that non-null school triggers consensus verification, this can also unpredictably increase verification load. fileciteturn20file0L1-L1

### Concrete “where a prompt would fail” examples, aligned to your questions

To make the failure channels explicit:

- **Tafsīr layering + tarjīḥ:** In the cited Ṭabarī passage, if the unit boundary falls between the report list and “والصواب…”, the resulting “والصواب…” excerpt looks like a complete statement but loses the contested alternatives. This is not explicitly prevented by current DP bullets. citeturn17view2turn18file0
- **Uṣūl qiyās macro-structure:** In the cited Waraqāt block, splitting “وأما القياس…” away from “ومن شرط…” produces syntactically valid but semantically dependent excerpts, because the conditioned object is outside. The prompts do not name “ومن شرط…” as a fragment marker, so false FULL/PARTIAL is plausible. citeturn18view0turn18file0
- **Mustalaḥ definitions:** Ibn al-Ṣalāḥ’s ṣaḥīḥ definition is packed with category names; C‑SC‑1 will systematically overestimate “standard terminology” unless calibrated by science/student level. citeturn17view0turn18file0
- **Lemma-based sharḥ:** In the Ṭaḥāwiyya sharḥ structure, the lemma “قوله: …” is essential context; splitting it away yields orphaned explanation with “ما تقدم” style references that can be subtle. citeturn17view6turn18file0
- **Epithet ambiguity:** “الشيخان” cannot be resolved correctly without using *science* as well as school; the enrichment prompt only mentions “الإمام/الشيخ/المصنف,” so scholar resolution will be wrong at scale in both hadith (“متفق عليه”) and fiqh (“قال الشيخان…”) contexts. citeturn17view4turn19view0turn19view1 fileciteturn19file0L1-L1

These are not hypothetical “corner cases”; they are **structural conventions** of classical Arabic scholarly prose and commentary systems, and they align with your own integrity threat model (T‑2/T‑4) in the SPEC. fileciteturn16file0L1-L1