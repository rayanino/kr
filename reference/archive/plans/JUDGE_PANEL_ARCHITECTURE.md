# Judge Panel Architecture — هيئة التحكيم

> **NOTE:** This document contains theoretical architecture based on research. The actual
> evaluation approach will be determined by the validation experiments in POST_PREP_PLAN.md.
> Do not implement this as-is — test assumptions first.


## Why a Panel, Not a Single Judge

Research (ICLR 2025, LLM-as-Judge survey, Multi-LLM Evaluator Framework) shows:

1. A single LLM judge has systematic biases: length bias (prefers longer output), self-model bias (prefers output similar to its own style), position bias
2. An ensemble of 3-5 diverse models outperforms any single strong model — even when the individual models are weaker
3. Role-specialized judges (each checking one dimension) outperform generalist judges (checking everything at once)
4. Cascaded evaluation (cheap checks first, expensive judges only for uncertain cases) cuts cost by 60-80% while maintaining reliability
5. Self-model bias: if the pipeline uses Claude for excerpting, Claude alone should NOT judge excerpt quality

For KR specifically: the pipeline uses LLMs for excerpting, taxonomy, and synthesis. If the SAME model judges its own output, it will be systematically biased toward approving it. The judge panel MUST include models from different families.

---

## The Judge Panel (via OpenRouter)

OpenRouter provides access to all major model families through one API key. The judge panel uses models from AT LEAST 3 different families:

### Panel Composition

```
TIER 1 — DETERMINISTIC CHECKS (free, instant, no API calls)
  - Text fidelity: byte-level comparison of Arabic text before/after each engine
  - Schema compliance: Pydantic model validation on every output
  - Metadata preservation: D-023 check — all upstream fields present
  - Isnad integrity: regex pattern check for split narrator chains
  - Diacritics preservation: character-level tashkeel comparison
  - Field completeness: no required field is None/empty
  
  Cost: $0. Catches: ~40% of all defects.

TIER 2 — FAST LLM JUDGE (cheap, handles 80% of remaining checks)
  Model: DeepSeek-V3 or Qwen3-235B via OpenRouter (~$0.50/M tokens)
  Role: First-pass scholarly evaluation. Structured prompts, parseable output.
  
  Checks: author identification, genre classification, death dates, 
          science scope, basic self-containment, obvious misplacements.
  
  Output: CORRECT / WRONG / UNCERTAIN for each check.
  
  Items marked CORRECT → accepted (no further review).
  Items marked WRONG → logged as findings (high confidence).
  Items marked UNCERTAIN → escalated to Tier 3.
  
  Cost: ~$0.02 per source. Catches: ~45% of all defects.

TIER 3 — EXPERT PANEL (expensive, only for uncertain/critical items)
  Three models from different families, each with a specialized role:
  
  Judge A — ATTRIBUTION SPECIALIST (Claude Sonnet via OpenRouter)
    Role: Verify scholarly attributions, school classifications, 
          teacher-student relationships, biographical accuracy.
    Why Claude: Best Arabic training data, strongest on Islamic studies facts.
    
  Judge B — COHERENCE SPECIALIST (GPT-4.1 via OpenRouter)  
    Role: Evaluate self-containment, argument completeness, 
          whether an excerpt makes sense standalone.
    Why GPT: Different training data = different biases. Cross-validates Claude.
    
  Judge C — ADVERSARIAL CRITIC (Gemini 2.5 Pro via OpenRouter)
    Role: Actively try to find errors the other judges missed.
          Look for: subtle misattributions, misleading implications,
          taxonomy placements that are close-but-wrong.
    Why Gemini: Third model family, different failure modes.
  
  CONSENSUS: All three judges must agree for CORRECT. 
             2/3 agreement → LIKELY_CORRECT (logged for spot-check).
             Any disagreement where one says WRONG → finding logged.
             All three UNCERTAIN → escalated to owner.
  
  Cost: ~$0.10 per escalated item. Only 15% of items escalate.
```

### Cost Model

For 500 sources, assuming each source produces ~150 excerpts + 1 entry:

