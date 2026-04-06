# Fewer rules, better compliance: compressing LLM prompts without breaking behavior

**Compressing a 1,474-word behavioral prompt to 800–1,000 words will likely *improve* instruction adherence, not degrade it.** The empirical evidence is unambiguous: compliance with N simultaneous instructions decays exponentially (P ≈ p^N), meaning a 25-rule prompt at 95% per-rule compliance yields only ~28% perfect-run success. Cutting to 12–15 well-crafted rules roughly doubles that rate. This finding, replicated across six independent studies from 2024–2026, means the compression goal and the quality goal are aligned — the prompt is currently too long for its own good. The key risk is not compression itself but *how* you compress: merging rules that encode hard-won edge cases, removing instructions that silently shape model reasoning, or stripping Arabic-specific guidance that carries outsized weight due to tokenization costs. What follows is a four-layer analysis and a step-by-step refactoring recipe.

---

## Layer 1: Every additional rule makes every other rule less reliable

The strongest empirical finding in this space comes from the **"Curse of Instructions" paper (Harada et al., ICLR 2025)**, which introduced the ManyIFEval benchmark testing up to 10 objectively verifiable instructions per prompt across GPT-4o, Claude 3.5, Gemini 1.5, and Llama 3.1. The core result: **P(all N instructions followed) ≈ P(individual)^N**. GPT-4o with 10 instructions achieved only **15% full compliance**; Claude 3.5 Sonnet reached 44%. Critically, the per-instruction success rate also degrades as instruction count rises — adding rules doesn't just multiply failure probability, it actively weakens adherence to existing rules.

For the 25-rule GROUP prompt, the math is stark. Even at an optimistic 95% per-rule compliance, 0.95^25 ≈ **27.7%** full-run success. Reducing to 12 rules: 0.95^12 ≈ **54%**. The IFScale benchmark (Jaroslawicz et al., July 2025) confirmed this pattern at larger scales, finding the best frontier models achieved only 68% accuracy at 500 instructions and documented **bias toward earlier instructions** — rules placed later in the prompt are disproportionately violated.

**Positional attention compounds the problem.** The "Lost in the Middle" finding (Liu et al., TACL 2024) demonstrated a **U-shaped attention curve**: performance peaks when relevant information sits at the beginning or end of context, with a **30%+ accuracy drop** for middle-positioned content. In a 25-rule prompt, rules 8–17 occupy the attention dead zone. A 2025 Chroma follow-up confirmed this U-shape persists across all 18 tested frontier models. Meanwhile, the **Context Rot study (Hong et al., Chroma 2025)** tested 18 LLMs and found **every model degrades at every input-length increment** — no model is immune. Structured content with shared terminology (exactly the profile of Arabic scholarly text) creates particularly severe degradation because related terms function as distractors.

**HumanLayer's "instruction budget" concept (March 2026)** adds a crucial architectural insight: instruction-following capacity correlates with model size, **not context window size**. Extending a model from 200K to 1M tokens does not increase how many instructions it can follow. When Anthropic switched Claude Code to Opus 4.6 with 1M context, HumanLayer observed dramatic instruction adherence degradation — the model ignored design documents, misunderstood simple instructions, and directly disobeyed them. Their solution was context isolation via sub-agents, not more context.

The AGENTIF benchmark (Qi et al., NeurIPS 2025) tested prompts averaging **1,723 words with ~12 constraints** — remarkably close to the GROUP prompt's profile. The best model (o1-mini) achieved only **26.9% Instruction Success Rate**. Condition-dependent rules ("if X, then Y") proved especially failure-prone, accounting for 30%+ of errors.

### Formatting vs. behavioral: a critical distinction

Not all instructions degrade equally. **Formatting instructions** (output JSON, use numbered lists) are more reliably followed because constrained decoding can enforce them mechanistically. **Behavioral/semantic instructions** (group by thematic coherence, maintain pedagogical progression) degrade faster because they require judgment with no enforcement mechanism. The Salus AI compliance study found that reducing from 24 compliance questions to 8 per prompt dramatically improved accuracy. For the GROUP prompt, this means formatting rules should be offloaded to structured output schemas, reserving prompt space for the harder behavioral rules that only natural language can express.

