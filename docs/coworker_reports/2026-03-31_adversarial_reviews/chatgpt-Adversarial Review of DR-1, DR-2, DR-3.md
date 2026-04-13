# KR Domain Rules — Adversarial Review of DR-1, DR-2, DR-3

## Sources reviewed and governing constraints

This review is grounded in the adversarial brief, the architect’s proposed domain rules, the architect’s backing analysis, and the excerpt architecture constraints in both the excerpting spec and the vision document. fileciteturn24file0L1-L1 fileciteturn25file0L1-L1 fileciteturn26file0L1-L1 fileciteturn27file0L1-L1 fileciteturn28file0L1-L1

Two architectural constraints are non-negotiable in the current design, and they are the right lens for “is this safe?”:

- **Self-containment is the primary excerpt quality criterion** (a teaching unit must stand on its own for a student with baseline domain familiarity). The excerpting spec defines formal self-containment criteria C‑SC‑1…C‑SC‑5 and explicitly flags “evidence without stating what it is evidence for” as failing argument completeness (C‑SC‑4). fileciteturn27file0L1-L1  
- **Content integrity overrides taxonomic convenience.** The vision document’s excerpt boundary rules explicitly prioritize preserving coherence over splitting for organizational benefits: when splitting would “corrupt” self-containment/coherence, the text stays as one excerpt, even if it spans multiple topics. fileciteturn28file0L1-L1

The proposed DR rules explicitly *change* how Phase 2b grouping behaves by adding DR‑1/2/3 and by **modifying the decontextualization rule DP‑4** (evidence-with-ruling binding) to allow splitting substantive evidence in some cases. That is a direct challenge to one of the excerpting spec’s core “context loss” defenses. fileciteturn25file0L1-L1 fileciteturn27file0L1-L1

## DR-1 definition pair splitting

### Is the **لغوي** unit self-contained without the **شرعي** definition?

**Usually yes, with an important caveat.** The linguistic definition segment often contains: (a) the meaning, (b) usage attestations (“تسمية … معروف”), and (c) sometimes scholarly citations. As a teaching unit, that can be complete on its own if it clearly states *the term being defined* and does not depend on the legal definition for comprehension. The DR‑1 rule is designed to split only when both definitions are substantive, and it adds cross-references between the pair. fileciteturn25file0L1-L1 fileciteturn24file0L1-L1

**Caveat (failure mode):** when the “لغوي” discussion includes a claim whose function is to explain how the legal meaning is derived from the linguistic meaning, then isolating it inside the لغوي unit can create an implicit dependence on the شرعي unit (C‑SC‑4 / C‑SC‑2 risk). The domain rules try to address this by explicitly placing “relationship statements” (e.g., “التعريف الشرعي فرد من…”) into the شرعي unit. fileciteturn25file0L1-L1

**Adversarial point:** DR‑1’s “MUST split if both substantive” may be too rigid. The safe rule is actually: *split if and only if both resulting units can be FULL (or at least PARTIAL repairable) self-contained after moving relationship clauses to the appropriate side*. That conditionality is aligned with the excerpt architecture in the vision doc (split only when you can do so without corrupting coherence). fileciteturn28file0L1-L1

### Is the **شرعي** unit self-contained without the **لغوي** definition, given the backward reference “وفي الشرع …”?

**Not automatically.** “وفي الشرع” is a classic C‑SC‑2 risk: anaphoric framing that presumes the ring-fenced reader already knows (i) the term and (ii) that a paired linguistic definition exists. The DR rules propose resolving this through metadata: ensuring `description_arabic` and/or a `context_hint` makes the target explicit, and cross-references link to the companion unit. fileciteturn25file0L1-L1

**Is a context_hint sufficient?** It can be sufficient *if* the UI/consumer always displays the description/context_hint alongside the primary text (because, in practice, the “excerpt” as consumed includes metadata). The excerpting spec already has a formal mechanism: PARTIAL units get a `context_hint` during enrichment, whereas DEPENDENT units require human review. fileciteturn27file0L1-L1

