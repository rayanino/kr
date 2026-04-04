# Deep Research Dispatch Framework

> Engineered prompts for ChatGPT Pro, Claude Chat, and Gemini DR.
> Each template extracts maximum reasoning depth from the specific model.
> Fill the [SLOTS] per atom/batch. Relay to owner for dispatch.

## When to Dispatch

Dispatch ALL THREE for every thematic batch. Each gets a different angle:

| Model | Strength to Exploit | Primary Role |
|-------|-------------------|--------------|
| **ChatGPT Pro** | Strongest structured analysis + web research. Can access the GitHub repo. | Feasibility Analyst — "Can this actually be built? What breaks?" |
| **Claude Chat** | Deepest scholarly reasoning + nuanced Arabic understanding. Can access the GitHub repo. | Scholarly Validator — "Is this correct Islamic scholarship? Grade the output." |
| **Gemini DR** | Broadest cross-domain research + corpus stress-testing. Needs file uploads. | Adversarial Stress-Tester — "Which classical text breaks this first?" |

---

## Template 1: ChatGPT Pro — Feasibility Analyst

**Access:** HAS private GitHub repo access. Give FILE PATHS, not pasted content.

```
ROLE: You are a senior systems engineer auditing the excerpting engine of an Islamic scholarly library (KR project). You have access to the full GitHub repository.

CONTEXT: The excerpting engine processes Arabic scholarly texts into self-contained teaching units. It has a 2530-line SPEC, a Phase 2b grouping prompt (1072 words), and 907+ tests. The engine is being hardened atom-by-atom from the owner's weekend feedback.

CURRENT WORK: [BATCH_NAME] batch — [ATOM_COUNT] atoms affecting [SUBSYSTEM].

Read these files:
- engines/excerpting/SPEC.md — search for "§1.1b" (foundational principles FP-1 through FP-18)
- engines/excerpting/src/phase2_group.py — the GROUP_SYSTEM_PROMPT (first 170 lines)
- engines/excerpting/contracts.py — type definitions
- [ADDITIONAL_FILES_PER_BATCH]

THE ATOMS BEING IMPLEMENTED:
[LIST_EACH_ATOM_WITH_ONE_LINE_DESCRIPTION]

ANALYSIS REQUIRED:

1. FEASIBILITY AUDIT: For each atom, answer:
   - Can this be implemented WITHOUT breaking existing behavior?
   - What specific contracts.py fields need to change?
   - What specific tests will fail or need updating?
   - Is the prompt already at 1072 words — can this atom fit without overloading?
   - Rate implementation difficulty: TRIVIAL / MODERATE / COMPLEX / ARCHITECTURAL

2. CONTRADICTION SCAN: Do any of these atoms contradict:
   - Each other?
   - The existing 18 FPs in SPEC §1.1b?
   - The current Phase 2b grouping prompt rules?
   - The current contract invariants (I-AC-*, I-CS-*, I-TU-*, I-ER-*)?

3. ADVERSARIAL SCENARIOS: For each atom, construct ONE concrete scenario where implementing it produces a confidently wrong excerpt. The scenario must use real Arabic text patterns (hadith + sharh, matn + hashiyah, fiqh masala + evidence).

4. IMPLEMENTATION ROADMAP: If you were implementing these atoms, what's the exact sequence? Which atom must come first? What's the dependency graph?

OUTPUT FORMAT: Structured findings per atom, then cross-atom analysis, then implementation roadmap. Rate each finding CRITICAL / HIGH / MEDIUM / LOW.
```

---

## Template 2: Claude Chat — Scholarly Validator

**Access:** HAS private GitHub repo access. Give FILE PATHS, not pasted content.

