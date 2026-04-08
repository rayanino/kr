# Drawing the Boundary Between Nahw and Sarf in Classical Scholarship

## Why the boundary is genuinely contested in the tradition

A key bottleneck is that *the earliest “grammar” tradition did not cleanly separate* what later curricula call **naḥw** (syntax/inflection) and **ṣarf/taṣrīf** (morphology). In other words, “naḥw” is sometimes used historically as an umbrella for what later becomes two sciences.

A foundational illustration is Ibn Jinnī’s well-known definition of *naḥw* in **al-خصائص**. He defines naḥw as *imitating the path of Arabic speech* in “iʿrāb **and other**” processes, and he explicitly lists among those “other” processes: dual, plural, diminutive, broken plural, iḍāfa, nisba, and composition/compounding. That definition makes *naḥw* (in his framing) a broad “science of Arabic correctness,” not merely “word-final case endings and sentence roles.” citeturn10view0turn12search2

Likewise, in **Sībawayh’s al-Kitāb**, the work’s internal organization includes substantial material that later readers classify as morphological “abniya” and patterning. Crucially for your boundary question, Sībawayh himself (in a morphological/patterning chapter) uses wording that distinguishes what “the grammarians call taṣrīf,” indicating that “taṣrīf” is a recognized analytic subdomain living inside the larger grammarian’s enterprise rather than a fully separate science at that early stage. citeturn5view0

By the 3rd/9th century and later, a distinct **taṣrīf/sarf** book tradition becomes visible. A common reference point (in later histories of the Arabic linguistic library) is the claim that **entity["people","Abu Uthman al-Mazini","basran grammarian d.249h"]’s** Kitāb al-Taṣrīf is among the earliest *independent* works focused on morphological patterns that has reached us, and it is discussed as a milestone in the emergence of “ṣarf as its own lane.” citeturn21view0

So you are not just managing “topic overlap.” You are formalizing a *later partition* of an earlier, more blended conceptual space.

## Classical boundary formulations you can treat as “formal rulesets”

You asked for “formal scholarly rules” (ḥudūd / ضوابط) rather than a modern textbook slogan. The most taxonomy-useful approach is to extract **several classical boundary logics** (which really are *different rulings*), then choose an “operational ruling” for your trees.

### The inclusive (early) ruling: “naḥw covers iʿrāb and the rest of Arabic word/sentence behavior”

This is the ruling implicit in Ibn Jinnī’s definition: naḥw includes iʿrāb **and** many word-form processes that later become “ṣarf.” Under this ruling:

- Dual/plural formation, diminutives, broken plurals, nisba, iḍāfa-related behavior, etc., can all sit under “naḥw” (as a general science of Arab speech norms). citeturn10view0turn12search2

This is historically important because it justifies why classical scholars can “disagree” about where the boundary is: sometimes they are not disagreeing about a *line* but about *which definition of naḥw they’re using*.

### The “two-kinds-of-change” ruling: naḥw as a science of changes, split into (a) end-changes (iʿrāb) vs (b) body-changes (what later readers call ṣarf)

A particularly explicit, structurally *formalizable* boundary appears in entity["people","Abu Ali al-Farisi","arab grammarian d.377h"]’s statement (preserved in his **entity["book","al-Takmila","arabic grammar supplement"]**, here via a digitized text witness). He defines naḥw as a science of analogical measures inferred from Arabic usage and says it “divides into two”:

1) **Change that affects the *ends* of words**, and  
2) **Change that affects the *bodies/selves* of words** (ذوات الكلم وأنفسها). citeturn16view0

He then subdivides “end-changes” into:

- end-changes **caused by differing ʿawāmil** (and he identifies that as what is called **iʿrāb**), versus  
- end-changes that occur **without** differing ʿawāmil (e.g., moving a sukūn, adding/removing/replacing letters, etc.). citeturn16view0

For taxonomy purposes, this is gold, because it gives you a decision procedure more precise than “internal vs final.” It says: *even word-final phenomena may fall on the non-iʿrāb side if they are not ʿāmil-governed.*

### The later “mutʾakhkhirūn” boundary: ṣarf = word-pattern states excluding iʿrāb/bina; naḥw = iʿrāb/bina and تركيب

A canonical later boundary is embedded in the standard definition attributed to entity["people","Ibn al-Hajib","arab grammarian d.646h"] and explained by entity["people","Radi al-Din al-Astarabadi","arab grammarian d.686h"] in **entity["book","Sharh Shafiyat Ibn al-Hajib","morphology commentary"]. The definition is:

> **Taṣrīf is a science of principles by which one knows the states of word-patterns (أحوال أبنية الكلم) that are not iʿrāb.** citeturn22view0

