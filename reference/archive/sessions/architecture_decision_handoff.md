# Architecture Decision Session Handoff

**Date:** 2026-03-22
**From:** Long architecture review chat (context degraded)
**To:** Fresh chat session
**Purpose:** Continue the architecture work — either validate further or begin excerpting engine SPEC

---

## What This Session Decided

### Pipeline Shape: 5 engines, 3 remaining

```
Source ✅ → Normalization ✅ → Excerpting → Taxonomy → Synthesis
```

Passaging absorbed into excerpting (Phase 1 preprocessing). Atomization absorbed into excerpting (Phase 2 LLM extraction). Taxonomy and synthesis remain separate.

**Governing document:** `experiments/architecture_test/ARCHITECTURE_DECISION.md` (v2, committed at 5636ceb)

### Evidence That Supports This

1. **Architecture C experiment** (10 divisions, 5 books, all prose):
   - LLM identifies sensible teaching unit boundaries in 10/10 divisions
   - Two-phase (classify then group) beats single-phase in 10/10
   - Cross-boundary context showed no benefit; D-011 stays hard
   - Results: `experiments/architecture_test/EVALUATION_WORKBOOK.md`

2. **Full Shamela division analysis** (2,065,297 divisions, 17,155 books):
   - 96.8% of divisions ≤ 2000 words (no split needed)
   - 99.1% ≤ 5000 words
   - 29.1% < 50 words (trivial merge with neighbor)
   - 0.9% > 5000 words (mostly heading detection artifacts in raw HTML)
   - Results: `experiments/architecture_test/SHAMELA_DIVISION_ANALYSIS.md`
   - Raw data: `experiments/architecture_test/shamela_division_data.json` (37MB)

3. **Passaging complexity analysis**: core logic is ~500 lines deterministic code (prototyped in `experiments/architecture_test/extract_divisions.py`). Not engine-worthy at 12-23 sessions per engine.

### What Is NOT Yet Validated — The Honest Gaps

These are real uncertainties, not theoretical risks:

| Gap | Why It Matters | What Would Test It |
|-----|---------------|-------------------|
| Zero non-prose texts tested | Verse, QA, commentary, dictionary have different structures. Phase 1 format-specific logic is designed from old SPECs, not empirical evidence. | Run experiment on verse (e.g., ألفية with sharh), QA (e.g., فتاوى), dictionary, commentary texts |
| Max tested division was 1040 words | 3.2% of divisions are 2000-5000w. LLM may behave differently on longer text. | Run experiment on 3-5 divisions in the 2000-5000w range |
| Same model evaluated its own output | Claude (Architect) evaluated Claude (Opus via OpenRouter). A human scholar might disagree. | Owner spot-checks 5-10 teaching unit boundaries against his own reading |
| Books with empty division trees not tested | 5,901 books in Shamela had < 5 headings. These need flat passaging or fallback. | Test 2-3 books with minimal structure |

### What the Next Session Should Do

The architect in the previous session (me) recommended: **run an expanded experiment covering the 4 gaps above BEFORE writing the excerpting engine SPEC.** The reasoning: the SPEC's internal design depends on how well the LLM handles non-prose formats and larger divisions. Designing without testing risks building the wrong thing — which is exactly the mistake that created the 7-engine architecture.

However, this is a judgment call. The alternative is to write the SPEC with explicit "needs empirical validation" flags on the uncertain sections, then validate during the engine's own evaluation phase. The fresh session should make this call independently.

---

## Key Files to Read

**Architecture decision:**
- `experiments/architecture_test/ARCHITECTURE_DECISION.md` — the committed decision with full evidence

**Experiment data:**
- `experiments/architecture_test/EVALUATION_WORKBOOK.md` — full Arabic text + LLM results for 10 divisions
- `experiments/architecture_test/EXPERIMENT_DESIGN.md` — methodology and decision criteria
- `experiments/architecture_test/results/RUN_SUMMARY.md` — quantitative overview
- `experiments/architecture_test/SHAMELA_DIVISION_ANALYSIS.md` — 2M division analysis

**Old SPECs to mine (not to follow blindly):**
- `engines/passaging/SPEC.md` — §4.A.4-§4.A.9 have format-specific strategies worth absorbing
- `engines/atomization/SPEC.md` — scholarly function classification taxonomy
- `engines/excerpting/SPEC.md` — self-containment evaluation, metadata enrichment

**Normalization output (excerpting's input):**
- `engines/normalization/SPEC.md` §3 — output contract
- `engines/normalization/contracts.py` — data schemas
- `experiments/architecture_test/packages/` — real normalized packages

**Taxonomy input (excerpting's output must match):**
- `engines/taxonomy/SPEC.md` §2 — input contract

**Quality and integrity:**
- `KNOWLEDGE_INTEGRITY.md` — T-1 through T-7 corruption threats
- `reference/protocols/QUALITY_AXIOM.md` — architect is sole quality gate
- `SILENT_FAILURES.md` — silent failure patterns

---

## Lessons From This Session

1. **The first pass was premature.** I read 10 divisions of experiment data and committed an architecture within one response. The owner pushed back. The deep review found 7 untested assumptions and led to a fundamentally different (better) conclusion.

2. **The experiment tested the wrong question.** It tested "can an LLM identify teaching units?" (yes) but assumed passaging was still needed. Nobody challenged that assumption until the deep review.

3. **96.8% confirmed across 2M divisions.** This is the strongest empirical finding. The passaging elimination hypothesis wasn't just plausible — it was overwhelmingly supported by full-scale data.

4. **All 10 experiment divisions were prose.** This is the biggest remaining gap. Format diversity was zero. The fresh session must address this before the SPEC is finalized.

5. **Context degradation is real.** This session ran extremely long. The quality of analysis visibly declined in later responses. The owner was right to request a fresh chat.

---

## Commits From This Session

```
5636ceb FINAL: 5-engine architecture — passaging absorbed into excerpting, 3 engines remain
2f47135 experiment: Shamela division size analysis — 23K books, 2M+ divisions
44b8999 handoff: CC task — analyze division sizes across 20K+ Shamela exports
a7ef956 decision: Commit Architecture C (C-1) — [SUPERSEDED by 5636ceb]
```