**Adversarial concern:** DR‑1 implicitly assumes a metadata repair will reliably convert many “وفي الشرع …” units into “usable.” That is plausible, but it raises an architectural question: are you comfortable with the library containing a *systematic class* of excerpts that would be DEPENDENT if read as raw primary text? If you are not, then DR‑1 must require one additional safeguard: the شرعي excerpt’s displayed title/description must repeat the term (“تعريف الصلاة شرعاً…”) and the pipeline must treat any failure to generate that as a gate-worthy defect. This is consistent with self-containment being a first-order integrity defense. fileciteturn27file0L1-L1

### Where should the relationship sentence go: لغوي or شرعي?

The proposed DR‑1 rule is directionally right: a statement like “والتعريف الشرعي فرد من معناه اللغوي العام” is mainly a *scope constraint* on the legal/technical definition, so placing it in the شرعي unit preserves the legal meaning’s internal completeness. fileciteturn25file0L1-L1

**Adversarial nuance:** there are relationship sentences that genuinely teach *both directions* (e.g., “سُمّيت شرعاً كذا لاستعمال العرب كذا”). If you always push them into the شرعي unit, the لغوي unit may lose the explanation of why the linguistic usage matters. If you always keep them with لغوي, the شرعي unit may lose a critical scope statement. The robust approach is to treat “relationship statements” as belonging to whichever side they are *logically needed* to satisfy C‑SC‑4 argument completeness for that side (and if needed by both, you may need duplication in metadata rather than in primary text, to honor primary-text immutability). fileciteturn27file0L1-L1 fileciteturn28file0L1-L1

### Are there cases where لغة and شرعاً are so interdependent that splitting produces two fragments that don’t stand alone?

Yes—at least two patterns should be expected in fiqh/usul writing:

- **Legal definition introduced by contrast** (“ليس المراد به لغةً كذا بل شرعاً كذا…”). Here, removing the linguistic half can leave the legal half semantically dangling (“ليس المراد…” with no antecedent), a direct C‑SC‑2 failure.  
- **A definition whose “meaning” is argued through the relationship** (e.g., the author’s point is precisely that the technical meaning is a constrained subset of the linguistic meaning, and the linguistic discussion is written only to justify that constraining move).

This is exactly the scenario where the vision doc’s “content integrity overrides taxonomic precision” rule should fire: keep the combined excerpt if separation would break self-containment. fileciteturn28file0L1-L1

**Bottom line on DR‑1:** The rule is broadly compatible with the architecture *if it is conditional on self-containment*, rather than unconditional “MUST split.” As written, it risks over-splitting a minority of interdependent definition passages. fileciteturn25file0L1-L1

## DR-2 evidence-type splitting and the DP-4 modification

DR‑2 is the core contested change because it modifies the “Evidence + Ruling must stay together” safeguard, narrowing it to brief/fused/khilaf cases and allowing evidence splitting otherwise. fileciteturn25file0L1-L1 fileciteturn27file0L1-L1

### Is the ~10 word threshold appropriate?

**As a first heuristic, it is defensible—but it is not a scholarly basis.** The adversarial brief itself calls out that the threshold is arbitrary and may be too high (missing useful evidence) or too low (creating trivially thin units). fileciteturn24file0L1-L1

The deeper issue is that **word count is a weak proxy for “unit teaches something.”** In Islamic scholarly writing, an evidence block can be short but conceptually dense (“أجمعوا…”), or long but mostly rhetorical padding. The excerpting spec’s self-containment criteria, especially C‑SC‑4, already encode the real standard: does the unit make a complete teachable move, or is it just a fragment? fileciteturn27file0L1-L1

A safer replacement for the threshold would be a *semantic threshold*:
- split only if the evidence-type segment includes either (a) **an identifiable canonical reference** (verse/hadith) *and* (b) **a minimal “وجه الاستدلال”** (even one sentence clarifying what the evidence is proving), or the excerpt’s own description makes that explicit enough to satisfy completeness in the reader-facing artifact. This aligns DR‑2 with the self-containment standard rather than competing with it. fileciteturn27file0L1-L1

### Case B: “فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات” — is this useful standalone at the leaf “الاستدلال من الكتاب”?

**It is borderline, and you should treat it as a red-flag example.** On its face, it is:
- not teaching why that verse demonstrates permissibility, and  
- not even enumerating the “other verses,” which reduces study value for “side-by-side Quran evidence” comparison.

