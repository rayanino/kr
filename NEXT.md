# NEXT — Excerpting Engine SPEC Design

## Context

Architecture decision FINAL (see `experiments/architecture_test/ARCHITECTURE_DECISION.md` v2).

The pipeline is 5 engines total, 3 remaining:
```
Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis
```

The excerpting engine absorbs passaging (as Phase 1 preprocessing) and atomization (merged into Phase 2 LLM extraction). This is the most complex remaining engine — it bridges deterministic text processing and LLM-powered knowledge extraction.

## Your Task

Design the excerpting engine SPEC (`engines/excerpting/SPEC_CORE.md`).

**This is a SPEC design session, not a build session. The deliverable is the SPEC.**

### What the Excerpting Engine Does

Takes normalized packages (from normalization engine) and produces teaching unit excerpts — self-contained scholarly segments with full metadata, ready for taxonomy placement and synthesis.

Three internal phases:

**Phase 1 — Deterministic Preprocessing (absorbs passaging):**
- Cross-page text assembly using boundary_continuity signals from normalization
- Division-to-chunk mapping: divisions ≤ 5000w processed directly; > 5000w split at structural markers (scholarly keywords, paragraph breaks)
- Tiny division merging: < 50w joined with adjacent sibling
- Format-specific handling: verse/commentary alignment, Q&A pair detection, مسألة block detection
- Metadata assembly: division path, text layers, content flags, footnotes, boundary_continuity
- CRLF normalization

**Phase 2 — LLM Teaching Unit Extraction (validated by Architecture C experiment):**
- Phase 2a: Classify segments by scholarly function (two-phase, validated)
- Phase 2b: Group classified segments into teaching units, evaluate self-containment
- Multi-model consensus (Opus canonical, Command A as verifier)
- D-011: teaching units contained within division/chunk boundaries

**Phase 3 — Metadata Enrichment:**
- Author attribution from text layers + source metadata
- School classification from scholarly markers
- Topic proposal for taxonomy placement
- Evidence reference detection (hadith, Quran, ijma, qiyas)
- Self-containment scoring
- Human gate triggers for low-confidence decisions

### Design Approach

1. **Read normalization engine output contracts** — the excerpting engine's input IS normalization output:
   - `engines/normalization/SPEC.md` §3 (output contract)
   - `engines/normalization/contracts.py` (NormalizedPackage, ContentUnit schemas)
   - `experiments/architecture_test/packages/` (real normalized packages)

2. **Read the old passaging SPEC** — mine it for format-specific strategies (§4.A.4-§4.A.9):
   - `engines/passaging/SPEC.md` — keep: prose splitting, verse strategy, QA strategy, masala strategy. Drop: all of §4.B.

3. **Read the old excerpting and atomization SPECs** — mine for metadata enrichment logic:
   - `engines/excerpting/SPEC.md` — self-containment evaluation, metadata enrichment
   - `engines/atomization/SPEC.md` — scholarly function classification taxonomy

4. **Read the experiment results** — empirical evidence for Phase 2:
   - `experiments/architecture_test/EVALUATION_WORKBOOK.md` — LLM output on 10 divisions
   - `experiments/architecture_test/ARCHITECTURE_DECISION.md` — decision rationale
   - `experiments/architecture_test/SHAMELA_DIVISION_ANALYSIS.md` — 2M division analysis

5. **Read threat model and quality axiom:**
   - `KNOWLEDGE_INTEGRITY.md` — T-1 through T-7 (especially T-2 attribution, T-4 context loss, T-5 hallucination)
   - `reference/protocols/QUALITY_AXIOM.md`

6. **Read what taxonomy expects** — the excerpting engine's OUTPUT must match taxonomy's input:
   - `engines/taxonomy/SPEC.md` §2 (input contract)

7. **Research** — use `kr-research` for:
   - Self-containment evaluation methods for Arabic scholarly text
   - LLM structured output reliability at scale (thousands of calls)
   - Multi-model consensus patterns for classification tasks

### Constraints

- D-011 HARD: teaching units contained within division/chunk boundaries
- D-023: never delete upstream metadata fields, always pass through
- D-004: primary_text assembled verbatim from normalization output, never modified
- All LLM calls through OpenRouter ONLY (model: anthropic/claude-opus-4.6)
- Multi-model consensus for all attribution and classification decisions
- CRLF normalization (owner on Windows)
- Error codes follow established pattern from normalization engine

### Skills to Use

- `kr-research` (output contracts, self-containment methods, consensus patterns)
- `thinking-frameworks` (DEEP tier — engine SPEC design)
- `critical-review` (verify SPEC before delivering)
- `kr-integrity` (audit for silent failures and T-1–T-7 threats)

### Do NOT Do

1. Do NOT write implementation code — SPEC only
2. Do NOT modify normalization or source engine code
3. Do NOT relax D-011
4. Do NOT design a separate passaging engine — it's Phase 1 inside excerpting
5. Do NOT assume discourse_flow will be populated — it won't
6. Do NOT skip reading the old SPECs — they contain valuable format-specific logic

## Read First

1. This file (NEXT.md)
2. `experiments/architecture_test/ARCHITECTURE_DECISION.md` — the architecture commitment
3. `engines/normalization/SPEC.md` §3 — input contracts
4. `engines/passaging/SPEC.md` §4.A — format-specific strategies to absorb
5. `engines/taxonomy/SPEC.md` §2 — output contract requirements
6. `KNOWLEDGE_INTEGRITY.md` — corruption threats
7. `reference/ENGINE_BUILD_BLUEPRINT.md` — engine build process
