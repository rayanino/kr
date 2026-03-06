# Research Log — Post-Preparatory Phase Design

Started: 2026-03-06
Purpose: Deep research before committing to any testing/building architecture

---

## FINDING 01: The C Compiler Case Study (Anthropic Engineering Blog)
Source: https://www.anthropic.com/engineering/building-c-compiler
Date: Feb 5, 2026

Key facts:
- 16 parallel Claude agents, ~2000 sessions, $20K, 2 billion input tokens
- Produced 100K-line Rust-based C compiler that compiles Linux 6.9
- Used bare-bones parallel setup: Docker containers, git-based locking
- NO orchestration agent — each agent decides what to do next
- Infinite loop: `while true; do claude -p "$(cat AGENT_PROMPT.md)"; done`

Critical lessons (direct quotes paraphrased):
- "Most of my effort went into designing the environment around Claude — 
  the tests, the environment, the feedback — so that it could orient 
  itself without me"
- Test verifier must be "nearly perfect" — Claude optimizes for whatever 
  the test measures, even if that's the wrong thing
- Context window pollution: test output should be minimal, log details 
  to files. Pre-compute summary statistics.
- Time blindness: Claude can't tell time, will spend hours on tests 
  without making progress. Use --fast mode (1-10% sample).
- Parallelism works when tasks are independent. Breaks down when tasks 
  are coupled (e.g., compiling one giant binary). Fix: use an oracle 
  (GCC) to isolate which files have bugs.
- Agent roles: specialized agents for code quality, performance, 
  documentation, design critique — not just "fix bugs"

