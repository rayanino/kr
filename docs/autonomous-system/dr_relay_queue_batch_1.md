# DR Relay Queue — Batch 1 (Research Gaps)

**Generated:** 2026-04-07
**Status:** READY FOR RELAY — /prompt-architect principles applied
**Purpose:** First batch of Pillar 1 research prompts. These address the highest-priority unresolved gaps found by scanning the codebase.

**Relay priority:** Top-to-bottom. Owner processes as many as capacity allows.

---

## RQ-001: Gemini DR — Excerpting Open Questions: Scholarly Calibration Cases

**Priority:** CRITICAL
**Unblocks:** OQ-001, OQ-002, OQ-003, OQ-004 in SPEC §6.18-6.23
**Target:** Gemini Deep Research
**File bundle:** Upload `engines/excerpting/SPEC.md` (sections §6.18-6.23) + `.claude/rules/arabic-scholarly-conventions.md`

```
You are an expert in classical Islamic legal texts (fiqh) and the methodology of Islamic scholarly writing. I need calibration cases — real examples from Islamic scholarly literature — to resolve 4 open questions in my text excerpting engine.

I have uploaded the relevant SPEC sections. Read §6.18-6.23 for the full context of each open question.

QUESTION 1 (OQ-001): School-specific distinction threshold
When a Hanafi fiqh text defines a technical term (e.g., الكلالة — those who die without parents or children) and a Shafi'i text defines the same term differently, when is the difference large enough to deserve SEPARATE definition entries versus being noted as a variant within ONE entry?

Provide 5 real examples from Islamic fiqh literature where:
- 2 cases where school definitions are genuinely distinct (different semantic scope)
- 2 cases where school definitions are merely different wordings of the same concept
- 1 borderline case that is genuinely hard to classify

For each example: the Arabic term, the two school definitions (in Arabic), and why they are distinct vs. same.

QUESTION 2 (OQ-002): Significance threshold generalization
The SPEC defines a "significance test" for when a brief mention of related content within a larger excerpt is significant enough to warrant its own excerpt. The current test has 3 criteria (from the D3 case of a short proof mention within a definition of الكلالة). Do these 3 criteria generalize?

Provide 5 cases from Islamic scholarly texts where:
- A brief mention appears within a larger scholarly discussion
- The mention is clearly significant (should be excerpted separately)
- OR the mention is clearly insignificant (should stay as part of the larger excerpt)

What additional criteria (beyond the current 3) would a classical Islamic scholar use to judge significance?

QUESTION 3 (OQ-003): Context-fill threshold
When an excerpt carries related text from another excerpt (e.g., a definition carries a brief proof), at what point should the carried text be replaced by a summary/pointer ("context-fill") instead of the full original text?

Provide examples from Islamic scholarly pedagogy: when do teachers give the full original text vs. a summary reference? What is the traditional scholarly principle governing this?

QUESTION 4 (OQ-004): Analysis authority boundary
Pre-excerpt structural analysis (identifying what kind of content is in a passage before excerpting it) must inform but not decide the excerpting outcome. How does traditional Islamic scholarly methodology handle the tension between classification and content?

Provide examples from classical Islamic scholarly practice where preliminary classification (e.g., "this is a fiqhi discussion") was wrong or misleading, and how scholars handled the correction.

For all questions: use real Arabic text. Cite specific classical works where possible.
```

---

## RQ-002: Claude DR — Taxonomy Tree Reliability Assessment

**Priority:** HIGH
**Unblocks:** Taxonomy engine trustworthiness (memory: "trees NOT yet trustworthy")
**Target:** Claude Deep Research

```
You are reviewing the taxonomy engine of the KR Islamic scholarly library project. The taxonomy engine organizes excerpted scholarly knowledge into a hierarchical tree of Islamic sciences.

Repository: github.com/rayanino/kr
Branch: excerpting-foundations-hardening-20260404

Read these files:
1. engines/taxonomy/SPEC.md — the taxonomy engine specification
2. engines/taxonomy/src/ — all source files
3. engines/taxonomy/tests/ — all test files
4. library/science_trees/ — current science tree data (if it exists)
5. NEXT.md — project status (the note: "Taxonomy: parallel build, trees NOT yet trustworthy")

The project leadership says the taxonomy trees are "NOT yet trustworthy." Your task: determine exactly WHY they are not trustworthy and what would make them trustworthy.

Investigate:

1. CURRENT STATE ASSESSMENT
   What does the taxonomy engine currently do? What works correctly? What is broken or incomplete? Cite specific test files and their pass/fail status.

2. TRUSTWORTHINESS CRITERIA
   What specific criteria must the taxonomy trees meet to be considered "trustworthy" for the summer full-build? Define these as measurable checkpoints.

3. DEPENDENCY ANALYSIS
   What does the taxonomy engine depend on from upstream engines (especially excerpting)? Are these dependencies currently satisfied? What is blocked?

4. HARDENING PRIORITIES
   If the autonomous system has 83 days to make the taxonomy engine trustworthy, what are the top 10 specific tasks, ordered by impact?

5. RESEARCH GAPS
   What questions about Islamic sciences classification need Deep Research (Gemini DR for Islamic methodology) before the taxonomy engine can be completed?

Cite specific files, functions, test names, and SPEC sections in every finding. Do not provide general advice.
```

