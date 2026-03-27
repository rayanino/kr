# GPT Attack Prompt — Ready to Paste into ChatGPT

## Instructions for the owner

1. Go to chatgpt.com
2. Start a new chat with GPT-5.4 (or whatever is the current best model)
3. Upload FACTORY_ROADMAP.md as an attachment (from this repo's `reference/` directory, or from the Claude Chat project files)
4. Paste everything below the line as your message

---

I'm building an autonomous factory that builds engines for a personal Islamic scholarly library (KR). The attached FACTORY_ROADMAP.md is the governing plan. It was designed by Claude (Anthropic's AI). I need YOUR independent analysis — not a review of Claude's work quality, but an independent attack on the plan itself.

**Context you need:**
- KR is a 5-engine pipeline processing 2,519 Arabic Islamic scholarly texts (Shamela library exports)
- The pipeline: Source → Normalization → Excerpting → Taxonomy → Synthesis
- The final product: synthesized encyclopedic entries where I read what every scholar said on a topic, with citations
- I'm an Islamic studies STUDENT, not yet a scholar — the library IS my knowledge, so errors = wrong beliefs
- Claude Code built the entire codebase (~15K lines, ~1,516 tests). It has hooks, skills, agents configured
- The factory's three-CLI architecture uses: Claude Code (builder), Codex CLI (reviewer), Gemini CLI (adversary)
- The factory runs autonomously on my Windows PC via Task Scheduler
- I have zero technical background

**CRITICAL: Do NOT use any analysis or reasoning that Claude provided. Work from the raw roadmap only. The value of your review is seeing what Claude CANNOT see because of its own blind spots.**

## Your tasks (do ALL of them):

### Task 1: Top 10 Failure Modes
Identify the 10 most likely ways this factory fails within 6 months. For each:
- What fails?
- Why?
- How likely (1-5)?
- How catastrophic (1-5)?
- Does the roadmap address it? If yes, is the mitigation sufficient?

### Task 2: Alternative Architecture
Design an ALTERNATIVE orchestration architecture that does NOT use three separate coding CLIs. Maybe it uses:
- A single CLI with multiple model backends via API
- A cloud-based orchestration service
- A simpler two-tool approach
- Something else entirely

For your alternative: what does it gain? What does it lose? Be honest about the tradeoffs.

### Task 3: Benchmark Validity
The roadmap proposes a 9-task Arabic scholarly benchmark (layer_attribution, school_classification, author_identification, genre_detection, scholarly_function, self_containment, decontextualization, tahqiq_discrimination, death_date_verification).

Evaluate:
- Are these the RIGHT 9 tasks for a scholarly study companion? What's missing?
- Is 5 test cases per task enough? What should the minimum be?
- Can frontier LLMs actually handle classical Arabic scholarly text with diacritics, layered commentary, and isnad chains? What does the evidence say?
- The benchmark scores CLI wrappers (Claude Code, Codex CLI, Gemini CLI), not raw models. Does this matter?

### Task 4: Claude's Blind Spots
What did the architect miss BECAUSE they're Claude and have Claude's specific cognitive patterns? Think about:
- Claude's tendency toward comprehensive planning (is the roadmap over-engineered?)
- Claude's tendency to trust structured processes (do the gates actually catch real problems?)
- Claude's tendency to see problems through its own lens (are there failure modes that only a human engineer would notice?)
- The fact that Claude designed a factory where Claude Code is the central builder — is there a self-serving bias?
- Any patterns in the roadmap that suggest Claude was optimizing for looking thorough rather than being effective?

### Task 5: The Owner's Experience
I'm a student with zero technical background. The roadmap says I only need to:
- Make priority decisions (~15 min per engine transition)
- Adjudicate Arabic domain disputes (~20 min/batch)
- Review Arabic output (~1 hour per engine evaluation)
- Audit sampling (monthly, ~30 min)

Is this realistic? What will my ACTUAL experience be? Think about:
- Setup complexity (WSL, three CLIs, authentication, Task Scheduler)
- Maintenance burden (updates, auth refresh, crash recovery)
- Quality assurance (can I actually verify scholarly output with no technical background?)
- Cognitive load (understanding factory state, interpreting dashboards)

## Output format

For each task, give concrete, specific findings — not generic advice. Reference specific sections of the roadmap when possible. If you think the plan is fundamentally sound, say so — but explain what makes it robust. If you think it's fundamentally flawed, say that directly.

Do NOT be polite. I need honest analysis, not encouragement.