The domain rules nonetheless treat it as a split-worthy Quran evidence unit and propose representing its purpose via `description_arabic` (e.g., “دليل مشروعية الطلاق…”) and linking back to the ruling excerpt. fileciteturn25file0L1-L1

**Architectural risk:** the excerpting spec states that “an excerpt that presents evidence without stating what it is evidence for cannot be FULL.” If the primary text is as thin as case B, the only way it becomes self-contained is by relying on metadata (description/context) displayed to the user. fileciteturn27file0L1-L1

That can be acceptable in KR *if and only if* the system treats metadata as part of the excerpt artifact always visible in study mode. If there is any mode where a user reads the raw excerpt text without nearby description/context, DR‑2’s outputs will systematically violate the self-containment intent.

**Most important adversarial conclusion for case B:** If your goal is “collect all ayah citations across scholars,” then a better architecture is to keep the ruling+evidence excerpt intact, extract `evidence_refs`, and let the entry (or interface) build the Quran-evidence comparison view from those references. That yields the comparison without storing an evidence-only excerpt whose primary text teaches almost nothing. This alternative is compatible with the vision’s emphasis on entries being the primary study product and on metadata fueling synthesis, while maintaining excerpt integrity. fileciteturn28file0L1-L1 fileciteturn27file0L1-L1

Notably, the backing analysis document argues against “intra-excerpt annotation” and favors splitting, but it frames the alternative as span annotation rather than as “use extracted evidence references + synthesis-level re-organization.” That looks like a missing option in the decision set being defended. fileciteturn26file0L1-L1

### Case C: hadith citation “أبغض الحلال…” — useful standalone, or does it need more context?

**Often it needs more context than just the hadith text.** Here are two concrete reasons:
- **Inferential gap:** how the hadith proves the ruling is not always obvious to a student; some sources may treat it as moral discouragement, not a direct legal proof of permissibility.  
- **Hadith-strength sensitivity:** “evidence” excerpts risk becoming misleading if they omit grading or critical commentary, because the study task is not only “what was cited” but “what counts as proof.”

DR‑2’s current safeguards are (a) “substantive text” threshold and (b) “description_arabic MUST state the ruling supported.” fileciteturn25file0L1-L1

Those safeguards help, but they don’t fully close the gap: **the unit can be self-contained yet still pedagogically misleading** if it reads like a standalone authoritative proof but lacks the source’s own qualification (grading, refutation, context that this is merely “يُستدل به” not “نص صريح”). This is structurally similar to why DP rules exist at all: preventing “looks complete but isn’t” content. fileciteturn27file0L1-L1

**Adversarial conclusion:** hadith evidence splitting is safe only when the evidence segment itself contains the author’s explanatory bridge (وجه الاستدلال) or critical qualifiers, or when the system reliably carries those qualifiers into the evidence unit (e.g., through included commentary sentences that remain with the hadith evidence). Otherwise, keep it bundled with the ruling.

### Evidence categories that may be non-separable even when substantive: can qiyas be standalone?

The adversarial brief correctly points out that **qiyas is structurally entangled with the ruling**: the analogical chain’s conclusion is often the ruling itself. fileciteturn24file0L1-L1

The domain rules attempt to handle this by:
- keeping “syntactically fused” evidence+ruling together, and  
- allowing “evidence_rational” blocks (which might include qiyas elaboration) to exist as a unit that still states the ruling in its description and links back. fileciteturn25file0L1-L1

This is directionally right, but you should assume a real failure mode: **many qiyas arguments are not cleanly “evidence” vs “ruling”; they are a chain where each sentence plays multiple roles**. The backing analysis document explicitly shows examples where boundaries are ambiguous and where sentences serve triple duty (refutation + reinterpretation + evidence), which is exactly why any mechanical “split evidence types” rule will sometimes cut through conceptual joints. fileciteturn26file0L1-L1

### Is modifying DP-4 safe?

**Not as written—only as a narrower, self-containment-gated exception.**

DP‑4 exists because decontextualized evidence is a high-probability corruption path: a verse/hadith appears as “proof” without the claim it proves, violating argument completeness (C‑SC‑4) and creating a misleading study artifact. fileciteturn27file0L1-L1