Implications for KR:
- The test environment IS the product, not the pipeline code
- Simple loop + good tests > complex orchestration
- Need an oracle for evaluation (what's "correct" output?)
- Pre-compute metrics so Claude doesn't waste context reading raw output
- Specialized roles: builder agent, evaluator agent, regression agent

---

## FINDING 02: LLM-as-Judge Research (Multiple Papers)

### 2a: Multi-LLM Evaluator Framework (EmergentMind survey)
Source: https://www.emergentmind.com/topics/multi-llm-evaluator-framework

Key findings:
- Role-specialized judges outperform generalist judges
  (e.g., RADAR: Security Auditor, Vulnerability Detector, Critic, Arbiter)
- Evaluator ensembles (AIME): concatenating independent LLM evaluations 
  each focused on separate criteria increases error detection significantly
- Meta-judge pipelines: multiple agents score along weighted rubric, 
  then consensus aggregation
- "Superior alignment with human judgment" compared to single-LLM baselines
- 62% higher error detection rate, 28.87% greater risk identification
- 8-15 point improvements in precision over single evaluators

### 2b: Trust or Escalate (ICLR 2025)
Source: https://proceedings.iclr.cc/paper_files/paper/2025/...

Key findings:
- Cascaded framework: cheap model first, expensive model only for 
  uncertain cases — reduces cost while maintaining reliability
- Risk of disagreement can be bounded mathematically
- "Simulated annotators" method for confidence estimation
- Key insight: you can guarantee maximum disagreement rate with humans

### 2c: LLM-as-Judge Survey (arxiv 2411.15594)
Key biases found:
- Position bias (order of options matters)
- Verbosity bias (longer = perceived as better)
- Self-model bias (models prefer output similar to their own style)
- Single LLM judges "struggle in highly specialized domains"

### 2d: Agent-as-a-Judge
Source: https://arxiv.org/html/2508.02994v1

Key finding:
- Agent judge (that can execute code, check facts) disagreed with 
  human majority vote only 0.3% of the time
- Single LLM judge disagreed 31% of the time
- Agent judge EXCEEDED individual human evaluator consistency
- "An AI agent, by virtue of tirelessly analyzing step-by-step details, 
  can nearly replace human evaluators for certain complex process-oriented tasks"

Implications for KR:
- Multi-model evaluation is strongly supported by evidence
- Self-model bias is critical: don't judge Claude output with Claude alone
- Cascaded evaluation (cheap → expensive) is proven cost-effective
- Agent-as-judge (can run code, verify) >> static LLM judge
- Role specialization matters: attribution checker ≠ coherence checker

---

## FINDING 03: Islamic Content Evaluation by LLMs

### 3a: "Can LLMs Write Faithfully?" (2025)
Source: https://arxiv.org/html/2510.24438

Key findings:
- Tested GPT-4o, Ansari AI, Fanar on 50 Islamic content prompts
- GPT-4o scored 3.90/5, Ansari 3.79/5, Fanar 3.04/5
- "Current LLMs fall short on faith-sensitive rigor and citation integrity"
- Recommends: heterogeneous ensemble of evaluator LLMs (Claude, Gemini, Llama)
- Recommends: Arabic-first evaluations with native-speaking scholars
- Recommends: 3-5 Islamic scholar panels for validation
- "AI should supplement scholars, not replace their judgment"

### 3b: IslamicLegalBench (Feb 2026)
Source: https://arxiv.org/html/2602.21226

Key findings:
- Tested 7+ models on Islamic inheritance law across 1200 years of traditions
- o3 and Gemini 2.5 scored >90% accuracy
- ALLaM, Fanar, LLaMA, Mistral scored <50%
- "Models fail systematically when Islamic jurisprudence demands exact, 
  condition-specific knowledge from classical fiqh texts"
- Extraction tasks: 76-98% correctness (strong)
- Principle-based reasoning: 70-88% (decent)
- Precise enumeration and statute synthesis: consistent DROP (weak)
- Hallucination rates vary significantly by model and task complexity

### 3c: Islamic Legal Reasoning Benchmark (ArabicNLP 2025)
Source: https://arxiv.org/html/2509.01081v1

Key findings:
- Inheritance share calculation: Gemini 2.5 (90.6%), o3 (93.4%)
- GPT-4.5 at 74% (no reasoning capability)
- Jais, Mistral, LLaMA below 50%
- Clear gap between models WITH reasoning and WITHOUT
- "Models without reasoning capability consistently struggled with 
  identifying complex familial relationships"
- Majority voting across 3 models (Gemini Flash 2.5, Gemini Pro 2.5, 
  GPT o3) achieved 92.7% — BEST result, third place in competition

### 3d: Domain-Specific LLMs for Islamic Worldview
Source: https://arxiv.org/html/2312.06652v1

Key findings:
- RAG is "the most promising approach" for accurate Islamic content
- Challenge: "different schools of theology and jurisprudence have emerged"
- Fine-tuning GPT-3.5 on hadith/Islamic QA data showed NO significant 
  improvement over base model — surprising
- Evaluation at scale is "crucial" but methodology is underdeveloped
- IslamQA dataset can serve as evaluation baseline

### 3e: Islamic Law Blog Roundtable (March 2025)
Source: https://islamiclaw.blog/2025/03/13/roundtable-...

Key insight:
- "A database excels at precisely storing and retrieving information... 
  The hadith scholar's training prioritizes maintaining fidelity in 
  transmitting information"
- "LLMs don't just count words — they encode the semantic relationships 
  between concepts based on their usage contexts"
- KR is doing BOTH: precise storage (pipeline) + semantic understanding 
  (synthesis). The pipeline must maintain hadith-scholar-level fidelity; 
  the synthesis must add LLM-level understanding.
- Shamela comparison: "researchers can instantly locate every instance 
  of a word or phrase across thousands of texts, the database can only 
  find exact matches — missing conceptually related discussions"

Implications for KR:
- Model selection for judges CRITICALLY matters — 50% vs 93% accuracy range
- Models with reasoning capability (o3, Gemini 2.5) dramatically outperform
- Majority voting across 3 strong models was THE best approach (92.7%)
- LLMs are good at broad principles, BAD at precise condition-specific knowledge
- This means: excerpt extraction (broad) is safer than synthesis (precise)
- The synthesis engine is the highest-risk component
- RAG approach (which KR essentially is) is the recommended architecture
- Arabic-first evaluation is non-negotiable

---

## FINDING 04: Arabic Text & Diacritics

### 4a: Tashkeela Corpus
- 75 million fully vocalized words from 97 books
- Classical and modern Arabic
- Freely available
- Used as training/evaluation data for diacritization systems

### 4b: QARI-OCR (June 2025)
Source: https://arxiv.org/html/2506.02295v1
- State-of-the-art Arabic OCR: WER 0.160, CER 0.061
- Based on Qwen2-VL-2B-Instruct
- Superior handling of tashkeel, diverse fonts, document layouts
- Works on low-resolution images
- Open source on HuggingFace: riotu-lab/QARI-OCR

### 4c: Diacritics matter for meaning
- عَلِمَ (alima — he knew) vs عُلِمَ (ulima — it was known)
- Single diacritic changes meaning completely
- Classical texts like Quran require precise diacritization
- Pipeline MUST preserve diacritics or risk knowledge corruption

### 4d: Arabic tokenization cost
- Arabic tokenizes 2-3x more than English for same semantic content
- Morphologically rich: one Arabic word can encode subject, verb, object
- This affects cost estimates for evaluation significantly
- Need actual measurement before committing to cost projections

### 4e: Evaluating Arabic LLMs Survey (Oct 2025)
Source: https://arxiv.org/html/2510.13430v1
- 40+ Arabic LLM benchmarks reviewed
- Key challenge: "critical cultural sensitivity requirements that 
  undermine translation-based approaches"
- Data scarcity despite 500 million speakers
- Three benchmark approaches: translation, synthetic generation, native collection
- Translation benchmarks are "culturally misaligned"
- Native Arabic models: Jais, ArabianGPT, AraGPT (Arabic-only)
- Adapted models: AceGPT, SILMA, Fanar, Falcon-Arabic (fine-tuned multilingual)
- Multilingual: Qwen3, Gemma3, Llama, Claude, GPT (general multilingual)

Implications for KR:
- Arabic text handling is a solved problem for OCR (QARI-OCR 0.061 CER)
- Diacritics preservation is non-negotiable — it's a fidelity check
- Cost estimates need real measurement (Arabic tokens ≠ English tokens)
- Evaluation must be Arabic-first, not translated
- Cultural sensitivity in evaluation prompts matters

---

## FINDING 05: Claude Code Autonomous Capabilities

### 5a: Non-interactive mode
Source: https://code.claude.com/docs/en/best-practices
- `claude -p "prompt"` runs without interaction
- `--output-format json` for parseable output  
- `--dangerously-skip-permissions` for unattended operation
- `--max-turns N` limits iterations
- Can pipe input: `cat file | claude -p "analyze"`

### 5b: Agent Teams (experimental)
Source: https://code.claude.com/docs/en/agent-teams
- Multiple Claude Code sessions coordinating via shared task list
- Team lead + teammates architecture
- Git-based coordination for file conflicts
- "Start with 3-5 teammates for most workflows"
- Experimental, disabled by default
- CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

### 5c: Batch processing
Source: SmartScope blog
- `/batch` command for codebase-wide migrations
- Headless mode (`claude -p`) for CI/CD integration
- Can combine both: batch changes + headless verification
- 60% of teams use non-interactive mode for automation

### 5d: Claude-Autopilot (VS Code extension)
Source: https://github.com/benbasha/Claude-Autopilot
- Queue hundreds of tasks, runs autonomously
- Auto-resume when usage limits reset
- Sleep prevention (keeps computer awake overnight)
- Error recovery with automatic retry
- Cross-platform (Windows, macOS, Linux)

Implications for KR:
- Autonomous overnight processing is proven and supported
- Non-interactive mode is the right interface for batch testing
- Agent teams for parallel investigation (experimental but functional)
- Claude-Autopilot could handle the "run 500 sources overnight" use case
- Rate limiting is a real concern for large batch runs

---

## FINDING 06: Paperclip (Agent Orchestration)
Source: https://github.com/paperclipai/paperclip

What it is:
- "Open-source orchestration for zero-human companies"
- Node.js server + React UI for managing AI agent teams
- Org charts, budgets, governance, goal alignment
- Supports Claude Code, Codex, Cursor, Bash, HTTP agents
- MIT licensed, self-hosted

Assessment for KR:
- OVERKILL for our use case. KR has one pipeline, one user.
- The orchestration overhead (PostgreSQL, Node.js server) doesn't justify 
  the benefit for a single-pipeline testing scenario.
- The C compiler approach (bash loop + git) is simpler and proven.
- HOWEVER: if KR testing scales to 20+ parallel agents, Paperclip's 
  task management and cost tracking would become valuable.
- Decision: start with bash scripts, evaluate Paperclip if we hit 
  coordination limits.

---

## FINDING 07: OpenITI / KITAB — The Existing Arabic Text Corpus

### 7a: OpenITI Corpus
Source: https://openiti.org/documentation/
Source: https://maximromanov.github.io/OpenITI/

What it is:
- Open-access machine-actionable corpus of premodern Arabic texts
- ~4,300 unique book titles, 1,800+ authors, 750M words (2B with all versions)
- Started at Tufts/Leipzig, now multi-institutional (Aga Khan, Maryland, Hamburg)
- Most texts collected from Shamela (shamela.ws) and Shia online library
- Organized by author death date in 25-year AH periods
- Uses CTS (Canonical Text Services) URN structure for permanent references
- Custom format: "OpenITI mARkdown" — simplified markdown for Arabic texts
- Files have quality stages: RAW → .inProgress → .completed → .mARkdown
- ALL on GitHub: https://github.com/openiti

Key organizational principle:
- Repository per 25-year period: `0525AH` = authors who died 501-525 AH
- Each author has a subfolder with all their works
- Each work may have multiple versions (editions)
- Human-readable URNs for easy subsetting

### 7b: KITAB Project
Source: https://kitab-project.org/

What it is:
- "Knowledge, Information Technology, and the Arabic Book"
- Uses the passim algorithm for text reuse detection across the entire corpus
- Splits texts into 300-word "milestones" for comparison
- Smith-Waterman alignment algorithm (same as genomics!)
- Produces pairwise text reuse statistics for ALL books in corpus
- Isnad detection using machine learning (where chains of transmission 
  begin and end in each text)
- Quranic quotation auto-tagging

Key methodological insights:
- "passim is powerful, but it cannot understand the content of texts,
  sometimes leading it to identify cases of similarity that do not 
  constitute meaningful reuse"
- Manual annotation of ground truth is essential for evaluating 
  algorithm performance
- They use human evaluation + algorithm comparison as standard practice
- "Reading text reuse alignments so closely can teach us a lot about 
  how authors copied, abridged and paraphrased their source texts"

Implications for KR:
- OpenITI has ALREADY done what KR's source engine does (collect/organize)
  but WITHOUT the intelligence layer (no excerpting, no synthesis, no entries)
- KR can potentially USE OpenITI texts as input — they're already Shamela-sourced
  and structured
- The 300-word milestone approach is similar to KR's passaging engine
- KITAB's text reuse data is exactly what KR's §4.B.1 (KITAB profiling) uses
- Their isnad detection work validates that ML can identify isnads — 
  KR's excerpting engine needs this same capability
- Ground truth annotation methodology is directly applicable to our 
  gold calibration approach

---

## FINDING 08: Agent Failure Modes

### 8a: Common failure patterns
Sources: Unite.AI "AI Agents Trap", Composio agent report, various

Known failure modes for autonomous agent loops:
1. **Infinite loops / stuck states**: Agent repeats same action without 
   progress. AutoGPT's original sin. Fix: max-turns limit, progress 
   detection, automatic restart.
   
2. **Oscillation**: Agent fixes bug A, which introduces bug B, then fixes 
   B which reintroduces A. The C compiler author saw this: "new features 
   and bugfixes frequently broke existing functionality." Fix: regression 
   tests that must ALL pass before committing.
   
3. **Context window saturation**: Long-running agents fill their context 
   with irrelevant history, degrading performance. The C compiler author: 
   "test harness should not print thousands of useless bytes." Fix: fresh 
   sessions per task, minimal output, log to files.
   
4. **Overconfident fixes**: Agent "fixes" something that wasn't broken, 
   breaking it. The Replit incident: agent deleted production DB despite 
   "code freeze" instruction. Fix: constrained permissions, sandbox mode.
   
5. **Wrong problem optimization**: Agent optimizes for the test metric 
   rather than the actual goal. "Claude will solve whatever problem I 
   give it, so the test verifier must be nearly perfect." Fix: high-quality 
   tests that measure what actually matters.
   
6. **Parallelism conflicts**: Multiple agents editing same files. The C 
   compiler used git-based file locking. Fix: clear file ownership, 
   git merge as coordination.

### 8b: Google DeepMind Scaling Paper (Dec 2025)
Source: "Towards a Science of Scaling Agent Systems" (via TDS article)

Key findings:
- "Coordination Tax": accuracy gains SATURATE or FLUCTUATE as you add 
  more agents beyond 4-5
- 3-5 agents is the sweet spot for most tasks
- Beyond 5 agents: diminishing returns, increasing coordination overhead
- Topology matters: Centralized (one lead + workers) outperforms 
  Decentralized for most tasks
- "Bag of agents" (just throwing more agents at a problem) has 17x 
  higher error rate than structured topology

Implications for KR:
- Don't use 16 parallel agents like the C compiler. Use 3-4.
- Centralized topology (one lead agent coordinating workers) is best
- Each agent session should be fresh (avoids context saturation)
- Regression tests are THE defense against oscillation
- Permission constraints prevent overconfident destructive fixes
- Max-turns limit prevents infinite loops

---

## FINDING 09: OpenRouter Pricing & Model Landscape (March 2026)

Source: Multiple pricing guides, OpenRouter docs

### Available models via OpenRouter (one API key):
- Claude Opus 4.6: $5/$25 per M tokens (1M context)
- Claude Sonnet 4.6: $3/$15 per M tokens (1M context)  
- Claude Haiku 4.5: $1/$5 per M tokens
- GPT-5: $1.25/$10 per M tokens
- GPT-4.1: cheaper than GPT-5, good for evaluation
- Gemini 3.1 Pro: $2/$12 per M tokens (1M context)
- Gemini 2.5 Flash: very cheap, good for fast checks
- DeepSeek V3.2: $0.14/$0.28 per M tokens (!!!)
- Llama 3.3 70B: FREE on some providers
- Gemma 3: FREE on some providers

### Cost implications for KR evaluation:
- Tier 2 (fast LLM check): DeepSeek V3.2 at $0.14/M = nearly free
- Tier 3 (expert panel): 
  - Claude Sonnet: $3/$15
  - GPT-4.1: ~$2/$8
  - Gemini 3.1 Pro: $2/$12
  - Average: ~$2.3/$11.7 per M tokens
- Cascaded approach: 85% handled by DeepSeek ($0.14/M), 
  15% by expert panel ($7/M average) = effective rate ~$1.2/M

### Key feature: OpenAI-compatible API
```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)
# Switch models by changing ONE parameter:
model="deepseek/deepseek-chat-v3"  # or
model="anthropic/claude-sonnet-4.6"  # or  
model="google/gemini-3.1-pro"
```

### Tokenization note:
"Token counts (and therefore costs) will vary between models, 
even when inputs and outputs are the same." 
Arabic text will tokenize differently per model. MUST measure empirically.

---

## FINDING 10: Scholarly Quality Metrics

From the Islamic content evaluation papers:
- **Theological accuracy**: Are positions correctly stated? (1-5 scale)
- **Attribution accuracy**: Is every opinion correctly attributed? (1-5)
- **Citation integrity**: Are sources real and correctly referenced? (1-5)
- **Completeness**: Are major scholarly positions covered? (1-5)
- **Scholarly tone**: Does it read like scholarship, not a summary? (1-5)
- **Hallucination rate**: % of claims not grounded in sources
- **School consistency**: Same school → same positions across entries

From KITAB's evaluation methodology:
- **Precision**: Of identified text reuse, how much is real reuse?
- **Recall**: Of actual text reuse, how much was found?
- **Ground truth comparison**: Manual annotation vs algorithm output
- **Cross-validation**: Multiple human annotators checking same items

---

## SYNTHESIS: What I Actually Know Now

### Confident conclusions:
1. Multi-model evaluation IS justified — research strongly supports it
2. Cascaded evaluation (cheap → expensive) IS cost-effective — proven
3. OpenRouter makes multi-model trivially easy — one API, one key
4. Models differ dramatically on Arabic/Islamic content — 50% to 93%
5. The synthesis engine is the highest-risk component — LLMs "fall short 
   on faith-sensitive rigor"
6. OpenITI/KITAB has already solved the corpus organization problem — 
   KR should learn from (maybe use) their infrastructure
7. 3-4 parallel agents is optimal — more causes coordination tax
8. Regression tests are the #1 defense against autonomous agent failures
9. Fresh sessions per task prevent context saturation
10. Arabic tokenization varies per model — must measure, not estimate

### Things I still can't plan:
1. Specific rubric prompts — need real pipeline output to test against
2. Exact model composition for judge panel — need Experiment 1
3. Whether synthesis engine produces good entries — need Experiment 2
4. Fix loop convergence — only knowable by running it
5. Timeline — too many unknowns

### The honest recommendation:
Don't design more architecture. Run the 4 validation experiments 
(from POST_PREP_PLAN.md) as soon as the prep sessions finish. 
Let the results guide the design, not the other way around.

The research IS valuable — it tells us WHAT to test and WHY. 
But it can't tell us what will work for KR specifically. 
Only experiments can do that.

---

## FINDING 11: RAG Evaluation & Hallucination Detection

### 11a: The RAG Triad (RAGAS Framework)
Source: Multiple (RAGAS docs, evaluation guides)

The standard metrics for RAG evaluation:
1. **Context Relevance**: Did the retriever find the RIGHT documents?
2. **Faithfulness**: Is every claim in the output SUPPORTED by the context?
3. **Answer Relevancy**: Does the output actually answer the query?

For KR specifically:
- Context Relevance → "Did the excerpting engine find the right excerpts for this topic?"
- Faithfulness → "Does the synthesized entry ONLY contain claims from the source excerpts?"
- Answer Relevancy → "Does the entry actually address the taxonomy topic?"

### 11b: Faithfulness as the Core Metric
Source: Hallucination Mitigation review (MDPI 2025), RAGAS docs

Faithfulness = "the fraction of statements in the answer that can be 
confirmed by the supplied context"

How to measure it:
1. **Statement extraction**: Break the synthesis output into individual claims
2. **Verification**: For each claim, check if it's supported by any excerpt
3. **Score**: faithfulness = (supported claims) / (total claims)

A perfectly faithful entry (score 1.0) means EVERY claim traces to an excerpt.
A score of 0.8 means 20% of claims are ungrounded — potential hallucination.

This is EXACTLY what KR's grounding_type system (D-040) is designed to do:
- source_grounded: claim comes directly from an excerpt
- metadata_derived: claim comes from metadata computation
- analytical: claim is the system's own analysis (flagged as such)

The faithfulness check can be automated:
- Extract every claim from the synthesis entry
- For each claim tagged "source_grounded", verify it appears in the cited excerpt
- For each claim tagged "analytical", verify the analysis is logically sound
- Flag any untagged claims as potential hallucinations

### 11c: SelfCheckGPT Method
Source: MetaRAG paper, Manakul et al.

"Query the LLM multiple times with the same prompt and measure 
semantic consistency across responses. The intuition is that 
hallucinated content often leads to instability under stochastic 
re-generation; true facts remain stable, while fabricated ones diverge."

For KR: Run the synthesis engine 3 times on the same excerpts.
- Claims that appear in all 3 runs → high confidence (likely grounded)
- Claims that appear in only 1 run → low confidence (likely hallucinated)
This is a COMPLEMENTARY check to direct excerpt verification.

### 11d: Multi-Judge Faithfulness Evaluation
Source: Evaluating Faithfulness in Agentic RAG (Dec 2025)

Recent paper used EXACTLY our proposed approach:
- Three LLM judges: GPT-4.1, Claude Sonnet 4.0, Gemini 2.5 Pro
- Temperature 0 for deterministic scoring
- Statement-level extraction → per-statement faithfulness scoring
- Each judge independently evaluates each statement
- Cross-judge agreement measured

This validates our multi-model panel design IS standard practice.

### 11e: Tools Available
- **RAGAS**: Open-source, Python, pip installable. Faithfulness, context 
  relevance, answer relevancy metrics. Reference-free (no ground truth needed).
- **DeepEval**: Open-source, pytest integration, CI/CD ready. 14+ metrics.
- **Phoenix (Arize)**: Open-source, real-time monitoring, hallucination detection.
- **LangSmith**: Tracing, evaluation, monitoring. LangChain ecosystem.

For KR: RAGAS is the natural choice — it's open-source, Python-native, 
designed for exactly our use case, and the metrics map directly to our 
quality requirements. Can be run from Claude Code non-interactively.

Implications for KR:
- The synthesis engine's output CAN be automatically checked for faithfulness
- Statement-level extraction → per-statement verification is proven methodology
- KR's grounding_type tagging (D-040) maps perfectly to faithfulness checking
- SelfCheckGPT (3 runs, consistency check) is a free, complementary method
- RAGAS framework can be integrated directly into the test harness
- Multi-model judging for faithfulness is established practice (not novel)

---

## FINAL SYNTHESIS: What This Research Means for KR

### The landscape is favorable:
1. Multi-model evaluation via OpenRouter is trivially easy and cheap
2. RAG faithfulness evaluation is a solved problem (RAGAS, etc.)
3. Autonomous agent loops work at scale (C compiler: 16 agents, 100K lines)
4. Arabic-specific models and tools exist (QARI-OCR, OpenITI, KITAB)
5. Islamic content evaluation has been benchmarked (3.9/5 GPT-4o score)

### The risks are real:
1. LLMs fail on precise Islamic jurisprudence (~50% accuracy for some models)
2. Autonomous loops can oscillate, get stuck, or optimize wrong metrics
3. Arabic tokenization costs are unknown until measured
4. The synthesis engine is the highest-risk component
5. No existing system does what KR does end-to-end

### What must happen BEFORE building:
1. **Experiment 1**: Can LLMs judge Arabic scholarly output? (10 samples, 4 models)
2. **Experiment 2**: Can the synthesis engine produce study-worthy entries? (owner judges)
3. **Experiment 3**: Arabic tokenization costs (actual measurement)
4. **Experiment 4**: Multi-layer detection feasibility (1 real Shamela source)
5. **Experiment 5 (NEW)**: RAGAS faithfulness on a synthetic KR example 
   (can we check if a synthesis entry is grounded in its source excerpts?)

### What to build when building:
1. Pipeline CLI (7 engines, testable, inspectable output at every stage)
2. RAGAS-based faithfulness checker (synthesis → excerpt grounding verification)
3. Multi-model rubric evaluator (OpenRouter, 3 model families)
4. Deterministic property tests (text fidelity, schema, metadata, isnads)
5. Autonomous test loop (bash while-true + claude -p, C compiler pattern)
6. Findings tracker (OPEN.md → Claude Code reads/fixes → re-runs)

### What NOT to build:
1. Complex orchestration (Paperclip, etc.) — bash scripts are sufficient
2. More than 3-4 parallel agents — diminishing returns beyond that
3. Elaborate planning documents — run experiments instead
4. Custom evaluation framework — use RAGAS + simple rubric scripts
