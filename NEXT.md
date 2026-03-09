# NEXT — Source Engine Step 3: Build Prep

**Session type:** BUILD PREP — technology survey and Claude Code environment preparation
**Skill:** `use kr-build-prep`
**Goal:** Prepare everything Claude Code needs to build the source engine in 6 focused sessions.

---

## Context

Steps 0–2 are complete. The source engine SPEC has been hardened through 8+ review passes (Step 1) and all LLM assumptions validated through empirical testing (Step 2). The SPEC is now the behavioral authority — no ASSUMPTION markers remain.

**Step 2 Summary (evaluated in `engines/source/review/STEP2_EVALUATION.md`):**
- A1 (JSON reliability): 100% parse, 0 enum violations across 6 models. Single-call prompt confirmed.
- A2 (Multi-layer detection): 100% accuracy across 5 production models.
- A3 (Name matching): Partially validated. KNOWN ISSUE: substring containment boost needed (A3-1).
- A4 (Trust weights): 13/13 correct at threshold 0.65 (uniquely optimal). 900→1000 AH cutpoint resolved.
- A5 (Consensus pair): Command A (Cohere) + Opus 4.6 (Anthropic). 92.3% "at least one right". Fallback: GPT-5.4 + Opus 4.6.

**Two mandatory build-phase tasks from Step 2:**
1. **Confidence calibration analysis** — extract confidence scores from Step 2 results, check correlation with accuracy. If models produce >0.90 on wrong answers, raise thresholds.
2. **Name matching substring boost** — implement A3-1 fix in `normalized_name_similarity`.

---

## What to Read First

1. `NEXT.md` (this file)
2. `engines/source/review/STEP2_EVALUATION.md` — Step 2 evaluation with 5 binding decisions
3. `engines/source/STRATEGIC_PLAN.md` Phase B — build prep work items
4. `engines/source/SPEC_CORE.md` — the behavioral authority (all ASSUMPTION markers resolved)
5. `engines/source/contracts.py` — the data authority
6. `engines/source/prompts/inference_v1.py` — the validated prompt (draft-3, final)
7. `KNOWLEDGE_INTEGRITY.md` — corruption threats

---

## Build Prep Work Items (from STRATEGIC_PLAN Phase B)

### 1. Technology Survey
Verify stack decisions:
- BeautifulSoup4 + lxml → Shamela HTML parsing
- hashlib → SHA-256 freezing (stdlib)
- LiteLLM + Instructor → LLM inference via OpenRouter
- Pydantic → schema validation (contracts.py exists)
- **Research:** PyArabic vs CAMeL Tools for Arabic name normalization (including A3-1 substring boost)
- **Verify:** Does Instructor's structured output mode work with Command A (Cohere) via OpenRouter?

### 2. Deferred Code Quarantine
`engines/source/src/` has ~28 Python files. Only ~19 are core. Explicitly exclude:
- Extractors: `pdf.py`, `image.py`, `word.py`, `owner_authored.py`
- Modules: `citation_discovery.py`, `gap_analysis.py`, `openiti_enrichment.py`, `enrichment.py`
- Step 0 artifact: `tracer.py`

### 3. Shared Component Requirements
Produce `shared/{component}/REQUIREMENTS_source.md` for: consensus, human_gate, scholar_authority, validation.
Cross-check against what the normalization engine will need.

### 4. Resolve Trust Evaluation Tension
ENGINE_PROTOCOL says "keep trust simple — 3-tier." SPEC_CORE has the full 5-factor algorithm, validated.
**Resolution: SPEC_CORE wins.** Document explicitly in CLAUDE.md.

### 5. Architecture Doc
Map the 9-step acquisition pipeline to modules.

### 6. Session Plans
One per build session (6 sessions), following pipeline order:
1. Staging + Format Detection + Extraction
2. LLM Metadata Inference + Consensus
3. Hashing + Dedup + Freezing
4. Registration + Scholar Authority
5. Trust Evaluation + Human Gate + Validation
6. Integration + Plain Text + Error Paths

### 7. Mandatory Step 2 Follow-ups
- **Confidence calibration:** Add as explicit task in Session 2 plan (LLM inference session). **DATA RISK:** The Step 2 results files (`tests/results/phase1_*.json`, `phase2_*.json`, `phase3_consensus.json`) are gitignored. They must exist on the build machine. If Claude Code's environment was reset, re-run `tests/test_llm_inference.py --phase 2` to regenerate ($2-5 API cost).
- **Author-specific consensus complementarity:** The consensus pair (Command A + Opus 4.6) was selected using a metric that treats all 7 fields equally. But consensus is only used for author identification and work matching. Before implementing the consensus module, re-run `consensus_analysis.py` filtered to `author_identification` field only. If a different pair ranks higher for author-specific complementarity, update §8.
- **Committed results summary:** Test runner should produce a committed summary (no raw API text, just per-fixture scores and confidence distributions).

### 8. Step 4 Blocking Conditions
These must be resolved before Step 4 (test and prove) begins:
- [ ] Confidence calibration analysis complete — thresholds confirmed or adjusted
- [ ] Name matching substring boost (A3-1) implemented and tested
- [ ] Author-specific consensus complementarity verified — pair confirmed or updated

---

## Output Artifacts (per STRATEGIC_PLAN Phase B)

| File | Purpose |
|------|---------|
| `engines/source/docs/architecture.md` | Module structure, 9-step pipeline mapping |
| `engines/source/docs/technology-inventory.md` | Use/build/test decisions |
| `shared/consensus/REQUIREMENTS_source.md` | What source engine needs from consensus |
| `shared/human_gate/REQUIREMENTS_source.md` | What source engine needs from human_gate |
| `shared/scholar_authority/REQUIREMENTS_source.md` | What source engine needs from scholar_authority |
| `shared/validation/REQUIREMENTS_source.md` | What source engine needs from validation |
| Updated `engines/source/CLAUDE.md` | Build instructions, deferred file list |
| `engines/source/session-{1-6}-plan.md` | Per-session build plans |

---

## Done When

- [ ] Technology survey complete with use/build/test decisions
- [ ] Deferred code quarantined (moved to `src/_deferred/` or listed in CLAUDE.md)
- [ ] Shared component requirements written for all 4 components
- [ ] Architecture doc maps pipeline to modules
- [ ] 6 session plans written, each with narrow scope and clear "done when"
- [ ] CLAUDE.md updated with build instructions
- [ ] Trust evaluation tension resolved and documented
- [ ] Confidence calibration task explicitly placed in a session plan
- [ ] Name matching A3-1 fix explicitly placed in a session plan
- [ ] Author-specific consensus complementarity check placed in a session plan
- [ ] Step 4 blocking conditions documented in session plans (not just here)

After Step 3: Move to Phase C (BUILD) — Claude Code executes session plans.