DR‑2’s modified DP‑4 is safer than “split everything” because it retains DP‑4 for:
- brief mentions,  
- fused syntax patterns, and  
- khilaf contexts governed by DR‑3. fileciteturn25file0L1-L1

However, the modification still creates a systematic class of excerpts whose primary text begins with discourse markers like “فأما الكتاب…” or “وأما السنة…” that are *intrinsically backward-referencing*, triggering C‑SC‑2 reference resolution concerns. The rules expect metadata and cross-references to repair this after splitting. fileciteturn25file0L1-L1 fileciteturn27file0L1-L1

**Why that is insufficient as a safety argument:**
- The vision and excerpting spec treat self-containment as a defining property of the excerpt artifact, not as an optional navigation improvement. fileciteturn28file0L1-L1  
- Cross-references are helpful but, by design, they are not supposed to be *required* for understanding (otherwise you have recreated the “puzzle” risk the owner explicitly warned about in earlier feedback). fileciteturn26file0L1-L1  
- A word-count threshold does not ensure semantic completeness, so it does not ensure DR‑2’s split outputs remain within the “safe” region of C‑SC‑4. fileciteturn27file0L1-L1

**The safe variant of DP‑4 modification** is:
- keep DP‑4 as the default (evidence stays with ruling), and  
- allow splitting only when the engine can ensure the resulting evidence unit is FULL (or at worst PARTIAL repairable) self-contained *without requiring the user to open another excerpt*, meaning the evidence unit’s own displayed content must explicitly state what it is evidence for and not dangle on “فأما/وأما” without resolution.

That’s consistent with the vision’s “content integrity takes absolute priority.” fileciteturn28file0L1-L1

## DR-3 khilaf preservation

DR‑3’s motivation is clear and strong: khilaf passages have high decontextualization risk because refutations and tarjih often reference positions by pronouns (“الأول… هذا القول…”) and evidence can simultaneously support one view and undermine another. fileciteturn25file0L1-L1 fileciteturn24file0L1-L1

### Would a student benefit more from seeing all positions together, or comparing positions separately across sources?

**It depends on the study task, and DR‑3 correctly optimizes for safety first.**

For comprehension and integrity, seeing all positions together often prevents the worst corruption: mistaking a reported view for the author’s endorsed view, or reading a refutation as a standalone proof. This maps directly to the excerpting spec’s rationale for decontextualization prevention. fileciteturn27file0L1-L1

For cross-source comparison, splitting into position-units could help—but that comparison can also be achieved at the entry layer by structuring “scholarly positions” side-by-side while still grounding each position in its full khilaf excerpt(s). The vision document treats entries as the primary study product and explicitly expects entries to surface positions and disagreements. fileciteturn28file0L1-L1

### If split into 3 position-units + 1 tarjih-unit, what is lost? Is dialogue completeness really violated if each position-unit includes the question?

The backing analysis demonstrates why simple “position block extraction” is fragile: tarjih statements can be meta-propositions, and refutations often do double duty (evidence against one view and implicit evidence for another). It also highlights that scholarly writing can fuse topics mid-sentence and use minimal structural markers, making clean splits unreliable in many khilaf-like passages. fileciteturn26file0L1-L1

Even if each position-unit repeats the debated question, you still lose:
- implicit dependencies (e.g., “قولهم ضعيف لأن…” without the referenced claim fully present),  
- meta-level criticisms (e.g., hadith criticism presented as neutral observation), and  
- the argumentative meaning of sequence.

That is exactly what C‑SC‑5 (dialogue completeness) is meant to protect: responses must retain enough of what they respond to so the response is intelligible and not misleading. fileciteturn27file0L1-L1

### The ~800-word threshold: what scholarly basis exists? Should it be based on number of positions?

As an explicit number, **800 words has no scholarly basis in the provided documents**; it’s a pragmatic heuristic. fileciteturn24file0L1-L1 fileciteturn25file0L1-L1

A better basis is structural dependence, not length:
- number of positions is relevant, but  
- more important is whether refutations/tarjih rely on “this/that/first/second” pronouns, and whether evidence is used comparatively.

