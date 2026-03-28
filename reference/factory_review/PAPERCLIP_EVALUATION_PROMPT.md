# Paperclip Evaluation — Hands-On Test for KR

## Your role

You are evaluating Paperclip (https://github.com/paperclipai/paperclip) as a potential orchestration layer for the KR factory. Your job is to install it, configure it for KR, run real tasks through it, and report HONESTLY on what works, what doesn't, and whether it fits.

**Be adversarial, not agreeable.** If Paperclip doesn't work well for KR, say so clearly. If it's amazing, say that too. We need truth, not diplomacy. If you find fewer than 3 problems, you haven't tested hard enough.

## Context

KR is a 5-engine pipeline for Arabic Islamic scholarly texts. The factory we're building needs:
- Multi-agent orchestration (CC builds, Codex reviews, Gemini challenges — as teams, not sequential)
- Scheduled autonomous operation (heartbeats every 30 minutes)
- Cost tracking and budget enforcement
- Governance gates (owner approves scholarly content, SPEC interpretations)
- A dashboard the owner can check from his phone
- Task management with dependencies
- Persistent state across reboots
- Support for 6 operating modes: BUILD, HUNT, FIX, EVALUATE, CROSS-ENGINE, BENCHMARK

We currently have `scripts/overnight_orchestrator.py` (1,287 lines) doing some of this. The question is whether Paperclip replaces the custom orchestrator and the dashboard we were going to build from scratch.

Read these documents for full context:
- `reference/FACTORY_ROADMAP_v2.md` — what we're building
- `reference/AUTONOMOUS_QUALITY_SYSTEM.md` — the 6 operating modes
- `reference/TEAM_ARCHITECTURE.md` — how agents collaborate

## Phase 1: Installation (report any issues)

1. Install Paperclip:
   ```bash
   npx paperclipai onboard --yes
   ```
   If that fails, try the manual route:
   ```bash
   git clone https://github.com/paperclipai/paperclip.git /home/you/paperclip
   cd /home/you/paperclip
   pnpm install
   pnpm dev
   ```

2. Document:
   - Did installation succeed? Any errors?
   - What dependencies were needed?
   - What ports/services are running?
   - How much disk space does it use?
   - Is the UI accessible? At what URL?

## Phase 2: KR Company Setup

1. Create a company:
   - Name: "خزانة ريان" (KR)
   - Mission: "Build a correct, robust Islamic scholarly library where every metadata claim is traceable and every scholarly position is faithfully represented"

2. Define goals:
   - Goal 1: "Complete the excerpting engine with zero silent corruption"
   - Goal 2: "Hunt and fix bugs continuously using synthetic adversarial data"
   - Goal 3: "Build remaining engines (taxonomy, synthesis) through the factory"

3. Set up agents (try configuring these — report what works and what doesn't):
   
   **Agent: CTO**
   - Adapter: claude_local (Claude Code)
   - Model: Opus
   - Role: Coordinates all technical work, decomposes SPECs into tasks
   - Working directory: the KR repo path
   - Budget: test with a small limit
   
   **Agent: Builder**
   - Adapter: claude_local
   - Model: Opus
   - Role: Implements code per SPEC sections
   - Reports to: CTO
   
   **Agent: Reviewer**
   - Adapter: codex_local (Codex CLI)
   - Role: Reviews code changes, checks SPEC compliance
   - Reports to: CTO
   
   **Agent: Adversary**
   - Adapter: gemini_local (if supported) or bash (wrapping gemini CLI)
   - Role: Challenges design decisions, tries to break implementations
   - Reports to: CTO

4. Document:
   - Can you set up org chart with reporting lines?
   - Can you assign different adapters (Claude, Codex, Gemini) to different agents?
   - Can you set per-agent budgets?
   - Does the goal hierarchy work (company mission → project goals → tasks)?
   - Can you configure heartbeat intervals per agent?
   - What does the dashboard look like with this setup?

## Phase 3: Task Execution Test

1. Create a simple task and assign it to the Builder agent:
   - Task: "Read `engines/excerpting/SPEC.md` and list all error codes defined in section 7"
   - This is a read-only task — safe to run

2. Trigger the agent (heartbeat or manual trigger) and observe:
   - Does the agent pick up the task?
   - Does it execute correctly?
   - Does it report results back to Paperclip?
   - Can you see the conversation thread in the dashboard?
   - Is the cost tracked?
   - Does the task status update (pending → in_progress → completed)?

3. Try a multi-agent workflow:
   - Create task A: "Builder: write a Python function that validates Arabic text has balanced parentheses" (assign to Builder)
   - Create task B: "Reviewer: review the function Builder wrote in task A" (assign to Reviewer, depends on task A)
   - Does the dependency system work? Does the Reviewer wait for the Builder to finish?
   - Does the Reviewer (Codex) actually pick up and execute the review?

4. Test governance:
   - Try to make the CTO agent "hire" a new agent
   - Does it require Board (owner) approval?
   - Can you approve/reject from the dashboard?

5. Document:
   - End-to-end: does a task go from creation → assignment → execution → completion?
   - Multi-agent: do dependencies and delegation work?
   - Governance: do approval gates work?
   - Cost: is spending tracked and visible?
   - Dashboard: can you see all agent activity, costs, task status in one place?

## Phase 4: KR-Specific Evaluation

Answer these questions based on your hands-on experience:

1. **Can Paperclip handle our 6 operating modes?** We have BUILD, HUNT, FIX, EVALUATE, CROSS-ENGINE, BENCHMARK modes. Could these be modeled as Projects or Goals in Paperclip? How?

2. **Can Paperclip handle our team compositions?** In BUILD mode, we want 4 agents (builder + reviewer + tester + validator) working together on the same SPEC section. Does Paperclip support this kind of coordination?

3. **Can agents invoke each other?** We need CC to invoke `codex exec review` and `gemini -p` during its own work (not as separate Paperclip tasks, but as inline cross-provider checks). Does Paperclip's model allow this, or does everything have to go through the ticket system?

4. **Can we use CC Agent Teams WITHIN Paperclip?** The most powerful pattern: Paperclip assigns a task to a CC agent, and that CC agent spawns an Agent Team internally. Does this work with the claude_local adapter?

5. **How does Paperclip handle our findings database?** We have `findings_db/` with threat-typed findings that flow through a lifecycle (DISCOVER→CLASSIFY→FIX→VERIFY→HARDEN). Can Paperclip's ticket system model this, or do we need our own system alongside Paperclip?

6. **What about our synthetic data generation?** The HUNT mode generates synthetic Arabic texts via Codex/Gemini, runs them through the pipeline, and compares output against ground truth. Can this workflow be modeled in Paperclip, or is it too specialized?

7. **Does Paperclip persist session state for CC?** One of our requirements: CC sessions should be resumable across heartbeats. Does the claude_local adapter use `--session-id` or `--resume` to maintain context?

8. **How robust is it?** Try to break it:
   - Kill the server mid-task. Does it recover on restart?
   - What happens if an agent times out?
   - What happens if the database gets corrupted?
   - What's the worst thing that could happen?

9. **What's missing for KR?** What would we still need to build custom, even with Paperclip handling orchestration?

10. **What does Paperclip give us that we'd be foolish to rebuild ourselves?** Be specific — which of our planned custom components (from FACTORY_ROADMAP_v2.md Sessions 6-8) does Paperclip do better?

## Phase 5: Verdict

Produce your final assessment as structured JSON:

```json
{
  "installation": {
    "success": true/false,
    "issues": ["..."],
    "time_to_setup": "X minutes"
  },
  "kr_company_setup": {
    "org_chart_works": true/false,
    "multi_adapter_works": true/false,
    "budget_enforcement_works": true/false,
    "goal_hierarchy_works": true/false,
    "issues": ["..."]
  },
  "task_execution": {
    "single_agent_works": true/false,
    "multi_agent_dependencies_work": true/false,
    "governance_gates_work": true/false,
    "cost_tracking_works": true/false,
    "issues": ["..."]
  },
  "kr_fit_assessment": {
    "replaces_orchestrator": true/false,
    "replaces_dashboard": true/false,
    "replaces_scheduler": true/false,
    "replaces_cost_tracking": true/false,
    "replaces_governance": true/false,
    "supports_6_modes": true/false,
    "supports_team_compositions": true/false,
    "supports_inline_cross_provider": true/false,
    "supports_cc_agent_teams_inside": true/false,
    "supports_findings_lifecycle": true/false,
    "sessions_saved_if_adopted": "N sessions",
    "custom_work_still_needed": ["..."],
    "issues": ["..."]
  },
  "recommendation": "ADOPT / EVALUATE_FURTHER / REJECT",
  "reasoning": "...",
  "risks": ["..."],
  "what_paperclip_does_better_than_custom": ["..."],
  "what_we_still_build_ourselves": ["..."]
}
```

## Rules

- Be thorough. Test everything. Don't assume.
- If something doesn't work, try to figure out WHY (is it a bug, a missing feature, or user error?)
- If documentation is poor, check the source code
- Compare honestly against our custom orchestrator (overnight_orchestrator.py)
- The owner has zero technical background. Consider setup complexity honestly.
- This evaluation should take 1-2 hours of real testing, not 10 minutes of surface-level checks

Stop after this evaluation. Do not continue to other work.