### Arabic amplifies every problem

Arabic text consumes **2–3x more tokens** per word in English-centric tokenizers like GPT's. Every unnecessary English word in the prompt therefore has outsized impact on the total context budget. Research on mixed-language prompting shows English instructions with Arabic content improve performance by up to **49.5%** compared to all-Arabic prompts. Arabic instruction-following compliance is measurably lower than English across models, making instruction count reduction even more impactful.

---

## Layer 2: Six compression techniques, ranked by behavioral safety

### Instruction distillation — the safest primary technique

Condensing verbose rules into tighter imperative formulations is the lowest-risk compression method. Doug Turnbull's controlled experiment (2025) on a 480-query dataset found **concise rules-only achieved 96.5% accuracy** vs. 94.4% for verbose rules-with-examples and 93.5% for few-shot alone. The ICLR 2025 study on whether LLMs "know internally" when they follow instructions found compliance correlates more with **phrasing quality** than inherent task difficulty. For a 25-rule prompt averaging ~59 words per rule, reducing each to 32–40 words is achievable by eliminating filler phrases and converting passive to active voice — yielding a **25–30% overall reduction** without removing any rule.

The failure signature: edge cases implicitly covered by verbose wording begin producing unexpected behavior. Hedging language that encoded nuance ("when appropriate," "unless the context suggests otherwise") gets stripped, making the model too aggressive or permissive. Mitigation: preserve all conditional qualifiers, cut only connective tissue.

### Rule merging — effective but precision-sensitive

Combining related rules into higher-level principles offers 10–15% further reduction. The OpenAI GPT-5.1 Prompting Guide explicitly documents "metaprompting" for this — having the model analyze its own prompt and propose "surgical revisions" including merging conflicting or overlapping rules. In a 25-rule system, 3–5 clusters of related rules likely exist.

The critical constraint: **never merge rules that encode learned edge cases**. Rules added during hardening sessions exist because they were violated. Merging "don't split segments that share a Quranic reference" with "group by thematic coherence" loses the specificity that caught a real production failure. Merge only thematic/tonal rules where the abstract principle genuinely subsumes the specifics. The failure signature is "weasel compliance" — the model technically satisfies the abstract principle while violating the spirit of the original specific rules.

### Structured rubric replacement — good for conditional logic only

Converting prose rules to tabular format (decision tables, rubrics) works when rules are naturally conditional — input/action mappings like "if text is introductory → label Level 1; if analytical → label Level 3." The RULERS framework showed rubrics with evidence-anchored scoring outperform free-form evaluation. However, the "Let Me Speak Freely?" study (Tam et al., 2024) found format restrictions cause **10–15% reasoning degradation** for open-ended tasks. Use tables exclusively for conditional processing logic; keep behavioral principles in imperative prose.

### Chain-of-density iterative compression — the right methodology

Rather than compressing in one pass, the CoD approach (Adams et al., 2023) iteratively compresses while measuring quality at each step. The original research found **steps 3–4 (60–80% of maximum density)** optimally balance information density and coherence. For prompt compression, this translates to: compress 10% per iteration, run behavioral test suite between each, stop when any rule's compliance drops below threshold. For 1,474 → 800–1,000 words, this means 3–4 iterations with measurement gates.

### Few-shot condensation — empirically counterproductive

Replacing explicit rules with examples is the most dangerous compression technique for behavioral prompts. Turnbull's experiment showed **examples actively hurt performance**: rules-only achieved 96.5% vs. rules-with-examples at 94.4%, with errors increasing *in exactly the categories the examples targeted*. Examples cause "loss of generality" — the model pattern-matches surface features rather than extracting principles. For 25 behavioral rules, you'd need many examples to cover the behavioral space, likely exceeding the original word budget. The one exception: if the prompt already contains verbose examples, reducing from 3 to 1–2 focused examples saves significant space.

