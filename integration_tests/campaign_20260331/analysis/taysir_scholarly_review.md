# Taysir Deep Scholarly Review — Diagnostic Report

**Book:** تيسير العلام شرح عمدة الأحكام by عبد الله البسام (Hanbali hadith-fiqh sharh)
**Dataset:** 1,283 excerpts from campaign_20260331 (Opus primary, pre-hardening prompts)
**Reviewer:** Claude Chat (Architect), independent of CC's structural analysis
**Methodology:** Stratified sample of 68 excerpts across all function types, self-containment levels, word count ranges, and book sections. Supplemented by systematic corpus-wide pattern analysis.

---

## Executive Assessment

The excerpting engine produces **structurally sound** output with **strong decontextualization defenses** but **inconsistent classification labels** and a **missing narrator role** that affects downstream taxonomy and attribution.

**What works well:**
- Decontextualization rules (DP-1 through DP-6): zero violations across all 6 rules
- Multi-school debates: kept intact with all positions in one excerpt
- Self-containment notes: 100% of PARTIAL excerpts have accurate notes
- Opinion vs rule distinction: accurate (97% precision on debate markers)
- DEPENDENT detection: correct for all 14 cases, properly gated

**What needs fixing before production:**
- المعنى الإجمالي sections classified into 7 different types (should be 1-2)
- Fawa'id granularity: 73% split vs 27% grouped with no predictable rule
- Companion narrators: 100% misclassified as "quoted_opinion" (SPEC has no narrator role)
- Author attribution: 100% "unknown" (upstream normalization layer detection absent)

---

## Reliability Scorecard

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| 5a Deterministic (boundaries) | **PASS** | 0 DP violations, 0 over-merges, 0 duplicates |
| 5b LLM Classification | **CONDITIONAL** | R-1 (7-way chaos), R-2 (granularity), H-2 (narrator) |
| 5c Metadata Integrity | **FAIL** | H-3 (100% unknown author_id), 100% wrong layer |
| Self-containment accuracy | **PASS** | 100% SC notes on PARTIAL, ~11 false FULL (0.9%) |
| Decontextualization defense | **PASS** | 0/6 DP rules violated, 69% refutations include target |

---

## Findings by Category

### SPEC GAPS (must fix SPEC before re-run)

**SG-1: No "narrator" role for hadith transmitters**
- SPEC §6.2 defines 3 roles: quoted_opinion, classification_frame, refuted_position
- 250 companion mentions in isnad chains have no appropriate role
- 100% are force-classified as "quoted_opinion"
- Fix: Add `narrator` role to quoted_scholars schema; update enrichment prompt to detect transmission formulas (عن، حدثنا، أخبرنا) as narrator signals

**SG-2: Hadith sharh grouping rule contradicts optimal study design**
- SPEC §6.3: "All segments in this sequence [hadith → gharib → meaning → fawa'id] should be grouped as one teaching unit"
- Reality: grouping the full sequence produces 200-400 word excerpts with 5-10 distinct rulings, making taxonomy placement ambiguous
- Fix: Amend SPEC §6.3 to distinguish:
  - MUST group: hadith text + gharib + المعنى الإجمالي (inseparable core)
  - MAY split: individual فوائد/ما يستفاد points IF each passes 20-word minimum and includes a `parent_hadith_ref` back to the hadith excerpt
  - Current prompt produces this split behavior ~88% of the time already

### LLM QUALITY ISSUES (fix prompts before re-run)

**LQ-1: المعنى الإجمالي classification — 7 types for identical structure**
- 122 المعنى الإجمالي sections spread across: narration (40), rule_statement (27), editorial_note (21), evidence_rational (19), definition (13), opinion_statement (1), example (1)
- Root cause: LLM classifies by content, not structure. A meaning section about a narrative event → narration; about a ruling → rule_statement
- Impact: taxonomy cannot find "all hadith commentaries"; editorial_note category polluted with commentary
- Fix: Add prompt guidance: "Sections starting with 'المعنى الإجمالي' in hadith sharh texts are commentary content. Classify by the dominant teaching purpose: rule_statement if deriving rulings, narration if retelling events, opinion_statement if comparing positions. Never classify as editorial_note — editorial notes are editor's apparatus, not author's commentary."

**LQ-2: Fawa'id granularity inconsistency**
- 380 single-point excerpts (avg 34 words) vs 143 grouped blocks (avg 4.9 items, 119 words)
- 257 consecutive singles: item N immediately followed by item N+1 as separate excerpts
- 113 excerpts under 15 words (8.8%), mostly individual fawa'id bullet points
- Fix: Add explicit prompt rule: "When extracting numbered fawa'id points, group consecutive points into one excerpt unless they address clearly different fiqh topics. Minimum excerpt length: 20 words."