The domain rules partially acknowledge this (“pronoun refutation markers” as rationale). fileciteturn25file0L1-L1  
So the adversarial recommendation is: replace the 800-word rule with a dependency-aware rule that checks for the markers DR‑3 already lists (tarjih markers, refutation markers, implicit pronouns) and splits only when position blocks are explicitly attributed and internally complete. fileciteturn25file0L1-L1

### Are there short khilaf passages where splitting is appropriate?

Yes. A short “khilaf” can be:
- a simple list of positions with no refutation, no tarjih, and each position stated as a self-contained claim with a distinct scholar attribution and its own evidence paragraph.

In those cases, splitting could still satisfy C‑SC‑5 if each unit contains enough of the question and the scholar’s claim. The core point is that “khilaf” is not a magic word; it’s a discourse structure. DR‑3 should key off structure, not only the presence of “اختلاف العلماء” headings. fileciteturn24file0L1-L1 fileciteturn25file0L1-L1

## Cross-genre applicability

The adversarial brief explicitly requires assessing whether DR‑1/2 generalize beyond fiqh (nahw, usul, balagha). fileciteturn24file0L1-L1

### Nahw: do Quranic/poetic شواهد behave like “evidence categories”?

Often **no**. In nahw, a شاهد verse is frequently meaningless without:
- the grammatical rule it instantiates, and  
- the iʿrāb/parsing demonstration (which is neither “evidence” nor “proposition” in a simple two-category sense).

The backing analysis explicitly notes that nahw teaching passages are a triad (rule + شاهد + iʿrāb) and that separating these breaks the pedagogy. fileciteturn26file0L1-L1

**Adversarial implication:** DR‑2 should not be globally applied as “split evidence types wherever detected” across sciences. At minimum it should be scoped to fiqh/usul/hadith genres where evidence categories are a conventional decomposition axis, and even there it should remain conditional on self-containment.

### Usul: does a “substantive threshold” for rational arguments make sense?

Usul frequently argues via reasoning chains about reasoning; the “evidence” is not a discrete citation block but a structured argument. The backing analysis flags that in usul “one paragraph → multiple leaves” and that “evidence” often blurs with the claim. fileciteturn26file0L1-L1

So a word-count-based DR‑2 threshold is particularly miscalibrated here. If you want finer granularity for usul, you likely need different domain rules (or a synthesis-level organization strategy), not DR‑2 as currently defined.

### Balagha: can rhetorical analysis be separated from what it demonstrates?

In many cases **no**—the analysis is the knowledge, and the cited text is simultaneously the object of study and the evidence of the phenomenon. The backing analysis makes this explicit: “Analysis IS the knowledge… no proposition/evidence boundary exists.” fileciteturn26file0L1-L1

Therefore, treating balagha examples as DR‑2 “evidence” candidates risks producing fragments.

### Are there sciences where DR‑1 should not apply?

Yes: any science where the “لغة/شرعاً” dichotomy is not a live convention. DR‑1 is premised on a domain convention in fiqh and related Islamic sciences. Applying it blindly elsewhere can create artificial splits or force cross-references that do not reflect how the discipline conceptualizes terms. The domain rules implicitly assume universality (“universal convention across all fiqh books”), but that is narrower than “across all sciences.” fileciteturn25file0L1-L1

## Overall assessment and recommendation

### Does DR-1 + DR-2 + DR-3 (plus modified DP-4) produce the right balance?

**DR‑1 and DR‑3 are broadly aligned with the architecture, while DR‑2 is not safe as a general modification to DP‑4.**

- **DR‑1 (definitions):** plausible and often correct, *if made conditional on self-containment*. The vision excerpt rules explicitly allow splitting when both parts become self-contained excerpts; they also explicitly forbid corrupting coherence for organizational benefit. DR‑1 must reflect that conditionality to be architecturally clean. fileciteturn28file0L1-L1 fileciteturn25file0L1-L1  
- **DR‑3 (khilaf):** strongly justified; it preserves the exact structure most likely to cause context-loss corruption if split. This is aligned with the excerpting spec’s emphasis on decontextualization prevention and with the backing analysis’s examples of refutation/tarjih ambiguity. fileciteturn27file0L1-L1 fileciteturn26file0L1-L1 fileciteturn25file0L1-L1  
- **DR‑2 (evidence splitting):** addresses the owner’s desire for per-evidence-type comparability, but it does so by weakening DP‑4 using a heuristic threshold and relying on cross-references/metadata to repair inherent backward references (“فأما/وأما”). That creates a systematic class of excerpts at risk of failing C‑SC‑2 and C‑SC‑4 unless the UI guarantees rich metadata display and unless the split evidence blocks actually contain “teaching,” not just citation pointers. fileciteturn27file0L1-L1 fileciteturn25file0L1-L1 fileciteturn24file0L1-L1

