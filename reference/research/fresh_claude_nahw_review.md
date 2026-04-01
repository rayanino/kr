# Nahw Taxonomy Tree — Adversarial Cold-Read Review

**Reviewer:** Fresh Claude Opus (cold-read, zero prior context)
**Date:** 2026-04-01
**Tree reviewed:** `reference/research/chatgpt_nahw_v2_synthesis.yaml`
**Verdict:** NOT READY — 3 required fixes before commit (all mechanical, <20 min total)
**Confidence:** HIGH

---

## Executive Summary

Across 8 systematic checks using 40+ tool calls (YAML parsing, corpus cross-referencing, web verification, engine loading, normalized string matching), I found:

- **0 HIGH-severity findings**
- **3 MEDIUM-severity findings** (all fixable in under 20 minutes combined)
- **4 LOW-severity findings**
- **2 organizational preferences** (non-blocking opinions)

The tree's architecture, scholarly coverage, and sarf boundary are sound. The 3 required fixes are mechanical — not architectural.

### Key Strengths
- 15/15 sampled leaves verified as real nahw topics (zero fabrication)
- Zero coverage gaps in ALL topics appearing in 10+ of 302 corpus books
- Zero sarf leaks — all 13 mandatory morphology markers absent
- Zero objective organizational misplacements
- Excellent sibling distinctness — only 1 partial overlap in 93 examined leaves
- Loads successfully in the KR taxonomy engine (182 leaves, version nahw_v2_0)
- Follows canonical nahw organization (النحو الوافي + ألفية ابن مالك)
- Clean, consistent structure: 9 L1 / 56 L2 / 182 leaves, all at depth 3

---

## Tree Overview (from YAML parsing)

| Metric | Value |
|--------|-------|
| Total nodes | 247 |
| L1 branches | 9 |
| L2 topics | 56 |
| Leaves (all at depth 3) | 182 |
| Max depth | 3 (perfectly uniform) |
| Confidence: HIGH | 147 leaves |
| Confidence: MEDIUM | 35 leaves |
| Confidence: LOW/MISSING | 0 |
| Tree ID | nahw_v2_0 |
| Methodology | 4-researcher synthesis (2 knowledge + 2 corpus, 302 books) |

### L1 Branch Summary

| # | Branch | Leaves | L2 Topics |
|---|--------|--------|-----------|
| 1 | مبادئ النحو وأحكام الإعراب | 18 | 3 |
| 2 | الأسماء والتعريف | 19 | 7 |
| 3 | الجملة الاسمية ونواسخها | 28 | 7 |
| 4 | الجملة الفعلية وأحكام الفعل | 18 | 6 |
| 5 | المنصوبات والمتعلقات | 25 | 8 |
| 6 | الجر والإضافة | 9 | 2 |
| 7 | الأسماء العاملة والمشتقات العاملة | 13 | 5 |
| 8 | التوابع والبيان | 13 | 4 |
| 9 | الأساليب النحوية والأبواب الخاصة | 39 | 14 |

---

## Check 1: Structural and Mechanical Soundness

### Passed (11 checks)

1. **YAML parses cleanly** with `yaml.safe_load` — no errors.
2. **Every non-leaf has `children`, every leaf has `leaf: true`** — 247 nodes traversed, zero violations.
3. **All 247 IDs are unique** — checked via `Counter`, zero duplicates.
4. **All IDs comply with `[a-z_][a-z0-9_]*` format** — regex-verified, zero violations.
5. **Consistent key patterns** — all 65 branches have `{id, title, children}`, all 182 leaves have `{id, title, leaf, confidence}`. No unexpected keys.
6. **No MISSING or LOW confidence leaves** — 147 HIGH, 35 MEDIUM, 0 other.
7. **Tree loads successfully in the KR taxonomy engine** — `load_tree()` returned 182 leaves, version `nahw_v2_0`.
8. **`all_leaves` and `leaf_by_path` are consistent** — 182 = 182.
9. **Perfectly uniform 3-level depth** — Depth 1: 9 branches, Depth 2: 56 branches, Depth 3: 182 leaves. No ragged edges.
10. **Confidence distribution** — all 182 leaves have labels (147 HIGH, 35 MEDIUM).
11. **Leaf enumeration** — all leaves reachable, paths well-formed (e.g., `mabadi_al_nahw.../al_kalam.../hadd_al_kalam...`).