And al-Astarabadi explicitly reports a later (“mutʾakhkhirūn”) expansion: ṣarf concerns the word’s pattern and what happens to its letters—original vs extra, addition/deletion, soundness vs weak/ʿilal, assimilation/idghām, vowel tendencies like imāla—**and also what may occur at the word’s end that is not iʿrāb nor bina**, such as الوقف and related matters. citeturn22view0

This matters because it *formally licenses* placing some “word-final” phenomena into ṣarf, as long as they are **not** iʿrāb/bina.

Finally, the definitional literature (*ḥudūd*) also encodes the later “tarkīb” emphasis. For example, entity["people","Ali ibn Muhammad al-Jurjani","lexicographer d.816h"] defines naḥw as laws by which one knows the states of Arabic constructions regarding iʿrāb and bina (and related things). citeturn23search7  
In the same work, “ṣarf” is defined more narrowly (e.g., as knowledge of word states with respect to iʿlāl), which reflects a common later compression: ṣarf is a word-form science. citeturn23search2

## Boundary rules you can operationalize for taxonomy ownership

Below is a rule-set that is (a) faithful to the classical “two-kinds-of-change” logic and (b) implementable as deterministic ownership tests.

### Owner test based on the explanatory lever

**Rule A (ʿāmil / iʿrāb / bina = naḥw).**  
If the topic’s core explanatory mechanism depends on **العامل** (governance), or the phenomenon is defined as **a change (or non-change) at the word’s end due to syntactic position**, then it belongs to **naḥw**. This is exactly the “end-change by differing ʿawāmil = iʿrāb” rule in entity["people","Abu Ali al-Farisi","arab grammarian d.377h"]’s partition, and it matches Ibn Jinnī’s definition of iʿrāb as a meaning-disambiguator realized by case differences. citeturn16view0turn10view0

**Rule B (pattern/letters/derivation/phonology not governed by ʿāmil = ṣarf).**  
If the topic’s explanatory mechanism is: أصل/زيادة, وزن/بنية, إعلال/إبدال/إدغام, صوغ (formation rules), أو توليد الألفاظ من المفرد (derivation), and it is not defined as an ʿāmil-driven syntactic alternation, then it belongs to **ṣarf**. This aligns with the Ibn al-Ḥājib → al-Astarabadi definition “states of word-patterns not iʿrāb,” and with the later expansion that ṣarf includes letter-level operations and even some word-final phenomena that are not iʿrāb/bina. citeturn22view0turn16view0

**Rule C (word-final but not iʿrāb/bina often still = ṣarf).**  
A common weak assumption is “word-final = naḥw.” Classical boundary texts explicitly disrupt that: al-Astarabadi’s نقل عن المتأخرين places **وقف** and similar word-final behaviors under ṣarf precisely because they are not iʿrāb/bina. citeturn22view0turn16view0

### Split rule for “true overlaps”

**Rule D (if one concept contains two different questions, split by question-type).**  
If a single label (e.g., “dual”) bundles two different analytical questions:

- **How is the form built?** (صوغ/بنية) → ṣarf  
- **How does that form behave syntactically (iʿrāb / governance / agreement / distribution)?** → naḥw

…then your taxonomy should not treat it as one overlapping leaf. It should become **two distinct leaves**, one per science, each with a tight scope statement and cross-reference. This split is already anticipated by the classical “two-kinds-of-change” framing: internal formation vs end/role behavior. citeturn16view0turn22view0

## Formal ownership rulings for your overlap topics

I’ll rule these using Rules A–D above, and I’ll explicitly separate “single-owner” vs “split-as-two-leaves” cases.

### المبني والمعرب

**Owner: naḥw (single-owner), with a required term-disambiguation note.**

Ibn Jinnī defines **البناء** (in the naḥw sense) as *the end of the word adhering to one state* (sukūn or a single vowel) **not caused by ʿawāmil**, contrasted with iʿrāb’s alternation. citeturn10view0  
That definition is quintessentially “end-state as a function of syntactic governance vs non-governance,” i.e., Rule A.

**Disambiguation requirement:** the word **بناء** is polysemous across sciences:

- **بناء (naḥw):** indeclinability vs declinability (آخر الكلمة، عوامل) citeturn10view0  
- **بنية/أبنية/بناء (ṣarf usage):** pattern/shape of the word (وزن/هيئة), which is squarely ṣarf per the “أحوال أبنية الكلم” framing. citeturn22view0turn16view0  

Taxonomically: keep *mabnī vs muʿrab* under naḥw, but ensure your ṣarf tree uses **بنية/وزن/أبنية** consistently for the pattern sense to avoid homonym collisions.

