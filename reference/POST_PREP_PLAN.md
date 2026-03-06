# Post-Preparatory Plan — ما بعد الإعداد

Last updated: 2026-03-06. Replaces: STRESS_TEST_DESIGN.md, TESTING_ARCHITECTURE.md.

## Honest Status

The autonomous prep sessions work. The SPECs are being refined. But everything 
AFTER prep is based on untested assumptions. This document names those assumptions 
and proposes experiments to test them before committing to any architecture.

---

## The Phases (simplified)

```
Phase 1: PREP          — Claude Chat refines SPECs (current, working)
Phase 2: VALIDATE      — Test critical assumptions BEFORE building
Phase 3: BUILD + TEST  — Claude Code builds incrementally, testing each layer
Phase 4: SCALE         — Process hundreds of sources, fix until trusted
Phase 5: APPLICATION   — Build the GUI on top of the trusted pipeline
```

Phase 2 is new. It didn't exist in any previous plan. It exists because I realized 
I was designing elaborate testing systems without knowing if the fundamental 
assumptions hold.

---

## Phase 2: VALIDATE (before Claude Code builds anything)

### Experiment 1: Can LLMs evaluate Arabic scholarly output?

**Why this matters:** The entire testing architecture depends on LLMs judging 
pipeline output. If they can't, every plan I wrote is wrong.

**Method:** Take 10 real Arabic excerpts from well-known Islamic texts. 
For each, write a claim (e.g., "this is attributed to the Hanbali school"). 
Make 5 correct and 5 deliberately wrong. Send to 4 models via OpenRouter 
(Claude, GPT, Gemini, DeepSeek). Measure:
- Accuracy: do they correctly identify right vs wrong?
- Agreement: do different models agree?
- Arabic competence: can they read Classical Arabic or only Modern Standard?

**What it decides:** If accuracy >85% and agreement >70%, multi-model 
evaluation is viable. If accuracy <70%, we need a fundamentally different 
approach (more human review, or a different evaluation strategy entirely).

**Cost:** ~$2. **Time:** 1 session.

### Experiment 2: Can the synthesis engine produce study-worthy entries?

**Why this matters:** The synthesis engine is the product. If LLMs can't 
produce scholarly Arabic entries at the target quality, the entire pipeline 
design needs rethinking.

**Method:** Take 5 excerpts (real Arabic text) on one topic. Send to Claude 
with the synthesis prompt from the SPEC. Compare output against ENTRY_EXAMPLE.md. 
Have the owner read it and judge: "Would I study from this?"

**What it decides:** If the owner says yes, the synthesis approach works. 
If no, we need to understand WHY (wrong attribution? bad Arabic? too shallow? 
hallucinated content?) and redesign before building.

**Cost:** ~$1. **Time:** 1 session with owner involvement.

### Experiment 3: What's the actual cost of Arabic evaluation?

**Why this matters:** I estimated $170 for 500 sources. Arabic tokenizes 
2-3x more than English. The real cost could be $500-1000.

**Method:** Send 10 Arabic text samples through OpenRouter. Measure token 
counts. Extrapolate to 500 sources × 150 excerpts.

**What it decides:** Whether the cost model is viable or needs adjustment.

**Cost:** ~$0.50. **Time:** 30 minutes.

### Experiment 4: Multi-layer detection feasibility

**Why this matters:** The normalization engine claims to detect sharh vs matn 
text layers. If this doesn't actually work, excerpting will produce garbage.

**Method:** Take one Shamela sharh export (e.g., Sharh Ibn Aqil). 
Manually identify 5 pages with clear matn+sharh. Send to Claude with 
the detection prompt. Does it correctly separate the layers?

**Cost:** ~$1. **Time:** 1 session.

---

## Phase 3: BUILD + TEST (incremental, not all-at-once)

After experiments validate the assumptions, Claude Code builds in layers. 
Each layer is tested with real sources before the next begins.

**Layer 1:** Source + Normalization → test with 20+ sources
**Layer 2:** Passaging + Atomization → test with same 20+ sources  
**Layer 3:** Excerpting + Taxonomy → test with 20+ sources (needs LLM APIs)
**Layer 4:** Synthesis → test with 20+ sources (needs LLM APIs)

The testing approach is determined by Experiment 1 results:
- If multi-model evaluation works → use a model panel
- If single strong model is sufficient → use that (simpler, cheaper)
- If LLMs can't evaluate well → rely more on deterministic checks + owner sampling

---

## Phase 4: SCALE (hundreds of sources)

The approach here depends entirely on what we learn in Phase 3. 
Designing it now is premature. What we DO know:

- Claude Code can run in a loop autonomously (C compiler proved this)
- Parallel agents with git-based locking works (C compiler proved this)
- OpenRouter provides access to all model families with one key
- The owner has unlimited Shamela exports and PDF sources
- Cost is not a constraint

What we DON'T know (and will learn in Phase 3):
- Which evaluation approach actually catches errors
- What the real failure modes are
- How the fix loop works in practice
- What "trusted" actually looks like for this specific pipeline

---

## What the Research Found (critical for KR)

### "Can LLMs Write Faithfully?" (2025)
- GPT-4o scored 3.90/5 on Islamic content quality — decent, not perfect
- "Current LLMs fall short on faith-sensitive rigor and citation integrity"
- Recommends: heterogeneous ensemble of evaluator LLMs, Arabic-first evaluations, 
  multi-expert human validation panels

### IslamicLegalBench (2026)
- Gemini 2.5 and o3 scored >90% on Islamic legal reasoning
- Llama and Mistral scored <50%
- "Models fail systematically when Islamic jurisprudence demands exact, 
  condition-specific knowledge from classical fiqh texts"
- Different models fail differently → ensemble approach is justified

### "Building Domain-Specific LLMs Faithful To The Islamic Worldview"
- RAG (retrieval-augmented generation) is "the most promising approach" 
  for accurate Islamic content
- KR's pipeline IS a RAG system (excerpts → synthesis)
- But: "scholarly commentaries may not have originally been written in English 
  and may be in disagreement" → the synthesis engine must handle scholarly 
  disagreement explicitly, not paper over it

### Implications for KR
1. The synthesis engine is the highest-risk component. It MUST be grounded 
   in source excerpts with verifiable citations. No uncited claims.
2. Multi-model evaluation is justified by the evidence (different models 
   have different blind spots), but the specific models and approach should 
   be determined by Experiment 1, not by theory.
3. The owner's review is NOT optional, even with a perfect judge panel. 
   Islamic scholarly judgment requires human expertise.
4. Arabic-first evaluation is critical. Models must evaluate in Arabic, 
   not translated text.

---

## What NOT to Do

1. Don't design the Phase 4 architecture now. It depends on Phase 3 results.
2. Don't assume any specific model composition for the judge panel. 
   Experiment 1 determines this.
3. Don't build the evaluation system before the pipeline. Build them together.
4. Don't optimize for 500 sources before 5 sources work perfectly.
5. Don't write more plan documents. Run experiments.
