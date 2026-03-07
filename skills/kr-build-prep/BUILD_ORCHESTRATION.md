## Build Orchestration: Single Session vs. Agent Teams

There are three ways to run Claude Code on a KR engine. Choose based on what you're building.

### Option A: Single Session (Default — Start Here)

One Claude Code instance, one task, one context window. Use for:
- First build session on any engine (get the basics working)
- Focused module implementation (one format, one capability)
- Bug fixes and small changes
- Any task where parallelism adds no value

This is always the starting point. Don't use agent teams until single sessions are working cleanly on the engine.

### Option B: Agent Teams (For Complex Build Sessions)

Multiple Claude Code instances working in parallel with built-in coordination. Requires Opus 4.6 and one-line setup.

**Setup (one-time):**
```bash
# Add to environment or Claude Code settings.json:
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Recommended: install tmux for split-pane visibility
# macOS: brew install tmux
# Ubuntu: sudo apt install tmux

# Start tmux before launching Claude Code
tmux
```

**When to use for KR:**
- Building a full engine module end-to-end (builder + tester + reviewer)
- Processing a large batch of test fixtures in parallel
- Refactoring across multiple files that interact (contracts + engine + tests)
- Any session where you need 3+ specialized perspectives simultaneously

**KR-specific team templates:**

**Template 1: Builder-Tester-Reviewer (the standard KR team)**
```
Create an agent team to build [module name] for the [engine] engine.

Spawn three teammates:
- Builder: Implement [module] following engines/{engine}/docs/spec-rules.md. 
  Own all files in engines/{engine}/ except tests/.
- Tester: Write and run tests for [module] using fixture [fixture name].
  Own all files in engines/{engine}/tests/. Run pytest after each builder change.
  Flag any test failure immediately.
- Reviewer: Read the SPEC at [spec path] §4.A.[section]. After builder completes 
  each function, verify the implementation matches the SPEC rules. Check Arabic 
  text handling and metadata preservation (D-023). Do NOT write code — only review 
  and flag issues.

Coordinate through the shared task list. Builder implements, tester verifies, 
reviewer audits. No code merges until all three agree.
```

**Template 2: Multi-Format Expansion (after base works)**
```
Create an agent team to add [format] support to the [engine] engine.

Spawn three teammates:
- Format specialist: Implement the [format] handler in engines/{engine}/formats/.
  Reference the existing Shamela handler as the pattern to follow.
- Integration tester: Run the full pipeline on [format] test fixtures.
  Compare output schema against contracts.py. Flag any field that's missing 
  or wrong.
- Regression guard: Run ALL existing tests after each change. If any 
  previously-passing test breaks, halt and report immediately. Nothing 
  ships with regressions.
```

**Template 3: Evaluation Sprint (for kr-evaluate phase)**
```
Create an agent team to evaluate [engine] output on [fixture set].

Spawn three teammates:
- Deterministic checker (5a): Run schema validation, text integrity, metadata 
  completeness on all output files. Produce a structured report.
- LLM worker auditor (5b): For each LLM call the engine made, compare the 
  call's output against the expected result. Score accuracy per task type.
- Quality reviewer (5c): Run independent LLM evaluation on 10 sampled outputs.
  Use the rubric from the SPEC's §5. Flag anything the engine's self-validation 
  missed.

Each teammate produces an independent report. Lead synthesizes into a single 
assessment with the inter-engine gate decision.
```

**Cost and limits:**
- Each teammate is a full Opus 4.6 session. A 3-agent team costs ~3x a single session.
- On Pro plan (~5x free tier): budget for 1-2 team sessions per day.
- On Max plan ($100-200/month): budget for 8-10 team sessions per day.
- 3-5 teammates is optimal. Beyond 5, coordination overhead eats the gains (Google DeepMind research confirms diminishing returns).
- All teammates run Opus 4.6 — no per-role model selection yet.
- Agent teams are ephemeral. No memory between sessions. All state must be in files.

**What agent teams can NOT do:**
- They can't replace good SPEC design. Garbage in, garbage out — faster.
- They can't coordinate across engines (each team works on one codebase area).
- They don't persist. Every team is spawned fresh each session.
- Nested teams are not supported (a teammate can't spawn its own team).

### Option C: Git Worktrees (For Manual Parallelism)

If you want parallel sessions without the coordination overhead of agent teams:
```bash
claude -w feature-name    # Creates isolated worktree with its own branch
```

Use for: working on two independent features simultaneously, or running a long test suite in one worktree while coding in another. Lighter than agent teams, but no inter-session communication.

### Option D: The Bash Loop (For Autonomous Test Runs)

From the C compiler case study — simplest autonomous pattern:
```bash
while true; do claude -p "$(cat PROMPT.md)"; done
```

Use for: running a test-fix-retest cycle overnight. Claude reads the prompt, runs tests, fixes failures, commits, and the loop restarts with a fresh context. Good for regression grinding after the main implementation is done.

### Progression for Each Engine

```
Session 1-2:  Single session. Get basic module working. One format, one fixture.
Session 3-5:  Single session. Add formats, edge cases, error handling.
Session 6+:   Agent teams IF the engine is complex enough to benefit.
              (Source engine: yes. Passaging engine: probably not.)
Evaluation:   Agent teams for the evaluation sprint (Template 3).
Regression:   Bash loop for overnight test grinding.
```

### Other Tools (Optional, Not Required)

**Faber** (github.com/orecus/faber): Desktop GUI wrapping Claude Code with Kanban and multi-pane sessions. Adds visual task management but also adds complexity. Consider only if the terminal workflow feels limiting.

---