```
Tier 1 (deterministic):
  500 sources × free = $0

Tier 2 (fast LLM):
  500 sources × ~3000 tokens per source = 1.5M tokens
  At $0.50/M = $0.75 total

Tier 3 (expert panel):
  ~15% of 500×150 = 11,250 items escalated
  × 3 judges × ~1000 tokens each = 33.75M tokens
  At ~$5/M average = $168.75

Total evaluation cost for 500 sources: ~$170
```

This is trivially affordable. Even 5,000 sources would cost ~$1,700.

---

## Rubric Architecture

Each engine has specialized rubrics. A rubric is NOT a generic prompt — it's a structured evaluation protocol with defined correct answers, severity levels, and escalation rules.

### Source Engine Rubrics

```python
SOURCE_RUBRICS = {
    "SRC-AUTHOR": {
        "tier": 2,  # Fast LLM first pass
        "escalate_on": "UNCERTAIN",
        "prompt": """
Source: {title}
Pipeline identified author as: {author_name_ar} (death: {death_date} AH)

Verify: Is this the correct author of this specific work?
Output EXACTLY one of:
- CORRECT
- WRONG|{correct_author}|{correct_death_date}
- UNCERTAIN|{reason}
""",
        "severity": "CRITICAL",  # Wrong author = knowledge corruption
    },
    
    "SRC-GENRE": {
        "tier": 2,
        "escalate_on": "UNCERTAIN",
        "prompt": """
Work: {title} by {author}
Pipeline classified genre as: {genre}
Pipeline detected genre chain: {genre_chain}

Is this genre classification correct? 
If it's a sharh, is the base work correctly identified?
Output EXACTLY one of:
- CORRECT
- WRONG|{correct_genre}|{correct_base_work}
- UNCERTAIN|{reason}
""",
        "severity": "HIGH",
    },
    
    "SRC-TRUST": {
        "tier": 2,
        "prompt": """
Work: {title}, tahqiq: {muhaqiq}
Pipeline trust score: {trust_score} ({trust_tier})
Factors: {trust_factors}

Is this trust assessment reasonable? Would a senior scholar 
approximately agree with this reliability assessment?
Output EXACTLY one of:
- REASONABLE
- TOO_HIGH|{reason}
- TOO_LOW|{reason}
- UNCERTAIN|{reason}
""",
        "severity": "MEDIUM",
    },
}
```

### Excerpting Engine Rubrics (MOST CRITICAL)

```python
EXCERPT_RUBRICS = {
    "EXC-SELF-CONTAIN": {
        "tier": 2,  # Fast LLM handles most
        "escalate_on": "UNCERTAIN",
        "prompt": """
Read this excerpt from an Arabic scholarly text:

«{excerpt_text_ar}»

Without reading anything before or after this excerpt:
1. Can you identify the TOPIC being discussed?
2. Can you identify WHO holds the opinion stated?
3. Does the excerpt make a complete point, or does it start/end mid-argument?

Output EXACTLY one of:
- PASS (topic clear, attribution clear, complete point)
- FAIL|{specific_reason_in_english}
- BORDERLINE|{what_is_missing}
""",
        "severity": "HIGH",
    },
    
    "EXC-ATTRIBUTION": {
        "tier": 3,  # Always goes to expert panel (highest corruption risk)
        "prompt": """
This excerpt attributes the following scholarly position:

Scholar: {attributed_scholar} ({school} school, d. {death_date} AH)
Position: «{position_text_ar}»
Source work: {source_title} by {source_author}

Based on your knowledge of Islamic jurisprudence and scholarship:
1. Is this a known position of this scholar or school?
2. Could this be a misattribution (e.g., a student's opinion attributed to the teacher)?
3. Is the school classification correct?

Output EXACTLY one of:
- CORRECT (verified attribution)
- WRONG|{correct_scholar_or_school}|{evidence}
- PLAUSIBLE_BUT_UNVERIFIED (scholar is obscure or position is rare)
- MISATTRIBUTED|{actual_attribution}|{evidence}
""",
        "severity": "CRITICAL",
    },
    
    "EXC-ISNAD": {
        "tier": 1,  # Deterministic check first
        "check": "If excerpt contains حدثنا/أخبرنا/عن, verify the isnad chain is complete within the excerpt",
        "pattern": r"(حدثنا|أخبرنا|عن)\s+\S+.*?(قال|أن)",
        "escalate_on": "pattern_incomplete",
        "severity": "CRITICAL",
    },
}
```