### LLMLingua — not suitable for behavioral prompts

LLMLingua (Microsoft, EMNLP 2023) and LLMLingua-2 (ACL 2024) achieve up to **20x compression** on factual/RAG prompts with minimal performance loss. But they operate by removing "predictable" tokens — and in behavioral prompts, predictable tokens are often semantically critical. "Never" and "always" are low-perplexity tokens that LLMLingua may strip. The April 2026 study "Prompt Compression in the Wild" confirmed that compressed prompts maintain quality for summarization and code generation but documented a **compression paradox**: aggressive compression can *increase* total inference cost due to an "output token explosion effect." For behavioral instructions, manual compression is categorically safer.

---

## Layer 3: A decision tree for triaging each of the 25 rules

No established "rule triage framework" exists in the literature — the following is synthesized from guardrails research, production prompt engineering, and empirical studies on format-behavior coupling.

### The four-category classification

**Category A — Must remain in prompt.** The rule requires semantic judgment, contextual reasoning, or domain expertise that cannot be expressed as a deterministic check. Examples: "Group segments by thematic coherence," "Maintain pedagogical progression within teaching units," "Distinguish introductory from analytical passages." These rules shape *how the model thinks*, not just what it outputs. No post-processing validator can enforce them because the reasoning process, not the output structure, is what they constrain.

**Category B — Can move to post-processing validator (with a critical caveat).** The rule is deterministically checkable on the output: JSON schema compliance, segment count within bounds, no duplicate segment IDs, all input segments accounted for. Implement these as code-based validators using Pydantic, Guardrails AI, or simple assertion checks. **The caveat**: research shows format-constraining instructions simultaneously shape the model's task representation. The MVES framework study found removing task-specific format instructions dropped extraction accuracy from 100% to 90%. The safe pattern is **keep a one-line version in the prompt + add a deterministic validator as a hard enforcement layer**.

**Category C — Can move to pre-processing.** The rule constrains input quality rather than output behavior: UTF-8 validation, duplicate segment removal, unique ID enforcement, batch size limits, metadata stripping. Every such rule removed from the prompt reduces context length. The Context Rot research confirms that every unnecessary token degrades performance — and these rules are entirely unnecessary in the prompt because they can be fully enforced before the LLM sees the input.

**Category D — Can be removed entirely.** The rule restates something implicit in the task description ("process all segments provided") or describes default model behavior ("be accurate"). These are candidates for removal, but **always A/B test before removing** — what appears redundant may carry implicit anti-hallucination signaling. The failure mode is silent quality degradation that only surfaces on edge cases.

### The dual-purpose problem

This is the most operationally important insight in the entire analysis. A rule like "output must be valid JSON with exactly one array of teaching units" serves two functions simultaneously: (1) it constrains output format (checkable post-hoc) and (2) it tells the model "this is a structured classification task, not a free-form discussion." Removing it from the prompt — even with a validator catching violations — may cause the model to approach the task differently, producing outputs that pass validation but are qualitatively worse.

The experimental protocol for detecting dual-purpose function:

1. **Baseline**: Run current prompt on ≥50 diverse inputs, 3 repetitions each. Record schema compliance rate, per-rule constraint satisfaction, and semantic quality scores (LLM-as-judge + human evaluation on 20+ samples).
2. **Experiment A**: Remove the rule, add post-processing validator. Run same inputs. Compare quality scores *before* validator applies corrections.
3. **Experiment B**: Remove the rule entirely, no validator. Run same inputs.
4. **Interpretation**: If A matches baseline quality → pure format rule, safe to move. If A shows lower quality even after validator → dual-purpose rule, keep condensed version in prompt. If B matches baseline → rule is Category D, removable.

### Decision flowchart for each rule

For each of the ~25 rules, apply this sequence:

