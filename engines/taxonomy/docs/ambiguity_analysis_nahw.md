# Taxonomy Placement Ambiguity Analysis — Nahw Tree

**Purpose:** Identify leaf pairs/groups that are semantically close enough to confuse an LLM during placement. This directly informs Stage 1/Stage 2 prompt design and adversarial test design.

**Generated:** Session prep for taxonomy build, 2026-03-30
**Tree:** nahw_v1_0 (226 leaves, 12 branches)

---

## Critical Finding: Cross-Branch Ambiguity Pairs

These are cases where the SAME Arabic particle or concept has dedicated leaves in DIFFERENT branches. An excerpt mentioning the keyword could legitimately be placed in either branch, depending on which grammatical function the excerpt discusses. **Keyword matching is dangerous — the prompt MUST instruct the LLM to analyze grammatical function, not keyword overlap.**

### 1. كي — Preposition vs Nasb Particle (ADVERSARIAL — in gold baseline)

| Leaf | Branch | When to use |
|------|--------|-------------|
| `almajrurat/huruf_aljar/ma3ani_huruf_aljar` | المجرورات | Excerpt discusses كي as a preposition (حرف جر) |
| `alaf3al/nawasiib_almudari3/kay` | الأفعال | Excerpt discusses كي as a nasb particle (ناصب للمضارع) |

**Disambiguation signal:** The excerpt's `div_path` and `description_arabic` usually indicate which function is being discussed. "كي حرف جر" → preposition. "كي الناصبة" → nasb particle.

### 2. حتى — Nasb Particle vs Conjunction

| Leaf | Branch | When to use |
|------|--------|-------------|
| `alaf3al/nawasiib_almudari3/hatta` | الأفعال | حتى as nasb particle for المضارع |
| `attawabi3/al3atf/huruf_al3atf__tafsil` | التوابع | حتى as a conjunction (عطف) |

### 3. واو — Four Different Grammatical Functions

| Leaf | Branch | When to use |
|------|--------|-------------|
| `almajrurat/huruf_aljar/ma3ani_huruf_aljar` | المجرورات | واو القسم (oath) |
| `alaf3al/nawasiib_almudari3/waw_ma3iyya` | الأفعال | واو المعية as nasb trigger |
| `almansubat/almaf3ulat/maf3ul_ma3ahu/waw_alma3iyya__nahw` | المنصوبات | واو المعية (distinguishing from عطف) |
| `almansubat/alhal/waw_alhal` | المنصوبات | واو الحال |
| `attawabi3/al3atf/huruf_al3atf__tafsil` | التوابع | واو العطف |
| `asaleeb_wamushaqaqat/alqasam` | أساليب | واو القسم (oath mechanism) |

**Six different grammatical functions of واو, each in a different branch.** This is the hardest disambiguation challenge in the nahw tree.

### 4. لام — Preposition vs Nasb vs Jazm

| Leaf | Branch | When to use |
|------|--------|-------------|
| `almajrurat/huruf_aljar/ma3ani_huruf_aljar` | المجرورات | لام as preposition (for possession, etc.) |
| `alaf3al/nawasiib_almudari3/li_anna` | الأفعال | لام التعليل / لام كي (nasb particle) |
| `alaf3al/jawazim_almudari3/lam_alamr` | الأفعال | لام الأمر (jazm particle) |

### 5. ⚠️ ظن — SAME TOPIC IN TWO BRANCHES (Tree Design Issue)

| Leaf | Branch | Content |
|------|--------|---------|
| `almansubat/almaf3ulat/af3al_tata3adda/maf3ulayn_asluhuma_mubtada_khabar` | المنصوبات | ظن verbs — from المنصوبات perspective |
| `annawasiikh/dhanna_wa2akhawatuha/maf3ulayn_dhanna` | النواسخ | ظن verbs — from النواسخ perspective |

**This is a genuine tree structural overlap**, not just a naming ambiguity. Both leaves describe the same grammatical topic (ظن and its sisters taking two objects whose origin is مبتدأ/خبر). The titles are almost identical. An excerpt about ظن's two objects could legitimately go to either.

**Recommendation for prompt design:** Provide a disambiguation rule — e.g., if the excerpt discusses ظن in the context of how it changes the nominative case of the subject to accusative (ناسخ behavior), route to النواسخ. If it discusses ظن in the context of transitive verbs and their objects (تعدي), route to المنصوبات.

**Recommendation for tree (Stage 2):** Consider merging these into one leaf, or making one a redirect to the other.

---

## Within-Branch Granularity Challenges

Branches with the most leaves (hardest Stage 2 scoring):

| Branch | Leaves | Challenge |
|--------|--------|-----------|
| المنصوبات (`almansubat`) | 50 | 5 types of مفعول, each with sub-leaves |
| المقدمات (`muqaddimat`) | 34 | Broad introductory topics |
| الأفعال (`alaf3al`) | 30 | Many nasb/jazm particles with sub-leaves |
| الأسماء (`alasmaa`) | 27 | Various noun categories |

For Stage 2 with > 20 candidates, the prompt should provide clear scoring anchors (1.0 = perfect match, 0.8 = correct topic area, 0.5 = tangentially related) to prevent score compression.

---

## Prompt Design Implications

1. **Never rely on keyword matching.** The prompt must explicitly instruct: "Analyze which GRAMMATICAL FUNCTION the excerpt discusses, not which keywords it shares with leaf titles."

2. **Use description_arabic as primary signal.** The `description_arabic` field explains what the excerpt is about in a sentence — this is the richest disambiguation signal for cross-branch ambiguities.

3. **Use div_path for context.** If the book section is "حروف الجر", the excerpt is more likely about prepositions than about nasb/jazm particles.

4. **Provide disambiguation rules for known pairs.** For كي, واو, لام, حتى, ظن — the prompt should include specific instructions about how to distinguish which function is being discussed.

5. **Score anchoring for large branches.** With 50+ candidates, the LLM needs concrete score descriptions, not just "rate 0-1."
