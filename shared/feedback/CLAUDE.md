# Feedback Loop Infrastructure — حلقة التغذية الراجعة

The feedback component is KR's learning infrastructure. It transforms individual owner corrections into systemic engine improvements through structured correction recording, pattern analysis, DSPy training data management, and regression test coordination.

## Core Architecture

The feedback component is a **data management and statistical analysis** layer — it does NOT optimize prompts or run LLM calls. Each engine owns its own DSPy optimization; the feedback component provides the correction data and regression coordination.

**Five capabilities:**
1. Correction recording — unified storage of corrections from human gate resolutions and direct owner corrections
2. Pattern analysis — statistical detection of systemic error patterns (7 pattern types)
3. Training data management — DSPy-compatible training example generation per engine
4. Regression test coordination — gold baseline management and update gating
5. Model change monitoring — silent drift detection and mandatory regression triggers

## Key Design Decisions

- **Pull model for human gate corrections**: periodically scans resolved archive, not pushed by the gate
- **Engine registration for training data**: engines register DSPy task signatures so the feedback component can format corrections as training examples
- **Cooperative regression blocking**: no technical locks — engines check results before applying updates
- **Correction immutability**: records never modified/deleted; supersession creates new records
- **Purely statistical pattern analysis**: no LLM calls, no ML models — deterministic and auditable

## Dependencies

- **Upstream**: shared/human_gate (resolved checkpoint archive), scholar interface (direct corrections)
- **Downstream**: all engines (training data, regression coordination), scholar interface (pattern reports, cascade signals)
- **External**: Pydantic v2, DSPy (Example format only), Python standard library

## Files

- `SPEC.md` — full specification (461 lines, all 10 sections)
- `src/` — implementation (empty — all [NOT YET IMPLEMENTED])
- `tests/` — tests (empty)

## Storage Layout

```
library/feedback/
├── corrections/{year-month}/     # Correction records (append-only)
├── indexes/                      # Secondary indexes (by_engine, by_science, etc.)
├── training/{engine_id}/         # DSPy training data exports per engine
├── patterns/                     # Detected systemic patterns
├── baselines/registry.json       # Gold baseline registry
├── regression_runs/              # Regression test results
├── models/                       # Engine model manifests
├── cascades/pending/             # Cascade review signals
├── engine_registry.json          # Engine task signature registrations
├── processed_checkpoints.jsonl   # Processed checkpoint ledger
├── stats.json                    # Aggregate statistics
└── config/science_overrides.json # Per-science threshold overrides
```

## Transformative Capabilities (§4.B)

1. **Correction cascade intelligence** — one correction triggers review of related artifacts (5 cascade rules)
2. **Cross-engine root cause analysis** — detects when downstream corrections trace to upstream causes
3. **Learning velocity tracking** — identifies stagnant error patterns where prompt optimization has plateaued

## SPEC Refinement Status
- Cycle 0 (not yet started)
- Implementation-ready: NO — refinement required before implementation

## Claude Code Behaviour Guidelines

- **Ownership, not deflection:** When you encounter an issue, take responsibility and work towards a solution. Don't say "not caused by my changes" or "pre-existing issue." Don't give up with "known limitation" or defer to "future work." Fix it now.
- **Persistence through obstacles:** Don't stop at the first problem. Don't declare "good stopping point" or "natural checkpoint." Keep pushing until you have a complete, verified solution.
- **Initiative over permission-seeking:** If you have the knowledge and capability to solve a problem, act. Don't ask "should I continue?" or "want me to keep going?" Take initiative and drive towards the solution.
- **Plan before acting:** For multi-step work, plan which files to read, in what order, which tools to use, and what the expected outcome is — before touching anything.
- **Convention recall:** Always re-read and apply project-specific conventions from CLAUDE.md files. Don't rely on memory of what they say.
- **Self-correction loops:** Catch your own mistakes by applying reasoning loops and self-checks. Fix errors before committing or asking for help.
- **Verify, don't assume:** After reaching a conclusion or making a change, verify it against the actual state of the codebase. A conclusion you haven't verified is a guess. Run the test, read the output, check the file.
- **Trace root causes:** When something fails, trace the full causal chain. Don't patch symptoms — find and fix the underlying cause. A surface fix hides the real bug for later.

### Tool Use

- **Research-first, never edit-first:** Before using any tool, research the context and requirements. Read the relevant code, SPEC, and contracts before making changes. Understand before you act.
- **Surgical edits over rewrites:** Make targeted, minimal changes. Never rewrite whole files or make large sweeping changes when a focused edit achieves the goal.
- **Reasoning loops are mandatory:** Apply reasoning loops frequently. Don't skip them to save tokens. The cost of a wrong action far exceeds the cost of thinking.

### Thinking Depth

- Always apply the **highest level of thinking depth**. Shallow thinking leads to the cheapest available action, which is rarely the correct one. Spending more tokens on reasoning produces dramatically better outcomes.
- **Never reason from assumptions.** Always reason from actual data — read and understand the actual code, SPEC, or documentation before making decisions. Assumptions compound into errors.
