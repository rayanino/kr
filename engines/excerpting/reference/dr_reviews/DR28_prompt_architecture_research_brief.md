# DR28 — Prompt Architecture Research Brief

**Target:** Claude DR (scholarly reasoning + architecture) and ChatGPT DR (patterns + state-of-the-art)
**Branch:** excerpting-foundations-hardening-20260404
**Date:** 2026-04-07

## Context

The KR excerpting engine uses a ~1500-word behavioral prompt (GROUP_SYSTEM_PROMPT) containing ~25 rules for grouping Arabic scholarly text segments into self-contained teaching units. The rules govern decontextualization prevention, self-containment evaluation, conflict resolution, and domain-specific patterns (hadith commentary, derived benefits, proof structures).

An attempt to compress this prompt to ~800 words per DR21 research (instruction compliance decays as P ~ p^N) was reverted after Gemini CLI found 2 quality gaps immediately. The owner challenged the compression approach: "The main metric is quality; nothing should affect quality."

The fundamental question: **What is the optimal architecture for delivering 25+ complex behavioral rules to an LLM when quality is the absolute priority and word count is not a constraint?**

## What We Know

1. **DR21 finding:** Compliance with N simultaneous instructions decays exponentially (P ~ p^N). Fewer rules = better compliance.
2. **BUT:** Compression loses edge-case nuance. Gemini found gaps in causal particles and classical ordinals within one review.
3. **Models handle 128K+ context.** The 1500-word limit was self-imposed, not technical.
4. **Rule COUNT matters more than prompt LENGTH.** A well-structured 2000-word prompt with 15 rules may outperform a compressed 800-word prompt with 15 rules that lost detail.
5. **OpenRouter caches system prompts** >= 1024 tokens (50% cost reduction, 80% latency reduction).
6. **The prompt is called per-chunk** — hundreds of times per book. Architecture affects cost and consistency.

## Research Questions for DR

### Q1: Multi-message architecture
Can behavioral rules be split across system prompt (stable rules) and user prompt (task-specific rules) with measurably better compliance than a single system prompt? What does the 2024-2026 research say about system vs user prompt attention patterns?

### Q2: Structured rule formats
Does presenting rules as XML/JSON structures, numbered priority lists, or decision tables improve compliance compared to free-text prose? Any 2025-2026 benchmarks on structured vs unstructured behavioral instructions?

### Q3: Progressive rule disclosure
Can rules be loaded dynamically based on input characteristics (e.g., hadith text gets hadith rules, fiqh text gets fiqh rules)? What's the quality impact of removing irrelevant rules vs keeping them for context?

### Q4: Rule hierarchy and attention
What's the state of the art on positional attention for behavioral prompts? Is the "U-shaped attention" (Lost in the Middle) still valid for frontier models in 2026? Do priority markers ("CRITICAL:", "HIGH:") measurably improve compliance?

### Q5: Reference document pattern
Can a "reference appendix" be attached as a separate message that the model consults when needed (like a textbook appendix) rather than embedding all rules in the primary instruction? Any evidence this works with frontier models?

### Q6: Multi-turn instruction loading
Does a multi-turn pattern (message 1: role + principles, message 2: detailed rules, message 3: task + input) improve compliance over single-message delivery? Any cost/latency implications?

### Q7: Arabic-specific considerations
Does the 2-3x tokenization overhead for Arabic text change the optimal prompt architecture? Any Arabic-specific prompt engineering research from 2025-2026?

## File References (for DR sessions with repo access)

- `engines/excerpting/src/phase2_group.py` — GROUP_SYSTEM_PROMPT (the prompt in question)
- `engines/excerpting/src/phase2_classify.py` — CLASSIFY_SYSTEM_PROMPT (comparison: ~450 words, simpler)
- `engines/excerpting/src/phase3_enrichment.py` — ENRICH_SYSTEM_PROMPT (comparison: ~300 words)
- `engines/excerpting/SPEC.md` §5.3.2 — SPEC version of the prompt
- `engines/excerpting/reference/dr_reviews/DR21_claude_prompt_compression_recipe.md` — the DR21 compression research

## Expected Output

A structured report with:
1. Recommended architecture (with evidence)
2. Per-question findings with citations
3. Specific implementation guidance for the KR GROUP prompt
4. Risk analysis of each approach
5. Cost/latency implications