### Failure modes to expect if DR-2 is implemented as written

These are the highest-probability failure modes given the documents:

- **Thin “evidence stubs” that do not teach.** Case B is the canonical example: it names one verse and waves at others. This will inflate excerpt counts without proportionate study value and risks polluting “evidence leaves” with low-signal units. fileciteturn24file0L1-L1 fileciteturn25file0L1-L1  
- **Self-containment drift from FULL to systematic PARTIAL.** If the split evidence units repeatedly require `context_hint` repairs for “فأما/وأما” discourse markers, you’ve effectively introduced a large class of “metadata-dependent” excerpts. That may be acceptable, but it is a conscious quality tradeoff and should be measured and gated, because the excerpting spec treats self-containment as the primary quality criterion. fileciteturn27file0L1-L1  
- **Genre misapplication.** Applying DR‑2 to nahw/balagha/usul patterns risks fragmenting rule-example-analysis triads. fileciteturn26file0L1-L1  
- **Cross-reference brittleness.** DR‑2 relies on Phase 3 enrichment to create semantic cross-references between split companions and even proposes a schema extension. Any linking error reintroduces the “puzzle corruption” risk the owner fears. fileciteturn25file0L1-L1 fileciteturn26file0L1-L1

### What’s missing from the rule set

The biggest missing structure is: **a self-containment gate** that can override “when in doubt, split.”

The domain rules’ governing principle says: “Over-granularity is safe… therefore, when in doubt, split.” fileciteturn25file0L1-L1  
But the vision excerpt architecture says the opposite risk ordering at boundary decisions: “content integrity takes absolute priority,” and you do not split if it would break coherence. fileciteturn28file0L1-L1

So the missing rule is: *splitting is permitted only if both resulting units can satisfy self-containment (FULL, or PARTIAL with an explicit, reliable repair path); otherwise keep them together.*

### Concrete recommendation

Your earlier recommendation (“don’t split evidence; do comparison via synthesis”) **still holds for DR‑2**, with one important concession: **DR‑1 definition splitting is likely worth adopting** (with a self-containment condition), and **DR‑3 khilaf preservation should absolutely remain**.

More concretely:

- **Adopt DR‑1, but soften “MUST” into “MUST unless splitting breaks self-containment.”** This makes DR‑1 consistent with the vision’s boundary rules and prevents interdependent definition fragments. fileciteturn25file0L1-L1 fileciteturn28file0L1-L1  
- **Keep DR‑3, but replace the 800‑word heuristic with a structure-based criterion.** Use the dependency markers DR‑3 already lists (pronouns, refutation/tarjih coupling) as the actual trigger for “do not split,” and allow splitting only when positions are explicitly attributed, internally complete, and minimally interdependent. fileciteturn25file0L1-L1  
- **Do not weaken DP‑4 globally.** If you want DR‑2 at all, implement it as a narrow exception that requires evidence units to be self-contained without requiring navigation to the ruling excerpt—meaning the evidence unit must explicitly state the supported ruling in its own student-facing artifact, and must include at least minimal “وجه الاستدلال” when the citation is not self-explanatory. Otherwise, preserve DP‑4 as originally specified. fileciteturn27file0L1-L1 fileciteturn25file0L1-L1  
- **Meet the owner’s comparison goal at the entry/interface level rather than via excerpt storage splits.** The vision document elevates entries to the primary study artifact and expects them to faithfully represent “evidence” and “positions.” Build the “Evidence from Quran / Sunnah / Ijma / Qiyas” comparison view as a structured entry section backed by evidence references, without creating evidence-only excerpts that are pedagogically thin. fileciteturn28file0L1-L1

This recommendation preserves DP‑4’s safety function while still delivering the owner’s study workflow—side-by-side evidence comparison—through the layer the architecture already intends for deep organization: the entry.