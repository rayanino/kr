# Prompt for Next Chat Session

Copy everything below the line into a new chat. This chat does NOT need to be in a specific engine project — it is project-level work.

---

<project>
خزانة ريان (KR) is a personal Islamic scholarly library with a 7-engine pipeline (Source → Normalization → Passaging → Atomization → Excerpting → Taxonomy → Synthesis) that transforms raw Arabic scholarly texts into structured knowledge entries.

Repository: github.com/rayanino/kr
The Github_key project knowledge file contains the personal access token.

Current state: The development protocol has been redesigned and refined across three sessions. No engine code runs yet. All 7 engines have SPECs and contracts.py files. The next action is the tracer bullet (Step 0 in ENGINE_PROTOCOL.md), but before starting it, the repo foundation needs a final check.
</project>

<startup>
Clone the repo and orient yourself:

```
cd /home/claude
rm -rf kr
git clone https://rayanino:TOKEN@github.com/rayanino/kr.git kr
cd kr
git config user.name "KR Architect"
git config user.email "kr-architect@khizanat-rayan.dev"
```

Replace TOKEN with the actual token from the Github_key project knowledge file.

Then read these files in order to understand the current plan:
1. `skills/shared/ENGINE_PROTOCOL.md` (301 lines) — the master development process
2. `OPEN_PROBLEMS.md` — the roadmap and status
3. `NEXT.md` — what happens next
4. `STEERING.md` — project overview
</startup>

<task_1>
## Final repo and plan audit before starting the tracer bullet

Investigate the repo for remaining problems. Read all files you need — do not limit yourself to what I list here. Look at the full picture: protocol, skills, templates, engine SPECs, contracts, existing code, supporting documents, test fixtures.

Specific concerns to check (not exhaustive — find issues I have not thought of too):

- Inconsistencies between ENGINE_PROTOCOL.md, the 6 skills in `skills/kr-*/SKILL.md`, the 7 engine templates in `skills/engine-project-template/*.md`, and supporting documents (TESTING_FRAMEWORK.md, KNOWLEDGE_INTEGRITY.md, STEERING.md). After three rounds of changes, things may have drifted.
- Root-level file clutter. There are ~15 root markdown files. Some may be obsolete or superseded by the new protocol (CHALLENGE_PROTOCOL.md? MILESTONES.md? ORCHESTRATOR.md? REVIEW_PROTOCOL.md?). Identify which are still needed.
- Stale code in engine src/ directories. Four engines (source, normalization, passaging, atomization) have src/ code from before the current protocol existed. Will this confuse the tracer bullet or build phases? Should it be archived?
- Anything else that would cause problems when the tracer bullet starts.

For each finding: state what you found, why it matters, and propose a concrete fix. Use severity levels: CRITICAL (blocks the tracer bullet), IMPORTANT (causes confusion or errors during engine work), MINOR (cosmetic or low-risk).

After presenting findings, implement all CRITICAL and IMPORTANT fixes. Present MINOR fixes for my approval before implementing.
</task_1>

<task_2>
## Autonomous project steering — feasibility analysis

After task 1 is complete, investigate this question:

The current protocol requires the owner (an Islamic studies student, no technical background) to do several things: write domain comments on SPECs, review core vs. deferred classification, approve SPEC changes, evaluate Arabic output at Step 4, define science tree structures, and make human gate decisions. 

Can an LLM with the right setup (domain knowledge files, web search, the existing SPECs) reliably replace some or all of these responsibilities? What would that setup look like concretely?

To answer this well:
- Research how other projects structure autonomous AI-driven development. Look at agentic workflows, Claude Code autonomous mode, multi-agent orchestration patterns.
- For each owner responsibility listed above, independently assess: can an LLM do this reliably for classical Arabic Islamic scholarly texts specifically? What would go wrong? What evidence exists?
- If a practical autonomous setup is feasible, describe it concretely: what project structure, what custom instructions, what safeguards, what the owner still must do manually.
- If it is not feasible (or only partially feasible), explain which responsibilities are genuinely human-irreplaceable and why.

Present your analysis as a structured assessment, not a recommendation I asked you to validate. I want your honest evaluation, including where autonomy would fail.
</task_2>

<output_format>
For task 1: Present findings with severity levels, then implement fixes (CRITICAL and IMPORTANT immediately; MINOR after my approval).
For task 2: Present a structured analysis with clear sections. Do not make repo changes for task 2 — it is analysis only.
</output_format>