**LQ-3: Self-containment leniency for connective starters**
- 11 excerpts start with وهو/وهذا/ولهذا/ولكن with external referents, rated FULL
- Fix: Add to SC evaluation prompt: "An excerpt starting with a connective particle whose referent is not defined within the excerpt violates C-SC-2 and cannot be FULL."

**LQ-4: Bare section headings as excerpts**
- 8 structural_transition excerpts, average 9 words, no teaching content
- Fix: Prompt guidance: "A standalone chapter heading (باب, كتاب, فصل) of under 15 words is not a teaching unit. Attach it to the first content excerpt in the section."

### UPSTREAM ERRORS (not excerpting engine responsibility)

**UE-1: Layer detection absent — all excerpts attributed to "matn"**
- All 1,283 excerpts: layer_id = "matn", coverage_pct = 1.0, author_id = "unknown"
- In reality, ~80% of text is البسام's sharh (commentary), not المقدسي's matn
- Correctly applies LA-4 (pure matn units) given the input, but the input is wrong
- Root cause: Normalization engine did not produce text_layers for this source
- Impact: Author attribution completely broken; every excerpt says "unknown" author

**UE-2: Division hierarchy nesting bug**
- 209 excerpts (16.3%) have div_path where a كتاب is nested inside another كتاب
- Example: "كتاب الرَّضَاع > فائدة: > كِتَابُ القِصَاص" (القصاص is NOT under الرضاع)
- Root cause: Normalization engine's division detection producing incorrect nesting
- Impact: div_path metadata wrong for 16% of excerpts, affecting taxonomy placement

### EXTENSION OPPORTUNITIES (not needed for core pipeline)

**EO-1: Hadith commentary structural tagging**
- A "hadith_sharh_unit" composite type linking hadith + gharib + meaning + fawa'id excerpts would enable study flows: "show me the hadith, then its vocabulary, then its meaning, then its rulings"
- Implementation: parent_hadith_ref field on fawa'id excerpts; hadith_sequence metadata

**EO-2: Specific topic extraction for fawa'id**
- 25.7% of topics are generic (<15 chars or "كتاب X")
- Individual fawa'id points could have more specific topics derived from their content
- Would improve taxonomy placement precision

**EO-3: Evidence linkage**
- Only 12.9% of excerpts have populated evidence_refs
- Many rule_statement excerpts cite hadith or Quran without the reference being extracted
- Full evidence extraction is deferred but valuable for the knowledge graph

---

## Lessons Learned

**L-1: Hadith sharh texts have a natural micro-structure** (hadith → gharib → meaning → fawa'id) that creates tension between SPEC §6.3 (group everything) and practical study design (split for granularity). The SPEC needs to acknowledge this tension and provide explicit rules rather than a blanket "group everything" directive.

**L-2: The LLM's content-based classification is both a strength and weakness.** It correctly identifies the intellectual purpose of text (ruling vs narrative vs definition), but it ignores structural signals (المعنى الإجمالي is ALWAYS commentary regardless of content). The prompt needs to blend structural and content awareness.

**L-3: The absence of a "narrator" role reveals a SPEC design gap.** The SPEC was designed around matn-sharh relationships and scholarly opinion attribution. It didn't account for isnad-chain participants, who are fundamentally different from scholars giving opinions. This gap affects 100% of hadith narrations.

**L-4: Decontextualization defenses work.** Despite the classification issues, the engine successfully keeps scholarly debates intact, preserves question-answer pairs, and includes refuted positions with their refutations. This is the most critical function of the excerpting engine, and it works.

**L-5: PARTIAL self-containment with notes is a reliable middle ground.** 100% of PARTIAL excerpts have accurate notes explaining what context is missing. This means the taxonomy and synthesis engines can work with PARTIAL excerpts by incorporating the context hints. The PARTIAL→FULL upgrade path through cross-references is a viable quality optimization.

---

## Verdict

**CONDITIONAL PASS** for the excerpting engine on Taysir.

The engine produces scholarly-quality excerpt boundaries with strong decontextualization defenses. The output is reliable enough for taxonomy placement and owner review. However, **3 fixes are required before production re-run:**

1. **SG-1** (add narrator role) — SPEC change + prompt update
2. **LQ-1** (المعنى الإجمالي standardization) — prompt update
3. **LQ-2** (fawa'id granularity rule) — prompt update

**2 fixes are required before synthesis engine:**

4. **UE-1** (layer detection) — normalization engine fix
5. **UE-2** (division hierarchy) — normalization engine fix

---

*Diagnostic generated: 2026-03-31 | Reviewer: Claude Chat (Architect) | Dataset: campaign_20260331/taysir*