### Synthesis Engine Rubrics (FINAL PRODUCT)

```python
SYNTHESIS_RUBRICS = {
    "SYN-GROUNDING": {
        "tier": 1,  # Deterministic
        "check": "Every claim in the entry cites a source excerpt. No uncited claims.",
        "severity": "CRITICAL",
    },
    
    "SYN-SCHOLARLY-QUALITY": {
        "tier": 3,  # Always expert panel (this is the product)
        "prompt": """
Read this synthesized entry from an Islamic scholarly knowledge base:

«{entry_text_ar}»

Topic: {taxonomy_leaf}
Sources used: {source_list}

Evaluate as if you are a senior Islamic studies professor reviewing 
a student's research summary. Rate each dimension:

1. ACCURACY: Are the scholarly positions correctly stated?
   Score: 1-5 (5 = perfectly accurate)
   
2. ATTRIBUTION: Is every opinion correctly attributed to its scholar/school?
   Score: 1-5 (5 = every attribution verifiable)

3. COMPLETENESS: Does the entry cover the major scholarly positions on this topic?
   Score: 1-5 (5 = comprehensive, 1 = missing major positions)

4. CLARITY: Would a student understand this entry?
   Score: 1-5 (5 = crystal clear, 1 = confusing)

5. SCHOLARLY_TONE: Does this read like scholarly text, not a chatbot summary?
   Score: 1-5 (5 = reads like published scholarship)

Output as JSON:
{
  "accuracy": N, "accuracy_note": "...",
  "attribution": N, "attribution_note": "...",
  "completeness": N, "completeness_note": "...",
  "clarity": N, "clarity_note": "...",
  "tone": N, "tone_note": "...",
  "overall_pass": true/false,
  "critical_errors": ["...", "..."]
}

An entry PASSES if all scores ≥3 AND no critical errors.
""",
        "severity": "CRITICAL",
    },
}
```

---

## The Oracle Pattern (from the C Compiler)

The C compiler project used GCC as a "known-good oracle" — a reference implementation to compare against. KR needs its own oracle.

**For engines 1-4 (deterministic):** The oracle is the input itself. Text fidelity checks compare output against the frozen source byte-by-byte.

**For engines 5-7 (LLM-dependent):** No oracle exists — KR is building something new. But we CAN create partial oracles:

1. **Gold sources**: 10 carefully selected books where YOU (the owner) hand-verify the correct excerpts, attributions, and taxonomy placements. These become the ground truth that the judge panel is calibrated against.

2. **Cross-source consistency oracle**: The same scholar (e.g., ابن قدامة) should have the same canonical_id, death date, school, and teacher-student relationships across ALL sources that mention him. Inconsistency = bug.

3. **Self-consistency oracle**: Run the same source 3 times. The LLM engines produce different text, but the FACTS should be consistent. If run 1 says "Hanbali" and run 2 says "Shafi'i" for the same excerpt, that's a reliability failure.

4. **Inverse oracle**: If the synthesis engine produces an entry claiming "the Hanafi position is X", the judge panel asks: "Is there an excerpt from a Hanafi source that actually states X?" If not, the claim is ungrounded — a hallucination.

---

## Autonomous Fix Loop (from the C Compiler)

The C compiler used an infinite loop:
```bash
while true; do
    claude --dangerously-skip-permissions -p "$(cat AGENT_PROMPT.md)"
done
```

KR's version, adapted for pipeline testing:

```bash
#!/bin/bash
# test_harness/autonomous_loop.sh
# Run in a Docker container. Runs indefinitely until stopped.

AGENT_PROMPT="test_harness/AGENT_PROMPT.md"

while true; do
    # 1. Pull latest code
    git pull
    
    # 2. Find next untested source (or source with open CRITICAL findings)
    NEXT_SOURCE=$(python3 test_harness/pick_next_source.py)
    
    if [ -z "$NEXT_SOURCE" ]; then
        echo "All sources tested, no open CRITICALs. Sleeping 1h."
        sleep 3600
        continue
    fi
    
    # 3. Run the agent
    claude --dangerously-skip-permissions \
           -p "$(cat $AGENT_PROMPT) 

Current source to process: $NEXT_SOURCE
Read test_corpus/findings/OPEN.md for any open findings on this source.
If there are CRITICAL findings, fix the engine code first, then re-run.
If no findings, run the pipeline and evaluation on this source.
After evaluation, commit results and move to next source." \
           --max-turns 100 \
           2>&1 | tee "test_corpus/logs/agent_$(date +%Y%m%d_%H%M%S).log"
    
    # 4. Push results
    git add -A && git commit -m "Test: $NEXT_SOURCE" && git push
done
```