### Findings

**F-1 (MEDIUM): 3 leaves have identical Arabic titles to their parent nodes.**

The leaves `asma_al_ishara_nizaman`, `kana_wa_akhawatuha_nizaman`, and `inna_wa_akhawatuha_nizaman` share their parent's exact Arabic title. The `_nizaman` ID suffix is an artificial disambiguator with no semantic meaning — not Arabic, not English. The owner would see a branch and a leaf both labeled identically with no way to distinguish them. Verified by Python script comparing child titles to parent titles.

**F-2 (LOW): 2 single-child nodes.**

- المعرّف بأل → only child: أل التعريف وأقسامها
- الاختصاص → only child: المنصوب على الاختصاص

In both cases the parent branch wraps exactly one leaf — structurally redundant. The leaf could be promoted to L2 level. Organizational preference, not blocking.

**F-3 (MEDIUM): v2.0 tree is missing `language`, `policy`, and `id_policy` fields present in v1.0.**

Comparison of v1.0 (`library/sciences/nahw/tree.yaml`) and v2.0 top-level keys:
- v1.0 keys: `['id', 'id_policy', 'language', 'nodes', 'policy', 'title']`
- v2.0 keys: `['date', 'id', 'methodology', 'nodes', 'title', 'validated']`
- **In v1 but NOT v2:** `['id_policy', 'language', 'policy']`

The v1.0 policy content:
```yaml
language: ar
policy:
  leaf_atomic: true
  single_core_node_per_excerpt: true
  exclude_cross_science_nodes: true
  allow_rhetorical_treatment_only: false
```

The tree loader accepted v2 without these (schema-optional), but when v2 replaces v1 as the active tree, the placement engine needs these policies.

**F-4 (LOW, initially flagged as HIGH, revised after Check 3):**

The leaf inventory plan proposed 147 leaves; the tree has 182 (+35). Several planned topics were dropped:
- إعراب الجمل (6 books as standalone heading — low frequency)
- الاستفهام as general topic (3 books standalone)
- لو الشرطية, لولا ولوما, أمّا التفصيلية (9 books — captured separately as F-5)
- أن المضمرة (not standalone)
- نظرية العامل (1 book standalone)

Corpus evidence showed most dropped topics have very low standalone frequencies (1-6 books), so the drift is justified. Downgraded from HIGH to LOW.

---

## Check 2: Scholarly Reality Verification

### Method
15 leaves selected at evenly-spaced indices (0, 12, 24, 36, 48, 60, 72, 84, 97, 109, 121, 133, 145, 157, 169) from the 182 total, spanning all 9 L1 branches, including 3 MEDIUM-confidence leaves.

### Results: 15/15 PASS (100%)

| # | Idx | Leaf Title | Conf. | Verification | Result |
|---|-----|-----------|-------|-------------|--------|
| 1 | 0 | حدّ الكلام والكلم والكلمة والقول | HIGH | Web: Wikipedia "الكلام (نحو)", multiple grammar sites | ✅ |
| 2 | 12 | الأسماء الستة | HIGH | Web: Shamela شرح الآجرومية, Mawdoo3, Wiki University | ✅ |
| 3 | 24 | نون الوقاية | MED | Web: Wikipedia article, النحو الوافي §21, شرح ألفية العثيمين | ✅ |
| 4 | 36 | صرف الممنوع من الصرف | HIGH | Web: Wikipedia, Mawdoo3, النحو الواضح | ✅ |
| 5 | 48 | لا العاملة عمل ليس | MED | Web: باحثو اللغة العربية, أكاديمية مكاوي | ✅ |
| 6 | 60 | أفعال القلوب | HIGH | Web: Wikipedia article; Corpus: 5 books | ✅ |
| 7 | 72 | رجحان نصب المشغول عنه | HIGH | Corpus: الاشتغال in 14 books | ✅ |
| 8 | 84 | تقديم المفعول به وتأخيره | HIGH | Corpus: المفعول به in 24 books | ✅ |
| 9 | 97 | الاستثناء المفرغ | HIGH | Web: Mawdoo3, Shamela; Corpus: الاستثناء in 36 books | ✅ |
| 10 | 109 | حروف الجر الزائدة وشبه الزائدة | HIGH | Corpus: حروف الجر in 32 books | ✅ |
| 11 | 121 | معمول اسم الفاعل وأحكامه | HIGH | Corpus: اسم الفاعل in 36 books | ✅ |
| 12 | 133 | قطع النعت | MED | Web: النحو العربي; Corpus: النعت in 37 books | ✅ |
| 13 | 145 | توابع المنادى | HIGH | Corpus: النداء in 35 books | ✅ |
| 14 | 157 | الإغراء | HIGH | Corpus: التحذير والإغراء in 17 books | ✅ |
| 15 | 169 | العدد المركب | HIGH | Corpus: العدد in 35 books | ✅ |