```
ROLE: You are an expert in classical Islamic scholarly methodology (usul al-fiqh, mustalah al-hadith, ulum al-quran, nahw) who also understands computational text processing. Your job is to validate whether the excerpting engine's rules correctly model how Islamic scholars actually wrote, organized, and transmitted knowledge.

CONTEXT: The KR library aims to be "the mind of a scholar put on a screen." Every excerpt must be as clear as if a scholar is explaining it directly. The excerpting engine has foundational principles (FP-1 through FP-18) governing how Arabic text is split into teaching units.

THE LIBRARY'S NORTH STAR: The owner's only remaining job after the library is complete is to MEMORIZE. Everything else — gathering, analyzing, organizing, cross-referencing, attributing — must be solved by the library.

CURRENT WORK: [BATCH_NAME] batch — [ATOM_COUNT] atoms.

Read these files:
- engines/excerpting/SPEC.md — search for "§1.1b" (foundational principles)
- engines/excerpting/reference/excerpt_definition_canon/01_dossier.md — the excerpt definition canon
- [ADDITIONAL_FILES_PER_BATCH]

THE ATOMS BEING IMPLEMENTED:
[LIST_EACH_ATOM_WITH_ONE_LINE_DESCRIPTION]

SCHOLARLY VALIDATION REQUIRED:

1. PER-SCIENCE CORRECTNESS: For each atom, assess whether it's correct across ALL major Islamic sciences:
   - Fiqh (jurisprudence) — does it handle ahkam + adillah + khilaf correctly?
   - Hadith (prophetic traditions) — does it handle isnad + matn + sharh correctly?
   - Tafsir (Quran commentary) — does it handle ayah + riwayat + ta'wil correctly?
   - Nahw/Sarf (Arabic grammar) — does it handle matn + sharh + shawahid correctly?
   - Usul al-fiqh (methodology) — does it handle qawa'id + ta'sil + tatbiq correctly?
   - Aqidah (creed) — does it handle musallama + burhan + radd correctly?

2. CONCRETE ARABIC COUNTEREXAMPLES: For each atom, provide:
   - One Arabic text passage where the atom WORKS perfectly
   - One Arabic text passage where the atom FAILS or produces wrong results
   - The specific scholarly methodology that the failure exploits

3. THE OWNER'S SCHOLARLY UNCERTAINTY: The owner said "I could totally be wrong" about hadith handling, tarjih structure, and explanation unity. For each atom derived from these assumptions:
   - Is the assumption correct?
   - What would a trained muhaddith or faqih say about this assumption?
   - Should this atom be finalized or kept provisional?

4. TEACHING UNIT GRADING: If the atoms are implemented, take this real excerpt output and grade each teaching unit 1-5 for study-readiness:
[PASTE_ATOM_TEST_OUTPUT_IF_AVAILABLE]

5. WHAT'S MISSING: What rule or principle would a scholar of [RELEVANT_SCIENCE] expect to see that ISN'T in these atoms? What scholarly convention is being violated?

OUTPUT FORMAT: Per-atom scholarly assessment, then cross-science analysis, then "missing principles" section. Use Arabic text examples (not transliteration) wherever possible.
```

---

## Template 3: Gemini DR — Adversarial Stress-Tester

**Access:** CANNOT access repo. Needs FILE UPLOADS. Prepare a bundle.

**File bundle to prepare and upload:**
- `engines/excerpting/SPEC.md` (or just §1.1b + relevant §6 subsections)
- `engines/excerpting/src/phase2_group.py` (just GROUP_SYSTEM_PROMPT, lines 43-170)
- `engines/excerpting/reference/FOUNDATIONS_HARDENING_LEDGER.md`
- The specific collection files for the current batch (e.g., `chatgpt_f3_collection/09_nonnegotiables.jsonl`)
- The atom_test.py output if available