The AGENT_PROMPT.md tells Claude Code:
- How to run the pipeline
- How to run the judge panel evaluations  
- How to read and write findings
- How to fix code when findings are CRITICAL
- How to run regression tests after fixing
- How to commit and report

### Parallel Agents (for scale)

For 500+ sources, run multiple agents in parallel Docker containers:

```bash
# Each agent works on different sources (locked via git file)
for i in $(seq 1 4); do
    docker run -d \
        -v $(pwd):/upstream \
        -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
        kr-test-agent agent_$i &
done
```

Git-based locking prevents double-work (same pattern as the C compiler):
- Agent claims a source by writing `test_corpus/locks/ibn_aqil.lock`
- Other agents skip locked sources
- After completion, lock is removed and results pushed

---

## Calibration: How Do We Know the Judges Are Right?

The judge panel itself needs validation. This is the meta-evaluation problem.

### Phase 0: Gold Calibration Set (BEFORE large-scale testing)

1. Select 5 diverse sources (sharh, matn, fiqh, hadith, nahw)
2. Run the pipeline on each
3. YOU (the owner) hand-verify every excerpt, attribution, and placement
4. These 5 sources become the gold standard
5. Run the judge panel on the same 5 sources
6. Compare: does the judge panel agree with your assessments?
7. Calibrate: adjust rubric prompts until judge panel accuracy ≥95% against gold

This calibration step is CRITICAL. Without it, the judge panel might be confidently wrong.

### Ongoing Calibration: Random Owner Spot-Checks

After the gold calibration, the system periodically flags random items for owner review:
- 1 random excerpt per 10 sources → owner verifies
- 1 random entry per 20 sources → owner reads
- If owner disagrees with judge panel → recalibrate rubric

The owner's time commitment: ~15 minutes per 10 sources processed. For 500 sources: ~12.5 hours total, spread over weeks.

---

## Summary: The Complete Testing Machine

```
LAYER 1: DETERMINISTIC CHECKS
  Cost: $0
  Catches: text corruption, schema violations, metadata loss, isnad splits
  Coverage: 100% of output, every run

LAYER 2: FAST LLM JUDGE  
  Cost: $0.75 for 500 sources
  Catches: wrong author, wrong genre, obvious misplacements
  Coverage: 100% of output, every run

LAYER 3: EXPERT PANEL (3 models, 3 families)
  Cost: ~$170 for 500 sources  
  Catches: subtle misattributions, self-containment failures, scholarly quality
  Coverage: ~15% of output (uncertain items from Layer 2) + all synthesis entries

LAYER 4: GOLD CALIBRATION
  Cost: owner time (~12.5 hours for 500 sources)
  Catches: everything the automated layers miss
  Coverage: ~5% random sample + 5 fully-verified gold sources

AUTONOMOUS LOOP:
  Claude Code runs pipeline + evaluation + fix cycle continuously
  Parallel agents for scale (4 agents = 4x throughput)
  Git-based locking prevents double-work
  Owner reviews NEEDS_OWNER.md weekly (~15 min per 10 sources)

TRUST GRADUATION:
  Level 0: Pipeline runs without crashing
  Level 1: Tier 1 checks pass on 50 sources
  Level 2: Tier 2 judge >90% CORRECT on 50 sources  
  Level 3: Tier 3 panel >95% consensus on 50 sources
  Level 4: Gold calibration: judge panel agrees with owner on 5 gold sources
  Level 5: 500 sources processed, 0 open CRITICALs
  Level 6: Owner reads 50 entries, approves all
  → PIPELINE TRUSTED
```
