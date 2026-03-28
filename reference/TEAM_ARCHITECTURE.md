# KR Team Architecture — بنية الفريق

**Authority:** GOVERNING for all factory agent operations.
**Principle:** No single agent's output is ever trusted alone. Every operation uses a team. Every decision has at least two independent perspectives before it's committed.
**Companion documents:** `FACTORY_ROADMAP_v2.md` (setup), `AUTONOMOUS_QUALITY_SYSTEM.md` (what the factory does)

---

## The Governing Rule

**Never solo. Always a team.**

No code is committed by one agent without review from another. No finding is classified without a second opinion. No design decision is made without challenge. No synthetic data is generated and evaluated by the same provider. No fix is merged without independent verification that the root cause was addressed.

This is not a preference. It is the operating rule of the factory. A solo agent that produces correct-looking output is the most dangerous thing in the system — it creates confidence without verification.

---

## Available Capabilities (Verified)

### CC Agent Teams (primary collaboration mechanism)
- Teammates run in parallel, each with own context window
- Peer-to-peer messaging (teammates talk directly, not just through lead)
- Shared task list with dependency tracking and self-claiming
- File locking prevents edit conflicts
- Requires Opus 4.6 (our default model) and `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Teams of 2-16 agents supported
- Cost: 3-7x tokens vs single session (acceptable on Max plan)
- **Limitation (March 2026):** All teammates run the same model (Opus 4.6). Cannot mix models within a team.

### CC Subagents (lightweight focused tasks)
- Run within a single session, report back to parent
- CAN use different models via `CLAUDE_CODE_SUBAGENT_MODEL` env var
- Good for: fast validation checks, file exploration, focused analysis
- Cannot communicate with each other (only with parent)
- Lower overhead than full teammates

### External CLI invocation (cross-provider validation)
- Any CC session (lead or teammate) can invoke `codex exec` and `gemini -p` via Bash tool
- This brings cross-provider perspective INTO a team session without leaving it
- Codex has a purpose-built `codex exec review --base HEAD~1 --uncommitted` command
- Gemini can be invoked with `--output-format json` for structured responses

### CC Model Routing (cost/capability optimization)
- Lead sessions: Opus 4.6 (complex reasoning, coordination)
- Subagents: Sonnet 4.5 via `CLAUDE_CODE_SUBAGENT_MODEL` (focused implementation)
- Quick checks: Haiku via subagent model routing (fast validation, low cost)
- External validation: GPT-5.4 (via Codex), Gemini 3.1 (via Gemini CLI)

### Session Persistence and Branching
- `--session-id` for named sessions that persist
- `--resume` / `--continue` for multi-turn workflows
- `--fork-session` for branching from existing context
- `--no-session-persistence` for ephemeral operations

### Defined Agents (21 in `.claude/agents/`)
- Build team: code-reviewer, build-prober, test-engineer
- SPEC team: spec-adversary, spec-auditor-a, spec-auditor-b, spec-writer
- Verification team: verifier-a, verifier-b, integrity-auditor, boundary-validator
- Red team: verdict-adversary, regression-detector, triage-analyst
- Specialized: arabic-reviewer, deep-researcher, library-integrity-checker, evaluation-prep
- Support: consolidator, audit-comparator, quick-check

### MCP Servers
- Tavily (web search)
- Context7 (documentation lookup)
- Available to any session via `--mcp-config`

---

## Team Compositions by Factory Mode

### BUILD Mode Team

**When:** A SPEC exists and needs implementation.
**Team size:** 4 teammates + lead
**Communication pattern:** Continuous — teammates share findings, challenge each other's work, and coordinate on API contracts and data flow.

```
┌──────────────────────────────────────────────────────┐
│                    LEAD (Opus 4.6)                    │
│  Reads SPEC. Decomposes into tasks with dependencies.│
│  Assigns tasks. Monitors quality. Resolves conflicts.│
│  Synthesizes final output. Reports to orchestrator.  │
└──────────────────┬───────────────────────────────────┘
                   │ spawns + coordinates
     ┌─────────────┼──────────────┬──────────────────┐
     ▼             ▼              ▼                  ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│IMPLEMENT│  │  REVIEW   │  │   TEST   │  │  VALIDATE    │
