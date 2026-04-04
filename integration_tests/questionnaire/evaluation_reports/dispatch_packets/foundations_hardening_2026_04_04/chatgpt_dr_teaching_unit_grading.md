# Grading Excerpting Teaching Units for باب المسح على الخفين

## Sources and what I could not locate

This assessment is grounded in the excerpting engine’s formal definition of a “teaching unit,” its self-containment standard, and its boundary rules for fiqh/hadith commentary patterns as specified in `engines/excerpting/SPEC.md`. fileciteturn21file0L1-L1

For the concrete 10-unit output, I used the Phase 2b grouping artifact in `integration_tests/smoke_api_v2/taysir/phase2b_groupings/chunk_div_src_test0001_6_004.json`, which includes unit boundaries (start/end word offsets), function labels, Arabic descriptions, and self-containment judgments/notes. fileciteturn34file0L1-L1

Two repo-navigation mismatches matter for interpreting your instructions:

- In the version of `SPEC.md` I retrieved, there are sections `§1.1` and `§6.4`, but I do not see literal section markers spelled “§1.1b” or “§6.4b.” I therefore keyed to the nearest relevant content: the `§1.1` “What This Engine Does” definition of teaching units, and `§6.4` “Implicit Reference Resolution” (plus the grouping prompt rules that operationalize boundary behavior). fileciteturn21file0L1-L1  
- The file path `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md` was not found in the accessible repo state. I attempted direct retrieval by path and also searched by filename tokens; I did not locate a file with that exact name/path. Because of that, “FOUNDATIONS_HARDENING_LEDGER” could not be used as an additional authority layer, and the evaluation relies on `SPEC.md` + the actual grouping output file. (This is a real limitation: if that ledger exists on another branch/commit, it may contain extra rules about minimum viable unit size, boundary exceptions, or pedagogical packaging.)

## Grading rubric anchored to the SPEC

### What “study-readiness” means here

Per the SPEC, a teaching unit is supposed to be “the smallest segment of text from which a student can learn a complete scholarly thought,” such as a ruling with its evidence, a definition, or a position with refutation. fileciteturn21file0L1-L1

The SPEC’s self-containment standard operationalizes this with five criteria (term resolution, reference resolution, evidence completeness, argument completeness, dialogue completeness) and three outcome levels: FULL / PARTIAL / DEPENDENT. fileciteturn21file0L1-L1

So, I treated “study-readiness” as: *Would a student of fiqh benefit from studying this unit in isolation without silently importing missing context?* That is stricter than “can be read,” and it penalizes units that are (a) pure cross-reference, (b) too short to carry their own inferential justification, or (c) labeled PARTIAL for reasons that matter pedagogically.

### The 1–5 scale

- **5 (Highly study-ready):** FULL self-containment *and* the unit is a clean “complete thought” with enough internal grounding that studying it alone won’t mislead.  
- **4 (Study-ready with minor friction):** Either FULL but compressed / multi-claim, or PARTIAL where the missing context is small and easily repaired (e.g., with a context hint or a merge).  
- **3 (Marginal standalone value):** Some learning value, but the unit is either overly terse, bound too tightly to adjacent evidence, or “PARTIAL” in a way that undermines standalone study.  
- **2 (Low standalone value):** Studying it alone likely produces confusion or ungrounded memorization; best treated as an attachment/merge rather than a standalone unit.  
- **1 (Not a teaching unit in practice):** Essentially metadata-only (e.g., a bare cross-reference) or structurally too fragmentary to function as independent study material.

One more important spec anchor for boundary decisions: the Phase 2b grouping prompt explicitly instructs that “Derived Benefits” sections beginning with **ما يؤخذ من الحديث** should be split per numbered item, each numbered benefit becoming its own teaching unit. fileciteturn21file0L1-L1  
At the same time, the SPEC explicitly flags over-segmentation as a known risk and does *not* commit to a minimum unit size; it proposes that any minimum-size enforcement (if adopted later) should occur as a **post-grouping merge** step rather than as a grouping-prompt constraint. fileciteturn21file0L1-L1

## Per-unit grades for study-readiness

All factual unit properties below (word ranges, self-containment, primary_function, and the Arabic descriptions/snippets/notes) come from the Phase 2b grouping output. fileciteturn34file0L1-L1