**Zero potentially fabricated topics found.** Every leaf — including all 3 MEDIUM-confidence ones — was verified as a real nahw topic discussed in named Arabic grammar books.

---

## Check 3: Coverage Completeness

### Method
Cross-referenced every corpus topic (302 books, 70,001 headings, 37,882 unique topic clusters) against the tree using normalized Arabic string matching (hamza/diacritics/singular-plural normalization), then manually verified every potential gap.

### Coverage by frequency tier

| Frequency Tier | Corpus Topics | In Tree | Sarf Exclusion | Generic | Genuine Gap |
|---|---|---|---|---|---|
| 50+ books | 2 | 2 | 0 | 0 | **0** |
| 40–49 books | 4 | 4 | 0 | 0 | **0** |
| 30–39 books | 17 | 12 | 4 | 1 | **0** |
| 20–29 books | 33 | 28 | 5 | 0 | **0** |
| 15–19 books | 22 | 22* | 0 | 0 | **0** |
| 10–14 books | 97 | ~70 | ~20 | ~7 | **0** |

*After correcting for Arabic spelling normalization (initial false negatives: اسم الاشاره → أسماء الإشارة, ان واخواتها → إن وأخواتها, etc.)

**Result: Zero genuine nahw gaps in any frequency tier ≥10 books.**

### Sarf exclusions (correct — 9 topics)

| Topic | Books | Classification |
|-------|-------|---------------|
| التصغير | 33 | Sarf (diminutive formation) |
| الوقف | 31 | Sarf (pausal forms) |
| الإمالة | 29 | Sarf (vowel tilting) |
| النسب | 28 | Sarf (nisba affiliation) |
| جمع التكسير | 27 | Sarf (broken plural patterns) |
| المقصور والممدود | 26 | Sarf (morphological form) |
| الإدغام | 26 | Sarf (assimilation) |
| الإبدال | 23 | Sarf (letter substitution) |
| التصريف | 20 | Sarf (conjugation) |

The corpus gaps file itself notes: "the nahw/sarf boundary is porous in practice — many grammar books include morphological topics as integral chapters."

### Finding

**F-5 (MEDIUM): أمّا ولولا ولوما absent from tree.**

Non-jazm conditional particles appear as a standalone chapter ("أمّا ولولا ولوما") in 9/302 corpus books. The tree's only conditional leaf is "أدوات الشرط الجازمة وجواب الشرط" which explicitly covers only jazm-inducing conditions. Excerpts from books discussing "لولا وجوابها" or "أمّا التفصيلية" have no placement target.

This is the only genuine coverage gap found across all frequency tiers.

---

## Check 4: Sarf Boundary Verification

### Mandatory sarf markers — ALL 13 ABSENT ✅

| Marker | Meaning | In Tree? |
|--------|---------|----------|
| تصريف | conjugation | ✅ Absent |
| إعلال | vowel weakening | ✅ Absent |
| إبدال | letter substitution | ✅ Absent |
| إدغام | assimilation | ✅ Absent |
| أبنية | morphological patterns | ✅ Absent |
| نسب | nisba affiliation | ✅ Absent |
| تصغير | diminutive | ✅ Absent |
| وقف | pausal forms | ✅ Absent |
| إمالة | vowel tilting | ✅ Absent |
| تكسير | broken plural | ✅ Absent |
| ممدود | extended form | ✅ Absent |
| مقصور | shortened form | ✅ Absent |
| تأنيث | feminization | ✅ Absent |

