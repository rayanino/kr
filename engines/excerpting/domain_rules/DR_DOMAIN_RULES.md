# Domain Rules for Fine-Grained Excerpting

**Date:** 2026-04-01
**Status:** APPROVED by architect — pending cross-provider review before implementation
**Source:** Scholarly reality check session (see `scholarly_reality_check_intra_excerpt.md`)
**Implements:** Owner's 2 review comments on taysir excerpts 1 and 2

---

## Overview

These three domain rules recalibrate the excerpting engine's Phase 2b grouping to produce finer-grained teaching units where self-containment allows. They are **additive** — they join the existing grouping rules and decontextualization prevention rules in the Phase 2b system prompt (SPEC §5.3.2). They do NOT change the engine's three-phase architecture.

**Governing principle:** Over-granularity is safe (synthesis can work with fine excerpts at coarse leaves). Under-granularity is not (synthesis at fine leaves has no data if the excerpt is at a coarse level). Therefore, when in doubt, split.

**Architectural constraint:** These are DOMAIN RULES, not tree-derived rules. They reflect Islamic scholarly conventions, not taxonomy structure. The excerpting engine remains taxonomy-independent per VISION §5.2.

---

## DR-1: Definition Pair Splitting

### Rule

When a passage contains both a linguistic definition (تعريف لغوي) and a legal/technical definition (تعريف شرعي / اصطلاحي) of the same term, they **MUST** be separate teaching units IF both definitions are **substantive**.

### Substantive threshold

A definition is "substantive" if it contains more than 3 words of definitional content. Examples:
- **Brief gloss (do NOT split):** "الطلاق لغة: الترك" — 1 word of definition
- **Substantive (SPLIT):** "الطلاق: في اللغة: حل الوثاق، مشتق من الإطلاق، وهو الترك والإرسال" — full definition with etymology

### Relationship statement placement

Any statement about the relationship between the two definitions (e.g., "والتعريف الشرعي فَرْد من معناه اللغوي العام") belongs in the **شرعي/اصطلاحي** teaching unit, because it elaborates on the legal/technical definition's scope relative to the linguistic meaning.

### Cross-reference requirement

Both resulting teaching units MUST carry a `cross_reference` to the other:
- The لغوي unit: `{reference_text: "التعريف الشرعي المقابل", relationship_type: "companion_definition"}`
- The شرعي unit: `{reference_text: "التعريف اللغوي المقابل", relationship_type: "companion_definition"}`

### Detection markers

Common textual markers for this pattern:
- `في اللغة... وفي الشرع...`
- `لغةً... واصطلاحاً...`
- `لغة:... وشرعاً:...`
- `لغة-... وفي الاصطلاح...`

### Example from taysir (excerpt 1)

**Before (current — one unit):**
```
‌‌كتاب الطلاق
الطلاق: في اللغة: حل الوثاق. مشتق من الإطلاق، وهو الترك والإرسال.
وفي الشرع: حَل عقدة التزويج، والتعريف الشرعي فَرْد من معناه اللغوي العام. قال إمام. الحرمين: هو لفظ جاهلي ورد الشرع بتقريره.
```

**After (two units):**

Unit A (linguistic definition):
```
primary_function: definition
description_arabic: تعريف الطلاق لغةً: حل الوثاق، واشتقاقه من الإطلاق
text: الطلاق: في اللغة: حل الوثاق. مشتق من الإطلاق، وهو الترك والإرسال.
cross_references: [{reference_text: "التعريف الشرعي المقابل", relationship_type: "companion_definition"}]
```

Unit B (legal definition):
```
primary_function: definition
description_arabic: تعريف الطلاق شرعاً: حل عقدة التزويج، وبيان أنه فرد من المعنى اللغوي العام
text: وفي الشرع: حَل عقدة التزويج، والتعريف الشرعي فَرْد من معناه اللغوي العام. قال إمام. الحرمين: هو لفظ جاهلي ورد الشرع بتقريره.
cross_references: [{reference_text: "التعريف اللغوي المقابل", relationship_type: "companion_definition"}]
```

### Prevalence

8 instances in 5 chapters of taysir alone. Universal convention across all fiqh books. Expected across all 2,519 Shamela sources.

---

## DR-2: Evidence-Type Splitting

### Rule

When a passage states a ruling and then cites evidence from multiple categories (Quran, hadith, ijma, qiyas, scholarly precedent), each evidence category **SHOULD** be a separate teaching unit IF:

**(a) Substantive citation:** The evidence citation includes the evidence text (verse, hadith text, scholarly quote) or provides a specific identifiable reference. Threshold: more than ~10 words of evidence content.

**(b) Identifiable ruling:** The ruling the evidence supports is identifiable from context. Each evidence unit's `description_arabic` MUST state what ruling the evidence supports.

### What stays together