```
ROLE: You are an adversarial auditor tasked with finding every way these excerpting rules will CATASTROPHICALLY FAIL when applied to the most structurally demanding texts in the classical Islamic corpus. You must think like a scholar who has spent decades with these texts and knows exactly where automated systems break.

CONTEXT: An excerpting engine processes Arabic scholarly texts into self-contained teaching units. The attached files show:
- SPEC §1.1b: 18 foundational principles (FP-1 through FP-18)
- GROUP_SYSTEM_PROMPT: The actual prompt the LLM receives (1072 words)
- LEDGER: What has been finalized so far

CURRENT WORK: [BATCH_NAME] batch — [ATOM_COUNT] atoms being hardened.

THE ATOMS:
[LIST_EACH_ATOM_WITH_ONE_LINE_DESCRIPTION]

ADVERSARIAL STRESS-TEST:

1. CORPUS ATTACK: Project these atoms against the three hardest texts in the tradition:
   - Al-Mughni by Ibn Qudamah (2000+ pages, multi-school comparative fiqh, tarjih-first structure)
   - Al-Muhalla by Ibn Hazm (recursive ilzam refutations, 3+ nesting levels)
   - Tafsir al-Tabari (20+ narrations per ayah with full isnads)
   Which atom breaks FIRST in each text? Why? Give a specific page/chapter reference if possible.

2. SILENT FAILURE CONSTRUCTION: For each atom, construct a scenario where:
   - The engine produces an excerpt that LOOKS correct
   - The excerpt PASSES all automated tests
   - But the excerpt is WRONG in a way only a scholar would notice
   - The error would propagate into the owner's understanding if studied

3. PRINCIPLE CONFLICTS: The current prompt has 38 directive lines. These atoms will add more. Identify:
   - Which pairs of rules will CONFLICT in real text?
   - What happens when the LLM encounters both rules simultaneously?
   - Which rule wins? Is that the RIGHT answer?

4. THE PROMPT OVERLOAD QUESTION: The prompt is at 1072 words with a cap at 1500. If these atoms add 200 more words:
   - Will the LLM start IGNORING some rules?
   - Which rules will be ignored first (LLMs have primacy and recency bias)?
   - Should some rules be moved to post-grouping validation instead?

5. WHAT WOULD IBN QUDAMAH SAY? If the greatest comparative jurist in Islamic history reviewed these excerpting rules, what would he say is:
   - The single biggest strength?
   - The single biggest blind spot?
   - The one thing the rules assume that no scholar would agree with?

6. MISSING GENRES: What Islamic text GENRE is completely unaccounted for by these rules?
   - Biographical dictionaries (tabaqat)?
   - Grammatical glossaries (mu'jam)?
   - Hadith nomenclature (mustalah)?
   - Poetic anthologies (diwan)?
   - Legal maxims collections (qawa'id fiqhiyyah)?

OUTPUT: Structured by attack category. Rate each finding CATASTROPHIC / SEVERE / MODERATE / MINOR. The findings rated CATASTROPHIC are the ones that will silently corrupt the owner's knowledge if not fixed.
```

---

## How Session 2 Uses This Framework

### Per Thematic Batch:

1. **Fill the slots** in all three templates:
   - `[BATCH_NAME]` — e.g., "Self-Containment"
   - `[ATOM_COUNT]` — e.g., "6"
   - `[SUBSYSTEM]` — e.g., "C-SC criteria, linking words, taqdir"
   - `[LIST_EACH_ATOM]` — one line per atom from the extraction
   - `[ADDITIONAL_FILES]` — collection files relevant to this batch

2. **Dispatch all three simultaneously:**
   - ChatGPT Pro: relay the filled Template 1
   - Claude Chat: relay the filled Template 2
   - Gemini DR: upload the file bundle + relay the filled Template 3

3. **Wait for all three to return.** Do NOT implement before all three report.

4. **Synthesize** using the ATOM_PROTOCOL Step 5 decision mechanism.

### Prompt Engineering Principles Applied:

- **RISEN framework:** Each template has Role → Instructions → Steps → End goal → Narrowing constraints
- **Devil's Advocate framework:** Template 3 (Gemini) is pure adversarial attack
- **Specificity over generality:** Each template names specific files, specific Arabic patterns, specific text references
- **Model-aware design:** ChatGPT gets implementation focus, Claude gets scholarly depth, Gemini gets breadth + stress-testing
- **Structured output requirement:** Every template demands categorized, severity-rated findings