### Broader scan — 11 hits from markers صرف, صيغ, مصدر

All 11 classified as NAHW (KEEP) — shared terminology, not sarf leaks:

**صرف hits (4):**
- ما لا ينصرف (L2 branch): صرف here = nunation/declension (syntactic). شرح ألفية ابن مالك: "هذا الباب خاتمة الأبواب عند النحاة" — explicitly nahw.
- علل منع الصرف: Reasons for diptosis — syntactic declension rules.
- صرف الممنوع من الصرف: When diptotes regain nunation (with أل or إضافة) — syntactic behavior.
- الظرف المتصرف وغير المتصرف: Whether adverbs can be used outside adverbial position — purely syntactic.

**صيغ hits (3):**
- صيغ المبالغة العاملة: About syntactic governance (عمل), not morphological formation.
- صيغة ما أفعل: Exclamation formula — a syntactic construction under أساليب نحوية.
- صيغة أفعل به: Second exclamation formula — same reasoning.

**مصدر hits (4):**
- ما ينوب عن المصدر في المفعول المطلق: Substitutes for the verbal noun as absolute object — syntactic function.
- إعمال المصدر (L2 branch): Verbal noun governing complements — syntactic topic.
- شروط إعمال المصدر: Conditions for masdar governance — syntactic.
- إعمال اسم المصدر: Governance of اسم المصدر — syntactic.

### Debatable exclusions — all correct

- **جمع التكسير** (27 books): Correctly excluded. باحثو اللغة العربية describes it as "نظامًا صرفيًا غنيًا ومعقدًا."
- **المقصور والممدود** (26 books): Correctly excluded. About morphological form (alif endings), not syntactic function.
- **التصغير** (33 books): Correctly excluded. Diminutive formation is pure sarf.
- **النسب** (28 books): Correctly excluded. Nisba formation is pure sarf.

**Zero sarf leaks. Clean boundary.**

---

## Check 5: Organizational Critique

### 1. L1 Coherence — ALL COHERENT

Every L1 branch maps cleanly to a classical textbook chapter grouping. Verified against النحو الوافي (48 chapters) and ألفية ابن مالك order:

| L1 | Classical Equivalent | Coherent? |
|----|---------------------|-----------|
| مبادئ النحو وأحكام الإعراب | مقدمات النحو | ✅ |
| الأسماء والتعريف | النكرة والمعرفة | ✅ |
| الجملة الاسمية ونواسخها | المبتدأ والخبر + النواسخ | ✅ |
| الجملة الفعلية وأحكام الفعل | الفاعل + المتعدي واللازم | ✅ |
| المنصوبات والمتعلقات | المفاعيل + الحال + التمييز | ✅ |
| الجر والإضافة | المجرورات | ✅ |
| الأسماء العاملة والمشتقات العاملة | إعمال المشتقات | ✅ |
| التوابع والبيان | التوابع الأربعة | ✅ |
| الأساليب النحوية والأبواب الخاصة | أبواب خاصة (end of ألفية) | ✅ (catch-all, classically conventional) |

No L1 branch is a "grab-bag" of unrelated topics.

### 2. L1 Balance

- L1-9 (39 leaves) is 4.3x the smallest (L1-6, 9 leaves)
- Mean: 20.2, Median: 18.0, StdDev: 9.2, CV: 46%
- L1-9's size follows classical convention; L1-6 reflects naturally narrow scope

### 3. Merge Candidates

L1-6 (الجر والإضافة, 9 leaves, 2 L2s) could merge into L1-5. But the classical tripartite case distinction (مرفوعات / منصوبات / مجرورات) supports keeping it separate. **PREFERENCE, not blocking.**

### 4. Split Candidates

L1-9 (39 leaves, 14 L2s) contains three natural sub-groups:
- Vocative cluster (النداء + related): 13 leaves, 5 L2s
- Special constructions (تعجب, مدح, قسم, تحذير): 10 leaves, 4 L2s
- Special topics (عدد, حكاية, إخبار, أسماء أفعال): 16 leaves, 5 L2s