### التعريف والتنكير

**Owner: naḥw (single-owner).**

In classical grammatical teaching, “النكرة والمعرفة” is treated as a core naḥw chapter because it is primarily about **distribution and تركيب-based consequences** (e.g., which noun types can function as مبتدأ, how definiteness interacts with iḍāfa, etc.), not about word-pattern mechanics. A representative classical locus is entity["people","Ibn Aqil","arab grammarian d.769h"]’s discussion of “النكرة والمعرفة” in his Alfiyya commentary, where the topic is organized as a syntactic-semantic classification of noun types (ضمير، اسم إشارة، علم، محلى بـ أل، موصول، والمضاف إلى واحد من هذه). citeturn24search0

The decisive boundary point is: the topic’s *core explanations* are about **noun reference types and their grammatical behavior inside constructions**, rather than letter-level formation or abniya. That’s Rule A-by-structure (tarkīb-centered naḥw) plus the al-Jurjānī definition linking naḥw to أحوال التراكيب من الإعراب والبناء وما يتصل بها. citeturn23search7

### الاشتقاق

**Owner: ṣarf (core), with a structural cross-reference into naḥw for “working/ʿamal” behavior of مشتقات.**

Classical morphology definitions often treat taṣrīf as “turning a single word into multiple forms to express multiple meanings.” In the same definitional block cited above, al-Astarabadi quotes entity["people","Abd al-Qahir al-Jurjani","arab rhetorician d.471h"] defining taṣrīf as “تصرف الكلمة المفردة فتتولد منها ألفاظ مختلفة ومعان متفاوته.” That is essentially a derivational (ishtiqāq-like) conception: generating forms/meanings from a base. citeturn22view0

So: **ishtiqāq-as-word-formation** belongs to ṣarf under Rule B.

However, many derivative categories (اسم فاعل، اسم مفعول، صيغ مبالغة، إلخ) have **syntactic “ʿamal” behaviors** (e.g., when an اسم فاعل governs a معموله). Those behaviors are naḥw by Rule A because the mechanism becomes تركيب/عمل/معمول and governance inside sentences, not word formation. This is exactly why classical pedagogy often discusses “المشتقات العاملة” in naḥw contexts while their formation lives in ṣarf contexts (a split consistent with Rule D). citeturn16view0turn22view0

**Practical ruling:** keep a single “الاشتقاق” leaf in ṣarf that owns:
- derivational theory (اشتقاق أصغر/أكبر/كبير if you include it),
- formation of مشتقات,
- constraints on derivation.

Then, in naḥw, do *not* duplicate “الاشتقاق”; instead point to ṣarf, and keep naḥw leaves that own only the **ʿamal/distribution** questions (عمل اسم الفاعل…).

### التثنية والجمع

**Owner: split into two leaves (one per tree), not duplicated content.**

This one is the archetype of Rule D.

1) **Formation (ṣarf):** how the dual is formed, how sound plurals are formed, patterns of broken plurals, phonological adjustments in formation, etc. These are “أحوال أبنية الكلم” operations. citeturn22view0

2) **Inflectional behavior (naḥw):** how dual and sound plurals participate in iʿrāb (e.g., letters substituting for vowels, النيابة في العلامات). Ibn Jinnī explicitly frames alif of dual and wāw/yāʾ of plurals as *nāʾib* (substituting) for vowel-case markers and comments that the locus of iʿrāb is “for the vowels,” with letters entering as substitutes. This is iʿrāb logic (Rule A). citeturn0search2

**Ruling statement you can encode:**  
- “Dual/plural **as sīgha (form)** → ṣarf.”  
- “Dual/plural **as iʿrāb-sign system / syntactic case realization** → naḥw.” citeturn22view0turn0search2

### النسب

**Owner: ṣarf (single-owner), with a narrow cross-reference from naḥw only if you have a dedicated “adjectivalization” module.**

“Nisba” is, at root, an **affixational derivation** (adding ياء النسب, and the letter/vowel transformations that come with it). That is a textbook case of “تصرف الكلمة المفردة” and “أحوال أبنية الكلم” in the Ibn al-Ḥājib/al-Astarabadi framing. citeturn22view0

Where nisba later shows up in naḥw is mostly *not unique to nisba*—it is the general naḥw of adjectives (النعت), agreement, and syntactic placement. Those are not “nisba-specific” enough to justify duplicating the nisba leaf inside naḥw; instead, your naḥw “نعت” system can simply treat nisba-words as one subclass of adjectives.