- **Brief mentions** (<~10 words of evidence text): "والأمة مجمعة عليه" (4 words) stays with the ruling.
- **Syntactically fused** evidence: "قوله [قبل أن يمسها] دليل على أنه لا يجوز" — the دليل على أن pattern makes evidence and ruling one sentence. These stay together.
- **Evidence inside khilaf passages:** Governed by DR-3, not DR-2.

### The general ruling statement

The overview statement that names evidence categories without detailing them (e.g., "وحكمه ثابت بالكتاب والسنة والإجماع والقياس الصحيح") is its own teaching unit — a summary excerpt placed at a general "حكم إجمالي" leaf.

### Per-evidence-instance splitting

When a single evidence category section discusses **multiple specific texts** (multiple Quranic verses, multiple hadith):
- Each specific text is a separate teaching unit IF discussed independently.
- If the author chains multiple texts in a single argument thread ("لقوله تعالى... ولقوله..."), they stay together.

### Cross-reference requirement

All evidence units MUST cross-reference back to the ruling unit:
- Evidence unit: `{reference_text: "الحكم الذي يُستدل عليه", relationship_type: "evidence_for"}`
- Ruling unit: `{reference_text: "الدليل من [الكتاب/السنة/...]", relationship_type: "ruling_proven_by"}`

### Example from taysir (excerpt 2)

**Before (current — one unit):**
```
وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح.
فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وعيرها من الآيات.
وأما السنة، فقوله صلى الله عليه وسلم: {أبغض الحلال إلى الله الطلاق} وغيره من فعله وتقريره صلى الله عليه وسلم.
والأمة مجمعة عليه، والقياس يقتضيه.
فإذا كان يتم النكاح بالعقد لمصالحه وأغراضه فإنه يفسخ ذلك العقد بالطلاق، للمقاصد الصحيحة.
```

**After (three or four units):**

Unit A (general ruling):
```
primary_function: rule_statement
description_arabic: بيان ثبوت حكم الطلاق بالأدلة الأربعة إجمالاً
text: وحكمه ثابت في الكتاب، والسنة، والإجماع، والقياس الصحيح.
cross_references: [evidence_for links to B, C, D]
```

Unit B (Quranic evidence):
```
primary_function: evidence_quran
description_arabic: دليل مشروعية الطلاق من الكتاب: آية {الطلاق مرتان}
text: فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات.
cross_references: [{reference_text: "حكم ثبوت الطلاق", relationship_type: "evidence_for"}]
```

Unit C (hadith evidence):
```
primary_function: evidence_hadith
description_arabic: دليل مشروعية الطلاق من السنة: حديث أبغض الحلال إلى الله الطلاق
text: وأما السنة، فقوله صلى الله عليه وسلم: {أبغض الحلال إلى الله الطلاق} وغيره من فعله وتقريره صلى الله عليه وسلم.
cross_references: [{reference_text: "حكم ثبوت الطلاق", relationship_type: "evidence_for"}]
```

Unit D (ijma + qiyas — kept together because ijma is brief):
```
primary_function: evidence_rational
description_arabic: دليل مشروعية الطلاق من الإجماع والقياس على عقد النكاح
text: والأمة مجمعة عليه، والقياس يقتضيه. فإذا كان يتم النكاح بالعقد لمصالحه وأغراضه فإنه يفسخ ذلك العقد بالطلاق، للمقاصد الصحيحة.
cross_references: [{reference_text: "حكم ثبوت الطلاق", relationship_type: "evidence_for"}]
```

**Note:** The ijma mention "والأمة مجمعة عليه" is only 4 words — below the substantive threshold. It stays with the qiyas elaboration which IS substantive. If a future text has a full paragraph on ijma, that would be a separate unit.

### Prevalence

120 excerpts (9.4%) in taysir mix 2+ evidence types. 281 excerpts (21.9%) mix ruling + evidence.

---

## DR-3: Khilaf Preservation

### Rule

Scholarly disagreement passages (اختلاف العلماء sections) that present multiple positions with their evidence and refutations **REMAIN** as single teaching units WHEN decomposition would lose the argumentative structure — specifically:

- Refutations reference positions by implicit pronouns (هذا القول, الأول, etc.)
- The tarjih depends on comparing all positions
- Evidence for one position is simultaneously a refutation of another

### Exception (very long khilaf)

If a khilaf passage exceeds ~800 words AND contains clearly independent position blocks (each position is a full paragraph with explicit attribution), the engine MAY split at position boundaries, ensuring each position unit includes enough of the opposing position to satisfy C-SC-5 (Dialogue Completeness).

### Rationale

This rule OVERRIDES DR-2 for evidence within khilaf passages. The decontextualization risk (T-4) in khilaf passages is extreme: if a refutation is separated from the position it refutes, the owner reads "Scholar A says X" when the original says "Scholar A reports Scholar B's view X, then disagrees."

### Detection markers

