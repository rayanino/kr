# Adversarial Review of Excerpting Foundations

## What I could and couldn’t verify in the specified files

The central bottleneck for an exact “FP‑1 … FP‑12” adversarial review is that (in the currently accessible refs of the selected repos) the excerpting spec *does not* appear to contain the requested labeled sections “§1.1b — Foundational Principles” (FP‑1 … FP‑12) nor “§6.4b — Explained‑Explanation Unity” (EE‑1) as named in your task. The excerpting spec that is present defines a different (but still foundation-like) structure: explicit **self-containment criteria** (C‑SC‑1 … C‑SC‑5) and multiple **domain rule families** (for example: decontextualization prevention, multi-layer attribution, evidence integrity, implicit reference resolution, verse-commentary unity, quoted-material integrity). fileciteturn16file0L1-L1

Similarly, the specific ledger file path you named (`engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md`) did not appear to be fetchable at that path in the selected repos at the refs examined; I therefore could not incorporate a “ledger-backed” audit trail of the foundations as requested.

Given that, the rest of this report does two things:

- It **anchors claims in what *is* present** in the repo files: excerpting self-containment criteria + domain rules + older excerpting spec material + campaign analyses and adversarial reviews. fileciteturn16file0L1-L1 fileciteturn38file0L1-L1 fileciteturn47file0L1-L1 fileciteturn50file0L1-L1  
- For your FP‑8 / FP‑12 questions, it **treats your descriptions of FP‑8 (“separate khilaf and tarjih”) and FP‑12 (“watch for taqdir/implied dependencies”) as “requirements statements”**, then stress-tests how such requirements collide with proven genre realities in Arabic scholarly writing (especially the “intra-excerpt reality check” findings). fileciteturn47file0L1-L1

## Failure modes these foundations cannot prevent

Even with strong “unit integrity” principles (keep what belongs together; preserve attribution; avoid fragmentation) and strong self-containment criteria, there are failure classes that are structurally outside what “excerpt boundary principles” can guarantee. Below are concrete gaps, each with an Arabic scenario and why the foundations (as currently specified/illustrated in repo artifacts) won’t reliably block them.

1) **Upstream text corruption (OCR / normalization) that changes meaning**  
Scenario: OCR (or normalization) silently flips a word that controls epistemic status:  
> “**قِيلَ**: يجوز …” becomes “**قالَ**: يجوز …”  
The excerpt may become perfectly self-contained *but false*, because the pipeline is now grounded on corrupted primary text. Excerpting rules can preserve “verbatim assembly,” but they cannot detect corruption if upstream already froze the wrong string. This risk is explicitly recognized as existential at the domain level (quality is existential; corruption propagates). fileciteturn39file0L1-L1

2) **Layer mis-detection (matn/sharh/hashiyah/tahqiq) that collapses authorship**  
Scenario (classical pattern):  
> “قال المصنف: …” (matn author)  
> “قال الشارح: …” (commentator)  
If upstream layer tagging is wrong (or absent), excerpting can apply “keep together” (explained + explanation unity) and still attribute the combined unit to the wrong voice. Multi-layer handling rules exist, but they *depend on correct upstream layer signals*; they don’t create those signals. fileciteturn16file0L1-L1 fileciteturn39file0L1-L1

3) **Rhetorical objection–response voice shifts (فإن قيل / قلنا) misread as authored doctrine**  
Scenario (ubiquitous in usul, kalam, advanced sharh):  
> “فإن قيل: كيف يصح …؟ قلنا: …”  
If excerpting produces only the objection (or treats it as “a stated position”), you get a self-contained unit that teaches the *opponent’s* claim as the author’s view. “Decontextualization prevention” examples in the older excerpting spec are mostly about *named scholar reports* (“وقال أبو حنيفة…”), not about *constructed interlocutor turns*. So a “separate khilaf/tarjih” style principle doesn’t necessarily cover “separate objection/answer.” fileciteturn38file0L1-L1

