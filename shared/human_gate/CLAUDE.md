# Human Gate (بوابة الإنسان)

Cross-engine component for human approval checkpoints.

## Role

The human gate manages checkpoint lifecycle for irreversible library changes. It creates, queries, resolves, and expires checkpoints that engines submit when they need owner decisions. It does NOT present checkpoints (that's the scholar interface) or analyze corrections (that's the feedback component).

## State

- **Status**: SPEC complete (413 lines, all 10 sections). Code: ABD-era legacy (D-019), needs complete rewrite.
- **Parent**: See shared/CLAUDE.md
- **Tests**: shared/human_gate/tests/test_human_gate.py (45 items, all ABD-era — need rewrite)

## Key Responsibilities

1. Checkpoint lifecycle (create → pending → approved/rejected/modified/expired)
2. Pre-approval policy management (auto-approve for routine decisions)
3. Bidirectional validation (verify owner decisions against library knowledge)
4. Owner confidence calibration per science (adjust gate conservatism)
5. Queue health monitoring and stale checkpoint detection

## Architecture

- Library (not a service) — engines import and call directly
- File-based storage: `library/gates/pending/`, `library/gates/resolved/`
- No external dependencies beyond Python stdlib + Pydantic v2 + shared/validation
- 18 gate types across all engines (source: 6, normalization: 3, excerpting: 1, taxonomy: 5, cross-engine: 1, meta: 1)
- Restricted gate types (never pre-approvable): tax_evolution_proposal, tax_rollback, source_trust_evaluation, gate_policy_suggestion

## Transformative Capabilities

- §4.B.1: Gate learning — suggests pre-approval policies from owner approval patterns
- §4.B.2: Review efficiency intelligence — behavioral metadata for scholar interface
- §4.B.3: Library consistency checking — deep semantic checks on owner decisions

## Integration Points

- All engines that create checkpoints (source, normalization, excerpting, taxonomy)
- shared/validation (schema validation, referential integrity)
- shared/feedback (receives audit trail for pattern analysis)
- interface/scholar (consumes checkpoint queue, presents to owner)

## Reference

- SPEC: shared/human_gate/SPEC.md
- VISION.md §9 (Human Gates), §8.1 (Layer 3: Judgment)

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