---

## RQ-003: ChatGPT DR — Passaging Engine: Scholarly Text Structure Patterns

**Priority:** HIGH
**Unblocks:** Passaging engine [NOT YET IMPLEMENTED] features, boundary detection quality
**Target:** ChatGPT Deep Research

```
You are a software architect specializing in text processing pipelines for structured documents. You have access to the private GitHub repository.

Repository: github.com/rayanino/kr
Branch: excerpting-foundations-hardening-20260404

Read these files:
1. engines/passaging/SPEC.md — passaging engine specification (note the [NOT YET IMPLEMENTED] features)
2. engines/passaging/src/ — all source files
3. engines/passaging/tests/ — all test files
4. engines/excerpting/SPEC.md §4 — how the excerpting engine consumes passages

The passaging engine splits normalized text into scholarly "passages" — coherent units that the downstream atomization and excerpting engines process. It has several [NOT YET IMPLEMENTED] features including quality prediction, commentary alignment, and argument structure detection.

Investigate:

1. IMPLEMENTATION GAP ANALYSIS
   List every [NOT YET IMPLEMENTED] feature in the passaging SPEC. For each, assess:
   - How critical is it for the downstream excerpting engine?
   - What would break or degrade in excerpting if this feature remains unimplemented?
   - Estimated implementation complexity (small/medium/large)

2. BOUNDARY DETECTION QUALITY
   The passaging engine must split text at scholarly-natural boundaries. Analyze the current boundary detection logic:
   - What patterns does it currently detect? (chapter headings, section markers, etc.)
   - What scholarly boundary patterns does it miss? (argument boundaries, isnad-to-matn transitions, commentary layer shifts)
   - What would cause a bad split that corrupts downstream excerpting?

3. COMMENTARY ALIGNMENT
   Arabic Islamic texts frequently have layered structure (matn + sharh + hashiyah). The passaging engine needs to align these layers. Analyze:
   - What does the current code handle?
   - What commentary structures would break it?
   - What is the minimum viable commentary alignment for the summer build?

4. HARDENING PRIORITIES
   Top 10 specific improvements for the passaging engine, ordered by impact on downstream excerpting quality.

Cite specific files, functions, line numbers, and SPEC sections. Include code snippets when relevant.
```

---

## RQ-004: Gemini DR — Hadith Text Processing: Isnad-Matn Boundaries

**Priority:** HIGH
**Unblocks:** Excerpting SPEC hardening for hadith texts, passaging boundary detection
**Target:** Gemini Deep Research
**File bundle:** Upload `engines/excerpting/SPEC.md` (§4, §6) + `AGENTS.md` (transmission formulas section) + `.claude/rules/arabic-scholarly-conventions.md`

```
You are an expert in hadith sciences (ulum al-hadith) and the structural conventions of hadith compilations. I am building a pipeline that processes Arabic hadith texts, and I need to understand the structural patterns to correctly identify boundaries.

Read the uploaded files for project context.

QUESTION 1: ISNAD-MATN BOUNDARY PATTERNS
An isnad (chain of narrators) transitions to a matn (hadith text) at a specific point. What are ALL the patterns that signal this transition?

Provide examples from major hadith compilations (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah) showing:
- The typical isnad-to-matn transition markers
- Unusual or irregular transitions that would fool a pattern-based detector
- Cases where the transition is ambiguous (the boundary is genuinely unclear)

For each example, provide the Arabic text and explain where exactly the boundary falls and why.

QUESTION 2: COMPOUND ISNADS
Some hadiths have multiple isnads (e.g., the same hadith narrated through different chains). How should the pipeline handle:
- Multiple isnads for the same matn (should they be grouped as one unit or kept separate?)
- Isnads that share a common link (mudtarib or mutallib patterns)
- Mu'allaq (suspended) isnads where part of the chain is omitted

QUESTION 3: HADITH COMMENTARY STRUCTURE
In hadith sharh works (e.g., Fath al-Bari, Sharh Muslim by Nawawi), the commentary interleaves with the hadith text. What structural patterns distinguish:
- The hadith text itself (matn)
- The commentator's explanation (sharh)
- Grammatical/lexical notes (sharh al-gharib)
- Extraction of legal rulings (istinbat)
- Cross-references to other hadiths (shawahid)

How would a machine reliably detect these transitions? What markers are consistent vs. unreliable?

QUESTION 4: ATOMIC HADITH UNITS
For the excerpting engine, what constitutes a "complete" hadith unit that should never be split? Is it:
- One isnad + one matn only?
- One isnad + one matn + takhrij (source attribution)?
- The full commentary entry (isnad + matn + all commentary)?
- Something else?

What is the traditional principle (from hadith methodology sources like al-Suyuti's Tadrib al-Rawi or Ibn al-Salah's Muqaddimah) for what constitutes a minimal complete hadith citation?

Provide real Arabic examples throughout. Scholarly precision is essential.
```