4) **Meta-textual hadith criticism/riwayah commentary that is neither proposition nor evidence**  
Scenario (mirrors the taysir analysis):  
> “وهذا الحديث في مسلم بدون قوله: … وقد استنكر العلماء هذا الحديث…”  
This chunk isn’t cleanly “evidence” nor “claim”; it’s *evidence provenance critique*. If a boundary principle tries to split “evidence excerpts” away from “ruling excerpts,” it may strand such material in the wrong place (or create garbage units). The campaign analysis explicitly shows these sentences breaking simplistic span/category schemes and carrying “critical” argumentative force indirectly. fileciteturn47file0L1-L1

5) **Syntactic fusion of ruling and proof that cannot be split without breaking Arabic grammar**  
Scenario (observed as a boundary case):  
> “قوله {…} **دليل على أنه** لا يجوز …”  
Here, the evidence text and ruling are one grammatical unit (subject–predicate style), so any “granularity” principle that enforces separation will produce linguistically bleeding fragments. This is not hypothetical; it’s called out as a structural boundary case in the taysir analysis. fileciteturn47file0L1-L1

6) **Cross-passage dependency when passaging boundaries are wrong**  
Scenario (frequent in fiqh debates): passage N ends with:  
> “واحتجوا بحديث …”  
and passage N+1 begins with:  
> “ولنا … فالراجح …”  
If excerpting is constrained by a “passage containment” invariant (the excerpt must not cross passages), then no amount of intra-passage “keep together” can restore the complete dialectical unit when the needed continuation is in the next passage. The older excerpting spec explicitly treats “refutation split across passage boundary” as a decontextualization-risk test case. fileciteturn38file0L1-L1

7) **Implicit consensus / “silent majority” not overtly stated in text**  
Scenario: a book states only minority disputes because the default is assumed (e.g., the author only says “وخالف فلان…” without ever stating the baseline). Excerpting principles can’t extract what isn’t there; this becomes a coverage/representation bias problem downstream. The domain primer flags “silent majority” as a core scholarly integrity risk. fileciteturn39file0L1-L1

8) **Ellipsis / taqdir that requires *unwritten* content to interpret correctly**  
Scenario:  
> “والأول أظهر، **لِما تقدم**”  
or  
> “وفيه نظر”  
The missing referent isn’t a named entity; it’s a whole implied argument or premise. Even perfect C‑SC‑2-style reference resolution can fail if the dependency is not resolvable from any explicit antecedent inside the excerpt. Arabic rhetoric and syntax treat حذف/إضمار as routine, especially in technical prose. fileciteturn39file0L1-L1 citeturn0search1turn0search6

9) **Embedded tarjih that functions as a “meta-proposition” mid-discussion**  
Scenario:  
> “… وهذا ضعيف، **والصحيح** كذا، لأن …”  
The tarjih sentence is simultaneously: (a) judgment on positions, (b) conclusion, and (c) often a bridge into further refutation. If principles mandate “tarjih separate from khilaf,” they cannot enforce clean separation when the author himself did not separate it (the discourse act is grammatically integrated). The taysir analysis calls this out explicitly (“tarjih as meta-proposition”). fileciteturn47file0L1-L1

10) **Genre shift inside one paragraph (fiqh → usul maxim → hadith criticism) that defeats rigid unit schemas**  
Scenario (compressed fiqh writing):  
> “والراجح … لأن… وهذا الحديث لا يصح … والقاعدة …”  
A “unit” can be coherent for a scholar but not align with any one taxonomy leaf cleanly. This is exactly the “multi-category” problem the campaign analysis quantifies: most excerpts include multiple content types, so unit schemas that assume separability fail at scale. fileciteturn47file0L1-L1

11) **Multi-leaf semantics: one teaching paragraph supplies multiple leaves simultaneously**  
Scenario: balagha definition paragraphs often encode multiple definitional constraints; splitting may be necessary for leaf coverage, but splitting can destroy integrity. Campaign analysis argues “under-granularity is not recoverable; under fine leaves there is no data,” while also showing that splitting can mutilate language. This is a structural impossibility triangle, not a missing rule. fileciteturn47file0L1-L1 fileciteturn50file0L1-L1

12) **Ambiguous “speaker” with weak attribution signals (قيل / ذكر / روي / حكي) in dense prose**  
Scenario:  
> “ورُوي عن بعضهم …” / “حُكي …” / “قيل …”  
Even if extracted as a coherent unit, the engine may not be able to resolve “who exactly holds this” without external scholarly knowledge or explicit context absent from the passage. The older excerpting spec handles some implicit references (“الإمام…”) by registry + context, but “قيل” chains often remain underdetermined. fileciteturn38file0L1-L1

