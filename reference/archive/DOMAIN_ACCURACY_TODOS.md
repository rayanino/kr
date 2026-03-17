# Domain Accuracy TODOs

**Purpose:** Improvements to make Claude Code more accurate and knowledgeable in KR's specific domain — Islamic scholarly knowledge representation, Arabic text processing, and pipeline correctness. These are separate from infrastructure/performance optimizations (already deployed).

---

## TODO 1: Domain Glossary Skill

**File:** `.claude/skills/domain-glossary/SKILL.md`

Create a glossary of 50-100 terms the pipeline actually uses, with Arabic originals, precise English definitions, and mappings to KR data model types. Claude's training data on Islamic sciences is uneven — it knows common terms but gets shaky on specialized scholarly vocabulary.

Terms to include (non-exhaustive):
- إسناد (isnad) — transmission chains, mapped to which data model
- متن / سند (matn/sanad) distinction
- جرح وتعديل (jarh wa ta'dil) — narrator grading system
- طبقات (tabaqat) — biographical dictionaries / generational layers
- شرح / حاشية / تعليق (sharh/hashiya/ta'liq) — commentary hierarchy
- تخريج (takhrij) — hadith source tracing
- مصنَّف / مسنَد / سنن / جامع (musannaf/musnad/sunan/jami') — hadith collection types
- الفروع / الأصول (furu'/usul) — branches vs foundations in fiqh
- Science tree terminology used in the taxonomy engine
- Source format terminology (Shamela BOK, OpenITI mARkdown, etc.)

Each entry must map to the corresponding KR data model type or pipeline concept. The glossary is a calibration mechanism — anchors Claude to precise definitions instead of training-data averages.

---

## TODO 2: Canonical Input/Output Examples per Engine

**Files:** Each engine's `CLAUDE.md` (7 files)

Extract 3-5 canonical input→output pairs for each engine using real Arabic text from `tests/fixtures/`. Place them directly in the engine's CLAUDE.md where Claude reads them at session start.

Format per engine:
```
## Canonical Examples

### Example 1: [description]
**Input:** [actual Arabic text or data structure]
**Output:** [actual expected output]
**Why:** [what this demonstrates about correct behavior]
```

Priority order:
1. `engines/source/CLAUDE.md` — raw source → frozen source + metadata
2. `engines/normalization/CLAUDE.md` — frozen source → manifest + content.jsonl
3. `engines/excerpting/CLAUDE.md` — atoms → self-contained excerpts (show exactly what self-containment adds)
4. `engines/taxonomy/CLAUDE.md` — excerpts → placed excerpts in science tree
5. Remaining engines

This is few-shot prompting applied to the codebase itself. Claude's code generation accuracy jumps when it can see what "correct" looks like.

---

## TODO 3: Adopt OpenITI Python Library

**File:** `requirements.txt`, engine source code, CLAUDE.md

The `openiti` Python package (`pip install openiti`) provides battle-tested Arabic text utilities:
- `openiti.helper.ara` — character normalization, composite Arabic character handling, Arabic-Indic vs Western digit distinction, text cleaning that preserves scholarly diacritics
- `openiti.new_books.convert.shamela_converter` — Shamela format conversion (directly relevant to source engine)
- `openiti.helper.funcs.text_cleaner` — removes non-word characters while respecting transcription characters

Steps:
1. Add `openiti` to `requirements.txt`
2. Audit `engines/source/src/` for hand-written Arabic text utilities that OpenITI already handles
3. Replace custom implementations with `openiti.helper.ara` functions where appropriate
4. Add to CLAUDE.md: "Use openiti.helper.ara for Arabic character normalization. Look up the API via Context7 MCP before writing custom Arabic text handling."
5. Update `.claude/skills/arabic-text/SKILL.md` to reference OpenITI functions as the preferred implementation

---

## TODO 4: Arabic Text Validation Hook

**File:** `.claude/hooks/arabic-safety-check.sh`

Replace the current advisory-only "Arabic text safe?" PostToolUse message with a concrete validation hook that catches common corruption patterns automatically:

```bash
# Checks to implement:
# 1. .lower()/.upper()/.strip() on lines containing Arabic characters
# 2. bare str.replace() on Arabic content
# 3. hardcoded Latin regex patterns applied to Arabic text (e.g., [a-zA-Z] used as word detector)
# 4. encoding assumptions (ascii/latin-1 on files that should be utf-8)
```

Wire into PostToolUse for `*.py` files in `engines/*/src/` and `shared/*/src/`. Output as stderr warnings (non-blocking) so Claude sees them but isn't interrupted.

---

## TODO 5: Multi-Model Consensus Pattern Skill

**File:** `.claude/skills/consensus-pattern/SKILL.md`

Document the exact implementation pattern for D-041 (multi-model consensus via LiteLLM + Instructor):
- How to set up a consensus call (which models, what prompt structure)
- Agreement threshold and what happens below it
- When human gates trigger vs when consensus is sufficient
- The Instructor structured output pattern for extracting typed results
- Show a complete working example with real KR types

Without this, Claude defaults to implementing naive single-LLM calls and adding consensus "later." The skill should make the consensus pattern the natural first choice.

---

## TODO 6: Session Discipline Documentation

**File:** `CLAUDE.md` or `.claude/rules/session-discipline.md`

Add explicit guidance about session management to prevent compaction-induced accuracy loss:

Key rules:
- One task per session. Start fresh for each engine, each SPEC section, each implementation block.
- Use `/catchup` to reload context from git + NEXT.md rather than relying on compacted memory.
- After any compaction, re-read the active engine's CLAUDE.md and SPEC.md before continuing.
- If a session exceeds 30 minutes, proactively run `/smart-compact` rather than waiting for auto-compaction at 80%.
- Never implement code after compaction without re-reading the relevant SPEC section — compacted context loses D-023 metadata semantics, Arabic handling nuances, and specific behavioral rules.

---

## TODO 7: Test-Fixture-Driven Development Enforcement

**File:** `.claude/rules/testing.md` (update existing)

Strengthen the testing rule to enforce real-fixture validation:
- No function is "done" until tested against at least one real Arabic fixture from `tests/fixtures/`.
- Synthetic test inputs (English text, placeholder Arabic, transliteration) are never acceptable as the only test data.
- Every PR/commit touching engine `src/` code must include or update a test that uses fixture data.
- Add a pre-push hook that verifies test coverage on modified engine code.

---

## TODO 8: Usul.ai as Research Verification Resource

**File:** `.claude/commands/research.md` (update), `reference/RESOURCES.md`

Add Usul.ai (https://usul.ai) as a verification resource for scholarly claims:
- Update the `/research` command to mention Usul.ai as a cross-reference source for Islamic text verification
- Add to `reference/RESOURCES.md` with description: "AI-powered search across 15,000+ Islamic texts including all of Shamela. Use for verifying scholarly attributions, checking hadith chains, confirming text existence."
- Not programmatically integrated, but Claude can use web search to query it when verifying scholarly claims during taxonomy or scholar_authority work

---

## Priority Order

1. **Domain glossary** (TODO 1) — highest impact, prevents most common hallucination class
2. **Canonical examples** (TODO 2) — calibrates output quality per engine
3. **OpenITI adoption** (TODO 3) — replaces handwritten code with battle-tested functions
4. **Session discipline** (TODO 6) — prevents domain knowledge degradation
5. **Arabic validation hook** (TODO 4) — catches bugs automatically
6. **Consensus pattern skill** (TODO 5) — ensures correct multi-model implementation
7. **Test fixture enforcement** (TODO 7) — forces real-data validation
8. **Usul.ai reference** (TODO 8) — adds verification resource
