# Cross-Provider Review Prompt: DR Domain Rules

**For:** ChatGPT 5.4 (deep research) and/or Gemini Pro 3.1
**Context:** The KR excerpting engine needs to produce finer-grained teaching units. The architect has designed 3 new domain rules (DR-1, DR-2, DR-3). This prompt asks you to adversarially test them.

---

## Background (read this first)

KR (خزانة ريان) is a personal Islamic scholarly library that processes Arabic source texts into a structured knowledge base. The excerpting engine breaks texts into "teaching units" — self-contained excerpts that each teach one scholarly thought. These excerpts are placed at leaves in taxonomy trees and compared across sources.

**The problem:** The owner reviewed the first batch of 1,283 excerpts from تيسير العلام (a fiqh hadith commentary) and rejected 2 as too coarse:

1. **Definition excerpt**: Combined the linguistic definition (تعريف لغوي) and legal definition (تعريف شرعي) of الطلاق in one excerpt. The owner says these should be separate because they map to different taxonomy leaves.

2. **Evidence excerpt**: Combined the general ruling + Quranic evidence + hadith evidence + ijma + qiyas into one excerpt. The owner wants per-evidence-type granularity for cross-source comparison.

**The architect's solution:** Three new domain rules that recalibrate the grouping prompt. Full details in `engines/excerpting/domain_rules/DR_DOMAIN_RULES.md`. Summary:

- **DR-1 (Definition Pair Splitting):** When a passage has both لغة and شرعا definitions of the same term, split them into separate teaching units if both are substantive (>3 words of definitional content).
- **DR-2 (Evidence-Type Splitting):** When a ruling cites evidence from multiple categories, each category is a separate unit IF the citation is substantive (>~10 words). Brief mentions stay with the ruling.
- **DR-3 (Khilaf Preservation):** Scholarly disagreement passages (اختلاف العلماء) remain as single units when decomposition would lose argumentative structure.

**Self-containment standard (SPEC §3):** Every teaching unit must be understandable by a student who knows the science's basic terminology but doesn't know this specific source or its surrounding text. Five criteria: C-SC-1 (term resolution), C-SC-2 (reference resolution), C-SC-3 (evidence completeness), C-SC-4 (argument completeness), C-SC-5 (dialogue completeness).

---

## Your Task: Adversarial Review

### Question 1: DR-1 — Definition Pair Splitting

Consider this text from كتاب الصلاة:
```
الصلاة -في اللغة- الدعاء. قال القاضي عياض: هو قول أكثر أهل العربية والفقهاء. وتسمية الدعاء صلاة معروف في كلام العرب. والعلاقة بين الدعاء والصلاة الجزئية. فإن الدعاء جزء من الصلاة، لأنها قد اشتملت عليه.
وفي الشرع: "أقوال وأفعال مفتتحة بالتكبير ومختتمة بالتسليم مع النية".
```

Under DR-1, this becomes two units. The لغوي unit includes the scholarly discussion about the term's usage. The شرعي unit is just one sentence.

**Adversarial questions:**
- Is the لغوي unit self-contained without the شرعي definition? (Yes/No and why)
- Is the شرعي unit self-contained without the لغوي definition? The شرعي unit starts with "وفي الشرع" — a backward reference. Is a context_hint sufficient to resolve this?
- The sentence "والعلاقة بين الدعاء والصلاة الجزئية" discusses the relationship between the two meanings. DR-1 places it in the لغوي unit. Should it instead be in the شرعي unit (since it explains how the legal meaning relates to the linguistic one)?
- Are there cases where لغة and شرعا definitions are so interdependent that splitting produces two fragments that neither make sense alone? Provide an example if you can find one.

### Question 2: DR-2 — Evidence-Type Splitting (Threshold)

DR-2 uses ~10 words as the substantive threshold. Consider these real examples:

**A. Brief mention (stays with ruling under DR-2):**
```
والأمة مجمعة عليه
```
(4 words — stays with ruling)

**B. Substantive citation (split under DR-2):**
```
فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات
```
(~10 words with a specific verse citation — split)

