# KR Owner Decision Map — Exhaustive Inventory

**Purpose:** Every point across all 5 engines where the owner's input is irreplaceable.
**Deadline:** July 1, 2026. All owner-dependent data must exist before autonomous period.
**Date produced:** 2026-04-06

**Classification key:**
- **PERMANENTLY OWNER-DEPENDENT** — No amount of training data or automation resolves this. The owner's personal scholarly preference, priority, or threshold is the answer.
- **AUTOMATABLE WITH TRAINING DATA** — Sufficient labeled examples from the owner enable automation. The owner provides seed data; the system learns.
- **TEDIOUS** — Boring, mechanical, can be collected in structured sessions now.
- **SUMMER** — Requires seeing real pipeline output, scholarly judgment, or emerges during study. Defer to summer.

---

## ENGINE 1: SOURCE (محرك المصادر)

### A. DECISION MAP

#### SRC-D-001: Recognized Muhaqiq List
- **Engine:** Source | **Spec:** §4.A.8
- **Description:** The list of tahqiq editors considered trustworthy (شعيب الأرناؤوط, أحمد شاكر, etc.). Determines trust_tier for every source. Initial list is hardcoded but extensible.
- **Status:** PARTIAL — initial list in SPEC, but owner has not reviewed or extended it.
- **Data needed:** Owner reviews the initial list, adds/removes editors. Binary per-editor: trusted or not.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT. Which editors the owner trusts is a personal scholarly judgment. Different students trust different editors.
- **Capture method:** BINARY_CHOICE per editor name. Present the initial list + common editors not on it. Owner marks yes/no.
- **Classification:** TEDIOUS — can collect now. ~30 min session.

#### SRC-D-002: Publisher Reputation List
- **Engine:** Source | **Spec:** §4.A.8
- **Description:** Which publishers are considered scholarly vs commercial. Affects trust_tier weight (0.15).
- **Status:** UNRESOLVED — SPEC mentions دار الرسالة, مؤسسة الرسالة, دار الكتب العلمية as examples but no formal list exists.
- **Data needed:** Owner classifies ~20-30 major Arabic publishers as: scholarly, neutral, commercial.
- **Automatable?** AUTOMATABLE WITH TRAINING DATA. After 20 labeled publishers, an LLM can classify new ones. But the owner's INITIAL labels are irreplaceable.
- **Training data:** ~30 labeled publishers with scholarly/neutral/commercial classification.
- **Capture method:** RANKING (3 tiers) for a presented list of publishers.
- **Classification:** TEDIOUS — can collect now. ~20 min session.