**Bottom line:** the foundations (even if perfectly enforced) can guarantee *some combination* of: contiguity, self-containment, attribution hygiene *given upstream correctness*, but they cannot guarantee correctness under upstream corruption, cannot extract unstated defaults, and cannot always reconcile structural impossibilities (syntax-fused evidence/ruling, multi-leaf semantics, embedded meta-discourse).

## Where foundational principles will conflict in real Arabic texts

Because the “FP-1 … FP-12” list isn’t directly visible in current repo text, I’m going to name the *conflict axes* that are clearly present in the repo’s excerpting debates and that match your FP‑1 vs FP‑9 example: “unity/keep-together” versus “avoid overgranulation / achieve leaf-level granularity.”

### Unity vs granularity (the core contradiction)

**Real-text trigger:** Arabic scholarly writing frequently fuses multiple pedagogically separable units into one syntactic flow (especially via **و**, **فـ**, **ثم**, **لأن**, **فإن**). The taysir analysis shows cases where two different masā’il are fused mid-sentence with a simple conjunction, making “keep together” and “split cleanly” simultaneously hard. fileciteturn47file0L1-L1

**Concrete conflict pattern:**  
- If you “keep together” to preserve argumentative structure (especially in khilaf), you end up with a unit that is too broad for leaf-level comparison (overgranulated excerpt).  
- If you “split” to serve the tree (fine leaves), you often produce linguistically broken fragments or lose the dialectical arc.

This is exactly the disagreement between the “calibrated fine-grained excerpting” recommendation in the campaign analysis and the Gemini adversarial critique that warns splitting yields orphaned conjunctions (e.g., “فأما…”, “وفي الشرع…”) and violates textual integrity for the student reader. fileciteturn47file0L1-L1 fileciteturn50file0L1-L1

### Evidence separation vs “evidence needs the ruling to be meaningful”

**Real-text trigger:** many evidence phrases are *deictic or elliptical* (“فأما الكتاب فنحو…”, “واستدلوا بحديث الباب…”) and depend on the ruling statement and the disputed question for meaning. fileciteturn49file0L1-L1

If principles require “evidence units” for cross-source comparison, they will conflict with self-containment: an ayah citation alone is often missing **وجه الدلالة** (how it proves the ruling). Gemini’s review argues metadata can patch the graph but not the pedagogical integrity of the Arabic fragment. fileciteturn50file0L1-L1

### Khilaf/tarjih separation vs authorial style that embeds tarjih inside narration

**Real-text trigger:** “tarjih as meta-proposition” appears as a clause inside refutation chains, not as a clean final paragraph (“ولكن الأرجح …”). fileciteturn47file0L1-L1

So a “separate khilaf from tarjih” principle conflicts with “don’t mutilate grammar / don’t orphan discourse particles.” In practice you must choose: (a) violate strict separation, or (b) violate textual integrity.

### “Explained-explanation unity” vs multi-layer attribution integrity

Even without the missing EE‑1 label, the repo’s excerpting logic clearly wants “keep explanation with explained text” (e.g., verse + commentary). fileciteturn16file0L1-L1  
But when the explained thing is in one layer (matn) and the explanation is in another (sharh/hashiyah), the same “keep together” action can create mixed-layer excerpts that require careful attribution handling, review flags, and sometimes separation of editor/tahqiq commentary. fileciteturn38file0L1-L1

### Practical resolution heuristic (what must dominate what)

If you want a deterministic outcome (and not oscillation), conflicts need a precedence stack. Based on the repo’s integrity posture (“KR is knowledge; errors are existential”), the precedence that minimizes irreversible corruption is:

1. **Speaker-role correctness (who is endorsing what)**  
2. **Dialogue completeness when omission flips meaning (refutation, objection-response, khilaf arcs)**  
3. **Textual/grammatical integrity of the extracted Arabic (avoid “bleeding” fragments)**  
4. **Self-containment for the target reader**  
5. **Granularity for leaf-level comparison**

This precedence aligns with: (a) the domain primer’s “secure by design” posture and decontextualization risk focus, and (b) Gemini’s warning that semantic graph fixes don’t automatically produce pedagogically valid Arabic units. fileciteturn39file0L1-L1 fileciteturn50file0L1-L1