│         │  │           │  │          │  │              │
│Writes   │  │Reviews    │  │Writes    │  │Invokes Codex │
│code per │  │each impl  │  │tests for │  │exec review   │
│SPEC     │  │against    │  │each impl │  │for cross-    │
│section. │  │SPEC. Flags│  │as it's   │  │provider      │
│Uses     │  │deviations │  │written.  │  │validation.   │
│spec-    │  │and ambi-  │  │Runs      │  │Invokes       │
│writer   │  │guities.   │  │suite     │  │Gemini for    │
│agent.   │  │Messages   │  │after     │  │adversarial   │
│         │  │IMPLEMENT  │  │each      │  │challenge on  │
│         │  │directly   │  │change.   │  │design        │
│         │  │with       │  │Messages  │  │decisions.    │
│         │  │findings.  │  │IMPLEMENT │  │Reports       │
│         │  │           │  │with      │  │cross-provider│
│         │  │Uses code- │  │failures. │  │findings to   │
│         │  │reviewer   │  │          │  │team.         │
│         │  │agent.     │  │Uses test-│  │              │
│         │  │           │  │engineer  │  │              │
│         │  │           │  │agent.    │  │              │
└─────────┘  └──────────┘  └──────────┘  └──────────────┘
     ↕              ↕            ↕              ↕
  [All teammates message each other directly]
```

**How it works in practice:**

1. Lead reads the SPEC section, decomposes into tasks: "Implement function X," "Write contract for Y," "Add validation for Z."
2. IMPLEMENT claims a task, writes the code.
3. REVIEW immediately reads the implementation, checks against SPEC, messages IMPLEMENT directly: "Your handling of multi-layer attribution doesn't match SPEC §4.3 — the sharh author should be tracked separately."
4. TEST writes tests for the implementation, runs them, messages IMPLEMENT: "Test for empty page list fails — your function doesn't handle the edge case."
5. VALIDATE invokes `codex exec review --base HEAD~1 --uncommitted` to get GPT-5.4's opinion on the code. Invokes `gemini -p "Review this design decision: [decision]. What could go wrong?"` for adversarial challenge. Reports findings to the team.
6. IMPLEMENT addresses all feedback, updates the code.
7. The cycle repeats for each task.
8. Lead synthesizes: fills the D-F018 response contract (assumptions made, decisions taken, escalations needed).

**Why this is better than sequential build→review→challenge:**
- REVIEW catches SPEC deviations in real-time, not after 50 functions are written
- TEST finds failures immediately, not in a separate session after the build is "done"
- VALIDATE brings cross-provider perspective into the build process, not as a post-hoc gate
- Teammates communicate directly — REVIEW doesn't have to go through Lead to tell IMPLEMENT about a problem

**Escalation within the team:**
If IMPLEMENT encounters a SPEC ambiguity, it messages Lead: "SPEC §4.3 is ambiguous about X." Lead creates an escalation artifact (D-F020) and messages VALIDATE: "Get Codex and Gemini's interpretation of this ambiguity." All three interpretations are logged. If they disagree, Lead pauses the task and routes to the escalation queue.

---

### HUNT Mode Team

**When:** No BUILD or FIX work exists. The factory hunts for bugs.
**Team size:** 3 teammates + lead
**Communication pattern:** Sequential generation → parallel processing → collaborative analysis.

```
┌──────────────────────────────────────────────────────┐
│                    LEAD (Opus 4.6)                    │
│  Selects threat type (coverage-weighted). Picks      │
│  template. Coordinates generation → processing →     │
│  comparison. Classifies findings. Writes reports.    │
└──────────────────┬───────────────────────────────────┘
                   │
     ┌─────────────┼──────────────────┐
     ▼             ▼                  ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ GENERATE │  │ PROCESS  │  │   ANALYZE    │
