# Environment Optimization — Prior Session Research Findings

> **Source:** Session 2 (2026-04-04), 3 research agents + plan synthesis.
> **Purpose:** This file is consumed by a SEPARATE environment-improvement session during Phase 2 (after independent reasoning). Do NOT read this file during Phase 1 — it introduces bias.

---

## Research Agent 1: Infrastructure Audit (Hooks, Settings, MCP)

### Hooks (19 active)
- **Safety barriers:** config-protection, destructive-guard, no-ask-human
- **Arabic text:** arabic-safety-check (blocks .lower()/.upper() on Arabic), diacritic-preservation
- **Quality gates:** pre-commit-check, stop-quality-gate, pyright-check, auto-test
- **Metadata flow:** boundary-check (D-023)
- **Spec validation:** spec-validate, spec-coverage-check
- **Cost control:** cost-guard, circuit-breaker
- **Session state:** prompt-context, pre-compact-checkpoint, post-compact-recovery
- **Formatting:** ruff-format

**GAPS found:**
1. No hook for SPEC-to-code synchronization drift (manual check_prompt_spec_sync.py only)
2. No runtime telemetry hook (budget burn rate, per-session cost warnings)
3. No concurrency/parallelization verification for worktree agents
4. No Arabic transliteration table validation
5. No cross-engine contract test validation on new tests

### MCP Servers
- Active useful: Context7, Tavily, Serena, memory graph
- Dead weight to remove: exa (duplicate of Tavily), gopls-lsp (Go, not Python), Next.js/React graph tools, duplicate Playwright instances
- Future: QuranHub MCP (deferred to taxonomy phase)

**GAPS found:**
1. No MCP for Arabic morphological analysis (camel-tools not exposed via MCP)
2. No monitoring/observability MCP (cost tracking, test failure rates)
3. No global memory bridge between agent memory and hooks

### Settings
- Model: Claude Opus 4.6 (1M context), effort: high
- Autocompact: 60% threshold
- Custom spinner tips: 7 critical reminders (Arabic safety, D-023, temperature=0, shared concepts)
- Status line: custom kr_statusline.py

---

## Research Agent 2: Agents, Skills, Commands Audit

### Agents (23 total)
**Evaluation pipeline:** excerpting-evaluator, triage-analyst, verifier-a, verifier-b, verdict-adversary, consolidator
**Quality assurance:** build-prober, spec-auditor-a, spec-auditor-b, regression-detector, quick-check
**Implementation:** code-reviewer, spec-writer, test-engineer, spec-adversary
**Research:** deep-researcher, model-researcher, arabic-reviewer
**Operational:** boundary-validator, evaluation-prep, library-integrity-checker, audit-comparator, integrity-auditor

**7 MISSING agents proposed:**
1. **isnad-validator** — parse hadith chains, validate narrator names, detect weak narrators
2. **madhab-detector** — detect legal school signals in fiqh excerpts
3. **quranic-citation-verifier** — validate Quranic references, detect diacritic corruption
4. **scholarly-convention-checker** — validate salawat formulas, colophon patterns, biographical structures
5. **prompt-drift-detector** — detect semantic drift in prompts across versions
6. **few-shot-auditor** — validate and optimize few-shot examples in prompts
7. **genre-validator** — genre-specialized excerpt quality assessment (hadith/fiqh/tafsir/nahw/aqidah)

### Skills (15 total)
Arabic text handling (4), domain/classification (3), evaluation (2), patterns (3), technical (3)

**7 MISSING skills proposed:**
1. **prompt-compression** — token optimization without semantic loss
2. **few-shot-management** — example coverage analysis, authenticity verification, replacement recommendations
3. **genre-detection** — automated genre classification + routing to specialized validators
4. **isnad-parsing** — narrator name normalization, chain integrity validation
5. **madhab-detection** — school signal identification, scholar-to-madhab cross-reference
6. **qira'at-detection** — variant reading validation against canonical sources
7. **scholarly-attribution-chains** — transmission chain analysis, spurious attribution detection

### Commands (23 total)
Quality gates, testing, development, research, admin — 23 commands exist.

**5 MISSING commands proposed:**
1. **/excerpt-test** — wrapper for atom_test.py with summary + regression detection
2. **/prompt-check** — sync check + word count + token analysis + drift detection
3. **/dispatch-all** — coordinated multi-coworker dispatch with structured logging
4. **/genre-analysis** — genre distribution analysis across excerpt corpus
5. **/arabic-fidelity-check** — comprehensive Arabic text quality verification

### 5 Agent Teams proposed (formalized):
1. Arabic Verification Team (arabic-reviewer + quranic-citation-verifier)
2. Structural Verification Team (consolidator + verifier-a + verifier-b + verdict-adversary)
3. SPEC Audit Team (spec-auditor-a + spec-auditor-b + audit-comparator + integrity-auditor)
4. Evaluation Team (evaluation-prep + triage-analyst + excerpting-evaluator + library-integrity-checker)
5. Build Quality Team (build-prober + quick-check + regression-detector)

---

## Research Agent 3: External Tools (partial — hit usage limit)

Research was cut short by API usage limits. Key findings before cutoff:
- **CAMeL Tools** (NYU Abu Dhabi, v1.4.1) — already installed but NOT used in excerpting. Provides morphological analysis, diacritization, NER for Arabic.
- **PyArabic** (v0.6.15) — already installed but NOT used in excerpting. Provides text normalization, tashkeel operations.
- Both installed but no `shared/arabic_nlp/` wrapper exists. The libraries sit unused.

**External tools that need web research (not completed):**
- Farasa (QCRI) — Arabic NLP toolkit
- OpenITI / KITAB project — corpus tools for Arabic historical texts
- Shamela API — programmatic access
- Usul.ai — Islamic scholarly verification
- Arabic-specific tokenizers (vs tiktoken)
- Isnad parsing tools
- Automated madhab detection tools

---

## Plan Summary (8 Dimensions by Impact)

| Dimension | Impact | Current Gap |
|-----------|--------|-------------|
| 1. Arabic NLP Tooling | HIGHEST | Libraries installed but unused, no wrapper |
| 2. Prompt Management | HIGH | No versioning, no A/B testing, no dashboard |
| 3. Coworker Automation | HIGH | All dispatch manual, no structured logging |
| 4. Evaluation Framework | HIGH | Single-chunk only, no batch/comparison |
| 5. Agents & Skills | MEDIUM | 23 agents but 7 missing specialists |
| 6. Testing Infrastructure | MEDIUM | 912 tests but 52/62 red-team unautomated |
| 7. MCP Servers | LOW-MEDIUM | Dead weight to remove, Arabic MCP missing |
| 8. Cost Tracking | LOW | Manual calculation only |

---

## DR Relay Prompt (not yet sent — for environment session to use)

> TASK: Research how world-class NLP projects optimize their development environments for Arabic text processing. Focus on:
> 1. What Arabic NLP tools (CAMeL Tools, Farasa, etc.) are production-ready in 2025-2026?
> 2. What evaluation frameworks exist for LLM-based text segmentation quality?
> 3. How do production LLM systems manage prompt versioning, A/B testing, and regression detection?
> 4. Are there MCP servers or VSCode extensions specifically for Arabic text analysis?
> 5. What automated tools exist for isnad (hadith chain) parsing and narrator disambiguation?
> 6. How do multi-model consensus systems automate the dispatch-collect-synthesize workflow?
>
> OUTPUT: Ranked list of tools/techniques by impact, with installation/integration instructions.
