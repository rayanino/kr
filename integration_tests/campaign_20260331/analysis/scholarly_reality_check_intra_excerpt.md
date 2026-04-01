# Scholarly Reality Check: Intra-Excerpt Annotation vs. Fine-Grained Excerpting

**Date:** 2026-04-01
**Author:** Claude Chat (Architect)
**Status:** DECISION MADE — See §Final Recommendation
**Triggered by:** Owner's 2 review comments on taysir excerpts 1 and 2 + Codex's "third option" proposal
**Input files read:**
- `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` (owner's 2 review comments)
- `reference/archive/VISION.md` §5 (excerpt definition, self-containment, cross-topic rules)
- `reference/ENTRY_EXAMPLE.md` (how synthesis works)
- `engines/excerpting/SPEC.md` §3 (self-containment) and §5.3 (cross-topic rules / Phase 2b grouping)
- `integration_tests/campaign_20260331/taysir/excerpts.jsonl` (all 1,283 excerpts)
- `library/sciences/nahw/tree.yaml`, `sarf/tree.yaml`, `balagha/tree.yaml`, `imlaa/tree.yaml` (taxonomy trees)

---

## Context

### The Problem

The excerpting engine's first campaign (2,303 excerpts across 5 packages) produced medium-grained excerpts that the owner rejected as too coarse. Two specific complaints:

1. **Excerpt 1** (definition of الطلاق): combines both the linguistic definition (تعريف لغوي) and the legal definition (تعريف شرعي) in one excerpt. The owner says these should be separate excerpts because they map to different taxonomy leaves (تعريف الطلاق لغة vs. تعريف الطلاق شرعا).

2. **Excerpt 2** (evidence for divorce ruling): combines the general ruling statement + Quranic evidence + hadith evidence + ijma + qiyas into one excerpt. The owner wants per-evidence-type granularity — one excerpt per evidence category, and ideally per-ayah / per-hadith granularity within each category.

### The Codex Proposal ("Third Option")

Codex CLI recommended keeping medium-grained excerpts but adding **intra-excerpt structure** — proposition spans, evidence spans, and support links — so synthesis can decompose them. The idea: annotate WITHIN excerpts rather than splitting them.

### The Question

Is intra-excerpt annotation feasible for real Arabic scholarly text? Or should the excerpting engine simply produce finer-grained excerpts?

---

## Phase 1: Annotation Feasibility on 5 Real Taysir Excerpts

### Method

Selected 5 mixed-content excerpts from the taysir corpus and attempted to annotate them with proposition `[P]` and evidence `[E]` spans, then identified where annotation breaks down.

### Test 1: Excerpt 2 — Ruling + Four Evidence Types

**Full text:**
```
وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح.
فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وعيرها من الآيات.
وأما السنة، فقوله صلى الله عليه وسلم: {أبغض الحلال إلى الله الطلاق} وغيره من فعله وتقريره صلى الله عليه وسلم.
والأمة مجمعة عليه، والقياس يقتضيه.
فإذا كان يتم النكاح بالعقد لمصالحه وأغراضه فإنه يفسخ ذلك العقد بالطلاق، للمقاصد الصحيحة.
```

**Attempted annotation:**
- `[P]` وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح.
- `[E-quran]` فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وعيرها من الآيات.
- `[E-hadith]` وأما السنة، فقوله صلى الله عليه وسلم: {أبغض الحلال إلى الله الطلاق}...
- `[E-ijma]` والأمة مجمعة عليه
- `[E-qiyas]` والقياس يقتضيه.
- `[???]` فإذا كان يتم النكاح بالعقد لمصالحه وأغراضه فإنه يفسخ ذلك العقد بالطلاق، للمقاصد الصحيحة.

**Breakdown:** The last sentence is the elaboration of the qiyas. It simultaneously serves as the evidence_rational span AND the author's editorial explanation. Is "the qiyas requires it" the evidence, and the elaboration a separate thing? Or is the whole block one evidence span? No clean boundary.

**Verdict: Mostly works** — well-structured passage. But the qiyas elaboration is ambiguous.

---

### Test 2: Excerpt 7 — Opinion + Khilaf + Evidence

**Full text:**
```
2- أمره صلى الله عليه وسلم ابن عمر برجعتها، دليل على وقوعه.
ووجهته أن الرجعة لا تكون إلا بعد طلاق، ويأتي الخلاف في ذلك إن شاء الله. والأمر برجعتها يقتضي الوجوب، وإليه ذهب أبو حنيفة وأحمد والأوزاعي، وحمله بعضهم على الاستحباب وذهب إليه الشافعي ورواية عن أحمد واحتجوا بأن ابتداء النكاح ليس بواجب فاستدامته كذلك.
```

**Breakdown:** This single sentence contains TWO completely different scholarly discussions. The first half discusses whether divorce during menstruation counts (وقوع الطلاق). The second half pivots, mid-sentence, to whether the return (رجعة) is obligatory or recommended. These are different fiqh questions mapping to different taxonomy leaves. The pivot happens with a simple و — no structural marker.

Within the second discussion: "واحتجوا بأن ابتداء النكاح ليس بواجب فاستدامته كذلك" is simultaneously (a) evidence for the istihbab position and (b) a legal maxim (قياس) that functions as both proposition and proof.

**Verdict: Fails.** Two-topic structure and proposition/evidence circularity make span annotation unreliable.

---

### Test 3: Excerpt 11 — Full Scholarly Debate

**Full text:**
```
اختلاف العلماء:
ذهب جمهور العلماء- ومنهم الأئمة الأربعة رضي الله عنهم: إلى وقوع الطلاق في الحيض.
ودليلهم على ذلك أمره صلى الله عليه وسلم ابن عمر بارتجاع زوجته حين طلقها حائضاً.
ولا تكون الرجعة إلا بعد طلاق سابق لها، ولأن في بعض ألفاظ الحديث "فحسبت من طلاقها".
وذهب بعض العلماء- ومنهم شيخ الإسلام (ابن تيميه) وتلميذه (ابن القيم) إلى أن الطلاق لا يقع فهو لاغ.
واستدلوا على ذلك بما رواه أبو داود والنسائي [أن عبد الله بن عمر طلق امرأته وهى حائض، قال عبد الله: فردها علي ولم يرها شيئا].
وهذا الحديث في (مسلم) بدون قوله: [ولم يرها شيئا].
وقد استنكر العلماء هذا الحديث، لمخالفته الأحاديث كلها.
وأجاب (ابن القيم) عن أدلة الجمهور بأن الأمر برجعتها، معناه إمساكها على حالها الأولى، لأن الطلاق لم يقع في وقته المأذون فيه شرعا فهو ملغى، فيكون النكاح بحاله.
وأما الاستدلال بلفظ " فحسبت من طلاقها" فليس فيه دليل، لأنه غير مرفوع إلى النبي صلى الله عليه وسلم.
وأطال (ابن القيم) النقاش في هذا الموضع في كتاب [تهذيب السنن] على عادته في الصولات والجولات، ولكن الأرجح ما ذهب إليه جمهور العلماء. والله أعلم.
```

**Attempted annotation:**
- `[P1-jumhur]` ذهب جمهور العلماء ... إلى وقوع الطلاق في الحيض.
- `[E1a-for-P1]` ودليلهم على ذلك أمره صلى الله عليه وسلم ابن عمر بارتجاع زوجته...
- `[E1b-for-P1]` ولا تكون الرجعة إلا بعد طلاق سابق لها (rational elaboration of E1a)
- `[E1c-for-P1]` ولأن في بعض ألفاظ الحديث "فحسبت من طلاقها" (hadith evidence)
- `[P2-minority]` وذهب بعض العلماء ... إلى أن الطلاق لا يقع فهو لاغ.
- `[E2-for-P2]` واستدلوا على ذلك بما رواه أبو داود والنسائي [أن عبد الله بن عمر...]
- `[???-CRITICAL]` وهذا الحديث في (مسلم) بدون قوله: [ولم يرها شيئا].
- `[???-CRITICAL]` وقد استنكر العلماء هذا الحديث، لمخالفته الأحاديث كلها.
- `[refutation-of-E1a]` وأجاب (ابن القيم) عن أدلة الجمهور بأن الأمر برجعتها...
- `[refutation-of-E1c]` وأما الاستدلال بلفظ "فحسبت من طلاقها" فليس فيه دليل...
- `[tarjih-editorial]` ولكن الأرجح ما ذهب إليه جمهور العلماء.

**Breakdown of `???-CRITICAL` sentences:**

"وهذا الحديث في (مسلم) بدون قوله: [ولم يرها شيئا]" — this is hadith criticism (نقد حديثي). Not a proposition, not evidence, not a refutation. It's a meta-scholarly observation about textual transmission. It implicitly undermines the minority position (the key phrase is an addition not in the main collections), but it's presented as a neutral observation.

"وقد استنكر العلماء هذا الحديث" — scholarly consensus ABOUT evidence, not evidence itself.

Ibn al-Qayyim's refutation section: every sentence simultaneously (a) refutes position 1's evidence, (b) proposes a new interpretation, and (c) provides evidence for position 2. Triple duty.

**Verdict: Fails hard.** Hadith criticism, refutation-as-reinterpretation, and tarjih don't fit into "proposition" or "evidence." The annotation categories need ~8 types, not 2.

---

### Test 4: Excerpt 24 — Multi-School Khilaf with Refutation

**Full text (summary):** Three positions (Ahmad, Hanafis, Malik+Shafi'i) on maintenance for irrevocably divorced women, with evidence for each and refutation of positions 2 and 3.

**Key annotation problem:** "والصحيح، هو القول الأول، لقوة الدليل وعدم المعارض" — the tarjih statement is a proposition ABOUT propositions, and its evidence ("لقوة الدليل") is a meta-evaluation OF evidence. Two-category annotation has no way to represent this level distinction.

The refutation "فأما القول الثاني فضعيف، لأن هذه الكلمة التي استدلوا بها، لم تثبت عن عمر" is simultaneously: evidence against position 2, evidence FOR position 1, AND hadith criticism.

**Verdict: Ambiguous.** Tarjih and refutation serve inherently dual roles.

---

### Test 5: Excerpt 10 — Rational Evidence with Sub-Points

**Full text (summary):** حِكمة (wisdom/rationale) passage explaining why the waiting period rules exist.

**Verdict: Mostly works** — but only because حِكمة passages have an unusually clean proposition→reason structure. This is the exception, not the rule.

---

### Phase 1 Summary

| Excerpt | Annotation Result | Core Problem |
|---------|------------------|--------------|
| 2 (ruling+evidence) | Mostly works | Qiyas elaboration is ambiguous |
| 7 (opinion+khilaf) | Fails | Two topics fused; proposition/evidence circularity |
| 11 (full debate) | Fails hard | Hadith criticism, refutation-as-reinterpretation, tarjih uncapturable |
| 24 (multi-school) | Ambiguous | Tarjih and refutation serve dual roles |
| 10 (rational) | Mostly works | Only works because حِكمة has clean structure |

**Fundamental problem:** Islamic scholarly writing has ~8 functional categories (ruling, evidence-quran, evidence-hadith, evidence-ijma, evidence-rational, refutation, tarjih, editorial), not 2. Many sentences serve multiple functions simultaneously.

---

## Phase 2: Boundary Cases in Islamic Scholarly Writing and LLM Reliability

### Quantitative Corpus Analysis (1,283 taysir excerpts)

| Pattern | Count | % of corpus |
|---------|-------|-------------|
| Multiple content types (would need annotation) | 901 | 70.2% |
| Both ruling AND evidence content types | 325 | 25.3% |
| لأن embedded reasoning | 338 | 26.3% |
| Khilaf (scholarly disagreement) passages | 118 | 9.2% |
| Explicit istidlal (evidence-citing) phrases | 63 | 4.9% |
| Tarjih (preference) statements | 12 | 0.9% |
| Short excerpts (<200 chars, ≤2 lines) | 372 | 29.0% |
| From ما يؤخذ/يستفاد sections | 181 | 14.1% |

**Critical finding:** 70.2% of excerpts have multiple content types — annotation is not a targeted enhancement for a few complex passages. It would need to run on nearly three-quarters of the entire corpus.

### Six Boundary Cases

#### Boundary Case 1: The دليل-حكم Syntactic Fusion

Excerpt 9: `4- قوله [قبل أن يمسها] دليل على أنه لا يجوز الطلاق في طُهْر جامعَ فيه.`

One sentence. The grammatical structure is: [evidence-text] + دليل على + أنه + [ruling]. The connector "دليل على أن" makes evidence and ruling syntactically inseparable — they are the subject and predicate of the same nominal sentence (جملة اسمية). You cannot draw a span boundary without splitting a grammatical unit.

**Prevalence:** 46 excerpts (3.6%) with explicit "دليل على" pattern; broader evidence-ruling-in-same-sentence pattern is far more common. Every "ما يؤخذ" derived benefit (14.1% of corpus) follows this structure.

#### Boundary Case 2: The إجماع (Consensus) Dual-Nature

`والأمة مجمعة عليه` — simultaneously a ruling-state (scholars have agreed) AND a proof-type (consensus is one of the four usul sources). The dual nature is foundational to usul methodology. Any annotation forcing a single label loses half the meaning.

#### Boundary Case 3: The لأن Chain (Embedded Reasoning)

Excerpt 30: `فيه دليل على ثبوت حكم الرضاع من زوج المرضعة وأقاربه، لأنه صاحب اللبن، فإن اللبن تسبب عن ماءه وماء المرأة جميعا. فوجب أن يكون الرضاع منهما...`

This is a reasoning chain: ruling → reason → evidence for the reason → conclusion. Each sentence's function depends on its relationship to adjacent sentences. The لأن clause is syntactically subordinate to the ruling — extracting it as a separate span breaks Arabic syntax. 26.3% of all excerpts contain لأن embedded reasoning.

#### Boundary Case 4: Tarjih as Meta-Proposition

`والصحيح، هو القول الأول، لقوة الدليل وعدم المعارض.` — A proposition ABOUT propositions. Its evidence ("لقوة الدليل") is a meta-evaluation OF evidence. Two-category annotation has no way to represent this level distinction.

#### Boundary Case 5: Refutation-as-Implicit-Evidence

`فأما القول الثاني فضعيف، لأن هذه الكلمة التي استدلوا بها، لم تثبت عن عمر.` — Four simultaneous functions: (a) proposition ("position 2 is weak"), (b) evidence against position 2, (c) implicit evidence FOR position 1, (d) hadith criticism. Function (c) exists only in scholarly logic, not in any textual marker.

#### Boundary Case 6: The مستدلين Construction

`فذهب الإمام أحمد: إلى أنه ليس لها نفقة، ولا سكنى... مستدلين بحديث الباب.` — The حال construction (مستدلين) creates a grammatically unified structure where position attribution AND evidence basis are one sentence. Splitting creates an attribution span with no content and an evidence reference with no attribution.

### LLM Reliability Assessment

The reliability concern is not about LLM Arabic capability (current models are strong). The concern is that **the categories don't map to the text**:

1. **Genuine ambiguity, not annotation error.** These are real scholarly ambiguities that Islamic studies professors would disagree about. Different annotators will make different arbitrary choices.
2. **Consistency across scale.** 70% of 1,283 excerpts need annotation. The same word لأن introduces evidence in one context and elaboration in another.
3. **Hidden cost of wrong boundaries.** A wrong span boundary creates a misleading decomposition that synthesis treats as authoritative — the exact T-4 threat the SPEC prevents.

---

## Phase 3: The Owner's Definition Comment — Why Separate Excerpts, Not Spans

### What the Owner Actually Said (3 principles)

**Principle 1:** تعريف الطلاق لغة and تعريف الطلاق شرعا map to different taxonomy leaves. Different questions, different topics.

**Principle 2:** Self-containment requires no question marks. "وفي الشرع..." is backward-referencing.

**Principle 3:** Inter-excerpt corruption risk. If the reader at the شرعا leaf wants the لغة definition, they might open a DIFFERENT source's لغة definition, creating a T-1 variant — understanding source A through source B.

### Prevalence: لغة/شرعا Definition Pairs in Taysir

In just 5 chapters of one book, 8 instances:

| Chapter | Definition Pair |
|---------|----------------|
| كتاب الطلاق | الطلاق لغة/شرعا |
| كتاب الصلاة | الصلاة لغة/شرعا |
| باب الشفعة | الشفعة لغة/شرعا |
| باب الوقف | الوقف لغة/شرعا |
| كتاب الوصايا | الوصية لغة/شرعا |
| كتاب الأيمان | الأيمان لغة/شرعا |
| باب الأذان | الأذان لغة/شرعا |
| كتاب الجهاد | الجهاد لغة/شرعا |

Universal convention — nearly every chapter of every fiqh book opens with this pair. Thousands across 2,519 books.

### Why Intra-Excerpt Spans Fail for Definitions

Under spans, the excerpt is placed at ONE leaf. Three options, all bad:

**(a) Parent node:** Synthesis at لغة leaf has no excerpt from this source. Synthesis at شرعا leaf has no excerpt. Coverage tracking reports zero.

**(b) لغة leaf:** The شرعا definition is trapped inside a لغة excerpt. Synthesis at شرعا cannot compare legal definitions cross-source.

**(c) Duplicated:** Breaks one-excerpt-per-source-per-leaf diagnostic (VISION §5.5). Synthesis needs to understand spans and extract sub-content — excerpting-inside-synthesis.

**Under separate excerpts:** Each goes to its correct leaf. Synthesis sees attributed, source-traceable definitions. Cross-references solve inter-excerpt navigation.

### The Third Piece of Knowledge

"والتعريف الشرعي فَرْد من معناه اللغوي العام" — the relationship statement between definitions. It naturally belongs in the شرعا excerpt because it elaborates on the legal definition's scope.

### Self-Containment Solution

The dangling "وفي الشرع" reference is resolved by enrichment: the context_hint provides framing ("التعريف الشرعي، يقابله التعريف اللغوي في نفس المصدر"), or the description_arabic states the topic. The primary text preserves the original exactly (text integrity invariant).

---

## Phase 4: Genre Variance — Fiqh vs. Nahw vs. Balagha vs. Usul

### Tree Evidence: All Sciences Demand Leaf-Level Granularity

ALL 4 verified science trees separate لغة from اصطلاح at the leaf level:

| Science | Total leaves | Definition leaves | لغة/اصطلاح sub-leaves |
|---------|-------------|-------------------|----------------------|
| Nahw | 226 | 38 (16.8%) | لغة + 6 اصطلاح sub-leaves |
| Sarf | 226 | 31 (13.7%) | لغة + 5 اصطلاح sub-leaves |
| Balagha | 335 | 74 (22.1%) | لغة + multiple اصطلاح + 4 sub-leaves for قيد المطابقة |
| Imlaa | 105 | 14 (13.3%) | لغة + 4 اصطلاح sub-leaves |

The balagha tree breaks the definition of البلاغة into 8+ sub-leaves. A paragraph defining البلاغة produces content for all of them. Span annotations in one excerpt cannot serve this — synthesis at each sub-leaf needs its own excerpt.

### Genre-Specific Annotation Challenges

#### Nahw: The شاهد Triad

Nahw teaching passages contain: (1) grammatical rule, (2) evidence text (شاهد — verse, hadith, poetry), (3) grammatical parsing (i'rab). The i'rab is NOT evidence and NOT a proposition — it's analytical demonstration. A third functional category that proposition/evidence annotation cannot represent.

Additionally, matn/sharh layering creates proposition-within-proposition nesting that flat span annotation cannot capture.

#### Balagha: Aesthetic Judgment Fused with Analysis

In balagha, the analysis of HOW a text achieves its rhetorical effect IS the knowledge. You can't separate "proposition" from "evidence" because analyzing the text serves both roles simultaneously. The act of identifying المشبه, المشبه به, and وجه الشبه is simultaneously evidence that the concept exists AND the knowledge the student needs.

#### Usul al-Fiqh: Meta-Level Reasoning

Usul discusses HOW to derive rulings. The "evidence" for a methodological principle is itself a chain of reasoning about reasoning. Application examples blur illustration/evidence. A single paragraph in usul produces content for 4+ taxonomy leaves. Span annotation can't solve the multi-leaf placement problem.

### Cross-Genre Verdict

| Genre | Unique annotation problem | Why spans fail |
|-------|--------------------------|----------------|
| Fiqh | Ruling/evidence fusion, refutation-as-evidence, tarjih | Two-category system misses 6+ functional categories |
| Nahw | شاهد triad, matn/sharh nesting | i'rab is a third category; nesting needs hierarchy |
| Balagha | Analysis IS the knowledge | No proposition/evidence boundary exists |
| Usul | Meta-level reasoning, one paragraph → 4+ leaves | Doesn't solve multi-leaf placement |

The annotation problem is genre-specific; the ARCHITECTURAL problem is universal: spans don't change where an excerpt gets placed in the tree.

---

## Phase 5: The Two-Level Alternative, Final Recommendation

### Evaluating the Two-Level Alternative (Canonical Excerpt + Derived Evidence Card)

**What it gets right:** Correctly identifies the tension between self-containment and granularity.

**Five architectural problems:**

1. **Evidence cards need self-containment too.** "فأما الكتاب فنحو {الطلاقُ مَرتَانِ}" is not self-contained — needs context about what ruling the verse proves. Once enriched, the "card" IS an excerpt.

2. **Canonical excerpt becomes orphaned.** If cards are self-contained at leaves, the canonical excerpt has no synthesis consumer. It becomes archival metadata.

3. **Consistency maintenance.** Two representations create synchronization problems. Metadata corrections must propagate. Partial card rejection partially invalidates the canonical excerpt.

4. **Decomposition IS excerpting.** The decomposition logic is exactly what the excerpting engine does in Phase 2b. Moving it to a post-excerpting layer doesn't simplify — it creates a second excerpting pass with less source context.

5. **Doesn't solve definitions.** The two-level model is designed for ruling+evidence relationships. Definitions (لغة/شرعا) are distinct topics, not evidence cards for a ruling.

### The Correct Architecture: Calibrated Fine-Grained Excerpting

Not a new layer. A recalibration of existing excerpting engine grouping rules.

The VISION already provides the framework:
- §5.2: grouping by content, not tree structure
- §5.3 Rule 2: split when both parts are self-contained
- §5.3 Rule 3: content integrity overrides taxonomic precision

What the owner's feedback adds: **the current calibration point is too coarse.** The SPEC's current rule "A position + its evidence + counter-evidence + conclusion = one unit" prevents exactly the granularity the owner wants.

### Specific SPEC Changes: Three New Domain Rules

See separate file: `engines/excerpting/domain_rules/DR_DOMAIN_RULES.md`

Summary:
- **DR-1 (Definition Pair Splitting):** لغة/شرعا definitions MUST be separate teaching units when both are substantive.
- **DR-2 (Evidence-Type Splitting):** Evidence from different categories (Quran, hadith, ijma, qiyas) SHOULD be separate teaching units when each citation is substantive (>~10 words of evidence text).
- **DR-3 (Khilaf Preservation):** Scholarly disagreement passages REMAIN as single units when decomposition would lose argumentative structure.
- **Modified decontextualization rule:** "Evidence MUST stay with ruling" narrowed to apply only when evidence is brief, syntactically fused, or inside a khilaf passage.
- **Cross-reference obligation:** All split excerpts carry cross_references to each other.

### The Tree-Awareness Question

The owner's instinct is correct: tree-agnostic excerpting. VISION §5.2 codifies this.

Resolution: the new rules are **domain rules** derived from Islamic scholarly conventions, not tree structure. The fact that لغة/شرعا are separate topics is a property of the SCIENCE. The tree reflects this; it doesn't create it.

**Rule: always excerpt at or below the finest expected leaf granularity. Over-granularity is recoverable (merge in synthesis). Under-granularity is not (synthesis at fine leaves has no data).**

### CrossReference Schema Extension

Current: `{reference_text, target_description, target_div_id, resolved}`
Extended: `{reference_text, target_description, target_div_id, target_excerpt_id, relationship_type, resolved}`

Where `relationship_type` is one of: `companion_definition`, `evidence_for`, `ruling_proven_by`, `refutation_of`, `continuation`.

### Impact Assessment

| Change | Excerpts affected | Nature |
|--------|------------------|--------|
| DR-1 (definition splitting) | ~8 in taysir, thousands across library | New grouping rule in Phase 2b prompt |
| DR-2 (evidence-type splitting) | ~120 multi-evidence, ~281 ruling+evidence | Modified grouping rule + threshold |
| DR-3 (khilaf preservation) | ~118 khilaf passages | Explicit exception to prevent over-splitting |
| Cross-reference requirement | All split excerpts | New Phase 3 enrichment step |

---

## Final Recommendation

### REJECTED: Intra-excerpt annotation
- Fails on 3 of 5 test excerpts
- Requires genre-specific schemas
- Pushes excerpting's job onto synthesis
- Doesn't solve taxonomy placement for definitions

### REJECTED: Two-level alternative (canonical + card)
- Creates double representation and orphaned excerpts
- Decomposition IS excerpting — just moved to a different layer
- Doesn't handle definitions

### ACCEPTED: Calibrated fine-grained excerpting with domain rules
- Three new domain rules (DR-1, DR-2, DR-3)
- Modified decontextualization threshold
- Extended CrossReference schema
- No architectural change to the engine's three-phase structure

### Implementation Path

1. **Prompt changes:** Implement DR-1/DR-2/DR-3 together with the 3 existing prompt fixes (narrator role, المعنى classification, fawa'id granularity) in one CC session.
2. **Schema extension:** Add `target_excerpt_id` and `relationship_type` to CrossReference. Add Phase 3 enrichment step.
3. **Calibration:** 30-book probe with owner review — is splitting too fine? Not fine enough? Are cross-references useful?

### Pending: Cross-Provider Review

This design decision MUST be reviewed by ChatGPT and/or Gemini before implementation. Key adversarial question: "Would per-evidence-type splitting at the DR-2 threshold lose scholarly meaning? Are there cases where evidence from different categories is so intertwined that splitting destroys the argument?"

---

## Appendix A: Owner's Original Review Comments

### Comment on Excerpt 1 (definition)

The owner rejected excerpt 1 and specified:
- "الطلاق: في اللغة: حل الوثاق..." should be one excerpt (تعريف الطلاق لغة)
- "وفي الشرع: حَل عقدة التزويج..." should be a separate excerpt (تعريف الطلاق شرعا)
- But "والتعريف الشرعي فَرْد من معناه اللغوي العام. قال إمام الحرمين: هو لفظ جاهلي ورد الشرع بتقريره." should NOT be its own excerpt — it belongs with the شرعا definition
- Principle: "the relationship between excerpts... need to be connected in some way" — cross-references between companion excerpts

### Comment on Excerpt 2 (evidence)

The owner rejected excerpt 2 and specified:
- The general ruling statement should be its own excerpt (الحكم إجمالا)
- Per-evidence-type excerpts: Quranic evidence separate, hadith evidence separate
- "Even better: per ayah. So the granularity should be: proofing, from quran, from this ayah"
- Principle: the excerpting engine should "give me the edge" — open a granulated leaf and get a direct cross-source comparison
- Warning: "I might as well just take pictures of books" if excerpts are just page chunks
- Question: should the taxonomy tree be provided to the excerpting engine? Owner's instinct: no (unbiased excerpting)

---

## Appendix B: Quantitative Corpus Data

From 1,283 taysir excerpts:
- 70.2% have multiple content types
- 25.3% have BOTH ruling AND evidence types
- 26.3% have لأن embedded reasoning
- 9.2% have khilaf patterns
- 4.9% have explicit istidlal phrases
- 14.1% are from ما يؤخذ/يستفاد sections
- 29.0% are short (<200 chars)
- 17.1% are short and FULL self-contained (already fine-grained)
- 9.4% mix 2+ evidence types (direct DR-2 targets)
- 105 total definition excerpts
- 8 contain both لغة+شرعا (direct DR-1 targets)