## Mid-argument tarjih when the author embeds it inside dispute narration

You specified FP‑8 as: **khilaf and tarjih should separate**, and asked what to do when tarjih occurs *mid-argument*.

The campaign analysis already shows why this is the norm rather than the exception: refutation, reinterpretation, and preference statements can do “triple duty,” and tarjih often appears as a clause inside a refutation chain (“tarjih as meta-proposition”). fileciteturn47file0L1-L1

### Why “always split tarjih” fails mechanically

Mid-argument tarjih is often:

- syntactically attached (و / لكن / بل / فـ),
- dependent on immediate preceding evidence,
- phrased as an evaluation that presupposes the dispute context (“والصحيح…” / “لِقوّة الدليل…”).

If you split it, you risk producing the same kind of “orphaned” fragments Gemini warned about for “فأما…/وفي الشرع…”, just at the discourse level rather than the conjunction level. fileciteturn50file0L1-L1

### A robust handling strategy: “tarjih anchoring” instead of “tarjih extraction”

The excerpting engine should treat tarjih markers as *internal structure signals* that influence boundaries, not as guaranteed boundary points.

A workable approach in three passes:

**Detection pass (cheap + high recall):** detect common tarjih lexemes and evaluative templates:  
- “والراجح / الأرجح / الصحيح / الأصح / المعتمد / الأقوى / المختار / الذي عليه العمل …”  
- plus negative-weighting templates: “هذا ضعيف / لا يصح / فيه نظر …”

**Scope pass (local syntax + discourse):** decide whether the tarjih clause is:
- **standalone** (new sentence/paragraph, often followed by closure like “والله أعلم”), or
- **embedded** (mid-sentence, inside a refutation, or followed by continued dialectic).

**Action pass (boundary policy):**
- If **standalone** and the preceding khilaf block is structurally complete, you may produce:
  - one **khilaf unit** (positions + evidences + refutations as needed), and
  - one **tarjih unit** that includes *the minimal context required to interpret the preference* (usually: the mas’ala question + a compressed pointer to the compared positions), plus cross-references linking the two.
- If **embedded**, you keep it *inside* the khilaf unit, but you **surface it as structured metadata**:
  - tag the specific sentence/atom span as `argument_role = weighing_preference` (or equivalent),
  - optionally also store `preferred_position_ref = (position_id / school / scholar)` if extractable.

This is consistent with the older excerpting spec’s longer-term direction: “argumentative discourse mapping” (mas’ala → positions → evidences → discussion → tarjih → conclusion) as a separate analytic capability, which is exactly what mid-argument tarjih needs. fileciteturn38file0L1-L1

**Crucial nuance:** separating “tarjih” from “khilaf” can be achieved in the **knowledge graph/UI layer** (a dedicated “tarjih view” derived from a larger excerpt) without physically splitting the primary Arabic text into damaged fragments. This directly addresses the “graph logical soundness vs linguistic/pedagogical integrity” split raised by Gemini. fileciteturn50file0L1-L1

## Taqdir in real Arabic scholarly text and whether C‑SC‑2 is enough

You asked: how common is implied dependency (taqdir) in real Arabic scholarly writing, and whether “C‑SC‑2 expansion” is sufficient or needs a dedicated detection mechanism.

### How common is taqdir / ellipsis?

At the domain level, the repo explicitly frames ellipsis (الحذف والإضمار) as routine Arabic behavior and as *especially salient in classical terse scholarly texts*, giving an example where a short title (“باب الفاعل”) implies several missing words. fileciteturn39file0L1-L1

External linguistic and computational literature supports that ellipsis/null arguments are not corner cases in Arabic:

- Arabic NLP surveys and task papers repeatedly list **ellipsis / dropped pronouns / null arguments** as core challenges for coreference and discourse understanding. citeturn0search0turn0search3  
- In Arabic rhetoric, ellipsis (الحذف) is treated as a standard device under “brevity vs verbosity” considerations, i.e., it is not exceptional; it is part of normal high-style writing. citeturn0search6  
- Arabic discussions of “الحذف والتقدير” define it precisely as the omission of syntactically relevant material assumed by context—again treating it as regular practice rather than rare anomaly. citeturn0search1turn0search2