│          │  │          │  │              │
│Invokes   │  │Runs      │  │Compares      │
│Codex OR  │  │synthetic │  │actual output │
│Gemini to │  │data      │  │against ground│
│generate  │  │through   │  │truth. Uses   │
│synthetic │  │the target│  │finding_      │
│data from │  │engine.   │  │classifier.   │
│template. │  │Captures  │  │Invokes       │
│Validates │  │full      │  │Codex to      │
│structure.│  │output.   │  │independently │
│          │  │          │  │assess: "Is   │
│NEVER CC  │  │Uses CC   │  │this a real   │
│generates │  │pipeline  │  │bug or a test │
│the data  │  │code.     │  │artifact?"   │
│(D-F021). │  │          │  │              │
└──────────┘  └──────────┘  └──────────────┘
```

**Why cross-provider generation matters:**
CC built the pipeline. If CC also generates test data, it unconsciously avoids the patterns that would break its own code. Codex and Gemini have different reasoning patterns — their synthetic Arabic texts probe CC's blind spots.

**The GENERATE teammate's workflow:**
1. Receives a threat template from Lead (e.g., T-2 decontextualization).
2. Invokes Codex: `codex exec "Generate a synthetic Arabic scholarly text matching this specification: [template JSON]. Output as JSON with fields: synthetic_text, ground_truth, threat_type, variation." --output-last-message /tmp/synthetic_T2_047.json`
3. Validates the output (well-formed JSON, Arabic text present, ground truth specified).
4. If Codex fails or produces invalid output, falls back to Gemini.
5. Messages PROCESS: "Synthetic case syn-T2-047 ready at /tmp/synthetic_T2_047.json"

**The ANALYZE teammate's independence check:**
After comparing actual vs expected output, ANALYZE invokes Codex: "Here is the pipeline input and output. The expected output was X. The actual output was Y. Is this divergence a genuine bug, or could it be a valid alternative interpretation?" This prevents the team from reporting false positives.

---

### FIX Mode Team

**When:** `findings_queue/pending/` contains unresolved CRITICAL or HIGH findings.
**Team size:** 3 teammates + lead
**Communication pattern:** Analytical — teammates debate root cause, challenge each other's diagnoses, and verify fixes adversarially.
**CRITICAL RULE:** The FIX team NEVER hunts. The HUNT team NEVER fixes. Separation prevents "make the failing test pass" optimization.

```
┌──────────────────────────────────────────────────────┐
│                    LEAD (Opus 4.6)                    │
│  Reads finding. Coordinates root cause analysis.     │
│  Ensures fix addresses root cause, not symptom.      │
│  Manages regression testing. Reports to orchestrator.│
└──────────────────┬───────────────────────────────────┘
                   │
     ┌─────────────┼──────────────────┐
     ▼             ▼                  ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ DIAGNOSE │  │   FIX    │  │   VERIFY     │