- `اختلاف العلماء` / `اختلف العلماء`
- `فذهب... وذهب...` (multiple positions with فذهب/وذهب)
- `والصحيح` / `والأرجح` / `والراجح` (tarjih markers)
- `ورد عليه` / `وأجاب` / `فضعيف` (refutation markers)

### Example preserved (excerpt 11)

The full اختلاف العلماء passage about وقوع الطلاق في الحيض (jumhur vs. Ibn Taymiyyah/Ibn al-Qayyim) stays as one teaching unit because:
1. Ibn al-Qayyim's refutation references "أدلة الجمهور" — requires the jumhur's evidence in the same unit
2. The tarjih ("ولكن الأرجح ما ذهب إليه جمهور العلماء") depends on the reader seeing all positions
3. The hadith criticism ("وقد استنكر العلماء هذا الحديث") only makes sense adjacent to the hadith it criticizes

### Prevalence

118 excerpts (9.2%) in taysir have khilaf patterns.

---

## Modified Existing Rule: Decontextualization Prevention

### Current rule (SPEC §5.3.2)

> Evidence cited for a ruling MUST stay with the ruling

### Modified rule

> Evidence cited for a ruling MUST stay with the ruling WHEN the evidence is:
> (a) a brief mention (< ~10 words of evidence text), OR
> (b) syntactically fused with the ruling (the "دليل على أن" pattern where evidence and ruling are one grammatical sentence), OR
> (c) inside a khilaf passage governed by DR-3.
>
> Otherwise, substantive evidence MAY be split into its own teaching unit per DR-2.

### Rationale

The original rule prevented ALL evidence splitting. The owner's feedback shows this produces excerpts too coarse for cross-source comparison. The modified rule preserves decontextualization prevention where it matters (brief evidence, fused syntax, khilaf) while allowing granularity where it's safe.

---

## CrossReference Schema Extension

### Current schema (SPEC §2.2.2)

```
CrossReference: {
  reference_text: str,
  target_description: str | null,
  target_div_id: str | null,
  resolved: bool
}
```

### Extended schema

```
CrossReference: {
  reference_text: str,
  target_description: str | null,
  target_div_id: str | null,
  target_excerpt_id: str | null,      # NEW — links to companion excerpt
  relationship_type: str | null,       # NEW — semantic relationship
  resolved: bool
}
```

**`relationship_type` values:**
- `companion_definition` — لغة ↔ شرعا definition pair
- `evidence_for` — evidence unit → ruling unit
- `ruling_proven_by` — ruling unit → evidence unit
- `refutation_of` — refutation → refuted position
- `continuation` — sequential content from same source passage

### When to populate

The new fields are populated by the Phase 3 enrichment step ONLY for teaching units that were split by DR-1 or DR-2. The LLM enrichment call (SPEC §7.2) adds cross-references between split companion units using the source passage context.

For units NOT split by DR-1/DR-2, the existing cross-reference behavior is unchanged.

---

## Implementation Notes for CC

### What changes in the codebase

1. **Phase 2b system prompt** (SPEC §5.3.2): Add DR-1, DR-2, DR-3 rules to the GROUPING RULES section. Modify the decontextualization rule per the modified version above.

2. **CrossReference model** (SPEC §2.2.2): Add `target_excerpt_id: str | null` and `relationship_type: str | null` fields.

3. **Phase 3 enrichment** (SPEC §7.2): Add a step that detects split companion units (units from the same chunk that were adjacent in the original text) and populates cross-references between them.

4. **Tests**: Add test cases for:
   - DR-1: لغة/شرعا definition pair → two teaching units with cross-references
   - DR-2: ruling + substantive Quranic evidence + substantive hadith evidence → three teaching units
   - DR-2 threshold: ruling + brief ijma mention → one teaching unit (not split)
   - DR-3: full khilaf passage → one teaching unit (not split despite multiple evidence types)
   - Modified decontextualization: "دليل على أن" fused syntax → one unit

### What does NOT change

- Three-phase architecture
- Self-containment evaluation criteria (C-SC-1 through C-SC-5)
- Self-containment levels (FULL/PARTIAL/DEPENDENT)
- Phase 1 deterministic preprocessing
- Phase 2a segment classification
- Output contract (ExcerptRecord fields — only CrossReference gets 2 new optional fields)
- Consensus mechanism

---

## Status: Pending Cross-Provider Review

Before implementation, the following adversarial questions must be answered by ChatGPT or Gemini:

1. Would per-evidence-type splitting at the DR-2 threshold (~10 words) lose scholarly meaning? Are there cases where evidence from different categories is so intertwined that splitting destroys the argument?

2. Is the لغة/شرعا split (DR-1) always correct? Are there cases where the linguistic and legal definitions are so interdependent that splitting produces two non-self-contained fragments?

3. Does the ~800-word threshold in DR-3's exception rule make sense? What are the characteristics of khilaf passages that CAN be safely split vs. those that cannot?