Splitting would improve balance but follows classical ألفية convention. **PREFERENCE, not blocking.**

### 5. Misplacement — ZERO OBJECTIVE ERRORS

Systematic check against classical categories: every L2 topic is under an L1 branch where classical grammar books place it.

The only flagged item was ما لا ينصرف (under الأسماء in the tree vs standalone after التوابع in النحو الوافي) — but the tree's placement under "nouns" is actually more intuitive for encyclopedic lookup than the classical standalone position. **PREFERENCE.**

Two organizational preferences noted:
- **أدوات الشرط under المضارع:** Classical but encyclopedically less intuitive — a student looking up "conditional sentences" might not think to look under "mudāriʿ inflection."
- **الاشتغال has 4 leaves (14 books) while الفاعل has 2 leaves (43 books):** Granularity ratio inverted relative to importance. Has ألفية precedent but imbalanced.

---

## Check 6: Sibling Distinctness

### Scope
All 19 L2 topics with 4+ sibling leaves examined (93 of 182 total leaves — 51% of tree).

### Results

| Category | Count | L2 Topics |
|----------|-------|-----------|
| Clearly DISTINCT | 17/19 | Each sibling pair covers non-overlapping content |
| POTENTIAL MERGE | 1/19 | الإعراب والبناء |
| BORDERLINE | 1/19 | الاشتغال |

### Detailed analysis of all 19 L2 topics

1. **الكلام والكلمة وأقسامها (5 leaves)** — DISTINCT. Each covers a different foundational concept (4 term definitions, tripartite division, noun signs, verb signs, particle definition).

2. **الإعراب والبناء (6 leaves)** — ONE POTENTIAL MERGE PAIR.
   - "البناء وأسباب بناء الأسماء" ↔ "المعرب والمبني من الأسماء" overlap partially. First explains WHY (causes of بناء). Second classifies WHICH (lists of المبنيات). A student reading both encounters the same nouns from slightly different angles. King Khalid University combines them into one lecture. Classical precedent supports separation (some commentators split them).

3. **علامات الإعراب والنيابة فيها (7 leaves)** — DISTINCT. Each covers a different morphological category with unique markers (الأسماء الستة, المثنى, جمع المذكر, جمع المؤنث, الأفعال الخمسة, الجزم).

4. **الضمائر (5 leaves)** — DISTINCT. Each covers a different pronoun type (منفصل, متصل, مستتر, شأن/قصة, نون الوقاية).

5. **المبتدأ والخبر (6 leaves)** — DISTINCT. Each covers a different rule (خبر types, نكرة justification, وصفي مبتدأ, fronting, deletion, multiplicity).

6. **كان وأخواتها (4 leaves)** — DISTINCT. Introduction, word order, pleonastic use, deletion.

7. **الحروف المشبهة بليس (4 leaves)** — DISTINCT. One leaf per particle: ما, لا, لات, إن. No overlap possible.

8. **أفعال المقاربة والرجاء والشروع (4 leaves)** — DISTINCT. Three semantic types + one shared rule (predicate). Clean partition.

9. **ظن وأخواتها (5 leaves)** — DISTINCT. Each covers a different sub-category or rule (قلوب, تصيير, إلغاء/تعليق, قول→ظن, أعلم/أرى).