**Operational takeaway:** in the subset of texts you care about (classical/middle Arabic scholarly prose + commentaries), taqdir should be treated as “frequent enough to deserve first-class instrumentation,” not as a once-per-book exception.

### Is C‑SC‑2-style reference resolution sufficient?

If C‑SC‑2 is scoped as “resolve explicit references” (pronouns, demonstratives, “هذا/ذلك/فيه/عليه”, implicit scholar epithets like “الإمام”), then it is necessary but *not sufficient* for taqdir.

Reason: taqdir often creates dependencies with **no surface token to resolve**. A pronoun resolver can’t recover an omitted predicate; a cross-reference resolver can’t point to a missing clause that was never written. This is the sharp boundary between “anaphora” and “ellipsis.”

You can see adjacent evidence of this at the campaign level: a large share of excerpts include embedded reasoning with لأن (≈26% in the taysir corpus stats), which is a common surface manifestation of “unstated premise depends on prior discourse.” That’s not identical to taqdir, but it’s a reliable proxy for “intra-unit dependency density is high.” fileciteturn47file0L1-L1

### What you need instead: a dedicated taqdir-risk detector (not necessarily a full expander)

To be blunt: if FP‑12’s goal is “don’t produce units that only make sense after the reader silently supplies missing prerequisites,” then you need more than C‑SC‑2.

A practical design is a **taqdir-risk detection mechanism** integrated into self-containment evaluation:

- **Signal:** “unit requires an implied clause/definition/premise that is not recoverable from explicit antecedents inside the unit.”
- **Action:** (a) expand the unit boundary *within the passage* to include the missing anchor, or (b) attach an explicit “context_hint / taqdir_hint” analytic field (clearly marked as non-verbatim) + review flag.

This pairs well with the repo’s insistence on preserving primary text verbatim while still enabling “self-containment repair suggestions” or context enrichment strategies. fileciteturn16file0L1-L1 fileciteturn38file0L1-L1

A minimal v1 detector can be LLM-based (because taqdir is semantic), but it should output *structured, testable artifacts*:

- boolean `taqdir_risk`,
- extracted “missing piece type” (missing definition / missing antecedent argument / missing subject-of-verb / missing scope condition),
- suggested anchor span if present nearby.

That makes hardening measurable (you can build a gold set of “taqdir traps”) rather than vibes-based.

## The single most dangerous blind spot

Given the repo’s stated integrity stance (“a bad excerpt is a bad piece of knowledge”), the most dangerous blind spot is the one that can create **confident, self-contained, linguistically intact units that teach the wrong epistemic status of a claim**—because those are hardest for downstream systems (and humans) to detect.

The highest-risk candidate is:

**Speaker-role inversion in dialogic/rhetorical structures** (objection–response, hypothetical interlocutor, “قيل/فإن قيل/قلنا/الجواب”, and similar constructs), especially in usul/kalam/advanced commentaries.

Why this is more dangerous than (say) overgranulation:

- Overgranulation is noisy and often correctable (merge later).  
- Speaker-role inversion is **quiet**: the excerpt can look beautiful, coherent, and self-contained—and be exactly wrong about what the author endorses.

The existing decontextualization framing (in older excerpting spec and the domain primer) focuses heavily on “scholar A reports scholar B but disagrees,” which is critical, but rhetorical interlocutor structures can produce the same corruption *without any scholar names at all*. fileciteturn38file0L1-L1 fileciteturn39file0L1-L1

### What to add (if you were to harden the foundations)

A single additional foundation-level rule closes a disproportionate amount of risk:

**Always keep objection and answer together, and explicitly label which voice is which.**

Concretely:

- detect objection markers (“فإن قيل”, “فإن قلت”, “قال قائل”, “اعترض”, “يقال”),
- require the adjacency of an answer marker (“قلنا”, “فالجواب”, “وأجيب”, “قلت”),
- refuse to emit an excerpt that contains an objection without its answer unless it is explicitly marked as “unanswered question posed by author” (rare but real).

This is the same pattern of structural prevention already advocated for other corruption paths (fail-loud, preserve provenance, prevent misattribution structurally), just applied to a different and extremely common classical discourse form. fileciteturn39file0L1-L1