# Handoff — Skills & Workflow Research — 2026-03-07

## What Was Done (This Session)

### Skills Created and Iterated (3 versions)
Six account-level Claude Chat skills written, hardened, and committed to `skills/`:

1. **kr-spec-review** — Owner comments treated as research hypotheses, not instructions. Investigation scales to complexity. Claude forms its own position and may disagree.
2. **kr-finalize** — Phased across 3-4 chats (consolidate → audit per section → assemble). Never one marathon session.
3. **kr-build-prep** — Tech survey mandatory first. CLAUDE.md under 200 lines. Dev docs pattern (plan.md, context.md, tasks.md per session).
4. **kr-evaluate** — Reviews test output across 5a deterministic / 5b LLM-worker / 5c LLM-evaluator. Error taxonomy: engine bug vs SPEC gap vs LLM quality vs data issue vs upstream error.
5. **kr-research** — Creative engine: Scholar's Dream, Impossibility Search, Cross-Tradition Steal, 5 design questions. Minimum 8 searches.
6. **kr-integrity** — Deep audit: 25 Perfection Standard criteria + 7 corruption threats + 7 silent failure patterns + per-field corruption analysis.

### Architecture Decision: Repo-First Workflow
Claude Chat clones the repo at each chat start (4-second shallow clone). This eliminated the need for heavy project knowledge files. Now only 2 files needed in project knowledge: Github_key + STEERING.md.

Benefits: ~198K tokens free (vs ~150K before), single source of truth, versioned changes, no manual file management.

### Source Engine Project Setup Produced
- Custom instructions with bibliographic specialist role + startup procedure + universal mandates
- Setup guide (knowledge_files.md) explaining the minimal 2-file approach
- Comment template for structured owner feedback

### Shared Infrastructure
- `skills/shared/COMMENT_TEMPLATE.md` — structured format for owner comments
- `skills/shared/HANDOFF_PROTOCOL.md` — session bridging protocol
- `skills/handoffs/` directory — committed handoff documents

### Key Research Findings Already Gathered

**Claude Code optimization:**
- CLAUDE.md must stay under 200 lines (HumanLayer research: models follow ~150-200 instructions; CC system prompt uses ~50)
- Dev docs pattern: separate plan.md/context.md/tasks.md per session
- Agent teams: 3-5 teammates optimal, experimental but functional (Opus 4.6+)
- Faber (github.com/orecus/faber): desktop GUI for agent orchestration, young but promising
- Bash-loop pattern (C compiler case study): simplest autonomous approach

**Skill authoring:**
- Vercel found skills trigger unreliably — 56% miss rate. Descriptions must be "pushy."
- Progressive disclosure: metadata always loaded (~100 tokens), SKILL.md loaded on trigger, reference files on demand
- Limit to 20-30 skills total for optimal performance
- Skills under 500 lines; split into reference files beyond that

**Context management:**
- 200K token window for Claude Chat
- Project knowledge files consume tokens from the start
- Context rot: accuracy degrades as token count grows
- Auto-summarization exists for long conversations (with code execution enabled)

---

## What Remains (Next Session's Focus)

### Deep Research Needed

1. **Reddit community insights** — r/ClaudeCode, r/ClaudeAI for:
   - Real-world Claude Chat project setups (not just Claude Code)
   - Prompt engineering patterns that work/fail
   - Common failure modes and workarounds
   - People using Claude Chat for non-coding project management

2. **MCP integrations for Claude Chat** — What MCPs could enhance our workflow?
   - GitHub MCP (does it exist? could it replace our manual clone approach?)
   - File system MCPs
   - Any scholarly/research MCPs
   - What MCPs does Claude Chat currently support vs Claude Code?

3. **Claude Chat-specific limitations and workarounds:**
   - How does skill triggering actually work in Claude Chat vs Claude Code?
   - Context management strategies for multi-session projects
   - Can Claude Chat use extended thinking? How does it affect context?
   - What happens when the clone fails? Fallback strategies?
   - Rate limiting and usage caps — how to work within them

4. **Community patterns for complex multi-session projects:**
   - How do people manage state across Claude Chat sessions?
   - Best project knowledge strategies
   - Custom instruction optimization techniques
   - Alternatives to our approach (e.g., using Claude Chat + Claude Code in tandem)

5. **Skill improvement based on research:**
   - Are our descriptions triggering reliably? 
   - Should we add reference files for progressive disclosure?
   - Do we need scripts in the skill directories?
   - Can we add validation scripts that Claude runs during skill execution?

6. **The Claude Chat + Claude Code handoff:**
   - kr-build-prep produces deliverables for Claude Code. Is the interface optimal?
   - Should Claude Chat push to a specific branch that Claude Code picks up?
   - How do people manage the Chat→Code transition in practice?

### Open Design Questions

- **Should we use a different project per workflow phase** (one for spec-review, one for building) or one project per engine?
- **Should the custom instructions include the clone command literally** or reference a script in the repo?
- **Should we version the skills in the repo** and have a script that generates the .zip files, or manage them manually?
- **Is there a way to test skills** without going through a full engine cycle?

---

## Files Changed This Session
- `skills/` — entire directory created and iterated
- `skills/README.md` — overview with architecture
- `skills/kr-{spec-review,finalize,build-prep,evaluate,research,integrity}/SKILL.md` — all 6 skills
- `skills/shared/COMMENT_TEMPLATE.md` — owner comment format
- `skills/shared/HANDOFF_PROTOCOL.md` — session bridging
- `skills/handoffs/.gitkeep` — handoff storage directory
- `skills/source-engine-project/custom_instructions.md` — source engine role + startup
- `skills/source-engine-project/knowledge_files.md` — setup guide (2-file approach)

## Context for Next Chat

The skills are functional but untested against real usage. The next priority is deepening the research into how other people use Claude Chat for complex, multi-session projects, and identifying MCPs, patterns, and workarounds that could improve our setup. The goal is to make the source engine project's Claude Chat instance as effective as possible BEFORE the owner starts using it for real comment review.

The repo is at github.com/rayanino/kr, branch master. All work is in the `skills/` directory.