#### SRC-D-003: Muhaqiq Watchlist (Commercial Editors)
- **Engine:** Source | **Spec:** §4.B.10
- **Description:** Editors known for commercial, non-scholarly editions. Used by tahqiq apparatus fingerprinting.
- **Status:** UNRESOLVED — SPEC says "informed by domain knowledge" but no list exists.
- **Data needed:** Owner identifies known commercial editors (or confirms architect's research).
- **Automatable?** AUTOMATABLE WITH TRAINING DATA — but initial seed from owner/domain research.
- **Capture method:** DEEP_QUESTION — "Which editors have you been warned about by teachers or scholars?"
- **Classification:** TEDIOUS — can collect now alongside SRC-D-001.

#### SRC-D-004: Science Scope Definition
- **Engine:** Source | **Spec:** §4.A.4, §4.A.6, §4.B.4
- **Description:** Which Islamic sciences are in scope for the library. Drives relevance evaluation, gap analysis, and autonomous discovery. Currently: fiqh, nahw, usul_al_fiqh, aqidah, sarf, balagha, imlaa + additional sciences from hardening (19 total in hardening protocol).
- **Status:** PARTIAL — hardening protocol lists 18 sciences, but owner has not formally prioritized or bounded.
- **Data needed:** Owner ranks all candidate sciences by study priority and confirms the boundary of "in scope."
- **Automatable?** PERMANENTLY OWNER-DEPENDENT. Which sciences to study is a personal curriculum choice.
- **Capture method:** RANKING of ~20 sciences.
- **Classification:** TEDIOUS — can collect now. ~15 min session.

#### SRC-D-005: Study Focus / Current Curriculum Position
- **Engine:** Source | **Spec:** §4.A.6, §4.B.4, §4.B.9
- **Description:** The owner's current study focus (e.g., "Hanbali fiqh, intermediate level"). Drives relevance evaluation priority, gap analysis recommendations, and processing order.
- **Status:** UNRESOLVED — referenced throughout source SPEC but never formally captured.
- **Data needed:** Owner states current study focus: science, school preference (if any), level.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT. Changes over time as the owner progresses.
- **Capture method:** DEEP_QUESTION — "What are you studying right now? What do you want to study next? What level are you at?"
- **Classification:** TEDIOUS — can collect now. ~10 min. BUT must be refreshable (summer update).

#### SRC-D-006: School Preference for Multi-Source Works
- **Engine:** Source | **Spec:** §4.A.1 (preferred_source_id)
- **Description:** When multiple editions of the same work exist, which is the preferred source? Drives excerpt extraction priority.
- **Status:** UNRESOLVED — default is "first acquired" but owner may prefer a specific tahqiq.
- **Data needed:** Per-work preference when duplicates exist. Most cases won't arise until library grows.
- **Automatable?** AUTOMATABLE WITH TRAINING DATA — after 5-10 edition preferences, the system can predict based on muhaqiq reputation and tahqiq fingerprint.
- **Training data:** 5-10 explicit edition preference decisions with reasoning.
- **Capture method:** BINARY_CHOICE when second edition is acquired.
- **Classification:** SUMMER — only arises when library has multiple editions.

#### SRC-D-007: Trust Tier Override Authority
- **Engine:** Source | **Spec:** §4.A.8 (owner_override)
- **Description:** Owner can override the algorithmic trust evaluation. When should this happen?
- **Status:** RESOLVED by design — human gate triggers for flagged sources. Owner approves/rejects.
- **Data needed:** No pre-collection needed. This is an operational gate during pipeline runs.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — trust override is a scholarly judgment.
- **Capture method:** Per-source decision during pipeline operation.
- **Classification:** SUMMER — operational, during pipeline runs.

#### SRC-D-008: Relevance Evaluation for Partially-Relevant Sources
- **Engine:** Source | **Spec:** §4.A.6
- **Description:** When autonomous discovery finds a source that's "partially relevant" (e.g., a history book with fiqh content), should it be included?
- **Status:** UNRESOLVED — SPEC says "CC decides scope based on owner context" but no explicit preference captured.
- **Data needed:** Owner's general policy: inclusive (include anything touching my sciences) vs exclusive (only primary works).
- **Automatable?** PERMANENTLY OWNER-DEPENDENT.
- **Capture method:** THRESHOLD_SETTING — "On a scale of 1-5, how broadly should the library cast its net?"
- **Classification:** TEDIOUS — can collect now. Single question.

#### SRC-D-009: Confidence Thresholds
- **Engine:** Source | **Spec:** §8 Configuration
- **Description:** Three thresholds: auto_accept (0.70), block (0.50), trust_verified (0.65). These determine how aggressive the system is about accepting LLM inferences vs requiring human review.
- **Status:** RESOLVED — defaults in SPEC. Owner can override but defaults are defensible.
- **Data needed:** Owner could adjust, but defaults are architecturally sound.
- **Automatable?** N/A — engineering defaults.
- **Classification:** N/A — no owner action needed unless dissatisfied.

#### SRC-D-010: Seed Collection Composition
- **Engine:** Source | **Spec:** §4.B.4 (gap analysis depends on what's already in library)
- **Description:** The initial 2,519 Shamela books that form the seed collection. Which of these should be processed first? Are there critical missing works?
- **Status:** PARTIAL — books exist as .htm exports, but no prioritized processing order.
- **Data needed:** Owner reviews the Shamela export list and identifies: (1) must-process-first books, (2) books to skip entirely, (3) missing books to acquire.
- **Automatable?** PARTIALLY — the difficulty prediction algorithm (§4.B.9) can rank by processing difficulty, but the STUDY PRIORITY is owner-dependent.
- **Training data:** Owner marks 20-30 books with priority (must/should/nice-to-have/skip).
- **Capture method:** RANKING of a presented book list.
- **Classification:** TEDIOUS — can collect now. ~1 hour session reviewing book titles.

---

## ENGINE 2: NORMALIZATION (محرك التطبيع)

### A. DECISION MAP

#### NORM-D-001: Layer Detection Confidence Threshold
- **Engine:** Normalization | **Spec:** §4.A.5, §5 Layer 3
- **Description:** When the normalizer cannot confidently distinguish matn from sharh text, what threshold triggers human review? Currently: >30% of pages below "medium" confidence.
- **Status:** RESOLVED — defaults in SPEC.
- **Data needed:** None pre-collection. Operational threshold.
- **Automatable?** N/A — engineering parameter.
- **Classification:** N/A.

#### NORM-D-002: Structure Format Override
- **Engine:** Normalization | **Spec:** §4.B.2, §5 Layer 3
- **Description:** When the normalizer detects a different structural format than the source engine classified (e.g., source says "prose" but normalizer detects "Q&A"), a human gate triggers.
- **Status:** RESOLVED by design — human gate triggers, owner decides.
- **Data needed:** Per-source decision during pipeline operation.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT for ambiguous cases.
- **Capture method:** BINARY_CHOICE at human gate.
- **Classification:** SUMMER — operational.

#### NORM-D-003: Page Order Conflict Resolution (Images)
- **Engine:** Normalization | **Spec:** §4.A.4
- **Description:** When OCR-detected page numbers disagree with filename order for image scans, owner must choose the correct order.
- **Status:** RESOLVED by design — human gate triggers.
- **Data needed:** Per-source decision during pipeline operation.
- **Automatable?** N/A — trivial human gate.
- **Classification:** SUMMER — only arises with image-based sources.

#### NORM-D-004: Layer Fingerprint Inversion Review
- **Engine:** Normalization | **Spec:** §4.B.9
- **Description:** When stylometric fingerprints suggest matn and sharh labels may be inverted, human gate triggers. Owner decides whether to swap labels.
- **Status:** RESOLVED by design — human gate triggers.
- **Data needed:** Per-source decision during pipeline operation.
- **Automatable?** N/A — requires reading the source.
- **Classification:** SUMMER — operational.

#### NORM-D-005: OCR Engine Selection for Diacritically-Heavy Texts
- **Engine:** Normalization | **Spec:** §4.A.4
- **Description:** Whether to use dual-OCR (Mistral + Qari-OCR) for critical texts. Currently applies to low-fidelity and critical scholarly texts.
- **Status:** RESOLVED — default policy in SPEC.
- **Data needed:** None.
- **Automatable?** N/A.
- **Classification:** N/A.

---

## ENGINE 3: EXCERPTING (محرك الاقتباس)

### A. DECISION MAP

#### EXC-D-001: What Constitutes a "Complete Scholarly Thought"
- **Engine:** Excerpting | **Spec:** §1.1, §3, §5.3
- **Description:** The fundamental unit of the excerpting engine — a teaching unit must teach "one complete scholarly thought." But the granularity of this is a judgment call: is a definition + its conditions one thought or two?
- **Status:** PARTIAL — FP-1 through FP-22 define extensive rules, but the 30-book owner review probe has not yet happened.
- **Data needed:** Owner reviews 30 real excerpts from diverse books and judges: "Does this teach one complete thought? Is it too big? Too small?"
- **Automatable?** AUTOMATABLE WITH TRAINING DATA — this is the core automation target. With ~100 owner-judged examples, the system calibrates its prompts and thresholds.
- **Training data:** 100+ excerpts labeled by owner as: good / too-granular / too-coarse / missing-context / wrong-boundary.
- **Capture method:** Reading sessions where owner evaluates real excerpts.
- **Classification:** SUMMER — requires real pipeline output to evaluate.

#### EXC-D-002: Self-Containment Threshold Calibration
- **Engine:** Excerpting | **Spec:** §3.3, §3.5
- **Description:** FULL/PARTIAL/DEPENDENT classification. FP-18 identifies that FULL conflates "acceptable" and "study-ready." The 30-book probe should calibrate where the owner draws the line.
- **Status:** UNRESOLVED — FP-18 explicitly defers to calibration via the 30-book probe.
- **Data needed:** Owner judges ~50 excerpts rated FULL by the system and marks which are truly "study-ready" vs merely "acceptable."
- **Automatable?** AUTOMATABLE WITH TRAINING DATA after calibration.
- **Training data:** ~50 FULL-rated excerpts with owner's study-readiness judgment.
- **Capture method:** Reading sessions.
- **Classification:** SUMMER — requires real output.

#### EXC-D-003: Forgiving Retention Policy (FP-3)
- **Engine:** Excerpting | **Spec:** §1.1b FP-3
- **Description:** When a small linked carryover (≤15%, max ~30 words) at the start of an excerpt has a causal conjunction (لأن, فإن, etc.), retain it. The threshold (15%, 30 words) and the exhaustive list of forgiving conjunctions were set by the architect.
- **Status:** RESOLVED — explicit in FP-3 with exhaustive conjunction list.
- **Data needed:** None pre-collection. But the 30-book probe will test if the threshold feels right.
- **Automatable?** N/A — resolved by design.
- **Classification:** N/A (validate during summer probe).

#### EXC-D-004: Title-Retention Policy for Hadith Collections
- **Engine:** Excerpting | **Spec:** §1.1b FP-3 (title-retention asymmetry)
- **Description:** In hadith collections like Bukhari, the chapter title (tarjama) IS the author's fiqhi ruling. Should titles always be retained in hadith collection excerpts?
- **Status:** PARTIAL — FP-3 says "when the title carries jurisprudential content the text does not repeat."
- **Data needed:** Owner confirms: "For hadith books, always include the chapter title in the excerpt."
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — this is a study-style preference.
- **Capture method:** BINARY_CHOICE — "Should Bukhari-style chapter titles always be included?"
- **Classification:** TEDIOUS — can collect now. Single question.

#### EXC-D-005: Owner Review Gate (30-Book Probe)
- **Engine:** Excerpting | **Spec:** Memory (non-negotiable owner review gate)
- **Description:** Owner personally reads real Arabic excerpts from 30 diverse books and evaluates quality. This is the NON-NEGOTIABLE gate before the excerpting engine is declared complete.
- **Status:** UNRESOLVED — not yet started. Pending hardened re-run.
- **Data needed:** Owner reads ~200-300 excerpts across 30 books (10 per book).
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — the whole point is human scholarly judgment on real output.
- **Capture method:** Reading sessions with structured feedback form per excerpt.
- **Classification:** SUMMER — requires hardened pipeline output.

#### EXC-D-006: Handling of DEPENDENT Excerpts (EX-G-002)
- **Engine:** Excerpting | **Spec:** §7.3.4
- **Description:** When an excerpt is classified DEPENDENT after consensus, the human gate asks: keep with context note, merge with adjacent, or exclude?
- **Status:** RESOLVED by design — human gate triggers during pipeline runs.
- **Data needed:** Per-excerpt decision during pipeline operation.
- **Automatable?** AUTOMATABLE WITH TRAINING DATA — after 20-30 DEPENDENT decisions, the system can predict the owner's preference pattern.
- **Training data:** 20-30 DEPENDENT excerpt decisions.
- **Capture method:** Human gate resolution during pipeline runs.
- **Classification:** SUMMER — operational.

#### EXC-D-007: Author Attribution Disambiguation (EX-G-001)
- **Engine:** Excerpting | **Spec:** §7.3.4
- **Description:** When 3 models all disagree on author attribution, human gate asks owner: "Which author wrote this passage?"
- **Status:** RESOLVED by design — human gate triggers.
- **Data needed:** Per-excerpt decision during pipeline operation.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT for truly ambiguous cases.
- **Capture method:** Human gate resolution.
- **Classification:** SUMMER — operational.

#### EXC-D-008: School Attribution Conflict (EX-G-003)
- **Engine:** Excerpting | **Spec:** §7.3.4
- **Description:** When school attribution conflicts with source metadata and both models disagree.
- **Status:** RESOLVED by design — human gate triggers.
- **Data needed:** Per-excerpt decision during pipeline operation.
- **Automatable?** PARTIALLY — most school attributions are deterministic from source metadata.
- **Classification:** SUMMER — operational.

#### EXC-D-009: Error Class Calibration (FP-5/FP-21)
- **Engine:** Excerpting | **Spec:** §1.1b FP-5, FP-21
- **Description:** When should the system HALT (Class A: engine-introduced fabrication) vs FLAG (Class B: source-inherited tashkeel ambiguity) vs QUARANTINE (Class C: source-specific OCR)? The thresholds for halt triggers.
- **Status:** PARTIAL — three-class system defined but "pattern of Class A errors" threshold not quantified.
- **Data needed:** Owner's risk tolerance: "How many flagged excerpts per batch before you want the system to stop and call for attention?"
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — risk tolerance is personal.
- **Capture method:** THRESHOLD_SETTING — flag budget percentage.
- **Classification:** TEDIOUS — can collect now. Single threshold.

#### EXC-D-010: Flag Budget (FP-21 Anti-Flag-Laundering)
- **Engine:** Excerpting | **Spec:** §1.1b FP-21
- **Description:** If the flagged-item rate exceeds a configurable threshold per run (e.g., >15%), the run must halt. What percentage?
- **Status:** UNRESOLVED — "configurable threshold" mentioned but not set.
- **Data needed:** Owner sets the threshold.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT.
- **Capture method:** THRESHOLD_SETTING.
- **Classification:** TEDIOUS — can collect now. Single number.

---

## ENGINE 4: TAXONOMY (محرك التصنيف)

### A. DECISION MAP

#### TAX-D-001: Science Tree Structures (Remaining 4 Trees)
- **Engine:** Taxonomy | **Spec:** §2.3
- **Description:** The taxonomy trees for sarf, balagha, aqidah, and imlaa must be validated and installed. Currently: nahw v2.0 (183 leaves) installed. Sarf 152-leaf draft paused. Balagha architect draft 197 leaves committed. Aqidah Gemini v2 processed. Imlaa pending.
- **Status:** PARTIAL — nahw done, 4 remaining trees in various stages.
- **Data needed:** Owner reviews each tree (or delegates to architect) and approves the leaf structure. The key question: "Is this tree's organization how you would organize this science if you were writing a textbook?"
- **Automatable?** PARTIALLY — the 4-researcher methodology produces candidate trees, but the FINAL approval requires owner's scholarly judgment that the organization makes sense for study.
- **Capture method:** DEEP_QUESTION per tree — owner reviews leaf list and says yes/no/modify.
- **Classification:** TEDIOUS for review — the trees are being built now. Owner review sessions can start as trees complete. ~30 min per tree.

#### TAX-D-002: Placement Confidence Thresholds
- **Engine:** Taxonomy | **Spec:** §7.1
- **Description:** Live threshold (0.80 teaching / 0.85 editorial), staging threshold (0.50), tie threshold (0.10).
- **Status:** RESOLVED — defaults in SPEC.
- **Data needed:** None unless owner wants to adjust.
- **Automatable?** N/A.
- **Classification:** N/A.

#### TAX-D-003: Per-Science Priority for Tree Formation
- **Engine:** Taxonomy | **Spec:** Memory (tree formation order)
- **Description:** Which science trees to build next after nahw. Currently: sarf highest priority (shares Shamela category with nahw).
- **Status:** PARTIAL — sarf priority established but full order not confirmed.
- **Data needed:** Owner confirms tree formation order: sarf → balagha → aqidah → imlaa, or different order.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — study priority.
- **Capture method:** RANKING of the 4 remaining sciences.
- **Classification:** TEDIOUS — can collect now. Single ranking. ~5 min.

#### TAX-D-004: Trees Branch by Topic, Never by School
- **Engine:** Taxonomy | **Spec:** §7.3
- **Description:** Hardcoded constraint. Trees organize by topic, not by school affiliation.
- **Status:** RESOLVED — hardcoded architectural constraint. Owner confirmed through STEERING.md.
- **Data needed:** None.
- **Automatable?** N/A.
- **Classification:** N/A.

#### TAX-D-005: Staged Excerpt Review
- **Engine:** Taxonomy | **Spec:** §3.2
- **Description:** Excerpts placed with 0.50-0.79 confidence go to staging. Owner (or automated reviewer) reviews to promote or reclassify.
- **Status:** RESOLVED by design — part of pipeline operation.
- **Data needed:** Per-excerpt decision during operation.
- **Automatable?** AUTOMATABLE WITH TRAINING DATA — after 50+ staging decisions.
- **Training data:** 50+ staged excerpt promotion/reclassification decisions.
- **Classification:** SUMMER — operational.

#### TAX-D-006: Science Scope per Book
- **Engine:** Taxonomy | **Spec:** §2.2 (science_id comes from run configuration)
- **Description:** Each taxonomy run processes one science at a time. Multi-science books (e.g., usul al-fiqh touching both fiqh and logic) need explicit science assignment per batch.
- **Status:** PARTIAL — extension hook noted for per-excerpt science classification.
- **Data needed:** For multi-science books, owner must indicate which science tree to place excerpts against.
- **Automatable?** AUTOMATABLE WITH TRAINING DATA — LLM can classify most cases.
- **Capture method:** Per-book assignment during pipeline runs.
- **Classification:** SUMMER — operational.

#### TAX-D-007: Additional Science Trees Beyond Initial 5
- **Engine:** Taxonomy | **Spec:** hardening protocol lists 18 sciences
- **Description:** The hardening protocol expanded to 18 sciences (adding kalam, fara'id, tasawwuf, qira'at/tajwid, takhrij/rijal, adab/shi'r, etc.). When to build these trees?
- **Status:** UNRESOLVED — trees for these sciences don't exist yet.
- **Data needed:** Owner confirms which additional sciences to build trees for, and in what order.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — curriculum decision.
- **Capture method:** RANKING + BINARY_CHOICE (include/exclude each science).
- **Classification:** TEDIOUS — can collect now alongside SRC-D-004.

---

## ENGINE 5: SYNTHESIS (محرك التوليف)

### A. DECISION MAP

#### SYN-D-001: Entry Format Preferences (SCIENCE.md)
- **Engine:** Synthesis | **Spec:** §2.2 (SCIENCE.md configuration)
- **Description:** Per-science synthesis configuration: whether schools exist and which ones, entry format preferences, scholarly conventions, science-specific synthesis rules.
- **Status:** UNRESOLVED — SCIENCE.md files don't exist yet for any science.
- **Data needed:** Owner defines per-science: (1) does this science have school divisions? (2) which schools? (3) preferred entry organization (chronological, by school, by evidence type?).
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — study-style preference.
- **Capture method:** DEEP_QUESTION per science.
- **Classification:** SUMMER — synthesis engine not yet built.

#### SYN-D-002: School List per Science
- **Engine:** Synthesis | **Spec:** §2.2
- **Description:** Which schools exist in each science? Nahw: بصري/كوفي/بغدادي/أندلسي. Fiqh: حنفي/مالكي/شافعي/حنبلي/ظاهري. Aqidah: different taxonomy.
- **Status:** UNRESOLVED — not formally captured per-science.
- **Data needed:** Owner confirms school lists per science.
- **Automatable?** PARTIALLY — standard school lists are well-known, but some sciences have non-obvious school structures.
- **Capture method:** DEEP_QUESTION per science.
- **Classification:** TEDIOUS — can collect now for the 5 current sciences. ~20 min.

#### SYN-D-003: Factual vs Analytical Layer Boundary
- **Engine:** Synthesis | **Spec:** §3.2 (implied)
- **Description:** Entries have two layers: factual (traceable to excerpts) and analytical (engine's scholarly contribution). How much analytical commentary does the owner want?
- **Status:** UNRESOLVED — no preference captured.
- **Data needed:** Owner's preference: minimal analysis (just present what scholars said), moderate (connections and context), or maximal (full scholarly narrative with synthesis).
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — study-style preference.
- **Capture method:** DEEP_QUESTION + example entries at different levels.
- **Classification:** SUMMER — needs synthesis engine output to evaluate.

#### SYN-D-004: Owner Corrections as Permanent Constraints
- **Engine:** Synthesis | **Spec:** §2.3
- **Description:** When owner identifies an error in an entry, the correction can be marked "permanent" — surviving all future regenerations. Owner decides which corrections are permanent.
- **Status:** RESOLVED by design — operational during study.
- **Data needed:** Per-correction decision during study.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT.
- **Classification:** SUMMER — operational.

#### SYN-D-005: Entry Language and Tone
- **Engine:** Synthesis | **Spec:** §1 (implied)
- **Description:** Should entries read like a textbook? Like an encyclopedia? Like study notes? What level of Arabic formality?
- **Status:** UNRESOLVED — ENTRY_EXAMPLE.md shows the target but owner hasn't confirmed it's what he wants.
- **Data needed:** Owner reads ENTRY_EXAMPLE.md and confirms or adjusts the style.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT — reading preference.
- **Capture method:** DEEP_QUESTION after reading example entry.
- **Classification:** TEDIOUS — can collect now by having owner read ENTRY_EXAMPLE.md. ~15 min.

#### SYN-D-006: Cross-Science Reference Policy
- **Engine:** Synthesis | **Spec:** §1 (Scenario 3)
- **Description:** When a nahw concept has implications for usul al-fiqh (e.g., the linguistic analysis of الأمر affects legal theory of commands), should entries cross-reference?
- **Status:** UNRESOLVED — deferred capability.
- **Data needed:** Owner's preference on cross-science linking depth.
- **Automatable?** PERMANENTLY OWNER-DEPENDENT.
- **Capture method:** DEEP_QUESTION.
- **Classification:** SUMMER — synthesis not built yet.

---

## B. AUTOMATABLE vs NOT — Summary Matrix

| Decision ID | Engine | Permanently Owner-Dependent? | Automatable After Training? | Training Data Needed |
|---|---|---|---|---|
| SRC-D-001 | Source | YES | No | N/A (binary choice) |
| SRC-D-002 | Source | Initial only | YES after ~30 labels | ~30 publisher labels |
| SRC-D-003 | Source | Initial only | YES after seed | ~10 editor flags |
| SRC-D-004 | Source | YES | No | N/A (ranking) |
| SRC-D-005 | Source | YES (evolves) | No | N/A (interview) |
| SRC-D-006 | Source | Per-work | YES after 5-10 | 5-10 edition preferences |
| SRC-D-008 | Source | YES | No | N/A (threshold) |
| SRC-D-010 | Source | Per-book | PARTIAL (50% auto) | 20-30 book priority labels |
| EXC-D-001 | Excerpting | No | YES after ~100 labels | 100+ excerpt judgments |
| EXC-D-002 | Excerpting | No | YES after ~50 labels | 50+ study-readiness judgments |
| EXC-D-005 | Excerpting | YES | No | 200-300 excerpt reviews |
| EXC-D-006 | Excerpting | No | YES after 20-30 | 20-30 DEPENDENT decisions |
| EXC-D-009 | Excerpting | YES | No | N/A (threshold) |
| EXC-D-010 | Excerpting | YES | No | N/A (threshold) |
| TAX-D-001 | Taxonomy | YES (final approval) | PARTIAL (formation automated) | Per-tree review |
| TAX-D-003 | Taxonomy | YES | No | N/A (ranking) |
| TAX-D-007 | Taxonomy | YES | No | N/A (ranking) |
| SYN-D-001 | Synthesis | YES | No | Per-science interview |
| SYN-D-002 | Synthesis | PARTIAL | YES (standard lists) | Per-science confirmation |
| SYN-D-003 | Synthesis | YES | No | Example entry review |
| SYN-D-005 | Synthesis | YES | No | Example entry review |

---

## C. TRAINING DATA REQUIREMENTS

For decisions that CAN be automated — what labeled data from the owner makes automation possible:

| Decision | Data Type | Minimum Examples | Format | Time Estimate |
|---|---|---|---|---|
| SRC-D-002 (publishers) | Publisher → tier label | 30 | spreadsheet | 20 min |
| SRC-D-006 (edition pref) | Work + 2 editions → preference | 5-10 | per-gate | ongoing |
| SRC-D-010 (book priority) | Book title → priority tier | 20-30 | spreadsheet | 60 min |
| EXC-D-001 (teaching units) | Excerpt → good/bad/reason | 100 | reading sessions | 5-8 hours |
| EXC-D-002 (study-readiness) | FULL excerpt → acceptable/study-ready | 50 | reading sessions | 3-4 hours |
| EXC-D-006 (DEPENDENT) | DEPENDENT excerpt → keep/merge/exclude | 20-30 | per-gate | ongoing |
| TAX-D-005 (staged review) | Staged excerpt → promote/reclassify | 50 | per-gate | ongoing |

**Total pre-collection time:** ~2 hours of structured sessions (tedious items).
**Total summer time:** ~10-15 hours of reading sessions (real output evaluation).

---

## D. PERMANENT PREFERENCES

Decisions that CANNOT be automated and must exist permanently:

| Pref ID | Description | Capture Method | Refresh Frequency |
|---|---|---|---|
| PP-001 | Trusted muhaqiq list | BINARY_CHOICE per editor | Annually |
| PP-002 | Science scope and priority ranking | RANKING of ~20 sciences | Per semester |
| PP-003 | Current study focus (science, school, level) | DEEP_QUESTION | Monthly |
| PP-004 | Library breadth policy (inclusive vs exclusive) | THRESHOLD_SETTING | Once |
| PP-005 | Error halt threshold (flag budget %) | THRESHOLD_SETTING | Once |
| PP-006 | Tree formation order | RANKING | Per phase |
| PP-007 | Entry style preference (textbook/encyclopedia/notes) | DEEP_QUESTION + example | Once |
| PP-008 | School lists per science | DEEP_QUESTION | Per science (once) |
| PP-009 | Title retention policy for hadith books | BINARY_CHOICE | Once |
| PP-010 | Per-science entry format preferences | DEEP_QUESTION | Per science (once) |
| PP-011 | Cross-science reference depth | DEEP_QUESTION | Once |
| PP-012 | Additional sciences beyond initial 5 | RANKING + BINARY_CHOICE | Per phase |

---

## E. CROSS-ENGINE DEPENDENCIES

Owner decisions in one engine that affect another engine's behavior:

| Upstream Decision | Downstream Impact | Mechanism |
|---|---|---|
| SRC-D-004 (science scope) | TAX-D-001 (which trees to build), TAX-D-007 (additional sciences) | Science scope defines tree inventory |
| SRC-D-005 (study focus) | Source processing order, Taxonomy placement priority | Current focus affects which excerpts are processed first |
| SRC-D-001 (muhaqiq trust) | Excerpting trust_tier → Synthesis verified_flagged_status | Untrusted muhaqiq → flagged source → excerpts enter critical analysis layer in entries |
| SRC-D-010 (book priority) | Normalization processing order → Excerpting batch composition | High-priority books processed first, determining which excerpts exist for taxonomy |
| EXC-D-001 (teaching unit granularity) | TAX placement accuracy, SYN entry quality | Overgranulated excerpts = harder to place, thinner entries. Undergranulated = taxonomic mismatch |
| EXC-D-002 (self-containment calibration) | SYN entry context quality | If FULL is too lenient, entries include context-dependent excerpts that confuse the reader |
| EXC-D-009 (error class thresholds) | All engines — halt cascades | Class A halt stops the entire pipeline for the affected source |
| TAX-D-001 (tree structure) | EXC topic keyword effectiveness, SYN entry organization | Tree leaf granularity must match excerpt granularity (FP-9) |
| TAX-D-003 (tree formation order) | SYN — which sciences have entries first | Can't synthesize without a tree |
| SYN-D-001 (SCIENCE.md) | TAX per-science config, EXC school attribution | School lists affect school consensus verification |
| SYN-D-003 (analytical layer depth) | Owner study experience | Too much analysis = noise; too little = missed connections |

---

## F. TEDIOUS vs SUMMER Classification

### TEDIOUS — Collect Now (Apr-Jun 2026)

| Item | Time | Method |
|---|---|---|
| PP-001: Muhaqiq trust list | 30 min | Present list, owner marks yes/no |
| PP-002: Science scope + priority ranking | 15 min | Rank ~20 sciences |
| PP-003: Current study focus | 10 min | Interview |
| PP-004: Library breadth policy | 5 min | Single threshold question |
| PP-005: Error halt threshold | 5 min | Single number |
| PP-006: Tree formation order | 5 min | Rank 4 sciences |
| PP-008: School lists per science | 20 min | Per-science confirmation |
| PP-009: Hadith title retention | 5 min | Single yes/no |
| PP-012: Additional sciences | 10 min | Review + rank |
| SRC-D-002: Publisher reputation | 20 min | Classify ~30 publishers |
| SRC-D-003: Commercial editor watchlist | 10 min | Free-form recall |
| SRC-D-010: Book processing priority (first batch) | 60 min | Review book titles |
| SYN-D-005: Entry style preference | 15 min | Read ENTRY_EXAMPLE.md + feedback |
| TAX-D-001: Tree reviews (as trees complete) | 30 min each × 4 = 2 hrs | Review leaf lists |

**Total tedious collection:** ~5 hours across multiple sessions.

### SUMMER — Defer to July+ (requires real output)

| Item | Time | Method |
|---|---|---|
| EXC-D-001: Teaching unit quality (30-book probe) | 5-8 hours | Reading sessions |
| EXC-D-002: Self-containment calibration | 3-4 hours | Reading sessions |
| EXC-D-005: Owner review gate | 5-10 hours | 30-book systematic review |
| EXC-D-006/007/008: Human gate decisions | Ongoing | Per-gate during pipeline runs |
| SYN-D-001: SCIENCE.md configuration | 1 hour per science | After seeing synthesis output |
| SYN-D-003: Analytical layer depth | 1 hour | After seeing example entries |
| SYN-D-006: Cross-science reference policy | 30 min | After seeing real cross-references |
| TAX-D-005: Staged excerpt review | Ongoing | During pipeline operation |
| TAX-D-006: Multi-science book assignment | Ongoing | During pipeline operation |

**Total summer collection:** ~20-30 hours across the study period.

---

## CRITICAL PATH

The decisions that BLOCK pipeline progress if not collected:

1. **SRC-D-004 (science scope)** → blocks tree formation → blocks taxonomy → blocks synthesis. **Collect first.**
2. **SRC-D-010 (book priority)** → blocks normalization processing order. **Collect second.**
3. **TAX-D-001 (tree reviews)** → blocks placement → blocks synthesis. **Collect as trees complete.**
4. **PP-001 (muhaqiq list)** → blocks trust_tier → affects all downstream quality signals. **Collect early.**
5. **EXC-D-005 (30-book probe)** → blocks excerpting engine completion. **Requires pipeline output first.**

The first 4 items can be collected in a single 2-hour session. Item 5 requires real pipeline output and is the longest-lead item.