**So:** keep “النسب (ياء النسب)” in ṣarf; in naḥw, if needed, add a cross-reference note under “النعت” like “nisba adjectives follow the general adjective rules; see ṣarf for formation.” This matches Rule D’s “do not duplicate; link unless the question changes.”

## Should overlaps exist in both trees or only one tree should own them?

Your design choice should depend on whether the “overlap” is **semantic overlap** (same label, two different questions) or **true duplication** (same question repeated).

### When a topic should appear in both trees

Only when the *label* names a domain that contains **two separable questions** that map to different sciences (Rule D). “التثنية والجمع” is exactly such a case: formation vs iʿrāb behavior. citeturn16view0turn0search2turn22view0

In that scenario, you should not “duplicate one leaf.” Instead you maintain:
- a ṣarf leaf whose scope is explicitly “الصوغ/البنية,” and
- a naḥw leaf whose scope is explicitly “علامات الإعراب/العمل/التراكيب.”

They are different leaves with different question-types, so you avoid drift.

### When a topic should have one owner only

When the topic is *fundamentally* defined by one science’s explanatory lever (Rule A or Rule B), e.g.:

- **المبني والمعرب** (naḥw) because it is literally defined as an end-state contrasted with iʿrāb and tied to ʿawāmil vs non-ʿawāmil framing. citeturn10view0turn16view0  
- **النسب** (ṣarf) because it is an affixational derivation and letter-level transformation, while its naḥw behavior is just adjective behavior. citeturn22view0  
- **التعريف والتنكير** (naḥw) because it is treated as a core classificatory chapter in syntactic grammar works and tied to constructional behavior. citeturn24search0turn23search7  

### Strong recommendation for taxonomic stability

For a pair of large trees (183 validated leaves vs 226 unvalidated leaves), *full duplication of the same question* in both trees is a predictable source of drift: definitions evolve, edge-cases get patched in one place, examples diverge.

So the stable pattern is:

- **One canonical owner leaf** for each *question-type*.  
- **Cross-references** (pointers) from the other tree where users would reasonably look for it.

This “canonical + pointer” model is the closest analogue to what classical literature actually did: even when scholars treated the whole as “naḥw,” they still recognized subdomains (“what grammarians call taṣrīf” inside al-Kitāb). citeturn5view0turn10view0

## A general rule you can apply to future overlap cases

Here is a concise decision procedure you can apply mechanically. It is designed to be faithful to (i) al-Fārisī’s “two kinds of change,” (ii) Ibn al-Ḥājib/al-Astarabadi’s “abniya not iʿrāb,” and (iii) the explicit exception that some word-final matters belong to ṣarf if not iʿrāb/bina. citeturn16view0turn22view0

### Step-based classifier

**Step one: identify the locus of the rule’s variable.**  
Ask: “What is actually varying?”

- If what varies is **syntactic role marking / case / mood / governance outcomes**, you are in naḥw territory (Rule A). citeturn16view0turn10view0turn23search7  
- If what varies is **the word’s internal pattern/letters/vowels/derivation**, you are in ṣarf territory (Rule B). citeturn22view0turn23search2  

**Step two: check the causal lever (ʿāmil test).**  
Ask: “Would the phenomenon change because the word moved to a different syntactic position or received a different ʿāmil?”

- **Yes → naḥw** (iʿrāb logic). citeturn16view0turn10view0  
- **No → likely ṣarf**, even if the change is at the end of the word. citeturn22view0turn16view0  

**Step three: explicitly guard against the ‘word-final = naḥw’ fallacy.**  
If the topic is word-final, ask: “Is it iʿrāb/bina, or is it something like الوقف/phonological conditioning?”

- If it is **iʿrāb/bina → naḥw**. citeturn10view0turn23search7  
- If it is **not iʿrāb/bina (e.g., الوقف) → ṣarf** per mutʾakhkhirūn’s inclusion. citeturn22view0turn16view0  

**Step four: if both levers are present, split by question-type (don’t duplicate).**  
If the label naturally prompts both:
- “How do we *form* X?” and
- “How does X *behave syntactically* once formed?”

…create two leaves, one per tree, and cross-reference. That implements the classical two-domain model explicitly rather than letting it sit as an ambiguous “overlap.” citeturn16view0turn22view0turn0search2

### One-sentence operational boundary rule

A compact rule you can apply to future overlaps:

**ṣarf owns rules whose primary explanation is word-form architecture (abniya/letters/derivation/phonology) independent of ʿawāmil; naḥw owns rules whose primary explanation is syntactic positioning/governance and the resulting iʿrāb/bina—even if the surface marker is just one letter at the word’s end.** citeturn22view0turn16view0turn10view0