**C. Borderline case:**
```
وأما السنة، فقوله صلى الله عليه وسلم: {أبغض الحلال إلى الله الطلاق} وغيره من فعله وتقريره صلى الله عليه وسلم.
```
(~15 words with a specific hadith — split)

**Adversarial questions:**
- Is the ~10 word threshold appropriate? Too high (misses useful evidence)? Too low (creates trivially thin excerpts)?
- For case B: the excerpt "فأما الكتاب فنحو {الطلاقُ مَرتَانِ} وغيرها من الآيات" — is this USEFUL as a standalone unit at the leaf "الاستدلال من الكتاب"? It says "like the verse {divorce is twice} and other verses" — is this enough scholarly content to be worth an excerpt?
- For case C: is a hadith citation that says "like his saying {the most hated of lawful things to Allah is divorce}" useful standalone? Or does the reader need more context about how this hadith proves the ruling?
- Are there evidence categories that CANNOT be separated from their ruling even when substantive? For example: qiyas (rational analogy) — the analogy's conclusion IS the ruling. Can qiyas evidence ever be a standalone unit?

### Question 3: DR-3 — Khilaf Preservation

Consider this passage (excerpt 24 from taysir):
```
اختلاف العلماء:
اختلف العلماء هل للبائن نفقة وسكنى، زمن العدة، أو لا؟
فذهب الإمام أحمد: إلى أنه ليس لها نفقة، ولا سكنى، وهو قول علي، وابن عباس، وجابر.
وبه قال عطاء، وطاوس، والحسن، وعكرمة، وإسحاق، وأبو ثور وداود، مستدلين بحديث الباب.
وذهب الحنفية إلى أن لها النفقة والسكنى... مستدلين بما روى عن عمر...
وذهب مالك، والشافعي، إلى أن لها السكنى دون النفقة... مستدلين بقوله تعالى: {أسكنوهن...}
والصحيح، هو القول الأول، لقوة الدليل وعدم المعارض.
فأما القول الثاني فضعيف، لأن هذه الكلمة التي استدلوا بها، لم تثبت عن عمر.
[...refutation of position 3...]
```

DR-3 keeps this as one unit.

**Adversarial questions:**
- Would a student benefit MORE from seeing all three positions together (DR-3), or from being able to compare each position separately across sources?
- If this passage were split into 3 position-units + 1 tarjih-unit, what information would be lost? Is C-SC-5 (dialogue completeness) truly violated if each position-unit includes the question being debated?
- The ~800-word threshold for the exception — what scholarly basis exists for this number? Should it be based on the number of positions rather than word count?
- Are there short khilaf passages (<200 words) where splitting IS appropriate because each position is genuinely self-contained?

### Question 4: Cross-Genre Applicability

The taysir examples are all fiqh. The KR library also covers nahw (grammar), sarf (morphology), balagha (rhetoric), usul al-fiqh, aqidah (theology), and more.

**Adversarial questions:**
- In nahw texts, the "evidence" is grammatical شواهد (Quranic verses, poetry). Does DR-2 apply to nahw? Can a grammatical شاهد be meaningful without the rule it demonstrates?
- In usul texts, "evidence" for a methodological principle is often a chain of reasoning. Does DR-2's substantive threshold make sense for rational arguments?
- In balagha, the "evidence" is literary analysis of a text. Can a rhetorical analysis be separated from the figure it demonstrates?
- Are there sciences where DR-1 (definition splitting) should NOT apply? For example, if a science has no لغة/شرعا distinction?

### Question 5: Overall Assessment

- Does this set of rules (DR-1 + DR-2 + DR-3 + modified decontextualization) produce the right balance between granularity and self-containment?
- What failure modes do you foresee? What excerpts would be produced that shouldn't be?
- Is there a case the rules don't cover that should be addressed?

---

## Files to Reference

If you have access to the KR repo (`github.com/rayanino/kr`):
- `engines/excerpting/domain_rules/DR_DOMAIN_RULES.md` — full rules with examples
- `integration_tests/campaign_20260331/analysis/scholarly_reality_check_intra_excerpt.md` — the full analysis
- `integration_tests/campaign_20260331/taysir/owner_feedback.jsonl` — the owner's original comments
- `engines/excerpting/SPEC.md` §3 (self-containment) and §5.3 (grouping rules)