| TU | Words | Primary function | Self-containment | Grade | Would a fiqh student benefit from studying it alone? | Main reason |
|---|---:|---|---|---:|---|---|
| TU-0 | 70 | editorial_note | FULL | 5 | Yes | Chapter introduction framing legitimacy of wiping + refutation of deniers is a complete “setup + stance” unit and matches the “complete thought” definition well. |
| TU-1 | 102 | evidence_hadith | FULL | 5 | Yes | Hadith + شرح لفظه + المعنى الإجمالي is a classic hadith-commentary micro-module; FULL suggests the necessary context is inside the unit. |
| TU-2 | 140 | opinion_statement | FULL | 4 | Yes, but it’s denser | A compact “ikhtilāf + response + tarjīḥ” bundle is still studyable, but it is multi-part and slightly above the typical mid-range size. |
| TU-3 | 26 | rule_statement | FULL | 4 | Yes | “مشروعية المسح … + كيفية المسح” is short but still a coherent rule-level takeaway without dangling references. |
| TU-4 | 16 | rule_statement | FULL | 4 | Yes (as a crisp rule) | Very short but it states a high-signal condition (“لبس الخفين على طهارة”) clearly enough to function as a standalone rule card. |
| TU-5 | 5 | rule_statement | PARTIAL | 2 | Weakly; mostly memorization | The unit is semantically clear (“استحباب خدمة العلماء والفضلاء”) but the file’s own notes say the وجه الاستنباط from the prior hadith is missing inside the unit. That’s a real standalone-study gap. |
| TU-6 | 14 | cross_reference | PARTIAL | 1 | No (as standalone) | It’s basically a narration-pointer (“في بعض روايات هذا الحديث… تبوك”) and explicitly depends on the prior hadith reference; this functions better as metadata attached to TU-1 than as an independent study unit. |
| TU-7 | 44 | evidence_hadith | PARTIAL | 3 | Somewhat, but imperfect | The unit is explicitly marked PARTIAL because the hadith is quoted مختصرًا; for hadith-based study, “abbreviated citation” is a meaningful completeness loss. |
| TU-8 | 41 | rule_statement | FULL | 4 | Yes | Travel wiping + duration rules + when counting begins are tightly related; this is dense but still a coherent ruling bundle. |
| TU-9 | 70 | rule_statement | FULL | 5 | Yes | A substantial rule/exception package (event scope: الحدث الأصغر, exclusions, related cases like الجبيرة) is a very typical “complete thought” study unit. |

A key correction versus your summary: in the concrete grouping file, TU-5 is **PARTIAL** (not FULL), TU-7 is **PARTIAL** (not FULL), and TU-8 is **FULL** (not PARTIAL). fileciteturn34file0L1-L1

## Boundary analysis of the specific questions

### TU-2 size and whether disagreement should be split

**Is 140 words too large?**  
Not inherently. The SPEC gives empirical reference points: typical unit sizes in experiments clustered around ~80–90 words median, with observed averages spanning roughly 45–126 words depending on format, and it explicitly treats over-segmentation as a real risk. fileciteturn21file0L1-L1  
A 140-word unit is “large-ish” relative to the median, but still within a normal human study chunk, especially if it is one coherent argument.

**Should individual opinions have been separate units?**  
Only if the text structure genuinely supports *opinion → evidence → response* as separable “complete thoughts.” The SPEC’s core grouping rule says “a position + its evidence + counter-evidence + conclusion = one unit,” and decontextualization rules require that reported positions and refutations not be split apart. fileciteturn21file0L1-L1  
In TU-2’s snippet and metadata, it looks like a single “disagreement block” that already includes (a) who dissents, (b) consensus evidence, and (c) a refutation/tarjīḥ framing. fileciteturn34file0L1-L1

So the structural tradeoff is:

- **Splitting TU-2 into per-opinion units** can improve retrieval (“I just want Malik’s view”) *if* each unit remains self-contained and includes what it takes to understand why that opinion is being accepted/rejected.  
- **Keeping TU-2 unified** reduces the risk of decontextualized or misleading “free-floating” dissenter claims, which is exactly the failure class the SPEC flags as highest-risk (decontextualization / context loss). fileciteturn21file0L1-L1

Given the output labels it FULL and describes it as “عرض خلاف … والجواب … وترجيح قول الجمهور,” the “one-unit disagreement bundle” boundary is defensible and likely preferable unless you have a strong downstream use case that requires per-opinion atomic retrieval. fileciteturn34file0L1-L1

### TU-5 micro-size as a standalone study unit

TU-5 is literally “3- استحباب خدمة العلماء والفضلاء.” (5 words) and is marked PARTIAL with the explicit note that the inferential link to the prior hadith is not present inside the unit. fileciteturn34file0L1-L1

**So yes: as a standalone study unit, it is too small in the sense that it collapses into an ungrounded slogan.** It can still be “true” and memorizable, but it does not satisfy the practical spirit of “complete scholarly thought,” because the *why / derivation* is exactly what’s missing (and the engine noticed that). fileciteturn21file0L1-L1

The subtle point: the SPEC explicitly avoids mandating a minimum teaching-unit size, so the engine is not violating a hard contract by producing a 5-word unit. fileciteturn21file0L1-L1  
But your question is pedagogical utility, and on that axis TU-5 should be treated as a boundary failure (or at least a unit that needs repair/merge).

### TU-1 vs TU-3–TU-6 split between hadith core and derived benefits

Structurally, this split is very aligned with the SPEC’s explicit “Derived Benefits Rule”: when a section opens with “ما يؤخذ من الحديث,” split by numbered benefits, each numbered item as a separate teaching unit. fileciteturn21file0L1-L1  
The observed output does that cleanly: TU-3 (benefit 1), TU-4 (benefit 2), TU-5 (benefit 3), TU-6 (benefit 4). fileciteturn34file0L1-L1