```
1. Does the rule constrain INPUT data (encoding, format, deduplication)?
   → YES → Category C: Move to pre-processing code
   → NO → Continue

2. Can the rule be checked deterministically on OUTPUT 
   (regex, schema validation, counting, set operations)?
   → NO → Category A: Must stay in prompt
   → YES → Continue

3. Does an existing rule already express this constraint, 
   or is it implicit in the task description?
   → YES → Category D candidate: A/B test removal
   → NO → Continue

4. Run dual-purpose test (Experiment A vs baseline):
   Quality preserved? 
   → YES → Category B: Move to validator, keep one-line 
           reminder in prompt
   → NO → Reclassify as Category A: Must stay in prompt
```

### Expected distribution for a 25-rule text-grouping prompt

Based on the literature and the nature of scholarly text grouping:

- **8–12 rules → Category A**: Core grouping logic, pedagogical sequencing, Arabic-specific semantic rules, domain expertise directives
- **6–8 rules → Category B**: Format constraints, count bounds, ID uniqueness, completeness checks — keep one-line versions in prompt, add validators
- **3–5 rules → Category C**: Input validation, data cleaning, batch constraints — move entirely to pre-processing
- **2–4 rules → Category D**: Redundant restatements, implicit defaults — remove after A/B validation

This distribution alone could reduce the prompt from 25 rules (~1,474 words) to 14–20 rules, with the remaining rules further compressed via instruction distillation.

---

## Layer 4: Architectural changes that shrink GROUP without losing coherence

### System prompt separation delivers the largest single reduction

The most impactful architectural change is extracting shared content into a **persistent system prompt** that serves all three pipeline phases. Role definition, Arabic text handling rules, output format conventions, and domain context ("you are processing scholarly Arabic text into teaching units") are common across CLASSIFY, GROUP, and ENRICH. Extracting **250–350 words** into the system prompt immediately reduces the GROUP user prompt to ~1,125–1,225 words — nearly reaching the target with no behavioral changes.

OpenAI automatically caches system prompts ≥1,024 tokens, reducing input costs by **50%** and latency by up to **80%** for cache hits. Since the pipeline processes many segments sequentially (CLASSIFY → GROUP → ENRICH, repeated per batch), the shared prefix is computed once and reused across all subsequent calls. The marginal cost of the shared preamble approaches zero.

**Anthropic's context engineering guidance** reinforces this pattern: "System prompts should be the model's constitution — stable, persistent behavioral scaffolding." PromptHub's production analysis found that separating role/behavior into system prompts and task-specifics into user prompts reduces "ambiguity and conflicting instructions" while making iteration easier.

### Few-shot examples are likely the biggest space consumer

If the GROUP prompt contains 2–3 detailed Arabic text examples showing correct grouping, those examples likely consume **400–600 words** — nearly 40% of the total. Reducing from 3 examples to 1 focused, representative example could save 200–400 words. The key is choosing an example that covers the most common case and the most important edge case simultaneously, rather than having separate examples for each.

For Arabic specifically, examples are disproportionately token-expensive due to the 2–3x tokenization overhead. A 100-word Arabic example consumes 200–300 tokens. Moving examples to a dynamic retrieval system (selecting the most relevant example based on input characteristics) is architecturally elegant but adds pipeline complexity that may not be justified for a 3-phase system.

### Progressive disclosure keeps edge-case handling without bloating the base prompt

The GROUP prompt's 1,474 words likely include detailed handling for edge cases — single-segment units, overlapping themes, mixed-dialect passages, exceptionally long segments. Progressive disclosure (loading edge-case rules only when the input triggers them) can keep the base prompt compact while preserving coverage.

The Claude Skills Architecture demonstrates this at scale: a three-tier loading system (Discovery → Activation → Execution) achieved **100% token efficiency** vs. 0.8% for monolithic approaches. For the GROUP prompt, a simpler version suffices: pre-analyze the input batch for edge-case indicators, and append relevant edge-case rules only when needed. This could reduce the base prompt by another 50–100 words.