│          │  │          │  │              │
│Analyzes  │  │Implements│  │Runs the      │
│the       │  │the code  │  │synthetic case│
│finding.  │  │fix based │  │that found the│
│Traces    │  │on root   │  │bug. Runs full│
│root      │  │cause     │  │regression.   │
│cause.    │  │analysis. │  │Invokes Codex:│
│Messages  │  │Messages  │  │"Did this fix │
│FIX with  │  │VERIFY    │  │address root  │
│"here's   │  │when      │  │cause or just │
│why it    │  │ready.    │  │patch the     │
│breaks."  │  │          │  │symptom?"     │
│          │  │Uses code-│  │Invokes       │
│Uses      │  │reviewer  │  │Gemini: "Can  │
│triage-   │  │agent.    │  │you construct │
│analyst   │  │          │  │an input that │
│agent.    │  │          │  │breaks this   │
│          │  │          │  │fix?"         │
└──────────┘  └──────────┘  └──────────────┘
```

**The VERIFY teammate's adversarial role:**
After FIX implements a change, VERIFY doesn't just run the existing test. It:
1. Runs the original synthetic case → must pass
2. Runs the full regression suite → must pass
3. Invokes Codex: "Review this diff. Does it fix the root cause or just the symptom?"
4. Invokes Gemini: "Here's the bug pattern: [pattern]. Here's the fix: [diff]. Can you construct an input that would still trigger the same class of failure?"
5. If Gemini finds a bypass, VERIFY messages FIX: "Your fix doesn't cover this variation."

---

### EVALUATE Mode Team

**When:** Pipeline has produced output the owner hasn't reviewed.
**Team size:** 2 teammates + lead
**Communication pattern:** Collaborative preparation of owner review packets.

```
Lead → PREPARE (formats Arabic output, RTL layout, Amiri font)
     → CHECK (reviews the packet for completeness, invokes Codex
        to independently assess: "What should the owner pay
        attention to in this output?")
```

---

### CROSS-ENGINE Mode Team

**When:** Weekly scheduled run, or after any engine modification.
**Team size:** 3 teammates + lead

```
Lead → GENERATE (creates synthetic output from engine N using Codex/Gemini)
     → PROCESS (feeds into engine N+1 using CC)
     → ANALYZE (compares output, invokes cross-provider validation)
```

Same pattern as HUNT, but focused on engine boundary contracts rather than individual threat types.

---

### BENCHMARK Mode Team

**When:** Monthly, after model updates, or after routing table staleness.
**Team size:** 1 lead dispatching sequential CLI runs

The benchmark is inherently sequential (each CLI processes the same cases). But the ANALYSIS is collaborative:
```
Lead runs benchmark → dispatches subagent per CLI
     → all results collected
     → Lead invokes ANALYZE teammate to compare results
     → ANALYZE invokes Codex: "Which model actually performed best on task X?"
     → ANALYZE invokes Gemini: "Are these results statistically meaningful?"
```

---

## Cross-Provider Integration Within Teams

Each CC teammate can invoke external CLIs as needed. This brings cross-provider perspective into every operation without breaking the team structure.

### Standard invocation patterns

**Codex code review (from any teammate):**
```bash
codex exec review --base HEAD~1 --uncommitted \
  --output-last-message /tmp/codex_review.md
```
The teammate reads `/tmp/codex_review.md` and incorporates findings.

**Codex analytical opinion (from any teammate):**
```bash
codex exec --full-auto \
  --output-last-message /tmp/codex_opinion.md \
  "Read engines/excerpting/src/phase1.py. Is the page boundary detection
   algorithm correct for texts where a sentence spans two pages?
   Focus on lines 142-189."
```

**Gemini adversarial challenge (from any teammate):**
```bash
gemini -p "A code review concluded that this implementation is correct:
[paste summary]. Challenge this conclusion. What edge cases could break it?
What assumptions is the reviewer making?" --output-format json
```
The teammate parses the JSON response and acts on findings.

**Gemini first-principles design check (from any teammate):**
```bash
gemini -p "Without knowing our current implementation, how would you design
a system that [description of what this code does]? What invariants would
you enforce?" --output-format json
```
Compare Gemini's independent design against the actual implementation. Divergences are potential findings.

### When to invoke external CLIs

**Always invoke Codex review on:** code that modifies contracts, code that handles Arabic text, code that affects attribution or school classification, any SPEC-deviation flagged by the REVIEW teammate.

**Always invoke Gemini challenge on:** design decisions, SPEC interpretations, ambiguity resolutions, any case where all CC teammates agree (consensus without external challenge is suspect).

**Never invoke external CLIs on:** trivial formatting changes, import ordering, comment updates, test reorganization. Use subagents for lightweight verification of these.

---

## The Orchestrator's Role

The orchestrator (Python script) does NOT participate in the team's work. It:

1. **Selects the mode** based on queue state (FIX > BUILD > EVALUATE > HUNT > CROSS-ENGINE > BENCHMARK)
2. **Dispatches the team** using `claude -p` with Agent Teams enabled
3. **Provides the team prompt** that defines the team composition, the work, and the quality bar
4. **Captures the result** from the JSON output
5. **Validates the response contract** (D-F018)
6. **Manages state transitions** (work unit status, findings lifecycle, git operations)
7. **Handles degraded modes** (if Codex/Gemini unavailable, teams still operate but flag `reduced_confidence`)

The orchestrator is software, not an agent. It makes deterministic decisions based on state. All judgment is inside the teams.

### Team dispatch prompt template

```
You are the lead of a KR factory team. Your mode is [BUILD/HUNT/FIX/...].

TEAM COMPOSITION:
Create an agent team with [N] teammates:
- "[Role 1]": [responsibilities]. Use the [agent-name] agent definition.
  This teammate should invoke `codex exec review` after [trigger condition].
- "[Role 2]": [responsibilities]. Use the [agent-name] agent definition.
  This teammate should invoke `gemini -p` to challenge [specific decisions].
- "[Role 3]": [responsibilities].

WORK:
[Work unit description, SPEC reference, input files, expected outputs]

QUALITY BAR:
- No output is trusted without at least one independent check
- Every SPEC interpretation must be cross-validated
- Every design decision must be challenged by an external CLI
- If you encounter ambiguity, create an escalation artifact — do NOT resolve silently
- Fill the response contract (D-F018) completely and honestly

RESPONSE CONTRACT:
[D-F018 schema]
```

---

## Cost and Token Management

Agent Teams use 3-7x tokens vs single session. On Max plan ($200/month), this is affordable but not infinite.

### Cost optimization strategies

1. **Subagents for focused tasks:** When a teammate needs a quick check (e.g., "does this import exist?"), it spawns a Haiku subagent instead of doing the work in its own Opus context.
   ```
   CLAUDE_CODE_SUBAGENT_MODEL="claude-haiku-4-5-20251001"
   ```

2. **Right-size teams per mode:**
   - BUILD: 4 teammates (high stakes, complex work)
   - HUNT: 3 teammates (parallel but focused)
   - FIX: 3 teammates (analytical, needs debate)
   - EVALUATE: 2 teammates (preparation work, lower complexity)
   - BENCHMARK: 1 lead + subagents (sequential CLI runs)

3. **External CLIs are free:** Every `codex exec` and `gemini -p` invocation uses subscription quota, not CC tokens. Using external CLIs for validation is the cheapest form of second opinion.

4. **Session persistence for multi-turn work:** Use `--session-id` for BUILD work units that span multiple orchestrator cycles. The team resumes with context from the previous cycle instead of rebuilding from scratch.

5. **Ephemeral sessions for one-shot work:** Use `--no-session-persistence` for HUNT cycles that don't need context from previous hunts.

---

## Enabling Agent Teams

### Settings change (Session 3 deliverable)

Add to `.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_CODE_SUBAGENT_MODEL": "claude-sonnet-4-5-20250929"
  }
}
```

### tmux requirement

Agent Teams need tmux for split-pane display (each teammate visible). In WSL:
```bash
sudo apt install tmux
```
For headless/scheduled operation, tmux is not required — teams run in-process.

### CLAUDE.md additions

Add to CLAUDE.md:
```markdown
## Team Operations
- This project uses Agent Teams for all factory operations
- Never work solo — always spawn at minimum 1 teammate for review
- Invoke `codex exec review` for cross-provider validation on any code change
- Invoke `gemini -p` for adversarial challenge on any design decision
- Fill D-F018 response contract for every work unit
- Create escalation artifacts for every ambiguity — never resolve silently
```

---

## What This Replaces

The sequential pipeline (CC builds → Codex reviews → Gemini challenges) is replaced by collaborative teams where all three perspectives operate simultaneously. The sequential approach was:
- Slow: three separate operations in series
- Fragile: if Codex is down, the entire review step is skipped
- Late: bugs found in review require restarting the build
- Silent: CC resolves ambiguities before review even sees them

The team approach is:
- Fast: parallel work with real-time communication
- Resilient: if Codex is unavailable, teammates note `reduced_confidence` and continue
- Early: review happens AS code is written, not after
- Transparent: ambiguities are debated between teammates, not silently resolved

---

## Summary

Every factory operation is a team operation. The team always includes at least one cross-provider check (Codex or Gemini invoked by a teammate). No single agent's output is ever the final word. The team structure is defined per mode, with the right number of teammates for the complexity of the work. The orchestrator dispatches teams, not individual agents. The quality bar is set by the lead and enforced by every teammate.

The factory is not one worker being supervised. It is a team of specialists that communicate, challenge each other, and produce output that has been tested from multiple angles before it ever reaches the owner.