Where it feels *less* right is not the hadith-vs-benefits boundary, but the **tail benefits’ viability**:

- TU-5 is PARTIAL and too small to carry its own inference. fileciteturn34file0L1-L1  
- TU-6 is a cross-reference-like note whose very text references “هذا الحديث” and is also PARTIAL. It reads more like contextual metadata than a “teaching unit.” fileciteturn34file0L1-L1

So: **the split pattern is correct; the unitization of benefits 3–4 is the weak link.** Conceptually, the engine followed the right boundary signals but didn’t ensure that each resulting atom remained a “complete thought” suitable for standalone study.

### What I would change about boundaries as a human excerptor

This is the highest-leverage re-boundary proposal, given the actual output:

- Keep the main structure intact where it is strong: TU-0, TU-1, TU-2, TU-3, TU-4, TU-8, TU-9 are broadly well-shaped as standalone building blocks. fileciteturn34file0L1-L1  
- Fix the two weak units (TU-5 and TU-6) in a way that matches SPEC intent: preserve the “Derived Benefits list” structure but avoid standalone fragments.

Concretely, I would do one of these two hand-excerpting strategies:

**Strategy A: Merge the fragile tail benefits into a single “supplementary notes” unit (recommended).**  
New structure:

- TU-5+TU-6 become one unit: “adab inference + event-context note,” explicitly tying both back to the hadith of entity["people","المغيرة بن شعبة","companion of prophet"] (and optionally stating the inference bridge in-text, not only in metadata). fileciteturn34file0L1-L1  
This turns two PARTIAL fragments into one coherent “the hadith also indicates X; and some narrations place it in entity["city","تبوك","tabuk, saudi arabia"]” mini-module. The resulting unit might be ~19 words—still short, but no longer structurally broken.

This is consistent with the SPEC’s explicit note that size optimization (merging small units) is best handled as a post-grouping step if needed, rather than forcing the LLM to ignore natural boundary markers. fileciteturn21file0L1-L1

**Strategy B: Attach TU-6 as metadata/cross-reference rather than a teaching unit (more aggressive).**  
I would remove TU-6 as a standalone study unit and instead treat it as a cross-reference note attached to TU-1 (or as a context hint). Rationale: the unit’s primary_function is `cross_reference`, and it does not teach a concept/ruling so much as it locates the incident historically. fileciteturn34file0L1-L1  
This better matches the SPEC’s idea that teaching units are the “building blocks of the knowledge library,” not a stream of every structurally marked sentence. fileciteturn21file0L1-L1

I would *not* split TU-3 further (it is already short and splitting would likely create two sub-20-word fragments), and I would *not* reflexively split TU-2 into per-opinion units without seeing that each opinion is internally self-contained with its refutation preserved. The decontextualization-prevention rules make that kind of splitting high-risk unless executed carefully. fileciteturn21file0L1-L1

## Direct answers to your five questions

The answers below are “boundary/evaluation” answers, not doctrinal fiqh judgments.

**Grades for each TU (1–5) and standalone usefulness**  
Using the rubric above, the grades are:  
TU-0: 5, TU-1: 5, TU-2: 4, TU-3: 4, TU-4: 4, TU-5: 2, TU-6: 1, TU-7: 3, TU-8: 4, TU-9: 5. fileciteturn34file0L1-L1  
A fiqh student benefits from studying all of them individually *except* TU-6 (and TU-5 is low-value unless merged/repaired). fileciteturn34file0L1-L1

**TU-2 size and whether opinions should be separate**  
TU-2 at 140 words is not automatically “too large”; it is plausibly a coherent “ikhtilaf + answer + tarjih” unit. The bigger risk is breaking DP-style integrity (position/refutation separation) if you split. I would only split if each opinion becomes its own “complete thought” unit with its refutation included. fileciteturn21file0L1-L1 fileciteturn34file0L1-L1

**TU-5 usefulness at 5 words**  
Yes, TU-5 is too small to be a strong standalone study unit, and the engine’s own self-containment notes corroborate why: the inferential bridge from the hadith is missing within the unit. Best fix is merge or in-text grounding. fileciteturn34file0L1-L1

**Split between TU-1 and TU-3–TU-6**  
The high-level split is correct and SPEC-aligned (Derived Benefits Rule). The problem is not “benefits should stay with the hadith,” but “some benefits are too fragmentary once separated.” I would keep the structural split but merge/repair benefits 3–4 (or demote the pure cross-reference to metadata). fileciteturn21file0L1-L1 fileciteturn34file0L1-L1

**What I’d change by hand-excerpting**  
I would preserve 8 of the 10 boundaries and change only the tail of the first benefits list: merge TU-5 and TU-6 (or attach TU-6 as metadata), aiming to eliminate standalone PARTIAL micro-fragments while preserving the “numbered benefits” shape. fileciteturn21file0L1-L1 fileciteturn34file0L1-L1