### Cross-phase context requires careful isolation

The Cross-Context Verification study (2603.21454) found that when prior conclusions are visible to later stages, **sycophancy and anchoring eliminate any verification benefit**. For the CLASSIFY → GROUP pipeline, this means: pass only CLASSIFY's output labels to GROUP, **not** CLASSIFY's reasoning or confidence scores. If GROUP sees that CLASSIFY was uncertain about a segment's classification, it may anchor on that uncertainty rather than independently evaluating grouping coherence.

---

## The refactoring recipe: 1,474 words to 800–1,000 in seven steps

This procedure is designed for an engineer who has not read the research above. Each step includes the technique, expected word savings, and a pass/fail gate.

### Step 1 — Extract shared preamble into system prompt

**What to do**: Read through the GROUP prompt and highlight every sentence that would also apply to CLASSIFY or ENRICH. This includes role definitions ("You are an expert in Arabic scholarly texts…"), Arabic handling rules ("Preserve diacritical marks…"), output conventions ("Respond in valid JSON…"), and domain definitions ("A teaching unit is…"). Move all highlighted content to a system prompt that will be shared across all three pipeline phases.

**Expected savings**: 250–350 words from the GROUP user prompt.

**Pass/fail gate**: Run the full test suite with the system prompt + reduced GROUP user prompt. All outputs must match baseline quality within statistical noise (≤2% deviation on any metric across 3 repetitions of ≥50 test inputs). If any regression, move content back and try a smaller extraction.

### Step 2 — Categorize each remaining rule using the triage flowchart

**What to do**: List every remaining rule in the GROUP prompt. For each, apply the decision flowchart from Layer 3. Physically label each rule A, B, C, or D. For Category B rules (deterministically checkable), write the corresponding validator function in code. For Category C rules (input constraints), write the corresponding pre-processing check. For Category D candidates, flag for removal testing in Step 5.

**Expected savings**: Category C rules (3–5 rules, ~75–150 words) are removed from the prompt and implemented in code. Category B rules (~6–8 rules) are replaced with one-line summaries, saving ~50–100 words.

**Pass/fail gate**: Pre-processing and post-processing validators must pass on 100% of current production outputs (no false positives on known-good outputs). If a validator flags a known-good output, the rule definition is wrong — fix the validator, not the prompt.

### Step 3 — Distill remaining Category A rules

**What to do**: For each Category A rule (must stay in prompt), rewrite it in the most concise imperative form possible. Remove filler phrases ("It is important to note that…"), convert passive voice to active, eliminate redundant qualifiers. Preserve all conditional logic, specific thresholds, and domain-specific terms. Each rule should ideally be 1–2 sentences.

**Expected savings**: 15–25% reduction in Category A rule text (~100–200 words).

**Pass/fail gate**: For each rewritten rule, run 10 test inputs that specifically exercise that rule. Compare outputs against baseline. If any behavioral change is detected, restore the original wording for that rule and try a less aggressive rewrite.

### Step 4 — Merge related rules (with extreme caution)

**What to do**: Among the remaining Category A rules, identify clusters of 2–3 rules that address the same behavioral dimension (e.g., multiple rules about thematic coherence, multiple rules about unit size). Attempt to merge each cluster into a single rule that captures all sub-rules. **Do not merge rules that were added during different hardening sessions** — they likely address distinct edge cases that are not obviously related.

**Expected savings**: 50–100 words from merging 2–3 clusters.

**Pass/fail gate**: For each merged rule, run the full test suite. Pay special attention to the edge cases that motivated the original sub-rules. If any previously-passing edge case now fails, revert the merge and keep the rules separate. This is the step most likely to introduce regressions.

### Step 5 — Test Category D removals

**What to do**: For each Category D candidate (flagged as potentially redundant or implicit), remove it from the prompt and run the full test suite. Test one removal at a time, not in batches — removals can interact.

**Expected savings**: 30–80 words per successful removal.