10. **الاشتغال (4 leaves)** — BORDERLINE. 4 sub-cases of one phenomenon (obligatory/preferred/equal nasb and raf'). Granular but each sub-case has distinct trigger conditions. No content overlap — just unusual subdivision depth.

11. **إعراب الفعل المضارع وأحكامه (5 leaves)** — DISTINCT. Each covers a different inflectional state (raf', nasb, jazm-single, jazm-conditional, emphasis nuns).

12. **الاستثناء (5 leaves)** — DISTINCT. Each covers a different exception tool (إلا, مفرغ, غير/سوى, خلا/عدا/حاشا, ليس/لا يكون).

13. **الحال (4 leaves)** — DISTINCT. Each covers a different dimension: form (مشتق/جامد), structure (جملة/شبه), function (مؤسسة/مؤكدة), connector (واو).

14. **حروف الجر (7 leaves)** — DISTINCT. General topics (meanings, extra, deletion, substitution) + 3 individual particles (مذ/منذ, رُبّ, حتى). No pair overlaps.

15. **النعت (4 leaves)** — DISTINCT. Each covers a different type or phenomenon (حقيقي, سببي, جملة, قطع).

16. **البدل (4 leaves)** — DISTINCT. The four classical types (كل, بعض, اشتمال, مباين). Mutually exclusive by definition.

17. **النداء (5 leaves)** — DISTINCT. Each covers a different aspect (particles, types/rules, dependents, ياء المتكلم, fixed-vocative names).

18. **العدد (5 leaves)** — DISTINCT. Each covers a different number range/type (مفرد 1-10, مركب 11-19, معطوف 21-99, تمييز, ترتيب).

19. **كنايات العدد (4 leaves)** — DISTINCT. One leaf per particle (كم استفهامية, كم خبرية, كأين, كذا). No overlap possible.

### Finding

**F-6 (LOW): One potential merge pair in الإعراب والبناء.** "البناء وأسباب بناء الأسماء" and "المعرب والمبني من الأسماء" overlap partially. Not blocking — classical precedent supports separation.

---

## Check 7: Granularity Uniformity

### 1. Leaves per L1 branch

| Metric | Value |
|--------|-------|
| Mean | 20.2 |
| Median | 18.0 |
| StdDev | 9.2 |
| CV | 46% |
| Min | 9 (الجر والإضافة) |
| Max | 39 (الأساليب) |
| Max/Min ratio | 4.3x |

### 2. Leaves per L2 topic

| Size | Count | % of L2s |
|------|-------|----------|
| 1 leaf (single-child) | 2 | 3.6% |
| 2 leaves | 18 | 32.1% |
| 3 leaves | 17 | 30.4% |
| 4 leaves | 8 | 14.3% |
| 5 leaves | 7 | 12.5% |
| 6 leaves | 2 | 3.6% |
| 7 leaves | 2 | 3.6% |

Median: 3.0 leaves. Max: 7. Well-concentrated around 2-3 leaves.

### 3. L2 topics with 8+ leaves (split candidates)

**NONE.** Maximum L2 size is 7 leaves. No L2 needs an L3 sub-level.

### 4. L1 branches with 1-2 L2 topics

L1-6 (الجر والإضافة) has 2 L2 topics, 9 leaves. Already discussed in Check 5 — coherent as the "genitive" branch. Not blocking.

### 5. Single-child nodes

2 (already reported as F-2 in Check 1): المعرّف بأل and الاختصاص.

### 6. Granularity vs importance

**F-7 (LOW): Granularity does not correlate well with scholarly importance.**

| Topic | Books | Leaves | Books/Leaf | Assessment |
|-------|-------|--------|------------|------------|
| الاشتغال | 14 | 4 | 3.5 | OVER — 4 sub-cases of one phenomenon |
| حروف الجر | 32 | 7 | 4.6 | HIGH — includes 3 individual particles |
| المبتدأ والخبر | 27 | 6 | 4.5 | OK — many distinct sub-rules |
| الاستثناء | 36 | 5 | 7.2 | OK — 5 different exception tools |
| البدل | 50 | 4 | 12.5 | OK — 4 classical types |
| الحال | 55 | 4 | 13.8 | UNDER — highest-frequency topic |
| الإضافة | 30 | 2 | 15.0 | UNDER — major topic |
| الفاعل | 43 | 2 | 21.5 | UNDER — most fundamental verbal component |
| التوكيد | 45 | 2 | 22.5 | OK — naturally splits into لفظي/معنوي |
| المفعول معه | 48 | 2 | 24.0 | UNDER — major topic |

The books-per-leaf ratio ranges 7x (3.5 to 24.0). This partly reflects inherent topic structure (البدل has 4 classical types regardless of frequency) rather than bias. Not blocking.

---

## Check 8: Adversarial Synthesis

### Q1: Single biggest problem?

**The _nizaman disambiguation pattern (F-1).** 3 leaves with identical Arabic titles to their parents. The `_nizaman` suffix is meaningless fabricated text. This signals the synthesis process didn't test the tree from the **owner's navigation perspective**. Fix is trivial but the pattern is a design smell.

### Q2: One structural change?

**Add الشرط (conditional sentences) as its own L2 topic under L1-9, with 2-3 leaves: أدوات الشرط الجازمة (move existing), لو ولولا ولوما, أمّا التفصيلية.** This fixes F-5, follows the leaf inventory plan, addresses the placement concern about الشرط buried under المضارع, and gives 9 books a proper placement target.

### Q3: Most dangerous false assumption?

**The tree assumes every nahw topic has exactly one correct home.** Five topics sit at genuine L1 boundary crossings:
- أدوات الشرط (المضارع ↔ أساليب)
- نونا التوكيد (المضارع ↔ أساليب)
- المبتدأ الوصفي (المبتدأ ↔ المشتقات)
- صيغ المبالغة (المشتقات ↔ ظن وأخواتها)
- ما لا ينصرف (الأسماء ↔ مبادئ)

The tree has no mechanism for cross-references or secondary placement. An inherent limitation of hierarchical classification, not a tree error — but the placement engine must handle this.

### Q4: Systematic bias?

**No significant bias detected.** The tree's 56 L2 topics map to the union of النحو الوافي (38 chapters) + ألفية ابن مالك (14 additional topics) — the canonical Basran nahw tradition. All 10 "non-matching" L2 titles are naming variants (المفعول له = المفعول لأجله, etc.). No non-canonical topics detected.

Mild tilt toward ألفية-style granularity (الاشتغال sub-cases) over النحو الوافي-style breadth (الفاعل under-subdivided). Not distortive.

---

## Final Verdict

### **NOT READY — 3 required fixes before commit**

**Confidence: HIGH**

### Blocking Findings (3 — all MEDIUM, all mechanical fixes)

**F-1: Rename the 3 _nizaman leaves.** They share their parent's exact Arabic title. Proposed: add "— مدخل عام" or restructure content into siblings. Effort: 5 min.

**F-3: Add policy/language/id_policy fields from v1.0.** Copy `language`, `policy`, and `id_policy` from `library/sciences/nahw/tree.yaml`. Effort: 2 min.

**F-5: Add لو/لولا/لوما/أمّا as leaf(s).** Minimum: 1 new leaf under L1-9. Better: new L2 "أدوات الشرط غير الجازمة" with 2-3 leaves. Effort: 10-15 min.

### Non-Blocking (4 findings + 2 preferences)

- **F-2 (LOW):** 2 single-child nodes (structural preference)
- **F-4 (LOW):** Plan-to-implementation drift (corpus justified)
- **F-6 (LOW):** 1 partial overlap pair (classical precedent for separation)
- **F-7 (LOW):** Granularity imbalance (inherent to topic structure)
- **PREFERENCE:** L1-9 disproportionately large (classical convention)
- **PREFERENCE:** الاشتغال over-granular vs الفاعل (ألفية precedent)

---

## Methodology Notes

- **Tool usage:** Every factual claim backed by tool calls (Python YAML parsing, corpus JSON analysis, web search, engine loading, regex matching). No assessment made from memory alone.
- **Selection bias mitigation:** Leaf sampling used evenly-spaced indices (not cherry-picked). Corpus cross-reference used normalized string matching to avoid false negatives from Arabic spelling variants.
- **Adversarial posture:** Active search for fabricated topics, sarf leaks, organizational errors, and coverage gaps. Three checks (2, 4, 5) returned zero findings — these clean results were earned, not assumed.
- **Evidence files consulted:**
  - `codex_nahw_topic_frequency.json` — 302-book corpus, 70,001 headings, 37,882 topic clusters
  - `codex_nahw_corpus_gaps.md` — 399 uncaptured topics at ≥5 books
  - `codex_nahw_content_analysis.md` — sub-topic analysis of 3 largest books
  - `nahw_v2_leaf_inventory.md` — 145-leaf plan with per-leaf reasoning
  - `library/sciences/nahw/tree.yaml` — active v1.0 tree for format comparison
  - `library/sciences/taxonomy_registry.yaml` — engine registry for compatibility check