---

## RQ-005: ChatGPT DR — Multi-Layer Text Detection: Sharh/Hashiyah Patterns

**Priority:** HIGH
**Unblocks:** Normalization layer detection (complete engine), excerpting layer-aware boundaries
**Target:** ChatGPT Deep Research

```
You are a software architect specializing in structured text analysis. You have access to the private GitHub repository.

Repository: github.com/rayanino/kr
Branch: excerpting-foundations-hardening-20260404

Read these files:
1. engines/normalization/SPEC.md — normalization engine specification (COMPLETE engine)
2. engines/normalization/src/ — source code (multi-layer text detection logic)
3. engines/excerpting/SPEC.md §6.18-6.19 — layer-aware excerpting rules
4. .claude/rules/arabic-scholarly-conventions.md — marginal note indicators and layer rules
5. tests/fixtures/ — examine any test fixtures that contain multi-layer text

Islamic scholarly texts frequently contain multiple layers:
- Matn (original text)
- Sharh (commentary on the matn)
- Hashiyah (gloss on the sharh)
- Ta'liq (editor's annotations)
- Muhaqqiq notes (critical edition apparatus)

These layers are often interleaved in the same page with subtle textual markers (font size, brackets, inline signals like "قال المصنف" / "قال الشارح").

Investigate:

1. CURRENT DETECTION CAPABILITIES
   What does the normalization engine currently detect? What patterns does it recognize? What layer types does it support? Cite specific code and test coverage.

2. FAILURE MODES
   What multi-layer patterns would the current system FAIL to detect? Provide 5 specific examples of real scholarly text structures that would be misclassified or missed entirely. What are the consequences for downstream excerpting?

3. DETECTION APPROACH COMPARISON
   For improving layer detection, compare these approaches:
   a) Rule-based pattern matching (regex + state machine for Arabic markers)
   b) LLM-based classification (send text chunk to model, ask "what layers are here?")
   c) Hybrid (rule-based first pass + LLM for ambiguous cases)
   Which approach best balances accuracy, cost, and maintainability? Consider that all LLM calls require D-041 multi-model consensus.

4. HASHIYAH-SPECIFIC CHALLENGES
   Hashiyah texts are the hardest layer to detect because they comment on the sharh, not the matn. The relationship chain is: matn → sharh → hashiyah. What structural patterns distinguish hashiyah text from sharh text? Are there reliable markers, or is this fundamentally ambiguous without broader context?

5. HARDENING RECOMMENDATIONS
   Top 5 improvements to layer detection that would most improve excerpting quality, ordered by impact.

Cite specific code, test names, and SPEC sections. Ground every recommendation in the actual codebase.
```

---

## Relay Summary

| ID | Target | Topic | Priority | Estimated Time |
|----|--------|-------|----------|---------------|
| RQ-001 | Gemini DR | Excerpting OQ-001 to OQ-004 calibration cases | CRITICAL | 30-60 min |
| RQ-002 | Claude DR | Taxonomy tree trustworthiness assessment | HIGH | 30-60 min |
| RQ-003 | ChatGPT DR | Passaging engine gap analysis + hardening | HIGH | 20-40 min |
| RQ-004 | Gemini DR | Hadith text processing: isnad-matn boundaries | HIGH | 30-60 min |
| RQ-005 | ChatGPT DR | Multi-layer text detection: sharh/hashiyah patterns | HIGH | 20-40 min |

**File bundles for Gemini DR (RQ-001 and RQ-004):**
- RQ-001: `engines/excerpting/SPEC.md` + `.claude/rules/arabic-scholarly-conventions.md`
- RQ-004: `engines/excerpting/SPEC.md` + `AGENTS.md` + `.claude/rules/arabic-scholarly-conventions.md`

**All 5 can be relayed in parallel — no dependencies.** Combined with Batch 0 (3 design prompts), this gives the owner 8 prompts to relay.