**Pass/fail gate**: Zero quality degradation on 3 repetitions of the full test suite. Because non-determinism can mask regressions, use statistical tests (Mann-Whitney U on quality scores) with p < 0.05 threshold. If in doubt, keep the rule.

### Step 6 — Compress or remove examples

**What to do**: If the prompt contains multi-line examples, reduce to the single most representative example. Choose an example that demonstrates the most common case while including at least one edge-case element. If the example is in Arabic, consider whether a shorter excerpt would suffice. If the prompt has no examples, skip this step.

**Expected savings**: 200–400 words if the prompt contained 2–3 detailed examples.

**Pass/fail gate**: Same as Step 1 — full test suite, ≤2% deviation.

### Step 7 — Reorder surviving rules for positional attention

**What to do**: Place the most critical behavioral rules (the ones that, if violated, produce the worst outputs) at the **beginning** and **end** of the prompt. Place less critical rules in the middle. This exploits the U-shaped attention curve documented in "Lost in the Middle."

**Expected savings**: Zero words saved — this is a quality optimization, not a compression step.

**Pass/fail gate**: Run full test suite. Expect 0–5% quality improvement on the rules moved to primacy/recency positions. No regression should occur on middle-positioned rules since they were already in the attention dead zone.

### Cumulative expected compression

| Step | Technique | Words saved | Running total |
|------|-----------|-------------|---------------|
| 1 | System prompt extraction | 250–350 | ~1,125–1,225 |
| 2 | Category B/C triage | 125–250 | ~900–1,075 |
| 3 | Instruction distillation | 100–200 | ~750–925 |
| 4 | Rule merging | 50–100 | ~700–850 |
| 5 | Category D removal | 30–80 | ~670–820 |
| 6 | Example compression | 200–400 | ~470–620 |
| 7 | Reordering | 0 | ~470–620 |

Steps 1–5 alone likely reach the 800–1,000 word target. Step 6 provides additional margin if the prompt contains substantial examples. If compression overshoots the target (prompt becomes too short), add back the most impactful rules from Step 5 or restore fuller examples from Step 6.

### The regression test suite

Build this before starting Step 1:

- **≥50 diverse Arabic text inputs** covering: short segments, long segments, single-segment edge cases, thematically similar segments (hardest grouping task), mixed-dialect passages, segments with diacritical marks, segments referencing shared Quranic sources
- **Golden outputs**: Expert-validated correct groupings for each input
- **Automated metrics**: JSON schema compliance (100% required), segment count per unit (within bounds), no duplicate assignments, all segments assigned, LLM-as-judge thematic coherence score (1–5 scale)
- **Human evaluation**: 2+ Arabic-literate evaluators scoring 20+ outputs on thematic coherence, pedagogical progression, and granularity appropriateness, with inter-rater reliability (Cohen's κ ≥ 0.7)
- **Run protocol**: Every prompt change triggers 3 repetitions of the full suite at temperature=0. Statistical significance testing (Mann-Whitney U, p < 0.05) on quality scores before accepting any change

---

## Conclusion

The empirical evidence converges on a counterintuitive conclusion: the 1,474-word GROUP prompt is too long to reliably govern 25 behavioral rules. The exponential compliance decay (P ≈ p^N), the U-shaped attention curve, the fixed instruction budget, and the context rot phenomenon all predict that compression will improve behavioral fidelity rather than degrade it. The key insight is that **not all compression techniques are equal for behavioral prompts** — LLMLingua and few-shot condensation are empirically counterproductive, while instruction distillation and system prompt extraction are safe and effective. The triage framework's most important finding is the dual-purpose problem: deterministically checkable rules often simultaneously shape model reasoning, so the safe pattern is to keep a one-line version in the prompt while adding a code-based validator. The seven-step recipe provides a conservative, gate-checked path to 800–1,000 words — each step produces a testable intermediate prompt, and any step can be reverted independently if regressions appear. The overarching principle: prompt engineering for behavioral fidelity is an exercise in signal density, not information completeness.